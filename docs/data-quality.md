# Data quality, corrections and replay

The normative contract is [contracts.md](contracts.md). Implementations are [contracts.py](../retailflow/contracts.py), [spark_transform.py](../retailflow/spark_transform.py) and [pipeline.py](../retailflow/pipeline.py).

## Validate before choosing a revision

A higher revision is eligible only after parsing, field validation and (for orders) foreign-key checks. Customer/product updates run before order evaluation. An invalid new record cannot erase an existing valid version.

| Rule | Reason code(s) | Result |
|---|---|---|
| Missing required value | `MISSING_<FIELD>` | Invalid; other field-specific reasons may also apply |
| Identifier syntax | `INVALID_<ID_FIELD>` | Invalid |
| Revision range/format | INVALID_REVISION | Invalid |
| Timestamp format, offset, date/time or UTC overflow | INVALID_SOURCE_UPDATED_AT | Invalid |
| Unsupported region | INVALID_HOME_REGION / INVALID_SALE_REGION | Invalid |
| Name/category over 200 characters | INVALID_CUSTOMER_NAME / INVALID_PRODUCT_NAME / INVALID_CATEGORY | Invalid |
| Invalid money syntax, sign or precision | INVALID_CURRENT_PRICE / INVALID_UNIT_PRICE / INVALID_DISCOUNT_AMOUNT | Invalid |
| Date syntax or horizon | INVALID_ORDER_DATE | Invalid |
| Quantity range/format | INVALID_QUANTITY | Invalid |
| Derived amount exceeds DECIMAL(18,2) | MONEY_OVERFLOW | Invalid |
| Line discount exceeds gross | DISCOUNT_EXCEEDS_GROSS | Invalid |
| Incorrect CSV row shape / quoting | MALFORMED_CSV | Raw line retained; invalid |
| Missing referenced dimension | UNKNOWN_CUSTOMER / UNKNOWN_PRODUCT | Invalid; explicit replay may later resolve |
| Same revision disagrees on business payload | REVISION_CONFLICT | Conflict; no conflicting candidate applied |

Reasons are arrays. Count distinct rejected occurrences separately from exploded reason counts. A malformed row can also have missing-field reasons.

Wrong headers, undecodable UTF-8, manifest/hash disagreement, unsafe paths and exceeded file limits fail ingestion rather than becoming ordinary record rejections. An input file is at most 10 MiB and 10,000 data records; one batch has exactly one file per entity. Embedded newlines within quoted fields are unsupported. Physical framing recognizes CRLF, LF and CR; a Unicode line separator within a value is not a record boundary.

## Revision decision order

For each business key, validate all candidates, then group valid candidates by source_revision. Determine eligible revisions before classifying individual rows:

1. If a first-seen revision has different payload hashes, exclude all candidates at that revision.
2. If the current target has that same revision, keep the established target; matching payloads are duplicates and disagreements are conflicts.
3. Among remaining revisions strictly greater than the target, choose the highest. For identical candidates at that revision, select the smallest occurrence_id deterministically.
4. Classify every occurrence with exactly one disposition below. Invalid candidates never participate in precedence.

| Disposition | Meaning | Changes Silver? | Quarantine? |
|---|---|---|---|
| accepted_winner | Chosen valid newer candidate | Yes | No |
| exact_duplicate | Matches established target at same revision, or repeats winning candidate | No | No |
| stale_superseded | Valid but not a winning/duplicate/conflict candidate | No | No |
| conflict | Equal revision disagrees | No | Yes |
| invalid | Parse, field or FK reasons | No | Yes |

Conflict classification precedes stale classification in the resolver: an ambiguous incoming revision can be classified conflict even if an established newer target already exists. A higher revision with identical payload still advances the target revision watermark. Source timestamps and arrival timestamps never break revision ties.

**Boundary:** simultaneous first-seen conflicts are handled consistently within an evaluation; the design does not promise order-invariance across separately arriving conflicting batches.

## Walk through the fixture

| Key / case | Input behavior | Expected decision |
|---|---|---|
| A1 / 1 | Revision 2 changes product, date, region and value | Replace revision 1; net 35.00 |
| A2 / 1 | Invalid newer correction | Preserve valid revision 1; net 25.00 |
| A2 / 2 | Same-revision disagreement | Keep established payload; net 10.00; reject disagreement |
| A3 / 1 | Higher identical payload, then intermediate stale revision | Advance to revision 3; net 15.00 |
| A4 / 1 | Customer C9 absent, then arrives | Remains rejected until batch2 is explicitly replayed; then net 7.00 |
| A5 / 1 | Two conflicting first-seen revision 2 payloads | Exclude revision 2; unambiguous revision 1 wins, net 6.00 |

These are local oracle expectations, not persisted Gold observations. [Expected final lines](../fixtures/expected.json).

## Retry, replay and rejection history

**Retry:** same evaluation_id and identical batch/replay scope. Reuse the frozen entity outcomes and finish writes. It must not silently revalidate against changed state.

**Replay:** new evaluation_id with replay_batches identifying previously ingested completed batches. Re-evaluate against current dimensions. The arrival batch alone does not reprocess previous rejects.

ops.evaluations keeps each evaluation's reasons and disposition. Gold rejected_records contains each ever-rejected occurrence once, using its latest active outcome and a resolved flag. A successful replay may leave the latest reasons empty; inspect earlier ops rows to see the original reasons. Abandoned/abandoning runs are excluded from the published rejection-history calculation. Earlier published snapshots remain historical views of what was known then.

## Publication gates

Mandatory checks cover fact/dimension/daily key uniqueness and nulls, valid line amounts, dimension referential integrity, total sales reconciliation, full grouped reconciliation, per-entity occurrence conservation and the three entity headers. A separate max_reject_fraction gate measures invalid/conflict rows across the current evaluation's three entities.

The demo default **1.0 permits any rejection fraction** because bad records are intentional; integrity checks still apply. This threshold is not a production service objective. Choose a justified threshold for a real feed and inspect ops.gates.report_json when it fails. [Runbook](runbook.md) · [testing](testing.md).
