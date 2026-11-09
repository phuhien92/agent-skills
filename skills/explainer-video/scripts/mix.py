#!/usr/bin/env python3
"""Mix narration, logged sound events and music into a mastered stereo WAV.

Usage:
  python3 mix.py --narration vo.wav --offset 0.6 --events frames/sfx.json --cues cues.json \
                 [--music bed.wav] [--music-db -4] [--duck 0.6] [--length 72] [--target -14] --out mix.wav

cues.json maps an event kind to [file, gain_dB] (file paths relative to cues.json) or [file, gain_dB, {"rate": 13}]. A kind may carry a
duration after a colon ("type:1.20"); with "rate", the sound repeats across that duration (typing),
without it the sound is trimmed to it (pen strokes). Unknown kinds are listed and skipped.
The voice is high-passed and set to -18 LUFS (+4 dB in the mix); music ducks under it. The master
is limited to -1 dBFS and set so the stereo file measures --target LUFS in ffmpeg's ebur128.
Needs numpy, scipy, soundfile, pyloudnorm, soxr.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys

SR = 48000


def load(path: str):
    import soundfile as sf
    import soxr
    x, sr = sf.read(path, always_2d=True)
    x = x.mean(1)
    return soxr.resample(x, sr, SR) if sr != SR else x


def place(buf, x, t: float, db: float = 0.0) -> None:
    i = max(0, int(t * SR))
    j = min(len(buf), i + len(x))
    if 0 <= i < len(buf):
        buf[i:j] += x[: j - i] * 10 ** (db / 20)


def limit(x, ceil: float = 0.89, look: float = 0.004, rel: float = 0.12):
    import numpy as np
    from scipy.ndimage import maximum_filter1d
    pk = maximum_filter1d(np.abs(x), 2 * int(look * SR) + 1)
    g = np.minimum(1.0, ceil / np.maximum(pk, 1e-9))
    a = np.exp(-1 / (rel * SR))
    out = np.empty_like(g)
    cur = 1.0
    for i in range(len(g)):
        cur = g[i] if g[i] < cur else a * cur + (1 - a) * g[i]
        out[i] = cur
    return x * np.minimum(out, g)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--narration")
    ap.add_argument("--offset", type=float, default=0.6)
    ap.add_argument("--events")
    ap.add_argument("--cues")
    ap.add_argument("--music")
    ap.add_argument("--music-db", type=float, default=-4.0)
    ap.add_argument("--duck", type=float, default=0.6, help="how far music drops under the voice (0-1)")
    ap.add_argument("--length", type=float, help="seconds; default = longest layer")
    ap.add_argument("--target", type=float, default=-14.0, help="stereo integrated LUFS")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    try:
        import numpy as np
        import pyloudnorm as pyln
        import soundfile as sf
        from scipy.ndimage import uniform_filter1d
        from scipy.signal import butter, sosfilt
    except ImportError as e:
        sys.exit(f"missing {e.name}: pip install numpy scipy soundfile pyloudnorm soxr")
    random.seed(1)

    vo = load(a.narration) if a.narration else np.zeros(1)
    music = load(a.music) if a.music else np.zeros(1)
    events = json.load(open(a.events)) if a.events else []
    cues = json.load(open(a.cues)) if a.cues else {}
    length = a.length or max(a.offset + len(vo) / SR + 1, len(music) / SR, max([e["t"] for e in events], default=0) + 2)
    n = int(length * SR)
    meter = pyln.Meter(SR)

    voice = np.zeros(n)
    if a.narration:
        place(voice, vo, a.offset)
        voice = sosfilt(butter(2, 80, "high", fs=SR, output="sos"), voice)
        voice *= 10 ** ((-18 - meter.integrated_loudness(voice)) / 20)

    fx = np.zeros(n)
    cache: dict = {}
    missing: set[str] = set()
    missing_files: set[str] = set()
    cue_dir = os.path.dirname(os.path.abspath(a.cues)) if a.cues else "."
    for e in events:
        kind, _, dur = e["kind"].partition(":")
        cue = cues.get(kind)
        if not cue:
            missing.add(kind)
            continue
        f = os.path.join(cue_dir, cue[0])
        if f not in cache:
            try:
                cache[f] = load(f)
            except Exception:
                missing_files.add(cue[0])
                cache[f] = None
        snd = cache[f]
        if snd is None:
            continue
        gain, extra = cue[1], (cue[2] if len(cue) > 2 else {})
        if dur and extra.get("rate"):
            for k in range(max(1, int(float(dur) * extra["rate"]))):
                place(fx, snd, e["t"] + k / extra["rate"] + random.uniform(-0.01, 0.01), gain + random.uniform(-2, 1))
        elif dur:
            place(fx, snd[: int(float(dur) * SR) + 2000], e["t"], gain)
        else:
            place(fx, snd, e["t"], gain)
    if missing:
        print("no cue for:", ", ".join(sorted(missing)))
    if missing_files:
        print("could not read (paths are relative to the cues file):", ", ".join(sorted(missing_files)))

    bed = np.zeros(n)
    if a.music:
        place(bed, music, 0.0)
        env = uniform_filter1d(np.abs(voice), int(0.3 * SR))
        env = env / env.max() if env.max() > 0 else env
        bed *= uniform_filter1d(1 - a.duck * np.clip(env * 6, 0, 1), int(0.25 * SR)) * 10 ** (a.music_db / 20)

    mix = bed + fx + voice * 10 ** (4 / 20)
    fade = min(int(1.2 * SR), n)
    mix[-fade:] *= np.linspace(1, 0, fade)
    mono_target = a.target - 3.0   # identical channels measure 3 dB louder in ebur128
    for _ in range(4):
        mix = limit(mix * 10 ** ((mono_target - meter.integrated_loudness(mix)) / 20))
    speaking = uniform_filter1d(np.abs(voice), int(0.3 * SR)) > 0.02 * (np.abs(voice).max() or 1)
    if a.narration and speaking.any():
        print(f"voice {meter.integrated_loudness(voice * 10 ** (4 / 20)):.1f} LUFS, "
              f"music+fx while speaking {meter.integrated_loudness((bed + fx) * speaking):.1f} LUFS")
    print(f"master {meter.integrated_loudness(mix):.1f} LUFS mono -> about {meter.integrated_loudness(mix) + 3:.1f} stereo")
    sf.write(a.out, np.stack([mix, mix], 1), SR, subtype="PCM_24")


if __name__ == "__main__":
    main()
