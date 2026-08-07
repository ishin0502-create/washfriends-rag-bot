# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from w3_clothing_items import CLOTHING_ITEMS, never_use_card_for_fabric
from graphrag_engine import _infer_item_from_text, _attach_match_diagnosis
from image_analyzer import _to_graphrag_entities
from failure_log import log_failure


def test_clothing_six():
    ids = {r["id"] for r in CLOTHING_ITEMS}
    assert ids == {"I_DRESS", "I_KNIT", "I_UNDERWEAR", "I_ACTIVEWEAR", "I_SCARF", "I_UNIFORM"}
    for r in CLOTHING_ITEMS:
        assert r["why_ko"] and r["fresh_path_ko"]
        assert r["fabric_id"]


def test_infer_items():
    assert _infer_item_from_text("니트 스웨터 세탁") == "I_KNIT"
    assert _infer_item_from_text("원피스 실크 얼룩") == "I_DRESS"
    assert _infer_item_from_text("운동복 땀 냄새") == "I_ACTIVEWEAR"
    assert _infer_item_from_text("ao nguc tay") == "I_UNDERWEAR"
    assert _infer_item_from_text("khan quang lua") == "I_SCARF"
    assert _infer_item_from_text("dong phuc cong so") == "I_UNIFORM"


def test_never_use_card():
    silk = never_use_card_for_fabric("silk", "ko")
    assert "효소" in silk or "금지" in silk
    wool = never_use_card_for_fabric("wool", "vi")
    assert "CAM" in wool or "enzyme" in wool.lower()
    assert never_use_card_for_fabric("cotton", "ko") == ""


def test_match_never_use_attach():
    g = {
        "fabric_context": {"name": "silk", "name_vi": "lua"},
        "stain_context": {"id": "S_BLACK_COFFEE", "contains_tannin": True},
        "tools": [],
        "chemicals": [],
    }
    out = _attach_match_diagnosis(g, entities={"_raw": "실크 커피", "fabric_type": "silk"})
    md = out.get("match_diagnosis") or {}
    assert md.get("never_use_ko")
    assert "실크" in md["never_use_ko"] or "금지" in md["never_use_ko"]


def test_vision_stain_id():
    ent = _to_graphrag_entities({"stain_type": "coffee", "fabric_type": "cotton", "confidence": "high", "lang": "ko"})
    assert ent["stain_id"] == "S_BLACK_COFFEE"
    ent2 = _to_graphrag_entities({"stain_type": "blood", "fabric_type": "cotton", "confidence": "high"})
    assert ent2["stain_id"] == "S_BLOOD_FRESH"
    ent3 = _to_graphrag_entities({"stain_type": "unknown", "confidence": "low"})
    assert ent3["stain_id"] is None


def test_failure_log_smoke(tmp_path=None):
    # best-effort; should not raise
    log_failure(reason="unit_test", message="smoke", lang="ko", entities={"stain_id": "S_X"})


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
