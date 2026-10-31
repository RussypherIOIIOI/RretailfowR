# Portfolio release checklist

Updated: 2026-10-30. [Latest evidence, pending permission plan and resume commands](../evidence/release-20261030/README.md). Checked items are supported by existing artifacts; unchecked items require work or execution. Documentation completion is separate from pipeline release completion.

## Implementation and evidence

- [x] Readable Python/SQL and deterministic sample batches committed.
- [x] Independent fixture oracle supplied.
- [x] 24 local tests, lint and wheel build recorded.
- [x] Nine real Spark checks recorded.
- [x] Six-task job deployed and read back.
- [x] Review findings and fixes documented.
- [x] Resolve execution-principal catalog permissions with the exact approved schema/volume plan.
- [ ] Run Delta acceptance in a fresh isolated namespace and retain successful output.
- [ ] Add/run interrupted-rollback and exact frozen-outcome regression assertions.
- [x] Verify strict bundle validation: CLI 1.16.1, zero warnings. Bundle deployment itself remains unexecuted.
- [x] Record real job success and persisted 55.00 → 91.00 → 98.00 results.
- [ ] Validate reruns, rejection history, replay and last-good publication retention.

## Dashboard and demonstration

- [x] SQL datasets, metric contract and layout authored.
- [x] Execute each SQL dataset against actual Gold with one registered publication ID (`demo04`).
- [ ] Test date/product/region filters and separate quality filters.
- [x] Create the dashboard and export its real definition; rendered publication remains approval-blocked.
- [ ] Capture screenshots showing real metrics, rejects and job execution.
- [ ] Record the two-minute walkthrough; link the actual video.

## Documentation and repository

- [x] README, architecture/ER/sequence diagrams, data dictionary and quality guide authored.
- [x] Quickstart, runbook, testing guide and limitations documented.
- [x] Portfolio case study and accurate resume/project-card wording supplied.
- [x] Publish source to [RussypherIOIIOI/RretailfowR](https://github.com/RussypherIOIIOI/RretailfowR).
- [x] Run hosted CI: [successful run](https://github.com/RussypherIOIIOI/RretailfowR/actions/runs/38928719727).
- [x] Preserve the owner's selected [GPL-3.0 license](../LICENSE).
- [ ] Review screenshots/logs for credentials or unrelated personal/workspace information.
- [ ] Replace dated status text with evidence from the completed release.

Do not check an execution item merely because its script exists. [Evidence index](../evidence/README.md).
