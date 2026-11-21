"""Async proposal orchestration; execution remains a separate receipt-gated step."""
from __future__ import annotations

from dataclasses import replace
from typing import Any

from app.services.incident_repair_bridge import plan_from_incident
from app.services.repair_pipeline import RepairProposal, prepare_repair_proposal


async def prepare_repair_proposal_async(
    incident: dict[str, object],
    *,
    base_sha: str,
    generator: Any,
) -> RepairProposal:
    if not isinstance(incident, dict):
        return RepairProposal("blocked", "", base_sha, reasons=("invalid_incident",))
    plan_data = plan_from_incident(incident)
    if plan_data.get("status") != "ready_for_owner_approval":
        return RepairProposal(
            "blocked",
            str(incident.get("incident_id", "")),
            base_sha,
            reasons=tuple(str(item) for item in plan_data.get("reasons", ())),
        )
    if generator is None or not callable(getattr(generator, "generate", None)):
        return RepairProposal(
            "blocked", str(incident.get("incident_id", "")), base_sha,
            reasons=("patch_generator_unavailable",),
        )
    try:
        generated = await generator.generate(incident, plan_data)
    except Exception:
        return RepairProposal(
            "blocked", str(incident.get("incident_id", "")), base_sha,
            reasons=("patch_generation_failed",),
        )

    class _CachedGenerator:
        is_mock = True

        def generate(self, _incident, _plan):
            return generated

    proposal = prepare_repair_proposal(
        incident, base_sha=base_sha, generator=_CachedGenerator()
    )
    return replace(
        proposal,
        provider_invoked=getattr(generator, "is_mock", False) is not True,
    )
