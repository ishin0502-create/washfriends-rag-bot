# -*- coding: utf-8 -*-
"""Per-owner education Q&A ring log — disk-backed, no LLM.

Stores recent turns + lightweight quiz cards extracted heuristically
from answers already given (zero extra model cost).
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Any, Optional

_LOCK = threading.Lock()
_MAX_TURNS = 80
_MAX_AGE_SEC = 90 * 24 * 3600
_A_SNIP = 900


def _data_dir() -> Path:
    return Path(
        os.environ.get("WF_OWNER_QA_DIR")
        or (Path(__file__).resolve().parent / "data" / "owner_qa")
    )


def _user_path(user_id: str) -> Path:
    safe = re.sub(r"[^\w\-]", "_", (user_id or "").strip())[:80] or "unknown"
    return _data_dir() / f"{safe}.json"


def _empty() -> dict[str, Any]:
    return {"mode": "field", "updated_at": time.time(), "turns": [], "quiz": None}


def load_user(user_id: str) -> dict[str, Any]:
    if not (user_id or "").strip():
        return _empty()
    path = _user_path(user_id)
    with _LOCK:
        if not path.exists():
            return _empty()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return _empty()
            data.setdefault("mode", "field")
            data.setdefault("turns", [])
            data.setdefault("quiz", None)
            return data
        except Exception:
            return _empty()


def save_user(user_id: str, data: dict[str, Any]) -> None:
    if not (user_id or "").strip():
        return
    data = dict(data)
    data["updated_at"] = time.time()
    # prune turns
    now = time.time()
    turns = [
        t
        for t in (data.get("turns") or [])
        if isinstance(t, dict) and now - float(t.get("ts") or 0) <= _MAX_AGE_SEC
    ]
    data["turns"] = turns[-_MAX_TURNS:]
    path = _user_path(user_id)
    tmp = path.with_suffix(".tmp")
    with _LOCK:
        _data_dir().mkdir(parents=True, exist_ok=True)
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")
        tmp.replace(path)


def get_mode(user_id: str) -> str:
    m = (load_user(user_id).get("mode") or "field").strip().lower()
    return m if m in {"field", "learning"} else "field"


def set_mode(user_id: str, mode: str) -> str:
    mode = "learning" if str(mode).lower() in {"learning", "learn", "학습"} else "field"
    data = load_user(user_id)
    data["mode"] = mode
    if mode == "field":
        data["quiz"] = None
    save_user(user_id, data)
    return mode


def get_quiz(user_id: str) -> Optional[dict[str, Any]]:
    q = load_user(user_id).get("quiz")
    return q if isinstance(q, dict) else None


def set_quiz(user_id: str, quiz: Optional[dict[str, Any]]) -> None:
    data = load_user(user_id)
    data["quiz"] = quiz
    save_user(user_id, data)


def list_personal_cards(user_id: str, limit: int = 30) -> list[dict[str, str]]:
    """Newest-first quiz cards from this owner's turns."""
    turns = list(reversed(load_user(user_id).get("turns") or []))
    out: list[dict[str, str]] = []
    seen = set()
    for t in turns:
        for c in t.get("cards") or []:
            if not isinstance(c, dict):
                continue
            q = (c.get("q") or "").strip()
            if not q or q in seen:
                continue
            seen.add(q)
            out.append(
                {
                    "q": q,
                    "accept": (c.get("accept") or "").strip(),
                    "explain": (c.get("explain") or "").strip()[:400],
                    "lang": (c.get("lang") or t.get("lang") or "ko"),
                }
            )
            if len(out) >= limit:
                return out
    return out


