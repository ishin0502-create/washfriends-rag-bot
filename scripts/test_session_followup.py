# -*- coding: utf-8 -*-
"""Multi-turn fabric/weight follow-up must keep stain context."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from graphrag_engine import (
    _looks_like_fabric_weight_followup,
    _message_has_new_stain_topic,
)
from user_session import clear_session, get_session, set_pending_treatment


def test_followup_detector():
    assert _looks_like_fabric_weight_followup("보통두께이고 면 입니다")
    assert _looks_like_fabric_weight_followup("면입니다")
    assert not _looks_like_fabric_weight_followup("볼펜 잉크 지우는 법")
    assert _message_has_new_stain_topic("볼펜 잉크")
    assert not _message_has_new_stain_topic("보통두께이고 면 입니다")


def test_pending_treatment_roundtrip():
    clear_session("test", "u1")
    set_pending_treatment(
        "test",
        "u1",
        stain_id="S_INK_PEN",
        stain_type="muc",
        lang="ko",
        raw_question="옷에 묻은 볼펜 잉크자국을 어떻게 지우나요?",
    )
    s = get_session("test", "u1")
    assert s["awaiting"] == "treatment_clarify"
    assert s["stain_id"] == "S_INK_PEN"
    assert _looks_like_fabric_weight_followup("보통두께이고 면 입니다")
    clear_session("test", "u1")


if __name__ == "__main__":
    failed = 0
    for fn in [v for k, v in list(globals().items()) if k.startswith("test_")]:
        try:
            fn()
            print("OK", fn.__name__)
        except Exception as e:
            failed += 1
            print("FAIL", fn.__name__, e)
    raise SystemExit(1 if failed else 0)
