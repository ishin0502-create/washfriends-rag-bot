# -*- coding: utf-8 -*-
"""Push L1/L2/L3 course counts to HQ (fail-open)."""
from __future__ import annotations

from typing import Any

from qa_usage import _http_json, fetch_access_meta


def _snapshot(user_id: str) -> dict[str, Any]:
    from l1_course import LESSONS as L1, l1_done_count
    from l2_course import LESSONS as L2, l2_done_count
    from l3_course import LESSONS as L3, l3_done_count

    uid = (user_id or "").strip()
    return {
        "zalo_user_id": uid,
        "l1_done": l1_done_count(uid),
        "l1_total": len(L1),
        "l2_done": l2_done_count(uid),
        "l2_total": len(L2),
        "l3_done": l3_done_count(uid),
        "l3_total": len(L3),
    }


def push_course_progress(user_id: str) -> bool:
    uid = (user_id or "").strip()
    if not uid:
        return False
    body = _snapshot(uid)
    meta = fetch_access_meta(uid)
    if meta:
        if meta.get("client_kind"):
            body["client_kind"] = str(meta["client_kind"])[:20]
        if meta.get("store_code"):
            body["store_code"] = str(meta["store_code"])[:40]
        if meta.get("store_name"):
            body["store_name"] = str(meta["store_name"])[:200]
        if meta.get("person_name"):
            body["person_name"] = str(meta["person_name"])[:120]
    data = _http_json("PUT", "/api/v1/internal/education-bot/course-progress", body)
    return bool(data and data.get("ok"))
