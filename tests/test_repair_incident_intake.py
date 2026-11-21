import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER_SOURCE = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
WORKER_TREE = ast.parse(WORKER_SOURCE)
SCHEMA = (ROOT / "cloudflare" / "schema.sql").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "incident-intake.yml").read_text(encoding="utf-8")


class RepairIncidentIntakeTests(unittest.TestCase):
    def function(self, name):
        return next(
            node for node in WORKER_TREE.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == name
        )

    def test_intake_route_requires_owner_api_key(self):
        route = self.function("ingest_ci_incident")
        decorator = ast.unparse(route.decorator_list[0])
        self.assertIn('"/repair/incidents"', decorator)
        self.assertIn("Depends(require_api_key)", decorator)

    def test_intake_accepts_only_fixed_repository_and_known_workflows(self):
        model = next(
            node for node in WORKER_TREE.body
            if isinstance(node, ast.ClassDef) and node.name == "CIIncidentIntakeIn"
        )
        source = ast.unparse(model)
        self.assertIn("ranggalazuardy-source/aura-autopilot", source)
        self.assertIn("AURA quality checks", source)
        self.assertIn("Deploy AURA to Cloudflare", source)
        self.assertIn("^[0-9a-f]{40}$", source)

    def test_intake_validates_canonical_run_url_and_failed_job_labels(self):
        source = ast.unparse(self.function("ingest_ci_incident"))
        self.assertIn("urlsplit", source)
        self.assertIn("github.com", source)
        self.assertIn("failed job names must be short, plain-text labels", source.lower())

    def test_incident_remains_unclassified_and_not_repair_eligible(self):
        source = ast.unparse(self.function("ingest_ci_incident"))
        self.assertIn("'unclassified'", source)
        self.assertIn("'candidate_paths': []", source)
        self.assertIn("'repair_eligible': False", source)
        self.assertNotIn("prepare_it_engineer_repair", source)
        self.assertNotIn("patch_text", source)

    def test_incident_evidence_is_sanitized_and_audited(self):
        source = ast.unparse(self.function("ingest_ci_incident"))
        self.assertIn("record_operational_incident", source)
        self.assertIn("operational_incident_evidence", source)
        self.assertIn("operational.ci_evidence_ingested", source)
        self.assertNotIn("request.body", source.lower())

    def test_owner_can_list_incidents_but_endpoint_is_read_only(self):
        route = self.function("list_repair_incidents")
        decorator = ast.unparse(route.decorator_list[0])
        source = ast.unparse(route)
        self.assertIn("Depends(require_api_key)", decorator)
        self.assertIn("operational_incident_evidence", source)
        self.assertNotIn(".insert(", source.lower())
        self.assertNotIn("patch", source.lower())

    def test_schema_keeps_candidate_paths_empty_and_category_unclassified(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS operational_incident_evidence", SCHEMA)
        self.assertIn("triage_category TEXT NOT NULL DEFAULT 'unclassified'", SCHEMA)
        self.assertIn("candidate_paths_json TEXT NOT NULL DEFAULT '[]'", SCHEMA)
        self.assertIn("CHECK(length(head_sha) = 40)", SCHEMA)

    def test_github_workflow_sends_only_metadata_when_secret_exists(self):
        self.assertIn("secrets.AURA_API_KEY", WORKFLOW)
        self.assertIn("/repair/incidents", WORKFLOW)
        self.assertIn("failed_jobs", WORKFLOW)
        self.assertIn("AURA_API_KEY repository secret is not configured", WORKFLOW)
        self.assertNotIn("AURA_REPAIR_RUNNER_SECRET", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
