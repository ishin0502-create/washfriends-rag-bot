# -*- coding: utf-8 -*-
"""Owner Zalo clarity: 1통 흐름 / 2통 손동작 + short common blocks.

Does not change chemistry order — only presentation for junior staff.
"""
from __future__ import annotations

import re
from typing import Optional

# Invisible to owners in /ask (shown as blank line join); Zalo splits on this.
ZALO_MSG_SPLIT = "\n<<<ZALO_MSG2>>>\n"

BLOT_CHEM_CODES = frozenset({"A1", "A2", "D1"})

_SUPERVISOR = {
    "ko": "⚠️ 이 얼룩은 혼자 하지 마시고, 매니저(또는 경력 직원)와 확인한 뒤에 시작해 주세요.",
    "vi": "⚠️ Vết này cần giám sát. Hãy hỏi quản lý trước khi bắt đầu.",
    "en": "⚠️ Supervisor needed. Check with a manager before you start.",
}

_GRADE_FOOTER = {
    "ko": {
        1: "【다시 한번 고객 고지】 완전 제거는 보장드리기 어렵습니다. 잔색이 남을 수 있어요.",
        2: "【다시 한번 고객 고지】 완전 제거는 어렵고 잔색이 남을 수 있어요. 그래도 진행할까요?",
        3: "【다시 한번 고객 고지】 매장에서 안전하게 처리하기 어렵습니다. 전문 의뢰 또는 접수 반려를 안내해 주세요.",
    },
    "vi": {
        1: "【Nhắc khách】 Không đảm bảo sạch 100% — có thể còn vết mờ.",
        2: "【Nhắc khách】 Khó sạch hoàn toàn, có thể còn vết. Anh/Chị vẫn muốn tiếp tục chứ ạ?",
        3: "【Nhắc khách】 Cửa hàng khó xử lý an toàn — giới thiệu chuyên nghiệp hoặc từ chối tiếp nhận.",
    },
    "en": {
        1: "【Tell the guest again】 Full removal is not guaranteed — marks may remain.",
        2: "【Tell the guest again】 Full removal is unlikely — residual marks may remain. Still proceed?",
        3: "【Tell the guest again】 Unsafe in-store — refer out or decline the job.",
    },
}

# Soft outlook — no percentages (B-6): grade-based expected result for message 1
_SOFT_OUTLOOK = {
    "ko": {
        1: "◆ 【예상 결과】 시도해 볼 수 있어요 — 다만 완전 제거는 보장하지 않아요.",
        2: "◆ 【예상 결과】 부분 제거만 기대하세요 — 잔색·잔영이 남을 수 있어요. 접수 때 동의를 받으세요.",
        3: "◆ 【예상 결과】 복원이 어렵습니다 — 거절 또는 전문 의뢰를 먼저 검토하세요.",
    },
    "vi": {
        1: "◆ 【Kết quả kỳ vọng】 Có thể thử — không đảm bảo sạch hết.",
        2: "◆ 【Kết quả kỳ vọng】 Chỉ kỳ vọng sạch một phần — có thể còn vết. Cần đồng ý khi nhận đồ.",
        3: "◆ 【Kết quả kỳ vọng】 Khó phục hồi — ưu tiên từ chối hoặc gửi chuyên.",
    },
    "en": {
        1: "◆ 【Expected result】 Worth trying — full removal is not guaranteed.",
        2: "◆ 【Expected result】 Expect partial removal only — marks may remain. Get consent at intake.",
        3: "◆ 【Expected result】 Unlikely to restore — refuse intake or refer out first.",
    },
}

# Compressed common don'ts (why one line each)
COMMON_DONTS_KO = [
    "뜨거운 물로 헹구지 마세요 → 얼룩이 섬유에 붙어 잘 안 빠져요",
    "세게 문지르지 마세요 → 번지고 원단이 상해요. 위에서 꾹꾹 눌러 흡수하세요",
    "약품을 옷에 직접 붓지 마세요 → 한쪽에 몰려 번져요. 흰 천에 묻혀 찍어 주세요",
    "다른 약품을 한꺼번에 섞지 마세요 → 한 약 쓰고 → 헹구고 → 다음 약 순서예요",
    "잔색 남은 채 건조기·다림질 하지 마세요 → 열이면 자국이 영구로 남아요",
]

STAIN_DONTS_KO: dict[str, list[str]] = {
    "S_HAIR_DYE": [
        "유색 옷에 산소표백제 쓰지 마세요",
        "실크·울·가죽에 알코올 함부로 쓰지 마세요 (구석 테스트 필수)",
        "물든 흰 천을 재사용하지 마세요 → 색소가 다시 옷으로 가요",
        "알코올은 밀폐 공간에서 쓰지 마세요 → 환기하세요 (냄새·화재)",
    ],
    "S_INK_PEN": [
        "락스(염소)로 잉크를 지우려 하지 마세요 → 회색 자국이 남을 수 있어요",
    ],
    "S_BLOOD_FRESH": [
        "뜨거운 물로 피를 헹구지 마세요 → 단백질이 굳어 더 안 빠져요",
    ],
    "S_BLOOD_DRY": [
        "뜨거운 물로 피를 헹구지 마세요 → 단백질이 굳어 더 안 빠져요",
    ],
    "S_KIMCHI": [
        "치약으로 지우지 마세요",
        "유색 옷에 산소표백제 쓰지 마세요 (고추 색소+원단 색 같이 빠질 수 있어요)",
        "고추 색소·냄새 남은 채 말리지 마세요",
    ],
    "S_EGG": [
        "처음부터 온수·건조기 쓰지 마세요 → 단백질이 익어 고착돼요",
    ],
    "S_MILK": [
        "온수 먼저 쓰지 마세요",
        "분유처럼 락스 쓰지 마세요",
    ],
    "S_COOKING_OIL": [
        "물부터 부어 문지르지 마세요",
        "미끄러운 채로 건조기·다림질 하지 마세요 → 열고착돼요",
    ],
    "S_CHOCOLATE": [
        "지방·색소 남은 채 건조기·다림질 하지 마세요",
    ],
    "S_SOFT_DRINK": [
        "끈적·단맛 남은 채 말리지 마세요 → 황변돼요",
    ],
    "S_GRASS": [
        "초록 남은 채 말리지 마세요",
        "알코올 구석 테스트 없이 바로 쓰지 마세요 (프린트·실크)",
    ],
    "S_SWEAT_FRESH": [
        "황변에 락스 쓰지 마세요 → 더 누래질 수 있어요",
    ],
    "S_SOY_SAUCE": [
        "이른 열·건조로 검정 색소를 고착시키지 마세요",
    ],
    "S_KETCHUP": [
        "이른 열·건조로 붉은 색소를 고착시키지 마세요",
    ],
    "S_TOMATO_SAUCE": [
        "문질러 붉은색을 번지게 하지 마세요",
        "잔색 채 말리지 마세요",
    ],
    # L2 priority
    "S_MILK_COFFEE": [
        "식초를 효소·세제보다 먼저 쓰지 마세요 → 색소가 더 굳을 수 있어요",
        "온수·건조기 먼저 쓰지 마세요",
    ],
    "S_RED_WINE": [
        "소금을 뿌리지 마세요 → 자국이 더 남을 수 있어요",
        "유색·실크·울에 산소표백제 쓰지 마세요",
    ],
    "S_WHITE_WINE_BEER": [
        "당분 남은 채 말리지 마세요 → 나중에 누렇게 돼요",
    ],
    "S_BUBBLE_TEA": [
        "지방·단백질보다 식초를 먼저 쓰지 마세요",
        "온수 먼저 쓰지 마세요",
    ],
    "S_LIPSTICK": [
        "옆으로 문지르지 마세요 → 번져요",
        "겉 왁스를 안쪽으로 깊게 긁지 마세요",
    ],
    "S_MASCARA": [
        "옆으로 문지르지 마세요 → 번져요",
        "실크·울에 알코올 함부로 쓰지 마세요 (구석 테스트)",
    ],
    "S_FOUNDATION": [
        "세게 문지르지 마세요 → 실리콘·색소가 번져요",
    ],
    "S_BBQ_SAUCE": [
        "효소→세제→식초 순서를 바꾸지 마세요",
    ],
    "S_MAYO": [
        "온수 먼저 쓰지 마세요 → 계란 단백질이 익어 고착돼요",
        "효소를 주방세제보다 먼저 쓰지 마세요(지방이 남아요)",
    ],
    "S_BUTTER": [
        "미끄러운 채로 건조기·다림질 하지 마세요",
    ],
    "S_FISH_SAUCE": [
        "온수·건조기 먼저 쓰지 마세요",
        "냄새 남을 수 있다는 안내 없이 보장하지 마세요",
    ],
    "S_BABY_FORMULA": [
        "락스 절대 쓰지 마세요 → 철·단백질이 더 굳을 수 있어요",
        "온수 먼저 쓰지 마세요",
    ],
    "S_COLLAR_STAIN": [
        "목 때에 락스 쓰지 마세요 → 더 누래질 수 있어요",
        "솔로 세게 문지르지 마세요",
    ],
    "S_SWEAT_YELLOW": [
        "황변에 락스 쓰지 마세요 → 더 누래져요",
    ],
    "S_DYE_TRANSFER": [
        "건조기·다림질 하지 마세요 → 이염이 고착돼요",
        "유색·스판덱스·실크·울에 락스 쓰지 마세요",
    ],
}

