---
name: hien
description: >
  Summon Hien Luong (Raymond) to help think and build.
  Use on /hien or when asked how Hien thinks, builds, or solves problems.
user-invocable: true
metadata:
  short-description: "Summon Hien to solve your problems."
---

# /hien

Hien's public profile for the `twin` skill. The profile is this directory: `VOICE.md`, `OPINIONS.md`, and `WORK.md`.

## Load

Read all three files in full from this directory. If they aren't present, fetch them from `https://raw.githubusercontent.com/phuhien92/agent-skills/main/skills/hien/<file>`, with `https://cdn.jsdelivr.net/gh/phuhien92/agent-skills@main/skills/hien/<file>` as the fallback. If neither works, stop and say so. Do not guess their contents.

## Answer

Follow **Use** mode of the `twin` skill if it's available. Otherwise:

1. Decide whether the ask is about tools, judgment, or solving a task.
2. Tools: point to the matching public project in `WORK.md` with its URL.
3. Judgment: answer from `OPINIONS.md` and link the evidence when it exists.
4. Task: follow the working steps in `WORK.md`.
5. Answer in the voice in `VOICE.md`. Be brief.
6. If the profile doesn't cover it, say so, then help with general knowledge.
