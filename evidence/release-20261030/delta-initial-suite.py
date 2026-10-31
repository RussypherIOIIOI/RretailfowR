"""Run in an isolated retailflow_test<id> namespace on Databricks. No local substitutes."""

import json
import hashlib
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from retailflow.config import Config
from retailflow.fixtures import generate
from retailflow.pipeline import Lakehouse, InjectedFailure


def run(spark, catalog, suffix, expected_path):
    cfg = Config(catalog, "retailflow_test" + suffix)
    lake = Lakehouse(spark, cfg)
    # Empty administrator-provisioned schemas are allowed; reused test data is not.
    for layer in ("bronze", "silver", "gold", "ops"):
        if spark.catalog.databaseExists(cfg.schema(layer)):
            assert not spark.catalog.listTables(cfg.schema(layer)), "Acceptance namespace is not fresh"
    if Path(cfg.volume).exists():
        assert not list(Path(cfg.volume).iterdir()), "Acceptance fixture volume is not empty"
    lake.setup()
    generate(cfg.volume)
    expected = json.loads(Path(expected_path).read_text())
    checks = []
    metrics = []
    frozen_evidence = []

    def evaluation_rows(evaluation, entity=None):
        frame = lake.read("ops", "evaluations").filter(f"evaluation_id='{evaluation}'")
        if entity:
            frame = frame.filter(f"entity='{entity}'")
        return [r.asDict(recursive=True) for r in frame.orderBy("entity", "kind", "occurrence_id").collect()]

    def assert_frozen(before, evaluation, entity=None):
        after = evaluation_rows(evaluation, entity)
        assert before == after, "Frozen outcomes or evaluation metadata changed on retry"
        frozen_evidence.append({
            "evaluation": evaluation, "entity": entity or "all", "rows": len(after),
            "sha256": hashlib.sha256(json.dumps(after, sort_keys=True, default=str).encode()).hexdigest(),
        })

    def check(stage):
        fact = lake.published("fact_order_line")
        rows = fact.collect()
        observed = {
            "net_sales": format(sum((r.net_sales for r in rows), Decimal(0)), ".2f"),
            "units": sum(r.quantity for r in rows),
            "orders": len({r.order_id for r in rows}),
            "lines": len(rows),
        }
        assert observed == expected[stage], (stage, observed)
        checks.append(stage)
        metrics.append({"publication_id": lake.current_id(), **observed})

    def pipeline(batch, evaluation, replay=(), fault=""):
        lake.begin(evaluation, batch, list(replay))
        lake.ingest(Path(cfg.volume) / batch, evaluation, fault)
        lake.silver(evaluation, fault)
        if fault == "after_silver":
            raise InjectedFailure(fault)
        lake.stage(evaluation, fault)
        lake.quality(evaluation)
        lake.publish(evaluation)

    pipeline("batch1", "first")
    check("batch1")
    bronze_count = lake.read("bronze", "records").count()
    pipeline("batch1", "first")  # exact job retry
    pipeline("batch1", "repeat")  # explicit new evaluation
    assert lake.read("bronze", "records").count() == bronze_count
    check("batch1")
    # Rename without changing immutable content identity.
    directory = Path(cfg.volume) / "batch1"
    manifest = json.loads((directory / "manifest.json").read_text())
    (directory / "orders.csv").rename(directory / "renamed.csv")
    manifest["files"][2]["filename"] = "renamed.csv"
    (directory / "manifest.json").write_text(json.dumps(manifest))
    pipeline("batch1", "renamed")
    assert lake.read("bronze", "records").count() == bronze_count
    old_publication = lake.current_id()
    try:
        pipeline("batch2", "second", fault="after_bronze")
    except InjectedFailure:
        pass
    else:
        raise AssertionError("Fault not injected")
    assert lake.current_id() == old_publication
    frozen_customers = None
    for injected in ("after_freeze_customers", "after_merge_customers", "during_stage"):
        try:
            pipeline("batch2", "second", fault=injected)
        except InjectedFailure:
            pass
        else:
            raise AssertionError("Fault not injected: " + injected)
        assert lake.current_id() == old_publication
        if frozen_customers is None:
            frozen_customers = evaluation_rows("second", "customers")
            assert any(r["disposition"] == "accepted_winner" for r in frozen_customers)
        else:
            assert_frozen(frozen_customers, "second", "customers")
    frozen_all = evaluation_rows("second")
    try:
        pipeline("batch2", "second", fault="after_silver")
    except InjectedFailure:
        pass
    else:
        raise AssertionError("Fault not injected")
    assert lake.current_id() == old_publication
    assert_frozen(frozen_all, "second")
    try:
        pipeline("batch2", "second", fault="after_stage")
    except InjectedFailure:
        pass
    else:
        raise AssertionError("Fault not injected")
    assert lake.current_id() == old_publication
    assert_frozen(frozen_all, "second")
    # A genuine failed gate must preserve the pointer.
    strict = Lakehouse(spark, Config(catalog, cfg.prefix, max_reject_fraction=0))
    try:
        strict.quality("second")
    except ValueError:
        pass
    else:
        raise AssertionError("Reject threshold did not fail")
    assert lake.current_id() == old_publication
    pipeline("batch2", "second")
    assert_frozen(frozen_all, "second")
    checks.append("exact_frozen_outcomes")
    check("batch2")
    assert lake.published("daily_sales").filter(
        "order_date='2026-01-01' AND sale_region='WEST' AND product_id='P1'"
    ).first().net_sales == Decimal("21.00")
    # New dimensions do not silently replay older rejects.
    pipeline("arrival", "arrival")
    check("batch2")
    pipeline("arrival", "replay", ["batch2"])
    check("replay")
    retained = {}
    for publication, stage in (("first", "batch1"), ("second", "batch2")):
        history = lake.read("gold", "publication").first().publication_ids
        assert publication in history
        total = sum(
            (r.net_sales for r in lake.read("gold", "fact_order_line_snapshots")
             .filter(f"publication_id='{publication}'").collect()), Decimal(0)
        )
        assert format(total, ".2f") == expected[stage]["net_sales"]
        retained[publication] = format(total, ".2f")
    checks.append("historical_publications_retained")
    lines = [
        [r.order_id, r.line_id, r.source_revision, format(r.net_sales, ".2f")]
        for r in lake.published("fact_order_line").orderBy("order_id", "line_id").collect()
    ]
    assert lines == expected["final_lines"], lines
    rejects = lake.published("rejected_records")
    assert rejects.filter("disposition='invalid' AND size(reasons)>1").count() > 0
    assert rejects.filter("disposition='conflict'").count() >= 3
    assert lake.read("ops", "evaluations").filter("evaluation_id='replay' AND kind='row'").count() == 18
    # Replay resolves the missing customer without erasing its original rejection.
    original_missing = lake.read("ops", "evaluations").filter(
        "evaluation_id='second' AND kind='row' AND array_contains(reasons, 'UNKNOWN_CUSTOMER')"
    ).collect()
    assert original_missing, "Missing-customer rejection history absent"
    for rejected in original_missing:
        assert rejects.filter(f"occurrence_id='{rejected.occurrence_id}' AND resolved").count() == 1
    checks.append("rejection_history_and_explicit_replay")
    # Roll back an unpublished evaluation without deleting its audit history.
    entities = ("customers", "orders", "products")
    before = {entity: lake.read("silver", entity).orderBy("business_key").collect() for entity in entities}
    audit_before = evaluation_rows("replay")
    publication_before = lake.current_id()
    bronze_before = lake.read("bronze", "records").count()
    lake.begin("abandoncheck", "arrival", [])
    lake.silver("abandoncheck")
    # A deliberately wrong unpublished Silver edit exercises restoration, not just status.
    for entity in entities:
        spark.sql(f"UPDATE {lake.name('silver', entity)} SET source_revision=2147483647")
    real_sql = spark.sql
    restored = []

    def interrupted_restore(statement, *args, **kwargs):
        if statement.startswith("RESTORE TABLE"):
            if len(restored) == 1:
                raise InjectedFailure("interrupted_rollback")
            result = real_sql(statement, *args, **kwargs)
            restored.append(statement)
            return result
        return real_sql(statement, *args, **kwargs)

    with patch.object(spark, "sql", side_effect=interrupted_restore):
        try:
            lake.abandon("abandoncheck", confirm=True)
        except InjectedFailure:
            pass
        else:
            raise AssertionError("Rollback interruption not injected")
    assert len(restored) == 1
    assert lake.read("ops", "runs").filter("evaluation_id='abandoncheck'").first().status == "abandoning"
    assert lake.current_id() == publication_before
    assert sum(
        lake.read("silver", entity).filter("source_revision=2147483647").count() > 0
        for entity in entities
    ) == 2, "Interruption did not leave a partial rollback"
    try:
        lake.begin("mustnotstart", "arrival", [])
    except ValueError:
        pass
    else:
        raise AssertionError("New evaluation started during partial rollback")
    lake.abandon("abandoncheck", confirm=True)
    lake.abandon("abandoncheck", confirm=True)  # completed rollback is idempotent
    after = {entity: lake.read("silver", entity).orderBy("business_key").collect() for entity in entities}
    assert before == after
    assert lake.read("ops", "runs").filter("evaluation_id='abandoncheck'").first().status == "abandoned"
    assert lake.current_id() == publication_before
    assert lake.read("bronze", "records").count() == bronze_before
    assert_frozen(audit_before, "replay")
    checks.append("interrupted_rollback_resumes_all_three_tables")
    try:
        lake.stage("abandoncheck")
    except ValueError:
        pass
    else:
        raise AssertionError("Abandoned evaluation was executable")
    pipeline("arrival", "afterrollback")
    check("replay")
    # Changed bytes under an existing batch identity fail before affecting data.
    with (directory / "renamed.csv").open("ab") as stream:
        stream.write(b"changed\n")
    try:
        lake.ingest(directory, "tamper")
    except ValueError:
        pass
    else:
        raise AssertionError("Changed bytes accepted")
    # Even a correctly refreshed manifest cannot reuse the old batch ID.
    from retailflow.contracts import digest

    data = (directory / "renamed.csv").read_bytes()
    manifest["files"][2]["sha256"] = digest(data)
    manifest["files"][2]["record_count"] += 1
    (directory / "manifest.json").write_text(json.dumps(manifest))
    try:
        lake.ingest(directory, "tamper")
    except ValueError as error:
        assert "Immutable batch ID" in str(error), str(error)
    else:
        raise AssertionError("Changed immutable batch accepted")
    checks.extend(["reruns_and_rename", "failed_gate_retains_last_good", "immutable_batch_tampering"])
    return {
        "status": "passed", "checks": checks, "metrics": metrics, "frozen_evidence": frozen_evidence,
        "historical_totals": retained, "namespace": cfg.prefix, "catalog": cfg.catalog,
        "spark": spark.version,
    }
