CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    channel TEXT NOT NULL,
    rationale TEXT NOT NULL,
    estimated_cost REAL NOT NULL DEFAULT 0,
    estimated_revenue REAL NOT NULL DEFAULT 0,
    risk_level TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'proposed',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_opportunities_created_at ON opportunities(created_at);

CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_approvals_created_at ON approvals(created_at);

CREATE TABLE IF NOT EXISTS ledger (
    id TEXT PRIMARY KEY,
    entry_type TEXT NOT NULL CHECK(entry_type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ledger_created_at ON ledger(created_at);
