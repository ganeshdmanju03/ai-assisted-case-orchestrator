CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    state TEXT,
    retry_count INTEGER,
    last_error_type TEXT,
    priority TEXT
);

CREATE TABLE IF NOT EXISTS ai_decisions (
    idempotency_key TEXT PRIMARY KEY,
    decision_json TEXT,
    model TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    outcome TEXT,
    intent TEXT,
    route_target TEXT,
    confidence REAL,
    created_at TEXT
);