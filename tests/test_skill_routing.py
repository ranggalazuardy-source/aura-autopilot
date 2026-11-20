import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        cls.assignments = {}
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {"SKILL_PACKS", "AGENT_SKILLS"}:
                        cls.assignments[target.id] = ast.literal_eval(node.value)
        cls.source = source
        cls.schema = (ROOT / "cloudflare" / "schema.sql").read_text(encoding="utf-8")

    def test_all_agent_bindings_reference_known_skill_packs(self):
        packs = self.assignments["SKILL_PACKS"]
        bindings = self.assignments["AGENT_SKILLS"]
        self.assertEqual(len(bindings), 15)
        for agent, pack_ids in bindings.items():
            with self.subTest(agent=agent):
                self.assertTrue(pack_ids)
                self.assertTrue(set(pack_ids).issubset(packs.keys()))

    def test_veto_agents_receive_all_skill_packs(self):
        all_packs = set(self.assignments["SKILL_PACKS"])
        bindings = self.assignments["AGENT_SKILLS"]
        self.assertEqual(set(bindings["Compliance & Rights"]), all_packs)
        self.assertEqual(set(bindings["QA / Auditor"]), all_packs)

    def test_task_routing_is_persisted_and_audited(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS task_skill_routes", self.schema)
        self.assertIn("agent_task.skills_routed", self.source)
        self.assertIn("persist_task_route(db, task_id, data[\"agent\"])", self.source)

    def test_skill_endpoints_are_present_and_authenticated(self):
        self.assertRegex(self.source, r'@app\.get\("/skills".*require_api_key')
        self.assertRegex(self.source, r'@app\.get\("/agents/\{agent_name\}/skills".*require_api_key')
        self.assertRegex(self.source, r'@app\.post\("/agent-tasks/\{task_id\}/route".*require_api_key')


    def test_skill_loader_contains_all_runtime_instruction_bodies(self):
        for pack_id in self.assignments["SKILL_PACKS"]:
            with self.subTest(pack=pack_id):
                self.assertIn('"' + pack_id + '": """', self.source)
        self.assertIn("def assemble_agent_context", self.source)
        self.assertIn("untrusted_task_input", self.source)

    def test_provider_adapter_is_prepare_only_and_disabled(self):
        self.assertIn("def build_openai_compatible_payload", self.source)
        self.assertIn("def provider_adapter_status", self.source)
        self.assertIn('"transport_enabled": False', self.source)
        self.assertIn("No provider credentials or per-task owner-approved model budget", self.source)
        self.assertNotIn("httpx.post(", self.source)
        self.assertNotIn("requests.post(", self.source)

    def test_task_context_prepare_endpoint_is_guarded(self):
        self.assertIn('@app.post("/agent-tasks/{task_id}/prepare", dependencies=[Depends(require_api_key)])', self.source)
        self.assertIn("agent_task.context_prepared", self.source)
        self.assertIn('"execution": "not_started"', self.source)


    def test_execution_schema_has_leases_and_artifacts(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS task_execution_leases", self.schema)
        self.assertIn("CREATE TABLE IF NOT EXISTS task_execution_artifacts", self.schema)

    def test_executor_endpoints_and_lease_guards_exist(self):
        for route in [
            '@app.post("/agent-tasks/claim-next"',
            '@app.post("/agent-tasks/{task_id}/heartbeat"',
            '@app.post("/agent-tasks/{task_id}/tools"',
            '@app.post("/agent-tasks/{task_id}/complete"',
            '@app.post("/agent-tasks/{task_id}/release"',
            '@app.get("/tools"',
        ]:
            with self.subTest(route=route):
                self.assertIn(route, self.source)
        self.assertIn("async def get_valid_lease", self.source)
        self.assertIn("hmac.compare_digest", self.source)

    def test_only_local_pure_tools_are_registered(self):
        self.assertIn('"text_stats"', self.source)
        self.assertIn('"unit_economics"', self.source)
        self.assertIn("AGENT_TOOL_ALLOWLIST", self.source)
        self.assertNotIn("subprocess.", self.source)
        self.assertNotIn("os.system(", self.source)

    def test_manual_status_endpoint_cannot_mark_tasks_completed(self):
        self.assertIn('status: str = Field(pattern="^(queued|blocked|cancelled)$")', self.source)

    def test_task_execution_is_not_model_execution(self):
        self.assertIn('"qa_status": "pending_review"', self.source)
        self.assertIn('"permission": "local_pure"', self.source)


    def test_research_intelligence_tables_exist(self):
        for table in ["research_runs", "research_sources", "opportunity_scores", "market_comparisons", "ceo_decisions"]:
            with self.subTest(table=table):
                self.assertIn("CREATE TABLE IF NOT EXISTS " + table, self.schema)

    def test_research_endpoints_are_present(self):
        for route in [
            '@app.post("/research/runs"',
            '@app.get("/research/runs"',
            '@app.post("/research/runs/{run_id}/close"',
            '@app.post("/research/sources"',
            '@app.get("/research/sources"',
            '@app.post("/research/sources/{source_id}/verify"',
            '@app.post("/opportunities/{opportunity_id}/score"',
            '@app.get("/opportunities/scores"',
            '@app.post("/research/compare"',
            '@app.get("/research/compare/{comparison_id}"',
            '@app.get("/ceo/recommendation/{comparison_id}"',
            '@app.post("/ceo/decisions"',
        ]:
            with self.subTest(route=route):
                self.assertIn(route, self.source)

    def test_scoring_is_transparent_and_zero_capital_guarded(self):
        self.assertIn("SCORE_WEIGHTS", self.source)
        self.assertIn("def score_opportunity_dimensions", self.source)
        self.assertIn("def recommendation_for_score", self.source)
        self.assertIn('"hold_for_owner_cost_approval"', self.source)
        self.assertIn('"recommend_zero_cost_pilot"', self.source)

    def test_research_source_intake_does_not_claim_automatic_verification(self):
        self.assertIn('"verification_status": "unverified"', self.source)
        self.assertIn('"verification_method": "authenticated_manual_review"', self.source)
        self.assertIn("def validate_public_https_url", self.source)

    def test_ceo_decision_never_executes_actions(self):
        self.assertIn('"owner_approval_required": True', self.source)
        self.assertIn('"execution": "not_started"', self.source)

    def test_router_does_not_claim_execution(self):
        self.assertIn('"execution": "not_started"', self.source)
        self.assertIn('"agent_execution": "not_automated"', self.source)


if __name__ == "__main__":
    unittest.main()
