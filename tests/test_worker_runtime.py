import unittest

from cloudflare import worker


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

    def test_worker_validation_and_security_middleware_are_registered(self):
        from fastapi.exceptions import RequestValidationError

        self.assertIn(RequestValidationError, worker.app.exception_handlers)
        self.assertTrue(callable(worker.add_security_headers))
        self.assertTrue(worker.app.user_middleware)


if __name__ == "__main__":
    unittest.main()
