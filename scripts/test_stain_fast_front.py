# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from stain_fast_front import bind_fast_stain_id, try_fast_front_card


def test_commands_not_bound():
    for t in ("교육", "모드", "메뉴", "hi", "xin chào"):
        assert bind_fast_stain_id(t) is None, t


def test_coffee_blood_fast_card():
    assert bind_fast_stain_id("면 셔츠에 커피 얼룩") == "S_BLACK_COFFEE"
    card = try_fast_front_card("면 셔츠에 커피 얼룩이요")
    assert card
    assert "지금 바로" in card
    assert "이어서" in card
    assert bind_fast_stain_id("Mau tuoi tren ao cotton") == "S_BLOOD_FRESH"
    vi = try_fast_front_card("Mau tuoi tren ao cotton")
    assert vi and "Làm ngay" in vi


def test_course_word_not_stain():
    assert bind_fast_stain_id("다음") is None


if __name__ == "__main__":
    test_commands_not_bound()
    test_coffee_blood_fast_card()
    test_course_word_not_stain()
    print("ok")
