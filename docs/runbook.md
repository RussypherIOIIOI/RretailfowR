# Setup, execution and recovery

## Current destination and release attempt — 2026-10-30

The former `workspace` catalog no longer exists. The exact approved schema/volume grants were applied in `tmc_solutions_jvs`, and existing job `1055508848756404` was updated to that catalog while retaining M2M principal `jarvis-cli-m2m` and concurrency one. All five demo runs succeeded, including the identical rerun. Use the current catalog in the operational examples below. Review existing state before any submission. Strict bundle validation passes without warnings; bundle deployment remains unexecuted.

Use the [current status, actual run IDs and remaining approval](../evidence/release-20261030/README.md). SQL dataset checks passed and the real dashboard export exists. Full corrected acceptance passed; do not duplicate its successful run. The next approval is private publisher-mode dashboard publication, not broader catalog grants. Do not switch the job to the admin identity. The sections below describe current operation; original failures remain in the historical evidence.

## Actual deployment

- Local repository: C:/workspace/retailflow
- Workspace: https://dbc-9d765ae8-3bb9.cloud.databricks.com
- Job ID: 1055508848756404
- CLI profile used: M2M; service principal display name jarvis-cli-m2m.
- Serverless environment version 5; observed Python 3.12.3 and Spark 4.2.0.
- SQL warehouse: ec9f4c81bc387245.
- Job has six ordered tasks, maximum one concurrent run, one retry per task, bounded timeouts, no schedule.

Five complete six-task demonstration runs succeeded, and the real dashboard exists. The original October 15 preflight failed on the former workspace catalog; that failure is retained in evidence/workspace-preflight.json as history, not a current provisioning blocker.

## Required permissions

Existing release provisioning is complete: eight named demo/test schemas and two fixture volumes have the approved scoped permissions. Do not rerun grants or expand access for this release. For a separate installation, an administrator must provision its namespaces and required privileges deliberately. No new catalog is required.

The principal needs USE CATALOG; USE SCHEMA and CREATE TABLE in each project schema; CREATE VOLUME on Bronze if the volume is not preprovisioned; READ VOLUME and WRITE VOLUME on fixtures; SELECT and MODIFY on tables it operates. Objects created by the principal are owned by it. Delta rollback additionally needs MODIFY and retained data files. Dashboard viewers require access appropriate to the chosen dashboard credential mode.

The deployed demonstration namespace is:
- tmc_solutions_jvs.retailflow_bronze
- tmc_solutions_jvs.retailflow_silver
- tmc_solutions_jvs.retailflow_gold
- tmc_solutions_jvs.retailflow_ops
- /Volumes/tmc_solutions_jvs/retailflow_bronze/fixtures

The recorded permission repair used the approved scoped plan. Runtime operations remain under jarvis-cli-m2m; dashboard access must not be repaired by silently expanding grants or changing identity.

## Deploy from a normal development shell

Install the dependencies in README and use existing Databricks authentication. If a nonstandard host does not set a home directory, use DATABRICKS_CONFIG_FILE for the existing config. Never paste credentials into project files.

The supported fallback used here:

```text
python -m scripts.deploy --profile M2M --catalog tmc_solutions_jvs --workspace-root /Workspace/Users/e92b585c-22cc-4813-b00e-b894ea680a37/retailflow
```

The deployment state is local and ignored by Git. Subsequent calls update the same owned job. Wheels are stored under a content-hash path so revised code cannot reuse a stale library cache key.

Do not deploy a second bundle-managed writer for the same namespace. If choosing the supplied bundle instead, first migrate job ownership deliberately; validate with:
```text
databricks bundle validate --strict --profile YOUR_PROFILE --var catalog=YOUR_CATALOG,warehouse_id=YOUR_WAREHOUSE
```

The initial October 15 validation was blocked by shell configuration. The later strict validation passed on CLI 1.16.1 without warnings; see evidence/release-20261030/bundle-validation-current.json. Bundle deployment itself has not been executed.

## Inspect or reproduce the demonstration

The existing namespace already contains demo01 through demo04. For portfolio recording, inspect these retained snapshots and completed runs; do not rerun batch1 expecting a reset.

| Stage | Registered publication | Completed run ID | Verified USD |
|---|---|---|---:|
| Baseline | demo01 | 165301235945373 | 55.00 |
| Correction | demo02 | 157203734280731 | 91.00 |
| Customer arrival | demo03 | 260330560109801 | 91.00 |
| Explicit replay | demo04 | 451352689364258 | 98.00 |
| Identical replay rerun | demo04 | 772106039108256 | 98.00 |

Read an existing run without starting work:

