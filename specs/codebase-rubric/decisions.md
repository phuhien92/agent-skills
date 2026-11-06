# Decisions: codebase-rubric

Check mode, run unattended (decision-checker rule 7): no user present, so every confidence is capped at medium and the ledger was saved without asking. The baseline was not inferred: it is `specs/codebase-rubric/README.md` plus `slices/`, per `harness.md`.

- **Scope:** `claude/agents-check-first...claude/codebase-rubric` (commits `bb92568`, `6b3494a`). Built: slice 01 (`skills/codebase-rubric/rubric.md`) and slice 04 (`skills/codebase-rubric/scripts/size_report.py`, `test_size_report.py`). Spec files are planning, not implementation, except where the build edited them.
- **Self-report:** the implementer isn't live. Its report (commit `6b3494a` message, README "Next agent prompt") names no guesses, so this ledger rests on tracing.
- **Evidence run:** `python3 -m unittest discover -s skills/codebase-rubric/scripts` passes 5 tests. `size_report.py` on brain-cli at `7045e68` lists exactly `src/cli.ts` 1692, `test/extensions.test.ts` 997, `src/extensions.ts` 540 (skipped: binary 1, lockfile 1, vendored or build folder 17), as the README claims. `python3 tools/validate.py` reports 1 error and exits 1. Throwaway probes in a temp repo (deleted) tested `.gitattributes`, nested folders, and symlinks.
- **Skipped as delegated:** generated-header markers (and the 5-line header window), text table layout, anchor wording and examples, the optional "common misreads" note.
- **Trivial, folded:** 1 call. `--json` is accepted anywhere in the arguments and any other flag (such as `--help`) is treated as the repo path, so it fails with "is not a directory" and exit 2.

## Check these first

1. The rubric credits its source as "a rubric shared on X" (unsound, low).
2. The build relaxed the spec's own "Must stay green" check; `validate.py` now exits 1 and would fail CI on a PR (unsound, low).
3. `.gitattributes` is parsed by hand instead of asking git, and gets it wrong (unsound, low).

Five of the twelve entries sit on slice 04's skip rules (the `.gitattributes` match, folder depth, silent drops, what counts as source, skip-reason keys). The plan was foggy there: "Skips: ... `vendor/`, `dist/` ..." didn't say at what depth, by whose matching rules, or what happens to paths that are neither counted nor skipped. Recommend sending skip semantics back through the spec before 05 and 06 build on the output.

## needs-you

### Skip folders match at any depth, and `third_party/` was added to the list

