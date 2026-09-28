# -*- coding: utf-8 -*-
"""Care-label symbol quiz (MCQ + open-ended) using SVG/PNG assets. No LLM."""
from __future__ import annotations

import random
import re
from typing import Any, Optional

from care_label_iso3758 import SYMBOLS, name_for
from care_symbol_svg import asset_paths, ensure_assets


def _wrong_names(correct_id: int, lang: str, k: int = 2) -> list[str]:
    same_cat = [
        sid for sid, row in SYMBOLS.items()
        if sid != correct_id and row.get("cat") == (SYMBOLS.get(correct_id) or {}).get("cat")
    ]
    others = [sid for sid in SYMBOLS if sid != correct_id]
    pool = same_cat if len(same_cat) >= k else others
    random.shuffle(pool)
    names: list[str] = []
    for sid in pool:
        n = name_for(sid, lang)
        if n and n not in names and n != name_for(correct_id, lang):
            names.append(n)
        if len(names) >= k:
            break
    while len(names) < k:
        names.append("—" if lang == "ko" else "—")
    return names[:k]


def build_mcq_item(symbol_id: int, lang: str = "ko") -> dict[str, Any]:
    ensure_assets()
    svg_p, png_p = asset_paths(symbol_id)
    correct = name_for(symbol_id, lang)
    wrong = _wrong_names(symbol_id, lang, 2)
    choices = [correct] + wrong
    random.shuffle(choices)
    ans_idx = choices.index(correct)  # 0,1,2
    letters = ["1", "2", "3"]
    if lang == "ko":
        q = (
            "이 세탁 표시 기호는 무슨 뜻인가요?\n"
            + "\n".join(f"{i + 1}) {c}" for i, c in enumerate(choices))
            + "\n\n번호(1·2·3) 또는 뜻을 보내 주세요."
        )
    elif lang == "en":
        q = (
            "What does this care-label symbol mean?\n"
            + "\n".join(f"{i + 1}) {c}" for i, c in enumerate(choices))
            + "\n\nSend 1 / 2 / 3 or the meaning."
        )
    else:
        q = (
            "Ký hiệu giặt này nghĩa là gì?\n"
            + "\n".join(f"{i + 1}) {c}" for i, c in enumerate(choices))
            + "\n\nGửi 1 / 2 / 3 hoặc nghĩa."
        )
    # accept: index number, letter, and meaning keywords
    accept_parts = [
        letters[ans_idx],
        re.escape(correct),
    ]
    for part in re.split(r"[·/,;(]", correct):
        p = part.strip()
        if len(p) >= 2:
            accept_parts.append(re.escape(p[:40]))
    return {
        "q": q,
        "accept": "|".join(accept_parts),
        "explain": correct,
        "lang": lang,
        "kind": "mcq",
        "symbol_id": symbol_id,
        "image_path": str(png_p),
        "svg_path": str(svg_p),
        "choices": choices,
        "answer_index": ans_idx,
    }


def build_open_item(symbol_id: int, lang: str = "ko") -> dict[str, Any]:
    ensure_assets()
    svg_p, png_p = asset_paths(symbol_id)
    correct = name_for(symbol_id, lang)
    row = SYMBOLS.get(symbol_id) or {}
    if lang == "ko":
        q = (
            "이 기호의 뜻을 짧게 적어 주세요.\n"
            "(예: 물세탁 금지 / 표백 금지 / 40°C 세탁 …)"
        )
    elif lang == "en":
        q = "Write briefly what this care symbol means."
    else:
        q = "Viết ngắn nghĩa của ký hiệu này."
    keys = [re.escape(correct)]
    for lang_key in ("ko", "en", "vi"):
        n = str(row.get(lang_key) or "")
        if n:
            keys.append(re.escape(n))
            for part in re.split(r"[·/,;(°℃]", n):
                p = part.strip()
                if len(p) >= 2:
                    keys.append(re.escape(p[:40]))
    # useful shortcuts by category
    cat = row.get("cat")
    hint = str(row.get("hint") or "")
    if "X" in hint or "crossed" in hint or symbol_id in {2, 8, 9, 17, 25}:
        if lang == "ko":
            keys.extend(["금지", "하지\\s*마", "안\\s*됨", "불가"])
        elif lang == "vi":
            keys.extend(["cấm", "không\\s*được", "khong\\s*duoc"])
        else:
            keys.extend(["do\\s*not", "no\\s+", "forbid"])
    if cat == "wash" and "40" in hint:
        keys.append("40")
    if cat == "wash" and "30" in hint:
        keys.append("30")
    return {
        "q": q,
        "accept": "|".join(dict.fromkeys(keys)),  # dedupe preserve order
        "explain": correct,
        "lang": lang,
        "kind": "open",
        "symbol_id": symbol_id,
        "image_path": str(png_p),
        "svg_path": str(svg_p),
    }


