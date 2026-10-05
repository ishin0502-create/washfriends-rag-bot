# -*- coding: utf-8 -*-
"""Course-progress HQ PUT retry queue."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["WF_OWNER_QA_DIR"] = str(Path(tempfile.mkdtemp()) / "owner_qa")

import course_progress_sync as cps  # noqa: E402


def test_enqueue_flush_success(monkey=None):
    calls = {"n": 0}

    def fake_http(method, path, payload=None):
        calls["n"] += 1
        if calls["n"] == 1:
            return None
        return {"ok": True}

    cps._http_json = fake_http
    cps.fetch_access_meta = lambda uid: {}
    cps._snapshot = lambda uid: {
        "zalo_user_id": uid,
        "l1_done": 1,
        "l1_total": 17,
        "l2_done": 0,
        "l2_total": 9,
        "l3_done": 0,
        "l3_total": 10,
    }

    assert cps.push_course_progress("u1") is True
    assert cps._load_retry_ids() == []

    calls["n"] = 0

    def always_fail(method, path, payload=None):
        return None

    cps._http_json = always_fail
    assert cps.push_course_progress("u2") is False
    assert "u2" in cps._load_retry_ids()

    cps._http_json = lambda *a, **k: {"ok": True}
    out = cps.flush_course_progress_retries(limit=10)
    assert out["pushed_ok"] == 1
    assert cps._load_retry_ids() == []


if __name__ == "__main__":
    test_enqueue_flush_success()
    print("ok")
