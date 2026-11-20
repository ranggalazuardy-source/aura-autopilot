import os
import tempfile
import unittest
from pathlib import Path

# Isolate the local FastAPI development database before importing the app module.
_TEST_DIRECTORY = tempfile.TemporaryDirectory(prefix="aura-local-api-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_TEST_DIRECTORY.name) / 'test.db'}"
os.environ["AURA_API_KEY"] = "aura-test-key-not-for-production"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)
AUTH = {"X-AURA-API-Key": os.environ["AURA_API_KEY"]}


class LocalApiSecurityTests(unittest.TestCase):
    def test_health_and_config_remain_public(self):
        self.assertEqual(client.get("/health").status_code, 200)
        response = client.get("/config")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["production_ready"])

    def test_private_read_endpoints_require_api_key(self):
        for path in ("/opportunities", "/approvals", "/ledger", "/ledger/summary", "/audit"):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 401)
                self.assertEqual(client.get(path, headers={"X-AURA-API-Key": "wrong"}).status_code, 401)

    def test_private_write_endpoints_require_api_key(self):
        requests = (
            ("/opportunities", {"title": "Valid idea", "channel": "YouTube", "rationale": "Test"}),
            ("/approvals", {"action_type": "purchase", "description": "Test purchase", "amount": 0}),
            ("/ledger", {"entry_type": "income", "category": "test", "amount": 1}),
        )
        for path, payload in requests:
            with self.subTest(path=path):
                self.assertEqual(client.post(path, json=payload).status_code, 401)

    def test_authenticated_mutations_are_audited(self):
        opportunity = client.post(
            "/opportunities",
            headers=AUTH,
            json={"title": "Valid idea", "channel": "YouTube", "rationale": "Demand research"},
        )
        self.assertEqual(opportunity.status_code, 200)
        self.assertEqual(client.get("/opportunities", headers=AUTH).status_code, 200)

        approval = client.post(
            "/approvals",
            headers=AUTH,
            json={"action_type": "purchase", "description": "Owner review required", "amount": 0},
        )
        self.assertEqual(approval.status_code, 200)
        approval_id = approval.json()["id"]
        decision = client.post(
            f"/approvals/{approval_id}/decision?decision=approved",
            headers=AUTH,
        )
        self.assertEqual(decision.status_code, 200)
        self.assertEqual(decision.json()["execution"], "not_executed")
        repeated = client.post(
            f"/approvals/{approval_id}/decision?decision=rejected",
            headers=AUTH,
        )
        self.assertEqual(repeated.status_code, 409)

        ledger = client.post(
            "/ledger",
            headers=AUTH,
            json={"entry_type": "income", "category": "test", "amount": 12500},
        )
        self.assertEqual(ledger.status_code, 200)
        summary = client.get("/ledger/summary", headers=AUTH).json()
        self.assertEqual(summary["income"], 12500)
        self.assertGreaterEqual(summary["entries"], 1)

        audit = client.get("/audit", headers=AUTH)
        self.assertEqual(audit.status_code, 200)
        event_types = {entry["event_type"] for entry in audit.json()}
        self.assertTrue({"opportunity.created", "approval.requested", "approval.approved", "ledger.income"}.issubset(event_types))

    def test_non_finite_financial_values_are_rejected(self):
        response = client.post(
            "/ledger",
            headers={**AUTH, "Content-Type": "application/json"},
            content='{"entry_type":"income","category":"test","amount":1e999}',
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
