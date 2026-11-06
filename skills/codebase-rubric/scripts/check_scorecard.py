#!/usr/bin/env python3
"""Check that a codebase scorecard follows the contract in ../scorecard.md.

Usage: check_scorecard.py <scorecard.md> [--repo <path>]

With --repo, every cited `path:line` must exist in that repo: the file is
there and the line is within its length.

Exits 0 when the scorecard is valid. Exits 1 and prints one reason per line
when it isn't. Exits 2 if the file can't be read. Standard library only.
Also importable: parse(text) returns the marked tables for delta.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

AREAS = ["Architecture", "Modularity", "Abstraction", "Components", "Errors"]
SECTIONS = ["meta", "size", "scores", "trace", "delta"]
META_KEYS = ["Repo", "Commit", "Date", "Rubric approved", "Scorers independent"]
CITATION = re.compile(r"`[^`\s]+:\d+(?:-\d+)?`")
SAMPLE = re.compile(r"^(\d+) of (\d+)$")
TIERS = {"over target (500)": (500, 800), "over soft (800)": (800, 1000), "over hard (1000)": (1000, None)}
NOT_SCORED = "not scored"
MIN_SCORED = 3
CITE_PARTS = re.compile(r"`([^`\s]+):(\d+)(?:-(\d+))?`")


class ContractError(Exception):
    """A scorecard section is missing or malformed."""


def section(text: str, name: str) -> str:
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ContractError(f"marker {start} or {end} missing or repeated")
    body = text.split(start, 1)[1].split(end, 1)[0]
    return body.strip()


def table_rows(body: str) -> list[list[str]]:
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows[1:]  # drop the header row


def parse(text: str) -> dict:
    """Return the marked tables. Raises ContractError if a marker is missing."""
    meta = {r[0]: r[1] for r in table_rows(section(text, "meta")) if len(r) >= 2}
    size = [{"path": r[0].strip("`"), "lines": r[1], "tier": r[2]}
            for r in table_rows(section(text, "size")) if len(r) >= 3]
    scores = [dict(zip(["area", "score", "scope", "sample", "evidence"], r))
              for r in table_rows(section(text, "scores"))]
    trace = [l.strip() for l in section(text, "trace").splitlines() if re.match(r"^\d+\.", l.strip())]
    return {"meta": meta, "size": size, "scores": scores, "trace": trace,
            "delta": section(text, "delta")}


def citation_problems(text: str, repo: Path) -> list[str]:
    data = parse(text)
    cited = " ".join(r.get("evidence", "") for r in data["scores"]) + " " + " ".join(data["trace"])
    found, seen = [], set()
    for path, start, end in CITE_PARTS.findall(cited):
        if (path, start, end) in seen:
            continue
        seen.add((path, start, end))
        if end and int(end) < int(start):
            found.append(f"citation: `{path}:{start}-{end}` runs backwards")
            continue
        target = (repo / path).resolve()
        try:
            target.relative_to(repo.resolve())
        except ValueError:
            found.append(f"citation: `{path}` points outside {repo}")
            continue
        if not target.is_file():
            found.append(f"citation: `{path}` is not a file in {repo}")
            continue
        with target.open("rb") as fh:
            length = sum(1 for _ in fh)
        last = int(end or start)
        if int(start) < 1 or last > length:
            found.append(f"citation: `{path}:{start}{'-' + end if end else ''}` is past the end ({length} lines)")
    return found


def problems(text: str, repo: Path | None = None) -> list[str]:
    found = []
    for name in SECTIONS:
        try:
            section(text, name)
        except ContractError as err:
            found.append(str(err))
    if found:
        return found
    data = parse(text)

    for key in META_KEYS:
        if not data["meta"].get(key) or data["meta"][key].startswith("<"):
            found.append(f"meta: missing {key}")
    for key in ("Rubric approved", "Scorers independent"):
        if data["meta"].get(key, "").lower() not in ("yes", "no"):
            found.append(f"meta: {key} must be yes or no")

    if not re.search(r"^Skipped: ", section(text, "size"), re.M):
        found.append("size: no 'Skipped:' line inside the size markers")
    for row in data["size"]:
        tier = TIERS.get(row["tier"])
        if not row["lines"].isdigit() or tier is None:
            found.append(f"size: bad row for {row['path']}: lines '{row['lines']}', tier '{row['tier']}'")
            continue
        low, high = tier
        n = int(row["lines"])
        if n <= low or (high is not None and n > high):
            found.append(f"size: {row['path']} has {n} lines, which is not {row['tier']}")

    areas = [s.get("area", "") for s in data["scores"]]
    if areas != AREAS:
        found.append(f"scores: areas must be {', '.join(AREAS)} in order; got {', '.join(areas) or 'none'}")
    errors_scored = True
    for row in data["scores"]:
        area, score = row.get("area", "?"), row.get("score", "").strip().lower()
        scope, sample, evidence = row.get("scope", ""), row.get("sample", ""), row.get("evidence", "")
        if score == NOT_SCORED:
            if area == "Errors":
                errors_scored = False
            if not scope or scope == "-":
                found.append(f"scores: {area} is not scored but names no scope")
            if not evidence or evidence == "-":
                found.append(f"scores: {area} is not scored but gives no reason")
            continue
        if score not in {"1", "2", "3", "4", "5"}:
            found.append(f"scores: {area} score must be 1-5 or 'not scored'; got '{row.get('score', '')}'")
            continue
        m = SAMPLE.match(sample)
        if not m:
            found.append(f"scores: {area} sample must read 'N of M'; got '{sample}'")
        elif int(m.group(2)) < 1 or int(m.group(1)) > int(m.group(2)):
            found.append(f"scores: {area} sample must have 1 <= M and N <= M; got '{sample}'")
        if not CITATION.search(evidence):
            found.append(f"scores: {area} evidence has no `path:line`")
        if not scope or scope == "-":
            found.append(f"scores: {area} names no scope")

    scored = sum(1 for r in data["scores"] if r.get("score", "").strip().lower() != NOT_SCORED)
    if scored < MIN_SCORED:
        found.append(f"scores: only {scored} areas scored; at least {MIN_SCORED} must be")

    if errors_scored:
        hops = data["trace"]
        if len(hops) < 2:
            found.append(f"trace: needs at least 2 hops; got {len(hops)}")
        for hop in hops:
            if not CITATION.match(re.sub(r"^\d+\.\s*", "", hop)):
                found.append(f"trace: hop does not start with `path:line`: {hop[:60]}")
    if repo is not None and not found:
        found += citation_problems(text, repo)
    return found


def main(argv: list[str]) -> int:
    repo = None
    if "--repo" in argv:
        i = argv.index("--repo")
        if i + 1 >= len(argv):
            print("usage: check_scorecard.py <scorecard.md> [--repo <path>]", file=sys.stderr)
            return 2
        repo = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
        if not repo.is_dir():
            print(f"check_scorecard: --repo {repo} is not a directory", file=sys.stderr)
            return 2
    if len(argv) != 1:
        print("usage: check_scorecard.py <scorecard.md> [--repo <path>]", file=sys.stderr)
        return 2
    try:
        text = Path(argv[0]).read_text(encoding="utf-8")
    except OSError as err:
        print(f"check_scorecard: can't read {argv[0]}: {err}", file=sys.stderr)
        return 2
    found = problems(text, repo)
    for p in found:
        print(p)
    if not found:
        print("ok")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
