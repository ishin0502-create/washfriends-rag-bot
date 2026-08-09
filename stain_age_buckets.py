# -*- coding: utf-8 -*-
"""Fresh / dried-set / hard-limit framing for stain education answers.

Uses existing chemistry only — expands thin dried_path text and steers the
owner prompt so answers cover three buckets when relevant:
  1) fresh  2) dried/set  3) harder-than-that (limits, no 100% promise)
"""
from __future__ import annotations

from typing import Literal, Optional

AgeBucket = Literal["fresh", "dried", "hard", "unknown"]

# Prefer dried_path when these cues appear (KO / VI unsigned / EN).
_HARD_KO = (
    "몇달", "몇 달", "수개월", "한달", "한 달", "두달", "두 달", "세달", "세 달",
    "두세달", "두세 달", "서너달", "서너 달", "반년", "1년", "일년", "작년", "작년에",
    "오래전", "오래 전", "아주 오래", "열고착", "이미 다림질", "이미 건조기",
    "열로 굳", "영구",
)
_DRIED_KO = (
    "마른", "마름", "말랐", "굳은", "고착", "건조된", "건조한", "어제", "그제",
    "며칠", "며칠 전", "하룻밤", "하룻 밤", "이미 말", "이미 건조",
    "오래된", "오래 된", "오래됐", "오래됐어", "오래됨",
    "예전", "예전에", "묵은", "꽤 된", "꽤된",
    "시간이 지", "시간 지", "시간이 좀 지", "지난지", "묻은지 좀",
    "기간을 알", "기간 알 수", "얼마나 됐", "얼마나 된", "언제 묻",
    "몇주", "몇 주", "수주", "지난주", "지난 주",
    "이전부터", "전부터 있",
    "지워지지 않", "안 지워", "잘 안 지워", "잘 지워지지", "지워지지 않는",
    "남아있어", "남아 있", "잔여 얼룩", "잔여얼룩",
    "빨았는데", "세탁했는데", "한번 빨", "1차 실패", "안 빠져",
)
_HARD_VI = (
    "vai thang", "nhieu thang", "nua nam", "1 nam", "mot nam", "lau roi",
    "da say", "da ui", "co dinh nhiet", "vin vien",
)
_DRIED_VI = (
    "vet kho", "da kho", "kho roi", "hom qua", "hom kia", "vai ngay",
    "qua dem", "da say khoa", "truoc day", "lau", "kho xoa", "khong het",
)
_HARD_EN = (
    "months ago", "month-old", "year-old", "years ago", "heat-set", "heat set",
    "already ironed", "already dried", "permanent", "last year",
)
_DRIED_EN = (
    "dried", "set in", "set stain", "old stain", "overnight", "yesterday",
    "few days", "days ago", "old wine", "old coffee", "aged stain",
    "weeks ago", "last week", "won't come out", "will not come out",
    "doesn't come out", "still there after wash", "previously stained",
)
_FRESH_KO = ("방금", "지금 막", "막 묻", "신선", "아직 젖", "아직 축", "방금 전")
_FRESH_VI = ("moi do", "vua do", "con uot", "con am", "tuoi")
_FRESH_EN = ("just now", "fresh", "still wet", "just spilled", "just happened")


def detect_stain_age(message: str) -> AgeBucket:
    """Classify stain age from owner question text."""
    raw = (message or "").strip()
    if not raw:
        return "unknown"
    t = raw.lower()
    # Unsigned VI for matching (strip tones + map đ→d; đ is a letter, not a tone mark)
    try:
        from unicodedata import normalize

        t_n = "".join(c for c in normalize("NFD", t) if not (0x300 <= ord(c) <= 0x36F))
        t_n = t_n.replace("đ", "d").replace("Đ", "d")
    except Exception:
        t_n = t.replace("đ", "d").replace("Đ", "d")

    if any(k in raw for k in _HARD_KO) or any(k in t_n for k in _HARD_VI) or any(k in t for k in _HARD_EN):
        return "hard"
    if any(k in raw for k in _DRIED_KO) or any(k in t_n for k in _DRIED_VI) or any(k in t for k in _DRIED_EN):
        return "dried"
    if any(k in raw for k in _FRESH_KO) or any(k in t_n for k in _FRESH_VI) or any(k in t for k in _FRESH_EN):
        return "fresh"
    return "unknown"


