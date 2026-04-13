"""Tests for Quill's health module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from health import CircuitBreaker, HealthChecker


class TestCircuitBreaker(unittest.TestCase):

    def test_starts_closed(self):
        cb = CircuitBreaker()
        self.assertTrue(cb.allow())
        self.assertEqual(cb.status()["state"], "closed")

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.failure()
        cb.failure()
        self.assertTrue(cb.allow())  # Still closed after 2
        cb.failure()  # Third failure opens it
        self.assertFalse(cb.allow())

    def test_success_resets(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.failure()
        cb.success()
        self.assertEqual(cb.status()["failures"], 0)
        self.assertEqual(cb.status()["state"], "closed")

    def test_manual_reset(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.failure()
        self.assertFalse(cb.allow())
        cb.reset()
        self.assertTrue(cb.allow())


class TestHealthChecker(unittest.TestCase):

    def test_all_healthy(self):
        hc = HealthChecker()
        hc.register("test", lambda: {"healthy": True})
        result = hc.check_all()
        self.assertTrue(result["healthy"])
        self.assertTrue(result["checks"]["test"]["healthy"])

    def test_one_unhealthy(self):
        hc = HealthChecker()
        hc.register("ok", lambda: {"healthy": True})
        hc.register("fail", lambda: {"healthy": False, "error": "test"})
        result = hc.check_all()
        self.assertFalse(result["healthy"])

    def test_exception_in_check(self):
        hc = HealthChecker()
        hc.register("crash", lambda: 1 / 0)
        result = hc.check_all()
        self.assertFalse(result["healthy"])
        self.assertIn("error", result["checks"]["crash"])


if __name__ == "__main__":
    unittest.main()
