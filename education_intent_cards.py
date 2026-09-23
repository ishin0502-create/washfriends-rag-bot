# -*- coding: utf-8 -*-
"""Standalone education cards for meta questions (no stain SOP required).

Used as an early gate in generate_response so Q1/Q2/Q6/Q8/Q9/Q10
do not fall through to empty-graph clarification or wrong SOPs.
"""
from __future__ import annotations

import re
from typing import Optional

# --- detectors (failure / pre-dry context; avoid bare "2차") ---
_RETRY = re.compile(
    r"(안\s*빠|안빠|빠지지\s*않|1차\s*(실패|안)|다시\s*(안|시도)|재시도|"
    r"두\s*번\s*째|2차\s*(시도|처리|실패)|"
    r"vẫn\s*còn|chưa\s*ra|lần\s*2|thử\s*lại|still\s*(not|there)|retry)",
    re.I,
)
_BEFORE_DRY = re.compile(
    r"(건조기|말려도|말려\s*도|말리도|다림질\s*(해도|해도\s*돼)|다려도|"
    r"말려도\s*돼|건조\s*해도|sấy|ủi\s*được|dryer|iron\s*(ok|okay|now))",
    re.I,
)
# Luxury bag / leather handbag — L3 gate + ask material
_BAG = re.compile(
    r"(명품\s*(핸드)?백|핸드백|손가방|가죽\s*가방|가방\s*(얼룩|케어|세탁)|"
    r"túi\s*xách|túi\s*da|handbag|leather\s*bag|designer\s*bag)",
    re.I,
)
_BEGINNER = re.compile(
    r"(초보|신입|처음|어디서\s*시작|어떻게\s*시작|입문|"
    r"mới\s*vào|bắt\s*đầu\s*từ|beginner|where\s*(do\s*I\s*)?start)",
    re.I,
)
# Oxygen bleach term — must beat chlorine SOP routing
_OXYGEN_TERM = re.compile(
    r"(산소\s*표백|산소계|과탄산|옥시클린|oxy\s*bleach|oxygen\s*bleach|"
    r"bột\s*tẩy\s*oxy|tay\s*oxy|"
    r"산소표백제\s*(가|이|은|는)?\s*(뭐|무엇))",
    re.I,
)
_NITRILE = re.compile(
    r"(니트릴\s*장갑|nitril|nitrile\s*glove|găng\s*nitrile|"
    r"니트릴\s*장갑\s*(은|는|이|가)?\s*(왜|뭐))",
    re.I,
)

CARD_RETRY_KO = (
    "◆ 【안 빠졌을 때 · 재시도】 매니저와 함께\n"
    "⚠️ 얼룩 종류를 알면 그 SOP의 재시도 규칙을 따릅니다. 공통만 적습니다.\n"
    "\n"
    "📌 2차 시도\n"
    "· 농도: 큰술 1 → 최대 큰술 2(약 2배)\n"
    "· 담금: 30분 → 60분(최대 2시간)\n"
    "· 매 단계 구석 테스트 다시\n"
    "· 단백질(피·우유·계란): 수온 올리지 마세요\n"
    "\n"
    "📌 3차 · 방향 전환(매니저)\n"
    "· 산소 실패 → 과산화수소 3%(흰 면만·테스트)\n"
    "· 알코올 실패 → 아세톤은 면·폴리만 · 실크·아세테이트 금지\n"
    "· 3차 후에도 남으면 → 전문 의뢰 또는 솔직 고지\n"
    "\n"
    "💡 어떤 얼룩인지(커피·피·기름 등)와 원단을 알려주시면 그 SOP에 맞춰 다시 안내합니다."
)

CARD_BEFORE_DRY_KO = (
    "◆ 【말리기 전】 건조기·다림질 전에 꼭\n"
    "밝은 조명(휴대폰 라이트 OK)에서 얼룩 자리를 한 번 더 보세요.\n"
    "· 깨끗하다 → 정상 건조·다림질 가능\n"
    "· 자국이 보인다 → 건조기·다림질 하지 마세요\n"
    "  → 약 단계를 한 번 더 하거나, 자연 건조 후 고객께 잔색을 말씀하세요\n"
    "\n"
    "💡 「거의 다 빠졌는데」라도 자국이 보이면 말리지 마세요.\n"
    "열이 가해지면 자국이 영구로 남을 수 있어요.\n"
    "\n"
    "어느 얼룩·원단인지 알려주시면 그 건에 맞춰 다시 확인 포인트를 적어 드립니다."
)

