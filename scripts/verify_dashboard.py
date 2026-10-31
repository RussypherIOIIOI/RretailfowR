"""Execute all real Gold datasets and independent filter checks; retain SQL receipts."""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from retailflow.config import Config, token
from scripts.databricks_cli import sql, rows, save

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="M2M")
    parser.add_argument("--catalog", default="tmc_solutions_jvs")
    parser.add_argument("--schema-prefix", default="retailflow")
    parser.add_argument("--warehouse", default="ec9f4c81bc387245")
    parser.add_argument("--publication", required=True)
    parser.add_argument("--evidence", default="evidence/release-20261030/dashboard-sql.json")
    args = parser.parse_args()
    cfg = Config(args.catalog, args.schema_prefix)
    token(args.publication)
    evidence = {
        "verified_at": datetime.now(timezone.utc).isoformat(), "catalog": cfg.catalog,
        "schema": cfg.prefix + "_gold", "publication_id": args.publication,
        "datasets": {}, "checks": [], "status": "running",
    }
    save(args.evidence, evidence)
    parameters = [{"name": "publication_id", "value": args.publication, "type": "STRING"}]

    def execute(statement, bound=True):
        return sql(args.profile, args.warehouse, args.catalog, cfg.prefix + "_gold", statement,
                   parameters if bound else [])

    def checked(name, statement, expected):
        response = execute(statement)
        observed = rows(response)
        assert len(observed) == 1, (name, observed)
        for key, value in expected.items():
            assert Decimal(observed[0][key]) == Decimal(value), (name, observed, expected)
        evidence["checks"].append({"name": name, "statement_id": response["statement_id"],
                                   "observed": observed[0], "expected": expected})
        save(args.evidence, evidence)

    datasets = {name: (ROOT / "dashboard" / (name + ".sql")).read_text()
                for name in ("publication", "sales_lines", "rejected_records", "rejected_reasons")}
    for name, statement in datasets.items():
        response = execute(statement, bound=name != "publication")
        evidence["datasets"][name] = response
        save(args.evidence, evidence)
    available = rows(evidence["datasets"]["publication"])
    assert any(row["available_publication_id"] == args.publication for row in available)

    sales = "WITH sales AS (\n" + datasets["sales_lines"] + "\n) "
    metrics = "SELECT SUM(net_sales) AS usd, SUM(quantity) AS units, COUNT(DISTINCT order_id) AS orders FROM sales"
    checked("reset_sales", sales + metrics, {"usd": "98.00", "units": "8", "orders": "5"})
    checked("date_only", sales + metrics + " WHERE order_date BETWEEN DATE'2026-01-01' AND DATE'2026-01-01'",
            {"usd": "63.00", "units": "5", "orders": "4"})
    checked("product_only", sales + metrics + " WHERE product_id='P1'",
            {"usd": "38.00", "units": "4", "orders": "4"})
    checked("region_only", sales + metrics + " WHERE sale_region='WEST'",
            {"usd": "28.00", "units": "3", "orders": "3"})
    checked("combined_sales", sales + metrics + " WHERE order_date=DATE'2026-01-01' AND product_id='P1' AND sale_region='WEST'",
            {"usd": "28.00", "units": "3", "orders": "3"})
    quality = "WITH rejects AS (\n" + datasets["rejected_records"] + "\n) "
    count = "SELECT COUNT(DISTINCT occurrence_id) AS rejects FROM rejects"
    checked("unresolved_quality", quality + count + " WHERE NOT resolved", {"rejects": "7"})
    checked("batch_quality", quality + count + " WHERE NOT resolved AND batch_id='batch2'", {"rejects": "6"})
    checked("entity_quality", quality + count + " WHERE entity='customers'", {"rejects": "0"})
    checked("resolved_history", quality + count + " WHERE resolved", {"rejects": "1"})
    # The sales-only date/product/region columns never filter invalid-date quality rows.
    # Dashboard widget binding still requires a separate rendered UI check.
    assert "order_date" not in {column["name"] for column in
                                evidence["datasets"]["rejected_records"]["manifest"]["schema"]["columns"]}
    parameters[0]["value"] = "unregistered_publication_20261030"
    for name in ("sales_lines", "rejected_records", "rejected_reasons"):
        response = execute(datasets[name])
        assert not rows(response), (name, "unregistered publication leaked")
        evidence["checks"].append({"name": name + "_unregistered", "statement_id": response["statement_id"],
                                   "observed_rows": 0})
    evidence["status"] = "passed_sql_only"
    evidence["widget_ui_verified"] = False
    save(args.evidence, evidence)
    print("All datasets and SQL filter assertions passed; rendered widget checks remain separate.")


if __name__ == "__main__":
    main()
