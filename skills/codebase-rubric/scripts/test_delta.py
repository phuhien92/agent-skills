"""Tests for delta.py. Run: python3 -m unittest discover -s skills/codebase-rubric/scripts"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import delta  # noqa: E402
from check_scorecard import ContractError, problems  # noqa: E402

GOOD = (HERE / "fixtures" / "good-keen.md").read_text(encoding="utf-8")
HEADER = "|---|---|---|\n"


def with_size(text: str, rows: list[str]) -> str:
    return text.replace(HEADER, HEADER + "".join(r + "\n" for r in rows), 1)


PREV = with_size(GOOD.replace("| Date | 2026-11-06 |", "| Date | 2026-11-01 |").replace("| Commit | 847e726 |", "| Commit | aaa1111 |"), [
    "| `src/cli.ts` | 950 | over soft (800) |",
    "| `src/old.ts` | 540 | over target (500) |",
    "| `src/same.ts` | 600 | over target (500) |",
])
CUR = with_size(GOOD.replace("| Abstraction | 3 |", "| Abstraction | 4 |"), [
    "| `src/cli.ts` | 1050 | over hard (1000) |",
    "| `src/new.ts` | 620 | over target (500) |",
    "| `src/same.ts` | 610 | over target (500) |",
])


class DeltaTest(unittest.TestCase):
    def test_fixtures_are_valid_scorecards(self) -> None:
        self.assertEqual(problems(PREV), [])
        self.assertEqual(problems(CUR), [])

    def test_score_change(self) -> None:
        out = delta.delta(PREV, CUR)
        self.assertIn("Since 2026-11-01 (`aaa1111`):", out)
        self.assertIn("- Abstraction: 3 → 4", out)
        self.assertIn("Unchanged: Architecture 4, Modularity 4, Components 4, Errors 3", out)

    def test_tier_moves(self) -> None:
        out = delta.delta(PREV, CUR)
        self.assertIn("- `src/cli.ts`: over soft (800) → over hard (1000) (950 → 1050 lines)", out)
        self.assertIn("- New over 500: `src/new.ts` (620 lines, over target (500))", out)
        self.assertIn("- Now under 500 or gone: `src/old.ts` (was 540 lines)", out)
        self.assertNotIn("same.ts", out)

    def test_nothing_changed(self) -> None:
        out = delta.delta(GOOD, GOOD)
        self.assertIn("- No score changed.", out)
        self.assertIn("- No file changed tier.", out)

    def test_not_scored_transition(self) -> None:
        line = next(l for l in GOOD.splitlines() if l.startswith("| Components |"))
        cur = GOOD.replace(line, "| Components | not scored | packages/keen | - | only one component |")
        self.assertIn("- Components: 4 → not scored", delta.delta(GOOD, cur))

    def test_first_run(self) -> None:
        self.assertEqual(delta.delta(None, GOOD), "First run.")

    def test_missing_marker_refuses(self) -> None:
        broken = PREV.replace("<!-- scores:end -->", "")
        with self.assertRaises(ContractError):
            delta.delta(broken, CUR)

    def test_previous_in_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            for name in ["2026-10-01.md", "2026-11-06.md", "2026-11-06-2.md", "2026-11-06-10.md", "notes.md"]:
                (folder / name).write_text(GOOD)
            self.assertEqual(delta.previous_in(folder, folder / "2026-11-06-10.md").name, "2026-11-06-2.md")
            self.assertEqual(delta.previous_in(folder, folder / "2026-11-06-2.md").name, "2026-11-06.md")
            self.assertEqual(delta.previous_in(folder, folder / "2026-11-06.md").name, "2026-10-01.md")
            self.assertIsNone(delta.previous_in(folder, folder / "2026-10-01.md"))
            with self.assertRaises(ContractError):
                delta.previous_in(folder, folder / "notes.md")

    def test_cli(self) -> None:
        script = HERE / "delta.py"
        run = lambda *a: subprocess.run([sys.executable, str(script), *a], capture_output=True)
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            (folder / "2026-11-01.md").write_text(PREV)
            (folder / "2026-11-06.md").write_text(CUR)
            res = run("--dir", str(folder), str(folder / "2026-11-06.md"))
            self.assertEqual(res.returncode, 0)
            self.assertIn("Abstraction: 3 → 4", res.stdout.decode())
            first = run("--dir", str(folder), str(folder / "2026-11-01.md"))
            self.assertEqual(first.stdout.decode().strip(), "First run.")
            (folder / "2026-10-01.md").write_text(PREV.replace("<!-- size:start -->", ""))
            bad = run(str(folder / "2026-10-01.md"), str(folder / "2026-11-06.md"))
            self.assertEqual(bad.returncode, 1)
            self.assertIn(b"size:start", bad.stderr)
            self.assertEqual(run("one-arg").returncode, 2)


if __name__ == "__main__":
    unittest.main()
