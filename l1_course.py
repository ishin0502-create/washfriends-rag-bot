# -*- coding: utf-8 -*-
"""L1 sequential owner course — additive UX only.

Does NOT touch GraphRAG / protocol / stain SOP seeds.
Progress is stored per Zalo user in owner_qa_log (disk).
Opt-in: only 「교육」/「다음」/「교육 진도」/「교육 끝」 are consumed.
"""
from __future__ import annotations

import re
import time
from typing import Any, Optional

from owner_qa_log import load_user, save_user
from reply_lang import detect_reply_lang

# Explicit commands only — never steal free-form stain questions.
_START_RE = re.compile(
    r"^\s*("
    r"교육|초급\s*교육|L1\s*교육|L1\s*코스|교육\s*시작|"
    r"l1\s*course|beginner\s*course|khóa\s*l1|khoa\s*l1|hoc\s*l1|"
    r"học\s*cơ\s*bản|hoc\s*co\s*ban"
    r")\s*$",
    re.I,
)
_NEXT_RE = re.compile(
    r"^\s*(다음|다음\s*장|next|tiếp|tiep|học\s*tiếp|hoc\s*tiep|trang\s*sau)\s*$",
    re.I,
)
_PROGRESS_RE = re.compile(
    r"^\s*(교육\s*진도|진도|progress|l1\s*진도|tiến\s*độ|tien\s*do)\s*$",
    re.I,
)
_EXIT_RE = re.compile(
    r"^\s*(교육\s*끝|교육\s*종료|코스\s*끝|exit\s*course|end\s*course|"
    r"kết\s*thúc\s*học|ket\s*thuc\s*hoc)\s*$",
    re.I,
)
_LEVEL_RE = re.compile(
    r"^\s*("
    r"중급|중급\s*교육|L2|L2\s*교육|L2\s*코스|"
    r"고급|고급\s*교육|L3|L3\s*교육|L3\s*코스|"
    r"intermediate|advanced|trung\s*cấp|cao\s*cấp"
    r")\s*$",
    re.I,
)


# After these lesson ids, 「다음」 shows a 1-question checkpoint (not stain Q&A).
_CHECKPOINT_QUIZ = {
    "l1a_03": "l1e_blot",
    "l1a_06": "l1e_mix",
    "l1a_09": "l1e_ppe",
    "l1b_coffee": "l1e_oxygen",
    "l1b_mud": "l1e_heat",
    "l1d_grades": "l1e_refuse",
}

_STAIN_HINT_RE = re.compile(
    r"얼룩|셔츠|블라우스|혈액|커피|와인|기름|잉크|"
    r"vết|máu|cà\s*phê|cà phê|áo |giặt|blot|stain",
    re.I,
)


def _looks_like_stain_question(raw: str) -> bool:
    t = (raw or "").strip()
    if len(t) >= 24:
        return True
    if _STAIN_HINT_RE.search(t) and len(t) >= 8:
        return True
    return False


def _l1_bank_item(qid: str) -> Optional[dict[str, Any]]:
    from l1_exam_bank import L1_BANK_KO

    for it in L1_BANK_KO:
        if str(it.get("id") or "") == qid:
            return it
    return None


def _quiz_prompt(qid: str, lang: str) -> str:
    from exam_i18n import localized_bank_item

    it = _l1_bank_item(qid)
    if not it:
        return ""
    loc = localized_bank_item(it, lang, "l1_bank")
    q = loc.get("q") or it.get("q") or ""
    if lang == "en":
        return (
            "◆ Checkpoint (1 question)\n"
            "You cannot skip with 「next」 until this is correct.\n"
            "Urgent stain: just type the stain (this quiz waits).\n\n"
            f"{q}"
        )
    if lang == "vi":
        return (
            "◆ Câu hỏi chốt (1 câu)\n"
            "Chưa đúng thì chưa sang trang (「tiếp」 không bỏ qua).\n"
            "Vết bẩn gấp: gửi câu hỏi vết bẩn (câu này chờ).\n\n"
            f"{q}"
        )
    return (
        "◆ 확인 문제 (1문항)\n"
        "맞히기 전에는 「다음」으로 넘어가지 않습니다.\n"
        "지금 얼룩이 급하면, 얼룩 질문을 그냥 보내 주세요. (이 문제는 나중에)\n\n"
        f"{q}"
    )


