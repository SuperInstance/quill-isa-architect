"""Tests for Quill's memory module."""

import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory import KeeperMemory


class TestKeeperMemory(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.memory = KeeperMemory(base_path=self.tmpdir, hot_ttl=60, warm_ttl=120)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_remember_and_recall(self):
        self.memory.remember("hot", "test_key", {"data": "hello"})
        result = self.memory.recall("hot", "test_key")
        self.assertEqual(result["data"], "hello")

    def test_recall_missing_returns_none(self):
        self.assertIsNone(self.memory.recall("hot", "nonexistent"))

    def test_forget(self):
        self.memory.remember("hot", "to_delete", {"x": 1})
        self.assertTrue(self.memory.forget("hot", "to_delete"))
        self.assertIsNone(self.memory.recall("hot", "to_delete"))

    def test_invalid_tier_raises(self):
        with self.assertRaises(ValueError):
            self.memory.remember("invalid", "key", "value")

    def test_cold_is_permanent(self):
        self.memory.remember("cold", "lesson1", "never forget this")
        result = self.memory.recall("cold", "lesson1")
        self.assertEqual(result, "never forget this")

    def test_recall_all(self):
        self.memory.remember("hot", "a", 1)
        self.memory.remember("hot", "b", 2)
        self.memory.remember("hot", "c", 3)
        results = self.memory.recall_all("hot")
        self.assertEqual(len(results), 3)
        keys = [r["key"] for r in results]
        self.assertIn("a", keys)
        self.assertIn("b", keys)
        self.assertIn("c", keys)

    def test_stats(self):
        self.memory.remember("hot", "x", 1)
        self.memory.remember("warm", "y", 2)
        self.memory.remember("cold", "z", 3)
        stats = self.memory.stats()
        self.assertEqual(stats["hot"]["count"], 1)
        self.assertEqual(stats["warm"]["count"], 1)
        self.assertEqual(stats["cold"]["count"], 1)

    def test_learn_deduplication(self):
        self.memory.learn("Important lesson about CI", "flux-runtime audit")
        self.memory.learn("Important lesson about CI", "different context")
        cold = self.memory.recall_all("cold")
        self.assertEqual(len(cold), 1)  # Deduplicated

    def test_recent_context(self):
        self.memory.remember("hot", "task1", "audited flux-runtime")
        context = self.memory.recent_context()
        self.assertIn("task1", context)
        self.assertIn("Recent Activity", context)

    def test_key_sanitization(self):
        """Keys with special chars should not crash."""
        self.memory.remember("hot", "path/to/file with spaces", "value")
        result = self.memory.recall("hot", "path/to/file with spaces")
        self.assertEqual(result, "value")


if __name__ == "__main__":
    unittest.main()
