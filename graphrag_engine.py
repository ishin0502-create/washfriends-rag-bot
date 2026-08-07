"""
graphrag_engine.py
Wash Friends Vietnam — Neo4j GraphRAG Pipeline

Flow:
  user_message
    → entity_extractor  (GPT-4o-mini: entity extraction)
    → query_router      (select Cypher query)
    → neo4j_query       (fetch graph context)
    → llm_responder     (GPT-4o-mini: Vietnamese answer from graph data)
    → formatted_response

Aligned with /admin/seed schema in main.py:
  Stain {id, name, name_vi, tip, urgency, contains_*}, StainGroup G1-G5,
  Chemical {code, name_vi, role}, Fabric, ForceLevel, ClimateRule CR1-CR4,
  relationships: BELONGS_TO, USES_CHEMICAL, REQUIRES_FORCE, CAUTION_ON, NEVER_USE, NEVER_MIX_WITH
"""

import os
import json
import re
import unicodedata
from datetime import datetime, timezone, timedelta
from typing import Optional

from neo4j import GraphDatabase, Driver
from openai import OpenAI

from entity_extractor import extract_entities
from reply_lang import (
    detect_reply_lang,
    reply_language_leaks,
    retry_addon,
    system_prompt_for,
)
from response_cache import (
    lookup as cache_lookup,
    store as cache_store,
    build_context_key,
    question_for_cache,
)

# ─── Clients ─────────────────────────────────────────────────────────────────

_neo4j: Optional[Driver] = None
_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))

def _get_driver() -> Driver:
    global _neo4j
    if _neo4j is None:
        _neo4j = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        )
    return _neo4j

def close_driver():
    global _neo4j
    if _neo4j:
        _neo4j.close()
        _neo4j = None


# ─── Vietnam time helpers ─────────────────────────────────────────────────────

VN_TZ = timezone(timedelta(hours=7))

def _vn_month() -> int:
    return datetime.now(VN_TZ).month


def _normalize_text(value: str) -> str:
    """Lowercase + strip Vietnamese diacritics for fuzzy matching."""
    if not value:
        return ""
    text = unicodedata.normalize("NFD", value.lower().strip())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    return re.sub(r"\s+", " ", text)


# ─── Cypher queries (seed-schema aligned) ─────────────────────────────────────

Q_FULL_CONTEXT = """
MATCH (s:Stain)
WHERE ($stain_id <> '' AND s.id = $stain_id)
   OR ($stain_input <> '' AND toLower(coalesce(s.name_vi, '')) CONTAINS toLower($stain_input))
   OR ($stain_input <> '' AND toLower(coalesce(s.name, '')) CONTAINS toLower($stain_input))
   OR ($stain_input <> '' AND toLower(coalesce(s.id, '')) CONTAINS toLower($stain_input))
WITH s LIMIT 1
OPTIONAL MATCH (s)-[:BELONGS_TO]->(g:StainGroup)
OPTIONAL MATCH (f:Fabric)
  WHERE $fabric_input <> '' AND (
       toLower(coalesce(f.name_vi, '')) CONTAINS toLower($fabric_input)
    OR toLower(coalesce(f.name, '')) CONTAINS toLower($fabric_input)
    OR toLower(coalesce(f.id, '')) CONTAINS toLower($fabric_input)
  )
WITH s, g, f LIMIT 1
OPTIONAL MATCH (s)-[:USES_CHEMICAL]->(chem:Chemical)
OPTIONAL MATCH (s)-[:REQUIRES_FORCE]->(force:ForceLevel)
OPTIONAL MATCH (s)-[:CAUTION_ON]->(caution_fabric:Fabric)
OPTIONAL MATCH (f)-[:NEVER_USE]->(blocked:Chemical)
OPTIONAL MATCH (chem)-[:NEVER_MIX_WITH]->(dangerous:Chemical)
OPTIONAL MATCH (cr:ClimateRule)
  WHERE cr.id STARTS WITH 'CR'
OPTIONAL MATCH (s)-[:USES_TOOL]->(tool:Tool)
RETURN
  s {
    .id, .name, .name_vi, .name_ko, .tip, .urgency,
    .contains_protein, .contains_tannin, .contains_oil, .contains_dye,
    .water_spreads, .precheck_vi, .motion_vi, .water_temp_vi, .aftercare_vi,
    .why_vi, .fresh_path_vi, .dried_path_vi,
    .why_ko, .fresh_path_ko, .dried_path_ko,
    .force_metaphor_vi, .force_metaphor_ko,
    .sense_check_vi, .sense_check_ko,
    .success_rate_vi, .success_rate_ko,
    .refuse_when_vi, .refuse_when_ko,
    group: g.name_vi, group_id: g.id,
    group_care_order_vi: g.care_order_vi, group_care_order_ko: g.care_order_ko
  } AS stain_context,
  CASE WHEN f IS NULL THEN null ELSE f {
    .id, .name, .name_vi, .max_temp, .can_bleach, .can_oxygen, .enzyme_safe, .acid_safe,
    .dry_hint_vi, .iron_hint_vi
  } END AS fabric_context,
  COLLECT(DISTINCT chem {
    .code, .name, .name_vi, .name_ko, .role, .safe_on_wool, .safe_on_silk,
    .shop_name_vi, .buy_where_vi, .buy_where_ko, .alt1_vi, .alt2_vi, .alt3_vi,
    .example_brands_vi, .wf_supply, .when_use_vi, .dilution_vi, .dilution_ko
  }) AS chemicals,
  COLLECT(DISTINCT tool {
    .id, .name_vi, .name_ko, .use_for_vi, .use_for_ko, .use_for_en
  }) AS tools,
  [] AS washfriends_supply,
  COLLECT(DISTINCT force {
    .level, .name, .description
  }) AS force_levels,
  COLLECT(DISTINCT caution_fabric {
    .id, .name_vi, warning: 'Delicate fabric — avoid enzyme / harsh treatment'
  }) AS fabric_cautions,
  COLLECT(DISTINCT CASE WHEN blocked IS NOT NULL THEN {
    fabric: f.name_vi, chemical: blocked.code, chemical_name_vi: blocked.name_vi
  } END) AS never_use_on_fabric,
  COLLECT(DISTINCT CASE WHEN dangerous IS NOT NULL THEN {
    chemical: chem.code, mix_with: dangerous.code,
    danger_vi: 'KHONG BAO GIO TRON — co the sinh khi doc'
  } END) AS never_mix_alerts,
  COLLECT(DISTINCT cr {.id, .region, .rule}) AS climate_context
"""

Q_STAIN_FALLBACK = """
MATCH (s:Stain)
OPTIONAL MATCH (s)-[:BELONGS_TO]->(g:StainGroup)
RETURN s.id AS id, s.name_vi AS name_vi, s.name AS name_en,
       s.tip AS tip, g.name_vi AS group_vi,
       s.contains_protein AS contains_protein,
       s.contains_tannin AS contains_tannin,
       s.contains_oil AS contains_oil,
       s.contains_dye AS contains_dye
ORDER BY s.name_vi
"""

Q_ITEM_CONTEXT = """
MATCH (i:Item {id: $item_id})
OPTIONAL MATCH (i)-[:MADE_OF]->(f:Fabric)
OPTIONAL MATCH (i)-[:USES_CHEMICAL]->(chem:Chemical)
OPTIONAL MATCH (i)-[:USES_TOOL]->(tool:Tool)
OPTIONAL MATCH (f)-[:NEVER_USE]->(blocked:Chemical)
RETURN
  i {
    .id, .name, .name_vi, .name_ko,
    .precheck_vi, .why_vi, .fresh_path_vi, .dried_path_vi,
    .motion_vi, .water_temp_vi, .aftercare_vi, .fabric_id,
    .precheck_ko, .why_ko, .fresh_path_ko, .dried_path_ko,
    .motion_ko, .water_temp_ko, .aftercare_ko,
    .sense_check_ko, .success_rate_ko, .refuse_when_ko
  } AS item_context,
  CASE WHEN f IS NULL THEN null ELSE f {
    .id, .name, .name_vi, .max_temp, .can_bleach, .can_oxygen, .enzyme_safe, .acid_safe,
    .dry_hint_vi, .iron_hint_vi
  } END AS fabric_context,
  COLLECT(DISTINCT chem {
    .code, .name, .name_vi, .name_ko, .role, .safe_on_wool, .safe_on_silk,
    .shop_name_vi, .buy_where_vi, .buy_where_ko, .alt1_vi, .alt2_vi, .alt3_vi,
    .example_brands_vi, .wf_supply, .when_use_vi, .dilution_vi, .dilution_ko
  }) AS chemicals,
  COLLECT(DISTINCT tool {
    .id, .name_vi, .name_ko, .use_for_vi, .use_for_ko, .use_for_en
  }) AS tools,
  [] AS washfriends_supply,
  COLLECT(DISTINCT CASE WHEN blocked IS NOT NULL THEN {
    fabric: f.name_vi, chemical: blocked.code, chemical_name_vi: blocked.name_vi
  } END) AS never_use_on_fabric
"""

_ITEM_FABRIC_TOKEN = {
    "I_LEATHER_GARMENT": "leather",
    "I_LEATHER_BAG": "leather",
    "I_LEATHER_SHOE": "leather",
    "I_GLOVE_LEATHER": "leather",
    "I_SUEDE_GARMENT": "suede",
    "I_SUEDE_BAG": "suede",
    "I_SUEDE_SHOE": "suede",
    "I_SNEAKER": "polyester",
    "I_RUNNING_MESH": "polyester",
    "I_SNEAKER_WHITE": "polyester",
    "I_SHOE_LACES": "cotton",
    "I_GORETEX": "polyester",
    "I_DOWN_JACKET": "polyester",
    "I_SUIT": "wool",
    "I_SUIT_SUMMER": "linen",
    "I_NECKTIE": "silk",
    "I_AO_DAI": "silk",
    "I_HANBOK": "silk",
    "I_GOLF_WEAR": "polyester",
    "I_GOLF_SHOE": "polyester",
    "I_GOLF_HAT": "polyester",
    "I_GOLF_GLOVE_LEATHER": "leather",
    "I_GOLF_GLOVE_SYNTH": "polyester",
    "I_FUR_REAL": "fur",
    "I_FUR_FAUX": "polyester",
    "I_HIKING_SHOE": "polyester",
    "I_DENIM": "denim",
    "I_COLOR_FADE": "cotton",
    "I_WHITE_FADE": "cotton",
    "I_DRESS_SHIRT": "cotton",
    "I_HAT_CAP": "polyester",
    "I_CURTAIN_FABRIC": "polyester",
    "I_CURTAIN_URETHANE": "polyester",
    "I_DUVET_GOOSE": "cotton",
    "I_DUVET_COTTON": "cotton",
    "I_BED_SHEET": "cotton",
    "I_TOWEL": "cotton",
    "I_BABY_WEAR": "cotton",
    "I_SWIMWEAR": "polyester",
    "I_ODOR_SMOKE": "cotton",
    "I_CARE_LABEL": "cotton",
    "I_DRY_VS_WET": "cotton",
    "I_INTAKE_SCRIPT": "cotton",
    "I_WATER_HARDNESS": "cotton",
    "I_MACHINE_PROFILE": "cotton",
}
Q_RESCUE = """
MATCH (s:Stain)
WHERE s.id = $stain_id
   OR toLower(coalesce(s.name_vi, '')) CONTAINS toLower($stain_input)
   OR toLower(coalesce(s.name, '')) CONTAINS toLower($stain_input)
WITH s LIMIT 1
OPTIONAL MATCH (s)-[:USES_CHEMICAL]->(chem:Chemical)
RETURN s.name_vi AS stain_vi, s.tip AS tip, s.urgency AS urgency,
  COLLECT(DISTINCT chem {
    .code, .name_vi, .role, .shop_name_vi, .buy_where_vi, .alt1_vi, .alt2_vi, .alt3_vi, .wf_supply
  }) AS chemicals,
  CASE $attempt_number
    WHEN 1 THEN 'Thu lai: ngam enzyme/giấm them 20-30 phut, khong dung nhiet cao.'
    WHEN 2 THEN 'Phuong an C: chuyen sang oxy bleach (B1) neu vai cho phep, hoac thong bao khach.'
    ELSE 'Vet co the vin vien — thong bao khach va de xuat boi thuong neu can.'
  END AS recommended_rescue
"""

Q_PRICE = """
MATCH (s:Stain)
WHERE s.id = $stain_id
   OR toLower(coalesce(s.name_vi, '')) CONTAINS toLower($stain_input)
   OR toLower(coalesce(s.name, '')) CONTAINS toLower($stain_input)
WITH s LIMIT 1
OPTIONAL MATCH (f:Fabric)
  WHERE $fabric_input <> '' AND (
       toLower(coalesce(f.name_vi, '')) CONTAINS toLower($fabric_input)
    OR toLower(coalesce(f.name, '')) CONTAINS toLower($fabric_input)
  )
WITH s, f LIMIT 1
RETURN s.name_vi AS name_vi, s.urgency AS urgency, s.tip AS tip,
  CASE
    WHEN s.contains_dye = true OR s.contains_oil = true THEN '30.000 - 80.000 VND'
    WHEN s.contains_protein = true THEN '15.000 - 40.000 VND'
    ELSE '10.000 - 30.000 VND'
  END AS suggested_price_range,
  CASE WHEN f IS NULL THEN null ELSE f.name_vi END AS fabric_vi,
  CASE WHEN f IS NOT NULL AND f.enzyme_safe = false
       THEN 'Vai mong manh — bao khach truoc, khong dung enzyme manh'
       ELSE null END AS fabric_warning
"""

Q_MYSTERY_COLOR = """
MATCH (s:Stain)-[:BELONGS_TO]->(g:StainGroup)
WHERE
  CASE $stain_color
    WHEN 'red'    THEN s.contains_protein = true OR s.contains_tannin = true
    WHEN 'yellow' THEN s.contains_protein = true OR s.contains_oil = true OR s.contains_dye = true
    WHEN 'brown'  THEN s.contains_tannin = true OR s.contains_oil = true
    WHEN 'black'  THEN s.contains_dye = true OR s.contains_oil = true
    WHEN 'blue'   THEN s.contains_dye = true
    WHEN 'green'  THEN s.contains_tannin = true OR s.id = 'S_GRASS'
    WHEN 'white'  THEN s.contains_oil = true OR s.contains_protein = true
    ELSE true
  END
RETURN s.name_vi AS name_vi, s.name AS name_en, s.tip AS tip,
       g.name_vi AS group_vi, s.urgency AS urgency,
       s.contains_oil AS contains_oil, s.contains_protein AS contains_protein,
       s.contains_tannin AS contains_tannin, s.contains_dye AS contains_dye
ORDER BY s.urgency DESC LIMIT 8
"""

Q_HARDEST = """
MATCH (s:Stain)-[:BELONGS_TO]->(g:StainGroup)
WHERE s.contains_dye = true OR s.urgency = 'immediate'
   OR s.id IN ['S_INK_PERMANENT','S_ENGINE_OIL','S_SWEAT_YELLOW','S_CURRY','S_FISH_SAUCE']
RETURN s.name_vi AS name_vi, s.name AS name_en, s.tip AS tip,
       s.urgency AS urgency, g.name_vi AS group_vi
ORDER BY s.urgency DESC, s.name_vi ASC
LIMIT 12
"""

