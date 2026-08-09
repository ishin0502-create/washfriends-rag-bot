# -*- coding: utf-8 -*-
"""Unit checks for education gaps v7 (dilution, iodine/chili, care label, drills)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from education_gaps_v7 import (
    DILUTION_V7,
    OPS_DRILLS_V7,
    VN_STAIN_SEED_V7,
    care_label_constraints,
    dilution_seed_rows,
)
from protocol import CHEM_META, PROTOCOL_BUILDERS, _chem_blocked, _fabric_flags
from w2_ops_rescue import DILUTION_GAPS, OPS_DRILLS, rescue_card_for_stain


def test_dilution_sync():
    codes = {d["code"] for d in DILUTION_V7}
    assert {"E2", "B2", "A2", "E3", "B1", "E1"} <= codes
    gap_codes = {d["code"] for d in DILUTION_GAPS}
    assert {"E2", "B2", "A2"} <= gap_codes
    for row in dilution_seed_rows():
        meta = CHEM_META.get(row["code"], {})
        assert meta.get("dilution_ko") == row["dilution_ko"], row["code"]
    assert "1 : 물 10–20" in CHEM_META["B2"]["dilution_ko"] or "10–20" in CHEM_META["B2"]["dilution_ko"]
    assert "아세테이트" in CHEM_META["A2"]["dilution_ko"]
    assert "큰술" in CHEM_META["E2"]["dilution_ko"]


def test_vn_stains_protocol():
    ids = {r["id"] for r in VN_STAIN_SEED_V7}
    assert ids == {"S_IODINE", "S_CHILI"}
    assert "S_IODINE" in PROTOCOL_BUILDERS
    assert "S_CHILI" in PROTOCOL_BUILDERS
    card = rescue_card_for_stain({"id": "S_IODINE", "dried_path_ko": "알코올"})
    assert "2차" in card["rescue_2nd_ko"] or "알코올" in card["rescue_2nd_ko"]


def test_ops_drills_v7():
    assert set(OPS_DRILLS_V7) <= set(OPS_DRILLS)
    for iid in ("I_CLAIM_SCRIPT", "I_PRICING_SCRIPT", "I_QUIZ_STAINS", "I_QUIZ_FABRIC"):
        row = OPS_DRILLS[iid]
        assert row.get("fresh_path_ko")
        assert row.get("refuse_when_ko")
        assert "가격표" in row["fresh_path_ko"] or "질문" in row["fresh_path_ko"] or "Q1" in row["fresh_path_ko"]


def test_care_label_constraints():
    flags = care_label_constraints(
        {
            "fiber_text": "cotton 100%",
            "wash": {"max_temp_c": 30, "hand_wash_only": True},
            "bleach": {"do_not_bleach": True},
        }
    )
    assert flags["_from_care_label"] is True
    assert flags["care_max_temp_c"] == 30
    assert flags["care_no_bleach"] is True
    assert flags["care_hand_wash_only"] is True

    ff = _fabric_flags({}, {**flags, "fabric_type": "cotton"})
    assert ff["no_oxygen"] is True
    blocked, _, _ = _chem_blocked("B2", ff, "white")
    assert blocked is True

    ox_only = care_label_constraints({"bleach": {"oxygen_only": True, "do_not_bleach": True}})
    ff2 = _fabric_flags({}, {**ox_only, "fabric_type": "cotton"})
    assert ff2.get("no_chlorine") is True
    b_chl, _, _ = _chem_blocked("B2", ff2, "white")
    assert b_chl is True


def test_hard_route_helpers():
    from graphrag_engine import _infer_item_from_text

    assert _infer_item_from_text("클레임 대응 스크립트") == "I_CLAIM_SCRIPT"
    assert _infer_item_from_text("요금 가격표 안내") == "I_PRICING_SCRIPT"
    assert _infer_item_from_text("얼룩 퀴즈") == "I_QUIZ_STAINS"
    assert _infer_item_from_text("원단 연습문제") == "I_QUIZ_FABRIC"


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            fn()
            print("OK", name)
        except Exception as e:
            failed += 1
            print("FAIL", name, e)
    raise SystemExit(1 if failed else 0)
