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
import re
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from typing import Optional

import httpx
from fastapi import Request, HTTPException

from graphrag_engine import generate_response
from image_flow import process_channel_image
from reply_lang import detect_reply_lang
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
from zalo_owner_access import gate_status, is_authorized_owner
from education_registration import handle_unauthorized_message
from learning_mode import maybe_append_footer, try_handle_mode_or_quiz
from owner_qa_log import append_turn, get_mode
from weekly_exam import try_handle_exam_history, try_handle_exam_message
from l1_course import try_handle_l1_course
from l2_course import try_handle_l2_course
from l3_course import try_handle_l3_course
from qa_usage import fetch_access_meta, gate_field_question, log_field_question
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


async def _send_zalo_local_png(
    user_id: str,
    png_path: str,
    *,
    public_url: Optional[str] = None,
) -> bool:
    """Upload/send a care-symbol (or any) PNG. Prefer public HTTPS URL for Zalo."""
    raw = (png_path or "").strip()
    sid = None
    if "|" in raw:
        path_s, sid_s = raw.split("|", 1)
        path = Path(path_s)
        try:
            sid = int(sid_s)
        except ValueError:
            sid = None
    else:
        path = Path(raw)
        # quiz image_path may be plain .../symbol_06.png
        m = re.search(r"symbol_(\d+)\.png$", path.name, re.I)
        if m:
            sid = int(m.group(1))

    if public_url is None and sid is not None:
        try:
            from care_symbol_svg import public_care_symbol_url

            public_url = public_care_symbol_url(sid)
        except Exception:
            public_url = None

    token = await get_access_token()
    if not token:
        print("[ZALO QUIZ IMG] empty token")
        return False
    send_url = f"{ZALO_API_BASE}/oa/message/cs"

    async with httpx.AsyncClient(timeout=25) as client:
        att = None
        # 1) Prefer image_url (Zalo fetches our Railway static PNG)
        if public_url:
            for api_ver, upload_url in ZALO_UPLOAD_URLS:
                for auth in ("header", "query"):
                    result = await _upload_zalo_image_attempt(
                        client,
                        token,
                        upload_url=upload_url,
                        image_url=public_url,
                        auth=auth,
                    )
                    att = result.get("attachment_id")
                    if att:
                        print(f"[ZALO QUIZ IMG] upload ok via {api_ver}/url+{auth} sid={sid}")
                        break
                if att:
                    break
        # 2) Fallback: multipart file (path only — never brand header URL)
        if not att and path.is_file():
            for api_ver, upload_url in ZALO_UPLOAD_URLS:
                for auth in ("header", "query"):
                    result = await _upload_zalo_image_attempt(
                        client,
                        token,
                        upload_url=upload_url,
                        path=path,
                        auth=auth,
                    )
                    att = result.get("attachment_id")
                    if att:
                        print(f"[ZALO QUIZ IMG] upload ok via {api_ver}/file+{auth}")
                        break
                if att:
                    break
        if not att:
            print(f"[ZALO QUIZ IMG] upload failed path={path} url={public_url}")
            return False

        headers = {"access_token": token, "Content-Type": "application/json"}
        attempts = [
            ("token_only", _image_msg(user_id, {"token": att})),
            ("attachment_id_only", _image_msg(user_id, {"attachment_id": att})),
        ]
        if public_url:
            attempts.append(("url", _image_msg(user_id, {"url": public_url})))
            attempts.append(("media_template_url", _media_template_msg(user_id, public_url)))
        for mode, payload in attempts:
            try:
                ok, data = await _post_zalo_image(client, send_url, headers, payload)
                if ok:
                    print(f"[ZALO QUIZ IMG] sent via {mode}")
                    return True
                print(f"[ZALO QUIZ IMG] send fail mode={mode} {data.get('error')} {data.get('message')}")
            except Exception as e:
                print(f"[ZALO QUIZ IMG] {mode} {type(e).__name__}: {e}")
    return False


