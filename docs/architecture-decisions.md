# Architecture decisions

1. **Revision controls precedence.** Source timestamps are audit data. Revisions are full replacements. A higher identical payload still advances the revision. Invalid data is removed from selection before comparing revisions. An established equal-revision target is preserved; simultaneous first-seen conflicts exclude that revision. Cross-batch conflict order invariance is not promised.

2. **Identity has three levels.** Natural keys identify business entities. A normalized business payload hash identifies content independently of revision/audit timestamps. A physical occurrence ID hashes batch, entity, file bytes and physical record number. Renaming a file within its immutable batch does not create occurrences; cross-batch copies remain distinct evidence but cannot inflate sales.

3. **Silver has explicit stored types.** Customer/product/order business columns are stored alongside normalized JSON and provenance in Delta. Quantity/revision are integral, dates are DATE, audit timestamps are TIMESTAMP UTC, and line money is DECIMAL(18,2). The JSON preserves normalized validation evidence; Gold does not rely on unsafe casts of raw strings. Aggregate money uses Spark's wider decimal sum type.

4. **Frozen evaluations make retries explainable.** Each entity evaluation atomically writes its outcomes and header into one Delta partition before applying Silver merges. A retry reuses that exact evidence. Foreign keys are checked after customer/product updates. Unknown dimensions require a new explicit replay evaluation after arrival.

5. **Publication is a separate operation.** Gold snapshots share a publication ID. The gate checks keys, foreign keys, amount equations, occurrence conservation, total and full-group reconciliation, and a separately configured rejection threshold. One Delta row atomically registers the publication in history and switches the current pointer. No multi-table transaction is claimed. Snapshots are staged before the switch; queries bind one registered publication across datasets.

6. **Failed work blocks subsequent work.** Resume the same evaluation ID after an infrastructure failure. A permanently failed evaluation requires explicit rollback: capture pre-run Silver versions, mark abandoning, restore all three tables, then mark abandoned. New work is blocked until restoration finishes. Bronze and evaluation history remain inspectable. Abandoned outcomes do not become published quality evidence. Do not vacuum captured versions while a run is unresolved.

7. **Small bounded first release.** Three CSV files per batch, driver parsing bounded to 30 MiB total, Spark record validation and per-key selection, full Gold recomputation. Python contracts use only the standard library; runtime PySpark/Delta stay Databricks-managed. Moving to larger files would require distributed raw record framing and native window-based selection. That is a future change with new performance evidence, not hidden complexity in v1.

8. **One writer is an operational contract.** The job uses max_concurrent_runs=1. Do not create another writer job for the same schema prefix or mutate Silver manually. Metadata sequence allocation and rollback rely on this restriction; they are not distributed locks.

9. **Dashboard deployment follows evidence.** SQL and layout are supplied now. The actual dashboard export and screenshots will be captured only after successful table-backed SQL validation. A plausible-looking JSON file or mocked screenshot is not deployment evidence.

## Alternatives considered and consequences

| Choice | Alternative | Reason for v1 choice / consequence |
|---|---|---|
| Explicit revision precedence | Latest ingestion timestamp wins | Re-delivery is not a correction; source must provide authoritative revisions |
| Retain invalid occurrences | Drop invalid rows | Enables inspection and later explicit replay; increases audit storage |
| Type 1 dimensions | SCD Type 2 | Smaller inspectable model; historical descriptions are not retained |
| Full Gold snapshots | Incremental aggregate updates | Simpler correction/reconciliation across changed date/product/region; more recomputation |
| One pointer plus pinned queries | Treat multi-table writes as atomic | Makes transaction boundary explicit; consumers must coordinate selected version |
| Bounded driver parsing / grouped resolver | Distributed ingestion / native windows | Small reproducible fixture scope; no scale claim and future redesign required |
| Serial writer and explicit rollback | Concurrent writers with locking | Keeps recovery comprehensible; operational exclusivity is mandatory |

These are implementation decisions, not benchmark comparisons. [Architecture](architecture.md) explains mechanisms; [limitations](limitations-and-roadmap.md) describes when to revisit them.
