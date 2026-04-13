"""
Quill Health Module — Health Checks and Circuit Breakers
=========================================================
Provides health check endpoints and circuit breaker pattern.

Zero dependencies — uses only stdlib.
"""

from datetime import datetime, timezone
from typing import Optional


class CircuitBreaker:
    """
    Simple circuit breaker for API calls.
    
    States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (probing)
    
    Usage:
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        if cb.allow():
            try:
                result = api_call()
                cb.success()
            except Exception:
                cb.failure()
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time = None

    def allow(self) -> bool:
        """Check if a request is allowed."""
        if self.state == "closed":
            return True
        if self.state == "open":
            elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
            if elapsed > self.recovery_timeout:
                self.state = "half_open"
                return True
            return False
        # half_open — allow one probe
        return True

    def success(self):
        """Record a successful call."""
        self.failures = 0
        self.state = "closed"

    def failure(self):
        """Record a failed call."""
        self.failures += 1
        self.last_failure_time = datetime.now(timezone.utc)
        if self.failures >= self.failure_threshold:
            self.state = "open"

    def reset(self):
        """Manually reset the circuit breaker."""
        self.failures = 0
        self.state = "closed"
        self.last_failure_time = None

    def status(self) -> dict:
        return {
            "state": self.state,
            "failures": self.failures,
            "threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


class HealthChecker:
    """Aggregates health status from multiple subsystems."""

    def __init__(self):
        self.checks = {}

    def register(self, name: str, check_fn):
        """Register a health check function. fn() should return dict with 'healthy' key."""
        self.checks[name] = check_fn

    def check_all(self) -> dict:
        """Run all registered health checks."""
        results = {}
        all_healthy = True

        for name, fn in self.checks.items():
            try:
                result = fn()
                results[name] = result
                if not result.get("healthy", False):
                    all_healthy = False
            except Exception as e:
                results[name] = {"healthy": False, "error": str(e)}
                all_healthy = False

        return {
            "healthy": all_healthy,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "checks": results,
        }
