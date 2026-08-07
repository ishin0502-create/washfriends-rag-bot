# -*- coding: utf-8 -*-
"""Single-truth Protocol for franchise education answers.

Design:
  - Ordered steps are the only executable truth (chem / tool / minutes / force).
  - fresh_path_* / chemicals[] / spray·timer howto are *renders* of Protocol.
  - Fabric safety rewrites steps (block / replace / refuse) — never silent empty+S1
    while leaving vinegar narrative intact.
  - Item overlay is explicit: stain_primary (default) vs item_primary.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


CHEM_META: dict[str, dict[str, str]] = {
    "A3": {
        "name_ko": "흰 식초(식용 식초 약 5%)",
        "name_vi": "Giấm trắng 5%",
        "name_en": "White vinegar ~5%",
        "dilution_ko": "식초 1 : 물 4",
        "dilution_vi": "1 phần giấm + 4 phần nước",
        "dilution_en": "vinegar 1 : water 4",
    },
    "B1": {
        "name_ko": "산소계 표백제(과탄산 계열)",
        "name_vi": "Tẩy oxy",
        "name_en": "Oxygen bleach",
        "dilution_ko": "병 라벨 따름; 보통 15–45분 — 구석 색 테스트",
        "dilution_vi": "Theo nhãn chai; thường 15-45 phút — test màu",
        "dilution_en": "Per bottle label; usually 15–45 min — spot test",
    },
    "D2": {
        "name_ko": "주방세제(중성)",
        "name_vi": "Nước rửa chén",
        "name_en": "Dish soap",
        "dilution_ko": "얼룩에 1–2방울 또는 약하게 희석",
        "dilution_vi": "1-2 giọt hoặc pha loãng nhẹ",
        "dilution_en": "1–2 drops neat or light dilution",
    },
    "E1": {
        "name_ko": "단백질 분해 효소세제",
        "name_vi": "Enzyme protease",
        "name_en": "Protease enzyme",
        "dilution_ko": "병 안내; 찬물 15–30분",
        "dilution_vi": "Theo nhãn; nước lạnh 15-30 phút",
        "dilution_en": "Per label; cold 15–30 min",
    },
    "S1": {
        "name_ko": "워시프렌즈 중성세제",
        "name_vi": "Nước giặt trung tính Wash Friends",
        "name_en": "Wash Friends neutral detergent",
        "dilution_ko": "워시프렌즈 중성세제 병 안내 따름 — 실크·울 우선",
        "dilution_vi": "Theo hướng dẫn chai Wash Friends — ưu tiên lụa/len",
        "dilution_en": "Per Wash Friends bottle — silk/wool first",
    },
    "A1": {
        "name_ko": "이소프로필 알코올(소독용)",
        "name_vi": "Cồn isopropyl",
        "name_en": "Isopropyl alcohol",
        "dilution_ko": "원액 또는 병 안내 — 구석 테스트, 환기",
        "dilution_vi": "Nguyên hoặc theo nhãn — test góc, thông gió",
        "dilution_en": "Neat or per label — corner test, ventilate",
    },
    "N3": {
        "name_ko": "옥수수전분·전분(흡착)",
        "name_vi": "Bột ngô / tinh bột",
        "name_en": "Cornstarch / starch absorbent",
        "dilution_ko": "두껍게 덮어 10–30분 후 털기",
        "dilution_vi": "Phủ dày 10-30 phút rồi phủi",
        "dilution_en": "Thick cover 10–30 min then brush off",
    },
    "N2": {
        "name_ko": "소금(흡착·찬물 보조)",
        "name_vi": "Muối ăn",
        "name_en": "Table salt",
        "dilution_ko": "신선 얼룩: 키친타월·소금으로 흡수(선택)",
        "dilution_vi": "Vết tươi: muối/giấy thấm (tuỳ chọn)",
        "dilution_en": "Fresh: salt/paper absorb (optional)",
    },
}


ITEM_PRIMARY_IDS = frozenset({
    "I_NECKTIE", "I_SUIT", "I_AO_DAI", "I_HANBOK",
    "I_FUR_REAL", "I_FUR_FAUX", "I_GOLF_GLOVE_LEATHER",
    "I_COLOR_FADE", "I_LEATHER_GARMENT", "I_LEATHER_BAG", "I_LEATHER_SHOE",
    "I_SUEDE_GARMENT", "I_SUEDE_BAG", "I_SUEDE_SHOE", "I_GLOVE_LEATHER",
})


@dataclass
class Step:
    id: str
    action_ko: str
    action_vi: str = ""
    action_en: str = ""
    chem: Optional[str] = None
    tool_ids: list[str] = field(default_factory=list)
    minutes_lo: Optional[int] = None
    minutes_hi: Optional[int] = None
    force: str = "Cap1"
    spray: bool = False
    soak: bool = False
    optional: bool = False
    when: str = "always"
    blocked: bool = False
    block_reason_ko: str = ""
    block_reason_vi: str = ""
    alt_chem: Optional[str] = None
    alt_action_ko: str = ""


@dataclass
class Protocol:
    stain_id: str
    mode: str = "stain_primary"
    steps: list[Step] = field(default_factory=list)
    why_ko: str = ""
    why_vi: str = ""
    fabric: str = ""
    weight: str = "unknown"
    garment_color: str = ""
    water_temp_ko: str = "찬물"
    water_temp_vi: str = "Nước lạnh"

    def active_steps(self) -> list[Step]:
        return [s for s in self.steps if not s.blocked]

    def spray_step(self) -> Optional[Step]:
        for s in self.active_steps():
            if s.spray and s.chem:
                return s
        return None

    def soak_step(self) -> Optional[Step]:
        for s in self.active_steps():
            if s.soak:
                return s
        return self.spray_step()

    def chem_codes(self) -> list[str]:
        out = []
        for s in self.active_steps():
            code = s.chem
            if code and code not in out:
                out.append(code)
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "stain_id": self.stain_id,
            "mode": self.mode,
            "fabric": self.fabric,
            "weight": self.weight,
            "garment_color": self.garment_color,
            "water_temp_ko": self.water_temp_ko,
            "water_temp_vi": self.water_temp_vi,
            "why_ko": self.why_ko,
            "why_vi": self.why_vi,
            "steps": [asdict(s) for s in self.steps],
            "spray_chem": (self.spray_step().chem if self.spray_step() else None),
            "chem_order": self.chem_codes(),
        }


def _tpl_red_wine() -> Protocol:
    return Protocol(
        stain_id="S_RED_WINE",
        why_ko="[왜 이 순서] 레드와인=안토시아닌+탄닌+산/당. 즉시·찬물. 흡수→식초 1:4→흰옷 산소. 건조하면 적자색 고착. 유색: 테스트, 락스 금지.",
        why_vi="GIAO DUC: Ruou vang do = anthocyanin + tannin. SOM + LANH. Tham → giấm 1:4 → oxy trang. CAM say khoa mau.",
        water_temp_ko="찬물 (미온은 식초·세탁 이후만)",
        water_temp_vi="Lạnh (ấm chỉ sau giấm/giặt)",
        steps=[
            Step("id", "레드와인·신선 여부·원단·색 확인", "Nhận: rượu vang đỏ, tươi, vải, màu", force="Cap1"),
            Step(
                "absorb",
                "바깥→안 흡수(소금/키친타월) — 문지르기 금지",
                "Thấm muối/giấy NGOÀI→TRONG — không chà",
                chem="N2",
                tool_ids=["T_CLOTH"],
                force="Cap1",
                optional=True,
            ),
            Step("rinse", "찬물 헹굼(안쪽)", "Xả lạnh mặt trái", tool_ids=["T_CLOTH"], force="Cap1"),
            Step(
                "vinegar",
                "식초 1:4 도포·분무 또는 담금",
                "Giấm 1:4 xịt/ngâm",
                chem="A3",
                tool_ids=["T_SPRAY", "T_SOAK_BIN", "T_TIMER"],
                minutes_lo=5,
                minutes_hi=15,
                force="Cap1–2",
                spray=True,
                soak=True,
            ),
            Step(
                "oxygen",
                "흰/면 잔색: 산소표백(구석 테스트)",
                "Trắng/cotton còn màu: tẩy oxy (test)",
                chem="B1",
                tool_ids=["T_SOAK_BIN", "T_TIMER"],
                minutes_lo=15,
                minutes_hi=45,
                force="Cap1–2",
                soak=True,
                when="white_only",
            ),
            Step("wash", "찬물·미온 세탁", "Giặt lạnh/ấm nhẹ", force="Cap2"),
            Step(
                "light",
                "건조 전 강광 확인 — 잔색 있으면 식초 반복, 건조 금지",
                "Ánh sáng TRƯỚC sấy — còn màu: lặp giấm, không sấy",
                force="Cap1",
            ),
        ],
    )


def _tpl_tannin_simple(stain_id: str, name_ko: str, name_vi: str) -> Protocol:
    return Protocol(
        stain_id=stain_id,
        why_ko=f"[왜 이 순서] {name_ko}=탄닌·색소. 즉시·찬물. 식초 1:4 → 흰옷 산소. 열·건조 고착.",
        why_vi=f"GIAO DUC: {name_vi}=tannin. SOM+LANH → giấm 1:4 → oxy trắng.",
        steps=[
            Step("id", f"{name_ko}·신선·원단·색 확인", f"Nhận: {name_vi}", force="Cap1"),
            Step("rinse", "찬물 흡수·헹굼(안쪽) — 문지르기 금지", "Xả/thấm lạnh — không chà", tool_ids=["T_CLOTH"], force="Cap1"),
            Step(
                "vinegar",
                "식초 1:4",
                "Giấm 1:4",
                chem="A3",
                tool_ids=["T_SPRAY", "T_SOAK_BIN", "T_TIMER"],
                minutes_lo=5,
                minutes_hi=15,
                force="Cap1–2",
                spray=True,
                soak=True,
            ),
            Step(
                "oxygen",
                "흰/면 잔색: 산소표백",
                "Trắng còn màu: tẩy oxy",
                chem="B1",
                tool_ids=["T_SOAK_BIN", "T_TIMER"],
                minutes_lo=15,
                minutes_hi=45,
                when="white_only",
                soak=True,
            ),
            Step("wash", "미온·찬물 세탁", "Giặt ấm/lạnh", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_kimchi() -> Protocol:
    return Protocol(
        stain_id="S_KIMCHI",
        why_ko="[왜 이 순서] 김치=고추색소+기름+염/산. 고형 제거→찬물→주방세제(기름)→식초(색소)→흰옷 산소.",
        why_vi="GIAO DUC: Kimchi = màu ớt + dầu + muối/acid. D2 rồi A3 rồi B1 trắng.",
        steps=[
            Step("id", "김치·건더기·원단·색 확인", "Nhận kimchi", force="Cap1"),
            Step("scrape", "고춧가루·건더기 제거", "Cạo phần đặc", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("rinse", "안쪽 찬물 헹굼", "Xả lạnh mặt trái", force="Cap1"),
            Step(
                "dish",
                "주방세제 1–2방울 바깥→안",
                "Nước rửa chén 1-2 giọt NGOÀI→TRONG",
                chem="D2",
                tool_ids=["T_CLOTH", "T_BRUSH_SOFT"],
                force="Cap2",
            ),
            Step(
                "vinegar",
                "식초 1:4 (색소·냄새)",
                "Giấm 1:4",
                chem="A3",
                tool_ids=["T_SPRAY", "T_SOAK_BIN", "T_TIMER"],
                minutes_lo=5,
                minutes_hi=10,
                force="Cap1–2",
                spray=True,
                soak=True,
            ),
            Step(
                "oxygen",
                "흰옷 잔색만 산소표백",
                "Trắng: tẩy oxy",
                chem="B1",
                when="white_only",
                soak=True,
                minutes_lo=15,
                minutes_hi=45,
            ),
            Step("wash", "세탁; 잔색 채 건조 금지", "Giặt; không sấy khi còn màu", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_cooking_oil() -> Protocol:
    return Protocol(
        stain_id="S_COOKING_OIL",
        why_ko="[왜 이 순서] 식용유=소수성 오일. 전분 흡착→주방세제. 미끄럼 남은 채 건조=열고착.",
        why_vi="GIAO DUC: Dầu ăn = hydrophobic. N3 hút → D2. CAM sấy khi còn nhờn.",
        steps=[
            Step("id", "식용유(오토바이 오일 아님)·원단 확인", "Nhận dầu ăn", force="Cap1"),
            Step(
                "absorb",
                "전분·옥수수전분 덮고 털기",
                "Phủ N3 rồi phủi",
                chem="N3",
                tool_ids=["T_CLOTH"],
                minutes_lo=10,
                minutes_hi=30,
                force="Cap1",
            ),
            Step(
                "dish",
                "주방세제 Cap2 미온",
                "D2 Cap2 nước ấm nhẹ",
                chem="D2",
                tool_ids=["T_CLOTH", "T_BRUSH_SOFT", "T_SPRAY"],
                force="Cap2",
                spray=True,
            ),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "미끄럼 없어진 뒤 건조·강광", "Hết nhờn mới sấy + ánh sáng", force="Cap1"),
        ],
    )


def _tpl_blood_fresh() -> Protocol:
    return Protocol(
        stain_id="S_BLOOD_FRESH",
        why_ko="[왜 이 순서] 신선 혈액=단백질. 찬물만. 온수·건조=열고착. 효소→흰면 산소. 실크·울: 효소·산소 금지.",
        why_vi="GIAO DUC: Máu tươi = protein. CHỈ lạnh. Enzyme rồi oxy trắng. Len/lụa: S1.",
        water_temp_ko="찬물만 (온수 금지)",
        water_temp_vi="CHỈ nước lạnh",
        steps=[
            Step("id", "신선 핏자국·원단 확인", "Nhận máu tươi", force="Cap1"),
            Step("rinse", "안쪽 찬물 헹굼 2–3분", "Xả lạnh mặt trái 2-3 phút", tool_ids=["T_CLOTH"], force="Cap1"),
            Step(
                "enzyme",
                "효소 찬물 침지",
                "Enzyme ngâm lạnh",
                chem="E1",
                tool_ids=["T_SOAK_BIN", "T_TIMER", "T_BRUSH_ULTRA"],
                minutes_lo=15,
                minutes_hi=30,
                soak=True,
                force="Cap1–2",
            ),
            Step(
                "oxygen",
                "흰 면만 산소(테스트)",
                "Cotton trắng: oxy (test)",
                chem="B1",
                when="white_only",
                minutes_lo=10,
                minutes_hi=30,
            ),
            Step("wash", "찬물 세탁", "Giặt lạnh", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


PROTOCOL_BUILDERS = {
    "S_RED_WINE": _tpl_red_wine,
    "S_BLACK_COFFEE": lambda: _tpl_tannin_simple("S_BLACK_COFFEE", "커피(블랙)", "cà phê đen"),
    "S_TEA": lambda: _tpl_tannin_simple("S_TEA", "차", "trà"),
    "S_FRUIT_JUICE": lambda: _tpl_tannin_simple("S_FRUIT_JUICE", "과일주스", "nước trái cây"),
    "S_SOFT_DRINK": lambda: _tpl_tannin_simple("S_SOFT_DRINK", "탄산·콜라", "nước ngọt"),
    "S_WHITE_WINE_BEER": lambda: _tpl_tannin_simple("S_WHITE_WINE_BEER", "화이트와인·맥주", "rượu trắng/bia"),
    "S_KIMCHI": _tpl_kimchi,
    "S_COOKING_OIL": _tpl_cooking_oil,
    "S_BLOOD_FRESH": _tpl_blood_fresh,
}


def has_protocol(stain_id: str) -> bool:
    return bool(stain_id) and stain_id in PROTOCOL_BUILDERS


def overlay_mode_for_item(item_id: str) -> str:
    if item_id in ITEM_PRIMARY_IDS:
        return "item_primary"
    return "stain_primary"


def _fabric_flags(graph: dict, entities: Optional[dict] = None) -> dict[str, Any]:
    fabric = graph.get("fabric_context") or {}
    entities = entities or {}
    fid = str(fabric.get("id") or "").upper()
    fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''} {entities.get('fabric_type') or ''}".lower()
    is_silk = fid == "F4" or "silk" in fname or "lua" in fname
    is_wool = fid == "F3" or "wool" in fname or " len" in f" {fname}" or fname.strip() == "len"
    is_leather = fid == "F8" or "leather" in fname or fname.strip() == "da"
    is_suede = fid == "F9" or "suede" in fname or "nubuck" in fname
    is_fur = fid == "F10" or "fur" in fname
    is_rayon = fid == "F7" or "rayon" in fname
    return {
        "is_silk": is_silk,
        "is_wool": is_wool,
        "is_leather": is_leather,
        "is_suede": is_suede,
        "is_fur": is_fur,
        "is_rayon": is_rayon,
        "delicate_protein": is_silk or is_wool,
        "no_oxygen": is_silk or is_wool or is_leather or is_suede or is_fur or is_rayon
        or fabric.get("can_oxygen") is False,
        "no_acid": fabric.get("acid_safe") is False or is_silk or is_wool,
        "no_enzyme": fabric.get("enzyme_safe") is False or is_silk or is_wool,
        "fname": fname,
        "fid": fid,
    }


def _chem_blocked(code: str, flags: dict, garment_color: str) -> tuple[bool, str, str]:
    c = (code or "").upper()
    if not c:
        return False, "", ""
    if flags.get("no_enzyme") and c in {"E1", "E2", "E3"}:
        return True, "실크·울 등: 효소 금지", "Len/lụa: cấm enzyme"
    if flags.get("no_acid") and c in {"A3", "A5", "X2"}:
        return True, "이 원단: 산(식초 등) 주의·금지", "Vải này: hạn chế acid"
    if flags.get("no_oxygen") and c in {"B1", "A4", "X1", "B2"}:
        return True, "이 원단: 산소/염소 표백 금지", "Vải này: cấm tẩy oxy/Javel"
    if garment_color in {"colored", "black"} and c in {"B2", "X1"}:
        return True, "유색·검정: 염소·환원표백 금지", "Màu/đen: cấm Javel"
    if garment_color == "black" and c in {"B1", "A4"}:
        return True, "검정: 표백 금지", "Đen: cấm tẩy"
    if (flags.get("is_leather") or flags.get("is_suede") or flags.get("is_fur")) and c in {
        "B1", "B2", "A3", "A4", "E1", "E2", "D3", "X1", "X2",
    }:
        return True, "가죽·스웨이드·모피: 해당 약품 금지", "Da/suede/fur: cấm hoá chất này"
    return False, "", ""


def apply_context_to_protocol(
    proto: Protocol,
    *,
    fabric: str = "",
    weight: str = "unknown",
    garment_color: str = "",
    flags: Optional[dict] = None,
) -> Protocol:
    out = deepcopy(proto)
    out.fabric = fabric or out.fabric
    out.weight = weight or out.weight
    out.garment_color = garment_color or out.garment_color
    flags = flags or {}
    color = (out.garment_color or "").lower()

    for s in out.steps:
        if s.when == "white_only" and color and color != "white":
            s.blocked = True
            s.block_reason_ko = "유색·색미상: 산소표백 단계 생략(흰옷만). 색 확인 후 재적용."
            s.block_reason_vi = "Không trắng: bỏ bước oxy. Xác nhận màu rồi mới dùng."
            continue

        if not s.chem:
            continue
        blocked, rk, rv = _chem_blocked(s.chem, flags, color)
        if not blocked:
            continue

        # Protein delicates: replace enzyme/oxygen/acid step with explicit S1 local care
        if flags.get("delicate_protein") and s.chem in {"E1", "E2", "E3", "B1", "A3"}:
            s.chem = "S1"
            s.action_ko = "실크·울: 중성세제 국소·찬물만 — 효소·산소·강한 산 대신. 심하면 거절·전문."
            s.action_vi = "Len/lụa: chỉ S1 cục bộ nước lạnh — không enzyme/oxy/acid mạnh."
            s.spray = False
            s.soak = False
            s.minutes_lo = None
            s.minutes_hi = None
            s.blocked = False
            s.block_reason_ko = ""
            continue

        s.blocked = True
        s.block_reason_ko = rk
        s.block_reason_vi = rv

    if weight == "thin":
        for s in out.steps:
            if s.force in {"Cap2", "Cap3", "Cap4"}:
                s.force = "Cap1–2"
            s.tool_ids = [t for t in s.tool_ids if t != "T_BRUSH_HARD"]

    return out


def render_fresh_path(proto: Protocol, lang: str = "ko") -> str:
    parts = []
    n = 0
    for s in proto.steps:
        if s.blocked:
            continue
        n += 1
        if lang == "ko":
            text = s.action_ko
            if s.minutes_lo is not None:
                if s.minutes_hi and s.minutes_hi != s.minutes_lo:
                    text = f"{text} ({s.minutes_lo}–{s.minutes_hi}분)"
                else:
                    text = f"{text} ({s.minutes_lo}분)"
            if s.optional:
                text = f"{text} (선택)"
        else:
            text = s.action_vi or s.action_ko
            if s.minutes_lo is not None:
                if s.minutes_hi and s.minutes_hi != s.minutes_lo:
                    text = f"{text} ({s.minutes_lo}-{s.minutes_hi} phút)"
                else:
                    text = f"{text} ({s.minutes_lo} phút)"
        parts.append(f"({n}) {text}")
    return " → ".join(parts) if parts else ""


def render_chemicals(proto: Protocol, graph_chems: Optional[list] = None) -> list[dict]:
    by_code = {}
    for c in graph_chems or []:
        if c and c.get("code"):
            by_code[str(c["code"]).upper()] = dict(c)

    out = []
    seen = set()
    for s in proto.steps:
        if s.blocked or not s.chem:
            continue
        code = s.chem.upper()
        if code in seen:
            continue
        seen.add(code)
        meta = CHEM_META.get(code, {})
        base = dict(by_code.get(code) or {})
        base["code"] = code
        base["name_ko"] = base.get("name_ko") or meta.get("name_ko") or code
        base["name_vi"] = base.get("name_vi") or meta.get("name_vi") or code
        base["name"] = base.get("name") or meta.get("name_en") or code
        base["dilution_ko"] = base.get("dilution_ko") or meta.get("dilution_ko") or ""
        base["dilution_vi"] = base.get("dilution_vi") or meta.get("dilution_vi") or ""
        base["protocol_order"] = len(out) + 1
        base["protocol_step"] = s.id
        out.append(base)
    return out


def bind_tools_from_protocol(proto: Protocol, tools: list) -> list:
    if not tools:
        return tools
    sp = proto.spray_step()
    # Prefer A3 soak window over B1 15–45 when both exist
    minute_step = None
    for s in proto.active_steps():
        if s.soak and s.chem == "A3" and s.minutes_lo is not None:
            minute_step = s
            break
    if minute_step is None:
        for s in proto.active_steps():
            if s.soak and s.minutes_lo is not None:
                minute_step = s
                break
    if minute_step is None:
        minute_step = sp

    lo = minute_step.minutes_lo if minute_step else None
    hi = minute_step.minutes_hi if minute_step else lo
    if lo is None:
        min_ko, min_vi = "규정 분", "đúng phút quy định"
    elif hi and hi != lo:
        min_ko, min_vi = f"{lo}–{hi}분", f"{lo}-{hi} phút"
    else:
        min_ko, min_vi = f"{lo}분", f"{lo} phút"

    spray_name_ko = "희석 약품"
    spray_dil_ko = "병·경로 희석"
    spray_name_vi = "dung dịch pha"
    spray_dil_vi = "theo pha"
    if sp and sp.chem:
        meta = CHEM_META.get(sp.chem.upper(), {})
        spray_name_ko = meta.get("name_ko") or sp.chem
        spray_dil_ko = meta.get("dilution_ko") or spray_dil_ko
        spray_name_vi = meta.get("name_vi") or sp.chem
        spray_dil_vi = meta.get("dilution_vi") or spray_dil_vi

    bound = []
    for t in tools:
        t = dict(t)
        tid = str(t.get("id") or "")
        if tid == "T_SPRAY" and sp and sp.chem:
            t["use_for_ko"] = (
                f"이 얼룩용: 「{spray_name_ko}」을 「{spray_dil_ko}」로 타서, "
                f"다른 약이 안 들어 있는 분무기에만 넣는다. 병 겉에 「{spray_name_ko} / {spray_dil_ko}」라고 적는다. "
                f"얼룩에 1–2번만 뿌리고 흠뻑 적시지 말 것."
            )
            t["use_for_vi"] = (
                f"Cho vết này: pha 「{spray_name_vi}」 theo 「{spray_dil_vi}」 vào bình RIÊNG. "
                f"Viết lên bình 「{spray_name_vi} / {spray_dil_vi}」. Xịt 1-2 phát — không ngập."
            )
            t["use_for_en"] = (
                f"Mix 「{spray_name_ko}」 at 「{spray_dil_ko}」 in a dedicated bottle. "
                f"Label the bottle. Mist 1–2 sprays — do not soak."
            )
        elif tid == "T_TIMER":
            t["use_for_ko"] = (
                f"이 오염·약품 기준 처리 시간은 {min_ko}. 타이머를 {min_ko}에 맞추고, "
                f"울리면 즉시 찬물로 헹군다. 감시 없이 밤새 담그지 말 것."
            )
            t["use_for_vi"] = (
                f"Thời gian xử lý: {min_vi}. Hẹn giờ {min_vi}; hết giờ → xả lạnh ngay. "
                f"Không để qua đêm không giám sát."
            )
        elif tid == "T_SOAK_BIN":
            t["use_for_ko"] = (
                f"희석액을 통에 만들어 {min_ko}만 담근다. 통에 약 이름을 적는다. "
                f"정장·넥타이·얇은 실크는 SOP에서 금하면 통담금 하지 말 것."
            )
            t["use_for_vi"] = (
                f"Pha dung dịch, ngâm đúng {min_vi}. Dán tên thuốc. "
                f"Cấm ngâm suit/cà vạt/lụa mỏng nếu SOP cấm."
            )
        bound.append(t)
    return bound


def build_protocol(graph: dict, entities: Optional[dict] = None) -> Optional[Protocol]:
    entities = entities or {}
    sc = graph.get("stain_context") or {}
    stain_id = str(sc.get("id") or entities.get("stain_id") or "")
    if not has_protocol(stain_id):
        return None

    item_id = str((graph.get("item_context") or {}).get("id") or entities.get("item_id") or "")
    mode = overlay_mode_for_item(item_id)
    proto = PROTOCOL_BUILDERS[stain_id]()
    proto.mode = mode
    if mode == "item_primary":
        return proto

    fabric = str(
        entities.get("fabric_type")
        or (graph.get("fabric_context") or {}).get("name")
        or ""
    )
    from match_diagnosis import infer_fabric_weight

    weight = entities.get("fabric_weight") or infer_fabric_weight(
        entities.get("_raw") or "",
        fabric_type=fabric,
        item_id=item_id,
    )
    color = str(entities.get("garment_color") or graph.get("garment_color") or "")
    flags = _fabric_flags(graph, entities)
    return apply_context_to_protocol(
        proto,
        fabric=fabric,
        weight=str(weight),
        garment_color=color,
        flags=flags,
    )


def apply_protocol_to_graph(graph: dict, entities: Optional[dict] = None) -> dict:
    """Sync paths / chemicals / tool howto from Protocol when stain_primary."""
    if not isinstance(graph, dict):
        return graph
    entities = entities or {}
    proto = build_protocol(graph, entities)
    if proto is None:
        return graph

    out = dict(graph)
    out["protocol"] = proto.to_dict()
    out["protocol_mode"] = proto.mode
    if proto.mode == "item_primary":
        return out

    sc = dict(out.get("stain_context") or {})
    path_ko = render_fresh_path(proto, "ko")
    path_vi = render_fresh_path(proto, "vi")
    if path_ko:
        sc["fresh_path_ko"] = path_ko
    if path_vi:
        sc["fresh_path_vi"] = path_vi
    if proto.why_ko:
        sc["why_ko"] = proto.why_ko
    if proto.why_vi:
        sc["why_vi"] = proto.why_vi
    if proto.water_temp_ko:
        sc["water_temp_ko"] = proto.water_temp_ko
    if proto.water_temp_vi:
        sc["water_temp_vi"] = proto.water_temp_vi
    out["stain_context"] = sc

    out["chemicals"] = render_chemicals(proto, out.get("chemicals") or [])
    out["tools"] = bind_tools_from_protocol(proto, list(out.get("tools") or []))
    sp = proto.spray_step()
    if sp and sp.chem:
        meta = CHEM_META.get(sp.chem.upper(), {})
        out["spray_recipe_ko"] = f"{meta.get('name_ko', sp.chem)} / {meta.get('dilution_ko', '')}"
        out["spray_recipe_vi"] = f"{meta.get('name_vi', sp.chem)} / {meta.get('dilution_vi', '')}"
    return out