def _grade_checkpoint(qid: str, raw: str, lang: str) -> bool:
    from exam_i18n import localized_bank_item
    from learning_quiz import _match_accept

    it = _l1_bank_item(qid)
    if not it:
        return False
    loc = localized_bank_item(it, lang, "l1_bank")
    accept = str(loc.get("accept") or it.get("accept") or "")
    return _match_accept(raw, accept)


def _quiz_explain(qid: str, lang: str) -> str:
    from exam_i18n import localized_bank_item

    it = _l1_bank_item(qid)
    if not it:
        return ""
    loc = localized_bank_item(it, lang, "l1_bank")
    return str(loc.get("explain") or it.get("explain") or "")


def _after_lesson_advance(user_id: str, st: dict[str, Any], lang: str) -> str:
    """Mark current page done; maybe checkpoint quiz; else next page or finish."""
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
        return _quiz_prompt(qid, lang)

    if idx + 1 >= len(LESSONS):
        st["active"] = False
        st["index"] = len(LESSONS) - 1
        st["pending_quiz"] = None
        _save_state(user_id, st)
        if lang == "ko":
            return (
                "◆ 세탁 초급 내용을 모두 읽으셨습니다.\n"
                f"읽은 내용: {len(completed)}/{len(LESSONS)}\n"
                f"확인 문제: {len(passed)}개 통과\n\n"
                "이제 실제 옷·얼룩을 그냥 물어보시면 됩니다.\n"
                "중급 「중급」 → 고급 「고급」 순서로 이어서 배울 수 있습니다.\n\n"
                "다시 보고 싶을 때: 「교육」\n"
                "시험 점수 볼 때: 「시험 성적」\n"
                "안내 메뉴: 「모드」\n"
                "사진 연습: 「사진과제」"
            )
        if lang == "en":
            return (
                f"◆ Beginner lessons finished ({len(completed)}/{len(LESSONS)}).\n"
                "Ask about stains anytime. Review: 「교육」."
            )
        return (
            f"◆ Đã đọc xong bài cơ bản ({len(completed)}/{len(LESSONS)}).\n"
            "Có thể hỏi vết bẩn. Xem lại: 「교육」."
        )

    st["index"] = idx + 1
    st["pending_quiz"] = None
    _save_state(user_id, st)
    return _render_lesson(st["index"], lang, done_n=len(completed))
