# -*- coding: utf-8 -*-
"""HQ-backed field-question usage log + optional daily limit.

Safe defaults:
  - Limit OFF until HQ enables it
  - API failure → fail-open (do not block owners)
  - Exam / L1 / quiz / mode commands are NOT counted (caller decides)
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

from l1_course import is_l1_complete
from reply_lang import detect_reply_lang


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


def _http_json(method: str, path: str, payload: Optional[dict] = None) -> Optional[dict]:
    base = _hq_base()
    secret = _hq_secret()
    if not base or not secret:
        return None
    url = f"{base}{path}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "X-Internal-Secret": secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return json.loads(raw) if raw else {}
    except Exception as e:
        print(f"[QA USAGE] HQ {method} {path} failed: {e}")
        return None


def fetch_access_meta(zalo_user_id: str) -> dict[str, Any]:
    uid = (zalo_user_id or "").strip()
    if not uid:
        return {}
    q = urllib.parse.urlencode({"zalo_user_id": uid})
    data = _http_json("GET", f"/api/v1/internal/education-bot/access?{q}")
    if not data or not data.get("allowed"):
        return {}
    return {
        "client_kind": data.get("client_kind"),
        "store_code": data.get("store_code"),
        "store_name": data.get("store_name_ko") or data.get("store_name") or "",
        "person_name": data.get("store_name_ko") or "",
    }


def check_quota(zalo_user_id: str) -> dict[str, Any]:
    """Return quota snapshot. Fail-open when HQ unreachable."""
    uid = (zalo_user_id or "").strip()
    if not uid:
        return {"allowed": True, "enabled": False, "fail_open": True}
    q = urllib.parse.urlencode({"zalo_user_id": uid})
    data = _http_json("GET", f"/api/v1/internal/education-bot/qa/quota?{q}")
    if not data:
        return {"allowed": True, "enabled": False, "fail_open": True}
    return {
        "allowed": bool(data.get("allowed", True)),
        "enabled": bool(data.get("enabled")),
        "limit": data.get("limit"),
        "used": data.get("used"),
        "remaining": data.get("remaining"),
        "fail_open": False,
    }


def log_field_question(
    zalo_user_id: str,
    question: str,
    *,
    meta: Optional[dict[str, Any]] = None,
) -> bool:
    uid = (zalo_user_id or "").strip()
    q = (question or "").strip()[:2000]
    if not uid or not q:
        return False
    body = {
        "zalo_user_id": uid,
        "question": q,
    }
    if meta:
        if meta.get("client_kind"):
            body["client_kind"] = str(meta["client_kind"])[:20]
        if meta.get("store_code"):
            body["store_code"] = str(meta["store_code"])[:40]
        if meta.get("store_name"):
            body["store_name"] = str(meta["store_name"])[:200]
        if meta.get("person_name"):
            body["person_name"] = str(meta["person_name"])[:120]
    data = _http_json("POST", "/api/v1/internal/education-bot/qa/events", body)
    return bool(data and data.get("ok"))


def over_limit_reply(zalo_user_id: str, text: str = "") -> str:
    """When daily limit hit: nudge L1 if incomplete, else ask to wait until tomorrow."""
    lang = detect_reply_lang(text or "")
    if not is_l1_complete(zalo_user_id):
        if lang == "ko":
            return (
                "오늘은 현장 질문 한도를 다 쓰셨어요.\n"
                "초급 교육 「교육」을 이어서 읽어 주세요.\n"
                "「다음」으로 다음 장 · 내일 다시 현장 질문을 하실 수 있어요."
            )
        if lang == "en":
            return (
                "You've used today's field-question allowance.\n"
                "Please continue the beginner course: type 「교육」.\n"
                "Use 「다음」 for the next lesson. Field Q&A resets tomorrow."
            )
        return (
            "Hôm nay anh/chị đã dùng hết số câu hỏi thực tế.\n"
            "Hãy tiếp tục khóa cơ bản: gõ 「교육」.\n"
            "「다음」 để sang bài tiếp. Câu hỏi thực tế sẽ mở lại ngày mai."
        )
    if lang == "ko":
        return (
            "오늘은 현장 질문 한도를 다 쓰셨어요.\n"
            "내일 다시 물어 주세요. (초급 교육은 「교육」으로 언제든 볼 수 있어요)"
        )
    if lang == "en":
        return (
            "You've used today's field-question allowance.\n"
            "Please ask again tomorrow. (Beginner course: type 「교육」 anytime.)"
        )
    return (
        "Hôm nay anh/chị đã dùng hết số câu hỏi thực tế.\n"
        "Mai hỏi lại nhé. (Khóa cơ bản: gõ 「교육」 bất cứ lúc nào.)"
    )


def gate_field_question(zalo_user_id: str, text: str) -> Optional[str]:
    """
    If daily limit is enabled and exhausted, return a reply string (block GraphRAG).
    Otherwise return None (allow).
    """
    snap = check_quota(zalo_user_id)
    if snap.get("allowed", True):
        return None
    return over_limit_reply(zalo_user_id, text)
