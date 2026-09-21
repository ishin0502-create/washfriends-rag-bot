# -*- coding: utf-8 -*-
"""
L2 mid-tier education blocks — safe assembly (no sop_data rewrite, no % rates).

Assembly order (matches inject_clarity):
  Msg1: glossary → L2 supervisor → [L2+] intake short → outlook → status
        → [fabric Q] full fabric guide OR short fabric warn → order → tools
  Msg2: detail head → [compound] principle → spot → soak → Steps
        → donts → [2+ chem | mix Q] chem interaction short/full
        → dry check → [L2+] retry short | [retry Q] retry full → footer

Triggers (never dump full blocks on every answer):
  - intake: level L2/L3 only (short)
  - fabric full: fabric-question keywords
  - fabric short: known delicate fabric or unknown
  - compound: COMPOUND_STAINS only
  - chem full: mix keywords; chem short: chemical_count >= 2
  - retry full: retry keywords; retry short: L2/L3 stain SOP
"""
from __future__ import annotations

from typing import Optional

COMPOUND_STAINS = frozenset({
    "S_BBQ_SAUCE",
    "S_BUBBLE_TEA",
    "S_LIPSTICK",
    "S_MASCARA",
    "S_FOUNDATION",
    "S_MAYO",
    "S_MILK_COFFEE",
    "S_CHOCOLATE",
    "S_KIMCHI",
    "S_GOCHUJANG",
    "S_BBQ_SAUCE",
    "S_CURRY",
    "S_FISH_SAUCE",
})

PROTEIN_NO_HEAT_UP = frozenset({
    "S_BLOOD_FRESH",
    "S_BLOOD_DRY",
    "S_MILK",
    "S_MILK_COFFEE",
    "S_EGG",
    "S_URINE",
    "S_VOMIT",
    "S_BABY_FORMULA",
    "S_SWEAT_FRESH",
    "S_SWEAT_YELLOW",
})

MIX_KEYWORDS_KO = (
    "섞으면", "섞어도", "섞어", "같이 쓰", "같이쓰", "혼합", "동시에",
    "락스 식초", "식초 락스", "표백제 식초", "같이 넣",
)
MIX_KEYWORDS_VI = (
    "trộn", "pha chung", "dùng cùng", "javel giấm", "javel giam",
    "kết hợp", "đổ chung", "pha tron",
)
FABRIC_Q_KO = (
    "원단", "소재", "라벨", "케어라벨", "세탁표시", "무슨 천", "어떤 원단",
)
FABRIC_Q_VI = (
    "chất liệu", "chat lieu", "vải gì", "vai gi", "nhãn", "nhan giat", "care label",
)
RETRY_Q_KO = (
    "안 빠", "안빠", "안지워", "안 지워", "2차", "3차", "다시 시도", "재시도",
    "한 번 더", "한번 더", "더 강하게",
)
RETRY_Q_VI = (
    "chưa sạch", "chua sach", "vẫn còn", "van con", "thử lại", "thu lai",
    "lần 2", "lan 2", "lần 3",
)


def _raw(graph: Optional[dict]) -> str:
    if not isinstance(graph, dict):
        return ""
    return str(graph.get("_raw") or graph.get("_user_caption") or "")


def _norm(s: str) -> str:
    return (s or "").lower()


def wants_mix_block(graph: Optional[dict], lang: str = "ko") -> bool:
    raw = _raw(graph)
    n = _norm(raw)
    if any(k in raw for k in MIX_KEYWORDS_KO) or any(k in n for k in MIX_KEYWORDS_VI):
        return True
    if any(k in n for k in ("mix", "combine", "bleach vinegar", "at the same time")):
        return True
    return False


def wants_fabric_full(graph: Optional[dict], lang: str = "ko") -> bool:
    raw = _raw(graph)
    n = _norm(raw)
    if any(k in raw for k in FABRIC_Q_KO):
        return True
    if any(k in n for k in FABRIC_Q_VI + ("fabric", "what material", "care label")):
        return True
    return False


def wants_retry_full(graph: Optional[dict], lang: str = "ko") -> bool:
    raw = _raw(graph)
    n = _norm(raw)
    if any(k in raw for k in RETRY_Q_KO):
        return True
    if any(k in n for k in RETRY_Q_VI + ("still not", "retry", "second try", "third try")):
        return True
    return False


