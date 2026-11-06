#!/usr/bin/env python3
"""Count new, moved and deleted lines per commit, so a slice or a PR can be sized.

Part of the slice-spec skill (specs/diff-size/). An added line that git's move
detection colours as moved counts as moved; every other added line counts as new.
Moves are found with --color-moved=zebra and --color-moved-ws=allow-indentation-change,
so a block that moved and changed indentation still counts as moved. Colours, prefixes
and other diff settings are pinned, so a user's git config cannot change the counts.

Known undercount of moves: git marks a block as moved only when it holds at least 20
alphanumeric characters, so short moved lines (a lone "}" or a one-word import) count
as new. Moves are found inside one diff, so a block moved across two commits counts
as deleted in one and new in the other.

Standard library only. Needs git 2.17 or later.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
MIN_GIT = (2, 17)

# Pinned colours: what the parser looks for. Every moved slot gets its own code, so
# a moved line is found by the first colour code on its line, never by guessing.
NEW_MOVED_CODES = {"1;35", "1;36"}   # bold magenta, bold cyan
OLD_MOVED_CODES = {"1;33", "1;34"}   # bold yellow, bold blue
PINNED_CONFIG = {
    "color.diff.new": "green",
    "color.diff.old": "red",
    "color.diff.newMoved": "bold magenta",
    "color.diff.newMovedAlternative": "bold cyan",
    "color.diff.newMovedDimmed": "bold magenta",
    "color.diff.newMovedAlternativeDimmed": "bold cyan",
    "color.diff.oldMoved": "bold yellow",
    "color.diff.oldMovedAlternative": "bold blue",
    "color.diff.oldMovedDimmed": "bold yellow",
    "color.diff.oldMovedAlternativeDimmed": "bold blue",
    "color.diff.context": "normal",
    "color.diff.meta": "normal",
    "color.diff.frag": "normal",
    "color.diff.func": "normal",
    "color.diff.whitespace": "normal",
    "core.quotePath": "false",
    "diff.noprefix": "false",
    "diff.mnemonicPrefix": "false",
    "diff.relative": "false",
    "diff.suppressBlankEmpty": "false",
    "diff.ignoreSubmodules": "none",
    "diff.submodule": "short",
    "core.attributesFile": "/dev/null",
}
DIFF_FLAGS = [
    "--color=always", "--color-moved=zebra", "--color-moved-ws=allow-indentation-change",
    "-M", "--no-ext-diff", "--no-textconv", "--src-prefix=a/", "--dst-prefix=b/",
    "--unified=0", "--diff-algorithm=myers", "--submodule=short", "--text",
]
# --text: a file a user's attributes mark -diff is still counted. Binary files are kept
# out by the product-code filter before the diff runs, so --text never sees them there.
SGR = re.compile(r"\x1b\[([0-9;]*)m")


class DiffSizeError(Exception):
    """Bad input: not a repo, an unknown commit or range, or git too old. Exit 2."""


@dataclass
class FileCount:
    """Counts for one file in one commit.

    new: added lines that are not moves. moved: added lines that are moves (moved in).
    deleted: removed lines that are not moves. moved_out: removed lines that are moves.
    old_path is the path in the parent (None for an added file); new_path is the path
    in the commit (None for a deleted file). A pure rename counts every line as moved.
    """
    old_path: str | None
    new_path: str | None
    new: int = 0
    moved: int = 0
    deleted: int = 0
    moved_out: int = 0

    @property
    def path(self) -> str:
        return self.new_path or self.old_path or ""


def git(repo: Path, *args: str, check: bool = True) -> str:
    try:
        done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    except FileNotFoundError:
        raise DiffSizeError("git is not installed") from None
    if check and done.returncode != 0:
        raise DiffSizeError(done.stderr.decode("utf-8", "replace").strip() or f"git {args[0]} failed")
    return done.stdout.decode("utf-8", "replace")


def check_git() -> None:
    out = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout
    found = re.search(r"(\d+)\.(\d+)", out)
    if not found or tuple(int(n) for n in found.groups()) < MIN_GIT:
        raise DiffSizeError(f"needs git {MIN_GIT[0]}.{MIN_GIT[1]} or later, found: {out.strip() or 'none'}")


def check_repo(repo: Path) -> None:
    if not repo.is_dir():
        raise DiffSizeError(f"not a directory: {repo}")
    if git(repo, "rev-parse", "--is-inside-work-tree", check=False).strip() != "true":
        raise DiffSizeError(f"not a git repository: {repo}")


def resolve(repo: Path, rev: str) -> str:
    out = git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", check=False).strip()
    if not out:
        raise DiffSizeError(f"unknown commit: {rev}")
    return out


def parent(repo: Path, commit: str) -> str:
    """The first parent (a merge is sized against its first parent), or the empty tree."""
    out = git(repo, "rev-parse", "--verify", "--quiet", f"{commit}^1", check=False).strip()
    return out or EMPTY_TREE


def unquote(path: str) -> str:
    """Undo git's C-style quoting of a path ("a\\tb", octal escapes for raw bytes)."""
    if not (len(path) >= 2 and path.startswith('"') and path.endswith('"')):
        return path
    body, out, i = path[1:-1], bytearray(), 0
    simple = {"a": 7, "b": 8, "t": 9, "n": 10, "v": 11, "f": 12, "r": 13, '"': 34, "\\": 92}
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            nxt = body[i + 1]
            if nxt in simple:
                out.append(simple[nxt])
                i += 2
                continue
            if body[i + 1:i + 4].isdigit():
                out.append(int(body[i + 1:i + 4], 8))
                i += 4
                continue
        out.extend(ch.encode("utf-8"))
        i += 1
    return out.decode("utf-8", "replace")


