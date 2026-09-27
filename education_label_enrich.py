# -*- coding: utf-8 -*-
"""Post-SOP enrichments: care-label photo CTA + dry-clean capability note."""
from __future__ import annotations

import re
from typing import Any, Optional

from dry_clean_capability import append_capability_block, is_dry_or_pro_topic

_ALREADY_ASKS_LABEL = re.compile(
    r"(라벨\s*사진|케어\s*라벨|nhãn\s*giặt|nhan\s*giat|care\s*label|"
    r"chụp\s*ảnh\s*nhãn|찍어\s*올려|보내\s*주)",
    re.I,
)
_CARE_LABEL_Q = re.compile(
    r"(케어라벨|세탁표시|세탁\s*기호|care\s*label|ký\s*hiệu|ky\s*hieu|nhãn\s*giặt)",
    re.I,
)
_DELICATE = re.compile(
    r"(실크|실크|울|양모|캐시미어|아세테이트|레이온|명품|정장|수트|한복|아오자이|"
    r"silk|wool|cashmere|acetate|rayon|suit|ao\s*dai|lụa|len\b)",
    re.I,
)
_STAINISH = re.compile(
    r"(얼룩|오염|묻|지워|빠지|커피|피|혈액|와인|기름|잉크|땀|"
    r"stain|spot|coffee|blood|wine|oil|ink|"
    r"vết|vet\s*ban|làm\s*sạch|tay\s*vết)",
    re.I,
)


def label_photo_cta(lang: str = "vi") -> str:
    if lang == "ko":
        return (
            "📌 가능하면 옷 안쪽 케어 라벨(세탁기호·혼용률) 사진을 보내 주세요.\n"
            "수온·표백·건조·다림질·전문 케어 한도를 맞춰 추가로 안내합니다."
        )
    if lang == "en":
        return (
            "📌 If possible, send a photo of the care label (symbols + fiber %).\n"
            "We will refine wash temp / bleach / dry / iron / professional-care limits."
        )
    return (
        "📌 Nếu có, gửi ảnh NHÃN GIẶT (ký hiệu + thành phần sợi).\n"
        "Sẽ bổ sung giới hạn nhiệt / tẩy / sấy / ủi / chăm sóc chuyên nghiệp."
    )


def should_append_label_cta(user_message: str, answer: str, entities: Optional[dict] = None) -> bool:
    raw = user_message or ""
    ans = answer or ""
    if _ALREADY_ASKS_LABEL.search(ans) or _CARE_LABEL_Q.search(raw):
        return False
    if "I_CARE_LABEL" in str((entities or {}).get("item_id") or ""):
        return False
    ent = entities or {}
    fabric = str(ent.get("fabric_type") or "").lower()
    delicate_fab = any(x in fabric for x in ("silk", "wool", "acetate", "rayon", "cashmere"))
    if _DELICATE.search(raw) or delicate_fab:
        return True
    if ent.get("stain_id") or ent.get("stain_type") or _STAINISH.search(raw):
        return True
    if str(ent.get("intent") or "") == "treatment" and (ent.get("stain_type") or ent.get("fabric_type")):
        return True
    return False


def enrich_owner_answer(
    answer: str,
    *,
    user_message: str = "",
    lang: str = "vi",
    user_id: str = "",
    channel: str = "",
    entities: Optional[dict[str, Any]] = None,
) -> str:
    """Append label CTA and/or dry-clean lock/unlock when appropriate."""
    text = (answer or "").rstrip()
    if not text:
        return answer

    ent = entities or {}
    item_id = str(ent.get("item_id") or "")

    # Dry / pro capability
    has_machine = False
    try:
        from dry_clean_capability import resolve_has_machine

        has_machine = resolve_has_machine(user_id, channel)
    except Exception:
        has_machine = False

    force_dry = item_id in {"I_DRY_VS_WET"} or bool(ent.get("care_do_not_wash"))
    if force_dry or is_dry_or_pro_topic(user_message) or is_dry_or_pro_topic(text):
        text = append_capability_block(
            text,
            lang=lang if lang in {"ko", "vi", "en"} else "vi",
            has_machine=has_machine,
            force=True,
            user_text=user_message,
        )

    if should_append_label_cta(user_message, text, ent):
        cta = label_photo_cta(lang if lang in {"ko", "vi", "en"} else "vi")
        if cta not in text:
            text = f"{text}\n\n{cta}"

    return text
