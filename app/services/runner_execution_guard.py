"""State-machine guard for the isolated repair runner credential boundary.

This is a pure policy object. The actual runner must call it at each stage and
must not expose write credentials to patch generation or quality-check steps.
"""

from dataclasses import dataclass
from enum import Enum


class RunnerStage(str, Enum):
    CREATED = "created"
    REQUEST_VERIFIED = "request_verified"
    RECEIPT_CONSUMED = "receipt_consumed"
    PATCH_VALIDATED = "patch_validated"
    QUALITY_PASSED = "quality_passed"
    WRITE_CREDENTIAL_MINTED = "write_credential_minted"
    BRANCH_CREATED = "branch_created"
    DRAFT_PR_CREATED = "draft_pr_created"
    BLOCKED = "blocked"


@dataclass
class RunnerExecutionGuard:
    """Enforce monotonic runner progression and late credential issuance."""

    stage: RunnerStage = RunnerStage.CREATED

    def advance(self, target: RunnerStage) -> None:
        transitions = {
            RunnerStage.CREATED: {RunnerStage.REQUEST_VERIFIED, RunnerStage.BLOCKED},
            RunnerStage.REQUEST_VERIFIED: {RunnerStage.RECEIPT_CONSUMED, RunnerStage.BLOCKED},
            RunnerStage.RECEIPT_CONSUMED: {RunnerStage.PATCH_VALIDATED, RunnerStage.BLOCKED},
            RunnerStage.PATCH_VALIDATED: {RunnerStage.QUALITY_PASSED, RunnerStage.BLOCKED},
            RunnerStage.QUALITY_PASSED: {RunnerStage.WRITE_CREDENTIAL_MINTED, RunnerStage.BLOCKED},
            RunnerStage.WRITE_CREDENTIAL_MINTED: {RunnerStage.BRANCH_CREATED, RunnerStage.BLOCKED},
            RunnerStage.BRANCH_CREATED: {RunnerStage.DRAFT_PR_CREATED, RunnerStage.BLOCKED},
            RunnerStage.DRAFT_PR_CREATED: set(),
            RunnerStage.BLOCKED: set(),
        }
        if not isinstance(target, RunnerStage) or target not in transitions[self.stage]:
            raise ValueError("runner_stage_transition_not_allowed")
        self.stage = target

    @property
    def may_mint_write_credential(self) -> bool:
        return self.stage == RunnerStage.QUALITY_PASSED

    @property
    def may_write_repository(self) -> bool:
        return self.stage in {
            RunnerStage.WRITE_CREDENTIAL_MINTED,
            RunnerStage.BRANCH_CREATED,
        }

    @property
    def terminal(self) -> bool:
        return self.stage in {RunnerStage.DRAFT_PR_CREATED, RunnerStage.BLOCKED}