```text
databricks jobs get-run 165301235945373 --profile M2M -o json
```

The source receipts are in [demo-persisted.json](../evidence/release-20261030/demo-persisted.json). Historical dashboard selections must show their own snapshot time; the current publication pointer remains demo04.

Reproduction in a separate namespace is not needed for this release. If separately authorized, provision an unused namespace and assign exactly one owned writer configured for it. Confirm the actual job's catalog and schema_prefix before submitting batch1, batch2, arrival, then arrival with replay_batches=batch2, using new evaluation IDs and waiting for SUCCESS between steps. Do not submit that sequence to the existing demonstration job expecting it to reset data.

Preflight generates the fixture set inside the managed volume only when batch1/manifest.json is absent; see the partial-fixture-tree warning in the configuration reference below. It does not download outside data. Use a new evaluation ID for deliberate re-evaluation; use the same ID and identical scope to resume failed work. Do not change a batch's bytes or manifest after first ingestion.

## Run acceptance tests

Local:
```text
python -m pytest -q
python -m ruff check retailflow tests scripts
```

Real Spark, no persisted tables:
```text
python -m scripts.run_checks --kind spark
```

Full isolated acceptance already passed; do not repeat it for documentation or recording. If a relevant behavior change requires a new run, first arrange an explicitly authorized unused test namespace, then submit, for example:
```text
python -m scripts.run_checks --kind delta --catalog tmc_solutions_jvs --test-suffix acceptance01
```

The latter creates retailflow_testacceptance01_* schemas. The execution principal needs CREATE SCHEMA on the selected catalog, or the administrator must preprovision the four matching test schemas and their Bronze fixture volume with the same scoped privileges. Grants limited to the four demonstration schemas do not authorize this separate namespace. It deliberately injects failures and mutates test-only data. Do not reuse a previous test suffix; the test preserves its evidence rather than resetting it.

Inspect the returned parent run ID with jobs get-run. Fetch notebook output using the checks task run ID, not its parent. A submitted or deployed run is not a passed test. Copy the real JSON output to evidence only after reading SUCCESS and the assertions.

## Recover without duplicating sales

| Failure boundary | Recovery |
|---|---|
| Bronze rows written, ledger incomplete | Rerun same evaluation; occurrence MERGE prevents extra rows |
| Entity evaluation frozen, Silver not merged | Retry uses frozen outcomes and revision-guarded MERGE |
| A dimension merged, later entity failed | Retry finishes remaining entities |
| Silver finished, Gold not complete | Retry rebuilds unpublished snapshots |
| Some Gold tables written | Retry replaces that unpublished publication partition |
| Stage complete, quality failed | Previous pointer stays active; inspect the gate report |
| Publish succeeded, subsequent logging failed | Retry sees the same publication and returns |

For a permanently failed evaluation, choose explicit rollback in a trusted notebook:
```python
from retailflow.config import Config
from retailflow.pipeline import Lakehouse
lake = Lakehouse(spark, Config("tmc_solutions_jvs"))
lake.abandon("FAILED_EVALUATION_ID", confirm=True)
```

This restores all Silver tables to the versions captured before that run; it keeps Bronze, stage and evaluation evidence. A partial rollback is marked abandoning and blocks new evaluations. Repeat the same abandon call to finish. Do not vacuum versions needed by unresolved evaluations. A failure to restore is a hard error; never enable ignoreMissingFiles to hide it. Published evaluations cannot be rolled back with this method.

## Inspect data quality

Inspect ops.evaluations by evaluation_id/entity. Every source occurrence has one disposition; the header contains its expected count. Rejection reason arrays can contain several reasons, so sums by reason can exceed unique rejected-record counts.

The Gold rejected_records view includes each ever-rejected occurrence once with its latest disposition and resolved flag. Ops retains earlier reason lists and evaluation timestamps. An explicit dimension replay can resolve a rejection while preserving its history.

## Finish dashboard and portfolio evidence

The dashboard and real export already exist, and all four SQL datasets passed against demo04. Follow [the remaining release procedure](release-resume.md) to recheck access, obtain the exact private publication approval if still absent, verify rendered widgets and filters, and capture authentic media. Keep the live definition and committed export synchronized.

