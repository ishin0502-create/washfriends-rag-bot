# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from protocol import (
    apply_protocol_to_graph,
    bind_tools_from_protocol,
    build_protocol,
    has_protocol,
    overlay_mode_for_item,
)


def _wine_graph(fabric_name="Cotton", fabric_id="F1", color=""):
    return {
        "stain_context": {
            "id": "S_RED_WINE",
            "name_ko": "레드와인",
            "contains_tannin": True,
            "contains_dye": True,
            "fresh_path_ko": "OLD PATH SHOULD BE REPLACED",
            "why_ko": "OLD WHY",
        },
        "fabric_context": {
            "id": fabric_id,
            "name": fabric_name,
            "name_vi": "vai cotton" if fabric_id == "F1" else fabric_name,
            "acid_safe": fabric_id in {"F1", "F2", "F5", "F6"},
            "enzyme_safe": fabric_id in {"F1", "F2", "F5", "F6"},
            "can_oxygen": fabric_id in {"F1", "F2", "F5", "F6"},
        },
        "chemicals": [
            {"code": "S1", "name_ko": "워시프렌즈 중성세제", "dilution_ko": "실크·울 우선"},
            {"code": "A1", "name_ko": "알코올"},
        ],
        "tools": [
            {"id": "T_CLOTH", "name_ko": "흰 천", "use_for_ko": "블롯"},
            {"id": "T_SPRAY", "name_ko": "분무기", "use_for_ko": "OLD"},
            {"id": "T_SOAK_BIN", "name_ko": "담금통", "use_for_ko": "OLD"},
            {"id": "T_TIMER", "name_ko": "타이머", "use_for_ko": "OLD"},
        ],
        "garment_color": color,
    }


def test_has_wine_protocol():
    assert has_protocol("S_RED_WINE")
    assert overlay_mode_for_item("I_KNIT") == "stain_primary"
    assert overlay_mode_for_item("I_NECKTIE") == "item_primary"


def test_cotton_wine_kills_s1_poison():
    """Even if graph chemicals were S1-only poison, protocol restores A3 (+ optional B1)."""
    g = _wine_graph()
    out = apply_protocol_to_graph(g, entities={"_raw": "면 와인", "fabric_type": "cotton", "stain_id": "S_RED_WINE"})
    codes = [c["code"] for c in out["chemicals"]]
    assert "A3" in codes
    assert codes[0] == "N2" or "A3" in codes
    assert "S1" not in codes
    spray = next(t for t in out["tools"] if t["id"] == "T_SPRAY")
    assert "식초" in spray["use_for_ko"]
    assert "실크·울 우선" not in spray["use_for_ko"]
    assert "중성세제" not in spray["use_for_ko"]
    timer = next(t for t in out["tools"] if t["id"] == "T_TIMER")
    assert "5" in timer["use_for_ko"] and "15" in timer["use_for_ko"]
    assert "OLD PATH" not in (out["stain_context"].get("fresh_path_ko") or "")
    assert "식초" in (out["stain_context"].get("fresh_path_ko") or "")


def test_wine_timer_prefers_vinegar_not_bleach():
    g = _wine_graph(color="white")
    out = apply_protocol_to_graph(g, entities={"fabric_type": "cotton", "garment_color": "white"})
    timer = next(t for t in out["tools"] if t["id"] == "T_TIMER")
    # Must be 5–15 (vinegar), not only 15–45 (bleach)
    assert "5–15" in timer["use_for_ko"] or "5-15" in timer["use_for_ko"]


def test_colored_skips_oxygen():
    g = _wine_graph(color="colored")
    out = apply_protocol_to_graph(
        g, entities={"fabric_type": "cotton", "garment_color": "colored"}
    )
    codes = [c["code"] for c in out["chemicals"]]
    assert "A3" in codes
    assert "B1" not in codes


def test_silk_wine_replaces_acid_with_s1_explicitly():
    g = _wine_graph(fabric_name="Silk", fabric_id="F4")
    g["fabric_context"]["acid_safe"] = False
    g["fabric_context"]["can_oxygen"] = False
    g["fabric_context"]["enzyme_safe"] = False
    out = apply_protocol_to_graph(g, entities={"fabric_type": "silk"})
    codes = [c["code"] for c in out["chemicals"]]
    assert "A3" not in codes
    assert "B1" not in codes
    assert "S1" in codes
    path = out["stain_context"]["fresh_path_ko"]
    assert "중성세제" in path or "실크" in path
    spray = next(t for t in out["tools"] if t["id"] == "T_SPRAY")
    assert "식초" not in spray["use_for_ko"] or "식초·효소 분무 금지" in spray["use_for_ko"]
    assert "중성세제" in spray["use_for_ko"]
    assert "1 : 물 4" not in spray["use_for_ko"]
    timer = next(t for t in out["tools"] if t["id"] == "T_TIMER")
    assert "규정 분" not in timer["use_for_ko"]
    assert "5" in timer["use_for_ko"]


def test_necktie_item_primary_skips_chem_rewrite():
    g = _wine_graph()
    g["item_context"] = {"id": "I_NECKTIE", "name_ko": "넥타이"}
    g["chemicals"] = [{"code": "S1", "name_ko": "중성세제"}]
    out = apply_protocol_to_graph(g, entities={"item_id": "I_NECKTIE"})
    assert out.get("protocol_mode") == "item_primary"
    # chemicals left as-is (item path owns them later)
    assert out["chemicals"][0]["code"] == "S1"


