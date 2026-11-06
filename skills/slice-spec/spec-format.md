# Spec format

Loaded by `slice-spec` at step 5 of Interview, and in Reslice. A spec is a folder:

```
specs/<feature>/
├── README.md          # intent, constraints, graph, handoff
├── slices/
│   ├── 01-<name>.md   # one file per slice, numbered in build order
│   └── 02-<name>.md
└── decisions.md       # written later by decision-checker, never by slice-spec
```

`<feature>` is short kebab-case. A one-slice feature still gets the folder, so every tool finds specs in the same place.

## README.md

```markdown
# <Feature name>

## Intent

> <The user's own words, quoted. Add context only where a reader needs it.>

How the user will know it worked: <their answer>

## Non-goals

- <what this must not touch or become>

## Constraints

- <data that must survive, APIs that must not break, budgets, deadlines>
- Backward compatibility: <none, or exactly what must keep working>

## Slice graph

| # | Slice | Question it answers | Check | Depends on |
|---|---|---|---|---|
| 01 | <name> | <one question> | `<command>` or <artifact + decision> | none |
| 02 | <name> | ... | ... | 01 |

Slices with no unmet dependency can be built in parallel.

## Open questions

- <question> **Recommended:** <answer>. <Who decides, and by when.>

## Decided in planning

- <decision>: <why>, and what was turned down.

## Next agent prompt

<Status, the next slice to pick up, and anything a cold agent needs. Keep it current and short; it is the handoff, not a log.>
```

When the intent was inferred (no user present), say so on the first line under **Intent**.

## slices/NN-name.md

```markdown
# NN: <Slice name>

**Question:** <the one question this slice answers>

**Seam:** <the module, interface, or file boundary it builds or changes, with inputs and outputs>

**Check:** `<command>` passes when <what pass means>. Fails when <what fail means>.

**Decided:**
- <choices already made for the worker, with the reason>

**Delegated to the worker:**
- <choices the worker may make alone; decision-checker skips these>

**Out of scope:**
- <what belongs to a later slice, with its number>
```

## Rules

- **Intent stays quoted.** Never rewrite the user's words into a broader goal. A reviewer treats the Intent section as acceptance criteria.
- **Delegated means delegated.** Anything listed there is the worker's call. Anything not listed and not decided is a gap, and decision-checker will report it.
- **Reslice in place.** Mark a replaced slice `Replaced by NN, NN` at the top and keep it, so the history is readable.
- **No product code in the spec.** Interfaces and examples are fine; implementations belong to the worker.
