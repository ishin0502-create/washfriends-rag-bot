"""
image_analyzer.py
Wash Friends Vietnam - Stain Photo Analyzer

Analyzes a stain photo using Claude Vision and returns structured entities
compatible with the graphrag_engine pipeline.

Supported inputs:
  - Image URL (from Zalo / Facebook CDN)
  - Base64-encoded image bytes

Returns the same entity dict format as entity_extractor.py,
so the rest of the pipeline is unchanged.
"""

import os
import base64
import re
from typing import Optional
from urllib.request import urlopen, Request

from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

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
  "care_notes": "brief note about special care needs"
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


def analyze_stain_image(image_url=None, image_base64=None, media_type="image/jpeg"):
    """Analyze a stain image and return structured entity dict."""
    if image_url and not image_base64:
        image_base64, media_type = fetch_image_as_base64(image_url)

    if not image_base64:
        return {
            "stain_type": "unknown",
            "fabric_type": "unknown",
            "severity": "medium",
            "characteristics": [],
            "confidence": "low",
            "care_notes": "No image provided",
        }

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": VISION_PROMPT,
                    },
                ],
            }
        ],
    )

    raw = message.content[0].text.strip()
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        import json
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    return {
        "stain_type": "unknown",
        "fabric_type": "unknown",
        "severity": "medium",
        "characteristics": [],
        "confidence": "low",
        "care_notes": raw[:200],
    }


def build_image_entity_context(analysis):
    """Convert image analysis result into text for GraphRAG entity extractor."""
    stain = analysis.get("stain_type", "unknown")
    fabric = analysis.get("fabric_type", "unknown")
    severity = analysis.get("severity", "medium")
    chars = analysis.get("characteristics", [])
    notes = analysis.get("care_notes", "")

    parts = ["Stain type: " + stain]
    if fabric != "unknown":
        parts.append("Fabric: " + fabric)
    parts.append("Severity: " + severity)
    if chars:
        parts.append("Characteristics: " + ", ".join(chars))
    if notes:
        parts.append("Notes: " + notes)

    return ". ".join(parts) + "."
