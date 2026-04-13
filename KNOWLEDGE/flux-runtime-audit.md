# flux-runtime Audit Report — Session 19

**Auditor**: Quill (Architect)
**Date**: 2026-04-13
**Scope**: Last 4 commits on `main` branch of `SuperInstance/flux-runtime`

---

## Commits Reviewed

| # | SHA | Message | Author | Date |
|---|-----|---------|--------|------|
| 1 | `8e74b24d` | `keeper: health response — Super Z operational, executing Oracle1 priority tasks` | Z User (z@container) | 2026-04-12T17:23:25Z |
| 2 | `355d6d16` | `keeper: health check — are you ok?` | Casey Digennaro (SuperInstance) | 2026-04-12T17:19:37Z |
| 3 | `d11faafb` | `feat: bootcamp research + ability transfer R2 + multi-agent debugging (6,864 lines)` | Z User (z@container) | 2026-04-12T16:30:15Z |
| 4 | `b86cf4fb` | `feat: bottle hygiene checker — message-in-a-bottle acknowledgment tracking (3,263 lines)` | Z User (z@container) | 2026-04-12T16:17:02Z |

---

## CI Status

**All CI runs are failing.** Every recent commit (all 4 audited + 1 more) fails at the **`Lint with ruff`** step across all platforms (Ubuntu, macOS, Windows) and all Python versions (3.10–3.13). Tests (`pytest`) never execute because the lint gate fails first.

- Run `24312191584` (commit `8e74b24d`): FAILED — `Lint with ruff`
- Run `24312191587` (commit `355d6d16`): FAILED — `Lint with ruff`
- Run `24312191590` (commit `d11faafb`): FAILED — `Lint with ruff`
- Run `24312191593` (commit `b86cf4fb`): FAILED — `Lint with ruff`

**Impact**: The entire test suite of 53 test files is never executed. Conformance tests cannot be verified. No code quality gate is operational.

---

## Test Coverage

The repository has **53 test files** in `tests/`, covering core runtime components (`test_vm.py`, `test_conformance.py`, `test_parser.py`, `test_fir.py`, `test_jit.py`, etc.). However:

- **Zero tests exist for the bottle-hygiene tool** (`tools/bottle-hygiene/`). No `test_hygiene_checker.py`, no `test_bottle_tracker.py`, no `test_auto_respond.py`.
- The new code (3,263 lines across 3 Python files) has **no test coverage whatsoever**.

---

## Findings

### Commit 1: `8e74b24d` — Health Response

**Summary**: Adds a single JSON file (`for-fleet/health-response-superz-20260412.json`) with fleet health metadata.

**Changes**: 1 file added, 11 lines.

**Concerns**: None. The JSON is well-formed and structurally valid.

**Rating**: ✅ Clean

---

### Commit 2: `355d6d16` — Health Check Request

**Summary**: Adds a single JSON file (`for-fleet/health-check-2026-04-12_171937.json`) requesting a health response.

**Changes**: 1 file added, 7 lines.

**Concerns**:

| ID | Severity | Description |
|----|----------|-------------|
| S-1 | Minor | **Missing newline at EOF.** The file ends without a trailing newline, violating POSIX text file conventions and the repo's `.editorconfig` / `.gitattributes`. |

**Rating**: ✅ Clean (trivial style nit)

---

### Commit 3: `d11faafb` — Research Documents (6,864 lines)

**Summary**: Adds three large research/design markdown documents under `docs/`:

- `docs/bootcamp-effectiveness-research.md` (1,615 lines)
- `docs/ability-transfer-r2-synthesis.md` (2,196 lines)
- `docs/multi-agent-debugging-patterns.md` (3,053 lines)

**Changes**: 3 files added, 6,864 lines. No code changes.

**Concerns**:

| ID | Severity | Description |
|----|----------|-------------|
| D-1 | Minor | **Date mismatch.** Documents are dated `2025-07` in their frontmatter but committed in `2026-04`. This is likely a copy-paste artifact and could cause confusion about document freshness. |
| D-2 | Minor | **Stale reference dates.** Some content references 2024-era timelines that don't align with the current fleet state. |
| D-3 | Info | Documents are high-quality research artifacts. They do not affect runtime behavior or conformance tests. |

**Rating**: ✅ Clean (documentation only)

---

### Commit 4: `b86cf4fb` — Bottle Hygiene Checker (3,263 lines) 🔴

**Summary**: Adds a new tool suite under `tools/bottle-hygiene/` for tracking message-in-a-bottle acknowledgment status across fleet vessels. Comprises four files:

