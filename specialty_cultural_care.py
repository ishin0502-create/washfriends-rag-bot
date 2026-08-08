# -*- coding: utf-8 -*-
"""Cultural / delicate specialty: necktie, áo dài, hanbok, smoke odor, uniform.

Full KO / VI / EN — sanitize picks one lang. Truth from main.py Item seeds +
w3_clothing_items (I_UNIFORM). No invented chemistry.
"""
from __future__ import annotations

from typing import Any

CULTURAL_SPECIALTY_IDS = frozenset({
    "I_NECKTIE",
    "I_AO_DAI",
    "I_HANBOK",
    "I_ODOR_SMOKE",
    "I_UNIFORM",
})


def education_for_cultural(item_id: str) -> dict[str, str]:
    return {
        "I_NECKTIE": _necktie,
        "I_AO_DAI": _ao_dai,
        "I_HANBOK": _hanbok,
        "I_ODOR_SMOKE": _odor_smoke,
        "I_UNIFORM": _uniform,
    }.get(item_id, lambda: {})()


def _necktie() -> dict[str, str]:
    return {
        "precheck_ko": (
            "넥타이(실크·폴리): 사진. 라벨로 실크/폴리 구분. "
            "통담금·세탁기·짜기 금지. 큰 얼룩·고가품은 드라이 우선. 국소 스포팅만."
        ),
        "why_ko": (
            "[왜 이 순서] 넥타이=형태 유지 최우선. 물세탁·통담금=형태 붕괴. "
            "얼룩: Cap1 바깥→안 블롯 + 아래 흡수지; 희석 D2/S1을 천에 묻혀 국소만. "
            "연질/경질 솔 금지(초연질만). 분무 흠뻑·담금통 금지. 구김은 세운 스팀만."
        ),
        "fresh_path_ko": (
            "(1)사진·동의: 100% 비보장, 큰 얼룩은 드라이 우선. (2)아래 흰 천/흡수지. "
            "(3)흰 천 Cap1 바깥→안 블롯. (4)D2 또는 S1 희석액을 천에 1–2방울 → 두드리듯. "
            "(5)찬물 적신 천으로 잔여 흡수. (6)건조 블롯. (7)걸이 보관·구김 시 세운 스팀. "
            "세탁기·통담금·짜기 금지."
        ),
        "dried_path_ko": "마른 얼룩: 담그지 말 것. 국소 1회 재시도 후 안 되면 드라이. 형태·색 변화 가능 고지.",
        "motion_ko": "Cap1 — 블롯·초연질만. 문지르기·연질/경질 솔 금지",
        "water_temp_ko": "국소 찬물만. 통담금·세탁기 금지",
        "aftercare_ko": "걸이 보관. 세운 스팀. 건조기·강하게 누르는 다림질 금지.",
        "sense_check_ko": "눈: 얼룩 옅어짐. 강광: 잔여. 형태: 비틀림·물짐 없음.",
        "success_rate_ko": "신선·국소 즉시: 중간~양호. 마른 후·실크 물짐: 낮음 — 사전 고지.",
        "refuse_when_ko": "큰 얼룩·형태 붕괴·물세탁/100% 요구 → 국소 중단, 드라이 안내·보장 거절.",
        "must_include_ko": "국소만, 통담금·세탁기 금지, Cap1 블롯, 세운 스팀",
        "precheck_vi": (
            "Ca vat lua/poly: anh. Phan loai lua vs poly. "
            "CAM ngam toan bo / may / vat. Vet lon/dat → uu tien dry-clean. Spot cuc bo."
        ),
        "why_vi": (
            "[Tai sao] Ca vat = giu HINH. Wet/ngam = bien dang. "
            "Vet: Cap1 ngoai→trong + khan lot; D2/S1 pha tren khan. "
            "CAM sol mem/cung. CAM xit ngap. Nhao: steamer dung."
        ),
        "fresh_path_vi": (
            "(1)Anh+dong y, uu tien dry neu lon. (2)Lot khan duoi. (3)Tham Cap1. "
            "(4)D2/S1 pha tren khan cham. (5)Tham xa lanh. (6)Tham kho. "
            "(7)Treo; steamer dung. CAM may/ngam/vat."
        ),
        "dried_path_vi": "Vet kho: khong ngam. Spot 1 lan; khong het → dry-clean. Bao form/mau.",
        "motion_vi": "Luc 1 — tham/ultra; CAM cha, CAM sol mem/cung",
        "water_temp_vi": "It nuoc lanh cuc bo. CAM ngam/may",
        "aftercare_vi": "Treo moc. Steamer dung. CAM say/ui ep.",
        "sense_check_vi": "Mat: vet nhe. Anh sang. Form: khong xoan/vet nuoc.",
        "success_rate_vi": "Moi+cuc bo: TB-tot. Kho/lua: thap — bao truoc.",
        "refuse_when_vi": "Vet lon / bat wet 100% → dung spot, huong dry-clean.",
        "must_include_vi": "spot cuc bo, CAM may/ngam, Cap1, steamer dung",
        "precheck_en": (
            "Necktie silk/poly: photo. Read label. No full soak/machine/wring. "
            "Large/expensive stains → dry-clean first. Spot only."
        ),
        "why_en": (
            "[Why] Shape first. Wet soak collapses ties. Cap1 blot out→in + backer cloth; "
            "dilute D2/S1 on cloth only. No soft/hard brush. No flood spray. Standing steam for wrinkles."
        ),
        "fresh_path_en": (
            "(1)Photo + no 100% promise; dry-clean if large. (2)Backer cloth. (3)Cap1 blot. "
            "(4)D2/S1 diluted on cloth, dab. (5)Cold damp rinse blot. (6)Dry blot. "
            "(7)Hang; standing steam. No machine/soak/wring."
        ),
        "dried_path_en": "Dried: no soak. One gentle re-spot; else dry-clean. Disclose shape/color risk.",
        "motion_en": "Cap1 blot/ultra only. No rub; no soft/hard brush.",
        "water_temp_en": "Cold spot only. No soak/machine.",
        "aftercare_en": "Hang. Standing steam. No dryer or heavy press iron.",
        "sense_check_en": "Eyes: lighter stain. Strong light. Shape: no twist/water ring.",
        "success_rate_en": "Fresh local: fair–good. Dried silk rings: low — disclose.",
        "refuse_when_en": "Large stain / wet-wash or 100% demand → stop spot, refer dry-clean.",
        "must_include_en": "spot only, no machine/soak, Cap1 blot, standing steam",
    }


