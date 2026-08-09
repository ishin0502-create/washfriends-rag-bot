# -*- coding: utf-8 -*-
"""Education gaps v8: VN residual stains (shrimp paste, sugarcane, gấc, annatto).

Additive Z16c pattern — mirror iodine/chili wiring.
"""
from __future__ import annotations

VN_STAIN_SEED_V8: list[dict] = [
    {
        "id": "S_SHRIMP_PASTE",
        "group_id": "G5",
        "name": "Shrimp paste / mam tom",
        "name_vi": "Mắm tôm",
        "name_ko": "새우젓·맘톰(mắm tôm)",
        "water_spreads": True,
        "contains_protein": True,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "high",
        "tip": "VN mắm tôm — oil+protein+dye+odor; not fish sauce alone",
        "why_ko": (
            "[왜 이 순서] 맘톰(새우젓)=유분+단백질+적갈 색소+냄새. "
            "느억맘과 다름. 순서: 긁기→찬물→주방세제→효소→식초(냄새)→흰/면 산소. "
            "문지르기·열고착·락스 남용 금지."
        ),
        "why_vi": (
            "[Tại sao] Mắm tôm = dầu+protein+màu đỏ+mùi. Khác nước mắm. "
            "Cạo → lạnh → D2 → E1 → A3 → oxy trắng. CẤM chà/nhiệt/Javel lạm."
        ),
        "fresh_path_ko": (
            "(1)맘톰·원단 확인(느억맘과 구분). (2)여분 Cap1 긁기·찬물. "
            "(3)주방세제 Cap2. (4)효소 찬물 15–45분. (5)식초 1:4 냄새 완화. "
            "(6)흰/면 산소(테스트). (7)세탁·강광. 100% 비보장."
        ),
        "fresh_path_vi": (
            "(1)Nhận mắm tôm (khác nước mắm). (2)Cạo Cap1 + xả lạnh. "
            "(3)D2 Cap2. (4)E1 ngâm 15–45. (5)Giấm 1:4 khử mùi. "
            "(6)Oxy trắng (test). (7)Giặt + ánh sáng. Không 100%."
        ),
        "dried_path_ko": (
            "(1)마른 맘톰. (2)주방세제→효소 장침지 15–30분. (3)식초 1:4. "
            "(4)흰/면 산소. (5)세탁·강광. (6)적갈·냄새 잔여 가능 — 100% 불가."
        ),
        "dried_path_vi": (
            "(1)Mắm tôm khô. (2)D2 → E1 ngâm 15–30. (3)Giấm 1:4. "
            "(4)Oxy trắng. (5)Giặt + ánh sáng. (6)Báo còn màu/mùi — không 100%."
        ),
        "success_rate_ko": "신선: 중~양호. 마른·열고착: 중하. 100% 비보장.",
        "success_rate_vi": "Tươi: TB–khá. Khô: TB–thấp. Không 100%.",
        "refuse_when_ko": "실크에 락스·강한 산소 강제 / 100% 약속 → 거절.",
        "refuse_when_vi": "Lụa + Javel/oxy mạnh / hứa 100% → từ chối.",
    },
    {
        "id": "S_SUGARCANE",
        "group_id": "G3",
        "name": "Sugarcane juice",
        "name_vi": "Nước mía",
        "name_ko": "사탕수수즙(nước mía)",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": True,
        "contains_oil": False,
        "contains_dye": True,
        "urgency": "high",
        "tip": "VN nước mía — sticky sugar + pigment; cold blot → vinegar → white oxygen",
        "why_ko": (
            "[왜 이 순서] 느억미아=당+연한 색소. 끈적·황변 위험. "
            "찬물 흡수(문지르기 금지)→식초 1:4→흰/면 산소. 열고착·건조 전 강광."
        ),
        "why_vi": (
            "[Tại sao] Nước mía = đường + sắc tố nhạt. Dính/vàng. "
            "Thấm lạnh (CẤM chà) → giấm 1:4 → oxy trắng. Ánh sáng trước sấy."
        ),
        "fresh_path_ko": (
            "(1)사탕수수즙·원단. (2)안쪽 찬물 흡수(문지르기 금지). "
            "(3)식초 1:4 10–20분. (4)흰/면 산소(테스트). (5)세탁. (6)강광."
        ),
        "fresh_path_vi": (
            "(1)Nhận nước mía + vải. (2)Thấm lạnh mặt trái — CẤM chà. "
            "(3)Giấm 1:4 10–20 phút. (4)Oxy trắng (test). (5)Giặt. (6)Ánh sáng."
        ),
        "dried_path_ko": (
            "(1)마른·끈적 느억미아. (2)식초 1:4 장침지 15–30분. (3)흰/면 산소. "
            "(4)세탁·강광. (5)황변 잔여 가능 — 100% 비보장."
        ),
        "dried_path_vi": (
            "(1)Nước mía khô/dính. (2)Giấm 1:4 ngâm 15–30. (3)Oxy trắng. "
            "(4)Giặt + ánh sáng. (5)Báo vàng còn — không 100%."
        ),
        "success_rate_ko": "신선: 양호. 마른·황변: 중. 100% 비보장.",
        "success_rate_vi": "Tươi: khá. Khô/vàng: TB. Không 100%.",
        "refuse_when_ko": "이미 열고착 황변에 100% 복원 약속 → 거절.",
        "refuse_when_vi": "Đã khóa nhiệt + hứa 100% → từ chối.",
    },
    {
        "id": "S_GAC",
        "group_id": "G4",
        "name": "Gac fruit / bot gac",
        "name_vi": "Gấc / bột gấc",
        "name_ko": "극·가정(gấc)",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "high",
        "tip": "VN gấc carotenoid — oil scrape → dish → alcohol blot → white oxygen + sun",
        "why_ko": (
            "[왜 이 순서] 가정(gấc)=카로티노이드 주황 색소+오일. "
            "커리와 구분. 긁기→주방세제→알코올 블롯→흰/면 산소·햇빛. 문지르기·열고착 금지."
        ),
        "why_vi": (
            "[Tại sao] Gấc = carotenoid cam + dầu. Khác cà ri. "
            "Cạo → D2 → blot A1 → oxy trắng + nắng. CẤM chà/nhiệt."
        ),
        "fresh_path_ko": (
            "(1)가정·원단 확인. (2)여분 오일 Cap1 긁기. (3)주방세제 Cap2. "
            "(4)알코올 안쪽 블롯(테스트). (5)흰/면 산소(테스트). (6)세탁·햇빛/강광."
        ),
        "fresh_path_vi": (
            "(1)Nhận gấc + vải. (2)Cạo dầu Cap1. (3)D2 Cap2. "
            "(4)Blot cồn mặt trái (test). (5)Oxy trắng (test). (6)Giặt + nắng/ánh sáng."
        ),
        "dried_path_ko": (
            "(1)마른 가정 주황. (2)주방세제→알코올 블롯 반복. (3)흰/면 산소 장침지. "
            "(4)세탁·햇빛. (5)주황 잔색 가능 — 100% 불가."
        ),
        "dried_path_vi": (
            "(1)Gấc khô cam. (2)D2 → blot cồn lặp. (3)Oxy dài. "
            "(4)Giặt + nắng. (5)Báo còn cam — không 100%."
        ),
        "success_rate_ko": "신선: 중. 마른·열고착: 낮음. 100% 비보장.",
        "success_rate_vi": "Tươi: TB. Khô: thấp. Không 100%.",
        "refuse_when_ko": "유색에 락스 강제 / 100% 약속 → 거절.",
        "refuse_when_vi": "Ép Javel màu / hứa 100% → từ chối.",
    },
    {
        "id": "S_ANNATTO",
        "group_id": "G4",
        "name": "Annatto / dieu mau",
        "name_vi": "Điều màu / annatto",
        "name_ko": "아나토·디에우마우(điều màu)",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "high",
        "tip": "VN điều màu food color — blot → alcohol → white oxygen; no scrub",
        "why_ko": (
            "[왜 이 순서] 디에우마우(아나토)=식품용 황·주황 색소(+오일). "
            "찬물→알코올 블롯→흰/면 산소. 문지르기·열고착 금지. 100% 비보장."
        ),
        "why_vi": (
            "[Tại sao] Điều màu = màu vàng–cam thực phẩm (+dầu). "
            "Lạnh → blot cồn → oxy trắng. CẤM chà/nhiệt. Không 100%."
        ),
        "fresh_path_ko": (
            "(1)아나토·원단. (2)찬물 흡수(문지르기 금지). (3)알코올 안쪽 블롯(테스트). "
            "(4)흰/면 산소(테스트). (5)세탁. (6)강광."
        ),
        "fresh_path_vi": (
            "(1)Nhận điều màu + vải. (2)Thấm lạnh — CẤM chà. (3)Blot cồn (test). "
            "(4)Oxy trắng (test). (5)Giặt. (6)Ánh sáng."
        ),
        "dried_path_ko": (
            "(1)마른 디에우마우. (2)알코올 블롯 반복. (3)흰/면 산소 장침지. "
            "(4)세탁·강광. (5)황·주황 잔색 — 100% 불가."
        ),
        "dried_path_vi": (
            "(1)Điều màu khô. (2)Blot cồn lặp. (3)Oxy dài. "
            "(4)Giặt + ánh sáng. (5)Báo còn vàng/cam — không 100%."
        ),
        "success_rate_ko": "신선: 중~양호. 마른: 중하. 100% 비보장.",
        "success_rate_vi": "Tươi: TB–khá. Khô: TB–thấp. Không 100%.",
        "refuse_when_ko": "100% 복원 약속·유색 락스 → 거절.",
        "refuse_when_vi": "Hứa 100% / Javel màu → từ chối.",
    },
]


