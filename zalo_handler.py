"""
zalo_handler.py
Wash Friends Vietnam — Zalo OA OpenAPI Webhook Handler

Zalo OA OpenAPI v3:
  POST /oa/message/cs  — send reply to user
  GET  /oa/getoa       — verify OA info

Webhook events received (POST /webhook/zalo):
  - user_send_text   → extract message → graphrag_engine → reply
  - user_send_image  → Claude Vision → graphrag_engine → reply

Docs: https://developers.zalo.me/docs/official-account/messages/send-message-to-follower
"""

import os
import hmac
import hashlib
import json
import time
from typing import Optional

import httpx
from fastapi import Request, HTTPException

from graphrag_engine import generate_response, generate_response_from_entities
from image_analyzer import analyze_stain_image, build_image_context_prefix

ZALO_OA_TOKEN   = os.environ.get("ZALO_OA_ACCESS_TOKEN", "")
ZALO_APP_SECRET = os.environ.get("ZALO_APP_SECRET", "")
ZALO_API_BASE   = "https://openapi.zalo.me/v3.0"

# Simple in-memory dedup: track processed event IDs (last 5 min)
_processed_events: dict[str, float] = {}
_DEDUP_TTL = 300  # seconds


def _verify_zalo_signature(body_bytes: bytes, mac_header: str) -> bool:
    """
    Verify Zalo webhook HMAC-SHA256 signature.
    Header format: mac=<hex_signature>
    """
    if not ZALO_APP_SECRET:
        return True  # Skip verification in dev mode if secret not set

    expected = hmac.new(
        ZALO_APP_SECRET.encode(),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    received = mac_header.replace("mac=", "").strip()
    return hmac.compare_digest(expected, received)


def _is_duplicate(event_id: str) -> bool:
    """Dedup check — Zalo may send the same webhook twice."""
    now = time.time()
    # Expire old entries
    expired = [k for k, ts in _processed_events.items() if now - ts > _DEDUP_TTL]
    for k in expired:
        del _processed_events[k]

    if event_id in _processed_events:
        return True
    _processed_events[event_id] = now
    return False


async def _send_zalo_reply(user_id: str, text: str) -> bool:
    """Send a text reply to a Zalo user via OA API."""
    url = f"{ZALO_API_BASE}/oa/message/cs"
    headers = {
        "access_token": ZALO_OA_TOKEN,
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"user_id": user_id},
        "message": {"text": text[:2000]},  # Zalo text limit
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, headers=headers, json=payload)
            data = r.json()
            if data.get("error") and data["error"] != 0:
                print(f"[ZALO SEND ERROR] code={data.get('error')} msg={data.get('message')}")
                return False
            return True
        except Exception as e:
            print(f"[ZALO HTTP ERROR] {e}")
            return False


async def handle_zalo_webhook(request: Request) -> dict:
    """
    Main Zalo webhook handler.
    Called by FastAPI route: POST /webhook/zalo

    Zalo sends JSON body with event_name, user_id_by_app, message.text, etc.
    Returns {"status": "ok"} immediately (Zalo expects fast ACK).
    """
    body_bytes = await request.body()

    # 1. Verify signature
    mac_header = request.headers.get("mac", "")
    if not _verify_zalo_signature(body_bytes, mac_header):
        raise HTTPException(status_code=403, detail="Invalid Zalo signature")

    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 2. Extract event info
    event_name = payload.get("event_name", "")
    app_id     = payload.get("app_id", "")
    timestamp  = payload.get("timestamp", "")
    event_id   = f"{app_id}_{timestamp}"

    # Only handle text and image messages
    if event_name not in ("user_send_text", "user_send_image"):
        return {"status": "ignored", "event": event_name}

    # 3. Dedup
    if _is_duplicate(event_id):
        return {"status": "duplicate"}

    # 4. Extract user info + message
    user_id  = payload.get("sender", {}).get("id", "")
    message  = payload.get("message", {})
    text     = message.get("text", "").strip()

    if not user_id:
        return {"status": "empty_message"}

    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_event_loop()

    # 5. Route: image vs text — wrap in try/except so Zalo always gets 200 OK
    try:
        if event_name == "user_send_image":
            # Zalo image message: attachments[0].payload.url
            attachments = message.get("attachments", [])
            image_url   = None
            if attachments:
                image_url = attachments[0].get("payload", {}).get("url")

            if not image_url:
                await _send_zalo_reply(user_id, "📸 Ảnh không tải được. Vui lòng gửi lại ảnh hoặc mô tả vết bẩn bằng chữ.")
                return {"status": "image_url_missing"}

            def _run_image_pipeline():
                entities = analyze_stain_image(image_url=image_url, user_caption=text)
                prefix   = build_image_context_prefix(entities)
                response = generate_response_from_entities(entities, user_caption=text, prefix=prefix)
                return response

            with ThreadPoolExecutor() as pool:
                reply_text = await loop.run_in_executor(pool, _run_image_pipeline)

        else:
            # Text message
            if not text:
                return {"status": "empty_message"}

            with ThreadPoolExecutor() as pool:
                reply_text = await loop.run_in_executor(pool, generate_response, text)

        # 6. Send reply
        await _send_zalo_reply(user_id, reply_text)

    except Exception as exc:
        # Log the error but always return 200 so Zalo keeps the webhook registered
        print(f"[ZALO HANDLER ERROR] {type(exc).__name__}: {exc}")

    return {"status": "ok"}


async def get_zalo_oa_info() -> dict:
    """Health check — verify OA token is valid."""
    url = f"{ZALO_API_BASE}/oa/getoa"
    headers = {"access_token": ZALO_OA_TOKEN}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(url, headers=headers)
            return r.json()
        except Exception as e:
            return {"error": str(e)}
