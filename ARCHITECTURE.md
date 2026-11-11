# Architecture

One-page map of this skill pack. Adapted from the layout of [wshobson/agents](https://github.com/wshobson/agents/blob/main/ARCHITECTURE.md), scaled down for a personal pack used in Claude Code and Cursor.

## Vision: skill blocks for software factories

A software factory is a loop of stations that agents run with little human attention. You set the intent and judge the result; agents do the work in between and check each other.

```
            command layer: dispatch, isolate, supervise (a harness, not this pack)
 Intent → Map → Slice → Build → Verify → Decide → Learn
   ↑                                                 │
   └──────────── lessons feed the next run ──────────┘
```

This pack does not build the factory. It ships the **blocks** a factory calls at each station, and the coaching skills that train the person who runs it. Files carry the state between stations (spec, slices, code, `decisions.md`, notes), so any agent can pick up the work cold.

| Station | Block | Status |
|---|---|---|
| Intent | `think-with-me`, `brain` | have |
| Map, Slice | `slice-spec` | have; writes the spec that Build and Decide read, and sizes each slice and PR with `scripts/diff_size.py` |
| Build | the harness's own workers | not ours |
| Verify | `codebase-rubric`, plus the "agents check before the human reviews" rule in `AGENTS.md` | have; a periodic scorecard, not a per-change gate |
| Decide | `decision-checker` | have; first block that runs as a gate |
| Learn | `brain` stores lessons | half: nothing feeds them back yet |
| (the human) | `behavioral-story-depth`, `radio-system-design-practice` | have; human-facing on purpose |

### Size before review

Before an agent opens a PR, it runs `python3 <slice-spec>/scripts/diff_size.py . <base>..HEAD`, with `<base>` the remote branch the PR targets (such as `origin/main`; a stale local `main` inflates the count), and pastes the table into the PR description. It counts new product-code lines, with moved code reported apart, against target 400, soft 800, hard 1,500, for each commit and for the whole branch. Over soft, a commit gets "consider Reslice" and the branch gets "split the goal". It warns and never blocks: one gate per task stays `decision-checker`.

### How a block joins a harness

| Level | The block gains | Proof |
|---|---|---|
| 1. Portable | Standard `SKILL.md`, installs in any harness | `npx skills`, the plugin marketplace, Cursor |
| 2. Callable | Runs with no human and never blocks a run | a "no user present" rule plus an eval |
| 3. File contract | Reads one known file, writes one known file | a contract table in the skill |
| 4. Enforced gate | A hook or task instructions require it before "done" | a hook script plus an eval |

`decision-checker` is at level 4: `harness.md` holds its contract, `hooks/require-ledger.sh` is its Stop-hook gate, and `.claude/agents/decision-checker.md` is the reviewer subagent the hook hands work to.

### Design rules for blocks

1. **Two ways, same files.** Every block runs by hand or from a harness, with the same files in and out. No block depends on one vendor's harness.
2. **Structure over prompts.** A rule that matters gets a hook, a script, or a required line in task instructions, not only a sentence asking nicely.
3. **One gate per task.** Add a block as the gate a delivery path owns. Don't stack reviewers on top of each other.
4. **Evidence is not authorization.** A ledger, report, or recommendation informs the human's call. It never merges, deletes, or ships anything on its own.
5. **Coaching skills stay human-facing.** They train the captain and don't need to run inside a harness.

## Invariants

1. **One source of truth per skill.** Each skill is authored once, at `skills/<name>/`. Everything else (slash commands, Cursor links, plugin manifests) only points at it. Never copy skill text into another folder.
2. **One canonical context file.** `AGENTS.md` is the only context file written by hand. `CLAUDE.md` is a symlink to it. Keep it under ~150 lines; it routes, it doesn't teach.
3. **Progressive disclosure.** `SKILL.md` holds the workflow and stays under 8 KB. Long material (examples, probe banks, knowledge files) lives next to it and is loaded only when the workflow says so.
4. **Every skill is wired the same way.** A skill isn't done until it has all five touchpoints listed under *Wiring*. `tools/validate.py` checks them.
5. **Checks give a fix, not just a failure.** Every validator finding prints the exact change to make.
6. **Skills never invent the user's facts.** Skills that work on personal material (stories, notes, opinions) ask for missing facts instead of filling them in. Evals check this.

## Layout

```
agent-skills/
├── AGENTS.md                     # canonical context file (routing only)
├── CLAUDE.md                     # symlink → AGENTS.md
├── ARCHITECTURE.md               # this file
├── README.md                     # user-facing landing page
├── skills/<name>/                # SOURCE OF TRUTH
│   ├── SKILL.md                  # frontmatter: name, description ("Use when …")
│   ├── *.md                      # optional, loaded on demand
│   └── hooks/                    # optional hook scripts that enforce a gate
├── .claude/agents/<name>.md      # optional Claude Code subagent that loads the <name> skill
├── .claude/commands/<name>.md    # Claude Code slash command → "follow the <name> skill"
├── commands/<name>.md            # plugin command copy (same text)
├── .cursor/commands/<name>.md    # Cursor slash command (same text)
├── .cursor/skills/<name>         # symlink → ../../skills/<name>
├── .claude-plugin/plugin.json    # Claude Code plugin manifest
├── plugin.json                   # generic manifest
├── evals/<name>.md               # behavior cases per skill
├── tools/validate.py             # structural checks (stdlib only)
├── .github/workflows/validate.yml
└── docs/
```

## Wiring (per skill)

| Touchpoint | Path | Checked by |
|---|---|---|
| Skill body | `skills/<name>/SKILL.md` with `name` matching the folder and a `description` | `validate.py` |
| Claude Code command | `.claude/commands/<name>.md` | `validate.py` |
| Plugin command copy | `commands/<name>.md` | `validate.py` |
| Cursor | `.cursor/commands/<name>.md` + `.cursor/skills/<name>` symlink | `validate.py` |
| Docs | a row in `README.md` and a `/name` section in `AGENTS.md` | `validate.py` |
| Behavior | `evals/<name>.md` | `validate.py` (warning until every skill has one) |
| Subagent (optional) | `.claude/agents/<name>.md` named after the skill and loading it, listed in `.claude-plugin/plugin.json` `agents` | `validate.py` |

## Quality gates

1. **`python3 tools/validate.py`** — structure and wiring. Errors fail CI; warnings are advisory.
2. **Evals** — `evals/<name>.md` lists prompts and what a good and a bad response look like. Run by hand for now: paste the prompt into a fresh session with the skill loaded and grade against the case. Automate only after the cases have caught a real regression.

CI: `.github/workflows/validate.yml` runs the validator and the `codebase-rubric` script tests on every push to `main` and every PR.

## What we deliberately didn't adopt (yet)

- **Per-harness adapters** (`tools/adapters/` in wshobson/agents). This pack targets Claude Code and Cursor, which both read the source files directly.
- **`plugins/<group>/` bundles.** Worth it once there are several skill families (interview, notes, design). With a handful of skills, a flat `skills/` folder is simpler.
- **Score snapshots and LLM judges.** Start with hand-graded cases; add automation when it has something to protect.

## Adding a skill

1. Write `skills/<name>/SKILL.md`.
2. Add the three command files and the Cursor symlink (see *Wiring*).
3. Add the README row and the `AGENTS.md` section.
4. Add `evals/<name>.md` with at least three cases.
5. Run `python3 tools/validate.py` until it reports no errors.

## Decisions log

Newest first. Each entry says what we decided, why, what we turned down, where it can fail, and when to revisit it.

### 2026-11-11: The Stop hook hands the check to a reviewer subagent

- **Decision:** add `.claude/agents/decision-checker.md`, a Claude Code subagent that loads the skill and runs Check with fresh context. `require-ledger.sh` now tells the agent to hand the branch to it, with the scope, the baseline and the author's own guesses, and to run the skill itself only when the subagent isn't installed. One real file, no symlink: the plugin manifest's `agents` field points at it, as `commands` already points at `.claude/commands`.
- **Why:** the hook made the author check its own work, against the "agents check before the human reviews" rule. Structure over prompts: the hook already fires reliably, so pointing it at an independent reviewer is the cheapest way to make that rule real.
- **Turned down:** a root `agents/` folder with a `.claude/agents/` symlink (nobody confirmed Claude Code follows a symlinked agent file, and a miss would quietly send the hook back to self-review), copying the skill's text into the agent (breaks one source of truth; the agent only loads the skill), preloading it with the `skills:` field (the name differs between a plugin and a project install, and a wrong name fails quietly), and a hook that spawns the subagent itself (hooks can't; the block reason is the lever).
- **Where it can fail:** the block reason is still words. The main agent can ignore it and review itself, and the hook can't tell the difference, because it only checks that `decisions.md` exists. In a subagent nobody can answer questions, so every run follows rule 7 and caps confidence at medium.
- **Revisit when:** Claude Code lets a hook start a subagent directly, or a self-review slips through on real work.

