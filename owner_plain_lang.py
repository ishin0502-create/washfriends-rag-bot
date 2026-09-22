# -*- coding: utf-8 -*-
"""Owner-facing plain language — expand jargon across all stains (KO/VI/EN).

Not stain-specific: enzyme/oxygen/tool purpose + emergency enzyme note.
"""
from __future__ import annotations

import re
from typing import Optional


# Longer phrases first. Skip if already expanded (protect tokens).
_PROTECT_KO = (
    "효소계 세제",
    "효소제",
    "효소(프로테아제)",
    "효소(단백질 분해",
    "산소계 표백제",
    "산소표백제",
    "과탄산",
    "옥시클린",
)

_KO_PHRASE = (
    ("효소로 단백질", "단백질 얼룩 → 효소계 세제(프로테아제)"),
    ("식초로 냄새 빼기", "식초로 냄새 중화·줄이기(완전 제거 보장 아님)"),
    ("식초로 냄새", "식초로 냄새 중화·줄이기(완전 제거 보장 아님)"),
    ("식초(냄새)", "흰 식초(냄새 중화·줄이기용)"),
    ("효소·세제", "효소계 세제(프로테아제)"),
    ("효소(또는 중성)", "효소계 세제(또는 중성)"),
    ("효소(또는", "효소계 세제(또는"),
    ("효소를 바르고", "효소계 세제(라벨에 「효소/enzyme/프로테아제」)를 바르고"),
    ("효소를 바르", "효소계 세제(라벨에 「효소/enzyme/프로테아제」)를 바르"),
    ("효소세제", "효소계 세제"),
    ("효소에 ", "효소계 세제에 "),
    ("효소 금지", "효소계 세제 금지"),
    ("효소 →", "효소계 세제 →"),
    ("효소→", "효소계 세제→"),
    ("효소 ·", "효소계 세제 ·"),
    ("효소·", "효소계 세제·"),
    ("효소 30분", "효소계 세제 30분"),
    ("효소 15", "효소계 세제 15"),
    ("효소 20", "효소계 세제 20"),
    ("흰/면 산소(테스트)", "흰/면만 산소계 표백제(과탄산·옥시클린 계열 · 테스트)"),
    ("산소(흰옷만)", "산소계 표백제(과탄산·옥시클린 계열 · 흰옷만)"),
    ("산소(흰옷)", "산소계 표백제(과탄산·옥시클린 계열 · 흰옷만)"),
    ("산소(테스트)", "산소계 표백제(과탄산·옥시클린 계열 · 테스트)"),
    ("흰옷만 산소", "흰옷만 산소계 표백제(과탄산·옥시클린 계열)"),
    ("흰옷 산소", "흰옷 산소계 표백제(과탄산·옥시클린 계열)"),
    ("흰/면 산소", "흰/면 산소계 표백제(과탄산·옥시클린 계열)"),
    ("잔색만 산소", "잔색만 산소계 표백제(흰옷)"),
    ("산소 30분", "산소계 표백제 30분"),
    ("산소 15분", "산소계 표백제 15분"),
    ("산소 1~2", "산소계 표백제 1~2"),
    ("산소 1–2", "산소계 표백제 1–2"),
    ("산소·", "산소계 표백제·"),
    ("산소 →", "산소계 표백제 →"),
    ("산소→", "산소계 표백제→"),
    ("· 산소", "· 산소계 표백제"),
    ("/산소", "/산소계 표백제"),
    (" 산소 ", " 산소계 표백제 "),
    (" 산소.", " 산소계 표백제."),
    (" 산소,", " 산소계 표백제,"),
    ("산소 금지", "산소계 표백제 금지"),
)

_VI_PHRASE = (
    ("Enzyme protease", "Nước giặt/enzyme protease (ghi enzyme trên nhãn)"),
    ("enzyme protease", "nước giặt/enzyme protease (ghi enzyme trên nhãn)"),
    ("Enzyme 30", "Nước giặt enzyme 30"),
    ("Enzyme 15", "Nước giặt enzyme 15"),
    ("Enzyme ", "Nước giặt enzyme "),
    ("enzyme ", "nước giặt enzyme "),
    ("Oxy trắng", "Tẩy oxy (percarbonate / Oxi — CHỈ đồ trắng)"),
    ("oxy trắng", "tẩy oxy (percarbonate / Oxi — CHỈ đồ trắng)"),
    ("Oxy (", "Tẩy oxy ("),
    ("oxy (", "tẩy oxy ("),
    ("Nước rửa chén", "Nước rửa chén (trung tính)"),
)