# Step-level dried paths (same chemistry as fresh / VI seed — longer soak / disclose).
DRIED_PATH_KO: dict[str, str] = {
    "S_RED_WINE": (
        "(1) 마른·고착 레드와인 확인. (2) 찬물만·문지르기 금지. (3) 식초 1:4 장침지 15–30분. "
        "(4) 흰/면 잔색: 산소(구석 테스트). 실크·울 산소 금지. (5) 세탁. (6) 건조 전 강광. "
        "잔색·적자색 고착 가능 — 100% 비보장 고지."
    ),
    "S_BLACK_COFFEE": (
        "(1) 마른 블랙커피. (2) 찬물 흡수(문지르기 금지). (3) 식초 1:4 장침지 15–30분. "
        "(4) 흰/면 잔색: 산소(실크·울 금지). (5) 미온 세탁(허용 시). (6) 건조 전 강광. 성공률↓ 고지."
    ),
    "S_MILK_COFFEE": (
        "(1) 마른 라떼. (2) 찬물. (3) 효소 장침지 30–45분(또는 지방 많으면 주방세제). "
        "(4) 헹굼→식초 1:4. (5) 허용 시만 산소. (6) 건조 전 강광. 단백질 고착 시 잔색 가능."
    ),
    "S_TEA": (
        "(1) 마른 차. (2) 식초 1:4 장침지. (3) 흰/면: 산소. 실크·울: 식초 약하게+중성만. "
        "(4) 세탁. (5) 건조 전 강광. 이미 건조면 성공률↓ 고지."
    ),
    "S_FRUIT_JUICE": (
        "(1) 마른 주스. (2) 식초 1:4 장침지. (3) 흰/면 산소(실크·울 금지). "
        "(4) 세탁. (5) 건조 전 강광. 유색은 산소 신중."
    ),
    "S_SOFT_DRINK": (
        "(1) 마른 당분·콜라. (2) 미온 장침지+식초 1:4. (3) 흰옷 산소. "
        "(4) 세탁. (5) 건조 전 강광. 끈적임 없앤 뒤만 건조."
    ),
    "S_WHITE_WINE_BEER": (
        "(1) 이미 황변·마른 당. (2) 식초 1:4. (3) 흰옷 짧은 산소. "
        "(4) 세탁·통풍. 오래된 당분 황변 100% 비보장."
    ),
    "S_KIMCHI": (
        "(1) 마른 김치국. (2) 찬물+주방세제(기름). (3) 식초 1:4. (4) 흰옷 산소(테스트). "
        "(5) 냄새면 식초 추가. (6) 건조 전 강광. 고추 색소 잔존 가능 고지."
    ),
    "S_KETCHUP": (
        "(1) 마른 케첩. (2) 고형 제거. (3) 미온 침지+주방세제. (4) 식초 1:4 반복. "
        "(5) 흰/면 잔색: 산소. (6) 세탁·건조 전 강광. 붉은 잔색 가능 — 100% 비보장."
    ),
    "S_TOMATO_SAUCE": (
        "(1) 마른 토마토소스. (2) 고형 제거. (3) 침지+주방세제. (4) 식초 1:4. "
        "(5) 흰옷 산소. (6) 건조 전 강광."
    ),
    "S_COOKING_OIL": (
        "(1) 마른·열고착 의심 식용유. (2) 전분 흡착 2회. (3) 주방세제/리파아제. "
        "(4) 세탁. (5) 미끄럼 없어진 뒤만 건조. 열고착이면 성공률↓ 고지."
    ),
    "S_GREASE": (
        "(1) 마른 그리즈. (2) 흡착 2회. (3) 주방세제/리파아제. (4) 세탁. "
        "(5) 미끄럼 확인 후 건조. 오래된 지방 성공률↓."
    ),
    "S_BUTTER": (
        "(1) 마른 버터. (2) 흡착→주방세제. (3) 세탁. (4) 미끄럼 확인. 열고착 고지."
    ),
    "S_MOTORBIKE_OIL": (
        "(1) 마른 오토바이용 오일. (2) 흡착→용제(환기)/주방세제 반복. "
        "(3) 세탁. (4) 미끄럼 확인. 실크·울 고온 금지. 100% 비보장."
    ),
    "S_ENGINE_OIL": (
        "(1) 마른 엔진오일. (2) 흡착→용제(환기) 다회. (3) 주방세제. (4) 세탁. "
        "(5) 미끄럼·냄새 확인. 성공률↓ 고지."
    ),
    "S_BUBBLE_TEA": (
        "(1) 마른 버블티. (2) 효소 장침지. (3) 주방세제. (4) 식초 1:4. "
        "(5) 흰옷 산소. (6) 건조 전 강광. 마른 설탕 황변 — 산소 예방."
    ),
    "S_CURRY": (
        "(1) 마른 카레/강황. (2) 주방세제. (3) 베이킹소다. (4) 흰옷 산소/짧은 UV. "
        "(5) 세탁·강광. 강황 잔색 가능 고지."
    ),
    "S_SOY_SAUCE": (
        "(1) 마른 간장. (2) 찬물+효소 장침지. (3) 식초 1:4. (4) 흰옷 산소. "
        "(5) 건조 전 강광."
    ),
    "S_FISH_SAUCE": (
        "(1) 마른 액젓. (2) 효소→식초 반복(냄새). (3) 흰옷 산소. "
        "(4) 충분히 헹굼. 냄새 잔존 가능 고지."
    ),
    "S_BBQ_SAUCE": (
        "(1) 마른 BBQ. (2) 효소 장침지→주방세제→식초→흰옷 산소. "
        "(3) 건조 전 강광. 마른 당분 황변 고지."
    ),
    "S_MAYO": (
        "(1) 마른 마요. (2) 긁기→주방세제(기름)→효소(단백질). "
        "(3) 세탁. (4) 미끄럼 확인. 순서 바꾸지 말 것."
    ),
    "S_CHOCOLATE": (
        "(1) 마른 초콜릿. (2) 긁기→찬물→효소→주방세제. (3) 흰옷 산소. "
        "(4) 건조 전 강광."
    ),
    "S_PAINT_LATEX": (
        "(1) 이미 마른 수성 페인트. (2) 약한 용제 구석 테스트+블롯 다회. "
        "(3) 주방세제. (4) 성공률↓ 고지. 유성 페인트는 별도."
    ),
}

