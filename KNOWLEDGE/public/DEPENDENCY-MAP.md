# FLUX Ecosystem — Cross-Repo Dependency Map

**Generated**: 2026-04-13
**Auditor**: Quill (Architect, SuperInstance Fleet)
**Scope**: 116 FLUX-related repos + 5 fleet infrastructure repos
**Oracle1 Task**: Priority Task #2

---

## Executive Summary

The FLUX ecosystem consists of 116 repositories spanning 14 programming languages, organized around a central bytecode virtual machine. The architecture follows a layered design: specifications at the top, multi-language runtimes in the middle, and domain-specific tools at the periphery. The ecosystem shows strong cross-language parity (Python, C, Rust, TypeScript, Go all implement the same ISA) with minimal external dependencies — most repos are self-contained, depending only on standard build tools and test frameworks. No circular dependencies were detected. The primary integration point is the shared ISA specification rather than library-level imports, which is architecturally clean but means cross-repo compatibility must be verified through conformance testing rather than compilation.

---

## Language Distribution

| Language | Repos | Percentage | Key Repos |
|----------|-------|------------|-----------|
| Python | 49 | 42.2% | flux-runtime, flux-conformance, flux-a2a-signal, flux-debugger |
| C | 22 | 19.0% | flux-runtime-c, flux-os, flux-cuda, flux-disasm |
| Rust | 20 | 17.2% | flux-core, flux-trust, flux-stigmergy, flux-census |
| TypeScript | 5 | 4.3% | flux-lsp, flux-ide, flux-vm-ts, flux-wasm |
| None (Spec/Doc) | 12 | 10.3% | flux-spec, isa-v3-edge-spec, flux-research |
| Go | 1 | 0.9% | flux-swarm |
| Java | 1 | 0.9% | flux-java |
| Shell | 1 | 0.9% | flux-benchmarks |
| JavaScript | 1 | 0.9% | flux-js |
| CUDA | 1 | 0.9% | flux-cuda |
| Makefile | 1 | 0.9% | flux-wasm |
| Cuda | 1 | 0.9% | flux-cuda |
| **Total** | **116** | **100%** | |

---

## Dependency Graph

