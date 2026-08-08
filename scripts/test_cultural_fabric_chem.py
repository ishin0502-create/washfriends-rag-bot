# -*- coding: utf-8 -*-
"""Cultural + fabric curriculum + chem safety specialty cards."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chem_safety_care import CHEM_SAFETY_IDS, education_for_chem_safety
from fabric_care import FABRIC_CURRICULUM_IDS, education_for_fabric
from graphrag_engine import _infer_item_from_text, _sanitize_graph_for_owner
from specialty_cultural_care import CULTURAL_SPECIALTY_IDS, education_for_cultural
from specialty_item_care import SPECIALTY_CARE_IDS, apply_specialty_item_education, education_for


def test_ids_wired():
    assert CULTURAL_SPECIALTY_IDS <= SPECIALTY_CARE_IDS
    assert FABRIC_CURRICULUM_IDS <= SPECIALTY_CARE_IDS
    assert CHEM_SAFETY_IDS <= SPECIALTY_CARE_IDS
    for iid in list(CULTURAL_SPECIALTY_IDS) + list(FABRIC_CURRICULUM_IDS) + list(CHEM_SAFETY_IDS):
        edu = education_for(iid)
        assert edu.get("fresh_path_ko") and edu.get("fresh_path_vi") and edu.get("fresh_path_en")
        assert edu.get("must_include_ko")
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_vi"])
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_en"])


def test_infer_cultural():
    assert _infer_item_from_text("넥타이 세탁방법") == "I_NECKTIE"
    assert _infer_item_from_text("아오자이 세탁") == "I_AO_DAI"
    assert _infer_item_from_text("한복 세탁 방법") == "I_HANBOK"
    assert _infer_item_from_text("담배냄새 옷 제거") == "I_ODOR_SMOKE"
    assert _infer_item_from_text("유니폼 세탁방법") == "I_UNIFORM"


def test_infer_fabric_and_chem():
    assert _infer_item_from_text("실크 원단 세탁 주의") == "I_FABRIC_SILK"
    assert _infer_item_from_text("울 소재 관리 방법") == "I_FABRIC_WOOL"
    assert _infer_item_from_text("면 원단 세탁방법") == "I_FABRIC_COTTON"
    assert _infer_item_from_text("락스 암모니아 혼합 금지") == "I_CHEM_NEVER_MIX"
    assert _infer_item_from_text("표백 안전 어떻게") == "I_CHEM_BLEACH"
    # garment wins over fabric curriculum
    assert _infer_item_from_text("실크 넥타이 세탁") == "I_NECKTIE"
    assert _infer_item_from_text("아오자이 실크 세탁") == "I_AO_DAI"


def test_apply_sanitize():
    for iid, raw, lang in (
        ("I_NECKTIE", "넥타이 세탁방법", "ko"),
        ("I_FABRIC_SILK", "실크 원단 세탁 주의", "ko"),
        ("I_CHEM_NEVER_MIX", "Never mix bleach and ammonia", "en"),
    ):
        g = {
            "item_context": {"id": iid},
            "stain_context": {"group": "item_care", "id": iid},
            "tools": [],
            "chemicals": [],
        }
        out = apply_specialty_item_education(g, entities={"item_id": iid, "_raw": raw})
        assert out.get("specialty_item_care") and out.get("item_wash_mode")
        san = _sanitize_graph_for_owner(out, lang)
        sc = san.get("stain_context") or {}
        assert sc.get(f"fresh_path_{lang}")
        for other in ("ko", "vi", "en"):
            if other != lang:
                assert not sc.get(f"fresh_path_{other}")


def test_key_phrases():
    assert "통담금" in education_for_cultural("I_NECKTIE")["must_include_ko"]
    assert "드라이" in education_for_cultural("I_HANBOK")["must_include_ko"]
    assert "A3" in education_for_cultural("I_ODOR_SMOKE")["must_include_ko"]
    assert "표백" in education_for_fabric("I_FABRIC_SILK")["must_include_ko"] or "효소" in education_for_fabric("I_FABRIC_SILK")["must_include_ko"]
    assert "B2" in education_for_chem_safety("I_CHEM_NEVER_MIX")["must_include_ko"]


def test_regression():
    assert _infer_item_from_text("청바지 세탁방법") == "I_DENIM"
    assert _infer_item_from_text("세탁물 분류") == "I_SORT"
    assert _infer_item_from_text("구스이불 세탁") == "I_DUVET_GOOSE"


if __name__ == "__main__":
    test_ids_wired()
    test_infer_cultural()
    test_infer_fabric_and_chem()
    test_apply_sanitize()
    test_key_phrases()
    test_regression()
    print("OK cultural_fabric_chem")
