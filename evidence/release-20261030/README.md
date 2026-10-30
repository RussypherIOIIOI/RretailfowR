# Release evidence — 30 October 2026

This is an incomplete release attempt. No Delta result, dashboard, screenshot or video is claimed.

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