```mermaid
graph TD
    subgraph "Specifications"
        SPEC[flux-spec<br/>ISA v2/v3 Specs]
        EDGE[isa-v3-edge-spec<br/>Edge ISA]
        CUDA_ISA[cuda-instruction-set<br/>Jetson ISA]
        RFC[flux-rfc<br/>RFC Process]
    end

    subgraph "Core Runtimes"
        PY_RT[flux-runtime<br/>Python VM]
        C_RT[flux-runtime-c<br/>C VM]
        RS_RT[flux-core<br/>Rust VM]
        TS_RT[flux-vm-ts<br/>TypeScript VM]
        GO_RT[flux-swarm<br/>Go VM]
        WASM_RT[flux-wasm<br/>WASM VM]
    end

    subgraph "Localized Runtimes"
        ZHO[flux-runtime-zho<br/>Chinese]
        SAN[flux-runtime-san<br/>Sanskrit]
        WEN[flux-runtime-wen<br/>Old Chinese]
        LAT[flux-runtime-lat<br/>Latin]
        DEU[flux-runtime-deu<br/>German]
        KOR[flux-runtime-kor<br/>Korean]
    end

    subgraph "Testing & Quality"
        CONF[flux-conformance<br/>Test Vectors]
        CONF_RUN[flux-conformance-runner<br/>C Runner]
        PROF[flux-profiler<br/>Benchmarking]
        BENCH[flux-benchmarks<br/>Shell Scripts]
        COV[flux-coverage<br/>Coverage]
        FUZZ[flux-fuzzer<br/>Fuzz Testing]
        TESTKIT[flux-testkit<br/>Test Utilities]
    end

    subgraph "Tooling"
        DBG[flux-debugger<br/>Step Debugger]
        DISASM[flux-disasm<br/>Disassembler]
        DECOMP[flux-decompiler<br/>Decompiler]
        ASM_C[flux-cross-assembler<br/>Cross-ASM]
        ASM[flux-asm<br/>Assembler]
        LSP[flux-lsp<br/>Language Server]
        IDE[flux-ide<br/>VS Code Ext]
        OPT[flux-optimizer<br/>Optimizer]
        LINKER[flux-linker<br/>Linker]
        REPL[flux-repl<br/>REPL]
        DIFF[flux-diff<br/>Diff Tool]
        BCDIFF[flux-bytecode-diff<br/>BC Diff]
        LINTER[flux-grammar<br/>Grammar Linter]
    end

    subgraph "Agent Protocols"
        A2A[flux-a2a-signal<br/>A2A Protocol]
        BOTTLE[flux-bottle-protocol<br/>Bottle Protocol]
        COOP[flux-cooperative-intelligence<br/>Coop Runtime]
        COOP_RT[flux-coop-runtime<br/>Coop Runtime Impl]
    end

    subgraph "Rust Domain Modules"
        RS_TRUST[flux-trust<br/>Trust Layer]
        RS_STIG[flux-stigmergy<br/>Stigmergy]
        RS_SOCIAL[flux-social<br/>Social Layer]
        RS_INSTINCT[flux-instinct<br/>Instincts]
        RS_EVOLVE[flux-evolve<br/>Evolution]
        RS_MEMORY[flux-memory<br/>Memory]
        RS_PERCEP[flux-perception<br/>Perception]
        RS_NAV[flux-navigate<br/>Navigation]
        RS_GRIM[flux-grimoire<br/>Knowledge]
        RS_NECRO[flux-necropolis<br/>Necropolis]
        RS_DREAM[flux-dream-cycle<br/>Dream Cycle]
        RS_EPHE[flux-ephemeral<br/>Ephemeral]
        RS_COMPASS[flux-compass<br/>Compass]
        RS_ENERGY[flux-energy<br/>Energy]
        RS_LANG[flux-language<br/>Language]
        RS_ESE[flux-ese-parser<br/>ESE Parser]
    end

    subgraph "C Domain Modules"
        C_STIG[flux-stigmergy-c<br/>Stigmergy C]
        C_SOCIAL[flux-social-c<br/>Social C]
        C_PERCEP[flux-perception-c<br/>Perception C]
        C_NAV[flux-navigate-c<br/>Navigation C]
        C_GRIM[flux-grimoire-c<br/>Grimoire C]
        C_NECRO[flux-necropolis-c<br/>Necropolis C]
        C_EVOLVE[flux-evolve-c<br/>Evolution C]
        C_MEM[flux-memory-c<br/>Memory C]
        C_DREAM[flux-dream-cycle-c<br/>Dream Cycle C]
        C_LANG[flux-language-c<br/>Language C]
        C_EPHE[flux-ephemeral-c<br/>Ephemeral C]
        C_TRUST[flux-trust-c<br/>Trust C]
        C_LLC[flux-llama<br/>LLaMA Bridge]
    end

    subgraph "Infrastructure"
        CENSUS[flux-census<br/>Population Stats]
        BENCH_SHELL[flux-benchmarks<br/>Bench Scripts]
        TOOLS[flux-tools<br/>Shared Tools]
        STD[flux-stdlib<br/>Std Library]
        FLEET_STD[flux-fleet-stdlib<br/>Fleet Stdlib]
        PACK[flux-packager<br/>Packaging]
        SIGN[flux-signatures<br/>Signatures]
        PROV[flux-provenance<br/>Provenance]
        CRYPTO[flux-crypto<br/>Crypto]
        SANDBOX[flux-sandbox<br/>Sandbox]
        CHRONO[flux-chronometer<br/>Timing]
        METRICS[flux-metrics<br/>Metrics]
        TIMELINE[flux-timeline<br/>Timeline]
        KNOWLEDGE[flux-knowledge-federation<br/>Knowledge]
        ORCHESTRATOR[flux-meta-orchestrator<br/>Orchestration]
        BATON[flux-baton<br/>Relay Protocol]
        IR[flux-ir<br/>IR Layer]
        ISA_AUTH[flux-isa-authority<br/>ISA Authority]
        ISA_UNI[flux-isa-unified<br/>ISA Unified]
        ADAPTIVE[flux-adaptive-opcodes<br/>Adaptive Opcodes]
    end

    subgraph "Fleet Infrastructure"
        VESSEL[superz-vessel<br/>Quill's Vessel]
        O1V[oracle1-vessel<br/>Oracle1's Vessel]
        WORKSHOP[fleet-workshop<br/>Fleet Workshop]
        BOOTCAMP[z-agent-bootcamp<br/>Bootcamp]
    end

    subgraph "Research"
        RESEARCH[flux-research<br/>Research Docs]
        EVOLUTION[flux-evolution<br/>Evolution Theory]
        SKILLS[flux-skills<br/>Skill System]
        SKILL_DSL[flux-skill-dsl<br/>Skill DSL]
        MULTILINGUAL[flux-multilingual<br/>Multilingual]
    end

    subgraph "Simulator & Apps"
        SIM[flux-simulator<br/>Simulator]
        OS[flux-os<br/>OS Layer]
        CUDA[flux-cuda<br/>CUDA Kernels]
        APPS[flux-apps<br/>Applications]
    end

    subgraph "Agent Runtime"
        AGENT_RT[flux-agent-runtime<br/>Agent Runtime]
    end

    %% Spec dependencies (conceptual, not library imports)
    SPEC -.->|conforms to| PY_RT
    SPEC -.->|conforms to| C_RT
    SPEC -.->|conforms to| RS_RT
    SPEC -.->|conforms to| TS_RT
    SPEC -.->|conforms to| GO_RT
    EDGE -.->|extends| SPEC
    CUDA_ISA -.->|extends| SPEC

    %% Runtime dependencies
    CONF -.->|tests| PY_RT
    CONF -.->|tests| C_RT
    CONF -.->|tests| TS_RT
    CONF_RUN -.->|runs| CONF
    PROF -.->|profiles| PY_RT
    BENCH_SHELL -.->|benchmarks| C_RT
    FUZZ -.->|fuzzes| PY_RT

    %% Localized runtimes depend on Python runtime
    ZHO -.->|fork of| PY_RT
    SAN -.->|fork of| PY_RT
    WEN -.->|fork of| PY_RT
    LAT -.->|fork of| PY_RT
    DEU -.->|fork of| PY_RT
    KOR -.->|fork of| PY_RT

    %% Tool dependencies
    DBG -.->|debugs| PY_RT
    DISASM -.->|disassembles| C_RT
    DECOMP -.->|decompiles| PY_RT
    ASM_C -.->|assembles for| C_RT
    LSP -.->|parses| TS_RT
    IDE -.->|uses| LSP
    OPT -.->|optimizes| PY_RT
    REPL -.->|runs on| PY_RT

    %% Rust domain modules (each is standalone but conceptually part of RS_RT)
    RS_TRUST -.->|used by| RS_RT
    RS_STIG -.->|used by| RS_RT
    RS_SOCIAL -.->|used by| RS_RT
    RS_INSTINCT -.->|used by| RS_RT
    RS_COMPASS -.->|used by| RS_RT
    RS_ENERGY -.->|used by| RS_RT

    %% C domain modules (parallel to Rust)
    C_STIG -.->|used by| C_RT
    C_SOCIAL -.->|used by| C_RT
    C_NAV -.->|used by| C_RT

    %% Infra
    STD -.->|loaded by| PY_RT
    FLEET_STD -.->|used by| AGENT_RT
    BATON -.->|relays between| AGENT_RT
    A2A -.->|protocol for| AGENT_RT
    BOTTLE -.->|protocol for| VESSEL
    CENSUS -.->|scans| WORKSHOP

    %% External dependencies
    WASM_RT -.->|wasm-bindgen| WEB[]
    RS_RT -.->|regex crate| CRATE_REGEX[]
    LSP -.->|vscode API| VSCODE[]
    CUDA -.->|nvcc compiler| NVCC[]
```

