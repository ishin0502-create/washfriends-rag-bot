"""
zalo_token.py
Wash Friends Vietnam — Zalo OA Access Token

Shared Nhượng Quyền OA is also used for order notify (Cloud Run).
Zalo refresh_token is one-time-use — only ONE writer may refresh.

Source of truth: WashFriends HQ Cloud SQL via
  GET /api/v1/internal/education-bot/zalo-oa-token
Fallback: Neo4j (:ZaloToken {id:'oa'}) + env, with PUT back to HQ after refresh.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
import urllib.error
import urllib.request
from typing import Optional

import httpx

from graphrag_engine import _get_driver

ZALO_TOKEN_URL = "https://oauth.zaloapp.com/v4/oa/access_token"
OUTREACH_OA_ID = (
    os.environ.get("OUTREACH_ZALO_OA_ID")
    or os.environ.get("ZALO_OA_ID")
    or "455360617365153111"
).strip()

# In-memory cache
_access_token: str = ""
_refresh_token: str = ""
_expires_at: float = 0.0  # unix time; 0 = unknown
_lock = asyncio.Lock()
_REFRESH_MARGIN_SEC = 30 * 60  # refresh 30 min before expiry
_HQ_CACHE_MARGIN_SEC = 5 * 60


def _clean_token(value: Optional[str]) -> str:
    """Strip whitespace/newlines — Railway paste often adds trailing \\n."""
    if not value:
        return ""
    return value.strip().replace("\r", "").replace("\n", "")


def _app_id() -> str:
    return _clean_token(os.environ.get("ZALO_APP_ID", "519523987326492768"))


def _app_secret() -> str:
    return _clean_token(os.environ.get("ZALO_APP_SECRET", ""))


def _hq_base() -> str:
    return (
        os.environ.get("WF_HQ_API_BASE")
        or os.environ.get("WASHFRIENDS_API_BASE")
        or ""
    ).strip().rstrip("/")


def _hq_secret() -> str:
    return (
        os.environ.get("EDUCATION_BOT_INTERNAL_SECRET")
        or os.environ.get("INTERNAL_WEBHOOK_SECRET")
        or ""
    ).strip()


def _load_env_tokens() -> None:
    global _access_token, _refresh_token
    if not _access_token:
        _access_token = _clean_token(os.environ.get("ZALO_OA_ACCESS_TOKEN", ""))
    if not _refresh_token:
        _refresh_token = _clean_token(os.environ.get("ZALO_OA_REFRESH_TOKEN", ""))


def _load_from_neo4j() -> None:
    """Load latest tokens from Neo4j if present."""
    global _access_token, _refresh_token, _expires_at
    try:
        driver = _get_driver()
        with driver.session() as session:
            row = session.run(
                "MATCH (t:ZaloToken {id: 'oa'}) "
                "RETURN t.access_token AS a, t.refresh_token AS r, t.expires_at AS e"
            ).single()
            if not row:
                return
            if row.get("a"):
                _access_token = _clean_token(row["a"])
            if row.get("r"):
                _refresh_token = _clean_token(row["r"])
            if row.get("e"):
                _expires_at = float(row["e"])
            print("[ZALO TOKEN] Loaded tokens from Neo4j")
    except Exception as e:
        print(f"[ZALO TOKEN] Neo4j load skipped: {e}")


def _save_to_neo4j() -> None:
    """Persist rotated tokens — refresh_token must not be lost."""
    try:
        driver = _get_driver()
        with driver.session() as session:
            session.run(
                """
                MERGE (t:ZaloToken {id: 'oa'})
                SET t.access_token = $a,
                    t.refresh_token = $r,
                    t.expires_at = $e,
                    t.oa_id = $oa,
                    t.updated_at = datetime()
                """,
                a=_access_token,
                r=_refresh_token,
                e=_expires_at,
                oa=OUTREACH_OA_ID,
            )
        print("[ZALO TOKEN] Saved tokens to Neo4j")
    except Exception as e:
        print(f"[ZALO TOKEN] Neo4j save FAILED (update Railway vars ASAP): {e}")
        print("[ZALO TOKEN] WARNING: refresh_token may be lost on restart if Neo4j save failed")


def _fetch_from_hq() -> bool:
    """Pull valid access token from HQ Cloud SQL. Returns True on success."""
    global _access_token, _expires_at
    base = _hq_base()
    secret = _hq_secret()
    if not base or not secret:
        return False
    url = f"{base}/api/v1/internal/education-bot/zalo-oa-token?oa_id={OUTREACH_OA_ID}"
    req = urllib.request.Request(
        url,
        headers={
            "X-Internal-Secret": secret,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace") or "{}")
    except Exception as e:
        print(f"[ZALO TOKEN] HQ fetch failed: {e}")
        return False
    at = _clean_token(data.get("access_token"))
    if not at:
        print("[ZALO TOKEN] HQ fetch empty access_token")
        return False
    _access_token = at
    try:
        exp = data.get("expires_at")
        _expires_at = float(exp) if exp else 0.0
    except (TypeError, ValueError):
        _expires_at = 0.0
    print("[ZALO TOKEN] Loaded access token from HQ")
    return True


def _push_to_hq(expires_in: int) -> None:
    """After local refresh, sync rotated tokens back to Cloud SQL."""
    base = _hq_base()
    secret = _hq_secret()
    if not base or not secret:
        print("[ZALO TOKEN] HQ push skipped — WF_HQ_API_BASE/secret missing")
        return
    url = f"{base}/api/v1/internal/education-bot/zalo-oa-token"
    payload = {
        "oa_id": OUTREACH_OA_ID,
        "access_token": _access_token,
        "refresh_token": _refresh_token,
        "expires_in": int(expires_in),
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "X-Internal-Secret": secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"[ZALO TOKEN] HQ push OK ({getattr(resp, 'status', '?')})")
    except Exception as e:
        print(f"[ZALO TOKEN] HQ push FAILED: {e}")


async def _call_refresh(refresh_token: str) -> dict:
    secret = _app_secret()
    app_id = _app_id()
    if not secret:
        raise RuntimeError("ZALO_APP_SECRET is empty — cannot refresh")
    if not app_id:
        raise RuntimeError("ZALO_APP_ID is empty — cannot refresh")
    if not refresh_token:
        raise RuntimeError("refresh_token is empty — cannot refresh")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "secret_key": secret,
    }
    data = {
        "refresh_token": refresh_token,
        "app_id": app_id,
        "grant_type": "refresh_token",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(ZALO_TOKEN_URL, headers=headers, data=data)
        payload = r.json()
    if not payload.get("access_token"):
        raise RuntimeError(f"Zalo refresh failed: {payload}")
    return payload


async def refresh_tokens(force: bool = False) -> str:
    """
    Refresh OA access token if expired (or force=True).
    Returns a usable access_token.
    Prefer HQ as SoT — only refresh locally as fallback.
    """
    global _access_token, _refresh_token, _expires_at

    async with _lock:
        now = time.time()
        if (
            not force
            and _access_token
            and _expires_at
            and now < (_expires_at - _REFRESH_MARGIN_SEC)
        ):
            return _access_token

        # Prefer HQ (Cloud SQL) — avoids fighting Cloud Run order-notify refresh
        if not force and _fetch_from_hq():
            if _access_token and (
                not _expires_at or now < (_expires_at - _HQ_CACHE_MARGIN_SEC)
            ):
                _save_to_neo4j()
                return _access_token

        _load_from_neo4j()
        _load_env_tokens()

        if (
            not force
            and _access_token
            and _expires_at
            and now < (_expires_at - _REFRESH_MARGIN_SEC)
        ):
            return _access_token

        if not _refresh_token:
            if _access_token:
                print("[ZALO TOKEN] No refresh_token — using existing access token only")
                return _access_token
            raise RuntimeError("No ZALO_OA_REFRESH_TOKEN / access token available")

        print("[ZALO TOKEN] Refreshing OA access token (local fallback)…")
        payload = await _call_refresh(_refresh_token)
        _access_token = _clean_token(payload["access_token"])
        new_refresh = payload.get("refresh_token") or _refresh_token
        _refresh_token = _clean_token(new_refresh)
        try:
            expires_in = int(payload.get("expires_in") or 90000)
        except (TypeError, ValueError):
            expires_in = 90000
        _expires_at = time.time() + expires_in
        _save_to_neo4j()
        _push_to_hq(expires_in)
        print(f"[ZALO TOKEN] Refresh OK — expires_in={expires_in}s")
        return _access_token


async def get_access_token() -> str:
    """Return a valid access token. HQ first; never force-refresh on bare boot."""
    global _access_token, _refresh_token, _expires_at

    # Always hydrate Neo4j expires_at before deciding to refresh
    _load_from_neo4j()
    _load_env_tokens()

    now = time.time()
    if _access_token and _expires_at and now < (_expires_at - _REFRESH_MARGIN_SEC):
        return _access_token

    # HQ is SoT for the shared OA (order notify + education)
    if _fetch_from_hq():
        if _access_token and (
            not _expires_at or now < (_expires_at - _HQ_CACHE_MARGIN_SEC)
        ):
            try:
                _save_to_neo4j()
            except Exception:
                pass
            return _access_token

    if not _access_token and _refresh_token:
        return await refresh_tokens(force=True)

    if _expires_at and now >= (_expires_at - _REFRESH_MARGIN_SEC):
        return await refresh_tokens(force=False)

    # expires unknown: try HQ/local soft refresh, but do NOT burn refresh on every boot
    if _refresh_token and not _expires_at:
        if _fetch_from_hq() and _access_token:
            return _access_token
        try:
            return await refresh_tokens(force=True)
        except Exception as e:
            print(f"[ZALO TOKEN] Boot refresh failed, using existing access token: {e}")
            return _access_token

    return _access_token


def is_token_error(error_code) -> bool:
    """Zalo API error codes that usually mean access token is invalid/expired."""
    try:
        code = int(error_code)
    except (TypeError, ValueError):
        return False
    return code in (-124, -204, -216, -201, -22)


async def token_refresh_loop(stop_event: Optional[asyncio.Event] = None) -> None:
    """Background loop: prefer HQ pull; local refresh only near expiry."""
    try:
        await get_access_token()
    except Exception as e:
        print(f"[ZALO TOKEN] Initial get failed: {e}")

    while True:
        if stop_event and stop_event.is_set():
            return
        try:
            # Soft path: HQ first inside refresh_tokens(force=False)
            await refresh_tokens(force=False)
        except Exception as e:
            print(f"[ZALO TOKEN] Periodic refresh error: {e}")
        await asyncio.sleep(60 * 60)
