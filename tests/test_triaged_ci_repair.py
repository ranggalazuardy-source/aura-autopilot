import json
import unittest

from app.patch_policy import ChangedFile
from app.services.triaged_ci_repair import prepare_triaged_ci_incident_repair


BASE = "a" * 40
PATCH = (
    "diff --git a/app/agents/example.py b/app/agents/example.py\n"
    "index 1111111..2222222 100644\n"
    "--- a/app/agents/example.py\n"
    "+++ b/app/agents/example.py\n"
    "@@ -1 +1,2 @@\n"
    " old_value\n"
    "+new_value\n"
)
FILES = (ChangedFile("app/agents/example.py", "modified", 1, 0, 1),)


class FakeGenerator:
    is_mock = True

    def __init__(self):
        self.calls = 0
        self.received = None

    def generate(self, incident, plan):
        self.calls += 1
        self.received = incident
        return PATCH, FILES


class TriagedCIRepairTests(unittest.TestCase):
    def evidence(self, **updates):
        row = {
            "incident_id": "a" * 24,
            "source": "github_actions",
            "status": "investigating",
            "repository": "ranggalazuardy-source/aura-autopilot",
            "workflow_name": "AURA quality checks",
            "conclusion": "failure",
            "head_sha": BASE,
            "triage_category": "automated_test_regression",
            "candidate_paths_json": json.dumps(["app/agents/example.py"]),
            "triage_owner": "IT_AI_ENGINEER",
            "failed_jobs_json": '["unit tests"]',
            "run_url": "https://github.com/untrusted/raw-log-link",
        }
        row.update(updates)
        return row

    def test_owner_confirmed_persisted_triage_reaches_mock_generator(self):
        generator = FakeGenerator()
        result = prepare_triaged_ci_incident_repair(
            self.evidence(), generator=generator, confirm_owner_generation=True
        )
        self.assertEqual(result.status, "ready_for_owner_approval")
        self.assertEqual(generator.calls, 1)
        self.assertEqual(generator.received["candidate_paths"], ["app/agents/example.py"])
        self.assertNotIn("run_url", generator.received)
        self.assertNotIn("failed_jobs_json", generator.received)
        self.assertTrue(result.requires_owner_approval)
        self.assertFalse(result.provider_invoked)
        self.assertFalse(result.files_written)
        self.assertFalse(result.github_written)

    def test_generation_confirmation_is_required_before_generator(self):
        generator = FakeGenerator()
        result = prepare_triaged_ci_incident_repair(
            self.evidence(), generator=generator, confirm_owner_generation=False
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("explicit_owner_generation_confirmation_required", result.reasons)
        self.assertEqual(generator.calls, 0)

    def test_rejects_untriaged_wrong_owner_and_high_risk_categories(self):
        cases = (
            ({"triage_owner": "Incident Response Commander"}, "incident_not_triaged_to_it_ai_engineer"),
            ({"triage_category": "database_schema"}, "triage_category_not_repair_eligible"),
            ({"status": "open"}, "incident_not_investigating"),
        )
        for update, reason in cases:
            with self.subTest(update=update):
                generator = FakeGenerator()
                result = prepare_triaged_ci_incident_repair(
                    self.evidence(**update), generator=generator,
                    confirm_owner_generation=True,
                )
                self.assertEqual(result.status, "blocked")
                self.assertIn(reason, result.reasons)
                self.assertEqual(generator.calls, 0)

    def test_rejects_wrong_repository_workflow_and_invalid_sha(self):
        cases = (
            ({"repository": "attacker/repo"}, "repository_not_allowlisted"),
            ({"workflow_name": "untrusted workflow"}, "workflow_not_allowlisted"),
            ({"head_sha": "not-a-commit"}, "invalid_base_sha"),
        )
        for update, reason in cases:
            with self.subTest(update=update):
                generator = FakeGenerator()
                result = prepare_triaged_ci_incident_repair(
                    self.evidence(**update), generator=generator,
                    confirm_owner_generation=True,
                )
                self.assertEqual(result.status, "blocked")
                self.assertIn(reason, result.reasons)
                self.assertEqual(generator.calls, 0)

    def test_rejects_malformed_or_missing_persisted_paths(self):
        for value in ('{"not":"a list"}', "not-json", "[]", '["../secrets"]'):
            with self.subTest(value=value):
                generator = FakeGenerator()
                result = prepare_triaged_ci_incident_repair(
                    self.evidence(candidate_paths_json=value), generator=generator,
                    confirm_owner_generation=True,
                )
                self.assertEqual(result.status, "blocked")
                self.assertEqual(generator.calls, 0)

    def test_live_generator_still_requires_provider_approval(self):
        class LiveGenerator(FakeGenerator):
            is_mock = False

        generator = LiveGenerator()
        result = prepare_triaged_ci_incident_repair(
            self.evidence(), generator=generator, confirm_owner_generation=True
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("provider_inference_not_approved", result.reasons)
        self.assertEqual(generator.calls, 0)


if __name__ == "__main__":
    unittest.main()
