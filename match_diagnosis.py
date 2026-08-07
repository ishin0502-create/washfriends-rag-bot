# -*- coding: utf-8 -*-
"""Match diagnosis: fabric + thickness + stain chemistry → owner-facing card.

Accuracy rule: only facts from graph flags / explicit user text. Never invent
chemistry or minutes — those come from seeded paths + tool binding.
"""
from __future__ import annotations

from typing import Any, Optional


def infer_fabric_weight(text: str, fabric_type: str = "", item_id: str = "") -> str:
    """Return thin | thick | medium | unknown from owner message / item defaults."""
    if not text and not fabric_type and not item_id:
        return "unknown"
    raw = text or ""
    t = raw.lower()

    thin_ko = ("얇은", "얇아", "얇음", "쉬어", "시폰", "보일", "얇게", "얇은원단", "얇은 옷")
    thick_ko = ("두꺼운", "두껍", "두툼", "두터운", "캔버스", "패딩", "코트", "청바지")
    thin_vi = ("mong", "mong manh", "voan", "sheer")
    # NOTE: never use bare "dam" — matches Vietnamese đầm (dress) → false thick
    thick_vi = ("day", "dày", "canvas", "jean", "nặng", "nang")
    thin_en = ("thin", "sheer", "lightweight", "light weight", "chiffon", "voile")
    thick_en = ("thick", "heavy", "heavyweight", "canvas", "denim")

    if any(k in raw for k in thin_ko) or any(k in t for k in thin_vi + thin_en):
        return "thin"
    if any(k in raw for k in thick_ko) or any(k in t for k in thick_vi + thick_en):
        return "thick"

    # Item defaults (only when message did not say thin/thick)
    thin_items = {
        "I_NECKTIE", "I_AO_DAI", "I_SUIT_SUMMER", "I_SWIMWEAR",
    }
    thick_items = {
        "I_DENIM", "I_DUVET_GOOSE", "I_DUVET_COTTON", "I_CURTAIN_FABRIC",
        "I_DOWN_JACKET", "I_FUR_REAL", "I_FUR_FAUX",
    }
    if item_id in thin_items:
        return "thin"
    if item_id in thick_items:
        return "thick"

    ft = (fabric_type or "").lower()
    if ft in ("silk", "rayon", "voile"):
        return "thin"
    if ft in ("denim", "leather", "suede", "fur"):
        return "thick"
    if ft in ("cotton", "polyester", "linen", "wool"):
        return "medium"
    return "unknown"


def chemistry_layers(sc: dict) -> list[str]:
    """Ordered chemistry tags from stain_context boolean flags."""
    if not isinstance(sc, dict):
        return []
    layers = []
    # Order matters for education: oil first when present (surfactant before acid), etc.
    if sc.get("contains_oil"):
        layers.append("oil_hydrophobic")
    if sc.get("contains_protein"):
        layers.append("protein")
    if sc.get("contains_tannin"):
        layers.append("tannin")
    if sc.get("contains_dye"):
        layers.append("dye_pigment")
    return layers


def chemistry_summary(sc: dict, lang: str = "ko") -> str:
    layers = chemistry_layers(sc)
    if not layers:
        return {
            "ko": "성분 불명 — 그래프 플래그 없음. 추측 금지, fresh_path만 따를 것.",
            "vi": "Thành phần chưa rõ — không đoán; chỉ theo fresh_path.",
            "en": "Chemistry unclear — do not guess; follow fresh_path only.",
        }.get(lang, "")

    labels = {
        "ko": {
            "oil_hydrophobic": "유지방·오일(소수성/물에 안 녹음) → 흡착·계면활성제 먼저",
            "protein": "단백질 → 찬물+효소(실크·울은 효소 금지·중성세제)",
            "tannin": "탄닌·식물성 색소 → 찬물+약한 산(식초) 후 필요 시 산소표백",
            "dye_pigment": "염료·안료 → 찍기(블롯)·용제; 문지르면 번짐",
        },
        "vi": {
            "oil_hydrophobic": "Dầu/mỡ (kỵ nước) → hút bột + surfactant trước",
            "protein": "Protein → nước lạnh + enzyme (lụa/len: không enzyme, S1)",
            "tannin": "Tannin → lạnh + giấm loãng rồi oxy nếu cần",
            "dye_pigment": "Nhuộm/pigment → blot/dung môi; không chà lan",
        },
        "en": {
            "oil_hydrophobic": "Oil/grease (hydrophobic) → absorb + surfactant first",
            "protein": "Protein → cold + enzyme (silk/wool: no enzyme, neutral)",
            "tannin": "Tannin → cold + mild acid then oxygen if needed",
            "dye_pigment": "Dye/pigment → blot/solvent; never rub-spread",
        },
    }
    lab = labels.get(lang) or labels["ko"]
    return " / ".join(lab[k] for k in layers if k in lab)


