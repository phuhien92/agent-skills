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
