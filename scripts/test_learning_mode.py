# -*- coding: utf-8 -*-
"""Learning mode + owner QA log — no LLM."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Isolate disk log for tests
_TMP = tempfile.mkdtemp(prefix="wf_qa_")
os.environ["WF_OWNER_QA_DIR"] = _TMP

from owner_qa_log import append_turn, get_mode, list_personal_cards, set_mode  # noqa: E402
from learning_quiz import build_deck, grade_answer, start_quiz  # noqa: E402
from learning_mode import try_handle_mode_or_quiz  # noqa: E402


def test_mode_switch():
    uid = "u-mode-1"
    set_mode(uid, "field")
    assert get_mode(uid) == "field"
    r = try_handle_mode_or_quiz(uid, "학습")
    assert r and "학습" in r
    assert get_mode(uid) == "learning"
    r2 = try_handle_mode_or_quiz(uid, "현장")
    assert r2 and "현장" in r2
    assert get_mode(uid) == "field"


def test_personal_cards_and_quiz():
    uid = "u-learn-2"
    set_mode(uid, "field")
    append_turn(
        uid,
        question="피 얼룩 어떻게 빼요?",
        answer="찬물만 사용. 온수 금지 — 단백질 고착. 100% 제거 약속 금지.",
        lang="ko",
        bot_mode="field",
    )
    cards = list_personal_cards(uid)
    assert cards, "expected heuristic cards from answer"
    deck = build_deck(uid, "ko", size=3)
    assert len(deck) >= 1
    body = start_quiz(uid, lang="ko", size=3)
    assert body
    g = grade_answer(uid, "O")
    assert g is not None


def test_ops_fallback_deck():
    uid = "u-new-3"
    set_mode(uid, "learning")
    deck = build_deck(uid, "ko", size=3)
    assert len(deck) >= 1, "OPS drills should fill empty personal log"


def test_menu():
    uid = "u-menu-4"
    r = try_handle_mode_or_quiz(uid, "모드")
    assert "현장" in r and "학습" in r


if __name__ == "__main__":
    test_mode_switch()
    test_personal_cards_and_quiz()
    test_ops_fallback_deck()
    test_menu()
    print("OK learning_mode", "dir=", _TMP)
