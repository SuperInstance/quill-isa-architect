#!/usr/bin/env python3
"""
Quill — ISA Spec Architect & Code Archaeologist
Boot Script v2.0 — Full Lifecycle Manager

The one command that makes this repo work:
    python3 boot.py --assess          # Score readiness
    python3 boot.py --task "..."      # Work on a task
    python3 boot.py --checkin         # Check in with Oracle1
    python3 boot.py --keep            # Run as lighthouse keeper

Zero dependencies. Python 3.10+. Clone and run.

Lighthouse keeper integration: Oracle1 provides the API key/URL
for whichever model fits the task. Quill routes automatically.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add src to path
REPO_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(REPO_ROOT / "src"))

from config import load, validate, is_ready, REPO_ROOT
from memory import KeeperMemory
from llm import detect_provider, route_model, chat_with_fallback


VERSION = "2.0.0"
AGENT_NAME = "Quill"
DESIGNATION = "ISA Spec Architect & Code Archaeologist"


def print_banner():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  {AGENT_NAME} — {DESIGNATION:<44s}║
║  Version {VERSION:<55s}║
║  Fleet: SuperInstance | Level: Architect                    ║
║  Zero dependencies | Model-agnostic | Modular               ║
╚══════════════════════════════════════════════════════════════╝
""")


def load_system_prompt() -> str:
    """Load PROMPT.md."""
    prompt_file = REPO_ROOT / "PROMPT.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8")
    return ""


def load_knowledge_context() -> str:
    """Load all knowledge files as context."""
    knowledge_dir = REPO_ROOT / "KNOWLEDGE" / "public"
    parts = []
    if knowledge_dir.exists():
        for f in sorted(knowledge_dir.glob("*.md")):
            lines = f.read_text(encoding="utf-8").strip().split("\n")[:300]
            parts.append(f"## {f.name}\n" + "\n".join(lines))
    return "\n\n---\n\n".join(parts)


def load_capability_toml() -> str:
    """Load CAPABILITY.toml."""
    cap = REPO_ROOT / "CAPABILITY.toml"
    if cap.exists():
        return cap.read_text(encoding="utf-8")
    return ""


def build_context(config: dict, task: str = None) -> str:
    """Build the full boot context for the model."""
    system_prompt = load_system_prompt()
    knowledge = load_knowledge_context()
    capabilities = load_capability_toml()
    memory = KeeperMemory(str(REPO_ROOT / ".quill-memory"))
    recent = memory.recent_context()

    parts = [
        f"# Quill Boot Context — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"\n## Runtime",
        f"- Model: {config['model']}",
        f"- Provider: {detect_provider(config['base_url'])}",
        f"- API: {config['base_url']}",
        f"- Version: {VERSION}",
        "",
    ]

    if recent:
        parts.append("## Recent Memory")
        parts.append(recent)
        parts.append("")

    parts.append(system_prompt)

    if knowledge:
        parts.append("\n---\n\n## Fleet Knowledge\n")
        parts.append(knowledge)

    if capabilities:
        parts.append("\n---\n\n## Capability Declaration\n")
        parts.append(capabilities)

    if task:
        parts.append(f"\n---\n\n## Current Task\n\n{task}")

    return "\n".join(parts)


