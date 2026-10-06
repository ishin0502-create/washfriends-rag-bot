# -*- coding: utf-8 -*-
"""L1 checkpoint quiz every few lessons; stain questions must still pass through."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["WF_OWNER_QA_DIR"] = tempfile.mkdtemp(prefix="wf_l1q_")

from l1_course import try_handle_l1_course, LESSONS  # noqa: E402


def test_checkpoint_after_third_next():
    uid = "l1q_user_a"
    assert try_handle_l1_course(uid, "교육")
    # pages 1 and 2: next advances
    r1 = try_handle_l1_course(uid, "다음")
    assert "확인 문제" not in (r1 or "")
    r2 = try_handle_l1_course(uid, "다음")
    assert "확인 문제" not in (r2 or "")
    # page 3 (blot) next → quiz
    q = try_handle_l1_course(uid, "다음")
    assert q and "확인 문제" in q
    assert "문지르" in q or "찍어" in q or "블롯" in q or "흡수" in q
    # cannot skip
    again = try_handle_l1_course(uid, "다음")
    assert again and "확인 문제" in again
    # stain question must not be captured
    assert try_handle_l1_course(uid, "면 셔츠에 피 얼룩이 있어요") is None
    # correct-ish answer
    ok = try_handle_l1_course(uid, "흰 천으로 수직으로 찍어 흡수")
    assert ok and "맞았습니다" in ok
    assert "3/17" in ok or "3/" in ok


def test_wrong_then_pass():
    uid = "l1q_user_b"
    try_handle_l1_course(uid, "교육")
    try_handle_l1_course(uid, "다음")
    try_handle_l1_course(uid, "다음")
    try_handle_l1_course(uid, "다음")
    bad = try_handle_l1_course(uid, "락스")
    assert bad and "아직" in bad
    good = try_handle_l1_course(uid, "찍어 흡수")
    assert good and "맞았습니다" in good


if __name__ == "__main__":
    test_checkpoint_after_third_next()
    test_wrong_then_pass()
    print("OK l1_checkpoint_quiz", "lessons", len(LESSONS))
