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


    def test_scheduler_is_registered_but_disabled_by_default(self):
        self.assertIn("from workers import asgi, handler", SOURCE)
        self.assertIn("@handler", SOURCE)
        self.assertIn("async def on_scheduled(event, env, ctx):", SOURCE)
        self.assertIn('"AURA_SCHEDULER_ENABLED": "false"', (ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        import json
        config = json.loads((ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertEqual(config["triggers"]["crons"], ["*/15 * * * *"])
        self.assertIn('"task_dispatch_enabled": False', SOURCE)
        self.assertIn('"model_provider_enabled": False', SOURCE)


    def test_model_provider_integration_is_disabled_and_fail_closed(self):
        self.assertIn('"AURA_MODEL_ENABLED": "false"', (ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertIn('"AURA_CLOUDFLARE_FREE_PLAN_CONFIRMED": "false"', (ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertIn('"binding": "AI"', (ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertIn('CLOUDFLARE_FREE_MODEL = "@cf/zai-org/glm-4.7-flash"', SOURCE)
        self.assertIn('GROQ_FREE_MODEL = "openai/gpt-oss-120b"', SOURCE)
        self.assertIn('GEMINI_FREE_MODEL = "gemini-2.5-flash-lite"', SOURCE)
        self.assertIn('"automatic_fallback": ["cloudflare", "groq", "gemini"]', SOURCE)
        self.assertIn("AURA_GEMINI_FREE_TIER_CONFIRMED", SOURCE)
        self.assertIn("quota exhaustion and transient upstream failures", SOURCE)
        self.assertIn("MAX_MODEL_CALLS_PER_UTC_DAY = 5", SOURCE)
        self.assertIn("Owner must confirm the Cloudflare Workers Free plan", SOURCE)
        self.assertIn("no fallback was attempted", SOURCE)
        self.assertIn('async def execute_agent_task(', SOURCE)

    def test_model_execution_requires_task_lease_and_owner_flags(self):
        self.assertIn('await get_valid_lease(db, task_id, payload.worker_id, payload.lease_token)', SOURCE)
        self.assertIn('if not _truthy_env(env, "AURA_MODEL_ENABLED"):', SOURCE)
        self.assertIn('if not _truthy_env(env, "AURA_CLOUDFLARE_FREE_PLAN_CONFIRMED"):', SOURCE)
        self.assertIn('if not _truthy_env(env, "AURA_GROQ_ENABLED"):', SOURCE)
        self.assertIn('AURA_GROQ_FREE_TIER_CONFIRMED', SOURCE)
        self.assertIn('Owner must confirm Groq Free tier and no billing method before use', SOURCE)
        self.assertIn("CREATE TABLE IF NOT EXISTS model_usage_daily", (ROOT / "cloudflare" / "schema.sql").read_text(encoding="utf-8"))

    def test_guarded_agent_console_is_registered_and_linked_from_dashboard(self):
        self.assertIn('AGENT_CONSOLE =', SOURCE)
        self.assertIn('@app.get("/agents", response_class=HTMLResponse', SOURCE)
        self.assertIn('async def agent_console():', SOURCE)
        self.assertIn('href="/agents"', SOURCE)
        self.assertIn('"/agent-tasks/"+id+"/prepare"', SOURCE)
        self.assertIn('sessionStorage.setItem("aura_agent_key"', SOURCE)


    def test_virtual_office_exposes_provider_configuration_without_live_probe(self):
        self.assertIn('"provider": provider_adapter_status(get_env(request))', SOURCE)
        self.assertIn('async def virtual_office_state(request: Request, db=Depends(get_db)):', SOURCE)
        self.assertIn('ProviderStatus provider={data?.runtime?.provider}', (ROOT / "virtual-office" / "src" / "App.jsx").read_text(encoding="utf-8"))
        self.assertIn("configuration-only", SOURCE)
        self.assertIn("does not send test requests", (ROOT / "virtual-office" / "src" / "App.jsx").read_text(encoding="utf-8"))

    def test_worker_runtime_dependencies_are_pinned(self):
        import tomllib
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("fastapi==0.165.0", project["project"]["dependencies"])
        self.assertIn("workers-py==1.17.9", project["dependency-groups"]["dev"])
        self.assertIn("workers-runtime-sdk==1.9.6", project["dependency-groups"]["dev"])


if __name__ == "__main__":
    unittest.main()
