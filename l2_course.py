# -*- coding: utf-8 -*-
"""L2 sequential owner course — additive UX only.

Requires L1 complete (soft gate). Does NOT rewrite GraphRAG / SOP seeds.
Progress stored per Zalo user in owner_qa_log under key l2_course.
Opt-in: 「중급」 / 「다음」 (while L2 active) / 「중급 진도」 / 「교육 끝」.
"""
from __future__ import annotations

import re
import time
from typing import Any, Optional

from l1_course import is_l1_complete, l1_done_count, LESSONS as L1_LESSONS
from owner_qa_log import load_user, save_user
from reply_lang import detect_reply_lang

_START_RE = re.compile(
    r"^\s*("
    r"중급|중급\s*교육|L2|L2\s*교육|L2\s*코스|중급\s*시작|"
    r"intermediate|l2\s*course|khóa\s*l2|hoc\s*l2|trung\s*cấp"
    r")\s*$",
    re.I,
)
_NEXT_RE = re.compile(
    r"^\s*(다음|다음\s*장|next|tiếp|tiep|học\s*tiếp|hoc\s*tiep|trang\s*sau)\s*$",
    re.I,
)
_PROGRESS_RE = re.compile(
    r"^\s*("
    r"중급\s*진도|L2\s*진도|l2\s*progress|intermediate\s*progress|"
    r"tiến\s*độ\s*l2|tien\s*do\s*l2"
    r")\s*$",
    re.I,
)
_EXIT_RE = re.compile(
    r"^\s*(교육\s*끝|교육\s*종료|코스\s*끝|exit\s*course|end\s*course|"
    r"kết\s*thúc\s*học|ket\s*thuc\s*hoc)\s*$",
    re.I,
)

# Zalo-sized excerpts from CURRICULUM_L1_L2_L3.md L2-A~E — copy, not live SOP rewrite.
LESSONS: list[dict[str, str]] = [
    {
        "id": "l2a_01",
        "title": "원단×색×신선/마름 — 면·린넨",
        "body": (
            "[L2] 면·린넨: 흰+신선 → 구석 테스트 후 전 약품 가능.\n"
            "흰+마름 → 산소 장침지·효소 밤새 가능. 유색+신선 → 산소는 테스트만.\n"
            "유색+마름 → 산소 원칙 금지, 흰 식초 반복."
        ),
    },
    {
        "id": "l2a_02",
        "title": "원단×색 — 폴리 vs 실크·울",
        "body": (
            "[L2] 폴리·혼방: 산소 OK(흰), 60°C 상한. 유색 마름은 식초·주방세제 위주.\n"
            "실크·울: 효소·산소·염소·용제·옥살산 금지. 중성세제+찬물만.\n"
            "심하면 전문 의뢰가 정답입니다."
        ),
    },
    {
        "id": "l2a_03",
        "title": "가죽·스웨이드·아세테이트",
        "body": (
            "[L2] 가죽·스웨이드·아세테이트는 물 침지 자체 금지.\n"
            "전용 케어 또는 전문 의뢰. 초보 단독으로 ‘세탁기 한 번’ 시도하지 마세요."
        ),
    },
    {
        "id": "l2b_01",
        "title": "3계열 · 탄닌(커피·와인·주스…)",
        "body": (
            "[L2] 탄닌: 즉시 찬물 → 흰 식초 1:4 → 흰 면만 산소.\n"
            "이른 열은 색소 고착. 실크·울에 산소 금지.\n"
            "(커피·차·와인·주스·간장·빈랑·사탕수수즙·화이트와인)"
        ),
    },
    {
        "id": "l2b_02",
        "title": "3계열 · 단백질(피·계란·우유…)",
        "body": (
            "[L2] 단백질: 찬물만(온수 금지) → 효소(실크·울은 중성세제) → 찬물·미온 세탁.\n"
            "열 = 갈색 영구. 피·계란·우유·땀·구토·분변·소변·모유 동일 계열."
        ),
    },
    {
        "id": "l2b_03",
        "title": "3계열 · 오일-지방",
        "body": (
            "[L2] 오일-지방: 흡착분(전분) → 주방세제 → 필요 시 리파아제 → 미끄럼 없앤 뒤 건조.\n"
            "열고착 시 성공률 급감. 실크·울에 강한 용제·고온 금지.\n"
            "(식용유·버터·마요·엔진오일·타르·립스틱·선크림 등)"
        ),
    },
    {
        "id": "l2c_01",
        "title": "색소·염료(립스틱·잉크·염모제…)",
        "body": (
            "[L2] (1) 안쪽에서 (2) 흡수지 깔고 (3) 알코올 또는 아세톤 찍어\n"
            "(4) 수직 블롯, 매번 새 천. 문지르면 옆으로 번집니다.\n"
            "아세테이트·레이온·비닐코팅은 아세톤 절대 금지(원단 녹음)."
        ),
    },
    {
        "id": "l2d_01",
        "title": "산소표백 결정 트리",
        "body": (
            "[L2] ① 흰 면·폴리·색 안정 유색? 아니면 중단.\n"
            "② 구석 테스트 30초 통과? 아니면 중단.\n"
            "③ 액체 3% 과수(흰 면) 또는 과탄산 미온 침지(상한 준수).\n"
            "색 미확인·실크·울·가죽·나일론·스판덱스 → 산소 자체 금지."
        ),
    },
    {
        "id": "l2e_01",
        "title": "이염(dye transfer) 대응",
        "body": (
            "[L2] 즉시 세탁기에서 분리, 건조 금지(열 고착).\n"
            "흰 면·폴리 단독 → 산소 장침지 후 재세탁.\n"
            "유색·실크·울 → 산소만·테스트만·염소 금지·전문 고려.\n"
            "이미 건조기 통과 = 복원 불가로 재분류."
        ),
    },
]