def _heuristic_cards(question: str, answer: str, lang: str) -> list[dict[str, str]]:
    """Build 0–2 cheap T/F or keyword cards from an already-paid answer. No LLM."""
    a = (answer or "").strip()
    q0 = (question or "").strip()
    if len(a) < 20:
        return []
    cards: list[dict[str, str]] = []
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    blob = f"{q0}\n{a}"

    # Prohibition claims → O/X (mid-string OK)
    ban_m = re.search(
        r"([^.\n]{0,40}(?:금지|하지\s*마|넣지\s*마|CẤM|do not|never)[^.\n]{0,60})",
        a,
        re.I,
    )
    if ban_m:
        claim = re.sub(r"\s+", " ", ban_m.group(1)).strip(" .。·-")
        if len(claim) >= 6:
            if lang == "ko":
                qq = f"맞으면 O, 틀리면 X\n「{claim}」"
            elif lang == "en":
                qq = f"True=O / False=X\n「{claim}」"
            else:
                qq = f"Đúng=O / Sai=X\n「{claim}」"
            cards.append(
                {
                    "q": qq,
                    "accept": r"o|ㅇ|맞|true|yes|đúng|dung|y|1",
                    "explain": claim[:280],
                    "lang": lang,
                }
            )

    # Cold water vs hot for blood/protein hints
    if re.search(r"피|혈액|protein|máu|blood", blob, re.I) and re.search(
        r"찬물|차가운|cold|lạnh|lanh", a, re.I
    ):
        if lang == "ko":
            qq = "신선한 피 얼룩 — 온수로 바로 헹궈도 되나?\nA) 안 됨(찬물)\nB) 온수가 더 좋음"
        elif lang == "en":
            qq = "Fresh blood — rinse with hot water?\nA) No (cold only)\nB) Hot is better"
        else:
            qq = "Máu tươi — xả nước nóng?\nA) Không (chỉ lạnh)\nB) Nóng tốt hơn"
        cards.append(
            {
                "q": qq,
                "accept": r"a|안\s*됨|찬물|no|không|khong|cold|1",
                "explain": "단백질(피)은 온수 고착 → 찬물.",
                "lang": lang,
            }
        )

    # Promise 100%
    if re.search(r"100\s*%|완전\s*제거|hứa\s*100", a, re.I):
        if lang == "ko":
            qq = "고객에게 「100% 제거」를 약속해도 되나?\nA) 안 됨\nB) 됨"
        elif lang == "en":
            qq = "OK to promise 100% stain removal?\nA) No\nB) Yes"
        else:
            qq = "Được hứa tẩy 100%?\nA) Không\nB) Có"
        cards.append(
            {
                "q": qq,
                "accept": r"a|안\s*됨|금지|no|không|khong|1",
                "explain": "100% 약속 금지.",
                "lang": lang,
            }
        )

    # Fallback: ask to recall topic from user question
    if not cards and len(q0) >= 4:
        topic = q0[:80]
        if lang == "ko":
            qq = (
                f"방금 주제 「{topic}」에서 가장 먼저 할 일은?\n"
                f"A) 답변에 나온 1단계·안전 확인\nB) 바로 강한 표백·온수"
            )
        elif lang == "en":
            qq = (
                f"For 「{topic}」, first step is?\n"
                f"A) Follow step 1 / safety in the answer\nB) Jump to strong bleach/hot water"
            )
        else:
            qq = (
                f"Chủ đề 「{topic}」 — bước đầu?\n"
                f"A) Theo bước 1 / an toàn trong câu trả lời\nB) Tẩy mạnh / nước nóng ngay"
            )
        cards.append(
            {
                "q": qq,
                "accept": r"a|1단계|step\s*1|bước\s*1|an toàn|안전|1",
                "explain": (a[:220] + "…") if len(a) > 220 else a,
                "lang": lang,
            }
        )

    return cards[:2]


def append_turn(
    user_id: str,
    *,
    question: str,
    answer: str,
    lang: str = "ko",
    stain_id: str = "",
    bot_mode: str = "",
) -> None:
    if not (user_id or "").strip():
        return
    if not (question or "").strip() or not (answer or "").strip():
        return
    # skip mode/menu noise
    if len(question.strip()) < 2:
        return
    data = load_user(user_id)
    cards = _heuristic_cards(question, answer, lang)
    data.setdefault("turns", []).append(
        {
            "ts": time.time(),
            "q": question.strip()[:500],
            "a": answer.strip()[:_A_SNIP],
            "lang": lang,
            "stain_id": stain_id or "",
            "bot_mode": bot_mode or data.get("mode") or "field",
            "cards": cards,
        }
    )
    save_user(user_id, data)
