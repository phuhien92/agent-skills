#!/usr/bin/env python3
"""decision-checker gate before a PR exists: a Claude Code PreToolUse hook.

Denies opening a pull request (`gh pr create` in Bash, or a GitHub MCP
`create_pull_request` tool) while the PR's branch changes non-doc files but has
no decisions.md. The Stop hook (require-ledger.sh) fires after the turn, when
the PR is already open; this one fires before it. Same ledger rule as the Stop
hook: a decisions.md added or changed on the branch, or one on disk that git
ignores. Docs-only branches pass.

It finds the repo from the command's `cd <path>`, `--repo`, or the MCP call's
owner/repo, looking at the session's cwd and its immediate child folders, so
it works from a home folder holding several repos. When it can't find the
repo, the branch, or a base, it lets the call through and says so in
additionalContext: it never blocks on a guess.

Output format (verified against https://code.claude.com/docs/en/hooks,
"PreToolUse decision control"): exit 0 and print
{"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny", "permissionDecisionReason": "..."}}.
The reason is shown to Claude.

Settings (env, all optional):
  DECISION_CHECKER_BASE  base ref to diff against (default: origin/<the PR's
                         base>, then origin/HEAD, origin/main, origin/master)
Stdlib only.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

LEDGER = re.compile(r"(^|/)decisions\.md$")
PR_CREATE = re.compile(r"\bgh\s+pr\s+create\b")


def git(repo: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(["git", "-C", str(repo), "-c", "core.quotePath=false", *args],
                             capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def is_repo(path: Path) -> bool:
    return path.is_dir() and git(path, "rev-parse", "--is-inside-work-tree") == "true"


def unquote(value: str) -> str:
    return value.strip().strip("'\"")


def flag(text: str, *names: str) -> str | None:
    """Value of the first of `names` (e.g. -H, --head) in a gh command line."""
    alts = "|".join(re.escape(n) for n in names)
    m = re.search(rf"(?:^|\s)(?:{alts})(?:=|\s+)(\"[^\"]*\"|'[^']*'|[^\s;&|)]+)", text)
    return unquote(m.group(1)) if m else None


def matches_remote(repo: Path, slug: str) -> bool:
    remotes = git(repo, "remote") or ""
    for name in remotes.split():
        url = (git(repo, "remote", "get-url", name) or "").lower()
        if re.search(rf"[/:]{re.escape(slug.lower())}(\.git)?/?$", url):
            return True
    return False


def find_repo(start: Path, cwd: Path, slug: str | None) -> Path | None:
    """The local clone the PR is for: start itself, else a child of start or cwd."""
    if is_repo(start) and (slug is None or matches_remote(start, slug)):
        return start
    if slug is None:
        return None
    for base in dict.fromkeys([start, cwd]):
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if (child / ".git").exists() and matches_remote(child, slug):
                return child
    return None


def from_bash(command: str, cwd: Path) -> dict | None:
    m = PR_CREATE.search(command)
    if not m:
        return None
    before, after = command[:m.start()], command[m.end():]
    start = cwd
    cds = re.findall(r"(?:^|[;&|(]|\s)cd\s+(\"[^\"]+\"|'[^']+'|[^\s;&|)]+)", before)
    if cds:
        start = (cwd / os.path.expanduser(unquote(cds[-1]))).resolve()
    return {"start": start, "slug": flag(after, "-R", "--repo"),
            "head": flag(after, "-H", "--head"), "base": flag(after, "-B", "--base")}


def from_mcp(tool_input: dict, cwd: Path) -> dict:
    owner, name = tool_input.get("owner"), tool_input.get("repo")
    return {"start": cwd, "slug": f"{owner}/{name}" if owner and name else None,
            "head": tool_input.get("head"), "base": tool_input.get("base")}


def ledger_state(repo: Path, head: str | None, base_name: str | None) -> tuple[str, str]:
    """('missing' | 'ok' | 'unknown', detail)."""
    current = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    if head and ":" in head:  # owner:branch from a fork
        head = head.split(":", 1)[1]
    branch = head or current
    if not branch or branch == "HEAD":
        return "unknown", "couldn't tell which branch the PR is for"
    on_branch = branch == current
    if on_branch:
        ref = "HEAD"
    else:
        ref = next((r for r in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}")
                    if git(repo, "rev-parse", "--verify", "--quiet", r)), None)
        if ref is None:
            return "unknown", f"no local or origin ref for branch {branch}"

    candidates = [os.environ.get("DECISION_CHECKER_BASE") or ""]
    if base_name:
        candidates.append(f"origin/{base_name}")
    candidates += ["origin/HEAD", "origin/main", "origin/master"]
    base = next((c for c in candidates if c and git(repo, "rev-parse", "--verify", "--quiet", c)), None)
    if base is None:
        return "unknown", "no base branch to diff against (set DECISION_CHECKER_BASE)"
    mb = git(repo, "merge-base", ref, base)
    if not mb:
        return "unknown", f"{branch} shares no history with {base}"

    changed = set((git(repo, "diff", "--name-only", "--diff-filter=d", mb, ref) or "").splitlines())
    if on_branch:
        changed |= set((git(repo, "diff", "--name-only", "--diff-filter=d", "HEAD") or "").splitlines())
        changed |= set((git(repo, "ls-files", "--others", "--exclude-standard") or "").splitlines())
    changed.discard("")
    detail = f"branch {branch} in {repo} (base {base})"
    if not changed or not any(not f.endswith(".md") for f in changed):
        return "ok", detail
    if any(LEDGER.search(f) for f in changed):
        return "ok", detail
    ignored = git(repo, "ls-files", "--others", "--ignored", "--exclude-standard") or ""
    if any(LEDGER.search(f) for f in ignored.splitlines()):
        return "ok", detail
    return "missing", detail


def emit(**fields: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", **fields}}))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    tool = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    cwd = Path(data.get("cwd") or os.getcwd())

    if tool == "Bash":
        target = from_bash(str(tool_input.get("command") or ""), cwd)
    elif tool.endswith("create_pull_request"):
        target = from_mcp(tool_input, cwd)
    else:
        return 0
    if target is None:
        return 0

    repo = find_repo(target["start"], cwd, target["slug"])
    if repo is None:
        where = target["slug"] or str(target["start"])
        emit(additionalContext=f"require-ledger-before-pr: no local clone of {where} found from {cwd}, "
                               "so no decisions-ledger check ran for this PR.")
        return 0
    repo = Path(git(repo, "rev-parse", "--show-toplevel") or repo)

    state, detail = ledger_state(repo, target["head"], target["base"])
    if state == "unknown":
        emit(additionalContext=f"require-ledger-before-pr: {detail}, so no decisions-ledger check ran.")
    elif state == "missing":
        emit(permissionDecision="deny", permissionDecisionReason=(
            f"No decisions ledger on {detail}, and the branch changes code. A PR opens only after the "
            "decisions are checked. Hand the branch to the decision-checker subagent (Agent tool: "
            "decision-checker, or agent-skills:decision-checker from the plugin) with the scope (everything "
            "since the branch left its base), the baseline (the spec path, the issue, or the user's request "
            "quoted) and every place you had to guess. It saves decisions.md. Then open the PR with its "
            "Check these first list in the description. If no such subagent is installed, run the "
            "decision-checker skill yourself in Check mode and save decisions.md."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
