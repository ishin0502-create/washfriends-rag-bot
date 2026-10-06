# -*- coding: utf-8 -*-
"""Pick exam items: failed ids first, then shuffle the rest."""
from __future__ import annotations

import random
from typing import Any, Optional


def pick_exam_pool(
    pool: list[dict[str, Any]],
    n: int,
    *,
    prefer_ids: Optional[list[str]] = None,
    rng: Optional[random.Random] = None,
) -> list[dict[str, Any]]:
    n = max(1, min(10, int(n or 7)))
    r = rng or random.Random()
    by_id = {str(it.get("id") or ""): it for it in pool if it.get("id")}
    picked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for pid in prefer_ids or []:
        key = str(pid or "").strip()
        if key and key in by_id and key not in seen:
            picked.append(by_id[key])
            seen.add(key)
        if len(picked) >= n:
            return picked[:n]
    rest = [it for it in pool if str(it.get("id") or "") not in seen]
    r.shuffle(rest)
    picked.extend(rest[: n - len(picked)])
    return picked[:n]
