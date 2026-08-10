# -*- coding: utf-8 -*-
"""Leather / suede franchise education — care, mold, cream, protector.

Item-primary garments already win over textile stain SOPs. This module
supplies rich KO/VI/EN fields + L1/L2/L3 chemicals so mold answers are not
generic cloth-blot + alcohol only.

VI copy MUST use proper diacritics (shop language) — never Cap/PPE telegrams.
"""
from __future__ import annotations

from typing import Any, Optional


LEATHER_SMOOTH_IDS = frozenset({
    "I_LEATHER_GARMENT",
    "I_LEATHER_BAG",
    "I_LEATHER_SHOE",
    "I_GLOVE_LEATHER",
    "I_GOLF_GLOVE_LEATHER",
})

SUEDE_IDS = frozenset({
    "I_SUEDE_GARMENT",
    "I_SUEDE_BAG",
    "I_SUEDE_SHOE",
})

LEATHER_FAMILY_IDS = LEATHER_SMOOTH_IDS | SUEDE_IDS


# Shop-facing leather products (not textile bleach/soak)
LEATHER_CHEM_SEED = [
    {
        "code": "L1",
        "name": "Leather cleaner",
        "name_vi": "Dung dịch vệ sinh da",
        "name_ko": "가죽 전용 클리너",
        "role": "pH-balanced leather surface cleaner — minimal water",
        "safe_on_wool": False,
        "safe_on_silk": False,
        "shop_name_vi": "Dung dịch / xịt vệ sinh da",
        "buy_where_vi": "Cửa đồ da, siêu thị đồ gia dụng / giày",
        "buy_where_ko": "구두·가죽용품점, 대형마트 신발케어 코너",
        "alt1_vi": "Xà phòng da pha rất loãng",
        "alt2_vi": "Khăn ẩm + xà phòng trung tính cực ít (test góc)",
        "alt3_vi": "Hết hàng: chỉ lau ẩm nhẹ — CẤM bột giặt/Javel",
        "alt1_ko": "가죽비누(leather soap) 아주 약하게 희석",
        "alt2_ko": "중성세제 극소량+미지근한 천(구석 테스트)",
        "alt3_ko": "없으면 미지근한 천만 — 일반세제·락스·산소표백 금지",
        "example_brands_vi": "",
        "wf_supply": False,
        "when_use_vi": "Da bóng: lau vết / bảo dưỡng. CẤM suede/nubuck ngâm nước.",
        "when_use_ko": "평활 가죽 표면 청소·오염 제거. 스웨이드·누벅에는 물/클리너 금지.",
        "dilution_vi": "Theo nhãn chai — ít nước, khăn, không ngâm",
        "dilution_ko": "병 안내 따름 — 천에 묻혀 국소만, 통담금·세탁기 금지",
    },
    {
        "code": "L2",
        "name": "Leather cream / conditioner",
        "name_vi": "Kem dưỡng da",
        "name_ko": "가죽 크림·컨디셔너",
        "role": "Restore oils after clean/mold — prevents dryness/cracking",
        "safe_on_wool": False,
        "safe_on_silk": False,
        "shop_name_vi": "Kem da / conditioner da",
        "buy_where_vi": "Cửa đồ da, cửa giày",
        "buy_where_ko": "구두·가죽용품점",
        "alt1_vi": "Balm / balsam da",
        "alt2_vi": "Mink oil chỉ khi nhãn cho (có thể tối màu — báo khách)",
        "alt3_vi": "CẤM bôi dầu ăn / vaseline lên áo da (bụi bám)",
        "alt1_ko": "레더 밤·밤삼",
        "alt2_ko": "밍크오일(라벨 허용 시만 — 어두워질 수 있음 고지)",
        "alt3_ko": "식용유·바셀린 금지(먼지 흡착·얼룩)",
        "example_brands_vi": "",
        "wf_supply": False,
        "when_use_vi": "BẮT BUỘC sau xử lý mốc/vết trên da bóng — khi da ĐÃ KHÔ.",
        "when_use_ko": "평활 가죽: 클리너/곰팡이 처리 후 완전 건조 뒤 필수 보습.",
        "dilution_vi": "Nguyên chất — bôi mỏng, đều, lau dư",
        "dilution_ko": "원액 얇게 펴 바르고 천으로 잉여 닦기 — 두껍게 바르지 말 것",
    },
    {
        "code": "L3",
        "name": "Leather protector",
        "name_vi": "Xịt bảo vệ da",
        "name_ko": "가죽 프로텍터(방수·오염방지)",
        "role": "Optional water/stain repellent after cream cured",
        "safe_on_wool": False,
        "safe_on_silk": False,
        "shop_name_vi": "Xịt chống thấm / bảo vệ da–giày",
        "buy_where_vi": "Cửa giày, siêu thị",
        "buy_where_ko": "구두용품점·마트 신발케어",
        "alt1_vi": "Bỏ qua nếu khách không cần",
        "alt2_vi": "Suede: chỉ xịt suede/nubuck riêng",
        "alt3_vi": "Thông gió khi xịt",
        "alt1_ko": "고객이 원치 않으면 생략",
        "alt2_ko": "스웨이드는 스웨이드 전용 스프레이만",
        "alt3_ko": "환기 후 분무",
        "example_brands_vi": "",
        "wf_supply": False,
        "when_use_vi": "Sau kem da khô — bảo vệ. Không thay kem dưỡng.",
        "when_use_ko": "크림이 마른 뒤 선택. 크림 대체가 아님.",
        "dilution_vi": "Xịt nhẹ 20–30cm, để khô theo nhãn",
        "dilution_ko": "20–30cm에서 약분무, 병 안내대로 건조",
    },
]


