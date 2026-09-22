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
        "◆ 【먼저 확인】 마스카라 종류\n"
        "· 일반 vs 워터프루프를 먼저 확인하세요\n"
        "· 문지르면 번짐 — 찍어 흡수만\n"
        "· 워터프루프·실크는 매니저 확인 · 성공률 낮음 고지\n"
        "· 검은 잔색 남은 채 말리지 마세요"
    ),
    "S_GLUE": (
        "◆ 【먼저 확인】 접착제 종류\n"
        "· 502/순간접착이 굳었으면 → 복원 불가·전문/반려 우선\n"
        "· 아크릴·목공풀 → 전분/오일 후 세제\n"
        "· 테이프 자국 → 알코올 테스트 후\n"
        "· 종류 불명·실크/아세테이트 → 용제 바로 쓰지 마세요"
    ),
    "S_DYE_TRANSFER": (
        "◆ 【먼저 확인】 이염\n"
        "· 다른 옷과 바로 분리 · 건조기 금지\n"
        "· 이미 건조기를 거쳤다면 복원이 매우 어렵습니다 — 손님께 먼저 말씀하세요\n"
        "· 락스는 흰 100% 면·폴리만, 매니저 확인 후"
    ),
    "S_BLACK_COFFEE": (
        "◆ 【먼저 확인】 커피 종류·상태\n"
        "· 우유·라떼·크림 탄 커피인가요? → 밀크커피 SOP(효소·세제 먼저 → 식초 나중)\n"
        "· 블랙(우유 없음)·젖어 있다 → 한 줄 순서 1번(흡수·찬물)부터\n"
        "· 이미 말랐다 → 잔색 가능 — 고객 동의 후 식초 중심으로\n"
        "· 건조기·다리미 지남 → 열고착. 부분 제거만 기대·사전 고지"
    ),
    "S_TEA": (
        "◆ 【먼저 확인】 차 종류·상태\n"
        "· 우유·라떼 탄 차인가요? → 밀크커피처럼 효소(또는 중성) 먼저 → 식초는 나중\n"
        "· 순차(홍/녹/우롱, 우유 없음) → 찬물 흡수 후 식초 1:4\n"
        "· 이미 말랐다 → 잔색·황변 가능 — 사전 고지\n"
        "· 당분 남은 채 말리지 마세요"
    ),
    "S_MILK": (
        "◆ 【먼저 확인】 우유·유제품\n"
        "· 아직 젖어 있다 → 찬물·효소(단백질) 먼저. 온수 금지\n"
        "· 이미 말랐다 → 효소 장침지 · 잔색 고지\n"
        "· 실크·울 → 효소 금지 · 중성세제·찬물만"
    ),
    "S_EGG": (
        "◆ 【먼저 확인】 계란\n"
        "· 노른자(지방) vs 흰자(단백질) — 온수부터 금지(익힘 고착)\n"
        "· 긁기 → 찬물 → 효소 → (노른자면) 주방세제\n"
        "· 실크·울 → 중성 위주"
    ),
    "S_CHOCOLATE": (
        "◆ 【먼저 확인】 초코\n"
        "· 지방+당+색소 — 고형 제거 후 주방세제(지방) → 효소\n"
        "· 이미 말랐거나 열 지남 → 잔색 가능 고지\n"
        "· 문지르면 번짐 — 찍어 흡수"
    ),
    "S_FRUIT_JUICE": (
        "◆ 【먼저 확인】 과일주스\n"
        "· 아직 젖어 있다 → 찬물 흡수·식초 1:4\n"
        "· 이미 말랐다 → 잔색 가능 — 동의 후\n"
        "· 흰/유색·실크 확인 전 산소 꺼내지 마세요"
    ),
    "S_KETCHUP": (
        "◆ 【먼저 확인】 케첩·토마토\n"
        "· 고형·당분 먼저 제거 · 찬물\n"
        "· 이미 말랐다 → 잔색·황변 고지\n"
        "· 당분 남은 채 말리지 마세요"
    ),
    "S_COOKING_OIL": (
        "◆ 【먼저 확인】 어떤 기름인가요?\n"
        "· 식용유·튀유 → 전분·흡착 후 세제(물부터 붓지 마세요)\n"
        "· 검고 냄새 세고 미끄러움 심함 → 엔진/오토바이 오일(L3)·매니저\n"
        "· 이미 건조기를 돌렸다 → 열고착. 완전 제거 어려움 — 먼저 고지\n"
        "· 미끄러움이 남으면 말리지 마세요"
    ),
    "S_INK_PEN": (
        "◆ 【먼저 확인】 잉크 종류부터\n"
        "· 수성·만년필 → 찬물 흡수/헹굼 먼저(알코올 바로 X)\n"
        "· 볼펜·유성 펜 → 안쪽 찍어 빼기 · 문지르면 번짐\n"
        "· 유성매직·영구마커 / 프린터·토너 → 전문·반려 우선\n"
        "· 실크·울·프린트 → 거절·전문·구석 테스트 없이 알코올 금지"
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
        "◆ 【먼저 확인】 와인 종류·상태\n"
        "· 레드와인인가요? 화이트·맥주·투명하면 → 화이트/맥주 SOP\n"
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
        "◆ 【Kiểm tra trước】 Loại cà phê · trạng thái\n"
        "· Có sữa/latte/kem? → SOP sữa (enzyme/xà phòng trước → giấm sau)\n"
        "· Đen (không sữa) còn ướt → thấm + xả lạnh trước\n"
        "· Đã khô → có thể còn vết — cần đồng ý\n"
        "· Đã sấy/ủi → cố định nhiệt, chỉ kỳ vọng một phần"
    ),
    "S_TEA": (
        "◆ 【Kiểm tra trước】 Loại trà\n"
        "· Trà sữa/latte? → enzyme (hoặc trung tính) trước → giấm sau\n"
        "· Trà thuần (hồng/xanh/oolong) → thấm lạnh rồi giấm 1:4\n"
        "· Đã khô → báo còn vết/ố\n"
        "· Còn đường → không sấy"
    ),
    "S_MILK": (
        "◆ 【Kiểm tra trước】 Sữa\n"
        "· Còn ướt → lạnh + enzyme trước. Cấm nước nóng\n"
        "· Đã khô → ngâm enzyme dài · báo còn vết\n"
        "· Lụa/len → cấm enzyme · chỉ trung tính + lạnh"
    ),
    "S_EGG": (
        "◆ 【Kiểm tra trước】 Trứng\n"
        "· Lòng đỏ (mỡ) vs lòng trắng (protein) — cấm nước nóng trước\n"
        "· Cạo → lạnh → enzyme → (lòng đỏ) nước rửa chén\n"
        "· Lụa/len → ưu tiên trung tính"
    ),
    "S_CHOCOLATE": (
        "◆ 【Kiểm tra trước】 Socola\n"
        "· Mỡ + đường + màu — cạo → nước rửa chén → enzyme\n"
        "· Đã khô/nhiệt → báo còn vết\n"
        "· Không chà ngang"
    ),
    "S_FRUIT_JUICE": (
        "◆ 【Kiểm tra trước】 Nước trái cây\n"
        "· Còn ướt → thấm lạnh + giấm 1:4\n"
        "· Đã khô → cần đồng ý\n"
        "· Chưa rõ vải/màu → chưa lấy bột oxy"
    ),
    "S_KETCHUP": (
        "◆ 【Kiểm tra trước】 Tương cà\n"
        "· Cạo đặc/đường trước · lạnh\n"
        "· Đã khô → báo còn vết/ố\n"
        "· Còn đường → không sấy"
    ),
    "S_COOKING_OIL": (
        "◆ 【Kiểm tra trước】 Loại dầu nào?\n"
        "· Dầu ăn/chiên → bột/thấm rồi xà phòng (đừng đổ nước trước)\n"
        "· Đen, mùi mạnh, nhờn nặng → dầu động cơ/xe máy (L3) · hỏi quản lý\n"
        "· Đã sấy → cố định nhiệt, báo khách trước\n"
        "· Còn nhờn → không sấy"
    ),
    "S_INK_PEN": (
        "◆ 【Kiểm tra trước】 Loại mực\n"
        "· Mực nước/bút máy → xả lạnh trước (chưa dùng cồn)\n"
        "· Bút bi/dầu → chấm mặt trái · không chà\n"
        "· Bút lông vĩnh cửu / mực in / toner → chuyên/từ chối trước\n"
        "· Lụa/len/in → cấm cồn mạnh không test"
    ),
    "S_MASCARA": (
        "◆ 【Kiểm tra trước】 Mascara thường hay waterproof?\n"
        "· Thường → IPA 70% chấm. Waterproof → hỏi quản lý, báo khó sạch\n"
        "· Không chà ngang · lụa cần test góc"
    ),
    "S_GLUE": (
        "◆ 【Kiểm tra trước】 Loại keo\n"
        "· 502 đã cứng → khó phục hồi · chuyên/từ chối\n"
        "· Keo acrylic/gỗ → bột/dầu rồi xà phòng\n"
        "· Keo băng → cồn sau test\n"
        "· Không rõ loại → đừng đổ dung môi ngay"
    ),
    "S_SWEAT_YELLOW": (
        "◆ 【Kiểm tra trước】 Ố vàng mồ hôi / nách\n"
        "· Khác mồ hôi mới — thường protein + khử mùi\n"
        "· Cấm Javel (làm vàng hơn)\n"
        "· Khó trắng lại hoàn toàn — cần đồng ý"
    ),
    "S_RED_WINE": (
        "◆ 【Kiểm tra trước】 Loại rượu · trạng thái\n"
        "· Đỏ? Trắng/bia/trong → SOP trắng/bia\n"
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
        "ko": ["이소프로필 알코올 70%", "흡수지", "주방세제", "흰 천(찍어 흡수)"],
        "vi": ["Cồn isopropyl 70%", "Giấy thấm", "Nước rửa chén", "Khăn trắng (chấm)"],
        "en": ["IPA 70%", "Blotting paper", "Dish soap", "White cloth (blot only)"],
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
            "· 묻은 직후·흰옷: 나아질 수 있어요. 완전 제거는 보장하지 않아요\n"
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
    stain = graph.get("stain") if isinstance(graph.get("stain"), dict) else {}
    ents = graph.get("entities") if isinstance(graph.get("entities"), dict) else {}
    proto = graph.get("protocol") if isinstance(graph.get("protocol"), dict) else {}
    return str(
        graph.get("_owner_stain_id")
        or sc.get("id")
        or stain.get("id")
        or ents.get("stain_id")
        or proto.get("stain_id")
        or ""
    )


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
    """Only steps with soak=True — freeze/wait minutes must not become soak UI."""
    proto = _proto_dict(graph)
    for s in proto.get("steps") or []:
        if not isinstance(s, dict) or s.get("blocked"):
            continue
        if s.get("soak") and s.get("minutes_lo") is not None:
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


def _use_fresh_path_for_order(graph: dict) -> bool:
    """Item-primary leather/suede (and specialty care) must not use fabric protocol steps."""
    if not isinstance(graph, dict):
        return False
    if graph.get("leather_care") or graph.get("specialty_item_care"):
        return True
    if str(graph.get("protocol_mode") or "") != "item_primary":
        return False
    ic = graph.get("item_context") if isinstance(graph.get("item_context"), dict) else {}
    iid = str(ic.get("id") or "")
    return iid.startswith(("I_LEATHER", "I_SUEDE")) or iid in {
        "I_GLOVE_LEATHER",
        "I_GOLF_GLOVE_LEATHER",
        "I_FAUX_LEATHER",
    }


def _bleach_unsafe_fabric(graph: dict) -> bool:
    """True when textile bleach SOP (oxygen/Javel extras·motions) must not show."""
    if not isinstance(graph, dict):
        return False
    if graph.get("leather_care"):
        return True
    try:
        from protocol import _fabric_flags

        ents = {}
        ic = graph.get("item_context") if isinstance(graph.get("item_context"), dict) else {}
        if ic.get("id"):
            ents["item_id"] = ic["id"]
        md = graph.get("match_diagnosis") if isinstance(graph.get("match_diagnosis"), dict) else {}
        if md.get("fabric_type"):
            ents["fabric_type"] = md["fabric_type"]
        fc = graph.get("fabric_context") if isinstance(graph.get("fabric_context"), dict) else {}
        if fc.get("name") and not ents.get("fabric_type"):
            ents["fabric_type"] = str(fc.get("name") or "").lower()
        flags = _fabric_flags(graph, ents)
        return bool(
            flags.get("delicate_protein")
            or flags.get("is_silk")
            or flags.get("is_wool")
            or flags.get("is_leather")
            or flags.get("is_suede")
            or flags.get("is_fur")
            or flags.get("is_acetate")
            or flags.get("no_oxygen")
        )
    except Exception:
        return False


_BLEACH_TOOL_MARKERS = ("산소", "락스", "표백", "oxy", "javel", "bleach")
_SOLVENT_TOOL_MARKERS = (
    "알코올",
    "이소프로필",
    "ipa",
    "cồn",
    "isopropyl",
    "아세톤",
    "acetone",
    "용제",
)


def _fabric_known(graph: dict) -> bool:
    """True when we have a usable fabric signal (not blank/unknown)."""
    if not isinstance(graph, dict):
        return False
    fc = graph.get("fabric_context") if isinstance(graph.get("fabric_context"), dict) else {}
    for key in ("id", "name", "name_ko", "name_vi"):
        v = str(fc.get(key) or "").strip().lower()
        if v and v not in {"unknown", "unk", "?", "미확인", "불명"}:
            return True
    md = graph.get("match_diagnosis") if isinstance(graph.get("match_diagnosis"), dict) else {}
    ft = str(md.get("fabric_type") or "").strip().lower()
    if ft and ft not in {"unknown", "unk", "?", "미확인", "불명"}:
        return True
    try:
        from protocol import _fabric_flags

        ents: dict = {}
        if ft:
            ents["fabric_type"] = ft
        ic = graph.get("item_context") if isinstance(graph.get("item_context"), dict) else {}
        if ic.get("id"):
            ents["item_id"] = ic["id"]
        flags = _fabric_flags(graph, ents)
        if any(
            flags.get(k)
            for k in (
                "delicate_protein",
                "is_silk",
                "is_wool",
                "is_leather",
                "is_suede",
                "is_fur",
                "is_acetate",
                "is_nylon",
                "is_blend",
                "is_rayon",
            )
        ):
            return True
        fid = str(flags.get("fid") or "").strip().upper()
        fname = str(flags.get("fname") or "").strip().lower()
        if fid and fid not in {"", "UNKNOWN"}:
            return True
        if fname and fname not in {"unknown", "unk", "?", ""}:
            return True
    except Exception:
        return False
    return False


def _color_known_white_safe(graph: dict) -> bool:
    """True only when garment is explicitly white (bleach extras OK by color)."""
    if not isinstance(graph, dict):
        return False
    proto = graph.get("protocol") if isinstance(graph.get("protocol"), dict) else {}
    color = str(proto.get("garment_color") or graph.get("garment_color") or "").strip().lower()
    if color == "white":
        return True
    md = graph.get("match_diagnosis") if isinstance(graph.get("match_diagnosis"), dict) else {}
    return str(md.get("garment_color") or "").strip().lower() == "white"


def _hide_aggressive_tool_extras(graph: dict, extra: str) -> bool:
    """Hide bleach/solvent prep items until fabric (and for bleach: white) is known."""
    ex = (extra or "").lower()
    is_bleach = any(m in ex for m in _BLEACH_TOOL_MARKERS)
    is_solvent = any(m in ex for m in _SOLVENT_TOOL_MARKERS)
    if not is_bleach and not is_solvent:
        return False
    if not _fabric_known(graph):
        return True
    if is_bleach and (_bleach_unsafe_fabric(graph) or not _color_known_white_safe(graph)):
        return True
    if is_solvent and _bleach_unsafe_fabric(graph):
        return True
    return False


def build_one_line_order(graph: dict, lang: str = "ko") -> str:
    """Numbered do-this-next list from Protocol steps."""
    proto = _proto_dict(graph)
    # P0 defense: leather mold etc. — prefer stain_context fresh_path, not fabric bleach SOP
    steps = [] if _use_fresh_path_for_order(graph) else (proto.get("steps") or [])
    # EN fallback when action_en empty — never use VI/KO labels (language purity)
    _en_by_id = {
        "id": "Identify stain · fabric",
        "rinse": "Cold rinse",
        "blot": "Cold blot (no rub)",
        "scrape": "Scrape solids",
        "dish": "Dish soap",
        "enzyme": "Enzyme soak",
        "vinegar": "Vinegar 1:4",
        "alcohol": "Alcohol blot",
        "oxygen": "Oxygen bleach (whites only)",
        "wash": "Wash",
        "light": "Check under bright light",
        "baking": "Baking-soda paste",
        "oil": "Cooking oil to dissolve sap",
        "warm": "Melt with lukewarm water",
        "dry": "Dry brush / tape",
        "soda": "Baking-soda paste",
        "acetone": "Acetone (test corner)",
        "freeze": "Freeze / chill to harden",
        "iron": "Low heat + absorbent paper",
    }
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
            action = str(s.get("action_en") or "").strip()
            if not action:
                sid = str(s.get("id") or "").strip()
                action = _en_by_id.get(sid) or sid.replace("_", " ").title()
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
            sid_step = str(s.get("id") or "").strip()
            action = _soften_step_label(action)
            action = _ensure_ko_step_verb(
                sid_step,
                action,
                chem=str(s.get("chem") or ""),
                blocked=bool(s.get("blocked")),
            )
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


def _ensure_ko_step_verb(
    step_id: str,
    action: str,
    *,
    chem: str = "",
    blocked: bool = False,
) -> str:
    """One-line order must say what to DO, not only product names."""
    t = (action or "").strip()
    if blocked:
        return t
    chem_u = str(chem or "").upper().strip()
    # Protocol already substituted S1 / delicate wording — never re-inject
    # bleach/acid verbs from step id (oxygen/chlorine/vinegar/acetone).
    if chem_u == "S1" or any(
        x in t
        for x in (
            "중성세제",
            "섬세 원단",
            "아세테이트:",
            "실크·울",
            "금지 —",
            "거절·전문",
        )
    ):
        if any(
            x in t
            for x in (
                "하세요",
                "주세요",
                "마세요",
                "두세요",
                "바르",
                "담가",
                "헹구",
                "확인",
                "깨",
                "녹이",
                "처리",
                "전문",
                "금지",
            )
        ):
            return t
        return f"{t}로 처리해 주세요" if t else t
    if any(x in t for x in ("하세요", "주세요", "마세요", "두세요", "바르", "담가", "헹구", "확인", "깨", "녹이")):
        return t
    by_id = {
        "rinse": "찬물로 헹궈 주세요",
        "blot": "찬물로 꾹꾹 눌러 흡수하세요(문지르지 마세요)",
        "scrape": "고형물을 살살 긁어 주세요",
        "dish": "주방세제(식기용·중성)를 얼룩에 바르고 잠시 두세요(섞지 마세요)",
        "enzyme": "효소계 세제(프로테아제)로 담가 주세요",
        "vinegar": "식초 1:4로 담가 냄새를 줄이세요(완전 제거 보장 아님 · 앞 단계와 섞지 마세요)",
        "alcohol": "알코올을 흰 천에 묻혀 꾹꾹 눌러 흡수하세요",
        "oxygen": "흰옷만 산소계 표백제(과탄산·옥시클린 계열)로 담가 주세요",
        "chlorine": "흰 면만 희석 락스(매니저 확인·식초와 혼합 금지)",
        "wash": "세탁해 주세요",
        "light": "말리기 전 밝은 조명에서 잔색을 확인해 주세요",
        "freeze": "비닐에 넣어 냉동실에서 단단해질 때까지 두세요",
        "break": "바삭할 때 깨서 제거하세요",
        "acetone": "잔여만 아세톤 극소(매니저·구석 테스트)",
        "baking": "베이킹소다 페이스트를 바르고 두세요",
        "soda": "베이킹소다 페이스트를 바르고 두세요",
        "dry": "마른 채로 털거나 테이프로 제거하세요",
        "warm": "미지근한 물로 먼저 녹이세요",
        "oil": "식용유 소량으로 수액을 녹인 뒤 주방세제로 빼세요",
    }
    if step_id in by_id:
        return by_id[step_id]
    if t:
        return f"{t}로 처리해 주세요"
    return t


def _soften_step_label(text: str) -> str:
    t = text.strip()
    if "하세요" in t or "마세요" in t or "해 주세요" in t:
        try:
            from owner_plain_lang import expand_owner_jargon

            return expand_owner_jargon(t, "ko")
        except Exception:
            return t
    reps = (
        ("즉시 찬물", "바로 찬물로 헹궈 주세요"),
        ("찬물 헹굼", "찬물로 헹궈 주세요"),
        ("알코올 블롯(테스트)", "알코올은 흰 천에 묻혀 꾹꾹 눌러 흡수하세요(구석 테스트 먼저)"),
        ("알코올 블롯", "알코올은 흰 천에 묻혀 꾹꾹 눌러 흡수하세요"),
        ("흰옷 산소 장침지", "흰옷만 산소계 표백제(과탄산·옥시클린 계열)로 담가 주세요"),
        ("흰옷 산소", "흰옷만 산소계 표백제(과탄산·옥시클린 계열)를 쓰세요"),
        ("건조 전 강광", "말리기 전 밝은 조명에서 잔색을 확인해 주세요"),
        ("세탁; 잔색 고지", "세탁해 주세요. 잔색이 남을 수 있다고 고객에게 말씀하세요"),
        ("세탁", "세탁해 주세요"),
    )
    for a, b in reps:
        if t == a:
            t = b
            break
        if t.startswith(a):
            t = b + t[len(a) :]
            break
    try:
        from owner_plain_lang import expand_owner_jargon

        return expand_owner_jargon(t, "ko")
    except Exception:
        return t


def build_tools_names_only(graph: dict, lang: str = "ko") -> str:
    try:
        from owner_plain_lang import tool_line_with_purpose
    except Exception:
        def tool_line_with_purpose(name: str, lang: str = "ko") -> str:  # type: ignore
            return name

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
    if lang == "ko":
        basics = ["니트릴 장갑", "흰 면 천 여러 장", "타이머(핸드폰 OK)"]
        head = "◆ 【준비물】 이름 + 용도(초보용)"
        extra_head = "· "
    elif lang == "vi":
        basics = ["Găng nitrile", "Khăn trắng", "Hẹn giờ"]
        head = "◆ 【Chuẩn bị】 Tên + công dụng (cho người mới)"
        extra_head = "· "
    else:
        basics = ["Nitrile gloves", "White cloths", "Timer"]
        head = "◆ 【Tools】 Name + what it's for (beginner)"
        extra_head = "· "
    lines = [f"{extra_head}{tool_line_with_purpose(b, lang)}" for b in basics]
    seen_lower = {ln.lower() for ln in lines}
    for n in names:
        if any(x in n.lower() for x in ("장갑", "găng", "glove", "흰 천", "khan", "cloth", "타이머", "timer", "hẹn")):
            continue
        line = f"{extra_head}{tool_line_with_purpose(n, lang)}"
        if line.lower() in seen_lower:
            continue
        lines.append(line)
        seen_lower.add(line.lower())
    sid = _motion_stain_id(graph)
    # Leather/suede + delicate: never append textile bleach extras
    if graph.get("leather_care") or _bleach_unsafe_fabric(graph):
        extras = []
    else:
        extras = (STAIN_TOOL_EXTRAS.get(sid) or {}).get(lang) or []
    for ex in extras:
        ex = str(ex).strip()
        if not ex:
            continue
        # P0: fabric/color unknown → hide bleach & solvent prep (confirm first)
        if _hide_aggressive_tool_extras(graph, ex):
            continue
        line = f"{extra_head}{tool_line_with_purpose(ex, lang)}"
        if line.lower() in seen_lower:
            continue
        if any(ex.lower() in ln.lower() or ln.lower() in line.lower() for ln in lines):
            continue
        lines.append(line)
        seen_lower.add(line.lower())
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
        try:
            from owner_plain_lang import expand_owner_jargon, block_enzyme_emergency_tip

            out = expand_owner_jargon(out, lang)
            enz = block_enzyme_emergency_tip(_motion_stain_id(g), lang, g)
            if enz and enz not in out:
                out = out.rstrip() + "\n\n" + enz
        except Exception as _e:
            print(f"[CLARITY] plain early skip: {type(_e).__name__}: {_e}")
        foot = (_GRADE_FOOTER.get(lang) or _GRADE_FOOTER["ko"]).get(grade, "")
        if foot and "【다시 한번 고객 고지】" not in out and "【Nhắc khách】" not in out:
            out = out.rstrip() + "\n\n" + foot
        return _normalize_fresh_wording(out)

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
    if g.get("leather_care"):
        if lang == "vi":
            outlook_override = (
                "◆ 【Kết quả kỳ vọng】\n"
                "· Da + mốc: chỉ bề mặt sớm có thể đỡ — không cam kết sạch hết\n"
                "· Ngấm sâu / nứt → chuyên"
            )
        elif lang == "en":
            outlook_override = (
                "◆ 【Expected result】\n"
                "· Leather mold: surface/early may improve — full removal not promised\n"
                "· Deep / cracked → refer pro"
            )
        else:
            outlook_override = (
                "◆ 【예상 결과】\n"
                "· 가죽 곰팡이: 표면·조기만 개선 가능 — 완전 제거 비보장\n"
                "· 침투·갈라짐 → 전문"
            )
    if outlook_override:
        outlook = outlook_override
    else:
        outlook = (_SOFT_OUTLOOK.get(lang) or _SOFT_OUTLOOK["ko"]).get(int(grade) or 2, "")
    if outlook:
        flow_bits.append(outlook)
    if g.get("leather_care"):
        if lang == "vi":
            status = (
                "◆ 【Kiểm tra trước】 Da + mốc\n"
                "· Phân biệt da bóng vs suede\n"
                "· CẤM ngâm giấm / tẩy oxy / Javel / máy giặt\n"
                "· PPE + ngoài trời · đồng ý trước khi làm"
            )
        elif lang == "en":
            status = (
                "◆ 【Check first】 Leather + mold\n"
                "· Smooth leather vs suede\n"
                "· No vinegar soak / oxygen / chlorine / washer\n"
                "· PPE outdoors · get consent first"
            )
        else:
            status = (
                "◆ 【먼저 확인】 가죽 + 곰팡이\n"
                "· 평활 가죽인지 스웨이드인지 확인\n"
                "· 식초 통담금·산소·락스·세탁기 금지\n"
                "· PPE·야외 · 진행 전 동의"
            )
    else:
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
            try:
                from owner_plain_lang import expand_owner_jargon

                compound = expand_owner_jargon(compound, lang)
            except Exception:
                pass
            detail_bits.append(compound)
    spot = build_spot_test_block(g, lang)
    if spot:
        detail_bits.append(spot)

    motions = ""
    try:
        from owner_hand_motions import build_hand_motions

        # Leather/suede + delicate: never attach textile mildew bleach Steps
        if g.get("leather_care") or (
            sid == "S_MILDEW" and _bleach_unsafe_fabric(g)
        ):
            sc_m = g.get("stain_context") if isinstance(g.get("stain_context"), dict) else {}
            path = ""
            if lang == "vi":
                path = str(sc_m.get("fresh_path_vi") or "")
            elif lang == "en":
                path = str(sc_m.get("fresh_path_en") or sc_m.get("fresh_path") or "")
            else:
                path = str(sc_m.get("fresh_path_ko") or "")
            if path:
                if g.get("leather_care"):
                    if lang == "vi":
                        motions = "◆ 【Tay nghề da】\n" + path
                    elif lang == "en":
                        motions = "◆ 【Leather hand steps】\n" + path
                    else:
                        motions = "◆ 【가죽 손동작】\n" + path
                else:
                    if lang == "vi":
                        motions = "◆ 【Tay nghề (vải nhạy)】\n" + path
                    elif lang == "en":
                        motions = "◆ 【Delicate fabric steps】\n" + path
                    else:
                        motions = "◆ 【섬세 원단 손동작】\n" + path
            elif not g.get("leather_care"):
                motions = build_hand_motions(sid, lang, graph=g)
        else:
            motions = build_hand_motions(sid, lang, graph=g)
    except Exception:
        motions = ""
    if motions:
        try:
            from owner_plain_lang import expand_owner_jargon

            motions = expand_owner_jargon(motions, lang)
        except Exception:
            pass

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
            try:
                from owner_plain_lang import expand_owner_jargon

                why = expand_owner_jargon(why, lang)
            except Exception:
                pass
            detail_bits.append(why)
    else:
        # Fallback: keep body but strip emoji TOC steps to reduce clutter
        body_clean = _strip_toc_steps(body.strip())
        if body_clean:
            try:
                from owner_plain_lang import expand_owner_jargon

                body_clean = expand_owner_jargon(body_clean, lang)
            except Exception:
                pass
            detail_bits.append(body_clean)

    detail_bits.append(build_donts_block(g, lang))
    if _mid is not None:
        try:
            mold_gate = _mid.block_mold_fabric_gate(g, lang)
            if mold_gate:
                detail_bits.append(mold_gate)
            mold_rec = _mid.block_mold_recurrence(sid, lang)
            if mold_rec:
                detail_bits.append(mold_rec)
        except Exception:
            pass
        for tip in _mid.block_vn_tips(sid, lang):
            try:
                from owner_plain_lang import expand_owner_jargon

                tip = expand_owner_jargon(tip, lang)
            except Exception:
                pass
            detail_bits.append(tip)
        chem_blk = _mid.block_chem(g, lang)
        if chem_blk:
            try:
                from owner_plain_lang import expand_owner_jargon

                chem_blk = expand_owner_jargon(chem_blk, lang)
            except Exception:
                pass
            detail_bits.append(chem_blk)
    try:
        from owner_plain_lang import block_enzyme_emergency_tip

        enz = block_enzyme_emergency_tip(sid, lang, g)
        if enz:
            detail_bits.append(enz)
    except Exception as _e:
        print(f"[CLARITY] enzyme tip skip: {type(_e).__name__}: {_e}")
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
    assembled = flow + ZALO_MSG_SPLIT + detail
    return _normalize_fresh_wording(assembled)


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


def _normalize_fresh_wording(text: str) -> str:
    """Replace laundry-jargon 「신선」 with clear 「방금 묻은 직후」."""
    if not text:
        return text
    reps = (
        ("· 신선: 개선", "· 방금 묻은 직후: 색·냄새가 나아질 수 있음"),
        ("· 흰·신선: 개선", "· 흰옷·방금 묻은 직후: 나아질 수 있음"),
        ("· 면·신선: 개선", "· 면·방금 묻은 직후: 나아질 수 있음"),
        ("· 수용성·신선: 개선", "· 수용성·방금 묻은 직후: 나아질 수 있음"),
        ("· 신선:", "· 방금 묻은 직후:"),
        ("신선+직사광선", "방금 묻은 뒤+직사광선"),
        ("신선·면", "방금 묻은 직후·면"),
        ("신선·흡수", "방금 묻은 직후·흡수"),
        ("Fresh:", "Just stained:"),
        ("· Fresh:", "· Just stained:"),
    )
    out = text
    for a, b in reps:
        out = out.replace(a, b)
    return out


for _sid, _blk in list(STAIN_SOFT_OUTLOOK.items()):
    if isinstance(_blk, dict):
        STAIN_SOFT_OUTLOOK[_sid] = {
            lk: _normalize_fresh_wording(lv) if isinstance(lv, str) else lv
            for lk, lv in _blk.items()
        }

# Force-refresh fish-sauce clarity (override cryptic v38 leftovers if any)
STAIN_STATUS_KO["S_FISH_SAUCE"] = (
    "◆ 【먼저 확인】 느억맘·액젓·피시소스\n"
    "· 방금 묻었나요, 이미 말랐나요?\n"
    "· 방금 묻음 → 냄새가 덜 밸 수 있음 · 마름·열 거침 → 냄새 반복·잔취 가능\n"
    "· 온수·건조기를 먼저 쓰지 마세요 · 락스 금지 · 냄새 완전 제거는 보장하지 마세요"
)
STAIN_SOFT_OUTLOOK["S_FISH_SAUCE"] = {
    "ko": (
        "◆ 【예상 결과】\n"
        "· 방금 묻은 직후: 색·냄새가 나아질 수 있음\n"
        "· 마름·열: 냄새가 남을 수 있음 — 접수 때 동의"
    ),
    "vi": (
        "◆ 【Kết quả kỳ vọng】\n"
        "· Mới dính: màu/mùi có thể đỡ\n"
        "· Khô/nhiệt: dễ còn mùi — đồng ý khi nhận"
    ),
    "en": (
        "◆ 【Expected result】\n"
        "· Just stained: color/odor may improve\n"
        "· Dried/heat: odor may remain — get consent"
    ),
}
STAIN_TOOL_EXTRAS["S_FISH_SAUCE"] = {
    "ko": [
        "찬물",
        "효소계 세제(프로테아제·라벨에 효소/enzyme)",
        "흰 식초(냄새 중화·줄이기용)",
        "산소계 표백제(흰옷만·과탄산)",
        "담금통(옷을 담그는 대야)",
    ],
    "vi": ["Nước lạnh", "Nước giặt enzyme (protease)", "Giấm (giảm mùi)", "Oxy trắng", "Chậu ngâm"],
    "en": ["Cold water", "Enzyme detergent (protease)", "Vinegar (reduce odor)", "Oxygen bleach (whites)", "Soak basin"],
}
STAIN_DONTS_KO["S_FISH_SAUCE"] = [
    "온수·건조기를 먼저 쓰지 마세요 → 냄새가 더 고착될 수 있어요",
    "냄새 완전 제거를 보장하지 마세요 — 남을 수 있다고 먼저 말씀하세요",
    "락스로 느억맘 냄새를 지우지 마세요",
    "향수·섬유유연제로 냄새만 덮지 마세요",
]
