# RetailFlow launch verification — 6 November 2026

The existing synthetic-data lakehouse and private published dashboard are verified. No data, grants, job schedule, writer identity, or dashboard definition changed during this check. The public repository includes genuine dashboard captures and a **129.52-second silent annotated walkthrough of retained snapshots**, not a continuous job execution or narrated recording.

| Gate | Evidence |
|---|---|
| Published credentials, warehouse, unchanged private ACL, current draft/export parity, single writer, all retained successful runs | [Live inspection](live-release-check.json), [published metadata](published-metadata.json), [ACL](dashboard-permissions.json), [dashboard](dashboard-resource.json) |
| Actual publisher identity | [Info panel](../../docs/assets/release-20261106/publisher-identity.jpg): e92b585c-22cc-4813-b00e-b894ea680a37, viewing with publisher credentials; matches jarvis-cli-m2m |
| Four datasets and twelve fresh SQL assertions | [SQL receipts](dashboard-sql.json); distinct from rendered checks |
| Rendered controls, historical snapshots, reset/refresh/reopen, provenance | [UI results](dashboard-ui.json), [captures](../../docs/assets/release-20261106/) |
| Persisted recovery behavior | [Successful isolated Delta acceptance](../release-20261030/delta-acceptance-passed.json); source hashes still match. No unnecessary rerun or new namespace |
| Local tests, lint, wheel, strict bundle validation, documentation | [Local verification](local-verification.json); bundle deployment was not executed |
| Public walkthrough | [MP4](../../docs/assets/retailflow-walkthrough.mp4), [timestamps](recording.json), [hashes, annotations and full-decode receipt](video-manifest.json) |
| Independent review | [Release and media review](review.json) |

The dashboard is private: [published RetailFlow](https://dbc-9d765ae8-3bb9.cloud.databricks.com/dashboardsv3/01f1d4bd43b6157d96bdf99719c7f0c3/published). Portfolio viewers can use the repository's screenshots and video without Databricks access. No public workspace sharing was enabled.

Final source publication is tracked by [PR #1](https://github.com/RussypherIOIIOI/RretailfowR/pull/1), [main CI](https://github.com/RussypherIOIIOI/RretailfowR/actions/workflows/ci.yml?query=branch%3Amain), and the [GitHub releases](https://github.com/RussypherIOIIOI/RretailfowR/releases) receipt. This file is the pre-merge verification snapshot; inspect those live records for merge, final-SHA CI and public-link results.

Scope remains one manually operated writer, USD, synthetic fixtures, Type 1 dimensions and retained snapshots. This release does not claim unattended operations, production customer traffic, large-data performance, multi-writer support or an enterprise SLA.
