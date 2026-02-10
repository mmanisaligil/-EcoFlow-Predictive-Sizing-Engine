-- Placeholder migration for future persistence requirements.
-- Current engine is deterministic and stateless.
CREATE TABLE IF NOT EXISTS migration_marker (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
