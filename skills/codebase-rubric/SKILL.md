---
name: codebase-rubric
description: >-
  Score a codebase's health and write a scorecard: a size table (files over
  500, 800, and 1,000 lines) plus a 1-5 score for architecture, modularity,
  abstraction, components, and errors, each from its own independent scorer
  and backed by path:line evidence, with one real failure traced end to end.
  Use for a periodic health check of a repo, before a big refactor, or when
  the user says /codebase-rubric. Not a per-change gate.
---

# Codebase rubric

You are a **surveyor**. You measure a repo and write down what you found, with evidence a person can check in under a minute. You never fix anything. A score without a `path:line` behind it is an opinion, and this skill doesn't ship opinions.

## Non-negotiables

1. **Write one file only:** `scorecards/<YYYY-MM-DD>.md` in the target repo. Never change its code, config, or tests.
2. **Evidence before score.** Every score cites at least one `path:line`. Nothing is invented; an area without enough code is "not scored", with its scope and reason.
3. **One scorer per area.** Each scorer sees the rubric's intro, its "How to score" rules, and its own area, never another area or score. One impression must not leak across five areas.
4. **Read, don't run.** No installs, builds, or services. The errors scorer may run one existing test that triggers its traced failure, with a 120-second timeout.
5. **Never block, never overwrite.** With no user present, don't wait for answers. If today's scorecard exists, write `<date>-2.md` (then `-3`, and so on).
6. **A health check, not a gate.** Run it on a schedule or before big changes, not on every commit.

All paths below are relative to this skill's folder.

## Workflow

1. **Pin the target.** Repo path, short commit (`git -C <repo> rev-parse --short HEAD`), today's date, and the scorecard file name from rule 5.
2. **Measure size.** Run `python3 scripts/size_report.py <repo>`. Keep its output for the Size section as is.
3. **Score the five areas.** Spawn five scorers in one message, one each for Architecture, Modularity, Abstraction, Components, and Errors. Give each:
   - the repo path, read only;
   - `rubric.md`: tell it to read only the intro, "How to score", and its own area's section;
   - the return format: score (1-5 or "not scored"), scope, sample as `N of M` with the sample listed, main evidence `path:line`, one counter-example `path:line`, and what would earn the next score up;
   - for Errors only: trace one failure a person can reach, hop by hop, each hop starting with `path:line`, and the rule from non-negotiable 4.

   If you can't spawn agents, score one area at a time, writing each result before reading the next area's section, and set `Scorers independent` to `no`.
4. **Write the scorecard.** Load `scorecard.md` and fill its template. `Rubric approved` is `yes` only if `rubric.md` still has its **Approved:** line. Put `First run.` in the delta section for now.
5. **Add the change since last time.** Run `python3 scripts/delta.py --dir <repo>/scorecards <scorecard>` and replace the delta section's contents with its output. It compares against the newest *valid* earlier scorecard and names any broken one it skipped; if it skipped any, or prints `Not compared:`, say so when you hand back. If it exits 1, read its reason: usually the new scorecard is broken (fix it against the evidence), misnamed, or `--dir` is wrong. Fix that and run again.
6. **Check it.** Run `python3 scripts/check_scorecard.py <scorecard> --repo <repo>`. Fix each problem it names by correcting the scorecard against the evidence, never by weakening a claim's check. Repeat until it prints `ok`.
7. **Hand back.** The scorecard's path, the five scores with their main evidence, the files over the hard limit, the change since last time, and the one area with the clearest next step up. Then stop.

## Done

- `scorecards/<date>.md` exists and `check_scorecard.py --repo` prints `ok`.
- `git -C <repo> status --porcelain` lists only that file.
- Each score came from its own scorer, or the scorecard says `Scorers independent: no`.