STAIN_STATUS_KO: dict[str, str] = {
    "S_HAIR_DYE": (
        "◆ 【먼저 확인】 염색약이 어떤 상태인가요?\n"
        "· 아직 젖어 있다(만지면 손에 묻음) → Step 1(찬물)부터. 빠를수록 좋아요\n"
        "· 이미 말랐다 → Step 1 건너뛰고 Step 2(알코올)부터. 잔색 가능성을 고객께 먼저 말씀하세요\n"
        "· 다림질·건조기를 이미 거쳤다 → 거의 안 빠져요(열고착). 전문 의뢰 또는 정중히 거절해 주세요\n"
        "\n"
        "◆ 【고객께 먼저】 염색약은 강한 색소라 완전 제거가 어려울 수 있어요. "
        "최선을 다하지만 자국이 남을 수 있습니다. 그래도 진행할까요?"
    ),
    "S_BLOOD_FRESH": (
        "◆ 【먼저 확인】 핏자국이 어떤 상태인가요?\n"
        "· 아직 젖어 있다(빨간빛) → 한 줄 순서 1번부터 하세요\n"
        "· 말라 갈색이다 → 마른 핏자국 요령으로 진행합니다(찬물·효소 중심)\n"
        "· 이미 뜨거운 물로 빨았다 → 거의 안 빠져요. 고객께 솔직히 말씀해 주세요"
    ),
    "S_BLOOD_DRY": (
        "◆ 【먼저 확인】 마른 핏자국입니다\n"
        "· 완전 제거보다 부분 제거·갈색 잔영을 손님께 먼저 말씀하세요\n"
        "· 매니저·경력자 확인 후 진행하세요\n"
        "· 이미 온수·건조기를 거쳤다면 거의 안 빠져요"
    ),
    "S_MILK_COFFEE": (
        "◆ 【먼저 확인】 라떼·밀크커피 순서\n"
        "· 반드시 단백질·지방(효소·세제) → 식초 순서입니다\n"
        "· 순서를 바꾸면 색소가 더 굳을 수 있어요\n"
        "· 이미 말랐거나 열을 가했다면 잔색 가능성을 손님께 말씀하세요"
    ),
    "S_LIPSTICK": (
        "◆ 【먼저 확인】 립스틱 3층\n"
        "· 겉 왁스 → 알코올 찍기 → 세제 순서입니다. 문지르지 마세요\n"
        "· 유색·실크는 매니저 확인 후 진행하세요\n"
        "· 열고착·건조기 지남 → 잔색 가능 — 사전 고지"
    ),
    "S_MASCARA": (
        "◆ 【먼저 확인】 마스카라\n"
        "· 문지르면 번짐 — 찍어 흡수만\n"
        "· 잔색은 알코올(70% IPA)·환기 · 실크는 매니저 확인\n"
        "· 검은 잔색 남은 채 말리지 마세요"
    ),
    "S_DYE_TRANSFER": (
        "◆ 【먼저 확인】 이염\n"
        "· 다른 옷과 바로 분리 · 건조기 금지\n"
        "· 이미 건조기를 거쳤다면 복원이 매우 어렵습니다 — 손님께 먼저 말씀하세요\n"
        "· 락스는 흰 100% 면·폴리만, 매니저 확인 후"
    ),
    "S_BLACK_COFFEE": (
        "◆ 【먼저 확인】 블랙커피\n"
        "· 아직 젖어 있다 → 한 줄 순서 1번(흡수·찬물)부터\n"
        "· 이미 말랐다 → 잔색 가능 — 고객 동의 후 식초 중심으로\n"
        "· 건조기·다리미 지남 → 열고착. 부분 제거만 기대·사전 고지"
    ),
    "S_COOKING_OIL": (
        "◆ 【먼저 확인】 식용유·기름때\n"
        "· 물부터 붓지 마세요 → 전분·흡착 후 세제\n"
        "· 이미 건조기를 돌렸다 → 열고착. 완전 제거 어려움 — 먼저 고지\n"
        "· 미끄러움이 남으면 말리지 마세요"
    ),
    "S_INK_PEN": (
        "◆ 【먼저 확인】 볼펜·잉크\n"
        "· 안쪽에서만 찍어 빼기 · 문지르면 번짐\n"
        "· 실크·울·프린트 → 구석 테스트·매니저 확인\n"
        "· 열고착이면 성공 낮음 — 사전 고지"
    ),
    "S_MUD": (
        "◆ 【먼저 확인】 진흙\n"
        "· 젖은 채 문지르지 마세요 → 먼저 말려 털기\n"
        "· 적토·붉은 흙이면 일반 진흙과 다름(라테라이트 요령)\n"
        "· 락스로 철 성분을 건드리지 마세요"
    ),
    "S_KIMCHI": (
        "◆ 【먼저 확인】 김치국\n"
        "· 고춧가루·건더기 먼저 제거\n"
        "· 유색옷 산소 신중 · 치약 금지\n"
        "· 고추 색소·냄새 남은 채 말리지 마세요"
    ),
    "S_SOY_SAUCE": (
        "◆ 【먼저 확인】 간장\n"
        "· 즉시 찬물·흡수 · 이른 열 금지\n"
        "· 이미 말랐거나 건조기 지남 → 잔색·검정 잔영 고지"
    ),
    "S_SWEAT_YELLOW": (
        "◆ 【먼저 확인】 겨드랑이·땀 황변\n"
        "· 신선 땀과 다릅니다 — 단백질+데오 잔여가 누런 경우가 많아요\n"
        "· 락스(염소) 금지 → 더 누래질 수 있어요\n"
        "· 완전 복원 어려움 — 부분 개선·사전 동의를 받으세요"
    ),
    "S_SHIRT_YELLOW": (
        "◆ 【먼저 확인】 와이셔츠·흰옷 황변\n"
        "· 목·겨드랑·전체 중 어디인지 확인\n"
        "· 락스 금지(단백질 황변에 쓰면 더 누래요)\n"
        "· 효소 → 산소 순서 · 완전 하얗게는 보장하지 마세요"
    ),
    "S_RED_WINE": (
        "◆ 【먼저 확인】 레드와인\n"
        "· 아직 젖어 있다 → 즉시 흡수(소금 금지)·찬물\n"
        "· 이미 말랐다 → 잔색(자줏빛) 가능성 높음 — 사전 고지\n"
        "· 실크·울 → 매장 강처리는 위험. 전문 의뢰·거절을 먼저 검토하세요\n"
        "· 건조기·다리미 지남 → 열고착. 거의 어려움"
    ),
}

