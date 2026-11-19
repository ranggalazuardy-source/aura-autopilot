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
