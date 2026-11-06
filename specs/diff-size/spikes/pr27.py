#!/usr/bin/env python3
"""Spike for slice 01: count new / moved / deleted lines in brain-cli PR #27.

Usage: pr27.py <brain-cli repo>   (writes the markdown table to stdout)

Throwaway evidence, not product code. Runs git diff with --color-moved=zebra and
pinned colours for every commit from the merge-base with main to the branch head, each against its parent, plus the whole range, under two whitespace settings,
excluding dist/ and specs/ by pathspec. An added line coloured as moved counts as
moved; any other added line counts as new. Read-only.
"""
import re
import subprocess
import sys

BASE, HEAD = "7045e68", "f6f554a"  # merge-base with main, branch head
NEW_MOVED = ("\x1b[1;35m", "\x1b[1;36m")  # bold magenta / bold cyan, pinned below
PINNED = [
    "-c", "color.diff.new=green", "-c", "color.diff.old=red",
    "-c", "color.diff.newMoved=bold magenta", "-c", "color.diff.newMovedAlternative=bold cyan",
    "-c", "color.diff.oldMoved=bold yellow", "-c", "color.diff.oldMovedAlternative=bold blue",
    "-c", "color.diff.newMovedDimmed=bold magenta", "-c", "color.diff.newMovedAlternativeDimmed=bold cyan",
]
SETTINGS = {"default": [], "allow-indentation-change": ["--color-moved-ws=allow-indentation-change"]}
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def count(repo, base, head, ws):
    out = subprocess.run(
        ["git", *PINNED, "diff", "--color=always", "--color-moved=zebra", "-M", *ws,
         base, head, "--", ".", ":!dist", ":!specs"],
        cwd=repo, capture_output=True, text=True, errors="replace", check=True).stdout
    new = moved = deleted = 0
    in_hunk = False
    for line in out.splitlines():
        plain = ANSI.sub("", line)
        # File headers come before the first @@ of each file; only hunk lines count,
        # so a content line that starts with "++" or "--" is never dropped.
        if plain.startswith("diff --git"):
            in_hunk = False
            continue
        if plain.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if plain.startswith("+"):
            if any(code in line for code in NEW_MOVED):
                moved += 1
            else:
                new += 1
        elif plain.startswith("-"):
            deleted += 1
    return new, moved, deleted


def subject(repo, c):
    return subprocess.run(["git", "log", "-1", "--format=%s", c], cwd=repo,
                          capture_output=True, text=True, check=True).stdout.strip()


def main(repo):
    print("| Commit | Subject | Default: new / moved / del | Indent-insensitive: new / moved / del | Moved share (indent-insensitive) |")
    print("|---|---|---|---|---|")
    commits = subprocess.run(["git", "rev-list", "--reverse", "--abbrev-commit", f"{BASE}..{HEAD}"],
                             cwd=repo, capture_output=True, text=True, check=True).stdout.split()
    rows = [(c, f"{c}~1", c, subject(repo, c)) for c in commits]
    rows.append(("whole PR", BASE, HEAD, f"{BASE}..{HEAD} diffed at once"))
    for label, base, head, subj in rows:
        a = count(repo, base, head, SETTINGS["default"])
        b = count(repo, base, head, SETTINGS["allow-indentation-change"])
        share = b[1] / (b[0] + b[1]) if b[0] + b[1] else 0
        subj = subj.replace("|", "\\|")
        print(f"| `{label}` | {subj} | {a[0]} / {a[1]} / {a[2]} | {b[0]} / {b[1]} / {b[2]} | {share:.0%} |")


if __name__ == "__main__":
    main(sys.argv[1])