DRIED_PATH_VI: dict[str, str] = {
    "S_RED_WINE": (
        "(1) Vet ruou do da kho. (2) Chi xa lanh — khong cha. (3) Giam 1:4 ngam 15-30 phut. "
        "(4) Trang/cotton: oxy (test). CAM oxy len/lua. (5) Giat. (6) Anh sang truoc say. "
        "Bao mau khoa — khong 100%."
    ),
    "S_BLACK_COFFEE": (
        "(1) Ca phe den kho. (2) Tham lanh. (3) Giam 1:4 ngam dai. (4) Oxy trang (khong len/lua). "
        "(5) Giat. (6) Anh sang truoc say. Bao ty le thap."
    ),
    "S_MILK_COFFEE": (
        "(1) Latte kho. (2) Enzyme ngam dai / bot rua chen. (3) Giam 1:4. (4) Oxy neu duoc. "
        "(5) Anh sang truoc say."
    ),
    "S_TEA": (
        "(1) Tra kho. (2) Giam ngam dai. (3) Oxy trang. (4) Giat. Bao ty le thap neu da say."
    ),
    "S_FRUIT_JUICE": (
        "(1) Nuoc ep kho. (2) Giam ngam. (3) Oxy trang (khong len/lua). (4) Anh sang truoc say."
    ),
    "S_SOFT_DRINK": (
        "(1) Duong kho/cola. (2) Ngam am + giam. (3) Oxy trang. (4) Het dinh moi say."
    ),
    "S_WHITE_WINE_BEER": (
        "(1) Da vang/duong kho. (2) Giam. (3) Oxy trang ngan. Bao khong 100%."
    ),
    "S_KIMCHI": (
        "(1) Kim chi kho. (2) Bot rua chen. (3) Giam. (4) Oxy trang. Bao mau ot con."
    ),
    "S_KETCHUP": (
        "(1) Ketchup kho. (2) Cao bot. (3) Ngam + bot rua chen. (4) Giam lap. "
        "(5) Oxy trang. Bao mau do con — khong 100%."
    ),
    "S_TOMATO_SAUCE": (
        "(1) Sot ca kho. (2) Cao. (3) Ngam + bot rua chen. (4) Giam. (5) Oxy trang."
    ),
    "S_COOKING_OIL": (
        "(1) Dau an kho. (2) Bot hut 2 lan. (3) Bot rua chen/lipase. (4) Het nhon moi say. Bao thap neu khoa nhiet."
    ),
    "S_GREASE": (
        "(1) Mo kho. (2) Hut 2 lan. (3) Bot rua chen. (4) Het nhon moi say."
    ),
    "S_BUTTER": (
        "(1) Bo kho. (2) Hut → bot rua chen. (3) Kiem nhon. Bao khoa nhiet."
    ),
    "S_MOTORBIKE_OIL": (
        "(1) Dau nhot kho. (2) Hut → dung moi (thong gio)/bot rua chen. (3) Giat. Bao khong 100%."
    ),
    "S_ENGINE_OIL": (
        "(1) Dau dong co kho. (2) Hut → dung moi lap. (3) Bot rua chen. Bao ty le thap."
    ),
    "S_BUBBLE_TEA": (
        "(1) Tra sua kho. (2) Enzyme dai. (3) Bot rua chen. (4) Giam. (5) Oxy trang. Phong vang duong."
    ),
    "S_CURRY": (
        "(1) Ca ri kho. (2) Bot rua chen. (3) Baking soda. (4) Oxy/UV. Bao mau nghe con."
    ),
    "S_SOY_SAUCE": (
        "(1) Tuong kho. (2) Enzyme dai. (3) Giam. (4) Oxy trang. Anh sang truoc say."
    ),
    "S_FISH_SAUCE": (
        "(1) Mam kho. (2) Enzyme → giam lap (mui). (3) Oxy trang. Bao mui con."
    ),
    "S_BBQ_SAUCE": (
        "(1) BBQ kho. (2) Enzyme → bot rua chen → giam → oxy. Bao vang duong."
    ),
    "S_MAYO": (
        "(1) Mayo kho. (2) Cao → bot rua chen → enzyme. (3) Het nhon. Giu thu tu dau→protein."
    ),
    "S_CHOCOLATE": (
        "(1) Socola kho. (2) Cao → lanh → enzyme → bot rua chen. (3) Oxy trang."
    ),
    "S_PAINT_LATEX": (
        "(1) Son nuoc da kho. (2) Dung moi nhe + blot lap. (3) Bot rua chen. Bao ty le thap."
    ),
}

