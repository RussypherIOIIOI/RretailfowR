# Remaining portfolio release procedure

This procedure resumes candidate `db158945f5c7cde1b6c9d8d21f481049ba40bfe8` in [PR #1](https://github.com/RussypherIOIIOI/RretailfowR/pull/1). Read current PR and live resource state before acting. This is a verified synthetic-data pipeline demonstration with unfinished dashboard/media gates, not an enterprise production-readiness claim.

## Preserve completed work

The [retained evidence](../evidence/release-20261030/README.md) records five successful six-task jobs, registered sales of USD 55.00 → 91.00 → 91.00 → 98.00, exact frozen outcomes, interrupted rollback/resumption and last-good retention. Full Delta acceptance succeeded in parent run 853846258218717, task 833933180481456, using `retailflow_test20261030a_*` schemas and fresh `attemptc_` tables. Preserve both earlier failed attempts. Documentation and recording do not require rerunning acceptance.

| Resource | Existing target |
|---|---|
| Catalog | tmc_solutions_jvs |
| Writer job | 1055508848756404; concurrency one; no schedule |
| Dashboard | 01f1d4bd43b6157d96bdf99719c7f0c3 |
| SQL warehouse | ec9f4c81bc387245 |
| CLI profile / publisher | M2M / jarvis-cli-m2m |
| Last recorded audience | Creator service principal and workspace admins only |
| Dashboard baseline publication | demo04 |

[Private dashboard](https://dbc-9d765ae8-3bb9.cloud.databricks.com/sql/dashboardsv3/01f1d4bd43b6157d96bdf99719c7f0c3). It is not a public portfolio link.

## Restore live inspection and obtain the publication decision

The November 3 (America/Denver) continuation can run commands locally and read/write the repository through the GitHub integration. Direct shell network connections to GitHub and Databricks are blocked in this session, preventing fresh Databricks authentication and bundle validation. No application settings change was identified. The previous remote-device offline result is historical; the current continuation uses local files and the repository. These are access limitations, not newly observed pipeline failures. See [the current verification receipt](../evidence/release-20261103/resume-verification.json).

Use a connected, authorized execution session and existing authentication. Never paste secrets into chat. Read identity, draft, published state and ACL before any mutation:

```powershell
databricks current-user me --profile M2M -o json
databricks lakeview get 01f1d4bd43b6157d96bdf99719c7f0c3 --profile M2M -o json
databricks lakeview get-published 01f1d4bd43b6157d96bdf99719c7f0c3 --profile M2M -o json
```

An unpublished-dashboard response is different from an authentication failure. Inspect the current permissions using the resource's current dashboard permission object and compare with [the saved ACL](../evidence/release-20261030/dashboard-permissions.json); do not assume this dated ACL is still current.

The earlier [automatic approval rejection](../evidence/release-20261030/dashboard-publication-blocker.json) says creation/export authorization did not cover publication using publisher query credentials. That action did not execute. General permission to continue is not the specific approval required by the release instructions.

If the exact approval remains absent, ask the owner to approve:

> I approve publishing RetailFlow dashboard 01f1d4bd43b6157d96bdf99719c7f0c3 using jarvis-cli-m2m's publisher query credentials on warehouse ec9f4c81bc387245, retaining only the existing creator/admin audience, with no added viewers or catalog/table grants.

Only after that approval and a matching live-state check, publish if still needed:

```powershell
databricks lakeview publish 01f1d4bd43b6157d96bdf99719c7f0c3 --embed-credentials --warehouse-id ec9f4c81bc387245 --profile M2M
databricks lakeview get-published 01f1d4bd43b6157d96bdf99719c7f0c3 --profile M2M -o json
```

Verify publisher identity, credential mode, warehouse and unchanged audience. Do not work around a further rejection by changing identity, grants or sharing.

## Rendered test record

Use the published dashboard, clear all filters, and pin `demo04` in every data-bearing dataset. Baseline: USD 98.00, 8 units, 5 orders, 6 lines; 8 ever-rejected occurrences, 7 unresolved and 1 resolved. Check selected snapshot time against the selected snapshot, not the latest pointer time.

The selections below come from [verify_dashboard.py](../scripts/verify_dashboard.py); expected values and actual SQL receipts are in [dashboard-sql.json](../evidence/release-20261030/dashboard-sql.json). The receipt records totals and check names, while the script supplies the exact predicates. These are SQL-verified expectations; every UI result is still unobserved.

| UI selection (clear other filters first) | Expected sales / units / orders | Expected quality result | UI status |
|---|---|---|---|
| Reset all filters | 98.00 / 8 / 5 | 7 unresolved; 1 resolved | Pending |
| Date: January 1, 2026 only, inclusive | 63.00 / 5 / 4 | Quality unaffected | Pending |
| Product ID P1 | 38.00 / 4 / 4 | Quality unaffected | Pending |
| Sale region WEST | 28.00 / 3 / 3 | Quality unaffected | Pending |
| January 1 + P1 + WEST | 28.00 / 3 / 3 | Quality unaffected | Pending |
| Quality batch batch2, unresolved only | Sales unaffected | 6 unresolved | Pending |
| Quality entity customers | Sales unaffected | 0 occurrences | Pending |
| Resolved records only | Sales unaffected | 1 resolved occurrence | Pending |
| Reset; refresh; reopen | 98.00 / 8 / 5 | 7 unresolved; 1 resolved | Pending |

Also compare daily, product and regional chart values against the retained sales dataset; inspect a raw unresolved record with filename, row number and reasons; inspect the resolved C9 order line A4/1 and its retained earlier rejection. Record observed values, timestamp, selected publication and pass/fail for every UI check. Never turn a SQL result into a UI pass.

If the dashboard definition changes, re-export the actual definition to [retailflow.lvdash.json](../dashboard/retailflow.lvdash.json) and repeat affected checks.

## Capture and release

Follow [the walkthrough](walkthrough.md). Reuse retained job and acceptance captures. Capture baseline, charts, applied filters, unresolved provenance and resolved history from the real UI; remove unrelated personal information. A slideshow must be labeled a walkthrough of captured results. The current renderer expects at least 30 timestamped, equal-sized real screenshots with original elapsed timing; do not fabricate a capture manifest or stretch a few stills to satisfy it.

Watch the final approximately two-minute video, check readability and timing, and make sanitized media accessible without Databricks access through the repository or release assets. Test public links before adding them to the README.

Run pytest, Ruff, wheel build, documentation links and diagram-source consistency. Strict bundle validation must be reported separately from actual bundle deployment, which remains unexecuted. Inspect required reviews/checks, confirm CI on the final PR SHA, mark ready, and merge only after all gates pass. Verify main CI, public media links and live/export parity afterward. Keep the single writer and schedule settings unchanged.
