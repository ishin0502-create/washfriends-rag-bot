# -*- coding: utf-8 -*-
"""Education parity v5: dried paths for remaining stains, per-stain rescue, VI ops canon,
acetate/nylon/blend fabric cards, VN specialty stains (oil paint, betel).
"""
from __future__ import annotations

# ── Dried paths (step-level) for stains that lacked DRIED_PATH_* ─────────────
EXTRA_DRIED_PATH_KO: dict[str, str] = {
    "S_BABY_FORMULA": (
        "(1) 마른 분유·철분 확인. (2) 찬물. (3) 효소 장침지 30–60분. (4) 주방세제(지방). "
        "(5) 식초 1:4(철·잔색). (6) 세탁·강광. 락스 금지. 온수/락스 후 주황 영구 가능 고지."
    ),
    "S_BLOOD_DRY": (
        "(1) 마른 핏가루 Cap1 제거. (2) 찬물 침지 30–60분. (3) 효소 30–60분→연질 솔. "
        "(4) 흰 면: 과산화수소 3% 10분(테스트). (5) 실크·울: 소금+중성, 효소/산소 금지. "
        "(6) 건조 전 강광. 갈색 잔존 가능 고지."
    ),
    "S_BLOOD_FRESH": (
        "(1) 이미 마르면 마른 피 경로. (2) 아직 축축: 안쪽 찬물만. (3) 소금물 15–30분. "
        "(4) 효소(실크·울 금지). (5) 찬물 세탁. (6) 강광. 온수·건조 금지."
    ),
    "S_CANDLE_WAX": (
        "(1) 마른 왁스 확인. (2) 굳힌 뒤 긁기. (3) 흡수지+저온 다리미로 왁스 이전(반복). "
        "(4) 잔여 오일: 주방세제. (5) 색소 잔색: 알코올 블롯(테스트). (6) 세탁·강광. "
        "열고착 색소 성공률↓ 고지."
    ),
    "S_COLLAR_STAIN": (
        "(1) 마른 깃·목때. (2) 효소 페이스트/장침지(가능 시 밤새). (3) 흰 면: 산소 침지. "
        "(4) 세탁. (5) 강광. (6) 잔영 가능 고지. 락스·잔여 다림질 금지."
    ),
    "S_DEODORANT": (
        "(1) 마른 데오/알루미늄 자국. (2) 식초 1:4 장침지 15–30분. (3) 헹굼. "
        "(4) 흰옷 산소(테스트). (5) 세탁. (6) 강광. 이미 락스면 황변 영구 가능 고지."
    ),
    "S_DYE_TRANSFER": (
        "(1) 이미 이염·건조. (2) 성공률 낮음 고지. (3) 흰/면만 산소 장침지(테스트). "
        "(4) 유색·실크·울: 염소 금지·전문 고려. (5) 세탁. (6) 강광. 100% 비보장."
    ),
    "S_EGG": (
        "(1) 마른 계란 단백질. (2) 찬물(온수 금지). (3) 효소 장침지 30–60분. "
        "(4) 연질 솔. (5) 세탁. (6) 강광. 열 처리 후 성공률↓ 고지."
    ),
    "S_FECES": (
        "(1) PPE·마른 고형 제거. (2) 찬물. (3) 효소 장침지(가능 시 밤새). "
        "(4) 흰 면: 단백질 후 산소/희석 락스(테스트). (5) 세탁. (6) 강광. 담즙 잔색 가능 고지."
    ),
    "S_FOUNDATION": (
        "(1) 마른 파운데이션(실리콘·오일·색소). (2) 긁기. (3) 주방세제 침지. "
        "(4) 알코올 블롯(테스트). (5) 흰옷 산소. (6) 세탁·강광. 건조 고착 고지."
    ),
    "S_GLUE": (
        "(1) 마른 접착제 종류 확인. (2) 구석 테스트. (3) 종류별 용제·시간(환기). "
        "(4) 블롯만·문지르기 금지. (5) 중성 세탁. (6) 얇은 원단 찢김·100% 비보장 고지."
    ),
    "S_GRASS": (
        "(1) 마른 잔디·엽록소. (2) 알코올 블롯 다회. (3) 효소. (4) 흰옷 산소. "
        "(5) 세탁. (6) 강광. 고착 초록 잔색 고지."
    ),
    "S_GUM": (
        "(1) 마른·붙은 껌. (2) 재냉동/얼음. (3) 깨서 제거. (4) 잔여: 주방세제/약한 용제(테스트). "
        "(5) 세탁. (6) 이미 다림질이면 더 어려움 — 고지."
    ),
    "S_HAIR_DYE": (
        "(1) 마른 염모제 색소. (2) 알코올 블롯(테스트). (3) 흰옷 산소 반복. "
        "(4) 세탁. (5) 강광. (6) 100% 비보장·실크/울 신중."
    ),
    "S_INK_PEN": (
        "(1) 마른 볼펜. (2) 안쪽 알코올 블롯 다회(문지르기 금지). (3) 새 흰 천 교체. "
        "(4) 흰옷 산소. (5) 세탁. (6) 건조·다림질 후 성공률↓ 고지."
    ),
    "S_INK_PERMANENT": (
        "(1) 유성·퍼머넌트 잉크. (2) 아세톤/알코올 구석 테스트. (3) 블롯 다회(환기). "
        "(4) 실패 시 중단. (5) 세탁. (6) 전문/잔여 수용 고지. 100% 비보장."
    ),
    "S_LATERITE": (
        "(1) 마른 적토·철. (2) 털기. (3) 안전 원단만 X2→즉시 중화. (4) 실크·울: 식초 약하게. "
        "(5) 세탁. (6) 이미 세탁·건조: 성공률↓·철 잔존 고지."
    ),
    "S_LIPSTICK": (
        "(1) 마른 립스틱. (2) 긁기. (3) 알코올 블롯. (4) 주방세제. (5) 흰옷 산소. "
        "(6) 세탁·강광. 다림질 고착·실크/울은 전문 고려."
    ),
    "S_MASCARA": (
        "(1) 마른 마스카라. (2) 안쪽 블롯. (3) 약한 리무버/알코올(테스트). "
        "(4) 주방세제. (5) 세탁. (6) 탄소 100% 제거 비보장."
    ),
    "S_MILDEW": (
        "(1) 마른 곰팡이·PPE. (2) 실외 브러시. (3) 식초 1:4. (4) 흰/면 산소. "
        "(5) 세탁·햇빛. (6) 심함·가죽·실크·울은 전문/신중. 100% 비보장."
    ),
    "S_MILK": (
        "(1) 마른 우유 단백질. (2) 찬물. (3) 효소 장침지 30–45분. (4) 신내 있으면 식초 1:4. "
        "(5) 세탁. (6) 강광. 분유 의심→분유 경로."
    ),
    "S_MUD": (
        "(1) 마른 흙. (2) 충분히 털기·솔(젖은 채 문지르기 금지). (3) 세탁. "
        "(4) 흙색: 식초 1:4. (5) 붉은 적토→라테라이트 경로. (6) 강광."
    ),
    "S_MUSTARD": (
        "(1) 마른 머스터드·강황. (2) 긁기. (3) 주방세제. (4) 베이킹소다. "
        "(5) 흰옷 산소/짧은 UV. (6) 세탁·강광. 실크 성공률↓ 고지."
    ),
    "S_NAIL_POLISH": (
        "(1) 마른 매니큐어. (2) 아세톤 구석 테스트. (3) 블롯 다회(환기). "
        "(4) 아세테이트면 즉시 중단·전문. (5) 세탁. (6) 100% 비보장."
    ),
    "S_PERFUME": (
        "(1) 마른 향수 산화 황변. (2) 식초 1:4. (3) 흰옷 산소. (4) 세탁. "
        "(5) 강광. (6) 오래된 산화 황변 100% 비보장."
    ),
    "S_RUST": (
        "(1) 마른 녹·철. (2) 면 등 안전 원단: X2→즉시 중화. (3) 실크·울: 식초 약하게만. "
        "(4) 헹굼. (5) 세탁. (6) 철 잔존·성공률↓ 고지. 장갑."
    ),
    "S_SHIRT_YELLOW": (
        "(1) 마른 셔츠 황변. (2) 효소(가능 시 밤새). (3) 산소 장침지. (4) 흰옷 단독 세탁. "
        "(5) 강광. (6) 오래된 황변 100% 비보장. 락스로 해결 금지."
    ),
    "S_SHOE_POLISH": (
        "(1) 마른 구두약. (2) 흡착. (3) 용제 블롯(환기·테스트). (4) 주방세제. "
        "(5) 세탁. (6) 색소 100% 비보장. 얇은 원단 테스트."
    ),
    "S_STARCH_TRANSFER": (
        "(1) 마른 전분·풀 이염. (2) 찬물. (3) 아밀라아제/효소 장침지. (4) 흰옷 산소. "
        "(5) 세탁. (6) 잔색 채 다림질 금지."
    ),
    "S_SUNSCREEN": (
        "(1) 마른 선크림. (2) 전분 흡착. (3) 주방세제 반복. (4) 세탁. "
        "(5) 강광. (6) 이미 락스면 황변 영구 가능 고지."
    ),
    "S_SWEAT_FRESH": (
        "(1) 마른 땀 잔여. (2) 효소 장침지. (3) 식초 1:4. (4) 세탁. "
        "(5) 황변 보이면 겨드랑이 황변 경로. (6) 강광."
    ),
    "S_SWEAT_YELLOW": (
        "(1) 마른 겨드랑이 황변. (2) 효소(가능 시 밤새). (3) 산소 장침지. "
        "(4) 세탁. (5) 강광. (6) 오래된 잔영 가능 고지. 락스 남용 금지."
    ),
    "S_TAR": (
        "(1) 마른 타르. (2) 흡착. (3) 용제 다회(환기·테스트). (4) 주방세제. "
        "(5) 실크·울 Cap1/전문. (6) 100% 비보장."
    ),
    "S_URINE": (
        "(1) 마른 소변·요산. (2) 찬물 15분. (3) 효소 고농도 45–60분. "
        "(4) 식초 1:4 ~30분. (5) 선택 베이킹소다→세탁+흰옷 산소. (6) 햇빛. 매트리스는 국소만."
    ),
    "S_VOMIT": (
        "(1) 마른 구토물. (2) PPE·고형 제거. (3) 찬물. (4) 효소(가능 시 밤새)→식초. "
        "(5) 흰옷 산소. (6) 세탁·강광. 담즙 고착 시 성공률↓ 고지."
    ),
    "S_PAINT_OIL": (
        "(1) 유성 페인트 마른 막. (2) 구석 테스트 후 페인트 시너/미네랄스피릿(환기·PPE). "
        "(3) 블롯 다회 — 문지르기 금지. (4) 주방세제. (5) 세탁. "
        "(6) 실크·울·아세테이트: 중단·전문. 100% 비보장."
    ),
    "S_BETEL": (
        "(1) 마른 빈랑·적갈색 탄닌/색소. (2) 찬물·문지르기 금지. "
        "(3) 식초 1:4 장침지 15–30분. (4) 흰/면 산소(테스트). (5) 세탁. "
        "(6) 강광. 고착 적갈 100% 비보장."
    ),
}