def chemical_count(graph: Optional[dict]) -> int:
    if not isinstance(graph, dict):
        return 0
    codes: set[str] = set()
    for c in graph.get("chemicals") or []:
        if isinstance(c, dict):
            code = str(c.get("code") or c.get("id") or "").strip()
            if code:
                codes.add(code)
        elif isinstance(c, str) and c.strip():
            codes.add(c.strip())
    return len(codes)


def _fabric_type(graph: Optional[dict]) -> str:
    if not isinstance(graph, dict):
        return ""
    ents = graph.get("entities") if isinstance(graph.get("entities"), dict) else {}
    md = graph.get("match_diagnosis") if isinstance(graph.get("match_diagnosis"), dict) else {}
    ft = str(
        ents.get("fabric_type")
        or md.get("fabric_type")
        or graph.get("fabric_type")
        or ""
    ).strip().lower()
    return ft


# ── Short blocks (default insert) ──────────────────────────────────────────

INTAKE_SHORT = {
    "ko": (
        "◆ 【접수 체크 · L2】 시작 전\n"
        "① 고객 동의 후 사진 3장(얼룩 근접·라벨·전체)\n"
        "② 등급 고지(완전 제거 보장 금지) ③ 소요(일반 당일~1일 / 어려움 2~3일)\n"
        "④ 「잔색 가능·잔색은 배상 대상 아님. 진행할까요?」 동의 확인"
    ),
    "vi": (
        "◆ 【Checklist tiếp nhận · L2】 Trước khi làm\n"
        "① Ảnh (đồng ý): cận vết · nhãn · tổng thể\n"
        "② Báo cấp độ (không cam kết sạch 100%) ③ Thời gian (thường 1 ngày / khó 2–3 ngày)\n"
        "④ Xác nhận: có thể còn vết, không bồi thường phần còn"
    ),
    "en": (
        "◆ 【Intake check · L2】 Before starting\n"
        "① Photos with consent (stain / label / full) ② Grade disclosure "
        "③ Turnaround ④ Consent: residual marks not compensable"
    ),
}

FABRIC_SHORT = {
    "silk": {
        "ko": "◆ 【원단】 실크 → 중성·찬물만. 알코올·산소·염소 금지. 강처리 전 전문·거절 검토.",
        "vi": "◆ 【Vải】 Lụa → chỉ trung tính + lạnh. Cấm cồn/oxy/clo. Ưu tiên chuyên/từ chối.",
        "en": "◆ 【Fabric】 Silk → neutral + cold only. No alcohol/oxygen/chlorine.",
    },
    "wool": {
        "ko": "◆ 【원단】 울·캐시미어 → 중성·찬물만. 산소·베이킹소다(알칼리) 금지 · 축소 주의.",
        "vi": "◆ 【Vải】 Len/cashmere → chỉ trung tính + lạnh. Cấm oxy/kiềm — dễ co.",
        "en": "◆ 【Fabric】 Wool/cashmere → neutral + cold. No oxygen/alkali — shrink risk.",
    },
    "leather": {
        "ko": "◆ 【원단】 가죽 → 물세탁·일반 SOP 금지. 가죽 전용·전문 의뢰.",
        "vi": "◆ 【Vải】 Da → cấm giặt nước / SOP thường. Chuyên da.",
        "en": "◆ 【Fabric】 Leather → no wet wash / normal SOP. Specialist only.",
    },
    "acetate": {
        "ko": "◆ 【원단】 아세테이트 → 아세톤 절대 금지(녹음). 전문 우선.",
        "vi": "◆ 【Vải】 Acetate → tuyệt đối cấm acetone. Ưu tiên chuyên.",
        "en": "◆ 【Fabric】 Acetate → no acetone (dissolves). Specialist first.",
    },
    "unknown": {
        "ko": "◆ 【원단】 라벨·원단 불명 → 중성+찬물만. 표백·강한 용제는 보류 · 고객 고지.",
        "vi": "◆ 【Vải】 Không rõ → chỉ trung tính + lạnh. Tẩy/dung môi mạnh: tạm dừng.",
        "en": "◆ 【Fabric】 Unknown → neutral + cold only. Hold bleach/strong solvents.",
    },
}

