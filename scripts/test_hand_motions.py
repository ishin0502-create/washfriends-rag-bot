# -*- coding: utf-8 -*-
"""Smoke: hand motions replace ◆(1)~(6) in message 2."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owner_answer_clarity import inject_clarity_into_answer, split_zalo_messages
from owner_hand_motions import build_hand_motions, has_hand_motions
from protocol import PROTOCOL_BUILDERS


def test_hair_motions_present():
    m = build_hand_motions("S_HAIR_DYE", "ko")
    assert "Step 2" in m
    assert "뒤집어" in m
    assert "꾹 3초" in m or "3초" in m
    assert "◆ (1)" not in m


def test_l1_full_coverage():
    from owner_hand_motions import l1_motion_coverage, HAND_MOTIONS_KO
    from stain_level_tags import L1

    missing = l1_motion_coverage()
    assert not missing, f"missing L1 motions: {missing}"
    for sid in L1:
        m = HAND_MOTIONS_KO[sid]
        assert "Step 1" in m
        assert "◆ (1)" not in m


def test_kimchi_specific():
    from owner_hand_motions import build_hand_motions

    m = build_hand_motions("S_KIMCHI")
    assert "고춧가루" in m
    assert "치약" in m
    assert "주방세제" in m


def test_oil_starch():
    from owner_hand_motions import build_hand_motions

    m = build_hand_motions("S_COOKING_OIL")
    assert "전분" in m
    assert "미끄러" in m


def test_inject_drops_toc():
    proto = PROTOCOL_BUILDERS["S_HAIR_DYE"]()
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_HAIR_DYE"},
        "chemicals": [{"code": "A1"}, {"code": "B1"}],
        "tools": [{"id": "T_CLOTH", "name_ko": "흰 면 천"}],
    }
    body = (
        "┌─ 기본 ─┐\n└──┘\n"
        "▼ 이번 건 세탁 교육 (아래부터 SOP)\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) 👕 오염 확인하세요\n긴 확인 본문\n"
        "◆ (2) 🧰 도구를 준비하세요\n긴 도구\n"
        "◆ (4) 🧴 약품\n알코올\n"
        "◆ [왜 이 순서인가요]\n염모제는 강한 색소입니다.\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="ko")
    parts = split_zalo_messages(out)
    assert len(parts) >= 2
    detail = "\n".join(parts[1:])
    assert "Step 2" in detail
    assert "뒤집어" in detail
    assert "◆ (1) 👕" not in detail
    assert "◆ (2) 🧰" not in detail
    assert "긴 도구" not in detail
    assert "한 줄 순서" in parts[0]
    assert "왜 이 순서" in detail


if __name__ == "__main__":
    test_hair_motions_present()
    test_l1_full_coverage()
    test_kimchi_specific()
    test_oil_starch()
    test_inject_drops_toc()
    print("OK hand motions L1 complete")
