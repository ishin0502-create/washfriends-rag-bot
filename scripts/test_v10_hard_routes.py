# -*- coding: utf-8 -*-
"""Hard-route keyword checks for v10 (no OpenAI import)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")


def route_msg(msg: str) -> str:
    raw_n = msg.lower()
    user_message = msg
    if any(k in user_message for k in ("케첩", "켓찹", "케찹")):
        return "S_KETCHUP"
    if any(
        k in user_message
        for k in ("토마토소스", "토마토 소스", "파스타소스", "파스타 소스", "볼로네제", "미트소스")
    ) or "tomato sauce" in raw_n or "pasta sauce" in raw_n:
        return "S_TOMATO_SAUCE"
    if any(k in user_message for k in ("기름때", "그리즈", "그리스")) or "grease" in raw_n:
        return "S_GREASE"
    if any(k in user_message for k in ("된장", "된장찌개", "된장국")):
        return "S_DOENJANG"
    if any(k in user_message for k in ("고추장", "비빔장")):
        return "S_GOCHUJANG"
    if any(k in user_message for k in ("감물", "감즙", "감 얼룩", "홍시")):
        return "S_PERSIMMON"
    if any(k in user_message for k in ("크레용", "크레파스")):
        return "S_CRAYON"
    if any(k in user_message for k in ("유연제 얼룩", "유연제스팟", "유연제 스팟", "린스 얼룩")):
        return "S_SOFTENER_SPOT"
    return ""


cases = [
    ("면 셔츠에 토마토소스", "S_TOMATO_SAUCE"),
    ("케첩 묻었어요", "S_KETCHUP"),
    ("기름때 심해요", "S_GREASE"),
    ("된장찌개 국물", "S_DOENJANG"),
    ("고추장 비빔", "S_GOCHUJANG"),
    ("감물 얼룩", "S_PERSIMMON"),
    ("크레용", "S_CRAYON"),
    ("유연제 스팟", "S_SOFTENER_SPOT"),
]

failed = 0
for msg, expect in cases:
    got = route_msg(msg)
    ok = got == expect
    print(("OK" if ok else "FAIL"), repr(msg), "->", got)
    failed += 0 if ok else 1

# Also verify graphrag source contains the tomato branch
from pathlib import Path

src = Path(__file__).resolve().parents[1].joinpath("graphrag_engine.py").read_text(encoding="utf-8")
assert 'entities["stain_id"] = "S_TOMATO_SAUCE"' in src
assert 'entities["stain_id"] = "S_GREASE"' in src
assert 'entities["stain_id"] = "S_DOENJANG"' in src
print("OK source_contains_routes")
raise SystemExit(failed)
