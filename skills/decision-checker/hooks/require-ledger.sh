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
# stop_hook_active=false and cap nothing.
#
# When the session's cwd is not a git repo (a home folder holding several
# repos), it checks each immediate child folder that is a git repo, and names
# every repo that needs a ledger. A repo with no base branch or no changes is
# skipped, so it still steps aside whenever it can't tell.
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
[ -z "$cwd" ] && cwd=$PWD
sid=$(field session_id)

# needs_ledger DIR: succeeds, and prints DIR<TAB>BASE, when DIR's branch changes
# code with no decisions ledger and this session hasn't already been nudged
# for the same changes.
needs_ledger() {
  local repo=$1 base ref mb changed mark key
  g() { git -C "$repo" -c core.quotePath=false "$@"; }
  g rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 1

  base=${DECISION_CHECKER_BASE:-}
  if [ -z "$base" ]; then
    for ref in origin/HEAD origin/main origin/master; do
      if g rev-parse --verify --quiet "$ref" >/dev/null; then base=$ref; break; fi
    done
  fi
  [ -z "$base" ] && return 1
  mb=$(g merge-base HEAD "$base" 2>/dev/null) || return 1

  # Deleted files don't count: removing decisions.md is not writing one.
  changed=$( {
    g diff --name-only --diff-filter=d "$mb" HEAD
    g diff --name-only --diff-filter=d HEAD
    g ls-files --others --exclude-standard
  } | sort -u )

  [ -z "$changed" ] && return 1
  printf '%s\n' "$changed" | grep -q '\(^\|/\)decisions\.md$' && return 1
  # A gitignored ledger never shows in git, so accept one on disk.
  g ls-files --others --ignored --exclude-standard | grep -q '\(^\|/\)decisions\.md$' && return 1
  printf '%s\n' "$changed" | grep -qv '\.md$' || return 1

  # Self-limit: one nudge per session per set of changes.
  if [ -n "$sid" ]; then
    mark="$(g rev-parse --absolute-git-dir)/decision-checker-gate/$(printf '%s' "$sid" | tr -c 'A-Za-z0-9._-' '_')"
    key=$( { g rev-parse HEAD 2>/dev/null; printf '%s\n' "$changed"; } | g hash-object --stdin)
    [ "$(cat "$mark" 2>/dev/null)" = "$key" ] && return 1
    mkdir -p "$(dirname "$mark")" && printf '%s' "$key" > "$mark"
  fi
  printf '%s\t%s\n' "$(g rev-parse --show-toplevel)" "$base"
}

found=""
if git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  found=$(needs_ledger "$cwd")
else
  for d in "$cwd"/*/; do
    [ -e "$d.git" ] || continue
    line=$(needs_ledger "${d%/}") && found="$found$line"$'\n'
  done
fi
[ -z "$found" ] && exit 0

FOUND="$found" python3 -c 'import json, os
rows = [l.split("\t") for l in os.environ["FOUND"].splitlines() if l.strip()]
if len(rows) == 1:
    repo, base = rows[0]
    where = "This branch (" + repo + ") changes code but has no decisions ledger."
    scope = "everything since the branch left " + base
    it = "it"
else:
    where = ("These repos have branches that change code but have no decisions ledger: "
             + "; ".join(r + " (base " + b + ")" for r, b in rows) + ". Check each one separately.")
    scope = "everything since each branch left its base"
    it = "each branch"
print(json.dumps({"decision": "block", "reason": (
    where + " Before finishing, hand " + it + " to the "
    "decision-checker subagent (Agent tool: decision-checker, or agent-skills:decision-checker "
    "from the plugin) so a reviewer with fresh context checks it. Give it the scope (" + scope + ": its commits plus uncommitted and untracked files), the baseline (the spec path, the issue, or the user\x27s request quoted) "
    "and every place you had to guess. It saves decisions.md. Then hand back its Check these first "
    "list, not the diff. If no such subagent is installed, run the decision-checker skill yourself "
    "in Check mode (no user is present: follow its rule 7) and save decisions.md.")}))'
exit 0
