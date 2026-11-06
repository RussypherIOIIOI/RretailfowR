# Release verification and future operation

The former permission, publication and rendered-dashboard blockers are resolved. The user approved private M2M publication on November 4. November 6 APIs and the published Info panel independently confirmed the publisher, credential mode, warehouse and unchanged creator/admin ACL. [Launch evidence](../evidence/release-20261106/README.md).

| Resource | Verified target |
|---|---|
| Catalog | tmc_solutions_jvs |
| Writer | Job 1055508848756404; six tasks; concurrency one; no schedule |
| Dashboard | 01f1d4bd43b6157d96bdf99719c7f0c3 |
| SQL warehouse | ec9f4c81bc387245 |
| Publisher | M2M / jarvis-cli-m2m / e92b585c-22cc-4813-b00e-b894ea680a37 |
| Audience | Existing creator service principal and inherited workspace admins only |
| Default snapshot | demo04 |

[Published dashboard](https://dbc-9d765ae8-3bb9.cloud.databricks.com/dashboardsv3/01f1d4bd43b6157d96bdf99719c7f0c3/published). This is private; public evidence is available through [the walkthrough and captures](walkthrough.md).

## Observed rendered checks

Use the published dashboard. The native calendar was operated with January 1, 2026 as both inclusive bounds. Text filters apply after their normal debounce. Wait for queries to settle before reading results.

| Selection | Observed result |
|---|---|
| demo04; clear sales filters | USD 98; 8 units; 5 orders; 6 lines |
| January 1 only | USD 63; 5 units; 4 orders |
| Product P1 only | USD 38; 4 units; 4 orders |
| WEST only | USD 28; 3 units; 3 orders |
| January 1 + P1 + WEST | USD 28; 3 units; 3 orders |
| Quality while combined sales filters remain | 7 unresolved; 1 resolved; 8 ever rejected |
| Quality batch2 | 6 unresolved; 1 resolved; 7 ever rejected |
| batch2; Ctrl-select its six rows with Resolved=false | 6 selected; counters 6 unresolved / 0 resolved / 6 ever rejected |
| Clear; quality entity customers | No data in all quality widgets; zero matching occurrences |
| Clear; select resolved A4/1 row | 1 selected; counters 0 unresolved / 1 resolved / 1 ever rejected |
| Return to Sales with quality selection retained | Existing sales selection remains USD 28 / 3 / 3 |
| Reset; refresh; reload | Default demo04 restores USD 98 / 8 / 5 |
| Historical demo01 / demo02 / demo03 | USD 55 / 91 / 91; units 4 / 7 / 7; orders 2 / 4 / 4 |

There is no separate resolution-status dropdown. Native table row selection filters other widgets using rejected_records; its source table remains visible with selections highlighted. The separate rejected_reasons aggregate retains batch/entity scope and contains unresolved reasons only. Clear the selection chip to reset. Reason counts are not selected unique-row counts.

A4/1 is traceable to batch2, orders.csv, record 2 and its raw payload. In demo02 it is invalid with UNKNOWN_CUSTOMER; in demo04 it is accepted_winner with resolved=true. BROKEN/1 retains invalid date, quantity and price reasons. Snapshot provenance displays the selected historical ID and its own creation time. [Exact observations and captures](../evidence/release-20261106/dashboard-ui.json).

## Preserve the verified installation

Use [the runbook](runbook.md) for reads, controlled deployment and recovery. Do not recreate the writer, rerun the fixture sequence expecting a reset, expand grants, switch identity, or rerun successful acceptance for documentation. A behavior change requires proportionate fresh verification; retain one deployment owner per namespace.

The public video is a silent annotated 129.52-second walkthrough of actual timestamped browser captures with original elapsed timing. It does not show a new pipeline execution. Source hashes, timestamps and captions are retained. [Walkthrough](walkthrough.md).

Final readiness, merge and main CI are evidenced by [PR #1](https://github.com/RussypherIOIIOI/RretailfowR/pull/1) and the [GitHub release receipt](https://github.com/RussypherIOIIOI/RretailfowR/releases). No enterprise availability or unattended-service claim is made.
