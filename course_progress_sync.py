# -*- coding: utf-8 -*-
"""Push L1/L2/L3 course counts to HQ (fail-open)."""
from __future__ import annotations

import json
import threading
import time
from typing import Any

from qa_usage import _http_json, fetch_access_meta

_RETRY_LOCK = threading.Lock()
_RETRY_MAX = 80
_RETRY_FILE = "_course_progress_retry.json"


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


def _retry_path():
    from owner_qa_log import _data_dir

    d = _data_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d / _RETRY_FILE


def _load_retry_ids() -> list[str]:
    path = _retry_path()
    with _RETRY_LOCK:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    ids = data.get("zalo_user_ids") if isinstance(data, dict) else data
    if not isinstance(ids, list):
        return []
    out = []
    seen = set()
    for uid in ids:
        u = str(uid or "").strip()
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out[:_RETRY_MAX]


def _save_retry_ids(ids: list[str]) -> None:
    path = _retry_path()
    uniq: list[str] = []
    seen = set()
    for uid in ids:
        u = str(uid or "").strip()
        if u and u not in seen:
            seen.add(u)
            uniq.append(u)
        if len(uniq) >= _RETRY_MAX:
            break
    with _RETRY_LOCK:
        path.write_text(
            json.dumps({"zalo_user_ids": uniq, "updated_at": time.time()}, ensure_ascii=False),
            encoding="utf-8",
        )


def enqueue_course_progress_retry(user_id: str) -> None:
    uid = (user_id or "").strip()
    if not uid:
        return
    ids = _load_retry_ids()
    if uid not in ids:
        ids.append(uid)
        _save_retry_ids(ids)


def dequeue_course_progress_retry(user_id: str) -> None:
    uid = (user_id or "").strip()
    if not uid:
        return
    ids = [x for x in _load_retry_ids() if x != uid]
    _save_retry_ids(ids)


def flush_course_progress_retries(*, limit: int = 20) -> dict:
    """Retry failed HQ PUTs. Fail-open; keep remaining ids on disk."""
    ids = _load_retry_ids()
    ok = fail = 0
    kept: list[str] = []
    for i, uid in enumerate(ids):
        if i >= max(1, int(limit)):
            kept.extend(ids[i:])
            break
        if push_course_progress(uid, from_retry=True):
            ok += 1
        else:
            fail += 1
            kept.append(uid)
    _save_retry_ids(kept)
    return {"ok": True, "tried": min(len(ids), max(1, int(limit))), "pushed_ok": ok, "pushed_fail": fail, "queued": len(kept)}


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


def push_course_progress(user_id: str, *, from_retry: bool = False) -> bool:
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
    delays = (0.0, 0.4, 1.0) if not from_retry else (0.0,)
    for delay in delays:
        if delay:
            time.sleep(delay)
        data = _http_json("PUT", "/api/v1/internal/education-bot/course-progress", body)
        if data and data.get("ok"):
            dequeue_course_progress_retry(uid)
            return True
    if not from_retry:
        enqueue_course_progress_retry(uid)
    return False
