# Portfolio release checklist

Updated: 2026-11-06, pre-merge verification snapshot. [Current launch evidence](../evidence/release-20261106/README.md). Publication approval, live identity/ACL, rendered checks and media are verified. Final PR/main publication is tracked by [PR #1](https://github.com/RussypherIOIIOI/RretailfowR/pull/1) and the [GitHub release receipt](https://github.com/RussypherIOIIOI/RretailfowR/releases). Earlier publication receipt: [November 4](../evidence/release-20261104/dashboard-publication-user-receipt.json).

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
- [x] Test rendered date/product/region filters and separate quality filters; all 12 SQL assertions already pass.
- [x] Create the dashboard and export its real definition.
- [x] Obtain the exact private publication approval and retain the user's successful CLI receipt with embedded credentials on the approved warehouse.
- [x] Independently verify published metadata, publisher identity and unchanged creator/admin ACL.
- [x] Capture real metrics, rejects, job and full acceptance; public repository assets are retained.
- [x] Record and link the 129.52-second silent annotated walkthrough of actual retained snapshots.

## Documentation and repository

- [x] README, architecture/ER/sequence diagrams, data dictionary and quality guide authored.
- [x] Quickstart, runbook, testing guide and limitations documented.
- [x] Portfolio case study and accurate resume/project-card wording supplied.
- [x] Publish source to [RussypherIOIIOI/RretailfowR](https://github.com/RussypherIOIIOI/RretailfowR).
- [x] Run hosted CI: [successful source run](https://github.com/RussypherIOIIOI/RretailfowR/actions/runs/41150023703).
- [x] Preserve the owner's selected [GPL-3.0 license](../LICENSE).
- [x] Complete media review: all 30 source captures, representative annotated output, hashes and full decode.
- [x] Reconcile documentation with retained October 30-31 evidence and explicitly separate historical blockers.
- [x] Finalize current documentation and repository media links; verify public retrieval after publication.
- [ ] Required review and CI pass for the final PR commit.
- [ ] Merge PR #1 and verify CI and links on the resulting main commit.

Do not check an execution item merely because its script exists. [Evidence index](../evidence/README.md).
