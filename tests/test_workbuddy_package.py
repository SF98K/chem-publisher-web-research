"""Offline package checks for the Tencent WorkBuddy distribution."""

import subprocess
import sys
import unittest
from pathlib import Path


PACKAGE = Path(__file__).parents[1] / "workbuddy" / "chem-publisher-web-research"
VALIDATOR = PACKAGE / "scripts" / "validate.py"


class WorkBuddyPackageTests(unittest.TestCase):
    def test_required_workbuddy_layout_and_frontmatter(self):
        required = [
            "SKILL.md",
            "references/batch-doi.md",
            "references/publishers.md",
            "scripts/prepare_doi_batch.py",
            "scripts/record_doi_result.py",
            "scripts/validate.py",
        ]
        for relative in required:
            self.assertTrue((PACKAGE / relative).is_file(), relative)
        frontmatter = (PACKAGE / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
        for field in ("name:", "description:", "description_zh:", "description_en:", "version:", "author:"):
            self.assertIn(field, frontmatter)

    def test_package_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--skill-root", str(PACKAGE)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("WorkBuddy package checks passed", result.stdout)

    def test_distributed_scripts_match_tested_sources(self):
        for name in ("prepare_doi_batch.py", "record_doi_result.py"):
            self.assertEqual((PACKAGE / "scripts" / name).read_bytes(), (PACKAGE.parents[1] / "scripts" / name).read_bytes())

    def test_documented_recorder_flags_exist(self):
        import re
        result = subprocess.run([sys.executable, str(PACKAGE / "scripts/record_doi_result.py"), "--help"], capture_output=True, text=True, check=True)
        for relative in ("SKILL.md", "references/batch-doi.md"):
            text = (PACKAGE / relative).read_text(encoding="utf-8")
            for line in text.splitlines():
                if line.startswith("python3 scripts/record_doi_result.py"):
                    for flag in re.findall(r"--[a-z-]+", line):
                        self.assertIn(flag, result.stdout)


if __name__ == "__main__":
    unittest.main()