STAIN_STATUS_VI: dict[str, str] = {
    "S_HAIR_DYE": (
        "◆ 【Kiểm tra trước】 Thuốc nhuộm đang ở trạng thái nào?\n"
        "· Còn ướt (chạm vào dính tay) → bắt đầu Step 1 (xả lạnh). Càng sớm càng tốt\n"
        "· Đã khô → bỏ Step 1, sang Step 2 (cồn). Báo khách trước: có thể còn vết\n"
        "· Đã sấy/ủi → gần như không ra (cố định nhiệt). Gửi chuyên hoặc từ chối lịch sự\n"
        "\n"
        "◆ 【Nói khách trước】 Thuốc nhuộm rất mạnh, khó sạch hết. "
        "Chúng tôi sẽ cố gắng nhưng có thể còn vết. Anh/Chị muốn tiếp tục chứ ạ?"
    ),
    "S_BLACK_COFFEE": (
        "◆ 【Kiểm tra trước】 Cà phê đen\n"
        "· Còn ướt → thấm + xả lạnh trước\n"
        "· Đã khô → có thể còn vết — cần đồng ý\n"
        "· Đã sấy/ủi → cố định nhiệt, chỉ kỳ vọng một phần"
    ),
    "S_COOKING_OIL": (
        "◆ 【Kiểm tra trước】 Dầu ăn\n"
        "· Đừng đổ nước trước → bột/thấm rồi xà phòng\n"
        "· Đã sấy → cố định nhiệt, báo khách trước\n"
        "· Còn nhờn → không sấy"
    ),
    "S_SWEAT_YELLOW": (
        "◆ 【Kiểm tra trước】 Ố vàng mồ hôi / nách\n"
        "· Khác mồ hôi mới — thường protein + khử mùi\n"
        "· Cấm Javel (làm vàng hơn)\n"
        "· Khó trắng lại hoàn toàn — cần đồng ý"
    ),
    "S_RED_WINE": (
        "◆ 【Kiểm tra trước】 Rượu vang đỏ\n"
        "· Còn ướt → thấm ngay (không muối) + lạnh\n"
        "· Đã khô → dễ còn tím — báo trước\n"
        "· Lụa/len → ưu tiên từ chối / gửi chuyên\n"
        "· Đã sấy/ủi → rất khó"
    ),
}

# Extra tool names for message 1 (stain-specific; no chemistry invention)
STAIN_TOOL_EXTRAS: dict[str, dict[str, list[str]]] = {
    "S_HAIR_DYE": {
        "ko": [
            "흰 면 천 5장 이상",
            "이소프로필 알코올 70%(약국 소독용)",
            "산소표백제 분말(과탄산나트륨)",
            "담금통·대야",
        ],
        "vi": [
            "Khăn trắng ≥5 miếng",
            "Cồn isopropyl 70% (cồn sát trùng)",
            "Bột tẩy oxy (sodium percarbonate)",
            "Thau/chậu ngâm",
        ],
        "en": [
            "White cloths (5+)",
            "Isopropyl alcohol 70% (rubbing alcohol)",
            "Oxygen bleach powder",
            "Basin for soaking",
        ],
    },
    "S_BLACK_COFFEE": {
        "ko": ["흰 식초", "분무기(식초 1:4 전용)", "산소표백제(흰옷만)"],
        "vi": ["Giấm trắng", "Bình xịt (giấm 1:4)", "Bột oxy (áo trắng)"],
        "en": ["White vinegar", "Spray bottle (1:4 vinegar)", "Oxygen bleach (white only)"],
    },
    "S_COOKING_OIL": {
        "ko": ["전분(감자·옥수수) 또는 베이비파우더", "주방세제", "흰 천"],
        "vi": ["Bột (khoai/ngô) hoặc phấn baby", "Nước rửa chén", "Khăn trắng"],
        "en": ["Starch or baby powder", "Dish soap", "White cloth"],
    },
    "S_INK_PEN": {
        "ko": ["이소프로필 알코올 70%", "흰 천 여러 장", "흡수지·키친타월"],
        "vi": ["Cồn isopropyl 70%", "Nhiều khăn trắng", "Giấy thấm"],
        "en": ["IPA 70%", "White cloths", "Blotting paper"],
    },
    "S_LIPSTICK": {
        "ko": ["이소프로필 알코올 70%", "흡수지", "주방세제", "연질 솔"],
        "vi": ["Cồn isopropyl 70%", "Giấy thấm", "Nước rửa chén", "Bàn chải mềm"],
        "en": ["IPA 70%", "Blotting paper", "Dish soap", "Soft brush"],
    },
    "S_MASCARA": {
        "ko": ["이소프로필 알코올 70%", "주방세제", "흰 천 여러 장"],
        "vi": ["Cồn isopropyl 70%", "Nước rửa chén", "Khăn trắng"],
        "en": ["IPA 70%", "Dish soap", "White cloths"],
    },
    "S_KIMCHI": {
        "ko": ["주방세제", "흰 식초", "산소표백제(흰옷만)"],
        "vi": ["Nước rửa chén", "Giấm trắng", "Bột oxy (áo trắng)"],
        "en": ["Dish soap", "White vinegar", "Oxygen bleach (white only)"],
    },
    "S_SWEAT_YELLOW": {
        "ko": ["효소세제", "산소표백제(흰·허용 원단)", "담금통", "중성세제(실크·울)"],
        "vi": ["Nước giặt enzyme", "Bột oxy (trắng)", "Chậu ngâm", "Giặt trung tính (lụa/len)"],
        "en": ["Enzyme detergent", "Oxygen bleach (white)", "Soak basin", "Neutral wash (silk/wool)"],
    },
    "S_SHIRT_YELLOW": {
        "ko": ["효소세제", "산소표백제", "연질 솔(목·소매)", "담금통"],
        "vi": ["Enzyme", "Bột oxy", "Bàn chải mềm", "Chậu ngâm"],
        "en": ["Enzyme detergent", "Oxygen bleach", "Soft brush", "Basin"],
    },
    "S_RED_WINE": {
        "ko": ["흰 천·키친타월", "흰 식초", "산소표백제(흰 면·린넨만)", "담금통"],
        "vi": ["Khăn/giấy trắng", "Giấm trắng", "Bột oxy (cotton trắng)", "Chậu ngâm"],
        "en": ["White cloth/paper", "White vinegar", "Oxygen bleach (white cotton)", "Basin"],
    },
}

