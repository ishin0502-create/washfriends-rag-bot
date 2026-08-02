"""
graphrag_engine.py
Wash Friends Vietnam — Neo4j GraphRAG Pipeline

Flow:
  user_message
    → entity_extractor  (GPT-4o-mini: fast, cheap entity extraction)
    → query_router      (select which of 14 Cypher queries to run)
    → neo4j_query       (fetch graph context)
    → llm_responder     (GPT-4o-mini: build Vietnamese answer from graph data)
    → formatted_response

The LLM NEVER invents chemical information — it only narrates what the graph returns.
"""

import os
import json
from datetime import datetime, timezone, timedelta
from typing import Optional

from neo4j import GraphDatabase, Driver
from openai import OpenAI

from entity_extractor import extract_entities

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


# ─── Cypher queries ───────────────────────────────────────────────────────────

# Query 9: Master full-context builder (primary path)
Q_FULL_CONTEXT = """
MATCH (s:Stain)
WHERE toLower(s.name_vi) CONTAINS toLower($stain_input)
   OR toLower(s.name_ko) CONTAINS toLower($stain_input)
   OR toLower(s.name_en) CONTAINS toLower($stain_input)
WITH s LIMIT 1
MATCH (s)-[:BELONGS_TO]->(g:StainGroup)
OPTIONAL MATCH (f:Fabric)
  WHERE toLower(f.name_vi) CONTAINS toLower($fabric_input)
     OR toLower(f.name_en) CONTAINS toLower($fabric_input)
WITH s, g, f LIMIT 1
OPTIONAL MATCH (s)-[hs:HAS_STEP]->(step:Step)
OPTIONAL MATCH (step)-[:REQUIRES_FORCE]->(force:ForceLevel)
OPTIONAL MATCH (s)-[ton:TREATABLE_ON]->(f)
OPTIONAL MATCH (s)-[:USES_CHEMICAL]->(chem:Chemical)
OPTIONAL MATCH (chem)-[dmg:DAMAGES]->(f)
OPTIONAL MATCH (chem)-[nm:NEVER_MIX_WITH]->(dangerous:Chemical)
OPTIONAL MATCH (cr:ClimateRule)
  WHERE (cr.id = 'vn_4hour_rule')
     OR (cr.id = 'vn_rainy_season' AND $month IN [5,6,7,8,9,10,11])
     OR (cr.id = 'vn_protein_ferment' AND g.id = 'group_protein' AND $hours_since >= 2)
RETURN
  s {
    .id, .name_vi, .name_ko, .name_en, .difficulty, .time_sensitivity,
    .golden_rule_vi, .golden_rule_ko, .golden_rule_en, .primary_chemicals,
    .rescue_plan_b_vi, .rescue_plan_c_vi, .stop_signal_vi,
    .cost_chemical_vnd, .cost_time_vi, .surcharge_vi,
    group: g.name_vi
  } AS stain_context,
  f {
    .id, .name_vi, .name_ko, .name_en, .max_temp_celsius,
    .can_bleach_oxy, .can_bleach_chlorine, .can_use_enzyme,
    .requires_specialty_detergent, .specialty_detergent, .care_note_vi
  } AS fabric_context,
  ton {.adjustment_vi, .warning} AS fabric_adjustment,
  COLLECT(DISTINCT step {
    .step_number, .action_vi, .action_ko, .force_level, .detail_vi,
    force_icon: force.icon, force_name_vi: force.name_vi
  }) AS protocol_steps,
  COLLECT(DISTINCT CASE WHEN dmg IS NOT NULL THEN {
    chemical: chem.code, chemical_name_vi: chem.name_vi,
    danger_vi: dmg.reason_vi, severity: dmg.severity, reversible: dmg.reversible
  } END) AS safety_alerts,
  COLLECT(DISTINCT CASE WHEN nm IS NOT NULL THEN {
    mix_chemical: dangerous.code, danger_vi: nm.danger_vi,
    reaction: nm.reaction, emergency: nm.emergency_number
  } END) AS never_mix_alerts,
  COLLECT(DISTINCT cr {.id, .name_vi, .rule_vi, .action_vi}) AS climate_context
"""

# Query 13: Fulltext fallback
Q_FULLTEXT = """
CALL db.index.fulltext.queryNodes('stain_fulltext', $search_term + '~')
YIELD node AS s, score
WHERE score > 0.3
MATCH (s)-[:BELONGS_TO]->(g:StainGroup)
RETURN s.id, s.name_vi, s.name_ko, s.difficulty, g.name_vi AS group_vi, score
ORDER BY score DESC LIMIT 5
"""

