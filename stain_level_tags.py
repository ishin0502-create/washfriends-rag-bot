# -*- coding: utf-8 -*-
"""Stain L1/L2/L3 tags + intake grade scripts for owner Zalo answers.

Source: docs/claude_review/claude_out/STAIN_LEVEL_TAGS.md + INTAKE_REFUSE_PROTOCOL.md
Cap = force band (not volume). Chemistry order unchanged.
"""
from __future__ import annotations

from typing import Any, Optional

# Base level by stain id (before auto-upgrade rules)
L1: set[str] = {
    "S_BLOOD_FRESH",
    "S_BLACK_COFFEE",
    "S_MILK",
    "S_SWEAT_FRESH",
    "S_COOKING_OIL",
    "S_EGG",
    "S_TEA",
    "S_FRUIT_JUICE",
    "S_SOFT_DRINK",
    "S_KETCHUP",
    "S_TOMATO_SAUCE",
    "S_KIMCHI",  # white only; colored → L2
    "S_CHOCOLATE",
    "S_MUD",
    "S_GRASS",
    "S_INK_PEN",
    "S_SOY_SAUCE",
}

L3: set[str] = {
    "S_ENGINE_OIL",
    "S_MOTORBIKE_OIL",
    "S_TAR",
    "S_LATERITE",
    "S_RUST",
    "S_PAINT_LATEX",
    "S_PAINT_OIL",
    "S_INK_PERMANENT",
    "S_GLUE",
    "S_NAIL_POLISH",
    "S_SHOE_POLISH",
    "S_FECES",
}

# Everything else defaults to L2 (including S_BLOOD_DRY, wine, lipstick, …)

LABEL = {
    "ko": {
        "L1": "L1 초보 단독",
        "L2": "L2 감독 필요",
        "L3": "L3 전문 의뢰·거절 우선",
        "grade1": "등급 1 시도",
        "grade2": "등급 2 부분 제거",
        "grade3": "등급 3 복원 불가",
    },
    "vi": {
        "L1": "L1 Tự xử lý (mới)",
        "L2": "L2 Cần giám sát",
        "L3": "L3 Ưu tiên từ chối / chuyên nghiệp",
        "grade1": "Cấp 1 Thử",
        "grade2": "Cấp 2 Xử lý một phần",
        "grade3": "Cấp 3 Không khôi phục",
    },
    "en": {
        "L1": "L1 beginner OK",
        "L2": "L2 supervisor needed",
        "L3": "L3 refuse / refer first",
        "grade1": "Grade 1 attempt",
        "grade2": "Grade 2 partial",
        "grade3": "Grade 3 cannot restore",
    },
}

GRADE_SCRIPT = {
    "ko": {
        1: (
            "【접수 고지 · 등급 1】 이 얼룩은 시도해 볼 수 있습니다. "
            "다만 완전 제거는 보장드리기 어렵습니다. 잔색이 남을 수 있습니다."
        ),
        2: (
            "【접수 고지 · 등급 2】 시도할 수 있지만 완전 제거는 어렵습니다. "
            "잔색·잔영이 남을 가능성이 큽니다. 진행 전 고객 동의를 받으세요. "
            "잔색은 배상 대상이 아님을 고지하세요."
        ),
        3: (
            "【접수 고지 · 등급 3】 이 얼룩·원단은 매장에서 안전하게 처리하기 어렵습니다. "
            "시도하면 원단 손상·색 손실 위험이 큽니다. "
            "① 전문 의뢰 안내 또는 ② 접수 반려 — 둘 중 하나를 안내하세요. "
            "초보는 배상 확약 금지."
        ),
    },
    "vi": {
        1: (
            "【Tiếp nhận · Cấp 1】 Có thể xử lý được. "
            "Không đảm bảo 100% sạch — có thể còn vết mờ."
        ),
        2: (
            "【Tiếp nhận · Cấp 2】 Có thể thử nhưng rất khó sạch hoàn toàn. "
            "Xin đồng ý trước khi xử lý. Vết còn lại không thuộc bồi thường."
        ),
        3: (
            "【Tiếp nhận · Cấp 3】 Cửa hàng không thể xử lý an toàn. "
            "① Giới thiệu đơn vị chuyên nghiệp hoặc ② Từ chối tiếp nhận. "
            "Nhân viên mới không được cam kết bồi thường."
        ),
    },
    "en": {
        1: (
            "【Intake · Grade 1】 We can attempt this stain. "
            "Full removal is not guaranteed — residual marks may remain."
        ),
        2: (
            "【Intake · Grade 2】 We can try, but full removal is unlikely. "
            "Get consent first. Remaining marks are not a compensation claim."
        ),
        3: (
            "【Intake · Grade 3】 Unsafe for in-store attempt. "
            "① Refer to a specialist or ② decline the job. "
            "Juniors must not promise compensation."
        ),
    },
}

REFUSE_GATE_KO = (
    "【거절 게이트】 아래면 즉시 등급 3: "
    "실크·울·가죽·아세테이트+유성페인트/유성매직/502 · "
    "건조기 지난 이염 · 원단 침투 오래된 곰팡이 · "
    "성분 미상 화학 · 실크·울에 흡수된 엔진오일·타르 · "
    "가죽·스웨이드·모피의 용제 얼룩."
)

REFUSE_GATE_VI = (
    "【Cổng từ chối】 Chuyển Cấp 3 ngay nếu: "
    "Lụa/Len/Da/Acetate + sơn dầu/bút dạ/keo 502 · "
    "đã sấy sau lem màu · nấm thấm sâu · "
    "hóa chất không rõ · Lụa/Len thấm dầu máy/hắc ín · "
    "Da/Da lộn cần dung môi."
)


