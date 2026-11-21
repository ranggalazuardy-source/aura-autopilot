import unittest

from app.services.repair_execution_request_store import dispatch_next_execution_request


class Statement:
    def __init__(self, row):
        self.row = row
        self.sql = ""
        self.values = ()

    def bind(self, *values):
        self.values = values
        return self

    async def first(self):
        return self.row


class DB:
    def __init__(self, row):
        self.row = row
        self.sql = ""

    def prepare(self, sql):
        self.sql = sql
        return Statement(self.row)


class DispatchNextRequestTests(unittest.IsolatedAsyncioTestCase):
    async def test_dispatch_reserves_only_metadata_and_not_patch(self):
        db = DB({"id": "a" * 32, "base_sha": "b" * 40, "expires_at": 1200})
        result = await dispatch_next_execution_request(db, clock=lambda: 1000)
        self.assertEqual(result, {"request_id": "a" * 32, "base_sha": "b" * 40, "expires_at": 1200, "status": "dispatched"})
        self.assertIn("SET status = 'dispatched'", db.sql)
        self.assertNotIn("patch_text", db.sql)

    async def test_empty_queue_returns_none(self):
        self.assertIsNone(await dispatch_next_execution_request(DB(None), clock=lambda: 1000))


if __name__ == "__main__":
    unittest.main()
