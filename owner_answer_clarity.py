# -*- coding: utf-8 -*-
"""Owner Zalo clarity: 1통 흐름 / 2통 손동작 + short common blocks.

Does not change chemistry order — only presentation for junior staff.
"""
from __future__ import annotations

import re
from typing import Optional

# Invisible to owners in /ask (shown as blank line join); Zalo splits on this.
ZALO_MSG_SPLIT = "\n<<<ZALO_MSG2>>>\n"

BLOT_CHEM_CODES = frozenset({"A1", "A2", "D1"})

_SUPERVISOR = {
    "ko": "⚠️ 이 얼룩은 혼자 하지 마시고, 매니저(또는 경력 직원)와 확인한 뒤에 시작해 주세요.",
    "vi": "⚠️ Vết này cần giám sát. Hãy hỏi quản lý trước khi bắt đầu.",
    "en": "⚠️ Supervisor needed. Check with a manager before you start.",
}

_GRADE_FOOTER = {
    "ko": {
        1: "【다시 한번 고객 고지】 완전 제거는 보장드리기 어렵습니다. 잔색이 남을 수 있어요.",
        2: "【다시 한번 고객 고지】 완전 제거는 어렵고 잔색이 남을 수 있어요. 그래도 진행할까요?",
        3: "【다시 한번 고객 고지】 매장에서 안전하게 처리하기 어렵습니다. 전문 의뢰 또는 접수 반려를 안내해 주세요.",
    },
    "vi": {
        1: "【Nhắc khách】 Không đảm bảo sạch 100% — có thể còn vết mờ.",
        2: "【Nhắc khách】 Khó sạch hoàn toàn, có thể còn vết. Anh/Chị vẫn muốn tiếp tục chứ ạ?",
        3: "【Nhắc khách】 Cửa hàng khó xử lý an toàn — giới thiệu chuyên nghiệp hoặc từ chối tiếp nhận.",
    },
    "en": {
        1: "【Tell the guest again】 Full removal is not guaranteed — marks may remain.",
        2: "【Tell the guest again】 Full removal is unlikely — residual marks may remain. Still proceed?",
        3: "【Tell the guest again】 Unsafe in-store — refer out or decline the job.",
    },
}

# Compressed common don'ts (why one line each)
COMMON_DONTS_KO = [
    "뜨거운 물로 헹구지 마세요 → 얼룩이 섬유에 붙어 잘 안 빠져요",
    "세게 문지르지 마세요 → 번지고 원단이 상해요. 위에서 꾹꾹 눌러 흡수하세요",
    "약품을 옷에 직접 붓지 마세요 → 한쪽에 몰려 번져요. 흰 천에 묻혀 찍어 주세요",
    "다른 약품을 한꺼번에 섞지 마세요 → 한 약 쓰고 → 헹구고 → 다음 약 순서예요",
    "잔색 남은 채 건조기·다림질 하지 마세요 → 열이면 자국이 영구로 남아요",
]

STAIN_DONTS_KO: dict[str, list[str]] = {
    "S_HAIR_DYE": [
        "유색 옷에 산소표백제 쓰지 마세요",
        "실크·울·가죽에 알코올 함부로 쓰지 마세요 (구석 테스트 필수)",
        "물든 흰 천을 재사용하지 마세요 → 색소가 다시 옷으로 가요",
    ],
    "S_INK_PEN": [
        "락스(염소)로 잉크를 지우려 하지 마세요 → 회색 자국이 남을 수 있어요",
    ],
    "S_BLOOD_FRESH": [
        "뜨거운 물로 피를 헹구지 마세요 → 단백질이 굳어 더 안 빠져요",
    ],
    "S_BLOOD_DRY": [
        "뜨거운 물로 피를 헹구지 마세요 → 단백질이 굳어 더 안 빠져요",
    ],
}

