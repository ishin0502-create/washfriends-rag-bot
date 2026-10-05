# -*- coding: utf-8 -*-
"""Exam VI/EN copy + fail guidance."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from l1_exam_bank import L1_BANK_KO, sample_l1_exam_questions
from l2_exam_bank import L2_BANK_KO, sample_l2_exam_questions
from l3_exam_bank import L3_BANK_KO, sample_l3_exam_questions
from exam_i18n import TEXTS
from weekly_exam import _finish_message

_HANGUL = re.compile(r"[\uac00-\ud7a3]")


def test_i18n_covers_all_bank_ids():
    ids = {it["id"] for it in L1_BANK_KO + L2_BANK_KO + L3_BANK_KO}
    missing = ids - set(TEXTS)
    extra = set(TEXTS) - ids
    assert not missing, missing
    assert not extra, extra


def test_vi_en_question_bodies():
    for sampler, src in (
        (sample_l1_exam_questions, "l1_bank"),
        (sample_l2_exam_questions, "l2_bank"),
        (sample_l3_exam_questions, "l3_bank"),
    ):
        for lang in ("vi", "en"):
            items = sampler(n=8, lang=lang, rng=__import__("random").Random(7))
            assert items
            for it in items:
                head = it["q"].split("\n")[0]
                assert not _HANGUL.search(head), (src, lang, it["id"], head)
                assert it["explain"]
                assert not _HANGUL.search(it["explain"]), (it["id"], it["explain"])
                assert it["source"] == src
                assert it["lang"] == lang


def test_fail_copy_points_to_course():
    part = {
        "score": 3,
        "max_score": 7,
        "questions_json": [{"source": "l1_bank", "correct": False, "explain": "cold water"}],
    }
    ko = _finish_message(part, "ko")
    vi = _finish_message(part, "vi")
    en = _finish_message(part, "en")
    assert "미합격" in ko and "교육" in ko
    assert "CHƯA ĐẠT" in vi and "khóa L1" in vi
    assert "NOT YET" in en and "L1 course" in en
    l3 = {"score": 2, "max_score": 7, "questions_json": [{"source": "l3_bank"}]}
    assert "cao cấp" in _finish_message(l3, "vi")
    assert "advanced" in _finish_message(l3, "en")


if __name__ == "__main__":
    test_i18n_covers_all_bank_ids()
    test_vi_en_question_bodies()
    test_fail_copy_points_to_course()
    print("ok")
