# Official references checked 2026-10-15

| Topic | Primary source | Implementation consequence |
|---|---|---|
| Free Edition limits | https://docs.databricks.com/aws/en/getting-started/free-edition-limitations | Serverless-only edition with quotas; actual account edition was not inferred from warehouse type |
| Bundle resources | https://docs.databricks.com/aws/en/dev-tools/bundles/resources | Parameterized job resource and bounded serverless environment |
| Bundle configuration | https://docs.databricks.com/aws/en/dev-tools/bundles/reference | Configuration validation uses installed CLI; unpassed validation is labeled blocked |
| Job parameters | https://docs.databricks.com/aws/en/dev-tools/bundles/job-parameters | Batch and evaluation IDs supplied as job parameters |
| Serverless bundle examples | https://github.com/databricks/bundle-examples | Notebook environment dependencies and relative paths |
| Delta table history and restore | https://docs.databricks.com/aws/en/tables/history | Capture pre-run versions; RESTORE requires MODIFY and retained files |
| RESTORE SQL | https://docs.databricks.com/aws/en/sql/language-manual/delta-restore | Explicit version restore on abandonment |
| Volume file limitations (rechecked 2026-10-31) | https://docs.databricks.com/aws/en/volumes/volume-files#limitations-of-working-with-files-in-volumes | Test-only tampering rewrites full bytes sequentially; direct append/random writes are unsupported |
| Databricks maintained skills | https://github.com/databricks/databricks-agent-skills | Installed skill release 0.2.10; core, jobs, dabs, compute, synthetic data, docs, SQL, SDK and AI/BI guidance |

Observed tooling: Databricks CLI 1.16.1, Git 2.54.0.windows.1, local Python 3.14.4. The tested serverless environment version 5 reported Python 3.12.3 and Spark 4.2.0. Runtime PySpark and Delta were not replaced by local packages.

The maintained skills were reconciled with the user's explicit project scope: a small standard-library fixture generator, existing authentication, and autonomous ordinary implementation choices. No claim is made that a prompt or model eliminates bugs.
