# -*- coding: utf-8 -*-
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["WF_OWNER_QA_DIR"] = str(Path(tempfile.mkdtemp()) / "owner_qa")

from photo_task import (
    pending_photo_task,
    photo_task_counts,
    try_handle_photo_task_image,
    try_handle_photo_task_text,
)
from learning_mode import try_handle_mode_or_quiz


def test_commands_and_no_stain_steal():
    uid = "u-photo-1"
    assert try_handle_photo_task_text(uid, "피 얼룩 어떻게 빼요?") is None
    r = try_handle_photo_task_text(uid, "사진과제")
    assert r and "케어라벨" in r
    assert pending_photo_task(uid) == "label"
    assert try_handle_photo_task_text(uid, "면 셔츠에 커피 얼룩") is None
    end = try_handle_photo_task_text(uid, "사진과제 끝")
    assert end and "멈췄" in end
    assert pending_photo_task(uid) is None


def test_label_pass_then_intake(monkey=None):
    uid = "u-photo-2"
    try_handle_photo_task_text(uid, "사진과제")
    with patch(
        "photo_task._classify_photo",
        return_value={"image_kind": "care_label", "confidence": "high"},
    ):
        r = try_handle_photo_task_image(uid, "https://cdn.example/l.jpg", "")
    assert r and "통과" in r
    assert pending_photo_task(uid) == "intake_label"
    n, total = photo_task_counts(uid)
    assert n == 1 and total == 2
    with patch(
        "photo_task._classify_photo",
        return_value={"image_kind": "stain_photo", "confidence": "high"},
    ):
        bad = try_handle_photo_task_image(uid, "https://cdn.example/s.jpg", "")
    assert "아닙니다" in bad
    assert pending_photo_task(uid) == "intake_label"


def test_unsolicited_image_not_consumed():
    uid = "u-photo-3"
    assert try_handle_photo_task_image(uid, "https://cdn.example/x.jpg", "커피") is None
    assert try_handle_mode_or_quiz(uid, "모드") and "사진과제" in try_handle_mode_or_quiz(
        uid, "모드"
    )


if __name__ == "__main__":
    test_commands_and_no_stain_steal()
    test_label_pass_then_intake()
    test_unsolicited_image_not_consumed()
    print("ok")
