# 04: Report and CLI

**Question:** Does `diff_size.py <range>` print the per-commit table with tiers, the PR sum line and `--json`, and reproduce the spike on #27?

**Seam:** the CLI `diff_size.py <repo> <range> [--json]`. Input: a git range (`A..B`, or one commit). Output: a markdown table, one row per commit oldest first (short hash, subject, new, moved, deleted, tier), skip counts by reason, a PR sum line tiered on the same numbers (over soft: "split the goal"), and a one-line note on what "moved" can miss. `--json` mirrors `size_report.py`'s style.

**Check:** `python3 -m unittest discover -s skills/slice-spec/scripts` passes with golden-output tests for tier boundaries (399 → none, 401 → over target, 801 → over soft with "consider Reslice", 1,501 → over hard with "reslice before review"; the same boundaries on the PR sum line, with "split the goal" over soft), exit 0 in all of them, and exit 2 on an unknown range or a non-repo. Then `diff_size.py /home/user/brain-cli ea9b3ed~1..f6f554a` matches the spike table's locked-setting column within the difference the filter explains (`dist/` was a pathspec in 01; here it is a skip rule). Then the user spot-checks `138fb64` (or another commit they pick) and accepts or rejects its "new" count; recorded in `decisions.md`.

**Must stay green:** 02 and 03 tests; codebase-rubric's tests; `tools/validate.py`.

**Decided:**
- Tiers are the numbers locked in 01, for each commit and for the PR sum. Over-hard is still exit 0.
- The PR sum is the new lines of the whole range diffed at once, not the sum of commit rows, so a move spread across commits counts as moved there. The output says which.
- Output is deterministic: no timestamps, no absolute paths.

**Delegated to the worker:**
- Column order and wording, and the exact `--json` field names.

**Out of scope:**
- Docs and CI (05).
