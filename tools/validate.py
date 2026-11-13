#!/usr/bin/env python3
"""Structural checks for this skill pack. Stdlib only.

Every finding prints a concrete fix. Exit code 1 if any ERROR.
Run from anywhere: python3 tools/validate.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_SKILL_BYTES = 8 * 1024
MAX_CONTEXT_LINES = 150
# A command's description is often all the model sees of a skill, so it must say when to use it.
TRIGGER = re.compile(r"\buse (when|before|after|proactively|for|on)\b|\bwhen the user\b|\bbefore\b|\bafter\b",
                     re.I)

errors: list[str] = []
warnings: list[str] = []


def err(msg: str, fix: str) -> None:
    errors.append(f"ERROR  {msg}\n       fix: {fix}")


def warn(msg: str, fix: str) -> None:
    warnings.append(f"WARN   {msg}\n       fix: {fix}")


def frontmatter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields: dict[str, str] = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km:
            fields[km.group(1)] = km.group(2).strip()
    return fields


def check_skill(name: str) -> None:
    skill = ROOT / "skills" / name / "SKILL.md"
    if not skill.is_file():
        err(f"skills/{name}/ has no SKILL.md", f"create skills/{name}/SKILL.md")
        return

    text = skill.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        err(f"skills/{name}/SKILL.md has no frontmatter",
            "start the file with ---\\nname: ...\\ndescription: ...\\n---")
    else:
        if fm.get("name") != name:
            err(f"skills/{name}/SKILL.md name is {fm.get('name')!r}",
                f"set `name: {name}` to match the folder")
        if "description" not in fm:
            err(f"skills/{name}/SKILL.md has no description",
                "add `description:` saying what it does and when to use it")

    size = len(text.encode("utf-8"))
    if size > MAX_SKILL_BYTES:
        warn(f"skills/{name}/SKILL.md is {size} bytes (> {MAX_SKILL_BYTES})",
             f"move long material into a sibling file in skills/{name}/ and load it on demand")

    for rel in (f".claude/commands/{name}.md", f"commands/{name}.md", f".cursor/commands/{name}.md"):
        if not (ROOT / rel).is_file():
            err(f"missing {rel}", f"add {rel} containing: Follow the `{name}` skill.")
        else:
            check_command(name, rel)

    link = ROOT / ".cursor" / "skills" / name
    if not link.is_symlink():
        err(f"missing symlink .cursor/skills/{name}",
            f"ln -s ../../skills/{name} .cursor/skills/{name}")
    elif os.readlink(link) != f"../../skills/{name}":
        err(f".cursor/skills/{name} points at {os.readlink(link)}",
            f"re-create it: ln -sfn ../../skills/{name} .cursor/skills/{name}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"(skills/{name}/SKILL.md)" not in readme:
        err(f"README.md has no Skills row for {name}",
            f"add a row linking [{name}](skills/{name}/SKILL.md)")

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    if f"`/{name}`" not in agents:
        err(f"AGENTS.md has no section for /{name}",
            f"add '## When the user runs `/{name}`' with one routing paragraph")

    if not (ROOT / "evals" / f"{name}.md").is_file():
        warn(f"no evals/{name}.md", f"add evals/{name}.md with at least three cases")


def check_command(name: str, rel: str) -> None:
    text = (ROOT / rel).read_text(encoding="utf-8")
    if f"`{name}`" not in text:
        warn(f"{rel} doesn't name the `{name}` skill",
             f"include the line: Follow the `{name}` skill.")
    desc = (frontmatter(text) or {}).get("description", "")
    if not TRIGGER.search(desc):
        warn(f"{rel} description has no trigger (no \"Use when\", \"before\", \"after\" or \"when the user\")",
             f"copy the \"Use when…\" clause from skills/{name}/SKILL.md into one line; "
             "the model may see only this description")


def check_context_files() -> None:
    agents = ROOT / "AGENTS.md"
    lines = len(agents.read_text(encoding="utf-8").splitlines())
    if lines > MAX_CONTEXT_LINES:
        warn(f"AGENTS.md is {lines} lines (> {MAX_CONTEXT_LINES})",
             "move detail into ARCHITECTURE.md or docs/; keep AGENTS.md to routing")

    claude = ROOT / "CLAUDE.md"
    if not claude.is_symlink() or os.readlink(claude) != "AGENTS.md":
        err("CLAUDE.md is not a symlink to AGENTS.md", "ln -sfn AGENTS.md CLAUDE.md")


def check_agents(skills: set[str]) -> None:
    """A subagent wraps one skill: .claude/agents/<name>.md, listed in the plugin manifest."""
    folder = ROOT / ".claude" / "agents"
    manifest = (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    for f in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        name, rel = f.stem, f".claude/agents/{f.name}"
        if f.is_symlink():
            err(f"{rel} is a symlink", f"make {rel} a real file; the plugin manifest points at it")
        text = f.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if fm is None or fm.get("name") != name:
            err(f"{rel} name is {None if fm is None else fm.get('name')!r}",
                f"start it with frontmatter and set `name: {name}` to match the file")
        elif "description" not in fm:
            err(f"{rel} has no description", "add `description:` saying when to hand work to this subagent")
        if name not in skills:
            err(f"{rel} has no matching skills/{name}/",
                f"name the subagent after the skill it runs, or delete {rel}")
        elif f"`{name}`" not in text:
            err(f"{rel} doesn't load the `{name}` skill",
                f"tell it to load the `{name}` skill; never copy the skill's text into it")
        if f'"./{rel}"' not in manifest:
            err(f"{rel} is not in .claude-plugin/plugin.json", f'add "./{rel}" to its "agents" list')


def check_orphans(skills: set[str]) -> None:
    for folder in (".claude/commands", "commands", ".cursor/commands"):
        for f in sorted((ROOT / folder).glob("*.md")):
            if f.stem not in skills:
                err(f"{folder}/{f.name} has no matching skills/{f.stem}/",
                    f"delete {folder}/{f.name} or add skills/{f.stem}/SKILL.md")
    cursor_skills = ROOT / ".cursor" / "skills"
    if cursor_skills.is_dir():
        for f in sorted(cursor_skills.iterdir()):
            if f.name not in skills:
                err(f".cursor/skills/{f.name} has no matching skill",
                    f"rm .cursor/skills/{f.name}")


def main() -> int:
    skills = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir()}
    for name in sorted(skills):
        check_skill(name)
    check_context_files()
    check_agents(skills)
    check_orphans(skills)

    for line in errors + warnings:
        print(line)
    print(f"\n{len(skills)} skills · {len(errors)} errors · {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
