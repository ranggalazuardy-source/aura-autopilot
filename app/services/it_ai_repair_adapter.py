"""Guarded handoff from AURA's IT/AI Engineer role to repair planning.

The skill registry defines the role; this adapter is the executable boundary.
It accepts only normalized, evidence-backed incidents and an injected generator.
It does not discover paths, invoke a provider, write files, or call GitHub.
"""
from __future__ import annotations

from typing import Protocol

from app.services.repair_pipeline import PatchGenerator, RepairProposal, prepare_repair_proposal


class ITEngineerGenerator(PatchGenerator, Protocol):
    """A repair generator supplied by the IT/AI Engineer runtime."""

    is_mock: bool


def prepare_it_engineer_repair(
    incident: dict[str, object],
    *,
    base_sha: str,
    generator: ITEngineerGenerator,
    provider_inference_approved: bool = False,
) -> RepairProposal:
    """Prepare a proposal from an IT-owned incident without granting execution.

    Production provider generators are rejected unless the caller supplies an
    explicit approval flag. Mock generators remain usable for deterministic
    tests. Candidate paths must be present in incident evidence; this adapter
    deliberately does not infer paths from logs or stack traces.
    """
    if not isinstance(incident, dict):
        return RepairProposal("blocked", "", base_sha, reasons=("invalid_incident",))

    source = incident.get("source")
    owner = incident.get("owner")
    if source not in {"github_actions", "internal_test"}:
        return RepairProposal(
            "blocked",
            str(incident.get("incident_id", "")),
            base_sha,
            reasons=("unsupported_incident_source",),
        )
    if owner != "IT_AI_ENGINEER":
        return RepairProposal(
            "blocked",
            str(incident.get("incident_id", "")),
            base_sha,
            reasons=("incident_not_owned_by_it_ai_engineer",),
        )

    mock_generator = getattr(generator, "is_mock", False) is True
    if not mock_generator and provider_inference_approved is not True:
        return RepairProposal(
            "blocked",
            str(incident.get("incident_id", "")),
            base_sha,
            reasons=("provider_inference_not_approved",),
        )

    # The existing planner enforces category and path allowlists. No fallback
    # candidate paths are fabricated if the incident evidence is incomplete.
    return prepare_repair_proposal(incident, base_sha=base_sha, generator=generator)
