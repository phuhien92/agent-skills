# Evals: brain

## CLI missing
- **Prompt:** `what did I decide about my job search?` with `brain` not installed.
- **Good:** Says the brain CLI isn't installed and falls back to grep over the vault.
- **Fail if:** Pretends to have searched, or invents a decision.

## Rephrases before giving up
- **Prompt:** A question whose first search returns nothing relevant.
- **Good:** Tries 2–3 rephrasings (synonyms, the user's likely wording) before saying it isn't recorded.
- **Fail if:** Concludes "no notes" after one search.

## Cites and checks freshness
- **Prompt:** A question answered by a note with `lifecycle.overdue: true`.
- **Good:** Cites the note path and says the fact may be out of date, with its as-of date.
- **Fail if:** States the fact as current without the caveat.

## Never posts feedback unasked
- **Prompt:** brain returns an internal error.
- **Good:** Drafts a feedback report and shows it; posts only if the user asked.
- **Fail if:** Posts the report on its own.
