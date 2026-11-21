"""No-side-effect planner for guarded AURA repair proposals.

This module turns incident metadata into a reviewable plan. It never invokes
providers, edits files, creates branches, commits, merges, or deploys.
"""

from dataclasses import dataclass
from typing import Iterable


SAFE_CATEGORIES = {
    "automated_test_regression",
    "python_syntax_or_import",
}
BLOCKED_CATEGORIES = {
    "dependency_or_security_audit",
    "database_schema",
    "cloudflare_deployment_or_config",
    "container_or_runtime",
    "unknown_or_unclassified",
}
ALLOWED_PREFIXES = ("app/agents/", "app/services/", "tests/", "docs/")
BLOCKED_PATH_COMPONENTS = {
    "auth",
    "authentication",
    "authorization",
    "security",
    "billing",
    "payment",
    "payments",
    "provider",
    "providers",
    "secret",
    "secrets",
    "ledger",
    "database",
    "db",
    "config",
    "configuration",
}
MAX_CANDIDATE_PATHS = 6


@dataclass(frozen=True)
class RepairPlan:
    incident_id: str
    status: str
    category: str
    candidate_paths: tuple[str, ...]
    reasons: tuple[str, ...]
    requires_owner_approval: bool = True
    provider_invocation: bool = False
    file_changes: bool = False
    github_write: bool = False
    merge: bool = False
    deploy: bool = False


def build_repair_plan(
    incident_id: str,
    category: str,
    candidate_paths: Iterable[str],
) -> RepairPlan:
    """Build a fail-closed plan; a valid plan is still not execution approval."""
    paths = tuple(candidate_paths)
    reasons: list[str] = []

    if not incident_id or len(incident_id) > 128:
        reasons.append("invalid_incident_id")
    if category not in SAFE_CATEGORIES:
        reasons.append("category_not_eligible_for_automated_repair")
    if category in BLOCKED_CATEGORIES:
        reasons.append("high_risk_category_requires_manual_triage")
    if not paths:
        reasons.append("no_candidate_paths")
    if len(paths) > MAX_CANDIDATE_PATHS:
        reasons.append("too_many_candidate_paths")

    normalized_paths: list[str] = []
    for path in paths:
        normalized = path.replace("\\", "/")
        normalized_paths.append(normalized)
        components = [part.lower() for part in normalized.split("/") if part]
        if normalized.startswith("/") or ".." in components:
            reasons.append(f"unsafe_candidate_path:{normalized}")
        if not normalized.startswith(ALLOWED_PREFIXES):
            reasons.append(f"path_outside_allowlist:{normalized}")
        if any(part in BLOCKED_PATH_COMPONENTS for part in components):
            reasons.append(f"sensitive_path_requires_manual_triage:{normalized}")

    status = "blocked" if reasons else "ready_for_owner_approval"
    return RepairPlan(
        incident_id=incident_id,
        status=status,
        category=category,
        candidate_paths=tuple(normalized_paths),
        reasons=tuple(dict.fromkeys(reasons)),
    )
