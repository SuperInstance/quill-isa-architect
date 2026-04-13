"""Tests for Quill's LLM module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import detect_provider, route_model


class TestProviderDetection(unittest.TestCase):

    def test_openai(self):
        self.assertEqual(detect_provider("https://api.openai.com/v1"), "openai")

    def test_anthropic(self):
        self.assertEqual(detect_provider("https://api.anthropic.com/v1"), "anthropic")

    def test_deepseek(self):
        self.assertEqual(detect_provider("https://api.deepseek.com/v1"), "deepseek")

    def test_google(self):
        self.assertEqual(detect_provider("https://generativelanguage.googleapis.com/v1"), "google")

    def test_local(self):
        self.assertEqual(detect_provider("http://localhost:11434/v1"), "local")

    def test_unknown_defaults_openai(self):
        self.assertEqual(detect_provider("https://api.unknown.ai/v1"), "openai")


class TestRouteModel(unittest.TestCase):

    def test_returns_provider(self):
        route = route_model("gpt-4o", "https://api.openai.com/v1")
        self.assertEqual(route["provider"], "openai")
        self.assertEqual(route["model"], "gpt-4o")

    def test_empty_model_gets_default(self):
        route = route_model("", "https://api.deepseek.com/v1")
        self.assertEqual(route["provider"], "deepseek")
        self.assertEqual(route["model"], "deepseek-chat")

    def test_has_max_context(self):
        for url in ["https://api.openai.com/v1", "https://api.anthropic.com/v1",
                     "http://localhost:11434/v1"]:
            route = route_model("test", url)
            self.assertIn("max_context", route)
            self.assertGreater(route["max_context"], 0)


class TestChat(unittest.TestCase):
    """Test the chat function with a fake endpoint (will fail gracefully)."""

    def test_unreachable_returns_error_status(self):
        from llm import chat
        result = chat(
            base_url="https://api.nonexistent-test.invalid/v1",
            api_key="test-key",
            model="test-model",
            message="ping",
            timeout=5,
        )
        self.assertEqual(result["status"], "unreachable")
        self.assertIn("error", result)
        self.assertIn("latency_ms", result)


if __name__ == "__main__":
    unittest.main()
