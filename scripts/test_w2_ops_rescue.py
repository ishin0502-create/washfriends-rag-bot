# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from w2_ops_rescue import DILUTION_GAPS, OPS_DRILLS, rescue_card_for_stain
from graphrag_engine import _enrich_rescue_aftercare, _enrich_teach_slots


def test_ops_five():
    core = {
        "I_CARE_LABEL",
        "I_DRY_VS_WET",
        "I_INTAKE_SCRIPT",
        "I_WATER_HARDNESS",
        "I_CLAIM_SCRIPT",
        "I_PRICING_SCRIPT",
        "I_QUIZ_STAINS",
        "I_QUIZ_FABRIC",
    }
    assert core <= set(OPS_DRILLS)
    for iid in core:
        row = OPS_DRILLS[iid]
        assert row.get("fresh_path_ko")
        assert row.get("refuse_when_ko")
        assert (
            "질문" in row["fresh_path_ko"]
            or "질문" in row.get("why_ko", "")
            or "Q1" in row["fresh_path_ko"]
            or "(1)" in row["fresh_path_ko"]
        )

def test_dilution_gaps():
    codes = {d["code"] for d in DILUTION_GAPS}
    assert {"E2", "B2", "A2", "WF_SOFT", "WF_FRAG"} <= codes


def test_rescue_oil():
    card = rescue_card_for_stain({"contains_oil": True, "group_id": "G2", "dried_path_ko": "흡착 반복"})
    assert "2차" in card["rescue_2nd_ko"]
    assert "고지" in card["rescue_disclose_ko"]


def test_enrich_aftercare_force():
    g = {
        "stain_context": {
            "id": "S_COOKING_OIL",
            "group_id": "G2",
            "contains_oil": True,
            "aftercare_ko": "미끄럼 확인.",
            "dried_path_ko": "전분 반복",
        }
    }
    out = _enrich_rescue_aftercare(g)
    sc = out["stain_context"]
    assert "강광" in sc["aftercare_ko"]
    assert "열고착" in sc["aftercare_ko"]
    assert sc["rescue_2nd_ko"]
    assert "100%" in sc["rescue_disclose_ko"]


def test_teach_then_rescue():
    g = {
        "stain_context": {
            "id": "S_RED_WINE",
            "group_id": "G3",
            "contains_tannin": True,
            "contains_dye": True,
        }
    }
    out = _enrich_teach_slots(g)
    assert "강광" in (out["stain_context"].get("aftercare_ko") or "")
    assert out["stain_context"].get("rescue_2nd_ko")


if __name__ == "__main__":
    failed = 0
    for fn in [v for k, v in list(globals().items()) if k.startswith("test_")]:
        try:
            fn()
            print("OK", fn.__name__)
        except Exception as e:
            failed += 1
            print("FAIL", fn.__name__, e)
    raise SystemExit(1 if failed else 0)
