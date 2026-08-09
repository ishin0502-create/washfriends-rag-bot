# -*- coding: utf-8 -*-
"""Protocol is the single truth for tools + chemicals in owner answers.

- Runtime: hydrate tools[] from Protocol tool_ids + PPE rules (never empty when SOP has tools).
- Seed: generate USES_TOOL / USES_CHEMICAL rows from PROTOCOL_BUILDERS (no hand N2 drift).
- Matrix: assert every protocol stain emits non-empty tools/chems for cotton baseline.
"""
from __future__ import annotations

from typing import Any, Optional

# ── Tool catalog (names only; howto rewritten at runtime) ─────────────────────
TOOL_CATALOG: dict[str, dict[str, str]] = {
    "T_BRUSH_SOFT": {
        "id": "T_BRUSH_SOFT",
        "name_ko": "연질 스포팅 솔",
        "name_vi": "Bàn chải spotting mềm",
        "name": "Soft spotting brush",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_BRUSH_HARD": {
        "id": "T_BRUSH_HARD",
        "name_ko": "경질 스포팅 솔",
        "name_vi": "Bàn chải spotting cứng",
        "name": "Hard spotting brush",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_BRUSH_ULTRA": {
        "id": "T_BRUSH_ULTRA",
        "name_ko": "초연질 솔·스펀지",
        "name_vi": "Bàn chải siêu mềm",
        "name": "Ultra-soft brush",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_CLOTH": {
        "id": "T_CLOTH",
        "name_ko": "흰 천·흡수지",
        "name_vi": "Khăn trắng / giấy thấm",
        "name": "White cloth / blotter",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_SPRAY": {
        "id": "T_SPRAY",
        "name_ko": "분무기(약마다 따로·겉에 이름·비율 쓰기)",
        "name_vi": "Bình xịt (mỗi hóa chất 1 bình)",
        "name": "Spray bottle",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_BRUSH_SHOE": {
        "id": "T_BRUSH_SHOE",
        "name_ko": "운동화 밑창용 경질 솔",
        "name_vi": "Bàn chải đế giày",
        "name": "Shoe sole brush",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_GLOVE_NITRILE": {
        "id": "T_GLOVE_NITRILE",
        "name_ko": "니트릴 장갑(PPE)",
        "name_vi": "Găng tay nitrile (PPE)",
        "name": "Nitrile gloves",
        "use_for_ko": "X2·락스·알코올·아세톤·용제·바이오하자드 전 필수. 병 열기 전 착용.",
        "use_for_vi": "BẮT BUỘC trước X2/Javel/cồn/acetone/dung môi/biohazard.",
        "use_for_en": "Required before X2/chlorine/solvent/biohazard.",
    },
    "T_MESH_BAG": {
        "id": "T_MESH_BAG",
        "name_ko": "세탁망",
        "name_vi": "Túi lưới giặt",
        "name": "Mesh bag",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_TIMER": {
        "id": "T_TIMER",
        "name_ko": "타이머",
        "name_vi": "Đồng hồ hẹn giờ",
        "name": "Timer",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_SOAK_BIN": {
        "id": "T_SOAK_BIN",
        "name_ko": "담금통·침지 용기",
        "name_vi": "Chậu ngâm",
        "name": "Soak bin",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_UV_LAMP": {
        "id": "T_UV_LAMP",
        "name_ko": "UV 램프(잔여 얼룩 검사용)",
        "name_vi": "Đèn UV 365nm",
        "name": "UV lamp",
        "use_for_ko": "방 불 끄고 ~15–20cm에서 잔여 확인. 건조 전.",
        "use_for_vi": "Tắt đèn, ~15-20cm quét vết còn. Trước sấy.",
        "use_for_en": "Lights off, ~15–20cm scan residue before dry.",
    },
    "T_STEAM_IRON": {
        "id": "T_STEAM_IRON",
        "name_ko": "스팀 다리미",
        "name_vi": "Bàn ủi hơi",
        "name": "Steam iron",
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    },
    "T_MASK": {
        "id": "T_MASK",
        "name_ko": "마스크(PPE)",
        "name_vi": "Khẩu trang (PPE)",
        "name": "Mask",
        "use_for_ko": "곰팡이·악취·용제·바이오하자드 시 장갑·환기와 함께.",
        "use_for_vi": "Mốc/mùi/dung môi/biohazard — kèm găng + thông gió.",
        "use_for_en": "Mold/odor/solvent/biohazard — with gloves + ventilation.",
    },
}

# Biohazard / body fluids — gloves + mask (DLI / housekeeping PPE practice)
BIOHAZARD_STAINS = frozenset({
    "S_BLOOD_FRESH", "S_BLOOD_DRY",
    "S_VOMIT", "S_URINE", "S_FECES",
})

# Chems that always require nitrile before opening (oxalic, chlorine, solvents, acetone, ammonia, reducing bleach)
GLOVE_CHEMS = frozenset({"X2", "X1", "B2", "A1", "A2", "D1", "A5"})