def test_bind_spray_from_protocol_direct():
    proto = build_protocol(_wine_graph(), entities={"fabric_type": "cotton"})
    assert proto is not None
    tools = bind_tools_from_protocol(proto, [{"id": "T_SPRAY", "use_for_ko": "x"}])
    assert "식초" in tools[0]["use_for_ko"]


def test_jiulsu_not_wool():
    """'지울수' must not infer wool (Hangul 울 false positive)."""
    from graphrag_engine import _infer_fabric_from_text
    msg = "면소재 옷에 와인이 많이 묻었어요. 어떻게 해야 지울수 있나요?"
    assert _infer_fabric_from_text(msg) == "cotton"
    assert _infer_fabric_from_text("울 코트 세탁") == "wool"
    assert _infer_fabric_from_text("얼룩 지울수 있나요") != "wool"


def test_protocol_v2_coverage():
    for sid in (
        "S_MILK_COFFEE", "S_BLOOD_DRY", "S_LIPSTICK", "S_MOTORBIKE_OIL",
        "S_INK_PEN", "S_RUST", "S_BUBBLE_TEA", "S_SOY_SAUCE", "S_KETCHUP",
    ):
        assert has_protocol(sid), sid
    latte = build_protocol(
        {"stain_context": {"id": "S_MILK_COFFEE"}, "fabric_context": {"id": "F1", "name": "Cotton"}, "tools": [], "chemicals": []},
        entities={"fabric_type": "cotton"},
    )
    assert latte is not None
    codes = latte.chem_codes()
    assert codes.index("E1") < codes.index("A3")


def test_protocol_v3_covers_all_ko_edu():
    import re
    from pathlib import Path
    from protocol import PROTOCOL_BUILDERS
    text = Path(__file__).resolve().parents[1].joinpath("ko_stain_education.py").read_text(encoding="utf-8")
    ids = set(re.findall(r'"(S_[A-Z0-9_]+)"', text))
    missing = sorted(ids - set(PROTOCOL_BUILDERS))
    assert not missing, f"missing protocols: {missing}"
    assert len(PROTOCOL_BUILDERS) >= 58


def test_mayo_oil_before_enzyme():
    p = build_protocol(
        {"stain_context": {"id": "S_MAYO"}, "fabric_context": {"id": "F1", "name": "Cotton"}, "tools": [], "chemicals": []},
        entities={"fabric_type": "cotton"},
    )
    codes = p.chem_codes()
    assert codes.index("D2") < codes.index("E1")


def test_entity_cotton_beats_graph_wool():
    g = _wine_graph(fabric_name="Wool", fabric_id="F3")
    g["fabric_context"]["acid_safe"] = False
    g["fabric_context"]["can_oxygen"] = False
    out = apply_protocol_to_graph(g, entities={"fabric_type": "cotton", "_raw": "면 와인 지울수"})
    codes = [c["code"] for c in out["chemicals"]]
    assert "A3" in codes
    assert "S1" not in codes


def test_protocol_clears_legacy_blocked_fields():
    g = _wine_graph()
    g["chemicals_blocked_for_fabric"] = [{"name_ko": "식초", "reason": "poison"}]
    g["delicate_chem_rule"] = "Chi dung chemicals[] con lai..."
    out = apply_protocol_to_graph(g, entities={"fabric_type": "cotton"})
    assert "chemicals_blocked_for_fabric" not in out
    assert "delicate_chem_rule" not in out
    assert any(c["code"] == "A3" for c in out["chemicals"])


def test_fabric_safety_skipped_when_protocol_stain_primary():
    from graphrag_engine import _apply_fabric_chem_safety

    g = _wine_graph(fabric_name="Wool", fabric_id="F3")
    g["fabric_context"]["acid_safe"] = False
    g["fabric_context"]["can_oxygen"] = False
    g["stain_context"]["fresh_path_ko"] = "KEEP_ME_LEGACY"
    before = [c["code"] for c in g["chemicals"]]
    out = _apply_fabric_chem_safety(g, entities={"fabric_type": "cotton", "stain_id": "S_RED_WINE"})
    assert [c["code"] for c in out["chemicals"]] == before
    assert out["stain_context"]["fresh_path_ko"] == "KEEP_ME_LEGACY"
    assert "chemicals_blocked_for_fabric" not in out


def test_fabric_safety_still_filters_without_protocol():
    from graphrag_engine import _apply_fabric_chem_safety

    g = {
        "stain_context": {"id": "S_NO_PROTOCOL_FAKE", "fresh_path_ko": "path"},
        "fabric_context": {"id": "F3", "name": "Wool", "acid_safe": False, "can_oxygen": False},
        "chemicals": [
            {"code": "A3", "name_ko": "식초", "safe_on_wool": False},
            {"code": "S1", "name_ko": "중성", "safe_on_wool": True},
        ],
        "tools": [],
    }
    out = _apply_fabric_chem_safety(g, entities={})
    codes = [c["code"] for c in out["chemicals"]]
    assert "A3" not in codes
    assert "S1" in codes
    assert out.get("chemicals_blocked_for_fabric")


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
