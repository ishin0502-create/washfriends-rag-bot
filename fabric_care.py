# -*- coding: utf-8 -*-
"""Fabric standalone curriculum (F1–F7 core + leather/suede/fur overview).

Synthetic Item ids I_FABRIC_* — used when user asks fabric care without a
specific garment. Full KO/VI/EN. Truth: Fabric seed flags + FABRIC_NEVER_USE_CARD.
"""
from __future__ import annotations

from typing import Any

FABRIC_CURRICULUM_IDS = frozenset({
    "I_FABRIC_COTTON",
    "I_FABRIC_POLY",
    "I_FABRIC_WOOL",
    "I_FABRIC_SILK",
    "I_FABRIC_LINEN",
    "I_FABRIC_DENIM",
    "I_FABRIC_RAYON",
    "I_FABRIC_LEATHER",
    "I_FABRIC_SUEDE",
    "I_FABRIC_FUR",
})

# token from _infer_fabric_from_text → curriculum item
FABRIC_TOKEN_TO_ITEM = {
    "cotton": "I_FABRIC_COTTON",
    "polyester": "I_FABRIC_POLY",
    "wool": "I_FABRIC_WOOL",
    "silk": "I_FABRIC_SILK",
    "linen": "I_FABRIC_LINEN",
    "denim": "I_FABRIC_DENIM",
    "rayon": "I_FABRIC_RAYON",
    "leather": "I_FABRIC_LEATHER",
    "suede": "I_FABRIC_SUEDE",
    "fur": "I_FABRIC_FUR",
}


def education_for_fabric(item_id: str) -> dict[str, str]:
    return {
        "I_FABRIC_COTTON": _cotton,
        "I_FABRIC_POLY": _poly,
        "I_FABRIC_WOOL": _wool,
        "I_FABRIC_SILK": _silk,
        "I_FABRIC_LINEN": _linen,
        "I_FABRIC_DENIM": _denim_fabric,
        "I_FABRIC_RAYON": _rayon,
        "I_FABRIC_LEATHER": _leather,
        "I_FABRIC_SUEDE": _suede,
        "I_FABRIC_FUR": _fur,
    }.get(item_id, lambda: {})()


def _cotton() -> dict[str, str]:
    return {
        "precheck_ko": "면(F1): 라벨 수온(보통 ≤60℃). 흰/유색 분리. 수축·이염 고지.",
        "why_ko": "[왜] 면=내열·효소·표백 상대적으로 강함. 흰만 염소(B2) 가능. 유색은 산소(B1) 신중.",
        "fresh_path_ko": "(1)분리. (2)얼룩이면 해당 SOP. (3)라벨 온도 기계. (4)흰: B1/B2 신중. (5)건조 전 강광.",
        "dried_path_ko": "황변·이염: 별도 SOP. 고온 건조는 수축↑.",
        "motion_ko": "Cap2–3 일반; 섬세 프린트는 Cap1–2",
        "water_temp_ko": "라벨; 보통 ≤40–60℃",
        "aftercare_ko": "건조기 가능(라벨). 다리미 중고온.",
        "sense_check_ko": "눈: 이염. 손: 수축 없음.",
        "success_rate_ko": "일반 면: 양호.",
        "refuse_when_ko": "유색에 염소 강제 → 거절.",
        "must_include_ko": "흰/유색 분리, 라벨 수온, 유색 락스 금지",
        "precheck_vi": "Cotton F1: nhan nhiet. Tach trang/mau.",
        "why_vi": "[Tai sao] Cotton chiu nhiet/enzyme. Trang: B2 duoc. Mau: than B1.",
        "fresh_path_vi": "(1)Tach. (2)Vet → SOP. (3)May theo nhan. (4)Trang B1/B2. (5)Anh sang.",
        "dried_path_vi": "Vang/lo mau: SOP. Say nong → rut.",
        "motion_vi": "Cap2-3",
        "water_temp_vi": "Theo nhan; thuong <=40-60C",
        "aftercare_vi": "Say neu nhan. Ui vua-cao.",
        "sense_check_vi": "Mat: lo mau. Tay: rut.",
        "success_rate_vi": "Tot.",
        "refuse_when_vi": "Bat Javel mau → tu choi.",
        "must_include_vi": "tach trang/mau, theo nhan, CAM Javel mau",
        "precheck_en": "Cotton F1: label temp (often ≤60°C). Sort lights/darks.",
        "why_en": "[Why] Heat/enzyme tolerant. Chlorine (B2) whites only. Colors: careful oxygen (B1).",
        "fresh_path_en": "(1)Sort. (2)Stain → SOP. (3)Machine per label. (4)Whites B1/B2. (5)Strong light.",
        "dried_path_en": "Yellow/bleed: separate SOP. Hot dryer → shrink.",
        "motion_en": "Cap2–3; prints Cap1–2.",
        "water_temp_en": "Label; often ≤40–60°C.",
        "aftercare_en": "Dryer if labeled. Med–hot iron.",
        "sense_check_en": "Eyes: bleed. Hand: no shrink.",
        "success_rate_en": "Good.",
        "refuse_when_en": "Forced chlorine on colors → refuse.",
        "must_include_en": "sort lights/darks, label temp, no chlorine on colors",
    }


