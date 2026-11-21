"""Regression tests for the model_execution_claims D1 migration."""
import sqlite3
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "cloudflare" / "schema.sql"
MIGRATION = ROOT / "cloudflare" / "migrations" / "0001_expand_model_execution_claims.sql"


class ModelExecutionClaimsMigrationTests(unittest.TestCase):
    def test_migration_preserves_existing_rows_and_accepts_runtime_values(self):
        db = sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript(SCHEMA.read_text(encoding="utf-8"))
        db.execute(
            """INSERT INTO agent_tasks
               (id, agent, objective, priority, related_opportunity_id, status,
                result_summary, created_at, updated_at)
               VALUES ('migration_existing', 'AI Engineer', 'existing claim',
                       'normal', '', 'in_progress', '', '2026-01-01', '2026-01-01')"""
        )
        db.execute(
            """INSERT INTO model_execution_claims
               (task_id, provider, status, artifact_id, created_at)
               VALUES ('migration_existing', 'cloudflare', 'started', NULL, '2026-01-01')"""
        )
        db.commit()

        db.executescript(MIGRATION.read_text(encoding="utf-8"))

        existing = db.execute(
            "SELECT provider, status FROM model_execution_claims WHERE task_id = ?",
            ("migration_existing",),
        ).fetchone()
        self.assertEqual(existing, ("cloudflare", "started"))

        db.execute(
            """INSERT INTO agent_tasks
               (id, agent, objective, priority, related_opportunity_id, status,
                result_summary, created_at, updated_at)
               VALUES ('migration_gemini', 'AI Engineer', 'Gemini claim',
                       'normal', '', 'in_progress', '', '2026-01-02', '2026-01-02')"""
        )
        db.execute(
            """INSERT INTO model_execution_claims
               (task_id, provider, status, artifact_id, created_at)
               VALUES ('migration_gemini', 'gemini', 'failed', NULL, '2026-01-02')"""
        )
        self.assertEqual(
            db.execute(
                "SELECT provider, status FROM model_execution_claims WHERE task_id = ?",
                ("migration_gemini",),
            ).fetchone(),
            ("gemini", "failed"),
        )
        db.execute(
            """INSERT INTO agent_tasks
               (id, agent, objective, priority, related_opportunity_id, status,
                result_summary, created_at, updated_at)
               VALUES ('migration_auto', 'AI Engineer', 'automatic provider claim',
                       'normal', '', 'in_progress', '', '2026-01-03', '2026-01-03')"""
        )
        db.execute(
            """INSERT INTO model_execution_claims
               (task_id, provider, status, artifact_id, created_at)
               VALUES ('migration_auto', 'auto', 'started', NULL, '2026-01-03')"""
        )
        self.assertEqual(
            db.execute(
                "SELECT provider, status FROM model_execution_claims WHERE task_id = ?",
                ("migration_auto",),
            ).fetchone(),
            ("auto", "started"),
        )
        self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
        db.close()


if __name__ == "__main__":
    unittest.main()
