# -*- coding: utf-8 -*-
"""Tests for VI text canon + care-label routing helpers."""
from vi_text_canon import canon_vi_text, apply_vi_canon_to_graph


def test_canon_blood_why():
    raw = (
        "GIAO DUC: Mau tuoi = hemoglobin. Nuoc LANH. CAM say. "
        "Len/lua: KHONG enzyme. mat trai xa lanh."
    )
    out = canon_vi_text(raw)
    assert "GIAO DUC" not in out
    assert "[Tại sao]" in out
    assert "nước LẠNH" in out or "nước lạnh" in out.lower()
    assert "CẤM sấy" in out or "sấy" in out
    assert "mặt trái" in out
    assert "len/lụa" in out or "lụa" in out


def test_canon_graph_nested():
    g = {
        "stain_context": {
            "why_vi": "GIAO DUC: Ca phe den. giam 1:4. truoc say.",
            "fresh_path_vi": "Xa nuoc lanh mat trai.",
        }
    }
    out = apply_vi_canon_to_graph(g)
    sc = out["stain_context"]
    assert "GIAO DUC" not in sc["why_vi"]
    assert "giấm" in sc["why_vi"]
    assert "mặt trái" in sc["fresh_path_vi"]
    assert "nước lạnh" in sc["fresh_path_vi"]


def test_care_label_infer():
    import os

    os.environ.setdefault("OPENAI_API_KEY", "sk-test-local-dummy")
    from graphrag_engine import _infer_item_from_text

    samples = [
        "Cách đọc nhãn giặt trên quần áo?",
        "Cach doc nhan giat?",
        "Huong dan doc care label",
        "케어라벨 세탁표시",
    ]
    for q in samples:
        iid = _infer_item_from_text(q)
        assert iid == "I_CARE_LABEL", (q, iid)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("OK", name)
