"""Fails when diff_size.py's copy of the skip rules drifts from size_report.py's.

slice-spec's diff_size.py copies codebase-rubric's skip rules so each skill installs on
its own (specs/diff-size/). Edit both copies together.
Run: python3 -m unittest discover -s tools
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ["LOCKFILES", "ANY_DEPTH_DIRS", "ROOT_BUILD_DIRS", "PACKAGE_MARKERS", "CODE_EXTENSIONS",
          "CODE_NAMES", "SKIP_LABELS", "GENERATED_MARKERS", "HEADER_LINES", "SNIFF_BYTES"]
SAMPLE_PATHS = ["a.py", "A.TSX", "Makefile", "x/Dockerfile", "notes.md", "data.json",
                "style.scss", "page.mdx", "img.png", "Cargo.lock", "run.sh", "README"]


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look their module up while it loads
    spec.loader.exec_module(module)
    return module


class SkipRulesDriftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.size_report = load("size_report", "skills/codebase-rubric/scripts/size_report.py")
        cls.diff_size = load("diff_size", "skills/slice-spec/scripts/diff_size.py")

    def test_rule_data_matches(self):
        for name in SHARED:
            with self.subTest(name=name):
                self.assertEqual(getattr(self.diff_size, name), getattr(self.size_report, name),
                                 f"{name} differs: edit both copies together")

    def test_is_code_agrees(self):
        for path in SAMPLE_PATHS:
            with self.subTest(path=path):
                self.assertEqual(self.diff_size.is_code(path), self.size_report.is_code(path))

    def test_skip_reason_agrees_on_content_rules(self):
        tree = set()
        for path, head in [("a.py", b"x = 1\n"), ("a.py", b"\0bin"), ("a.py", b"# @generated\n"),
                           ("yarn.lock", b""), ("a.md", b""), ("vendor/a.py", b""), ("dist/a.py", b"")]:
            with self.subTest(path=path, head=head):
                self.assertEqual(self.diff_size.skip_reason(path, head, set(), tree),
                                 self.size_report.skip_reason(ROOT / "no-such-dir", path, head, set()))


if __name__ == "__main__":
    unittest.main()