def base_level(stain_id: str) -> str:
    sid = (stain_id or "").strip().upper()
    if sid in L1:
        return "L1"
    if sid in L3:
        return "L3"
    if sid:
        return "L2"
    return "L2"


def _is_delicate_fabric(graph: dict, entities: dict) -> bool:
    fc = graph.get("fabric_context") if isinstance(graph.get("fabric_context"), dict) else {}
    fid = str(fc.get("id") or entities.get("fabric_id") or "").upper()
    fname = f"{fc.get('name') or ''} {fc.get('name_ko') or ''} {fc.get('name_vi') or ''}".lower()
    item = str(entities.get("item_id") or "").upper()
    if fid in {"F3", "F4"}:  # wool / silk common ids in this KB
        return True
    if any(k in fname for k in ("silk", "wool", "lua", "len", "실크", "울", "가죽", "leather", "acetate", "아세테이트", "모피", "suede")):
        return True
    if item in {"I_NECKTIE", "I_AO_DAI", "I_HANBOK", "I_SCARF", "I_LEATHER_BAG", "I_LEATHER_JACKET"}:
        return True
    if graph.get("leather_care"):
        return True
    return False


def _heat_set(entities: dict, user_text: str, age_bucket: str) -> bool:
    if age_bucket in {"hard"}:
        return True
    t = (user_text or "").lower()
    raw = user_text or ""
    if any(k in raw for k in ("건조기", "다림", "다리미", "열풍", "이미 말려", "말린 뒤")):
        return True
    if any(k in t for k in ("dryer", "iron", "heat-set", "may say", "sấy", "ủi")):
        return True
    if str(entities.get("stain_age") or "") == "hard":
        return True
    return False


def _kimchi_colored(graph: dict, entities: dict) -> bool:
    color = str(entities.get("garment_color") or entities.get("color") or "").lower()
    sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
    note = f"{sc.get('color_note_ko') or ''} {graph.get('color_note_ko') or ''}"
    if color in {"color", "coloured", "colored", "dark", "유색"}:
        return True
    if "유색" in note and "흰" not in note[:20]:
        return True
    return False


def _bump(level: str) -> str:
    if level == "L1":
        return "L2"
    if level == "L2":
        return "L3"
    return "L3"


def resolve_level(
    stain_id: str,
    *,
    graph: Optional[dict] = None,
    entities: Optional[dict] = None,
    user_text: str = "",
) -> tuple[str, int]:
    """Return (L1|L2|L3, grade 1|2|3)."""
    g = graph if isinstance(graph, dict) else {}
    ents = entities if isinstance(entities, dict) else {}
    sid = (stain_id or str(g.get("_owner_stain_id") or (g.get("stain_context") or {}).get("id") or "")).upper()
    level = base_level(sid)

    sc = g.get("stain_context") if isinstance(g.get("stain_context"), dict) else {}
    age = str(sc.get("age_bucket") or g.get("age_bucket") or ents.get("stain_age") or "")

    # Kimchi: white L1, colored L2
    if sid == "S_KIMCHI" and _kimchi_colored(g, ents):
        level = "L2"

    # Dried blood / mildew severity already in L2/L3 sets; dried cooking oil stays L1 base but heat bumps
    if sid == "S_MOTORBIKE_OIL" and age in {"dried", "hard"}:
        level = "L3"
    if sid == "S_PAINT_LATEX" and age in {"dried", "hard"}:
        level = "L3"
    if sid == "S_HAIR_DYE" and age in {"dried", "hard"}:
        level = "L3"
    if sid == "S_MILDEW" and (_is_delicate_fabric(g, ents) or age in {"hard"}):
        level = "L3"

    if _is_delicate_fabric(g, ents):
        level = _bump(level)
    if _heat_set(ents, user_text, age):
        level = _bump(level)

    # Unknown chemical stain keyword
    raw = user_text or ""
    if any(k in raw for k in ("성분 모름", "무슨 약", "화학약품", "không rõ", "unknown chemical")):
        level = "L3"

    grade = {"L1": 1, "L2": 2, "L3": 3}[level]
    # Dried / hard on L1 stains → at least grade 2 script
    if level == "L1" and age in {"dried", "hard"}:
        grade = 2
    return level, grade


def format_banner(level: str, grade: int, lang: str = "ko") -> str:
    lang = lang if lang in LABEL else "ko"
    lab = LABEL[lang]
    return f"◆ [{lab[level]} · {lab[f'grade{grade}']}]"


def format_intake_block(level: str, grade: int, lang: str = "ko") -> str:
    lang = lang if lang in GRADE_SCRIPT else "ko"
    parts = [format_banner(level, grade, lang), GRADE_SCRIPT[lang][grade]]
    if grade >= 3:
        parts.append(REFUSE_GATE_KO if lang == "ko" else (REFUSE_GATE_VI if lang == "vi" else GRADE_SCRIPT["en"][3]))
    return "\n".join(parts)


def prepend_level_to_answer(
    answer: str,
    *,
    stain_id: str = "",
    graph: Optional[dict] = None,
    entities: Optional[dict] = None,
    user_text: str = "",
    lang: str = "ko",
) -> str:
    if not answer:
        return answer
    g = graph if isinstance(graph, dict) else {}
    if g.get("specialty_item_care") and not (stain_id or (g.get("stain_context") or {}).get("id")):
        return answer
    level, grade = resolve_level(stain_id, graph=g, entities=entities or {}, user_text=user_text)
    block = format_intake_block(level, grade, lang)
    # Avoid double-prepend on cache retries
    if answer.lstrip().startswith("◆ [") and ("L1" in answer[:80] or "L2" in answer[:80] or "L3" in answer[:80]):
        return answer
    return block + "\n\n" + answer.lstrip()
