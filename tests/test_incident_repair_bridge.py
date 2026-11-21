import unittest

from app.services.incident_repair_bridge import plan_from_incident


class IncidentRepairBridgeTests(unittest.TestCase):
    def test_explicit_low_risk_diagnostic_becomes_approval_gated_plan(self):
        result = plan_from_incident({
            "incident_id": "ci-44865476534",
            "category": "automated_test_regression",
            "candidate_paths": ["tests/test_repair.py"],
        })
        self.assertEqual(result["status"], "ready_for_owner_approval")
        self.assertTrue(result["requires_owner_approval"])
        self.assertFalse(result["provider_invocation"])
        self.assertFalse(result["file_changes"])
        self.assertFalse(result["github_write"])
        self.assertFalse(result["merge"])
        self.assertFalse(result["deploy"])

    def test_missing_candidate_paths_are_blocked_not_guessed(self):
        result = plan_from_incident({
            "incident_id": "ci-unknown-paths",
            "category": "automated_test_regression",
        })
        self.assertEqual(result["status"], "blocked")
        self.assertIn("no_candidate_paths", result["reasons"])

    def test_malformed_candidate_paths_are_blocked(self):
        for candidate_paths in ("tests/test_x.py", [None], {"path": "tests/test_x.py"}):
            with self.subTest(candidate_paths=candidate_paths):
                result = plan_from_incident({
                    "incident_id": "ci-malformed",
                    "category": "automated_test_regression",
                    "candidate_paths": candidate_paths,
                })
                self.assertEqual(result["status"], "blocked")
                self.assertIn("malformed_candidate_paths", result["reasons"])

    def test_high_risk_incident_remains_blocked(self):
        result = plan_from_incident({
            "incident_id": "ci-deploy",
            "category": "cloudflare_deployment_or_config",
            "candidate_paths": ["tests/test_x.py"],
        })
        self.assertEqual(result["status"], "blocked")

    def test_non_string_identity_and_category_fail_closed(self):
        result = plan_from_incident({
            "incident_id": 123,
            "category": None,
            "candidate_paths": ["tests/test_x.py"],
        })
        self.assertEqual(result["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
