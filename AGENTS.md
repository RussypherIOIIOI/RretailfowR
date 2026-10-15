# RetailFlow agent guidance

Read docs/contracts.md and docs/runbook.md before changes. Use databricks-core, databricks-jobs and databricks-dabs skills for deployment. Keep one writer job per project namespace. Add failing behavioral tests before changing revision, validation or publication logic. Run pytest, Ruff and bundle validation; distinguish local, Spark and Delta evidence. Never claim deployment from static tests. Credentials belong in supported external authentication only. No reset or deletion without explicit opt-in.