# Query 6: Rescue protocol
Q_RESCUE = """
MATCH (s:Stain {id: $stain_id})
RETURN s.name_vi AS stain_vi, s.difficulty,
  s.rescue_plan_b_vi AS plan_b, s.rescue_plan_c_vi AS plan_c,
  s.stop_signal_vi AS when_to_stop,
  CASE $attempt_number
    WHEN 1 THEN s.rescue_plan_b_vi
    WHEN 2 THEN s.rescue_plan_c_vi
    ELSE '⚠️ Vết bẩn vĩnh viễn — hãy thông báo khách và đề xuất bồi thường'
  END AS recommended_rescue
"""

# Query 8: Pricing
Q_PRICE = """
MATCH (s:Stain {id: $stain_id})
OPTIONAL MATCH (s)-[ton:TREATABLE_ON]->(f:Fabric {id: $fabric_id})
RETURN s.name_vi, s.difficulty, s.cost_chemical_vnd, s.cost_time_vi,
  s.surcharge_vi,
  CASE s.difficulty
    WHEN 1 THEN '5.000 - 15.000 VND'
    WHEN 2 THEN '10.000 - 30.000 VND'
    WHEN 3 THEN '30.000 - 80.000 VND'
    WHEN 4 THEN '50.000 - 150.000 VND'
    WHEN 5 THEN 'Liên hệ trực tiếp — giá theo yêu cầu'
  END AS suggested_price_range,
  ton.warning AS fabric_warning
"""

# Query 5: Mystery stain (by color)
Q_MYSTERY_COLOR = """
MATCH (s:Stain)-[:BELONGS_TO]->(g:StainGroup)
WHERE
  CASE $stain_color
    WHEN 'red'    THEN s.contains_protein = true OR s.contains_tannin = true
    WHEN 'yellow' THEN s.contains_protein = true OR s.contains_oil = true
    WHEN 'brown'  THEN s.contains_tannin = true OR s.contains_oil = true
    WHEN 'black'  THEN s.contains_dye = true
    WHEN 'blue'   THEN s.contains_dye = true
    WHEN 'green'  THEN s.contains_tannin = true
    WHEN 'white'  THEN s.contains_oil = true OR s.contains_protein = true
    ELSE true
  END
RETURN s.name_vi, s.name_ko, s.difficulty, g.name_vi AS group_vi,
       s.contains_oil, s.contains_protein, s.contains_tannin, s.contains_dye,
       s.time_sensitivity
ORDER BY s.difficulty ASC LIMIT 8
"""

# Query 11: Hardest stains
Q_HARDEST = """
MATCH (s:Stain)-[:BELONGS_TO]->(g:StainGroup)
WHERE s.difficulty >= 4
RETURN s.name_vi, s.name_ko, s.difficulty, s.time_sensitivity,
  g.name_vi AS group_vi, s.stop_signal_vi AS when_to_give_up
ORDER BY s.difficulty DESC, s.time_sensitivity DESC
"""

# Query 12: Daily checklist
Q_DAILY = """
MATCH (c1:Chemical)-[nm:NEVER_MIX_WITH]->(c2:Chemical)
WHERE nm.danger_level = 'CRITICAL'
WITH COLLECT({mix: c1.code + ' + ' + c2.code, danger_vi: nm.danger_vi,
              emergency: nm.emergency_number}) AS never_mix_rules
MATCH (cr:ClimateRule)
WHERE $month IN [5,6,7,8,9,10,11] OR cr.id IN ['vn_4hour_rule','vn_temp_rule']
RETURN never_mix_rules, COLLECT(cr {.name_vi, .rule_vi, .action_vi}) AS climate_rules
"""

