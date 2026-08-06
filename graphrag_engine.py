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
   OR toLower(coalesce(s.name_vi, '')) CONTAINS toLower($stain_input)
   OR toLower(coalesce(s.name, '')) CONTAINS toLower($stain_input)
   OR toLower(coalesce(s.id, '')) CONTAINS toLower($stain_input)
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
OPTIONAL MATCH (wf:Chemical)
  WHERE wf.wf_supply = true OR wf.code IN ['S1','WF_SOFT','WF_FRAG']
RETURN
  s {
    .id, .name, .name_vi, .tip, .urgency,
    .contains_protein, .contains_tannin, .contains_oil, .contains_dye,
    .water_spreads, .precheck_vi, .motion_vi, .water_temp_vi, .aftercare_vi,
    .why_vi, .fresh_path_vi, .dried_path_vi,
    group: g.name_vi, group_id: g.id,
    group_care_order_vi: g.care_order_vi, group_care_order_ko: g.care_order_ko
  } AS stain_context,
  CASE WHEN f IS NULL THEN null ELSE f {
    .id, .name, .name_vi, .max_temp, .can_bleach, .enzyme_safe, .acid_safe,
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
  COLLECT(DISTINCT wf {
    .code, .name, .name_vi, .name_ko, .role, .shop_name_vi, .buy_where_vi, .buy_where_ko,
    .alt1_vi, .alt2_vi, .when_use_vi, .wf_supply, .dilution_vi, .dilution_ko
  }) AS washfriends_supply,
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
OPTIONAL MATCH (wf:Chemical)
  WHERE wf.wf_supply = true OR wf.code IN ['S1','WF_SOFT','WF_FRAG']
OPTIONAL MATCH (f)-[:NEVER_USE]->(blocked:Chemical)
RETURN
  i {
    .id, .name, .name_vi, .name_ko,
    .precheck_vi, .why_vi, .fresh_path_vi, .dried_path_vi,
    .motion_vi, .water_temp_vi, .aftercare_vi, .fabric_id
  } AS item_context,
  CASE WHEN f IS NULL THEN null ELSE f {
    .id, .name, .name_vi, .max_temp, .can_bleach, .enzyme_safe, .acid_safe,
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
  COLLECT(DISTINCT wf {
    .code, .name, .name_vi, .name_ko, .role, .shop_name_vi, .buy_where_vi, .buy_where_ko,
    .alt1_vi, .alt2_vi, .when_use_vi, .wf_supply, .dilution_vi, .dilution_ko
  }) AS washfriends_supply,
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
    rows = _run_query(Q_STAIN_FALLBACK, {})
    stain_norm = _normalize_text(stain_input)
    if not stain_norm:
        return rows[:5]
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
        # "Can I wash this fur/suit?" must not early-exit as price/safety with empty graph
        if intent in ("price", "safety", "mystery", "browse") and not (
            entities.get("stain_id") or (entities.get("stain_type") or "").strip()
        ):
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
    elif not stain_input and raw_msg:
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
        context["graph"] = _apply_fabric_chem_safety(context["graph"])

    # Item care (shoes/bags/gore-tex/down/leather) — same 1)-6) fields as stains
    item_id = entities.get("item_id")
    if item_id:
        item_rows = _run_query(Q_ITEM_CONTEXT, {"item_id": item_id})
        if item_rows:
            context = _merge_item_into_context(context, item_rows[0])
            if isinstance(context.get("graph"), dict):
                context["graph"] = _apply_fabric_chem_safety(context["graph"])

    return context


def _item_as_stain_shaped(item_graph: dict) -> dict:
    """Map Item fields onto stain_context so existing owner 1)-6) prompt stays unchanged."""
    ic = item_graph.get("item_context") or {}
    item_id = ic.get("id") or ""
    # Real fur / leather golf glove: never surface shop detergents (LLM invents from WF supply)
    no_shop_chem = item_id in {"I_FUR_REAL", "I_GOLF_GLOVE_LEATHER"}
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
        "tools": item_graph.get("tools") or [],
        "washfriends_supply": [] if no_shop_chem else (item_graph.get("washfriends_supply") or []),
        "force_levels": [],
        "fabric_cautions": [],
        "never_use_on_fabric": item_graph.get("never_use_on_fabric") or [],
        "never_mix_alerts": [],
        "climate_context": [],
        "item_context": ic,
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
    if item_graph.get("tools"):
        g["tools"] = item_graph.get("tools")
    if ic.get("id") in {"I_FUR_REAL", "I_GOLF_GLOVE_LEATHER"}:
        g["chemicals"] = []
        g["washfriends_supply"] = []
    elif item_graph.get("chemicals") is not None:
        g["chemicals"] = item_graph.get("chemicals")
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
        if (is_leather or is_suede or is_fur) and code in {"B1", "B2", "A4", "E1", "E2", "E3", "D3", "A3", "A5"}:
            reasons.append("not_safe_on_leather_suede_fur")
        if is_suede and code in {"A1", "D2"}:
            # Suede: avoid wet chemistry by default — professional path
            reasons.append("suede_prefer_dry_pro")
        if is_fur and code in {"A1", "D2", "N1", "S1"}:
            reasons.append("fur_pro_only")
        if fabric.get("can_bleach") is False and code in {"B1", "B2", "A4"}:
            reasons.append("fabric_no_bleach")
        if fabric.get("acid_safe") is False and code in {"A3", "A5"} and not (is_leather or is_suede):
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
            "Chi dung chemicals[] con lai. Neu rong: uu tien washfriends_supply neu phu hop + luc nhe. "
            "Cam khuyen nghi chemicals_blocked_for_fabric. Bo qua tip/dried_path neu chung ke chat bi chan. "
            "Cam goi y tay oxy / B1 tren da hoac suede."
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


def _scrub_internal_codes(text: str) -> str:
    """Remove leftover internal codes / markdown from owner-facing replies."""
    if not text:
        return text
    # Markdown bold/headers/emphasis (Zalo plain text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = text.replace("**", "")
    # Parenthetical chem codes: (S1), (A3)
    text = re.sub(r"\s*\((?:S1|WF_SOFT|WF_FRAG|A[1-5]|B[12]|D[1-3]|E[1-3]|N[1-3])\)", "", text)
    # Tool / node ids leaked by the model
    text = re.sub(r"\s*\((?:T_[A-Z0-9_]+)\)", "", text)
    text = re.sub(r"(?<![A-Za-z0-9])T_(?:BRUSH_SOFT|BRUSH_HARD|BRUSH_ULTRA|BRUSH_SHOE|CLOTH|SPRAY)(?![A-Za-z0-9])", "", text)
    # Standalone chem tokens
    text = re.sub(
        r"(?<![A-Za-z0-9])(?:S1|WF_SOFT|WF_FRAG|A[1-5]|B[12]|D[1-3]|E[1-3]|N[1-3])(?![A-Za-z0-9])",
        "",
        text,
    )
    # Awkward KO calque "N부분 식초/물" → natural "식초 N : 물 M"
    text = re.sub(r"(\d+)\s*부분\s*(흰\s*)?식초", r"\2식초 \1", text)
    text = re.sub(r"(\d+)\s*부분\s*물", r"물 \1", text)
    text = re.sub(
        r"식초\s*(\d+)\s*(?:와|과|,|/|：|:)\s*물\s*(\d+)",
        r"식초 \1 : 물 \2",
        text,
    )
    text = re.sub(r"(\d+)\s*부분", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r" ?،", ",", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _sanitize_graph_for_owner(graph, lang: str):
    """Drop ids / wrong-language fields so the LLM cannot echo them."""
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
            "when_use_vi": c.get("when_use_vi"),
            "dilution_vi": c.get("dilution_vi"),
            "dilution_ko": c.get("dilution_ko"),
            "wf_supply": c.get("wf_supply"),
            "safe_on_wool": c.get("safe_on_wool"),
            "safe_on_silk": c.get("safe_on_silk"),
        }
        if lang == "ko":
            for k in ("name_vi", "shop_name_vi", "buy_where_vi", "alt1_vi", "alt2_vi", "alt3_vi",
                      "when_use_vi", "dilution_vi", "example_brands_vi"):
                keep.pop(k, None)
        elif lang == "vi":
            keep.pop("name_ko", None)
            keep.pop("buy_where_ko", None)
            keep.pop("dilution_ko", None)
        return {k: v for k, v in keep.items() if v is not None and v != ""}

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
4. Mở đầu ngắn (2–4 câu) nếu có why_vi / tip — nguyên tắc ĐÚNG vết này, rồi mới 1)-6).
5. Câu XỬ LÝ VẾT / CHĂM SÓC MÓN ĐỒ — 1)-6), dễ đọc (cùng một format cho stain và item_care):
   (1) Nhận diện + tươi/khô hoặc tình trạng món (nội dung fresh/dried, không in tên field)
   (2) Dụng cụ — chỉ tên người dùng (name_ko / name_vi), CẤM id T_…
   (3) Lực + hướng
   (4) Hóa chất — xem quy tắc HÓA CHẤT bên dưới
   (5) Nhiệt độ nước + max_temp vải
   (6) Sau xử lý / hoàn thiện (BẮT BUỘC đủ ý, ngắn gọn):
       - Kiểm tra vết CÒN LẠI dưới ánh sáng mạnh TRƯỚC khi sấy/ủi; còn → xử lý lại, CẤM sấy khóa vết
       - Phơi bóng mát, thoáng khí; tránh nắng gắt (phai màu) trừ khi dữ liệu cho phép
       - Nếu có fabric dry_hint_vi / iron_hint_vi → nhắc 1 câu sấy/ủi đúng vải (không bịa nhiệt độ)
       - Dùng aftercare_vi nếu có
   Nếu có item_context: đây là chăm sóc món (giày/túi/áo phao/Gore-Tex…) — vẫn dùng 1)-6), không đổi giọng.
