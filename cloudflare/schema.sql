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
