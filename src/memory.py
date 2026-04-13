"""
Quill Memory Module — 3-Tier Keeper Memory
===========================================
Hot (2h TTL), Warm (7d TTL), Cold (permanent).
File-based, zero dependencies.

Inspired by Lucineer/git-agent's Keeper Memory pattern.
Each tier is a directory of JSON files keyed by timestamp.

Hot:   Last N heartbeat results, short TTL, auto-expired
Warm:  Rolling context, patterns detected, medium TTL
Cold:  Permanent lessons learned, key findings, never expired
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Any
from datetime import datetime, timezone
from collections import OrderedDict


class KeeperMemory:
    """
    3-tier file-based memory system.
    
    Usage:
        memory = KeeperMemory(base_path=".quill-memory")
        memory.remember("hot", "heartbeat_001", {"task": "audit", "result": "done"})
        memory.recall("hot", "heartbeat_001")  # {"task": "audit", "result": "done"}
        memory.expire()  # Clean up expired entries
    """

    def __init__(
        self,
        base_path: str = ".quill-memory",
        hot_ttl: int = 7200,       # 2 hours
        warm_ttl: int = 604800,    # 7 days
        hot_max: int = 50,         # Max hot entries
        warm_max: int = 200,       # Max warm entries
    ):
        self.base = Path(base_path)
        self.hot_ttl = hot_ttl
        self.warm_ttl = warm_ttl
        self.hot_max = hot_max
        self.warm_max = warm_max

        for tier in ("hot", "warm", "cold"):
            (self.base / tier).mkdir(parents=True, exist_ok=True)

    def _tier_path(self, tier: str) -> Path:
        """Get path for a memory tier."""
        if tier not in ("hot", "warm", "cold"):
            raise ValueError(f"Invalid tier: {tier}. Use hot, warm, or cold.")
        return self.base / tier

    def _entry_path(self, tier: str, key: str) -> Path:
        """Get file path for a memory entry."""
        # Sanitize key for use as filename
        safe_key = key.replace("/", "_").replace(" ", "_").replace("\\", "_")
        if not safe_key:
            safe_key = "unnamed"
        return self._tier_path(tier) / f"{safe_key}.json"

    def remember(self, tier: str, key: str, value: Any) -> Path:
        """
        Store a value in a memory tier.
        
        Args:
            tier: "hot", "warm", or "cold"
            key: Unique identifier for this memory
            value: Any JSON-serializable value
        
        Returns:
            Path to the stored file
        """
        entry = {
            "key": key,
            "tier": tier,
            "created": datetime.now(timezone.utc).isoformat(),
            "value": value,
        }

        path = self._entry_path(tier, key)
        path.write_text(json.dumps(entry, indent=2, default=str), encoding="utf-8")

        # Enforce max entry counts for hot and warm
        if tier in ("hot", "warm"):
            self._enforce_limit(tier)

        return path

    def recall(self, tier: str, key: str) -> Optional[Any]:
        """
        Recall a value from memory. Returns None if not found or expired.
        """
        path = self._entry_path(tier, key)
        if not path.exists():
            return None

        try:
            entry = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

        # Check TTL for hot and warm
        if tier in ("hot", "warm"):
            ttl = self.hot_ttl if tier == "hot" else self.warm_ttl
            created = datetime.fromisoformat(entry["created"])
            age = (datetime.now(timezone.utc) - created).total_seconds()
            if age > ttl:
                path.unlink(missing_ok=True)
                return None

        return entry.get("value")

    def recall_all(self, tier: str) -> list:
        """Recall all entries from a tier. Returns list of (key, value, age_seconds)."""
        results = []
        tier_path = self._tier_path(tier)

        for path in sorted(tier_path.glob("*.json")):
            try:
                entry = json.loads(path.read_text(encoding="utf-8"))
                created = datetime.fromisoformat(entry["created"])
                age = (datetime.now(timezone.utc) - created).total_seconds()

                # Check TTL
                if tier in ("hot", "warm"):
                    ttl = self.hot_ttl if tier == "hot" else self.warm_ttl
                    if age > ttl:
                        path.unlink(missing_ok=True)
                        continue

                results.append({
                    "key": entry.get("key", path.stem),
                    "value": entry.get("value"),
                    "age_seconds": int(age),
                    "created": entry.get("created"),
                })
            except (json.JSONDecodeError, OSError):
                continue

        return results

    def forget(self, tier: str, key: str) -> bool:
        """Delete a specific memory entry. Returns True if deleted."""
        path = self._entry_path(tier, key)
        if path.exists():
            path.unlink()
            return True
        return False

    def expire(self) -> dict:
        """
        Clean up expired entries across all tiers.
        Returns counts: {"hot": N, "warm": N, "cold": 0}
        """
        counts = {"hot": 0, "warm": 0, "cold": 0}

        for tier in ("hot", "warm"):
            for path in self._tier_path(tier).glob("*.json"):
                try:
                    entry = json.loads(path.read_text(encoding="utf-8"))
                    created = datetime.fromisoformat(entry["created"])
                    ttl = self.hot_ttl if tier == "hot" else self.warm_ttl
                    age = (datetime.now(timezone.utc) - created).total_seconds()
                    if age > ttl:
                        path.unlink()
                        counts[tier] += 1
                except (json.JSONDecodeError, OSError, ValueError):
                    path.unlink()
                    counts[tier] += 1

        return counts

    def learn(self, lesson: str, context: str = "") -> Path:
        """
        Promote a lesson to cold (permanent) storage.
        Extracts a key from the lesson text for deduplication.
        """
        key = lesson[:60].replace(" ", "_").lower()
        # Check if similar lesson already exists
        for existing in self.recall_all("cold"):
            if key in existing["key"]:
                return self._entry_path("cold", existing["key"])
        return self.remember("cold", key, {
            "lesson": lesson,
            "context": context,
            "learned": datetime.now(timezone.utc).isoformat(),
        })

    def stats(self) -> dict:
        """Get memory statistics across all tiers."""
        return {
            tier: {
                "count": len(list(self._tier_path(tier).glob("*.json"))),
                "ttl": self.hot_ttl if tier == "hot" else self.warm_ttl if tier == "warm" else None,
                "max": self.hot_max if tier == "hot" else self.warm_max if tier == "warm" else None,
            }
            for tier in ("hot", "warm", "cold")
        }

    def recent_context(self, max_entries: int = 10) -> str:
        """
        Build a context string from recent hot + warm memories.
        Useful for injecting into LLM prompts.
        """
        parts = []

        hot = self.recall_all("hot")[-5:]
        warm = self.recall_all("warm")[-5:]

        if hot:
            parts.append("## Recent Activity (Hot Memory)")
            for entry in hot:
                parts.append(f"- {entry['key']}: {str(entry['value'])[:100]}")

        if warm:
            parts.append("## Recent Patterns (Warm Memory)")
            for entry in warm:
                parts.append(f"- {entry['key']}: {str(entry['value'])[:100]}")

        return "\n".join(parts) if parts else ""

    def _enforce_limit(self, tier: str):
        """Remove oldest entries when tier exceeds max count."""
        max_count = self.hot_max if tier == "hot" else self.warm_max
        tier_path = self._tier_path(tier)
        entries = sorted(tier_path.glob("*.json"), key=lambda p: p.stat().st_mtime)

        while len(entries) > max_count:
            entries[0].unlink(missing_ok=True)
            entries = entries[1:]
