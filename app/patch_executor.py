"""Approval-gated orchestration for isolated repair patch proposals.

The executor is adapter-driven. It never calls an AI provider and exposes no
merge or deployment operation. Production adapters must independently enforce
branch-scoped writes and verify owner approvals against trusted storage.
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
    def verify(self, approval: PatchApproval) -> bool:
        """Verify a stored, owner-issued approval receipt."""


class PatchWorkspace(Protocol):
    def create_isolated_branch(self, branch_name: str, base_sha: str) -> None: ...
    def apply_unified_diff(self, branch_name: str, patch_text: str) -> None: ...
    def run_quality_checks(self, branch_name: str) -> bool: ...
    def create_draft_pull_request(
        self, branch_name: str, title: str, body: str
    ) -> str: ...


def execute_approved_patch(
    request: PatchExecutionRequest,
    verifier: ApprovalVerifier,
    workspace: PatchWorkspace,
) -> PatchExecutionResult:
    """Validate, then prepare a tested draft PR on a dedicated isolated branch.

    This function requires concrete trusted approval and workspace adapters.
    It deliberately has no provider, merge, deployment, or main-branch API.
    """
    plan = request.plan
    approval = request.approval
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

    metadata_paths = tuple(sorted(item.filename.replace("\\", "/") for item in request.changed_files))
    planned_paths = tuple(sorted(path.replace("\\", "/") for path in plan.candidate_paths))
    approved_paths = tuple(sorted(path.replace("\\", "/") for path in approval.approved_paths))
    if not metadata_paths or metadata_paths != planned_paths:
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
        return PatchExecutionResult("blocked", reasons=tuple(dict.fromkeys(reasons)))

    try:
        approval_valid = verifier.verify(approval)
    except Exception:
        return PatchExecutionResult("blocked", reasons=("approval_verification_failed",))
    if not approval_valid:
        return PatchExecutionResult("blocked", reasons=("owner_approval_not_verified",))

    digest = patch_sha256[:10]
    incident_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", plan.incident_id).strip("-")
    branch_name = f"aura/repair/{incident_slug}-{digest}"

    # Side effects start only after all local gates and trusted approval pass.
    workspace.create_isolated_branch(branch_name, request.base_sha)
    workspace.apply_unified_diff(branch_name, request.patch_text)
    if not workspace.run_quality_checks(branch_name):
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
    pr_url = workspace.create_draft_pull_request(branch_name, title, body)
    return PatchExecutionResult(
        "draft_pr_created",
        branch_name=branch_name,
        draft_pr_url=pr_url,
    )
