# Pandania WebAuth Worker

This Worker is the server-side authentication and cloud-save API for Adventures of Pandania: The Lost Realms.

## Security design

- The browser requests a Proton identity proof using `link.identify()`.
- The Worker decodes the proof with the official Proton signing-request package.
- The Worker retrieves the wallet's current account permissions from XPR Network RPC and verifies the proof signature against the selected on-chain permission authority.
- A proof fingerprint is stored in `wallet_auth_proofs` to prevent the same proof being accepted twice.
- The Worker issues a random 256-bit session token; only its SHA-256 hash is stored in `wallet_sessions`.
- Save and load endpoints accept only a valid, unexpired, non-revoked WebAuth session.
- Existing wallet-to-player associations are authoritative. This code never moves an existing wallet association or overwrites another character's data.
- An old guest token can be supplied once during sign-in to migrate that guest player ID, but only if that player is not already associated with another wallet.

## Before building or deploying

1. Create a separate **staging D1 database** for authentication testing. Do not point a test Worker at the live `pandania-game-db` until testing is complete.
2. Apply `migrations/0001_webauth_sessions.sql` to the staging database.
3. In `wrangler.toml`, replace `REPLACE_WITH_STAGING_D1_DATABASE_ID` with the staging D1 database ID.
4. Confirm the staging Worker name is `pandania-game-api-webauth-test`. It must not overwrite the current production Worker.
5. Configure Workers Builds to use this directory (`cloudflare-worker`) as the root directory and branch `webauth-secure-login`.
6. Build command: `npm install`. Deploy command: `npx wrangler deploy`.

## D1 schema requirements

The staging database needs the existing game tables with the same schema as production:

- `players`
- `wallet_accounts`
- `guest_accounts`
- `player_saves`

The additive migration in this directory creates only the WebAuth proof/session tables and indexes. It does not alter or delete existing game records.

## Important deployment note

Do not deploy this Worker against production or merge this branch yet. First verify the proof flow on desktop and mobile using a staging D1 copy. Then test:
- a wallet with an existing `wallet_accounts` association and save,
- a wallet with no existing association,
- an expired/replayed identity proof,
- an account signing with an invalid permission,
- a wallet already linked to a different player,
- save/load persistence after closing and reopening the browser.

The current production Worker remains untouched until an explicit production cutover.
