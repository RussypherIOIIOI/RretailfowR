# Testing strategy and acceptance matrix

Test layers establish different facts. Local Python success does not establish Delta behavior; a deployed job does not establish a successful run. [Dated results](verification.md) and [evidence provenance](../evidence/README.md) are authoritative.

## Layers

| Layer | Entry point | What it establishes | Recorded status |
|---|---|---|---|
| Pure contracts and release guard rails | tests/test_*.py via pytest | Validation, revision decisions, manifest identity, lifecycle policy, independent fixture totals, refusal to grant on unrelated/nonempty schemas, evidence completeness and fresh attempt isolation | 30 tests and seven subtests passed; [evidence](../evidence/release-20261030/local-verification-current.json) |
| Static/build | Ruff; Python build | Source lint and distributable wheel | Passed |
| Real Spark | tests/spark_acceptance.py via notebooks/spark_checks.py | Runtime validation, FK joins, selection and typed projection | Nine checks passed |
| Persisted Delta | tests/delta_acceptance.py via notebooks/integration.py | MERGE, ledgers, snapshots, retries, replay and recovery assertions | Full isolated acceptance passed, plus five real demo jobs; [complete output](../evidence/release-20261030/delta-acceptance-passed.json) |
| Dashboard | Execute dashboard/*.sql and test widgets | SQL compatibility, pinned snapshots, metrics and filters | Four datasets and 12 SQL checks passed; real export retained; rendered publication approval pending |
| GitHub CI | .github/workflows/ci.yml | Repeat local checks and wheel build in hosted CI | Passed on acceptance source `f43dcc2`; [run](https://github.com/RussypherIOIIOI/RretailfowR/actions/runs/41150023703) |

Local commands are in [quickstart](quickstart.md). Remote submission and output inspection are in [runbook](runbook.md). The Spark script needs the deployment state and wheel from scripts.deploy; it does not create project tables. The Delta script creates an explicitly selected, new test namespace and intentionally mutates test data.

## Behavioral coverage

All persisted scenarios below now passed in full isolated attempt C. [Actual successful parent/task output and source hashes](../evidence/release-20261030/delta-acceptance-passed.json). Detailed edge-case validation also retains its local/Spark evidence; a tiny fixture is not a scale benchmark.

| Scenario | Local / Spark evidence | Persisted acceptance |
|---|---|---|
| Money precision, invalid timestamps/dates/quantity, multiple reasons | test_contracts.py; spark_acceptance.py | Passed for persisted fixture cases; detailed validation edges also have local/Spark checks |
| Deterministic winners, stale records and equal-revision conflicts | test_contracts.py; test_oracle.py; Spark checks | Passed batch2 and independent final-line assertions |
| Higher revision with same payload advances watermark | Local contract/oracle checks | Passed final revision assertion |
| Immutable batches, rename identity, malformed CSV | test_manifest.py; test_contracts.py | Passed rename, byte/hash and refreshed-manifest tampering checks |
| Unknown dimension and explicit replay | test_oracle.py; Spark FK checks | Passed arrival at 91.00, replay at 98.00, original rejection retained, malformed row unresolved |
| Rerun does not inflate Bronze or sales | Local identity/contract checks | Passed same evaluation, new evaluation and real six-task job rerun |
| Frozen evaluation and partial dimension merge interruption | Policy unit coverage is not persistence proof | Passed exact equality of frozen data and metadata across injected boundaries |
| Silver complete / partial Gold / stage complete interruptions | No local persistence substitute | Passed all injected boundaries and retained current publication |
| Failed rejection gate preserves current publication | No local persistence substitute | Passed strict threshold failure and last-good retention |
| Abandon unpublished work and restore Silver | Lifecycle permission/policy tests | Passed interruption after one real RESTORE, blocked new work, retry, all-three-table equality and repeat abandonment |
| Daily grouped totals and final facts | Independent local totals | Passed grouped/final-line reconciliation, historical 55.00/91.00 snapshots and post-rollback 98.00 |

Paths in this matrix are relative to [tests](../tests/). Do not turn a scenario's presence in a test file into a passed result.

## Independent oracle

[expected.json](../fixtures/expected.json) is manually calculated, separate from transformation logic. [test_oracle.py](../tests/test_oracle.py) drives batches through pure contracts and compares totals. The Delta acceptance suite compares persisted results to the same independent values. This prevents a test from simply recomputing expected output with the production transform.

Expected progression: 55.00 / 4 units / 2 orders / 3 lines; 91.00 / 7 / 4 / 5; arrival unchanged; explicit replay 98.00 / 8 / 5 / 6. Distinct order counts are calculated from order IDs, not added across product groups.

## Failure-injection scope and gaps

The Delta suite interrupts after Bronze, after customer evaluation freeze, after customer merge, after Silver, during Gold staging and after complete staging. It forces a failing reject threshold and interrupts rollback after one real table restore, requiring the retry to restore all three tables. Full attempt C passed; the two preceding actual failures are retained alongside the successful output.

Exact frozen outcomes and interrupted three-table rollback/resume executed in attempt B; that run later failed when the test used unsupported append-mode file I/O on the volume. Full corrected attempt C passed using sequential fixture rewriting and a fresh logical table/file namespace within the same approved schemas/volume. It also passed historical snapshot totals, original C9 rejection retention and malformed records remaining rejected. [Current evidence](../evidence/release-20261030/README.md). Still unproven: multi-writer behavior (unsupported), large data performance, rendered dashboard cross-refresh behavior and long-term snapshot cleanup.

## Change verification

For logic changes: first reproduce a failing behavior, implement the narrow fix, run relevant local tests and then the required runtime layer. Review revision, freeze and publication changes independently. For documentation-only changes: verify relative links, code/schema references, diagram source parity and claim consistency; do not rerun expensive remote workloads without a concrete need.

The documentation revision does not change pipeline code or upgrade its runtime verification status.
