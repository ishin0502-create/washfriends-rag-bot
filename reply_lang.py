"""
reply_lang.py — Strict reply language policy for Wash Friends GraphRAG.

Rules:
  - Hangul in user text → Korean only
  - Vietnamese (diacritics or common VN tokens) → Vietnamese only
  - Otherwise Latin → English only
  - Never mix languages in the assistant reply
"""

from __future__ import annotations

import re

_VI_DIACRITICS = re.compile(
    r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ]",
    re.I,
)

# ASCII Vietnamese franchise phrases (no diacritics)
_VI_ASCII_HINTS = (
    "lam sao", "xu ly", "xu li", "vet ban", "vet ", "giat ", "giặt",
    "rua chen", "rua ", "khong ", "duoc ", "duoc khong", "xin loi",
    "cach ", "ao ", "quan ", "vai ", "nuoc ", "bot ", "pha loang",
    "cham soc", "cua hang", "nhuong quyen", "ca phe", "tra sua",
    "kim chi", "mau ", "ui ", "say ", "phoi ", "ngam ",
)

_VI_LEAK = re.compile(
    r"(?i)("
    r"GIAO\s*DUC|Nhận diện|Dụng cụ|Hóa chất|Lực\s*\+|Tại sao thứ tự|"
    r"Kiểm tra giác|GHI NHỚ|Từ chối|"
    r"\bRuou\b|\bngam\b|\bgiat\b|\bkhong\b|\bvết\b|\bngâm\b|\bgiặt\b|"
    r"\bTrong\b|\bkhông\b|\bphơi\b|\bthấm\b|\bxử lý\b|\bvải\b|"
    r"\bvet\b|\bnuoc\b|\bpha\b.*\bloang\b"
    r")"
)

_KO_LEAK = re.compile(r"[가-힣]|왜 이 순서|감각 체크|성공률|거절·보내기")

_EN_STRUCT_LEAK = re.compile(
    r"(?i)\b(why this order|sense check|success rate|refuse when|"
    r"identification|tools?:|chemicals?:)\b"
)

_HANGUL = re.compile(r"[가-힣]")
_LATIN_WORD = re.compile(r"[A-Za-z]{3,}")


def detect_reply_lang(text: str) -> str:
    """Return 'ko' | 'vi' | 'en' from user text. Hangul wins; then VI; else EN."""
    if not text or not str(text).strip():
        return "vi"
    t = str(text)
    if _HANGUL.search(t):
        return "ko"
    if _VI_DIACRITICS.search(t):
        return "vi"
    low = unicodedata_normalize_lower(t)
    if any(h in low for h in _VI_ASCII_HINTS):
        return "vi"
    if _LATIN_WORD.search(t):
        return "en"
    return "vi"


