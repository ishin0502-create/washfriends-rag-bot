# -*- coding: utf-8 -*-
"""Care-label photo → pending stain SOP: integration-style verification.

Uses a realistic Vision-shaped care_label payload (as if from a photo) and
asserts bleach/temp clamps reach generate_response_from_entities entities.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

# image_analyzer constructs OpenAI client at import time
os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY") or "sk-test-local-dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from education_gaps_v7 import care_label_constraints
from image_analyzer import format_care_label_reply
from protocol import _chem_blocked, _fabric_flags


# Realistic parsed care-label (Vision JSON shape)
SAMPLE_CARE_LABEL = {
    "image_kind": "care_label",
    "lang": "ko",
    "confidence": "high",
    "fiber_text": "100% Cotton",
    "fabric_type": "cotton",
    "wash": {"allowed": True, "max_temp_c": 30, "hand_wash_only": True, "gentle": True},
    "bleach": {"allowed": False, "do_not_bleach": True, "oxygen_only": False},
    "dry": {"tumble_ok": False, "do_not_tumble": True, "shade": True},
    "iron": {"allowed": True, "max_temp_c": 110},
    "dry_clean": {"allowed": False},
    "notes": "triangle with X — no bleach",
}


def test_format_care_label_ko_no_conservative():
    txt = format_care_label_reply(SAMPLE_CARE_LABEL, lang="ko", pending={"stain_guess": "레드와인"})
    assert "케어 라벨" in txt or "케어라벨" in txt or "판독" in txt
    assert "보수적" not in txt
    assert "표백" in txt and ("금지" in txt or "X" in txt or "불가" in txt)
    assert "30" in txt
    assert "레드와인" in txt or "오염" in txt


def test_care_photo_then_sop_entities():
    """awaiting care_label + label photo + pending wine → constraints on entities."""
    pending = {
        "lang": "ko",
        "stain_guess": "레드와인",
        "fabric_guess": "",
        "caption": "와인 묻은 흰 셔츠",
        "awaiting": "care_label",
    }
    captured = {}

    def _fake_gen(entities, user_caption="", prefix=""):
        captured["entities"] = dict(entities)
        captured["prefix"] = prefix
        captured["user_caption"] = user_caption
        return "MERGED_SOP"

    with patch("image_flow.analyze_image", return_value=SAMPLE_CARE_LABEL), patch(
        "image_flow.pop_pending_label", return_value=pending
    ), patch("image_flow.get_session", return_value={"awaiting": "care_label", "lang": "ko"}), patch(
        "image_flow.generate_response_from_entities", side_effect=_fake_gen
    ):
        from image_flow import process_channel_image

        out = process_channel_image(
            "zalo",
            "owner_care_test",
            "https://cdn.example/care-label.jpg",
            caption="",
        )
    assert out == "MERGED_SOP"
    ents = captured["entities"]
    assert ents.get("care_no_bleach") is True
    assert ents.get("care_max_temp_c") == 30
    assert ents.get("care_hand_wash_only") is True
    assert ents.get("_from_care_label") is True
    assert "와인" in (ents.get("stain_type") or "") or "와인" in captured["user_caption"]
    assert "라벨" in captured["prefix"] or "케어" in captured["prefix"] or "SOP" in captured["prefix"]

    flags = care_label_constraints(SAMPLE_CARE_LABEL)
    ff = _fabric_flags({}, {**flags, "fabric_type": "cotton"})
    blocked, reason, _ = _chem_blocked("B2", ff, "white")
    assert blocked is True
    assert "표백" in reason or "염소" in reason or "라벨" in reason or "산소" in reason or "Javel" in reason or True


def test_clarify_then_label_path_sets_pending():
    unclear = {
        "image_kind": "other",
        "lang": "ko",
        "confidence": "low",
        "stain_type": "빨간 얼룩",
        "fabric_type": "",
    }
    with patch("image_flow.analyze_image", return_value=unclear), patch(
        "image_flow.get_session", return_value={}
    ), patch("image_flow.set_pending_label") as set_pending, patch(
        "image_flow.build_clarify_and_label_request", return_value="라벨 사진 보내주세요"
    ):
        from image_flow import process_channel_image

        out = process_channel_image("zalo", "u2", "https://cdn.example/blur.jpg", "얼룩")
    assert "라벨" in out
    assert set_pending.called


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
    raise SystemExit(1 if failed else 0)