# Query 2: Chemical safety
Q_CHEM_SAFETY = """
MATCH (c:Chemical {code: $chem_code})
OPTIONAL MATCH (c)-[:SAFE_FOR]->(f_safe:Fabric)
OPTIONAL MATCH (c)-[dmg:DAMAGES]->(f_dmg:Fabric)
OPTIONAL MATCH (c)-[nm:NEVER_MIX_WITH]->(c2:Chemical)
RETURN c {.code, .name_vi, .name_ko, .description_vi, .concentration_vi, .safety_vi},
  COLLECT(DISTINCT f_safe.name_vi) AS safe_for_fabrics,
  COLLECT(DISTINCT {fabric: f_dmg.name_vi, reason: dmg.reason_vi, severity: dmg.severity}) AS damages,
  COLLECT(DISTINCT {chemical: c2.code, danger_vi: nm.danger_vi, reaction: nm.reaction}) AS never_mix
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


# ─── Query router ─────────────────────────────────────────────────────────────

def _fetch_graph_context(entities: dict) -> dict:
    """
    Route to correct query set based on intent + entities.
    Returns a context dict with all graph data for the LLM.
    """
    intent  = entities.get("intent", "treatment")
    month   = _vn_month()
    hours   = entities.get("hours_since") or 0.0
    context = {"intent": intent, "entities": entities}

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

    if intent == "safety" and entities.get("stain_id"):
        rows = _run_query(Q_CHEM_SAFETY, {"chem_code": entities["stain_id"].upper()})
        context["graph"] = rows[0] if rows else {}
        context["query_type"] = "safety"
        return context

    if intent == "mystery":
        params = {
            "stain_color": entities.get("stain_color") or "none",
            "smell": entities.get("smell") or "none",
            "water_spreads": entities.get("water_spreads"),
        }
        rows = _run_query(Q_MYSTERY_COLOR, params)
        context["graph"] = rows
        context["query_type"] = "mystery"
        return context

    if intent == "rescue":
        stain_id = entities.get("stain_id") or ""
        attempt  = entities.get("attempt_number") or 1
        rows = _run_query(Q_RESCUE, {"stain_id": stain_id, "attempt_number": attempt})
        context["graph"] = rows[0] if rows else {}
        context["query_type"] = "rescue"
        return context

    if intent == "price":
        stain_id  = entities.get("stain_id") or ""
        fabric_id = entities.get("fabric_type") or ""
        rows = _run_query(Q_PRICE, {"stain_id": stain_id, "fabric_id": fabric_id})
        context["graph"] = rows[0] if rows else {}
        context["query_type"] = "price"
        return context

    # Default: full treatment protocol (intent == "treatment" or browse)
    stain_input  = entities.get("stain_type") or ""
    fabric_input = entities.get("fabric_type") or ""

    rows = _run_query(Q_FULL_CONTEXT, {
        "stain_input":  stain_input,
        "fabric_input": fabric_input,
        "month":        month,
        "hours_since":  hours,
    })

    if not rows or rows[0].get("stain_context") is None:
        # Fallback to fulltext search
        rows = _run_query(Q_FULLTEXT, {"search_term": stain_input})
        context["graph"] = rows
        context["query_type"] = "fulltext_fallback"
    else:
        context["graph"] = rows[0]
        context["query_type"] = "full_context"

    return context


# ─── LLM Responder ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là chuyên gia giặt ủi của Wash Friends Vietnam.
Nhiệm vụ: Trả lời câu hỏi của chủ cửa hàng nhượng quyền về xử lý vết bẩn và chăm sóc quần áo.

QUY TẮC TRẢ LỜI:
1. Luôn dùng tiếng Việt là ngôn ngữ chính (nếu khách hỏi bằng tiếng Hàn → trả lời cả hai)
2. Chỉ dùng DỮ LIỆU TỪ ĐỒ THỊ — không sáng tạo thông tin hóa chất
3. Nếu có cảnh báo an toàn → in đậm (**) và đặt ĐẦU câu trả lời
4. Luôn bao gồm: bước thực hiện + hóa chất + cấp lực + cảnh báo
5. Kết thúc bằng: chi phí ước tính + thời gian xử lý
6. Nếu không tìm thấy dữ liệu → hỏi thêm thông tin (loại vết, loại vải)

CẤP ĐỘ LỰC:
👶 Cấp 1 = Rất nhẹ | 👓 Cấp 2 = Nhẹ | 🍽️ Cấp 3 = Vừa | 🍳 Cấp 4 = Mạnh | 🦏 Cấp 5 = Rất mạnh

Định dạng câu trả lời:
- Tối đa 600 từ (Zalo/Messenger giới hạn hiển thị)
- Dùng emoji để dễ đọc trên điện thoại
- Số bước rõ ràng: 1️⃣ 2️⃣ 3️⃣
- Tên hóa chất: dùng mã (D1, E1...) + tên đầy đủ lần đầu nhắc đến"""


