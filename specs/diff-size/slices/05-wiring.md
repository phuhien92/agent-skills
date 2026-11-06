# 05: Wiring

**Question:** Do workers run it after each slice, does Reslice get the third trigger, does the PR handback carry the table, and does CI run the new tests?

**Seam:** docs and CI only:
- `skills/slice-spec/spec-format.md`: a **Size** line in the slice template (after the slice commit, run `diff_size.py . HEAD~1..HEAD`; over soft goes in the handback).
- `skills/slice-spec/SKILL.md`: Reslice's triggers gain "the slice's diff crossed soft"; the script is listed so the skill can find it.
- `ARCHITECTURE.md` loop section and `README.md`: before opening a PR, run it over the branch range and paste the table into the description.
- `evals/slice-spec.md`: one case where a slice commit lands over soft and the expected behaviour is to suggest Reslice, not to reslice.
- `.github/workflows/validate.yml`: run `skills/slice-spec/scripts` tests and `tools/` tests.

**Check:** `python3 tools/validate.py` reports no errors; `grep -l diff_size.py skills/slice-spec/spec-format.md skills/slice-spec/SKILL.md ARCHITECTURE.md README.md` lists all four; `grep -n "crossed soft" skills/slice-spec/SKILL.md` matches; the workflow lists both test commands and they pass locally.

**Must stay green:** every test from 02 to 04; `tools/validate.py`.

**Decided:**
- The PR handback instruction lives in ARCHITECTURE.md and the README, not in `decision-checker`, which stays about decisions.
- If agent-skills PR #9 (which also adds a `tools/` test step) merges first, keep one step for `tools/`, not two.

**Delegated to the worker:**
- Wording of every doc edit, and the eval case's text.

**Out of scope:**
- Any change to `decision-checker` or `codebase-rubric`.
