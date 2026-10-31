"""Existing CLI authentication, bounded SQL execution, and JSON evidence helpers."""

import json
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def cli(profile, *parts, payload=None):
    request = None
    try:
        command = ["databricks", *map(str, parts), "--profile", profile, "-o", "json"]
        if payload is not None:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf8", dir=ROOT, suffix=".local.json", delete=False
            ) as stream:
                json.dump(payload, stream)
                request = Path(stream.name)
            command += ["--json", "@" + str(request)]
        response = subprocess.run(command, capture_output=True, text=True, check=False)
        if response.returncode:
            raise RuntimeError(response.stderr.strip() or "Databricks CLI failed")
        return json.loads(response.stdout) if response.stdout.strip() else {}
    finally:
        if request is not None:
            request.unlink(missing_ok=True)


def sql(profile, warehouse, catalog, schema, statement, parameters=()):
    result = cli(profile, "api", "post", "/api/2.0/sql/statements", payload={
        "warehouse_id": warehouse, "catalog": catalog, "schema": schema,
        "statement": statement, "parameters": list(parameters), "wait_timeout": "10s",
        "on_wait_timeout": "CONTINUE", "format": "JSON_ARRAY", "disposition": "INLINE",
        "row_limit": 10000,
    })
    deadline = time.monotonic() + 600
    while result["status"]["state"] in ("PENDING", "RUNNING"):
        if time.monotonic() > deadline:
            raise TimeoutError("SQL statement still pending: " + result["statement_id"])
        time.sleep(2)
        result = cli(profile, "api", "get", "/api/2.0/sql/statements/" + result["statement_id"])
    if result["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(json.dumps(result["status"]))
    assert not result.get("manifest", {}).get("truncated"), "SQL evidence was truncated"
    assert result.get("manifest", {}).get("total_chunk_count", 1) <= 1, "SQL evidence has extra chunks"
    return result


def rows(result):
    columns = [column["name"] for column in result["manifest"]["schema"]["columns"]]
    return [dict(zip(columns, row)) for row in result.get("result", {}).get("data_array", [])]


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf8")
