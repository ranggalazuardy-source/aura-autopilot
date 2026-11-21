import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
DASHBOARD = (ROOT / "app" / "repair_dashboard.py").read_text(encoding="utf-8")
TREE = ast.parse(WORKER)


class RepairConsoleSelfTestTests(unittest.TestCase):
    def function(self, name):
        return next(node for node in TREE.body
                    if isinstance(node, ast.AsyncFunctionDef) and node.name == name)

    def test_self_test_route_requires_owner_auth_and_explicit_confirmation(self):
        route = self.function("create_repair_self_test")
        self.assertIn("Depends(require_api_key)", ast.unparse(route.decorator_list[0]))
        self.assertIn("confirm_owner_self_test", ast.unparse(route))
        self.assertIn("StrictBool", ast.unparse(next(
            node for node in TREE.body
            if isinstance(node, ast.ClassDef) and node.name == "RepairSelfTestIn"
        )))

    def test_self_test_is_d1_only_and_has_no_external_side_effects(self):
        source = ast.unparse(self.function("create_repair_self_test"))
        self.assertIn("operational_incidents", source)
        self.assertIn("self_test:repair_console:v1", source)
        self.assertIn("operational.repair_console_self_test_created", source)
        self.assertIn("'proposal_created': False", source)
        self.assertIn("'external_side_effects': False", source)
        self.assertNotIn("requests.", source.lower())
        self.assertNotIn("AsyncBoundedModelPatchGenerator", source)
        self.assertNotIn("create_execution_request", source)

    def test_self_test_triage_never_becomes_repair_eligible(self):
        source = ast.unparse(self.function("triage_repair_incident"))
        self.assertIn("row.source == 'self_test'", source)
        self.assertIn("Self-test incidents cannot carry repair candidate paths", source)
        self.assertIn("'repair_eligible': False", source)
        self.assertIn("'patch_generated': False", source)
        self.assertIn("'files_written': False", source)
        self.assertIn("'merged': False", source)
        self.assertIn("'deployed': False", source)

    def test_incident_inbox_includes_test_records_but_keeps_proposals_separate(self):
        source = ast.unparse(self.function("list_repair_incidents"))
        self.assertIn("i.source = 'self_test'", source)
        self.assertIn("AS is_test", source)
        proposal_list = self.function("list_repair_proposals")
        self.assertIn("repair_patch_proposals", ast.unparse(proposal_list))

    def test_console_marks_self_test_and_disables_proposal_generation(self):
        self.assertIn("Create safe self-test", DASHBOARD)
        self.assertIn('api("/repair/self-test"', DASHBOARD)
        self.assertIn('data-test="'+(test?', DASHBOARD)
        self.assertIn("!test&&", DASHBOARD)
        self.assertIn("Self-test records are permanently blocked", DASHBOARD)


if __name__ == "__main__":
    unittest.main()
