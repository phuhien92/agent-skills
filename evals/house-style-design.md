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
