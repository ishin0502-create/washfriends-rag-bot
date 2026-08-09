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
    "E2": {
        "name_ko": "전분 분해 효소(아밀라아제)",
        "name_vi": "Enzyme amylase",
        "name_en": "Amylase enzyme",
        "dilution_ko": "전분 효소: 찬물 1L에 큰술 1(또는 병 표기) → 잘 녹여 15–60분 담금. 실크·울 금지.",
        "dilution_vi": "Amylase: 1 muỗng canh / 1L nước lạnh (hoặc theo nhãn) → ngâm 15–60 phút. CẤM lụa/len.",
        "dilution_en": "Amylase: 1 tbsp / 1L cold (or per label); soak 15–60 min. No silk/wool.",
    },
    "A2": {
        "name_ko": "아세톤(네일리무버 계열)",
        "name_vi": "Acetone",
        "name_en": "Acetone",
        "dilution_ko": "원액 극소량만 — 흰 천/솜에 묻혀 안쪽 Cap1 블롯(흡수지 아래). 아세테이트·레이온·트리아세테이트 즉시 금지. 환기·PPE.",
        "dilution_vi": "Nguyên chất rất ít — thấm khăn mặt trái Cap1 (giấy thấm dưới). CẤM acetate/rayon/triacetate. Thông gió + PPE.",
        "dilution_en": "Neat tiny amount on cloth; Cap1 blot from reverse with blotter under. Never acetate/rayon/triacetate. Ventilate + PPE.",
    },
    "B2": {
        "name_ko": "염소계 표백제(락스/자벨)",
        "name_vi": "Javel",
        "name_en": "Chlorine bleach",
        "dilution_ko": "흰 면만. 예: 가정용 자벨/락스 원액 1 : 물 10–20(병 우선) · 짧은 담금·즉시 헹굼. 유색·실크·울·아세테이트 금지. 식초·암모니아와 절대 혼합 금지.",
        "dilution_vi": "CHỈ cotton TRẮNG. VD: Javel đặc 1 : nước 10–20 (ưu tiên nhãn) · ngâm ngắn · xả ngay. CẤM màu/lụa/len/acetate. CẤM trộn giấm/amoniac.",
        "dilution_en": "White cotton only. Example: household chlorine 1 : water 10–20 (label first); short soak then rinse. Never color/silk/wool/acetate. Never mix vinegar/ammonia.",
    },
    "E3": {
        "name_ko": "리파아제(지방 분해 효소)",
        "name_vi": "Enzyme lipase",
        "name_en": "Lipase enzyme",
        "dilution_ko": "리파아제: 병 표기; 보통 미온 1L에 큰술 1 → 탈지 후 15–30분 담금. 실크·울 주의.",
        "dilution_vi": "Lipase: theo nhãn; thường 1 muỗng / 1L ấm nhẹ → ngâm 15–30 phút sau khử dầu.",
        "dilution_en": "Lipase: per label; often 1 tbsp / 1L warm; soak 15–30 min after degrease.",
    },
    "B1": {
        "name_ko": "산소계 표백제(과탄산 계열) — 흰옷만",
        "name_vi": "Tẩy oxy — CHỈ đồ trắng",
        "name_en": "Oxygen bleach — white garments only",
        "dilution_ko": "흰옷만·구석 색 테스트. 병 라벨; 보통 찬물·미지근 1L에 큰술 1–2 → 15–45분. 유색·색 미확인·실크·울 금지.",
        "dilution_vi": "CHỈ trắng + test góc. Theo nhãn; thường 1–2 muỗng / 1L lạnh/ấm → 15–45 phút. CẤM màu/chưa rõ/lụa/len.",
        "dilution_en": "White only + corner test. Per label; often 1–2 tbsp / 1L cold–warm; 15–45 min. Never colored/unknown/silk/wool.",
    },
    "E1": {
        "name_ko": "단백질 분해 효소세제",
        "name_vi": "Enzyme protease",
        "name_en": "Protease enzyme",
        "dilution_ko": "단백질 효소: 찬물 1L에 큰술 1 → 잘 녹여 15–60분(병 우선). 실크·울 금지→중성세제.",
        "dilution_vi": "Protease: 1 muỗng / 1L lạnh → ngâm 15–60 phút (ưu tiên nhãn). CẤM lụa/len → S1.",
        "dilution_en": "Protease: 1 tbsp / 1L cold; soak 15–60 min (label first). No silk/wool → neutral.",
    },
    "D2": {
        "name_ko": "주방세제(중성)",
        "name_vi": "Nước rửa chén",
        "name_en": "Dish soap",
        "dilution_ko": "얼룩에 1–2방울 또는 약하게 희석",
        "dilution_vi": "1-2 giọt hoặc pha loãng nhẹ",
        "dilution_en": "1–2 drops neat or light dilution",
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
    "L1": {
        "name_ko": "가죽 전용 클리너",
        "name_vi": "Dung dịch vệ sinh da (leather cleaner)",
        "name_en": "Leather cleaner",
        "dilution_ko": "병 안내 — 천에 묻혀 국소만, 통담금·세탁기 금지",
        "dilution_vi": "Theo nhãn — khăn, không ngâm",
        "dilution_en": "Per bottle — cloth spot only, no soak",
    },
    "L2": {
        "name_ko": "가죽 크림·컨디셔너",
        "name_vi": "Kem dưỡng da (leather cream)",
        "name_en": "Leather cream / conditioner",
        "dilution_ko": "원액 얇게 → 잉여 닦기 (클리너 후 완전 건조 뒤)",
        "dilution_vi": "Nguyên mỏng → lau dư (sau khi khô)",
        "dilution_en": "Thin neat coat → wipe excess after dry",
    },
    "L3": {
        "name_ko": "가죽 프로텍터(방수·오염방지)",
        "name_vi": "Xịt bảo vệ da (protector)",
        "name_en": "Leather protector",
        "dilution_ko": "크림 마른 뒤 20–30cm 약분무(선택)",
        "dilution_vi": "Sau kem khô — xịt nhẹ 20-30cm (tuỳ chọn)",
        "dilution_en": "After cream cured — light spray 20–30cm optional",
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
    "D1": {
        "name_ko": "유성 얼룩용 용제(탈지)",
        "name_vi": "Dung môi tẩy dầu",
        "name_en": "Oil solvent / degreaser",
        "dilution_ko": "환기·PPE; 병 안내; 안쪽 블롯",
        "dilution_vi": "Thông gió+PPE; theo nhãn; thấm mặt trái",
        "dilution_en": "Ventilate+PPE; per label; blot from back",
    },
    "D3": {
        "name_ko": "일반 세탁세제",
        "name_vi": "Nước giặt thường",
        "name_en": "Laundry detergent",
        "dilution_ko": "병 안내·라벨 수온",
        "dilution_vi": "Theo nhãn / nhiệt độ nhãn",
        "dilution_en": "Per bottle / care-label temp",
    },
    "X2": {
        "name_ko": "옥살산(녹·철 얼룩용)",
        "name_vi": "Acid oxalic",
        "name_en": "Oxalic acid",
        "dilution_ko": "라벨 약 2–3%; 면·폴리 ~30분; 장갑 필수; 헹굼 후 중화",
        "dilution_vi": "~2-3% theo nhãn; cotton/poly ~30 phút; găng tay; xả + trung hòa",
        "dilution_en": "~2–3% per label; cotton/poly ~30 min; gloves; rinse+neutralize",
    },
    "N1": {
        "name_ko": "베이킹소다",
        "name_vi": "Baking soda",
        "name_en": "Baking soda",
        "dilution_ko": "페이스트 또는 약희석(중화·냄새)",
        "dilution_vi": "Bột nhão hoặc pha loãng",
        "dilution_en": "Paste or light dilution",
    },
    "A4": {
        "name_ko": "과산화수소 3%(옥시)",
        "name_vi": "Hydrogen peroxide 3%",
        "name_en": "Hydrogen peroxide 3%",
        "dilution_ko": "원액·구석 테스트; 흰 면 위주",
        "dilution_vi": "Nguyên/test góc; ưu tiên cotton trắng",
        "dilution_en": "Neat/corner test; prefer white cotton",
    },
    "A5": {
        "name_ko": "암모니아 희석액",
        "name_vi": "Amoniac pha loãng",
        "name_en": "Diluted ammonia",
        "dilution_ko": "약희석; 환기; 락스와 혼합 금지",
        "dilution_vi": "Pha loãng; thông gió; CAM trộn Javel",
        "dilution_en": "Dilute; ventilate; never mix with chlorine",
    },
    "X1": {
        "name_ko": "환원 표백제(하이드로설파이트)",
        "name_vi": "Tẩy khử (hydrosulfite)",
        "name_en": "Reducing bleach",
        "dilution_ko": "흰 면·린넨만; 즉석 조제; 장갑",
        "dilution_vi": "CHI cotton/linen trắng; pha mới; găng",
        "dilution_en": "White cotton/linen only; fresh mix; gloves",
    },
    "WF_SOFT": {
        "name_ko": "워시프렌즈 섬유유연제",
        "name_vi": "Nước xả Wash Friends",
        "name_en": "Wash Friends softener",
        "dilution_ko": "병 안내; 얼룩 처리 후 마무리만",
        "dilution_vi": "Theo nhãn; chỉ sau xử lý vết",
        "dilution_en": "Per bottle; finish only after stain work",
    },
    "WF_FRAG": {
        "name_ko": "워시프렌즈 독일 향수 스프레이",
        "name_vi": "Xịt hương Đức Wash Friends",
        "name_en": "Wash Friends fragrance spray",
        "dilution_ko": "건조·다림질 후 약분무",
        "dilution_vi": "Xịt nhẹ sau khô/ủi",
        "dilution_en": "Light mist after dry/iron",
    },
}

# Authoritative dilution/safety overwrite (v9) — single table for owner answers
try:
    from education_gaps_v9 import apply_dilution_to_chem_meta as _apply_dil_v9

    _apply_dil_v9(CHEM_META)
except Exception:
    pass


ITEM_PRIMARY_IDS = frozenset({
    "I_NECKTIE", "I_SUIT", "I_AO_DAI", "I_HANBOK",
    "I_ODOR_SMOKE", "I_UNIFORM",
    "I_FUR_REAL", "I_FUR_FAUX", "I_GOLF_GLOVE_LEATHER",
    "I_COLOR_FADE", "I_LEATHER_GARMENT", "I_LEATHER_BAG", "I_LEATHER_SHOE",
    "I_SUEDE_GARMENT", "I_SUEDE_BAG", "I_SUEDE_SHOE", "I_GLOVE_LEATHER",
    "I_DUVET_GOOSE", "I_DUVET_COTTON", "I_DOWN_JACKET",
    "I_MACHINE_PROFILE", "I_DRY_VS_WET",
    "I_SORT", "I_RINSE", "I_QC_HANDOVER",
    "I_CURTAIN_FABRIC", "I_CURTAIN_URETHANE", "I_DENIM", "I_GORETEX",
    "I_BABY_WEAR", "I_SWIMWEAR", "I_GOLF_WEAR", "I_GOLF_SHOE",
    "I_HIKING_SHOE", "I_RUNNING_MESH",
    "I_FAUX_LEATHER", "I_SNEAKER", "I_SNEAKER_WHITE", "I_SHOE_LACES",
    "I_HAT_CAP", "I_GOLF_HAT",
    "I_LINEN_GARMENT", "I_FINISHING", "I_SUIT_SUMMER", "I_DRESS", "I_DRESS_SHIRT",
    "I_FABRIC_COTTON", "I_FABRIC_POLY", "I_FABRIC_WOOL", "I_FABRIC_SILK",
    "I_FABRIC_LINEN", "I_FABRIC_DENIM", "I_FABRIC_RAYON",
    "I_FABRIC_LEATHER", "I_FABRIC_SUEDE", "I_FABRIC_FUR",
    "I_FABRIC_ACETATE", "I_FABRIC_NYLON", "I_FABRIC_BLEND",
    "I_CHEM_NEVER_MIX", "I_CHEM_BLEACH", "I_CHEM_SOLVENT", "I_CHEM_ACID_PPE",
    "I_CARE_LABEL", "I_INTAKE_SCRIPT", "I_CLAIM_SCRIPT", "I_PRICING_SCRIPT",
    "I_QUIZ_STAINS", "I_QUIZ_FABRIC", "I_WATER_HARDNESS",
    "I_COLOR_FADE", "I_WHITE_FADE",
    "I_KNIT", "I_UNDERWEAR", "I_ACTIVEWEAR", "I_SCARF", "I_GOLF_GLOVE_SYNTH",
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
        why_ko="[왜 이 순서] 신선 혈액=단백질·바이오하자드. PPE(장갑·마스크)→찬물만. 온수·건조=열고착. 효소→흰면 산소. 실크·울: 효소·산소 금지.",
        why_vi="GIAO DUC: Máu tươi = protein + biohazard. PPE → CHỈ lạnh. Enzyme rồi oxy trắng. Len/lụa: S1.",
        water_temp_ko="찬물만 (온수 금지)",
        water_temp_vi="CHỈ nước lạnh",
        steps=[
            Step("id", "신선 핏자국·PPE·원단 확인", "Nhận máu tươi + PPE", tool_ids=["T_GLOVE_NITRILE", "T_MASK"], force="Cap1"),
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


def _tpl_blood_dry() -> Protocol:
    return Protocol(
        stain_id="S_BLOOD_DRY",
        why_ko="[왜 이 순서] 마른 피=섬유 고착 단백질·바이오하자드. PPE→효소 장침지. 열 금지. 흰 면만 과산화/산소(테스트). 갈색 고착 시 성공률 낮음 고지.",
        why_vi="GIAO DUC: Máu khô = protein + biohazard. PPE → enzyme dài. CAM nhiệt. Oxy trắng test.",
        water_temp_ko="찬물만",
        water_temp_vi="CHỈ lạnh",
        steps=[
            Step("id", "마른 핏자국·PPE·원단 확인", "Nhận máu khô + PPE", tool_ids=["T_GLOVE_NITRILE", "T_MASK"], force="Cap1"),
            Step("brush", "마른 가루 Cap1 제거", "Cạo bột khô Cap1", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("rinse", "찬물 30–60분 담금", "Ngâm lạnh 30-60 phút", tool_ids=["T_SOAK_BIN", "T_TIMER"], minutes_lo=30, minutes_hi=60, soak=True, force="Cap1"),
            Step(
                "enzyme",
                "효소 희석 30–60분→연질 솔",
                "Enzyme 30-60 phút + chải mềm",
                chem="E1",
                tool_ids=["T_SOAK_BIN", "T_TIMER", "T_BRUSH_SOFT"],
                minutes_lo=30,
                minutes_hi=60,
                soak=True,
                force="Cap1–2",
            ),
            Step("oxygen", "흰 면만 산소/과산화(테스트)", "Trắng: oxy (test)", chem="B1", when="white_only", minutes_lo=10, minutes_hi=30),
            Step("wash", "찬물 세탁", "Giặt lạnh", force="Cap2"),
            Step("light", "건조 전 강광; 갈색 남으면 효소 반복·고지", "Ánh sáng; còn nâu → lặp enzyme", force="Cap1"),
        ],
    )


def _tpl_milk_coffee() -> Protocol:
    return Protocol(
        stain_id="S_MILK_COFFEE",
        why_ko="[왜 이 순서] 라떼=탄닌+우유 단백질/지방. 필수: 효소·주방세제(단백질·지방) 먼저 → 식초(탄닌) 나중. 순서 바꾸면 색소 고착.",
        why_vi="GIAO DUC: Latte = tannin + protein/mỡ sữa. Enzyme/D2 TRƯỚC → giấm SAU.",
        steps=[
            Step("id", "라떼·우유커피·원단 확인", "Nhận cà phê sữa", force="Cap1"),
            Step("rinse", "찬물 헹굼", "Xả lạnh", tool_ids=["T_CLOTH"], force="Cap1"),
            Step(
                "enzyme",
                "효소 15–30분(또는 지방 많으면 주방세제)",
                "Enzyme 15-30 phút (hoặc D2 nếu nhiều mỡ)",
                chem="E1",
                tool_ids=["T_SOAK_BIN", "T_TIMER"],
                minutes_lo=15,
                minutes_hi=30,
                soak=True,
                force="Cap1–2",
            ),
            Step(
                "vinegar",
                "헹굼 후 식초 1:4",
                "Xả rồi giấm 1:4",
                chem="A3",
                tool_ids=["T_SPRAY", "T_SOAK_BIN", "T_TIMER"],
                minutes_lo=5,
                minutes_hi=15,
                spray=True,
                soak=True,
                force="Cap1–2",
            ),
            Step("oxygen", "흰옷 잔색만 산소(테스트)", "Trắng: oxy", chem="B1", when="white_only"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_lipstick() -> Protocol:
    return Protocol(
        stain_id="S_LIPSTICK",
        why_ko="[왜 이 순서] 립스틱=왁스→오일→색소 3층. 긁기→알코올 안쪽 블롯→주방세제→흰옷 산소. 문지르면 색소 확산.",
        why_vi="GIAO DUC: Son = sáp→dầu→pigment. Cạo → A1 blot mặt trái → D2 → B1 trắng. CAM chà.",
        steps=[
            Step("id", "립스틱·원단·색 확인", "Nhận son môi", force="Cap1"),
            Step("scrape", "왁스·여분 Cap1 긁기", "Cạo sáp Cap1", tool_ids=["T_CLOTH"], force="Cap1"),
            Step(
                "alcohol",
                "알코올 안쪽 Cap1 블롯(흡수지 아래)",
                "A1 thấm mặt trái Cap1",
                chem="A1",
                tool_ids=["T_CLOTH", "T_GLOVE_NITRILE"],
                force="Cap1",
                spray=True,
            ),
            Step("dish", "주방세제 Cap2", "D2 Cap2", chem="D2", tool_ids=["T_CLOTH", "T_BRUSH_SOFT"], force="Cap2"),
            Step("oxygen", "흰옷 잔색 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁; 잔색 채 건조 금지", "Giặt; không sấy khi còn màu", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_grease_like(stain_id: str, name_ko: str, name_vi: str) -> Protocol:
    return Protocol(
        stain_id=stain_id,
        why_ko=f"[왜 이 순서] {name_ko}=소수성 오일/지방. 전분 흡착→주방세제. 미끄럼 남은 채 건조=열고착.",
        why_vi=f"GIAO DUC: {name_vi}=dầu. N3 → D2. CAM sấy khi còn nhờn.",
        steps=[
            Step("id", f"{name_ko}·원단 확인", f"Nhận {name_vi}", force="Cap1"),
            Step("absorb", "전분 10–30분 덮고 털기", "Phủ N3 10-30 phút", chem="N3", tool_ids=["T_CLOTH"], minutes_lo=10, minutes_hi=30, force="Cap1"),
            Step("dish", "주방세제 Cap2", "D2 Cap2", chem="D2", tool_ids=["T_CLOTH", "T_BRUSH_SOFT", "T_SPRAY"], force="Cap2", spray=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "미끄럼 없어진 뒤 건조·강광", "Hết nhờn mới sấy", force="Cap1"),
        ],
    )


def _tpl_motorbike_oil() -> Protocol:
    return Protocol(
        stain_id="S_MOTORBIKE_OIL",
        why_ko="[왜 이 순서] 오토바이 오일=중질유+색소. 전분 흡착→용제(환기)→알코올 스팟→일반세제. 미끄럼·냄새 남은 채 건조 금지.",
        why_vi="GIAO DUC: Dầu nhớt xe = dầu nặng + màu. N3 → D1 thông gió → A1 → D3. CAM sấy khi còn nhờn.",
        steps=[
            Step("id", "오토바이 오일(식용유 아님)·원단", "Nhận dầu nhớt xe", force="Cap1"),
            Step("absorb", "전분 두껍게 10–30분×가능하면 2회", "N3 dày 10-30 phút x2", chem="N3", minutes_lo=10, minutes_hi=30, force="Cap1"),
            Step(
                "solvent",
                "용제 안쪽 블롯(환기·장갑)",
                "D1 thấm mặt trái (thông gió+găng)",
                chem="D1",
                tool_ids=["T_CLOTH", "T_GLOVE_NITRILE", "T_SPRAY"],
                force="Cap1–2",
                spray=True,
            ),
            Step("alcohol", "잔색: 알코올 스팟(테스트)", "Còn màu: A1 test", chem="A1", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("detergent", "일반세제 세탁(면·폴리)", "Giặt D3 cotton/poly", chem="D3", force="Cap2"),
            Step("light", "미끄럼·냄새 확인 후 건조·강광", "Hết nhờn/mùi mới sấy", force="Cap1"),
        ],
    )


def _tpl_ink_pen() -> Protocol:
    return Protocol(
        stain_id="S_INK_PEN",
        why_ko="[왜 이 순서] 볼펜 잉크=염료. 알코올 안쪽 블롯만 — 문지르면 번짐. 흰옷 잔색 산소.",
        why_vi="GIAO DUC: Mực bút = dye. A1 blot mặt trái — CAM chà. B1 trắng nếu cần.",
        steps=[
            Step("id", "볼펜·잉크·원단", "Nhận mực bút", force="Cap1"),
            Step(
                "alcohol",
                "알코올 안쪽 Cap1 블롯·흡수지(환기)",
                "A1 thấm mặt trái Cap1",
                chem="A1",
                tool_ids=["T_CLOTH", "T_GLOVE_NITRILE", "T_SPRAY"],
                force="Cap1",
                spray=True,
            ),
            Step("oxygen", "흰옷 잔색 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "찬물 세탁", "Giặt lạnh", force="Cap2"),
            Step("light", "잉크 없어진 뒤 건조·강광", "Hết mực mới sấy", force="Cap1"),
        ],
    )


def _tpl_rust() -> Protocol:
    return Protocol(
        stain_id="S_RUST",
        why_ko="[왜 이 순서] 녹=산화철. 면·폴리: 옥살산+장갑. 실크·울: 옥살산 금지→식초 약하게. 락스로 철 고착 금지. 사용 후 헹굼·중화.",
        why_vi="GIAO DUC: Rỉ = Fe oxide. Cotton: X2 + găng. Len/lụa: A3 nhẹ. CAM Javel.",
        steps=[
            Step("id", "녹·원단·장갑 준비", "Nhận rỉ + PPE", force="Cap1"),
            Step(
                "oxalic",
                "옥살산(라벨)~30분·장갑 — 실크·울이면 이 단계 대체",
                "X2 ~30 phút + găng",
                chem="X2",
                tool_ids=["T_GLOVE_NITRILE", "T_CLOTH", "T_TIMER"],
                minutes_lo=20,
                minutes_hi=30,
                soak=True,
                force="Cap1–2",
            ),
            Step("rinse", "헹굼 + 베이킹소다 약희석 중화", "Xả + N1 loãng trung hòa", chem="N1", force="Cap1"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_bubble_tea() -> Protocol:
    return Protocol(
        stain_id="S_BUBBLE_TEA",
        why_ko="[왜 이 순서] 버블티=탄닌+우유 단백질+전분+설탕. 찬물→효소→주방세제→식초→흰옷 산소. 처음부터 온수 금지.",
        why_vi="GIAO DUC: Trà sữa = tannin+protein+tinh bột+đường. Lạnh → E → D2 → A3 → B1 trắng.",
        steps=[
            Step("id", "버블티·펄 제거·원단", "Nhận trà sữa, bỏ trân châu", force="Cap1"),
            Step("rinse", "즉시 찬물", "Xả lạnh ngay", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("enzyme", "효소 15–30분", "Enzyme 15-30 phút", chem="E1", tool_ids=["T_SOAK_BIN", "T_TIMER"], minutes_lo=15, minutes_hi=30, soak=True),
            Step("dish", "주방세제(유지방)", "D2", chem="D2", tool_ids=["T_CLOTH"], force="Cap2"),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", tool_ids=["T_SPRAY", "T_TIMER"], minutes_lo=5, minutes_hi=15, spray=True, soak=True),
            Step("oxygen", "흰옷 잔색 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁; 잔색·단맛 채 건조 금지", "Giặt; không sấy khi còn ngọt/màu", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_sauce_oil_tannin(stain_id: str, name_ko: str, name_vi: str) -> Protocol:
    """Ketchup / tomato: oil then vinegar then oxygen white."""
    return Protocol(
        stain_id=stain_id,
        why_ko=f"[왜 이 순서] {name_ko}=색소+기름막. 긁기→주방세제→식초→흰옷 산소. 문질러 번짐 금지.",
        why_vi=f"GIAO DUC: {name_vi}=màu+dầu. Cạo → D2 → A3 → B1 trắng.",
        steps=[
            Step("id", f"{name_ko}·원단", f"Nhận {name_vi}", force="Cap1"),
            Step("scrape", "고형 제거", "Cạo đặc", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("dish", "주방세제 바깥→안", "D2 NGOÀI→TRONG", chem="D2", tool_ids=["T_CLOTH", "T_BRUSH_SOFT"], force="Cap2"),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", tool_ids=["T_SPRAY", "T_TIMER"], minutes_lo=5, minutes_hi=10, spray=True, soak=True),
            Step("oxygen", "흰옷 잔색 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁; 잔색 채 건조 금지", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_mud() -> Protocol:
    return Protocol(
        stain_id="S_MUD",
        why_ko="[왜 이 순서] 진흙=흙입자. 완전히 마른 뒤 털기 — 젖은 채로 문지르면 섬유에 박힘. 그다음 세탁·필요 시 식초.",
        why_vi="GIAO DUC: Bùn = đất. Để KHÔ rồi chải — CAM chà khi ướt.",
        steps=[
            Step("id", "진흙·원단", "Nhận bùn", force="Cap1"),
            Step("dry", "완전히 마를 때까지 대기", "Để khô hoàn toàn", force="Cap1"),
            Step("brush", "마른 흙 털기(경질·연질)", "Chải đất khô", tool_ids=["T_BRUSH_HARD", "T_BRUSH_SOFT", "T_CLOTH"], force="Cap2"),
            Step("wash", "세탁", "Giặt", chem="D2", force="Cap2"),
            Step("vinegar", "잔여·냄새면 식초 1:4", "Còn: giấm 1:4", chem="A3", optional=True, spray=True, minutes_lo=5, minutes_hi=10),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_foundation() -> Protocol:
    p = _tpl_lipstick()
    p.stain_id = "S_FOUNDATION"
    p.why_ko = "[왜 이 순서] 파운데이션=오일 베이스+색소. 블롯→주방세제→잔색 알코올→흰옷 산소. 실크·울: 중성만."
    p.why_vi = "GIAO DUC: Kem nền = dầu+pigment. Blot → D2 → A1 → B1 trắng. Len/lụa: S1."
    p.steps[0] = Step("id", "파운데이션·쿠션·원단", "Nhận kem nền", force="Cap1")
    return p


def _tpl_protein_then_vinegar(stain_id: str, name_ko: str, name_vi: str) -> Protocol:
    """Soy / fish sauce: enzyme then vinegar then oxygen white."""
    return Protocol(
        stain_id=stain_id,
        why_ko=f"[왜 이 순서] {name_ko}=단백질+탄닌/색소. 찬물→효소→식초→흰옷 산소. 냄새는 식초.",
        why_vi=f"GIAO DUC: {name_vi}=protein+tannin. Lạnh → E → A3 → B1 trắng.",
        steps=[
            Step("id", f"{name_ko}·원단", f"Nhận {name_vi}", force="Cap1"),
            Step("rinse", "찬물 헹굼", "Xả lạnh", tool_ids=["T_CLOTH"], force="Cap1"),
            Step(
                "enzyme",
                "효소 15–30분",
                "Enzyme 15-30 phút",
                chem="E1",
                tool_ids=["T_SOAK_BIN", "T_TIMER"],
                minutes_lo=15,
                minutes_hi=30,
                soak=True,
            ),
            Step(
                "vinegar",
                "식초 1:4 (색소·냄새)",
                "Giấm 1:4",
                chem="A3",
                tool_ids=["T_SPRAY", "T_TIMER"],
                minutes_lo=5,
                minutes_hi=15,
                spray=True,
                soak=True,
            ),
            Step("oxygen", "흰옷 잔색 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_protein_simple(stain_id: str, name_ko: str, name_vi: str, *, minutes=(15, 30)) -> Protocol:
    lo, hi = minutes
    return Protocol(
        stain_id=stain_id,
        why_ko=f"[왜 이 순서] {name_ko}=단백질. 찬물·효소. 온수·건조=고착. 흰면 잔색만 산소.",
        why_vi=f"GIAO DUC: {name_vi}=protein. Lạnh + enzyme. CAM nóng/sấy sớm.",
        water_temp_ko="찬물 우선",
        water_temp_vi="Ưu tiên lạnh",
        steps=[
            Step("id", f"{name_ko}·원단", f"Nhận {name_vi}", force="Cap1"),
            Step("scrape", "고형 제거(해당 시)", "Cạo đặc nếu có", tool_ids=["T_CLOTH"], force="Cap1", optional=True),
            Step("rinse", "찬물 헹굼", "Xả lạnh", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("enzyme", "효소 침지", "Enzyme ngâm", chem="E1", tool_ids=["T_SOAK_BIN", "T_TIMER"], minutes_lo=lo, minutes_hi=hi, soak=True),
            Step("oxygen", "흰옷 잔색 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "찬물·미온 세탁", "Giặt lạnh/ấm nhẹ", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_mayo() -> Protocol:
    return Protocol(
        stain_id="S_MAYO",
        why_ko="[왜 이 순서] 마요=오일+계란 단백질. 기름(주방세제) 먼저→효소(단백질). 순서 바꾸면 지방이 단백질 고착.",
        why_vi="GIAO DUC: Mayo = dầu + trứng. D2 TRƯỚC → E1 SAU.",
        steps=[
            Step("id", "마요네즈·원단", "Nhận mayonnaise", force="Cap1"),
            Step("scrape", "고형 제거", "Cạo", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("dish", "주방세제 5–10분(기름 먼저)", "D2 5-10 phút", chem="D2", minutes_lo=5, minutes_hi=10, force="Cap2", spray=True),
            Step("enzyme", "헹굼 후 효소 15–30분", "Xả rồi enzyme 15-30", chem="E1", minutes_lo=15, minutes_hi=30, soak=True),
            Step("wash", "미온 세탁; 미끄럼 없어진 뒤 건조", "Giặt ấm; hết nhờn mới sấy", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_bbq() -> Protocol:
    return Protocol(
        stain_id="S_BBQ_SAUCE",
        why_ko="[왜 이 순서] BBQ=당/토마토 색소+기름+단백질. 효소→주방세제→식초→흰옷 산소. 잔여 채 열·건조 금지.",
        why_vi="GIAO DUC: BBQ = đường/màu + dầu + protein. E → D2 → A3 → B1.",
        steps=[
            Step("id", "BBQ 소스·원단", "Nhận sốt BBQ", force="Cap1"),
            Step("scrape", "고형 제거", "Cạo", force="Cap1"),
            Step("rinse", "찬물", "Xả lạnh", force="Cap1"),
            Step("enzyme", "효소 20–30분", "Enzyme 20-30", chem="E1", minutes_lo=20, minutes_hi=30, soak=True),
            Step("dish", "주방세제 Cap2", "D2 Cap2", chem="D2", force="Cap2"),
            Step("vinegar", "식초 1:4 ~15분", "Giấm 1:4 ~15 phút", chem="A3", minutes_lo=10, minutes_hi=15, spray=True, soak=True),
            Step("oxygen", "흰옷 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁; 건조 전 강광", "Giặt + ánh sáng", force="Cap2"),
        ],
    )


def _tpl_collar() -> Protocol:
    return Protocol(
        stain_id="S_COLLAR_STAIN",
        why_ko="[왜 이 순서] 목때=피지+땀 산화. 마른 깃에 효소 먼저. 락스 금지(더 누렇게). 이후 산소. 잔여 다림질 금지.",
        why_vi="GIAO DUC: Vòng cổ = bã nhờn+mồ hôi. Enzyme khô trước. CAM Javel. Rồi B1.",
        steps=[
            Step("id", "와이셔츠 깃·목때", "Nhận vòng cổ", force="Cap1"),
            Step("enzyme", "마른 깃에 효소 5–15분", "Enzyme trên cổ khô 5-15", chem="E1", minutes_lo=5, minutes_hi=15, force="Cap1–2"),
            Step("dish", "지방 많으면 주방세제", "Nhiều mỡ: D2", chem="D2", optional=True, force="Cap2"),
            Step("oxygen", "흰옷: 산소 미온 1–2시간(병 안내)", "Trắng: B1 1-2 giờ", chem="B1", when="white_only", minutes_lo=60, minutes_hi=120, soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "강광; 남으면 반복. 락스·잔여 다림질 금지", "Ánh sáng; CAM Javel/ủi khi còn vết", force="Cap1"),
        ],
    )


def _tpl_shirt_yellow() -> Protocol:
    return Protocol(
        stain_id="S_SHIRT_YELLOW",
        why_ko="[왜 이 순서] 흰 셔츠 황변=피지·땀 산화. 락스 금지. 효소→산소 장침지. 심한 흰 면만 환원표백(X1)·PPE. 깃만이면 목때 SOP.",
        why_vi="GIAO DUC: Áo trắng vàng = bã nhờn. CAM Javel. E → B1 dài. Nặng: X1 PPE (cotton trắng).",
        steps=[
            Step("id", "흰 셔츠 황변(이염 아님)", "Nhận vàng áo trắng", force="Cap1"),
            Step("enzyme", "황변 부위 효소 전처리", "Enzyme vùng vàng", chem="E1", tool_ids=["T_CLOTH", "T_BRUSH_SOFT", "T_SOAK_BIN", "T_TIMER"], force="Cap1–2", minutes_lo=15, minutes_hi=30, soak=True),
            Step("oxygen", "산소 미온 1–6시간(병·테스트)", "B1 ấm 1-6 giờ", chem="B1", when="white_only", minutes_lo=60, minutes_hi=360, soak=True, tool_ids=["T_SOAK_BIN", "T_TIMER"]),
            Step(
                "reducing",
                "심한 흰 면·린넨만: 환원표백 X1 즉석·15–30분·장갑(선택)",
                "Nặng cotton trắng: X1 mới pha 15-30 phút + găng (tuỳ)",
                chem="X1",
                when="white_only",
                optional=True,
                minutes_lo=15,
                minutes_hi=30,
                soak=True,
                tool_ids=["T_GLOVE_NITRILE", "T_TIMER", "T_SOAK_BIN"],
            ),
            Step("wash", "세제 세탁", "Giặt", chem="D3", force="Cap2"),
            Step("light", "강광; 락스 금지; 황변 남은 채 건조·다림질 금지", "Ánh sáng; CAM Javel", force="Cap1"),
        ],
    )


def _tpl_sweat_yellow() -> Protocol:
    return Protocol(
        stain_id="S_SWEAT_YELLOW",
        why_ko="[왜 이 순서] 겨드랑이 황변=땀+데오 잔여. 효소→산소(흰). 락스 금지. 냄새는 식초.",
        why_vi="GIAO DUC: Nách vàng = mồ hôi+deo. E → B1 trắng. CAM Javel. Mùi: A3.",
        steps=[
            Step("id", "겨드랑이 황변·원단", "Nhận nách vàng", force="Cap1"),
            Step("enzyme", "효소 15–30분", "Enzyme 15-30", chem="E1", minutes_lo=15, minutes_hi=30, soak=True),
            Step("oxygen", "흰/면: 산소 침지", "Trắng: B1", chem="B1", when="white_only", soak=True, minutes_lo=30, minutes_hi=120),
            Step("vinegar", "냄새: 식초 1:4", "Mùi: giấm 1:4", chem="A3", optional=True, spray=True, minutes_lo=5, minutes_hi=15),
            Step("wash", "세탁; 락스 금지", "Giặt; CAM Javel", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_grass() -> Protocol:
    return Protocol(
        stain_id="S_GRASS",
        why_ko="[왜 이 순서] 잔디=엽록소+단백질. 알코올 먼저→효소→흰옷 산소. 문지르면 녹색 번짐.",
        why_vi="GIAO DUC: Cỏ = chlorophyll+protein. A1 → E → B1 trắng.",
        steps=[
            Step("id", "잔디·풀물·원단", "Nhận cỏ xanh", force="Cap1"),
            Step("alcohol", "알코올 바깥→안 블롯", "A1 blot NGOÀI→TRONG", chem="A1", tool_ids=["T_CLOTH"], force="Cap1", spray=True),
            Step("enzyme", "효소 15–30분", "Enzyme 15-30", chem="E1", minutes_lo=15, minutes_hi=30, soak=True),
            Step("oxygen", "흰옷 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_chocolate() -> Protocol:
    return Protocol(
        stain_id="S_CHOCOLATE",
        why_ko="[왜 이 순서] 초코=지방+단백질+탄닌. 긁기→찬물→효소→주방세제→식초→흰옷 산소.",
        why_vi="GIAO DUC: Socola = mỡ+protein+tannin. Cạo → E → D2 → A3 → B1.",
        steps=[
            Step("id", "초콜릿·원단", "Nhận socola", force="Cap1"),
            Step("scrape", "고형 긁기", "Cạo", force="Cap1"),
            Step("rinse", "찬물", "Xả lạnh", force="Cap1"),
            Step("enzyme", "효소 15–30분", "Enzyme", chem="E1", minutes_lo=15, minutes_hi=30, soak=True),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2"),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", spray=True, minutes_lo=5, minutes_hi=15),
            Step("oxygen", "흰옷 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_curry_mustard(stain_id: str, name_ko: str, name_vi: str) -> Protocol:
    return Protocol(
        stain_id=stain_id,
        why_ko=f"[왜 이 순서] {name_ko}=커큐민 색소(+기름). 긁기→주방세제→베이킹소다→흰옷 산소/짧은 햇볕. 이른 열 고착.",
        why_vi=f"GIAO DUC: {name_vi}=curcumin. Cạo → D2 → N1 → B1/nắng ngắn.",
        steps=[
            Step("id", f"{name_ko}·원단·색", f"Nhận {name_vi}", force="Cap1"),
            Step("scrape", "여분 제거", "Cạo", force="Cap1"),
            Step("dish", "주방세제(기름)", "D2", chem="D2", force="Cap2", spray=True),
            Step("soda", "베이킹소다 페이스트 15–30분", "N1 paste 15-30", chem="N1", minutes_lo=15, minutes_hi=30),
            Step("oxygen", "흰/면: 산소(테스트)", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁; 유색은 산소 신중", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_ink_permanent() -> Protocol:
    return Protocol(
        stain_id="S_INK_PERMANENT",
        why_ko="[왜 이 순서] 유성매직=강한 염료. 아세톤/알코올 테스트 후 안쪽 블롯. 100% 비보장. 아세테이트·레이온+아세톤 금지.",
        why_vi="GIAO DUC: Bút lông = dye mạnh. A2/A1 test + blot. Không cam kết 100%.",
        steps=[
            Step("id", "유성매직·원단 테스트", "Nhận bút lông + test", force="Cap1"),
            Step("acetone", "아세톤 극소량 안쪽 블롯(환기·테스트)", "A2 rất ít mặt trái", chem="A2", tool_ids=["T_CLOTH", "T_GLOVE_NITRILE"], force="Cap1", spray=True),
            Step("alcohol", "또는 알코올 반복 블롯", "Hoặc A1 lặp", chem="A1", optional=True, force="Cap1"),
            Step("oxygen", "흰옷 잔색 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁; 잔색 가능 고지", "Giặt; báo còn mực", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_nail_polish() -> Protocol:
    return Protocol(
        stain_id="S_NAIL_POLISH",
        why_ko="[왜 이 순서] 매니큐어=용제+색소. 아세톤 안쪽만 — 문질러 섬유에 박지 말 것. 아세테이트 금지.",
        why_vi="GIAO DUC: Sơn móng = dung môi+màu. A2 mặt trái — CAM chà. CAM acetate.",
        steps=[
            Step("id", "매니큐어·원단", "Nhận sơn móng", force="Cap1"),
            Step("acetone", "아세톤 안쪽 Cap1 블롯(환기)", "A2 thấm mặt trái", chem="A2", tool_ids=["T_CLOTH", "T_GLOVE_NITRILE"], force="Cap1", spray=True),
            Step("wash", "세제 세탁", "Giặt", chem="D2", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_dye_transfer() -> Protocol:
    return Protocol(
        stain_id="S_DYE_TRANSFER",
        why_ko="[왜 이 순서] 이염=타 옷 색소 전이. 건조·다림질 금지. 산소 장침지→재세탁. 흰 면만 희석 락스 신중. 100% 비보장.",
        why_vi="GIAO DUC: Lo màu. CAM sấy/ủi. B1 ngâm dài → giặt. Javel chỉ trắng cẩn thận.",
        steps=[
            Step("id", "이염·흰/유색·원단 구분 — 건조 금지", "Nhận lo màu — CAM sấy", force="Cap1"),
            Step("oxygen", "산소 장침지(병 최대, 종종 수시간)", "B1 ngâm dài", chem="B1", minutes_lo=120, minutes_hi=480, soak=True),
            Step("wash", "세제 재세탁", "Giặt lại", chem="D3", force="Cap2"),
            Step("chlorine", "흰 면만 희석 락스(안전할 때만)", "Trắng cotton: Javel loãng", chem="B2", when="white_only", optional=True),
            Step("light", "강광; 잔색 채 건조 금지·고지", "Ánh sáng; báo không 100%", force="Cap1"),
        ],
    )


def _tpl_laterite() -> Protocol:
    return Protocol(
        stain_id="S_LATERITE",
        why_ko="[왜 이 순서] 라테라이트=철 산화 적토. 마른 뒤 털기→면은 옥살산+장갑. 실크·울: 옥살산 금지→식초 약. 락스로 철 고착 금지.",
        why_vi="GIAO DUC: Laterite = Fe đất đỏ. Khô chải → X2 cotton. Len/lụa: A3. CAM Javel.",
        steps=[
            Step("id", "적토·라테라이트·원단", "Nhận đất đỏ laterite", force="Cap1"),
            Step("dry", "마른 뒤 흙 털기", "Để khô rồi phủi", tool_ids=["T_BRUSH_HARD", "T_CLOTH"], force="Cap2"),
            Step("oxalic", "옥살산 ~30분·장갑", "X2 ~30 phút + găng", chem="X2", minutes_lo=20, minutes_hi=30, soak=True, tool_ids=["T_GLOVE_NITRILE", "T_TIMER"]),
            Step("rinse", "헹굼+베이킹소다 중화", "Xả + N1 trung hòa", chem="N1", force="Cap1"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_mildew() -> Protocol:
    return Protocol(
        stain_id="S_MILDEW",
        why_ko="[왜 이 순서] 곰팡이=포자+색소. PPE·환기. 식초로 살균→산소로 색소→흰 면만 락스 신중. 맑아질 때까지 건조 금지.",
        why_vi="GIAO DUC: Mốc. PPE. A3 diệt → B1 màu → Javel chỉ trắng. CAM sấy khi còn.",
        steps=[
            Step("id", "곰팡이·PPE·야외/환기", "Nhận mốc + PPE", tool_ids=["T_GLOVE_NITRILE", "T_MASK"], force="Cap1"),
            Step("brush", "마른 포자 털기(마스크)", "Chải khô + khẩu trang", tool_ids=["T_BRUSH_SOFT", "T_CLOTH", "T_MASK"], force="Cap1"),
            Step("vinegar", "식초 1:4 침지·살균", "Giấm 1:4 ngâm", chem="A3", minutes_lo=15, minutes_hi=30, soak=True, spray=True, tool_ids=["T_SPRAY", "T_SOAK_BIN", "T_TIMER"]),
            Step("oxygen", "색소: 산소", "Màu: B1", chem="B1", soak=True, minutes_lo=30, minutes_hi=120, tool_ids=["T_SOAK_BIN", "T_TIMER"]),
            Step("chlorine", "흰 면만 희석 락스(선택)", "Trắng: Javel loãng", chem="B2", when="white_only", optional=True, tool_ids=["T_GLOVE_NITRILE"]),
            Step("wash", "세탁; 맑아질 때까지 건조 금지", "Giặt; CAM sấy khi còn mốc", force="Cap2"),
            Step("light", "강광·통풍 건조", "Ánh sáng + thoáng", force="Cap1"),
        ],
    )


def _tpl_gum() -> Protocol:
    return Protocol(
        stain_id="S_GUM",
        why_ko="[왜 이 순서] 껌=끈적 폴리머. 핵심은 냉동. 바삭할 때 깨기→잔여 아세톤 극소(아세테이트 금지)·PPE→세제.",
        why_vi="GIAO DUC: Kẹo cao su. ĐÔNG lạnh → bẻ → A2 ít + PPE → D2.",
        steps=[
            Step("id", "껌·원단", "Nhận kẹo cao su", force="Cap1"),
            Step("freeze", "비닐+냉동 30–60분 단단해질 때까지", "Túi + đông 30-60 phút", minutes_lo=30, minutes_hi=60, tool_ids=["T_TIMER"], force="Cap1"),
            Step("break", "바삭할 때 Cap2로 깨서 제거", "Bẻ khi giòn Cap2", tool_ids=["T_CLOTH"], force="Cap2"),
            Step("acetone", "잔여 유분: 아세톤 극소(테스트·장갑)", "Còn dầu: A2 rất ít + găng", chem="A2", optional=True, force="Cap1", tool_ids=["T_CLOTH", "T_GLOVE_NITRILE"]),
            Step("dish", "주방세제+미온 세탁", "D2 + giặt ấm nhẹ", chem="D2", force="Cap2"),
            Step("light", "건조 전 확인", "Kiểm trước sấy", force="Cap1"),
        ],
    )


def _tpl_candle_wax() -> Protocol:
    return Protocol(
        stain_id="S_CANDLE_WAX",
        why_ko="[왜 이 순서] 촛농=왁스. 얼려 깨기→흡수지+낮은 다리미로 흡수→잔여 세제. 얼룩 위 강한 다림질 금지.",
        why_vi="GIAO DUC: Sáp nến. Đông bẻ → giấy+ủi thấp hút → D2.",
        steps=[
            Step("id", "촛농·원단", "Nhận sáp nến", force="Cap1"),
            Step("freeze", "얼리거나 차게 해 깨기", "Làm lạnh rồi bẻ", force="Cap2", tool_ids=["T_TIMER"], minutes_lo=20, minutes_hi=40),
            Step("iron", "흡수지 위아래+낮은 열로 왁스 흡수(반복)", "Giấy + ủi thấp hút sáp", tool_ids=["T_CLOTH", "T_STEAM_IRON"], force="Cap1"),
            Step("dish", "잔여: 주방세제", "Còn: D2", chem="D2", force="Cap2", tool_ids=["T_CLOTH"]),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 확인", "Kiểm trước sấy", force="Cap1"),
        ],
    )


def _tpl_sunscreen() -> Protocol:
    return Protocol(
        stain_id="S_SUNSCREEN",
        why_ko="[왜 이 순서] 선크림=실리콘 오일+UV필터. 전분→주방세제. 락스 금지(영구 황변). 미끄럼 남은 채 건조 금지.",
        why_vi="GIAO DUC: Kem chống nắng = silicone+UV. N3 → D2. CAM Javel (vàng vĩnh viễn).",
        steps=[
            Step("id", "선크림·원단", "Nhận kem chống nắng", force="Cap1"),
            Step("absorb", "전분 10–30분", "N3 10-30", chem="N3", minutes_lo=10, minutes_hi=30),
            Step("dish", "주방세제 Cap2", "D2 Cap2", chem="D2", force="Cap2", spray=True),
            Step("wash", "세탁; 락스 금지", "Giặt; CAM Javel", force="Cap2"),
            Step("light", "미끄럼 없어진 뒤 건조·강광", "Hết nhờn mới sấy", force="Cap1"),
        ],
    )


def _tpl_tar() -> Protocol:
    p = _tpl_motorbike_oil()
    p.stain_id = "S_TAR"
    p.why_ko = "[왜 이 순서] 타르=초고점도 오일+탄소. 얼려 긁기→전분→용제 다회(환기). 인내. 미끄럼 남은 채 건조 금지."
    p.why_vi = "GIAO DUC: Nhựa đường = dầu cực đặc. Đông cạo → N3 → D1 nhiều lần."
    p.steps[0] = Step("id", "타르·아스팔트·원단", "Nhận nhựa đường", force="Cap1")
    return p


def _tpl_engine_oil() -> Protocol:
    p = _tpl_motorbike_oil()
    p.stain_id = "S_ENGINE_OIL"
    p.why_ko = "[왜 이 순서] 엔진오일=탄화수소+검정 탄소 — 최난. 전분 반복→용제+환기→알코올→면/폴리 세제. 미끄럼 남은 채 건조 금지."
    p.why_vi = "GIAO DUC: Dầu động cơ = hydrocarbon+carbon. N3 lặp → D1 → A1 → D3."
    p.steps[0] = Step("id", "엔진오일·원단·환기", "Nhận dầu động cơ", force="Cap1")
    return p


def _tpl_deodorant() -> Protocol:
    return Protocol(
        stain_id="S_DEODORANT",
        why_ko="[왜 이 순서] 데오 흰 잔여=염/왁스 → 식초. 겨드랑이 황변이면 황변 SOP(효소→산소).",
        why_vi="GIAO DUC: Cặn deo trắng → giấm. Nách vàng → SOP vàng.",
        steps=[
            Step("id", "데오 잔여 vs 황변 구분", "Nhận cặn deo vs vàng", force="Cap1"),
            Step("vinegar", "흰 잔여: 식초 1:4", "Cặn trắng: giấm 1:4", chem="A3", spray=True, minutes_lo=5, minutes_hi=15, soak=True),
            Step("enzyme", "황변이면 효소", "Nếu vàng: enzyme", chem="E1", optional=True, minutes_lo=15, minutes_hi=30),
            Step("oxygen", "흰옷 황변: 산소", "Trắng vàng: B1", chem="B1", when="white_only", optional=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_perfume() -> Protocol:
    return Protocol(
        stain_id="S_PERFUME",
        why_ko="[왜 이 순서] 향수=알코올+향료(탄닌성). 식초 희석. 흰옷 나중에 황변 가능 — 산소 예방·고지.",
        why_vi="GIAO DUC: Nước hoa = cồn+hương. Giấm loãng. Trắng có thể vàng sau.",
        steps=[
            Step("id", "향수·원단", "Nhận nước hoa", force="Cap1"),
            Step("rinse", "찬물", "Xả lạnh", force="Cap1"),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", spray=True, minutes_lo=5, minutes_hi=15, soak=True),
            Step("oxygen", "흰옷: 짧은 산소(황변 예방)", "Trắng: B1 ngắn", chem="B1", when="white_only", optional=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "통풍 건조·강광", "Phơi thoáng + ánh sáng", force="Cap1"),
        ],
    )


def _tpl_mascara() -> Protocol:
    return Protocol(
        stain_id="S_MASCARA",
        why_ko="[왜 이 순서] 마스카라=왁스+색소. 블롯→주방세제→잔색 알코올→흰옷 산소. 문지르면 번짐.",
        why_vi="GIAO DUC: Mascara = sáp+màu. Blot → D2 → A1 → B1.",
        steps=[
            Step("id", "마스카라·원단", "Nhận mascara", force="Cap1"),
            Step("blot", "흰 천 블롯 Cap1", "Thấm khăn trắng", tool_ids=["T_CLOTH"], force="Cap1"),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2"),
            Step("alcohol", "잔색 알코올(테스트)", "Còn màu: A1", chem="A1", force="Cap1", spray=True),
            Step("oxygen", "흰옷 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_hair_dye() -> Protocol:
    return Protocol(
        stain_id="S_HAIR_DYE",
        why_ko="[왜 이 순서] 염모제=강한 염료. 즉시 찬물→알코올→산소(흰). 유색·실크 위험 — 테스트·고지. 100% 비보장.",
        why_vi="GIAO DUC: Thuốc nhuộm tóc = dye mạnh. Lạnh → A1 → B1 trắng. Báo không 100%.",
        steps=[
            Step("id", "염모제·즉시·원단", "Nhận thuốc nhuộm", force="Cap1"),
            Step("rinse", "즉시 찬물", "Xả lạnh ngay", force="Cap1"),
            Step("alcohol", "알코올 블롯(테스트)", "A1 blot test", chem="A1", force="Cap1", spray=True),
            Step("oxygen", "흰옷 산소 장침지", "Trắng: B1 dài", chem="B1", when="white_only", soak=True, minutes_lo=30, minutes_hi=180),
            Step("wash", "세탁; 잔색 고지", "Giặt; báo còn màu", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_shoe_polish() -> Protocol:
    return Protocol(
        stain_id="S_SHOE_POLISH",
        why_ko="[왜 이 순서] 구두약=왁스/오일+색소. 환기. 긁기→용제 안쪽 블롯→주방세제→잔색 알코올→흰옷 산소.",
        why_vi="GIAO DUC: Xi giày = sáp/dầu+màu. Cạo → D1 → D2 → A1 → B1.",
        steps=[
            Step("id", "구두약·환기·원단", "Nhận xi giày + thông gió", force="Cap1"),
            Step("scrape", "여분 제거", "Cạo", force="Cap1"),
            Step("solvent", "용제 안쪽 블롯(환기)", "D1 thấm mặt trái", chem="D1", tool_ids=["T_CLOTH", "T_GLOVE_NITRILE"], force="Cap1", spray=True),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2"),
            Step("alcohol", "잔색 알코올(테스트)", "A1", chem="A1", optional=True),
            Step("oxygen", "흰옷 산소", "Trắng: B1", chem="B1", when="white_only"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_paint_latex() -> Protocol:
    return Protocol(
        stain_id="S_PAINT_LATEX",
        why_ko="[왜 이 순서] 수성페인트=젖었을 때 찬물·세제. 마르면 용제 테스트. 문질러 번짐 주의.",
        why_vi="[Tại sao] Sơn nước. Ướt: lạnh+D2. Khô: dung môi test.",
        steps=[
            Step("id", "수성페인트·젖음/마름", "Nhận sơn nước ướt/khô", force="Cap1"),
            Step("rinse", "젖었으면 즉시 찬물·긁기", "Nếu ướt: xả lạnh + cạo", force="Cap1"),
            Step("dish", "세제", "D2", chem="D2", force="Cap2", spray=True),
            Step("solvent", "마른 후: 용제/알코올 테스트", "Khô: D1/A1 test", chem="D1", optional=True, force="Cap1"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_paint_oil() -> Protocol:
    return Protocol(
        stain_id="S_PAINT_OIL",
        why_ko="[왜 이 순서] 유성페인트=수지·안료·유기용제. 수성과 다름. 시너 테스트·환기·PPE. 아세테이트 금지.",
        why_vi="[Tại sao] Sơn dầu ≠ sơn nước. Dung môi test + thông gió + PPE. CẤM acetate.",
        steps=[
            Step("id", "유성페인트 확인(수성과 구분)", "Xác nhận sơn dầu", force="Cap1"),
            Step("scrape", "고형 긁기", "Cạo", force="Cap1"),
            Step("solvent", "시너/미네랄스피릿 구석 테스트+블롯", "Dung môi test + blot", chem="D1", force="Cap1"),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2", spray=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_betel() -> Protocol:
    return Protocol(
        stain_id="S_BETEL",
        why_ko="[왜 이 순서] 빈랑=탄닌+적갈 색소. 찬물·문지르기 금지. 식초 1:4→흰/면 산소.",
        why_vi="[Tại sao] Trầu/cau = tannin đỏ nâu. Lạnh, không chà. Giấm 1:4 → oxy trắng.",
        steps=[
            Step("id", "빈랑·적갈 확인", "Nhận trầu đỏ nâu", force="Cap1"),
            Step("blot", "찬물 흡수(문지르기 금지)", "Thấm lạnh — CẤM chà", force="Cap1"),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", minutes_lo=5, minutes_hi=15, soak=True, spray=True),
            Step("oxygen", "흰/면 잔색: 산소", "Oxy trắng/cotton", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_iodine() -> Protocol:
    return Protocol(
        stain_id="S_IODINE",
        why_ko="[왜 이 순서] 요오드·thuốc đỏ=할로겐 색소. 찬물→알코올 안쪽 블롯→흰/면 산소. 문지르기·열고착 금지.",
        why_vi="[Tại sao] Thuốc đỏ/iod = sắc tố. Lạnh → blot cồn mặt trái → oxy trắng. CẤM chà/nhiệt.",
        steps=[
            Step("id", "요오드·thuốc đỏ·원단", "Nhận thuốc đỏ/iod", force="Cap1"),
            Step("rinse", "안쪽 찬물 흡수(문지르기 금지)", "Thấm lạnh mặt trái — CẤM chà", force="Cap1"),
            Step("alcohol", "알코올 안쪽 블롯(테스트·환기)", "Cồn blot mặt trái", chem="A1", force="Cap1", tool_ids=["T_CLOTH"]),
            Step("oxygen", "흰/면: 산소(테스트)", "Oxy trắng", chem="B1", when="white_only", soak=True),
            Step("wash", "찬물 세탁", "Giặt lạnh", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_chili() -> Protocol:
    return Protocol(
        stain_id="S_CHILI",
        why_ko="[왜 이 순서] 칠리·핫소스=오일+색소+산. 찬물→주방세제→식초 1:4→흰/면 산소.",
        why_vi="[Tại sao] Tương ớt = dầu+màu+acid. Lạnh → D2 → giấm 1:4 → oxy trắng.",
        steps=[
            Step("id", "칠리·핫소스·원단", "Nhận tương ớt", force="Cap1"),
            Step("scrape", "여분 긁기·찬물", "Cạo + xả lạnh", force="Cap1"),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2", spray=True),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", minutes_lo=10, minutes_hi=20, soak=True, spray=True),
            Step("oxygen", "흰/면 산소(테스트)", "Oxy trắng", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_shrimp_paste() -> Protocol:
    return Protocol(
        stain_id="S_SHRIMP_PASTE",
        why_ko="[왜 이 순서] 맘톰=유분+단백질+색소+냄새. 긁기→찬물→D2→E1→A3→흰/면 산소. 느억맘과 구분.",
        why_vi="[Tại sao] Mắm tôm = dầu+protein+màu+mùi. Cạo → D2 → E1 → A3 → oxy. Khác nước mắm.",
        steps=[
            Step("id", "맘톰·원단(느억맘 구분)", "Nhận mắm tôm", force="Cap1"),
            Step("scrape", "여분 긁기·찬물", "Cạo + xả lạnh", force="Cap1"),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2", spray=True),
            Step("enzyme", "효소 찬물", "E1", chem="E1", minutes_lo=15, minutes_hi=45, soak=True),
            Step("vinegar", "식초 1:4 냄새", "Giấm 1:4", chem="A3", minutes_lo=10, minutes_hi=20, soak=True),
            Step("oxygen", "흰/면 산소(테스트)", "Oxy trắng", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_sugarcane() -> Protocol:
    return Protocol(
        stain_id="S_SUGARCANE",
        why_ko="[왜 이 순서] 느억미아=당+색소. 찬물 흡수→식초 1:4→흰/면 산소. 문지르기·열고착 금지.",
        why_vi="[Tại sao] Nước mía = đường+màu. Thấm lạnh → giấm 1:4 → oxy trắng. CẤM chà.",
        steps=[
            Step("id", "사탕수수즙·원단", "Nhận nước mía", force="Cap1"),
            Step("rinse", "안쪽 찬물 흡수(문지르기 금지)", "Thấm lạnh — CẤM chà", force="Cap1"),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", minutes_lo=10, minutes_hi=20, soak=True, spray=True),
            Step("oxygen", "흰/면 산소(테스트)", "Oxy trắng", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_gac() -> Protocol:
    return Protocol(
        stain_id="S_GAC",
        why_ko="[왜 이 순서] 가정=카로티노이드+오일. 긁기→D2→알코올 블롯→흰/면 산소·햇빛. 커리와 구분.",
        why_vi="[Tại sao] Gấc = carotenoid+dầu. Cạo → D2 → blot A1 → oxy + nắng. Khác cà ri.",
        steps=[
            Step("id", "가정·원단", "Nhận gấc", force="Cap1"),
            Step("scrape", "여분 오일 긁기", "Cạo dầu", force="Cap1"),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2", spray=True),
            Step("alcohol", "알코올 안쪽 블롯(테스트)", "Blot cồn", chem="A1", force="Cap1", tool_ids=["T_CLOTH"]),
            Step("oxygen", "흰/면 산소(테스트)", "Oxy trắng", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "햇빛·강광", "Nắng/ánh sáng", force="Cap1"),
        ],
    )


def _tpl_annatto() -> Protocol:
    return Protocol(
        stain_id="S_ANNATTO",
        why_ko="[왜 이 순서] 디에우마우=식품 황·주황 색소. 찬물→알코올 블롯→흰/면 산소. 문지르기 금지.",
        why_vi="[Tại sao] Điều màu = màu vàng–cam. Lạnh → blot cồn → oxy trắng. CẤM chà.",
        steps=[
            Step("id", "아나토·원단", "Nhận điều màu", force="Cap1"),
            Step("rinse", "찬물 흡수(문지르기 금지)", "Thấm lạnh — CẤM chà", force="Cap1"),
            Step("alcohol", "알코올 안쪽 블롯(테스트)", "Blot cồn", chem="A1", force="Cap1", tool_ids=["T_CLOTH"]),
            Step("oxygen", "흰/면 산소(테스트)", "Oxy trắng", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_fish_sauce() -> Protocol:
    return Protocol(
        stain_id="S_FISH_SAUCE",
        why_ko="[왜 이 순서] 느억맘=단백질+유분+냄새. 찬물→효소→주방세제→식초→흰/면 산소. 락스 남용 금지.",
        why_vi="[Tại sao] Nước mắm = protein+dầu+mùi. Lạnh → E1 → D2 → A3 → oxy. CẤM Javel lạm.",
        steps=[
            Step("id", "느억맘·원단", "Nhận nước mắm", force="Cap1"),
            Step("rinse", "찬물", "Xả lạnh", force="Cap1"),
            Step("enzyme", "효소", "E1", chem="E1", minutes_lo=15, minutes_hi=45, soak=True),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2", spray=True),
            Step("vinegar", "식초 1:4", "Giấm 1:4", chem="A3", minutes_lo=10, minutes_hi=20, soak=True),
            Step("oxygen", "흰/면 산소(테스트)", "Oxy trắng", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 강광", "Ánh sáng trước sấy", force="Cap1"),
        ],
    )


def _tpl_glue() -> Protocol:
    return Protocol(
        stain_id="S_GLUE",
        why_ko="[왜 이 순서] 접착제=종류 다양. 고형 제거→세제→알코올/아세톤(원단 테스트). 아세테이트+아세톤 금지.",
        why_vi="GIAO DUC: Keo. Cạo → D2 → A1/A2 test. CAM acetate+A2.",
        steps=[
            Step("id", "접착제·원단", "Nhận keo", force="Cap1"),
            Step("scrape", "고형 제거", "Cạo", force="Cap1"),
            Step("dish", "주방세제", "D2", chem="D2", force="Cap2"),
            Step("alcohol", "잔여: 알코올(테스트)", "A1 test", chem="A1", optional=True, force="Cap1"),
            Step("acetone", "필요 시 아세톤 극소(테스트)", "A2 rất ít test", chem="A2", optional=True, force="Cap1"),
            Step("wash", "세탁", "Giặt", force="Cap2"),
            Step("light", "건조 전 확인", "Kiểm trước sấy", force="Cap1"),
        ],
    )


def _tpl_starch_transfer() -> Protocol:
    return Protocol(
        stain_id="S_STARCH_TRANSFER",
        why_ko="[왜 이 순서] 풀/전분 이염=전분+색소. 효소(전분)→산소(흰). 뜨거운 다림질로 고착 금지.",
        why_vi="GIAO DUC: Hồ tinh bột lo màu. Enzyme tinh bột → B1 trắng.",
        steps=[
            Step("id", "전분·풀 이염·원단", "Nhận hồ tinh bột", force="Cap1"),
            Step("rinse", "찬물", "Xả lạnh", force="Cap1"),
            Step("enzyme", "전분 효소(아밀라아제/E2) 침지", "Enzyme tinh bột E2", chem="E2", minutes_lo=15, minutes_hi=60, soak=True),
            Step("oxygen", "흰옷 산소", "Trắng: B1", chem="B1", when="white_only", soak=True),
            Step("wash", "세탁; 잔색 채 다림질 금지", "Giặt; CAM ủi khi còn", force="Cap2"),
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
    "S_BLOOD_DRY": _tpl_blood_dry,
    "S_MILK_COFFEE": _tpl_milk_coffee,
    "S_LIPSTICK": _tpl_lipstick,
    "S_FOUNDATION": _tpl_foundation,
    "S_GREASE": lambda: _tpl_grease_like("S_GREASE", "기름때·그리즈", "mỡ/grease"),
    "S_BUTTER": lambda: _tpl_grease_like("S_BUTTER", "버터", "bơ"),
    "S_MOTORBIKE_OIL": _tpl_motorbike_oil,
    "S_INK_PEN": _tpl_ink_pen,
    "S_RUST": _tpl_rust,
    "S_BUBBLE_TEA": _tpl_bubble_tea,
    "S_KETCHUP": lambda: _tpl_sauce_oil_tannin("S_KETCHUP", "케첩", "ketchup"),
    "S_TOMATO_SAUCE": lambda: _tpl_sauce_oil_tannin("S_TOMATO_SAUCE", "토마토소스", "sốt cà"),
    "S_MUD": _tpl_mud,
    "S_SOY_SAUCE": lambda: _tpl_protein_then_vinegar("S_SOY_SAUCE", "간장", "nước tương"),
    "S_FISH_SAUCE": _tpl_fish_sauce,
    # v3 — remaining high-frequency / VN specialty
    "S_EGG": lambda: _tpl_protein_simple("S_EGG", "계란", "trứng"),
    "S_MILK": lambda: _tpl_protein_simple("S_MILK", "우유", "sữa"),
    "S_BABY_FORMULA": lambda: _tpl_protein_simple("S_BABY_FORMULA", "분유", "sữa công thức", minutes=(20, 40)),
    "S_SWEAT_FRESH": lambda: _tpl_protein_simple("S_SWEAT_FRESH", "땀(신선)", "mồ hôi tươi"),
    "S_VOMIT": lambda: _tpl_protein_then_vinegar("S_VOMIT", "구토물", "chất nôn"),
    "S_URINE": lambda: _tpl_protein_then_vinegar("S_URINE", "소변", "nước tiểu"),
    "S_FECES": lambda: _tpl_protein_simple("S_FECES", "대변", "phân", minutes=(20, 45)),
    "S_MAYO": _tpl_mayo,
    "S_BBQ_SAUCE": _tpl_bbq,
    "S_COLLAR_STAIN": _tpl_collar,
    "S_SHIRT_YELLOW": _tpl_shirt_yellow,
    "S_SWEAT_YELLOW": _tpl_sweat_yellow,
    "S_GRASS": _tpl_grass,
    "S_CHOCOLATE": _tpl_chocolate,
    "S_CURRY": lambda: _tpl_curry_mustard("S_CURRY", "카레·강황", "cà ri/nghệ"),
    "S_MUSTARD": lambda: _tpl_curry_mustard("S_MUSTARD", "머스터드", "mù tạt"),
    "S_INK_PERMANENT": _tpl_ink_permanent,
    "S_NAIL_POLISH": _tpl_nail_polish,
    "S_DYE_TRANSFER": _tpl_dye_transfer,
    "S_LATERITE": _tpl_laterite,
    "S_MILDEW": _tpl_mildew,
    "S_GUM": _tpl_gum,
    "S_CANDLE_WAX": _tpl_candle_wax,
    "S_SUNSCREEN": _tpl_sunscreen,
    "S_TAR": _tpl_tar,
    "S_ENGINE_OIL": _tpl_engine_oil,
    "S_DEODORANT": _tpl_deodorant,
    "S_PERFUME": _tpl_perfume,
    "S_MASCARA": _tpl_mascara,
    "S_HAIR_DYE": _tpl_hair_dye,
    "S_SHOE_POLISH": _tpl_shoe_polish,
    "S_PAINT_LATEX": _tpl_paint_latex,
    "S_PAINT_OIL": _tpl_paint_oil,
    "S_BETEL": _tpl_betel,
    "S_IODINE": _tpl_iodine,
    "S_CHILI": _tpl_chili,
    "S_SHRIMP_PASTE": _tpl_shrimp_paste,
    "S_SUGARCANE": _tpl_sugarcane,
    "S_GAC": _tpl_gac,
    "S_ANNATTO": _tpl_annatto,
    "S_GLUE": _tpl_glue,
    "S_STARCH_TRANSFER": _tpl_starch_transfer,
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
    ft = str(entities.get("fabric_type") or "").lower().strip()
    # Text-inferred sturdy fabrics win over a wrong Neo4j fabric row (e.g. 지울→wool)
    if ft in ("cotton", "polyester", "linen", "denim"):
        flags = {
            "is_silk": False,
            "is_wool": False,
            "is_leather": False,
            "is_suede": False,
            "is_fur": False,
            "is_rayon": False,
            "is_acetate": False,
            "is_nylon": False,
            "delicate_protein": False,
            "no_oxygen": False,
            "no_acid": False,
            "no_enzyme": False,
            "no_acetone": False,
            "no_chlorine": False,
            "fname": ft,
            "fid": {"cotton": "F1", "polyester": "F2", "linen": "F5", "denim": "F6"}.get(ft, ""),
        }
    else:
        fid = str(fabric.get("id") or "").upper()
        fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''} {ft}".lower()
        is_silk = fid == "F4" or "silk" in fname or "lua" in fname or ft == "silk"
        is_wool = fid == "F3" or "wool" in fname or " len" in f" {fname}" or fname.strip() == "len" or ft == "wool"
        is_leather = fid == "F8" or "leather" in fname or fname.strip() == "da" or ft == "leather"
        is_suede = fid == "F9" or "suede" in fname or "nubuck" in fname or ft == "suede"
        is_fur = fid == "F10" or "fur" in fname or ft == "fur"
        is_rayon = fid == "F7" or "rayon" in fname or ft == "rayon"
        is_acetate = "acetate" in fname or "아세테이트" in ft or ft == "acetate"
        is_nylon = "nylon" in fname or "나일론" in ft or ft == "nylon"
        flags = {
            "is_silk": is_silk,
            "is_wool": is_wool,
            "is_leather": is_leather,
            "is_suede": is_suede,
            "is_fur": is_fur,
            "is_rayon": is_rayon,
            "is_acetate": is_acetate,
            "is_nylon": is_nylon,
            "delicate_protein": is_silk or is_wool,
            "no_oxygen": is_silk or is_wool or is_leather or is_suede or is_fur or is_rayon
            or fabric.get("can_oxygen") is False,
            "no_acid": fabric.get("acid_safe") is False or is_silk or is_wool,
            "no_enzyme": fabric.get("enzyme_safe") is False or is_silk or is_wool,
            "no_acetone": is_acetate or is_rayon,
            "no_chlorine": False,
            "fname": fname,
            "fid": fid,
        }

    # Care-label Vision overlays (photo → SOP clamp)
    if entities.get("care_no_bleach"):
        flags["no_oxygen"] = True
        flags["no_chlorine"] = True
    if entities.get("care_oxygen_only"):
        flags["no_chlorine"] = True
    if entities.get("care_do_not_wash"):
        flags["care_do_not_wash"] = True
    if entities.get("care_hand_wash_only"):
        flags["care_hand_wash_only"] = True
    if entities.get("care_max_temp_c"):
        try:
            flags["care_max_temp_c"] = int(entities["care_max_temp_c"])
        except (TypeError, ValueError):
            pass
    return flags


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
    if flags.get("no_chlorine") and c in {"B2", "X1"}:
        return True, "케어라벨: 염소·강표백 금지(산소만 가능 시)", "Nhãn: cấm Javel (có thể chỉ oxy)"
    if garment_color in {"colored", "black"} and c in {"B2", "X1"}:
        return True, "유색·검정: 염소·환원표백 금지", "Màu/đen: cấm Javel"
    if garment_color == "black" and c in {"B1", "A4"}:
        return True, "검정: 표백 금지", "Đen: cấm tẩy"
    # Unknown / missing color: never offer oxygen/chlorine/reducing as active step
    if (not garment_color or garment_color in {"unknown", ""}) and c in {"B1", "A4", "B2", "X1"}:
        return True, "색 미확인: 표백(산소·염소·환원) 생략 — 흰옷 확인 후", "Chưa rõ màu: bỏ tẩy — chỉ sau khi xác nhận trắng"
    if flags.get("no_acetone") and c == "A2":
        return True, "아세테이트·레이온: 아세톤 금지", "Acetate/rayon: cấm acetone"
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
    color = (out.garment_color or "").lower().strip()

    for s in out.steps:
        # Require explicit white — unknown/empty/colored all skip white_only steps
        if s.when == "white_only" and color != "white":
            s.blocked = True
            if not color or color == "unknown":
                s.block_reason_ko = "색 미확인: 산소·표백 단계 생략. 흰옷 확인 후에만 적용(구석 테스트)."
                s.block_reason_vi = "Chưa rõ màu: bỏ tẩy oxy. Chỉ khi xác nhận trắng (+test góc)."
            else:
                s.block_reason_ko = "유색·검정: 산소표백 단계 생략(흰옷만)."
                s.block_reason_vi = "Không trắng: bỏ bước oxy."
            continue

        if not s.chem:
            continue
        blocked, rk, rv = _chem_blocked(s.chem, flags, color)
        if not blocked:
            continue

        # Protein delicates: replace enzyme/oxygen/acid/oxalic step with explicit S1 local care
        if flags.get("delicate_protein") and s.chem in {"E1", "E2", "E3", "B1", "A3", "X2"}:
            if s.chem == "X2":
                s.chem = "A3"
                s.action_ko = "실크·울 녹: 옥살산 금지 — 식초 약하게만·테스트. 심하면 전문."
                s.action_vi = "Len/lụa rỉ: không X2 — chỉ giấm nhẹ, test. Nặng → chuyên."
                s.spray = True
                s.soak = True
                s.minutes_lo = 5
                s.minutes_hi = 10
                s.blocked = False
                continue
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


# Home textiles: wash/mesh/temp education — not generic spotting-brush copy
HOME_TEXTILE_ITEM_IDS = frozenset({
    "I_CURTAIN_FABRIC", "I_CURTAIN_URETHANE",
    "I_DUVET_GOOSE", "I_DUVET_COTTON",
    "I_BED_SHEET", "I_TOWEL",
})

BIOHAZARD_FOR_NARRATE = frozenset({
    "S_BLOOD_FRESH", "S_BLOOD_DRY", "S_VOMIT", "S_URINE", "S_FECES",
})


def _stain_family(stain_id: str, sc: Optional[dict] = None) -> str:
    """Coarse chemistry family for tool howto (not a second truth source)."""
    sid = str(stain_id or "").upper()
    sc = sc or {}
    if sid in {"S_MUD", "S_LATERITE"}:
        return "mud"
    if sid == "S_MILDEW":
        return "mildew"
    if sid in {"S_INK_PEN", "S_INK_PERMANENT", "S_HAIR_DYE", "S_MASCARA", "S_PAINT_LATEX", "S_PAINT_OIL", "S_IODINE", "S_GAC", "S_ANNATTO"}:
        return "ink"
    if sid in {
        "S_ENGINE_OIL", "S_MOTORBIKE_OIL", "S_TAR", "S_GREASE", "S_COOKING_OIL",
        "S_BUTTER", "S_SUNSCREEN", "S_FOUNDATION", "S_LIPSTICK", "S_SHOE_POLISH",
    }:
        return "oil"
    if sid in {"S_KIMCHI", "S_BBQ_SAUCE", "S_MAYO", "S_BUBBLE_TEA", "S_MILK_COFFEE"}:
        return "oil_tannin"
    if sid.startswith("S_BLOOD") or sid in {
        "S_EGG", "S_MILK", "S_BABY_FORMULA", "S_SWEAT_FRESH", "S_SWEAT_YELLOW",
        "S_VOMIT", "S_URINE", "S_FECES", "S_COLLAR_STAIN",
    }:
        return "protein"
    if sc.get("contains_protein") and (sc.get("contains_tannin") or sc.get("contains_oil")):
        return "oil_tannin" if sc.get("contains_oil") else "protein"
    if sc.get("contains_protein"):
        return "protein"
    if sc.get("contains_oil") and sc.get("contains_tannin"):
        return "oil_tannin"
    if sc.get("contains_oil"):
        return "oil"
    if sc.get("contains_tannin") or sc.get("contains_dye"):
        return "tannin"
    if sid in {
        "S_RED_WINE", "S_TEA", "S_BLACK_COFFEE", "S_FRUIT_JUICE", "S_SOFT_DRINK",
        "S_WHITE_WINE_BEER", "S_CURRY", "S_MUSTARD", "S_KETCHUP", "S_TOMATO_SAUCE",
        "S_SOY_SAUCE", "S_FISH_SAUCE",
    }:
        return "tannin"
    return "general"


def _force_for_tool(proto: Optional[Protocol], tool_id: str, default: str = "Cap1–2") -> str:
    if not proto:
        return default
    forces = []
    for s in proto.active_steps():
        if tool_id in (s.tool_ids or []) and s.force:
            forces.append(s.force)
    return forces[-1] if forces else default


def _fabric_label(fabric: str, weight: str) -> tuple[str, str]:
    f = (fabric or "").lower().strip() or "원단"
    w = (weight or "unknown").lower().strip()
    w_ko = {"thin": "얇은", "medium": "보통 두께", "thick": "두꺼운", "unknown": ""}.get(w, "")
    w_vi = {"thin": "mỏng", "medium": "dày vừa", "thick": "dày", "unknown": ""}.get(w, "")
    f_ko = {
        "cotton": "면", "polyester": "폴리에스터", "silk": "실크", "wool": "울",
        "linen": "린넨", "denim": "데님",
    }.get(f, f or "원단")
    f_vi = {
        "cotton": "cotton", "polyester": "polyester", "silk": "lụa", "wool": "len",
        "linen": "linen", "denim": "denim",
    }.get(f, f or "vải")
    ko = f"{w_ko + ' ' if w_ko else ''}{f_ko}".strip()
    vi = f"{f_vi}{(' ' + w_vi) if w_vi else ''}".strip()
    return ko, vi


def _cap_plain_ko(cap: str) -> str:
    """Owner-facing force metaphor — bare Cap# is jargon."""
    c = (cap or "Cap1–2").replace("–", "-").replace(" ", "")
    if c in {"Cap1", "1"}:
        return "힘 Cap1=안경 닦듯 아주 약하게(찍기·두드림, 문지르기 아님)"
    if c in {"Cap2", "2"}:
        return "힘 Cap2=칫솔로 거품 내듯 가볍게 한 방향(세게 문지르기 아님)"
    if c in {"Cap3", "3", "Cap2-3"}:
        return "힘 Cap2–3=짧은 구간만 조금 더 세게(데님·마른 흙 등)"
    return "힘 Cap1–2=안경 닦듯~칫솔 거품 내듯 약하게(왕복 문지르기 금지)"


def _cap_plain_vi(cap: str) -> str:
    c = (cap or "Cap1-2").replace("–", "-").replace(" ", "")
    if c in {"Cap1", "1"}:
        return "Lực Cap1=lau kính (chấm/đập, không chà)"
    if c in {"Cap2", "2"}:
        return "Lực Cap2=chải nhẹ 1 chiều như đánh răng (không chà mạnh)"
    if c in {"Cap3", "3", "Cap2-3"}:
        return "Lực Cap2-3=mạnh hơn một chút trên đoạn ngắn (denim/đất khô)"
    return "Lực Cap1-2=lau kính → chải nhẹ (không chà qua lại)"


def _narrate_soft_brush(
    *,
    family: str,
    fabric: str,
    weight: str,
    force: str,
    delicate: bool,
    item_id: str,
    local_spot_only: bool,
) -> tuple[str, str, str]:
    fab_ko, fab_vi = _fabric_label(fabric, weight)
    w = (weight or "unknown").lower()
    cap = force or "Cap1–2"
    cap_ko = _cap_plain_ko(cap)
    cap_vi = _cap_plain_vi(cap)
    spot = "국소 얼룩만 — " if local_spot_only or item_id in HOME_TEXTILE_ITEM_IDS else ""
    spot_vi = "chỉ vết cục bộ — " if local_spot_only or item_id in HOME_TEXTILE_ITEM_IDS else ""

    if delicate:
        return (
            f"{spot}이 원단({fab_ko}): 연질 솔 금지 → 초연질·흰 천만. {_cap_plain_ko('Cap1')}.",
            f"{spot_vi}{fab_vi}: CẤM bàn chải mềm thường → siêu mềm/khăn. {_cap_plain_vi('Cap1')}.",
            f"{spot}Delicate ({fab_ko}): no soft spotting brush — ultra/cloth Cap1 dab only.",
        )

    if family == "tannin":
        if w == "thin":
            ko = (
                f"{spot}탄닌·색소 + {fab_ko}: 흰 천으로만 찍어 흡수(블롯). "
                f"연질솔·왕복 문지르기 금지 — 색소 번짐. {_cap_plain_ko('Cap1')}."
            )
            vi = (
                f"{spot_vi}Tannin/màu + {fab_vi}: chỉ thấm khăn (blot). "
                f"CẤM chà bàn chải — lem màu. {_cap_plain_vi('Cap1')}."
            )
        elif w == "thick":
            ko = (
                f"{spot}탄닌·색소 + {fab_ko}: 식초 도포 후 흰 천 흡수 우선. "
                f"남은 자국만 연질솔은 바깥→안 한 방향 찍기 — 왕복 문지르기 금지. {cap_ko}."
            )
            vi = (
                f"{spot_vi}Tannin + {fab_vi}: sau giấm, thấm khăn trước. "
                f"Còn vết: chải 1 chiều NGOÀI→TRONG — CẤM chà qua lại. {cap_vi}."
            )
        else:
            ko = (
                f"{spot}탄닌·색소 + {fab_ko}: ①먼저 흰 천으로 흡수(블롯). "
                f"②솔로 문지르기 금지 — 색소 번짐. 필요 시 Cap1 바깥→안 찍기만. "
                f"왕복 문지르기 금지."
            )
            vi = (
                f"{spot_vi}Tannin + {fab_vi}: ①thấm khăn trước. "
                f"②CẤM chà bàn chải — lem. Chỉ dab Cap1 NGOÀI→TRONG nếu cần."
            )
        return ko, vi, ko

    if family == "oil":
        ko = (
            f"{spot}유성 + {fab_ko}: 마른 천으로 기름 과잉 흡수 → 주방세제와 함께 연질솔 — "
            f"{cap_ko}, 바깥→안. 온수·세게 문지르면 더 퍼짐."
        )
        vi = (
            f"{spot_vi}Dầu + {fab_vi}: thấm dầu thừa khăn khô → D2 + chải {cap_vi} NGOÀI→TRONG. "
            f"Không nước nóng/chà mạnh."
        )
        return ko, vi, ko

    if family == "oil_tannin":
        ko = (
            f"{spot}기름+색소 + {fab_ko}: 고형 제거 후 주방세제와 연질솔 — {cap_ko}, 바깥→안 → "
            f"색소는 식초 단계. 번지면 힘 낮추고 흰 천."
        )
        vi = (
            f"{spot_vi}Dầu+màu + {fab_vi}: cạo đặc → D2 chải {cap_vi} NGOÀI→TRONG → giấm cho màu. "
            f"Loang → giảm lực, dùng khăn."
        )
        return ko, vi, ko

    if family == "protein":
        ko = (
            f"{spot}단백질 + {fab_ko}: 찬물만. 연질솔은 {_cap_plain_ko('Cap1')} — "
            f"온수·강하게 문지르면 갈색 고착. 섬세면 초연질."
        )
        vi = (
            f"{spot_vi}Protein + {fab_vi}: CHỈ lạnh. Chải {_cap_plain_vi('Cap1')} — "
            f"nóng/chà mạnh = cố định. Đồ mỏng: siêu mềm."
        )
        return ko, vi, ko

    if family == "mud":
        ko = (
            f"{spot}흙·진흙 + {fab_ko}: 마른 흙은 경질로 먼저 털고, 원단면은 연질솔 — "
            f"{cap_ko}, 바깥→안. 젖은 채 문지르면 더 박힘."
        )
        vi = (
            f"{spot_vi}Bùn + {fab_vi}: chải khô đất (cứng) trước; mặt vải mềm {cap_vi} "
            f"NGOÀI→TRONG. Ướt mà chà = ngấm sâu."
        )
        return ko, vi, ko

    if family == "mildew":
        ko = (
            f"{spot}곰팡이 + {fab_ko}: 마스크 후 마른 포자만 — {_cap_plain_ko('Cap1')}로 살살 털기. "
            f"세게 문지르면 포자 확산. 그다음 약품."
        )
        vi = (
            f"{spot_vi}Mốc + {fab_vi}: khẩu trang; phủi bào tử khô — {_cap_plain_vi('Cap1')}. "
            f"Không chà mạnh. Rồi hóa chất."
        )
        return ko, vi, ko

    if family == "ink":
        ko = (
            f"{spot}잉크·염료 + {fab_ko}: 솔보다 흰 천+약품 블롯 우선. "
            f"연질솔은 {_cap_plain_ko('Cap1')}만 — 문지르면 번짐."
        )
        vi = (
            f"{spot_vi}Mực + {fab_vi}: ưu tiên khăn+hóa chất thấm. "
            f"Bàn chải mềm chỉ {_cap_plain_vi('Cap1')} — không chà."
        )
        return ko, vi, ko

    if w == "thin":
        ko = f"{spot}{fab_ko}: {_cap_plain_ko('Cap1')}, 바깥→안. 마찰 큰 솔질 금지 — 흰 천·초연질 우선."
        vi = f"{spot_vi}{fab_vi}: {_cap_plain_vi('Cap1')} NGOÀI→TRONG. Ưu tiên khăn/siêu mềm."
    elif w == "thick":
        ko = f"{spot}{fab_ko}: {cap_ko}, 바깥→안 한 방향. 넓게 문지르지 말 것."
        vi = f"{spot_vi}{fab_vi}: {cap_vi} 1 chiều NGOÀI→TRONG — không chà diện rộng."
    else:
        ko = f"{spot}{fab_ko}: {cap_ko}, 바깥→안 한 방향(45°). 실크·울이면 초연질로 교체."
        vi = f"{spot_vi}{fab_vi}: {cap_vi} NGOÀI→TRONG 1 chiều (45°). Lụa/len → siêu mềm."
    return ko, vi, ko


def _narrate_hard_brush(*, family: str, fabric: str, weight: str, force: str, delicate: bool) -> tuple[str, str, str]:
    if delicate or (weight or "").lower() == "thin":
        return (
            "이 경로: 경질 솔 금지(섬세·얇은 원단 손상).",
            "CẤM bàn chải cứng trên vải mỏng/tinh tế.",
            "No hard brush on delicate/thin fabric.",
        )
    fab_ko, fab_vi = _fabric_label(fabric, weight)
    cap = force or "Cap2–3"
    if family == "mud":
        ko = f"흙·진흙 + {fab_ko}: 마른 흙·밑창만 {cap} 짧게 털기. 젖은 원단 면·메시에는 쓰지 말 것."
        vi = f"Bùn + {fab_vi}: chỉ đất khô/đế {cap} ngắn. CẤM mặt vải ướt/mesh."
    elif family == "oil":
        ko = f"중유·타르 잔여 + {fab_ko}: PPE 후 {cap} 짧게 — 갑피 메시·섬세면 금지."
        vi = f"Dầu nặng/nhựa + {fab_vi}: PPE, {cap} ngắn — CẤM mesh/tinh tế."
    else:
        ko = f"데님·캔버스·밑창·마른 흙만 {cap} 짧게. {fab_ko} 메시·실크·울·얇은 원단 금지."
        vi = f"Chỉ denim/canvas/đế/đất khô {cap} ngắn. CẤM mesh/lụa/len/{fab_vi} mỏng."
    return ko, vi, ko


def _narrate_ultra_brush(*, family: str, fabric: str, force: str) -> tuple[str, str, str]:
    fab_ko, fab_vi = _fabric_label(fabric, "thin" if not fabric else "")
    cap = force or "Cap1"
    if family == "protein":
        ko = f"단백질·섬세({fab_ko or '실크·울'}): {cap} 두드리듯·흡수만 — 문지르기 금지. 스펀지 대체 OK."
        vi = f"Protein/tinh tế ({fab_vi or 'lụa/len'}): {cap} đập/thấm — KHÔNG chà. Foam OK."
    elif family == "ink":
        ko = f"잉크·섬세: {cap}로 약 묻힌 초연질만 살짝 — 문지르면 번짐."
        vi = f"Mực/tinh tế: {cap} siêu mềm có hóa chất — không chà."
    else:
        ko = f"실크·울·얇은 원단: {cap} 두드리듯·흡수만 — 문지르기 금지. 연질 일반 솔 대신 이것."
        vi = f"Lụa/len/mỏng: {cap} đập/thấm — KHÔNG chà. Thay bàn chải mềm thường."
    return ko, vi, ko


def _narrate_cloth(*, family: str, fabric: str, weight: str, item_id: str) -> tuple[str, str, str]:
    fab_ko, fab_vi = _fabric_label(fabric, weight)
    if item_id in HOME_TEXTILE_ITEM_IDS and not family:
        ko = (
            f"홈텍({fab_ko or '커튼·침구'}): 국소만 흰 천으로 닦기/받침. "
            f"전체를 스포팅하듯 문지르지 말 것 — 세탁망·세탁 경로 우선."
        )
        vi = (
            f"Đồ gia dụng ({fab_vi or 'rèm/chăn'}): chỉ lau/lót cục bộ bằng khăn trắng. "
            f"Không chà cả tấm — ưu tiên túi lưới + giặt."
        )
        return ko, vi, ko

    if family == "tannin":
        ko = (
            f"탄닌·색소 + {fab_ko}: 바깥→안 찍어 흡수(블롯). 천이 붉/노랗게 물들면 즉시 새 흰 천. "
            f"원단 아래 흡수지 깔아 뒷면 번짐 방지."
        )
        vi = (
            f"Tannin/màu + {fab_vi}: CHẤM NGOÀI→TRONG. Khăn nhuốm → đổi khăn trắng mới. "
            f"Lót giấy dưới vải chống loang mặt sau."
        )
    elif family == "oil":
        ko = (
            f"유성 + {fab_ko}: 먼저 마른 흰 천으로 기름 과잉 흡수(문지르지 말 것) → "
            f"약품 후 다시 블롯. 물든 천은 폐기·교체."
        )
        vi = (
            f"Dầu + {fab_vi}: thấm dầu thừa bằng khăn khô trước (không chà) → "
            f"sau hóa chất thấm lại. Đổi khăn khi bẩn."
        )
    elif family == "protein":
        ko = (
            f"단백질 + {fab_ko}: 찬물에 적신 흰 천으로만 바깥→안 블롯 — "
            f"문지르면 섬유에 밀어 넣음. 온수 천 금지."
        )
        vi = (
            f"Protein + {fab_vi}: chỉ khăn trắng lạnh CHẤM NGOÀI→TRONG — "
            f"không chà. CẤM khăn nóng."
        )
    elif family == "ink":
        ko = (
            f"잉크 + {fab_ko}: 약을 흰 천/솜에 묻혀 안쪽(뒷면)에서 바깥으로 밀어내듯 블롯. "
            f"천 물들면 즉시 교체 — 솔로 문지르지 말 것."
        )
        vi = (
            f"Mực + {fab_vi}: thấm hóa chất từ mặt TRÁI đẩy ra ngoài. "
            f"Đổi khăn khi nhuốm — không chà bàn chải."
        )
    elif family == "mildew":
        ko = f"곰팡이: 마른 천으로 포자 털기(마스크) → 약품 천은 별도. 사용한 천은 따로 세탁·폐기."
        vi = f"Mốc: khăn khô phủi bào tử (khẩu trang) → khăn hóa chất riêng. Giặt/bỏ khăn đã dùng."
    else:
        ko = (
            f"{fab_ko}: 얼룩 위 바깥→안 찍어 흡수, 물들면 새 천. "
            f"흡수지/천을 원단 아래에 깔아 뒷면·작업대 번짐 방지."
        )
        vi = (
            f"{fab_vi}: CHẤM/THẤM NGOÀI→TRONG, đổi khăn khi nhuốm. "
            f"Lót giấy dưới vải chống loang."
        )
    return ko, vi, ko


def _narrate_mesh(*, item_id: str, fabric: str, weight: str) -> tuple[str, str, str]:
    if item_id == "I_CURTAIN_FABRIC":
        ko = (
            "패브릭 커튼: 세탁망(또는 섬세 코스)에 넣고 ~30℃(면 라벨 허용 시 ≤40℃), "
            "세제 소량·탈수 약하게. 젖은 채로 바로 봉에 걸어 주름·수축 관리. "
            "연질 솔로 커튼 전체를 문지르지 말 것."
        )
        vi = (
            "Rèm vải: cho vào túi lưới / chương trình tinh tế ~30℃ (cotton nhãn cho ≤40℃), "
            "ít bột, vắt nhẹ. Treo ngay khi ẩm. Không chà cả tấm bằng bàn chải spotting."
        )
        return ko, vi, ko
    if item_id == "I_CURTAIN_URETHANE":
        ko = (
            "우레탄·비닐 커튼: 가능하면 손걸레+중성. 세탁기 쓸 때만 세탁망·≤40℃·유연제 금지·열건조 금지. "
            "코팅면 세게 솔질 금지."
        )
        vi = (
            "Rèm PU/vinyl: ưu tiên lau tay + trung tính. Máy (nếu nhãn cho): túi lưới ≤40℃, "
            "CẤM xả vải/sấy nóng. Không chải mạnh lớp phủ."
        )
        return ko, vi, ko
    if item_id in {"I_DUVET_GOOSE", "I_DUVET_COTTON"}:
        ko = (
            "이불·다운: 대형기·여유 공간. 다운은 전용/중성·찬물·추가헹굼; "
            "망/쿠션으로 형태 보호. 솔 스포팅은 커버 국소만."
        )
        vi = (
            "Chăn/down: máy lớn. Down: chất down/trung tính, lạnh, xả thêm; "
            "bảo vệ form. Spotting chỉ vỏ cục bộ."
        )
        return ko, vi, ko
    if item_id in {"I_BED_SHEET", "I_TOWEL"}:
        ko = "시트·수건: 세탁망은 선택. 핵심은 수온(면 흰시트~60℃/유색~40℃)·분류·얼룩 국소 전처리."
        vi = "Ga/khăn: túi lưới tùy chọn. Quan trọng: nhiệt độ + phân loại + pretreat cục bộ."
        return ko, vi, ko
    if item_id == "I_SWIMWEAR":
        ko = "수영복: 반드시 세탁망 + 찬물 섬세 — 탈수·고온 금지."
        vi = "Đồ bơi: BẮT BUỘC túi lưới + lạnh tinh tế — CẤM vắt/sấy nóng."
        return ko, vi, ko
    fab_ko, fab_vi = _fabric_label(fabric, weight)
    if (weight or "").lower() == "thin" or fabric in {"silk", "wool"}:
        ko = f"얇은·섬세({fab_ko}): 세탁망에 넣고 섬세 코스 — 마찰·변형 감소."
        vi = f"Mỏng/tinh tế ({fab_vi}): cho túi lưới + chương trình nhẹ."
        return ko, vi, ko
    ko = "얇은 옷·모자·장갑·끈: 세탁망에 넣고 세탁 — 마찰·변형 감소."
    vi = "Đồ mỏng/mũ/găng/dây: cho túi lưới trước khi giặt máy."
    return ko, vi, ko


def _apply_howto(t: dict, ko: str, vi: str, en: str = "") -> dict:
    t = dict(t)
    t["use_for_ko"] = ko
    t["use_for_vi"] = vi
    t["use_for_en"] = en or ko
    return t


def narrate_tools_for_context(
    tools: list,
    *,
    stain_id: str = "",
    stain_context: Optional[dict] = None,
    fabric: str = "",
    weight: str = "unknown",
    item_id: str = "",
    delicate: bool = False,
    proto: Optional[Protocol] = None,
) -> list:
    """Rewrite ALL tool use_for_* from stain/fabric/weight/item — never leave global seed copy."""
    if not tools:
        return tools
    sc = stain_context or {}
    family = _stain_family(stain_id or sc.get("id") or "", sc)
    local_spot = bool(item_id in HOME_TEXTILE_ITEM_IDS and stain_id)
    # Home-textile care without a stain: drop generic soft spotting brush
    drop_soft = bool(item_id in HOME_TEXTILE_ITEM_IDS and not stain_id)

    out = []
    for raw in tools:
        tid = str(raw.get("id") or "")
        if drop_soft and tid == "T_BRUSH_SOFT":
            continue
        t = dict(raw)
        if tid == "T_BRUSH_SOFT":
            ko, vi, en = _narrate_soft_brush(
                family=family,
                fabric=fabric,
                weight=weight,
                force=_force_for_tool(proto, tid, "Cap1–2"),
                delicate=delicate,
                item_id=item_id,
                local_spot_only=local_spot,
            )
            t = _apply_howto(t, ko, vi, en)
        elif tid == "T_BRUSH_HARD":
            ko, vi, en = _narrate_hard_brush(
                family=family,
                fabric=fabric,
                weight=weight,
                force=_force_for_tool(proto, tid, "Cap2–3"),
                delicate=delicate,
            )
            t = _apply_howto(t, ko, vi, en)
        elif tid == "T_BRUSH_ULTRA":
            ko, vi, en = _narrate_ultra_brush(
                family=family,
                fabric=fabric,
                force=_force_for_tool(proto, tid, "Cap1"),
            )
            t = _apply_howto(t, ko, vi, en)
        elif tid == "T_CLOTH":
            ko, vi, en = _narrate_cloth(
                family=family if stain_id else "",
                fabric=fabric,
                weight=weight,
                item_id=item_id,
            )
            t = _apply_howto(t, ko, vi, en)
        elif tid == "T_MESH_BAG":
            ko, vi, en = _narrate_mesh(item_id=item_id, fabric=fabric, weight=weight)
            t = _apply_howto(t, ko, vi, en)
        elif tid == "T_BRUSH_SHOE":
            t = _apply_howto(
                t,
                "고무·클리트 밑창만: 마른 흙 털고 D2. 갑피 메시·실크에 사용 금지.",
                "Chỉ đế cao su/gai: phủi đất khô rồi D2. CẤM thân mesh/lụa.",
                "Rubber/cleat outsole only: dry mud then D2. Never mesh/silk upper.",
            )
        elif tid == "T_GLOVE_NITRILE":
            if (
                family in {"mildew", "ink", "oil", "protein"}
                or stain_id in BIOHAZARD_FOR_NARRATE
                or stain_id in {
                    "S_RUST", "S_LATERITE", "S_ENGINE_OIL", "S_MOTORBIKE_OIL", "S_TAR",
                    "S_HAIR_DYE", "S_GUM", "S_NAIL_POLISH", "S_SHIRT_YELLOW",
                }
            ):
                t = _apply_howto(
                    t,
                    f"이 오염({family or stain_id}): 약품·체액·포자 취급 전 니트릴 장갑 필수. 병 열기 전 착용. 산에 얇은 장갑 금지.",
                    f"Vết này ({family or stain_id}): BẮT BUỘC găng nitrile trước hóa chất/dịch cơ thể/bào tử.",
                    f"For this stain: nitrile gloves before chemicals/body fluids/spores.",
                )
        elif tid == "T_MASK":
            if family == "mildew" or stain_id in BIOHAZARD_FOR_NARRATE or stain_id == "S_MILDEW":
                t = _apply_howto(
                    t,
                    "바이오하자드·곰팡이·용제: 야외·환기 + 마스크. 장갑과 함께.",
                    "Biohazard/mốc/dung môi: ngoài trời/thoáng + khẩu trang + găng.",
                    "Biohazard/mold/solvent: ventilate + mask + gloves.",
                )
        elif tid == "T_STEAM_IRON":
            if stain_id == "S_CANDLE_WAX":
                t = _apply_howto(
                    t,
                    "촛농: 흡수지 위·아래 + 다리미 낮은 열로 왁스만 흡수(반복). 얼룩 위 강한 스팀·고열 금지. 색이음 테스트.",
                    "Sáp nến: giấy trên/dưới + ủi thấp hút sáp. CẤM hơi/nhiệt cao lên vết.",
                    "Wax: blotter paper + low heat to absorb wax only. No high heat on stain.",
                )
            else:
                t = _apply_howto(
                    t,
                    "얼룩이 다 빠진 뒤에만. 케어라벨 다림질 온도. 넥타이: 세워 스팀만.",
                    "Chỉ sau khi hết vết. Nhiệt theo nhãn. Cà vạt: hơi đứng.",
                    "Only after stain gone. Match care-label heat. Ties: upright steam.",
                )
        out.append(t)
    return out


def bind_tools_from_protocol(proto: Protocol, tools: list, *, item_id: str = "") -> list:
    from protocol_equipment import hydrate_tool_list

    tools = hydrate_tool_list(proto, tools)
    if not tools:
        return tools
    sp = proto.spray_step()
    codes = set(proto.chem_codes())
    # Prefer first timed soak in Protocol order (enzyme before vinegar when both exist).
    # Fall back: any timed step, then spray step.
    minute_step = None
    for s in proto.active_steps():
        if s.soak and s.minutes_lo is not None:
            minute_step = s
            break
    if minute_step is None:
        for s in proto.active_steps():
            if s.minutes_lo is not None:
                minute_step = s
                break
    if minute_step is None:
        minute_step = sp

    lo = minute_step.minutes_lo if minute_step else None
    hi = minute_step.minutes_hi if minute_step else lo
    if lo is None and "S1" in codes and "A3" not in codes:
        # Delicate local-care rewrite cleared soak minutes — use short window
        lo, hi = 5, 10
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
    spray_chem = (sp.chem.upper() if sp and sp.chem else "")
    soak_chem = (
        minute_step.chem.upper()
        if minute_step and minute_step.chem
        else spray_chem
    )
    delicate_s1 = "S1" in codes and "A3" not in codes
    if spray_chem:
        meta = CHEM_META.get(spray_chem, {})
        spray_name_ko = meta.get("name_ko") or spray_chem
        spray_dil_ko = meta.get("dilution_ko") or spray_dil_ko
        spray_name_vi = meta.get("name_vi") or spray_chem
        spray_dil_vi = meta.get("dilution_vi") or spray_dil_vi
    elif delicate_s1:
        # Acid/enzyme → S1 rewrite cleared spray=True; do not leave Neo4j vinegar howto
        meta = CHEM_META["S1"]
        spray_chem = "S1"
        soak_chem = "S1"
        spray_name_ko = meta["name_ko"]
        spray_dil_ko = meta["dilution_ko"]
        spray_name_vi = meta["name_vi"]
        spray_dil_vi = meta["dilution_vi"]

    soak_meta = CHEM_META.get(soak_chem, {}) if soak_chem else {}
    soak_name_ko = soak_meta.get("name_ko") or spray_name_ko
    soak_dil_ko = soak_meta.get("dilution_ko") or spray_dil_ko
    soak_name_vi = soak_meta.get("name_vi") or spray_name_vi
    soak_dil_vi = soak_meta.get("dilution_vi") or spray_dil_vi

    bound = []
    for t in tools:
        t = dict(t)
        tid = str(t.get("id") or "")
        if tid == "T_SPRAY" and spray_chem:
            if spray_chem == "S1" and delicate_s1:
                t["use_for_ko"] = (
                    f"실크·울 경로: 식초·효소 분무 금지. 「{spray_name_ko}」을 병 안내대로 약하게만 타서 "
                    f"국소 도포·블롯(분무는 1회 이하). 병 겉에 「{spray_name_ko}」라고 적는다."
                )
                t["use_for_vi"] = (
                    f"Len/lụa: CAM xịt giấm/enzyme. Chỉ 「{spray_name_vi}」 pha nhẹ theo nhãn — "
                    f"chấm/thấm cục bộ. Viết tên lên bình."
                )
                t["use_for_en"] = (
                    f"Silk/wool: no vinegar/enzyme spray. Use 「{spray_name_ko}」 lightly per bottle — dab/blot only."
                )
            else:
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
        elif tid == "T_SPRAY":
            # No spray step — strip any Neo4j vinegar/example howto
            t["use_for_ko"] = "이 경로: 분무 단계 없음. (4)약품을 국소 도포·블롯만. 식초 예시 문구 무시."
            t["use_for_vi"] = "Không bước xịt — chỉ chấm/thấm theo (4). Bỏ hướng dẫn giấm mẫu."
            t["use_for_en"] = "No spray step — dab/blot per (4) chemicals only. Ignore sample vinegar howto."
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
            if delicate_s1:
                t["use_for_ko"] = (
                    f"실크·울: 통담금보다 국소·찬물 헹굼 우선. 담그면 「{soak_name_ko}」만·짧게, "
                    f"타이머 {min_ko}. 식초·효소 담금 금지."
                )
                t["use_for_vi"] = (
                    f"Len/lụa: ưu tiên chấm/xả lạnh. Nếu ngâm: chỉ 「{soak_name_vi}」 ngắn ({min_vi}). "
                    f"CAM giấm/enzyme."
                )
            elif soak_chem and soak_chem == spray_chem and spray_chem:
                t["use_for_ko"] = (
                    f"분무기와 같은 약: 「{soak_name_ko}」을 「{soak_dil_ko}」로 통에 만들어 "
                    f"{min_ko}만 담근다(분무·담금 중 하나 또는 병행). "
                    f"통 겉에 「{soak_name_ko} / {soak_dil_ko}」라고 적는다. "
                    f"정장·넥타이·얇은 실크는 SOP에서 금하면 통담금 하지 말 것."
                )
                t["use_for_vi"] = (
                    f"Cùng thuốc với bình xịt: pha 「{soak_name_vi}」 theo 「{soak_dil_vi}」 vào chậu, "
                    f"ngâm đúng {min_vi} (xịt hoặc ngâm). Dán 「{soak_name_vi} / {soak_dil_vi}」. "
                    f"Cấm ngâm suit/cà vạt/lụa mỏng nếu SOP cấm."
                )
                t["use_for_en"] = (
                    f"Same chem as spray: mix 「{soak_name_ko}」 at 「{soak_dil_ko}」 in the bin, "
                    f"soak only {min_ko}. Label the bin. Skip full soak if SOP forbids."
                )
            elif soak_chem:
                t["use_for_ko"] = (
                    f"담금용: 「{soak_name_ko}」을 「{soak_dil_ko}」로 통에 만들어 {min_ko}만 담근다. "
                    f"통 겉에 「{soak_name_ko} / {soak_dil_ko}」. "
                    f"분무 약이 다르면 섞지 말 것. 정장·넥타이·얇은 실크는 SOP에서 금하면 통담금 금지."
                )
                t["use_for_vi"] = (
                    f"Ngâm: pha 「{soak_name_vi}」 theo 「{soak_dil_vi}」, đúng {min_vi}. "
                    f"Dán nhãn. Không trộn với thuốc xịt khác. Cấm ngâm suit/cà vạt/lụa mỏng nếu SOP cấm."
                )
                t["use_for_en"] = (
                    f"Soak chem 「{soak_name_ko}」 at 「{soak_dil_ko}」 for {min_ko}. "
                    f"Do not mix with a different spray chem. Skip soak if SOP forbids."
                )
            else:
                t["use_for_ko"] = (
                    f"(4)약품의 희석액을 통에 만들어 {min_ko}만 담근다. 통에 약 이름을 적는다. "
                    f"정장·넥타이·얇은 실크는 SOP에서 금하면 통담금 하지 말 것."
                )
                t["use_for_vi"] = (
                    f"Pha dung dịch (4) vào chậu, ngâm đúng {min_vi}. Dán tên thuốc. "
                    f"Cấm ngâm suit/cà vạt/lụa mỏng nếu SOP cấm."
                )
        bound.append(t)

    # Brush/cloth/mesh etc. — never leave global Neo4j seed template
    return narrate_tools_for_context(
        bound,
        stain_id=proto.stain_id,
        fabric=proto.fabric,
        weight=proto.weight or "unknown",
        item_id=item_id or "",
        delicate=bool("S1" in codes and "A3" not in codes) or (proto.fabric or "").lower() in {
            "silk", "wool",
        },
        proto=proto,
    )


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
    item_id = str(
        (graph.get("item_context") or {}).get("id")
        or entities.get("item_id")
        or ""
    )
    fabric = str(
        entities.get("fabric_type")
        or (graph.get("fabric_context") or {}).get("name")
        or ""
    )
    from match_diagnosis import infer_fabric_weight

    weight = str(
        entities.get("fabric_weight")
        or infer_fabric_weight(
            entities.get("_raw") or "",
            fabric_type=fabric,
            item_id=item_id,
        )
        or "unknown"
    )

    sc_raw = graph.get("stain_context") or {}
    sc_dict = sc_raw if isinstance(sc_raw, dict) else {}
    # item_care shapes put I_* into stain_context.id — not a real stain
    real_stain_id = ""
    if sc_dict.get("group") != "item_care":
        cand = str(sc_dict.get("id") or entities.get("stain_id") or "").strip()
        if cand.startswith("S_"):
            real_stain_id = cand

    proto = build_protocol(graph, entities)
    if proto is None:
        # Still rewrite brush/cloth/mesh so Neo4j global seed copy never reaches the LLM
        out = dict(graph)
        flags = _fabric_flags(out, entities)
        out["tools"] = narrate_tools_for_context(
            list(out.get("tools") or []),
            stain_id=real_stain_id,
            stain_context=sc_dict,
            fabric=fabric,
            weight=weight,
            item_id=item_id,
            delicate=bool(flags.get("delicate_protein")),
            proto=None,
        )
        try:
            from leather_care import apply_leather_education

            out = apply_leather_education(out, entities)
        except Exception:
            pass
        try:
            from specialty_item_care import apply_specialty_item_education

            out = apply_specialty_item_education(out, entities)
        except Exception:
            pass
        return out

    out = dict(graph)
    out["protocol"] = proto.to_dict()
    out["protocol_mode"] = proto.mode
    if proto.mode == "item_primary":
        flags = _fabric_flags(out, entities)
        out["tools"] = narrate_tools_for_context(
            list(out.get("tools") or []),
            stain_id=real_stain_id,
            stain_context=sc_dict,
            fabric=fabric or proto.fabric,
            weight=weight,
            item_id=item_id,
            delicate=bool(flags.get("delicate_protein")),
            proto=None,
        )
        try:
            from leather_care import apply_leather_education

            out = apply_leather_education(out, entities)
        except Exception:
            pass
        try:
            from specialty_item_care import apply_specialty_item_education

            out = apply_specialty_item_education(out, entities)
        except Exception:
            pass
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
    flags = _fabric_flags(out, entities)
    tmax = flags.get("care_max_temp_c")
    if tmax:
        sc["water_temp_ko"] = (
            f"{sc.get('water_temp_ko') or '찬물'} · 라벨 최대 약 {tmax}°C 이하"
        )
        sc["water_temp_vi"] = (
            f"{sc.get('water_temp_vi') or 'Lạnh'} · nhãn ≤ ~{tmax}C"
        )
        sc["must_include_ko"] = (
            (str(sc.get("must_include_ko") or "") + ", 라벨 수온 한도").strip(", ")
        )
    if flags.get("care_do_not_wash"):
        sc["care_lock_ko"] = "라벨 물세탁 X — 습식 강처리 금지"
        sc["care_lock_vi"] = "Nhãn CẤM giặt nước — dừng wet mạnh"
        sc["must_include_ko"] = (
            (str(sc.get("must_include_ko") or "") + ", 라벨 물세탁 금지").strip(", ")
        )
    if flags.get("care_hand_wash_only"):
        sc["must_include_ko"] = (
            (str(sc.get("must_include_ko") or "") + ", 손세탁만").strip(", ")
        )
    out["stain_context"] = sc

    out["chemicals"] = render_chemicals(proto, out.get("chemicals") or [])
    out["tools"] = bind_tools_from_protocol(
        proto, list(out.get("tools") or []), item_id=item_id
    )
    # Drop legacy fabric-safety dual-truth leftovers so the LLM cannot prefer them.
    out.pop("chemicals_blocked_for_fabric", None)
    out.pop("delicate_chem_rule", None)
    sp = proto.spray_step()
    if sp and sp.chem:
        meta = CHEM_META.get(sp.chem.upper(), {})
        out["spray_recipe_ko"] = f"{meta.get('name_ko', sp.chem)} / {meta.get('dilution_ko', '')}"
        out["spray_recipe_vi"] = f"{meta.get('name_vi', sp.chem)} / {meta.get('dilution_vi', '')}"
    return out