EXTRA_DRIED_PATH_VI: dict[str, str] = {
    "S_BABY_FORMULA": (
        "(1) Sữa công thức khô/sắt. (2) Xả lạnh. (3) Enzyme ngâm 30–60 phút. "
        "(4) Nước rửa chén. (5) Giấm 1:4. (6) Giặt + ánh sáng. CẤM Javel. "
        "Đã nóng/Javel: có thể vàng cam vĩnh viễn — báo."
    ),
    "S_BLOOD_DRY": (
        "(1) Máu khô: phủi bột Cap1. (2) Ngâm lạnh 30–60 phút. (3) Enzyme 30–60 phút → chải mềm. "
        "(4) Cotton trắng: H₂O₂ 3% 10 phút (test). (5) Lụa/len: muối + trung tính, CẤM enzyme/oxy. "
        "(6) Ánh sáng trước sấy. Báo vết nâu có thể còn."
    ),
    "S_BLOOD_FRESH": (
        "(1) Đã khô → theo máu khô. (2) Còn ẩm: chỉ xả lạnh mặt trái. (3) Nước muối 15–30 phút. "
        "(4) Enzyme (CẤM lụa/len). (5) Giặt lạnh. (6) Ánh sáng. CẤM nóng/sấy."
    ),
    "S_CANDLE_WAX": (
        "(1) Sáp nến khô. (2) Cạo. (3) Giấy thấm + ủi thấp chuyển sáp (lặp). "
        "(4) Dầu còn: nước rửa chén. (5) Màu: blot cồn (test). (6) Giặt. "
        "Báo tỷ lệ thấp nếu màu đã nhiệt."
    ),
    "S_COLLAR_STAIN": (
        "(1) Cổ áo khô. (2) Enzyme paste/ngâm dài. (3) Trắng: oxy. (4) Giặt. "
        "(5) Ánh sáng. (6) Báo bóng mờ có thể còn. CẤM Javel/ủi khi còn."
    ),
    "S_DEODORANT": (
        "(1) Vệt khử mùi khô. (2) Giấm 1:4 ngâm 15–30 phút. (3) Xả. "
        "(4) Oxy trắng. (5) Giặt. (6) Đã Javel: vàng có thể vĩnh viễn — báo."
    ),
    "S_DYE_TRANSFER": (
        "(1) Loang màu đã khô. (2) Báo tỷ lệ thấp. (3) Chỉ trắng/cotton: oxy dài (test). "
        "(4) Màu/lụa/len: CẤM clo — cân nhắc chuyên. (5) Giặt. (6) Không 100%."
    ),
    "S_EGG": (
        "(1) Trứng khô (protein). (2) Lạnh — CẤM nóng. (3) Enzyme 30–60 phút. "
        "(4) Chải mềm. (5) Giặt. (6) Đã nhiệt: báo thấp."
    ),
    "S_FECES": (
        "(1) PPE + cạo khô. (2) Lạnh. (3) Enzyme dài. "
        "(4) Trắng: oxy/Javel loãng sau protein (test). (5) Giặt. (6) Báo màu mật có thể còn."
    ),
    "S_FOUNDATION": (
        "(1) Kem nền khô. (2) Cạo. (3) Ngâm nước rửa chén. (4) Blot cồn (test). "
        "(5) Oxy trắng. (6) Giặt. Báo nếu đã khô cứng."
    ),
    "S_GLUE": (
        "(1) Keo khô — xác định loại. (2) Test góc. (3) Dung môi theo loại (thông gió). "
        "(4) Chỉ blot — CẤM chà. (5) Giặt trung tính. (6) Báo rách vải mỏng / không 100%."
    ),
    "S_GRASS": (
        "(1) Cỏ khô. (2) Blot cồn nhiều lần. (3) Enzyme. (4) Oxy trắng. "
        "(5) Giặt. (6) Báo xanh còn."
    ),
    "S_GUM": (
        "(1) Kẹo cao su dính. (2) Đá lạnh. (3) Bẻ lấy. "
        "(4) Dư: nước rửa chén/dung môi nhẹ. (5) Giặt. (6) Đã ủi: khó hơn — báo."
    ),
    "S_HAIR_DYE": (
        "(1) Thuốc nhuộm khô. (2) Blot cồn (test). (3) Oxy trắng lặp. "
        "(4) Giặt. (5) Ánh sáng. (6) Không 100%; lụa/len thận trọng."
    ),
    "S_INK_PEN": (
        "(1) Mực bút bi khô. (2) Blot cồn mặt trái nhiều lần — CẤM chà. "
        "(3) Đổi khăn trắng. (4) Oxy trắng. (5) Giặt. (6) Đã sấy/ủi: báo thấp."
    ),
    "S_INK_PERMANENT": (
        "(1) Mực dầu/permanent. (2) Test acetone/cồn. (3) Blot nhiều (thông gió). "
        "(4) Fail → dừng. (5) Giặt. (6) Chuyên/chấp nhận dư. Không 100%."
    ),
    "S_LATERITE": (
        "(1) Đất đỏ/sắt khô. (2) Phủi. (3) Chỉ vải an toàn: X2 → trung hòa ngay. "
        "(4) Lụa/len: giấm nhẹ. (5) Giặt. (6) Đã giặt-sấy: báo thấp / sắt còn."
    ),
    "S_LIPSTICK": (
        "(1) Son khô. (2) Cạo. (3) Blot cồn. (4) Nước rửa chén. (5) Oxy trắng. "
        "(6) Giặt. Đã ủi / lụa-len: cân nhắc chuyên."
    ),
    "S_MASCARA": (
        "(1) Mascara khô. (2) Blot mặt trái. (3) Tẩy trang/cồn nhẹ (test). "
        "(4) Nước rửa chén. (5) Giặt. (6) Carbon không 100%."
    ),
    "S_MILDEW": (
        "(1) Mốc khô + PPE. (2) Chải ngoài trời. (3) Giấm 1:4. (4) Oxy trắng/cotton. "
        "(5) Giặt + nắng. (6) Nặng / da / lụa / len: chuyên. Không 100%."
    ),
    "S_MILK": (
        "(1) Sữa khô. (2) Lạnh. (3) Enzyme 30–45 phút. (4) Có mùi chua: giấm 1:4. "
        "(5) Giặt. (6) Nghi sữa bột → SOP sữa công thức."
    ),
    "S_MUD": (
        "(1) Bùn khô. (2) Phủi/chải — CẤM chà khi ướt. (3) Giặt. "
        "(4) Màu đất: giấm 1:4. (5) Đỏ laterite → SOP laterite. (6) Ánh sáng."
    ),
    "S_MUSTARD": (
        "(1) Mù tạt/nghệ khô. (2) Cạo. (3) Nước rửa chén. (4) Baking soda. "
        "(5) Oxy/UV ngắn trắng. (6) Giặt. Lụa: báo thấp."
    ),
    "S_NAIL_POLISH": (
        "(1) Sơn móng khô. (2) Test acetone. (3) Blot nhiều (thông gió). "
        "(4) Acetate/triacetate: DỪNG + chuyên. (5) Giặt. (6) Không 100%."
    ),
    "S_PERFUME": (
        "(1) Nước hoa vàng oxy hóa. (2) Giấm 1:4. (3) Oxy trắng. (4) Giặt. "
        "(5) Ánh sáng. (6) Vàng cũ không 100%."
    ),
    "S_RUST": (
        "(1) Gỉ sắt khô. (2) Cotton an toàn: X2 → trung hòa ngay. "
        "(3) Lụa/len: chỉ giấm nhẹ. (4) Xả. (5) Giặt. (6) Báo sắt còn. Găng tay."
    ),
    "S_SHIRT_YELLOW": (
        "(1) Áo sơ mi vàng khô. (2) Enzyme dài. (3) Oxy dài. (4) Giặt riêng trắng. "
        "(5) Ánh sáng. (6) Vàng cũ không 100%. CẤM Javel \"chữa\"."
    ),
    "S_SHOE_POLISH": (
        "(1) Xi đánh giày khô. (2) Hút. (3) Blot dung môi (thông gió/test). "
        "(4) Nước rửa chén. (5) Giặt. (6) Màu không 100%. Test vải mỏng."
    ),
    "S_STARCH_TRANSFER": (
        "(1) Hồ tinh bột lo màu khô. (2) Lạnh. (3) Enzyme tinh bột dài. "
        "(4) Oxy trắng. (5) Giặt. (6) CẤM ủi khi còn màu."
    ),
    "S_SUNSCREEN": (
        "(1) Kem chống nắng khô. (2) Bột hút. (3) Nước rửa chén lặp. (4) Giặt. "
        "(5) Ánh sáng. (6) Đã Javel: vàng có thể vĩnh viễn."
    ),
    "S_SWEAT_FRESH": (
        "(1) Mồ hôi khô. (2) Enzyme. (3) Giấm 1:4. (4) Giặt. "
        "(5) Thấy vàng → SOP nách vàng. (6) Ánh sáng."
    ),
    "S_SWEAT_YELLOW": (
        "(1) Nách vàng khô. (2) Enzyme dài. (3) Oxy dài. (4) Giặt. "
        "(5) Ánh sáng. (6) Bóng cũ có thể còn. CẤM lạm Javel."
    ),
    "S_TAR": (
        "(1) Nhựa đường khô. (2) Hút. (3) Dung môi nhiều lần (thông gió/test). "
        "(4) Nước rửa chén. (5) Lụa/len Cap1/chuyên. (6) Không 100%."
    ),
    "S_URINE": (
        "(1) Nước tiểu khô/uric. (2) Lạnh 15 phút. (3) Enzyme đậm 45–60 phút. "
        "(4) Giấm 1:4 ~30 phút. (5) Baking soda tùy chọn → giặt + oxy trắng. "
        "(6) Nắng. Nệm: chỉ cục bộ."
    ),
    "S_VOMIT": (
        "(1) Chất nôn khô. (2) PPE + cạo. (3) Lạnh. (4) Enzyme dài → giấm. "
        "(5) Oxy trắng. (6) Giặt. Mật khô: báo thấp."
    ),
    "S_PAINT_OIL": (
        "(1) Sơn dầu khô. (2) Test góc → dung môi sơn/mineral spirit (thông gió + PPE). "
        "(3) Blot nhiều — CẤM chà. (4) Nước rửa chén. (5) Giặt. "
        "(6) Lụa/len/acetate: dừng + chuyên. Không 100%."
    ),
    "S_BETEL": (
        "(1) Trầu/cau khô — tannin đỏ nâu. (2) Lạnh — CẤM chà. "
        "(3) Giấm 1:4 ngâm 15–30 phút. (4) Oxy trắng/cotton (test). (5) Giặt. "
        "(6) Ánh sáng. Đỏ nâu cố định: không 100%."
    ),
}

