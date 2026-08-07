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
    "A2": {
        "name_ko": "아세톤(네일리무버 계열)",
        "name_vi": "Acetone",
        "name_en": "Acetone",
        "dilution_ko": "극소량 Cap1; 아세테이트·레이온 금지; 환기",
        "dilution_vi": "Rất ít Cap1; CAM acetate/rayon; thông gió",
        "dilution_en": "Tiny Cap1; no acetate/rayon; ventilate",
    },
    "N1": {
        "name_ko": "베이킹소다",
        "name_vi": "Baking soda",
        "name_en": "Baking soda",
        "dilution_ko": "페이스트 또는 약희석(중화·냄새)",
        "dilution_vi": "Bột nhão hoặc pha loãng",
        "dilution_en": "Paste or light dilution",
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


def _tpl_blood_dry() -> Protocol:
    return Protocol(
        stain_id="S_BLOOD_DRY",
        why_ko="[왜 이 순서] 마른 피=섬유 고착 단백질. 효소 장침지. 열 금지. 흰 면만 과산화/산소(테스트). 갈색 고착 시 성공률 낮음 고지.",
        why_vi="GIAO DUC: Máu khô = protein bám. Enzyme dài. CAM nhiệt. Oxy trắng test.",
        water_temp_ko="찬물만",
        water_temp_vi="CHỈ lạnh",
        steps=[
            Step("id", "마른 핏자국·원단 확인", "Nhận máu khô", force="Cap1"),
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
    "S_FISH_SAUCE": lambda: _tpl_protein_then_vinegar("S_FISH_SAUCE", "느억맘·액젓", "nước mắm"),
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
        return {
            "is_silk": False,
            "is_wool": False,
            "is_leather": False,
            "is_suede": False,
            "is_fur": False,
            "is_rayon": False,
            "delicate_protein": False,
            "no_oxygen": False,
            "no_acid": False,
            "no_enzyme": False,
            "fname": ft,
            "fid": {"cotton": "F1", "polyester": "F2", "linen": "F5", "denim": "F6"}.get(ft, ""),
        }

    fid = str(fabric.get("id") or "").upper()
    fname = f"{fabric.get('name') or ''} {fabric.get('name_vi') or ''} {ft}".lower()
    is_silk = fid == "F4" or "silk" in fname or "lua" in fname or ft == "silk"
    is_wool = fid == "F3" or "wool" in fname or " len" in f" {fname}" or fname.strip() == "len" or ft == "wool"
    is_leather = fid == "F8" or "leather" in fname or fname.strip() == "da" or ft == "leather"
    is_suede = fid == "F9" or "suede" in fname or "nubuck" in fname or ft == "suede"
    is_fur = fid == "F10" or "fur" in fname or ft == "fur"
    is_rayon = fid == "F7" or "rayon" in fname or ft == "rayon"
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