_EN_PHRASE = (
    ("Enzyme 30", "Enzyme detergent (protease) 30"),
    ("Enzyme 15", "Enzyme detergent (protease) 15"),
    ("Apply enzyme", "Apply enzyme detergent (protease; label says enzyme)"),
    ("enzyme 30", "enzyme detergent (protease) 30"),
    ("Oxygen (whites)", "Oxygen bleach (percarbonate / Oxi-type — whites only)"),
    ("oxygen whites", "oxygen bleach (percarbonate / Oxi-type — whites only)"),
    ("Whites: oxygen", "Whites: oxygen bleach (percarbonate / Oxi-type)"),
    ("Dish soap", "Dish soap (neutral)"),
)


def expand_owner_jargon(text: str, lang: str = "ko") -> str:
    """Expand short chem jargon for beginner franchise owners. Idempotent-ish."""
    if not text:
        return text
    if lang == "vi":
        pairs = _VI_PHRASE
        protect = ("nước giặt enzyme", "tẩy oxy", "percarbonate")
    elif lang == "en":
        pairs = _EN_PHRASE
        protect = ("enzyme detergent", "oxygen bleach", "percarbonate")
    else:
        pairs = _KO_PHRASE
        protect = _PROTECT_KO

    # Avoid double-expanding already-clear spans
    slots: list[str] = []

    def _hold(m: re.Match) -> str:
        slots.append(m.group(0))
        return f"\x00J{len(slots) - 1}\x00"

    out = text
    if protect:
        pat = "|".join(re.escape(p) for p in sorted(protect, key=len, reverse=True))
        out = re.sub(pat, _hold, out, flags=re.I)
    for a, b in pairs:
        if a in out:
            out = out.replace(a, b)
    for i, s in enumerate(slots):
        out = out.replace(f"\x00J{i}\x00", s)
    if lang == "ko":
        # Standalone 효소 / 산소 left in titles (not already expanded)
        out = re.sub(r"(?<![가-힣계])효소(?![가-힣/」\(계])", "효소계 세제(프로테아제)", out)
        out = re.sub(r"(?<![가-힣계])산소(?![가-힣표])", "산소계 표백제(과탄산·옥시클린 계열)", out)
        out = re.sub(
            r"주방세제(?!\(식기용)",
            "주방세제(식기용·중성)",
            out,
        )
        # De-dupe accidental double oxygen wraps
        out = re.sub(
            r"산소계 표백제\(([^)]+)\)\(과탄산[^)]*\)",
            r"산소계 표백제(\1)",
            out,
        )
        out = out.replace("효소계 세제계 세제", "효소계 세제")
        out = out.replace(
            "효소계 세제(라벨에 「효소/enzyme/프로테아제」)세제",
            "효소계 세제(라벨에 「효소/enzyme/프로테아제」)",
        )
    return out