Source was published on 2026-10-16 to [RussypherIOIIOI/RretailfowR](https://github.com/RussypherIOIIOI/RretailfowR), preserving its initial commit and owner-selected GPL-3.0 license. The local main branch tracks origin/main. Credentials and local deployment state remain excluded.

No automated reset command is supplied. Any cleanup must explicitly name only project-owned objects and requires deliberate opt-in.

## Portable configuration reference

Replace the example workspace/profile/catalog values above with your own authorized destination. Install the Databricks CLI separately and make its executable available on PATH; [official references](references.md) record the documentation used. Local Python setup is in [quickstart](quickstart.md).

| Job parameter | Default | Meaning / rule |
|---|---|---|
| catalog | Deployment choice | Existing catalog; the script does not create one |
| schema_prefix | retailflow | retailflow or retailflow_<lowercase alphanumeric> |
| batch_id | batch1 | Directory/manifest identity beneath the fixture volume |
| evaluation_id | Job run ID | Override with the original ID to resume failed work |
| replay_batches | Empty string | Comma-separated prior completed batch IDs, without spaces |
| max_reject_fraction | 1.0 | 0..1; invalid/conflict fraction across evaluation row outcomes |

Batch/evaluation identifiers accept 1–100 ASCII letters, digits, underscores or hyphens. The notebook splits replay_batches on commas without trimming whitespace.

Preflight checks only whether batch1/manifest.json exists before generating the fixture set. It does **not** repair a partially missing fixture tree. If files are missing, inspect and restore the exact original bytes before retry; never replace already ingested content under the same batch ID.

### Deployment-state ownership

scripts.deploy normally writes .deployment.local.json containing the job ID, profile and workspace root. Reusing it updates that job after a project-tag check. Without it, deployment creates a new job; it does not discover/adopt an existing job by name. Keep the file private to the appropriate checkout. If it is lost, retrieve the exact owned job information before deliberately restoring the state or migrating ownership; do not repeatedly deploy into the same namespace.

The deploy script supports --state for a custom state filename, but scripts.run_checks reads **only .deployment.local.json**. Use the default for this workflow. Deployment uses environment version 5 and a wheel addressed by content hash. It does not start the permanent job.

### Inspect a submitted run

Replace numeric placeholders with the IDs returned by your own submission. In PowerShell, quote the @file argument to avoid splatting ambiguity:

```text
databricks jobs run-now --profile YOUR_PROFILE --json "@run.json" --no-wait
databricks jobs get-run RUN_ID --profile YOUR_PROFILE -o json
databricks jobs get-run-output TASK_RUN_ID --profile YOUR_PROFILE -o json
```

Read the parent/task state and notebook output. TERMINATED without result_state=SUCCESS is not a pass. The acceptance submit script returns immediately; wait for completion before starting another dependent run.

### Inspect quality and provenance

After tables exist, select the configured catalog and schema or qualify names as below. Replace demo02 with the evaluation being inspected:

```sql
SELECT entity, disposition, COUNT(*) AS occurrences
FROM tmc_solutions_jvs.retailflow_ops.evaluations
WHERE evaluation_id = 'demo02' AND kind = 'row'
GROUP BY entity, disposition;

SELECT publication_id, passed, checked_at, report_json
FROM tmc_solutions_jvs.retailflow_ops.gates
WHERE publication_id = 'demo02';

SELECT publication_id, sequence, published_at
FROM tmc_solutions_jvs.retailflow_gold.publication;

SELECT r.occurrence_id, r.filename, r.record_index, r.raw_record,
       e.evaluation_id, e.disposition, e.reasons
FROM tmc_solutions_jvs.retailflow_bronze.records r
JOIN tmc_solutions_jvs.retailflow_ops.evaluations e
  ON r.occurrence_id = e.occurrence_id
WHERE e.kind = 'row' AND e.evaluation_id = 'demo02'
  AND e.disposition IN ('invalid', 'conflict');
```

These are operational query examples, not captured results. Gold quality counts use latest occurrence state; ops queries above count the selected evaluation.

### Troubleshooting

| Symptom | Inspect | Next action |
|---|---|---|
| CREATE SCHEMA denied | Execution principal and chosen catalog | Ask administrator for scoped provisioning/grants; preflight again afterward |
| CLI profile/home error | External auth configuration and shell environment | Repair environment; do not copy credentials into repo |
| Immutable batch/hash failure | Manifest, exact CSV bytes and batch ID | Restore original bytes or assign a truly new batch identity |
| Unfinished evaluation blocks start | ops.runs and current publication | Resume original ID/scope or explicitly abandon unpublished work |
| Quality gate failure | ops.gates.report_json | Diagnose actual failing invariant; do not disable mandatory checks |
| No dashboard data | Successful publication registry and parameter value | Validate datasets with a registered ID; staged IDs are intentionally excluded |
| Rollback fails | Retained Delta versions, permissions, abandoning status | Keep new work stopped; correct cause and repeat same abandon call |

No Databricks service-level guarantee or unattended operations claim is made. [Testing](testing.md) lists unverified failure modes.
