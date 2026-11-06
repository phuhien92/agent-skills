#!/usr/bin/env python3
"""Compare a scorecard with the previous one: score changes and tier moves.

Usage:
  delta.py <previous.md> <current.md>
  delta.py --dir <scorecards-dir> <current.md>

With --dir, the previous scorecard is the newest *valid* one in that folder
that sorts before <current.md> (names are <YYYY-MM-DD>.md, then
<YYYY-MM-DD>-<n>.md with n from 1 up). Valid means check_scorecard.py's checks
pass without --repo, so citations are not re-verified. Newer earlier scorecards
that aren't valid or can't be read are skipped and named with the reason, so one
broken file can never hide a trend.
With no earlier scorecard, prints "First run."; with earlier ones but none
valid, prints "Not compared:" and lists them. Prints markdown for the scorecard's
delta section. Exits 1 when the current scorecard isn't valid, can't be read,
or isn't named as above, when --dir isn't a folder, or (two-file form only) when
the previous scorecard isn't valid. Exits 2 on bad usage. Never guesses.
Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_scorecard import AREAS, ContractError, parse, problems  # noqa: E402

NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-([1-9]\d*))?\.md$")


def order_key(path: Path) -> tuple[str, int] | None:
    m = NAME.match(path.name)
    return (m.group(1), int(m.group(2) or 0)) if m else None


def earlier_in(folder: Path, current: Path) -> list[Path]:
    """Scorecards in folder that sort before current, newest first."""
    here = order_key(current)
    if here is None:
        raise ContractError(f"{current.name} is not named <YYYY-MM-DD>.md or <YYYY-MM-DD>-<n>.md")
    if not folder.is_dir():
        raise ContractError(f"--dir {folder} is not a folder")
    older = [(k, p) for p in folder.glob("*.md") if (k := order_key(p)) and k < here]
    return [p for _, p in sorted(older, reverse=True)]


def previous_in(folder: Path, current: Path) -> Path | None:
    """Newest scorecard in folder that sorts before current, valid or not, or None."""
    earlier = earlier_in(folder, current)
    return earlier[0] if earlier else None


def pick_previous(folder: Path, current: Path) -> tuple[Path | None, list[str]]:
    """Newest valid earlier scorecard, plus 'name: reason' for each newer one skipped."""
    skipped = []
    for path in earlier_in(folder, current):
        try:
            found = problems(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as err:
            found = [f"can't read it ({getattr(err, 'strerror', None) or err})"]
        if not found:
            return path, skipped
        skipped.append(f"{path.name}: {found[0]}")
    return None, skipped


def require_valid(text: str, which: str) -> None:
    found = problems(text)
    if found:
        raise ContractError(f"{which} scorecard is not valid: " + "; ".join(found))


def delta(prev_text: str | None, cur_text: str, skipped: list[str] | None = None) -> str:
    require_valid(cur_text, "current")
    skipped = skipped or []
    if prev_text is None:
        if skipped:
            return "Not compared: no valid earlier scorecard.\n\nSkipped:\n" + "\n".join(f"- {s}" for s in skipped)
        return "First run."
    require_valid(prev_text, "previous")
    cur, prev = parse(cur_text), parse(prev_text)
    lines = [f"Since {prev['meta'].get('Date', '?')} (`{prev['meta'].get('Commit', '?')}`):", ""]
    if skipped:
        lines += ["Skipped newer scorecards that aren't valid:"] + [f"- {s}" for s in skipped] + [""]

    before = {r.get("area"): r.get("score", "").strip() for r in prev["scores"]}
    after = {r.get("area"): r.get("score", "").strip() for r in cur["scores"]}
    changed = [f"- {a}: {before.get(a, 'missing')} → {after.get(a, 'missing')}"
               for a in AREAS if before.get(a) != after.get(a)]
    same = [f"{a} {after.get(a)}" for a in AREAS if before.get(a) == after.get(a)]
    lines.append("Scores:")
    lines += changed or ["- No score changed."]
    if same:
        lines.append(f"Unchanged: {', '.join(same)}")

    old = {r["path"]: r for r in prev["size"]}
    new = {r["path"]: r for r in cur["size"]}
    moves = []
    for path in sorted(old.keys() & new.keys()):
        o, n = old[path], new[path]
        if o["tier"] != n["tier"]:
            moves.append(f"- `{path}`: {o['tier']} → {n['tier']} ({o['lines']} → {n['lines']} lines)")
    for path in sorted(new.keys() - old.keys()):
        moves.append(f"- New over 500: `{path}` ({new[path]['lines']} lines, {new[path]['tier']})")
    for path in sorted(old.keys() - new.keys()):
        moves.append(f"- Now under 500 or gone: `{path}` (was {old[path]['lines']} lines)")
    lines += ["", "Size:"] + (moves or ["- No file changed tier."])
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    try:
        skipped: list[str] = []
        if len(argv) == 3 and argv[0] == "--dir":
            current = Path(argv[2])
            prev_path, skipped = pick_previous(Path(argv[1]), current)
        elif len(argv) == 2 and not argv[0].startswith("--"):
            prev_path, current = Path(argv[0]), Path(argv[1])
        else:
            print(__doc__.strip().splitlines()[2], file=sys.stderr)
            return 2
        prev_text = prev_path.read_text(encoding="utf-8") if prev_path else None
        print(delta(prev_text, current.read_text(encoding="utf-8"), skipped))
        return 0
    except ContractError as err:
        print(f"delta: {err}", file=sys.stderr)
        return 1
    except (OSError, UnicodeDecodeError) as err:
        print(f"delta: can't read a scorecard: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
