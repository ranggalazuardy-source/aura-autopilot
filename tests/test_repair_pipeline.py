import hashlib
import unittest

from app.patch_executor import PatchApproval
from app.patch_policy import ChangedFile
from app.services.repair_pipeline import (
    build_execution_request,
    prepare_repair_proposal,
)


BASE = "a" * 40
DIFF = (
    "diff --git a/app/agents/demo.py b/app/agents/demo.py\n"
    "index 1111111..2222222 100644\n"
    "--- a/app/agents/demo.py\n"
    "+++ b/app/agents/demo.py\n"
    "@@ -1 +1,2 @@ demo\n"
    " old_line\n"
    "+new_line\n"
)
FILES = (ChangedFile("app/agents/demo.py", "modified", 1, 0, 1),)


class FakeGenerator:
    def __init__(self, result=(DIFF, FILES), error=None):
        self.result = result
        self.error = error
        self.called = False

    def generate(self, incident, plan):
        self.called = True
        if self.error:
            raise self.error
        return self.result


class RepairPipelineTests(unittest.TestCase):
    def incident(self, **updates):
        value = {
            "incident_id": "ci-incident-123",
            "category": "automated_test_regression",
            "candidate_paths": ["app/agents/demo.py"],
        }
        value.update(updates)
        return value

    def proposal(self):
        return prepare_repair_proposal(
            self.incident(), base_sha=BASE, generator=FakeGenerator()
        )

    def approval_for(self, proposal):
        return PatchApproval(
            approval_id="opaque-receipt",
            approved_by="owner-hash",
            incident_id=proposal.incident_id,
            base_sha=proposal.base_sha,
            patch_sha256=proposal.patch_sha256,
            approved_paths=proposal.changed_paths,
        )

    def test_valid_incident_returns_proposal_without_side_effect_flags(self):
        generator = FakeGenerator()
        result = prepare_repair_proposal(self.incident(), base_sha=BASE, generator=generator)
        self.assertEqual(result.status, "ready_for_owner_approval")
        self.assertEqual(result.changed_paths, ("app/agents/demo.py",))
        self.assertEqual(len(result.patch_sha256), 64)
        self.assertIsNotNone(result.plan)
        self.assertEqual(result.changed_files, FILES)
        self.assertTrue(result.requires_owner_approval)
        self.assertFalse(result.provider_invoked)
        self.assertFalse(result.files_written)
        self.assertFalse(result.github_written)
        self.assertFalse(result.merged)
        self.assertFalse(result.deployed)
        self.assertTrue(generator.called)

    def test_unsupported_category_blocks_before_generator(self):
        generator = FakeGenerator()
        result = prepare_repair_proposal(
            self.incident(category="database_schema"), base_sha=BASE, generator=generator
        )
        self.assertEqual(result.status, "blocked")
        self.assertFalse(generator.called)

    def test_missing_candidate_paths_blocks_before_generator(self):
        generator = FakeGenerator()
        result = prepare_repair_proposal(
            self.incident(candidate_paths=[]), base_sha=BASE, generator=generator
        )
        self.assertEqual(result.status, "blocked")
        self.assertFalse(generator.called)

    def test_invalid_base_sha_blocks_before_generator(self):
        generator = FakeGenerator()
        result = prepare_repair_proposal(self.incident(), base_sha="main", generator=generator)
        self.assertEqual(result.status, "blocked")
        self.assertFalse(generator.called)

    def test_generated_paths_must_match_explicit_incident_candidates(self):
        generator = FakeGenerator(result=(DIFF, (ChangedFile("tests/other.py", "modified", 1, 0, 1),)))
        result = prepare_repair_proposal(self.incident(), base_sha=BASE, generator=generator)
        self.assertEqual(result.status, "blocked")

    def test_malformed_generator_result_fails_closed(self):
        generator = FakeGenerator(result={"patch": DIFF})
        result = prepare_repair_proposal(self.incident(), base_sha=BASE, generator=generator)
        self.assertEqual(result.status, "blocked")
        self.assertIn("invalid_generator_result", result.reasons)

    def test_generator_exception_fails_closed(self):
        generator = FakeGenerator(error=RuntimeError("provider unavailable"))
        result = prepare_repair_proposal(self.incident(), base_sha=BASE, generator=generator)
        self.assertEqual(result.status, "blocked")
        self.assertIn("patch_generation_failed", result.reasons)

    def test_invalid_incident_type_fails_closed(self):
        result = prepare_repair_proposal([], base_sha=BASE, generator=FakeGenerator())
        self.assertEqual(result.status, "blocked")

    def test_proposal_converts_to_executor_request_only_with_matching_receipt(self):
        proposal = self.proposal()
        request = build_execution_request(proposal, self.approval_for(proposal))
        self.assertEqual(request.plan, proposal.plan)
        self.assertEqual(request.patch_text, DIFF)
        self.assertEqual(request.base_sha, BASE)
        self.assertEqual(request.approval.patch_sha256, hashlib.sha256(DIFF.encode()).hexdigest())

    def test_conversion_rejects_wrong_incident_receipt(self):
        proposal = self.proposal()
        approval = self.approval_for(proposal)
        wrong = PatchApproval(
            approval_id=approval.approval_id, approved_by=approval.approved_by,
            incident_id="other-incident", base_sha=approval.base_sha,
            patch_sha256=approval.patch_sha256, approved_paths=approval.approved_paths,
        )
        with self.assertRaisesRegex(ValueError, "does not match"):
            build_execution_request(proposal, wrong)

    def test_conversion_rejects_changed_patch_digest(self):
        proposal = self.proposal()
        tampered = type(proposal)(
            **{**proposal.__dict__, "patch_text": proposal.patch_text + "# tampered\n"}
        )
        with self.assertRaisesRegex(ValueError, "digest changed"):
            build_execution_request(tampered, self.approval_for(proposal))

    def test_blocked_proposal_cannot_be_converted(self):
        blocked = prepare_repair_proposal(
            self.incident(category="database_schema"), base_sha=BASE, generator=FakeGenerator()
        )
        with self.assertRaisesRegex(ValueError, "not eligible"):
            build_execution_request(blocked, self.approval_for(self.proposal()))


if __name__ == "__main__":
    unittest.main()
