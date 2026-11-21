import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


class RepairProposalRouteTests(unittest.TestCase):
    def function(self, name):
        return next(node for node in TREE.body
                    if isinstance(node, ast.AsyncFunctionDef) and node.name == name)

    def test_generation_route_is_owner_authenticated_and_requires_both_confirmations(self):
        route = self.function("generate_ci_repair_proposal")
        decorator = ast.unparse(route.decorator_list[0])
        source = ast.unparse(route)
        self.assertIn("Depends(require_api_key)", decorator)
        self.assertIn("confirm_owner_generation", source)
        self.assertIn("confirm_provider_inference", source)
        self.assertIn("AURA_MODEL_ENABLED", source)
        self.assertIn("provider_adapter_status", source)

    def test_generation_reads_persisted_d1_triage_and_never_accepts_paths(self):
        source = ast.unparse(self.function("generate_ci_repair_proposal"))
        self.assertIn("prepare_triaged_ci_repair_from_d1_async", source)
        self.assertIn("GitHubRawCommitSourceReader", source)
        self.assertNotIn("candidate_paths", source)
        self.assertNotIn("run_url", source)
        self.assertNotIn("failed_jobs", source)

    def test_generation_returns_proposal_but_does_not_execute_or_write(self):
        source = ast.unparse(self.function("generate_ci_repair_proposal")).lower()
        self.assertIn("requires_owner_approval", source)
        self.assertIn("files_written", source)
        self.assertIn("github_written", source)
        self.assertIn("merged", source)
        self.assertIn("deployed", source)
        self.assertNotIn("execute_repair_proposal", source)
        self.assertNotIn("create_execution_request", source)
        self.assertNotIn("issue_patch_approval_receipt", source)

    def test_provider_invoker_enforces_model_switch_quota_and_retry_policy(self):
        source = ast.unparse(self.function("invoke_repair_patch_model"))
        self.assertIn("AURA_MODEL_ENABLED", source)
        self.assertIn("reserve_model_call", source)
        self.assertIn("invoke_cloudflare_model", source)
        self.assertIn("invoke_groq_model", source)
        self.assertIn("invoke_gemini_model", source)
        self.assertIn("_should_failover_provider", source)

    def test_source_reader_requires_immutable_sha_and_safe_prefix(self):
        source = ast.unparse(next(node for node in TREE.body
                                  if isinstance(node, ast.ClassDef)
                                  and node.name == "GitHubRawCommitSourceReader"))
        self.assertIn("raw.githubusercontent.com", source)
        self.assertIn("re.fullmatch", source)
        self.assertIn("source_path_not_allowlisted", source)


if __name__ == "__main__":
    unittest.main()
