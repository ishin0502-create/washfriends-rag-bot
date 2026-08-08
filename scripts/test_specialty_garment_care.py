# -*- coding: utf-8 -*-
"""Garment specialty cards — formerly GraphRAG-only high-traffic items."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graphrag_engine import _infer_item_from_text, _sanitize_graph_for_owner
from specialty_garment_care import GARMENT_SPECIALTY_IDS, education_for_garment
from specialty_item_care import SPECIALTY_CARE_IDS, apply_specialty_item_education, education_for


def test_ids_wired():
    assert GARMENT_SPECIALTY_IDS <= SPECIALTY_CARE_IDS
    for iid in GARMENT_SPECIALTY_IDS:
        edu = education_for(iid)
        assert edu.get("fresh_path_ko") and edu.get("fresh_path_vi") and edu.get("fresh_path_en")
        assert edu.get("must_include_ko") and edu.get("must_include_vi") and edu.get("must_include_en")
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_vi"])
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_en"])


def test_infer_routes():
    assert _infer_item_from_text("커튼 세탁 방법") == "I_CURTAIN_FABRIC"
    assert _infer_item_from_text("샤워커튼 우레탄") == "I_CURTAIN_URETHANE"
    assert _infer_item_from_text("청바지 세탁") == "I_DENIM"
    assert _infer_item_from_text("고어텍스 자켓 세탁") == "I_GORETEX"
    assert _infer_item_from_text("아기옷 세탁") == "I_BABY_WEAR"
    assert _infer_item_from_text("수영복 세탁") == "I_SWIMWEAR"
    assert _infer_item_from_text("골프복 세탁") == "I_GOLF_WEAR"
    assert _infer_item_from_text("골프화 세탁") == "I_GOLF_SHOE"
    assert _infer_item_from_text("등산화 세탁") == "I_HIKING_SHOE"
    assert _infer_item_from_text("러닝화 메시") == "I_RUNNING_MESH"


def test_apply_sanitize_langs():
    for iid, raw, lang in (
        ("I_DENIM", "청바지 세탁방법", "ko"),
        ("I_SWIMWEAR", "Lam sao giat do boi?", "vi"),
        ("I_GORETEX", "How do I wash Gore-Tex jacket?", "en"),
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
    assert "흰옷" in education_for_garment("I_DENIM")["must_include_ko"]
    assert "DWR" in education_for_garment("I_GORETEX")["must_include_ko"]
    assert "세탁망" in education_for_garment("I_RUNNING_MESH")["must_include_ko"]
    assert "치수" in education_for_garment("I_CURTAIN_FABRIC")["must_include_ko"]


def test_regression_specialty_still_works():
    assert _infer_item_from_text("구스이불 세탁") == "I_DUVET_GOOSE"
    assert _infer_item_from_text("세탁물 분류") == "I_SORT"
    edu = education_for("I_DUVET_GOOSE")
    assert "테니스" in edu["fresh_path_ko"] or "건조볼" in edu["fresh_path_ko"]


if __name__ == "__main__":
    test_ids_wired()
    test_infer_routes()
    test_apply_sanitize_langs()
    test_key_phrases()
    test_regression_specialty_still_works()
    print("OK garment_specialty")
