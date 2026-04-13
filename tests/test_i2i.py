"""Tests for Quill's I2I module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from i2i import format_i2i, parse_i2i, is_i2i, validate_i2i


class TestFormatI2I(unittest.TestCase):

    def test_proposal(self):
        msg = format_i2i("PROPOSAL", "flux-runtime", "Fix CI ruff failures")
        self.assertEqual(msg, "[I2I:PROPOSAL] flux-runtime — Fix CI ruff failures")

    def test_review(self):
        msg = format_i2i("REVIEW", "quill-isa-architect", "Found 3 bugs")
        self.assertEqual(msg, "[I2I:REVIEW] quill-isa-architect — Found 3 bugs")

    def test_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            format_i2i("INVALID", "scope", "summary")


class TestParseI2I(unittest.TestCase):

    def test_parse_valid(self):
        result = parse_i2i("[I2I:PROPOSAL] flux-runtime — Fix CI")
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "PROPOSAL")
        self.assertEqual(result["scope"], "flux-runtime")
        self.assertEqual(result["summary"], "Fix CI")

    def test_parse_invalid_returns_none(self):
        self.assertIsNone(parse_i2i("Just a regular commit message"))
        self.assertIsNone(parse_i2i(""))

    def test_parse_multiline(self):
        msg = "Some header\n[I2I:REVIEW] isa-v3-edge — Critical encoding bugs\nSome footer"
        result = parse_i2i(msg)
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "REVIEW")


class TestIsI2I(unittest.TestCase):

    def test_valid(self):
        self.assertTrue(is_i2i("[I2I:ACCEPT] repo — Merged fix"))

    def test_invalid(self):
        self.assertFalse(is_i2i("regular commit message"))


class TestValidateI2I(unittest.TestCase):

    def test_valid_message(self):
        issues = validate_i2i("[I2I:COMMENT] flux-census — Updated to 878 repos")
        self.assertEqual(len(issues), 0)

    def test_invalid_type(self):
        issues = validate_i2i("[I2I:BOGUS] repo — message")
        self.assertTrue(len(issues) > 0)

    def test_long_scope(self):
        issues = validate_i2i(f"[I2I:REVIEW] {'x' * 100} — message")
        self.assertTrue(any("Scope too long" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