# Upgrade existing priority dried VI (ASCII) to diacritic forms where still unsigned-looking.
CANON_DRIED_PATH_VI: dict[str, str] = {
    "S_RED_WINE": (
        "(1) Vết rượu đỏ đã khô. (2) Chỉ xả lạnh — không chà. (3) Giấm 1:4 ngâm 15–30 phút. "
        "(4) Trắng/cotton: oxy (test). CẤM oxy lên len/lụa. (5) Giặt. (6) Ánh sáng trước sấy. "
        "Báo màu khóa — không 100%."
    ),
    "S_BLACK_COFFEE": (
        "(1) Cà phê đen khô. (2) Thấm lạnh. (3) Giấm 1:4 ngâm dài. (4) Oxy trắng (không len/lụa). "
        "(5) Giặt. (6) Ánh sáng trước sấy. Báo tỷ lệ thấp."
    ),
    "S_MILK_COFFEE": (
        "(1) Latte khô. (2) Enzyme ngâm dài / nước rửa chén. (3) Giấm 1:4. "
        "(4) Oxy nếu được. (5) Ánh sáng trước sấy."
    ),
    "S_TEA": (
        "(1) Trà khô. (2) Giấm ngâm dài. (3) Oxy trắng. (4) Giặt. Báo tỷ lệ thấp nếu đã sấy."
    ),
    "S_FRUIT_JUICE": (
        "(1) Nước ép khô. (2) Giấm ngâm. (3) Oxy trắng (không len/lụa). (4) Ánh sáng trước sấy."
    ),
    "S_SOFT_DRINK": (
        "(1) Đường khô/cola. (2) Ngâm ấm + giấm. (3) Oxy trắng. (4) Hết dính mới sấy."
    ),
    "S_WHITE_WINE_BEER": (
        "(1) Đã vàng/đường khô. (2) Giấm. (3) Oxy trắng ngắn. Báo không 100%."
    ),
    "S_KIMCHI": (
        "(1) Kim chi khô. (2) Nước rửa chén. (3) Giấm. (4) Oxy trắng. Báo màu ớt còn."
    ),
    "S_KETCHUP": (
        "(1) Tương cà khô. (2) Cạo. (3) Ngâm + nước rửa chén. (4) Giấm lặp. "
        "(5) Oxy trắng. Báo màu đỏ còn — không 100%."
    ),
    "S_TOMATO_SAUCE": (
        "(1) Sốt cà khô. (2) Cạo. (3) Ngâm + nước rửa chén. (4) Giấm. (5) Oxy trắng."
    ),
    "S_COOKING_OIL": (
        "(1) Dầu ăn khô. (2) Bột hút 2 lần. (3) Nước rửa chén/lipase. "
        "(4) Hết nhờn mới sấy. Báo thấp nếu khóa nhiệt."
    ),
    "S_GREASE": (
        "(1) Mỡ khô. (2) Hút 2 lần. (3) Nước rửa chén. (4) Hết nhờn mới sấy."
    ),
    "S_BUTTER": (
        "(1) Bơ khô. (2) Hút → nước rửa chén. (3) Kiểm nhờn. Báo khóa nhiệt."
    ),
    "S_MOTORBIKE_OIL": (
        "(1) Dầu nhớt khô. (2) Hút → dung môi (thông gió)/nước rửa chén. "
        "(3) Giặt. Báo không 100%."
    ),
    "S_ENGINE_OIL": (
        "(1) Dầu động cơ khô. (2) Hút → dung môi lặp. (3) Nước rửa chén. Báo tỷ lệ thấp."
    ),
    "S_BUBBLE_TEA": (
        "(1) Trà sữa khô. (2) Enzyme dài. (3) Nước rửa chén. (4) Giấm. "
        "(5) Oxy trắng. Phòng vàng đường."
    ),
    "S_CURRY": (
        "(1) Cà ri khô. (2) Nước rửa chén. (3) Baking soda. (4) Oxy/UV. Báo màu nghệ còn."
    ),
    "S_SOY_SAUCE": (
        "(1) Nước tương khô. (2) Enzyme dài. (3) Giấm. (4) Oxy trắng. Ánh sáng trước sấy."
    ),
    "S_FISH_SAUCE": (
        "(1) Nước mắm khô. (2) Enzyme → giấm lặp (mùi). (3) Oxy trắng. Báo mùi còn."
    ),
    "S_BBQ_SAUCE": (
        "(1) BBQ khô. (2) Enzyme → nước rửa chén → giấm → oxy. Báo vàng đường."
    ),
    "S_MAYO": (
        "(1) Mayo khô. (2) Cạo → nước rửa chén → enzyme. (3) Hết nhờn. Giữ thứ tự dầu→protein."
    ),
    "S_CHOCOLATE": (
        "(1) Sô-cô-la khô. (2) Cạo → lạnh → enzyme → nước rửa chén. (3) Oxy trắng."
    ),
    "S_PAINT_LATEX": (
        "(1) Sơn nước đã khô. (2) Dung môi nhẹ + blot lặp. (3) Nước rửa chén. Báo tỷ lệ thấp."
    ),
}

