"""Pure adapter from normalized incident records to guarded repair plans.

This module does not ingest GitHub issues, infer candidate files, invoke providers,
write files, or perform GitHub operations. Callers must supply explicit diagnostic
candidate_paths; missing or malformed evidence is blocked by default.
"""

from collections.abc import Mapping
from dataclasses import asdict

from app.repair_planner import build_repair_plan


def plan_from_incident(incident: Mapping[str, object]) -> dict[str, object]:
    """Return a JSON-friendly, approval-gated plan from explicit incident data."""
    if not isinstance(incident, Mapping):
        raise TypeError("incident must be a mapping")

    raw_id = incident.get("incident_id", "")
    raw_category = incident.get("category", "unknown_or_unclassified")
    raw_paths = incident.get("candidate_paths", ())

    incident_id = raw_id if isinstance(raw_id, str) else ""
    category = raw_category if isinstance(raw_category, str) else "unknown_or_unclassified"

    malformed_paths = not isinstance(raw_paths, (list, tuple))
    paths = list(raw_paths) if isinstance(raw_paths, (list, tuple)) else []
    invalid_path_values = any(not isinstance(path, str) for path in paths)
    safe_paths = [path for path in paths if isinstance(path, str)]

    # A deliberately unsafe sentinel forces the existing fail-closed planner to
    # block malformed path evidence without attempting to coerce arbitrary data.
    if malformed_paths or invalid_path_values:
        safe_paths.append("../invalid-candidate-path")

    plan = build_repair_plan(incident_id, category, safe_paths)
    result = asdict(plan)
    if malformed_paths or invalid_path_values:
        result["reasons"] = list(dict.fromkeys(
            [*result["reasons"], "malformed_candidate_paths"]
        ))
        result["status"] = "blocked"
    else:
        result["reasons"] = list(result["reasons"])
    result["candidate_paths"] = list(result["candidate_paths"])
    return result
