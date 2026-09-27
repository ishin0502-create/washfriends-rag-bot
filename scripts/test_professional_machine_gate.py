# -*- coding: utf-8 -*-
"""Professional dry-machine gate: OFF lock / ON unlock; no invented PROG."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from professional_machine_gate import (
    is_professional_machine_question,
    try_professional_machine_card,
)


def test_detect_realstar_and_prog():
    assert is_professional_machine_question("리어스타 PROG 몇 번이에요?")
    assert is_professional_machine_question("드라이클리닝 기계 코스 어떻게?")
    assert not is_professional_machine_question("면 티셔츠 세탁기 40도")


def test_off_returns_lock():
    with patch("professional_machine_gate.resolve_has_machine", return_value=False):
        out = try_professional_machine_card(
            "리어스타 몇 번 버튼?", lang="ko", user_id="u1"
        )
    assert "교육 잠금" in out
    assert "본사" in out
    assert "구비" in out or "확인" in out


def test_on_returns_unlock_no_fake_prog():
    with patch("professional_machine_gate.resolve_has_machine", return_value=True):
        out = try_professional_machine_card(
            "Realstar dry clean machine PROG?", lang="ko", user_id="u1"
        )
    assert "교육 해금" in out
    assert "매뉴얼" in out or "본사" in out
    # Must not invent a specific PROG number like "PROG 12"
    assert not re_has_fake_prog(out)


def re_has_fake_prog(text: str) -> bool:
    import re

    return bool(re.search(r"PROG\s*\d{1,3}\b", text or "", re.I))


def test_non_machine_returns_empty():
    with patch("professional_machine_gate.resolve_has_machine", return_value=True):
        assert try_professional_machine_card("커피 얼룩 면", lang="ko", user_id="u1") == ""


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            fn()
            print("OK", name)
        except Exception as e:
            failed += 1
            print("FAIL", name, e)
    raise SystemExit(failed)
