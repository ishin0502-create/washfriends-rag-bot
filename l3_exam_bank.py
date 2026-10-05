# -*- coding: utf-8 -*-
"""Fixed L3 curriculum exam bank for weekly mastery tests.

Additive only — used when the owner has finished the L3 sequential course.
"""
from __future__ import annotations

import random
from typing import Optional

from l1_exam_bank import pass_threshold  # noqa: F401 — re-export for callers

L3_BANK_KO: list[dict[str, str]] = [
    {
        "id": "l3e_retry_order",
        "q": "1차 세척이 실패했을 때, 2차 시도 전에 꼭 해야 할 것은? (원단·계열 재판단 등 짧게)",
        "accept": r"재판단|다른\s*계열|원단|잔여|확인|2차",
        "explain": "1차 실패 → 원단·잔여 얼룩 재판단 → 다른 계열인지 확인 후 2차.",
    },
    {
        "id": "l3e_no_heat_hide",
        "q": "잔색·미끄럼·냄새가 남았을 때 다림질·건조기로 ‘감추기’ 해도 되나요?",
        "accept": r"안\s*됨|안됨|않|금지|말|안\s*돼|no|불가",
        "explain": "열로 감추기 금지 — 클레임이 커집니다. 열 가하지 마세요.",
    },
    {
        "id": "l3e_grade2",
        "q": "2차까지 실패하면 점주가 고객에게 먼저 말해야 하는 등급 개념은? (등급 2 등)",
        "accept": r"등급\s*2|부분|2|잔여|수용|재고지",
        "explain": "등급 2(부분 제거) 재고지 → 잔여 수용 또는 전문 의뢰.",
    },
    {
        "id": "l3e_down_jacket",
        "q": "다운(패딩) 전체를 물에 담가 세탁해도 되나요?",
        "accept": r"안\s*됨|안됨|국소|중성|미온|전용|완전\s*건조|침수\s*금",
        "explain": "다운: 국소만 중성·미온. 전체 침수는 전용·완전 건조.",
    },
    {
        "id": "l3e_waterproof",
        "q": "방수·스포츠 기능성 옷에 유연제·산소를 써도 되나요?",
        "accept": r"안\s*됨|안됨|금지|전용|말|불가",
        "explain": "방수·스포츠: 유연제·산소·염소 금지 · 전용 세제.",
    },
    {
        "id": "l3e_laterite",
        "q": "라테라이트(붉은 적토) 얼룩에 젖은 채 문지르거나 락스를 쓰면 어떻게 되나요?",
        "accept": r"고착|철|악화|금지|안\s*됨|브러시|건조",
        "explain": "젖은 채 문지르기·락스 절대 금지(철 고착). 건조 후 마른 브러시.",
    },
    {
        "id": "l3e_motorbike_oil",
        "q": "오토바이 오일 얼룩 처리 후 건조기에 넣기 전 확인할 감각은?",
        "accept": r"미끄|기름|탈지|미끄럼|슬립",
        "explain": "흡착·탈지·주방세제 후 미끄럼 없이 건조.",
    },
    {
        "id": "l3e_kimchi_broth",
        "q": "김치국 얼룩에 유색 면에 산소표백을 원칙적으로 써도 되나요?",
        "accept": r"안\s*됨|안됨|금지|흰|식초|찬물|유색",
        "explain": "유색 산소 원칙 금지. 찬물·세제·식초 → 흰옷만 산소.",
    },
    {
        "id": "l3e_mold_leather",
        "q": "가죽·실크·울에 심한 곰팡이가 있으면 매장에서 산소로 무리해도 되나요?",
        "accept": r"전문|안\s*됨|금지|의뢰|말",
        "explain": "가죽·실크·울·심함=전문. 허용 원단만 산소 경로.",
    },
    {
        "id": "l3e_claim_photo",
        "q": "클레임·등급 2·3 접수 시 사진은 몇 장·어떤 조건이 원칙인가요? (짧게)",
        "accept": r"3|자연광|라벨|근접|원상태|사진",
        "explain": "라벨·얼룩 원상태·색상 근접 3장(자연광). 동의서·Zalo 저장.",
    },
    {
        "id": "l3e_pro_refer",
        "q": "이미 건조기를 통과한 이염은 매장에서 자체 복원 시도해도 되나요?",
        "accept": r"안\s*됨|불가|전문|등급|3|복원\s*불",
        "explain": "건조기 통과 이염 — 자체 무리 시도 금지·전문·등급 재분류.",
    },
    {
        "id": "l3e_bleach_not_universal",
        "q": "락스(염소표백)를 데오·분유·실크 얼룩에 쓰면 보통 어떻게 되나요?",
        "accept": r"악화|황변|손상|금지|안\s*됨|데오|만능\s*아",
        "explain": "락스는 만능 아님 — 데오·황변·분유·이염·실크·울은 악화 가능.",
    },
]


def sample_l3_exam_questions(
    n: int = 7,
    lang: str = "ko",
    *,
    rng: Optional[random.Random] = None,
) -> list[dict[str, str]]:
    """Return up to n shuffled L3 bank items in KO/VI/EN."""
    from exam_i18n import localized_bank_item

    n = max(1, min(10, int(n or 7)))
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    pool = list(L3_BANK_KO)
    r = rng or random.Random()
    r.shuffle(pool)
    return [localized_bank_item(it, lang, "l3_bank") for it in pool[:n]]