CARD_BAG_L3_KO = (
    "◆ 【명품·핸드백 · L3】 거절·전문 우선\n"
    "【접수 고지 · 등급 3】 가방·핸드백(특히 가죽·스웨이드·코팅)은\n"
    "매장 일반 세탁·강한 용제로 안전하게 처리하기 어렵습니다.\n"
    "시도하면 원단·색·형태 손상 위험이 큽니다.\n"
    "① 가죽·가방 전문 의뢰 안내 또는 ② 접수 반려 — 둘 중 하나를 안내하세요.\n"
    "초보는 배상 확약 금지.\n"
    "\n"
    "◆ 【먼저 확인】\n"
    "· 진가죽 / 스웨이드·누벅 / 인조(레자·PU) / 천·나일론 중 무엇인가요?\n"
    "· 어떤 얼룩인가요? (기름, 잉크, 곰팡이, 물때…)\n"
    "\n"
    "◆ 【매장에서 하지 말 것】\n"
    "· 물세탁기·건조기·산소·락스·아세톤 임의 사용\n"
    "· 「명품이라 책임지고 빼 드린다」 확약\n"
    "\n"
    "소재·얼룩을 알려주시면 거절 멘트 또는 최소 응급(흡수만)만 짧게 안내합니다."
)

CARD_OXYGEN_KO = (
    "◆ 【용어】 산소표백제란?\n"
    "· 성분: 과탄산나트륨 계열(슈퍼의 「산소계·옥시클린」 분말)\n"
    "· 하는 일: 흰 면·린넨의 잔색을 밝게(표백)·탈취\n"
    "· 락스(염소·자벨)와 다름 — 섞지 마세요. 용도·위험이 다릅니다\n"
    "\n"
    "◆ 【언제 쓰나】\n"
    "· 흰옷 확인 후, 구석 테스트 통과 시\n"
    "· 보통: 찬물~미온 1L에 큰술 1–2 → 15–45분(병 라벨 우선)\n"
    "\n"
    "◆ 【쓰지 말 때】\n"
    "· 유색·검정·색 미확인\n"
    "· 실크·울·가죽·모피·아세테이트\n"
    "· 단백질 얼룩에 온수+표백을 한꺼번에(고착·손상)\n"
    "\n"
    "◆ 【초보】 산소표백은 L1(초보 단독)이 아닙니다. 매니저 확인 후."
)

CARD_NITRILE_KO = (
    "◆ 【도구】 니트릴 장갑 — 왜 쓰나?\n"
    "· 하는 일: 약품·얼룩(피·구토·소변 등)로부터 손을 보호\n"
    "· 라텍스와 다름 — 니트릴은 용제·세제에 더 잘 견딤(매장 기본 PPE)\n"
    "\n"
    "◆ 【언제 필수】\n"
    "· 락스·산소·알코올·아세톤·암모니아 등 약품 다룰 때\n"
    "· 피·소변·구토·분변 등 바이오 얼룩\n"
    "· 곰팡이 포자 털 때(마스크와 함께)\n"
    "\n"
    "◆ 【초보】 L1이어도 장갑은 기본입니다.\n"
    "※ 「니트」(옷감)와 「니트릴」(장갑 소재)은 다른 말입니다."
)

CARD_BEGINNER_KO = (
    "◆ 【초보 시작】 어디서부터?\n"
    "\n"
    "📌 혼자 해도 되는 것 (L1)\n"
    "· 찬물로 흡수·헹구기, 중성·주방세제, 식초 1:4(탄닌)\n"
    "· 예: 신선 피(찬물·효소), 블랙커피·차(순차), 케첩, 진흙(마른 뒤)\n"
    "· 항상: 원단·색 확인 → 「잔색 가능」 짧게 고지 → 동의\n"
    "\n"
    "📌 매니저 확인 후 (L2)\n"
    "· 알코올·아세톤·산소표백·강한 담금\n"
    "· 잉크·마스카라·와인·마른 피·황변 등\n"
    "\n"
    "📌 거절·전문 우선 (L3)\n"
    "· 엔진/체인 기름·타르·유성페인트·가죽·오래된 곰팡이(섬세품)\n"
    "\n"
    "다음으로 「면티에 커피」처럼 얼룩+원단을 적어 주시면\n"
    "그 건의 한 줄 순서부터 안내합니다."
)

