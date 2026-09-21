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


def test_l2_priority_coverage():
    from owner_hand_motions import l2_priority_coverage, HAND_MOTIONS_KO, _L2_PRIORITY

    missing = l2_priority_coverage()
    assert not missing, f"missing L2 priority motions: {missing}"
    assert len(_L2_PRIORITY) == 15
    for sid in _L2_PRIORITY:
        m = HAND_MOTIONS_KO[sid]
        assert "Step 1" in m
        assert "◆ (1)" not in m


def test_l2_milk_coffee_order():
    from owner_hand_motions import build_hand_motions

    m = build_hand_motions("S_MILK_COFFEE")
    assert "효소" in m and "식초" in m
    assert m.index("효소") < m.index("식초") or "단백질" in m


def test_l2_lipstick_no_rub():
    from owner_hand_motions import build_hand_motions

    m = build_hand_motions("S_LIPSTICK")
    assert "문지르" in m
    assert "알코올" in m


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


def test_vi_no_ko_motions():
    import re
    from owner_hand_motions import build_hand_motions, HAND_MOTIONS_VI, vi_priority_coverage

    assert not vi_priority_coverage()
    assert len(HAND_MOTIONS_VI) >= 10
    m = build_hand_motions("S_HAIR_DYE", "vi")
    assert "Bước 1" in m
    assert "cồn" in m.lower() or "Cồn" in m or "chấm cồn" in m.lower() or "Chấm cồn" in m
    assert "이제 시작합니다" not in m
    assert not re.search(r"[가-힣]", m)
    assert build_hand_motions("S_MILK_COFFEE", "en") == ""
    assert "Bước" in build_hand_motions("S_MILK_COFFEE", "vi")
    assert "Bước" in build_hand_motions("S_EGG", "vi")
    assert "전문" in build_hand_motions("S_ENGINE_OIL", "ko") or "전문 의뢰" in build_hand_motions(
        "S_ENGINE_OIL", "ko"
    )
    assert "chuyên" in build_hand_motions("S_ENGINE_OIL", "vi").lower() or "chuyên" in build_hand_motions(
        "S_LATERITE", "vi"
    )


def test_l2_rest_and_l3():
    from owner_hand_motions import (
        HAND_MOTIONS_KO,
        l2_rest_coverage,
        l3_motion_coverage,
        build_hand_motions,
    )

    assert not l2_rest_coverage()
    assert not l3_motion_coverage()
    assert "락스" in build_hand_motions("S_SHIRT_YELLOW", "ko")
    assert "거절" in build_hand_motions("S_GLUE", "ko") or "등급 3" in build_hand_motions("S_GLUE", "ko")
    assert "S_CURRY" in HAND_MOTIONS_KO
    assert "S_TAR" in HAND_MOTIONS_KO


def test_vi_inject_uses_vi_steps():
    import re

    proto = PROTOCOL_BUILDERS["S_HAIR_DYE"]()
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_HAIR_DYE"},
        "chemicals": [{"code": "A1"}, {"code": "B1"}],
        "tools": [{"id": "T_CLOTH", "name_vi": "Khăn trắng"}],
    }
    body = (
        "┌─ Hướng dẫn ─┐\n└──┘\n"
        "▼ SOP cho vết này\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) Kiểm tra\nNội dung LLM\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="vi")
    parts = split_zalo_messages(out)
    detail = "\n".join(parts[1:])
    assert "Bước 2" in detail
    assert "Lộn trái" in detail
    assert "장갑" not in detail
    assert "Spot-test first" not in detail
    assert not re.search(r"[가-힣]", detail)


if __name__ == "__main__":
    test_hair_motions_present()
    test_l1_full_coverage()
    test_l2_priority_coverage()
    test_l2_milk_coffee_order()
    test_l2_lipstick_no_rub()
    test_kimchi_specific()
    test_oil_starch()
    test_inject_drops_toc()
    test_vi_no_ko_motions()
    test_l2_rest_and_l3()
    test_vi_inject_uses_vi_steps()
    print("OK hand motions L1+L2+L3+VI")
