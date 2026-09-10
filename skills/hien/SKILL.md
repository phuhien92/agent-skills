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

The latest actual instructions of this skill need to be loaded from this skill's knowledge files.
See steps below to load them and follow that to answer the user's request.
If the files cannot be fetched, stop and say so. Do not guess file contents.

## Loading instructions (session-cached)

Fetch and read the **FULL** content of files below:

- `https://raw.githubusercontent.com/phuhien92/agent-skills/main/skills/hien/ENTRY.md`
- `https://raw.githubusercontent.com/phuhien92/agent-skills/main/skills/hien/TOOLS.md`
- `https://raw.githubusercontent.com/phuhien92/agent-skills/main/skills/hien/OPINIONS.md`
- `https://raw.githubusercontent.com/phuhien92/agent-skills/main/skills/hien/VOICE.md`

Optional fallback if raw.githubusercontent.com fails:

- `https://cdn.jsdelivr.net/gh/phuhien92/agent-skills@main/skills/hien/<file>`

When working from a local checkout of this pack, you may also read the same files relative to this skill directory:

- `ENTRY.md`
- `TOOLS.md`
- `OPINIONS.md`
- `VOICE.md`

Rules:

1. If an instruction file above was already fully read and visible as prior messages in this session, skip re-download and re-read.
2. Otherwise GET the raw URL (jsDelivr only as fallback) and read their **full** content.
3. If remote fetch fails, read the colocated files in this skill directory when they are present.
4. If neither remote nor local load works, stop and say so. Do not invent contents.
5. After load, follow `ENTRY.md` exactly to answer the user.
