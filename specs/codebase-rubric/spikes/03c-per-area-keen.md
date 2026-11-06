# Per-area scorers on keen-design-system

Five fresh scorers, one per area, each shown only its own section of `rubric.md` and never another score. Repo: phuhien92/keen-design-system (shallow clone; its history is one squashed commit, `847e726`). Size run with the code-only rules: no code file over 500 lines; skipped: generated header 4, lockfile 2, not a code file 61. Compare with `03b-scores-keen.md`, one scorer for all areas.

| Area | One scorer | Per area | Sample fit | Main evidence | Counter-example |
|---|---|---|---|---|---|
| Architecture | 4 | 4 | 8 of 10 | `tools/token-generator/src/cli.ts:14-22`, `pipeline.ts:81-108` | `boundary.ts:87-92` reads disk mid-check |
| Modularity | 4 | 4 | 14 of 16 | `motion-checks.ts:1`, `contrast.ts:1` | `gates.ts:53` registry imports 14 modules |
| Abstraction | 4 | 3 | 5 of 12 | casts at `gates.ts:168`, `gates.ts:210`, `motion.ts:66`, `contrast.ts:28`; `Tier` at `model.ts:3` vs `gates.ts:27` | `model.ts:37` `cssVar` |
| Components | 4 | 4 | 7 of 10 | `boundary.ts:33` with `test/boundary.test.ts:17-22` | `test/gates.test.ts:10-35` copies the repo |
| Errors | 4 | 3 | 5 of 9 | trace: `resolve.ts:32` → `resolve.ts:23` → `pipeline.ts:87-88` → `cli.ts:16` → `cli.ts:17` (exit 1); the issue names the token but not its file | `gates.ts:273` keeps only the message |

All paths are under `tools/token-generator/src/` unless shown. Every scorer scoped to the generator and set aside `packages/keen` (5 small files) as too little to score.

Findings:
- Per-area scoring separates areas: two of five dropped to 3 once each scorer had to count a sample.
- The modularity 5 anchor needs git history ("a recent feature whose files share one folder"). A squashed history caps the area at 4. Fix: let folder layout stand in when history is flat.
