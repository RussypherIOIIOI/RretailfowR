"""Small reproducible fixtures. Runs unchanged locally or inside Databricks."""

import csv
import io
import json
import random
from pathlib import Path
from retailflow.contracts import FIELDS, digest

STAMP = "2026-01-01T00:00:00Z"


def generate(root, seed=17):
    rng = random.Random(seed)
    root = Path(root)
    customers = [["C1", "Ada", "WEST", "1", STAMP], ["C2", "Ben", "EAST", "1", STAMP]]
    products = [["P1", "Mug", "Home", "10.00", "1", STAMP], ["P2", "Kettle", "Home", "30.00", "1", STAMP]]

    def order(
        oid,
        line="1",
        cid="C1",
        pid="P1",
        day="2026-01-01",
        region="WEST",
        qty="1",
        price="10.00",
        discount="0.00",
        rev="1",
    ):
        return [oid, line, cid, pid, day, region, qty, price, discount, rev, STAMP]

    a1 = order("A1", qty="2")
    a21 = order("A2", cid="C2", pid="P2", region="EAST", price="30.00", discount="5.00")
    a22 = order("A2", line="2", cid="C2", region="EAST")
    correction = order(
        "A1", pid="P2", day="2026-01-02", region="EAST", qty="3", price="12.00", discount="1.00", rev="2"
    )
    batch1 = {
        "customers": customers,
        "products": products,
        "orders": [a1, a21, a22, a1, order("BAD", qty="0")],
    }
    batch2 = {
        "customers": [["C1", "Ada Lovelace", "SOUTH", "2", STAMP], ["C3", "Cy", "NORTH", "1", STAMP]],
        "products": [["P2", "Kettle Plus", "Home", "99.00", "2", STAMP]],
        "orders": [
            correction,
            correction,
            a1,
            order("A2", cid="C2", pid="P2", region="EAST", qty="0", price="30.00", rev="2"),
            order("A2", line="2", cid="C2", region="EAST", price="11.00"),
            order("A3", price="15.00"),
            order("A3", price="15.00", rev="3"),
            order("A3", price="19.00", rev="2"),
            order("A4", cid="C9", price="7.00"),
            order("A5", price="8.00", rev="2"),
            order("A5", price="9.00", rev="2"),
            order("A5", price="6.00"),
            order("BROKEN", day="2026-02-30", qty="0", price="oops"),
        ],
    }
    arrival = {"customers": [["C9", "Dee", "NORTH", "1", STAMP]], "products": [], "orders": []}
    for batch_id, entities in [("batch1", batch1), ("batch2", batch2), ("arrival", arrival)]:
        directory = root / batch_id
        directory.mkdir(parents=True, exist_ok=True)
        manifest = {"contract_version": 1, "batch_id": batch_id, "files": []}
        for entity, source_rows in entities.items():
            rows = list(source_rows)
            rng.shuffle(rows)
            out = io.StringIO(newline="")
            writer = csv.writer(out, lineterminator="\n")
            writer.writerow(FIELDS[entity])
            writer.writerows(rows)
            if batch_id == "batch2" and entity == "orders":
                out.write('MALFORMED,"unterminated\n')
            content = out.getvalue().encode("utf8")
            path = directory / (entity + ".csv")
            if path.exists() and path.read_bytes() != content:
                raise ValueError(f"Refusing to replace changed immutable fixture {path}")
            path.write_bytes(content)
            manifest["files"].append(
                {
                    "entity": entity,
                    "filename": path.name,
                    "sha256": digest(content),
                    "record_count": len(rows) + (batch_id == "batch2" and entity == "orders"),
                }
            )
        encoded = json.dumps(manifest, indent=2) + "\n"
        mpath = directory / "manifest.json"
        if mpath.exists() and mpath.read_text() != encoded:
            raise ValueError("Refusing to replace changed manifest")
        mpath.write_text(encoded, encoding="utf8")
    return root


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="fixtures")
    parser.add_argument("--seed", type=int, default=17)
    args = parser.parse_args()
    generate(args.output, args.seed)
