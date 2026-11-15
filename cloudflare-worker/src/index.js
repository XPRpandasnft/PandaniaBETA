import { IdentityProof } from "@proton/signing-request";

const GAME_ORIGIN = "https://pandania.xyz";
const MAX_SAVE_SIZE = 500_000;
const SESSION_TTL_SECONDS = 60 * 60 * 24 * 30;
const CHAIN_ID = "384da888112027f0321850a169f737c33e53b388aad48b5adace4bab97f437e0";
const RPC_ENDPOINTS = [
  "https://api.protonnz.com",
  "https://proton.eosusa.io",
  "https://proton.protonuk.io"
];

function jsonResponse(data, status = 200) {
  return Response.json(data, {
    status,
    headers: {
      "Access-Control-Allow-Origin": GAME_ORIGIN,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
      "Vary": "Origin",
      "Cache-Control": "no-store"
    }
  });
}

function randomToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return Array.from(bytes, b => b.toString(16).padStart(2, "0")).join("");
}

async function sha256(value) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, "0")).join("");
}

async function authenticateSession(request, env) {
  const header = request.headers.get("Authorization") || "";
  if (!header.startsWith("Bearer ")) return null;
  const token = header.slice(7);
  if (!/^[a-f0-9]{64}$/.test(token)) return null;

  const tokenHash = await sha256(token);
  const now = Math.floor(Date.now() / 1000);
  return env.DB.prepare(
    "SELECT player_id, chain_id, wallet_account FROM wallet_sessions WHERE token_hash = ? AND expires_at > ? AND revoked_at IS NULL"
  ).bind(tokenHash, now).first();
}

async function getChainAccount(accountName) {
  const payload = JSON.stringify({ account_name: accountName });
  for (const endpoint of RPC_ENDPOINTS) {
    try {
      const response = await fetch(endpoint + "/v1/chain/get_account", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload
      });
      if (!response.ok) continue;
      const account = await response.json();
      if (account && Array.isArray(account.permissions)) return account;
    } catch (error) {
      console.warn("XPR RPC unavailable:", endpoint, String(error));
    }
  }
  throw new Error("Unable to retrieve the wallet's on-chain permissions.");
}

async function authenticateLegacyGuestToken(token, env) {
  if (typeof token !== "string" || !/^[a-f0-9]{64}$/.test(token)) return null;
  const tokenHash = await sha256(token);
  return env.DB.prepare(
    "SELECT player_id FROM guest_accounts WHERE token_hash = ?"
  ).bind(tokenHash).first();
}

