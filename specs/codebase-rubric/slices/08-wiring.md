# 08: Wiring

**Question:** Is the skill registered everywhere the pack expects, evaluated, and tested in CI?

**Seam:** the three command files, the `.cursor/skills` symlink, `README.md`, `AGENTS.md`, plugin descriptions, `evals/codebase-rubric.md`, `.github/workflows/validate.yml`, and the Verify row plus a decision entry in `ARCHITECTURE.md`.

**Check:** `python3 tools/validate.py` reports 0 errors and 0 warnings; `python3 -m unittest discover -s skills/codebase-rubric/scripts` passes and is a step in `validate.yml`; `grep -r "—" skills/codebase-rubric` finds nothing; the eval file has at least 3 cases (no-evidence score fails, untested failure not triggered, only the scorecard is written).

**Must stay green:** everything above.

**Decided:**
- Verify row in `ARCHITECTURE.md` changes from "rule, not yet a block" to the new skill.

**Delegated to the worker:**
- README placement and wording.

**Out of scope:**
- Any change to other skills.