def _poly() -> dict[str, str]:
    return {
        "precheck_ko": "폴리에스터(F2): 라벨 ≤40℃. 고온·강한 솔벤트 주의. 유연제 과다=흡습↓(기능성).",
        "why_ko": "[왜] 폴리=열에 약해 수축·광택. 염소 표백 비권장. 기능성=유연제 금지.",
        "fresh_path_ko": "(1)라벨. (2)≤40℃·세제 소량. (3)기능성: 유연제 금지·추가 헹굼. (4)저온 건조/그늘.",
        "dried_path_ko": "기름 얼룩: D2 전처리. 고온 건조 금지.",
        "motion_ko": "Cap2",
        "water_temp_ko": "≤40℃",
        "aftercare_ko": "저온 건조. 다리미 저온.",
        "sense_check_ko": "손: 잔여 세제 없음(기능성).",
        "success_rate_ko": "양호.",
        "refuse_when_ko": "고온·염소 강제 → 거절.",
        "must_include_ko": "≤40℃, 유연제 주의, 고온건조 금지",
        "precheck_vi": "Polyester F2: <=40C. CAM nhiet cao. Softener it (do the thao).",
        "why_vi": "[Tai sao] Poly yeu nhiet. Than bleach. Do wicking: CAM xa vai.",
        "fresh_path_vi": "(1)Nhan. (2)<=40C bot it. (3)The thao: CAM xa + xa them. (4)Say thap/phoi.",
        "dried_path_vi": "Dau: pretreat D2. CAM say nong.",
        "motion_vi": "Cap2",
        "water_temp_vi": "<=40C",
        "aftercare_vi": "Say thap. Ui thap.",
        "sense_check_vi": "Tay: het bot (do the thao).",
        "success_rate_vi": "Tot.",
        "refuse_when_vi": "Bat nhiet/Javel → tu choi.",
        "must_include_vi": "<=40C, than xa vai, CAM say nong",
        "precheck_en": "Polyester F2: label ≤40°C. Avoid high heat/harsh solvent. Softener clogs wicking.",
        "why_en": "[Why] Heat damages poly. Avoid chlorine. Performance: no softener.",
        "fresh_path_en": "(1)Label. (2)≤40°C little detergent. (3)Sport: no softener + extra rinse. (4)Low dryer/shade.",
        "dried_path_en": "Oil: D2 pretreat. No hot dryer.",
        "motion_en": "Cap2.",
        "water_temp_en": "≤40°C.",
        "aftercare_en": "Low heat dry. Cool iron.",
        "sense_check_en": "Hand: no detergent slip on sportwear.",
        "success_rate_en": "Good.",
        "refuse_when_en": "Forced high heat/chlorine → refuse.",
        "must_include_en": "≤40°C, softener caution, no hot dryer",
    }


