import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
SCHEMA = (ROOT / "cloudflare" / "schema.sql").read_text(encoding="utf-8")
TREE = ast.parse(WORKER)


class PersistedRepairProposalRouteTests(unittest.TestCase):
    def function(self, name):
        return next(node for node in TREE.body
                    if isinstance(node, ast.AsyncFunctionDef) and node.name == name)

    def test_generation_persists_exact_patch_digest_paths_and_expiry(self):
        source = ast.unparse(self.function("generate_ci_repair_proposal"))
        for token in ("INSERT INTO repair_patch_proposals", "patch_text",
                      "patch_sha256", "approved_paths_json", "expires_at",
                      "operational.repair_patch_proposed"):
            self.assertIn(token, source)

    def test_read_route_returns_stored_patch_not_regenerated_patch(self):
        route = self.function("get_repair_proposal")
        source = ast.unparse(route)
        self.assertIn("Depends(require_api_key)", ast.unparse(route.decorator_list[0]))
        self.assertIn("SELECT", source)
        self.assertIn("patch_text", source)
        self.assertIn("410", source)
        self.assertNotIn("invoke_repair_patch_model", source)

    def test_approval_is_owner_bound_and_receipt_binds_exact_proposal(self):
        route = self.function("approve_repair_proposal")
        source = ast.unparse(route)
        self.assertIn("Depends(require_api_key)", ast.unparse(route.decorator_list[0]))
        for token in ("confirm_owner_approval", "AURA_API_KEY", "hashlib.sha256",
                      "issue_patch_approval_receipt", "base_sha", "patch_sha256",
                      "approved_paths", "status = 'approving'", "status = 'approved'"):
            self.assertIn(token, source)
        self.assertNotIn("owner_id", ast.unparse(route.args))

    def test_queue_requires_matching_unused_receipt_and_exact_stored_patch(self):
        route = self.function("queue_approved_repair_proposal")
        source = ast.unparse(route)
        for token in ("confirm_owner_queue", "approved_by", "incident_id", "base_sha",
                      "patch_sha256", "approved_paths_json", "consumed_at",
                      "revoked_at", "create_execution_request", "status = 'queueing'",
                      "status = 'queued'"):
            self.assertIn(token, source)
        self.assertIn("hashlib.sha256", source)
        self.assertNotIn("payload.patch_text", source)
        self.assertNotIn("payload.approved_paths", source)

    def test_schema_persists_expiring_proposals_with_constrained_states(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS repair_patch_proposals", SCHEMA)
        self.assertIn("REFERENCES operational_incidents(id)", SCHEMA)
        for state in ("proposed", "approving", "approved", "queueing", "queued", "expired", "blocked"):
            self.assertIn("'" + state + "'", SCHEMA)
        self.assertIn("idx_repair_patch_proposals_status_expiry", SCHEMA)

    def test_schema_ci_gate_requires_proposal_table(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertIn('"repair_patch_proposals"', workflow)


if __name__ == "__main__":
    unittest.main()
