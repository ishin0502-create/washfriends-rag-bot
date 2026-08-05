"""
entity_extractor.py
Wash Friends Vietnam — GraphRAG Entity Extractor

Extracts structured entities from a free-text user message (Vietnamese / Korean / English)
using GPT-4o-mini (fast + cheap) so the main engine can route to the right Neo4j query.

Entities extracted:
  - stain_type      : "nuoc tuong" / "혈액" / "coffee" / etc.  (None if unknown)
  - fabric_type     : "lua" / "면" / "cotton" / etc.           (None if unknown)
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
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

EXTRACTION_SYSTEM = """You are an entity extractor for a Vietnamese laundry shop chatbot.
Extract structured data from the user's message. Output ONLY valid JSON, nothing else.

JSON schema (all fields optional -- use null if absent):
{
  "stain_type": "string or null",
  "fabric_type": "string or null",
  "intent": "treatment|rescue|price|mystery|browse|safety|daily|hardest",
  "hours_since": "number or null",
  "stain_color": "red|yellow|brown|black|blue|green|white|null",
  "smell": "food|sweet|sour|fishy|chemical|none|null",
  "water_spreads": "true|false|null",
  "group_id": "G1|G2|G3|G4|G5|null",
  "stain_id": "string or null",
  "attempt_number": "1|2|null",
  "lang": "vi|ko|en"
}

Intent rules:
- treatment: user wants step-by-step stain removal (default when stain mentioned)
- rescue: user says tried but still there, "da lam roi nhung", "이미 했는데"
- price: user asks about cost, "bao nhieu tien", "얼마"
- mystery: user does not know what the stain is, "khong biet", "모르겠어"
- browse: user asks to list stains in a category, "co bao nhieu loai"
- safety: user asks about chemical safety or mixing
- daily: user asks what to watch today, "hom nay can luu y gi"
- hardest: user asks which stains are hardest, "vet nao kho nhat"

Stain IDs (use exact ID if confident):
S_COOKING_OIL=cooking oil/dau an, S_ENGINE_OIL=machine oil, S_LIPSTICK=lipstick/son moi,
S_BLOOD_FRESH=fresh blood/mau tuoi, S_BLOOD_DRY=old blood/mau kho, S_EGG=egg/trung,
S_MILK=milk/sua, S_SWEAT_FRESH=sweat/mo hoi, S_SWEAT_YELLOW=armpit yellow,
S_BLACK_COFFEE=black coffee/ca phe den, S_MILK_COFFEE=milk coffee/ca phe sua,
S_TEA=tea/tra, S_RED_WINE=wine, S_SOY_SAUCE=soy sauce/nuoc tuong, S_FISH_SAUCE=nuoc mam,
S_INK_PEN=ballpoint ink/muc, S_INK_PERMANENT=permanent marker, S_GRASS=grass/co,
S_MUD=mud/bun, S_CURRY=curry/nghe, S_MUSTARD=mustard,
S_LATERITE=laterite/dat do/dat do laterite/red soil Vietnam,
S_MOTORBIKE_OIL=motorbike oil/dau nhot xe may,
S_MILDEW=mildew/nam moc, S_RUST=rust/ri set,
S_DEODORANT=deodorant, S_PAINT_LATEX=latex paint/son nuoc, S_GLUE=glue/keo

IMPORTANT: "dat do" / "laterite" / "đất đỏ" = S_LATERITE (red soil), NEVER blood.
"đỏ" alone does not mean blood if "dat"/"laterite"/"đất" is present.
If the user names a specific stain, intent MUST be "treatment" (not mystery).

Group IDs: G1=protein, G2=oil, G3=tannin, G4=dye, G5=complex

Language detection:
- vi: Vietnamese words (vet, giat, ao, quan, chat, tay, nuoc, lua, etc.)
- ko: Korean characters
- en: English otherwise

Common stain names:
- VI: vet dau, vet mau, vet ca phe, vet nuoc tuong, nuoc mam, co, muc, gi set, moc
- KO: 기름, 혈액, 커피, 간장, 액젓, 잔디, 잉크, 녹, 곰팡이
- EN: oil, blood, coffee, soy sauce, fish sauce, grass, ink, rust, mold

Common fabric names:
- VI: lua, cotton, vai bong, len, tong hop, polyester, denim, vai lanh
- KO: 실크, 면, 울, 합성섬유, 폴리에스터, 데님, 린넨
- EN: silk, cotton, wool, synthetic, polyester, denim, linen"""


def extract_entities(user_message: str) -> dict:
    """
    Extract entities from a user message.
    Returns a dict with all entity fields (None for missing ones).
    Falls back to safe defaults on any error.
    """
    try:
        response = _client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=512,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM},
                {"role": "user", "content": user_message},
            ],
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        entities = json.loads(raw)

        # Normalize types
        _coerce_types(entities)
        return entities

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        # Graceful fallback -- return minimal safe defaults
        return _fallback_entities(user_message)


def _coerce_types(e: dict) -> None:
    """Coerce extracted values to expected Python types in-place."""
    # Normalize null-like strings
    for key in list(e.keys()):
        if e[key] in (None, "null", "none", "", "None"):
            e[key] = None

    # hours_since -> float
    if e.get("hours_since") is not None:
        try:
            e["hours_since"] = float(e["hours_since"])
        except (ValueError, TypeError):
            e["hours_since"] = None

    # attempt_number -> int
    if e.get("attempt_number") is not None:
        try:
            e["attempt_number"] = int(e["attempt_number"])
        except (ValueError, TypeError):
            e["attempt_number"] = None

    # water_spreads -> bool
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