def fabric_weight_rule(weight: str, fabric_type: str = "", lang: str = "ko") -> str:
    ft = (fabric_type or "").lower()
    delicate = ft in ("silk", "wool", "leather", "suede", "fur", "rayon")
    if weight == "thin":
        if lang == "vi":
            return (
                "Vải MỎNG: chỉ Cap1–2, blot; CẤM ngâm cả áo / chà mạnh / bàn chải cứng. "
                "Lụa/len mỏng: ưu tiên S1, test góc."
            )
        if lang == "en":
            return (
                "THIN fabric: Cap1–2 blot only; no full soak, hard brush, or scrub. "
                "Sheer silk/wool: S1 + corner test."
            )
        return (
            "얇은 원단: Cap1–2·블롯만. 통담금·세게 문지르기·경질 솔 금지. "
            "얇은 실크·울: 중성세제 우선, 구석 테스트."
        )
    if weight == "thick":
        if delicate:
            if lang == "vi":
                return "Vải DÀY nhưng nhạy (da/lụa/len): vẫn nhẹ — không dùng lực denim."
            if lang == "en":
                return "THICK but delicate (leather/silk/wool): still gentle — not denim force."
            return "두껍더라도 가죽·실크·울이면 약하게 — 데님식 Cap3 금지."
        if lang == "vi":
            return (
                "Vải DÀY (denim/canvas/cotton dày): có thể Cap2–3 ngắn + bàn chải cứng "
                "nếu tools[] có; ngâm đúng phút protocol — vẫn kiểm tra trước sấy."
            )
        if lang == "en":
            return (
                "THICK (denim/canvas/heavy cotton): Cap2–3 short + hard brush if tools list it; "
                "soak only protocol minutes — inspect before dry."
            )
        return (
            "두꺼운 원단(데님·캔버스·두꺼운 면): tools에 있으면 Cap2–3 짧게+경질 솔 가능. "
            "담금은 protocol 분만 — 건조 전 확인."
        )
    if weight == "medium":
        if lang == "vi":
            return "Độ dày trung bình: theo fresh_path + tools[]; không tự tăng lực."
        if lang == "en":
            return "Medium weight: follow fresh_path + tools[]; do not escalate force."
        return "보통 두께: fresh_path·tools[]만 따를 것. 힘 단계 임의 상향 금지."
    # unknown
    if lang == "vi":
        return (
            "Chưa rõ độ dày/loại vải: nêu giả định an toàn (nhẹ hơn), "
            "và hỏi 1 câu — vải gì + mỏng/dày — trước khi dùng oxy/enzyme mạnh."
        )
    if lang == "en":
        return (
            "Fabric weight unknown: stay conservative; ask one question "
            "(fiber + thin/thick) before strong oxy/enzyme."
        )
    return (
        "원단·두께 미상: 보수적으로(약하게) 안내하고, "
        "강한 산소표백·효소 전에 원단(면/폴리/실크·울)과 얇음/두꺼움을 한 문장으로 되물을 것."
    )