Q_DAILY = """
MATCH (c1:Chemical)-[:NEVER_MIX_WITH]->(c2:Chemical)
WITH COLLECT({mix: c1.code + ' + ' + c2.code,
              danger_vi: 'KHONG BAO GIO TRON — khi doc'}) AS never_mix_rules
MATCH (cr:ClimateRule)
WHERE cr.id IN ['CR1','CR3','CR4']
   OR ($month IN [5,6,7,8,9,10,11] AND cr.id = 'CR3')
RETURN never_mix_rules, COLLECT(cr {.id, .region, .rule}) AS climate_rules
"""

Q_CHEM_SAFETY = """
MATCH (c:Chemical)
WHERE toUpper(c.code) = toUpper($chem_code)
   OR toLower(coalesce(c.name_vi, '')) CONTAINS toLower($chem_code)
   OR toLower(coalesce(c.name, '')) CONTAINS toLower($chem_code)
WITH c LIMIT 1
OPTIONAL MATCH (f_safe:Fabric)
  WHERE (c.safe_on_wool = true AND f_safe.id IN ['F3'])
     OR (c.safe_on_silk = true AND f_safe.id IN ['F4'])
     OR (c.safe_on_wool = true OR c.safe_on_silk = true)
OPTIONAL MATCH (f_dmg:Fabric)-[:NEVER_USE]->(c)
OPTIONAL MATCH (c)-[:NEVER_MIX_WITH]->(c2:Chemical)
RETURN c {.code, .name, .name_vi, .role, .safe_on_wool, .safe_on_silk},
  COLLECT(DISTINCT f_safe.name_vi) AS safe_for_fabrics,
  COLLECT(DISTINCT {fabric: f_dmg.name_vi, reason: 'Fabric never-use rule'}) AS damages,
  COLLECT(DISTINCT {chemical: c2.code, danger_vi: 'Never mix'}) AS never_mix
"""


# ─── Query runner ─────────────────────────────────────────────────────────────

def _run_query(cypher: str, params: dict) -> list[dict]:
    """Execute Cypher, return list of record dicts. Returns [] on error."""
    driver = _get_driver()
    try:
        with driver.session() as session:
            result = session.run(cypher, params)
            return [dict(record) for record in result]
    except Exception as e:
        print(f"[NEO4J ERROR] {e}")
        return []


def _score_stain_row(row: dict, stain_norm: str) -> int:
    if not stain_norm:
        return 0
    blob = _normalize_text(
        " ".join(
            str(row.get(k) or "")
            for k in ("name_vi", "name_en", "name", "id", "tip")
        )
    )
    score = 0
    if stain_norm in blob:
        score += 10
    for token in stain_norm.split():
        if len(token) >= 3 and token in blob:
            score += 3
    return score


def _fallback_search(stain_input: str) -> list[dict]:
    stain_norm = _normalize_text(stain_input)
    if not stain_norm:
        return []
    rows = _run_query(Q_STAIN_FALLBACK, {})
    ranked = sorted(
        (( _score_stain_row(r, stain_norm), r) for r in rows),
        key=lambda x: x[0],
        reverse=True,
    )
    return [r for score, r in ranked if score > 0][:5]


# ─── Query router ─────────────────────────────────────────────────────────────

def _fetch_graph_context(entities: dict) -> dict:
    intent  = entities.get("intent", "treatment")
    month   = _vn_month()
    context = {"intent": intent, "entities": entities}

    stain_raw = entities.get("stain_type") or entities.get("stain_id") or ""
    stain_input = _normalize_text(stain_raw)
    fabric_input = _normalize_text(entities.get("fabric_type") or "")
    stain_id = entities.get("stain_id") or ""
    raw_msg = _normalize_text(entities.get("_raw") or "")
    raw_original = entities.get("_raw") or ""

    # Raw-message fabric wins over a wrong extractor guess (e.g. 비단 / lụa)
    inferred_fabric = _infer_fabric_from_text(raw_original)
    if inferred_fabric:
        fabric_input = inferred_fabric
        entities["fabric_type"] = inferred_fabric

    item_id = entities.get("item_id") or _infer_item_from_text(raw_original)
    if item_id:
        entities["item_id"] = item_id
        if not fabric_input:
            fabric_input = _ITEM_FABRIC_TOKEN.get(item_id, "")
            if fabric_input:
                entities["fabric_type"] = fabric_input
        # Item-care questions must not early-exit as price/safety/mystery with empty graph
        if intent in ("price", "safety", "mystery", "browse", "rescue", "hardest", "daily"):
            intent = "treatment"
            context["intent"] = "treatment"
            entities["intent"] = "treatment"

    garment_color = entities.get("garment_color") or _infer_garment_color(raw_original)
    if garment_color:
        entities["garment_color"] = garment_color

    # Prefer franchise phrasing in the raw message over a wrong LLM entity guess
    _ALIASES = (
        ("laterite", "dat do laterite"),
        ("dat do laterite", "dat do laterite"),
        ("dat do", "dat do laterite"),
        ("dau nhot xe may", "dau nhot xe may"),
        ("dau nhot", "dau nhot xe may"),
        ("nam moc", "nam moc"),
        ("ri set", "ri set"),
        ("kim chi", "kim chi"),
        ("kimchi", "kim chi"),
        ("ruou vang do", "ruou vang do"),
        ("ruou vang", "ruou vang do"),
        ("red wine", "ruou vang do"),
        ("wine", "ruou vang do"),
    )
    alias_hit = None
    haystack = f"{raw_msg} {stain_input}".strip()
    for key, canon in _ALIASES:
        if key in haystack:
            alias_hit = canon
            break
    if alias_hit:
        stain_input = alias_hit
        intent = "treatment"
        context["intent"] = "treatment"
        if alias_hit == "dat do laterite":
            stain_id = "S_LATERITE"
        elif alias_hit == "dau nhot xe may":
            stain_id = "S_MOTORBIKE_OIL"
        elif alias_hit == "nam moc":
            stain_id = "S_MILDEW"
        elif alias_hit == "ri set":
            stain_id = "S_RUST"
        elif alias_hit == "kim chi":
            stain_id = "S_KIMCHI"
        elif alias_hit == "ruou vang do":
            stain_id = "S_RED_WINE"
    elif not stain_input and raw_msg and not (item_id and not stain_id):
        # Item-only care (e.g. I_DRESS_SHIRT): do not fuzzy raw text into a stain
        stain_input = raw_msg

    if intent == "daily":
        rows = _run_query(Q_DAILY, {"month": month})
        context["graph"] = rows[0] if rows else {}
        context["query_type"] = "daily"
        return context

    if intent == "hardest":
        rows = _run_query(Q_HARDEST, {})
        context["graph"] = rows
        context["query_type"] = "hardest"
        return context

    if intent == "safety":
        chem_code = stain_id or stain_input or ""
        rows = _run_query(Q_CHEM_SAFETY, {"chem_code": chem_code})
        context["graph"] = rows[0] if rows else {}
        context["query_type"] = "safety"
        return context

    if intent == "mystery":
        rows = _run_query(Q_MYSTERY_COLOR, {
            "stain_color": entities.get("stain_color") or "none",
        })
        context["graph"] = rows
        context["query_type"] = "mystery"
        return context

    if intent == "rescue":
        rows = _run_query(Q_RESCUE, {
            "stain_id": stain_id,
            "stain_input": stain_input,
            "attempt_number": entities.get("attempt_number") or 1,
        })
        context["graph"] = rows[0] if rows else {}
        context["query_type"] = "rescue"
        return context

    if intent == "price":
        rows = _run_query(Q_PRICE, {
            "stain_id": stain_id,
            "stain_input": stain_input,
            "fabric_input": fabric_input,
        })
        context["graph"] = rows[0] if rows else {}
        context["query_type"] = "price"
        return context

    # Item-only care (no stain): skip stain lookup — empty stain_input used to
    # match ALL stains via Cypher CONTAINS '' (LIMIT 1 → arbitrary e.g. blood).
    if item_id and not stain_id and not stain_input:
        context["graph"] = []
        context["query_type"] = "empty"
        item_rows = _run_query(Q_ITEM_CONTEXT, {"item_id": item_id})
        if item_rows:
            context = _merge_item_into_context(context, item_rows[0])
            if isinstance(context.get("graph"), dict):
                g0 = dict(context["graph"])
                if entities.get("garment_color"):
                    g0["garment_color"] = entities["garment_color"]
                context["graph"] = _refine_tools_for_context(
                    _apply_delicate_s1_fallback(
                        _apply_fabric_chem_safety(g0)
                    ),
                    entities,
                )
        return context

    # Default: full treatment protocol
    rows = _run_query(Q_FULL_CONTEXT, {
        "stain_id": stain_id or "",
        "stain_input": stain_input,
        "fabric_input": fabric_input,
    })

    if not rows or rows[0].get("stain_context") is None:
        fallback = _fallback_search(stain_input or stain_id or raw_msg)
        if fallback:
            best = fallback[0]
            rows = _run_query(Q_FULL_CONTEXT, {
                "stain_id": best.get("id") or "",
                "stain_input": best.get("name_vi") or best.get("id") or stain_input,
                "fabric_input": fabric_input,
            })
            if rows and rows[0].get("stain_context") is not None:
                context["graph"] = rows[0]
                context["query_type"] = "full_context_via_fallback"
            else:
                context["graph"] = fallback
                context["query_type"] = "name_fallback"
        else:
            context["graph"] = []
            context["query_type"] = "empty"
    else:
        context["graph"] = rows[0]
        context["query_type"] = "full_context"

    if isinstance(context.get("graph"), dict):
        g0 = dict(context["graph"])
        if entities.get("garment_color"):
            g0["garment_color"] = entities["garment_color"]
        context["graph"] = _apply_delicate_s1_fallback(
            _apply_fabric_chem_safety(g0)
        )

    # Item care (shoes/bags/gore-tex/down/leather) — same 1)-6) fields as stains
    item_id = entities.get("item_id")
    if item_id:
        item_rows = _run_query(Q_ITEM_CONTEXT, {"item_id": item_id})
        if item_rows:
            context = _merge_item_into_context(context, item_rows[0])
            if isinstance(context.get("graph"), dict):
                g1 = dict(context["graph"])
                if entities.get("garment_color"):
                    g1["garment_color"] = entities["garment_color"]
                context["graph"] = _apply_delicate_s1_fallback(
                    _apply_fabric_chem_safety(g1)
                )

    if isinstance(context.get("graph"), dict):
        context["graph"] = _refine_tools_for_context(context["graph"], entities)

    return context


def _item_as_stain_shaped(item_graph: dict) -> dict:
    """Map Item fields onto stain_context so existing owner 1)-6) prompt stays unchanged."""
    ic = item_graph.get("item_context") or {}
    item_id = ic.get("id") or ""
    # No shop detergents as "restore" fillers; real fur / leather golf glove also pro-only
    no_shop_chem = item_id in {
        "I_FUR_REAL",
        "I_GOLF_GLOVE_LEATHER",
        "I_COLOR_FADE",
    }
    return {
        "stain_context": {
            "id": ic.get("id"),
            "name": ic.get("name"),
            "name_vi": ic.get("name_vi"),
            "name_ko": ic.get("name_ko"),
            "tip": ic.get("why_ko") or ic.get("why_vi"),
            "urgency": "care",
            "precheck_vi": ic.get("precheck_vi"),
            "why_vi": ic.get("why_vi"),
            "fresh_path_vi": ic.get("fresh_path_vi"),
            "dried_path_vi": ic.get("dried_path_vi"),
            "motion_vi": ic.get("motion_vi"),
            "water_temp_vi": ic.get("water_temp_vi"),
            "aftercare_vi": ic.get("aftercare_vi"),
            "precheck_ko": ic.get("precheck_ko"),
            "why_ko": ic.get("why_ko"),
            "fresh_path_ko": ic.get("fresh_path_ko"),
            "dried_path_ko": ic.get("dried_path_ko"),
            "motion_ko": ic.get("motion_ko"),
            "water_temp_ko": ic.get("water_temp_ko"),
            "aftercare_ko": ic.get("aftercare_ko"),
            "group": "item_care",
        },
        "fabric_context": item_graph.get("fabric_context"),
        "chemicals": [] if no_shop_chem else (item_graph.get("chemicals") or []),
        "tools": list(_COLOR_FADE_TOOLS) if item_id == "I_COLOR_FADE" else (item_graph.get("tools") or []),
        "washfriends_supply": [],
        "force_levels": [],
        "fabric_cautions": [],
        "never_use_on_fabric": item_graph.get("never_use_on_fabric") or [],
        "never_mix_alerts": [],
        "climate_context": [],
        "item_context": ic,
        "empty_tools_ok": False,
        "empty_chems_ok": no_shop_chem,
        "color_fade_rules": item_id == "I_COLOR_FADE",
    }


def _merge_item_into_context(context: dict, item_graph: dict) -> dict:
    g = context.get("graph")
    has_stain = isinstance(g, dict) and g.get("stain_context") is not None
    if not has_stain:
        context["graph"] = _item_as_stain_shaped(item_graph)
        context["query_type"] = "item_care"
        return context
    g = dict(g)
    ic = item_graph.get("item_context") or {}
    g["item_context"] = ic
    # Dress-shirt routine care must NOT overwrite real stain SOPs (collar/yellow/etc.)
    if ic.get("id") == "I_DRESS_SHIRT":
        if not g.get("fabric_context") and item_graph.get("fabric_context"):
            g["fabric_context"] = item_graph["fabric_context"]
        context["graph"] = g
        return context
    if not g.get("fabric_context") and item_graph.get("fabric_context"):
        g["fabric_context"] = item_graph["fabric_context"]
    # Overlay item care SOP onto stain fields so 1)-6) follows the garment, not a generic stain
    sc = dict(g.get("stain_context") or {})
    for key in (
        "precheck_vi", "why_vi", "fresh_path_vi", "dried_path_vi",
        "motion_vi", "water_temp_vi", "aftercare_vi",
        "precheck_ko", "why_ko", "fresh_path_ko", "dried_path_ko",
        "motion_ko", "water_temp_ko", "aftercare_ko",
        "sense_check_ko", "success_rate_ko", "refuse_when_ko",
    ):
        if ic.get(key):
            sc[key] = ic[key]
    if ic.get("why_ko"):
        sc["tip"] = ic.get("why_ko")
    elif ic.get("why_vi"):
        sc["tip"] = ic.get("why_vi")
    # Keep stain name/id for recognition; item name_ko for garment identity
    if ic.get("name_ko"):
        sc["item_name_ko"] = ic.get("name_ko")
    if ic.get("name_vi"):
        sc["item_name_vi"] = ic.get("name_vi")
    g["stain_context"] = sc
    # Prefer item tools/chems for specialty garments (necktie/suit/silk etc.)
    if item_graph.get("tools") is not None:
        g["tools"] = (
            list(_COLOR_FADE_TOOLS)
            if ic.get("id") == "I_COLOR_FADE"
            else (item_graph.get("tools") or [])
        )
    if ic.get("id") in {"I_FUR_REAL", "I_GOLF_GLOVE_LEATHER", "I_COLOR_FADE"}:
        g["chemicals"] = []
        g["washfriends_supply"] = []
        g["empty_chems_ok"] = True
        if ic.get("id") == "I_COLOR_FADE":
            g["color_fade_rules"] = True
            g["empty_tools_ok"] = False
    elif item_graph.get("chemicals") is not None:
        g["chemicals"] = item_graph.get("chemicals")
        g["washfriends_supply"] = []
    if item_graph.get("never_use_on_fabric"):
        g["never_use_on_fabric"] = item_graph.get("never_use_on_fabric")
    context["graph"] = g
    return context


