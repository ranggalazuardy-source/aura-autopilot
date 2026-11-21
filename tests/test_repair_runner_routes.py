import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class RepairRunnerRouteTests(unittest.TestCase):
    def route(self, name):
        return next(node for node in TREE.body
                    if isinstance(node, ast.AsyncFunctionDef) and node.name == name)

    def test_queue_poll_is_runner_authenticated_and_returns_only_reserved_metadata(self):
        source = ast.unparse(self.route("dispatch_next_repair_request"))
        self.assertIn("AURA_REPAIR_RUNNER_SECRET", source)
        self.assertIn("hmac.compare_digest", source)
        self.assertIn("dispatch_next_execution_request", source)

    def test_patch_retrieval_uses_separate_runner_secret_and_one_time_claim(self):
        source = ast.unparse(self.route("fetch_repair_patch"))
        self.assertIn("AURA_REPAIR_RUNNER_SECRET", source)
        self.assertIn("X-AURA-Runner-Key", source)
        self.assertIn("hmac.compare_digest", source)
        self.assertIn("claim_execution_patch", source)

    def test_execution_request_creation_requires_owner_api_key_and_receipt_match(self):
        route = self.route("create_repair_execution_request")
        decorator = ast.unparse(route.decorator_list[0])
        source = ast.unparse(route)
        self.assertIn("Depends(require_api_key)", decorator)
        self.assertIn("patch_approval_receipts", source)
        self.assertIn("consumed_at IS NULL", source)
        self.assertIn("create_execution_request", source)

    def test_write_authorization_consumes_receipt_before_token_eligibility(self):
        source = ast.unparse(self.route("authorize_repair_runner_write"))
        self.assertIn("AURA_REPAIR_RUNNER_SECRET", source)
        self.assertIn("D1PatchApprovalStore", source)
        self.assertIn("verify_and_consume", source)
        self.assertIn("owner_receipt_consumed", source)
        self.assertIn("write_token_eligible", source)

    def test_no_runner_route_can_merge_or_deploy(self):
        source = "\n".join(ast.unparse(self.route(name)) for name in (
            "dispatch_next_repair_request", "fetch_repair_patch", "create_repair_execution_request",
            "authorize_repair_runner_write",
        )).lower()
        self.assertNotIn("merge_pull_request", source)
        self.assertNotIn("deploy", source)


if __name__ == "__main__":
    unittest.main()
