import hashlib
import unittest

from app.services.repair_execution_request_store import (
    claim_execution_patch, create_execution_request,
)


class FakeStatement:
    def __init__(self, db, sql):
        self.db, self.sql, self.values = db, sql, ()

    def bind(self, *values):
        self.values = values
        return self

    async def run(self):
        self.db.inserted = self.values
        self.db.last_sql = self.sql
        return {}

    async def first(self):
        request_id = self.values[1]
        now = self.values[2]
        row = self.db.rows.get(request_id)
        if not row or row["status"] != "queued" or row["expires_at"] <= now:
            return None
        row["status"] = "claimed"
        row["claimed_at"] = now
        return {k: row[k] for k in (
            "id", "incident_id", "base_sha", "patch_sha256", "patch_text",
            "approved_paths_json", "approval_receipt_id", "expires_at"
        )}


class FakeD1:
    def __init__(self):
        self.rows = {}
        self.inserted = None
        self.last_sql = ""

    def prepare(self, sql):
        return FakeStatement(self, sql)


class ExecutionRequestStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_create_persists_hash_bound_patch_and_short_expiry(self):
        db = FakeD1()
        result = await create_execution_request(
            db, incident_id="incident_123", base_sha="a" * 40,
            patch_text="diff --git a/app/services/a.py b/app/services/a.py\n",
            approved_paths=["app/services/a.py"], receipt_id="r" * 40,
            ttl_seconds=120, clock=lambda: 1000,
        )
        self.assertEqual(result["expires_at"], 1120)
        self.assertEqual(result["status"], "queued")
        self.assertEqual(len(result["request_id"]), 32)
        self.assertEqual(result["patch_sha256"], hashlib.sha256(
            b"diff --git a/app/services/a.py b/app/services/a.py\n"
        ).hexdigest())
        self.assertIn("INSERT INTO repair_execution_requests", db.last_sql)

    async def test_claim_is_single_use_and_returns_verified_patch(self):
        db = FakeD1()
        created = await create_execution_request(
            db, incident_id="incident_123", base_sha="b" * 40,
            patch_text="patch", approved_paths=["tests/test_x.py"],
            receipt_id="z" * 40, clock=lambda: 100,
        )
        vals = db.inserted
        db.rows[created["request_id"]] = {
            "id": vals[0], "incident_id": vals[1], "base_sha": vals[2],
            "patch_sha256": vals[3], "patch_text": vals[4],
            "approved_paths_json": vals[5], "approval_receipt_id": vals[6],
            "status": "queued", "expires_at": vals[7], "claimed_at": None,
        }
        first = await claim_execution_patch(db, request_id=created["request_id"], clock=lambda: 101)
        second = await claim_execution_patch(db, request_id=created["request_id"], clock=lambda: 101)
        self.assertEqual(first["patch_text"], "patch")
        self.assertIsNone(second)

    async def test_expired_request_is_not_claimed(self):
        db = FakeD1()
        created = await create_execution_request(
            db, incident_id="incident_123", base_sha="c" * 40,
            patch_text="patch", approved_paths=["docs/readme.md"],
            receipt_id="q" * 40, clock=lambda: 100,
        )
        vals = db.inserted
        db.rows[created["request_id"]] = {
            "id": vals[0], "incident_id": vals[1], "base_sha": vals[2],
            "patch_sha256": vals[3], "patch_text": vals[4],
            "approved_paths_json": vals[5], "approval_receipt_id": vals[6],
            "status": "queued", "expires_at": vals[7], "claimed_at": None,
        }
        self.assertIsNone(await claim_execution_patch(db, request_id=created["request_id"], clock=lambda: 1000))

    async def test_rejects_invalid_path_and_patch_too_large(self):
        db = FakeD1()
        with self.assertRaises(ValueError):
            await create_execution_request(
                db, incident_id="incident_123", base_sha="d" * 40,
                patch_text="x", approved_paths=["cloudflare/worker.py"],
                receipt_id="r" * 40, clock=lambda: 100,
            )
        with self.assertRaises(ValueError):
            await create_execution_request(
                db, incident_id="incident_123", base_sha="d" * 40,
                patch_text="x" * 256001, approved_paths=["tests/test_x.py"],
                receipt_id="r" * 40, clock=lambda: 100,
            )


if __name__ == "__main__":
    unittest.main()
