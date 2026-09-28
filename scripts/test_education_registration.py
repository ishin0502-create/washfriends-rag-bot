# -*- coding: utf-8 -*-
"""Parse registration messages for education bot deny path."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def test_parse_franchise_ko():
    from education_registration import parse_registration

    p = parse_registration(
        "가맹점\n매장 이름: 워시프렌즈 1호\n본인 이름: 김점주\n역할: 점주"
    )
    assert p is not None
    assert p["client_kind"] == "franchise"
    assert "워시프렌즈" in p["store_name"]
    assert p["person_name"] == "김점주"
    assert p["person_role"] == "owner"


def test_parse_general_staff():
    from education_registration import parse_registration

    p = parse_registration(
        "일반세탁소\n매장 이름: Happy Laundry\n본인 이름: Lan\n역할: 직원"
    )
    assert p is not None
    assert p["client_kind"] == "general"
    assert p["person_role"] == "staff"


def test_prompt_no_ask_zalo_id():
    from education_registration import registration_prompt

    for lang in ("ko", "vi", "en"):
        t = registration_prompt(lang)
        assert "숫자 ID" in t or "numeric ID" in t or "ID số" in t or "Zalo ID" in t


def test_unrelated_not_parsed():
    from education_registration import parse_registration

    assert parse_registration("커피 얼룩 어떻게 빼요?") is None


if __name__ == "__main__":
    test_parse_franchise_ko()
    test_parse_general_staff()
    test_prompt_no_ask_zalo_id()
    test_unrelated_not_parsed()
    print("OK education_registration")
