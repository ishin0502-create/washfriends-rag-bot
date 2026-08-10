# -*- coding: utf-8 -*-
"""VI education quality gates (lang, chem follow-up, shop labels, no GIAO DUC)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")


def test_detect_reply_lang_ascii_vi():
    from reply_lang import detect_reply_lang

    cases = [
        ("hoa chat gi", "vi"),
        ("Enzyme protease la hoa chat gi", "vi"),
        ("protease la gi", "vi"),
        ("chat lieu cotton", "vi"),
        ("chat non xu ly", "vi"),
        ("Enzyme protease là hóa chất gì", "vi"),
        ("nuoc tieu xu ly", "vi"),
        ("sua bot tre em", "vi"),
    ]
    for q, expect in cases:
        got = detect_reply_lang(q)
        assert got == expect, f"{q!r} -> {got} want {expect}"


def test_session_lang_sticky():
    from reply_lang import detect_reply_lang

    # Without sticky, short English-looking chem Q still VI via hints;
    # with sticky after VI turn, pure latin stays VI
    assert detect_reply_lang("ok", session_lang="vi") == "vi"
    assert detect_reply_lang("E1", session_lang="vi") == "vi"


def test_chem_explain_e1_vi():
    from chem_explain import try_explain_chem

    ans = try_explain_chem("Enzyme protease la hoa chat gi", ["E1"], lang="vi")
    assert ans, "must explain"
    assert "Sorry" not in ans
    assert "could not find" not in ans.lower()
    low = ans.lower()
    assert "enzyme" in low or "đạm" in ans or "dam" in low
    assert "siêu thị" in low or "siêu" in ans or "cửa hàng" in low or "Nước giặt" in ans or "nước giặt" in low
    assert "Enzyme protease" not in ans.split("\n")[0] or "phân giải" in ans
    assert "Không trả lời bằng tên tiếng Anh" not in ans
    assert "Cap" not in ans


def test_chem_explain_without_prefer_still_matches():
    from chem_explain import try_explain_chem

    ans = try_explain_chem("protease la gi", [], lang="vi")
    assert ans and "phân giải đạm" in ans


def test_chem_meta_owner_vi_not_english_only():
    from protocol import CHEM_META

    e1 = CHEM_META["E1"]
    assert "Enzyme protease" != e1.get("name_vi")
    assert "phân giải" in (e1.get("name_vi") or "") or "đạm" in (e1.get("name_vi") or "")
    assert e1.get("shop_name_vi")
    assert "Javel" in (CHEM_META["B2"].get("name_vi") or "") or "Javel" in (CHEM_META["B2"].get("shop_name_vi") or "")


def test_protocol_why_no_giao_duc():
    from protocol import PROTOCOL_BUILDERS

    bad = []
    for sid, builder in PROTOCOL_BUILDERS.items():
        p = builder()
        w = p.why_vi or ""
        if "GIAO DUC" in w.upper().replace(" ", ""):
            bad.append(sid)
        if "GIAO DUC" in w:
            bad.append(sid)
    assert not bad, f"GIAO DUC remains in {bad[:10]}"


def test_render_chemicals_has_shop_name():
    from protocol import apply_protocol_to_graph

    out = apply_protocol_to_graph(
        {
            "stain_context": {"id": "S_VOMIT"},
            "fabric_context": {
                "id": "F1",
                "name": "Cotton",
                "enzyme_safe": True,
                "acid_safe": True,
                "can_oxygen": True,
            },
            "chemicals": [],
            "tools": [],
            "garment_color": "white",
        },
        entities={"stain_id": "S_VOMIT", "fabric_type": "cotton", "garment_color": "white"},
    )
    chems = out.get("chemicals") or []
    assert chems
    e1 = next((c for c in chems if c.get("code") == "E1"), None)
    assert e1, "vomit should include E1"
    assert e1.get("shop_name_vi")
    assert e1.get("name_vi") != "Enzyme protease"


def test_session_chem_followup_path():
    from user_session import clear_session, get_session, set_pending_treatment
    from chem_explain import looks_like_chem_question, try_explain_chem

    clear_session("test", "u1")
    set_pending_treatment(
        "test",
        "u1",
        stain_id="S_VOMIT",
        lang="vi",
        raw_question="chat non cotton",
        last_chem_codes=["E1", "A3"],
    )
    sess = get_session("test", "u1")
    assert sess.get("lang") == "vi"
    assert "E1" in sess.get("last_chem_codes")
    q = "Enzyme protease la hoa chat gi"
    assert looks_like_chem_question(q)
    ans = try_explain_chem(q, sess["last_chem_codes"], lang="vi")
    assert "Sorry" not in ans
    clear_session("test", "u1")


def test_shop_speak_strips_cap_ppe():
    from vi_text_canon import shop_speak_ko, shop_speak_vi

    vi = shop_speak_vi("Cap1 thấm. Cap2 cạo. Đúng PPE. E1 ngâm. CẤM lụa/len cùng ngâm với Javel.")
    assert "Cap" not in vi
    assert "PPE" not in vi
    assert "enzyme" in vi.lower() or "đạm" in vi
    assert "Javel" in vi
    ko = shop_speak_ko("Cap1 흡수. PPE 필수.")
    assert "Cap" not in ko
    assert "PPE" not in ko


def test_sanitize_strips_giao_duc():
    from vi_text_canon import sanitize_education_vi_fields

    g = sanitize_education_vi_fields(
        {"stain_context": {"why_vi": "GIAO DUC: Chat non = protein. Enzyme protease. Cap2 + PPE."}}
    )
    w = g["stain_context"]["why_vi"]
    assert "GIAO DUC" not in w
    assert "Chất nôn" in w or "chất nôn" in w
    assert "Cap" not in w
    assert "PPE" not in w


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
