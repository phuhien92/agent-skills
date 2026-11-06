#!/usr/bin/env python3
"""Compare a scorecard with the previous one: score changes and tier moves.

Usage:
  delta.py <previous.md> <current.md>
  delta.py --dir <scorecards-dir> <current.md>

With --dir, the previous scorecard is the newest one in that folder that sorts
before <current.md> (names are <YYYY-MM-DD>.md or <YYYY-MM-DD>-<n>.md). With no
previous scorecard, prints "First run." Prints markdown for the scorecard's
delta section. Exits 1 with a reason if either file breaks the contract (for
example, a marker was edited away), 2 on bad usage. Never guesses.
Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_scorecard import AREAS, ContractError, parse  # noqa: E402

NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-(\d+))?\.md$")


def order_key(path: Path) -> tuple[str, int] | None:
    m = NAME.match(path.name)
    return (m.group(1), int(m.group(2) or 1)) if m else None


def previous_in(folder: Path, current: Path) -> Path | None:
    """Newest scorecard in folder that sorts before current, or None."""
    here = order_key(current)
    if here is None:
        raise ContractError(f"{current.name} is not named <YYYY-MM-DD>.md or <YYYY-MM-DD>-<n>.md")
    older = [(k, p) for p in folder.glob("*.md") if (k := order_key(p)) and k < here]
    return max(older)[1] if older else None


def delta(prev_text: str | None, cur_text: str) -> str:
    cur = parse(cur_text)
    if prev_text is None:
        return "First run."
    prev = parse(prev_text)
    lines = [f"Since {prev['meta'].get('Date', '?')} (`{prev['meta'].get('Commit', '?')}`):", ""]

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
        if len(argv) == 3 and argv[0] == "--dir":
            current = Path(argv[2])
            prev_path = previous_in(Path(argv[1]), current)
        elif len(argv) == 2 and not argv[0].startswith("--"):
            prev_path, current = Path(argv[0]), Path(argv[1])
        else:
            print(__doc__.strip().splitlines()[2], file=sys.stderr)
            return 2
        prev_text = prev_path.read_text(encoding="utf-8") if prev_path else None
        print(delta(prev_text, current.read_text(encoding="utf-8")))
        return 0
    except ContractError as err:
        print(f"delta: {err}", file=sys.stderr)
        return 1
    except OSError as err:
        print(f"delta: can't read a scorecard: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
