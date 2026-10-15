"""Read-only Spark checks. This is not a Delta integration test."""

import json
from retailflow.contracts import canonical
from retailflow.spark_transform import prepare, choose


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
    return {"checks": 4, "status": "passed", "spark": spark.version}
