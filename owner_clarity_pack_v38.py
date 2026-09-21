# -*- coding: utf-8 -*-
"""Bulk clarity fields for remaining L1 + priority L2 (no % success rates)."""
from __future__ import annotations

# Short status branches — wet / dry / heat where useful
EXTRA_STATUS_KO: dict[str, str] = {
    "S_MILK": (
        "◆ 【먼저 확인】 우유\n"
        "· 온수·건조기 먼저 금지 → 단백질이 익어 고착돼요\n"
        "· 젖어 있다 → 찬물·효소 중심\n"
        "· 이미 말랐다 → 잔색 가능 — 사전 고지"
    ),
    "S_EGG": (
        "◆ 【먼저 확인】 계란\n"
        "· 처음부터 온수·건조기 금지\n"
        "· 고형 먼저 걷고 찬물·효소\n"
        "· 익어 고착되면 부분 제거만 기대"
    ),
    "S_TEA": (
        "◆ 【먼저 확인】 차(탄닌)\n"
        "· 젖어 있다 → 찬물·식초 1:4\n"
        "· 말랐다 → 잔색 가능\n"
        "· 유색·실크 산소 신중"
    ),
    "S_FRUIT_JUICE": (
        "◆ 【먼저 확인】 과일주스\n"
        "· 즉시 찬물 · 식초 1:4(탄닌·색소)\n"
        "· 당분 남은 채 말리면 황변될 수 있어요"
    ),
    "S_SOFT_DRINK": (
        "◆ 【먼저 확인】 탄산·청량음료\n"
        "· 끈적·당분 먼저 헹구기\n"
        "· 남은 채 말리면 황변\n"
        "· 유색 색소면 식초·흰옷만 산소"
    ),
    "S_KETCHUP": (
        "◆ 【먼저 확인】 케첩\n"
        "· 고형 제거 → 주방세제 → 식초 1:4\n"
        "· 이른 열 금지(붉은 색소 고착)\n"
        "· 이미 건조기 → 잔색 고지"
    ),
    "S_TOMATO_SAUCE": (
        "◆ 【먼저 확인】 토마토소스\n"
        "· 문지르면 번짐 · 고형 먼저\n"
        "· 주방세제 → 식초 · 흰옷만 산소\n"
        "· 잔색 채 말리지 마세요"
    ),
    "S_CHOCOLATE": (
        "◆ 【먼저 확인】 초콜릿\n"
        "· 굳으면 살살 긁기 → 지방(세제) → 색소\n"
        "· 지방·색소 남은 채 건조 금지"
    ),
    "S_GRASS": (
        "◆ 【먼저 확인】 풀·잔디\n"
        "· 흙 털기 → 알코올은 구석 테스트 후\n"
        "· 초록 남은 채 말리지 마세요\n"
        "· 전분 이염이면 별도 요령"
    ),
    "S_SWEAT_FRESH": (
        "◆ 【먼저 확인】 신선 땀\n"
        "· 방금·냄새 위주 → 효소·세탁\n"
        "· 이미 노랗게 변했으면 황변(S_SWEAT_YELLOW) 요령\n"
        "· 락스로 황변 건드리지 마세요"
    ),
    "S_FOUNDATION": (
        "◆ 【먼저 확인】 파운데이션\n"
        "· 실리콘·오일 → 주방세제 먼저, 그다음 색소(알코올)\n"
        "· 문지르면 번짐 · 실크는 약하게\n"
        "· 환기(알코올 사용 시)"
    ),
    "S_IODINE": (
        "◆ 【먼저 확인】 요오드·포비돈\n"
        "· 색소가 셉니다 — 매니저 확인\n"
        "· 알코올 구석 테스트 · 환기\n"
        "· 실크·울은 약하게·짧게 또는 전문"
    ),
    "S_WHITE_WINE_BEER": (
        "◆ 【먼저 확인】 화이트와인·맥주\n"
        "· 당분이 나중에 누렇게 될 수 있어요 — 사전 고지\n"
        "· 즉시 흡수 · 세제 → 흰옷만 산소"
    ),
    "S_BUBBLE_TEA": (
        "◆ 【먼저 확인】 버블티\n"
        "· 순서: 지방(펄) → 단백질 → 차 색소(식초)\n"
        "· 온수 먼저 금지"
    ),
    "S_BBQ_SAUCE": (
        "◆ 【먼저 확인】 BBQ소스\n"
        "· 효소 → 주방세제 → 식초 순서 지키기\n"
        "· 실크·울 효소 금지"
    ),
    "S_MAYO": (
        "◆ 【먼저 확인】 마요네즈\n"
        "· 온수 먼저 금지(계란 단백질)\n"
        "· 지방(세제) 먼저, 효소는 그다음"
    ),
    "S_BUTTER": (
        "◆ 【먼저 확인】 버터\n"
        "· 전분·흡착 → 세제 · 미끄러움 남으면 말리지 마세요"
    ),
    "S_FISH_SAUCE": (
        "◆ 【먼저 확인】 액젓·피시소스\n"
        "· 냄새·염 · 온수·건조기 먼저 금지\n"
        "· 냄새 남을 수 있음 — 보장 금지"
    ),
    "S_BABY_FORMULA": (
        "◆ 【먼저 확인】 분유\n"
        "· 락스 절대 금지 · 온수 먼저 금지\n"
        "· 효소·찬물 중심"
    ),
    "S_COLLAR_STAIN": (
        "◆ 【먼저 확인】 목때·칼라\n"
        "· 락스 금지(더 누래요)\n"
        "· 마른 부위에 효소 → 세탁 · 솔은 약하게"
    ),
}

