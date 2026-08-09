# -*- coding: utf-8 -*-
"""Regression matrix: every Protocol stain must emit tools + chemicals for cotton.

Definition of done for equipment/chem education — if this fails, answers will miss
(2) tools / (4) chemicals for franchise owners.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from protocol import (
    CHEM_META,
    PROTOCOL_BUILDERS,
    apply_protocol_to_graph,
    has_protocol,
)
from protocol_equipment import (
    BIOHAZARD_STAINS,
    GLOVE_CHEMS,
    collect_required_tool_ids,
    seed_chem_link_rows,
    seed_tool_link_rows,
)


FABRICS = [
    ("cotton", "F1", "Cotton", True),
    ("silk", "F4", "Silk", False),
]


def _graph(stain_id: str, fabric_id: str, fabric_name: str, color: str = "white"):
    return {
        "stain_context": {"id": stain_id},
        "fabric_context": {
            "id": fabric_id,
            "name": fabric_name,
            "acid_safe": fabric_id in {"F1", "F2", "F5", "F6"},
            "enzyme_safe": fabric_id in {"F1", "F2", "F5", "F6"},
            "can_oxygen": fabric_id in {"F1", "F2", "F5", "F6"},
            "can_bleach": fabric_id == "F1",
        },
        "chemicals": [],  # empty Neo4j — must hydrate from Protocol
        "tools": [],  # empty Neo4j — must hydrate from Protocol
        "garment_color": color,
    }


def test_all_protocols_registered():
    assert len(PROTOCOL_BUILDERS) >= 70
    for sid in PROTOCOL_BUILDERS:
        assert has_protocol(sid)


def test_fallback_tools_when_no_protocol():
    from protocol import apply_protocol_to_graph

    g = {
        "stain_context": {"id": "S_UNKNOWN_FAKE"},
        "fabric_context": {"id": "F1", "name": "Cotton"},
        "chemicals": [],
        "tools": [],
    }
    out = apply_protocol_to_graph(g, entities={"fabric_type": "cotton"})
    assert out.get("tools"), "fallback tools required"
    assert out.get("fallback_tools") is True
    assert any(t.get("id") == "T_CLOTH" for t in out["tools"])


def test_new_v10_stains_in_builders():
    for sid in ("S_DOENJANG", "S_GOCHUJANG", "S_PERSIMMON", "S_CRAYON", "S_SOFTENER_SPOT"):
        assert has_protocol(sid)
        out = apply_protocol_to_graph(
            {
                "stain_context": {"id": sid},
                "fabric_context": {"id": "F1", "name": "Cotton", "enzyme_safe": True, "acid_safe": True, "can_oxygen": True},
                "chemicals": [],
                "tools": [],
                "garment_color": "white",
            },
            entities={"stain_id": sid, "fabric_type": "cotton", "garment_color": "white"},
        )
        assert out.get("tools") and out.get("chemicals"), sid


def test_acetate_fabric_flag_blocks_acetone_path():
    from protocol import _fabric_flags

    flags = _fabric_flags(
        {"fabric_context": {"id": "F11", "name": "Acetate", "acid_safe": False, "enzyme_safe": False}},
        {"fabric_type": "acetate"},
    )
    assert flags.get("is_acetate")
    assert flags.get("no_acetone")
    assert flags.get("no_oxygen")



def test_seed_rows_cover_all_protocols():
    tools = {r["id"]: r["tools"] for r in seed_tool_link_rows()}
    chems = {r["id"]: r["chems"] for r in seed_chem_link_rows()}
    for sid in PROTOCOL_BUILDERS:
        assert sid in tools and tools[sid], f"missing tools seed {sid}"
        assert sid in chems and chems[sid], f"missing chems seed {sid}"


def test_matrix_cotton_never_empty_tools_or_chems():
    failures = []
    for sid in sorted(PROTOCOL_BUILDERS):
        g = _graph(sid, "F1", "Cotton", "white")
        out = apply_protocol_to_graph(
            g,
            entities={"stain_id": sid, "fabric_type": "cotton", "garment_color": "white", "_raw": "면"},
        )
        tools = out.get("tools") or []
        chems = out.get("chemicals") or []
        tids = {t.get("id") for t in tools}
        codes = [c.get("code") for c in chems]
        if not tools:
            failures.append(f"{sid}: tools empty")
        if not chems:
            failures.append(f"{sid}: chemicals empty")
        # howto must not stay as stub-only for spray/timer when present
        for t in tools:
            uf = str(t.get("use_for_ko") or "")
            if t.get("id") in {"T_SPRAY", "T_TIMER", "T_SOAK_BIN"} and uf in {"(런타임)", ""}:
                failures.append(f"{sid}: {t.get('id')} howto not rewritten")
        # required ids from collector must be present
        from protocol import build_protocol

        proto = build_protocol(out, entities={"stain_id": sid, "fabric_type": "cotton", "garment_color": "white"})
        if proto:
            for tid in collect_required_tool_ids(proto):
                if tid not in tids:
                    failures.append(f"{sid}: missing required tool {tid}")
    assert not failures, "\n".join(failures[:40])


def test_rust_has_x2_gloves_timer():
    out = apply_protocol_to_graph(
        _graph("S_RUST", "F1", "Cotton"),
        entities={"stain_id": "S_RUST", "fabric_type": "cotton", "garment_color": "white"},
    )
    codes = [c["code"] for c in out["chemicals"]]
    tids = {t["id"] for t in out["tools"]}
    assert "X2" in codes
    assert "T_GLOVE_NITRILE" in tids
    assert "T_TIMER" in tids
    x2 = next(c for c in out["chemicals"] if c["code"] == "X2")
    assert "장갑" in (x2.get("dilution_ko") or "") or "2–3%" in (x2.get("dilution_ko") or "")


def test_cooking_oil_has_spray_timer():
    out = apply_protocol_to_graph(
        _graph("S_COOKING_OIL", "F1", "Cotton"),
        entities={"stain_id": "S_COOKING_OIL", "fabric_type": "cotton"},
    )
    tids = {t["id"] for t in out["tools"]}
    codes = [c["code"] for c in out["chemicals"]]
    assert "T_SPRAY" in tids
    assert "T_TIMER" in tids
    assert "D2" in codes
    assert "N3" in codes


def test_blood_has_ppe():
    for sid in ("S_BLOOD_FRESH", "S_BLOOD_DRY"):
        out = apply_protocol_to_graph(
            _graph(sid, "F1", "Cotton"),
            entities={"stain_id": sid, "fabric_type": "cotton"},
        )
        tids = {t["id"] for t in out["tools"]}
        assert "T_GLOVE_NITRILE" in tids, sid
        assert "T_MASK" in tids, sid


def test_gum_wax_equipment():
    gum = apply_protocol_to_graph(
        _graph("S_GUM", "F1", "Cotton"),
        entities={"stain_id": "S_GUM", "fabric_type": "cotton"},
    )
    wax = apply_protocol_to_graph(
        _graph("S_CANDLE_WAX", "F1", "Cotton"),
        entities={"stain_id": "S_CANDLE_WAX", "fabric_type": "cotton"},
    )
    assert "T_TIMER" in {t["id"] for t in gum["tools"]}
    assert "A2" in [c["code"] for c in gum["chemicals"]] or "D2" in [c["code"] for c in gum["chemicals"]]
    assert "T_STEAM_IRON" in {t["id"] for t in wax["tools"]}
    iron = next(t for t in wax["tools"] if t["id"] == "T_STEAM_IRON")
    assert "왁스" in iron["use_for_ko"] or "흡수지" in iron["use_for_ko"]


def test_silk_blocks_aggressive_chems():
    out = apply_protocol_to_graph(
        _graph("S_RUST", "F4", "Silk"),
        entities={"stain_id": "S_RUST", "fabric_type": "silk"},
    )
    codes = [c["code"] for c in out["chemicals"]]
    # X2 must not remain active on silk path
    assert "X2" not in codes


def test_chem_meta_dilutions_not_thin():
    thin_markers = ("병 안내", "theo nhãn", "per label", "병·경로")
    critical = ["D1", "D2", "X1", "X2", "N1", "N2", "A1", "B2", "E1"]
    for code in critical:
        d = CHEM_META[code].get("dilution_ko") or ""
        assert len(d) >= 20, f"{code} dilution too short: {d!r}"
        if code in {"X2", "B2", "D1"}:
            assert any(k in d for k in ("장갑", "PPE", "혼합", "환기", "니트릴")), code


def test_glove_chems_documented():
    assert "X2" in GLOVE_CHEMS and "B2" in GLOVE_CHEMS
    assert "S_BLOOD_FRESH" in BIOHAZARD_STAINS


def test_empty_neo4j_still_answers():
    """The original P0 bug: empty tools[] → 해당 없음. Must not happen."""
    out = apply_protocol_to_graph(
        _graph("S_RED_WINE", "F1", "Cotton"),
        entities={"stain_id": "S_RED_WINE", "fabric_type": "cotton", "garment_color": "white"},
    )
    assert out["tools"]
    assert out["chemicals"]
    assert any(t["id"] == "T_SPRAY" for t in out["tools"])
    assert any(c["code"] == "A3" for c in out["chemicals"])


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            fn()
            print("OK", name)
        except Exception as e:
            failed += 1
            print("FAIL", name, e)
    raise SystemExit(1 if failed else 0)