# Per-stain 2nd-pass rescue (falls back to group card if missing)
RESCUE_BY_STAIN: dict[str, dict[str, str]] = {
    "S_RED_WINE": {
        "ko": "2차: 식초 1:4 재침지 15–30분 → 흰/면만 산소(테스트) → 강광. 적자색 고착·100% 불가 고지.",
        "vi": "Lần 2: giấm 1:4 ngâm lại 15–30 phút → oxy chỉ trắng/cotton → ánh sáng. Báo đỏ tím khóa, không 100%.",
        "en": "2nd: vinegar 1:4 again 15–30 → oxygen white cotton only → strong light. Disclose set purple; no 100%.",
    },
    "S_BLOOD_DRY": {
        "ko": "2차: 효소 농도·시간↑(실크·울 금지) → 흰 면만 과산화 재시도 → 갈색 남으면 한계 고지.",
        "vi": "Lần 2: tăng enzyme (CẤM lụa/len) → H₂O₂ lại chỉ cotton trắng → báo nếu nâu còn.",
        "en": "2nd: longer enzyme (no silk/wool) → H2O2 again white cotton only → disclose brown residual.",
    },
    "S_BLOOD_FRESH": {
        "ko": "2차: 이미 마르면 마른 피 경로로 전환. 온수·건조 금지 재고지.",
        "vi": "Lần 2: nếu đã khô → chuyển SOP máu khô. Nhắc CẤM nóng/sấy.",
        "en": "2nd: if dried, switch to dry-blood path. Re-state no heat/dryer.",
    },
    "S_INK_PEN": {
        "ko": "2차: 안쪽 알코올 블롯만 반복 → 안 되면 중단·전문. 문지르기·100% 금지.",
        "vi": "Lần 2: chỉ blot cồn mặt trái lặp → fail thì dừng/chuyên. CẤM chà / 100%.",
        "en": "2nd: reverse alcohol blot only → stop/refer if failing. No scrub/100%.",
    },
    "S_INK_PERMANENT": {
        "ko": "2차: 용제 테스트 후 1회만 추가 → 실패 시 전문. 원단 손상 위험 고지.",
        "vi": "Lần 2: thêm 1 lần dung môi sau test → fail thì chuyên. Báo rủi ro hỏng vải.",
        "en": "2nd: one more solvent pass after test → refer if fail. Disclose fabric risk.",
    },
    "S_RUST": {
        "ko": "2차: 안전 원단만 X2 재시도→즉시 중화. 실크·울은 식초만·전문. 철 잔존 고지.",
        "vi": "Lần 2: chỉ vải an toàn X2 lại → trung hòa ngay. Lụa/len: giấm/chuyên. Báo sắt còn.",
        "en": "2nd: X2 again only on safe fabrics → neutralize. Silk/wool: vinegar/refer. Disclose iron residual.",
    },
    "S_MOTORBIKE_OIL": {
        "ko": "2차: 흡착→용제(환기) 반복 → 미끄럼 없어진 뒤만 건조. 열고착이면 한계 고지.",
        "vi": "Lần 2: hút → dung môi (thông gió) lặp → hết nhờn mới sấy. Khóa nhiệt: báo giới hạn.",
        "en": "2nd: absorb → solvent (vent) repeats → dry only when not greasy. Heat-set: disclose limits.",
    },
    "S_PAINT_OIL": {
        "ko": "2차: 시너 블롯 1회만 추가(테스트) → 실패 시 전문. 아세테이트·실크 중단.",
        "vi": "Lần 2: thêm 1 blot dung môi (test) → fail thì chuyên. Acetate/lụa: dừng.",
        "en": "2nd: one more thinner blot after test → refer if fail. Stop on acetate/silk.",
    },
    "S_BETEL": {
        "ko": "2차: 식초 장침지 재실시 → 흰/면 산소 → 적갈 잔색·100% 불가 고지.",
        "vi": "Lần 2: giấm ngâm lại → oxy trắng/cotton → báo đỏ nâu còn, không 100%.",
        "en": "2nd: vinegar soak again → oxygen white cotton → disclose red-brown residual; no 100%.",
    },
    "S_MILDEW": {
        "ko": "2차: 식초→산소(허용 시) 1회 → 심한 곰팡이·가죽·실크는 전문. 100% 불가.",
        "vi": "Lần 2: giấm → oxy (nếu được) 1 lần → nặng/da/lụa: chuyên. Không 100%.",
        "en": "2nd: vinegar→oxygen once if allowed → heavy/leather/silk: refer. No 100%.",
    },
    "S_LIPSTICK": {
        "ko": "2차: 긁기+알코올 블롯+주방세제 재실시 → 흰옷 산소. 실크·울은 전문 고려.",
        "vi": "Lần 2: cạo + blot cồn + nước rửa chén lại → oxy trắng. Lụa/len: cân nhắc chuyên.",
        "en": "2nd: scrape+alcohol blot+detergent again → oxygen whites. Silk/wool: consider pro.",
    },
    "S_NAIL_POLISH": {
        "ko": "2차: 아세톤 1회만 추가(테스트) → 아세테이트면 즉시 중단·전문.",
        "vi": "Lần 2: thêm 1 lần acetone (test) → acetate: dừng ngay + chuyên.",
        "en": "2nd: one more acetone pass after test → acetate: stop and refer.",
    },
}

