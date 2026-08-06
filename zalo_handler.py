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
from pathlib import Path

from typing import Optional

import httpx
from fastapi import Request, HTTPException

from graphrag_engine import generate_response
from image_flow import process_channel_image
from brand_header import (
    should_send_brand_header,
    confirm_brand_header_sent,
    clear_brand_header,
    clear_all_brand_headers,
    header_image_path,
    public_header_url,
    _HEADER_ASSET_VER,
)
from user_session import get_session
from zalo_token import get_access_token, is_token_error, refresh_tokens, _app_secret, _app_id

ZALO_API_BASE   = "https://openapi.zalo.me/v3.0"
ZALO_UPLOAD_URLS = [
    ("v2", "https://openapi.zalo.me/v2.0/oa/upload/image"),
    ("v3", f"{ZALO_API_BASE}/oa/upload/image"),
]

_processed_events: dict[str, float] = {}
_DEDUP_TTL = 300
_executor = ThreadPoolExecutor(max_workers=4)
_zalo_header_token: Optional[str] = None
_zalo_header_token_ts: float = 0.0
_zalo_header_token_ver: Optional[str] = None
_ZALO_TOKEN_TTL = 5 * 60  # short — asset changes must re-upload quickly
_last_zalo_user_id: Optional[str] = None


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


async def _upload_zalo_image_attempt(
    client: httpx.AsyncClient,
    token: str,
    *,
    upload_url: str,
    path: Optional[Path] = None,
    image_url: Optional[str] = None,
    auth: str = "header",
) -> dict:
    """Single upload attempt; returns raw Zalo JSON + parsed attachment id."""
    headers: dict = {}
    params: dict = {}
    if auth == "header":
        headers["access_token"] = token
    else:
        params["access_token"] = token

    try:
        if path:
            with path.open("rb") as f:
                files = {"file": (path.name, f, "image/png")}
                r = await client.post(
                    upload_url,
                    headers=headers,
                    params=params,
                    files=files,
                    timeout=20,
                )
        elif image_url:
            r = await client.post(
                upload_url,
                headers=headers,
                params=params,
                data={"image_url": image_url},
                timeout=20,
            )
        else:
            return {"ok": False, "error": "no path or image_url"}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    try:
        data = r.json()
    except Exception as e:
        return {"ok": False, "http_status": r.status_code, "error": f"json: {e}", "body": r.text[:500]}

    err = data.get("error")
    payload = data.get("data") or {}
    att = payload.get("attachment_id") or payload.get("token")
    return {
        "ok": bool(att) and err in (None, 0),
        "error_code": err,
        "message": data.get("message"),
        "attachment_id": att,
        "raw": data,
        "http_status": r.status_code,
        "upload_url": upload_url,
    }


def _upload_attempt_specs(path: Optional[Path]) -> list[tuple[str, dict]]:
    specs: list[tuple[str, dict]] = []
    for api_ver, upload_url in ZALO_UPLOAD_URLS:
        if path:
            specs.append((f"{api_ver}/file+header", {"upload_url": upload_url, "path": path, "auth": "header"}))
            specs.append((f"{api_ver}/file+query", {"upload_url": upload_url, "path": path, "auth": "query"}))
        pub = public_header_url()
        specs.append((f"{api_ver}/image_url+header", {"upload_url": upload_url, "image_url": pub, "auth": "header"}))
        specs.append((f"{api_ver}/image_url+query", {"upload_url": upload_url, "image_url": pub, "auth": "query"}))
    return specs


async def _upload_zalo_header_token(client: httpx.AsyncClient, token: str) -> Optional[str]:
    """Upload brand header once (cached briefly). Fail-open → None."""
    global _zalo_header_token, _zalo_header_token_ts, _zalo_header_token_ver
    now = time.time()
    if (
        _zalo_header_token
        and _zalo_header_token_ver == _HEADER_ASSET_VER
        and now - _zalo_header_token_ts < _ZALO_TOKEN_TTL
    ):
        return _zalo_header_token
    path = header_image_path()
    if not path:
        print(f"[ZALO BRAND] upload skipped: {_HEADER_ASSET_VER} asset missing")
        return None

    attempts = _upload_attempt_specs(path)
    for mode, kwargs in attempts:
        result = await _upload_zalo_image_attempt(client, token, **kwargs)
        att = result.get("attachment_id")
        if att:
            _zalo_header_token = str(att)
            _zalo_header_token_ts = now
            _zalo_header_token_ver = _HEADER_ASSET_VER
            print(f"[ZALO BRAND] upload ok via {mode} ver={_HEADER_ASSET_VER} id={_zalo_header_token[:12]}…")
            return _zalo_header_token
        err = result.get("error_code")
        print(
            f"[ZALO BRAND] upload failed mode={mode} "
            f"code={err} msg={result.get('message')}"
        )
    return None


