import json
import tempfile
import unittest
from pathlib import Path
from retailflow.fixtures import generate
from retailflow.manifest import load_batch


class ManifestTests(unittest.TestCase):
    def test_renamed_identical_file_retains_manifest_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp)
            root = Path(tmp) / "batch1"
            before = load_batch(root)
            manifest = json.loads((root / "manifest.json").read_text())
            (root / "orders.csv").rename(root / "renamed.csv")
            manifest["files"][2]["filename"] = "renamed.csv"
            (root / "manifest.json").write_text(json.dumps(manifest))
            after = load_batch(root)
            self.assertEqual(before["manifest_hash"], after["manifest_hash"])
            self.assertEqual(len(after["records"]), 9)

    def test_changed_bytes_and_unsafe_paths_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp)
            root = Path(tmp) / "batch1"
            (root / "orders.csv").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                load_batch(root)
            manifest = json.loads((root / "manifest.json").read_text())
            manifest["files"][2]["filename"] = "../orders.csv"
            (root / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "filename"):
                load_batch(root)

    def test_empty_required_entity_is_represented(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp)
            result = load_batch(Path(tmp) / "arrival")
            self.assertEqual(result["record_count"], 1)
            self.assertEqual(len(result["files"]), 3)
