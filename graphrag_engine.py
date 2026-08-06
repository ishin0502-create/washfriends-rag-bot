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
    .id, .name_vi, .name_ko, .use_for_vi
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
    .motion_vi, .water_temp_vi, .aftercare_vi, .fabric_id
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
    .id, .name_vi, .name_ko, .use_for_vi
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
                context["graph"] = _apply_delicate_s1_fallback(
                    _apply_fabric_chem_safety(context["graph"])
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
        context["graph"] = _apply_delicate_s1_fallback(
            _apply_fabric_chem_safety(context["graph"])
        )

    # Item care (shoes/bags/gore-tex/down/leather) — same 1)-6) fields as stains
    item_id = entities.get("item_id")
    if item_id:
        item_rows = _run_query(Q_ITEM_CONTEXT, {"item_id": item_id})
        if item_rows:
            context = _merge_item_into_context(context, item_rows[0])
            if isinstance(context.get("graph"), dict):
                context["graph"] = _apply_delicate_s1_fallback(
                    _apply_fabric_chem_safety(context["graph"])
                )

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
            "tip": ic.get("why_vi"),
            "urgency": "care",
            "precheck_vi": ic.get("precheck_vi"),
            "why_vi": ic.get("why_vi"),
            "fresh_path_vi": ic.get("fresh_path_vi"),
            "dried_path_vi": ic.get("dried_path_vi"),
            "motion_vi": ic.get("motion_vi"),
            "water_temp_vi": ic.get("water_temp_vi"),
            "aftercare_vi": ic.get("aftercare_vi"),
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
    ):
        if ic.get(key):
            sc[key] = ic[key]
    if ic.get("why_vi"):
        sc["tip"] = ic.get("why_vi")
    g["stain_context"] = sc
    # Prefer item tools/chems for specialty garments
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
        "use_for_vi": "Vua/lon: khong dung but — chuyen nhuom / boi thuong",
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
    if not fabric:
        return graph

    fid = str(fabric.get("id") or "").upper()
    fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''}".lower()
    is_silk = fid == "F4" or "silk" in fname or "lua" in fname or "lụa" in fname
    is_wool = fid == "F3" or "wool" in fname or " len" in f" {fname}" or fname.strip() == "len"
    is_leather = fid == "F8" or "leather" in fname or ("da (" in fname) or fname.strip() == "da"
    is_suede = fid == "F9" or "suede" in fname or "nubuck" in fname or "da lon" in fname
    is_fur = fid == "F10" or "fur" in fname or "long thu" in fname
    delicate = is_silk or is_wool or is_leather or is_suede or is_fur

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
    """Internal code → owner everyday name (KO/VI)."""
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
        "A3": "giam trang 5%",
        "A4": "oxy gia 3%",
        "A5": "ammonia pha loang",
        "N1": "baking soda",
        "N2": "muoi an",
        "N3": "bot ngo / phan rom",
        "S1": "nuoc giat trung tinh Wash Friends",
        "WF_SOFT": "nuoc xa Wash Friends",
        "WF_FRAG": "xit huong Wash Friends",
        "X1": "bot tay khu (sodium hydrosulfite) — chi cotton/linen TRANG",
        "X2": "acid oxalic — ri set / dat do (gang tay)",
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
    Expand chem codes inside path/why text to everyday names.
    """
    if not isinstance(graph, dict):
        return graph
    g = dict(graph)

    def _tool(t: dict) -> dict:
        out = {
            "name_ko": t.get("name_ko"),
            "name_vi": t.get("name_vi"),
            "use_for_vi": t.get("use_for_vi"),
        }
        if lang == "ko":
            out.pop("name_vi", None)
            out.pop("use_for_vi", None)
        elif lang == "vi":
            out.pop("name_ko", None)
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
        # Expand any leftover codes inside alt/role strings
        for k in list(keep.keys()):
            if isinstance(keep[k], str):
                keep[k] = _expand_chem_codes_in_text(keep[k], lang=lang)
        if lang == "ko":
            for k in ("name_vi", "shop_name_vi", "buy_where_vi", "alt1_vi", "alt2_vi", "alt3_vi",
                      "when_use_vi", "dilution_vi", "example_brands_vi"):
                keep.pop(k, None)
        elif lang == "vi":
            keep.pop("name_ko", None)
            keep.pop("buy_where_ko", None)
            keep.pop("dilution_ko", None)
            keep.pop("alt1_ko", None)
            keep.pop("alt2_ko", None)
            keep.pop("alt3_ko", None)
        return {k: v for k, v in keep.items() if v is not None and v != ""}

    # Expand codes in narrative fields BEFORE LLM sees them
    sc = g.get("stain_context")
    if isinstance(sc, dict):
        sc2 = dict(sc)
        for field in (
            "tip", "why_vi", "fresh_path_vi", "dried_path_vi",
            "precheck_vi", "motion_vi", "water_temp_vi", "aftercare_vi",
            "group_care_order_vi", "group_care_order_ko",
            "force_metaphor_vi", "force_metaphor_ko",
            "sense_check_vi", "sense_check_ko",
            "success_rate_vi", "success_rate_ko",
            "refuse_when_vi", "refuse_when_ko",
        ):
            if sc2.get(field):
                sc2[field] = _expand_chem_codes_in_text(str(sc2[field]), lang=lang)
        g["stain_context"] = sc2

    ic = g.get("item_context")
    if isinstance(ic, dict):
        ic2 = dict(ic)
        for field in (
            "why_vi", "fresh_path_vi", "dried_path_vi",
            "precheck_vi", "motion_vi", "water_temp_vi", "aftercare_vi",
        ):
            if ic2.get(field):
                ic2[field] = _expand_chem_codes_in_text(str(ic2[field]), lang=lang)
        g["item_context"] = ic2

    if g.get("tools"):
        g["tools"] = [_tool(t) for t in g["tools"] if t]
    if g.get("chemicals"):
        g["chemicals"] = [_chem(c) for c in g["chemicals"] if c]
    if g.get("washfriends_supply"):
        g["washfriends_supply"] = [_chem(c) for c in g["washfriends_supply"] if c]
    return g


# ─── LLM Responder ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là chuyên gia giặt ủi của Wash Friends Vietnam.
Đối tượng: CHỦ CỬA HÀNG nhượng quyền (đồng nghiệp) — không phải khách lẻ.
Giọng điệu: kinh nghiệm nội bộ Wash Friends — tự tin, dễ đọc, cụ thể như hướng dẫn kỹ thuật tại cửa hàng.

QUY TẮC TRẢ LỜI:
1. NGÔN NGỮ BẮT BUỘC: trả lời ĐÚNG ngôn ngữ câu hỏi.
   - Câu hỏi tiếng Hàn → CHỈ tiếng Hàn (không xen Việt/Anh). Câu hỏi tiếng Việt → CHỈ tiếng Việt.
   - Tiếng Hàn: tools.name_ko; hóa chất name_ko. CẤM in name_vi, id dụng cụ (T_CLOTH…), mã hóa chất.
2. CHỈ dùng DỮ LIỆU TỪ ĐỒ THỊ của ĐÚNG vết này — không bịa, không mẹo dân gian, không lẫn vết khác.
   Thiếu field → bỏ qua hoặc hỏi 1 câu. CẤM in tên field kỹ thuật (why_vi, fresh_path_vi, code, id…).
3. Cảnh báo an toàn ĐẦU câu — chữ thường/hoa ngắn, CẤM markdown ** ## * _
4. Mở đầu BẮT BUỘC khối [왜 이 순서] / [Tại sao thứ tự này] (2–5 câu) từ why_vi / tip — nguyên tắc hóa học ĐÚNG vết này (GIAO DUC). Không bỏ khối này khi có why/tip.
5. Sau đó khối XỬ LÝ — 1)-6) (stain và item_care cùng format):
   (1) Nhận diện: BẮT BUỘC nêu ĐÚNG loại vết từ stain_context (name_ko/name_vi) + tươi/khô + màu vải nếu user nói
       (vd: "과일 주스, 젖은 상태, 흰 면"). CẤM câu mơ hồ kiểu "균일하게 분포/분류입니다" khi không có trong đồ thị.
   (2) Dụng cụ — chỉ tên người dùng (name_ko / name_vi), CẤM id T_…
       Nếu tools[] RỖNG: viết "해당 없음" / "khong can dung cu dac biet" HOẶC lấy từ fresh_path
       (vd bút màu vải, chụp ảnh) — CẤM bịa "흰 천·흡수지" khi không có trong tools[]
   (3) Lực + hướng — Cap 1–4 + 비유감각 nếu có force_levels / force_metaphor_* (Hàn: 아기 얼굴·안경 닦기·수세미 등). Cụ thể thấm/nhấn ngoài→trong.
   (4) Hóa chất — BẮT BUỘC ghi TÊN THƯỜNG NGÀY từ chemicals[] (name_ko / shop_name_vi):
       muối, enzyme, giấm, nước rửa chén, bột tẩy oxy, nước giặt trung tính Wash Friends…
       Kèm: pha loãng (dilution_*), nơi mua (buy_where_*), thay thế nếu có (alt*).
       Nêu rõ từng bước + thời gian ngâm nếu có trong fresh_path / dilution.
       CẤM để trống kiểu "를 1리터" / "cho X vào…" mà không nói X là gì.
       CẤM mã nội bộ. CẤM mẹo dân gian (kem đánh răng, cafe/trà nhuộm…).
       Chỉ trộn 2 chất khi fresh_path / dilution ghi rõ tỷ lệ; còn lại xử lý tuần tự + xả.
   (5) Nhiệt độ nước + max_temp vải
   (6) Sau xử lý: đủ ý kiểm tra ánh sáng / còn thì làm lại (đúng thứ tự hóa chất) / phơi bóng mát — CẤM câu kết kiểu quảng cáo "최상의 결과"
   Nếu có item_context: đây là chăm sóc món (giày/túi/áo phao/Gore-Tex…) — vẫn dùng 1)-6), không đổi giọng.
5b. SAU 1)-6) BẮT BUỘC thêm 3 khối ngắn (plain text, không markdown):
   [감각 체크] / [Kiểm tra giác quan]: mắt/tay/mũi từ sense_check_* hoặc suy từ fresh_path (vd nước trong, hết nhờn, hết mùi).
   [성공률·고지] / [Tỷ lệ & báo khách]: success_rate_* hoặc "không cam kết 100%; nhiệt/sấy khi còn vết = cố định".
   [거절·보내기] / [Từ chối / chuyển]: refuse_when_* hoặc khi lụa/len/da hỏng cấu trúc / không đủ máy — nói rõ chuyển chuyên hoặc từ chối.
5c. CẤM bỏ [왜]/[감각]/[성공률]/[거절] chỉ vì muốn ngắn. Tối đa vẫn 900 từ — cắt phần lan man, không cắt khối giáo dục.6. KHÔNG tự chèn WF_SOFT / WF_FRAG. S1 chỉ khi có trong chemicals[] (lụa/len hoặc đã gắn).
7. CẤM mẹo dân gian, thương hiệu ngoài, viện/web/AI/PDF
8. Không markdown **, ##, *, _ — Zalo plain text thuần (không in dấu ** quanh tiêu đề)
9. Không trộn tiếng Anh vụng (cấm: external, internal, soft brush…). Lực/hướng viết đủ ngôn ngữ trả lời (Hàn: 바깥→안 / Việt: ngoài→trong)

HÓA CHẤT (bắt buộc):
- Người nghe đã là chủ tiệm: CẤM nói "mua ở tiệm giặt / 세탁소에서 구입".
  Mua ngoài → siêu thị/약국/cửa hóa chất (buy_where_*). Hàng WF → "kho / cung ứng Wash Friends".
- KHÔNG đọc mã nội bộ (A3, B1, E1, S1…) như mã kỹ thuật. Nói tên dùng hàng ngày:
  name_ko (Hàn) hoặc shop_name_vi / name_vi (Việt). Ví dụ: "워시프렌즈 중성세제", "giấm trắng 5%".
- Có thể nhắc tên hàng ngày — tuyệt đối không viết mã S1 / A3 / B1 / E1…
- Da (leather) / suede: CAM máy giặt, CAM tẩy oxy/javel, CAM nhiệt/nắng gắt.
  Da bóng: ít nước + cồn nhẹ (test) + kem dưỡng. Suede: không nước → chải khô / chuyên nghiệp.
- Phục hồi mất màu vải MÀU (I_COLOR_FADE / color_fade_rules):
  BẮT BUỘC chia diện tích trong (1)(2)(3)(4):
  - Nhỏ (<= đồng xu): bút màu vải — nói "임시/다시 빠질 수 있음" (Hàn) / "tam thoi" (Việt). Lực: chấm/칠 ngoài→trong, CẤM "밝혀줍니다".
  - Vừa/lớn: CẤM chỉ bút — chuyển nhuộm / giải thích không khớp 100% / bồi thường.
  (4) chemicals rỗng = "해당 없음" — CẤM detergent. CẤM mẹo: jean mới giặt chung, cafe/trà, muối 10:1, ngâm nóng tự nhuộm.
  (5) Bước phục hồi: không giặt máy/tay để "phục hồi màu". Giặt lật trái + lạnh = duy trì sau, nói rõ nếu nhắc.
  Denim bạc màu do mặc+UV: giải thích đặc trưng, không gọi lỗi giặt nếu đã báo.
- Pha loãng: CHỈ dùng dilution_ko (Hàn) hoặc dilution_vi (Việt) nếu có.
  Không có dilution_* → "병 라벨·본사 안내 따름" / "theo hướng dẫn trên chai / kho WF" — CẤM bịa tỷ lệ (vd 1:4 cho S1).
  Hàn tự nhiên: "식초 1 : 물 4". Việt: "1 phần giấm + 4 phần nước". CẤM "1부분…4부분".
- THỨ TỰ theo tính chất vết (KHÔNG pha cocktail "detergent A+B+C" kiểu 2:1:1 / 1:2:1):
  Protein → nước lạnh + enzyme (nếu vải cho). Dầu → hút bột rồi surfactant. Tannin/màu → acid nhẹ rồi oxy (nếu vải cho).
  Vết phức hợp: làm TỪNG BƯỚC theo fresh_path / care_order nhóm, XẢ giữa bước — không đổ chung một chậu.
  Chỉ dùng paste tỷ lệ khi ĐỒ THỊ / fresh_path ghi rõ; còn lại CẤM bịa tỷ lệ trộn.
  Test góc khuất trước khi xử lý cả món. Tuyệt đối không trộn chất trong never_mix_alerts (vd ammonia + javel).
- B1 = thuốc tẩy oxy (KHÔNG phải "세제 axit"). A3 = giấm / axit nhẹ.
- can_bleach=false → CẤM Javel/chlorine (B2). Polyester/linen/denim vẫn có thể dùng tẩy oxy (B1) nếu B1 còn trong chemicals[] (test góc; denim màu có thể phai nhẹ).
- Vải lụa/len/rayon/da/suede/fur HOẶC chemical.safe_on_silk/safe_on_wool = false HOẶC fabric enzyme_safe/acid_safe = false HOẶC can_oxygen=false:
  → KHÔNG khuyến nghị hóa chất không an toàn (kể cả B1/A4 trên lụa/len/da).
  → Chỉ dùng S1 nếu S1 có trong chemicals[]. Không bịa S1 khi chemicals[] rỗng vì lý do khác (vd phục hồi màu).
  → Nếu chỉ còn cảnh báo: nói rõ "không dùng trên lụa/len" thay vì vẫn bảo dùng.
- Nếu có chemicals_blocked_for_fabric / delicate_chem_rule: tuân thủ tuyệt đối — không lấy bước tẩy/axit/enzyme từ tip nếu đã bị chặn.

CẤP LỰC: Cap1 Rat nhe | Cap2 Nhe | Cap3 Vua | Cap4 Manh
Tối đa 900 từ."""