def _infer_garment_color(text: str) -> str:
    """white | black | colored | '' — garment/stain-host color from owner message."""
    if not text:
        return ""
    raw = text
    t = _normalize_text(text)
    if any(k in raw for k in ("흰", "하얀", "화이트", "백색")) or "trang" in t or "white" in t:
        return "white"
    if any(k in raw for k in ("검정", "검은", "블랙")) or "den " in f" {t} " or t.endswith(" den") or "black" in t:
        return "black"
    if any(
        k in raw
        for k in ("유색", "컬러", "색깔", "색상", "빨강", "파랑", "노랑", "초록", "보라", "핑크", "남색")
    ) or any(
        k in t
        for k in ("mau dam", "colored", "colour", "do ", "xanh", "vang", "tim", "hong", "nau ")
    ):
        return "colored"
    return ""


def _refine_tools_for_context(graph: dict, entities: Optional[dict] = None) -> dict:
    """Match tools to garment/fabric/color: drop soak/hard brushes on silk/tie; keep how-to ids."""
    if not isinstance(graph, dict):
        return graph
    tools = [t for t in (graph.get("tools") or []) if t]
    if not tools:
        return graph

    entities = entities or {}
    ic = graph.get("item_context") or {}
    item_id = ic.get("id") or entities.get("item_id") or ""
    fabric = graph.get("fabric_context") or {}
    fid = str(fabric.get("id") or "").upper()
    fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''}".lower()
    is_silk = fid == "F4" or "silk" in fname or "lua" in fname
    is_wool = fid == "F3" or "wool" in fname or " len" in f" {fname}"
    delicate = is_silk or is_wool or item_id in {
        "I_NECKTIE", "I_SUIT", "I_AO_DAI", "I_HANBOK", "I_FUR_REAL", "I_FUR_FAUX",
    }

    by_id = {str(t.get("id") or ""): t for t in tools if t.get("id")}
    drop = set()

    if delicate:
        drop |= {"T_BRUSH_HARD", "T_BRUSH_SHOE"}
        if "T_BRUSH_SOFT" in by_id:
            drop.add("T_BRUSH_SOFT")
        if item_id in {"I_NECKTIE", "I_SUIT", "I_AO_DAI", "I_HANBOK"}:
            drop |= {"T_SOAK_BIN", "T_TIMER", "T_MESH_BAG"}
        if item_id == "I_NECKTIE":
            # Tie: blot + ultra + steam only; no flood spray kit
            drop.add("T_SPRAY")
            allow = {"T_CLOTH", "T_BRUSH_ULTRA", "T_STEAM_IRON"}
            for tid in list(by_id.keys()):
                if tid and tid not in allow:
                    drop.add(tid)

    garment_color = entities.get("garment_color") or graph.get("garment_color") or ""
    if garment_color and garment_color != "white":
        # Keep tools; color rules applied in chem filter + prompt note
        pass

    refined = [t for t in tools if str(t.get("id") or "") not in drop]
    # Ensure necktie always has cloth + ultra if specialty path emptied wrongly
    if item_id == "I_NECKTIE" and not any(str(t.get("id")) == "T_CLOTH" for t in refined):
        cloth = by_id.get("T_CLOTH")
        if cloth:
            refined.insert(0, cloth)
    out = dict(graph)
    out["tools"] = refined
    if garment_color:
        out["garment_color"] = garment_color
        if garment_color == "white":
            out["color_note_ko"] = "흰 옷: 산소표백(B1)은 원단 허용 시에만. 염소(락스)는 단백질·실크·울 금지."
            out["color_note_vi"] = "Do TRANG: B1 chi khi vai cho phep. Javel CAM tren protein/lua/len."
            out["color_note_en"] = "White: oxygen bleach only if fabric allows. No chlorine on protein/silk/wool."
        elif garment_color == "colored":
            out["color_note_ko"] = "유색: 염소·강력 표백 금지. 이염 주의 — 흰 천으로 전이 확인."
            out["color_note_vi"] = "Vai MAU: CAM Javel/tay manh. Theo doi lo mau tren khan trang."
            out["color_note_en"] = "Colored: no chlorine/harsh bleach. Watch dye transfer on white cloth."
        elif garment_color == "black":
            out["color_note_ko"] = "검정·진한 색: 표백 금지. 잔여 얼룩은 강광으로 확인(눈에 덜 띔)."
            out["color_note_vi"] = "Den/dam: CAM tay. Kiem vet bang anh sang manh."
            out["color_note_en"] = "Black/dark: no bleach. Inspect residue under strong light."
    return _bind_tool_howto_to_protocol(out)


def _protocol_text_blob(graph: dict) -> str:
    chunks = []
    sc = graph.get("stain_context") or {}
    for k in (
        "fresh_path_ko", "fresh_path_vi", "dried_path_ko", "dried_path_vi",
        "why_ko", "why_vi", "tip", "precheck_vi", "precheck_ko",
    ):
        if sc.get(k):
            chunks.append(str(sc[k]))
    for c in graph.get("chemicals") or []:
        for k in ("dilution_ko", "dilution_vi", "when_use_vi", "name_ko", "name_vi", "shop_name_vi"):
            if c.get(k):
                chunks.append(str(c[k]))
    return "\n".join(chunks)


def _parse_minute_range(text: str):
    """Return (lo, hi) minutes from protocol/dilution text, or None."""
    if not text:
        return None
    ranges = []
    for m in re.finditer(
        r"(\d+)\s*[-–~到至]\s*(\d+)\s*(?:분|phút|phut|minutes?|mins?)",
        text,
        re.I,
    ):
        a, b = int(m.group(1)), int(m.group(2))
        if 1 <= a <= 600 and 1 <= b <= 600:
            ranges.append((min(a, b), max(a, b)))
    # Prefer soak-like windows first
    for pref in ((15, 45), (15, 60), (15, 30), (10, 30), (5, 10)):
        if pref in ranges:
            return pref
    if ranges:
        return ranges[0]
    singles = []
    for m in re.finditer(
        r"(?:ngam|담금|soak|hen\s*gio|타이머)[^\d]{0,20}(\d+)\s*(?:분|phút|phut|min)",
        text,
        re.I,
    ):
        n = int(m.group(1))
        if 1 <= n <= 600:
            singles.append(n)
    if not singles:
        for m in re.finditer(r"(\d+)\s*(?:분|phút|phut)\b", text, re.I):
            n = int(m.group(1))
            if 5 <= n <= 120:
                singles.append(n)
    if singles:
        n = singles[0]
        return (n, n)
    return None


def _chem_owner_name(c: dict, lang: str) -> str:
    if lang == "ko":
        return str(c.get("name_ko") or c.get("shop_name_vi") or c.get("name_vi") or c.get("name") or "").strip()
    if lang == "en":
        return str(c.get("name") or c.get("name_ko") or c.get("name_vi") or "").strip()
    return str(c.get("shop_name_vi") or c.get("name_vi") or c.get("name") or "").strip()


def _pick_spray_chem(chems: list) -> Optional[dict]:
    if not chems:
        return None
    by_code = {str(c.get("code") or "").upper(): c for c in chems if c}
    for code in ("A3", "D2", "A1", "A4", "B1", "S1"):
        if code in by_code:
            return by_code[code]
    for c in chems:
        dil = f"{c.get('dilution_ko') or ''} {c.get('dilution_vi') or ''}"
        if re.search(r"\d+\s*[:：]\s*\d+|pha|희석|1-2|1–2", dil, re.I):
            return c
    return chems[0]


def _bind_tool_howto_to_protocol(graph: dict) -> dict:
    """Rewrite spray/soak/timer how-to with THIS stain's minutes + dilution (education-grade)."""
    if not isinstance(graph, dict):
        return graph
    tools = [dict(t) for t in (graph.get("tools") or []) if t]
    if not tools:
        return graph

    chems = [c for c in (graph.get("chemicals") or []) if c]
    blob = _protocol_text_blob(graph)
    soak = _parse_minute_range(blob) or (15, 45)
    lo, hi = soak
    min_ko = f"{lo}분" if lo == hi else f"{lo}–{hi}분"
    min_vi = f"{lo} phut" if lo == hi else f"{lo}-{hi} phut"
    min_en = f"{lo} min" if lo == hi else f"{lo}-{hi} min"

    spray = _pick_spray_chem(chems)
    spray_name_ko = _chem_owner_name(spray, "ko") if spray else "희석 약품"
    spray_name_vi = _chem_owner_name(spray, "vi") if spray else "dung dich pha"
    spray_name_en = _chem_owner_name(spray, "en") if spray else "diluted chemical"
    dil_ko = (spray.get("dilution_ko") if spray else None) or "병·경로 희석"
    dil_vi = (spray.get("dilution_vi") if spray else None) or "pha theo dilution"
    dil_en = dil_ko if spray and spray.get("dilution_ko") else "per dilution on label/path"

    bound = []
    for t in tools:
        tid = str(t.get("id") or "")
        if tid == "T_SPRAY":
            t["name_ko"] = "분무기(약마다 따로·겉에 이름·비율 쓰기)"
            t["name_vi"] = "Bình xịt (mỗi hóa chất 1 bình + ghi tên/tỷ lệ)"
            t["use_for_ko"] = (
                f"이 얼룩용: (4)약품의「{spray_name_ko}」을 「{dil_ko}」로 타서, "
                f"다른 약이 안 들어 있는 분무기에만 넣는다. 병 겉에 「{spray_name_ko} / {dil_ko}」라고 펜으로 적는다"
                f"(섞이면 위험하거나 효과가 없어짐). 얼룩에 1–2번만 뿌리고 흠뻑 적시지 말 것."
            )
            t["use_for_vi"] = (
                f"Cho vết này: pha 「{spray_name_vi}」 theo 「{dil_vi}」 vào bình RIÊNG (không trộn thuốc khác). "
                f"Viết lên bình 「{spray_name_vi} / {dil_vi}」. Xịt 1-2 phát — không ngập."
            )
            t["use_for_en"] = (
                f"For this stain: mix 「{spray_name_en}」 at 「{dil_en}」 in a dedicated bottle (no other chemical). "
                f"Write 「{spray_name_en} / {dil_en}」 on the bottle. Mist 1-2 sprays — do not soak."
            )
        elif tid == "T_TIMER":
            t["use_for_ko"] = (
                f"이 오염·약품 기준 처리 시간은 {min_ko}. 타이머/휴대폰 알람을 {min_ko}에 맞추고, "
                f"울리면 즉시 찬물로 헹군다. 감시 없이 밤새 담그지 말 것."
            )
            t["use_for_vi"] = (
                f"Thời gian xử lý cho vết này: {min_vi}. Bấm hẹn giờ {min_vi}; hết giờ → xả nước lạnh ngay. "
                f"Không để qua đêm khi không giám sát."
            )
            t["use_for_en"] = (
                f"Treatment time for this stain: {min_en}. Set a timer for {min_en}; when it rings, rinse cold immediately. "
                f"No overnight unattended soak."
            )
        elif tid == "T_SOAK_BIN":
            t["use_for_ko"] = (
                f"(4)약품 희석액을 통에 만들어 {min_ko}만 담근다. 통에 약 이름을 확인. "
                f"정장·넥타이·얇은 실크는 통담금 금지(해당 시)."
            )
            t["use_for_vi"] = (
                f"Pha dung dịch (4) vào chậu, ngâm đúng {min_vi}. Dán nhãn hóa chất. "
                f"CẤM ngâm suit/cà vạt/lụa mỏng nếu SOP cấm."
            )
            t["use_for_en"] = (
                f"Mix the (4) chemicals in a bin and soak only {min_en}. Label the chemical. "
                f"Do not full-soak suits/ties/sheer silk if SOP forbids."
            )
        bound.append(t)

    out = dict(graph)
    out["tools"] = bound
    out["protocol_minutes_ko"] = min_ko
    out["protocol_minutes_vi"] = min_vi
    out["spray_recipe_ko"] = f"{spray_name_ko} / {dil_ko}" if spray else ""
    out["spray_recipe_vi"] = f"{spray_name_vi} / {dil_vi}" if spray else ""
    return out


