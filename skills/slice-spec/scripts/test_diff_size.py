"""Tests for diff_size.py's move classifier (slice 02 of specs/diff-size/).

Each test builds a tiny git repo in a temp folder; nothing reads real history.
Run: python3 -m unittest discover -s skills/slice-spec/scripts
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diff_size as d  # noqa: E402

# Long enough lines that every block clears git's 20-alphanumeric-character floor.
BLOCK = [
    "def calculate_invoice_total(items, tax_rate):",
    "    subtotal = sum(item.price * item.quantity for item in items)",
    "    discount = apply_customer_discount(subtotal, items)",
    "    taxed = (subtotal - discount) * (1 + tax_rate)",
    "    return round(taxed, 2)",
]
OTHER = [
    "def render_customer_statement(customer, invoices):",
    "    header = format_statement_header(customer.name, customer.address)",
    "    rows = [format_statement_row(invoice) for invoice in invoices]",
    "    return header + rows",
]


def lines(*groups: list[str]) -> str:
    return "".join(line + "\n" for group in groups for line in group)


def indent(block: list[str], by: str = "    ") -> list[str]:
    return [by + line for line in block]


class Repo:
    def __init__(self, root: Path):
        self.root = root
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_DATE="2026-01-01T00:00:00Z", GIT_COMMITTER_DATE="2026-01-01T00:00:00Z")
        self.env = env
        self.run("init", "-q", "-b", "main")
        self.run("config", "user.email", "t@example.com")
        self.run("config", "user.name", "t")
        self.run("config", "commit.gpgsign", "false")

    def run(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.root, env=self.env,
                              capture_output=True, text=True, check=True).stdout

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, message: str = "c") -> str:
        self.run("add", "-A")
        self.run("commit", "-q", "--allow-empty", "-m", message)
        return self.run("rev-parse", "HEAD").strip()


def totals(files: list[d.FileCount]) -> tuple[int, int, int, int]:
    return (sum(f.new for f in files), sum(f.moved for f in files),
            sum(f.deleted for f in files), sum(f.moved_out for f in files))


class ClassifierTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self.tmp.name))
        # diff_size runs git itself; keep the user's global config out of every test.
        self.old_env = dict(os.environ)
        os.environ.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.old_env)
        self.tmp.cleanup()

    def count(self, commit: str) -> tuple[int, int, int, int]:
        return totals(d.count_commit(self.repo.root, commit))

    def test_new_code_is_new(self):
        self.repo.write("a.py", lines(OTHER))
        self.repo.commit()
        self.repo.write("a.py", lines(OTHER, BLOCK))
        self.assertEqual(self.count(self.repo.commit()), (5, 0, 0, 0))

    def test_pure_move_between_files(self):
        self.repo.write("a.py", lines(OTHER, BLOCK))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"]))
        self.repo.commit()
        self.repo.write("a.py", lines(OTHER))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"], BLOCK))
        self.assertEqual(self.count(self.repo.commit()), (0, 5, 0, 5))

    def test_reindented_move_counts_as_moved(self):
        self.repo.write("a.py", lines(OTHER, BLOCK))
        self.repo.write("b.py", lines(["class InvoiceService:"]))
        self.repo.commit()
        self.repo.write("a.py", lines(OTHER))
        self.repo.write("b.py", lines(["class InvoiceService:"], indent(BLOCK)))
        self.assertEqual(self.count(self.repo.commit()), (0, 5, 0, 5))

    def test_move_plus_one_edited_line(self):
        self.repo.write("a.py", lines(OTHER, BLOCK))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"]))
        self.repo.commit()
        edited = list(BLOCK)
        edited[2] = "    discount = apply_loyalty_discount(subtotal, items, customer_tier)"
        self.repo.write("a.py", lines(OTHER))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"], edited))
        new, moved, deleted, moved_out = self.count(self.repo.commit())
        self.assertEqual(new, 1)
        self.assertEqual(moved, 4)
        self.assertEqual(deleted + moved_out, 5)

    def test_plain_deletion(self):
        self.repo.write("a.py", lines(OTHER, BLOCK))
        self.repo.commit()
        self.repo.write("a.py", lines(OTHER))
        self.assertEqual(self.count(self.repo.commit()), (0, 0, 5, 0))

    def test_pure_rename_counts_every_line_as_moved(self):
        self.repo.write("old/name.py", lines(OTHER, BLOCK))
        self.repo.commit()
        (self.repo.root / "new").mkdir()
        self.repo.run("mv", "old/name.py", "new/name.py")
        files = d.count_commit(self.repo.root, self.repo.commit())
        self.assertEqual(totals(files), (0, 9, 0, 9))
        self.assertEqual((files[0].old_path, files[0].new_path), ("old/name.py", "new/name.py"))

    def test_rename_with_an_edit_keeps_its_unchanged_lines_as_moved(self):
        self.repo.write("old/name.py", lines(OTHER, BLOCK))
        self.repo.commit()
        (self.repo.root / "new").mkdir()
        self.repo.run("mv", "old/name.py", "new/name.py")
        self.repo.write("new/name.py", lines(OTHER, BLOCK, ["x = compute_new_value(1)"]))
        self.assertEqual(self.count(self.repo.commit()), (1, 9, 0, 9))

    def test_files_without_hunk_headers_keep_their_paths(self):
        self.repo.write("tool.sh", lines(["echo building the release artefacts now"]))
        self.repo.commit()
        os.chmod(self.repo.root / "tool.sh", 0o755)
        self.repo.write("empty.py", "")
        self.repo.write("blob.bin", "\0\1\2")
        files = d.count_commit(self.repo.root, self.repo.commit())
        self.assertEqual(sorted(f.path for f in files), ["blob.bin", "empty.py", "tool.sh"])
        empty = [f for f in files if f.path == "empty.py"][0]
        self.assertEqual((empty.old_path, empty.new_path), (None, "empty.py"))

    def test_user_diff_settings_cannot_change_counts(self):
        self.repo.write("a.py", lines(OTHER, BLOCK))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"]))
        self.repo.commit()
        self.repo.write("a.py", lines(OTHER))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"], BLOCK, ["x = compute_new_value(1)"]))
        commit = self.repo.commit()
        before = self.count(commit)
        attrs = self.repo.root.parent / (self.repo.root.name + "-attrs")
        attrs.write_text("*.py -diff\n")
        self.addCleanup(attrs.unlink)
        for key, value in [("diff.algorithm", "histogram"), ("diff.ignoreSubmodules", "all"),
                           ("diff.submodule", "diff"), ("core.attributesFile", str(attrs))]:
            self.repo.run("config", key, value)
        self.assertEqual(self.count(commit), before)
        self.assertEqual(before, (1, 5, 0, 5))

    def test_user_colour_and_prefix_config_cannot_change_counts(self):
        self.repo.write("a.py", lines(OTHER, BLOCK))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"]))
        self.repo.commit()
        self.repo.write("a.py", lines(OTHER))
        self.repo.write("b.py", lines(["# helpers for invoices and statements"], BLOCK, ["x = compute_new_value(1)"]))
        commit = self.repo.commit()
        before = self.count(commit)
        for key, value in [("color.diff.new", "bold magenta"), ("color.diff.newMoved", "green"),
                           ("color.diff.oldMoved", "red"), ("diff.noprefix", "true"),
                           ("diff.mnemonicPrefix", "true"), ("diff.colorMoved", "no"),
                           ("diff.colorMovedWS", "no"), ("color.ui", "never")]:
            self.repo.run("config", key, value)
        self.assertEqual(self.count(commit), before)
        self.assertEqual(before, (1, 5, 0, 5))

    def test_content_lines_starting_with_plus_or_minus_are_counted(self):
        self.repo.write("notes.diff", lines(["context line for the patch file"]))
        self.repo.commit()
        self.repo.write("notes.diff", lines(["context line for the patch file", "++ added two pluses", "--- three minuses"]))
        self.assertEqual(self.count(self.repo.commit()), (2, 0, 0, 0))

    def test_root_commit_is_sized_against_the_empty_tree(self):
        self.repo.write("a.py", lines(BLOCK))
        self.assertEqual(self.count(self.repo.commit()), (5, 0, 0, 0))

    def test_merge_is_sized_against_its_first_parent(self):
        self.repo.write("a.py", lines(OTHER))
        self.repo.commit()
        self.repo.run("checkout", "-q", "-b", "side")
        self.repo.write("b.py", lines(BLOCK))
        self.repo.commit()
        self.repo.run("checkout", "-q", "main")
        self.repo.run("merge", "-q", "--no-ff", "-m", "merge side", "side")
        merge = self.repo.run("rev-parse", "HEAD").strip()
        self.assertEqual(self.count(merge), (5, 0, 0, 0))

    def test_pathspecs_keep_excluded_files_from_supplying_moves(self):
        self.repo.write("dist/a.js", lines(BLOCK))
        self.repo.commit()
        self.repo.run("rm", "-q", "dist/a.js")
        self.repo.write("src/a.py", lines(BLOCK))
        commit = self.repo.commit()
        self.assertEqual(self.count(commit), (0, 5, 0, 5))
        only_src = totals(d.count_commit(self.repo.root, commit, ["src"]))
        self.assertEqual(only_src, (5, 0, 0, 0))

    def test_odd_path_names_are_unquoted(self):
        name = 'we"ird\tname é.py'
        self.repo.write(name, lines(BLOCK))
        files = d.count_commit(self.repo.root, self.repo.commit())
        self.assertEqual([f.path for f in files], [name])

    def test_a_range_follows_first_parents_so_merged_lines_count_once(self):
        start = self.repo.commit("start")
        self.repo.run("checkout", "-q", "-b", "side")
        self.repo.write("b.py", lines(BLOCK))
        side = self.repo.commit("side")
        self.repo.run("checkout", "-q", "main")
        self.repo.run("merge", "-q", "--no-ff", "-m", "merge side", "side")
        merge = self.repo.run("rev-parse", "HEAD").strip()
        rows = d.commits_in(self.repo.root, f"{start}..{merge}")
        self.assertEqual(rows, [merge])
        self.assertNotIn(side, rows)

    def test_commits_in_a_range_are_oldest_first(self):
        first = self.repo.commit("one")
        second = self.repo.commit("two")
        third = self.repo.commit("three")
        self.assertEqual(d.commits_in(self.repo.root, f"{first}..{third}"), [second, third])
        self.assertEqual(d.commits_in(self.repo.root, third), [third])


class BadInputTest(unittest.TestCase):
    def test_unknown_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            Repo(Path(tmp)).commit()
            with self.assertRaises(d.DiffSizeError):
                d.count_commit(Path(tmp), "no-such-commit")
            with self.assertRaises(d.DiffSizeError):
                d.commits_in(Path(tmp), "HEAD..no-such-commit")

    def test_not_a_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(d.DiffSizeError):
                d.check_repo(Path(tmp))
            with self.assertRaises(d.DiffSizeError):
                d.check_repo(Path(tmp) / "missing")

    def test_three_dot_range_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            Repo(Path(tmp)).commit()
            with self.assertRaises(d.DiffSizeError):
                d.commits_in(Path(tmp), "HEAD...HEAD")


class ParserTest(unittest.TestCase):
    def test_unquote(self):
        self.assertEqual(d.unquote('"a\\tb"'), "a\tb")
        self.assertEqual(d.unquote('"caf\\303\\251"'), "café")
        self.assertEqual(d.unquote("plain"), "plain")


if __name__ == "__main__":
    unittest.main()
