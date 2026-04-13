"""Tests for Quill's configuration module."""

import sys
import os
import unittest
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import load_env_file, load_vessel_json, validate, is_ready


class TestLoadEnvFile(unittest.TestCase):

    def test_loads_valid_env(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("KEY1=value1\nKEY2=value2\n# Comment\nKEY3 = value with spaces \n")
            f.flush()
            result = load_env_file(Path(f.name))
        os.unlink(f.name)

        self.assertEqual(result["KEY1"], "value1")
        self.assertEqual(result["KEY2"], "value2")
        self.assertEqual(result["KEY3"], "value with spaces")
        self.assertNotIn("# Comment", result)

    def test_missing_file_returns_empty(self):
        result = load_env_file(Path("/nonexistent/.env"))
        self.assertEqual(result, {})


class TestValidate(unittest.TestCase):

    def test_empty_config_has_errors(self):
        config = {"api_key": "", "base_url": "", "model": "", "github_pat": "",
                  "prompt_file": Path("/nonexistent/PROMPT.md")}
        issues = validate(config)
        self.assertTrue(len(issues) >= 3)
        levels = [i["level"] for i in issues]
        self.assertIn("error", levels)

    def test_full_config_is_clean(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test prompt")
            f.flush()
            config = {
                "api_key": "sk-test", "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o", "github_pat": "ghp-test",
                "prompt_file": Path(f.name),
            }
            issues = validate(config)
        os.unlink(f.name)
        self.assertEqual(len(issues), 0)

    def test_is_ready(self):
        self.assertFalse(is_ready({"api_key": "", "base_url": "", "model": ""}))
        self.assertTrue(is_ready({"api_key": "k", "base_url": "u", "model": "m"}))


if __name__ == "__main__":
    unittest.main()