def build_care_symbol_deck(
    lang: str = "ko",
    size: int = 6,
    *,
    mix: str = "mixed",  # mixed | mcq | open
    prefer_high_freq: bool = True,
) -> list[dict[str, Any]]:
    """Build a quiz deck mixing MCQ and open-ended symbol questions."""
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    ensure_assets()
    ids = list(SYMBOLS.keys())
    if prefer_high_freq:
        high = [i for i in ids if (SYMBOLS[i].get("freq") == "high")]
        med = [i for i in ids if (SYMBOLS[i].get("freq") == "med")]
        random.shuffle(high)
        random.shuffle(med)
        ordered = high + med + [i for i in ids if i not in high and i not in med]
    else:
        ordered = ids[:]
        random.shuffle(ordered)

    deck: list[dict[str, Any]] = []
    for i, sid in enumerate(ordered):
        if len(deck) >= size:
            break
        if mix == "mcq":
            deck.append(build_mcq_item(sid, lang))
        elif mix == "open":
            deck.append(build_open_item(sid, lang))
        else:
            deck.append(build_mcq_item(sid, lang) if i % 2 == 0 else build_open_item(sid, lang))
    return deck


def start_care_symbol_quiz(user_id: str, lang: str = "ko", size: int = 6) -> str:
    from learning_quiz import _render_question
    from owner_qa_log import set_quiz

    deck = build_care_symbol_deck(lang=lang, size=size, mix="mixed")
    set_quiz(
        user_id,
        {
            "items": deck,
            "index": 0,
            "correct": 0,
            "wrong": 0,
            "lang": lang,
            "source": "care_symbols",
        },
    )
    # reuse renderer; patch intro text via source line
    body = _render_question(user_id, intro=True)
    if lang == "ko":
        body = body.replace(
            "· 출처: 기본 얼룩·원단 드릴 (개인 기록 부족 시)\n",
            "· 출처: 세탁표시 기호 (그림 → 객관식·주관식)\n",
        ).replace(
            "· 출처: 회원님이 물은 내용 위주\n",
            "· 출처: 세탁표시 기호 (그림 → 객관식·주관식)\n",
        )
        if "세탁표시 기호" not in body:
            body = "◆ 세탁표시 기호 시험\n· 그림이 오면 보고 답하세요.\n\n" + body
    return body


def current_quiz_image_path(user_id: str) -> Optional[str]:
    from owner_qa_log import get_quiz

    quiz = get_quiz(user_id) or {}
    items = quiz.get("items") or []
    idx = int(quiz.get("index") or 0)
    if idx < 0 or idx >= len(items):
        return None
    path = items[idx].get("image_path")
    return str(path) if path else None


# ── Show symbol images on request (not a quiz) ─────────────────────────────

_pending_show: dict[str, list[str]] = {}

