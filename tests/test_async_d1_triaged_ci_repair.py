import json
import unittest

from app.services.async_d1_triaged_ci_repair import prepare_triaged_ci_repair_from_d1_async


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
        self.sql = ""

    def prepare(self, sql):
        self.sql = sql
        if self.error:
            raise self.error
        return self.statement


class FakeGenerator:
    is_mock = True

    async def generate(self, incident, plan):
        raise AssertionError("mock generator should not run for blocked or unconfirmed cases")


class AsyncD1TriagedRepairTests(unittest.IsolatedAsyncioTestCase):
    def row(self, **updates):
        value = {
            "incident_id": "c" * 24,
            "source": "github_actions",
            "status": "investigating",
            "repository": "ranggalazuardy-source/aura-autopilot",
            "workflow_name": "AURA quality checks",
            "conclusion": "failure",
            "head_sha": "d" * 40,
            "triage_category": "automated_test_regression",
            "candidate_paths_json": json.dumps(["app/agents/example.py"]),
            "triage_owner": "IT_AI_ENGINEER",
        }
        value.update(updates)
        return value

    async def test_missing_evidence_fails_closed(self):
        result = await prepare_triaged_ci_repair_from_d1_async(
            FakeD1(), "c" * 24, generator=FakeGenerator(), confirm_owner_generation=True
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("triaged_ci_evidence_not_found", result.reasons)

    async def test_d1_error_fails_closed(self):
        result = await prepare_triaged_ci_repair_from_d1_async(
            FakeD1(error=RuntimeError("offline")), "c" * 24,
            generator=FakeGenerator(), confirm_owner_generation=True,
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("d1_evidence_read_failed", result.reasons)

    async def test_requires_persisted_safe_triage_and_owner_confirmation(self):
        result = await prepare_triaged_ci_repair_from_d1_async(
            FakeD1(self.row()), "c" * 24,
            generator=FakeGenerator(), confirm_owner_generation=False,
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("explicit_owner_generation_confirmation_required", result.reasons)

    async def test_high_risk_category_never_invokes_generator(self):
        result = await prepare_triaged_ci_repair_from_d1_async(
            FakeD1(self.row(triage_category="database_schema")), "c" * 24,
            generator=FakeGenerator(), confirm_owner_generation=True,
        )
        self.assertEqual(result.status, "blocked")
        self.assertIn("triage_category_not_repair_eligible", result.reasons)

    async def test_query_joins_persisted_incident_and_evidence_by_id(self):
        db = FakeD1(self.row())
        result = await prepare_triaged_ci_repair_from_d1_async(
            db, "c" * 24, generator=FakeGenerator(), confirm_owner_generation=False
        )
        self.assertIn("INNER JOIN operational_incident_evidence", db.sql)
        self.assertEqual(db.statement.bound, ("c" * 24,))
        self.assertEqual(result.status, "blocked")


if __name__ == "__main__":
    unittest.main()
