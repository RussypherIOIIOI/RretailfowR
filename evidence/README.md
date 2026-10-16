# Evidence index

Evidence is dated 2026-10-15 unless its contents say otherwise. These files record different stages of development; an earlier run is not the final verification result. [Verification summary](../docs/verification.md).

| File | What it records | What it does not establish |
|---|---|---|
| [documentation-verification.json](documentation-verification.json) | Documentation link/fence checks, diagram source parity and fresh-reader review | Mermaid visual rendering or runtime tests |
| [local-verification.txt](local-verification.txt) | Local Python version, 24 passing tests, clean Ruff | Spark/Delta behavior |
| [tdd-red.json](tdd-red.json) | Initial failing live Spark check | A current failure after fixes |
| [spark-submit.json](spark-submit.json) | Earlier run submission | Completion or success by itself |
| [spark-acceptance.json](spark-acceptance.json) | Earlier successful four-check Spark run | Final nine-check coverage |
| [spark-final-submit.json](spark-final-submit.json) | Submission for final Spark run | Success by itself |
| [spark-final-result.json](spark-final-result.json) | Final task SUCCESS and nine checks; Python 3.12.3, Spark 4.2.0 | Delta writes, recovery or dashboard correctness |
| [preflight-submit.json](preflight-submit.json) | Workspace probe submission | Permission success |
| [workspace-preflight.json](workspace-preflight.json) | CREATE SCHEMA denial and run/task IDs | Permission repair or table creation |
| [deployment.json](deployment.json) | Deployed job ID, six-task order, concurrency and wheel path | Successful pipeline execution |

The earlier preflight trace reported a Python 3.11 environment. Final acceptance used serverless environment 5 and reported Python 3.12.3. These are different runs, not conflicting descriptions of one run.

The fixture [expected.json](../fixtures/expected.json) is a manually calculated **oracle**, not execution evidence. Screenshots, dashboard export, recording, Delta output and GitHub CI results are not present yet.

## Reproducing and updating evidence

Use [quickstart](../docs/quickstart.md) for local checks and [runbook](../docs/runbook.md) for remote submission. Record the command, date, source commit, configuration and actual outcome for new checks. For notebooks, preserve both parent run ID and task run ID; fetch output from the task. A submitted run is not a passing run.

Keep failed and blocked results when they explain an engineering decision. Never replace an actual result with expected output. Remove secrets, not failure context. Use [release checklist](../docs/release-checklist.md) to track missing captures.
