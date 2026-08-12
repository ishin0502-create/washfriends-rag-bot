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


def test_polish_coffee_thin_and_vinegar_dup():
    from graphrag_engine import _polish_owner_ko_phrasing, _strip_misplaced_fresh_rescue

    raw = (
        "(1) 원단·두께 미확인시 얇음으로 약하게(흡수·찍기만), 표백 보류.\n"
        "(2) 흰 식초(식용 식초 약 5%)를 흰 식초(~5%): 식초 1 : 물 4로 타서.\n"
        "(4) 식초."
    )
    out = _polish_owner_ko_phrasing(raw)
    assert "얇음으로" not in out
    assert "(흡수·찍기만)(흡수·찍기만)" not in out
    assert "흰 식초(~5%): 식초" not in out
    with_rescue = (
        out
        + "\n\n1차 실패·마른 얼룩: 성공률 하락·잔여 가능을 고지한 뒤에만 2차 진행. 100% 약속 금지."
    )
    out2 = _strip_misplaced_fresh_rescue(
        with_rescue,
        {"graph": {"age_bucket": "unknown", "stain_context": {"age_bucket": "unknown"}}},
        "ko",
    )
    assert "1차 실패" not in out2
    kept = _strip_misplaced_fresh_rescue(
        with_rescue,
        {"graph": {"age_bucket": "dried", "stain_context": {"age_bucket": "dried"}}},
        "ko",
    )
    assert "1차 실패" in kept


def test_ko_blood_compact_and_wine_named():
    from graphrag_engine import _blood_stain_mentioned, _named_laundry_stain, _offline_stain_graph

    assert _blood_stain_mentioned("피묻은 옷은 어떻게 세탁하나요?")
    assert _blood_stain_mentioned("피 묻은 옷")
    assert _blood_stain_mentioned("면 티셔츠에 피 얼룩 어떻게 빼?")
    assert not _blood_stain_mentioned("커피 묻은 옷")
    assert not _blood_stain_mentioned("면 티셔츠에 방금 쏟은 블랙커피 얼룩 어떻게 빼?")
    assert not _blood_stain_mentioned("블랙커피 얼룩")
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


def test_infer_garment_color_ignores_stain_names():
    from graphrag_engine import _infer_garment_color

    assert _infer_garment_color("면 티셔츠에 방금 쏟은 블랙커피 얼룩") == ""
    assert _infer_garment_color("옷에 화이트와인 묻었어") == ""
    assert _infer_garment_color("흰 면 셔츠에 레드와인") == "white"
    assert _infer_garment_color("검정 면 티에 커피") == "black"


def test_polish_tannin_wine_kimchi_and_dried_path():
    from graphrag_engine import _polish_owner_ko_phrasing, _strip_misplaced_fresh_rescue

    wine = "분무기: 흰 식초(식용 식초 약 5%)을 식초 1 : 물 4로 희석."
    out = _polish_owner_ko_phrasing(wine)
    assert "을 식초" not in out
    assert "%)를" in out or "식초를" in out

    kimchi = "문지르기 금지. 주방세제 후 바깥→안 문지름."
    out_k = _polish_owner_ko_phrasing(kimchi)
    assert "문지름" not in out_k
    assert "찍어 바름" in out_k

    blood = (
        "건조 전 강광.\n"
        "1차 실패 시 2차 진행 가능 — 마른 얼룩은 dried_path로 진행."
    )
    polished = _polish_owner_ko_phrasing(blood)
    assert "dried_path" not in polished
    stripped = _strip_misplaced_fresh_rescue(
        polished,
        {"graph": {"age_bucket": "fresh", "stain_context": {"age_bucket": "fresh"}}},
        "ko",
    )
    assert "1차 실패" not in stripped
    assert "dried_path" not in stripped


def test_tannin_oxygen_if_white_and_unknown():
    from graphrag_engine import _enforce_stain_education

    wine_unknown = "(1) 레드와인 (2) 흰 천 (3) 약하게 (4) 흰 식초 1:4 (5) 찬물 (6) 강광"
    g_unknown = {
        "graph": {
            "_owner_stain_id": "S_RED_WINE",
            "garment_color": "",
            "stain_context": {"id": "S_RED_WINE", "contains_tannin": True},
            "chem_owner_lines": [],
        }
    }
    out_u = _enforce_stain_education(wine_unknown, g_unknown, "ko")
    assert "산소표백" in out_u
    assert "색 미확인 시 생략" in out_u

    wine_white = wine_unknown
    g_white = {
        "graph": {
            "_owner_stain_id": "S_RED_WINE",
            "garment_color": "white",
            "stain_context": {"id": "S_RED_WINE", "contains_tannin": True},
            "chem_owner_lines": [],
        }
    }
    out_w = _enforce_stain_education(wine_white, g_white, "ko")
    assert "흰옷 잔색" in out_w
    assert "산소표백" in out_w

    wine_color = wine_unknown
    g_color = {
        "graph": {
            "_owner_stain_id": "S_RED_WINE",
            "garment_color": "colored",
            "stain_context": {"id": "S_RED_WINE", "contains_tannin": True},
            "chem_owner_lines": [],
        }
    }
    out_c = _enforce_stain_education(wine_color, g_color, "ko")
    assert "산소표백" not in out_c

    coffee_already = wine_unknown + "\n흰/면 잔색: 산소표백(색 미확인 시 생략)."
    g_coffee = {
        "graph": {
            "_owner_stain_id": "S_BLACK_COFFEE",
            "stain_context": {"id": "S_BLACK_COFFEE", "contains_tannin": True},
            "chem_owner_lines": [],
        }
    }
    out_cf = _enforce_stain_education(coffee_already, g_coffee, "ko")
    assert out_cf.count("산소표백") == 1


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