def _wool() -> dict[str, str]:
    return {
        "precheck_ko": "울(F3): 라벨. 효소·산소/염소 표백·강한 산 금지. 수축·펠팅 고지.",
        "why_ko": "[왜] 울=단백질 섬유. 효소·표백·열·비틀기=영구 손상. S1·찬물·Cap1–2.",
        "fresh_path_ko": "(1)드라이 또는 손세탁 S1 찬물. (2)비틀지 말 것. (3)평건·형태 고정. (4)건조기 금지.",
        "dried_path_ko": "수축 후 복원 한계 고지. 얼룩은 울 안전 경로만.",
        "motion_ko": "Cap1–2. 비틀기 금지",
        "water_temp_ko": "≤30℃ 찬물",
        "aftercare_ko": "평건. 저온 스팀. 건조기 금지.",
        "sense_check_ko": "손: 펠팅·수축 없음.",
        "success_rate_ko": "손세탁 신중: 중간~양호. 기계 일반: 위험.",
        "refuse_when_ko": "효소·표백·건조기 강제 → 거절.",
        "must_include_ko": "S1·찬물, 효소·표백 금지, 평건, 건조기 금지",
        "precheck_vi": "Len F3: CAM enzyme/tay/acid manh. Bao rut.",
        "why_vi": "[Tai sao] Len protein — enzyme/tay/nhiet/vat = hong. S1+lanh Cap1-2.",
        "fresh_path_vi": "(1)Dry hoac tay S1 lanh. (2)CAM vat. (3)Phoi phang. (4)CAM say.",
        "dried_path_vi": "Rut: bao gioi han. Vet: chi duong an toan len.",
        "motion_vi": "Cap1-2; CAM vat",
        "water_temp_vi": "<=30C",
        "aftercare_vi": "Phoi phang. Steam thap. CAM say.",
        "sense_check_vi": "Tay: khong felting.",
        "success_rate_vi": "Tay than: TB-tot. May thuong: thap.",
        "refuse_when_vi": "Bat enzyme/tay/say → tu choi.",
        "must_include_vi": "S1 lanh, CAM enzyme/tay, phoi phang, CAM say",
        "precheck_en": "Wool F3: no enzyme/oxygen/chlorine/strong acid. Disclose shrink/felt.",
        "why_en": "[Why] Protein fiber. Enzyme/bleach/heat/wring permanent damage. S1 cold Cap1–2.",
        "fresh_path_en": "(1)Dry-clean or hand S1 cold. (2)No wring. (3)Flat reshape dry. (4)No dryer.",
        "dried_path_en": "Post-shrink restore limited. Stains: wool-safe only.",
        "motion_en": "Cap1–2. No wring.",
        "water_temp_en": "≤30°C cold.",
        "aftercare_en": "Flat dry. Low steam. No dryer.",
        "sense_check_en": "Hand: no felting/shrink.",
        "success_rate_en": "Careful hand: fair–good. Normal machine: risky.",
        "refuse_when_en": "Forced enzyme/bleach/dryer → refuse.",
        "must_include_en": "S1 cold, no enzyme/bleach, flat dry, no dryer",
    }


