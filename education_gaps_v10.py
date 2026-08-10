# -*- coding: utf-8 -*-
"""Education gaps v10: close scorecard holes.

1) Tomato/grease routing (wired in graphrag)
2) Thin shared-SOP why overlays
3) Fabric F11–F13 Neo4j rows
4) New high-frequency stains (doenjang, gochujang, persimmon, crayon, softener spot)
5) Safe tools fallback when no Protocol match
"""
from __future__ import annotations

# ── Thin SOP why overlays (shared templates → distinctive franchise education) ─
THIN_SOP_WHY: dict[str, dict[str, str]] = {
    "S_BLACK_COFFEE": {
        "why_ko": "[왜 이 순서] 블랙커피=탄닌+갈색 색소(우유 없음). 즉시 찬물→식초 1:4→흰/면 산소. 라떼면 우유커피 SOP.",
        "why_vi": "[Tại sao] Cà phê đen = tannin (không sữa). Lạnh → giấm 1:4 → oxy trắng. Latte → S_MILK_COFFEE.",
    },
    "S_TEA": {
        "why_ko": "[왜 이 순서] 차=탄닌. 녹차·홍차 모두 즉시 찬물→식초 1:4. 밀크티·버블티는 별도 SOP.",
        "why_vi": "[Tại sao] Trà = tannin. Lạnh → giấm 1:4. Trà sữa/boba → SOP riêng.",
    },
    "S_FRUIT_JUICE": {
        "why_ko": "[왜 이 순서] 과일주스=과일산+색소(탄닌성). 즉시 찬물·문지르기 금지→식초 1:4→흰옷 산소. 열·건조 고착.",
        "why_vi": "[Tại sao] Nước trái cây = acid+màu. Lạnh, không chà → giấm → oxy trắng.",
    },
    "S_SOFT_DRINK": {
        "why_ko": "[왜 이 순서] 탄산·콜라=색소+당+산. 당이 남으면 끈적·재오염. 찬물→식초→흰옷 산소. 잔당 채 건조 금지.",
        "why_vi": "[Tại sao] Nước ngọt = màu+đường+acid. Lạnh → giấm → oxy. CAM sấy khi còn dính.",
    },
    "S_WHITE_WINE_BEER": {
        "why_ko": "[왜 이 순서] 화이트와인·맥주=탄닌 약·당/단백질 흔적. 레드와인과 다름. 찬물→식초→흰옷 산소. 맥주 거품 단백질은 효소 추가 가능.",
        "why_vi": "[Tại sao] Rượu trắng/bia ≠ đỏ. Lạnh → giấm → oxy. Bia: thêm enzyme nếu cần.",
    },
    "S_GREASE": {
        "why_ko": "[왜 이 순서] 기름때·그리즈=주방·기계 주변 고착 유지방. 식용유와 유사하나 더 끈적. 전분 흡착→주방세제 Cap2→리파아제. 미끄럼 남은 채 건조 금지.",
        "why_vi": "[Tại sao] Mỡ/grease bám. N3 → D2 Cap2 → E3. CAM sấy khi còn nhờn.",
    },
    "S_BUTTER": {
        "why_ko": "[왜 이 순서] 버터=유지방+유단백 흔적. 차게 긁기→전분→주방세제→필요 시 효소. 녹여 문지르면 번짐.",
        "why_vi": "[Tại sao] Bơ = mỡ sữa. Cạo lạnh → N3 → D2 → enzyme nếu cần.",
    },
    "S_KETCHUP": {
        "why_ko": "[왜 이 순서] 케첩=토마토 색소+당+식초+약간 기름. 고형 제거→찬물→주방세제→식초→흰옷 산소. 토마토 파스타소스와 구분(소스 쪽이 기름·향신 더 많음).",
        "why_vi": "[Tại sao] Ketchup = màu cà+đường. D2 → A3 → B1 trắng. Khác sốt cà pasta.",
    },
    "S_TOMATO_SAUCE": {
        "why_ko": "[왜 이 순서] 토마토소스·파스타소스=리코펜 색소+오일+허브. 케첩보다 기름 많음. 긁기→찬물→주방세제(기름)→식초(색소)→흰옷 산소.",
        "why_vi": "[Tại sao] Sốt cà/pasta = lycopene+dầu. D2 TRƯỚC → A3 → B1 trắng.",
    },
    "S_EGG": {
        "why_ko": "[왜 이 순서] 계란=알부민 단백질. 찬물만·온수 금지(응고). 고형 긁기→효소 15–30분→흰면 산소. 노른자 기름 많으면 주방세제 선행.",
        "why_vi": "[Tại sao] Trứng = albumin. CHỈ lạnh. Enzyme 15-30. Lòng đỏ nhiều mỡ: D2 trước.",
    },
    "S_MILK": {
        "why_ko": "[왜 이 순서] 우유=카제인 단백질+지방. 찬물→효소. 커피·초코 우유는 해당 복합 SOP. 온수 금지.",
        "why_vi": "[Tại sao] Sữa = casein+mỡ. Lạnh → enzyme. Cà phê sữa → SOP latte.",
    },
    "S_BABY_FORMULA": {
        "why_ko": "[왜 이 순서] 분유=단백질+유지방+당·철분 강화. 효소 장침지(20–40분). 철분 잔색은 흰면에만 산소·심하면 녹 SOP 검토.",
        "why_vi": "[Tại sao] Sữa công thức = protein+mỡ+sắt. Enzyme 20-40. Còn nâu: oxy / xem ri.",
    },
    "S_SWEAT_FRESH": {
        "why_ko": "[왜 이 순서] 신선 땀=염·요소·소량 피지. 찬물·효소. 겨드랑이 황변은 땀황변 SOP. 데오 잔여는 데오 SOP.",
        "why_vi": "[Tại sao] Mồ hôi tươi. Enzyme. Nách vàng → S_SWEAT_YELLOW.",
    },
    "S_FECES": {
        "why_ko": "[왜 이 순서] 대변=바이오하자드+단백질+색소. PPE(장갑·마스크)→고형 제거→찬물→효소 장침지. 락스 남용 금지(원단·가스).",
        "why_vi": "[Tại sao] Phân = biohazard+protein. PPE → enzyme dài. Không Javel lạm.",
    },
    "S_SOY_SAUCE": {
        "why_ko": "[왜 이 순서] 간장=아미노산·색소·염. 단백질성→효소 먼저→식초(색소)·흰옷 산소. 피시소스와 구분.",
        "why_vi": "[Tại sao] Nước tương. Enzyme → giấm → oxy. Khác nước mắm.",
    },
    "S_VOMIT": {
        "why_ko": "[왜 이 순서] 구토=바이오하자드+위산+단백질·음식물. PPE→고형 제거→찬물→효소→식초(냄새·산). 열·건조 전 PPE·환기.",
        "why_vi": "[Tại sao] Chất nôn. PPE → enzyme → giấm khử mùi.",
    },
    "S_URINE": {
        "why_ko": "[왜 이 순서] 소변=요소·염·냄새. PPE→찬물→효소→식초(냄새). 오래된 노란 자국은 장침지. 락스로 냄새만 가리지 말 것.",
        "why_vi": "[Tại sao] Nước tiểu. PPE → enzyme → giấm. Không chỉ Javel che mùi.",
    },
    "S_CURRY": {
        "why_ko": "[왜 이 순서] 카레·강황=커큐민 색소(난제거). 주방세제→식초→흰면 산소·UV 잔색 확인. 유색은 테스트. 100% 비보장.",
        "why_vi": "[Tại sao] Cà ri/nghệ = curcumin. D2 → A3 → oxy + UV. Không 100%.",
    },
    "S_MUSTARD": {
        "why_ko": "[왜 이 순서] 머스터드=강황·향신 색소+식초. 카레와 유사. 긁기→세제→식초→흰면 산소·UV.",
        "why_vi": "[Tại sao] Mù tạt ≈ nghệ. D2 → A3 → oxy + UV.",
    },
}


