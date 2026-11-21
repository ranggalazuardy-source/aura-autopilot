import unittest
from dataclasses import dataclass

from app.services.patch_approval_store import D1PatchApprovalStore


@dataclass(frozen=True)
class Approval:
    approval_id: str = "receipt-1"
    approved_by: str = "owner-123"
    incident_id: str = "incident-123"
    base_sha: str = "a" * 40
    patch_sha256: str = "b" * 64
    approved_paths: tuple[str, ...] = ("app/agents/demo.py", "tests/test_demo.py")


class FakeStatement:
    def __init__(self, row):
        self.row = row
        self.sql = ""
        self.values = ()
        self.first_calls = 0

    def bind(self, *values):
        self.values = values
        return self

    async def first(self):
        self.first_calls += 1
        return self.row


class FakeD1:
    def __init__(self, row={"id": "receipt-1"}):
        self.statement = FakeStatement(row)
        self.sql = None

    def prepare(self, sql):
        self.sql = sql
        self.statement.sql = sql
        return self.statement


class PatchApprovalStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_receipt_is_consumed_by_one_conditional_update(self):
        db = FakeD1()
        store = D1PatchApprovalStore(db, clock=lambda: 1_800_000_000)

        result = await store.verify_and_consume(Approval())

        self.assertTrue(result)
        self.assertEqual(db.statement.first_calls, 1)
        self.assertIn("UPDATE patch_approval_receipts", db.sql)
        self.assertIn("consumed_at IS NULL", db.sql)
        self.assertIn("revoked_at IS NULL", db.sql)
        self.assertIn("expires_at > ?", db.sql)
        self.assertIn("RETURNING id", db.sql)
        self.assertEqual(db.statement.values[0], 1_800_000_000)
        self.assertEqual(db.statement.values[1], "receipt-1")

    async def test_missing_returned_row_means_expired_revoked_or_replayed(self):
        db = FakeD1(row=None)
        store = D1PatchApprovalStore(db, clock=lambda: 1_800_000_000)

        self.assertFalse(await store.verify_and_consume(Approval()))

    async def test_receipt_fields_are_bound_to_exact_approval(self):
        db = FakeD1()
        store = D1PatchApprovalStore(db, clock=lambda: 1_800_000_000)
        approval = Approval(approved_by="different-owner")

        self.assertTrue(await store.verify_and_consume(approval))
        self.assertEqual(db.statement.values[2], "different-owner")

    async def test_malformed_receipt_does_not_touch_database(self):
        db = FakeD1()
        store = D1PatchApprovalStore(db, clock=lambda: 1_800_000_000)
        approval = Approval(approved_paths=())

        self.assertFalse(await store.verify_and_consume(approval))
        self.assertIsNone(db.sql)

    async def test_duplicate_paths_are_rejected(self):
        db = FakeD1()
        store = D1PatchApprovalStore(db, clock=lambda: 1_800_000_000)
        approval = Approval(approved_paths=("app/agents/demo.py",) * 2)

        self.assertFalse(await store.verify_and_consume(approval))
        self.assertIsNone(db.sql)

    async def test_invalid_clock_fails_closed(self):
        db = FakeD1()
        store = D1PatchApprovalStore(db, clock=lambda: 0)

        self.assertFalse(await store.verify_and_consume(Approval()))
        self.assertIsNone(db.sql)


if __name__ == "__main__":
    unittest.main()