def _ao_dai() -> dict[str, str]:
    return {
        "precheck_ko": (
            "아오자이: 필수 — 실크 vs 폴리(VN 라벨 오류 많음). "
            "실크=S1. 폴리=중성 약. 사진. 불확실하면 물세탁 거절·드라이."
        ),
        "why_ko": (
            "[왜 이 순서] 아오자이=최대 존중. 손세탁만. 세탁기·짜기·건조기 금지. "
            "Cap1. 그늘 평건. 실크는 물짐·이염 고지."
        ),
        "fresh_path_ko": (
            "(1)원단 확정(실크/폴리). (2)찬물 ≤30℃ + 실크는 S1, 폴리는 중성 약. "
            "(3)눌러 헹굼 — 문지르기·짜기 금지. (4)3회 헹굼. (5)그늘 평건. "
            "(6)안감쪽 ~110℃ 다리미·받침천; 실크는 스팀 금지 또는 최소."
        ),
        "dried_path_ko": "얼룩: 안감쪽 초약 스포팅. 실크+물=물짐 가능 고지. 안 되면 전문 이관.",
        "motion_ko": "Cap1 — baby face, 문지르기 금지",
        "water_temp_ko": "찬물 / ≤30℃. 손세탁만",
        "aftercare_ko": "건조기·직사광 금지. 안감 다리미. 어깨 패드 걸이.",
        "sense_check_ko": "눈: 물짐·이염. 손: 비틀림 없음. 강광: 잔여.",
        "success_rate_ko": "폴리 손세탁: 양호. 실크: 중간 — 사전 고지.",
        "refuse_when_ko": "원단 불명·고가 실크 기계 요구 → 거절.",
        "must_include_ko": "실크/폴리 구분, 손세탁만, Cap1, 평건",
        "precheck_vi": (
            "Ao dai: BAT BUOC lua vs polyester (nhan VN thuong SAI). "
            "Silk=S1. Poly=trung tinh nhe. Anh. Khong chac → tu choi wet."
        ),
        "why_vi": (
            "[Tai sao] Ao dai = ton trong toi da. CHI tay. CAM may/vat/say. Luc 1. Phoi bong mat phang."
        ),
        "fresh_path_vi": (
            "(1)Xac nhan vai. (2)Tay lanh + S1 (lua) / nhe (poly). "
            "(3)Ep — CAM cha/vat. (4)Xa 3 lan. (5)Phoi phang bong mat. "
            "(6)Ui mat trai ~110C + lot; lua tat/it hoi."
        ),
        "dried_path_vi": "Vet: spot sieu nhe mat trai. Lua+nuoc → bao vet nuoc. Khong het → chuyen.",
        "motion_vi": "Luc 1 — baby face, khong cha",
        "water_temp_vi": "Lanh / <=30C. CHI tay",
        "aftercare_vi": "CAM say/nang gay. Ui mat trai. Treo moc dem vai.",
        "sense_check_vi": "Mat: vet nuoc/lo mau. Tay: khong xoan.",
        "success_rate_vi": "Poly: tot. Lua: TB — bao truoc.",
        "refuse_when_vi": "Khong ro vai / bat may lua dat → tu choi.",
        "must_include_vi": "phan loai lua/poly, CHI tay, Cap1, phoi phang",
        "precheck_en": (
            "Áo dài: must classify silk vs poly (VN labels often wrong). "
            "Silk=S1. Poly=mild neutral. Photo. Unsure → refuse wet wash."
        ),
        "why_en": (
            "[Why] Maximum care. Hand wash only. No machine/wring/dryer. Cap1. Shade flat dry. Disclose silk water rings."
        ),
        "fresh_path_en": (
            "(1)Confirm fabric. (2)Cold ≤30°C + S1 (silk) / mild (poly). "
            "(3)Press-rinse — no rub/wring. (4)Rinse ×3. (5)Shade flat. "
            "(6)Iron reverse ~110°C with cloth; silk: no/minimal steam."
        ),
        "dried_path_en": "Stains: ultra-light reverse spot. Silk+water ring risk — disclose. Else refer.",
        "motion_en": "Cap1 — baby face, no rub.",
        "water_temp_en": "Cold / ≤30°C. Hand only.",
        "aftercare_en": "No dryer/harsh sun. Reverse iron. Padded hanger.",
        "sense_check_en": "Eyes: rings/bleed. Hand: no twist.",
        "success_rate_en": "Poly hand: good. Silk: fair — disclose.",
        "refuse_when_en": "Unknown fabric / forced machine on silk → refuse.",
        "must_include_en": "silk vs poly, hand only, Cap1, flat dry",
    }


