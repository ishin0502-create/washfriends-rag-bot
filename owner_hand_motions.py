# -*- coding: utf-8 -*-
"""Hand-motion Steps for Zalo message 2 (junior-friendly).

Used instead of LLM ◆(1)~(6) when available — chemistry order unchanged.
"""
from __future__ import annotations

from typing import Optional

# Full custom scripts (highest priority)
HAND_MOTIONS_KO: dict[str, str] = {
    "S_HAIR_DYE": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 장갑 끼고 찬물로 헹궈 주세요\n"
        "─────\n"
        "장갑을 먼저 껴 주세요.\n"
        "찬물을 틀어 얼룩 뒷면에 2~3분 흘려 주세요.\n"
        "세게 문지르지 마세요. 물로만 씻어내는 거예요.\n"
        "→ 색이 물에 씻겨 나오면 잘 되고 있는 거예요.\n"
        "\n"
        "Step 2. 알코올로 색소를 빼 주세요\n"
        "─────\n"
        "① 옷을 뒤집어 주세요 (안감이 위로)\n"
        "② 얼룩 아래에 깨끗한 흰 천을 깔아 받쳐 주세요\n"
        "   (빠져나온 색소가 아래로 흡수되게 해요)\n"
        "③ 다른 흰 천에 알코올을 묻혀 주세요\n"
        "   (옷에 직접 붓지 마세요 — 번져요)\n"
        "④ 얼룩 위에서 수직으로 꾹 3초 → 떼세요\n"
        "   옆으로 문지르면 퍼져요. 위에서 아래로만!\n"
        "⑤ 아래 천에 색소가 옮으면 잘 되고 있는 거예요\n"
        "⑥ 천이 물들면 바로 새 천으로 바꿔 주세요\n"
        "⑦ 5~10번 반복해 주세요. 더 안 묻으면 다음으로\n"
        "\n"
        "Step 3. 산소표백제로 담가 주세요 (흰옷만!)\n"
        "─────\n"
        "⚠️ 유색·실크·울이면 이 Step은 하지 마세요.\n"
        "미지근한 물 1L에 산소표백제 큰술 1을 풀어 주세요.\n"
        "얼룩 부위만 담가 주세요.\n"
        "(시간은 위 【담금 시간】대로: 30분→확인→더)\n"
        "\n"
        "Step 4. 세탁해 주세요\n"
        "─────\n"
        "허용 수온으로 일반 세탁해 주세요.\n"
        "잔색이 남을 수 있다고 고객께 미리 말씀해 주세요."
    ),
    "S_INK_PEN": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 여분을 살짝 걷어 주세요\n"
        "─────\n"
        "마른 천으로 겉의 잉크만 가볍게 닦아 주세요. 문지르지 마세요.\n"
        "\n"
        "Step 2. 알코올로 꾹꾹 빼 주세요\n"
        "─────\n"
        "① 옷을 뒤집고 아래에 흰 천을 깔아 주세요\n"
        "② 다른 흰 천에 알코올을 묻혀 주세요 (직접 붓지 마세요)\n"
        "③ 위에서 수직으로 꾹 3초 → 떼기\n"
        "④ 아래 천·위 천이 물들면 바로 새 천으로\n"
        "⑤ 5~10번 반복해 주세요\n"
        "\n"
        "Step 3. 주방세제로 마무리해 주세요\n"
        "─────\n"
        "중성·주방세제 한두 방울을 흰 천에 묻혀 약하게 찍어 주세요.\n"
        "찬물로 헹군 뒤 세탁해 주세요.\n"
        "흰옷 잔색만: 매니저 확인 후 산소 검토."
    ),
    "S_BLOOD_FRESH": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 찬물로만 헹궈 주세요\n"
        "─────\n"
        "장갑을 껴 주세요.\n"
        "찬물만 사용하세요. 뜨거운 물은 절대 안 됩니다 → 피가 굳어요.\n"
        "뒷면에서 2~3분 흘려 주세요. 세게 문지르지 마세요.\n"
        "\n"
        "Step 2. 효소(또는 중성)로 담가 주세요\n"
        "─────\n"
        "찬물에 효소세제를 타서 담가 주세요.\n"
        "(시간은 【담금 시간】 안내대로)\n"
        "실크·울이면 중성만·짧게, 매니저 확인.\n"
        "\n"
        "Step 3. 헹구고 세탁해 주세요\n"
        "─────\n"
        "찬물로 충분히 헹군 뒤 세탁해 주세요.\n"
        "흰옷 잔색만: 매니저 확인 후 산소 검토."
    ),
    "S_BLACK_COFFEE": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 찬물로 흡수해 주세요\n"
        "─────\n"
        "안쪽에서 찬물로 흡수하세요. 세게 문지르지 마세요 → 번져요.\n"
        "\n"
        "Step 2. 식초 물(1:4)을 만들어 주세요\n"
        "─────\n"
        "흰 식초 1 : 물 4 (예: 식초 50ml + 물 200ml).\n"
        "분무기에 넣고 겉에 「식초 1:4」라고 적어 주세요.\n"
        "얼룩에 1~2번만 뿌리고, 너무 흠뻑 적시지 마세요.\n"
        "5~15분 기다린 뒤 찬물로 헹궈 주세요.\n"
        "\n"
        "Step 3. 세탁해 주세요\n"
        "─────\n"
        "일반 세탁해 주세요.\n"
        "흰옷 잔색만: 매니저 확인 후 산소 검토."
    ),
    "S_COOKING_OIL": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 여분 기름을 걷어 주세요\n"
        "─────\n"
        "키친타월로 겉 기름만 눌러 흡수하세요. 문지르지 마세요.\n"
        "\n"
        "Step 2. 주방세제를 묻혀 주세요\n"
        "─────\n"
        "주방세제 한두 방울을 흰 천에 묻혀 얼룩 위에 약하게 찍어 주세요.\n"
        "바깥→안 방향으로, 세게 문지르지 마세요.\n"
        "몇 분 둔 뒤 찬물(또는 미지근)로 헹궈 주세요.\n"
        "\n"
        "Step 3. 세탁해 주세요\n"
        "─────\n"
        "허용 수온으로 세탁해 주세요. 잔기름이 있으면 Step 2를 한 번 더."
    ),
    "S_MUD": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 마른 흙을 털어 주세요\n"
        "─────\n"
        "완전히 마른 뒤 털거나 살살 긁어 주세요. 젖은 채로 문지르면 더 먹어요.\n"
        "\n"
        "Step 2. 찬물·세제로 국소 처리해 주세요\n"
        "─────\n"
        "찬물로 적신 뒤 중성·주방세제를 약하게 찍어 주세요.\n"
        "데님 등 두꺼운 옷만 조금 더 세게, 얇은 옷은 살살.\n"
        "\n"
        "Step 3. 세탁해 주세요\n"
        "─────\n"
        "세탁 후 밝은 조명에서 확인하세요."
    ),
}

