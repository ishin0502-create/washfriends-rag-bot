# -*- coding: utf-8 -*-
"""Education gaps v9: complete chem dilution + safety for owner answers.

Sources aligned with commercial laundry practice (DLI/Cleaners Monthly stain bulletins,
oxalic textile SDS guidance, enzyme detergent labels):
- Protein: cold first; enzyme soak; no heat-set; PPE on body fluids
- Oil: absorbent / solvent / dish soap; never dry while greasy
- Rust/iron: oxalic or proprietary rust remover + thorough rinse + neutralize; gloves
- Chlorine: never mix with acids/ammonia; never on silk/wool
- Enzyme: do not share bath with chlorine bleach

This pack is the authoritative dilution text synced into protocol.CHEM_META + Neo4j.
"""
from __future__ import annotations

DILUTION_V9: list[dict[str, str]] = [
    {
        "code": "E1",
        "dilution_ko": (
            "단백질 효소: 찬물 1L에 큰술 1(또는 병 표기) → 잘 녹여 15–60분. "
            "실크·울 금지→중성세제(S1). 락스(B2)와 같은 욕조·동시 사용 금지."
        ),
        "dilution_vi": (
            "Protease: 1 muỗng / 1L lạnh → 15–60 phút. CẤM lụa/len → S1. "
            "CẤM cùng bồn với Javel(B2)."
        ),
        "dilution_en": "Protease: 1 tbsp/1L cold; 15–60 min. No silk/wool. Never same bath as chlorine.",
    },
    {
        "code": "E2",
        "dilution_ko": (
            "전분 효소: 찬물 1L에 큰술 1(또는 병 표기) → 15–60분. 실크·울 금지. "
            "락스와 동시 사용 금지."
        ),
        "dilution_vi": "Amylase: 1 muỗng / 1L lạnh → 15–60 phút. CẤM lụa/len. CẤM cùng Javel.",
        "dilution_en": "Amylase: 1 tbsp/1L cold; 15–60 min. No silk/wool. No chlorine same bath.",
    },
    {
        "code": "E3",
        "dilution_ko": (
            "리파아제: 병 표기; 보통 미온 1L에 큰술 1 → 탈지 후 15–30분. 실크·울 주의. "
            "락스와 동시 사용 금지."
        ),
        "dilution_vi": "Lipase: theo nhãn; ~1 muỗng / 1L ấm → 15–30 phút sau khử dầu. CẤM cùng Javel.",
        "dilution_en": "Lipase: per label; ~1 tbsp/1L warm; 15–30 min after degrease. No chlorine same bath.",
    },
    {
        "code": "D2",
        "dilution_ko": (
            "주방세제(중성): 얼룩에 Cap2로 1–2방울 원액 또는 미온에 약희석(티스푼 수준/컵). "
            "바깥→안 문지름. 오일·소스 전처리 기본."
        ),
        "dilution_vi": (
            "Nước rửa chén: 1-2 giọt nguyên hoặc pha nhẹ ấm (Cap2). "
            "Chà NGOÀI→TRONG. Tiền xử lý dầu/sốt."
        ),
        "dilution_en": "Dish soap: 1–2 drops neat or light warm dilution Cap2. Outside→in.",
    },
    {
        "code": "D1",
        "dilution_ko": (
            "유성 용제/탈지제: 환기+니트릴 장갑+마스크. 제품 라벨. "
            "흰 천에 소량만 묻혀 안쪽 블롯(흠뻑 금지). 구석 색·원단 테스트. "
            "아세테이트·일부 합성은 손상 위험 — 테스트 후."
        ),
        "dilution_vi": (
            "Dung môi dầu: thông gió + găng nitrile + khẩu trang. Theo nhãn. "
            "Chấm khăn mặt trái — không ngập. Test góc."
        ),
        "dilution_en": "Oil solvent: ventilate + nitrile + mask. Tiny blot from reverse per label. Corner test.",
    },
    {
        "code": "D3",
        "dilution_ko": "일반 세탁세제: 병 라벨 용량·수온. 얼룩 전처리(4) 끝난 뒤 본세탁만.",
        "dilution_vi": "Nước giặt thường: theo nhãn. Chỉ sau khi đã tiền xử lý vết.",
        "dilution_en": "Laundry detergent: per bottle. Main wash only after stain pretreatment.",
    },
    {
        "code": "A1",
        "dilution_ko": (
            "이소프로필 알코올 70–90%: 솜·흰 천에 묻혀 안쪽 Cap1 찍기(흠뻑 붓지 말 것). "
            "환기·화기 주의. 구석 테스트."
        ),
        "dilution_vi": "Cồn 70–90%: chấm bông/khăn mặt trái Cap1 — không đổ ngập. Thông gió. Test góc.",
        "dilution_en": "IPA 70–90%: dab cloth Cap1 from reverse — no flood. Ventilate. Corner test.",
    },
    {
        "code": "A2",
        "dilution_ko": (
            "아세톤: 원액 극소량 — 흰 천에 묻혀 안쪽 Cap1 블롯(흡수지 아래). "
            "아세테이트·레이온·트리아세테이트 즉시 금지. 환기·니트릴 PPE. 락스와 혼합 금지."
        ),
        "dilution_vi": (
            "Acetone rất ít — thấm khăn mặt trái Cap1. CẤM acetate/rayon/triacetate. "
            "Thông gió + găng. CẤM trộn Javel."
        ),
        "dilution_en": "Acetone: tiny Cap1 blot reverse. Never acetate/rayon. Ventilate + gloves. Never mix chlorine.",
    },
    {
        "code": "A3",
        "dilution_ko": (
            "흰 식초(~5%): 식초 1 : 물 4. 탄닌·냄새·약한 산 킬레이트. "
            "락스(B2)·암모니아와 절대 혼합 금지(유독 가스)."
        ),
        "dilution_vi": "Giấm trắng ~5%: 1 phần giấm + 4 phần nước. CẤM trộn Javel/amoniac.",
        "dilution_en": "White vinegar ~5%: 1:4 water. Never mix chlorine or ammonia.",
    },
    {
        "code": "A4",
        "dilution_ko": (
            "과산화수소 3%: 흰 면 위주 원액·구석 테스트. 짧은 접촉 후 헹굼. "
            "유색·실크·울 주의. 락스와 같은 욕조 금지."
        ),
        "dilution_vi": "H2O2 3%: ưu tiên cotton trắng; test góc; xả. CẤM cùng bồn Javel.",
        "dilution_en": "3% peroxide: white cotton; corner test; rinse. Not same bath as chlorine.",
    },
    {
        "code": "A5",
        "dilution_ko": (
            "암모니아 희석: 물 1컵에 큰술 1(또는 병 안내). 환기 필수. "
            "락스(B2)와 절대 혼합 금지(클로라민 가스)."
        ),
        "dilution_vi": "Amoniac: 1 muỗng / 1 cốc nước (hoặc nhãn). Thông gió. CẤM trộn Javel.",
        "dilution_en": "Ammonia: 1 tbsp/cup water. Ventilate. NEVER mix chlorine (chloramine gas).",
    },
    {
        "code": "B1",
        "dilution_ko": (
            "산소계(과탄산) 표백제: 흰옷만·구석 색 테스트. 병 라벨; 보통 찬물·미지근 1L에 큰술 1–2 → 15–45분(또는 병). "
            "유색·색 미확인·실크·울 금지. 락스와 목적·욕조 분리."
        ),
        "dilution_vi": (
            "Oxy (percarbonate): CHỈ trắng + test. 1–2 muỗng / 1L → 15–45 phút. "
            "CẤM màu/lụa/len. Tách khỏi Javel."
        ),
        "dilution_en": "Oxygen bleach: white only + test; 1–2 tbsp/1L; 15–45 min. No silk/wool. Separate from chlorine.",
    },
    {
        "code": "B2",
        "dilution_ko": (
            "염소계(락스/자벨): 흰 면만. 예: 원액 1 : 물 10–20(병 우선) · 짧은 담금·즉시 헹굼. "
            "유색·실크·울·아세테이트·나일론 금지. "
            "식초·암모니아·옥살산·효소와 절대 혼합 금지(유독·효과 파괴)."
        ),
        "dilution_vi": (
            "Javel: CHỈ cotton TRẮNG. 1:10–20 (nhãn) · ngâm ngắn · xả. "
            "CẤM màu/lụa/len/acetate. CẤM trộn giấm/amoniac/X2/enzyme."
        ),
        "dilution_en": (
            "Chlorine: white cotton only; 1:10–20; short soak; rinse. "
            "Never silk/wool/color. Never mix vinegar/ammonia/oxalic/enzyme."
        ),
    },
    {
        "code": "N1",
        "dilution_ko": (
            "베이킹소다: 페이스트(가루+물 약간) 또는 담금 시 1L에 1–2큰술. "
            "옥살산(X2)·산 처리 후 중화·냄새 제거. 산과 한꺼번에 섞어 거품 폭주 시키지 말 것 — 헹군 뒤 사용."
        ),
        "dilution_vi": (
            "Baking soda: paste hoặc 1–2 muỗng / 1L. Trung hòa sau X2/acid — "
            "xả trước rồi mới N1 (không trộn ồ ạt với acid đặc)."
        ),
        "dilution_en": "Baking soda: paste or 1–2 tbsp/L. Neutralize after acid rinse — do not dump into strong acid.",
    },
    {
        "code": "N2",
        "dilution_ko": (
            "소금(선혈 보조): 찬물 1L에 큰술 2 — 신선 핏자국 흡수·보조만. "
            "온수 금지. 본처리는 효소(E1)."
        ),
        "dilution_vi": "Muối: 2 muỗng / 1L lạnh (máu tươi phụ). CAM nóng. Chính: enzyme E1.",
        "dilution_en": "Salt: 2 tbsp/1L cold for fresh blood assist only. No hot water. Main: E1.",
    },
    {
        "code": "N3",
        "dilution_ko": "옥수수전분·전분: 기름 얼룩에 두껍게 덮어 10–30분 후 털기. 흡착 후 주방세제(D2).",
        "dilution_vi": "Tinh bột: phủ dày 10–30 phút rồi phủi → D2.",
        "dilution_en": "Starch absorbent: thick cover 10–30 min then brush off → dish soap.",
    },
    {
        "code": "S1",
        "dilution_ko": (
            "워시프렌즈 중성세제: 병 안내 용량. 실크·울·아세테이트 우선. "
            "효소·산소·염소·강한 산 대신 국소·찬물."
        ),
        "dilution_vi": "S1 Wash Friends: theo chai. Ưu tiên lụa/len. Thay enzyme/oxy/acid mạnh.",
        "dilution_en": "WF neutral: per bottle. Silk/wool first. Replaces enzyme/oxygen/strong acid on delicates.",
    },
    {
        "code": "X1",
        "dilution_ko": (
            "환원 표백제(하이드로설파이트): 흰 면·린넨만. "
            "40–50℃ 물 1L에 큰술 1 — 즉석 조제 → 15–30분 → 즉시 헹굼. "
            "니트릴 장갑. 유색·실크·울 금지. 락스와 혼합 금지."
        ),
        "dilution_vi": (
            "Tẩy khử (hydrosulfite): CHỈ cotton/linen trắng. "
            "1L nước 40–50°C + 1 muỗng — pha mới → 15–30 phút → xả ngay. Găng. CẤM trộn Javel."
        ),
        "dilution_en": (
            "Reducing bleach: white cotton/linen only. 1 tbsp/1L at 40–50°C fresh mix; "
            "15–30 min; rinse. Gloves. Never chlorine mix."
        ),
    },
    {
        "code": "X2",
        "dilution_ko": (
            "옥살산(녹·철): 라벨 약 2–3% 또는 병 안내. 면·린넨·폴리 ~20–30분. "
            "니트릴 장갑 필수(독성·피부 손상). 실크·울 금지→식초(A3) 약하게. "
            "사용 후 여러 번 헹굼 → 베이킹소다(N1) 약희석 중화. "
            "락스(B2)로 철 얼룩 처리 금지(철 고착). 락스와 혼합 금지."
        ),
        "dilution_vi": (
            "Acid oxalic: ~2–3% theo nhãn; cotton/poly ~20–30 phút. Găng nitrile BẮT BUỘC. "
            "CẤM lụa/len → A3 nhẹ. Xả kỹ → N1 trung hòa. CẤM Javel (cố định sắt). CẤM trộn Javel."
        ),
        "dilution_en": (
            "Oxalic ~2–3%; cotton/poly 20–30 min; nitrile required; rinse well then N1 neutralize. "
            "Never silk/wool. Never chlorine on rust / never mix chlorine."
        ),
    },
    {
        "code": "WF_SOFT",
        "dilution_ko": "워시프렌즈 유연제: 병 안내 — 헹굼·마감만. 얼룩 처리·표백 단계에 쓰지 말 것.",
        "dilution_vi": "Softener WF: theo chai — chỉ xả/hoàn thiện. Không dùng khi xử lý vết.",
        "dilution_en": "WF softener: per bottle; finish rinse only — never in stain chemistry.",
    },
    {
        "code": "WF_FRAG",
        "dilution_ko": "워시프렌즈 향수 스프레이: 건조·청결 후 1–2회 약분무. 흠뻑·얼룩 위 분사 금지.",
        "dilution_vi": "Xịt hương WF: 1–2 phát sau khô/sạch. Không ngập lên vết.",
        "dilution_en": "WF fragrance: 1–2 light sprays after dry/clean. Never soak stain.",
    },
    {
        "code": "L1",
        "dilution_ko": "가죽 클리너: 병 안내 — 천에 묻혀 국소만. 통담금·세탁기·표백 금지.",
        "dilution_vi": "Leather cleaner: theo nhãn — khăn cục bộ. CẤM ngâm/máy/tẩy.",
        "dilution_en": "Leather cleaner: cloth spot only per bottle. No soak/machine/bleach.",
    },
    {
        "code": "L2",
        "dilution_ko": "가죽 크림: 클리너 후 완전 건조 → 원액 얇게 → 잉여 닦기.",
        "dilution_vi": "Kem dưỡng: sau sạch+khô → mỏng → lau dư.",
        "dilution_en": "Leather cream: after clean+dry; thin coat; wipe excess.",
    },
    {
        "code": "L3",
        "dilution_ko": "가죽 프로텍터: 크림 마른 뒤 20–30cm 약분무(선택).",
        "dilution_vi": "Protector: sau kem khô — xịt nhẹ 20–30cm.",
        "dilution_en": "Leather protector: light spray 20–30cm after cream cured.",
    },
]


def dilution_seed_rows() -> list[dict[str, str]]:
    return [
        {"code": d["code"], "dilution_ko": d["dilution_ko"], "dilution_vi": d["dilution_vi"]}
        for d in DILUTION_V9
    ]


def apply_dilution_to_chem_meta(chem_meta: dict) -> None:
    for d in DILUTION_V9:
        code = d["code"]
        if code not in chem_meta:
            chem_meta[code] = {
                "name_ko": code,
                "name_vi": code,
                "name_en": code,
            }
        chem_meta[code]["dilution_ko"] = d["dilution_ko"]
        chem_meta[code]["dilution_vi"] = d["dilution_vi"]
        if d.get("dilution_en"):
            chem_meta[code]["dilution_en"] = d["dilution_en"]
