# -*- coding: utf-8 -*-
"""Golden-set style unit tests for fabric×chemistry matching (no Neo4j/LLM)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from match_diagnosis import (
    apply_weight_to_tools,
    build_match_diagnosis,
    chemistry_layers,
    chemistry_summary,
    infer_fabric_weight,
)


def test_oil_is_hydrophobic_layer():
    sc = {"contains_oil": True, "contains_protein": False, "contains_tannin": False, "contains_dye": False}
    assert chemistry_layers(sc) == ["oil_hydrophobic"]
    assert "소수성" in chemistry_summary(sc, "ko")


def test_kimchi_layers_order():
    sc = {"contains_oil": True, "contains_tannin": True, "contains_dye": True, "contains_protein": False}
    assert chemistry_layers(sc) == ["oil_hydrophobic", "tannin", "dye_pigment"]


def test_thin_silk_necktie():
    assert infer_fabric_weight("실크 넥타이에 케첩", fabric_type="silk", item_id="I_NECKTIE") == "thin"


def test_thick_denim_keyword():
    assert infer_fabric_weight("두꺼운 청바지에 기름", fabric_type="denim", item_id="I_DENIM") == "thick"


def test_thin_drops_soak_bin():
    g = {
        "tools": [
            {"id": "T_SOAK_BIN", "name_ko": "담금통"},
            {"id": "T_CLOTH", "name_ko": "흰 천"},
            {"id": "T_BRUSH_HARD", "name_ko": "경질솔"},
        ],
        "fabric_context": {"id": "F4", "name": "Silk", "name_vi": "lua"},
        "stain_context": {"id": "S_KETCHUP", "contains_oil": True, "contains_tannin": True, "contains_dye": True},
    }
    out = apply_weight_to_tools(g, "thin")
    ids = {t["id"] for t in out["tools"]}
    assert "T_SOAK_BIN" not in ids
    assert "T_BRUSH_HARD" not in ids
    assert "T_CLOTH" in ids


def test_match_diagnosis_asks_when_fabric_unknown():
    g = {
        "stain_context": {
            "id": "S_COOKING_OIL",
            "name_ko": "식용유",
            "contains_oil": True,
        },
        "tools": [],
    }
    card = build_match_diagnosis(g, entities={}, raw_text="옷에 기름이 묻었어요")
    assert card["fabric_weight"] in ("unknown", "medium", "thin", "thick")
    assert card["ask_fabric_ko"]
    assert "소수성" in card["chemistry_ko"]


def test_match_diagnosis_no_ask_when_fabric_known():
    g = {
        "fabric_context": {"id": "F1", "name": "Cotton", "name_vi": "cotton"},
        "stain_context": {"id": "S_BLOOD_FRESH", "contains_protein": True, "name_ko": "피"},
    }
    card = build_match_diagnosis(
        g,
        entities={"fabric_type": "cotton", "fabric_weight": "medium"},
        raw_text="면 티셔츠에 피가",
    )
    assert card["fabric_type"] == "cotton"
    assert card["ask_fabric_ko"] == ""
    assert "단백질" in card["chemistry_ko"]


def test_ko_edu_covers_all_rich_stains():
    from ko_stain_education import KO_STAIN_EDU
    assert len(KO_STAIN_EDU) >= 54
    for sid, row in KO_STAIN_EDU.items():
        assert row["why_ko"].startswith("[왜 이 순서]"), sid
        assert row["fresh_path_ko"].strip(), sid
        assert row["dried_path_ko"].strip(), sid
        # Oil stains must mention hydrophobic / oil handling in why
        if sid in ("S_COOKING_OIL", "S_GREASE", "S_MOTORBIKE_OIL", "S_ENGINE_OIL", "S_SUNSCREEN"):
            assert "소수성" in row["why_ko"] or "오일" in row["why_ko"] or "지방" in row["why_ko"], sid


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in tests:
        try:
            fn()
            print("OK", fn.__name__)
        except Exception as e:
            failed += 1
            print("FAIL", fn.__name__, e)
    raise SystemExit(1 if failed else 0)