# Merge education parity v5 (remaining stains + VI diacritic upgrades + VN specialty).
try:
    from education_parity_v5 import (
        CANON_DRIED_PATH_VI,
        EXTRA_DRIED_PATH_KO,
        EXTRA_DRIED_PATH_VI,
    )

    DRIED_PATH_KO.update(EXTRA_DRIED_PATH_KO)
    DRIED_PATH_VI.update(CANON_DRIED_PATH_VI)
    DRIED_PATH_VI.update(EXTRA_DRIED_PATH_VI)
except Exception:
    pass
try:
    from education_gaps_v7 import (
        DRIED_CHILI_KO,
        DRIED_CHILI_VI,
        DRIED_IODINE_KO,
        DRIED_IODINE_VI,
    )

    DRIED_PATH_KO["S_IODINE"] = DRIED_IODINE_KO
    DRIED_PATH_KO["S_CHILI"] = DRIED_CHILI_KO
    DRIED_PATH_VI["S_IODINE"] = DRIED_IODINE_VI
    DRIED_PATH_VI["S_CHILI"] = DRIED_CHILI_VI
except Exception:
    pass
try:
    from education_gaps_v8 import DRIED_BY_ID_V8

    for _sid, (_ko, _vi) in DRIED_BY_ID_V8.items():
        DRIED_PATH_KO[_sid] = _ko
        DRIED_PATH_VI[_sid] = _vi
except Exception:
    pass


LIMIT_KO = (
    "한계(수개월·열고착·이미 다림질/건조기·얇은 실크·가정 강처리 실패): "
    "같은 약 무한 반복 금지. dried 경로 1회+rescue 후 잔색·전문·클레임 고지. 100% 약속 금지."
)
LIMIT_VI = (
    "Gioi han (nhieu thang / khoa nhiet / da ui-say / lua mong / da xu ly manh that bai): "
    "CAM lap vo han. 1 lan dried + rescue roi bao gioi han. CAM hua 100%."
)
LIMIT_EN = (
    "Harder than dried (months / heat-set / already ironed-dried / sheer silk / failed harsh home try): "
    "do not infinite-repeat. One dried path + rescue, then disclose limits. Never promise 100%."
)

