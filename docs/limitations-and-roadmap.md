# Limitations and roadmap

## Current release boundary

The bounded synthetic-data lakehouse and private published dashboard are verified. Five retained demo jobs and full isolated Delta recovery acceptance passed; November 6 APIs revalidated those runs, the single writer, publisher identity, unchanged ACL and export parity. SQL and rendered controls, historical snapshots and provenance passed. Genuine dashboard images and a 2:10 silent snapshot walkthrough are public repository artifacts. [Current evidence](../evidence/release-20261106/README.md). Final source-publication receipts are in [GitHub releases](https://github.com/RussypherIOIIOI/RretailfowR/releases).

## Deliberate v1 limits

| Limit | Consequence | When to revisit |
|---|---|---|
| One writer per namespace | Concurrency=1 on one job is not a distributed lock | Before multiple producers/jobs or manual writers |
| Driver CSV parsing; 10 MiB and 10,000 records per file | At most three bounded files; embedded newlines unsupported | Before larger/more varied feeds |
| collect_list and Python resolver; 1,000 candidates per key | Guard runs after grouping; no memory/throughput guarantee | Before skewed or large revision histories |
| USD only; no returns/deletes/tax/shipping | Net sales is a limited synthetic metric | Before richer commercial reporting |
| Full-record revisions; timestamps audit only | Source must supply authoritative monotonic revisions per key | Before event-time/CDC integration |
| Type 1 dimensions | Historical names/category/home-region not preserved | Before point-in-time dimension analysis |
| Full Gold recomputation | Simple reconciliation; cost grows with current model | After measured runtime/cost warrants incremental Gold |
| No automatic history cleanup | Snapshots and registry grow; rollback needs retained files | Before sustained scheduled operation |
| No schedule or alert integration | Manual demonstration and inspection | Before unattended execution |
| Reject threshold defaults to 1.0 | Permissive dirty-data demo, not an SLA | Before any real feed |
| No row/column security design for real customer data | Synthetic-only scope | Before handling sensitive source data |

## Work beyond this release

Before sustained unattended operation, define a real-feed contract and owner, alert routing, retention and measured freshness/cost objectives. Benchmark representative larger data before changing ingestion or candidate selection. Multiple writers, sensitive customer data, returns/deletes and enterprise availability require new design and evidence. These are future scope, not features claimed by this release.

## Definition of the first portfolio release

A viewer can inspect source and documentation without workspace access, see genuine dashboard evidence, and trace all claims to passing checks. Persisted correction/rerun/replay behavior must match the independent oracle. [Release checklist](release-checklist.md).
