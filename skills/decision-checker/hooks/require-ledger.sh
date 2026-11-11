#!/usr/bin/env bash
# decision-checker gate: a Claude Code Stop hook. Also runs unchanged in
# DeepSeek Harness through its dsh-hooks-claude-code bridge.
#
# Blocks the agent from finishing once, when the branch changes non-doc files
# but no decisions.md was written or updated. The agent is told to hand the
# branch to the decision-checker subagent (agents/decision-checker.md), so a
# reviewer with fresh context checks it, and to run the skill itself only
# when no such subagent is installed. It self-limits: it never blocks twice in a row
# (stop_hook_active) and never twice in one session for the same changes
# (a marker in the git dir), because some harnesses always send
# stop_hook_active=false and cap nothing. It steps aside whenever it can't
# tell: no git repo, no base branch.
#
# Settings (env, all optional):
#   DECISION_CHECKER_BASE  base ref to diff against (default: origin/HEAD,
#                          then origin/main, then origin/master)
set -u

input=$(cat)
field() {
  printf '%s' "$input" | python3 -c "import json,sys
try: v=json.load(sys.stdin).get('$1')
except Exception: v=None
print('' if v is None else str(v))"
}

case "$(field stop_hook_active)" in true|True) exit 0 ;; esac

cwd=$(field cwd)
[ -n "$cwd" ] && cd "$cwd" 2>/dev/null
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

base=${DECISION_CHECKER_BASE:-}
if [ -z "$base" ]; then
  for ref in origin/HEAD origin/main origin/master; do
    if git rev-parse --verify --quiet "$ref" >/dev/null; then base=$ref; break; fi
  done
fi
[ -z "$base" ] && exit 0
mb=$(git merge-base HEAD "$base" 2>/dev/null) || exit 0

g() { git -c core.quotePath=false "$@"; }
# Deleted files don't count: removing decisions.md is not writing one.
changed=$( {
  g diff --name-only --diff-filter=d "$mb" HEAD
  g diff --name-only --diff-filter=d HEAD
  g ls-files --others --exclude-standard
} | sort -u )

[ -z "$changed" ] && exit 0
printf '%s\n' "$changed" | grep -q '\(^\|/\)decisions\.md$' && exit 0
# A gitignored ledger never shows in git, so accept one on disk.
g ls-files --others --ignored --exclude-standard | grep -q '\(^\|/\)decisions\.md$' && exit 0
printf '%s\n' "$changed" | grep -qv '\.md$' || exit 0

# Self-limit: one nudge per session per set of changes.
sid=$(field session_id)
if [ -n "$sid" ]; then
  mark="$(git rev-parse --git-dir)/decision-checker-gate/$(printf '%s' "$sid" | tr -c 'A-Za-z0-9._-' '_')"
  key=$( { git rev-parse HEAD 2>/dev/null; printf '%s\n' "$changed"; } | git hash-object --stdin)
  [ "$(cat "$mark" 2>/dev/null)" = "$key" ] && exit 0
  mkdir -p "$(dirname "$mark")" && printf '%s' "$key" > "$mark"
fi

BASE="$base" python3 -c 'import json, os
base = os.environ["BASE"]
print(json.dumps({"decision": "block", "reason": (
    "This branch changes code but has no decisions ledger. Before finishing, hand it to the "
    "decision-checker subagent (Agent tool: decision-checker, or agent-skills:decision-checker "
    "from the plugin) so a reviewer with fresh context checks it. Give it the scope (this branch "
    "against " + base + "), the baseline (the spec path, the issue, or the user\x27s request quoted) "
    "and every place you had to guess. It saves decisions.md. Then hand back its Check these first "
    "list, not the diff. If no such subagent is installed, run the decision-checker skill yourself "
    "in Check mode (no user is present: follow its rule 7) and save decisions.md.")}))'
exit 0
