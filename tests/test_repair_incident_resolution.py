import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
DASHBOARD = (ROOT / "app" / "repair_dashboard.py").read_text(encoding="utf-8")
TREE = ast.parse(WORKER)


class RepairIncidentResolutionTests(unittest.TestCase):
    def function(self, name):
        return next(node for node in TREE.body
                    if isinstance(node, ast.AsyncFunctionDef) and node.name == name)

    def test_resolution_route_requires_owner_auth_and_explicit_confirmation(self):
        route = self.function("resolve_repair_incident")
        self.assertIn("Depends(require_api_key)", ast.unparse(route.decorator_list[0]))
        source = ast.unparse(route)
        self.assertIn("confirm_owner_resolution", source)
        self.assertIn("RepairIncidentResolutionIn", source)
        self.assertIn("StrictBool", ast.unparse(next(
            node for node in TREE.body
            if isinstance(node, ast.ClassDef) and node.name == "RepairIncidentResolutionIn"
        )))

    def test_only_real_open_ci_incidents_can_be_resolved(self):
        source = ast.unparse(self.function("resolve_repair_incident"))
        self.assertIn("incident.source != 'github_actions'", source)
        self.assertIn("incident.status not in ('open', 'investigating')", source)
        self.assertIn("status = 'resolved'", source)
        self.assertIn("RETURNING id", source)

    def test_github_run_must_match_repository_workflow_success_and_commit(self):
        source = ast.unparse(self.function("resolve_repair_incident"))
        for required in (
            "api.github.com/repos/ranggalazuardy-source/aura-autopilot/actions/runs/",
            "repository",
            "incident.workflow_name",
            "status",
            "conclusion",
            "verification_commit_sha",
            "verified_run.get('head_sha')",
            "verified_run.get('id')",
        ):
            self.assertIn(required, source)
        self.assertIn("completed", source)
        self.assertIn("success", source)

    def test_resolution_is_audited_and_has_no_execution_side_effects(self):
        source = ast.unparse(self.function("resolve_repair_incident"))
        self.assertIn("operational.incident_resolved", source)
        self.assertIn("resolution_note", source)
        self.assertIn("verification_run_url", source)
        self.assertIn("'patch_generated': False", source)
        self.assertIn("'runner_queued': False", source)
        self.assertIn("'merged': False", source)
        self.assertIn("'deployed': False", source)
        self.assertNotIn("create_execution_request", source)
        self.assertNotIn("AsyncBoundedModelPatchGenerator", source)

    def test_console_exposes_resolution_only_for_real_unresolved_incidents(self):
        self.assertIn('data-resolve-id=', DASHBOARD)
        self.assertIn('x.source==="github_actions"', DASHBOARD)
        self.assertIn('x.status==="open"||x.status==="investigating"', DASHBOARD)
        self.assertIn('/resolve', DASHBOARD)
        self.assertIn('verification_commit_sha', DASHBOARD)
        self.assertIn('confirm_owner_resolution:true', DASHBOARD)


if __name__ == "__main__":
    unittest.main()
