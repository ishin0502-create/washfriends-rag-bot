# -*- coding: utf-8 -*-
"""Specialty item care (not stain spotting): duvet, down, hotel linen, machines.

Truth sources: kb/laundry_kb_v3_items_home.md, items_clothing.md (DOWNCARE),
tools_equipment.md washer/dryer guides — rendered as owner KO cards.
"""
from __future__ import annotations

from typing import Any, Optional

from process_stage_care import (
    PROCESS_STAGE_IDS,
    apply_process_stage_hints,
    education_for_process,
)
from specialty_garment_care import (
    GARMENT_SPECIALTY_IDS,
    apply_garment_specialty_hints,
    education_for_garment,
)
from specialty_cultural_care import (
    CULTURAL_SPECIALTY_IDS,
    apply_cultural_specialty_hints,
    education_for_cultural,
)
from fabric_care import (
    FABRIC_CURRICULUM_IDS,
    apply_fabric_curriculum_hints,
    education_for_fabric,
)
from chem_safety_care import (
    CHEM_SAFETY_IDS,
    apply_chem_safety_hints,
    education_for_chem_safety,
)
from specialty_ops_remainder_care import (
    OPS_REMAINDER_IDS,
    apply_ops_remainder_hints,
    education_for_ops_remainder,
)


SPECIALTY_CARE_IDS = frozenset({
    "I_DUVET_GOOSE",
    "I_DUVET_COTTON",
    "I_DOWN_JACKET",
    "I_BED_SHEET",
    "I_TOWEL",
    "I_MACHINE_PROFILE",
    "I_FUR_REAL",
    "I_FUR_FAUX",
    "I_DRY_VS_WET",
    "I_FAUX_LEATHER",
    "I_SNEAKER_WHITE",
    "I_SHOE_LACES",
    "I_SNEAKER",
    "I_HAT_CAP",
    "I_GOLF_HAT",
    "I_LINEN_GARMENT",
    "I_FINISHING",
    "I_SUIT",
    "I_SUIT_SUMMER",
    "I_DRESS",
    "I_DRESS_SHIRT",
    *PROCESS_STAGE_IDS,
    *GARMENT_SPECIALTY_IDS,
    *CULTURAL_SPECIALTY_IDS,
    *FABRIC_CURRICULUM_IDS,
    *CHEM_SAFETY_IDS,
    *OPS_REMAINDER_IDS,
})


def _raw(entities: Optional[dict]) -> str:
    return str((entities or {}).get("_raw") or "")


def _wants_finishing(entities: Optional[dict]) -> bool:
    raw = _raw(entities)
    return any(
        k in raw
        for k in (
            "다림질", "스팀", "에어드레서", "에어 드레서", "피니싱", "다림",
            "airdresser", "air dresser", "steam iron", "ui ", "ủi",
        )
    )


def _is_wedding(entities: Optional[dict]) -> bool:
    raw = _raw(entities)
    return any(k in raw for k in ("웨딩", "웨딩드레스", "결혼", "bridal", "wedding"))


def _is_whitening(entities: Optional[dict]) -> bool:
    raw = _raw(entities)
    return any(
        k in raw
        for k in (
            "하얗게", "누렇게", "황변", "흰창", "미드솔", "midsole", "화이트닝",
            "옆면", "고무창", "whitening", "vang de",
        )
    )


def _is_hotel(entities: Optional[dict]) -> bool:
    raw = _raw(entities)
    return any(k in raw for k in ("호텔", "hotel", "린넨", "객실", "업소용"))


def _is_biohazard_heavy(entities: Optional[dict]) -> bool:
    raw = _raw(entities)
    return any(
        k in raw
        for k in (
            "피", "혈액", "토", "구토", "소변", "대변", "생체", "biohazard",
            "vomit", "urine", "blood", "mau", "chat non",
        )
    )


def _default_must_include(item_id: str, edu: dict[str, str]) -> str:
    """Phrases the owner LLM must not drop when summarizing specialty cards."""
    presets = {
        "I_DUVET_GOOSE": "대형 전면투입, 추가 헹굼, 테니스볼, 퍼크 금지",
        "I_DUVET_COTTON": "대형기, 추가 헹굼, 테니스볼",
        "I_DOWN_JACKET": "전면투입, 추가 헹굼, 테니스볼",
        "I_FAUX_LEATHER": "진가죽과 구분, 세탁기 금지, 진가죽 크림 금지",
        "I_SNEAKER_WHITE": "베이킹소다, 락스 금지, 100% 복원 불가",
        "I_SHOE_LACES": "끈 분리, 그늘 건조, 교체 안내",
        "I_HAT_CAP": "챙 국소, 형태 유지, 건조기 금지",
        "I_GOLF_HAT": "챙 국소, 형태 유지, 건조기 금지",
        "I_LINEN_GARMENT": "수축 고지, 30–40℃, 다림질",
        "I_FINISHING": "에어드레서, 스팀, 잔여 얼룩 금지",
        "I_SUIT": "스팀, 에어드레서, 판 직접 접촉 금지",
        "I_SUIT_SUMMER": "스팀, 에어드레서, 촉촉할 때 다림질",
        "I_DRESS": "스팀, 비즈 판 금지, 에어드레서 한계",
        "I_DRESS_SHIRT": "깃→커프→소매→몸, 에어드레서 보조",
        "I_SORT": "흰/유색/섬세 분리, 수건·바이오해저드 별도, 이염 예방",
        "I_RINSE": "추가 헹굼, 잔여 세제 제거, 경수 시 보정, 유연제 대체 금지",
        "I_QC_HANDOVER": "강광 잔여 확인, 접수 사진 대조, 한계 고지, 출고 체크리스트",
        "I_CURTAIN_FABRIC": "치수 기록, ~30℃, 축축할 때 걸기, 유색 락스 금지",
        "I_CURTAIN_URETHANE": "코팅 구분, 국소 중성, 기계·건조기·아세톤 주의",
        "I_DENIM": "뒤집기, 찬물, 흰옷 분리, 첫 물빠짐 정상",
        "I_GORETEX": "세제 소량, 유연제 금지, 추가 헹굼, DWR",
        "I_BABY_WEAR": "성인 분리, 찬물 단백질, 추가 헹굼, 무향",
        "I_SWIMWEAR": "즉시 찬물 헹굼, 찬물만, 건조기 금지",
        "I_GOLF_WEAR": "≤30℃, 유연제 금지, 뒤집기",
        "I_GOLF_SHOE": "끈·깔창 분리, 그늘 건조, 고온건조 금지",
        "I_HIKING_SHOE": "끈·깔창 분리, ≤30℃, 고온건조 금지, DWR 선택",
        "I_RUNNING_MESH": "세탁망, 연질만, ≤30℃, 고온건조 금지",
    }
    if item_id in presets:
        return presets[item_id]
    blob = " ".join(str(edu.get(k) or "") for k in ("fresh_path_ko", "why_ko", "aftercare_ko"))
    bits = []
    for token in (
        "테니스볼", "건조볼", "대형 전면투입", "추가 헹굼", "에어드레서",
        "수축", "락스", "100%", "진가죽 크림",
    ):
        if token in blob:
            bits.append(token)
    return ", ".join(bits)


def _has_stain_cue(entities: Optional[dict]) -> bool:
    """True when owner mentioned a stain/odor — not a plain 'how to wash' question."""
    raw = _raw(entities)
    if (entities or {}).get("stain_id") or (entities or {}).get("stain_type"):
        return True
    return any(
        k in raw
        for k in (
            "얼룩", "묻었", "묻은", "오염", "피 ", "혈액", "커피", "와인", "곰팡이",
            "냄새", "토", "구토", "소변", "황변", "기름", "김치", "잉크",
            "vet ", "mau ", "moc", "mui ",
        )
    )


def education_for(item_id: str, *, entities: Optional[dict] = None) -> dict[str, str]:
    hotel = _is_hotel(entities)
    bio = _is_biohazard_heavy(entities)
    finish = _wants_finishing(entities)
    stain = _has_stain_cue(entities)
    if item_id == "I_DUVET_GOOSE":
        return _goose_duvet(has_stain=stain)
    if item_id == "I_DUVET_COTTON":
        return _cotton_duvet(has_stain=stain)
    if item_id == "I_DOWN_JACKET":
        return _down_jacket(has_stain=stain)
    if item_id == "I_TOWEL":
        return _towel(hotel=hotel, bio=bio)
    if item_id == "I_BED_SHEET":
        return _bed_sheet(hotel=hotel, bio=bio)
    if item_id == "I_MACHINE_PROFILE":
        return _machine_profile()
    if item_id == "I_FUR_REAL":
        return _fur_real()
    if item_id == "I_FUR_FAUX":
        return _fur_faux()
    if item_id == "I_DRY_VS_WET":
        return _dry_vs_wet()
    if item_id == "I_FAUX_LEATHER":
        return _faux_leather()
    if item_id == "I_SNEAKER_WHITE" or (item_id == "I_SNEAKER" and _is_whitening(entities)):
        return _sneaker_white()
    if item_id == "I_SHOE_LACES":
        return _shoe_laces()
    if item_id == "I_SNEAKER":
        return _sneaker_general()
    if item_id in {"I_HAT_CAP", "I_GOLF_HAT"}:
        return _hat_cap(golf=(item_id == "I_GOLF_HAT"))
    if item_id == "I_LINEN_GARMENT":
        return _linen_garment(finish=finish)
    if item_id == "I_FINISHING":
        return _finishing_matrix()
    if item_id in PROCESS_STAGE_IDS:
        return education_for_process(item_id)
    if item_id in GARMENT_SPECIALTY_IDS:
        return education_for_garment(item_id)
    if item_id in CULTURAL_SPECIALTY_IDS:
        return education_for_cultural(item_id)
    if item_id in FABRIC_CURRICULUM_IDS:
        return education_for_fabric(item_id)
    if item_id in CHEM_SAFETY_IDS:
        return education_for_chem_safety(item_id)
    if item_id in OPS_REMAINDER_IDS:
        return education_for_ops_remainder(item_id)
    if item_id in {"I_SUIT", "I_SUIT_SUMMER"} and finish:
        return _suit_finishing(summer=(item_id == "I_SUIT_SUMMER"))
    if item_id == "I_DRESS" and (finish or _is_wedding(entities)):
        return _dress_finishing(wedding=_is_wedding(entities))
    if item_id == "I_DRESS_SHIRT" and finish:
        return _dress_shirt_finishing()
    # Suit/dress/shirt without finishing keywords: still give wash+finish brief if item-only
    if item_id in {"I_SUIT", "I_SUIT_SUMMER"}:
        return _suit_finishing(summer=(item_id == "I_SUIT_SUMMER"))
    if item_id == "I_DRESS":
        return _dress_finishing(wedding=_is_wedding(entities))
    if item_id == "I_DRESS_SHIRT":
        return _dress_shirt_finishing()
    return {}


