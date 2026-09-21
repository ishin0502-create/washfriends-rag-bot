# -*- coding: utf-8 -*-
"""Hard stain binds for yellowing vs fresh sweat (no LLM)."""
from __future__ import annotations

import unicodedata
from typing import Optional


def _norm_ascii(text: str) -> str:
    t = unicodedata.normalize("NFD", text or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t.lower()


def bind_sweat_or_yellow_stain(user_message: str, raw_n: Optional[str] = None) -> Optional[str]:
    """Return S_SWEAT_YELLOW / S_SHIRT_YELLOW / S_SWEAT_FRESH or None."""
    msg = user_message or ""
    raw_n = raw_n if raw_n is not None else _norm_ascii(msg)

    if any(k in msg for k in ("겨드랑이", "암내", "누런 겨드랑이")) or "ve o nach" in raw_n or "armpit" in raw_n:
        return "S_SWEAT_YELLOW"

    if (
        (
            "땀" in msg
            or "mo hoi" in raw_n
            or "sweat" in raw_n
            or "겨드랑" in msg
        )
        and any(
            k in msg
            for k in (
                "황변", "누렇", "노랗", "노란", "누래", "누런",
                "오래된", "오래됐", "오래 된", "몇 달", "몇달", "오랫동안", "오래전",
            )
        )
        and not any(
            k in msg for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠")
        )
    ) or (
        ("mo hoi" in raw_n or "sweat" in raw_n)
        and any(k in raw_n for k in ("vang", "yellow", "o vang", "lau ngay", "old sweat", "aged"))
        and "ao so mi" not in raw_n
    ):
        return "S_SWEAT_YELLOW"

    if any(
        k in msg for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠")
    ) and any(
        k in msg
        for k in ("누렇", "황변", "노랗", "누래", "변색", "노란", "누래짐", "누래졌")
    ) and not any(k in msg for k in ("향수", "데오", "데오드란트")):
        return "S_SHIRT_YELLOW"

    if any(k in msg for k in ("누렇게", "황변", "변색", "누래짐")) and any(
        k in msg for k in ("셔츠", "와이", "흰옷", "흰 옷", "흰티", "흰 티")
    ) and not any(k in msg for k in ("향수", "데오", "데오드란트")):
        return "S_SHIRT_YELLOW"

    if any(k in msg for k in ("황변 제거", "황변빼", "황변 빼", "누래짐 제거")) and not any(
        k in msg for k in ("향수", "데오", "데오드란트")
    ):
        return "S_SHIRT_YELLOW"

    if any(k in msg for k in ("땀냄새", "땀 묻", "땀얼룩", "땀 얼룩")) or (
        "땀" in msg
        and not any(
            k in msg
            for k in (
                "겨드랑", "누렇", "황변", "데오", "땀억제",
                "노랗", "노란", "누래", "누런",
                "오래된", "오래됐", "몇 달", "몇달", "오랫동안",
            )
        )
    ) or "mo hoi tuoi" in raw_n or (
        "sweat" in raw_n
        and "yellow" not in raw_n
        and "armpit" not in raw_n
        and "old" not in raw_n
        and "aged" not in raw_n
        and "deodorant" not in raw_n
        and "khu mui" not in raw_n
    ):
        return "S_SWEAT_FRESH"

    return None