EXTRA_STATUS_VI: dict[str, str] = {
    "S_MILK": (
        "◆ 【Kiểm tra trước】 Sữa\n"
        "· Cấm nước nóng/sấy sớm\n"
        "· Còn ướt → lạnh + enzyme\n"
        "· Đã khô → báo còn vết"
    ),
    "S_EGG": (
        "◆ 【Kiểm tra trước】 Trứng\n"
        "· Cấm nóng/sấy đầu\n"
        "· Gỡ đặc rồi lạnh + enzyme"
    ),
    "S_TEA": (
        "◆ 【Kiểm tra trước】 Trà\n"
        "· Ướt → lạnh + giấm 1:4\n"
        "· Đã khô → dễ còn\n"
        "· Oxy cẩn thận áo màu/lụa"
    ),
    "S_GRASS": (
        "◆ 【Kiểm tra trước】 Cỏ\n"
        "· Phủi đất → thử góc rồi cồn\n"
        "· Còn xanh → không sấy"
    ),
    "S_FOUNDATION": (
        "◆ 【Kiểm tra trước】 Kem nền\n"
        "· Silicon/dầu → nước rửa chén trước, rồi cồn\n"
        "· Không chà · thông gió khi dùng cồn"
    ),
    "S_IODINE": (
        "◆ 【Kiểm tra trước】 Iodine\n"
        "· Màu mạnh — hỏi quản lý\n"
        "· Thử góc cồn + thông gió"
    ),
    "S_KETCHUP": (
        "◆ 【Kiểm tra trước】 Tương cà\n"
        "· Gỡ đặc → nước rửa chén → giấm\n"
        "· Cấm nhiệt sớm"
    ),
    "S_CHOCOLATE": (
        "◆ 【Kiểm tra trước】 Sô-cô-la\n"
        "· Cạo khi cứng → dầu rồi màu\n"
        "· Không sấy khi còn nhờn/màu"
    ),
    "S_SWEAT_FRESH": (
        "◆ 【Kiểm tra trước】 Mồ hôi mới\n"
        "· Mới/mùi → enzyme\n"
        "· Đã vàng → SOP ố vàng nách"
    ),
}

