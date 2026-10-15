import json
import tempfile
import unittest
from pathlib import Path
from retailflow.fixtures import generate
from retailflow.contracts import digest, parse_csv


class FixtureTests(unittest.TestCase):
    def test_seeded_manifests_and_regeneration(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(tmp)
            first = {str(p.relative_to(tmp)): p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            generate(tmp)
            second = {str(p.relative_to(tmp)): p.read_bytes() for p in Path(tmp).rglob("*") if p.is_file()}
            self.assertEqual(first, second)
            for batch in ("batch1", "batch2", "arrival"):
                manifest = json.loads((Path(tmp) / batch / "manifest.json").read_text())
                for entry in manifest["files"]:
                    content = (Path(tmp) / batch / entry["filename"]).read_bytes()
                    self.assertEqual(digest(content), entry["sha256"])
                    self.assertEqual(
                        len(parse_csv(entry["entity"], content, batch, entry["filename"])),
                        entry["record_count"],
                    )