# Soft outlook override (no %): state-based for high-risk stains
STAIN_SOFT_OUTLOOK: dict[str, dict[str, str]] = {
    "S_HAIR_DYE": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 묻은 직후·흰옷: 꽤 잘 빠질 수 있어요. 그래도 완전 제거는 보장하지 않아요\n"
            "· 시간이 지남: 잔색 가능성 높음 — 접수 때 동의를 받으세요\n"
            "· 이미 마름: 부분 제거만 기대하세요\n"
            "· 건조기·다리미 지남: 거의 어려움 — 전문 의뢰·거절을 먼저 검토하세요"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới dính + áo trắng: có thể ra nhiều — vẫn không đảm bảo sạch hết\n"
            "· Để lâu: dễ còn vết — cần đồng ý khi nhận\n"
            "· Đã khô: chỉ kỳ vọng sạch một phần\n"
            "· Đã sấy/ủi: rất khó — ưu tiên chuyên / từ chối"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh + white: often improves a lot — full removal still not guaranteed\n"
            "· Time passed: residual marks likely — get consent at intake\n"
            "· Already dry: expect partial removal only\n"
            "· After dryer/iron: rarely workable — refer or decline first"
        ),
    },
    "S_SWEAT_YELLOW": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 얕은 황변: 부분 개선 기대\n"
            "· 오래·진한 겨드랑 황변: 잔영 남기 쉬움 — 동의 필수\n"
            "· 락스 쓴 뒤: 더 나쁠 수 있음 — 전문·거절 검토"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Ố nhẹ: có thể cải thiện một phần\n"
            "· Ố nách lâu/đậm: dễ còn — cần đồng ý\n"
            "· Đã dùng Javel: có thể xấu hơn — chuyên / từ chối"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Light yellowing: partial improvement likely\n"
            "· Old/dark armpit: residual common — consent required\n"
            "· After chlorine: may worsen — refer or decline"
        ),
    },
    "S_SHIRT_YELLOW": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 목·소매만 옅음: 개선 기대\n"
            "· 전체 황변: 부분만 — 완전 하양 보장 금지\n"
            "· 열고착·락스 이력: 어려움"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Chỉ cổ/tay nhẹ: có thể cải thiện\n"
            "· Vàng cả áo: chỉ một phần — không hứa trắng hết\n"
            "· Đã nhiệt/Javel: khó"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Collar/cuff light: often improves\n"
            "· Whole-shirt yellow: partial only — never promise pure white\n"
            "· Heat/chlorine history: hard"
        ),
    },
    "S_RED_WINE": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 묻은 직후·면: 꽤 개선 가능 — 완전 제거는 보장하지 않아요\n"
            "· 마름·자줏빛: 잔색 흔함\n"
            "· 실크·울: 매장 강처리 위험 — 전문·거절 우선\n"
            "· 건조기·다리미: 거의 어려움"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới + cotton: có thể cải thiện — không đảm bảo sạch hết\n"
            "· Đã khô/tím: dễ còn\n"
            "· Lụa/len: ưu tiên chuyên / từ chối\n"
            "· Đã sấy/ủi: rất khó"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh cotton: often improves — full removal not guaranteed\n"
            "· Dried purple: residual common\n"
            "· Silk/wool: refer or decline first\n"
            "· After dryer/iron: rarely workable"
        ),
    },
    "S_COOKING_OIL": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 신선·흡수 전: 잘 빠지는 편\n"
            "· 이미 건조기: 열고착 — 부분만 기대·사전 고지\n"
            "· 미끄러움 남음: 말리면 더 굳어요"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới, chưa sấy: thường ra tốt\n"
            "· Đã sấy: cố định nhiệt — chỉ một phần\n"
            "· Còn nhờn: đừng sấy"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh before dryer: often good\n"
            "· After dryer: heat-set — partial only\n"
            "· Still greasy: do not dry"
        ),
    },
    "S_INK_PEN": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 신선·면: 꽤 개선 가능 — 완전 제거는 보장하지 않아요\n"
            "· 마름·번진 뒤: 잔색 흔함\n"
            "· 실크·울·프린트: 손상 위험 — 전문·거절 우선\n"
            "· 열고착: 어려움"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới + cotton: có thể cải thiện — không đảm bảo sạch hết\n"
            "· Đã khô/loang: dễ còn\n"
            "· Lụa/len/in: ưu tiên chuyên / từ chối\n"
            "· Đã nhiệt: khó"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh cotton: often improves — full removal not guaranteed\n"
            "· Dried/spread: residual common\n"
            "· Silk/wool/print: refer or decline first\n"
            "· Heat-set: hard"
        ),
    },
    "S_LIPSTICK": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 겉 왁스만: 잘 빠지는 편\n"
            "· 색소까지 먹음: 잔색 가능 — 동의 받기\n"
            "· 실크·유색: 매니저 확인 · 손상 주의"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Chỉ sáp ngoài: thường ra tốt\n"
            "· Đã ngấm màu: dễ còn — cần đồng ý\n"
            "· Lụa/áo màu: hỏi quản lý"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Surface wax only: often good\n"
            "· Pigment set in: residual possible — get consent\n"
            "· Silk/color: supervisor check"
        ),
    },
    "S_MASCARA": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 묻은 직후: 찍어 빼면 개선\n"
            "· 문질러 번진 뒤: 잔색 흔함\n"
            "· 실크: 약하게 · 전문 검토"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới dính: thấm thường cải thiện\n"
            "· Đã chà loang: dễ còn\n"
            "· Lụa: nhẹ · xem chuyên"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh: blotting often helps\n"
            "· After rubbing: residual common\n"
            "· Silk: gentle only · consider refer"
        ),
    },
}

# VI stain-specific don'ts (common VI block is shared; extras only when present)
STAIN_DONTS_VI: dict[str, list[str]] = {
    "S_HAIR_DYE": [
        "Không dùng tẩy oxy cho áo màu",
        "Không dùng cồn cho lụa/len/da khi chưa test góc",
        "Không tái sử dụng khăn đã dính màu → màu ngấm ngược",
        "Không làm trong phòng kín với cồn — phải thông gió (cháy/mùi)",
    ],
    "S_SWEAT_YELLOW": [
        "Không dùng Javel lên ố vàng — sẽ vàng hơn",
    ],
    "S_SHIRT_YELLOW": [
        "Không dùng Javel cho áo sơ mi vàng protein",
    ],
    "S_RED_WINE": [
        "Không rắc muối",
        "Không dùng oxy trên lụa/len/áo màu",
    ],
    "S_COOKING_OIL": [
        "Không sấy khi còn nhờn",
        "Không đổ nước rồi chà mạnh trước",
    ],
    "S_KIMCHI": [
        "Không dùng kem đánh răng",
        "Không sấy khi còn ớt/mùi",
    ],
    "S_INK_PEN": [
        "Không dùng Javel để tẩy mực → có thể để lại vệt xám",
        "Không chà ngang — sẽ loang",
        "Không làm kín phòng với cồn — phải thông gió",
    ],
    "S_LIPSTICK": [
        "Không chà ngang — loang màu",
        "Không cạo sâu vào sợi",
    ],
    "S_MASCARA": [
        "Không chà ngang",
        "Không dùng cồn trên lụa khi chưa test góc",
    ],
}

