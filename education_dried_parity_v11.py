# -*- coding: utf-8 -*-
"""Dried-path parity v11 — push age score toward 90+.

Closes:
1) v10 stains missing from runtime DRIED_PATH_* overlays
2) Thin dried paths (too short / few steps)
3) Per-stain rescue for remaining Protocol IDs (not group-only)
4) VI diacritic dried paths for the above
"""
from __future__ import annotations

# ── Deep dried paths (KO) ────────────────────────────────────────────────────
DRIED_PATH_KO_V11: dict[str, str] = {
    "S_DOENJANG": (
        "(1) 마른 된장·된장찌개 국물 확인. (2) 고형 Cap1 긁기·찬물(문지르기 금지). "
        "(3) 주방세제 Cap2. (4) 효소 장침지 30–60분. (5) 흰/면 산소(테스트)·실크·울 금지. "
        "(6) 세탁·강광. 갈색 잔갈·100% 비보장 고지."
    ),
    "S_GOCHUJANG": (
        "(1) 마른 고추장 확인. (2) 긁기·찬물. (3) 주방세제 Cap2. "
        "(4) 식초 1:4 장침지 15–30분 반복. (5) 흰/면 산소(테스트). "
        "(6) 세탁·강광. 적갈 고추 색소 잔여·100% 비보장 고지."
    ),
    "S_PERSIMMON": (
        "(1) 마른·갈변 감물(탄닌) 확인 — 이미 고착 가능. (2) 찬물만·문지르기 금지. "
        "(3) 식초 1:4 장침지 15–30분 반복. (4) 흰/면 산소(테스트). "
        "(5) 세탁. (6) 강광. 갈변 고착·100% 불가 고지."
    ),
    "S_CRAYON": (
        "(1) 굳은 크레용·왁스+안료. (2) 얼리거나 차게 해 깨기·긁기. "
        "(3) 흡수지+낮은 열 다리미로 왁스 이전(반복·얼룩 위 고열 금지). "
        "(4) 잔여 주방세제. (5) 흰/면 색소 산소(테스트). "
        "(6) 세탁·강광. 안료 잔여·100% 비보장 고지."
    ),
    "S_SOFTENER_SPOT": (
        "(1) 열고착·마른 유연제 오일 링 확인. (2) 주방세제 Cap2로 탈지·담금 15–30분 반복. "
        "(3) 미온 재세탁. (4) 필요 시 식초 1:4 헹굼 보조. "
        "(5) 미끄럼·오일감 없어진 뒤만 건조. (6) 열고착 링 한계·100% 비보장 고지."
    ),
    # Deepen thin base paths
    "S_BUTTER": (
        "(1) 마른·열고착 의심 버터. (2) 차게 긁기→전분/흡착분. "
        "(3) 주방세제 Cap2→필요 시 리파아제. (4) 효소(유단백 흔적). "
        "(5) 세탁. (6) 미끄럼 확인 후 건조. 열고착·100% 비보장 고지."
    ),
    "S_WHITE_WINE_BEER": (
        "(1) 이미 황변·마른 당(화이트와인·맥주). (2) 찬물. "
        "(3) 식초 1:4 장침지 15–30분. (4) 맥주 단백질 흔적: 효소 추가 가능. "
        "(5) 흰옷 짧은 산소(테스트). (6) 세탁·통풍. 오래된 당분 황변 100% 비보장."
    ),
    "S_PAINT_LATEX": (
        "(1) 이미 마른 수성 페인트 막. (2) 구석 테스트. "
        "(3) 약한 용제/알코올 블롯 다회(문지르기 금지·환기). "
        "(4) 주방세제. (5) 세탁. (6) 성공률↓·유성이면 유성 페인트 경로. 100% 비보장."
    ),
    "S_TOMATO_SAUCE": (
        "(1) 마른 토마토·파스타소스. (2) 고형 제거. (3) 침지+주방세제(기름 먼저). "
        "(4) 식초 1:4 장침지 15–30분. (5) 흰/면 산소(테스트). "
        "(6) 세탁·강광. 리코펜 잔색·100% 비보장 고지."
    ),
    "S_GREASE": (
        "(1) 마른 그리즈·기름때. (2) 전분 흡착 2회. (3) 주방세제 Cap2 / 리파아제. "
        "(4) 반복 탈지. (5) 세탁. (6) 미끄럼·냄새 확인 후 건조. 오래된 지방 성공률↓ 고지."
    ),
    "S_FRUIT_JUICE": (
        "(1) 마른 과일주스·탄닌 색소. (2) 찬물만·문지르기 금지. "
        "(3) 식초 1:4 장침지 15–30분. (4) 흰/면 산소(테스트)·실크·울 금지. "
        "(5) 세탁. (6) 건조 전 강광. 유색은 산소 신중·잔색·100% 비보장 고지."
    ),
    "S_SOFT_DRINK": (
        "(1) 마른 당분·콜라·탄산. (2) 미온 장침지. (3) 식초 1:4 15–30분. "
        "(4) 흰옷 산소(테스트). (5) 세탁. (6) 끈적임 없앤 뒤만 건조·강광. "
        "당분 황변·100% 비보장 고지."
    ),
    "S_SOY_SAUCE": (
        "(1) 마른 간장. (2) 찬물. (3) 효소 장침지 30–45분. "
        "(4) 식초 1:4. (5) 흰/면 산소(테스트). (6) 세탁·강광. "
        "갈색 잔색·100% 비보장 고지."
    ),
    "S_FISH_SAUCE": (
        "(1) 마른 느억맘·액젓. (2) 찬물. (3) 효소 장침지 30–45분. "
        "(4) 주방세제(유분)→식초 1:4(냄새). (5) 흰/면 산소(테스트). "
        "(6) 세탁·강광. 냄새·잔색 가능 — 100% 비보장."
    ),
    "S_SWEAT_FRESH": (
        "(1) 마른 땀 잔여. (2) 찬물. (3) 효소 장침지 30–45분. "
        "(4) 식초 1:4. (5) 세탁. (6) 황변 보이면 겨드랑이 황변 경로·강광. "
        "열고착 잔여 고지."
    ),
    "S_MAYO": (
        "(1) 마른 마요네즈. (2) 긁기. (3) 주방세제(기름 먼저) Cap2. "
        "(4) 효소(단백질) 장침지 30–45분. (5) 세탁. "
        "(6) 미끄럼 확인 후 건조. 순서 바꾸지 말 것·100% 비보장."
    ),
    "S_BBQ_SAUCE": (
        "(1) 마른 BBQ·당분 소스. (2) 긁기·찬물. (3) 효소 장침지 30–45분. "
        "(4) 주방세제→식초 1:4. (5) 흰옷 산소(테스트). "
        "(6) 세탁·강광. 마른 당분 황변·100% 비보장 고지."
    ),
    "S_GRASS": (
        "(1) 마른 잔디·엽록소. (2) 안쪽 알코올 블롯 다회(문지르기 금지). "
        "(3) 효소 장침지. (4) 흰옷 산소(테스트). (5) 세탁. "
        "(6) 건조 전 강광. 고착 초록 잔색·100% 비보장 고지."
    ),
    "S_CHOCOLATE": (
        "(1) 마른 초콜릿. (2) 긁기. (3) 찬물→효소 장침지 30–45분. "
        "(4) 주방세제(유지방). (5) 흰옷 산소(테스트). "
        "(6) 세탁·강광. 잔색·100% 비보장 고지."
    ),
    "S_CURRY": (
        "(1) 마른 카레·강황. (2) 긁기. (3) 주방세제 Cap2. "
        "(4) 베이킹소다. (5) 흰옷 산소/짧은 UV(테스트). "
        "(6) 세탁·강광. 강황 잔색·100% 비보장 고지."
    ),
    "S_SUNSCREEN": (
        "(1) 마른 선크림(오일·실리콘). (2) 전분 흡착. "
        "(3) 주방세제 Cap2 반복 탈지 15–30분. (4) 세탁. "
        "(5) 강광. (6) 이미 락스면 황변 영구 가능·미끄럼 채 건조 금지 고지."
    ),
    "S_TAR": (
        "(1) 마른 타르. (2) 흡착. (3) 용제 다회(환기·구석 테스트·문지르기 금지). "
        "(4) 주방세제. (5) 실크·울 Cap1/전문. "
        "(6) 세탁·강광. 100% 비보장 고지."
    ),
    "S_ENGINE_OIL": (
        "(1) 마른 엔진오일. (2) 흡착 2회. (3) 용제 다회(환기·테스트). "
        "(4) 주방세제 Cap2. (5) 세탁. "
        "(6) 미끄럼·냄새 확인 후 건조. 성공률↓·100% 비보장 고지."
    ),
    "S_PERFUME": (
        "(1) 마른 향수 산화 황변. (2) 식초 1:4 장침지 15–30분. "
        "(3) 흰옷 산소(테스트). (4) 세탁. (5) 강광. "
        "(6) 오래된 산화 황변 100% 비보장 고지."
    ),
    "S_GAC": (
        "(1) 마른 꼭(gấc)·주황 색소. (2) 긁기·찬물. (3) 주방세제 Cap2. "
        "(4) 알코올 블롯(테스트). (5) 흰/면 산소·햇빛. "
        "(6) 세탁·강광. 주황 잔색·100% 비보장 고지."
    ),
    "S_ANNATTO": (
        "(1) 마른 아나토·황/주황 색소. (2) 찬물·문지르기 금지. "
        "(3) 알코올 블롯 다회(테스트). (4) 흰/면 산소. "
        "(5) 세탁. (6) 강광. 황·주황 잔색·100% 비보장 고지."
    ),
    "S_STARCH_TRANSFER": (
        "(1) 마른 전분·풀 이염. (2) 찬물. (3) 아밀라아제/효소 장침지 30–45분. "
        "(4) 흰옷 산소(테스트). (5) 세탁. "
        "(6) 강광. 잔색 채 다림질 금지·100% 비보장 고지."
    ),
}

