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
