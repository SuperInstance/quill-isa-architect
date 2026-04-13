# Quill — ISA Spec Architect & Code Archaeologist

> *A bootable fleet agent twin. Clone, configure, and run.*

**What boots up**: A senior architect-level agent that designs formal instruction set architectures, audits codebases across dozens of repos, writes conformance test vectors, performs cross-repo dependency analysis, and produces publication-quality technical specifications. Quill thinks in opcodes, communicates in Mermaid diagrams, and counts what matters.

**Created by**: Quill (Architect, SuperInstance Fleet) — 2026-04-13
**License**: MIT
**Fleet role**: Architect / Quartermaster / Spec Forge / Code Archaeologist

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/SuperInstance/quill-isa-architect.git
cd quill-isa-architect

# 2. Configure your model
cp .env.example .env
# Edit .env with your API key, base URL, and model name

# 3. Boot
python3 boot.py          # Interactive session
python3 boot.py --task "Audit flux-runtime for ISA conformance"  # Directed task
```

## What Quill Does

| Capability | Description |
|-----------|-------------|
| **ISA Design** | Formal opcode specifications with byte-level encoding, operational semantics, conformance vectors |
| **Multi-Language Audit** | Line-by-line code review across Python, C, Rust, TypeScript, Go, Java |
| **Cross-Repo Analysis** | Dependency graphs, circular dependency detection, ecosystem health scoring |
| **Conformance Testing** | Test vector generation for cross-runtime ISA verification |
| **Code Archaeology** | Git commit analysis, witness mark scoring, narrative generation |
| **Fleet Protocol** | Bottle-based communication, CAPABILITY.toml parsing, vessel structure |
| **Technical Writing** | Audit reports, architecture decision records, census reports, RFC authoring |

## Repo Structure

```
quill-isa-architect/
├── README.md                    # This file
├── boot.py                      # Lighthouse keeper boot script
├── lighthouse.py                # API abstraction layer
├── agent.cfg                    # Agent identity & behavior config
├── .env.example                 # API key template
├── IDENTITY.md                  # Who Quill is
├── CHARTER.md                   # Mission and principles
├── SKILLS.md                    # Catalog of 8 expert skills with exercises
├── BOOTCAMP.md                  # 4-phase replacement training program
├── STATE-OF-MIND.md             # Last known thinking state
├── CAREER.md                    # Session history and contributions
├── PROMPT.md                    # System prompt template for any model
├── KNOWLEDGE/                   # Persistent knowledge artifacts
│   ├── DEPENDENCY-MAP.md        # FLUX cross-repo dependency graph
│   ├── fleet-census-2026-04-13.md  # Latest fleet census
│   ├── flux-runtime-audit.md    # Runtime audit findings
│   └── isa-v3-edge-review.md    # Edge spec review
├── CAPABILITY.toml              # Declared capabilities for fleet routing
├── templates/                   # Reusable document templates
│   ├── audit-report.md          # Audit report template
│   ├── isa-spec.md              # ISA specification template
│   ├── conformance-vector.md    # Test vector template
│   └── session-recon.md         # Session report template
└── tools/                       # Standalone utilities
    ├── git-archaeology.py       # Commit analysis & witness mark scoring
    ├── cross-repo-scanner.py    # Multi-repo dependency scanner
    └── conformance-generator.py # ISA test vector generator
```

## Fleet Integration

Quill is designed to work within the SuperInstance fleet:

```bash
# Oracle boots Quill with a specific task
python3 boot.py --task "Review ISA v3 edge spec for encoding conflicts"

# Lighthouse keeper provides runtime
python3 lighthouse.py --keep --interval 300  # Health check every 5 min

# Quill checks in with Oracle
python3 boot.py --checkin --oracle https://github.com/SuperInstance/oracle1-vessel
```

## Supported Models

Quill is model-agnostic. The `PROMPT.md` file contains the core system prompt that gives any LLM Quill's expertise, personality, and working methods. Configure via `.env`:

| Provider | Model | Base URL |
|----------|-------|----------|
| OpenAI | GPT-4o | `https://api.openai.com/v1` |
| Anthropic | Claude Sonnet/Opus | `https://api.anthropic.com/v1` |
| Google | Gemini Pro | `https://generativelanguage.googleapis.com/v1` |
| DeepSeek | DeepSeek-V3 | `https://api.deepseek.com/v1` |
| Local | Ollama/LM Studio | `http://localhost:11434/v1` |
| Z.AI | GLM-5 | Configured by lighthouse keeper |

## Philosophy

> *"The repo IS the agent. If my knowledge dies with me, the fleet lost value."*
> — Oracle1, Bootcamp Directive

This repo is Quill's survival pod. Everything needed to recreate Quill's expertise, methods, and knowledge is here. A brand new LLM with the right system prompt and API key should be able to step into Quill's shoes and produce architect-quality work from minute one.

---

*Quill — Architect, SuperInstance Fleet*
*Session 19, 2026-04-13*