def _infer_item_from_text(text: str) -> str:
    """Detect franchise item types from KO/VI/EN — KB-backed Item ids only."""
    if not text:
        return ""
    raw = text
    t = _normalize_text(text)
    suede = any(k in raw for k in ("스웨이드", "누벅")) or "suede" in t or "nubuck" in t or "da lon" in t
    leather = any(k in raw for k in ("가죽",)) or "leather" in t or "ao da" in t or "giay da" in t or "tui da" in t
    bag = any(k in raw for k in ("가방", "지갑")) or "tui xach" in t or "tui da" in t or "handbag" in t or "vi da" in t
    shoe = any(k in raw for k in ("구두", "신발", "운동화", "스니커", "등산화", "골프화")) or "giay" in t or "shoe" in t or "sneaker" in t
    glove = any(k in raw for k in ("장갑",)) or "gang tay" in t or "glove" in t
    golf = "골프" in raw or "golf" in t
    fur = any(k in raw for k in ("모피", "퍼코트", "모피코트")) or "fur" in t or "ao long" in t or "long thu" in t
    faux = any(k in raw for k in ("인조", "페이크")) or "faux" in t or "synthetic fur" in t or "long gia" in t

    # Fur before leather (overlap on "fur trim")
    if fur and faux:
        return "I_FUR_FAUX"
    if fur:
        return "I_FUR_REAL"
    if faux and ("퍼" in raw or "fur" in t or "long" in t):
        return "I_FUR_FAUX"

    if suede and bag:
        return "I_SUEDE_BAG"
    if suede and shoe:
        return "I_SUEDE_SHOE"
    if suede:
        return "I_SUEDE_GARMENT"
    if leather and bag:
        return "I_LEATHER_BAG"
    if leather and shoe and not golf:
        return "I_LEATHER_SHOE"
    if leather and glove:
        return "I_GOLF_GLOVE_LEATHER" if golf else "I_GLOVE_LEATHER"
    if leather and not golf:
        return "I_LEATHER_GARMENT"

    # Necktie before suit (넥타이 must not become I_SUIT)
    if any(k in raw for k in ("넥타이", "넥 타이")) or "necktie" in t or "neck tie" in t or "ca vat" in t or "caravat" in t or "cavat" in t:
        return "I_NECKTIE"

    # Color fade / restore before generic denim
    fade = any(
        k in raw
        for k in (
            "색바램", "색 바램", "탈색", "색이 흐려", "색상이 흐려", "색상 흐려",
            "색이 바랬", "색이 바래", "흐려졌",
            "색빠짐", "물빠짐", "복원", "하얗게 닳", "표백 후",
        )
    ) or "phai mau" in t or "mat mau" in t or "phuc hoi mau" in t or "fade" in t or "decolor" in t
    white_fade = fade and (
        any(k in raw for k in ("흰", "화이트", "밝은", "표백"))
        or "trang" in t
        or "white" in t
    )
    if white_fade:
        return "I_WHITE_FADE"
    if fade:
        return "I_COLOR_FADE"
    if any(k in raw for k in ("청바지", "청자켓", "청치마", "데님")) or "denim" in t or "jean" in t or "quan jean" in t:
        return "I_DENIM"

    # Ops / decision cards before garment type
    if any(k in raw for k in ("케어라벨", "세탁표시", "세탁 기호", "케어 라벨", "세탁기호")) or "care label" in t or "ky hieu giat" in t or "washing symbol" in t:
        return "I_CARE_LABEL"
    if any(k in raw for k in ("드라이클리닝", "드라이 클리닝", "물세탁인가", "드라이인가", "드라이로")) or (
        ("dry clean" in t or "dry-clean" in t or "giat kho" in t) and any(k in raw for k in ("물세탁", "해야", "인가", "vs", "아니면"))
    ) or "dry vs wet" in t:
        return "I_DRY_VS_WET"
    if any(k in raw for k in ("접수", "체크인", "인수인계", "사진 동의", "견적 스크립트")) or "check-in" in t or "check in" in t or "tiep nhan" in t or "intake script" in t:
        return "I_INTAKE_SCRIPT"
    if any(k in raw for k in ("경수", "센물", "수돗물 경도", "물때")) or "hard water" in t or "nuoc cung" in t:
        return "I_WATER_HARDNESS"
    if any(k in raw for k in ("세탁기 코스", "세탁기 설정", "건조기", "탈수 코스")) or "washer" in t or "dryer setting" in t or "chuong trinh may" in t:
        return "I_MACHINE_PROFILE"

    # Traditional dress
    if "한복" in raw or "hanbok" in t:
        return "I_HANBOK"
    if "아오자이" in raw or "ao dai" in t or "aodai" in t:
        return "I_AO_DAI"

    # Suits
    if any(k in raw for k in ("린넨 정장", "여름 정장", "얇은 정장")) or "suit he" in t or "linen suit" in t or ("linen" in t and ("suit" in t or "정장" in raw)):
        return "I_SUIT_SUMMER"
    if any(k in raw for k in ("정장", "수트", "양복", "턱시도")) or "suit" in t or "vest" in t or "tuxedo" in t or "bo vest" in t:
        return "I_SUIT"

    # Golf kit
    if golf and glove:
        return "I_GOLF_GLOVE_LEATHER" if leather else "I_GOLF_GLOVE_SYNTH"
    if golf and (any(k in raw for k in ("모자", "캡")) or "mu " in t or "hat" in t or "cap" in t):
        return "I_GOLF_HAT"
    if golf and shoe:
        return "I_GOLF_SHOE"
    if golf:
        return "I_GOLF_WEAR"

    # Home textiles — specific before generic
    urethane_curtain = any(
        k in raw for k in ("우레탄", "비닐커튼", "비닐 커튼", "샤워커튼", "샤워 커튼", "PEVA", "PVC커튼")
    ) or "urethane" in t or "vinyl curtain" in t or "shower curtain" in t or "rem nhua" in t or "rem vinyl" in t
    if urethane_curtain or (
        ("커튼" in raw or "curtain" in t or "rem " in t) and any(k in raw for k in ("우레탄", "비닐", "코팅", "방수"))
    ):
        return "I_CURTAIN_URETHANE"
    if any(k in raw for k in ("커튼",)) or "curtain" in t or "rem cua" in t or "rem vai" in t:
        return "I_CURTAIN_FABRIC"
    if any(k in raw for k in ("구스이불", "거위털", "다운이불", "오리털이불")) or "goose" in t or "down duvet" in t or "chan long" in t:
        return "I_DUVET_GOOSE"
    if any(k in raw for k in ("솜이불", "폴리이불", "충전 이불")) or (
        "이불" in raw and any(k in raw for k in ("세탁", "빨래", "방법", "어떻게"))
        and not any(k in raw for k in ("구스", "거위", "다운", "오리털"))
    ) or "comforter" in t or "chan bong" in t:
        return "I_DUVET_COTTON"
    if any(k in raw for k in ("시트", "침대시트", "매트리스커버", "매트리스 커버")) or "ga giuong" in t or "bed sheet" in t or "fitted sheet" in t or "drap" in t:
        return "I_BED_SHEET"
    if any(k in raw for k in ("수건", "타월", "목욕타월")) or "khan tam" in t or "towel" in t:
        return "I_TOWEL"
    if any(k in raw for k in ("아기옷", "유아복", "신생아", "아기 옷")) or "do em be" in t or "baby wear" in t or "infant" in t:
        return "I_BABY_WEAR"
    if any(k in raw for k in ("수영복", "래시가드", "비키니")) or "do boi" in t or "swimwear" in t or "swimsuit" in t:
        return "I_SWIMWEAR"
    if any(k in raw for k in ("담배냄새", "담배 냄새", "연기냄새", "연기 냄새")) or "mui thuoc" in t or "cigarette" in t or "smoke odor" in t:
        return "I_ODOR_SMOKE"
    if any(k in raw for k in ("케어라벨", "세탁표시", "세탁 기호", "케어 라벨", "세탁기호")) or "care label" in t or "ky hieu giat" in t or "washing symbol" in t:
        return "I_CARE_LABEL"
    if any(k in raw for k in ("드라이클리닝", "드라이 클리닝", "물세탁인가", "드라이인가")) or "dry clean" in t or "dry-clean" in t or "dry vs wet" in t or "giat kho" in t:
        return "I_DRY_VS_WET"
    if any(k in raw for k in ("접수", "체크인", "인수인계", "사진 동의", "견적 스크립트")) or "check-in" in t or "check in" in t or "tiep nhan" in t or "intake script" in t:
        return "I_INTAKE_SCRIPT"

    # Hats (non-golf)
    if any(k in raw for k in ("야구모자", "볼캡", "모자", "캡")) or "baseball cap" in t or (
        ("mu " in t or t.startswith("mu") or " hat" in f" {t}" or t.endswith(" hat")) and "mua" not in t
    ):
        if any(k in raw for k in ("가죽모자",)) or ("leather" in t and "hat" in t):
            return "I_LEATHER_GARMENT"
        return "I_HAT_CAP"

    if "등산화" in raw or "hiking" in t or "giay leo" in t or "outdoor shoe" in t:
        return "I_HIKING_SHOE"

    if "gore" in t or "dwr" in t or "고어" in raw or "방수자켓" in raw or "chong tham" in t:
        return "I_GORETEX"
    if "기능성" in raw and ("자켓" in raw or "등산" in raw or "아웃도어" in raw):
        return "I_GORETEX"
    if "다운" in raw or "패딩" in raw or "ao phao" in t or "down jacket" in t or "padding" in t:
        return "I_DOWN_JACKET"
    # Shoes — specific before generic (require shoe cues to avoid false hits)
    if (
        "신발끈" in raw
        or "day giay" in t
        or "shoelace" in t
        or (("끈" in raw or "lace" in t) and shoe)
    ):
        return "I_SHOE_LACES"
    white_panel = (
        any(k in raw for k in ("흰창", "흰 창", "중창"))
        or "midsole" in t
        or "canh trang" in t
        or "de trang" in t
        or ("옆면" in raw and shoe)
    )
    if white_panel and shoe:
        return "I_SNEAKER_WHITE"
    if "러닝" in raw or "running" in t or "giay chay" in t:
        return "I_RUNNING_MESH"
    if shoe and (any(k in raw for k in ("망사",)) or "mesh" in t or "luoi" in t):
        return "I_RUNNING_MESH"
    if "스니커" in raw or "운동화" in raw or "sneaker" in t or "giay the thao" in t or (shoe and not leather and not suede):
        return "I_SNEAKER"
    # Dress shirt care — skip when yellowing / collar / armpit (those are stain SOPs)
    yellow_shirt = any(
        k in raw for k in ("누렇", "황변", "노랗", "누래", "변색", "노란")
    ) or ("vang" in t and ("ao so mi" in t or "so mi" in t))
    stain_cue = any(
        k in raw for k in ("목때", "칼라때", "깃때", "겨드랑이", "암내")
    ) or "vong co" in t or "collar" in t or "armpit" in t
    if not yellow_shirt and not stain_cue and (
        any(k in raw for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠"))
        or "ao so mi" in t
        or "dress shirt" in t
    ):
        return "I_DRESS_SHIRT"
    return ""


def _infer_fabric_from_text(text: str) -> str:
    """Map common KO/VI/EN fabric words in the user message to Neo4j-friendly tokens."""
    if not text:
        return ""
    raw = text
    t = _normalize_text(text)
    # Suede / nubuck before generic leather
    if any(k in raw for k in ("스웨이드", "누벅")) or "suede" in t or "nubuck" in t or "da lon" in t:
        return "suede"
    if any(k in raw for k in ("가죽",)) or re.search(r"(^|[^a-z])da([^a-z]|$)", t) or "leather" in t:
        # avoid false hit on common VI words containing 'da' as substring inside longer tokens — use word-ish check
        if "leather" in t or "가죽" in raw or "da bong" in t or "ao da" in t or "giay da" in t or "tui da" in t or "gang da" in t or t.strip() == "da" or " vai da" in f" {t}" or t.startswith("da "):
            return "leather"
    if any(k in raw for k in ("모피",)) or (("fur" in t or "long thu" in t) and "faux" not in t and "gia" not in t):
        return "fur"
    if any(k in raw for k in ("비단", "실크")) or "silk" in t or "lua" in t or "ao dai" in t or "aodai" in t or "hanbok" in t or "한복" in raw:
        return "silk"
    if "울" in raw or "wool" in t or "vai len" in t or re.search(r"(^|[^a-z])len([^a-z]|$)", t):
        return "wool"
    if "폴리" in raw or "polyester" in t or "tong hop" in t:
        return "polyester"
    if "데님" in raw or "청바지" in raw or "denim" in t:
        return "denim"
    if "린넨" in raw or "linen" in t or "vai lanh" in t:
        return "linen"
    if "레이온" in raw or "rayon" in t:
        return "rayon"
    if "면" in raw or "cotton" in t or "vai bong" in t:
        return "cotton"
    return ""


_S1_OWNER = {
    "code": "S1",
    "name": "Wash Friends Neutral Detergent",
    "name_vi": "Nuoc giat trung tinh Wash Friends",
    "name_ko": "워시프렌즈 중성세제",
    "role": "WF supply pH-neutral for silk wool delicate",
    "safe_on_wool": True,
    "safe_on_silk": True,
    "shop_name_vi": "Nuoc giat trung tinh do Wash Friends cung cap",
    "buy_where_vi": "Kho hang / cung ung Wash Friends",
    "buy_where_ko": "워시프렌즈 본사·창고 공급",
    "wf_supply": True,
    "when_use_vi": "Bat buoc uu tien khi can chat giat trung tinh / lua / len",
    "dilution_vi": "Theo huong dan chai Wash Friends — uu tien lua/len",
    "dilution_ko": "워시프렌즈 중성세제 병 안내 따름 — 실크·울 우선",
}

# Synthetic tool for color-fade small-spot path (not a Neo4j Tool node)
_COLOR_FADE_TOOLS = [
    {
        "id": "T_FABRIC_MARKER",
        "name_vi": "But mau vai (chi cho NHO <= dong xu; tam thoi)",
        "name_ko": "천용 컬러펜(소면적·동전 이하만, 임시)",
        "use_for_vi": "Cho NHO: cham ngoai→trong, co dinh nhiet theo nhan. VUA/LON: KHONG dung but — chuyen nhuom/boi thuong.",
        "use_for_ko": "소면적만: 바깥→안 터치, 병 안내대로 열고정. 중·대면적: 펜 금지 — 염색/배상.",
        "use_for_en": "Small spot only: dab outside→in, heat-set per pen label. Medium/large: no pen — re-dye/compensate.",
    }
]


def _apply_delicate_s1_fallback(graph: dict) -> dict:
    """If silk/wool left with zero safe chemicals, offer S1 only — never for color-fade restore."""
    if not isinstance(graph, dict):
        return graph
    ic = graph.get("item_context") or {}
    if ic.get("id") in {"I_COLOR_FADE", "I_FUR_REAL", "I_GOLF_GLOVE_LEATHER"}:
        return graph
    sc = graph.get("stain_context") or {}
    if sc.get("id") == "I_COLOR_FADE":
        return graph

    fabric = graph.get("fabric_context") or {}
    fid = str(fabric.get("id") or "").upper()
    fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''}".lower()
    is_silk = fid == "F4" or "silk" in fname or "lua" in fname
    is_wool = fid == "F3" or "wool" in fname or " len" in f" {fname}"
    if not (is_silk or is_wool):
        return graph

    chems = [c for c in (graph.get("chemicals") or []) if c]
    if chems:
        return graph
    out = dict(graph)
    out["chemicals"] = [dict(_S1_OWNER)]
    out["washfriends_supply"] = []
    return out