def _silk() -> dict[str, str]:
    return {
        "precheck_ko": "실크(F4): 효소·산소/염소·강한 산·옥살산·환원표백 금지. 물짐·이염 고지.",
        "why_ko": "[왜] 실크=섬세 단백질. S1·찬물·Cap1–2. 과다 수분=물짐.",
        "fresh_path_ko": "(1)고가·천연염→드라이 우선. (2)손세탁 S1 찬물 Cap1. (3)눌러 헹굼. (4)그늘 평건. (5)안감 저온 다리미.",
        "dried_path_ko": "물짐 있으면 추가 물 최소화·고지.",
        "motion_ko": "Cap1–2",
        "water_temp_ko": "≤30℃",
        "aftercare_ko": "그늘. 스팀 최소. 건조기 금지.",
        "sense_check_ko": "눈: 물짐·이염.",
        "success_rate_ko": "손세탁: 중간. 기계: 위험.",
        "refuse_when_ko": "표백·효소·기계 강제 → 거절.",
        "must_include_ko": "S1·찬물, 표백·효소 금지, Cap1, 물짐 고지",
        "precheck_vi": "Lua F4: CAM enzyme/tay/acid manh/X2/X1. Bao vet nuoc.",
        "why_vi": "[Tai sao] Lua mong — S1+lanh Cap1-2. Nuoc nhieu = vet nuoc.",
        "fresh_path_vi": "(1)Dat/nhuan → dry. (2)Tay S1 lanh Cap1. (3)Ep xa. (4)Phoi phang. (5)Ui mat trai thap.",
        "dried_path_vi": "Vet nuoc: giam nuoc, bao.",
        "motion_vi": "Cap1-2",
        "water_temp_vi": "<=30C",
        "aftercare_vi": "Bong mat. It steam. CAM say.",
        "sense_check_vi": "Mat: vet nuoc/lo mau.",
        "success_rate_vi": "Tay: TB. May: thap.",
        "refuse_when_vi": "Bat tay/enzyme/may → tu choi.",
        "must_include_vi": "S1 lanh, CAM tay/enzyme, Cap1, bao vet nuoc",
        "precheck_en": "Silk F4: NEVER enzyme, oxygen/chlorine, strong acid, oxalic, reducing bleach. Disclose water rings.",
        "why_en": "[Why] Delicate protein. S1 cold Cap1–2. Excess water → rings.",
        "fresh_path_en": "(1)Expensive/natural dye → dry-clean. (2)Hand S1 cold Cap1. (3)Press-rinse. (4)Shade flat. (5)Reverse cool iron.",
        "dried_path_en": "If rings: minimize more water; disclose.",
        "motion_en": "Cap1–2.",
        "water_temp_en": "≤30°C.",
        "aftercare_en": "Shade. Minimal steam. No dryer.",
        "sense_check_en": "Eyes: rings/bleed.",
        "success_rate_en": "Hand: fair. Machine: risky.",
        "refuse_when_en": "Forced bleach/enzyme/machine → refuse.",
        "must_include_en": "S1 cold, no bleach/enzyme, Cap1, disclose water rings",
    }


def _linen() -> dict[str, str]:
    return {
        "precheck_ko": "린넨·마(F5): 수축 3–8% 고지. 흰/유색 분리. 구김=특성.",
        "why_ko": "[왜] 린넨=물·열에 구김. 중성·충분한 헹굼. 축축할 때 다리미/스팀.",
        "fresh_path_ko": "(1)라벨. (2)30–40℃ 중성. (3)충분히 헹굼. (4)축축할 때 다리미/스팀. (5)건조기 과열 주의.",
        "dried_path_ko": "수축·구김은 특성 고지.",
        "motion_ko": "Cap2",
        "water_temp_ko": "~30–40℃",
        "aftercare_ko": "축축할 때 다리미. 걸이.",
        "sense_check_ko": "손: 잔여 세제 없음.",
        "success_rate_ko": "양호(수축 고지 시).",
        "refuse_when_ko": "수축 0% 보장 요구 → 거절.",
        "must_include_ko": "수축 고지, 30–40℃, 축축할 때 다림질",
        "precheck_vi": "Linen F5: bao rut 3-8%. Tach mau. Nhao = dac trung.",
        "why_vi": "[Tai sao] De nhao — trung tinh + xa ky. Ui/steam khi am.",
        "fresh_path_vi": "(1)Nhan. (2)30-40C trung tinh. (3)Xa ky. (4)Ui/steam khi am. (5)Than say nong.",
        "dried_path_vi": "Rut/nhao: bao dac trung.",
        "motion_vi": "Cap2",
        "water_temp_vi": "~30-40C",
        "aftercare_vi": "Ui khi am. Treo.",
        "sense_check_vi": "Tay: het bot.",
        "success_rate_vi": "Tot neu bao rut.",
        "refuse_when_vi": "Cam ket 0% rut → tu choi.",
        "must_include_vi": "bao rut, 30-40C, ui khi am",
        "precheck_en": "Linen F5: disclose 3–8% shrink. Sort colors. Wrinkles are normal.",
        "why_en": "[Why] Wrinkles with water/heat. Mild soap + thorough rinse. Iron/steam damp.",
        "fresh_path_en": "(1)Label. (2)30–40°C mild. (3)Rinse well. (4)Iron/steam damp. (5)Avoid overhot dryer.",
        "dried_path_en": "Shrink/wrinkle: disclose as trait.",
        "motion_en": "Cap2.",
        "water_temp_en": "~30–40°C.",
        "aftercare_en": "Iron damp. Hang.",
        "sense_check_en": "Hand: no detergent slip.",
        "success_rate_en": "Good with shrink disclosure.",
        "refuse_when_en": "0% shrink guarantee → refuse.",
        "must_include_en": "disclose shrink, 30–40°C, iron damp",
    }


