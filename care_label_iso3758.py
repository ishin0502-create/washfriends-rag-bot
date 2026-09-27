# -*- coding: utf-8 -*-
"""ISO 3758:2023 care-label symbols (32) + wet-laundry shop actions.

Used to enrich Vision care-label replies. Does NOT invent dry-machine PROG
numbers — professional care unlock is gated separately.
"""
from __future__ import annotations

from typing import Any, Optional

# id → category, symbol hint, KO/EN/VI names, frequency
SYMBOLS: dict[int, dict[str, Any]] = {
    1: {"cat": "wash", "hint": "tub+40", "freq": "high",
        "ko": "일반 세탁 40°C", "en": "Normal wash 40°C", "vi": "Giặt thường 40°C"},
    2: {"cat": "bleach", "hint": "triangle+X", "freq": "high",
        "ko": "표백 금지", "en": "Do not bleach", "vi": "Không được tẩy"},
    3: {"cat": "dry", "hint": "square+circle+dot1", "freq": "high",
        "ko": "텀블 건조 저온", "en": "Tumble dry low", "vi": "Sấy máy nhiệt thấp"},
    4: {"cat": "iron", "hint": "iron+dot2", "freq": "high",
        "ko": "중온 다림질 150°C", "en": "Iron medium 150°C", "vi": "Ủi nhiệt trung bình 150°C"},
    5: {"cat": "wash", "hint": "tub+60", "freq": "high",
        "ko": "일반 세탁 60°C", "en": "Normal wash 60°C", "vi": "Giặt thường 60°C"},
    6: {"cat": "pro", "hint": "circle+P", "freq": "high",
        "ko": "드라이클리닝 P", "en": "Dry clean P", "vi": "Giặt khô P"},
    7: {"cat": "wash", "hint": "tub+30", "freq": "high",
        "ko": "일반 세탁 30°C", "en": "Normal wash 30°C", "vi": "Giặt thường 30°C"},
    8: {"cat": "dry", "hint": "square+circle+X", "freq": "high",
        "ko": "텀블 건조 금지", "en": "Do not tumble dry", "vi": "Cấm sấy máy"},
    9: {"cat": "wash", "hint": "tub+X", "freq": "high",
        "ko": "물세탁 금지", "en": "Do not wash", "vi": "Cấm giặt"},
    10: {"cat": "pro", "hint": "circle+F", "freq": "high",
         "ko": "드라이클리닝 F", "en": "Dry clean F", "vi": "Giặt khô F"},
    11: {"cat": "iron", "hint": "iron+dot3", "freq": "med",
         "ko": "고온 다림질 200°C", "en": "Iron high 200°C", "vi": "Ủi nhiệt cao 200°C"},
    12: {"cat": "iron", "hint": "iron+dot1", "freq": "med",
         "ko": "저온 다림질 110°C", "en": "Iron low 110°C", "vi": "Ủi nhiệt thấp 110°C"},
    13: {"cat": "bleach", "hint": "triangle+slash", "freq": "med",
         "ko": "산소 표백만 가능", "en": "Non-chlorine bleach only", "vi": "Chỉ tẩy bằng oxy"},
    14: {"cat": "wash", "hint": "tub+40+line1", "freq": "med",
         "ko": "약한 세탁 40°C", "en": "Gentle wash 40°C", "vi": "Giặt nhẹ 40°C"},
    15: {"cat": "dry", "hint": "square+circle+dot2", "freq": "med",
         "ko": "텀블 건조 보통", "en": "Tumble dry normal", "vi": "Sấy máy bình thường"},
    16: {"cat": "pro", "hint": "circle+P+underline", "freq": "med",
         "ko": "드라이클리닝 P 약하게", "en": "Dry clean P mild", "vi": "Giặt khô P nhẹ"},
    17: {"cat": "iron", "hint": "iron+X", "freq": "med",
         "ko": "다림질 금지", "en": "Do not iron", "vi": "Không được ủi"},
    18: {"cat": "dry", "hint": "square+line+slash", "freq": "med",
         "ko": "그늘 걸어 건조", "en": "Line dry in shade", "vi": "Phơi trong bóng râm"},
    19: {"cat": "wash", "hint": "tub+30+line2", "freq": "med",
         "ko": "매우 약한 세탁 30°C", "en": "Very gentle wash 30°C", "vi": "Giặt rất nhẹ 30°C"},
    20: {"cat": "bleach", "hint": "triangle empty", "freq": "med",
         "ko": "모든 표백 가능", "en": "Any bleach allowed", "vi": "Được tẩy tất cả"},
    21: {"cat": "pro", "hint": "circle+F+underline", "freq": "low",
         "ko": "드라이클리닝 F 약하게", "en": "Dry clean F mild", "vi": "Giặt khô F nhẹ"},
    22: {"cat": "pro", "hint": "circle+W", "freq": "low",
         "ko": "웨트클리닝 W", "en": "Wet clean W", "vi": "Giặt ướt W"},
    23: {"cat": "pro", "hint": "circle+W+underline", "freq": "low",
         "ko": "웨트클리닝 W 약하게", "en": "Wet clean W mild", "vi": "Giặt ướt W nhẹ"},
    24: {"cat": "pro", "hint": "circle+W+double", "freq": "low",
         "ko": "웨트클리닝 W 매우 약하게", "en": "Wet clean W very mild", "vi": "Giặt ướt W rất nhẹ"},
    25: {"cat": "pro", "hint": "circle+X", "freq": "low",
         "ko": "드라이클리닝 금지", "en": "Do not dry clean", "vi": "Không được giặt khô"},
    26: {"cat": "wash", "hint": "tub+hand", "freq": "low",
         "ko": "손세탁 40°C 이하", "en": "Hand wash only ≤40°C", "vi": "Chỉ giặt tay ≤40°C"},
    27: {"cat": "wash", "hint": "tub+95", "freq": "low",
         "ko": "일반 세탁 95°C", "en": "Normal wash 95°C", "vi": "Giặt thường 95°C"},
    28: {"cat": "dry", "hint": "square+hline", "freq": "low",
         "ko": "눕혀 건조", "en": "Dry flat", "vi": "Phơi phẳng"},
    29: {"cat": "dry", "hint": "square+vline", "freq": "low",
         "ko": "걸어 건조", "en": "Line dry", "vi": "Phơi treo"},
    30: {"cat": "dry", "hint": "square+3vline", "freq": "low",
         "ko": "물기 제거 후 걸어 건조", "en": "Drip dry", "vi": "Phơi nhỏ giọt"},
    31: {"cat": "wash", "hint": "tub+50", "freq": "low",
         "ko": "일반 세탁 50°C", "en": "Normal wash 50°C", "vi": "Giặt thường 50°C"},
    32: {"cat": "wash", "hint": "tub+70", "freq": "low",
         "ko": "일반 세탁 70°C", "en": "Normal wash 70°C", "vi": "Giặt thường 70°C"},
}

