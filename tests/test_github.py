"""Tests for Quill's GitHub module."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from github import GitHubAPI


class TestGitHubAPIInit(unittest.TestCase):

    def test_default_org(self):
        gh = GitHubAPI(pat="test-token")
        self.assertEqual(gh.org, "SuperInstance")
        self.assertEqual(gh.pat, "test-token")

    def test_custom_org(self):
        gh = GitHubAPI(pat="test-token", org="Lucineer")
        self.assertEqual(gh.org, "Lucineer")

    def test_base_url(self):
        gh = GitHubAPI(pat="test-token")
        self.assertTrue(gh.base.endswith("github.com"))


class TestGitHubAPIRequest(unittest.TestCase):
    """Test the _request method with mocked urllib."""

    @patch("github.urllib.request.urlopen")
    def test_successful_get(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"name": "test"}'
        mock_resp.headers = {"X-RateLimit-Remaining": "59"}
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        gh = GitHubAPI(pat="test-token")
        result = gh._request("/repos/test/repo")
        self.assertEqual(result["name"], "test")
        self.assertEqual(gh.request_count, 1)

    @patch("github.urllib.request.urlopen")
    def test_handles_404(self, mock_urlopen):
        import urllib.error
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"message": "Not Found"}'
        mock_resp.code = 404
        mock_resp.headers = {"X-RateLimit-Reset": "0"}
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="", code=404, msg="Not Found", hdrs=mock_resp.headers, fp=mock_resp
        )

        gh = GitHubAPI(pat="test-token")
        result = gh._request("/repos/nonexistent/repo", retries=1)
        # 404 is a client error, should contain message from body
        self.assertIn("message", result)

    @patch("github.urllib.request.urlopen")
    def test_read_file(self, mock_urlopen):
        import base64
        content = "Hello, World!"
        encoded = base64.b64encode(content.encode()).decode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = f'{{"content": "{encoded}"}}'.encode()
        mock_resp.headers = {"X-RateLimit-Remaining": "58"}
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        gh = GitHubAPI(pat="test-token")
        result = gh.read_file("owner/repo", "file.txt")
        self.assertEqual(result, "Hello, World!")

    @patch("github.urllib.request.urlopen")
    def test_list_directory(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'[{"name": "README.md", "size": 100, "sha": "abcdef1234567890", "type": "file"}]'
        mock_resp.headers = {"X-RateLimit-Remaining": "57"}
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        gh = GitHubAPI(pat="test-token")
        result = gh.list_directory("owner/repo")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "README.md")
        self.assertEqual(result[0]["sha"], "abcdef12")


if __name__ == "__main__":
    unittest.main()
