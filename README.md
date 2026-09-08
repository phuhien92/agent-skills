# Agent Skills

Personal skills for AI coding agents. Layout matches the [Agent Skills](https://github.com/addyosmani/agent-skills) pack: one directory per skill, slash commands as entry points, plugin manifests for Claude Code / Cursor.

```
  PRACTICE
 ┌──────────────────────────────────┐
 │  RADIO system design coaching    │
 │  one question → lock → next      │
 └──────────────────────────────────┘
  /radio-system-design-practice
```

## Commands

| What you're doing | Command | Key principle |
|---|---|---|
| Practice a frontend system design interview | `/radio-system-design-practice` | RADIO, one question at a time |

## Quick start

**Cursor** — this repo already maps `skills/` into `.cursor/skills/` (symlink). Open the repo, or add it as a project skill pack.

**Claude Code**

```
/plugin marketplace add https://github.com/phuhien92/agent-skills.git
/plugin install agent-skills@agent-skills
```

Then run `/radio-system-design-practice`.

**Any agent (skills CLI)**

```bash
npx skills add phuhien92/agent-skills --skill radio-system-design-practice
```

## Skills

| Skill | What it does | Use when |
|---|---|---|
| [radio-system-design-practice](skills/radio-system-design-practice/SKILL.md) | Coaches RADIO (Requirements → Architecture → Data model → Interfaces → Optimizations). Hidden rubric, one question, score, lock, next. | System design practice, news feed / autocomplete / docs / chat, `@solution.md` or an Excalidraw board |

## Project structure

```
agent-skills/
├── skills/
│   └── radio-system-design-practice/
│       ├── SKILL.md
│       └── examples.md
├── .claude/commands/          # Claude Code slash commands
├── .cursor/skills/            # Cursor: symlink to skills/
├── commands/                  # Extra slash-command copies
├── .claude-plugin/plugin.json
├── plugin.json
└── docs/
```

## How a skill is shaped

Each skill is a workflow, not a dump of notes:

- YAML frontmatter: `name` + `description` (what + when)
- Steps the agent must follow
- Supporting files loaded only when needed (`examples.md`)

## License

MIT
