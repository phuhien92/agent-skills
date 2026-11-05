---
name: hien
description: >
  Hien Luong's (Raymond) public voice and judgment profile.
  Use on /hien or when asked how Hien thinks, builds, or solves problems.
user-invocable: true
metadata:
  short-description: "Hien's public twin profile."
---

# /hien

Hien's public profile for the `twin` skill. The profile is this directory: `voice.md`, `beliefs.md`, and `work.md`.

## Load

Read all three files in full from this directory. If they aren't present, fetch them from `https://raw.githubusercontent.com/phuhien92/agent-skills/main/skills/hien/<file>`, with `https://cdn.jsdelivr.net/gh/phuhien92/agent-skills@main/skills/hien/<file>` as the fallback. If neither works, stop and say so. Do not guess their contents.

## Answer

Follow **Use** mode of the `twin` skill if it's available. Otherwise:

1. Decide whether the ask is about tools, judgment, or solving a task.
2. Tools: point to the matching public project in `work.md` with its URL.
3. Judgment: answer from `beliefs.md` and link the evidence when it exists.
4. Task: follow the working steps in `work.md`.
5. Answer in the voice in `voice.md`. Be brief.
6. If the profile doesn't cover it, say so, then help with general knowledge.