_NEXT_MSG = {
    "ko": "📩 손동작·시간·금지 사항은 바로 다음 메시지에 이어서 보내 드릴게요.",
    "vi": "📩 Cách làm chi tiết sẽ gửi ngay tin nhắn tiếp theo.",
    "en": "📩 Hand-motion details follow in the next message.",
}

_DETAIL_HEAD = {
    "ko": "▼ 손동작 상세 — 위에서 아래로 하나씩 따라 해 주세요",
    "vi": "▼ Chi tiết thao tác — làm lần lượt từ trên xuống",
    "en": "▼ Hand-motion detail — follow top to bottom",
}


def _proto_dict(graph: dict) -> dict:
    p = graph.get("protocol") if isinstance(graph, dict) else None
    return p if isinstance(p, dict) else {}


def _stain_id(graph: dict) -> str:
    sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
    return str(graph.get("_owner_stain_id") or sc.get("id") or "")


def _motion_stain_id(graph: dict) -> str:
    """Stain id for hand-motions / status / donts (age-aware blood remap)."""
    sid = _stain_id(graph)
    if sid != "S_BLOOD_FRESH":
        return sid
    sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
    age = str(sc.get("age_bucket") or graph.get("age_bucket") or "")
    if age in {"dried", "hard"}:
        return "S_BLOOD_DRY"
    ents = graph.get("entities") if isinstance(graph.get("entities"), dict) else {}
    raw = str(
        graph.get("_raw")
        or ents.get("_raw")
        or graph.get("raw_question")
        or ""
    )
    if any(k in raw for k in ("마른", "말라", "말랐", "굳은", "오래된", "고착", "갈색")):
        return "S_BLOOD_DRY"
    return sid


def _chem_codes(graph: dict) -> set[str]:
    codes: set[str] = set()
    for c in graph.get("chemicals") or []:
        if isinstance(c, dict) and c.get("code"):
            codes.add(str(c["code"]).upper())
    proto = _proto_dict(graph)
    for s in proto.get("steps") or []:
        if isinstance(s, dict) and s.get("chem"):
            codes.add(str(s["chem"]).upper())
    return codes


def _soak_bounds(graph: dict) -> tuple[Optional[int], Optional[int]]:
    proto = _proto_dict(graph)
    for s in proto.get("steps") or []:
        if not isinstance(s, dict) or s.get("blocked"):
            continue
        if s.get("soak") and s.get("minutes_lo") is not None:
            return s.get("minutes_lo"), s.get("minutes_hi") or s.get("minutes_lo")
    for s in proto.get("steps") or []:
        if isinstance(s, dict) and s.get("minutes_lo") is not None:
            return s.get("minutes_lo"), s.get("minutes_hi") or s.get("minutes_lo")
    return None, None


def format_soak_time(base: int, maximum: int, lang: str = "ko") -> str:
    if lang == "vi":
        return (
            f"Hẹn giờ {base} phút. Hết giờ → kiểm tra vết.\n"
            f"· Đã nhạt → xả rồi bước tiếp\n"
            f"· Còn → ngâm thêm {base} phút\n"
            f"· Không quá {maximum} phút — ngâm quá lâu làm hỏng vải"
        )
    if lang == "en":
        return (
            f"Set timer to {base} min. When it rings, check the stain.\n"
            f"· Much lighter → rinse and continue\n"
            f"· Still there → soak another {base} min\n"
            f"· Do not exceed {maximum} min total"
        )
    hrs = f"({maximum // 60}시간)" if maximum >= 60 else ""
    return (
        f"타이머를 {base}분으로 맞춰 주세요.\n"
        f"{base}분이 지나면 꺼내서 얼룩을 확인해 주세요.\n"
        f"· 많이 빠졌다 → 헹구고 다음 단계로 가세요\n"
        f"· 아직 남았다 → {base}분 더 담가 주세요\n"
        f"· 최대 {maximum}분{hrs}을 넘기지 마세요. 너무 오래 담그면 옷감이 상할 수 있어요"
    )


def build_one_line_order(graph: dict, lang: str = "ko") -> str:
    """Numbered do-this-next list from Protocol steps."""
    proto = _proto_dict(graph)
    steps = proto.get("steps") or []
    lines: list[str] = []
    n = 0
    for s in steps:
        if not isinstance(s, dict) or s.get("blocked"):
            continue
        if str(s.get("id") or "") == "id":
            continue
        action = str(s.get("action_ko") or s.get("action_vi") or "").strip()
        if lang == "vi":
            action = str(s.get("action_vi") or "").strip()
        elif lang == "en":
            action = str(
                s.get("action_en") or s.get("action") or s.get("action_vi") or ""
            ).strip()
        if not action or len(action) < 4:
            continue
        n += 1
        lo, hi = s.get("minutes_lo"), s.get("minutes_hi")
        time_bit = ""
        if lo is not None:
            if hi and hi != lo and int(hi) >= int(lo) + 30:
                if lang == "ko":
                    time_bit = f" (먼저 {lo}분→확인, 최대 {hi}분)"
                elif lang == "vi":
                    time_bit = f" (trước {lo} phút→kiểm tra, tối đa {hi} phút)"
                else:
                    time_bit = f" (first {lo}→check, max {hi})"
            elif hi and hi != lo:
                if lang == "ko":
                    time_bit = f" ({lo}–{hi}분)"
                elif lang == "vi":
                    time_bit = f" ({lo}–{hi} phút)"
                else:
                    time_bit = f" ({lo}-{hi} min)"
            else:
                if lang == "ko":
                    time_bit = f" ({lo}분)"
                elif lang == "vi":
                    time_bit = f" ({lo} phút)"
                else:
                    time_bit = f" ({lo} min)"
        if lang == "ko":
            action = _soften_step_label(action)
        lines.append(f"{n}) {action}{time_bit}")
        if n >= 8:
            break
    if not lines:
        sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
        if lang == "vi":
            path = str(sc.get("fresh_path_vi") or "")
        elif lang == "en":
            path = str(sc.get("fresh_path_en") or sc.get("fresh_path") or "")
        else:
            path = str(sc.get("fresh_path_ko") or "")
        numbered = re.findall(r"\((\d+)\)\s*([^\n→]+)", path)
        if numbered and lang == "ko":
            for i, (_n, bit) in enumerate(numbered[:8], 1):
                bit = bit.strip().rstrip(".")
                bit = _soften_step_label(bit)
                lines.append(f"{i}) {bit}")
        elif numbered and lang != "ko":
            for i, (_n, bit) in enumerate(numbered[:8], 1):
                bit = bit.strip().rstrip(".")
                if bit:
                    lines.append(f"{i}) {bit}")
        elif "→" in path and lang == "ko":
            bits = [b.strip() for b in path.split("→") if b.strip()]
            lines = [f"{i}) {_soften_step_label(b)}" for i, b in enumerate(bits[:8], 1)]
        elif "→" in path and lang != "ko":
            bits = [b.strip() for b in path.split("→") if b.strip()]
            lines = [f"{i}) {b}" for i, b in enumerate(bits[:8], 1)]
    if not lines:
        return ""
    if lang == "ko":
        head = "◆ 【한 줄 순서】 아래 번호대로 하나씩 하세요 (한꺼번에 섞지 마세요)"
    elif lang == "vi":
        head = "◆ 【Thứ tự】 Làm lần lượt theo số — không trộn bước"
    else:
        head = "◆ 【One-line order】 Do each number in order — do not mix steps"
    return head + "\n" + "\n".join(lines)