# Chems / stains that need mask + ventilation emphasis
MASK_CHEMS = frozenset({"D1", "A2", "B2"})
MASK_STAINS = frozenset({
    "S_MILDEW", "S_ENGINE_OIL", "S_MOTORBIKE_OIL", "S_TAR", "S_PAINT_OIL",
}) | BIOHAZARD_STAINS

# Extra tools not always in step.tool_ids but required for franchise QA
EXTRA_TOOLS_BY_STAIN: dict[str, list[str]] = {
    "S_CURRY": ["T_UV_LAMP"],
    "S_MUSTARD": ["T_UV_LAMP"],
    "S_GAC": ["T_UV_LAMP"],
    "S_ANNATTO": ["T_UV_LAMP"],
}


def _ordered_unique(ids: list[str]) -> list[str]:
    out: list[str] = []
    for tid in ids:
        if tid and tid not in out:
            out.append(tid)
    return out


def collect_required_tool_ids(proto: Any) -> list[str]:
    """Union of Protocol step tool_ids + PPE / timer / spray / soak implications."""
    ids: list[str] = []
    for s in proto.active_steps():
        for tid in s.tool_ids or []:
            if tid not in ids:
                ids.append(tid)

    codes = set(proto.chem_codes())
    sid = str(getattr(proto, "stain_id", "") or "")

    has_minutes = any(s.minutes_lo is not None for s in proto.active_steps())
    has_soak = any(s.soak for s in proto.active_steps())
    has_spray = any(s.spray for s in proto.active_steps())

    if has_minutes and "T_TIMER" not in ids:
        ids.append("T_TIMER")
    if has_soak and "T_SOAK_BIN" not in ids:
        ids.append("T_SOAK_BIN")
    if has_spray and "T_SPRAY" not in ids:
        ids.append("T_SPRAY")

    need_glove = (
        sid in BIOHAZARD_STAINS
        or bool(codes & GLOVE_CHEMS)
        or sid in {"S_RUST", "S_LATERITE", "S_GUM", "S_NAIL_POLISH"}
    )
    if need_glove and "T_GLOVE_NITRILE" not in ids:
        ids.append("T_GLOVE_NITRILE")

    need_mask = sid in MASK_STAINS or bool(codes & MASK_CHEMS)
    if need_mask and "T_MASK" not in ids:
        ids.append("T_MASK")

    for tid in EXTRA_TOOLS_BY_STAIN.get(sid, []):
        if tid not in ids:
            ids.append(tid)

    return _ordered_unique(ids)


def tool_stub(tid: str) -> dict[str, str]:
    base = TOOL_CATALOG.get(tid)
    if base:
        return dict(base)
    return {
        "id": tid,
        "name_ko": tid,
        "name_vi": tid,
        "name": tid,
        "use_for_ko": "(런타임)",
        "use_for_vi": "(runtime)",
        "use_for_en": "(runtime)",
    }


def hydrate_tool_list(proto: Any, tools: Optional[list] = None) -> list[dict]:
    """Ensure tools[] contains every required Protocol/PPE tool (stubs OK)."""
    by_id: dict[str, dict] = {}
    for t in tools or []:
        if not t:
            continue
        tid = str(t.get("id") or "")
        if tid:
            by_id[tid] = dict(t)

    required = collect_required_tool_ids(proto)
    for tid in required:
        if tid not in by_id:
            by_id[tid] = tool_stub(tid)

    ordered = [by_id[tid] for tid in required if tid in by_id]
    for tid, t in by_id.items():
        if tid not in required:
            ordered.append(t)
    return ordered


def seed_tool_link_rows() -> list[dict[str, Any]]:
    """Neo4j W_tool_links rows — derived from Protocol builders only."""
    from protocol import PROTOCOL_BUILDERS

    rows = []
    for sid, builder in PROTOCOL_BUILDERS.items():
        proto = builder()
        tools = collect_required_tool_ids(proto)
        if not tools:
            tools = ["T_CLOTH"]
        rows.append({"id": sid, "tools": tools})
    return rows


def seed_chem_link_rows() -> list[dict[str, Any]]:
    """Neo4j USES_CHEMICAL rows — chem_codes from base Protocol (pre-fabric)."""
    from protocol import PROTOCOL_BUILDERS

    rows = []
    for sid, builder in PROTOCOL_BUILDERS.items():
        proto = builder()
        # Include optional / white_only chems from template (not fabric-blocked yet)
        chems: list[str] = []
        for s in proto.steps:
            if s.chem and s.chem not in chems:
                chems.append(s.chem)
        if not chems:
            continue
        rows.append({"id": sid, "chems": chems})
    return rows


def never_mix_pairs() -> list[tuple[str, str]]:
    """Franchise-critical never-mix edges (chlorine + acid/ammonia)."""
    return [
        ("B2", "A5"),  # chlorine + ammonia → chloramine gas
        ("B2", "A3"),  # chlorine + vinegar/acid
        ("B2", "X2"),  # chlorine + oxalic (acid) — fix iron worse + fumes risk
        ("B2", "A4"),  # chlorine + peroxide — reactive; keep separate baths
        ("E1", "B2"),  # enzyme + chlorine kills enzyme / unsafe mix habit
        ("E2", "B2"),
        ("E3", "B2"),
    ]
