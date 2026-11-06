#!/usr/bin/env python3
"""Measure how the factory skills do on real work, from the files they leave behind.

Usage: skill_metrics.py [repo ...] [--json]

Reads each repo (default: the current folder) and reports, per skill:

- slice-spec: specs, slices, resliced slices (a slice file marked "Replaced by").
- decision-checker: ledger runs, entries by verdict and confidence, entries per
  slice. Many entries on one slice means that slice was unclear.
- codebase-rubric: scorecards per repo, first-to-latest score change per area,
  and the largest score gap between two scorecards of the same commit
  (scoring noise; it should stay at 1 or less).
- outcomes: lines you add to `skill-outcomes.md` when a skill's call was wrong,
  one per event:  `- 2026-11-06 | decision-checker | overruled | <note>`
  Kinds: overruled (you disagreed with a call), escaped (a problem the skill
  should have caught got through), confirmed (a call proved right).

Reads only; writes nothing. Standard library only. Exits 2 on bad usage.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

AREAS = ["Architecture", "Modularity", "Abstraction", "Components", "Errors"]
VERDICT = re.compile(r"\*\*Verdict:\*\*\s*(sound|unsound|needs-you)", re.I)
CONFIDENCE = re.compile(r"\*\*Confidence:\*\*\s*(low|medium|high)", re.I)
SLICE = re.compile(r"\*\*Slice:\*\*\s*(\d+)")
SCORECARD_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:-([1-9]\d*))?\.md$")
OUTCOME = re.compile(r"^\s*-\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([\w-]+)\s*\|\s*(overruled|escaped|confirmed)\s*\|\s*(.*)$", re.I)
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build"}


def walk(root: Path, pattern: str) -> list[Path]:
    return sorted(p for p in root.rglob(pattern)
                  if not SKIP_DIRS.intersection(p.relative_to(root).parts[:-1]))


def ledger_stats(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = text.split("\n### ")[1:]
    verdicts, confidence, per_slice = Counter(), Counter(), Counter()
    for entry in entries:
        if m := VERDICT.search(entry):
            verdicts[m.group(1).lower()] += 1
        if m := CONFIDENCE.search(entry):
            confidence[m.group(1).lower()] += 1
        if m := SLICE.search(entry):
            per_slice[m.group(1)] += 1
    runs = 1 + len(re.findall(r"^# Check ", text, re.M)) if entries else 0
    return {"path": str(path), "runs": runs, "entries": len(entries),
            "verdicts": dict(sorted(verdicts.items())),
            "confidence": dict(sorted(confidence.items())),
            "per_slice": dict(sorted(per_slice.items()))}


def spec_stats(spec: Path) -> dict:
    slices = sorted((spec / "slices").glob("*.md")) if (spec / "slices").is_dir() else []
    replaced = [s.name for s in slices if "Replaced by" in s.read_text(encoding="utf-8", errors="replace")[:400]]
    return {"spec": spec.name, "slices": len(slices), "resliced": len(replaced)}


def table(text: str, name: str) -> list[list[str]]:
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    if start not in text or end not in text:
        return []
    body = text.split(start, 1)[1].split(end, 1)[0]
    rows = []
    for line in body.splitlines():
        if line.strip().startswith("|") and not re.fullmatch(r"[|\s:-]+", line.strip()):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows[1:]


def scorecard(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = {r[0]: r[1] for r in table(text, "meta") if len(r) >= 2}
    scores = {r[0]: r[1] for r in table(text, "scores") if len(r) >= 2}
    if not meta or not scores:
        return None
    return {"file": path.name, "commit": meta.get("Commit", "?"), "date": meta.get("Date", "?"),
            "independent": meta.get("Scorers independent", "?"), "scores": scores}


def as_number(score: str) -> int | None:
    return int(score) if score.strip().isdigit() else None


def rubric_stats(folder: Path) -> dict:
    named = [p for p in folder.glob("*.md") if SCORECARD_NAME.match(p.name)]
    # Run order: by date, then plain name before -1, -2, ... (text sort gets -2 before plain).
    named.sort(key=lambda p: (SCORECARD_NAME.match(p.name).group(1), int(SCORECARD_NAME.match(p.name).group(2) or 0)))
    cards = [c for p in named if (c := scorecard(p))]
    result = {"folder": str(folder), "scorecards": len(cards), "unreadable": 0, "change": {}, "noise": None}
    result["unreadable"] = len(named) - len(cards)
    if len(cards) >= 2:
        first, last = cards[0], cards[-1]
        result["change"] = {a: f"{first['scores'].get(a, '?')} → {last['scores'].get(a, '?')}" for a in AREAS}
    by_commit = defaultdict(list)
    for c in cards:
        by_commit[c["commit"]].append(c)
    gaps = []
    for same in by_commit.values():
        if len(same) < 2:
            continue
        for a in AREAS:
            nums = [n for c in same if (n := as_number(c["scores"].get(a, ""))) is not None]
            if len(nums) >= 2:
                gaps.append(max(nums) - min(nums))
    result["noise"] = max(gaps) if gaps else None
    return result


def outcome_stats(path: Path) -> dict:
    counts = defaultdict(Counter)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if m := OUTCOME.match(line):
            counts[m.group(2)][m.group(3).lower()] += 1
    return {k: dict(sorted(v.items())) for k, v in sorted(counts.items())}


def collect(repo: Path) -> dict:
    specs = [spec_stats(p.parent) for p in walk(repo, "README.md")
             if p.parent.parent.name == "specs" and (p.parent / "slices").is_dir()]
    ledgers = [ledger_stats(p) for p in walk(repo, "decisions.md")]
    rubrics = [rubric_stats(p) for p in walk(repo, "scorecards") if p.is_dir()]
    outcomes_file = repo / "skill-outcomes.md"
    return {"repo": str(repo), "specs": specs, "ledgers": ledgers, "rubrics": rubrics,
            "outcomes": outcome_stats(outcomes_file) if outcomes_file.is_file() else {}}


def as_text(results: list[dict]) -> str:
    out = []
    for r in results:
        out.append(f"# {r['repo']}")
        out.append("\n## slice-spec")
        out += [f"- {s['spec']}: {s['slices']} slices, {s['resliced']} resliced" for s in r["specs"]] or ["- no specs"]
        out.append("\n## decision-checker")
        for l in r["ledgers"]:
            v = ", ".join(f"{k} {n}" for k, n in l["verdicts"].items()) or "none"
            c = ", ".join(f"{k} {n}" for k, n in l["confidence"].items()) or "none"
            out.append(f"- {l['path']}: {l['runs']} runs, {l['entries']} entries ({v}; confidence {c})")
            if l["per_slice"]:
                top = max(l["per_slice"].items(), key=lambda kv: kv[1])
                out.append(f"  - per slice: {', '.join(f'{k}: {n}' for k, n in l['per_slice'].items())} (most: slice {top[0]})")
        if not r["ledgers"]:
            out.append("- no ledgers")
        out.append("\n## codebase-rubric")
        for b in r["rubrics"]:
            noise = "n/a (no repeat run on one commit)" if b["noise"] is None else str(b["noise"])
            out.append(f"- {b['folder']}: {b['scorecards']} scorecards, {b['unreadable']} unreadable, noise {noise}")
            if b["change"]:
                out.append("  - first to latest: " + ", ".join(f"{a} {d}" for a, d in b["change"].items()))
        if not r["rubrics"]:
            out.append("- no scorecards")
        out.append("\n## outcomes (skill-outcomes.md)")
        out += [f"- {skill}: " + ", ".join(f"{k} {n}" for k, n in kinds.items()) for skill, kinds in r["outcomes"].items()] or ["- none logged"]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    paths = [a for a in argv if a != "--json"]
    if any(a.startswith("--") for a in paths):
        print("usage: skill_metrics.py [repo ...] [--json]", file=sys.stderr)
        return 2
    repos = [Path(p) for p in paths] or [Path.cwd()]
    for repo in repos:
        if not repo.is_dir():
            print(f"skill_metrics: {repo} is not a folder", file=sys.stderr)
            return 2
    results = [collect(r.resolve()) for r in repos]
    print(json.dumps(results, indent=2, ensure_ascii=False) if as_json else as_text(results), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
