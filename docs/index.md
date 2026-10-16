# Documentation index

The authoritative status is [verification](verification.md); expected sales are in [expected.json](../fixtures/expected.json). Last documentation review: 2026-10-15.

| Reader | Suggested path |
|---|---|
| Hiring manager, 2 minutes | [README](../README.md) → [case study](portfolio-case-study.md) → [evidence](verification.md) |
| Data engineer, 10 minutes | [architecture](architecture.md) → [data model](data-model.md) → [quality](data-quality.md) → [tests](testing.md) |
| Reproducer / operator | [quickstart](quickstart.md) → [contracts](contracts.md) → [runbook](runbook.md) → [dashboard](../dashboard/README.md) |
| Maintainer | [CONTRIBUTING](../CONTRIBUTING.md) → [decisions](architecture-decisions.md) → [review](review.md) → [release checklist](release-checklist.md) |

## Complete guide

| Document | Purpose |
|---|---|
| [Portfolio case study](portfolio-case-study.md) | Business problem, skill evidence and honest portfolio copy |
| [Architecture](architecture.md) | Data movement, publication sequence and recovery boundaries |
| [Diagram sources](diagrams/README.md) | Editable architecture, ER and publication diagrams |
| [Data model](data-model.md) | Source fields, table grains, types and metrics |
| [Contracts](contracts.md) | Compact normative input and processing contract |
| [Data quality](data-quality.md) | Rules, revision precedence, quarantine and replay |
| [Architecture decisions](architecture-decisions.md) | Rationale and tradeoffs |
| [Quickstart](quickstart.md) | Local reproduction without a workspace |
| [Runbook](runbook.md) | Permissions, deployment, parameters, inspection and rollback |
| [Testing](testing.md) | Test layers, coverage and known gaps |
| [Verification](verification.md) | Actual pass / blocked / pending results |
| [Evidence index](../evidence/README.md) | Provenance of captured artifacts |
| [Dashboard specification](../dashboard/README.md) | Datasets, metrics, filters and layout |
| [Walkthrough](walkthrough.md) | Recording script and screenshot plan |
| [Limitations and roadmap](limitations-and-roadmap.md) | Scope boundaries and next work |
| [Release checklist](release-checklist.md) | Criteria for a publishable portfolio release |
| [Tools and skills](tools-and-skills.md) | Purpose, timing and actual usage |
| [References](references.md) | Official platform sources previously consulted |
| [Security and access](../SECURITY.md) | Synthetic data, authentication and publication hygiene |
| [Contributing](../CONTRIBUTING.md) | Change workflow and evidence standards |
| [Changelog](../CHANGELOG.md) | Implementation and documentation milestones |

## Terminology

**Batch:** immutable source content identified by batch_id. **Occurrence:** one physical CSV record, distinct from a business record. **Business key:** entity identity, such as (order_id,line_id). **Revision:** source precedence number, not event time. **Evaluation:** processing scope with frozen per-entity decisions; reuse its ID to resume, choose a new ID to replay. **Publication:** Gold snapshots identified by the evaluation ID, made current only after a passing gate. **Quarantine:** retained rejection evidence, not a discarded file.