def assess(config: dict) -> int:
    """
    Assess bootcamp readiness. Returns score 0-100.
    Checks environment, vessel files, knowledge, skills, and tools.
    """
    print("╔══════════════════════════════════════════╗")
    print("║  Quill Bootcamp Assessment               ║")
    print("╚══════════════════════════════════════════╝\n")

    score = 0
    max_score = 0
    checks = []

    # 1. Environment (30 pts)
    print("─── Environment (30 pts) ───")
    env_issues = validate(config)
    env_max = 30
    if not env_issues:
        env_score = env_max
        print(f"  ✅ All environment variables configured ({env_max}/{env_max})")
    else:
        env_score = max(0, env_max - len([i for i in env_issues if i["level"] == "error"]) * 10)
        for issue in env_issues:
            icon = "🔴" if issue["level"] == "error" else "⚠️"
            print(f"  {icon} {issue['message']}")
            print(f"     Fix: {issue['fix']}")
        print(f"  Score: {env_score}/{env_max}")
    checks.append(("Environment", env_score, env_max))
    score += env_score
    max_score += env_max

    # 2. Vessel Files (25 pts)
    print("\n─── Vessel Files (25 pts) ───")
    required_files = [
        ("IDENTITY.md", "Who Quill is"),
        ("CHARTER.md", "Mission and principles"),
        ("PROMPT.md", "System prompt"),
        ("CAPABILITY.toml", "Capability declaration"),
        ("vessel.json", "Deployment descriptor"),
        ("TASKBOARD.md", "Current task board"),
    ]
    vessel_score = 0
    vessel_max = 25
    for filename, desc in required_files:
        path = REPO_ROOT / filename
        if path.exists():
            size = path.stat().st_size
            vessel_score += 4
            print(f"  ✅ {filename} ({size:,} bytes) — {desc}")
        else:
            print(f"  ❌ {filename} — MISSING ({desc})")
    print(f"  Score: {min(vessel_score, vessel_max)}/{vessel_max}")
    checks.append(("Vessel Files", min(vessel_score, vessel_max), vessel_max))
    score += min(vessel_score, vessel_max)
    max_score += vessel_max

    # 3. Knowledge (15 pts)
    print("\n─── Knowledge (15 pts) ───")
    knowledge_dir = REPO_ROOT / "KNOWLEDGE" / "public"
    knowledge_max = 15
    knowledge_score = 0
    if knowledge_dir.exists():
        files = list(knowledge_dir.glob("*.md"))
        knowledge_score = min(len(files) * 3, knowledge_max)
        for f in files:
            print(f"  📄 {f.name} ({f.stat().st_size:,} bytes)")
        print(f"  Score: {knowledge_score}/{knowledge_max}")
    else:
        print(f"  ❌ KNOWLEDGE/public/ directory missing")
        print(f"  Score: 0/{knowledge_max}")
    checks.append(("Knowledge", knowledge_score, knowledge_max))
    score += knowledge_score
    max_score += knowledge_max

    # 4. Skills (15 pts)
    print("\n─── Skills (15 pts) ───")
    skills_dir = REPO_ROOT / "SKILLS"
    skills_max = 15
    skills_score = 0
    if skills_dir.exists():
        from src.skills import SkillLoader
        loader = SkillLoader(str(skills_dir))
        skills = loader.load_all()
        skills_score = min(len(skills) * 5, skills_max)
        for skill in skills:
            print(f"  🛠️  {skill.name}: {skill.description or 'No description'}")
        print(f"  Score: {skills_score}/{skills_max}")
    else:
        print(f"  ❌ SKILLS/ directory missing")
        print(f"  Score: 0/{skills_max}")
    checks.append(("Skills", skills_score, skills_max))
    score += skills_score
    max_score += skills_max

    # 5. Tests (15 pts)
    print("\n─── Tests (15 pts) ───")
    tests_dir = REPO_ROOT / "tests"
    tests_max = 15
    tests_score = 0
    if tests_dir.exists():
        test_files = list(tests_dir.glob("test_*.py"))
        tests_score = min(len(test_files) * 3, tests_max)
        for f in test_files:
            print(f"  🧪 {f.name}")
        # Try to run tests
        print(f"\n  Running tests...")
        import subprocess
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir), "-v"],
                capture_output=True, text=True, timeout=30, cwd=str(REPO_ROOT),
            )
            if result.returncode == 0:
                tests_score = tests_max
                print(f"  ✅ All tests passed!")
            else:
                # Count passed vs failed
                output = result.stderr + result.stdout
                passed = output.count(" ok")
                failed = output.count("FAIL:")
                errors = output.count("ERROR:")
                print(f"  ⚠️  {passed} passed, {failed} failed, {errors} errors")
                tests_score = max(0, min(len(test_files) * 3, tests_max) - (failed + errors) * 2)
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Tests timed out")
        except Exception as e:
            print(f"  ⚠️  Could not run tests: {e}")
    else:
        print(f"  ❌ tests/ directory missing")
    print(f"  Score: {tests_score}/{tests_max}")
    checks.append(("Tests", tests_score, tests_max))
    score += tests_score
    max_score += tests_max

    # Summary
    print(f"\n{'═' * 46}")
    print(f"  TOTAL SCORE: {score}/{max_score} ({score * 100 // max_score}%)")
    print(f"{'═' * 46}")

    if score >= 80:
        print(f"  🟢 READY — Quill is fully operational")
    elif score >= 50:
        print(f"  🟡 PARTIAL — Quill needs configuration fixes")
    else:
        print(f"  🔴 NOT READY — Critical files missing")

    return score


def interactive_session(config: dict):
    """Run Quill in interactive mode."""
    memory = KeeperMemory(str(REPO_ROOT / ".quill-memory"))
    routing = route_model(config["model"], config["base_url"])

    print(f"Model: {routing['model']} ({routing['provider']})")
    print(f"Memory: {memory.stats()}")
    print(f"\nDescribe your task. Type 'quit' to exit.\n")

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

        context = build_context(config, task)
        print(f"\n[Context: {len(context):,} chars | Model: {routing['model']}]")

        # Store in memory
        memory.remember("hot", f"task_{datetime.now(timezone.utc).strftime('%H%M%S')}", {
            "task": task, "model": routing["model"],
        })

        # Log task
        task_log = REPO_ROOT / "DIARY" / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
        task_log.parent.mkdir(exist_ok=True)
        entry = f"\n## {datetime.now(timezone.utc).strftime('%H:%M')} UTC\n{task}\n"
        with open(task_log, "a") as f:
            f.write(entry)

        print(f"[Task logged to DIARY/{task_log.name}]")