STAIN_STATUS_KO: dict[str, str] = {
    "S_HAIR_DYE": (
        "◆ 【먼저 확인】 염색약이 어떤 상태인가요?\n"
        "· 아직 젖어 있다 → 아래 한 줄 순서 1번(찬물)부터 하세요\n"
        "· 이미 말랐다 → 찬물보다 알코올 찍기부터 하시고, 잔색 가능성을 고객께 먼저 말씀하세요\n"
        "· 다림질·건조기를 이미 거쳤다 → 거의 안 빠져요. 전문 의뢰 또는 정중히 거절해 주세요"
    ),
    "S_BLOOD_FRESH": (
        "◆ 【먼저 확인】 핏자국이 어떤 상태인가요?\n"
        "· 아직 젖어 있다(빨간빛) → 한 줄 순서 1번부터 하세요\n"
        "· 말라 갈색이다 → 마른 핏자국 요령으로 진행합니다(찬물·효소 중심)\n"
        "· 이미 뜨거운 물로 빨았다 → 거의 안 빠져요. 고객께 솔직히 말씀해 주세요"
    ),
}

_NEXT_MSG = {
    "ko": "📩 손동작·시간·금지 사항은 바로 다음 메시지에 이어서 보내 드릴게요.",
    "vi": "📩 Cách làm chi tiết sẽ gửi ngay tin nhắn tiếp theo.",
    "en": "📩 Hand-motion details follow in the next message.",
}

_DETAIL_HEAD = {
    "ko": "▼ 손동작 상세 — 위에서 아래로 하나씩 따라 해 주세요",
    "vi": "▼ Chi tiết thao tác — làm lần lượt từ trên xuống",
    "en": "▼ Hand-motion detail — follow top to bottom",
}


def _proto_dict(graph: dict) -> dict:
    p = graph.get("protocol") if isinstance(graph, dict) else None
    return p if isinstance(p, dict) else {}


def _stain_id(graph: dict) -> str:
    sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
    return str(graph.get("_owner_stain_id") or sc.get("id") or "")


def _chem_codes(graph: dict) -> set[str]:
    codes: set[str] = set()
    for c in graph.get("chemicals") or []:
        if isinstance(c, dict) and c.get("code"):
            codes.add(str(c["code"]).upper())
    proto = _proto_dict(graph)
    for s in proto.get("steps") or []:
        if isinstance(s, dict) and s.get("chem"):
            codes.add(str(s["chem"]).upper())
    return codes


def _soak_bounds(graph: dict) -> tuple[Optional[int], Optional[int]]:
    proto = _proto_dict(graph)
    for s in proto.get("steps") or []:
        if not isinstance(s, dict) or s.get("blocked"):
            continue
        if s.get("soak") and s.get("minutes_lo") is not None:
            return s.get("minutes_lo"), s.get("minutes_hi") or s.get("minutes_lo")
    for s in proto.get("steps") or []:
        if isinstance(s, dict) and s.get("minutes_lo") is not None:
            return s.get("minutes_lo"), s.get("minutes_hi") or s.get("minutes_lo")
    return None, None


def format_soak_time(base: int, maximum: int, lang: str = "ko") -> str:
    if lang == "vi":
        return (
            f"Hẹn giờ {base} phút. Hết giờ → kiểm tra vết.\n"
            f"· Đã nhạt → xả rồi bước tiếp\n"
            f"· Còn → ngâm thêm {base} phút\n"
            f"· Không quá {maximum} phút — ngâm quá lâu làm hỏng vải"
        )
    if lang == "en":
        return (
            f"Set timer to {base} min. When it rings, check the stain.\n"
            f"· Much lighter → rinse and continue\n"
            f"· Still there → soak another {base} min\n"
            f"· Do not exceed {maximum} min total"
        )
    hrs = f"({maximum // 60}시간)" if maximum >= 60 else ""
    return (
        f"타이머를 {base}분으로 맞춰 주세요.\n"
        f"{base}분이 지나면 꺼내서 얼룩을 확인해 주세요.\n"
        f"· 많이 빠졌다 → 헹구고 다음 단계로 가세요\n"
        f"· 아직 남았다 → {base}분 더 담가 주세요\n"
        f"· 최대 {maximum}분{hrs}을 넘기지 마세요. 너무 오래 담그면 옷감이 상할 수 있어요"
    )


