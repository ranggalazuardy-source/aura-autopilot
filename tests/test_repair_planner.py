import unittest

from app.repair_planner import build_repair_plan


class RepairPlannerTests(unittest.TestCase):
    def test_safe_test_regression_builds_approval_gated_plan(self):
        plan = build_repair_plan(
            "incident-123",
            "automated_test_regression",
            ["app/agents/research.py", "tests/test_research.py"],
        )
        self.assertEqual(plan.status, "ready_for_owner_approval")
        self.assertTrue(plan.requires_owner_approval)
        self.assertFalse(plan.provider_invocation)
        self.assertFalse(plan.file_changes)
        self.assertFalse(plan.github_write)
        self.assertFalse(plan.merge)
        self.assertFalse(plan.deploy)

    def test_python_error_can_be_planned_only_in_allowlisted_scope(self):
        plan = build_repair_plan(
            "incident-124", "python_syntax_or_import", ["app/services/queue.py"]
        )
        self.assertEqual(plan.status, "ready_for_owner_approval")

    def test_unknown_and_high_risk_categories_are_blocked(self):
        for category in (
            "unknown_or_unclassified",
            "dependency_or_security_audit",
            "database_schema",
            "cloudflare_deployment_or_config",
            "container_or_runtime",
        ):
            with self.subTest(category=category):
                plan = build_repair_plan("incident-125", category, ["tests/test_x.py"])
                self.assertEqual(plan.status, "blocked")

    def test_sensitive_and_out_of_scope_paths_are_blocked(self):
        for path in (
            "cloudflare/worker.py",
            ".github/workflows/quality.yml",
            "app/services/auth.py",
            "../secrets.env",
        ):
            with self.subTest(path=path):
                plan = build_repair_plan(
                    "incident-126", "automated_test_regression", [path]
                )
                self.assertEqual(plan.status, "blocked")

    def test_empty_too_many_paths_and_invalid_incident_are_blocked(self):
        self.assertEqual(
            build_repair_plan("incident-127", "automated_test_regression", []).status,
            "blocked",
        )
        self.assertEqual(
            build_repair_plan(
                "incident-128",
                "automated_test_regression",
                [f"tests/test_{i}.py" for i in range(7)],
            ).status,
            "blocked",
        )
        self.assertEqual(
            build_repair_plan("", "automated_test_regression", ["tests/test_x.py"]).status,
            "blocked",
        )


if __name__ == "__main__":
    unittest.main()
