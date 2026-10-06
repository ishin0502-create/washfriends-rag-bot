# -*- coding: utf-8 -*-
"""Opt-in Zalo photo homework — care-label + intake 3-shot.

Exact-match commands only. Images are graded only while a task is pending.
Stain questions and unsolicited photos still go to GraphRAG.
"""
from __future__ import annotations

import re
import time
from typing import Any, Optional

from owner_qa_log import load_user, save_user
from reply_lang import detect_reply_lang

_START_RE = re.compile(
    r"^\s*("
    r"사진\s*과제|사진과제|숙제|"
    r"photo\s*(task|homework)|photo\s*drill|"
    r"bài\s*tập\s*ảnh|bai\s*tap\s*anh"
    r")\s*$",
    re.I,
)
_END_RE = re.compile(
    r"^\s*("
    r"사진\s*과제\s*끝|사진과제\s*끝|숙제\s*끝|"
    r"end\s*photo|cancel\s*photo|"
    r"kết\s*thúc\s*ảnh|ket\s*thuc\s*anh"
    r")\s*$",
    re.I,
)

_STEPS = ("label", "intake_label", "intake_stain", "intake_full")
_PASS_LABEL = "label"
_PASS_INTAKE = "intake"


def _empty_state() -> dict[str, Any]:
    return {"pending": None, "passed": [], "updated_at": time.time()}


def _state(user_id: str) -> dict[str, Any]:
    u = load_user(user_id)
    st = u.get("photo_task")
    if not isinstance(st, dict):
        st = _empty_state()
    st.setdefault("pending", None)
    st.setdefault("passed", [])
    if not isinstance(st["passed"], list):
        st["passed"] = []
    return st


def _save(user_id: str, st: dict[str, Any]) -> None:
    st["updated_at"] = time.time()
    u = load_user(user_id)
    u["photo_task"] = st
    save_user(user_id, u)
    try:
        from course_progress_sync import push_course_progress

        push_course_progress(user_id)
    except Exception:
        pass


def pending_photo_task(user_id: str) -> Optional[str]:
    pend = _state(user_id).get("pending")
    if pend in _STEPS:
        return str(pend)
    return None


def photo_task_counts(user_id: str) -> tuple[int, int]:
    passed = {str(x) for x in (_state(user_id).get("passed") or [])}
    n = 0
    if _PASS_LABEL in passed:
        n += 1
    if _PASS_INTAKE in passed:
        n += 1
    return n, 2


def _prompt(step: str, lang: str) -> str:
    if lang == "en":
        if step == "label":
            return (
                "◆ Photo drill 1/2 — care label\n"
                "Send one photo of the wash-symbol tag (inside the garment).\n"
                "For a real stain question, type it as text, or send 「end photo」."
            )
        if step == "intake_label":
            return (
                "◆ Photo drill 2/2 — intake shot 1/3 (label)\n"
                "Send the care-label close-up first."
            )
        if step == "intake_stain":
            return (
                "◆ Intake shot 2/3 — stain as-is\n"
                "Close-up of the stain in daylight. Do not wipe it first."
            )
        return (
            "◆ Intake shot 3/3 — whole garment / color\n"
            "One photo showing the garment color and the stain location."
        )
    if lang == "vi":
        if step == "label":
            return (
                "◆ Bài ảnh 1/2 — nhãn giặt\n"
                "Gửi 1 ảnh ký hiệu giặt (trong áo).\n"
                "Hỏi vết bẩn thì gõ chữ, hoặc 「kết thúc ảnh」."
            )
        if step == "intake_label":
            return "◆ Bài ảnh 2/2 — ảnh nhận 1/3 (nhãn)\nGửi cận nhãn giặt trước."
        if step == "intake_stain":
            return "◆ Ảnh nhận 2/3 — vết nguyên trạng\nCận vết dưới ánh sáng. Đừng chà trước."
        return "◆ Ảnh nhận 3/3 — cả áo / màu\nMột ảnh thấy màu áo và vị trí vết."
    if step == "label":
        return (
            "◆ 사진 과제 1/2 — 케어라벨\n"
            "옷 안쪽 세탁 기호(케어라벨) 사진 한 장을 보내 주세요.\n"
            "지금 얼룩을 물어보려면 글로 보내시거나 「사진과제 끝」."
        )
    if step == "intake_label":
        return (
            "◆ 사진 과제 2/2 — 접수 사진 1/3 (라벨)\n"
            "먼저 케어라벨 근접 사진을 보내 주세요."
        )
    if step == "intake_stain":
        return (
            "◆ 접수 사진 2/3 — 얼룩 원상태\n"
            "자연광에서 얼룩 근접. 먼저 문지르지 마세요."
        )
    return (
        "◆ 접수 사진 3/3 — 옷 전체·색상\n"
        "옷 색과 얼룩 위치가 보이게 한 장 보내 주세요."
    )


