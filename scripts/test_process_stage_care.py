# -*- coding: utf-8 -*-
"""Process-stage education: sort / rinse / QC-handover — routing + lang purity."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from graphrag_engine import _infer_item_from_text, _sanitize_graph_for_owner
from process_stage_care import PROCESS_STAGE_IDS, education_for_process
from reply_lang import reply_language_leaks
from specialty_item_care import apply_specialty_item_education, education_for


def test_infer_sort_rinse_qc_ko_vi_en():
    assert _infer_item_from_text("세탁물 분류 어떻게 해요?") == "I_SORT"
    assert _infer_item_from_text("흰옷과 유색 분리세탁 기준") == "I_SORT"
    assert _infer_item_from_text("Phan loai do giat tach mau") == "I_SORT"
    assert _infer_item_from_text("How do I sort laundry lights and darks?") == "I_SORT"

    assert _infer_item_from_text("추가 헹굼은 언제 하나요?") == "I_RINSE"
    assert _infer_item_from_text("잔여 세제 때문에 뻣뻣해요 헹굼") == "I_RINSE"
    assert _infer_item_from_text("Khi nao can xa them?") == "I_RINSE"
    assert _infer_item_from_text("When do I use an extra rinse?") == "I_RINSE"

    assert _infer_item_from_text("출고 전 QC 체크리스트") == "I_QC_HANDOVER"
    assert _infer_item_from_text("고객 인도 멘트 알려줘") == "I_QC_HANDOVER"
    assert _infer_item_from_text("Checklist ban giao khach truoc giao") == "I_QC_HANDOVER"
    assert _infer_item_from_text("Quality check before pickup handover") == "I_QC_HANDOVER"


def test_process_does_not_steal_garment_or_stain():
    assert _infer_item_from_text("구스이불 세탁 추가 헹굼") == "I_DUVET_GOOSE"
    assert _infer_item_from_text("커피 얼룩 면 셔츠") != "I_SORT"
    assert _infer_item_from_text("커피 얼룩 면 셔츠") != "I_RINSE"
    assert _infer_item_from_text("에어드레서 사용법") == "I_FINISHING"
    assert _infer_item_from_text("접수 스크립트") == "I_INTAKE_SCRIPT"
    assert _infer_item_from_text("경수 보정") == "I_WATER_HARDNESS"


def test_education_has_all_langs_and_must():
    for iid in sorted(PROCESS_STAGE_IDS):
        edu = education_for(iid)
        assert edu.get("fresh_path_ko") and edu.get("why_ko")
        assert edu.get("fresh_path_vi") and edu.get("why_vi")
        assert edu.get("fresh_path_en") and edu.get("why_en")
        assert edu.get("must_include_ko")
        assert edu.get("must_include_vi")
        assert edu.get("must_include_en")
        # No cross-lang contamination in primary narrative fields
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_vi"])
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_en"])
        assert "Phan loai" not in edu["fresh_path_ko"] and "Extra rinse" not in edu["fresh_path_ko"]


def test_apply_and_sanitize_lang_purity():
    for iid, raw, lang in (
        ("I_SORT", "세탁물 분류 방법", "ko"),
        ("I_RINSE", "Khi nao can xa them", "vi"),
        ("I_QC_HANDOVER", "Quality check before pickup", "en"),
    ):
        g = {
            "item_context": {"id": iid, "name_ko": iid},
            "stain_context": {"group": "item_care", "id": iid},
            "tools": [],
            "chemicals": [],
        }
        out = apply_specialty_item_education(g, entities={"item_id": iid, "_raw": raw})
        assert out.get("specialty_item_care")
        assert out.get("item_wash_mode")
        sc = out.get("stain_context") or {}
        assert sc.get(f"fresh_path_{lang}")
        san = _sanitize_graph_for_owner(out, lang)
        sc2 = san.get("stain_context") or {}
        # Wrong-lang path keys must be dropped
        for other in ("ko", "vi", "en"):
            if other == lang:
                continue
            assert not sc2.get(f"fresh_path_{other}")
            assert not sc2.get(f"why_{other}")
        path = sc2.get(f"fresh_path_{lang}") or ""
        assert path
        if lang == "ko":
            assert any("\uac00" <= c <= "\ud7a3" for c in path)
            assert "Phan loai" not in path and "Extra rinse" not in path
        elif lang == "vi":
            assert not any("\uac00" <= c <= "\ud7a3" for c in path)
        else:
            assert not any("\uac00" <= c <= "\ud7a3" for c in path)
            leaks = reply_language_leaks(path, "en")
            assert "hangul" not in leaks and "ko_markers" not in leaks, leaks


def test_process_ids_in_specialty_set():
    from specialty_item_care import SPECIALTY_CARE_IDS

    assert PROCESS_STAGE_IDS <= SPECIALTY_CARE_IDS
    assert education_for_process("I_SORT")["must_include_ko"]


if __name__ == "__main__":
    test_infer_sort_rinse_qc_ko_vi_en()
    test_process_does_not_steal_garment_or_stain()
    test_education_has_all_langs_and_must()
    test_apply_and_sanitize_lang_purity()
    test_process_ids_in_specialty_set()
    print("OK process_stage")