async function authenticateWebAuth(request, env) {
  const body = await request.json();
  if (!body || typeof body.proof !== "string" || body.proof.length > 8192) {
    return jsonResponse({ success: false, error: "A valid WebAuth identity proof is required." }, 400);
  }

  let proof;
  try {
    proof = IdentityProof.fromString(body.proof);
  } catch (error) {
    return jsonResponse({ success: false, error: "The WebAuth identity proof could not be decoded." }, 400);
  }

  const chainId = proof.chainId.toString().toLowerCase();
  const walletAccount = proof.signer.actor.toString().toLowerCase();
  const permissionName = proof.signer.permission.toString().toLowerCase();

  if (chainId !== CHAIN_ID) {
    return jsonResponse({ success: false, error: "The proof is for an unsupported blockchain." }, 400);
  }
  if (!/^[a-z1-5.]{1,13}$/.test(walletAccount) || !/^[a-z1-5.]{1,13}$/.test(permissionName)) {
    return jsonResponse({ success: false, error: "The proof contains an invalid XPR account or permission." }, 400);
  }

  let chainAccount;
  try {
    chainAccount = await getChainAccount(walletAccount);
  } catch (error) {
    console.error("WebAuth account lookup failed:", error);
    return jsonResponse({ success: false, error: "Could not verify the wallet on XPR Network. Please retry." }, 503);
  }

  const permission = chainAccount.permissions.find(
    item => String(item.perm_name).toLowerCase() === permissionName
  );
  if (!permission || !permission.required_auth) {
    return jsonResponse({ success: false, error: "The signing permission does not exist on this wallet." }, 401);
  }

  if (String(chainAccount.account_name || "").toLowerCase() !== walletAccount) {
    return jsonResponse({ success: false, error: "The XPR RPC account response did not match the signed wallet." }, 503);
  }

  let proofValid = false;
  try {
    proofValid = proof.verify(permission.required_auth, chainAccount.head_block_time);
  } catch (error) {
    console.warn("WebAuth proof verification error:", String(error));
  }
  if (!proofValid) {
    return jsonResponse({ success: false, error: "The WebAuth signature or its expiration is invalid." }, 401);
  }

  // Identity proofs are not nonce-bound by the Proton SDK. Store a one-use
  // fingerprint so a previously accepted proof cannot create another session.
  const proofHash = await sha256(proof.toString());
  const proofUsedAt = Math.floor(Date.now() / 1000);
  await env.DB.prepare(
    "DELETE FROM wallet_auth_proofs WHERE used_at < ?"
  ).bind(proofUsedAt - 60 * 60 * 24 * 30).run();

  const replayInsert = await env.DB.prepare(
    "INSERT OR IGNORE INTO wallet_auth_proofs (proof_hash, used_at) VALUES (?, ?)"
  ).bind(proofHash, proofUsedAt).run();
  if (!replayInsert.meta || replayInsert.meta.changes !== 1) {
    return jsonResponse({ success: false, error: "This WebAuth proof has already been used. Please reconnect and sign in again." }, 409);
  }

  let walletLink = await env.DB.prepare(
    "SELECT player_id FROM wallet_accounts WHERE chain_id = ? AND wallet_account = ?"
  ).bind(chainId, walletAccount).first();

  let playerId;
  let migratedGuest = false;
  if (walletLink) {
    // Existing wallet associations are authoritative and are never reassigned here.
    playerId = walletLink.player_id;
  } else {
    const legacyTokens = Array.isArray(body.legacy_tokens)
      ? body.legacy_tokens
      : [body.legacy_token];
    let legacy = null;
    for (const candidate of legacyTokens) {
      legacy = await authenticateLegacyGuestToken(candidate, env);
      if (legacy) break;
    }

    if (legacy) {
      migratedGuest = true;
      const existingPlayerWallet = await env.DB.prepare(
        "SELECT wallet_account FROM wallet_accounts WHERE chain_id = ? AND player_id = ? LIMIT 1"
      ).bind(chainId, legacy.player_id).first();

      if (existingPlayerWallet &&
          String(existingPlayerWallet.wallet_account).toLowerCase() !== walletAccount) {
        return jsonResponse({
          success: false,
          code: "PLAYER_ALREADY_LINKED_TO_ANOTHER_WALLET",
          error: "This saved character is already linked to a different wallet. No character data was changed."
        }, 409);
      }
      playerId = legacy.player_id;
    } else {
      playerId = crypto.randomUUID();
    }

    await env.DB.prepare(
      "INSERT OR IGNORE INTO players (player_id, username, level, xp, gold) VALUES (?, ?, 1, 0, 0)"
    ).bind(playerId, walletAccount).run();

    // Enforce one wallet per player atomically during the insert as well as
    // in the earlier friendly check. This closes the race where two wallets
    // try to claim the same legacy guest character at the same time.
    await env.DB.prepare(
      `INSERT OR IGNORE INTO wallet_accounts (chain_id, wallet_account, player_id)
       SELECT ?, ?, ?
       WHERE NOT EXISTS (
         SELECT 1 FROM wallet_accounts
         WHERE chain_id = ? AND player_id = ? AND wallet_account <> ?
       )`
    ).bind(chainId, walletAccount, playerId, chainId, playerId, walletAccount).run();

    walletLink = await env.DB.prepare(
      "SELECT player_id FROM wallet_accounts WHERE chain_id = ? AND wallet_account = ?"
    ).bind(chainId, walletAccount).first();

    if (!walletLink || walletLink.player_id !== playerId) {
      return jsonResponse({ success: false, code: "WALLET_LINK_CONFLICT", error: "The wallet is already associated with another character. Existing data was not moved." }, 409);
    }
  }

  const token = randomToken();
  const tokenHash = await sha256(token);
  const expiresAt = Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS;
  await env.DB.prepare(
    "INSERT INTO wallet_sessions (token_hash, player_id, chain_id, wallet_account, expires_at) VALUES (?, ?, ?, ?, ?)"
  ).bind(tokenHash, playerId, chainId, walletAccount, expiresAt).run();

  return jsonResponse({
    success: true,
    player_id: playerId,
    wallet_account: walletAccount,
    migrated_guest: migratedGuest,
    token,
    expires_at: expiresAt
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin");
    if (origin && origin !== GAME_ORIGIN) {
      return jsonResponse({ success: false, error: "Origin not allowed" }, 403);
    }

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": GAME_ORIGIN,
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
          "Vary": "Origin"
        }
      });
    }

    const url = new URL(request.url);
    try {
      if (url.pathname === "/health" && request.method === "GET") {
        return jsonResponse({ success: true, message: "Pandania API is online", auth: "webauth" });
      }

      if (url.pathname === "/api/auth/webauth" && request.method === "POST") {
        return await authenticateWebAuth(request, env);
      }

      if (url.pathname === "/api/auth/logout" && request.method === "POST") {
        const header = request.headers.get("Authorization") || "";
        const token = header.startsWith("Bearer ") ? header.slice(7) : "";
        if (/^[a-f0-9]{64}$/.test(token)) {
          await env.DB.prepare(
            "UPDATE wallet_sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL"
          ).bind(Math.floor(Date.now() / 1000), await sha256(token)).run();
        }
        return jsonResponse({ success: true });
      }

      if (url.pathname === "/api/player/save" && request.method === "POST") {
        const account = await authenticateSession(request, env);
        if (!account) return jsonResponse({ success: false, error: "WebAuth session expired. Please reconnect." }, 401);

        const contentLength = Number(request.headers.get("Content-Length") || 0);
        if (contentLength > MAX_SAVE_SIZE) return jsonResponse({ success: false, error: "Save data is too large." }, 413);

        const body = await request.json();
        if (!body || typeof body.save !== "object" || body.save === null || Array.isArray(body.save)) {
          return jsonResponse({ success: false, error: "A valid save object is required." }, 400);
        }
        const saveJson = JSON.stringify(body.save);
        if (saveJson.length > MAX_SAVE_SIZE) return jsonResponse({ success: false, error: "Save data is too large." }, 413);

        await env.DB.prepare(`
          INSERT INTO player_saves (player_id, save_json, updated_at)
          VALUES (?, ?, CURRENT_TIMESTAMP)
          ON CONFLICT(player_id) DO UPDATE SET
            save_json = excluded.save_json,
            updated_at = CURRENT_TIMESTAMP
        `).bind(account.player_id, saveJson).run();

        return jsonResponse({ success: true, message: "Game saved", player_id: account.player_id });
      }

      if (url.pathname === "/api/player/load" && request.method === "GET") {
        const account = await authenticateSession(request, env);
        if (!account) return jsonResponse({ success: false, error: "WebAuth session expired. Please reconnect." }, 401);

        const result = await env.DB.prepare(
          "SELECT save_json, updated_at FROM player_saves WHERE player_id = ?"
        ).bind(account.player_id).first();

        if (!result) {
          return jsonResponse({ success: true, player_id: account.player_id, save: null, message: "No saved game found" });
        }
        return jsonResponse({
          success: true,
          player_id: account.player_id,
          save: JSON.parse(result.save_json),
          updated_at: result.updated_at
        });
      }

      return jsonResponse({ success: false, error: "Route not found" }, 404);
    } catch (error) {
      console.error("Pandania API error:", error);
      return jsonResponse({ success: false, error: "Internal server error" }, 500);
    }
  }
};