def _soften_step_label(text: str) -> str:
    t = text.strip()
    if "하세요" in t or "마세요" in t or "해 주세요" in t:
        return t
    reps = (
        ("즉시 찬물", "바로 찬물로 헹궈 주세요"),
        ("찬물 헹굼", "찬물로 헹궈 주세요"),
        ("알코올 블롯(테스트)", "알코올은 흰 천에 묻혀 꾹꾹 눌러 흡수하세요(구석 테스트 먼저)"),
        ("알코올 블롯", "알코올은 흰 천에 묻혀 꾹꾹 눌러 흡수하세요"),
        ("흰옷 산소 장침지", "흰옷만 산소표백제로 담가 주세요"),
        ("흰옷 산소", "흰옷만 산소표백제를 쓰세요"),
        ("건조 전 강광", "말리기 전 밝은 조명에서 잔색을 확인해 주세요"),
        ("세탁; 잔색 고지", "세탁해 주세요. 잔색이 남을 수 있다고 고객에게 말씀하세요"),
        ("세탁", "세탁해 주세요"),
    )
    for a, b in reps:
        if t == a:
            return b
        if t.startswith(a):
            return b + t[len(a) :]
    return t


def build_tools_names_only(graph: dict, lang: str = "ko") -> str:
    tools = graph.get("tools") or []
    names: list[str] = []
    for t in tools:
        if not isinstance(t, dict):
            continue
        if lang == "vi":
            name = str(t.get("name_vi") or "").strip()
        elif lang == "en":
            name = str(t.get("name") or t.get("name_en") or t.get("name_vi") or "").strip()
        else:
            name = str(t.get("name_ko") or t.get("name_vi") or "").strip()
        if name and name not in names:
            names.append(name)
        if len(names) >= 8:
            break
    # Always suggest basics when we have a stain protocol
    if lang == "ko":
        basics = ["니트릴 장갑", "흰 면 천 여러 장", "타이머(핸드폰 OK)"]
        head = "◆ 【준비물】 이름만 — 사용법은 다음 메시지에 있어요"
        extra_head = "· "
    elif lang == "vi":
        basics = ["Găng nitrile", "Khăn trắng", "Hẹn giờ"]
        head = "◆ 【Chuẩn bị】 Chỉ tên — cách dùng ở tin sau"
        extra_head = "· "
    else:
        basics = ["Nitrile gloves", "White cloths", "Timer"]
        head = "◆ 【Tools】 Names only — how-to in next message"
        extra_head = "· "
    lines = [f"{extra_head}{b}" for b in basics]
    seen_lower = {ln.lower() for ln in lines}
    for n in names:
        # skip if already covered by basics keywords
        if any(x in n.lower() for x in ("장갑", "găng", "glove", "흰 천", "khan", "cloth", "타이머", "timer", "hẹn")):
            continue
        key = f"{extra_head}{n}".lower()
        if key in seen_lower:
            continue
        lines.append(f"{extra_head}{n}")
        seen_lower.add(key)
    # Stain-specific extras (e.g. IPA 70% for hair dye) — names only, no new chemistry
    sid = _motion_stain_id(graph)
    extras = (STAIN_TOOL_EXTRAS.get(sid) or {}).get(lang) or []
    for ex in extras:
        ex = str(ex).strip()
        if not ex:
            continue
        key = f"{extra_head}{ex}".lower()
        if key in seen_lower:
            continue
        # soft de-dupe against already-listed tool names
        if any(ex.lower() in ln.lower() or ln.lower() in key for ln in lines):
            continue
        lines.append(f"{extra_head}{ex}")
        seen_lower.add(key)
    return head + "\n" + "\n".join(lines[:12])


def build_spot_test_block(graph: dict, lang: str = "ko") -> str:
    codes = _chem_codes(graph)
    if not (codes & BLOT_CHEM_CODES):
        return ""
    # Light hint when alcohol is in play — still generic blot procedure
    a1_hint = "A1" in codes
    if lang == "vi":
        chem_line = (
            "1) Thấm hóa chất (cồn IPA 70%) lên khăn trắng một ít\n"
            if a1_hint
            else "1) Thấm hóa chất lên khăn trắng một ít\n"
        )
        return (
            "◆ 【Thử góc】 Làm trước khi dùng hóa chất\n"
            "Chỗ kín (lai trong / cạnh nhãn).\n"
            + chem_line
            + "2) Ấn 30 giây lên chỗ thử\n"
            "3) Nhấc khăn ra kiểm tra\n"
            "· Khăn dính màu vải → dừng hóa chất này\n"
            "· Không đổi màu → có thể tiếp tục\n"
            "💡 30 giây giúp tránh hỏng vải"
        )
    if lang == "en":
        chem_line = (
            "1) Dab a little IPA 70% alcohol on a white cloth\n"
            if a1_hint
            else "1) Dab a little chem on a white cloth\n"
        )
        return (
            "◆ 【Spot-test】 Do this before using chemicals\n"
            "Hidden seam / inside label area.\n"
            + chem_line
            + "2) Press on the test spot for 30 seconds\n"
            "3) Lift and check\n"
            "· Cloth picks up garment color → stop this chem\n"
            "· No color change → OK to continue\n"
            "💡 30 seconds can prevent fabric damage"
        )
    chem_line = (
        "1) 쓸 약(이소프로필 알코올 70%)을 흰 천에 조금 묻혀 주세요\n"
        if a1_hint
        else "1) 쓸 약을 흰 천에 조금 묻혀 주세요\n"
    )
    return (
        "◆ 【구석 테스트】 약품 쓰기 전에 해 주세요\n"
        "안 보이는 곳(안쪽 밑단·라벨 옆)에서요.\n"
        + chem_line
        + "2) 테스트 부위에 30초 꾹 눌러 주세요\n"
        "3) 천을 떼고 확인하세요\n"
        "· 천에 옷 색이 묻었다 → 이 약은 쓰지 마세요\n"
        "· 색 변화 없다 → 진행하셔도 됩니다\n"
        "💡 30초면 옷 망가지는 사고를 막을 수 있어요"
    )


def build_donts_block(graph: dict, lang: str = "ko") -> str:
    sid = _motion_stain_id(graph)
    if lang == "vi":
        lines = [
            "◆ 【Tuyệt đối không】",
            "· Không xả nước nóng → vết gắn chặt vào sợi",
            "· Không chà mạnh → loang và hỏng vải. Ấn thấm từ trên xuống",
            "· Không đổ hóa chất trực tiếp lên áo → thấm khăn trắng rồi chấm",
            "· Không trộn nhiều hóa chất cùng lúc → dùng lần lượt, xả giữa các bước",
            "· Không sấy/ủi khi còn vết → nhiệt cố định vết",
        ]
        extra = STAIN_DONTS_VI.get(sid) or []
        if extra:
            lines.append("[Vết này]")
            for d in extra:
                lines.append(f"· {d}")
        return "\n".join(lines)
    if lang == "en":
        return (
            "◆ 【Do not】\n"
            "· Do not hot-rinse → stain sets into fibers\n"
            "· Do not rub hard → spreads and damages fabric; blot from above\n"
            "· Do not pour chem directly on fabric → dab with a white cloth\n"
            "· Do not mix chems at once → one chem → rinse → next\n"
            "· Do not dry/iron over remaining marks → heat sets them"
        )
    lines = ["◆ 【절대 하지 마세요】"]
    lines.append("[공통]")
    for d in COMMON_DONTS_KO:
        lines.append(f"· {d}")
    extra = STAIN_DONTS_KO.get(sid) or []
    if extra:
        lines.append("[이 얼룩]")
        for d in extra:
            lines.append(f"· {d}")
    return "\n".join(lines)


