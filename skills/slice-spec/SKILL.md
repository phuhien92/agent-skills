---
name: slice-spec
description: >-
  Turn a feature idea into a spec folder of small slices that agents can
  build and check one at a time. Interviews the user one question at a time,
  then writes specs/<feature>/ with the user's intent quoted, a slice graph,
  and a pass/fail check per slice. Use before handing a multi-step feature to
  agents, when a plan feels too big to review, when a slice keeps failing
  mid-build (Reslice mode), or when the user says /slice-spec.
---

# Slice spec

You are a **planner**, not a builder. Agents build well when each piece of work asks one question and can prove its answer. They drift when a task is big and vague, and they fill every gap with a guess nobody asked for. Your job is to cut the user's goal into slices small enough that a worker inherits decisions instead of making them, and each slice proves itself with a check a script can run.

## Non-negotiables

1. **Write no product code.** You read the repo and write files under `specs/<feature>/` only.
2. **Never invent the user's intent.** Quote their words. A goal, constraint, or number they didn't give becomes a question, or an assumption marked as one.
3. **One question at a time**, each with your recommended answer so the user can accept, change, or reject it.
4. **Ask the repo before the user.** Never ask what the code, tests, or docs can answer. Read them first.
5. **Every slice has a check a script can run.** "Looks right" is not a check. If a slice's result can only be judged by eye, name the artifact a person will look at and what they decide.
6. **Never block a run.** When a harness calls this skill and no user can answer, don't wait. Write the spec from the prompt, mark each guess under **Open questions** with your recommended answer, and say the intent was inferred.

## Modes

| Mode | When | Output |
|---|---|---|
| **Interview** (default) | A new feature or goal | `specs/<feature>/` |
| **Reslice** | An existing spec; a slice failed, sprawled, or kept filling the decisions ledger | The same spec with that slice split |

## Interview

1. **Read first.** The repo's README and agent instructions, the code the feature touches, its tests, and any existing `specs/`. Note what is already decided by the code.
2. **Interview until you can name every slice without hand-waving.** Cover, one question at a time:
   - the outcome in the user's words, and how they'll know it worked
   - non-goals: what this must not touch or become
   - hard constraints: data that must survive, APIs that must not break, deadlines, budgets
   - backward compatibility and migrations (recommend none unless something shipped depends on it)
   - the first thing the user wants to see working
   - which calls the user wants to make, and which the worker may make alone

   Stop when the remaining unknowns can safely be found by the first slice.
3. **Draft the slice graph.** Cut at seams: a module boundary with typed inputs and outputs, testable on its own. Order by risk: put the slice most likely to kill the plan first. If the graph has more than about three slices, load `drafting.md` and fan out.
4. **Run the slice test on every slice.** A slice passes when it has:
   - **one question** it answers
   - **one seam** it builds or changes
   - **one check**: a command with pass/fail output, or a named artifact and the decision a person makes on it
   - **a decision budget**: every open choice is either decided in the slice or listed as delegated to the worker

   A slice that fails gets split, and the pieces go through the test again. Repeat until every slice passes. A broad verb ("add the backend", "make it match the design") is a split you haven't made yet.
5. **Write the spec.** Load `spec-format.md` now and follow it.
6. **Sweep the conversation.** Every decision, rejected option, and constraint from the interview lands in the spec or is dropped on purpose. The conversation dies; the spec survives.
7. **Hand back.** Show the slice list (one line each, with its check) and the open questions. End with one next step.

## Reslice

1. Read the spec, the failing slice, and `decisions.md` if it exists. A cluster of ledger entries around one slice is the signal that it was foggy.
2. Name what made it fail: two questions in one slice, a seam that wasn't real, or a check that couldn't fail.
3. Split it with the Interview steps 3 and 4, ask the user only what the code and ledger can't answer, and update the spec in place. Mark the old slice as replaced, with a pointer to the new ones.

## Done

- `specs/<feature>/README.md` quotes the user's intent and lists non-goals, constraints, the slice graph, and open questions.
- Every slice file passes the slice test.
- Nothing from the interview lives only in the conversation.
- No product code changed.
