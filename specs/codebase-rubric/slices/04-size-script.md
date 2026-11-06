# 04: Size script

**Question:** Does a script put every source file into the right tier, deterministically, and skip the files it should?

**Seam:** `skills/codebase-rubric/scripts/size_report.py <repo> [--json]`. Input: a repo path. Output: files over 500 lines with their count and tier (over target, over soft, over hard), sorted by count, plus skip counts by reason. Uses `git ls-files` when the path is a git repo.

**Check:** `python3 -m unittest discover -s skills/codebase-rubric/scripts` passes. Fixtures in a temp dir: files of 499, 501, 801, and 1001 lines land in the right tiers (499 not listed); `package-lock.json`, `node_modules/x.js`, a `linguist-generated` file, a file with a generated header, and a binary file are skipped with reasons; two runs give byte-identical output.

**Must stay green:** `python3 tools/validate.py`, except the one expected "skills/codebase-rubric/ has no SKILL.md" error until 07 adds it. (Corrected during build: the validator treats every folder under `skills/` as a skill.)

**Decided:**
- Raw newline count of all lines. Skip rules as listed in the README under Decided in planning.
- Standard library only.

**Delegated to the worker:**
- The exact generated-header markers, and the text table layout.

**Out of scope:**
- Writing the scorecard (05) or comparing runs (06).
