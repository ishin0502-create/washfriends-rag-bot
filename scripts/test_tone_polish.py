# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reply_lang import system_prompt_for


def test_ko_tone_rules_present():
    p = system_prompt_for("ko")
    assert "본사 현장 교육" in p
    assert "번역투" in p or "장황" in p
    assert "브랜드" in p
    assert "고객 응대" in p
    iw = system_prompt_for("ko", item_wash=True)
    assert "본사 현장 교육" in iw
    assert "빈말" in iw or "지시형" in iw


def test_vi_en_tone_present():
    assert "Ngắn" in system_prompt_for("vi") or "ra lệnh" in system_prompt_for("vi")
    assert "floor-training" in system_prompt_for("en") or "Short" in system_prompt_for("en")


if __name__ == "__main__":
    test_ko_tone_rules_present()
    test_vi_en_tone_present()
    print("OK tone_polish")
