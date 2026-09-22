# -*- coding: utf-8 -*-
"""Safe intake subtype branching for umbrella stains (top-5 pattern)."""
from __future__ import annotations

from ko_stain_education import KO_STAIN_EDU
from owner_answer_clarity import STAIN_STATUS_KO, STAIN_STATUS_VI
from owner_hand_motions import build_hand_motions


def _edu(sid: str) -> str:
    return str((KO_STAIN_EDU.get(sid) or {}).get("fresh_path_ko") or "")


def test_ink_intake_kinds():
    path = _edu("S_INK_PEN")
    assert "수성" in path and "만년필" in path
    assert "토너" in path
    assert "볼펜" in path
    status = STAIN_STATUS_KO["S_INK_PEN"]
    assert "수성" in status and "토너" in status
    m = build_hand_motions("S_INK_PEN", "ko")
    assert "수성" in m or "만년필" in m
    # silk refuse still first-class
    silk = build_hand_motions(
        "S_INK_PEN",
        "ko",
        graph={
            "fabric_context": {"id": "F4", "name": "Silk"},
            "entities": {"fabric_type": "silk"},
        },
    )
    assert "전문" in silk or "거절" in silk
    assert "수성" in silk or "찬물" in silk


def test_glue_mascara_wine_oil_intake():
    assert "502" in _edu("S_GLUE") and "【확인】" in _edu("S_GLUE")
    assert "워터프루프" in _edu("S_MASCARA") and "【확인】" in _edu("S_MASCARA")
    assert "화이트" in _edu("S_RED_WINE") or "맥주" in _edu("S_RED_WINE")
    assert "엔진" in _edu("S_COOKING_OIL") or "오토바이" in _edu("S_COOKING_OIL")

    assert "502" in STAIN_STATUS_KO["S_GLUE"]
    assert "워터프루프" in STAIN_STATUS_KO["S_MASCARA"]
    assert "화이트" in STAIN_STATUS_KO["S_RED_WINE"]
    assert "엔진" in STAIN_STATUS_KO["S_COOKING_OIL"] or "오토바이" in STAIN_STATUS_KO["S_COOKING_OIL"]

    # VI parity for new status cards
    for sid in ("S_INK_PEN", "S_GLUE", "S_MASCARA", "S_COOKING_OIL", "S_RED_WINE"):
        assert sid in STAIN_STATUS_VI

    glue_m = build_hand_motions("S_GLUE", "ko")
    assert "종류" in glue_m or "502" in glue_m
    mas_m = build_hand_motions("S_MASCARA", "ko")
    assert "워터프루프" in mas_m


def test_no_glycerin_invented():
    """Safe patch: do not add glycerin as shop chem primary."""
    blob = _edu("S_INK_PEN") + STAIN_STATUS_KO["S_INK_PEN"]
    assert "글리세린" not in blob


if __name__ == "__main__":
    test_ink_intake_kinds()
    test_glue_mascara_wine_oil_intake()
    test_no_glycerin_invented()
    print("intake_branch_top5 ok")
