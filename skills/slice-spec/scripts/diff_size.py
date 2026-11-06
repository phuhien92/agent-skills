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

Usage: diff_size.py <repo> <range> [--json]

<range> is A..B (the commits after A up to B, first parents only) or one commit.
Prints one row per commit, oldest first, then the whole range diffed at once, with a
tier for each: target 400, soft 800, hard 1500 new lines. Over soft, a commit gets
"consider Reslice" and the range gets "split the goal"; over hard, a commit gets
"reslice before review". These are warnings: the exit code is 0 whatever the size,
and 2 only on bad input (not a repo, unknown commit, git too old).

Standard library only. Needs git 2.17 or later.
"""
from __future__ import annotations

import json
import os
import re
import sys
import subprocess
import tempfile
from pathlib import PurePosixPath
from dataclasses import dataclass, field
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


def git(repo: Path, *args: str, check: bool = True, env: dict[str, str] | None = None) -> str:
    try:
        done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)
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


def diff_text(repo: Path, base: str, head: str, pathspecs: list[str] | None = None,
              env: dict[str, str] | None = None) -> str:
    """Coloured diff of base..head. Moves are matched only among the files diffed, so
    pass pathspecs to keep non-product files (build output, say) from supplying moves."""
    config: list[str] = []
    for key, value in PINNED_CONFIG.items():
        config += ["-c", f"{key}={value}"]
    tail = ["--", *pathspecs] if pathspecs else []
    return git(repo, *config, "diff", *DIFF_FLAGS, base, head, *tail, env=env)


def line_count(repo: Path, commit: str, path: str, env: dict[str, str] | None = None) -> int:
    blob = subprocess.run(["git", "-C", str(repo), "cat-file", "-p", f"{commit}:{path}"],
                          capture_output=True, env=env).stdout
    if not blob:
        return 0
    return blob.count(b"\n") + (0 if blob.endswith(b"\n") else 1)


def count_range(repo: Path, base: str, head: str, pathspecs: list[str] | None = None,
                env: dict[str, str] | None = None) -> list[FileCount]:
    """Per-file counts for `base..head` diffed at once, limited to pathspecs if given.
    `base` and `head` may be any tree-ish; `env` lets git find temporary objects."""
    files = parse(diff_text(repo, base, head, pathspecs, env))
    for f in files:
        if f.old_path and f.new_path and f.old_path != f.new_path:
            # A rename: the lines it kept moved with it. Edited lines are already in the
            # hunks; what the hunks don't show was carried over unchanged.
            f.moved += line_count(repo, head, f.new_path, env) - f.new - f.moved
            f.moved_out += line_count(repo, base, f.old_path, env) - f.deleted - f.moved_out
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


# --- Product-code filter (slice 03) -------------------------------------------------
# The rule data below is copied from skills/codebase-rubric/scripts/size_report.py so
# each skill installs on its own. tools/test_skip_rules_drift.py fails if they drift.
# The predicates differ on purpose: size_report reads files on disk; here each side of
# a diff is judged against its own commit's tree.

LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock",
    "Cargo.lock", "poetry.lock", "Pipfile.lock", "uv.lock", "composer.lock",
    "Gemfile.lock", "go.sum", "mix.lock", "pubspec.lock", "Podfile.lock",
    "flake.lock", "packages.lock.json",
}
ANY_DEPTH_DIRS = {"node_modules", "vendor", ".git"}
ROOT_BUILD_DIRS = {"dist", "build"}
PACKAGE_MARKERS = ("package.json", "pyproject.toml", "setup.py", "Cargo.toml",
                   "go.mod", "pom.xml", "build.gradle", "build.gradle.kts",
                   "composer.json", "Gemfile", "mix.exs", "pubspec.yaml")
CODE_EXTENSIONS = {
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts",
    ".go", ".rs", ".java", ".kt", ".kts", ".scala", ".swift", ".m", ".mm",
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh", ".cs", ".fs", ".rb",
    ".php", ".ex", ".exs", ".erl", ".clj", ".cljs", ".dart", ".lua", ".pl",
    ".pm", ".r", ".jl", ".hs", ".ml", ".mli", ".elm", ".vue", ".svelte",
    ".astro", ".sh", ".bash", ".zsh", ".fish", ".ps1", ".sql", ".graphql",
    ".proto", ".zig", ".nim", ".v", ".sv", ".vhd", ".tf", ".hcl",
    ".css", ".scss", ".sass", ".less", ".html", ".htm", ".mdx",
}
CODE_NAMES = {"Makefile", "Dockerfile", "Rakefile", "Justfile"}
# Stable keys for --json; phrases for the text table.
SKIP_LABELS = {
    "not-a-file": "symlink or not a file",
    "not-code": "not a code file",
    "lockfile": "lockfile",
    "vendored-or-build": "vendored or build folder",
    "marked-generated": "marked generated or vendored",
    "binary": "binary",
    "generated-header": "generated header",
}
GENERATED_MARKERS = (
    "@generated", "do not edit", "code generated by", "autogenerated",
    "auto-generated", "this file is generated", "automatically generated",
)
HEADER_LINES = 5
SNIFF_BYTES = 8192


def is_code(rel: str) -> bool:
    p = PurePosixPath(rel)
    return p.suffix.lower() in CODE_EXTENSIONS or p.name in CODE_NAMES


def in_build_dir(tree_files: set[str], rel: str) -> bool:
    """dist/ or build/ directly under the repo root or a package root, in this tree."""
    parts = PurePosixPath(rel).parts[:-1]
    for i, part in enumerate(parts):
        if part in ANY_DEPTH_DIRS:
            return True
        if part in ROOT_BUILD_DIRS:
            parent = "/".join(parts[:i])
            if i == 0 or any(f"{parent}/{m}" in tree_files for m in PACKAGE_MARKERS):
                return True
    return False


def skip_reason(rel: str, head: bytes, marked: set[str], tree_files: set[str]) -> str | None:
    """Same rules, same order as size_report.skip_reason."""
    if PurePosixPath(rel).name in LOCKFILES:
        return "lockfile"
    if in_build_dir(tree_files, rel):
        return "vendored-or-build"
    if not is_code(rel):
        return "not-code"
    if rel in marked:
        return "marked-generated"
    if b"\0" in head:
        return "binary"
    top = b"\n".join(head.splitlines()[:HEADER_LINES]).decode("utf-8", "replace").lower()
    if any(m in top for m in GENERATED_MARKERS):
        return "generated-header"
    return None


@dataclass
class Side:
    """One side of a diff: a commit's tree, read once."""
    treeish: str
    entries: dict[str, tuple[str, str]] = field(default_factory=dict)  # path -> (mode, sha)

    @property
    def files(self) -> set[str]:
        return set(self.entries)