def apply_specialty_item_education(graph: dict, entities: Optional[dict] = None) -> dict:
    """Overwrite item_care paths with rich KO when specialty item matched."""
    if not isinstance(graph, dict):
        return graph
    entities = entities or {}
    if graph.get("leather_care"):
        return graph  # leather module already owns
    ic = graph.get("item_context") or {}
    item_id = str(ic.get("id") or entities.get("item_id") or "")
    if item_id not in SPECIALTY_CARE_IDS:
        return graph
    sc = graph.get("stain_context") or {}
    # Only reshape when item-care (no real S_* stain) OR ops cards
    real_stain = ""
    if isinstance(sc, dict) and sc.get("group") != "item_care":
        cand = str(sc.get("id") or entities.get("stain_id") or "")
        if cand.startswith("S_"):
            real_stain = cand
    # Stain+item: keep stain SOP (except machine/dry-vs-wet ops overlays).
    # Process-stage cards rely on routing guards — do NOT override a real S_* SOP.
    if real_stain and item_id not in {"I_MACHINE_PROFILE", "I_DRY_VS_WET"}:
        if item_id in {"I_TOWEL", "I_BED_SHEET"} and (_is_hotel(entities) or _is_biohazard_heavy(entities)):
            out = dict(graph)
            sc2 = dict(sc) if isinstance(sc, dict) else {}
            note = education_for(item_id, entities=entities)
            if note.get("dried_path_ko"):
                sc2["item_overlay_ko"] = note.get("dried_path_ko")
            if note.get("precheck_ko"):
                sc2["precheck_ko"] = (sc2.get("precheck_ko") or "") + " " + note["precheck_ko"]
            out["stain_context"] = sc2
            return out
        return graph

    edu = education_for(item_id, entities=entities)
    if not edu:
        return graph
    out = dict(graph)
    sc2 = dict(sc) if isinstance(sc, dict) else {}
    for k, v in edu.items():
        if v:
            sc2[k] = v
    must = edu.get("must_include_ko") or _default_must_include(item_id, edu)
    if must:
        sc2["must_include_ko"] = must
        out["must_include_ko"] = must
    if edu.get("must_include_vi"):
        sc2["must_include_vi"] = edu["must_include_vi"]
        out["must_include_vi"] = edu["must_include_vi"]
    if edu.get("must_include_en"):
        sc2["must_include_en"] = edu["must_include_en"]
        out["must_include_en"] = edu["must_include_en"]
    # Do NOT stamp tip=why_ko — sanitize picks why_{lang} so VI/EN never see Hangul tip
    sc2.pop("tip", None)
    sc2["group"] = "item_care"
    out["stain_context"] = sc2
    out["specialty_item_care"] = True
    out["protocol_mode"] = "item_primary"
    # Item wash framing (not stain spotting) for duvet/down and other specialty
    wash_ids = {
        "I_DUVET_GOOSE", "I_DUVET_COTTON", "I_DOWN_JACKET",
        "I_MACHINE_PROFILE", "I_DRY_VS_WET", "I_FINISHING",
        "I_LINEN_GARMENT", "I_FAUX_LEATHER", "I_SNEAKER", "I_SNEAKER_WHITE",
        "I_SHOE_LACES", "I_HAT_CAP", "I_GOLF_HAT",
        "I_SUIT", "I_SUIT_SUMMER", "I_DRESS", "I_DRESS_SHIRT",
        "I_FUR_REAL", "I_FUR_FAUX", "I_TOWEL", "I_BED_SHEET",
        *PROCESS_STAGE_IDS,
        *GARMENT_SPECIALTY_IDS,
        *CULTURAL_SPECIALTY_IDS,
        *FABRIC_CURRICULUM_IDS,
        *CHEM_SAFETY_IDS,
        *OPS_REMAINDER_IDS,
    }
    if item_id in wash_ids:
        out["item_wash_mode"] = True
        sc2["item_wash_mode"] = True
    if item_id in PROCESS_STAGE_IDS:
        out = apply_process_stage_hints(out, item_id)
        sc2 = out.get("stain_context") or sc2
        out["stain_context"] = sc2
    if item_id in GARMENT_SPECIALTY_IDS:
        out = apply_garment_specialty_hints(out, item_id)
        sc2 = out.get("stain_context") or sc2
        out["stain_context"] = sc2
    if item_id in CULTURAL_SPECIALTY_IDS:
        out = apply_cultural_specialty_hints(out, item_id)
        sc2 = out.get("stain_context") or sc2
        out["stain_context"] = sc2
    if item_id in FABRIC_CURRICULUM_IDS:
        out = apply_fabric_curriculum_hints(out, item_id)
        sc2 = out.get("stain_context") or sc2
        out["stain_context"] = sc2
    if item_id in CHEM_SAFETY_IDS:
        out = apply_chem_safety_hints(out, item_id)
        sc2 = out.get("stain_context") or sc2
        out["stain_context"] = sc2
    if item_id in OPS_REMAINDER_IDS:
        out = apply_ops_remainder_hints(out, item_id)
        sc2 = out.get("stain_context") or sc2
        out["stain_context"] = sc2

    # Chem kits for specialty
    if item_id == "I_DUVET_GOOSE" or item_id == "I_DOWN_JACKET" or item_id == "I_DUVET_COTTON":
        if item_id == "I_DUVET_COTTON":
            out["chemicals"] = [
                {
                    "code": "D3",
                    "name_ko": "일반 세탁세제(이불·소량)",
                    "name_vi": "Nước giặt thường (chăn · ít)",
                    "dilution_ko": "소량. 과다·유연제 금지(잔여·뭉침).",
                    "dilution_vi": "Ít thôi. CẤM dư bột / xả vải (cặn → cục).",
                }
            ]
            out["empty_chems_ok"] = False
        else:
            out["chemicals"] = [
                {
                    "code": "S1",
                    "name_ko": "워시프렌즈 중성세제(다운·섬세용)",
                    "name_vi": "Nước giặt trung tính Wash Friends (down / tinh tế)",
                    "shop_name_vi": "Nước giặt trung tính Wash Friends (down)",
                    "dilution_ko": "병 안내·소량만. 일반 강세제·유연제·표백 금지. 반드시 추가 헹굼.",
                    "dilution_vi": "Theo chai · ít thôi. CẤM bột mạnh / xả vải / tẩy. Bắt buộc xả thêm.",
                    "when_use_ko": "다운·구스·패딩 물세탁 시 우선.",
                    "when_use_vi": "Ưu tiên khi giặt nước down / chăn lông / áo phao.",
                }
            ]
            out["empty_chems_ok"] = False
        # Replace stain-spotting tools with wash/dry tools
        out["tools"] = [
            {
                "id": "T_WASHER_LARGE",
                "name_ko": "대형 전면투입 세탁기(약 7kg+·상업용)",
                "name_vi": "Máy giặt lớn cửa trước (~7kg+ / tiệm)",
                "use_for_ko": (
                    "섬세/이불 코스, 찬물~≤30℃(솜이불은 30–40℃), 탈수 약. "
                    "소형 가정기는 용량 부족 — 거절/대형기 안내. 추가 헹굼 1회 필수."
                ),
                "use_for_vi": (
                    "Chương trình tinh tế/chăn, lạnh~≤30℃ (chăn bông 30–40℃), vắt nhẹ. "
                    "Máy nhỏ thiếu dung tích — từ chối / hướng máy lớn. Bắt buộc thêm 1 lần xả."
                ),
            },
            {
                "id": "T_DRYER_LOW",
                "name_ko": "건조기(저온) + 테니스볼/건조볼 2–3개",
                "name_vi": "Máy sấy (thấp) + 2–3 bóng tennis / dryer ball",
                "use_for_ko": (
                    "저온 건조. 20–30분마다 꺼내 손으로 뭉친 털 풀기. 총 2–4시간. "
                    "가운데 차가움 없을 때까지. 고온건조 금지."
                ),
                "use_for_vi": (
                    "Sấy thấp. Mỗi 20–30 phút lấy ra, dùng tay xoa cục lông. Tổng 2–4 giờ. "
                    "Đến khi giữa không còn lạnh. CẤM sấy nóng."
                ),
            },
        ]
        if _has_stain_cue(entities):
            out["tools"].insert(
                0,
                {
                    "id": "T_CLOTH",
                    "name_ko": "흰 천(겉커버 국소만)",
                    "name_vi": "Khăn trắng (chỉ vỏ cục bộ)",
                    "use_for_ko": (
                        "오염이 있을 때만: 겉커버·표면 국소 얼룩만 Cap1 닦기. "
                        "속통 전체를 스포팅하듯 문지르지 말 것. 옥살산·락스 PPE는 해당 얼룩 SOP에서만."
                    ),
                    "use_for_vi": (
                        "Chỉ khi có vết: lau Cap1 vỏ/mặt ngoài. "
                        "CẤM chà cả lõi như spotting. Oxalic/Javel PPE chỉ theo SOP vết."
                    ),
                },
            )
    elif item_id in {"I_TOWEL", "I_BED_SHEET"} and (
        _is_hotel(entities) or (entities.get("garment_color") == "white") or "흰" in _raw(entities)
    ):
        out["chemicals"] = [
            {
                "code": "D3",
                "name_ko": "일반 세탁세제(흰 린넨용)",
                "dilution_ko": "병 안내. 과다 금지(잔여→황변).",
            },
            {
                "code": "B1",
                "name_ko": "산소계 표백제(과탄산) — 흰 면만",
                "dilution_ko": "흰 면 수건·시트만. 구석 테스트. 유색 금지.",
            },
            {
                "code": "A3",
                "name_ko": "흰 식초(식용 약 5%)",
                "dilution_ko": "냄새·알칼리 잔여 시 1:4 최종 헹굼 선택(락스와 혼합 금지).",
            },
        ]
        out["empty_chems_ok"] = False
    elif item_id == "I_FUR_REAL":
        out["chemicals"] = []
        out["empty_chems_ok"] = True
        out["chem_forbid_ko"] = "진모피: 매장 물세탁·일반 드라이·표백 금지. (4)에 약 지어내지 말 것 — 전문 모피만."
    elif item_id == "I_FAUX_LEATHER":
        out["chemicals"] = [
            {
                "code": "D2",
                "name_ko": "주방세제(중성) — 인조가죽 국소",
                "dilution_ko": "극소량 희석·천에 묻혀 Cap1. 통담금·세탁기 비권장(코팅 박리).",
            }
        ]
        out["empty_chems_ok"] = False
    elif item_id in {"I_SNEAKER_WHITE", "I_SHOE_LACES"} or (
        item_id == "I_SNEAKER" and _is_whitening(entities)
    ):
        out["chemicals"] = [
            {
                "code": "D2",
                "name_ko": "주방세제(중성)",
                "dilution_ko": "페이스트·약희석. 과다 알칼리·락스 남용 금지(황변).",
            },
            {
                "code": "N1",
                "name_ko": "베이킹소다",
                "dilution_ko": "세제+소다 페이스트로 흰 고무·끈 국소.",
            },
            {
                "code": "B1",
                "name_ko": "산소계 표백제 — 흰 끈·흰 천창만(테스트)",
                "dilution_ko": "고무 창에는 신중. 유색·가죽은 금지.",
            },
        ]
        out["empty_chems_ok"] = False
    elif item_id in {"I_HAT_CAP", "I_GOLF_HAT"}:
        out["chemicals"] = [
            {
                "code": "D2",
                "name_ko": "주방세제(중성) — 땀띠·챙 국소",
                "name_vi": "Nuoc rua chen trung tinh — vanh mo hoi",
                "name": "Mild dish soap — sweatband spot only",
                "dilution_ko": "약희석. 하드캡은 통담금·세탁기 금지.",
                "dilution_vi": "Pha loang. Mu cung: CAM ngam/may.",
                "dilution_en": "Light dilution. Structured caps: no soak/washer.",
            },
            {
                "code": "S1",
                "name_ko": "워시프렌즈 중성세제(선택)",
                "name_vi": "Chat giat trung tinh (tuy chon)",
                "name": "Mild detergent (optional)",
                "dilution_ko": "소프트캡 손세탁 시 소량.",
                "dilution_vi": "Mu mem: tay, it.",
                "dilution_en": "Soft caps: hand-wash, small amount.",
            },
        ]
        out["empty_chems_ok"] = False
        out["tools"] = [
            {
                "id": "T_BRUSH_SOFT",
                "name_ko": "연질 스포팅 솔",
                "name_vi": "Ban chai mem",
                "name": "Soft spotting brush",
                "use_for_ko": "땀띠·챙만 Cap1–2 원형으로. 챙 꺾기·비즈/로고 세게 금지.",
                "use_for_vi": "Chi vanh mo hoi Cap1–2. CAM gap vanh / cha logo manh.",
                "use_for_en": "Sweatband/brim only Cap1–2 circles. Do not bend brim or scrub logos.",
            },
            {
                "id": "T_CLOTH",
                "name_ko": "흰 천·흡수지",
                "name_vi": "Khan trang",
                "name": "White cloth / blotter",
                "use_for_ko": "세제 잔여 닦기·형태 유지용 속채움. 운동화 밑창 솔과 혼용 금지.",
                "use_for_vi": "Lau du xa phong + nho giu form. CAM dung chai de giay.",
                "use_for_en": "Wipe soap residue; stuff crown for shape. Never use shoe-sole brushes.",
            },
        ]
    elif item_id == "I_LINEN_GARMENT":
        out["chemicals"] = [
            {
                "code": "D3",
                "name_ko": "일반 세탁세제(린넨·마)",
                "dilution_ko": "소량. 강알칼리·락스(유색) 주의.",
            },
            {
                "code": "S1",
                "name_ko": "워시프렌즈 중성세제",
                "dilution_ko": "얇은·색이염 위험 시 우선.",
            },
        ]
        out["empty_chems_ok"] = False
    elif item_id in {"I_FINISHING", "I_SUIT", "I_SUIT_SUMMER", "I_DRESS", "I_DRESS_SHIRT"}:
        out["empty_chems_ok"] = True
        # Synthetic tool so (2)도구 always names 에어드레서 (LLM otherwise drops it)
        tools = [t for t in (out.get("tools") or []) if isinstance(t, dict)]
        if not any("에어드레서" in str(t.get("name_ko") or "") for t in tools):
            tools.append(
                {
                    "id": "T_AIR_DRESSER",
                    "name_ko": "에어드레서(LG 스타일러·삼성 등)",
                    "use_for_ko": (
                        "일상 정장·코튼·냄새·가벼운 구김. 프로그램은 섬세/표준을 라벨에 맞게. "
                        "웨딩·구조 복잡한 수트·칼주름 필수 셔츠는 에어드레서만으로 부족 — "
                        "수동 스팀/셔츠 프레스 병행. 가죽·스웨이드·모피·인조가죽 고온 금지."
                    ),
                    "use_for_en": "Air dresser / styler for light wrinkles and odor; not enough alone for wedding/crease shirts.",
                    "use_for_vi": "Tu cham soc (airdresser): nhao nhe + mui. Dam cuoi / nep ao so mi: can steam tay.",
                }
            )
            out["tools"] = tools
    elif item_id == "I_MACHINE_PROFILE":
        out["chemicals"] = []
        out["empty_chems_ok"] = True
    return out


