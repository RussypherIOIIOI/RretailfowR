# Setup, execution and recovery

## Actual deployment

- Local repository: C:/workspace/retailflow
- Workspace: https://dbc-9d765ae8-3bb9.cloud.databricks.com
- Job ID: 1055508848756404
- CLI profile used: M2M; service principal display name jarvis-cli-m2m.
- Serverless environment version 5; observed Python 3.12.3 and Spark 4.2.0.
- SQL warehouse: ec9f4c81bc387245.
- Job has six ordered tasks, maximum one concurrent run, one retry per task, bounded timeouts, no schedule.

The job exists but has not completed the table pipeline. Preflight returned PERMISSION_DENIED: CREATE SCHEMA on catalog workspace. No project data schemas or dashboard were created.

## Required permissions

An administrator can either grant CREATE SCHEMA on the chosen catalog to the execution principal, or provision the four project schemas and a managed fixture volume, then grant the principal the required scoped privileges. Do not create a new catalog.

The principal needs USE CATALOG; USE SCHEMA and CREATE TABLE in each project schema; CREATE VOLUME on Bronze if the volume is not preprovisioned; READ VOLUME and WRITE VOLUME on fixtures; SELECT and MODIFY on tables it operates. Objects created by the principal are owned by it. Delta rollback additionally needs MODIFY and retained data files. Dashboard viewers require access appropriate to the chosen dashboard credential mode.

The requested namespace is:
- workspace.retailflow_bronze
- workspace.retailflow_silver
- workspace.retailflow_gold
- workspace.retailflow_ops
- /Volumes/workspace/retailflow_bronze/fixtures

This build does not grant privileges or switch to another identity to evade the denial.

## Deploy from a normal development shell

Install the dependencies in README and use existing Databricks authentication. If a nonstandard host does not set a home directory, use DATABRICKS_CONFIG_FILE for the existing config. Never paste credentials into project files.

The supported fallback used here:

```text
python -m scripts.deploy --profile M2M --catalog workspace --workspace-root /Workspace/Users/e92b585c-22cc-4813-b00e-b894ea680a37/retailflow
```

The deployment state is local and ignored by Git. Subsequent calls update the same owned job. Wheels are stored under a content-hash path so revised code cannot reuse a stale library cache key.

Do not deploy a second bundle-managed writer for the same namespace. If choosing the supplied bundle instead, first migrate job ownership deliberately; validate with:
```text
databricks bundle validate --strict --profile YOUR_PROFILE --var catalog=YOUR_CATALOG,warehouse_id=YOUR_WAREHOUSE
```

The actual environment blocked this command because the CLI could not resolve its global Git home configuration. Direct job creation and API retrieval succeeded.

## Run the demonstration after permission repair

Create a JSON request file with the job ID and parameters, then invoke:

```text
databricks jobs run-now --profile M2M --json @run.json --no-wait
```

Run these in order, waiting for SUCCESS before proceeding:

| Step | batch_id | evaluation_id | replay_batches | Expected USD |
|---|---|---|---|---:|
| Baseline | batch1 | demo01 | empty string | 55.00 |
| Correction | batch2 | demo02 | empty string | 91.00 |
| Customer arrival | arrival | demo03 | empty string | 91.00 |
| Explicit replay | arrival | demo04 | batch2 | 98.00 |

Example run.json:
```json
{"job_id":1055508848756404,"job_parameters":{"batch_id":"batch1","evaluation_id":"demo01","replay_batches":""}}
```

Preflight generates the fixture files inside the managed volume only when they are absent. It does not download outside data. Use a new evaluation ID for deliberate re-evaluation; use the same ID and identical scope to resume failed work. Do not change a batch's bytes or manifest after first ingestion.

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

Real Delta, after catalog permission repair, using a new isolated namespace:
```text
python -m scripts.run_checks --kind delta --catalog workspace --test-suffix acceptance01
```

The latter creates retailflow_testacceptance01_* schemas. It deliberately injects failures and mutates test-only data. Do not reuse a previous test suffix; the test preserves its evidence rather than resetting it.

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
lake = Lakehouse(spark, Config("workspace"))
lake.abandon("FAILED_EVALUATION_ID", confirm=True)
```

This restores all Silver tables to the versions captured before that run; it keeps Bronze, stage and evaluation evidence. A partial rollback is marked abandoning and blocks new evaluations. Repeat the same abandon call to finish. Do not vacuum versions needed by unresolved evaluations. A failure to restore is a hard error; never enable ignoreMissingFiles to hide it. Published evaluations cannot be rolled back with this method.

## Inspect data quality

Inspect ops.evaluations by evaluation_id/entity. Every source occurrence has one disposition; the header contains its expected count. Rejection reason arrays can contain several reasons, so sums by reason can exceed unique rejected-record counts.

The Gold rejected_records view includes each ever-rejected occurrence once with its latest disposition and resolved flag. Ops retains earlier reason lists and evaluation timestamps. An explicit dimension replay can resolve a rejection while preserving its history.

## Finish dashboard and portfolio evidence

Follow dashboard/README.md. Execute all four SQL datasets with a real registered publication ID before creating the dashboard. Pin that same ID across widgets. Export the actual dashboard definition and capture screenshots only after correct results appear. Record the two-minute script in docs/walkthrough.md.

GitHub publication is pending: the connector could inspect the account, but no RetailFlow repository was present; the CLI and browser were signed out and the connector exposed no repository-creation tool. Create/select the destination repository, add its remote, and push the reviewed commits. No credentials are stored in the archive.

No automated reset command is supplied. Any cleanup must explicitly name only project-owned objects and requires deliberate opt-in.
