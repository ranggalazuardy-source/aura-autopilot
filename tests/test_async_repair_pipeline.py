import unittest

from app.patch_policy import ChangedFile
from app.services.async_repair_pipeline import prepare_repair_proposal_async

PATCH = (
    "diff --git a/app/agents/example.py b/app/agents/example.py\n"
    "index 1111111..2222222 100644\n"
    "--- a/app/agents/example.py\n"
    "+++ b/app/agents/example.py\n"
    "@@ -1 +1,2 @@\n"
    " old_value\n"
    "+new_value\n"
)
BASE = "a" * 40


class Generator:
    is_mock = False

    async def generate(self, incident, plan):
        self.incident, self.plan = incident, plan
        return PATCH, (ChangedFile("app/agents/example.py", "modified", 1, 0, 1),)


class AsyncRepairPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_generator_result_is_revalidated_by_sync_policy(self):
        incident = {
            "incident_id": "b" * 24,
            "source": "github_actions",
            "owner": "IT_AI_ENGINEER",
            "category": "automated_test_regression",
            "candidate_paths": ["app/agents/example.py"],
        }
        generator = Generator()
        proposal = await prepare_repair_proposal_async(incident, base_sha=BASE, generator=generator)
        self.assertEqual(proposal.status, "ready_for_owner_approval")
        self.assertTrue(proposal.provider_invoked)
        self.assertTrue(proposal.requires_owner_approval)
        self.assertFalse(proposal.files_written)
        self.assertFalse(proposal.github_written)

    async def test_generator_failure_is_blocked(self):
        class Failing:
            async def generate(self, incident, plan):
                raise RuntimeError("provider details must not leak")

        proposal = await prepare_repair_proposal_async(
            {"incident_id": "b" * 24, "category": "automated_test_regression",
             "candidate_paths": ["app/agents/example.py"]},
            base_sha=BASE, generator=Failing(),
        )
        self.assertEqual(proposal.status, "blocked")
        self.assertEqual(proposal.reasons, ("patch_generation_failed",))


if __name__ == "__main__":
    unittest.main()
