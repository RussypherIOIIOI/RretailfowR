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
| Incremental processing | Occurrence identity, immutable ledger and guarded MERGE | [Pipeline](../retailflow/pipeline.py); persistence awaits Delta acceptance |
| PySpark | Validation UDF, FK joins, grouped selection, typed projection | [Transforms](../retailflow/spark_transform.py); nine live checks passed |
| Dimensional modeling | Order-line fact, Type 1 dimensions, daily aggregate | [Model](data-model.md); persisted Gold unverified |
| Data quality | Multiple reasons, exclusive dispositions, retained audit | [Quality](data-quality.md); local/Spark checks passed, Delta history pending |
| Reliability | Frozen decisions, snapshots, gated pointer and rollback | [Architecture](architecture.md); fault suite written, not run |
| Orchestration | Six tasks, retries, timeouts, one concurrent run | [Deployment](../evidence/deployment.json); job deployed, pipeline incomplete |
| Analytics | Defined metrics, filter semantics and snapshot pinning | [Dashboard](../dashboard/README.md); live validation pending |
| Delivery discipline | Fixtures, tests, review fixes and evidence boundaries | [Testing](testing.md), [review](review.md), [verification](verification.md) |

## Measurable demonstration

Expected net sales progress **USD 55.00 → 91.00 → 98.00**. Arrival alone leaves USD 91.00 unchanged; explicit replay admits the missing-customer line. These values are an acceptance oracle, not a business outcome. Local simulation agrees with independent calculations; persisted Gold results remain unobserved.

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

**Project card:** “RetailFlow is a Databricks sales lakehouse implementation for messy synthetic orders. It demonstrates explicit revision handling, inspectable rejection evidence and gated publication. Twenty-four local tests and nine live Spark checks passed; end-to-end Delta and dashboard validation are pending scoped catalog access.”

**Resume bullet:** “Implemented a PySpark/Delta Lake sales lakehouse with deterministic fixtures, revision-aware merge logic, data-quality quarantine and a deployed six-task Lakeflow Job; verified 24 local tests and nine live Spark checks.”

Do not describe the dashboard as launched or recovery as proven until those gates pass. Update dated counts with fresh evidence. No throughput, uptime or financial-impact claim is supported.

## Portfolio placement

RetailFlow can be the data engineering centerpiece alongside GitPulse (API/application integration) and IncidentLens (applied AI/evaluation). Those adjacent project descriptions are positioning context, not evidence supplied here. [Walkthrough](walkthrough.md) · [release checklist](release-checklist.md).
