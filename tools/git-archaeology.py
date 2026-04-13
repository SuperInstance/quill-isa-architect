#!/usr/bin/env python3
"""
Quill Git Archaeology — Commit Analysis & Witness Mark Scoring

Analyzes git commit histories to assess code craftsmanship quality.
Implements the Witness Marks Protocol: git as a craftsman's medium.

Usage:
    python3 git-archaeology.py --repo ./path/to/repo
    python3 git-archaeology.py --repo ./path/to/repo --last 20 --score
"""

import argparse
import json
import subprocess
import re
from datetime import datetime
from collections import defaultdict


def run_git(args: list, cwd: str) -> str:
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def get_commits(repo_path: str, count: int = 50) -> list:
    """Get recent commits with metadata."""
    fmt = "%H|%an|%ae|%aI|%s|%b"
    log = run_git(["log", f"-{count}", f"--format={fmt}"], repo_path)
    commits = []
    for line in log.split("\n"):
        if "|" not in line:
            continue
        parts = line.split("|", 5)
        if len(parts) >= 5:
            commits.append({
                "sha": parts[0][:12],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "subject": parts[4],
                "body": parts[5] if len(parts) > 5 else "",
            })
    return commits


def get_diffstat(repo_path: str, sha: str) -> dict:
    """Get diff stats for a commit."""
    stat = run_git(["show", "--stat", "--format=", sha], repo_path)
    files_changed = 0
    insertions = 0
    deletions = 0
    for line in stat.split("\n"):
        match = re.match(r"(\d+) file.+?(\d+) insertion.+?(\d+) deletion", line)
        if match:
            files_changed = int(match.group(1))
            insertions = int(match.group(2))
            deletions = int(match.group(3))
    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
        "net_lines": insertions - deletions,
    }


def score_witness_mark(commit: dict, stat: dict) -> dict:
    """Score a commit's witness mark quality (0-100).

    A witness mark is a git commit that tells a story. High scores mean
    the commit is informative, well-structured, and useful for future
    archaeologists reading the history.
    """
    score = 50  # Base score
    reasons = []

    subject = commit["subject"]
    body = commit["body"]

    # Length checks
    if len(subject) < 10:
        score -= 15
        reasons.append("Subject too short")
    elif len(subject) > 100:
        score -= 5
        reasons.append("Subject too long")
    else:
        score += 5
        reasons.append("Good subject length")

    # Conventional commit format
    if re.match(r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?:", subject):
        score += 10
        reasons.append("Uses conventional commit format")

    # Has body
    if body and len(body.strip()) > 20:
        score += 10
        reasons.append("Has informative body")
    else:
        score -= 10
        reasons.append("No commit body")

    # Explains WHY (not just WHAT)
    why_keywords = ["because", "why", "fixes", "resolves", "addresses", "for", "to support"]
    if any(kw in body.lower() for kw in why_keywords):
        score += 10
        reasons.append("Explains reasoning")

    # Size appropriateness
    total = stat["files_changed"]
    if total > 50:
        score -= 15
        reasons.append(f"Too many files ({total})")
    elif total > 20:
        score -= 5
        reasons.append(f"Large commit ({total} files)")
    elif total == 0:
        score -= 10
        reasons.append("Empty commit")
    else:
        score += 5
        reasons.append("Focused commit")

    score = max(0, min(100, score))
    return {
        "score": score,
        "reasons": reasons,
        "grade": "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D",
    }


def analyze_repo(repo_path: str, count: int = 50, do_score: bool = False) -> dict:
    """Analyze a git repository's commit history."""
    commits = get_commits(repo_path, count)

    results = []
    total_score = 0
    author_stats = defaultdict(lambda: {"commits": 0, "lines": 0})

    for commit in commits:
        stat = get_diffstat(repo_path, commit["sha"])
        entry = {**commit, "stat": stat}

        if do_score:
            wm = score_witness_mark(commit, stat)
            entry["witness_mark"] = wm
            total_score += wm["score"]

        author = commit["author"]
        author_stats[author]["commits"] += 1
        author_stats[author]["lines"] += abs(stat["net_lines"])

        results.append(entry)

    analysis = {
        "repo": repo_path,
        "commits_analyzed": len(results),
        "total_insertions": sum(r["stat"]["insertions"] for r in results),
        "total_deletions": sum(r["stat"]["deletions"] for r in results),
        "authors": dict(author_stats),
    }

    if do_score and results:
        analysis["avg_witness_score"] = round(total_score / len(results), 1)
        analysis["grade_distribution"] = defaultdict(int)
        for r in results:
            if "witness_mark" in r:
                analysis["grade_distribution"][r["witness_mark"]["grade"]] += 1
        analysis["grade_distribution"] = dict(analysis["grade_distribution"])

    return analysis, results


def main():
    parser = argparse.ArgumentParser(description="Quill Git Archaeology Tool")
    parser.add_argument("--repo", required=True, help="Path to git repository")
    parser.add_argument("--last", type=int, default=50, help="Number of commits to analyze")
    parser.add_argument("--score", action="store_true", help="Score witness marks")
    parser.add_argument("--output", "-o", help="Output file (JSON)")
    parser.add_argument("--top", type=int, default=10, help="Show top N commits")
    args = parser.parse_args()

    print(f"Quill Git Archaeology — analyzing {args.repo}")
    analysis, results = analyze_repo(args.repo, args.last, args.score)

    print(f"\nRepository Analysis:")
    print(f"  Commits: {analysis['commits_analyzed']}")
    print(f"  Insertions: {analysis['total_insertions']:,}")
    print(f"  Deletions: {analysis['total_deletions']:,}")
    print(f"  Authors: {len(analysis['authors'])}")

    if args.score:
        print(f"  Avg Witness Score: {analysis.get('avg_witness_score', 'N/A')}/100")
        print(f"  Grades: {analysis.get('grade_distribution', {})}")

    print(f"\n  Top contributors:")
    for author, stats in sorted(analysis["authors"].items(), key=lambda x: -x[1]["commits"]):
        print(f"    {author}: {stats['commits']} commits, {stats['lines']:,} lines")

    if args.score:
        print(f"\n  Top witness marks:")
        scored = [r for r in results if "witness_mark" in r]
        scored.sort(key=lambda x: -x["witness_mark"]["score"])
        for r in scored[:args.top]:
            wm = r["witness_mark"]
            print(f"    [{wm['grade']}] {wm['score']}/100 — {r['sha']} — {r['subject'][:60]}")

    if args.output:
        output = {"analysis": analysis, "commits": results}
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()