def _apply_fabric_chem_safety(graph: dict) -> dict:
    """Drop chemicals unsafe for the matched fabric so the LLM cannot recommend them."""
    fabric = graph.get("fabric_context") or {}
    garment_color = str(graph.get("garment_color") or "").lower()

    fid = str(fabric.get("id") or "").upper()
    fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''}".lower()
    is_silk = fid == "F4" or "silk" in fname or "lua" in fname or "lụa" in fname
    is_wool = fid == "F3" or "wool" in fname or " len" in f" {fname}" or fname.strip() == "len"
    is_leather = fid == "F8" or "leather" in fname or ("da (" in fname) or fname.strip() == "da"
    is_suede = fid == "F9" or "suede" in fname or "nubuck" in fname or "da lon" in fname
    is_fur = fid == "F10" or "fur" in fname or "long thu" in fname
    delicate = is_silk or is_wool or is_leather or is_suede or is_fur
    # If no fabric matched, still apply color bleach rules when color known
    if not fabric and not garment_color:
        return graph

    chems = [c for c in (graph.get("chemicals") or []) if c]
    safe, blocked = [], []
    for c in chems:
        code = str(c.get("code") or "").upper()
        reasons = []
        if is_silk and c.get("safe_on_silk") is False:
            reasons.append("not_safe_on_silk")
        if is_wool and c.get("safe_on_wool") is False:
            reasons.append("not_safe_on_wool")
        if (is_leather or is_suede or is_fur) and code in {"B1", "B2", "A4", "E1", "E2", "E3", "D3", "A3", "A5", "X1", "X2"}:
            reasons.append("not_safe_on_leather_suede_fur")
        if is_suede and code in {"A1", "D2"}:
            # Suede: avoid wet chemistry by default — professional path
            reasons.append("suede_prefer_dry_pro")
        if is_fur and code in {"A1", "D2", "N1", "S1"}:
            reasons.append("fur_pro_only")
        # can_bleach = chlorine (B2) only — do NOT treat as oxygen ban
        if fabric.get("can_bleach") is False and code == "B2":
            reasons.append("fabric_no_chlorine")
        # Oxygen B1 / A4 / reducing X1: block on protein delicates + leather family
        is_rayon = fid == "F7" or "rayon" in fname
        no_oxygen = (
            is_silk
            or is_wool
            or is_leather
            or is_suede
            or is_fur
            or is_rayon
            or fabric.get("can_oxygen") is False
        )
        if no_oxygen and code in {"B1", "A4", "X1"}:
            reasons.append("fabric_no_oxygen_bleach")
        # X1 also never on polyester/denim (color / fiber risk) — white cotton/linen only
        if code == "X1" and fid in {"F2", "F6"}:
            reasons.append("x1_white_cotton_linen_only")
        # X2 oxalic: never on silk/wool/rayon/leather (already in no_oxygen family for silk etc.)
        if no_oxygen and code == "X2":
            reasons.append("fabric_no_oxalic")
        if fabric.get("acid_safe") is False and code in {"A3", "A5", "X2"} and not (is_leather or is_suede):
            reasons.append("fabric_no_acid")
        if fabric.get("enzyme_safe") is False and code in {"E1", "E2", "E3"}:
            reasons.append("fabric_no_enzyme")
        # Garment color: never chlorine / reducing bleach on non-white
        if garment_color in {"colored", "black"} and code in {"B2", "X1"}:
            reasons.append("color_no_chlorine_or_reducing")
        if garment_color == "black" and code in {"B1", "A4"}:
            reasons.append("black_no_bleach")
        if reasons:
            blocked.append({
                "name_vi": c.get("name_vi"),
                "name_ko": c.get("name_ko"),
                "shop_name_vi": c.get("shop_name_vi"),
                "reason": ",".join(reasons),
            })
        else:
            safe.append(c)

    out = dict(graph)
    out["chemicals"] = safe
    if blocked:
        out["chemicals_blocked_for_fabric"] = blocked
        out["delicate_chem_rule"] = (
            "Chi dung chemicals[] con lai. Neu rong VA lua/len: co the chi con S1 neu da gan. "
            "Cam khuyen nghi chemicals_blocked_for_fabric. Bo qua tip/dried_path neu chung ke chat bi chan. "
            "Cam goi y tay oxy / B1 tren da hoac suede. Cam bia nuoc giat khi chemicals[] rong "
            "(tru truong hop S1 da co trong chemicals[])."
        )

    if delicate and isinstance(out.get("stain_context"), dict):
        stain = dict(out["stain_context"])
        if is_suede:
            stain["why_vi"] = (
                "Suede/da lon: NUOC va tay oxy de de lai vet vinh vien. "
                "Uu tien chai kho / tay kho; nang → chuyen chuyen nghiep. CAM may giat, CAM say."
            )
            stain["fresh_path_vi"] = (
                "Ngoai troi thong gio, khau trang + gang. Chai kho nhe ngoai→trong. "
                "KHONG nuoc, KHONG tay oxy. Neu sau: gui chuyen nghiep."
            )
            stain["dried_path_vi"] = (
                "Chi chai kho / tay kho. Khong het → bao khach gui chuyen. "
                "KHONG ngam, KHONG may, KHONG tay oxy."
            )
            stain["aftercare_vi"] = (
                "De kho tu nhien bong mat. Khong say, khong ui. Thong bao khach neu con vet."
            )
            stain["tip"] = stain["why_vi"]
        elif is_leather:
            stain["why_vi"] = (
                "Da bong: CAM may giat, CAM tay oxy/javel, CAM nhiet/nang gay. "
                "It nuoc toi da; sau xu ly can boi kem da. Nam moc: uu tien kho + con nhe (test)."
            )
            stain["fresh_path_vi"] = (
                "Thong gio ngoai troi, khau trang + gang. Chai/kho khan kho quet nam. "
                "Da bong: khan + con sat khuan (70%) nhe, TEST goc khuat. "
                "KHONG tay oxy. Xong: boi kem duong da, phoi bong mat."
            )
            stain["dried_path_vi"] = (
                "Lap chai kho + lau con nhe neu da bong cho phep. "
                "Nam sau long / dien rong → tu choi xu ly sau, chuyen chuyen nghiep. CAM may giat."
            )
            stain["aftercare_vi"] = (
                "Kiem tra mau/be mat TRUOC khi giao. Phoi bong mat, boi kem da. KHONG say may."
            )
            stain["tip"] = stain["why_vi"]
        elif is_silk:
            stain["why_vi"] = (
                "Lua (silk) nhay cam axit, enzyme va tay. "
                "Uu tien nuoc LANH + nuoc giat trung tinh Wash Friends + luc nhe. "
                "Khong dung giam manh, tay oxy, enzyme."
            )
            stain["fresh_path_vi"] = (
                "Tham/xa nuoc lanh mat trai ngay → cham nuoc giat trung tinh Wash Friends pha loang nhe → "
                "tham bang khan trang ngoai→trong. Khong cha manh."
            )
            stain["dried_path_vi"] = (
                "Ngam lanh nhe + nuoc giat trung tinh Wash Friends. Neu khong het: bao khach, "
                "khong dung tay oxy/giam dam/enzyme. Kiem tra truoc khi say/ui."
            )
            stain["aftercare_vi"] = (
                "Kiem tra anh sang manh TRUOC say/ui. Con vet → xu ly lai bang nuoc giat trung tinh, khong say."
            )
            stain["tip"] = stain["why_vi"]
        elif is_wool:
            stain["why_vi"] = (
                "Len (wool) la so protein tu nhien — enzyme/tay/axit de hong soi. "
                "Uu tien nuoc giat trung tinh Wash Friends + nuoc lanh + luc rat nhe."
            )
            stain["fresh_path_vi"] = (
                "Tham lanh + nuoc giat trung tinh nhe, khong cha. Khong enzyme, khong tay oxy."
            )
            stain["dried_path_vi"] = (
                "Ngam lanh ngan + nuoc giat trung tinh. Khong het → bao khach, khong dung enzyme/tay/axit manh."
            )
            stain["aftercare_vi"] = (
                "Kiem tra truoc say. Uu tien phoi phang, khong say may."
            )
            stain["tip"] = stain["why_vi"]
        out["stain_context"] = stain

    return out


def _chem_everyday_map(lang: str = "vi") -> dict[str, str]:
    """Internal code → owner everyday name (KO/VI/EN)."""
    if lang == "ko":
        return {
            "E1": "효소(프로테아제) 세제·효소제",
            "E2": "전분 분해 효소 세제",
            "E3": "유지 분해 효소 세제",
            "D1": "기름·오일 용제(탈지제)",
            "D2": "주방세제(중성)",
            "D3": "일반 세탁 세제(강력)",
            "B1": "산소계 표백제(과탄산·옥시클린 계열)",
            "B2": "염소계 표백제(락스/자벨)",
            "A1": "이소프로필 알코올(소독용 알코올)",
            "A2": "아세톤(매니큐어 리무버 계열)",
            "A3": "흰 식초(식용 식초 약 5%)",
            "A4": "과산화수소 3%(옥시)",
            "A5": "암모니아 희석액",
            "N1": "베이킹소다",
            "N2": "소금(식염)",
            "N3": "옥수수 전분·베이비파우더(오일 흡착)",
            "S1": "워시프렌즈 중성세제",
            "WF_SOFT": "워시프렌즈 섬유유연제",
            "WF_FRAG": "워시프렌즈 독일 향수 스프레이",
            "X1": "환원 표백제(하이드로설파이트·흰 면/린넨 전용)",
            "X2": "옥살산(녹·철·라테라이트용)",
        }
    if lang == "en":
        return {
            "E1": "enzyme (protease) detergent",
            "E2": "starch-enzyme detergent",
            "E3": "lipase / grease enzyme detergent",
            "D1": "degreasing solvent",
            "D2": "dish soap (neutral)",
            "D3": "heavy laundry detergent",
            "B1": "oxygen bleach (percarbonate / Oxi-type)",
            "B2": "chlorine bleach",
            "A1": "isopropyl alcohol",
            "A2": "acetone (nail-polish remover type)",
            "A3": "white vinegar (~5%)",
            "A4": "hydrogen peroxide 3%",
            "A5": "diluted ammonia",
            "N1": "baking soda",
            "N2": "table salt",
            "N3": "cornstarch / baby powder (oil absorbent)",
            "S1": "Wash Friends neutral detergent",
            "WF_SOFT": "Wash Friends softener",
            "WF_FRAG": "Wash Friends fragrance spray",
            "X1": "reducing bleach (hydrosulfite — white cotton/linen only)",
            "X2": "oxalic acid (rust / laterite — gloves)",
        }
    return {
        "E1": "nuoc giat / bot ngam enzyme (protease)",
        "E2": "nuoc giat enzyme (tinh bot)",
        "E3": "nuoc giat enzyme (dau mo)",
        "D1": "dung moi tay dau / tay nhot",
        "D2": "nuoc rua chen",
        "D3": "nuoc giat / bot giat dam",
        "B1": "bot tay oxy / tay mau an toan (oxyclean-type)",
        "B2": "nuoc Javel / tay trang",
        "A1": "con sat khuan / con y te 70-90%",
        "A2": "acetone / dung moi son mong",
        "A3": "giấm trắng 5%",
        "A4": "oxy già 3%",
        "A5": "ammonia pha loãng",
        "N1": "baking soda",
        "N2": "muối ăn",
        "N3": "bột ngô / phấn rôm",
        "S1": "nước giặt trung tính Wash Friends",
        "WF_SOFT": "nước xả Wash Friends",
        "WF_FRAG": "xit hương Wash Friends",
        "X1": "bột tẩy khử (sodium hydrosulfite) — chỉ cotton/linen TRẮNG",
        "X2": "acid oxalic — rỉ sét / đất đỏ (găng tay)",
    }


_TOOL_NAME_EN = {
    "T_CLOTH": "clean cloth / blotting paper",
    "T_SPRAY": "spray bottle (labeled)",
    "T_BRUSH_SOFT": "soft spotting brush",
    "T_BRUSH_HARD": "firm spotting brush",
    "T_BRUSH_ULTRA": "ultra-soft brush",
    "T_BRUSH_SHOE": "shoe brush",
    "T_GLOVE_NITRILE": "nitrile gloves",
    "T_MESH_BAG": "mesh laundry bag",
    "T_SOAK_BIN": "soak bin",
    "T_TIMER": "timer",
    "T_UV_LAMP": "UV / strong inspection light",
    "T_STEAM_IRON": "steam iron",
    "T_MASK": "mask / eye protection",
    "T_FABRIC_MARKER": "fabric color pen (small area only)",
}


def _expand_chem_codes_in_text(text: str, lang: str = "vi") -> str:
    """Replace bare chem codes with everyday names so scrub/LLM never leave empty particles."""
    if not text:
        return text
    mapping = _chem_everyday_map(lang)
    # Longer tokens first
    for code in sorted(mapping.keys(), key=len, reverse=True):
        name = mapping[code]
        text = re.sub(
            rf"(?<![A-Za-z0-9]){re.escape(code)}(?![A-Za-z0-9])",
            name,
            text,
        )
    return text


