# 02: Move classifier

**Question:** Given one commit, which of its added lines are new and which are moved, and how many lines did it delete, per file?

**Seam:** `skills/slice-spec/scripts/diff_size.py`, a function from (repo, commit) to per-file counts `{path: (new, moved, deleted)}`, built from `git diff` with `--color-moved=zebra`, the whitespace setting locked in 01, pinned colours and `-M` renames. A thin git runner and a pure parser over the coloured text, so the parser can be tested on fixed strings.

**Check:** `python3 -m unittest discover -s skills/slice-spec/scripts` passes, with synthetic temp repos for: a pure block move (0 new), a re-indented move (0 new under the locked setting), a move plus one edited line (1 new), a plain deletion (0 new), a whole-file rename (0 new), and a user git config with different `color.diff.*` values (same counts). Fails when any case miscounts.

**Must stay green:** `python3 tools/validate.py`; `python3 -m unittest discover -s skills/codebase-rubric/scripts`.

**Decided:**
- Standard library only; git ≥ 2.17 (for `--color-moved-ws`), else exit 2 naming the version.
- A merge commit is diffed against its first parent.
- Short moved lines below git's block-size floor count as new; that is labelled, not fixed.

**Delegated to the worker:**
- The exact git flags beyond those above, and how the parser reads colour codes.
- Fixture layout (tiny temp repos built in the test; never brain-cli history).

**Out of scope:**
- Skipping non-product files (03). Tiers, table and CLI (04).
