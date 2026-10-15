# Databricks notebook source
import json
import sys
result = {'python':sys.version,'spark':spark.version}
for layer in ['bronze','silver','gold','ops']:
    spark.sql(f'CREATE SCHEMA IF NOT EXISTS workspace.retailflow_{layer}')
spark.sql('CREATE VOLUME IF NOT EXISTS workspace.retailflow_bronze.fixtures')
result['schemas_and_volume']='ready'
dbutils.notebook.exit(json.dumps(result))