def _is_mold(stain_id: str, entities: Optional[dict] = None) -> bool:
    sid = str(stain_id or "").upper()
    if sid == "S_MILDEW":
        return True
    raw = str((entities or {}).get("_raw") or "")
    return any(k in raw for k in ("곰팡이", "곰팡", "mold", "mildew", "nam moc", "nấm mốc"))


def _canon_vi_fields(edu: dict[str, str]) -> dict[str, str]:
    """Ensure VI education never ships Cap/PPE/ASCII telegrams to the LLM."""
    try:
        from vi_text_canon import shop_speak_vi
    except Exception:
        return edu
    out = dict(edu)
    for k, v in list(out.items()):
        if isinstance(v, str) and k.endswith("_vi"):
            out[k] = shop_speak_vi(v)
    return out


def education_for(item_id: str, *, stain_id: str = "", entities: Optional[dict] = None) -> dict[str, str]:
    """Return path/teach fields to merge into stain_context / item_context."""
    mold = _is_mold(stain_id, entities)
    if item_id in SUEDE_IDS:
        return _canon_vi_fields(_suede_card(item_id, mold=mold))
    if item_id in LEATHER_SMOOTH_IDS:
        return _canon_vi_fields(_smooth_card(item_id, mold=mold))
    return {}


def _smooth_card(item_id: str, *, mold: bool) -> dict[str, str]:
    kind = {
        "I_LEATHER_GARMENT": "가죽 의류(평활)",
        "I_LEATHER_BAG": "가죽 가방·지갑",
        "I_LEATHER_SHOE": "가죽 구두",
        "I_GLOVE_LEATHER": "가죽 장갑",
        "I_GOLF_GLOVE_LEATHER": "골프 가죽장갑",
    }.get(item_id, "평활 가죽")
    kind_vi = {
        "I_LEATHER_GARMENT": "Áo/quần da bóng",
        "I_LEATHER_BAG": "Túi / ví da bóng",
        "I_LEATHER_SHOE": "Giày da bóng",
        "I_GLOVE_LEATHER": "Găng da",
        "I_GOLF_GLOVE_LEATHER": "Găng golf da",
    }.get(item_id, "Da bóng")

    if mold:
        return {
            "precheck_ko": (
                f"{kind}: 평활 가죽인지 스웨이드/누벅인지 먼저 확인. "
                "야외·환기. 마스크·니트릴 장갑. 사진·동의(100% 복원 약속 금지)."
            ),
            "why_ko": (
                "[왜 이 순서] 가죽 곰팡이=표면 포자+습도. 섬유용 식초 통담금·산소/락스·세탁기는 "
                "가죽을 굳히거나 갈라지게 함. 순서: 보호구→마른 털기→국소 소독(클리너/알코올 약하게)→"
                "완전 건조→가죽 크림 필수→(선택)프로텍터. 깊게 침투·갈라짐→전문."
            ),
            "fresh_path_ko": (
                "(1)스웨이드면 이 경로 중단→스웨이드 SOP/전문. "
                "(2)야외에서 마스크·장갑 착용. "
                "(3)마른 부드러운 천/솔로 표면 포자만 약하게 살살 털기(문지르기 금지). "
                "(4)가죽 전용 클리너 또는 소독용 알코올 70%를 흰 천에 묻혀 구석 테스트 후 "
                "바깥→안 약하게 국소 찍기 — 흠뻑·통담금·식초 담금·표백 금지. "
                "(5)물기 남은 천으로 잔여만 닦고 그늘에서 완전 건조(형태 유지). "
                "(6)마른 뒤 가죽 크림 얇게 → 잉여 닦기. "
                "(7)필요 시 프로텍터 약분무. "
                "(8)냄새·반점 남거나 갈라짐→전문·거절."
            ),
            "dried_path_ko": (
                "이미 마른 곰팡이·넓은 면적: 같은 순서 반복 1회만. "
                "안감까지 침투·가죽 갈라짐·고가 → 가정 추가 처리 중단, 전문."
            ),
            "motion_ko": "약하게만 — 찍기·털기. 문지르기·흔들어 '치료' 금지.",
            "water_temp_ko": "물 최소·실온. 세탁기·온수·통담금 금지.",
            "aftercare_ko": (
                "완전 건조 확인 후 크림. 건조기·직사광선·다림질 금지. "
                "보관: 통풍·제습, 비닐 밀봉 장기보관 금지(재발)."
            ),
            "sense_check_ko": "눈: 흰 반점·포자 잔여. 코: 곰팡이 냄새. 손: 건조·갈라짐.",
            "success_rate_ko": "표면·조기: 양호. 하룻밤+·안감 침투: 낮음·전문.",
            "refuse_when_ko": (
                "스웨이드/누벅 물세탁·알코올 과다, 세탁기 요구, "
                "깊게 침투·구조 손상·고가 명품 강제 가정처리 → 거절·전문."
            ),
            "precheck_vi": (
                f"{kind_vi}: phân biệt da bóng vs suede/nubuck. "
                "Ngoài trời + thông gió. Găng nitrile + khẩu trang. Ảnh + đồng ý (không cam kết 100%)."
            ),
            "why_vi": (
                "[Tại sao] Mốc trên da = bào tử + ẩm. "
                "CẤM ngâm giấm / bột tẩy oxy / Javel / máy giặt (da cứng, nứt). "
                "Thứ tự: bảo hộ → phủi khô → dung dịch vệ sinh da hoặc cồn 70% chấm nhẹ "
                "→ khô hẳn → kem dưỡng da bắt buộc → (tuỳ chọn) xịt bảo vệ. "
                "Ngấm sâu / nứt → chuyên."
            ),
            "fresh_path_vi": (
                "(1)Nếu suede → dừng đường này, chuyển SOP suede / chuyên. "
                "(2)Ngoài trời: găng + khẩu trang. "
                "(3)Khăn/bàn chải mềm khô: phủi bào tử nhẹ — không chà. "
                "(4)Dung dịch vệ sinh da hoặc cồn 70% thấm khăn trắng, test góc, "
                "chấm ngoài→trong nhẹ — CẤM ngâm / ướt đẫm / giấm / tẩy. "
                "(5)Lau dư bằng khăn hơi ẩm; phơi bóng mát đến khô hẳn (giữ form). "
                "(6)Khi khô: kem dưỡng da mỏng → lau dư. "
                "(7)Tuỳ chọn xịt bảo vệ. "
                "(8)Còn mùi / đốm / nứt → chuyên hoặc từ chối."
            ),
            "dried_path_vi": (
                "Mốc khô / diện rộng: lặp cùng thứ tự tối đa 1 lần. "
                "Ngấm lót / nứt / hàng đắt → dừng xử lý tại quán, chuyển chuyên."
            ),
            "motion_vi": "Lực nhẹ — chỉ phủi/chấm. CẤM chà mạnh.",
            "water_temp_vi": "Ít nước, nhiệt phòng. CẤM máy giặt / nước nóng / ngâm.",
            "aftercare_vi": (
                "Xác nhận khô rồi mới kem. CẤM máy sấy / nắng gắt / ủi. "
                "Bảo quản thoáng + hút ẩm; CẤM bịt kín nylon lâu (tái phát)."
            ),
            "sense_check_vi": "Mắt: hết đốm trắng/bào tử. Mũi: hết mùi mốc. Tay: khô/nứt?",
            "success_rate_vi": "Bề mặt sớm: tốt. Đã qua đêm / ngấm lót: thấp — chuyên.",
            "refuse_when_vi": (
                "Suede/nubuck đòi nước/cồn nhiều, đòi máy giặt, "
                "ngấm sâu / hỏng cấu trúc / ép xử lý hàng hiệu tại quán → từ chối."
            ),
        }

    shoe_bit_ko = (
        " 구두: 신문지·키친타월로 형태 유지. 끈 있으면 빼서 별도(갑피만 국소)."
        if item_id == "I_LEATHER_SHOE"
        else ""
    )
    shoe_bit_vi = (
        " Giày: nhồi giấy giữ form. Tháo dây nếu có — chỉ xử lý thân giày."
        if item_id == "I_LEATHER_SHOE"
        else ""
    )
    shoe_bit_en = (
        " Shoes: stuff with paper to hold shape. Remove laces if present."
        if item_id == "I_LEATHER_SHOE"
        else ""
    )
    return {
        "precheck_ko": (
            f"{kind}: 평활 가죽 확인(스웨이드 아님). 라벨·장식·안감. "
            "세탁기·건조기·산소/락스 요구 시 거절."
            f"{shoe_bit_ko}"
        ),
        "why_ko": (
            "[왜 이 순서] 평활 가죽은 물·열·표백에 약함. 관리 루프: "
            "클리너로 표면 → 완전 건조 → 크림 보습 → (선택)프로텍터. "
            "얼룩은 국소만. 「일반·통세탁」 금지. 곰팡이는 별도 곰팡이 SOP."
        ),
        "fresh_path_ko": (
            "(1)먼지는 마른 천으로."
            f"{shoe_bit_ko} "
            "(2)가죽 전용 클리너를 천에 묻혀 약하게 닦기 → 젖은 천으로 잔여. "
            "(3)그늘에서 완전 건조(형태 유지 — 구두면 신문지). "
            "(4)가죽 크림 얇게 → 광택·잉여 닦기. "
            "(5)비·오염 많은 환경이면 프로텍터 약분무. "
            "(6)유분·잉크 등 얼룩: 국소만(과다 용제 금지) → 다시 크림. "
            "(7)세탁기·통담금·표백·고온건조 금지."
        ),
        "dried_path_ko": "이미 hardened/갈라짐: 크림 시도 1회 → 안 되면 전문. 강제 세탁 금지.",
        "motion_ko": "약하게 — 닦기·바르기. 세게 문지르기 금지.",
        "water_temp_ko": "물 최소·실온. 세탁기·온수 금지.",
        "aftercare_ko": "통풍 보관·제습. 직사광선·히터 근처 금지. 주기적 크림.",
        "sense_check_ko": "눈: 얼룩·백화. 손: 건조·갈라짐. 코: 곰팡이 냄새 없는지.",
        "success_rate_ko": "일상 클리너+크림: 높음. 심한 곰팡이·침투: 전문.",
        "refuse_when_ko": "세탁기·표백·스웨이드에 물클리너 → 거절.",
        "must_include_ko": "세탁기 금지, 가죽 크림, 최소 수분",
        "precheck_vi": (
            f"{kind_vi}: xác nhận da bóng (không phải suede). "
            "Nhãn / phụ kiện / lót. Đòi máy giặt / sấy / Javel → từ chối."
            f"{shoe_bit_vi}"
        ),
        "why_vi": (
            "[Tại sao] Da bóng yếu nước / nhiệt / tẩy. "
            "Vòng chăm sóc: dung dịch vệ sinh da → khô hẳn → kem dưỡng → (tuỳ chọn) xịt bảo vệ. "
            "Vết chỉ xử lý cục bộ. CẤM gọi là 「giặt thường / ngâm máy」. "
            "Mốc → SOP mốc riêng."
        ),
        "fresh_path_vi": (
            "(1)Phủi bụi bằng khăn khô."
            f"{shoe_bit_vi} "
            "(2)Dung dịch vệ sinh da thấm khăn, lau nhẹ → khăn hơi ẩm lau dư. "
            "(3)Phơi bóng mát đến khô hẳn (giày: nhồi giấy). "
            "(4)Kem dưỡng da mỏng → lau dư. "
            "(5)Mưa / bẩn nhiều: xịt bảo vệ nhẹ. "
            "(6)Vết dầu/mực: chỉ cục bộ (không ngâm dung môi) → kem lại. "
            "(7)CẤM máy giặt / ngâm / tẩy / sấy nóng."
        ),
        "dried_path_vi": "Đã cứng/nứt: thử kem 1 lần → không được thì chuyên. CẤM ép giặt máy.",
        "motion_vi": "Lực nhẹ — lau/bôi. CẤM chà mạnh.",
        "water_temp_vi": "Ít nước, nhiệt phòng. CẤM máy giặt / nước nóng.",
        "aftercare_vi": "Bảo quản thoáng + hút ẩm. CẤM nắng gắt / gần máy sưởi. Kem định kỳ.",
        "sense_check_vi": "Mắt: vết / bạc. Tay: khô / nứt. Mũi: không mốc.",
        "success_rate_vi": "Chăm sóc thường (vệ sinh + kem): cao. Mốc sâu: chuyên.",
        "refuse_when_vi": "Máy giặt / tẩy oxy / suede bằng nước → từ chối.",
        "must_include_vi": "CẤM máy giặt, kem dưỡng da, ít nước",
        "precheck_en": (
            f"{kind}: confirm smooth leather (not suede). Refuse washer/dryer/bleach."
            f"{shoe_bit_en}"
        ),
        "why_en": (
            "[Why this order] Smooth leather hates water/heat/bleach. Loop: "
            "cleaner → dry fully → cream → optional protector. "
            "Spot only — never machine-wash / soak."
        ),
        "fresh_path_en": (
            "(1)Dust with dry cloth."
            f"{shoe_bit_en} "
            "(2)Leather cleaner on cloth, light wipe → wipe residue. "
            "(3)Air-dry in shade (stuff shoes with paper). "
            "(4)Thin leather cream. (5)Optional protector. "
            "(6)Stains: local only. (7)No washer, soak, bleach, or hot dryer."
        ),
        "dried_path_en": "Hardened/cracked: one cream try → refer out. No forced wash.",
        "motion_en": "Light wipe/apply only — no scrubbing.",
        "water_temp_en": "Minimal room-temp water. No washer/hot water.",
        "aftercare_en": "Airy storage + periodic cream. No sun/heater.",
        "sense_check_en": "Eyes: marks/bloom. Hand: dryness/cracks. Nose: mold.",
        "success_rate_en": "Routine cleaner+cream: high. Deep mold: professional.",
        "refuse_when_en": "Washer/bleach/suede wet-clean demands → refuse.",
        "must_include_en": "no machine wash, leather cream, minimal water",
    }


