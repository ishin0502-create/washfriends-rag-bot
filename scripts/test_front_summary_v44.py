# -*- coding: utf-8 -*-
"""Day-0 front summary card on message 1 — long SOP stays in message 2."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from owner_answer_clarity import (
    build_front_summary,
    inject_clarity_into_answer,
    split_zalo_messages,
)
from protocol import PROTOCOL_BUILDERS


def _g(sid: str, *, fabric: str = "cotton", color: str = "white", lang_raw: str = ""):
    proto = PROTOCOL_BUILDERS[sid]()
    return {
        "protocol": {**proto.to_dict(), "garment_color": color},
        "stain_context": {"id": sid},
        "fabric_context": {"id": "F1", "name": fabric},
        "garment_color": color,
        "entities": {"fabric_type": fabric},
        "chemicals": [{"code": "A1"}],
        "tools": [{"id": "T_CLOTH", "name_ko": "흰 면 천", "name_vi": "Khăn trắng"}],
        "_raw": lang_raw or "면 셔츠 얼룩",
    }


def _body(lang: str = "ko") -> str:
    if lang == "vi":
        return (
            "┌─ Hướng dẫn ─┐\n└──┘\n"
            "▼ 이번 건 세탁 교육\n"
            "━━━━━━━━━━━━━━━━\n"
            "◆ (1) x\n"
        )
    return (
        "┌─ 기본 ─┐\n└──┘\n"
        "▼ 이번 건 세탁 교육\n"
        "━━━━━━━━━━━━━━━━\n"
        "◆ (1) x\n"
    )


def test_front_summary_ko_has_steps_and_ban():
    s = build_front_summary(_g("S_BLACK_COFFEE"), "ko")
    assert "【지금 바로】" in s
    assert re.search(r"^\d+\)\s+", s, re.M)
    assert "금지" in s
    assert "다음 메시지" in s
    assert s.count("\n") <= 8


def test_front_summary_vi_no_hangul():
    s = build_front_summary(_g("S_BLOOD_FRESH", lang_raw="Mau tuoi"), "vi")
    assert "Làm ngay" in s
    assert not re.search(r"[가-힣]", s)
    assert "Cấm" in s or "Không" in s


def test_inject_puts_summary_in_msg1_keeps_detail_msg2():
    out = inject_clarity_into_answer(
        _body("ko"),
        graph=_g("S_BLACK_COFFEE"),
        level="L1",
        grade=1,
        lang="ko",
    )
    parts = split_zalo_messages(out)
    assert len(parts) >= 2
    flow, detail = parts[0], "\n".join(parts[1:])
    assert "【지금 바로】" in flow
    assert "금지(짧게)" in flow
    # Full donts + motions remain in later part(s)
    assert "절대 하지" in detail
    assert "손동작" in detail or "Step" in detail or "흡수" in detail


def test_inject_vi_summary_no_hangul_in_flow():
    out = inject_clarity_into_answer(
        _body("vi"),
        graph=_g("S_BLOOD_FRESH", lang_raw="Ao dinh mau"),
        level="L1",
        grade=1,
        lang="vi",
    )
    flow = split_zalo_messages(out)[0]
    assert "Làm ngay" in flow
    # Job banner may still be KO from test fixture front; check summary region has no KO
    # Take from Làm ngay onward
    idx = flow.find("Làm ngay")
    assert idx >= 0
    assert not re.search(r"[가-힣]", flow[idx:])


def test_silk_wine_still_refuse_in_detail():
    g = _g("S_RED_WINE", fabric="silk", color="unknown", lang_raw="실크 와인")
    g["match_diagnosis"] = {"fabric_type": "silk"}
    out = inject_clarity_into_answer(_body("ko"), graph=g, level="L3", grade=3, lang="ko")
    detail = "\n".join(split_zalo_messages(out)[1:])
    assert "거절" in detail or "전문" in detail
    assert "【지금 바로】" in split_zalo_messages(out)[0]


if __name__ == "__main__":
    test_front_summary_ko_has_steps_and_ban()
    test_front_summary_vi_no_hangul()
    test_inject_puts_summary_in_msg1_keeps_detail_msg2()
    test_inject_vi_summary_no_hangul_in_flow()
    test_silk_wine_still_refuse_in_detail()
    print("OK front_summary_v44")
