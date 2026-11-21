"""Cloudflare D1-backed, atomic single-use approval receipt verifier.

This module consumes receipts only. It deliberately has no receipt-creation,
revocation, HTTP, GitHub, patch, merge, or deployment capabilities.
"""

import json
import re
import time
from collections.abc import Callable
from typing import Any


class D1PatchApprovalStore:
    """Verify and atomically consume a receipt with one conditional D1 UPDATE."""

    def __init__(self, db: Any, clock: Callable[[], float] = time.time):
        if db is None or not callable(clock):
            raise ValueError("database and clock are required")
        self._db = db
        self._clock = clock

    async def verify_and_consume(self, approval: Any) -> bool:
        """Return True only when this exact, live receipt is consumed once.

        D1 executes the conditional UPDATE as one atomic statement. Concurrent
        calls race on consumed_at IS NULL; only one can receive a returned row.
        """
        fields = (
            "approval_id", "approved_by", "incident_id", "base_sha",
            "patch_sha256", "approved_paths",
        )
        if any(not hasattr(approval, field) for field in fields):
            return False

        values = [getattr(approval, field) for field in fields[:5]]
        paths = getattr(approval, "approved_paths")
        if (
            any(not isinstance(value, str) or not value.strip() for value in values)
            or not re.fullmatch(r"[0-9a-f]{40}", values[3])
            or not re.fullmatch(r"[0-9a-f]{64}", values[4])
            or not isinstance(paths, tuple)
            or not paths
            or any(not isinstance(path, str) or not path for path in paths)
        ):
            return False

        canonical_paths = json.dumps(
            sorted(set(paths)), separators=(",", ":"), ensure_ascii=True
        )
        if len(set(paths)) != len(paths):
            return False

        now = int(self._clock())
        if now <= 0:
            return False

        statement = self._db.prepare(
            """UPDATE patch_approval_receipts
               SET consumed_at = ?
               WHERE id = ?
                 AND approved_by = ?
                 AND incident_id = ?
                 AND base_sha = ?
                 AND patch_sha256 = ?
                 AND approved_paths_json = ?
                 AND expires_at > ?
                 AND revoked_at IS NULL
                 AND consumed_at IS NULL
               RETURNING id"""
        ).bind(
            now,
            approval.approval_id,
            approval.approved_by,
            approval.incident_id,
            approval.base_sha,
            approval.patch_sha256,
            canonical_paths,
            now,
        )
        row = await statement.first()
        return row is not None
