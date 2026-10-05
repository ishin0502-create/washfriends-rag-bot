"""
zalo_token.py
Wash Friends Vietnam — Zalo OA Access Token

Shared Nhượng Quyền OA is also used for order notify (Cloud Run).
Zalo refresh_token is one-time-use — only HQ Cloud Run may refresh.

This service NEVER calls Zalo OAuth refresh. It only GETs a valid access
token from HQ (which refreshes if needed) and caches it for sends.
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
                    t.expires_at = $e,
                    t.oa_id = $oa,
                    t.updated_at = datetime()
                """,
                a=_access_token,
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
    raise RuntimeError(
        "Local Zalo OAuth refresh is disabled — HQ Cloud Run is the only writer"
    )


async def refresh_tokens(force: bool = False) -> str:
    """Reload access from HQ. Never calls Zalo OAuth (force is ignored)."""
    print("[ZALO TOKEN] Reloading access from HQ (local OAuth refresh disabled)")
    return await get_access_token(force_hq=True)


async def get_access_token(*, force_hq: bool = False) -> str:
    """Return a valid access token from HQ. Never refresh OAuth locally."""
    global _access_token, _refresh_token, _expires_at

    async with _lock:
        now = time.time()
        if (
            not force_hq
            and _access_token
            and _expires_at
            and now < (_expires_at - _REFRESH_MARGIN_SEC)
        ):
            return _access_token

        if _fetch_from_hq() and _access_token:
            try:
                _save_to_neo4j()
            except Exception:
                pass
            return _access_token

        _load_from_neo4j()
        _load_env_tokens()
        if _access_token:
            print("[ZALO TOKEN] HQ unavailable — using cached access (no local OAuth refresh)")
            return _access_token
        print("[ZALO TOKEN] No access token from HQ or cache")
        return ""


def is_token_error(error_code) -> bool:
    """Zalo API error codes that mean access token is invalid/expired.

    Do not treat -201 (invalid params) as a token error — that path used to
    force a local OAuth refresh and fight the shared HQ refresh token.
    """
    try:
        code = int(error_code)
    except (TypeError, ValueError):
        return False
    return code in (-124, -204, -216, -22)


async def token_refresh_loop(stop_event: Optional[asyncio.Event] = None) -> None:
    """Background loop: pull a fresh access token from HQ only."""
    try:
        await get_access_token()
    except Exception as e:
        print(f"[ZALO TOKEN] Initial get failed: {e}")

    while True:
        if stop_event and stop_event.is_set():
            return
        try:
            await get_access_token(force_hq=True)
        except Exception as e:
            print(f"[ZALO TOKEN] Periodic HQ pull error: {e}")
        await asyncio.sleep(60 * 60)
