import unittest

from app.services.runner_execution_guard import RunnerExecutionGuard, RunnerStage


class RunnerExecutionGuardTests(unittest.TestCase):
    def test_write_credential_is_blocked_until_quality_passes(self):
        guard = RunnerExecutionGuard()
        self.assertFalse(guard.may_mint_write_credential)
        with self.assertRaisesRegex(ValueError, "transition_not_allowed"):
            guard.advance(RunnerStage.WRITE_CREDENTIAL_MINTED)
        guard.advance(RunnerStage.REQUEST_VERIFIED)
        guard.advance(RunnerStage.RECEIPT_CONSUMED)
        guard.advance(RunnerStage.PATCH_VALIDATED)
        self.assertFalse(guard.may_mint_write_credential)
        guard.advance(RunnerStage.QUALITY_PASSED)
        self.assertTrue(guard.may_mint_write_credential)

    def test_repository_write_requires_late_credential_stage(self):
        guard = RunnerExecutionGuard()
        self.assertFalse(guard.may_write_repository)
        for stage in (
            RunnerStage.REQUEST_VERIFIED,
            RunnerStage.RECEIPT_CONSUMED,
            RunnerStage.PATCH_VALIDATED,
            RunnerStage.QUALITY_PASSED,
        ):
            guard.advance(stage)
            self.assertFalse(guard.may_write_repository)
        guard.advance(RunnerStage.WRITE_CREDENTIAL_MINTED)
        self.assertTrue(guard.may_write_repository)
        guard.advance(RunnerStage.BRANCH_CREATED)
        self.assertTrue(guard.may_write_repository)

    def test_receipt_consumption_must_precede_patch_validation(self):
        guard = RunnerExecutionGuard()
        guard.advance(RunnerStage.REQUEST_VERIFIED)
        with self.assertRaisesRegex(ValueError, "transition_not_allowed"):
            guard.advance(RunnerStage.PATCH_VALIDATED)

    def test_quality_must_pass_before_credential_mint(self):
        guard = RunnerExecutionGuard()
        for stage in (
            RunnerStage.REQUEST_VERIFIED,
            RunnerStage.RECEIPT_CONSUMED,
            RunnerStage.PATCH_VALIDATED,
        ):
            guard.advance(stage)
        with self.assertRaisesRegex(ValueError, "transition_not_allowed"):
            guard.advance(RunnerStage.WRITE_CREDENTIAL_MINTED)

    def test_blocked_stage_is_terminal(self):
        guard = RunnerExecutionGuard()
        guard.advance(RunnerStage.BLOCKED)
        self.assertTrue(guard.terminal)
        with self.assertRaisesRegex(ValueError, "transition_not_allowed"):
            guard.advance(RunnerStage.REQUEST_VERIFIED)

    def test_full_happy_path_is_monotonic(self):
        guard = RunnerExecutionGuard()
        for stage in (
            RunnerStage.REQUEST_VERIFIED,
            RunnerStage.RECEIPT_CONSUMED,
            RunnerStage.PATCH_VALIDATED,
            RunnerStage.QUALITY_PASSED,
            RunnerStage.WRITE_CREDENTIAL_MINTED,
            RunnerStage.BRANCH_CREATED,
            RunnerStage.DRAFT_PR_CREATED,
        ):
            guard.advance(stage)
        self.assertTrue(guard.terminal)
        self.assertEqual(guard.stage, RunnerStage.DRAFT_PR_CREATED)

    def test_cannot_mint_token_after_draft_pr(self):
        guard = RunnerExecutionGuard()
        for stage in (
            RunnerStage.REQUEST_VERIFIED,
            RunnerStage.RECEIPT_CONSUMED,
            RunnerStage.PATCH_VALIDATED,
            RunnerStage.QUALITY_PASSED,
            RunnerStage.WRITE_CREDENTIAL_MINTED,
            RunnerStage.BRANCH_CREATED,
            RunnerStage.DRAFT_PR_CREATED,
        ):
            guard.advance(stage)
        with self.assertRaisesRegex(ValueError, "transition_not_allowed"):
            guard.advance(RunnerStage.WRITE_CREDENTIAL_MINTED)


if __name__ == "__main__":
    unittest.main()
