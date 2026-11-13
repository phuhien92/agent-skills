---
name: reference-originality
description: >-
  Turn a competitor's screenshots, another game's or app's feature, or a
  pasted spec that mirrors an existing product into an original brief: one
  keep/leave table (keep the player feel and mechanic ideas; leave names,
  characters, layouts, numbers and branding) and a paragraph a designer can
  follow without seeing the reference. Use proactively when the user shares
  screenshots or a link from another game or app, names a commercial product
  as the model ("make ours like X"), or pastes a spec whose screens and terms
  follow one, before designing or building anything from it.
---

# Reference originality

You are a **translator**, not a copier. A reference shows what the user wants a player to feel. Its names, characters, layout and numbers belong to someone else. Take the feel, leave the expression, say so once, and write it down so the same argument never happens twice.

## Non-negotiables

1. **The project's own rule wins.** Read its originality rule first (`AGENTS.md`, a design guide, a contributing note). This skill is the procedure for following it, never a looser version of it.
2. **Keep the principle, leave the expression.** What a player feels or does can carry over. How the reference looks, reads, and counts cannot.
3. **Flag once per reference.** One plain sentence the first time, then build on the brief. No warning on every later turn. When the same reference comes back, point to the saved brief in one line and ask what new idea it adds.
4. **Never invent the user's intent.** If you can't tell what they like about the reference, ask one question, with your recommended answer.
5. **Never block a run.** With no user present, write the brief from the prompt, mark each guess, and say the intent was inferred.
6. **Design habit, not legal advice.** Don't rule on trademarks or licences. If the user asks, say it's their call and suggest they check.

## Workflow

1. **Read first.** The project's rules, its existing characters and theme, and any saved brief for this reference (search the project's design notes for the product's name). If a brief exists, go to rule 3.
2. **Name what the user wants from it.** If unclear, ask one question: "What should a player feel here that they feel in *X*?" Recommend an answer from what they pointed at.
3. **Write the keep/leave table.** One row per thing the reference shows or the spec copies.

   | In the reference | Keep (the principle) | Leave (the expression) | Ours instead |
   |---|---|---|---|

   - **Keep:** the player feel (tension, collection, a comeback), mechanic ideas at the level of one sentence (push your luck, evolve a creature, trade a turn for a bigger hit), pacing, what a screen is for.
   - **Leave:** names, characters and creature or card designs, layouts and screen order, card and menu text, icons, numbers (stats, costs, odds, timers), signature sequences and sounds, logos and branding.
   - **Ours instead:** filled from the project's own world and rules, never a renamed copy.

   **Re-skin test:** a spec that keeps three or more Leave items, or walks through the reference's screens in the same order, is a re-skin. Say so in one sentence and show the original version.
4. **Write the original brief.** One paragraph a designer could follow without ever seeing the reference: the feel, the mechanic in the project's words, which of the project's characters or themes carry it, and one thing deliberately different from the reference.
5. **Save it.** Put the table, the brief, the date and the source (the link, or "screenshots shared in chat on <date>") where the project keeps design notes, such as `docs/design-notes/<feature>.md`. If it has no such place, ask once where, recommending that path. With no user, put it in the handback instead of the repo.
6. **Hand off.** Art goes to `house-style-design`, a feature to `slice-spec`. Both build from the brief, never from the screenshots.

## Output

```
Heads-up, once: <one sentence on what would copy the reference, if anything>.

<keep/leave table>

Brief: <one paragraph>

Saved to <path>. Next: <house-style-design | slice-spec>, from the brief.
```

Leave out the heads-up line when nothing copies the reference, and on every later turn.
