# Scoring spike: brain-cli @ 7045e68

Slice 03. Hand-written against `skills/codebase-rubric/rubric.md`. Four non-error areas only. Paths are relative to the brain-cli repo root. Size evidence from `size_report.py`: `src/cli.ts` 1,692 lines (over hard), `src/extensions.ts` 540 (over target); every other `src/` file is under 500.

How I read rule 4 (tie): a 4 needs the 5 anchor to describe most of the repo with only isolated exceptions. When the 3 anchor's own description fits the repo as a whole and I was unsure between 3 and 4, I took 3 and named what would earn 4.

| Area | Score | Main citation |
|---|---|---|
| Architecture | 3 | `src/cli.ts:1381` |
| Modularity | 3 | `src/cli.ts:1083-1094` (one of several unrelated sections in a 1,692-line file) |
| Abstraction | 3 | `src/cli.ts:206` vs `src/extensions.ts:79-82` |
| Components | 3 | `test/lint.test.ts:14-20` |

## Architecture: 3

The layers have names and a documented shape, but some paths skip them. A command handler runs raw SQL against the index instead of going through the Store API (`src/cli.ts:1381`, `s.db.prepare("SELECT path, title FROM notes")`). The `log add` handler also holds a 45-line URL-redaction protocol inline (`src/cli.ts:658-702`) that belongs with `redactor` in `src/feedback.ts:68`.

- Strongest evidence: `src/cli.ts:1381` (handler writes SQL directly; `Store.db` is public at `src/store.ts:71`).
- Wrong-way import: the index layer imports the extensions feature, `src/store.ts:20`, used inside `refresh()` at `src/store.ts:145` and `src/store.ts:172-180`.
- Counter-example (toward 5): `docs/architecture.md:28-36` draws the CLI as args, refresh, then four command groups, and `src/cli.ts:562-570` (`ingest`) is a thin handler that validates, delegates to `ingest()`, and prints.
- What would earn 4: handlers that only parse, delegate, and print; the redaction block moved next to `redactor`; a Store method for the note list instead of SQL in `cli.ts`.

## Modularity: 3

Most modules are small and focused (15 of 17 `src/` files under 500 lines; `src/paths.ts:1-3` states its one job), but `src/cli.ts` is the hub that collects every new feature. Besides command dispatch, it owns extension process supervision, setup, feedback drafting, doctor checks, and markdown section extraction.

- Strongest evidence: unrelated sections of `src/cli.ts`: process-tree killing at `src/cli.ts:1083-1094`, doctor checks at `src/cli.ts:1452-1456`, markdown section parsing at `src/cli.ts:1651-1660`.
- Hub shape: `src/cli.ts:9-50` imports from 15 of the other 16 `src/` modules.
- Counter-example (toward 5): `src/paths.ts:10-32`, a 59-line module that is the one place locations are resolved.
- Why not 2: the 1 anchor needs most modules to be tangled; here only one is. What would earn 4: moving the extension runner (`src/cli.ts:1083-1253`) into `extensions.ts` or a new module, and `extractSections` (`src/cli.ts:1651-1690`) into `note.ts`.

## Abstraction: 3

The main concepts have names and homes (Store, Note, Config, scope), but some leak or live in two places. The list of built-in command names is kept twice, and the two copies already disagree: `src/cli.ts:206` includes `"update"`, `src/extensions.ts:79-82` (`RESERVED`) does not.

- Strongest evidence: `src/cli.ts:206` vs `src/extensions.ts:79-82` (one concept, two homes, drifted).
- Near-identical blocks: `killExtensionTree` at `src/cli.ts:1083-1094` and `killTree` at `src/hooks.ts:72-82`; `readScope` at `src/config.ts:198-201` and `integrationScope` at `src/config.ts:232-235` compute the same prefix list.
- Leak: `src/config.ts:210` spells the lifecycle folder as the literal `"lifecycle/"` while `src/log.ts:37` exports `LIFECYCLE_KIND`.
- Counter-example (toward 5): `src/cli.ts:590-592` searches through `store.search(query, {...})` with no SQL or FTS5 knowledge.
- What would earn 4: one exported command list, one process-kill helper, `readScope` calling `integrationScope`, and `LIFECYCLE_KIND` used in `config.ts`.

## Components: 3

Most units take explicit inputs (`lint(store, cfg)` at `src/lint.ts:32`, `parseNote(relPath, source)` at `src/note.ts:26`), but 13 of 18 test files test through the spawned binary with environment setup rather than calling the unit. Lint, for example, is tested by spawning `bin/brain.js` with six environment variables (`test/lint.test.ts:14-20`).

- Strongest evidence: `test/lint.test.ts:14-20` (whole-CLI setup to test a function that already takes `store, cfg`).
- Hidden global read deep in a unit: `loadConfig` reads `process.env.BRAIN_EXTENSION_SCOPE` at `src/config.ts:140`, though the line above (`src/config.ts:138`) shows the pattern done right: `opts.as ?? process.env.BRAIN_AS`.
- Heavy setup: `test/extensions.test.ts:36-54` sets or clears nine environment variables per test.
- Counter-example (toward 5): `src/note.ts:26` and its direct test `test/note.test.ts:5-34`, which passes a string and asserts the result, no files or env.
- What would earn 4: unit tests that call `lint`, `loadConfig`, and the hooks directly with explicit options, leaving CLI spawning to a few contract tests.

## 60-second check: fastest and slowest

Fastest to verify:

1. `src/cli.ts:1381`: one line of SQL in a command file; the reason is visible without context. Pair with `src/store.ts:71` if the reader wants to see `db` is public.
2. `src/cli.ts:206` vs `src/extensions.ts:79-82`: two short arrays; search for `"update"` in each.
3. `src/hooks.ts:72-82` vs `src/cli.ts:1083-1094`: two 11-line functions that read the same side by side.

Slowest to verify:

1. `src/cli.ts:658-702`: 45 lines of nested redaction logic; a reader has to understand it before agreeing it is business logic in a handler.
2. `src/store.ts:20` with `src/store.ts:145` and `:172-180`: judging the import as "wrong-way" needs a view of which module is the lower layer, which the folder tree (flat `src/`) does not show.
3. The modularity claim that `src/cli.ts` holds unrelated sections: three ranges in a 1,692-line file, and "unrelated" is a judgment across them, not one visible line. The "13 of 18 test files spawn the binary" count also needs a grep, not a glance.
