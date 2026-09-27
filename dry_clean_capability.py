# -*- coding: utf-8 -*-
"""Dry-clean machine capability messaging for education bot.

OFF (default): no Realstar/PROG teaching — equip-then-train + HQ inquiry.
ON (HQ verified): professional-care education unlocked (machine PROG from
store/HQ manuals — never invent button numbers here).
"""
from __future__ import annotations

import re
from typing import Optional

_DRY_TOPIC = re.compile(
    r"(드라이\s*클리닝|드라이클리닝|전문\s*세탁|전문\s*케어|드라이\s*하라|"
    r"dry\s*-?\s*clean|professional\s*care|giặt\s*khô|giat\s*kho|"
    r"원\s*\+?\s*P|circle\s*P|\bPCE\b|퍼클로|웨트\s*클리닝|wet\s*clean|"
    r"원\s*안\s*P|동그라미\s*(안)?\s*P)",
    re.I,
)


def is_dry_or_pro_topic(text: str) -> bool:
    return bool(_DRY_TOPIC.search(text or ""))


def lock_message(lang: str = "vi") -> str:
    """Store has no HQ-confirmed dry-cleaning machine."""
    if lang == "ko":
        return (
            "◆ [전문 케어 · 교육 잠금]\n"
            "이 건은 드라이클리닝(전문 세탁) 기준일 수 있습니다.\n"
            "이 매장에는 본사 확인된 드라이클리닝 기계가 없어, "
            "지금은 기계 작동법·전문 코스 교육은 열려 있지 않습니다.\n"
            "드라이클리닝 기계 구비·본사 확인 후에 "
            "작동법과 전문 세탁 교육이 진행됩니다.\n"
            "도입·문의 → 본사(Wash Friends HQ).\n"
            "⚠️ 라벨에 물세탁 금지가 있으면 습식 강처리·세탁기 투입을 하지 마세요."
        )
    if lang == "en":
        return (
            "◆ [Professional care · education locked]\n"
            "This item may require dry cleaning (professional care).\n"
            "This store has no HQ-confirmed dry-cleaning machine, so "
            "machine operation / professional course training is not open yet.\n"
            "After the machine is installed and HQ verifies it, "
            "operation and professional-care training will be enabled.\n"
            "Ask HQ (Wash Friends) about equipment.\n"
            "⚠️ If the label forbids water wash, do not force wet/machine wash."
        )
    return (
        "◆ [Chăm sóc chuyên nghiệp · đào tạo khóa]\n"
        "Món này có thể cần giặt khô (chăm sóc chuyên nghiệp).\n"
        "Cửa hàng chưa có máy giặt khô được HQ xác nhận → "
        "chưa mở hướng dẫn vận hành / khóa học chuyên nghiệp.\n"
        "Sau khi trang bị máy và HQ xác nhận, "
        "đào tạo vận hành + chăm sóc chuyên nghiệp sẽ được mở.\n"
        "Liên hệ HQ (Wash Friends) để tư vấn máy.\n"
        "⚠️ Nếu nhãn cấm giặt nước: không ép giặt ướt / bỏ máy."
    )


def unlock_message(lang: str = "vi", code: str = "") -> str:
    """Store has HQ-confirmed dry-cleaning machine — education open."""
    code_bit = f" ({code})" if code else ""
    if lang == "ko":
        return (
            f"◆ [전문 케어 · 교육 해금]{code_bit}\n"
            "본사 확인된 드라이클리닝 기계 보유 매장입니다. "
            "전문 케어·기계 교육이 열려 있습니다.\n"
            "기호 요지:\n"
            "· P = PCE(퍼클로) 드라이 가능\n"
            "· F = 석유계 용제만 (PCE 금지)\n"
            "· W = 전문 웨트클리닝 (저온·약탈수·전용 세제)\n"
            "· 밑줄 = 약공정 / 이중 밑줄 = 매우 약 / 원+X = 드라이 금지\n"
            "PROG·버튼 번호는 매장 기종 매뉴얼·본사 자료를 따르세요 "
            "(임의 번호 안내 금지).\n"
            "⚠️ 초급: 불확실하면 매니저·본사 확인. 라벨 X는 절대 무시하지 마세요."
        )
    if lang == "en":
        return (
            f"◆ [Professional care · education unlocked]{code_bit}\n"
            "HQ has confirmed a dry-cleaning machine at this store. "
            "Professional-care / machine training is open.\n"
            "Symbols:\n"
            "· P = PCE dry clean OK\n"
            "· F = hydrocarbon solvent only (no PCE)\n"
            "· W = professional wet clean (low temp, gentle spin, special detergent)\n"
            "· Underline = mild / double = very mild / circle+X = no dry clean\n"
            "Use store machine manual / HQ materials for PROG numbers "
            "(do not invent button numbers).\n"
            "⚠️ Beginners: ask manager/HQ if unsure. Never ignore label X."
        )
    return (
        f"◆ [Chăm sóc chuyên nghiệp · đã mở]{code_bit}\n"
        "HQ đã xác nhận máy giặt khô tại cửa hàng. "
        "Đào tạo chăm sóc chuyên nghiệp / vận hành đã mở.\n"
        "Ký hiệu:\n"
        "· P = giặt khô PCE được\n"
        "· F = chỉ dung môi dầu (cấm PCE)\n"
        "· W = wet clean chuyên nghiệp (nhiệt thấp, vắt nhẹ, hóa chất riêng)\n"
        "· Gạch dưới = nhẹ / hai gạch = rất nhẹ / vòng+X = cấm dry-clean\n"
        "Số PROG/nút theo sổ máy cửa hàng / tài liệu HQ "
        "(không bịa số nút).\n"
        "⚠️ Mới: không chắc → hỏi quản lý/HQ. Không bỏ qua X trên nhãn."
    )


def append_capability_block(
    answer: str,
    *,
    lang: str,
    has_machine: bool,
    force: bool = False,
    user_text: str = "",
    code: str = "",
) -> str:
    """Append lock/unlock block when topic or force (e.g. care label pro)."""
    text = (answer or "").rstrip()
    if not text:
        return answer
    if "교육 잠금" in text or "education locked" in text.lower() or "đào tạo khóa" in text.lower():
        return answer
    if "교육 해금" in text or "education unlocked" in text.lower() or "đã mở" in text:
        return answer
    if not force and not is_dry_or_pro_topic(user_text) and not is_dry_or_pro_topic(text):
        return answer
    block = unlock_message(lang, code=code) if has_machine else lock_message(lang)
    return f"{text}\n\n{block}"


def resolve_has_machine(user_id: str = "", channel: str = "", *, fresh: bool = True) -> bool:
    """Look up HQ profile; default False (safe). fresh=True bypasses short cache for toggle immediacy."""
    if not user_id:
        return False
    try:
        from zalo_owner_access import store_has_dry_clean_machine

        return bool(store_has_dry_clean_machine(user_id, fresh=fresh))
    except Exception:
        return False