# Wet-shop action text (no Realstar PROG). Keys match inferred symbol ids.
WET_ACTIONS: dict[int, dict[str, str]] = {
    1: {"ko": "온수 40°C · 일반 코스", "en": "40°C · normal cycle", "vi": "40°C · chu trình thường"},
    2: {"ko": "🚫 표백제 사용 금지 · 세제만", "en": "🚫 No bleach · detergent only", "vi": "🚫 Cấm tẩy · chỉ xà phòng"},
    3: {"ko": "건조기 저온(≤60°C)", "en": "Tumble low (≤60°C)", "vi": "Sấy thấp (≤60°C)"},
    4: {"ko": "다리미 약 150°C · 소재 확인 후", "en": "Iron ~150°C · check fabric", "vi": "Ủi ~150°C · kiểm vai"},
    5: {"ko": "고온 60°C · 일반 (흰/타월 등)", "en": "60°C · normal (whites/towels)", "vi": "60°C · thường (trắng/khăn)"},
    7: {"ko": "냉수/미온 30°C · 일반 회전", "en": "Cold/warm 30°C · normal", "vi": "Lạnh/ấm 30°C · thường"},
    8: {"ko": "🚫 건조기 금지 · 자연 건조", "en": "🚫 No tumble · air dry", "vi": "🚫 Cấm sấy máy · phơi"},
    9: {"ko": "🚫 세탁기 투입 금지", "en": "🚫 Do not put in washer", "vi": "🚫 Cấm bỏ máy giặt"},
    11: {"ko": "다리미 약 200°C (면·마)", "en": "Iron ~200°C (cotton/linen)", "vi": "Ủi ~200°C (cotton/linen)"},
    12: {"ko": "다리미 약 110°C · 스팀 주의 · 천 덮고", "en": "Iron ~110°C · no/low steam · cloth", "vi": "Ủi ~110°C · hạn chế hơi · lót vải"},
    13: {"ko": "⚠️ 염소(락스) 금지 · 산소계만", "en": "⚠️ No chlorine · oxygen only", "vi": "⚠️ Cấm chlorine · chỉ oxy"},
    14: {"ko": "섬세/약탈 · 40°C · ⚠️ 과탈수 주의", "en": "Delicate · 40°C · ⚠️ gentle spin", "vi": "Nhẹ · 40°C · ⚠️ vắt nhẹ"},
    15: {"ko": "건조기 보통(≤80°C)", "en": "Tumble medium (≤80°C)", "vi": "Sấy vừa (≤80°C)"},
    17: {"ko": "🚫 다리미·프레스·스팀 금지", "en": "🚫 No iron/press/steam", "vi": "🚫 Cấm ủi/hơi"},
    18: {"ko": "그늘에 걸어 건조 (직사광선 금지)", "en": "Line dry in shade", "vi": "Phơi treo bóng râm"},
    19: {"ko": "울/섬세 · 30°C · 약탈수 ≤600rpm · ⚠️ 초급 주의",
         "en": "Wool/delicate · 30°C · spin ≤600 · ⚠️ beginner",
         "vi": "Len/nhẹ · 30°C · vắt ≤600 · ⚠️ mới"},
    20: {"ko": "염소·산소 표백 가능 (원단·색상 확인)", "en": "Any bleach OK (check color)", "vi": "Được tẩy (kiểm màu)"},
    26: {"ko": "⚠️ 기계 금지 · 미온수+중성 · 주물러 · 비틀지 말 것",
         "en": "⚠️ No machine · lukewarm+mild · squeeze gently · no wring",
         "vi": "⚠️ Cấm máy · ấm nhẹ+trung tính · vò nhẹ · không vặn"},
    27: {"ko": "삶기/고온 위생 코스 (업소)", "en": "Boil/sanitize cycle", "vi": "Chu trình sát trùng cao"},
    28: {"ko": "평건 (니트/울 — 걸면 늘어남) ⚠️", "en": "Dry flat (knit/wool) ⚠️", "vi": "Phơi phẳng (len) ⚠️"},
    29: {"ko": "옷걸이 걸어 자연 건조", "en": "Hang to dry", "vi": "Phơi treo"},
    30: {"ko": "탈수 없이 drip · ⚠️ 탈수기 금지", "en": "Drip dry · ⚠️ no spin", "vi": "Phơi nhỏ giọt · ⚠️ cấm vắt"},
    31: {"ko": "온수 50°C · 일반", "en": "50°C · normal", "vi": "50°C · thường"},
    32: {"ko": "고온 70°C · 일반 (작업복 등)", "en": "70°C · normal (workwear)", "vi": "70°C · thường"},
}