LESSONS: list[dict[str, str]] = [
    {
        "id": "l1a_01",
        "title": "섬유 라벨 30초",
        "body": (
            "[L1] 삼각형(표백)·원(드라이만)·손세탁 표시를 먼저 보세요.\n"
            "광택+얇음+미끈하면 실크·아세테이트 의심 → 강한 약품은 전부 보류하세요."
        ),
    },
    {
        "id": "l1a_02",
        "title": "물 온도 4단계",
        "body": (
            "[L1] 찬물 15–20°C / 미온 30–35°C / 온수 40–50°C / 고온 60°C+.\n"
            "단백질(피·계란·우유·땀·구토 등)은 무조건 찬물. 의심되면 찬물부터."
        ),
    },
    {
        "id": "l1a_03",
        "title": "문지름 금지 · 찍어 바름",
        "body": (
            "[L1] 흰 면 천을 얼룩 위에 얹고 수직으로만 눌러 흡수하세요. 매번 새 면.\n"
            "옆으로 문지르면 색소·오일이 깊게 들어갑니다. 색소 계열은 처음 3분은 블롯만."
        ),
    },
    {
        "id": "l1a_04",
        "title": "건조 전 강광 확인",
        "body": (
            "[L1] 밝은 빛 아래에서 잔색·기름 미끄럼·냄새를 확인하세요.\n"
            "하나라도 있으면 건조기·다림질·햇빛 금지. 열 = 영구 고착입니다."
        ),
    },
    {
        "id": "l1a_05",
        "title": "구석 테스트 30초",
        "body": (
            "[L1] 밑단·안감·솔기에 약품 1–2방울 → 흰 천으로 30초.\n"
            "색빠짐·번짐·손상이 없어야 진행. 알코올·아세톤·용제·산소·옥살산은 테스트 없이 금지."
        ),
    },
    {
        "id": "l1a_06",
        "title": "절대 혼합 금지 3쌍",
        "body": (
            "[L1] 식초+락스 / 암모니아+락스 / 산소표백+락스 — 위험하거나 효과가 사라집니다.\n"
            "락스 쓴 통·솔은 완전히 헹군 뒤에만 다른 약품을 쓰세요."
        ),
    },
    {
        "id": "l1a_07",
        "title": "보호구 3종",
        "body": (
            "[L1] 니트릴 장갑(피·구토·용제·옥살산·락스) / 마스크(포자·먼지) / 환기(용제·락스).\n"
            "밀폐 공간에서 용제·락스 작업을 하지 마세요."
        ),
    },
    {
        "id": "l1a_08",
        "title": "거절 게이트 6조합",
        "body": (
            "[L1→L3] 아래면 초보 단독 금지 — 접수 시 불가 고지 후 진행 또는 거절:\n"
            "① 실크·울·가죽·아세테이트 + 유성페인트/유성매직/502\n"
            "② 건조기 지난 이염 ③ 깊이 밴 오래된 곰팡이\n"
            "④ 성분 미상 화학 ⑤ 실크·울의 엔진오일·타르 ⑥ 가죽·모피의 유기용제 필요 얼룩"
        ),
    },
    {
        "id": "l1a_09",
        "title": "도구 5종",
        "body": (
            "[L1] 흰 면 천·키친타월 / 200ml 분무기 / 부드러운 솔(아기 칫솔급) /\n"
            "얕은 담금통 / 타이머. 색 있는 천·강모·철사 솔·눈짐작 금지."
        ),
    },
    {
        "id": "l1a_10",
        "title": "약품 4대 그룹",
        "body": (
            "[L1→L2] 효소 — 실크·울 금지, 40°C 초과 시 실활.\n"
            "산소 — 흰 면·폴리·안정 유색만. 염소 — 흰 면·폴리만.\n"
            "용제 — 아세테이트·레이온·비닐코팅 금지, 구석 테스트·환기 필수."
        ),
    },
    {
        "id": "l1b_blood",
        "title": "대표 얼룩 · 피(신선)",
        "body": (
            "[L1] 안쪽 찬물 2–3분 → 소금물(1L+큰술2) 15–30분 → 효소 15분(실크·울 금지)\n"
            "→ 찬물 세탁 → 강광. 온수·건조기 절대 금지. 세게 문지르지 마세요."
        ),
    },
    {
        "id": "l1b_coffee",
        "title": "대표 얼룩 · 블랙커피(신선)",
        "body": (
            "[L1] 안쪽 찬물 블롯 → 흰 식초 1:4(식초40+물160) 5–10분\n"
            "→ 흰 면만 산소 15–30분(구석 테스트) → 미온 세탁 → 강광. 실크·울에 산소 금지."
        ),
    },
    {
        "id": "l1b_oil",
        "title": "대표 얼룩 · 식용유(신선)",
        "body": (
            "[L1] 전분·밀가루 10–30분 → 털기 → 주방세제 1–2방울 미온 5–10분, 솔 가볍게\n"
            "→ 헹굼 → 세탁 → 미끄럼 없어진 뒤에만 건조."
        ),
    },
    {
        "id": "l1b_ink",
        "title": "대표 얼룩 · 볼펜(신선)",
        "body": (
            "[L1] 70% 이소프로판올 구석 테스트 → 흡수지 깔고 안쪽에서 찍어 수직 블롯\n"
            "(매번 새 흰 천) → 찬물 세탁 → 강광. 문지름 금지(번짐)."
        ),
    },
    {
        "id": "l1b_mud",
        "title": "대표 얼룩 · 진흙(마름)",
        "body": (
            "[L1] 완전 건조 → 실외 털기·부드러운 솔 → 세제 세탁\n"
            "→ 잔색이면 흰 식초 1:4 → 강광. 젖은 채 문지르지 마세요. 붉은 적토는 L3 경로."
        ),
    },
    {
        "id": "l1c_intake",
        "title": "접수 3분",
        "body": (
            "[L1] ① 얼룩·언제·이미 세탁했는지 ② 원단·색상\n"
            "③ 성공률 3단(시도/부분/불가) + 사진 동의\n"
            "④ 실크·울·가죽·아세테이트는 상급 확인."
        ),
    },
    {
        "id": "l1d_grades",
        "title": "거절 3단 문구",
        "body": (
            "[L1] 등급1: 시도할 수 있으나 완전 제거는 보장하기 어렵습니다.\n"
            "등급2: 완전 제거는 어렵고 잔색이 남을 수 있습니다. 진행할까요?\n"
            "등급3: 매장에서 안전하게 처리하기 어렵습니다. 전문 의뢰를 안내합니다."
        ),
    },
]


