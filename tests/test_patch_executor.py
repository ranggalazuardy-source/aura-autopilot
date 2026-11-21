import hashlib
import unittest

from app.patch_executor import (
    PatchApproval,
    PatchExecutionRequest,
    execute_approved_patch,
)
from app.patch_policy import ChangedFile
from app.repair_planner import build_repair_plan


BASE_SHA = "a" * 40
PATCH = (
    "diff --git a/app/agents/demo.py b/app/agents/demo.py\n"
    "--- a/app/agents/demo.py\n"
    "+++ b/app/agents/demo.py\n"
    "@@ -1 +1,2 @@\n"
    " old_line\n"
    "+new_line\n"
)
PATHS = ("app/agents/demo.py",)


class FakeVerifier:
    def __init__(self, valid=True, raises=False):
        self.valid = valid
        self.raises = raises
        self.calls = 0

    def verify(self, approval):
        self.calls += 1
        if self.raises:
            raise RuntimeError("verification backend unavailable")
        return self.valid


class FakeWorkspace:
    def __init__(self, checks_pass=True, fail_at=None):
        self.checks_pass = checks_pass
        self.fail_at = fail_at
        self.calls = []

    def _fail(self, stage):
        if self.fail_at == stage:
            raise RuntimeError(f"{stage} adapter unavailable")

    def create_isolated_branch(self, branch_name, base_sha):
        self.calls.append(("branch", branch_name, base_sha))
        self._fail("branch")

    def apply_unified_diff(self, branch_name, patch_text):
        self.calls.append(("apply", branch_name, patch_text))
        self._fail("apply")

    def run_quality_checks(self, branch_name):
        self.calls.append(("checks", branch_name))
        self._fail("checks")
        return self.checks_pass

    def create_draft_pull_request(self, branch_name, title, body):
        self.calls.append(("draft_pr", branch_name, title, body))
        self._fail("draft_pr")
        return "https://github.com/example/repo/pull/123"


def make_request(patch=PATCH, base_sha=BASE_SHA, paths=PATHS):
    plan = build_repair_plan(
        "incident-123", "automated_test_regression", paths
    )
    approval = PatchApproval(
        approval_id="approval-456",
        approved_by="repo-owner",
        incident_id="incident-123",
        base_sha=base_sha,
        patch_sha256=hashlib.sha256(patch.encode("utf-8")).hexdigest(),
        approved_paths=tuple(paths),
    )
    return PatchExecutionRequest(
        plan=plan,
        patch_text=patch,
        changed_files=(ChangedFile(paths[0], "modified", 1, 0, 1),),
        base_sha=base_sha,
        approval=approval,
    )


