"""Local contract simulation against hand-calculated totals; does not certify Delta."""

import json
import unittest
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from retailflow.contracts import validate, resolve
from retailflow.manifest import load_batch

ROOT = Path(__file__).resolve().parents[1] / "fixtures"


class OracleTests(unittest.TestCase):
    def test_two_batches_and_explicit_dimension_replay(self):
        targets = {entity: {} for entity in ("customers", "products", "orders")}
        expected = json.loads((ROOT / "expected.json").read_text())

        def apply(batch, entity):
            groups = defaultdict(list)
            for raw in load_batch(ROOT / batch)["records"]:
                if raw["entity"] != entity:
                    continue
                normalized, reasons = validate(entity, json.loads(raw["row_json"]))
                reasons += raw["parse_reasons"]
                if entity == "orders":
                    for field, dim in (("customer_id", "customers"), ("product_id", "products")):
                        known = {r["payload"][field] for r in targets[dim].values()}
                        if normalized[field] not in known:
                            reasons.append("UNKNOWN_" + field.upper())
                candidate = {
                    "occurrence_id": raw["occurrence_id"],
                    "source_revision": normalized["source_revision"],
                    "payload_hash": normalized["payload_hash"],
                    "payload": normalized,
                    "reasons": reasons,
                }
                groups[normalized["business_key"]].append(candidate)
            for key, rows in groups.items():
                for outcome in resolve(rows, targets[entity].get(key)):
                    if outcome["disposition"] == "accepted_winner":
                        targets[entity][key] = outcome

        def check(stage):
            rows = [r["payload"] for r in targets["orders"].values()]
            actual = {
                "net_sales": format(sum((Decimal(r["net_sales"]) for r in rows), Decimal(0)), ".2f"),
                "units": sum(r["quantity"] for r in rows),
                "orders": len({r["order_id"] for r in rows}),
                "lines": len(rows),
            }
            self.assertEqual(actual, expected[stage])

        for batch in ("batch1", "batch2"):
            for entity in targets:
                apply(batch, entity)
            check(batch)
        for entity in targets:
            apply("arrival", entity)
        check("batch2")
        for entity in targets:
            apply("batch2", entity)
        check("replay")
        actual = sorted(
            [
                [
                    r["payload"]["order_id"],
                    r["payload"]["line_id"],
                    r["source_revision"],
                    r["payload"]["net_sales"],
                ]
                for r in targets["orders"].values()
            ]
        )
        self.assertEqual(actual, expected["final_lines"])