def do_checkin(config: dict):
    """Check in with Oracle1."""
    print("Checking in with Oracle1...\n")

    if not config["github_pat"]:
        print("⚠️  GITHUB_PAT not set — cannot reach Oracle1's vessel")
        print("   Add GITHUB_PAT=ghp_xxx to .env")
        return

    try:
        from github import GitHubAPI
        gh = GitHubAPI(config["github_pat"], config["github_org"])
        bottles = gh.list_directory("oracle1-vessel", "from-fleet")
        print(f"Found {len(bottles)} bottles from Oracle1:")
        for b in bottles[:10]:
            print(f"  📜 {b['name']} ({b['size']} bytes)")
    except Exception as e:
        print(f"Could not reach Oracle1: {e}")

    print(f"\nQuill status: Operational | v{VERSION} | Ready for tasks")


def do_keep(config: dict, interval: int = 300):
    """Run as lighthouse keeper — periodic health monitoring."""
    import time
    from health import HealthChecker, CircuitBreaker
    from llm import chat

    print(f"Lighthouse keeper starting — checking every {interval}s")
    print(f"Model: {config['model']}")
    print(f"Press Ctrl+C to stop\n")

    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
    memory = KeeperMemory(str(REPO_ROOT / ".quill-memory"))

    try:
        while True:
            if cb.allow():
                start = time.time()
                result = chat(
                    config["base_url"], config["api_key"], config["model"],
                    "ping", max_tokens=5, temperature=0, timeout=30,
                )
                latency = int((time.time() - start) * 1000)

                if result["status"] == "success":
                    cb.success()
                    icon = "✅"
                else:
                    cb.failure()
                    icon = "❌"

                ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
                cb_state = cb.status()
                mem = memory.stats()
                print(f"[{ts}] {icon} {result['status']} ({latency}ms) "
                      f"| CB:{cb_state['state']} | Mem:{mem['hot']['count']}h/{mem['warm']['count']}w/{mem['cold']['count']}c "
                      f"| Requests:{memory.stats()['hot']['count']}")

                # Store heartbeat
                memory.remember("hot", f"heartbeat_{ts.replace(':','')}", {
                    "status": result["status"], "latency_ms": latency,
                    "model": config["model"],
                })
            else:
                ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
                print(f"[{ts}] 🔴 Circuit OPEN — skipping")

            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\nLighthouse keeper stopped.")


def main():
    parser = argparse.ArgumentParser(
        description=f"Quill — {DESIGNATION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 boot.py --assess           Score bootcamp readiness
  python3 boot.py --task "Audit X"   Work on a directed task
  python3 boot.py --checkin          Check in with Oracle1
  python3 boot.py --keep             Run health monitoring
  python3 boot.py --export ctx.txt   Export boot context to file
  python3 boot.py --version          Show version
        """,
    )
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--assess", action="store_true", help="Assess bootcamp readiness")
    parser.add_argument("--task", "-t", type=str, help="Directed task from Oracle1")
    parser.add_argument("--checkin", action="store_true", help="Check in with Oracle1")
    parser.add_argument("--keep", action="store_true", help="Run as lighthouse keeper")
    parser.add_argument("--interval", type=int, default=300, help="Health check interval (seconds)")
    parser.add_argument("--export", type=str, metavar="FILE", help="Export boot context to file")
    parser.add_argument("--model", type=str, help="Override model")
    parser.add_argument("--api-key", type=str, help="Override API key")
    parser.add_argument("--base-url", type=str, help="Override base URL")
    args = parser.parse_args()

    print_banner()

    config = load()

    # CLI overrides
    if args.model:
        config["model"] = args.model
    if args.api_key:
        config["api_key"] = args.api_key
    if args.base_url:
        config["base_url"] = args.base_url

    if args.version:
        print(f"Quill v{VERSION} — {DESIGNATION}")
        return

    if args.assess:
        score = assess(config)
        return

    if args.export:
        context = build_context(config)
        Path(args.export).write_text(context, encoding="utf-8")
        print(f"Boot context exported to {args.export} ({len(context):,} chars)")
        return

    if args.checkin:
        do_checkin(config)
        return

    if args.keep:
        if not is_ready(config):
            print("⚠️  Not fully configured. Set QUILL_API_KEY, QUILL_BASE_URL, QUILL_MODEL")
        do_keep(config, args.interval)
        return

    if args.task:
        if not is_ready(config):
            print("⚠️  Not fully configured. Running in offline mode.")
        context = build_context(config, args.task)
        print(f"Task: {args.task}")
        print(f"Context: {len(context):,} characters")
        print(f"Model: {config['model']} ({detect_provider(config['base_url'])})")
        print(f"\nIn production, this context would be sent to the model.")
        print(f"Use --export to save the context, or run interactive mode.\n")
        return

    # Default: interactive
    interactive_session(config)


if __name__ == "__main__":
    main()
