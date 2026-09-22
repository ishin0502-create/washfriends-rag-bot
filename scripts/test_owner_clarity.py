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
        "protocol": {**proto.to_dict(), "garment_color": "white"},
        "stain_context": {"id": "S_HAIR_DYE"},
        "fabric_context": {"id": "F1", "name": "cotton"},
        "garment_color": "white",
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


def test_hide_aggressive_tools_when_fabric_unknown():
    from owner_answer_clarity import build_tools_names_only

    proto = _proto("S_BLACK_COFFEE")
    g_unknown = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_BLACK_COFFEE"},
        "tools": [],
    }
    tools_u = build_tools_names_only(g_unknown, "ko")
    assert "산소" not in tools_u

    g_white_cotton = {
        "protocol": {**proto.to_dict(), "garment_color": "white"},
        "stain_context": {"id": "S_BLACK_COFFEE"},
        "fabric_context": {"id": "F1", "name": "cotton"},
        "garment_color": "white",
        "tools": [],
    }
    tools_ok = build_tools_names_only(g_white_cotton, "ko")
    assert "산소" in tools_ok or "식초" in tools_ok


def test_silk_blocks_a1_in_one_line():
    from protocol import apply_context_to_protocol, _fabric_flags

    proto = apply_context_to_protocol(
        _proto("S_INK_PEN"),
        fabric="silk",
        garment_color="colored",
        flags=_fabric_flags({}, {"fabric_type": "silk"}),
    )
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_INK_PEN"},
        "fabric_context": {"id": "F4", "name": "silk"},
    }
    order = build_one_line_order(g, "ko")
    # A1 should be substituted to S1 / neutral — no alcohol action left active
    assert "알코올" not in order or "중성" in order
    for s in proto.steps:
        if s.chem == "A1":
            assert s.blocked or s.chem == "S1"
    assert any(s.chem == "S1" for s in proto.steps)


def test_l1_status_and_tea_milk_order():
    from owner_answer_clarity import STAIN_STATUS_KO
    from owner_hand_motions import build_hand_motions
    from ko_stain_education import KO_STAIN_EDU

    for sid in ("S_TEA", "S_MILK", "S_EGG", "S_CHOCOLATE", "S_FRUIT_JUICE", "S_KETCHUP"):
        assert sid in STAIN_STATUS_KO
        assert "먼저 확인" in STAIN_STATUS_KO[sid]
    tea_m = build_hand_motions("S_TEA", "ko")
    assert "우유" in tea_m and "효소" in tea_m
    assert "식초를 효소보다 먼저" in tea_m or "효소" in tea_m
    edu = KO_STAIN_EDU["S_TEA"]["fresh_path_ko"]
    assert "효소" in edu and "식초를 효소보다 먼저" in edu
    assert "라떼" in STAIN_STATUS_KO["S_BLACK_COFFEE"] or "우유" in STAIN_STATUS_KO["S_BLACK_COFFEE"]


def test_delicate_makeup_refuse():
    from owner_hand_motions import build_hand_motions

    g = {"fabric_context": {"id": "F4", "name": "silk"}}
    for sid in ("S_LIPSTICK", "S_FOUNDATION", "S_MASCARA"):
        ko = build_hand_motions(sid, "ko", graph=g)
        assert "거절" in ko or "전문" in ko
        assert "알코올" in ko  # warn / ban wording
        vi = build_hand_motions(sid, "vi", graph=g)
        assert "từ chối" in vi.lower() or "chuyên" in vi.lower()


def test_p2_glossary_blood_compound_intake_mildew():
    from stain_level_tags import GLOSSARY
    from owner_hand_motions import build_hand_motions, HAND_MOTIONS_EN
    from owner_mid_blocks_v40 import COMPOUND_STAINS, block_compound
    from owner_answer_clarity import STAIN_STATUS_KO
    from protocol import PROTOCOL_BUILDERS, apply_context_to_protocol

    assert "알코올" in GLOSSARY["ko"] and "L1 아님" in GLOSSARY["ko"]
    blood = build_hand_motions("S_BLOOD_FRESH", "ko")
    assert "15–30분" in blood or "15-30" in blood
    assert "【담금 시간】" not in blood.split("Step 2")[1].split("Step 3")[0]
    for sid in ("S_EGG", "S_TEA", "S_CHOCOLATE", "S_KETCHUP"):
        assert sid in COMPOUND_STAINS
    assert "신입용" in block_compound("S_EGG", "ko")
    for sid in (
        "S_PAINT_LATEX",
        "S_PAINT_OIL",
        "S_SWEAT_FRESH",
        "S_DEODORANT",
        "S_URINE",
        "S_VOMIT",
        "S_CHILI",
    ):
        assert sid in STAIN_STATUS_KO
        assert "먼저 확인" in STAIN_STATUS_KO[sid]
    assert "Step 1" in HAND_MOTIONS_EN["S_BLOOD_FRESH"]
    assert "enzyme" in HAND_MOTIONS_EN["S_TEA"].lower()
    mildew_u = apply_context_to_protocol(
        PROTOCOL_BUILDERS["S_MILDEW"](),
        fabric="",
        garment_color="white",
        flags={},
    )
    bleach_chems = {s.chem for s in mildew_u.steps if s.chem in {"B1", "B2"}}
    assert not bleach_chems, bleach_chems
    assert any(s.chem == "S1" for s in mildew_u.steps)
    hold = build_hand_motions("S_MILDEW", "ko", graph={})
    assert "원단" in hold and ("표백" in hold or "산소" in hold)


if __name__ == "__main__":
    test_hair_dye_no_spray_mix()
    test_two_message_split()
    test_chunk_long()
    test_vi_clarity_no_ko_en_stubs()
    test_hide_aggressive_tools_when_fabric_unknown()
    test_silk_blocks_a1_in_one_line()
    test_l1_status_and_tea_milk_order()
    test_delicate_makeup_refuse()
    test_p2_glossary_blood_compound_intake_mildew()
    print("OK two-msg clarity")
