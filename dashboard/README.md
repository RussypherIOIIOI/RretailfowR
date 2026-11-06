# RetailFlow dashboard specification

Status, 6 November: the private published dashboard and all rendered checks passed. The Info panel verifies jarvis-cli-m2m as publisher; APIs verify embedded credentials, the approved warehouse and unchanged creator/admin ACL. Four datasets and twelve fresh SQL checks pass, and the live draft structurally matches the committed export. [Actual launch evidence](../evidence/release-20261106/README.md) · [screenshots and 2:10 silent walkthrough](../docs/walkthrough.md).

The existing dashboard is 01f1d4bd43b6157d96bdf99719c7f0c3 on warehouse ec9f4c81bc387245. Use [the release verification procedure](../docs/release-resume.md) for this instance. The following layout and dataset instructions also describe how to reproduce it in a separately authorized installation. Set the dataset catalog and schema to the configured Gold namespace. Import each SQL file as one dataset. Resolve the current publication from publication.sql and bind one publication_id parameter to the three sales/rejection datasets (publication.sql supplies the selection list and has no parameter); refresh this parameter deliberately after a successful job. The supplied dataset SQL returns rows only for IDs atomically registered in the publication pointer; direct access to snapshot tables does not enforce that restriction. This prevents mixed versions across separate widget queries and keeps failed stage IDs out of the dashboard.

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

Dataset execution, persisted progression, actual export and rendered checks are complete. Re-export dashboard/retailflow.lvdash.json and repeat affected checks if the live definition changes.

## Snapshot and metric checks

For a historical selection, display the selected publication ID and its snapshot_created_at from sales_lines; publication.sql.latest_published_at describes the latest pointer, not necessarily the selected historical snapshot. The selected ID must occur in available_publication_id. Changing current views between separate queries is not a substitute for pinning.

Group top products by product_id as well as product_name; two products can share a display name. Label net sales as USD and reject counts as unresolved unique source occurrences. Do not add reason bars together to produce the rejection KPI.

Validate that date/product/region filters affect all sales widgets, quality batch/entity filters affect only rejection widgets, and resetting filters restores the expected total for the selected publication. Test an unregistered ID: the supplied queries should return no rows. Record actual SQL/widget results before export.

[Metric dictionary](../docs/data-model.md) · [walkthrough and shot list](../docs/walkthrough.md) · [release checklist](../docs/release-checklist.md).

Resolution inspection uses native table row selection. Selecting A4/1 filters same-dataset counters to 0 unresolved / 1 resolved / 1 ever rejected; Ctrl-select the six unresolved batch2 rows for 6 / 0 / 6. The source table remains visible and highlights selections. The separate unresolved-reasons aggregate keeps its batch/entity scope. Clear the selection chip to reset; there is no separate status dropdown.
