# Databricks notebook source
# MAGIC %pip install /Workspace/Users/e92b585c-22cc-4813-b00e-b894ea680a37/retailflow/retailflow-0.1.0-py3-none-any.whl
# COMMAND ----------
import json
exec(open('/Workspace/Users/e92b585c-22cc-4813-b00e-b894ea680a37/retailflow/spark_acceptance.py').read())
dbutils.notebook.exit(json.dumps(run(spark)))
