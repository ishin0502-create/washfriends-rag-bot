# -*- coding: utf-8 -*-
"""Shared L2/L3 checkpoint quiz helpers (same rules as L1)."""
from __future__ import annotations

import re
from typing import Any, Callable, Optional

from exam_i18n import localized_bank_item
from learning_quiz import _match_accept
from reply_lang import detect_reply_lang

_LETTER = re.compile(r"^([A-D])[\.\)\:\s]?", re.I)


def quiz_prompt(qid: str, lang: str, *, find_item: Callable[[str], Optional[dict]], source: str) -> str:
    it = find_item(qid)
    loc = localized_bank_item(it or {"id": qid, "q": qid}, lang, source) if it else {"q": qid}
    q = str(loc.get("q") or qid)
    choices = loc.get("choices") or []
    if isinstance(choices, list) and choices:
        q = q + "\n" + "\n".join(str(x) for x in choices)
    if lang == "en":
        return (
            "◆ Checkpoint (1 question)\n"
            "「next」 does not skip this. For a real stain, send the stain question.\n\n"
            f"{q}"
        )
    if lang == "vi":
        return (
            "◆ Câu hỏi chốt (1 câu)\n"
            "「tiếp」 không bỏ qua. Vết bẩn gấp: gửi câu hỏi vết bẩn.\n\n"
            f"{q}"
        )
    return (
        "◆ 확인 문제 (1문항)\n"
        "맞히기 전에는 「다음」으로 넘어가지 않습니다.\n"
        "지금 얼룩이 급하면, 얼룩 질문을 그냥 보내 주세요. (이 문제는 나중에)\n\n"
        f"{q}"
    )


def quiz_explain(qid: str, lang: str, *, find_item: Callable[[str], Optional[dict]], source: str) -> str:
    it = find_item(qid)
    if not it:
        return ""
    loc = localized_bank_item(it, lang, source)
    return str(loc.get("explain") or it.get("explain") or "")


def grade_checkpoint(
    qid: str,
    raw: str,
    lang: str,
    *,
    find_item: Callable[[str], Optional[dict]],
    source: str,
) -> bool:
    it = find_item(qid)
    if not it:
        return False
    loc = localized_bank_item(it, lang, source)
    if _match_accept(raw, str(loc.get("accept") or it.get("accept") or "")):
        return True
    letter = str(loc.get("answer") or "").strip().upper()[:1]
    if letter not in "ABCD":
        return False
    u = (raw or "").strip().upper()
    if u == letter:
        return True
    m = _LETTER.match(u)
    return bool(m and m.group(1).upper() == letter)


def pass_message(lang: str, explain: str, nxt: str) -> str:
    if lang == "en":
        return f"◆ Correct.\n{explain}\n\n{nxt}"
    if lang == "vi":
        return f"◆ Đúng.\n{explain}\n\n{nxt}"
    return f"◆ 맞았습니다.\n{explain}\n\n{nxt}"


def fail_message(lang: str, explain: str, again: str) -> str:
    if lang == "en":
        return f"◆ Not yet.\n{explain}\n\n{again}"
    if lang == "vi":
        return f"◆ Chưa đúng.\n{explain}\n\n{again}"
    return f"◆ 아직 아닙니다.\n{explain}\n\n다시:\n{again}"
