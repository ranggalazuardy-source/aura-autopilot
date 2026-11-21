"""Owner-confirmed bridge from persisted CI triage evidence to repair proposals.

This service is deliberately side-effect-free: callers supply a joined incident /
evidence row and an injected generator. It validates provenance, persisted
triage ownership, exact base SHA, and explicit generation confirmation before
the IT/AI Engineer adapter can invoke that generator.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any

from app.services.it_ai_repair_adapter import (
    ITEngineerGenerator,
    prepare_it_engineer_repair,
)
from app.services.repair_pipeline import RepairProposal


_INCIDENT_ID = re.compile(r"^[0-9a-f]{24}$")
_BASE_SHA = re.compile(r"^[0-9a-f]{40}$")
_SAFE_CATEGORIES = {"automated_test_regression", "python_syntax_or_import"}
_ALLOWED_WORKFLOWS = {"AURA quality checks", "Deploy AURA to Cloudflare"}
_REPOSITORY = "ranggalazuardy-source/aura-autopilot"


def _blocked(incident_id: str = "", base_sha: str = "", reason: str = "invalid_triaged_incident") -> RepairProposal:
    return RepairProposal("blocked", incident_id, base_sha, reasons=(reason,))


def prepare_triaged_ci_incident_repair(
    evidence: Mapping[str, Any],
    *,
    generator: ITEngineerGenerator,
    confirm_owner_generation: bool,
    provider_inference_approved: bool = False,
) -> RepairProposal:
    """Prepare a proposal only from persisted, owner-triaged CI evidence.

    The caller must pass a row joined from operational_incidents and
    operational_incident_evidence. Raw logs and client-supplied candidate paths
    are intentionally not accepted by this boundary.
    """
    if not isinstance(evidence, Mapping):
        return _blocked()
    incident_id = evidence.get("incident_id")
    base_sha = evidence.get("head_sha")
    incident_id = incident_id if isinstance(incident_id, str) else ""
    base_sha = base_sha if isinstance(base_sha, str) else ""
    if not _INCIDENT_ID.fullmatch(incident_id):
        return _blocked(reason="invalid_incident_id")
    if evidence.get("source") != "github_actions":
        return _blocked(incident_id, base_sha, "unsupported_incident_source")
    if evidence.get("status") != "investigating":
        return _blocked(incident_id, base_sha, "incident_not_investigating")
    if evidence.get("repository") != _REPOSITORY:
        return _blocked(incident_id, base_sha, "repository_not_allowlisted")
    if evidence.get("workflow_name") not in _ALLOWED_WORKFLOWS:
        return _blocked(incident_id, base_sha, "workflow_not_allowlisted")
    if evidence.get("conclusion") != "failure":
        return _blocked(incident_id, base_sha, "incident_evidence_not_failed")
    if evidence.get("triage_owner") != "IT_AI_ENGINEER":
        return _blocked(incident_id, base_sha, "incident_not_triaged_to_it_ai_engineer")
    if evidence.get("triage_category") not in _SAFE_CATEGORIES:
        return _blocked(incident_id, base_sha, "triage_category_not_repair_eligible")
    if not _BASE_SHA.fullmatch(base_sha):
        return _blocked(incident_id, "", "invalid_base_sha")
    if confirm_owner_generation is not True:
        return _blocked(incident_id, base_sha, "explicit_owner_generation_confirmation_required")

    raw_paths = evidence.get("candidate_paths_json")
    if not isinstance(raw_paths, str):
        return _blocked(incident_id, base_sha, "candidate_paths_evidence_missing")
    try:
        candidate_paths = json.loads(raw_paths)
    except (TypeError, ValueError):
        return _blocked(incident_id, base_sha, "candidate_paths_evidence_invalid")
    if (
        not isinstance(candidate_paths, list)
        or not candidate_paths
        or len(candidate_paths) > 6
        or any(not isinstance(path, str) for path in candidate_paths)
    ):
        return _blocked(incident_id, base_sha, "candidate_paths_evidence_invalid")

    # Pass only normalized, persisted fields to the generator. No raw logs,
    # workflow URLs, secrets, or caller-supplied diagnostic text are forwarded.
    normalized_incident: dict[str, object] = {
        "incident_id": incident_id,
        "source": "github_actions",
        "owner": "IT_AI_ENGINEER",
        "category": evidence["triage_category"],
        "base_sha": base_sha,
        "candidate_paths": candidate_paths,
    }
    return prepare_it_engineer_repair(
        normalized_incident,
        base_sha=base_sha,
        generator=generator,
        provider_inference_approved=provider_inference_approved,
    )