EXTRA_TOOL_EXTRAS: dict[str, dict[str, list[str]]] = {
    "S_MILK": {
        "ko": ["효소세제", "찬물", "담금통"],
        "vi": ["Nước giặt enzyme", "Nước lạnh", "Chậu ngâm"],
        "en": ["Enzyme detergent", "Cold water", "Basin"],
    },
    "S_EGG": {
        "ko": ["효소세제", "찬물", "흰 천"],
        "vi": ["Enzyme", "Nước lạnh", "Khăn trắng"],
        "en": ["Enzyme detergent", "Cold water", "White cloth"],
    },
    "S_TEA": {
        "ko": ["흰 식초", "분무기(1:4)", "산소표백제(흰옷만)"],
        "vi": ["Giấm trắng", "Bình xịt 1:4", "Bột oxy (trắng)"],
        "en": ["White vinegar", "Spray 1:4", "Oxygen bleach (white)"],
    },
    "S_FRUIT_JUICE": {
        "ko": ["흰 식초", "찬물", "산소(흰옷만)"],
        "vi": ["Giấm trắng", "Nước lạnh", "Oxy (trắng)"],
        "en": ["White vinegar", "Cold water", "Oxygen (white)"],
    },
    "S_SOFT_DRINK": {
        "ko": ["찬물", "중성세제", "식초(색소 시)"],
        "vi": ["Nước lạnh", "Giặt trung tính", "Giấm (nếu màu)"],
        "en": ["Cold water", "Neutral detergent", "Vinegar if dyed"],
    },
    "S_KETCHUP": {
        "ko": ["주방세제", "흰 식초", "산소(흰옷만)"],
        "vi": ["Nước rửa chén", "Giấm trắng", "Oxy (trắng)"],
        "en": ["Dish soap", "White vinegar", "Oxygen (white)"],
    },
    "S_TOMATO_SAUCE": {
        "ko": ["주방세제", "흰 식초", "산소(흰옷만)"],
        "vi": ["Nước rửa chén", "Giấm", "Oxy (trắng)"],
        "en": ["Dish soap", "Vinegar", "Oxygen (white)"],
    },
    "S_CHOCOLATE": {
        "ko": ["주방세제", "효소(선택)", "흰 천"],
        "vi": ["Nước rửa chén", "Enzyme (tuỳ)", "Khăn trắng"],
        "en": ["Dish soap", "Enzyme (optional)", "White cloth"],
    },
    "S_GRASS": {
        "ko": ["이소프로필 알코올 70%", "효소세제", "흰 천"],
        "vi": ["Cồn IPA 70%", "Enzyme", "Khăn trắng"],
        "en": ["IPA 70%", "Enzyme detergent", "White cloth"],
    },
    "S_SWEAT_FRESH": {
        "ko": ["효소세제", "담금통", "중성세제(실크·울)"],
        "vi": ["Enzyme", "Chậu ngâm", "Trung tính (lụa/len)"],
        "en": ["Enzyme detergent", "Basin", "Neutral (silk/wool)"],
    },
    "S_SOY_SAUCE": {
        "ko": ["찬물", "주방세제", "식초", "산소(흰옷만)"],
        "vi": ["Nước lạnh", "Nước rửa chén", "Giấm", "Oxy (trắng)"],
        "en": ["Cold water", "Dish soap", "Vinegar", "Oxygen (white)"],
    },
    "S_MUD": {
        "ko": ["솔(마른 흙)", "중성·주방세제", "찬물"],
        "vi": ["Bàn chải (đất khô)", "Xà phòng", "Nước lạnh"],
        "en": ["Brush (dry mud)", "Detergent", "Cold water"],
    },
    "S_FOUNDATION": {
        "ko": ["주방세제", "이소프로필 알코올 70%", "흰 천"],
        "vi": ["Nước rửa chén", "Cồn IPA 70%", "Khăn trắng"],
        "en": ["Dish soap", "IPA 70%", "White cloth"],
    },
    "S_IODINE": {
        "ko": ["이소프로필 알코올 70%", "흰 천", "산소(흰옷만)", "장갑"],
        "vi": ["Cồn IPA 70%", "Khăn trắng", "Oxy (trắng)", "Găng"],
        "en": ["IPA 70%", "White cloth", "Oxygen (white)", "Gloves"],
    },
    "S_WHITE_WINE_BEER": {
        "ko": ["흰 천", "중성세제", "산소(흰옷만)"],
        "vi": ["Khăn trắng", "Giặt trung tính", "Oxy (trắng)"],
        "en": ["White cloth", "Neutral detergent", "Oxygen (white)"],
    },
    "S_BUBBLE_TEA": {
        "ko": ["주방세제", "효소", "흰 식초"],
        "vi": ["Nước rửa chén", "Enzyme", "Giấm trắng"],
        "en": ["Dish soap", "Enzyme", "White vinegar"],
    },
    "S_BBQ_SAUCE": {
        "ko": ["효소", "주방세제", "흰 식초"],
        "vi": ["Enzyme", "Nước rửa chén", "Giấm"],
        "en": ["Enzyme", "Dish soap", "Vinegar"],
    },
    "S_MAYO": {
        "ko": ["주방세제", "효소", "찬물"],
        "vi": ["Nước rửa chén", "Enzyme", "Nước lạnh"],
        "en": ["Dish soap", "Enzyme", "Cold water"],
    },
    "S_BUTTER": {
        "ko": ["전분·베이비파우더", "주방세제"],
        "vi": ["Bột/phấn baby", "Nước rửa chén"],
        "en": ["Starch/baby powder", "Dish soap"],
    },
    "S_FISH_SAUCE": {
        "ko": ["찬물", "효소·세제", "식초(냄새)"],
        "vi": ["Nước lạnh", "Enzyme/xà phòng", "Giấm (mùi)"],
        "en": ["Cold water", "Enzyme/detergent", "Vinegar (odor)"],
    },
    "S_BABY_FORMULA": {
        "ko": ["효소세제", "찬물", "담금통"],
        "vi": ["Enzyme", "Nước lạnh", "Chậu"],
        "en": ["Enzyme detergent", "Cold water", "Basin"],
    },
    "S_COLLAR_STAIN": {
        "ko": ["효소세제", "연질 솔", "산소(허용 시)"],
        "vi": ["Enzyme", "Bàn chải mềm", "Oxy (nếu được)"],
        "en": ["Enzyme detergent", "Soft brush", "Oxygen if allowed"],
    },
    "S_MILK_COFFEE": {
        "ko": ["효소세제", "흰 식초", "분무기"],
        "vi": ["Enzyme", "Giấm trắng", "Bình xịt"],
        "en": ["Enzyme detergent", "White vinegar", "Spray bottle"],
    },
}