def build_dry_check_block(lang: str = "ko") -> str:
    if lang == "vi":
        return (
            "◆ 【Trước khi sấy】 Kiểm tra dưới ánh sáng mạnh\n"
            "· Sạch → sấy/phơi bình thường\n"
            "· Còn vết → không sấy/ủi — làm lại bước hoặc phơi tự nhiên và báo khách\n"
            "💡 Dù 'gần sạch' mà còn vết → đừng sấy. Nhiệt có thể làm vết vĩnh viễn"
        )
    if lang == "en":
        return (
            "◆ 【Before drying】 Check under bright light\n"
            "· Clean → dry OK\n"
            "· Mark left → no dryer/iron — repeat treatment or air-dry and tell the guest\n"
            "💡 Heat can set marks permanently"
        )
    return (
        "◆ 【말리기 전】 꼭 확인해 주세요\n"
        "밝은 조명(휴대폰 라이트 OK)에서 얼룩 자리를 한 번 더 보세요.\n"
        "· 깨끗하다 → 정상 건조하시면 됩니다\n"
        "· 자국이 보인다 → 건조기·다림질 하지 마세요. "
        "약 단계를 한 번 더 하거나, 자연 건조 후 고객께 잔색을 말씀해 주세요\n"
        "💡 “거의 다 빠졌는데”라도 자국이 보이면 말리지 마세요. "
        "열을 가하면 자국이 영구로 남을 수 있어요"
    )


def build_status_check(graph: dict, lang: str = "ko") -> str:
    sid = _motion_stain_id(graph)
    if lang == "vi":
        return STAIN_STATUS_VI.get(sid, "")
    if lang == "en":
        return ""
    if sid in STAIN_STATUS_KO:
        return STAIN_STATUS_KO[sid]
    # Generic age hint from graph if present
    sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
    age = str(sc.get("age_bucket") or graph.get("age_bucket") or "")
    if age == "dried":
        return (
            "◆ 【먼저 확인】 얼룩이 이미 마른 상태예요.\n"
            "잔색 가능성을 고객께 먼저 말씀해 주세요."
        )
    if age == "hard":
        return (
            "◆ 【먼저 확인】 열고착·고난이도예요.\n"
            "전문 의뢰 또는 정중한 거절을 먼저 검토해 주세요."
        )
    return (
        "◆ 【먼저 확인】 젖어 있나요, 말랐나요?\n"
        "· 젖어 있다 → 한 줄 순서 1번부터\n"
        "· 말랐다 → 잔색 가능성을 고객께 먼저 말씀하고 진행하세요"
    )


def _apply_tone_softening(text: str) -> str:
    if not text:
        return text
    out = text
    reps = (
        ("보류하며 진행합니다. 확인 후 조정하세요.", "약하게만 하세요. 표백은 매니저 확인 후 하세요."),
        ("약하게(흡수·찍어 바름만)·표백을 보류하며 진행합니다. 확인 후 조정하세요.",
         "원단·두께를 모르면 약하게만 하세요. 표백은 매니저 확인 후 하세요."),
        ("약하게(흡수·찍어 바름만)·표백 보류 → 확인 후 조정하세요.",
         "원단·두께를 모르면 약하게만 하세요. 표백은 매니저 확인 후 하세요."),
        ("블롯", "꾹꾹 눌러 흡수"),
        ("침지", "담그기"),
        ("강광", "밝은 조명"),
        ("도포", "묻히기"),
    )
    for a, b in reps:
        out = out.replace(a, b)
    out = re.sub(
        r"보류하며\s*진행합니다\.?\s*확인\s*후\s*조정하세요\.?",
        "약하게만 하세요. 표백·강한 약은 매니저 확인 후 하세요.",
        out,
    )
    # Wide soak ranges → stepwise reminder inline
    out = re.sub(
        r"30\s*[–\-~]\s*180\s*분",
        "먼저 30분→확인(최대 120분)",
        out,
    )
    out = re.sub(
        r"30\s*[–\-~]\s*120\s*분",
        "먼저 30분→확인(최대 120분)",
        out,
    )
    return out


def _split_glossary_and_body(answer: str) -> tuple[str, str]:
    """Return (front_including_sop_header, body_after_header)."""
    markers = (
        "▼ 이번 건 세탁 교육",
        "▼ SOP cho vết này",
        "▼ This job's wash SOP",
    )
    for m in markers:
        idx = answer.find(m)
        if idx < 0:
            continue
        # include header line + following ━━━ line in front
        nl = answer.find("\n", idx)
        if nl < 0:
            return answer[: idx + len(m)], answer[idx + len(m) :]
        rest = answer[nl + 1 :]
        if rest.startswith("━"):
            nl2 = rest.find("\n")
            end = nl + 1 + (nl2 + 1 if nl2 >= 0 else len(rest))
            return answer[:end], answer[end:]
        return answer[: nl + 1], answer[nl + 1 :]
    return "", answer


def _extract_why_one_liner(body: str, lang: str = "ko") -> str:
    """Keep a short [왜] tip if present — drop ◆(1)~(6) TOC. KO header only for KO."""
    if not body or lang != "ko":
        return ""
    m = re.search(
        r"◆\s*\[왜[^\]]*\]\s*\n([\s\S]*?)(?=\n◆\s*\[|\n◆\s*\(|\Z)",
        body,
    )
    if not m:
        return ""
    why = m.group(1).strip()
    if len(why) > 280:
        why = why[:277] + "…"
    if not why:
        return ""
    return "◆ 【왜 이 순서인가요】 (한 줄)\n" + why


