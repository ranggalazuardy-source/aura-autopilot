import ast
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
TREE = ast.parse(WORKER)


class RepairProposalLifecycleTests(unittest.TestCase):
    def function(self, name):
        return next(node for node in TREE.body
                    if isinstance(node, ast.AsyncFunctionDef) and node.name == name)

    def test_generation_persists_exact_diff_and_digest_before_return(self):
        source = ast.unparse(self.function("generate_ci_repair_proposal"))
        self.assertIn("repair_patch_proposals", source)
        self.assertIn("proposal.patch_text", source)
        self.assertIn("proposal.patch_sha256", source)
        self.assertIn("approved_paths_json", source)
        self.assertIn("REPAIR_PROPOSAL_TTL_SECONDS", source)

    def test_get_route_returns_persisted_diff_for_owner_review(self):
        route = self.function("get_repair_proposal")
        decorator = ast.unparse(route.decorator_list[0])
        source = ast.unparse(route)
        self.assertIn("Depends(require_api_key)", decorator)
        self.assertIn("repair_patch_proposals", source)
        self.assertIn("patch_text", source)
        self.assertIn("410", source)

    def test_approval_uses_persisted_proposal_and_strict_owner_confirmation(self):
        route = self.function("approve_repair_proposal")
        decorator = ast.unparse(route.decorator_list[0])
        source = ast.unparse(route)
        self.assertIn("Depends(require_api_key)", decorator)
        self.assertIn("StrictBool", ast.unparse(TREE))
        self.assertIn("confirm_owner_approval", source)
        self.assertIn("UPDATE repair_patch_proposals", source)
        self.assertIn("status = 'approving'", source)
        self.assertIn("issue_patch_approval_receipt", source)
        self.assertIn("row.patch_sha256", source)
        self.assertNotIn("payload.patch_text", source)
        self.assertNotIn("payload.approved_paths", source)

    def test_queue_uses_only_persisted_patch_and_matching_unused_receipt(self):
        route = self.function("queue_approved_repair_proposal")
        source = ast.unparse(route)
        self.assertIn("confirm_owner_queue", source)
        self.assertIn("row.patch_text", source)
        self.assertIn("row.approval_receipt_id", source)
        self.assertIn("consumed_at IS NULL", source)
        self.assertIn("create_execution_request", source)
        self.assertNotIn("payload.patch_text", source)
        self.assertNotIn("payload.approved_paths", source)
        self.assertNotIn("verify_and_consume", source)

    def test_queue_route_does_not_merge_or_deploy(self):
        source = ast.unparse(self.function("queue_approved_repair_proposal")).lower()
        self.assertNotIn("merge_pull_request", source)
        self.assertNotIn("deploy", source)

    def test_d1_schema_has_bounded_persisted_proposal_state_machine(self):
        db = sqlite3.connect(":memory:")
        db.executescript((ROOT / "cloudflare" / "schema.sql").read_text(encoding="utf-8"))
        columns = {row[1] for row in db.execute("PRAGMA table_info(repair_patch_proposals)")}
        self.assertTrue({
            "id", "incident_id", "base_sha", "patch_sha256", "patch_text",
            "approved_paths_json", "status", "expires_at", "approval_receipt_id",
            "execution_request_id",
        }.issubset(columns))
        sql = db.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='repair_patch_proposals'"
        ).fetchone()[0]
        for status in ("proposed", "approving", "approved", "queueing", "queued", "expired", "blocked"):
            self.assertIn(status, sql)


if __name__ == "__main__":
    unittest.main()
