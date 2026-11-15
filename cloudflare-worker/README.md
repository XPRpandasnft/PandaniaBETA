# Pandania WebAuth Worker — staging only

This project is a separate staging API for Adventures of Pandania: The Lost Realms.
It must deploy as `pandania-game-api-webauth-test`, never as the production Worker.

## Cloudflare Workers Builds settings

Create a **new Worker** in Cloudflare named exactly `pandania-game-api-webauth-test`, then connect it to this GitHub repository.

Use these settings:

| Setting | Value |
|---|---|
| Git repository | `XPRpandasnft/PandaniaBETA` |
| Branch | `webauth-secure-login` |
| Root directory | `cloudflare-worker` |
| Build command | Leave blank |
| Deploy command | `npx wrangler deploy` |
| Preview builds | Disable for this staging-only setup |

The package manifest pins `@proton/signing-request` and Wrangler. Workers Builds installs the npm dependencies and Wrangler bundles the dependency when deploying. Cloudflare's documented settings are under **Workers & Pages → [the new staging Worker] → Settings → Builds**.

**Do not connect this repository to the existing production Worker.** Do not set `main` as the branch for this staging project. The Worker name in Cloudflare must match the `name` in `wrangler.toml`.

## Staging database — do not use production D1

Create a separate D1 database named exactly `pandania-game-db-webauth-test`. Copy the required game tables and records from the production database into staging so existing wallet-to-player mappings and saves can be tested without touching production. Preserve the original `player_id` values and all rows in `wallet_accounts`, `guest_accounts`, and `player_saves`.

Required existing tables:
- `players`
- `wallet_accounts`
- `guest_accounts`
- `player_saves`

Then replace `REPLACE_WITH_STAGING_D1_DATABASE_ID` in `wrangler.toml` with the ID of the **new staging database only**. The D1 binding must be named `DB`.

Apply the additive migration to staging:
```sh
npx wrangler d1 execute pandania-game-db-webauth-test --remote --file=./migrations/0001_webauth_sessions.sql
```

The migration creates only `wallet_auth_proofs`, `wallet_sessions`, and indexes. It does not alter or delete player data.

## Authentication behavior

- The game asks WebAuth for an identity proof with `link.identify()`.
- The Worker parses the proof with the Proton signing-request package.
- The Worker checks the XPR mainnet chain ID, loads the wallet's current on-chain permission authority, and verifies the proof signature and expiry.
- The Worker records a proof fingerprint to reject exact proof replay.
- It issues a random 256-bit session token and stores only its SHA-256 hash.
- Save/load require a valid, unexpired, non-revoked WebAuth session.
- Existing wallet mappings are authoritative and are never reassigned.
- A legacy guest token may migrate an unlinked guest character only when no other wallet is already associated with that player. Existing guest records are retained.
- Guest creation and unsigned wallet-link routes are not provided by this Worker.

## Staging verification checklist

Do not merge the branch or change the production game/API until all of these pass:

1. Confirm `GET /health` returns the WebAuth staging API status.
2. Log in with a wallet that already has a `wallet_accounts` mapping; confirm it receives the same `player_id`.
3. Load the matching copied `player_saves` row and verify inventory, location, quests, stats, and character progress.
4. Log in with a new wallet; confirm a new player identity is created.
5. Confirm an invalid signature, wrong chain, unknown permission, expired proof, and replayed proof are rejected.
6. Confirm an already-linked wallet cannot be moved to another character.
7. Save, close the browser, reconnect, and load the same character on desktop and mobile.
8. Confirm guest-create and unsigned wallet-link requests are rejected.

The game page on this branch points to the staging Worker URL. Production `main`, the live game, production Worker, and production D1 must remain untouched until staging tests pass and a separate production cutover is approved.
