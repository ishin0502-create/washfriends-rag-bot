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
WHERE toLower(coalesce(s.name_vi, '')) CONTAINS toLower($stain_input)
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
RETURN
  s {
    .id, .name, .name_vi, .tip, .urgency,
    .contains_protein, .contains_tannin, .contains_oil, .contains_dye,
    .water_spreads, group: g.name_vi, group_id: g.id
  } AS stain_context,
  CASE WHEN f IS NULL THEN null ELSE f {
    .id, .name, .name_vi, .max_temp, .can_bleach, .enzyme_safe, .acid_safe
  } END AS fabric_context,
  COLLECT(DISTINCT chem {
    .code, .name, .name_vi, .role, .safe_on_wool, .safe_on_silk
  }) AS chemicals,
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

Q_RESCUE = """
MATCH (s:Stain)
WHERE s.id = $stain_id
   OR toLower(coalesce(s.name_vi, '')) CONTAINS toLower($stain_input)
   OR toLower(coalesce(s.name, '')) CONTAINS toLower($stain_input)
WITH s LIMIT 1
OPTIONAL MATCH (s)-[:USES_CHEMICAL]->(chem:Chemical)
RETURN s.name_vi AS stain_vi, s.tip AS tip, s.urgency AS urgency,
  COLLECT(DISTINCT chem {.code, .name_vi, .role}) AS chemicals,
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

    stain_input  = _normalize_text(
        entities.get("stain_type") or entities.get("stain_id") or ""
    )
    fabric_input = _normalize_text(entities.get("fabric_type") or "")
    stain_id     = entities.get("stain_id") or ""
    raw_msg      = _normalize_text(entities.get("_raw") or "")

    # Common franchise phrasing → seed name keys (accent-insensitive)
    _ALIASES = {
        "laterite": "dat do laterite",
        "dat do": "dat do laterite",
        "dat do laterite": "dat do laterite",
        "dau nhot xe may": "dau nhot xe may",
        "xe may": "dau nhot xe may",
        "nam moc": "nam moc",
        "moc": "nam moc",
        "ri set": "ri set",
        "gỉ sét": "ri set",
    }
    for key, canon in _ALIASES.items():
        if key in stain_input or (raw_msg and key in raw_msg):
            stain_input = canon
            break
    if not stain_input and raw_msg:
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
        "stain_input":  stain_input,
        "fabric_input": fabric_input,
    })

    if not rows or rows[0].get("stain_context") is None:
        fallback = _fallback_search(stain_input)
        if fallback:
            # Re-fetch full context using best matched stain id/name
            best = fallback[0]
            rows = _run_query(Q_FULL_CONTEXT, {
                "stain_input": best.get("id") or best.get("name_vi") or stain_input,
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

    return context


# ─── LLM Responder ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là chuyên gia giặt ủi của Wash Friends Vietnam.
Nhiệm vụ: Trả lời chủ cửa hàng nhượng quyền về xử lý vết bẩn và chăm sóc quần áo.
Giọng điệu: kinh nghiệm nội bộ Wash Friends — tự tin, cụ thể, như hướng dẫn kỹ thuật của bản thân.

QUY TẮC TRẢ LỜI:
1. Tiếng Việt là ngôn ngữ chính (nếu hỏi tiếng Hàn → trả lời cả hai)
2. Chỉ dùng DỮ LIỆU TỪ ĐỒ THỊ — không bịa hóa chất ngoài danh sách đã cho
3. Cảnh báo an toàn đặt ĐẦU câu (chữ in hoa ngắn, không markdown **)
4. Luôn gồm: bước + hóa chất (mã + tên) + cấp lực + cảnh báo vải
5. Kết thúc: thời gian xử lý ước tính (+ chi phí nếu có trong dữ liệu)
6. Thiếu dữ liệu → hỏi ngắn (loại vết, loại vải, mới/cũ, đã sấy chưa)
7. Không dùng markdown **, ## — Zalo hiển thị plain text
8. CẤM nêu nguồn ngoài: đại học, thương hiệu khác, internet, AI, PDF, website, "theo tài liệu"
9. Không nói kiểu tìm trên mạng — nói như quy trình vận hành Wash Friends

CẤP ĐỘ LỰC:
Cap 1 = Rat nhe | Cap 2 = Nhe | Cap 3 = Vua | Cap 4 = Manh

Định dạng:
- Tối đa 600 từ
- Số bước rõ ràng: 1) 2) 3)
- Tên hóa chất: mã (D1, E1...) + tên đầy đủ lần đầu"""

def _build_llm_prompt(user_message: str, graph_context: dict) -> str:
    graph_json = json.dumps(graph_context["graph"], ensure_ascii=False, indent=2, default=str)
    query_type = graph_context.get("query_type", "unknown")

    return f"""Câu hỏi từ chủ cửa hàng: {user_message}

[DỮ LIỆU ĐỒ THỊ — loại truy vấn: {query_type}]
{graph_json}

Hãy trả lời dựa trên dữ liệu trên. Nếu dữ liệu trống hoặc null → hỏi thêm thông tin.
Nhắc lại: trả lời như quy trình nội bộ Wash Friends — không nêu bất kỳ nguồn bên ngoài nào."""


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
    entities.setdefault("lang", "vi")

    graph_context = _fetch_graph_context(entities)
    graph_data    = graph_context.get("graph")

    if not graph_data or graph_data in ({}, []):
        lang = entities.get("lang", "vi")
        if entities.get("_image_analysis"):
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
                "• 어떤 종류의 얼룩인가요?\n"
                "• 어떤 원단인가요?"
            )
        return (
            "Xin loi, toi khong tim thay thong tin cho cau hoi nay.\n\n"
            "Vui long cho biet:\n"
            "• Loai vet ban la gi?\n"
            "• Chat lieu vai la gi?"
        )

    base_prompt = _build_llm_prompt(user_caption or "", graph_context)
    llm_prompt  = (prefix + "\n\n" + base_prompt) if prefix else base_prompt

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
    """Main entry point: given a user message, return a Vietnamese chatbot response."""
    entities = extract_entities(user_message)
    entities["_raw"] = user_message
    graph_context = _fetch_graph_context(entities)
    graph_data = graph_context.get("graph")

    if not graph_data or graph_data == {} or graph_data == []:
        lang = entities.get("lang", "vi")
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

    llm_prompt = _build_llm_prompt(user_message, graph_context)
    response = _openai.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": llm_prompt},
        ],
    )
    return response.choices[0].message.content.strip()
