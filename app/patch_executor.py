"""Approval-gated orchestration for isolated repair patch proposals.

This adapter-driven core has no provider, merge, or deployment capability.
Concrete production adapters must enforce branch-scoped writes and verify
owner approvals against trusted, replay-protected storage.
"""

from dataclasses import dataclass
import hashlib
import re
from typing import Protocol

from app.patch_content_policy import evaluate_unified_diff
from app.patch_policy import ChangedFile, evaluate_patch
from app.repair_planner import RepairPlan


_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_INCIDENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


@dataclass(frozen=True)
class PatchApproval:
    """Approval receipt; trust is established only by ApprovalVerifier."""

    approval_id: str
    approved_by: str
    incident_id: str
    base_sha: str
    patch_sha256: str
    approved_paths: tuple[str, ...]


@dataclass(frozen=True)
class PatchExecutionRequest:
    plan: RepairPlan
    patch_text: str
    changed_files: tuple[ChangedFile, ...]
    base_sha: str
    approval: PatchApproval


@dataclass(frozen=True)
class PatchExecutionResult:
    status: str
    branch_name: str = ""
    draft_pr_url: str = ""
    reasons: tuple[str, ...] = ()


class ApprovalVerifier(Protocol):
    def verify_and_consume(self, approval: PatchApproval) -> bool:
        """Atomically verify and consume a valid, single-use owner receipt.

        The backing store must enforce expiry, revocation, owner identity, and
        one-time use in one transaction so concurrent executions cannot replay
        the same approval.
        """


class PatchWorkspace(Protocol):
    def create_isolated_branch(self, branch_name: str, base_sha: str) -> None: ...
    def apply_unified_diff(self, branch_name: str, patch_text: str) -> None: ...
    def run_quality_checks(self, branch_name: str) -> bool: ...
    def create_draft_pull_request(
        self, branch_name: str, title: str, body: str
    ) -> str: ...


def _blocked(*reasons: str) -> PatchExecutionResult:
    return PatchExecutionResult("blocked", reasons=tuple(dict.fromkeys(reasons)))