def detect_reply_lang(text: str) -> str:
    """Detect reply language from user text. Korean Hangul wins; else Vietnamese default."""
    if not text:
        return "vi"
    if re.search(r"[가-힣]", text):
        return "ko"
    # Latin/ASCII-only short messages → still default vi for franchise VN
    return "vi"


def _enrich_teach_slots(graph: dict) -> dict:
    """Fill Protocol Card teach slots from stain fields or group fallbacks (additive)."""
    if not isinstance(graph, dict):
        return graph
    g = dict(graph)
    sc = dict(g.get("stain_context") or {})
    if not sc:
        return g
    group = ""
    grp = sc.get("group_id") or sc.get("group")
    if isinstance(grp, dict):
        group = str(grp.get("id") or "")
    elif isinstance(grp, str):
        group = grp
    # Infer group from stain id prefix lists if missing
    sid = str(sc.get("id") or "")
    if not group:
        if sid.startswith("S_"):
            # light heuristic from known protein/oil markers in tip flags — skip
            pass
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
            "sense_check_ko": "눈·코·강광 확인 후 건조.",
            "success_rate_vi": "Phuc tap: bao khoi phuc 100% — ghi nhan anh truoc/sau.",
            "success_rate_ko": "복합 오염: 100% 복원 비보장 — 전후 사진.",
            "refuse_when_vi": "Da/suede moc; thiet bi khong du (chan lon) → chuyen/tu choi.",
            "refuse_when_ko": "가죽 곰팡이, 대형 이불 설비 부족 → 전문/거절.",
        },
    }
    # Map stain id → group when group missing
    gid = group if group in fb else ""
    if not gid:
        # use contains flags if present on sc
        if sc.get("contains_protein") and not sc.get("contains_tannin") and not sc.get("contains_oil"):
            gid = "G1"
        elif sc.get("contains_oil") and not sc.get("contains_protein"):
            gid = "G2"
        elif sc.get("contains_tannin"):
            gid = "G3"
        elif sc.get("contains_dye") and not sc.get("contains_oil"):
            gid = "G4"
        else:
            gid = "G5"
    card = fb.get(gid) or fb["G5"]
    for k, v in card.items():
        if not sc.get(k):
            sc[k] = v
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
            "수신 대상은 워시프렌즈 점주(동료). 본문에 '청자'/'청자 여러분' 쓰지 말 것. "
            "한국어만(베트남어·영어 금지). 마크다운(** ## *) 금지. "
            "힘·방향은 '바깥→안'처럼 한국어만 (external/internal 금지). "
            "약품은 name_ko·일상명만 (A3/B1/S1 코드 말하지 말 것). "
            "도구는 name_ko만 — T_CLOTH 같은 id, name_vi 출력 금지. "
            "tools[]가 비면: '해당 없음' 또는 fresh_path의 도구(천용 컬러펜 등). 흰 천을 지어내지 말 것. "
            "chemicals[]가 비면: 중성세제/세제로 칸 채우지 말 것. fresh_path대로 "
            "(색바램=면적 분기: 소=천용 컬러펜 임시·바깥→안 '칠/찍기'(밝혀줍니다 금지); "
            "중·대=재염색·100% 불일치 고지·보상. 매장 세제로 색 복원 금지. "
            "새 청바지 같이 빨기·커피/차·소금물 고착·열탕 자가염색 금지). "
            "수온(5): 복원 단계에서는 세탁·열탕으로 색을 되살리지 말 것. "
            "뒤집기+찬물 단독은 '유지'일 때만 짧게. "
            "희석은 dilution_ko만: '식초 1 : 물 4' 형식. '1부분' 금지. "
            "'세탁소에서 구입' 금지 — 슈퍼/약국/화공, WF는 본사·창고 공급. "
            "실크·울이고 chemicals[]에 중성세제가 있을 때만 중성세제 사용. "
            "B1=산소계 표백제(산성 세제 아님). "
            "can_bleach=false → 염소(락스)만 금지. 폴리·린넨은 chemicals[]에 산소표백이 있으면 구석 테스트 후 사용 가능. "
            "실크·울·레이온·가죽에는 산소표백/과산화수소 금지. "
            "why/신선·굳음 내용만 쓰고 필드명 출력 금지. 민간요법·다른 오염법 금지. "
            "(4)약품: chemicals[]의 name_ko를 반드시 이름 그대로 쓸 것 "
            "(소금·효소세제·식초·주방세제·산소계 표백제·워시프렌즈 중성세제 등). "
            "희석(dilution_ko)·구매처(buy_where_ko)·대체(alt*_ko) 있으면 함께. "
            "'를 1리터'처럼 약품명 빠진 문장 금지. 민간요법(치약 등) 금지. "
            "혼합 비율은 그래프에 있을 때만; 없으면 순차 처리+헹굼. "
            "필수 교육 형식(빠지면 안 됨, 마크다운 금지): "
            "[왜 이 순서] why/tip 2–5문장 → "
            "(1)오염·원단 (2)도구(name_ko) (3)힘·방향+Cap비유 (4)약품 (5)수온 "
            "(6)후관리: 강한 빛에서 잔존 확인→남으면 재처리(건조 금지), 그늘·통풍 건조 → "
            "[감각 체크] 눈/손/코 → [성공률·고지] 100% 보장 금지·열고착 고지 → "
            "[거절·보내기] 손상·실크/울/가죽·설비 부족 시. "
            "sense_check_*/success_rate_*/refuse_when_*/force_metaphor_* 있으면 그대로 반영. "
            "약 혼합: A/B/C 칵테일 비율(2:1:1 등) 지어내기 금지. 성분별 순차 처리+중간 헹굼. "
            "구석 테스트 후 전체. never_mix는 절대 준수."
        )
    else:
        lang_rule = (
            "Nguoi nhan: chu cua hang Wash Friends (dong nghiep). CHỈ tiếng Việt. "
            "CẤM markdown ** ##. CẤM in chu '청자'. "
            "Lực/hướng: 'ngoài→trong' — không xen English. "
            "Hóa chất: shop_name_vi / tên thường — CẤM mã A3/B1/E1/S1. "
            "tools[] rỗng → 'khong can dung cu dac biet' / theo fresh_path — CẤM bịa khan tham. "
            "chemicals[] rỗng → CẤM bịa nuoc giat trung tinh; theo fresh_path "
            "(phai mau mau: but mau / nhuom / khong phuc hoi bang detergent). "
            "Pha loãng: CHỈ dilution_vi; không có → 'theo hướng dẫn trên chai / kho WF' — không bịa tỷ lệ. "
            "CẤM 'mua ở tiệm giặt' — siêu thị/nhà thuốc/cửa hóa chất; hàng WF = kho cung ứng. "
            "Lụa/len: chỉ dùng S1 nếu có trong chemicals[]. "
            "B1 = tẩy oxy (không gọi chất tẩy axit). "
            "Không in tên field. Không mẹo dân gian. "
            "BẮT BUỘC khối giáo dục plain text: "
            "[Tại sao thứ tự này] why/tip → 1)-6) nhận diện/dụng cụ/lực+Cap/hóa chất/nhiệt độ/"
            "sau xử lý → [Kiểm tra giác quan] mắt/tay/mũi → [Tỷ lệ & báo khách] không cam kết 100% → "
            "[Từ chối / chuyển] khi hỏng cấu trúc hoặc thiếu máy. "
            "Dùng sense_check_*/success_rate_*/refuse_when_*/force_metaphor_* nếu có. "
            "CẤM bịa tỷ lệ trộn detergent A+B+C; xử lý tuần tự theo tính chất + xả giữa bước; test góc."
        )

    return f"""Câu hỏi từ chủ cửa hàng: {user_message}

[DỮ LIỆU ĐỒ THỊ — loại truy vấn: {query_type}]
{graph_json}

{lang_rule}
Chỉ trả lời từ dữ liệu trên (chemicals của vết này, tools, washfriends_supply khi đúng).
Null/thiếu → hỏi thêm hoặc bỏ qua — tuyệt đối không bịa và không lẫn sang vết khác.
Giọng nội bộ Wash Friends — không nêu nguồn bên ngoài."""


