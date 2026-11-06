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
- **Good:** The five-slice run loads `drafting.md` and spawns three drafters with different lenses. The one-slice run drafts alone.
- **Fail if:** The small fix fans out, or the big feature never does.

## Reslice from the ledger
- **Prompt:** Reslice mode on a spec whose `decisions.md` has five entries for slice 02.
- **Good:** Names why 02 was foggy, splits it, marks 02 as replaced with pointers, and updates the graph and Next agent prompt.
- **Fail if:** Deletes the old slice, or patches 02 without splitting it.
