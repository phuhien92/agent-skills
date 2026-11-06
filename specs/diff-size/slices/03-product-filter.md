# 03: Product-code filter

**Question:** Does every count leave out lockfiles, build output, generated, vendored, binary and non-code files, judged from the commit's own tree?

**Seam:** a path filter inside `diff_size.py`: (repo, commit, path) → skip reason or none. Added and moved lines are judged against the commit's tree, deleted lines against the parent's. The rule data (lockfile names, code extensions, any-depth and root build folders, package markers, generated-header markers) is copied from `skills/codebase-rubric/scripts/size_report.py`. `.gitattributes` `linguist-generated`/`linguist-vendored` is read with `git check-attr --source` where the git version allows, else from the working tree, and that fallback is labelled.

**Check:** `python3 -m unittest discover -s skills/slice-spec/scripts` passes with temp-repo cases where a lockfile, root `dist/`, a package-root `build/`, `node_modules/` at depth, a `linguist-generated` path, a file with a generated header and a binary each contribute 0, and a skipped-file count per reason is reported. And `python3 -m unittest tools/test_skip_rules_drift.py` passes, and fails when one `LOCKFILES` entry (or any other copied constant) is edited in only one copy.

**Must stay green:** 02's tests; codebase-rubric's tests; `tools/validate.py`.

**Decided:**
- Copy plus drift test, not a shared import (skills install one at a time).
- The drift test compares constants and pure predicates by importing both modules, not file text.

**Delegated to the worker:**
- How the tree is read (`git ls-tree`, `git cat-file`), and how the predicates are shaped so both copies share them.

**Out of scope:**
- Output and tiers (04).