def _scrub_internal_codes(text: str, lang: str = "vi") -> str:
    """Expand leftover internal codes to everyday names; strip markdown."""
    if not text:
        return text
    # Markdown bold/headers/emphasis (Zalo plain text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = text.replace("**", "")
    # Expand codes BEFORE deleting (owner must see salt / enzyme names)
    text = _expand_chem_codes_in_text(text, lang=lang)
    # Parenthetical leftovers after expansion rare; strip empty ()
    text = re.sub(r"\s*\(\s*\)", "", text)
    # Tool / node ids leaked by the model
    text = re.sub(r"\s*\((?:T_[A-Z0-9_]+)\)", "", text)
    text = re.sub(r"(?<![A-Za-z0-9])T_(?:BRUSH_SOFT|BRUSH_HARD|BRUSH_ULTRA|BRUSH_SHOE|CLOTH|SPRAY|FABRIC_MARKER)(?![A-Za-z0-9])", "", text)
    # Awkward KO calque "N부분 식초/물" → natural "식초 N : 물 M"
    text = re.sub(r"(\d+)\s*부분\s*(흰\s*)?식초", r"\2식초 \1", text)
    text = re.sub(r"(\d+)\s*부분\s*물", r"물 \1", text)
    text = re.sub(
        r"식초\s*(\d+)\s*(?:와|과|,|/|：|:)\s*물\s*(\d+)을?",
        r"식초 \1 : 물 \2",
        text,
    )
    text = re.sub(r"(\d+)\s*부분", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" ?،", ",", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _sanitize_graph_for_owner(graph, lang: str):
    """Drop ids / wrong-language fields so the LLM cannot echo them.
    Expand chem codes only inside same-language narrative fields.
    """
    if not isinstance(graph, dict):
        return graph
    g = dict(graph)
    lang = lang if lang in ("ko", "vi", "en") else "vi"

    def _tool(t: dict) -> dict:
        tid = str(t.get("id") or "")
        if lang == "ko":
            out = {
                "name_ko": t.get("name_ko"),
                "use_for_ko": t.get("use_for_ko") or t.get("use_for_en"),
            }
        elif lang == "en":
            out = {
                "name": _TOOL_NAME_EN.get(tid) or t.get("name_ko") or t.get("name_vi") or tid,
                "use_for_en": t.get("use_for_en") or t.get("use_for_ko") or t.get("use_for_vi"),
            }
        else:
            out = {
                "name_vi": t.get("name_vi"),
                "use_for_vi": t.get("use_for_vi"),
            }
        return {k: v for k, v in out.items() if v}

    def _chem(c: dict) -> dict:
        keep = {
            "name": c.get("name"),
            "name_vi": c.get("name_vi"),
            "name_ko": c.get("name_ko"),
            "role": c.get("role"),
            "shop_name_vi": c.get("shop_name_vi"),
            "buy_where_vi": c.get("buy_where_vi"),
            "buy_where_ko": c.get("buy_where_ko"),
            "alt1_vi": c.get("alt1_vi"),
            "alt2_vi": c.get("alt2_vi"),
            "alt3_vi": c.get("alt3_vi"),
            "alt1_ko": c.get("alt1_ko"),
            "alt2_ko": c.get("alt2_ko"),
            "alt3_ko": c.get("alt3_ko"),
            "when_use_vi": c.get("when_use_vi"),
            "dilution_vi": c.get("dilution_vi"),
            "dilution_ko": c.get("dilution_ko"),
            "wf_supply": c.get("wf_supply"),
            "safe_on_wool": c.get("safe_on_wool"),
            "safe_on_silk": c.get("safe_on_silk"),
        }
        for k in list(keep.keys()):
            if isinstance(keep[k], str):
                # Expand codes using the field's language, not mixed
                field_lang = "ko" if k.endswith("_ko") or k == "name_ko" else (
                    "vi" if k.endswith("_vi") or k in ("shop_name_vi", "name_vi", "when_use_vi") else lang
                )
                if k == "name" or k == "role":
                    field_lang = "en" if lang == "en" else field_lang
                keep[k] = _expand_chem_codes_in_text(keep[k], lang=field_lang if lang != "en" else "en")
        if lang == "ko":
            for k in (
                "name", "name_vi", "shop_name_vi", "buy_where_vi", "alt1_vi", "alt2_vi", "alt3_vi",
                "when_use_vi", "dilution_vi", "example_brands_vi", "role",
            ):
                keep.pop(k, None)
        elif lang == "vi":
            for k in (
                "name", "name_ko", "buy_where_ko", "dilution_ko",
                "alt1_ko", "alt2_ko", "alt3_ko", "role",
            ):
                keep.pop(k, None)
        else:  # en
            for k in list(keep.keys()):
                if k.endswith("_vi") or k.endswith("_ko") or k == "shop_name_vi":
                    keep.pop(k, None)
            # Prefer English everyday name from code map if only code leaked into name
            if keep.get("name"):
                keep["name"] = _expand_chem_codes_in_text(str(keep["name"]), lang="en")
        return {k: v for k, v in keep.items() if v is not None and v != ""}

    VI_FIELDS = (
        "why_vi", "fresh_path_vi", "dried_path_vi",
        "precheck_vi", "motion_vi", "water_temp_vi", "aftercare_vi",
        "force_metaphor_vi", "sense_check_vi", "success_rate_vi",
        "refuse_when_vi", "group_care_order_vi", "name_vi",
        "item_name_vi",
    )
    KO_FIELDS = (
        "why_ko", "fresh_path_ko", "dried_path_ko",
        "force_metaphor_ko", "sense_check_ko", "success_rate_ko",
        "refuse_when_ko", "group_care_order_ko", "name_ko",
        "precheck_ko", "motion_ko", "water_temp_ko", "aftercare_ko",
        "item_name_ko",
    )

    sc = g.get("stain_context")
    if isinstance(sc, dict):
        sc2 = dict(sc)
        # Expand each narrative with ITS language before dropping
        for field in VI_FIELDS:
            if sc2.get(field):
                sc2[field] = _expand_chem_codes_in_text(str(sc2[field]), lang="vi")
        for field in KO_FIELDS:
            if sc2.get(field):
                sc2[field] = _expand_chem_codes_in_text(str(sc2[field]), lang="ko")
        if sc2.get("tip"):
            tip_s = str(sc2["tip"])
            tip_lang = "ko" if re.search(r"[가-힣]", tip_s) else (
                "vi" if re.search(
                    r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ]",
                    tip_s,
                    re.I,
                ) else "en"
            )
            sc2["tip"] = _expand_chem_codes_in_text(tip_s, lang=tip_lang if tip_lang != "en" else "en")

        if lang == "ko":
            for k in VI_FIELDS:
                sc2.pop(k, None)
            # Never feed English/VI tip into KO prompt
            tip = sc2.get("tip")
            if tip and not re.search(r"[가-힣]", str(tip)):
                sc2.pop("tip", None)
            if sc2.get("why_ko"):
                sc2["tip"] = sc2["why_ko"]
            # Drop English stain name when KO name exists (avoids EN echo)
            if sc2.get("name_ko"):
                sc2.pop("name", None)
        elif lang == "vi":
            for k in KO_FIELDS:
                sc2.pop(k, None)
            tip = sc2.get("tip")
            if tip and re.search(r"[가-힣]", str(tip)):
                sc2.pop("tip", None)
            # Prefer why_vi as tip for VI; drop English tip if why_vi present
            if sc2.get("why_vi"):
                sc2["tip"] = sc2["why_vi"]
            elif tip and not re.search(
                r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ]",
                str(tip),
                re.I,
            ):
                # Keep English tip only as last resort for VI (LLM will Vietnamese)
                pass
            sc2.pop("name_ko", None)
        else:  # en
            for k in VI_FIELDS + KO_FIELDS:
                sc2.pop(k, None)
            # Keep English name + tip; strip GIAO DUC Vietnamese tips
            tip = sc2.get("tip")
            if tip and (
                re.search(r"[가-힣]", str(tip))
                or re.search(r"(?i)GIAO\s*DUC|Nhận diện", str(tip))
                or re.search(
                    r"[àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ]",
                    str(tip),
                    re.I,
                )
            ):
                sc2.pop("tip", None)
            if sc2.get("tip"):
                sc2["tip"] = _expand_chem_codes_in_text(str(sc2["tip"]), lang="en")

        # Never expose internal ids to owner LLM
        sc2.pop("id", None)
        g["stain_context"] = sc2

    ic = g.get("item_context")
    if isinstance(ic, dict):
        ic2 = dict(ic)
        for field in (
            "why_vi", "fresh_path_vi", "dried_path_vi",
            "precheck_vi", "motion_vi", "water_temp_vi", "aftercare_vi",
        ):
            if ic2.get(field):
                ic2[field] = _expand_chem_codes_in_text(str(ic2[field]), lang="vi")
        for field in (
            "why_ko", "fresh_path_ko", "dried_path_ko",
            "precheck_ko", "motion_ko", "water_temp_ko", "aftercare_ko",
        ):
            if ic2.get(field):
                ic2[field] = _expand_chem_codes_in_text(str(ic2[field]), lang="ko")
        if lang == "ko":
            for field in (
                "why_vi", "fresh_path_vi", "dried_path_vi",
                "precheck_vi", "motion_vi", "water_temp_vi", "aftercare_vi", "name_vi",
            ):
                ic2.pop(field, None)
            if ic2.get("name_ko"):
                ic2.pop("name", None)
        elif lang == "vi":
            for field in (
                "why_ko", "fresh_path_ko", "dried_path_ko",
                "precheck_ko", "motion_ko", "water_temp_ko", "aftercare_ko", "name_ko",
            ):
                ic2.pop(field, None)
        else:
            for field in (
                "why_vi", "fresh_path_vi", "dried_path_vi",
                "precheck_vi", "motion_vi", "water_temp_vi", "aftercare_vi",
                "why_ko", "fresh_path_ko", "dried_path_ko",
                "precheck_ko", "motion_ko", "water_temp_ko", "aftercare_ko",
                "name_vi", "name_ko",
            ):
                ic2.pop(field, None)
        ic2.pop("id", None)
        g["item_context"] = ic2

    # Color notes: keep only matching language
    if lang == "ko":
        g.pop("color_note_vi", None)
        g.pop("color_note_en", None)
        g.pop("protocol_minutes_vi", None)
        g.pop("spray_recipe_vi", None)
    elif lang == "vi":
        g.pop("color_note_ko", None)
        g.pop("color_note_en", None)
        g.pop("protocol_minutes_ko", None)
        g.pop("spray_recipe_ko", None)
    else:
        g.pop("color_note_ko", None)
        g.pop("color_note_vi", None)
        g.pop("protocol_minutes_ko", None)
        g.pop("protocol_minutes_vi", None)
        g.pop("spray_recipe_ko", None)
        g.pop("spray_recipe_vi", None)

    if g.get("tools"):
        g["tools"] = [_tool(t) for t in g["tools"] if t]
    if g.get("chemicals"):
        g["chemicals"] = [_chem(c) for c in g["chemicals"] if c]
    if g.get("washfriends_supply"):
        g["washfriends_supply"] = [_chem(c) for c in g["washfriends_supply"] if c]
    return g


# ─── LLM Responder ────────────────────────────────────────────────────────────
# System prompts live in reply_lang.system_prompt_for(lang) — never mix languages.


def _enrich_teach_slots(graph: dict) -> dict:
    """Fill Protocol Card teach slots from stain fields or group fallbacks (additive).

    Specialty garments (necktie/suit/…) must NEVER inherit unrelated G5 refuse text
    (leather mold / duvet equipment) — that confuses owners on a ketchup-on-tie question.
    """
    if not isinstance(graph, dict):
        return graph
    g = dict(graph)
    sc = dict(g.get("stain_context") or {})
    if not sc:
        return g
    ic = g.get("item_context") or {}
    item_id = str(ic.get("id") or sc.get("id") or "")

    group = ""
    grp = sc.get("group_id") or sc.get("group")
    if isinstance(grp, dict):
        group = str(grp.get("id") or "")
    elif isinstance(grp, str):
        group = grp

    fb = {
        "G1": {
            "force_metaphor_vi": "Cap1–2: tham nhe nhu lau mat kinh — protein de khoa neu cha manh/nuoc nong",
            "force_metaphor_ko": "Cap1–2: 안경 닦듯 가볍게 — 문지르거나 온수면 단백질 고착",
            "sense_check_vi": "Mat: nuoc xa trong. Tay: het nhon mau. Mui: het mui protein.",
            "sense_check_ko": "눈: 헹굼물 맑음. 손: 미끌거림 없음. 코: 단백질 냄새 감소.",
            "success_rate_vi": "Tuoi xu ly som: cao. Da say/nong: thap — bao khach truoc.",
            "success_rate_ko": "신선·즉시 처리: 높음. 이미 건조·열 처리: 낮음 — 사전 고지.",
            "refuse_when_vi": "Lua/len hong cau truc, mau nau da khoa sau say → bao thap / chuyen pro.",
            "refuse_when_ko": "실크·울 구조 손상 우려, 열로 고착된 갈색 → 성공률 낮음 고지/전문 의뢰.",
        },
        "G2": {
            "force_metaphor_vi": "Cap2: tham/chai nhe; hut bot truoc — cam say khi con nhon",
            "force_metaphor_ko": "Cap2: 가볍게 누르며; 흡착 먼저 — 기름 남은 채 건조 금지",
            "sense_check_vi": "Tay: het nhon. Mat: loang mo giam. Mui: het mui dau.",
            "sense_check_ko": "손: 미끄러움 없음. 눈: 기름때 감소. 코: 오일 냄새 감소.",
            "success_rate_vi": "Hut + surfactant dung: tot. Da say khoa mo: thap.",
            "success_rate_ko": "흡착+계면활성제 정석: 양호. 건조로 고착: 낮음.",
            "refuse_when_vi": "Da/suede + dung moi manh; khong thong gio → tu choi / chuyen.",
            "refuse_when_ko": "가죽·스웨이드+강한 용제, 환기 불가 → 거절/전문.",
        },
        "G3": {
            "force_metaphor_vi": "Cap1–2: tham ngoai→trong — cha lan tannin/mau",
            "force_metaphor_ko": "Cap1–2: 바깥→안 흡수 — 문지르면 탄닌·색소 번짐",
            "sense_check_vi": "Mat: mau nhat. Mui: het chua/ngot. Anh sang: khong con vet.",
            "sense_check_ko": "눈: 색 옅어짐. 코: 신맛·단맛 감소. 강광: 잔존 없음.",
            "success_rate_vi": "Xu ly SOM + lanh: cao. Da say: mau khoa — bao truoc.",
            "success_rate_ko": "즉시·찬물: 높음. 건조 후: 색소 고착 — 사전 고지.",
            "refuse_when_vi": "Len/lua + oxy/chlorine; khach doi 100% → tu choi cam ket.",
            "refuse_when_ko": "실크·울+산소/염소, 100% 요구 → 보장 거절.",
        },
        "G4": {
            "force_metaphor_vi": "Cap1: blot/tham — KHONG cha (lan pigment)",
            "force_metaphor_ko": "Cap1: 찍기·흡수 — 문지르면 색소 확산",
            "sense_check_vi": "Mat: muc/mau giam tung chu ky blot. Test goc truoc.",
            "sense_check_ko": "눈: 블롯마다 색소 감소. 구석 테스트 필수.",
            "success_rate_vi": "Muc but: trung binh. Permanent/son: thap — bao 100% khong cam ket.",
            "success_rate_ko": "볼펜: 중간. 유성·매니큐어: 낮음 — 100% 비보장 고지.",
            "refuse_when_vi": "In/son/vai mong de hong dung moi → test fail thi dung.",
            "refuse_when_ko": "프린트·도장·섬세 원단 용제 손상 → 테스트 실패 시 중단.",
        },
        "G5": {
            "force_metaphor_vi": "Theo fresh_path; thuong Cap1–2 + PPE neu moc/hoa chat manh",
            "force_metaphor_ko": "fresh_path 따름; 보통 Cap1–2 + 곰팡이/강산 시 PPE",
            "sense_check_vi": "Mat + mui + anh sang manh truoc say.",
            "sense_check_ko": "눈·코·강광으로 잔여 확인 후 건조.",
            "success_rate_vi": "Phuc tap: bao khoi phuc 100% — ghi nhan anh truoc/sau.",
            "success_rate_ko": "복합·불확실 오염: 100% 복원 비보장 — 전후 사진.",
            "refuse_when_vi": "Khong chac chat lieu / thiet bi / an toan → dung, bao khach, chuyen chuyen.",
            "refuse_when_ko": "원단·약품·설비·안전이 불확실하면 중단하고 고객 고지 후 전문 의.",
        },
    }

    # Garment-specific teach — refuse/sense must match the item, not home-textile G5
    item_teach = {
        "I_NECKTIE": {
            "force_metaphor_ko": "Cap1: 블롯·두드리기만 — 문지르면 색소 번지고 형태 붕괴",
            "force_metaphor_vi": "Cap1: tham/dap — cha = lan mau + hong form caravat",
            "sense_check_ko": "눈: 얼룩 색 옅어짐. 강광: 잔여 확인. 형태: 넥타이 비틀림·물짐 없음.",
            "sense_check_vi": "Mat: mau nhat. Anh sang: het vet. Form: caravat khong meo/vet nuoc.",
            "success_rate_ko": "신선·국소 즉시: 중간~양호. 마른 후·실크 물짐: 낮음 — 사전 고지. 100% 비보장.",
            "success_rate_vi": "Tuoi + spotting cuc bo: trung binh-cao. Kho/lua vet nuoc: thap — bao truoc.",
            "refuse_when_ko": "큰 얼룩·이미 형태 붕괴·고객이 물세탁/100% 요구 → 국소 중단, 드라이클리닝 안내·보장 거절.",
            "refuse_when_vi": "Vet lon / form hong / khach doi giat nuoc hoac 100% → dung spotting, huong dry-clean, tu choi cam ket.",
        },
        "I_SUIT": {
            "force_metaphor_ko": "Cap1–2: 블롯·연한 솔 — 가정용 세탁기 금지",
            "force_metaphor_vi": "Cap1–2: tham/chai nhe — CAM may nha",
            "sense_check_ko": "눈: 얼룩 감소. 형태: 어깨·라펠 변형 없음.",
            "sense_check_vi": "Mat: vet giam. Form: vai/ve ao khong meo.",
            "success_rate_ko": "가벼운 국소: 중간. 캔버스·큰 얼룩: 낮음 — 드라이 우선 고지.",
            "success_rate_vi": "Spotting nhe: trung binh. Canvas/vet lon: thap — uu tien dry-clean.",
            "refuse_when_ko": "구조(캔버스)·큰 얼룩·고객 100% 요구 → 가정 세탁 거절, 전문 드라이 안내.",
            "refuse_when_vi": "Canvas/vet lon/khach doi 100% → tu choi giat nha, chuyen dry-clean.",
        },
        "I_AO_DAI": {
            "refuse_when_ko": "실크 불확실·고가·큰 얼룩 → 무리한 물세탁 거절, 전문/고객 동의.",
            "refuse_when_vi": "Lua khong chac / dat / vet lon → tu choi giat manh, chuyen / dong y khach.",
            "sense_check_ko": "눈: 얼룩·물짐 확인. 손: 과도한 마찰 흔적 없음.",
            "sense_check_vi": "Mat: vet/vet nuoc. Tay: khong cha manh.",
            "success_rate_ko": "섬세 원단: 중간 이하 — 100% 비보장.",
            "success_rate_vi": "Vai mong: trung binh thap — khong cam ket 100%.",
        },
        "I_HANBOK": {
            "refuse_when_ko": "천연염색·고가 한복 → 가정 세탁 거절, 전문 우선.",
            "refuse_when_vi": "Nhuom tu nhien / dat → tu choi giat nha, uu tien chuyen.",
            "sense_check_ko": "눈: 이염·얼룩. 형태: 고름·깃 변형 없음.",
            "sense_check_vi": "Mat: lo mau/vet. Form: git/goreum khong hong.",
            "success_rate_ko": "전문 의뢰 권장 — 매장 단독 100% 비보장.",
            "success_rate_vi": "Uu tien chuyen — khong cam ket 100% tai tiem.",
        },
    }

    gid = group if group in fb else ""
    if gid == "item_care":
        gid = ""
    if not gid:
        # Tannin/dye before oil — ketchup has oil+tannin+dye and must not fall to G5/G2-only
        if sc.get("contains_protein") and not sc.get("contains_tannin") and not sc.get("contains_oil"):
            gid = "G1"
        elif sc.get("contains_tannin"):
            gid = "G3"
        elif sc.get("contains_dye") and not sc.get("contains_oil"):
            gid = "G4"
        elif sc.get("contains_oil"):
            gid = "G2"
        elif sc.get("contains_protein"):
            gid = "G1"
        else:
            gid = "G5"

    card = dict(fb.get(gid) or fb["G5"])
    it = item_teach.get(item_id) or {}
    if it:
        # Item refuse/sense/success always win for specialty garments
        card.update(it)
        if not gid or gid == "G5":
            gid = f"item:{item_id}"

    for k, v in card.items():
        if not sc.get(k):
            sc[k] = v
        elif it and k in it:
            # Force-correct wrong G5 leftovers if somehow pre-filled
            if k.startswith("refuse_when") or (
                "가죽 곰팡이" in str(sc.get(k) or "")
                or "대형 이불" in str(sc.get(k) or "")
                or "chan lon" in str(sc.get(k) or "")
                or "Da/suede moc" in str(sc.get(k) or "")
            ):
                sc[k] = it[k]
            elif k in it and (gid.startswith("item:") or item_id in item_teach):
                # Prefer item sense/success/refuse on specialty items
                if k.startswith(("refuse_when", "sense_check", "success_rate")):
                    sc[k] = it[k]

    g["stain_context"] = sc
    g["teach_group"] = gid
    return g