def vn_specialty_stain_seed_rows_v8() -> list[dict]:
    return list(VN_STAIN_SEED_V8)


DRIED_BY_ID_V8 = {
    r["id"]: (r["dried_path_ko"], r["dried_path_vi"]) for r in VN_STAIN_SEED_V8
}

RESCUE_BY_STAIN_V8 = {
    "S_SHRIMP_PASTE": {
        "ko": "2차: 주방세제→효소 장침지→식초→흰/면 산소. 냄새·적갈 잔여 고지. 100% 금지.",
        "vi": "Lần 2: D2 → E1 dài → A3 → oxy trắng. Báo mùi/màu. CẤM 100%.",
        "en": "2nd: dish → longer enzyme → vinegar → white oxygen. Disclose odor/color. No 100%.",
    },
    "S_SUGARCANE": {
        "ko": "2차: 식초 1:4 장침지 15–30분→흰/면 산소. 황변 고지. 100% 금지.",
        "vi": "Lần 2: giấm 1:4 15–30 → oxy trắng. Báo vàng. CẤM 100%.",
        "en": "2nd: vinegar 1:4 soak 15–30 → white oxygen. Disclose yellowing. No 100%.",
    },
    "S_GAC": {
        "ko": "2차: 주방세제→알코올 블롯→흰/면 산소·햇빛. 주황 잔색 고지. 100% 금지.",
        "vi": "Lần 2: D2 → blot cồn → oxy + nắng. Báo cam. CẤM 100%.",
        "en": "2nd: dish → alcohol blot → oxygen + sun. Disclose orange residual. No 100%.",
    },
    "S_ANNATTO": {
        "ko": "2차: 알코올 블롯→흰/면 산소. 황·주황 잔색 고지. 100% 금지.",
        "vi": "Lần 2: blot cồn → oxy trắng. Báo vàng/cam. CẤM 100%.",
        "en": "2nd: alcohol blot → white oxygen. Disclose yellow/orange. No 100%.",
    },
}