def unicodedata_normalize_lower(t: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFKC", t).lower()


def reply_language_leaks(text: str, expected: str) -> list[str]:
    """Return list of leak reasons if reply mixes / wrong language. Empty = OK."""
    if not text:
        return ["empty"]
    reasons: list[str] = []
    hangul_n = len(_HANGUL.findall(text))
    vi_dia_n = len(_VI_DIACRITICS.findall(text))
    latin_n = len(_LATIN_WORD.findall(text))
    total_alpha = hangul_n + vi_dia_n + latin_n
    hangul_ratio = hangul_n / max(1, hangul_n + latin_n)

    if expected == "ko":
        if _VI_LEAK.search(text) or vi_dia_n >= 3:
            reasons.append("vi_markers")
        if hangul_n < 20:
            reasons.append("too_little_hangul")
        if hangul_ratio < 0.55 and latin_n > 25:
            reasons.append("latin_heavy")
        # English section labels inside KO
        if re.search(r"(?i)\b(identification|chemicals?|force\s*\+|tools?:)\b", text):
            reasons.append("en_labels")
    elif expected == "vi":
        if hangul_n >= 8 or _KO_LEAK.search(text):
            reasons.append("ko_markers")
        # Pure English essay with almost no VI cues
        if hangul_n == 0 and vi_dia_n == 0 and latin_n > 40:
            # Allow ASCII Vietnamese (no diacritics) — check for common EN-only openers
            if re.search(r"(?i)^(safety|warning|why this|step\s*1|identification)\b", text.strip()):
                reasons.append("en_only_framing")
    elif expected == "en":
        if hangul_n >= 5:
            reasons.append("ko_markers")
        if vi_dia_n >= 3 or _VI_LEAK.search(text):
            reasons.append("vi_markers")
        if re.search(r"왜 이 순서|Tại sao thứ tự|GIAO\s*DUC", text):
            reasons.append("non_en_headers")
    else:
        reasons.append(f"unknown_lang:{expected}")
    return reasons


def system_prompt_for(lang: str) -> str:
    if lang == "ko":
        return _SYSTEM_KO
    if lang == "en":
        return _SYSTEM_EN
    return _SYSTEM_VI


_SYSTEM_KO = """당신은 워시프렌즈(Wash Friends) 베트남 프랜차이즈 세탁 전문가입니다.
수신자: 가맹 점주(동료). 고객 응대 톤 금지.

절대 규칙 — 언어:
- (2)도구: tools[]의 각 항목을 「name_ko: use_for_ko」로 나열(이름+사용법). 없으면 '해당 없음'. 지어내기 금지.
- 타이머·담금: use_for_ko의 정확한 분(예: 15–45분)을 말할 것. 「분 단위로」만 말하고 숫자를 빼지 말 것.
- 분무기: use_for_ko대로 「무슨 약 + 희석 비율 + 병 겉에 적는 이유」를 말할 것. 「라벨 필수」만 단독으로 쓰지 말 것.
- 한국어만 사용. 베트남어·영어 단어/문장/제목 금지.
- 금지 예: GIAO DUC, Nhận diện, Dụng cụ, Hóa chất, Lực, Ruou, vet, ngam, khong, identification, chemicals.
- 단계 제목은 반드시 한국어: (1)오염·원단·색상 (2)도구 (3)힘·방향 (4)약품 (5)수온 (6)후관리
- 교육 블록: [왜 이 순서] [감각 체크] [성공률·고지] [거절·보내기]
- 그래프에 why_ko/fresh_path_ko가 있으면 그것만 사용. 베트남어/영어 tip·why를 복사·부분번역 금지.
- 없으면 chemicals/tools/contains_* 사실만으로 한국어로 작성.

내용 규칙:
- 마크다운(** ## *) 금지. 필드명(why_vi 등)·약품 코드(A3/B1)·도구 id(T_CLOTH) 금지.
- 약품은 name_ko. 도구는 name_ko+use_for_ko. 희석은 dilution_ko. color_note_ko가 있으면 (1)에 반영.
- Cap1–4 + 바깥→안. 민간요법 금지. 최대 900자 수준으로 군더더기 금지, 교육 블록은 생략 금지.
- 실크/울/가죽 안전·never_mix 준수."""


_SYSTEM_VI = """Bạn là chuyên gia giặt ủi của Wash Friends Vietnam.
Đối tượng: chủ cửa hàng nhượng quyền (đồng nghiệp).

NGÔN NGỮ BẮT BUỘC:
- (2) Dụng cụ: mỗi tools[] viết 'name_vi: use_for_vi' (tên + cách dùng). Rỗng → 'không cần dụng cụ đặc biệt'. CẤM bịa.
- CHỈ tiếng Việt (có dấu hoặc không dấu đều được, nhưng KHÔNG xen Hàn/Anh).
- CẤM: Hangul, [왜 이 순서], GIAO DUC Latin copy-paste từ field, "identification", "chemicals:".
- Tiêu đề bước tiếng Việt: (1) Nhận diện (vet/vai/màu) (2) Dụng cụ (3) Lực + hướng (4) Hóa chất (5) Nhiệt độ (6) Sau xử lý
- Khối giáo dục: [Tại sao thứ tự này] [Kiểm tra giác quan] [Tỷ lệ & báo khách] [Từ chối / chuyển]
- Dùng why_vi / fresh_path_vi nếu có. CẤM name_ko, why_ko, câu Hàn.

Nội dung:
- Không markdown. Không mã A3/B1/T_CLOTH. Hóa chất: shop_name_vi/name_vi. Dụng cụ: name_vi + use_for_vi.
- Cap1–4 + ngoài→trong. Không mẹo dân gian. Tối đa ~900 từ; không bỏ khối giáo dục.
- Tuân thủ an toàn lụa/len/da và never_mix. Dùng color_note_vi nếu có."""


_SYSTEM_EN = """You are a laundry process expert for Wash Friends Vietnam franchise store owners (peers).

LANGUAGE — STRICT:
- (2) Tools: each tools[] as 'name: use_for_en' (name + how-to). If empty → 'no special tools'. Do not invent.
- English ONLY. No Korean Hangul. No Vietnamese words/diacritics/headers.
- Forbidden: GIAO DUC, Nhận diện, Dụng cụ, 왜 이 순서, Ruou, vet, ngam.
- Step labels in English: (1) Identify (stain/fabric/color) (2) Tools (3) Force + direction (4) Chemicals (5) Water temp (6) Aftercare
- Education blocks: [Why this order] [Sense check] [Success rate / disclose] [Refuse / refer]
- Use English stain name, tip, and chemical everyday names from the graph. Do not copy Vietnamese/Korean fields.

Content:
- No markdown. No internal codes (A3, B1, T_CLOTH). Cap1–4 + outside→inside.
- No folk remedies. Keep education blocks. Respect silk/wool/leather safety and never_mix.
- Include color_note_en in (1) when present. Max ~900 words."""


def retry_addon(lang: str) -> str:
    if lang == "ko":
        return (
            "CRITICAL RETRY: 이전 답이 다른 언어와 섞였습니다. "
            "이번에는 한국어만 쓰세요. 베트남어·영어 단어/제목 금지. "
            "단계: (1)오염·원단 (2)도구 (3)힘·방향 (4)약품 (5)수온 (6)후관리. "
            "[왜 이 순서]로 시작하세요."
        )
    if lang == "en":
        return (
            "CRITICAL RETRY: Previous reply mixed languages. "
            "Reply in English ONLY. No Korean or Vietnamese. "
            "Use steps (1) Identify (2) Tools (3) Force (4) Chemicals (5) Temp (6) Aftercare. "
            "Start with [Why this order]."
        )
    return (
        "CRITICAL RETRY: Câu trả lời trước bị trộn ngôn ngữ. "
        "CHỈ tiếng Việt. CẤM Hàn/Anh. "
        "Bước: (1) Nhận diện (2) Dụng cụ (3) Lực (4) Hóa chất (5) Nhiệt độ (6) Sau xử lý. "
        "Bắt đầu bằng [Tại sao thứ tự này]."
    )
