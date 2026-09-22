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


def test_tool_purpose():
    line = tool_line_with_purpose("연질 스포팅 솔", "ko")
    assert "—" in line and "살살" in line
    line2 = tool_line_with_purpose("담금통·침지 용기", "ko")
    assert "대야" in line2 or "통" in line2


def test_enzyme_emergency_reference_not_sop():
    tip = block_enzyme_emergency_tip("S_FISH_SAUCE", "ko")
    assert tip
    assert "참고" in tip and "응급" in tip
    assert "표준 아님" in tip or "권장 아님" in tip or "SOP" in tip
    assert "소화제" in tip
    assert "내부" in tip
    assert "손님에게" in tip and ("고지하지" in tip or "설명" in tip)
    # must NOT tell staff to disclose the workaround to guests as a tip to share
    assert "「응급 변통」이라고 고지" not in tip
    assert block_enzyme_emergency_tip("S_BLOOD_FRESH", "ko")
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
        "_owner_stain_id": sid,
        "entities": {"stain_id": sid, "lang": "ko"},
        "protocol": proto.to_dict(),
        "chemicals": [{"code": "E1"}, {"code": "A3"}, {"code": "B1"}, {"code": "D2"}],
        "tools": [
            {"id": "T_BRUSH_SOFT", "name_ko": "연질 스포팅 솔"},
            {"id": "T_SOAK_BIN", "name_ko": "담금통·침지 용기"},
        ],
        "_raw": "느억맘 얼룩 흰옷",
    }
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="ko")
    assert "신선: 개선" not in out
    assert "방금 묻은 직후" in out
    assert "느억맘" in out or "액젓" in out
    assert "온수·건조기" in out
    assert "냄새·염" not in out
    assert "효소·세제" not in out
    assert "효소계 세제" in out
    assert "산소계 표백" in out or "과탄산" in out
    assert "연질 스포팅 솔 —" in out
    assert "소화제" in out
    assert "손님에게" in out and "고지하지" in out
    assert "바르고" in out or "담가" in out or "바르" in out  # one-line has verbs
    order_i = out.find("【한 줄 순서】")
    assert order_i >= 0
    order = out[order_i : order_i + 450]
    assert "주방세제" in order
    assert "바르" in order or "담가" in order
    assert "섞지" in order or "하나씩" in out
    assert "(과탄산·옥시클린 계열)(과탄산" not in out
    # 1→2→3 are sequential actions, not mix-all
    assert "식초" in order and ("냄새" in order or "줄이" in order)


def test_expand_enzyme_oxygen_all_stains():
    samples = [
        "효소를 바르고 30분. 흰옷 산소(테스트).",
        "Step 2. 효소로 단백질\n효소 30분",
        "식초로 냄새",
        "주방세제로 기름",
        "효소·세제",
    ]
    for s in samples:
        out = expand_owner_jargon(s, "ko")
        assert "효소계 세제" in out or "식초로 냄새 중화" in out or "주방세제(식기용" in out
        assert "효소로 단백질" not in out
        assert "효소·세제" not in out
        if "효소를 바르" in s:
            assert "라벨" in out or "프로테아제" in out
        if "산소" in s:
            assert "산소계 표백" in out or "과탄산" in out


def test_blood_also_gets_plain_enzyme():
    sid = "S_BLOOD_FRESH"
    raw = build_hand_motions(sid, "ko")
    m = expand_owner_jargon(raw, "ko")
    if "효소" in raw:
        assert "효소계 세제" in m


if __name__ == "__main__":
    test_expand_enzyme_oxygen_all_stains()
    test_tool_purpose()
    test_enzyme_emergency_reference_not_sop()
    test_gum_no_false_soak()
    test_fish_sauce_clarity_plain()
    test_blood_also_gets_plain_enzyme()
    print("plain_lang_v42 ok")