def _lang_key(lang: str) -> str:
    if lang == "ko":
        return "ko"
    if lang == "en":
        return "en"
    return "vi"


def name_for(symbol_id: int, lang: str = "vi") -> str:
    row = SYMBOLS.get(symbol_id) or {}
    return str(row.get(_lang_key(lang)) or row.get("en") or "")


def action_for(symbol_id: int, lang: str = "vi") -> str:
    row = WET_ACTIONS.get(symbol_id) or {}
    return str(row.get(_lang_key(lang)) or row.get("en") or "")


def infer_symbol_ids_from_label(label: dict) -> list[int]:
    """Map Vision structured care-label JSON → symbol ids (best effort)."""
    if not isinstance(label, dict):
        return []
    ids: list[int] = []
    wash = label.get("wash") if isinstance(label.get("wash"), dict) else {}
    bleach = label.get("bleach") if isinstance(label.get("bleach"), dict) else {}
    dry = label.get("dry") if isinstance(label.get("dry"), dict) else {}
    iron = label.get("iron") if isinstance(label.get("iron"), dict) else {}
    dc = label.get("dry_clean") if isinstance(label.get("dry_clean"), dict) else {}

    if wash.get("do_not_wash"):
        ids.append(9)
    elif wash.get("hand_wash_only"):
        ids.append(26)
    else:
        temp = wash.get("max_temp_c")
        gentle = bool(wash.get("gentle"))
        try:
            t = int(temp) if temp is not None else None
        except (TypeError, ValueError):
            t = None
        if t == 95:
            ids.append(27)
        elif t == 70:
            ids.append(32)
        elif t == 60:
            ids.append(5)
        elif t == 50:
            ids.append(31)
        elif t == 40 and gentle:
            ids.append(14)
        elif t == 40:
            ids.append(1)
        elif t == 30 and gentle:
            ids.append(19)
        elif t == 30:
            ids.append(7)
        elif wash.get("allowed"):
            ids.append(7)  # safe default low

    if bleach.get("do_not_bleach") or bleach.get("allowed") is False:
        if bleach.get("oxygen_only"):
            ids.append(13)
        else:
            ids.append(2)
    elif bleach.get("oxygen_only"):
        ids.append(13)
    elif bleach.get("allowed"):
        ids.append(20)

    if dry.get("do_not_tumble") or dry.get("tumble_ok") is False:
        if dry.get("flat_dry"):
            ids.append(28)
        elif dry.get("shade"):
            ids.append(18)
        else:
            ids.append(8)
    elif dry.get("tumble_ok"):
        ids.append(3 if dry.get("low_heat") else 15)

    if iron.get("do_not_iron") or iron.get("allowed") is False:
        ids.append(17)
    else:
        it = iron.get("max_temp_c")
        try:
            itn = int(it) if it is not None else None
        except (TypeError, ValueError):
            itn = None
        if itn is not None:
            if itn <= 110:
                ids.append(12)
            elif itn <= 150:
                ids.append(4)
            else:
                ids.append(11)

    if dc.get("do_not_dry_clean"):
        ids.append(25)
    elif dc.get("allowed"):
        code = str(dc.get("code") or "").upper().strip()
        mild = "mild" in code or "_" in code or code.endswith("-")
        if code.startswith("W"):
            ids.append(24 if "very" in code.lower() else (23 if mild else 22))
        elif code.startswith("F"):
            ids.append(21 if mild else 10)
        elif code.startswith("P") or not code:
            ids.append(16 if mild else 6)

    # unique preserve order
    seen: set[int] = set()
    out: list[int] = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def wet_action_lines(label: dict, lang: str = "vi") -> list[str]:
    """Shop-facing action bullets from inferred symbols (wet only)."""
    lk = _lang_key(lang)
    lines: list[str] = []
    for sid in infer_symbol_ids_from_label(label):
        row = SYMBOLS.get(sid) or {}
        if row.get("cat") == "pro":
            continue  # professional block handled elsewhere
        act = action_for(sid, lang)
        nm = name_for(sid, lang)
        if act:
            if lk == "ko":
                lines.append(f"· {nm}: {act}")
            elif lk == "en":
                lines.append(f"· {nm}: {act}")
            else:
                lines.append(f"· {nm}: {act}")
    return lines


def needs_professional_care(label: dict) -> bool:
    """True if label implies dry-clean / wet-clean professional path or no-wash."""
    if not isinstance(label, dict):
        return False
    wash = label.get("wash") if isinstance(label.get("wash"), dict) else {}
    dc = label.get("dry_clean") if isinstance(label.get("dry_clean"), dict) else {}
    if wash.get("do_not_wash"):
        return True
    if dc.get("allowed") and not dc.get("do_not_dry_clean"):
        return True
    return False


def professional_code(label: dict) -> str:
    dc = label.get("dry_clean") if isinstance(label.get("dry_clean"), dict) else {}
    return str(dc.get("code") or "").upper().strip()
