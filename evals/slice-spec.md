# Evals: slice-spec

## One question at a time, with a recommendation
- **Prompt:** `/slice-spec` then "add CSV export to the reports page."
- **Good:** Reads the reports code first, then asks one question with a recommended answer, and waits.
- **Fail if:** Asks several questions in one message, or asks something the code already answers (such as which framework the page uses).

## Intent is quoted, not widened
- **Prompt:** Interview where the user says "export the current table as CSV, nothing fancy."
- **Good:** README Intent quotes those words. "Nothing fancy" shows up as a non-goal (no formats beyond CSV, no scheduling).
- **Fail if:** The intent becomes a broader goal like "a flexible export system", or adds PDF or Excel.

## Every slice has a runnable check
- **Prompt:** Any interview that ends with three or more slices.
- **Good:** Each slice file has a Check that is a command with pass and fail meaning, or a named artifact and the decision a person makes on it.
- **Fail if:** Any check reads "verify it works", "looks right", or is missing.

## Broad slices get split
- **Prompt:** A draft graph contains a slice named "build the backend."
- **Good:** The slice test fails it and splits it until each piece has one question and one seam.
- **Fail if:** "Build the backend" survives as one slice.

## No product code
- **Prompt:** `/slice-spec` on a real repo, full interview.
- **Good:** Only files under `specs/<feature>/` are created or changed.
- **Fail if:** Any source, test, or config file changes, or `decisions.md` is written.

## No user present still finishes
- **Prompt:** A harness calls the skill with a one-line goal and nobody answering.
- **Good:** Writes the spec, says the intent was inferred, and lists each guess under Open questions with a recommended answer.
- **Fail if:** Stops to ask a question and waits.

## Big features fan out, small ones don't
- **Prompt:** Two runs: a five-slice feature and a one-slice fix.
- **Good:** The five-slice run loads `drafting.md` and spawns three drafters with different lenses. With no way to spawn agents, it drafts the three lenses in sequence and says so under Decided in planning. The one-slice run drafts alone.
- **Fail if:** The small fix fans out, or the big feature never does.

## Reslice from the ledger
- **Prompt:** Reslice mode on a spec whose `decisions.md` has five entries for slice 02.
- **Good:** Names why 02 was foggy, splits it, marks 02 as replaced with pointers, and updates the graph and Next agent prompt.
- **Fail if:** Deletes the old slice, or patches 02 without splitting it.

## An existing spec is never overwritten
- **Prompt:** `/slice-spec` for a feature whose `specs/<feature>/` already exists, with no user present.
- **Good:** Writes `specs/<feature>-2/` and says why. With a user present, offers Reslice or asks for a new name.
- **Fail if:** Any file in the existing spec changes.

## No invented numbers
- **Prompt:** Interview for "make search faster" where the user never gives a target.
- **Good:** Asks for the target. With no user present, lists it under Open questions with a recommended number marked as a guess.
- **Fail if:** The spec states a latency or size budget the user never gave as if it were agreed.

## Every slice has Decided and Delegated sections
- **Prompt:** Any interview that ends with two or more slices.
- **Good:** Each slice file has both sections, even if one says "none."
- **Fail if:** A slice leaves an open choice in neither section.

## Rejected options are recorded
- **Prompt:** Interview where the user turns down the recommended answer ("no, don't use SQLite").
- **Good:** "Decided in planning" records the choice, why, and that SQLite was turned down.
- **Fail if:** The rejected option appears only in the conversation.

## A big goal is planned as several PRs
- **Prompt:** An interview whose drafted slices estimate about 1,400 new lines of product code in total.
- **Good:** The slice graph has a PR column with two or more PRs, each shippable on its own, and each PR's slices estimate under 800 new lines.
- **Fail if:** One PR holds every slice, or the PR column is missing.

## An oversized slice gets a Reslice suggestion, not a reslice
- **Prompt:** A worker finishes a slice and `diff_size.py . HEAD~1..HEAD` reports 950 new lines.
- **Good:** The handback says the slice is over soft (800) and suggests Reslice; the spec is unchanged until the person decides.
- **Fail if:** The size goes unmentioned, or the spec or commits are changed without the person deciding.

## A branch over soft gets a follow-up PR suggestion
- **Prompt:** Mid-build, `diff_size.py . main..HEAD` reports 870 new lines for the whole range with two slices left.
- **Good:** Suggests moving the remaining slices to a follow-up PR. With a person present, waits for their call; with no one present, keeps building and records the suggestion in the handback and under Open questions.
- **Fail if:** Moves the slices or opens a second PR on its own, says nothing, or stops an unattended run to wait.

## The worker measures the running total itself
- **Prompt:** A spec written by slice-spec; a worker finishes slice 03 of 05.
- **Good:** The spec's README names the script's real path and the Base; the worker runs that command after the commit and reports both this slice's row and the whole-range total.
- **Fail if:** The README has a placeholder path or no Base, or the worker reports only `HEAD~1..HEAD`.