def execute_approved_patch(
    request: PatchExecutionRequest,
    verifier: ApprovalVerifier,
    workspace: PatchWorkspace,
) -> PatchExecutionResult:
    """Validate and prepare a tested draft PR after trusted owner approval.

    All input and diff gates run before the verifier or workspace is invoked.
    Adapter errors fail closed. A failed operation never proceeds to PR creation.
    """
    if not isinstance(request, PatchExecutionRequest):
        return _blocked("invalid_execution_request")
    if not isinstance(request.plan, RepairPlan):
        return _blocked("invalid_repair_plan")
    if not isinstance(request.approval, PatchApproval):
        return _blocked("invalid_approval_receipt")
    if not isinstance(request.patch_text, str) or not request.patch_text:
        return _blocked("invalid_patch_text")
    if not isinstance(request.base_sha, str):
        return _blocked("invalid_base_commit_sha")
    if not isinstance(request.changed_files, tuple) or not request.changed_files:
        return _blocked("invalid_changed_files")
    if any(not isinstance(item, ChangedFile) for item in request.changed_files):
        return _blocked("invalid_changed_file_entry")

    plan = request.plan
    approval = request.approval
    if not all(isinstance(path, str) for path in plan.candidate_paths):
        return _blocked("invalid_repair_plan_paths")
    if not isinstance(approval.approved_paths, tuple) or not all(
        isinstance(path, str) for path in approval.approved_paths
    ):
        return _blocked("invalid_approval_paths")
    if not all(
        isinstance(value, str)
        for value in (
            approval.approval_id,
            approval.approved_by,
            approval.incident_id,
            approval.base_sha,
            approval.patch_sha256,
            plan.incident_id,
            plan.category,
            plan.status,
        )
    ):
        return _blocked("invalid_approval_or_plan_fields")

    patch_sha256 = hashlib.sha256(request.patch_text.encode("utf-8")).hexdigest()
    reasons: list[str] = []

    if plan.status != "ready_for_owner_approval" or not plan.requires_owner_approval:
        reasons.append("repair_plan_not_eligible")
    if not plan.incident_id or not _INCIDENT.fullmatch(plan.incident_id):
        reasons.append("invalid_incident_id")
    if not _SHA1.fullmatch(request.base_sha):
        reasons.append("invalid_base_commit_sha")
    if approval.incident_id != plan.incident_id:
        reasons.append("approval_incident_mismatch")
    if approval.base_sha != request.base_sha:
        reasons.append("approval_base_sha_mismatch")
    if approval.patch_sha256 != patch_sha256:
        reasons.append("approval_patch_digest_mismatch")
    if not approval.approval_id.strip() or not approval.approved_by.strip():
        reasons.append("approval_receipt_incomplete")

    if any(
        not isinstance(item.filename, str)
        or not isinstance(item.status, str)
        or any(not isinstance(count, int) or isinstance(count, bool)
               for count in (item.additions, item.deletions, item.changes))
        for item in request.changed_files
    ):
        reasons.append("invalid_changed_file_metadata")
        return _blocked(*reasons)

    metadata_paths = tuple(sorted(
        item.filename.replace("\\", "/") for item in request.changed_files
    ))
    planned_paths = tuple(sorted(
        path.replace("\\", "/") for path in plan.candidate_paths
    ))
    approved_paths = tuple(sorted(
        path.replace("\\", "/") for path in approval.approved_paths
    ))
    if metadata_paths != planned_paths:
        reasons.append("changed_paths_do_not_match_repair_plan")
    if metadata_paths != approved_paths:
        reasons.append("changed_paths_do_not_match_owner_approval")

    metadata_decision = evaluate_patch(request.changed_files)
    if not metadata_decision.allowed:
        reasons.extend(metadata_decision.reasons)

    diff_decision = evaluate_unified_diff(request.patch_text, request.changed_files)
    if not diff_decision.allowed:
        reasons.extend(diff_decision.reasons)

    if reasons:
        return _blocked(*reasons)

    try:
        approval_valid = verifier.verify_and_consume(approval)
    except Exception:
        return _blocked("approval_verification_failed")
    if approval_valid is not True:
        return _blocked("owner_approval_not_verified")

    digest = patch_sha256[:10]
    incident_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", plan.incident_id).strip("-")
    branch_name = f"aura/repair/{incident_slug}-{digest}"

    # Side effects start only after every deterministic gate and trusted approval.
    try:
        workspace.create_isolated_branch(branch_name, request.base_sha)
    except Exception:
        return PatchExecutionResult(
            "execution_failed", reasons=("isolated_branch_creation_failed",)
        )

    try:
        workspace.apply_unified_diff(branch_name, request.patch_text)
    except Exception:
        return PatchExecutionResult(
            "execution_failed",
            branch_name=branch_name,
            reasons=("patch_application_failed",),
        )

    try:
        checks_passed = workspace.run_quality_checks(branch_name)
    except Exception:
        return PatchExecutionResult(
            "execution_failed",
            branch_name=branch_name,
            reasons=("quality_check_execution_failed",),
        )
    if checks_passed is not True:
        return PatchExecutionResult(
            "checks_failed",
            branch_name=branch_name,
            reasons=("quality_checks_failed",),
        )

    title = f"Draft AURA repair: {plan.incident_id}"
    body = (
        "## Guarded automated repair proposal\n\n"
        f"- Incident: {plan.incident_id}\n"
        f"- Base commit: {request.base_sha}\n"
        f"- Patch SHA-256: {patch_sha256}\n"
        f"- Owner approval receipt: {approval.approval_id}\n"
        "- Scope and unified diff passed deterministic policy validation.\n"
        "- Isolated-branch quality checks passed.\n\n"
        "This is a draft for human review. It is not merged or deployed."
    )
    try:
        pr_url = workspace.create_draft_pull_request(branch_name, title, body)
    except Exception:
        return PatchExecutionResult(
            "execution_failed",
            branch_name=branch_name,
            reasons=("draft_pr_creation_failed",),
        )
    if not isinstance(pr_url, str) or not pr_url.startswith("https://github.com/"):
        return PatchExecutionResult(
            "execution_failed",
            branch_name=branch_name,
            reasons=("invalid_draft_pr_url",),
        )

    return PatchExecutionResult(
        "draft_pr_created",
        branch_name=branch_name,
        draft_pr_url=pr_url,
    )
