# -*- coding: utf-8 -*-
"""Zalo first card from protocol — no LLM, no Neo4j.

High-confidence stain binds only. Course/menu/exam commands return None
so GraphRAG / course handlers stay untouched.
"""
from __future__ import annotations

import re
from typing import Optional

from reply_lang import detect_reply_lang
from stain_hard_bind import bind_sweat_or_yellow_stain, bind_vn_specialty_stain, _norm_ascii

_CMD = re.compile(
    r"^\s*("
    r"교육|초급|중급|고급|모드|메뉴|도움말|시험|다음|진도|"
    r"hi|hello|hey|menu|help|xin\s*chào|xin\s*chao|"
    r"l1|l2|l3|course|khóa|khoa"
    r")\s*$",
    re.I,
)


def _fabric_hint(msg: str, raw_n: str) -> str:
    if any(k in msg for k in ("실크", "비단")) or "silk" in raw_n or "lua" in raw_n:
        return "silk"
    if any(k in msg for k in ("울", "모직", "캐시미어")) or "wool" in raw_n or "len " in f"{raw_n} ":
        return "wool"
    if any(k in msg for k in ("데님", "청바")) or "denim" in raw_n or "jean" in raw_n:
        return "denim"
    if any(k in msg for k in ("가죽", "스웨이드")) or "leather" in raw_n or "da " in f"{raw_n} ":
        return "leather"
    return "cotton"


def bind_fast_stain_id(user_message: str) -> Optional[str]:
    msg = user_message or ""
    if not msg.strip() or _CMD.match(msg.strip()):
        return None
    raw_n = _norm_ascii(msg)
    vn = bind_vn_specialty_stain(msg, raw_n)
    if vn:
        return vn
    if "laterite" in raw_n or "dat do" in raw_n or any(
        k in msg for k in ("라테라이트", "적토", "붉은 흙", "빨간 흙")
    ):
        return "S_LATERITE"
    if any(k in msg for k in ("카레", "강황")) or "ca ri" in raw_n or "curry" in raw_n:
        return "S_CURRY"
    if any(k in msg for k in ("볼펜", "잉크")) or "muc but" in raw_n or "pen ink" in raw_n:
        return "S_INK_PEN"
    if any(k in msg for k in ("녹물", "녹슨", "녹 얼룩")) or "ri set" in raw_n or "rust" in raw_n:
        return "S_RUST"
    if any(k in msg for k in ("김치",)) or "kim chi" in raw_n or "kimchi" in raw_n:
        return "S_KIMCHI"
    if any(k in msg for k in ("염색약", "헤어 염색")) or "thuoc nhuom" in raw_n or "hair dye" in raw_n:
        return "S_HAIR_DYE"
    if any(k in msg for k in ("립스틱",)) or "son moi" in raw_n or "lipstick" in raw_n:
        return "S_LIPSTICK"
    if any(k in msg for k in ("라떼",)) or "latte" in raw_n:
        return "S_MILK_COFFEE"
    if any(k in msg for k in ("커피", "블랙커피")) or "ca phe" in raw_n or "coffee" in raw_n:
        return "S_BLACK_COFFEE"
    if any(k in msg for k in ("와인", "적포도")) or "ruou vang" in raw_n or "wine" in raw_n:
        return "S_RED_WINE"
    if any(k in msg for k in ("혈액", "피 얼룩", "핏자국", "피묻")) or "mau tuoi" in raw_n or "blood" in raw_n:
        if any(k in msg for k in ("마른", "건조", "굳은")) or "kho" in raw_n or "dried" in raw_n:
            return "S_BLOOD_DRY"
        return "S_BLOOD_FRESH"
    if any(k in msg for k in ("식용유", "기름 얼룩", "오일 얼룩")) or "cooking oil" in raw_n:
        return "S_COOKING_OIL"
    sy = bind_sweat_or_yellow_stain(msg, raw_n)
    if sy:
        return sy
    return None


def try_fast_front_card(user_message: str) -> Optional[str]:
    """Return a short 【지금 바로】 card, or None if bind is weak."""
    sid = bind_fast_stain_id(user_message)
    if not sid:
        return None
    from protocol import PROTOCOL_BUILDERS, has_protocol

    if not has_protocol(sid):
        return None
    lang = detect_reply_lang(user_message)
    if lang not in {"vi", "ko", "en"}:
        lang = "ko"
    raw_n = _norm_ascii(user_message)
    fabric = _fabric_hint(user_message, raw_n)
    proto = PROTOCOL_BUILDERS[sid]()
    graph = {
        "protocol": {**proto.to_dict(), "garment_color": ""},
        "stain_context": {"id": sid},
        "fabric_context": {"id": "F1", "name": fabric},
        "entities": {"fabric_type": fabric, "stain_id": sid, "_raw": user_message},
        "_raw": user_message,
    }
    from owner_answer_clarity import build_front_summary

    card = (build_front_summary(graph, lang) or "").strip()
    if not card or len(card) < 12:
        return None
    if lang == "en":
        wait = "Full steps next — please wait a moment."
    elif lang == "vi":
        wait = "Bước chi tiết gửi tiếp. Xin chờ một chút."
    else:
        wait = "자세한 Step은 이어서 보냅니다. 잠시만 기다려 주세요."
    return f"{wait}\n\n{card}"
