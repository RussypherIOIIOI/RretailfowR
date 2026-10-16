# Testing strategy and acceptance matrix

Test layers establish different facts. Local Python success does not establish Delta behavior; a deployed job does not establish a successful run. [Dated results](verification.md) and [evidence provenance](../evidence/README.md) are authoritative.

## Layers

| Layer | Entry point | What it establishes | Recorded status |
|---|---|---|---|
| Pure contracts | tests/test_*.py via pytest | Validation, revision decisions, manifest identity, lifecycle policy, independent fixture totals | 24 passed |
| Static/build | Ruff; Python build | Source lint and distributable wheel | Passed |
| Real Spark | tests/spark_acceptance.py via notebooks/spark_checks.py | Runtime validation, FK joins, selection and typed projection | Nine checks passed |
| Persisted Delta | tests/delta_acceptance.py via notebooks/integration.py | MERGE, ledgers, snapshots, retries, replay and recovery assertions | Not run; catalog permission blocked |
| Dashboard | Execute dashboard/*.sql and test widgets | SQL compatibility, pinned snapshots, metrics and filters | Not run |
| GitHub CI | .github/workflows/ci.yml | Repeat local checks and wheel build in hosted CI | Passed on publication commit 37cf3da; [evidence](../evidence/github-ci.json) |

Local commands are in [quickstart](quickstart.md). Remote submission and output inspection are in [runbook](runbook.md). The Spark script needs the deployment state and wheel from scripts.deploy; it does not create project tables. The Delta script creates an explicitly selected, new test namespace and intentionally mutates test data.

## Behavioral coverage

| Scenario | Local / Spark evidence | Persisted acceptance |
|---|---|---|
| Money precision, invalid timestamps/dates/quantity, multiple reasons | test_contracts.py; spark_acceptance.py | Cases included; unexecuted |
| Deterministic winners, stale records and equal-revision conflicts | test_contracts.py; test_oracle.py; Spark checks | batch2 and final-line assertions; unexecuted |
| Higher revision with same payload advances watermark | Local contract/oracle checks | Final revision assertion; unexecuted |
| Immutable batches, rename identity, malformed CSV | test_manifest.py; test_contracts.py | Rename and content-tampering assertions; unexecuted |
| Unknown dimension and explicit replay | test_oracle.py; Spark FK checks | Arrival keeps 91.00, replay yields 98.00; unexecuted |
| Rerun does not inflate Bronze or sales | Local identity/contract checks only | Same evaluation plus new evaluation; unexecuted |
| Frozen evaluation and partial dimension merge interruption | Policy unit coverage is not persistence proof | Injected boundaries; unexecuted |
| Silver complete / partial Gold / stage complete interruptions | No local persistence substitute | Injected boundaries; unexecuted |
| Failed rejection gate preserves current publication | No local persistence substitute | Strict threshold assertion; unexecuted |
| Abandon unpublished work and restore Silver | Lifecycle permission/policy tests | Real RESTORE assertion; unexecuted |
| Daily grouped totals and final facts | Independent local totals | Group/final-line assertions and quality checks; unexecuted |

Paths in this matrix are relative to [tests](../tests/). Do not turn a scenario's presence in a test file into a passed result.

## Independent oracle

[expected.json](../fixtures/expected.json) is manually calculated, separate from transformation logic. [test_oracle.py](../tests/test_oracle.py) drives batches through pure contracts and compares totals. The Delta acceptance suite compares persisted results to the same independent values. This prevents a test from simply recomputing expected output with the production transform.

Expected progression: 55.00 / 4 units / 2 orders / 3 lines; 91.00 / 7 / 4 / 5; arrival unchanged; explicit replay 98.00 / 8 / 5 / 6. Distinct order counts are calculated from order IDs, not added across product groups.

## Failure-injection scope and gaps

The Delta suite interrupts after Bronze, after customer evaluation freeze, after customer merge, after Silver, during Gold staging and after complete staging. It also forces a failing reject threshold and tests explicit abandonment/restoration. The complete suite remains unexecuted.

Two important follow-up tests are **not implemented as full assertions**: crash midway through rollback followed by restoration of all three tables, and exact frozen-outcome equality across retries (beyond pointer/totals assertions). Also unproven: multi-writer behavior (unsupported), large data performance, dashboard cross-refresh behavior and long-term snapshot cleanup.

## Change verification

For logic changes: first reproduce a failing behavior, implement the narrow fix, run relevant local tests and then the required runtime layer. Review revision, freeze and publication changes independently. For documentation-only changes: verify relative links, code/schema references, diagram source parity and claim consistency; do not rerun expensive remote workloads without a concrete need.

The documentation revision does not change pipeline code or upgrade its runtime verification status.