def _denim_fabric() -> dict[str, str]:
    return {
        "precheck_ko": "데님 원단(F6): 첫 물빠짐 정상. 흰옷 분리. 세부 품목은 청바지 카드(I_DENIM) 연계.",
        "why_ko": "[왜] 인디고 이염. 뒤집기·찬물·세제 소량. 과도한 표백=손상.",
        "fresh_path_ko": "(1)뒤집기. (2)찬물/~30℃. (3)첫 2–3회 단독. (4)그늘 건조. (5)염소 금지.",
        "dried_path_ko": "색빠짐 클레임: 특성 고지.",
        "motion_ko": "Cap2–3",
        "water_temp_ko": "찬물 / ~30℃",
        "aftercare_ko": "그늘. 흰옷 분리 유지.",
        "sense_check_ko": "눈: 흰옷 이염 없음.",
        "success_rate_ko": "양호(분리 시).",
        "refuse_when_ko": "흰옷 동시세탁 강제 → 거절.",
        "must_include_ko": "뒤집기, 찬물, 흰옷 분리, 첫 물빠짐 정상",
        "precheck_vi": "Denim F6: ra mau lan dau OK. Tach trang. Xem them I_DENIM.",
        "why_vi": "[Tai sao] Indigo lo mau. Lat trai + lanh + bot it.",
        "fresh_path_vi": "(1)Lat. (2)Lanh/~30C. (3)2-3 lan rieng. (4)Phoi bong. (5)CAM Javel.",
        "dried_path_vi": "Phai mau: bao dac trung.",
        "motion_vi": "Cap2-3",
        "water_temp_vi": "Lanh / ~30C",
        "aftercare_vi": "Bong mat. Tach trang.",
        "sense_check_vi": "Mat: khong lo sang trang.",
        "success_rate_vi": "Tot neu tach.",
        "refuse_when_vi": "Bat giat chung trang → tu choi.",
        "must_include_vi": "lat trai, lanh, tach trang, ra mau lan dau OK",
        "precheck_en": "Denim fabric F6: first bleed normal. Never with whites. See I_DENIM for jeans SOP.",
        "why_en": "[Why] Indigo transfer. Inside out + cold + little detergent.",
        "fresh_path_en": "(1)Inside out. (2)Cold/~30°C. (3)First 2–3 alone. (4)Shade. (5)No chlorine.",
        "dried_path_en": "Fade claims: disclose trait.",
        "motion_en": "Cap2–3.",
        "water_temp_en": "Cold / ~30°C.",
        "aftercare_en": "Shade. Keep away from whites.",
        "sense_check_en": "Eyes: no white transfer.",
        "success_rate_en": "Good if sorted.",
        "refuse_when_en": "Forced wash with whites → refuse.",
        "must_include_en": "inside out, cold, separate whites, first bleed OK",
    }


