import json
import unittest

from app.patch_policy import ChangedFile
from app.services.d1_triaged_ci_repair import prepare_triaged_ci_repair_from_d1


BASE = "b" * 40
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

    def generate(self, incident, plan):
        self.calls += 1
        return PATCH, FILES


class FakeStatement:
    def __init__(self, row):
        self.row = row
        self.bound = None

    def bind(self, *args):
        self.bound = args
        return self

    async def first(self):
        return self.row


class FakeD1:
    def __init__(self, row=None, error=None):
        self.statement = FakeStatement(row)
        self.error = error
        self.sql = None

    def prepare(self, sql):
        self.sql = sql
        if self.error:
            raise self.error
        return self.statement


class D1TriagedRepairTests(unittest.IsolatedAsyncioTestCase):
    def row(self, **updates):
        value = {
            "incident_id": "c" * 24,
            "source": "github_actions",
            "status": "investigating",
            "repository": "ranggalazuardy-source/aura-autopilot",
            "workflow_name": "AURA quality checks",
            "conclusion": "failure",
            "head_sha": BASE,
            "triage_category": "automated_test_regression",
            "candidate_paths_json": json.dumps(["app/agents/example.py"]),
            "triage_owner": "IT_AI_ENGINEER",
        }
        value.update(updates)
        return value

    async def test_reads_joined_persisted_evidence_and_prepares_proposal(self):
        db, generator = FakeD1(self.row()), FakeGenerator()
        result = await prepare_triaged_ci_repair_from_d1(
            db, "c" * 24, generator=generator, confirm_owner_generation=True
        )
        self.assertEqual(result.status, "ready_for_owner_approval")
        self.assertEqual(generator.calls, 1)
        self.assertEqual(db.statement.bound, ("c" * 24,))
        self.assertIn("INNER JOIN operational_incident_evidence", db.sql)
        self.assertIn("i.status", db.sql)

    async def test_missing_evidence_fails_before_generator(self):
        generator = FakeGenerator()
        result = await prepare_triaged_ci_repair_from_d1(
            FakeD1(None), "c" * 24, generator=generator, confirm_owner_generation=True
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("triaged_ci_evidence_not_found", result.reasons)
        self.assertEqual(generator.calls, 0)

    async def test_database_failure_fails_closed(self):
        generator = FakeGenerator()
        result = await prepare_triaged_ci_repair_from_d1(
            FakeD1(error=RuntimeError("database unavailable")), "c" * 24,
            generator=generator, confirm_owner_generation=True,
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("d1_evidence_read_failed", result.reasons)
        self.assertEqual(generator.calls, 0)

    async def test_confirmation_is_required_after_database_read(self):
        generator = FakeGenerator()
        result = await prepare_triaged_ci_repair_from_d1(
            FakeD1(self.row()), "c" * 24,
            generator=generator, confirm_owner_generation=False,
        )
        self.assertEqual(result.status, "blocked")
        self.assertEqual(generator.calls, 0)

    async def test_missing_database_or_invalid_id_fails_closed(self):
        generator = FakeGenerator()
        for db, incident_id in ((None, "c" * 24), (FakeD1(self.row()), "invalid")):
            result = await prepare_triaged_ci_repair_from_d1(
                db, incident_id, generator=generator, confirm_owner_generation=True
            )
            self.assertEqual(result.status, "blocked")
        self.assertEqual(generator.calls, 0)


if __name__ == "__main__":
    unittest.main()