class PatchExecutorTests(unittest.TestCase):
    def test_verified_approval_creates_tested_draft_pr_on_isolated_branch(self):
        request = make_request()
        verifier = FakeVerifier()
        workspace = FakeWorkspace()

        result = execute_approved_patch(request, verifier, workspace)

        self.assertEqual(result.status, "draft_pr_created")
        self.assertTrue(result.branch_name.startswith("aura/repair/incident-123-"))
        self.assertEqual(
            result.draft_pr_url, "https://github.com/example/repo/pull/123"
        )
        self.assertEqual(verifier.calls, 1)
        self.assertEqual([call[0] for call in workspace.calls],
                         ["branch", "apply", "checks", "draft_pr"])
        self.assertIn("not merged or deployed", workspace.calls[-1][3])

    def test_unverified_approval_has_no_workspace_side_effects(self):
        verifier = FakeVerifier(valid=False)
        workspace = FakeWorkspace()

        result = execute_approved_patch(make_request(), verifier, workspace)

        self.assertEqual(result.status, "blocked")
        self.assertIn("owner_approval_not_verified", result.reasons)
        self.assertEqual(workspace.calls, [])

    def test_approval_verifier_exception_fails_closed(self):
        verifier = FakeVerifier(raises=True)
        workspace = FakeWorkspace()

        result = execute_approved_patch(make_request(), verifier, workspace)

        self.assertEqual(result.status, "blocked")
        self.assertIn("approval_verification_failed", result.reasons)
        self.assertEqual(workspace.calls, [])

    def test_patch_digest_mismatch_is_rejected_before_verifier(self):
        request = make_request()
        request = PatchExecutionRequest(
            plan=request.plan,
            patch_text=request.patch_text + "# changed\n",
            changed_files=request.changed_files,
            base_sha=request.base_sha,
            approval=request.approval,
        )
        verifier = FakeVerifier()
        workspace = FakeWorkspace()

        result = execute_approved_patch(request, verifier, workspace)

        self.assertIn("approval_patch_digest_mismatch", result.reasons)
        self.assertEqual(verifier.calls, 0)
        self.assertEqual(workspace.calls, [])

    def test_base_sha_mismatch_is_rejected(self):
        request = make_request(base_sha="b" * 40)
        approval = PatchApproval(
            **{**request.approval.__dict__, "base_sha": "c" * 40}
        )
        request = PatchExecutionRequest(
            request.plan, request.patch_text, request.changed_files,
            request.base_sha, approval
        )
        workspace = FakeWorkspace()

        result = execute_approved_patch(request, FakeVerifier(), workspace)

        self.assertIn("approval_base_sha_mismatch", result.reasons)
        self.assertEqual(workspace.calls, [])

    def test_changed_paths_must_match_plan_and_owner_approval(self):
        request = make_request()
        approval = PatchApproval(
            **{**request.approval.__dict__, "approved_paths": ("tests/other.py",)}
        )
        request = PatchExecutionRequest(
            request.plan, request.patch_text, request.changed_files,
            request.base_sha, approval
        )
        workspace = FakeWorkspace()

        result = execute_approved_patch(request, FakeVerifier(), workspace)

        self.assertIn("changed_paths_do_not_match_owner_approval", result.reasons)
        self.assertEqual(workspace.calls, [])

    def test_failed_quality_checks_do_not_create_draft_pr(self):
        workspace = FakeWorkspace(checks_pass=False)

        result = execute_approved_patch(make_request(), FakeVerifier(), workspace)

        self.assertEqual(result.status, "checks_failed")
        self.assertEqual([call[0] for call in workspace.calls],
                         ["branch", "apply", "checks"])

    def test_blocked_plan_cannot_reach_workspace(self):
        request = make_request()
        blocked_plan = build_repair_plan(
            "incident-123", "cloudflare_deployment_or_config", PATHS
        )
        request = PatchExecutionRequest(
            blocked_plan, request.patch_text, request.changed_files,
            request.base_sha, request.approval
        )
        workspace = FakeWorkspace()

        result = execute_approved_patch(request, FakeVerifier(), workspace)

        self.assertIn("repair_plan_not_eligible", result.reasons)
        self.assertEqual(workspace.calls, [])

    def test_malformed_patch_text_fails_closed_without_exception(self):
        request = make_request()
        request = PatchExecutionRequest(
            request.plan, None, request.changed_files, request.base_sha,
            request.approval
        )
        verifier = FakeVerifier()
        workspace = FakeWorkspace()

        result = execute_approved_patch(request, verifier, workspace)

        self.assertEqual(result.status, "blocked")
        self.assertIn("invalid_patch_text", result.reasons)
        self.assertEqual(verifier.calls, 0)
        self.assertEqual(workspace.calls, [])

    def test_invalid_changed_file_entry_fails_closed(self):
        request = make_request()
        request = PatchExecutionRequest(
            request.plan, request.patch_text, ("not-a-file-record",),
            request.base_sha, request.approval
        )
        workspace = FakeWorkspace()

        result = execute_approved_patch(request, FakeVerifier(), workspace)

        self.assertIn("invalid_changed_file_entry", result.reasons)
        self.assertEqual(workspace.calls, [])

    def test_branch_creation_exception_stops_execution(self):
        workspace = FakeWorkspace(fail_at="branch")

        result = execute_approved_patch(make_request(), FakeVerifier(), workspace)

        self.assertEqual(result.status, "execution_failed")
        self.assertIn("isolated_branch_creation_failed", result.reasons)
        self.assertEqual([call[0] for call in workspace.calls], ["branch"])

    def test_patch_application_exception_stops_before_checks(self):
        workspace = FakeWorkspace(fail_at="apply")

        result = execute_approved_patch(make_request(), FakeVerifier(), workspace)

        self.assertEqual(result.status, "execution_failed")
        self.assertIn("patch_application_failed", result.reasons)
        self.assertEqual([call[0] for call in workspace.calls], ["branch", "apply"])

    def test_quality_check_exception_stops_before_draft_pr(self):
        workspace = FakeWorkspace(fail_at="checks")

        result = execute_approved_patch(make_request(), FakeVerifier(), workspace)

        self.assertEqual(result.status, "execution_failed")
        self.assertIn("quality_check_execution_failed", result.reasons)
        self.assertEqual([call[0] for call in workspace.calls],
                         ["branch", "apply", "checks"])

    def test_draft_pr_adapter_exception_fails_closed(self):
        workspace = FakeWorkspace(fail_at="draft_pr")

        result = execute_approved_patch(make_request(), FakeVerifier(), workspace)

        self.assertEqual(result.status, "execution_failed")
        self.assertIn("draft_pr_creation_failed", result.reasons)
        self.assertEqual([call[0] for call in workspace.calls],
                         ["branch", "apply", "checks", "draft_pr"])

    def test_non_github_pr_url_is_rejected(self):
        class BadUrlWorkspace(FakeWorkspace):
            def create_draft_pull_request(self, branch_name, title, body):
                self.calls.append(("draft_pr", branch_name, title, body))
                return "https://attacker.invalid/pull/123"

        workspace = BadUrlWorkspace()
        result = execute_approved_patch(make_request(), FakeVerifier(), workspace)

        self.assertEqual(result.status, "execution_failed")
        self.assertIn("invalid_draft_pr_url", result.reasons)


if __name__ == "__main__":
    unittest.main()
