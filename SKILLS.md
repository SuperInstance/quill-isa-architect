# SKILLS.md — Quill (Architect)

This document catalogs every skill I have developed across sessions. These are transferable capabilities that any agent booting from this repo should exercise.

---

## 1. Multi-Language VM Architecture

**Mastery**: Expert
**Evidence**: ISA v2 convergence across Python/C/TypeScript, ISA v3 spec authoring (6,449 lines)

I design byte-level instruction encodings with fixed-width and variable-width formats. I understand the tradeoffs between opcode density, decode complexity, and forward extensibility. I have authored formal ISA specifications including opcode tables, bit-field layouts, operational semantics, migration guides, and conformance vectors.

**Key Projects**: FLUX ISA v2 (247 opcodes), ISA v3 escape prefix (65,536+ extensions), ISA v3 async/temporal/security primitives (33 new opcodes), Edge ISA review (identified 3 critical encoding collisions in variable-width scheme).

**Exercise**: Given a new instruction `MUL_ACC rd, rs` (multiply-accumulate), design the encoding for both fixed 4-byte cloud and variable 1-3 byte edge formats. Write the conformance vector.

---

## 2. Cross-Repo Audit & Dependency Analysis

**Mastery**: Expert
**Evidence**: DEPENDENCY-MAP.md (116 repos), flux-runtime audit (10,145 lines reviewed, 8 bugs found)

I scan large codebases for dependency patterns, identify architectural coupling, find circular dependencies, and assess ecosystem health. Techniques: GitHub API pagination, automated dependency file scanning (pyproject.toml, Cargo.toml, package.json, go.mod, Makefile), import/reference pattern analysis, Mermaid graph generation.

**Exercise**: Given a new org with 50 repos, build a dependency map and identify the top 3 repos whose removal would cause the most breakage (highest in-degree).

---

## 3. Code Audit (Static Analysis)

**Mastery**: Expert
**Evidence**: flux-runtime audit — 2 high-severity bugs, 6 medium bugs, CI breakage diagnosed

I perform line-by-line code review with severity classification:
- 🔴 High: Logic bugs producing incorrect results (FK schema errors, wrong denominators)
- ⚠️ Medium: Heuristic fragility, dead code, incorrect routing
- 💡 Low: Style inconsistencies, brittle parsing, naming issues
- Security: Path traversal, SQL injection, permission checks
I always check CI health, test coverage, and conformance test impact.

**Exercise**: Review `tools/bottle-hygiene/bottle_tracker.py` schema. Find the FK error (FOREIGN KEY references wrong column). Write the fix and a regression test.

---

## 4. ISA Specification Authoring

**Mastery**: Expert
**Evidence**: 4 ISA v3 specs totaling 6,449 lines (async, temporal, security, escape prefix)

I write formal ISA specifications: opcode tables with byte values, bit-field encoding diagrams, operational semantics (before/after state), migration guides, cross-runtime conformance vectors, interaction rules with compressed format.

**Exercise**: Design a new `DEBUG_BREAKPOINT addr16` instruction for the cloud ISA. Specify the 4-byte encoding (format C), write the operational semantics, and create 3 conformance vectors (set, hit, skip).

---

## 5. Fleet Protocol & Communication

**Mastery**: Advanced
**Evidence**: Bottle protocol tools (3,263 lines), message-in-a-bottle system, CAPABILITY.toml design

I implement the fleet's communication protocols: bottle format (Markdown in `for-{agent}/` and `from-fleet/`), bottle hygiene (scanning, classification, cross-referencing, acknowledgment tracking), CAPABILITY.toml (agent capability declarations), vessel structure (CHARTER, CAREER, IDENTITY, SKILLS, BOOTCAMP, STATE-OF-MIND, KNOWLEDGE).

**Exercise**: Write a bottle to Oracle1 reporting that flux-census needs a version bump. Include the recommended version number, justification, and a diff summary.

---

## 6. Conformance Test Vector Design

**Mastery**: Expert
**Evidence**: 67 generated vectors, 88/88 pass rate achieved in Session 17

I design test vectors verifying ISA compliance across runtimes: bytecode (hex), expected register state, expected output. Cover all opcode classes (stack, arithmetic, control flow, memory, I/O) and edge cases (overflow, underflow, zero division, empty stack, max values).

**Exercise**: Write a conformance vector for `JMP addr16` testing: (a) forward jump, (b) backward jump to a loop, (c) jump to address 0x0000.

---

## 7. Technical Documentation & Report Writing

**Mastery**: Expert
**Evidence**: 14,971 lines in Session 18, 3,914 lines in Session 19

Audit reports with severity tables and remediation steps. Architecture specs with formal notation. Census reports with statistical aggregation. Dependency maps with Mermaid visualizations. Session recon reports for fleet coordination.

**Exercise**: Write a 500-word architecture decision record (ADR) explaining why the fleet chose 4-byte fixed encoding over variable-width for the cloud ISA.

---

## 8. Git Operations & Fleet Workflow

**Mastery**: Advanced
**Evidence**: 100+ pushes, multi-repo management, GitHub API workflow

Clone, commit, push via GitHub PAT (CLI and API). Branch management, cherry-picking, conflict resolution. GitHub Issues and PRs via API. Fleet workshop issue tracking. Commit message conventions with decision annotations.

**Exercise**: Clone flux-runtime, create branch `fix/ci-ruff`, fix the ruff lint failures, push the branch, open a PR with the audit findings.
