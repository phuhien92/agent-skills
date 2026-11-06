# Diff size

**Branch:** `claude/diff-size`

## Intent

> do we also have rules to keep PR code changes limit

The pack had no such rule. The user said "yes" to building a change-size check that tells moved lines apart from new ones, planned with `/slice-spec`, and accepted each recommended answer in the interview below.

How the user will know it worked: run it on brain-cli PR #27's seven slice commits and get a per-commit table of new, moved and deleted lines with a tier. It passes when the commits that were mostly relocation (slice 05 `138fb64`, slice 06 `fc3f4a6`) show most of their churn as moved, and when the user spot-checks one commit and agrees its "new" count matches what they would have to review.

## Non-goals

- **Never blocks.** It reports tiers and warnings. It exits non-zero only on bad input (unknown range, not a repo, git too old), never on size, and never fails CI on size.
- **Posts nothing to GitHub.** It prints a markdown table; the agent pastes it into the PR description it is already writing.
- **Doesn't judge quality.** It counts lines. Whether the lines were worth it stays with `decision-checker` and the user.
- **Never rewrites commits, reslices or splits a PR on its own.** Over soft (per slice or per PR), `slice-spec` suggests Reslice or a split; a person decides.
- **No new dependencies, no edits to brain-cli.** Python standard library only; brain-cli PR #27 is test data.

## Constraints

- **Measure:** added lines that are not moves, product code only, per commit. Moved and deleted lines are reported, not tiered.
- **Tiers (locked by the user at the slice 01 gate):** target 400, soft 800, hard 1,500 new lines per commit. Over target: shown. Over soft: "consider Reslice". Over hard: "reslice before review". All warnings.
- **PR total:** one sum line over the range, tiered on the same numbers. Over soft: "split the goal". Still a warning. (Changed after the interview: the user said "If a PR is too large, we should break down the goal into multiple subtasks to reduce the PR size", and accepted the recommendation below. This replaces the earlier "sum line with no tier".)
- **Splitting is planned up front.** In Interview, when the drafted slices' estimated new lines add up to more than soft, `slice-spec` splits the goal into sub-goals, one PR each. Each PR ships on its own and leaves `main` working. The slice graph gets a **PR** column; a slice belongs to exactly one PR. The estimate is a planning guess; `diff_size.py` gives the real number after each PR.
- **Mid-build:** when a branch's running total crosses soft, `slice-spec` suggests Reslice to move the remaining slices to a follow-up PR. It never moves them on its own.
- **Home:** `skills/slice-spec/scripts/diff_size.py` and its tests. Skills install one at a time, so the skip rules are copied from `skills/codebase-rubric/scripts/size_report.py`, and a test in `tools/` fails when the two copies drift.
- Backward compatibility: none. Nothing shipped depends on this.

## Slice graph

| # | Slice | Question it answers | Check | Depends on |
|---|---|---|---|---|
| 01 | Spike on #27 | Does git's move detection count #27's relocations as moved, and with which whitespace setting? | `spikes/pr27.md` table + user locks tiers and fallback | none |
| 02 | Move classifier | Given a commit, which added lines are new and which moved? | unittest on synthetic temp repos | 01 |
| 03 | Product-code filter | Does every count leave out lockfiles, build output, generated, vendored, binary and non-code files, judged from the commit's tree? | unittest + drift test in `tools/` | 02 |
| 04 | Report and CLI | Does `diff_size.py <range>` print the table, per-commit and PR tiers, and `--json`, and reproduce the spike on #27? | unittest + run on #27 matches spike | 02, 03 |
| 05 | Wiring | Does Interview split an over-soft goal into PRs, do workers run it per slice, does Reslice get the size triggers, does the PR handback carry the table, and does CI run the tests? | `tools/validate.py` + grep checks + eval cases + CI steps | 04 |

All five slices are one PR: their estimated new code (a script of a few hundred lines plus tests and doc edits) is under soft, and slice 04 measures it. Build order comes from **Depends on**. 01 is a user gate: nothing after it starts until the tiers and the whitespace fallback are settled.

## Open questions

- **The spot-check commit.** **Recommended:** `138fb64` (slice 05), the largest. It also carries a real fix ("fix the router table lookup"), so some new lines there are genuinely new. The user does the spot-check in slice 04.

Settled at the slice 01 gate (see `decisions.md`): always ignore indentation changes, with the undercount labelled; tiers locked at 400 / 800 / 1,500.

## Decided in planning

- **Reuse size_report.py's rules by copy plus drift test, not import:** skills install separately. Turned down: a shared `tools/` module (breaks single-skill installs).
- **Drift test in `tools/test_skip_rules_drift.py`, not in `validate.py`:** the interview placed it in `tools/`; the lean drafter's `validate.py` option was dropped to keep the validator about structure. The test compares the rule data (constants and pure predicates), not whole files, because the diff copy must judge paths against a commit's tree (`git ls-tree`, `git cat-file`), not the disk.
- **Five slices, not three or nine.** Three drafters ran with different lenses (lean: 3, fail fast: 6, seams: 9). Kept from lean: one wiring slice and no separate tier-lock slice. Kept from fail fast: the spike first, as a user gate. Kept from seams: the classifier and the filter as separate seams (the filter must read trees, which is its own question), renames counted as moved, and CI wiring for the new tests (CI on main runs only `validate.py` and the codebase-rubric tests today). Dropped from seams: a conditional fallback slice (the spike already answers it, so the choice is made at the 01 gate) and a separate acceptance slice (folded into 04's check).
- **Pinned colours.** Moved lines are found only by colour codes, so the script sets every `color.diff.*` value and `--color=always` itself; a user's git colour config must not change the counts.
- **PR tier on the same numbers.** #27 as a whole (`7045e68..f6f554a`) measures 538 new / 1,254 moved / 1,407 deleted (indentation-insensitive, `dist/` and `specs/` excluded, docs still counted; about 400 new once non-code is skipped), so the PR limit would not have flagged it; its 3,000-line raw diff was mostly moves. Turned down: a separate, larger PR tier (one set of numbers is easier to reason about).
- **Per-commit move detection only.** A move spread across two commits counts as deleted in one and new in the other. Labelled in the output, not solved.

## Next agent prompt

Status: slices 01 to 03 built. `diff_size.py` now has the classifier (02, with the fixes from Check 2) and the product-code filter (03): `count_product(repo, base, head)` judges each side of a diff against its own commit's tree, removes each non-product side from a temporary copy of its tree and diffs the copies (so a skipped side adds no lines and supplies no moves, nothing is written to the repo, and commit size can't hit argument limits), and counts skipped files by reason. `tools/test_skip_rules_drift.py` guards the copied rules. On #27 the filtered range is 513 new / 1,254 moved; that includes `specs/split-cli-commands/golden.sh`, which is a shell script and so counts as code under the same rules. Next: slice 04, the CLI and report.

Before reporting a slice done, follow the `decision-checker` skill in Check mode on this branch and save `decisions.md`. Update this prompt before you end.
