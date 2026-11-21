import ast
import json
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
        self.assertEqual(len(bindings), 24)
        for agent, pack_ids in bindings.items():
            with self.subTest(agent=agent):
                self.assertTrue(pack_ids)
                self.assertTrue(set(pack_ids).issubset(packs.keys()))

    def test_veto_agents_receive_all_skill_packs(self):
        all_packs = set(self.assignments["SKILL_PACKS"])
        bindings = self.assignments["AGENT_SKILLS"]
        self.assertEqual(set(bindings["Legal Compliance Checker"]), all_packs)
        self.assertEqual(set(bindings["Model QA Specialist"]), all_packs)

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

    def test_provider_adapter_is_integrated_but_fail_closed_by_default(self):
        self.assertIn("def build_openai_compatible_payload", self.source)
        self.assertIn("def provider_adapter_status", self.source)
        self.assertIn("async def invoke_cloudflare_model", self.source)
        self.assertIn("async def invoke_groq_model", self.source)
        self.assertIn("AURA_MODEL_ENABLED", self.source)
        self.assertIn("AURA_CLOUDFLARE_FREE_PLAN_CONFIRMED", self.source)
        self.assertIn("AURA_GROQ_FREE_TIER_CONFIRMED", self.source)
        self.assertIn('"automatic_fallback": ["cloudflare", "groq", "gemini"]', self.source)
        self.assertIn('("cloudflare", "groq", "gemini")', self.source)
        self.assertIn("exc.status_code in (429, 502, 503, 504)", self.source)
        self.assertIn("billing, authentication, configuration and invalid-request errors stop execution", self.source)
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



    def test_public_search_adapter_is_fixed_host_and_rate_limited(self):
        self.assertIn('https://html.duckduckgo.com/html/?', self.source)
        self.assertIn("10 queries per 10 minutes", self.source)
        self.assertIn("async def search_research_web", self.source)
        self.assertIn("class DuckDuckGoHTMLParser", self.source)
        self.assertIn("async function loadResearchSources", self.source)
        self.assertIn("async function linkResearchSource", self.source)
        self.assertIn('"verification_status": "unverified"', self.source)

    def test_research_search_logs_schema_exists(self):
        self.assertIn("CREATE TABLE IF NOT EXISTS research_search_logs", self.schema)

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
            '@app.post("/research/sources/{source_id}/link"',
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


    def test_office_profiles_cover_all_registered_agents(self):
        profiles = {}
        tree = ast.parse(self.source)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "AGENT_OFFICE_PROFILES":
                        profiles = ast.literal_eval(node.value)
        self.assertEqual(set(profiles), set(self.assignments["AGENT_SKILLS"]))
        self.assertEqual(len(profiles), 24)
        self.assertEqual({item["zone"] for item in profiles.values()}, {"command", "research", "marketing", "sales", "operations", "engineering"})

    def test_virtual_office_state_uses_live_tasks_leases_and_audit_logs(self):
        self.assertIn('@app.get("/office/state", dependencies=[Depends(require_api_key)])', self.source)
        self.assertIn("LEFT JOIN task_execution_leases l ON l.task_id = t.id", self.source)
        self.assertIn("l.expires_at AS lease_expires_at", self.source)
        self.assertIn('state = "waiting_input"', self.source)
        self.assertIn('state = "working"', self.source)
        self.assertIn('FROM audit_log ORDER BY created_at DESC LIMIT 60', self.source)
        self.assertIn('"background_scheduler_enabled": _truthy_env(get_env(request), "AURA_SCHEDULER_ENABLED")', self.source)
        self.assertIn('"model_provider_enabled": _truthy_env(get_env(request), "AURA_MODEL_ENABLED")', self.source)
        config = json.loads((ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertEqual(config["vars"]["AURA_SCHEDULER_ENABLED"], "false")
        self.assertEqual(config["vars"]["AURA_MODEL_ENABLED"], "false")

    def test_virtual_office_frontend_uses_react_three_fiber_and_live_api(self):
        frontend = (ROOT / "virtual-office" / "src" / "App.jsx").read_text(encoding="utf-8")
        scene = (ROOT / "virtual-office" / "src" / "OfficeScene.jsx").read_text(encoding="utf-8")
        package = (ROOT / "virtual-office" / "package.json").read_text(encoding="utf-8")
        self.assertIn("@react-three/fiber", package)
        self.assertIn("useFrame", scene)
        self.assertIn("Canvas", scene)
        self.assertIn("/office/state", frontend)
        self.assertIn("X-AURA-API-Key", frontend)
        self.assertIn("setInterval", frontend)
        self.assertIn("active_tasks", frontend)
        self.assertIn("logs", frontend)


    def test_root_landing_links_both_apps_on_one_origin(self):
        self.assertIn('@app.get("/", response_class=HTMLResponse, include_in_schema=False)', self.source)
        self.assertIn('href="/dashboard"', self.source)
        self.assertIn('href="/office/"', self.source)

    def test_office_api_path_is_routed_to_worker_before_static_assets(self):
        import json
        config = json.loads((ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        self.assertIn("/office/state*", config["assets"]["run_worker_first"])
        self.assertTrue(config["workers_dev"])


    def test_cloudflare_deploy_workflow_is_secret_gated_and_manual(self):
        workflow = (ROOT / ".github" / "workflows" / "deploy-cloudflare.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("secrets.CLOUDFLARE_API_TOKEN", workflow)
        self.assertIn("secrets.CLOUDFLARE_ACCOUNT_ID", workflow)
        self.assertIn("secrets.AURA_API_KEY", workflow)
        self.assertIn("wrangler d1 create aura-autopilot-db --location apac", workflow)
        self.assertIn("wrangler d1 execute aura-autopilot-db --remote --file=cloudflare/schema.sql", workflow)
        self.assertIn("pywrangler secret put AURA_API_KEY", workflow)
        self.assertIn("pywrangler deploy", workflow)
        self.assertIn("/office/state", workflow)

    def test_task_claim_recovers_orphaned_and_expired_leases(self):
        self.assertIn("NOT EXISTS", self.source)
        self.assertIn("orphan_cutoff", self.source)
        self.assertIn("updated_at <= ?", self.source)
        self.assertIn("expired.expires_at <= ?", self.source)

    def test_worker_mutations_are_lease_bound_and_terminal_states_guarded(self):
        self.assertIn("AND worker_id = ? AND lease_token = ? AND expires_at > ?", self.source)
        self.assertIn("completed or cancelled tasks are terminal", self.source)
        self.assertIn("task state changed; refresh before retrying", self.source)

    def test_agent_and_related_opportunity_are_validated_before_queue_insert(self):
        self.assertIn("pack_ids = resolve_agent_skills(payload.agent)", self.source)
        self.assertIn("related opportunity not found", self.source)
        self.assertIn("resolve_agent_skills(payload.agent)", self.source)

    def test_financial_and_tool_inputs_reject_non_finite_values(self):
        self.assertIn("allow_inf_nan=False", self.source)
        self.assertIn("math.isfinite(float(value))", self.source)

    def test_office_completion_metric_uses_jakarta_calendar_day(self):
        self.assertIn('timezone(timedelta(hours=7))', self.source)
        self.assertIn("updated.astimezone(jakarta_tz).date()", self.source)

    def test_research_source_url_rejects_malformed_ports(self):
        self.assertIn("parsed.port", self.source)
        self.assertIn('raise HTTPException(422, "source URL is malformed")', self.source)

    def test_content_cannot_self_clear_rights_on_creation(self):
        content_model = self.source.split("class ContentItemIn", 1)[1].split("class ContentStatusIn", 1)[0]
        self.assertNotIn("rights_status:", content_model)
        self.assertIn("'needs_review', 'idea'", self.source)
        self.assertIn('@app.post("/content/{content_id}/rights"', self.source)
        self.assertIn("content.rights_", self.source)

    def test_invalid_request_errors_are_sanitized_to_json_422(self):
        self.assertIn("sanitize_validation_data", self.source)
        self.assertIn("RequestValidationError", self.source)
        self.assertIn("status_code=422", self.source)

    def test_approval_decision_is_single_winner_atomic_update(self):
        self.assertIn("UPDATE approvals SET status = ? WHERE id = ? AND status = 'pending' RETURNING id", self.source)

    def test_content_approval_requires_reviewed_rights_and_valid_transition(self):
        self.assertIn("allowed_transitions", self.source)
        self.assertIn("(? != 'approved' OR rights_status = 'cleared')", self.source)
        self.assertIn("WHERE id = ? AND rights_status = ? RETURNING id", self.source)

    def test_research_source_verification_is_one_time_atomic_update(self):
        self.assertIn("WHERE id = ? AND verification_status = 'unverified' RETURNING id", self.source)

    def test_research_run_close_is_atomic_single_winner(self):
        handler = self.source.split("async def close_research_run", 1)[1].split(
            '@app.get("/research/runs"', 1
        )[0]
        self.assertIn("AND status = 'collecting' RETURNING id", handler)
        self.assertIn("research run was already closed", handler)

    def test_closed_research_runs_reject_manual_source_ingestion(self):
        handler = self.source.split("async def add_research_source", 1)[1].split(
            '@app.get("/research/sources"', 1
        )[0]
        self.assertIn("SELECT id, status FROM research_runs", handler)
        self.assertIn('run.status != "collecting"', handler)
        self.assertIn("research run is not accepting new sources", handler)

    def test_upstream_search_http_failures_are_logged(self):
        handler = self.source.split("async def search_research_web", 1)[1].split(
            '@app.post("/research/runs"', 1
        )[0]
        self.assertIn("except HTTPException as exc", handler)
        self.assertIn('"failed"', handler)
        self.assertIn("research.web_search_failed", handler)

    def test_worker_auth_failures_use_cloudflare_rate_limit_binding(self):
        self.assertIn('getattr(env, "AURA_AUTH_RATE_LIMITER", None)', self.source)
        self.assertIn('await limiter.limit({"key": str(client_ip)})', self.source)
        self.assertIn("Too many invalid API-key attempts", self.source)
        self.assertIn("Authentication rate limiter is not configured", self.source)

    def test_cloudflare_rate_limiter_and_free_plan_observability_are_configured(self):
        import json
        config = json.loads((ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))
        rate = next(item for item in config["ratelimits"] if item["name"] == "AURA_AUTH_RATE_LIMITER")
        self.assertEqual(rate["simple"], {"limit": 10, "period": 60})
        self.assertTrue(config["observability"]["enabled"])
        self.assertTrue(config["observability"]["logs"]["enabled"])


if __name__ == "__main__":
    unittest.main()
