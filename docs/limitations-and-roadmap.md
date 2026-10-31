# Limitations and roadmap

## Current release boundary

Scoped permissions are repaired, and five real six-task jobs passed. Actual registered Gold results verify correction, arrival, replay, rerun conservation and rejection history. Full isolated Delta acceptance passed, including interrupted rollback, exact frozen outcomes, historical/last-good retention and immutable-batch tampering. Four dashboard datasets and 12 SQL assertions passed, and the real dashboard definition was exported. Rendered dashboard publication requires a separate private publisher-mode approval. Metric/rejection captures and recording remain incomplete. Source is proposed in [draft PR #1](https://github.com/RussypherIOIIOI/RretailfowR/pull/1). See [current evidence](../evidence/release-20261030/README.md).

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

1. **Obtain the remaining publication decision:** the exact private publisher-mode operation is pending; no broader table grants or audience changes are proposed.
2. **Validate rendered consumption:** test the real date/product/region and separate quality controls, then capture actual dashboard metrics/rejects. SQL checks and the real export already pass/exist.
3. **Retain completed implementation evidence:** full acceptance and all five demo jobs passed; preserve the actual successful output plus both earlier failed attempts and diagnoses.
4. **Complete the portfolio evidence:** record the walkthrough, retain hosted CI results and update status links. Source and the owner-selected GPL-3.0 license are published.
5. **Only then expand scope:** benchmark larger data, consider distributed ingestion/native window selection, retention, alerting, and richer source contracts.

These are ordered milestones, not delivery-date promises. The original four-day estimate assumed a working workspace and PySpark/SQL familiarity; permission blockers prevent treating that estimate as an achieved schedule.

## Definition of the first portfolio release

A viewer can inspect source and documentation without workspace access, see genuine dashboard evidence, and trace all claims to passing checks. Persisted correction/rerun/replay behavior must match the independent oracle. [Release checklist](release-checklist.md).
