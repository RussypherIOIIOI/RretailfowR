"""Spark transforms use bounded Python contracts at the record/key boundary."""

import json
from retailflow.contracts import canonical, resolve, validate

CANDIDATE_SCHEMA = """occurrence_id string, business_key string, source_revision long,
payload_hash string, payload_json string, reasons array<string>"""
OUTCOME_SCHEMA = CANDIDATE_SCHEMA + ", disposition string"


def _validate(entity, raw_json, parse_reasons):
    row, reasons = validate(entity, json.loads(raw_json))
    return (
        canonical(row),
        row["business_key"],
        row["source_revision"],
        row["payload_hash"],
        sorted(set(reasons + list(parse_reasons or []))),
    )


def prepare(spark, bronze, entity):
    from pyspark.sql import functions as F

    validate_udf = F.udf(
        lambda raw, reasons: _validate(entity, raw, reasons),
        "payload_json string,business_key string,source_revision long,payload_hash string,reasons array<string>",
    )
    return bronze.withColumn("validated", validate_udf("row_json", "parse_reasons")).select(
        "occurrence_id", "validated.*"
    )


def foreign_keys(candidates, customers, products):
    from pyspark.sql import functions as F

    result = candidates
    for field, target, reason in [
        ("customer_id", customers, "UNKNOWN_CUSTOMER"),
        ("product_id", products, "UNKNOWN_PRODUCT"),
    ]:
        dimension = target.select(F.get_json_object("payload_json", "$." + field).alias("_fk")).distinct()
        result = (
            result.withColumn("_requested", F.get_json_object("payload_json", "$." + field))
            .join(dimension, F.col("_requested") == F.col("_fk"), "left")
            .withColumn(
                "reasons",
                F.when(F.col("_fk").isNull(), F.array_union("reasons", F.array(F.lit(reason)))).otherwise(
                    F.col("reasons")
                ),
            )
            .drop("_requested", "_fk")
        )
    return result


def _choose(rows, target):
    candidates = [r.asDict(recursive=True) for r in rows]
    previous = target.asDict(recursive=True) if target and target["source_revision"] is not None else None
    return resolve(candidates, previous)


def choose(spark, candidates, target):
    from pyspark.sql import functions as F

    columns = ["occurrence_id", "business_key", "source_revision", "payload_hash", "payload_json", "reasons"]
    groups = candidates.groupBy("business_key").agg(F.collect_list(F.struct(*columns)).alias("candidates"))
    previous = target.select("business_key", F.struct("source_revision", "payload_hash").alias("target"))
    merged = groups.join(previous, "business_key", "left")
    choose_udf = F.udf(_choose, "array<struct<" + OUTCOME_SCHEMA + ">>")
    return merged.select(F.explode(choose_udf("candidates", "target")).alias("outcome")).select("outcome.*")
