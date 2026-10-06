# -*- coding: utf-8 -*-
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["WF_OWNER_QA_DIR"] = str(Path(tempfile.mkdtemp()) / "owner_qa")

from exam_i18n import localized_bank_item
from exam_mcq import EXAM_MCQ
from l1_exam_bank import L1_BANK_KO, sample_l1_exam_questions
from l2_exam_bank import L2_BANK_KO
from l3_exam_bank import L3_BANK_KO
from owner_qa_log import get_exam_retry_ids, merge_exam_retry_ids
from weekly_exam import _grade_exam_answer, _render_q


def test_mcq_covers_banks():
    ids = {it["id"] for it in L1_BANK_KO + L2_BANK_KO + L3_BANK_KO}
    assert ids == set(EXAM_MCQ), (ids - set(EXAM_MCQ), set(EXAM_MCQ) - ids)
    for qid, row in EXAM_MCQ.items():
        assert row["answer"] in "ABCD", qid
        for lang in ("ko", "vi", "en"):
            assert len(row[lang]) == 4, (qid, lang)


def test_letter_grade_and_keyword():
    item = localized_bank_item(L1_BANK_KO[1], "ko", "l1_bank")  # protein
    assert item["answer"] == "B"
    assert _grade_exam_answer("B", item)
    assert _grade_exam_answer("b.", item)
    assert _grade_exam_answer("찬물", item)
    assert not _grade_exam_answer("A", item)
    rendered = _render_q(1, 7, item, "ko")
    assert "A." in rendered and "B. 찬물" in rendered


def test_prefer_failed_ids():
    merge_exam_retry_ids("u-exam", wrong_ids=["l1e_coffee", "l1e_care_x"], correct_ids=[])
    assert "l1e_coffee" in get_exam_retry_ids("u-exam")
    items = sample_l1_exam_questions(n=7, lang="ko", prefer_ids=get_exam_retry_ids("u-exam"))
    assert items[0]["id"] == "l1e_coffee"
    assert items[1]["id"] == "l1e_care_x"
    merge_exam_retry_ids("u-exam", wrong_ids=[], correct_ids=["l1e_coffee"])
    assert "l1e_coffee" not in get_exam_retry_ids("u-exam")


if __name__ == "__main__":
    test_mcq_covers_banks()
    test_letter_grade_and_keyword()
    test_prefer_failed_ids()
    print("ok")