# Tool display: name → short purpose (beginner)
TOOL_PURPOSE = {
    "ko": {
        "니트릴 장갑": "약품·얼룩 다룰 때 손 보호",
        "니트릴 장갑(PPE)": "약품·얼룩 다룰 때 손 보호",
        "흰 면 천 여러 장": "약을 묻혀 찍어 빼기(직접 붓지 않기)",
        "흰 천·흡수지": "약을 묻혀 찍어 빼기",
        "타이머(핸드폰 OK)": "담금·대기 시간 재기",
        "타이머": "담금·대기 시간 재기",
        "연질 스포팅 솔": "얼룩만 살살 두드릴 때(세게 문지르기용 아님)",
        "경질 스포팅 솔": "흙·밑창 등 거친 면만(섬세 원단 금지)",
        "초연질 솔·스펀지": "실크·울·단백질 얼룩용 아주 부드러운 솔",
        "담금통·침지 용기": "약을 희석해 옷을 담가 두는 대야/통",
        "담금통": "옷을 담가 두는 대야/통",
        "분무기(약마다 따로·겉에 이름·비율 쓰기)": "희석액을 뿌릴 때(약마다 병 따로)",
        "분무기": "희석액을 뿌릴 때(약마다 병 따로)",
        "세탁망": "얇은 옷·커튼 등을 세탁기에서 보호",
        "효소세제": "단백질 얼룩용(라벨에 효소/enzyme/프로테아제) — 산소계·알칼리계와 구분",
        "효소계 세제(프로테아제·라벨에 효소/enzyme)": "단백질 얼룩용 — 왜: 단백질을 잘라 빼기 쉽게",
        "효소계 세제(프로테아제)": "단백질 얼룩용 — 왜: 단백질을 잘라 빼기 쉽게",
        "흰 식초": "탄닌·냄새 중화·줄이기용(식용 식초 약 5%, 보통 식초1:물4)",
        "흰 식초(냄새 중화·줄이기용)": "냄새를 줄이는 용도(완전 제거 보장 아님)",
        "식초(냄새)": "냄새 중화·줄이기용(완전 제거 보장 아님)",
        "산소(흰옷)": "흰옷 잔색용 산소계 표백제(과탄산·옥시클린 계열)",
        "산소표백제(흰옷만)": "흰옷 잔색용(과탄산·옥시클린 계열)",
        "산소표백제 분말(과탄산나트륨)": "흰옷 잔색용 가루 표백",
        "산소계 표백제(흰옷만·과탄산)": "흰옷 잔색용 — 락스(염소)와 다름",
        "중성세제(실크·울)": "실크·울용 약한 세제(워시프렌즈 중성 권장)",
        "주방세제": "기름·오일 전처리(식기용·중성)",
        "담금통(옷을 담그는 대야)": "약을 희석해 옷을 담가 두는 통",
        "베이킹소다": "냄새 흡착·약알칼리(페이스트로 바름)",
    },
    "vi": {
        "Găng nitrile": "Bảo vệ tay khi dùng hóa chất",
        "Khăn trắng": "Thấm hóa chất để chấm (không đổ trực tiếp)",
        "Hẹn giờ": "Đo thời gian ngâm",
        "Bàn chải spotting mềm": "Gõ nhẹ vết — không chà mạnh",
        "Chậu ngâm / thùng ngâm": "Chậu để ngâm áo với dung dịch",
        "Enzyme": "Nước giặt/enzyme (ghi enzyme trên nhãn) — vết protein",
        "Giấm trắng": "Tannin/mùi — thường giấm 1 : nước 4",
        "Oxy (áo trắng)": "Tẩy oxy cho đồ trắng (percarbonate)",
        "Nước rửa chén": "Khử dầu (trung tính)",
        "Baking soda": "Hút mùi (làm paste)",
    },
    "en": {
        "Nitrile gloves": "Hand protection with chemicals",
        "White cloths": "Blot chem on cloth — do not pour neat on fabric",
        "Timer": "Time soaks / waits",
        "Soft spotting brush": "Gentle tapping on stain — not hard scrubbing",
        "Soak basin": "Basin to soak garment in diluted chem",
        "Enzyme detergent": "Protein stains — label says enzyme/protease",
        "White vinegar": "Tannin/odor — usually vinegar 1 : water 4",
        "Oxygen (whites)": "Oxygen bleach for whites (percarbonate / Oxi-type)",
        "Dish soap": "Grease pre-treat (neutral)",
        "Baking soda": "Odor absorb (as a paste)",
    },
}


def tool_line_with_purpose(name: str, lang: str = "ko") -> str:
    name = (name or "").strip()
    if not name:
        return ""
    purpose_map = TOOL_PURPOSE.get(lang) or TOOL_PURPOSE["ko"]
    purpose = purpose_map.get(name)
    if not purpose:
        # fuzzy: match if name startswith a known key
        for k, v in purpose_map.items():
            if name.startswith(k) or k in name:
                purpose = v
                break
    if purpose:
        return f"{name} — {purpose}"
    return name