def _done_all(lang: str) -> str:
    if lang == "en":
        return (
            "◆ Photo drills done (2/2).\n"
            "Label + 3 intake shots. Real stains: just send a photo or a sentence."
        )
    if lang == "vi":
        return (
            "◆ Xong bài ảnh (2/2).\n"
            "Nhãn + 3 ảnh nhận. Vết thật: gửi ảnh hoặc câu hỏi."
        )
    return (
        "◆ 사진 과제를 모두 마치셨습니다. (2/2)\n"
        "라벨 + 접수 3장 연습이 끝났습니다.\n"
        "실제 얼룩은 사진이나 글로 그냥 보내 주세요."
    )


def try_handle_photo_task_text(user_id: str, text: str) -> Optional[str]:
    raw = (text or "").strip()
    if not user_id or not raw:
        return None
    lang = detect_reply_lang(raw)
    if _END_RE.match(raw):
        st = _state(user_id)
        st["pending"] = None
        _save(user_id, st)
        if lang == "en":
            return "◆ Photo drill paused. Stain photos work as usual. Resume: 「photo task」."
        if lang == "vi":
            return "◆ Đã dừng bài ảnh. Ảnh vết bẩn như bình thường. Học lại: 「bài tập ảnh」."
        return "◆ 사진 과제를 멈췄습니다. 얼룩 사진은 평소처럼 보내시면 됩니다. 다시: 「사진과제」."
    if not _START_RE.match(raw):
        return None
    st = _state(user_id)
    passed = {str(x) for x in (st.get("passed") or [])}
    if _PASS_LABEL in passed and _PASS_INTAKE in passed:
        st["pending"] = None
        _save(user_id, st)
        return _done_all(lang)
    if _PASS_LABEL not in passed:
        st["pending"] = "label"
        _save(user_id, st)
        return _prompt("label", lang)
    st["pending"] = "intake_label"
    _save(user_id, st)
    return _prompt("intake_label", lang)


def _expect_kind(step: str) -> str:
    if step in {"label", "intake_label"}:
        return "care_label"
    if step == "intake_stain":
        return "stain_photo"
    return "garment"


def _kind_ok(step: str, kind: str) -> bool:
    want = _expect_kind(step)
    k = (kind or "").strip()
    if want == "care_label":
        return k == "care_label"
    if want == "stain_photo":
        return k == "stain_photo"
    return k in {"stain_photo", "other"}


def _classify_photo(image_url: str, caption: str) -> dict:
    from image_analyzer import analyze_image

    return analyze_image(image_url=image_url or "", user_caption=caption or "") or {}


def try_handle_photo_task_image(
    user_id: str,
    image_url: str,
    caption: str = "",
) -> Optional[str]:
    if not user_id or not pending_photo_task(user_id):
        return None
    lang = detect_reply_lang(caption or "") if (caption or "").strip() else "ko"
    step = pending_photo_task(user_id)
    result = _classify_photo(image_url, caption)
    kind = str(result.get("image_kind") or "other")
    st = _state(user_id)
    if not _kind_ok(step, kind):
        if lang == "en":
            return (
                "◆ Not the shot for this drill.\n"
                f"Need: {_expect_kind(step)}. Got: {kind}.\n"
                "Retry this photo, or 「end photo」 for a real stain."
            )
        if lang == "vi":
            return (
                "◆ Ảnh chưa đúng bài.\n"
                f"Cần: {_expect_kind(step)}. Nhận: {kind}.\n"
                "Chụp lại, hoặc 「kết thúc ảnh」 để hỏi vết bẩn."
            )
        need = {
            "care_label": "케어라벨(세탁 기호)",
            "stain_photo": "얼룩 근접(원상태)",
            "garment": "옷 전체·색상",
        }.get(_expect_kind(step), step)
        return (
            f"◆ 이번 과제의 사진이 아닙니다.\n"
            f"필요한 것: {need}\n"
            "다시 찍어 보내 주세요. 현장 얼룩이면 「사진과제 끝」."
        )

    passed = [str(x) for x in (st.get("passed") or [])]
    nxt = None
    msg_ok = ""
    if step == "label":
        if _PASS_LABEL not in passed:
            passed.append(_PASS_LABEL)
        st["passed"] = passed
        st["pending"] = "intake_label"
        nxt = "intake_label"
        if lang == "en":
            msg_ok = "◆ Care-label photo OK.\n"
        elif lang == "vi":
            msg_ok = "◆ Ảnh nhãn đạt.\n"
        else:
            msg_ok = "◆ 케어라벨 사진, 통과입니다.\n"
    elif step == "intake_label":
        st["pending"] = "intake_stain"
        nxt = "intake_stain"
        msg_ok = "◆ 1/3 OK.\n" if lang == "ko" else "◆ 1/3 OK.\n"
    elif step == "intake_stain":
        st["pending"] = "intake_full"
        nxt = "intake_full"
        msg_ok = "◆ 2/3 OK.\n" if lang == "ko" else "◆ 2/3 OK.\n"
    else:
        if _PASS_INTAKE not in passed:
            passed.append(_PASS_INTAKE)
        st["passed"] = passed
        st["pending"] = None
        _save(user_id, st)
        return _done_all(lang)

    _save(user_id, st)
    return msg_ok + _prompt(nxt, lang)
