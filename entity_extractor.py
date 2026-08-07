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
S_COOKING_OIL=cooking oil/dau an/기름/식용유, S_ENGINE_OIL=machine oil, S_GREASE=grease/mo,
S_MAYO=mayonnaise/마요네즈, S_COLLAR_STAIN=collar/목때/vong co,
S_BLOOD_FRESH=fresh blood/mau tuoi/핏자국, S_BLOOD_DRY=old blood/mau kho,
S_EGG=egg/trung, S_MILK=milk/sua/우유(비커피·비분유), S_VOMIT=vomit/chat non/구토/토물,
S_URINE=urine/nuoc tieu/소변/오줌, S_FECES=feces/phan/대변/분변,
S_BABY_FORMULA=baby formula/sua cong thuc/분유,
S_GRASS=grass/co xanh/잔디/풀물, S_MUD=mud/bun/진흙, S_CHOCOLATE=chocolate/socola/초코,
S_SWEAT_FRESH=sweat/mo hoi/땀(신선), S_SWEAT_YELLOW=armpit yellow,
S_BLACK_COFFEE=black coffee/ca phe den, S_MILK_COFFEE=milk coffee/ca phe sua/latte,
S_TEA=tea/tra, S_RED_WINE=wine, S_SOY_SAUCE=soy sauce/nuoc tuong/간장,
S_FISH_SAUCE=nuoc mam/느억맘/액젓, S_KETCHUP=ketchup/케첩, S_TOMATO_SAUCE=tomato sauce,
S_FRUIT_JUICE=juice/주스, S_KIMCHI=kimchi/김치,
S_INK_PEN=ballpoint ink/muc, S_INK_PERMANENT=permanent marker,
S_CURRY=curry/nghe,
S_DYE_TRANSFER=dye transfer/이염/mau lan/lo mau,
S_STARCH_TRANSFER=starch dye/풀 이염/ho tinh bot,
S_SHIRT_YELLOW=yellowed white shirt/와이셔츠 황변/누렇게,
S_LATERITE=laterite/dat do/dat do laterite/red soil Vietnam,
S_MOTORBIKE_OIL=motorbike oil/dau nhot xe may,
S_MILDEW=mildew/nam moc/곰팡이, S_RUST=rust/ri set,
S_LIPSTICK=lipstick/립스틱/son moi, S_FOUNDATION=foundation/파운데이션/쿠션/kem nen,
S_DEODORANT=deodorant/데오/땀억제제, S_PERFUME=perfume/향수/nuoc hoa,
S_GUM=chewing gum/껌/keo cao su, S_CANDLE_WAX=candle wax/촛농/sap nen,
S_BUTTER=butter/버터/bo, S_SHOE_POLISH=shoe polish/구두약/xi giay,
S_BBQ_SAUCE=BBQ sauce/바베큐, S_MUSTARD=mustard/머스터드/겨자,
S_NAIL_POLISH=nail polish/매니큐어/son mong, S_GLUE=glue/접착제/keo dan,
S_PAINT_LATEX=latex paint/수성페인트/son nuoc,
S_SUNSCREEN=sunscreen/선크림/kem chong nang, S_TAR=tar/타르/nhua duong,
S_MASCARA=mascara/마스카라, S_HAIR_DYE=hair dye/염색약/thuoc nhuom,
I_BED_SHEET=bed sheet/시트, I_TOWEL=towel/수건, I_BABY_WEAR=baby clothes/아기옷,
I_SWIMWEAR=swimwear/수영복, I_ODOR_SMOKE=smoke odor/담배냄새

IMPORTANT: "dat do" / "laterite" / "đất đỏ" = S_LATERITE (red soil), NEVER blood.
"đỏ" alone does not mean blood if "dat"/"laterite"/"đất" is present.
Kimchi / 김치 / kim chi = S_KIMCHI (not tomato alone).
Ketchup / 케첩 = S_KETCHUP (not generic tomato only).
Lipstick / 립스틱 / son moi = S_LIPSTICK. Foundation/cushion/파운데이션 = S_FOUNDATION.
Generic 화장품/makeup without type → prefer S_LIPSTICK if lip color; else S_FOUNDATION.
이염 / dye transfer / mau lan = S_DYE_TRANSFER (not color fade restore).
와이셔츠 누렇/황변/변색 = S_SHIRT_YELLOW (not only armpit sweat).
와이셔츠 세탁 방법(얼룩·황변 미지정) = item I_DRESS_SHIRT (일반 세탁·관리), NOT S_SHIRT_YELLOW.
버블티/밀크티/타피오카 = S_BUBBLE_TEA.
버터 = S_BUTTER. 구두약 = S_SHOE_POLISH (not shoe item alone).
우레탄·비닐·샤워 커튼 = I_CURTAIN_URETHANE. 일반 커튼 세탁 = I_CURTAIN_FABRIC.
구스/거위/다운 이불 = I_DUVET_GOOSE. 솜이불/폴리이불 = I_DUVET_COTTON.
침대 시트 = I_BED_SHEET. 수건/타월 = I_TOWEL. 아기옷 = I_BABY_WEAR. 수영복 = I_SWIMWEAR.
담배냄새 = I_ODOR_SMOKE. 선크림 = S_SUNSCREEN. 마스카라 = S_MASCARA. 타르 = S_TAR. 염색약 = S_HAIR_DYE.
케어라벨/세탁표시 = I_CARE_LABEL. 드라이 vs 물세탁 = I_DRY_VS_WET. 접수/체크인 스크립트 = I_INTAKE_SCRIPT.
경수/수돗물 = I_WATER_HARDNESS. 세탁기·건조기 코스 = I_MACHINE_PROFILE.
모자/캡 세탁(비골프) = I_HAT_CAP. 골프모자 = I_GOLF_HAT.
If the user names a specific stain, intent MUST be "treatment" (not mystery).

Group IDs: G1=protein, G2=oil, G3=tannin, G4=dye, G5=complex

Language detection:
- vi: Vietnamese words (vet, giat, ao, quan, chat, tay, nuoc, lua, etc.)
- ko: Korean characters
- en: English otherwise

Common stain names:
- VI: vet dau, vet mau, vet ca phe, vet nuoc tuong, nuoc mam, co, muc, gi set, moc, kim chi, ketchup, lo mau
- KO: 기름, 혈액, 커피, 간장, 액젓, 느억맘, 잔디, 잉크, 녹, 곰팡이, 김치, 케첩, 마요, 목때, 이염, 와이셔츠, 립스틱, 화장품, 파운데이션
- EN: oil, blood, coffee, soy sauce, fish sauce, grass, ink, rust, mold, kimchi, ketchup, mayo, collar, dye transfer, lipstick, makeup, foundation
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
    # Caller (graphrag_engine) may override lang via Hangul detection


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