def strip_prefix(path: str, prefix: str) -> str | None:
    # git ends a header path that contains a space with a tab; it is not part of the name.
    path = path[:-1] if path.endswith("\t") else path
    if path == "/dev/null":
        return None
    path = unquote(path)
    return path[len(prefix):] if path.startswith(prefix) else path


def first_code(raw: str) -> str | None:
    found = SGR.match(raw)
    return found.group(1) if found else None


def header_paths(rest: str) -> tuple[str | None, str | None]:
    """Paths from a `diff --git a/X b/Y` header, so a file with no ---/+++ lines (binary,
    mode-only, empty) still has a name. Renames are named by their `rename` lines."""
    if rest.startswith('"'):
        end = 1
        while end < len(rest) and (rest[end] != '"' or rest[end - 1] == "\\"):
            end += 1
        old, new = rest[:end + 1], rest[end + 2:]
        return strip_prefix(old, "a/"), strip_prefix(new, "b/")
    if (len(rest) - 5) % 2 == 0:
        size = (len(rest) - 5) // 2
        old, sep, new = rest[2:2 + size], rest[2 + size:5 + size], rest[5 + size:]
        if rest.startswith("a/") and sep == " b/" and old == new:
            return old, new
    if ' "b/' in rest:
        old, _, new = rest.partition(' "b/')
        return strip_prefix(old, "a/"), strip_prefix('"b/' + new, "b/")
    return None, None


def parse(text: str) -> list[FileCount]:
    """Turn coloured `git diff` output (made with DIFF_FLAGS and PINNED_CONFIG) into counts.

    Only lines inside a hunk are counted, so a content line that starts with "++" or
    "--" is never mistaken for a file header. Pure renames have no hunk; the caller
    fills their moved count from the file's length (see `count_commit`).
    """
    files: list[FileCount] = []
    cur: FileCount | None = None
    in_hunk = False
    for raw in text.split("\n"):
        plain = SGR.sub("", raw)
        if plain.startswith("diff --git "):
            cur = FileCount(*header_paths(plain[len("diff --git "):]))
            files.append(cur)
            in_hunk = False
            continue
        if cur is None:
            continue
        if not in_hunk:
            if plain.startswith("@@"):
                in_hunk = True
            elif plain.startswith("--- "):
                cur.old_path = strip_prefix(plain[4:], "a/")
            elif plain.startswith("+++ "):
                cur.new_path = strip_prefix(plain[4:], "b/")
            elif plain.startswith("rename from "):
                cur.old_path = unquote(plain[len("rename from "):])
            elif plain.startswith("rename to "):
                cur.new_path = unquote(plain[len("rename to "):])
            elif plain.startswith("new file mode"):
                cur.old_path = None
            elif plain.startswith("deleted file mode"):
                cur.new_path = None
            continue
        if plain.startswith("@@"):
            continue
        code = first_code(raw)
        if plain.startswith("+"):
            if code in NEW_MOVED_CODES:
                cur.moved += 1
            else:
                cur.new += 1
        elif plain.startswith("-"):
            if code in OLD_MOVED_CODES:
                cur.moved_out += 1
            else:
                cur.deleted += 1
    return files


def diff_text(repo: Path, base: str, head: str, pathspecs: list[str] | None = None) -> str:
    """Coloured diff of base..head. Moves are matched only among the files diffed, so
    pass pathspecs to keep non-product files (build output, say) from supplying moves."""
    config: list[str] = []
    for key, value in PINNED_CONFIG.items():
        config += ["-c", f"{key}={value}"]
    tail = ["--", *pathspecs] if pathspecs else []
    return git(repo, *config, "diff", *DIFF_FLAGS, base, head, *tail)


def line_count(repo: Path, commit: str, path: str) -> int:
    blob = subprocess.run(["git", "-C", str(repo), "cat-file", "-p", f"{commit}:{path}"],
                          capture_output=True).stdout
    if not blob:
        return 0
    return blob.count(b"\n") + (0 if blob.endswith(b"\n") else 1)


def count_range(repo: Path, base: str, head: str,
                pathspecs: list[str] | None = None) -> list[FileCount]:
    """Per-file counts for `base..head` diffed at once, limited to pathspecs if given."""
    files = parse(diff_text(repo, base, head, pathspecs))
    for f in files:
        if f.old_path and f.new_path and f.old_path != f.new_path:
            # A rename: the lines it kept moved with it. Edited lines are already in the
            # hunks; what the hunks don't show was carried over unchanged.
            f.moved += line_count(repo, head, f.new_path) - f.new - f.moved
            f.moved_out += line_count(repo, base, f.old_path) - f.deleted - f.moved_out
    return files


def count_commit(repo: Path, commit: str, pathspecs: list[str] | None = None) -> list[FileCount]:
    """Per-file counts for one commit against its first parent."""
    sha = resolve(repo, commit)
    return count_range(repo, parent(repo, sha), sha, pathspecs)


def commits_in(repo: Path, rev_range: str) -> list[str]:
    """Commits of a range (`A..B`) oldest first, or the one commit named.

    Follows first parents only: a merge's row already covers the side branch it brings
    in (it is diffed against its first parent), so listing the side commits too would
    count their lines twice."""
    if ".." in rev_range:
        base, _, head = rev_range.partition("..")
        if head.startswith("."):
            raise DiffSizeError(f"use A..B, not A...B: {rev_range}")
        resolve(repo, base or "HEAD")
        resolve(repo, head or "HEAD")
        out = git(repo, "rev-list", "--reverse", "--first-parent", rev_range)
        return out.split()
    return [resolve(repo, rev_range)]