def build_one_line_order(graph: dict, lang: str = "ko") -> str:
    """Numbered do-this-next list from Protocol steps."""
    proto = _proto_dict(graph)
    steps = proto.get("steps") or []
    lines: list[str] = []
    n = 0
    for s in steps:
        if not isinstance(s, dict) or s.get("blocked"):
            continue
        if str(s.get("id") or "") == "id":
            continue
        action = str(s.get("action_ko") or s.get("action_vi") or "").strip()
        if lang == "vi":
            action = str(s.get("action_vi") or s.get("action_ko") or "").strip()
        if not action or len(action) < 4:
            continue
        n += 1
        lo, hi = s.get("minutes_lo"), s.get("minutes_hi")
        time_bit = ""
        if lo is not None:
            if hi and hi != lo and int(hi) >= int(lo) + 30:
                if lang == "ko":
                    time_bit = f" (먼저 {lo}분→확인, 최대 {hi}분)"
                else:
                    time_bit = f" (first {lo}→check, max {hi})"
            elif hi and hi != lo:
                time_bit = f" ({lo}–{hi}분)" if lang == "ko" else f" ({lo}-{hi} min)"
            else:
                time_bit = f" ({lo}분)" if lang == "ko" else f" ({lo} min)"
        if lang == "ko":
            action = _soften_step_label(action)
        lines.append(f"{n}) {action}{time_bit}")
        if n >= 8:
            break
    if not lines:
        sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
        path = str(sc.get("fresh_path_ko") or "")
        numbered = re.findall(r"\((\d+)\)\s*([^\n→]+)", path)
        if numbered:
            for i, (_n, bit) in enumerate(numbered[:8], 1):
                bit = bit.strip().rstrip(".")
                if lang == "ko":
                    bit = _soften_step_label(bit)
                lines.append(f"{i}) {bit}")
        elif "→" in path and lang == "ko":
            bits = [b.strip() for b in path.split("→") if b.strip()]
            lines = [f"{i}) {_soften_step_label(b)}" for i, b in enumerate(bits[:8], 1)]
    if not lines:
        return ""
    if lang == "ko":
        head = "◆ 【한 줄 순서】 아래 번호대로 하나씩 하세요 (한꺼번에 섞지 마세요)"
    elif lang == "vi":
        head = "◆ 【Thứ tự】 Làm lần lượt theo số — không trộn bước"
    else:
        head = "◆ 【One-line order】 Do each number in order — do not mix steps"
    return head + "\n" + "\n".join(lines)


def _soften_step_label(text: str) -> str:
    t = text.strip()
    if "하세요" in t or "마세요" in t or "해 주세요" in t:
        return t
    reps = (
        ("즉시 찬물", "바로 찬물로 헹궈 주세요"),
        ("찬물 헹굼", "찬물로 헹궈 주세요"),
        ("알코올 블롯(테스트)", "알코올은 흰 천에 묻혀 꾹꾹 눌러 흡수하세요(구석 테스트 먼저)"),
        ("알코올 블롯", "알코올은 흰 천에 묻혀 꾹꾹 눌러 흡수하세요"),
        ("흰옷 산소 장침지", "흰옷만 산소표백제로 담가 주세요"),
        ("흰옷 산소", "흰옷만 산소표백제를 쓰세요"),
        ("건조 전 강광", "말리기 전 밝은 조명에서 잔색을 확인해 주세요"),
        ("세탁; 잔색 고지", "세탁해 주세요. 잔색이 남을 수 있다고 고객에게 말씀하세요"),
        ("세탁", "세탁해 주세요"),
    )
    for a, b in reps:
        if t == a:
            return b
        if t.startswith(a):
            return b + t[len(a) :]
    return t


