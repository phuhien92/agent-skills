"""validate.py's check_command: a command's description must say when to use the skill.

Run: python3 -m unittest discover -s tools
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

COMMAND = """---
description: {desc}
---

Follow the `demo` skill.
"""


def load_validate():
    spec = importlib.util.spec_from_file_location("validate", ROOT / "tools" / "validate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckCommandTriggerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".claude" / "commands").mkdir(parents=True)
        self.v = load_validate()
        self.v.ROOT = self.root

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def warnings_for(self, desc: str) -> list[str]:
        rel = ".claude/commands/demo.md"
        (self.root / rel).write_text(COMMAND.format(desc=desc))
        self.v.warnings.clear()
        self.v.check_command("demo", rel)
        return self.v.warnings

    def test_a_description_with_a_trigger_passes(self) -> None:
        for desc in ("Do a thing. Use when the user asks for it.",
                     "Check it. Use proactively BEFORE opening a PR.",
                     "Score it. Use for a periodic check.",
                     "Summon help when the user runs /demo."):
            with self.subTest(desc=desc):
                self.assertEqual(self.warnings_for(desc), [])

    def test_a_description_without_a_trigger_warns_with_a_fix(self) -> None:
        warnings = self.warnings_for("Check the decisions an agent made, not its diff.")
        self.assertEqual(len(warnings), 1, warnings)
        self.assertIn("no trigger", warnings[0])
        self.assertIn("skills/demo/SKILL.md", warnings[0])

    def test_every_shipped_command_has_a_trigger(self) -> None:
        self.v.ROOT = ROOT
        self.v.warnings.clear()
        for folder in (".claude/commands", "commands", ".cursor/commands"):
            for f in sorted((ROOT / folder).glob("*.md")):
                self.v.check_command(f.stem, f"{folder}/{f.name}")
        self.assertEqual([w for w in self.v.warnings if "no trigger" in w], [])


if __name__ == "__main__":
    unittest.main()