### 2026-11-07: Add `explainer-video` and `house-style-design`, the first "make" skills

- **Decision:** two skills that produce media from a project's own art. `explainer-video` builds a film as one deterministic web page (camera rig, elements on twos, `SEEK(t)`), times every beat to the narration with `scripts/vo_lines.py`, renders frame by frame, and mixes to −14 LUFS with `scripts/mix.py`. `house-style-design` reads the house style and rules, draws at twice the house canvas, frames the art (an ultimate card template), and renders PNGs checked at phone size.
- **Why:** both came out of real work on one game (three cuts of a lore video, two ultimate cards). The same failures repeated: labels shifted after fonts loaded, highlights guessed instead of measured, a Vox-style desk chosen for an invented world, sentence times guessed from pause length, faces hidden by props. Each is now a rule, a check or a script.
- **Turned down:** shipping per-style starters (one starter has every helper; styles are a reference file); hosted video services (a local render keeps the user's art off third parties); bundling a sound library (any library works through a cues file).
- **Where it can fail:** `vo_lines.py` aligns phrases to the script's punctuation and pause length; narrators who skip many commas or read in one breath need a manual check (lines are flagged). Neither skill can hear or judge taste; both say what they couldn't check. They sit outside the factory stations: human-facing make tools, like the coaching skills.
- **Revisit when:** a second project uses them; if they grow, group them in a `plugins/make/` bundle.

### 2026-11-06: Measure the skills from their own output first

- **Decision:** `tools/skill_metrics.py` reads specs, `decisions.md` ledgers, `scorecards/`, and a hand-kept `skill-outcomes.md`, and reports per-skill numbers: reslices, verdicts per slice, score change, scoring noise, and overruled, escaped, and confirmed calls. Read only, standard library only, tested in CI.
- **Why:** whether a skill was *right* lives in the files it writes and in what the user later finds out, not in session traces. Local files keep the user's code off third-party services.
- **Turned down for now:** PostHog LLM Analytics. Useful for cost, duration, and failures per run, but its traces carry prompts and code, so it needs the user's approval and a metadata-only setup. Revisit if cost or reliability becomes the open question.
- **Where it can fail:** outcomes are only as complete as the log; "escaped" problems are the ones nobody notices. Scoring noise needs two runs on the same commit, which nobody does by accident.
- **Revisit when:** the first real end-to-end run has produced a month of data.

### 2026-11-06: `codebase-rubric` is the Verify block

- **Decision:** a periodic health check that writes `scorecards/<date>.md`: a size table (500, 800, 1,000 lines), five areas scored 1-5 by five independent scorers with `path:line` evidence, one failure traced end to end, and the change since the last scorecard. Three standard-library scripts own the mechanics (`size_report.py`, `check_scorecard.py --repo`, `delta.py`); agents own the judgment. Built from the spec in `specs/codebase-rubric/`, the first spec written by `slice-spec`.
- **Why:** the size tiers and five areas came from a rubric the user shared. Size is report only; enforcement is left to adopting dzhng's `ratchet-files` later. One scorer per area, because a single scorer gave every area the same score on two repos (all 3s, then all 4s); five independent scorers gave keen-design-system 4, 4, 3, 4, 3 and brain-cli 4, 3, 3, 3, 4, each from a counted sample.
- **Turned down:** blocking commits (a second gate on every change), running live failures (slow and fragile across repos), and one scorer for all areas (one impression leaks across all five).
- **Where it can fail:** about five scorers' worth of tokens per run; scores rest on samples, so a different sample can move a score by one; git history that is squashed limits the Modularity evidence (folder layout stands in). Four `decision-checker` ledgers ran during the build. The unsound calls they found were fixed, or settled by one of the user's calls; the user made 14 calls along the way.
- **Revisit when:** a repo's second scorecard shows whether the delta catches real change, or scores swing by more than one between runs with no code change.

### 2026-11-06: Rename `/hien` to `/think-with-me`

- **Decision:** the skill is now `think-with-me` (folder, commands, Cursor link, eval, docs, manifests). Its persona and knowledge files are unchanged.
- **Why:** the user's call. A name that says what the skill does reads better next to the other blocks.
- **Where it can fail:** the skill fetches its knowledge files from `main`. Until this rename is merged, `skills/think-with-me/` doesn't exist there, so `SKILL.md` falls back to the old `skills/hien/` URLs. After the merge, the old URLs 404 and the new ones serve. Anyone who installed the old name keeps `/hien` until they reinstall.
- **Revisit when:** merged; then drop the `skills/hien/` fallback line.

### 2026-11-06: `slice-spec` is the second factory block

- **Decision:** `slice-spec` interviews the user one question at a time (each with a recommended answer), then writes `specs/<feature>/`: quoted intent, non-goals, a slice graph, and one file per slice with a check that can fail, what's decided, and what's delegated. It fans out to three drafters with different lenses only when the first draft has four or more slices.
- **Why:** it fills the Map and Slice stations and feeds `decision-checker` directly: the spec is its baseline, the Delegated lists are what it skips, and every gap a slice leaves becomes a ledger entry. Clearer slices should mean shorter ledgers. Interview style matches the coaching skills; fan-out only for big features keeps token cost down on small work.
- **Turned down:** draft-first specs (faster, but the user corrects a plan instead of shaping it), and always fanning out (about three times the tokens on every spec).
- **Where it can fail:** a check is only as strong as the tests the worker writes for it. With no user present, the intent is inferred, and every guess goes under Open questions. A blind run on a toy app (persist notes, add tags, keep the CLI) passed 6 of 6 graded cases: four slices, each check failing on today's repo and passing once built, and no product code touched. The fan-out case only ran through its sequential fallback, because the test agent couldn't spawn agents.
- **Revisit when:** a real spec runs end to end through a harness and `decision-checker`.

### 2026-11-06: Support DeepSeek Harness without a DSH-specific build

- **Decision:** ship the same `skills/<name>/SKILL.md` bundles to DeepSeek Harness (`dsh`) by linking them into `.agents/skills`. Reuse the Claude Code Stop hook through dsh's `dsh-hooks-claude-code` bridge instead of writing a Cordis plugin.
- **Why:** dsh's filesystem skill provider reads exactly our format (`name` and `description` required, `user-invocable` and `disable-model-invocation` honored, bundle files loaded on demand) from `.agents/skills`. Its hook bridge maps `Stop` to `agent/turn-stopping` and honors `{"decision": "block"}`. Design rule 1 holds with zero forks.
- **Turned down:** a native dsh plugin bundle (`package.json` with a `dsh` field). More reach (UI, events), but a second code path to maintain for one harness. Revisit only if a block needs dsh-only features.
- **Where it can fail:** dsh is a preview (0.2.x) and the hook bridge is experimental. It always sends `stop_hook_active: false` and caps nothing, so the hook now self-limits per session. Verified against dsh source at 0.2.2-rc.1 (2026-11-04), not by running dsh: running it needs a model API key.
- **Revisit when:** dsh ships a stop loop-guard or reaches 1.0.

### 2026-11-06: Enforce gates with structure, starting with a Stop hook

- **Decision:** `decision-checker` ships `hooks/require-ledger.sh`. It blocks a Claude Code agent from finishing once when the branch changes code but has no `decisions.md`.
- **Why:** DeepSeek's harness team reported that a single agent prompted to "use a sub-agent when appropriate" never delegated in five runs; only structural separation made it reliable. Our "agents check first" rule is a prompt and will fail the same way.
- **Turned down:** a hook that grades the ledger's quality. Grading is the skill's job; the hook only proves the check happened.
- **Where it can fail:** it checks that a ledger exists on the branch, not that it's current. A ledger written early and never updated still passes. An independent review found three bugs before commit (a lowercased working-directory path, a deleted ledger counting as written, non-ASCII paths breaking the checks); all fixed and re-tested. It's Claude Code only; other harnesses use the task-instructions line.
- **Revisit when:** a stale ledger slips through on real work.

### 2026-11-06: Plug into an existing command layer; don't build our own

- **Decision:** this pack stays a library of blocks. For orchestration, try [firstmate](https://github.com/kunchenguid/firstmate) on one real project, with its workers loading these skills.
- **Why:** firstmate and DeepSeek's super agent design both use the same shape: one agent you talk to, which never does the work itself, dispatching isolated workers. firstmate is mature (about 260 scripts in `bin/` and 380 files in `tests/` as of 2026-11-05, with restart-proof state on disk). Our value is the blocks, not another router.
- **Turned down:** building a router skill here. It would duplicate firstmate badly and grow this pack into the workshop it should serve.
- **Where it can fail:** firstmate's contracts change, or it doesn't load external skills cleanly. Design rule 1 keeps every block usable without it. Its optional public-mention relay reads untrusted input, so leave it off at first.
- **Revisit when:** the firstmate trial ends.

### 2026-11-06: `decision-checker` is the first factory block

- **Decision:** build `decision-checker` before `slice-spec`. It lists the calls an agent made where the prompt was silent, ranked least-confident first, and changes no code.
- **Why:** it works on any agent-written change, not only long runs; it turns the "agents check first" rule into something runnable; and it backs the whiteboard rule (explain the shape and the key decisions without reading every line). Inspired by [dzhng/skills](https://github.com/dzhng/skills) `audit-decisions`, rewritten in our own words and voice.
- **Turned down:** copying dzhng's full build loop (`write-spec` → `implement-spec` → `close-spec`). Too big to adopt at once, and its verification leans on the target repo already having good tests.
- **Where it can fail:** agents under-report decisions, and the ledger is only as good as the baseline it checks against. A blind eval run on 3 of its 12 cases passed all 3 (lucky timeout fix marked unsound, unused dependency caught, tree untouched).
- **Revisit when:** `slice-spec` exists, since clearer slices should shorten the ledger.

### 2026-11-06: Position the pack as "Agent skill blocks for software factories"

- **Decision:** new slogan, hero image, and README story. The README's first lines say the blocks train the human part of the factory and check what agents decided.
- **Why:** "software factory" is a term engineers recognize. Hexagon blocks in the hero match the "blocks" idea.
- **Turned down:** dzhng's exact line ("AI skills for building software factories"). It's their identity, and it would promise a build loop this pack doesn't have yet.
- **Where it can fail:** readers expect build-loop skills and find coaching skills. `decision-checker` and `slice-spec` close that gap.
- **Revisit when:** the factory blocks outnumber the coaching skills.

### 2026-11-06: Agents check before the human reviews

- **Decision:** for build, review, or research work, independent subagents draft, verify, and critique first; the human gets the checked result plus a decisions ledger. Recorded in `AGENTS.md`.
- **Why:** human attention is the bottleneck. A fresh agent with no stake in the work catches what the author misses. It caught two overstated claims and copied wording in this pack's own README.
- **Where it can fail:** stacked reviews burn tokens and time without adding proof. Keep one gate per task (design rule 3).

### 2026-11-06: Marketplace name `hien-skills`

- **Decision:** the Claude Code marketplace is `hien-skills`; the plugin stays `agent-skills`.
- **Why:** `agent-skills` is reserved for official Anthropic marketplaces. `claude plugin validate` passes it, but adding the marketplace fails. Caught by a real install test.

### Sources

- [dzhng/skills](https://github.com/dzhng/skills): the software factory loop, `audit-decisions`.
- [kunchenguid/firstmate](https://github.com/kunchenguid/firstmate): `VISION.md`, the agent distro and command layer.
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness): `packages/skill/skill-filesystem` (skill discovery) and `packages/experimental/hooks-claude-code` (hook bridge).
- [DeepSeek Harness post](https://x.com/deepseekharness/status/2116857257245987236), read through [MindStudio's write-up](https://www.mindstudio.ai/blog/deepseek-super-agent-harness-design) because the article itself blocks scrapers.