def _state(user_id: str) -> dict[str, Any]:
    u = load_user(user_id)
    st = u.get("l2_course")
    if not isinstance(st, dict):
        st = {"active": False, "index": 0, "completed": [], "updated_at": time.time()}
    st.setdefault("completed", [])
    if not isinstance(st["completed"], list):
        st["completed"] = []
    st.setdefault("active", False)
    st.setdefault("index", 0)
    st.setdefault("pending_quiz", None)
    st.setdefault("quiz_passed", [])
    if not isinstance(st["quiz_passed"], list):
        st["quiz_passed"] = []
    return st


def _save_state(user_id: str, st: dict[str, Any]) -> None:
    st["updated_at"] = time.time()
    u = load_user(user_id)
    u["l2_course"] = st
    save_user(user_id, u)
    try:
        from course_progress_sync import push_course_progress

        push_course_progress(user_id)
    except Exception:
        pass


def deactivate_l2_course(user_id: str) -> None:
    st = _state(user_id)
    if not st.get("active"):
        return
    st["active"] = False
    _save_state(user_id, st)


def is_l2_active(user_id: str) -> bool:
    return bool(_state(user_id).get("active"))


_CHECKPOINT_QUIZ = {
    "l2a_01": "l2e_cotton_dry_color",
    "l2a_03": "l2e_leather",
    "l2b_02": "l2e_protein_heat",
    "l2d_01": "l2e_oxygen_tree",
    "l2e_01": "l2e_dye_transfer",
}


def _l2_bank_item(qid: str) -> Optional[dict[str, Any]]:
    from l2_exam_bank import L2_BANK_KO

    for it in L2_BANK_KO:
        if str(it.get("id") or "") == qid:
            return it
    return None


def is_l2_course_command(text: str) -> bool:
    raw = (text or "").strip()
    return bool(
        _START_RE.match(raw)
        or _NEXT_RE.match(raw)
        or _PROGRESS_RE.match(raw)
        or _EXIT_RE.match(raw)
    )


def l2_quiz_counts(user_id: str) -> tuple[int, int]:
    st = _state(user_id)
    passed = {str(x) for x in (st.get("quiz_passed") or []) if x}
    return len(passed), len(_CHECKPOINT_QUIZ)


def _after_lesson_advance(user_id: str, st: dict[str, Any], lang: str) -> str:
    from course_checkpoint import quiz_prompt

    idx = int(st.get("index") or 0)
    idx = max(0, min(idx, len(LESSONS) - 1))
    completed = [str(x) for x in (st.get("completed") or [])]
    lid = LESSONS[idx]["id"]
    if lid not in completed:
        completed.append(lid)
    st["completed"] = completed
    passed = [str(x) for x in (st.get("quiz_passed") or [])]
    qid = _CHECKPOINT_QUIZ.get(lid)
    if qid and qid not in passed:
        st["pending_quiz"] = qid
        st["active"] = True
        _save_state(user_id, st)
        return quiz_prompt(qid, lang, find_item=_l2_bank_item, source="l2_bank")

    if idx + 1 >= len(LESSONS):
        st["active"] = False
        st["index"] = len(LESSONS) - 1
        st["pending_quiz"] = None
        _save_state(user_id, st)
        if lang == "ko":
            return (
                "◆ 세탁 중급 내용을 모두 읽으셨습니다.\n"
                f"읽은 내용: {len(completed)}/{len(LESSONS)}\n"
                f"확인 문제: {len(passed)}개 통과\n\n"
                "이제 원단·색·신선/마름을 떠올리며 「현장」질문을 해 보세요.\n"
                "고급을 이어서 배우려면 「고급」이라고 보내 주세요.\n\n"
                "중급 다시 보기: 「중급」 · 초급: 「교육」 · 시험: 「시험 성적」"
            )
        if lang == "en":
            return (
                f"◆ Intermediate finished ({len(completed)}/{len(LESSONS)}).\n"
                "Ask stains anytime. Review: 「중급」."
            )
        return (
            f"◆ Đã xong trung cấp ({len(completed)}/{len(LESSONS)}).\n"
            "Hỏi vết bẩn. Xem lại: 「중급」."
        )

    st["index"] = idx + 1
    st["pending_quiz"] = None
    _save_state(user_id, st)
    return _render_lesson(st["index"], lang, done_n=len(completed))


