from pathlib import Path
import unittest


class ProductionDeployGateTests(unittest.TestCase):
    def test_manual_dispatch_requires_explicit_yes_confirmation(self):
        workflow = Path(".github/workflows/deploy-cloudflare.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("confirm_production_deploy:", workflow)
        self.assertIn("required: true", workflow)
        self.assertIn("type: choice", workflow)
        self.assertIn("- 'no'", workflow)
        self.assertIn("- 'yes'", workflow)
        self.assertIn("default: 'no'", workflow)

    def test_production_job_is_limited_to_confirmed_main_branch_dispatch(self):
        workflow = Path(".github/workflows/deploy-cloudflare.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "if: github.ref == 'refs/heads/main' && "
            "inputs.confirm_production_deploy == 'yes'",
            workflow,
        )

    def test_deploy_workflow_has_no_automatic_push_or_pull_request_trigger(self):
        workflow = Path(".github/workflows/deploy-cloudflare.yml").read_text(
            encoding="utf-8"
        )
        trigger_block = workflow.split("permissions:", 1)[0]
        self.assertNotIn("push:", trigger_block)
        self.assertNotIn("pull_request:", trigger_block)


if __name__ == "__main__":
    unittest.main()
