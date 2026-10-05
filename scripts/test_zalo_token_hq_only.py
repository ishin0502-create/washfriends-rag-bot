# -*- coding: utf-8 -*-
"""Education bot must not burn the shared OA refresh token locally."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("OPENAI_API_KEY", "test-not-used")
os.environ.setdefault("WF_HQ_API_BASE", "https://hq.example.test")
os.environ.setdefault("INTERNAL_WEBHOOK_SECRET", "test-secret")

import zalo_token  # noqa: E402


def test_params_invalid_is_not_token_error():
    assert zalo_token.is_token_error(-201) is False
    assert zalo_token.is_token_error("-201") is False
    assert zalo_token.is_token_error(-216) is True


def test_call_refresh_hard_disabled():
    async def _run():
        try:
            await zalo_token._call_refresh("anything")
        except RuntimeError as e:
            assert "only writer" in str(e).lower() or "disabled" in str(e).lower()
            return
        raise AssertionError("_call_refresh must not call Zalo OAuth")

    asyncio.run(_run())


def test_refresh_tokens_uses_hq_not_oauth(monkeypatch=None):
    zalo_token._access_token = ""
    zalo_token._expires_at = 0.0
    called = {"oauth": 0, "hq": 0}

    def fake_hq():
        called["hq"] += 1
        zalo_token._access_token = "hq-access"
        zalo_token._expires_at = 9e12
        return True

    async def boom(_rt):
        called["oauth"] += 1
        raise AssertionError("must not OAuth refresh")

    zalo_token._fetch_from_hq = fake_hq
    zalo_token._save_to_neo4j = lambda: None
    zalo_token._call_refresh = boom

    async def _run():
        tok = await zalo_token.refresh_tokens(force=True)
        assert tok == "hq-access"
        assert called["hq"] == 1
        assert called["oauth"] == 0

    asyncio.run(_run())


if __name__ == "__main__":
    test_params_invalid_is_not_token_error()
    test_call_refresh_hard_disabled()
    test_refresh_tokens_uses_hq_not_oauth()
    print("OK zalo_token_hq_only")
