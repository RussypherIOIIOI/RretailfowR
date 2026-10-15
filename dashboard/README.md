# RetailFlow dashboard specification

Status: SQL and layout prepared; live SQL validation, dashboard creation/export and screenshots are pending Unity Catalog access. No fabricated .lvdash.json is included.

Create a Databricks AI/BI dashboard using the existing serverless SQL warehouse. Set the dataset catalog and schema to the configured Gold namespace. Import each SQL file as one dataset. Resolve the current publication from publication.sql and bind one publication_id parameter to every dataset; refresh this parameter deliberately after a successful job. Only IDs atomically registered in the publication pointer can be queried. This prevents mixed versions across separate widget queries and keeps failed stage IDs out of the dashboard.

| Position | Widget | Dataset and calculation |
|---|---|---|
| Top | RetailFlow / trustworthy sales | Text: USD, synthetic data, snapshot ID and snapshot time |
| First row | Net sales / units / orders | sales_lines: SUM(net_sales), SUM(quantity), COUNT(DISTINCT order_id) |
| Second row | Daily sales / top products | sales_lines: net sales by order_date / product_name, descending |
| Third row | Regional sales / rejected records | sales_lines by sale_region / rejected_records COUNT(DISTINCT occurrence_id) where resolved=false |
| Fourth row | Rejection reasons and batches | rejected_reasons, bars; label overlapping reason counts |
| Last row | Inspect rejected records | rejected_records table: raw text, filename, record number, revision, reason list, resolved flag |

Use date range, transaction region and product filters on the shared sales_lines dataset. Rejection batch/entity filters apply only to quality widgets; rejected rows can have invalid dates, so never imply the sales date filter scopes their count. Distinct orders are calculated at the active filter grain, never summed from daily/product groups. Dimensions show current Type 1 descriptions while line prices and region retain transaction meaning.

Use a 12-column layout, 3 KPI cards of width 4 and height 3, paired charts of width 6 and height 5, and a full-width evidence table. Use a white background, navy text, teal sales and orange reject indicators, with labels as well as colors. The tiny fixture intentionally explains corrections; it is not evidence of realistic commercial trends.

Before publishing: execute all datasets with a real registered publication ID; verify 55.00 baseline, 91.00 corrected, and 98.00 after dimension replay; test each filter; export the actual dashboard to dashboard/retailflow.lvdash.json; capture real screenshots.