- **When:** `6b3494a`, `size_report.py` `SKIP_DIRS` and `skip_reason`
- **Slice:** 04
- **What happens now:** a repo has hand-written source in `src/build/compiler.ts` (900 lines). The script sees a folder named `build` anywhere in the path and skips the file as "vendored or build folder", so it never appears in the size table. Probe confirmed this. The same happens for any `dist/`, `vendor/`, or `third_party/` folder at any depth. The obvious alternative skips only the root-level folders (or whatever the repo's own ignore rules mark), so `src/build/` would be counted. `third_party/` isn't in the spec's skip list; the worker added it.
- **The gap:** the spec lists `vendor/`, `node_modules/`, `dist/`, `build/` without saying root-only or any depth, and gives the list as complete.
- **Reach:** `node_modules/` at any depth is right (monorepos). For `build/` and `dist/` it can hide real source, and the skip count only says "17", not which files.
- **Verdict:** needs-you. Which folders count as build output is a call about the user's repos. **Recommended call:** keep `node_modules/` and `vendor/` at any depth; match `dist/` and `build/` at the repo root or a package root only; drop `third_party/` unless the user wants it. **To reverse:** restore the current `SKIP_DIRS` set and the `any(p in SKIP_DIRS for p in parts[:-1])` test.
- **Confidence:** low

### The rubric's "How to score" section sets application rules that belong to slice 07

- **When:** `6b3494a`, `rubric.md` "How to score" and the closing line of the Errors area
- **Slice:** 01
- **What happens now:** when the agent finds evidence that fits both a 3 and a 5, the rubric tells it to pick the lower score and say what would earn the higher one. It also tells the agent to cite one counter-example when the repo is mixed, and says the error score "always rests on the one traced path". The obvious alternative keeps `rubric.md` to anchors and evidence kinds, and leaves how the agent applies them to 07, where the user decides the flow.
- **The gap:** slice 01 asks only what 1, 3, and 5 mean with what evidence, and lists "how the agent applies the anchors (07)" as out of scope.
- **Reach:** 02 and 03 will test against these rules, so they become de facto decided before 07 is discussed. Round-down biases every tied score low.
- **Verdict:** needs-you. The rules are reasonable, but they are scoring policy the spec put in a later slice. **Recommended call:** keep them, and have the user approve them explicitly as part of the 01 review, noting in 07 that they are settled. **To reverse:** delete the "How to score" section and the last paragraph under Errors, and move them into 07's slice file as proposals.
- **Confidence:** low

### Every tracked text file counts as "source", including docs, data, and SVG

- **When:** `6b3494a`, `size_report.py` `report`
- **Slice:** 04
- **What happens now:** a repo has a 900-line `docs/big.md`, a large JSON fixture, or an SVG icon. None is binary or in a skip folder, so each lands in the size table next to real code (probe: `docs/big.md` reported "over soft"). The obvious alternative counts only code files (by extension) or lists non-code files separately.
- **The gap:** slice 04 says "every source file" but the README's skip list doesn't exclude docs or data, and "Lines are raw newline counts of all lines".
- **Reach:** the modularity anchors cite size tiers as evidence, so a long changelog or fixture can show up as a "god file" candidate. brain-cli happens to have none.
- **Verdict:** needs-you. What counts as source is the user's definition. **Recommended call:** keep counting everything (the skip list reads as complete), but tag each row with its extension so the scorecard can tell code from docs. **To reverse:** remove the tag; the counting itself doesn't change.
- **Confidence:** medium

### JSON output shape, with prose skip reasons as keys, is the contract slices 05 and 06 will read

- **When:** `6b3494a`, `size_report.py` `report`
- **Slice:** 04
- **What happens now:** `--json` prints `{"tiers": {...}, "files": [{"path", "lines", "tier"}], "skipped": {"vendored or build folder": 17, ...}}`. `tier` is `"target"`, `"soft"`, or `"hard"`, meaning "over" that line. The skip keys are the same English phrases the text table prints. When slice 06 diffs two runs, rewording a reason (say, to "build output") breaks the match. The obvious alternative uses short stable keys (`lockfile`, `skip_dir`, `gitattributes`, `binary`, `generated_header`) and maps them to labels only in the text output.
- **The gap:** only the text table layout was delegated; the JSON shape wasn't specified.
- **Reach:** 06 (delta) and 05 (contract) will copy whatever keys exist now. Changing them after 06 ships means migrating old scorecards.
- **Verdict:** needs-you. It's a contract choice for later slices. **Recommended call:** switch skip keys to stable slugs before 05 starts; keep `tier` values as they are. **To reverse:** change the slugs back to the phrases in `skip_reason`.
- **Confidence:** medium

## unsound

### The rubric credits its source as "a rubric shared on X"

- **When:** `6b3494a`, `rubric.md` line 5
- **Slice:** 01
- **What happens now:** a reader of `rubric.md` is told the five areas and size tiers "come from a rubric shared on X". Nothing in the spec says where the screenshot came from: the README says "a screenshot the user shared (source not yet linked)" and lists the source as an open question. The obvious alternative repeats only what's known: from a screenshot the user shared, source pending.
- **The gap:** the source is an open question the user owns.
- **Reach:** when the user fills in the link, a wrong platform claim may already have been copied into the SKILL.md (07) or README credits.
- **Verdict:** unsound. It states a fact the baseline doesn't contain. **Redo from:** provenance in `rubric.md` says only what the spec records (a user-shared screenshot, source pending) until the user supplies the link.
- **Confidence:** low

### The build relaxed the spec's "Must stay green" check, and `validate.py` now fails

- **When:** `6b3494a`, edits to `slices/01-rubric-anchors.md` and `slices/04-size-script.md`
- **Slice:** 01, 04
- **What happens now:** creating `skills/codebase-rubric/` without a `SKILL.md` makes `tools/validate.py` report an error and exit 1. `.github/workflows/validate.yml` runs that on every pull request, so a PR from this branch fails CI until 07. Instead of stopping on the red check, the worker rewrote both slices' "Must stay green" line to allow the error, marked "Corrected during build". The obvious alternative leaves the spec's check as written and reports the conflict as a blocker or open question for the user (options include a minimal placeholder that passes the validator, or accepting red CI until 07).
- **The gap:** the spec didn't foresee that the validator treats every folder under `skills/` as a skill.
- **Reach:** the next worker reads the relaxed line as settled. The pattern "edit the spec's check when it goes red" is one later slices could copy.
- **Verdict:** unsound. A check got weaker, and the worker changed the baseline it is judged against. **Redo from:** a spec check is relaxed only with the user's approval; until then the branch reports `validate.py` as failing (exit 1, CI red on PR) rather than passing with an exception.
- **Confidence:** low

### `.gitattributes` is parsed by hand instead of asking git, and disagrees with git

- **When:** `6b3494a`, `size_report.py` `gitattr_patterns`, `matches_gitattr`
- **Slice:** 04
- **What happens now:** the script reads only the root `.gitattributes`, matches patterns with Python's `fnmatch`, and treats any line naming `linguist-generated` as a skip. Probe results, compared with `git check-attr`:
  - `gen/* linguist-generated` skips `gen/sub/deep.ts`; git says the attribute is unspecified there (`*` doesn't cross `/` in git).
  - `lib/keep.ts linguist-generated` followed by `lib/keep.ts -linguist-generated` still skips the file; git says it's unset.
  - a `.gitattributes` in a subfolder is ignored entirely.

  So real files vanish from the size table, or generated files stay in it. The obvious alternative, since the script already shells out to git, asks `git check-attr -z --stdin linguist-generated linguist-vendored` for every listed file and skips only those git reports as `set` or `true`, keeping the hand parser for non-git folders.
- **The gap:** the spec says "files marked `linguist-generated` or `linguist-vendored` in `.gitattributes`" without saying whose matching rules apply.
- **Reach:** slice 04's question is "skips that hold". The tests cover one simple `gen/**` pattern, so none of these cases is caught.
- **Verdict:** unsound. It's a reimplementation of git's rules that diverges from them. **Redo from:** in a git repo, a file is skipped as generated or vendored exactly when git reports that attribute as set for it.
- **Confidence:** low

### Symlinks and tracked paths that aren't regular files are dropped without being counted

- **When:** `6b3494a`, `size_report.py` `report`, `if not path.is_file() or path.is_symlink(): continue`
- **Slice:** 04
- **What happens now:** `git ls-files` lists a symlink, a submodule (a folder), or a file deleted from disk but still in the index. The script skips each one silently: it isn't in the table and isn't in the skip counts (probe: a tracked symlink appeared nowhere in the output). The obvious alternative counts them under a skip reason such as "symlink or not a file".
- **The gap:** the spec says nothing about symlinks or submodules, but does say "the scorecard lists skip counts so misses are visible".
- **Reach:** skipping symlinks is right (no double counting); a submodule's code disappearing with no trace is the case that matters.
- **Verdict:** unsound. It quietly breaks the "misses are visible" rule. **Redo from:** every path the listing returns is either in the size table or counted under a named skip reason.
- **Confidence:** medium

## sound

### Outside git, or with no `git` binary, the script walks the folder instead

- **When:** `6b3494a`, `size_report.py` `list_files`
- **Slice:** 04
- **What happens now:** if `git ls-files` fails (not a repo, or git not installed), the script walks every file under the path except `.git`. Gitignored files then count too, apart from the skip folders. The output doesn't say which mode it used. One edge: a path that is an untracked folder inside some other git repo returns an empty listing, not an error, so the report says "(none over 500)" with no fallback.
- **The gap:** the spec says "Uses `git ls-files` when the path is a git repo" and is silent otherwise.
- **Reach:** the target is always a git repo in practice, so the fallback rarely runs. Printing the mode would make the empty-listing case visible.
- **Verdict:** sound. It's the natural reading of "when the path is a git repo".
- **Confidence:** medium

### Tier boundaries are strict: exactly 1,000 lines is "over soft", exactly 800 is "over target"

- **When:** `6b3494a`, `size_report.py` `tier`; tests `e1000.py`, `f800.py`
- **Slice:** 04
- **What happens now:** a file of 1,000 lines lands in "over soft (800)", not hard; 500 lines isn't listed at all. The alternative treats a limit as reached at the number itself (`>=`). The tests pin both boundaries.
- **The gap:** the intent says "target 500 / soft 800 / hard 1000" and "files over 500/800/1000"; slice 04's fixtures use 499/501/801/1001, which avoid the boundary.
- **Reach:** 06's tier-move detection inherits this.
- **Verdict:** sound. "Over 1,000" reads as strictly greater, and labels say "over".
- **Confidence:** medium

### A file is binary if its first 8 KB contain a NUL byte

- **When:** `6b3494a`, `size_report.py` `skip_reason`
- **Slice:** 04
- **What happens now:** a PNG has a NUL byte early and is skipped as binary (brain-cli's PNG is caught). A UTF-16 text file also has NULs and would be skipped as binary; a binary format with no NUL in its first 8 KB would be counted. The alternative uses an extension list. NUL sniffing is what git itself uses.
- **The gap:** the spec says "binary files" without a method.
- **Reach:** small; misses show up in the "binary" skip count.
- **Verdict:** sound
- **Confidence:** medium

### "Lockfiles" means a fixed list of 17 file names

- **When:** `6b3494a`, `size_report.py` `LOCKFILES`
- **Slice:** 04
- **What happens now:** `package-lock.json`, `yarn.lock`, `Cargo.lock`, `go.sum`, `poetry.lock` and 12 others are skipped by exact name, wherever they sit. A lockfile with an unlisted name would be counted.
- **The gap:** the spec says "lockfiles" without a list.
- **Reach:** adding a name is a one-line change.
- **Verdict:** sound
- **Confidence:** medium

### Modularity anchors use the size tiers as evidence

- **When:** `6b3494a`, `rubric.md` Modularity
- **Slice:** 01
- **What happens now:** a score of 1 cites "a file in the hard size tier with several unrelated sections"; a 3 cites "a file in the soft or hard tier that many others import". Size alone doesn't set the score; the anchor also needs unrelated sections or many importers. The alternative keeps size out of the rubric entirely, since the non-goals call size "report only".
- **The gap:** the spec doesn't say whether the size report feeds any score.
- **Reach:** ties the rubric to the size script's output (so the "source" and skip questions above matter for scores). On brain-cli, `src/cli.ts` at 1,692 lines will be the first candidate.
- **Verdict:** sound. Size is used as a pointer to evidence, not a limit, so it stays report-only.
- **Confidence:** medium

### Error anchors are built around four things: what, where, why, and a handle to trace

- **When:** `6b3494a`, `rubric.md` Errors
- **Slice:** 01
- **What happens now:** a 5 needs all four at the last hop of the traced failure path; a 3 is "what broke but not where or why", evidenced by a rethrow that drops the cause or a log line with no identifiers; a 1 is a swallowed error or a rethrow without the original. "Handle" is defined as an ID, a path, a request or command name, or the kept cause.
- **The gap:** none on the four things (the slice decided them); the worker chose which failure shapes map to 1 and 3.
- **Reach:** 02's trace spike will be judged against these four.
- **Verdict:** sound. It matches the slice's Decided list and the intent's "one real failure path traced end to end".
- **Confidence:** medium

## Next step

The user reviews `rubric.md` (slice 01) with the "How to score" and "shared on X" entries in hand, and decides how to handle the red `validate.py` check, before 02 and 03 start. Fix the `.gitattributes` match and the silent drops in 04 before 05 and 06 read its output.
