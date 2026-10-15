import unittest
from retailflow.contracts import validate, parse_csv, resolve

ORDER = dict(
    order_id="O1",
    line_id="1",
    customer_id="C1",
    product_id="P1",
    order_date="2026-01-01",
    sale_region="west",
    quantity="2",
    unit_price="10.00",
    discount_amount="1.00",
    source_revision="1",
    source_updated_at="2026-01-01T00:00:00Z",
)


class ContractTests(unittest.TestCase):
    def test_valid_money_is_exact(self):
        row, reasons = validate("orders", ORDER)
        self.assertEqual(reasons, [])
        self.assertEqual(row.get("net_sales"), "19.00")
        self.assertEqual(row.get("sale_region"), "WEST")

    def test_multiple_errors_and_precision(self):
        _, reasons = validate(
            "orders",
            {
                **ORDER,
                "quantity": "0",
                "unit_price": "1.999",
                "source_revision": "1.5",
                "order_date": "2026-02-30",
            },
        )
        self.assertTrue(
            {"INVALID_QUANTITY", "INVALID_UNIT_PRICE", "INVALID_REVISION", "INVALID_ORDER_DATE"}
            <= set(reasons)
        )

    def test_timestamp_requires_timezone(self):
        _, reasons = validate("orders", {**ORDER, "source_updated_at": "2026-01-01T00:00:00"})
        self.assertIn("INVALID_SOURCE_UPDATED_AT", reasons)

    def test_gross_overflow_and_discount(self):
        for changes, expected in [
            ({"quantity": "1000000", "unit_price": "9999999999999999.99"}, "MONEY_OVERFLOW"),
            ({"discount_amount": "21.00"}, "DISCOUNT_EXCEEDS_GROSS"),
        ]:
            self.assertIn(expected, validate("orders", {**ORDER, **changes})[1])

    def test_csv_preserves_duplicate_occurrences_and_renames(self):
        raw = b"customer_id,customer_name,home_region,source_revision,source_updated_at\nC1,Ada,WEST,1,2026-01-01T00:00:00Z\nC1,Ada,WEST,1,2026-01-01T00:00:00Z\n"
        a = parse_csv("customers", raw, "batch1", "a.csv")
        b = parse_csv("customers", raw, "batch1", "renamed.csv")
        self.assertEqual(len(a), 2)
        self.assertNotEqual(a[0]["occurrence_id"], a[1]["occurrence_id"])
        self.assertEqual([r["occurrence_id"] for r in a], [r["occurrence_id"] for r in b])

    def test_malformed_line_is_preserved(self):
        raw = b'customer_id,customer_name,home_region,source_revision,source_updated_at\nC1,"unterminated,WEST,1,2026-01-01T00:00:00Z\n'
        rows = parse_csv("customers", raw, "b", "bad.csv")
        self.assertEqual(len(rows), 1)
        self.assertIn("MALFORMED_CSV", rows[0]["parse_reasons"])
        self.assertIn("unterminated", rows[0]["raw_record"])

    def test_changed_header_fails(self):
        with self.assertRaises(ValueError):
            parse_csv("orders", b"wrong\nx\n", "b", "x.csv")


def candidate(occ, rev, payload, reasons=None):
    return dict(occurrence_id=occ, source_revision=rev, payload_hash=payload, reasons=reasons or [])


class ResolutionTests(unittest.TestCase):
    def outcomes(self, rows, target=None):
        return {r["occurrence_id"]: r["disposition"] for r in resolve(rows, target)}

    def test_newest_valid_wins_invalid_newer_does_not(self):
        rows = [candidate("a", 1, "x"), candidate("b", 2, "y"), candidate("c", 3, "z", ["BAD"])]
        self.assertEqual(
            self.outcomes(rows), {"a": "stale_superseded", "b": "accepted_winner", "c": "invalid"}
        )

    def test_conflict_falls_back_and_shuffling_does_not_matter(self):
        rows = [
            candidate("a", 1, "x"),
            candidate("b", 2, "y"),
            candidate("c", 2, "z"),
            candidate("d", 1, "x"),
        ]
        expected = {"a": "accepted_winner", "d": "exact_duplicate", "b": "conflict", "c": "conflict"}
        self.assertEqual(self.outcomes(rows), expected)
        self.assertEqual(self.outcomes(list(reversed(rows))), expected)

    def test_target_is_preserved_on_conflict(self):
        self.assertEqual(
            self.outcomes([candidate("a", 2, "y")], candidate("target", 2, "x")), {"a": "conflict"}
        )

    def test_identical_higher_revision_advances_watermark(self):
        result = resolve([candidate("a", 3, "x")], candidate("target", 1, "x"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["disposition"], "accepted_winner")
        self.assertEqual(
            self.outcomes([candidate("b", 2, "y")], candidate("target", 3, "x")), {"b": "stale_superseded"}
        )

    def test_duplicate_target_does_not_inflate(self):
        self.assertEqual(
            self.outcomes([candidate("a", 1, "x")], candidate("t", 1, "x")), {"a": "exact_duplicate"}
        )


class TimestampBoundaryTests(unittest.TestCase):
    def test_invalid_offset_is_rejected(self):
        self.assertIn(
            "INVALID_SOURCE_UPDATED_AT",
            validate("orders", {**ORDER, "source_updated_at": "2026-01-01T00:00:00+00:99"})[1],
        )

    def test_utc_overflow_is_quarantined(self):
        for value in ("0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00"):
            self.assertIn(
                "INVALID_SOURCE_UPDATED_AT", validate("orders", {**ORDER, "source_updated_at": value})[1]
            )


class CsvBoundaryTests(unittest.TestCase):
    def test_unicode_separator_is_field_content_not_a_record_boundary(self):
        raw = "customer_id,customer_name,home_region,source_revision,source_updated_at\nC1,Ada\u2028Lovelace,WEST,1,2026-01-01T00:00:00Z\n".encode(
            "utf8"
        )
        rows = parse_csv("customers", raw, "b", "x.csv")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["parse_reasons"], [])


class InvalidCorrectionTests(unittest.TestCase):
    def test_invalid_timestamp_cannot_win_over_valid_revision(self):
        normalized, reasons = validate(
            "orders", {**ORDER, "source_revision": "2", "source_updated_at": "2026-01-01T00:00:00+00:99"}
        )
        outcomes = resolve(
            [candidate("new", normalized["source_revision"], "different", reasons)],
            candidate("target", 1, "old"),
        )
        self.assertEqual(outcomes[0]["disposition"], "invalid")
