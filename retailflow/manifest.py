"""Validate every file before starting a batch. Filenames are locators, not identity."""

import json
import re
from pathlib import Path
from retailflow.contracts import FIELDS, MAX_BYTES, canonical, digest, parse_csv


def load_batch(root):
    root = Path(root).resolve()
    manifest_path = root / "manifest.json"
    if manifest_path.stat().st_size > 65536:
        raise ValueError("Manifest exceeds 64 KiB")
    manifest = json.loads(manifest_path.read_text(encoding="utf8"))
    batch_id = manifest["batch_id"]
    if manifest["contract_version"] != 1 or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", batch_id):
        raise ValueError("Unsupported contract or invalid batch ID")
    files = manifest["files"]
    if len(files) != 3 or {f["entity"] for f in files} != set(FIELDS):
        raise ValueError("Exactly one file for each of three entities is required")
    for entry in files:
        if not re.fullmatch(r"[A-Za-z0-9_-]+\.csv", entry["filename"]):
            raise ValueError("Unsafe source filename")
    records = []
    identity = []
    for entry in files:
        path = (root / entry["filename"]).resolve()
        if path.parent != root or path.stat().st_size > MAX_BYTES:
            raise ValueError("Unsafe path or oversized source file")
        content = path.read_bytes()
        if digest(content) != entry["sha256"]:
            raise ValueError(f"File fingerprint mismatch: {entry['filename']}")
        parsed = parse_csv(entry["entity"], content, batch_id, entry["filename"])
        if len(parsed) != entry["record_count"]:
            raise ValueError(f"Manifest count mismatch: {entry['filename']}")
        records.extend(parsed)
        identity.append({k: entry[k] for k in ("entity", "sha256", "record_count")})
    return {
        "batch_id": batch_id,
        "files": files,
        "records": records,
        "record_count": len(records),
        "manifest_hash": digest(canonical(sorted(identity, key=lambda x: x["entity"]))),
        "manifest_json": canonical(manifest),
    }