# Family fallback for other L1 ids
_FAMILY_OF: dict[str, str] = {
    "S_TEA": "tannin",
    "S_FRUIT_JUICE": "tannin",
    "S_SOFT_DRINK": "tannin",
    "S_KETCHUP": "tannin_oil",
    "S_TOMATO_SAUCE": "tannin_oil",
    "S_KIMCHI": "tannin_oil",
    "S_SOY_SAUCE": "protein_tannin",
    "S_MILK": "protein",
    "S_EGG": "protein",
    "S_SWEAT_FRESH": "protein",
    "S_BABY_FORMULA": "protein",
    "S_CHOCOLATE": "oil",
    "S_GRASS": "tannin",
    "S_MASCARA": "alcohol_blot",
}

_FAMILY_MOTIONS_KO: dict[str, str] = {
    "tannin": HAND_MOTIONS_KO["S_BLACK_COFFEE"],
    "tannin_oil": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 여분을 걷고 찬물로 흡수해 주세요\n"
        "─────\n"
        "고형은 살살 긁고, 안쪽에서 찬물로 흡수하세요. 세게 문지르지 마세요.\n"
        "\n"
        "Step 2. 주방세제 → 식초 1:4\n"
        "─────\n"
        "먼저 주방세제 한두 방울을 흰 천에 묻혀 약하게 찍어 주세요.\n"
        "헹군 뒤 식초 1:4를 분무·도포하고 안내 시간만큼 두세요.\n"
        "\n"
        "Step 3. 세탁해 주세요\n"
        "─────\n"
        "흰옷 잔색만: 매니저 확인 후 산소 검토."
    ),
    "protein": HAND_MOTIONS_KO["S_BLOOD_FRESH"].replace(
        "피가 굳어요", "단백질이 굳어요"
    ).replace("피가", "얼룩이"),
    "protein_tannin": (
        "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n"
        "\n"
        "Step 1. 찬물로 흡수해 주세요 (온수 금지)\n"
        "─────\n"
        "안쪽에서 찬물만. 세게 문지르지 마세요.\n"
        "\n"
        "Step 2. 효소(또는 중성) → 필요 시 식초 1:4\n"
        "─────\n"
        "프로토콜 순서대로 담그거나 국소 처리해 주세요.\n"
        "(시간은 【담금 시간】 안내)\n"
        "\n"
        "Step 3. 세탁해 주세요\n"
        "─────\n"
        "흰옷 잔색만: 매니저 확인 후 산소 검토."
    ),
    "oil": HAND_MOTIONS_KO["S_COOKING_OIL"],
    "alcohol_blot": HAND_MOTIONS_KO["S_INK_PEN"],
}


def build_hand_motions(stain_id: str, lang: str = "ko") -> str:
    """Return Step script for message 2, or empty if none."""
    sid = str(stain_id or "").strip()
    if lang != "ko":
        # KO-first phase; VI later
        return HAND_MOTIONS_KO.get(sid, "")
    if sid in HAND_MOTIONS_KO:
        return HAND_MOTIONS_KO[sid]
    fam = _FAMILY_OF.get(sid)
    if fam and fam in _FAMILY_MOTIONS_KO:
        return _FAMILY_MOTIONS_KO[fam]
    return ""


def has_hand_motions(stain_id: str, lang: str = "ko") -> bool:
    return bool(build_hand_motions(stain_id, lang))
