"""Lightweight tests for response_cache (no Neo4j required)."""
from response_cache import (
    _normalize_key,
    _similarity,
    _should_store,
    _topics_compatible,
)


def test_normalize():
    assert _normalize_key("Vết Máu Tươi!") == "vet mau tuoi"
    assert _normalize_key("  Ca phe   tren cotton  ") == "ca phe tren cotton"


def test_similarity():
    a = _normalize_key("vet mau tuoi tren cotton")
    b = _normalize_key("vet mau tuoi tren vai cotton")
    assert _similarity(a, b) >= 0.85


def test_topic_guard():
    coffee_cotton = _normalize_key("ca phe tren cotton")
    coffee_silk = _normalize_key("ca phe tren lua")
    assert _topics_compatible(coffee_cotton, coffee_cotton)
    assert not _topics_compatible(coffee_cotton, coffee_silk)


def test_should_store():
    assert not _should_store("short")
    assert not _should_store("Xin loi, toi khong tim thay thong tin cho cau hoi nay.")
    assert _should_store("1) Xa nuoc lanh. 2) Ngam enzyme E1 30 phut. " * 3)


if __name__ == "__main__":
    test_normalize()
    test_similarity()
    test_topic_guard()
    test_should_store()
    print("OK")