def read_side(repo: Path, treeish: str) -> Side:
    out = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "-z", "--full-tree", treeish],
                         capture_output=True, check=True).stdout.decode("utf-8", "surrogateescape")
    side = Side(treeish)
    for record in filter(None, out.split("\0")):
        meta, _, path = record.partition("\t")
        mode, _kind, sha = meta.split(" ")
        side.entries[path] = (mode, sha)
    return side


def blob_heads(repo: Path, shas: list[str]) -> dict[str, bytes]:
    """The first SNIFF_BYTES of each blob, read in one `git cat-file --batch`."""
    if not shas:
        return {}
    out = subprocess.run(["git", "-C", str(repo), "cat-file", "--batch"],
                         input=("\n".join(shas) + "\n").encode(), capture_output=True, check=True).stdout
    heads, pos = {}, 0
    for sha in shas:
        end = out.index(b"\n", pos)
        header = out[pos:end].split()
        size = int(header[2]) if len(header) == 3 else 0
        heads[sha] = out[end + 1:end + 1 + min(size, SNIFF_BYTES)]
        pos = end + 1 + size + 1
    return heads


def git_at_least(major: int, minor: int) -> bool:
    out = subprocess.run(["git", "--version"], capture_output=True, text=True).stdout
    found = re.search(r"(\d+)\.(\d+)", out)
    return bool(found) and tuple(int(n) for n in found.groups()) >= (major, minor)


