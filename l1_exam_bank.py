# -*- coding: utf-8 -*-
"""Fixed L1 curriculum exam bank for weekly mastery tests.

Additive only — does not change GraphRAG / protocol stain SOP answers.
Questions are short Zalo-friendly; accept uses learning_quiz._match_accept style.
"""
from __future__ import annotations

import random
from typing import Optional


# Each item: id, q, accept (regex|keywords), explain
L1_BANK_KO: list[dict[str, str]] = [
    {
        "id": "l1e_label",
        "q": "케어라벨에서 삼각형·원(동그라미)·손세탁 표시는 각각 무엇을 뜻하나요? (짧게)",
        "accept": r"표백|드라이|손\s*세탁|손세탁|삼각형|원",
        "explain": "삼각형=표백, 원=드라이클리닝, 손세탁 표시=손세탁 우선.",
    },
    {
        "id": "l1e_temp_protein",
        "q": "피·계란·우유 같은 단백질 얼룩은 처음에 어떤 물로 해야 하나요?",
        "accept": r"찬물|cold|차가운\s*물",
        "explain": "단백질은 찬물. 온수·건조기는 갈색으로 고착됩니다.",
    },
    {
        "id": "l1e_blot",
        "q": "색소·잉크 얼룩을 처음 다룰 때, 문지르면 안 되고 어떻게 해야 하나요?",
        "accept": r"찍|블롯|수직|눌러|흡수|흰\s*천|면\s*천",
        "explain": "흰 천으로 수직으로 찍어 흡수(블롯). 옆으로 문지르면 번집니다.",
    },
    {
        "id": "l1e_heat",
        "q": "잔색·기름 미끄럼·냄새가 남아 있는데 건조기·다리미를 써도 될까요? (예/아니오 + 이유 짧게)",
        "accept": r"안\s*됨|안됨|않|금지|말|안\s*돼|안돼|no|불가|고착",
        "explain": "안 됩니다. 열이 있으면 얼룩이 영구 고착됩니다. 강광 확인 후 건조.",
    },
    {
        "id": "l1e_corner",
        "q": "알코올·아세톤·산소표백을 쓰기 전에 꼭 해야 하는 30초 확인은?",
        "accept": r"구석|테스트|안감|밑단|솔기|패치",
        "explain": "구석(밑단·안감·솔기) 테스트 30초. 색빠짐·손상이 없어야 진행.",
    },
    {
        "id": "l1e_mix",
        "q": "절대 섞으면 안 되는 조합 하나를 말해 주세요. (예: ○○ + ○○)",
        "accept": r"식초.*락스|락스.*식초|암모니아.*락스|락스.*암모니아|산소.*락스|락스.*산소",
        "explain": "식초+락스 / 암모니아+락스 / 산소표백+락스 — 위험하거나 효과가 사라집니다.",
    },
    {
        "id": "l1e_ppe",
        "q": "피·구토·용제·락스 작업 때 기본적으로 끼는 장갑은 어떤 종류인가요?",
        "accept": r"니트릴|nitrile|고무장갑|장갑",
        "explain": "니트릴 장갑(+필요 시 마스크·환기).",
    },
    {
        "id": "l1e_refuse",
        "q": "실크에 유성 페인트가 묻었을 때, 초보 매장에서 먼저 해야 할 일은 무리한 시도인가요, 거절·전문 의뢰 안내인가요?",
        "accept": r"거절|의뢰|전문|안내|반려|보내",
        "explain": "거절 게이트 — 전문 의뢰·거절 안내가 우선입니다.",
    },
    {
        "id": "l1e_enzyme",
        "q": "효소 세제를 쓰면 안 되는 원단을 하나 말해 주세요.",
        "accept": r"실크|울|모직|가죽|silk|wool",
        "explain": "효소는 실크·울에 금지. 40°C 초과 시 효소도 힘이 약해집니다.",
    },
    {
        "id": "l1e_oxygen",
        "q": "산소표백은 어떤 옷에만 쓰나요? (원단·색 기준 짧게)",
        "accept": r"흰|흰색|면|폴리|유색.*테스트|안정",
        "explain": "흰 면·폴리·색 안정 유색(구석 테스트). 실크·울·색 미확인은 금지.",
    },
    {
        "id": "l1e_blood",
        "q": "신선한 피 얼룩에 온수나 건조기를 쓰면 어떻게 되나요?",
        "accept": r"고착|갈색|안\s*지워|영구|굳|고정",
        "explain": "단백질이 갈색으로 영구 고착됩니다. 찬물부터.",
    },
    {
        "id": "l1e_coffee",
        "q": "블랙커피(신선)에 쓰는 흰 식초와 물의 비율은? (예: 1:4)",
        "accept": r"1\s*[:：]\s*4|1대\s*4|식초\s*1|1/4",
        "explain": "흰 식초 1 : 물 4 (분무기 예: 식초 40ml + 물 160ml).",
    },
    {
        "id": "l1e_oil",
        "q": "식용유 얼룩을 건조기 돌리기 전에 꼭 확인해야 하는 감각은?",
        "accept": r"미끄|기름|미끄럼|미끄러|슬립|없어",
        "explain": "미끄럼(기름기)이 없어진 뒤에만 건조.",
    },
    {
        "id": "l1e_ink",
        "q": "볼펜 잉크를 알코올로 지울 때, 문지르면 안 되는 이유는?",
        "accept": r"번|확산|퍼|옆|깊이",
        "explain": "문지르면 잉크가 옆으로·깊이 번집니다. 수직 블롯, 매번 새 흰 천.",
    },
    {
        "id": "l1e_mud",
        "q": "마른 진흙은 바로 물로 문지를까요, 먼저 말리고 털까요?",
        "accept": r"말|건조|털|솔|먼저",
        "explain": "완전 건조 후 실외에서 털고 부드러운 솔. 젖은 채 문지르면 깊이 들어갑니다.",
    },
    {
        "id": "l1e_grade",
        "q": "손님에게 ‘완전 제거는 어렵고 잔색이 남을 수 있다’고 고지하는 것은 등급 몇인가요? (1/2/3)",
        "accept": r"2|이|등급\s*2",
        "explain": "등급 2 = 부분 제거 가능·잔색 남을 수 있음 고지.",
    },
    {
        "id": "l1e_care_x",
        "q": "케어라벨 세탁통(물세탁) 표시 위에 X가 있으면 무슨 뜻인가요?",
        "accept": r"금지|하지\s*말|하지\s*마|물세탁\s*금|세탁\s*금|엑스|X",
        "explain": "X = 하지 말 것. 물세탁 표시에 X면 물세탁 금지.",
    },
]


def sample_l1_exam_questions(
    n: int = 7,
    lang: str = "ko",
    *,
    rng: Optional[random.Random] = None,
    prefer_ids: Optional[list] = None,
) -> list[dict[str, str]]:
    """Return up to n L1 bank items; failed ids first, then shuffle."""
    from exam_i18n import localized_bank_item
    from exam_sample import pick_exam_pool

    n = max(1, min(10, int(n or 7)))
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    picked = pick_exam_pool(list(L1_BANK_KO), n, prefer_ids=prefer_ids, rng=rng)
    return [localized_bank_item(it, lang, "l1_bank") for it in picked]


def pass_threshold(score: int, max_score: int, ratio: float = 0.7) -> bool:
    mx = max(0, int(max_score or 0))
    sc = max(0, int(score or 0))
    if mx <= 0:
        return False
    need = int((mx * ratio) + 0.999)  # ceil
    need = max(1, min(mx, need))
    return sc >= need
