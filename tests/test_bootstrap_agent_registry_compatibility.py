"""Ensure legacy D1 bootstrap tasks resolve to canonical agent skill packs."""
import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKER = (ROOT / "cloudflare" / "worker.py").read_text(encoding="utf-8")
SCHEMA = (ROOT / "cloudflare" / "schema.sql").read_text(encoding="utf-8")
TREE = ast.parse(WORKER)


def assignment(name):
    for node in TREE.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"Missing assignment: {name}")


class BootstrapAgentRegistryCompatibilityTests(unittest.TestCase):
    def test_all_bootstrap_task_agents_resolve_to_registered_roles(self):
        registry = assignment("AGENT_SKILLS")
        aliases = assignment("AGENT_ALIASES")
        bootstrap_agents = re.findall(
            r"VALUES \('bootstrap_agent_\d+',\s*'((?:[^']|'')*)'",
            SCHEMA,
        )
        self.assertEqual(len(bootstrap_agents), 15)
        for legacy_name in bootstrap_agents:
            canonical = aliases.get(legacy_name, legacy_name)
            with self.subTest(agent=legacy_name):
                self.assertIn(canonical, registry)
                self.assertTrue(registry[canonical])

    def test_alias_targets_are_all_canonical_registry_roles(self):
        registry = assignment("AGENT_SKILLS")
        aliases = assignment("AGENT_ALIASES")
        self.assertEqual(len(aliases), 15)
        self.assertTrue(set(aliases.values()).issubset(registry))

    def test_registry_alias_resolution_is_used_by_task_routing(self):
        function = next(
            node for node in TREE.body
            if isinstance(node, ast.FunctionDef) and node.name == "resolve_agent_skills"
        )
        source = ast.unparse(function)
        self.assertIn("AGENT_ALIASES.get(agent, agent)", source)
        self.assertIn("AGENT_SKILLS.get(canonical_agent)", source)
        context_function = next(
            node for node in TREE.body
            if isinstance(node, ast.FunctionDef) and node.name == "assemble_agent_context"
        )
        context_source = ast.unparse(context_function)
        self.assertIn("AGENT_ALIASES.get(agent, agent)", context_source)
        self.assertIn("AGENT_OFFICE_PROFILES.get(canonical_agent, {})", context_source)


if __name__ == "__main__":
    unittest.main()
