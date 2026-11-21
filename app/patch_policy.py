"""Fail-closed policy for proposed autonomous repair pull requests.

This module validates GitHub changed-file metadata only. It does not generate,
apply, merge, or deploy patches.
"""

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Iterable


MAX_CHANGED_FILES = 6
MAX_ADDITIONS = 400
MAX_DELETIONS = 200

# Keep the first autonomous repair scope narrow. Expand only with reviewed tests.
ALLOWED_PREFIXES = ("app/agents/", "app/services/", "tests/", "docs/")
DENIED_PARTS = (
    ".github/", "cloudflare/", "migrations/", "infra/", "terraform/",
    "auth", "security", "billing", "payment", "secret", "credential",
    "provider", "wrangler", "schema", "database", "ledger",
)
DENIED_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".env")


@dataclass(frozen=True)
class ChangedFile:
    filename: str
    status: str
    additions: int = 0
    deletions: int = 0
    changes: int = 0


@dataclass(frozen=True)
class PatchDecision:
    allowed: bool
    reasons: tuple[str, ...]


def evaluate_patch(files: Iterable[ChangedFile]) -> PatchDecision:
    """Return an explainable fail-closed decision for a proposed repair diff."""
    try:
        items = tuple(files)
    except (TypeError, ValueError):
        return PatchDecision(False, ("invalid_changed_file_collection",))
    reasons: list[str] = []

    if any(not isinstance(item, ChangedFile) for item in items):
        return PatchDecision(False, ("invalid_changed_file_entry",))

    for item in items:
        if not isinstance(item.filename, str) or not isinstance(item.status, str):
            reasons.append("invalid_file_metadata")
            continue
        counts = (item.additions, item.deletions, item.changes)
        if any(not isinstance(value, int) or isinstance(value, bool) for value in counts):
            reasons.append(f"invalid_change_counts:{item.filename}")
            continue
        if min(counts) < 0 or item.changes != item.additions + item.deletions:
            reasons.append(f"invalid_change_counts:{item.filename}")

    if reasons:
        return PatchDecision(False, tuple(dict.fromkeys(reasons)))

    if not items:
        reasons.append("empty_patch")
    if len(items) > MAX_CHANGED_FILES:
        reasons.append("too_many_changed_files")

    additions = sum(max(0, item.additions) for item in items)
    deletions = sum(max(0, item.deletions) for item in items)
    if additions > MAX_ADDITIONS:
        reasons.append("addition_limit_exceeded")
    if deletions > MAX_DELETIONS:
        reasons.append("deletion_limit_exceeded")

    seen: set[str] = set()
    for item in items:
        path = item.filename.replace("\\", "/")
        normalized = str(PurePosixPath(path))
        lower = normalized.lower()

        if normalized in seen:
            reasons.append("duplicate_path")
        seen.add(normalized)

        if item.status != "modified":
            reasons.append(f"non_modify_change:{normalized}")
        if not normalized.startswith(ALLOWED_PREFIXES):
            reasons.append(f"path_outside_allowlist:{normalized}")
        if any(part in lower for part in DENIED_PARTS):
            reasons.append(f"sensitive_path:{normalized}")
        if lower.endswith(DENIED_SUFFIXES):
            reasons.append(f"sensitive_file_type:{normalized}")
        if (
            path.startswith("/")
            or "\x00" in path
            or ".." in PurePosixPath(path).parts
            or PurePosixPath(path).is_absolute()
            or (len(path) >= 2 and path[1] == ":")
            or normalized in {"", "."}
        ):
            reasons.append(f"unsafe_path:{normalized}")
        if min(item.additions, item.deletions, item.changes) < 0:
            reasons.append(f"invalid_change_counts:{normalized}")

    return PatchDecision(not reasons, tuple(dict.fromkeys(reasons)))