def _rayon() -> dict[str, str]:
    return {
        "precheck_ko": "레이온(F7): 젖으면 약함. 아세톤 금지. 손세탁·형태 고정 건조.",
        "why_ko": "[왜] 레이온=젖은 상태 강도↓. 기계·아세톤 위험. Cap1–2·평건.",
        "fresh_path_ko": "(1)손세탁 찬물 중성. (2)비틀지 말 것. (3)평건 형태 고정. (4)아세톤·강한 솔벤트 금지.",
        "dried_path_ko": "늘어남·찢김 고지.",
        "motion_ko": "Cap1–2",
        "water_temp_ko": "≤30℃",
        "aftercare_ko": "평건. 건조기 금지.",
        "sense_check_ko": "손: 늘어남 없음.",
        "success_rate_ko": "손세탁: 중간.",
        "refuse_when_ko": "아세톤·강한 기계 요구 → 거절.",
        "must_include_ko": "손세탁, 아세톤 금지, 평건, 젖은 상태 약함",
        "precheck_vi": "Rayon F7: yeu khi uot. CAM acetone. Tay + giu form.",
        "why_vi": "[Tai sao] Uot = yeu. CAM may/acetone. Cap1-2 phoi phang.",
        "fresh_path_vi": "(1)Tay lanh trung tinh. (2)CAM vat. (3)Phoi phang. (4)CAM acetone.",
        "dried_path_vi": "Bao gian/rach.",
        "motion_vi": "Cap1-2",
        "water_temp_vi": "<=30C",
        "aftercare_vi": "Phoi phang. CAM say.",
        "sense_check_vi": "Tay: khong gian.",
        "success_rate_vi": "Tay: TB.",
        "refuse_when_vi": "Bat acetone/may → tu choi.",
        "must_include_vi": "tay, CAM acetone, phoi phang, yeu khi uot",
        "precheck_en": "Rayon F7: weak when wet. No acetone. Hand wash + reshape dry.",
        "why_en": "[Why] Wet strength drops. Machine/acetone risk. Cap1–2 flat dry.",
        "fresh_path_en": "(1)Hand cold mild. (2)No wring. (3)Flat reshape. (4)No acetone/harsh solvent.",
        "dried_path_en": "Disclose stretch/tear risk.",
        "motion_en": "Cap1–2.",
        "water_temp_en": "≤30°C.",
        "aftercare_en": "Flat dry. No dryer.",
        "sense_check_en": "Hand: no stretch-out.",
        "success_rate_en": "Hand: fair.",
        "refuse_when_en": "Forced acetone/harsh machine → refuse.",
        "must_include_en": "hand wash, no acetone, flat dry, weak when wet",
    }


def _leather() -> dict[str, str]:
    return {
        "precheck_ko": "가죽(F8): 세탁기·표백·효소·강한 침지 금지. 최소 수분·전문 크림.",
        "why_ko": "[왜] 가죽은 섬유 세탁이 아님. 물 과다=변형·얼룩.",
        "fresh_path_ko": "(1)마른 흙 제거. (2)약간 젖은 천 국소. (3)가죽 크림. (4)그늘 건조. (5)세탁기 금지.",
        "dried_path_ko": "심하면 전문 가죽. 100% 비보장.",
        "motion_ko": "Cap1 닦기",
        "water_temp_ko": "최소 수분·상온",
        "aftercare_ko": "크림·통풍. 건조기 금지.",
        "sense_check_ko": "눈: 물짐·변형.",
        "success_rate_ko": "국소: 중간. 기계: 실패.",
        "refuse_when_ko": "세탁기·표백 강제 → 거절.",
        "must_include_ko": "세탁기 금지, 최소 수분, 크림, 전문 이관",
        "precheck_vi": "Da F8: CAM may/tay/enzyme/ngam. It nuoc + kem.",
        "why_vi": "[Tai sao] Khong giat nhu vai. Nuoc nhieu = bien dang.",
        "fresh_path_vi": "(1)Chai kho. (2)Lau am cuc bo. (3)Kem da. (4)Phoi bong. (5)CAM may.",
        "dried_path_vi": "Nang → chuyen. Bao 100%.",
        "motion_vi": "Cap1 lau",
        "water_temp_vi": "It nuoc",
        "aftercare_vi": "Kem. CAM say.",
        "sense_check_vi": "Mat: vet nuoc/bien dang.",
        "success_rate_vi": "Cuc bo: TB. May: that bai.",
        "refuse_when_vi": "Bat may/tay → tu choi.",
        "must_include_vi": "CAM may, it nuoc, kem, chuyen neu nang",
        "precheck_en": "Leather F8: NEVER washer/bleach/enzyme/heavy soak. Minimal water + cream.",
        "why_en": "[Why] Not textile wash. Excess water warps/stains.",
        "fresh_path_en": "(1)Dry brush. (2)Damp wipe spot. (3)Leather cream. (4)Shade. (5)No washer.",
        "dried_path_en": "Severe → pro. No 100%.",
        "motion_en": "Cap1 wipe.",
        "water_temp_en": "Minimal ambient moisture.",
        "aftercare_en": "Cream + airflow. No dryer.",
        "sense_check_en": "Eyes: water marks/warp.",
        "success_rate_en": "Spot: fair. Machine: fail.",
        "refuse_when_en": "Forced washer/bleach → refuse.",
        "must_include_en": "no washer, minimal water, cream, refer if severe",
    }


