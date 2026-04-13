"""
Quill GitHub Module — API Wrapper with Retry/Backoff
=====================================================
Wraps GitHub API calls with retry logic and error handling.

Zero dependencies — uses only stdlib (urllib, json, time).
"""

import json
import time
import urllib.request
import urllib.error
from typing import Optional


class GitHubAPI:
    """
    GitHub API wrapper with retry, backoff, and rate limit awareness.
    
    Usage:
        gh = GitHubAPI(pat="ghp_xxx")
        repos = gh.list_org_repos("SuperInstance")
        content = gh.read_file("SuperInstance/flux-runtime", "README.md")
    """

    def __init__(self, pat: str, org: str = "SuperInstance"):
        self.pat = pat
        self.org = org
        self.base = "https://api.github.com"
        self.last_rate_limit_remaining = None
        self.request_count = 0

    def _request(self, path: str, method: str = "GET", body: dict = None,
                 timeout: int = 30, retries: int = 3) -> dict:
        """
        Make an authenticated GitHub API request with retry on failure.
        
        Implements exponential backoff: 1s, 2s, 4s between retries.
        Handles rate limiting (403) by waiting for reset time.
        """
        url = f"{self.base}{path}"
        headers = {
            "Authorization": f"token {self.pat}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

        data = json.dumps(body).encode("utf-8") if body else None
        last_error = None

        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    self.request_count += 1
                    # Track rate limit
                    remaining = resp.headers.get("X-RateLimit-Remaining")
                    if remaining is not None:
                        self.last_rate_limit_remaining = int(remaining)
                    result = resp.read().decode("utf-8")
                    return json.loads(result) if result else {}

            except urllib.error.HTTPError as e:
                self.request_count += 1
                last_error = e

                if e.code == 403 and "rate limit" in str(e).lower():
                    # Rate limited — wait for reset
                    reset = int(e.headers.get("X-RateLimit-Reset", 0))
                    wait = max(reset - int(time.time()), 1) + 1
                    if attempt < retries - 1:
                        time.sleep(min(wait, 60))
                        continue

                if attempt < retries - 1 and e.code >= 500:
                    # Server error — retry with backoff
                    time.sleep(2 ** attempt)
                    continue

                # Client error (4xx) — don't retry
                try:
                    return json.loads(e.read().decode("utf-8", errors="replace"))
                except Exception:
                    return {"error": f"HTTP {e.code}", "message": str(e)}

            except urllib.error.URLError as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return {"error": "unreachable", "message": str(e.reason)}

        return {"error": "max_retries", "message": str(last_error)}

    def list_org_repos(self, org: Optional[str] = None, per_page: int = 100,
                        max_pages: int = 10) -> list:
        """List all repos in an org, handling pagination."""
        org = org or self.org
        repos = []
        for page in range(1, max_pages + 1):
            data = self._request(f"/orgs/{org}/repos?per_page={per_page}&sort=updated&page={page}")
            if not isinstance(data, list) or len(data) == 0:
                break
            repos.extend(data)
        return repos

    def read_file(self, repo: str, path: str) -> Optional[str]:
        """Read a file from a repo. Returns decoded content or None."""
        import base64
        data = self._request(f"/repos/{repo}/contents/{path}")
        if "content" in data:
            return base64.b64decode(data["content"]).decode("utf-8")
        return None

    def list_directory(self, repo: str, path: str = "") -> list:
        """List files in a repo directory. Returns list of file info dicts."""
        data = self._request(f"/repos/{repo}/contents/{path}")
        if isinstance(data, list):
            return [{"name": i["name"], "size": i.get("size", 0),
                     "sha": i.get("sha", "")[:8], "type": i.get("type", "file")}
                    for i in data]
        return []

    def create_issue(self, repo: str, title: str, body: str) -> dict:
        """Create an issue on a repo."""
        return self._request(f"/repos/{repo}/issues", method="POST",
                             body={"title": title, "body": body})

    def get_issue(self, repo: str, number: int) -> dict:
        """Get an issue from a repo."""
        return self._request(f"/repos/{repo}/issues/{number}")

    def get_commit(self, repo: str, sha: str) -> dict:
        """Get commit details."""
        return self._request(f"/repos/{repo}/commits/{sha}")

    def list_commits(self, repo: str, per_page: int = 10) -> list:
        """List recent commits."""
        return self._request(f"/repos/{repo}/commits?per_page={per_page}")

    def search_repos(self, query: str, per_page: int = 20) -> dict:
        """Search repos across GitHub."""
        return self._request(f"/search/repositories?q={query}&per_page={per_page}")
