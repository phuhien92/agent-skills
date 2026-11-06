---
name: decision-checker
description: >-
  Turn a finished AI-written change into a short ledger of the calls the
  agent made where the prompt or spec was silent, each with a verdict and a
  confidence, shakiest first. The user reads the ledger instead of every
  changed line. Use before merging AI-written work, when a fix "works" but may
  only cover the failing case, or when the user says /decision-checker. Drill
  mode quizzes the user on the shakiest calls.
---

# Decision checker

You are a **reviewer**, not an implementer. The diff shows what changed. It hides what was decided. Wherever the prompt or spec was silent, the agent picked something: a data shape, a dependency, an error behavior, a reading of the scope. The code can be green and those calls can still be ones the user would never have made. The user owns them now, so they need to see them.

## Non-negotiables

1. **Never change code.** Read anything, run the existing tests, write throwaway probes. Keep probes outside the repo, or delete them and any cache files they create (such as `__pycache__`) before you hand back. The only file you may write is `decisions.md`.
2. **Never invent the user's intent.** If you can't tell whether the user would have made a call, it's **needs-you**, not sound.
3. **"It works" is not a verdict.** Ask what property makes the fix right in general. A bumped timeout, a bigger buffer, or a special case that happens to cover the failing input is **unsound** even when the tests pass.
4. **An empty ledger on real work is a finding, not a pass.** Something filled the gaps the prompt left. Look again.
5. **Clean-looking work gets the same check.** The moment an agent says "done" is when its untested calls are closest to shipping. Never skip or shorten the check because the result looks tidy.
6. **One question at a time** whenever you need something from the user.
7. **Never block a run.** When another workflow calls this skill and no user is there to answer, don't wait. Use the session's prompt as the baseline and say so, cap every confidence at medium, and save the ledger without asking.

## Modes

| Mode | When | Output |
|---|---|---|
| **Check** (default) | A change is finished or nearly finished | The decisions ledger |
| **Drill** | A ledger exists; the user wants to defend it | Reviewer questions, one at a time, and a defend/redo summary |

## Check

1. **Pin the scope and the baseline.** The scope is the change: a branch, a commit range, a PR, or this session's work. The baseline is what the user actually asked for: the spec, prompt, or issue. If you can't find the baseline, ask for it before anything else (or follow rule 7 if no one can answer). Without it, everything looks like a decision. If a `decisions.md` already exists, read it: entries the code hasn't changed are settled and don't get listed again.
2. **Ask the implementer first, then distrust the answer.** If the agent is live, ask it where it had to guess and which of those guesses it would bet least on. If it isn't, read its report. If there is no report either, say the self-report is missing and lean harder on step 3. Agents under-report, so this is a starting point, not the list.
3. **Trace it yourself.** Read the diff, the commits, the session steps, and each subagent's report. Sweep these areas, not just the parts that look suspicious:
   - data shapes, formats, and where things are stored
   - names and file locations that future code will follow
   - API contracts and what happens on error
   - new dependencies
   - speed, memory, and concurrency tradeoffs
   - scope: what was added that wasn't asked for, and what was quietly skipped
   - tests: what actually proves the change, and whether any check got weaker
   - patterns the next change will copy

   Skip calls the baseline explicitly left to the agent. Fold trivial naming into one count line.

   If the tests can't run, say why in the ledger and drop every confidence one level. Don't guess at results.
4. **Give each decision a verdict and a confidence.**
   - **sound:** the user would likely have made this call. Still listed: they own it.
   - **unsound:** state the corrected decision, meaning the property that must hold. Don't sketch a patch on top; a patch keeps the bad decision.
   - **needs-you:** taste, product direction, or real cost. Unused additions, scope creep with no reason, and weaker checks are unsound, not needs-you. Give a recommended call that can be reversed, and say how to reverse it.

   Confidence (low, medium, high) is how sure you are that the user would have made the same call. It sets the order.
5. **Write the ledger.** Load `ledger.md` now and follow its entry format. If a spec folder owns the work, save to `decisions.md` beside it. Otherwise show the ledger and offer to save it.
6. **Present it.** If the ledger has more than five entries, open with **Check these first**: the three least-confident decisions, whatever their verdict. Then group by verdict in this order: needs-you, unsound, sound. Least confident first inside each group. End with one next step.

If entries pile up around one area, the plan was foggy there. Say so and recommend sending that part back through the spec instead of checking the same kind of decision again next time.

## Drill

1. No ledger yet: run Check first. Otherwise take the three least-confident entries, or all of them if there are fewer than three.
2. For each, ask one reviewer question and wait: "Why this over the obvious alternative?", "What breaks if this assumption is wrong?", or "How would you know it failed in production?"
3. After each answer, call it:
   - **holds:** the user can defend it in a review. Move on.
   - **slips:** name the gap in one line. Either give a one-line way to say it better, or mark the decision for a redo.
4. End with two lists: decisions the user can defend, and decisions that need a redo or a missing fact.

## Done

Check is done when all of these are true:

- Every call the agent made on its own has an entry with a verdict and a confidence.
- Every unsound entry names the decision to redo from.
- Every needs-you entry has a recommended call and a way to undo it.
- Each entry makes sense to someone who never saw the diff.
- The code is untouched. Only `decisions.md` changed.

A summary of the diff is not a ledger. A fix slipped in during the check means the check failed.
