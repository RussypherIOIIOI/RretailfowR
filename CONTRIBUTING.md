# Contributing to RetailFlow

Read [contracts](docs/contracts.md), [architecture decisions](docs/architecture-decisions.md) and [runbook](docs/runbook.md) before changing behavior. Agent-specific requirements are in [AGENTS.md](AGENTS.md).

## Development workflow

1. Work from the repository root in a virtual environment; follow [quickstart](docs/quickstart.md).
2. Explain the behavioral change and add a failing test for revision, validation or publication logic.
3. Implement the smallest coherent change. Keep expected fixture values independently calculated.
4. Run pytest, Ruff and the wheel build. For Spark/Delta changes, run the relevant remote layer in an isolated namespace when authorized and available.
5. Review recovery, replay and publication consequences, then update documentation and evidence together.

Do not install local PySpark/Delta into the managed runtime or commit credentials, deployment state, generated build artifacts or a virtual environment.

## Review checklist

- Does the change preserve natural-key, revision and immutable-batch contracts?
- Can retry resume the same evaluation without reclassifying frozen decisions?
- Are multiple rejection reasons preserved and unique record counts distinguished?
- Can unpublished state leak into dashboard results?
- Does the quality gate still reconcile every date/region/product group?
- Are failure, rollback and retained-history requirements explicit?
- Are executed, unexecuted and blocked checks labeled accurately?

One writer per namespace is mandatory. Do not deploy a second job or manually edit Silver in the demonstration namespace. Fault tests must use a new explicitly selected test suffix.

## Documentation changes

Maintain relative links and keep Mermaid .mmd sources synchronized with embedded diagrams. Update [verification](docs/verification.md) only from actual results. Add new evidence files with command/run context, redact credentials, and describe what each artifact does and does not prove. Do not substitute mock screenshots for live evidence.

Repository: [RussypherIOIIOI/RretailfowR](https://github.com/RussypherIOIIOI/RretailfowR). Describe the concrete problem, resulting behavior, tests and material limits in each PR. See the owner-selected [GPL-3.0 license](LICENSE).