def _suede_card(item_id: str, *, mold: bool) -> dict[str, str]:
    kind = {
        "I_SUEDE_GARMENT": "스웨이드·누벅 의류",
        "I_SUEDE_BAG": "스웨이드 가방",
        "I_SUEDE_SHOE": "스웨이드 구두",
    }.get(item_id, "스웨이드")
    kind_vi = {
        "I_SUEDE_GARMENT": "Áo suede / nubuck",
        "I_SUEDE_BAG": "Túi suede",
        "I_SUEDE_SHOE": "Giày suede",
    }.get(item_id, "Suede / nubuck")

    if mold:
        return {
            "precheck_ko": (
                f"{kind}: 물·알코올·일반 가죽클리너 금지. 야외·마스크. "
                "넓거나 젖은 곰팡이→전문 우선."
            ),
            "why_ko": (
                "[왜 이 순서] 스웨이드+물=영구 얼룩. 곰팡이는 마른 브러시로만. "
                "평활 가죽 크림/알코올 경로를 쓰지 말 것."
            ),
            "fresh_path_ko": (
                "(1)보호구·야외. "
                "(2)스웨이드 브러시/부드러운 솔로 결 따라 약하게 마른 털기만. "
                "(3)스웨이드 전용 이레이서·전용 스프레이만(라벨). "
                "(4)물·식초·표백·세탁기·평활용 크림 금지. "
                "(5)안 되면 즉시 전문·거절."
            ),
            "dried_path_ko": "젖은 채 곰팡이·넓은 면적: 가정 처리 중단, 전문.",
            "motion_ko": "약하게 마른 솔 — 물로 문지르기 금지.",
            "water_temp_ko": "물 사용 금지.",
            "aftercare_ko": "완전 건조·통풍. 스웨이드 프로텍터만(해당 시).",
            "sense_check_ko": "눈: 반점. 손: 결·수분.",
            "success_rate_ko": "가벼운 표면: 중간. 젖음·침투: 낮음.",
            "refuse_when_ko": "물세탁·알코올 과다·가정 강처리 요구 → 거절.",
            "precheck_vi": (
                f"{kind_vi}: CẤM nước / cồn mạnh / dung dịch da bóng. "
                "Ngoài trời + khẩu trang. Diện rộng hoặc ướt → ưu tiên chuyên."
            ),
            "why_vi": (
                "[Tại sao] Suede + nước = vết vĩnh viễn. "
                "Mốc: chỉ bàn chải khô. Không dùng kem/cồn của da bóng."
            ),
            "fresh_path_vi": (
                "(1)Bảo hộ + ngoài trời. "
                "(2)Bàn chải suede / mềm: phủi khô theo chiều lông — lực nhẹ. "
                "(3)Chỉ sản phẩm suede (eraser / xịt riêng theo nhãn). "
                "(4)CẤM nước / giấm / tẩy / máy / kem da bóng. "
                "(5)Không hết → chuyên / từ chối."
            ),
            "dried_path_vi": "Mốc khi còn ướt / diện rộng: dừng tại quán, chuyển chuyên.",
            "motion_vi": "Lực nhẹ — chỉ chải khô. CẤM chà bằng nước.",
            "water_temp_vi": "CẤM dùng nước.",
            "aftercare_vi": "Khô thoáng. Chỉ xịt protector suede (nếu có).",
            "sense_check_vi": "Mắt: đốm. Tay: chiều lông / ẩm.",
            "success_rate_vi": "Bề mặt nhẹ: trung bình. Ướt / ngấm: thấp.",
            "refuse_when_vi": "Đòi giặt nước / cồn nhiều / ép xử lý tại quán → từ chối.",
        }

    return {
        "precheck_ko": f"{kind}: 물 금지. 스웨이드 브러시·전용 제품만.",
        "why_ko": "[왜 이 순서] 스웨이드는 물·일반 크림이 위험. 마른 관리·전용 스프레이.",
        "fresh_path_ko": (
            "(1)마른 스웨이드 브러시로 결 따라. "
            "(2)유분: 전용 이레이서/고무. "
            "(3)스웨이드 프로텍터만(선택). "
            "(4)물·평활용 클리너/크림·세탁기 금지."
        ),
        "dried_path_ko": "이미 물얼룩: 전문.",
        "motion_ko": "약하게 마른 솔.",
        "water_temp_ko": "물 금지.",
        "aftercare_ko": "통풍 보관.",
        "sense_check_ko": "눈: 물얼룩. 손: 결.",
        "success_rate_ko": "마른 관리: 양호. 물 사고: 전문.",
        "refuse_when_ko": "물세탁 요구 → 거절.",
        "precheck_vi": f"{kind_vi}: CẤM nước. Chỉ bàn chải / sản phẩm suede.",
        "why_vi": "[Tại sao] Suede sợ nước và kem da bóng. Chỉ chăm sóc khô / xịt suede.",
        "fresh_path_vi": (
            "(1)Chải khô theo chiều lông. "
            "(2)Dầu: eraser / cao su suede. "
            "(3)Xịt protector suede (tuỳ chọn). "
            "(4)CẤM nước / dung dịch da bóng / kem da bóng / máy giặt."
        ),
        "dried_path_vi": "Đã có vết nước → chuyên.",
        "motion_vi": "Lực nhẹ — chỉ chải khô.",
        "water_temp_vi": "CẤM nước.",
        "aftercare_vi": "Bảo quản thoáng.",
        "sense_check_vi": "Mắt: vết nước. Tay: chiều lông.",
        "success_rate_vi": "Chăm sóc khô: tốt. Sự cố nước: chuyên.",
        "refuse_when_vi": "Đòi giặt nước → từ chối.",
    }