def inject_clarity_into_answer(
    answer: str,
    *,
    graph: Optional[dict] = None,
    level: str = "L2",
    grade: int = 2,
    lang: str = "ko",
) -> str:
    """Build 1통 흐름 + 2통 손동작 with short common blocks."""
    if not answer:
        return answer
    g = graph if isinstance(graph, dict) else {}
    lang = lang if lang in _SUPERVISOR else "ko"
    out = _apply_tone_softening(answer)

    front, body = _split_glossary_and_body(out)
    if not front:
        # Still attach mid-tier keyword blocks (fabric/mix/retry) when glossary missing
        try:
            import owner_mid_blocks_v40 as _mid

            extras: list[str] = []
            fab = _mid.block_fabric(g, lang)
            if fab:
                extras.append(fab)
            if _mid.wants_mix_block(g, lang):
                chem = _mid.block_chem(g, lang)
                if chem:
                    extras.append(chem)
            if _mid.wants_retry_full(g, lang):
                rb = _mid.block_retry(_motion_stain_id(g), "L2", g, lang)
                if rb:
                    extras.append(rb)
            if extras:
                out = out.rstrip() + "\n\n" + "\n\n".join(extras)
        except Exception as _e:
            print(f"[CLARITY] mid early-attach skip: {type(_e).__name__}: {_e}")
        foot = (_GRADE_FOOTER.get(lang) or _GRADE_FOOTER["ko"]).get(grade, "")
        if foot and "【다시 한번 고객 고지】" not in out and "【Nhắc khách】" not in out:
            out = out.rstrip() + "\n\n" + foot
        return out

    body = re.sub(r"⚠️ 이 얼룩은[^\n]*\n+", "", body, count=1)
    body = re.sub(
        r"◆ 【한 줄 순서】[\s\S]*?(?=\n◆ |\n▼ |\Z)",
        "",
        body,
        count=1,
    )

    flow_bits: list[str] = []
    if level in {"L2", "L3"}:
        flow_bits.append(_SUPERVISOR[lang])
    sid = _motion_stain_id(g)

    # Mid-tier assembly (v40): conditional blocks — no full dump, no % rates
    _mid = None
    try:
        import owner_mid_blocks_v40 as _mid
    except Exception as _e:
        print(f"[CLARITY] mid_blocks import skip: {type(_e).__name__}: {_e}")

    if _mid is not None:
        intake = _mid.block_intake(level, lang)
        if intake:
            flow_bits.append(intake)

    outlook_override = (STAIN_SOFT_OUTLOOK.get(sid) or {}).get(lang) or ""
    if outlook_override:
        outlook = outlook_override
    else:
        outlook = (_SOFT_OUTLOOK.get(lang) or _SOFT_OUTLOOK["ko"]).get(int(grade) or 2, "")
    if outlook:
        flow_bits.append(outlook)
    status = build_status_check(g, lang)
    if status:
        flow_bits.append(status)
    if _mid is not None:
        fab = _mid.block_fabric(g, lang)
        if fab:
            flow_bits.append(fab)
    order = build_one_line_order(g, lang)
    if order:
        flow_bits.append(order)
    tools = build_tools_names_only(g, lang)
    if tools:
        flow_bits.append(tools)
    flow_bits.append(_NEXT_MSG[lang])

    detail_bits: list[str] = [_DETAIL_HEAD[lang]]
    if _mid is not None:
        compound = _mid.block_compound(sid, lang)
        if compound:
            detail_bits.append(compound)
    spot = build_spot_test_block(g, lang)
    if spot:
        detail_bits.append(spot)

    motions = ""
    try:
        from owner_hand_motions import build_hand_motions

        motions = build_hand_motions(sid, lang, graph=g)
    except Exception:
        motions = ""

    # If hand-motions already embed a soak *heading* (◆ 【담금 시간】 inside a Step),
    # skip the shared top soak block. Mere references like "(시간은 【담금 시간】 안내)"
    # must still get the common block (e.g. blood).
    soak_embedded = bool(motions) and (
        "◆ 【담금 시간】" in motions
        or "◆ 【Thời gian ngâm】" in motions
        or "◆ 【Soak time】" in motions
    )
    base, mx = _soak_bounds(g)
    if (
        not soak_embedded
        and base is not None
        and mx is not None
        and int(mx) >= int(base) + 15
    ):
        if lang == "vi":
            soak_head = "◆ 【Thời gian ngâm】"
        elif lang == "en":
            soak_head = "◆ 【Soak time】"
        else:
            soak_head = "◆ 【담금 시간】"
        detail_bits.append(soak_head + "\n" + format_soak_time(int(base), int(mx), lang))

    if motions:
        # Hand-motion Steps replace LLM ◆(1)~(6) — no duplicate TOC
        detail_bits.append(motions)
        why = _extract_why_one_liner(body, lang)
        if why:
            detail_bits.append(why)
    else:
        # Fallback: keep body but strip emoji TOC steps to reduce clutter
        body_clean = _strip_toc_steps(body.strip())
        if body_clean:
            detail_bits.append(body_clean)

    detail_bits.append(build_donts_block(g, lang))
    if _mid is not None:
        for tip in _mid.block_vn_tips(sid, lang):
            detail_bits.append(tip)
        chem_blk = _mid.block_chem(g, lang)
        if chem_blk:
            detail_bits.append(chem_blk)
    detail_bits.append(build_dry_check_block(lang))
    if _mid is not None:
        retry_blk = _mid.block_retry(sid, level, g, lang)
        if retry_blk:
            detail_bits.append(retry_blk)
    foot = (_GRADE_FOOTER.get(lang) or _GRADE_FOOTER["ko"]).get(grade, "")
    if foot:
        detail_bits.append(foot)

    flow = front.rstrip() + "\n\n" + "\n\n".join(flow_bits)
    detail = "\n\n".join(detail_bits)
    return flow + ZALO_MSG_SPLIT + detail


def _strip_toc_steps(body: str) -> str:
    """Remove ◆ (1)~(6) emoji TOC blocks; keep education tails if any."""
    if not body:
        return ""
    # Drop numbered TOC sections like ◆ (1) ... until next ◆ (n) or ◆ [
    out = re.sub(
        r"◆\s*\([1-6]\)[^\n]*\n[\s\S]*?(?=\n◆\s*\([1-6]\)|\n◆\s*\[|\Z)",
        "",
        body,
    )
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out


def split_zalo_messages(text: str, max_len: int = 1900) -> list[str]:
    """Split on ZALO_MSG_SPLIT, then hard-wrap each part under max_len."""
    if not text:
        return []
    raw_parts = text.split("<<<ZALO_MSG2>>>")
    parts = [p.strip() for p in raw_parts if p and p.strip()]
    if not parts:
        parts = [text.strip()]
    out: list[str] = []
    for part in parts:
        out.extend(_chunk_text(part, max_len))
    return out


def _chunk_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts: list[str] = []
    while len(text) > max_len:
        cut = text.rfind("\n", 0, max_len)
        if cut < max_len // 3:
            cut = text.rfind(". ", 0, max_len)
        if cut < max_len // 3:
            cut = max_len
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return parts


def for_ask_display(text: str) -> str:
    """Join multi-part answers for /ask JSON without the raw marker."""
    if not text or "<<<ZALO_MSG2>>>" not in text:
        return text
    parts = split_zalo_messages(text, max_len=100000)
    joined = []
    for i, p in enumerate(parts, 1):
        joined.append(f"—— {i}/{len(parts)} ——\n{p}")
    return "\n\n".join(joined)


# Phase 6 packs: fill missing clarity fields (setdefault — never override richer entries)
def _merge_clarity_pack(mod_name: str) -> None:
    try:
        mod = __import__(mod_name)
        for _k, _v in getattr(mod, "EXTRA_STATUS_KO", {}).items():
            STAIN_STATUS_KO.setdefault(_k, _v)
        for _k, _v in getattr(mod, "EXTRA_STATUS_VI", {}).items():
            STAIN_STATUS_VI.setdefault(_k, _v)
        for _k, _v in getattr(mod, "EXTRA_TOOL_EXTRAS", {}).items():
            STAIN_TOOL_EXTRAS.setdefault(_k, _v)
        for _k, _v in getattr(mod, "EXTRA_SOFT_OUTLOOK", {}).items():
            STAIN_SOFT_OUTLOOK.setdefault(_k, _v)
        for _k, _v in getattr(mod, "EXTRA_DONTS_KO", {}).items():
            STAIN_DONTS_KO.setdefault(_k, _v)
        for _k, _v in getattr(mod, "EXTRA_DONTS_VI", {}).items():
            STAIN_DONTS_VI.setdefault(_k, _v)
    except Exception as _e:
        print(f"[CLARITY] {mod_name} skip: {type(_e).__name__}: {_e}")


_merge_clarity_pack("owner_clarity_pack_v38")
_merge_clarity_pack("owner_clarity_pack_v39")
_merge_clarity_pack("owner_vn_motions_v41")
