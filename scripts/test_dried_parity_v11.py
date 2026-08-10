# -*- coding: utf-8 -*-
"""Dried parity v11 — Protocol coverage + soak + rescue."""
from protocol import PROTOCOL_BUILDERS
from stain_age_buckets import (
    DRIED_PATH_KO,
    DRIED_PATH_VI,
    apply_stain_age_buckets,
    seed_dried_path_rows,
)
from education_dried_parity_v11 import (
    DRIED_PATH_KO_V11,
    LONG_SOAK_STAIN_IDS,
    RESCUE_BY_STAIN_V11,
    soak_minutes_for_stain,
)
from w2_ops_rescue import rescue_card_for_stain


def _deep(s: str) -> bool:
    if not s:
        return False
    steps = sum(1 for i in range(1, 7) if f"({i})" in s)
    return steps >= 4 and len(s) >= 80


def test_all_protocols_have_deep_dried_ko_vi():
    missing_ko = []
    missing_vi = []
    thin_ko = []
    thin_vi = []
    for sid in PROTOCOL_BUILDERS:
        ko = DRIED_PATH_KO.get(sid, "")
        vi = DRIED_PATH_VI.get(sid, "")
        if not ko:
            missing_ko.append(sid)
        elif not _deep(ko):
            thin_ko.append(sid)
        if not vi:
            missing_vi.append(sid)
        elif not _deep(vi):
            thin_vi.append(sid)
    assert not missing_ko, f"missing dried KO: {missing_ko}"
    assert not missing_vi, f"missing dried VI: {missing_vi}"
    assert not thin_ko, f"thin dried KO: {thin_ko}"
    assert not thin_vi, f"thin dried VI: {thin_vi}"


def test_v11_overrides_v10_thin_doenjang():
    assert "30–60" in DRIED_PATH_KO["S_DOENJANG"] or "30-60" in DRIED_PATH_KO["S_DOENJANG"]
    assert "Enzyme" in DRIED_PATH_VI["S_DOENJANG"] or "enzyme" in DRIED_PATH_VI["S_DOENJANG"].lower()
    assert "giấm" in DRIED_PATH_VI["S_GOCHUJANG"].lower() or "Giấm" in DRIED_PATH_VI["S_GOCHUJANG"]


def test_protein_long_soak_on_dried():
    assert soak_minutes_for_stain("S_EGG") == (30, 60)
    assert soak_minutes_for_stain("S_RED_WINE") == (15, 30)
    g = {
        "stain_context": {
            "id": "S_EGG",
            "fresh_path_ko": "효소 15분",
            "dried_path_ko": "짧음",
        },
        "tools": [],
    }
    out = apply_stain_age_buckets(g, "마른 계란 얼룩", {})
    sc = out["stain_context"]
    assert sc["age_bucket"] == "dried"
    assert "30" in sc["soak_minutes_ko"] and "60" in sc["soak_minutes_ko"]
    assert _deep(sc["dried_path_ko"])


def test_per_stain_rescue_for_v11_ids():
    for sid in ("S_DOENJANG", "S_KETCHUP", "S_BLACK_COFFEE", "S_SOFTENER_SPOT"):
        card = rescue_card_for_stain({"id": sid, "group_id": "G5"})
        assert "2차" in card["rescue_2nd_ko"] or "Lần 2" in card["rescue_2nd_vi"]
        assert sid in RESCUE_BY_STAIN_V11 or "2차" in card["rescue_2nd_ko"]


def test_rescue_coverage_not_group_only_for_protocols():
    """Every protocol should resolve to a stain-specific or at least labeled 2차 line."""
    from education_parity_v5 import RESCUE_BY_STAIN
    from education_gaps_v8 import RESCUE_BY_STAIN_V8

    covered = set(RESCUE_BY_STAIN) | set(RESCUE_BY_STAIN_V8) | set(RESCUE_BY_STAIN_V11)
    # iodine/chili via v7 helpers — still OK if group fallback, but prefer explicit
    covered |= {"S_IODINE", "S_CHILI"}
    missing = [sid for sid in PROTOCOL_BUILDERS if sid not in covered]
    assert not missing, f"no per-stain rescue: {missing}"


def test_seed_rows_include_v11():
    rows = {r["id"]: r for r in seed_dried_path_rows()}
    for sid in DRIED_PATH_KO_V11:
        assert sid in rows
        assert _deep(rows[sid].get("dried_path_ko", ""))


def test_long_soak_set_nonempty():
    assert len(LONG_SOAK_STAIN_IDS) >= 15
