# Limitations and roadmap

## Current release boundary

The code is implemented and partially verified. Local tests, lint/build and nine live Spark checks passed. The job is deployed. CREATE SCHEMA denial blocked table initialization, so Delta acceptance, actual Gold data, dashboard SQL/export and recording remain unfinished. Source is published at [RussypherIOIIOI/RretailfowR](https://github.com/RussypherIOIIOI/RretailfowR); consult the Actions page for hosted CI results. See [verification](verification.md).

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

## Prioritized next work

1. **Finish evidence:** resolve catalog grants through the administrator, run isolated Delta acceptance, fix any real failures, and record actual output.
2. **Close recovery gaps:** add interruption-mid-rollback and exact frozen-outcome preservation assertions, then run them.
3. **Validate consumption:** execute all SQL datasets with registered IDs, test metric/filter behavior, create/export the real dashboard and capture screenshots.
4. **Complete the portfolio evidence:** record the walkthrough, retain hosted CI results and update status links. Source and the owner-selected GPL-3.0 license are published.
5. **Only then expand scope:** benchmark larger data, consider distributed ingestion/native window selection, retention, alerting, and richer source contracts.

These are ordered milestones, not delivery-date promises. The original four-day estimate assumed a working workspace and PySpark/SQL familiarity; permission blockers prevent treating that estimate as an achieved schedule.

## Definition of the first portfolio release

A viewer can inspect source and documentation without workspace access, see genuine dashboard evidence, and trace all claims to passing checks. Persisted correction/rerun/replay behavior must match the independent oracle. [Release checklist](release-checklist.md).