def l2_done_count(user_id: str) -> int:
    st = _state(user_id)
    done = {str(x) for x in (st.get("completed") or [])}
    return sum(1 for les in LESSONS if les["id"] in done)


def is_l2_complete(user_id: str) -> bool:
    return l2_done_count(user_id) >= len(LESSONS)


def _l1_gate_msg(user_id: str, lang: str) -> str:
    done = l1_done_count(user_id)
    total = len(L1_LESSONS)
    if lang == "ko":
        return (
            "◆ 중급은 아직 차례가 아니에요.\n\n"
            f"먼저 초급을 끝까지 읽어 주세요. (지금 {done}/{total})\n"
            "초급을 이어가려면 「교육」이라고 보내 주세요.\n"
            "다 읽은 뒤에 「중급」을 다시 보내시면 됩니다.\n\n"
            "※ 지금 당장 옷·얼룩이 급하면 「현장」으로 물어보시면 됩니다."
        )
    if lang == "en":
        return (
            "◆ Intermediate comes after beginner.\n"
            f"Finish beginner first ({done}/{total}). Send 「교육」.\n"
            "Urgent stain: 「field」."
        )
    return (
        "◆ Trung cấp sau bài cơ bản.\n"
        f"Đọc xong cơ bản trước ({done}/{total}). Gửi 「교육」.\n"
        "Hỏi vết bẩn gấp: 「hiện trường」."
    )


def _render_lesson(idx: int, lang: str, *, done_n: int) -> str:
    from course_i18n import lesson_title_body

    total = len(LESSONS)
    lesson = LESSONS[idx]
    title, body = lesson_title_body(lesson, lang)
    n = idx + 1
    if lang == "en":
        return (
            f"◆ Intermediate lesson {n} of {total}\n"
            f"{title}\n\n"
            f"{body}\n\n"
            f"Finished so far: {done_n} of {total}\n"
            "Send 「next」 for the next page · Pause: 「end course」"
        )
    if lang == "vi":
        return (
            f"◆ Bài trung cấp {n}/{total}\n"
            f"{title}\n\n"
            f"{body}\n\n"
            f"Đã đọc: {done_n}/{total}\n"
            "Gửi 「tiếp」 · Dừng: 「kết thúc học」"
        )
    return (
        f"◆ 세탁 중급 배우기 ({n}/{total})\n"
        f"【{lesson['title']}】\n\n"
        f"{lesson['body']}\n\n"
        f"지금까지 읽은 내용: {done_n}/{total}\n"
        "다 읽으셨으면 「다음」이라고 보내 주세요.\n"
        "오늘은 여기까지: 「교육 끝」 · 급하면 「현장」"
    )


def _progress_msg(st: dict[str, Any], lang: str) -> str:
    done = {str(x) for x in (st.get("completed") or [])}
    n = sum(1 for les in LESSONS if les["id"] in done)
    total = len(LESSONS)
    idx = int(st.get("index") or 0)
    active = bool(st.get("active"))
    if lang == "en":
        return (
            f"◆ Intermediate progress: {n} of {total}\n"
            f"{'Learning now.' if active else 'Paused.'} Page {min(idx + 1, total)}/{total}.\n"
            "Continue: 「중급」 · Next: 「next」"
        )
    if lang == "vi":
        return (
            f"◆ Tiến độ trung cấp: {n}/{total}\n"
            f"{'Đang học.' if active else 'Đã dừng.'} Trang {min(idx + 1, total)}/{total}.\n"
            "Học tiếp: 「중급」 · Trang sau: 「tiếp」"
        )
    cur = min(idx + 1, total)
    status = (
        f"지금 중급 내용을 보고 계십니다. ({cur}/{total}번째)"
        if active
        else f"중급 배우기를 잠시 멈추신 상태입니다. (마지막 위치 {cur}/{total})"
    )
    return (
        f"◆ 세탁 중급, 어디까지 보셨나요\n"
        f"읽은 내용: {n}/{total}\n"
        f"{status}\n\n"
        "이어서: 「중급」 · 다음 장: 「다음」"
    )


