"""
user_session.py
Short-lived per-user conversation state for Zalo / Facebook image flows.
In-memory (single Railway replica). TTL clears stale pending label waits.
"""

from __future__ import annotations

import time
from typing import Any, Optional

_TTL_SEC = 30 * 60
_store: dict[str, dict[str, Any]] = {}


def _key(channel: str, user_id: str) -> str:
    return f"{channel}:{user_id}"


def _prune() -> None:
    now = time.time()
    dead = [k for k, v in _store.items() if now - float(v.get("ts", 0)) > _TTL_SEC]
    for k in dead:
        del _store[k]


def get_session(channel: str, user_id: str) -> dict[str, Any]:
    _prune()
    return dict(_store.get(_key(channel, user_id)) or {})


def set_pending_label(
    channel: str,
    user_id: str,
    *,
    lang: str = "vi",
    stain_guess: str = "",
    fabric_guess: str = "",
    caption: str = "",
    confidence: str = "low",
) -> None:
    _prune()
    _store[_key(channel, user_id)] = {
        "ts": time.time(),
        "awaiting": "care_label",
        "lang": lang or "vi",
        "stain_guess": stain_guess or "",
        "fabric_guess": fabric_guess or "",
        "caption": caption or "",
        "confidence": confidence or "low",
    }


def pop_pending_label(channel: str, user_id: str) -> Optional[dict[str, Any]]:
    _prune()
    k = _key(channel, user_id)
    data = _store.get(k)
    if not data or data.get("awaiting") != "care_label":
        return None
    del _store[k]
    return dict(data)


def clear_session(channel: str, user_id: str) -> None:
    _store.pop(_key(channel, user_id), None)
