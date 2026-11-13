---
name: house-style-design
description: Draw new art in a project's own visual style, as code (SVG), mockup first, and frame it as a finished design such as a premium or "ultimate" collectible card, a character sheet, a poster, or a social image. Use when the user asks to redraw, upgrade, or add a character, mascot, boss, face or mood set, card, icon set, or promo graphic that must match an existing app's or game's look; asks for a mockup or options; says "more detailed", "ultimate card", "legendary version", or "in our style"; or calls the art ugly, generic, or too similar.
compatibility: Needs Node 18+ with Playwright Chromium to render PNGs; fonts install from npm. Works without network beyond the package registry.
---

# house-style-design

New art should look like it came from the same hand as the project's existing art, only richer.
That means reading the style before drawing, drawing in code in the project's own coordinate
system, and checking the render the way a player will see it: small, on a phone.

## 1. Read the house style (before drawing anything)

Find, and note in a few lines:
- **Where art lives:** the components or files that draw characters, icons and cards
  (search for `viewBox`, `<svg`, `Art`, `Icon`, `Card`).
- **The grammar:** canvas size (for example 210×190), stroke colour and width, line caps, fill
  style (flat, gradient, halftone), palette, how faces are built, what props look like.
- **The card or layout component:** its slots (stats, banner, art window, nameplate, text area)
  and its CSS. A new design keeps that layout and upgrades its finish.
- **The rules:** the project's AGENTS.md, design guide, or design notes (a `docs/design-guide.md`
  or similar wins over your taste). Common ones: everything original, never
  imitate an existing game or franchise; one icon style; card text generated from game data.

If the request names a character, find its current drawing and keep what makes it recognisable
(colours, silhouette, signature props). If two characters could match the name, pick the one the
project treats as main and say which.

## 2. Decide what you are making

State it in one line before drawing: subject, format, size, and whether it is a concept or meant
to ship. Mechanics shown on a card (stats, effects, costs) are placeholders unless they come from
the project's data; a project that generates card text from data or needs balance runs gets a
concept card plus a note on what wiring it would take. Never edit game data unasked.

## 3. Mockup first: explore before you polish

**New character, mascot, boss or set (no house drawing to keep): show three distinct directions
first.** Before drawing, ask one question, with a recommended answer: "Which two words should it
feel like, and which existing art should it sit beside?" Then draw three rough mockups on one
contact sheet at phone size. Distinct means a different silhouette, a different base (species,
object, or shape idea), and a different personality word for each. Three colourways or poses of
one idea count as one direction. Polish only the direction the user picks; with no user present,
pick one, say why, and hand over all three. An upgrade of an existing character skips this step:
its drawing is the direction.

**After vague negative feedback** ("ugly", "generic", "not it"): don't swap the whole concept.
Ask one question naming the parts that could have failed (silhouette, face, palette, detail
level, proportions) with your best guess first, then change that part and keep the rest.
A second vague "no" on the same part is the signal to go back to new directions.

**Sets (faces, moods, eyes, icons, a family of enemies) vary in shape, not only colour.** For each
member, change at least two of: outline or silhouette, eye shape, pupil size, brow angle, mouth
shape, a signature prop. Render the set as greyscale thumbnails at about 48 px: any two that read
the same get redrawn before handover.

## 4. Draw

Load `drawing.md`. Short version:
- Work at twice the house canvas (210×190 becomes 420×380) so detail has room, and keep the
  house stroke weight in proportion (4 px at 1× becomes 6 px at 2×).
- Paint back to front: backdrop prop, cape or wings, body, clothing details, face, headgear,
  hand-held props, sparkles. Every shape gets the ink outline unless the house style says not.
- "More detail" means more *things*, each simple: trims, gems with a highlight dot, pattern
  bands, a second prop, fold lines, a backdrop object. Not thinner lines or gradients everywhere.
- Characters stay original. No known characters, logos, or real people. If the user shared
  another product's art as the model, run `reference-originality` first and draw from its brief.

## 5. Frame it

Start from `assets/card.html` for cards. It has a foil frame, a sunburst art window with a holo
sheen, a ribbon, stat badges, a nameplate, and a text panel with moves and a highlighted
"ultimate" move. Map its slots onto the house card's slots and recolour it from the palette.
Minimum sizes at 750×1050: name 60 px, move names 22 px, body text 20 px.

## 6. Render and check

Copy `assets/card.html` to a work folder outside the user's repo, run
`npm i @fontsource/anton @fontsource/oswald @fontsource/source-serif-4` there, then
`node <skill>/scripts/render.cjs card.html out/`. It writes one PNG per `.card` at 2× (transparent
corners) and `sheet.png`, and fails if a font or image doesn't load. Look at the contact sheet at a third of full size (phone size). Then check:
- [ ] The figure fills the art window; nothing important hides behind the nameplate or ribbon.
- [ ] The face reads at phone size; no prop or cloud covers the mouth or eyes.
- [ ] Limbs and props make sense (hands hold things; nothing crosses the face).
- [ ] No text overflows its box or wraps where it shouldn't; nameplate line on one line.
- [ ] Stroke weight matches the house art when shown next to an existing character.
- [ ] Nothing imitates an existing franchise; icons match the house icon style.
- [ ] Set members tell apart in greyscale at thumbnail size (about 48 px).
- [ ] New work: the three directions differ in silhouette and base, not only colour.
Expect two or three passes. Fix by moving or resizing shapes, not by shrinking text.

## 7. Hand over

Send the PNGs (one per design, or the contact sheet of directions) with one line each on what
changed from the original or what each direction is going for. Say which
parts are placeholders (stats, moves) and what it would take to ship them in the project (which
files, which checks). Offer to wire it in; don't do it unasked. Keep the source HTML or SVG so
the user can tweak it.

## Files

| File | Load when |
|---|---|
| `drawing.md` | drawing or upgrading a character |
| `assets/card.html` | framing a card |
| `scripts/render.cjs` | rendering PNGs and the contact sheet |
