# Checks

Run these on a contact sheet of stills (one per beat plus mid-transition), then on the final file.
Each line is a failure that has actually happened.

## Picture

- [ ] Every label sits where it was placed. A label that types in from empty must be measured with
      its full text, or re-placing after fonts load shifts it right by half its width.
- [ ] Highlights and underlines sit on their words (measured from text spans, after fonts load).
- [ ] No text is cut by the frame edge at the zoom used for that beat; nothing important within
      120 px of an edge.
- [ ] Beats don't overlap: the next station's elements don't show inside this beat's frame.
- [ ] Text on a dark panel is readable (switch to a light ink with an outline).
- [ ] Each beat's material fills at least 60% of the frame width.
- [ ] Transitions: no half-faded slides; cuts land on sentence breaks; camera moves end before
      new text appears.
- [ ] The end card fits the frame (rotation adds width) and the page or desk extends past the
      frame at the final zoom.

## Timing

- [ ] Beat k starts within 0.2 s of narration sentence k. Measure motion onset by frame
      differencing around each logged turn, not by eye.
- [ ] The last sentence ends before the end card arrives.

## Sound

- [ ] Integrated loudness −14 LUFS (±1) on the final MP4; true peak ≤ −1 dB.
- [ ] Measure mono stems carefully: duplicating mono into two channels reads 3 dB louder in ffmpeg's
      ebur128 than pyloudnorm's mono figure. Don't add gain to "fix" a mono reading.
- [ ] The voice sits 12–16 dB above music plus effects while speaking.
- [ ] Hits (stamps, impacts) are limited, not clipped.
- [ ] Say plainly that you could not listen, and name the moments most worth checking.

## Hygiene

- [ ] No temporary capture pages or renders left in the user's project.
- [ ] Third-party repos and downloads were cloned into their own empty folders and run with
      `python -I`.
