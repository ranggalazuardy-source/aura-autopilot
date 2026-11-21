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

    plan = plan_from_incident(incident)
    if plan.get("status") != "ready_for_owner_approval":
        return RepairProposal(
            "blocked", incident_id, base_sha,
            reasons=tuple(str(item) for item in plan.get("reasons", ())),
        )

    try:
        generated = generator.generate(incident, plan)
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

    paths = tuple(sorted(item.filename.replace("\\", "/") for item in changed_files))
    planned_paths = tuple(sorted(str(item).replace("\\", "/") for item in plan["candidate_paths"]))
    if paths != planned_paths:
        return RepairProposal("blocked", incident_id, base_sha, reasons=("generated_paths_do_not_match_incident_plan",))

    digest = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
    return RepairProposal(
        "ready_for_owner_approval", incident_id, base_sha,
        patch_text=patch_text, patch_sha256=digest, changed_paths=paths,
    )