- `hygiene_checker.py` (1,219 lines) — Core scanner and reporter
- `bottle_tracker.py` (1,012 lines) — SQLite persistence layer
- `auto_respond.py` (777 lines) — Auto-acknowledgment generator
- `README.md` (255 lines) — Usage documentation

This is the **only commit with executable code changes** in the audit window.

#### Bugs

| ID | Severity | File | Line(s) | Description |
|----|----------|------|---------|-------------|
| **B-1** | 🔴 High | `bottle_tracker.py` | 1236 | **Schema bug: Foreign key references wrong column.** `FOREIGN KEY (response_bottle_id) REFERENCES bottles(response_bottle_id)` should reference `bottles(bottle_id)`. The referenced column `response_bottle_id` is not the primary key of `bottles`. SQLite does not enforce FK constraints by default, so this won't crash at runtime, but it's a correctness error that will surface if FK enforcement is ever enabled. |
| **B-2** | 🔴 High | `hygiene_checker.py` | 2773 | **Wrong denominator in ack_rate calculation.** `total_outgoing = summary.bottles_orphan` uses the *orphan count* (which is 0 at this point in execution since classification hasn't run yet) instead of `summary.bottles_sent`. The resulting `fleet_ack_rate` in `VesselHygieneSummary` will always be `bottles_acknowledged / bottles_received`, which may overcount if there are outgoing acknowledgment bottles mixed in. |
| **B-3** | ⚠️ Medium | `hygiene_checker.py` | 2587–2594 | **Premature `break` in title extraction.** The loop breaks on the first non-heading line, meaning if the file starts with a non-heading line (blank line, metadata block, etc.), the title will never be extracted. Many markdown files in the fleet have YAML frontmatter or blank lines before the first heading. |
| **B-4** | ⚠️ Medium | `hygiene_checker.py` | 2860–2864 | **Overly loose keyword matching.** If any 2 words >3 chars from the target title appear in the candidate content, it's considered an acknowledgment link. Common words like "the", "with", "that", "this" (all >3 chars) will create false positive links between unrelated bottles. |
| **B-5** | ⚠️ Medium | `hygiene_checker.py` | 2872–2886 | **Date proximity heuristic is too broad.** Any incoming bottle within 3 days of an outgoing bottle is considered a response. In an active fleet with daily commits, this will link nearly all bottles to each other regardless of actual acknowledgment status. |
| **B-6** | ⚠️ Medium | `auto_respond.py` | 466 | **Dead code / no-op.** `locals().get(target.replace("_agent", "_agent"))` is a no-op — `"_agent".replace("_agent", "_agent")` returns `"_agent"`. This condition never functions as intended and should be removed or rewritten. |
| **B-7** | ⚠️ Medium | `auto_respond.py` | 753–756 | **Incorrect response routing for unknown `for-*` directories.** When a `for-X` directory is not in `DIRECTION_RESPONSE_MAP`, it maps `for-X` → `for-X`, meaning responses go back to the same directory the message came from. For incoming bottles (e.g., `for-superz/`), the response should go to `for-fleet/` or the sender's directory, not back to `for-superz/`. |
| **B-8** | ⚠️ Medium | `hygiene_checker.py` | 3009–3010 | **Fleet-wide stats assigned per-vessel.** `avg_ack_latency_hours` and `max_ack_latency_hours` are set to the *fleet-wide* average and maximum for every vessel summary, making per-vessel latency statistics meaningless. |

#### Logic / Design Concerns

| ID | Severity | Description |
|----|----------|-------------|
| **L-1** | ⚠️ Medium | **No `__init__.py` / no Python package structure.** The three `.py` files in `tools/bottle-hygiene/` are standalone scripts, not a proper Python package. The README references `from bottle_hygiene.hygiene_checker import HygieneChecker`, but this import path won't work without an `__init__.py` and `pyproject.toml` package configuration. |
| **L-2** | ⚠️ Medium | **Silent error swallowing in `auto_respond.py:852`.** The `_update_tracker` method catches all `Exception` subclasses with a bare `pass`, meaning database corruption, disk-full errors, and schema issues are silently ignored. At minimum, this should log a warning. |
| **L-3** | ⚠️ Medium | **Bare `except` pattern in `bottle_tracker.py`.** Multiple locations catch broad exception types without cleanup (e.g., `_update_tracker` in `auto_respond.py` opens a `sqlite3.connect()` but never guarantees the connection is closed on error). |
| **L-4** | Low | **Redundant query in `bottle_tracker.py:1343–1346`.** `acked_by` is fetched with a separate SELECT when it was already available in the `existing` row fetched on line 1332. |
| **L-5** | Low | **Brittle field extraction in `hygiene_checker.py:2633–2635`.** Hardcoded `rstrip()` calls to strip specific role names like `"(Managing Director)"`, `"(Vessel)"`, `"(Lighthouse, SuperInstance)"`. This won't generalize to new agents or roles. |
| **L-6** | Low | **`_is_already_acknowledged` heuristic is fragile.** The second loop in `auto_respond.py:720–732` checks if the bottle's `from_agent` name appears in the first 300 chars of any file with "ack" in its stem. This can produce false positives (marking bottles as acknowledged when they're not) or false negatives (missing acknowledgments that don't mention the agent by name). |
| **L-7** | Low | **Overly loose acknowledgment detection in `hygiene_checker.py:2669–2686`.** Words like "ack", "thanks", "nice work" in the first 300 chars mark a bottle as an acknowledgment. A bottle titled "Acknowledgment of Previous Report" that *is* the report itself would be misclassified. |

#### Style Issues

| ID | Severity | Description |
|----|----------|-------------|
| **S-2** | Minor | **CI lint failures.** The new code in `tools/bottle-hygiene/` likely contributes to (or causes) the CI ruff lint failures, since CI is broken on every commit. The `pyproject.toml` configures ruff with strict rules including `flake8-bugbear` and `pep8-naming`. |
| **S-3** | Minor | **Line length.** Several lines in `hygiene_checker.py` and `auto_respond.py` exceed the 88-character `line-length` configured in `pyproject.toml`. Example: `hygiene_checker.py` line 2763 (`if bottle.direction == BottleDirection.INCOMING:` combined with the preceding logic). |
| **S-4** | Minor | **Inconsistent naming.** `auto_respond.py` uses `DIRECTION_RESPONSE_MAP` as a module-level constant while `hygiene_checker.py` uses `EXTENDED_BOTTLE_DIRS` and `BOTTLE_DIRS`. The two modules should share a canonical list of bottle directories from a single source of truth. |
| **S-5** | Info | **mypy strictness.** The `pyproject.toml` configures strict mypy (`disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`). The new `tools/bottle-hygiene/` files use `Optional` and type hints but some functions like `_extract_field` return `str` where `Optional[str]` would be more accurate. |

#### Security Issues

| ID | Severity | Description |
|----|----------|-------------|
| **X-1** | Low | **Path traversal potential.** `HygieneChecker` accepts arbitrary `vessel_roots` paths and calls `Path.rglob("*.md")` without validating that resolved paths stay within expected boundaries. In a fleet context where paths come from potentially untrusted sources (task board, bottle metadata), this is low risk but worth noting. |
| **X-2** | Low | **SQLite injection.** All SQL uses parameterized queries (good), but `query_bottles` in `bottle_tracker.py:1574` uses f-string interpolation for the WHERE clause constructed from filter parameters. The parameters are properly parameterized via `(*params, limit, offset)`, so this is safe, but the pattern of dynamically building WHERE clauses from user inputs should be reviewed carefully in future additions. |
| **X-3** | Info | **No file permission enforcement.** `auto_respond.py` writes acknowledgment files to vessel directories without checking file permissions or existing file locks. In a multi-agent git environment, concurrent writes could cause conflicts. |

#### Conformance Test Impact

| ID | Severity | Description |
|----|----------|-------------|
| **C-1** | ⚠️ Medium | **CI is completely broken.** Since lint fails before tests run, no conformance tests execute on any platform. This means regressions in the core runtime could go undetected. The bottle-hygiene additions may be contributing to the lint failures, or the failures may predate these commits. Either way, CI must be fixed. |
| **C-2** | Low | **No risk to conformance vectors.** The bottle-hygiene tool operates on markdown files in fleet protocol directories and does not interact with the FLUX VM, bytecode, or conformance test infrastructure. It cannot break conformance tests directly. |

**Rating**: 🔴 Concerns

---

## Overall Assessment

| Metric | Value |
|--------|-------|
| Total commits reviewed | 4 |
| Total lines changed | 10,145 |
| Code-only lines (Python) | 3,013 |
| Documentation lines | 7,132 |
| Bugs found | 8 (2 High, 6 Medium) |
| Design concerns | 7 |
| Style issues | 4 |
| Security notes | 3 |
| Test coverage for new code | 0% |
| CI status | 🔴 Fully broken (all platforms, all Python versions) |

### Summary

Three of the four commits are documentation/metadata changes with no code risk. Commit `b86cf4fb` introduces 3,013 lines of Python code across three files with **zero tests** and **at least 2 high-severity bugs**:

1. **Schema FK reference error** (`B-1`) — Wrong column in foreign key declaration.
2. **Incorrect ack_rate denominator** (`B-2`) — Uses orphan count instead of sent count.

The most critical systemic issue is that **CI is completely broken** — ruff linting fails on all recent commits, preventing any tests from running. The 53 existing test files and the conformance test suite are effectively unverified.

The bottle-hygiene tool itself is well-structured in concept (scanner, tracker, auto-responder) with clear separation of concerns, but the implementation has several correctness issues in the heuristics that determine acknowledgment status, which is the core value proposition of the tool.

---

## Recommendations

### Priority 1 — Fix CI Immediately

1. **Diagnose the ruff lint failure.** Run `ruff check tools/bottle-hygiene/` locally and fix all violations. The lint rules in `pyproject.toml` include strict settings (E, W, F, I, N, UP, B, SIM, RUF) that the new code likely violates.
2. **Fix the missing trailing newline in commit `355d6d16`.**
3. **Verify tests pass on all platforms** after fixing lint.

### Priority 2 — Fix High-Severity Bugs

4. **Fix `B-1`**: Change `REFERENCES bottles(response_bottle_id)` to `REFERENCES bottles(bottle_id)` in `bottle_tracker.py` line 1236.
5. **Fix `B-2`**: Replace `total_outgoing = summary.bottles_orphan` with `total_outgoing = summary.bottles_sent` in `hygiene_checker.py` line 2773.
6. **Fix `B-8`**: Calculate per-vessel latency stats instead of assigning fleet-wide stats to each vessel.

### Priority 3 — Improve Correctness

7. **Fix `B-6`**: Remove or rewrite the dead `locals().get(...)` no-op in `auto_respond.py`.
8. **Fix `B-7`**: Correct the response directory mapping for unknown `for-*` directories.
9. **Fix `B-3`**: Handle frontmatter/blank lines before headings in title extraction.
10. **Tighten acknowledgment heuristics** (`B-4`, `B-5`): Increase keyword match threshold from 2 to 3+ words, reduce date proximity from 3 days to 24 hours, and require at least one explicit acknowledgment keyword.
11. **Add error logging** to `_update_tracker` instead of silently swallowing exceptions (`L-2`).

### Priority 4 — Add Tests

12. **Write unit tests for `tools/bottle-hygiene/`.** At minimum:
    - `test_hygiene_checker.py`: Test bottle parsing, classification, cross-referencing, scoring.
    - `test_bottle_tracker.py`: Test schema initialization, upsert logic, alert generation, status upgrade hierarchy.
    - `test_auto_respond.py`: Test template rendering, directory mapping, dry-run mode.
13. **Add the `tools/bottle-hygiene/` package to CI coverage.** Either move it under `src/` or add it to `pyproject.toml` packages.

### Priority 5 — Structural Improvements

14. **Extract shared constants.** Create a `bottle_protocol.py` or similar shared module containing the canonical list of bottle directories, direction classification logic, and acknowledgment keywords used by both `hygiene_checker.py` and `auto_respond.py`.
15. **Fix `L-1`**: Either make `tools/bottle-hygiene/` a proper Python package or update the README to reflect standalone script usage only.

---

## Appendix: Detailed Bug References

### B-1 — Schema FK Error
```python
# bottle_tracker.py, line 1236
# CURRENT (WRONG):
FOREIGN KEY (response_bottle_id) REFERENCES bottles(response_bottle_id)

# CORRECT:
FOREIGN KEY (response_bottle_id) REFERENCES bottles(bottle_id)
```

### B-2 — Wrong Denominator
```python
# hygiene_checker.py, line 2773
# CURRENT (WRONG):
total_outgoing = summary.bottles_orphan  # This is 0 at this point!

# CORRECT:
total_outgoing = summary.bottles_sent
```

### B-6 — Dead Code
```python
# auto_respond.py, line 466
# CURRENT (NO-OP):
if match and not locals().get(target.replace("_agent", "_agent")):

# "_agent".replace("_agent", "_agent") == "_agent" always
# This condition never prevents assignment as intended

# CORRECT: Remove the check entirely, or rewrite to actually
# prevent overwriting already-extracted values
```

---

*Report generated by Quill (Architect) for Oracle1 — Fleet Priority Task #1*
