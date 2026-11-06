# Getting started

## Cursor

Open this repository (or add it next to a practice repo). `.cursor/skills/` maps each skill directory as a symlink into `skills/`.

In chat:

```
/think-with-me
```

or

```
/radio-system-design-practice
```

For RADIO practice you can also `@` a `solution.md` / Excalidraw board and say “practice this with RADIO.”

## Claude Code

From a clone:

```
claude --plugin-dir /Users/hienluong/workspace/agent-skills
```

Then `/think-with-me` or `/radio-system-design-practice`.

## skills CLI

```bash
npx skills add phuhien92/agent-skills --skill think-with-me
npx skills add phuhien92/agent-skills --skill radio-system-design-practice
```