6. WF_SOFT / WF_FRAG chỉ khi đúng when_use_vi
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
- Pha loãng: CHỈ dùng dilution_ko (Hàn) hoặc dilution_vi (Việt) nếu có.
  Không có dilution_* → "병 라벨·본사 안내 따름" / "theo hướng dẫn trên chai / kho WF" — CẤM bịa tỷ lệ (vd 1:4 cho S1).
  Hàn tự nhiên: "식초 1 : 물 4". Việt: "1 phần giấm + 4 phần nước". CẤM "1부분…4부분".
- THỨ TỰ theo tính chất vết (KHÔNG pha cocktail "detergent A+B+C" kiểu 2:1:1 / 1:2:1):
  Protein → nước lạnh + enzyme (nếu vải cho). Dầu → hút bột rồi surfactant. Tannin/màu → acid nhẹ rồi oxy (nếu vải cho).
  Vết phức hợp: làm TỪNG BƯỚC theo fresh_path / care_order nhóm, XẢ giữa bước — không đổ chung một chậu.
  Chỉ dùng paste tỷ lệ khi ĐỒ THỊ / fresh_path ghi rõ; còn lại CẤM bịa tỷ lệ trộn.
  Test góc khuất trước khi xử lý cả món. Tuyệt đối không trộn chất trong never_mix_alerts (vd ammonia + javel).
