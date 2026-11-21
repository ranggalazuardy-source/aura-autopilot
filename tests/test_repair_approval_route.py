import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class RepairApprovalRouteTests(unittest.TestCase):
    def route(self):
        return next(
            node for node in TREE.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "issue_repair_approval"
        )

    def test_receipt_route_requires_api_key_dependency(self):
        route = self.route()
        decorator = route.decorator_list[0]
        self.assertIsInstance(decorator, ast.Call)
        self.assertEqual(ast.unparse(decorator.func), "app.post")
        self.assertEqual(ast.literal_eval(decorator.args[0]), "/repair/approvals")
        self.assertIn("Depends(require_api_key)", ast.unparse(decorator))

    def test_owner_confirmation_is_strict_and_required(self):
        model = next(node for node in TREE.body
                     if isinstance(node, ast.ClassDef)
                     and node.name == "PatchApprovalReceiptIn")
        field = next(node for node in model.body if isinstance(node, ast.AnnAssign)
                     and isinstance(node.target, ast.Name)
                     and node.target.id == "confirm_owner_approval")
        self.assertEqual(ast.unparse(field.annotation), "StrictBool")
        self.assertIn("payload.confirm_owner_approval is not True", ast.unparse(self.route()))

    def test_owner_identity_is_derived_from_server_secret_not_request_body(self):
        source = ast.unparse(self.route())
        self.assertIn("AURA_API_KEY", source)
        self.assertIn("hashlib.sha256(owner_key.encode", source)
        self.assertNotIn("payload.owner_id", source)
        self.assertIn("authenticated_owner_id=owner_id", source)

    def test_approval_issue_is_audited_and_only_returns_receipt_metadata(self):
        source = ast.unparse(self.route())
        self.assertIn("patch_approval.issued", source)
        self.assertIn("await write_audit", source)
        self.assertIn("receipt_id", source)
        self.assertIn("expires_in_seconds", source)

    def test_receipt_endpoint_does_not_enable_execution_merge_or_deploy(self):
        source = ast.unparse(self.route()).lower()
        self.assertNotIn("execute_approved_patch", source)
        self.assertNotIn("merge", source)
        self.assertNotIn("deploy", source)


if __name__ == "__main__":
    unittest.main()
