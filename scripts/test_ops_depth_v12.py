# -*- coding: utf-8 -*-
"""Ops depth v12 — intake dried consent + claim script."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from education_ops_depth_v12 import OPS_DEPTH_V12, education_for_ops_depth
from graphrag_engine import _infer_item_from_text
from specialty_item_care import education_for
from w2_ops_rescue import OPS_DRILLS

_DIA = re.compile(
    r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ]",
    re.I,
)


def test_depth_keys():
    assert "I_INTAKE_SCRIPT" in OPS_DEPTH_V12
    assert "I_CLAIM_SCRIPT" in OPS_DEPTH_V12
    intake = education_for_ops_depth("I_INTAKE_SCRIPT")
    assert "100%" in intake["fresh_path_ko"]
    assert "동의" in intake["fresh_path_ko"] or "동의" in intake["must_include_ko"]
    assert "không 100%" in intake["fresh_path_vi"] or "không 100%" in intake["must_include_vi"]
    assert _DIA.search(intake["why_vi"])


def test_ops_drills_win():
    intake = OPS_DRILLS["I_INTAKE_SCRIPT"]
    claim = OPS_DRILLS["I_CLAIM_SCRIPT"]
    assert "전표" in intake["fresh_path_ko"] and "100%" in intake["fresh_path_ko"]
    assert "접수 사진" in claim["fresh_path_ko"] or "접수 사진" in claim["why_ko"]
    assert "xin lỗi" in claim["fresh_path_vi"].lower() or "Xin lỗi" in claim["fresh_path_vi"]
    assert _DIA.search(claim["why_vi"])
    assert "impulse" in claim["fresh_path_en"].lower() or "100%" in claim["refuse_when_en"]


def test_specialty_education():
    edu = education_for("I_CLAIM_SCRIPT")
    assert edu.get("fresh_path_ko") and edu.get("fresh_path_vi") and edu.get("fresh_path_en")
    assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_vi"])
    blob = " ".join(
        str(edu.get(k) or "")
        for k in ("fresh_path_ko", "refuse_when_ko", "must_include_ko", "why_ko")
    )
    assert "100%" in blob
    assert "사과" in blob or "보상" in blob


def test_infer_claim_intake():
    assert _infer_item_from_text("클레임 대응 스크립트") == "I_CLAIM_SCRIPT"
    assert _infer_item_from_text("손님 항의 보상 어떻게") == "I_CLAIM_SCRIPT"
    assert _infer_item_from_text("접수 때 마른 얼룩 고지") == "I_INTAKE_SCRIPT"
    assert _infer_item_from_text("khiếu nại khách") == "I_CLAIM_SCRIPT"