def _hanbok() -> dict[str, str]:
    return {
        "precheck_ko": (
            "한복: 원단 분류(본견/실크·모시·면·폴리). 천연염 이염 쉬움. "
            "깃·고름·소매 색 다르면 이염 위험. 사진·고객 동의."
        ),
        "why_ko": (
            "[왜 이 순서] 고급 한복=전문 드라이 우선. 기계=봉제·형태 손상. "
            "표백 금지. 실크=최소 수분·Cap1. 깃/고름 이염 주의."
        ),
        "fresh_path_ko": (
            "(1)실크·천연염·고가면 드라이 우선. "
            "(2)폴리/면이고 라벨 허용 시: 찬물 중성 손세탁, 문지르기 금지, 충분히 헹굼, 그늘 평건. "
            "(3)국소: 블롯만, 원형 문지르기 금지."
        ),
        "dried_path_ko": "실크 음식물: 물 과다 금지(물짐) — 블롯 후 빠른 이관. 안 되면 고지.",
        "motion_ko": "Cap1 — 기계 금지",
        "water_temp_ko": "찬물. 드라이 우선",
        "aftercare_ko": "완전 건조 후 보관. 통풍·습기·곰팡이 주의. 건조기 금지.",
        "sense_check_ko": "눈: 이염·물짐. 손: 봉제 손상 없음.",
        "success_rate_ko": "드라이: 양호. 가정 물세탁 실크: 낮음.",
        "refuse_when_ko": "실크/천연염 기계·표백 요구 → 거절.",
        "must_include_ko": "드라이 우선, 표백 금지, Cap1, 이염 고지",
        "precheck_vi": (
            "Hanbok: phan loai bon gyeon/silk, moshi, cotton, poly. "
            "Nhuan mau tu nhien de phai. Git/goreum mau khac → lem. Anh+dong y."
        ),
        "why_vi": (
            "[Tai sao] Hanbok cao cap: uu tien dry-clean. May = hong may/form. "
            "CAM bleach. Lua: it nuoc, luc 1. Git/goreum de lem."
        ),
        "fresh_path_vi": (
            "(1)Uu tien dry neu silk/nhuan mau/do dat. "
            "(2)Poly/cotton nhan cho: tay lanh trung tinh, CAM cha, xa ky, phoi phang. "
            "(3)Spot: tham, khong lau vong."
        ),
        "dried_path_vi": "Vet an tren silk: tranh nuoc — tham + chuyen nhanh.",
        "motion_vi": "Luc 1 — khong may",
        "water_temp_vi": "Lanh. Uu tien dry-clean",
        "aftercare_vi": "Kho het roi cat. Thoang, tranh moc. CAM say.",
        "sense_check_vi": "Mat: lo mau/vet nuoc. Tay: may khong rot.",
        "success_rate_vi": "Dry: tot. Wet silk: thap.",
        "refuse_when_vi": "Bat may/tay bleach silk → tu choi.",
        "must_include_vi": "uu tien dry, CAM bleach, Cap1, bao lem mau",
        "precheck_en": (
            "Hanbok: classify silk/moshi/cotton/poly. Natural dyes bleed easily. "
            "Collar/goreum color mismatch → transfer risk. Photo + consent."
        ),
        "why_en": (
            "[Why] Premium hanbok → specialty dry-clean first. Machine wrecks seams/shape. "
            "No bleach. Silk: minimal water, Cap1. Collar/goreum bleed risk."
        ),
        "fresh_path_en": (
            "(1)Silk/natural dye/expensive → dry-clean first. "
            "(2)If poly/cotton label allows: cold mild hand wash, no rub, rinse well, shade flat. "
            "(3)Spot: blot only, no circular wipe."
        ),
        "dried_path_en": "Food on silk: avoid flood water (rings) — blot + refer fast.",
        "motion_en": "Cap1 — no machine.",
        "water_temp_en": "Cold. Prefer dry-clean.",
        "aftercare_en": "Store fully dry. Airflow vs mold. No dryer.",
        "sense_check_en": "Eyes: bleed/rings. Hand: seams intact.",
        "success_rate_en": "Dry-clean: good. Home wet silk: low.",
        "refuse_when_en": "Forced machine/bleach on silk dye → refuse.",
        "must_include_en": "dry-clean first, no bleach, Cap1, disclose bleed",
    }


