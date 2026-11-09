#!/usr/bin/env python3
"""Find where each narration sentence starts and ends, from the pauses.

Usage: python3 vo_lines.py narration.wav --script script.txt [--noise -38] [--min-pause 0.25] [--json]
       python3 vo_lines.py narration.wav --lines 10            (no script: guess from pause length)

ffmpeg's silencedetect splits the take into spoken phrases. With --script (one sentence per line),
each sentence is expected to hold about (its commas, colons, semicolons, dashes and inner full stops)
+ 1 phrases. The phrases are split into one run per sentence so the counts fit and the breaks fall
on long pauses; lines whose count differs are flagged (narrators skip some commas). Without a
script it guesses: the N-1 longest pauses as sentence breaks (narrators often pause as long at a
colon as at a full stop, so check the result).
Prints a table, or JSON with --json: {"duration", "method", "lines": [{"start", "end", "phrases"}]}.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys


def pauses(path: str, noise: float, min_pause: float) -> tuple[list[tuple[float, float]], float]:
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=n={noise}dB:d={min_pause}", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not dur:
        sys.exit("ffmpeg could not read the audio:\n" + out.strip()[-800:])
    total = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3)) if dur else 0.0
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    if len(ends) < len(starts):
        ends.append(total)
    return list(zip(starts, ends)), total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("audio")
    ap.add_argument("--script", help="text file, one narration sentence per line")
    ap.add_argument("--lines", type=int, help="number of sentences, when there is no script")
    ap.add_argument("--noise", type=float, default=-38.0, help="silence threshold in dB (default -38)")
    ap.add_argument("--min-pause", type=float, default=0.25, help="shortest pause in seconds (default 0.25)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    ps, total = pauses(a.audio, a.noise, a.min_pause)
    lead = ps[0] if ps and ps[0][0] < 0.05 else None
    tail = ps[-1] if ps and ps[-1][1] >= total - 0.05 else None
    inner = [p for p in ps if p is not lead and p is not tail]
    t0, t1 = (lead[1] if lead else 0.0), (tail[0] if tail else total)
    bounds = [t0] + [x for p in inner for x in p] + [t1]
    segs = [(bounds[i], bounds[i + 1]) for i in range(0, len(bounds), 2)]      # spoken phrases
    sentences = [ln.strip() for ln in open(a.script, encoding="utf-8") if ln.strip()] if a.script else []
    want = [len(re.findall(r"[,:;\u2014]|--|[.!?](?=\s+\S)", s)) + 1 for s in sentences]
    lines, method = [], "script"
    if sentences and len(segs) >= len(sentences):
        # Split the phrases into len(sentences) runs: each run should hold about its sentence's
        # expected phrase count, and sentence breaks should fall on long pauses.
        n, m = len(segs), len(sentences)
        gap = [segs[i + 1][0] - segs[i][1] for i in range(n - 1)] + [0.0]
        INF = float("inf")
        best = [[INF] * (m + 1) for _ in range(n + 1)]
        back = [[0] * (m + 1) for _ in range(n + 1)]
        best[0][0] = 0.0
        for j in range(1, m + 1):
            for i in range(j, n - (m - j) + 1):
                for k in range(j - 1, i):
                    if best[k][j - 1] == INF:
                        continue
                    c = best[k][j - 1] + abs((i - k) - want[j - 1]) - (2.0 * gap[i - 1] if j < m else 0)
                    if c < best[i][j]:
                        best[i][j], back[i][j] = c, k
        cuts, i = [], n
        for j in range(m, 0, -1):
            k = back[i][j]; cuts.append((k, i)); i = k
        for (k, i), w in zip(reversed(cuts), want):
            lines.append({"start": round(segs[k][0], 2), "end": round(segs[i - 1][1], 2), "phrases": i - k, "expected": w})
    else:
        n_lines = len(sentences) or a.lines
        if not n_lines:
            ap.error("give --script or --lines")
        if len(inner) < n_lines - 1:
            print(f"only {len(inner)} pauses for {n_lines} lines: lower --min-pause or raise --noise", file=sys.stderr)
            return 1
        method = "longest pauses (check by hand)"
        breaks = sorted(sorted(inner, key=lambda p: p[1] - p[0], reverse=True)[: n_lines - 1])
        cur = t0
        for b in breaks + [(t1, t1)]:
            lines.append({"start": round(cur, 2), "end": round(b[0], 2), "phrases": sum(1 for s0, s1 in segs if cur <= s0 < b[0])}); cur = b[1]

    if a.json:
        print(json.dumps({"duration": round(total, 2), "method": method, "lines": lines}, indent=1))
    else:
        print(f"{'line':>4}  {'start':>6}  {'end':>6}  phrases")
        for i, ln in enumerate(lines, 1):
            flag = f"  (script suggests {ln['expected']})" if ln.get("expected", ln["phrases"]) != ln["phrases"] else ""
            print(f"{i:>4}  {ln['start']:>6.2f}  {ln['end']:>6.2f}  {ln['phrases']}{flag}")
        print(f"method: {method}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
