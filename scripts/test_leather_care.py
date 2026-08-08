# -*- coding: utf-8 -*-
"""Leather / suede education — mold vs routine; no textile vinegar soak."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leather_care import apply_leather_education, leather_chemicals_for
from match_diagnosis import chemistry_layers, chemistry_summary
from protocol import apply_protocol_to_graph


def _base_graph(item_id: str, *, tools=None, chems=None, stain_id: str = ""):
    sc = {"group": "item_care", "id": item_id, "fresh_path_ko": "구 시드 텍스트"}
    if stain_id:
        sc = {
            "id": stain_id,
            "contains_protein": False,
            "contains_tannin": False,
            "fresh_path_ko": "섬유 식초 통담금 경로",
        }
    return {
        "item_context": {"id": item_id, "name_ko": item_id},
        "stain_context": sc,
        "tools": tools or [
            {"id": "T_CLOTH", "use_for_ko": "흰 천만"},
            {"id": "T_SOAK_BIN", "use_for_ko": "식초 담금"},
            {"id": "T_SPRAY", "use_for_ko": "식초 분무"},
            {"id": "T_TIMER", "use_for_ko": "15분"},
        ],
        "chemicals": chems or [{"code": "A3", "name_ko": "흰 식초"}],
    }


def test_leather_mold_has_cream_ppe_no_soak():
    g = _base_graph("I_LEATHER_GARMENT", stain_id="S_MILDEW")
    out = apply_protocol_to_graph(
        g,
        entities={
            "item_id": "I_LEATHER_GARMENT",
            "stain_id": "S_MILDEW",
            "_raw": "가죽옷에 곰팡이가 생겼어요",
        },
    )
    assert out.get("leather_care") is True
    codes = [c.get("code") for c in out.get("chemicals") or []]
    assert "L2" in codes, codes
    assert "L1" in codes
    assert "A3" not in codes
    tool_ids = [t.get("id") for t in out.get("tools") or []]
    assert "T_GLOVE_NITRILE" in tool_ids
    assert "T_MASK" in tool_ids
    assert "T_SOAK_BIN" not in tool_ids
    assert "T_SPRAY" not in tool_ids
    path = (out.get("stain_context") or {}).get("fresh_path_ko") or ""
    assert "가죽 크림" in path or "L2" in path
    assert "통담금" in path or "식초" in path  # explicit ban
    assert "흔들며 치료" not in path
    assert (out.get("stain_context") or {}).get("contains_protein") is False


def test_leather_routine_cream_no_mold_ppe_required():
    g = _base_graph("I_LEATHER_BAG")
    # Seed wrongly includes PPE — routine must drop it
    g["tools"] = [
        {"id": "T_CLOTH"},
        {"id": "T_GLOVE_NITRILE"},
        {"id": "T_MASK"},
        {"id": "T_SOAK_BIN"},
    ]
    out = apply_leather_education(
        g, entities={"item_id": "I_LEATHER_BAG", "_raw": "가죽가방 관리 방법"}
    )
    codes = [c.get("code") for c in out.get("chemicals") or []]
    assert codes == ["L1", "L2", "L3"] or set(codes) >= {"L1", "L2", "L3"}
    tool_ids = [t.get("id") for t in out.get("tools") or []]
    assert "T_GLOVE_NITRILE" not in tool_ids
    assert "T_MASK" not in tool_ids
    assert "T_SOAK_BIN" not in tool_ids
    path = (out.get("stain_context") or {}).get("fresh_path_ko") or ""
    assert "L2" in path or "크림" in path
    assert "곰팡이" not in path or "관리" in path


def test_suede_mold_no_water_cleaner():
    g = _base_graph("I_SUEDE_GARMENT", stain_id="S_MILDEW")
    g["chemicals"] = [
        {"code": "A3", "name_ko": "흰 식초"},
        {"code": "B1", "name_ko": "산소표백"},
        {"code": "B2", "name_ko": "락스"},
    ]
    out = apply_protocol_to_graph(
        g,
        entities={
            "item_id": "I_SUEDE_GARMENT",
            "stain_id": "S_MILDEW",
            "_raw": "스웨이드에 곰팡이",
        },
    )
    codes = [c.get("code") for c in out.get("chemicals") or []]
    assert codes == []
    assert out.get("empty_chems_ok") is True
    assert "식초" in (out.get("chem_forbid_ko") or "")
    path = (out.get("stain_context") or {}).get("fresh_path_ko") or ""
    assert "물" in path or "금지" in path
    tool_ids = [t.get("id") for t in out.get("tools") or []]
    assert "T_BRUSH_SOFT" in tool_ids
    assert "T_SOAK_BIN" not in tool_ids
    assert "T_GLOVE_NITRILE" in tool_ids  # mold PPE ok


def test_shoe_glove_same_framework():
    for iid in ("I_LEATHER_SHOE", "I_GLOVE_LEATHER"):
        chems = leather_chemicals_for(iid, mold=True)
        assert any(c["code"] == "L2" for c in chems)
        out = apply_leather_education(
            _base_graph(iid, stain_id="S_MILDEW"),
            entities={"item_id": iid, "stain_id": "S_MILDEW", "_raw": "곰팡이"},
        )
        assert out.get("leather_care") is True
        assert any(c.get("code") == "L2" for c in out["chemicals"])


def test_mildew_chemistry_not_protein():
    layers = chemistry_layers({"id": "S_MILDEW", "contains_protein": True})
    assert layers == ["mold_spore"]
    assert "단백질" not in chemistry_summary({"id": "S_MILDEW"}, "ko") or "아님" in chemistry_summary(
        {"id": "S_MILDEW"}, "ko"
    )


if __name__ == "__main__":
    test_leather_mold_has_cream_ppe_no_soak()
    test_leather_routine_cream_no_mold_ppe_required()
    test_suede_mold_no_water_cleaner()
    test_shoe_glove_same_framework()
    test_mildew_chemistry_not_protein()
    print("OK leather_care tests")