# Protein / enzyme-using stains for emergency digest tip
ENZYME_TIP_STAINS = frozenset({
    "S_FISH_SAUCE",
    "S_SHRIMP_PASTE",
    "S_VN_NUOC_CHAM",
    "S_BLOOD_FRESH",
    "S_BLOOD_DRY",
    "S_MILK",
    "S_MILK_COFFEE",
    "S_EGG",
    "S_BABY_FORMULA",
    "S_SWEAT_FRESH",
    "S_SWEAT_YELLOW",
    "S_VOMIT",
    "S_URINE",
    "S_FECES",
    "S_SOY_SAUCE",
    "S_KIMCHI",
    "S_COLLAR_STAIN",
    "S_MAYO",
    "S_CHOCOLATE",
    "S_BBQ_SAUCE",
})

ENZYME_EMERGENCY_TIP = {
    "ko": (
        "◆ 【참고 · 응급 · 내부용】 전용 효소계 세제가 없을 때만\n"
        "표준·권장: 세탁/전처리용 효소계 세제(라벨에 「효소·enzyme·프로테아제」).\n"
        "현장 내부 참고(급할 때만 · 표준 아님 · SOP 아님):\n"
        "일부 세탁소에서는 소화제(프로테아제 함유) 몇 알을 곱게 가루 내어 "
        "세제와 섞어 쓰기도 합니다.\n"
        "· 권장 아님 · 용량·성분이 들쭉날쭉 · 구석 테스트 필수 · 매니저 확인\n"
        "· 내부 참고만 — 손님에게 이 변통 방법을 설명·고지하지 마세요\n"
        "· 가능하면 정식 효소계 세제로 교체"
    ),
    "vi": (
        "◆ 【Tham khảo · khẩn · NỘI BỘ】 Chỉ khi hết nước giặt enzyme\n"
        "Chuẩn: nước giặt enzyme (nhãn enzyme/protease).\n"
        "Ghi chú nội bộ (khẩn · KHÔNG phải SOP):\n"
        "Một số tiệm nghiền vài viên thuốc tiêu hóa (có protease) trộn với xà phòng.\n"
        "· Không khuyến nghị · liều không ổn định · thử góc · hỏi quản lý\n"
        "· Chỉ nội bộ — KHÔNG giải thích cách này cho khách\n"
        "· Ưu tiên mua enzyme đúng chuẩn"
    ),
    "en": (
        "◆ 【Reference · emergency · INTERNAL】 Only if enzyme detergent is unavailable\n"
        "Standard: laundry enzyme detergent (label: enzyme/protease).\n"
        "Internal field note (emergency only — NOT SOP):\n"
        "Some shops crush digestive tablets (protease) and mix with detergent.\n"
        "· Not recommended · unstable dose · spot-test · ask a manager\n"
        "· Internal only — do NOT explain this workaround to the guest\n"
        "· Switch to proper enzyme detergent ASAP"
    ),
}


def wants_enzyme_emergency_tip(sid: str, graph: Optional[dict] = None) -> bool:
    sid = str(sid or "")
    if sid in ENZYME_TIP_STAINS:
        return True
    if not isinstance(graph, dict):
        return False
    for c in graph.get("chemicals") or []:
        code = ""
        if isinstance(c, dict):
            code = str(c.get("code") or c.get("id") or "").upper()
        elif isinstance(c, str):
            code = c.upper()
        if code in {"E1", "E2", "E3"}:
            return True
    proto = graph.get("protocol") if isinstance(graph.get("protocol"), dict) else {}
    for s in proto.get("steps") or []:
        if isinstance(s, dict) and str(s.get("chem") or "").upper() in {"E1", "E2", "E3"}:
            return True
    return False


def block_enzyme_emergency_tip(sid: str, lang: str, graph: Optional[dict] = None) -> str:
    if not wants_enzyme_emergency_tip(sid, graph):
        return ""
    lang = lang if lang in ENZYME_EMERGENCY_TIP else "ko"
    return ENZYME_EMERGENCY_TIP[lang]
