# Decisions ledger format

Loaded by `decision-checker` at step 5 of Check. One entry per decision.

Each later run appends its entries under a heading `# Check N: <scope>` (N counts runs; the first run may skip its heading). `tools/skill_metrics.py` counts runs from these headings.

## Entry

```
### <Headline: the decision in one line>

- **When:** commit, pass, or step where it landed
- **Slice:** NN, when a spec owns the work (lets Reslice spot clusters)
- **What happens now:** a short scenario in plain words. The event that
  triggers it, what the code does today, and what the obvious alternative
  would have done. Define any term the build invented the first time you use it.
  When the decision is about order, timing, or control flow, add a few lines
  of pseudocode.
- **The gap:** what the prompt or spec didn't say, which forced the call
- **Reach:** what future work this makes easier or harder
- **Verdict:** sound / unsound / needs-you, with a one-line reason
  - unsound: **Redo from:** the property that must hold
  - needs-you: **Recommended call:** ... **To reverse:** ...
- **Confidence:** low / medium / high that the user would have made this call
```

## The standard: it reads on its own

Someone who never saw the session, the spec, or the diff should be able to judge the decision from the entry alone. A headline isn't an entry.

**Too thin:**

> Retries are capped at 3 with no backoff.

**Reads on its own:**

> **Failed webhook sends are retried 3 times, back to back, then dropped.**
>
> - **What happens now:** a partner's endpoint returns a 503 during a deploy. The sender retries three times within about a second, all three fail, and the event is gone. The obvious alternative waits longer between attempts (for example 1s, 10s, 60s) and parks events that still fail in a queue someone can replay.
> - **The gap:** the spec said "retry failed sends" without saying how many times, how far apart, or what happens after the last try.
> - **Reach:** every integration built on this sender inherits silent drops during short outages.
> - **Verdict:** needs-you. Dropping events is a product call. **Recommended call:** retry with backoff over about a minute, then park in a dead-letter table. **To reverse:** set the retry policy back to `{ attempts: 3, delay: 0 }`.
> - **Confidence:** low.

This example is a format illustration only. Never copy its facts into a real ledger.

## Rules

- **Settled stays settled.** A decision already in the ledger isn't re-listed on later checks unless the code changed it.
- **Rewrites keep the scenario.** When entries are merged or cleaned up, each one keeps its full "What happens now". A ledger cut back to headlines is a broken ledger, even if nothing factual was lost.
- **Decisions only.** No test logs or review chatter. Those live in the PR.