def _state(user_id: str) -> dict[str, Any]:
    data = load_user(user_id)
    st = data.get("l1_course")
    if not isinstance(st, dict):
        st = {"active": False, "index": 0, "completed": [], "updated_at": time.time()}
    st.setdefault("active", False)
    st.setdefault("index", 0)
    st.setdefault("completed", [])
    if not isinstance(st["completed"], list):
        st["completed"] = []
    st.setdefault("quiz_passed", [])
    if not isinstance(st["quiz_passed"], list):
        st["quiz_passed"] = []
    st.setdefault("pending_quiz", None)
    return st


def _save_state(user_id: str, st: dict[str, Any]) -> None:
    data = load_user(user_id)
    st = dict(st)
    st["updated_at"] = time.time()
    data["l1_course"] = st
    save_user(user_id, data)
    try:
        from course_progress_sync import push_course_progress

        push_course_progress(user_id)
    except Exception:
        pass


def deactivate_course(user_id: str) -> None:
    st = _state(user_id)
    if not st.get("active"):
        return
    st["active"] = False
    _save_state(user_id, st)


def is_l1_course_command(text: str) -> bool:
    raw = (text or "").strip()
    return bool(
        _START_RE.match(raw)
        or _NEXT_RE.match(raw)
        or _PROGRESS_RE.match(raw)
        or _EXIT_RE.match(raw)
        or _LEVEL_RE.match(raw)
    )


def l1_quiz_counts(user_id: str) -> tuple[int, int]:
    st = _state(user_id)
    passed = {str(x) for x in (st.get("quiz_passed") or []) if x}
    total = len(_CHECKPOINT_QUIZ)
    return len(passed), total


def l1_done_count(user_id: str) -> int:
    st = _state(user_id)
    done = {str(x) for x in (st.get("completed") or [])}
    return sum(1 for les in LESSONS if les["id"] in done)


def is_l1_complete(user_id: str) -> bool:
    return l1_done_count(user_id) >= len(LESSONS)


