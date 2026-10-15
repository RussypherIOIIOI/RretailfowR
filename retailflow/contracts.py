"""Pure contracts shared by local tests and Databricks workers. No Spark dependency."""

import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation

RULESET = "retailflow-v1"
REGIONS = {"NORTH", "SOUTH", "EAST", "WEST"}
FIELDS = {
    "customers": ["customer_id", "customer_name", "home_region", "source_revision", "source_updated_at"],
    "products": [
        "product_id",
        "product_name",
        "category",
        "current_price",
        "source_revision",
        "source_updated_at",
    ],
    "orders": [
        "order_id",
        "line_id",
        "customer_id",
        "product_id",
        "order_date",
        "sale_region",
        "quantity",
        "unit_price",
        "discount_amount",
        "source_revision",
        "source_updated_at",
    ],
}
KEYS = {"customers": ["customer_id"], "products": ["product_id"], "orders": ["order_id", "line_id"]}
MAX_MONEY = Decimal("9999999999999999.99")
MAX_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 10000


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode("utf8")).hexdigest()


def validate(entity, row):
    if entity not in FIELDS:
        raise ValueError("Unknown source entity")
    result = {k: str(row.get(k) or "").strip() for k in FIELDS[entity]}
    reasons = []
    for key, value in result.items():
        if not value:
            reasons.append("MISSING_" + key.upper())
        if key.endswith("_id") and not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", value):
            reasons.append("INVALID_" + key.upper())
    revision = result["source_revision"]
    if not re.fullmatch(r"[0-9]{1,10}", revision) or not 1 <= int(revision) <= 2147483647:
        reasons.append("INVALID_REVISION")
        result["source_revision"] = None
    else:
        result["source_revision"] = int(revision)
    stamp = result["source_updated_at"]
    try:
        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)", stamp
        ):
            raise ValueError("Timestamp needs explicit timezone")
        result["source_updated_at"] = (
            datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
        )
    except (ValueError, OverflowError):
        reasons.append("INVALID_SOURCE_UPDATED_AT")
    for key in ("sale_region", "home_region"):
        if key in result:
            result[key] = result[key].upper()
            if result[key] not in REGIONS:
                reasons.append("INVALID_" + key.upper())
    for key in ("customer_name", "product_name", "category"):
        if key in result and len(result[key]) > 200:
            reasons.append("INVALID_" + key.upper())
    money = {}
    for key in ("unit_price", "discount_amount", "current_price"):
        if key not in result:
            continue
        value = result[key]
        try:
            if not re.fullmatch(r"[0-9]{1,16}(?:\.[0-9]{1,2})?", value):
                raise InvalidOperation
            amount = Decimal(value)
            if amount > MAX_MONEY:
                raise InvalidOperation
            money[key] = amount
            result[key] = format(amount, ".2f")
        except InvalidOperation:
            reasons.append("INVALID_" + key.upper())
    if entity == "orders":
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", result["order_date"]):
                raise ValueError
            day = date.fromisoformat(result["order_date"])
            if not date(2020, 1, 1) <= day <= date(2030, 12, 31):
                raise ValueError
        except ValueError:
            reasons.append("INVALID_ORDER_DATE")
        quantity = result["quantity"]
        if not re.fullmatch(r"[0-9]{1,7}", quantity) or not 1 <= int(quantity) <= 1000000:
            reasons.append("INVALID_QUANTITY")
            result["quantity"] = None
        else:
            result["quantity"] = int(quantity)
        if result["quantity"] and "unit_price" in money and "discount_amount" in money:
            gross = result["quantity"] * money["unit_price"]
            net = gross - money["discount_amount"]
            if gross > MAX_MONEY or net > MAX_MONEY:
                reasons.append("MONEY_OVERFLOW")
            if money["discount_amount"] > gross:
                reasons.append("DISCOUNT_EXCEEDS_GROSS")
            result["net_sales"] = format(net, ".2f")
    result["business_key"] = canonical([result[k] for k in KEYS[entity]])
    payload = {
        k: v for k, v in result.items() if k not in ("source_revision", "source_updated_at", "business_key")
    }
    result["payload_hash"] = digest(canonical(payload))
    return result, sorted(set(reasons))


def parse_csv(entity, content, batch_id, filename):
    if entity not in FIELDS or len(content) > MAX_BYTES:
        raise ValueError("Unsupported entity or file larger than 10 MiB")
    lines = re.split(r"\r\n|\n|\r", content.decode("utf-8-sig", errors="strict"))
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or next(csv.reader([lines[0]], strict=True)) != FIELDS[entity]:
        raise ValueError("CSV header must match the versioned contract exactly")
    if len(lines) - 1 > MAX_RECORDS:
        raise ValueError("More than 10000 physical records")
    file_hash = digest(content)
    records = []
    for index, raw in enumerate(lines[1:], start=2):
        parse_reasons = []
        values = []
        try:
            values = next(csv.reader([raw], strict=True))
            if len(values) != len(FIELDS[entity]):
                parse_reasons.append("MALFORMED_CSV")
        except csv.Error:
            parse_reasons.append("MALFORMED_CSV")
        records.append(
            {
                "occurrence_id": digest(canonical([batch_id, entity, file_hash, index])),
                "batch_id": batch_id,
                "entity": entity,
                "filename": filename,
                "file_hash": file_hash,
                "record_index": index,
                "raw_record": raw,
                "row_json": canonical(dict(zip(FIELDS[entity], values))),
                "parse_reasons": parse_reasons,
            }
        )
    return records


def resolve(candidates, target=None):
    """Resolve one natural key. Invalid rows never participate in precedence."""
    if len(candidates) > 1000:
        raise ValueError("More than 1000 candidates for one key; split/revise upstream feed")
    groups = defaultdict(list)
    for row in candidates:
        if not row["reasons"]:
            groups[row["source_revision"]].append(row)
    conflicting = {rev for rev, rows in groups.items() if len({r["payload_hash"] for r in rows}) > 1}
    target_rev = target["source_revision"] if target else 0
    if target and target_rev in groups:
        # Against an established target, matching payloads remain duplicates.
        conflicting.discard(target_rev)
    eligible = [rev for rev in groups if rev not in conflicting and rev > target_rev]
    winning_revision = max(eligible, default=None)
    winner_id = (
        min((r["occurrence_id"] for r in groups[winning_revision]), default=None)
        if winning_revision
        else None
    )
    output = []
    for source in candidates:
        row = dict(source)
        revision = row["source_revision"]
        if row["reasons"]:
            disposition = "invalid"
        elif revision in conflicting:
            disposition = "conflict"
        elif target and revision == target_rev:
            disposition = "exact_duplicate" if row["payload_hash"] == target["payload_hash"] else "conflict"
        elif revision == winning_revision:
            disposition = "accepted_winner" if row["occurrence_id"] == winner_id else "exact_duplicate"
        else:
            disposition = "stale_superseded"
        row["disposition"] = disposition
        if disposition == "conflict":
            row["reasons"] = ["REVISION_CONFLICT"]
        output.append(row)
    return output