CHEM_INTERACTION_SHORT = {
    "ko": (
        "◆ 【약품 여러 개】 한 번에 하나만 · 바꿀 때 찬물 헹굼\n"
        "· OK(헹굼 후): 알코올→산소 · 세제→효소 · 효소→산소 · 식초→중성\n"
        "· 금지: 락스+식초/암모니아/산소 · 과산화수소+식초 → 유독·화상 위험"
    ),
    "vi": (
        "◆ 【Nhiều hóa chất】 Mỗi lần một loại · đổi thì xả lạnh\n"
        "· OK (sau xả): cồn→oxy · xà phòng→enzyme · enzyme→oxy · giấm→trung tính\n"
        "· CẤM: javel+giấm/amoniac/oxy · H2O2+giấm"
    ),
    "en": (
        "◆ 【Multiple chemicals】 One at a time · rinse cold when switching\n"
        "· OK after rinse: alcohol→oxygen · soap→enzyme · enzyme→oxygen · vinegar→neutral\n"
        "· NEVER: chlorine+vinegar/ammonia/oxygen · H2O2+vinegar"
    ),
}

CHEM_INTERACTION_FULL = {
    "ko": (
        "◆ 【약품 상호작용】\n"
        "바꿀 때는 반드시 중간에 찬물 헹굼. 남은 약 위에 다음 약 금지.\n"
        "✅ 순서 OK(헹굼 필수): 알코올→산소 · 주방세제→효소 · 세제→산소 · 효소→산소 · 식초→중성\n"
        "🛑 절대 금지(위험):\n"
        "· 락스(염소)+식초 → 염소 가스 · 폐 손상 위험\n"
        "· 락스+암모니아 → 독성 가스\n"
        "· 락스+산소표백 → 효과 상쇄+위험 반응\n"
        "· 과산화수소+식초 → 과초산 · 피부 화상\n"
        "⚠️ 효과↓: 효소+50°C↑(효소 실활) · 산소+15°C↓(활성화 약함)\n"
        "💡 한 번에 한 가지만. 바꾸면 헹굼."
    ),
    "vi": (
        "◆ 【Tương tác hóa chất】\n"
        "Đổi chất → xả lạnh giữa bước. Không chồng chất cũ.\n"
        "✅ OK (xả giữa): cồn→oxy · rửa chén→enzyme · xà phòng→oxy · enzyme→oxy · giấm→trung tính\n"
        "🛑 CẤM: javel+giấm (khí clo) · javel+amoniac · javel+oxy · H2O2+giấm\n"
        "⚠️ Enzyme + >50°C chết enzyme · Oxy + <15°C kém hiệu quả\n"
        "💡 Mỗi lần một loại. Đổi thì xả."
    ),
    "en": (
        "◆ 【Chemical interaction】\n"
        "Rinse cold between chemicals. Never stack wet chemicals.\n"
        "✅ OK with rinse: alcohol→oxygen · dish soap→enzyme · enzyme→oxygen · vinegar→neutral\n"
        "🛑 NEVER: chlorine+vinegar/ammonia/oxygen · H2O2+vinegar\n"
        "⚠️ Enzyme dies >50°C · oxygen weak <15°C\n"
        "💡 One at a time. Rinse when you switch."
    ),
}

COMPOUND_PRINCIPLE = {
    "ko": (
        "◆ 【복합 얼룩】 성분을 나눠 순서대로\n"
        "① 기름·왁스 → 주방세제 또는 알코올\n"
        "② 단백질 → 효소(찬물~미온) ③ 색소·탄닌 → 식초 또는 산소(흰옷)\n"
        "기름 남은 채 표백·단백질에 온수 → 고착돼요. 단계마다 헹굼."
    ),
    "vi": (
        "◆ 【Vết phức hợp】 Tách thành phần · đúng thứ tự\n"
        "① Dầu/sáp → rửa chén hoặc cồn\n"
        "② Protein → enzyme ③ Màu/tannin → giấm hoặc oxy (áo trắng)\n"
        "Còn dầu mà tẩy / protein + nóng → cố định. Xả giữa bước."
    ),
    "en": (
        "◆ 【Compound stain】 Split components · keep order\n"
        "① Grease/wax → dish soap or alcohol\n"
        "② Protein → enzyme ③ Color/tannin → vinegar or oxygen (whites)\n"
        "Bleach on grease / hot on protein sets the stain. Rinse between."
    ),
}

