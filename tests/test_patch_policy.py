import unittest

from app.patch_policy import ChangedFile, evaluate_patch


class PatchPolicyTests(unittest.TestCase):
    def test_small_agent_change_and_regression_test_are_allowed(self):
        result = evaluate_patch([
            ChangedFile("app/agents/research.py", "modified", 35, 8, 43),
            ChangedFile("tests/test_research_agent.py", "modified", 24, 0, 24),
        ])
        self.assertTrue(result.allowed)
        self.assertEqual(result.reasons, ())

    def test_worker_and_workflow_changes_are_blocked(self):
        result = evaluate_patch([
            ChangedFile("cloudflare/worker.py", "modified", 10, 2, 12),
            ChangedFile(".github/workflows/quality.yml", "modified", 2, 1, 3),
        ])
        self.assertFalse(result.allowed)
        self.assertTrue(any("path_outside_allowlist" in reason for reason in result.reasons))

    def test_security_billing_and_provider_paths_are_blocked(self):
        for path in (
            "app/services/authentication.py",
            "app/services/provider_router.py",
            "app/services/billing.py",
            "app/services/ledger_ops.py",
        ):
            with self.subTest(path=path):
                self.assertFalse(evaluate_patch([
                    ChangedFile(path, "modified", 1, 0, 1)
                ]).allowed)

    def test_new_deleted_renamed_or_binary_style_changes_fail_closed(self):
        for status in ("added", "removed", "renamed"):
            with self.subTest(status=status):
                self.assertFalse(evaluate_patch([
                    ChangedFile("tests/test_new.py", status, 1, 0, 1)
                ]).allowed)


    def test_malformed_metadata_types_fail_closed(self):
        for changed in (
            ChangedFile("tests/test_bad.py", "modified", True, 0, 1),
            ChangedFile("tests/test_bad.py", "modified", 1, 0, 3),
            ChangedFile(None, "modified", 1, 0, 1),
        ):
            with self.subTest(changed=changed):
                result = evaluate_patch([changed])
                self.assertFalse(result.allowed)

    def test_windows_absolute_and_null_byte_paths_are_rejected(self):
        for path in (
            "C:/workspace/tests/test_bad.py",
            "\\\\server\\share\\tests\\test_bad.py",
            "tests/test_bad.py\x00.py",
        ):
            with self.subTest(path=path):
                result = evaluate_patch([
                    ChangedFile(path, "modified", 1, 0, 1)
                ])
                self.assertFalse(result.allowed)

    def test_path_prefix_lookalikes_are_not_allowed(self):
        for path in (
            "tests-evil/test_bad.py",
            "app/agents-evil/test_bad.py",
            "docs_private/notes.md",
        ):
            with self.subTest(path=path):
                self.assertFalse(evaluate_patch([
                    ChangedFile(path, "modified", 1, 0, 1)
                ]).allowed)

    def test_change_size_limits_are_enforced(self):
        self.assertFalse(evaluate_patch([
            ChangedFile("docs/repair.md", "modified", 401, 0, 401)
        ]).allowed)
        self.assertFalse(evaluate_patch([
            ChangedFile("docs/repair.md", "modified", 0, 201, 201)
        ]).allowed)

    def test_empty_patch_and_path_traversal_are_rejected(self):
        self.assertFalse(evaluate_patch([]).allowed)
        self.assertFalse(evaluate_patch([
            ChangedFile("tests/../../secrets.env", "modified", 1, 0, 1)
        ]).allowed)


if __name__ == "__main__":
    unittest.main()
