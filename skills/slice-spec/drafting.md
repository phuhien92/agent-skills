# Parallel drafting

Loaded by `slice-spec` at step 3 of Interview when the slice graph has more than about three slices. One drafter misses cuts that a differently minded drafter finds. Where independent drafts agree, the cut is solid; where they split is where to think hardest.

## Fan out

Spawn three subagents in one message, each with fresh context. Give each the **same brief** and nothing else: the quoted intent, non-goals, constraints, and the repo facts you gathered. Never show one draft to another drafter.

Give each a different lens:

- **Fewest slices:** the shortest path that still ships. Merge slices and question every one.
- **Riskiest first:** order so the plan fails fast if an assumption is wrong.
- **Cleanest seams:** sharpen module boundaries and testability, even at the cost of more slices.

Swap a lens for one the feature needs (data migration safety, performance, visual fidelity) but never run the same lens twice. If more than one model family is available, mix them.

Each drafter returns a slice graph in the README table format from `spec-format.md`, plus the risks it saw. Drafters write no files.

## Merge

Build the plan yourself. Don't pick a winner.

1. Take the strongest cut, then add every seam, risk, and constraint any single drafter caught.
2. Where drafts disagree, choose the better-argued option and record the other under **Decided in planning** with why it lost.
3. Run the slice test from `SKILL.md` step 4 on the merged graph.

## When you can't fan out

With no subagent tool, write the three drafts yourself in sequence, one lens at a time, before reading them together. Say in the spec that the drafts were not independent.
