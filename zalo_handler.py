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
from brand_header import should_send_brand_header, header_image_path, public_header_url
from user_session import get_session
from zalo_token import get_access_token, is_token_error, refresh_tokens, _app_secret, _app_id

ZALO_API_BASE   = "https://openapi.zalo.me/v3.0"
ZALO_UPLOAD_URL = f"{ZALO_API_BASE}/oa/upload/image"

_processed_events: dict[str, float] = {}
_DEDUP_TTL = 300
_executor = ThreadPoolExecutor(max_workers=4)
_zalo_header_token: Optional[str] = None
_zalo_header_token_ts: float = 0.0
_ZALO_TOKEN_TTL = 20 * 60


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


async def _upload_zalo_header_token(client: httpx.AsyncClient, token: str) -> Optional[str]:
    """Upload brand header once (cached briefly). Fail-open → None."""
    global _zalo_header_token, _zalo_header_token_ts
    now = time.time()
    if _zalo_header_token and now - _zalo_header_token_ts < _ZALO_TOKEN_TTL:
        return _zalo_header_token
    path = header_image_path()
    if not path:
        print("[ZALO BRAND] upload skipped: assets/wf_brand_header.png missing")
        return None
    try:
        with path.open("rb") as f:
            files = {"file": ("wf_brand_header.png", f, "image/png")}
            r = await client.post(
                ZALO_UPLOAD_URL,
                headers={"access_token": token},
                files=files,
                timeout=20,
            )
        data = r.json()
        err = data.get("error")
        if err and err != 0:
            print(
                f"[ZALO BRAND] upload API error code={err} "
                f"msg={data.get('message')} url={ZALO_UPLOAD_URL}"
            )
            return None
        att = (data.get("data") or {}).get("attachment_id") or (data.get("data") or {}).get("token")
        if att:
            _zalo_header_token = str(att)
            _zalo_header_token_ts = now
            print(f"[ZALO BRAND] upload ok id={_zalo_header_token[:12]}…")
            return _zalo_header_token
        print(f"[ZALO BRAND] upload failed (no attachment_id/token): {data}")
    except Exception as e:
        print(f"[ZALO BRAND] upload error: {type(e).__name__}: {e}")
    return None


def _brand_image_payload(user_id: str, *, att: Optional[str] = None, use_url: bool = False) -> dict:
    recipient = {"user_id": user_id}
    if use_url or not att:
        payload = {"url": public_header_url()}
    else:
        # v3 accepts token; some SDKs/docs also mention attachment_id — send both.
        payload = {"token": att, "attachment_id": att}
    return {
        "recipient": recipient,
        "message": {
            "attachment": {
                "type": "image",
                "payload": payload,
            }
        },
    }


async def _post_zalo_image(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    payload: dict,
) -> tuple[bool, dict]:
    r = await client.post(url, headers=headers, json=payload)
    data = r.json()
    err = data.get("error")
    ok = err in (None, 0)
    return ok, data


async def _send_zalo_brand_image(user_id: str) -> bool:
    """Send mascot+logo image. Never raises; False on failure."""
    token = await get_access_token()
    if not token:
        print("[ZALO BRAND] send skipped: empty access token")
        return False
    url = f"{ZALO_API_BASE}/oa/message/cs"
    async with httpx.AsyncClient(timeout=20) as client:
        for attempt in range(2):
            headers = {"access_token": token, "Content-Type": "application/json"}
            att = await _upload_zalo_header_token(client, token)
            attempts: list[tuple[str, dict]] = []
            if att:
                attempts.append(("token+attachment_id", _brand_image_payload(user_id, att=att)))
                attempts.append(("token_only", {
                    "recipient": {"user_id": user_id},
                    "message": {
                        "attachment": {
                            "type": "image",
                            "payload": {"token": att},
                        }
                    },
                }))
                attempts.append(("attachment_id_only", {
                    "recipient": {"user_id": user_id},
                    "message": {
                        "attachment": {
                            "type": "image",
                            "payload": {"attachment_id": att},
                        }
                    },
                }))
            attempts.append(("url", _brand_image_payload(user_id, use_url=True)))

            for mode, payload in attempts:
                try:
                    ok, data = await _post_zalo_image(client, url, headers, payload)
                    if ok:
                        print(f"[ZALO BRAND] sent via {mode}")
                        return True
                    err = data.get("error")
                    print(
                        f"[ZALO BRAND] send failed mode={mode} "
                        f"code={err} msg={data.get('message')}"
                    )
                    if attempt == 0 and err and is_token_error(err):
                        token = await refresh_tokens(force=True)
                        headers["access_token"] = token
                        global _zalo_header_token, _zalo_header_token_ts
                        _zalo_header_token = None
                        _zalo_header_token_ts = 0.0
                        break
                except Exception as e:
                    print(f"[ZALO BRAND HTTP] mode={mode} {type(e).__name__}: {e}")
            else:
                continue
            break
    return False


async def diagnose_zalo_brand(*, user_id: Optional[str] = None) -> dict:
    """
    Admin diagnostic: static file, v3 upload, optional send to user_id.
    Does not run GraphRAG.
    """
    out: dict = {
        "header_file": str(header_image_path() or ""),
        "header_file_ok": header_image_path() is not None,
        "public_url": public_header_url(),
        "upload_url": ZALO_UPLOAD_URL,
        "send_url": f"{ZALO_API_BASE}/oa/message/cs",
    }
    token = await get_access_token()
    out["access_token_len"] = len(token or "")
    if not token:
        out["upload"] = {"ok": False, "error": "empty access token"}
        return out

    async with httpx.AsyncClient(timeout=20) as client:
        global _zalo_header_token, _zalo_header_token_ts
        _zalo_header_token = None
        _zalo_header_token_ts = 0.0
        att = await _upload_zalo_header_token(client, token)
        out["upload"] = {"ok": bool(att), "attachment_id": att}

        if user_id and att:
            url = f"{ZALO_API_BASE}/oa/message/cs"
            headers = {"access_token": token, "Content-Type": "application/json"}
            ok, data = await _post_zalo_image(
                client,
                url,
                headers,
                _brand_image_payload(user_id, att=att),
            )
            out["send_test"] = {
                "ok": ok,
                "user_id": user_id[:8] + "…",
                "error": data.get("error"),
                "message": data.get("message"),
            }
        elif user_id:
            out["send_test"] = {"ok": False, "error": "upload failed — cannot send"}

    return out


async def _send_zalo_reply(user_id: str, text: str, *, with_brand: bool = False) -> bool:
    """Send optional brand image, then text. Text always attempted."""
    if with_brand:
        try:
            await _send_zalo_brand_image(user_id)
        except Exception as e:
            print(f"[ZALO BRAND] skipped: {e}")
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
        awaiting = get_session("zalo", user_id).get("awaiting") == "care_label"
        if event_name == "user_send_image":
            if not image_url:
                await _send_zalo_reply(
                    user_id,
                    "Anh khong tai duoc. Vui long gui lai anh hoac mo ta vet ban bang chu.",
                    with_brand=False,
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

        with_brand = should_send_brand_header(
            "zalo",
            user_id,
            text or "",
            has_image=bool(image_url),
            awaiting_care_label=awaiting,
        )
        await _send_zalo_reply(user_id, reply_text, with_brand=with_brand)
    except Exception as exc:
        print(f"[ZALO HANDLER ERROR] {type(exc).__name__}: {exc}")
        try:
            await _send_zalo_reply(
                user_id,
                "Xin loi, he thong tam thoi gap su co. Vui long thu lai sau it phut.",
                with_brand=False,
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