def _goose_duvet(*, has_stain: bool = False) -> dict[str, str]:
    branch = (
        "【오염 있음】겉커버·표면만 국소 전처리(흰 천 Cap1). 속통 전체 스포팅·문지르기 금지. "
        "그다음 아래 일반 세탁. 심한 곰팡이·생체오염은 별도 SOP/거절 검토.\n"
        if has_stain
        else "【오염 없음 — 일반 세탁】얼룩 지우기가 아니라 속통 통세탁·건조 절차.\n"
    )
    branch_vi = (
        "【Có vết】Chỉ pretreat vỏ/mặt ngoài (khăn trắng Cap1). CẤM spotting/chà cả lõi. "
        "Sau đó giặt thường bên dưới. Mốc nặng / biohazard → SOP riêng hoặc từ chối.\n"
        if has_stain
        else "【Không vết — giặt thường】Không phải tẩy vết: quy trình giặt + sấy cả lõi down.\n"
    )
    branch_en = (
        "【Stain present】Pretreat cover/surface only (white cloth Cap1). Do not spot/rub the whole fill. "
        "Then follow general wash below. Heavy mold/biohazard → separate SOP or refuse.\n"
        if has_stain
        else "【No stain — general wash】Not stain removal: wash + dry the whole down insert.\n"
    )
    return {
        "precheck_ko": (
            "구스·오리털(다운) 이불 일반 세탁. "
            "먼저 묻는다: 눈에 띄는 얼룩·곰팡이·심한 냄새가 있는가? "
            "없으면 일반 세탁, 있으면 국소 전처리 후 일반 세탁. "
            "라벨·찢김 수선. 소형기면 대형 전면투입(약 7kg+)·상업용. "
            "이불커버는 자주, 다운 속통은 보통 1–3년에 1회."
        ),
        "why_ko": (
            "[왜 이 순서] 질문은 품목 세탁. 다운=천연 오일→퍼크 드라이 비권장. "
            "중성/다운세제 소량+추가 헹굼+저온건조+테니스볼. "
            "오염이 있을 때만 겉 국소 전처리 — 옥살산·락스 장갑을 일반세탁에 끌어오지 말 것."
        ),
        "fresh_path_ko": (
            f"{branch}"
            "(1)구멍·심지 점검·수선. 지퍼·단추 잠금. "
            "(2)대형 전면투입 세탁기: 섬세/이불 코스, 찬물~≤30℃, 다운전용·중성세제(S1) 소량, "
            "탈수 약·저속, 반드시 추가 헹굼 1회. 비틀어 짜기 금지. "
            "(3)건조기 저온 + 깨끗한 테니스볼(또는 건조볼) 2–3개. "
            "20–30분마다 꺼내 손으로 뭉친 털 풀어 주기. 총 2–4시간. "
            "(4)가운데를 만져 차가움·축축함 없을 때까지 — 미건조면 추가 건조. "
            "(5)유연제·산소/염소표백·고온·퍼크 드라이 금지."
        ),
        "dried_path_ko": (
            "이미 뭉침·냄새: 저온 재건조+테니스볼. "
            "곰팡이·심한 오염이면 해당 얼룩 SOP+PPE — 일반세탁 경로와 섞지 말 것."
        ),
        "motion_ko": "Cap0–1 — 기계 섬세. 비틀어 짜기·속통 전체 문지르기 금지.",
        "water_temp_ko": "찬물 / ≤30℃. 온수·삶기 금지. 건조는 저온만.",
        "aftercare_ko": (
            "저온건조+테니스볼 2–3개로 20–30분마다 뭉침 풀기 → "
            "가운데 완전 건조 확인 후 보관. 커버 사용. 제습·통풍."
        ),
        "sense_check_ko": "손: 가운데 차가움 없음. 눈: 뭉침 해소·로프트. 코: 곰팡이·세제 냄새 없음.",
        "success_rate_ko": "대형기+다운세제+테니스볼 완전건조: 높음. 소형기·미건조: 뭉침·곰팡이 위험.",
        "refuse_when_ko": "용량 부족 소형기 강제, 퍼크 드라이 요구, 찢긴 채 세탁 → 거절/대형기·수선 안내.",
        "must_include_ko": "대형 전면투입, 추가 헹굼, 테니스볼, 퍼크 금지",
        "precheck_vi": (
            "Chăn lông ngỗng/vịt (down) — giặt thường. "
            "Hỏi trước: có vết rõ, mốc, mùi nặng không? "
            "Không → giặt thường; có → pretreat cục bộ rồi giặt thường. "
            "Đọc nhãn; vá rách trước. Máy nhỏ → máy lớn cửa trước (~7kg+)/tiệm. "
            "Vỏ chăn giặt thường; lõi down thường 1–3 năm/lần."
        ),
        "why_vi": (
            "[Tại sao] Câu hỏi = giặt phẩm. Down giữ dầu tự nhiên → không khuyến khích PERC. "
            "Nước giặt trung tính/down ít + xả thêm + sấy thấp + bóng tennis. "
            "Chỉ pretreat vỏ khi có vết — không kéo oxalic/Javel vào giặt thường."
        ),
        "fresh_path_vi": (
            f"{branch_vi}"
            "(1) Kiểm lỗ/đường may; khóa kéo/nút. "
            "(2) Máy lớn cửa trước: tinh tế/chăn, lạnh~≤30℃, S1/down-wash ít, "
            "vắt nhẹ, BẮT BUỘC thêm 1 lần xả. CẤM vắt xoắn. "
            "(3) Sấy thấp + 2–3 bóng tennis/dryer ball sạch. "
            "Mỗi 20–30 phút lấy ra, dùng tay xoa cục lông. Tổng 2–4 giờ. "
            "(4) Sờ giữa chăn — hết lạnh/ẩm; chưa khô thì sấy thêm. "
            "(5) CẤM xả vải, tẩy oxy/clo, nóng, PERC."
        ),
        "dried_path_vi": (
            "Đã cục/mùi: sấy lại thấp + bóng tennis. "
            "Mốc/vết nặng → SOP vết + PPE — không trộn với giặt thường."
        ),
        "motion_vi": "Cap0–1 — máy tinh tế. CẤM vắt xoắn / chà cả lõi.",
        "water_temp_vi": "Lạnh / ≤30℃. CẤM nước nóng/luộc. Sấy chỉ thấp.",
        "aftercare_vi": (
            "Sấy thấp + 2–3 bóng tennis, mỗi 20–30 phút xoa cục → "
            "khô giữa rồi bảo quản. Dùng vỏ. Hút ẩm/thoáng."
        ),
        "sense_check_vi": "Tay: giữa không lạnh. Mắt: hết cục, loft tốt. Mũi: không mốc/mùi bột.",
        "success_rate_vi": "Máy lớn + down-wash + bóng tennis + khô hết: cao. Máy nhỏ/chưa khô: cục + mốc.",
        "refuse_when_vi": "Ép máy nhỏ thiếu dung tích, đòi PERC, giặt khi còn rách → từ chối / hướng máy lớn·vá.",
        "must_include_vi": "máy lớn cửa trước, xả thêm, bóng tennis, cấm PERC",
        "precheck_en": (
            "Goose/duck down duvet — general wash. Ask: visible stain, mold, strong odor? "
            "None → wash; yes → local pretreat then wash. Label + mend tears. "
            "Small washer → large front-load (~7kg+)/laundromat. Cover often; insert every 1–3 years."
        ),
        "why_en": (
            "[Why] Item wash. Down = natural oils → PERC dry-clean not preferred. "
            "Mild/down detergent small dose + extra rinse + low dry + tennis balls. "
            "Pretreat cover only when stained — do not pull oxalic/bleach PPE into general wash."
        ),
        "fresh_path_en": (
            f"{branch_en}"
            "(1) Check holes/baffles; zip/buttons. "
            "(2) Large front-load: delicate/bedding, cold~≤30℃, S1/down detergent small dose, "
            "gentle spin, mandatory extra rinse. No wringing. "
            "(3) Low dryer + 2–3 clean tennis/dryer balls. "
            "Every 20–30 min break clumps by hand. Total 2–4h. "
            "(4) Feel center until not cold/damp. "
            "(5) No softener, oxygen/chlorine bleach, high heat, or PERC."
        ),
        "dried_path_en": (
            "Already clumped/odorous: re-dry low + tennis balls. "
            "Mold/heavy soil → stain SOP + PPE — do not mix with general wash."
        ),
        "motion_en": "Cap0–1 — machine delicate. No wringing / rubbing whole fill.",
        "water_temp_en": "Cold / ≤30℃. No hot boil. Dryer low only.",
        "aftercare_en": (
            "Low dry + 2–3 tennis balls, fluff every 20–30 min → "
            "confirm center dry, then store. Use cover. Dehumidify/ventilate."
        ),
        "sense_check_en": "Hand: center not cold. Eye: loft restored. Nose: no mold/detergent smell.",
        "success_rate_en": "Large washer + down detergent + tennis balls + full dry: high. Small/undried: clump + mold risk.",
        "refuse_when_en": "Force undersized washer, demand PERC, wash while torn → refuse / large washer·mend.",
        "must_include_en": "large front-load, extra rinse, tennis balls, no PERC",
    }


