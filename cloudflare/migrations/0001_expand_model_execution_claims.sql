-- Expand model execution claim constraints to match the runtime contract.
-- Preserve all existing claims while allowing Gemini and explicit failed outcomes.
CREATE TABLE model_execution_claims_new (
    task_id TEXT PRIMARY KEY,
    provider TEXT NOT NULL CHECK(provider IN ('auto','cloudflare','groq','gemini')),
    status TEXT NOT NULL CHECK(status IN ('started','completed','failed')),
    artifact_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES agent_tasks(id) ON DELETE CASCADE
);

INSERT INTO model_execution_claims_new (task_id, provider, status, artifact_id, created_at)
SELECT task_id, provider, status, artifact_id, created_at
FROM model_execution_claims;

DROP TABLE model_execution_claims;
ALTER TABLE model_execution_claims_new RENAME TO model_execution_claims;
