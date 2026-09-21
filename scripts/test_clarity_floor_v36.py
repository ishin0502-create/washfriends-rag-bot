# -*- coding: utf-8 -*-
"""Phase 0 floor + Phase 1 yellow bind + Phase 3 silk×wine motion."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owner_answer_clarity import (
    STAIN_SOFT_OUTLOOK,
    STAIN_STATUS_KO,
    STAIN_TOOL_EXTRAS,
    inject_clarity_into_answer,
    split_zalo_messages,
)
from owner_hand_motions import build_hand_motions
from protocol import PROTOCOL_BUILDERS
from stain_hard_bind import bind_sweat_or_yellow_stain


def test_phase1_yellow_not_fresh():
    assert bind_sweat_or_yellow_stain("오래된 땀 얼룩이 노랗게 변했어요") == "S_SWEAT_YELLOW"
    assert bind_sweat_or_yellow_stain("겨드랑이가 누렇게 됐어요") == "S_SWEAT_YELLOW"
    assert bind_sweat_or_yellow_stain("방금 땀 묻었어요") == "S_SWEAT_FRESH"
    assert bind_sweat_or_yellow_stain("와이셔츠가 누렇게 변했어요") == "S_SHIRT_YELLOW"
    assert bind_sweat_or_yellow_stain("땀억제제 자국") is None  # deodorant handled elsewhere


def test_phase0_floor_no_percent_and_blocks():
    for sid in ("S_HAIR_DYE", "S_RED_WINE", "S_SWEAT_YELLOW"):
        assert sid in STAIN_STATUS_KO
        assert sid in STAIN_TOOL_EXTRAS
        assert sid in STAIN_SOFT_OUTLOOK
    proto = PROTOCOL_BUILDERS["S_SWEAT_YELLOW"]()
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_SWEAT_YELLOW"},
        "chemicals": [{"code": "E1"}, {"code": "B1"}],
        "tools": [],
        "_raw": "오래된 땀이 노랗게",
    }
    body = (
        "┌─ 기본 ─┐\n└──┘\n"
        "▼ 이번 건 세탁 교육\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) x\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="ko")
    parts = split_zalo_messages(out)
    flow = parts[0]
    detail = "\n".join(parts[1:])
    assert "【예상 결과】" in flow
    assert "【먼저 확인】" in flow
    assert "【준비물】" in flow
    assert "절대 하지" in detail
    assert "말리기 전" in detail
    assert "70~80" not in out and "50~60" not in out
    assert not re.search(r"\b\d{2}\s*~\s*\d{2}\s*%", out)


def test_phase3_silk_wine_refuse_motions():
    proto = PROTOCOL_BUILDERS["S_RED_WINE"]()
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_RED_WINE"},
        "chemicals": [{"code": "A3"}],
        "tools": [],
        "entities": {"fabric_type": "silk"},
        "_raw": "실크 블라우스에 레드와인이 쏟아졌어요",
        "match_diagnosis": {"fabric_type": "silk"},
    }
    m = build_hand_motions("S_RED_WINE", "ko", graph=g)
    assert "거절" in m or "전문" in m
    assert "산소에 15" not in m

    body = (
        "┌─ 기본 ─┐\n└──┘\n"
        "▼ 이번 건 세탁 교육\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) x\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L3", grade=3, lang="ko")
    detail = "\n".join(split_zalo_messages(out)[1:])
    assert "거절" in detail or "전문" in detail
    assert "흰 면·린넨: 산소" not in detail


def test_phase3_cotton_wine_keeps_normal():
    m = build_hand_motions(
        "S_RED_WINE",
        "ko",
        graph={
            "entities": {"fabric_type": "cotton"},
            "_raw": "면 티에 레드와인",
        },
    )
    assert "흡수" in m
    assert "【담금 시간】" in m
    assert "소금" in m
    assert "식초" in m


def test_sweat_yellow_rich_steps():
    m = build_hand_motions("S_SWEAT_YELLOW", "ko")
    assert "락스" in m
    assert "【담금 시간】" in m
    assert "흰옷만" in m
    vi = build_hand_motions("S_SWEAT_YELLOW", "vi")
    assert "javel" in vi.lower() or "Javel" in vi
    assert "Thời gian ngâm" in vi


if __name__ == "__main__":
    test_phase1_yellow_not_fresh()
    test_phase0_floor_no_percent_and_blocks()
    test_phase3_silk_wine_refuse_motions()
    test_phase3_cotton_wine_keeps_normal()
    print("OK phase0-3 floor/bind/silk")