_SHOW_CMD = re.compile(
    r"(보여\s*줘|보여줘|보여\s*주|보여\s*달라|이미지|그림|라벨\s*이미지|"
    r"photo|show|ảnh|hien\s*thi|hiển\s*thị)",
    re.I,
)
_DRY_CLEAN_TOPIC = re.compile(
    r"(드라이\s*클?리?닝|드라이클리닝|드라이\s*크리닝|크리닝|클리닝|"
    r"드라이\s*기호|dry\s*-?\s*clean|giặt\s*khô|giat\s*kho|"
    r"원\s*기호|P\s*기호|F\s*기호|웨트\s*클?리?닝|"
    r"전문\s*세탁\s*기호|드라이\s*전용)",
    re.I,
)
_SYMBOL_WORD = re.compile(
    r"(기호|세탁\s*표시|케어\s*라벨|케어라벨|라벨\s*기호|레벨\s*기호|"
    r"care\s*label|ký\s*hiệu|ky\s*hieu|symbol)",
    re.I,
)
_LABEL_SHOW = re.compile(
    r"(세탁\s*기호|케어\s*라벨|라벨\s*기호|레벨\s*기호).{0,12}(보여|이미지|그림)|"
    r"(보여|이미지|그림).{0,12}(세탁\s*기호|케어\s*라벨|라벨\s*기호)",
    re.I,
)


def _dry_clean_symbol_ids() -> list[int]:
    """Main dry-clean / professional circle symbols for display."""
    # P, F, P mild, F mild, W, do-not-dry-clean; plus do-not-wash (often paired)
    return [6, 10, 16, 21, 22, 25, 9]


def match_show_symbol_ids(text: str) -> Optional[list[int]]:
    raw = (text or "").strip()
    if not raw:
        return None
    wants_show = bool(_SHOW_CMD.search(raw))
    about_symbols = bool(_SYMBOL_WORD.search(raw))
    about_dry = bool(_DRY_CLEAN_TOPIC.search(raw))
    # 「드라이클리닝 기호 보여줘」 / 「크리닝 기호 보여줘」 / 「드라이 기호 이미지」
    if about_dry and (wants_show or about_symbols):
        return _dry_clean_symbol_ids()
    # 「세탁 기호 보여줘」 / 「라벨 기호 보여줘」 → dry-clean set (most asked) + note in caption
    if wants_show and about_symbols:
        return _dry_clean_symbol_ids()
    if _LABEL_SHOW.search(raw):
        return _dry_clean_symbol_ids()
    return None


def queue_symbol_images(user_id: str, symbol_ids: list[int]) -> list[str]:
    ensure_assets()
    paths: list[str] = []
    for sid in symbol_ids:
        _, png = asset_paths(sid)
        if png.is_file():
            paths.append(str(png))
    if user_id:
        _pending_show[user_id] = list(paths)
    return paths


def pop_queued_symbol_images(user_id: str) -> list[str]:
    return list(_pending_show.pop(user_id, []) or [])


def format_show_symbols_reply(symbol_ids: list[int], lang: str = "ko") -> str:
    lines: list[str] = []
    if lang == "ko":
        lines.append("◆ 드라이클리닝·전문 세탁 기호")
        lines.append("아래에 그림이 이어집니다. (원 안 글자 = 용제/방식)")
        lines.append("")
        for sid in symbol_ids:
            lines.append(f"· {name_for(sid, 'ko')}")
        lines.append("")
        lines.append("퀴즈로 연습: 「기호퀴즈」")
    elif lang == "en":
        lines.append("◆ Dry-clean / professional care symbols")
        lines.append("Images follow.")
        for sid in symbol_ids:
            lines.append(f"· {name_for(sid, 'en')}")
    else:
        lines.append("◆ Ký hiệu giặt khô / chuyên nghiệp")
        lines.append("Ảnh gửi tiếp theo.")
        for sid in symbol_ids:
            lines.append(f"· {name_for(sid, 'vi')}")
    return "\n".join(lines)


def try_handle_show_symbols(user_id: str, text: str) -> Optional[str]:
    """If user asks to show dry-clean (etc.) symbols, queue PNGs and return caption."""
    ids = match_show_symbol_ids(text or "")
    if not ids:
        return None
    from reply_lang import detect_reply_lang

    lang = detect_reply_lang(text or "")
    queue_symbol_images(user_id, ids)
    return format_show_symbols_reply(ids, lang=lang)
