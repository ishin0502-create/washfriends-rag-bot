# -*- coding: utf-8 -*-
"""Franchise-owner gate for Zalo OA 1:1 education bot.

OA chats are already private (A cannot see B). This module decides whether
a given sender.user_id may receive GraphRAG education answers.

Sources (OR):
  1) HQ API — stores with education_bot_enabled + up to 2 Zalo IDs
     Env: WF_HQ_API_BASE, INTERNAL_WEBHOOK_SECRET (or EDUCATION_BOT_INTERNAL_SECRET)
  2) Legacy env allowlist — ZALO_OWNER_ALLOWLIST / FILE / GATE

Gate turns ON when HQ API is configured OR env allowlist/GATE is set.
"""
from __future__ import annotations

import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache
from pathlib import Path
from typing import FrozenSet, Optional, Tuple

from reply_lang import detect_reply_lang

_TRUTHY = frozenset({"1", "true", "yes", "on", "y"})
_hq_cache: dict[str, object] = {"ts": 0.0, "allowed": frozenset()}
_HQ_CACHE_TTL = 60.0  # seconds


def _parse_ids(raw: str) -> FrozenSet[str]:
    if not raw or not str(raw).strip():
        return frozenset()
    parts = re.split(r"[,;\s]+", str(raw).strip())
    return frozenset(p.strip() for p in parts if p.strip() and not p.strip().startswith("#"))


def _ids_from_file(path: str) -> FrozenSet[str]:
    p = Path(path.strip())
    if not p.is_file():
        print(f"[ZALO OWNER GATE] allowlist file missing: {p}")
        return frozenset()
    out: set[str] = set()
    try:
        for line in p.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if ":" in s and not s.startswith("http"):
                s = s.split(":")[-1].strip()
            out.update(_parse_ids(s))
    except OSError as e:
        print(f"[ZALO OWNER GATE] allowlist file read error: {e}")
    return frozenset(out)


def _hq_api_base() -> str:
    return (
        os.environ.get("WF_HQ_API_BASE")
        or os.environ.get("WASHFRIENDS_API_BASE")
        or ""
    ).strip().rstrip("/")


def _hq_secret() -> str:
    return (
        os.environ.get("EDUCATION_BOT_INTERNAL_SECRET")
        or os.environ.get("INTERNAL_WEBHOOK_SECRET")
        or ""
    ).strip()


def hq_api_configured() -> bool:
    return bool(_hq_api_base() and _hq_secret())


