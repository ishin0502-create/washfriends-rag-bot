# -*- coding: utf-8 -*-
"""Fixed L2 curriculum exam bank for weekly mastery tests.

Additive only — does not change GraphRAG / protocol stain SOP answers.
Used when the owner has finished the L2 sequential course.
"""
from __future__ import annotations

import random
from typing import Optional

from l1_exam_bank import pass_threshold  # noqa: F401 — re-export for callers

# Each item: id, q, accept (regex|keywords), explain
L2_BANK_KO: list[dict[str, str]] = [
    {
        "id": "l2e_cotton_dry_color",
        "q": "유색 면·린넨에 마른 얼룩이 있을 때, 산소표백은 원칙적으로 써도 되나요? (예/아니오 + 짧게)",
        "accept": r"안\s*됨|안됨|않|금지|말|안\s*돼|안돼|no|불가|식초",
        "explain": "유색+마름 → 산소 원칙 금지. 흰 식초 반복이 우선입니다.",
    },
    {
        "id": "l2e_silk_chem",
        "q": "실크·울에 효소·산소·염소·용제 중 써도 되는 것이 있나요? (짧게)",
        "accept": r"없|전부\s*금|금지|중성|찬물|안\s*됨|안됨",
        "explain": "실크·울: 효소·산소·염소·용제·옥살산 금지. 중성세제+찬물만.",
    },
    {
        "id": "l2e_leather",
        "q": "가죽·스웨이드·아세테이트를 세탁기에 통째로 담가도 되나요?",
        "accept": r"안\s*됨|안됨|않|금지|말|안\s*돼|안돼|no|불가|전문|전용",
        "explain": "물 침지 자체 금지. 전용 케어 또는 전문 의뢰.",
    },
    {
        "id": "l2e_tannin",
        "q": "커피·와인 같은 탄닌 얼룩의 기본 순서를 짧게 말해 주세요. (찬물→?)",
        "accept": r"식초|1\s*[:：]\s*4|산소|찬물",
        "explain": "즉시 찬물 → 흰 식초 1:4 → 흰 면만 산소. 이른 열 금지.",
    },
    {
        "id": "l2e_protein_heat",
        "q": "단백질(피·계란·우유) 얼룩에 온수를 먼저 쓰면 어떻게 되나요?",
        "accept": r"고착|갈색|영구|굳|고정|안\s*지워",
        "explain": "열이 단백질을 갈색으로 영구 고착시킵니다. 찬물만.",
    },
    {
        "id": "l2e_oil_dry",
        "q": "오일·지방 얼룩을 건조기 돌리기 전에 꼭 없어져야 하는 감각은?",
        "accept": r"미끄|기름|미끄럼|미끄러|슬립",
        "explain": "미끄럼(기름기)이 없어진 뒤에만 건조. 열고착 시 성공률 급감.",
    },
    {
        "id": "l2e_dye_blot",
        "q": "립스틱·잉크 등 색소 얼룩을 지울 때, 문지르면 안 되고 어떻게 하나요?",
        "accept": r"찍|블롯|수직|눌러|흡수|안쪽|흡수지",
        "explain": "안쪽에서, 흡수지 깔고, 수직 블롯. 문지르면 옆으로 번집니다.",
    },
    {
        "id": "l2e_acetone_ban",
        "q": "아세톤을 절대 쓰면 안 되는 원단을 하나 말해 주세요.",
        "accept": r"아세테이트|레이온|비닐|코팅|acetate|rayon",
        "explain": "아세테이트·레이온·비닐코팅 — 아세톤이 원단을 녹입니다.",
    },
    {
        "id": "l2e_oxygen_tree",
        "q": "산소표백 전에 꼭 확인해야 할 것 두 가지를 말해 주세요. (원단·테스트)",
        "accept": r"흰|면|폴리|구석|테스트|유색|안정",
        "explain": "흰 면·폴리·색 안정 유색인지 + 구석 테스트 30초 통과 여부.",
    },
    {
        "id": "l2e_oxygen_ban",
        "q": "산소표백을 쓰면 안 되는 원단을 하나 말해 주세요.",
        "accept": r"실크|울|가죽|나일론|스판|모직|silk|wool",
        "explain": "실크·울·가죽·나일론·스판덱스·색 미확인은 산소 금지.",
    },
    {
        "id": "l2e_dye_transfer",
        "q": "이염(다른 옷 물감이 옮음)이 생기면 건조기는 돌려도 되나요?",
        "accept": r"안\s*됨|안됨|않|금지|말|안\s*돼|안돼|no|불가|고착",
        "explain": "건조 금지 — 열이 이염을 고착시킵니다. 먼저 분리·처리.",
    },
    {
        "id": "l2e_dryer_transfer",
        "q": "이미 건조기를 통과한 이염은 어떻게 분류하나요? (복원 가능/불가)",
        "accept": r"불가|안\s*됨|복원\s*불|등급\s*3|3",
        "explain": "건조기 통과 이염 = 복원 불가로 재분류(등급 3 계열).",
    },
]


def sample_l2_exam_questions(
    n: int = 7,
    lang: str = "ko",
    *,
    rng: Optional[random.Random] = None,
) -> list[dict[str, str]]:
    """Return up to n shuffled L2 bank items in KO/VI/EN."""
    from exam_i18n import localized_bank_item

    n = max(1, min(10, int(n or 7)))
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    pool = list(L2_BANK_KO)
    r = rng or random.Random()
    r.shuffle(pool)
    return [localized_bank_item(it, lang, "l2_bank") for it in pool[:n]]
