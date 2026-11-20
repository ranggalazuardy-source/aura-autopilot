import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "cloudflare" / "worker.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class CloudflareWorkerEntrypointTests(unittest.TestCase):
    def test_worker_uses_official_asgi_entrypoint(self):
        entrypoint = next(
            node for node in TREE.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "Default" for target in node.targets)
        )
        self.assertIsInstance(entrypoint.value, ast.Call)
        self.assertIsInstance(entrypoint.value.func, ast.Attribute)
        self.assertIsInstance(entrypoint.value.func.value, ast.Name)
        self.assertEqual(entrypoint.value.func.value.id, "asgi")
        self.assertEqual(entrypoint.value.func.attr, "entrypoint")
        self.assertIn("app", [arg.id for arg in entrypoint.value.args if isinstance(arg, ast.Name)])

    def test_production_worker_disables_public_openapi_docs(self):
        self.assertIn("openapi_url=None", SOURCE)
        self.assertIn("docs_url=None", SOURCE)
        self.assertIn("redoc_url=None", SOURCE)

    def test_worker_defines_api_key_scheme_and_safe_error_handler(self):
        self.assertIn('APIKeyHeader(name="X-AURA-API-Key"', SOURCE)
        self.assertIn("RequestValidationError", SOURCE)
        self.assertIn("sanitize_validation_data", SOURCE)
        self.assertIn("add_security_headers", SOURCE)


    def test_d1_rows_supports_native_lists_and_pyodide_proxies(self):
        helper = next(
            node for node in TREE.body
            if isinstance(node, ast.FunctionDef) and node.name == "d1_rows"
        )
        namespace = {}
        module = ast.Module(body=[helper], type_ignores=[])
        exec(compile(module, str(SOURCE_PATH), "exec"), namespace)

        class Result:
            def __init__(self, rows):
                self.results = rows

        class Proxy:
            def to_py(self):
                return [{"id": "proxy"}]

        self.assertEqual(namespace["d1_rows"](Result([{"id": "native"}])), [{"id": "native"}])
        self.assertEqual(namespace["d1_rows"](Result(Proxy())), [{"id": "proxy"}])
        self.assertEqual(namespace["d1_rows"](Result(None)), [])

    def test_worker_runtime_dependencies_are_pinned(self):
        import tomllib
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("fastapi==0.165.0", project["project"]["dependencies"])
        self.assertIn("workers-py==1.17.9", project["dependency-groups"]["dev"])
        self.assertIn("workers-runtime-sdk==1.9.6", project["dependency-groups"]["dev"])


if __name__ == "__main__":
    unittest.main()