FABRIC_ROWS_V10: list[dict] = [
    {
        "id": "F11",
        "name": "Acetate",
        "name_vi": "Vai acetate / triacetate",
        "name_ko": "아세테이트·트리아세테이트",
        "max_temp": 30,
        "can_bleach": False,
        "enzyme_safe": False,
        "acid_safe": False,
        "can_oxygen": False,
        "dry_hint_vi": "KHONG say may; tranh acetone/A2",
        "iron_hint_vi": "Nhiet rat thap hoac khong ui",
    },
    {
        "id": "F12",
        "name": "Nylon",
        "name_vi": "Vai nylon / polyamide",
        "name_ko": "나일론·폴리아미드",
        "max_temp": 40,
        "can_bleach": False,
        "enzyme_safe": True,
        "acid_safe": True,
        "can_oxygen": False,
        "dry_hint_vi": "Say thap; tranh nhiet cao (co)",
        "iron_hint_vi": "Ui thap",
    },
    {
        "id": "F13",
        "name": "Blend",
        "name_vi": "Vai pha (cotton-poly / wool-blend…)",
        "name_ko": "혼방(면폴리·울혼방 등)",
        "max_temp": 40,
        "can_bleach": False,
        "enzyme_safe": True,
        "acid_safe": True,
        "can_oxygen": False,
        "dry_hint_vi": "Theo thanh phan yeu nhat (len/lua uu tien an toan)",
        "iron_hint_vi": "Theo nhan; chon muc thap hon",
    },
]


