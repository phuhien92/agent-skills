#!/usr/bin/env bash
# decision-checker gate: a Claude Code Stop hook.
#
# Blocks the agent from finishing once, when the branch changes non-doc files
# but no decisions.md was written or updated. The agent is told to run
# decision-checker first. It never blocks twice in a row (stop_hook_active),
# and it steps aside whenever it can't tell: no git repo, no base branch.
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

cat <<'EOF'
{"decision": "block", "reason": "This branch changes code but has no decisions ledger. Before finishing, run the decision-checker skill in Check mode on this branch (no user is present: follow its rule 7) and save decisions.md. Then hand back the ledger, not the diff."}
EOF
exit 0