# VI ops drills with proper diacritics (replace unsigned GIAO DUC DRILL strings)
OPS_VI_CANON: dict[str, dict[str, str]] = {
    "I_CARE_LABEL": {
        "why_vi": (
            "[Tại sao] Nhãn = hợp đồng với vải. Không đoán ký hiệu. "
            "5 nhóm: giặt / tẩy / sấy / ủi / dry-clean. Có X → TUÂN THỦ."
        ),
        "fresh_path_vi": (
            "(1) Hỏi: nhãn rõ? (2) Đọc 5 nhóm, ghi max °C + tẩy + sấy + ủi + dry. "
            "(3) Nói khách đúng theo nhãn. (4) CẤM bỏ qua X. Nhãn mất → đường an toàn thấp + báo."
        ),
        "aftercare_vi": "Không cắt nhãn. Ghi tóm tắt ký hiệu trên phiếu.",
        "sense_check_vi": "Mắt: đủ 5 nhóm. Tay: nhãn không rách.",
        "success_rate_vi": "Nhãn rõ: cao. Mờ/mất: chỉ đường an toàn.",
        "refuse_when_vi": "Khách bắt bất chấp X → từ chối + báo rủi ro.",
    },
    "I_DRY_VS_WET": {
        "why_vi": (
            "[Tại sao] Ưu tiên nhãn. X chậu → dry. Suit/lụa đắt → dry. "
            "Down → wet nhẹ. Fur/da → spot/chuyên."
        ),
        "fresh_path_vi": (
            "(1) Hỏi nhãn + loại đồ. (2) X nước → dry. (3) Nói rõ wet hay dry. "
            "(4) CẤM máy mạnh khi không chắc."
        ),
        "aftercare_vi": "Ghi lý do wet/dry trên phiếu.",
        "sense_check_vi": "Mắt: nhãn/cấu trúc. Phiếu: lý do.",
        "success_rate_vi": "Nhãn rõ: cao. Không nhãn: trung bình.",
        "refuse_when_vi": "Fur thật / da / suit canvas bắt giặt nhà → từ chối.",
    },
    "I_INTAKE_SCRIPT": {
        "why_vi": (
            "[Tại sao] Ảnh + chữ ký bắt buộc. Vết khô: báo trước không 100%. "
            "Không ảnh = rủi ro khiếu nại. (Không nêu giá/bồi thường chi tiết — chỉ quy trình.)"
        ),
        "fresh_path_vi": (
            "(1) Đếm+ghi. (2) Chụp tổng+close-up. (3) Báo thời gian xử lý. "
            "(4) Phiếu 2 bản. (5) Vết khô: xin đồng ý giới hạn. (6) CẤM nhận không ảnh."
        ),
        "aftercare_vi": "Lưu ảnh+phiếu. Zalo phản hồi nhanh nếu có ảnh.",
        "sense_check_vi": "Mắt: ≥2 ảnh. Tay: chữ ký. Phiếu: cảnh báo vết khô.",
        "success_rate_vi": "Đủ ảnh+ký: tốt. Thiếu ảnh: rủi ro cao.",
        "refuse_when_vi": "Đòi 100% / từ chối ảnh → từ chối nhận hoặc chỉ khi có văn bản.",
    },
    "I_WATER_HARDNESS": {
        "why_vi": (
            "[Tại sao] Nước cứng → tăng bột + xả thêm + giấm A3 xả cuối tùy chọn + vệ sinh máy. "
            "Không thay bằng softener."
        ),
        "fresh_path_vi": (
            "(1) Nhận dấu hiệu. (2) Bột +1, extra rinse. (3) A3 xả nhẹ nếu cần. "
            "(4) CẤM dùng softener thay rinse."
        ),
        "aftercare_vi": "Ghi khu vực. Khăn: ít softener.",
        "sense_check_vi": "Tay: hết căng. Mắt: bột/vàng.",
        "success_rate_vi": "Bù đúng: tốt. Bỏ qua: tái phát.",
        "refuse_when_vi": "Đòi Javel trị vàng protein/màu → từ chối.",
    },
    "I_MACHINE_PROFILE": {
        "why_vi": (
            "[Tại sao] Chọn chương trình theo vải. Kiểm vết TRƯỚC sấy. "
            "CẤM sấy len/lụa/spandex/da."
        ),
        "fresh_path_vi": (
            "(1) Hỏi vải+nhãn. (2) Chọn chương trình. (3) Kiểm ánh sáng trước sấy. "
            "(4) CẤM sấy khi còn vết."
        ),
        "aftercare_vi": "Lấy đồ ngay. Vệ sinh phin. Ánh sáng trước sấy.",
        "sense_check_vi": "Mắt: hết vết trước sấy. Tay: hết bột.",
        "success_rate_vi": "Kiểm trước sấy: cao. Sấy sớm: khóa vết.",
        "refuse_when_vi": "Bắt sấy len/lụa/da → từ chối.",
    },
}

