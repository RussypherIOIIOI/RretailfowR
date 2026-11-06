"""Verify registered persisted demo results after all real six-task job runs."""

import json
from decimal import Decimal
from pathlib import Path
from scripts.databricks_cli import sql, rows, save

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/release-20261030"


def main():
    run_ids = {}
    for step in ("baseline", "correction", "arrival", "replay", "rerun"):
        run = json.loads((EVIDENCE / ("demo-" + step + ".json")).read_text())
        assert run["state"]["result_state"] == "SUCCESS", step
        assert len(run["tasks"]) == 6 and all(t["state"]["result_state"] == "SUCCESS" for t in run["tasks"])
        run_ids[step] = run["run_id"]
    evidence = {"status": "running", "job_runs": run_ids, "queries": {}}

    def execute(name, statement, layer="gold"):
        result = sql("M2M", "ec9f4c81bc387245", "tmc_solutions_jvs", "retailflow_" + layer, statement)
        evidence["queries"][name] = result
        save(EVIDENCE / "demo-persisted.json", evidence)
        return rows(result)

    metrics = execute("registered_metrics", """SELECT f.publication_id, SUM(f.net_sales) AS net_sales,
        SUM(f.quantity) AS units, COUNT(DISTINCT f.order_id) AS orders, COUNT(*) AS lines
        FROM fact_order_line_snapshots f JOIN publication p ON array_contains(p.publication_ids, f.publication_id)
        GROUP BY f.publication_id ORDER BY f.publication_id""")
    expected = json.loads((ROOT / "fixtures/expected.json").read_text())
    assert [r["publication_id"] for r in metrics] == ["demo01", "demo02", "demo03", "demo04"]
    for row in metrics:
        stage = {"demo01": "batch1", "demo02": "batch2", "demo03": "batch2", "demo04": "replay"}[row["publication_id"]]
        assert all(Decimal(row[k]) == Decimal(str(v)) for k, v in expected[stage].items()), row
    pointer = execute("publication", "SELECT publication_id, sequence, publication_ids FROM publication")
    assert len(pointer) == 1 and pointer[0]["publication_id"] == "demo04" and pointer[0]["sequence"] == "4"
    facts = execute("final_lines", """SELECT order_id, line_id, source_revision, net_sales
        FROM fact_order_line WHERE publication_id='demo04' ORDER BY order_id, line_id""")
    observed_lines = [[r["order_id"], r["line_id"], int(r["source_revision"]), r["net_sales"]] for r in facts]
    assert observed_lines == expected["final_lines"]
    bronze = execute("bronze_rerun_conservation", "SELECT COUNT(*) AS occurrences, COUNT(DISTINCT occurrence_id) AS unique_occurrences FROM records", "bronze")
    assert bronze == [{"occurrences": "27", "unique_occurrences": "27"}]
    runs = execute("evaluation_rerun_conservation", "SELECT evaluation_id, sequence FROM runs ORDER BY sequence", "ops")
    assert [r["evaluation_id"] for r in runs] == ["demo01", "demo02", "demo03", "demo04"]
    gates = execute("gates", "SELECT publication_id, passed, report_json FROM gates ORDER BY publication_id", "ops")
    assert len(gates) == 4 and all(r["passed"] == "true" for r in gates)
    history = execute("resolved_rejection_history", """SELECT e.occurrence_id, e.evaluation_id,
        e.disposition AS original_disposition, e.reasons AS original_reasons, r.disposition AS latest_disposition, r.resolved
        FROM tmc_solutions_jvs.retailflow_ops.evaluations e JOIN rejected_records r USING (occurrence_id)
        WHERE e.evaluation_id='demo02' AND e.kind='row' AND array_contains(e.reasons,'UNKNOWN_CUSTOMER')
        AND get_json_object(e.payload_json,'$.customer_id')='C9'""")
    assert len(history) == 1 and history[0]["original_disposition"] == "invalid"
    assert history[0]["resolved"] == "true" and history[0]["latest_disposition"] == "accepted_winner"
    quality = execute("quality_counts", """SELECT COUNT(DISTINCT occurrence_id) AS ever_rejected,
        COUNT(DISTINCT CASE WHEN NOT resolved THEN occurrence_id END) AS unresolved,
        COUNT(DISTINCT CASE WHEN resolved THEN occurrence_id END) AS resolved FROM rejected_records""")
    assert quality == [{"ever_rejected": "8", "unresolved": "7", "resolved": "1"}]
    evidence.update(status="passed", progression=metrics, final_lines=observed_lines)
    save(EVIDENCE / "demo-persisted.json", evidence)
    print(json.dumps({"status": "passed", "progression": metrics, "job_runs": run_ids}))


if __name__ == "__main__":
    main()
