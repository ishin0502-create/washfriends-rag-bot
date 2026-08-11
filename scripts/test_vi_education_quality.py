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
    # Korean particles after Cap code (common LLM output)
    ko2 = shop_speak_ko("Cap1과 블롯. Cap1–2: 안경 닦듯. E1 침지.")
    assert "Cap" not in ko2
    assert "약하게" in ko2 or "흡수" in ko2
    assert "슈퍼" in ko2 or "효소" in ko2


def test_owner_chem_line_ko_has_buy():
    from chem_owner_vi import owner_chem_line, collect_owner_chem_lines

    line = owner_chem_line("E1", "ko", {"code": "E1", "name_ko": "효소(프로테아제)"})
    assert "구매" in line or "슈퍼" in line
    assert "희석" in line or "사용" in line
    lines = collect_owner_chem_lines([{"code": "E1"}, {"code": "N2"}], "ko")
    assert any("소금" in x or "N2" not in x for x in lines)
    assert any("슈퍼" in x or "마트" in x for x in lines)


def test_ko_blood_compact_and_wine_named():
    from graphrag_engine import _blood_stain_mentioned, _named_laundry_stain, _offline_stain_graph

    assert _blood_stain_mentioned("피묻은 옷은 어떻게 세탁하나요?")
    assert _blood_stain_mentioned("피 묻은 옷")
    assert not _blood_stain_mentioned("커피 묻은 옷")
    assert not _blood_stain_mentioned("옷에 와인이 묻었는데 어떻게 지우나요?")
    assert _named_laundry_stain("옷에 와인이 묻었는데 어떻게 지우나요?")
    assert _named_laundry_stain("옷에 김치국물이 묻었어. 어떻게 세탁하는지?")
    wine = _offline_stain_graph("S_RED_WINE")
    assert wine.get("stain_context", {}).get("id") == "S_RED_WINE"
    assert "식초" in str(wine["stain_context"].get("fresh_path_ko") or "")
    kimchi = _offline_stain_graph("S_KIMCHI")
    assert "주방세제" in str(kimchi["stain_context"].get("fresh_path_ko") or "")
    blood = _offline_stain_graph("S_BLOOD_FRESH")
    assert "소금" in str(blood["stain_context"].get("fresh_path_ko") or "")


def test_blood_protocol_has_salt_before_enzyme():
    from protocol import PROTOCOL_BUILDERS

    p = PROTOCOL_BUILDERS["S_BLOOD_FRESH"]()
    chems = [s.chem for s in p.steps if getattr(s, "chem", None)]
    assert "N2" in chems
    assert "E1" in chems
    assert chems.index("N2") < chems.index("E1")


def test_enforce_stain_education_blood_ko():
    from graphrag_engine import _enforce_stain_education

    bad = (
        "(1) 피 얼룩 (2) 흰천 (3) Cap1 (4) 효소(프로테아제) 세제 라벨 희석 "
        "(5) 찬물 (6) 건조"
    )
    g = {
        "graph": {
            "_owner_stain_id": "S_BLOOD_FRESH",
            "force_guide": "약~중간(흡수·찍기) — 안경 닦듯 가볍게",
            "execution_path": "(2) 찬물 헹굼 (3) 소금 15–30분 (4) 효소",
            "chem_owner_lines": [
                "「효소(프로테아제)」 — 매장: 슈퍼 enzyme — 구매: 슈퍼/마트 — 희석·사용: 찬물 침지 15–30분",
                "「소금」 — 구매: 슈퍼/마트 — 희석·사용: 찬물 1L에 소금 큰술 2",
            ],
            "stain_context": {},
        }
    }
    out = _enforce_stain_education(bad, g, "ko")
    assert "소금" in out
    assert "슈퍼" in out or "마트" in out
    assert "힘" in out or "약" in out or "흡수" in out


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
