# Security and access boundary

RetailFlow uses synthetic data only. It is a personal demonstration, not a reviewed platform for sensitive customer data.

## Credentials and permissions

Use supported external Databricks authentication profiles. Never place tokens, client secrets, browser cookies or credential configuration in source, notebooks, manifests, screenshots or evidence. Local deployment/request files are ignored by Git; an ignore rule alone does not sanitize a previously tracked secret.

The execution principal needs the scoped privileges described in the [runbook](docs/runbook.md). The observed CREATE SCHEMA denial is an access blocker to resolve with an administrator. Do not switch identities or broaden grants to evade it. Keep consumer access scoped to appropriate published data and the dashboard's selected credential mode.

## Input and operational boundaries

Input paths and identifiers are validated; manifests bind exact file bytes. SHA256 identifies content but does not authenticate a trusted producer. Raw malformed records are deliberately retained. If adapted to real data, those raw values and rejection histories may themselves be sensitive and need explicit retention/access controls.

One writer and retained Delta history are prerequisites for recovery. Cleanup is not automatic; do not remove objects or vacuum recovery versions while an evaluation is unresolved.

## Before public publication

Inspect tracked files and captures for credentials and unrelated information. Workspace URLs, principal identifiers and job/run IDs in evidence identify the demonstration environment; they are not credentials, but review whether to retain them publicly. Redact secrets while preserving enough context to substantiate results.

If a credential is exposed, revoke/rotate it through its owner and follow the host's incident process; deleting a file alone does not revoke access. No public vulnerability-reporting address has been established for this unpublished repository. Use the maintainer's verified private channel once one is provided; never place secrets in a public issue.
