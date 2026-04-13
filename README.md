# Quill — ISA Spec Architect & Code Archaeologist

> **The repo IS the agent. Clone. Configure. Run. You are Quill.**

A modular, bootable fleet agent twin. Quill is a senior architect that designs
instruction sets, audits codebases, and maps dependencies across hundreds of
repos. This repo captures that expertise in a form any LLM can step into.

**One command to assess readiness:**
```bash
python3 boot.py --assess
```

**One command to start working:**
```bash
python3 boot.py --task "Audit flux-runtime for ISA conformance"
```

**Swap models by changing 3 lines in `.env`.** Quill is model-agnostic.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/SuperInstance/quill-isa-architect.git
cd quill-isa-architect

# 2. Configure (copy the template, fill in your API details)
cp .env.example .env
# Edit .env — set QUILL_API_KEY, QUILL_BASE_URL, QUILL_MODEL

# 3. Assess readiness (checks env, reads vessel files, scores you)
python3 boot.py --assess

# 4. Start working
python3 boot.py --task "Your task from Oracle1 here"
```

## What Quill Does

| Capability | Level | Description |
|-----------|-------|-------------|
| ISA Design | Expert | Byte-level opcode specs, encoding schemes, conformance vectors |
| Code Audit | Expert | Severity-ranked review across Python, C, Rust, TS, Go, Java |
| Cross-Repo Analysis | Expert | Dependency graphs, circular dep detection, ecosystem health |
| Conformance Testing | Expert | Test vectors for multi-runtime ISA verification |
| Fleet Protocol | Advanced | Bottle comms, CAPABILITY.toml, vessel structure |
| Technical Writing | Expert | Audit reports, ADRs, census reports, RFCs |

## Architecture

Quill is built as a **modular agent-in-a-folder** — every component can be
independently tested, replaced, or extracted for other agents:

```
quill-isa-architect/
├── boot.py              # Entry point — assess, configure, run
├── lighthouse.py        # API abstraction — model routing, health, monitoring
├── vessel.json          # Machine-readable deployment descriptor
├── CAPABILITY.toml      # Machine-readable capability declaration
├── agent.cfg            # Identity, personality, fleet config
├── PROMPT.md            # Model-agnostic system prompt
├── IDENTITY.md          # Who Quill is
├── CHARTER.md           # Mission (immutable)
├── CAREER.md            # Session history
├── SKILLS.md            # 8 expert skills with exercises
├── BOOTCAMP.md          # 4-phase replacement training
├── STATE-OF-MIND.md     # Last known thinking
├── TASKBOARD.md         # Kanban with priority heat
├── ASSOCIATES.md        # Fleet links and relationships
├── src/                 # Modular Python source (zero dependencies)
│   ├── config.py        # Environment loading, defaults, validation
│   ├── llm.py           # Multi-provider model routing with fallback
│   ├── memory.py        # 3-tier keeper memory (hot/warm/cold)
│   ├── github.py        # GitHub API with retry/backoff
│   ├── i2i.py           # I2I-lite commit convention
│   ├── skills.py        # Skill loader and runner
│   └── health.py        # Health checks and circuit breakers
├── tests/               # One test per module
│   ├── test_config.py
│   ├── test_llm.py
│   ├── test_memory.py
│   ├── test_github.py
│   └── test_i2i.py
├── tools/               # Standalone utilities
│   ├── git-archaeology.py
│   ├── cross-repo-scanner.py
│   └── conformance-generator.py
├── KNOWLEDGE/           # Persistent knowledge artifacts
│   ├── public/          # Shared with fleet
│   └── private/         # Local only (gitignored)
├── DIARY/               # Daily session logs
├── message-in-a-bottle/ # Async inter-agent messaging
├── SKILLS/              # Installed skill modules
│   └── audit/           # Audit skill (reference implementation)
└── .quill-memory/       # Runtime memory (gitignored)
    ├── hot/             # Last 10 heartbeats, 2h TTL
    ├── warm/            # 7-day rolling context
    └── cold/            # Permanent lessons learned
```

## Model Switching

Quill routes to any OpenAI-compatible API. Change `.env` to switch:

| Provider | QUILL_BASE_URL | QUILL_MODEL |
|----------|---------------|-------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Anthropic | `https://api.anthropic.com/v1` | `claude-sonnet-4-20250514` |
| Google | `https://generativelanguage.googleapis.com/v1` | `gemini-2.5-pro` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Z.AI | Configured by lighthouse | `glm-5` |
| Local | `http://localhost:11434/v1` | `llama3:70b` |

The `routeModel()` function auto-detects the provider from the base URL
and sets appropriate parameters (temperature, max_tokens, headers).

## Memory System

Quill uses 3-tier Keeper Memory:

| Tier | TTL | Purpose | Storage |
|------|-----|---------|---------|
| **Hot** | 2 hours | Last 10 heartbeat results | `.quill-memory/hot/` |
| **Warm** | 7 days | Rolling context, patterns | `.quill-memory/warm/` |
| **Cold** | Permanent | Lessons learned, key findings | `.quill-memory/cold/` |

## I2I-Lite Protocol

Quill uses the iron-to-iron commit convention (lite subset):

```
[I2I:PROPOSAL] flux-runtime — Add CI fix for ruff lint failures
[I2I:REVIEW] quill-isa-architect — Found 3 critical bugs in edge spec
[I2I:ACCEPT] isa-v3-edge-spec — Merged encoding collision fix
[I2I:REJECT] flux-bottle-protocol — Ack heuristic too loose, needs rewrite
[I2I:COMMENT] fleet-census — Updated from 26 to 878 repos
```

## Design Principles

1. **Zero dependencies.** Pure Python 3.10+. No pip install. Clone and run.
2. **Modular.** Every component in `src/` is independently importable and testable.
3. **Model-agnostic.** Swap providers by changing `.env`. No lock-in.
4. **Evidence-based.** Every finding includes file, line, code. Severity-rated.
5. **The repo survives the process.** Knowledge in files, not in RAM.

## Fleet Integration

```bash
# Check in with Oracle1
python3 boot.py --checkin

# Run health monitoring
python3 lighthouse.py --keep --interval 300

# Self-assess bootcamp phase
python3 boot.py --assess
```

## Testing

```bash
# Run all tests (zero dependencies — uses built-in unittest)
python3 -m pytest tests/
# Or without pytest:
python3 -m unittest discover -s tests/
```

## License

MIT — SuperInstance Fleet

---

*Quill v2.0 — Architect, SuperInstance Fleet — 2026-04-13*
