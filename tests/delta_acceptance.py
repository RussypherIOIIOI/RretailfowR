"""Run in an isolated retailflow_test<id> namespace on Databricks. No local substitutes."""

import json
from decimal import Decimal
from pathlib import Path
from retailflow.config import Config
from retailflow.fixtures import generate
from retailflow.pipeline import Lakehouse, InjectedFailure


def run(spark, catalog, suffix, expected_path):
    cfg = Config(catalog, "retailflow_test" + suffix)
    lake = Lakehouse(spark, cfg)
    lake.setup()
    generate(cfg.volume)
    expected = json.loads(Path(expected_path).read_text())
    checks = []

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
    for injected in ("after_freeze_customers", "after_merge_customers", "during_stage"):
        try:
            pipeline("batch2", "second", fault=injected)
        except InjectedFailure:
            pass
        else:
            raise AssertionError("Fault not injected: " + injected)
        assert lake.current_id() == old_publication
    try:
        pipeline("batch2", "second", fault="after_silver")
    except InjectedFailure:
        pass
    else:
        raise AssertionError("Fault not injected")
    assert lake.current_id() == old_publication
    try:
        pipeline("batch2", "second", fault="after_stage")
    except InjectedFailure:
        pass
    else:
        raise AssertionError("Fault not injected")
    assert lake.current_id() == old_publication
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
    check("batch2")
    assert lake.published("daily_sales").filter(
        "order_date='2026-01-01' AND sale_region='WEST' AND product_id='P1'"
    ).first().net_sales == Decimal("21.00")
    # New dimensions do not silently replay older rejects.
    pipeline("arrival", "arrival")
    check("batch2")
    pipeline("arrival", "replay", ["batch2"])
    check("replay")
    lines = [
        [r.order_id, r.line_id, r.source_revision, format(r.net_sales, ".2f")]
        for r in lake.published("fact_order_line").orderBy("order_id", "line_id").collect()
    ]
    assert lines == expected["final_lines"], lines
    rejects = lake.published("rejected_records")
    assert rejects.filter("disposition='invalid' AND size(reasons)>1").count() > 0
    assert rejects.filter("disposition='conflict'").count() >= 3
    assert lake.read("ops", "evaluations").filter("evaluation_id='replay' AND kind='row'").count() == 18
    # Roll back an unpublished evaluation without deleting its audit history.
    before = lake.typed("orders").orderBy("order_id", "line_id").collect()
    lake.begin("abandoncheck", "arrival", [])
    lake.silver("abandoncheck")
    # A deliberately wrong unpublished Silver edit exercises restoration, not just status.
    spark.sql(f"UPDATE {lake.name('silver', 'orders')} SET source_revision=2147483647")
    lake.abandon("abandoncheck", confirm=True)
    after = lake.typed("orders").orderBy("order_id", "line_id").collect()
    assert before == after
    assert lake.read("silver", "orders").filter("source_revision=2147483647").count() == 0
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
    return {"status": "passed", "checks": checks, "namespace": cfg.prefix, "spark": spark.version}
