# Databricks notebook source
import json
from pathlib import Path

check_path = Path(dbutils.widgets.get("check_path"))
exec(compile(check_path.read_text(), str(check_path), "exec"))
result = run(spark, dbutils.widgets.get("catalog"), dbutils.widgets.get("test_suffix"), dbutils.widgets.get("expected_path"), dbutils.widgets.get("attempt"))
dbutils.notebook.exit(json.dumps(result))
