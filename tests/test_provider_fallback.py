"""Deterministic provider policy tests; never contacts live AI endpoints."""
import ast
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)

POLICY_NAMES = {
    "CLOUDFLARE_FREE_MODEL",
    "GROQ_FREE_MODEL",
    "GEMINI_FREE_MODEL",
    "MAX_MODEL_CALLS_PER_UTC_DAY",
    "MAX_MODEL_OUTPUT_TOKENS",
}
FUNCTION_NAMES = {
    "_truthy_env",
    "_is_quota_exhaustion",
    "_should_failover_provider",
    "provider_adapter_status",
}
nodes = []
for node in TREE.body:
    if isinstance(node, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id in POLICY_NAMES
        for target in node.targets
    ):
        nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in FUNCTION_NAMES:
        nodes.append(node)
namespace = {}
exec(compile(ast.Module(body=nodes, type_ignores=[]), "<provider-policy>", "exec"), namespace)


class ProviderFallbackContractTests(unittest.TestCase):
    def test_provider_order_and_daily_cap_are_fixed(self):
        status = namespace["provider_adapter_status"](SimpleNamespace())
        self.assertEqual(status["automatic_fallback"], ["cloudflare", "groq", "gemini"])
        self.assertEqual(status["daily_call_cap"], 5)
        self.assertFalse(status["model_enabled"])
        self.assertFalse(status["transport_enabled"])

    def test_all_provider_flags_and_free_confirmations_are_required(self):
        env = SimpleNamespace(
            AI=object(),
            GROQ_API_KEY="test-only",
            GEMINI_API_KEY="test-only",
            AURA_MODEL_ENABLED="true",
            AURA_CLOUDFLARE_FREE_PLAN_CONFIRMED="true",
            AURA_GROQ_ENABLED="true",
            AURA_GROQ_FREE_TIER_CONFIRMED="true",
            AURA_GEMINI_ENABLED="true",
            AURA_GEMINI_FREE_TIER_CONFIRMED="true",
        )
        status = namespace["provider_adapter_status"](env)
        self.assertTrue(status["transport_enabled"])
        self.assertTrue(status["groq_alternative"]["enabled"])
        self.assertTrue(status["gemini_alternative"]["enabled"])

    def test_missing_free_confirmation_keeps_alternative_disabled(self):
        env = SimpleNamespace(
            GROQ_API_KEY="test-only",
            AURA_MODEL_ENABLED="true",
            AURA_GROQ_ENABLED="true",
            AURA_GROQ_FREE_TIER_CONFIRMED="false",
        )
        status = namespace["provider_adapter_status"](env)
        self.assertFalse(status["groq_alternative"]["enabled"])
        self.assertFalse(status["transport_enabled"])

    def test_only_retryable_upstream_statuses_fail_over_in_auto_mode(self):
        should = namespace["_should_failover_provider"]
        for status_code in (429, 502, 503, 504):
            with self.subTest(status_code=status_code):
                error = SimpleNamespace(status_code=status_code, detail="upstream failure")
                self.assertTrue(should(error, "auto", 0, 3))
        for status_code in (400, 401, 402, 403, 422, 500):
            with self.subTest(status_code=status_code):
                error = SimpleNamespace(status_code=status_code, detail="request failed")
                self.assertFalse(should(error, "auto", 0, 3))

    def test_quota_signatures_are_detected_without_live_requests(self):
        is_quota = namespace["_is_quota_exhaustion"]
        for detail in (
            "resource_exhausted",
            "quota exceeded",
            "quota_exceeded",
            "rate limit reached",
            "neurons limit reached",
            "daily limit exceeded",
        ):
            with self.subTest(detail=detail):
                self.assertTrue(is_quota(detail))
        self.assertFalse(is_quota("invalid API key"))
        self.assertFalse(is_quota("billing required"))

    def test_explicit_provider_and_last_provider_never_fall_over(self):
        should = namespace["_should_failover_provider"]
        retryable = SimpleNamespace(status_code=503, detail="temporarily unavailable")
        self.assertFalse(should(retryable, "groq", 0, 3))
        self.assertFalse(should(retryable, "auto", 2, 3))


if __name__ == "__main__":
    unittest.main()