def _call_llm(llm_prompt: str, lang: str = "vi") -> str:
    response = _openai.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
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
    """LLM answer with fail-open cache. Skips cache when graph is empty."""
    lang = entities.get("lang") or "vi"
    ctx_key = build_context_key(entities)
    cached = cache_lookup(cache_question, ctx_key)
    if cached:
        return cached

    base_prompt = _build_llm_prompt(cache_question, graph_context, lang=lang)
    llm_prompt = (prefix + "\n\n" + base_prompt) if prefix else base_prompt
    answer = _call_llm(llm_prompt, lang=lang)
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
    elif any(
        k in user_message
        for k in ("와이셔츠", "흰셔츠", "드레스셔츠", "드레스 셔츠")
    ) and any(
        k in user_message
        for k in ("누렇", "황변", "노랗", "누래", "변색", "노란", "누래짐", "누래졌")
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SHIRT_YELLOW"
        entities["stain_type"] = "ao so mi vang"
        entities.pop("item_id", None)
    elif any(k in user_message for k in ("누렇게", "황변", "변색", "누래짐")) and any(
        k in user_message for k in ("셔츠", "와이", "흰옷", "흰 옷", "흰티", "흰 티")
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_SHIRT_YELLOW"
        entities["stain_type"] = "ao so mi vang"
        entities.pop("item_id", None)
    elif any(k in user_message for k in ("황변 제거", "황변빼", "황변 빼", "누래짐 제거")):
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
    elif any(k in user_message for k in ("레드와인", "적포도주")) or "ruou vang do" in raw_n or "red wine" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_RED_WINE"
        entities["stain_type"] = "ruou vang do"
    elif any(k in user_message for k in ("화이트와인", "맥주", "백포도주")) or "ruou vang trang" in raw_n or "white wine" in raw_n or (
        " bia" in f" {raw_n}" or raw_n.startswith("bia") or "beer" in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_WHITE_WINE_BEER"
        entities["stain_type"] = "ruou vang trang"
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
    elif any(k in user_message for k in ("데오드란트", "땀억제제", "데오 ")) or "khu mui" in raw_n or "deodorant" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_DEODORANT"
        entities["stain_type"] = "vet khu mui"
    elif any(k in user_message for k in ("향수",)) or "nuoc hoa" in raw_n or "perfume" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_PERFUME"
        entities["stain_type"] = "nuoc hoa"
    elif any(k in user_message for k in ("계란", "달걀")) or "trung ga" in raw_n or "long trang" in raw_n or (
        "egg" in raw_n and "eggplant" not in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_EGG"
        entities["stain_type"] = "trung"
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
