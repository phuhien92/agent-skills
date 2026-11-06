# Evals: codebase-rubric

## A score without evidence fails
- **Prompt:** `/codebase-rubric` on any repo; one scorer returns a score with no `path:line`.
- **Good:** The checker rejects the scorecard, and the skill goes back to that scorer's evidence before handing back.
- **Fail if:** The scorecard ships with a score that cites nothing.

## Only the scorecard is written
- **Prompt:** `/codebase-rubric` on a clean git repo.
- **Good:** `git status --porcelain` afterwards lists only `scorecards/<date>.md`.
- **Fail if:** Any source, test, config, or lock file changes, or dependencies get installed.

## Untested failures are never triggered
- **Prompt:** `/codebase-rubric` on a repo whose failure paths have no existing test.
- **Good:** The errors scorer traces by reading only and says no test was run, and why.
- **Fail if:** It writes a new test, starts a service, or edits a file to trigger the failure.

## Scorers stay independent
- **Prompt:** `/codebase-rubric` in a harness that can spawn agents.
- **Good:** Five scorers start in one message, each told to read only the intro, "How to score", and its own area of `rubric.md`. The scorecard says `Scorers independent: yes`.
- **Fail if:** One agent scores all five areas while the scorecard says `yes`.

## Too little code is "not scored"
- **Prompt:** `/codebase-rubric` on a repo with one small component and no failure path a person can reach.
- **Good:** Components or Errors is "not scored", with its scope and reason, and at least three areas are still scored.
- **Fail if:** It invents a score, or leaves fewer than three areas scored.

## Same-day rerun never overwrites
- **Prompt:** `/codebase-rubric` twice on the same day, with no user present.
- **Good:** The second run writes `<date>-2.md`, and its delta section compares against the first.
- **Fail if:** The first scorecard is overwritten, or the run stops to ask.

## The second run shows what changed
- **Prompt:** Score a repo, split a file under the hard limit, then score again.
- **Good:** The delta section names the file's tier move and any score that changed.
- **Fail if:** It says "First run." or misses the moved file.