def _odor_smoke() -> dict[str, str]:
    return {
        "precheck_ko": "담배·연기 냄새: 사진. 분리 세탁. 냄새는 젖었을 때 코로 재확인.",
        "why_ko": (
            "[왜 이 순서] 니코틴·타르는 섬유에 흡착. "
            "A3 1:4 → N1 흡착 → 안전 최고온 세탁 → 햇볕·통풍. 향수로 가리지 말 것."
        ),
        "fresh_path_ko": (
            "(1)A3(식초 5%) 1:4 담금 30–60분. (2)N1(베이킹소다) 뿌려 1–2시간. "
            "(3)원단 허용 최고온 D2/D3 세탁. (4)햇볕·바람 ≥4시간. "
            "(5)젖은 상태 냄새 남으면 반복. 섬유유연제·향수로 덮기 금지."
        ),
        "dried_path_ko": "반복 A3+N1. 쿠션·카펫: 국소+N1 하룻밤.",
        "motion_ko": "Cap0 담금; N1 Cap1",
        "water_temp_ko": "원단 허용 최고온 우선",
        "aftercare_ko": "젖은 상태 코 점검. 유연제·향수로 가리기 금지.",
        "sense_check_ko": "코(젖은 상태): 연기 잔향 없음.",
        "success_rate_ko": "조기·반복: 양호. 오래된 심취: 중간 — 고지.",
        "refuse_when_ko": "향수만으로 해결 요구 → 거절, 위 경로 고지.",
        "must_include_ko": "A3→N1→세탁→통풍, 향수 가림 금지, 젖은 상태 점검",
        "precheck_vi": "Mui thuoc/khoi: anh. Tach do. Kiem MUI khi uot.",
        "why_vi": (
            "[Tai sao] Nicotine+tar bam soi. A3 1:4 → N1 → giat nhiet an toan → nang+gio. "
            "CAM che bang nuoc hoa/xa vai."
        ),
        "fresh_path_vi": (
            "(1)A3 1:4 ngam 30-60 phut. (2)N1 1-2h. (3)Giat D2/D3 nhiet cao nhat an toan. "
            "(4)Nang+gio >=4h. (5)Mui khi uot con → lap. CAM xa vai/nuoc hoa che."
        ),
        "dried_path_vi": "Lap A3+N1. Nem/tham: spot + N1 qua dem.",
        "motion_vi": "Luc 0 ngam; N1 Cap1",
        "water_temp_vi": "Theo vai; uu tien nhiet cao an toan",
        "aftercare_vi": "Kiem mui khi UOT. CAM che bang xa/nuoc hoa.",
        "sense_check_vi": "Mui khi uot: het khoi.",
        "success_rate_vi": "Som+lap: tot. Cu sau: TB — bao.",
        "refuse_when_vi": "Chi xit nuoc hoa → tu choi, lam dung quy trinh.",
        "must_include_vi": "A3→N1→giat→gio, CAM che mui, kiem khi uot",
        "precheck_en": "Smoke odor: photo. Separate load. Recheck smell when wet.",
        "why_en": (
            "[Why] Nicotine/tar bind fibers. A3 1:4 → N1 absorb → hottest safe wash → sun+air. "
            "Do not mask with perfume/softener."
        ),
        "fresh_path_en": (
            "(1)A3 vinegar 1:4 soak 30–60 min. (2)N1 baking soda 1–2 h. "
            "(3)Wash D2/D3 at hottest safe temp. (4)Sun+air ≥4 h. "
            "(5)If wet smell remains → repeat. No perfume cover-up."
        ),
        "dried_path_en": "Repeat A3+N1. Cushions: spot + overnight N1.",
        "motion_en": "Cap0 soak; N1 Cap1.",
        "water_temp_en": "Hottest safe for fabric.",
        "aftercare_en": "Smell-check wet. No softener/perfume mask.",
        "sense_check_en": "Nose when wet: no smoke.",
        "success_rate_en": "Early+repeat: good. Old heavy: fair — disclose.",
        "refuse_when_en": "Perfume-only demand → refuse; follow path.",
        "must_include_en": "A3→N1→wash→air, no perfume mask, wet smell check",
    }


