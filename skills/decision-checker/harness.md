# decision-checker in a harness

Loaded only when wiring this skill into a harness, or when a harness calls it. The same skill runs by hand (`/decision-checker`) or as a gate; the files in and out are identical either way.

## Contract

| | What | Where |
|---|---|---|
| **In: scope** | The change to check | The current branch against its base, unless the caller names a commit range or PR |
| **In: baseline** | What was actually asked | First match: a path the caller passes; the spec whose README names this branch (`specs/<feature>/README.md` plus its `slices/`, whose **Delegated to the worker** lists are skipped); the task's intent section in its instructions (firstmate: `## Captain's intent`); the session prompt |
| **Out: ledger** | Every decision, verdict, confidence | `decisions.md` beside the spec, else at the repo root |
| **Out: handback** | What the caller reports | The ledger's "Check these first" and verdict counts, never the diff |
| **Side effects** | None | The code is untouched. Only `decisions.md` changes |

With no user present the skill follows its rule 7: baseline inferred and said so, confidence capped at medium, ledger saved without asking. It never waits.

## Who runs the check: a reviewer subagent

`.claude/agents/decision-checker.md` is a Claude Code subagent that runs this skill with fresh context. The author is the worst reviewer of its own work, so in Claude Code the check runs there, not in the session that wrote the code. The plugin ships it as `agent-skills:decision-checker`; in a project, copy it into the project's `.claude/agents/`.

Hand it a brief with three things:

- **Scope:** the branch, commit range, or PR. From the hook, that's everything since the branch left its base, uncommitted and untracked files included.
- **Baseline:** the spec path, the issue, or the user's request quoted.
- **Where the author guessed:** the author's own list. The subagent treats it as step 2 of Check, never as the ledger.

It has no way to ask a user, so rule 7 always applies there. To answer questions yourself, run `/decision-checker` in your own session instead.

To review someone's PR: check out its branch and ask for the subagent with the PR as the scope and its linked issue as the baseline.

## Five ways to make it a gate

### 1. A line in the task's instructions

Any orchestrator that writes task instructions (a firstmate brief, a spec's Next Agent Prompt, a subagent prompt) adds:

> Before reporting done, follow the `decision-checker` skill in Check mode on this branch and save `decisions.md`. Report its "Check these first" list, not the diff.

Cheapest to add. It's still a prompt, so a worker can skip it. Pair it with option 2 or 3 where you can.

### 2. A Claude Code Stop hook

`hooks/require-ledger.sh` blocks the agent from finishing once when the branch changes non-doc files but has no new or updated `decisions.md`. It then tells the agent to hand the branch to the reviewer subagent (above), and to run this skill itself only when that subagent isn't installed. It never blocks twice in a row, and it steps aside when it can't tell (no base branch, no changes). Docs-only changes pass.

When the session's cwd isn't a git repo (a home folder holding several repos), it checks each immediate child folder that is one, and names every repo whose branch needs a ledger. It looks one level down only, to stay cheap.

Install the subagent too, or the hook falls back to a self-review. For one project, add to its `.claude/settings.json`, with the path pointing at wherever this skill is installed:

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

Set `DECISION_CHECKER_BASE` if the base branch isn't `origin/HEAD`, `origin/main`, or `origin/master`. Stacked PRs (one branch built on another) need it set to the branch below, or the ledger check counts the lower branch's changes too.

It limits itself: never twice in a row, and never twice in one session for the same set of changed files (a marker under `.git/decision-checker-gate/`). Some harnesses never report a repeat stop, so the hook can't rely on the harness to stop it.

Limits, on purpose: it checks that a ledger exists on the branch, not that it's good or current. A ledger written early and never updated still passes, and so does any gitignored `decisions.md` on disk. Deleting a ledger never counts as writing one. Quality is the skill's job; the hook only makes sure the check happened.

Its weak spot: a Stop hook fires when the turn ends. An agent that opens a PR mid-turn has already opened it by then. Option 3 closes that gap.

### 3. A Claude Code PreToolUse hook before the PR

`hooks/require-ledger-before-pr.py` denies opening a pull request while the PR's branch changes code and has no `decisions.md`. It fires on `gh pr create` in Bash and on a GitHub MCP `create_pull_request` tool, before the PR exists. The deny reason tells the agent to hand the branch to the reviewer subagent, then open the PR with the ledger's "Check these first" list in the description. Same ledger rule as option 2; docs-only branches pass.

It finds the repo from the command's `cd <path>` or `--repo owner/name`, or from the MCP call's `owner` and `repo`, looking in the session's cwd and its immediate child folders. For a branch other than the one checked out (`--head`, or the MCP call's `head`), it reads that branch's commits only. When it can't find the clone, the branch, or a base, it lets the call through and adds a one-line note to Claude's context saying no check ran. It never blocks on a guess, and it never self-limits: the PR waits until a ledger exists. To skip it for one PR, the person removes or disables the hook (`/hooks`); nothing the agent types gets past it.

Its output follows the PreToolUse format in the [hooks reference](https://code.claude.com/docs/en/hooks) ("PreToolUse decision control"): exit 0 and print `hookSpecificOutput` with `permissionDecision: "deny"` and a `permissionDecisionReason`, which Claude reads. Checked against that page on 2026-11-13.

Not covered: PRs opened through `gh api`, a browser, or another tool name. Add a matcher if you use one.

### Install both at user level (multi-repo sessions)

When you start Claude Code in a folder that holds several repos, no single project's `.claude/settings.json` is read for all of them. Put the hooks in `~/.claude/settings.json` instead; they then run in every session on that machine. Cloud sessions don't read your local user settings, so there the gate goes in each repo's `.claude/settings.json` or the environment's setup. Point the paths at your clone (or a symlink such as `~/.claude/skills/decision-checker`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(gh pr create *)",
            "command": "python3 \"$HOME\"/src/agent-skills/skills/decision-checker/hooks/require-ledger-before-pr.py"
          }
        ]
      },
      {
        "matcher": "mcp__.*__create_pull_request",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$HOME\"/src/agent-skills/skills/decision-checker/hooks/require-ledger-before-pr.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "bash \"$HOME\"/src/agent-skills/skills/decision-checker/hooks/require-ledger.sh" }
        ]
      }
    ]
  }
}
```