async def _send_queued_care_symbol_images(user_id: str) -> int:
    """Send all pending care-symbol PNGs; return how many succeeded."""
    from care_label_quiz import pop_queued_symbol_images
    from care_symbol_svg import public_care_symbol_url

    items = pop_queued_symbol_images(user_id)
    if not items:
        return 0
    ok_n = 0
    fail_urls: list[str] = []
    for i, item in enumerate(items):
        sid = None
        path_s = item
        if "|" in item:
            path_s, sid_s = item.split("|", 1)
            try:
                sid = int(sid_s)
            except ValueError:
                sid = None
        pub = public_care_symbol_url(sid) if sid is not None else None
        sent = await _send_zalo_local_png(user_id, item, public_url=pub)
        if sent:
            ok_n += 1
        elif pub:
            fail_urls.append(pub)
        if i + 1 < len(items):
            await asyncio.sleep(0.45)
    if ok_n == 0 and fail_urls:
        links = "\n".join(f"· {u}" for u in fail_urls[:6])
        await _send_zalo_reply(
            user_id,
            "기호 그림 전송이 잠시 막혔습니다. 아래 링크를 눌러 확인해 주세요:\n" + links,
            with_brand=False,
        )
    return ok_n


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
                        token = await refresh_tokens(force=True)  # HQ access reload only
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
    """Send text first (owners wait on GraphRAG already), then optional brand image."""
    try:
        from owner_answer_clarity import split_zalo_messages

        parts = split_zalo_messages(text or "", max_len=1900)
    except Exception:
        parts = [(text or "")[:1900]] if text else []
    if not parts:
        return False

    all_ok = True
    for i, part in enumerate(parts):
        ok = await _send_zalo_text_once(user_id, part)
        if not ok:
            all_ok = False
            break
        if i + 1 < len(parts):
            await asyncio.sleep(0.45)

    if with_brand:
        try:
            ok = await _send_zalo_brand_image(user_id)
            if ok:
                confirm_brand_header_sent("zalo", user_id)
            else:
                clear_brand_header("zalo", user_id)
                print("[ZALO BRAND] send failed after text — topic gate cleared for retry")
        except Exception as e:
            clear_brand_header("zalo", user_id)
            print(f"[ZALO BRAND] skipped after text: {e}")
    return all_ok


async def _send_zalo_text_once(user_id: str, text: str) -> bool:
    """Single OA text message (API hard cap ~2000)."""
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
                        print(f"[ZALO SEND] token error {err} — reloading access from HQ")
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


def _thinking_ack_text(user_text: str = "") -> str:
    """Short wait notice in the same language as the user (KO/VI/EN). No LLM."""
    lang = detect_reply_lang(user_text or "")
    if lang == "ko":
        return "확인 중입니다. 잠시만 기다려 주세요."
    if lang == "en":
        return "Checking now. Please wait a moment."
    return "Đang kiểm tra. Vui lòng chờ trong giây lát."


def _error_reply_text(user_text: str = "") -> str:
    lang = detect_reply_lang(user_text or "")
    if lang == "ko":
        return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."
    if lang == "en":
        return "Sorry — a temporary error occurred. Please try again in a moment."
    return "Xin lỗi, hệ thống tạm thời gặp sự cố. Vui lòng thử lại sau ít phút."


