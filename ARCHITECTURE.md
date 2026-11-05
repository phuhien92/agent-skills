# Architecture

One-page map of this skill pack. Adapted from the layout of [wshobson/agents](https://github.com/wshobson/agents/blob/main/ARCHITECTURE.md), scaled down for a personal pack used in Claude Code and Cursor.

## Invariants

1. **One source of truth per skill.** Each skill is authored once, at `skills/<name>/`. Everything else (slash commands, Cursor links, plugin manifests) only points at it. Never copy skill text into another folder.
2. **One canonical context file.** `AGENTS.md` is the only context file written by hand. `CLAUDE.md` is a symlink to it. Keep it under ~150 lines; it routes, it doesn't teach.
3. **Progressive disclosure.** `SKILL.md` holds the workflow and stays under 8 KB. Long material (examples, probe banks, knowledge files) lives next to it and is loaded only when the workflow says so.
4. **Every skill is wired the same way.** A skill isn't done until it has all five touchpoints listed under *Wiring*. `tools/validate.py` checks them.
5. **Checks give a fix, not just a failure.** Every validator finding prints the exact change to make.
6. **Skills never invent the user's facts.** Skills that work on personal material (stories, notes, opinions) ask for missing facts instead of filling them in. Evals check this.

## Layout

```
agent-skills/
├── AGENTS.md                     # canonical context file (routing only)
├── CLAUDE.md                     # symlink → AGENTS.md
├── ARCHITECTURE.md               # this file
├── README.md                     # user-facing landing page
├── skills/<name>/                # SOURCE OF TRUTH
│   ├── SKILL.md                  # frontmatter: name, description ("Use when …")
│   └── *.md                      # optional, loaded on demand
├── .claude/commands/<name>.md    # Claude Code slash command → "follow the <name> skill"
├── commands/<name>.md            # plugin command copy (same text)
├── .cursor/commands/<name>.md    # Cursor slash command (same text)
├── .cursor/skills/<name>         # symlink → ../../skills/<name>
├── .claude-plugin/plugin.json    # Claude Code plugin manifest
├── plugin.json                   # generic manifest
├── evals/<name>.md               # behavior cases per skill
├── tools/validate.py             # structural checks (stdlib only)
├── .github/workflows/validate.yml
└── docs/
```

## Wiring (per skill)

| Touchpoint | Path | Checked by |
|---|---|---|
| Skill body | `skills/<name>/SKILL.md` with `name` matching the folder and a `description` | `validate.py` |
| Claude Code command | `.claude/commands/<name>.md` | `validate.py` |
| Plugin command copy | `commands/<name>.md` | `validate.py` |
| Cursor | `.cursor/commands/<name>.md` + `.cursor/skills/<name>` symlink | `validate.py` |
| Docs | a row in `README.md` and a `/name` section in `AGENTS.md` | `validate.py` |
| Behavior | `evals/<name>.md` | `validate.py` (warning until every skill has one) |

## Quality gates

1. **`python3 tools/validate.py`** — structure and wiring. Errors fail CI; warnings are advisory.
2. **Evals** — `evals/<name>.md` lists prompts and what a good and a bad response look like. Run by hand for now: paste the prompt into a fresh session with the skill loaded and grade against the case. Automate only after the cases have caught a real regression.

CI: `.github/workflows/validate.yml` runs the validator on every push and PR.

## What we deliberately didn't adopt (yet)

- **Per-harness adapters** (`tools/adapters/` in wshobson/agents). This pack targets Claude Code and Cursor, which both read the source files directly.
- **`plugins/<group>/` bundles.** Worth it once there are several skill families (interview, notes, design). With a handful of skills, a flat `skills/` folder is simpler.
- **Score snapshots and LLM judges.** Start with hand-graded cases; add automation when it has something to protect.

## Adding a skill

1. Write `skills/<name>/SKILL.md`.
2. Add the three command files and the Cursor symlink (see *Wiring*).
3. Add the README row and the `AGENTS.md` section.
4. Add `evals/<name>.md` with at least three cases.
5. Run `python3 tools/validate.py` until it reports no errors.