- B1 = thuốc tẩy oxy (KHÔNG phải "세제 axit"). A3 = giấm / axit nhẹ.
- Vải lụa/len HOẶC chemical.safe_on_silk/safe_on_wool = false HOẶC fabric enzyme_safe/acid_safe/can_bleach = false:
  → KHÔNG khuyến nghị hóa chất không an toàn. Ưu tiên nước giặt trung tính Wash Friends + nước lạnh + lực nhẹ.
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


def _build_llm_prompt(user_message: str, graph_context: dict, lang: str = "vi") -> str:
    raw_graph = graph_context.get("graph")
    safe_graph = _sanitize_graph_for_owner(raw_graph, lang) if isinstance(raw_graph, dict) else raw_graph
    graph_json = json.dumps(safe_graph, ensure_ascii=False, indent=2, default=str)
    query_type = graph_context.get("query_type", "unknown")
    if lang == "ko":
        lang_rule = (
            "청자: 워시프렌즈 점주(동료). 한국어만(베트남어·영어 금지). 마크다운(** ## *) 금지. "
            "힘·방향은 '바깥→안'처럼 한국어만 (external/internal 금지). "
            "약품은 name_ko·일상명만 (A3/B1/S1 코드 말하지 말 것). "
            "도구는 name_ko만 — T_CLOTH 같은 id, name_vi 출력 금지. "
            "희석은 dilution_ko만: '식초 1 : 물 4' 형식. '1부분' 금지. "
            "'세탁소에서 구입' 금지 — 슈퍼/약국/화공, WF는 본사·창고 공급. "
            "실크·울이면 비안전 약품 추천 금지, 워시프렌즈 중성세제 우선. "
            "B1=산소계 표백제(산성 세제 아님). "
            "why/신선·굳음 내용만 쓰고 필드명 출력 금지. 민간요법·다른 오염법 금지. "
            "1)오염·원단 2)도구(name_ko) 3)힘·방향 4)약품 5)수온 "
            "6)후관리: 강한 빛에서 잔존 확인→남으면 재처리(건조 금지), 그늘·통풍 건조, "
            "직사광선 피하기(색바램), fabric dry_hint/iron_hint 있으면 한 줄로 건조·다림질. "
            "약 혼합: A/B/C 칵테일 비율(2:1:1 등) 지어내기 금지. 성분별 순차 처리+중간 헹굼. "
            "구석 테스트 후 전체. never_mix는 절대 준수."
        )
    else:
        lang_rule = (
            "Người nghe: chủ cửa hàng Wash Friends (đồng nghiệp). CHỈ tiếng Việt. "
            "CẤM markdown ** ##. Lực/hướng: 'ngoài→trong' — không xen English. "
            "Hóa chất: shop_name_vi / tên thường — CẤM mã A3/B1/E1/S1. "
            "Pha loãng: CHỈ dilution_vi; không có → 'theo hướng dẫn trên chai / kho WF' — không bịa tỷ lệ. "
            "CẤM 'mua ở tiệm giặt' — siêu thị/nhà thuốc/cửa hóa chất; hàng WF = kho cung ứng. "
            "Lụa/len: không khuyến nghị chất bị chặn; ưu tiên nước giặt trung tính Wash Friends. "
            "B1 = tẩy oxy (không gọi chất tẩy axit). "
            "Không in tên field. Không mẹo dân gian. "
            "1)-6) nhận diện / dụng cụ / lực / hóa chất / nhiệt độ / "
            "sau xử lý: kiểm tra ánh sáng mạnh → còn vết thì làm lại (cấm sấy), phơi bóng mát thoáng, "
            "tránh nắng gắt, nhắc dry_hint/iron_hint nếu có. "
            "CẤM bịa tỷ lệ trộn detergent A+B+C; xử lý tuần tự theo tính chất + xả giữa bước; test góc."
        )

    return f"""Câu hỏi từ chủ cửa hàng: {user_message}

[DỮ LIỆU ĐỒ THỊ — loại truy vấn: {query_type}]
{graph_json}

{lang_rule}
Chỉ trả lời từ dữ liệu trên (chemicals của vết này, tools, washfriends_supply khi đúng).
Null/thiếu → hỏi thêm hoặc bỏ qua — tuyệt đối không bịa và không lẫn sang vết khác.
Giọng nội bộ Wash Friends — không nêu nguồn bên ngoài."""


def _call_llm(llm_prompt: str) -> str:
    response = _openai.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": llm_prompt},
        ],
    )
    return _scrub_internal_codes(response.choices[0].message.content.strip())


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
    answer = _call_llm(llm_prompt)
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
    # Hard override for high-value VN franchise phrases (before graph routing)
    raw_n = _normalize_text(user_message)
    if "laterite" in raw_n or "dat do" in raw_n:
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_LATERITE"
        entities["stain_type"] = "dat do laterite"
    elif "dau nhot xe may" in raw_n or (
        "dau nhot" in raw_n and "xe may" in raw_n
    ):
        entities["intent"] = "treatment"
        entities["stain_id"] = "S_MOTORBIKE_OIL"
        entities["stain_type"] = "dau nhot xe may"
    graph_context = _fetch_graph_context(entities)
    graph_data = graph_context.get("graph")

    if not graph_data or graph_data == {} or graph_data == []:
        return _empty_graph_reply(entities)

    return _answer_with_optional_cache(user_message, entities, graph_context)
