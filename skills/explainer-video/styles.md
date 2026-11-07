# Styles

Pick by what the content is, not by what looks impressive. Each style has a grammar: what fills
the frame, how things enter, how the camera moves, how scenes change.

| Style | Use for | Avoid for | Assets |
|---|---|---|---|
| Notebook draw-on | invented worlds, lore, a story told by hand, how-it-works sketches, anything "doodle" | real events that need proof | the project's own SVG art (strokes animate) |
| Collage desk (Vox-style) | real history, news, sourced claims, documents, quotes, numbers | invented worlds: it turns into a fake archive | real photos, scans, clippings |
| Record the app | a product or game whose screens already animate (storybooks, onboarding, flows) | apps with no motion of their own | the running app, recorded with Playwright |
| Cartoon stage | characters acting out a process; trailers | tight budgets: limbs need rigs | vector characters with joints |
| Royal chronicle / vintage sketch | lore with a "long ago" voice, biographies | playful brands | parchment, ink drawings, gold capitals |
| Kinetic type | title cards, chapter cards, one big number | whole films (tiring past ~30 s) | fonts only |

## Notebook draw-on

- One tall page (grid or ruled paper). Beats sit in a zig-zag down the page, joined by
  hand-drawn arrows. The camera follows the pen; the ending scrolls or pulls back so the whole
  story reads as one page.
- Drawings draw themselves: every stroked shape gets `pathLength=1` and a dash offset; strokes go
  in document order, each taking time in proportion to its length; fills fade in just after the
  shape's outline closes (it reads as colouring in). A pen sprite rides the current stroke.
- Handwriting (a script font) is revealed left to right at about 15 characters a second.
- Sound: a pencil scratch synthesised from the stroke schedule (band-passed noise gated by when
  the pen is down, with a writing flutter), quiet under the voice.

## Collage desk (Vox-style)

From the Y2 grammar in alchaincyf/huashu-art-motion, in short:
- Real material fills the frame. Prints and clippings appear on the cut; only items along a
  timeline slide in, tilted 5–15°, and settle flat (≈0.55 s).
- Two frame rates: camera smooth; elements on twos (12 fps), so lines, typing and highlighter
  step like hand animation.
- Black typed labels (≈13 characters a second), red ink circles that don't close, red strings
  with a dot head, a yellow highlighter swept across the line the narrator is saying.
- Hard cuts on the narration's sentence breaks; camera pushes 0.6–1.5 s, pulls ≈1 s with a long
  tail; when the camera stops, it stops. No torn-paper transitions.
- Palette: near-black, paper white, one red in two shades, an olive yellow. No pure white or
  black.
- Paper props can be generated: cloveric/claude-drawing-skill's newspaper-collage library makes
  torn newsprint, aged strips, halftone prints and a desk board with numpy + Pillow.

## Record the app

Open the app's own animated page in Playwright, hide its chrome with injected CSS, widen it for
resolution (override max-width rather than zoom, which breaks `dvh` layouts), log the time of
each interaction, and record video or screenshots. Re-record with page holds that match the
narration's sentence lengths, then place each narration sentence just after its page turn.

## Credits

The desk and collage rules summarise huashu-art-motion (MIT); the camera rig and the frame-exact
export idea follow bangtutorial/bang-motion (MIT); procedural paper comes from
cloveric/claude-drawing-skill (MIT). The licences were checked in each repo's LICENSE file on
2026-11-07; the summaries above are in our own words. Read their repos for the full grammars.
