# -*- coding: utf-8 -*-
"""Phase-1 L1/L2/L3 tags + glossary + TOC emoji (chemistry untouched)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_resolve_levels():
    from stain_level_tags import resolve_level, format_intake_block, prepend_level_to_answer

    assert resolve_level("S_BLOOD_FRESH") == ("L1", 1)
    assert resolve_level("S_ENGINE_OIL") == ("L3", 3)
    assert resolve_level("S_BLOOD_DRY") == ("L2", 2)
    # IPA solvent stains are L2 (supervisor), not unsupervised L1
    assert resolve_level("S_INK_PEN") == ("L2", 2)
    assert resolve_level("S_GRASS") == ("L2", 2)

    lvl, grade = resolve_level(
        "S_BLOOD_FRESH",
        graph={"fabric_context": {"id": "F4", "name": "silk"}},
        entities={},
    )
    assert lvl == "L2" and grade == 2

    block = format_intake_block("L3", 3, "ko")
    assert "등급 3" in block or "L3" in block

    ans = prepend_level_to_answer(
        "본문입니다.",
        stain_id="S_ENGINE_OIL",
        graph={},
        entities={},
        lang="ko",
    )
    assert ans.startswith("┌─ 기본 안내")
    assert "용어 안내" in ans
    assert "이번 건 세탁 교육" in ans
    assert "본문입니다." in ans
    # idempotent
    assert prepend_level_to_answer(ans, stain_id="S_ENGINE_OIL", lang="ko") == ans


def test_l1_twelve_instructional():
    from ko_stain_education import KO_STAIN_EDU

    ids = (
        "S_MILK",
        "S_SWEAT_FRESH",
        "S_EGG",
        "S_TEA",
        "S_FRUIT_JUICE",
        "S_SOFT_DRINK",
        "S_KETCHUP",
        "S_TOMATO_SAUCE",
        "S_KIMCHI",
        "S_CHOCOLATE",
        "S_SOY_SAUCE",
    )
    for sid in ids:
        path = KO_STAIN_EDU[sid]["fresh_path_ko"]
        assert "【확인】" in path, sid
        assert "【도구】" in path, sid
        assert "하세요" in path or "마세요" in path, sid
        assert "Cap1" not in path and "Cap2" not in path, sid


def test_skip_without_stain_id():
    from stain_level_tags import prepend_level_to_answer

    body = "품목 세탁만 안내합니다."
    assert prepend_level_to_answer(body, stain_id="", graph={}, lang="ko") == body
    assert (
        prepend_level_to_answer(
            body,
            stain_id="",
            graph={"specialty_item_care": True},
            lang="ko",
        )
        == body
    )


def test_five_stain_instructional_tone():
    from ko_stain_education import KO_STAIN_EDU

    for sid in ("S_BLOOD_FRESH", "S_BLACK_COFFEE", "S_COOKING_OIL", "S_INK_PEN", "S_MUD"):
        path = KO_STAIN_EDU[sid]["fresh_path_ko"]
        assert "하세요" in path or "마세요" in path, sid
        if sid == "S_BLACK_COFFEE":
            assert "1:4" in path
            assert "식초 1:8로" not in path
            assert "1:8로 더 묽게" not in path


def test_toc_emoji_only_on_headers():
    from graphrag_engine import _promote_ko_section_headers

    sample = (
        "(1) 핏자국·면.\n"
        "(2) 흰 면 천.\n"
        "(3) 약하게.\n"
        "(4) 식초 1:4 분무 5분.\n"
        "(5) 찬물.\n"
        "(6) 건조 전 강광.\n"
        "[왜 이 순서] 탄닌이라서입니다."
    )
    out = _promote_ko_section_headers(sample, item_wash=False)
    assert "👕" in out and "🧰" in out and "✋" in out
    assert "🧴" in out and "🌡" in out and "🌬" in out
    # chemistry ratio preserved in body
    assert "식초 1:4" in out
    # education block: ◆ only, no TOC emoji on it
    assert "◆ [왜 이 순서인가요]" in out
    why_line = [ln for ln in out.splitlines() if "왜 이 순서" in ln][0]
    assert "👕" not in why_line and "🧴" not in why_line
    # idempotent
    out2 = _promote_ko_section_headers(out, item_wash=False)
    assert out2.count("👕") == out.count("👕") == 1


def test_item_wash_toc_emoji():
    from graphrag_engine import _promote_ko_section_headers

    sample = "(1) 모자.\n(2) 솔.\n(3) 약하게.\n(4) 중성세제.\n(5) 미온.\n(6) 통풍."
    out = _promote_ko_section_headers(sample, item_wash=True)
    assert "🏷️" in out
    assert "오염·원단·두께·색상" not in out


def test_tone_complement_polish():
    from graphrag_engine import _polish_owner_ko_phrasing

    raw = (
        "【확인】흰옷인가요. 【도구】식초. "
        "문지르기 금지. 잔색 채 건조 금지. 사전 고지.\n"
        "(1) 핏자국.\n(2) 천.\n식초 1:4."
    )
    out = _polish_owner_ko_phrasing(raw)
    assert "세게 문지르지 마세요" in out
    assert "잔색이 남은 채로 말리지 마세요" in out
    assert "미리 고객에게 고지하세요" in out
    assert "◆ 【확인 먼저】" in out
    assert "◆ 【도구 준비】" in out
    assert "식초 1:4" in out  # chemistry intact
    assert "👕" in out


if __name__ == "__main__":
    test_resolve_levels()
    test_skip_without_stain_id()
    test_five_stain_instructional_tone()
    test_l1_twelve_instructional()
    test_toc_emoji_only_on_headers()
    test_item_wash_toc_emoji()
    test_tone_complement_polish()
    print("OK test_stain_level_tags")
