# Check 1: slice 01 spike

- **Scope:** commit `3d30961` on `claude/diff-size` (`specs/diff-size/spikes/pr27.py`, `spikes/pr27.md`, one line in `slices/04-report-cli.md`).
- **Baseline:** `specs/diff-size/README.md` and `slices/01-spike-pr27.md`. Run by another workflow with no user present (rule 7): every confidence is capped at medium, and the slice 01 user gate (lock tiers and whitespace setting) is still open.
- **Self-report:** missing. The implementer is not live and left no report beyond the commit message, so this ledger rests on an independent trace.
- **Tests:** `python3 tools/validate.py` passes (7 skills, 0 errors). brain-cli is untouched (clean status).

## Reproduction

An independent counter (different pinned colours, a line's first colour code instead of a substring match, hunk-aware header detection, and a `git diff --numstat` cross-check of the totals) reproduced every number checked:

- `138fb64`: 513 / 127 / 532 default, 171 / 469 / 532 indent-insensitive. new + moved = 640 = numstat added.
- `fc3f4a6`: 166 / 160 / 321 and 78 / 248 / 321.
- `ea9b3ed~1..f6f554a`: 996 / 734 / 1407 and 476 / 1254 / 1407. new + moved = 1730 = numstat added.
- No added or removed content line in any of these diffs starts with `++` or `--`, so the `+++`/`---` skip did not drop anything here. There are no renames in the range, and zebra mode never emits dimmed colours, so neither could miscount.
- For the user's gate, not a worker decision: the slice itself chose `--color-moved=zebra`, whose 20-alphanumeric-character block floor matters. `--color-moved=plain` gives `138fb64` 133 new (not 171) and the range 392 (not 476), indent-insensitive.

What does not reproduce is the interpretation in two places, below.

## Check these first

1. The "whole PR" row is not the whole PR.
2. The per-commit vs whole-range finding is reversed, and slice 04 now cites it.
3. The README's next-agent prompt was not updated.

## Needs you

### The "deleted" column counts moved-out lines as deleted

- **When:** `3d30961`, `pr27.py` `count()`.
- **Slice:** 01
- **What happens now:** in `138fb64`, 469 lines are moved out of `cli.ts` into `src/commands/`. The spike reports 532 deleted, which includes those 469 moved-out lines. So the same relocated line shows once as moved (on the added side) and once as deleted. The obvious alternative reports only lines that were removed and not moved (about 63 here), so the three columns add up to the actual churn without double counting.
- **The gap:** the README says "moved and deleted lines are reported, not tiered" but never defines whether a moved-out line counts as deleted.
- **Reach:** slice 02's classifier and slice 04's table will copy whichever definition the spike used. A reader seeing "171 new / 469 moved / 532 deleted" may think 532 lines of behaviour were removed.
- **Verdict:** needs-you. It only changes a reported column, but what a reviewer reads into it is a product call. **Recommended call:** in 02, report deleted as removed-and-not-moved, and say so in the output note. **To reverse:** count every `-` line as deleted, as the spike does now.
- **Confidence:** medium.

### A pure rename counts as zero lines, not as moved

- **When:** `3d30961`, `pr27.py` passes `-M`.
- **Slice:** 01
- **What happens now:** with `-M`, a file renamed without changes produces no `+` or `-` lines, so it counts 0 new / 0 moved / 0 deleted. A probe repo with a 50-line file renamed and one line appended counts 1 new, 0 moved. #27 has no renames, so the spike's numbers are unaffected, but nothing tested this case. The README's planning notes say "renames counted as moved", which suggests a renamed file's lines should show up in the moved column. Without `-M`, the same rename shows as a full delete plus a full add, coloured as moved.
- **The gap:** the slice didn't say whether to pass `-M`. The README's "renames counted as moved" doesn't say whether "counted" means "not new" or "shown in the moved column".
- **Reach:** slice 02 decides rename handling. If it copies `-M` silently, a PR that renames a directory reports almost nothing moved.
- **Verdict:** needs-you. Both readings keep renames out of "new", which is the tiered number. **Recommended call:** keep `-M` and add a renamed-file line count to the moved column in 02, with a temp-repo test. **To reverse:** drop the added count and leave renames at zero.
- **Confidence:** medium.

## Unsound

### The "whole PR" row is not the whole PR

- **When:** `3d30961`, `pr27.py` `main()` and the `whole PR` row in `pr27.md`.
- **Slice:** 01
- **What happens now:** the row diffs `ea9b3ed~1..f6f554a`, the span of the seven slice commits. That span also holds two commits that are not in the table: `490a7fd` (3 lines of AGENTS.md) and `5ddb658` (a 71-line scorecard). It leaves out the four commits before slice 02 that are also on the branch (`fbf78f7`, `d1ca4c4`, `5390bbf`, `030ddec`). The branch against its merge-base with `main` (`7045e68..f6f554a`) measures 538 / 1254 / 1407 indent-insensitive, not 476. Of the 476 "new" lines in the row, 74 are markdown. The "Result" bullets then tier "the whole PR" on 476.
- **The gap:** the slice named seven commits but did not say what range the PR total uses. The label "whole PR" claims more than the range shows.
- **Reach:** slice 04's check compares the real script against this row, and the README already quotes "#27 as a whole measures 476 new". A PR total computed from the wrong range teaches 04 to take the first slice commit's parent as the base.
- **Verdict:** unsound. A label is wrong about what the number measures. **Redo from:** the PR-total row's range is the PR's own range (merge-base with `main` to head), or the row is labelled as the slice-commit span and its extra commits are listed.
- **Confidence:** low.

### The per-commit vs whole-range finding is reversed, and slice 04 now cites it

- **When:** `3d30961`, the third "Result" bullet in `pr27.md` and the edited "Decided" line in `slices/04-report-cli.md`.
- **Slice:** 01
- **What happens now:** the spike compares the seven rows' sum (447 new) with the range (476) and concludes that the whole range counts more as new, because code added in one commit and moved later "never existed on the base". But the range also holds the two unlisted commits' 74 new lines. Summing all nine commits in the range gives 521 new / 1408 moved / 1606 deleted. Against that, the range (476 / 1254 / 1407) counts fewer lines as new, not more. That fits the plan's original reason: a move spread across commits shows as moved when the range is diffed at once. The 04 edit replaced that original reason with the reversed claim and its 447 vs 476 numbers.
- **The gap:** nothing asked the spike to explain the difference between rows and range. It added the explanation unasked and also edited a later slice's rationale.
- **Reach:** 04's implementer will build the PR sum line on a reason that is backwards. The output note ("says which") may tell users the range is stricter when it is looser.
- **Verdict:** unsound. The comparison mixes two different sets of commits. **Redo from:** compare the range diff with the sum of every commit in that same range, and justify 04's choice only with that comparison. Range-at-once stays a sound choice. Only its stated reason is wrong.
- **Confidence:** low.

### The README's next-agent prompt was not updated

- **When:** `3d30961` (README untouched).
- **Slice:** 01
- **What happens now:** `README.md` still says "Status: spec written, nothing built. Start with slice 01". The next agent who opens the spec will rerun the spike. The README's own instruction is "Update this prompt before you end". The alternative says slice 01 is built and waiting on the user's gate (tiers plus whitespace setting), with this ledger's corrections to settle first.
- **The gap:** none. The baseline asked for it. It was skipped.
- **Reach:** every later session starts from this prompt.
- **Verdict:** unsound. A required step was quietly skipped. **Redo from:** the next-agent prompt reflects the branch's real state after every slice.
- **Confidence:** low.

### Diff file headers are found by prefix, so content lines starting with `++` or `--` are dropped

- **When:** `3d30961`, `pr27.py` `count()`: `if plain.startswith(("+++", "---")): continue`.
- **Slice:** 01
- **What happens now:** any removed line whose content begins with `--` (a SQL or Lua comment, a markdown `---` rule or frontmatter fence) renders as `---…` and is skipped. So is an added line whose content begins with `++` (`++i;`). Neither is counted at all. In #27 this happens zero times (checked), so the spike's numbers stand. The obvious alternative treats `+++`/`---` as headers only before a file's first `@@` hunk.
- **The gap:** the parsing was delegated to the worker as throwaway, but slice 02 will likely copy it.
- **Reach:** a markdown-heavy or SQL commit would quietly undercount deletions and additions in the real script.
- **Verdict:** unsound as a pattern, harmless in this spike. **Redo from:** header lines are recognised by their position in the diff (between `diff --git` and the first `@@`), never by their content prefix.
- **Confidence:** medium.

## Sound

### Moved lines are matched by pinned colour codes, dimmed variants pinned to the same codes

- **When:** `3d30961`, `PINNED` and `NEW_MOVED` in `pr27.py`.
- **Slice:** 01
- **What happens now:** the script pins new, old and moved colours, and the two `newMoved*Dimmed` slots too, so a user's config can't change the counts. An added line containing bold magenta or bold cyan counts as moved. `oldMoved*Dimmed` is not pinned, but zebra mode never dims and moved-out lines aren't split by colour anyway, so nothing changes. The independent counter, with different colours and a first-code match, gives the same numbers.
- **The gap:** the slice said "pin colours" without listing which keys.
- **Reach:** 02 should pin all four dimmed keys too if it ever uses `dimmed-zebra`.
- **Verdict:** sound. It matches the plan's "pinned colours" decision and reproduces.
- **Confidence:** medium.

### The check is reported as passing

- **When:** `3d30961`, first "Result" bullet.
- **Slice:** 01
- **What happens now:** under `allow-indentation-change`, `138fb64` shows 469 moved against 171 new and `fc3f4a6` 248 against 78, which meets "moved ≥ new under at least one setting". Under the default setting both fail. Both reproduced. The alternative was to stop and reslice, and the numbers don't call for it.
- **The gap:** none. The slice defined the pass rule.
- **Reach:** unblocks 02 once the user locks the tiers and the setting.
- **Verdict:** sound.
- **Confidence:** medium.

Trivial calls folded: script layout, stdout output, subject and moved-share columns, `|` escaping (4, delegated to the worker).

## Next step

Fix the PR-range label and the reversed rows-vs-range reason in `pr27.md` and slice 04, update the README prompt, then put the corrected table in front of the user for the tier and whitespace gate. Four of the six non-trivial entries sit in how the spike reads and frames its numbers, not in the counting. When 02 is drafted, settle the definitions of "deleted", "renamed" and "PR range" in the spec first.

# User decisions at the slice 01 gate (2026-11-06)

- **Whitespace setting:** always `--color-moved-ws=allow-indentation-change`; the small remaining undercount (short moved lines below git's block-size floor) is labelled in the output. Approved by the user after reading `spikes/pr27.md`.
- **Tiers locked:** target 400, soft 800, hard 1,500 new product-code lines, for each commit and for the PR total. Approved by the user; no longer provisional.

# Check 2: slice 02 move classifier

- **Scope:** commit `c0d7eef` on `claude/diff-size` (`skills/slice-spec/scripts/diff_size.py`, `test_diff_size.py`, the README's next-agent prompt).
- **Baseline:** `specs/diff-size/README.md`, `slices/02-move-classifier.md`, and the user's slice 01 gate decisions above. Run by another workflow with no user present (rule 7): every confidence is capped at medium. Check 1 entries the code did not change are not relisted.
- **Self-report:** missing beyond the commit message and the README prompt, so this ledger rests on an independent trace and throwaway probes in temp repos outside this repo.
- **Tests:** `python3 -m unittest discover -s skills/slice-spec/scripts` passes (17 tests). `python3 tools/validate.py` passes (7 skills, 0 errors). `skills/codebase-rubric/scripts` tests pass.

## Reproduction on brain-cli

With pathspecs `. :!dist :!specs` and an empty user config, the classifier gives exactly the spike's indent-insensitive numbers for every slice commit (`ea9b3ed` 111 / 76, `9083e81` 42 / 273, `adf8ed2` 34 / 205, `138fb64` 171 / 469, `fc3f4a6` 78 / 248, `596eacd` 5 / 130, `f6f554a` 6 / 7 new / moved), and deleted plus moved-out equals the spike's deleted column in each (for `138fb64`: 63 + 469 = 532). The range `7045e68..f6f554a` gives 538 new / 1,254 moved / 154 deleted / 1,253 moved out (154 + 1,253 = 1,407). The README's `dist/` claim also reproduces (`ea9b3ed` 110 vs 111, the range 536 vs 538). Over the whole brain-cli history diffed against the empty tree, new + moved equals `--numstat` added (20,086).

## Check these first

1. A user's diff config still changes the counts.
2. Some files come back with an empty path.
3. A renamed binary file counts its newline bytes as moved lines.

## Needs you

### A rename with one edited line drops every moved line

- **When:** `c0d7eef`, `count_range()`: the line-count fill-in runs only when a renamed file has no hunk.
- **Slice:** 02
- **What happens now:** a 40-line file renamed with no changes counts 0 new / 40 moved. The same file renamed with one line changed counts 1 new / 0 moved / 1 deleted, because git prints a hunk for the one line and the 39 unchanged lines appear nowhere. So the moved column jumps from 40 to 0 on a one-line edit. The tiered "new" number is right either way (1). The obvious alternative counts a renamed file's unchanged lines as moved in both cases: its line count in the commit minus its added lines.
- **The gap:** the README says "renames counted as moved", and Check 1 recommended adding a renamed file's line count to the moved column, but neither said what happens when the rename also has edits.
- **Reach:** slice 04's table and the PR total will under-report moves for any directory rename that also touches imports, which is the common case.
- **Verdict:** needs-you. Only a reported column changes, so it is a reporting call. **Recommended call:** a renamed file's lines that are not in an added hunk count as moved (and as moved out), with or without edits, plus a temp-repo test. **To reverse:** fill in the count only for renames with no hunk, as now.
- **Confidence:** medium.

### "Deleted" and rename handling follow Check 1's recommendations without a user answer

- **When:** `c0d7eef`, `FileCount` (`deleted` vs `moved_out`) and the pure-rename fill-in.
- **Slice:** 02
- **What happens now:** a removed line that git colours as moved is now `moved_out`, not `deleted`, so `138fb64` reports 63 deleted instead of 532. A pure rename counts every line as moved instead of 0. Both are the recommended calls from Check 1's two needs-you entries. The user's gate notes record only the whitespace setting and the tiers, so the user never answered these two. The README prompt told slice 02 to "settle" them, and the worker took the recommendations.
- **The gap:** Check 1 left both as needs-you. The gate did not close them.
- **Reach:** slice 04's table columns and the output note follow these definitions.
- **Verdict:** needs-you. The calls are sound and easy to reverse, but they are still the user's to confirm. **Recommended call:** keep both and say in 04's output note that deleted means removed and not moved. **To reverse:** add `moved_out` back into `deleted`, and drop the rename fill-in.
- **Confidence:** medium.

### A range of commits sizes a merge and the side-branch commits it brings in

- **When:** `c0d7eef`, `commits_in()` (`git rev-list --reverse A..B`, no `--first-parent`).
- **Slice:** 02
- **What happens now:** a branch merges a side branch that added a 5-line file. `commits_in` returns the side commit and the merge. The side commit counts 5 new, and the merge (against its first parent) counts the same 5 again, so the rows add up to 11 new while the range diffed at once counts 6. The merge row can cross a tier on lines that were already sized in their own row. The obvious alternative walks `--first-parent`, so each line lands in one row. The PR total is unaffected, because it diffs the range at once.
- **The gap:** slice 02 asked for one commit. `commits_in` is a range helper for 04, added without a spec line on merges in a range.
- **Reach:** slice 04's per-commit table copies this walk.
- **Verdict:** needs-you. Which commits a PR's table should list is a reporting call for 04. **Recommended call:** `--first-parent` in `commits_in`, decided in 04's spec. **To reverse:** drop the flag.
- **Confidence:** medium.

## Unsound

### A user's diff config still changes the counts

- **When:** `c0d7eef`, `PINNED_CONFIG` and `DIFF_FLAGS`; the module docstring says a user's config "cannot change the counts".
- **Slice:** 02
- **What happens now:** colours, prefixes and move settings are pinned, but other settings that change what the diff contains are not. With `diff.algorithm=histogram` in the user's global config, brain-cli `138fb64` counts 166 new / 479 moved (not 171 / 469) and `fc3f4a6` 80 new (not 78). With `diff.submodule=diff`, a submodule bump that counted 1 new / 1 deleted instead counts the submodule's own changed file as 4 new lines. With `diff.ignoreSubmodules=all` or `diff.submodule=log` it counts nothing. With `core.attributesFile` marking `*.py -diff`, a 5-line addition counts 0. The obvious alternative sets these on the command line (the diff algorithm the spike used, the submodule format, the submodule ignore rule) and neutralises the user's attributes file, then tests each key. The existing config test covers colours, prefixes and `diff.colorMoved` only.
- **The gap:** the README's planning decision was "pinned colours" so "a user's git colour config must not change the counts". The worker widened the claim in the docstring without covering the wider set.
- **Reach:** two people sizing the same commit can get different tiers. Slice 04's "reproduce the spike" check passes only for users on git's default algorithm.
- **Verdict:** unsound. The stated property does not hold. **Redo from:** every user setting that changes the diff's lines or files (algorithm, submodule format and ignore rule, attributes file) is fixed by the script, and a test sets each one and expects the same counts.
- **Confidence:** low.

### Some files come back with an empty path

- **When:** `c0d7eef`, `parse()`: paths are read only from `---`/`+++` and `rename from`/`rename to` lines.
- **Slice:** 02
- **What happens now:** git prints no `---`/`+++` lines for an added binary file, a mode-only change (`chmod +x`), an empty new file, or a file whose attributes say `-diff`. Each comes back as a `FileCount` with both paths `None`, so `.path` is `""`. Counts are 0, so totals are right, but slice 03 judges files by path and slice 04 prints them by path, and both will see `""`. The obvious alternative takes the paths from the `diff --git a/… b/…` header (or the `new file`, `deleted file` and rename lines) whenever `---`/`+++` are missing.
- **The gap:** the parsing was delegated to the worker; no test has a file without a hunk except the pure rename.
- **Reach:** 03's filter and 04's table both key on path.
- **Verdict:** unsound. A record that names no file is not a per-file count. **Redo from:** every `FileCount` names the file it counts, whether or not git printed a hunk for it.
- **Confidence:** low.

### A renamed binary file counts its newline bytes as moved lines

- **When:** `c0d7eef`, `count_range()` and `line_count()`.
- **Slice:** 02
- **What happens now:** a binary file is renamed. git prints `Binary files … differ` and no hunk, so the pure-rename fill-in runs and counts the newline bytes in the blob: 50 moved and 50 moved out for a 70-byte file. Renamed with its bytes changed, it counts 51 / 51. An added binary file counts 0, as it should. The obvious alternative treats a file git calls binary as having no lines.
- **The gap:** binary files were not in slice 02's cases, and slice 03 skips them only later, from the tree.
- **Reach:** small for the tiered number (moved is not tiered), but the moved column for a PR that renames an assets folder becomes noise, and 03's filter only hides it if it gets binary detection right.
- **Verdict:** unsound. Line counts on a binary blob have no meaning. **Redo from:** a file git reports as binary contributes zero line counts in every column, with its path kept.
- **Confidence:** low.

### The git version and repo checks exist but nothing runs them

- **When:** `c0d7eef`, `check_git()` and `check_repo()`.
- **Slice:** 02
- **What happens now:** slice 02's Decided list says git older than 2.17 exits 2 naming the version. `check_git()` does that, but no code path calls it and no test covers it, so on old git the user would see git's own "unknown option" error. `count_commit()` also skips `check_repo()`, so a path that is not a repo reports "unknown commit: …" instead of "not a git repository". The obvious alternative runs both checks at the entry points, or hands both to slice 04 in the README prompt.
- **The gap:** there is no CLI yet, so "exit 2" has no home in 02. The README prompt does not say that 04 must wire the checks in.
- **Reach:** 04 may assume the checks are already in force.
- **Verdict:** unsound. A decided behaviour is untested and unreachable, and the hand-off doesn't mention it. **Redo from:** the bad-input checks run before any count, and a test proves each one, or the next-agent prompt names them as 04's job.
- **Confidence:** medium.

## Sound

### Counts come back as a list of per-file records with four columns and both paths

- **When:** `c0d7eef`, `FileCount` and `count_commit()`.
- **Slice:** 02
- **What happens now:** the slice named the result `{path: (new, moved, deleted)}`. The build returns a list of `FileCount` records with `new`, `moved`, `deleted`, `moved_out`, `old_path` and `new_path`. The fourth column is needed for the moved-out split, and both paths let 03 judge a rename by either side. The alternative, a dict keyed by path, can't hold a rename's two paths.
- **The gap:** the seam's shape predates the moved-out split.
- **Reach:** 03 and 04 build on this record.
- **Verdict:** sound. It is the slice's shape plus what the later calls needed.
- **Confidence:** medium.

### Diffs use zero context lines and only hunk lines are counted

- **When:** `c0d7eef`, `--unified=0` in `DIFF_FLAGS` and `parse()`'s hunk tracking.
- **Slice:** 02
- **What happens now:** the diff carries no context lines, and `+`/`-` lines count only after a file's first `@@`, which fixes Check 1's header-by-prefix entry (a removed `-- comment` line is counted). `\ No newline at end of file` lines are ignored, and a moved block whose last line lacked a newline still counts as moved. All brain-cli numbers match the spike, which used git's default context, so zero context does not change move detection here.
- **The gap:** the flags were delegated to the worker.
- **Reach:** later slices inherit the parser.
- **Verdict:** sound. It reproduces and closes the earlier gap.
- **Confidence:** medium.

### The README prompt tells slice 03 to filter with pathspecs

- **When:** `c0d7eef`, `README.md` "Next agent prompt".
- **Slice:** 02
- **What happens now:** the prompt says moves are matched only among the files diffed, so 03 must pass its filter to git as pathspecs. Its evidence reproduces: `ea9b3ed` counts 110 new `src/` lines with `dist/` in the diff and 111 without, and the range 536 vs 538. The alternative, filtering counts after the diff, would let compiled output supply moves.
- **The gap:** none. The README asks for the prompt to be updated.
- **Reach:** sets 03's design.
- **Verdict:** sound.
- **Confidence:** medium.

Trivial calls folded: path unquoting, the header-tab strip, refusing `A...B`, the empty-tree constant, and the test fixture layout (5, delegated to the worker or harmless). Relative repo paths, CRLF files, whitespace-error highlighting, a 20,000-line re-indented move and `diff.renames`, `diff.renameLimit`, `diff.indentHeuristic`, `diff.interHunkContext` and `core.whitespace` all probed with no miscount.

## Next step

Fix the three unsound parsing and config entries in `diff_size.py` with a temp-repo test each, then put the three needs-you calls in front of the user before slice 03 starts. Four of the ten entries sit in what the diff contains before parsing (config, binaries, files with no hunk, renames with edits). Settle "which git settings and file kinds the counts must survive" in 03's spec instead of finding them one by one.

# Check 3: slice 03 product-code filter

- **Scope:** commit `0c7aaf1` on `claude/diff-size`: the "Product-code filter (slice 03)" section of `skills/slice-spec/scripts/diff_size.py` plus the `literal` pathspec option, `test_diff_size_filter.py`, and `tools/test_skip_rules_drift.py`.
- **Baseline:** `specs/diff-size/README.md`, `slices/03-product-filter.md`, and the slice 01 gate decisions above. Run by another workflow with no user present (rule 7): every confidence is capped at medium. Check 1 and Check 2 entries the code did not change are not relisted.
- **Self-report:** missing beyond the commit message and the README prompt, so this ledger rests on an independent trace and throwaway probes in temp repos outside this repo.
- **Tests:** `python3 -m unittest discover -s skills/slice-spec/scripts` passes (29 tests). `python3 -m unittest tools/test_skip_rules_drift.py` passes (3). codebase-rubric's tests pass (36). `python3 tools/validate.py` passes (7 skills, 0 errors). git 2.43, so the pre-2.40 working-tree fallback for attributes was not exercised.

## Reproduction on brain-cli

`count_product` on `7045e68..f6f554a` gives 513 new / 1,254 moved / 154 deleted / 1,253 moved out, skipping 54 not-code and 23 vendored-or-build files, as the README says. Of the 513 new lines, 402 are in `src/` and 111 are `specs/split-cli-commands/golden.sh`. Per commit, the filter matches the spike's indent-insensitive numbers except `138fb64` (177 new, not 171): the extra 6 lines are all `golden.sh`, which the spike's `:!specs` left out. For the head tree, `skip_reason` (judged from `git ls-tree`) and `size_report.py` (judged from a checkout of `f6f554a`) agree on all 213 tracked paths, and both pick the same 24 changed files as product code.

## Check these first

1. A file is kept or dropped by path, so lines from its skipped side still count.
2. A skipped old side can still supply moves, so new product code counts as moved.
3. Pointing the filter at a subfolder of the repo counts nothing.

## Needs you

### A skipped file paired as a rename disappears from the skip counts

- **When:** `0c7aaf1`, `product_paths()`: a file is counted as skipped only when neither side is product code.
- **Slice:** 03
- **What happens now:** a commit deletes `dist/a.js` and adds `src/a.py` with the same lines. git pairs the two as a rename. The new side is product code and is kept; the `dist/` side is dropped from the diff, but it is not counted under "vendored or build folder" either, so the report names neither file as skipped (`test_build_output_cannot_supply_moves` asserts `skipped == {}`). `size_report.py` keeps the property that every path is either counted or skipped. The obvious alternative counts each non-product side under its own reason, so a rename out of `dist/` shows one skipped build file next to the new product file.
- **The gap:** the slice asks for "a skipped-file count per reason" without saying whether the count is per file or per side, or what happens when only one side of a rename is skipped.
- **Reach:** slice 04 prints this count. A reader checking "what was left out" will not see build or generated files that git happened to pair with product files.
- **Verdict:** needs-you. Only a reported count changes. **Recommended call:** count skipped sides, not skipped files, so every changed path is either counted or skipped, and say so in 04's output note. **To reverse:** count a file only when both sides are skipped, as now.
- **Confidence:** medium.

### The two copies of the rules disagree when the user has an attributes file

- **When:** `0c7aaf1`, `marked_paths()` passes `-c core.attributesFile=/dev/null`; `size_report.marked_paths()` does not.
- **Slice:** 03
- **What happens now:** a user's global git config sets `core.attributesFile` to a file containing `*.py linguist-generated`. `size_report.py` skips `src/a.py` as marked generated. `diff_size.py` ignores that file and counts the same `src/a.py` as 5 new lines. Both read the repo's own `.gitattributes` and `.git/info/attributes` the same way. The drift test cannot see this, because it compares constants and calls the predicates with an empty `marked` set.
- **The gap:** Check 2 said a user's settings must not change diff_size's counts. The README says the skip rules are copied so the two scripts agree. Neither said which wins when those collide.
- **Reach:** a user who checks a file's verdict with `size_report.py` and then sizes a commit with `diff_size.py` can get two different answers for the same tree.
- **Verdict:** needs-you. diff_size's choice follows Check 2, but whether size_report should match is a codebase-rubric call outside this slice. **Recommended call:** keep diff_size ignoring the user's attributes file and record the difference in the drift test's docstring. Change `size_report.py` only in its own skill's work. **To reverse:** drop the `core.attributesFile` override from diff_size's `marked_paths()`.
- **Confidence:** medium.

## Unsound

### A file is kept or dropped by path, so lines from its skipped side still count

- **When:** `0c7aaf1`, `product_paths()` keeps a set of paths, and `count_product()` zeroes a side only when its path is missing from that set.
- **Slice:** 03
- **What happens now:** `product_paths()` judges the old side of each file against the base tree and the new side against the head tree. Then it throws away which side passed and keeps just the path. If either side passes, the whole file goes into the diff and both sides' lines count. Probes, each expected to add 0 new lines:
  - In one commit, `.gitattributes` gains `gen/** linguist-generated` and `gen/x.py` gains 4 lines. The 4 lines count as new.
  - `pkg/package.json` is added while `pkg/build/out.js` gains 4 lines. Those 4 lines count as new, although the head tree makes `pkg/build/` build output.
  - `src/a.py` gains a `# @generated` first line plus 4 lines. 5 new.
  - `src/a.py` becomes binary. Because `DIFF_FLAGS` has `--text`, its bytes are diffed as text: 4 "new" lines and 5 deleted. The `--text` comment in `DIFF_FLAGS` says the filter keeps binaries away from it. That only holds when both sides are binary.
  - `src/t.py` becomes a symlink. Its target string counts as 1 new line. The reverse, a symlink becoming a file, counts the old target as 1 deleted line.

  The obvious alternative carries the verdict per side. Lines on a skipped side contribute nothing in any column.
- **The gap:** the slice says added lines are judged against the commit's tree and deleted lines against the parent's. It doesn't say what to do with one file whose two sides get different verdicts. The tests cover only files whose sides agree, plus one rename.
- **Reach:** the tiered "new" number grows whenever a commit marks a file generated, adds a package root, or replaces a source file with a binary or a symlink. These are exactly the commits where the filter exists to help.
- **Verdict:** unsound. The slice's own property, added lines judged against the commit's tree, does not hold. **Redo from:** every line is counted only if its own side is product code, in every column. A file that changes type, gains a generated mark, or turns binary contributes nothing from its skipped side. Add a temp-repo test for each case above.
- **Confidence:** low.

### A skipped old side can still supply moves, so new product code counts as moved

- **When:** `0c7aaf1`, `count_product()` passes whole paths to the diff, and its docstring says non-product files "can't supply moves".
- **Slice:** 03
- **What happens now:** the base has `.gitattributes` with `gen/** linguist-generated` and a 5-line `gen/x.py`. The head deletes `.gitattributes`, rewrites `gen/x.py` to one line, and adds `src/y.py` with the 5 lines that were in the generated file. The old side of `gen/x.py` is generated, but its new side is now product code, so the path enters the diff, and git colours the old generated lines as moved into `src/y.py`. `src/y.py` counts 0 new / 5 moved. It should be 5 new, because the code it came from was never reviewed as product code. The obvious alternative keeps a skipped side out of move matching entirely.
- **The gap:** the README's next-agent prompt (from Check 2) said to keep non-product files out of the diff so they can't supply moves. It talked about files and didn't cover a file whose old side is skipped and new side is not.
- **Reach:** the tiered number undercounts in the direction the README warns about: code copied out of generated or build output passes as relocation.
- **Verdict:** unsound. The stated property ("can't supply moves") does not hold. **Redo from:** a side that is not product code is never a move source or target. Zeroing its counts after the diff is not enough. The diff that finds moves must not contain it.
- **Confidence:** low.

### Pointing the filter at a subfolder of the repo counts nothing

- **When:** `0c7aaf1`, `count_product()` passes repo-root paths as `--literal-pathspecs`, which git reads relative to the folder it runs in.
- **Slice:** 03
- **What happens now:** a commit adds `src/a.py` and `lib/b.py`, 5 lines each. `count_product(repo_root, …)` gives 10 new. `count_product(repo_root / "src", …)` gives 0 new and no error. `ls-tree --full-tree` and `diff --name-status` return root-relative paths, but the diff runs with `-C src`, so the pathspec `src/a.py` means `src/src/a.py`. Slice 02's `count_commit(repo_root / "src", …)` still gives 10. The obvious alternative anchors the pathspecs at the top of the repo (`:(top,literal)` magic, or running git at the repo's top level).
- **The gap:** the slice didn't say which folder the repo argument may name. Slice 02 worked from any folder inside the repo, and nothing tests that for 03.
- **Reach:** slice 04's CLI will likely take a repo path or the current folder. Run from a subfolder, it would print an all-zero table with no warning.
- **Verdict:** unsound. A regression from slice 02 that gives a silent wrong answer. **Redo from:** the counts are the same from any folder inside the repo, and a test runs the filter from a subfolder.
- **Confidence:** low.

### The drift test can't see a change to the package-root or generated-mark rules

- **When:** `0c7aaf1`, `tools/test_skip_rules_drift.py`.
- **Slice:** 03
- **What happens now:** I edited copies of the two scripts in a temp folder, outside the repo. Editing a `LOCKFILES` entry, `HEADER_LINES`, a skip label, or the root-`dist/` branch in only diff_size's copy fails the drift test, as the slice requires. Deleting the package-root branch of diff_size's `in_build_dir()`, or its `marked-generated` rule, still passes. The test calls `skip_reason` with an empty tree and an empty `marked` set, and it never builds a `build/` folder under a package marker. The obvious alternative gives both copies the same small fixture: a tree with a package marker for the build rule, and a marked set for the attributes rule.
- **The gap:** the slice decided that the test compares "constants and pure predicates". It didn't list which predicates or which branches.
- **Reach:** the package-root rule is the one the two copies implement differently (disk vs tree), so it is the one most likely to drift.
- **Verdict:** unsound. Two of the seven rules can drift without failing the test. **Redo from:** every rule in `skip_reason`, and the order they run in, has a case in the drift test that fails when only one copy changes.
- **Confidence:** medium.

### A commit with tens of thousands of product files crashes with a raw error

- **When:** `0c7aaf1`, `count_product()` passes every product path to `git diff` on the command line.
- **Slice:** 03
- **What happens now:** a commit adds 40,000 one-line `.py` files with paths of about 70 characters. Linux's 2 MB argument limit is exceeded, and Python raises `OSError: [Errno 7] Argument list too long` instead of a `DiffSizeError`, so slice 04's CLI would crash with a traceback. 5,000 files work (1 second). Skipped files never reach the command line, so vendoring a dependency doesn't trigger it, but a repo-wide codemod or a first import of a large codebase can. The obvious alternative keeps the path list off the command line, for example by running the diff without pathspecs and excluding the skipped paths instead, or by splitting the list where moves can't cross.
- **The gap:** the slice didn't mention commit size. Slice 04's non-goal says the script fails only on bad input.
- **Reach:** the PR total diffs a whole range at once, which makes the limit easier to reach than one commit.
- **Verdict:** unsound. A valid input crashes. **Redo from:** any number of changed files is counted, or the script exits with a named error, and a test covers a list over the argument limit.
- **Confidence:** medium.

## Sound

### Paths go to git as literal pathspecs

- **When:** `0c7aaf1`, the `literal` option on `diff_text()` and `count_range()`.
- **Slice:** 03
- **What happens now:** product paths are passed with `--literal-pathspecs`, so git takes them as names, not patterns. Probes with spaces, a double quote, `[x]?`, a leading dash (`-lead.py`), `:(top)x.py`, a tab, a backslash and non-ASCII letters were all counted once, 45 of 45 lines. Without the flag, `[abc]*.py` would match other files and `:(top)…` would be read as pathspec magic.
- **The gap:** the pathspec format was delegated to the worker.
- **Reach:** slice 04 reuses `count_range`.
- **Verdict:** sound.
- **Confidence:** medium.

### Submodules and symlinks count as "not a file" with no lines

- **When:** `0c7aaf1`, `product_paths()`: only modes `100644` and `100755` are read.
- **Slice:** 03
- **What happens now:** adding a submodule counts 0 lines and skips it as "not a file" (its `.gitmodules` skips as not code). Adding or deleting a symlink skips it the same way. This matches `size_report.py`, which skips symlinks and submodule folders as "symlink or not a file". A symlink that replaces a file, or the reverse, is the entry above.
- **The gap:** delegated to the worker.
- **Reach:** none beyond this slice.
- **Verdict:** sound.
- **Confidence:** medium.

Trivial calls folded: the `Side` and `Filtered` record shapes, skip reasons keyed by stable ids with phrases in `SKIP_LABELS`, a skipped file counted under its newest side's reason, `git_at_least` duplicating `check_git`'s version parse, and a `cat-file --batch` parse that reads one byte past a `missing` record but still lands inside the next object's header, so it survives (a missing blob is read as empty, judged as product code, and the diff then fails with a named error) (5, delegated to the worker or harmless). Unprobed: `blob_heads` holds every changed blob whole in memory although it reads only the first 8 KB of each, and the pre-2.40 working-tree fallback for attributes.

## Next step

Rebuild `product_paths()` and `count_product()` around sides instead of paths, with one temp-repo test for each case in the first two unsound entries, and make the filter work from a subfolder. Then put the two needs-you calls in front of the user before slice 04 starts. Three of the eight entries come from one gap: the slice judges sides, but the diff works on files. Settle in the spec what the unit is: a file, a side, or a line.

# Check 4: slice 04 report and CLI

- **Scope:** commit `bee2fab` on `claude/diff-size`: the "Report and CLI (slice 04)" section and the module docstring of `skills/slice-spec/scripts/diff_size.py`, `test_diff_size_cli.py`, `spikes/pr27-cli.md`, and the README status. Also, briefly, whether `57d7830` (the slice 03 fixes) resolves Check 3.
- **Baseline:** `specs/diff-size/README.md`, `slices/04-report-cli.md`, and the slice 01 gate decisions above. Run by another workflow with no user present (rule 7): every confidence is capped at medium. Check 1 to 3 entries the code did not change are not relisted.
- **Self-report:** missing beyond the commit message, the README prompt and `spikes/pr27-cli.md`, so this ledger rests on an independent trace and throwaway probes in temp repos outside this repo.
- **Tests:** `python3 -m unittest discover -s skills/slice-spec/scripts` passes (44). `tools/test_skip_rules_drift.py` passes (5). codebase-rubric's tests pass (36). `python3 tools/validate.py` passes (7 skills, 0 errors). git 2.43. The slice's last check, the user's spot-check of `138fb64`, is still open; the README says so.

## Reproduction on brain-cli

`diff_size.py /home/user/brain-cli 7045e68..f6f554a` exits 0 and prints, byte for byte, the table in `spikes/pr27-cli.md`, twice in a row. The rows match `pr27.md`'s indent-insensitive column except where the filter explains it (`golden.sh` now counts; `deleted` no longer holds moved-out lines). The slice's own range, `ea9b3ed~1..f6f554a`, gives 408 new for the whole range, over target. brain-cli's status stays clean, its object count stays 260 and `git fsck` is clean; the run only refreshed the timestamps of 5 tree objects that already existed (git's `write-tree` does this when an object is already present).

## Check 3's fixes (`57d7830`)

All five unsound entries are resolved. Each has a temp-repo test, and probes agree: from a subfolder the counts match the root, a 40,000-file commit counts 40,000 new in 24 s with exit 0, and deleting the package-root branch or the marked-generated rule from a copy of `diff_size.py` now fails the drift test. Check 3's two needs-you entries (skip counts per file, not per side; the user's attributes file) are unchanged in the code and still wait on the user.