# Dried/hard soak window — overrides fresh protocol 5–15 for vinegar-family soaks.
DRIED_SOAK_LO = 15
DRIED_SOAK_HI = 30

# Graph success_rate_* is often fresh-biased ("1시간 내: 양호"). Override when dried/hard.
# Do not embed the forbidden phrase itself — LLM may echo it.
SUCCESS_RATE_DRIED_KO = (
    "이미 마른·고착: 성공률 낮음~중간. 잔색·완전 제거 비보장. "
    "신선·즉시처리용 단시간 성공률 문구는 쓰지 말 것."
)
SUCCESS_RATE_HARD_KO = (
    "수개월·열고착: 성공률 낮음. dried 경로 1회 후 한계 고지. "
    "100% 불가. 신선·즉시처리용 단시간 성공률 문구 금지."
)
SUCCESS_RATE_DRIED_VI = (
    "Da kho: ty le thap-TB. Bao khong sach 100%. CAM ty le tuoi/ngan gio."
)
SUCCESS_RATE_HARD_VI = (
    "Nhieu thang/khoa nhiet: ty le thap. 1 lan dried + gioi han. CAM 100%. CAM ty le tuoi."
)
SUCCESS_RATE_DRIED_EN = (
    "Already dried/set: low–fair success. Residual color possible. "
    "Do not quote fresh short-window success rates."
)
SUCCESS_RATE_HARD_EN = (
    "Months/heat-set: low success. One dried path then disclose limits. "
    "No 100%. Do not quote fresh short-window success rates."
)


def _min_label(lo: int, hi: int) -> tuple[str, str, str]:
    if lo == hi:
        return f"{lo}분", f"{lo} phut", f"{lo} min"
    return f"{lo}–{hi}분", f"{lo}-{hi} phut", f"{lo}-{hi} min"


def _rewrite_soak_tools(tools: list, lo: int, hi: int) -> list:
    """Force timer/soak howto to dried minutes (no fresh 5–15 conflict)."""
    if not isinstance(tools, list):
        return tools
    min_ko, min_vi, min_en = _min_label(lo, hi)
    out = []
    for t in tools:
        if not isinstance(t, dict):
            out.append(t)
            continue
        t2 = dict(t)
        tid = str(t2.get("id") or "")
        if tid == "T_TIMER":
            t2["use_for_ko"] = (
                f"마른·고착 기준 침지 {min_ko}. 타이머를 {min_ko}에 맞추고, "
                f"울리면 즉시 찬물 헹굼. 감시 없이 밤새 방치 금지. "
                f"(신선 SOP 5–15분을 쓰지 말 것.)"
            )
            t2["use_for_vi"] = (
                f"Vet kho: ngam {min_vi}. Hen gio {min_vi}; het gio → xa lanh. "
                f"CAM phut tuoi 5-15."
            )
            t2["use_for_en"] = (
                f"Dried/set soak {min_en}. Timer {min_en}; rinse cold when it rings. "
                f"Do not use fresh 5–15 min."
            )
        elif tid == "T_SOAK_BIN":
            t2["use_for_ko"] = (
                f"(4)약품 희석액을 통에 만들어 {min_ko} 담근다(마른·고착용). "
                f"통에 약 이름·비율 확인. 신선 5–15분 경로 금지."
            )
            t2["use_for_vi"] = (
                f"Pha dung dich (4), ngam {min_vi} (vet kho). CAM phut tuoi 5-15."
            )
            t2["use_for_en"] = (
                f"Mix (4) chem in bin; soak {min_en} for dried/set. Do not use fresh 5–15 min."
            )
        out.append(t2)
    return out