def marked_paths(repo: Path, side: Side, paths: list[str]) -> tuple[set[str], bool]:
    """Paths marked linguist-generated or linguist-vendored in that side's tree.

    Uses `git check-attr --source` (git 2.40+). On older git, falls back to the working
    tree's .gitattributes and says so (the second value is True)."""
    if not paths:
        return set(), False
    from_worktree = not git_at_least(2, 40) or side.treeish == EMPTY_TREE
    source = [] if from_worktree else [f"--source={side.treeish}"]
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "core.attributesFile=/dev/null", "check-attr", "-z",
         *source, "--stdin", "linguist-generated", "linguist-vendored"],
        input="\0".join(paths).encode("utf-8", "surrogateescape"), capture_output=True)
    fields = done.stdout.decode("utf-8", "surrogateescape").split("\0")
    marked = set()
    for i in range(0, len(fields) - 2, 3):
        path, _attr, value = fields[i:i + 3]
        if value in ("set", "true"):
            marked.add(path)
    return marked, from_worktree and side.treeish != EMPTY_TREE


def changed_files(repo: Path, base: str, head: str) -> list[tuple[str | None, str | None]]:
    """(old path, new path) per changed file, with the same rename detection as the count."""
    out = subprocess.run(
        ["git", "-C", str(repo), "-c", "diff.renames=true", "-c", "core.quotePath=false",
         "-c", "diff.ignoreSubmodules=none", "diff", "--name-status", "-z", "-M",
         "--no-ext-diff", base, head], capture_output=True, check=True,
    ).stdout.decode("utf-8", "surrogateescape").split("\0")
    pairs, i = [], 0
    while i < len(out) and out[i]:
        status = out[i]
        if status[0] in "RC":
            pairs.append((out[i + 1], out[i + 2]) if status[0] == "R" else (None, out[i + 2]))
            i += 3
        else:
            path = out[i + 1]
            pairs.append((None if status[0] == "A" else path, None if status[0] == "D" else path))
            i += 2
    return pairs


@dataclass
class Filtered:
    paths: list[str]                                       # product paths, either side
    skipped: dict[str, int] = field(default_factory=dict)  # reason -> changed files
    attrs_from_worktree: bool = False
    drop_old: list[str] = field(default_factory=list)      # changed old sides that aren't product
    drop_new: list[str] = field(default_factory=list)      # changed new sides that aren't product


def product_paths(repo: Path, base: str, head: str) -> Filtered:
    """Which changed files are product code. A file's new side is judged against the
    head tree, its old side against the base tree; a file is skipped (and counted once,
    under the reason of its newest side) when no side of it is product code."""
    pairs = changed_files(repo, base, head)
    sides = {"old": read_side(repo, base), "new": read_side(repo, head)}
    wanted = {"old": sorted({o for o, _ in pairs if o}), "new": sorted({n for _, n in pairs if n})}
    reasons: dict[tuple[str, str], str | None] = {}
    worktree_attrs = False
    for key, side in sides.items():
        marked, fallback = marked_paths(repo, side, wanted[key])
        worktree_attrs = worktree_attrs or fallback
        regular = [p for p in wanted[key] if side.entries.get(p, ("",))[0] in ("100644", "100755")]
        heads = blob_heads(repo, sorted({side.entries[p][1] for p in regular}))
        tree = side.files
        for p in wanted[key]:
            if p not in regular:
                reasons[(key, p)] = "not-a-file"
            else:
                reasons[(key, p)] = skip_reason(p, heads[side.entries[p][1]], marked, tree)
    result = Filtered([], attrs_from_worktree=worktree_attrs)
    keep: set[str] = set()
    for old, new in pairs:
        old_ok = old is not None and reasons[("old", old)] is None
        new_ok = new is not None and reasons[("new", new)] is None
        if old_ok:
            keep.add(old)
        elif old is not None:
            result.drop_old.append(old)
        if new_ok:
            keep.add(new)
        elif new is not None:
            result.drop_new.append(new)
        if not (old_ok or new_ok):
            reason = reasons[("new", new)] if new is not None else reasons[("old", old)]
            result.skipped[reason] = result.skipped.get(reason, 0) + 1
    result.paths = sorted(keep)
    return result


def toplevel(repo: Path) -> Path:
    out = git(repo, "rev-parse", "--show-toplevel").strip()
    return Path(out)


