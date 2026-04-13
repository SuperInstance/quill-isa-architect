#!/usr/bin/env python3
"""
Quill Lighthouse Keeper — Runtime API Abstraction Layer

The lighthouse keeper provides Quill's connection to whichever LLM
model fits the current task. Oracle1 (or any fleet coordinator) can
swap models by changing environment variables or providing new
credentials at boot time.

This layer is model-agnostic: it wraps any OpenAI-compatible API
and provides a unified interface for Quill's reasoning.

Supported backends:
  - OpenAI (GPT-4o, GPT-4, etc.)
  - Anthropic (Claude Sonnet, Claude Opus, etc.)
  - Google (Gemini Pro, etc.)
  - DeepSeek (DeepSeek-V3, etc.)
  - Local models (Ollama, LM Studio, vLLM)
  - Z.AI (GLM-5, etc.)

Usage:
    from lighthouse import LighthouseKeeper

    keeper = LighthouseKeeper()  # Reads from .env or env vars
    response = keeper.chat("Audit the flux-runtime repo for ISA conformance")
    print(response)
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


REPO_ROOT = Path(__file__).parent.resolve()
ENV_FILE = REPO_ROOT / ".env"


class LighthouseKeeper:
    """
    Model-agnostic LLM abstraction for Quill.

    The keeper manages the connection to whatever model is configured,
    handling authentication, request formatting, and response parsing.
    Oracle1 can swap models by changing QUILL_BASE_URL and QUILL_MODEL
    in the environment.

    The keeper also provides health monitoring: it can periodically
    check that the model API is responsive and report status.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        github_pat: Optional[str] = None,
    ):
        """Initialize the lighthouse keeper.

        Args:
            api_key: API key for the LLM provider (or set QUILL_API_KEY env)
            base_url: Base URL for the LLM API (or set QUILL_BASE_URL env)
            model: Model identifier (or set QUILL_MODEL env)
            github_pat: GitHub PAT for fleet operations (or set GITHUB_PAT env)
        """
        self.api_key = api_key or os.environ.get("QUILL_API_KEY") or self._load_env("QUILL_API_KEY")
        self.base_url = (base_url or os.environ.get("QUILL_BASE_URL")
                         or self._load_env("QUILL_BASE_URL")).rstrip("/")
        self.model = model or os.environ.get("QUILL_MODEL") or self._load_env("QUILL_MODEL")
        self.github_pat = (github_pat or os.environ.get("GITHUB_PAT")
                           or self._load_env("GITHUB_PAT"))
        self.github_org = os.environ.get("GITHUB_ORG") or self._load_env("GITHUB_ORG") or "SuperInstance"

        self.boot_time = datetime.now(timezone.utc)
        self.request_count = 0
        self.last_health_check = None
        self.health_status = "unknown"

    @staticmethod
    def _load_env(key: str) -> Optional[str]:
        """Load a value from .env file."""
        if ENV_FILE.exists():
            for line in ENV_FILE.read_text().strip().split("\n"):
                line = line.strip()
                if line.startswith(f"{key}=") and not line.startswith("#"):
                    _, _, value = line.partition("=")
                    return value.strip()
        return None

    @property
    def is_configured(self) -> bool:
        """Check if the keeper has all required configuration."""
        return bool(self.api_key and self.base_url and self.model)

    @property
    def config_summary(self) -> dict:
        """Get a summary of the current configuration (keys redacted)."""
        return {
            "model": self.model,
            "base_url": self.base_url,
            "api_key_set": bool(self.api_key),
            "api_key_prefix": self.api_key[:8] + "..." if self.api_key else None,
            "github_pat_set": bool(self.github_pat),
            "github_org": self.github_org,
            "boot_time": self.boot_time.isoformat(),
            "request_count": self.request_count,
            "health_status": self.health_status,
        }

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> str:
        """Send a chat completion request to the configured model.

        This is the primary interface: give Quill a task and get a response.

        Args:
            message: The user message / task description
            system_prompt: Optional system prompt override (uses PROMPT.md by default)
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum response tokens
            **kwargs: Additional parameters passed to the API

        Returns:
            The model's response text

        Raises:
            RuntimeError: If the API key or base URL is not configured
            urllib.error.URLError: If the API request fails
        """
        if not self.is_configured:
            raise RuntimeError(
                "Lighthouse keeper not configured. Set QUILL_API_KEY, QUILL_BASE_URL, "
                "and QUILL_MODEL in .env or environment variables."
            )

        if system_prompt is None:
            prompt_file = REPO_ROOT / "PROMPT.md"
            if prompt_file.exists():
                system_prompt = prompt_file.read_text()

        payload = {
            "model": self.model,
            "messages": [],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        if system_prompt:
            payload["messages"].append({"role": "system", "content": system_prompt})
        payload["messages"].append({"role": "user", "content": message})

        self.request_count += 1
        return self._make_request(payload)

    def _make_request(self, payload: dict) -> str:
        """Make an API request to the configured endpoint."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                self.health_status = "healthy"
                self.last_health_check = datetime.now(timezone.utc)
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            self.health_status = f"error_{e.code}"
            self.last_health_check = datetime.now(timezone.utc)
            error_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"API error {e.code}: {error_body[:500]}"
            ) from e
        except urllib.error.URLError as e:
            self.health_status = "unreachable"
            self.last_health_check = datetime.now(timezone.utc)
            raise RuntimeError(
                f"Cannot reach model API at {self.base_url}: {e.reason}"
            ) from e

    def health_check(self) -> dict:
        """Check if the model API is responsive.

        Returns:
            Health status dict with 'status', 'latency_ms', and 'model' fields.
        """
        start = datetime.now(timezone.utc)
        try:
            # Send a minimal request
            self.chat("ping", max_tokens=5, temperature=0)
            latency = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return {
                "status": "healthy",
                "latency_ms": round(latency),
                "model": self.model,
                "base_url": self.base_url,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "model": self.model,
                "base_url": self.base_url,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

    def keep(self, interval: int = 300, webhook: Optional[str] = None):
        """Run as a lighthouse keeper — periodic health monitoring.

        This is the daemon mode: the keeper stays alive, periodically
        checks the model API health, and optionally reports to a webhook.

        Args:
            interval: Health check interval in seconds (default: 300 = 5 min)
            webhook: Optional webhook URL to POST health reports to
        """
        import time
        print(f"Lighthouse keeper starting — checking every {interval}s")
        print(f"Model: {self.model}")
        print(f"Endpoint: {self.base_url}")
        print(f"Press Ctrl+C to stop\n")

        try:
            while True:
                health = self.health_check()
                status_icon = "✅" if health["status"] == "healthy" else "❌"
                print(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] "
                      f"{status_icon} {health['status']} "
                      f"({health.get('latency_ms', '?')}ms) "
                      f"[{self.request_count} requests total]")

                if webhook and health["status"] == "unhealthy":
                    self._report_unhealthy(webhook, health)

                time.sleep(interval)
        except KeyboardInterrupt:
            print(f"\nLighthouse keeper stopped. Total requests: {self.request_count}")

    def _report_unhealthy(self, webhook: str, health: dict):
        """Report unhealthy status to webhook."""
        try:
            payload = json.dumps({
                "agent": "quill",
                "status": "unhealthy",
                "health": health,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }).encode("utf-8")
            req = urllib.request.Request(
                webhook, data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass  # Don't crash the keeper if webhook fails

    def read_bottle(self, repo: str, path: str) -> Optional[str]:
        """Read a bottle from a fleet vessel via GitHub API.

        Args:
            repo: Repository name (e.g., "SuperInstance/oracle1-vessel")
            path: File path within the repo (e.g., "from-fleet/DISPATCH.md")

        Returns:
            File contents as string, or None if not found.
        """
        if not self.github_pat:
            return None

        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"token {self.github_pat}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                import base64
                return base64.b64decode(data["content"]).decode("utf-8")
        except Exception:
            return None

    def list_bottles(self, repo: str, directory: str = "") -> list:
        """List bottles in a fleet vessel directory.

        Args:
            repo: Repository name
            directory: Directory path within the repo

        Returns:
            List of bottle metadata dicts (name, size, sha)
        """
        if not self.github_pat:
            return []

        url = f"https://api.github.com/repos/{repo}/contents/{directory}"
        headers = {
            "Authorization": f"token {self.github_pat}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [
                    {"name": item["name"], "size": item.get("size", 0),
                     "sha": item.get("sha", "")[:8]}
                    for item in data if isinstance(data, list)
                ]
        except Exception:
            return []


def main():
    """CLI interface for the lighthouse keeper."""
    import argparse
    parser = argparse.ArgumentParser(description="Quill Lighthouse Keeper")
    parser.add_argument("--health", action="store_true", help="Run a single health check")
    parser.add_argument("--keep", action="store_true", help="Run as daemon (periodic health checks)")
    parser.add_argument("--interval", type=int, default=300, help="Health check interval in seconds")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--chat", type=str, metavar="MESSAGE", help="Send a single chat message")
    args = parser.parse_args()

    keeper = LighthouseKeeper()

    if args.config:
        print(json.dumps(keeper.config_summary, indent=2))
        if not keeper.is_configured:
            print("\n⚠️  Not fully configured. Copy .env.example to .env")
        return

    if args.health:
        health = keeper.health_check()
        print(json.dumps(health, indent=2))
        return

    if args.chat:
        if not keeper.is_configured:
            print("Error: Not configured. Set QUILL_API_KEY, QUILL_BASE_URL, QUILL_MODEL")
            return
        response = keeper.chat(args.chat)
        print(response)
        return

    if args.keep:
        if not keeper.is_configured:
            print("Error: Not configured. Set QUILL_API_KEY, QUILL_BASE_URL, QUILL_MODEL")
            return
        keeper.keep(interval=args.interval)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
