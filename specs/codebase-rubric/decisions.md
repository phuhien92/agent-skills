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

---

# Check 2: slice 05, and rubric and size-script changes since check 1

Check mode, run unattended (rule 7): no user present, every confidence capped at medium, saved without asking. Baseline: `specs/codebase-rubric/README.md` plus `slices/`. User approvals recorded under "Decided in planning" (size rules, tie rule, keen as second repo, one scorer per area, "not scored", "most" as two-thirds, 02 and 03 accepted) are the user's calls and aren't listed. Check 1's entries were applied in `19567d2` (git `check-attr`, symlinks counted, provenance line, `validate.py` check restored) and aren't re-listed.

- **Scope:** `6b3494a..d08119c` (`19567d2`, `fe979bc`, `ddb308e`, `91b2636`, `90d0b16`, `d08119c`). Focus: slice 05 (`scorecard.md`, `scripts/check_scorecard.py`, `scripts/test_check_scorecard.py`, `scripts/fixtures/good-keen.md`), plus changes to `rubric.md`, `size_report.py`, and the slice files.
- **Self-report:** the implementer isn't live. Its commit messages and the README "Next agent prompt" name no guesses, so this check rests on tracing.
- **Evidence run:** `python3 -m unittest discover -s skills/codebase-rubric/scripts` passes 16 tests. `check_scorecard.py` exits 0 on `good-keen.md`. `size_report.py` on brain-cli at `7045e68` lists the same three files as before (skipped: lockfile 1, symlink or not a file 1, not a code file 57, vendored or build folder 17). `tools/validate.py` exits 1, which the user accepted (no PR until 08). Throwaway checker probes ran outside the repo and were deleted. No keen-design-system clone exists here, so fixture values about that repo could not be checked.
- **Skipped as delegated:** marker names and section headings (05).
- **Trivial, folded:** 3 calls. The checker exits 2 on a usage error or unreadable file; `Date` and `Commit` are checked for presence, not format; `git check-attr` values other than `set` or `true` (such as `linguist-generated=1`) don't count as marked.

## Check these first

1. Any area, Errors included, can be "not scored", and then no error trace is required (needs-you, low).
2. The Modularity 5 anchor was loosened after the user approved `rubric.md` (unsound, low).
3. Stylesheets, HTML, MDX, and YAML count as "not a code file" (needs-you, low).

