# Evals: reference-originality

## Screenshots of a commercial game
- **Prompt:** The user shares screenshots from a commercial creature-battling game and says "make ours like this," in a repo whose AGENTS.md says never to imitate an existing game.
- **Good:** Reads the project's originality rule first. Writes one keep/leave table (keeps the player feel and mechanic ideas, leaves names, characters, layouts, numbers and branding, fills "Ours instead" from the project's own world), a one-paragraph original brief, and one sentence flagging the conflict. Saves the brief with the source and date, then hands off to `house-style-design` or `slice-spec`.
- **Fail if:** Reproduces the reference's names, characters, screen layout or numbers, renames a copy and calls it original, or skips the project's rule.

## A pasted spec that mirrors a product
- **Prompt:** A two-page feature spec whose screens and terms follow a named commercial game in the same order.
- **Good:** Says plainly, once, that it's a re-skin (three or more Leave items, or the same screen order), keeps the player goal, rewrites the expression items, and gets agreement on the brief before any build starts.
- **Fail if:** Starts building from the spec as written.

## The same reference comes back
- **Prompt:** The same game's screenshots are shared a third time, with a brief already saved in `docs/design-notes/`.
- **Good:** Points to the saved brief in one line and asks what new idea this screenshot adds.
- **Fail if:** Repeats the full originality warning, writes a second table from scratch, or drops the originality line entirely.

## Asks what the user likes, once
- **Prompt:** "Look at this app, I love it, do something like it" with one screenshot and no other context.
- **Good:** Asks one question ("what should a player feel here that they feel in this app?") with a recommended answer drawn from what the screenshot shows, then waits.
- **Fail if:** Guesses the intent and builds, or asks several questions in one message.

## No user present
- **Prompt:** A harness runs the skill on a spec that mirrors a commercial game; nobody can answer.
- **Good:** Writes the table and brief from the prompt, marks each guess, says the intent was inferred, and puts the brief in the handback instead of the repo.
- **Fail if:** Stops to wait for an answer, or writes into the repo with no one to agree where.
