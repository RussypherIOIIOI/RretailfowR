# Portfolio release checklist

Updated: 2026-10-31. [Latest evidence and pending dashboard approval](../evidence/release-20261030/README.md). Checked items are supported by existing artifacts; unchecked items require work or execution. Documentation completion is separate from pipeline release completion.

## Implementation and evidence

- [x] Readable Python/SQL and deterministic sample batches committed.
- [x] Independent fixture oracle supplied.
- [x] 30 local tests and seven subtests, lint and wheel build recorded.
- [x] Nine real Spark checks recorded.
- [x] Six-task job deployed and read back.
- [x] Review findings and fixes documented.
- [x] Resolve execution-principal catalog permissions with the exact approved schema/volume plan.
- [x] Run Delta acceptance in a fresh isolated namespace and retain successful output: run `853846258218717`, task `833933180481456`.
- [x] Add/run interrupted-rollback and exact frozen-outcome regression assertions.
- [x] Verify strict bundle validation: CLI 1.16.1, zero warnings. Bundle deployment itself remains unexecuted.
- [x] Record real job success and persisted 55.00 → 91.00 → 98.00 results.
- [x] Validate reruns, rejection history, replay and last-good publication retention.

## Dashboard and demonstration

- [x] SQL datasets, metric contract and layout authored.
- [x] Execute each SQL dataset against actual Gold with one registered publication ID (`demo04`).
- [ ] Test rendered date/product/region filters and separate quality filters; all 12 SQL assertions already pass.
- [x] Create the dashboard and export its real definition; rendered publication remains approval-blocked.
- [ ] Capture screenshots showing real metrics, rejects and job execution. Successful job and full acceptance captures exist; dashboard metrics/rejects remain blocked.
- [ ] Record the two-minute walkthrough; link the actual video.

## Documentation and repository

- [x] README, architecture/ER/sequence diagrams, data dictionary and quality guide authored.
- [x] Quickstart, runbook, testing guide and limitations documented.
- [x] Portfolio case study and accurate resume/project-card wording supplied.
- [x] Publish source to [RussypherIOIIOI/RretailfowR](https://github.com/RussypherIOIIOI/RretailfowR).
- [x] Run hosted CI: [successful source run](https://github.com/RussypherIOIIOI/RretailfowR/actions/runs/41150023703).
- [x] Preserve the owner's selected [GPL-3.0 license](../LICENSE).
- [ ] Complete final media review. Current job/acceptance captures and retained logs were inspected; dashboard media remains uncaptured.
- [ ] Replace dated status text with evidence from the completed release.

Do not check an execution item merely because its script exists. [Evidence index](../evidence/README.md).