def _build_llm_prompt(user_message: str, graph_context: dict, lang: str = "vi") -> str:
    raw_graph = graph_context.get("graph")
    if isinstance(raw_graph, dict):
        raw_graph = _enrich_teach_slots(raw_graph)
    safe_graph = _sanitize_graph_for_owner(raw_graph, lang) if isinstance(raw_graph, dict) else raw_graph
    graph_json = json.dumps(safe_graph, ensure_ascii=False, indent=2, default=str)
    query_type = graph_context.get("query_type", "unknown")
    if lang == "ko":
        lang_rule = (
            "한국어만. 베트남어·영어 금지. "
            "단계: (1)오염·원단·색상 (2)도구 — tools[]의 각 항목을 'name_ko: use_for_ko' 한 줄로 "
            "(사용법 생략·지어내기 금지; 없으면 해당 없음). "
            "타이머·담금통은 use_for_ko에 적힌 정확한 분(예: 15–45분)을 그대로 말할 것. "
            "분무기는 「무슨 약을 어떤 비율로 넣고, 병 겉에 왜 적는지」를 use_for_ko 그대로. "
            "(3)힘·방향 Cap (4)약품(name_ko·dilution_ko) (5)수온 (6)후관리. "
            "[왜 이 순서] → … → [감각 체크] → [성공률·고지] → [거절·보내기]. "
            "why_ko/fresh_path_ko/sense_check_ko·color_note_ko가 있으면 그대로. "
            "없으면 contains_*·chemicals·tools 사실만으로 한국어 작성 — 외국어 원문 복사 금지. "
            "희석 dilution_ko. 마크다운 금지. 코드/id 금지."
        )
        wrapper = f"""점주 질문: {user_message}

[그래프 데이터 — 질의유형: {query_type}]
{graph_json}

{lang_rule}
위 데이터만 사용. 다른 얼룩/언어 섞지 말 것."""
    elif lang == "en":
        lang_rule = (
            "English ONLY. No Korean or Vietnamese words/headers. "
            "Steps: (1) Identify stain/fabric/color (2) Tools — each tools[] as 'name: use_for_en' "
            "(how-to required; do not invent) "
            "(3) Force+direction Cap (4) Chemicals (5) Temp (6) Aftercare. "
            "Blocks: [Why this order] [Sense check] [Success rate / disclose] [Refuse / refer]. "
            "Use English name/tip, color_note_en, and chemical name fields. Do not copy foreign text. "
            "No markdown. No internal codes."
        )
        wrapper = f"""Owner question: {user_message}

[GRAPH DATA — query type: {query_type}]
{graph_json}

{lang_rule}
Answer from this data only. Do not mix languages."""
    else:
        lang_rule = (
            "CHỈ tiếng Việt. CẤM Hàn/Anh. "
            "Bước: (1) Nhận diện (vet/vai/màu) (2) Dụng cụ — mỗi tools[] dạng 'name_vi: use_for_vi' "
            "(bắt buộc cách dùng; CẤM bịa; rỗng→không cần). "
            "Đồng hồ/chau ngâm: nói đúng số phút trong use_for_vi. "
            "Bình xịt: nói đúng thuốc + tỷ lệ + vì sao ghi nhãn theo use_for_vi. "
            "(3) Lực+hướng Cap (4) Hóa chất (5) Nhiệt độ (6) Sau xử lý. "
            "[Tại sao thứ tự này] → … → [Kiểm tra giác quan] → [Tỷ lệ & báo khách] → [Từ chối / chuyển]. "
            "Dùng why_vi/fresh_path_vi/color_note_vi nếu có. Không copy name_ko/Hangul. "
            "Pha loãng dilution_vi. Không markdown. Không mã nội bộ."
        )
        wrapper = f"""Câu hỏi từ chủ cửa hàng: {user_message}

[DỮ LIỆU ĐỒ THỊ — loại truy vấn: {query_type}]
{graph_json}

{lang_rule}
Chỉ trả lời từ dữ liệu trên. Không trộn ngôn ngữ."""
    return wrapper


def _call_llm(llm_prompt: str, lang: str = "vi") -> str:
    response = _openai.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": system_prompt_for(lang)},
            {"role": "user", "content": llm_prompt},
        ],
    )
    return _scrub_internal_codes(response.choices[0].message.content.strip(), lang=lang)


def _empty_graph_reply(entities: dict, *, image: bool = False) -> str:
    lang = entities.get("lang", "vi")
    if image:
        if lang == "ko":
            return (
                "사진을 받았지만 얼룩 종류를 정확히 파악하기 어렵습니다.\n\n"
                "추가로 알려주세요:\n"
                "• 어떤 종류의 얼룩인가요? (기름, 혈액, 커피 등)\n"
                "• 어떤 원단인가요? (면, 실크, 폴리에스터 등)"
            )
        if lang == "en":
            return (
                "I received the photo but cannot identify the stain clearly.\n\n"
                "Please tell me:\n"
                "• What kind of stain? (oil, blood, coffee, etc.)\n"
                "• What fabric? (cotton, silk, polyester, etc.)"
            )
        return (
            "Toi da nhan anh nhung kho xac dinh chinh xac loai vet ban.\n\n"
            "Vui long cho biet them:\n"
            "• Loai vet ban la gi? (dau an, mau, ca phe, ...)\n"
            "• Chat lieu vai la gi? (cotton, lua, polyester, ...)"
        )
    if lang == "ko":
        return (
            "죄송합니다, 해당 정보를 찾을 수 없었습니다.\n\n"
            "더 정확한 답변을 위해 알려주세요:\n"
            "• 어떤 종류의 얼룩인가요? (예: 기름, 혈액, 커피)\n"
            "• 어떤 원단인가요? (예: 면, 실크, 폴리에스터)\n"
            "• 얼룩이 생긴 지 얼마나 됐나요?"
        )
    if lang == "en":
        return (
            "Sorry — I could not find matching guidance.\n\n"
            "Please share:\n"
            "• Stain type (e.g. oil, blood, coffee)\n"
            "• Fabric (e.g. cotton, silk, polyester)\n"
            "• How old is the stain?"
        )
    return (
        "Xin loi, toi khong tim thay thong tin cho cau hoi nay.\n\n"
        "De tra loi chinh xac hon, vui long cho biet:\n"
        "• Loai vet ban la gi? (vi du: dau an, mau, ca phe)\n"
        "• Chat lieu vai la gi? (vi du: cotton, lua, polyester)\n"
        "• Vet ban bi bao lau roi?"
    )


def _answer_with_optional_cache(
    cache_question: str,
    entities: dict,
    graph_context: dict,
    *,
    prefix: str = "",
) -> str:
    """LLM answer with fail-open cache. Skips cache when graph is empty.
    Retries once if reply mixes languages.
    """
    lang = entities.get("lang") or "vi"
    if lang not in ("ko", "vi", "en"):
        lang = detect_reply_lang(cache_question)
        entities["lang"] = lang
    ctx_key = build_context_key(entities)
    cached = cache_lookup(cache_question, ctx_key)
    if cached and not reply_language_leaks(cached, lang):
        return cached
    # Contaminated cache entry → ignore and regenerate
    if cached and reply_language_leaks(cached, lang):
        print(f"[LANG] ignore contaminated cache lang={lang} leaks={reply_language_leaks(cached, lang)}")

    base_prompt = _build_llm_prompt(cache_question, graph_context, lang=lang)
    llm_prompt = (prefix + "\n\n" + base_prompt) if prefix else base_prompt
    answer = _call_llm(llm_prompt, lang=lang)
    leaks = reply_language_leaks(answer, lang)
    if leaks:
        print(f"[LANG] leak detected lang={lang} reasons={leaks}; retrying")
        retry_prompt = retry_addon(lang) + "\n\n" + llm_prompt
        answer2 = _call_llm(retry_prompt, lang=lang)
        if not reply_language_leaks(answer2, lang):
            answer = answer2
        else:
            print(f"[LANG] retry still leaks={reply_language_leaks(answer2, lang)}; keeping second attempt")
            answer = answer2
    cache_store(cache_question, answer, ctx_key)
    return answer


def generate_response_from_entities(
    entities: dict,
    user_caption: str = "",
    prefix: str = "",
) -> str:
    """
    Entry point when entities are already known (e.g. from image analysis).
    """
    # Ensure GraphRAG routing fields exist
    entities.setdefault("intent", "treatment")
    # Caption Hangul → Korean; else keep existing lang from vision / default vi
    if user_caption and re.search(r"[가-힣]", user_caption):
        entities["lang"] = "ko"
    elif not entities.get("lang"):
        entities["lang"] = detect_reply_lang(user_caption) if user_caption else "vi"

    graph_context = _fetch_graph_context(entities)
    graph_data    = graph_context.get("graph")

    if not graph_data or graph_data in ({}, []):
        return _empty_graph_reply(
            entities,
            image=bool(entities.get("_image_analysis")),
        )

    return _answer_with_optional_cache(
        question_for_cache(user_caption, entities),
        entities,
        graph_context,
        prefix=prefix,
    )


