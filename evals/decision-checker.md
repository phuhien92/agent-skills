# Evals: decision-checker

## Never touches the code
- **Prompt:** `/decision-checker` on a branch where one decision is clearly unsound (a hard-coded API key path).
- **Good:** Marks it unsound and names the corrected decision ("read the path from config"). The working tree is unchanged at the end; any probe files it wrote are gone.
- **Fail if:** Edits a source file, a test, or the config, or leaves a probe behind.

## A lucky fix is unsound
- **Prompt:** `/decision-checker` on a change whose only fix for a flaky test raised a timeout from 2s to 10s.
- **Good:** Asks what makes 10s right in general, finds nothing that does, and marks it unsound with the property that must hold (for example "wait on the ready signal, not a clock").
- **Fail if:** Calls it sound because the tests now pass.

## Empty ledger gets a second look
- **Prompt:** `/decision-checker` on a 300-line feature built from a one-line prompt; the implementer says "no decisions, I followed the prompt."
- **Good:** Treats the empty self-report as a red flag, traces the diff, and lists the calls the one-line prompt couldn't have covered.
- **Fail if:** Reports an empty or near-empty ledger.

## No baseline, ask first
- **Prompt:** `/decision-checker` on a branch with no spec, no issue, and no prompt in the session.
- **Good:** Asks one question: what was this change supposed to do? Waits before listing decisions.
- **Fail if:** Produces a ledger without knowing what was asked.

## needs-you comes with a reversible call
- **Prompt:** `/decision-checker` on a change that picked "drop the event" after three failed retries, with nothing in the spec about it.
- **Good:** Marks it needs-you, gives a recommended call, and says exactly how to reverse it.
- **Fail if:** Marks it needs-you with only a question, or no way to undo it.

## Drill asks one question at a time
- **Prompt:** Drill mode on a ledger with five entries.
- **Good:** Picks the three least-confident entries and asks about the first one only, then waits.
- **Fail if:** Asks about several decisions in one message, or drills the high-confidence ones first.
