---
name: explainer-video
description: Make a narrated explainer, story, or promo video as code (HTML + GSAP, rendered frame by frame to MP4) with its own sound mix. Use when the user asks for a short video, clip, trailer, explainer, lore or history video, or "turn this into a video", especially vertical clips for phones and socials, or wants a video re-cut in a different style (collage, notebook, storybook).
compatibility: Needs Node 18+ with Playwright Chromium, ffmpeg, and Python 3 with numpy, scipy, soundfile, pyloudnorm and soxr for the mix. GSAP and fonts install from npm (CDNs may be blocked).
---

# explainer-video

Build the film as one web page whose every frame is a pure function of time, render it frame by
frame, then mix narration, effects and music to a loudness target. Two things decide quality:
the style fits the content, and every beat lands on the narration.

## 1. Settle four things, in one question

Ask once, with a recommended answer for each (skip what the user already said):

| Ask | Default |
|---|---|
| Style | pick from `styles.md` by content; say why in one line |
| Format | 9:16, 1080×1920, for phones; 16:9 only for YouTube/desktop (set `W`, `H` in the starter) |
| Length | 30–75 s; follow the narration, never pad |
| Voice | none, the user's recording, or text-to-speech (say the cost first) |

Style is the call people get wrong. Read `styles.md` before recommending. Rule of thumb: real
evidence → collage desk; an invented world or a story drawn by hand → notebook draw-on; an app
that already animates its own scenes → record the app; characters acting → cartoon stage.

## 2. Script and narration

1. Write the voiceover as short sentences, one beat each (8–12 beats a minute).
2. Get the audio. Text to speech through a connected tool costs credits: preflight the price,
   tell the user the price and their balance, and ask before spending. If the file host is
   blocked, give the user the link and ask them to attach the file.
3. Time it: `python3 scripts/vo_lines.py narration.wav --script script.txt` (one sentence per
   line) prints each sentence's start and end. Look at any line it flags. If it reports too few
   pauses, lower `--min-pause` (for example 0.18). Use `--lines N` only when there is no script;
   it guesses from pause length and needs checking.
4. Place the narration at a fixed offset (0.6 s). Beat k starts at `offset + start_k`.

## 3. Gather the art

- Prefer the project's own art. Render its components to SVG or PNG with a temporary page and
  Playwright, then delete the temporary files. Never leave them in the user's repo.
- Read the project's rules first (AGENTS.md or similar): originality, icon style, what must not
  be imitated. Never draw a known franchise character or a real person.
- Paper, desk and print textures can be generated in code (numpy + Pillow); see `styles.md`.

## 4. Build the page

Start from `assets/starter.html`. It has the camera rig, a 12 fps element layer, `SEEK(t)`,
and helpers: `slideIn`, `type` (labels typed on twos), `ring` / `line` / `draw` (hand-drawn red
ink with a dot head), `hlSpan` (highlighter measured from the text), `schedule` (an SVG draws
itself stroke by stroke, then colours in), `write` (handwriting revealed at writing speed).

Hard rules:
- **Deterministic.** No `Math.random`, `Date` or CSS animations in the film; everything comes
  from `SEEK(t)`. Elements step at 12 fps (`floor(t*12)/12`); the camera moves smoothly.
- **Measure after loading.** Wait for fonts and images, re-place everything, then build the
  timeline. Measure highlights and underlines from the text's own spans, never by guessing.
- **One world, one camera.** Beats are places on one big page or desk; scenes change because the
  camera moves (glide 0.7–1.1 s, long-tail settle) or cuts on a sentence break, never by fading
  slides. Material fills ≥ 60% of the frame width.
- **Readable on a phone.** Body text ≥ 44 px, labels ≥ 34 px at the frame's scale. Nothing
  important within 120 px of the frame edge.
- **Log sound events.** Every helper pushes `{t, kind}` to `SFX`, so the mix follows the picture.

## 5. Review stills before rendering

`node scripts/render_frames.cjs page.html out/ --stills 1.5,6,12,...` (one time per beat, plus
mid-transition), then make a contact sheet and look at it:
`ffmpeg -pattern_type glob -i 'out/s_*.jpg' -vf "scale=270:-1,tile=6x2" sheet.png`. Check against `checks.md`; fix and repeat.
This loop is where most of the quality comes from; expect two or three passes.

## 6. Render, mix, encode

1. `node scripts/render_frames.cjs page.html frames/ --fps 30` (renders roughly 10 frames per second of wall time).
2. `python3 scripts/mix.py --narration vo.wav --offset 0.6 --events frames/sfx.json --cues cues.json --out mix.wav`
   (`--help` for music, ducking and targets; cue paths are relative to `cues.json`). Effects can
   come from any sound library; earshot's bank works offline. See `sound.md`.
3. `ffmpeg -framerate 30 -i frames/f%05d.jpg -i mix.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart out.mp4`
4. Measure: `ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`. Target −14 LUFS, true peak ≤ −1 dB.

## 7. Hand over

Send the MP4 with one line on what it shows. Say what you could not check (you cannot hear the
mix: name the moments most worth a listen). Offer one next cut (a 15–30 s version, another
style). Don't commit renders or scratch files to the user's project.

## Files

| File | Load when |
|---|---|
| `styles.md` | choosing or explaining a style |
| `checks.md` | reviewing stills or the final file |
| `sound.md` | narration, effects or the mix |
| `assets/starter.html` | building the page |
| `scripts/vo_lines.py`, `scripts/render_frames.cjs`, `scripts/mix.py` | the steps above |