def fish_sauce_upgrade_fields() -> dict[str, str]:
    """Richer fish-sauce education (existing S_FISH_SAUCE node)."""
    return {
        "why_ko": (
            "[왜 이 순서] 느억맘=단백질+유분+염·냄새. "
            "찬물→효소→주방세제(유분)→식초(냄새)→흰/면 산소. 락스 남용·열고착 금지."
        ),
        "why_vi": (
            "[Tại sao] Nước mắm = protein+dầu+mặn/mùi. "
            "Lạnh → E1 → D2 → A3 → oxy trắng. CẤM Javel lạm/nhiệt."
        ),
        "fresh_path_ko": (
            "(1)느억맘·원단. (2)찬물. (3)효소 15–45분. (4)주방세제 Cap2. "
            "(5)식초 1:4. (6)흰/면 산소(테스트). (7)세탁·강광."
        ),
        "fresh_path_vi": (
            "(1)Nhận nước mắm. (2)Xả lạnh. (3)E1 15–45. (4)D2 Cap2. "
            "(5)Giấm 1:4. (6)Oxy trắng. (7)Giặt + ánh sáng."
        ),
        "dried_path_ko": (
            "(1)마른 느억맘. (2)효소 장침지 15–30분→주방세제→식초. "
            "(3)흰/면 산소. (4)세탁·강광. (5)냄새 잔여 가능 — 100% 비보장."
        ),
        "dried_path_vi": (
            "(1)Nước mắm khô. (2)E1 15–30 → D2 → A3. "
            "(3)Oxy trắng. (4)Giặt + ánh sáng. (5)Báo mùi — không 100%."
        ),
    }
