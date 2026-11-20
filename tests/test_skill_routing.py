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

    def test_router_does_not_claim_execution(self):
        self.assertIn('"execution": "not_started"', self.source)
        self.assertIn('"agent_execution": "not_automated"', self.source)


if __name__ == "__main__":
    unittest.main()