def build_tools_names_only(graph: dict, lang: str = "ko") -> str:
    tools = graph.get("tools") or []
    names: list[str] = []
    for t in tools:
        if not isinstance(t, dict):
            continue
        if lang == "vi":
            name = str(t.get("name_vi") or t.get("name_ko") or "").strip()
        else:
            name = str(t.get("name_ko") or t.get("name_vi") or "").strip()
        if name and name not in names:
            names.append(name)
        if len(names) >= 8:
            break
    # Always suggest basics when we have a stain protocol
    if lang == "ko":
        basics = ["니트릴 장갑", "흰 면 천 여러 장", "타이머(핸드폰 OK)"]
        head = "◆ 【준비물】 이름만 — 사용법은 다음 메시지에 있어요"
        extra_head = "· "
    elif lang == "vi":
        basics = ["Găng nitrile", "Khăn trắng", "Hẹn giờ"]
        head = "◆ 【Chuẩn bị】 Chỉ tên — cách dùng ở tin sau"
        extra_head = "· "
    else:
        basics = ["Nitrile gloves", "White cloths", "Timer"]
        head = "◆ 【Tools】 Names only — how-to in next message"
        extra_head = "· "
    lines = [f"{extra_head}{b}" for b in basics]
    for n in names:
        # skip if already covered by basics keywords
        low = n.lower()
        if any(x in n for x in ("장갑", "găng", "glove", "흰 천", "khan", "cloth", "타이머", "timer", "hẹn")):
            continue
        lines.append(f"{extra_head}{n}")
    return head + "\n" + "\n".join(lines[:10])


def build_spot_test_block(graph: dict, lang: str = "ko") -> str:
    codes = _chem_codes(graph)
    if not (codes & BLOT_CHEM_CODES):
        return ""
    if lang != "ko":
        return (
            "◆ Spot-test first (hidden seam / inside label).\n"
            "Dab chem on white cloth → press 30 sec.\n"
            "· Color on cloth → stop this chem\n"
            "· No color change → OK to continue"
        )
    return (
        "◆ 【구석 테스트】 약품 쓰기 전에 해 주세요\n"
        "안 보이는 곳(안쪽 밑단·라벨 옆)에서요.\n"
        "1) 쓸 약을 흰 천에 조금 묻혀 주세요\n"
        "2) 테스트 부위에 30초 꾹 눌러 주세요\n"
        "3) 천을 떼고 확인하세요\n"
        "· 천에 옷 색이 묻었다 → 이 약은 쓰지 마세요\n"
        "· 색 변화 없다 → 진행하셔도 됩니다\n"
        "💡 30초면 옷 망가지는 사고를 막을 수 있어요"
    )


def build_donts_block(graph: dict, lang: str = "ko") -> str:
    if lang != "ko":
        return (
            "◆ Do not: hot rinse · rub hard · pour chem on fabric · "
            "mix chems · dry/iron over remaining marks"
        )
    sid = _stain_id(graph)
    lines = ["◆ 【절대 하지 마세요】"]
    lines.append("[공통]")
    for d in COMMON_DONTS_KO:
        lines.append(f"· {d}")
    extra = STAIN_DONTS_KO.get(sid) or []
    if extra:
        lines.append("[이 얼룩]")
        for d in extra:
            lines.append(f"· {d}")
    return "\n".join(lines)


