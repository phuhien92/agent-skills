# Drawing in a house style, with more detail

## Set up

- Copy the house canvas and double it: `viewBox="0 0 420 380"` for a 210×190 house box.
- One `<g>` carries the house stroke: `stroke="#1b1b1f" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"`.
  Inner details use 3–4 px; sparkles 2.5 px.
- Use the house palette by name. Add at most two new colours, both from the same family.
- Write each part as its own commented block so the next pass can move it.

## Layer order (back to front)

1. Backdrop object that tells you who it is: a throne back, a halo with rays, a castle, a temple.
2. Big soft shapes behind the body: cape, robe, wings, cloud.
3. Body in the house shape (for stationery characters: the pencil, crayon, marker silhouette).
4. Clothing over the body: collar or mantle, sash, chain, wrapper pattern band.
5. Arms (simple curves ending in round hands), then whatever the hands hold.
6. Face: cheeks (soft ellipses, no stroke), brows, eyes with a white highlight dot, nose, mouth.
   Beards and mustaches go over the mouth area but never hide the eyes.
7. Headgear: crown, eraser cap, hat, with gems or rivets.
8. Floating extras: sparkles, stars, a small orbiting prop.

## Detail that reads

| Kind | Example | Why it works |
|---|---|---|
| Trim | ermine hem with black tail marks, gold edge on a throne | adds richness without new forms |
| Highlights | a white dot on gems, eyes and orbs; one light stroke down a body | reads as shine at tiny size |
| Pattern band | zigzag wrapper stripes, ruled lines on paper wings | gives a surface material |
| Second prop | sceptre and orb, quill and glowing tip | tells the story of the character |
| Fold lines | 2–4 darker strokes on a cape | shape without shading |
| Material cue | hexagon facets on a pencil (light, mid, dark stripe), ridges on a metal band | makes the object specific |

Avoid: gradients on every shape (one glow behind the figure is enough), hairline strokes that
vanish at phone size, details smaller than ~6 px at 2×, and symmetric stiffness (tilt the head or
body 2–4°, give props an angle).

## Common fixes

- Wings or arms that look like crossed sticks: make wings a fan of 3 rounded shapes from one
  pivot, and drop the arms below them.
- A face hidden by a scarf, beard or cloud: move the cover 20–30 px down; a smile must show.
- The figure lost behind the nameplate: crop the `viewBox` tighter (for example `30 0 360 380`)
  rather than shrinking the figure.
- A busy backdrop fighting the figure: lower its contrast (one darker tone of the burst colours).

## Upgrading an existing character

Keep the silhouette, the main colours, and the one signature prop. Then add, in this order, until
it feels "ultimate": a backdrop object, a second prop, trims, highlights, sparkles. Show the old
and new side by side once, so the user can see it's the same character.