AFTERCARE_FORCE_VI_CANON = (
    "Ánh sáng mạnh TRƯỚC sấy/ủi. Còn vết/nhờn/mùi mà sấy = khóa vết."
)

RESCUE_DISCLOSE_VI_CANON = (
    "Lần 1 thất bại/vết khô: báo tỷ lệ thấp trước khi làm lần 2. CẤM hứa 100%."
)


def all_dried_path_ko(base: dict[str, str] | None = None) -> dict[str, str]:
    out = dict(base or {})
    out.update(EXTRA_DRIED_PATH_KO)
    return out


def all_dried_path_vi(base: dict[str, str] | None = None) -> dict[str, str]:
    out = dict(base or {})
    out.update(CANON_DRIED_PATH_VI)
    out.update(EXTRA_DRIED_PATH_VI)
    return out


def seed_dried_parity_rows(base_ko: dict[str, str] | None = None, base_vi: dict[str, str] | None = None) -> list[dict[str, str]]:
    ko = all_dried_path_ko(base_ko)
    vi = all_dried_path_vi(base_vi)
    ids = sorted(set(ko) | set(vi))
    rows = []
    for sid in ids:
        row: dict[str, str] = {"id": sid}
        if sid in ko:
            row["dried_path_ko"] = ko[sid]
        if sid in vi:
            row["dried_path_vi"] = vi[sid]
        rows.append(row)
    return rows


