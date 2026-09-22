# -*- coding: utf-8 -*-
"""Smoke checks for two-message clarity + hair-dye binding."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owner_answer_clarity import (
    ZALO_MSG_SPLIT,
    build_one_line_order,
    for_ask_display,
    inject_clarity_into_answer,
    split_zalo_messages,
)
from protocol import PROTOCOL_BUILDERS, bind_tools_from_protocol


def _proto(sid: str):
    return PROTOCOL_BUILDERS[sid]()


def test_hair_dye_no_spray_mix():
    proto = _proto("S_HAIR_DYE")
    assert proto.spray_step() is None
    tools = bind_tools_from_protocol(proto, [])
    by_id = {t.get("id"): t for t in tools}
    timer = by_id.get("T_TIMER")
    assert timer
    uf = timer.get("use_for_ko") or ""
    assert "먼저 타이머" in uf or "30분" in uf


def test_two_message_split():
    proto = _proto("S_HAIR_DYE")
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_HAIR_DYE"},
        "chemicals": [{"code": "A1"}, {"code": "B1"}],
        "tools": [
            {"id": "T_CLOTH", "name_ko": "흰 면 천"},
            {"id": "T_TIMER", "name_ko": "타이머"},
            {"id": "T_SOAK_BIN", "name_ko": "담금통"},
        ],
    }
    body = (
        "┌─ 기본 안내 ─┐\n용어…\n└──┘\n"
        "▼ 이번 건 세탁 교육 (아래부터 SOP)\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) 오염 확인\n"
        "약하게(흡수·찍어 바름만)·표백을 보류하며 진행합니다. 확인 후 조정하세요.\n"
        "◆ (4) 알코올 블롯 30–180분\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="ko")
    assert ZALO_MSG_SPLIT.strip() in out or "<<<ZALO_MSG2>>>" in out
    parts = split_zalo_messages(out, max_len=1900)
    assert len(parts) >= 2
    flow, detail = parts[0], parts[1]
    assert "【한 줄 순서】" in flow
    assert "【준비물】" in flow
    assert "다음 메시지" in flow
    assert "손동작 상세" in detail or "구석 테스트" in detail
    assert "절대 하지" in detail
    # Pre-dry check may land in msg1 one-line order or a later Zalo chunk
    assert "말리기 전" in out
    assert "보류하며 진행" not in out
    assert "30–180" not in out
    assert "이소프로필" in flow or "70%" in flow
    assert detail.count("【담금 시간】") == 1
    assert "70~80" not in out and "50~60" not in out and "80%" not in out
    disp = for_ask_display(out)
    assert "메시지 1/" not in disp
    assert "—— 1/" in disp
    assert "<<<ZALO_MSG2>>>" not in disp


def test_chunk_long():
    long = "가" * 5000
    parts = split_zalo_messages(long, max_len=1900)
    assert len(parts) >= 3
    assert all(len(p) <= 1900 for p in parts)


def test_vi_clarity_no_ko_en_stubs():
    """VI must not get Korean hand-motions or English spot/donts stubs."""
    import re

    from owner_hand_motions import build_hand_motions

    assert "Bước" in build_hand_motions("S_HAIR_DYE", "vi")
    assert build_hand_motions("S_HAIR_DYE", "en") == ""

    proto = _proto("S_HAIR_DYE")
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_HAIR_DYE"},
        "chemicals": [{"code": "A1"}, {"code": "B1"}],
        "tools": [
            {"id": "T_CLOTH", "name_vi": "Khăn trắng"},
            {"id": "T_TIMER", "name_vi": "Hẹn giờ"},
        ],
    }
    body = (
        "┌─ Hướng dẫn ─┐\nthuật ngữ…\n└──┘\n"
        "▼ SOP cho vết này\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) Kiểm tra\n"
        "Nội dung VI dài.\n"
        "◆ (4) Cồn blot\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="vi")
    parts = split_zalo_messages(out)
    assert len(parts) >= 2
    detail = "\n".join(parts[1:])
    assert "Chi tiết thao tác" in detail
    assert "Thử góc" in detail or "Thời gian ngâm" in detail or "Tuyệt đối không" in detail
    assert "Bước 1" in detail
    assert "Spot-test first" not in detail
    assert "Do not: hot rinse" not in detail
    assert "Before drying:" not in detail
    assert "담금 시간" not in detail
    assert "이제 시작합니다" not in detail
    assert "장갑 끼고" not in detail
    assert "왜 이 순서인가요" not in detail
    assert not re.search(r"[가-힣]", detail)


if __name__ == "__main__":
    test_hair_dye_no_spray_mix()
    test_two_message_split()
    test_chunk_long()
    test_vi_clarity_no_ko_en_stubs()
    print("OK two-msg clarity")
