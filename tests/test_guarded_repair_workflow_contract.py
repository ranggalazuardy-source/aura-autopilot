"""Static security contract tests for the guarded repair runner workflow.

These tests inspect the checked-in workflow and preserve the boundary between
untrusted patch validation and the later, owner-authorized repository write.
"""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "guarded-repair-runner.yml").read_text(
    encoding="utf-8"
)


class GuardedRepairWorkflowContractTests(unittest.TestCase):
    def job(self, name: str) -> str:
        marker = f"  {name}:\n"
        self.assertIn(marker, WORKFLOW)
        start = WORKFLOW.index(marker) + len(marker)
        next_job = re.search(r"\n  [a-z][a-z0-9-]*:\n", WORKFLOW[start:])
        end = start + next_job.start() if next_job else len(WORKFLOW)
        return WORKFLOW[start:end]

    def test_runner_is_disabled_until_owner_enables_it(self):
        self.assertIn("if: vars.AURA_REPAIR_RUNNER_ENABLED == 'true'", self.job("acquire-request"))
        self.assertIn("schedule:", WORKFLOW)
        self.assertIn("workflow_dispatch:", WORKFLOW)

    def test_validation_job_has_read_only_permissions_and_no_write_credentials(self):
        validation = self.job("validate-patch")
        self.assertIn("permissions:\n      contents: read", validation)
        forbidden = (
            "AURA_REPAIR_APP_PRIVATE_KEY",
            "AURA_REPAIR_APP_ID",
            "create-github-app-token",
            "gh pr create",
            "git push",
            "GITHUB_TOKEN",
        )
        for value in forbidden:
            self.assertNotIn(value, validation)

    def test_publish_job_waits_for_validation_and_owner_receipt_consumption(self):
        publish = self.job("publish-draft-pr")
        self.assertIn("needs: [acquire-request, validate-patch]", publish)
        self.assertIn("authorize-write", publish)
        self.assertIn("create-github-app-token", publish)
        self.assertLess(publish.index("authorize-write"), publish.index("create-github-app-token"))

    def test_publish_job_creates_draft_pr_without_merge_or_deploy(self):
        publish = self.job("publish-draft-pr")
        self.assertIn("gh pr create --draft", publish)
        self.assertNotIn("gh pr merge", publish)
        self.assertNotIn("wrangler deploy", publish)
        self.assertNotIn("pywrangler deploy", publish)

    def test_queue_poll_uses_separate_runner_secret_and_no_patch_in_dispatch(self):
        acquire = self.job("acquire-request")
        self.assertIn("AURA_REPAIR_RUNNER_SECRET", acquire)
        self.assertIn("/repair/runner/next", acquire)
        self.assertNotIn("patch_text", acquire)


if __name__ == "__main__":
    unittest.main()
