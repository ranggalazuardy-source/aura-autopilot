import hashlib
import unittest

from app.patch_executor import PatchApproval, PatchExecutionRequest
from app.patch_policy import ChangedFile
from app.repair_planner import build_repair_plan
from app.services.async_patch_execution import execute_approved_patch_with_d1


BASE_SHA = "a" * 40
PATCH = (
    "diff --git a/app/agents/demo.py b/app/agents/demo.py\n"
    "--- a/app/agents/demo.py\n"
    "+++ b/app/agents/demo.py\n"
    "@@ -1 +1,2 @@\n"
    " old_line\n"
    "+new_line\n"
)


def make_request(patch=PATCH):
    plan = build_repair_plan("incident-123", "automated_test_regression", ("app/agents/demo.py",))
    approval = PatchApproval(
        "receipt-123", "owner-1", "incident-123", BASE_SHA,
        hashlib.sha256(patch.encode()).hexdigest(), ("app/agents/demo.py",)
    )
    return PatchExecutionRequest(
        plan, patch, (ChangedFile("app/agents/demo.py", "modified", 1, 0, 1),),
        BASE_SHA, approval
    )


class FakeD1Statement:
    def __init__(self, db, sql):
        self.db, self.sql, self.values = db, sql, ()

    def bind(self, *values):
        self.values = values
        return self

    async def first(self):
        self.db.calls.append((self.sql, self.values))
        if self.db.raises:
            raise RuntimeError("D1 unavailable")
        if self.db.consumed:
            return None
        self.db.consumed = True
        return {"id": self.values[1]}


class FakeD1:
    def __init__(self, raises=False):
        self.raises = raises
        self.consumed = False
        self.calls = []

    def prepare(self, sql):
        return FakeD1Statement(self, sql)


class FakeWorkspace:
    def __init__(self):
        self.calls = []

    def create_isolated_branch(self, branch_name, base_sha):
        self.calls.append("branch")

    def apply_unified_diff(self, branch_name, patch_text):
        self.calls.append("apply")

    def run_quality_checks(self, branch_name):
        self.calls.append("checks")
        return True

    def create_draft_pull_request(self, branch_name, title, body):
        self.calls.append("draft")
        return "https://github.com/example/repo/pull/123"


class AsyncPatchExecutionTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_receipt_is_consumed_before_workspace_side_effects(self):
        db, workspace = FakeD1(), FakeWorkspace()
        result = await execute_approved_patch_with_d1(
            make_request(), db=db, workspace=workspace, clock=lambda: 1000
        )
        self.assertEqual(result.status, "draft_pr_created")
        self.assertTrue(db.consumed)
        self.assertEqual(workspace.calls, ["branch", "apply", "checks", "draft"])
        self.assertIn("consumed_at IS NULL", db.calls[0][0])

    async def test_replayed_receipt_is_blocked_before_workspace(self):
        db, workspace = FakeD1(), FakeWorkspace()
        db.consumed = True
        result = await execute_approved_patch_with_d1(
            make_request(), db=db, workspace=workspace, clock=lambda: 1000
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("owner_approval_not_verified", result.reasons)
        self.assertEqual(workspace.calls, [])

    async def test_invalid_patch_is_rejected_before_d1_is_touched(self):
        db, workspace = FakeD1(), FakeWorkspace()
        request = make_request()
        invalid = PatchExecutionRequest(
            request.plan, request.patch_text + "# tampered\n",
            request.changed_files, request.base_sha, request.approval
        )
        result = await execute_approved_patch_with_d1(
            invalid, db=db, workspace=workspace, clock=lambda: 1000
        )
        self.assertEqual(result.status, "blocked")
        self.assertEqual(db.calls, [])
        self.assertEqual(workspace.calls, [])

    async def test_d1_failure_fails_closed(self):
        db, workspace = FakeD1(raises=True), FakeWorkspace()
        result = await execute_approved_patch_with_d1(
            make_request(), db=db, workspace=workspace, clock=lambda: 1000
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("approval_verification_failed", result.reasons)
        self.assertEqual(workspace.calls, [])

    async def test_quality_failure_does_not_create_draft_pr(self):
        class FailingWorkspace(FakeWorkspace):
            def run_quality_checks(self, branch_name):
                self.calls.append("checks")
                return False

        db, workspace = FakeD1(), FailingWorkspace()
        result = await execute_approved_patch_with_d1(
            make_request(), db=db, workspace=workspace, clock=lambda: 1000
        )
        self.assertEqual(result.status, "checks_failed")
        self.assertEqual(workspace.calls, ["branch", "apply", "checks"])


if __name__ == "__main__":
    unittest.main()
