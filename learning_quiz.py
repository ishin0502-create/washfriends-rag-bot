# -*- coding: utf-8 -*-
"""Learning-mode quiz — personal cards first, OPS drills fallback. No LLM."""
from __future__ import annotations

import re
from typing import Any, Optional

from owner_qa_log import get_quiz, list_personal_cards, set_quiz
from reply_lang import detect_reply_lang


def _parse_ops_stain_cards(lang: str) -> list[dict[str, str]]:
    try:
        from education_gaps_v7 import OPS_DRILLS_V7
    except Exception:
        return []
    row = OPS_DRILLS_V7.get("I_QUIZ_STAINS") or {}
    raw = row.get("fresh_path_ko") if lang == "ko" else row.get("fresh_path_vi") or row.get("fresh_path_ko")
    if lang == "en":
        raw = row.get("fresh_path_ko") or ""
    text = raw or ""
    cards: list[dict[str, str]] = []
    # (1)Q1: ... → 정답: ...
    for m in re.finditer(
        r"\(\d\)\s*Q?\d*\s*[:：]?\s*(.+?)\s*→\s*(?:정답|đáp)?\s*[:：]?\s*(.+?)(?=\(\d\)|$)",
        text,
        re.I | re.S,
    ):
        q = re.sub(r"\s+", " ", m.group(1)).strip()
        ans = re.sub(r"\s+", " ", m.group(2)).strip()
        if len(q) < 6 or len(ans) < 2:
            continue
        # build accept keywords from answer
        keys = [ans]
        for part in re.split(r"[·/,;]|vs", ans):
            p = part.strip()
            if len(p) >= 2:
                keys.append(p)
        accept = "|".join(re.escape(k)[:40] for k in keys[:6] if k)
        if lang == "ko":
            qq = f"{q}\n(짧게 정답만 보내 주세요)"
        elif lang == "en":
            qq = f"{q}\n(short answer)"
        else:
            qq = f"{q}\n(trả lời ngắn)"
        cards.append({"q": qq, "accept": accept or ans[:40], "explain": ans[:300], "lang": lang})
    # VI format without Q labels
    if not cards and lang != "ko":
        for m in re.finditer(
            r"\(\d\)\s*(.+?)\s*→\s*(.+?)(?=\(\d\)|$)",
            text,
            re.S,
        ):
            q = re.sub(r"\s+", " ", m.group(1)).strip()
            ans = re.sub(r"\s+", " ", m.group(2)).strip()
            if len(q) < 6:
                continue
            cards.append(
                {
                    "q": q + ("\n(trả lời ngắn)" if lang != "en" else "\n(short answer)"),
                    "accept": re.escape(ans[:50]),
                    "explain": ans[:300],
                    "lang": lang,
                }
            )
    return cards[:6]


def _parse_ops_fabric_cards(lang: str) -> list[dict[str, str]]:
    try:
        from education_gaps_v7 import OPS_DRILLS_V7
    except Exception:
        return []
    row = OPS_DRILLS_V7.get("I_QUIZ_FABRIC") or {}
    raw = row.get("fresh_path_ko") if lang != "vi" else (row.get("fresh_path_vi") or row.get("fresh_path_ko"))
    text = raw or ""
    cards: list[dict[str, str]] = []
    for m in re.finditer(
        r"\(\d\)\s*Q?\d*\s*[:：]?\s*(.+?)\s*→\s*(?:정답)?\s*[:：]?\s*(.+?)(?=\(\d\)|$)",
        text,
        re.I | re.S,
    ):
        q = re.sub(r"\s+", " ", m.group(1)).strip()
        ans = re.sub(r"\s+", " ", m.group(2)).strip()
        if len(q) < 6:
            continue
        cards.append(
            {
                "q": q + ("\n(짧게 정답)" if lang == "ko" else "\n(short)"),
                "accept": "|".join(
                    re.escape(p.strip())[:40]
                    for p in re.split(r"[·/,;]", ans)
                    if len(p.strip()) >= 2
                )[:200]
                or re.escape(ans[:40]),
                "explain": ans[:300],
                "lang": lang,
            }
        )
    return cards[:6]


def build_deck(user_id: str, lang: str, size: int = 3) -> list[dict[str, str]]:
    """Personal cards first, then OPS stain/fabric drills. Deduped."""
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    deck: list[dict[str, str]] = []
    seen = set()
    for c in list_personal_cards(user_id, limit=40):
        q = c.get("q") or ""
        if q in seen:
            continue
        seen.add(q)
        deck.append(c)
        if len(deck) >= size:
            return deck[:size]
    for c in _parse_ops_stain_cards(lang) + _parse_ops_fabric_cards(lang):
        q = c.get("q") or ""
        if q in seen:
            continue
        seen.add(q)
        deck.append(c)
        if len(deck) >= size:
            break
    return deck[:size]


def start_quiz(user_id: str, lang: str = "ko", size: int = 3) -> str:
    deck = build_deck(user_id, lang, size=size)
    if not deck:
        if lang == "ko":
            return (
                "◆ 학습 모드\n"
                "아직 복습 카드가 없습니다.\n"
                "현장 모드에서 질문 2~3개 하신 뒤 「복습」을 보내 주세요.\n"
                "(또는 「현장」으로 바로 질문)"
            )
        if lang == "en":
            return (
                "◆ Learning mode\n"
                "No review cards yet. Ask 2–3 questions in field mode, then send 「review」."
            )
        return (
            "◆ Chế độ học\n"
            "Chưa có thẻ ôn. Hỏi 2–3 câu ở chế độ hiện trường, rồi gửi 「ôn」."
        )
    personal_n = len(list_personal_cards(user_id, limit=40))
    set_quiz(
        user_id,
        {
            "items": deck,
            "index": 0,
            "correct": 0,
            "wrong": 0,
            "lang": lang,
            "source": "personal" if personal_n else "ops",
        },
    )
    return _render_question(user_id, intro=True)


