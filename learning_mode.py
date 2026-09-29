# -*- coding: utf-8 -*-
"""Field vs learning mode UX for education bot. No LLM."""
from __future__ import annotations

import re
from typing import Optional

from learning_quiz import grade_answer, start_quiz
from owner_qa_log import get_mode, get_quiz, set_mode
from reply_lang import detect_reply_lang

_MODE_CMD = re.compile(
    r"^\s*(모드|mode|모드\s*변경|đổi\s*chế\s*độ|doi\s*che\s*do)\s*$",
    re.I,
)
_FIELD_CMD = re.compile(
    r"^\s*(현장|현장\s*모드|field|field\s*mode|hiện\s*trường|hien\s*truong)\s*$",
    re.I,
)
_LEARN_CMD = re.compile(
    r"^\s*(학습|학습\s*모드|learning|learn|ôn\s*tập|on\s*tap|ôn|복습|review|quiz)\s*$",
    re.I,
)
_REVIEW_CMD = re.compile(
    r"^\s*(복습|다시\s*복습|review|ôn|ôn\s*lại|quiz)\s*$",
    re.I,
)
_CARE_SYMBOL_QUIZ_CMD = re.compile(
    r"^\s*("
    r"기호\s*퀴즈|기호\s*시험|세탁\s*표시\s*퀴즈|세탁\s*표시\s*시험|케어\s*라벨\s*퀴즈|케어라벨\s*퀴즈|"
    r"care\s*symbol\s*quiz|care\s*label\s*quiz|symbol\s*quiz|"
    r"ký\s*hiệu\s*quiz|ky\s*hieu\s*quiz|quiz\s*ký\s*hiệu|quiz\s*ky\s*hieu"
    r")\s*$",
    re.I,
)


def mode_menu(lang: str = "ko") -> str:
    if lang == "ko":
        return (
            "◆ Wash Friends 교육봇 모드\n"
            "\n"
            "① 현장 모드 — 지금 옷·얼룩 바로 질문 (기본)\n"
            "② 학습 모드 — 내 질문 위주로 짧게 복습 후 질문\n"
            "③ 기호 퀴즈 — 세탁표시 그림 보고 객관식·주관식\n"
            "④ 초급 교육 — L1 기초·대표얼룩 순서 학습 (「교육」)\n"
            "\n"
            "「현장」 / 「학습」 / 「기호퀴즈」 / 「교육」\n"
            "언제든 「모드」로 다시 열 수 있습니다."
        )
    if lang == "en":
        return (
            "◆ Education bot mode\n"
            "\n"
            "① Field — ask stains/labels now (default)\n"
            "② Learning — short review from YOUR past questions\n"
            "③ Symbol quiz — care-label pictures (MCQ + short answer)\n"
            "④ L1 course — beginner path (「L1 course」)\n"
            "\n"
            "Send 「field」 / 「learning」 / 「symbol quiz」 / 「L1 course」. 「mode」 anytime."
        )
    return (
        "◆ Chế độ bot đào tạo\n"
        "\n"
        "① Hiện trường — hỏi vết bẩn ngay (mặc định)\n"
        "② Học — ôn ngắn từ câu hỏi CỦA BẠN\n"
        "③ Quiz ký hiệu — ảnh nhãn giặt (trắc nghiệm + tự luận ngắn)\n"
        "④ Khóa L1 — lộ trình cơ bản (「khóa L1」)\n"
        "\n"
        "Gửi 「hiện trường」 / 「học」 / 「ký hiệu quiz」 / 「khóa L1」. 「mode」 bất cứ lúc nào."
    )


def _field_on(lang: str) -> str:
    if lang == "ko":
        return (
            "◆ 현장 모드 ON\n"
            "막히지 않고 바로 답합니다. 사진·케어라벨·얼룩을 보내 주세요.\n"
            "복습이 필요하면 「학습」또는 「복습」."
        )
    if lang == "en":
        return "◆ Field mode ON\nAsk freely. For review: 「learning」 or 「review」."
    return "◆ Hiện trường ON\nHỏi tự do. Ôn: 「học」 hoặc 「ôn」."


def _learn_on(lang: str, quiz_body: str) -> str:
    if lang == "ko":
        head = (
            "◆ 학습 모드 ON\n"
            "회원님이 물을 내용으로 복습합니다(추가 AI 비용 거의 없음).\n"
            "급하면 「현장」.\n\n"
        )
    elif lang == "en":
        head = "◆ Learning mode ON\nReview from your questions. Urgent: 「field」.\n\n"
    else:
        head = "◆ Chế độ học ON\nÔn từ câu hỏi của bạn. Gấp: 「hiện trường」.\n\n"
    return head + quiz_body


def try_handle_mode_or_quiz(user_id: str, text: str) -> Optional[str]:
    """
    Handle mode menu / switch / active quiz grading.
    Returns reply text, or None to continue to GraphRAG.
    """
    raw = (text or "").strip()
    if not raw or not user_id:
        return None
    lang = detect_reply_lang(raw)

    if _MODE_CMD.match(raw):
        return mode_menu(lang)

    if _FIELD_CMD.match(raw):
        set_mode(user_id, "field")
        return _field_on(lang)

    if _CARE_SYMBOL_QUIZ_CMD.match(raw):
        from care_label_quiz import start_care_symbol_quiz

        set_mode(user_id, "learning")
        return start_care_symbol_quiz(user_id, lang=lang, size=6)

    if _LEARN_CMD.match(raw) or _REVIEW_CMD.match(raw):
        set_mode(user_id, "learning")
        # 「복습」alone while already learning → restart quiz
        quiz_body = start_quiz(user_id, lang=lang, size=3)
        return _learn_on(lang, quiz_body)

    # Active quiz: consume answer (do not send to GraphRAG)
    if get_quiz(user_id):
        # allow escape phrases already handled above; anything else grades
        graded = grade_answer(user_id, raw)
        if graded is not None:
            return graded

    return None


def learning_footer(lang: str, mode: str) -> str:
    if mode != "learning":
        return ""
    if lang == "ko":
        return "\n\n— 학습 모드 · 복습: 「복습」 · 현장: 「현장」"
    if lang == "en":
        return "\n\n— Learning · 「review」 / 「field」"
    return "\n\n— Học · 「ôn」 / 「hiện trường」"


def maybe_append_footer(reply: str, user_id: str, user_text: str) -> str:
    mode = get_mode(user_id)
    if mode != "learning":
        return reply
    lang = detect_reply_lang(user_text or "")
    foot = learning_footer(lang, mode)
    if foot and foot.strip() not in (reply or ""):
        return (reply or "") + foot
    return reply
