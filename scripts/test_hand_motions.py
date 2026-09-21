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
    assert "70%" in m or "이소프로필" in m
    assert "환기" in m
    assert "⑧" in m or "8)" in m or "한 번 헹궈" in m
    assert "15~20" in m or "15–20" in m
    assert "【담금 시간】" in m
    assert "건너뛰" in m


def test_hair_dye_clarity_p0():
    """P0: soak inside Step3 only, IPA tools, state outlook, no %."""
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
        "◆ (1) x\n"
        "◆ [왜 이 순서인가요]\n염모제는 강한 색소입니다.\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="ko")
    parts = split_zalo_messages(out)
    flow, detail = parts[0], "\n".join(parts[1:])
    assert detail.count("【담금 시간】") == 1
    assert "이소프로필" in flow or "70%" in flow
    assert "산소" in flow
    assert "이미 말랐다" in flow or "말랐다" in flow
    assert "고객께 먼저" in flow or "진행할까요" in flow
    # IPA "70%" in tools is OK; ban success-rate style percents
    assert "70~80" not in out and "50–60" not in out and "50~60" not in out
    assert "30%" not in out and "80%" not in out
    assert "환기" in detail
    assert "밀폐" in detail or "환기" in detail
    assert "이소프로필" in detail
    # Blood still gets common soak above steps (no soak heading in blood motions)
    g2 = {
        "protocol": PROTOCOL_BUILDERS["S_BLOOD_FRESH"]().to_dict(),
        "stain_context": {"id": "S_BLOOD_FRESH"},
        "chemicals": [],
        "tools": [],
    }
    body2 = (
        "┌─ 기본 ─┐\n└──┘\n"
        "▼ 이번 건 세탁 교육\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) x\n"
    )
    out2 = inject_clarity_into_answer(body2, graph=g2, level="L1", grade=1, lang="ko")
    d2 = "\n".join(split_zalo_messages(out2)[1:])
    assert "【담금 시간】" in d2
    # Common soak appears before Step for blood (motions reference it, don't embed heading)
    assert d2.index("【담금 시간】") < d2.index("Step 1") or "담가" in d2


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
    assert "70%" in m or "이소프로필" in m
    assert "환기" in m


def test_phase4_ink_mascara_rich():
    from owner_hand_motions import build_hand_motions

    ink = build_hand_motions("S_INK_PEN", "ko")
    assert "70%" in ink or "이소프로필" in ink
    assert "환기" in ink
    assert "⑧" in ink or "한 번 헹궈" in ink
    mas = build_hand_motions("S_MASCARA", "ko")
    assert "알코올" in mas or "IPA" in mas
    assert "환기" in mas
    vi_ink = build_hand_motions("S_INK_PEN", "vi")
    assert "70%" in vi_ink or "isopropyl" in vi_ink.lower()
    assert "thông gió" in vi_ink.lower() or "Thông gió" in vi_ink


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
        HAND_MOTIONS_VI,
        l2_rest_coverage,
        l3_motion_coverage,
        build_hand_motions,
        protocol_motion_gaps,
    )

    assert not l2_rest_coverage()
    assert not l3_motion_coverage()
    assert not protocol_motion_gaps(), protocol_motion_gaps()
    assert "락스" in build_hand_motions("S_SHIRT_YELLOW", "ko")
    assert "거절" in build_hand_motions("S_GLUE", "ko") or "등급 3" in build_hand_motions("S_GLUE", "ko")
    assert "S_CURRY" in HAND_MOTIONS_KO
    assert "S_TAR" in HAND_MOTIONS_KO
    assert "S_SUGARCANE" in HAND_MOTIONS_KO
    assert "S_DOENJANG" in HAND_MOTIONS_KO
    assert "Bước" in build_hand_motions("S_SUGARCANE", "vi")
    assert "Bước" in build_hand_motions("S_MUSTARD", "vi")
    assert len(HAND_MOTIONS_VI) >= len(HAND_MOTIONS_KO) - 5  # VI near-parity


def test_soft_outlook_no_percent():
    from owner_answer_clarity import inject_clarity_into_answer, split_zalo_messages
    from protocol import PROTOCOL_BUILDERS

    proto = PROTOCOL_BUILDERS["S_BLOOD_FRESH"]()
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_BLOOD_FRESH"},
        "chemicals": [],
        "tools": [],
    }
    body = (
        "┌─ 기본 ─┐\n└──┘\n"
        "▼ 이번 건 세탁 교육\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) x\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L1", grade=1, lang="ko")
    parts = split_zalo_messages(out)
    assert "예상 결과" in parts[0]
    assert "%" not in parts[0]
    assert "80%" not in out and "60–80" not in out


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
    assert detail.count("【Thời gian ngâm】") == 1
    assert "thông gió" in detail.lower() or "Thông gió" in detail
    assert "70%" in detail or "isopropyl" in detail.lower()
    assert "70~80" not in out and "50~60" not in out and "80%" not in out
    assert "Kiểm tra trước" in parts[0] or "ướt" in parts[0].lower()


if __name__ == "__main__":
    test_hair_motions_present()
    test_hair_dye_clarity_p0()
    test_l1_full_coverage()
    test_l2_priority_coverage()
    test_l2_milk_coffee_order()
    test_l2_lipstick_no_rub()
    test_phase4_ink_mascara_rich()
    test_kimchi_specific()
    test_oil_starch()
    test_inject_drops_toc()
    test_vi_no_ko_motions()
    test_l2_rest_and_l3()
    test_soft_outlook_no_percent()
    test_vi_inject_uses_vi_steps()
    print("OK hand motions full + soft outlook")
