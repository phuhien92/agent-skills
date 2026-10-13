# Agent Skills

This repo is a skill pack. Skills live under `skills/<name>/SKILL.md`. Slash commands under `.claude/commands/` activate them.

## When the user runs `/hien`

Read `skills/hien/SKILL.md` and follow it exactly. Load the colocated knowledge files, then follow `ENTRY.md`. If those files cannot be loaded, stop and say so. Do not invent their contents.

## When the user runs `/radio-system-design-practice`

Read `skills/radio-system-design-practice/SKILL.md` and follow it exactly. Coach. One question per turn. Do not implement the product.

## When the user runs `/brain`

Read `skills/brain/SKILL.md` and follow it. It drives the `brain` CLI; if `brain` is not installed, say so and fall back to grep. The skill is copied from `phuhien92/brain-cli` — change it there first, then copy it here.

## Adding a skill

1. Create `skills/<name>/SKILL.md` with `name` + `description` frontmatter.
2. Add `.claude/commands/<name>.md` that says “follow the `<name>` skill.”
3. List it in `README.md`.
