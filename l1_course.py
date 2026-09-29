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
    r"l1\s*course|beginner\s*course|khóa\s*l1|hoc\s*l1"
    r")\s*$",
    re.I,
)
_NEXT_RE = re.compile(
    r"^\s*(다음|다음\s*장|next|tiếp|tiep)\s*$",
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


# Static curriculum excerpts (Zalo-sized). Source: CURRICULUM_L1_L2_L3.md — copy, not live SOP rewrite.
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
    return st


def _save_state(user_id: str, st: dict[str, Any]) -> None:
    data = load_user(user_id)
    st = dict(st)
    st["updated_at"] = time.time()
    data["l1_course"] = st
    save_user(user_id, data)


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
    )


def _render_lesson(idx: int, lang: str, *, done_n: int) -> str:
    total = len(LESSONS)
    lesson = LESSONS[idx]
    n = idx + 1
    if lang == "en":
        return (
            f"◆ L1 lesson ({n}/{total})\n"
            f"{lesson['title']}\n\n"
            f"{lesson['body']}\n\n"
            f"Progress: {done_n}/{total} done · 「next」 · 「end course」 · field: 「field」"
        )
    if lang == "vi":
        return (
            f"◆ Bài L1 ({n}/{total})\n"
            f"{lesson['title']}\n\n"
            f"{lesson['body']}\n\n"
            f"Tiến độ: {done_n}/{total} · 「tiếp」 · 「kết thúc học」 · 「hiện trường」"
        )
    return (
        f"◆ L1 초급 교육 ({n}/{total})\n"
        f"【{lesson['title']}】\n\n"
        f"{lesson['body']}\n\n"
        f"진도 {done_n}/{total} · 「다음」 · 「교육 끝」 · 현장 질문은 「현장」"
    )


def _progress_msg(st: dict[str, Any], lang: str) -> str:
    done = {str(x) for x in (st.get("completed") or [])}
    n = sum(1 for les in LESSONS if les["id"] in done)
    total = len(LESSONS)
    idx = int(st.get("index") or 0)
    active = bool(st.get("active"))
    if lang == "en":
        return (
            f"◆ L1 progress: {n}/{total}\n"
            f"{'In course' if active else 'Paused'} · current step {min(idx + 1, total)}/{total}\n"
            "「L1 course」 to resume · 「next」 while in course"
        )
    if lang == "vi":
        return (
            f"◆ Tiến độ L1: {n}/{total}\n"
            f"{'Đang học' if active else 'Tạm dừng'} · bước {min(idx + 1, total)}/{total}\n"
            "「khóa L1」 để tiếp tục"
        )
    return (
        f"◆ L1 초급 진도: {n}/{total}\n"
        f"{'진행 중' if active else '일시 중지'} · 현재 {min(idx + 1, total)}/{total}단원\n"
        "이어가기: 「교육」 · 다음 장: 「다음」"
    )


def try_handle_l1_course(user_id: str, text: str) -> Optional[str]:
    """Handle L1 course navigation. None → continue to other handlers / GraphRAG."""
    raw = (text or "").strip()
    if not user_id or not raw:
        return None
    lang = detect_reply_lang(raw)

    if _PROGRESS_RE.match(raw):
        return _progress_msg(_state(user_id), lang)

    if _EXIT_RE.match(raw):
        deactivate_course(user_id)
        if lang == "en":
            return "◆ L1 course paused. Ask stains anytime. Resume: 「L1 course」."
        if lang == "vi":
            return "◆ Đã tạm dừng khóa L1. Hỏi vết bẩn bình thường. Tiếp: 「khóa L1」."
        return "◆ 초급 교육을 잠시 멈췄습니다. 얼룩 질문은 그대로 가능합니다. 이어가기: 「교육」"

    if _START_RE.match(raw):
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
            head = (
                "◆ L1 초급 교육을 시작합니다.\n"
                "기초 → 대표 5얼룩 → 접수·거절 문구 순서입니다.\n"
                "현장 질문이 급하면 「현장」또는 「교육 끝」.\n\n"
            )
        elif lang == "en":
            head = "◆ Starting L1 course. Urgent stains: 「field」.\n\n"
        else:
            head = "◆ Bắt đầu khóa L1. Gấp: 「hiện trường」.\n\n"
        return head + _render_lesson(idx, lang, done_n=len(done))

    if _NEXT_RE.match(raw):
        st = _state(user_id)
        if not st.get("active"):
            if lang == "ko":
                return "◆ 교육이 열려 있지 않습니다. 「교육」이라고 보내 주세요."
            if lang == "en":
                return "◆ Course not open. Send 「L1 course」."
            return "◆ Chưa mở khóa. Gửi 「khóa L1」."

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
                    "◆ L1 초급 교육 완료\n"
                    f"진도 {len(completed)}/{len(LESSONS)}\n\n"
                    "이제 현장 모드에서 얼룩을 물어보세요.\n"
                    "복습: 「교육」 · 성적: 「시험 성적」 · 모드: 「모드」"
                )
            if lang == "en":
                return f"◆ L1 complete ({len(completed)}/{len(LESSONS)}). Ask stains anytime."
            return f"◆ Hoàn thành L1 ({len(completed)}/{len(LESSONS)})."

        st["index"] = idx + 1
        _save_state(user_id, st)
        return _render_lesson(st["index"], lang, done_n=len(completed))

    return None
