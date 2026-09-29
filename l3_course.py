# -*- coding: utf-8 -*-
"""L3 sequential owner course — additive UX only.

Requires L2 complete (and thus L1). Does NOT rewrite GraphRAG / SOP seeds.
Progress stored per Zalo user in owner_qa_log under key l3_course.
Opt-in: 「고급」 / 「다음」 (while L3 active) / 「고급 진도」 / 「교육 끝」.
"""
from __future__ import annotations

import re
import time
from typing import Any, Optional

from l1_course import is_l1_complete, l1_done_count, LESSONS as L1_LESSONS
from l2_course import is_l2_complete, l2_done_count, LESSONS as L2_LESSONS
from owner_qa_log import load_user, save_user
from reply_lang import detect_reply_lang

_START_RE = re.compile(
    r"^\s*("
    r"고급|고급\s*교육|L3|L3\s*교육|L3\s*코스|고급\s*시작|"
    r"advanced|l3\s*course|khóa\s*l3|hoc\s*l3|cao\s*cấp"
    r")\s*$",
    re.I,
)
_NEXT_RE = re.compile(
    r"^\s*(다음|다음\s*장|next|tiếp|tiep)\s*$",
    re.I,
)
_PROGRESS_RE = re.compile(
    r"^\s*("
    r"고급\s*진도|L3\s*진도|l3\s*progress|advanced\s*progress|"
    r"tiến\s*độ\s*l3|tien\s*do\s*l3"
    r")\s*$",
    re.I,
)
_EXIT_RE = re.compile(
    r"^\s*(교육\s*끝|교육\s*종료|코스\s*끝|exit\s*course|end\s*course|"
    r"kết\s*thúc\s*học|ket\s*thuc\s*hoc)\s*$",
    re.I,
)

# Zalo-sized excerpts from CURRICULUM_L1_L2_L3.md L3-A~E — copy, not live SOP rewrite.
LESSONS: list[dict[str, str]] = [
    {
        "id": "l3a_01",
        "title": "1차 실패 후 2·3차 순서",
        "body": (
            "[L3] 1차 실패 → 원단·잔여 얼룩 재판단 → 다른 계열인지 확인 후 2차.\n"
            "2차도 실패면 등급 2(부분 제거) 재고지 → 잔여 수용 또는 전문 의뢰.\n"
            "락스는 만능이 아님(데오·황변·분유·이염·실크·울은 악화 가능)."
        ),
    },
    {
        "id": "l3a_02",
        "title": "열로 감추기 금지",
        "body": (
            "[L3] 다림질·건조기로 ‘대충 감추기’ 시도 금지 — 클레임이 커집니다.\n"
            "잔색·미끄럼·냄새가 있으면 열을 가하지 마세요."
        ),
    },
    {
        "id": "l3b_01",
        "title": "특수 품목 · 가죽·다운·정장",
        "body": (
            "[L3] 가죽·스웨이드·모피: 물 침지 금지 · 전용·전문.\n"
            "다운: 국소만 중성·미온. 전체 침수는 전용·완전 건조.\n"
            "정장(울): 얼룩 부위만 가볍게. 전체는 원칙 드라이."
        ),
    },
    {
        "id": "l3b_02",
        "title": "특수 품목 · 기능성·아기옷",
        "body": (
            "[L3] 방수·스포츠: 유연제·산소·염소 금지 · 전용 세제.\n"
            "아기옷: 락스·강한 향 금지. 산소·효소는 헹굼 충분히.\n"
            "잔색 없을 때만 햇빛 건조."
        ),
    },
    {
        "id": "l3c_01",
        "title": "베트남 · 라테라이트(붉은 적토)",
        "body": (
            "[L3] 젖은 채 문지르기·락스 절대 금지(철 고착).\n"
            "완전 건조 → 마른 브러시(마스크) → 찬물 → (면·린넨·폴리만) 옥살산 경로.\n"
            "실크·울은 식초 약하게만 · 심하면 전문."
        ),
    },
    {
        "id": "l3c_02",
        "title": "베트남 · 오토바이 오일·느억맘",
        "body": (
            "[L3] 오토바이 오일: 흡착분 반복 → 탈지(환기·화기 금지) → 주방세제 → 미끄럼 없이 건조.\n"
            "느억맘: 찬물 → 효소 → 흰 식초 1:4(냄새) → 흰 면만 산소 → 충분 헹굼."
        ),
    },
    {
        "id": "l3c_03",
        "title": "베트남 · 김치국·습기 곰팡이",
        "body": (
            "[L3] 김치국: 건더기 제거 → 안쪽 찬물 → 주방세제 → 식초 → 흰옷만 산소(유색 산소 원칙 금지).\n"
            "곰팡이: 실외·PPE → 마른 포자 털기 → 식초 → 허용 원단만 산소. 가죽·실크·울·심함=전문."
        ),
    },
    {
        "id": "l3d_01",
        "title": "클레임 · 접수 사진·동의서",
        "body": (
            "[L3] 접수 사진 필수: 라벨·얼룩 원상태·색상 근접 3장(자연광).\n"
            "등급 2·3은 동의서 또는 Zalo 회신 저장.\n"
            "초보 매장은 상급 판단 전 배상 확약 금지."
        ),
    },
    {
        "id": "l3d_02",
        "title": "전문 의뢰 판단선",
        "body": (
            "[L3] 즉시 전문·거절 검토:\n"
            "실크·울·가죽·모피·아세테이트 / 유성페인트·유성매직·502·엔진오일 마름·오래된 곰팡이\n"
            "/ 이미 건조기 통과한 이염 — 자체 무리 시도 금지."
        ),
    },
    {
        "id": "l3e_01",
        "title": "전문 의뢰 안내 스크립트",
        "body": (
            "[L3] 「이 얼룩·원단은 저희 매장에서 안전하게 처리하기 어렵습니다.\n"
            "시도하면 원단 손상·색 손실 위험이 큽니다.\n"
            "전문 의뢰를 안내드리거나, 원치 않으시면 접수 반려로 처리해 드리겠습니다.」"
        ),
    },
]


