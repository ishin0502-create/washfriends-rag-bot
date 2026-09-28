# -*- coding: utf-8 -*-
"""Unauthorized Zalo users: registration form + submit pending HQ request.

Never asks the user to type their Zalo numeric ID — the bot already has it.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional

from reply_lang import detect_reply_lang

_REG_HINT = re.compile(
    r"(등록|허용|가맹|일반\s*세탁|세탁소|매장\s*이름|점주|직원|"
    r"đăng\s*ký|cua\s*hang|cửa\s*hàng|chu\s*cua|chủ|"
    r"nhân\s*viên|nhan\s*vien|"
    r"tên\s*[:：]|ten\s*[:：]|"
    r"register|franchise|laundry\s*shop|staff|owner)",
    re.I,
)


def registration_prompt(lang: str = "ko") -> str:
    if lang == "ko":
        return (
            "◆ 허용된 교육 채널입니다.\n"
            "아직 등록되지 않았습니다. 아래를 **한 번에** 적어 보내 주세요.\n"
            "\n"
            "1) 구분: 가맹점 또는 일반세탁소\n"
            "2) 매장 이름:\n"
            "3) 본인 이름:\n"
            "4) 역할: 점주 또는 직원\n"
            "\n"
            "본사가 확인한 뒤 허용됩니다. "
            "(Zalo 숫자 ID는 보낼 필요 없습니다 — 시스템이 이미 알고 있습니다.)"
        )
    if lang == "en":
        return (
            "◆ This is a restricted education channel.\n"
            "You are not registered yet. Please send all of the following:\n"
            "\n"
            "1) Type: franchise OR general laundry\n"
            "2) Store name:\n"
            "3) Your name:\n"
            "4) Role: owner OR staff\n"
            "\n"
            "HQ will review and approve. "
            "(No need to send a Zalo numeric ID — we already have it.)"
        )
    return (
        "◆ Đây là kênh đào tạo có kiểm soát.\n"
        "Chưa đăng ký. Vui lòng gửi đủ:\n"
        "\n"
        "1) Loại: franchise (nhượng quyền) HOẶC general (tiệm giặt thường)\n"
        "2) Tên cửa hàng:\n"
        "3) Tên của bạn:\n"
        "4) Vai trò: owner (chủ) HOẶC staff (nhân viên)\n"
        "\n"
        "HQ sẽ duyệt. "
        "(Không cần gửi Zalo ID số — hệ thống đã biết.)"
    )


def looks_like_registration(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 8 or len(t) > 2000:
        return False
    return bool(_REG_HINT.search(t))


def parse_registration(text: str) -> Optional[dict]:
    """Best-effort parse. Returns None if too incomplete."""
    raw = (text or "").strip()
    if not looks_like_registration(raw):
        return None
    low = raw.lower()

    kind = "franchise"
    if re.search(r"일반\s*세탁|일반세탁|general|tiệm\s*giặt\s*thường|tiem\s*giat", raw, re.I):
        kind = "general"
    elif re.search(r"가맹|franchise|nhượng\s*quyền|nhuong\s*quyen", raw, re.I):
        kind = "franchise"

    role = "owner"
    if re.search(r"직원|staff|nhân\s*viên|nhan\s*vien", raw, re.I):
        role = "staff"
    elif re.search(r"점주|owner|chủ|chu\s*cua", raw, re.I):
        role = "owner"

    store = ""
    m = re.search(
        r"(?:매장\s*이름|매장명|store\s*name|tên\s*cửa\s*hàng|ten\s*cua\s*hang)\s*[:：]?\s*(.+)",
        raw,
        re.I,
    )
    if m:
        store = m.group(1).splitlines()[0].strip()[:200]

    person = ""
    m2 = re.search(
        r"(?:본인\s*이름|your\s*name|tên\s*của\s*bạn|ten\s*cua\s*ban)\s*[:：]?\s*(.+)",
        raw,
        re.I,
    )
    if not m2:
        # VI/KO bare name label: "Tên:" / "이름:" (not store name)
        m2 = re.search(
            r"(?:^|[/\n\s])(?:tên|ten|이름)\s*[:：]\s*(.+)",
            raw,
            re.I,
        )
    if m2:
        person = m2.group(1).split("/")[0].splitlines()[0].strip()[:120]
        person = re.sub(r"\s*[-–—].*$", "", person).strip()

    # "Name / role / phone" one-liner without store
    if not person:
        m3 = re.search(
            r"(?:^|[/\n])\s*([A-Za-zÀ-ỹĂăÂâÊêÔôƠơƯưĐđ][A-Za-zÀ-ỹăâêôơưđ\s]{1,60})\s*/\s*(?:nhân\s*viên|nhan\s*vien|staff|점주|owner|chủ)",
            raw,
            re.I,
        )
        if m3:
            person = m3.group(1).strip()[:120]

    if not store:
        # Prefer explicit store; else keep placeholder (do NOT steal person name line)
        for line in raw.splitlines():
            s = line.strip()
            if len(s) < 2:
                continue
            if re.search(r"^(?:tên|ten|이름)\s*[:：]", s, re.I):
                continue
            if re.fullmatch(
                r"(가맹점|일반세탁소|점주|직원|franchise|general|owner|staff|nhân\s*viên|nhan\s*vien)",
                s,
                re.I,
            ):
                continue
            if re.search(r"nhân\s*viên|nhan\s*vien|staff|점주|owner", s, re.I) and re.search(
                r"tên|ten|이름", s, re.I
            ):
                continue
            # phone-only line
            if re.fullmatch(r"[\d\s\-+]{8,}", s):
                continue
            store = s.split("/")[0].strip()[:200]
            break
    if not store:
        store = "미기재"
    if not person:
        person = "미기재"

    return {
        "client_kind": kind,
        "store_name": store,
        "person_name": person,
        "person_role": role,
        "raw_message": raw[:4000],
    }


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


def submit_access_request(zalo_user_id: str, parsed: dict) -> bool:
    base = _hq_base()
    secret = _hq_secret()
    if not base or not secret:
        print("[EDU REG] HQ API not configured — cannot submit request")
        return False
    url = f"{base}/api/v1/internal/education-bot/access-requests"
    payload = {
        "zalo_user_id": zalo_user_id,
        "client_kind": parsed["client_kind"],
        "store_name": parsed["store_name"],
        "person_name": parsed["person_name"],
        "person_role": parsed["person_role"],
        "raw_message": parsed.get("raw_message"),
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "X-Internal-Secret": secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return 200 <= getattr(resp, "status", 200) < 300
    except Exception as e:
        print(f"[EDU REG] submit failed: {e}")
        return False


def handle_unauthorized_message(user_id: str, text: str) -> str:
    """Return reply for unauthorized sender (registration form or ack)."""
    lang = detect_reply_lang(text or "")
    parsed = parse_registration(text or "")
    if parsed:
        ok = submit_access_request(user_id, parsed)
        if ok:
            if lang == "ko":
                return (
                    "◆ 등록 요청을 접수했습니다.\n"
                    f"구분: {'가맹점' if parsed['client_kind']=='franchise' else '일반세탁소'}\n"
                    f"매장: {parsed['store_name']}\n"
                    f"이름: {parsed['person_name']} ({'점주' if parsed['person_role']=='owner' else '직원'})\n"
                    "본사 확인 후 허용됩니다. 허용되면 다시 질문해 주세요."
                )
            if lang == "en":
                return (
                    "◆ Registration request received.\n"
                    f"Type: {parsed['client_kind']}\n"
                    f"Store: {parsed['store_name']}\n"
                    f"Name: {parsed['person_name']} ({parsed['person_role']})\n"
                    "HQ will approve. Please ask again after approval."
                )
            return (
                "◆ Đã nhận yêu cầu đăng ký.\n"
                f"Loại: {parsed['client_kind']}\n"
                f"Cửa hàng: {parsed['store_name']}\n"
                f"Tên: {parsed['person_name']} ({parsed['person_role']})\n"
                "HQ sẽ duyệt. Sau khi được phép hãy hỏi lại."
            )
        # submit failed — still show form
        return registration_prompt(lang) + (
            "\n\n(접수 전송에 실패했습니다. 잠시 후 다시 보내 주세요.)"
            if lang == "ko"
            else "\n\n(Submit failed — please try again shortly.)"
        )
    return registration_prompt(lang)
