"""Async IT/AI Engineer boundary for injected repair generators."""
from __future__ import annotations

from typing import Any

from app.services.async_repair_pipeline import prepare_repair_proposal_async
from app.services.repair_pipeline import RepairProposal


async def prepare_it_engineer_repair_async(
    incident: dict[str, object],
    *,
    base_sha: str,
    generator: Any,
    provider_inference_approved: bool = False,
) -> RepairProposal:
    if not isinstance(incident, dict):
        return RepairProposal("blocked", "", base_sha, reasons=("invalid_incident",))
    incident_id = str(incident.get("incident_id", ""))
    if incident.get("source") not in {"github_actions", "internal_test"}:
        return RepairProposal("blocked", incident_id, base_sha, reasons=("unsupported_incident_source",))
    if incident.get("owner") != "IT_AI_ENGINEER":
        return RepairProposal("blocked", incident_id, base_sha, reasons=("incident_not_owned_by_it_ai_engineer",))
    if getattr(generator, "is_mock", False) is not True and provider_inference_approved is not True:
        return RepairProposal("blocked", incident_id, base_sha, reasons=("provider_inference_not_approved",))
    return await prepare_repair_proposal_async(incident, base_sha=base_sha, generator=generator)