def _state(user_id: str) -> dict[str, Any]:
    u = load_user(user_id)
    st = u.get("l3_course")
    if not isinstance(st, dict):
        st = {"active": False, "index": 0, "completed": [], "updated_at": time.time()}
    st.setdefault("completed", [])
    if not isinstance(st["completed"], list):
        st["completed"] = []
    st.setdefault("active", False)
    st.setdefault("index", 0)
    return st


def _save_state(user_id: str, st: dict[str, Any]) -> None:
    st["updated_at"] = time.time()
    u = load_user(user_id)
    u["l3_course"] = st
    save_user(user_id, u)
    try:
        from course_progress_sync import push_course_progress

        push_course_progress(user_id)
    except Exception:
        pass


def deactivate_l3_course(user_id: str) -> None:
    st = _state(user_id)
    if not st.get("active"):
        return
    st["active"] = False
    _save_state(user_id, st)


def is_l3_active(user_id: str) -> bool:
    return bool(_state(user_id).get("active"))


def l3_done_count(user_id: str) -> int:
    st = _state(user_id)
    done = {str(x) for x in (st.get("completed") or [])}
    return sum(1 for les in LESSONS if les["id"] in done)


def is_l3_complete(user_id: str) -> bool:
    return l3_done_count(user_id) >= len(LESSONS)


def _gate_msg(user_id: str, lang: str) -> str:
    if not is_l1_complete(user_id):
        done = l1_done_count(user_id)
        total = len(L1_LESSONS)
        if lang == "ko":
            return (
                "◆ 고급은 아직 차례가 아니에요.\n\n"
                f"먼저 초급을 끝까지 읽어 주세요. (지금 {done}/{total})\n"
                "「교육」으로 초급 → 그다음 「중급」→ 「고급」 순서입니다.\n"
                "급하면 「현장」으로 물어보시면 됩니다."
            )
        if lang == "en":
            return (
                "◆ Advanced comes after beginner → intermediate.\n"
                f"Finish beginner first ({done}/{total}). Send 「교육」."
            )
        return (
            "◆ Cao cấp sau cơ bản → trung cấp.\n"
            f"Đọc xong cơ bản trước ({done}/{total}). Gửi 「교육」."
        )
    if not is_l2_complete(user_id):
        done = l2_done_count(user_id)
        total = len(L2_LESSONS)
        if lang == "ko":
            return (
                "◆ 고급은 중급을 마친 뒤에 열려요.\n\n"
                f"중급 진도: {done}/{total}\n"
                "중급을 이어가려면 「중급」이라고 보내 주세요.\n"
                "다 읽은 뒤 「고급」을 다시 보내시면 됩니다."
            )
        if lang == "en":
            return (
                "◆ Advanced unlocks after intermediate.\n"
                f"Intermediate progress: {done}/{total}. Send 「중급」."
            )
        return (
            "◆ Cao cấp mở sau trung cấp.\n"
            f"Tiến độ trung cấp: {done}/{total}. Gửi 「중급」."
        )
    return ""