## Check these first

1. The whole-range row diffs from A, not from where the branch started.
2. A shallow clone's oldest commit is sized as if it added the whole repo.
3. Warnings and notes render as one markdown list.

## Needs you

### A merge commit's row counts the lines the merge brought in

- **When:** `bee2fab`, `report()` sizes every first-parent commit against its first parent, using `commits_in()` from `0945449`.
- **Slice:** 04
- **What happens now:** a feature branch adds 20 lines, then merges `main`, which had added 300 lines meanwhile. `diff_size.py . main..feat` prints the feature commit at 20 new and the merge row at 300 new, while the whole-range row says 20. With a bigger `main`, the merge row would cross soft and say "consider Reslice" about code this PR didn't write. The obvious alternative shows merge rows without a tier (or sizes only what the merge itself changed, such as conflict fixes), so the table's rows describe the PR's own work.
- **The gap:** Check 2 recommended `--first-parent` and said the merge rule should be decided in 04's spec. The spec was never updated, so what a merge row means was never decided.
- **Reach:** any branch kept up to date by merging `main` gets false Reslice warnings in the table a worker pastes into the PR.
- **Verdict:** needs-you. Which rows a PR table shows, and which get tiers, is a reporting call. **Recommended call:** list merge commits with their counts but no tier, and say so in the notes. **To reverse:** tier merge rows like any other row, as now.
- **Confidence:** medium.

