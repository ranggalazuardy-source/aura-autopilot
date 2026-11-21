"""D1-backed, read-only loading and preparation of owner-triaged CI repairs."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.services.it_ai_repair_adapter import ITEngineerGenerator
from app.services.repair_pipeline import RepairProposal
from app.services.triaged_ci_repair import prepare_triaged_ci_incident_repair


def _row_mapping(row: Any) -> Mapping[str, Any] | None:
    if row is None:
        return None
    to_py = getattr(row, "to_py", None)
    if callable(to_py):
        row = to_py()
    if isinstance(row, Mapping):
        return row
    try:
        return dict(row)
    except (TypeError, ValueError):
        return None


async def prepare_triaged_ci_repair_from_d1(
    db: Any,
    incident_id: str,
    *,
    generator: ITEngineerGenerator,
    confirm_owner_generation: bool,
    provider_inference_approved: bool = False,
) -> RepairProposal:
    """Load authoritative persisted evidence, then run the guarded proposal flow.

    This function is read-only with respect to D1. It never updates triage,
    creates execution requests, consumes receipts, or writes to a repository.
    """
    if db is None:
        return RepairProposal("blocked", incident_id if isinstance(incident_id, str) else "",
                              "", reasons=("d1_unavailable",))
    if not isinstance(incident_id, str) or len(incident_id) != 24:
        return RepairProposal("blocked", "", "", reasons=("invalid_incident_id",))
    try:
        row = await db.prepare(
            """SELECT i.id AS incident_id, i.source, i.status,
                      e.repository, e.workflow_name, e.conclusion, e.head_sha,
                      e.triage_category, e.candidate_paths_json, e.triage_owner
               FROM operational_incidents i
               INNER JOIN operational_incident_evidence e ON e.incident_id = i.id
               WHERE i.id = ? AND i.source = 'github_actions'
               LIMIT 1"""
        ).bind(incident_id).first()
    except Exception:
        return RepairProposal("blocked", incident_id, "", reasons=("d1_evidence_read_failed",))
    evidence = _row_mapping(row)
    if evidence is None:
        return RepairProposal("blocked", incident_id, "", reasons=("triaged_ci_evidence_not_found",))
    return prepare_triaged_ci_incident_repair(
        evidence,
        generator=generator,
        confirm_owner_generation=confirm_owner_generation,
        provider_inference_approved=provider_inference_approved,
    )
