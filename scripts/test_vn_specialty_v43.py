# -*- coding: utf-8 -*-
"""VN specialty v43 + mildew leather P0."""
from __future__ import annotations

from education_vn_specialty_v43 import NEW_VN_STAINS_V43, FIRE_HAZARD_V43
from protocol import PROTOCOL_BUILDERS, apply_protocol_to_graph
from stain_hard_bind import bind_vn_specialty_stain, bind_sweat_or_yellow_stain
from owner_answer_clarity import build_one_line_order, inject_clarity_into_answer
from owner_mid_blocks_v40 import block_fire_hazard, block_mold_recurrence


def test_v43_protocols_registered():
    ids = [r["id"] for r in NEW_VN_STAINS_V43]
    assert len(ids) >= 8
    for sid in ids:
        assert sid in PROTOCOL_BUILDERS, sid
        p = PROTOCOL_BUILDERS[sid]()
        assert p.stain_id == sid
        assert p.why_ko and p.steps


def test_binds_chain_gasoline_sweat_sunscreen():
    assert bind_vn_specialty_stain("오토바이 체인 기름이 바지에") == "S_VN_CHAIN_OIL"
    assert bind_vn_specialty_stain("Quần bị dính dầu xích") == "S_VN_CHAIN_OIL"
    assert bind_vn_specialty_stain("옷에 휘발유 냄새가 나요") == "S_VN_GASOLINE"
    assert bind_vn_specialty_stain("Áo dính xăng") == "S_VN_GASOLINE"
    assert bind_vn_specialty_stain("브레이크액이 묻었어요") == "S_VN_BRAKE_FLUID"
    assert bind_sweat_or_yellow_stain("목둘레가 노랗게 — 선크림이랑 땀") == "S_VN_SWEAT_SUNSCREEN"


def test_gasoline_fire_tip():
    tip = block_fire_hazard("S_VN_GASOLINE", "ko")
    assert "건조기" in tip and "금지" in tip
    assert "S_VN_GASOLINE" in FIRE_HAZARD_V43


def test_mold_recurrence_block():
    assert "제습" in block_mold_recurrence("S_MILDEW", "ko")
    assert not block_mold_recurrence("S_GUM", "ko")


def test_leather_mildew_no_bleach_in_order():
    g = {
        "item_context": {"id": "I_LEATHER_GARMENT"},
        "stain_context": {"id": "S_MILDEW"},
        "tools": [{"id": "T_CLOTH"}],
        "chemicals": [{"code": "A3"}],
    }
    out = apply_protocol_to_graph(
        g,
        entities={
            "item_id": "I_LEATHER_GARMENT",
            "stain_id": "S_MILDEW",
            "_raw": "가죽 옷에 곰팡이가 묻었다",
        },
    )
    order = build_one_line_order(out, "ko")
    assert "락스" not in order
    assert "희석 락스" not in order
    joined = " ".join(
        str(s.get("action_ko") or "") for s in ((out.get("protocol") or {}).get("steps") or [])
    )
    assert "락스" not in joined


def test_chain_oil_clarity_two_stage():
    sid = "S_VN_CHAIN_OIL"
    proto = PROTOCOL_BUILDERS[sid]()
    g = {
        "_owner_stain_id": sid,
        "stain": {"id": sid},
        "protocol": proto.to_dict(),
        "stain_context": {"id": sid, "why_ko": proto.why_ko, "fresh_path_ko": ""},
        "chemicals": [{"code": "D2"}, {"code": "A3"}, {"code": "B1"}],
        "tools": [{"id": "T_CLOTH", "name_ko": "흰 면 천 여러 장"}],
        "_raw": "체인 기름",
    }
    out = inject_clarity_into_answer(
        "▼ 교육\n━━━━━━━━━━━━━━━━━━━━\n◆ 【용어】\nx\n\n" + proto.why_ko,
        graph=g,
        level="L2",
        grade=2,
        lang="ko",
    )
    assert "주방세제" in out
    assert "식초" in out or "철분" in out or "레몬" in out


if __name__ == "__main__":
    test_v43_protocols_registered()
    test_binds_chain_gasoline_sweat_sunscreen()
    test_gasoline_fire_tip()
    test_mold_recurrence_block()
    test_leather_mildew_no_bleach_in_order()
    test_chain_oil_clarity_two_stage()
    print("vn_specialty_v43 ok")