def _suede() -> dict[str, str]:
    return {
        "precheck_ko": "스웨이드(F9): 물·표백·효소 과다 금지. 마른 브러시 우선.",
        "why_ko": "[왜] 스웨이드=기모. 물=얼룩·굳음. 마른 관리 우선, 심하면 전문.",
        "fresh_path_ko": "(1)마른 브러시. (2)국소 최소 수분. (3)전문 스웨이드 클리너(라벨). (4)세탁기 금지.",
        "dried_path_ko": "물짐·굳음: 전문. 고지.",
        "motion_ko": "Cap1 마른 브러시",
        "water_temp_ko": "물 최소화",
        "aftercare_ko": "그늘. 발수 스프레이 선택.",
        "sense_check_ko": "눈: 물짐·기모.",
        "success_rate_ko": "마른 관리: 중간. 물세탁: 낮음.",
        "refuse_when_ko": "물세탁·표백 강제 → 거절.",
        "must_include_ko": "마른 브러시 우선, 물 최소화, 세탁기 금지",
        "precheck_vi": "Suede F9: CAM nuoc/tay/enzyme manh. Chai kho uu tien.",
        "why_vi": "[Tai sao] Long mong — nuoc = vet. Chai kho; nang → chuyen.",
        "fresh_path_vi": "(1)Chai kho. (2)It nuoc cuc bo. (3)Cleaner suede neu co. (4)CAM may.",
        "dried_path_vi": "Vet nuoc: chuyen. Bao.",
        "motion_vi": "Cap1 chai kho",
        "water_temp_vi": "It nuoc",
        "aftercare_vi": "Bong mat. Xit DWR tuy chon.",
        "sense_check_vi": "Mat: vet nuoc/long.",
        "success_rate_vi": "Chai kho: TB. Wet: thap.",
        "refuse_when_vi": "Bat giat nuoc/tay → tu choi.",
        "must_include_vi": "chai kho uu tien, it nuoc, CAM may",
        "precheck_en": "Suede F9: avoid water/bleach/heavy enzyme. Dry brush first.",
        "why_en": "[Why] Napped surface. Water marks/stiffens. Dry care; severe → pro.",
        "fresh_path_en": "(1)Dry brush. (2)Minimal damp spot. (3)Suede cleaner if labeled. (4)No washer.",
        "dried_path_en": "Water marks → pro. Disclose.",
        "motion_en": "Cap1 dry brush.",
        "water_temp_en": "Minimize water.",
        "aftercare_en": "Shade. Optional DWR.",
        "sense_check_en": "Eyes: water marks/nap.",
        "success_rate_en": "Dry care: fair. Wet wash: low.",
        "refuse_when_en": "Forced wet wash/bleach → refuse.",
        "must_include_en": "dry brush first, minimize water, no washer",
    }


