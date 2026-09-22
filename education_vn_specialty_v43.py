# -*- coding: utf-8 -*-
"""VN specialty stains v43 — motorbike / climate stains (no % rates).

Safe batch: new IDs that do not conflict with S_MILDEW fabric assembly.
Engine kept; data + protocol builders only.
"""
from __future__ import annotations

NEW_VN_STAINS_V43: list[dict] = [
    {
        "id": "S_VN_CHAIN_OIL",
        "name": "Motorbike chain oil",
        "name_vi": "Dầu xích xe máy",
        "name_ko": "오토바이 체인 기름",
        "group_id": "G2",
        "water_spreads": False,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "same_day",
        "tip": "Compound: grease then iron dust; dish soap then vinegar for metal; oxygen whites only",
        "why_ko": (
            "[왜 이 순서] 체인 기름=윤활유+철분·먼지 복합. "
            "①주방세제로 기름 → ②식초·레몬으로 철분 잔색. 한꺼번에 섞지 마세요."
        ),
        "why_vi": (
            "[Tại sao] Dầu xích = dầu + bụi kim loại. "
            "①Nước rửa chén lấy dầu → ②giấm/chanh lấy sắt. Không trộn bước."
        ),
        "fresh_path_ko": (
            "(1) 주방세제 원액 15–20분 → 미지근 헹굼(반복 OK). "
            "(2) 검은 잔색(철분): 식초 또는 레몬 15분 → 찬물. "
            "(3) 흰옷만 산소계 표백제 30분. (4) 세탁(면·폴리 40℃까지). "
            "※ WD-40는 내부 응급·매니저 확인·구석 테스트 — 손님에게 비법 고지 금지."
        ),
        "fresh_path_vi": (
            "(1) Nước rửa chén nguyên 15–20 phút → xả ấm (lặp OK). "
            "(2) Vết đen (sắt): giấm/chanh 15 phút → xả lạnh. "
            "(3) Áo trắng: tẩy oxy 30 phút. (4) Giặt (cotton/poly ≤40℃). "
            "※ WD-40 chỉ nội bộ · hỏi quản lý · test góc."
        ),
        "dried_path_ko": "마른 체인유: 세제 반복 → 철분 식초. 미끄럼 남은 채 건조 금지.",
        "dried_path_vi": "Khô: lặp xà phòng → giấm sắt. Cấm sấy khi còn nhờn.",
        "success_rate_ko": "2단계 지키면 개선. 완전 제거·검은 잔영 비보장 — 동의.",
        "success_rate_vi": "Đúng 2 bước: cải thiện. Không cam kết sạch hết — đồng ý.",
        "refuse_when_ko": "실크·울에 강한 용제·고온 강제 → 거절·전문.",
        "refuse_when_vi": "Ép dung môi mạnh/nóng lên lụa/len → từ chối/chuyên.",
    },
    {
        "id": "S_VN_EXHAUST_SOOT",
        "name": "Exhaust soot",
        "name_vi": "Bồ hóng / khói xe",
        "name_ko": "배기가스 매연·그을음",
        "group_id": "G5",
        "water_spreads": False,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "same_day",
        "tip": "Dry brush first — wet rub drives carbon in; then dish soap; oxygen whites",
        "why_ko": (
            "[왜 이 순서] 매연=카본 입자+미량 기름. "
            "물 먼저 문지르면 섬유에 박힘 → 마른 털기 → 주방세제 → 흰옷 산소."
        ),
        "why_vi": (
            "[Tại sao] Bồ hóng = carbon + ít dầu. "
            "Làm ướt trước → ngấm sâu. Phủi khô → nước rửa chén → oxy trắng."
        ),
        "fresh_path_ko": (
            "(1) 마른 솔·테이프로 털기(물 먼저 금지). "
            "(2) 주방세제 10분 → 미지근 헹굼. "
            "(3) 흰옷만 산소계 15–30분. (4) 세탁. "
            "목둘레 누적: 주 1–2회 주방세제 전처리 권장."
        ),
        "fresh_path_vi": (
            "(1) Phủi khô bàn chải/băng dính (cấm ướt trước). "
            "(2) Nước rửa chén 10 phút → xả ấm. "
            "(3) Áo trắng: oxy 15–30 phút. (4) Giặt. "
            "Cổ áo: tiền xử lý 1–2 lần/tuần."
        ),
        "dried_path_ko": "마른 검댕: 마른 털기 반복 → 세제. 세게 문지르지 마세요.",
        "dried_path_vi": "Khô: phủi lại → xà phòng. Không chà mạnh.",
        "success_rate_ko": "조기·마른 제거 시 양호. 누적 목둘레: 부분 개선.",
        "success_rate_vi": "Làm sớm + phủi khô: tốt. Cổ tích tụ: cải thiện một phần.",
        "refuse_when_ko": "락스로 매연만 지우기 요구 → 거절.",
        "refuse_when_vi": "Chỉ muốn Javel cho bồ hóng → từ chối.",
    },
    {
        "id": "S_VN_BRAKE_FLUID",
        "name": "Brake fluid",
        "name_vi": "Dầu thắng / dầu phanh",
        "name_ko": "브레이크액·유압유",
        "group_id": "G5",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": False,
        "contains_dye": False,
        "urgency": "immediate",
        "tip": "Water-soluble glycol — rinse cold first, NOT dish soap first; may fade synthetics",
        "why_ko": (
            "[왜 이 순서] 브레이크액=수용성(글리콜). "
            "엔진오일과 다름 → 찬물 헹굼이 먼저. 주방세제 먼저 쓰지 마세요."
        ),
        "why_vi": (
            "[Tại sao] Dầu thắng tan trong nước (khác dầu nhớt). "
            "Xả lạnh trước — không bắt đầu bằng nước rửa chén."
        ),
        "fresh_path_ko": (
            "(1) 즉시 찬물로 충분히 헹구기. "
            "(2) 중성세제 세탁. "
            "(3) 흰옷만 잔색 시 산소계 15분. "
            "방치 시 합성 원단 색빠짐·손상 가능 — 빨리 처리."
        ),
        "fresh_path_vi": (
            "(1) Xả lạnh ngay, kỹ. "
            "(2) Giặt xà phòng trung tính. "
            "(3) Áo trắng còn vết: oxy 15 phút. "
            "Để lâu có thể phai/hỏng vải tổng hợp — xử lý nhanh."
        ),
        "dried_path_ko": "마른 뒤: 찬물 재헹굼 → 중성세제. 완전 제거 비보장.",
        "dried_path_vi": "Khô: xả lạnh lại → xà phòng trung tính. Không cam kết sạch hết.",
        "success_rate_ko": "즉시 헹굼 시 양호. 방치·합성 색빠짐: 낮음.",
        "success_rate_vi": "Xả sớm: tốt. Để lâu/phai: thấp.",
        "refuse_when_ko": "이미 색빠짐·고가 합성에 강한 표백 강제 → 거절·전문.",
        "refuse_when_vi": "Đã phai / ép tẩy mạnh → từ chối/chuyên.",
    },
    {
        "id": "S_VN_GASOLINE",
        "name": "Gasoline / petrol",
        "name_vi": "Xăng",
        "name_ko": "휘발유·가솔린",
        "group_id": "G2",
        "water_spreads": False,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": False,
        "urgency": "immediate",
        "tip": "FIRE RISK: outdoor ventilate, evaporate, dish soap, vinegar odor; NEVER tumble dryer",
        "why_ko": (
            "[왜 이 순서] 휘발유=인화성·휘발성. "
            "실외 통풍→자연 증발→주방세제→식초(냄새). 건조기 절대 금지(화재)."
        ),
        "why_vi": (
            "[Tại sao] Xăng dễ cháy. Ngoài trời → bay hơi → nước rửa chén → giấm mùi. "
            "CẤM máy sấy (cháy)."
        ),
        "fresh_path_ko": (
            "(1) 실외·환기 · 화기 근처 금지. "
            "(2) 15–30분 펼쳐 자연 휘발. "
            "(3) 냄새 남으면 주방세제 → 미지근(약 35℃) 세탁. "
            "(4) 잔취: 식초 1:4 20분 → 통풍 자연 건조만. "
            "🔥 건조기·다림질·히터 근처 절대 금지."
        ),
        "fresh_path_vi": (
            "(1) Ngoài trời · thông gió · tránh lửa. "
            "(2) Trải 15–30 phút cho bay hơi. "
            "(3) Còn mùi: nước rửa chén → giặt ~35℃. "
            "(4) Còn mùi: giấm 1:4 20 phút → chỉ phơi gió. "
            "🔥 CẤM máy sấy / ủi / gần lửa."
        ),
        "dried_path_ko": "마른 뒤에도 냄새면 세제→식초→통풍. 건조기 금지.",
        "dried_path_vi": "Còn mùi: xà phòng → giấm → phơi gió. CẤM sấy.",
        "success_rate_ko": "냄새는 줄일 수 있음. 완전 무취·화재 안전이 우선.",
        "success_rate_vi": "Mùi có thể giảm. An toàn cháy quan trọng hơn sạch 100%.",
        "refuse_when_ko": "건조기 사용 요구·실내 화기 근처 작업 → 즉시 거절.",
        "refuse_when_vi": "Đòi máy sấy / làm gần lửa → từ chối ngay.",
    },
    {
        "id": "S_VN_RUBBER_MARK",
        "name": "Rubber / tire scuff",
        "name_vi": "Vết cao su / vết lốp",
        "name_ko": "고무·타이어 자국",
        "group_id": "G5",
        "water_spreads": False,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "same_day",
        "tip": "Alcohol dissolves rubber residue then dish soap; act fast before it sets",
        "why_ko": (
            "[왜 이 순서] 고무 자국=불용성 잔여+카본. "
            "알코올로 녹인 뒤 주방세제로 잔여 제거. 오래두면 섬유 침투."
        ),
        "why_vi": (
            "[Tại sao] Cao su không tan nước. "
            "Cồn hòa tan → nước rửa chén. Để lâu ngấm sợi."
        ),
        "fresh_path_ko": (
            "(1) 흰 천에 알코올(70%) 묻혀 5–10회 찍기. "
            "(2) 주방세제 10분. (3) 세탁. "
            "실크·아세테이트: 구석 테스트·매니저 확인."
        ),
        "fresh_path_vi": (
            "(1) Thấm cồn 70% khăn trắng, chấm 5–10 lần. "
            "(2) Nước rửa chén 10 phút. (3) Giặt. "
            "Lụa/acetate: test góc · hỏi quản lý."
        ),
        "dried_path_ko": "마른 줄: 알코올 반복 → 세제. 완전 제거 비보장.",
        "dried_path_vi": "Vết khô: lặp cồn → xà phòng. Không cam kết sạch hết.",
        "success_rate_ko": "조기 처리 시 양호. 고착: 부분.",
        "success_rate_vi": "Làm sớm: tốt. Cố định: một phần.",
        "refuse_when_ko": "아세톤 강제(아세테이트·실크) → 거절.",
        "refuse_when_vi": "Ép acetone (acetate/lụa) → từ chối.",
    },
    {
        "id": "S_VN_SWEAT_SUNSCREEN",
        "name": "Sweat + sunscreen yellow",
        "name_vi": "Mồ hôi + kem chống nắng",
        "name_ko": "땀+선크림 복합 황변",
        "group_id": "G2",
        "water_spreads": False,
        "contains_protein": True,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "same_day",
        "tip": "Compound: dish soap for sunscreen oil then enzyme for sweat protein then oxygen whites",
        "why_ko": (
            "[왜 이 순서] 땀+선크림=오일+단백질 반응 황변. "
            "일반 세탁만으로는 부족. ①주방세제(오일) → ②효소계 세제(단백질) → ③흰옷 산소."
        ),
        "why_vi": (
            "[Tại sao] Mồ hôi + kem = dầu + protein tạo vàng. "
            "①Nước rửa chén → ②enzyme → ③oxy trắng."
        ),
        "fresh_path_ko": (
            "(1) 주방세제 원액 15분 → 미지근(~40℃) 헹굼. "
            "(2) 효소계 세제 30분 → 미지근(30–35℃) 헹굼(50℃↑ 금지). "
            "(3) 흰옷만 산소계 1시간. (4) 세탁+직사광선. "
            "유색: 1–2만. 예방법: 선크림 바른 뒤 5분 후 옷 입기."
        ),
        "fresh_path_vi": (
            "(1) Nước rửa chén 15 phút → xả ~40℃. "
            "(2) Enzyme 30 phút → xả 30–35℃ (cấm ≥50℃). "
            "(3) Áo trắng: oxy 1 giờ. (4) Giặt + nắng. "
            "Áo màu: chỉ bước 1–2. Khuyên: đợi 5 phút sau kem rồi mặc."
        ),
        "dried_path_ko": "오래된 목둘레 황변: 1→2→3 반복. 완전 제거 비보장 — 동의.",
        "dried_path_vi": "Vàng cổ cũ: lặp 1→2→3. Không cam kết sạch hết — đồng ý.",
        "success_rate_ko": "복합 순서 시 개선. 완전 흰색 비보장.",
        "success_rate_vi": "Đúng thứ tự: cải thiện. Không cam kết sạch hết.",
        "refuse_when_ko": "유색에 산소·락스 강제 → 거절.",
        "refuse_when_vi": "Ép oxy/Javel lên áo màu → từ chối.",
    },
    {
        "id": "S_VN_ACID_RAIN",
        "name": "Dirty rain / urban rain mark",
        "name_vi": "Vết mưa bẩn",
        "name_ko": "빗물·대기오염 자국",
        "group_id": "G5",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": False,
        "contains_dye": True,
        "urgency": "same_day",
        "tip": "Cold rinse then neutral wash; yellow residue oxygen whites; first rains of season worst",
        "why_ko": (
            "[왜 이 순서] 도시 빗물=미세먼지·산성·광물. "
            "찬물 헹굼 → 중성세제 → 흰옷 노란 잔색만 산소."
        ),
        "why_vi": (
            "[Tại sao] Mưa đô thị = bụi + acid. "
            "Xả lạnh → xà phòng trung tính → oxy nếu còn vàng (trắng)."
        ),
        "fresh_path_ko": (
            "(1) 찬물 헹굼. (2) 중성세제 세탁. "
            "(3) 노란 자국·흰옷만 산소계 15분. "
            "우기 첫 비: 실내 건조 권장 안내."
        ),
        "fresh_path_vi": (
            "(1) Xả lạnh. (2) Giặt xà phòng trung tính. "
            "(3) Còn vàng + áo trắng: oxy 15 phút. "
            "Mưa đầu mùa: khuyên phơi trong nhà."
        ),
        "dried_path_ko": "마른 회·노란 자국: 헹굼→중성→산소(흰옷).",
        "dried_path_vi": "Vết khô: xả → trung tính → oxy trắng.",
        "success_rate_ko": "대부분 개선. 강한 노란 잔색: 부분.",
        "success_rate_vi": "Thường cải thiện. Vàng đậm: một phần.",
        "refuse_when_ko": "락스 강제 → 거절.",
        "refuse_when_vi": "Ép Javel → từ chối.",
    },
    {
        "id": "S_VN_CEMENT",
        "name": "Cement / lime dust",
        "name_vi": "Xi măng / vôi",
        "name_ko": "시멘트·석회",
        "group_id": "G5",
        "water_spreads": False,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": False,
        "contains_dye": False,
        "urgency": "same_day",
        "tip": "Dry scrape first — wet rub binds alkali; then vinegar neutralize; dish soap wash",
        "why_ko": (
            "[왜 이 순서] 시멘트=강알칼리. "
            "젖은 채 문지르면 섬유 결합 → 마른 뒤 긁기 → 식초로 중화 → 세제."
        ),
        "why_vi": (
            "[Tại sao] Xi măng = kiềm mạnh. "
            "Chà ướt → liên kết sợi. Khô rồi cạo → giấm trung hòa → xà phòng."
        ),
        "fresh_path_ko": (
            "(1) 장갑 착용. 완전 마른 뒤 솔·긁기로 가루 제거(물 먼저 금지). "
            "(2) 식초 1:3 30분 담금 → 찬물. "
            "(3) 주방세제 세탁."
        ),
        "fresh_path_vi": (
            "(1) Đeo găng. Để khô hẳn → cạo/phủi (cấm xả trước). "
            "(2) Giấm 1:3 ngâm 30 phút → xả lạnh. "
            "(3) Giặt nước rửa chén."
        ),
        "dried_path_ko": "굳은 시멘트: 물리 제거 우선 → 식초. 무리한 표백 금지.",
        "dried_path_vi": "Cứng: cạo trước → giấm. Cấm tẩy mạnh tùy tiện.",
        "success_rate_ko": "마른 제거+식초 시 양호. 이미 화학 결합: 낮음.",
        "success_rate_vi": "Cạo khô + giấm: tốt. Đã liên kết: thấp.",
        "refuse_when_ko": "실크·가죽에 식초 통담금 강제 → 거절·전문.",
        "refuse_when_vi": "Ép ngâm giấm lên lụa/da → từ chối/chuyên.",
    },
]


def vn_specialty_stain_seed_rows_v43() -> list[dict]:
    """Rows for Neo4j MERGE (same shape as v41)."""
    return list(NEW_VN_STAINS_V43)


COMPOUND_VN_V43 = frozenset({
    "S_VN_CHAIN_OIL",
    "S_VN_SWEAT_SUNSCREEN",
})

OIL_FIRST_V43 = frozenset({
    "S_VN_CHAIN_OIL",
    "S_VN_EXHAUST_SOOT",
    "S_VN_GASOLINE",
    "S_VN_RUBBER_MARK",
    "S_VN_SWEAT_SUNSCREEN",
})

FIRE_HAZARD_V43 = frozenset({"S_VN_GASOLINE"})
