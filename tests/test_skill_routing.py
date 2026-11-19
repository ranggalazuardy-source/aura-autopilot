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

    def test_router_does_not_claim_execution(self):
        self.assertIn('"execution": "not_started"', self.source)
        self.assertIn('"agent_execution": "not_automated"', self.source)


if __name__ == "__main__":
    unittest.main()