def _fetch_hq_allowlist() -> FrozenSet[str]:
    """Pull enabled education-bot Zalo IDs from WashFriends HQ API."""
    base = _hq_api_base()
    secret = _hq_secret()
    if not base or not secret:
        return frozenset()
    url = f"{base}/api/v1/internal/education-bot/allowlist"
    req = urllib.request.Request(
        url,
        headers={"X-Internal-Secret": secret, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            import json

            data = json.loads(resp.read().decode("utf-8"))
        items = data.get("items") or []
        return frozenset(
            str(it.get("zalo_user_id") or "").strip()
            for it in items
            if str(it.get("zalo_user_id") or "").strip()
        )
    except Exception as e:
        print(f"[ZALO OWNER GATE] HQ allowlist fetch failed: {e}")
        return frozenset()


def _hq_allowlist_cached() -> FrozenSet[str]:
    now = time.time()
    if now - float(_hq_cache.get("ts") or 0) < _HQ_CACHE_TTL:
        return _hq_cache.get("allowed") or frozenset()  # type: ignore[return-value]
    allowed = _fetch_hq_allowlist()
    _hq_cache["ts"] = now
    _hq_cache["allowed"] = allowed
    return allowed


def check_hq_access(user_id: str) -> Optional[bool]:
    """True/False if HQ API answers; None if HQ not configured or request failed."""
    if not hq_api_configured():
        return None
    uid = (user_id or "").strip()
    if not uid:
        return False
    # Prefer live check for toggle immediacy (still short timeout)
    base = _hq_api_base()
    secret = _hq_secret()
    q = urllib.parse.urlencode({"zalo_user_id": uid})
    url = f"{base}/api/v1/internal/education-bot/access?{q}"
    req = urllib.request.Request(
        url,
        headers={"X-Internal-Secret": secret, "Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=6) as resp:
            import json

            data = json.loads(resp.read().decode("utf-8"))
        return bool(data.get("allowed"))
    except Exception as e:
        print(f"[ZALO OWNER GATE] HQ access check failed, falling back to cache: {e}")
        return uid in _hq_allowlist_cached()


@lru_cache(maxsize=1)
def _load_env_config() -> Tuple[bool, FrozenSet[str]]:
    file_path = (os.environ.get("ZALO_OWNER_ALLOWLIST_FILE") or "").strip()
    ids = set(_parse_ids(os.environ.get("ZALO_OWNER_ALLOWLIST", "")))
    if file_path:
        ids |= _ids_from_file(file_path)
    allow = frozenset(ids)
    force = (os.environ.get("ZALO_OWNER_GATE") or "").strip().lower() in _TRUTHY
    enabled = force or bool(allow)
    return enabled, allow


def clear_owner_access_cache() -> None:
    _load_env_config.cache_clear()
    _hq_cache["ts"] = 0.0
    _hq_cache["allowed"] = frozenset()


def owner_gate_enabled() -> bool:
    env_on, _ = _load_env_config()
    return env_on or hq_api_configured()


def owner_allowlist() -> FrozenSet[str]:
    _, env_ids = _load_env_config()
    if hq_api_configured():
        return env_ids | _hq_allowlist_cached()
    return env_ids


def owner_allowlist_size() -> int:
    return len(owner_allowlist())


def is_authorized_owner(user_id: str) -> bool:
    """True if this Zalo sender may use the education bot."""
    uid = (user_id or "").strip()
    if not uid:
        return False

    env_on, env_ids = _load_env_config()
    if uid in env_ids:
        return True

    hq = check_hq_access(uid)
    if hq is True:
        return True
    if hq is False:
        # HQ says no — still allow env list above; otherwise deny if gate on
        if env_on and not env_ids:
            return False
        if hq_api_configured() or env_on:
            return False
        return True  # gate fully off

    # HQ not configured
    if not env_on:
        return True
    if not env_ids:
        return False
    return False


def deny_reply_text(user_text: str = "") -> str:
    lang = detect_reply_lang(user_text or "")
    if lang == "ko":
        return (
            "◆ 가맹 점주 전용 교육 채널입니다.\n"
            "등록된 Wash Friends 가맹 점주만 질문·답변을 받을 수 있습니다.\n"
            "등록이 필요하시면 본사(Nhượng Quyền Giặt Sấy Wash Friends)에 "
            "매장명·점주 Zalo를 알려 주세요."
        )
    if lang == "en":
        return (
            "◆ Franchise-owner education channel only.\n"
            "Only registered Wash Friends owners can ask and receive answers.\n"
            "To register, contact HQ (Nhượng Quyền Giặt Sấy Wash Friends) "
            "with your store name and Zalo."
        )
    return (
        "◆ Kênh đào tạo chỉ dành cho chủ cửa hàng nhượng quyền.\n"
        "Chỉ chủ cửa hàng Wash Friends đã đăng ký mới hỏi và nhận hướng dẫn.\n"
        "Cần đăng ký: liên hệ HQ (Nhượng Quyền Giặt Sấy Wash Friends), "
        "gửi tên cửa hàng + Zalo của anh/chị."
    )


def gate_status() -> dict:
    env_on, env_ids = _load_env_config()
    hq = hq_api_configured()
    enabled = env_on or hq
    mode = "off"
    if enabled:
        if hq and env_ids:
            mode = "hq_api+env"
        elif hq:
            mode = "hq_api"
        elif env_ids:
            mode = "allowlist"
        else:
            mode = "deny_all_until_ids"
    return {
        "enabled": enabled,
        "allowlist_size": len(env_ids),
        "hq_api": hq,
        "mode": mode,
    }
