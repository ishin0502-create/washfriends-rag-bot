# -*- coding: utf-8 -*-
"""Leather / suede franchise education — care, mold, cream, protector.

Item-primary garments already win over textile stain SOPs. This module
supplies rich KO/VI fields + L1/L2/L3 chemicals so mold answers are not
generic cloth-blot + alcohol only.
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
        "name_vi": "Dung dich ve sinh da (leather cleaner)",
        "name_ko": "가죽 전용 클리너",
        "role": "pH-balanced leather surface cleaner — minimal water",
        "safe_on_wool": False,
        "safe_on_silk": False,
        "shop_name_vi": "Dung dich/xit ve sinh da (leather cleaner)",
        "buy_where_vi": "Cua do da, sieu thi do gia dung / giay",
        "buy_where_ko": "구두·가죽용품점, 대형마트 신발케어 코너",
        "alt1_vi": "Xa phong da (leather soap) pha rat loang",
        "alt2_vi": "Khan am + xa phong trung tinh cuc it (test)",
        "alt3_vi": "Het hang: chi lau am nhe — CAM bot giat/Javel",
        "alt1_ko": "가죽비누(leather soap) 아주 약하게 희석",
        "alt2_ko": "중성세제 극소량+미지근한 천(구석 테스트)",
        "alt3_ko": "없으면 미지근한 천만 — 일반세제·락스·산소표백 금지",
        "example_brands_vi": "",
        "wf_supply": False,
        "when_use_vi": "Da bong: lau vet / bao duong. CAM suede/nubuck nuoc.",
        "when_use_ko": "평활 가죽 표면 청소·오염 제거. 스웨이드·누벅에는 물/클리너 금지.",
        "dilution_vi": "Theo nhan chai — it nuoc, khan, khong ngam",
        "dilution_ko": "병 안내 따름 — 천에 묻혀 국소만, 통담금·세탁기 금지",
    },
    {
        "code": "L2",
        "name": "Leather cream / conditioner",
        "name_vi": "Kem duong da (leather cream/conditioner)",
        "name_ko": "가죽 크림·컨디셔너",
        "role": "Restore oils after clean/mold — prevents dryness/cracking",
        "safe_on_wool": False,
        "safe_on_silk": False,
        "shop_name_vi": "Kem da / conditioner da / cream leather",
        "buy_where_vi": "Cua do da, cua giay",
        "buy_where_ko": "구두·가죽용품점",
        "alt1_vi": "Leather balm / balsam",
        "alt2_vi": "Mink oil chi khi nhan cho (co the toi mau)",
        "alt3_vi": "CAM boi dau an / vaseline len ao da (bui bam)",
        "alt1_ko": "레더 밤·밤삼",
        "alt2_ko": "밍크오일(라벨 허용 시만 — 어두워질 수 있음 고지)",
        "alt3_ko": "식용유·바셀린 금지(먼지 흡착·얼룩)",
        "example_brands_vi": "",
        "wf_supply": False,
        "when_use_vi": "BAT BUOC sau khi xu ly moc/vet tren da bong — khi da KHO.",
        "when_use_ko": "평활 가죽: 클리너/곰팡이 처리 후 완전 건조 뒤 필수 보습.",
        "dilution_vi": "Nguyen chat — boi mong, deu, lau du",
        "dilution_ko": "원액 얇게 펴 바르고 천으로 잉여 닦기 — 두껍게 바르지 말 것",
    },
    {
        "code": "L3",
        "name": "Leather protector",
        "name_vi": "Xit bao ve da (protector/water repellent)",
        "name_ko": "가죽 프로텍터(방수·오염방지)",
        "role": "Optional water/stain repellent after cream cured",
        "safe_on_wool": False,
        "safe_on_silk": False,
        "shop_name_vi": "Xit chong tham / protector da-giay",
        "buy_where_vi": "Cua giay, sieu thi",
        "buy_where_ko": "구두용품점·마트 신발케어",
        "alt1_vi": "Bo qua neu khach khong can",
        "alt2_vi": "Suede: chi xit suede/nubuck rieng",
        "alt3_vi": "Thong gio khi xit",
        "alt1_ko": "고객이 원치 않으면 생략",
        "alt2_ko": "스웨이드는 스웨이드 전용 스프레이만",
        "alt3_ko": "환기 후 분무",
        "example_brands_vi": "",
        "wf_supply": False,
        "when_use_vi": "Sau kem da kho — bao ve. Khong thay the kem duong.",
        "when_use_ko": "크림이 마른 뒤 선택. 크림 대체가 아님.",
        "dilution_vi": "Xit nhe 20-30cm, de kho theo nhan",
        "dilution_ko": "20–30cm에서 약분무, 병 안내대로 건조",
    },
]


def _is_mold(stain_id: str, entities: Optional[dict] = None) -> bool:
    sid = str(stain_id or "").upper()
    if sid == "S_MILDEW":
        return True
    raw = str((entities or {}).get("_raw") or "")
    return any(k in raw for k in ("곰팡이", "곰팡", "mold", "mildew", "nam moc", "nấm mốc"))


def education_for(item_id: str, *, stain_id: str = "", entities: Optional[dict] = None) -> dict[str, str]:
    """Return path/teach fields to merge into stain_context / item_context."""
    mold = _is_mold(stain_id, entities)
    if item_id in SUEDE_IDS:
        return _suede_card(item_id, mold=mold)
    if item_id in LEATHER_SMOOTH_IDS:
        return _smooth_card(item_id, mold=mold)
    return {}


def _smooth_card(item_id: str, *, mold: bool) -> dict[str, str]:
    kind = {
        "I_LEATHER_GARMENT": "가죽 의류(평활)",
        "I_LEATHER_BAG": "가죽 가방·지갑",
        "I_LEATHER_SHOE": "가죽 구두",
        "I_GLOVE_LEATHER": "가죽 장갑",
        "I_GOLF_GLOVE_LEATHER": "골프 가죽장갑",
    }.get(item_id, "평활 가죽")

    if mold:
        return {
            "precheck_ko": (
                f"{kind}: 평활 가죽인지 스웨이드/누벅인지 먼저 확인. "
                "야외·환기. 마스크·니트릴 장갑. 사진·동의(100% 복원 약속 금지)."
            ),
            "why_ko": (
                "[왜 이 순서] 가죽 곰팡이=표면 포자+습도. 섬유용 식초 통담금·산소/락스·세탁기는 "
                "가죽을 굳히거나 갈라지게 함. 순서: PPE→마른 털기→국소 소독(클리너/알코올 Cap1)→"
                "완전 건조→가죽 크림 필수→(선택)프로텍터. 깊게 침투·갈라짐→전문."
            ),
            "fresh_path_ko": (
                "(1)스웨이드면 이 경로 중단→스웨이드 SOP/전문. "
                "(2)야외에서 마스크·장갑 착용. "
                "(3)마른 부드러운 천/솔로 표면 포자만 Cap1로 살살 털기(문지르기 금지). "
                "(4)가죽 전용 클리너(L1) 또는 소독용 알코올 70%를 흰 천에 묻혀 구석 테스트 후 "
                "바깥→안 Cap1로 국소 찍기 — 흠뻑·통담금·식초 담금·표백 금지. "
                "(5)물기 남은 천으로 잔여만 닦고 그늘에서 완전 건조(형태 유지). "
                "(6)마른 뒤 가죽 크림(L2) 얇게 → 잉여 닦기. "
                "(7)필요 시 프로텍터(L3) 약분무. "
                "(8)냄새·반점 남거나 갈라짐→전문·거절."
            ),
            "dried_path_ko": (
                "이미 마른 곰팡이·넓은 면적: 같은 순서 반복 1회만. "
                "안감까지 침투·가죽 갈라짐·고가 → 가정 추가 처리 중단, 전문."
            ),
            "motion_ko": "Cap1만 — 찍기·털기. 문지르기·흔들어 '치료' 금지.",
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
                f"{kind}: phan biet da bong vs suede. Ngoai troi+PPE. Anh+dong y (khong 100%)."
            ),
            "why_vi": (
                "[Tại sao] Moc tren da — CAM ngam giấm/oxy/Javel/may. "
                "PPE → phui kho → L1/con Cap1 → kho → L2 kem da → L3 tuy chon."
            ),
            "fresh_path_vi": (
                "(1)Suede → dung. (2)PPE ngoai troi. (3)Phui kho Cap1. "
                "(4)L1 hoac con 70% cham Cap1 (test) — CAM ngam. "
                "(5)Kho bong mat. (6)L2. (7)L3 neu can. (8)Sau long → chuyen."
            ),
            "dried_path_vi": "Dien rong/nut → chuyen chuyen nghiep.",
            "motion_vi": "Cap1 — cham/phui, khong cha.",
            "water_temp_vi": "It nuoc, nhiet phong. CAM may/ngam.",
            "aftercare_vi": "Kem da bat buoc khi kho. CAM say/nang/ui.",
            "sense_check_vi": "Mat: vet trang. Mui: moc. Tay: nut.",
            "success_rate_vi": "Be mat som: tot. Sau long: thap.",
            "refuse_when_vi": "Suede/may/nut sau → tu choi.",
        }

    # Routine / general leather care (P1)
    shoe_bit_ko = (
        " 구두: 신문지·키친타월로 형태 유지. 끈 있으면 빼서 별도(갑피만 국소)."
        if item_id == "I_LEATHER_SHOE"
        else ""
    )
    shoe_bit_vi = (
        " Giay: nho bao giu form. Thao day neu co."
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
            "클리너(L1)로 표면 → 완전 건조 → 크림(L2) 보습 → (선택)프로텍터(L3). "
            "얼룩은 국소만. 「일반·통세탁」 금지. 곰팡이는 별도 곰팡이 SOP."
        ),
        "fresh_path_ko": (
            "(1)먼지는 마른 천으로."
            f"{shoe_bit_ko} "
            "(2)가죽 전용 클리너(L1)를 천에 묻혀 Cap1로 닦기 → 젖은 천으로 잔여. "
            "(3)그늘에서 완전 건조(형태 유지 — 구두면 신문지). "
            "(4)가죽 크림(L2) 얇게 → 광택·잉여 닦기. "
            "(5)비·오염 많은 환경이면 프로텍터(L3) 약분무. "
            "(6)유분·잉크 등 얼룩: 국소만(과다 용제 금지) → 다시 크림. "
            "(7)세탁기·통담금·표백·고온건조 금지."
        ),
        "dried_path_ko": "이미 hardened/갈라짐: 크림 시도 1회 → 안 되면 전문. 강제 세탁 금지.",
        "motion_ko": "Cap1 — 닦기·바르기. 세게 문지르기 금지.",
        "water_temp_ko": "물 최소·실온. 세탁기·온수 금지.",
        "aftercare_ko": "통풍 보관·제습. 직사광선·히터 근처 금지. 주기적 크림.",
        "sense_check_ko": "눈: 얼룩·백화. 손: 건조·갈라짐. 코: 곰팡이 냄새 없는지.",
        "success_rate_ko": "일상 클리너+크림: 높음. 심한 곰팡이·침투: 전문.",
        "refuse_when_ko": "세탁기·표백·스웨이드에 물클리너 → 거절.",
        "must_include_ko": "세탁기 금지, 가죽 크림, 최소 수분",
        "precheck_vi": f"{kind}: da bong (khong suede). CAM may/Javel.{shoe_bit_vi}",
        "why_vi": (
            "[Tai sao] Da bong yeu nuoc/nhiet/tay. Vong cham soc: L1 → kho → L2 → (L3). "
            "CAM giat may / ngam / goi la 'giat thong thuong'."
        ),
        "fresh_path_vi": (
            "(1)Phui kho."
            f"{shoe_bit_vi} "
            "(2)L1 Cap1 tren khan → lau du. (3)Kho bong mat (giay: nho bao). "
            "(4)L2 mong. (5)L3 tuy chon. (6)Vet: chi cuc bo. (7)CAM may/ngam/tay/say nong."
        ),
        "dried_path_vi": "Nut/cung: 1 lan L2 → chuyen.",
        "motion_vi": "Cap1 lau/boi.",
        "water_temp_vi": "It nuoc. CAM may.",
        "aftercare_vi": "Kho thoang + kem dinh ky.",
        "sense_check_vi": "Mat/tay/mui.",
        "success_rate_vi": "Cham soc: cao. Moc sau: thap.",
        "refuse_when_vi": "May/tay oxy/suede nuoc → tu choi.",
        "must_include_vi": "CAM may giat, kem da, it nuoc",
        "precheck_en": (
            f"{kind}: confirm smooth leather (not suede). Refuse washer/dryer/bleach."
            f"{shoe_bit_en}"
        ),
        "why_en": (
            "[Why this order] Smooth leather hates water/heat/bleach. Loop: "
            "cleaner (L1) → dry fully → cream (L2) → optional protector (L3). "
            "Spot only — never machine-wash / soak."
        ),
        "fresh_path_en": (
            "(1)Dust with dry cloth."
            f"{shoe_bit_en} "
            "(2)Leather cleaner (L1) on cloth Cap1 → wipe residue. "
            "(3)Air-dry in shade (stuff shoes with paper). "
            "(4)Thin leather cream (L2). (5)Optional protector (L3). "
            "(6)Stains: local only. (7)No washer, soak, bleach, or hot dryer."
        ),
        "dried_path_en": "Hardened/cracked: one cream try → refer out. No forced wash.",
        "motion_en": "Cap1 wipe/apply only — no scrubbing.",
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
                "(1)PPE·야외. "
                "(2)스웨이드 브러시/부드러운 솔로 결 따라 Cap1 마른 털기만. "
                "(3)스웨이드 전용 이레이서·전용 스프레이만(라벨). "
                "(4)물·식초·표백·세탁기·평활용 크림 금지. "
                "(5)안 되면 즉시 전문·거절."
            ),
            "dried_path_ko": "젖은 채 곰팡이·넓은 면적: 가정 처리 중단, 전문.",
            "motion_ko": "Cap1 마른 솔 — 물로 문지르기 금지.",
            "water_temp_ko": "물 사용 금지.",
            "aftercare_ko": "완전 건조·통풍. 스웨이드 프로텍터만(해당 시).",
            "sense_check_ko": "눈: 반점. 손: 결·수분.",
            "success_rate_ko": "가벼운 표면: 중간. 젖음·침투: 낮음.",
            "refuse_when_ko": "물세탁·알코올 과다·가정 강처리 요구 → 거절.",
            "precheck_vi": "Suede: CAM nuoc. PPE. Rong → chuyen.",
            "why_vi": "[Tại sao] Suede + nuoc = vet. Chi chai kho.",
            "fresh_path_vi": "(1)PPE. (2)Chai kho Cap1. (3)Chi san pham suede. (4)CAM nuoc/kem da. (5)Chuyen.",
            "dried_path_vi": "Uot/rong → chuyen.",
            "motion_vi": "Cap1 chai kho.",
            "water_temp_vi": "CAM nuoc.",
            "aftercare_vi": "Kho thoang. Protector suede neu co.",
            "sense_check_vi": "Mat/tay.",
            "success_rate_vi": "Be mat: TB. Uot: thap.",
            "refuse_when_vi": "Bat nuoc/may → tu choi.",
        }

    return {
        "precheck_ko": f"{kind}: 물 금지. 스웨이드 브러시·전용 제품만.",
        "why_ko": "[왜 이 순서] 스웨이드는 물·일반 크림이 위험. 마른 관리·전용 스프레이.",
        "fresh_path_ko": (
            "(1)마른 스웨이드 브러시로 결 따라. "
            "(2)유분: 전용 이레이서/고무. "
            "(3)스웨이드 프로텍터만(선택). "
            "(4)물·평활용 L1/L2·세탁기 금지."
        ),
        "dried_path_ko": "이미 물얼룩: 전문.",
        "motion_ko": "Cap1 마른 솔.",
        "water_temp_ko": "물 금지.",
        "aftercare_ko": "통풍 보관.",
        "sense_check_ko": "눈: 물얼룩. 손: 결.",
        "success_rate_ko": "마른 관리: 양호. 물 사고: 전문.",
        "refuse_when_ko": "물세탁 요구 → 거절.",
        "precheck_vi": "Suede: CAM nuoc.",
        "why_vi": "[Tại sao] Chi chai kho / san pham suede.",
        "fresh_path_vi": "(1)Chai kho. (2)Eraser. (3)Protector suede. (4)CAM nuoc/L1.",
        "dried_path_vi": "Vet nuoc → chuyen.",
        "motion_vi": "Cap1 kho.",
        "water_temp_vi": "CAM nuoc.",
        "aftercare_vi": "Kho thoang.",
        "sense_check_vi": "Mat.",
        "success_rate_vi": "Kho: tot.",
        "refuse_when_vi": "May/nuoc → tu choi.",
    }


def leather_chemicals_for(item_id: str, *, mold: bool = False) -> list[dict]:
    """Executable chemicals[] for leather item answers."""
    if item_id in SUEDE_IDS:
        return []  # suede: tools only; no L1 water cleaner as default
    out = []
    by = {c["code"]: c for c in LEATHER_CHEM_SEED}
    if mold:
        # Spot sanitize + mandatory cream after — cream listed early so (4) does not drop it
        a1 = {
            "code": "A1",
            "name_ko": "이소프로필 알코올(소독용)",
            "name_vi": "Cồn isopropyl 70%",
            "name": "Isopropyl Alcohol",
            "dilution_ko": "흰 천에 묻혀 Cap1 국소만(구석 테스트) — 흠뻑·통담금 금지",
            "dilution_vi": "Chấm khăn Cap1 (test góc) — không ngâm",
            "shop_name_vi": "Cồn sát khuẩn 70-90%",
            "buy_where_ko": "약국·마트",
            "when_use_ko": "평활 가죽 곰팡이 국소만. 스웨이드 금지.",
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
        # item_care shapes put I_* into id — ignore
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
    out["stain_context"] = sc2

    # Replace textile soak chem kits with leather L1/L2/L3 (+A1 if mold)
    out["chemicals"] = leather_chemicals_for(item_id, mold=mold)
    out["washfriends_supply"] = []
    # Suede: intentionally empty shop chems — never invent vinegar/bleach in (4)
    out["empty_chems_ok"] = item_id in SUEDE_IDS or not out["chemicals"]
    if item_id in SUEDE_IDS:
        out["chem_forbid_ko"] = (
            "스웨이드: chemicals[] 비어 있음이 정상. (4)에 식초·산소/염소표백·가죽클리너·물약품을 "
            "지어내지 말 것. 마른 솔·전문만."
        )
        out["chem_forbid_vi"] = (
            "Suede: chemicals[] rỗng là đúng. CẤM bịa giấm/oxy/Javel/L1 vào (4). Chỉ chai khô / chuyên."
        )

    # Tools: only leather kit (do not keep seed PPE on routine care)
    want = leather_tool_ids(item_id, mold=mold)
    stubs = {
        "T_CLOTH": {"id": "T_CLOTH", "name_ko": "흰 천·흡수지", "name_vi": "Khăn trắng"},
        "T_BRUSH_SOFT": {"id": "T_BRUSH_SOFT", "name_ko": "연질 솔", "name_vi": "Bàn chải mềm"},
        "T_GLOVE_NITRILE": {"id": "T_GLOVE_NITRILE", "name_ko": "니트릴 장갑(PPE)", "name_vi": "Găng nitrile"},
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
    return out


def _narrate_leather_tools(tools: list, *, item_id: str, mold: bool) -> list:
    out = []
    for t in tools:
        t = dict(t)
        tid = str(t.get("id") or "")
        if tid == "T_CLOTH":
            if item_id in SUEDE_IDS:
                t["use_for_ko"] = "스웨이드: 마른 천만(선택). 물 적신 천으로 문지르기 금지."
                t["use_for_vi"] = "Suede: chỉ khăn khô — CAM khăn ướt chà."
            elif mold:
                t["use_for_ko"] = (
                    "평활 가죽 곰팡이: ①마른 천으로 포자 털기 ②약품은 천에 묻혀 Cap1 국소 찍기 "
                    "(흠뻑 금지) ③물기 천으로 잔여만. 천 물들면 교체."
                )
                t["use_for_vi"] = (
                    "Da bong+mốc: phui khô → chấm hóa chất Cap1 trên khăn → lau dư. Đổi khăn khi bẩn."
                )
            else:
                t["use_for_ko"] = (
                    "평활 가죽: 클리너·크림을 천에 묻혀 Cap1로 닦기/바르기. "
                    "섬유 얼룩용 '바깥→안 블롯'만 반복하지 말 것."
                )
                t["use_for_vi"] = "Da bong: L1/L2 trên khăn Cap1 — không chỉ blot như vải."
                t["use_for_en"] = "Smooth leather: apply L1/L2 on cloth Cap1 — not textile blot-only."
        elif tid == "T_BRUSH_SOFT":
            if item_id in SUEDE_IDS:
                t["use_for_ko"] = "스웨이드: 결 따라 Cap1 마른 솔만 — 물·세게 문지르기 금지."
                t["use_for_vi"] = "Suede: Cap1 chai khô theo chiều lông — CAM nước."
                t["use_for_en"] = "Suede: dry Cap1 brush with nap — no water/scrubbing."
            elif mold:
                t["use_for_ko"] = (
                    "가죽 곰팡이: 마스크 후 마른 포자만 Cap1로 살살 털기 — "
                    "문지르면 포자 확산. 그다음 천+약품."
                )
                t["use_for_vi"] = "Mốc da: khẩu trang; phủi bào tử khô Cap1 — không chà."
                t["use_for_en"] = "Leather mold: mask on; dry Cap1 brush spores — then cloth+chem."
            else:
                t["use_for_ko"] = "평활 가죽: 보통 솔보다 천 우선. 먼지 털 때만 Cap1."
                t["use_for_vi"] = "Da bong: ưu tiên khăn; chải bụi Cap1 nếu cần."
                t["use_for_en"] = "Smooth leather: prefer cloth; Cap1 brush dust only if needed."
        elif tid == "T_GLOVE_NITRILE":
            t["use_for_ko"] = "곰팡이·약품 전 필수. 병·포자 만지기 전 착용."
            t["use_for_vi"] = "BẮT BUỘC trước mốc/hóa chất."
            t["use_for_en"] = "Required before mold/chemicals."
        elif tid == "T_MASK":
            t["use_for_ko"] = "곰팡이 포자 흡입 방지 — 야외·환기와 함께."
            t["use_for_vi"] = "Khẩu trang chống bào tử — ngoài trời/thoáng."
            t["use_for_en"] = "Mask against spores — outdoors/ventilated."
        out.append(t)
    return out
