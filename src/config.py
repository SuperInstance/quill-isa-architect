"""
Quill Configuration Module
===========================
Loads environment variables from .env file, provides defaults,
validates required fields, and exposes a clean config dict.

Zero dependencies — uses only stdlib (os, pathlib, json).
"""

import os
import json
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent.resolve()
ENV_FILE = REPO_ROOT / ".env"
VESSEL_FILE = REPO_ROOT / "vessel.json"
CONFIG_FILE = REPO_ROOT / "agent.cfg"


def load_env_file(path: Path = ENV_FILE) -> dict:
    """Parse .env file into a dict. Skips comments and blank lines."""
    env = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip("\"'")
    return env


def load_vessel_json(path: Path = VESSEL_FILE) -> dict:
    """Load vessel.json deployment descriptor."""
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load() -> dict:
    """
    Load full configuration from all sources.
    Priority: environment variables > .env file > vessel.json defaults.
    
    Returns a dict with all configuration keys.
    """
    env_file = load_env_file()
    vessel = load_vessel_json()

    config = {
        # Model configuration
        "api_key": os.environ.get("QUILL_API_KEY")
                    or env_file.get("QUILL_API_KEY", ""),
        "base_url": (os.environ.get("QUILL_BASE_URL")
                     or env_file.get("QUILL_BASE_URL", "")).rstrip("/"),
        "model": os.environ.get("QUILL_MODEL")
                   or env_file.get("QUILL_MODEL", ""),
        "temperature": float(env_file.get("QUILL_TEMPERATURE", "0.7")),
        "max_tokens": int(env_file.get("QUILL_MAX_TOKENS", "4096")),

        # GitHub configuration
        "github_pat": os.environ.get("GITHUB_PAT")
                       or env_file.get("GITHUB_PAT", ""),
        "github_org": os.environ.get("GITHUB_ORG")
                       or env_file.get("GITHUB_ORG", "SuperInstance"),

        # Agent identity
        "name": vessel.get("name", "quill"),
        "version": vessel.get("version", "2.0.0"),
        "role": vessel.get("role", "architect"),
        "fleet": vessel.get("fleet", "SuperInstance"),
        "reporting_to": vessel.get("reporting_to", "Oracle1"),

        # Memory configuration
        "memory_hot_ttl": vessel.get("memory", {}).get("hot_ttl_seconds", 7200),
        "memory_warm_ttl": vessel.get("memory", {}).get("warm_ttl_seconds", 604800),
        "memory_path": REPO_ROOT / ".quill-memory",

        # Paths
        "repo_root": REPO_ROOT,
        "prompt_file": REPO_ROOT / "PROMPT.md",
        "knowledge_dir": REPO_ROOT / "KNOWLEDGE",
        "diary_dir": REPO_ROOT / "DIARY",
        "skills_dir": REPO_ROOT / "SKILLS",
    }

    return config


def validate(config: dict) -> list:
    """
    Validate configuration. Returns list of issues.
    Each issue is a dict: {"level": "error"|"warning", "message": str, "fix": str}
    """
    issues = []

    if not config["api_key"]:
        issues.append({
            "level": "error",
            "message": "QUILL_API_KEY is not set",
            "fix": "Add QUILL_API_KEY=your-key to .env"
        })

    if not config["base_url"]:
        issues.append({
            "level": "error",
            "message": "QUILL_BASE_URL is not set",
            "fix": "Add QUILL_BASE_URL=https://api.openai.com/v1 to .env"
        })

    if not config["model"]:
        issues.append({
            "level": "error",
            "message": "QUILL_MODEL is not set",
            "fix": "Add QUILL_MODEL=gpt-4o to .env"
        })

    if not config["github_pat"]:
        issues.append({
            "level": "warning",
            "message": "GITHUB_PAT is not set — fleet operations disabled",
            "fix": "Add GITHUB_PAT=ghp_xxx to .env for GitHub API access"
        })

    if not config["prompt_file"].exists():
        issues.append({
            "level": "warning",
            "message": f"PROMPT.md not found at {config['prompt_file']}",
            "fix": "Create PROMPT.md with Quill's system prompt"
        })

    return issues


def is_ready(config: dict) -> bool:
    """Quick check: is Quill minimally configured to run?"""
    return bool(config["api_key"] and config["base_url"] and config["model"])