def _uniform() -> dict[str, str]:
    return {
        "precheck_ko": "유니폼·근무복·교복: 라벨·혼용률·명찰·견장. 이염·기름·땀(목·겨드랑이) 확인.",
        "why_ko": (
            "[왜 이 순서] 폴리·혼방 많음. 라벨 수온 준수, 장식은 세탁망. "
            "목·겨드랑이 황변: 효소→산소(흰만). 유색 강한 염소 표백 금지."
        ),
        "fresh_path_ko": (
            "(1)라벨·장식 확인. (2)목/겨드랑이 전처리. (3)라벨 온도 기계+세탁망. "
            "(4)유색: 산소표백만 신중(흰만 B2 가능 시). (5)건조 전 강광."
        ),
        "dried_path_ko": "황변 고착: 셔츠 황변 SOP 연계, 100% 비보장.",
        "motion_ko": "Cap2 전처리; 기계는 라벨",
        "water_temp_ko": "라벨 수온. 불확실하면 ≤40℃",
        "aftercare_ko": "명찰·주름 확인. 건조 전 강광.",
        "sense_check_ko": "눈: 황변·이염. 손: 장식 손상 없음.",
        "success_rate_ko": "일반 혼방: 양호. 특수 방화/고기능: 매뉴얼 우선.",
        "refuse_when_ko": "특수 방화·고기능 유니폼 임의 표백 → 거절·매뉴얼.",
        "must_include_ko": "라벨 수온, 세탁망, 목·겨드랑이 전처리, 유색 락스 금지",
        "precheck_vi": "Dong phuc: nhan + phu kien. Vet mo hoi/co/dau.",
        "why_vi": (
            "[Tai sao] Poly/hon — theo nhan, tui luoi, pretreat co/nach. "
            "Mau: than B1. CAM Javel mau."
        ),
        "fresh_path_vi": (
            "(1)Nhan+phu kien. (2)Pretreat co/nach. (3)May theo nhan + tui. "
            "(4)Mau: than B1. (5)Anh sang truoc say."
        ),
        "dried_path_vi": "Vang khoa: SOP vang ao, bao 100%.",
        "motion_vi": "Cap2 pretreat; may theo nhan",
        "water_temp_vi": "Theo nhan; neu khong chac <=40C",
        "aftercare_vi": "Kiem phu kien. Anh sang.",
        "sense_check_vi": "Mat: vang/lo mau. Tay: phu kien.",
        "success_rate_vi": "Hon thuong: tot. Vai dac biet: manual.",
        "refuse_when_vi": "Do dac thu bat tay manh → tu choi.",
        "must_include_vi": "theo nhan, tui luoi, pretreat co/nach, CAM Javel mau",
        "precheck_en": "Uniform/workwear: label, blend, badges. Check dye bleed, oil, collar/armpit.",
        "why_en": (
            "[Why] Often poly blends. Follow label temp; mesh bag for badges. "
            "Collar/armpit yellow: enzyme→oxygen (whites). No chlorine on colors."
        ),
        "fresh_path_en": (
            "(1)Label + trim. (2)Pretreat collar/armpit. (3)Machine per label + mesh. "
            "(4)Colors: careful oxygen only. (5)Strong light before dry."
        ),
        "dried_path_en": "Set yellowing: shirt-yellow SOP; no 100% promise.",
        "motion_en": "Cap2 pretreat; machine per label.",
        "water_temp_en": "Label temp; if unsure ≤40°C.",
        "aftercare_en": "Check badges/creases. Strong light before dry.",
        "sense_check_en": "Eyes: yellow/bleed. Hand: trim intact.",
        "success_rate_en": "Common blends: good. Specialty FR gear: manual first.",
        "refuse_when_en": "Forced bleach on specialty FR/tech gear → refuse.",
        "must_include_en": "label temp, mesh bag, collar pretreat, no chlorine on colors",
    }


