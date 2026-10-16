# Diagrams

These diagrams describe implemented design, not a completed deployment. Persisted Delta behavior and the dashboard remain unverified. No diagram is a dashboard screenshot.

| Source | Rendered in | Use |
|---|---|---|
| [architecture.mmd](architecture.mmd) | [Architecture](../architecture.md) | Data dependencies and publication boundary |
| [data-model.mmd](data-model.mmd) | [Data model](../data-model.md) | Fact/dimension relationships and composite snapshot keys |
| [publication.mmd](publication.mmd) | [Architecture](../architecture.md) | Success/failure sequence and reader pinning |

GitHub renders the Mermaid blocks in the linked Markdown pages. The .mmd files contain identical editable sources for export in a Mermaid-compatible editor. Keep embedded blocks and source files synchronized. ER key annotations express logical invariants checked by code; they do not claim database-enforced primary/foreign-key constraints. Audit columns are omitted from the ER drawing for readability; see the data dictionary.
