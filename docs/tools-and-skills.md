# Execution tools and skills

| Tool or skill | When to use | Purpose | Use in this build |
|---|---|---|---|
| Codex | Throughout implementation | Edit real files, run tests, maintain evidence | Used |
| GitHub plugin | Inspect repository/account access; review/publish when a target repo exists | Repository collaboration | Account/repository discovery used; no RetailFlow repository found |
| Git CLI / Git CMD installation | Local branching, diffs and commits | Reproducible source control | Git executable used directly; terminal UI automation is unnecessary |
| Context7 | Before version-sensitive APIs and recovery operations | Retrieve current official documentation | Used for bundle/serverless configuration and Delta RESTORE |
| Browser / computer-use | Inspect workspace or GitHub UI and capture real evidence when available | UI-only operations | GitHub repository page checked; browser is signed out |
| GitHub Copilot | Optional editor suggestions or independent review when its app session is available | Supplemental coding assistance | Not required; Codex performs implementation and review |
| Prompt Perfect | Before implementation, to refine requirements | Prompt preparation | Saved build prompt is the accepted execution specification |
| test-driven-development | Before contract/transform changes | Failing behavior tests followed by implementation | Applied; red local and Spark evidence retained |
| diagnosing-bugs | On reproducible failures | Find the cause before fixing | Applied to timestamp, CSV and environment failures |
| requesting-code-review | After major behavior changes | Independent review of correctness and recovery | Reviewer found timestamp, CSV and failed-evaluation defects; fixes reviewed |
| verification-before-completion | Before any pass/deployed claim | Fresh command and remote-result evidence | Applied; blocked Delta work remains clearly labeled |
| Databricks core/docs | Preflight and documentation checks | Auth, CLI and platform constraints | Used |
| Databricks synthetic-data-gen | Fixture design/generation | Deterministic, business-relevant data | Used with the user's explicit small, standard-library fixture scope |
| Databricks execution-compute | Read-only remote Spark checks | Verify real runtime behavior | Used; Spark 4.2.0, Python 3.12.3 |
| Databricks jobs/dabs | Job definition and deployment | One serial serverless workflow | Used; CLI deployment succeeded, bundle validation environment-blocked |
| Databricks dbsql/aibi-dashboards | Gold SQL and dashboard setup | Metric/filter correctness and real export | SQL/layout prepared; live dataset validation blocked |
| Databricks python-sdk | API reference and authentication patterns | Supported programmatic access | Guidance consulted; deployment uses CLI |

Do not add tools just to increase the tool count. Direct file and Git operations are more reliable here than controlling a terminal or editor through clicks. None of these tools guarantees bug-free code; evidence and review determine what can be claimed.
