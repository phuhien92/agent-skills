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

## When the user runs `/decision-checker`

Read `skills/decision-checker/SKILL.md` and follow it. Review. Never change code. Rank decisions least-confident first. Load `ledger.md` only when writing the ledger. Load `harness.md` only when another workflow or a hook calls it, or when wiring it in as a gate.

## Agents check before the human reviews

For build, review, or research work (including authoring skills here), have independent subagents do the front-loaded work first: drafting, verifying, and critiquing each other's output with fresh context. Hand the user the checked result plus a short ledger of the decisions made on their behalf, least-confident first (`/decision-checker` produces it). Ask before starting only when intent or scope is unclear.

## Adding a skill

See `ARCHITECTURE.md` for the full wiring. Short version:

1. Create `skills/<name>/SKILL.md` with `name` + `description` frontmatter.
2. Add `.claude/commands/`, `commands/`, and `.cursor/commands/` files that say “follow the `<name>` skill,” plus the `.cursor/skills/<name>` symlink.
3. List it in `README.md` and add a `/name` section here.
4. Add `evals/<name>.md` with at least three cases.
5. Run `python3 tools/validate.py` until it reports no errors.
