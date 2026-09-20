# -*- coding: utf-8 -*-
"""Phase-1 L1/L2/L3 tags + intake scripts + 5-stain instructional paths."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_resolve_levels():
    from stain_level_tags import resolve_level, format_intake_block, prepend_level_to_answer

    assert resolve_level("S_BLOOD_FRESH") == ("L1", 1)
    assert resolve_level("S_BLACK_COFFEE") == ("L1", 1)
    assert resolve_level("S_COOKING_OIL") == ("L1", 1)
    assert resolve_level("S_INK_PEN") == ("L1", 1)
    assert resolve_level("S_MUD") == ("L1", 1)
    assert resolve_level("S_ENGINE_OIL") == ("L3", 3)
    assert resolve_level("S_BLOOD_DRY") == ("L2", 2)

    # Delicate fabric bumps L1 → L2
    lvl, grade = resolve_level(
        "S_BLOOD_FRESH",
        graph={"fabric_context": {"id": "F4", "name": "silk"}},
        entities={},
    )
    assert lvl == "L2" and grade == 2

    # Heat / hard age bumps
    lvl2, g2 = resolve_level(
        "S_BLACK_COFFEE",
        graph={"stain_context": {"age_bucket": "hard"}},
        entities={},
        user_text="건조기 돌렸어요",
    )
    assert lvl2 in {"L2", "L3"} and g2 >= 2

    block = format_intake_block("L3", 3, "ko")
    assert "등급 3" in block or "L3" in block
    assert "거절" in block or "의뢰" in block

    ans = prepend_level_to_answer(
        "본문입니다.",
        stain_id="S_ENGINE_OIL",
        graph={},
        entities={},
        lang="ko",
    )
    assert ans.startswith("◆ [")
    assert "본문입니다." in ans
    # idempotent
    assert prepend_level_to_answer(ans, stain_id="S_ENGINE_OIL", lang="ko") == ans


def test_five_stain_instructional_tone():
    from ko_stain_education import KO_STAIN_EDU

    for sid in ("S_BLOOD_FRESH", "S_BLACK_COFFEE", "S_COOKING_OIL", "S_INK_PEN", "S_MUD"):
        path = KO_STAIN_EDU[sid]["fresh_path_ko"]
        assert "하세요" in path or "마세요" in path, sid
        assert "【확인】" in path or "확인" in path, sid
        # rejected: coffee silk vinegar 1:8 as treatment ratio
        if sid == "S_BLACK_COFFEE":
            assert "1:4" in path
            assert "1:8 금지" in path or "1:8" not in path.replace("1:8 금지", "")


def test_no_coffee_silk_vinegar_18_as_dose():
    from ko_stain_education import KO_STAIN_EDU

    text = KO_STAIN_EDU["S_BLACK_COFFEE"]["fresh_path_ko"]
    # Must not instruct silk dose as vinegar 1:8 (reject Claude sample)
    assert "식초 1:8로" not in text
    assert "1:8로 더 묽게" not in text
    assert "1:4" in text


if __name__ == "__main__":
    test_resolve_levels()
    test_five_stain_instructional_tone()
    test_no_coffee_silk_vinegar_18_as_dose()
    print("OK test_stain_level_tags")