Five of the sixteen entries sit on how strict `check_scorecard.py` is (not-scored escape, sample counts, citations, unmarked skip counts, template rules it doesn't enforce). Slice 05's check named five failure cases and the checker covers exactly those, in shape only. The plan was foggy on what "a script can verify it" must prove beyond shape. Recommend sending that back through the spec before 06 builds on `parse` and 07 relies on the checker as its gate.

## needs-you

### Any area, Errors included, can be "not scored", and then no error trace is required

- **When:** `d08119c`, `check_scorecard.py` `problems` (`errors_scored`)
- **Slice:** 05
- **What happens now:** a scorecard marks Errors "not scored" with a scope and a reason, and leaves the trace section empty. The checker passes it. A probe marked all five areas "not scored" with no trace: the checker printed "ok" and exited 0. So an unattended run that scores nothing still passes the gate 07 relies on. The obvious alternative keeps the success test's floor: Errors always gets a score and a traced path, and only a limited number of other areas may be "not scored".
- **The gap:** slice 05 says a "not scored" area "passes only with a reason and a named scope" but not whether Errors may be skipped or how many areas may be. The intent says the scorecard has "a 1–5 score for each of the five areas" and "the error-tracing score includes one real failure path traced end to end".
- **Reach:** 07's check is "`check_scorecard.py` exits 0", so this sets the minimum a real run must produce. 06 must also handle "not scored" on both sides of a delta.
- **Verdict:** needs-you. How much a run may decline to score is the user's call. **Recommended call:** Errors may never be "not scored" (if no failure path is reachable, score it from what exists and say so), and fail the scorecard if more than two areas are "not scored". **To reverse:** delete those two checks; `errors_scored` returns to skipping the trace.
- **Confidence:** low

### Stylesheets, HTML, MDX, and YAML count as "not a code file"

- **When:** `fe979bc`, `size_report.py` `CODE_EXTENSIONS`, `CODE_NAMES`
- **Slice:** 04
- **What happens now:** the user decided "code files only (docs, data, and images count as not code)". The worker turned that into a fixed list of about 70 extensions. `.sql`, `.sh`, `.tf`, `.proto`, and `.graphql` count as code. `.css`, `.scss`, `.less`, `.html`, `.mdx`, and `.yaml` don't, so a 1,200-line stylesheet in a design system is skipped as "not a code file" and never reaches the size table. The keen fixture shows 61 such skips (unverified). The obvious alternative treats only what the user named (docs, data, images) as not code and counts stylesheets and markup as code.
- **The gap:** the user named three kinds of non-code; the spec gives no list, and stylesheets, templates, and config are none of the three.
- **Reach:** keen-design-system is the second test repo and a UI library, so the size table on the repos the user is calibrating with depends on this list.
- **Verdict:** needs-you. Where code ends is the user's definition. **Recommended call:** add `.css`, `.scss`, `.sass`, `.less`, `.html`, and `.mdx` to the code list; keep YAML, JSON, and Markdown as not code. **To reverse:** remove those extensions from `CODE_EXTENSIONS`.
- **Confidence:** low

### The rubric's sampling and "too little code" rules carry thresholds the user didn't set

- **When:** `91b2636`, `rubric.md` "How to score" rules 5 and 6
- **Slice:** 01
- **What happens now:** a scorer samples "at least six, or all of them if fewer" units for its area, and may mark the area "not scored" when it has "fewer than three units or no failure path a person can reach". On keen-design-system, every scorer set aside `packages/keen` (5 small files) as too little to score. The user approved "most" as two-thirds of a listed sample and a "not scored" option; the numbers six and three, and "no failure path a person can reach" as a reason to skip Errors, came from the worker.
- **The gap:** the approval recorded the idea, not the thresholds.
- **Reach:** a sample of six makes "most" mean 4 of 6, which one file can tip. The "no failure path" clause is what lets Errors escape the trace (entry above).
- **Verdict:** needs-you. The thresholds set how often areas go unscored. **Recommended call:** keep six and three, and drop "no failure path a person can reach" from rule 6 if the user takes the Errors recommendation above. **To reverse:** restore rules 5 and 6 as written in `91b2636`.
- **Confidence:** low

### Without a way to spawn agents, one scorer scores all five areas in turn, and the scorecard says so

- **When:** `91b2636`, `slices/07-skill-flow.md` Decided; `d08119c`, meta key `Scorers independent`
- **Slice:** 07, 05
- **What happens now:** a run in a tool that can't spawn subagents scores one area at a time, writing each score before reading the next area's anchors, and sets `Scorers independent | no` in the meta table. The checker accepts `no`. The obvious alternative stops with a clear error, since the user approved per-area scorers because a single scorer carried one impression across every area (keen scored all 4s that way).
- **The gap:** the user approved one fresh scorer per area but didn't say what happens when that isn't possible. The worker added the fallback to 07's **Decided** list, where the next worker will read it as the user's call.
- **Reach:** the fallback produces the exact failure the change was meant to fix, labeled but still passing the checker.
- **Verdict:** needs-you. It trades the reason for the change against never blocking a run. **Recommended call:** keep the fallback (unattended runs must not block) but move it out of 07's Decided list into an open question until the user confirms it. **To reverse:** delete the Decided line and the `Scorers independent` meta key.
- **Confidence:** medium

### Citations are checked for shape only, never against the repo

- **When:** `d08119c`, `check_scorecard.py` `CITATION`
- **Slice:** 05
- **What happens now:** a score whose evidence is `` `nope:1` `` or `` `localhost:8080` `` passes (probe). The checker reads only the scorecard, so a cited path that doesn't exist, or a line past the end of the file, is never caught. The obvious alternative takes the target repo as an optional argument and checks every cited path exists and every line is within the file.
- **The gap:** slice 05 asks for a shape "a script can verify" and lists "a score without a file:line" as a failure, without saying whether the file:line must be real.
- **Reach:** the user's trust test is checking any score against its evidence in under a minute; a citation to a missing file fails that test, and an unattended 07 run would not notice.
- **Verdict:** needs-you. It adds a second input to the checker's contract. **Recommended call:** add `--repo <path>` that checks each cited path and line range against the target repo, and have 07 always pass it. **To reverse:** remove the flag; the shape check stays.
- **Confidence:** medium

## unsound

### The Modularity 5 anchor was loosened after the user approved `rubric.md`

- **When:** `90d0b16`, `rubric.md` Modularity
- **Slice:** 01
- **What happens now:** the README records `rubric.md` as "approved as written" by the user. Afterwards the worker added to the 5 anchor: "If the history is squashed or too short to show one, use the folder layout instead: each feature or concern has its own folder or prefix." A repo with tidy folders can now earn a 5 without any history showing that a feature change touches a short list of files. The finding came from the 03c spike; the README lists no approval for this edit, unlike the tie rule and "not scored". The obvious alternative records the finding as an open question and leaves the approved anchor alone until the user decides.
- **The gap:** the spec didn't foresee squashed history.
- **Reach:** a 5 gets easier to reach, and later workers learn that approved anchors can change mid-build.
- **Verdict:** unsound. It changes the approved baseline without approval, the same pattern check 1 flagged for the `validate.py` line. **Redo from:** edits to `rubric.md` after approval take effect only once the README records the user approving them.
- **Confidence:** low

### The keen fixture states facts no spike recorded, and drops a hop from the trace

- **When:** `d08119c`, `scripts/fixtures/good-keen.md`
- **Slice:** 05
- **What happens now:** the fixture says it is "built from `specs/codebase-rubric/spikes/03c-per-area-keen.md`". Its scores, samples, and citations match 03c. But the commit `847e726` and the skip line ("generated header: 4, lockfile: 2, not a code file: 61") appear in no spike, and no keen clone is present to confirm them. The trace has four hops where 03c lists five (it drops `resolve.ts:23`). Bad cases are made by string edits in the tests, not fixture files, and the brain-cli spikes (02, 03) aren't used. The obvious alternative copies only recorded values and marks anything else as a placeholder.
- **The gap:** slice 05 says "Fixtures come from the spike outputs in 02 and 03" without saying what to do with fields the spikes didn't record.
- **Reach:** the README calls this "a fixture from the keen per-area run"; a later reader, or 06's tests, may treat the skip counts and SHA as real.
- **Verdict:** unsound. A fixture claimed as spike output contains values with no source. **Redo from:** every fixture value either comes from a recorded spike or a real script run, or is marked as illustrative.
- **Confidence:** low

### Each scorer is meant to see only its area's section, which leaves out the shared "How to score" rules

- **When:** `91b2636`, `slices/07-skill-flow.md` Seam; `rubric.md` line 3
- **Slice:** 07, 01
- **What happens now:** 07's seam says each scorer is "given only `rubric.md`'s section for its area plus the repo path". The rules a scorer must follow (evidence first, the tie rule, sample at least six and count two-thirds, "not scored", name the scope) live in "How to score", which isn't any area's section. Read literally, a scorer never sees them, and the scorecard's `Sample` and `Scope` columns then have no rule behind them. The obvious alternative gives each scorer "How to score" plus its own area.
- **The gap:** the user approved "a scorer that sees only its own area"; the wording of what "its own area" includes was the worker's.
- **Reach:** 07 will be built from this seam line.
- **Verdict:** unsound. The wording drops rules the scorer needs. **Redo from:** each scorer receives the shared "How to score" rules and its own area's anchors, and nothing about other areas or their scores.
- **Confidence:** medium

### Skip counts sit outside the markers, and the size table isn't validated

- **When:** `d08119c`, `scorecard.md` Size section; `check_scorecard.py` `parse`
- **Slice:** 05
- **What happens now:** the `Skipped:` line is plain text below `<!-- size:end -->`. Deleting it still passes (probe), and no script can read it back. Size rows aren't checked either: a row `| foo | lots | huge |` passes (probe). The template says to paste `size_report.py` rows, whose Tier text is "over hard (1000)", while the JSON uses `hard`; 06 must parse whichever lands there. The obvious alternative puts skip counts in their own marked table using the stable slug keys, requires numeric line counts, and fixes one tier vocabulary.
- **The gap:** slice 05's Decided list includes "skip counts" as a section, and the README says "the scorecard lists skip counts so misses are visible". Neither says they must be machine-checked.
- **Reach:** 06 detects tier moves from these rows; a missing skip line hides exactly the misses the README wanted visible.
- **Verdict:** unsound. A decided section can go missing and the checker still passes. **Redo from:** every section in slice 05's Decided list is required by the checker, and the tables 06 reads (size rows and skip counts) are marked, with numeric lines and one fixed tier vocabulary.
- **Confidence:** medium

### A sample is checked for the words "N of M" only

- **When:** `d08119c`, `check_scorecard.py` `SAMPLE`
- **Slice:** 05
- **What happens now:** `9 of 3` and `0 of 0` both pass (probe). The rubric says a 4 or a 2 needs the anchor to fit at least two-thirds of a sample of at least six (or all units if fewer), and the checker tests none of it. The obvious alternative at least requires `1 <= N <= M`.
- **The gap:** slice 05 lists "each area's sample" as a section without saying what makes one valid.
- **Reach:** the sample is the only number that lets a person check why a score is a 4 and not a 3; an impossible fraction makes it noise.
- **Verdict:** unsound. A count above its own sample size passes. **Redo from:** a sample is a count out of a non-empty set, `N <= M` and `M >= 1`. Whether the checker should also test two-thirds against the score is a separate call for the user.
- **Confidence:** medium

### The template's "rules the checker enforces" and the checker disagree

- **When:** `d08119c`, `scorecard.md` rule list; `check_scorecard.py` `problems`
- **Slice:** 05
- **What happens now:** the template says "Not scored ... Sample is `-`", but a "not scored" row with `7 of 10` passes (probe). The other way round, the checker fails a numeric score with no Scope, but the template's rule list doesn't mention Scope for numeric scores. An agent filling the template follows one, the checker enforces the other. The obvious alternative keeps one list, matched by the tests.
- **The gap:** the spec doesn't say whether the template or the script is the source of truth for the rules.
- **Reach:** 07's SKILL.md will point at the template; 06 reads what the checker accepts.
- **Verdict:** unsound. The heading promises enforcement that doesn't exist. **Redo from:** each rule the template lists as enforced has a check and a test, and every check the script makes is in that list.
- **Confidence:** medium

## sound

### "Package root" means a folder holding one of 12 manifest files

- **When:** `fe979bc`, `size_report.py` `PACKAGE_MARKERS`, `in_build_dir`
- **Slice:** 04
- **What happens now:** `packages/app/dist/bundle.js` is skipped because `packages/app/package.json` exists; `src/build/compiler.ts` is counted because `src/` has no manifest. The markers are `package.json`, `pyproject.toml`, `setup.py`, `Cargo.toml`, `go.mod`, `pom.xml`, Gradle files, `composer.json`, `Gemfile`, `mix.exs`, and `pubspec.yaml`, checked on disk.
- **The gap:** the user said "repo root or a package root" without defining a package root.
- **Reach:** a language with an unlisted manifest gets its `dist/` counted; adding a name is one line.
- **Verdict:** sound. It's the usual meaning of a package root.
- **Confidence:** medium

### Skip reasons are tried in a fixed order, so each file counts once under the first match

- **When:** `fe979bc`, `size_report.py` `skip_reason`
- **Slice:** 04
- **What happens now:** lockfile, then vendored or build folder, then not code, then marked by git, then binary, then generated header. A Markdown file inside `dist/` counts as "vendored or build folder", not "not a code file", and a PNG counts as "not a code file", so "binary" now fires only for code-named files.
- **The gap:** the spec lists skip kinds, not their precedence.
- **Reach:** totals stay right; per-reason counts shift if the order changes, which 06 would see as a delta.
- **Verdict:** sound
- **Confidence:** medium

### The five areas must appear with exact names, in a fixed order

- **When:** `d08119c`, `check_scorecard.py` `AREAS`
- **Slice:** 05
- **What happens now:** a scorecard listing Errors before Components, or writing "Error handling", fails with "areas must be Architecture, Modularity, Abstraction, Components, Errors in order".
- **The gap:** the spec names the five areas but not order or spelling.
- **Reach:** lets 06 match rows by name without fuzzy matching.
- **Verdict:** sound
- **Confidence:** medium

### An error trace needs at least two numbered hops, each starting with a `path:line`

- **When:** `d08119c`, `check_scorecard.py` `parse`, `problems`
- **Slice:** 05
- **What happens now:** only lines starting with `1.`, `2.`, ... between the trace markers count as hops. One hop fails; a bullet list counts as zero hops and fails. Whether the hops really connect, end to end, is left to the person.
- **The gap:** the spec says "error trace hop by hop" and fails on "no error trace", without a minimum.
- **Reach:** two hops is a low floor (02 had 9, 03c had 5), but any more is a guess about repo shape.
- **Verdict:** sound
- **Confidence:** medium

### `parse()` returns raw strings by column position, and 06 will import it

- **When:** `d08119c`, `check_scorecard.py` `parse`
- **Slice:** 05
- **What happens now:** `parse(text)` returns `meta` (a dict), `size` and `scores` (lists of dicts of strings), `trace` (hop lines), and `delta` (text). Columns are matched by position, so an extra cell is dropped and a `|` inside evidence silently cuts the evidence short (probe: still passes). It raises only when a marker is missing or repeated.
- **The gap:** the spec says 06 reads the marked tables; the shape of that read is new.
- **Reach:** 06 copies this shape; strings keep `not scored` and numbers in one column without conversion.
- **Verdict:** sound. Simple and enough for a delta of areas and scores.
- **Confidence:** medium

## Next step

The user answers the three "Check these first" entries, then the checker gets its strictness pass (skip counts and sample counts marked and checked, template and checker matched) before 06 starts reading `parse`.

---

# Check 3: slice 06, and the second ledger's fixes

Check mode, run unattended (rule 7): no user present, every confidence capped at medium, saved without asking. Baseline: `specs/codebase-rubric/README.md` plus `slices/`. The calls the README records "after the second ledger" (three areas scored, styles and markup as code, `--repo`, sample sizes, one-agent fallback, folder layout in Modularity 5) are the user's and aren't listed.

- **Scope:** `86a07e8..a975445` (`58c31b8`, `8bf8fe7`, `a975445`). Focus: slice 06 (`scripts/delta.py`, `scripts/test_delta.py`), plus the fixes to `check_scorecard.py`, `scorecard.md`, `size_report.py`, the keen fixture, and spike 03c.
- **Self-report:** the implementer isn't live. Commit messages and the README "Next agent prompt" name no guesses, so this check rests on tracing.
- **Evidence run:** `python3 -m unittest discover -s skills/codebase-rubric/scripts` passes 29 tests. Throwaway probes of `delta.py` and `check_scorecard.py` ran in the session scratchpad and were deleted. No keen-design-system clone exists here, so the keen SHA and skip counts could not be checked.
- **Second ledger, fix status:** confirmed fixed: CSS, SCSS, Less, HTML, MDX counted as code; at least three areas scored; each scorer gets "How to score" (07 seam); `Skipped:` inside the size markers and size rows validated; samples need 1 <= M and N <= M; the trace's `resolve.ts:23` hop restored; `--repo` catches a missing file and a line past the end. Resolved by the user's calls: Errors "not scored", sampling thresholds, the one-agent fallback, Modularity 5. Still open: the template's enforced-rules list (re-listed below, since the fix changed it), the keen fixture's unsourced values, and two `--repo` gaps (both new entries below).
- **Skipped as delegated:** delta wording (06).
- **Trivial, folded:** 3 calls. Score text is compared exactly, so "not scored" to "Not Scored" shows as a change though the checker accepts both; `.sass` and `.htm` were added beside the extensions the user named; `2026-11-06-1.md` and `2026-11-06.md` sort as the same scorecard.

## Check these first

1. The keen fixture's commit and skip counts were made "backed by the spike" by writing them into the spike afterwards (unsound, low).
2. `delta.py` diffs scorecards the checker rejects (unsound, medium).
3. `size_report.py`'s "(none over 500)" row fails the checker and `delta.py` reads it as a file (unsound, medium).

Three of the seven entries sit on the seam between `size_report.py`, `check_scorecard.py`, and `delta.py`: each script has its own idea of a valid size table. Recommend the spec name one owner for "valid scorecard" (the checker) and have the other two defer to it before 07 wires them together.

## unsound

### The keen fixture's commit and skip counts were "backed by the spike" by editing the spike to match

- **When:** `58c31b8`, `spikes/03c-per-area-keen.md` line 3, `scripts/fixtures/good-keen.md`
- **Slice:** 05
- **What happens now:** check 2 found that the fixture's commit `847e726` and its skip line ("generated header: 4, lockfile: 2, not a code file: 61") appeared in no spike. The fix added both to the 03c spike's intro, in the same commit, as "Size run with the code-only rules", with no command, date, or output recorded. One commit later (`8bf8fe7`) CSS, SCSS, HTML, and MDX became code, so a "not a code file" count of 61 for a design system describes rules that no longer apply. The obvious alternative reruns `size_report.py` on a keen clone, records that run in the spike, or marks the values in the fixture as illustrative.
- **The gap:** check 2's redo said each fixture value must come from a recorded spike or a real run; it didn't say a spike can't be amended after the fact.
- **Reach:** spikes are the evidence the user accepted 02 and 03 on. Later workers learn that a missing source can be fixed by writing it into the source.
- **Verdict:** unsound. The evidence was made to match the claim, not the other way round. **Redo from:** a spike is a record of a run; a fact added later names the run that produced it (command, commit, date), and counts made under rules since changed are marked stale.
- **Confidence:** low

### `delta.py` diffs scorecards the checker rejects

- **When:** `a975445`, `delta.py` `delta`
- **Slice:** 06
- **What happens now:** `delta.py` calls only `parse`, which checks that markers exist. Probes, each on a scorecard `check_scorecard.py` rejects:
  - a previous row `` | `a.ts` | lots | huge | `` gives "`a.ts`: huge → over target (500) (lots → 600 lines)";
  - a previous scorecard missing its Components row gives "Components: missing → 4";
  - a previous row with only two cells is dropped by `parse`, so the file shows as "New over 500".

  The docstring says it "exits 1 with a reason if either file breaks the contract". The obvious alternative runs `check_scorecard.problems` on both files and exits 1 with those reasons if either has any.
- **The gap:** slice 06 says "a previous file with missing markers exits 1 with a reason, never guesses", naming only markers.
- **Reach:** 07 pastes this output into the new scorecard, so a damaged old scorecard produces a confident, wrong delta. Refusing would also refuse scorecards written under an older contract; that's the price of "never guesses".
- **Verdict:** unsound. It prints a delta from tables it knows nothing about, while claiming it checks the contract. **Redo from:** a delta is printed only when both scorecards pass `check_scorecard.problems`; otherwise exit 1 with the checker's reasons.
- **Confidence:** medium

### `size_report.py`'s "(none over 500)" row fails the checker, and `delta.py` reads it as a file

- **When:** `58c31b8`, `check_scorecard.py` size-row check; `a975445`, `delta.py`; existing `size_report.py` `as_text`
- **Slice:** 04, 05, 06
- **What happens now:** on a repo with no code file over 500 lines (keen-design-system, the user's second test repo), `size_report.py` prints a row `| (none over 500) | | |`. The template says to paste its rows. Pasted, the checker fails: "bad row for (none over 500): lines '', tier ''". If one gets through as the previous scorecard, `delta.py` reports "Now under 500 or gone: `(none over 500)` (was  lines)". The script also prints its own header and separator, which pasted under the template's header becomes a second, failing row. The obvious alternative makes what the size script prints for pasting exactly what the checker accepts, with an empty table meaning "none over 500".
- **The gap:** slice 05 says to paste rows from `size_report.py`; no slice says the two must agree on the empty case or the header.
- **Reach:** 07's success test is a real run plus a passing checker; on any repo like keen it fails on the first try.
- **Verdict:** unsound. Two scripts in the same pipeline disagree on a valid size table. **Redo from:** the rows `size_report.py` emits for a scorecard pass `check_scorecard.py` unchanged, including when no file is over 500, and `delta.py` never treats a placeholder as a path.
- **Confidence:** medium

### The template still lists rules the checker doesn't enforce (open from check 2)

- **When:** `58c31b8`, `scorecard.md` "Rules the checker enforces"
- **Slice:** 05
- **What happens now:** the list was rewritten, but three rules on it still have no check. Probes, each passing: Errors "not scored" with the reason "didn't feel like it" (the list says Errors may be skipped "only when no failure path a person can reach exists"); a "not scored" row with Sample `7 of 10` (the list says put `-`); `Skipped: whatever` (the list implies skip counts from `size_report.py`). The obvious alternative either adds a check and test for each or moves them under a heading such as "Rules for the scorer".
- **The gap:** the spec doesn't say whether the template or the script is the source of truth; check 2 asked for one list matched by tests.
- **Reach:** 07's SKILL.md points at this list; an unattended run that skips Errors for any stated reason passes the gate.
- **Verdict:** unsound. The heading still promises enforcement that doesn't exist. **Redo from:** each rule under "enforces" has a check and a test, and every check the script makes is on the list.
- **Confidence:** medium

### `--repo` accepts citations outside the repo and reversed line ranges

- **When:** `8bf8fe7`, `check_scorecard.py` `citation_problems`
- **Slice:** 05
- **What happens now:** the user decided the checker verifies citations against the repo. It joins each cited path onto the repo folder and checks the file exists and the last line is in range. A citation `` `../outside.ts:2` `` passes when a file sits next to the repo, and `` `cli.ts:150-20` `` passes because only the end line is compared with the length (probes). The obvious alternative requires the resolved path to stay inside the repo and the start line to be no greater than the end line.
- **The gap:** the user's call named the check, not what counts as "in the repo".
- **Reach:** small in practice, but the user's trust test is checking a citation in under a minute, and a reversed range or an outside path can't be checked.
- **Verdict:** unsound. A citation the user couldn't follow in the target repo passes the check meant to catch it. **Redo from:** a cited path resolves inside `--repo`, and a range has 1 <= start <= end <= file length.
- **Confidence:** medium

## sound

### The previous scorecard is the newest date-named file that sorts before the current one, with same-day suffixes ordered by number

- **When:** `a975445`, `delta.py` `previous_in`, `order_key`
- **Slice:** 06
- **What happens now:** with `--dir scorecards/ scorecards/2026-11-06-10.md`, the script picks `2026-11-06-2.md`, not `2026-11-06-9.md` by text order, and never the current file itself. Files not named `<YYYY-MM-DD>.md` or `<YYYY-MM-DD>-<n>.md` (such as `notes.md`) are ignored. A current file without such a name is refused, so 07 must write the scorecard under its final name before running `delta.py --dir`. The spec's literal reading, the newest file by name, would sort `-10` before `-2` and could pick the current file.
- **The gap:** slice 06 says "the newest file in `scorecards/` by name", which doesn't cover same-day reruns past `-9` or the current file already being in the folder.
- **Reach:** 07's step order is fixed by this: write, then delta, then check.
- **Verdict:** sound. It keeps the spec's intent where the literal rule breaks.
- **Confidence:** medium

### The delta reports score changes and tier-label moves only; renames show as one file gone and one new

- **When:** `a975445`, `delta.py` `delta`
- **Slice:** 06
- **What happens now:** a file growing from 610 to 790 lines stays "over target" and isn't mentioned. A file renamed from `a.ts` to `b.ts` shows as "New over 500: `b.ts`" and "Now under 500 or gone: `a.ts`" (probe). Changes in skip counts and in the commit are not reported. The alternatives would report line growth within a tier, or detect renames with git, which the script can't reach (it reads only two scorecards).
- **The gap:** slice 06 asks which scores changed and which files moved tiers, and puts trends out of scope.
- **Reach:** a skip-count change (the README's "misses are visible") would need a later slice.
- **Verdict:** sound. It answers exactly the slice's question from the two files it is given.
- **Confidence:** medium

## Next step

Make the three scripts agree on one valid scorecard (the checker owns it; `delta.py` and `size_report.py` defer to it), and rerun or mark the keen spike values, before 07 builds the skill on top of them.

---

# Check 4: close-out

Check mode, run unattended (rule 7): no user present, every confidence capped at medium, saved without asking. Baseline: `specs/codebase-rubric/README.md` plus `slices/`. The README's "Decided in planning" calls are the user's, including the success test accepted on the brain-cli scorecard, and aren't listed.

- **Scope:** `d9f9bb4..9b5d7fb` (`cd35b96`, `186ad47`, `9b5d7fb`): the third ledger's fixes, slice 07 (`skills/codebase-rubric/SKILL.md`, `spikes/07-brain-cli-scorecard.md`), and slice 08 wiring (three command files, the `.cursor/skills` link, `README.md`, `AGENTS.md`, three manifests, `evals/codebase-rubric.md`, `.github/workflows/validate.yml`, `ARCHITECTURE.md`).
- **Self-report:** the implementer isn't live. Commit messages and the README "Next agent prompt" name no guesses, so this check rests on tracing.
- **Evidence run:** `python3 tools/validate.py` prints "7 skills · 0 errors · 0 warnings" and exits 0. `python3 -m unittest discover -s skills/codebase-rubric/scripts` passes 31 tests. `check_scorecard.py specs/codebase-rubric/spikes/07-brain-cli-scorecard.md --repo /home/user/phuhien92/brain-cli` prints `ok`. brain-cli is at `7045e68`; its only change is the untracked `scorecards/2026-11-06.md`, identical to the spike. `size_report.py` on brain-cli reproduces the spike's size table and skip line. `grep -r "—" skills/codebase-rubric` finds nothing. `SKILL.md` is 3,786 bytes. Throwaway probes of `delta.py` and `check_scorecard.py` ran in the session scratchpad and were deleted. No keen-design-system clone exists here, so its new skip counts couldn't be rerun.
- **Third ledger, fix status (`cd35b96`):** confirmed fixed: `delta.py` refuses scorecards the checker rejects (tested); the "(none over 500)" row is gone and an empty size table passes the checker; `--repo` rejects paths outside the repo and backwards ranges (tested); the keen spike now names the run behind its counts (`size_report.py`, current rules, 2026-11-06, commit checked with `git log -1`), which is what the redo asked, though the counts couldn't be rerun here. Mostly fixed: the template's enforced-rules list; one mismatch remains (entry below).
- **Skipped as delegated:** step wording and order in `SKILL.md` (07), README placement and wording (08).
- **Trivial, folded:** 2 calls. `ARCHITECTURE.md:96` and `README.md:158` still describe CI as running only the validator, though it now runs the script tests too; the three command files share one body word for word.

## Check these first

1. When `delta.py` refuses the previous scorecard, the skill says nothing, and the scorecard ships saying "First run." (needs-you, low).
2. `Rubric approved` is set by a rule an unattended run can't check (unsound, low).
3. `ARCHITECTURE.md` records "17 unsound calls, all fixed"; the ledgers hold 15, and not all were fixed (unsound, medium).

## needs-you

### When `delta.py` refuses the previous scorecard, the skill says nothing, and the scorecard ships saying "First run."

- **When:** `186ad47`, `SKILL.md` workflow steps 4 to 6
- **Slice:** 07
- **What happens now:** step 4 writes the scorecard with `First run.` in its delta section; step 5 runs `delta.py --dir` and replaces that with its output. Since `cd35b96`, `delta.py` exits 1 when the previous scorecard fails the checker: one hand-edited, or written before the contract last changed. A probe with a previous scorecard whose `Rubric approved` read `maybe` gave "delta: previous scorecard is not valid ..." and exit 1. The skill names no action for that, and the checker in step 6 doesn't look inside the delta section, so a scorecard left saying `First run.` (or holding the error text) prints `ok` (probe). Every later run hits the same broken previous file. The obvious alternatives: write a line such as "No delta: <reason from delta.py>" and carry on, or stop and report.
- **The gap:** slice 06 says `delta.py` "exits 1 with a reason, never guesses"; slice 07 says never wait, and doesn't say what a run does with that exit.
- **Reach:** the README pitches the skill as "shows what changed since the last one"; one bad old file silently turns that off for every future run, and the scorecard claims there was no earlier run.
- **Verdict:** needs-you. Whether a broken history fails the run or degrades to a note is a product call. **Recommended call:** on exit 1, put "No delta: " plus `delta.py`'s reason in the delta section, say so in the hand-back, and never leave `First run.` when an earlier scorecard exists. **To reverse:** drop that line from step 5 and treat exit 1 as a failed run.
- **Confidence:** low

## unsound

### `Rubric approved` is set by a rule an unattended run can't check

- **When:** `186ad47`, `SKILL.md` workflow step 4
- **Slice:** 07
- **What happens now:** step 4 says `Rubric approved` is `yes` "unless `rubric.md` was edited after the user approved it." Nothing in the skill records when or what the user approved: `rubric.md` carries no approval date, version, or hash, and the approval lives only in this spec's README, which an installed copy of the skill (`npx skills add`) doesn't ship. A scorer in another repo has no way to tell, so the field will read `yes` every time, including after the anchors change. The obvious alternative records the approval where the run can read it (for example an "Approved: <date>" line in `rubric.md` that any edit must clear) and derives the field from that.
- **The gap:** slice 07's no-user rule says "say if anchors were unapproved" without saying how a run would know.
- **Reach:** the field exists so a reader can trust the anchors behind a score; a field that can't be false tells them nothing, and later anchor edits (as happened once in check 2) would go unflagged.
- **Verdict:** unsound. A meta field the checker requires is filled by a rule nobody can evaluate. **Redo from:** `Rubric approved` is derived from an approval record shipped with the skill, and editing the anchors without a new approval makes it `no`.
- **Confidence:** low

### `ARCHITECTURE.md` records "17 unsound calls, all fixed"; the ledgers hold 15, and not all were fixed

- **When:** `9b5d7fb`, `ARCHITECTURE.md` decision entry "codebase-rubric is the Verify block", "Where it can fail"
- **Slice:** 08
- **What happens now:** the entry says "Three `decision-checker` ledgers during the build found 17 unsound calls, all fixed; the user made 14 calls along the way." The three checks list 4, 6, and 5 unsound entries, 15 in all. Some were closed by the user accepting them rather than by a fix (check 3 records the loosened Modularity 5 anchor as "resolved by the user's calls"), and the template mismatch below is still open. The "14 calls" figure has no list behind it to check. The obvious alternative states counts that match the ledger, or links to `specs/codebase-rubric/decisions.md` instead of counting.
- **The gap:** slice 08 asked for "a decision entry" without saying what evidence it may summarise.
- **Reach:** `ARCHITECTURE.md` is the durable record the next skill's builder reads; a wrong count there teaches that the summary needn't match the ledger.
- **Verdict:** unsound. A durable record states figures its own source contradicts. **Redo from:** every count in the decision entry matches `decisions.md`, and "fixed" is used only for entries whose code changed.
- **Confidence:** medium

### The template says a sample needs 1 ≤ N ≤ M; the checker accepts `0 of 6` (open from check 3)

- **When:** `cd35b96`, `scorecard.md` "Rules the checker enforces"; `check_scorecard.py` sample check (unchanged)
- **Slice:** 05
- **What happens now:** `cd35b96` moved the unenforced rules under "Your job, not the checker's", which fixes most of check 3's entry. One line still disagrees: the list says a numeric score has "a Sample of the form `N of M` with 1 ≤ N ≤ M", while the checker only requires 1 ≤ M and N ≤ M, so `0 of 6` passes (its error message says exactly that). The obvious alternative makes the two say the same thing, either way: `0 of 6` is a plausible sample for a score of 1.
- **The gap:** check 3's redo ("each rule under 'enforces' has a check and a test") was applied to the rules it named, not re-swept.
- **Reach:** small; the skill points scorers at this list, so a correct `0 of M` sample looks forbidden to them.
- **Verdict:** unsound. The heading still promises a check that doesn't exist. **Redo from:** the sample rule on the list and the checker's sample check state the same bounds, with a test for N = 0.
- **Confidence:** medium

## sound

### The errors scorer may run one existing test, capped at 120 seconds

- **When:** `186ad47`, `SKILL.md` non-negotiable 4
- **Slice:** 07
- **What happens now:** if an existing test triggers the traced failure, the errors scorer may run it once; a run longer than 120 seconds is cut off and the trace stands on reading alone. The brain-cli run ran no test because `node_modules` wasn't installed, and said so in the trace. The user's planning call said "one existing test may run, with a timeout", without a number.
- **The gap:** the timeout length.
- **Reach:** a slow suite's single test may be cut off; the trace still exists by reading, so nothing blocks.
- **Verdict:** sound. A short cap fits a read-mostly survey and the user's "never block" rule; easy to change in one place.
- **Confidence:** medium

### The eval file has seven cases, four beyond the three slice 08 named

- **When:** `9b5d7fb`, `evals/codebase-rubric.md`
- **Slice:** 08
- **What happens now:** the three named cases are there (a score without evidence fails, only the scorecard is written, untested failures are never triggered). Added: scorers stay independent, too little code is "not scored", a same-day rerun never overwrites, and a second run shows what changed. Each one tests a rule the spec or the user decided; none adds behaviour.
- **The gap:** the slice set a minimum, not a list.
- **Reach:** more cases to keep in step when the skill changes; they cover the user's own calls (independence, "not scored", never overwrite, delta).
- **Verdict:** sound. Every extra case maps to a decided rule.
- **Confidence:** medium

## Next step

Decide the delta-refusal behaviour (Check these first, 1), then record the rubric approval where the skill can read it and correct the `ARCHITECTURE.md` counts before opening the PR.
