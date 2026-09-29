# -*- coding: utf-8 -*-
"""Weekly education exam — Zalo delivery + grading (low AI cost).

- Primary: fixed L1 curriculum bank (mastery) + 70% pass line
- Fallback: personal/OPS deck, then optional AI from Q&A log
- Time limit enforced server-side via deadline_at
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from urllib.parse import quote
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from learning_quiz import _match_accept, build_deck
from l1_exam_bank import pass_threshold, sample_l1_exam_questions
from l2_course import is_l2_complete
from l2_exam_bank import sample_l2_exam_questions
from owner_qa_log import load_user
from reply_lang import detect_reply_lang

# In-memory cursor: participant_id -> current question index
_exam_cursor: dict[str, int] = {}


def _hq_base() -> str:
    return (
        os.environ.get("WF_HQ_API_BASE")
        or os.environ.get("WASHFRIENDS_API_BASE")
        or ""
    ).strip().rstrip("/")


def _hq_secret() -> str:
    return (
        os.environ.get("EDUCATION_BOT_INTERNAL_SECRET")
        or os.environ.get("INTERNAL_WEBHOOK_SECRET")
        or ""
    ).strip()


def _http_json(method: str, path: str, payload: Optional[dict] = None) -> dict:
    base = _hq_base()
    secret = _hq_secret()
    if not base or not secret:
        raise RuntimeError("HQ API not configured")
    url = f"{base}{path}"
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "X-Internal-Secret": secret,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", "replace")
        return json.loads(raw) if raw else {}


def _ai_generate_questions(user_id: str, n: int, lang: str) -> list[dict[str, str]]:
    """One gpt-4o-mini call. Returns [] on failure."""
    try:
        from openai import OpenAI
    except Exception:
        return []
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return []
    turns = load_user(user_id).get("turns") or []
    recent = turns[-12:]
    if not recent:
        return []
    blob = "\n---\n".join(
        f"Q: {t.get('q','')}\nA: {t.get('a','')[:400]}" for t in recent if isinstance(t, dict)
    )[:6000]
    lang_name = {"ko": "Korean", "vi": "Vietnamese", "en": "English"}.get(lang, "Korean")
    prompt = (
        f"You are a laundry shop education examiner. Based ONLY on the Q&A below, "
        f"create {n} short quiz questions in {lang_name} for the SAME owner.\n"
        "Return JSON array only: "
        '[{"q":"question text with A/B if useful","accept":"regex|keywords for correct","explain":"one-line correct reason"}]\n'
        "accept must match correct answers (e.g. a|찬물|cold). No markdown.\n\n"
        f"Q&A:\n{blob}"
    )
    try:
        client = OpenAI(api_key=key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
        )
        text = (resp.choices[0].message.content or "").strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I | re.M)
        arr = json.loads(text)
        out = []
        for i, it in enumerate(arr if isinstance(arr, list) else []):
            if not isinstance(it, dict):
                continue
            q = str(it.get("q") or "").strip()
            acc = str(it.get("accept") or "").strip()
            exp = str(it.get("explain") or "").strip()[:300]
            if len(q) < 8 or not acc:
                continue
            out.append({"id": f"ai{i+1}", "q": q, "accept": acc, "explain": exp, "lang": lang})
            if len(out) >= n:
                break
        return out
    except Exception as e:
        print(f"[WEEKLY EXAM] AI generate failed: {e}")
        return []


def build_exam_questions(user_id: str, n: int = 7, lang: str = "ko") -> list[dict[str, str]]:
    """Build weekly exam: L2 bank if L2 course done, else L1 bank.

    Does not change GraphRAG stain SOP paths — exam generation only.
    """
    n = max(5, min(10, int(n or 7)))
    lang = lang if lang in {"ko", "vi", "en"} else "ko"

    use_l2 = False
    try:
        use_l2 = bool(is_l2_complete(user_id))
    except Exception:
        use_l2 = False

    if use_l2:
        qs = sample_l2_exam_questions(n=n, lang=lang)
        # Pad with L1 if L2 bank somehow short
        if len(qs) < n:
            for it in sample_l1_exam_questions(n=n - len(qs), lang=lang):
                if len(qs) >= n:
                    break
                qs.append(it)
        if len(qs) >= n:
            return qs[:n]
    else:
        # Primary: L1 mastery (also for owners mid-L2)
        qs = sample_l1_exam_questions(n=n, lang=lang)
        if len(qs) >= n:
            return qs[:n]

    # Pad from personal/OPS deck if bank somehow short
    for c in build_deck(user_id, lang, size=n):
        if len(qs) >= n:
            break
        qs.append({
            "id": f"deck{len(qs)+1}",
            "q": c.get("q") or "",
            "accept": c.get("accept") or "",
            "explain": c.get("explain") or "",
            "lang": lang,
            "source": "deck",
        })
    if len(qs) >= max(3, n // 2):
        return qs[:n]

    # Last resort: previous AI path (optional enrichment — never required)
    ai = _ai_generate_questions(user_id, n - len(qs), lang)
    for it in ai:
        if len(qs) >= n:
            break
        it = dict(it)
        it["source"] = "ai"
        qs.append(it)
    return qs[:n]


def _exam_level_label(qs: list) -> str:
    sources = {
        str(it.get("source") or "")
        for it in qs
        if isinstance(it, dict)
    }
    if "l2_bank" in sources and "l1_bank" not in sources:
        return "l2"
    if "l2_bank" in sources:
        return "l2"
    return "l1"


def _finish_message(part: dict, lang: str) -> str:
    score = int(part.get("score") or 0)
    mx = int(part.get("max_score") or 0)
    qs = part.get("questions_json") or []
    passed = pass_threshold(score, mx, 0.7)
    need = max(1, min(mx, int((mx * 0.7) + 0.999))) if mx else 0
    level = _exam_level_label(qs if isinstance(qs, list) else [])
    wrong_lines = []
    for i, it in enumerate(qs):
        if not isinstance(it, dict):
            continue
        if it.get("correct") is False:
            wrong_lines.append(
                f"{i+1}) {it.get('explain') or it.get('accept') or ''}"
            )
    wrong_block = "\n".join(wrong_lines[:8])
    if lang == "ko":
        if passed:
            result = f"결과: 합격 (기준 {need}/{mx} 이상)\n"
        elif level == "l2":
            result = f"결과: 미합격 (합격 기준 {need}/{mx} — 중급 「중급」으로 복습해 주세요)\n"
        else:
            result = f"결과: 미합격 (합격 기준 {need}/{mx} — 초급 「교육」으로 복습해 주세요)\n"
        msg = f"◆ 시험 종료\n점수: {score}/{mx}\n{result}"
        if wrong_lines:
            msg += f"\n틀린 부분 복습:\n{wrong_block}\n"
        elif passed:
            msg += "\n모두 잘하셨습니다.\n"
        msg += "이제 일반 질문을 다시 보내셔도 됩니다."
        return msg
    if lang == "en":
        result = f"Result: PASS (need {need}/{mx})\n" if passed else f"Result: NOT YET (need {need}/{mx})\n"
        msg = f"◆ Exam finished\nScore: {score}/{mx}\n{result}"
        if wrong_lines:
            msg += f"\nReview:\n{wrong_block}\n"
        return msg + "You can ask normal questions again."
    result = f"Kết quả: ĐẠT (cần {need}/{mx})\n" if passed else f"Kết quả: CHƯA ĐẠT (cần {need}/{mx})\n"
    msg = f"◆ Kết thúc\nĐiểm: {score}/{mx}\n{result}"
    if wrong_lines:
        msg += f"\nÔn lại:\n{wrong_block}\n"
    return msg + "Có thể hỏi bình thường lại."


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def fetch_active_assignment(zalo_user_id: str) -> Optional[dict]:
    try:
        data = _http_json(
            "GET",
            f"/api/v1/internal/education-bot/exams/active-for-user?zalo_user_id={quote(zalo_user_id)}",
        )
        if data.get("active"):
            return data
    except Exception as e:
        print(f"[WEEKLY EXAM] active-for-user failed: {e}")
    return None


def patch_participant(participant_id: str, body: dict) -> dict:
    return _http_json(
        "PATCH",
        f"/api/v1/internal/education-bot/exams/participants/{participant_id}",
        body,
    )


def _render_q(idx: int, total: int, item: dict, lang: str, minutes_left: Optional[int] = None) -> str:
    timer = ""
    if minutes_left is not None:
        if lang == "ko":
            timer = f"남은 시간 약 {max(0, minutes_left)}분\n"
        elif lang == "en":
            timer = f"~{max(0, minutes_left)} min left\n"
        else:
            timer = f"Còn ~{max(0, minutes_left)} phút\n"
    if lang == "ko":
        return (
            f"◆ 주간 시험 ({idx}/{total})\n"
            f"{timer}"
            f"{item.get('q')}\n\n"
            "답만 보내 주세요. (시험 중에는 일반 질문이 잠시 중단됩니다)"
        )
    if lang == "en":
        return f"◆ Weekly exam ({idx}/{total})\n{timer}{item.get('q')}\n\nSend answer only."
    return f"◆ Thi tuần ({idx}/{total})\n{timer}{item.get('q')}\n\nChỉ gửi đáp án."


# Owner asking for past scores — must not be graded as an exam answer.
_HISTORY_INTENT_RE = re.compile(
    r"("
    r"시험\s*(성적|점수|결과|기록)|"
    r"(성적|점수)\s*(알려|확인|보|조회)|"
    r"몇\s*점|"
    r"틀린\s*(문제|문항|부분)|"
    r"exam\s*(score|result|grade|history)|"
    r"my\s*(score|exam)|"
    r"điểm\s*(thi|kiểm)|"
    r"kết\s*quả\s*(thi|kiểm)|"
    r"lịch\s*sử\s*thi"
    r")",
    re.I,
)

_MONTH_EN = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sept": 9,
    "sep": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


def is_exam_history_intent(text: str) -> bool:
    return bool(_HISTORY_INTENT_RE.search((text or "").strip()))


def _parse_year_month(text: str) -> tuple[Optional[int], Optional[int]]:
    raw = (text or "").strip()
    year: Optional[int] = None
    month: Optional[int] = None
    ym = re.search(r"(20\d{2})\s*년?\s*(\d{1,2})\s*월", raw)
    if ym:
        year = int(ym.group(1))
        month = int(ym.group(2))
        return year, month if 1 <= month <= 12 else None
    y_only = re.search(r"(20\d{2})\s*년", raw)
    if y_only:
        year = int(y_only.group(1))
    m = re.search(
        r"(?:^|[^\d])(\d{1,2})\s*월|(january|february|march|april|may|june|july|august|"
        r"september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)"
        r"|tháng\s*(\d{1,2})",
        raw,
        re.I,
    )
    if m:
        if m.group(1):
            month = int(m.group(1))
        elif m.group(2):
            key = m.group(2).lower()
            month = _MONTH_EN.get(key)
        elif m.group(3):
            month = int(m.group(3))
        if month is not None and not (1 <= month <= 12):
            month = None
    return year, month


def _fmt_started(iso: Optional[str]) -> str:
    if not iso:
        return ""
    try:
        # 2026-06-02T09:00:00+07:00 → 2026-06-02
        return str(iso)[:10]
    except Exception:
        return ""


def _format_history_reply(data: dict, lang: str, year: Optional[int], month: Optional[int]) -> str:
    exams = data.get("exams") if isinstance(data, dict) else None
    if not isinstance(exams, list) or not exams:
        if lang == "en":
            scope = f" for {year}-{month:02d}" if year and month else (" for that period" if year or month else "")
            return f"◆ No exam scores found{scope}."
        if lang == "vi":
            return "◆ Không có điểm thi đã lưu."
        if year and month:
            return f"◆ {year}년 {month}월에 기록된 시험 성적이 없습니다."
        if month:
            return f"◆ {month}월에 기록된 시험 성적이 없습니다."
        return "◆ 아직 제출·마감된 시험 성적이 없습니다."

    # Single exam detail when filtered or only one result
    detail_one = len(exams) == 1 or (month is not None)
    lines: list[str] = []
    if lang == "ko":
        head = "◆ 내 시험 성적"
        if year and month:
            head += f" ({year}년 {month}월)"
        elif month:
            head += f" ({month}월)"
        lines.append(head)
    elif lang == "en":
        lines.append("◆ My exam scores")
    else:
        lines.append("◆ Điểm thi của tôi")

    show = exams[:5]
    for ex in show:
        if not isinstance(ex, dict):
            continue
        score = int(ex.get("score") or 0)
        mx = int(ex.get("max_score") or 0)
        title = (ex.get("title") or ex.get("week_key") or "시험").strip()
        when = _fmt_started(ex.get("started_at"))
        st = ex.get("status") or ""
        st_ko = "제출" if st == "submitted" else ("시간초과" if st == "expired" else st)
        if lang == "ko":
            lines.append(f"\n· {when} {title}\n  점수: {score}/{mx} ({st_ko})")
        else:
            lines.append(f"\n· {when} {title}\n  {score}/{mx} ({st})")

        items = ex.get("items") if detail_one else None
        if not isinstance(items, list):
            continue
        wrong = [it for it in items if isinstance(it, dict) and it.get("correct") is False]
        if not wrong:
            if lang == "ko":
                lines.append("  틀린 문항 없음")
            continue
        if lang == "ko":
            lines.append("  틀린 문항:")
        for it in wrong[:8]:
            n = it.get("n") or "?"
            q = str(it.get("q") or "").replace("\n", " ")[:80]
            exp = str(it.get("explain") or "").replace("\n", " ")[:100]
            ans = str(it.get("user_answer") or "").replace("\n", " ")[:40]
            if lang == "ko":
                bit = f"  {n}) {q}"
                if ans:
                    bit += f"\n     내 답: {ans}"
                if exp:
                    bit += f"\n     요지: {exp}"
                lines.append(bit)
            else:
                lines.append(f"  {n}) {q} — {exp}")

    if len(exams) > 5 and lang == "ko":
        lines.append(f"\n(최근 {len(show)}건만 표시)")
    if lang == "ko" and not detail_one:
        lines.append("\n특정 달: 「6월 시험 성적」처럼 보내 주세요.")
    return "\n".join(lines).strip()


def try_handle_exam_history(user_id: str, text: str) -> Optional[str]:
    """If owner asks for past exam scores, return summary. Else None.

    Always queries ONLY this Zalo user_id (never accepts a third-party id).
    """
    raw = (text or "").strip()
    if not user_id or not raw or not is_exam_history_intent(raw):
        return None
    lang = detect_reply_lang(raw)

    # Don't interrupt an active exam with a history dump
    try:
        active = fetch_active_assignment(user_id)
    except Exception:
        active = None
    if active and (active.get("status") or "") in {"invited", "in_progress"}:
        if lang == "ko":
            return (
                "◆ 지금 시험이 진행 중입니다.\n"
                "시험이 끝난 뒤에 「시험 성적」이라고 보내 주세요."
            )
        if lang == "en":
            return "◆ Exam in progress. Ask for scores after you finish."
        return "◆ Đang thi. Hỏi điểm sau khi kết thúc."

    year, month = _parse_year_month(raw)
    # Default: recent few exams (no month → limit 5). Month filter → up to 20.
    limit = 20 if month is not None else 5
    qs = [
        f"zalo_user_id={quote(user_id)}",
        f"limit={limit}",
        "include_items=true",
    ]
    if year is not None:
        qs.append(f"year={int(year)}")
    if month is not None:
        qs.append(f"month={int(month)}")
    path = "/api/v1/internal/education-bot/exams/history-for-user?" + "&".join(qs)
    try:
        data = _http_json("GET", path)
    except Exception as e:
        print(f"[WEEKLY EXAM] history fetch failed: {e}")
        if lang == "ko":
            return "◆ 성적 조회에 실패했습니다. 잠시 후 다시 시도해 주세요."
        return "◆ Could not load exam history. Try again later."

    # Extra safety: API echoes zalo_user_id — ignore if mismatch
    echoed = str((data or {}).get("zalo_user_id") or "").strip()
    if echoed and echoed != user_id.strip():
        print("[WEEKLY EXAM] history zalo_user_id mismatch — refusing")
        return "◆ 성적 조회를 할 수 없습니다."

    return _format_history_reply(data or {}, lang, year, month)


def try_handle_exam_message(user_id: str, text: str) -> Optional[str]:
    """If user has an active weekly exam, consume message for grading. Else None."""
    raw = (text or "").strip()
    if not user_id or not raw:
        return None
    # Don't steal care-symbol show / quiz commands
    if re.search(
        r"(기호|크리닝|클리닝|케어\s*라벨|세탁\s*표시).{0,20}(보여|이미지|그림|퀴즈|시험)",
        raw,
        re.I,
    ):
        return None
    if is_exam_history_intent(raw):
        return None
    try:
        from l1_course import is_l1_course_command

        if is_l1_course_command(raw):
            return None
    except Exception:
        pass
    if re.fullmatch(
        r"(모드|mode|현장|학습|복습|field|learning|review|ôn|hiện\s*trường|기호\s*퀴즈)",
        raw,
        re.I,
    ):
        return None

    part = fetch_active_assignment(user_id)
    if not part:
        return None

    lang = detect_reply_lang(raw)
    pid = str(part.get("id") or "")
    qs = list(part.get("questions_json") or [])
    duration = int(part.get("duration_minutes") or 15)
    status = part.get("status") or "invited"

    # Expire check
    deadline = _parse_iso(part.get("deadline_at"))
    now = _utc_now()
    if deadline and now > deadline and status == "in_progress":
        # finalize as expired with current score
        patch_participant(
            pid,
            {
                "status": "expired",
                "submitted_at": now.isoformat(),
                "questions_json": qs,
                "score": int(part.get("score") or 0),
                "max_score": max(len(qs), int(part.get("max_score") or 0)),
            },
        )
        _exam_cursor.pop(pid, None)
        if lang == "ko":
            return (
                f"◆ 시험 시간 종료\n"
                f"점수: {int(part.get('score') or 0)}/{max(len(qs), int(part.get('max_score') or 0))}\n"
                "미완료 문항은 미응시 처리됩니다. 결과는 본사 HQ에 기록됩니다."
            )
        return "◆ Exam time over. Partial score recorded at HQ."

    # First touch: start clock if invited with questions ready
    if status == "invited":
        if not qs:
            # Still preparing — ask to wait or generate inline once
            try:
                qs = build_exam_questions(user_id, n=int(part.get("max_score") or 7), lang=lang)
                started = now
                deadline = started + timedelta(minutes=duration)
                patch_participant(
                    pid,
                    {
                        "status": "in_progress",
                        "questions_json": qs,
                        "max_score": len(qs),
                        "score": 0,
                        "started_at": started.isoformat(),
                        "deadline_at": deadline.isoformat(),
                    },
                )
                _exam_cursor[pid] = 0
                mins = duration
                return (
                    (f"◆ 주간 교육 시험 시작 ({len(qs)}문항, {duration}분)\n\n" if lang == "ko" else f"◆ Exam start ({len(qs)} Q, {duration}m)\n\n")
                    + _render_q(1, len(qs), qs[0], lang, minutes_left=mins)
                )
            except Exception as e:
                print(f"[WEEKLY EXAM] start gen failed: {e}")
                return None
        started = now
        deadline = started + timedelta(minutes=duration)
        patch_participant(
            pid,
            {
                "status": "in_progress",
                "started_at": started.isoformat(),
                "deadline_at": deadline.isoformat(),
            },
        )
        _exam_cursor[pid] = 0
        mins = duration
        return (
            (f"◆ 주간 교육 시험 시작 ({len(qs)}문항, {duration}분)\n\n" if lang == "ko" else f"◆ Exam start\n\n")
            + _render_q(1, len(qs), qs[0], lang, minutes_left=mins)
        )

    if status != "in_progress" or not qs:
        return None

    idx = int(_exam_cursor.get(pid, 0))
    if idx >= len(qs):
        return None

    item = qs[idx]
    ok = _match_accept(raw, item.get("accept") or "")
    item["user_answer"] = raw[:200]
    item["correct"] = bool(ok)
    qs[idx] = item
    score = sum(1 for x in qs if isinstance(x, dict) and x.get("correct") is True)
    idx += 1
    _exam_cursor[pid] = idx

    mins_left = None
    if deadline:
        mins_left = int(max(0, (deadline - now).total_seconds() // 60))

    if idx >= len(qs):
        updated = patch_participant(
            pid,
            {
                "status": "submitted",
                "score": score,
                "max_score": len(qs),
                "questions_json": qs,
                "submitted_at": now.isoformat(),
            },
        )
        _exam_cursor.pop(pid, None)
        part2 = (updated or {}).get("participant") or {
            "score": score,
            "max_score": len(qs),
            "questions_json": qs,
        }
        fb = ("○ 맞습니다.\n" if ok else "× 아쉽습니다.\n") if lang == "ko" else ("○\n" if ok else "×\n")
        return fb + _finish_message(part2, lang)

    patch_participant(
        pid,
        {
            "score": score,
            "max_score": len(qs),
            "questions_json": qs,
            "status": "in_progress",
        },
    )
    fb = ""
    if lang == "ko":
        fb = ("○ 맞습니다.\n\n" if ok else f"× 아쉽습니다. 요지: {item.get('explain') or ''}\n\n")
    else:
        fb = ("○\n\n" if ok else f"× {item.get('explain') or ''}\n\n")
    return fb + _render_q(idx + 1, len(qs), qs[idx], lang, minutes_left=mins_left)


def dispatch_week(week_id: str) -> dict:
    """Generate questions + send Zalo invite for each invited participant."""
    from zalo_handler import _send_zalo_reply  # local import — async needed by caller

    data = _http_json("GET", f"/api/v1/internal/education-bot/exams/{week_id}/participants")
    week = data.get("week") or {}
    parts = data.get("participants") or []
    n = int(week.get("question_count") or 7)
    duration = int(week.get("duration_minutes") or 15)
    results = {"ok": 0, "fail": 0, "items": []}
    return {
        "week": week,
        "participants": parts,
        "question_count": n,
        "duration_minutes": duration,
        "results": results,
        "_needs_async_send": True,
    }


async def dispatch_week_async(week_id: str, send_fn) -> dict:
    """send_fn(user_id, text) -> awaitable bool"""
    data = _http_json("GET", f"/api/v1/internal/education-bot/exams/{week_id}/participants")
    week = data.get("week") or {}
    parts = data.get("participants") or []
    n = int(week.get("question_count") or 7)
    duration = int(week.get("duration_minutes") or 15)
    title = week.get("title") or "주간 교육 시험"
    ok_n = fail_n = 0
    for p in parts:
        if (p.get("status") or "") not in {"invited", "error"}:
            continue
        uid = p.get("zalo_user_id") or ""
        pid = p.get("id") or ""
        try:
            qs = build_exam_questions(uid, n=n, lang="ko")
            level = _exam_level_label(qs)
            level_ko = "중급(L2)" if level == "l2" else "초급(L1)"
            patch_participant(
                pid,
                {
                    "questions_json": qs,
                    "max_score": len(qs),
                    "status": "invited",
                    "invite_error": None,
                },
            )
            msg = (
                f"◆ {title}\n"
                f"이번 주 {level_ko} 복습 시험입니다. {len(qs)}문항 · 제한 {duration}분\n"
                f"합격 기준: 약 70% ({max(1, int((len(qs) * 0.7) + 0.999))}/{len(qs)}문제 이상)\n"
                "아무 답이나 보내면 시험이 시작됩니다.\n"
                "(허용된 교육봇 사용자에게만 발송됩니다)"
            )
            await send_fn(uid, msg)
            ok_n += 1
        except Exception as e:
            fail_n += 1
            try:
                patch_participant(pid, {"status": "error", "invite_error": str(e)[:480]})
            except Exception:
                pass
            print(f"[WEEKLY EXAM] invite fail {uid}: {e}")
    return {"ok": True, "sent": ok_n, "failed": fail_n, "week_id": week_id}
