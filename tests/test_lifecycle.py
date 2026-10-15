import unittest
from retailflow.lifecycle import may_start, may_abandon


class LifecycleTests(unittest.TestCase):
    def test_unfinished_evaluation_must_resume_or_be_abandoned(self):
        self.assertFalse(may_start([{"sequence": 2, "status": "silver_complete"}], 1))
        self.assertTrue(may_start([{"sequence": 2, "status": "abandoned"}], 1))
        self.assertTrue(may_start([{"sequence": 1, "status": "silver_complete"}], 1))

    def test_cannot_abandon_published_evaluation(self):
        self.assertFalse(may_abandon({"sequence": 1}, 1))
        self.assertTrue(may_abandon({"sequence": 2}, 1))
