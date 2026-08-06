"""
image_flow.py
Zalo / Facebook owner image path: stain → GraphRAG, or care-label clarify loop.
"""

from __future__ import annotations

from graphrag_engine import generate_response_from_entities
from image_analyzer import (
    analyze_image,
    build_image_context_prefix,
    build_clarify_and_label_request,
    format_care_label_reply,
    needs_clarification,
)
from user_session import get_session, set_pending_label, pop_pending_label, clear_session


def process_channel_image(
    channel: str,
    user_id: str,
    image_url: str,
    caption: str = "",
) -> str:
    """
    Sync pipeline for messenger image events.
    Returns owner-facing reply text (VI/KO).
    """
    caption = (caption or "").strip()
    session = get_session(channel, user_id)
    awaiting_label = session.get("awaiting") == "care_label"

    result = analyze_image(image_url=image_url, user_caption=caption)
    kind = result.get("image_kind") or "stain_photo"
    lang = result.get("lang") or session.get("lang") or "vi"

    # Owner already asked for a care label — prefer label path
    if awaiting_label:
        if kind == "care_label":
            pending = pop_pending_label(channel, user_id) or session
            return format_care_label_reply(result, lang=pending.get("lang") or lang, pending=pending)
        # Sent another stain / unclear photo while waiting
        if kind == "stain_photo" and not needs_clarification(result):
            clear_session(channel, user_id)
            prefix = build_image_context_prefix(result)
            user_cap = caption or result.get("stain_type") or ""
            return generate_response_from_entities(result, user_caption=user_cap, prefix=prefix)
        # Still unclear — keep waiting, re-ask
        set_pending_label(
            channel,
            user_id,
            lang=lang,
            stain_guess=result.get("stain_type") or session.get("stain_guess") or "",
            fabric_guess=result.get("fabric_type") or session.get("fabric_guess") or "",
            caption=caption or session.get("caption") or "",
            confidence=str(result.get("confidence") or "low"),
        )
        return build_clarify_and_label_request(result, lang=lang)

    # Fresh image: care label without prior ask
    if kind == "care_label":
        return format_care_label_reply(result, lang=lang, pending=None)

    if kind == "other" or needs_clarification(result):
        set_pending_label(
            channel,
            user_id,
            lang=lang,
            stain_guess=result.get("stain_type") or "",
            fabric_guess=result.get("fabric_type") or "",
            caption=caption,
            confidence=str(result.get("confidence") or "low"),
        )
        return build_clarify_and_label_request(result, lang=lang)

    prefix = build_image_context_prefix(result)
    user_cap = caption or result.get("stain_type") or ""
    return generate_response_from_entities(result, user_caption=user_cap, prefix=prefix)