def leather_chemicals_for(item_id: str, *, mold: bool = False) -> list[dict]:
    """Executable chemicals[] for leather item answers."""
    if item_id in SUEDE_IDS:
        return []  # suede: tools only; no L1 water cleaner as default
    out = []
    by = {c["code"]: c for c in LEATHER_CHEM_SEED}
    if mold:
        a1 = {
            "code": "A1",
            "name_ko": "이소프로필 알코올(소독용)",
            "name_vi": "Cồn y tế / cồn sát khuẩn 70–90%",
            "name": "Isopropyl Alcohol",
            "dilution_ko": "흰 천에 묻혀 약하게 국소만(구석 테스트) — 흠뻑·통담금 금지",
            "dilution_vi": "Thấm khăn, chấm nhẹ (test góc) — không ngâm, không ướt đẫm",
            "shop_name_vi": "Cồn sát khuẩn 70–90%",
            "buy_where_ko": "약국·마트",
            "buy_where_vi": "Nhà thuốc / siêu thị",
            "when_use_ko": "평활 가죽 곰팡이 국소만. 스웨이드 금지.",
            "when_use_vi": "Da bóng + mốc: chỉ chấm cục bộ. CẤM suede.",
        }
        out.append(dict(by["L1"]))
        out.append(a1)
        out.append(dict(by["L2"]))
        out.append(dict(by["L3"]))
    else:
        out.append(dict(by["L1"]))
        out.append(dict(by["L2"]))
        out.append(dict(by["L3"]))
    return out


