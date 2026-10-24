-- Offline-precomputed ESCO/UN map coordinates and associations.
-- Model inference runs only in the explicit snapshot generator, never at startup.
CREATE TABLE IF NOT EXISTS futuretwin_sdg_map_snapshots (
    snapshot_key TEXT PRIMARY KEY,
    payload JSONB NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL
);
