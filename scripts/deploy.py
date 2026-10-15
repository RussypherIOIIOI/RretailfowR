"""Single documented deployment fallback when bundle Git-environment discovery is unavailable."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--schema-prefix", default="retailflow")
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--state", default=".deployment.local.json")
    args = parser.parse_args()
    from retailflow.config import Config

    Config(args.catalog, args.schema_prefix)
    if not args.workspace_root.startswith("/Workspace/Users/") or ".." in args.workspace_root.split("/"):
        raise ValueError("Use a project folder beneath /Workspace/Users/")

    def cli(*parts):
        result = subprocess.run(
            ["databricks", *parts, "--profile", args.profile, "-o", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout.strip() else {}

    subprocess.run([sys.executable, "-m", "build", "--wheel", "--no-isolation"], cwd=ROOT, check=True)
    wheel = ROOT / "dist" / "retailflow-0.1.0-py3-none-any.whl"
    cli("workspace", "mkdirs", args.workspace_root)
    artifact_root = args.workspace_root + "/artifacts/" + hashlib.sha256(wheel.read_bytes()).hexdigest()[:16]
    cli("workspace", "mkdirs", artifact_root)
    cli(
        "workspace",
        "import",
        artifact_root + "/" + wheel.name,
        "--file",
        str(wheel),
        "--format",
        "AUTO",
        "--overwrite",
    )
    cli(
        "workspace",
        "import",
        args.workspace_root + "/task",
        "--file",
        str(ROOT / "notebooks/task.py"),
        "--format",
        "SOURCE",
        "--language",
        "PYTHON",
        "--overwrite",
    )
    settings = json.loads((ROOT / "resources/retailflow.job.yml").read_text())["resources"]["jobs"][
        "retailflow"
    ]
    settings["name"] = "RetailFlow — Sales Lakehouse"
    settings["tags"] = {"project": "retailflow", "schema_prefix": args.schema_prefix}
    for parameter in settings["parameters"]:
        if parameter["name"] == "catalog":
            parameter["default"] = args.catalog
        if parameter["name"] == "schema_prefix":
            parameter["default"] = args.schema_prefix
    for task in settings["tasks"]:
        task["notebook_task"]["notebook_path"] = args.workspace_root + "/task"
    settings["environments"][0]["spec"]["dependencies"] = [artifact_root + "/" + wheel.name]
    state_path = ROOT / args.state
    request = ROOT / ".job-request.local.json"
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if state["workspace_root"] != args.workspace_root or state["profile"] != args.profile:
            raise ValueError("Deployment state belongs to a different destination")
        existing = cli("jobs", "get", str(state["job_id"]))
        if existing["settings"].get("tags", {}).get("project") != "retailflow":
            raise ValueError("Refusing to update an unowned job")
        request.write_text(json.dumps({"job_id": state["job_id"], "new_settings": settings}), encoding="utf8")
        cli("jobs", "reset", "--json", "@" + str(request))
    else:
        request.write_text(json.dumps(settings), encoding="utf8")
        state = cli("jobs", "create", "--json", "@" + str(request))
        state.update(workspace_root=args.workspace_root, profile=args.profile)
        state_path.write_text(json.dumps(state, indent=2), encoding="utf8")
    verified = cli("jobs", "get", str(state["job_id"]))
    if len(verified["settings"]["tasks"]) != 6:
        raise ValueError("Deployed job does not have all six tasks")
    print(json.dumps({"job_id": state["job_id"], "tasks": 6, "status": "deployed_not_run"}))


if __name__ == "__main__":
    main()