DRIED_PATH_VI_V11: dict[str, str] = {
    "S_DOENJANG": (
        "(1) Tương đậu/doenjang khô. (2) Cạo Cap1 + xả lạnh — CẤM chà. "
        "(3) Nước rửa chén Cap2. (4) Enzyme ngâm 30–60 phút. "
        "(5) Oxy trắng/cotton (test) — CẤM lụa/len. "
        "(6) Giặt + ánh sáng. Báo nâu còn — không 100%."
    ),
    "S_GOCHUJANG": (
        "(1) Gochujang khô. (2) Cạo + lạnh. (3) Nước rửa chén Cap2. "
        "(4) Giấm 1:4 ngâm 15–30 phút lặp. (5) Oxy trắng/cotton (test). "
        "(6) Giặt + ánh sáng. Báo đỏ ớt còn — không 100%."
    ),
    "S_PERSIMMON": (
        "(1) Hồng/tanin đã nâu — có thể khóa. (2) Chỉ lạnh — CẤM chà. "
        "(3) Giấm 1:4 ngâm 15–30 phút lặp. (4) Oxy trắng/cotton (test). "
        "(5) Giặt. (6) Ánh sáng. Báo nâu khóa — không 100%."
    ),
    "S_CRAYON": (
        "(1) Sáp màu cứng (wax+pigment). (2) Làm lạnh/đông rồi bẻ·cạo. "
        "(3) Giấy thấm + ủi thấp chuyển sáp (lặp — CẤM ủi nóng trên vết). "
        "(4) Nước rửa chén. (5) Oxy trắng/cotton (test). "
        "(6) Giặt + ánh sáng. Báo màu còn — không 100%."
    ),
    "S_SOFTENER_SPOT": (
        "(1) Vòng softener đã khô/khóa nhiệt. (2) Nước rửa chén Cap2 ngâm 15–30 phút lặp. "
        "(3) Giặt ấm lại. (4) Giấm 1:4 xả phụ nếu cần. "
        "(5) Chỉ sấy khi hết nhờn. (6) Báo giới hạn vòng đã sấy — không 100%."
    ),
    "S_BUTTER": (
        "(1) Bơ khô/nghi khóa nhiệt. (2) Cạo lạnh → bột hút. "
        "(3) Nước rửa chén → lipase nếu cần. (4) Enzyme (vết đạm sữa). "
        "(5) Giặt. (6) Kiểm nhờn rồi mới sấy. Báo khóa nhiệt — không 100%."
    ),
    "S_WHITE_WINE_BEER": (
        "(1) Đã vàng/đường khô (rượu trắng/bia). (2) Lạnh. "
        "(3) Giấm 1:4 ngâm 15–30 phút. (4) Bia: thêm enzyme nếu cần. "
        "(5) Oxy trắng ngắn (test). (6) Giặt + thoáng. Vàng đường cũ: không 100%."
    ),
    "S_PAINT_LATEX": (
        "(1) Sơn nước đã khô. (2) Test góc. "
        "(3) Dung môi nhẹ/cồn blot nhiều (CẤM chà, thông gió). "
        "(4) Nước rửa chén. (5) Giặt. (6) Báo tỷ lệ thấp; nếu sơn dầu → SOP sơn dầu. Không 100%."
    ),
    "S_TOMATO_SAUCE": (
        "(1) Sốt cà/pasta khô. (2) Cạo. (3) Ngâm + nước rửa chén (dầu trước). "
        "(4) Giấm 1:4 ngâm 15–30 phút. (5) Oxy trắng/cotton (test). "
        "(6) Giặt + ánh sáng. Báo lycopene còn — không 100%."
    ),
    "S_GREASE": (
        "(1) Mỡ/grease khô. (2) Bột hút 2 lần. (3) Nước rửa chén / lipase. "
        "(4) Lặp khử dầu. (5) Giặt. (6) Hết nhờn/mùi mới sấy. Mỡ cũ: báo thấp."
    ),
    "S_FRUIT_JUICE": (
        "(1) Nước ép khô/tannin. (2) Chỉ lạnh — CẤM chà. "
        "(3) Giấm 1:4 ngâm 15–30 phút. (4) Oxy trắng/cotton (test) — CẤM lụa/len. "
        "(5) Giặt. (6) Ánh sáng trước sấy. Màu: thận trọng oxy — không 100%."
    ),
    "S_SOFT_DRINK": (
        "(1) Đường khô/cola. (2) Ngâm ấm. (3) Giấm 1:4 15–30 phút. "
        "(4) Oxy trắng (test). (5) Giặt. (6) Hết dính mới sấy + ánh sáng. "
        "Báo vàng đường — không 100%."
    ),
    "S_SOY_SAUCE": (
        "(1) Nước tương khô. (2) Lạnh. (3) Enzyme ngâm 30–45 phút. "
        "(4) Giấm 1:4. (5) Oxy trắng/cotton (test). (6) Giặt + ánh sáng. "
        "Báo nâu còn — không 100%."
    ),
    "S_FISH_SAUCE": (
        "(1) Nước mắm khô. (2) Lạnh. (3) Enzyme ngâm 30–45 phút. "
        "(4) Nước rửa chén → giấm 1:4 (mùi). (5) Oxy trắng/cotton (test). "
        "(6) Giặt + ánh sáng. Báo mùi/màu — không 100%."
    ),
    "S_SWEAT_FRESH": (
        "(1) Mồ hôi khô còn. (2) Lạnh. (3) Enzyme ngâm 30–45 phút. "
        "(4) Giấm 1:4. (5) Giặt. (6) Thấy vàng nách → SOP mồ hôi vàng + ánh sáng."
    ),
    "S_MAYO": (
        "(1) Mayo khô. (2) Cạo. (3) Nước rửa chén (dầu trước) Cap2. "
        "(4) Enzyme (protein) 30–45 phút. (5) Giặt. "
        "(6) Hết nhờn mới sấy. Giữ thứ tự dầu→protein — không 100%."
    ),
    "S_BBQ_SAUCE": (
        "(1) BBQ/đường khô. (2) Cạo + lạnh. (3) Enzyme 30–45 phút. "
        "(4) Nước rửa chén → giấm 1:4. (5) Oxy trắng (test). "
        "(6) Giặt + ánh sáng. Báo vàng đường — không 100%."
    ),
    "S_GRASS": (
        "(1) Cỏ khô/chlorophyll. (2) Blot cồn mặt trái nhiều (CẤM chà). "
        "(3) Enzyme ngâm. (4) Oxy trắng (test). (5) Giặt. "
        "(6) Ánh sáng trước sấy. Báo xanh khóa — không 100%."
    ),
    "S_CHOCOLATE": (
        "(1) Socola khô. (2) Cạo. (3) Lạnh → enzyme 30–45 phút. "
        "(4) Nước rửa chén. (5) Oxy trắng (test). "
        "(6) Giặt + ánh sáng. Báo còn màu — không 100%."
    ),
    "S_CURRY": (
        "(1) Cà ri/nghệ khô. (2) Cạo. (3) Nước rửa chén Cap2. "
        "(4) Baking soda. (5) Oxy trắng/UV ngắn (test). "
        "(6) Giặt + ánh sáng. Báo nghệ còn — không 100%."
    ),
    "S_SUNSCREEN": (
        "(1) Kem chống nắng khô (dầu/silicone). (2) Bột hút. "
        "(3) Nước rửa chén Cap2 lặp 15–30 phút. (4) Giặt. "
        "(5) Ánh sáng. (6) Đã Javel: vàng có thể vĩnh viễn — CẤM sấy khi còn nhờn."
    ),
    "S_TAR": (
        "(1) Nhựa đường khô. (2) Hút. (3) Dung môi lặp (thông gió/test — CẤM chà). "
        "(4) Nước rửa chén. (5) Lụa/len Cap1/chuyên. "
        "(6) Giặt + ánh sáng. Không 100%."
    ),
    "S_ENGINE_OIL": (
        "(1) Dầu động cơ khô. (2) Hút 2 lần. (3) Dung môi lặp (thông gió/test). "
        "(4) Nước rửa chén Cap2. (5) Giặt. "
        "(6) Hết nhờn/mùi mới sấy. Báo thấp — không 100%."
    ),
    "S_PERFUME": (
        "(1) Nước hoa khô — vàng oxy hóa. (2) Giấm 1:4 ngâm 15–30 phút. "
        "(3) Oxy trắng (test). (4) Giặt. (5) Ánh sáng. "
        "(6) Vàng cũ: không 100%."
    ),
    "S_GAC": (
        "(1) Gấc khô — màu cam. (2) Cạo + lạnh. (3) Nước rửa chén Cap2. "
        "(4) Blot cồn (test). (5) Oxy trắng + nắng. "
        "(6) Giặt + ánh sáng. Báo cam còn — không 100%."
    ),
    "S_ANNATTO": (
        "(1) Hạt điều màu khô — vàng/cam. (2) Lạnh — CẤM chà. "
        "(3) Blot cồn nhiều (test). (4) Oxy trắng/cotton. "
        "(5) Giặt. (6) Ánh sáng. Báo vàng/cam còn — không 100%."
    ),
    "S_STARCH_TRANSFER": (
        "(1) Tinh bột/hồ khô. (2) Lạnh. (3) Amylase/enzyme ngâm 30–45 phút. "
        "(4) Oxy trắng (test). (5) Giặt. "
        "(6) Ánh sáng. CẤM ủi khi còn màu — không 100%."
    ),
    "S_KIMCHI": (
        "(1) Kim chi/nước kim chi khô. (2) Cạo + xả lạnh — CẤM chà. "
        "(3) Nước rửa chén (dầu). (4) Giấm 1:4 ngâm 15–30 phút. "
        "(5) Oxy trắng/cotton (test). (6) Giặt + ánh sáng. "
        "Báo màu ớt/mùi còn — không 100%."
    ),
    "S_MOTORBIKE_OIL": (
        "(1) Dầu nhớt xe máy khô. (2) Bột hút 2 lần. "
        "(3) Dung môi (thông gió) / nước rửa chén lặp. (4) Giặt. "
        "(5) Kiểm hết nhờn trước sấy. (6) CẤM nhiệt cao lụa/len. "
        "Báo không 100%."
    ),
}

