# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graphrag_engine import _infer_item_from_text, _sanitize_graph_for_owner
from specialty_item_care import SPECIALTY_CARE_IDS, apply_specialty_item_education, education_for
from specialty_ops_remainder_care import OPS_REMAINDER_IDS, education_for_ops_remainder


def test_ids_wired():
    assert OPS_REMAINDER_IDS <= SPECIALTY_CARE_IDS
    for iid in OPS_REMAINDER_IDS:
        edu = education_for(iid)
        assert edu.get("fresh_path_ko") and edu.get("fresh_path_vi") and edu.get("fresh_path_en")
        assert edu.get("must_include_ko")
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_vi"])


def test_infer():
    assert _infer_item_from_text("케어라벨 세탁표시 어떻게 읽어?") == "I_CARE_LABEL"
    assert _infer_item_from_text("접수 스크립트 알려줘") == "I_INTAKE_SCRIPT"
    assert _infer_item_from_text("경수 세탁 보정") == "I_WATER_HARDNESS"
    assert _infer_item_from_text("유색 옷 색바램 복원") == "I_COLOR_FADE"
    assert _infer_item_from_text("흰옷 얼룩환 복원") == "I_WHITE_FADE"
    assert _infer_item_from_text("니트 스웨터 세탁") == "I_KNIT"
    assert _infer_item_from_text("브라 세탁방법") == "I_UNDERWEAR"
    assert _infer_item_from_text("운동복 세탁") == "I_ACTIVEWEAR"
    assert _infer_item_from_text("실크 스카프 세탁") == "I_SCARF"
    assert _infer_item_from_text("합성 골프장갑 세탁") == "I_GOLF_GLOVE_SYNTH"


def test_apply():
    g = {
        "item_context": {"id": "I_KNIT"},
        "stain_context": {"group": "item_care", "id": "I_KNIT"},
        "tools": [],
        "chemicals": [],
    }
    out = apply_specialty_item_education(g, entities={"item_id": "I_KNIT", "_raw": "니트 세탁"})
    assert out.get("specialty_item_care") and out.get("item_wash_mode")
    san = _sanitize_graph_for_owner(out, "ko")
    assert (san.get("stain_context") or {}).get("fresh_path_ko")


def test_phrases():
    assert "X" in education_for_ops_remainder("I_CARE_LABEL")["must_include_ko"]
    assert "사진" in education_for_ops_remainder("I_INTAKE_SCRIPT")["must_include_ko"]
    assert "평건" in education_for_ops_remainder("I_KNIT")["must_include_ko"]
    assert "100%" in education_for_ops_remainder("I_COLOR_FADE")["must_include_ko"]


if __name__ == "__main__":
    test_ids_wired()
    test_infer()
    test_apply()
    test_phrases()
    print("OK ops_remainder")