EXTRA_SOFT_OUTLOOK: dict[str, dict[str, str]] = {
    "S_BLACK_COFFEE": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 묻은 직후: 잘 빠지는 편\n"
            "· 마름·열 지남: 잔색 가능 — 동의 받기\n"
            "· 유색·실크: 산소 없이 식초 반복"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới dính: thường ra tốt\n"
            "· Đã khô/nhiệt: dễ còn — cần đồng ý\n"
            "· Áo màu/lụa: chỉ giấm, không oxy"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh: often good\n"
            "· Dried/heat: residual possible\n"
            "· Color/silk: vinegar only, no oxygen"
        ),
    },
    "S_MILK": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 신선·찬물: 잘 빠지는 편\n"
            "· 온수·건조기 먼저: 고착 — 부분만"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới + lạnh: thường tốt\n"
            "· Nóng/sấy sớm: chỉ một phần"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh cold: often good\n"
            "· Hot/dryer first: partial only"
        ),
    },
    "S_EGG": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 익히기 전: 개선 기대\n"
            "· 이미 익어 고착: 부분만 — 고지"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Chưa chín: cải thiện\n"
            "· Đã chín: chỉ một phần"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Before cooked-in: improves\n"
            "· Heat-set protein: partial"
        ),
    },
    "S_KETCHUP": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 신선: 잘 빠지는 편\n"
            "· 열고착 붉은색: 잔색 가능"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới: thường ra tốt\n"
            "· Đỏ cố định nhiệt: dễ còn"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh: often good\n"
            "· Heat-set red: residual possible"
        ),
    },
    "S_GRASS": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 신선·테스트 OK: 초록 개선\n"
            "· 프린트·실크: 손상 주의 · 중단 가능"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới + test OK: cải thiện xanh\n"
            "· In/lụa: rủi ro — có thể dừng"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh + spot OK: green improves\n"
            "· Print/silk: damage risk — may stop"
        ),
    },
    "S_FOUNDATION": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 겉 실리콘만: 잘 빠지는 편\n"
            "· 색소까지 먹음: 잔색 가능"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Chỉ silicon ngoài: thường tốt\n"
            "· Đã ngấm màu: dễ còn"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Surface silicone: often good\n"
            "· Pigment set: residual possible"
        ),
    },
    "S_IODINE": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 신선·면: 개선 기대\n"
            "· 마름·실크: 잔색·손상 위험 — 전문 검토"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới + cotton: cải thiện\n"
            "· Khô/lụa: dễ còn — xem chuyên"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh cotton: improves\n"
            "· Dried/silk: residual — consider refer"
        ),
    },
    "S_KIMCHI": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 신선·흰옷: 개선 기대\n"
            "· 고추 색소·유색: 잔색·냄새 가능 — 동의"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới + trắng: cải thiện\n"
            "· Ớt/áo màu: dễ còn màu/mùi"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Fresh white: improves\n"
            "· Chili/color: residual/odor possible"
        ),
    },
    "S_MUD": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 말려 털기 후: 잘 빠지는 편\n"
            "· 적토면 별도(라테라이트) · 더 어려움"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Sau phủi khô: thường tốt\n"
            "· Đất đỏ laterite: khó hơn"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· After dry brush: often good\n"
            "· Laterite red earth: harder"
        ),
    },
}

