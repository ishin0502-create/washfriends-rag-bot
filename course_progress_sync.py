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


def snapshot_owner_qa_dir(dest) -> dict:
    """Copy owner_qa JSON files (not mutating originals)."""
    import json
    import time
    from pathlib import Path

    from owner_qa_log import _data_dir

    src = _data_dir()
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    if src.is_dir():
        for p in src.glob("*.json"):
            if p.name.startswith("_"):
                continue
            (dest / p.name).write_bytes(p.read_bytes())
            n += 1
    meta = {"copied": n, "src": str(src), "dest": str(dest), "ts": time.time()}
    (dest / "_manifest.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


def backfill_course_progress(*, apply: bool) -> dict:
    """Push disk L1/L2/L3 counts to HQ. apply=False is dry-run."""
    from owner_qa_log import _data_dir, load_user

    d = _data_dir()
    uids: list[str] = []
    if d.is_dir():
        for p in sorted(d.glob("*.json")):
            if p.name.startswith("_"):
                continue
            uid = p.stem.strip()
            if uid:
                uids.append(uid)
    items = []
    ok = fail = skip = 0
    for uid in uids:
        data = load_user(uid)
        if not any(isinstance(data.get(k), dict) for k in ("l1_course", "l2_course", "l3_course")):
            skip += 1
            continue
        snap = _snapshot(uid)
        row = {
            "zalo_user_id": uid,
            "l1_done": snap["l1_done"],
            "l1_total": snap["l1_total"],
            "l2_done": snap["l2_done"],
            "l2_total": snap["l2_total"],
            "l3_done": snap["l3_done"],
            "l3_total": snap["l3_total"],
            "pushed": False,
        }
        if apply:
            row["pushed"] = bool(push_course_progress(uid))
            if row["pushed"]:
                ok += 1
            else:
                fail += 1
        items.append(row)
    return {
        "ok": True,
        "apply": apply,
        "dir": str(d),
        "files": len(uids),
        "with_course": len(items),
        "skip_no_course": skip,
        "pushed_ok": ok,
        "pushed_fail": fail,
        "items": items,
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
