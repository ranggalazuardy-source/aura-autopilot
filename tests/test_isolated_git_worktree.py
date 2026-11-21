import subprocess
import tempfile
import unittest
from pathlib import Path

from app.services.isolated_git_worktree import GitWorktreeError, IsolatedGitWorktree


class IsolatedGitWorktreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "aura-tests@example.invalid"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "AURA Tests"], cwd=self.repo, check=True)
        target = self.repo / "app" / "services" / "sample.py"
        target.parent.mkdir(parents=True)
        target.write_text("VALUE = 1\n", encoding="utf-8")
        (self.repo / "README.md").write_text("old\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=self.repo, check=True, capture_output=True)
        self.base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, check=True, capture_output=True, text=True).stdout.strip()
        self.workspace = IsolatedGitWorktree(self.repo, self.root / "worktrees")

    def tearDown(self):
        if self.workspace.path is not None:
            self.workspace.cleanup()
        self.temp.cleanup()

    def test_patch_is_applied_only_in_detached_runner_worktree_branch(self):
        path = self.workspace.create("aura/repair/unit-test", self.base)
        patch = (
            "diff --git a/app/services/sample.py b/app/services/sample.py\n"
            "index 2b5f3a2..e5c0d5d 100644\n"
            "--- a/app/services/sample.py\n"
            "+++ b/app/services/sample.py\n"
            "@@ -1 +1 @@\n"
            "-VALUE = 1\n"
            "+VALUE = 2\n"
        )
        self.assertEqual(self.workspace.apply(patch), ("app/services/sample.py",))
        self.assertEqual((path / "app/services/sample.py").read_text(encoding="utf-8"), "VALUE = 2\n")
        self.assertEqual((self.repo / "app/services/sample.py").read_text(encoding="utf-8"), "VALUE = 1\n")
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=path, check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(branch, "aura/repair/unit-test")

    def test_rejects_branch_outside_repair_namespace_and_invalid_sha(self):
        with self.assertRaises(GitWorktreeError):
            self.workspace.create("main", self.base)
        with self.assertRaises(GitWorktreeError):
            self.workspace.create("aura/repair/test", "HEAD")
        self.assertIsNone(self.workspace.path)

    def test_rejects_patch_outside_allowlist(self):
        path = self.workspace.create("aura/repair/unsafe-path", self.base)
        patch = (
            "diff --git a/README.md b/README.md\n"
            "--- a/README.md\n"
            "+++ b/README.md\n"
            "@@ -1 +1 @@\n"
            "-old\n"
            "+new\n"
        )
        with self.assertRaisesRegex(GitWorktreeError, "outside the repair allowlist"):
            self.workspace.apply(patch)
        self.assertTrue(path.exists())
        self.assertEqual((self.repo / "README.md").read_text(encoding="utf-8"), "old\n")

    def test_cleanup_removes_temporary_worktree_and_repair_branch_only(self):
        branch = "aura/repair/cleanup"
        path = self.workspace.create(branch, self.base)
        self.workspace.cleanup()
        self.assertFalse(path.exists())
        self.assertEqual((self.repo / "app/services/sample.py").read_text(encoding="utf-8"), "VALUE = 1\n")
        branches = subprocess.run(
            ["git", "branch", "--list", branch], cwd=self.repo,
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(branches, "")
        main = subprocess.run(
            ["git", "branch", "--show-current"], cwd=self.repo,
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(main, "main")


if __name__ == "__main__":
    unittest.main()
