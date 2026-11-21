"""Async bridge from Cloudflare D1 approval receipts to guarded patch execution.

The synchronous executor remains the deterministic orchestration core. This
adapter first runs its complete validation against a side-effect-free workspace,
then atomically consumes the D1 receipt, and finally invokes the real workspace.
"""

from collections.abc import Callable
from typing import Any

from app.patch_executor import (
    PatchApproval,
    PatchExecutionRequest,
    PatchExecutionResult,
    execute_approved_patch,
)
from app.services.patch_approval_store import D1PatchApprovalStore


class _PreflightVerifier:
    """Only used after a no-side-effect preflight; never trusts external input."""

    def verify_and_consume(self, approval: PatchApproval) -> bool:
        return True


class _ConsumedReceiptVerifier:
    """The D1 receipt has already been atomically consumed by this call."""

    def verify_and_consume(self, approval: PatchApproval) -> bool:
        return True


class _PreflightWorkspace:
    """Validates executor gates without creating branches or contacting GitHub."""

    def create_isolated_branch(self, branch_name: str, base_sha: str) -> None:
        return None

    def apply_unified_diff(self, branch_name: str, patch_text: str) -> None:
        return None

    def run_quality_checks(self, branch_name: str) -> bool:
        return True

    def create_draft_pull_request(self, branch_name: str, title: str, body: str) -> str:
        return "https://github.com/preflight/validation-only/pull/1"


async def execute_approved_patch_with_d1(
    request: PatchExecutionRequest,
    *,
    db: Any,
    workspace: Any,
    clock: Callable[[], float] | None = None,
) -> PatchExecutionResult:
    """Execute only after deterministic validation and atomic D1 receipt use.

    The preflight calls the existing executor with a validation-only workspace.
    Invalid plans, paths, metadata, diffs, or approval bindings return before D1
    is touched. A valid request then consumes its owner-bound receipt exactly
    once. Only after consumption does the real workspace receive side effects.

    A consumed receipt is not restored if a later workspace stage fails. This
    deliberately fails closed: the owner must issue a fresh short-lived receipt.
    """
    preflight = execute_approved_patch(
        request, _PreflightVerifier(), _PreflightWorkspace()
    )
    if preflight.status != "draft_pr_created":
        return preflight

    try:
        store = D1PatchApprovalStore(db, clock=clock) if clock is not None else D1PatchApprovalStore(db)
        consumed = await store.verify_and_consume(request.approval)
    except Exception:
        return PatchExecutionResult(
            "blocked", reasons=("approval_verification_failed",)
        )
    if consumed is not True:
        return PatchExecutionResult(
            "blocked", reasons=("owner_approval_not_verified",)
        )

    return execute_approved_patch(
        request, _ConsumedReceiptVerifier(), workspace
    )
