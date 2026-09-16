#!/usr/bin/env python3
"""Offline structural checks for the WorkBuddy Skill package."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
import sys

REQUIRED_FILES = ("SKILL.md", "references/batch-doi.md", "references/publishers.md", "scripts/prepare_doi_batch.py", "scripts/record_doi_result.py")
REQUIRED_FIELDS = ("name", "description", "description_zh", "description_en", "version", "author")

def parse_frontmatter(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must begin with YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("SKILL.md frontmatter is not closed")
    values: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values

def validate(skill_root: Path) -> list[str]:
    errors = [f"Missing required file: {relative}" for relative in REQUIRED_FILES if not (skill_root / relative).is_file()]
    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        return errors
    try:
        fields = parse_frontmatter(skill_file)
    except ValueError as error:
        return errors + [str(error)]
    for field in REQUIRED_FIELDS:
        if not fields.get(field):
            errors.append(f"Missing or empty frontmatter field: {field}")
    if fields.get("name") != "chem-publisher-web-research":
        errors.append("Frontmatter name must be chem-publisher-web-research")
    body = skill_file.read_text(encoding="utf-8")
    for reference in ("@references/publishers.md", "@references/batch-doi.md"):
        if reference not in body:
            errors.append(f"SKILL.md does not reference {reference}")
    for relative in ("scripts/prepare_doi_batch.py", "scripts/record_doi_result.py"):
        script = skill_root / relative
        if script.is_file():
            try:
                ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
            except SyntaxError as error:
                errors.append(f"Python syntax error in {relative}: {error}")
    return errors

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.skill_root)
    if errors:
        print("WorkBuddy package checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("WorkBuddy package checks passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
