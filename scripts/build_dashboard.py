"""Create/update the real AI/BI dashboard only after successful Gold SQL checks.

The local plan is not an export. retailflow.lvdash.json is written only from the
definition retrieved back from the workspace. This script changes no viewer ACL.
"""

import argparse
import json
from pathlib import Path
from scripts.databricks_cli import cli, save

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/release-20261030"


def query(dataset, fields, disaggregated=False):
    return {"name": "main_query", "query": {"datasetName": dataset,
            "fields": [{"name": name, "expression": expression} for name, expression in fields],
            "disaggregated": disaggregated}}


def item(widget, x, y, width, height):
    return {"widget": widget, "position": {"x": x, "y": y, "width": width, "height": height}}


def text(name, heading, description, y):
    return item({"name": name, "multilineTextboxSpec": {"lines": [heading + "\n", "\n", description]}},
                0, y, 12, 2)


def counter(name, title, dataset, expression, x, y, currency=False):
    value = {"fieldName": name, "displayName": title}
    if currency:
        value["format"] = {"type": "number-currency", "currencyCode": "USD",
                           "decimalPlaces": {"type": "exact", "places": 2}}
    return item({"name": name, "queries": [query(dataset, [(name, expression)])], "spec": {
        "version": 2, "widgetType": "counter", "encodings": {"value": value},
        "frame": {"showTitle": True, "title": title}}}, x, y, 4, 3)


def field_filter(name, title, datasets, field, x, y, width=4, kind="filter-multi-select"):
    queries, fields = [], []
    for dataset in datasets:
        q = query(dataset, [(field, "`" + field + "`")])
        q["name"] = dataset + "_" + name
        queries.append(q)
        fields.append({"fieldName": field, "queryName": q["name"], "displayName": title})
    result = item({"name": name, "queries": queries, "spec": {
        "version": 2, "widgetType": kind, "encodings": {"fields": fields},
        "frame": {"showTitle": True, "title": title}}}, x, y, width, 2)
    if kind == "filter-text-entry":
        result["widget"]["spec"].update(matchMode="exact-match", isCaseSensitive=False)
    return result


def chart(name, title, dataset, dimension, metric, x, y, width=6, kind="bar", temporal=False):
    fields = [(dimension, "`" + dimension + "`"), ("value", metric)]
    binding = query(dataset, fields)
    binding["query"]["orders"] = [{"direction": "ASC" if temporal else "DESC",
                                   "expression": "`" + dimension + "`" if temporal else metric}]
    return item({"name": name, "queries": [binding], "spec": {
        "version": 3, "widgetType": kind,
        "encodings": {"x": {"fieldName": dimension, "scale": {
            "type": "temporal" if temporal else "categorical"}},
            "y": {"fieldName": "value", "displayName": "USD" if dataset == "sales_lines" else "Occurrences",
                  "scale": {"type": "quantitative"}}},
        "frame": {"showTitle": True, "title": title}}}, x, y, width, 5)