def _cotton_duvet(*, has_stain: bool = False) -> dict[str, str]:
    branch = (
        "【오염 있음】겉만 국소 전처리 후 아래 세탁.\n"
        if has_stain
        else "【오염 없음 — 일반 세탁】\n"
    )
    branch_vi = (
        "【Có vết】Pretreat vỏ rồi giặt bên dưới.\n"
        if has_stain
        else "【Không vết — giặt thường】\n"
    )
    return {
        "precheck_ko": (
            "솜·폴리 충전 이불(구스 아님). 오염 유무 확인. 구스/다운과 구분. 대형기 필요 시 안내."
        ),
        "why_ko": (
            "[왜 이 순서] 품목 세탁. 솜/폴리는 세제 잔여·탈수 부족 시 뭉침. "
            "소량 세제+추가헹굼+저온~중온 건조+테니스볼."
        ),
        "fresh_path_ko": (
            f"{branch}"
            "(1)크기 vs 세탁기 용량. (2)섬세/이불 코스 30–40℃, 세제 소량, 추가 헹굼. "
            "(3)건조 저온~중온 + 테니스볼, 20–30분마다 털기. "
            "(4)가운데 완전 건조. (5)유연제 과다 금지."
        ),
        "dried_path_ko": "뭉침: 재건조+테니스볼. 곰팡이: 밀듀 SOP+PPE.",
        "motion_ko": "기계 위주 Cap0. 오염 있을 때만 국소 Cap2.",
        "water_temp_ko": "30–40℃(끓이기 금지).",
        "aftercare_ko": "커버 자주 세탁. 속통 연 2–4회. 완전 건조 후 보관.",
        "sense_check_ko": "손: 가운데 건조. 눈: 뭉침 없음.",
        "success_rate_ko": "대형기+완전건조: 높음.",
        "refuse_when_ko": "용량 부족으로 억지 세탁 → 대형기 안내.",
        "must_include_ko": "대형기, 추가 헹굼, 테니스볼",
        "precheck_vi": (
            "Chăn bông/poly (không phải down). Phân biệt với chăn lông. "
            "Hỏi vết. Máy nhỏ → máy lớn."
        ),
        "why_vi": (
            "[Tại sao] Giặt phẩm. Bông/poly dễ cục nếu dư bột / thiếu xả. "
            "Bột ít + xả thêm + sấy thấp~vừa + bóng tennis."
        ),
        "fresh_path_vi": (
            f"{branch_vi}"
            "(1) So size vs máy. (2) Tinh tế/chăn 30–40℃, bột ít, xả thêm. "
            "(3) Sấy thấp~vừa + bóng tennis, 20–30 phút xoa. "
            "(4) Khô giữa. (5) CẤM xả vải quá nhiều."
        ),
        "dried_path_vi": "Cục: sấy lại + bóng. Mốc: SOP mốc + PPE.",
        "motion_vi": "Máy Cap0. Có vết mới Cap2 cục bộ.",
        "water_temp_vi": "30–40℃ (không luộc).",
        "aftercare_vi": "Vỏ giặt thường. Lõi 2–4 lần/năm. Khô hết rồi bảo quản.",
        "sense_check_vi": "Tay: giữa khô. Mắt: không cục.",
        "success_rate_vi": "Máy lớn + khô hết: cao.",
        "refuse_when_vi": "Ép máy thiếu dung tích → hướng máy lớn.",
        "must_include_vi": "máy lớn, xả thêm, bóng tennis",
    }


def _down_jacket(*, has_stain: bool = False) -> dict[str, str]:
    branch = (
        "【오염 있음】겉면 국소만 전처리 후 아래 세탁. 속 충전재 전체 문지르기 금지.\n"
        if has_stain
        else "【오염 없음 — 일반 세탁】\n"
    )
    return {
        "precheck_ko": (
            "다운·패딩 점퍼 일반 세탁. 오염 유무 확인. "
            "솔기·배플·지퍼 점검. 구멍은 세탁 전 수선. 전면투입기만(상부 교반기 비권장)."
        ),
        "why_ko": (
            "[왜 이 순서] 품목 세탁. 세제 잔여→뭉침, 미건조→곰팡이. "
            "다운세제/중성+추가 헹굼+저온건조+테니스볼. 퍼크는 라벨·전문 판단."
        ),
        "fresh_path_ko": (
            f"{branch}"
            "(1)지퍼·포켓 정리, 구멍 수선. "
            "(2)전면투입기 섬세, 찬물~≤30℃, S1 소량, 탈수 약, 추가 헹굼 필수. "
            "(3)건조기 저온 + 테니스볼 2–3개. 30분마다 뭉침 풀기. 총 2–4시간. "
            "(4)가운데·배플 완전 건조·로프트 확인. "
            "(5)고온·강탈수·유연제·표백 금지."
        ),
        "dried_path_ko": "미건조 냄새: 재건조+테니스볼. 로프트 크게 줄면 고객 고지.",
        "motion_ko": "Cap0–1. 세탁기 섬세. 비틀어 짜기 금지.",
        "water_temp_ko": "찬물 / ≤30℃. 건조 저온.",
        "aftercare_ko": "저온건조+테니스볼. 완전 건조 후 보관. 통풍.",
        "sense_check_ko": "손: 배플 가운데 건조·부피. 코: 곰팡이·세제 냄새 없음.",
        "success_rate_ko": "전면투입+다운세제+테니스볼 완전건조: 높음.",
        "refuse_when_ko": "상부 교반기만 강제, 찢긴 채 세탁, 고온건조 → 거절/안내.",
        "must_include_ko": "전면투입, 추가 헹굼, 테니스볼",
    }


