# Pandania WebAuth-only game API

This Worker is the staging API for the Lost Realms WebAuth migration.

## Required Cloudflare configuration

- Worker name: `pandania-game-api-webauth-test`
- D1 binding variable: `DB`
- D1 database: the existing `pandania-game-db` (do not create a replacement)
- Existing tables required:
  - `wallet_accounts(chain_id, wallet_account, player_id, linked_at)`
  - `wallet_sessions(token_hash, player_id, chain_id, wallet_account, expires_at, revoked_at)`
  - `wallet_auth_proofs(proof_hash, used_at)`
  - `guest_accounts(player_id, token_hash)` (read-only for one-time migration)
  - `player_saves(player_id, save_json, updated_at)`

Install and build with npm, then deploy this directory to the staging Worker. Keep the live Worker untouched.

## Authentication behavior

- The browser submits the WebAuth ESR identity proof.
- The Worker parses the proof with WharfKit, checks the XPR mainnet chain ID, loads the signer's current on-chain permission authority, and verifies the signature and expiration.
- A proof hash is consumed once to reject exact replays.
- Existing wallet mappings always win. Existing mappings are never reassigned.
- A legacy guest token may migrate its character only if that player has no existing wallet association. Legacy guest rows are never deleted.
- New wallet mappings create a new player ID.
- Session bearer tokens are 256-bit random values; only SHA-256 hashes are stored.
- Save/load endpoints accept only unexpired, non-revoked WebAuth sessions.
- Guest creation and unsigned wallet linking return HTTP 410.

## Important deployment note

This source must be built with Wrangler so the WharfKit dependency is bundled. It cannot be pasted unchanged into the Cloudflare dashboard's plain-text editor. Do not switch the production game URL to this Worker until the staging tests pass.