def _level_gate_reply(user_id: str, text: str, lang: str) -> str:
    raw = (text or "").strip()
    want_l3 = bool(re.search(r"고급|L3|advanced|cao\s*cấp", raw, re.I))
    level_name = "고급" if want_l3 else "중급"
    if lang == "en":
        level_name = "advanced" if want_l3 else "intermediate"
    if lang == "vi":
        level_name = "cao cấp" if want_l3 else "trung cấp"

    done = l1_done_count(user_id)
    total = len(LESSONS)

    if not is_l1_complete(user_id):
        if lang == "ko":
            return (
                f"◆ {level_name}은 아직 차례가 아니에요.\n\n"
                f"먼저 초급을 끝까지 읽어 주세요. (지금 {done}/{total})\n"
                "초급을 이어가려면 「교육」이라고 보내 주세요.\n"
                "다 읽은 뒤에는 「중급」또는 「고급」을 다시 보내시면 됩니다.\n\n"
                "※ 지금 당장 옷·얼룩이 급하면, 초급을 안 마쳐도 「현장」으로 물어보시면 됩니다."
            )
        if lang == "en":
            return (
                f"◆ {level_name.title()} comes after beginner.\n"
                f"Finish beginner first ({done}/{total}). Send 「교육」 to continue.\n"
                "Urgent stain help anytime: 「field」."
            )
        return (
            f"◆ {level_name.capitalize()} sau bài cơ bản.\n"
            f"Hãy đọc xong cơ bản trước ({done}/{total}). Gửi 「교육」.\n"
            "Hỏi vết bẩn gấp: 「hiện trường」."
        )

    # L1 complete — L2/L3 courses are live (handled by l2/l3 modules when wired first)
    if lang == "ko":
        if want_l3:
            return (
                "◆ 초급은 모두 마치셨네요. 고맙습니다.\n\n"
                "고급은 중급을 마친 뒤에 열려요.\n"
                "먼저 「중급」을 보내 중급을 끝낸 뒤, 「고급」을 보내 주세요.\n\n"
                "초급 다시 보기: 「교육」 · 시험 점수: 「시험 성적」"
            )
        return (
            "◆ 초급은 모두 마치셨네요. 고맙습니다.\n\n"
            "중급을 시작하려면 「중급」이라고 보내 주세요.\n"
            "한 장씩 읽고 「다음」으로 이어갑니다.\n\n"
            "초급 다시 보기: 「교육」 · 시험 점수: 「시험 성적」"
        )
    if lang == "en":
        return (
            "◆ Beginner complete — thank you.\n"
            f"Page-by-page {level_name} lessons will open soon.\n"
            "For now, ask real stains anytime (「field」)."
        )
    return (
        "◆ Đã xong bài cơ bản — cảm ơn.\n"
        f"Bài {level_name} từng trang sẽ mở sớm.\n"
        "Hiện hỏi vết bẩn bình thường (「hiện trường」)."
    )


def _render_lesson(idx: int, lang: str, *, done_n: int) -> str:
    from course_i18n import lesson_title_body

    total = len(LESSONS)
    lesson = LESSONS[idx]
    title, body = lesson_title_body(lesson, lang)
    n = idx + 1
    if lang == "en":
        return (
            f"◆ Beginner lesson {n} of {total}\n"
            f"{title}\n\n"
            f"{body}\n\n"
            f"Finished so far: {done_n} of {total}\n"
            "When you finish reading, send 「next」 for the next page.\n"
            "To stop for now: 「end course」 · Need help with a real stain now: 「field」"
        )
    if lang == "vi":
        return (
            f"◆ Bài cơ bản {n}/{total}\n"
            f"{title}\n\n"
            f"{body}\n\n"
            f"Đã đọc xong: {done_n}/{total}\n"
            "Đọc xong thì gửi 「tiếp」 để sang trang sau.\n"
            "Dừng tạm: 「kết thúc học」 · Cần hỏi vết bẩn ngay: 「hiện trường」"
        )
    return (
        f"◆ 세탁 초급 배우기 ({n}/{total})\n"
        f"【{lesson['title']}】\n\n"
        f"{lesson['body']}\n\n"
        f"지금까지 읽은 내용: {done_n}/{total}\n"
        "다 읽으셨으면 「다음」이라고 보내 주세요. 다음 내용이 나옵니다.\n"
        "오늘은 여기까지 하시려면 「교육 끝」\n"
        "지금 당장 옷·얼룩이 급하면 「현장」"
    )


