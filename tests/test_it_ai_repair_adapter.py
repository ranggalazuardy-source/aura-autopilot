import unittest

from app.patch_policy import ChangedFile
from app.services.it_ai_repair_adapter import prepare_it_engineer_repair


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


class FakeITEngineerGenerator:
    is_mock = True

    def generate(self, incident, plan):
        return PATCH, FILES


class NonMockGenerator:
    is_mock = False

    def generate(self, incident, plan):
        raise AssertionError("must not be called without provider approval")


class ITAIRepairAdapterTests(unittest.TestCase):
    def incident(self, **updates):
        data = {
            "incident_id": "ci-incident-001",
            "category": "automated_test_regression",
            "candidate_paths": ["app/agents/example.py"],
            "source": "github_actions",
            "owner": "IT_AI_ENGINEER",
        }
        data.update(updates)
        return data

    def test_hands_safe_incident_to_injected_mock_generator(self):
        result = prepare_it_engineer_repair(
            self.incident(), base_sha=BASE, generator=FakeITEngineerGenerator()
        )
        self.assertEqual(result.status, "ready_for_owner_approval")
        self.assertEqual(result.changed_paths, ("app/agents/example.py",))
        self.assertTrue(result.requires_owner_approval)
        self.assertFalse(result.provider_invoked)
        self.assertFalse(result.github_written)
        self.assertFalse(result.merged)
        self.assertFalse(result.deployed)

    def test_rejects_live_generator_without_explicit_provider_approval(self):
        result = prepare_it_engineer_repair(
            self.incident(), base_sha=BASE, generator=NonMockGenerator()
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("provider_inference_not_approved", result.reasons)

    def test_rejects_wrong_owner_or_source_before_generator(self):
        for update, reason in (
            ({"owner": "DEVOPS_AUTOMATOR"}, "incident_not_owned_by_it_ai_engineer"),
            ({"source": "external_webhook"}, "unsupported_incident_source"),
        ):
            with self.subTest(update=update):
                result = prepare_it_engineer_repair(
                    self.incident(**update), base_sha=BASE,
                    generator=NonMockGenerator(),
                )
                self.assertEqual(result.status, "blocked")
                self.assertIn(reason, result.reasons)

    def test_does_not_invent_missing_candidate_paths(self):
        result = prepare_it_engineer_repair(
            self.incident(candidate_paths=[]), base_sha=BASE,
            generator=FakeITEngineerGenerator(),
        )
        self.assertEqual(result.status, "blocked")
        self.assertFalse(result.patch_text)

    def test_blocks_sensitive_or_high_risk_candidate_paths(self):
        result = prepare_it_engineer_repair(
            self.incident(candidate_paths=["cloudflare/worker.py"]),
            base_sha=BASE, generator=FakeITEngineerGenerator(),
        )
        self.assertEqual(result.status, "blocked")
        self.assertFalse(result.patch_text)


if __name__ == "__main__":
    unittest.main()
