# Audit Skill

**Description**: Severity-ranked code review across multiple languages
**Version**: 1.0.0
**Author**: Quill (Architect)
**Dependencies**: None

## Overview

The audit skill enables systematic code review with evidence-based findings,
severity classification, and actionable remediation steps.

## Methodology

1. **Scope**: Identify files to review (commit range, directory, or full repo)
2. **Read**: Load each file's content
3. **Analyze**: Check for bugs, style issues, design concerns, security issues
4. **Classify**: Rate each finding by severity (🔴 High, ⚠️ Medium, 💡 Low)
5. **Report**: Generate structured audit report

## Severity Scale

| Level | Symbol | Criteria |
|-------|--------|----------|
| Critical | 🔴 | Bugs producing incorrect results, security vulnerabilities |
| Major | ⚠️ Major | Logic errors, missing error handling, incorrect routing |
| Medium | ⚠️ Medium | Heuristic fragility, dead code, style inconsistencies |
| Low | 💡 | Naming, documentation, minor improvements |

## Output Format

Each finding includes:
- **ID**: Unique identifier (e.g., A-1)
- **Severity**: Symbol + level
- **File**: Path to the affected file
- **Line(s)**: Line number(s)
- **Description**: What the issue is
- **Evidence**: Code snippet showing the issue
- **Fix**: Suggested remediation

## Example

```python
from src.skills import SkillLoader

loader = SkillLoader("SKILLS/")
audit = loader.load("audit")
print(audit.description)
# Output: "Severity-ranked code review across multiple languages"
```