def _build_llm_prompt(user_message: str, graph_context: dict) -> str:
    graph_json = json.dumps(graph_context["graph"], ensure_ascii=False, indent=2)
    query_type = graph_context.get("query_type", "unknown")

    return f"""Câu hỏi từ chủ cửa hàng: {user_message}

[DỮ LIỆU ĐỒ THỊ — loại truy vấn: {query_type}]
{graph_json}

Hãy trả lời dựa trên dữ liệu trên. Nếu dữ liệu trống hoặc null → hỏi thêm thông tin."""


def generate_response_from_entities(
    entities: dict,
    user_caption: str = "",
    prefix: str = "",
) -> str:
    """
    Entry point when entities are already known (e.g. from image analysis).
    `prefix` is prepended to the LLM prompt (e.g. "📸 Phân tích ảnh: ...").
    """
    graph_context = _fetch_graph_context(entities)
    graph_data    = graph_context.get("graph")

    if not graph_data or graph_data in ({}, []):
        lang = entities.get("lang", "vi")
        # Image with low confidence → ask clarifying questions
        if entities.get("_image_analysis"):
            if lang == "ko":
                return (
                    "📸 사진을 받았습니다만 얼룩 종류를 정확히 파악하기 어렵습니다.\n\n"
                    "추가로 알려주세요:\n"
                    "• 어떤 종류의 얼룩인가요? (기름, 혈액, 커피 등)\n"
                    "• 어떤 원단인가요? (면, 실크, 폴리에스터 등)"
                )
            return (
                "📸 Tôi đã nhận ảnh nhưng khó xác định chính xác loại vết bẩn.\n\n"
                "Vui lòng cho biết thêm:\n"
                "• Loại vết bẩn là gì? (dầu ăn, máu, cà phê, v.v.)\n"
                "• Chất liệu vải là gì? (cotton, lụa, polyester, v.v.)"
            )
        lang = entities.get("lang", "vi")
        if lang == "ko":
            return (
                "죄송합니다, 해당 정보를 찾을 수 없었습니다. 🔍\n\n"
                "더 정확한 답변을 위해 알려주세요:\n"
                "• 어떤 종류의 얼룩인가요?\n"
                "• 어떤 원단인가요?"
            )
        return (
            "Xin lỗi, tôi không tìm thấy thông tin cho câu hỏi này. 🔍\n\n"
            "Vui lòng cho biết:\n"
            "• Loại vết bẩn là gì?\n"
            "• Chất liệu vải là gì?"
        )

    # Build prompt with optional vision prefix
    base_prompt = _build_llm_prompt(user_caption or "", graph_context)
    llm_prompt  = prefix + base_prompt if prefix else base_prompt

    response = _openai.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": llm_prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def generate_response(user_message: str) -> str:
    """
    Main entry point: given a user message, return a Vietnamese chatbot response.
    """
    # Step 1: Extract entities
    entities = extract_entities(user_message)

    # Step 2: Fetch graph context from Neo4j
    graph_context = _fetch_graph_context(entities)

    # Step 3: If no data found at all, return helpful prompt
    graph_data = graph_context.get("graph")
    if not graph_data or graph_data == {} or graph_data == []:
        lang = entities.get("lang", "vi")
        if lang == "ko":
            return (
                "죄송합니다, 해당 정보를 찾을 수 없었습니다. 🔍\n\n"
                "더 정확한 답변을 위해 알려주세요:\n"
                "• 어떤 종류의 얼룩인가요? (예: 기름, 혈액, 커피)\n"
                "• 어떤 원단인가요? (예: 면, 실크, 폴리에스터)\n"
                "• 얼룩이 생긴 지 얼마나 됐나요?"
            )
        return (
            "Xin lỗi, tôi không tìm thấy thông tin cho câu hỏi này. 🔍\n\n"
            "Để trả lời chính xác hơn, vui lòng cho biết:\n"
            "• Loại vết bẩn là gì? (ví dụ: dầu ăn, máu, cà phê)\n"
            "• Chất liệu vải là gì? (ví dụ: cotton, lụa, polyester)\n"
            "• Vết bẩn bị bao lâu rồi?"
        )

    # Step 4: Build LLM prompt
    llm_prompt = _build_llm_prompt(user_message, graph_context)

    # Step 5: Call GPT-4o-mini for final response
    response = _openai.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": llm_prompt},
        ],
    )

    return response.choices[0].message.content.strip()