def build_match_diagnosis(
    graph: dict,
    entities: Optional[dict] = None,
    raw_text: str = "",
) -> dict[str, Any]:
    """Attach owner-facing diagnosis so LLM cannot skip fabric×stain matching."""
    entities = entities or {}
    sc = graph.get("stain_context") if isinstance(graph.get("stain_context"), dict) else {}
    ic = graph.get("item_context") if isinstance(graph.get("item_context"), dict) else {}
    fabric = graph.get("fabric_context") if isinstance(graph.get("fabric_context"), dict) else {}

    fabric_type = (
        entities.get("fabric_type")
        or fabric.get("name")
        or fabric.get("name_vi")
        or ""
    )
    if isinstance(fabric_type, str):
        fabric_type = fabric_type.strip()
    else:
        fabric_type = ""

    item_id = str(ic.get("id") or entities.get("item_id") or "")
    weight = entities.get("fabric_weight") or infer_fabric_weight(
        raw_text or entities.get("_raw") or "",
        fabric_type=str(fabric_type),
        item_id=item_id,
    )
    layers = chemistry_layers(sc)
    garment_color = entities.get("garment_color") or graph.get("garment_color") or ""

    need_ask = False  # Do not gate SOP on a clarify question (session + weight bands instead)
    fabric_missing = not fabric_type or str(fabric_type).lower() in ("unknown", "")
    weight_missing = weight == "unknown"

    bands_ko = (
        "두께별: 얇음→Cap1·블롯·통담금·경질솔 금지 / "
        "보통→아래 SOP 기준 / "
        "두꺼움→Cap2–3·담금·솔 여유. "
        "실크·울이면 효소·산소·강한 산 대신 중성세제·국소."
    )
    bands_vi = (
        "Theo độ dày: mỏng→Cap1·blot·cấm ngâm cả áo / "
        "vừa→SOP dưới / "
        "dày→Cap2–3·ngâm. "
        "Lụa/len: S1 cục bộ, không enzyme/oxy/acid mạnh."
    )
    bands_en = (
        "By thickness: thin→Cap1 blot, no full soak / "
        "medium→SOP below / "
        "thick→Cap2–3 soak room. "
        "Silk/wool: neutral detergent local only."
    )

    card = {
        "fabric_type": fabric_type or "unknown",
        "fabric_weight": weight,
        "garment_color": garment_color or "unknown",
        "stain_id": sc.get("id") or "",
        "chemistry_layers": layers,
        "chemistry_ko": chemistry_summary(sc, "ko"),
        "chemistry_vi": chemistry_summary(sc, "vi"),
        "chemistry_en": chemistry_summary(sc, "en"),
        "fabric_rule_ko": fabric_weight_rule(weight, fabric_type, "ko"),
        "fabric_rule_vi": fabric_weight_rule(weight, fabric_type, "vi"),
        "fabric_rule_en": fabric_weight_rule(weight, fabric_type, "en"),
        "weight_bands_ko": bands_ko if (fabric_missing or weight_missing) else "",
        "weight_bands_vi": bands_vi if (fabric_missing or weight_missing) else "",
        "weight_bands_en": bands_en if (fabric_missing or weight_missing) else "",
        # Soft optional note — never replaces a full SOP
        "ask_fabric_ko": (
            "원단(면/폴리/실크·울)·두께를 알면 더 정확히 맞출 수 있습니다."
            if (fabric_missing or weight_missing) and bool(sc.get("id"))
            else ""
        ),
        "ask_fabric_vi": (
            "Nếu biết loại vải và độ dày sẽ khớp SOP hơn."
            if (fabric_missing or weight_missing) and bool(sc.get("id"))
            else ""
        ),
        "ask_fabric_en": (
            "Fiber + thickness refine the SOP further if known."
            if (fabric_missing or weight_missing) and bool(sc.get("id"))
            else ""
        ),
        "accuracy_rule_ko": (
            "(1)에서 반드시: 오염 성분 + 원단 + 두께(+색). "
            "원단·두께 미상이면 weight_bands로 얇/보통/두꺼움 차이를 말하고 SOP는 보통(면) 기준으로 완결. "
            "도구 분·희석·사용법은 tools[]/chemicals[]만 — 지어내기 금지."
        ),
        "accuracy_rule_vi": (
            "Ở (1): thành phần + vải + độ dày (+màu). "
            "Nếu chưa rõ: nói weight_bands và hoàn tất SOP mức vừa. "
            "Phút/pha chỉ từ tools[]/chemicals[]."
        ),
        "accuracy_rule_en": (
            "In (1): chemistry + fabric + thickness (+color). "
            "If unknown: state weight_bands and complete medium SOP. "
            "Minutes/dilution only from tools[]/chemicals[]."
        ),
    }
    return card


def apply_weight_to_tools(graph: dict, weight: str) -> dict:
    """Drop unsafe tools for thin/delicate; keep how-to ids for thick cotton/denim."""
    if not isinstance(graph, dict):
        return graph
    tools = [t for t in (graph.get("tools") or []) if t]
    if not tools or weight not in ("thin", "thick"):
        return graph

    fabric = graph.get("fabric_context") or {}
    fid = str(fabric.get("id") or "").upper()
    fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''}".lower()
    is_delicate = (
        fid in ("F3", "F4", "F7", "F8", "F9", "F10")
        or any(x in fname for x in ("silk", "lua", "wool", " len", "leather", "suede", "fur", "rayon"))
    )

    drop = set()
    if weight == "thin" or (weight == "thick" and is_delicate):
        drop |= {"T_BRUSH_HARD", "T_BRUSH_SHOE"}
        if weight == "thin":
            drop |= {"T_SOAK_BIN"}

    refined = [t for t in tools if str(t.get("id") or "") not in drop]
    out = dict(graph)
    out["tools"] = refined
    return out