def scratch_env(repo: Path, objects: Path) -> dict[str, str]:
    """An environment where new git objects land in `objects`, a temporary folder, while
    the repo's own objects (and its alternates) stay readable. Nothing is written to the
    repo."""
    own = Path(git(repo, "rev-parse", "--git-path", "objects").strip())
    own = own if own.is_absolute() else (repo / own)
    alternates = [str(own.resolve())]
    info = own / "info" / "alternates"
    if info.is_file():
        alternates += [line.strip() for line in info.read_text().splitlines()
                       if line.strip() and not line.startswith("#")]
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_OBJECT_DIRECTORY=str(objects), GIT_ALTERNATE_OBJECT_DIRECTORIES=os.pathsep.join(alternates),
               GIT_INDEX_FILE=str(objects.parent / "index"))
    return env


def pruned_tree(repo: Path, treeish: str, drop: list[str], env: dict[str, str]) -> str:
    """`treeish` with the `drop` paths removed, written as a temporary tree object."""
    if not drop:
        return git(repo, "rev-parse", f"{treeish}^{{tree}}", env=env).strip()
    git(repo, "read-tree", treeish, env=env)
    done = subprocess.run(["git", "-C", str(repo), "update-index", "--force-remove", "-z", "--stdin"],
                          input="\0".join(drop).encode("utf-8", "surrogateescape"),
                          capture_output=True, env=env)
    if done.returncode != 0:
        raise DiffSizeError(done.stderr.decode("utf-8", "replace").strip())
    return git(repo, "write-tree", env=env).strip()


def count_product(repo: Path, base: str, head: str) -> tuple[list[FileCount], Filtered]:
    """Counts for product code only.

    Each side is judged on its own: a side that isn't product code is removed from a
    temporary copy of its tree, and the two copies are diffed. So a skipped side adds
    no lines and supplies no moves (a src/ line never counts as moved from dist/), and
    no path list is passed to git, whatever the size of the commit."""
    repo = toplevel(repo)
    filtered = product_paths(repo, base, head)
    if not filtered.paths:
        return [], filtered
    with tempfile.TemporaryDirectory(prefix="diff-size-") as tmp:
        objects = Path(tmp) / "objects"
        objects.mkdir()
        env = scratch_env(repo, objects)
        base_tree = pruned_tree(repo, base, filtered.drop_old, env)
        head_tree = pruned_tree(repo, head, filtered.drop_new, env)
        files = count_range(repo, base_tree, head_tree, env=env)
    return files, filtered


# --- Report and CLI (slice 04) ------------------------------------------------------

DIFF_TARGET, DIFF_SOFT, DIFF_HARD = 400, 800, 1500
DIFF_LABEL = {"target": f"over target ({DIFF_TARGET})", "soft": f"over soft ({DIFF_SOFT})",
              "hard": f"over hard ({DIFF_HARD})"}
NOTES = [
    "Product code only, with codebase-rubric's skip rules.",
    "Moved lines ignore indentation changes. A moved line shorter than git's block floor "
    "(20 letters and digits) counts as new, so new leans high.",
    "The commit rows find moves inside each commit; the whole-range row finds moves across "
    "the range, so its new count can be lower than the rows' sum.",
    "The whole-range row starts where the branch left the base (their merge base), as a PR does.",
    "Deleted leaves out moved-out lines; a moved block shows only under Moved.",
]


def diff_tier(new: int) -> str | None:
    if new > DIFF_HARD:
        return "hard"
    if new > DIFF_SOFT:
        return "soft"
    if new > DIFF_TARGET:
        return "target"
    return None


def summarise(files: list[FileCount], filtered: Filtered) -> dict:
    new = sum(f.new for f in files)
    return {"new": new, "moved": sum(f.moved for f in files),
            "deleted": sum(f.deleted for f in files), "moved_out": sum(f.moved_out for f in files),
            "tier": diff_tier(new), "skipped": dict(sorted(filtered.skipped.items())),
            "attrs_from_worktree": filtered.attrs_from_worktree}


def shallow_commits(repo: Path) -> set[str]:
    """Commits whose parents a shallow clone doesn't have."""
    path = Path(git(repo, "rev-parse", "--git-path", "shallow").strip())
    path = path if path.is_absolute() else repo / path
    return set(path.read_text().split()) if path.is_file() else set()


def merge_base(repo: Path, a: str, b: str) -> str | None:
    out = git(repo, "merge-base", a, b, check=False).strip()
    return out or None


def subject(repo: Path, commit: str) -> str:
    return git(repo, "log", "-1", "--format=%s", commit).strip()


