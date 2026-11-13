# Agent Skills

This repo is a skill pack. Skills live under `skills/<name>/SKILL.md`. Slash commands under `.claude/commands/` activate them.

## When the user runs `/think-with-me`

Read `skills/think-with-me/SKILL.md` and follow it exactly. Load the colocated knowledge files, then follow `ENTRY.md`. If those files cannot be loaded, stop and say so. Do not invent their contents.

## When the user runs `/radio-system-design-practice`

Read `skills/radio-system-design-practice/SKILL.md` and follow it exactly. Coach. One question per turn. Do not implement the product.

## When the user runs `/brain`

Read `skills/brain/SKILL.md` and follow it. It drives the `brain` CLI; if `brain` is not installed, say so and fall back to grep. The skill is copied from `phuhien92/brain-cli` — change it there first, then copy it here.

## When the user runs `/behavioral-story-depth`

Read `skills/behavioral-story-depth/SKILL.md` and follow it. Coach. One question per turn. Never invent metrics, names, or events; missing facts become questions. Load `probes.md` only in Drill mode.

## When the user runs `/slice-spec`

Read `skills/slice-spec/SKILL.md` and follow it. Plan. One question per turn, with a recommended answer. Write only under `specs/<feature>/`. Load `spec-format.md` when writing the spec and `drafting.md` only when the first draft has four or more slices.

## When the user runs `/codebase-rubric`

Read `skills/codebase-rubric/SKILL.md` and follow it. Survey. Write only `scorecards/<date>.md` in the target repo. One independent scorer per area; every score cites `path:line`. Load `rubric.md` for the scorers and `scorecard.md` when writing. Run `scripts/check_scorecard.py --repo` until it prints `ok`.

## When the user runs `/decision-checker`

Read `skills/decision-checker/SKILL.md` and follow it. Review. Never change code. Rank decisions least-confident first. Load `ledger.md` only when writing the ledger. Load `harness.md` only when another workflow or a hook calls it, or when wiring it in as a gate.

## When the user runs `/explainer-video`

Read `skills/explainer-video/SKILL.md` and follow it. Make. Settle style, format, length and voice in one question with recommendations; load `styles.md` before recommending a style. Time beats with `scripts/vo_lines.py`. Review stills against `checks.md` before the full render. Ask before spending credits on text to speech.

## When the user runs `/house-style-design`

Read `skills/house-style-design/SKILL.md` and follow it. Make. Read the house style and the project's rules before drawing; load `drawing.md` when drawing. Anything new gets three distinct directions before one is polished. Characters stay original. Mechanics on a card are placeholders unless they come from the project's data; don't edit the project unasked.

## When the user runs `/reference-originality`

Read `skills/reference-originality/SKILL.md` and follow it. Translate. Use it unasked when the user shares another product's screenshots or a spec that mirrors one. Read the project's originality rule first; one keep/leave table and an original brief; flag the conflict once, not every turn.

## Agents check before the human reviews

For build, review, or research work (including authoring skills here), have independent subagents do the front-loaded work first: drafting, verifying, and critiquing each other's output with fresh context. Hand the user the checked result plus a short ledger of the decisions made on their behalf, least-confident first (`/decision-checker` produces it; in Claude Code, hand that check to the `decision-checker` subagent so the author doesn't review itself). Ask before starting only when intent or scope is unclear.

## Keep the human posted on long work

In an interactive session, send a one- or two-line status at each phase change (mockup ready, tests green, PR open) and at least every ~10 minutes of tool work: what's done, what's next, what you need. Worktrees when the cwd isn't a git repo, and the fetch-refspec fix for false "unpushed" warnings, are in `docs/long-agent-runs.md`.

## Adding a skill

See `ARCHITECTURE.md` for the full wiring. Short version:

1. Create `skills/<name>/SKILL.md` with `name` + `description` frontmatter.
2. Add `.claude/commands/`, `commands/`, and `.cursor/commands/` files that say “follow the `<name>` skill,” plus the `.cursor/skills/<name>` symlink.
3. List it in `README.md` and add a `/name` section here.
4. Add `evals/<name>.md` with at least three cases.
5. Run `python3 tools/validate.py` until it reports no errors.
