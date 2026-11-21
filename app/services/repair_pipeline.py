"""Side-effect-free orchestration from a normalized incident to a repair proposal.

The generator is an injected capability. This module does not configure or call
an AI provider by itself, and it never applies patches or writes to GitHub.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
from typing import Protocol

from app.patch_content_policy import evaluate_unified_diff
from app.patch_policy import ChangedFile, evaluate_patch
from app.repair_planner import RepairPlan, build_repair_plan
from app.patch_executor import PatchApproval, PatchExecutionRequest
from app.services.incident_repair_bridge import plan_from_incident


_SHA1 = re.compile(r"^[0-9a-f]{40}$")


class PatchGenerator(Protocol):
    def generate(self, incident: dict[str, object], plan: dict[str, object]) -> tuple[str, tuple[ChangedFile, ...]]:
        """Return a unified diff and matching metadata; must not perform writes."""


@dataclass(frozen=True)
class RepairProposal:
    status: str
    incident_id: str
    base_sha: str
    patch_text: str = ""
    patch_sha256: str = ""
    changed_paths: tuple[str, ...] = ()
    changed_files: tuple[ChangedFile, ...] = ()
    plan: RepairPlan | None = None
    reasons: tuple[str, ...] = ()
    requires_owner_approval: bool = True
    provider_invoked: bool = False
    files_written: bool = False
    github_written: bool = False
    merged: bool = False
    deployed: bool = False


def prepare_repair_proposal(
    incident: dict[str, object],
    *,
    base_sha: str,
    generator: PatchGenerator,
) -> RepairProposal:
    """Generate and validate a proposal; execution remains a separate approval step.

    Candidate paths must be explicitly supplied in the incident. The planner
    blocks unsupported categories and malformed paths before the generator is
    invoked. This function never trusts generator metadata without revalidation.
    """
    if not isinstance(incident, dict):
        return RepairProposal("blocked", "", base_sha, reasons=("invalid_incident",))
    incident_id = incident.get("incident_id")
    incident_id = incident_id if isinstance(incident_id, str) else ""
    if not isinstance(base_sha, str) or not _SHA1.fullmatch(base_sha):
        return RepairProposal("blocked", incident_id, "", reasons=("invalid_base_sha",))
    if generator is None or not callable(getattr(generator, "generate", None)):
        return RepairProposal("blocked", incident_id, base_sha, reasons=("patch_generator_unavailable",))

    plan_data = plan_from_incident(incident)
    if plan_data.get("status") != "ready_for_owner_approval":
        return RepairProposal(
            "blocked", incident_id, base_sha,
            reasons=tuple(str(item) for item in plan_data.get("reasons", ())),
        )
    plan = build_repair_plan(
        incident_id,
        str(plan_data["category"]),
        tuple(str(path) for path in plan_data["candidate_paths"]),
    )
    if plan.status != "ready_for_owner_approval":
        return RepairProposal("blocked", incident_id, base_sha, reasons=plan.reasons)

    try:
        generated = generator.generate(incident, plan_data)
    except Exception:
        return RepairProposal("blocked", incident_id, base_sha, reasons=("patch_generation_failed",))
    if not isinstance(generated, tuple) or len(generated) != 2:
        return RepairProposal("blocked", incident_id, base_sha, reasons=("invalid_generator_result",))
    patch_text, changed_files = generated
    if not isinstance(patch_text, str) or not patch_text or not isinstance(changed_files, tuple) or not changed_files:
        return RepairProposal("blocked", incident_id, base_sha, reasons=("invalid_generated_patch",))
    if any(not isinstance(item, ChangedFile) for item in changed_files):
        return RepairProposal("blocked", incident_id, base_sha, reasons=("invalid_changed_file_metadata",))

    metadata = evaluate_patch(changed_files)
    diff = evaluate_unified_diff(patch_text, changed_files)
    if not metadata.allowed or not diff.allowed:
        reasons = tuple(dict.fromkeys((*metadata.reasons, *diff.reasons)))
        return RepairProposal("blocked", incident_id, base_sha, reasons=reasons or ("generated_patch_rejected",))

    paths = tuple(sorted(item.filename.replace("\\\\", "/") for item in changed_files))
    planned_paths = tuple(sorted(plan.candidate_paths))
    if paths != planned_paths:
        return RepairProposal("blocked", incident_id, base_sha, reasons=("generated_paths_do_not_match_incident_plan",))

    digest = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
    return RepairProposal(
        "ready_for_owner_approval", incident_id, base_sha,
        patch_text=patch_text, patch_sha256=digest, changed_paths=paths,
        changed_files=changed_files, plan=plan,
    )


def build_execution_request(
    proposal: RepairProposal,
    approval: PatchApproval,
) -> PatchExecutionRequest:
    """Bind a validated proposal to a receipt for the existing guarded executor.

    This only constructs an immutable request. D1 verification/consumption and
    workspace side effects remain the responsibility of the async executor.
    """
    if not isinstance(proposal, RepairProposal) or proposal.status != "ready_for_owner_approval":
        raise ValueError("repair proposal is not eligible for execution")
    if proposal.plan is None or not proposal.patch_text or not proposal.changed_files:
        raise ValueError("repair proposal is incomplete")
    if not isinstance(approval, PatchApproval):
        raise TypeError("approval must be a PatchApproval receipt")
    if hashlib.sha256(proposal.patch_text.encode("utf-8")).hexdigest() != proposal.patch_sha256:
        raise ValueError("repair proposal patch digest changed")
    if approval.incident_id != proposal.incident_id or approval.base_sha != proposal.base_sha:
        raise ValueError("approval receipt does not match the proposal")
    if approval.patch_sha256 != proposal.patch_sha256:
        raise ValueError("approval receipt patch digest does not match the proposal")
    if tuple(sorted(approval.approved_paths)) != tuple(sorted(proposal.changed_paths)):
        raise ValueError("approval receipt paths do not match the proposal")
    return PatchExecutionRequest(
        plan=proposal.plan,
        patch_text=proposal.patch_text,
        changed_files=proposal.changed_files,
        base_sha=proposal.base_sha,
        approval=approval,
    )
