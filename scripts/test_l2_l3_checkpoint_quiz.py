# -*- coding: utf-8 -*-
"""L2/L3 checkpoints like L1; stain questions still pass through."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["WF_OWNER_QA_DIR"] = tempfile.mkdtemp(prefix="wf_l23q_")

from l1_course import LESSONS as L1  # noqa: E402
from l2_course import LESSONS as L2, try_handle_l2_course  # noqa: E402
from l3_course import LESSONS as L3, try_handle_l3_course  # noqa: E402
from owner_qa_log import load_user, save_user  # noqa: E402


def _finish_l1(uid: str) -> None:
    u = load_user(uid)
    u["l1_course"] = {
        "active": False,
        "index": len(L1) - 1,
        "completed": [les["id"] for les in L1],
    }
    save_user(uid, u)


def _finish_l2(uid: str) -> None:
    u = load_user(uid)
    u["l2_course"] = {
        "active": False,
        "index": len(L2) - 1,
        "completed": [les["id"] for les in L2],
        "quiz_passed": [],
        "pending_quiz": None,
    }
    save_user(uid, u)


def test_l2_checkpoint():
    uid = "l2q_user_a"
    _finish_l1(uid)
    start = try_handle_l2_course(uid, "중급")
    assert start and "중급" in start
    q = try_handle_l2_course(uid, "다음")
    assert q and "확인 문제" in q
    again = try_handle_l2_course(uid, "다음")
    assert again and "확인 문제" in again
    assert try_handle_l2_course(uid, "면 셔츠에 피 얼룩이 있어요") is None
    bad = try_handle_l2_course(uid, "락스")
    assert bad and "아직" in bad
    ok = try_handle_l2_course(uid, "안됨 금지")
    assert ok and "맞았습니다" in ok


def test_l3_checkpoint():
    uid = "l3q_user_a"
    _finish_l1(uid)
    _finish_l2(uid)
    start = try_handle_l3_course(uid, "고급")
    assert start and "고급" in start
    q = try_handle_l3_course(uid, "다음")
    assert q and "확인 문제" in q
    assert try_handle_l3_course(uid, "면 셔츠에 커피 얼룩") is None
    ok = try_handle_l3_course(uid, "원단 재판단 후 다른 계열인지 확인")
    assert ok and "맞았습니다" in ok


if __name__ == "__main__":
    test_l2_checkpoint()
    test_l3_checkpoint()
    print("OK l2_l3_checkpoint_quiz", "l2", len(L2), "l3", len(L3))
