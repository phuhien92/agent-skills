# Sound

## Narration

- Text to speech through a connected tool costs credits: preflight the cost, tell the user the
  price and their balance, and wait for a yes. One take of the whole script is cheaper
  and more consistent than one call per line.
- If the sandbox can't download the result (blocked host), give the user the link and ask them to
  attach the file, or to allow the domain.
- Never estimate sentence times. `scripts/vo_lines.py` finds them from the pauses.
- For page-turn styles, either re-time the picture to the narration (preferred), or slice the
  narration at mid-pause cut points and place each sentence just after its beat.

## Effects

- The starter logs these kinds: `tap`, `slide`, `cut`, `move`, `type:d`, `pen:d`, `marker:d`,
  `draw:d`, `write:d` (`d` is a duration in seconds). Add your own with `sfx(t, 'kind')`.
- Map kinds to sounds in a cues file (paths relative to it):
  `{"slide": ["snd/slide1.wav", -15], "type": ["snd/key.wav", -27, {"rate": 13}], "pen": ["snd/pen.wav", -27], "tap": ["snd/tap.wav", -22]}`.
  With `rate`, the sound repeats across the duration (typing); without it, it is trimmed to it.
- earshot (github.com/Leonxlnx/earshot) renders a large code-made bank offline:
  `python -m earshot sfx list`, then `sfx render <id> -o file.wav`. Useful ids: `swipe/paper`,
  `typing_key/light`, `knock/desk`, `pro_sub_drop/soft`, `cut_hit/rumble`, `pro_pop_in/round`,
  `logo_sting/soft_bloom`, `pluck/kalimba_soft --pitch C5`. Its listening tools need model
  downloads that sandboxes often block.
- A pencil scratch is better synthesised than sampled: band-pass noise (1.8–7 kHz plus a little
  300–1200 Hz grit), gated by the pen-down intervals, with a 7–8 Hz flutter for handwriting. The
  starter exposes those intervals as `FILM.STROKES` and the renderer saves them to
  `strokes.json`; `mix.py` doesn't synthesise the scratch, so write a few lines of numpy for it
  and pass the result as `--music` or mix it in.

## Music

- Keep it under the voice: a soft pad that changes chord twice per beat, a few plucked notes on
  bright beats, low-passed and sparse on dark ones. Duck it 8 dB while the voice speaks.
- If the project has rules about sound (for example "synthesised only, no audio files" in the
  product), they apply to the product, not to a promo clip; say which you followed.

## Targets

| Thing | Target |
|---|---|
| Final MP4 | −14 LUFS integrated, true peak ≤ −1 dB |
| Voice vs music+effects while speaking | voice 12–16 dB louder |
| Mono master before duplicating to stereo | −17 LUFS (reads −14 once duplicated) |