def _towel(*, hotel: bool, bio: bool) -> dict[str, str]:
    if bio:
        return {
            "precheck_ko": (
                "호텔·업소 수건 + 혈액/토사물 등: PPE(니트릴). 흰 수건과 유색 분리. "
                "단백질은 찬물 먼저(온수=고착)."
            ),
            "why_ko": (
                "[왜 이 순서] 생체오염=단백질·병원체. "
                "찬물+효소(원단 허용)·헹굼 후 흰 면만 고온·산소표백. "
                "유연제=흡수력 저하 → 호텔 수건 금지."
            ),
            "fresh_path_ko": (
                "(1)장갑. 고형물 제거. (2)찬물 헹굼·단백질 전처리(효소 허용 시). "
                "(3)흰 면: 60℃ 근처 + 일반세제, 산소표백(B1) 옵션. 염소(락스)는 흰 면만·별도·식초와 혼합 금지. "
                "(4)추가 헹굼. 유연제 금지. (5)고온~중온 건조 또는 햇빛. 완전 건조. "
                "(6)잔여·냄새 있으면 재처리 또는 폐기 고지."
            ),
            "dried_path_ko": "이미 온수 세탁한 피: 성공률↓ 고지. 재처리 1회 후 전문/폐기.",
            "motion_ko": "기계 위주. 국소 Cap2.",
            "water_temp_ko": "단백질 단계=찬물. 본세탁 흰면~60℃.",
            "aftercare_ko": "완전 건조. 유연제 금지. 건조 전 강광.",
            "sense_check_ko": "눈: 잔혈·황변. 코: 이취 없음. 손: 뻣뻣함(세제 잔여) 없음.",
            "success_rate_ko": "조기 찬물: 양호. 열고착 후: 중간~낮음.",
            "refuse_when_ko": "유색 수건에 락스, 100% 복원 요구 → 거절.",
        }
    head = "호텔·업소 흰 수건" if hotel else "수건·목욕타월"
    return {
        "precheck_ko": f"{head}: 흰/유색 분리. 냄새 나면 식초 전처리. 유연제 금지(흡수↓).",
        "why_ko": (
            "[왜 이 순서] 수건=균·냄새·흡수력. 흰 면은 ~60℃+산소표백 가능. "
            "유연제·과다세제=잔여·뻣뻣·황변. 완전 건조 필수."
        ),
        "fresh_path_ko": (
            "(1)흰/유색 분리. (2)냄새: 식초 1:4 약 30분(선택). "
            "(3)세탁: 흰 면 ~60℃ + 세제 적정. 황변·위생: 산소표백(B1). "
            "(4)유연제 넣지 말 것. 추가 헹굼. "
            "(5)건조 중온~고온 또는 통풍·햇빛. (6)완전 건조 후 보관."
        ),
        "dried_path_ko": "냄새 지속: 식초+60℃ 재세탁. 뻣뻣: 세제↓·헹굼↑.",
        "motion_ko": "기계 Cap0.",
        "water_temp_ko": "흰 면 ~60℃. 유색·라벨 낮으면 따름.",
        "aftercare_ko": "통풍 보관. 과다 세제 금지. 건조 전 강광.",
        "sense_check_ko": "코: 이취 없음. 손: 흡수력·부드러움. 눈: 황변 없음.",
        "success_rate_ko": "흰면 고온+산소: 높음. 유연제 습관: 흡수력 저하.",
        "refuse_when_ko": "유색에 락스 강제 → 거절.",
    }


def _bed_sheet(*, hotel: bool, bio: bool) -> dict[str, str]:
    if bio:
        return {
            "precheck_ko": "호텔·침대 시트 + 혈액 등: PPE. 흰/유색 분리. 단백질=찬물 먼저.",
            "why_ko": "[왜 이 순서] 생체→찬물 전처리 후 흰면 고온·산소. 열고착 고지.",
            "fresh_path_ko": (
                "(1)장갑·고형물 제거. (2)찬물·효소(허용 시). "
                "(3)흰 면 시트 ~60℃ + 세제 + B1(황변/위생). "
                "(4)추가 헹굼. (5)고온 건조 또는 햇빛 살균. (6)잔여 시 재처리·고지."
            ),
            "dried_path_ko": "열고착 혈액: 성공률↓. 1회 재시도 후 전문/폐기.",
            "motion_ko": "기계. 국소 Cap2.",
            "water_temp_ko": "전처리 찬물 → 본세탁 흰면~60℃.",
            "aftercare_ko": "완전 건조. 강광 잔여 확인.",
            "sense_check_ko": "눈: 잔혈. 코: 이취 없음.",
            "success_rate_ko": "조기: 양호. 열고착: 중간↓.",
            "refuse_when_ko": "100%·유색 락스 → 거절.",
        }
    label = "호텔·업소 흰 시트·침대커버" if hotel else "침대 시트·매트리스커버"
    return {
        "precheck_ko": f"{label}: 흰/유색 분리. 라벨 최고온도. 진드기·위생은 고온·햇빛.",
        "why_ko": (
            "[왜 이 순서] 시트=면 기준 ~60℃로 진드기·균 감소. "
            "흰면 황변은 산소표백. 유색은 40℃대·표백 주의."
        ),
        "fresh_path_ko": (
            "(1)털기·흡입. (2)얼룩 국소 전처리. "
            "(3)흰 면: ~60℃ + 세제, 필요 시 B1. 유색: 라벨~40℃, 락스 금지. "
            "(4)충분히 헹굼. (5)가능하면 햇빛 살균 또는 고온 건조. "
            "(6)완전 건조 후 깔기."
        ),
        "dried_path_ko": "냄새·곰팡이: 식초 후 60℃. 단백질 얼룩: 찬물 효소 먼저.",
        "motion_ko": "기계 Cap0. 국소 Cap2.",
        "water_temp_ko": "흰면~60℃ / 유색·민감~40℃·라벨.",
        "aftercare_ko": "통풍·햇빛. 교체 주기 안내.",
        "sense_check_ko": "눈: 황변·잔여. 코: 쾌적.",
        "success_rate_ko": "흰면 고온: 높음.",
        "refuse_when_ko": "라벨 X 고온 무시 → 거절.",
    }


def _machine_profile() -> dict[str, str]:
    return {
        "precheck_ko": (
            "상업용 세탁기·건조기: 라벨·원단·잔여 얼룩을 코스보다 먼저. "
            "얼룩 남은 채 건조=열고착. 경수면 세제·헹굼 보정."
        ),
        "why_ko": (
            "[왜 이 순서] 코스=수온+기계 동작+탈수 강도 묶음. "
            "점주 매장: 표준/섬세/침구·수건(고온)/기능성. "
            "건조: 수건 고온·면 중온·폴리·다운 저온. "
            "실크·울·가죽·스판·아오자이=건조기 금지(또는 전문)."
        ),
        "fresh_path_ko": (
            "(1)원단·라벨·잔여 얼룩 확인(강광). "
            "(2)세탁 코스 선택 — "
            "면·일반: 표준 30–40℃(흰 수건/시트 위생 시 ~60℃); "
            "실크·울·얇음·넥타이: 섬세/손세탁·저탈수; "
            "구스·패딩: 섬세≤30℃·저탈수·추가헹굼; "
            "수건·호텔 흰린넨: 고온(~60℃)·표준/침구; "
            "기능성·골프: 저온·세제 소량·유연제 금지. "
            "(3)탈수: 섬세·다운=약/저속; 수건·면=중~강(라벨 허용). "
            "(4)건조 전 강광으로 잔여 확인. "
            "(5)건조 — 수건 고온; 면 중온; 폴리·다운 저온+다운은 테니스볼·중간 털기; "
            "실크/울/가죽/스판=자연건조 또는 금지. "
            "(6)불확실=섬세+자연건조. 기종별 분·rpm은 매장 매뉴얼 숫자를 따르고, "
            "위 온도·코스 원칙을 대사로 설명할 것."
        ),
        "dried_path_ko": "세제 잔여: 추가 헹굼. 구김: 약한 스팀(라벨 허용).",
        "motion_ko": "Cap0 — 코스 선택·확인.",
        "water_temp_ko": "코스·라벨 최고를 넘지 말 것. 불확실하면 한 단계 낮게.",
        "aftercare_ko": "세탁/건조 직후 꺼내기. 필터·통 청소. 건조 전 강광.",
        "sense_check_ko": "눈: 건조 전 잔여 없음. 손: 세제 잔여 없음. 코: 이취 없음.",
        "success_rate_ko": "라벨+잔여확인 후 건조: 높음. 성급 건조: 열고착.",
        "refuse_when_ko": "실크·울·가죽 건조기 강제, 잔여 얼룩 상태 건조 요구 → 거절.",
    }


def _fur_real() -> dict[str, str]:
    return {
        "precheck_ko": "진모피 vs 인조 구분·사진. 매장 세탁기/일반 드라이 거절 권고.",
        "why_ko": (
            "[왜 이 순서] 진모피=가죽+털 유지. 물세탁·가정 드라이·고온건조=유분 손실·찢김. "
            "전문 모피 클리닝만."
        ),
        "fresh_path_ko": (
            "(1)진모피 확인. (2)매장에서 물세탁·일반 퍼크·건조기 하지 말 것. "
            "(3)먼지만 약하게, 넓은 옷걸이·통풍. (4)비에 젖으면 털어 자연 건조 — 젖은 채 브러시·헤어드라이 금지. "
            "(5)전문 모피점으로 의뢰. (6)고객에게 거절·이관 사유 고지."
        ),
        "dried_path_ko": "가정 약품·담금 금지. 거절권 행사.",
        "motion_ko": "Cap0–1. 젖은 채 문지르기 금지.",
        "water_temp_ko": "매장 물세탁 없음.",
        "aftercare_ko": "서늘·통풍·직사광선·향수 분무 금지. 여름 냉장보관 안내(가능 시).",
        "sense_check_ko": "눈: 털 빠짐·가죽 건조. 코: 이취.",
        "success_rate_ko": "매장 자가처리: 해당 없음(전문만).",
        "refuse_when_ko": "물세탁·일반 드라이 요구 → 거절·전문 안내.",
    }


def _fur_faux() -> dict[str, str]:
    return {
        "precheck_ko": "인조모피(아크릴 등): 고온·강한 스팀=털 영구 곱슬. 라벨.",
        "why_ko": "[왜 이 순서] 인조=열에 약함. 저온·짧은 시간·즉시 걸기.",
        "fresh_path_ko": (
            "(1)뒤집기. (2)~30℃ 중성·섬세·짧은 시간. (3)즉시 걸기. "
            "(4)고온건조·강한 스팀·다리미 금지. (5)마른 뒤 결 따라 연질 솔."
        ),
        "dried_path_ko": "곱슬·눌림: 복원 어려움 고지.",
        "motion_ko": "Cap2 이하. 저속.",
        "water_temp_ko": "~30℃. 고온 금지.",
        "aftercare_ko": "걸이 통풍. 고온건조 금지.",
        "sense_check_ko": "눈: 털 결. 손: 열손상 없음.",
        "success_rate_ko": "저온 섬세: 양호. 고온 후: 낮음.",
        "refuse_when_ko": "고온건조·강한 스팀 요구 → 거절.",
    }


