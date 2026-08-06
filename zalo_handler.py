"""
zalo_handler.py
Wash Friends Vietnam — Zalo OA OpenAPI Webhook Handler

Webhook path (do not change — registered in Zalo OA console):
  POST /webhook/zalo

Zalo OA OpenAPI v3:
  POST /oa/message/cs  — send reply to user
  GET  /oa/getoa       — verify OA info
"""

import os
import hmac
import hashlib
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from typing import Optional

import httpx
from fastapi import Request, HTTPException

from graphrag_engine import generate_response
from image_flow import process_channel_image
from zalo_token import get_access_token, is_token_error, refresh_tokens, _app_secret, _app_id

ZALO_API_BASE   = "https://openapi.zalo.me/v3.0"

_processed_events: dict[str, float] = {}
_DEDUP_TTL = 300
_executor = ThreadPoolExecutor(max_workers=4)


def _verify_zalo_signature(body_bytes: bytes, mac_header: str) -> bool:
    """
    Verify Zalo webhook HMAC-SHA256 signature.
    Accepts headers like: mac=<hex> or raw hex.
    """
    secret = _app_secret()
    if not secret:
        print("[ZALO SIG] ZALO_APP_SECRET not set — skipping verification")
        return True

    expected = hmac.new(
        secret.encode(),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    received = (mac_header or "").replace("mac=", "").replace("sha256=", "").strip()
    if not received:
        return False
    return hmac.compare_digest(expected, received)


def _is_duplicate(event_id: str) -> bool:
    now = time.time()
    expired = [k for k, ts in _processed_events.items() if now - ts > _DEDUP_TTL]
    for k in expired:
        del _processed_events[k]

    if event_id in _processed_events:
        return True
    _processed_events[event_id] = now
    return False


async def _send_zalo_reply(user_id: str, text: str) -> bool:
    """Send a text reply to a Zalo user via OA API (auto-refreshes token on expiry)."""
    token = await get_access_token()
    if not token:
        print("[ZALO SEND ERROR] access token is empty — set ZALO_OA_ACCESS_TOKEN / REFRESH_TOKEN")
        return False

    url = f"{ZALO_API_BASE}/oa/message/cs"
    payload = {
        "recipient": {"user_id": user_id},
        "message": {"text": text[:2000]},
    }

    async with httpx.AsyncClient(timeout=15) as client:
        for attempt in range(2):
            headers = {
                "access_token": token,
                "Content-Type": "application/json",
            }
            try:
                r = await client.post(url, headers=headers, json=payload)
                data = r.json()
                err = data.get("error")
                if err and err != 0:
                    if attempt == 0 and is_token_error(err):
                        print(f"[ZALO SEND] token error {err} — refreshing and retrying")
                        token = await refresh_tokens(force=True)
                        continue
                    print(f"[ZALO SEND ERROR] code={err} msg={data.get('message')}")
                    return False
                print(f"[ZALO SEND OK] user={user_id[:8]}… chars={len(text)}")
                return True
            except Exception as e:
                print(f"[ZALO HTTP ERROR] {e}")
                return False
    return False


async def _process_zalo_event(event_name: str, user_id: str, text: str, image_url: Optional[str]) -> None:
    """Heavy AI work — runs after webhook ACK."""
    loop = asyncio.get_event_loop()
    try:
        if event_name == "user_send_image":
            if not image_url:
                await _send_zalo_reply(
                    user_id,
                    "Anh khong tai duoc. Vui long gui lai anh hoac mo ta vet ban bang chu.",
                )
                return

            reply_text = await loop.run_in_executor(
                _executor,
                process_channel_image,
                "zalo",
                user_id,
                image_url,
                text or "",
            )
        else:
            if not text:
                return
            reply_text = await loop.run_in_executor(_executor, generate_response, text)

        await _send_zalo_reply(user_id, reply_text)
    except Exception as exc:
        print(f"[ZALO HANDLER ERROR] {type(exc).__name__}: {exc}")
        try:
            await _send_zalo_reply(
                user_id,
                "Xin loi, he thong tam thoi gap su co. Vui long thu lai sau it phut.",
            )
        except Exception:
            pass


async def handle_zalo_webhook(request: Request) -> dict:
    """
    POST /webhook/zalo — ACK quickly, process GraphRAG in background.
    """
    body_bytes = await request.body()

    # Signature: accept multiple header names Zalo may send
    mac_header = (
        request.headers.get("mac")
        or request.headers.get("X-ZaloOA-Signature")
        or request.headers.get("x-zalooa-signature")
        or ""
    )
    if not _verify_zalo_signature(body_bytes, mac_header):
        # Temporary: allow through so OA keeps delivering while secret is corrected.
        # Still logs loudly — restore hard 403 after ZALO_APP_SECRET is fixed.
        print(f"[ZALO SIG WARNING] mac_header={mac_header!r} - allowing through")

    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_name = payload.get("event_name", "")
    app_id = payload.get("app_id", "")
    timestamp = payload.get("timestamp", "")
    event_id = f"{app_id}_{timestamp}"

    if event_name not in ("user_send_text", "user_send_image"):
        return {"status": "ignored", "event": event_name}

    if _is_duplicate(event_id):
        return {"status": "duplicate"}

    user_id = payload.get("sender", {}).get("id", "")
    message = payload.get("message", {})
    text = (message.get("text") or "").strip()

    if not user_id:
        return {"status": "empty_message"}

    image_url = None
    if event_name == "user_send_image":
        attachments = message.get("attachments") or []
        if attachments:
            image_url = attachments[0].get("payload", {}).get("url")

    # ACK immediately — Zalo times out slow handlers
    asyncio.create_task(_process_zalo_event(event_name, user_id, text, image_url))
    return {"status": "ok"}


async def get_zalo_oa_info() -> dict:
    """Health check — verify OA token is valid (uses auto-refresh)."""
    diag = {
        "app_id_len": len(_app_id()),
        "secret_len": len(_app_secret()),
    }
    try:
        token = await get_access_token()
        diag["access_token_len"] = len(token or "")
    except Exception as e:
        return {"error": f"token: {e}", "diag": diag}

    url = f"{ZALO_API_BASE}/oa/getoa"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(url, headers={"access_token": token})
            data = r.json()
            err = data.get("error")
            if err and err != 0:
                print(f"[ZALO INFO] error={err} msg={data.get('message')} — trying refresh")
                try:
                    token = await refresh_tokens(force=True)
                    diag["refresh"] = "ok"
                    diag["access_token_len"] = len(token or "")
                    r = await client.get(url, headers={"access_token": token})
                    data = r.json()
                except Exception as refresh_err:
                    diag["refresh"] = f"fail: {refresh_err}"
                    return {
                        "error": err,
                        "message": data.get("message"),
                        "diag": diag,
                        "hint": "Refresh failed. Check ZALO_OA_REFRESH_TOKEN + ZALO_APP_SECRET.",
                    }
            if isinstance(data, dict):
                data = {**data, "diag": diag}
            return data
        except Exception as e:
            return {"error": str(e), "diag": diag}
