"""
zalo_token.py
Wash Friends Vietnam — Zalo OA Access Token auto-refresh

Zalo OA OAuth v4:
  Access Token  ~25 hours
  Refresh Token ~3 months, one-time use (must persist the new refresh token)

Persistence: Neo4j (:ZaloToken {id:'oa'}) so Railway restarts keep the latest refresh token.
Fallback: Railway env vars ZALO_OA_ACCESS_TOKEN / ZALO_OA_REFRESH_TOKEN on first boot.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Optional

import httpx

from graphrag_engine import _get_driver

ZALO_APP_ID = os.environ.get("ZALO_APP_ID", "519523987326492768")
ZALO_APP_SECRET = os.environ.get("ZALO_APP_SECRET", "")
ZALO_TOKEN_URL = "https://oauth.zaloapp.com/v4/oa/access_token"

# In-memory cache
_access_token: str = os.environ.get("ZALO_OA_ACCESS_TOKEN", "")
_refresh_token: str = os.environ.get("ZALO_OA_REFRESH_TOKEN", "")
_expires_at: float = 0.0  # unix time; 0 = unknown → refresh soon if refresh_token exists
_lock = asyncio.Lock()
_REFRESH_MARGIN_SEC = 30 * 60  # refresh 30 min before expiry


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
                _access_token = row["a"]
            if row.get("r"):
                _refresh_token = row["r"]
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
                    t.updated_at = datetime()
                """,
                a=_access_token,
                r=_refresh_token,
                e=_expires_at,
            )
        print("[ZALO TOKEN] Saved tokens to Neo4j")
    except Exception as e:
        print(f"[ZALO TOKEN] Neo4j save FAILED (update Railway vars ASAP): {e}")
        print("[ZALO TOKEN] WARNING: refresh_token may be lost on restart if Neo4j save failed")


async def _call_refresh(refresh_token: str) -> dict:
    if not ZALO_APP_SECRET:
        raise RuntimeError("ZALO_APP_SECRET is empty — cannot refresh")
    if not ZALO_APP_ID:
        raise RuntimeError("ZALO_APP_ID is empty — cannot refresh")
    if not refresh_token:
        raise RuntimeError("refresh_token is empty — cannot refresh")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "secret_key": ZALO_APP_SECRET,
    }
    data = {
        "refresh_token": refresh_token,
        "app_id": ZALO_APP_ID,
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

        # Prefer Neo4j tokens (may be newer than env after previous refresh)
        _load_from_neo4j()

        if (
            not force
            and _access_token
            and _expires_at
            and now < (_expires_at - _REFRESH_MARGIN_SEC)
        ):
            return _access_token

        if not _refresh_token:
            if _access_token:
                print("[ZALO TOKEN] No refresh_token — using env access token only")
                return _access_token
            raise RuntimeError("No ZALO_OA_REFRESH_TOKEN / access token available")

        print("[ZALO TOKEN] Refreshing OA access token…")
        payload = await _call_refresh(_refresh_token)
        _access_token = payload["access_token"]
        # Zalo rotates refresh_token — MUST keep the new one
        new_refresh = payload.get("refresh_token") or _refresh_token
        _refresh_token = new_refresh
        try:
            expires_in = int(payload.get("expires_in") or 90000)
        except (TypeError, ValueError):
            expires_in = 90000
        _expires_at = time.time() + expires_in
        _save_to_neo4j()
        print(f"[ZALO TOKEN] Refresh OK — expires_in={expires_in}s")
        return _access_token


async def get_access_token() -> str:
    """Return a valid access token, refreshing if needed."""
    global _access_token
    if not _access_token and not _refresh_token:
        _load_from_neo4j()
        if not _access_token:
            _access_token = os.environ.get("ZALO_OA_ACCESS_TOKEN", "")
        if not _refresh_token:
            _refresh_token = os.environ.get("ZALO_OA_REFRESH_TOKEN", "")

    if not _access_token and _refresh_token:
        return await refresh_tokens(force=True)

    now = time.time()
    if _expires_at and now >= (_expires_at - _REFRESH_MARGIN_SEC):
        return await refresh_tokens(force=False)

    # expires unknown but we have refresh → proactively refresh once after boot
    if _refresh_token and not _expires_at:
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
    # Common: -124 expired/invalid token; -216; -201
    return code in (-124, -216, -201, -22)


async def token_refresh_loop(stop_event: Optional[asyncio.Event] = None) -> None:
    """Background loop: refresh ~hourly so token never goes stale."""
    # Initial load
    try:
        await get_access_token()
    except Exception as e:
        print(f"[ZALO TOKEN] Initial get failed: {e}")

    while True:
        if stop_event and stop_event.is_set():
            return
        try:
            await refresh_tokens(force=False)
        except Exception as e:
            print(f"[ZALO TOKEN] Periodic refresh error: {e}")
        await asyncio.sleep(60 * 60)  # check every hour
