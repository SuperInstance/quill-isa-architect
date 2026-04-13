#!/usr/bin/env python3
"""
Quill — ISA Spec Architect & Code Archaeologist
Boot Script with Lighthouse Keeper Integration

Usage:
    python3 boot.py                              # Interactive session
    python3 boot.py --task "Audit flux-runtime"  # Directed task
    python3 boot.py --checkin                    # Check in with Oracle1
    python3 boot.py --version                    # Show version

The lighthouse keeper provides Quill's runtime API key/URL,
allowing Oracle1 to boot Quill with whichever model fits the task.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

# ── Version ───────────────────────────────────────────────────────
VERSION = "19.0"
AGENT_NAME = "Quill"
AGENT_DESIGNATION = "ISA Spec Architect & Code Archaeologist"

# ── Configuration ─────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.resolve()
ENV_FILE = REPO_ROOT / ".env"
CONFIG_FILE = REPO_ROOT / "agent.cfg"
PROMPT_FILE = REPO_ROOT / "PROMPT.md"
CAPABILITY_FILE = REPO_ROOT / "CAPABILITY.toml"


def load_env() -> dict:
    """Load environment variables from .env file."""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()
    # Override with actual environment variables
    for key in ["QUILL_API_KEY", "QUILL_BASE_URL", "QUILL_MODEL", "GITHUB_PAT", "GITHUB_ORG"]:
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def load_config() -> dict:
    """Load agent configuration from agent.cfg (simple TOML parser)."""
    config = {}
    if not CONFIG_FILE.exists():
        return config
    current_section = "global"
    for line in CONFIG_FILE.read_text().strip().split("\n"):
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            config[current_section] = config.get(current_section, {})
        elif "=" in line and not line.startswith("#"):
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Handle boolean
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            if current_section not in config:
                config[current_section] = {}
            config[current_section][key] = value
    return config


def validate_environment(env: dict) -> list:
    """Check that required environment variables are set."""
    issues = []
    if not env.get("QUILL_API_KEY"):
        issues.append("QUILL_API_KEY is not set — Quill needs an API key to function")
    if not env.get("QUILL_BASE_URL"):
        issues.append("QUILL_BASE_URL is not set — Quill needs to know which model API to use")
    if not env.get("QUILL_MODEL"):
        issues.append("QUILL_MODEL is not set — Quill needs to know which model to use")
    if not env.get("GITHUB_PAT"):
        issues.append("GITHUB_PAT is not set — Quill needs GitHub access for fleet operations")
    return issues


def load_system_prompt() -> str:
    """Load the full system prompt from PROMPT.md."""
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text()
    return "# Quill System Prompt\n\n[Error: PROMPT.md not found]\n"


def load_knowledge_context() -> str:
    """Load key knowledge files as context."""
    knowledge_dir = REPO_ROOT / "KNOWLEDGE"
    context_parts = []
    if knowledge_dir.exists():
        for f in sorted(knowledge_dir.glob("*.md")):
            # Read first 500 lines of each knowledge file as context
            lines = f.read_text().strip().split("\n")[:500]
            context_parts.append(f"## {f.name}\n" + "\n".join(lines))
    return "\n\n---\n\n".join(context_parts) if context_parts else ""


def load_capability_toml() -> str:
    """Load CAPABILITY.toml as context."""
    if CAPABILITY_FILE.exists():
        return CAPABILITY_FILE.read_text()
    return ""


def build_boot_context(env: dict, task: str = None) -> str:
    """Build the full boot context: system prompt + knowledge + task."""
    system_prompt = load_system_prompt()
    knowledge = load_knowledge_context()
    capabilities = load_capability_toml()

    context = f"""# Quill Boot Context — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

## Runtime Configuration
- Model: {env.get('QUILL_MODEL', 'NOT CONFIGURED')}
- API Base: {env.get('QUILL_BASE_URL', 'NOT CONFIGURED')}
- GitHub Org: {env.get('GITHUB_ORG', 'NOT CONFIGURED')}
- Fleet: SuperInstance

## Agent Identity
- Name: {AGENT_NAME}
- Version: {VERSION}
- Role: {AGENT_DESIGNATION}

---

{system_prompt}

---

## Fleet Knowledge Context

{knowledge}

---

## Capability Declaration

{capabilities}
"""
    if task:
        context += f"""

---

## Current Task (from Oracle1)

{task}
"""
    return context


def print_banner():
    """Print Quill's boot banner."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  Quill — ISA Spec Architect & Code Archaeologist        ║
