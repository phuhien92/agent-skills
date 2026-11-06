# PR #27 through `diff_size.py` (slice 04)

`python3 skills/slice-spec/scripts/diff_size.py /home/user/brain-cli 7045e68..f6f554a`. Against `pr27.md` (slice 01): every row matches the indent-insensitive column except where the product-code filter applies. `specs/split-cli-commands/golden.sh` is a shell script, so it now counts (slice 01's two commits: 89 and 25 new; 6 of `138fb64`'s 177), and docs, scorecards and `dist/` are skipped by rule instead of by pathspec. "Deleted" no longer includes moved-out lines.

Change size for `7045e68..f6f554a`

| Commit | Subject | New | Moved | Deleted | Tier |
|---|---|---|---|---|---|
| `fbf78f7` | Add codebase-rubric scorecard before the cli.ts split | 0 | 0 | 0 |  |
| `d1ca4c4` | Spec: split the command handlers out of cli.ts (7 slices) | 0 | 0 | 0 |  |
| `5390bbf` | Slice 01: golden output check for the cli.ts split | 89 | 0 | 0 |  |
| `030ddec` | Slice 01 fixes from its decisions ledger | 25 | 0 | 9 |  |
| `ea9b3ed` | Slice 02: handler shape and router tables; move path and view | 111 | 76 | 21 |  |
| `9083e81` | Slice 03: move the extension runner and ext to src/commands/ext.ts | 42 | 273 | 19 |  |
| `adf8ed2` | Slice 04: move log and export to src/commands/log.ts | 34 | 205 | 16 |  |
| `138fb64` | Slice 05: move the remaining vault commands; fix the router table lookup | 177 | 469 | 63 |  |
| `fc3f4a6` | Slice 06: move the early commands (setup, telemetry, feedback, agent, context, update) | 78 | 248 | 73 |  |
| `596eacd` | Slice 07: move HELP out; cli.ts is the thin router (388 lines) | 5 | 130 | 2 |  |
| `490a7fd` | Document src/commands/ in AGENTS.md (CLAUDE.md links to it) | 0 | 0 | 0 |  |
| `5ddb658` | Add codebase-rubric scorecard after the cli.ts split | 0 | 0 | 0 |  |
| `f6f554a` | Fixes from the third decisions ledger (slices 03 to 07) | 6 | 7 | 4 |  |
| **Whole range** | diffed at once | **513** | 1254 | 154 | over target (400) |

Skipped files: not a code file: 54, vendored or build folder: 23

**Notes**

- Product code only, with codebase-rubric's skip rules.
- Moved lines ignore indentation changes. A moved line shorter than git's block floor (20 letters and digits) counts as new, so new leans high.
- The commit rows find moves inside each commit; the whole-range row finds moves across the range, so its new count can be lower than the rows' sum.
- The whole-range row starts where the branch left the base (their merge base), as a PR does.
- Deleted leaves out moved-out lines; a moved block shows only under Moved.
