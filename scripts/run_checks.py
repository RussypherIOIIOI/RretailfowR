"""Submit read-only Spark or isolated Delta acceptance checks using the deployed wheel."""

import argparse
import json
from pathlib import Path
import subprocess
from retailflow.config import Config

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["spark", "delta"], default="spark")
    parser.add_argument("--catalog")
    parser.add_argument("--test-suffix")
    parser.add_argument("--attempt", default="", help="Fresh table/file namespace inside approved test schemas")
    args = parser.parse_args()
    if args.kind == "delta":
        if not args.catalog or not args.test_suffix:
            raise ValueError(
                "Delta checks require an explicitly chosen catalog and new lowercase test suffix"
            )
        Config(args.catalog, "retailflow_test" + args.test_suffix)
    state = json.loads((ROOT / ".deployment.local.json").read_text())

    def cli(*parts):
        response = subprocess.run(
            ["databricks", *parts, "--profile", state["profile"], "-o", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(response.stdout) if response.stdout.strip() else {}

    root = state["workspace_root"]
    kind = args.kind
    code = ROOT / "tests" / (kind + "_acceptance.py")
    cli("workspace", "import", root + "/" + code.name, "--file", str(code), "--format", "AUTO", "--overwrite")
    notebook = ROOT / "notebooks" / ("spark_checks.py" if kind == "spark" else "integration.py")
    cli(
        "workspace",
        "import",
        root + "/" + kind + "_checks",
        "--file",
        str(notebook),
        "--format",
        "SOURCE",
        "--language",
        "PYTHON",
        "--overwrite",
    )
    parameters = {"check_path": root + "/" + code.name}
    if kind == "delta":
        cli(
            "workspace",
            "import",
            root + "/expected.json",
            "--file",
            str(ROOT / "fixtures/expected.json"),
            "--format",
            "AUTO",
            "--overwrite",
        )
        parameters.update(
            catalog=args.catalog, test_suffix=args.test_suffix, expected_path=root + "/expected.json",
            attempt=args.attempt,
        )
    settings = cli("jobs", "get", str(state["job_id"]))["settings"]
    payload = {
        "run_name": "RetailFlow " + kind + " acceptance",
        "environments": settings["environments"],
        "tasks": [
            {
                "task_key": "checks",
                "environment_key": "default",
                "max_retries": 0,
                "timeout_seconds": 3600 if kind == "delta" else 900,
                "notebook_task": {
                    "notebook_path": root + "/" + kind + "_checks",
                    "base_parameters": parameters,
                },
            }
        ],
    }
    request = ROOT / ".checks-request.local.json"
    request.write_text(json.dumps(payload), encoding="utf8")
    print(json.dumps(cli("jobs", "submit", "--json", "@" + str(request), "--no-wait")))


if __name__ == "__main__":
    main()
