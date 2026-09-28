# -*- coding: utf-8 -*-
from care_label_quiz import build_care_symbol_deck, build_mcq_item, build_open_item
from care_symbol_svg import ensure_assets, svg_for
from learning_mode import try_handle_mode_or_quiz
from learning_quiz import _match_accept
from owner_qa_log import set_quiz


def test_assets_and_svg():
    d = ensure_assets()
    assert (d / "symbol_09.svg").exists()
    assert (d / "symbol_09.png").exists()
    assert "svg" in svg_for(9)
    assert b"PNG" in (d / "symbol_09.png").read_bytes()[:8]


def test_mcq_and_open():
    m = build_mcq_item(9, "ko")
    assert m["kind"] == "mcq"
    assert "1)" in m["q"]
    assert _match_accept(str(m["answer_index"] + 1), m["accept"])
    o = build_open_item(9, "ko")
    assert o["kind"] == "open"
    assert _match_accept("물세탁 금지", o["accept"])


def test_deck_mixed():
    deck = build_care_symbol_deck("ko", size=6, mix="mixed")
    assert len(deck) == 6
    kinds = {x["kind"] for x in deck}
    assert "mcq" in kinds and "open" in kinds


def test_zalo_command_starts_quiz():
    set_quiz("test-care-user", None)
    reply = try_handle_mode_or_quiz("test-care-user", "기호퀴즈")
    assert reply
    assert "기호" in reply or "세탁표시" in reply or "학습" in reply


def test_show_dry_clean_symbols():
    from care_label_quiz import match_show_symbol_ids, try_handle_show_symbols, pop_queued_symbol_images

    ids = match_show_symbol_ids("드라이클리닝 기호 보여줘")
    assert ids and 6 in ids and 25 in ids
    reply = try_handle_show_symbols("u-show", "드라이클리닝 기호 보여줘")
    assert reply and "드라이" in reply
    paths = pop_queued_symbol_images("u-show")
    assert len(paths) >= 3
