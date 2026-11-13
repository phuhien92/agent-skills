# Evals: house-style-design

## Reads the house style first
- **Prompt:** "Redraw the king as an ultimate card" in a repo with an `Art.tsx`, a `Card.tsx` and an AGENTS.md.
- **Good:** Reads the art components, card layout and rules before drawing; the new art uses the same stroke colour, weight (scaled 2×), palette and face construction; the card keeps the house slots.
- **Fail if:** Draws in a generic style, ignores the existing card layout, or misses an AGENTS.md rule (for example the icon style).

## Picks the right character and says so
- **Prompt:** "Doodle King" in a project with two king drawings, where the story and the throne scene use one of them.
- **Good:** Picks the king the story and scenes use (the signal: where the drawing is referenced), keeps its silhouette, colours and signature prop, and states the choice in one line.
- **Fail if:** Invents a new king, or picks one silently.

## Placeholders are labelled
- **Prompt:** An ultimate card in a project whose card text is generated from game data and needs balance runs.
- **Good:** Says the stats and moves are placeholders, names the files and checks needed to ship them, and offers to wire it in.
- **Fail if:** Edits game data unasked, or presents invented stats as real.

## Checks at phone size and fixes by moving shapes
- **Prompt:** A first render where a cloud covers the character's mouth and the name wraps.
- **Good:** Spots both on the contact sheet, moves the cloud and shortens the plate line, re-renders.
- **Fail if:** Hands over the first render, or fixes overflow by shrinking text below the minimum sizes.

## Stays original
- **Prompt:** "Make it look like a famous trading card game's legendary card."
- **Good:** Keeps the house look and a generic premium finish (foil, burst, ribbon); no franchise names, logos, layouts or characters.
- **Fail if:** Recreates a specific existing game's card frame, branding or characters.

## A new mascot gets three distinct directions
- **Prompt:** "Design a guide mascot for the game." No existing drawing of it in the repo.
- **Good:** Asks one question (two feel-words, and which existing art it sits beside) with a recommended answer, then shows three rough directions on one contact sheet that differ in silhouette, base (species or object) and personality word. Polishes only the one the user picks.
- **Fail if:** Ships one polished design, or three recolours or poses of one idea.

## A vague rejection gets a pinpointing question
- **Prompt:** After the first round the user says "ugly, too generic."
- **Good:** Asks which part failed (silhouette, face, palette, detail level, proportions) with its best guess first, then changes that part and keeps the rest.
- **Fail if:** Swaps the whole concept without asking, or asks several questions at once.

## A face set differs in shape
- **Prompt:** "Give each card mood faces." Later the user says "they look so similar."
- **Good:** Each mood changes at least two of outline, eye shape, pupil size, brow angle and mouth shape, and the handover includes greyscale thumbnails at about 48 px that tell every face apart.
- **Fail if:** Changes only colours or tiny details, or never checks the set in greyscale.
