# -*- coding: utf-8 -*-
"""Explain a chemical from SOP follow-up questions (VI/KO/EN)."""
from __future__ import annotations

import re
from typing import Optional

from chem_owner_vi import CHEM_OWNER_KO, CHEM_OWNER_VI, match_chem_code, owner_card


_CHEM_Q = re.compile(
    r"(?i)("
    r"hoa\s*chat|hóa\s*chất|la\s*gi|là\s*gì|nghia\s*la|nghĩa\s*là|"
    r"dung\s*de\s*gi|dùng\s*để\s*gì|cai\s*gi|cái\s*gì|"
    r"enzyme|protease|amylase|lipase|javel|acetone|giấm|giam|"
    r"what\s+is|what\s+chemical|화확|약품|뭐야|무엇인가|란\s*뭐"
    r")"
)


def looks_like_chem_question(msg: str) -> bool:
    t = (msg or "").strip()
    if not t or len(t) > 160:
        return False
    return bool(_CHEM_Q.search(t)) or bool(re.search(r"(?i)\b(e1|e2|e3|a3|b1|b2|d2|x2|s1)\b", t))


def format_chem_explain(code: str, *, lang: str = "vi") -> str:
    card = owner_card(code, lang=lang)
    if not card.get("name_vi") and not card.get("name_ko"):
        return ""
    if lang == "ko":
        # Prefer KO from CHEM_META + CHEM_OWNER_KO (shop/buy)
        try:
            from protocol import CHEM_META

            meta = CHEM_META.get(code.upper()) or {}
        except Exception:
            meta = {}
        own_ko = CHEM_OWNER_KO.get(code.upper()) or {}
        name = meta.get("name_ko") or own_ko.get("shop_name_ko") or card.get("name_vi") or code
        shop = own_ko.get("shop_name_ko") or ""
        dil = meta.get("dilution_ko") or card.get("dilution_vi") or ""
        when = own_ko.get("alt1_ko") or card.get("when_use_vi") or ""
        forbid = card.get("forbid_vi") or ""
        buy = own_ko.get("buy_where_ko") or card.get("buy_where_vi") or ""
        lines = [
            f"약품 설명 — {name}",
            f"· 매장명: {shop}" if shop and shop not in str(name) else "",
            f"· 용도: {when}" if when else "",
            f"· 희석·사용: {dil}" if dil else "",
            f"· 구매: {buy}" if buy else "",
            f"· 주의: {forbid}" if forbid else "",
            "코드명만 외우지 말고, 매장에서는 위 제품·구매처로 설명하세요.",
        ]
        return "\n".join(x for x in lines if x)

    if lang == "en":
        name = card.get("name_vi") or code
        return (
            f"Chemical — {name}\n"
            f"· What it is / when: {card.get('when_use_vi') or ''}\n"
            f"· Shop name: {card.get('shop_name_vi') or ''}\n"
            f"· Buy: {card.get('buy_where_vi') or ''}\n"
            f"· Dilution: {card.get('dilution_vi') or ''}\n"
            f"· Limits: {card.get('forbid_vi') or ''}"
        ).strip()

    # Vietnamese (default) — franchise shop language
    name = card.get("name_vi") or code
    shop = card.get("shop_name_vi") or name
    lines = [
        f"Hóa chất trong SOP — {name}",
        f"· Tên gọi cửa hàng: {shop}",
        f"· Là gì / dùng khi nào: {card.get('when_use_vi') or ''}",
        f"· Mua ở đâu: {card.get('buy_where_vi') or ''}",
        f"· Pha / dùng thế nào: {card.get('dilution_vi') or ''}",
        f"· Cấm / lưu ý: {card.get('forbid_vi') or ''}",
    ]
    # Keep forbid clauses split for staff (silk/wool vs Javel mix)
    fixed = []
    for line in lines:
        if not line or line.endswith(": "):
            continue
        if "forbid" in line.lower() or line.startswith("· Cấm"):
            line = line.replace(
                "CẤM lụa/len — chuyển sang nước giặt trung tính. CẤM ngâm cùng Javel.",
                "CẤM dùng trên lụa/len (chuyển sang nước giặt trung tính). Riêng: CẤM ngâm chung với Javel.",
            )
            line = line.replace(
                "CẤM lụa, len. CẤM trộn Javel/amoniac.",
                "CẤM dùng trên lụa, len. Riêng: CẤM trộn với Javel hoặc amoniac.",
            )
        fixed.append(line)
    return "\n".join(fixed)

def try_explain_chem(
    msg: str,
    prefer_codes: Optional[list[str]] = None,
    *,
    lang: str = "vi",
) -> str:
    if not looks_like_chem_question(msg) and not prefer_codes:
        return ""
    code = match_chem_code(msg, prefer_codes)
    if not code and prefer_codes:
        # "hoa chat gi" with one chem in session
        if len(prefer_codes) == 1:
            code = prefer_codes[0]
        elif prefer_codes:
            # pick first enzyme-like or first
            for c in prefer_codes:
                if str(c).upper() in CHEM_OWNER_VI:
                    code = c
                    break
    if not code:
        return ""
    return format_chem_explain(code, lang=lang)
