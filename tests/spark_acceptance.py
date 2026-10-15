"""Read-only Spark checks. This is not a Delta integration test."""

import json
from retailflow.contracts import canonical
from retailflow.spark_transform import prepare, choose, foreign_keys


def run(spark):
    row = dict(
        order_id="A1",
        line_id="1",
        customer_id="C1",
        product_id="P1",
        order_date="2026-01-01",
        sale_region="WEST",
        quantity="2",
        unit_price="10.00",
        discount_amount="1.00",
        source_revision="1",
        source_updated_at="2026-01-01T00:00:00Z",
    )
    raw = spark.createDataFrame(
        [("a", canonical(row), [])], "occurrence_id string,row_json string,parse_reasons array<string>"
    )
    clean = prepare(spark, raw, "orders")
    assert "payload_json" in clean.columns, "Missing normalized, validated candidate payload"
    first = clean.first()
    assert first["reasons"] == []
    assert json.loads(first["payload_json"])["net_sales"] == "19.00"
    schema = "occurrence_id string,business_key string,source_revision long,payload_hash string,payload_json string,reasons array<string>"
    candidates = spark.createDataFrame(
        [
            ("a", "K", 1, "x", "{}", []),
            ("b", "K", 2, "y", "{}", []),
            ("c", "K", 2, "z", "{}", []),
            ("d", "K", 3, "q", "{}", ["INVALID_QUANTITY"]),
            ("e", "K", 1, "x", "{}", []),
        ],
        schema,
    )
    empty = spark.createDataFrame([], schema)
    outcomes = choose(spark, candidates, empty)
    actual = {r.occurrence_id: r.disposition for r in outcomes.collect()}
    assert actual == {
        "a": "accepted_winner",
        "e": "exact_duplicate",
        "b": "conflict",
        "c": "conflict",
        "d": "invalid",
    }, actual
    target = spark.createDataFrame([("t", "K", 3, "x", "{}", [])], schema)
    assert {r.disposition for r in choose(spark, candidates, target).collect()} == {
        "stale_superseded",
        "conflict",
        "invalid",
    }
    customer = spark.createDataFrame([('{"customer_id":"C1"}',)], "payload_json string")
    product = spark.createDataFrame([('{"product_id":"P1"}',)], "payload_json string")
    assert foreign_keys(clean, customer, product).first().reasons == []
    assert foreign_keys(clean, customer, product.limit(0)).first().reasons == ["UNKNOWN_PRODUCT"]
    from retailflow.contracts import parse_csv

    weird = "customer_id,customer_name,home_region,source_revision,source_updated_at\nC1,Ada\u2028Lovelace,WEST,1,2026-01-01T00:00:00Z\n".encode()
    assert len(parse_csv("customers", weird, "b", "x.csv")) == 1
    row["source_updated_at"] = "2026-01-01T00:00:00+00:99"
    invalid = spark.createDataFrame(
        [("bad", canonical(row), [])], "occurrence_id string,row_json string,parse_reasons array<string>"
    )
    assert "INVALID_SOURCE_UPDATED_AT" in prepare(spark, invalid, "orders").first().reasons
    from pyspark.sql import functions as F
    from decimal import Decimal
    from retailflow.pipeline import PAYLOAD_SCHEMAS

    typed = (
        clean.select(F.from_json("payload_json", PAYLOAD_SCHEMAS["orders"]).alias("p")).select("p.*").first()
    )
    assert typed.net_sales == Decimal("19.00") and typed.quantity == 2 and typed.source_updated_at is not None
    import sys

    return {"python": sys.version, "checks": 9, "status": "passed", "spark": spark.version}
