"""
Quill Skills Module — Skill Loader and Runner
=============================================
Loads skills from SKILLS/ directory.
Each skill is a folder with SKILL.md and optional src/ and tests/.

Zero dependencies — uses only stdlib.
"""

from pathlib import Path
from typing import Optional


class Skill:
    """A loaded skill module."""

    def __init__(self, name: str, path: Path, manifest: dict):
        self.name = name
        self.path = path
        self.manifest = manifest

    @property
    def description(self) -> str:
        return self.manifest.get("description", "")

    @property
    def version(self) -> str:
        return self.manifest.get("version", "0.0.0")

    def read_skill_md(self) -> Optional[str]:
        """Read the SKILL.md documentation."""
        skill_md = self.path / "SKILL.md"
        if skill_md.exists():
            return skill_md.read_text(encoding="utf-8")
        return None


class SkillLoader:
    """
    Loads and manages skill modules from the SKILLS/ directory.
    
    Usage:
        loader = SkillLoader(skills_dir="SKILLS/")
        skills = loader.list_skills()
        audit = loader.load("audit")
        print(audit.description)
    """

    def __init__(self, skills_dir: str = "SKILLS/"):
        self.skills_dir = Path(skills_dir)

    def list_skills(self) -> list:
        """List all installed skills."""
        if not self.skills_dir.exists():
            return []
        return [
            d.name for d in self.skills_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        ]

    def load(self, name: str) -> Optional[Skill]:
        """Load a skill by name."""
        skill_path = self.skills_dir / name
        if not skill_path.exists() or not (skill_path / "SKILL.md").exists():
            return None

        manifest = {
            "name": name,
            "description": self._extract_field(skill_path / "SKILL.md", "Description"),
            "version": self._extract_field(skill_path / "SKILL.md", "Version") or "0.0.0",
            "author": self._extract_field(skill_path / "SKILL.md", "Author"),
            "dependencies": self._extract_field(skill_path / "SKILL.md", "Dependencies"),
            "files": [f.name for f in skill_path.rglob("*") if f.is_file()],
        }

        return Skill(name, skill_path, manifest)

    def load_all(self) -> list:
        """Load all installed skills."""
        return [self.load(name) for name in self.list_skills()]

    def _extract_field(self, path: Path, field: str) -> Optional[str]:
        """Extract a field value from a SKILL.md frontmatter-like format."""
        if not path.exists():
            return None
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.lower().startswith(f"{field.lower()}:"):
                _, _, value = line.partition(":")
                return value.strip()
        return None
