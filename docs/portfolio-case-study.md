# Portfolio case study: RetailFlow

## Problem and audience

Sales dashboards can appear correct while duplicate deliveries inflate revenue, invalid corrections overwrite valid orders, or missing dimensions silently remove transactions. RetailFlow asks which products and regions drive sales and what evidence supports those numbers.

This personal project helps hiring viewers assess data engineering judgment. It uses synthetic customers, products and order lines with deliberate defects. There is no real customer dataset, claimed business savings or production traffic.

## Approach

Bronze preserves raw occurrences and file provenance. Silver validates values, resolves revisions and retains rejection evidence. Gold models a fact table, dimensions and daily aggregates. A six-task Lakeflow Job coordinates the sequence. Publication is separate from computation: snapshots are staged and checked before a pointer makes them current.

The second batch contains a valid correction moving a line across date/product/region, exact duplicates, stale records, equal-revision conflicts, invalid newer records, malformed CSV and a sale referencing a missing customer. A later customer arrival requires explicit replay before that sale can contribute to Gold.

## Evidence of skills

| Skill | Concrete implementation | Evidence and limit |
|---|---|---|
| Data contracts | Keys, types, revision rules and bounded format | [Contracts](contracts.md); local tests passed |
| Incremental processing | Occurrence identity, immutable ledger and guarded MERGE | [Real demo verification](../evidence/release-20261030/demo-persisted.json); five successful jobs, conserved Bronze and facts |
| PySpark | Validation UDF, FK joins, grouped selection, typed projection | [Transforms](../retailflow/spark_transform.py); nine live checks passed |
| Dimensional modeling | Order-line fact, Type 1 dimensions, daily aggregate | [Model](data-model.md); real registered Gold results match the independent oracle |
| Data quality | Multiple reasons, exclusive dispositions, retained audit | [Real SQL receipts](../evidence/release-20261030/demo-persisted.json); 8 ever rejected, 7 unresolved, 1 resolved |
| Reliability | Frozen decisions, snapshots, gated pointer and rollback | [Full successful Delta acceptance](../evidence/release-20261030/delta-acceptance-passed.json), including exact frozen outcomes and interrupted three-table rollback/resume |
| Orchestration | Six tasks, retries, timeouts, one concurrent run | [Actual run IDs](../evidence/release-20261030/demo-persisted.json); all five demo jobs and all six tasks per job succeeded |
| Analytics | Defined metrics, filter semantics and snapshot pinning | [Four real datasets and 12 SQL checks](../evidence/release-20261030/dashboard-sql.json); rendered publication remains approval-blocked |
| Delivery discipline | Fixtures, tests, review fixes and evidence boundaries | [Testing](testing.md), [review](review.md), [verification](verification.md) |

## Measurable demonstration

Observed registered Gold net sales progress **USD 55.00 → 91.00 → 91.00 → 98.00**. Arrival alone leaves USD 91.00 unchanged; explicit replay admits the missing-customer line. An identical rerun preserves 27 unique Bronze occurrences, four evaluations, six final fact lines and the rejection history. These synthetic demonstration results agree with an independently calculated oracle; they are not a business-impact measurement. [Actual persisted verification](../evidence/release-20261030/demo-persisted.json).

Explain why each line changed, which rows were rejected, and why a rerun should preserve sales. The story is correctness under imperfect input.

## Interview discussion

- Revision numbers determine precedence; timestamps provide audit context.
- Natural keys, payload hashes and occurrence IDs solve distinct identity problems.
- One Delta pointer is atomic; several tables are not one transaction. Readers pin a registered publication.
- Type 1 dimensions keep v1 small. Sale region and transaction price stay on the fact.
- Driver parsing and grouped Python selection are bounded; scaling requires new design and evidence.
- Independent review found timestamp, CSV framing and recovery defects. Fixes and remaining gaps are recorded.

[Architecture decisions](architecture-decisions.md) explain these tradeoffs.

## Portfolio copy accurate today

**Project card:** "RetailFlow is a Databricks sales lakehouse for messy synthetic orders. Five six-task jobs and actual Gold SQL verify corrections, rerun conservation, explicit replay and retained rejection history. The real 55-to-91-to-98-dollar progression matches an independent oracle, and full isolated Delta recovery acceptance passed. Rendered dashboard publication remains a separate approval gate."

**Resume bullet:** "Implemented a PySpark/Delta Lake sales lakehouse with deterministic fixtures, revision-aware merges, quality quarantine and six-task orchestration; verified five real jobs, persisted correction/replay totals and rejection-history retention."

Do not describe the dashboard as launched or recovery as proven until those gates pass. Update dated counts with fresh evidence. No throughput, uptime or financial-impact claim is supported.

## Portfolio placement

RetailFlow can be the data engineering centerpiece alongside GitPulse (API/application integration) and IncidentLens (applied AI/evaluation). Those adjacent project descriptions are positioning context, not evidence supplied here. [Walkthrough](walkthrough.md) · [release checklist](release-checklist.md).
