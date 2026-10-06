# -*- coding: utf-8 -*-
"""Protocol stains skip _call_llm (template SOP). Item-care still uses LLM."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("WF_OWNER_QA_DIR", os.environ.get("WF_OWNER_QA_DIR") or ".")
os.environ.setdefault("OPENAI_API_KEY", "sk-test-skip")

from graphrag_engine import (  # noqa: E402
    _answer_with_optional_cache,
    _offline_stain_graph,
)


def test_protocol_template_skips_llm():
    sid = "S_BLACK_COFFEE"
    ctx = {"graph": _offline_stain_graph(sid)}
    with patch("graphrag_engine.cache_lookup", return_value=None):
        with patch("graphrag_engine._call_llm") as llm:
            llm.side_effect = AssertionError("LLM must not run for protocol stains")
            ans = _answer_with_optional_cache(
                "면 셔츠에 커피 얼룩",
                {"lang": "ko", "stain_id": sid, "intent": "treatment"},
                ctx,
            )
    assert ans
    assert "커피" in ans or "식초" in ans or "찬물" in ans
    llm.assert_not_called()


if __name__ == "__main__":
    test_protocol_template_skips_llm()
    print("OK protocol_skip_llm")
