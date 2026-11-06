# decision-checker in a harness

Loaded only when wiring this skill into a harness, or when a harness calls it. The same skill runs by hand (`/decision-checker`) or as a gate; the files in and out are identical either way.

## Contract

| | What | Where |
|---|---|---|
| **In: scope** | The change to check | The current branch against its base, unless the caller names a commit range or PR |
| **In: baseline** | What was actually asked | First match: a path the caller passes; `specs/<feature>/README.md` for the branch's spec; the task's intent section in its instructions (firstmate: `## Captain's intent`); the session prompt |
| **Out: ledger** | Every decision, verdict, confidence | `decisions.md` beside the spec, else at the repo root |
| **Out: handback** | What the caller reports | The ledger's "Check these first" and verdict counts, never the diff |
| **Side effects** | None | The code is untouched. Only `decisions.md` changes |

With no user present the skill follows its rule 7: baseline inferred and said so, confidence capped at medium, ledger saved without asking. It never waits.

## Three ways to make it a gate

### 1. A line in the task's instructions

Any orchestrator that writes task instructions (a firstmate brief, a spec's Next Agent Prompt, a subagent prompt) adds:

> Before reporting done, follow the `decision-checker` skill in Check mode on this branch and save `decisions.md`. Report its "Check these first" list, not the diff.

Cheapest to add. It's still a prompt, so a worker can skip it. Pair it with option 2 where you can.

### 2. A Claude Code Stop hook

`hooks/require-ledger.sh` blocks the agent from finishing once when the branch changes non-doc files but has no new or updated `decisions.md`. It then tells the agent to run this skill. It never blocks twice in a row, and it steps aside when it can't tell (no git repo, no base branch). Docs-only changes pass.

Add to the project's `.claude/settings.json`, with the path pointing at wherever this skill is installed:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/skills/decision-checker/hooks/require-ledger.sh" }
        ]
      }
    ]
  }
}
```

Set `DECISION_CHECKER_BASE` if the base branch isn't `origin/HEAD`, `origin/main`, or `origin/master`.

Limits, on purpose: it checks that a ledger exists on the branch, not that it's good or current. A ledger written early and never updated still passes, and so does any gitignored `decisions.md` on disk. Deleting a ledger never counts as writing one. Quality is the skill's job; the hook only makes sure the check happened.

### 3. A firstmate task

In a firstmate home, install this skill where workers can load it, then put the line from option 1 in the brief's `## Firstmate spec`. The brief's `## Captain's intent` is the baseline. The ledger counts as evidence for the captain, not authorization: merging still follows the project's merge authority.