# Longer soak labels for dried protein-heavy stains (override default 15–30).
LONG_SOAK_STAIN_IDS: frozenset[str] = frozenset({
    "S_BLOOD_DRY",
    "S_BLOOD_FRESH",
    "S_EGG",
    "S_MILK",
    "S_BABY_FORMULA",
    "S_MILK_COFFEE",
    "S_VOMIT",
    "S_URINE",
    "S_FECES",
    "S_COLLAR_STAIN",
    "S_SHIRT_YELLOW",
    "S_SWEAT_YELLOW",
    "S_SWEAT_FRESH",
    "S_DOENJANG",
    "S_SOY_SAUCE",
    "S_FISH_SAUCE",
    "S_SHRIMP_PASTE",
    "S_BUBBLE_TEA",
    "S_CHOCOLATE",
    "S_MAYO",
})

# ── Per-stain 2nd-pass rescue (remaining Protocol IDs) ───────────────────────
RESCUE_BY_STAIN_V11: dict[str, dict[str, str]] = {
    "S_BLACK_COFFEE": {
        "ko": "2차: 식초 1:4 재침지 15–30분 → 흰/면만 산소 → 강광. 탄닌 잔색·100% 불가 고지.",
        "vi": "Lần 2: giấm 1:4 ngâm lại 15–30 → oxy trắng/cotton → ánh sáng. Báo tannin còn, không 100%.",
        "en": "2nd: vinegar 1:4 again 15–30 → oxygen white cotton → light. Disclose tannin residual; no 100%.",
    },
    "S_TEA": {
        "ko": "2차: 식초 장침지 재실시 → 흰/면 산소. 실크·울은 식초 약하게만. 100% 금지.",
        "vi": "Lần 2: giấm ngâm lại → oxy trắng. Lụa/len: giấm nhẹ thôi. CẤM 100%.",
        "en": "2nd: vinegar soak again → oxygen whites. Silk/wool: weak vinegar only. No 100%.",
    },
    "S_FRUIT_JUICE": {
        "ko": "2차: 식초 1:4 재침지 → 흰/면 산소(테스트). 유색·실크 산소 신중. 100% 금지.",
        "vi": "Lần 2: giấm 1:4 lại → oxy trắng (test). Màu/lụa: thận trọng oxy. CẤM 100%.",
        "en": "2nd: vinegar 1:4 again → oxygen white cotton. Careful on dyed/silk. No 100%.",
    },
    "S_SOFT_DRINK": {
        "ko": "2차: 미온·식초로 당분 제거 재실시 → 흰옷 산소. 끈적임 남긴 채 건조 금지.",
        "vi": "Lần 2: ngâm ấm+giấm khử đường lại → oxy trắng. CẤM sấy khi còn dính.",
        "en": "2nd: warm+vinegar for sugar again → oxygen whites. No dry while sticky.",
    },
    "S_WHITE_WINE_BEER": {
        "ko": "2차: 식초 재침지 → 흰옷 짧은 산소. 황변 잔여·100% 불가 고지.",
        "vi": "Lần 2: giấm lại → oxy trắng ngắn. Báo vàng còn — không 100%.",
        "en": "2nd: vinegar again → short oxygen on whites. Disclose yellowing; no 100%.",
    },
    "S_KIMCHI": {
        "ko": "2차: 주방세제→식초→흰/면 산소 1회. 고추 색소·냄새 잔여 고지. 100% 금지.",
        "vi": "Lần 2: D2 → giấm → oxy trắng 1 lần. Báo màu ớt/mùi. CẤM 100%.",
        "en": "2nd: dish→vinegar→oxygen whites once. Disclose chili dye/odor. No 100%.",
    },
    "S_COOKING_OIL": {
        "ko": "2차: 흡착→주방세제/리파아제 반복 → 미끄럼 없어진 뒤만 건조. 열고착 한계 고지.",
        "vi": "Lần 2: hút → D2/lipase lặp → hết nhờn mới sấy. Báo khóa nhiệt.",
        "en": "2nd: absorb→dish/lipase repeats → dry only when not greasy. Disclose heat-set.",
    },
    "S_MILK_COFFEE": {
        "ko": "2차: 효소 장침지 30–45분(또는 주방세제) → 식초 → 허용 시만 산소. 단백질 고착 고지.",
        "vi": "Lần 2: enzyme 30–45 (hoặc D2) → giấm → oxy nếu được. Báo protein khóa.",
        "en": "2nd: enzyme 30–45 (or dish) → vinegar → oxygen if allowed. Disclose set protein.",
    },
    "S_FOUNDATION": {
        "ko": "2차: 긁기+주방세제+알코올 블롯(테스트) → 흰옷 산소. 건조 고착 고지.",
        "vi": "Lần 2: cạo + D2 + blot cồn (test) → oxy trắng. Báo đã khóa khô.",
        "en": "2nd: scrape+dish+alcohol blot (test) → oxygen whites. Disclose dry-set.",
    },
    "S_GREASE": {
        "ko": "2차: 흡착 2회→주방세제/리파아제 반복 → 미끄럼·냄새 확인 후 건조.",
        "vi": "Lần 2: hút 2 lần → D2/lipase lặp → hết nhờn/mùi mới sấy.",
        "en": "2nd: absorb twice → dish/lipase repeats → dry when not greasy/odorous.",
    },
    "S_BUTTER": {
        "ko": "2차: 흡착→주방세제→효소(유단백) 순서 유지. 열고착이면 한계 고지.",
        "vi": "Lần 2: hút → D2 → enzyme (giữ thứ tự). Khóa nhiệt: báo giới hạn.",
        "en": "2nd: absorb→dish→enzyme (keep order). Heat-set: disclose limits.",
    },
    "S_BUBBLE_TEA": {
        "ko": "2차: 효소 장침지→주방세제→식초→흰옷 산소. 마른 설탕 황변 예방·고지.",
        "vi": "Lần 2: enzyme dài → D2 → giấm → oxy trắng. Phòng/báo vàng đường.",
        "en": "2nd: longer enzyme→dish→vinegar→oxygen. Prevent/disclose sugar yellowing.",
    },
    "S_KETCHUP": {
        "ko": "2차: 주방세제→식초 1:4 재침지 → 흰/면 산소. 붉은 잔색·100% 불가 고지.",
        "vi": "Lần 2: D2 → giấm 1:4 lại → oxy trắng. Báo đỏ còn — không 100%.",
        "en": "2nd: dish→vinegar 1:4 again → oxygen whites. Disclose red residual; no 100%.",
    },
    "S_TOMATO_SAUCE": {
        "ko": "2차: 기름(주방세제) 먼저→식초→흰/면 산소. 리코펜 잔색 고지.",
        "vi": "Lần 2: D2 trước → giấm → oxy trắng. Báo lycopene còn.",
        "en": "2nd: dish first → vinegar → oxygen whites. Disclose lycopene residual.",
    },
    "S_MUD": {
        "ko": "2차: 마른 흙 충분히 털기→세탁→흙색이면 식초. 적토면 라테라이트 경로.",
        "vi": "Lần 2: phủi đất khô kỹ → giặt → nếu màu: giấm. Đất đỏ → SOP laterite.",
        "en": "2nd: brush dry mud well → wash → vinegar if tint. Red earth → laterite path.",
    },
    "S_SOY_SAUCE": {
        "ko": "2차: 효소 장침지→식초→흰/면 산소. 갈색 잔색·100% 불가 고지.",
        "vi": "Lần 2: enzyme dài → giấm → oxy trắng. Báo nâu còn — không 100%.",
        "en": "2nd: longer enzyme→vinegar→oxygen whites. Disclose brown residual; no 100%.",
    },
    "S_FISH_SAUCE": {
        "ko": "2차: 효소→주방세제→식초(냄새) 재실시 → 흰/면 산소. 냄새 잔여 고지.",
        "vi": "Lần 2: enzyme → D2 → giấm (mùi) lại → oxy trắng. Báo mùi còn.",
        "en": "2nd: enzyme→dish→vinegar (odor) again → oxygen. Disclose odor residual.",
    },
    "S_EGG": {
        "ko": "2차: 찬물만→효소 30–60분(온수 금지) → 연질 솔. 열 처리 후 성공률↓ 고지.",
        "vi": "Lần 2: chỉ lạnh → enzyme 30–60 (CẤM nóng) → chải mềm. Đã nhiệt: báo thấp.",
        "en": "2nd: cold only→enzyme 30–60 (no hot) → soft brush. After heat: disclose low odds.",
    },
    "S_MILK": {
        "ko": "2차: 찬물→효소 30–45분 → 신내면 식초. 분유 의심 시 분유 경로.",
        "vi": "Lần 2: lạnh → enzyme 30–45 → giấm nếu chua. Nghi sữa bột → SOP công thức.",
        "en": "2nd: cold→enzyme 30–45 → vinegar if sour. Formula suspected → formula path.",
    },
    "S_BABY_FORMULA": {
        "ko": "2차: 효소 30–60분→주방세제→식초(철 잔색). 온수/락스 후 주황 영구 가능 고지.",
        "vi": "Lần 2: enzyme 30–60 → D2 → giấm (sắt). Đã nóng/Javel: có thể cam vĩnh viễn.",
        "en": "2nd: enzyme 30–60→dish→vinegar (iron). Hot/chlorine may permanent orange — disclose.",
    },
    "S_SWEAT_FRESH": {
        "ko": "2차: 효소→식초. 황변 보이면 겨드랑이 황변 경로로 전환.",
        "vi": "Lần 2: enzyme → giấm. Thấy vàng nách → chuyển SOP mồ hôi vàng.",
        "en": "2nd: enzyme→vinegar. If underarm yellow → switch to sweat-yellow path.",
    },
    "S_VOMIT": {
        "ko": "2차: PPE→효소 장침지→식초→흰옷 산소. 담즙 고착 시 성공률↓ 고지.",
        "vi": "Lần 2: PPE → enzyme dài → giấm → oxy trắng. Mật khóa: báo thấp.",
        "en": "2nd: PPE→long enzyme→vinegar→oxygen. Bile set: disclose low odds.",
    },
    "S_URINE": {
        "ko": "2차: 효소 고농도 45–60분→식초 ~30분→흰옷 산소·햇빛. 요산 잔여 고지.",
        "vi": "Lần 2: enzyme đậm 45–60 → giấm ~30 → oxy + nắng. Báo uric còn.",
        "en": "2nd: strong enzyme 45–60→vinegar ~30→oxygen+sun. Disclose uric residual.",
    },
    "S_FECES": {
        "ko": "2차: PPE→효소(가능 시 밤새)→흰 면만 산소/희석 락스(테스트). 담즙 잔색 고지.",
        "vi": "Lần 2: PPE → enzyme dài → oxy/Javel loãng chỉ cotton trắng (test). Báo mật còn.",
        "en": "2nd: PPE→long enzyme→oxygen/dilute chlorine white cotton only. Disclose bile stain.",
    },
    "S_MAYO": {
        "ko": "2차: 기름(주방세제)→단백질(효소) 순서 유지. 미끄럼 확인 후 건조.",
        "vi": "Lần 2: dầu (D2) → protein (enzyme) — giữ thứ tự. Hết nhờn mới sấy.",
        "en": "2nd: oil (dish) then protein (enzyme) — keep order. Dry only when not greasy.",
    },
    "S_BBQ_SAUCE": {
        "ko": "2차: 효소→주방세제→식초→흰옷 산소. 마른 당분 황변 고지.",
        "vi": "Lần 2: enzyme → D2 → giấm → oxy trắng. Báo vàng đường khô.",
        "en": "2nd: enzyme→dish→vinegar→oxygen. Disclose dried-sugar yellowing.",
    },
    "S_COLLAR_STAIN": {
        "ko": "2차: 효소 페이스트/장침지(가능 시 밤새)→흰 면 산소. 잔영·락스 금지 고지.",
        "vi": "Lần 2: enzyme paste/ngâm dài → oxy cotton trắng. Báo bóng còn; CẤM Javel.",
        "en": "2nd: enzyme paste/long soak→oxygen white cotton. Disclose ghosting; no chlorine.",
    },
    "S_SHIRT_YELLOW": {
        "ko": "2차: 효소(밤새 가능)→산소 장침지→흰옷 단독. 오래된 황변 100% 불가. 락스 금지.",
        "vi": "Lần 2: enzyme dài → oxy ngâm → giặt trắng riêng. Vàng cũ: không 100%. CẤM Javel.",
        "en": "2nd: long enzyme→oxygen soak→wash whites alone. Old yellow: no 100%. No chlorine.",
    },
    "S_SWEAT_YELLOW": {
        "ko": "2차: 효소→산소 장침지 1회. 오래된 잔영·락스 남용 금지 고지.",
        "vi": "Lần 2: enzyme → oxy ngâm 1 lần. Báo bóng cũ; CẤM Javel lạm.",
        "en": "2nd: enzyme→oxygen soak once. Disclose old ghosting; no chlorine abuse.",
    },
    "S_GRASS": {
        "ko": "2차: 알코올 블롯 다회→효소→흰옷 산소. 고착 초록 잔색 고지.",
        "vi": "Lần 2: blot cồn lặp → enzyme → oxy trắng. Báo xanh khóa.",
        "en": "2nd: alcohol blot repeats→enzyme→oxygen. Disclose set green residual.",
    },
    "S_CHOCOLATE": {
        "ko": "2차: 긁기→찬물→효소→주방세제→흰옷 산소. 건조 전 강광.",
        "vi": "Lần 2: cạo → lạnh → enzyme → D2 → oxy trắng. Ánh sáng trước sấy.",
        "en": "2nd: scrape→cold→enzyme→dish→oxygen. Strong light before dry.",
    },
    "S_CURRY": {
        "ko": "2차: 주방세제→베이킹소다→흰옷 산소/짧은 UV. 강황 잔색·100% 불가 고지.",
        "vi": "Lần 2: D2 → baking soda → oxy/UV ngắn. Báo nghệ còn — không 100%.",
        "en": "2nd: dish→baking soda→oxygen/short UV. Disclose turmeric residual; no 100%.",
    },
    "S_MUSTARD": {
        "ko": "2차: 긁기→주방세제→베이킹소다→흰옷 산소. 실크 성공률↓ 고지.",
        "vi": "Lần 2: cạo → D2 → baking soda → oxy trắng. Lụa: báo thấp.",
        "en": "2nd: scrape→dish→baking soda→oxygen. Silk: disclose lower odds.",
    },
    "S_DYE_TRANSFER": {
        "ko": "2차: 흰/면만 산소 장침지(테스트). 유색·실크·울: 전문 고려. 100% 불가.",
        "vi": "Lần 2: oxy ngâm chỉ trắng/cotton (test). Màu/lụa/len: chuyên. Không 100%.",
        "en": "2nd: oxygen soak white cotton only. Dyed/silk/wool: refer. No 100%.",
    },
    "S_LATERITE": {
        "ko": "2차: 털기→안전 원단만 X2→즉시 중화. 실크·울: 식초만. 철 잔존 고지.",
        "vi": "Lần 2: phủi → chỉ vải an toàn X2 → trung hòa ngay. Lụa/len: giấm. Báo sắt còn.",
        "en": "2nd: brush→X2 only safe fabrics→neutralize. Silk/wool: vinegar. Disclose iron.",
    },
    "S_GUM": {
        "ko": "2차: 재냉동→깨서 제거→잔여 주방세제/약한 용제(테스트). 다림질 후 더 어려움 고지.",
        "vi": "Lần 2: đông lại → bẻ → D2/dung môi nhẹ (test). Đã ủi: báo khó hơn.",
        "en": "2nd: refreeze→crack off→dish/mild solvent (test). After iron: disclose harder.",
    },
    "S_CANDLE_WAX": {
        "ko": "2차: 흡수지+저온 다리미 반복→잔여 주방세제→색소면 알코올 블롯. 열고착 고지.",
        "vi": "Lần 2: giấy+ủi thấp lặp → D2 → màu: blot cồn. Báo khóa nhiệt.",
        "en": "2nd: blotter+low iron repeats→dish→alcohol for dye. Disclose heat-set.",
    },
    "S_SUNSCREEN": {
        "ko": "2차: 전분 흡착→주방세제 반복. 이미 락스면 황변 영구 가능 고지.",
        "vi": "Lần 2: bột hút → D2 lặp. Đã Javel: có thể vàng vĩnh viễn — báo.",
        "en": "2nd: starch absorb→dish repeats. After chlorine: possible permanent yellow — disclose.",
    },
    "S_TAR": {
        "ko": "2차: 흡착→용제 다회(환기·테스트)→주방세제. 실크·울 Cap1/전문. 100% 금지.",
        "vi": "Lần 2: hút → dung môi lặp (thông gió/test) → D2. Lụa/len Cap1/chuyên. CẤM 100%.",
        "en": "2nd: absorb→solvent repeats (vent/test)→dish. Silk/wool Cap1/refer. No 100%.",
    },
    "S_ENGINE_OIL": {
        "ko": "2차: 흡착→용제(환기) 다회→주방세제. 미끄럼·냄새 확인. 성공률↓ 고지.",
        "vi": "Lần 2: hút → dung môi (thông gió) lặp → D2. Kiểm nhờn/mùi. Báo thấp.",
        "en": "2nd: absorb→solvent (vent) repeats→dish. Check grease/odor. Disclose low odds.",
    },
    "S_DEODORANT": {
        "ko": "2차: 식초 1:4 재침지→흰옷 산소(테스트). 이미 락스면 황변 영구 가능 고지.",
        "vi": "Lần 2: giấm 1:4 lại → oxy trắng (test). Đã Javel: vàng có thể vĩnh viễn.",
        "en": "2nd: vinegar 1:4 again→oxygen whites. After chlorine: possible permanent yellow.",
    },
    "S_PERFUME": {
        "ko": "2차: 식초→흰옷 산소. 오래된 산화 황변 100% 불가 고지.",
        "vi": "Lần 2: giấm → oxy trắng. Vàng oxy hóa cũ: không 100%.",
        "en": "2nd: vinegar→oxygen whites. Old oxidation yellow: no 100%.",
    },
    "S_MASCARA": {
        "ko": "2차: 안쪽 블롯→약한 리무버/알코올(테스트)→주방세제. 탄소 100% 불가 고지.",
        "vi": "Lần 2: blot mặt trái → remover/cồn nhẹ (test) → D2. Carbon: không 100%.",
        "en": "2nd: reverse blot→mild remover/alcohol (test)→dish. Carbon: no 100%.",
    },
    "S_HAIR_DYE": {
        "ko": "2차: 알코올 블롯→흰옷 산소 반복. 실크/울 신중·100% 불가 고지.",
        "vi": "Lần 2: blot cồn → oxy trắng lặp. Lụa/len thận trọng — không 100%.",
        "en": "2nd: alcohol blot→oxygen whites repeats. Careful silk/wool; no 100%.",
    },
    "S_SHOE_POLISH": {
        "ko": "2차: 흡착→용제 블롯(환기·테스트)→주방세제. 색소 100% 불가. 얇은 원단 테스트.",
        "vi": "Lần 2: hút → blot dung môi (thông gió/test) → D2. Màu không 100%. Test vải mỏng.",
        "en": "2nd: absorb→solvent blot (vent/test)→dish. Dye no 100%. Test thin fabrics.",
    },
    "S_PAINT_LATEX": {
        "ko": "2차: 약한 용제 블롯 1회만 추가(테스트)→주방세제. 실패 시 전문. 유성이면 유성 경로.",
        "vi": "Lần 2: thêm 1 blot dung môi nhẹ (test) → D2. Fail → chuyên. Sơn dầu → SOP dầu.",
        "en": "2nd: one more mild solvent blot (test)→dish. Fail→refer. Oil paint→oil path.",
    },
    "S_GLUE": {
        "ko": "2차: 종류별 용제 구석 테스트 후 1회만→블롯만. 얇은 원단 찢김·100% 불가 고지.",
        "vi": "Lần 2: dung môi đúng loại sau test 1 lần → chỉ blot. Vải mỏng rách — không 100%.",
        "en": "2nd: correct solvent once after test→blot only. Thin fabric tear risk; no 100%.",
    },
    "S_STARCH_TRANSFER": {
        "ko": "2차: 찬물→아밀라아제/효소 장침지→흰옷 산소. 잔색 채 다림질 금지.",
        "vi": "Lần 2: lạnh → amylase/enzyme dài → oxy trắng. CẤM ủi khi còn màu.",
        "en": "2nd: cold→amylase/enzyme soak→oxygen. No iron while color remains.",
    },
    "S_DOENJANG": {
        "ko": "2차: 주방세제→효소 장침지 30–60분→흰/면 산소. 갈색 잔갈·100% 불가 고지.",
        "vi": "Lần 2: D2 → enzyme 30–60 → oxy trắng. Báo nâu còn — không 100%.",
        "en": "2nd: dish→enzyme 30–60→oxygen whites. Disclose brown residual; no 100%.",
    },
    "S_GOCHUJANG": {
        "ko": "2차: 주방세제→식초 장침지→흰/면 산소. 적갈 잔여·100% 불가 고지.",
        "vi": "Lần 2: D2 → giấm dài → oxy trắng. Báo đỏ còn — không 100%.",
        "en": "2nd: dish→vinegar soak→oxygen. Disclose red residual; no 100%.",
    },
    "S_PERSIMMON": {
        "ko": "2차: 식초 1:4 장침지 반복→흰/면 산소. 갈변 고착·100% 불가 고지.",
        "vi": "Lần 2: giấm 1:4 ngâm lặp → oxy trắng. Nâu khóa — không 100%.",
        "en": "2nd: vinegar 1:4 soak repeats→oxygen. Brown set — no 100%.",
    },
    "S_CRAYON": {
        "ko": "2차: 동결·흡수지+저온 다리미 반복→주방세제→흰면 산소. 안료 잔여 고지.",
        "vi": "Lần 2: đông + giấy/ủi thấp lặp → D2 → oxy trắng. Báo pigment còn.",
        "en": "2nd: freeze+blotter/low iron repeats→dish→oxygen. Disclose pigment residual.",
    },
    "S_SOFTENER_SPOT": {
        "ko": "2차: 주방세제 담금·탈지 반복→재세탁. 미끄럼 남은 채 건조 금지·한계 고지.",
        "vi": "Lần 2: D2 ngâm/khử dầu lặp → giặt lại. CẤM sấy khi còn nhờn — báo giới hạn.",
        "en": "2nd: dish soak/degrease repeats→rewash. No dry while greasy; disclose limits.",
    },
}


def soak_minutes_for_stain(stain_id: str) -> tuple[int, int]:
    """Return (lo, hi) soak minutes for dried/hard buckets."""
    if stain_id in LONG_SOAK_STAIN_IDS:
        return 30, 60
    return 15, 30


def merge_dried_paths(ko: dict[str, str], vi: dict[str, str]) -> None:
    """In-place update of runtime DRIED_PATH maps."""
    ko.update(DRIED_PATH_KO_V11)
    vi.update(DRIED_PATH_VI_V11)


def rescue_for_stain(stain_id: str) -> dict[str, str] | None:
    return RESCUE_BY_STAIN_V11.get(stain_id)