def leather_tool_ids(item_id: str, *, mold: bool = False) -> list[str]:
    if item_id in SUEDE_IDS:
        return ["T_BRUSH_SOFT", "T_CLOTH"] + (["T_MASK", "T_GLOVE_NITRILE"] if mold else [])
    ids = ["T_CLOTH"]
    if mold:
        ids = ["T_GLOVE_NITRILE", "T_MASK", "T_CLOTH", "T_BRUSH_SOFT"]
    return ids


def apply_leather_education(graph: dict, entities: Optional[dict] = None) -> dict:
    """Merge leather education into graph when item is leather/suede family."""
    if not isinstance(graph, dict):
        return graph
    entities = entities or {}
    ic = graph.get("item_context") or {}
    item_id = str(ic.get("id") or entities.get("item_id") or "")
    if item_id not in LEATHER_FAMILY_IDS:
        return graph

    sc = graph.get("stain_context") or {}
    stain_id = ""
    if isinstance(sc, dict):
        cand = str(sc.get("id") or entities.get("stain_id") or "")
        if cand.startswith("S_"):
            stain_id = cand
    mold = _is_mold(stain_id, entities)

    edu = education_for(item_id, stain_id=stain_id, entities=entities)
    if not edu:
        return graph

    out = dict(graph)
    sc2 = dict(sc) if isinstance(sc, dict) else {}
    for k, v in edu.items():
        if v:
            sc2[k] = v
    if mold:
        sc2["contains_protein"] = False
        sc2["chemistry_note_ko"] = "곰팡이=포자·색소(단백질 얼룩 아님). 가죽: 통담금·표백 금지."
        sc2["chemistry_note_vi"] = (
            "Mốc = bào tử/sắc tố (không phải vết đạm). Da: CẤM ngâm / tẩy."
        )
    out["stain_context"] = sc2

    out["chemicals"] = leather_chemicals_for(item_id, mold=mold)
    out["washfriends_supply"] = []
    out["empty_chems_ok"] = item_id in SUEDE_IDS or not out["chemicals"]
    if item_id in SUEDE_IDS:
        out["chem_forbid_ko"] = (
            "스웨이드: chemicals[] 비어 있음이 정상. (4)에 식초·산소/염소표백·가죽클리너·물약품을 "
            "지어내지 말 것. 마른 솔·전문만."
        )
        out["chem_forbid_vi"] = (
            "Suede: để trống hóa chất là đúng. "
            "CẤM bịa giấm / bột tẩy oxy / Javel / dung dịch da bóng vào mục (4). "
            "Chỉ bàn chải khô hoặc chuyển chuyên."
        )

    want = leather_tool_ids(item_id, mold=mold)
    stubs = {
        "T_CLOTH": {"id": "T_CLOTH", "name_ko": "흰 천·흡수지", "name_vi": "Khăn trắng sạch"},
        "T_BRUSH_SOFT": {"id": "T_BRUSH_SOFT", "name_ko": "연질 솔", "name_vi": "Bàn chải mềm"},
        "T_GLOVE_NITRILE": {
            "id": "T_GLOVE_NITRILE",
            "name_ko": "니트릴 장갑",
            "name_vi": "Găng nitrile (bảo hộ)",
        },
        "T_MASK": {"id": "T_MASK", "name_ko": "마스크", "name_vi": "Khẩu trang"},
    }
    have = {str(t.get("id") or ""): t for t in (out.get("tools") or []) if t}
    tools = []
    for tid in want:
        base = have.get(tid) or stubs.get(tid) or {"id": tid}
        tools.append(dict(base))
    out["tools"] = _narrate_leather_tools(tools, item_id=item_id, mold=mold)
    out["leather_care"] = True
    out["protocol_mode"] = "item_primary"
    try:
        from vi_text_canon import sanitize_education_vi_fields

        out = sanitize_education_vi_fields(out)
    except Exception:
        pass
    return out


