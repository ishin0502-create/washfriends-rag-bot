# -*- coding: utf-8 -*-
"""Mid-tier v40 assembly: intake / fabric / compound / chem / retry."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owner_answer_clarity import inject_clarity_into_answer, split_zalo_messages
from owner_mid_blocks_v40 import (
    block_chem,
    block_compound,
    block_fabric,
    block_intake,
    block_retry,
    wants_mix_block,
)
from protocol import PROTOCOL_BUILDERS


def _body() -> str:
    return (
        "┌─ 기본 ─┐\n└──┘\n"
        "▼ 이번 건 세탁 교육\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) x\n"
    )


def _graph(sid: str, raw: str = "", fabric: str = "", chems: list | None = None) -> dict:
    proto = PROTOCOL_BUILDERS[sid]()
    return {
        "protocol": proto.to_dict(),
        "stain_context": {"id": sid},
        "chemicals": chems or [{"code": "E1"}, {"code": "B1"}],
        "tools": [],
        "entities": {"fabric_type": fabric} if fabric else {},
        "_raw": raw,
        "match_diagnosis": {"fabric_type": fabric} if fabric else {},
    }


def test_l1_no_intake_no_retry():
    assert block_intake("L1", "ko") == ""
    assert block_retry("S_BLACK_COFFEE", "L1", {}, "ko") == ""


def test_l2_intake_and_retry_short():
    assert "사진" in block_intake("L2", "ko")
    r = block_retry("S_RED_WINE", "L2", {"_raw": "와인"}, "ko")
    assert "2차" in r or "안 빠" in r
    assert "60~80" not in r and "%" not in r.replace("100%", "")  # allow nothing
    assert not re.search(r"\d{2}\s*~\s*\d{2}\s*%", r)


def test_compound_bbq():
    assert "복합" in block_compound("S_BBQ_SAUCE", "ko")
    assert block_compound("S_MUD", "ko") == ""


def test_chem_mix_full_and_multi_short():
    assert wants_mix_block({"_raw": "락스랑 식초 섞어도 돼요?"})
    full = block_chem({"_raw": "락스랑 식초 섞어도"}, "ko")
    assert "염소 가스" in full or "유독" in full
    short = block_chem({"_raw": "커피", "chemicals": [{"code": "A3"}, {"code": "B1"}]}, "ko")
    assert "한 번에 하나" in short
    assert block_chem({"_raw": "커피", "chemicals": [{"code": "A3"}]}, "ko") == ""


def test_fabric_silk_short_and_full_on_question():
    short = block_fabric({"entities": {"fabric_type": "silk"}, "_raw": "실크 커피"}, "ko")
    assert "실크" in short and "중성" in short
    full = block_fabric({"_raw": "원단이 뭔지 모르겠어요"}, "ko")
    assert "원단 판단" in full or "라벨" in full


def test_inject_bbq_l2_has_compound_intake_retry():
    g = _graph("S_BBQ_SAUCE", raw="흰 셔츠에 BBQ 소스")
    out = inject_clarity_into_answer(_body(), graph=g, level="L2", grade=2, lang="ko")
    parts = split_zalo_messages(out)
    flow, detail = parts[0], "\n".join(parts[1:])
    assert "접수 체크" in flow
    assert "복합" in detail
    assert "약품 여러 개" in detail or "약품 상호작용" in detail
    assert "안 빠졌" in detail or "2차" in detail
    assert not re.search(r"\d{2}\s*~\s*\d{2}\s*%", out)


def test_inject_l1_coffee_no_l2_intake():
    g = _graph("S_BLACK_COFFEE", raw="커피 얼룩", chems=[{"code": "A3"}])
    out = inject_clarity_into_answer(_body(), graph=g, level="L1", grade=1, lang="ko")
    assert "접수 체크" not in out
    assert "안 빠졌을 때 · L2" not in out


def test_retry_protein_no_heat():
    r = block_retry("S_BLOOD_FRESH", "L2", {"_raw": "피가 안 빠져요 2차"}, "ko")
    assert "수온 올리지" in r or "단백질" in r
    assert "매니저" in r


def test_retry_full_on_keyword():
    r = block_retry("S_INK_PEN", "L2", {"_raw": "1차에 안 빠졌는데 어떻게?"}, "ko")
    assert "3차" in r and "아세톤" in r
