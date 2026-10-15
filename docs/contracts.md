# RetailFlow contracts

USD only. Natural keys are trimmed, case-sensitive identifiers (1–64 ASCII letters, digits, underscores or hyphens). Blank values are invalid. Regions normalize to uppercase and are NORTH, SOUTH, EAST, WEST. Timestamps must be ISO-8601 with an explicit UTC offset; output is UTC. Dates are strict YYYY-MM-DD, from 2020-01-01 through 2030-12-31 (fixed demo horizon). Revisions are positive signed 32-bit integers. Quantity is 1–1000000. Money accepts at most 2 fractional digits, is nonnegative DECIMAL(18,2); gross and net must fit that precision. No silent rounding of excess precision.

| Entity | Grain/key | Required business fields | Ownership |
|---|---|---|---|
| customers | customer_id | customer_name, home_region | source customer system |
| products | product_id | product_name, category, current_price | source product system |
| orders | order_id + line_id | customer_id, product_id, order_date, sale_region, quantity, unit_price, discount_amount | source order system |

Every entity also requires source_revision and source_updated_at. Higher revisions replace the entire record. Missing keys never delete records. Dimensions are Type 1; line price and sale_region retain transaction meaning. Audit timestamp is excluded from the business payload fingerprint; revision is separate. Equal business payload/revision is an exact logical duplicate, even if audit timestamp differs.

Bronze stores one physical CSV record occurrence, including raw text, original filename, file SHA256, batch, record index, ingestion UTC timestamp. UTF-8 CSV is one physical line per record; embedded newlines are deliberately unsupported. Malformed individual lines are retained and rejected. Wrong headers/encoding/manifest hashes fail the batch. File limit 10 MiB and 10000 records; grouped revision selection is bounded to 1000 candidates per key. These deliberate v1 limits fail loudly.

Occurrence identity is SHA256(batch, entity, file bytes fingerprint, physical line number). Rename within a batch retains identity. Cross-batch occurrences remain separate audit evidence. Immutable manifest identity ignores filenames but includes entity, bytes fingerprint and row count. A reused batch ID with different content fails.

Silver validates before selection, then compares valid revisions against the existing target. Conflicting equal revisions are quarantined. An established target wins a same-revision disagreement. First-seen simultaneous conflicts exclude that entire revision; an earlier unambiguous revision can win. Outcomes are accepted_winner, exact_duplicate, stale_superseded, conflict, invalid. Each evaluation has exactly one outcome per occurrence. A frozen evaluation is reused on retry; a new evaluation is required for explicit replay.

Gold: fact key (order_id,line_id), dimensions natural keys, daily grain (order_date,sale_region,product_id). Distinct orders must be recalculated from fact at the selected filter grain. Versioned snapshots use one publication_id across all tables. One pointer switches after quality checks; dashboard queries pin a publication for cross-query consistency.
