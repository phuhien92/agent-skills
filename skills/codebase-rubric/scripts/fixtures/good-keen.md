# Codebase scorecard: keen-design-system

Fixture built from `specs/codebase-rubric/spikes/03c-per-area-keen.md`.

<!-- meta:start -->
| Key | Value |
|---|---|
| Repo | phuhien92/keen-design-system |
| Commit | 847e726 |
| Date | 2026-11-06 |
| Rubric approved | yes |
| Scorers independent | yes |
<!-- meta:end -->

## Size

<!-- size:start -->
| File | Lines | Tier |
|---|---|---|

Skipped: generated header: 4, lockfile: 2, not a code file: 61
<!-- size:end -->

## Scores

<!-- scores:start -->
| Area | Score | Scope | Sample | Evidence |
|---|---|---|---|---|
| Architecture | 4 | tools/token-generator/src | 8 of 10 | `tools/token-generator/src/pipeline.ts:81-108` runs load, resolve, emit with no I/O |
| Modularity | 4 | token-generator, keen, storybook | 14 of 16 | `tools/token-generator/src/contrast.ts:1` one check per module |
| Abstraction | 3 | tools/token-generator/src | 5 of 12 | `tools/token-generator/src/gates.ts:168` casts stored values by hand |
| Components | 4 | token-generator and Icon | 7 of 10 | `tools/token-generator/src/boundary.ts:33` with a one-string test |
| Errors | 3 | token-generator CLI | 5 of 9 | `tools/token-generator/src/resolve.ts:32` names the token but not its file |
<!-- scores:end -->

## Error trace

A missing token reference during a build.

<!-- trace:start -->
1. `tools/token-generator/src/resolve.ts:32`: issue raised with the token name; no source file.
2. `tools/token-generator/src/resolve.ts:23`: deduplicated and pushed.
3. `tools/token-generator/src/pipeline.ts:87-88`: merged into issues; nothing written.
4. `tools/token-generator/src/cli.ts:16`: printed as `color.x [reference]: references missing token`.
5. `tools/token-generator/src/cli.ts:17`: exits 1, the same code as every failure.
<!-- trace:end -->

## Change since last scorecard

<!-- delta:start -->
First run.
<!-- delta:end -->
