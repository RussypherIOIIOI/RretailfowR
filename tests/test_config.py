import unittest
from retailflow.config import Config, token


class ConfigTests(unittest.TestCase):
    def test_quoted_catalog_and_restricted_namespace(self):
        self.assertEqual(Config("my-catalog").table("gold", "fact"), "`my-catalog`.`retailflow_gold`.`fact`")
        for value in ("default", "retailflow;drop", "retailflow_../"):
            with self.assertRaises(ValueError):
                Config("workspace", value)
        with self.assertRaises(ValueError):
            Config("workspace", max_reject_fraction=float("nan"))
        with self.assertRaises(ValueError):
            token("bad'id")
