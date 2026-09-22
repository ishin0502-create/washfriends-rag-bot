# -*- coding: utf-8 -*-
"""Plain-language owner education (jargon + tools + enzyme emergency tip)."""
from __future__ import annotations

from owner_plain_lang import (
    expand_owner_jargon,
    tool_line_with_purpose,
    block_enzyme_emergency_tip,
)
from owner_answer_clarity import inject_clarity_into_answer, _soak_bounds
from owner_hand_motions import build_hand_motions
from protocol import PROTOCOL_BUILDERS


def test_expand_enzyme_oxygen_all_stains():
    samples = [
        "효소를 바르고 30분. 흰옷 산소(테스트).",
        "Step 2. 효소로 단백질\n효소 30분",
        "식초로 냄새",
        "주방세제로 기름",
    ]
    for s in samples:
        out = expand_owner_jargon(s, "ko")
        assert "효소세제" in out or "식초로 냄새 빼기" in out or "주방세제(식기용" in out
        assert "효소로 단백질" not in out
        # must not leave bare confusing titles
        if "효소를 바르" in s:
            assert "라벨" in out or "프로테아제" in out
        if "산소" in s:
            assert "산소계 표백" in out or "과탄산" in out


def test_tool_purpose():
    line = tool_line_with_purpose("연질 스포팅 솔", "ko")
    assert "—" in line and "살살" in line
    line2 = tool_line_with_purpose("담금통·침지 용기", "ko")
    assert "대야" in line2 or "통" in line2


def test_enzyme_emergency_reference_not_sop():
    tip = block_enzyme_emergency_tip("S_FISH_SAUCE", "ko")
    assert tip
    assert "참고" in tip and "응급" in tip
    assert "표준 아님" in tip or "권장 아님" in tip
    assert "소화제" in tip
    assert "정식 효소세제" in tip or "효소세제" in tip
    # blood also gets tip
    assert block_enzyme_emergency_tip("S_BLOOD_FRESH", "ko")
    # gum should not (no enzyme)
    assert not block_enzyme_emergency_tip("S_GUM", "ko")


def test_gum_no_false_soak():
    proto = PROTOCOL_BUILDERS["S_GUM"]()
    g = {"protocol": proto.to_dict(), "stain": {"id": "S_GUM"}}
    lo, hi = _soak_bounds(g)
    assert lo is None and hi is None


def test_fish_sauce_clarity_plain():
    sid = "S_FISH_SAUCE"
    proto = PROTOCOL_BUILDERS[sid]()
    motions = build_hand_motions(sid, "ko")
    body = (
        "▼ 이번 건 세탁 교육 (L2)\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "◆ 【용어】\n효소 = 단백질 분해\n\n"
        + proto.why_ko
        + "\n"
        + motions
    )
    g = {
        "stain": {"id": sid},
        "entities": {"stain_id": sid, "lang": "ko"},
        "protocol": proto.to_dict(),
        "chemicals": [{"code": "E1"}, {"code": "A3"}, {"code": "B1"}],
        "tools": [
            {"id": "T_BRUSH_SOFT", "name_ko": "연질 스포팅 솔"},
            {"id": "T_SOAK_BIN", "name_ko": "담금통·침지 용기"},
        ],
        "_raw": "느억맘 얼룩",
    }
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="ko")
    assert "효소세제" in out
    assert "산소계 표백" in out or "과탄산" in out
    assert "연질 스포팅 솔 —" in out
    assert "소화제" in out
    assert "표준 아님" in out or "권장 아님" in out
    assert "식초로 냄새 빼기" in out or "냄새 빼기" in out


def test_blood_also_gets_plain_enzyme():
    sid = "S_BLOOD_FRESH"
    m = expand_owner_jargon(build_hand_motions(sid, "ko"), "ko")
    if "효소" in build_hand_motions(sid, "ko"):
        assert "효소세제" in m


if __name__ == "__main__":
    test_expand_enzyme_oxygen_all_stains()
    test_tool_purpose()
    test_enzyme_emergency_reference_not_sop()
    test_gum_no_false_soak()
    test_fish_sauce_clarity_plain()
    test_blood_also_gets_plain_enzyme()
    print("plain_lang_v42 ok")