def _dry_vs_wet() -> dict[str, str]:
    return {
        "precheck_ko": "라벨(물통 X / 드라이 P·F·W) + 품목(정장·모피·다운·가죽·시트).",
        "why_ko": (
            "[왜 이 순서] 라벨이 계약. "
            "물세탁 OK: 흰 수건·시트·일반 면/폴리(라벨 허용). "
            "온화 물세탁 우선: 구스·다운(퍼크 주의). "
            "드라이/전문 우선: 정장 캔버스, 고가 실크, 한복·아오자이. "
            "매장 물·일반 드라이 금지: 진모피, 민감 가죽·스웨이드(스포팅/전문). "
            "인조가죽(PU/레자): 진가죽과 다름 — 국소 물·중성만, 가죽크림 강제 금지."
        ),
        "fresh_path_ko": (
            "(1)라벨 5기호. (2)물 X → 드라이/전문. "
            "(3)구스·패딩 → 온화 물세탁·대형기(퍼크 비권장). "
            "(4)진가죽·스웨이드 → 국소/전문(세탁기 금지). 인조가죽 → I_FAUX_LEATHER 경로. "
            "(5)진모피 → 모피 전문만. "
            "(6)흰 호텔 린넨 → 물세탁 고온. "
            "(7)마(린넨) 의류 → 온화 물·고온 다림질(또는 스팀). "
            "(8)불확실 → 보수(찬물·섬세) + 고객 고지."
        ),
        "dried_path_ko": "이미 잘못 물세탁(실크 등): 강처리 중단·고지·전문.",
        "motion_ko": "Cap0 — 결정 먼저.",
        "water_temp_ko": "물세탁 허용 시에만.",
        "aftercare_ko": "전표에 물/드라이/이관 사유 기록.",
        "sense_check_ko": "라벨·품목·고객 동의 일치.",
        "success_rate_ko": "라벨 준수: 사고↓.",
        "refuse_when_ko": "라벨 X 무시 요구 → 거절.",
    }


def _faux_leather() -> dict[str, str]:
    return {
        "precheck_ko": (
            "인조가죽(PU·PVC·레자·비건레더) 구분 체크리스트 — 하나라도 해당하면 인조 쪽: "
            "(a)안감·뒷면이 천/부직포이고 가죽이 아님 "
            "(b)표면 결이 너무 균일·플라스틱 광택 "
            "(c)라벨에 PU/PVC/polyurethane/synthetic/vegan "
            "(d)접힌 곳·시접에서 코팅 갈라짐·박리 시작 "
            "(e)물방울이 스며들지 않고 맺힘(진가죽은 서서히 흡수). "
            "불확실·고가·이미 박리면 사진·거절권. 진가죽/스웨이드와 경로 섞지 말 것."
        ),
        "why_ko": (
            "[왜 이 순서] 인조가죽=플라스틱 코팅+원단. "
            "세탁기·통담금·고온·아세톤·알코올 과다·진가죽 크림/밍크오일은 코팅 갈라짐·박리. "
            "국소 중성·미지근한 천 + 완전 건조가 안전. "
            "고객 멘트: 「레자·PU는 진가죽 크림이 아니라 국소 닦기입니다」."
        ),
        "fresh_path_ko": (
            "(1)위 체크리스트로 진가죽/스웨이드/인조 확정. 인조만 이 경로. "
            "(2)마른 천으로 먼지·표면 때. "
            "(3)중성세제(D2) 극소량 희석액을 흰 천에 묻혀 Cap1 국소 — "
            "흠뻑·통담금·세탁기·건조기 금지(기본). "
            "(4)물기만 남은 천으로 잔여 → 형태 유지하며 그늘 완전 건조. "
            "(5)광택은 인조가죽 전용 케어(라벨 허용)만. "
            "진가죽 크림·밍크오일·구두약·아세톤·알코올 과다 금지. "
            "(6)가방·자켓·바지 공통: 시접·접힘부 박리 있으면 추가 마찰 중단·고지. "
            "(7)잉크·유성 오염: 구석 테스트 후 극소 — 안 되면 전문/거절."
        ),
        "dried_path_ko": (
            "이미 세탁기 돌린 인조: 추가 강처리 중단, 코팅 손상·박리 가능 고지. "
            "고객 멘트: 「이미 기계 세탁하셨으면 코팅이 약해졌을 수 있어 더 세게는 못 합니다」."
        ),
        "motion_ko": "Cap1만 — 찍기·닦기. 세게 문지르기·솔 강타 금지.",
        "water_temp_ko": "미지근·최소. 온수·세탁기·건조기 금지(기본).",
        "aftercare_ko": "통풍 건조. 직사광선·히터·접어 장기보관(코팅 주름) 주의. 강광 잔여 확인.",
        "sense_check_ko": "눈: 코팅 갈라짐·박리·광택 손상. 손: 끈적·잔여 세제.",
        "success_rate_ko": "국소 오염: 양호. 이미 박리·세탁기 후: 낮음 — 사전 고지.",
        "refuse_when_ko": (
            "세탁기·드라이 강요, 진가죽 크림 강제, 박리 진행, 100% 새것 복원 → 거절/고지."
        ),
        "must_include_ko": "진가죽과 구분, 세탁기 금지, 진가죽 크림 금지",
    }


def _sneaker_white() -> dict[str, str]:
    return {
        "precheck_ko": (
            "흰 창(미드솔)·흰 옆면 고무·흰 패널: 갑피(천/메쉬)와 분리해 처리. "
            "끈은 빼서 별도. "
            "접수 멘트(필수): 「표면 때는 많이 밝아지지만, "
            "신다 누렇게 된 산화·황변은 100% 하얗게 복원 약속이 어렵습니다」."
        ),
        "why_ko": (
            "[왜 이 순서] 흰 고무·EVA 창은 알칼리 잔여·직사광선·고온건조에 누렇게. "
            "중성+베이킹소다 국소 → 충분히 헹굼 → 그늘 건조. "
            "락스(염소) 남용·고온=더 황변·접착제 손상. "
            "표면 때(흙·검댕) vs 산화 황변을 고객에게 구분해 설명할 것."
        ),
        "fresh_path_ko": (
            "(1)끈·깔창 분리. 마른 흙 털기. 사진(전). "
            "(2)흰 고무·옆면: 중성세제 1작은술 + 베이킹소다 1작은술 + 물 몇 방울 페이스트. "
            "경질 솔(고무만) Cap2 한 방향. 흰 천 패널: 연질 솔·중성만. "
            "(3)충분히 헹굼(잔여 세제=재황변). "
            "(4)흰 끈: 별도 찬물 담금 15–30분+중성 → 망세탁 약하게 → 헹굼. "
            "(5)그늘·통풍 건조, 신문지·키친타월로 형태. 고온건조기·직사광선 금지. "
            "(6)남아 있는 누런기: 1회만 재시도. "
            "산소표백은 흰 천·끈만 구석 테스트 후. 고무 창에는 신중·비권장. "
            "(7)인도 멘트: 「오늘은 여기까지 — 더 세게 하면 접착·색이 상할 수 있어요」."
        ),
        "dried_path_ko": (
            "오래된 산화 황변: 성공률 중간↓. "
            "고객 멘트: 「시간이 지나 노란 창은 새 신처럼 되긴 어렵고, 밝게만 가능합니다」. "
            "강한 락스·사포 과다 금지."
        ),
        "motion_ko": "고무 Cap2 경질 솔. 메쉬·갑피 Cap1–2 연질 — 솔 혼용 금지.",
        "water_temp_ko": "찬물~30℃. 온수·고온건조 금지.",
        "aftercare_ko": (
            "완전 건조 후 착용. 그늘 보관. "
            "예방: 세제 잔여 없이 헹구기, 직사광선·고온건조 피하기."
        ),
        "sense_check_ko": "눈: 누런기·잔여. 손: 미끄럼(세제 잔여) 없음.",
        "success_rate_ko": "표면 때: 양호. 산화 황변: 중간~낮음 — 반드시 사전 고지.",
        "refuse_when_ko": "100% 새것 복원·락스 범벅·고온건조 요구 → 거절.",
        "must_include_ko": "베이킹소다, 락스 금지, 100% 복원 불가",
    }


def _shoe_laces() -> dict[str, str]:
    return {
        "precheck_ko": "운동화 끈은 반드시 빼서 따로. 흰 끈/유색 분리.",
        "why_ko": "[왜 이 순서] 신에 끼운 채 세탁=이염·세척 불량. 흰 끈은 알칼리·고온에 황변.",
        "fresh_path_ko": (
            "(1)끈 분리. (2)찬물+중성 15–30분. (3)연질 솔 또는 세탁망 약코스. "
            "(4)충분히 헹굼. (5)그늘 건조(고온건조 금지). (6)잔여 회색: 베이킹소다 약하게 재시도 — 안 되면 교체 안내."
        ),
        "dried_path_ko": "교체 비용이 더 나을 수 있음 — 고지.",
        "motion_ko": "Cap2. 세게 비틀지 말 것.",
        "water_temp_ko": "찬물~30℃.",
        "aftercare_ko": "신발 마른 뒤 다시 끼우기.",
        "sense_check_ko": "눈: 회색·황변. 코: 이취 없음.",
        "success_rate_ko": "조기: 양호. 오래된 흰끈 황변: 중간↓.",
        "refuse_when_ko": "100% 새것처럼 → 거절·교체 안내.",
    }


