import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "cloudflare" / "worker.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class CloudflareWorkerEntrypointTests(unittest.TestCase):
    def test_worker_entrypoint_delegates_to_asgi_with_runtime_environment(self):
        entrypoint = next(
            node for node in TREE.body
            if isinstance(node, ast.ClassDef) and node.name == "Default"
        )
        self.assertTrue(any(
            isinstance(base, ast.Name) and base.id == "WorkerEntrypoint"
            for base in entrypoint.bases
        ))
        fetch = next(
            node for node in entrypoint.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "fetch"
        )
        self.assertTrue(any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "asgi"
            and node.func.attr == "fetch"
            for node in ast.walk(fetch)
        ))
        self.assertIn("self.env", ast.unparse(fetch))

    def test_worker_defines_api_key_scheme_and_safe_error_handler(self):
        self.assertIn('APIKeyHeader(name="X-AURA-API-Key"', SOURCE)
        self.assertIn("RequestValidationError", SOURCE)
        self.assertIn("sanitize_validation_data", SOURCE)
        self.assertIn("add_security_headers", SOURCE)

    def test_worker_runtime_dependencies_are_pinned(self):
        import tomllib
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("fastapi==0.165.0", project["project"]["dependencies"])
        self.assertIn("workers-py==1.17.9", project["dependency-groups"]["dev"])
        self.assertIn("workers-runtime-sdk==1.9.6", project["dependency-groups"]["dev"])


if __name__ == "__main__":
    unittest.main()