NEW_STAIN_SEED_V10: list[dict] = [
    {
        "id": "S_DOENJANG",
        "group_id": "G5",
        "name": "Doenjang / soybean paste",
        "name_vi": "Tương đậu / doenjang",
        "name_ko": "된장·된장찌개 국물",
        "water_spreads": True,
        "contains_protein": True,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "same_day",
        "tip": "KR doenjang — protein+oil+salt pigment; scrape cold then D2 then enzyme",
        "why_ko": (
            "[왜 이 순서] 된장=발효 대두 단백질+기름+갈색 색소·염. "
            "고형 긁기→찬물→주방세제→효소→흰/면 산소. 열고착·문지르기 금지."
        ),
        "why_vi": "[Tại sao] Doenjang = protein+dầu+màu nâu. Cạo → D2 → E1 → oxy trắng.",
        "fresh_path_ko": (
            "(1)된장·원단 확인. (2)고형 Cap1 긁기·찬물. (3)주방세제 Cap2. "
            "(4)효소 15–40분. (5)흰/면 산소(테스트). (6)세탁·강광."
        ),
        "fresh_path_vi": (
            "(1)Nhận doenjang. (2)Cạo + xả lạnh. (3)D2. (4)E1 15-40. "
            "(5)Oxy trắng. (6)Giặt + ánh sáng."
        ),
        "dried_path_ko": "(1)마른 된장. (2)D2→효소 장침지. (3)흰면 산소. (4)잔갈 가능·100% 비보장.",
        "dried_path_vi": "(1)Khô. (2)D2→E1 dài. (3)Oxy. (4)Không 100%.",
        "success_rate_ko": "신선·찬물: 중~양호. 마른·열고착: 중하. 100% 비보장.",
        "success_rate_vi": "Tươi+lạnh: trung-cao. Khô/say: thấp-trung. Không 100%.",
        "refuse_when_ko": "실크에 락스·강한 산소 강제 / 100% 복원 약속 → 거절.",
        "refuse_when_vi": "Lụa + Javel/oxy mạnh / hứa 100% → từ chối.",
    },
    {
        "id": "S_GOCHUJANG",
        "group_id": "G5",
        "name": "Gochujang / chili paste",
        "name_vi": "Tương ớt Hàn / gochujang",
        "name_ko": "고추장·비빔 고추장",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "high",
        "tip": "KR gochujang — chili dye+oil+sugar; not plain ketchup",
        "why_ko": (
            "[왜 이 순서] 고추장=고춧가루 색소+기름+당·메주. 김치·칠리소스와 유사하나 페이스트가 진함. "
            "긁기→찬물→주방세제→식초→흰/면 산소. 유색 테스트."
        ),
        "why_vi": "[Tại sao] Gochujang = màu ớt+dầu+đường. Cạo → D2 → A3 → oxy trắng.",
        "fresh_path_ko": (
            "(1)고추장·원단. (2)긁기·찬물. (3)주방세제 Cap2. (4)식초 1:4 5–15분. "
            "(5)흰/면 산소. (6)세탁·강광. 100% 비보장."
        ),
        "fresh_path_vi": (
            "(1)Nhận gochujang. (2)Cạo + lạnh. (3)D2. (4)Giấm 1:4. (5)Oxy. (6)Giặt."
        ),
        "dried_path_ko": "(1)마른 고추장. (2)D2→식초 장시간. (3)흰면 산소. (4)적갈 잔여 고지.",
        "dried_path_vi": "(1)Khô. (2)D2→A3 dài. (3)Oxy. (4)Báo còn màu.",
        "success_rate_ko": "신선: 중~양호. 마른·적갈 고착: 중하. 100% 비보장.",
        "success_rate_vi": "Tươi: trung-cao. Khô màu đỏ: thấp-trung. Không 100%.",
        "refuse_when_ko": "유색에 락스 강제 / 100% 복원 약속 → 거절.",
        "refuse_when_vi": "Ép Javel màu / hứa 100% → từ chối.",
    },
    {
        "id": "S_PERSIMMON",
        "group_id": "G3",
        "name": "Persimmon / kaki tannin",
        "name_vi": "Hồng / nước hồng (tanin)",
        "name_ko": "감·감물·감즙(탄닌)",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": True,
        "contains_oil": False,
        "contains_dye": True,
        "urgency": "immediate",
        "tip": "Persimmon juice sets fast with heat/air — cold vinegar ASAP",
        "why_ko": (
            "[왜 이 순서] 감물=강한 탄닌(감물 염색과 동일 계열). 공기·열에 갈변 고착 빠름. "
            "즉시 찬물→식초 1:4 반복→흰/면 산소. 지연 시 성공률 급락."
        ),
        "why_vi": "[Tại sao] Hồng = tannin mạnh. SOM lạnh → giấm lặp → oxy. Trễ = khó.",
        "fresh_path_ko": (
            "(1)감물·즉시 처리. (2)찬물 흡수(문지르기 금지). (3)식초 1:4 10–20분 반복. "
            "(4)흰/면 산소. (5)세탁·강광. 마른·열고착: 한계 고지."
        ),
        "fresh_path_vi": (
            "(1)Xử lý ngay. (2)Thấm lạnh. (3)Giấm 1:4 10-20 lặp. (4)Oxy. (5)Giặt."
        ),
        "dried_path_ko": "(1)갈변 고착 가능. (2)식초 장침지 반복. (3)흰면 산소. (4)100% 불가 고지.",
        "dried_path_vi": "(1)Có thể cố định. (2)Giấm dài. (3)Oxy. (4)Không 100%.",
        "success_rate_ko": "즉시·찬물: 중~양호. 지연·갈변 고착: 낮음. 100% 비보장.",
        "success_rate_vi": "Xử lý ngay: trung-cao. Trễ/nâu: thấp. Không 100%.",
        "refuse_when_ko": "이미 갈변 고착에 100% 복원 약속 / 유색 락스 → 거절.",
        "refuse_when_vi": "Đã nâu cố định + hứa 100% / Javel màu → từ chối.",
    },
    {
        "id": "S_CRAYON",
        "group_id": "G2",
        "name": "Crayon / wax pastel",
        "name_vi": "Sáp màu / bút sáp",
        "name_ko": "크레용·크레파스",
        "water_spreads": False,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "same_day",
        "tip": "Wax+pigment — freeze/scrape then low heat blotter like candle wax then D2",
        "why_ko": (
            "[왜 이 순서] 크레용=왁스+안료. 촛농과 유사. 얼려 깨기→흡수지+낮은 열 흡수→잔여 주방세제·색소는 흰면 산소. "
            "얼룩 위 고열 다림질 금지."
        ),
        "why_vi": "[Tại sao] Sáp màu ≈ sáp nến. Đông bẻ → giấy+ủi thấp → D2 → oxy trắng.",
        "fresh_path_ko": (
            "(1)크레용. (2)얼리거나 차게 해 깨기. (3)흡수지+낮은 다리미로 왁스 흡수. "
            "(4)잔여 D2. (5)흰/면 색소 산소(테스트). (6)세탁·강광."
        ),
        "fresh_path_vi": (
            "(1)Nhận sáp màu. (2)Lạnh bẻ. (3)Giấy+ủi thấp. (4)D2. (5)Oxy trắng. (6)Giặt."
        ),
        "dried_path_ko": "(1)굳은 크레용. (2)동결·다리미 흡수 반복. (3)D2·산소. (4)안료 잔여 가능.",
        "dried_path_vi": "(1)Cứng. (2)Đông/ủi hút lặp. (3)D2+oxy. (4)Còn màu có thể.",
        "success_rate_ko": "동결·흡수 정석: 중~높음. 안료 진함·열고착: 중간. 100% 비보장.",
        "success_rate_vi": "Đông+hút đúng: trung-cao. Màu đậm/say: trung. Không 100%.",
        "refuse_when_ko": "얼룩 위 고열 다림질 강제 / 100% 약속 → 거절.",
        "refuse_when_vi": "Ép ủi nóng trên vết / hứa 100% → từ chối.",
    },
    {
        "id": "S_SOFTENER_SPOT",
        "group_id": "G2",
        "name": "Fabric softener oil spot",
        "name_vi": "Vết dầu nước xả / softener",
        "name_ko": "유연제 오일 스팟·얼룩",
        "water_spreads": False,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": False,
        "urgency": "same_day",
        "tip": "Softener concentrate ring — dish soap + rewash; do not heat-set",
        "why_ko": (
            "[왜 이 순서] 유연제 스팟=농축 양이온·오일 링. 표백으로 안 지워짐. "
            "주방세제로 탈지→재세탁. 미끄럼 남은 채 건조·다림질 금지."
        ),
        "why_vi": "[Tại sao] Vết softener = dầu. D2 khử → giặt lại. CAM sấy/ủi khi còn nhờn.",
        "fresh_path_ko": (
            "(1)유연제 링 확인. (2)주방세제 Cap2 문질러 탈지 5–15분. (3)미온 재세탁. "
            "(4)필요 시 식초 1:4 헹굼 보조. (5)미끄럼 없어진 뒤 건조."
        ),
        "fresh_path_vi": (
            "(1)Nhận vòng softener. (2)D2 5-15 phút. (3)Giặt ấm lại. (4)Giấm 1:4 nếu cần. (5)Khô khi hết nhờn."
        ),
        "dried_path_ko": "(1)열고착 링. (2)D2 반복·담금. (3)재세탁. (4)한계 고지.",
        "dried_path_vi": "(1)Vòng đã sấy. (2)D2 lặp. (3)Giặt lại. (4)Báo hạn chế.",
        "success_rate_ko": "신선 링+D2: 높음. 열고착 미끄럼: 중. 100% 비보장.",
        "success_rate_vi": "Vòng tươi+D2: cao. Đã sấy nhờn: trung. Không 100%.",
        "refuse_when_ko": "표백만으로 해결 약속 / 미끄럼 남은 채 건조 강요 → 거절.",
        "refuse_when_vi": "Hứa chỉ tẩy / ép sấy khi còn nhờn → từ chối.",
    },
]


def thin_why_for(stain_id: str) -> dict[str, str]:
    return dict(THIN_SOP_WHY.get(stain_id) or {})


def fabric_seed_rows_v10() -> list[dict]:
    return list(FABRIC_ROWS_V10)


def vn_specialty_stain_seed_rows_v10() -> list[dict]:
    return list(NEW_STAIN_SEED_V10)
