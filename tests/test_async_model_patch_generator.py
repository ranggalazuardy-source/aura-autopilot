import json
import unittest

from app.services.async_model_patch_generator import AsyncBoundedModelPatchGenerator

BASE = "f" * 40
PATCH = (
    "diff --git a/app/agents/example.py b/app/agents/example.py\n"
    "index 1111111..2222222 100644\n"
    "--- a/app/agents/example.py\n"
    "+++ b/app/agents/example.py\n"
    "@@ -1 +1,2 @@\n"
    " old_value\n"
    "+new_value\n"
)


class Reader:
    def __init__(self, files):
        self.files = files
        self.calls = []

    async def read_file(self, path, *, ref):
        self.calls.append((path, ref))
        return self.files[path]


class Model:
    def __init__(self):
        self.prompt = None

    async def __call__(self, prompt):
        self.prompt = prompt
        return json.dumps({
            "unified_diff": PATCH,
            "files": [{"filename": "app/agents/example.py", "additions": 1, "deletions": 0}],
        })


class AsyncBoundedModelPatchGeneratorTests(unittest.IsolatedAsyncioTestCase):
    async def test_reads_only_persisted_paths_at_exact_sha(self):
        reader, model = Reader({"app/agents/example.py": "def x(): return 1"}), Model()
        generator = AsyncBoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        patch, files = await generator.generate(
            {"incident_id": "a" * 24, "category": "automated_test_regression", "base_sha": BASE},
            {"candidate_paths": ["app/agents/example.py"]},
        )
        self.assertEqual(patch, PATCH)
        self.assertEqual(reader.calls, [("app/agents/example.py", BASE)])
        self.assertEqual(files[0].filename, "app/agents/example.py")
        self.assertIn(BASE, model.prompt)

    async def test_rejects_unsafe_path_before_source_or_model(self):
        reader, model = Reader({}), Model()
        generator = AsyncBoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        with self.assertRaisesRegex(ValueError, "candidate_paths_blocked"):
            await generator.generate(
                {"incident_id": "a" * 24, "category": "automated_test_regression", "base_sha": BASE},
                {"candidate_paths": ["cloudflare/worker.py"]},
            )
        self.assertEqual(reader.calls, [])
        self.assertIsNone(model.prompt)

    async def test_rejects_invalid_sha_before_source_or_model(self):
        reader, model = Reader({}), Model()
        generator = AsyncBoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        with self.assertRaisesRegex(ValueError, "immutable_base_sha_required"):
            await generator.generate(
                {"incident_id": "a" * 24, "category": "automated_test_regression", "base_sha": "bad"},
                {"candidate_paths": ["app/agents/example.py"]},
            )
        self.assertEqual(reader.calls, [])
        self.assertIsNone(model.prompt)


if __name__ == "__main__":
    unittest.main()
