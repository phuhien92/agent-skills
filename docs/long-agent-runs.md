# Long agent runs

Four habits for agent work that runs longer than a few minutes, especially from a folder that holds several repos. None of them is a skill: they are how the session around the skills should behave. `AGENTS.md` points here.

## Keep the human posted

In an interactive session, send a one- or two-line status:

- at each phase change: brief agreed, mockup ready, tests green, ledger written, PR open;
- at least every ~10 minutes of tool work, even mid-phase;
- when background subagents start or finish.

Each status says what's done, what's next, and anything you need from the person. One line is enough; a status is not a report.

Why: the pack's blocks were built for unattended runs ("never block a run"), and that habit carried into interactive sessions as long silences. A person watching a session can't tell a slow step from a stuck one. In an unattended run, the handback and the ledger replace these updates.

Ask-or-go: ask before starting only for a new character or look, a change to rules or balance, or a pasted spec (`reference-originality` and `slice-spec` cover those). Otherwise go, and list your guesses in the ledger.

## Say what was checked, in three groups

A report is only as good as the line between what was seen and what merely didn't fail. In every handback and PR body, sort each claim into one of three groups, and list anything that never ran as **not run**:

- **Verified:** you saw, heard or measured the result. A screenshot you read, a number you compared, a check that ran to the end and printed its pass line.
- **Ran without error:** it built, the suite passed, the script didn't throw, but nobody looked at what it produced. Say so in those words.
- **Needs a human:** you can't check it from here. How music sounds on a phone speaker, how a control feels, a real iPhone, a judgement of taste. Say who should check it and how.

Rules that come with it:

- A check that didn't run is not a pass. A device suite that exited because its port was busy, a step skipped for a missing key, a test filtered out: list it as **not run**, with the reason, and rerun it or hand it over.
- A one-line status doesn't need the full sort; it only must not claim a pass it didn't see.
- Read the output, not the exit code. A wrapper loop can print `exit 0` after the real command failed.
- When two runs disagree (flaky), say both happened. "Passed on the second run" is a different claim from "passed".
- In a PR body, put anything not re-run on the final commit under its own line ("passed before the merge; not re-run on the merged result").

Why: an agent's "done" is read as "checked". The worst report is a confident green made of skipped or half-run checks, because nobody goes back to look. Idea from op7418/guizang-game-skill (AGPL-3.0); no text copied.

## Worktrees when the cwd isn't a git repo

A session started in a home folder (`/home/user` holding `game/`, `notes/`, `agent-skills/`) can't use built-in worktree isolation: it needs the session's cwd inside a git repo. Make the worktree by hand, from the repo, on a branch off the remote base:

```bash
git -C /home/user/<repo> fetch origin
git -C /home/user/<repo> worktree add <scratch>/wt/<slug> -b claude/<slug> origin/main
cd <scratch>/wt/<slug> && npm ci   # or the repo's own install step
```

`<scratch>` is the session's scratchpad (or any folder outside the repo). The install step matters: a worktree shares git history, not `node_modules`, so tests fail in it until dependencies are installed there.

Give a subagent the absolute path, and say "work only in `<scratch>/wt/<slug>`; run git with `-C <that path>`", because a subagent's working directory resets between shell calls. Remove it when the branch is pushed: `git -C /home/user/<repo> worktree remove <scratch>/wt/<slug>`.

## Fix the fetch refspec before trusting "unpushed commits"

Some clones fetch named branches only. Check:

```bash
git -C <repo> config --get-all remote.origin.fetch
```

If that lists one line per branch (`+refs/heads/claude/battle-moments:refs/remotes/origin/claude/battle-moments`) and no `+refs/heads/*:refs/remotes/origin/*`, a branch you create and push never gets an `origin/<branch>` ref. Fix it once per repo:

```bash
git -C <repo> config --add remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git -C <repo> fetch origin
```

Why a Stop hook needs it: a hook that warns about unpushed work compares the branch with `origin/<branch>`, and falls back to `origin/HEAD` when that ref is missing. With single-branch refspecs the ref is always missing for new branches, so every commit since `main` reads as unpushed, right after a successful push, on every stop. The decision-checker hooks diff against `origin/main` (or `origin/<the PR's base>`) too, so a stale or missing remote ref skews their change list the same way. For one branch without changing the config: `git -C <repo> fetch origin <branch>:refs/remotes/origin/<branch>` right after `git push -u origin <branch>`.