def build_dry_check_block(lang: str = "ko") -> str:
    if lang != "ko":
        return (
            "◆ Before drying: check under bright light.\n"
            "· Clean → dry OK\n"
            "· Mark left → no dryer/iron — repeat treatment or air-dry + tell guest"
        )
    return (
        "◆ 【말리기 전】 꼭 확인해 주세요\n"
        "밝은 조명(휴대폰 라이트 OK)에서 얼룩 자리를 한 번 더 보세요.\n"
        "· 깨끗하다 → 정상 건조하시면 됩니다\n"
        "· 자국이 보인다 → 건조기·다림질 하지 마세요. "
        "약 단계를 한 번 더 하거나, 자연 건조 후 고객께 잔색을 말씀해 주세요\n"
        "💡 열을 가하면 자국이 영구로 남을 수 있어요"
    )


def build_status_check(graph: dict, lang: str = "ko") -> str:
    if lang != "ko":
        return ""
    sid = _stain_id(graph)
    if sid in STAIN_STATUS_KO:
        return STAIN_STATUS_KO[sid]
    # Generic age hint from graph if present
    age = ""
    sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
    age = str(sc.get("age_bucket") or graph.get("age_bucket") or "")
    if age == "dried":
        return (
            "◆ 【먼저 확인】 얼룩이 이미 마른 상태예요.\n"
            "성공률이 낮아질 수 있어요. 잔색 가능성을 고객께 먼저 말씀해 주세요."
        )
    if age == "hard":
        return (
            "◆ 【먼저 확인】 열고착·고난이도예요.\n"
            "전문 의뢰 또는 정중한 거절을 먼저 검토해 주세요."
        )
    return (
        "◆ 【먼저 확인】 젖어 있나요, 말랐나요?\n"
        "· 젖어 있다 → 한 줄 순서 1번부터\n"
        "· 말랐다 → 잔색 가능성을 고객께 먼저 말씀하고 진행하세요"
    )


def _apply_tone_softening(text: str) -> str:
    if not text:
        return text
    out = text
    reps = (
        ("보류하며 진행합니다. 확인 후 조정하세요.", "약하게만 하세요. 표백은 매니저 확인 후 하세요."),
        ("약하게(흡수·찍어 바름만)·표백을 보류하며 진행합니다. 확인 후 조정하세요.",
         "원단·두께를 모르면 약하게만 하세요. 표백은 매니저 확인 후 하세요."),
        ("약하게(흡수·찍어 바름만)·표백 보류 → 확인 후 조정하세요.",
         "원단·두께를 모르면 약하게만 하세요. 표백은 매니저 확인 후 하세요."),
        ("블롯", "꾹꾹 눌러 흡수"),
        ("침지", "담그기"),
        ("강광", "밝은 조명"),
        ("도포", "묻히기"),
    )
    for a, b in reps:
        out = out.replace(a, b)
    out = re.sub(
        r"보류하며\s*진행합니다\.?\s*확인\s*후\s*조정하세요\.?",
        "약하게만 하세요. 표백·강한 약은 매니저 확인 후 하세요.",
        out,
    )
    # Wide soak ranges → stepwise reminder inline
    out = re.sub(
        r"30\s*[–\-~]\s*180\s*분",
        "먼저 30분→확인(최대 120분)",
        out,
    )
    out = re.sub(
        r"30\s*[–\-~]\s*120\s*분",
        "먼저 30분→확인(최대 120분)",
        out,
    )
    return out


def _split_glossary_and_body(answer: str) -> tuple[str, str]:
    """Return (front_including_sop_header, body_after_header)."""
    markers = (
        "▼ 이번 건 세탁 교육",
        "▼ SOP cho vết này",
        "▼ This job's wash SOP",
    )
    for m in markers:
        idx = answer.find(m)
        if idx < 0:
            continue
        # include header line + following ━━━ line in front
        nl = answer.find("\n", idx)
        if nl < 0:
            return answer[: idx + len(m)], answer[idx + len(m) :]
        rest = answer[nl + 1 :]
        if rest.startswith("━"):
            nl2 = rest.find("\n")
            end = nl + 1 + (nl2 + 1 if nl2 >= 0 else len(rest))
            return answer[:end], answer[end:]
        return answer[: nl + 1], answer[nl + 1 :]
    return "", answer