def _image_msg(user_id: str, payload: dict) -> dict:
    return {
        "recipient": {"user_id": user_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": payload,
            }
        },
    }


def _media_template_msg(user_id: str, image_url: str) -> dict:
    return {
        "recipient": {"user_id": user_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "media",
                    "elements": [{"media_type": "image", "url": image_url}],
                },
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


def _brand_send_attempts(user_id: str, att: Optional[str]) -> list[tuple[str, dict]]:
    """Official docs: image + payload.token. Fallbacks: attachment_id, url, media template."""
    pub = public_header_url()
    attempts: list[tuple[str, dict]] = []
    if att:
        attempts.append(("token_only", _image_msg(user_id, {"token": att})))
        attempts.append(("attachment_id_only", _image_msg(user_id, {"attachment_id": att})))
        attempts.append(("token+attachment_id", _image_msg(user_id, {"token": att, "attachment_id": att})))
    attempts.append(("url", _image_msg(user_id, {"url": pub})))
    attempts.append(("media_template_url", _media_template_msg(user_id, pub)))
    return attempts


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
            need_retry = False
            for mode, payload in _brand_send_attempts(user_id, att):
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
                        global _zalo_header_token, _zalo_header_token_ts
                        _zalo_header_token = None
                        _zalo_header_token_ts = 0.0
                        need_retry = True
                        break
                except Exception as e:
                    print(f"[ZALO BRAND HTTP] mode={mode} {type(e).__name__}: {e}")
            if not need_retry:
                break
    return False


async def diagnose_zalo_brand(*, user_id: Optional[str] = None, reset: bool = False) -> dict:
    """
    Admin diagnostic: static file, upload, optional send to user_id.
    Does not run GraphRAG.
    """
    global _last_zalo_user_id
    if reset:
        cleared = clear_all_brand_headers()
    else:
        cleared = 0

    out: dict = {
        "header_file": str(header_image_path() or ""),
        "header_file_ok": header_image_path() is not None,
        "public_url": public_header_url(),
        "upload_urls": [u for _, u in ZALO_UPLOAD_URLS],
        "send_url": f"{ZALO_API_BASE}/oa/message/cs",
        "last_zalo_user_id": (_last_zalo_user_id[:8] + "…") if _last_zalo_user_id else None,
        "brand_cache_cleared": cleared,
    }
    token = await get_access_token()
    out["access_token_len"] = len(token or "")
    if not token:
        out["upload"] = {"ok": False, "error": "empty access token"}
        return out

    uid = user_id or _last_zalo_user_id

    async with httpx.AsyncClient(timeout=20) as client:
        global _zalo_header_token, _zalo_header_token_ts
        _zalo_header_token = None
        _zalo_header_token_ts = 0.0

        path = header_image_path()
        upload_attempts = []
        att = None
        for mode, kwargs in _upload_attempt_specs(path):
            if not kwargs.get("path") and not kwargs.get("image_url"):
                continue
            result = await _upload_zalo_image_attempt(client, token, **kwargs)
            # Drop huge raw bodies from response
            slim = {k: v for k, v in result.items() if k != "raw"}
            upload_attempts.append({"mode": mode, **slim})
            if result.get("ok"):
                out["upload"] = {
                    "ok": True,
                    "mode": mode,
                    "attachment_id": result.get("attachment_id"),
                    "attempts": upload_attempts,
                }
                att = result.get("attachment_id")
                break
        else:
            out["upload"] = {"ok": False, "attachment_id": None, "attempts": upload_attempts}

        if uid:
            url = f"{ZALO_API_BASE}/oa/message/cs"
            headers = {"access_token": token, "Content-Type": "application/json"}
            send_attempts = []
            for send_mode, payload in _brand_send_attempts(uid, att):
                ok, data = await _post_zalo_image(client, url, headers, payload)
                send_attempts.append({
                    "mode": send_mode,
                    "ok": ok,
                    "error": data.get("error"),
                    "message": data.get("message"),
                })
                if ok:
                    confirm_brand_header_sent("zalo", uid)
                    break
            out["send_test"] = {
                "ok": any(a["ok"] for a in send_attempts),
                "user_id": uid[:8] + "…",
                "attempts": send_attempts,
            }
        else:
            out["send_test"] = {
                "ok": None,
                "hint": "Pass user_id=… or send any Zalo message first (captures last user).",
            }

    return out


async def _send_zalo_reply(user_id: str, text: str, *, with_brand: bool = False) -> bool:
    """Send optional brand image, then text. Text always attempted."""
    if with_brand:
        try:
            ok = await _send_zalo_brand_image(user_id)
            if ok:
                confirm_brand_header_sent("zalo", user_id)
            else:
                clear_brand_header("zalo", user_id)
                print("[ZALO BRAND] send failed — topic gate cleared for retry")
        except Exception as e:
            clear_brand_header("zalo", user_id)
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

    global _last_zalo_user_id
    _last_zalo_user_id = user_id

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
