# Scorecard template

Loaded by `codebase-rubric` when writing the scorecard. Copy the block below into `scorecards/<YYYY-MM-DD>.md` in the target repo (or `<date>-2.md` if that exists), and fill every `<...>`. Keep the HTML comment markers exactly as written: `check_scorecard.py` and `delta.py` read the tables between them. Run `check_scorecard.py` on the file before handing it back.

Rules the checker enforces:

- **Meta** has every key. `Rubric approved` and `Scorers independent` are `yes` or `no`.
- **Scores** has exactly five rows, one per area, in this order: Architecture, Modularity, Abstraction, Components, Errors.
- A **numeric score** is 1 to 5, has a Sample of the form `N of M`, and its Evidence holds at least one `` `path:line` `` or `` `path:start-end` ``.
- **Not scored** needs a Scope and a reason in Evidence. Sample is `-`.
- **Error trace** has at least two hops, each starting with `` `path:line` ``, unless Errors is not scored.

````markdown
# Codebase scorecard: <repo name>

<!-- meta:start -->
| Key | Value |
|---|---|
| Repo | <owner/name or path> |
| Commit | <short sha> |
| Date | <YYYY-MM-DD> |
| Rubric approved | <yes or no> |
| Scorers independent | <yes or no> |
<!-- meta:end -->

## Size

<!-- size:start -->
| File | Lines | Tier |
|---|---|---|
<rows from size_report.py>
<!-- size:end -->

Skipped: <skip counts from size_report.py>

## Scores

<!-- scores:start -->
| Area | Score | Scope | Sample | Evidence |
|---|---|---|---|---|
| Architecture | <1-5 or not scored> | <part of the repo scored> | <N of M> | <`path:line` and a short reason> |
| Modularity | ... | ... | ... | ... |
| Abstraction | ... | ... | ... | ... |
| Components | ... | ... | ... | ... |
| Errors | ... | ... | ... | ... |
<!-- scores:end -->

## Error trace

<What failure was traced and what the person sees.>

<!-- trace:start -->
1. `<path:line>`: <where it's raised; which of what, where, why, handle survive>
2. `<path:line>`: <next hop>
<!-- trace:end -->

## Per area

<For each area: the sample, the counter-example with `path:line`, and what would earn the next score up.>

## Change since last scorecard

<!-- delta:start -->
<output of delta.py, or "First run.">
<!-- delta:end -->
````