def _narrate_leather_tools(tools: list, *, item_id: str, mold: bool) -> list:
    out = []
    for t in tools:
        t = dict(t)
        tid = str(t.get("id") or "")
        if tid == "T_CLOTH":
            if item_id in SUEDE_IDS:
                t["use_for_ko"] = "스웨이드: 마른 천만(선택). 물 적신 천으로 문지르기 금지."
                t["use_for_vi"] = "Suede: chỉ khăn khô — CẤM khăn ướt chà."
                t["use_for_en"] = "Suede: dry cloth only — never wet wipe/scrub."
            elif mold:
                t["use_for_ko"] = (
                    "평활 가죽 곰팡이: ①마른 천으로 포자 털기 ②약품은 천에 묻혀 약하게 국소 찍기 "
                    "(흠뻑 금지) ③물기 천으로 잔여만. 천 물들면 교체."
                )
                t["use_for_vi"] = (
                    "Da bóng + mốc: phủi khô → thấm hóa chất nhẹ trên khăn → lau dư. "
                    "Đổi khăn khi bẩn."
                )
                t["use_for_en"] = (
                    "Smooth leather mold: dry wipe spores → light chem on cloth → wipe residue."
                )
            else:
                t["use_for_ko"] = (
                    "평활 가죽: 클리너·크림을 천에 묻혀 약하게 닦기/바르기. "
                    "섬유 얼룩용 '바깥→안 블롯'만 반복하지 말 것."
                )
                t["use_for_vi"] = (
                    "Da bóng: dung dịch vệ sinh da / kem dưỡng trên khăn, lau nhẹ — "
                    "không chỉ thấm như vải."
                )
                t["use_for_en"] = (
                    "Smooth leather: apply cleaner/cream on cloth lightly — not textile blot-only."
                )
        elif tid == "T_BRUSH_SOFT":
            if item_id in SUEDE_IDS:
                t["use_for_ko"] = "스웨이드: 결 따라 약하게 마른 솔만 — 물·세게 문지르기 금지."
                t["use_for_vi"] = "Suede: chải khô nhẹ theo chiều lông — CẤM nước."
                t["use_for_en"] = "Suede: dry light brush with nap — no water/scrubbing."
            elif mold:
                t["use_for_ko"] = (
                    "가죽 곰팡이: 마스크 후 마른 포자만 약하게 살살 털기 — "
                    "문지르면 포자 확산. 그다음 천+약품."
                )
                t["use_for_vi"] = (
                    "Mốc da: khẩu trang; phủi bào tử khô nhẹ — không chà. Sau đó khăn + hóa chất."
                )
                t["use_for_en"] = "Leather mold: mask on; dry-brush spores lightly — then cloth+chem."
            else:
                t["use_for_ko"] = "평활 가죽: 보통 솔보다 천 우선. 먼지 털 때만 약하게."
                t["use_for_vi"] = "Da bóng: ưu tiên khăn; chải bụi nhẹ nếu cần."
                t["use_for_en"] = "Smooth leather: prefer cloth; light brush dust only if needed."
        elif tid == "T_GLOVE_NITRILE":
            t["use_for_ko"] = "곰팡이·약품 전 필수. 병·포자 만지기 전 착용."
            t["use_for_vi"] = "BẮT BUỘC trước khi đụng mốc / hóa chất."
            t["use_for_en"] = "Required before mold/chemicals."
        elif tid == "T_MASK":
            t["use_for_ko"] = "곰팡이 포자 흡입 방지 — 야외·환기와 함께."
            t["use_for_vi"] = "Khẩu trang chống bào tử — ngoài trời / chỗ thoáng."
            t["use_for_en"] = "Mask against spores — outdoors/ventilated."
        out.append(t)
    return out
