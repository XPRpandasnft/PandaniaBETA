-- Safe, additive WebAuth session tables.
-- Existing players, wallet_accounts, guest_accounts, and player_saves are not changed.

CREATE TABLE IF NOT EXISTS wallet_auth_proofs (
  proof_hash TEXT PRIMARY KEY,
  used_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS wallet_sessions (
  token_hash TEXT PRIMARY KEY,
  player_id TEXT NOT NULL,
  chain_id TEXT NOT NULL,
  wallet_account TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  revoked_at INTEGER,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_wallet_sessions_player
  ON wallet_sessions (player_id);

CREATE INDEX IF NOT EXISTS idx_wallet_sessions_wallet
  ON wallet_sessions (chain_id, wallet_account);
