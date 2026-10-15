# Databricks notebook source
import json
from pathlib import Path
from retailflow.config import Config
from retailflow.fixtures import generate
from retailflow.pipeline import Lakehouse

# The same notebook supplies explicit tasks in one serial Lakeflow Job.
stage = dbutils.widgets.get("stage")
evaluation = dbutils.widgets.get("evaluation_id")
batch = dbutils.widgets.get("batch_id")
replay = [value for value in dbutils.widgets.get("replay_batches").split(",") if value]
cfg = Config(
    dbutils.widgets.get("catalog"),
    dbutils.widgets.get("schema_prefix"),
    float(dbutils.widgets.get("max_reject_fraction")),
)
lake = Lakehouse(spark, cfg)
if stage == "preflight":
    lake.setup()
    if not (Path(cfg.volume) / "batch1" / "manifest.json").exists():
        generate(cfg.volume)
    lake.begin(evaluation, batch, replay)
elif stage == "bronze":
    lake.ingest(Path(cfg.volume) / batch, evaluation)
elif stage == "silver":
    lake.silver(evaluation)
elif stage == "gold":
    lake.stage(evaluation)
elif stage == "quality":
    lake.quality(evaluation)
elif stage == "publish":
    lake.publish(evaluation)
else:
    raise ValueError("Unknown pipeline stage")
dbutils.notebook.exit(json.dumps({"stage": stage, "evaluation_id": evaluation, "status": "completed"}))
