# RetailFlow dashboard specification

Status, 30 October: all four SQL datasets and 12 assertions passed against registered publication `demo04`; the real dashboard was created and its server definition exported as [retailflow.lvdash.json](retailflow.lvdash.json). Browser-owner draft queries lack direct Gold SELECT. Publication using the approved service-principal publisher and the unchanged private audience awaits a separate credential-embedding publication approval. Rendered widget/filter checks, metric/rejection screenshots and recording remain incomplete. [Actual evidence](../evidence/release-20261030/README.md).

Create a Databricks AI/BI dashboard using the existing serverless SQL warehouse. Set the dataset catalog and schema to the configured Gold namespace. Import each SQL file as one dataset. Resolve the current publication from publication.sql and bind one publication_id parameter to the three sales/rejection datasets (publication.sql supplies the selection list and has no parameter); refresh this parameter deliberately after a successful job. The supplied dataset SQL returns rows only for IDs atomically registered in the publication pointer; direct access to snapshot tables does not enforce that restriction. This prevents mixed versions across separate widget queries and keeps failed stage IDs out of the dashboard.

| Position | Widget | Dataset and calculation |
|---|---|---|
| Top | RetailFlow / trustworthy sales | Text: USD, synthetic data, snapshot ID and snapshot time |
| First row | Net sales / units / orders | sales_lines: SUM(net_sales), SUM(quantity), COUNT(DISTINCT order_id) |
| Second row | Daily sales / top products | sales_lines: net sales by order_date / product_id and product_name, descending |
| Third row | Regional sales / rejected records | sales_lines by sale_region / rejected_records COUNT(DISTINCT occurrence_id) where resolved=false |
| Fourth row | Rejection reasons and batches | rejected_reasons table; 26 observed reason codes make a full bar chart unreadable; counts overlap |
| Last row | Inspect rejected records | rejected_records table: raw text, filename, record number, revision, reason list, resolved flag |

Use date range, transaction region and product filters on the shared sales_lines dataset. Rejection batch/entity filters apply only to quality widgets; rejected rows can have invalid dates, so never imply the sales date filter scopes their count. Distinct orders are calculated at the active filter grain, never summed from daily/product groups. Dimensions show current Type 1 descriptions while line prices and region retain transaction meaning.

Use a 12-column layout, 3 KPI cards of width 4 and height 3, paired charts of width 6 and height 5, and a full-width evidence table. Use a white background, navy text, teal sales and orange reject indicators, with labels as well as colors. The tiny fixture intentionally explains corrections; it is not evidence of realistic commercial trends.

Before publishing: execute all datasets with a real registered publication ID; verify 55.00 baseline, 91.00 corrected, and 98.00 after dimension replay; test each filter; export the actual dashboard to dashboard/retailflow.lvdash.json; capture real screenshots.

## Snapshot and metric checks

For a historical selection, display the selected publication ID and its snapshot_created_at from sales_lines; publication.sql.latest_published_at describes the latest pointer, not necessarily the selected historical snapshot. The selected ID must occur in available_publication_id. Changing current views between separate queries is not a substitute for pinning.

Group top products by product_id as well as product_name; two products can share a display name. Label net sales as USD and reject counts as unresolved unique source occurrences. Do not add reason bars together to produce the rejection KPI.

Validate that date/product/region filters affect all sales widgets, quality batch/entity filters affect only rejection widgets, and resetting filters restores the expected total for the selected publication. Test an unregistered ID: the supplied queries should return no rows. Record actual SQL/widget results before export.

[Metric dictionary](../docs/data-model.md) · [walkthrough and shot list](../docs/walkthrough.md) · [release checklist](../docs/release-checklist.md).
