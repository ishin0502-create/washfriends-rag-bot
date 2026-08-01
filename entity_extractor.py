"""
entity_extractor.py
Wash Friends Vietnam — GraphRAG Entity Extractor

Extracts structured entities from a free-text user message (Vietnamese / Korean / English)
using Claude Haiku (fast + cheap) so the main engine can route to the right Neo4j query.

Entities extracted:
  - stain_type      : "nước tương" / "혈액" / "coffee" / etc.  (None if unknown)
  - fabric_type     : "lụa" / "면" / "cotton" / etc.          (None if unknown)
  - intent          : treatment | rescue | price | mystery | browse | safety | daily | hardest
  - hours_since     : float (None if not mentioned)
  - stain_color     : red|yellow|brown|black|blue|green|white  (None if unknown)
  - smell           : food|sweet|sour|fishy|chemical|none      (None if not mentioned)
  - water_spreads   : bool (None if not mentioned)
  - group_id        : group_oil|group_tannin|group_protein|group_dye|group_special (None)
  - stain_id        : exact stain ID if identifiable from text (None otherwise)
  - attempt_number  : 1 or 2 (rescue plan B or C)
  - lang            : vi|ko|en  (detected from message)
"""

import os
import json
import re
from anthropic import Anthropic

_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

EXTRACTION_SYSTEM = """You are an entity extractor for a Vietnamese laundry shop chatbot.
Extract structured data from the user's message. Output ONLY valid JSON, nothing else.

JSON schema (all fields optional — use null if absent):
{
  "stain_type": "string or null",
  "fabric_type": "string or null",
  "intent": "treatment|rescue|price|mystery|browse|safety|daily|hardest",
  "hours_since": "number or null",
  "stain_color": "red|yellow|brown|black|blue|green|white|null",
  "smell": "food|sweet|sour|fishy|chemical|none|null",
  "water_spreads": "true|false|null",
  "group_id": "group_oil|group_tannin|group_protein|group_dye|group_special|null",
  "stain_id": "string or null",
  "attempt_number": "1|2|null",
  "lang": "vi|ko|en"
}

Intent rules:
- treatment: user wants step-by-step stain removal (default when stain mentioned)
- rescue: user says "tried but still there", "đã làm rồi nhưng", "이미 했는데"
- price: user asks about cost, "bao nhiêu tiền", "얼마"
- mystery: user doesn't know what the stain is, "không biết", "모르겠어"
- browse: user asks to list stains in a category, "có bao nhiêu loại"
- safety: user asks about chemical safety or mixing
- daily: user asks "what to watch today", "hôm nay cần lưu ý gì"
- hardest: user asks which stains are hardest, "vết nào khó nhất"

Stain IDs (use exact ID if confident):
oil-1=cooking oil, oil-2=machine oil, oil-3=cosmetic oil, lip-1=lipstick,
blood-1=fresh blood, blood-2=old blood, egg-1=egg, milk-1=milk, sweat-1=sweat,
coffee-1=coffee, tea-1=tea, wine-1=wine, sauce-1=soy sauce, tan-9=nuocmam/nước mắm,
ink-1=ballpoint pen, ink-2=permanent marker, grass-1=grass/chlorophyll,
rust-1=rust, mold-1=mold/mildew

Group IDs: group_oil, group_tannin, group_protein, group_dye, group_special

Language detection:
- vi: Vietnamese words (vết, giặt, áo, quần, chất, tẩy, nước, lụa, etc.)
- ko: Korean characters (한글)
- en: English otherwise

Common stain names:
- VI: vết dầu, vết máu, vết cà phê, vết nước tương, nước mắm, cỏ, mực, gỉ sét, mốc
- KO: 기름, 혈액, 커피, 간장, 액젓, 잔디, 잉크, 녹, 곰팡이
- EN: oil, blood, coffee, soy sauce, fish sauce, grass, ink, rust, mold

Common fabric names:
- VI: lụa, cotton, vải bông, len, tổng hợp, polyester, denim, vải lanh
- KO: 실크, 면, 울, 합성섬유, 폴리에스터, 데님, 린넨
- EN: silk, cotton, wool, synthetic, polyester, denim, linen"""


def extract_entities(user_message: str) -> dict:
    """
    Extract entities from a user message.
    Returns a dict with all entity fields (None for missing ones).
    Falls back to safe defaults on any error.
    """
    try:
        response = _client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            system=EXTRACTION_SYSTEM,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        entities = json.loads(raw)

        # Normalize types
        _coerce_types(entities)
        return entities

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        # Graceful fallback — return minimal safe defaults
        return _fallback_entities(user_message)


def _coerce_types(e: dict) -> None:
    """Coerce extracted values to expected Python types in-place."""
    # Normalize null-like strings
    for key in list(e.keys()):
        if e[key] in (None, "null", "none", "", "None"):
            e[key] = None

    # hours_since → float
    if e.get("hours_since") is not None:
        try:
            e["hours_since"] = float(e["hours_since"])
        except (ValueError, TypeError):
            e["hours_since"] = None

    # attempt_number → int
    if e.get("attempt_number") is not None:
        try:
            e["attempt_number"] = int(e["attempt_number"])
        except (ValueError, TypeError):
            e["attempt_number"] = None

    # water_spreads → bool
    if isinstance(e.get("water_spreads"), str):
        e["water_spreads"] = e["water_spreads"].lower() == "true"

    # Defaults
    if not e.get("intent"):
        e["intent"] = "treatment"
    if not e.get("lang"):
        e["lang"] = "vi"


def _fallback_entities(message: str) -> dict:
    """
    Minimal heuristic fallback when LLM extraction fails.
    Detects Korean characters for lang; everything else is None.
    """
    lang = "vi"
    if re.search(r"[가-힣]", message):
        lang = "ko"
    elif re.search(r"[a-zA-Z]{4,}", message) and not re.search(r"[àáâãèéêìíòóôùúăđơư]", message):
        lang = "en"

    return {
        "stain_type": None,
        "fabric_type": None,
        "intent": "treatment",
        "hours_since": None,
        "stain_color": None,
        "smell": None,
        "water_spreads": None,
        "group_id": None,
        "stain_id": None,
        "attempt_number": None,
        "lang": lang,
    }