def _render_lesson(idx: int, lang: str, *, done_n: int) -> str:
    total = len(LESSONS)
    lesson = LESSONS[idx]
    n = idx + 1
    if lang == "en":
        return (
            f"◆ Advanced lesson {n} of {total}\n"
            f"{lesson['title']}\n\n"
            f"{lesson['body']}\n\n"
            f"Finished so far: {done_n} of {total}\n"
            "Send 「next」 · Pause: 「end course」"
        )
    if lang == "vi":
        return (
            f"◆ Bài cao cấp {n}/{total}\n"
            f"{lesson['title']}\n\n"
            f"{lesson['body']}\n\n"
            f"Đã đọc: {done_n}/{total}\n"
            "Gửi 「tiếp」 · Dừng: 「kết thúc học」"
        )
    return (
        f"◆ 세탁 고급 배우기 ({n}/{total})\n"
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
            f"◆ Advanced progress: {n} of {total}\n"
            f"{'Learning now.' if active else 'Paused.'} Page {min(idx + 1, total)}/{total}.\n"
            "Continue: 「고급」 · Next: 「next」"
        )
    if lang == "vi":
        return (
            f"◆ Tiến độ cao cấp: {n}/{total}\n"
            f"{'Đang học.' if active else 'Đã dừng.'} Trang {min(idx + 1, total)}/{total}.\n"
            "Học tiếp: 「고급」 · Trang sau: 「tiếp」"
        )
    cur = min(idx + 1, total)
    status = (
        f"지금 고급 내용을 보고 계십니다. ({cur}/{total}번째)"
        if active
        else f"고급 배우기를 잠시 멈추신 상태입니다. (마지막 위치 {cur}/{total})"
    )
    return (
        f"◆ 세탁 고급, 어디까지 보셨나요\n"
        f"읽은 내용: {n}/{total}\n"
        f"{status}\n\n"
        "이어서: 「고급」 · 다음 장: 「다음」"
    )


def try_handle_l3_course(user_id: str, text: str) -> Optional[str]:
    """Handle L3 course. None → other handlers."""
    raw = (text or "").strip()
    if not user_id or not raw:
        return None
    lang = detect_reply_lang(raw)
    st = _state(user_id)
    l3_on = bool(st.get("active"))

    if _PROGRESS_RE.match(raw):
        gate = _gate_msg(user_id, lang)
        if gate:
            return gate
        return _progress_msg(st, lang)

    if _START_RE.match(raw):
        gate = _gate_msg(user_id, lang)
        if gate:
            return gate
        try:
            from l1_course import deactivate_course
            from l2_course import deactivate_l2_course

            deactivate_course(user_id)
            deactivate_l2_course(user_id)
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
                "◆ 세탁 고급 배우기를 시작합니다.\n\n"
                "실패 후 순서 → 특수 품목 → 베트남 현장 → 클레임·전문 의뢰\n"
                f"전부 {len(LESSONS)}장입니다. 한 장씩 읽고 「다음」을 보내 주세요.\n"
                "급하면 「현장」또는 「교육 끝」.\n\n"
            )
            if done:
                head = (
                    "◆ 세탁 고급, 이어서 배워 볼게요.\n"
                    f"이미 읽으신 내용: {len(done)}/{len(LESSONS)}\n\n"
                    "다 읽으면 「다음」· 급하면 「현장」.\n\n"
                )
        elif lang == "en":
            head = (
                "◆ Starting advanced lessons.\n"
                "Send 「next」 after each page · Urgent: 「field」.\n\n"
            )
        else:
            head = (
                "◆ Bắt đầu bài cao cấp.\n"
                "Gửi 「tiếp」 sau mỗi trang · Gấp: 「hiện trường」.\n\n"
            )
        return head + _render_lesson(idx, lang, done_n=len(done))

    if not l3_on:
        return None

    if _EXIT_RE.match(raw):
        deactivate_l3_course(user_id)
        if lang == "en":
            return (
                "◆ Advanced lessons paused.\n"
                "Ask stains anytime. Continue later: 「고급」."
            )
        if lang == "vi":
            return (
                "◆ Đã tạm dừng bài cao cấp.\n"
                "Vẫn hỏi được vết bẩn. Học tiếp: 「고급」."
            )
        return (
            "◆ 고급 배우기를 잠시 멈췄습니다.\n"
            "얼룩·옷 질문은 평소처럼 보내시면 됩니다.\n"
            "다시 이어서: 「고급」"
        )

    if _NEXT_RE.match(raw):
        idx = int(st.get("index") or 0)
        idx = max(0, min(idx, len(LESSONS) - 1))
        completed = [str(x) for x in (st.get("completed") or [])]
        lid = LESSONS[idx]["id"]
        if lid not in completed:
            completed.append(lid)
        st["completed"] = completed

        if idx + 1 >= len(LESSONS):
            st["active"] = False
            st["index"] = len(LESSONS) - 1
            _save_state(user_id, st)
            if lang == "ko":
                return (
                    "◆ 세탁 고급 내용을 모두 읽으셨습니다.\n"
                    f"읽은 내용: {len(completed)}/{len(LESSONS)}\n\n"
                    "거절·전문 의뢰가 필요한 경우도 「현장」질문으로 물어보시면 됩니다.\n"
                    "초급 「교육」 · 중급 「중급」 · 고급 다시 「고급」\n"
                    "시험 점수: 「시험 성적」"
                )
            if lang == "en":
                return (
                    f"◆ Advanced finished ({len(completed)}/{len(LESSONS)}).\n"
                    "Ask stains anytime. Review: 「고급」."
                )
            return (
                f"◆ Đã xong cao cấp ({len(completed)}/{len(LESSONS)}).\n"
                "Hỏi vết bẩn. Xem lại: 「고급」."
            )

        st["index"] = idx + 1
        _save_state(user_id, st)
        return _render_lesson(st["index"], lang, done_n=len(completed))

    return None
