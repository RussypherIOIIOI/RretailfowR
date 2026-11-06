"""Guard rails for privileged provisioning and evidence completeness (no live mutations)."""

import unittest
from unittest.mock import patch
from scripts import provision_release
from scripts.databricks_cli import sql


class ReleaseToolsTests(unittest.TestCase):
    def test_provisioning_refuses_to_adopt_existing_schema_before_any_grants(self):
        existing = [{"name": "retailflow_gold", "comment": "Unrelated existing dataset"}]
        with patch("sys.argv", ["provision_release", "--apply"]), \
             patch.object(provision_release, "save"), \
             patch.object(provision_release, "cli", return_value=existing) as remote:
            with self.assertRaisesRegex(ValueError, "Refusing to adopt"):
                provision_release.main()
        remote.assert_called_once_with("U2M", "schemas", "list", "tmc_solutions_jvs")

    def test_provisioning_refuses_nonempty_owned_schema_before_any_grants(self):
        responses = [[{"name": "retailflow_bronze", "comment": provision_release.COMMENT}],
                     [{"name": "existing_records"}]]
        with patch("sys.argv", ["provision_release", "--apply"]), \
             patch.object(provision_release, "save"), \
             patch.object(provision_release, "cli", side_effect=responses) as remote:
            with self.assertRaisesRegex(ValueError, "expects empty schemas"):
                provision_release.main()
        self.assertEqual(remote.call_count, 2)
        self.assertFalse(any("grants" in call.args for call in remote.call_args_list))

    def test_failed_statement_cannot_become_evidence_success(self):
        result = {"status": {"state": "FAILED", "error": {"message": "missing Gold"}}}
        with patch("scripts.databricks_cli.cli", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "missing Gold"):
                sql("M2M", "warehouse", "catalog", "schema", "SELECT 1")

    def test_incomplete_statement_result_cannot_become_evidence_success(self):
        for manifest in ({"truncated": True}, {"total_chunk_count": 2}):
            with self.subTest(manifest=manifest), patch("scripts.databricks_cli.cli", return_value={
                "status": {"state": "SUCCEEDED"}, "manifest": manifest,
            }):
                with self.assertRaises(AssertionError):
                    sql("M2M", "warehouse", "catalog", "schema", "SELECT 1")
