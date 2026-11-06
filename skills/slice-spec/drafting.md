# Parallel drafting

Loaded by `slice-spec` at step 3 of Interview when your first draft has four or more slices. A single planner has blind spots. Drafters with different priorities, working apart, cover each other: a cut they all reach is trustworthy, and a cut they argue about deserves the most thought.

## Fan out

Spawn three subagents in one message, each with fresh context. Give each the **same brief** and nothing else: the quoted intent, non-goals, constraints, and the repo facts you gathered. Never show one draft to another drafter.

Give each a different lens:

- **Lean:** what is the least work that still delivers the intent? Every slice must justify itself.
- **Fail fast:** which assumption, if wrong, sinks the plan? Test that one first.
- **Seams:** where do the module boundaries want to be? Accept extra slices to get boundaries that test cleanly.

Swap a lens for one the feature needs (data migration safety, performance, visual fidelity). Each drafter gets a lens no other drafter has. If more than one model family is available, mix them.

Each drafter returns a slice graph in the README table format from `spec-format.md`, plus the risks it saw. Drafters write no files.

## Merge

Build the plan yourself. Don't pick a winner.

1. Take the strongest cut, then add every seam, risk, and constraint any single drafter caught.
2. Where drafts disagree, choose the better-argued option and record the other under **Decided in planning** with why it lost.
3. Run the slice test from `SKILL.md` step 4 on the merged graph.

## When you can't fan out

If you can't spawn a fresh agent in this session, write the three drafts yourself in sequence, one lens at a time, before reading them together. Keep the drafts outside the repo (they are scratch, not spec), and say in the spec's **Decided in planning** that the drafts were not independent.
