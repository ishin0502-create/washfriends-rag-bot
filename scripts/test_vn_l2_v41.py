# -*- coding: utf-8 -*-
"""VN L2 v41 — specialty motions, tips, binds, language purity."""
from __future__ import annotations

from reply_lang import detect_reply_lang, reply_language_leaks
from stain_hard_bind import bind_vn_specialty_stain
from owner_hand_motions import build_hand_motions, HAND_MOTIONS_EN
from owner_mid_blocks_v40 import block_vn_tips, COMPOUND_STAINS
from owner_answer_clarity import inject_clarity_into_answer
from protocol import PROTOCOL_BUILDERS
from education_vn_l2_v41 import NEW_VN_STAINS_V41, COMPOUND_VN_NEW


def test_seed_and_protocols():
    ids = {r["id"] for r in NEW_VN_STAINS_V41}
    assert len(ids) == 11
    for sid in ids:
        assert sid in PROTOCOL_BUILDERS
        p = PROTOCOL_BUILDERS[sid]()
        assert p.stain_id == sid
        assert p.why_ko and p.why_vi


def test_motions_ko_vi_en_language_pure():
    for sid in (
        "S_FISH_SAUCE",
        "S_VN_MANGOSTEEN",
        "S_VN_DURIAN",
        "S_VN_BANH_XEO",
        "S_VN_NUOC_CHAM",
    ):
        ko = build_hand_motions(sid, "ko")
        vi = build_hand_motions(sid, "vi")
        en = build_hand_motions(sid, "en")
        assert ko and "Step" in ko
        assert vi and "Bước" in vi
        assert en and "Step" in en
        assert not reply_language_leaks(ko, "ko")
        assert not reply_language_leaks(vi, "vi")
        # EN must not leak Hangul / heavy VI structure
        assert not reply_language_leaks(en, "en")
        assert "【담금" not in en and "【Kiểm" not in en


def test_hand_motions_en_map():
    assert "S_VN_MANGOSTEEN" in HAND_MOTIONS_EN
    assert "S_FISH_SAUCE" in HAND_MOTIONS_EN


def test_compound_includes_vn():
    for sid in COMPOUND_VN_NEW:
        assert sid in COMPOUND_STAINS


def test_vn_tips_language():
    tips_ko = block_vn_tips("S_FISH_SAUCE", "ko")
    tips_vi = block_vn_tips("S_FISH_SAUCE", "vi")
    tips_en = block_vn_tips("S_FISH_SAUCE", "en")
    assert tips_ko and "냄새" in tips_ko[0]
    assert tips_vi and "mùi" in tips_vi[0].lower()
    assert tips_en and "Odor" in tips_en[0]
    assert not reply_language_leaks("\n".join(tips_ko), "ko")
    assert not reply_language_leaks("\n".join(tips_vi), "vi")
    assert not reply_language_leaks("\n".join(tips_en), "en")


def test_hard_binds():
    cases = [
        ("망고스틴 얼룩 어떻게 빼요?", "S_VN_MANGOSTEEN"),
        ("Ao bi mang cut lam sao xu ly?", "S_VN_MANGOSTEEN"),
        ("How to remove mangosteen stain?", "S_VN_MANGOSTEEN"),
        ("두리안 냄새 옷에 배었어요", "S_VN_DURIAN"),
        ("Vet sau rieng tren ao", "S_VN_DURIAN"),
        ("반쎄오 기름 묻었어요", "S_VN_BANH_XEO"),
        ("Nuoc cham do ra ao", "S_VN_NUOC_CHAM"),
        ("Sa te oil on shirt", "S_VN_SA_TE"),
        ("코코넛 오일 얼룩", "S_VN_COCONUT_OIL"),
    ]
    for q, expect in cases:
        got = bind_vn_specialty_stain(q)
        assert got == expect, f"{q!r} -> {got} want {expect}"


def test_detect_lang_for_vn_specialty():
    assert detect_reply_lang("망고스틴 빼는 법") == "ko"
    assert detect_reply_lang("Ao bi mang cut lam sao?") == "vi"
    assert detect_reply_lang("How to remove mangosteen stain on cotton?") == "en"


def test_inject_clarity_lang_pure():
    from owner_hand_motions import build_hand_motions as _bhm

    gloss = {
        "ko": "◆ 【용어】\n효소 = 단백질 분해\n",
        "vi": "◆ 【Thuật ngữ】\nEnzyme = phân hủy protein\n",
        "en": "◆ 【Glossary】\nEnzyme = breaks protein\n",
    }
    for lang, q_hint in (("ko", "망고스틴"), ("vi", "mang cut"), ("en", "mangosteen")):
        sid = "S_VN_MANGOSTEEN"
        proto = PROTOCOL_BUILDERS[sid]()
        why = proto.why_ko if lang == "ko" else proto.why_vi if lang == "vi" else "[Why] strong purple dye"
        body = gloss[lang] + "\n" + why + "\n" + _bhm(sid, lang)
        g = {
            "stain": {"id": sid},
            "entities": {"stain_id": sid, "lang": lang},
            "protocol": proto.to_dict(),
            "chemicals": [{"code": "A1"}, {"code": "B1"}],
            "_raw": q_hint,
        }
        out = inject_clarity_into_answer(body, graph=g, level="L2", grade=2, lang=lang)
        assert out
        leaks = reply_language_leaks(out, lang)
        assert not leaks, f"lang={lang} leaks={leaks}"


if __name__ == "__main__":
    test_seed_and_protocols()
    test_motions_ko_vi_en_language_pure()
    test_hand_motions_en_map()
    test_compound_includes_vn()
    test_vn_tips_language()
    test_hard_binds()
    test_detect_lang_for_vn_specialty()
    test_inject_clarity_lang_pure()
    print("vn_l2_v41 ok")