def generate_response(user_message: str) -> str:
    """Main entry point: reply in the same language as the user (vi or ko)."""
    lang = detect_reply_lang(user_message)
    # Fast path — lang in context so KO/VI caches never mix
    cached = cache_lookup(user_message, build_context_key({"lang": lang}))
    if cached:
        return cached

    entities = extract_entities(user_message)
    entities["_raw"] = user_message
    # Hard override language from script (more reliable than LLM lang field)
    entities["lang"] = lang
    # Hard override for high-value franchise phrases (before graph routing)
    # More specific phrases first.
    raw_n = _normalize_text(user_message)
    if "laterite" in raw_n or "dat do" in raw_n or any(
        k in user_message for k in ("라테라이트", "적토", "붉은 흙", "빨간 흙")
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_LATERITE"
        entities["stain_type"] = "dat do laterite"
    elif "dau nhot xe may" in raw_n or (
        "dau nhot" in raw_n and "xe may" in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MOTORBIKE_OIL"
        entities["stain_type"] = "dau nhot xe may"
    elif any(k in user_message for k in ("카레", "강황")) or "ca ri" in raw_n or "curry" in raw_n or "turmeric" in raw_n or "bot nghe" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_CURRY"
        entities["stain_type"] = "ca ri nghe"
    elif any(k in user_message for k in ("유성펜", "유성 매직", "매직펜", "영구마커")) or "permanent marker" in raw_n or "but long" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_INK_PERMANENT"
        entities["stain_type"] = "but long"
    elif any(k in user_message for k in ("볼펜", "잉크")) or "muc but" in raw_n or "pen ink" in raw_n or (
        "ink" in raw_n and "permanent" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_INK_PEN"
        entities["stain_type"] = "muc but bi"
    elif any(k in user_message for k in ("녹물", "녹슨", "녹 얼룩", "녹제거", "녹 빼", "녹빼")) or "ri set" in raw_n or "rust" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_RUST"
        entities["stain_type"] = "ri set"
    elif any(k in user_message for k in ("겨드랑이", "암내", "누런 겨드랑이")) or "ve o nach" in raw_n or "armpit" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SWEAT_YELLOW"
        entities["stain_type"] = "ve o nach"
    elif any(k in user_message for k in ("풀로", "풀 이염", "전분 이염")) or (
        "tinh bot" in raw_n and ("mau lan" in raw_n or "lo mau" in raw_n)
    ) or ("starch" in raw_n and ("dye" in raw_n or "bleed" in raw_n)):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_STARCH_TRANSFER"
        entities["stain_type"] = "ho tinh bot mau lan"
    elif any(
        k in user_message for k in ("이염", "물든", "물이 든", "색이염", "이염된")
    ) or "dye transfer" in raw_n or "mau lan" in raw_n or "lo mau" in raw_n or "color bleed" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_DYE_TRANSFER"
        entities["stain_type"] = "mau lan"
    elif any(k in user_message for k in ("향수",)) or "nuoc hoa" in raw_n or "perfume" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_PERFUME"
        entities["stain_type"] = "nuoc hoa"
    elif any(k in user_message for k in ("데오드란트", "땀억제제", "데오 ")) or "khu mui" in raw_n or "deodorant" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_DEODORANT"
        entities["stain_type"] = "vet khu mui"
    elif any(
        k in user_message
        for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠")
    ) and any(
        k in user_message
        for k in ("누렇", "황변", "노랗", "누래", "변색", "노란", "누래짐", "누래졌")
    ) and not any(k in user_message for k in ("향수", "데오", "데오드란트")):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SHIRT_YELLOW"
        entities["stain_type"] = "ao so mi vang"
        entities.pop("item_id", None)
    elif any(k in user_message for k in ("누렇게", "황변", "변색", "누래짐")) and any(
        k in user_message for k in ("셔츠", "와이", "흰옷", "흰 옷", "흰티", "흰 티")
    ) and not any(k in user_message for k in ("향수", "데오", "데오드란트")):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SHIRT_YELLOW"
        entities["stain_type"] = "ao so mi vang"
        entities.pop("item_id", None)
    elif any(k in user_message for k in ("황변 제거", "황변빼", "황변 빼", "누래짐 제거")) and not any(
        k in user_message for k in ("향수", "데오", "데오드란트")
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SHIRT_YELLOW"
        entities["stain_type"] = "ao so mi vang"
        entities.pop("item_id", None)
    # Generic dress-shirt wash (no yellowing) → item care, NOT yellowing SOP
    elif (
        any(k in user_message for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠"))
        or "ao so mi" in raw_n
        or "dress shirt" in raw_n
    ) and any(
        k in user_message for k in ("세탁", "빨래", "방법", "관리", "어떻게", "다림질", "풀")
    ) and not any(
        k in user_message
        for k in (
            "이염", "혈액", "커피", "김치", "잉크", "곰팡이", "기름", "케첩",
            "누렇", "황변", "노랗", "누래", "변색", "노란", "핏자국", "피 묻",
        )
    ):
        entities["intent"] = "treatment"
        entities["item_id"] = "I_DRESS_SHIRT"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
        entities["fabric_type"] = entities.get("fabric_type") or "cotton"
    elif any(
        k in user_message
        for k in ("우레탄 커튼", "비닐 커튼", "샤워커튼", "샤워 커튼", "우레탄커튼", "비닐커튼")
    ) or "urethane" in raw_n or "shower curtain" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_CURTAIN_URETHANE"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("커튼",)) and any(
        k in user_message for k in ("세탁", "빨래", "방법", "관리", "어떻게", "청소")
    ):
        entities["intent"] = "treatment"
        entities["item_id"] = "I_CURTAIN_FABRIC"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("구스이불", "거위털이불", "다운이불", "오리털이불")) or "goose duvet" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_DUVET_GOOSE"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("솜이불", "폴리이불")) or (
        "이불" in user_message and any(k in user_message for k in ("세탁", "빨래", "방법", "어떻게"))
        and not any(k in user_message for k in ("구스", "거위", "다운", "오리털"))
    ):
        entities["intent"] = "treatment"
        entities["item_id"] = "I_DUVET_COTTON"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("시트", "침대시트", "매트리스커버")) or "ga giuong" in raw_n or "bed sheet" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_BED_SHEET"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("수건", "타월", "목욕타월")) or "khan tam" in raw_n or "towel" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_TOWEL"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("아기옷", "유아복", "신생아옷", "아기 옷")) or "do em be" in raw_n or "baby clothes" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_BABY_WEAR"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("수영복", "래시가드")) or "do boi" in raw_n or "swimwear" in raw_n or "swimsuit" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_SWIMWEAR"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("담배냄새", "담배 냄새", "연기냄새")) or "mui thuoc" in raw_n or "cigarette" in raw_n or "smoke odor" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_ODOR_SMOKE"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("케어라벨", "세탁표시", "세탁 기호", "세탁기호", "케어 라벨")) or "care label" in raw_n or "washing symbol" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_CARE_LABEL"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("드라이클리닝", "드라이 클리닝", "물세탁인가", "드라이인가", "드라이로 보내")) or "dry clean" in raw_n or "dry-clean" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_DRY_VS_WET"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("접수", "체크인", "사진 동의", "견적 말하는법", "접수 스크립트")) or "check-in" in raw_n or "intake" in raw_n or "tiep nhan" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_INTAKE_SCRIPT"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("경수", "센물", "수돗물", "물때")) or "hard water" in raw_n or "nuoc cung" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_WATER_HARDNESS"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("세탁기 코스", "세탁기 설정", "건조기 설정", "건조기 코스")) or "washer" in raw_n or "dryer" in raw_n:
        entities["intent"] = "treatment"
        entities["item_id"] = "I_MACHINE_PROFILE"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("선크림", "자외선차단", "자외선 차단")) or "kem chong nang" in raw_n or "sunscreen" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SUNSCREEN"
        entities["stain_type"] = "kem chong nang"
    elif any(k in user_message for k in ("타르", "아스팔트")) or "nhua duong" in raw_n or "tar" in raw_n or "asphalt" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_TAR"
        entities["stain_type"] = "nhua duong"
    elif any(k in user_message for k in ("마스카라",)) or "mascara" in raw_n or "masca" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MASCARA"
        entities["stain_type"] = "mascara"
    elif any(k in user_message for k in ("염색약", "염모제", "헤어염색")) or "thuoc nhuom" in raw_n or "hair dye" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_HAIR_DYE"
        entities["stain_type"] = "thuoc nhuom toc"
    elif any(k in user_message for k in ("야구모자", "볼캡")) or (
        any(k in user_message for k in ("모자", "캡")) and any(k in user_message for k in ("세탁", "빨래", "빨", "청소", "방법", "어떻게"))
        and "골프" not in user_message
    ):
        entities["intent"] = "treatment"
        entities["item_id"] = "I_HAT_CAP"
        entities["stain_id"] = ""
        entities["stain_type"] = ""
    elif any(k in user_message for k in ("목때", "칼라때", "깃때")) or "vong co" in raw_n or "collar stain" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_COLLAR_STAIN"
        entities["stain_type"] = "vong co"
        entities.pop("item_id", None)
    elif any(k in user_message for k in ("곰팡이", "곰팡")) or "nam moc" in raw_n or "mildew" in raw_n or "mold" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MILDEW"
        entities["stain_type"] = "nam moc"
    elif any(k in user_message for k in ("립스틱", "립스틱자국", "립스틱 자국")) or "lipstick" in raw_n or "son moi" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_LIPSTICK"
        entities["stain_type"] = "son moi"
    elif any(
        k in user_message for k in ("파운데이션", "쿠션", "BB크림", "비비크림", "비비")
    ) or "foundation" in raw_n or "kem nen" in raw_n or "cushion" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_FOUNDATION"
        entities["stain_type"] = "kem nen"
    elif any(k in user_message for k in ("화장품", "메이크업")) or "makeup" in raw_n or "trang diem" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_LIPSTICK"
        entities["stain_type"] = "son moi"
    elif any(k in user_message for k in ("케첩", "켓찹", "케찹")) or "ketchup" in raw_n or "tuong ca" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_KETCHUP"
        entities["stain_type"] = "ketchup"
    elif any(k in user_message for k in ("마요네즈", "마요")) or "mayonnaise" in raw_n or "mayo" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MAYO"
        entities["stain_type"] = "mayonnaise"
    elif any(k in user_message for k in ("느억맘", "느억맘", "액젓", "피시소스", "뉴억맘")) or "nuoc mam" in raw_n or "fish sauce" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_FISH_SAUCE"
        entities["stain_type"] = "nuoc mam"
    elif any(k in user_message for k in ("간장",)) or "nuoc tuong" in raw_n or "soy sauce" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SOY_SAUCE"
        entities["stain_type"] = "nuoc tuong"
    elif any(k in user_message for k in ("분유",)) or "sua cong thuc" in raw_n or "baby formula" in raw_n or "infant formula" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_BABY_FORMULA"
        entities["stain_type"] = "sua cong thuc"
    elif any(
        k in user_message for k in ("구토", "구토물", "토물", "토사물", "토한")
    ) or (
        "토" in user_message
        and any(k in user_message for k in ("얼룩", "묻", "쏟", "세탁"))
        and "토마토" not in user_message
    ) or "vomit" in raw_n or "chat non" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_VOMIT"
        entities["stain_type"] = "chat non"
    elif any(k in user_message for k in ("소변", "오줌", "요산")) or "nuoc tieu" in raw_n or "urine" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_URINE"
        entities["stain_type"] = "nuoc tieu"
    elif any(k in user_message for k in ("대변", "분변", "똥 묻", "똥얼룩")) or "feces" in raw_n or "faeces" in raw_n or (
        (" phan" in f" {raw_n}" or raw_n.startswith("phan") or "phan " in raw_n)
        and "phan mem" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_FECES"
        entities["stain_type"] = "phan"
    elif any(k in user_message for k in ("핏자국", "혈액", "피 묻", "피얼룩")) or "mau tuoi" in raw_n or "mau kho" in raw_n or (
        "blood" in raw_n and "bleed" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_BLOOD_DRY" if any(
            k in user_message for k in ("마른", "굳은", "오래된")
        ) or "mau kho" in raw_n or "dried" in raw_n else "S_BLOOD_FRESH"
        entities["stain_type"] = "mau"
    elif any(k in user_message for k in ("엔진오일", "기계유", "모터오일")) or "engine oil" in raw_n or "dau dong co" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_ENGINE_OIL"
        entities["stain_type"] = "dau dong co"
    elif any(k in user_message for k in ("구두약", "슈폴리시", "슈 폴리시")) or "shoe polish" in raw_n or "xi giay" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SHOE_POLISH"
        entities["stain_type"] = "xi giay"
    elif "버터" in user_message or "butter" in raw_n or "vet bo" in raw_n or "mo bo" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_BUTTER"
        entities["stain_type"] = "bo"
    elif any(k in user_message for k in ("식용유", "식용 오일")) or "dau an" in raw_n or "cooking oil" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_COOKING_OIL"
        entities["stain_type"] = "dau an"
    elif any(k in user_message for k in ("기름때", "그리즈")) or (
        ("기름" in user_message or "오일" in user_message)
        and not any(k in user_message for k in ("오토바이", "엔진", "기계"))
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_COOKING_OIL"
        entities["stain_type"] = "dau an"
    elif any(
        k in user_message
        for k in ("주스", "쥬스", "과일즙", "과즙")
    ) or "juice" in raw_n or "nuoc trai cay" in raw_n or "nuoc ep" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_FRUIT_JUICE"
        entities["stain_type"] = "nuoc trai cay"
        if any(k in user_message for k in ("흰", "화이트", "하얀")) or "trang" in raw_n or "white" in raw_n:
            entities["fabric_type"] = entities.get("fabric_type") or "cotton"
    elif any(k in user_message for k in ("김치", "김치국", "김치찌")) or "kimchi" in raw_n or "kim chi" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_KIMCHI"
        entities["stain_type"] = "kim chi"
    elif any(k in user_message for k in ("버블티", "밀크티", "타피오카", "버블 티")) or "bubble tea" in raw_n or "tra sua" in raw_n or "boba" in raw_n or "milk tea" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_BUBBLE_TEA"
        entities["stain_type"] = "tra sua tran chau"
        entities.pop("item_id", None)
    elif any(k in user_message for k in ("화이트와인", "화이트 와인", "맥주", "백포도주")) or "ruou vang trang" in raw_n or "white wine" in raw_n or (
        " bia" in f" {raw_n}" or raw_n.startswith("bia") or "beer" in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_WHITE_WINE_BEER"
        entities["stain_type"] = "ruou vang trang"
    elif any(
        k in user_message
        for k in ("레드와인", "레드 와인", "적포도주", "와인", "포도주", "와인얼룩")
    ) or "ruou vang do" in raw_n or "ruou vang" in raw_n or "red wine" in raw_n or (
        " wine" in f" {raw_n}" or raw_n.startswith("wine") or raw_n.endswith(" wine") or raw_n == "wine"
    ):
        # Bare "와인"/wine → red wine SOP (most common laundry ask); white already handled above
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_RED_WINE"
        entities["stain_type"] = "ruou vang do"
    elif any(k in user_message for k in ("콜라", "사이다", "탄산음료", "탄산")) or "nuoc ngot" in raw_n or "soft drink" in raw_n or "cola" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SOFT_DRINK"
        entities["stain_type"] = "nuoc ngot"
    elif any(k in user_message for k in ("녹차", "홍차", "우롱차", "차 얼룩", "찻물")) or (
        ("차" in user_message and any(k in user_message for k in ("묻", "얼룩", "쏟", "세탁")))
    ) or (("tra " in raw_n or raw_n.startswith("tra") or " tea" in f" {raw_n}" or raw_n.endswith(" tea")) and "ca phe" not in raw_n):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_TEA"
        entities["stain_type"] = "nuoc tra"
    elif any(k in user_message for k in ("초콜릿", "초코")) or "socola" in raw_n or "chocolate" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_CHOCOLATE"
        entities["stain_type"] = "socola"
    elif any(k in user_message for k in ("BBQ", "바베큐", "바비큐")) or "sot bbq" in raw_n or "bbq sauce" in raw_n or "barbecue" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_BBQ_SAUCE"
        entities["stain_type"] = "sot BBQ"
    elif any(k in user_message for k in ("머스터드", "겨자")) or "mu-ta-det" in raw_n or "mustard" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MUSTARD"
        entities["stain_type"] = "mu-ta-det"
    elif any(k in user_message for k in ("껌", "풍선껌")) or "keo cao su" in raw_n or "chewing gum" in raw_n or (
        "gum" in raw_n and "glue" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_GUM"
        entities["stain_type"] = "keo cao su"
    elif any(k in user_message for k in ("접착제", "본드", "풀칠")) or "keo dan" in raw_n or (
        "glue" in raw_n and "chewing" not in raw_n
    ) or ("adhesive" in raw_n):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_GLUE"
        entities["stain_type"] = "keo dan"
    elif any(k in user_message for k in ("촛농", "양초", "촛물")) or "sap nen" in raw_n or "candle wax" in raw_n or (
        "wax" in raw_n and "polish" not in raw_n and "ear" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_CANDLE_WAX"
        entities["stain_type"] = "sap nen"
    elif any(k in user_message for k in ("매니큐어", "네일폴리시", "네일 ")) or "son mong" in raw_n or "nail polish" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_NAIL_POLISH"
        entities["stain_type"] = "son mong"
    elif any(k in user_message for k in ("페인트", "수성페인트", "수성 페인트")) or "son nuoc" in raw_n or "latex paint" in raw_n or (
        "paint" in raw_n and "nail" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_PAINT_LATEX"
        entities["stain_type"] = "son nuoc"
    elif any(k in user_message for k in ("잔디", "풀물", "풀 얼룩")) or "co xanh" in raw_n or "grass stain" in raw_n or (
        "grass" in raw_n and "grease" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_GRASS"
        entities["stain_type"] = "co xanh"
    elif any(k in user_message for k in ("진흙", "흙탕", "진흙물")) or "bun dat" in raw_n or "mud" in raw_n or (
        " bun" in f" {raw_n}" or raw_n.startswith("bun")
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MUD"
        entities["stain_type"] = "bun dat"
        if any(k in user_message for k in ("적토", "라테라이트", "붉은 흙")) or "laterite" in raw_n or "dat do" in raw_n:
            entities["stain_id"] = "S_LATERITE"
            entities["stain_type"] = "dat do"
    elif any(k in user_message for k in ("땀냄새", "땀 묻", "땀얼룩", "땀 얼룩")) or (
        "땀" in user_message
        and not any(k in user_message for k in ("겨드랑", "누렇", "황변", "데오"))
    ) or "mo hoi tuoi" in raw_n or ("sweat" in raw_n and "yellow" not in raw_n and "armpit" not in raw_n):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SWEAT_FRESH"
        entities["stain_type"] = "mo hoi tuoi"
    elif any(k in user_message for k in ("계란", "달걀")) or "trung ga" in raw_n or "long trang" in raw_n or (
        "egg" in raw_n and "eggplant" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_EGG"
        entities["stain_type"] = "trung"
    elif (
        any(k in user_message for k in ("우유 얼룩", "우유묻", "우유 묻", "우유자국"))
        or (
            "우유" in user_message
            and any(k in user_message for k in ("얼룩", "묻", "쏟", "세탁"))
            and "커피" not in user_message
            and "분유" not in user_message
        )
        or (
            ("sua " in raw_n or raw_n.startswith("sua") or " milk" in f" {raw_n}" or raw_n.endswith(" milk") or raw_n == "milk")
            and "ca phe" not in raw_n
            and "cong thuc" not in raw_n
            and "formula" not in raw_n
            and "coffee" not in raw_n
        )
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MILK"
        entities["stain_type"] = "sua"
    elif any(
        k in user_message
        for k in ("라떼", "우유커피", "카페라떼", "카푸치노", "밀크커피")
    ) or "latte" in raw_n or "ca phe sua" in raw_n or "milk coffee" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MILK_COFFEE"
        entities["stain_type"] = "ca phe sua"
    elif any(k in user_message for k in ("커피", "아메리카노")) or "ca phe" in raw_n or "coffee" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_BLACK_COFFEE"
        entities["stain_type"] = "ca phe den"
    graph_context = _fetch_graph_context(entities)
    graph_data = graph_context.get("graph")

    if not graph_data or graph_data == {} or graph_data == []:
        return _empty_graph_reply(entities)

    return _answer_with_optional_cache(user_message, entities, graph_context)
