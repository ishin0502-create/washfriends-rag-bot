# -*- coding: utf-8 -*-
"""Tests for ISO care-label KB + dry-clean capability messaging + CTA."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY") or "sk-test-local-dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from care_label_iso3758 import (
    SYMBOLS,
    infer_symbol_ids_from_label,
    needs_professional_care,
    wet_action_lines,
)
from dry_clean_capability import lock_message, unlock_message, append_capability_block
from education_label_enrich import enrich_owner_answer, should_append_label_cta, label_photo_cta
from image_analyzer import format_care_label_reply


def test_symbols_count_32():
    assert len(SYMBOLS) == 32


def test_infer_hand_wash_no_bleach_no_tumble():
    label = {
        "wash": {"allowed": True, "hand_wash_only": True, "max_temp_c": 40},
        "bleach": {"do_not_bleach": True},
        "dry": {"do_not_tumble": True},
        "iron": {"allowed": True, "max_temp_c": 110},
        "dry_clean": {"allowed": False},
    }
    ids = infer_symbol_ids_from_label(label)
    assert 26 in ids  # hand wash
    assert 2 in ids  # no bleach
    assert 8 in ids or 18 in ids or 28 in ids
    assert 12 in ids  # iron low
    acts = wet_action_lines(label, lang="ko")
    assert acts
    assert any("손세탁" in a or "기계 금지" in a for a in acts)


def test_pro_label_needs_professional():
    label = {
        "wash": {"do_not_wash": True},
        "bleach": {"do_not_bleach": True},
        "dry": {"do_not_tumble": True},
        "iron": {"do_not_iron": True},
        "dry_clean": {"allowed": True, "code": "P"},
    }
    assert needs_professional_care(label) is True


def test_format_reply_lock_when_no_machine():
    label = {
        "image_kind": "care_label",
        "lang": "ko",
        "confidence": "high",
        "fiber_text": "100% Wool",
        "wash": {"do_not_wash": True},
        "bleach": {"do_not_bleach": True},
        "dry": {"do_not_tumble": True},
        "iron": {"allowed": False, "do_not_iron": True},
        "dry_clean": {"allowed": True, "code": "P"},
    }
    txt = format_care_label_reply(label, lang="ko", dry_clean_machine=False)
    assert "교육 잠금" in txt
    assert "본사" in txt
    assert "구비" in txt or "확인" in txt
    assert "PROG" not in txt or "임의" in unlock_message("ko")  # lock has no fake PROG


def test_format_reply_unlock_when_machine():
    label = {
        "wash": {"do_not_wash": True},
        "bleach": {"do_not_bleach": True},
        "dry": {"do_not_tumble": True},
        "iron": {},
        "dry_clean": {"allowed": True, "code": "P"},
    }
    txt = format_care_label_reply(label, lang="ko", dry_clean_machine=True)
    assert "교육 해금" in txt
    assert "P" in txt


def test_lock_unlock_messages():
    assert "교육 잠금" in lock_message("ko")
    assert "교육 해금" in unlock_message("ko", code="P")
    assert "đào tạo khóa" in lock_message("vi").lower() or "khóa" in lock_message("vi")


def test_cta_for_silk():
    assert should_append_label_cta("실크에 커피 묻었어요", "SOP 본문입니다", {"stain_type": "coffee"})
    assert "라벨" in label_photo_cta("ko")
    out = enrich_owner_answer(
        "실크는 손세탁입니다.",
        user_message="실크 얼룩",
        lang="ko",
        user_id="",
        entities={"stain_type": "coffee", "fabric_type": "silk"},
    )
    assert "라벨" in out


def test_dry_topic_gets_lock_without_machine():
    with patch("education_label_enrich.resolve_has_machine", return_value=False, create=True), patch(
        "dry_clean_capability.resolve_has_machine", return_value=False
    ):
        out = enrich_owner_answer(
            "라벨에 물세탁 금지가 있으면 드라이 기준입니다.",
            user_message="드라이클리닝 어떻게 해요?",
            lang="ko",
            user_id="u1",
            entities={"item_id": "I_DRY_VS_WET"},
        )
    assert "교육 잠금" in out
    assert "본사" in out


def test_unlock_includes_symbol_guide():
    u = unlock_message("ko", code="P")
    assert "교육 해금" in u
    assert "P =" in u or "P=" in u
    assert "본사" in u or "매뉴얼" in u


def test_image_flow_uses_dry_flag():
    """Care-label photo path must pass HQ dry-machine flag into formatter."""
    label = {
        "image_kind": "care_label",
        "lang": "ko",
        "confidence": "high",
        "wash": {"do_not_wash": True},
        "bleach": {"do_not_bleach": True},
        "dry": {"do_not_tumble": True},
        "iron": {},
        "dry_clean": {"allowed": True, "code": "P"},
    }
    captured = {}

    def _fmt(result, lang="vi", pending=None, dry_clean_machine=None):
        captured["dry"] = dry_clean_machine
        return f"FMT dry={dry_clean_machine}"

    with patch("image_flow.analyze_image", return_value=label), patch(
        "image_flow.get_session", return_value={}
    ), patch("image_flow._dry_machine_flag", return_value=True), patch(
        "image_flow.format_care_label_reply", side_effect=_fmt
    ):
        from image_flow import process_channel_image

        out = process_channel_image("zalo", "owner1", "https://cdn.example/l.jpg", "")
    assert captured.get("dry") is True
    assert "dry=True" in out

    with patch("image_flow.analyze_image", return_value=label), patch(
        "image_flow.get_session", return_value={}
    ), patch("image_flow._dry_machine_flag", return_value=False), patch(
        "image_flow.format_care_label_reply", side_effect=_fmt
    ):
        out2 = process_channel_image("zalo", "owner1", "https://cdn.example/l.jpg", "")
    assert "dry=False" in out2


def test_append_capability_idempotent():
    base = lock_message("ko")
    again = append_capability_block(base, lang="ko", has_machine=False, force=True)
    assert again.count("교육 잠금") == 1


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