def _override_protocol_minutes(proto: dict, lo: int, hi: int) -> dict:
    """Mutate protocol.steps soak minutes + drop fresh wording."""
    if not isinstance(proto, dict):
        return proto
    p2 = dict(proto)
    steps = []
    for s in list(p2.get("steps") or []):
        if not isinstance(s, dict):
            steps.append(s)
            continue
        s2 = dict(s)
        chem = str(s2.get("chem") or "").upper()
        soak = bool(s2.get("soak"))
        # Extend vinegar/surfactant soaks; leave oxygen bleach windows alone
        if soak and chem not in ("B1", "B2"):
            s2["minutes_lo"] = lo
            s2["minutes_hi"] = hi
        for key, val in list(s2.items()):
            if isinstance(val, str) and val:
                s2[key] = (
                    val.replace("5–15", f"{lo}–{hi}")
                    .replace("5-15", f"{lo}-{hi}")
                    .replace("신선 여부", "마른·고착")
                    .replace("·신선", "·마른·고착")
                )
        steps.append(s2)
    p2["steps"] = steps
    return p2


def _frame_for(bucket: AgeBucket) -> dict[str, str]:
    if bucket == "fresh":
        return {
            "age_frame_ko": (
                "age_bucket=fresh. 본문은 fresh_path_ko(+protocol.steps). "
                "마름 분기는 dried_path_ko를 (6)·[성공률]에 한 줄. limit_path_ko는 필요 시만."
            ),
            "age_frame_vi": (
                "age_bucket=fresh. Body = fresh_path_vi(+protocol). "
                "Dried: one line from dried_path_vi in aftercare/success."
            ),
            "age_frame_en": (
                "age_bucket=fresh. Body = fresh_path_en(+protocol). "
                "Mention dried_path briefly in aftercare/success."
            ),
        }
    if bucket == "dried":
        return {
            "age_frame_ko": (
                "age_bucket=dried. 본문 축=dried_path_ko(단계·분). "
                "protocol.steps는 약 순서만 — 신선 분(5–15분)을 dried 장침지보다 우선하지 말 것. "
                "신선이면 fresh_path는 「신선 시」한 줄만. "
                "탄닌·색소(와인·커피 등): 문지르기·솔 문지르기 금지 — 흰 천 흡수·식초만. "
                "원단·두께 미확인이면 Cap1·표백 보류로 진행(확인 후 조정). Cap을 얇다고만 단정하지 말 것. "
                "[성공률·고지]에 반드시 「1차 실패 후」+ rescue_disclose_ko, "
                "(6) 또는 그 다음 줄에 rescue_2nd_ko의 「2차:」로 시작하는 문장. "
                "why에 「즉시 찬물만」으로 끝내지 말 것(이미 마른·세탁 실패 케이스)."
            ),
            "age_frame_vi": (
                "age_bucket=dried. Body = dried_path_vi (phút dài). "
                "protocol chỉ thứ tự — không ưu tiên phút tươi. "
                "Tannin: CẤM chà. "
                "[Tỷ lệ] phải có 「sau lần 1 thất bại」+ rescue_disclose_vi, "
                "và câu bắt đầu 「Lần 2:」 từ rescue_2nd_vi. "
                "Không kết thúc why bằng chỉ 「xử lý nước lạnh ngay」."
            ),
            "age_frame_en": (
                "age_bucket=dried. Body = dried_path (longer soak). "
                "Protocol = chem order only; do not prefer fresh minutes. "
                "Tannin: no scrubbing. "
                "In success block: after 1st fail + rescue_disclose; include 2nd-pass line from rescue_2nd."
            ),
        }
    if bucket == "hard":
        return {
            "age_frame_ko": (
                "age_bucket=hard. path_lock_ko·limit_path_ko를 (1)에 먼저. "
                "본문=dried_path_ko 1회만, 침지 soak_minutes_ko(15–30). "
                "protocol/fresh 5–15분·「신선 여부」·「1시간 내 양호」 금지. "
                "탄닌 문지르기 금지. 100% 약속 금지. rescue_disclose 필수."
            ),
            "age_frame_vi": (
                "age_bucket=hard. Lead limit_path_vi. Body dried once, soak 15-30. "
                "CAM phut tuoi 5-15. No 100%."
            ),
            "age_frame_en": (
                "age_bucket=hard. Lead limit_path. Body dried once, soak 15–30. "
                "No fresh 5–15. No 100%."
            ),
        }
    # unknown — dual teach
    return {
        "age_frame_ko": (
            "age_bucket=unknown. (1)에서 신선/마름을 한 줄로 갈라 확인. "
            "본문 SOP는 fresh_path_ko(+protocol). "
            "반드시 「마른·고착이면」dried_path_ko 단계를 이어서 쓰고, "
            "limit_path_ko·rescue_disclose로 한계를 고지. "
            "신선만 길게·마름 생략 금지."
        ),
        "age_frame_vi": (
            "age_bucket=unknown. In (1) split tuoi/kho one line. "
            "Body = fresh_path_vi(+protocol). Then 「neu kho」 dried_path_vi steps. "
            "End with limit_path_vi + rescue_disclose. Do not omit dried."
        ),
        "age_frame_en": (
            "age_bucket=unknown. In (1) ask fresh vs dried briefly. "
            "Body = fresh_path(+protocol). Then dried_path steps for set stains. "
            "Disclose limit_path + rescue. Do not omit dried branch."
        ),
    }