### The output never says what "Deleted" leaves out

- **When:** `bee2fab`, `as_text()` and `NOTES`.
- **Slice:** 04
- **What happens now:** the table's Deleted column is removed lines that are not moves; moved-out lines appear only in `--json` (`moved_out`). For #27's `138fb64`, the table says 63 deleted where `git diff --stat` and slice 01's spike say 532. Nothing in the printed notes says this. Check 2 and Check 3 each left a needs-you whose recommended call was to explain it (and the skip counts) in 04's output note. The worker wrote the explanation into `spikes/pr27-cli.md` but not into the tool's output.
- **The gap:** those two calls are still open, and the slice says nothing about what each column means.
- **Reach:** a reviewer comparing the pasted table with GitHub's numbers sees a large mismatch with no explanation.
- **Verdict:** needs-you. It follows calls the user hasn't answered. **Recommended call:** keep the definitions and add one note line: "Deleted is removed lines that are not moves; skipped counts are files with no product-code side." **To reverse:** delete the line.
- **Confidence:** medium.

## Unsound

### The whole-range row diffs from A, not from where the branch started

- **When:** `bee2fab`, `report()` runs `count_product(repo, A, B)` for `A..B`.
- **Slice:** 04
- **What happens now:** a branch off `main` adds 20 lines. Meanwhile `main` deletes a 900-line file. `diff_size.py . main..feat` prints the one commit at 20 new, then the whole-range row at **920 new, over soft (800): split the goal**, exit 0. The 900 lines are `main`'s deletion, read backwards. If `main` instead adds 300 lines, the range shows 300 deleted. A reversed range (`HEAD..<an older commit>`) gives no rows and a whole range of 0 new / 320 deleted, with no error. The rows (from `git rev-list A..B`) and the whole range (A's tree against B's) describe different changes whenever A isn't an ancestor of B. The obvious alternative diffs from the merge base of A and B, which is what GitHub's PR diff shows and what slice 01's spike did (`7045e68` is the merge base).
- **The gap:** the slice says "the whole range diffed at once" but doesn't say from which commit. "A..B" in git means "commits in B not in A", which is the merge base reading, not A's tree.
- **Reach:** `main..HEAD` is the natural command for a PR, and `main` usually moves on. The tiered PR number, and the "split the goal" warning, can be wrong by whatever `main` changed.
- **Verdict:** unsound. The PR total stops measuring the PR. **Redo from:** the whole-range row covers exactly the changes the listed commits bring in (merge base of A and B, to B), and a test advances `main` with both an addition and a deletion after the branch point.
- **Confidence:** low.

