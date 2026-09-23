# -*- coding: utf-8 -*-
"""Hard stain binds for yellowing vs fresh sweat + VN specialty (no LLM)."""
from __future__ import annotations

import unicodedata
from typing import Optional


def _norm_ascii(text: str) -> str:
    t = unicodedata.normalize("NFD", text or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return t.lower()


def bind_vn_specialty_stain(user_message: str, raw_n: Optional[str] = None) -> Optional[str]:
    """Return VN specialty stain ids (v41) or None. More specific phrases first."""
    msg = user_message or ""
    raw_n = raw_n if raw_n is not None else _norm_ascii(msg)
    low = msg.lower()

    # Mangosteen before mango
    if any(k in msg for k in ("망고스틴", "망고스텐")) or any(
        k in raw_n for k in ("mangosteen", "mang cut", "mangcut")
    ) or "măng cụt" in low:
        return "S_VN_MANGOSTEEN"

    if "두리안" in msg or "durian" in raw_n or "sau rieng" in raw_n or "sầu riêng" in low:
        return "S_VN_DURIAN"

    if any(k in msg for k in ("잭프루트", "미 수액", "미수액")) or any(
        k in raw_n for k in ("jackfruit", "nhua mit")
    ) or ("nhựa mít" in low) or (
        ("mít" in low or " mit" in f" {raw_n}")
        and ("nhựa" in low or "nhua" in raw_n or "sap" in raw_n)
    ):
        return "S_VN_JACKFRUIT"

    if any(k in msg for k in ("반쎄오", "바인쎄오", "반세오")) or "banh xeo" in raw_n or "bánh xèo" in low:
        return "S_VN_BANH_XEO"

    if any(k in msg for k in ("용과", "드래곤프루트", "드래곤 프루트")) or any(
        k in raw_n for k in ("dragon fruit", "thanh long", "pitaya")
    ):
        return "S_VN_DRAGON_FRUIT"

    if "람부탄" in msg or "rambutan" in raw_n or "chom chom" in raw_n or "chôm chôm" in low:
        return "S_VN_RAMBUTAN"

    # Mango juice — after mangosteen
    mango_hit = (
        any(k in msg for k in ("망고 주스", "망고주스", "망고즙", "망고 얼룩"))
        or "mango juice" in raw_n
        or "nuoc xoai" in raw_n
        or "nước xoài" in low
        or (
            ("망고" in msg or "mango" in raw_n or "xoai" in raw_n or "xoài" in low)
            and (
                any(k in msg for k in ("얼룩", "묻", "주스", "즙"))
                or any(k in raw_n for k in ("vet", "stain", "juice"))
            )
        )
    )
    if mango_hit and "mangosteen" not in raw_n and "망고스틴" not in msg and "망고스텐" not in msg:
        return "S_VN_MANGO"

    if any(k in msg for k in ("코코넛 오일", "코코넛오일", "야자유")) or any(
        k in raw_n for k in ("coconut oil", "dau dua")
    ) or "dầu dừa" in low:
        return "S_VN_COCONUT_OIL"

    if any(k in msg for k in ("향재", "향 그을음", "향재 얼룩", "분향")) or any(
        k in raw_n for k in ("incense ash", "tro nhang", "incense soot")
    ) or ("nhang" in raw_n and ("tro" in raw_n or "ash" in raw_n or "soot" in raw_n)):
        return "S_VN_INCENSE_ASH"

    if any(k in msg for k in ("사테", "사떼", "칠리오일", "칠리 오일")) or any(
        k in raw_n for k in ("sa te", "satay", "chili oil")
    ) or "sa tế" in low:
        return "S_VN_SA_TE"

    # Nuoc cham before fish sauce
    if any(k in msg for k in ("느엉쩜", "느억짬", "디핑소스", "월남 소스")) or any(
        k in raw_n for k in ("nuoc cham", "dipping sauce")
    ) or "nước chấm" in low:
        return "S_VN_NUOC_CHAM"

    # --- v43 motorbike / climate (specific before generic oil) ---
    if any(
        k in msg
        for k in (
            "체인 기름",
            "체인기름",
            "체인유",
            "체인 오일",
            "체인오일",
            "오토바이 체인",
            "바이크 체인",
        )
    ) or (
        ("체인" in msg or "chain" in raw_n)
        and any(k in msg for k in ("기름", "오일", "묻", "얼룩"))
    ) or any(
        k in raw_n
        for k in ("chain oil", "chain grease", "dau xich", "dầu xích", "dau xích")
    ) or "dầu xích" in low:
        return "S_VN_CHAIN_OIL"

    # "오토바이 … 기름" without 체인 → still prefer chain if 체인 cue; else motorbike oil later
    if (
        any(k in msg for k in ("오토바이", "바이크", "xe máy", "xe may"))
        and any(k in msg for k in ("체인", "chain", "xích", "xich"))
        and any(k in msg for k in ("기름", "오일", "dầu", "dau", "묻", "얼룩"))
    ):
        return "S_VN_CHAIN_OIL"

    if any(k in msg for k in ("매연", "그을음", "배기가스", "검댕")) or any(
        k in raw_n for k in ("bo hong", "bồ hóng", "exhaust soot", "khoi xe", "khói xe")
    ) or "bồ hóng" in low:
        return "S_VN_EXHAUST_SOOT"

    if any(k in msg for k in ("브레이크액", "브레이크 오일", "브레이크 기름", "유압유")) or any(
        k in raw_n for k in ("brake fluid", "dau thang", "dầu thắng", "dau phanh", "dầu phanh")
    ):
        return "S_VN_BRAKE_FLUID"

    if any(k in msg for k in ("휘발유", "가솔린", "주유소")) or any(
        k in raw_n for k in ("gasoline", "petrol", "xang ", " xang")
    ) or ("xăng" in low and any(k in low for k in ("vết", "mùi", "đổ", "dính", "stain", "묻", "얼룩", "냄새"))):
        return "S_VN_GASOLINE"
    if "xăng" in low and any(k in msg for k in ("묻", "얼룩", "냄새", "옷")):
        return "S_VN_GASOLINE"

    if any(k in msg for k in ("고무 자국", "타이어 자국", "고무줄 자국")) or any(
        k in raw_n for k in ("rubber mark", "tire mark", "vet cao su", "vết cao su")
    ):
        return "S_VN_RUBBER_MARK"

    if (
        any(k in msg for k in ("선크림", "썬크림", "자외선차단"))
        or "kem chong nang" in raw_n
        or "kem chống nắng" in low
        or "sunscreen" in raw_n
    ) and (
        any(k in msg for k in ("땀", "목둘레", "겨드랑", "노랗", "황변", "누렇"))
        or any(k in raw_n for k in ("mo hoi", "mồ hôi", "co ao", "cổ áo", "vang", "yellow"))
    ):
        return "S_VN_SWEAT_SUNSCREEN"

    if any(k in msg for k in ("빗물 자국", "빗물 때", "산성비", "비 얼룩")) or any(
        k in raw_n for k in ("vet mua", "vết mưa", "acid rain", "dirty rain", "mua ban")
    ):
        return "S_VN_ACID_RAIN"

    if any(k in msg for k in ("시멘트", "석회", "콘크리트 가루")) or any(
        k in raw_n for k in ("xi mang", "xi măng", "cement", "vôi", "voi ")
    ):
        return "S_VN_CEMENT"

    return None


def bind_sweat_or_yellow_stain(user_message: str, raw_n: Optional[str] = None) -> Optional[str]:
    """Return S_SWEAT_YELLOW / S_SHIRT_YELLOW / S_SWEAT_FRESH or None."""
    msg = user_message or ""
    raw_n = raw_n if raw_n is not None else _norm_ascii(msg)

    # Prefer compound sweat+sunscreen when both cues present
    if (
        any(k in msg for k in ("선크림", "썬크림", "자외선차단"))
        or "sunscreen" in raw_n
        or "kem chong nang" in raw_n
        or "kem chống nắng" in (msg or "").lower()
    ) and any(k in msg for k in ("땀", "목둘레", "겨드랑", "노랗", "황변", "누렇")):
        return "S_VN_SWEAT_SUNSCREEN"

    if any(k in msg for k in ("겨드랑이", "암내", "누런 겨드랑이")) or "ve o nach" in raw_n or "armpit" in raw_n:
        return "S_SWEAT_YELLOW"

    if (
        (
            "땀" in msg
            or "mo hoi" in raw_n
            or "sweat" in raw_n
            or "겨드랑" in msg
        )
        and any(
            k in msg
            for k in (
                "황변", "누렇", "노랗", "노란", "누래", "누런",
                "오래된", "오래됐", "오래 된", "몇 달", "몇달", "오랫동안", "오래전",
            )
        )
        and not any(
            k in msg for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠")
        )
    ) or (
        ("mo hoi" in raw_n or "sweat" in raw_n)
        and any(k in raw_n for k in ("vang", "yellow", "o vang", "lau ngay", "old sweat", "aged"))
        and "ao so mi" not in raw_n
    ):
        return "S_SWEAT_YELLOW"

    if any(
        k in msg for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠")
    ) and any(
        k in msg
        for k in ("누렇", "황변", "노랗", "누래", "변색", "노란", "누래짐", "누래졌")
    ) and not any(k in msg for k in ("향수", "데오", "데오드란트")):
        return "S_SHIRT_YELLOW"

    if any(k in msg for k in ("누렇게", "황변", "변색", "누래짐")) and any(
        k in msg for k in ("셔츠", "와이", "흰옷", "흰 옷", "흰티", "흰 티")
    ) and not any(k in msg for k in ("향수", "데오", "데오드란트")):
        return "S_SHIRT_YELLOW"

    if any(k in msg for k in ("황변 제거", "황변빼", "황변 빼", "누래짐 제거")) and not any(
        k in msg for k in ("향수", "데오", "데오드란트")
    ):
        return "S_SHIRT_YELLOW"

    if any(k in msg for k in ("땀냄새", "땀 묻", "땀얼룩", "땀 얼룩")) or (
        "땀" in msg
        and not any(
            k in msg
            for k in (
                "겨드랑", "누렇", "황변", "데오", "땀억제",
                "노랗", "노란", "누래", "누런",
                "오래된", "오래됐", "몇 달", "몇달", "오랫동안",
            )
        )
    ) or "mo hoi tuoi" in raw_n or (
        "sweat" in raw_n
        and "yellow" not in raw_n
        and "armpit" not in raw_n
        and "old" not in raw_n
        and "aged" not in raw_n
        and "deodorant" not in raw_n
        and "khu mui" not in raw_n
    ):
        return "S_SWEAT_FRESH"

    return None