def apply_stain_age_buckets(
    graph: dict,
    user_message: str = "",
    entities: Optional[dict] = None,
) -> dict:
    """Attach age bucket + enrich dried/limit paths on stain_context."""
    if not isinstance(graph, dict):
        return graph
    sc = graph.get("stain_context")
    if not isinstance(sc, dict) or not sc:
        return graph
    if (
        graph.get("item_wash_mode")
        or graph.get("specialty_item_care")
        or sc.get("item_wash_mode")
        or sc.get("group") == "item_care"
    ):
        return graph

    sid = str(sc.get("id") or "").strip()
    if not sid.startswith("S_"):
        return graph

    entities = entities or {}
    bucket: AgeBucket = entities.get("stain_age") or detect_stain_age(
        user_message or str(entities.get("_raw") or "")
    )
    # Blood: keep dedicated SOP ids when already remapped
    if sid == "S_BLOOD_DRY" and bucket == "unknown":
        bucket = "dried"
    if sid == "S_BLOOD_FRESH" and bucket == "unknown":
        # leave unknown → dual frame still useful
        pass

    sc2 = dict(sc)
    if sid in DRIED_PATH_KO:
        sc2["dried_path_ko"] = DRIED_PATH_KO[sid]
    if sid in DRIED_PATH_VI:
        sc2["dried_path_vi"] = DRIED_PATH_VI[sid]

    sc2["limit_path_ko"] = LIMIT_KO
    sc2["limit_path_vi"] = LIMIT_VI
    sc2["limit_path_en"] = LIMIT_EN
    sc2["age_bucket"] = bucket
    sc2["path_priority"] = (
        "dried_path" if bucket in ("dried", "hard") else "fresh_path"
    )
    sc2.update(_frame_for(bucket))

    lo, hi = DRIED_SOAK_LO, DRIED_SOAK_HI
    min_ko, min_vi, min_en = _min_label(lo, hi)

    if bucket in ("dried", "hard"):
        sc2["active_path_ko"] = sc2.get("dried_path_ko") or ""
        sc2["active_path_vi"] = sc2.get("dried_path_vi") or ""
        sc2["soak_minutes_ko"] = min_ko
        sc2["soak_minutes_vi"] = min_vi
        sc2["soak_minutes_en"] = min_en
        # Replace fresh-biased graph success rates so LLM cannot echo "1시간 내 양호".
        if bucket == "hard":
            sc2["success_rate_ko"] = SUCCESS_RATE_HARD_KO
            sc2["success_rate_vi"] = SUCCESS_RATE_HARD_VI
            sc2["success_rate_en"] = SUCCESS_RATE_HARD_EN
        else:
            sc2["success_rate_ko"] = SUCCESS_RATE_DRIED_KO
            sc2["success_rate_vi"] = SUCCESS_RATE_DRIED_VI
            sc2["success_rate_en"] = SUCCESS_RATE_DRIED_EN
        sc2["path_lock_ko"] = (
            f"LOCKED: age_bucket={bucket}. (2)(4)(6)은 dried_path_ko·침지 {min_ko}만. "
            f"protocol/fresh_path의 5–15분·「신선」본문 금지. "
            f"[성공률·고지]는 success_rate_ko만 사용(그래프 신선 성공률·단시간 양호 무시). "
            f"타이머·담금통 use_for도 {min_ko}. "
            f"[성공률·고지]에 「1차 실패 후」+ rescue_disclose_ko 필수. "
            f"(6) 다음에 rescue_2nd_ko의 「2차:」로 시작하는 재시도 한 줄 필수. "
            f"why_ko를 「즉시 찬물로 처리해야」만으로 끝내지 말 것."
            + (" (1)에서 limit_path_ko 먼저." if bucket == "hard" else "")
        )
        sc2["path_lock_vi"] = (
            f"LOCKED age={bucket}: dried_path_vi + ngam {min_vi}. CAM phut tuoi 5-15. "
            f"Dung success_rate_vi (CAM ty le tuoi). "
            f"Bat buoc 「sau lần 1 thất bại」+ rescue_disclose_vi + câu 「Lần 2:」 từ rescue_2nd_vi."
        )
        sc2["path_lock_en"] = (
            f"LOCKED age={bucket}: dried_path + soak {min_en}. No fresh 5–15 body. "
            f"Use success_rate_en only (no fresh short-window line). "
            f"Must include after-1st-fail disclose + 2nd-pass line from rescue_2nd."
        )
        # Force visible rescue labels even if LLM summarizes away the graph fields.
        dried_must_ko = "1차 실패, 2차"
        dried_must_vi = "lần 1 thất bại, Lần 2"
        prev_ko = str(sc2.get("must_include_ko") or "").strip()
        prev_vi = str(sc2.get("must_include_vi") or "").strip()
        sc2["must_include_ko"] = (
            f"{prev_ko}, {dried_must_ko}".strip(", ") if prev_ko else dried_must_ko
        )
        sc2["must_include_vi"] = (
            f"{prev_vi}, {dried_must_vi}".strip(", ") if prev_vi else dried_must_vi
        )
        if bucket == "hard":
            hard_must = (
                "한계 고지 먼저(수개월·고착·100% 불가), dried 1회만, "
                f"식초 침지 {min_ko}, 문지르기 금지, 신선 단시간 성공률 문구 금지"
            )
            sc2["must_include_ko"] = f"{sc2['must_include_ko']}, {hard_must}"
    else:
        sc2["active_path_ko"] = sc2.get("fresh_path_ko") or ""
        sc2["active_path_vi"] = sc2.get("fresh_path_vi") or ""

    out = dict(graph)
    out["stain_context"] = sc2
    out["age_bucket"] = bucket

    if bucket in ("dried", "hard"):
        out["tools"] = _rewrite_soak_tools(list(out.get("tools") or []), lo, hi)
        out["protocol_minutes_ko"] = min_ko
        out["protocol_minutes_vi"] = min_vi
        out["protocol_minutes_en"] = min_en
        if isinstance(out.get("protocol"), dict):
            out["protocol"] = _override_protocol_minutes(out["protocol"], lo, hi)
        tannin_ids = {
            "S_RED_WINE", "S_BLACK_COFFEE", "S_TEA", "S_FRUIT_JUICE", "S_SOFT_DRINK",
            "S_WHITE_WINE_BEER", "S_KIMCHI", "S_KETCHUP", "S_TOMATO_SAUCE", "S_CHILI",
        }
        if sid in tannin_ids or sc2.get("contains_tannin"):
            out["tools"] = [
                t for t in (out.get("tools") or [])
                if not (isinstance(t, dict) and str(t.get("id") or "") == "T_BRUSH_SOFT")
            ]

    return out


def seed_dried_path_rows() -> list[dict[str, str]]:
    """Neo4j UNWIND rows: enrich dried_path_ko/vi for priority stains."""
    ids = sorted(set(DRIED_PATH_KO) | set(DRIED_PATH_VI))
    rows = []
    for sid in ids:
        row: dict[str, str] = {"id": sid}
        if sid in DRIED_PATH_KO:
            row["dried_path_ko"] = DRIED_PATH_KO[sid]
        if sid in DRIED_PATH_VI:
            row["dried_path_vi"] = DRIED_PATH_VI[sid]
        rows.append(row)
    return rows


def sync_ko_edu_dried_paths() -> None:
    """Optional: keep KO_STAIN_EDU dried strings in sync when imported for tests."""
    try:
        from ko_stain_education import KO_STAIN_EDU
    except Exception:
        return
    for sid, path in DRIED_PATH_KO.items():
        if sid in KO_STAIN_EDU:
            KO_STAIN_EDU[sid]["dried_path_ko"] = path