The `if` filter keeps the Bash hook from starting Python on every command; `Bash(gh pr create *)` also matches a bare `gh pr create`. The regex matcher catches both `mcp__github__create_pull_request` and a plugin-scoped GitHub server's tool. Merge these entries into any hooks you already have rather than replacing the file, and copy `.claude/agents/decision-checker.md` to `~/.claude/agents/` so the deny and block reasons have a reviewer to hand to.

### 4. A firstmate task

In a firstmate home, install this skill where workers can load it, then put the line from option 1 in the brief's `## Firstmate spec`. The brief's `## Captain's intent` is the baseline. The ledger counts as evidence for the captain, not authorization: merging still follows the project's merge authority.

### 5. DeepSeek Harness

DeepSeek Harness (`dsh`) discovers `<name>/SKILL.md` bundles in `<project>/.agents/skills` and `~/.agents/skills`, so this skill loads as-is. For the gate, mount its `@deepseek-ai/dsh-hooks-claude-code` bridge (experimental) and point `configPath` at the settings file from option 2:

```yaml
- name: '@deepseek-ai/dsh-hooks-claude-code'
  config:
    configPath: ./.claude/settings.json
    projectDir: .
```

Claude Code subagents don't carry over, so there the hook's fallback applies: the agent runs the skill itself. The bridge maps `Stop` to its `agent/turn-stopping` checkpoint, honors `{"decision": "block"}`, and passes `cwd` and `session_id`. It always sends `stop_hook_active: false` and has no cap on forced continuations, which is why the hook limits itself per session.
