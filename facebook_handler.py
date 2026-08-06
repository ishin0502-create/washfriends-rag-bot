"""
facebook_handler.py
Wash Friends Vietnam — Facebook Messenger Webhook Handler

Facebook Graph API v18:
  GET  /webhook         — webhook verification (hub.challenge)
  POST /webhook        ℔ receive messages

Send API: https://graph.facebook.com/v18.0/me/messages
Docs: https://developers.facebook.com/docs/messenger-platform/webhooks
"""

import os
import hmac
import hashlib
import json
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

import httpx
from fastapi import Request, HTTPException, Query

from graphrag_engine import generate_response
from image_flow import process_channel_image

FB_PAGE_TOKEN    = os.environ.get("FB_PAGE_TOKEN", "")
FB_VERIFY_TOKEN  = os.environ.get("FB_VERIFY_TOKEN", "washfriends_vn_2024")
FB_APP_SECRET    = os.environ.get("FB_APP_SECRET", "")
FB_API_BASE      = "https://graph.facebook.com/v18.0"

# Dedup: track processed message IDs (last 5 min)
_processed_mids: dict[str, float] = {}
_DEDUP_TTL = 300


def _verify_fb_signature(body_bytes: bytes, sig_header: str) -> bool:
    """
    Verify Facebook X-Hub-Signature-256 header.
    Header format: sha256=<hex_signature>
    """
    if not FB_APP_SECRET:
        return True  # Dev mode

    if not sig_header.startswith("sha256="):
        return False

    expected = hmac.new(
        FB_APP_SECRET.encode(),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    received = sig_header[7:]  # Strip "sha256="
    return hmac.compare_digest(expected, received)


def _is_duplicate(mid: str) -> bool:
    now = time.time()
    expired = [k for k, ts in _processed_mids.items() if now - ts > _DEDUP_TTL]
    for k in expired:
        del _processed_mids[k]
    if mid in _processed_mids:
        return True
    _processed_mids[mid] = now
    return False


async def _send_fb_message(recipient_id: str, text: str) -> bool:
    """Send a text reply via Facebook Send API."""
    url = f"{FB_API_BASE}/me/messages"
    params = {"access_token": FB_PAGE_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text[:2000]},  # FB text limit
        "messaging_type": "RESPONSE",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, params=params, json=payload)
            data = r.json()
            if "error" in data:
                print(f"[FB SEND ERROR] {data['error']}")
                return False
            return True
        except Exception as e:
            print(f"[FB HTTP ERROR] {e}")
            return False


async def handle_fb_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
) -> str:
    """
    GET /webhook/facebook
    Facebook sends this once to verify the webhook URL.
    Must return hub.challenge as plain text.
    """
    if hub_mode == "subscribe" and hub_verify_token == FB_VERIFY_TOKEN:
        print("[FB] Webhook verified ✅")
        return hub_challenge
    raise HTTPException(status_code=403, detail="Verification token mismatch")


async def handle_fb_webhook(request: Request) -> dict:
    """
    POST /webhook/facebook
    Receives Messenger events (messages, postbacks, etc.)
    Returns {"status": "ok"} immediately.
    """
    body_bytes = await request.body()

    # 1. Verify signature
    sig_header = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_fb_signature(body_bytes, sig_header):
        raise HTTPException(status_code=403, detail="Invalid FB signature")

    try:
        payload = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 2. Only process page messages
    if payload.get("object") != "page":
        return {"status": "ignored"}

    # 3. Process each entry / each messaging event
    tasks = []
    for entry in payload.get("entry", []):
        for event in entry.get("messaging", []):

            # Text message
            if "message" in event and "text" in event["message"]:
                mid         = event["message"].get("mid", "")
                sender_id   = event["sender"]["id"]
                text        = event["message"]["text"].strip()

                if not text or _is_duplicate(mid):
                    continue

                tasks.append(_process_and_reply(sender_id, text))

            # Image / attachment message
            elif "message" in event and "attachments" in event["message"]:
                mid       = event["message"].get("mid", "")
                sender_id = event["sender"]["id"]
                caption   = event["message"].get("text", "").strip()

                if _is_duplicate(mid):
                    continue

                attachments = event["message"]["attachments"]
                for att in attachments:
                    if att.get("type") == "image":
                        image_url = att.get("payload", {}).get("url")
                        if image_url:
                            tasks.append(_process_image_and_reply(sender_id, image_url, caption))
                        break  # Process first image only

            # Postback (quick reply buttons)
            elif "postback" in event:
                sender_id = event["sender"]["id"]
                payload_str = event["postback"].get("payload", "")
                title       = event["postback"].get("title", payload_str)
                tasks.append(_process_and_reply(sender_id, title))

    # Run all reply tasks concurrently
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    return {"status": "ok"}


async def _process_and_reply(sender_id: str, text: str) -> None:
    """Generate GraphRAG response from text and send to user."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        reply = await loop.run_in_executor(pool, generate_response, text)
    await _send_fb_message(sender_id, reply)


async def _process_image_and_reply(sender_id: str, image_url: str, caption: str = "") -> None:
    """Stain photo → GraphRAG, or low-confidence → ask for care-label photo."""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        reply = await loop.run_in_executor(
            pool,
            process_channel_image,
            "facebook",
            sender_id,
            image_url,
            caption or "",
        )
    await _send_fb_message(sender_id, reply)