FABRIC_GUIDE_FULL = {
    "ko": (
        "◆ 【원단 판단】\n"
        "면·린넨: 대부분 약 OK · 폴리: 고온 주의 · 실크/울: 중성+찬물만(산소·염소·알코올 신중/금지)\n"
        "가죽: 물세탁 금지 · 아세테이트: 아세톤 금지\n"
        "라벨 없으면: 안 보이는 곳 물방울(흡수=천연 / 맺힘=합성) · 모르면 중성+찬물만 · 고객 고지"
    ),
    "vi": (
        "◆ 【Nhận diện vải】\n"
        "Cotton/lanh: hầu hết OK · Poly: tránh nhiệt cao · Lụa/len: chỉ trung tính+lạnh\n"
        "Da: cấm giặt nước · Acetate: cấm acetone\n"
        "Không nhãn: test giọt nước · không rõ → chỉ nhẹ + báo khách"
    ),
    "en": (
        "◆ 【Fabric guide】\n"
        "Cotton/linen: most chems OK · Poly: watch heat · Silk/wool: neutral+cold only\n"
        "Leather: no wet wash · Acetate: no acetone\n"
        "No label: water-drop test · unknown → gentlest + disclose"
    ),
}

RETRY_SHORT = {
    "ko": (
        "◆ 【안 빠졌을 때 · L2】 매니저와 함께\n"
        "2차: 농도·담금 시간만 소폭↑(최대 약 2배/2시간) · 구석 테스트 다시\n"
        "단백질(피·우유 등)은 수온 올리지 마세요\n"
        "3차·용제 전환(아세톤 등)은 매니저 확인 · 실크·아세테이트 아세톤 금지\n"
        "3차 후에도 남으면 전문 의뢰·솔직 고지"
    ),
    "vi": (
        "◆ 【Chưa sạch · L2】 Làm với quản lý\n"
        "Lần 2: tăng nhẹ nồng độ/thời gian (≤~2× / 2 giờ) · thử góc lại\n"
        "Protein (máu/sữa…): không tăng nhiệt\n"
        "Lần 3 / dung môi (acetone…): hỏi quản lý · cấm acetone lên lụa/acetate\n"
        "Vẫn còn → chuyên / nói thật với khách"
    ),
    "en": (
        "◆ 【If still stained · L2】 With supervisor\n"
        "2nd: slight↑ dose/soak (max ~2× / 2h) · re-spot-test\n"
        "Protein stains: do not raise temperature\n"
        "3rd/solvent switch: supervisor only · no acetone on silk/acetate\n"
        "Still left → specialist / honest disclosure"
    ),
}


