# -*- coding: utf-8 -*-
"""Professional dry-cleaning machine Q&A gate (HQ dry_clean_machine flag).

- OFF: equip-then-train + HQ inquiry (no PROG numbers).
- ON: ISO P/F/W + safe checklist; optional steps from data/realstar_courses.json only.
Never invent button/PROG numbers.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from dry_clean_capability import lock_message, unlock_message, resolve_has_machine

_DATA = Path(__file__).resolve().parent / "data" / "realstar_courses.json"

_MACHINE_Q = re.compile(
    r"(리어스타|real\s*-?\s*star|realstar|"
    r"드라이\s*(클리닝\s*)?기계|드라이기|퍼클로|PCE|"
    r"dry\s*-?\s*clean(ing)?\s*(machine|prog|program|course)|"
    r"máy\s*giặt\s*khô|may\s*giat\s*kho|"
    r"\bPROG\b|프로그램\s*(번호|코스)|몇\s*번\s*(버튼|코스|프로그램)|"
    r"버튼\s*(몇|번호)|코스\s*(몇|번호|선택)|"
    r"용제\s*(넣|선택)|솔벤트)",
    re.I,
)


def is_professional_machine_question(text: str) -> bool:
    return bool(_MACHINE_Q.search(text or ""))


def _load_courses() -> list[dict[str, Any]]:
    if not _DATA.is_file():
        return []
    try:
        raw = json.loads(_DATA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"[REALSTAR] courses load skip: {e}")
        return []
    items = raw.get("courses") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []
    return [c for c in items if isinstance(c, dict)]


def _match_course(msg: str, courses: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    t = (msg or "").lower()
    for c in courses:
        keys = c.get("match") or c.get("keywords") or []
        if not isinstance(keys, list):
            continue
        for k in keys:
            ks = str(k or "").strip().lower()
            if ks and ks in t:
                return c
    return None


def _steps_from_course(course: dict[str, Any], lang: str) -> list[str]:
    key = {"ko": "steps_ko", "en": "steps_en", "vi": "steps_vi"}.get(lang, "steps_vi")
    steps = course.get(key) or course.get("steps") or []
    if not isinstance(steps, list):
        return []
    out = [str(s).strip() for s in steps if str(s).strip()]
    # Reject steps that look like invented bare PROG numbers without context from HQ file
    return out


def _safe_ops_card(lang: str, code_hint: str = "") -> str:
    hint = f" (라벨 {code_hint})" if code_hint else ""
    if lang == "ko":
        return (
            f"◆ 【전문 드라이 기계 · 작업 전】{hint}\n"
            "1) 케어 라벨: P / F / W / X 확인 (X·물세탁 금지는 습식 투입 금지)\n"
            "2) 이염·장식·가죽·모피 → 매니저 확인\n"
            "3) 용제·PROG는 **매장 기종 매뉴얼 / 본사 코스표**만 사용 "
            "(임의 번호 금지)\n"
            "4) 약공정(밑줄)·이중 밑줄은 초급 단독 금지 → 매니저와\n"
            "5) 종료 후 라벨·외관 QC, 이상 시 본사\n"
            "\n"
            "본사에서 Realstar 코스표를 `data/realstar_courses.json`에 넣으면 "
            "해당 단계가 여기에 이어서 안내됩니다."
        )
    if lang == "en":
        return (
            f"◆ 【Professional dry machine · before run】{hint}\n"
            "1) Check label P / F / W / X (X / no-wash → do not wet-process)\n"
            "2) Bleed risk / trim / leather / fur → ask manager\n"
            "3) Solvent & PROG only from **store manual / HQ course sheet** "
            "(no invented numbers)\n"
            "4) Mild / double-underline: beginners with manager only\n"
            "5) QC after cycle; escalate issues to HQ\n"
            "\n"
            "When HQ adds Realstar courses to `data/realstar_courses.json`, "
            "those steps append here."
        )
    return (
        f"◆ 【Máy giặt khô · trước khi chạy】{hint}\n"
        "1) Đọc nhãn P / F / W / X (X / cấm nước → không giặt ướt)\n"
        "2) Lem màu / trang trí / da / lông → hỏi quản lý\n"
        "3) Dung môi & PROG chỉ theo **sổ máy / bảng HQ** "
        "(không bịa số)\n"
        "4) Gạch dưới / hai gạch: mới vào phải có quản lý\n"
        "5) QC sau chu trình; sự cố → HQ\n"
        "\n"
        "Khi HQ đưa bảng Realstar vào `data/realstar_courses.json`, "
        "các bước sẽ hiện tiếp theo."
    )


def try_professional_machine_card(
    user_message: str,
    *,
    lang: str = "ko",
    user_id: str = "",
) -> str:
    """If message is about dry machine/PROG, return gated card; else empty."""
    msg = (user_message or "").strip()
    if not msg or not is_professional_machine_question(msg):
        return ""
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    has = resolve_has_machine(user_id, fresh=True) if user_id else False
    if not has:
        return lock_message(lang)

    # Optional HQ-authored courses
    course = _match_course(msg, _load_courses())
    code = ""
    if course:
        code = str(course.get("code") or course.get("solvent") or "").upper()
    parts = [unlock_message(lang, code=code), "", _safe_ops_card(lang, code_hint=code)]
    if course:
        steps = _steps_from_course(course, lang)
        title = str(course.get("title_ko") or course.get("title") or course.get("id") or "course")
        if lang == "vi":
            title = str(course.get("title_vi") or title)
        elif lang == "en":
            title = str(course.get("title_en") or title)
        if steps:
            parts.append("")
            parts.append(f"▶ {title}")
            for i, s in enumerate(steps, 1):
                parts.append(f"{i}) {s}")
        else:
            if lang == "ko":
                parts.append("")
                parts.append(f"(코스 매칭: {title} — 단계 문구가 JSON에 비어 있음 → 매뉴얼 확인)")
    return "\n".join(parts).strip()