async def _process_zalo_event(event_name: str, user_id: str, text: str, image_url: Optional[str]) -> None:
    """Heavy AI work — runs after webhook ACK."""
    loop = asyncio.get_event_loop()
    lang_src = text or ""
    try:
        # Franchise-owner gate: unauthorized users get a fixed refusal (no GraphRAG).
        # OA 1:1 already keeps A/B chats private; this only controls who may use the bot.
        if not is_authorized_owner(user_id):
            st = gate_status()
            print(
                f"[ZALO OWNER GATE] denied user_id={user_id} "
                f"mode={st.get('mode')} allowlist_size={st.get('allowlist_size')}"
            )
            # Registration form / pending request — Zalo ID is never asked of the user.
            reply = handle_unauthorized_message(user_id, lang_src)
            await _send_zalo_reply(user_id, reply, with_brand=False)
            return

        # Past exam scores (own Zalo id only) — before active exam grading
        if event_name == "user_send_text" and text:
            hist_reply = try_handle_exam_history(user_id, text)
            if hist_reply:
                await _send_zalo_reply(user_id, hist_reply, with_brand=False)
                return

        # Weekly exam (if assigned) — before field/learning mode
        if event_name == "user_send_text" and text:
            exam_reply = try_handle_exam_message(user_id, text)
            if exam_reply:
                await _send_zalo_reply(user_id, exam_reply, with_brand=False)
                return

        # Show care-symbol images on request (e.g. 「드라이클리닝 기호 보여줘」)
        if event_name == "user_send_text" and text:
            try:
                from care_label_quiz import try_handle_show_symbols

                show_reply = try_handle_show_symbols(user_id, text)
                if show_reply:
                    await _send_zalo_reply(user_id, show_reply, with_brand=False)
                    await _send_queued_care_symbol_images(user_id)
                    return
            except Exception as show_err:
                print(f"[ZALO SHOW SYMBOLS] skip: {show_err}")

        # L3 advanced course (after L2) — before L2 so 「다음」 routes correctly
        if event_name == "user_send_text" and text:
            try:
                course_reply = try_handle_l3_course(user_id, text)
                if course_reply:
                    await _send_zalo_reply(user_id, course_reply, with_brand=False)
                    return
            except Exception as course_err:
                print(f"[ZALO L3 COURSE] skip: {course_err}")

        # L2 intermediate course (after L1) — before L1 so 「다음」 routes correctly
        if event_name == "user_send_text" and text:
            try:
                course_reply = try_handle_l2_course(user_id, text)
                if course_reply:
                    await _send_zalo_reply(user_id, course_reply, with_brand=False)
                    return
            except Exception as course_err:
                print(f"[ZALO L2 COURSE] skip: {course_err}")

        # L1 sequential course (opt-in commands only — never steals stain Q&A)
        if event_name == "user_send_text" and text:
            try:
                course_reply = try_handle_l1_course(user_id, text)
                if course_reply:
                    await _send_zalo_reply(user_id, course_reply, with_brand=False)
                    return
            except Exception as course_err:
                print(f"[ZALO L1 COURSE] skip: {course_err}")

        # Field / learning mode + active quiz (no GraphRAG / no LLM)
        if event_name == "user_send_text" and text:
            mode_reply = try_handle_mode_or_quiz(user_id, text)
            if mode_reply:
                await _send_zalo_reply(user_id, mode_reply, with_brand=False)
                # Care-symbol quiz: send the symbol PNG for the current question
                try:
                    from care_label_quiz import current_quiz_image_path

                    img = current_quiz_image_path(user_id)
                    if img:
                        await _send_zalo_local_png(user_id, img)
                except Exception as img_err:
                    print(f"[ZALO QUIZ IMG] skip: {img_err}")
                return

        # Optional HQ daily field-question limit (off by default; fail-open)
        if event_name == "user_send_text" and text:
            try:
                limit_reply = gate_field_question(user_id, text)
                if limit_reply:
                    await _send_zalo_reply(user_id, limit_reply, with_brand=False)
                    return
            except Exception as qa_err:
                print(f"[QA USAGE] gate skip: {qa_err}")

        # Image field questions also count toward the optional daily limit
        if event_name == "user_send_image":
            try:
                limit_reply = gate_field_question(user_id, text or "")
                if limit_reply:
                    await _send_zalo_reply(user_id, limit_reply, with_brand=False)
                    return
            except Exception as qa_err:
                print(f"[QA USAGE] image gate skip: {qa_err}")

        # Immediate "thinking" notice (fail-open: never block the real answer)
        sent_fast = False
        if event_name == "user_send_text" and text:
            try:
                from stain_fast_front import try_fast_front_card

                fast = try_fast_front_card(text)
                if fast:
                    await _send_zalo_reply(user_id, fast, with_brand=False)
                    sent_fast = True
                    print("[ZALO FAST] front card sent")
            except Exception as fast_err:
                print(f"[ZALO FAST] skip: {fast_err}")
        if not sent_fast:
            if event_name == "user_send_text" and text:
                try:
                    await _send_zalo_reply(user_id, _thinking_ack_text(lang_src), with_brand=False)
                except Exception as ack_err:
                    print(f"[ZALO ACK] failed (continuing): {ack_err}")
            elif event_name == "user_send_image":
                try:
                    await _send_zalo_reply(user_id, _thinking_ack_text(lang_src), with_brand=False)
                except Exception as ack_err:
                    print(f"[ZALO ACK] failed (continuing): {ack_err}")

        awaiting = get_session("zalo", user_id).get("awaiting") == "care_label"
        if event_name == "user_send_image":
            if not image_url:
                lang = detect_reply_lang(lang_src)
                if lang == "ko":
                    miss = "사진을 받지 못했습니다. 다시 보내 주시거나 얼룩을 글로 설명해 주세요."
                elif lang == "en":
                    miss = "Could not download the photo. Please resend it or describe the stain in text."
                else:
                    miss = "Anh khong tai duoc. Vui long gui lai anh hoac mo ta vet ban bang chu."
                await _send_zalo_reply(user_id, miss, with_brand=False)
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
            import time as _t

            _t0 = _t.time()
            reply_text = await loop.run_in_executor(
                _executor,
                lambda: generate_response(text, channel="zalo", user_id=user_id),
            )
            print(f"[ZALO TIMING] generate_s={_t.time() - _t0:.1f} chars={len(reply_text or '')}")
            if sent_fast and reply_text and "<<<ZALO_MSG2>>>" in reply_text:
                reply_text = "<<<ZALO_MSG2>>>" + reply_text.split("<<<ZALO_MSG2>>>", 1)[1]

        # Persist Q&A for personalized learning cards (disk, no LLM)
        try:
            if text and reply_text:
                append_turn(
                    user_id,
                    question=text if event_name == "user_send_text" else (text or "[image]"),
                    answer=reply_text,
                    lang=detect_reply_lang(lang_src),
                    bot_mode=get_mode(user_id),
                )
                reply_text = maybe_append_footer(reply_text, user_id, lang_src)
        except Exception as log_err:
            print(f"[OWNER QA LOG] skip: {log_err}")

        # HQ usage log (for counts/history + optional daily limit) — fail-open
        try:
            if reply_text and (event_name == "user_send_text" or event_name == "user_send_image"):
                q_log = text if event_name == "user_send_text" else (text or "[image]")
                if q_log:
                    meta = fetch_access_meta(user_id)
                    log_field_question(user_id, q_log, meta=meta)
        except Exception as qa_log_err:
            print(f"[QA USAGE] log skip: {qa_log_err}")

        with_brand = should_send_brand_header(
            "zalo",
            user_id,
            text or "",
            has_image=bool(image_url),
            awaiting_care_label=awaiting,
        )
        await _send_zalo_reply(user_id, reply_text, with_brand=with_brand)
        # If generate_response queued care-symbol PNGs, send them now
        try:
            await _send_queued_care_symbol_images(user_id)
        except Exception as img_err:
            print(f"[ZALO SHOW SYMBOLS] after-reply skip: {img_err}")
    except Exception as exc:
        print(f"[ZALO HANDLER ERROR] {type(exc).__name__}: {exc}")
        try:
            await _send_zalo_reply(
                user_id,
                _error_reply_text(lang_src),
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
                        "hint": "HQ access reload failed. Check WF_HQ_API_BASE + education-bot secret.",
                    }
            if isinstance(data, dict):
                data = {**data, "diag": diag, "owner_gate": gate_status()}
            return data
        except Exception as e:
            return {"error": str(e), "diag": diag, "owner_gate": gate_status()}
