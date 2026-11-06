"""Tests for skill_metrics.py. Run: python3 -m unittest discover -s tools"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import skill_metrics  # noqa: E402

LEDGER = """# Decisions: demo

### First call
- **Slice:** 01
- **Verdict:** unsound. Redo from: x.
- **Confidence:** low

### Second call
- **Slice:** 02
- **Verdict:** sound, fine.
- **Confidence:** medium

# Check 2: later

### Third call
- **Slice:** 02, 03
- **Verdict:** needs-you. Recommended call: y.
- **Confidence:** medium
"""


def card(date: str, commit: str, scores: list[str]) -> str:
    rows = "\n".join(f"| {a} | {s} | src | 3 of 4 | `a.py:1` |" for a, s in zip(skill_metrics.AREAS, scores))
    return f"""# Codebase scorecard: demo
<!-- meta:start -->
| Key | Value |
|---|---|
| Repo | demo |
| Commit | {commit} |
| Date | {date} |
| Rubric approved | yes |
| Scorers independent | yes |
<!-- meta:end -->
<!-- scores:start -->
| Area | Score | Scope | Sample | Evidence |
|---|---|---|---|---|
{rows}
<!-- scores:end -->
"""


class SkillMetricsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        r = self.repo = Path(self.tmp.name)
        spec = r / "specs" / "feature"
        (spec / "slices").mkdir(parents=True)
        (spec / "README.md").write_text("# Feature\n")
        (spec / "slices" / "01-a.md").write_text("# 01: A\n")
        (spec / "slices" / "02-b.md").write_text("Replaced by 03, 04\n\n# 02: B\n")
        (spec / "slices" / "03-c.md").write_text("# 03: C\n")
        (spec / "decisions.md").write_text(LEDGER)
        sc = r / "scorecards"
        sc.mkdir()
        (sc / "2026-10-01.md").write_text(card("2026-10-01", "aaa", ["3", "3", "3", "3", "4"]))
        (sc / "2026-10-01-2.md").write_text(card("2026-10-01", "aaa", ["3", "2", "3", "3", "4"]))
        (sc / "2026-11-01.md").write_text(card("2026-11-01", "bbb", ["4", "4", "3", "not scored", "4"]))
        (sc / "2026-11-02.md").write_text("broken, no markers\n")
        (sc / "notes.md").write_text("ignored\n")
        (r / "node_modules" / "x" / "specs" / "y" / "slices").mkdir(parents=True)
        (r / "node_modules" / "x" / "decisions.md").write_text(LEDGER)
        copy = r / ".claude" / "worktrees" / "w" / "specs" / "feature"
        (copy / "slices").mkdir(parents=True)
        (copy / "README.md").write_text("# Feature\n")
        (r / "notes" / "decisions.md").mkdir(parents=True)
        (r / "skill-outcomes.md").write_text(
            "# Outcomes\n"
            "- 2026-11-02 | decision-checker | overruled | timeout was fine\n"
            "- 2026-11-03 | decision-checker | confirmed | caught the unused dep\n"
            "- 2026-11-04 | codebase-rubric | escaped | missed a god file\n"
            "- not a valid line\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_specs(self) -> None:
        specs = skill_metrics.collect(self.repo)["specs"]
        self.assertEqual([(s["spec"], s["slices"], s["resliced"]) for s in specs], [("feature", 3, 1)],
                         "copies under .claude/ must be skipped")

    def test_ledger(self) -> None:
        ledgers = skill_metrics.collect(self.repo)["ledgers"]
        self.assertEqual(len(ledgers), 1, "node_modules must be skipped")
        l = ledgers[0]
        self.assertEqual((l["runs"], l["entries"]), (2, 3))
        self.assertEqual(l["verdicts"], {"needs-you": 1, "sound": 1, "unsound": 1})
        self.assertEqual(l["confidence"], {"low": 1, "medium": 2})
        self.assertEqual(l["per_slice"], {"01": 1, "02": 2, "03": 1})

    def test_rubric(self) -> None:
        b = skill_metrics.collect(self.repo)["rubrics"][0]
        self.assertEqual((b["scorecards"], b["unreadable"]), (3, 1))
        self.assertEqual(b["noise"], 1)
        self.assertEqual(b["change"]["Modularity"], "3 → 4")
        self.assertEqual(b["change"]["Components"], "3 → not scored")

    def test_outcomes(self) -> None:
        self.assertEqual(skill_metrics.collect(self.repo)["outcomes"], {
            "codebase-rubric": {"escaped": 1},
            "decision-checker": {"confirmed": 1, "overruled": 1},
        })

    def test_run_headings(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "decisions.md"
            p.write_text("# Check 1: first\n\n### A\n- **Verdict:** sound\n")
            self.assertEqual(skill_metrics.ledger_stats(p)["runs"], 1)
            p.write_text("# Decisions\n\n### A\n- **Verdict:** sound\n\n## Check 3: later\n\n### B\n- **Verdict:** sound\n")
            self.assertEqual(skill_metrics.ledger_stats(p)["runs"], 3)

    def test_unknown_commit_is_not_noise(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sc = Path(d) / "scorecards"
            sc.mkdir()
            (sc / "2026-10-01.md").write_text(card("2026-10-01", "?", ["1", "1", "1", "1", "1"]))
            (sc / "2026-10-02.md").write_text(card("2026-10-02", "?", ["5", "5", "5", "5", "5"]))
            self.assertIsNone(skill_metrics.rubric_stats(sc)["noise"])

    def test_empty_repo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            text = skill_metrics.as_text([skill_metrics.collect(Path(d))])
            for line in ["- no specs", "- no ledgers", "- no scorecards", "- none logged"]:
                self.assertIn(line, text)

    def test_cli(self) -> None:
        script = HERE / "skill_metrics.py"
        run = lambda *a: subprocess.run([sys.executable, str(script), *a], capture_output=True)
        res = run(str(self.repo), "--json")
        self.assertEqual(res.returncode, 0)
        self.assertEqual(json.loads(res.stdout)[0]["ledgers"][0]["entries"], 3)
        text = run(str(self.repo)).stdout.decode()
        self.assertIn("2 runs, 3 entries", text)
        self.assertIn("noise 1", text)
        self.assertEqual(run(str(self.repo / "nope")).returncode, 2)
        self.assertEqual(run("--bogus").returncode, 2)


if __name__ == "__main__":
    unittest.main()
