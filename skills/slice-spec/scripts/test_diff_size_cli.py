"""Tests for diff_size.py's report and CLI (slice 04 of specs/diff-size/).

Run: python3 -m unittest discover -s skills/slice-spec/scripts
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diff_size as d  # noqa: E402
from test_diff_size import Repo  # noqa: E402


def new_lines(n: int, tag: str) -> str:
    return "".join(f"value_{tag}_{i} = compute_distinct_value({i}, '{tag}')\n" for i in range(n))


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = d.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self.tmp.name))
        self.old_env = dict(os.environ)
        os.environ.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.repo.write("README.md", "start\n")
        self.base = self.repo.commit("start")

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_env)
        self.tmp.cleanup()

    def add(self, n: int, tag: str) -> str:
        self.repo.write(f"src/{tag}.py", new_lines(n, tag))
        return self.repo.commit(f"add {n} lines")

    def test_commit_tier_boundaries_and_warnings(self):
        expected = {}
        for n, tier in [(400, None), (401, "target"), (800, "target"), (801, "soft"),
                        (1500, "soft"), (1501, "hard")]:
            expected[self.add(n, f"t{n}")[:7]] = (n, tier)
        code, out, _ = run(str(self.repo.root), f"{self.base}..HEAD", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        got = {r["commit"]: (r["new"], r["tier"]) for r in data["commits"]}
        self.assertEqual(got, expected)
        self.assertEqual(data["total"]["new"], sum(n for n, _ in expected.values()))
        self.assertEqual(data["total"]["tier"], "hard")
        code, text, _ = run(str(self.repo.root), f"{self.base}..HEAD")
        self.assertEqual(code, 0)
        soft = [c for c, (_, t) in expected.items() if t == "soft"]
        hard = [c for c, (_, t) in expected.items() if t == "hard"]
        for c in soft:
            self.assertIn(f"`{c}` is over soft (800): consider Reslice.", text)
        for c in hard:
            self.assertIn(f"`{c}` is over hard (1500): reslice before review.", text)
        self.assertIn("The whole range is over hard (1500): split the goal.", text)

    def test_range_tier_boundaries(self):
        for n, tier, warned in [(400, None, False), (401, "target", False),
                                (801, "soft", True), (1501, "hard", True)]:
            with self.subTest(n=n):
                start = self.repo.commit(f"start {n}")
                self.add(n // 2, f"a{n}")
                self.add(n - n // 2, f"b{n}")
                code, out, _ = run(str(self.repo.root), f"{start}..HEAD", "--json")
                total = json.loads(out)["total"]
                self.assertEqual((code, total["new"], total["tier"]), (0, n, tier))
                _, text, _ = run(str(self.repo.root), f"{start}..HEAD")
                self.assertEqual("split the goal" in text, warned)

    def test_one_commit_has_no_range_row(self):
        commit = self.add(3, "one")
        code, out, _ = run(str(self.repo.root), commit, "--json")
        data = json.loads(out)
        self.assertEqual((code, len(data["commits"]), data["total"]), (0, 1, None))

    def test_text_output_is_deterministic_and_has_no_absolute_paths(self):
        self.add(3, "x")
        first = run(str(self.repo.root), f"{self.base}..HEAD")[1]
        second = run(str(self.repo.root), f"{self.base}..HEAD")[1]
        self.assertEqual(first, second)
        self.assertNotIn(str(self.repo.root), first)
        self.assertIn("| **Whole range** | diffed at once | **3** |", first)

    def test_pipe_in_a_subject_is_escaped(self):
        self.repo.write("src/p.py", new_lines(1, "p"))
        self.repo.commit("a | b")
        text = run(str(self.repo.root), f"{self.base}..HEAD")[1]
        self.assertIn("a \\| b", text)

    def test_bad_input_exits_2(self):
        cases = [(str(self.repo.root), "no-such..HEAD"), (str(self.repo.root), "nope"),
                 (str(Path(self.tmp.name) / "missing"), "HEAD"), (str(self.repo.root),)]
        for argv in cases:
            with self.subTest(argv=argv):
                code, out, err = run(*argv)
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(err)

    def test_not_a_repo_exits_2(self):
        with tempfile.TemporaryDirectory() as plain:
            code, _, err = run(plain, "HEAD")
            self.assertEqual(code, 2)
            self.assertIn("not a git repository", err)


if __name__ == "__main__":
    unittest.main()