def retry_full(sid: str, lang: str = "ko") -> str:
    protein = sid in PROTEIN_NO_HEAT_UP
    if lang == "vi":
        heat = (
            "· Protein (máu/sữa…): KHÔNG tăng nhiệt"
            if protein
            else "· Có thể thử ấm nhẹ 30–35°C (không phải protein)"
        )
        return (
            "◆ 【Thử lại · L2】 Cùng quản lý\n"
            "⚠️ Nội dung trung cấp — hỏi quản lý trước.\n"
            "📌 Lần 2 — mạnh hơn một chút\n"
            "· Nồng độ: 1 muỗng → tối đa 2 (≤2×)\n"
            "· Ngâm: 30 → 60 phút (tối đa 2 giờ)\n"
            f"{heat}\n"
            "· Thử góc lại mỗi lần\n"
            "📌 Lần 3 — đổi hướng (quản lý)\n"
            "· Oxy kém → xem H2O2 3% (cotton trắng, thử góc)\n"
            "· Cồn kém → acetone chỉ cotton/poly · cấm lụa/acetate\n"
            "· Amoniac loãng: thông gió + quản lý — không tự ý\n"
            "🛑 Hết 3 lần → chuyên hoặc báo khách thật"
        )
    if lang == "en":
        heat = (
            "· Protein (blood/milk…): do NOT raise temperature"
            if protein
            else "· May try lukewarm 30–35°C (if not protein)"
        )
        return (
            "◆ 【Retry · L2】 With supervisor\n"
            "⚠️ Intermediate — confirm with manager.\n"
            "📌 2nd try\n"
            "· Dose up to ~2× · soak up to 2h · re-spot-test\n"
            f"{heat}\n"
            "📌 3rd try (manager)\n"
            "· Oxygen failed → H2O2 3% on white cotton only\n"
            "· Alcohol failed → acetone cotton/poly only · never silk/acetate\n"
            "· Dilute ammonia: ventilate + manager only\n"
            "🛑 After 3rd → specialist or honest disclose"
        )
    heat = (
        "· 단백질(피·우유 등): 수온 올리지 마세요"
        if protein
        else "· 미지근(30~35°C) 검토 가능(단백질 얼룩 제외)"
    )
    return (
        "◆ 【안 빠졌나요 · L2 재시도】 매니저와 함께\n"
        "⚠️ 중급 내용입니다. 매니저 확인 후 진행하세요.\n"
        "📌 2차 시도 — 조금 더\n"
        "· 농도: 큰술 1 → 최대 큰술 2(약 2배)\n"
        "· 담금: 30분 → 60분(최대 2시간)\n"
        f"{heat}\n"
        "· 매 단계 구석 테스트 다시\n"
        "📌 3차 시도 — 방향 전환(매니저)\n"
        "· 산소 실패 → 과산화수소 3%(흰 면만·테스트)\n"
        "· 알코올 실패 → 아세톤은 면·폴리만 · 실크·아세테이트 금지\n"
        "· 약한 암모니아: 환기+매니저 — 혼자 결정 금지\n"
        "🛑 3차 후에도 남으면 → 전문 의뢰 또는 솔직 고지"
    )


def block_intake(level: str, lang: str) -> str:
    if level not in {"L2", "L3"}:
        return ""
    return INTAKE_SHORT.get(lang) or INTAKE_SHORT["ko"]


def block_fabric(graph: Optional[dict], lang: str) -> str:
    if wants_fabric_full(graph, lang):
        return FABRIC_GUIDE_FULL.get(lang) or FABRIC_GUIDE_FULL["ko"]
    ft = _fabric_type(graph)
    key = ""
    if "silk" in ft or "lua" in ft:
        key = "silk"
    elif "wool" in ft or "cashmere" in ft:
        key = "wool"
    elif "leather" in ft or "da" == ft:
        key = "leather"
    elif "acetate" in ft:
        key = "acetate"
    raw = _raw(graph)
    if not key and any(k in raw for k in ("실크", "비단", "울", "가죽", "아세테이트")):
        if "실크" in raw or "비단" in raw:
            key = "silk"
        elif "울" in raw or "캐시미어" in raw:
            key = "wool"
        elif "가죽" in raw:
            key = "leather"
        elif "아세테이트" in raw:
            key = "acetate"
    if key:
        row = FABRIC_SHORT.get(key) or {}
        return row.get(lang) or row.get("ko") or ""
    # unknown fabric tip only when user asked about fabric vaguely
    if wants_fabric_full(graph, lang):
        row = FABRIC_SHORT["unknown"]
        return row.get(lang) or row["ko"]
    return ""


def block_compound(sid: str, lang: str) -> str:
    if sid not in COMPOUND_STAINS:
        return ""
    return COMPOUND_PRINCIPLE.get(lang) or COMPOUND_PRINCIPLE["ko"]


def block_chem(graph: Optional[dict], lang: str) -> str:
    if wants_mix_block(graph, lang):
        return CHEM_INTERACTION_FULL.get(lang) or CHEM_INTERACTION_FULL["ko"]
    if chemical_count(graph) >= 2:
        return CHEM_INTERACTION_SHORT.get(lang) or CHEM_INTERACTION_SHORT["ko"]
    return ""


def block_retry(sid: str, level: str, graph: Optional[dict], lang: str) -> str:
    if level not in {"L2", "L3"}:
        return ""
    if wants_retry_full(graph, lang):
        return retry_full(sid, lang)
    return RETRY_SHORT.get(lang) or RETRY_SHORT["ko"]
