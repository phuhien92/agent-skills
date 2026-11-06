# 06: Delta

**Question:** Since the last scorecard, which area scores changed and which files moved tiers?

**Seam:** `skills/codebase-rubric/scripts/delta.py <previous> <current>`, reading the marked tables from 05. Output: a delta section to paste into the current scorecard.

**Check:** `python3 -m unittest discover -s skills/codebase-rubric/scripts` passes with fixture pairs: a score change shows as "2 → 3"; a file crossing 800 shows in "moved tiers"; a new file over 500 and a file that dropped under 500 both show; no previous file prints "first run"; a previous file with missing markers exits 1 with a reason, never guesses.

**Must stay green:** 04 and 05 tests.

**Decided:**
- The previous scorecard is the newest file in `scorecards/` by name.

**Delegated to the worker:**
- Delta wording.

**Out of scope:**
- Trends over more than two scorecards.
