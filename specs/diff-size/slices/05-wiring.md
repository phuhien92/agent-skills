# 05: Wiring

**Question:** Does Interview split an over-soft goal into PRs, do workers run it after each slice, does Reslice get the size triggers, does the PR handback carry the table, and does CI run the new tests?

**Seam:** docs and CI only:
- `skills/slice-spec/spec-format.md` (also): a **Size** line in the slice template (after the slice commit, run `diff_size.py . HEAD~1..HEAD`; over soft goes in the handback).
- `skills/slice-spec/SKILL.md`:
  - Interview step 4 (or a new step after it): estimate each slice's new lines; when the total is over soft, split the goal into sub-goals, one PR each, each shippable on its own and leaving `main` working.
  - Reslice's triggers gain "the slice's diff crossed soft" and "the branch's running total crossed soft" (the second suggests moving the remaining slices to a follow-up PR).
  - The script is listed so the skill can find it.
- `skills/slice-spec/spec-format.md`: the slice-graph table gets a **PR** column, and a rule that a slice belongs to exactly one PR.
- `ARCHITECTURE.md` loop section and `README.md`: before opening a PR, run it over the branch range and paste the table into the description.
- `evals/slice-spec.md`: three cases: a goal whose slices estimate over soft is planned as two or more PRs; a slice commit over soft gets a Reslice suggestion, not a reslice; a branch total over soft gets a follow-up-PR suggestion, not a move.
- `.github/workflows/validate.yml`: run `skills/slice-spec/scripts` tests and `tools/` tests.

**Check:** `python3 tools/validate.py` reports no errors; `grep -l diff_size.py skills/slice-spec/spec-format.md skills/slice-spec/SKILL.md ARCHITECTURE.md README.md` lists all four; `grep -n "crossed soft" skills/slice-spec/SKILL.md` matches twice; `grep -n "| PR |" skills/slice-spec/spec-format.md` matches; `evals/slice-spec.md` has the three new cases; the workflow lists both test commands and they pass locally.

**Must stay green:** every test from 02 to 04; `tools/validate.py`.

**Decided:**
- The PR handback instruction lives in ARCHITECTURE.md and the README, not in `decision-checker`, which stays about decisions.
- If agent-skills PR #9 (which also adds a `tools/` test step) merges first, keep one step for `tools/`, not two.

**Delegated to the worker:**
- Wording of every doc edit, and the eval case's text.

**Out of scope:**
- Any change to `decision-checker` or `codebase-rubric`.
