# -*- coding: utf-8 -*-
"""Franchise-owner gate for Zalo OA 1:1 education bot.

OA chats are already private (A cannot see B). This module only decides
whether a given sender.user_id may receive GraphRAG education answers.

Env:
  ZALO_OWNER_GATE=1|on|true   — force gate on (deny if not on allowlist)
  ZALO_OWNER_ALLOWLIST=id1,id2 — comma/space/newline-separated Zalo user_ids
  ZALO_OWNER_ALLOWLIST_FILE=path — optional file (one id per line, # comments)

Behavior:
  - Gate OFF (default): everyone who DMs the OA gets answers (legacy).
  - Gate ON + empty allowlist: deny all (safe lock until HQ adds IDs).
  - Gate ON + allowlist: only listed user_ids get education answers.
  Gate auto-turns ON when ALLOWLIST (or file) has at least one id.
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import FrozenSet, Tuple

from reply_lang import detect_reply_lang

_TRUTHY = frozenset({"1", "true", "yes", "on", "y"})


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
            # allow "name:id" or bare id
            if ":" in s and not s.startswith("http"):
                s = s.split(":")[-1].strip()
            out.update(_parse_ids(s))
    except OSError as e:
        print(f"[ZALO OWNER GATE] allowlist file read error: {e}")
    return frozenset(out)


@lru_cache(maxsize=1)
def _load_config() -> Tuple[bool, FrozenSet[str]]:
    """Return (gate_enabled, allowlist). Cached until process restart / clear_cache."""
    file_path = (os.environ.get("ZALO_OWNER_ALLOWLIST_FILE") or "").strip()
    ids = set(_parse_ids(os.environ.get("ZALO_OWNER_ALLOWLIST", "")))
    if file_path:
        ids |= _ids_from_file(file_path)
    allow = frozenset(ids)
    force = (os.environ.get("ZALO_OWNER_GATE") or "").strip().lower() in _TRUTHY
    enabled = force or bool(allow)
    return enabled, allow


def clear_owner_access_cache() -> None:
    """Tests / after Railway env change without redeploy (rare)."""
    _load_config.cache_clear()


def owner_gate_enabled() -> bool:
    return _load_config()[0]


def owner_allowlist() -> FrozenSet[str]:
    return _load_config()[1]


def owner_allowlist_size() -> int:
    return len(owner_allowlist())


def is_authorized_owner(user_id: str) -> bool:
    """True if this Zalo sender may use the education bot."""
    uid = (user_id or "").strip()
    if not uid:
        return False
    enabled, allow = _load_config()
    if not enabled:
        return True
    if not allow:
        return False
    return uid in allow


def deny_reply_text(user_text: str = "") -> str:
    """Fixed refusal — no SOP, no graph. KO/VI/EN by message language."""
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
    enabled, allow = _load_config()
    return {
        "enabled": enabled,
        "allowlist_size": len(allow),
        "mode": (
            "off"
            if not enabled
            else ("deny_all_until_ids" if not allow else "allowlist")
        ),
    }
