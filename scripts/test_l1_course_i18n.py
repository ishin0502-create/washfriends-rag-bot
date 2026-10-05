# -*- coding: utf-8 -*-
"""L1 course cards are VI/EN in the body, KO unchanged."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from course_i18n import L1_TEXTS
from l1_course import LESSONS, _render_lesson

_HANGUL = re.compile(r"[\uac00-\ud7a3]")


def test_every_l1_id_has_vi_en():
    ids = {it["id"] for it in LESSONS}
    assert ids == set(L1_TEXTS), (ids - set(L1_TEXTS), set(L1_TEXTS) - ids)
    for lid, t in L1_TEXTS.items():
        for k in ("title_vi", "body_vi", "title_en", "body_en"):
            assert t.get(k, "").strip(), (lid, k)


def test_vi_en_render_has_no_hangul():
    for i, les in enumerate(LESSONS):
        vi = _render_lesson(i, "vi", done_n=i)
        en = _render_lesson(i, "en", done_n=i)
        assert not _HANGUL.search(vi), (les["id"], vi)
        assert not _HANGUL.search(en), (les["id"], en)
        assert les["title"] not in vi
        assert "[L1]" in vi or "[L1→L3]" in vi or "[L1→L2]" in vi


def test_ko_render_unchanged_uses_bank():
    msg = _render_lesson(0, "ko", done_n=0)
    assert "섬유 라벨" in msg
    assert "삼각형" in msg
    assert "Bài cơ bản" not in msg


if __name__ == "__main__":
    test_every_l1_id_has_vi_en()
    test_vi_en_render_has_no_hangul()
    test_ko_render_unchanged_uses_bank()
    print("ok")