def _progress_msg(st: dict[str, Any], lang: str) -> str:
    done = {str(x) for x in (st.get("completed") or [])}
    n = sum(1 for les in LESSONS if les["id"] in done)
    total = len(LESSONS)
    idx = int(st.get("index") or 0)
    active = bool(st.get("active"))
    if lang == "en":
        return (
            f"◆ Beginner progress: {n} of {total} finished\n"
            f"{'You are learning now.' if active else 'You paused.'} "
            f"Page {min(idx + 1, total)} of {total}.\n"
            "Continue: send 「교육」 or 「L1 course」 · Next page: 「next」"
        )
    if lang == "vi":
        return (
            f"◆ Tiến độ: đã xong {n}/{total}\n"
            f"{'Đang học.' if active else 'Đã dừng tạm.'} "
            f"Trang {min(idx + 1, total)}/{total}.\n"
            "Học tiếp: gửi 「교육」 · Trang sau: 「tiếp」"
        )
    cur = min(idx + 1, total)
    if active:
        status = f"지금 초급 내용을 보고 계십니다. ({cur}/{total}번째)"
    else:
        status = f"초급 배우기를 잠시 멈추신 상태입니다. (마지막 위치 {cur}/{total})"
    return (
        f"◆ 세탁 초급, 어디까지 보셨나요\n"
        f"읽은 내용: {n}/{total}\n"
        f"{status}\n\n"
        "다시 이어서 보려면 「교육」이라고 보내 주세요.\n"
        "이미 배우는 중이라면, 다음 장으로 「다음」이라고 보내 주세요."
    )


