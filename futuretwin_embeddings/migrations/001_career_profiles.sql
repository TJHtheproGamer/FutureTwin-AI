-- Resume-derived profiles only; uploaded documents are never persisted.
-- The application encrypts encrypted_payload with AES-GCM before writing it.
CREATE TABLE IF NOT EXISTS futuretwin_career_profiles (
    profile_id UUID PRIMARY KEY,
    owner_hash BYTEA NOT NULL UNIQUE CHECK (octet_length(owner_hash) = 32),
    encrypted_payload BYTEA NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
