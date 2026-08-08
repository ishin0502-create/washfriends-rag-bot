# -*- coding: utf-8 -*-
"""Specialty item care — goose duvet typo, hotel linen, machine profile."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graphrag_engine import _empty_graph_reply, _infer_item_from_text
from protocol import apply_protocol_to_graph
from specialty_item_care import apply_specialty_item_education, education_for


def test_goose_typo_maps():
    assert _infer_item_from_text("구스이블 세탁방법 알려줘") == "I_DUVET_GOOSE"
    assert _infer_item_from_text("구스이불 세탁방법") == "I_DUVET_GOOSE"


def test_hotel_sheet_not_cotton_duvet():
    assert _infer_item_from_text("호텔 이불 시트 일반 세탁") == "I_BED_SHEET"
    assert _infer_item_from_text("호텔 흰 수건 세탁") == "I_TOWEL"


def test_empty_reply_item_care_not_stain():
    msg = _empty_graph_reply({"lang": "ko", "_raw": "구스이블 세탁방법 알려줘"})
    assert "얼룩인가요" not in msg
    assert "구스" in msg or "이불" in msg


def test_goose_sop_has_tennis_and_no_perc():
    edu = education_for("I_DUVET_GOOSE")
    path = edu["fresh_path_ko"]
    assert "테니스" in path or "건조볼" in path
    assert "30" in path
    assert "퍼크" in edu["why_ko"] or "PERC" in edu["why_ko"]


def test_apply_goose_graph():
    g = {
        "item_context": {"id": "I_DUVET_GOOSE", "name_ko": "구스이불"},
        "stain_context": {"group": "item_care", "id": "I_DUVET_GOOSE", "fresh_path_ko": "얇은 시드"},
        "tools": [{"id": "T_CLOTH"}],
        "chemicals": [{"code": "A3"}],
    }
    out = apply_protocol_to_graph(
        g, entities={"item_id": "I_DUVET_GOOSE", "_raw": "구스이불 세탁방법"}
    )
    path = (out.get("stain_context") or {}).get("fresh_path_ko") or ""
    assert "테니스" in path or "건조볼" in path
    assert out.get("specialty_item_care") or "30" in path
    codes = [c.get("code") for c in out.get("chemicals") or []]
    assert "S1" in codes


def test_hotel_towel_bio_branch():
    edu = education_for(
        "I_TOWEL",
        entities={"_raw": "호텔 흰 수건에 피가 묻었어요"},
    )
    assert "찬물" in edu["fresh_path_ko"]
    assert "60" in edu["fresh_path_ko"] or "산소" in edu["fresh_path_ko"]


def test_machine_profile_has_courses():
    edu = education_for("I_MACHINE_PROFILE")
    assert "섬세" in edu["fresh_path_ko"]
    assert "60" in edu["fresh_path_ko"]
    assert "다운" in edu["fresh_path_ko"] or "구스" in edu["fresh_path_ko"]


def test_padding_sop():
    edu = education_for("I_DOWN_JACKET")
    assert "테니스" in edu["fresh_path_ko"]
    assert "전면" in edu["fresh_path_ko"] or "≤30" in edu["fresh_path_ko"] or "30" in edu["fresh_path_ko"]


def test_faux_leather_not_real_leather():
    assert _infer_item_from_text("인조가죽 자켓 세탁") == "I_FAUX_LEATHER"
    assert _infer_item_from_text("레자 코트 관리") == "I_FAUX_LEATHER"
    assert _infer_item_from_text("가죽옷 곰팡이") == "I_LEATHER_GARMENT"
    edu = education_for("I_FAUX_LEATHER")
    assert "크림" in edu["fresh_path_ko"] or "금지" in edu["fresh_path_ko"]
    assert "세탁기" in edu["fresh_path_ko"] or "통담금" in edu.get("why_ko", "")


def test_sneaker_whitening_and_laces():
    assert _infer_item_from_text("운동화 흰창 누렇게") == "I_SNEAKER_WHITE"
    assert _infer_item_from_text("신발끈 하얗게") == "I_SHOE_LACES"
    edu = education_for("I_SNEAKER_WHITE")
    assert "베이킹" in edu["fresh_path_ko"] or "중성" in edu["fresh_path_ko"]
    assert "락스" in edu["why_ko"] or "황변" in edu["why_ko"]


def test_linen_and_finishing():
    assert _infer_item_from_text("마소재 의류 세탁방법") == "I_LINEN_GARMENT"
    assert _infer_item_from_text("에어드레서 사용법") == "I_FINISHING"
    assert _infer_item_from_text("정장 다림질") == "I_SUIT"
    linen = education_for("I_LINEN_GARMENT")
    assert "수축" in linen["precheck_ko"] or "수축" in linen["why_ko"]
    assert "다림질" in linen["fresh_path_ko"] or "스팀" in linen["fresh_path_ko"]
    fin = education_for("I_FINISHING")
    assert "에어드레서" in fin["fresh_path_ko"]
    suit = education_for("I_SUIT", entities={"_raw": "양복 스팀 다림질"})
    assert "스팀" in suit["fresh_path_ko"] or "에어드레서" in suit["fresh_path_ko"]


def test_apply_faux_leather_graph():
    g = {
        "item_context": {"id": "I_FAUX_LEATHER", "name_ko": "인조가죽"},
        "stain_context": {"group": "item_care", "id": "I_FAUX_LEATHER"},
        "tools": [{"id": "T_CLOTH"}],
        "chemicals": [],
    }
    out = apply_protocol_to_graph(
        g, entities={"item_id": "I_FAUX_LEATHER", "_raw": "인조가죽 세탁"}
    )
    assert out.get("specialty_item_care")
    assert out.get("leather_care") is not True
    codes = [c.get("code") for c in out.get("chemicals") or []]
    assert "D2" in codes


def test_must_include_on_goose_and_suit():
    goose = education_for("I_DUVET_GOOSE")
    assert "테니스볼" in goose["must_include_ko"]
    assert "테니스볼" in goose["aftercare_ko"]
    g = {
        "item_context": {"id": "I_DUVET_GOOSE", "name_ko": "구스이불"},
        "stain_context": {"group": "item_care", "id": "I_DUVET_GOOSE"},
        "tools": [],
        "chemicals": [],
    }
    out = apply_specialty_item_education(
        g, entities={"item_id": "I_DUVET_GOOSE", "_raw": "구스이불 세탁"}
    )
    assert "테니스볼" in (out.get("must_include_ko") or "")
    assert "테니스볼" in ((out.get("stain_context") or {}).get("must_include_ko") or "")

    faux = education_for("I_FAUX_LEATHER")
    assert "체크리스트" in faux["precheck_ko"] or "뒷면" in faux["precheck_ko"]
    white = education_for("I_SNEAKER_WHITE")
    assert "100%" in white["precheck_ko"]
    suit = education_for("I_SUIT", entities={"_raw": "정장 다림질"})
    assert "에어드레서" in suit["fresh_path_ko"]
    assert "에어드레서" in suit["must_include_ko"]


if __name__ == "__main__":
    test_goose_typo_maps()
    test_hotel_sheet_not_cotton_duvet()
    test_empty_reply_item_care_not_stain()
    test_goose_sop_has_tennis_and_no_perc()
    test_apply_goose_graph()
    test_hotel_towel_bio_branch()
    test_machine_profile_has_courses()
    test_padding_sop()
    test_faux_leather_not_real_leather()
    test_sneaker_whitening_and_laces()
    test_linen_and_finishing()
    test_apply_faux_leather_graph()
    test_must_include_on_goose_and_suit()
    print("OK specialty_item_care")
