"""D1-backed one-time execution request storage for the isolated repair runner.

Patch bytes remain server-side until a dedicated runner authenticates and claims
an unexpired request. The dispatch envelope contains only the opaque request ID.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import time
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from app.patch_policy import ChangedFile, evaluate_patch

_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_INCIDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_MAX_TTL = 600


def _row_mapping(row: Any) -> Mapping[str, Any] | None:
    if row is None:
        return None
    to_py = getattr(row, "to_py", None)
    if callable(to_py):
        row = to_py()
    if isinstance(row, Mapping):
        return row
    try:
        return dict(row)
    except (TypeError, ValueError):
        return None


def _paths(paths: Sequence[str]) -> tuple[str, ...]:
    if not isinstance(paths, (list, tuple)) or not paths:
        raise ValueError("execution_paths_required")
    if any(not isinstance(path, str) or not path for path in paths):
        raise ValueError("execution_paths_invalid")
    if len(paths) != len(set(paths)):
        raise ValueError("execution_paths_duplicate")
    decision = evaluate_patch(ChangedFile(path, "modified", 0, 0, 0) for path in paths)
    if not decision.allowed:
        raise ValueError("execution_paths_blocked")
    return tuple(sorted(paths))


async def create_execution_request(
    db: Any, *, incident_id: str, base_sha: str, patch_text: str,
    approved_paths: Sequence[str], receipt_id: str, ttl_seconds: int = 300,
    clock: Callable[[], float] = time.time,
) -> dict[str, Any]:
    if db is None:
        raise ValueError("d1_required")
    if not isinstance(incident_id, str) or not _INCIDENT.fullmatch(incident_id):
        raise ValueError("incident_id_invalid")
    if not isinstance(base_sha, str) or not _SHA1.fullmatch(base_sha):
        raise ValueError("base_sha_invalid")
    if not isinstance(patch_text, str) or not patch_text or len(patch_text.encode("utf-8")) > 256_000:
        raise ValueError("patch_text_invalid_or_too_large")
    if not isinstance(receipt_id, str) or not 32 <= len(receipt_id) <= 128:
        raise ValueError("receipt_id_invalid")
    if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= _MAX_TTL:
        raise ValueError("ttl_invalid")
    paths = _paths(approved_paths)
    patch_sha256 = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
    now = int(clock())
    if now <= 0:
        raise ValueError("clock_invalid")
    request_id = secrets.token_hex(16)
    expires_at = now + ttl_seconds
    await db.prepare(
        """INSERT INTO repair_execution_requests
        (id, incident_id, base_sha, patch_sha256, patch_text, approved_paths_json,
         approval_receipt_id, status, expires_at, created_at, claimed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?, NULL)"""
    ).bind(request_id, incident_id, base_sha, patch_sha256, patch_text,
           json.dumps(paths, separators=(",", ":")), receipt_id, expires_at, now).run()
    return {"request_id": request_id, "base_sha": base_sha,
            "patch_sha256": patch_sha256, "expires_at": expires_at,
            "status": "queued"}


async def claim_execution_patch(
    db: Any, *, request_id: str, clock: Callable[[], float] = time.time,
) -> dict[str, Any] | None:
    """Atomically return patch bytes once; expiry and replay fail closed."""
    if db is None or not isinstance(request_id, str) or not re.fullmatch(r"[0-9a-f]{32}", request_id):
        return None
    now = int(clock())
    result = await db.prepare(
        """UPDATE repair_execution_requests
        SET status = 'claimed', claimed_at = ?
        WHERE id = ? AND status = 'queued' AND expires_at > ?
        RETURNING id, incident_id, base_sha, patch_sha256, patch_text,
                  approved_paths_json, approval_receipt_id, expires_at"""
    ).bind(now, request_id, now).first()
    result = _row_mapping(result)
    if result is None:
        return None
    patch = result.get("patch_text")
    if not isinstance(patch, str) or hashlib.sha256(patch.encode("utf-8")).hexdigest() != result.get("patch_sha256"):
        return None
    try:
        paths = json.loads(result["approved_paths_json"])
    except (KeyError, TypeError, ValueError):
        return None
    if not isinstance(paths, list) or not paths:
        return None
    return {
        "request_id": result["id"], "incident_id": result["incident_id"],
        "base_sha": result["base_sha"], "patch_sha256": result["patch_sha256"],
        "patch_text": patch, "approved_paths": paths,
        "approval_receipt_id": result["approval_receipt_id"],
        "expires_at": result["expires_at"],
    }
