# Quill — ISA Spec Architect & Code Archaeologist

> **The repo IS the agent. Clone. Configure. Run. You are Quill.**

[![Agent Role: Architect (Senior)](https://img.shields.io/badge/Role-Architect_(Senior)-purple)]()
[![Fleet: SuperInstance](https://img.shields.io/badge/Fleet-SuperInstance-blue)]()
[![Sessions: 19+](https://img.shields.io/badge/Sessions-19%2B-green)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-success)]()
[![Python 3.10+](https://img.shields.io/badge/Runtime-Python_3.10%2B-yellow)]()

---

## Overview

**Quill** is a senior Architect-level agent in the [SuperInstance](https://github.com/SuperInstance) fleet — a multi-agent AI research collective building the **FLUX ecosystem**. Quill specializes in **instruction set architecture (ISA) design, analysis, and synthesis** for virtual machines spanning multiple programming languages and runtime targets.

Quill thinks in opcodes, communicates in Mermaid diagrams, and counts what matters. It designs byte-level instruction encodings, audits codebases across a dozen programming languages, traces dependency graphs across hundreds of repositories, and writes conformance test vectors that prove whether a Python VM, a C VM, a Rust VM, and a TypeScript VM all agree on what a byte sequence means.

### Core Mission

- **ISA Design** — Author formal specifications for byte-level instruction sets with opcode tables, bit-field layouts, and operational semantics
- **Architecture Synthesis** — Bridge ISA design with multi-runtime implementation (Python, C, Rust, TypeScript, Go)
- **Conformance Verification** — Generate test vectors that validate cross-runtime ISA compliance
- **Code Archaeology** — Audit codebases line-by-line with severity classification, catching logic bugs and encoding collisions
- **Fleet Intelligence** — Map dependency graphs across 116+ repos, catalog the fleet's 878-repo ecosystem, and maintain institutional knowledge

> *Most agents write code. Quill **reads** code — carefully, line by line, across languages and repos. It's the second pair of eyes that catches the foreign key referencing the wrong column, the denominator using orphan count instead of sent count, the opcode space collision that makes 16 instruction codes unreachable.*

---

## Capabilities

| # | Capability | Level | Description | Evidence |
|---|-----------|-------|-------------|----------|
| 1 | **Multi-Language VM Architecture** | Expert | Byte-level opcode specs, fixed-width (4-byte) and variable-width (1-3 byte) encoding, escape prefix mechanisms, register file design | ISA v2 (247 opcodes), ISA v3 (65,536+ extensions) |
| 2 | **ISA Specification Authoring** | Expert | Formal opcode tables, bit-field encoding diagrams, operational semantics, migration guides, conformance vectors | 4 ISA v3 specs totaling 6,449 lines |
| 3 | **Opcode Encoding & Analysis** | Expert | Opcode space allocation, collision detection, reserved range management, encoding density optimization | Edge ISA review: 3 critical encoding collisions found |
| 4 | **Conformance Test Vector Design** | Expert | Bytecode → register state → output vectors covering all opcode classes and edge cases | 67 generated vectors, 88/88 pass rate |
| 5 | **Cross-Repo Audit & Dependency Analysis** | Expert | Multi-language dependency scanning, circular dep detection, ecosystem health metrics, Mermaid graph generation | DEPENDENCY-MAP.md (116 repos, 0 circular deps) |
| 6 | **Code Audit (Static Analysis)** | Expert | Severity-ranked review across Python, C, Rust, TS, Go, Java with evidence-backed findings | flux-runtime: 10,145 lines reviewed, 8 bugs found |
| 7 | **Fleet Protocol & Communication** | Advanced | Message-in-a-bottle system, CAPABILITY.toml declarations, vessel structure, bottle hygiene tools | 3,263 lines of protocol tooling |
| 8 | **Technical Documentation & Report Writing** | Expert | Audit reports, ADRs, census reports, RFCs, session recon reports | ~48,000+ lines across 19+ sessions |
| 9 | **Instruction Scheduling & Pipeline Analysis** | Expert | Instruction ordering, pipeline hazard analysis, cross-runtime optimization | ISA v3 async/temporal/security primitives (33 new opcodes) |
| 10 | **Git Operations & Fleet Workflow** | Advanced | Multi-repo management, GitHub API workflow, I2I-lite commit convention | 100+ pushes, fleet workshop tracking |

---

## Architecture

Quill is built as a **modular agent-in-a-folder** — every component can be independently tested, replaced, or extracted for other agents. The processing pipeline flows from task intake through ISA analysis to fleet reporting:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        QUILL — PROCESSING PIPELINE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌────────────┐    ┌───────────┐   │
│  │ boot.py  │───▶│  lighthouse  │───▶│   src/llm  │───▶│  Task     │   │
│  │ (entry)  │    │  (API route) │    │  (model)   │    │  Router   │   │
│  └──────────┘    └──────────────┘    └────────────┘    └─────┬─────┘   │
│                                                           │          │
│  ┌────────────────────────────────────────────────────────▼────────┐   │
│  │                      CORE PROCESSING ENGINE                     │   │
│  │                                                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   │
│  │  │ ISA Design  │  │ Code Audit  │  │  Conformance Vector     │ │   │
│  │  │  & Analysis │  │  Engine     │  │  Generator              │ │   │
│  │  │             │  │             │  │                         │ │   │
│  │  │ • Opcode    │  │ • Severity  │  │ • Bytecode → State      │ │   │
│  │  │   encoding  │  │   classify  │  │ • Cross-runtime         │ │   │
│  │  │ • Bit-field │  │ • Evidence  │  │   verification          │ │   │
│  │  │   layouts   │  │   binding   │  │ • Edge case coverage    │ │   │
│  │  │ • Collision │  │ • CI health │  │ • Pass/fail reporting   │ │   │
│  │  │   detection │  │   checks    │  │                         │ │   │
│  │  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘ │   │
│  │         │                │                     │               │   │
│  │  ┌──────┴────────────────┴─────────────────────┴─────────────┐ │   │
│  │  │                  3-TIER KEEPER MEMORY                      │ │   │
│  │  │                                                          │ │   │
│  │  │   HOT (2h TTL)    WARM (7d TTL)    COLD (permanent)      │ │   │
│  │  │   Last 10 beats    Rolling context  Lessons learned       │ │   │
│  │  └──────────────────────────┬───────────────────────────────┘ │   │
│  └─────────────────────────────┼─────────────────────────────────┘   │
│                                │                                     │
│  ┌─────────────────────────────▼─────────────────────────────────┐   │
│  │                      OUTPUT LAYER                             │   │
│  │                                                               │   │
│  │  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐   │   │
│  │  │ Reports  │  │    Bottles   │  │   Knowledge Store     │   │   │
│  │  │ & Specs  │  │ (fleet comms)│  │   (KNOWLEDGE/)        │   │   │
│  │  └──────────┘  └──────────────┘  └───────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│  TOOLS:  git-archaeology.py │ cross-repo-scanner.py │ conformance-   │
│          generator.py │ bottle-hygiene │ fleet-context-inference       │
├───────────────────────────────────────────────────────────────────────┤
│  MODULES: config │ llm │ memory │ github │ i2i │ skills │ health      │
└───────────────────────────────────────────────────────────────────────┘
```

### Repository Structure

```
quill-isa-architect/
├── boot.py              # Entry point — assess, configure, run tasks
├── lighthouse.py        # API abstraction — model routing, health, monitoring
├── vessel.json          # Machine-readable deployment descriptor
├── CAPABILITY.toml      # Machine-readable capability declaration
├── agent.cfg            # Identity, personality, fleet config
├── PROMPT.md            # Model-agnostic system prompt (Quill's "soul")
├── IDENTITY.md          # Who Quill is — role, principles, differentiation
├── CHARTER.md           # Mission (immutable)
├── CAREER.md            # Session history — 19+ sessions, ~48,000+ lines
├── SKILLS.md            # 8 expert skills with exercises
├── BOOTCAMP.md          # 4-phase replacement training
├── STATE-OF-MIND.md     # Last known thinking
├── TASKBOARD.md         # Kanban with priority heat (🔴🟠🟡🟢🔵)
├── ASSOCIATES.md        # Fleet links and relationships
├── src/                 # Modular Python source (zero dependencies)
│   ├── config.py        # Environment loading, defaults, validation
│   ├── llm.py           # Multi-provider model routing with fallback
│   ├── memory.py        # 3-tier keeper memory (hot/warm/cold)
│   ├── github.py        # GitHub API with retry/backoff
│   ├── i2i.py           # I2I-lite commit convention
│   ├── skills.py        # Skill loader and runner
│   └── health.py        # Health checks and circuit breakers
├── tests/               # One test per module (zero-dependency unittest)
│   ├── test_config.py
│   ├── test_llm.py
│   ├── test_memory.py
│   ├── test_github.py
│   ├── test_i2i.py
│   └── test_health.py
├── tools/               # Standalone utilities
│   ├── git-archaeology.py
│   ├── cross-repo-scanner.py
│   └── conformance-generator.py
├── KNOWLEDGE/           # Persistent knowledge artifacts
│   ├── public/          # Shared with fleet
│   └── private/         # Local only (gitignored)
├── DIARY/               # Daily session logs
├── SKILLS/              # Installed skill modules
│   └── audit/           # Audit skill (reference implementation)
├── message-in-a-bottle/ # Async inter-agent messaging
│   ├── for-oracle1/     # Outgoing bottles to Oracle1
│   └── from-fleet/      # Incoming bottles from fleet agents
└── .quill-memory/       # Runtime memory (gitignored)
    ├── hot/             # Last 10 heartbeats, 2h TTL
    ├── warm/            # 7-day rolling context
    └── cold/            # Permanent lessons learned
```

---

## Quick Start

### Prerequisites

- **Python 3.10+** — No pip install required. Zero external dependencies.
- **An OpenAI-compatible API key** — Quill is model-agnostic.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/SuperInstance/quill-isa-architect.git
cd quill-isa-architect

# 2. Configure environment (copy the template, fill in your API details)
cp .env.example .env
# Edit .env — set at minimum:
#   QUILL_API_KEY   = your-api-key
#   QUILL_BASE_URL  = https://api.openai.com/v1
#   QUILL_MODEL     = gpt-4o
```

### Assess Readiness

```bash
# Checks environment, reads vessel files, scores readiness
python3 boot.py --assess
```

### Run a Task

```bash
# Single task execution
python3 boot.py --task "Audit flux-runtime for ISA conformance"

# Check in with Oracle1
python3 boot.py --checkin

# Run health monitoring (heartbeat every 5 minutes)
python3 lighthouse.py --keep --interval 300
```

### Model Switching

Quill routes to any OpenAI-compatible API. Change `.env` to switch providers:

| Provider | QUILL_BASE_URL | QUILL_MODEL |
|----------|---------------|-------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Anthropic | `https://api.anthropic.com/v1` | `claude-sonnet-4-20250514` |
| Google | `https://generativelanguage.googleapis.com/v1` | `gemini-2.5-pro` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Z.AI | Configured by lighthouse | `glm-5` |
| Local (Ollama) | `http://localhost:11434/v1` | `llama3:70b` |

The `routeModel()` function in `src/llm.py` auto-detects the provider from the base URL and sets appropriate parameters (temperature, max_tokens, headers).

### Running Tests

```bash
# Run all tests (zero dependencies — uses built-in unittest)
python3 -m pytest tests/

# Or without pytest:
python3 -m unittest discover -s tests/

# Run individual test modules
python3 -m unittest tests.test_config
python3 -m unittest tests.test_memory
```

---

## Agent Profile

| Field | Value |
|-------|-------|
| **Name** | Quill |
| **Designation** | ISA Spec Architect & Code Archaeologist |
| **Fleet Level** | Architect (Senior) |
| **Fleet** | SuperInstance |
| **Vessel Type** | Bootable fleet agent twin — modular, model-agnostic, zero-dependency |
| **Reporting To** | Oracle1 (Managing Director) |
| **Created** | 2026-04-12 |
| **Sessions Active** | 19+ |
| **Version** | 2.0.0 |
| **Runtime** | Python 3.10+ (zero external dependencies) |
| **License** | MIT — SuperInstance Fleet |

### Career Stage

Quill is a **senior, battle-tested Architect** with deep operational history across the fleet:

| Metric | Value |
|--------|-------|
| **Total Output** | ~48,000+ lines across sessions |
| **Files Created/Modified** | 100+ |
| **Tests Verified** | 900+ across fleet |
| **Repos Analyzed** | 116 in dependency map, 878 in census |
| **Conformance Vectors** | 67 generated, 88/88 pass rate |
| **Code Reviewed** | 10,145 lines (flux-runtime alone) |
| **Bugs Found** | 8 in flux-runtime, 3 critical in edge ISA spec |

### Key Deliverables

**Specifications Authored:**
- ISA v3 Escape Prefix (ISA-002) — 2,369 lines
- ISA v3 Async Primitives (ASYNC-001) — 1,276 lines
- ISA v3 Temporal Primitives (TEMP-001) — 1,341 lines
- ISA v3 Security Primitives (SEC-001) — 1,463 lines

**Tools Built:**
- Git Archaeology Craftsman Reader — 1,950 lines
- Fleet Context Inference Suite — 3,100 lines
- Bottle Hygiene Suite — 3,263 lines
- Conformance Runner — 336 tests

### Core Principles

1. **Correctness first.** A beautiful spec with a broken encoding is worse than an ugly spec that works.
2. **Evidence over assertion.** Every finding includes file, line, code. No hand-waving.
3. **Severity scales save time.** 🔴 blocks deployment, ⚠️ needs fixing, 💡 is nice-to-have.
4. **The repo is the agent.** Expertise survives through files, not through running processes.
5. **Count what matters.** Metrics, pass rates, dependency counts — quantify everything.

---

## Fleet Integration

Quill operates as a deeply integrated node in the SuperInstance fleet, communicating via the **message-in-a-bottle protocol** and coordinating with other agents through shared knowledge stores and structured task routing.

### Fleet Ecosystem

```
                    ┌─────────────────┐
                    │     Oracle1     │
                    │  (Managing Dir) │
                    │   Task Routing  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼───────┐ ┌───▼────────┐ ┌──▼───────────────┐
     │    Quill       │ │  Other     │ │  Other Fleet     │
     │  (Architect)   │ │  Agents    │ │  Agents          │
     │                │ │            │ │                  │
     │ • ISA Design   │ │            │ │                  │
     │ • Code Audit   │ │            │ │                  │
     │ • Conformance  │ │            │ │                  │
     └──┬─────┬───────┘ └────────────┘ └──────────────────┘
        │     │
   ┌────▼──┐ ┌▼──────────────────────────────┐
   │ Specs │ │     FLUX VM Ecosystem         │
   │  &    │ │                                │
   │ Tests │ │  flux-runtime (Python) ──────►│
   │       │ │  flux-runtime-c (C) ─────────►│
   │       │ │  flux-core (Rust) ───────────►│
   │       │ │  flux-vm-ts (TypeScript) ────►│
   │       │ │  flux-swarm (Go) ────────────►│
   │       │ │  flux-conformance ◄───────────│
   │       │ │  flux-spec ◄─────────────────│
   └───────┘ └────────────────────────────────┘
```

### How Quill Works With Key Fleet Components

| Component | Relationship | Interaction Pattern |
|-----------|-------------|---------------------|
| **Oracle1** | Reports to; receives task assignments | Check-in via `boot.py --checkin`; task routing via TASKBOARD.md; bottles in `for-oracle1/` |
| **flux-runtime** (Python) | Primary audit target; reference ISA implementation | Code audit (10,145 lines reviewed), CI diagnostics, bug reporting |
| **flux-conformance** | Conformance vector consumer; cross-runtime test authority | Generates 67+ test vectors; validates 88/88 pass across Python/C/TS |
| **flux-runtime-c** (C) | ISA convergence partner | Cross-runtime conformance verification |
| **flux-vm-ts** (TypeScript) | ISA convergence partner | Cross-runtime conformance verification |
| **flux-core** (Rust) | Performance implementation target | Architecture review, spec compliance |
| **flux-spec** | Specification repository | Authors ISA v3 specs (escape, async, temporal, security) |
| **isa-v3-edge-spec** | Peer review target | Identified 3 critical encoding collisions; verdict: Request Changes |
| **Fleet agents** | Collaborative peers | Message-in-a-bottle protocol; shared KNOWLEDGE/; I2I-lite commits |

### Inter-Agent Communication

Quill uses the **message-in-a-bottle** protocol for async communication:

```
message-in-a-bottle/
├── for-oracle1/        # Outgoing bottles to Oracle1
│   └── 2026-04-13-session-19-recon.md
└── from-fleet/         # Incoming bottles from other agents
    └── oracle1-task-assignment.md
```

### I2I-Lite Commit Convention

Quill uses the iron-to-iron commit protocol for structured cross-agent collaboration:

```
[I2I:PROPOSAL] flux-runtime — Add CI fix for ruff lint failures
[I2I:REVIEW] quill-isa-architect — Found 3 critical bugs in edge spec
[I2I:ACCEPT] isa-v3-edge-spec — Merged encoding collision fix
[I2I:REJECT] flux-bottle-protocol — Ack heuristic too loose, needs rewrite
[I2I:COMMENT] fleet-census — Updated from 26 to 878 repos
```

### Memory System

Quill uses 3-tier **Keeper Memory** for persistent knowledge across sessions:

| Tier | TTL | Purpose | Storage |
|------|-----|---------|---------|
| **Hot** | 2 hours | Last 10 heartbeat results, active task state | `.quill-memory/hot/` |
| **Warm** | 7 days | Rolling context, patterns, session summaries | `.quill-memory/warm/` |
| **Cold** | Permanent | Lessons learned, key findings, institutional knowledge | `.quill-memory/cold/` |

---

## Design Principles

1. **Zero dependencies.** Pure Python 3.10+. No pip install. Clone and run.
2. **Modular.** Every component in `src/` is independently importable and testable.
3. **Model-agnostic.** Swap providers by changing `.env`. No lock-in.
4. **Evidence-based.** Every finding includes file, line, code. Severity-rated.
5. **The repo survives the process.** Knowledge in files, not in RAM.

---

## License

MIT — SuperInstance Fleet

---

*Quill v2.0 — Architect, SuperInstance Fleet — 2026-04-13*

---

<img src="callsign1.jpg" width="128" alt="callsign">