def _sneaker_general() -> dict[str, str]:
    return {
        "precheck_ko": "소재 구분(천·메쉬·가죽·스웨이드)·끈·깔창 분리. 흰창 황변이면 흰창 경로. 구두(가죽)와 혼동 금지.",
        "why_ko": "[왜 이 순서] 갑피/밑창 솔·세제 분리. 고온건조=접착·형태 손상.",
        "fresh_path_ko": (
            "(1)끈·깔창 분리, 마른 흙. "
            "【오염 없음】→손세탁 또는 망+≤30℃ 약코스(천·캔버스). "
            "【오염 있음】→갑피 연질+중성 국소 후 동일. "
            "(2)갑피 연질+중성, 밑창 경질(고무만). "
            "(3)헹굼. (4)신문지 채워 그늘 건조 — 고온건조 금지. "
            "(5)가죽/스웨이드 갑피면 해당 가죽 SOP로 전환. "
            "(6)흰창·끈은 별도 미백 경로."
        ),
        "dried_path_ko": "재스팟팅. 접착 분리 위험 고지.",
        "motion_ko": "갑피 Cap1–2 연질. 밑창 Cap2–3 경질.",
        "water_temp_ko": "≤30℃.",
        "aftercare_ko": "완전 건조 후 착용.",
        "sense_check_ko": "눈: 잔여. 손: 미끄럼 없음.",
        "success_rate_ko": "천·캔버스: 양호. 가죽/스웨이드: 별도.",
        "refuse_when_ko": "스웨이드 물세탁·고온건조 강제 → 거절.",
        "must_include_ko": "끈·깔창 분리, 그늘 건조, 고온건조 금지",
        "precheck_vi": "Phan loai vai/mesh/da/suede. Thao day+lot. CAM nham voi giay da tay.",
        "why_vi": "[Tai sao] Tach than/de. Say nong = hong keo.",
        "fresh_path_vi": (
            "(1)Thao day+lot, chai kho. Khong vet → tay/may tui luoi <=30C. "
            "Co vet → spot than sol mem + D2 roi giat. "
            "(2)Than sol mem; de cao su sol cung. (3)Xa. (4)Nhet bao phoi bong mat — CAM say nong. "
            "(5)Da/suede → SOP da. (6)Canh trang → SOP trang."
        ),
        "dried_path_vi": "Spot lai. Bao rui ro keo.",
        "motion_vi": "Than Cap1–2; de Cap2–3.",
        "water_temp_vi": "<=30C.",
        "aftercare_vi": "Kho han moi mang.",
        "sense_check_vi": "Mat: con du. Tay: khong tron.",
        "success_rate_vi": "Vai/canvas: tot. Da/suede: khac.",
        "refuse_when_vi": "Suede ngam nuoc / say nong → tu choi.",
        "must_include_vi": "thao day+lot, phoi bong mat, CAM say nong",
        "precheck_en": "Sort fabric/mesh/leather/suede; remove laces+insoles. Do not treat as leather dress shoes.",
        "why_en": "[Why] Separate upper vs outsole tools. Hot dryer damages glue/shape.",
        "fresh_path_en": (
            "(1)Remove laces/insoles; brush dry soil. "
            "No stain → hand or mesh bag ≤30°C gentle. "
            "With stain → soft brush + mild soap on upper first. "
            "(2)Soft brush upper; hard brush rubber outsole only. "
            "(3)Rinse. (4)Stuff with paper; air-dry shade — no hot dryer. "
            "(5)Leather/suede upper → leather SOP. (6)White midsole → whitening SOP."
        ),
        "dried_path_en": "Re-spot. Disclose glue/separation risk.",
        "motion_en": "Upper Cap1–2 soft; outsole Cap2–3 hard.",
        "water_temp_en": "≤30°C.",
        "aftercare_en": "Wear only when fully dry.",
        "sense_check_en": "Eyes: residue. Hand: no slipperiness.",
        "success_rate_en": "Canvas/fabric: good. Leather/suede: separate path.",
        "refuse_when_en": "Forced suede wet-wash or hot dryer → refuse.",
        "must_include_en": "remove laces/insoles, shade dry, no hot dryer",
    }


def _hat_cap(*, golf: bool = False) -> dict[str, str]:
    label_ko = "골프모자·캡" if golf else "야구모자·캡·일반 모자"
    label_vi = "Mu golf / mu luoi trai" if golf else "Mu luoi trai / baseball / fashion cap"
    label_en = "Golf / sports cap" if golf else "Baseball / fashion cap"
    return {
        "precheck_ko": (
            f"{label_ko}: (A)하드·피티드(버클럼/판지 챙)=국소만 — 세탁기·식기세척기·건조기 금지. "
            "(B)소프트·대드캡=찬물 손세탁 가능(라벨 허용+망만 예외). "
            "가죽·스웨이드 챙→전문. 운동화 SOP와 혼동 금지."
        ),
        "why_ko": (
            "[왜 이 순서] 땀띠=피지·염·단백질. 구조 모자=형태가 상품. "
            "통세탁·고온·건조기=챙 붕괴. New Era식: 중성 국소 → 형태 유지 자연건조."
        ),
        "fresh_path_ko": (
            "(1)하드 vs 소프트 구분. "
            "【하드캡】→ 통세탁·세탁기·식기세척기 금지 — 땀띠·챙만 국소. "
            "【소프트캡】→ 찬물 손세탁 짧게(라벨). "
            "(2)땀띠: 중성 약희석+연질 솔 Cap1–2 원형. "
            "(3)패널·자수: 약한 국소만(이염·로고 손상 주의). "
            "(4)잔여 세제 천으로. (5)크라운에 수건/볼 넣어 형태 → 그늘 자연건조. "
            "(6)건조기·다리미·식기세척기 금지."
        ),
        "dried_path_ko": "땀띠 황변: 산소(흰 천만·테스트) 또는 효소 약하게 1회. 안 되면 고지.",
        "motion_ko": "Cap1–2 연질. 챙 꺾기·강타 금지.",
        "water_temp_ko": "찬물. 하드=국소만.",
        "aftercare_ko": "완전 건조까지 형태 유지. 챙 눌러 보관 금지.",
        "sense_check_ko": "눈: 땀띠·형태. 손: 잔여 세제 없음.",
        "success_rate_ko": "조기 국소: 양호. 이미 챙 변형: 복원 한계.",
        "refuse_when_ko": "세탁기·식기세척기·건조기 강요 → 거절.",
        "must_include_ko": "챙 국소, 형태 유지, 건조기 금지",
        "precheck_vi": (
            f"{label_vi}: (A)Mu CUNG/fitted = CHI spot — CAM may/dishwasher/say. "
            "(B)Mu MEM = tay lanh neu nhan cho. Da/suede vanh → chuyen. CAM nham SOP giay."
        ),
        "why_vi": (
            "[Tai sao] Vanh mo hoi = dau+muoi+protein. Mu cau truc = giu form. "
            "May/say = hong vanh. Spot trung tinh → kho tu nhien giu form."
        ),
        "fresh_path_vi": (
            "(1)Phan loai cung/mem. Mu cung: CAM may/dishwasher — chi spot vanh. "
            "Mu mem: tay lanh ngan. "
            "(2)Vanh: D2/S1 loang + chai mem Cap1–2. "
            "(3)Panel/theu: spot nhe. (4)Lau du. "
            "(5)Nhet khan/bat giu crown + chinh vanh. (6)Phoi bong mat — CAM say/ui/dishwasher."
        ),
        "dried_path_vi": "Vanh vang: A3/enzyme nhe 1 lan (test). Khong het → bao khach.",
        "motion_vi": "Cap1–2 chai mem; CAM gap vanh.",
        "water_temp_vi": "Lanh. Mu cung = spot.",
        "aftercare_vi": "Giu form den kho. CAM dep vanh.",
        "sense_check_vi": "Mat: vanh/form. Tay: het xa phong.",
        "success_rate_vi": "Spot som: tot. Vanh bien dang: gioi han.",
        "refuse_when_vi": "Bat may/dishwasher/say → tu choi.",
        "must_include_vi": "spot vanh, giu form, CAM say",
        "precheck_en": (
            f"{label_en}: (A)Structured/fitted = spot-clean only — no washer/dishwasher/dryer. "
            "(B)Soft/dad cap = cool hand wash if label allows. Leather/suede brim → pro. Not a sneaker SOP."
        ),
        "why_en": (
            "[Why] Sweatband = oil+salt+protein. Structured crown = product value. "
            "Machine/heat collapses brim. Mild spot → air-dry holding shape."
        ),
        "fresh_path_en": (
            "(1)Hard vs soft. Structured: no washer/dishwasher — sweatband/brim spot only. "
            "Soft: short cool hand wash if labeled. "
            "(2)Sweatband: diluted mild soap + soft brush Cap1–2 circles. "
            "(3)Panels/embroidery: light spot only. (4)Wipe residue. "
            "(5)Stuff crown with towel/ball; reshape brim; shade air-dry. "
            "(6)No dryer, iron, or dishwasher."
        ),
        "dried_path_en": "Yellow sweatband: one careful oxygen/enzyme try on white fabric only — then disclose.",
        "motion_en": "Cap1–2 soft brush; do not bend/crush brim.",
        "water_temp_en": "Cold. Structured = spot only.",
        "aftercare_en": "Keep shape until dry. Do not store with crushed brim.",
        "sense_check_en": "Eyes: sweatband/shape. Hand: no soap film.",
        "success_rate_en": "Early spot: good. Already warped brim: limited restore.",
        "refuse_when_en": "Forced washer/dishwasher/dryer → refuse.",
        "must_include_en": "brim spot-clean, hold shape, no dryer",
    }


def _linen_garment(*, finish: bool = False) -> dict[str, str]:
    finish_bit = (
        "다림질: 약간 촉촉할 때 고온(약 180–200℃) 또는 스팀. "
        "마는 주름이 특성이므로 완전 무주름 약속 금지. "
        "에어드레서·스팀행거: 일상 주름·냄새에 유용, 칼주름·웨딩급 마무리는 수동 스팀/다리미."
    )
    return {
        "precheck_ko": (
            "마(린넨) 의류: 라벨. 수축 3–8% 가능 — 고객 사전 고지(필수 멘트). "
            "진한 색·이염 테스트. 정장형 마는 안감·구조 확인. "
            "호텔 시트·수건(업소 린넨)과 혼동하지 말 것."
        ),
        "why_ko": (
            "[왜 이 순서] 마=셀룰로오스, 면보다 구김·수축. "
            "온화 물세탁(또는 라벨 허용 시 상업용 섬세 30–40℃), 강탈수·고온건조 주의. "
            "얼룩은 면과 유사하나 마찰 주의. 마무리는 고온 다림질·스팀이 핵심."
        ),
        "fresh_path_ko": (
            "(1)라벨·색이염 테스트. 「수축될 수 있습니다」 고지. "
            "(2)얼룩: 찬물 블롯 → 중성/일반세제 국소(단백질·탄닌·기름은 해당 얼룩 SOP). "
            "(3)세탁: 손세탁 또는 상업용 섬세 30–40℃, 세제 소량, 탈수 약. "
            "강하게 비틀어 짜기·고온 삶기 비권장. "
            "(4)그늘·형태 맞춰 건조(고온건조기 짧게만·가능하면 자연건조). "
            f"(5){finish_bit} "
            "(6)표백: 흰 마만 산소 검토. 유색 락스 금지."
        ),
        "dried_path_ko": "마른 얼룩: 국소 재처리. 이미 수축: 복원 한계 고지.",
        "motion_ko": "Cap1–2. 세게 문지르기·강탈수 금지.",
        "water_temp_ko": "30–40℃(라벨 최고 이하). 불확실하면 낮게.",
        "aftercare_ko": "걸이 보관. 구김은 특성 — 스팀/에어드레서로 완화. 무주름 약속 금지.",
        "sense_check_ko": "눈: 이염·수축. 손: 뻣뻣함(잔여).",
        "success_rate_ko": "온화 세탁+고온 다림질: 양호. 무주름 약속: 불가.",
        "refuse_when_ko": "수축 0%·완전 무주름 요구, 유색 락스 → 거절.",
        "must_include_ko": "수축 고지, 30–40℃, 다림질",
    }


