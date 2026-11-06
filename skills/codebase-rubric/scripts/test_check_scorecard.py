"""Tests for check_scorecard.py. Run: python3 -m unittest discover -s skills/codebase-rubric/scripts"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import check_scorecard  # noqa: E402

GOOD = (HERE / "fixtures" / "good-keen.md").read_text(encoding="utf-8")


def problems(text: str) -> list[str]:
    return check_scorecard.problems(text)


class CheckScorecardTest(unittest.TestCase):
    def test_good_fixture_passes(self) -> None:
        self.assertEqual(problems(GOOD), [])

    def test_missing_area(self) -> None:
        bad = "\n".join(l for l in GOOD.splitlines() if not l.startswith("| Components |"))
        self.assertTrue(any("areas must be" in p for p in problems(bad)))

    def test_score_out_of_range(self) -> None:
        bad = GOOD.replace("| Architecture | 4 |", "| Architecture | 7 |")
        self.assertTrue(any("Architecture score must be 1-5" in p for p in problems(bad)))

    def test_score_without_citation(self) -> None:
        bad = GOOD.replace("`tools/token-generator/src/gates.ts:168` casts", "callers cast")
        self.assertTrue(any("Abstraction evidence has no `path:line`" in p for p in problems(bad)))

    def test_bad_sample(self) -> None:
        bad = GOOD.replace("| 7 of 10 |", "| most |")
        self.assertTrue(any("Components sample" in p for p in problems(bad)))

    def test_sample_counts_must_make_sense(self) -> None:
        bad = GOOD.replace("| 7 of 10 |", "| 9 of 3 |")
        self.assertTrue(any("N <= M" in p for p in problems(bad)))

    def test_size_rows_checked(self) -> None:
        row = "| `src/big.ts` | 1200 | over hard (1000) |\n"
        ok = GOOD.replace("|---|---|---|\n", "|---|---|---|\n" + row, 1)
        self.assertEqual(problems(ok), [])
        bad = ok.replace("| 1200 | over hard (1000) |", "| 700 | over hard (1000) |")
        self.assertTrue(any("src/big.ts has 700 lines" in p for p in problems(bad)))
        no_skip = GOOD.replace("Skipped: generated header: 4, lockfile: 2, not a code file: 61\n", "")
        self.assertTrue(any("Skipped:" in p for p in problems(no_skip)))

    def test_missing_trace(self) -> None:
        start = GOOD.index("<!-- trace:start -->") + len("<!-- trace:start -->")
        end = GOOD.index("<!-- trace:end -->")
        bad = GOOD[:start] + "\n" + GOOD[end:]
        self.assertTrue(any("trace: needs at least 2 hops" in p for p in problems(bad)))

    def test_lost_marker(self) -> None:
        bad = GOOD.replace("<!-- scores:end -->", "")
        self.assertTrue(any("scores:" in p and "missing" in p for p in problems(bad)))

    def test_not_scored_needs_scope_and_reason(self) -> None:
        ok = GOOD.replace(
            "| Components | 4 | token-generator and Icon | 7 of 10 | `tools/token-generator/src/boundary.ts:33` with a one-string test |",
            "| Components | not scored | packages/keen | - | only one component exists |")
        self.assertEqual(problems(ok), [])
        bad = ok.replace("| not scored | packages/keen | - | only one component exists |",
                         "| not scored | - | - | - |")
        found = problems(bad)
        self.assertTrue(any("names no scope" in p for p in found))
        self.assertTrue(any("gives no reason" in p for p in found))

    def test_errors_not_scored_skips_trace(self) -> None:
        start = GOOD.index("<!-- trace:start -->") + len("<!-- trace:start -->")
        end = GOOD.index("<!-- trace:end -->")
        bad = (GOOD[:start] + "\n" + GOOD[end:]).replace(
            "| Errors | 3 | token-generator CLI | 5 of 9 | `tools/token-generator/src/resolve.ts:32` names the token but not its file |",
            "| Errors | not scored | packages/keen | - | no failure path a person can reach |")
        self.assertEqual(problems(bad), [])

    def test_meta_flags(self) -> None:
        bad = GOOD.replace("| Rubric approved | yes |", "| Rubric approved | maybe |")
        self.assertTrue(any("Rubric approved must be yes or no" in p for p in problems(bad)))

    def test_cli_exit_codes(self) -> None:
        script = HERE / "check_scorecard.py"
        with tempfile.TemporaryDirectory() as d:
            good, bad = Path(d) / "good.md", Path(d) / "bad.md"
            good.write_text(GOOD)
            bad.write_text(GOOD.replace("| Architecture | 4 |", "| Architecture | 9 |"))
            run = lambda p: subprocess.run([sys.executable, str(script), str(p)], capture_output=True)
            self.assertEqual(run(good).returncode, 0)
            res = run(bad)
            self.assertEqual(res.returncode, 1)
            self.assertIn(b"Architecture score", res.stdout)
            self.assertEqual(run(Path(d) / "missing.md").returncode, 2)


if __name__ == "__main__":
    unittest.main()