def try_handle_l1_course(user_id: str, text: str) -> Optional[str]:
    """Handle L1 course navigation. None → continue to other handlers / GraphRAG."""
    raw = (text or "").strip()
    if not user_id or not raw:
        return None
    lang = detect_reply_lang(raw)

    st_now = _state(user_id)
    pending = st_now.get("pending_quiz")
    if pending and not is_l1_course_command(raw):
        if _looks_like_stain_question(raw):
            return None
        if _grade_checkpoint(str(pending), raw, lang):
            passed = [str(x) for x in (st_now.get("quiz_passed") or [])]
            if str(pending) not in passed:
                passed.append(str(pending))
            st_now["quiz_passed"] = passed
            st_now["pending_quiz"] = None
            explain = _quiz_explain(str(pending), lang)
            nxt = _after_lesson_advance(user_id, st_now, lang)
            if lang == "en":
                return f"◆ Correct.\n{explain}\n\n{nxt}"
            if lang == "vi":
                return f"◆ Đúng.\n{explain}\n\n{nxt}"
            return f"◆ 맞았습니다.\n{explain}\n\n{nxt}"
        explain = _quiz_explain(str(pending), lang)
        again = _quiz_prompt(str(pending), lang)
        if lang == "en":
            return f"◆ Not yet.\n{explain}\n\n{again}"
        if lang == "vi":
            return f"◆ Chưa đúng.\n{explain}\n\n{again}"
        return f"◆ 아직 아닙니다.\n{explain}\n\n다시:\n{again}"

    if _PROGRESS_RE.match(raw):
        return _progress_msg(_state(user_id), lang)

    if _LEVEL_RE.match(raw):
        return _level_gate_reply(user_id, raw, lang)

    if _EXIT_RE.match(raw):
        deactivate_course(user_id)
        if lang == "en":
            return (
                "◆ Beginner lessons are paused.\n"
                "You can still ask about stains anytime.\n"
                "To continue later, send 「교육」."
            )
        if lang == "vi":
            return (
                "◆ Đã tạm dừng bài cơ bản.\n"
                "Vẫn hỏi được về vết bẩn.\n"
                "Học tiếp sau: gửi 「교육」."
            )
        return (
            "◆ 초급 배우기를 잠시 멈췄습니다.\n"
            "괜찮습니다. 얼룩·옷 질문은 평소처럼 그냥 보내시면 됩니다.\n"
            "나중에 초급을 다시 이어서 보시려면 「교육」이라고 보내 주세요."
        )

    if _START_RE.match(raw):
        try:
            from l2_course import deactivate_l2_course
            from l3_course import deactivate_l3_course

            deactivate_l2_course(user_id)
            deactivate_l3_course(user_id)
        except Exception:
            pass
        st = _state(user_id)
        done = {str(x) for x in (st.get("completed") or [])}
        # Resume at first incomplete, else restart from 0 if all done
        idx = 0
        for i, les in enumerate(LESSONS):
            if les["id"] not in done:
                idx = i
                break
        else:
            # all complete — allow review from start without clearing completion
            idx = 0
        st["active"] = True
        st["index"] = idx
        _save_state(user_id, st)
        head = ""
        if lang == "ko":
            if done:
                head = (
                    "◆ 세탁 초급, 이어서 배워 볼게요.\n"
                    f"이미 읽으신 내용: {len(done)}/{len(LESSONS)}\n\n"
                    "순서: 기본 습관 → 자주 오는 얼룩 5가지 → 손님에게 어떻게 말할지\n"
                    "한 장씩 읽고, 다 읽으면 「다음」이라고 보내 주세요.\n"
                    "지금 당장 얼룩이 급하면 「현장」또는 「교육 끝」이라고 보내시면 됩니다.\n\n"
                )
            else:
                head = (
                    "◆ 세탁 초급 배우기를 시작합니다.\n\n"
                    "처음 오셔도 괜찮습니다. 짧게, 한 장씩만 보여 드릴게요.\n"
                    "순서: 기본 습관 → 자주 오는 얼룩 5가지 → 손님에게 어떻게 말할지\n"
                    f"전부 {len(LESSONS)}장입니다.\n\n"
                    "읽는 동안은 「다음」이라고만 보내시면 됩니다.\n"
                    "중간에 실제 옷·얼룩이 급하면 「현장」또는 「교육 끝」이라고 보내 주세요.\n\n"
                )
        elif lang == "en":
            head = (
                "◆ Starting beginner laundry lessons.\n"
                "Read one short page, then send 「next」.\n"
                "Urgent stain help: 「field」.\n\n"
            )
        else:
            head = (
                "◆ Bắt đầu bài giặt cơ bản.\n"
                "Đọc từng trang ngắn, rồi gửi 「tiếp」.\n"
                "Hỏi vết bẩn gấp: 「hiện trường」.\n\n"
            )
        if st.get("pending_quiz"):
            _save_state(user_id, st)
            return head + _quiz_prompt(str(st["pending_quiz"]), lang)
        return head + _render_lesson(idx, lang, done_n=len(done))

    if _NEXT_RE.match(raw):
        st = _state(user_id)
        if st.get("pending_quiz"):
            return _quiz_prompt(str(st["pending_quiz"]), lang)
        if not st.get("active"):
            if lang == "ko":
                return (
                    "◆ 아직 초급 배우기를 시작하지 않으셨어요.\n\n"
                    "시작하려면 「교육」이라고 보내 주세요.\n"
                    "그러면 세탁 초급 내용이 한 장씩 나옵니다.\n\n"
                    "「다음」은, 교육을 이미 시작한 뒤에\n"
                    "‘다음 장 보여 주세요’라고 할 때 쓰는 말입니다.\n"
                    "지금은 먼저 「교육」을 보내 주세요."
                )
            if lang == "en":
                return (
                    "◆ You have not started the beginner lessons yet.\n"
                    "Send 「교육」 to start.\n"
                    "Send 「next」 only after lessons have started, to see the next page."
                )
            return (
                "◆ Bạn chưa bắt đầu bài cơ bản.\n"
                "Gửi 「교육」 để bắt đầu.\n"
                "「tiếp」 dùng sau khi đã bắt đầu, để xem trang sau."
            )
        return _after_lesson_advance(user_id, st, lang)

    return None
