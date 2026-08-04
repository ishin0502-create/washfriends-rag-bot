"""
image_analyzer.py
Wash Friends Vietnam - Stain Photo Analyzer

Analyzes a stain photo using GPT-4o-mini Vision and returns structured entities
compatible with the graphrag_engine pipeline.
"""

import os
import base64
import json
import re
from urllib.request import urlopen, Request

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

VISION_PROMPT = """You are a laundry expert AI assistant specializing in stain identification.

Analyze this photo and identify:
1. The type of stain (e.g., coffee, blood, oil, grass, wine, ink, rust, makeup)
2. The fabric type if visible (e.g., cotton, silk, polyester, wool, denim)
3. The stain severity (light / medium / heavy)
4. Any special characteristics (dried vs fresh, set-in, colorfast, etc.)

Respond in JSON with this exact format:
{
  "stain_type": "...",
  "fabric_type": "...",
  "severity": "light|medium|heavy",
  "characteristics": ["...", "..."],
  "confidence": "high|medium|low",
  "care_notes": "brief note about special care needs",
  "stain_color": "red|yellow|brown|black|blue|green|white|null",
  "lang": "vi"
}

If you cannot identify the stain clearly, still return JSON but set confidence to "low"
and use your best guess for stain_type."""


def fetch_image_as_base64(url):
    """Download an image from a URL and return (base64_data, media_type)."""
    headers = {
        "User-Agent": "WashFriendsBot/1.0",
        "Accept": "image/*",
    }
    req = Request(url, headers=headers)
    with urlopen(req, timeout=10) as resp:
        content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip()
        data = resp.read()
    return base64.standard_b64encode(data).decode("utf-8"), content_type


def _to_graphrag_entities(analysis: dict, user_caption: str = "") -> dict:
    """Normalize vision output into graphrag_engine entity shape."""
    stain = analysis.get("stain_type") or None
    fabric = analysis.get("fabric_type") or None
    if stain in ("unknown", "", "null"):
        stain = None
    if fabric in ("unknown", "", "null"):
        fabric = None

    # Prefer caption hints when vision confidence is low
    caption = (user_caption or "").strip()
    confidence = analysis.get("confidence", "low")
    if caption and (not stain or confidence == "low"):
        # Keep caption for LLM; extractor-like fields stay from vision when present
        pass

    return {
        "stain_type": stain,
        "fabric_type": fabric,
        "intent": "mystery" if not stain else "treatment",
        "hours_since": None,
        "stain_color": analysis.get("stain_color") if analysis.get("stain_color") not in (None, "null") else None,
        "smell": None,
        "water_spreads": None,
        "group_id": None,
        "stain_id": None,
        "attempt_number": None,
        "lang": analysis.get("lang") or "vi",
        "severity": analysis.get("severity", "medium"),
        "characteristics": analysis.get("characteristics") or [],
        "confidence": confidence,
        "care_notes": analysis.get("care_notes") or "",
        "_image_analysis": True,
        "_user_caption": caption,
    }


def analyze_stain_image(image_url=None, image_base64=None, media_type="image/jpeg", user_caption=""):
    """Analyze a stain image and return GraphRAG-compatible entity dict."""
    if image_url and not image_base64:
        image_base64, media_type = fetch_image_as_base64(image_url)

    if not image_base64:
        return _to_graphrag_entities({
            "stain_type": "unknown",
            "fabric_type": "unknown",
            "severity": "medium",
            "characteristics": [],
            "confidence": "low",
            "care_notes": "No image provided",
        }, user_caption=user_caption)

    prompt_text = VISION_PROMPT
    if user_caption:
        prompt_text += f"\n\nUser caption/hint: {user_caption}"

    message = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_base64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt_text,
                    },
                ],
            }
        ],
    )

    raw = message.choices[0].message.content.strip()
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            return _to_graphrag_entities(parsed, user_caption=user_caption)
        except json.JSONDecodeError:
            pass

    return _to_graphrag_entities({
        "stain_type": "unknown",
        "fabric_type": "unknown",
        "severity": "medium",
        "characteristics": [],
        "confidence": "low",
        "care_notes": raw[:200],
    }, user_caption=user_caption)


def build_image_entity_context(analysis):
    """Convert image analysis result into text prefix for GraphRAG LLM."""
    stain = analysis.get("stain_type") or "unknown"
    fabric = analysis.get("fabric_type") or "unknown"
    severity = analysis.get("severity", "medium")
    chars = analysis.get("characteristics", [])
    notes = analysis.get("care_notes", "")
    caption = analysis.get("_user_caption", "")

    parts = [f"Anh phan tich: loai vet={stain}", f"vai={fabric}", f"muc do={severity}"]
    if chars:
        parts.append("dac diem: " + ", ".join(chars))
    if notes:
        parts.append("ghi chu: " + notes)
    if caption:
        parts.append("chu thich nguoi dung: " + caption)

    return " | ".join(parts)


# backward-compatibility alias used by zalo_handler and facebook_handler
build_image_context_prefix = build_image_entity_context