### A shallow clone's oldest commit is sized as if it added the whole repo

- **When:** `bee2fab`, `report()` uses `parent()`, which falls back to the empty tree when `^1` doesn't resolve.
- **Slice:** 04
- **What happens now:** in a `git clone --depth 1`, `diff_size.py . HEAD` sizes the commit against the empty tree: a merge that changed 300 lines shows 330 new, exit 0, no warning. The same fallback is right for a true root commit, but in a shallow clone the parent exists and was just not fetched. The obvious alternative tells the two apart (git lists cut-off commits in `.git/shallow`, and `git rev-parse --is-shallow-repository` says whether there are any) and exits 2 with "fetch more history".
- **The gap:** the non-goals say exit 2 only on bad input. They don't say whether missing history is bad input.
- **Reach:** CI checkouts are shallow by default, and slice 05 wires this into worker runs and CI.
- **Verdict:** unsound. A valid-looking run gives a wrong number silently. **Redo from:** a commit whose parent was cut off by a shallow clone is never sized against the empty tree; the script exits 2 and names the commit. Add a test with `--depth 1`.
- **Confidence:** medium.

### Warnings and notes render as one markdown list

- **When:** `bee2fab`, `as_text()` puts the warnings list, a blank line, then the notes list.
- **Slice:** 04
- **What happens now:** when any warning prints, GitHub-flavoured markdown joins the two lists, because two lists split only by a blank line are one list. Rendered with `pandoc -f gfm`, "Warnings:" is followed by four bullets: the real warning, then the three notes as if they were warnings too. #27 has no warning, so its spike output renders fine and the tests never render anything. Separately, `cell()` escapes `|` but not a backslash, so a subject containing `\|` becomes `\\|`, which ends the cell and shifts the row's columns. The obvious alternative gives the notes their own heading or a non-list form, and escapes backslashes before pipes.
- **The gap:** the README says the agent pastes the output into the PR description. Nothing said it must render as written.
- **Reach:** every PR over soft shows notes as warnings in the description reviewers read.
- **Verdict:** unsound. The pasted text says something the tool didn't mean. **Redo from:** each block of the output (title, table, skipped line, warnings, notes) renders as its own block in GitHub-flavoured markdown, and every cell round-trips any subject. Add a test that renders the warning case and a subject with `\|`.
- **Confidence:** medium.