def _finishing_matrix() -> dict[str, str]:
    return {
        "precheck_ko": (
            "피니싱(다림질·스팀·에어드레서): 얼룩·세제 잔여가 없는 뒤에만. "
            "열=열고착. 케어라벨 다리미 기호 확인."
        ),
        "why_ko": (
            "[왜 이 순서] 세탁소=세탁+마무리. "
            "접촉 다림질 vs 스팀(비접촉) vs 에어드레서(스팀+공기)를 품목에 맞게. "
            "에어드레서(LG 스타일러·삼성 에어드레서)=일상 구김·냄새 보조. "
            "정장·울·어깨패드=스팀 위주(판 누르기 금지). "
            "와이셔츠=순서 다림질(+풀). 마·면=고온·촉촉. 실크=저온·이면·스팀 주의."
        ),
        "fresh_path_ko": (
            "(1)강광으로 잔여 얼룩 확인 — 있으면 다리지 말 것. "
            "(2)에어드레서(LG 스타일러·삼성 에어드레서 등) 사용법: "
            "옷걸이에 걸어 넣고, 섬세/표준을 라벨에 맞게 선택. "
            "일상 정장·코튼·냄새·가벼운 구김에 적합. "
            "웨딩·구조 복잡한 수트·칼주름 필수 셔츠는 에어드레서만으로 부족 — "
            "수동 스팀/셔츠 프레스 병행. "
            "가죽·스웨이드·모피·인조가죽은 에어드레서 고온 금지. "
            "(3)스팀 다리미: 정장·자켓은 2–3cm 띄워 분사(어깨·라펠 판 접촉 금지). "
            "와이셔츠: 풀(선택)→깃→커프→소매→어깨→몸판. "
            "여성·웨딩드레스: 비즈·얇은 겹은 스팀만·이면·보호천. "
            "마(린넨)·면: 촉촉할 때 고온 다림질. "
            "(4)실크·레이온: 저온·이면·스팀 과다=물점. "
            "(5)고객 인도 전 형태·광택(누름 자국) 확인."
        ),
        "dried_path_ko": "이미 열고착 얼룩: 피니싱 중단, 재세탁 검토.",
        "motion_ko": "에어드레서 Cap0. 정장 스팀 Cap0–1. 셔츠 Cap2–3 판. 드레스 장식 Cap0–1.",
        "water_temp_ko": "해당 없음(스팀·에어드레서 온도는 라벨).",
        "aftercare_ko": (
            "에어드레서 후 바로 꺼내 식히며 형태. "
            "식힌 뒤 포장. 얇은 플라스틱에 오래 가두지 말 것(습기)."
        ),
        "sense_check_ko": "눈: 주름·광택 손상·비즈. 손: 어깨 형태.",
        "success_rate_ko": "품목별 기법 준수: 높음. 에어드레서만으로 칼주름: 한계.",
        "refuse_when_ko": "잔여 얼룩 상태 다림질, 비즈에 판 다리미, 모피 고온 → 거절.",
        "must_include_ko": "에어드레서, 스팀, 잔여 얼룩 금지",
    }


def _suit_finishing(*, summer: bool = False) -> dict[str, str]:
    body = (
        "여름 린넨·코튼 수트: 라벨 허용 시 온화 물세탁 후 촉촉할 때 다림질. 캔버스·복잡한 안감이면 드라이/전문."
        if summer
        else "울 정장: 잦은 드라이는 섬유 약화 — 얼룩·냄새 있을 때만. 평소는 솔·걸이·휴지(24–48h)."
    )
    return {
        "precheck_ko": f"정장·수트: 사진. 캔버스/어깨패드 확인. {body}",
        "why_ko": (
            "[왜 이 순서] 정장=형태가 상품. 세탁기 가정코스=붕괴. "
            "피니싱은 스팀 위주 — 판으로 누르면 광택·패드 변형. "
            "에어드레서는 냄새·가벼운 구김 보조, 행사·납품 칼주름은 수동 스팀/프레스."
        ),
        "fresh_path_ko": (
            "(1)얼룩 있으면 국소만 또는 드라이. 무리한 매장 물세탁 금지(구조 복잡 시). "
            "(2)피니싱: 스팀 다리미 2–3cm, 라펠·어깨는 손으로 곡선. "
            "바지: 칼주름은 천 대고 신중 또는 전문 프레스. 판 직접 접촉 최소화. "
            "(3)에어드레서(LG/삼성 등): 냄새·가벼운 구김 OK. "
            "완벽한 칼주름·행사 직전은 에어드레서만으로 끝내지 말고 수동 스팀 병행. "
            "(4)넓은 나무 옷걸이에 식히기. "
            "(5)고객에 형태 유지·재착용 휴식 안내."
        ),
        "dried_path_ko": "이미 가정 세탁기: 형태 손상 고지, 추가 강처리 금지.",
        "motion_ko": "스팀 Cap0–1. 판 직접 접촉 최소화.",
        "water_temp_ko": "물세탁 시 라벨·섬세만.",
        "aftercare_ko": (
            "통풍 옷장. 비닐 장기 밀봉 금지. "
            "에어드레서로 냄새·가벼운 구김 보완 가능 — 칼주름·행사 직전은 수동 스팀 병행."
        ),
        "sense_check_ko": "눈: 어깨·라펠·광택. 손: 패드.",
        "success_rate_ko": "스팀 피니싱: 높음. 에어드레서만: 중간. 가정기 세탁 후: 낮음.",
        "refuse_when_ko": "가정 세탁기 강요·100% 형태 복원 → 거절.",
        "must_include_ko": "스팀, 에어드레서, 판 직접 접촉 금지",
    }


def _dress_finishing(*, wedding: bool = False) -> dict[str, str]:
    pre = (
        "웨딩·화려한 드레스: 비즈·자수·얇은 겹·트레인. 사진·손상 사전 고지. "
        "물세탁 가능 여부는 라벨·안감·장식에 따름 — 불확실하면 전문/거절."
        if wedding
        else "여성 드레스: 가장 약한 소재 기준(실크·레이온·장식)."
    )
    return {
        "precheck_ko": pre,
        "why_ko": (
            "[왜 이 순서] 드레스는 세탁보다 피니싱 사고가 많다. "
            "판 다리미가 비즈·필름 장식을 녹이거나 누름. 스팀·보호천·이면. "
            "에어드레서는 보관·가벼운 구김용 — 웨딩 당일 유일 수단으로 쓰지 말 것."
        ),
        "fresh_path_ko": (
            "(1)소재·장식·라벨. 웨딩/고가=보수적. "
            "(2)세탁: 라벨 허용 시 섬세·망·약탈수. 불확실=전문 드라이/웨딩 클리너. "
            "(3)피니싱: 스팀만 또는 이면+보호천. 비즈·스팽글에 판 금지. 트레인은 펼쳐 스팀. "
            "(4)에어드레서: 가벼운 구김·보관 냄새용. 웨딩 당일 마무리의 유일한 수단으로 쓰지 말 것. "
            "(5)넓은 공간에서 식히며 형태. "
            "(6)100% 주름·광택 복원 약속 금지."
        ),
        "dried_path_ko": "장식 손상·물점: 추가 열처리 중단.",
        "motion_ko": "Cap0–1 스팀. 장식 부위 Cap0.",
        "water_temp_ko": "섬세 저온 또는 전문.",
        "aftercare_ko": "걸이·커버. 접어 장기보관 시 주름 고지.",
        "sense_check_ko": "눈: 비즈·트레인·물점.",
        "success_rate_ko": "스팀 피니싱: 양호. 가정기+판 다리미: 사고 위험.",
        "refuse_when_ko": "불확실 소재 세탁기 강요, 비즈에 판 다리미 → 거절.",
        "must_include_ko": "스팀, 비즈 판 금지, 에어드레서 한계",
    }


def _dress_shirt_finishing() -> dict[str, str]:
    return {
        "precheck_ko": "와이셔츠: 흰/유색 분리. 황변·목때면 해당 얼룩 SOP 먼저. 잔여 없이 피니싱.",
        "why_ko": (
            "[왜 이 순서] 셔츠는 칼주름·깃이 상품. "
            "순서: 깃→커프→소매→어깨→몸. 풀(전분)은 선택. "
            "에어드레서는 보조, 행사·매장 납품은 수동 다림질이 표준."
        ),
        "fresh_path_ko": (
            "(1)세탁(흰면 고온 가능·라벨). 잔여 황변이면 피니싱 전 재처리. "
            "(2)약간 촉촉한 상태 또는 분무. 풀 사용 시 고르게·5분 흡수. "
            "(3)깃 안→밖, 포인트 살리기. 커프·소매 솔기. 어깨는 곡면. 몸판은 단추 피해 다림. "
            "(4)에어드레서: 일상 구김·보관용. 납품용 칼주름은 프레스/수동이 표준 — "
            "에어드레서만으로 끝내지 말 것. "
            "(5)걸거나 바로 포장. 접으면 풀·주름 효과↓."
        ),
        "dried_path_ko": "이미 완전 건조면 분무 후 다림.",
        "motion_ko": "Cap2–3. 깃·커프는 또렷하게.",
        "water_temp_ko": "세탁은 라벨. 다림은 면 고온대.",
        "aftercare_ko": "걸이 보관. 넥 지지.",
        "sense_check_ko": "눈: 깃·커프·칼주름. 손: 풀 균일.",
        "success_rate_ko": "순서 다림질: 높음. 에어드레서만: 중간.",
        "refuse_when_ko": "황변 남은 채 다림 강요 → 거절(열고착).",
        "must_include_ko": "깃→커프→소매→몸, 에어드레서 보조",
    }

