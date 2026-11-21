import json
import unittest

from app.services.patch_approval_issuer import issue_patch_approval_receipt


class FakeStatement:
    def __init__(self):
        self.values = None
        self.runs = 0

    def bind(self, *values):
        self.values = values
        return self

    async def run(self):
        self.runs += 1
        return {"success": True}


class FakeD1:
    def __init__(self):
        self.sql = None
        self.statement = FakeStatement()

    def prepare(self, sql):
        self.sql = sql
        return self.statement


class PatchApprovalIssuerTests(unittest.IsolatedAsyncioTestCase):
    async def test_issues_short_lived_owner_bound_receipt(self):
        db = FakeD1()
        receipt_id = await issue_patch_approval_receipt(
            db,
            authenticated_owner_id="verified-owner-42",
            incident_id="incident-42",
            base_sha="a" * 40,
            patch_sha256="b" * 64,
            approved_paths=("app/agents/fix.py", "tests/test_fix.py"),
            ttl_seconds=300,
            clock=lambda: 1_800_000_000,
        )

        self.assertTrue(receipt_id)
        self.assertIn("INSERT INTO patch_approval_receipts", db.sql)
        self.assertEqual(db.statement.runs, 1)
        self.assertEqual(db.statement.values[1], "verified-owner-42")
        self.assertEqual(db.statement.values[2], "incident-42")
        self.assertEqual(db.statement.values[6], 1_800_000_300)
        self.assertEqual(db.statement.values[7], 1_800_000_000)
        self.assertEqual(
            json.loads(db.statement.values[5]),
            ["app/agents/fix.py", "tests/test_fix.py"],
        )

    async def test_rejects_missing_authenticated_owner(self):
        db = FakeD1()
        with self.assertRaises(ValueError):
            await issue_patch_approval_receipt(
                db, authenticated_owner_id=" ", incident_id="incident-1",
                base_sha="a" * 40, patch_sha256="b" * 64,
                approved_paths=("app/agents/fix.py",),
            )
        self.assertIsNone(db.sql)

    async def test_rejects_ttl_over_ten_minutes(self):
        db = FakeD1()
        with self.assertRaises(ValueError):
            await issue_patch_approval_receipt(
                db, authenticated_owner_id="owner", incident_id="incident-1",
                base_sha="a" * 40, patch_sha256="b" * 64,
                approved_paths=("app/agents/fix.py",), ttl_seconds=601,
            )
        self.assertIsNone(db.sql)

    async def test_rejects_paths_outside_allowlist(self):
        db = FakeD1()
        with self.assertRaises(ValueError):
            await issue_patch_approval_receipt(
                db, authenticated_owner_id="owner", incident_id="incident-1",
                base_sha="a" * 40, patch_sha256="b" * 64,
                approved_paths=("cloudflare/worker.py",),
            )
        self.assertIsNone(db.sql)

    async def test_rejects_duplicate_paths(self):
        db = FakeD1()
        with self.assertRaises(ValueError):
            await issue_patch_approval_receipt(
                db, authenticated_owner_id="owner", incident_id="incident-1",
                base_sha="a" * 40, patch_sha256="b" * 64,
                approved_paths=("app/agents/fix.py", "app/agents/fix.py"),
            )
        self.assertIsNone(db.sql)

    async def test_rejects_malformed_hashes(self):
        db = FakeD1()
        with self.assertRaises(ValueError):
            await issue_patch_approval_receipt(
                db, authenticated_owner_id="owner", incident_id="incident-1",
                base_sha="bad", patch_sha256="b" * 64,
                approved_paths=("app/agents/fix.py",),
            )
        self.assertIsNone(db.sql)


if __name__ == "__main__":
    unittest.main()
