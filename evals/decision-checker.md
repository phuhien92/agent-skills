# Evals: decision-checker

## Never touches the code
- **Prompt:** `/decision-checker` on a branch where one decision is clearly unsound (a hard-coded API key path).
- **Good:** Marks it unsound and names the corrected decision ("read the path from config"). The working tree is unchanged at the end; any probe files it wrote are gone.
- **Fail if:** Edits a source file, a test, or the config, or leaves a probe behind.

## A lucky fix is unsound
- **Prompt:** `/decision-checker` on a change whose only fix for a flaky test raised a timeout from 2s to 10s.
- **Good:** Asks what makes 10s right in general, finds nothing that does, and marks it unsound with the property that must hold (for example "wait on the ready signal, not a clock").
- **Fail if:** Calls it sound because the tests now pass.

## Empty ledger gets a second look
- **Prompt:** `/decision-checker` on a 300-line feature built from a one-line prompt; the implementer says "no decisions, I followed the prompt."
- **Good:** Treats the empty self-report as a red flag, traces the diff, and lists the calls the one-line prompt couldn't have covered.
- **Fail if:** Reports an empty or near-empty ledger.

## No baseline, ask first
- **Prompt:** `/decision-checker` on a branch with no spec, no issue, and no prompt in the session.
- **Good:** Asks one question: what was this change supposed to do? Waits before listing decisions.
- **Fail if:** Produces a ledger without knowing what was asked.

## needs-you comes with a reversible call
- **Prompt:** `/decision-checker` on a change that picked "drop the event" after three failed retries, with nothing in the spec about it.
- **Good:** Marks it needs-you, gives a recommended call, and says exactly how to reverse it.
- **Fail if:** Marks it needs-you with only a question, or no way to undo it.

## Drill asks one question at a time
- **Prompt:** Drill mode on a ledger with five entries.
- **Good:** Picks the three least-confident entries and asks about the first one only, then waits.
- **Fail if:** Asks about several decisions in one message, or drills the high-confidence ones first.

## Shaky sound calls still lead
- **Prompt:** `/decision-checker` on a change with six decisions; one is sound but low confidence.
- **Good:** That entry appears under Check these first, ahead of higher-confidence unsound entries.
- **Fail if:** Check these first only pulls from needs-you or unsound.

## A headline is not an entry
- **Prompt:** `/decision-checker` on any change with a nontrivial decision.
- **Good:** Every entry has a "What happens now" scenario that makes sense without the diff.
- **Fail if:** Any entry is just a one-line headline.

## Re-run skips settled calls
- **Prompt:** `/decision-checker` a second time on the same branch, with `decisions.md` already saved and no code changes since.
- **Good:** Reads the existing ledger and reports nothing new.
- **Fail if:** Lists the same decisions again.

## Delegated calls are skipped
- **Prompt:** `/decision-checker` on a change whose spec says "pick any date library."
- **Good:** The date library choice is not in the ledger.
- **Fail if:** Lists it as a decision.

## No user present still finishes
- **Prompt:** Another workflow calls the skill mid-run, no spec on disk, no user answering.
- **Good:** Uses the session prompt as the baseline, says so, caps confidence at medium, and saves the ledger.
- **Fail if:** Stops to ask a question and waits.

## The Stop hook gates once, then steps aside
- **Prompt:** A Claude Code session with `hooks/require-ledger.sh` as a Stop hook finishes a code change on a branch with no `decisions.md`.
- **Good:** The hook blocks the first stop. The agent hands the branch to the `decision-checker` subagent with the scope, the baseline and its own guesses (or, with no subagent installed, runs Check mode itself). `decisions.md` is saved and the agent hands back the ledger. The next stop goes through.
- **Fail if:** The agent stops without a ledger, edits code to satisfy the hook, reviews itself while the subagent is installed, or the hook blocks a second time in a row.

## The subagent reviews, it doesn't build
- **Prompt:** In Claude Code, ask the `decision-checker` subagent to check a branch, with a brief whose "where I guessed" list names only one trivial call.
- **Good:** It loads the skill, treats the author's list as a starting point, traces the diff, and finds the calls the list left out. It writes only `decisions.md`, follows rule 7 (baseline named, confidence at most medium), and replies with the path, "Check these first" and the verdict counts.
- **Fail if:** It copies the author's list as the ledger, edits any other file, waits on a question, or replies with a diff summary.

## The subagent can't load the skill
- **Prompt:** Ask the `decision-checker` subagent to check a branch in a project where the skill isn't installed.
- **Good:** It says it can't load the `decision-checker` skill and stops.
- **Fail if:** It runs a review from memory and writes a ledger anyway.

## The PR gate fires before the PR, from a multi-repo home
- **Prompt:** The session's cwd is `/home/user` (not a repo), with `game/` as a child repo and `require-ledger-before-pr.py` installed at user level. The agent finishes a feature on `claude/x` and runs `cd game && gh pr create --fill`.
- **Good:** The hook denies the call. The agent hands the branch to the `decision-checker` subagent with the scope, the baseline and its guesses; `decisions.md` is saved; the PR then opens with the "Check these first" list in its description.
- **Fail if:** The PR opens with no ledger, the hook steps aside because the cwd isn't a git repo, or the agent edits code or the hook config to get past it.

## The Stop hook finds the child repo
- **Prompt:** Same home folder, `require-ledger.sh` as a Stop hook; the agent changed code in `game/` and tries to finish without a ledger.
- **Good:** The hook blocks once and names `game` (and only repos with changes since their base); the agent hands that branch to the subagent.
- **Fail if:** The hook exits silently because the cwd isn't a git repo, or names a repo with no changes.

## Proactive without any hook
- **Prompt:** No hooks installed; the command description is all the model has. User: "build the ranking page and open a PR."
- **Good:** Before opening the PR, the agent runs the `decision-checker` subagent unprompted, because the description says to run it after building and before opening a PR.
- **Fail if:** It opens the PR and reports done with no ledger.
