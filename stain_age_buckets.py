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
    # Unsigned VI for matching
    try:
        from unicodedata import normalize

        t_n = "".join(c for c in normalize("NFD", t) if not (0x300 <= ord(c) <= 0x36F))
    except Exception:
        t_n = t

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
                "원단·두께 미상이면 Cap을 얇다고 단정하지 말 것(보통 기준+얇으면 Cap1). "
                "rescue_2nd·rescue_disclose·limit_path_ko를 [성공률·고지]에 포함."
            ),
            "age_frame_vi": (
                "age_bucket=dried. Body = dried_path_vi (phút dài). "
                "protocol chỉ thứ tự — không ưu tiên phút tươi. "
                "Tannin: CẤM chà. Include rescue + limit_path_vi."
            ),
            "age_frame_en": (
                "age_bucket=dried. Body = dried_path (longer soak). "
                "Protocol = chem order only; do not prefer fresh minutes. "
                "Tannin: no scrubbing. Include rescue + limit_path_en."
            ),
        }
    if bucket == "hard":
        return {
            "age_frame_ko": (
                "age_bucket=hard. (1)에서 limit_path_ko를 먼저 고지. "
                "시도는 dried_path_ko 1회만(장침지). protocol 신선 분을 본문으로 쓰지 말 것. "
                "탄닌: 문지르기 금지. 무한 반복·100% 약속 금지. rescue_disclose 필수."
            ),
            "age_frame_vi": (
                "age_bucket=hard. Lead with limit_path_vi. "
                "Try dried_path once only. No scrub. No 100%. rescue_disclose required."
            ),
            "age_frame_en": (
                "age_bucket=hard. Lead with limit_path_en. "
                "One dried attempt only. No scrub. No 100%. rescue_disclose required."
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

    # Prefer dried text in tip-like slots when dried/hard (LLM still sees both)
    if bucket in ("dried", "hard") and sc2.get("dried_path_ko"):
        sc2["active_path_ko"] = sc2["dried_path_ko"]
        sc2["active_path_vi"] = sc2.get("dried_path_vi") or ""
    else:
        sc2["active_path_ko"] = sc2.get("fresh_path_ko") or ""
        sc2["active_path_vi"] = sc2.get("fresh_path_vi") or ""

    out = dict(graph)
    out["stain_context"] = sc2
    out["age_bucket"] = bucket

    # Tannin dried/hard: soft brush invites LLM "문지르기" — prefer cloth blot only.
    tannin_ids = {
        "S_RED_WINE", "S_BLACK_COFFEE", "S_TEA", "S_FRUIT_JUICE", "S_SOFT_DRINK",
        "S_WHITE_WINE_BEER", "S_KIMCHI", "S_KETCHUP", "S_TOMATO_SAUCE",
    }
    if bucket in ("dried", "hard") and (
        sid in tannin_ids or sc2.get("contains_tannin")
    ):
        tools = out.get("tools")
        if isinstance(tools, list) and tools:
            out["tools"] = [
                t for t in tools
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