def table(name, title, dataset, columns, y, height=6, disaggregated=True):
    return item({"name": name, "queries": [query(dataset, [(col, "`" + col + "`") for col in columns],
                                                       disaggregated)], "spec": {
        "version": 2, "widgetType": "table", "encodings": {"columns": [
            {"fieldName": col, "displayName": col.replace("_", " ").title()} for col in columns]},
        "frame": {"showTitle": True, "title": title}}}, 0, y, 12, height)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="M2M")
    args = parser.parse_args()
    checks = json.loads((EVIDENCE / "dashboard-sql.json").read_text())
    assert checks["status"] == "passed_sql_only", "Execute and inspect Gold SQL verification first"
    publication = checks["publication_id"]
    datasets = []
    for name in ("publication", "sales_lines", "rejected_records", "rejected_reasons"):
        datasets.append({"name": name, "displayName": name.replace("_", " ").title(),
                         "queryLines": (ROOT / "dashboard" / (name + ".sql")).read_text().splitlines(True)})
        if name != "publication":
            datasets[-1]["parameters"] = [{"keyword": "publication_id", "displayName": "Registered publication", "dataType": "STRING",
                "defaultSelection": {"values": {"dataType": "STRING", "values": [{"value": publication}]}}}]
    pub_filter = field_filter("publication-selector", "Registered publication (all pages)",
                              ["publication"], "available_publication_id", 0, 0, 12, "filter-single-select")
    for name in ("sales_lines", "rejected_records", "rejected_reasons"):
        qname = name + "_publication"
        pub_filter["widget"]["queries"].append({"name": qname, "query": {"datasetName": name,
            "parameters": [{"name": "publication_id", "keyword": "publication_id"}], "disaggregated": False}})
        pub_filter["widget"]["spec"]["encodings"]["fields"].append({"parameterName": "publication_id", "queryName": qname})
    pub_filter["widget"]["spec"]["selection"] = {"defaultSelection": {
        "values": {"dataType": "STRING", "values": [{"value": publication}]}}}
    sales = [text("sales-heading", "# RetailFlow / trustworthy sales",
                  "USD · synthetic fixtures · one registered snapshot across all datasets. "
                  "55 baseline → 91 corrected → 98 after explicit replay. Sales filters affect this page only.", 0)]
    sales += [field_filter("sales-date", "Transaction date", ["sales_lines"], "order_date", 0, 2,
                           kind="filter-date-range-picker"),
              field_filter("sales-product", "Product", ["sales_lines"], "product_id", 4, 2),
              field_filter("sales-region", "Transaction region", ["sales_lines"], "sale_region", 8, 2)]
    sales += [counter("net-sales", "Net sales (USD)", "sales_lines", "SUM(`net_sales`)", 0, 4, True),
              counter("units", "Units", "sales_lines", "SUM(`quantity`)", 4, 4),
              counter("orders", "Distinct orders", "sales_lines", "COUNT(DISTINCT `order_id`)", 8, 4),
              chart("daily-sales", "Daily sales (USD)", "sales_lines", "order_date", "SUM(`net_sales`)", 0, 7,
                    kind="line", temporal=True),
              chart("product-sales", "Products · transaction sales", "sales_lines", "product_label", "SUM(`net_sales`)", 6, 7),
              chart("regional-sales", "Transaction region · sales (USD)", "sales_lines", "sale_region", "SUM(`net_sales`)", 0, 12, 12),
              table("active-snapshot", "Selected snapshot provenance", "sales_lines", ["publication_id", "snapshot_created_at"],
                    17, 3, False),
              table("line-evidence", "Published order lines", "sales_lines", ["order_id", "line_id", "product_label",
                    "order_date", "sale_region", "quantity", "net_sales"], 20, 5)]
    quality = [text("quality-heading", "# Data quality / retained rejection history",
                    "Unique source occurrences, including resolved history. Quality batch/entity filters never scope sales. "
                    "Reason counts overlap; invalid dates remain inspectable.", 0),
               field_filter("quality-batch", "Quality batch", ["rejected_records", "rejected_reasons"], "batch_id", 0, 2, 6),
               field_filter("quality-entity", "Quality entity (exact)", ["rejected_records", "rejected_reasons"], "entity", 6, 2, 6,
                            kind="filter-text-entry"),
               counter("unresolved", "Unresolved occurrences", "rejected_records", "COUNT(DISTINCT `unresolved_occurrence_id`)", 0, 4),
               counter("resolved", "Resolved occurrences", "rejected_records", "COUNT(DISTINCT `resolved_occurrence_id`)", 4, 4),
               counter("ever-rejected", "Ever rejected · unique", "rejected_records", "COUNT(DISTINCT `occurrence_id`)", 8, 4),
               chart("reasons", "Rejection reasons · overlapping counts", "rejected_reasons", "reason", "SUM(`rejected_records`)", 0, 7, 12),
               table("reject-evidence", "Rejected source records · original bytes and latest disposition", "rejected_records",
                     ["batch_id", "filename", "record_index", "business_key", "disposition", "reasons", "resolved", "raw_record"], 12, 8)]
    pages = [{"name": name, "displayName": title, "pageType": kind, "layoutVersion": "GRID_V1", "layout": layout}
             for name, title, kind, layout in [("sales", "Sales", "PAGE_TYPE_CANVAS", sales),
                 ("quality", "Data quality", "PAGE_TYPE_CANVAS", quality),
                 ("publication", "Publication", "PAGE_TYPE_GLOBAL_FILTERS", [pub_filter])]]
    definition = {"datasets": datasets, "pages": pages, "uiSettings": {"theme": {
        "canvasBackgroundColor": {"light": "#F3F6F8", "dark": "#15212D"},
        "widgetBackgroundColor": {"light": "#FFFFFF", "dark": "#1B2C3A"},
        "widgetBorderColor": {"light": "#FFFFFF", "dark": "#1B2C3A"},
        "fontColor": {"light": "#153047", "dark": "#EDF4F7"},
        "selectionColor": {"light": "#147D92", "dark": "#65CBD2"},
        "visualizationColors": ["#157F86", "#E38D31", "#406A9E", "#9273B3", "#A64B67", "#6B8F71"],
        "widgetHeaderAlignment": "LEFT"}}}
    save(ROOT / ".dashboard-plan.local.json", definition)
    state_path = ROOT / ".dashboard-state.local.json"
    flags = ("--dataset-catalog", checks["catalog"], "--dataset-schema", checks["schema"])
    payload = {"display_name": "RetailFlow — Trustworthy Sales", "warehouse_id": "ec9f4c81bc387245",
               "serialized_dashboard": json.dumps(definition)}
    if state_path.exists():
        dashboard_id = json.loads(state_path.read_text())["dashboard_id"]
        receipt = cli(args.profile, "lakeview", "update", dashboard_id, *flags, payload=payload)
    else:
        parent = "/Workspace/Users/e92b585c-22cc-4813-b00e-b894ea680a37/retailflow/dashboards"
        cli(args.profile, "workspace", "mkdirs", parent)
        receipt = cli(args.profile, "lakeview", "create", *flags, payload={**payload, "parent_path": parent})
        dashboard_id = receipt["dashboard_id"]
        save(state_path, {"dashboard_id": dashboard_id})
    actual = cli(args.profile, "lakeview", "get", dashboard_id)
    save(EVIDENCE / "dashboard-resource.json", actual)
    save(ROOT / "dashboard/retailflow.lvdash.json", json.loads(actual["serialized_dashboard"]))
    print(json.dumps({"dashboard_id": dashboard_id, "status": "created_and_exported_draft",
        "url": "https://dbc-9d765ae8-3bb9.cloud.databricks.com/sql/dashboardsv3/" + dashboard_id}))


if __name__ == "__main__":
    main()