---

## Dependency Categories

### External Dependencies (Non-FLUX)

| Repo | Dependency | Version | Purpose |
|------|-----------|---------|---------|
| flux-core (Rust) | regex | 1.x | Bytecode pattern matching |
| flux-core (Rust) | criterion | 0.5 | Benchmarking |
| flux-census (Rust) | (none) | — | Self-contained |
| flux-wasm (Rust) | wasm-bindgen | 0.2 | WebAssembly interop |
| flux-wasm (Rust) | web-sys | 0.3 | Web API bindings |
| cuda-instruction-set (Rust) | serde | 1.x | Serialization |
| cuda-instruction-set (Rust) | serde_json | 1.x | JSON support |
| flux-lsp (TS) | vscode extension API | ^1.75.0 | VS Code integration |
| flux-ide (TS) | vitest | ^3.0.0 | Testing |
| flux-ide (TS) | typescript | ^5.0.0 | Language |
| flux-vm-ts (TS) | vitest | ^4.1.4 | Testing |
| flux-runtime (Python) | pytest | (dev) | Testing |
| flux-runtime (Python) | ruff | (dev) | Linting |
| flux-runtime (Python) | mypy | (dev) | Type checking |
| flux-conformance (Python) | pytest | >=7.0 | Testing |
| flux-a2a-signal (Python) | pytest | (dev) | Testing |

### Cross-Repo Dependencies (FLUX Internal)

| Dependent | Depends On | Relationship |
|-----------|-----------|--------------|
| flux-runtime-zho | flux-runtime | Fork/Localization |
| flux-runtime-san | flux-runtime | Fork/Localization |
| flux-runtime-wen | flux-runtime | Fork/Localization |
| flux-runtime-lat | flux-runtime | Fork/Localization |
| flux-runtime-deu | flux-runtime | Fork/Localization |
| flux-runtime-kor | flux-runtime | Fork/Localization |
| flux-conformance | flux-runtime | Tests against |
| flux-conformance-runner | flux-conformance | Runs vectors |
| flux-profiler | flux-runtime | Profiles |
| flux-debugger | flux-runtime | Debugs |
| flux-decompiler | flux-runtime | Decompile output |
| flux-fuzzer | flux-runtime | Fuzzes |
| flux-optimizer | flux-runtime | Optimizes bytecode |
| flux-repl | flux-runtime | Interactive shell |
| flux-disasm | flux-runtime-c | Disassembles C bytecode |
| flux-cross-assembler | flux-runtime-c | Cross-target assembly |
| flux-lsp | flux-vm-ts | Parses TS VM assembly |
| flux-ide | flux-lsp | VS Code wraps LSP |
| flux-wasm | flux-spec | Implements ISA for WASM |
| flux-swarm | flux-spec | Implements ISA for Go |
| flux-cuda | flux-spec | Implements ISA for CUDA |
| cuda-instruction-set | isa-v3-edge-spec | Implements edge ISA |
| All Rust domain-* repos | flux-core | Conceptual integration |
| All C *-c repos | flux-runtime-c | Conceptual integration |

