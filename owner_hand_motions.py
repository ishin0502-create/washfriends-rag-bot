# -*- coding: utf-8 -*-
"""Hand-motion Steps for Zalo message 2 (junior-friendly).

L1 17 stains + hair dye: individual scripts. Chemistry order from education/protocol.
"""
from __future__ import annotations

_START = "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n\n"


def _step(n: int, title: str, body: str) -> str:
    return f"Step {n}. {title}\n─────\n{body.strip()}\n"


HAND_MOTIONS_KO: dict[str, str] = {
    "S_HAIR_DYE": (
        _START
        + _step(
            1,
            "장갑 끼고 찬물로 헹궈 주세요",
            "장갑을 먼저 껴 주세요.\n"
            "찬물을 틀어 얼룩 뒷면에 2~3분 흘려 주세요.\n"
            "세게 문지르지 마세요. 물로만 씻어내는 거예요.\n"
            "→ 색이 물에 씻겨 나오면 잘 되고 있는 거예요.",
        )
        + "\n"
        + _step(
            2,
            "알코올로 색소를 빼 주세요",
            "① 옷을 뒤집어 주세요 (안감이 위로)\n"
            "② 얼룩 아래에 깨끗한 흰 천을 깔아 받쳐 주세요\n"
            "③ 다른 흰 천에 알코올을 묻혀 주세요 (옷에 직접 붓지 마세요)\n"
            "④ 위에서 수직으로 꾹 3초 → 떼세요 (옆으로 문지르면 퍼져요)\n"
            "⑤ 아래 천에 색소가 옮으면 잘 되고 있는 거예요\n"
            "⑥ 천이 물들면 바로 새 천으로 바꿔 주세요\n"
            "⑦ 5~10번 반복. 더 안 묻으면 다음으로",
        )
        + "\n"
        + _step(
            3,
            "산소표백제로 담가 주세요 (흰옷만!)",
            "⚠️ 유색·실크·울이면 이 Step은 하지 마세요.\n"
            "미지근한 물 1L에 산소표백제 큰술 1을 풀어 주세요.\n"
            "얼룩 부위만 담가 주세요. (시간은 위 【담금 시간】대로)",
        )
        + "\n"
        + _step(
            4,
            "세탁해 주세요",
            "허용 수온으로 세탁해 주세요.\n"
            "잔색이 남을 수 있다고 고객께 미리 말씀해 주세요.",
        )
    ),
    "S_BLOOD_FRESH": (
        _START
        + _step(
            1,
            "찬물로만 헹궈 주세요",
            "장갑을 껴 주세요.\n"
            "찬물만 사용하세요. 뜨거운 물은 절대 안 됩니다 → 피가 굳어요.\n"
            "뒷면에서 2~3분 흘려 주세요. 세게 문지르지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "효소(또는 중성)로 담가 주세요",
            "찬물에 효소세제를 타서 담가 주세요. (시간은 【담금 시간】 안내)\n"
            "실크·울이면 중성만·짧게, 매니저 확인.",
        )
        + "\n"
        + _step(
            3,
            "헹구고 세탁해 주세요",
            "찬물로 충분히 헹군 뒤 세탁해 주세요.\n"
            "흰옷 잔색만: 매니저 확인 후 산소 검토.",
        )
    ),
    "S_BLACK_COFFEE": (
        _START
        + _step(
            1,
            "옷을 뒤집고 찬물로 흡수해 주세요",
            "옷을 뒤집어 주세요.\n"
            "안쪽에서 찬물로 흡수하세요. 세게 문지르지 마세요 → 번져요.",
        )
        + "\n"
        + _step(
            2,
            "식초 물(1:4)을 만들어 뿌려 주세요",
            "흰 식초 1 : 물 4 (예: 식초 50ml + 물 200ml).\n"
            "분무기에 넣고 겉에 「식초 1:4」라고 적어 주세요.\n"
            "얼룩에 1~2번만 뿌리고 5~15분 두세요. 너무 흠뻑 적시지 마세요.\n"
            "찬물로 헹궈 주세요.",
        )
        + "\n"
        + _step(
            3,
            "세탁해 주세요",
            "일반 세탁해 주세요.\n"
            "흰옷 잔색만: 구석 테스트 후 산소(실크·울·유색은 생략).",
        )
    ),
    "S_TEA": (
        _START
        + _step(
            1,
            "옷을 뒤집고 찬물로 흡수해 주세요",
            "옷을 뒤집어 주세요.\n"
            "찬물로 안쪽에서 흡수하세요. 옆으로 문지르지 마세요.\n"
            "💡 우유 탄 차면 단백질이 있으니 효소를 먼저 쓰는 편이 좋아요.",
        )
        + "\n"
        + _step(
            2,
            "식초 1:4를 뿌려 주세요",
            "식초 1 : 물 4로 만들어 분무하세요. 5~15분 두세요.\n"
            "찬물로 헹궈 주세요.",
        )
        + "\n"
        + _step(
            3,
            "세탁해 주세요",
            "미온(허용 시)으로 세탁해 주세요.\n"
            "흰/면 잔색: 구석 테스트 후 산소. 실크·울은 산소 금지.\n"
            "당분이 남은 채로 말리지 마세요 → 황변돼요.",
        )
    ),
    "S_FRUIT_JUICE": (
        _START
        + _step(
            1,
            "옷을 뒤집고 찬물로 헹궈 주세요",
            "옷을 뒤집어 주세요.\n"
            "찬물로 안쪽부터 헹궈·흡수하세요. 세게 문지르지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "식초 1:4를 뿌려 주세요",
            "식초 1:4를 분무·도포하고 5~10분 두세요.\n"
            "찬물로 헹궈 주세요.",
        )
        + "\n"
        + _step(
            3,
            "세탁해 주세요",
            "허용 수온으로 세탁해 주세요.\n"
            "흰/면 잔색만 산소(테스트). 실크·울·유색은 식초만 반복.",
        )
    ),
    "S_SOFT_DRINK": (
        _START
        + _step(
            1,
            "찬물로 흡수·헹궈 주세요",
            "찬물로 흡수·헹구세요. 옆으로 문지르지 마세요.\n"
            "끈적한 당분이 남아 있으면 말리지 마세요 → 황변돼요.",
        )
        + "\n"
        + _step(
            2,
            "색소가 있으면 식초 1:4",
            "콜라·색소 음료면 식초 1:4를 뿌리고 5~10분 두세요.\n"
            "헹궈 주세요.",
        )
        + "\n"
        + _step(
            3,
            "세탁해 주세요",
            "세탁해 주세요.\n"
            "흰옷 잔색·황변 걱정이면 구석 테스트 후 산소.\n"
            "끈적·단맛이 없어진 뒤에만 말리세요.",
        )
    ),
    "S_KIMCHI": (
        _START
        + _step(
            1,
            "고춧가루·건더기를 제거해 주세요",
            "고춧가루·건더기를 살살 털거나 긁어 주세요.\n"
            "문질러 번지게 하지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "찬물로 헹군 뒤 주방세제를 찍어 주세요",
            "안쪽에서 찬물로 헹궈 주세요.\n"
            "주방세제 1~2방울을 흰 천에 묻혀 찍어 바르고 30초 두세요.\n"
            "부드러운 솔로 약하게만 → 바로 헹구세요.",
        )
        + "\n"
        + _step(
            3,
            "식초 1:4를 해 주세요",
            "식초 1:4를 분무하고 5~10분 두세요 (색소·냄새).\n"
            "헹군 뒤, 흰옷만 구석 테스트 후 산소.\n"
            "⚠️ 유색은 산소 금지. 치약 쓰지 마세요.",
        )
        + "\n"
        + _step(
            4,
            "세탁해 주세요",
            "세탁해 주세요.\n"
            "고추 색소·냄새가 남은 채로 말리지 마세요.",
        )
    ),
    "S_KETCHUP": (
        _START
        + _step(
            1,
            "고형을 긁어 주세요",
            "케첩 고형을 살살 긁어 제거하세요. 문질러 번지게 하지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "찬물 흡수 → 주방세제",
            "찬물로 흡수하세요.\n"
            "주방세제 1~2방울을 흰 천에 묻혀 바깥→안으로 약하게 찍어 주세요.\n"
            "헹궈 주세요.",
        )
        + "\n"
        + _step(
            3,
            "식초 1:4 → 세탁",
            "식초 1:4를 5~10분 두세요.\n"
            "흰옷 잔색만 산소(테스트). 이른 열·건조는 붉은 색을 고착시켜요.",
        )
    ),
    "S_TOMATO_SAUCE": (
        _START
        + _step(
            1,
            "고형을 긁어 주세요",
            "토마토소스 고형을 긁어 주세요. 옆으로 문질러 붉은색을 번지게 하지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "찬물 → 주방세제",
            "찬물로 흡수·헹군 뒤, 주방세제 1~2방울을 약하게 찍어 주세요.",
        )
        + "\n"
        + _step(
            3,
            "식초 1:4 → 세탁",
            "식초 1:4를 5~10분 두고 헹구세요.\n"
            "흰옷만 산소(테스트). 잔색 채 말리지 마세요.",
        )
    ),
    "S_COOKING_OIL": (
        _START
        + _step(
            1,
            "여분 기름을 눌러 흡수해 주세요",
            "키친타월로 겉 기름만 눌러 흡수하세요. 문지르지 마세요.\n"
            "💡 검고 냄새 세면 엔진/오토바이 오일(L3)일 수 있어요 — 매니저 확인.",
        )
        + "\n"
        + _step(
            2,
            "전분으로 기름을 빨아 주세요",
            "옥수수전분(또는 밀가루)을 얼룩 위에 두껍게 덮으세요.\n"
            "10~30분 둔 뒤 털어 주세요. 필요하면 한 번 더.",
        )
        + "\n"
        + _step(
            3,
            "주방세제를 바르고 헹궈 주세요",
            "미지근한 물에 적신 뒤 주방세제 1~2방울을 얼룩에 바르세요.\n"
            "부드러운 솔로 약하게 5~10분. 세게 문지르지 마세요.\n"
            "헹군 뒤 손끝으로 미끄러운지 확인하세요. 미끄러우면 이 Step 반복.",
        )
        + "\n"
        + _step(
            4,
            "세탁해 주세요",
            "미끄러움이 사라진 뒤에만 세탁·건조하세요.\n"
            "미끄러운 채로 건조기 돌리면 열고착돼요.",
        )
    ),
    "S_CHOCOLATE": (
        _START
        + _step(
            1,
            "고형을 긁어 주세요",
            "초코 고형을 살살 긁어 제거하세요.",
        )
        + "\n"
        + _step(
            2,
            "찬물 → 효소",
            "찬물로 헹군 뒤 효소세제를 바르고 약 30분 두세요.\n"
            "(실크·울은 중성세제 위주)",
        )
        + "\n"
        + _step(
            3,
            "주방세제 → 식초·산소(흰옷)",
            "지방이 남으면 주방세제 1~2방울을 찍어 주세요.\n"
            "잔색은 식초 1:4, 흰옷만 구석 테스트 후 산소.\n"
            "지방·색소 남은 채 건조기·다림질 하지 마세요.",
        )
        + "\n"
        + _step(4, "세탁해 주세요", "세탁해 주세요. 말리기 전 밝은 조명에서 확인하세요.")
    ),
    "S_EGG": (
        _START
        + _step(
            1,
            "여분을 긁어 주세요",
            "여분을 긁어 제거하세요.\n"
            "⚠️ 처음부터 온수 금지 → 단백질이 ‘익어’ 고착돼요.",
        )
        + "\n"
        + _step(
            2,
            "찬물 → 효소",
            "찬물만 사용하세요.\n"
            "효소를 바르고 20~30분 두세요. (실크·울은 중성 위주)",
        )
        + "\n"
        + _step(
            3,
            "노른자 미끄럼이면 주방세제 → 세탁",
            "미끄러우면 주방세제 1~2방울을 찍어 주세요.\n"
            "찬물·미온으로 세탁해 주세요.",
        )
    ),
    "S_MILK": (
        _START
        + _step(
            1,
            "찬물로 헹궈 주세요",
            "찬물로 헹구세요. 온수 먼저 금지.\n"
            "💡 분유(철분)면 분유 SOP — 락스 쓰지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "효소를 해 주세요",
            "효소를 바르고 20~30분 두세요. (실크·울은 중성세제·찬물)",
        )
        + "\n"
        + _step(
            3,
            "지방 남으면 주방세제 → 세탁",
            "미끄러우면 주방세제 1~2방울.\n"
            "세탁 후 냄새·잔색을 확인해 주세요.",
        )
    ),
    "S_SWEAT_FRESH": (
        _START
        + _step(
            1,
            "신선 땀인지 황변인지 확인해 주세요",
            "이미 겨드랑이가 누렇다면 황변 SOP로 가세요.\n"
            "신선 냄새면 아래대로 진행하세요. 락스는 쓰지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "효소를 바르고 세탁해 주세요",
            "마른 부위에 효소를 바르고 약 30분 두세요. (실크·울→중성)\n"
            "찬물 또는 미온으로 세탁해 주세요.",
        )
        + "\n"
        + _step(
            3,
            "냄새 남으면 식초",
            "냄새 남으면 식초 1:4를 5~10분 두고 헹구세요.\n"
            "통풍 건조. 황변이 시작됐는지 밝은 조명에서 보세요.",
        )
    ),
    "S_SOY_SAUCE": (
        _START
        + _step(
            1,
            "바로 찬물로 헹궈 주세요",
            "즉시 찬물로 헹구세요. 이른 열·건조는 검정 색소를 고착시켜요.",
        )
        + "\n"
        + _step(
            2,
            "효소 → 식초 1:4",
            "효소를 바르고 15~30분 두세요. (실크·울→중성)\n"
            "그다음 식초 1:4를 5~10분 분무·도포하세요.",
        )
        + "\n"
        + _step(
            3,
            "세탁해 주세요",
            "흰옷 잔색만 산소(테스트). 세탁 후 말리기 전 확인하세요.",
        )
    ),
    "S_INK_PEN": (
        _START
        + _step(
            1,
            "여분을 살짝 걷어 주세요",
            "마른 천으로 겉 잉크만 가볍게. 문지르지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "알코올로 꾹꾹 빼 주세요",
            "① 옷을 뒤집고 아래에 흰 천을 깔아 주세요\n"
            "② 다른 흰 천에 알코올을 묻혀 주세요 (직접 붓지 마세요)\n"
            "③ 위에서 수직으로 꾹 3초 → 떼기\n"
            "④ 천이 물들면 바로 새 천으로\n"
            "⑤ 5~10번 반복해 주세요",
        )
        + "\n"
        + _step(
            3,
            "주방세제 → 세탁",
            "주방세제 한두 방울을 약하게 찍어 헹군 뒤 세탁하세요.\n"
            "락스로 잉크를 지우려 하지 마세요 → 회색 자국이 남을 수 있어요.",
        )
    ),
    "S_MUD": (
        _START
        + _step(
            1,
            "마른 흙을 털어 주세요",
            "완전히 마른 뒤 털거나 살살 긁으세요.\n"
            "젖은 채로 문지르면 더 먹어요.",
        )
        + "\n"
        + _step(
            2,
            "찬물·세제로 국소 처리해 주세요",
            "찬물로 적신 뒤 중성·주방세제를 약하게 찍어 주세요.\n"
            "데님 등 두꺼운 옷만 조금 더 세게, 얇은 옷은 살살.",
        )
        + "\n"
        + _step(3, "세탁해 주세요", "세탁 후 밝은 조명에서 확인하세요.")
    ),
    "S_GRASS": (
        _START
        + _step(
            1,
            "흙을 털고 구석 테스트해 주세요",
            "흙을 털어 주세요.\n"
            "밑단에 알코올 1~2방울·30초. 색이 빠지면 알코올 Step을 중단하세요.\n"
            "💡 풀(전분) 이염이면 전분 이염 SOP입니다.",
        )
        + "\n"
        + _step(
            2,
            "알코올로 초록을 찍어 빼 주세요",
            "옷을 뒤집고 아래에 흡수지·흰 천을 깔아 주세요.\n"
            "알코올을 흰 천에 묻혀 수직으로 꾹꾹 찍어 주세요. 옆으로 문지르지 마세요.\n"
            "천이 물들면 바로 교체하세요.",
        )
        + "\n"
        + _step(
            3,
            "효소 → 세탁",
            "효소에 15~30분 담근 뒤 세탁하세요.\n"
            "흰옷만 산소(테스트). 초록 남은 채 말리지 마세요.",
        )
    ),
    # ── L2 priority 15 (supervisor) ──
    "S_BLOOD_DRY": (
        _START
        + _step(
            1,
            "매니저 확인 · 갈색 잔영 설명",
            "마름 피는 완전 제거가 어렵습니다. 갈색 잔영·부분 제거를 손님께 먼저 말씀하세요.\n"
            "온수·건조기 절대 금지(더 굳습니다).",
        )
        + "\n"
        + _step(
            2,
            "찬물·효소에 담가 주세요",
            "찬물에 효소를 풀고 20~45분 담가 주세요. 중간에 한 번 흔들어 주세요.\n"
            "실크·울은 효소 금지 → 중성세제·찬물만.",
        )
        + "\n"
        + _step(
            3,
            "(흰 면만) 과산화수소 테스트",
            "흰 면만: 약국 3% 과산화수소를 구석 1방울·30초. OK면 얼룩에 10분, 바로 찬물 헹굼.\n"
            "유색·실크·울은 이 Step 건너뛰세요.",
        )
        + "\n"
        + _step(4, "세탁 · 말리기 전 확인", "세탁 후 밝게 확인. 갈색 남은 채 말리지 마세요.")
    ),
    "S_MILK_COFFEE": (
        _START
        + _step(
            1,
            "순서 지키기 · 단백질·지방 먼저",
            "①효소·주방세제 → ②식초. 순서를 바꾸면 색소가 더 굳을 수 있어요.\n"
            "찬물만. 온수·건조기 금지.",
        )
        + "\n"
        + _step(
            2,
            "주방세제·효소로 지방·단백질",
            "주방세제를 약하게 찍어 바르고 30초 기다리세요.\n"
            "효소에 15~30분 담가 주세요. 실크·울은 효소 금지 → 중성세제만.",
        )
        + "\n"
        + _step(
            3,
            "식초로 탄닌 빼기",
            "흰 식초 Cap1 + 물 Cap4(약 1:4). 얼룩에 바르고 5~10분.\n"
            "유색·실크·울은 산소 금지. 흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(4, "세탁 · 확인", "세탁 후 밝게 확인. 갈색 남은 채 말리지 마세요.")
    ),
    "S_RED_WINE": (
        _START
        + _step(
            1,
            "흡수 · 소금 금지",
            "흰 천으로 위에서 꾹꾹 눌러 흡수하세요. 옆으로 문지르지 마세요.\n"
            "소금을 뿌리지 마세요(더 남을 수 있어요).",
        )
        + "\n"
        + _step(
            2,
            "흰옷 / 유색 나누기",
            "흰 면·린넨: 산소에 15~45분(구석 테스트).\n"
            "유색·실크·울: 식초 Cap1+물 Cap4만 반복. 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 밝게 확인. 자줏빛 남은 채 말리지 마세요.")
    ),
    "S_WHITE_WINE_BEER": (
        _START
        + _step(
            1,
            "바로 흡수 · 나중에 누렇게 될 수 있음",
            "흰 천으로 꾹꾹 흡수하세요.\n"
            "당분이 남아 나중에 누렇게 될 수 있으니 손님께 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "찬물·세제 → (흰옷) 산소",
            "찬물·중성세제로 국소 처리하세요.\n"
            "흰옷만 산소(테스트). 유색·실크·울은 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 밝게 확인. 누런기 남은 채 말리지 마세요.")
    ),
    "S_BUBBLE_TEA": (
        _START
        + _step(
            1,
            "층 순서 지키기",
            "①지방(펄·밀크) → ②단백질 → ③탄닌(차). 순서가 중요합니다.\n"
            "찬물만. 온수 금지.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 효소",
            "주방세제를 약하게 찍어 바르고 30초.\n"
            "효소 15~30분. 실크·울은 효소 금지.",
        )
        + "\n"
        + _step(
            3,
            "식초로 차 색소",
            "식초 Cap1+물 Cap4, 5~10분.\n"
            "흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(4, "세탁 · 확인", "세탁 후 확인. 갈색 남은 채 말리지 마세요.")
    ),
    "S_LIPSTICK": (
        _START
        + _step(
            1,
            "겉 왁스만 살살",
            "부드러운 솔·티슈로 겉만 살살. Cap2 안쪽으로 긁지 마세요.\n"
            "옆으로 문지르면 번집니다.",
        )
        + "\n"
        + _step(
            2,
            "알코올로 안쪽→바깥 찍어 빼기",
            "옷을 뒤집고 흡수지를 깔아 주세요.\n"
            "알코올을 흰 천에 묻혀 안쪽에서 바깥으로 꾹꾹. 3~5회, 천 매번 교체.\n"
            "구석 테스트 먼저.",
        )
        + "\n"
        + _step(
            3,
            "주방세제로 남은 색",
            "미지근한 물(약 40°)에 주방세제를 풀어 남은 색을 살살.\n"
            "실크·울은 미지근한 물 금지 → 찬물·중성만.",
        )
        + "\n"
        + _step(4, "세탁 · 확인", "세탁 후 확인. 빨간 남은 채 말리지 마세요.")
    ),
    "S_FOUNDATION": (
        _START
        + _step(
            1,
            "겉만 살살 · 실리콘 먼저",
            "티슈로 겉만 살살. 문지르지 마세요.\n"
            "주방세제를 약하게 찍어 바르고 1분 기다리세요(실리콘·오일).",
        )
        + "\n"
        + _step(
            2,
            "색소는 알코올(테스트)",
            "구석 테스트 후 OK면 알코올로 꾹꾹 찍어 빼세요. 천 교체.\n"
            "실크·울은 약하게·짧게.",
        )
        + "\n"
        + _step(3, "찬물 헹굼 · 세탁", "찬물로 헹군 뒤 세탁하세요. 남은 채 말리지 마세요.")
    ),
    "S_BBQ_SAUCE": (
        _START
        + _step(
            1,
            "3층 순서",
            "①효소(단백질) → ②주방세제(오일) → ③식초(색소).\n"
            "찬물만.",
        )
        + "\n"
        + _step(
            2,
            "효소 → 주방세제 → 식초",
            "효소 15~30분 → 주방세제 30초 → 식초 Cap1+물 Cap4.\n"
            "실크·울은 효소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "흰옷만 산소(테스트). 빨간·갈색 남은 채 말리지 마세요.")
    ),
    "S_MAYO": (
        _START
        + _step(
            1,
            "지방 먼저 · 단백질 나중",
            "①주방세제(지방) → ②효소(계란·단백질). 순서 바꾸지 마세요.\n"
            "온수 금지(단백질이 굳습니다).",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 효소",
            "주방세제를 약하게 찍어 바르고 1분.\n"
            "효소 15~30분. 실크·울은 효소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 기름기 남은 채 말리지 마세요.")
    ),
    "S_BUTTER": (
        _START
        + _step(
            1,
            "흡착 · 열고착 주의",
            "티슈로 겉 버터를 살살 걷어 주세요. 문지르지 마세요.\n"
            "미끄럼·냄새 남은 채 건조기 금지.",
        )
        + "\n"
        + _step(
            2,
            "주방세제·효소",
            "주방세제를 약하게 찍어 바르고 1~2분.\n"
            "효소 15~30분(실크·울 제외).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 기름 자국 남은 채 말리지 마세요.")
    ),
    "S_FISH_SAUCE": (
        _START
        + _step(
            1,
            "냄새 잔존 설명 · 찬물",
            "냄새·얼룩이 남을 수 있다고 손님께 먼저 말씀하세요.\n"
            "찬물만. 온수·건조기 금지.",
        )
        + "\n"
        + _step(
            2,
            "효소 → 식초",
            "효소 15~30분 → 식초 Cap1+물 Cap4.\n"
            "실크·울: 효소 금지 → 중성세제·찬물 + 식초만 약하게.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 냄새·색 확인. 남은 채 말리지 마세요.")
    ),
    "S_BABY_FORMULA": (
        _START
        + _step(
            1,
            "락스 금지 · 찬물",
            "락스 절대 금지(철·단백질이 더 굳을 수 있어요).\n"
            "찬물만. 온수 금지.",
        )
        + "\n"
        + _step(
            2,
            "효소에 담가 주세요",
            "효소 20~40분. 중간에 한 번 흔들어 주세요.\n"
            "실크·울은 효소 금지 → 중성세제·찬물만.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 누런기 남은 채 말리지 마세요.")
    ),
    "S_COLLAR_STAIN": (
        _START
        + _step(
            1,
            "락스 금지 · 효소 우선",
            "목 때는 단백질·피지입니다. 락스는 더 누렇게 만들 수 있어요.\n"
            "효소를 목 둘레에만 약하게 바르세요.",
        )
        + "\n"
        + _step(
            2,
            "효소 담그기 · 살살",
            "효소에 20~40분. 솔로 세게 문지르지 마세요.\n"
            "흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 목 안쪽을 밝게 확인하세요.")
    ),
    "S_SWEAT_YELLOW": (
        _START
        + _step(
            1,
            "락스 금지 · 황변 설명",
            "누런 땀은 락스로 더 심해질 수 있어요.\n"
            "완전 제거가 어렵다고 손님께 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "효소 → (흰옷) 산소",
            "효소 20~40분 → 흰옷만 산소(테스트).\n"
            "유색·실크·울은 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 누런기 남은 채 말리지 마세요.")
    ),
    "S_DYE_TRANSFER": (
        _START
        + _step(
            1,
            "즉시 분리 · 건조기 금지",
            "다른 옷과 바로 분리하세요. 건조기·다림질 금지(고착).\n"
            "이미 건조기 통과면 복원이 매우 어렵습니다 — 손님께 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "찬물 헹굼 · (흰옷만) 주의 락스",
            "찬물로 바로 헹구세요.\n"
            "흰 100% 면·폴리만: 매니저 확인 후 락스 5~10분 상한 → 즉시 완전 헹굼.\n"
            "스판덱스·유색·실크·울: 락스 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 이염 남은 채 말리지 마세요.")
    ),
}

from owner_hand_motions_ext import (  # noqa: E402
    HAND_MOTIONS_KO_L2_REST,
    HAND_MOTIONS_KO_L3,
    HAND_MOTIONS_KO_TAIL,
    HAND_MOTIONS_VI_EXTRA,
    HAND_MOTIONS_VI_TAIL,
)

HAND_MOTIONS_KO.update(HAND_MOTIONS_KO_L2_REST)
HAND_MOTIONS_KO.update(HAND_MOTIONS_KO_L3)
HAND_MOTIONS_KO.update(HAND_MOTIONS_KO_TAIL)

_L1_REQUIRED = {
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
    "S_KIMCHI",
    "S_CHOCOLATE",
    "S_MUD",
    "S_GRASS",
    "S_INK_PEN",
    "S_SOY_SAUCE",
}
_L2_PRIORITY = {
    "S_BLOOD_DRY",
    "S_MILK_COFFEE",
    "S_RED_WINE",
    "S_WHITE_WINE_BEER",
    "S_BUBBLE_TEA",
    "S_LIPSTICK",
    "S_FOUNDATION",
    "S_BBQ_SAUCE",
    "S_MAYO",
    "S_BUTTER",
    "S_FISH_SAUCE",
    "S_BABY_FORMULA",
    "S_COLLAR_STAIN",
    "S_SWEAT_YELLOW",
    "S_DYE_TRANSFER",
}
_L2_REST = set(HAND_MOTIONS_KO_L2_REST.keys())
_L3_REQUIRED = set(HAND_MOTIONS_KO_L3.keys())
assert _L1_REQUIRED.issubset(HAND_MOTIONS_KO.keys()), "L1 hand-motion coverage incomplete"
assert _L2_PRIORITY.issubset(HAND_MOTIONS_KO.keys()), "L2 priority hand-motion coverage incomplete"
assert _L2_REST.issubset(HAND_MOTIONS_KO.keys()), "L2 rest hand-motion coverage incomplete"
assert _L3_REQUIRED.issubset(HAND_MOTIONS_KO.keys()), "L3 hand-motion coverage incomplete"

_START_VI = "▼ Bắt đầu — làm lần lượt từ trên xuống\n\n"


def _step_vi(n: int, title: str, body: str) -> str:
    return f"Bước {n}. {title}\n─────\n{body.strip()}\n"


# Top-frequency VI hand motions (franchise HQ). Cap = lực, not ml.
HAND_MOTIONS_VI: dict[str, str] = {
    "S_HAIR_DYE": (
        _START_VI
        + _step_vi(
            1,
            "Đeo găng và xả nước lạnh",
            "Đeo găng trước.\n"
            "Xả nước lạnh từ mặt trái 2–3 phút.\n"
            "Không chà mạnh — chỉ để nước cuốn màu.\n"
            "→ Thấy màu ra theo nước là đang đúng.",
        )
        + "\n"
        + _step_vi(
            2,
            "Chấm cồn lấy màu",
            "① Lộn trái áo\n"
            "② Lót khăn trắng sạch dưới vết\n"
            "③ Thấm cồn lên khăn trắng khác (không đổ trực tiếp lên áo)\n"
            "④ Ấn thẳng đứng 3 giây → nhấc (không chà ngang)\n"
            "⑤ Màu sang khăn dưới = đang lấy được\n"
            "⑥ Khăn dính màu → đổi khăn mới ngay\n"
            "⑦ Lặp 5–10 lần. Hết dính màu → bước tiếp",
        )
        + "\n"
        + _step_vi(
            3,
            "Ngâm oxy (chỉ áo trắng!)",
            "⚠️ Áo màu / lụa / len → bỏ bước này.\n"
            "Pha 1L nước ấm nhẹ + 1 thìa oxy.\n"
            "Chỉ ngâm chỗ vết. (Thời gian theo 【Thời gian ngâm】 phía trên)",
        )
        + "\n"
        + _step_vi(
            4,
            "Giặt",
            "Giặt theo nhiệt độ cho phép.\n"
            "Nhắc khách trước: có thể còn vết.",
        )
    ),
    "S_BLOOD_FRESH": (
        _START_VI
        + _step_vi(
            1,
            "Chỉ xả nước lạnh",
            "Đeo găng.\n"
            "Chỉ nước lạnh. Nước nóng tuyệt đối không — máu sẽ đông.\n"
            "Xả mặt trái 2–3 phút. Không chà mạnh.",
        )
        + "\n"
        + _step_vi(
            2,
            "Ngâm enzyme (hoặc trung tính)",
            "Pha enzyme với nước lạnh rồi ngâm. (Theo 【Thời gian ngâm】)\n"
            "Lụa/len: chỉ trung tính, ngắn, hỏi quản lý.",
        )
        + "\n"
        + _step_vi(
            3,
            "Xả và giặt",
            "Xả lạnh kỹ rồi giặt.\n"
            "Áo trắng còn vết: hỏi quản lý rồi mới xem oxy.",
        )
    ),
    "S_BLOOD_DRY": (
        _START_VI
        + _step_vi(
            1,
            "Hỏi quản lý · báo vết nâu",
            "Máu khô khó sạch hoàn toàn. Báo khách trước: có thể còn vết nâu / chỉ sạch một phần.\n"
            "Cấm nước nóng và máy sấy (sẽ cố định hơn).",
        )
        + "\n"
        + _step_vi(
            2,
            "Ngâm lạnh + enzyme",
            "Pha enzyme nước lạnh, ngâm 20–45 phút. Lắc nhẹ giữa chừng.\n"
            "Lụa/len: cấm enzyme → chỉ trung tính + lạnh.",
        )
        + "\n"
        + _step_vi(
            3,
            "(Chỉ cotton trắng) thử H2O2",
            "Chỉ cotton trắng: nhỏ 1 giọt H2O2 3% (nhà thuốc) góc kín · 30 giây.\n"
            "OK → thấm lên vết 10 phút, xả lạnh ngay.\n"
            "Áo màu / lụa / len → bỏ bước này.",
        )
        + "\n"
        + _step_vi(4, "Giặt · kiểm trước khi sấy", "Giặt xong kiểm dưới ánh sáng. Còn nâu → không sấy.")
    ),
    "S_MILK_COFFEE": (
        _START_VI
        + _step_vi(
            1,
            "Giữ thứ tự · đạm/mỡ trước",
            "① Enzyme / nước rửa chén → ② giấm. Đổi thứ tự dễ cố định màu.\n"
            "Chỉ nước lạnh. Cấm nóng / sấy trước.",
        )
        + "\n"
        + _step_vi(
            2,
            "Nước rửa chén + enzyme",
            "Chấm nhẹ nước rửa chén, chờ 30 giây.\n"
            "Ngâm enzyme 15–30 phút. Lụa/len: cấm enzyme → chỉ trung tính.",
        )
        + "\n"
        + _step_vi(
            3,
            "Giấm lấy tannin",
            "Giấm trắng Cap1 + nước Cap4 (≈1:4). Thoa lên vết 5–10 phút.\n"
            "Áo màu / lụa / len: cấm oxy. Áo trắng mới oxy (sau thử góc).",
        )
        + "\n"
        + _step_vi(4, "Giặt · kiểm", "Giặt xong kiểm. Còn nâu → không sấy.")
    ),
    "S_RED_WINE": (
        _START_VI
        + _step_vi(
            1,
            "Thấm · không rắc muối",
            "Ấn khăn trắng từ trên xuống. Không chà ngang.\n"
            "Không rắc muối (có thể để lại vết).",
        )
        + "\n"
        + _step_vi(
            2,
            "Áo trắng / áo màu",
            "Cotton/linen trắng: ngâm oxy 15–45 phút (thử góc).\n"
            "Áo màu / lụa / len: chỉ giấm Cap1+nước Cap4 lặp lại. Cấm oxy.",
        )
        + "\n"
        + _step_vi(3, "Giặt · kiểm", "Giặt xong kiểm. Còn tím → không sấy.")
    ),
    "S_BLACK_COFFEE": (
        _START_VI
        + _step_vi(
            1,
            "Lộn trái · thấm lạnh",
            "Lộn trái áo.\n"
            "Thấm nước lạnh từ trong. Không chà mạnh — dễ loang.",
        )
        + "\n"
        + _step_vi(
            2,
            "Pha giấm 1:4 và xịt",
            "Giấm trắng 1 : nước 4 (vd 50ml giấm + 200ml nước).\n"
            "Cho vào bình xịt, ghi nhãn 「giấm 1:4」.\n"
            "Xịt 1–2 lần lên vết, chờ 5–15 phút. Không ướt đẫm.\n"
            "Xả lạnh.",
        )
        + "\n"
        + _step_vi(
            3,
            "Giặt",
            "Giặt bình thường.\n"
            "Áo trắng còn vết: thử góc rồi oxy (bỏ nếu lụa/len/áo màu).",
        )
    ),
    "S_LIPSTICK": (
        _START_VI
        + _step_vi(
            1,
            "Chỉ lấy lớp sáp ngoài",
            "Dùng bàn chải mềm / khăn giấy, nhẹ trên bề mặt. Không cạo sâu Cap2.\n"
            "Chà ngang sẽ loang.",
        )
        + "\n"
        + _step_vi(
            2,
            "Chấm cồn từ trong ra ngoài",
            "Lộn trái, lót khăn thấm.\n"
            "Thấm cồn khăn trắng, ấn từ trong ra ngoài. 3–5 lần, đổi khăn mỗi lần.\n"
            "Thử góc trước.",
        )
        + "\n"
        + _step_vi(
            3,
            "Nước rửa chén lấy màu còn lại",
            "Nước ấm nhẹ (~40°) + nước rửa chén, chà nhẹ.\n"
            "Lụa/len: cấm ấm → chỉ lạnh + trung tính.",
        )
        + "\n"
        + _step_vi(4, "Giặt · kiểm", "Giặt xong kiểm. Còn đỏ → không sấy.")
    ),
    "S_KIMCHI": (
        _START_VI
        + _step_vi(
            1,
            "Gỡ ớt bột / xác",
            "Phủi hoặc gạt nhẹ ớt bột.\n"
            "Không chà — dễ loang.",
        )
        + "\n"
        + _step_vi(
            2,
            "Xả lạnh · chấm nước rửa chén",
            "Xả lạnh từ trong.\n"
            "Chấm 1–2 giọt nước rửa chén lên khăn, thoa, chờ 30 giây.\n"
            "Chải mềm nhẹ → xả ngay.",
        )
        + "\n"
        + _step_vi(
            3,
            "Giấm 1:4",
            "Xịt/thoa giấm 1:4, chờ 5–10 phút (màu + mùi).\n"
            "Xả rồi: chỉ áo trắng oxy sau thử góc.\n"
            "⚠️ Áo màu: cấm oxy. Không dùng kem đánh răng.",
        )
        + "\n"
        + _step_vi(
            4,
            "Giặt",
            "Giặt.\n"
            "Còn màu/mùi ớt → không sấy.",
        )
    ),
    "S_COOKING_OIL": (
        _START_VI
        + _step_vi(
            1,
            "Hút dầu · kiểm trơn",
            "Rắc bột (tinh bột / bột mì) lên vết, chờ rồi phủi.\n"
            "Còn trơn / còn mùi → chưa được sấy.",
        )
        + "\n"
        + _step_vi(
            2,
            "Nước rửa chén · enzyme",
            "Chấm nước rửa chén, chờ 1–2 phút.\n"
            "Ngâm enzyme 15–30 phút (trừ lụa/len).",
        )
        + "\n"
        + _step_vi(3, "Giặt · kiểm", "Giặt xong kiểm. Còn dầu → không sấy.")
    ),
    "S_DYE_TRANSFER": (
        _START_VI
        + _step_vi(
            1,
            "Tách ngay · cấm sấy",
            "Tách khỏi đồ khác ngay. Cấm sấy / ủi (cố định).\n"
            "Đã qua máy sấy → rất khó phục hồi — báo khách trước.",
        )
        + "\n"
        + _step_vi(
            2,
            "Xả lạnh · (chỉ trắng) javel thận trọng",
            "Xả lạnh ngay.\n"
            "Chỉ cotton/poly trắng 100%: hỏi quản lý rồi javel tối đa 5–10 phút → xả kỹ ngay.\n"
            "Spandex / áo màu / lụa / len: cấm javel.",
        )
        + "\n"
        + _step_vi(3, "Giặt · kiểm", "Giặt xong kiểm. Còn phai → không sấy.")
    ),
}

HAND_MOTIONS_VI.update(HAND_MOTIONS_VI_EXTRA)
HAND_MOTIONS_VI.update(HAND_MOTIONS_VI_TAIL)

_VI_CORE = {
    "S_HAIR_DYE",
    "S_BLOOD_FRESH",
    "S_BLOOD_DRY",
    "S_MILK_COFFEE",
    "S_RED_WINE",
    "S_BLACK_COFFEE",
    "S_LIPSTICK",
    "S_KIMCHI",
    "S_COOKING_OIL",
    "S_DYE_TRANSFER",
}
assert _VI_CORE.issubset(HAND_MOTIONS_VI.keys()), "VI core hand-motion coverage incomplete"
assert set(HAND_MOTIONS_VI_EXTRA).issubset(HAND_MOTIONS_VI.keys()), "VI extra merge failed"
assert set(HAND_MOTIONS_KO_TAIL).issubset(HAND_MOTIONS_KO.keys()), "KO tail merge failed"
assert set(HAND_MOTIONS_VI_TAIL).issubset(HAND_MOTIONS_VI.keys()), "VI tail merge failed"


def protocol_motion_gaps() -> list[str]:
    """PROTOCOL_BUILDERS ids missing KO hand motions (should be empty)."""
    from protocol import PROTOCOL_BUILDERS

    return sorted(sid for sid in PROTOCOL_BUILDERS if sid not in HAND_MOTIONS_KO)


def build_hand_motions(stain_id: str, lang: str = "ko") -> str:
    """KO scripts (L1/L2/L3); VI covered set; EN empty (SOP body fallback)."""
    sid = str(stain_id or "").strip()
    if lang == "ko":
        return HAND_MOTIONS_KO.get(sid, "")
    if lang == "vi":
        return HAND_MOTIONS_VI.get(sid, "")
    return ""


def has_hand_motions(stain_id: str, lang: str = "ko") -> bool:
    return bool(build_hand_motions(stain_id, lang))


def l1_motion_coverage() -> list[str]:
    """Return L1 stain ids missing hand motions (should be empty)."""
    from stain_level_tags import L1

    return sorted(sid for sid in L1 if sid not in HAND_MOTIONS_KO)


def l2_priority_coverage() -> list[str]:
    """Return priority L2 stain ids missing hand motions (should be empty)."""
    return sorted(sid for sid in _L2_PRIORITY if sid not in HAND_MOTIONS_KO)


def l2_rest_coverage() -> list[str]:
    return sorted(sid for sid in _L2_REST if sid not in HAND_MOTIONS_KO)


def l3_motion_coverage() -> list[str]:
    return sorted(sid for sid in _L3_REQUIRED if sid not in HAND_MOTIONS_KO)


def vi_priority_coverage() -> list[str]:
    """Return VI core ids missing scripts (should be empty)."""
    return sorted(sid for sid in _VI_CORE if sid not in HAND_MOTIONS_VI)
