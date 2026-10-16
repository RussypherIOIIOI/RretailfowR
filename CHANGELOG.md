# Changelog

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
