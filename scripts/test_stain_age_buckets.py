# -*- coding: utf-8 -*-
"""Unit tests for stain age buckets (fresh / dried / hard framing)."""
from stain_age_buckets import (
    DRIED_PATH_KO,
    apply_stain_age_buckets,
    detect_stain_age,
    seed_dried_path_rows,
)


def test_detect_fresh():
    assert detect_stain_age("방금 와인 묻었어") == "fresh"
    assert detect_stain_age("just spilled coffee") == "fresh"


def test_detect_dried():
    assert detect_stain_age("마른 와인 얼룩 지우는 법") == "dried"
    assert detect_stain_age("이미 마른 케첩") == "dried"
    assert detect_stain_age("dried wine stain") == "dried"
    assert detect_stain_age("오래된 와인이 옷에 묻어있는데 어떻게 해야 지울수 있나요?") == "dried"
    assert detect_stain_age("오래된 커피 얼룩") == "dried"
    assert detect_stain_age("예전에 묻은 것 같은 와인") == "dried"
    assert detect_stain_age("잘 지워지지 않는 오염이 있다") == "dried"
    assert detect_stain_age("묵은 케첩 얼룩") == "dried"
    assert detect_stain_age("시간이 지난 소스 얼룩") == "dried"


def test_detect_hard():
    assert detect_stain_age("몇달 전 와인 열고착") == "hard"
    assert detect_stain_age("한달 전에 묻은 커피") == "hard"
    assert detect_stain_age("두세달 이상 된 것 같은 와인") == "hard"
    assert detect_stain_age("작년에 묻은 얼룩") == "hard"


def test_detect_unknown():
    assert detect_stain_age("와인 묻은 옷 어떻게 세탁해") == "unknown"


def test_apply_unknown_dual_frame():
    g = {
        "stain_context": {
            "id": "S_RED_WINE",
            "fresh_path_ko": "신선 경로",
            "dried_path_ko": "짧음",
            "group": "G3",
        }
    }
    out = apply_stain_age_buckets(g, "와인 묻은 옷 어떻게", {"stain_age": "unknown"})
    sc = out["stain_context"]
    assert sc["age_bucket"] == "unknown"
    assert "dried_path_ko" in sc["age_frame_ko"]
    assert "(1)" in sc["dried_path_ko"]
    assert "limit_path_ko" in sc
    assert "100%" in sc["limit_path_ko"]


def test_apply_dried_priority():
    g = {
        "stain_context": {
            "id": "S_KETCHUP",
            "fresh_path_ko": "신선",
            "dried_path_ko": "짧음",
        }
    }
    out = apply_stain_age_buckets(g, "마른 케첩", {"stain_age": "dried"})
    sc = out["stain_context"]
    assert sc["path_priority"] == "dried_path"
    assert sc["active_path_ko"] == sc["dried_path_ko"]
    assert "주방세제" in sc["dried_path_ko"]
    assert "15–30" in sc.get("soak_minutes_ko", "")


def test_hard_overrides_fresh_minutes():
    g = {
        "stain_context": {
            "id": "S_RED_WINE",
            "fresh_path_ko": "신선 5–15분",
            "dried_path_ko": "짧음",
            "contains_tannin": True,
        },
        "protocol": {
            "steps": [
                {"ko": "레드와인·신선 여부", "chem": "", "soak": False},
                {"ko": "식초 5–15분", "chem": "A3", "soak": True, "minutes_lo": 5, "minutes_hi": 15},
            ]
        },
        "tools": [
            {"id": "T_TIMER", "use_for_ko": "5–15분"},
            {"id": "T_SOAK_BIN", "use_for_ko": "5–15분 담금"},
            {"id": "T_BRUSH_SOFT", "use_for_ko": "솔"},
        ],
    }
    out = apply_stain_age_buckets(g, "두세달된 와인 자국", {"stain_age": "hard"})
    sc = out["stain_context"]
    assert sc["age_bucket"] == "hard"
    assert "path_lock_ko" in sc
    assert "15–30" in sc["soak_minutes_ko"]
    assert out["protocol_minutes_ko"] == "15–30분"
    assert "1시간 내" not in sc["success_rate_ko"]
    assert "100%" in sc["success_rate_ko"] or "불가" in sc["success_rate_ko"]
    soak = out["protocol"]["steps"][1]
    assert soak["minutes_lo"] == 15 and soak["minutes_hi"] == 30
    timer = next(t for t in out["tools"] if t["id"] == "T_TIMER")
    assert "15–30" in timer["use_for_ko"]
    assert "5–15분을 쓰지 말" in timer["use_for_ko"]
    assert not any(t.get("id") == "T_BRUSH_SOFT" for t in out["tools"])


def test_dried_overrides_fresh_success_rate():
    g = {
        "stain_context": {
            "id": "S_RED_WINE",
            "success_rate_ko": "1시간 내: 양호. 하룻밤·건조 후: 낮음.",
            "dried_path_ko": "짧음",
        }
    }
    out = apply_stain_age_buckets(g, "오래된 와인", {"stain_age": "dried"})
    sc = out["stain_context"]
    assert "1시간 내" not in sc["success_rate_ko"]
    assert "마른" in sc["success_rate_ko"] or "고착" in sc["success_rate_ko"]


def test_item_care_skipped():
    g = {
        "specialty_item_care": True,
        "stain_context": {"id": "I_CURTAIN", "group": "item_care", "dried_path_ko": "x"},
    }
    out = apply_stain_age_buckets(g, "마른 커튼", {})
    assert "age_bucket" not in (out.get("stain_context") or {})


def test_seed_rows():
    rows = seed_dried_path_rows()
    assert len(rows) >= 20
    wine = next(r for r in rows if r["id"] == "S_RED_WINE")
    assert "(1)" in wine["dried_path_ko"]
    assert "(1)" in wine["dried_path_vi"]


def test_priority_covers_high_freq():
    for sid in (
        "S_RED_WINE",
        "S_BLACK_COFFEE",
        "S_KETCHUP",
        "S_KIMCHI",
        "S_COOKING_OIL",
    ):
        assert sid in DRIED_PATH_KO
        assert DRIED_PATH_KO[sid].startswith("(1)")


def test_ko_edu_seed_syncs_dried():
    from ko_stain_education import seed_rows

    rows = {r["id"]: r for r in seed_rows()}
    assert "(1)" in rows["S_RED_WINE"]["dried_path_ko"]
    assert "장침지" in rows["S_RED_WINE"]["dried_path_ko"] or "식초" in rows["S_RED_WINE"]["dried_path_ko"]


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
