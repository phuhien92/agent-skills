# 01: Spike on #27

**Question:** Does git's move detection count #27's relocations as moved, and with which whitespace setting?

**Seam:** none in product code. A throwaway script under `specs/diff-size/spikes/` reads `git diff --color=always --color-moved=zebra` with pinned colours for each of brain-cli's seven commits (`ea9b3ed 9083e81 adf8ed2 138fb64 fc3f4a6 596eacd f6f554a`, each against its parent), excluding `dist/` and `specs/` by pathspec, and writes `spikes/pr27.md`.

**Check:** `spikes/pr27.md` has, per commit, new / moved / deleted under the default whitespace setting and under `allow-indentation-change`. It passes when `138fb64` and `fc3f4a6` show moved ≥ new under at least one setting. It fails if neither setting does; then stop and reslice (a custom whitespace-insensitive matcher becomes its own slice). Then the user's decision on the artifact: lock the tiers and the whitespace setting, recorded in `decisions.md`.

**Must stay green:** `python3 tools/validate.py`. brain-cli untouched (read-only git commands only).

**Decided:**
- Both whitespace settings are measured, so the user chooses from numbers, not a guess.
- Each commit's message is shown next to its row: `f6f554a` is a fixes commit and `138fb64` includes a real router fix, so "mostly moved" is judged per commit, not by slice number.
- Colours are pinned with `-c color.diff.*` so local config can't change the counts.

**Delegated to the worker:**
- The spike script's language and layout; it is scratch and is kept only as evidence.
- Table formatting.

**Out of scope:**
- The real script and its filter (02, 03). Here `dist/` is excluded by pathspec only.
