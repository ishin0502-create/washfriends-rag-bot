# -*- coding: utf-8 -*-
"""Append-only failure / weak-answer log for weekly seed feedback."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

_LOG_PATH = Path(os.getenv("WF_FAILURE_LOG", "logs/ask_failures.jsonl"))


def log_failure(
    *,
    reason: str,
    message: str = "",
    lang: str = "",
    entities: Optional[dict] = None,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    """Best-effort local JSONL — never raises into the ask path."""
    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "ts": int(time.time()),
            "reason": reason,
            "lang": lang,
            "message": (message or "")[:500],
            "stain_id": (entities or {}).get("stain_id"),
            "item_id": (entities or {}).get("item_id"),
            "fabric_type": (entities or {}).get("fabric_type"),
        }
        if extra:
            row["extra"] = extra
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass
