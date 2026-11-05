# Agent Skills

This repo is a skill pack. Skills live under `skills/<name>/SKILL.md`. Slash commands under `.claude/commands/` activate them.

## When the user runs `/hien`

Read `skills/hien/SKILL.md` and follow it exactly. It loads Hien's public profile for the `twin` skill. If the files cannot be loaded, stop and say so. Do not invent their contents.

## When the user runs `/twin`

Read `skills/twin/SKILL.md` and follow it. Evidence or nothing: every trait points at a source. Profiles live outside this repo unless the user says otherwise.

## When the user runs `/radio-system-design-practice`

Read `skills/radio-system-design-practice/SKILL.md` and follow it exactly. Coach. One question per turn. Do not implement the product.

## When the user runs `/brain`

Read `skills/brain/SKILL.md` and follow it. It drives the `brain` CLI; if `brain` is not installed, say so and fall back to grep. The skill is copied from `phuhien92/brain-cli` — change it there first, then copy it here.

## When the user runs `/behavioral-story-depth`

Read `skills/behavioral-story-depth/SKILL.md` and follow it. Coach. One question per turn. Never invent metrics, names, or events; missing facts become questions. Load `probes.md` only in Drill mode.

## Adding a skill

See `ARCHITECTURE.md` for the full wiring. Short version:

1. Create `skills/<name>/SKILL.md` with `name` + `description` frontmatter.
2. Add `.claude/commands/`, `commands/`, and `.cursor/commands/` files that say “follow the `<name>` skill,” plus the `.cursor/skills/<name>` symlink.
3. List it in `README.md` and add a `/name` section here.
4. Add `evals/<name>.md` with at least three cases.
5. Run `python3 tools/validate.py` until it reports no errors.