def inject_clarity_into_answer(
    answer: str,
    *,
    graph: Optional[dict] = None,
    level: str = "L2",
    grade: int = 2,
    lang: str = "ko",
) -> str:
    """Build 1통 흐름 + 2통 손동작 with short common blocks."""
    if not answer:
        return answer
    g = graph if isinstance(graph, dict) else {}
    lang = lang if lang in _SUPERVISOR else "ko"
    out = _apply_tone_softening(answer)

    front, body = _split_glossary_and_body(out)
    if not front:
        # No SOP divider — soften only, keep single message
        foot = (_GRADE_FOOTER.get(lang) or _GRADE_FOOTER["ko"]).get(grade, "")
        if foot and "【다시 한번 고객 고지】" not in out and "【Nhắc khách】" not in out:
            out = out.rstrip() + "\n\n" + foot
        return out

    # Strip previous clarity inserts from body if re-running
    body = re.sub(
        r"⚠️ 이 얼룩은[^\n]*\n+",
        "",
        body,
        count=1,
    )
    body = re.sub(
        r"◆ 【한 줄 순서】[\s\S]*?(?=\n◆ |\n▼ |\Z)",
        "",
        body,
        count=1,
    )

    flow_bits: list[str] = []
    if level in {"L2", "L3"}:
        flow_bits.append(_SUPERVISOR[lang])
    status = build_status_check(g, lang)
    if status:
        flow_bits.append(status)
    order = build_one_line_order(g, lang)
    if order:
        flow_bits.append(order)
    tools = build_tools_names_only(g, lang)
    if tools:
        flow_bits.append(tools)
    flow_bits.append(_NEXT_MSG[lang])

    detail_bits: list[str] = [_DETAIL_HEAD[lang]]
    spot = build_spot_test_block(g, lang)
    if spot:
        detail_bits.append(spot)
    base, mx = _soak_bounds(g)
    if base is not None and mx is not None and int(mx) >= int(base) + 15:
        detail_bits.append("◆ 【담금 시간】\n" + format_soak_time(int(base), int(mx), lang))
    # LLM / education body (hand motions live here for now)
    body_clean = body.strip()
    if body_clean:
        detail_bits.append(body_clean)
    detail_bits.append(build_donts_block(g, lang))
    detail_bits.append(build_dry_check_block(lang))
    foot = (_GRADE_FOOTER.get(lang) or _GRADE_FOOTER["ko"]).get(grade, "")
    if foot:
        detail_bits.append(foot)

    flow = front.rstrip() + "\n\n" + "\n\n".join(flow_bits)
    detail = "\n\n".join(detail_bits)
    return flow + ZALO_MSG_SPLIT + detail


def split_zalo_messages(text: str, max_len: int = 1900) -> list[str]:
    """Split on ZALO_MSG_SPLIT, then hard-wrap each part under max_len."""
    if not text:
        return []
    raw_parts = text.split("<<<ZALO_MSG2>>>")
    parts = [p.strip() for p in raw_parts if p and p.strip()]
    if not parts:
        parts = [text.strip()]
    out: list[str] = []
    for part in parts:
        out.extend(_chunk_text(part, max_len))
    return out


def _chunk_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts: list[str] = []
    while len(text) > max_len:
        cut = text.rfind("\n", 0, max_len)
        if cut < max_len // 3:
            cut = text.rfind(". ", 0, max_len)
        if cut < max_len // 3:
            cut = max_len
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return parts


def for_ask_display(text: str) -> str:
    """Join multi-part answers for /ask JSON without the raw marker."""
    if not text or "<<<ZALO_MSG2>>>" not in text:
        return text
    parts = split_zalo_messages(text, max_len=100000)
    joined = []
    for i, p in enumerate(parts, 1):
        joined.append(f"—— 메시지 {i}/{len(parts)} ——\n{p}")
    return "\n\n".join(joined)
