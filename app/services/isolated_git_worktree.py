"""Ephemeral local Git worktree primitives for a trusted Actions runner.

This module deliberately has no remote, push, merge, deployment, or PR API.
It can only prepare and test a local isolated branch in the runner workspace.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_BRANCH = re.compile(r"^aura/repair/[A-Za-z0-9._-]{1,90}$")
_ALLOWED_PREFIXES = ("app/agents/", "app/services/", "tests/", "docs/")


class GitWorktreeError(RuntimeError):
    """Raised when an isolated worktree operation cannot be completed safely."""


class IsolatedGitWorktree:
    """Create, patch, and test a local branch without any remote write capability."""

    def __init__(self, repository: str | Path, worktree_root: str | Path, timeout: int = 180):
        self.repository = Path(repository).resolve()
        self.worktree_root = Path(worktree_root).resolve()
        self.timeout = timeout
        self.path: Path | None = None
        self.branch: str | None = None

    def _run(self, args: list[str], *, cwd: Path, input_text: str | None = None) -> str:
        try:
            result = subprocess.run(
                args, cwd=cwd, input=input_text, text=True, capture_output=True,
                timeout=self.timeout, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise GitWorktreeError("git operation could not complete") from exc
        if result.returncode != 0:
            raise GitWorktreeError("git operation failed: " + result.stderr[-1000:])
        return result.stdout.strip()

    def create(self, branch: str, base_sha: str) -> Path:
        if not isinstance(branch, str) or not _BRANCH.fullmatch(branch):
            raise GitWorktreeError("branch name is outside the repair namespace")
        if not isinstance(base_sha, str) or not _SHA1.fullmatch(base_sha):
            raise GitWorktreeError("base commit must be a full lowercase SHA-1")
        if self.path is not None:
            raise GitWorktreeError("worktree instance is already in use")
        root = self._run(["git", "rev-parse", "--show-toplevel"], cwd=self.repository)
        if Path(root).resolve() != self.repository:
            raise GitWorktreeError("repository path is not the Git worktree root")
        self.worktree_root.mkdir(parents=True, exist_ok=True)
        target = (self.worktree_root / (base_sha[:12] + "-" + branch.rsplit("/", 1)[-1])).resolve()
        if target == self.worktree_root or self.worktree_root not in target.parents or target.exists():
            raise GitWorktreeError("worktree target is invalid or already exists")
        self._run(["git", "worktree", "add", "--detach", str(target), base_sha], cwd=self.repository)
        try:
            self._run(["git", "checkout", "-b", branch, base_sha], cwd=target)
        except Exception:
            self._run(["git", "worktree", "remove", "--force", str(target)], cwd=self.repository)
            raise
        self.path, self.branch = target, branch
        return target

    def apply(self, patch_text: str) -> tuple[str, ...]:
        if self.path is None:
            raise GitWorktreeError("worktree has not been created")
        if not isinstance(patch_text, str) or not patch_text or "\x00" in patch_text:
            raise GitWorktreeError("patch text is invalid")
        self._run(["git", "apply", "--check", "--whitespace=error", "-"], cwd=self.path, input_text=patch_text)
        self._run(["git", "apply", "--whitespace=error", "-"], cwd=self.path, input_text=patch_text)
        changed = self._run(["git", "diff", "--name-only", "--diff-filter=ACDMRT"], cwd=self.path)
        paths = tuple(line.replace("\\", "/") for line in changed.splitlines() if line)
        if not paths:
            raise GitWorktreeError("patch produced no tracked file changes")
        for path in paths:
            if path.startswith("/") or any(part in {"", ".", ".."} for part in path.split("/")):
                raise GitWorktreeError("patch produced an unsafe path")
            if not path.startswith(_ALLOWED_PREFIXES):
                raise GitWorktreeError("patch changed a path outside the repair allowlist")
        raw = self._run(["git", "diff", "--raw"], cwd=self.path)
        if any(" 120000 " in line or " 160000 " in line for line in raw.splitlines()):
            raise GitWorktreeError("symlink and submodule changes are not allowed")
        return tuple(sorted(paths))

    def run_quality_checks(self) -> bool:
        if self.path is None:
            raise GitWorktreeError("worktree has not been created")
        self._run(["uv", "run", "python", "-m", "compileall", "-q", "app", "cloudflare"], cwd=self.path)
        self._run(["uv", "run", "python", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=self.path)
        return True

    def cleanup(self) -> None:
        if self.path is None:
            return
        path = self.path
        self._run(["git", "worktree", "remove", "--force", str(path)], cwd=self.repository)
        self.path = None
        self.branch = None