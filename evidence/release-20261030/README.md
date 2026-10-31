# Release evidence — 30 October 2026

## Current checkpoint — 31 October 2026

| Requirement | Observed status | Evidence |
|---|---|---|
| Exact scoped permissions | **Passed** — eight schemas and two fixture volumes; no catalog grant added | [Applied plan](permission-apply.json), [effective privileges verified as M2M](permission-effective.json) |
| Correct existing job destination | **Passed** — job `1055508848756404`, six tasks, concurrency one, `tmc_solutions_jvs`; no schedule | [Current deployment](deployment-current.json) |
| Real baseline, correction, arrival, replay and identical rerun | **All five succeeded**, all six tasks per run | [Persisted verification and run IDs](demo-persisted.json), `demo-*-outputs.json` |
| Persisted Gold results | **Passed** — `demo01` 55.00/4 units/2 orders/3 lines; `demo02` and `demo03` 91.00/7/4/5; `demo04` 98.00/8/5/6 | [Real SQL receipts](demo-persisted.json) |
| Real rerun conservation | **Passed** — 27 unique Bronze occurrences, four evaluations, final facts unchanged | [Real SQL receipts](demo-persisted.json) |
| Exact frozen outcomes in the real job rerun | **Passed** — all 21 rows and fields unchanged, SHA256 `daca53d2fc2952ad5fba7c4f0805121f1f9f3ac8afdc4bcf1c9e6ba8c618aa30` | [Comparison and statement IDs](demo04-frozen-rerun-comparison.json) |
| Rejection history and explicit replay | **Passed** — C9's original invalid occurrence remains in ops and becomes resolved/accepted in Gold; 8 ever rejected, 7 unresolved, 1 resolved | [Real SQL receipts](demo-persisted.json) |
| Full Delta failure/recovery acceptance | **Passed**, fresh attempt C: parent `853846258218717`, task `833933180481456`, both SUCCESS; result `passed`, not truncated | [Complete successful result and provenance](delta-acceptance-passed.json), [raw parent state](delta-attemptc-run.json), [raw task output](delta-attemptc-output.json) |
| Isolated Delta attempt B | **Failed in test fixture I/O after interrupted rollback/resume assertions passed** — append mode is unsupported on managed volumes | [Failure](delta-attemptb-failed-output.json), [executed suite](delta-attemptb-suite.py) |
| Initial isolated Delta attempt | **Failed at a test assertion**, preserved without reset/deletion | [Failure](delta-initial-failed-output.json), [diagnosis](delta-assertion-diagnosis.json), [executed original suite](delta-initial-suite.py) |
| Strict bundle validation | **Passed**, zero warnings. Bundle deployment itself is not claimed | [Current CLI receipt](bundle-validation-current.json) |
| Four actual Gold SQL datasets | **Passed**, one registered publication `demo04` | [Dataset receipts and 12 checks](dashboard-sql.json) |
| SQL date/product/region and separate quality filters | **Passed** — date 63, product 38, WEST 28, quality batch2 6 unresolved, resolved history 1, unregistered ID zero rows | [SQL receipts](dashboard-sql.json) |
| Dashboard creation and real export | **Passed** — actual draft ID `01f1d4bd43b6157d96bdf99719c7f0c3` | [Server resource](dashboard-resource.json), [actual exported definition](../../dashboard/retailflow.lvdash.json) |
| Rendered dashboard metrics and filter testing | **Blocked** — browser owner has no direct SELECT on the service principal's Gold tables | Proposed private publisher mode requires approval; see below |
| Real job screenshot | **Captured and inspected** | [Six successful tasks and run ID](../../docs/assets/lakeflow-baseline-success.jpg) |
| Real full-acceptance screenshot | **Captured and inspected** — actual passed output and parent/task IDs | [Successful Delta acceptance](../../docs/assets/delta-acceptance-success.jpg) |
| Dashboard metric/rejection screenshots and two-minute recording | **Not captured/recorded** pending rendered dashboard access | Recording encoder prepared in [render_walkthrough.py](../../scripts/render_walkthrough.py); no video link exists yet |
| Production/main publication | **Not performed** | Work remains on [draft PR #1](https://github.com/RussypherIOIIOI/RretailfowR/pull/1) |

The completed demo run IDs are baseline `165301235945373`, correction `157203734280731`, arrival `260330560109801`, replay `451352689364258`, and rerun `772106039108256`.

### Retained failure and corrected fresh namespace

The initial run `806119123199987` / task `1116104186911172` reached the replay assertions, then the newly added test incorrectly required every row carrying `UNKNOWN_CUSTOMER` to become resolved. Actual persisted diagnosis showed two such rows: the recoverable C9 order and a malformed CSV row with many additional defects. C9 resolved correctly; malformed CSV correctly remained rejected. The corrected assertion selects the C9 payload and separately requires the malformed occurrence to remain unresolved. No production transform was changed to satisfy this test.

Attempt B used fresh `attemptb_*` tables/views and fixture files in the approved schemas/volume. It reached and passed the interrupted three-table restoration, repeated abandonment, last-good pointer, audit-history, and post-rollback 98.00 assertions, then failed at append-mode opening of the tiny tamper-test CSV with `OSError: [Errno 29] Illegal seek`. [Databricks documents that direct-append and random writes are unsupported](https://docs.databricks.com/aws/en/volumes/volume-files#limitations-of-working-with-files-in-volumes). The test now reads the tiny fixture and rewrites all changed bytes sequentially. No production transform was changed.

The successful full attempt C used fresh `attemptc_*` tables/views in the **same four approved** `retailflow_test20261030a_*` schemas and a fresh `attemptc` subdirectory in the **same approved** fixture volume. It created no new schema or volume and added no privileges. Fresh-table/path guards refuse collisions. Attempts A and B, their original source and outputs, all data and Delta history remain intact. Two local namespace tests prove table separation, unchanged schema/volume scope, and rejection of unsafe attempt identifiers. Local verification: **30 tests and seven subtests passed**, Ruff clean. [Hosted CI passed on source commit f43dcc2](github-ci-f43dcc2.json).

The complete successful output reports exact frozen-outcome hashes, interrupted three-table restoration/resumption, reruns/rename, original rejection retention and explicit replay, failed-gate last-good retention, historical 55.00/91.00 snapshots, changed-byte/manifest rejection, and post-rollback 98.00 results. It reports Spark 4.2.0. Both parent and task are SUCCESS; the actual notebook JSON says `status: passed` with `truncated: false`.

### Pending dashboard publication approval

Draft dashboard: https://dbc-9d765ae8-3bb9.cloud.databricks.com/sql/dashboardsv3/01f1d4bd43b6157d96bdf99719c7f0c3

Its [actual ACL](dashboard-permissions.json) contains only the creator service principal and inherited workspace admins. The SQL verifier succeeded as the approved service principal; the browser owner's individual-permission draft queries fail with `INSUFFICIENT_PERMISSIONS` on `tmc_solutions_jvs.retailflow_gold.fact_order_line_snapshots`.

The proposed action is `databricks lakeview publish 01f1d4bd43b6157d96bdf99719c7f0c3 --embed-credentials --warehouse-id ec9f4c81bc387245 --profile M2M`. This lets the unchanged private dashboard audience query using publisher `jarvis-cli-m2m`; it adds no catalog/table grants or viewers. **Automatic approval review rejected this publication because creation/export authorization did not include credential-embedding publication. The command did not execute, and no workaround was attempted.** User approval for that exact action is pending.

Acceptance is complete; do not duplicate run `853846258218717`. After explicit publication approval, perform the exact publish action once, retrieve published metadata, test rendered widgets/filters, re-export if the definition changes, capture actual metrics/rejects, and record the real walkthrough. Until those stages complete, this remains an incomplete portfolio release.

<details>
<summary>Historical pre-approval plan and original blockers (superseded by the checkpoint above)</summary>

At the initial checkpoint, no Delta result, dashboard, screenshot or video was claimed.

| Requirement | Status | Evidence / exact dependency |
|---|---|---|
| Execution identity and catalog inspection | Passed | [Access inspection](access-inspection.json); existing job runs as `jarvis-cli-m2m`, not the U2M administrator |
| Catalog repair | Pending approval | `workspace` does not exist. [Exact scoped plan](permission-plan.json) uses existing `tmc_solutions_jvs`; no catalog-wide grant |
| Local checks / lint / wheel | Passed | [Local result](local-verification.json); additional tests protect provisioning and evidence completeness |
| Strict bundle validation | Passed | [CLI result](bundle-validation.json); zero warnings, six tasks, concurrency one. Validation does not establish bundle deployment |
| Exact frozen-outcome assertions | Added; live execution blocked | [Delta suite](../../tests/delta_acceptance.py): all persisted evaluation fields, including metadata, must remain equal on retry |
| Interrupted rollback assertions | Added; live execution blocked | After one real RESTORE, interrupt before the second; require `abandoning`, block new work, retry and compare all three full Silver tables |
| Fresh Delta acceptance | Not run | Requires approved schemas `retailflow_test20261030a_{bronze,silver,gold,ops}` and fixture volume; suite rejects reused namespaces |
| Successful six-task demo and persisted 55 → 91 → 98 | Not run | Existing job `1055508848756404` still targets nonexistent `workspace`; no deployment mutation performed in this attempt |
| Reruns, rejects, replay, last-good retention | Assertions added/existing; live execution blocked | Delta suite also verifies 55/91 historical snapshots after 98 replay and original missing-customer rejection retention |
| Four SQL datasets and sales/quality filters | Prepared; not run | [Verifier](../../scripts/verify_dashboard.py); requires actual registered Gold publication. SQL success and rendered-widget success are separate gates |
| Dashboard creation/export | Not run | Deliberately depends on successful SQL validation; no invented `.lvdash.json` |
| Metrics/rejects/job screenshots | Not captured | Requires real successful job and rendered dashboard. Desktop/browser connection exists |
| Two-minute walkthrough / actual video | Not recorded | Requires live results and capture; [shot list](../../docs/walkthrough.md). No video URL exists |
| Production portfolio publication | Not performed | Exact repository is `RussypherIOIIOI/RretailfowR`; work is proposed on a draft branch. No main merge, dashboard audience change, or portfolio-site deployment |

The earlier 24-test baseline and nine Spark checks are historical evidence, not proof that the extended Delta suite passed. `fixtures/expected.json` and hard-coded filter expectations are independent oracles, not observed Gold output.

## Approval scope

Principal: `jarvis-cli-m2m`, application ID `e92b585c-22cc-4813-b00e-b894ea680a37`.

Catalog: `tmc_solutions_jvs`. Effective `USE_CATALOG` is already inherited through the workspace users group. Add **no catalog privilege**.

Create only the eight named empty schemas in [permission-plan.json](permission-plan.json). Grant `USE_SCHEMA`, `CREATE_TABLE`, `SELECT`, `MODIFY` on those schemas only. Preprovision two managed `fixtures` volumes and grant `READ_VOLUME` and `WRITE_VOLUME` on those exact volumes. Existing business schemas are outside the scope. No credentials, identity changes, table deletion, or security-control changes are proposed.

The handoff requires action-time approval for persistent sensitive/security-critical access changes. Approval is **pending**, not denied. No grant operation was attempted. The plan-only script ran locally; its `--apply` path has not been executed against Databricks.

## Resume after approval

Use the repository root and a Python environment installed from `requirements-dev.txt`. Profiles are the existing authorized profiles; never copy credentials into this checkout.

1. Review [permission-plan.json](permission-plan.json), approve it, then run `python -m scripts.provision_release --apply`. It refuses to adopt unrelated or nonempty schemas. Retain its actual receipt and verify effective grants as M2M.
2. Restore the **existing** job's local ownership state, avoiding a second writer. Create ignored `.deployment.local.json` with `job_id: 1055508848756404`, `profile: M2M`, and `workspace_root: /Workspace/Users/e92b585c-22cc-4813-b00e-b894ea680a37/retailflow`.
3. Update that job with `python -m scripts.deploy --profile M2M --catalog tmc_solutions_jvs --workspace-root /Workspace/Users/e92b585c-22cc-4813-b00e-b894ea680a37/retailflow`. This does not run it. Keep the existing single-writer concurrency and no schedule. Do not also deploy a bundle-managed writer.
4. Run `python -m scripts.run_checks --kind delta --catalog tmc_solutions_jvs --test-suffix 20261030a`. Wait for task SUCCESS, retrieve the **task** output, inspect every assertion, and save parent/task IDs, namespace, hashes and metrics. If it starts and fails, preserve the namespace and use a genuinely new approved suffix for a fresh full acceptance attempt; never reset it.
5. Run the existing six-task job sequentially for `batch1/demo01`, `batch2/demo02`, `arrival/demo03`, `arrival/demo04` with `replay_batches=batch2` on the last only. Wait for SUCCESS each time. Verify persisted snapshots and retain 55.00, 91.00, 91.00, 98.00 receipts. See [runbook](../../docs/runbook.md).
6. Run `python -m scripts.verify_dashboard --publication demo04`. It executes all four SQL files in the actual Gold namespace, with one registered publication, and validates date/product/region, quality batch/entity, resolved history and an unregistered ID. Retain actual SQL results before dashboard creation.
7. Create and test the real dashboard, pin `demo04` across datasets, separately exercise rendered sales and quality filters, export its actual definition, and capture sanitized evidence. Record and inspect the real two-minute walkthrough before linking it. Preserve existing dashboard credential/audience boundaries.
8. Review source and captures for secrets/unrelated private content, update this index only from observed results, and obtain any remaining exact production publication decision. Do not label this release complete while any live gate remains unverified.

## Tooling observations

Databricks CLI 1.16.1, local Python 3.12, existing serverless environment 5, existing SQL warehouse `ec9f4c81bc387245`. The SQL warehouse was STOPPED at inspection; it was not started for queries against absent Gold tables. No new infrastructure or spending commitment was created.

Initial strict bundle validation failed because `.venv/**`, `build/**` and `*.egg-info/**` exclusion patterns matched no tracked files in the fresh clone. They were removed from `sync.exclude`; `.gitignore` already excludes them. The subsequent strict command exited zero with no warnings. Full resolved CLI metadata remains in an ignored local file, because it includes unrelated account metadata.

An initial sandboxed pytest run encountered Windows temporary-directory access denials. The same suite passed outside that sandbox. These are environment failures, not red behavioral regression evidence.

</details>
