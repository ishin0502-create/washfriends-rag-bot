# -*- coding: utf-8 -*-
"""Unit tests for Zalo franchise-owner allowlist gate."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_owner_gate_off_by_default(monkeypatch=None):
    # Manual env isolation without pytest dependency
    keys = (
        "ZALO_OWNER_GATE",
        "ZALO_OWNER_ALLOWLIST",
        "ZALO_OWNER_ALLOWLIST_FILE",
        "WF_HQ_API_BASE",
        "WASHFRIENDS_API_BASE",
        "INTERNAL_WEBHOOK_SECRET",
        "EDUCATION_BOT_INTERNAL_SECRET",
    )
    saved = {k: os.environ.get(k) for k in keys}
    try:
        for k in saved:
            os.environ.pop(k, None)
        from zalo_owner_access import clear_owner_access_cache, is_authorized_owner, gate_status, deny_reply_text

        clear_owner_access_cache()
        assert gate_status()["enabled"] is False
        assert is_authorized_owner("111") is True
        assert "가맹" in deny_reply_text("산소표백제 뭐예요?")
        assert "nhượng quyền" in deny_reply_text("vết cà phê").lower() or "nhượng" in deny_reply_text("vết cà phê").lower()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        from zalo_owner_access import clear_owner_access_cache

        clear_owner_access_cache()


def test_allowlist_only():
    keys = (
        "ZALO_OWNER_GATE",
        "ZALO_OWNER_ALLOWLIST",
        "ZALO_OWNER_ALLOWLIST_FILE",
        "WF_HQ_API_BASE",
        "WASHFRIENDS_API_BASE",
        "INTERNAL_WEBHOOK_SECRET",
        "EDUCATION_BOT_INTERNAL_SECRET",
    )
    saved = {k: os.environ.get(k) for k in keys}
    try:
        for k in keys:
            os.environ.pop(k, None)
        os.environ["ZALO_OWNER_ALLOWLIST"] = "aaa111, bbb222"
        from zalo_owner_access import clear_owner_access_cache, is_authorized_owner, gate_status

        clear_owner_access_cache()
        st = gate_status()
        assert st["enabled"] is True
        assert st["mode"] == "allowlist"
        assert st["allowlist_size"] == 2
        assert is_authorized_owner("aaa111") is True
        assert is_authorized_owner("bbb222") is True
        assert is_authorized_owner("ccc333") is False
        assert is_authorized_owner("") is False
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        from zalo_owner_access import clear_owner_access_cache

        clear_owner_access_cache()


def test_force_gate_empty_denies_all():
    keys = (
        "ZALO_OWNER_GATE",
        "ZALO_OWNER_ALLOWLIST",
        "ZALO_OWNER_ALLOWLIST_FILE",
        "WF_HQ_API_BASE",
        "WASHFRIENDS_API_BASE",
        "INTERNAL_WEBHOOK_SECRET",
        "EDUCATION_BOT_INTERNAL_SECRET",
    )
    saved = {k: os.environ.get(k) for k in keys}
    try:
        for k in keys:
            os.environ.pop(k, None)
        os.environ["ZALO_OWNER_GATE"] = "1"
        os.environ["ZALO_OWNER_ALLOWLIST"] = ""
        from zalo_owner_access import clear_owner_access_cache, is_authorized_owner, gate_status

        clear_owner_access_cache()
        assert gate_status()["mode"] == "deny_all_until_ids"
        assert is_authorized_owner("anyone") is False
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        from zalo_owner_access import clear_owner_access_cache

        clear_owner_access_cache()


if __name__ == "__main__":
    test_owner_gate_off_by_default()
    test_allowlist_only()
    test_force_gate_empty_denies_all()
    print("OK zalo_owner_access")
