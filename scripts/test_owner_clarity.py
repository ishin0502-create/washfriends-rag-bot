# -*- coding: utf-8 -*-
"""Smoke checks for owner_answer_clarity + hair-dye tool binding."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owner_answer_clarity import build_one_line_order, inject_clarity_into_answer
from protocol import PROTOCOL_BUILDERS, bind_tools_from_protocol


def _proto(sid: str):
    return PROTOCOL_BUILDERS[sid]()


def test_hair_dye_no_spray_mix():
    proto = _proto("S_HAIR_DYE")
    assert proto is not None
    sp = proto.spray_step()
    assert sp is None, f"hair dye must not have spray_step, got {sp}"
    alcohol = next(s for s in proto.steps if s.id == "alcohol")
    assert alcohol.spray is False
    assert alcohol.chem == "A1"
    tools = bind_tools_from_protocol(proto, [])
    by_id = {t.get("id"): t for t in tools}
    # Timer should be stepwise for long B1
    timer = by_id.get("T_TIMER")
    assert timer, f"expected T_TIMER in {list(by_id)}"
    uf = timer.get("use_for_ko") or ""
    assert "먼저 타이머" in uf or "30분" in uf
    assert "밤새" in uf
    # If spray bottle present, must NOT say mix alcohol into bottle
    spray = by_id.get("T_SPRAY")
    if spray:
        uf2 = spray.get("use_for_ko") or ""
        assert "분무기에만 넣" not in uf2
        assert "분무기에 타지" in uf2 or "국소" in uf2 or "천" in uf2


def test_one_line_order_and_inject():
    proto = _proto("S_HAIR_DYE")
    g = {"protocol": proto.to_dict(), "stain_context": {"id": "S_HAIR_DYE"}}
    order = build_one_line_order(g, "ko")
    assert "【한 줄 순서】" in order
    assert "찬물" in order
    body = (
        "◆ [L2]\n"
        "┌─ 기본 안내 ─┐\n"
        "용어…\n"
        "└────────────┘\n"
        "▼ 이번 건 세탁 교육 (아래부터 SOP)\n"
        "━━━━━━━━━━━━━━━━\n"
        "(1) 테스트 본문\n"
        "약하게(흡수·찍어 바름만)·표백을 보류하며 진행합니다. 확인 후 조정하세요.\n"
    )
    out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang="ko")
    assert "【한 줄 순서】" in out
    assert "감독이 필요" in out
    assert "보류하며 진행" not in out
    assert "【다시 한번 고객 고지】" in out


def test_vinegar_still_spray():
    for sid in ("S_RED_WINE", "S_TEA", "S_BLACK_COFFEE"):
        if sid not in PROTOCOL_BUILDERS:
            continue
        p = _proto(sid)
        if p and p.spray_step() and (p.spray_step().chem or "").upper() == "A3":
            tools = bind_tools_from_protocol(p, [])
            spray = next((t for t in tools if t.get("id") == "T_SPRAY"), None)
            if spray:
                assert "분무기" in (spray.get("use_for_ko") or "")
                assert "타서" in (spray.get("use_for_ko") or "") or "넣" in (spray.get("use_for_ko") or "")
            return
    print("skip vinegar spray check — no A3 protocol found")


if __name__ == "__main__":
    test_hair_dye_no_spray_mix()
    test_one_line_order_and_inject()
    test_vinegar_still_spray()
    print("OK clarity + hair-dye bind")
