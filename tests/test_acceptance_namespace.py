import unittest
from tests.delta_acceptance import acceptance_config


class AcceptanceNamespaceTests(unittest.TestCase):
    def test_fresh_attempt_uses_only_approved_schemas_and_fixture_volume(self):
        original = acceptance_config("tmc_solutions_jvs", "20261030a", "")
        attempt = acceptance_config("tmc_solutions_jvs", "20261030a", "attemptb")
        for layer in ("bronze", "silver", "gold", "ops"):
            self.assertEqual(original.schema(layer), attempt.schema(layer))
            self.assertNotEqual(original.table(layer, "records"), attempt.table(layer, "records"))
            self.assertTrue(attempt.table(layer, "records").endswith("`attemptb_records`"))
        self.assertEqual(original.table("bronze", "fixtures"), attempt.table("bronze", "fixtures"))
        self.assertEqual(attempt.volume, original.volume + "/attemptb")

    def test_attempt_cannot_escape_approved_namespace(self):
        for attempt in ("../x", "b;drop", "b/x", "B", "b" * 17):
            with self.subTest(attempt=attempt), self.assertRaises(ValueError):
                acceptance_config("tmc_solutions_jvs", "20261030a", attempt)
