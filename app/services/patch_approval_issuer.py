"""Owner-context-bound issuance of short-lived patch approval receipts.

Callers MUST obtain authenticated_owner_id from a verified owner session, never
from request JSON. This service intentionally exposes no HTTP route or auth logic.
"""

import json
import re
import secrets
import time
from collections.abc import Callable, Sequence
from typing import Any

from app.patch_policy import ChangedFile, evaluate_patch


_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_INCIDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
MAX_TTL_SECONDS = 600


def _validate_approved_paths(paths: Sequence[str]) -> tuple[str, ...]:
    if not isinstance(paths, (tuple, list)) or not paths:
        raise ValueError("approved paths are required")
    if any(not isinstance(path, str) or not path for path in paths):
        raise ValueError("approved paths must be non-empty strings")
    if len(set(paths)) != len(paths):
        raise ValueError("duplicate approved paths are not allowed")
    decision = evaluate_patch(
        ChangedFile(path, "modified", 0, 0, 0) for path in paths
    )
    if not decision.allowed:
        raise ValueError("approved paths violate patch policy")
    return tuple(sorted(paths))


async def issue_patch_approval_receipt(
    db: Any,
    *,
    authenticated_owner_id: str,
    incident_id: str,
    base_sha: str,
    patch_sha256: str,
    approved_paths: Sequence[str],
    ttl_seconds: int = 300,
    clock: Callable[[], float] = time.time,
) -> str:
    """Persist a short-lived receipt after the caller authenticates the owner.

    The returned opaque ID is not itself authorization: execution still requires
    matching every bound field and atomically consuming the receipt once.
    """
    if db is None:
        raise ValueError("D1 database binding is required")
    if not isinstance(authenticated_owner_id, str) or not authenticated_owner_id.strip():
        raise ValueError("authenticated owner identity is required")
    if not isinstance(incident_id, str) or not _INCIDENT.fullmatch(incident_id):
        raise ValueError("invalid incident ID")
    if not isinstance(base_sha, str) or not _SHA1.fullmatch(base_sha):
        raise ValueError("invalid base commit SHA")
    if not isinstance(patch_sha256, str) or not _SHA256.fullmatch(patch_sha256):
        raise ValueError("invalid patch SHA-256")
    if (
        not isinstance(ttl_seconds, int)
        or isinstance(ttl_seconds, bool)
        or not 1 <= ttl_seconds <= MAX_TTL_SECONDS
    ):
        raise ValueError("receipt lifetime must be between 1 and 600 seconds")
    if not callable(clock):
        raise ValueError("clock must be callable")

    paths = _validate_approved_paths(approved_paths)
    created_at = int(clock())
    if created_at <= 0:
        raise ValueError("invalid clock")
    expires_at = created_at + ttl_seconds
    receipt_id = secrets.token_urlsafe(32)
    paths_json = json.dumps(paths, separators=(",", ":"), ensure_ascii=True)

    await db.prepare(
        """INSERT INTO patch_approval_receipts
           (id, approved_by, incident_id, base_sha, patch_sha256,
            approved_paths_json, expires_at, revoked_at, consumed_at, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?)"""
    ).bind(
        receipt_id,
        authenticated_owner_id,
        incident_id,
        base_sha,
        patch_sha256,
        paths_json,
        expires_at,
        created_at,
    ).run()
    return receipt_id
