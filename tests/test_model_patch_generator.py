import json
import unittest

from app.services.model_patch_generator import (
    BoundedModelPatchGenerator,
    MAX_SOURCE_FILE_CHARS,
    MAX_TOTAL_SOURCE_CHARS,
)


BASE = "d" * 40
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

    def read_file(self, path, *, ref):
        self.calls.append((path, ref))
        return self.files[path]


class Model:
    def __init__(self, result):
        self.result = result
        self.prompt = None

    def __call__(self, prompt):
        self.prompt = prompt
        return self.result


class BoundedModelPatchGeneratorTests(unittest.TestCase):
    def incident(self, **updates):
        value = {
            "incident_id": "e" * 24,
            "category": "automated_test_regression",
            "base_sha": BASE,
        }
        value.update(updates)
        return value

    def plan(self, paths=None):
        return {"candidate_paths": paths or ["app/agents/example.py"]}

    def response(self, patch=PATCH, files=None):
        return json.dumps({
            "unified_diff": patch,
            "files": files or [{
                "filename": "app/agents/example.py",
                "additions": 1,
                "deletions": 0,
            }],
        })

    def test_reads_only_explicit_paths_at_exact_commit_and_returns_metadata(self):
        reader = Reader({"app/agents/example.py": "def example():\n    return 1\n"})
        model = Model(self.response())
        generator = BoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        patch, files = generator.generate(self.incident(), self.plan())
        self.assertEqual(patch, PATCH)
        self.assertEqual(reader.calls, [("app/agents/example.py", BASE)])
        self.assertEqual(files[0].filename, "app/agents/example.py")
        self.assertEqual(files[0].changes, 1)
        self.assertIn(BASE, model.prompt)
        self.assertIn("allowed_paths", model.prompt)

    def test_rejects_missing_sha_or_unapproved_paths_before_model(self):
        reader = Reader({"app/agents/example.py": "source"})
        model = Model(self.response())
        generator = BoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        cases = (
            (self.incident(base_sha="not-a-sha"), self.plan()),
            (self.incident(), self.plan(["app/agents/example.py", "../secrets"])),
            (self.incident(), self.plan([])),
        )
        for incident, plan in cases:
            with self.subTest(incident=incident, plan=plan):
                with self.assertRaises(ValueError):
                    generator.generate(incident, plan)
        self.assertEqual(model.prompt, None)

    def test_source_context_limits_are_enforced(self):
        reader = Reader({"app/agents/example.py": "x" * (MAX_SOURCE_FILE_CHARS + 1)})
        model = Model(self.response())
        generator = BoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        with self.assertRaisesRegex(ValueError, "source_file_context_limit_exceeded"):
            generator.generate(self.incident(), self.plan())
        self.assertIsNone(model.prompt)

    def test_rejects_unsafe_paths_before_source_reader_access(self):
        reader = Reader({"app/agents/example.py": "source"})
        model = Model(self.response())
        generator = BoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        with self.assertRaisesRegex(ValueError, "candidate_paths_blocked"):
            generator.generate(
                self.incident(),
                self.plan(["app/agents/example.py", "../secrets"]),
            )
        self.assertEqual(reader.calls, [])
        self.assertIsNone(model.prompt)

    def test_total_source_context_limit_is_enforced(self):
        paths = [
            "app/agents/one.py",
            "app/agents/two.py",
            "app/agents/three.py",
        ]
        reader = Reader({path: "x" * 11_000 for path in paths})
        model = Model(self.response())
        generator = BoundedModelPatchGenerator(source_reader=reader, invoke_model=model)
        with self.assertRaisesRegex(ValueError, "total_source_context_limit_exceeded"):
            generator.generate(self.incident(), self.plan(paths))
        self.assertIsNone(model.prompt)

    def test_rejects_invalid_model_json_and_unknown_keys(self):
        for raw in ("not-json", json.dumps({"unified_diff": PATCH, "files": [], "extra": True})):
            with self.subTest(raw=raw):
                generator = BoundedModelPatchGenerator(
                    source_reader=Reader({"app/agents/example.py": "source"}),
                    invoke_model=Model(raw),
                )
                with self.assertRaises(ValueError):
                    generator.generate(self.incident(), self.plan())

    def test_rejects_invalid_metadata_types_and_bool_counts(self):
        for item in (
            {"filename": "app/agents/example.py", "additions": True, "deletions": 0},
            {"filename": "app/agents/example.py", "additions": "1", "deletions": 0},
            {"filename": "app/agents/example.py", "additions": 1, "deletions": 0, "extra": 0},
        ):
            raw = json.dumps({"unified_diff": PATCH, "files": [item]})
            generator = BoundedModelPatchGenerator(
                source_reader=Reader({"app/agents/example.py": "source"}),
                invoke_model=Model(raw),
            )
            with self.subTest(item=item), self.assertRaises(ValueError):
                generator.generate(self.incident(), self.plan())

    def test_generator_is_not_marked_as_mock(self):
        generator = BoundedModelPatchGenerator(
            source_reader=Reader({"app/agents/example.py": "source"}),
            invoke_model=Model(self.response()),
        )
        self.assertIs(generator.is_mock, False)


if __name__ == "__main__":
    unittest.main()
