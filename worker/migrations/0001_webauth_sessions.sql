-- Apply to the existing pandania-game-db D1 database only.
-- Idempotent: preserves all existing wallet associations and player saves.
CREATE TABLE IF NOT EXISTS wallet_sessions (
  token_hash TEXT PRIMARY KEY,
  player_id TEXT NOT NULL,
  chain_id TEXT NOT NULL,
  wallet_account TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  revoked_at INTEGER,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wallet_sessions_player
  ON wallet_sessions(player_id);

CREATE TABLE IF NOT EXISTS wallet_auth_proofs (
  proof_hash TEXT PRIMARY KEY,
  used_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_wallet_auth_proofs_used
  ON wallet_auth_proofs(used_at);
