# -*- coding: utf-8 -*-
"""Tests for education parity v5."""
from education_parity_v5 import (
    EXTRA_DRIED_PATH_KO,
    EXTRA_DRIED_PATH_VI,
    OPS_VI_CANON,
    RESCUE_BY_STAIN,
    vn_specialty_stain_seed_rows,
)
from fabric_care import FABRIC_CURRICULUM_IDS, education_for_fabric
from protocol import PROTOCOL_BUILDERS, has_protocol
from stain_age_buckets import DRIED_PATH_KO, DRIED_PATH_VI
from w2_ops_rescue import OPS_DRILLS, rescue_card_for_stain


def test_dried_parity_covers_former_gaps():
    for sid in (
        "S_BLOOD_DRY",
        "S_INK_PEN",
        "S_RUST",
        "S_MILDEW",
        "S_URINE",
        "S_PAINT_OIL",
        "S_BETEL",
    ):
        assert sid in DRIED_PATH_KO
        assert sid in DRIED_PATH_VI
        assert "(1)" in DRIED_PATH_KO[sid]
        assert len(DRIED_PATH_KO[sid]) >= 40


def test_extra_dried_counts():
    assert len(EXTRA_DRIED_PATH_KO) >= 35
    assert len(EXTRA_DRIED_PATH_VI) >= 35


def test_vi_ops_canon_has_diacritics():
    sample = OPS_DRILLS["I_CARE_LABEL"]["why_vi"]
    assert "GIAO DUC DRILL" not in sample
    assert any(ord(c) > 127 for c in sample)  # has non-ASCII (diacritics)


def test_rescue_per_stain_wine():
    card = rescue_card_for_stain({"id": "S_RED_WINE", "group_id": "G3", "dried_path_ko": "dried"})
    assert "식초" in card["rescue_2nd_ko"]
    assert RESCUE_BY_STAIN["S_RED_WINE"]
    assert "100%" in RESCUE_BY_STAIN["S_RED_WINE"]["ko"]


def test_fabric_acetate_nylon_blend():
    for iid in ("I_FABRIC_ACETATE", "I_FABRIC_NYLON", "I_FABRIC_BLEND"):
        assert iid in FABRIC_CURRICULUM_IDS
        edu = education_for_fabric(iid)
        assert edu.get("fresh_path_ko") and edu.get("fresh_path_vi")
        assert not any("\uac00" <= c <= "\ud7a3" for c in edu["fresh_path_vi"])


def test_new_stain_protocols():
    assert has_protocol("S_PAINT_OIL")
    assert has_protocol("S_BETEL")
    assert "S_PAINT_OIL" in PROTOCOL_BUILDERS
    rows = vn_specialty_stain_seed_rows()
    assert {r["id"] for r in rows} == {"S_PAINT_OIL", "S_BETEL"}


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("OK", name)
