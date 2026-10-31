# Two-minute portfolio walkthrough

**Capture status: incomplete.** The five real demo jobs, persisted 55.00 → 91.00 → 91.00 → 98.00 results and full isolated Delta recovery acceptance passed. A [real successful-job screenshot](assets/lakeflow-baseline-success.jpg) is captured. Rendered dashboard access requires a separate private publisher-mode publication approval. The two-minute video has not been recorded and no video URL is claimed. [Current evidence](../evidence/release-20261030/README.md).

## Prepare the demonstration

Use a fresh demo namespace with one writer, or explicitly account for existing publications. Complete [Delta acceptance](testing.md), then run the ordered demo steps in the [runbook](runbook.md). Pre-run and record each stage; use short edited clips so job startup time does not consume the two-minute video. Keep the publication ID visible and label any time cuts. Use only observed results.

Prepare the source, fixture oracle, successful job run, dashboard, rejection detail and evidence report. Frame the browser so tokens, unrelated tabs and personal details are absent. [Dashboard specification](../dashboard/README.md).

## Script and screen plan

| Time | Show | Suggested narration |
|---|---|---|
| 0:00–0:15 | README question and architecture | “RetailFlow connects sales metrics to evidence about source-data quality. It uses synthetic orders and runs inside Databricks.” |
| 0:15–0:30 | Small CSVs and independent oracle | “The fixture has deliberate defects. Expected totals were calculated independently so the pipeline cannot grade itself.” |
| 0:30–0:45 | Completed baseline job, current publication, dashboard | “The baseline should contain three lines, two orders and 55 dollars. Here are the observed values.” |
| 0:45–1:10 | Batch2 changes, updated fact and dashboard | “This valid correction changes product, date and region. Duplicates add no sales; an invalid newer correction leaves the valid record intact. The corrected expectation is 91 dollars.” |
| 1:10–1:35 | Raw rejected row/reasons; arrival then replay | “Customer arrival alone does not replay old rejects. Explicit replay admits the seven-dollar line, giving an expected 98 dollars, while retaining its rejection history.” |
| 1:35–1:50 | Successful retry/fault-test evidence and pointer | “Retries reuse frozen decisions. A failed publication gate should leave the last successful snapshot visible; this test result shows the observed behavior.” |
| 1:50–2:00 | Source/tests and scope note | “The repository documents contracts, tests and recovery. This release is intentionally small: one writer, USD and Type 1 dimensions.” |

Use statements about observed values and passed fault tests only after corresponding checks succeed. Until then, a code-only walkthrough must explicitly say “implemented, not yet verified on persisted Delta” and should show the blocked status instead.

## Screenshot shot list

| Planned filename | Required real content | Acceptance check |
|---|---|---|
| dashboard-baseline.png | KPIs and publication ID | 55.00 / 4 units / 2 orders |
| dashboard-corrections.png | Trend/product/region widgets | 91.00; corrected line appears in correct groups |
| rejected-record-detail.png | Raw record, filename, line number, reasons | Traceable occurrence; multiple reasons readable |
| dashboard-replay.png | Sales and resolved rejection | 98.00; historical rejection still inspectable |
| lakeflow-success.png | All six successful tasks | Same completed demo run |
| acceptance-result.png | Actual Delta assertions and run ID | No expected-output substitution |

Store finished images under docs/assets/ and the real dashboard export under dashboard/retailflow.lvdash.json. The actual dashboard export, [successful-job screenshot](assets/lakeflow-baseline-success.jpg) and [full-acceptance screenshot](assets/delta-acceptance-success.jpg) now exist; metric/rejection captures and the video remain pending rendered access. Add image/video links only after actual capture; do not create placeholder success evidence.

## Hiring-viewer close

The key takeaway is explainability under imperfect input: which business line changed, why a row was rejected, and how the published result remained consistent. Use the [case study](portfolio-case-study.md) for accompanying project-card or resume copy.
