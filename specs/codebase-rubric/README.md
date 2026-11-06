# Codebase rubric

**Branch:** `claude/codebase-rubric` (to be created from `claude/agents-check-first`)

## Intent

> A skill block that reports file size in three tiers (target 500 / soft 800 / hard 1000 LOC) via a deterministic script, plus an agent rubric scoring architecture, modularity, abstraction, components, and how errors are described and traced, with evidence per score. Fills the Verify station.

How the user will know it worked:

> "I run `/codebase-rubric` on one of my real repos and get a scorecard file: a size table (files over 500/800/1000 lines) plus a 1–5 score for each of the five areas. Every score cites at least one file:line as evidence, and the error-tracing score includes one real failure path traced end to end. I'd trust it if I could check any score against its evidence in under a minute."

The size tiers and the five areas come from a screenshot the user shared (source not yet linked).

## Non-goals

- Blocking commits or enforcing size limits. Size is report only. For a gate later, adopt [dzhng's `ratchet-files`](https://github.com/dzhng/skills/blob/main/skills/engineering/ratchet-files/SKILL.md) with its budget near 1,000 lines.
- Installing dependencies, starting services, or triggering failures no existing test covers.
- Charts, dashboards, or comparing repos with each other.
- Running on every change. This is a periodic health check, not a per-task gate (design rule 3).

## Constraints

- Python 3 standard library and bash only. No new dependencies.
- In the target repo, write only `scorecards/<YYYY-MM-DD>.md`. Never overwrite: a same-day rerun writes `<date>-2.md`.
- `SKILL.md` under 8 KB, no em dashes in prose, full wiring per `AGENTS.md`.
- Works with no user present, like the sibling blocks. Anchor approval happens once at build time, never as a runtime prompt.
- Backward compatibility: none needed, this is a new skill.

## Slice graph

| # | Slice | Question it answers | Check | Depends on |
|---|---|---|---|---|
| 01 | rubric-anchors | What do 1, 3, 5 mean per area, with what evidence? | User approves `rubric.md` | none |
| 02 | trace-spike | Can an agent trace one real failure by reading, hop by hop? | User follows every hop | 01 |
| 03 | scoring-spike | Can each score be checked against its evidence in under a minute? | User times 3 random scores | 01 |
| 04 | size-script | Are tiers deterministic, with skips that hold? | `unittest` on fixtures | none |
| 05 | scorecard-contract | What shape must a scorecard have so a script can verify it? | `check_scorecard.py` on fixtures | 02, 03 |
| 06 | delta | Which scores changed and which files moved tiers since last time? | `unittest` on fixture pairs | 04, 05 |
| 07 | skill-flow | Does one run, by hand or unattended, write only a valid scorecard? | Real-repo run + checker | 02, 03, 05, 06 |
| 08 | wiring | Is the skill registered, evaluated, and tested in CI? | `validate.py`, `unittest`, grep | 07 |

Build order comes from **Depends on**. 01 and 04 can start in parallel; 02 and 03 can run in parallel after 01.

## Open questions

- **Where is the screenshot from?** **Recommended:** link the source in `rubric.md` for credit. The user provides it; not blocking.

## Decided in planning

- **Prove the hard part by hand first (02, 03).** If an agent can't produce evidence a person checks in under a minute, the scripts are wasted. From the fail-fast draft; the lean draft tested this last, which risks building everything before learning it fails.
- **Score deltas come from a script**, which reads marked tables in the previous scorecard. Deterministic, and it fails loudly if the markers were edited away. The lean draft had the agent compute score deltas; turned down because two runs could disagree.
- **A machine-checkable scorecard contract (05).** It makes "every score cites file:line" and "error trace present" checkable by a script. From the seams draft.
- **One existing test may run, with a timeout, even unattended.** This was the user's interview answer. The fail-fast draft argued unattended runs should read only; turned down because running an existing test is evidence-gathering, the same as `decision-checker` does. If the test needs missing dependencies, trace by reading and say so.
- **Size detection in one slice (04), not two.** The seams draft split skip rules from counting; turned down because both live in one script with one test file.
- **CI runs the script tests** (08), not just `validate.py`, so the tests can't silently rot. From the seams draft.
- **Lines are raw newline counts** of all lines. Skips: lockfiles, `vendor/`, `node_modules/`, `dist/`, `build/`, files marked `linguist-generated` or `linguist-vendored` in `.gitattributes`, files with a generated-code header, and binary files. The scorecard lists skip counts so misses are visible.
- Drafts were independent: three subagents with lean, fail-fast, and seams lenses.
- **`rubric.md` approved as written** by the user (2026-11-06), including its "How to score" rules (evidence before score; on a tie, take the lower score and say what would earn the higher). Those rules count as settled for 07.
- **Size rules settled by the user after the first ledger:** `node_modules/` and `vendor/` skipped at any depth, `dist/` and `build/` only at the repo root or a package root, no `third_party/`; **code files only** (docs, data, and images count as "not code"; this was not the recommended option); JSON skip keys are stable slugs; and **no pull request from this branch until 08**, keeping the `validate.py` check as written.
- **Tie rule reworded, approved by the user:** "pick the lower anchor; a 4 needs the 5 anchor to fit most of the repo, a 2 needs the 1 anchor to fit most of it."
- **Second repo for separation, approved by the user: [phuhien92/keen-design-system](https://github.com/phuhien92/keen-design-system).** A component library with no code file over 500 lines, the opposite shape of brain-cli. If it also scores all 3s, sharpen the anchors before 07.
- **One fresh scorer per area, approved by the user.** The keen-design-system check scored all five areas 4, and brain-cli scored four 3s: each scorer carried one impression across every area. A scorer that sees only its own area can't. The rubric also gains "not scored" (too little code, with scope named) and "most" as at least two-thirds of a listed sample. Costs about five scorers per run, acceptable for a periodic check.
- **Target repo: [phuhien92/brain-cli](https://github.com/phuhien92/brain-cli) at `7045e68`** (user's choice). It has three source files over 500 lines (`src/cli.ts` 1,692, `test/extensions.test.ts` 997, `src/extensions.ts` 540) and two files the skip rules must catch (`dist/src/cli.js` 1,579, a PNG under `assets/`). The session clone is read-only, so scorecards stay local.

## Next agent prompt

Status: 01 approved (tie rule reworded); 04 built. 02 and 03 ran on brain-cli (outputs in `spikes/`), waiting for the user's checks. Per-area scorers on keen-design-system gave 4, 4, 3, 4, 3 where one scorer gave all 4s (`spikes/03c-per-area-keen.md`): the change separates areas. Modularity anchor now accepts folder layout when git history is flat. Waiting on the user's checks of 02 and 03; then 05.

Before reporting a slice done, follow the `decision-checker` skill in Check mode on this branch and save `decisions.md`. Update this prompt before you end.