def report(repo: Path, rev_range: str) -> dict:
    check_git()
    check_repo(repo)
    repo = toplevel(repo)
    commits = commits_in(repo, rev_range)
    shallow = shallow_commits(repo)
    rows = []
    for sha in commits:
        files, filtered = count_product(repo, parent(repo, sha), sha)
        rows.append({"commit": sha[:7], "subject": subject(repo, sha), **summarise(files, filtered),
                     "parent_missing": sha in shallow})
    total, base_note = None, None
    if ".." in rev_range:
        a, _, b = rev_range.partition("..")
        a_sha, b_sha = resolve(repo, a or "HEAD"), resolve(repo, b or "HEAD")
        base = merge_base(repo, a_sha, b_sha)
        if base is None:
            base, base_note = EMPTY_TREE, "no-common-history"
        elif base != a_sha:
            base_note = "base-not-ancestor"
        files, filtered = count_product(repo, base, b_sha)
        total = {**summarise(files, filtered), "base": base[:7] if base != EMPTY_TREE else None,
                 "base_note": base_note}
    return {"range": rev_range,
            "tiers": {"target": DIFF_TARGET, "soft": DIFF_SOFT, "hard": DIFF_HARD},
            "commits": rows, "total": total, "notes": NOTES}


def warnings(data: dict) -> list[str]:
    out = []
    for row in data["commits"]:
        if row["tier"] == "soft":
            out.append(f"`{row['commit']}` is {DIFF_LABEL['soft']}: consider Reslice.")
        elif row["tier"] == "hard":
            out.append(f"`{row['commit']}` is {DIFF_LABEL['hard']}: reslice before review.")
    total = data["total"]
    if total and total["tier"] in ("soft", "hard"):
        out.append(f"The whole range is {DIFF_LABEL[total['tier']]}: split the goal.")
    for row in data["commits"]:
        if row["parent_missing"]:
            out.append(f"`{row['commit']}` has no parent in this shallow clone, so its row counts "
                       "every line as new. Fetch more history for a real count.")
    if total and total["base_note"] == "base-not-ancestor":
        out.append(f"`{data['range'].partition('..')[0]}` is not an ancestor of the range's end; "
                   f"the whole range is sized from their merge base `{total['base']}`.")
    if total and total["base_note"] == "no-common-history":
        out.append("The range's two ends share no history; the whole range is sized from an empty tree.")
    if any(r["attrs_from_worktree"] for r in data["commits"]) or (total and total["attrs_from_worktree"]):
        out.append("linguist attributes were read from the working tree (git older than 2.40).")
    return out


def cell(text: str) -> str:
    """Table-safe text: an HTML entity for |, so no backslash in a subject can unescape it."""
    return text.replace("|", "&#124;")


def as_text(data: dict) -> str:
    out = [f"Change size for `{data['range']}`", "",
           "| Commit | Subject | New | Moved | Deleted | Tier |", "|---|---|---|---|---|---|"]
    for r in data["commits"]:
        tier = DIFF_LABEL[r["tier"]] if r["tier"] else ""
        out.append(f"| `{r['commit']}` | {cell(r['subject'])} | {r['new']} | {r['moved']} | {r['deleted']} | {tier} |")
    total = data["total"]
    if total:
        tier = DIFF_LABEL[total["tier"]] if total["tier"] else ""
        out.append(f"| **Whole range** | diffed at once | **{total['new']}** | {total['moved']} | "
                   f"{total['deleted']} | {tier} |")
    skipped = (total or (data["commits"][0] if data["commits"] else {"skipped": {}}))["skipped"]
    out += ["", "Skipped files: " + (", ".join(f"{SKIP_LABELS[k]}: {v}" for k, v in skipped.items()) or "none")]
    warn = warnings(data)
    if warn:
        out += ["", "**Warnings**", ""] + [f"- {w}" for w in warn]
    out += ["", "**Notes**", ""] + [f"- {n}" for n in data["notes"]]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--json"]
    if len(args) != 2 or any(a.startswith("-") for a in args):
        print("usage: diff_size.py <repo> <range> [--json]", file=sys.stderr)
        return 2
    try:
        data = report(Path(args[0]), args[1])
    except DiffSizeError as err:
        print(f"diff_size: {err}", file=sys.stderr)
        return 2
    print(json.dumps(data, indent=2) if "--json" in argv else as_text(data))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