CARD_RETRY_VI = (
    "◆ 【Vẫn còn vết · thử lại】 Cùng quản lý\n"
    "Lần 2: tăng nhẹ nồng độ/thời gian ( tối đa ~2× / 2 giờ) · test góc lại.\n"
    "Protein: không tăng nhiệt.\n"
    "Lần 3 / đổi hướng: hỏi quản lý. Còn → chuyên hoặc báo thật.\n"
    "Cho biết loại vết + vải để SOP cụ thể."
)

CARD_BEFORE_DRY_VI = (
    "◆ 【Trước khi sấy/ủi】\n"
    "Soi đèn mạnh chỗ vết.\n"
    "· Sạch → sấy/ủi được\n"
    "· Còn vết → CẤM sấy/ủi — xử lý lại hoặc phơi tự nhiên + báo khách.\n"
    "「Gần sạch」 mà còn vết → đừng sấy."
)

CARD_BAG_L3_VI = (
    "◆ 【Túi xách / hàng hiệu · L3】 Ưu tiên từ chối / chuyên\n"
    "Da/suede/túi đắt: không giặt máy / oxy / Javel / acetone bừa.\n"
    "① Gửi chuyên da ② Từ chối nhận.\n"
    "Hỏi: da thật / da lộn / PU / vải? Vết gì?"
)

CARD_OXYGEN_VI = (
    "◆ 【Thuật ngữ】 Bột tẩy oxy là gì?\n"
    "· Percarbonate (oxy) — khác Javel (clo). Không trộn.\n"
    "· Chỉ đồ trắng + test góc. CẤM màu / lụa / len.\n"
    "· Không phải việc L1 tự quyết — hỏi quản lý."
)

CARD_NITRILE_VI = (
    "◆ 【Dụng cụ】 Găng nitrile — để làm gì?\n"
    "· Bảo vệ tay khỏi hóa chất + vết sinh học.\n"
    "· Bắt buộc khi dùng Javel/oxy/cồn/acetone hoặc máu/nôn.\n"
    "· Khác với 「áo len/nit」 (vải)."
)

CARD_BEGINNER_VI = (
    "◆ 【Người mới】 Bắt đầu từ đâu?\n"
    "L1: lạnh / trung tính / giấm 1:4 — hỏi vải·màu trước.\n"
    "L2: cồn/oxy → hỏi quản lý.\n"
    "L3: dầu máy / da / mốc nặng → từ chối/chuyên.\n"
    "Gửi: loại vết + vải (vd cà phê trên cotton)."
)


def try_intent_education_card(user_message: str, lang: str = "ko") -> str:
    """Return a standalone card if message is a meta education question."""
    msg = (user_message or "").strip()
    if not msg or len(msg) > 220:
        return ""
    lang = lang if lang in {"ko", "vi", "en"} else "ko"

    # Order: specific tools/terms before bag/retry (oxygen before generic bleach SOP)
    if _OXYGEN_TERM.search(msg) and not re.search(r"락스|자벨|javel|clo\b", msg, re.I):
        if lang == "vi":
            return CARD_OXYGEN_VI
        return CARD_OXYGEN_KO

    if _NITRILE.search(msg):
        if lang == "vi":
            return CARD_NITRILE_VI
        return CARD_NITRILE_KO

    if _BAG.search(msg) and not re.search(
        r"(면\s*티|티셔츠|바지\s*얼룩|와이셔츠|청바지)", msg
    ):
        if lang == "vi":
            return CARD_BAG_L3_VI
        return CARD_BAG_L3_KO

    if _RETRY.search(msg) and not re.search(
        r"(피|커피|와인|기름|잉크|곰팡|김치)\s*.{0,8}(안\s*빠|재시도)", msg
    ):
        # bare retry without stain → standalone; if stain named, let SOP handle
        if not re.search(
            r"(피|혈액|커피|와인|기름|잉크|곰팡|김치|케첩|초콜릿|계란)", msg
        ):
            if lang == "vi":
                return CARD_RETRY_VI
            return CARD_RETRY_KO

    if _BEFORE_DRY.search(msg) and not re.search(
        r"(피|커피|와인|기름|잉크|곰팡|김치).{0,12}(건조|말리|다림질|sấy)", msg
    ):
        if not re.search(
            r"(피|혈액|커피|와인|기름|잉크|곰팡|김치|케첩)", msg
        ):
            if lang == "vi":
                return CARD_BEFORE_DRY_VI
            return CARD_BEFORE_DRY_KO

    if _BEGINNER.search(msg) and not re.search(
        r"(피|커피|와인|기름|잉크|곰팡|실크|울).{0,6}(묻|얼룩)", msg
    ):
        if lang == "vi":
            return CARD_BEGINNER_VI
        return CARD_BEGINNER_KO

    return ""
