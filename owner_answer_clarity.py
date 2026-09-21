# -*- coding: utf-8 -*-
"""Make owner Zalo answers easier to follow (one-line order + clear tools).

Does not change chemistry order — only how we present steps to juniors.
"""
from __future__ import annotations

import re
from typing import Any, Optional

# Chems that are blot/dab on cloth — never "mix into spray bottle"
BLOT_CHEM_CODES = frozenset({"A1", "A2", "D1"})

_SUPERVISOR = {
    "ko": "⚠️ 이 얼룩은 감독이 필요합니다. 매니저(또는 경력 직원)와 확인한 뒤에 시작하세요.",
    "vi": "⚠️ Vết này cần giám sát. Hãy hỏi quản lý trước khi bắt đầu.",
    "en": "⚠️ Supervisor needed. Check with a manager before you start.",
}

_GRADE_FOOTER = {
    "ko": {
        1: "【다시 한번 고객 고지】 완전 제거는 보장드리기 어렵습니다. 잔색이 남을 수 있습니다.",
        2: "【다시 한번 고객 고지】 완전 제거는 어렵고 잔색·잔영이 남을 수 있습니다. 그래도 진행하시겠어요?",
        3: "【다시 한번 고객 고지】 매장에서 안전하게 처리하기 어렵습니다. 전문 의뢰 또는 접수 반려를 안내하세요.",
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


def _proto_dict(graph: dict) -> dict:
    p = graph.get("protocol") if isinstance(graph, dict) else None
    return p if isinstance(p, dict) else {}


def build_one_line_order(graph: dict, lang: str = "ko") -> str:
    """Numbered do-this-next list from Protocol steps (skip id-only labels)."""
    proto = _proto_dict(graph)
    steps = proto.get("steps") or []
    lines: list[str] = []
    n = 0
    for s in steps:
        if not isinstance(s, dict) or s.get("blocked"):
            continue
        sid = str(s.get("id") or "")
        if sid in {"id", "identify", "light"}:
            # keep light as last; skip pure identify
            if sid == "id":
                continue
        action = str(s.get("action_ko") or s.get("action_vi") or "").strip()
        if lang == "vi":
            action = str(s.get("action_vi") or s.get("action_ko") or "").strip()
        elif lang == "en":
            action = str(s.get("action_ko") or "").strip()
        if not action:
            continue
        # Skip ultra-short identity crumbs
        if len(action) < 4:
            continue
        n += 1
        lo, hi = s.get("minutes_lo"), s.get("minutes_hi")
        time_bit = ""
        if lo is not None:
            if hi and hi != lo:
                time_bit = f" ({lo}–{hi}분)" if lang == "ko" else f" ({lo}-{hi} min)"
            else:
                time_bit = f" ({lo}분)" if lang == "ko" else f" ({lo} min)"
        # Friendlier KO verbs when still telegram-like
        if lang == "ko":
            action = _soften_step_label(action)
        lines.append(f"{n}) {action}{time_bit}")
        if n >= 8:
            break
    if not lines:
        # Fallback: compress fresh_path arrows
        sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
        path = str(sc.get("fresh_path_ko") or graph.get("fresh_path_ko") or "")
        if "→" in path and lang == "ko":
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
    t = text
    reps = (
        ("즉시 찬물", "바로 찬물로 헹구세요"),
        ("찬물 헹굼", "찬물로 헹구세요"),
        ("알코올 블롯(테스트)", "알코올은 흰 천에 묻혀 찍어 흡수하세요(구석 테스트 먼저)"),
        ("알코올 블롯", "알코올은 흰 천에 묻혀 찍어 흡수하세요"),
        ("흰옷 산소 장침지", "흰옷만 산소표백제로 담그세요"),
        ("흰옷 산소", "흰옷만 산소표백제를 쓰세요"),
        ("건조 전 강광", "말리기 전 밝은 조명에서 잔색을 확인하세요"),
        ("세탁; 잔색 고지", "세탁하세요. 잔색이 남을 수 있다고 고객에게 고지하세요"),
        ("세탁", "세탁하세요"),
    )
    for a, b in reps:
        if t == a or t.startswith(a):
            return b + t[len(a) :] if t.startswith(a) and t != a else b
    return t


def inject_clarity_into_answer(
    answer: str,
    *,
    graph: Optional[dict] = None,
    level: str = "L2",
    grade: int = 2,
    lang: str = "ko",
) -> str:
    """Insert one-line order + L2 note after SOP divider; grade reminder at end."""
    if not answer:
        return answer
    g = graph if isinstance(graph, dict) else {}
    lang = lang if lang in _SUPERVISOR else "ko"
    out = answer

    # Soften confusing "보류하며 진행" style lines
    out = out.replace(
        "약하게(흡수·찍어 바름만)·표백을 보류하며 진행합니다. 확인 후 조정하세요.",
        "원단·두께를 아직 모르면: 세게 문지르지 말고 약하게만 하세요. "
        "산소·표백은 매니저와 확인한 뒤에만 쓰세요.",
    )
    out = out.replace(
        "약하게(흡수·찍어 바름만)·표백 보류 → 확인 후 조정하세요.",
        "원단·두께를 모르면 약하게만 하세요. 표백은 매니저 확인 후 하세요.",
    )
    out = out.replace(
        "약하게(흡수·찍어 바름만)·표백 보류로 진행하세요",
        "약하게만 하세요. 표백은 매니저 확인 후 하세요",
    )
    out = re.sub(
        r"보류하며\s*진행합니다\.?\s*확인\s*후\s*조정하세요\.?",
        "약하게만 하세요. 표백·강한 약은 매니저 확인 후 하세요.",
        out,
    )

    order = build_one_line_order(g, lang)
    # Insert after SOP divider, or at top of body if no divider
    marker_ko = "▼ 이번 건 세탁 교육"
    marker_vi = "▼ SOP cho vết này"
    marker_en = "▼ This job's wash SOP"
    insert_at = -1
    for m in (marker_ko, marker_vi, marker_en):
        idx = out.find(m)
        if idx >= 0:
            # after the underline following the marker
            nl = out.find("\n", idx)
            if nl > 0:
                # skip next line of ━━━ if present
                rest = out[nl + 1 :]
                if rest.startswith("━"):
                    nl2 = rest.find("\n")
                    insert_at = nl + 1 + (nl2 + 1 if nl2 >= 0 else 0)
                else:
                    insert_at = nl + 1
            break

    block_parts = []
    if level in {"L2", "L3"}:
        block_parts.append(_SUPERVISOR[lang])
    if order:
        block_parts.append(order)
    block = "\n\n".join(block_parts)

    if block:
        if "【한 줄 순서】" in out or "【Thứ tự】" in out or "【One-line order】" in out:
            pass  # already injected
        elif insert_at > 0:
            out = out[:insert_at] + "\n" + block + "\n\n" + out[insert_at:].lstrip("\n")
        else:
            out = block + "\n\n" + out

    # Grade reminder at end (once)
    foot = (_GRADE_FOOTER.get(lang) or _GRADE_FOOTER["ko"]).get(grade, "")
    if foot and foot.split("】")[0] not in out[-200:]:
        if "【다시 한번 고객 고지】" not in out and "【Nhắc khách】" not in out and "【Tell the guest again】" not in out:
            out = out.rstrip() + "\n\n" + foot

    return out
