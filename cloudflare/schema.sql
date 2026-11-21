CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    channel TEXT NOT NULL,
    rationale TEXT NOT NULL,
    estimated_cost REAL NOT NULL DEFAULT 0 CHECK(estimated_cost >= 0),
    estimated_revenue REAL NOT NULL DEFAULT 0 CHECK(estimated_revenue >= 0),
    risk_level TEXT NOT NULL DEFAULT 'medium' CHECK(risk_level IN ('low','medium','high')),
    status TEXT NOT NULL DEFAULT 'proposed',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_opportunities_created_at ON opportunities(created_at);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0 CHECK(amount >= 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_approvals_created_at ON approvals(created_at);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);

CREATE TABLE IF NOT EXISTS ledger (
    id TEXT PRIMARY KEY,
    entry_type TEXT NOT NULL CHECK(entry_type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ledger_created_at ON ledger(created_at);

CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_log(created_at);

CREATE TABLE IF NOT EXISTS content_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    platform TEXT NOT NULL CHECK(platform IN ('YouTube','TikTok','Instagram','Website')),
    format TEXT NOT NULL CHECK(format IN ('Shorts','Long-form','Carousel','Article')),
    pillar TEXT NOT NULL,
    hook TEXT NOT NULL,
    script TEXT NOT NULL DEFAULT '',
    rights_status TEXT NOT NULL DEFAULT 'needs_review' CHECK(rights_status IN ('needs_review','cleared','not_cleared')),
    status TEXT NOT NULL DEFAULT 'idea' CHECK(status IN ('idea','draft','in_review','approved','published','paused')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_content_items_status ON content_items(status);
CREATE INDEX IF NOT EXISTS idx_content_items_updated_at ON content_items(updated_at);

-- Initial Mas Mas Wibu content backlog; all items require owner review and rights clearance.
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_01','3 hal sebelum mulai baca manhua','YouTube','Shorts','Manhua discovery','Jangan mulai manhua sebelum cek tiga hal ini.','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_02','Rekomendasi manhua dengan MC strategis','YouTube','Shorts','Recommendation','Suka MC yang menang pakai otak?','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_03','Kenapa cerita cultivation punya tingkatan kekuatan?','YouTube','Shorts','Explainer','Kenapa di banyak manhua ada tingkatan kekuatan?','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_04','Review spoiler-light: [judul manhua]','YouTube','Shorts','Manhua review','Premisnya menarik, tapi ada satu hal yang perlu lu tahu.','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_05','MC overpower: seru atau membosankan?','YouTube','Shorts','Discussion','MC terlalu kuat bikin cerita makin seru atau hambar?','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_06','Checklist memilih manhua untuk pemula','YouTube','Shorts','Recommendation','Baru mau baca manhua? Cek ini dulu.','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_07','3 temuan manhua minggu ini','YouTube','Shorts','Weekly roundup','Tiga judul yang layak masuk daftar bacaan.','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_08','Apa yang bikin protagonis manhua memorable?','YouTube','Shorts','Character analysis','MC bagus bukan cuma soal kuat.','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_09','Manhua dengan world-building menarik','YouTube','Shorts','Recommendation','Kalau lu suka dunia cerita yang detail...','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_10','Istilah manhua yang sering bikin bingung','YouTube','Shorts','Explainer','Istilah ini sering muncul, tapi artinya apa?','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_11','Review: manhua ini cocok buat siapa?','YouTube','Shorts','Manhua review','Manhua ini cocok buat siapa?','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_12','Komentar adegan: kenapa momen ini menarik?','YouTube','Shorts','Original commentary','Adegan ini menarik karena...','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_13','Dua tipe perkembangan karakter','YouTube','Shorts','Original commentary','Dua tipe perkembangan karakter ini beda jauh.','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO content_items (id,title,platform,format,pillar,hook,script,rights_status,status,created_at,updated_at) VALUES ('maswibu_seed_14','Manhua apa yang wajib direview berikutnya?','YouTube','Shorts','Community prompt','Manhua apa yang wajib gua review berikutnya?','','needs_review','idea','2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;

CREATE TABLE IF NOT EXISTS agent_tasks (
    id TEXT PRIMARY KEY,
    agent TEXT NOT NULL,
    objective TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'normal' CHECK(priority IN ('low','normal','high','urgent')),
    related_opportunity_id TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'queued' CHECK(status IN ('queued','in_progress','blocked','completed','cancelled')),
    result_summary TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent ON agent_tasks(agent);

-- Initial work queue for the multi-agent company; queued tasks are plans, not executed agent runs.
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_01','CEO Orchestrator','Coordinate agent workstreams and rank portfolio priorities','urgent','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_02','Market Intelligence','Discover and score zero-capital revenue opportunities across sectors','high','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_03','Service Sales','Identify prospective clients for authorized short-form editing services','high','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_04','Clipping Studio','Prepare integration requirements for the owner''s Google AI Studio clipper','high','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_05','Affiliate Commerce','Research affiliate programs and products with positive unit economics','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_06','Content & Media','Develop content opportunities across the owner''s approved channels','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_07','E-commerce / Dropship','Validate supplier reliability, demand, margins and returns exposure','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_08','Digital Products','Find validated demand for zero-cost digital product experiments','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_09','SEO / Website','Identify search-led website opportunities with low operating costs','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_10','Equity Research','Build an evidence-based watchlist and paper portfolio; no live orders','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_11','Crypto Research','Research digital assets and risks; no live orders or custody','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_12','Trading Risk Manager','Define moderate-risk monitoring and hard-stop requirements','high','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_13','Finance & Treasury','Prepare 50/50 monthly close and cash reconciliation design','high','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_14','Compliance & Rights','Review proposed business models for legal, platform and IP constraints','high','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;
INSERT INTO agent_tasks (id,agent,objective,priority,related_opportunity_id,status,result_summary,created_at,updated_at) VALUES ('bootstrap_agent_15','QA / Auditor','Audit assumptions, agent outputs and task completion evidence','normal','','queued','', '2026-11-20T00:00:00+00:00','2026-11-20T00:00:00+00:00') ON CONFLICT(id) DO NOTHING;

-- Deterministic agent-to-skill routing metadata. This records assignment only;
-- it does not execute an LLM, external tool, integration, or financial action.
CREATE TABLE IF NOT EXISTS task_skill_routes (
    task_id TEXT NOT NULL,
    pack_id TEXT NOT NULL,
    routing_reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (task_id, pack_id)
);
CREATE INDEX IF NOT EXISTS idx_task_skill_routes_pack ON task_skill_routes(pack_id);



-- Bounded task execution: one lease per task and append-only artifacts.
CREATE TABLE IF NOT EXISTS task_execution_leases (
    task_id TEXT PRIMARY KEY,
    worker_id TEXT NOT NULL,
    lease_token TEXT NOT NULL,
    expires_at INTEGER NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES agent_tasks(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_task_execution_leases_expiry ON task_execution_leases(expires_at);

CREATE TABLE IF NOT EXISTS task_execution_artifacts (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL CHECK(artifact_type IN ('tool_result','evidence','agent_output')),
    artifact_name TEXT NOT NULL,
    content_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES agent_tasks(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_task_execution_artifacts_task ON task_execution_artifacts(task_id, created_at);



-- Research Intelligence Engine: source provenance, transparent scoring and CEO decisions.
CREATE TABLE IF NOT EXISTS research_runs (
    id TEXT PRIMARY KEY,
    agent TEXT NOT NULL,
    query TEXT NOT NULL,
    market_scope TEXT NOT NULL DEFAULT 'Indonesia',
    status TEXT NOT NULL DEFAULT 'collecting' CHECK(status IN ('collecting','reviewing','completed','cancelled')),
    started_at TEXT NOT NULL,
    completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_research_runs_started ON research_runs(started_at);

CREATE TABLE IF NOT EXISTS research_sources (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    opportunity_id TEXT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    publisher TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('official','industry','news','community','academic','other')),
    published_at TEXT NOT NULL DEFAULT '',
    excerpt TEXT NOT NULL DEFAULT '',
    content_hash TEXT NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'unverified' CHECK(verification_status IN ('unverified','verified','rejected')),
    reviewer_notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES research_runs(id) ON DELETE CASCADE,
    FOREIGN KEY(opportunity_id) REFERENCES opportunities(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_research_sources_run ON research_sources(run_id);
CREATE INDEX IF NOT EXISTS idx_research_sources_opportunity ON research_sources(opportunity_id);
CREATE INDEX IF NOT EXISTS idx_research_sources_status ON research_sources(verification_status);

CREATE TABLE IF NOT EXISTS opportunity_scores (
    opportunity_id TEXT PRIMARY KEY,
    dimensions_json TEXT NOT NULL,
    score REAL NOT NULL CHECK(score >= 0 AND score <= 100),
    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 100),
    verified_sources INTEGER NOT NULL DEFAULT 0,
    distinct_publishers INTEGER NOT NULL DEFAULT 0,
    recommendation TEXT NOT NULL,
    rationale TEXT NOT NULL,
    scored_at TEXT NOT NULL,
    FOREIGN KEY(opportunity_id) REFERENCES opportunities(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_opportunity_scores_rank ON opportunity_scores(score DESC, confidence DESC);

CREATE TABLE IF NOT EXISTS market_comparisons (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    opportunity_ids_json TEXT NOT NULL,
    comparison_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_market_comparisons_created ON market_comparisons(created_at);

CREATE TABLE IF NOT EXISTS ceo_decisions (
    id TEXT PRIMARY KEY,
    comparison_id TEXT NOT NULL,
    selected_opportunity_id TEXT,
    decision TEXT NOT NULL CHECK(decision IN ('recommend_pilot','collect_evidence','deprioritize')),
    rationale TEXT NOT NULL,
    owner_approval_required INTEGER NOT NULL DEFAULT 1 CHECK(owner_approval_required = 1),
    created_at TEXT NOT NULL,
    FOREIGN KEY(comparison_id) REFERENCES market_comparisons(id) ON DELETE CASCADE,
    FOREIGN KEY(selected_opportunity_id) REFERENCES opportunities(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_ceo_decisions_created ON ceo_decisions(created_at);



CREATE TABLE IF NOT EXISTS research_search_logs (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    query TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('completed','failed')),
    result_count INTEGER NOT NULL DEFAULT 0 CHECK(result_count >= 0),
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES research_runs(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_research_search_logs_created ON research_search_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_research_search_logs_run ON research_search_logs(run_id);



-- Per-UTC-day model call cap. This is not a substitute for provider neuron/token quotas.
CREATE TABLE IF NOT EXISTS model_usage_daily (
    day_utc TEXT PRIMARY KEY,
    call_count INTEGER NOT NULL DEFAULT 0 CHECK(call_count >= 0),
    updated_at TEXT NOT NULL
);


-- One model attempt per task, including failed attempts, to prevent accidental duplicate billing.
CREATE TABLE IF NOT EXISTS model_execution_claims (
    task_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL CHECK(provider IN ('cloudflare','groq','gemini')),
    status TEXT NOT NULL CHECK(status IN ('started','completed','failed')),
    artifact_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES agent_tasks(id) ON DELETE CASCADE
);


-- Continuous IT operations: deduplicated incident queue and scheduler heartbeat.
CREATE TABLE IF NOT EXISTS operational_incidents (
    id TEXT PRIMARY KEY,
    fingerprint TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('low','medium','high','critical')),
    summary TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','investigating','resolved','ignored')),
    occurrence_count INTEGER NOT NULL DEFAULT 1 CHECK(occurrence_count >= 1),
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    resolved_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_operational_incidents_status ON operational_incidents(status, last_seen_at);

-- Sanitized provenance for CI/runtime incidents; never stores raw logs or secrets.
CREATE TABLE IF NOT EXISTS operational_incident_evidence (
    incident_id TEXT PRIMARY KEY,
    repository TEXT NOT NULL CHECK(repository = 'ranggalazuardy-source/aura-autopilot'),
    workflow_name TEXT NOT NULL,
    workflow_run_id INTEGER NOT NULL CHECK(workflow_run_id > 0),
    run_attempt INTEGER NOT NULL CHECK(run_attempt > 0),
    run_url TEXT NOT NULL,
    head_branch TEXT NOT NULL,
    head_sha TEXT NOT NULL CHECK(length(head_sha) = 40),
    conclusion TEXT NOT NULL CHECK(conclusion = 'failure'),
    failed_jobs_json TEXT NOT NULL CHECK(json_valid(failed_jobs_json) AND json_type(failed_jobs_json) = 'array'),
    triage_category TEXT NOT NULL DEFAULT 'unclassified' CHECK(triage_category IN ('unclassified','automated_test_regression','python_syntax_or_import','dependency_or_security_audit','database_schema','cloudflare_deployment_or_config','container_or_runtime','unknown_or_unclassified')),
    candidate_paths_json TEXT NOT NULL DEFAULT '[]' CHECK(json_valid(candidate_paths_json) AND json_type(candidate_paths_json) = 'array'),
    triage_owner TEXT NOT NULL DEFAULT 'Incident Response Commander' CHECK(triage_owner IN ('Incident Response Commander','IT_AI_ENGINEER')),
    created_at TEXT NOT NULL,
    FOREIGN KEY(incident_id) REFERENCES operational_incidents(id) ON DELETE CASCADE,
    UNIQUE(repository, workflow_run_id, run_attempt)
);
CREATE INDEX IF NOT EXISTS idx_operational_incident_evidence_created
    ON operational_incident_evidence(created_at);


CREATE TABLE IF NOT EXISTS operational_heartbeats (
    id TEXT PRIMARY KEY,
    scheduled_at TEXT NOT NULL,
    queued_tasks INTEGER NOT NULL DEFAULT 0 CHECK(queued_tasks >= 0),
    in_progress_tasks INTEGER NOT NULL DEFAULT 0 CHECK(in_progress_tasks >= 0),
    blocked_tasks INTEGER NOT NULL DEFAULT 0 CHECK(blocked_tasks >= 0),
    recovered_leases INTEGER NOT NULL DEFAULT 0 CHECK(recovered_leases >= 0)
);
CREATE INDEX IF NOT EXISTS idx_operational_heartbeats_scheduled ON operational_heartbeats(scheduled_at);


-- Single-use owner receipts for guarded automated repair execution.
-- Consumption is a single conditional UPDATE ... RETURNING statement.
CREATE TABLE IF NOT EXISTS patch_approval_receipts (
    id TEXT PRIMARY KEY,
    approved_by TEXT NOT NULL,
    incident_id TEXT NOT NULL,
    base_sha TEXT NOT NULL CHECK(length(base_sha) = 40),
    patch_sha256 TEXT NOT NULL CHECK(length(patch_sha256) = 64),
    approved_paths_json TEXT NOT NULL CHECK(json_valid(approved_paths_json) AND json_type(approved_paths_json) = 'array'),
    expires_at INTEGER NOT NULL,
    revoked_at INTEGER,
    consumed_at INTEGER,
    created_at INTEGER NOT NULL,
    CHECK(expires_at > created_at)
);
CREATE INDEX IF NOT EXISTS idx_patch_approval_receipts_expiry
    ON patch_approval_receipts(expires_at);
CREATE INDEX IF NOT EXISTS idx_patch_approval_receipts_incident
    ON patch_approval_receipts(incident_id, created_at);


-- Single-use repair runner execution requests; patch bytes remain private until claimed.
CREATE TABLE IF NOT EXISTS repair_execution_requests (
    id TEXT PRIMARY KEY CHECK(length(id) = 32),
    incident_id TEXT NOT NULL,
    base_sha TEXT NOT NULL CHECK(length(base_sha) = 40),
    patch_sha256 TEXT NOT NULL CHECK(length(patch_sha256) = 64),
    patch_text TEXT NOT NULL CHECK(length(patch_text) BETWEEN 1 AND 256000),
    approved_paths_json TEXT NOT NULL CHECK(json_valid(approved_paths_json) AND json_type(approved_paths_json) = 'array'),
    approval_receipt_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK(status IN ('queued','dispatched','claimed','expired','blocked')),
    expires_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    claimed_at INTEGER,
    CHECK(expires_at > created_at)
);
CREATE INDEX IF NOT EXISTS idx_repair_execution_requests_status_expiry
    ON repair_execution_requests(status, expires_at);


-- Owner-reviewable repair proposals, persisted before any approval or runner queueing.
CREATE TABLE IF NOT EXISTS repair_patch_proposals (
    id TEXT PRIMARY KEY CHECK(length(id) = 32),
    incident_id TEXT NOT NULL REFERENCES operational_incidents(id),
    base_sha TEXT NOT NULL CHECK(length(base_sha) = 40),
    patch_sha256 TEXT NOT NULL CHECK(length(patch_sha256) = 64),
    patch_text TEXT NOT NULL CHECK(length(patch_text) BETWEEN 1 AND 256000),
    approved_paths_json TEXT NOT NULL
        CHECK(json_valid(approved_paths_json) AND json_type(approved_paths_json) = 'array'),
    status TEXT NOT NULL DEFAULT 'proposed'
        CHECK(status IN ('proposed','approving','approved','queueing','queued','expired','blocked')),
    expires_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    approval_receipt_id TEXT,
    execution_request_id TEXT,
    CHECK(expires_at > created_at)
);
CREATE INDEX IF NOT EXISTS idx_repair_patch_proposals_status_expiry
    ON repair_patch_proposals(status, expires_at);
CREATE INDEX IF NOT EXISTS idx_repair_patch_proposals_incident
    ON repair_patch_proposals(incident_id, created_at);