## Sound

### The PR total is the whole range diffed at once, tiered on the same numbers

- **When:** `bee2fab`, `report()` and `warnings()`.
- **Slice:** 04
- **What happens now:** for `A..B` the table ends with a bold "Whole range, diffed at once" row with its own tier. Over soft or hard, it adds "split the goal". A note says the rows find moves inside each commit and the range finds them across it, so its new count can be lower than the rows' sum. One commit gets no whole-range row, since it would repeat the commit row. An empty range (`HEAD..HEAD`) prints a 0 row. These follow the slice's "Decided" list, except for the base commit (above).
- **The gap:** the slice decided the numbers, not the one-commit and empty-range cases.
- **Reach:** slice 05's PR handback pastes this table.
- **Verdict:** sound.
- **Confidence:** medium.

### Exit 0 on any size, exit 2 on bad input, and `--json` in `size_report.py`'s shape

- **When:** `bee2fab`, `main()` and `report()`.
- **Slice:** 04
- **What happens now:** a 40,000-line commit is over hard and exits 0. An unknown commit, `A...B`, `A..B..C`, `HEAD^!`, a path that doesn't exist, a folder that isn't a repo, and `HEAD` in an empty repo each exit 2 with a one-line message and no stdout. `--json` follows `size_report.py`: the same `main()` shape, a `tiers` object, skip reasons as sorted stable keys, and tiers as `"target"`, `"soft"`, `"hard"` (here `null` when under target, since every commit gets a row). Output repeats byte for byte and holds no timestamps or absolute paths.
- **The gap:** field names were delegated; the exit codes and determinism were decided.
- **Reach:** slice 05 and any hook reading `--json`.
- **Verdict:** sound.
- **Confidence:** medium.

Trivial calls folded: 7-character commit hashes (`sha[:7]`, not git's unique abbreviation), per-commit skip counts only in `--json` while the text shows the range's, `..B` meaning `HEAD..B`, a bare repo reported as "not a git repository", and `--json` accepted in any position (5, delegated to the worker or harmless).

## Next step

Make the whole-range row start at the merge base, with a test where `main` moves after the branch point, then fix the markdown blocks and the shallow-clone fallback. Then put the merge-row and column-note calls, together with Check 2 and Check 3's open needs-you entries, in front of the user with the `138fb64` spot-check. Three of the seven entries are about which commits a range means (merge base, merges, shallow history). Settle in the spec that a range is "what the PR introduces", the way GitHub shows it, before slice 05 wires it in.
