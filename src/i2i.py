"""
Quill I2I-Lite Module — Iron-to-Iron Commit Convention
========================================================
Lightweight subset of the iron-to-iron protocol.
5 message types: PROPOSAL, REVIEW, ACCEPT, REJECT, COMMENT.

Format: [I2I:TYPE] scope — summary

Zero dependencies — uses only stdlib (re, datetime).
"""

import re
from datetime import datetime, timezone
from typing import Optional


I2I_TYPES = {"PROPOSAL", "REVIEW", "ACCEPT", "REJECT", "COMMENT"}

# Pattern: [I2I:TYPE] scope — summary
I2I_PATTERN = re.compile(
    r"^\[I2I:(\w+)\]\s+(.+?)\s+[-—]\s+(.+)$",
    re.MULTILINE
)


def format_i2i(msg_type: str, scope: str, summary: str) -> str:
    """Format an I2I commit message."""
    msg_type = msg_type.upper()
    if msg_type not in I2I_TYPES:
        raise ValueError(f"Invalid I2I type: {msg_type}. Use: {', '.join(sorted(I2I_TYPES))}")
    return f"[I2I:{msg_type}] {scope} — {summary}"


def parse_i2i(message: str) -> Optional[dict]:
    """Parse an I2I commit message. Returns dict or None."""
    match = I2I_PATTERN.search(message)
    if match:
        return {
            "type": match.group(1).upper(),
            "scope": match.group(2).strip(),
            "summary": match.group(3).strip(),
            "raw": match.group(0),
        }
    return None


def is_i2i(message: str) -> bool:
    """Check if a message follows I2I convention."""
    return I2I_PATTERN.search(message) is not None


def validate_i2i(message: str) -> list:
    """Validate an I2I message. Returns list of issues (empty = valid)."""
    issues = []
    parsed = parse_i2i(message)

    if not parsed:
        if "[I2I:" in message:
            issues.append("Malformed I2I format. Expected: [I2I:TYPE] scope — summary")
        else:
            issues.append("Not an I2I message")
        return issues

    if parsed["type"] not in I2I_TYPES:
        issues.append(f"Unknown I2I type: {parsed['type']}. Valid: {', '.join(sorted(I2I_TYPES))}")

    if len(parsed["scope"]) > 60:
        issues.append("Scope too long (>60 chars). Keep it concise.")

    if len(parsed["summary"]) > 200:
        issues.append("Summary too long (>200 chars). Keep it concise.")

    return issues
