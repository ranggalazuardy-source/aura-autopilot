"""Fail-closed validation for opaque GitHub Actions repair dispatch envelopes.

The runner receives an opaque execution ID only. Patch text, approval receipts,
and write credentials must be fetched or minted through separate trusted
channels; they are never accepted as dispatch inputs.
"""

from dataclasses import dataclass
import re
from collections.abc import Mapping

_REQUEST_ID = re.compile(r"^[0-9a-f]{32}$")
_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_REPOSITORY = "ranggalazuardy-source/aura-autopilot"
_MAX_TTL_SECONDS = 600
_ALLOWED_KEYS = frozenset({"request_id", "repository", "base_sha", "expires_at"})


@dataclass(frozen=True)
class RunnerDispatch:
    request_id: str
    repository: str
    base_sha: str
    expires_at: int


def validate_runner_dispatch(
    payload: object, *, now: int, expected_repository: str = _REPOSITORY
) -> RunnerDispatch:
    """Validate an opaque dispatch envelope before any network or Git operation.

    Extra fields are rejected to prevent callers smuggling patch text, tokens,
    approval claims, branch names, or arbitrary workflow instructions.
    """
    if not isinstance(payload, Mapping):
        raise ValueError("dispatch_payload_must_be_mapping")
    if set(payload.keys()) != _ALLOWED_KEYS:
        raise ValueError("dispatch_payload_fields_invalid")
    request_id = payload.get("request_id")
    repository = payload.get("repository")
    base_sha = payload.get("base_sha")
    expires_at = payload.get("expires_at")
    if not isinstance(request_id, str) or not _REQUEST_ID.fullmatch(request_id):
        raise ValueError("dispatch_request_id_invalid")
    if not isinstance(repository, str) or repository != expected_repository:
        raise ValueError("dispatch_repository_invalid")
    if not isinstance(base_sha, str) or not _SHA1.fullmatch(base_sha):
        raise ValueError("dispatch_base_sha_invalid")
    if isinstance(now, bool) or not isinstance(now, int) or now < 0:
        raise ValueError("dispatch_clock_invalid")
    if isinstance(expires_at, bool) or not isinstance(expires_at, int):
        raise ValueError("dispatch_expiry_invalid")
    if expires_at <= now:
        raise ValueError("dispatch_request_expired")
    if expires_at - now > _MAX_TTL_SECONDS:
        raise ValueError("dispatch_request_ttl_exceeded")
    return RunnerDispatch(request_id, repository, base_sha, expires_at)
