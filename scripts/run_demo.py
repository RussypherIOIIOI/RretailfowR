"""Run the existing single-writer job sequentially and retain real task receipts."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
from scripts.databricks_cli import cli, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="M2M")
    parser.add_argument("--job-id", type=int, default=1055508848756404)
    args = parser.parse_args()
    settings = cli(args.profile, "jobs", "get", args.job_id)["settings"]
    assert settings["tags"]["project"] == "retailflow"
    assert settings["max_concurrent_runs"] == 1
    assert len(settings["tasks"]) == 6
    save("evidence/release-20261030/deployment-current.json", settings)
    steps = [
        ("baseline", "batch1", "demo01", ""),
        ("correction", "batch2", "demo02", ""),
        ("arrival", "arrival", "demo03", ""),
        ("replay", "arrival", "demo04", "batch2"),
        ("rerun", "arrival", "demo04", "batch2"),
    ]
    for name, batch, evaluation, replay in steps:
        receipt = Path("evidence/release-20261030/demo-" + name + ".json")
        if receipt.exists():
            run_id = json.loads(receipt.read_text())["run_id"]
        else:
            response = cli(args.profile, "jobs", "run-now", "--no-wait", payload={
                "job_id": args.job_id, "job_parameters": {
                    "catalog": "tmc_solutions_jvs", "schema_prefix": "retailflow",
                    "batch_id": batch, "evaluation_id": evaluation, "replay_batches": replay,
                },
            })
            run_id = response["run_id"]
            save(receipt, response)  # Preserve the ID before polling; never blindly resubmit.
        print(f"{name}: run {run_id}", flush=True)
        deadline = time.monotonic() + 9000
        last = None
        while True:
            run = cli(args.profile, "jobs", "get-run", run_id)
            save(receipt, run)
            state = run["state"]
            progress = [(task["task_key"], task["state"].get("result_state") or
                         task["state"]["life_cycle_state"]) for task in run.get("tasks", [])]
            if progress != last:
                print(name + ": " + json.dumps(progress), flush=True)
                last = progress
            if state["life_cycle_state"] in ("TERMINATED", "SKIPPED", "INTERNAL_ERROR"):
                break
            if time.monotonic() > deadline:
                raise TimeoutError(f"{name} still pending; inspect existing run {run_id}")
            time.sleep(5)
        if state.get("result_state") != "SUCCESS":
            raise RuntimeError(f"{name} failed: {state}")
        assert all(task["state"].get("result_state") == "SUCCESS" for task in run["tasks"])
        with ThreadPoolExecutor(max_workers=6) as pool:
            outputs = list(pool.map(lambda task: {
                "task_key": task["task_key"], "task_run_id": task["run_id"],
                "output": cli(args.profile, "jobs", "get-run-output", task["run_id"]),
            }, run["tasks"]))
        save(receipt.with_name("demo-" + name + "-outputs.json"), outputs)
        print(name + ": all six tasks SUCCESS", flush=True)


if __name__ == "__main__":
    main()