def seed_ops_vi_canon_rows() -> list[dict[str, str]]:
    rows = []
    for iid, fields in OPS_VI_CANON.items():
        row = {"id": iid}
        row.update(fields)
        rows.append(row)
    return rows


def vn_specialty_stain_seed_rows() -> list[dict]:
    """Minimal MERGE rows for oil paint + betel."""
    return [
        {
            "id": "S_PAINT_OIL",
            "name": "Oil Paint",
            "name_vi": "Sơn dầu",
            "name_ko": "유성 페인트",
            "group_id": "G4",
            "water_spreads": False,
            "contains_protein": False,
            "contains_tannin": False,
            "contains_oil": True,
            "contains_dye": True,
            "urgency": "same_day",
            "tip": "Oil paint needs solvent; test corner; ventilate; no acetate",
            "why_ko": (
                "[왜 이 순서] 유성페인트=수지·안료·유기용제. 수성(S_PAINT_LATEX)과 다름. "
                "시너/미네랄스피릿 구석 테스트·환기·PPE. 아세테이트·실크 손상 위험."
            ),
            "fresh_path_ko": (
                "(1) 유성 확인(수성과 구분). (2) 고형 긁기. (3) 용제 테스트+블롯. "
                "(4) 주방세제. (5) 세탁. (6) 강광. 아세테이트면 중단."
            ),
            "dried_path_ko": EXTRA_DRIED_PATH_KO["S_PAINT_OIL"],
            "why_vi": (
                "[Tại sao] Sơn dầu = nhựa + pigment + dung môi. Khác sơn nước. "
                "Test góc dung môi, thông gió, PPE. Acetate/lụa dễ hỏng."
            ),
            "fresh_path_vi": (
                "(1) Xác nhận sơn dầu. (2) Cạo. (3) Test + blot dung môi. "
                "(4) Nước rửa chén. (5) Giặt. (6) Ánh sáng. Acetate: dừng."
            ),
            "dried_path_vi": EXTRA_DRIED_PATH_VI["S_PAINT_OIL"],
            "success_rate_ko": "젖은 직후: 중간. 마른 막: 낮음 — 100% 비보장.",
            "success_rate_vi": "Vừa dính: TB. Màng khô: thấp — không 100%.",
            "refuse_when_ko": "아세테이트·고객 100%·환기 불가 → 거절/전문.",
            "refuse_when_vi": "Acetate / đòi 100% / không thông gió → từ chối/chuyên.",
        },
        {
            "id": "S_BETEL",
            "name": "Betel / Areca stain",
            "name_vi": "Vết trầu cau",
            "name_ko": "빈랑·빈랑즙",
            "group_id": "G3",
            "water_spreads": True,
            "contains_protein": False,
            "contains_tannin": True,
            "contains_oil": False,
            "contains_dye": True,
            "urgency": "same_day",
            "tip": "Betel tannin/pigment; cold; vinegar; oxygen whites only",
            "why_ko": (
                "[왜 이 순서] 빈랑·빈랑즙=탄닌+적갈 색소. 찬물·문지르기 금지. "
                "식초 1:4→흰/면 산소. 고착 시 잔색·100% 비보장."
            ),
            "fresh_path_ko": (
                "(1) 빈랑 적갈 확인. (2) 찬물 흡수(문지르기 금지). (3) 식초 1:4 5–15분. "
                "(4) 흰/면 산소. (5) 세탁. (6) 강광."
            ),
            "dried_path_ko": EXTRA_DRIED_PATH_KO["S_BETEL"],
            "why_vi": (
                "[Tại sao] Trầu/cau = tannin + pigment đỏ nâu. Lạnh, không chà. "
                "Giấm 1:4 → oxy trắng/cotton. Khô cứng: không 100%."
            ),
            "fresh_path_vi": (
                "(1) Nhận đỏ nâu trầu. (2) Thấm lạnh — CẤM chà. (3) Giấm 1:4 5–15 phút. "
                "(4) Oxy trắng/cotton. (5) Giặt. (6) Ánh sáng."
            ),
            "dried_path_vi": EXTRA_DRIED_PATH_VI["S_BETEL"],
            "success_rate_ko": "즉시·찬물: 중간~양호. 마른 적갈: 낮음 — 100% 비보장.",
            "success_rate_vi": "Xử lý sớm lạnh: TB–tốt. Đỏ nâu khô: thấp — không 100%.",
            "refuse_when_ko": "실크·울+산소 강제·100% 요구 → 거절.",
            "refuse_when_vi": "Bắt oxy lên lụa/len hoặc đòi 100% → từ chối.",
        },
    ]
