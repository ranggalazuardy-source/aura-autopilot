import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)
SCHEMA = (ROOT / "cloudflare" / "schema.sql").read_text(encoding="utf-8")


class RepairIncidentTriageTests(unittest.TestCase):
    def function(self):
        return next(
            node for node in TREE.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "triage_repair_incident"
        )

    def test_triage_requires_owner_api_key(self):
        route = self.function()
        decorator = ast.unparse(route.decorator_list[0])
        self.assertIn("/repair/incidents/{incident_id}/triage", decorator)
        self.assertIn("Depends(require_api_key)", decorator)

    def test_triage_requires_strict_explicit_confirmation(self):
        model = next(
            node for node in TREE.body
            if isinstance(node, ast.ClassDef) and node.name == "RepairIncidentTriageIn"
        )
        source = ast.unparse(model)
        self.assertIn("StrictBool", source)
        self.assertIn("confirm_owner_triage", source)

    def test_only_low_risk_categories_can_have_candidate_paths(self):
        source = ast.unparse(self.function())
        self.assertIn("automated_test_regression", source)
        self.assertIn("python_syntax_or_import", source)
        self.assertIn("build_repair_plan", source)
        self.assertIn("High-risk or unclassified incidents cannot carry repair candidate paths", source)

    def test_triage_updates_only_existing_open_ci_incidents(self):
        source = ast.unparse(self.function())
        self.assertIn("source = 'github_actions'", source)
        self.assertIn("status IN ('open','investigating')", source)
        self.assertIn("UPDATE operational_incident_evidence", source)
        self.assertIn("UPDATE operational_incidents", source)
        self.assertIn("triage_owner = ?", source)
        self.assertIn("IT_AI_ENGINEER", source)
        self.assertIn("Incident Response Commander", source)
        self.assertIn("ready_for_owner_approval", source)

    def test_triage_never_generates_or_executes_patch(self):
        source = ast.unparse(self.function())
        self.assertIn("'patch_generated': False", source)
        self.assertIn("'files_written': False", source)
        self.assertIn("'merged': False", source)
        self.assertIn("'deployed': False", source)
        self.assertNotIn("prepare_it_engineer_repair", source)
        self.assertNotIn("execute_repair_proposal", source)

    def test_triage_audit_is_written(self):
        self.assertIn("operational.incident_triaged", ast.unparse(self.function()))

    def test_triage_response_exposes_explicit_repair_owner(self):
        source = ast.unparse(self.function())
        self.assertIn("owner", source)
        self.assertIn("IT_AI_ENGINEER", source)
        self.assertIn("Incident Response Commander", source)
        self.assertIn("ready_for_owner_approval", source)

    def test_schema_supports_only_known_triage_states(self):
        self.assertIn("triage_category TEXT NOT NULL DEFAULT 'unclassified' CHECK(triage_category IN", SCHEMA)
        self.assertIn("triage_owner TEXT NOT NULL DEFAULT 'Incident Response Commander'", SCHEMA)
        for category in (
            "automated_test_regression",
            "python_syntax_or_import",
            "dependency_or_security_audit",
            "database_schema",
            "cloudflare_deployment_or_config",
            "container_or_runtime",
            "unknown_or_unclassified",
        ):
            self.assertIn(category, SCHEMA)


if __name__ == "__main__":
    unittest.main()
