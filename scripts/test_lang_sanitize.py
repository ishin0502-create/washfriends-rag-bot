# -*- coding: utf-8 -*-
"""Language purity: sanitize must not feed wrong-lang narratives to the LLM."""
from graphrag_engine import _sanitize_graph_for_owner
from reply_lang import reply_language_leaks


def _sample_graph():
    return {
        "must_include_ko": "테니스볼, 퍼크 금지",
        "must_include_vi": "bong tennis, CAM perc",
        "must_include_en": "tennis balls, no perc",
        "chem_forbid_ko": "옥살산 지어내기 금지",
        "delicate_chem_rule": "Chi dung chemicals[] con lai. Cam bia.",
        "leather_care": False,
        "specialty_item_care": True,
        "stain_context": {
            "group": "item_care",
            "why_ko": "[왜 이 순서] 한국어 why",
            "why_vi": "[Tai sao] Vietnamese why",
            "why_en": "[Why] English why",
            "fresh_path_ko": "(1)한국어 경로",
            "fresh_path_vi": "(1)duong VI",
            "fresh_path_en": "(1)EN path",
            "tip": "[왜 이 순서] 한국어 tip stamped by bug",
            "must_include_ko": "테니스볼",
        },
        "tools": [
            {
                "id": "T_CLOTH",
                "name_ko": "흰 천",
                "name_vi": "Khan trang",
                "use_for_ko": "한국어 사용법",
                "use_for_vi": "cach dung VI",
                "use_for_en": "EN how-to",
            }
        ],
        "protocol": {
            "mode": "item_primary",
            "chem_order": ["D2"],
            "steps": [
                {
                    "action_ko": "한국어 단계",
                    "action_vi": "buoc VI",
                    "action_en": "EN step",
                    "force": "Cap1",
                    "chem": "D2",
                }
            ],
        },
        "item_context": {
            "id": "I_DUVET_GOOSE",
            "name_ko": "구스이불",
            "name_vi": "Chan long",
            "why_ko": "KO item why",
            "why_vi": "VI item why",
            "why_en": "EN item why",
        },
    }


def test_sanitize_vi_drops_hangul_tip_and_must():
    g = _sanitize_graph_for_owner(_sample_graph(), "vi")
    assert "must_include_ko" not in g
    assert "chem_forbid_ko" not in g
    sc = g["stain_context"]
    assert "why_ko" not in sc
    assert "fresh_path_ko" not in sc
    assert sc.get("tip") == "[Tai sao] Vietnamese why"
    assert "가" not in str(sc.get("tip") or "")
    tools = g.get("tools") or []
    assert tools and "use_for_ko" not in tools[0]
    assert tools[0].get("use_for_vi")
    proto = g.get("protocol") or {}
    for step in proto.get("steps") or []:
        assert "한국어" not in str(step.get("action") or "")


def test_sanitize_en_drops_ko_vi():
    g = _sanitize_graph_for_owner(_sample_graph(), "en")
    assert "must_include_ko" not in g
    assert "must_include_vi" not in g
    assert "delicate_chem_rule" not in g
    sc = g["stain_context"]
    assert "why_ko" not in sc and "why_vi" not in sc
    assert sc.get("tip") == "[Why] English why"
    tools = g.get("tools") or []
    assert tools and tools[0].get("use_for_en") == "EN how-to"
    assert "use_for_ko" not in tools[0]


def test_sanitize_ko_drops_vi_rule():
    g = _sanitize_graph_for_owner(_sample_graph(), "ko")
    assert "delicate_chem_rule" not in g
    assert "must_include_vi" not in g
    sc = g["stain_context"]
    assert "why_vi" not in sc
    assert sc.get("tip") == "[왜 이 순서] 한국어 why"


def test_en_leak_detector_any_hangul():
    assert reply_language_leaks("Wash then 헹굼 carefully.", "en")
    assert not reply_language_leaks("Wash with mild soap then air dry.", "en")


if __name__ == "__main__":
    test_sanitize_vi_drops_hangul_tip_and_must()
    test_sanitize_en_drops_ko_vi()
    test_sanitize_ko_drops_vi_rule()
    test_en_leak_detector_any_hangul()
    print("OK lang_sanitize")