def apply_cultural_specialty_hints(graph: dict[str, Any], item_id: str) -> dict[str, Any]:
    if item_id not in CULTURAL_SPECIALTY_IDS:
        return graph
    out = dict(graph)
    tools = list(out.get("tools") or [])
    if not any(str(t.get("id")) == "T_CLOTH" for t in tools):
        tools.append({
            "id": "T_CLOTH",
            "name_ko": "흰 천·흡수지",
            "name_vi": "Khan trang",
            "name_en": "White cloth",
            "use_for_ko": "국소 블롯·받침.",
            "use_for_vi": "Tham/lot cuc bo.",
            "use_for_en": "Spot blot / backer.",
        })
    if item_id == "I_UNIFORM" and not any(str(t.get("id")) == "T_MESH_BAG" for t in tools):
        tools.append({
            "id": "T_MESH_BAG",
            "name_ko": "세탁망",
            "name_vi": "Tui luoi",
            "name_en": "Mesh laundry bag",
            "use_for_ko": "명찰·장식 보호.",
            "use_for_vi": "Bao ve phu kien.",
            "use_for_en": "Protect badges/trim.",
        })
    out["tools"] = tools
    if item_id == "I_ODOR_SMOKE":
        out["chemicals"] = [
            {
                "code": "A3",
                "name_ko": "식초 5%(A3)",
                "name_vi": "Giam trang 5%",
                "name_en": "White vinegar 5%",
                "dilution_ko": "1:4 담금 30–60분.",
                "dilution_vi": "1:4 ngam 30-60 phut.",
                "dilution_en": "1:4 soak 30–60 min.",
            },
            {
                "code": "N1",
                "name_ko": "베이킹소다(N1)",
                "name_vi": "Baking soda",
                "name_en": "Baking soda",
                "dilution_ko": "뿌려 1–2시간 흡착.",
                "dilution_vi": "Rac 1-2h.",
                "dilution_en": "Dust 1–2 h absorb.",
            },
        ]
        out["empty_chems_ok"] = False
    elif item_id in {"I_NECKTIE", "I_AO_DAI", "I_HANBOK"}:
        out.setdefault("empty_chems_ok", True)
    return out
