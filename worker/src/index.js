import { IdentityProof } from "@wharfkit/signing-request";

const GAME_ORIGIN = "https://pandania.xyz";
const XPR_CHAIN_ID = "384da888112027f0321850a169f737c33e53b388aad48b5adace4bab97f437e0";
const RPC_ENDPOINTS = [
  "https://api.protonnz.com",
  "https://proton.eosusa.io",
  "https://proton.protonuk.io"
];
const MAX_SAVE_SIZE = 500_000;
const SESSION_TTL_SECONDS = 30 * 24 * 60 * 60;
const MAX_BODY_SIZE = 600_000;

function headers(extra = {}) {
  return {
    "Access-Control-Allow-Origin": GAME_ORIGIN,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Vary": "Origin",
    "Cache-Control": "no-store",
    ...extra
  };
}
function json(data, status = 200) {
  return Response.json(data, { status, headers: headers() });
}
function hex(bytes) {
  return Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2, "0")).join("");
}
function randomToken() {
  return hex(crypto.getRandomValues(new Uint8Array(32)));
}
async function sha256(value) {
  return hex(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)));
}
async function readJson(request) {
  const length = Number(request.headers.get("Content-Length") || 0);
  if (length > MAX_BODY_SIZE) throw new Error("BODY_TOO_LARGE");
  const raw = await request.text();
  if (raw.length > MAX_BODY_SIZE) throw new Error("BODY_TOO_LARGE");
  try { return JSON.parse(raw); } catch { throw new Error("INVALID_JSON"); }
}
function validAccountName(value) {
  return typeof value === "string" && /^[a-z1-5.]{1,12}$/.test(value);
}
async function getChainAccount(accountName) {
  const body = JSON.stringify({ account_name: accountName });
  for (const endpoint of RPC_ENDPOINTS) {
    try {
      const response = await fetch(endpoint + "/v1/chain/get_account", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body
      });
      if (!response.ok) continue;
      const account = await response.json();
      if (account && Array.isArray(account.permissions)) return account;
    } catch (_) {}
  }
  throw new Error("CHAIN_ACCOUNT_UNAVAILABLE");
}
async function verifyWebAuthProof(proofText) {
  if (typeof proofText !== "string" || proofText.length < 20 || proofText.length > 12000) {
    throw new Error("INVALID_IDENTITY_PROOF");
  }

  let proof;
  try {
    proof = IdentityProof.fromString(proofText);
  } catch (_) {
    throw new Error("INVALID_IDENTITY_PROOF");
  }

  const chainId = String(proof.chainId);
  const walletAccount = String(proof.signer.actor).toLowerCase();
  const permissionName = String(proof.signer.permission).toLowerCase();

  if (chainId.toLowerCase() !== XPR_CHAIN_ID) throw new Error("WRONG_CHAIN");
  if (!validAccountName(walletAccount) || !validAccountName(permissionName)) {
    throw new Error("INVALID_SIGNER");
  }

  const account = await getChainAccount(walletAccount);
  const permission = account.permissions.find(p =>
    String(p.perm_name).toLowerCase() === permissionName
  );
  if (!permission || !permission.required_auth) throw new Error("UNKNOWN_PERMISSION");

  let verified = false;
  try { verified = proof.verify(permission.required_auth, account.head_block_time); } catch (_) {}
  if (!verified) throw new Error("INVALID_SIGNATURE_OR_EXPIRED_PROOF");

  return { walletAccount, chainId, permissionName, proofText };
}
async function consumeProofOnce(env, proofText) {
  const proofHash = await sha256(proofText);
  const inserted = await env.DB.prepare(
    "INSERT INTO wallet_auth_proofs (proof_hash, used_at) VALUES (?, ?) ON CONFLICT(proof_hash) DO NOTHING RETURNING proof_hash"
  ).bind(proofHash, Math.floor(Date.now() / 1000)).first();
  if (!inserted) throw new Error("IDENTITY_PROOF_ALREADY_USED");
}
async function findLegacyPlayer(env, tokens, chainId) {
  if (!Array.isArray(tokens)) return null;
  for (const token of tokens.slice(0, 2)) {
    if (typeof token !== "string" || !/^[a-f0-9]{64}$/.test(token)) continue;
    const tokenHash = await sha256(token);
    const guest = await env.DB.prepare(
      "SELECT player_id FROM guest_accounts WHERE token_hash = ?"
    ).bind(tokenHash).first();
    if (!guest || !guest.player_id) continue;

    const otherWallet = await env.DB.prepare(
      "SELECT wallet_account FROM wallet_accounts WHERE chain_id = ? AND player_id = ? LIMIT 1"
    ).bind(chainId, guest.player_id).first();
    if (!otherWallet) return guest.player_id;
    // A legacy token already attached to a different wallet must never be moved.
  }
  return null;
}
async function resolvePlayerForWallet(env, auth, legacyTokens) {
  const existing = await env.DB.prepare(
    "SELECT player_id FROM wallet_accounts WHERE chain_id = ? AND wallet_account = ?"
  ).bind(auth.chainId, auth.walletAccount).first();
  if (existing && existing.player_id) {
    return { playerId: existing.player_id, migratedGuest: false, alreadyLinked: true };
  }

  const legacyPlayerId = await findLegacyPlayer(env, legacyTokens, auth.chainId);
  const candidatePlayerId = legacyPlayerId || crypto.randomUUID();

  // Insert only if this player has no other wallet mapping. This conditional
  // statement makes the one-wallet-per-player rule part of the DB write itself.
  await env.DB.prepare(
    `INSERT INTO wallet_accounts (chain_id, wallet_account, player_id)
     SELECT ?, ?, ?
     WHERE NOT EXISTS (
       SELECT 1 FROM wallet_accounts
       WHERE chain_id = ? AND player_id = ?
     )
     ON CONFLICT(chain_id, wallet_account) DO NOTHING`
  ).bind(auth.chainId, auth.walletAccount, candidatePlayerId, auth.chainId, candidatePlayerId).run();

  // Resolve concurrent first-login races using the database's winning mapping.
  let finalMapping = await env.DB.prepare(
    "SELECT player_id FROM wallet_accounts WHERE chain_id = ? AND wallet_account = ?"
  ).bind(auth.chainId, auth.walletAccount).first();

  // If another wallet claimed the same legacy guest identity at the same time,
  // do not merge the two wallets. Give this wallet a fresh independent player.
  if (!finalMapping && legacyPlayerId) {
    const separatePlayerId = crypto.randomUUID();
    await env.DB.prepare(
      `INSERT OR IGNORE INTO wallet_accounts (chain_id, wallet_account, player_id)
       VALUES (?, ?, ?)`
    ).bind(auth.chainId, auth.walletAccount, separatePlayerId).run();
    finalMapping = await env.DB.prepare(
      "SELECT player_id FROM wallet_accounts WHERE chain_id = ? AND wallet_account = ?"
    ).bind(auth.chainId, auth.walletAccount).first();
  }

  if (!finalMapping || !finalMapping.player_id) throw new Error("WALLET_MAPPING_FAILED");
  return {
    playerId: finalMapping.player_id,
    migratedGuest: !!legacyPlayerId && finalMapping.player_id === legacyPlayerId,
    alreadyLinked: false
  };
}
async function createWalletPlayer(env, auth) {
  const candidate = crypto.randomUUID();
  await env.DB.prepare(
    "INSERT OR IGNORE INTO wallet_accounts (chain_id, wallet_account, player_id) VALUES (?, ?, ?)"
  ).bind(auth.chainId, auth.walletAccount, candidate).run();
  const row = await env.DB.prepare(
    "SELECT player_id FROM wallet_accounts WHERE chain_id = ? AND wallet_account = ?"
  ).bind(auth.chainId, auth.walletAccount).first();
  if (!row || !row.player_id) throw new Error("WALLET_MAPPING_FAILED");
  return row.player_id;
}
async function createSession(env, playerId, auth) {
  const token = randomToken();
  const tokenHash = await sha256(token);
  const expiresAt = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  await env.DB.prepare(
    "INSERT INTO wallet_sessions (token_hash, player_id, chain_id, wallet_account, expires_at, revoked_at) VALUES (?, ?, ?, ?, ?, NULL)"
  ).bind(tokenHash, playerId, auth.chainId, auth.walletAccount, expiresAt).run();
  return { token, expires_at: expiresAt };
}
async function authenticate(request, env) {
  const authorization = request.headers.get("Authorization") || "";
  if (!authorization.startsWith("Bearer ")) return null;
  const token = authorization.slice(7);
  if (!/^[a-f0-9]{64}$/.test(token)) return null;
  const tokenHash = await sha256(token);
  return env.DB.prepare(
    "SELECT player_id, chain_id, wallet_account FROM wallet_sessions WHERE token_hash = ? AND expires_at > ? AND revoked_at IS NULL"
  ).bind(tokenHash, Math.floor(Date.now() / 1000)).first();
}
async function handleLogin(request, env) {
  const body = await readJson(request);
  const auth = await verifyWebAuthProof(body.proof);
  await consumeProofOnce(env, auth.proofText);
  const resolved = await resolvePlayerForWallet(env, auth, body.legacy_tokens);
  const session = await createSession(env, resolved.playerId, auth);
  return json({
    success: true,
    player_id: resolved.playerId,
    wallet_account: auth.walletAccount,
    token: session.token,
    expires_at: session.expires_at,
    already_linked: resolved.alreadyLinked,
    migrated_guest: resolved.migratedGuest
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin");
    if (origin && origin !== GAME_ORIGIN) return json({ success: false, error: "Origin not allowed" }, 403);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: headers() });
    }
    if (!env.DB) return json({ success: false, error: "Database binding DB is not configured" }, 500);

    const url = new URL(request.url);
    try {
      if (url.pathname === "/health" && request.method === "GET") {
        return json({ success: true, message: "Pandania WebAuth API online", auth: "webauth-only" });
      }

      if (url.pathname === "/api/auth/webauth" && request.method === "POST") {
        return await handleLogin(request, env);
      }

      if (url.pathname === "/api/auth/logout" && request.method === "POST") {
        const account = await authenticate(request, env);
        if (!account) return json({ success: false, error: "Invalid or expired session" }, 401);
        const token = request.headers.get("Authorization").slice(7);
        await env.DB.prepare(
          "UPDATE wallet_sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL"
        ).bind(Math.floor(Date.now() / 1000), await sha256(token)).run();
        return json({ success: true });
      }

      if (url.pathname === "/api/player/save" && request.method === "POST") {
        const account = await authenticate(request, env);
        if (!account) return json({ success: false, error: "Invalid or expired WebAuth session" }, 401);
        const body = await readJson(request);
        if (!body || typeof body.save !== "object" || body.save === null || Array.isArray(body.save)) {
          return json({ success: false, error: "A valid save object is required" }, 400);
        }
        const saveJson = JSON.stringify(body.save);
        if (saveJson.length > MAX_SAVE_SIZE) return json({ success: false, error: "Save data is too large" }, 413);
        await env.DB.prepare(`
          INSERT INTO player_saves (player_id, save_json, updated_at)
          VALUES (?, ?, CURRENT_TIMESTAMP)
          ON CONFLICT(player_id) DO UPDATE SET
            save_json = excluded.save_json,
            updated_at = CURRENT_TIMESTAMP
        `).bind(account.player_id, saveJson).run();
        return json({ success: true, message: "Game saved", player_id: account.player_id });
      }

      if (url.pathname === "/api/player/load" && request.method === "GET") {
        const account = await authenticate(request, env);
        if (!account) return json({ success: false, error: "Invalid or expired WebAuth session" }, 401);
        const result = await env.DB.prepare(
          "SELECT save_json, updated_at FROM player_saves WHERE player_id = ?"
        ).bind(account.player_id).first();
        if (!result) return json({ success: true, player_id: account.player_id, save: null });
        let save;
        try { save = JSON.parse(result.save_json); } catch { throw new Error("CORRUPT_SAVE_JSON"); }
        return json({ success: true, player_id: account.player_id, save, updated_at: result.updated_at });
      }

      // Legacy guest endpoints are intentionally disabled. Existing rows remain
      // available only for one-time migration after a valid WebAuth proof.
      if (url.pathname === "/api/guest/create" || url.pathname === "/api/wallet/link") {
        return json({ success: false, code: "WEBAUTH_REQUIRED", error: "Guest login and unsigned wallet linking are disabled. Connect WebAuth." }, 410);
      }

      return json({ success: false, error: "Route not found" }, 404);
    } catch (error) {
      const code = String(error && error.message || "INTERNAL_ERROR");
      const clientErrors = new Set([
        "BODY_TOO_LARGE", "INVALID_JSON", "INVALID_IDENTITY_PROOF", "WRONG_CHAIN",
        "INVALID_SIGNER", "UNKNOWN_PERMISSION", "INVALID_SIGNATURE_OR_EXPIRED_PROOF",
        "IDENTITY_PROOF_ALREADY_USED"
      ]);
      if (clientErrors.has(code)) {
        const status = code === "BODY_TOO_LARGE" ? 413 : 401;
        return json({ success: false, code, error: code.replaceAll("_", " ").toLowerCase() }, status);
      }
      console.error("Pandania WebAuth API error:", error);
      return json({ success: false, code: "INTERNAL_ERROR", error: "Internal server error" }, 500);
    }
  }
};