def _fur() -> dict[str, str]:
    return {
        "precheck_ko": "모피(F10): 물세탁·표백·건조기 금지. 전문 모피 클리닝.",
        "why_ko": "[왜] 모피=가죽+털. 가정 물세탁=영구 손상.",
        "fresh_path_ko": "(1)전문 모피만. (2)가정: 통풍·습기 제거 수준. (3)물·표백·건조기 금지.",
        "dried_path_ko": "이미 물세탁: 추가 강처리 금지·고지.",
        "motion_ko": "Cap0 — 이관",
        "water_temp_ko": "가정 물세탁 해당 없음",
        "aftercare_ko": "통풍 보관. 습기·곰팡이 주의.",
        "sense_check_ko": "눈: 털 엉킴·가죽 건조.",
        "success_rate_ko": "전문: 양호. 가정 물세탁: 실패.",
        "refuse_when_ko": "물세탁 요구 → 거절·전문 안내.",
        "must_include_ko": "전문 모피만, 물세탁·표백·건조기 금지",
        "precheck_vi": "Fur F10: CAM giat nuoc/tay/say. Chuyen fur.",
        "why_vi": "[Tai sao] Da+long — wet nha = hong vinh vien.",
        "fresh_path_vi": "(1)Chi chuyen fur. (2)Nha: thoang kho. (3)CAM nuoc/tay/say.",
        "dried_path_vi": "Da wet: dung xu ly manh, bao.",
        "motion_vi": "Cap0 — chuyen",
        "water_temp_vi": "N/A wet nha",
        "aftercare_vi": "Cat thoang. Tranh moc.",
        "sense_check_vi": "Mat: long xoan/da kho.",
        "success_rate_vi": "Chuyen: tot. Wet nha: that bai.",
        "refuse_when_vi": "Bat giat nuoc → tu choi.",
        "must_include_vi": "chi chuyen fur, CAM nuoc/tay/say",
        "precheck_en": "Fur F10: NEVER wet wash/bleach/dryer. Professional fur only.",
        "why_en": "[Why] Hide+hair. Home wet wash = permanent damage.",
        "fresh_path_en": "(1)Pro fur only. (2)Home: air/dehumidify only. (3)No water/bleach/dryer.",
        "dried_path_en": "Already wet-washed: stop aggressive treatment; disclose.",
        "motion_en": "Cap0 — refer.",
        "water_temp_en": "N/A for home wet.",
        "aftercare_en": "Airy storage. Watch mold.",
        "sense_check_en": "Eyes: matting/hide dryness.",
        "success_rate_en": "Pro: good. Home wet: fail.",
        "refuse_when_en": "Forced wet wash → refuse; refer pro.",
        "must_include_en": "pro fur only, no wet wash/bleach/dryer",
    }


def apply_fabric_curriculum_hints(graph: dict[str, Any], item_id: str) -> dict[str, Any]:
    if item_id not in FABRIC_CURRICULUM_IDS:
        return graph
    out = dict(graph)
    out.setdefault("empty_chems_ok", True)
    return out


_FABRIC_META = {
    "I_FABRIC_COTTON": ("Cotton fabric care", "Cham soc vai cotton", "면 원단 관리", "F1"),
    "I_FABRIC_POLY": ("Polyester fabric care", "Cham soc vai polyester", "폴리에스터 원단 관리", "F2"),
    "I_FABRIC_WOOL": ("Wool fabric care", "Cham soc vai len", "울 원단 관리", "F3"),
    "I_FABRIC_SILK": ("Silk fabric care", "Cham soc vai lua", "실크 원단 관리", "F4"),
    "I_FABRIC_LINEN": ("Linen fabric care", "Cham soc vai linen", "린넨·마 원단 관리", "F5"),
    "I_FABRIC_DENIM": ("Denim fabric care", "Cham soc vai denim", "데님 원단 관리", "F6"),
    "I_FABRIC_RAYON": ("Rayon fabric care", "Cham soc vai rayon", "레이온 원단 관리", "F7"),
    "I_FABRIC_LEATHER": ("Leather material care", "Cham soc da", "가죽 소재 관리", "F8"),
    "I_FABRIC_SUEDE": ("Suede material care", "Cham soc suede", "스웨이드 소재 관리", "F9"),
    "I_FABRIC_FUR": ("Fur material care", "Cham soc long thu", "모피 소재 관리", "F10"),
}


def fabric_seed_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for iid, (name, name_vi, name_ko, fid) in _FABRIC_META.items():
        edu = education_for_fabric(iid)
        row = {
            "id": iid,
            "name": name,
            "name_vi": name_vi,
            "name_ko": name_ko,
            "fabric_id": fid,
        }
        row.update(edu)
        rows.append(row)
    return rows