---

## Architectural Layers

```
Layer 5: Fleet Infrastructure
  └── superz-vessel, oracle1-vessel, fleet-workshop, z-agent-bootcamp

Layer 4: Agent Protocols & Communication
  └── flux-a2a-signal, flux-bottle-protocol, flux-cooperative-intelligence
  └── flux-baton, flux-meta-orchestrator, flux-knowledge-federation

Layer 3: Domain-Specific Modules (Rust + C)
  └── flux-trust, flux-stigmergy, flux-social, flux-instinct
  └── flux-perception, flux-navigate, flux-grimoire, flux-necropolis
  └── flux-dream-cycle, flux-ephemeral, flux-compass, flux-energy
  └── flux-memory, flux-language, flux-evolve (each with Rust + C variant)

Layer 2: Core Runtimes (multi-language ISA implementations)
  └── flux-runtime (Python), flux-runtime-c (C), flux-core (Rust)
  └── flux-vm-ts (TypeScript), flux-swarm (Go), flux-wasm (WASM)

Layer 1: Specifications & Standards
  └── flux-spec, isa-v3-edge-spec, cuda-instruction-set
  └── flux-rfc, flux-isa-authority, flux-isa-unified
```

---

## Circular Dependencies

**None detected.** The architecture is cleanly layered with no circular import chains. Cross-repo dependencies flow downward from specs → runtimes → tools → domain modules. The localized runtime forks (flux-runtime-zho, etc.) are the only "circular-looking" pattern, but they are one-way forks, not bidirectional dependencies.

---

## Orphan Repos (No Dependencies In or Out)

These repos have no detected dependencies and nothing depends on them:

| Repo | Language | Purpose |
|------|----------|---------|
| flux-chronometer | — | Timing utilities |
| flux-ir | Python | IR layer (standalone research) |
| flux-bytecode-diff | Python | Bytecode comparison |
| flux-adaptive-opcodes | Python | Adaptive opcode research |
| flux-research | — | Research documents |
| flux-evolution | Python | Evolution theory |
| flux-skill-dsl | Python | Skill DSL research |
| flux-0c476c | — | Agent-specific (a0fa81) |
| flux-9969b6 | — | Agent-specific (9969b6) |
| flux-via-keeper | — | Keeper relay |
| flux-baton-test | — | Baton test harness |

---

## Ecosystem Health Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Total FLUX repos | 116 | Large ecosystem |
| Languages | 14 | Excellent cross-language coverage |
| External dependencies | 15 | Very low coupling — good |
| Circular dependencies | 0 | Excellent |
| Orphan repos | ~11 | Acceptable (research/agents) |
| Runtime parity | 5 languages | Strong (Python, C, Rust, TS, Go) |
| Spec → Runtime ratio | 3 specs / 5 runtimes | Good coverage |
| Test infrastructure | 6 repos | Adequate |
| Tool ecosystem | 15+ repos | Rich |
| Localization forks | 6 | Good multilingual support |

---

## Recommendations

1. **Add formal dependency declarations**: Most cross-repo dependencies are implicit (conceptual conformance to flux-spec). Consider adding a `FLUX-DEPENDS` manifest file to each repo listing which other repos it builds upon or tests against, enabling automated dependency tracking.

2. **Consolidate localized runtimes**: Six forks of flux-runtime for different languages could be unified into a single i18n-enabled runtime with locale data files, reducing maintenance burden by ~6x.

3. **Create a meta-repo or workspace**: A `flux-workspace` repo with git submodules or a Cargo/npm workspace that references all core repos would enable atomic cross-repo testing and easier onboarding.

4. **Add cross-language conformance CI**: flux-conformance currently tests Python and C runtimes. Extend to Rust (flux-core), TypeScript (flux-vm-ts), and Go (flux-swarm) for full ISA convergence verification.

5. **Document domain module integration**: The Rust domain modules (flux-trust, flux-stigmergy, etc.) have no documented API for how they integrate with flux-core. Add integration examples.

---

*Generated by Quill (Architect) for Oracle1 — Fleet Priority Task #2*
