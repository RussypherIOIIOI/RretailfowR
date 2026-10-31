# Changelog

## Release verification in progress — 2026-10-30/31

- Applied and verified the exact owner-approved eight-schema/two-volume permissions; no catalog-wide grant.
- Updated the existing job to the actual catalog, retaining one writer and no schedule.
- Verified all five six-task demo jobs and real persisted 55.00 / 91.00 / 91.00 / 98.00 results, rerun conservation, final facts and retained rejection history.
- Compared all 21 frozen evaluation rows/fields across real rerun samples; identical hashes.
- Added exact frozen-outcome and interrupted three-table rollback assertions, fresh table/file isolation within approved schemas, and managed-volume-compatible fixture tampering. Failed test attempts and diagnoses are retained; the full corrected suite is running.
- Passed strict bundle validation with zero warnings, 30 local tests plus seven subtests, Ruff and hosted CI on `4ba6d95`.
- Executed all four Gold datasets and 12 SQL checks against registered publication `demo04`; created and retrieved the real dashboard export.
- Retained a real successful-job screenshot. Private publisher-mode publication remains pending explicit approval after automatic review rejected the unapproved credential-embedding operation. Rendered dashboard filters, metric/rejection captures and video remain incomplete.

This is not a finished production portfolio release. [Current evidence](evidence/release-20261030/README.md).

## Repository publication — 2026-10-16

Published the implementation and documentation to [RussypherIOIIOI/RretailfowR](https://github.com/RussypherIOIIOI/RretailfowR), preserving the remote initial commit and GPL-3.0 license. Local checks passed again: 24 tests and Ruff. [Hosted CI passed](https://github.com/RussypherIOIIOI/RretailfowR/actions/runs/38928719727), including wheel build. This publication does not establish end-to-end Databricks completion.

## Unreleased — 2026-10-15

### Implemented

- Deterministic messy fixtures, immutable manifests and raw Bronze provenance.
- Typed Silver validation, revision resolution, frozen evaluation evidence and explicit replay.
- Gold fact/dimensions/aggregates, versioned snapshots and gated publication.
- Serial six-task Lakeflow Job, CLI deployment and acceptance runners.
- Explicit abandonment/restoration of unpublished Silver work.
- Review fixes for timestamp offset/overflow handling and CSV physical-line framing.

### Verified

- 24 local tests, Ruff and wheel build passed.
- Nine read-only real Spark checks passed on Spark 4.2.0 / Python 3.12.3.
- Six-task job deployment/readback succeeded.

### Documented

- Portfolio README/case study, architecture and data-model diagrams, dictionary, quality rules, quickstart, operations, testing, security boundary, walkthrough and release criteria.
- Clear separation of local/Spark evidence from unexecuted Delta/dashboard checks.

### Pending

Unity Catalog CREATE SCHEMA access, Delta acceptance, dashboard validation/export/captures, recording. Strict bundle validation remains environment-blocked. See [verification](docs/verification.md); this entry is not a claim of a released v1.
