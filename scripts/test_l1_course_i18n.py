# -*- coding: utf-8 -*-
"""L1–L3 course cards are VI/EN in the body, KO unchanged."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from course_i18n import L1_TEXTS, L2_TEXTS, L3_TEXTS
from l1_course import LESSONS as L1, _render_lesson as r1
from l2_course import LESSONS as L2, _render_lesson as r2
from l3_course import LESSONS as L3, _render_lesson as r3

_HANGUL = re.compile(r"[\uac00-\ud7a3]")


def _check_bank(lessons, texts, render, tag):
    ids = {it["id"] for it in lessons}
    assert ids == set(texts), (tag, ids - set(texts), set(texts) - ids)
    for lid, t in texts.items():
        for k in ("title_vi", "body_vi", "title_en", "body_en"):
            assert t.get(k, "").strip(), (tag, lid, k)
    for i, les in enumerate(lessons):
        vi = render(i, "vi", done_n=i)
        en = render(i, "en", done_n=i)
        assert not _HANGUL.search(vi), (tag, les["id"], vi)
        assert not _HANGUL.search(en), (tag, les["id"], en)
        assert les["title"] not in vi
        assert tag[:3] in vi  # [L1 / [L2 / [L3


def test_all_levels():
    _check_bank(L1, L1_TEXTS, r1, "[L1]")
    _check_bank(L2, L2_TEXTS, r2, "[L2]")
    _check_bank(L3, L3_TEXTS, r3, "[L3]")
    assert "섬유 라벨" in r1(0, "ko", done_n=0)
    assert "면·린넨" in r2(0, "ko", done_n=0)
    assert "1차 실패" in r3(0, "ko", done_n=0)


if __name__ == "__main__":
    test_all_levels()
    print("ok")
