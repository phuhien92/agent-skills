"""decision-checker's two gates: the Stop hook and the PreToolUse PR hook.

Builds throwaway git repos with an origin, then feeds each hook the JSON
Claude Code sends and reads its decision.
Run: python3 -m unittest discover -s tools
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOKS = ROOT / "skills" / "decision-checker" / "hooks"
STOP = HOOKS / "require-ledger.sh"
PR = HOOKS / "require-ledger-before-pr.py"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}
ENV.pop("DECISION_CHECKER_BASE", None)


def sh(cwd: Path, *args: str) -> str:
    return subprocess.run(args, cwd=cwd, env=ENV, check=True, capture_output=True, text=True).stdout


@unittest.skipUnless(shutil.which("git") and shutil.which("bash"), "needs git and bash")
class LedgerHooksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def make_repo(self, name: str, slug: str) -> Path:
        """A clone of a fresh origin, on branch claude/x, remote URL pointing at github.com/<slug>."""
        bare = Path(self.tmp.name) / f"{name}.git"
        sh(Path(self.tmp.name), "git", "init", "-q", "--bare", "-b", "main", str(bare))
        repo = self.home / name
        sh(self.home, "git", "clone", "-q", str(bare), name)
        (repo / "README.md").write_text("hi\n")
        sh(repo, "git", "add", ".")
        sh(repo, "git", "commit", "-q", "-m", "init")
        sh(repo, "git", "push", "-q", "origin", "HEAD:main")
        sh(repo, "git", "remote", "set-head", "origin", "main")
        sh(repo, "git", "remote", "set-url", "origin", f"https://github.com/{slug}.git")
        sh(repo, "git", "checkout", "-q", "-b", "claude/x")
        return repo

    def commit(self, repo: Path, rel: str, text: str = "x\n") -> None:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        sh(repo, "git", "add", rel)
        sh(repo, "git", "commit", "-q", "-m", f"add {rel}")

    def run_hook(self, script: Path, payload: dict) -> dict | None:
        cmd = ["bash", str(script)] if script.suffix == ".sh" else ["python3", str(script)]
        out = subprocess.run(cmd, input=json.dumps(payload), env=ENV, capture_output=True,
                             text=True, check=True).stdout.strip()
        return json.loads(out) if out else None

    def stop(self, cwd: Path, sid: str = "s1") -> dict | None:
        return self.run_hook(STOP, {"hook_event_name": "Stop", "cwd": str(cwd), "session_id": sid,
                                    "stop_hook_active": False})

    def pr_bash(self, cwd: Path, command: str) -> dict | None:
        return self.run_hook(PR, {"hook_event_name": "PreToolUse", "cwd": str(cwd),
                                  "tool_name": "Bash", "tool_input": {"command": command}})

    def pr_mcp(self, cwd: Path, **tool_input: str) -> dict | None:
        return self.run_hook(PR, {"hook_event_name": "PreToolUse", "cwd": str(cwd),
                                  "tool_name": "mcp__github__create_pull_request",
                                  "tool_input": tool_input})

    def decision(self, out: dict | None) -> str | None:
        return None if out is None else out["hookSpecificOutput"].get("permissionDecision")

    # Stop hook

    def test_stop_blocks_code_without_ledger_once(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        out = self.stop(repo)
        self.assertEqual(out["decision"], "block")
        self.assertIn(str(repo), out["reason"])
        self.assertIsNone(self.stop(repo), "a second stop in the same session must pass")

    def test_stop_passes_with_ledger(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        self.commit(repo, "decisions.md")
        self.assertIsNone(self.stop(repo))

    def test_stop_from_a_home_folder_checks_child_repos(self) -> None:
        game = self.make_repo("game", "acme/game")
        self.make_repo("clean", "acme/clean")
        self.commit(game, "src/app.ts")
        out = self.stop(self.home)
        self.assertEqual(out["decision"], "block")
        self.assertIn(str(game), out["reason"])
        self.assertNotIn("clean", out["reason"])

    def test_stop_names_every_child_repo_that_needs_a_ledger(self) -> None:
        a, b = self.make_repo("a", "acme/a"), self.make_repo("b", "acme/b")
        self.commit(a, "x.py")
        self.commit(b, "y.py")
        out = self.stop(self.home)
        self.assertIn(str(a), out["reason"])
        self.assertIn(str(b), out["reason"])

    def test_stop_home_with_no_changes_passes(self) -> None:
        self.make_repo("game", "acme/game")
        self.assertIsNone(self.stop(self.home))

    # PreToolUse PR hook

    def test_pr_denied_without_ledger(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        out = self.pr_bash(repo, 'gh pr create --title "x" --body "y"')
        self.assertEqual(self.decision(out), "deny")
        self.assertIn("claude/x", out["hookSpecificOutput"]["permissionDecisionReason"])

    def test_pr_allowed_with_ledger(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        self.commit(repo, "specs/x/decisions.md")
        self.assertIsNone(self.pr_bash(repo, "gh pr create --fill"))

    def test_pr_allowed_for_docs_only(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "docs/notes.md")
        self.assertIsNone(self.pr_bash(repo, "gh pr create --fill"))

    def test_other_bash_commands_pass(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        self.assertIsNone(self.pr_bash(repo, "gh pr view 3"))

    def test_pr_from_home_follows_cd(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        out = self.pr_bash(self.home, f"cd {repo} && gh pr create --fill")
        self.assertEqual(self.decision(out), "deny")

    def test_pr_from_home_follows_repo_flag(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        out = self.pr_bash(self.home, "gh pr create -R acme/game --head claude/x --fill")
        self.assertEqual(self.decision(out), "deny")

    def test_mcp_pr_from_home(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        out = self.pr_mcp(self.home, owner="acme", repo="game", head="claude/x", base="main", title="t")
        self.assertEqual(self.decision(out), "deny")
        self.commit(repo, "decisions.md")
        self.assertIsNone(self.pr_mcp(self.home, owner="acme", repo="game", head="claude/x", base="main"))

    def test_mcp_pr_for_another_branch_reads_that_branch(self) -> None:
        repo = self.make_repo("game", "acme/game")
        self.commit(repo, "src/app.ts")
        sh(repo, "git", "checkout", "-q", "main")
        out = self.pr_mcp(self.home, owner="acme", repo="game", head="claude/x", base="main")
        self.assertEqual(self.decision(out), "deny")

    def test_unknown_repo_lets_the_call_through_with_a_note(self) -> None:
        out = self.pr_mcp(self.home, owner="acme", repo="nowhere", head="claude/x")
        self.assertIsNone(self.decision(out))
        self.assertIn("no local clone", out["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__":
    unittest.main()
