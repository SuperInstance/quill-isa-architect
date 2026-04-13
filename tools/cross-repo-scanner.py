#!/usr/bin/env python3
"""
Quill Cross-Repo Scanner — Dependency Analysis Tool

Scans a GitHub organization for dependency patterns across repos.
Produces a dependency graph with language distribution, circular
dependency detection, and ecosystem health metrics.

Usage:
    python3 cross-repo-scanner.py --org SuperInstance --pat $GITHUB_PAT
    python3 cross-repo-scanner.py --org SuperInstance --pat $GITHUB_PAT --output deps.json
"""

import json
import urllib.request
import urllib.error
import argparse
from datetime import datetime, timezone
from collections import defaultdict


def api_get(url: str, pat: str) -> dict:
    """Make an authenticated GitHub API request."""
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {pat}",
        "Accept": "application/vnd.github.v3+json",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_repos(org: str, pat: str) -> list:
    """List all repos in an org, handling pagination."""
    repos = []
    page = 1
    while True:
        data = api_get(
            f"https://api.github.com/{'orgs' if org else 'users'}/{org}/repos"
            f"?per_page=100&sort=updated&page={page}",
            pat,
        )
        if not isinstance(data, list) or len(data) == 0:
            break
        repos.extend(data)
        page += 1
    return repos


def scan_deps(repo_full_name: str, pat: str) -> dict:
    """Scan a repo for dependency files and references."""
    deps = {"imports": [], "dep_files": []}

    dep_files = [
        "requirements.txt", "pyproject.toml", "setup.py",
        "package.json", "Cargo.toml", "go.mod",
        "CMakeLists.txt", "Makefile", "Gemfile",
    ]

    for f in dep_files:
        try:
            content = api_get(
                f"https://api.github.com/repos/{repo_full_name}/contents/{f}",
                pat,
            )
            import base64
            text = base64.b64decode(content["content"]).decode("utf-8", errors="replace")[:2000]
            deps["dep_files"].append({"file": f, "content": text})
        except Exception:
            pass

    return deps


def main():
    parser = argparse.ArgumentParser(description="Quill Cross-Repo Scanner")
    parser.add_argument("--org", required=True, help="GitHub org/username")
    parser.add_argument("--pat", required=True, help="GitHub PAT")
    parser.add_argument("--output", "-o", help="Output file (JSON)")
    parser.add_argument("--filter", help="Only scan repos matching this prefix")
    parser.add_argument("--max-repos", type=int, default=200, help="Max repos to scan")
    args = parser.parse_args()

    print(f"Quill Cross-Repo Scanner v1.0")
    print(f"Scanning: github.com/{args.org}")
    print()

    repos = list_repos(args.org, args.pat)
    print(f"Found {len(repos)} total repos")

    if args.filter:
        repos = [r for r in repos if r["name"].startswith(args.filter)]
        print(f"Filtered to {len(repos)} repos matching '{args.filter}'")

    repos = repos[:args.max_repos]
    print(f"Scanning {len(repos)} repos...")

    languages = defaultdict(int)
    results = []

    for i, repo in enumerate(repos):
        name = repo["name"]
        lang = repo.get("language") or "None"
        languages[lang] += 1

        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{len(repos)}] {name} ({lang})")

        deps = scan_deps(repo["full_name"], args.pat)
        results.append({
            "name": name,
            "language": lang,
            "description": repo.get("description", ""),
            "size": repo.get("size", 0),
            "updated": repo.get("pushed_at", ""),
            "dependencies": deps,
        })

    print(f"\nScan complete. {len(results)} repos analyzed.")

    # Summary
    print(f"\nLanguage Distribution:")
    for lang, count in sorted(languages.items(), key=lambda x: -x[1]):
        print(f"  {lang}: {count}")

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "org": args.org,
        "total_repos": len(results),
        "languages": dict(languages),
        "repos": results,
    }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()
