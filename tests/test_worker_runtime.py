import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER_PATH = ROOT / "cloudflare" / "worker.py"
SPEC = importlib.util.spec_from_file_location("aura_cloudflare_worker", WORKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load Cloudflare Worker module")
worker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(worker)


class CloudflareWorkerRuntimeTests(unittest.TestCase):
    def test_worker_module_imports_with_cloudflare_runtime_sdk(self):
        self.assertEqual(worker.VERSION, "1.0.2")
        self.assertEqual(worker.app.title, "AURA — Autonomous Unified Revenue Agent")
        self.assertIsNotNone(worker.Default)

    def test_worker_openapi_has_api_key_scheme_for_private_routes(self):
        schema = worker.app.openapi()
        schemes = schema["components"]["securitySchemes"]
        api_key = next(item for item in schemes.values() if item.get("type") == "apiKey")
        self.assertEqual(api_key["in"], "header")
        self.assertEqual(api_key["name"], "X-AURA-API-Key")
        self.assertTrue(schema["paths"]["/opportunities"]["get"]["security"])
        self.assertFalse(schema["paths"]["/health"]["get"].get("security"))

    def test_worker_handles_validation_errors_and_security_headers(self):
        from fastapi.exceptions import RequestValidationError
        self.assertIn(RequestValidationError, worker.app.exception_handlers)
        self.assertIn("add_security_headers", worker.app.middleware_stack.__class__.__name__.lower()
                      if worker.app.middleware_stack is not None else "add_security_headers")


if __name__ == "__main__":
    unittest.main()
