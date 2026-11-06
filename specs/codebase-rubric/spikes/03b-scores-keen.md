# Scorecard: keen-design-system (hand-scored, independent)

Target: shallow clone of phuhien92/keen-design-system. Paths below are relative to the repo root. Read only.

Size evidence (`size_report.py`): no code file over 500 lines. The largest hand-written files are `tools/token-generator/src/gates.ts` (284) and `design.ts` (222). The whole generator plus the runtime package is about 2,400 lines. Most code is the token generator (a build/verify CLI). The shipped React library is tiny: one `Icon` component plus a generated registry and token files.

| Area | Score |
|---|---|
| Architecture | 4 |
| Modularity | 4 |
| Abstraction | 4 |
| Components | 4 |
| Errors | 4 |

## Architecture: 4

The README names the workspace parts (tokens, `keen` package, generator, docs, Storybook, Astro fixture), and the generator flows one way: `cli.ts` hands off to `pipeline.generate`, which runs load (`model.ts`), then resolve (`resolve.ts`), then emit (`emit.ts`, `pen.ts`, `motion.ts`, `icons.ts`). I found no import cycles. Pure generation is kept apart from file reads (`readSources`/`readExtras`).

- Strongest: `tools/token-generator/src/cli.ts:13-23` (entry delegates), `tools/token-generator/src/pipeline.ts:81-108` (load, then resolve, then emit, all in memory).
- Counter-example: `tools/token-generator/src/gates.ts:230-234`. The gate runner reads and parses the contract files itself instead of going through the pipeline's read layer, so the orchestrator also does I/O.
- What would earn a 5: give the gate layer one job by moving its file reads behind the same read functions the pipeline uses.

## Modularity: 4

Modules are small and each has one job: `contrast.ts` (42 lines) only checks contrast, and `resolve.ts` only resolves references. The icon feature lives in a predictable set of files (`src/icons.ts`, `packages/keen/src/icons/*`, `test/icons.test.ts`, `docs/foundations/icons.md`). `scaffold.ts` lists exactly which files a new component touches.

- Strongest: `tools/token-generator/src/contrast.ts:1-42`. It is self-contained, with two imports.
- Counter-example: `tools/token-generator/src/gates.ts:1-25`, `53-221`. This is the one hub. It imports 12 modules, and every new check adds an entry here plus one in `.keen/gates.json`. It stays under the soft tier, so the hub problem is mild.

## Abstraction: 4

The domain ideas each have one type and one home: `Token`, `Issue`, and `Source` (`model.ts`), `Resolved` (`resolve.ts`), `Contract` (`contract.ts`). Callers use `generate()` and `resolveTokens()` without knowing how they work inside.

- Strongest: `tools/token-generator/src/model.ts:1-26` (core types), used unchanged by `pipeline.ts:81` and `contrast.ts:24`.
- Counter-examples (the 3 anchor's "leaks"):
  - `tools/token-generator/src/gates.ts:163`. The `motion-timings` gate regex-parses the text of the generated `motion.ts` instead of comparing against the emitter's output, so it depends on the emitter's formatting.
  - `Tier` names two different ideas: token tier at `tools/token-generator/src/model.ts:3` and gate tier at `tools/token-generator/src/gates.ts:27`.
  - The same "token sources have issues; see tokens-valid" guard is copied 9 times in `gates.ts`, for example at `gates.ts:58`, `71`, and `84`.
- These are small next to the core types, so 4 rather than 3.

## Components: 4

Units take explicit inputs and return values. `generate(sources, extras)` takes in-memory sources, so rule tests build a small fixture in place, and the `Icon` test renders markup with no setup.

- Strongest: `packages/keen/src/icons/Icon.tsx:11-22` with its direct test `packages/keen/tests/icons/Icon.test.tsx:6-25`. `tools/token-generator/test/rules.test.ts:20-46` is a minimal fixture passed straight to `generate`.
- Counter-example: `tools/token-generator/test/gates.test.ts:10-35`. The gate tests copy half the repo to a temp dir, symlink `node_modules`, and patch the module-level `gates` registry in place to stub two gates. That is heavy setup, and it works by mutating shared state.

## Errors: 4

**Traced path: a token references a missing token, during `pnpm tokens:build`.**

1. Origin: `tools/token-generator/src/resolve.ts:32`. `report({ rule: "reference", token: from, message: "references missing token {x}" })`. The issue names the referring token, the rule, and the missing target.
2. `tools/token-generator/src/pipeline.ts:88`. All issues are collected (not stopped at the first one) and returned with no files written.
3. `tools/token-generator/src/cli.ts:15-17`. Each issue is printed through `formatIssue` (`pipeline.ts:110`) as `color.semantic.action [reference]: references missing token {color.primitive.blue-601}`, and the build exits with code 1. A usage error exits with code 2 (`cli.ts:40-41`).

At the last hop the person sees **what** (the reference failed), **where** (the token's dotted name, which also tells you its tier file), **why** (the target is missing), and a **handle** (the rule id plus the token name). Through `verify`, the same issues appear under a named gate with its description (`gates.ts:276-277`), and other gates prefix the failing file and the fix command (for example `gates.ts:64` and `contrast.ts:37`). The pattern repeats across the checks.

- Counter-example: unexpected exceptions. `readSources` calls `JSON.parse` with no file context (`tools/token-generator/src/pipeline.ts:77-78`). Under `verify`, the catch at `tools/token-generator/src/gates.ts:272-273` keeps only `error.message` and drops the stack. So a malformed `tokens/semantic.json` shows up as a bare `Unexpected token ...` under `tokens-valid`, with no file name: you get what and why, but not where.
- What would earn a 5: attach the file name when parsing, and keep the cause or stack in the gate-runner catch.
- The runtime library has almost no failure paths (`Icon` cannot fail at runtime for a typed `name`). This score covers the generator.

## Notes on the rubric

- All five areas landed on 4. For this small, carefully kept repo, "5 fits most, plus one counter-example" describes every area, so 4 became the resting score. The anchors pushed scores toward 4, not 3.
- The size-based evidence named in the Modularity 1 and 3 anchors (soft/hard-tier files) never fires here. Modularity then rests only on judgment about the hub.
- Components and Errors are scored almost entirely on the build tool, because the shipped library is one component. The rubric has no way to say "too little code to score this area".
