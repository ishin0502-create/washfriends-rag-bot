# -*- coding: utf-8 -*-
"""Local smoke for VI chem follow-up (no OpenAI/network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from reply_lang import detect_reply_lang
from user_session import clear_session, set_pending_treatment, get_session
from chem_explain import try_explain_chem, looks_like_chem_question
from protocol import apply_protocol_to_graph, CHEM_META


def main():
    failed = 0
    q1 = "chat lieu cotton mau trang. Vet chat non xu ly the nao?"
    assert detect_reply_lang(q1) == "vi"

    clear_session("zalo", "smoke_vi12")
    # Simulate after vomit SOP
    g = apply_protocol_to_graph(
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
    codes = [c["code"] for c in (g.get("chemicals") or [])]
    set_pending_treatment(
        "zalo",
        "smoke_vi12",
        stain_id="S_VOMIT",
        lang="vi",
        raw_question=q1,
        last_chem_codes=codes,
    )
    q2 = "Enzyme protease la hoa chat gi"
    assert detect_reply_lang(q2, session_lang="vi") == "vi"
    assert looks_like_chem_question(q2)
    ans = try_explain_chem(q2, get_session("zalo", "smoke_vi12")["last_chem_codes"], lang="vi")
    print(ans)
    if not ans or "Sorry" in ans or "could not find" in ans.lower():
        failed += 1
        print("FAIL chem explain")
    if CHEM_META["E1"]["name_vi"] == "Enzyme protease":
        failed += 1
        print("FAIL E1 still english-only")
    e1 = next(c for c in g["chemicals"] if c["code"] == "E1")
    if not e1.get("shop_name_vi") or e1.get("name_vi") == "Enzyme protease":
        failed += 1
        print("FAIL shop name", e1)
    clear_session("zalo", "smoke_vi12")
    print("RESULT", "PASS" if failed == 0 else f"FAIL:{failed}")
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
