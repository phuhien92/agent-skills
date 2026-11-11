"""validate.py's check_agents: a subagent wraps one skill, as a real file the plugin lists.

Run: python3 -m unittest discover -s tools
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AGENT = """---
name: {name}
description: Reviews a change.
tools: Read, Grep
---

Load the `{skill}` skill and follow it.
"""


def load_validate():
    spec = importlib.util.spec_from_file_location("validate", ROOT / "tools" / "validate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CheckAgentsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".claude" / "agents").mkdir(parents=True)
        (self.root / ".claude-plugin").mkdir()
        self.v = load_validate()
        self.v.ROOT = self.root

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_check(self, agents: list[str], files: dict[str, str]) -> list[str]:
        (self.root / ".claude-plugin" / "plugin.json").write_text(json.dumps({"agents": agents}))
        for rel, text in files.items():
            (self.root / rel).write_text(text)
        self.v.errors.clear()
        self.v.check_agents({"reviewer"})
        return self.v.errors

    def test_a_wired_agent_passes(self) -> None:
        errors = self.run_check(["./.claude/agents/reviewer.md"],
                                {".claude/agents/reviewer.md": AGENT.format(name="reviewer", skill="reviewer")})
        self.assertEqual(errors, [])

    def test_name_must_match_the_file(self) -> None:
        errors = self.run_check(["./.claude/agents/reviewer.md"],
                                {".claude/agents/reviewer.md": AGENT.format(name="other", skill="reviewer")})
        self.assertTrue(any("name is 'other'" in e for e in errors), errors)

    def test_agent_needs_a_matching_skill(self) -> None:
        errors = self.run_check(["./.claude/agents/stray.md"],
                                {".claude/agents/stray.md": AGENT.format(name="stray", skill="stray")})
        self.assertTrue(any("no matching skills/stray/" in e for e in errors), errors)

    def test_agent_must_load_its_skill(self) -> None:
        errors = self.run_check(["./.claude/agents/reviewer.md"],
                                {".claude/agents/reviewer.md": AGENT.format(name="reviewer", skill="something-else")})
        self.assertTrue(any("doesn't load the `reviewer` skill" in e for e in errors), errors)

    def test_agent_must_be_in_the_manifest(self) -> None:
        errors = self.run_check([], {".claude/agents/reviewer.md": AGENT.format(name="reviewer", skill="reviewer")})
        self.assertTrue(any("not in .claude-plugin/plugin.json" in e for e in errors), errors)

    def test_a_symlink_is_refused(self) -> None:
        real = self.root / "real.md"
        real.write_text(AGENT.format(name="reviewer", skill="reviewer"))
        (self.root / ".claude" / "agents" / "reviewer.md").symlink_to(real)
        errors = self.run_check(["./.claude/agents/reviewer.md"], {})
        self.assertTrue(any("is a symlink" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