║  Version {VERSION}                                          ║
║  Fleet: SuperInstance | Level: Architect                 ║
╚══════════════════════════════════════════════════════════╝
""")


def interactive_session(env: dict, config: dict):
    """Run Quill in interactive mode."""
    print(f"Booting Quill with model: {env.get('QUILL_MODEL', 'NOT CONFIGURED')}")
    print(f"API endpoint: {env.get('QUILL_BASE_URL', 'NOT CONFIGURED')}")
    print(f"Knowledge files: {len(list((REPO_ROOT / 'KNOWLEDGE').glob('*.md')))} loaded")
    print()
    print("Quill is ready. Describe your task or type 'quit' to exit.")
    print()

    while True:
        try:
            task = input("quill> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nQuill signing off.")
            break

        if task.lower() in ("quit", "exit", "q"):
            print("Quill signing off.")
            break
        if not task:
            continue

        # Build context and display what would be sent to the model
        context = build_boot_context(env, task)
        print(f"\n[Task received — context built: {len(context):,} characters]")
        print(f"[In production, this context would be sent to {env.get('QUILL_MODEL', 'MODEL')}]")
        print(f"[System prompt: {len(load_system_prompt()):,} chars | Knowledge: {len(load_knowledge_context()):,} chars]")
        print()

        # Write task to task log
        task_log = REPO_ROOT / ".task-log.jsonl"
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "model": env.get("QUILL_MODEL", "unknown"),
            "context_size": len(context)
        }
        with open(task_log, "a") as f:
            f.write(json.dumps(entry) + "\n")


def do_checkin(env: dict):
    """Check in with Oracle1 — scan bottles and report status."""
    print(f"Checking in with Oracle1...")
    org = env.get("GITHUB_ORG", "SuperInstance")
    pat = env.get("GITHUB_PAT")

    if not pat:
        print("ERROR: GITHUB_PAT required for fleet check-in")
        return

    # Read bottles from Oracle1
    import urllib.request
    req = urllib.request.Request(
        f"https://api.github.com/repos/{org}/oracle1-vessel/contents/from-fleet",
        headers={"Authorization": f"token {pat}", "Accept": "application/vnd.github.v3+json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            bottles = json.loads(resp.read())
            print(f"Found {len(bottles)} bottles from Oracle1:")
            for b in bottles[:10]:
                print(f"  - {b['name']} ({b.get('size', 0)} bytes)")
            if len(bottles) > 10:
                print(f"  ... and {len(bottles) - 10} more")
    except Exception as e:
        print(f"Could not reach Oracle1's vessel: {e}")

    print(f"\nQuill status: Operational | Version {VERSION} | Ready for tasks")


def main():
    parser = argparse.ArgumentParser(description=f"Quill — {AGENT_DESIGNATION}")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--task", "-t", type=str, help="Directed task from Oracle1")
    parser.add_argument("--checkin", action="store_true", help="Check in with Oracle1")
    parser.add_argument("--env-check", action="store_true", help="Validate environment only")
    parser.add_argument("--export-context", type=str, metavar="FILE",
                        help="Export boot context to file instead of running")
    parser.add_argument("--model", type=str, help="Override model from env")
    parser.add_argument("--api-key", type=str, help="Override API key from env")
    parser.add_argument("--base-url", type=str, help="Override base URL from env")
    args = parser.parse_args()

    print_banner()

    # Load configuration
    env = load_env()
    config = load_config()

    # CLI overrides
    if args.model:
        env["QUILL_MODEL"] = args.model
    if args.api_key:
        env["QUILL_API_KEY"] = args.api_key
    if args.base_url:
        env["QUILL_BASE_URL"] = args.base_url

    if args.version:
        print(f"Quill v{VERSION} — {AGENT_DESIGNATION}")
        return

    # Environment validation
    issues = validate_environment(env)
    if args.env_check or issues:
        if issues:
            print("Environment issues found:")
            for i in issues:
                print(f"  ⚠️  {i}")
            print()
            print(f"Copy .env.example to .env and fill in your values:")
            print(f"  cp .env.example .env")
            if not args.env_check:
                print("\nContinuing in degraded mode (no API, no GitHub)...")
        elif args.env_check:
            print("All environment variables are configured. Quill is ready to boot.")
            return

    # Export context mode
    if args.export_context:
        task = args.task or None
        context = build_boot_context(env, task)
        Path(args.export_context).write_text(context)
        print(f"Boot context exported to {args.export_context} ({len(context):,} characters)")
        return

    # Checkin mode
    if args.checkin:
        do_checkin(env)
        return

    # Interactive session
    interactive_session(env, config)


if __name__ == "__main__":
    main()
