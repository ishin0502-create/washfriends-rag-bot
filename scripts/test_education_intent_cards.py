# -*- coding: utf-8 -*-
"""Tests for education intent cards + VN v43 motions + silk coffee align."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_intent_cards():
    from education_intent_cards import try_intent_education_card

    assert "과탄산" in try_intent_education_card("산소표백제가 뭐예요?", "ko")
    assert "락스" in try_intent_education_card("산소표백제가 뭐예요?", "ko")
    assert "니트릴" in try_intent_education_card("니트릴 장갑은 왜 써요?", "ko")
    assert "손을 보호" in try_intent_education_card("니트릴 장갑은 왜 써요?", "ko")
    assert "등급 3" in try_intent_education_card("명품 핸드백에 얼룩이 생겼어요", "ko")
    assert "재시도" in try_intent_education_card("1차에 안 빠졌어요, 어떻게 해요?", "ko")
    assert "말리기 전" in try_intent_education_card("얼룩이 다 빠진 것 같은데 건조기 돌려도 돼요?", "ko")
    assert "L1" in try_intent_education_card("초보인데 어디서 시작해요?", "ko")
    assert "소수성" not in try_intent_education_card("초보인데 어디서 시작해요?", "ko")
    # should NOT steal normal stain SOPs
    assert try_intent_education_card("면티에 커피 얼룩", "ko") == ""


def test_silk_coffee_neutral_motions():
    from owner_hand_motions import build_hand_motions

    g = {"fabric_context": {"id": "F4", "name": "silk"}}
    m = build_hand_motions("S_BLACK_COFFEE", "ko", graph=g)
    assert "중성" in m
    assert "식초 1 : 물 4" not in m and "식초 1:4" not in m


def test_vn_v43_motions_complete():
    from owner_hand_motions import build_hand_motions
    from protocol import PROTOCOL_BUILDERS

    for sid in (
        "S_VN_CHAIN_OIL",
        "S_VN_GASOLINE",
        "S_VN_BRAKE_FLUID",
        "S_VN_EXHAUST_SOOT",
        "S_VN_RUBBER_MARK",
        "S_VN_CEMENT",
        "S_VN_ACID_RAIN",
        "S_VN_SWEAT_SUNSCREEN",
    ):
        assert sid in PROTOCOL_BUILDERS
        assert build_hand_motions(sid, "ko"), sid
        assert build_hand_motions(sid, "vi"), sid
    assert "체인" in build_hand_motions("S_VN_CHAIN_OIL", "ko")


def test_chain_oil_bind():
    from stain_hard_bind import bind_vn_specialty_stain

    assert bind_vn_specialty_stain("오토바이 체인 기름이 바지에 묻었어요") == "S_VN_CHAIN_OIL"
    assert bind_vn_specialty_stain("체인기름 얼룩") == "S_VN_CHAIN_OIL"


def test_one_line_dedup_s1():
    from owner_answer_clarity import build_one_line_order
    from protocol import PROTOCOL_BUILDERS, apply_context_to_protocol, _fabric_flags

    proto = apply_context_to_protocol(
        PROTOCOL_BUILDERS["S_MILDEW"](),
        fabric="wool",
        garment_color="colored",
        flags=_fabric_flags({}, {"fabric_type": "wool"}),
    )
    g = {
        "protocol": proto.to_dict(),
        "stain_context": {"id": "S_MILDEW"},
        "fabric_context": {"id": "F3", "name": "wool"},
    }
    order = build_one_line_order(g, "ko")
    # should not repeat identical neutral lines back-to-back
    bodies = []
    for ln in order.splitlines():
        if ln[:1].isdigit() and ") " in ln:
            bodies.append(ln.split(") ", 1)[1].split(" (")[0].strip())
    for a, b in zip(bodies, bodies[1:]):
        assert a != b, (a, order)


if __name__ == "__main__":
    test_intent_cards()
    test_silk_coffee_neutral_motions()
    test_vn_v43_motions_complete()
    test_chain_oil_bind()
    test_one_line_dedup_s1()
    print("OK intent + vn43 + silk coffee")