def _render_question(user_id: str, *, intro: bool = False, feedback: str = "") -> str:
    quiz = get_quiz(user_id) or {}
    items = quiz.get("items") or []
    idx = int(quiz.get("index") or 0)
    lang = quiz.get("lang") or "ko"
    if idx >= len(items):
        return _finish(user_id)
    item = items[idx]
    n = idx + 1
    total = len(items)
    src = quiz.get("source") or ""
    if lang == "ko":
        head = "◆ 학습 복습" if intro else "◆ 다음"
        src_line = (
            "· 출처: 회원님이 물은 내용 위주\n"
            if src == "personal"
            else (
                "· 출처: 세탁표시 기호 (그림 객관식·주관식)\n"
                if src == "care_symbols"
                else "· 출처: 기본 얼룩·원단 드릴 (개인 기록 부족 시)\n"
            )
        )
        body = (
            f"{head} ({n}/{total})\n"
            f"{src_line if intro else ''}"
            f"{feedback}"
            f"{item.get('q')}\n\n"
            "답만 보내 주세요. 그만: 「현장」 / 메뉴: 「모드」"
        )
    elif lang == "en":
        body = (
            f"{'◆ Learning review' if intro else '◆ Next'} ({n}/{total})\n"
            f"{feedback}{item.get('q')}\n\n"
            "Send answer only. Stop: 「field」 / Menu: 「mode」"
        )
    else:
        body = (
            f"{'◆ Ôn tập' if intro else '◆ Tiếp'} ({n}/{total})\n"
            f"{feedback}{item.get('q')}\n\n"
            "Chỉ gửi đáp. Dừng: 「hiện trường」 / Menu: 「mode」"
        )
    return body


def _finish(user_id: str) -> str:
    quiz = get_quiz(user_id) or {}
    ok = int(quiz.get("correct") or 0)
    bad = int(quiz.get("wrong") or 0)
    total = ok + bad
    lang = quiz.get("lang") or "ko"
    set_quiz(user_id, None)
    if lang == "ko":
        return (
            f"◆ 복습 완료 ({ok}/{total} 맞음)\n"
            "이제 학습 모드에서 질문을 보내셔도 됩니다.\n"
            "급하면 「현장」— 막히지 않고 바로 답합니다.\n"
            "다시 복습: 「복습」"
        )
    if lang == "en":
        return (
            f"◆ Review done ({ok}/{total} correct)\n"
            "You can ask freely in learning mode.\n"
            "Urgent: 「field」. Again: 「review」"
        )
    return (
        f"◆ Xong ôn ({ok}/{total} đúng)\n"
        "Có thể hỏi tiếp. Gấp: 「hiện trường」. Ôn lại: 「ôn」"
    )


def grade_answer(user_id: str, text: str) -> Optional[str]:
    """If a quiz is active, grade and advance. Else None."""
    quiz = get_quiz(user_id)
    if not quiz or not quiz.get("items"):
        return None
    items = quiz["items"]
    idx = int(quiz.get("index") or 0)
    if idx >= len(items):
        return _finish(user_id)
    item = items[idx]
    lang = quiz.get("lang") or detect_reply_lang(text or "")
    raw = (text or "").strip()
    accept = item.get("accept") or ""
    ok = _match_accept(raw, accept)
    if ok:
        quiz["correct"] = int(quiz.get("correct") or 0) + 1
        if lang == "ko":
            fb = f"○ 맞습니다.\n· {item.get('explain') or ''}\n\n"
        elif lang == "en":
            fb = f"○ Correct.\n· {item.get('explain') or ''}\n\n"
        else:
            fb = f"○ Đúng.\n· {item.get('explain') or ''}\n\n"
    else:
        quiz["wrong"] = int(quiz.get("wrong") or 0) + 1
        if lang == "ko":
            fb = f"× 아쉽습니다.\n· 정답 요지: {item.get('explain') or accept}\n\n"
        elif lang == "en":
            fb = f"× Not quite.\n· Key: {item.get('explain') or accept}\n\n"
        else:
            fb = f"× Chưa đúng.\n· Ý: {item.get('explain') or accept}\n\n"
    quiz["index"] = idx + 1
    set_quiz(user_id, quiz)
    if quiz["index"] >= len(items):
        return fb + _finish(user_id)
    return _render_question(user_id, intro=False, feedback=fb)


def _match_accept(user_text: str, accept: str) -> bool:
    t = (user_text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    if not t:
        return False
    # O/X shortcuts
    if re.fullmatch(r"[oｏㅇoxｘ×]|맞음?|틀림?|true|false|yes|no|đúng|sai", t, re.I):
        if re.fullmatch(r"[oｏㅇ]|맞음?|true|yes|đúng", t, re.I):
            return bool(re.search(r"(^|[|])(o|ㅇ|맞|true|yes|đúng|dung|y|1)([|]|$)", accept, re.I))
        return bool(re.search(r"(^|[|])(x|틀|false|no|sai)([|]|$)", accept, re.I))
    for part in accept.split("|"):
        p = part.strip()
        if not p:
            continue
        try:
            if re.search(p, t, re.I):
                return True
        except re.error:
            if p.lower() in t:
                return True
    # letter choice A/B/C
    if re.fullmatch(r"[abc123]", t):
        return bool(re.search(rf"(^|[|]){re.escape(t)}([|]|$)", accept, re.I))
    return False
