# Databricks notebook source
import json
from pathlib import Path

check_path = Path(dbutils.widgets.get("check_path"))
exec(compile(check_path.read_text(), str(check_path), "exec"))
dbutils.notebook.exit(json.dumps(run(spark)))
