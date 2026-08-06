"""
brand_header.py
Messenger-only brand header (mascot + Wash Friends logo).

Isolated from GraphRAG / Neo4j / answer generation.
Fail-open: if anything fails, callers still send the text reply.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Optional

# Separate store — do not share mutations with care-label session
_TTL_SEC = 4 * 60 * 60
_brand: dict[str, dict] = {}

_HEADER_FILE = Path(__file__).resolve().parent / "assets" / "wf_brand_header.png"

# Short clarifications / answers — no brand header
_FOLLOWUP_RE = re.compile(
    r"^("
    r"네|아니요|예|응|어|ㅇㅇ|ㄴㄴ|좋아|싫어|맞아요|아니|"
    r"yes|no|ok|okay|"
    r"\d+\s*(시간|분|일|시간쯤|시간요|h|hr|hrs|min|mins)?|"
    r".{0,8}(시간|분)\s*(전|지났|됐어|되었).{0,12}|"
    r"어제|오늘|방금|금방|방금\s*전|"
    r"면|폴리|실크|울|코튼|데님|"
    r"cotton|silk|wool|poly|"
    r"vâng|không|ok|được|rồi|"
    r".{0,10}(giờ|phút).{0,10}"
    r")$",
    re.IGNORECASE | re.DOTALL,
)

# Lightweight topic tokens (local copy — do not import graphrag)
_TOPIC_TOKENS = [
    "피", "혈액", "커피", "차", "와인", "기름", "오일", "잉크", "볼펜", "매니큐어",
    "땀", "곰팡이", "녹", "진흙", "잔디", "주스", "쥬스", "소스", "케첩", "카레",
    "립스틱", "화장", "소변", "토", "초코", "왁스", "껌", "페인트", "접착",
    "청바지", "데님", "실크", "울", "가죽", "스웨이드", "스니커", "운동화",
    "다운", "패딩", "고어텍스", "정장", "수트", "아오자이", "한복", "골프",
    "색바램", "탈색", "복원", "얼룩", "세탁", "지우", "빼", "제거",
    "blood", "coffee", "wine", "oil", "ink", "juice", "sauce", "denim", "fade",
    "ca phe", "mau", "dau", "muc", "nuoc trai", "quan jean", "phai mau",
]


def header_image_path() -> Optional[Path]:
    if _HEADER_FILE.is_file():
        return _HEADER_FILE
    return None


def public_header_url() -> str:
    """Public URL for Messenger image attachment (FB). Optional override."""
    override = (os.getenv("BRAND_HEADER_IMAGE_URL") or "").strip()
    if override:
        return override
    base = (os.getenv("PUBLIC_BASE_URL") or os.getenv("RAILWAY_PUBLIC_DOMAIN") or "").strip()
    if base and not base.startswith("http"):
        base = "https://" + base
    if not base:
        base = "https://washfriends-rag-bot-production.up.railway.app"
    return base.rstrip("/") + "/static/wf_brand_header.png"


def _key(channel: str, user_id: str) -> str:
    return f"{channel}:{user_id}"


def _prune() -> None:
    now = time.time()
    dead = [k for k, v in _brand.items() if now - float(v.get("ts", 0)) > _TTL_SEC]
    for k in dead:
        del _brand[k]


def _topic_signature(text: str) -> str:
    if not text:
        return ""
    raw = text
    low = text.lower()
    hits = []
    for tok in _TOPIC_TOKENS:
        if any("\uac00" <= c <= "\ud7a3" for c in tok):  # Hangul token
            if tok in raw:
                hits.append(tok)
        else:
            if tok in low or tok in raw:
                hits.append(tok.lower())
    return "|".join(sorted(set(hits)))


def _is_followup_text(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if len(t) <= 24 and _FOLLOWUP_RE.match(t):
        return True
    # Very short numeric / time-only
    if re.fullmatch(r"\d{1,3}", t):
        return True
    return False


def should_send_brand_header(
    channel: str,
    user_id: str,
    user_text: str = "",
    *,
    has_image: bool = False,
    awaiting_care_label: bool = False,
) -> bool:
    """
    True only for the first AI reply of a new laundry topic.
    Follow-ups (time answers, yes/no, care-label photo) → False.
    """
    if awaiting_care_label:
        return False

    _prune()
    text = (user_text or "").strip()
    sig = _topic_signature(text)

    # Pure follow-up with no new topic tokens
    if text and _is_followup_text(text) and not sig:
        return False

    # Image with no caption while mid-topic: still treat as same topic if we have one
    k = _key(channel, user_id)
    prev = _brand.get(k)
    now = time.time()

    if not sig:
        if has_image:
            sig = "image_stain"
        else:
            sig = "general"

    if prev and prev.get("topic") == sig:
        # Same topic — no header
        prev["ts"] = now
        return False

    # New topic (or first message)
    _brand[k] = {"topic": sig, "ts": now, "header_sent": True}
    return True