def try_handle_l2_course(user_id: str, text: str) -> Optional[str]:
    """Handle L2 course. None → other handlers. Does not steal L1 when L2 inactive."""
    raw = (text or "").strip()
    if not user_id or not raw:
        return None
    lang = detect_reply_lang(raw)
    st = _state(user_id)
    l2_on = bool(st.get("active"))

    pending = st.get("pending_quiz")
    if pending and l2_on and not is_l2_course_command(raw):
        from course_checkpoint import fail_message, grade_checkpoint, pass_message, quiz_explain, quiz_prompt
        from l1_course import _looks_like_stain_question

        if _looks_like_stain_question(raw):
            return None
        if grade_checkpoint(str(pending), raw, lang, find_item=_l2_bank_item, source="l2_bank"):
            passed = [str(x) for x in (st.get("quiz_passed") or [])]
            if str(pending) not in passed:
                passed.append(str(pending))
            st["quiz_passed"] = passed
            st["pending_quiz"] = None
            explain = quiz_explain(str(pending), lang, find_item=_l2_bank_item, source="l2_bank")
            nxt = _after_lesson_advance(user_id, st, lang)
            return pass_message(lang, explain, nxt)
        explain = quiz_explain(str(pending), lang, find_item=_l2_bank_item, source="l2_bank")
        again = quiz_prompt(str(pending), lang, find_item=_l2_bank_item, source="l2_bank")
        return fail_message(lang, explain, again)

    if _PROGRESS_RE.match(raw):
        if not is_l1_complete(user_id):
            return _l1_gate_msg(user_id, lang)
        return _progress_msg(st, lang)

    if _START_RE.match(raw):
        if not is_l1_complete(user_id):
            return _l1_gate_msg(user_id, lang)
        # Pause L1 if it was active
        try:
            from l1_course import deactivate_course
            from l3_course import deactivate_l3_course

            deactivate_course(user_id)
            deactivate_l3_course(user_id)
        except Exception:
            pass
        done = {str(x) for x in (st.get("completed") or [])}
        idx = 0
        for i, les in enumerate(LESSONS):
            if les["id"] not in done:
                idx = i
                break
        else:
            idx = 0
        st["active"] = True
        st["index"] = idx
        _save_state(user_id, st)
        if lang == "ko":
            head = (
                "◆ 세탁 중급 배우기를 시작합니다.\n\n"
                "원단×색 판단 → 3계열(탄닌·단백질·오일) → 색소·산소·이염\n"
                f"전부 {len(LESSONS)}장입니다. 한 장씩 읽고 「다음」을 보내 주세요.\n"
                "급하면 「현장」또는 「교육 끝」.\n\n"
            )
            if done:
                head = (
                    "◆ 세탁 중급, 이어서 배워 볼게요.\n"
                    f"이미 읽으신 내용: {len(done)}/{len(LESSONS)}\n\n"
                    "다 읽으면 「다음」· 급하면 「현장」.\n\n"
                )
        elif lang == "en":
            head = (
                "◆ Starting intermediate lessons.\n"
                "Send 「next」 after each page · Urgent: 「field」.\n\n"
            )
        else:
            head = (
                "◆ Bắt đầu bài trung cấp.\n"
                "Gửi 「tiếp」 sau mỗi trang · Gấp: 「hiện trường」.\n\n"
            )
        if st.get("pending_quiz"):
            from course_checkpoint import quiz_prompt

            return head + quiz_prompt(
                str(st["pending_quiz"]), lang, find_item=_l2_bank_item, source="l2_bank"
            )
        return head + _render_lesson(idx, lang, done_n=len(done))

    # Shared 「다음」 / 「교육 끝」 only while L2 is the active course
    if not l2_on:
        return None

    if _EXIT_RE.match(raw):
        deactivate_l2_course(user_id)
        if lang == "en":
            return (
                "◆ Intermediate lessons paused.\n"
                "Ask stains anytime. Continue later: 「중급」."
            )
        if lang == "vi":
            return (
                "◆ Đã tạm dừng bài trung cấp.\n"
                "Vẫn hỏi được vết bẩn. Học tiếp: 「중급」."
            )
        return (
            "◆ 중급 배우기를 잠시 멈췄습니다.\n"
            "얼룩·옷 질문은 평소처럼 보내시면 됩니다.\n"
            "다시 이어서: 「중급」"
        )

    if _NEXT_RE.match(raw):
        idx = int(st.get("index") or 0)
        idx = max(0, min(idx, len(LESSONS) - 1))
        if st.get("pending_quiz"):
            from course_checkpoint import quiz_prompt

            return quiz_prompt(str(st["pending_quiz"]), lang, find_item=_l2_bank_item, source="l2_bank")
        return _after_lesson_advance(user_id, st, lang)

    return None
