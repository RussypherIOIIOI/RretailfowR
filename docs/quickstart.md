# Reproduce the local checks

This path needs no Databricks account. It exercises pure Python contracts and the independent fixture oracle. Spark and Delta require the separate workspace path in the [runbook](runbook.md).

## Prerequisites

- Python 3.11 or later, pip and an extracted repository. Git is optional for an archive checkout.
- Open a terminal in the directory containing pyproject.toml. Use a path without square brackets or other glob characters; the bundle CLI rejected the original bracketed checkout path.
- Do not override the Databricks runtime's PySpark / Delta packages with local dependencies.

GitHub publication is pending, so no clone URL is advertised. Extract the supplied source archive, then enter its retailflow directory.

## Windows PowerShell

Using the environment's Python directly avoids activation-policy changes:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check retailflow tests scripts
.\.venv\Scripts\python.exe -m build --wheel --no-isolation
```

## macOS / Linux

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check retailflow tests scripts
.venv/bin/python -m build --wheel --no-isolation
```

The recorded baseline is 24 passing tests, clean Ruff and a built wheel. The count is a dated observation. Local success does not prove persisted merges, rollback or dashboard SQL. [Verification report](verification.md).

## Inspect the demonstration data

Read [batch1 orders](../fixtures/batch1/orders.csv), [batch2 orders](../fixtures/batch2/orders.csv), [arrival customers](../fixtures/arrival/customers.csv), and the [oracle](../fixtures/expected.json). Every batch includes all three entities and a manifest, even when one CSV has only its header.

To regenerate into a new directory, run with the environment Python:

```text
python -m retailflow.fixtures --output generated-fixtures --seed 17
```

Use a disposable output directory. Do not regenerate an ingested batch in place. Manifests bind exact bytes; line-ending changes can invalidate hashes. Committed CSVs are protected by [.gitattributes](../.gitattributes). Do not update expected.json merely to make a failing test pass: recalculate independently.

## Continue in Databricks

Arrange scoped access, authenticate with an external profile, and follow [deployment](runbook.md). The archive excludes credentials, the virtual environment, build outputs and local deployment state. A fresh checkout does not inherit ownership of an existing job; avoid deploying a second writer to the same namespace.
