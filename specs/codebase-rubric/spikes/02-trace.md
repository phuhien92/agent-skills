# 02 trace spike: brain-cli @ 7045e68

## Failure chosen

A person edits `<vault>/brain.json` and leaves it malformed (for example a trailing comma), then runs `brain search foo`. `JSON.parse` throws, and the CLI exits 1.

Method: read only. No test was run: `node_modules/` is absent and `npm test` runs `tsc` first, and no existing test feeds brain.json invalid JSON anyway (`grep "invalid JSON" test/` finds nothing).

Legend for the four things: **What** broke, **Where**, **Why**, **Handle** (ID, path, command name, or original cause kept attached).

## Hops

| # | path:line | What happens | What | Where | Why | Handle |
|---|---|---|---|---|---|---|
| 1 | `src/config.ts:338` | `JSON.parse(readFileSync(path))` throws a `SyntaxError` (message has the token and position). | yes | no (no file path in a SyntaxError) | yes | stack only |
| 2 | `src/config.ts:340-341` | `readJson` catches it and throws `new ConfigError(\`${path}: invalid JSON (${err.message})\`)`. The message is copied in; the original error is not attached (`cause` not set), so its stack is dropped. | yes | yes (absolute path to brain.json) | yes (as text) | path yes; original error object lost |
| 3 | `src/config.ts:69` | `loadConfig` calls `readJson(join(vault, "brain.json"))` with no catch; the `ConfigError` propagates. | yes | yes | yes | path |
| 4 | `src/cli.ts:547` | `run` calls `loadConfig(vault, …)` inside the `try` opened at `src/cli.ts:542`. (`userSettings()` at `src/cli.ts:256` reads only the user config and swallows its own errors at `src/config.ts:294`, so it does not intercept this.) | yes | yes | yes | path |
| 5 | `src/cli.ts:977-978` | `catch (err) { return fail(out, command, err); }` hands the error and the command name (`search`) to `fail`. | yes | yes | yes | path + command |
| 6 | `src/cli.ts:1601-1602` | `fail` maps `ConfigError` to `new CliError("config", err.message, 1)`. Message kept verbatim, code `config` added, exit set to generic 1 (shared with `no_vault`, `internal`, `post_failed`, per the help text at `src/cli.ts:182`). | yes | yes | yes | code `config` + path |
| 7 | `src/cli.ts:1606-1616` -> `src/feedback.ts:45-51` | `saveLastError` writes `{time, command, args, code, exit, message, version}` to `<state>/last-error.json`; any write failure is swallowed on purpose (`src/feedback.ts:49`). `brain feedback --from-last-error` reads it back. | yes | yes | yes | durable record: command, args, code, time, version |
| 8 | `src/cli.ts:1627` (human) / `src/cli.ts:1619-1625` (`--json`) | Human: stderr `brain: /path/to/vault/brain.json: invalid JSON (Expected double-quoted property name in JSON at position N)`. JSON: stdout envelope `{ok:false, command:"search", error:{code:"config", message:…}}`. | yes | yes | yes | path in message; `code` and `command` in JSON |
| 9 | `src/cli.ts:1630` -> `src/cli.ts:263`, `src/cli.ts:284` -> `bin/brain.js:10` | `fail` returns 1; `main` returns it after telemetry/update bookkeeping; `bin/brain.js` sets `process.exitCode = 1`. | exit 1 only | n/a | n/a | n/a |

Note: the published binary runs `dist/src/cli.js` (`bin/brain.js:2`); the hops above are in the TypeScript source it is compiled from. Line numbers in `dist/` differ.

## What the person sees (last hop)

`brain: /…/brain.json: invalid JSON (<parser message with position>)` on stderr, exit code 1. With `--json`, the same message plus `code: "config"` and `command: "search"`.

All four survive at the last hop: what (invalid JSON), where (the file path and parser position), why (the parser's message), handle (the path itself, plus `last-error.json` with command and args).

## Error score: 4

Evidence before score:
- For: the message is built once at the origin with path and cause text (`src/config.ts:341`) and survives every hop unchanged to stderr (`src/cli.ts:1627`). `fail` (`src/cli.ts:1593-1631`) is the single exit funnel for every built-in command and maps each error class to a stable `code`. `saveLastError` leaves a durable handle.
- Against 5: the cause chain is flattened to a string (no `{ cause: err }` at `src/config.ts:341`; same pattern at `src/config.ts:135` and `src/config.ts:149`), so the original stack is gone. The exit code for config errors is generic 1, not specific; only the JSON `code` distinguishes it.
- Above 3: context does not drop between layers; where and why both reach the person.

What would earn 5: attach the original error as `cause` in `ConfigError`, and give config errors their own exit code (or document that `code` in `--json` is the specific signal).
