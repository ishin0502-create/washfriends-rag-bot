# -*- coding: utf-8 -*-
"""Specialty garment care for formerly GraphRAG-only items.

Full KO / VI / EN — sanitize picks one lang. Truth from main.py Item seeds +
kb/laundry_kb_v3_items_clothing.md / items_home.md. No invented chemistry.
"""
from __future__ import annotations

from typing import Any

GARMENT_SPECIALTY_IDS = frozenset({
    "I_CURTAIN_FABRIC",
    "I_CURTAIN_URETHANE",
    "I_DENIM",
    "I_GORETEX",
    "I_BABY_WEAR",
    "I_SWIMWEAR",
    "I_GOLF_WEAR",
    "I_GOLF_SHOE",
    "I_HIKING_SHOE",
    "I_RUNNING_MESH",
})


def education_for_garment(item_id: str) -> dict[str, str]:
    return {
        "I_CURTAIN_FABRIC": _curtain_fabric,
        "I_CURTAIN_URETHANE": _curtain_urethane,
        "I_DENIM": _denim,
        "I_GORETEX": _goretex,
        "I_BABY_WEAR": _baby_wear,
        "I_SWIMWEAR": _swimwear,
        "I_GOLF_WEAR": _golf_wear,
        "I_GOLF_SHOE": _golf_shoe,
        "I_HIKING_SHOE": _hiking_shoe,
        "I_RUNNING_MESH": _running_mesh,
    }.get(item_id, lambda: {})()


def _curtain_fabric() -> dict[str, str]:
    return {
        "precheck_ko": (
            "일반 패브릭 커튼: 세탁 전 가로·세로 치수 기록(면 3–5%·린넨 5–8% 수축 고지). "
            "고리·핀 제거. 흰/유색 분리. 곰팡이면 S_MILDEW+PPE. "
            "암막 코팅 라벨에 드라이만이면 물세탁 거절."
        ),
        "why_ko": (
            "[왜 이 순서] 커튼=수축·곰팡이(VN 습도). 섬세 ~30℃·세제 소량·탈수 약. "
            "축축할 때 바로 봉에 걸어 무게로 펴기. 유색 락스 금지."
        ),
        "fresh_path_ko": (
            "(1)치수·사진. (2)먼지 흡입·털기. (3)얼룩 국소. "
            "(4)망/섬세 ~30℃ 중성·소량(또는 손세탁). (5)탈수 약. "
            "(6)축축한 채 봉에 걸어 형태. VN: 4시간 내 건조 시작. "
            "(7)수축·곰팡이 가능 고지."
        ),
        "dried_path_ko": "곰팡이: PPE + S_MILDEW. 수축: 사전 고지. 필요 시 약하게 다림질(촉촉할 때).",
        "motion_ko": "Cap1–2. 얇은 커튼 세게 문지르기 금지.",
        "water_temp_ko": "~30℃. 라벨 허용 면은 최대 ~40℃.",
        "aftercare_ko": "곧게 걸기. 곰팡이 주기 점검. AC 직풍으로 결로 주의.",
        "sense_check_ko": "눈: 곰팡이·잔여. 손: 완전 건조. 치수: 수축 여부.",
        "success_rate_ko": "일반 패브릭: 양호. 암막·코팅 오인: 손상 위험.",
        "refuse_when_ko": "라벨 드라이 전용·이미 심한 곰팡이·100% 치수 복원 → 거절/고지.",
        "must_include_ko": "치수 기록, ~30℃, 축축할 때 걸기, 유색 락스 금지",
        "precheck_vi": (
            "Rem vai: do size TRUOC (cotton 3-5%, linen 5-8%). Thao moc. Tach mau. "
            "Moc → S_MILDEW+PPE. Blackout dry-only → tu choi wet."
        ),
        "why_vi": (
            "[Tai sao] Rem = rut + moc. Tinh te ~30C, bot it, vat nhe. "
            "Treo UOT de trong. CAM Javel mau."
        ),
        "fresh_path_vi": (
            "(1)Do size+anh. (2)Hut/chai. (3)Spot. (4)Tui luoi/~30C bot nhe. "
            "(5)Vat nhe. (6)Treo am len thanh. VN: kho <4h. (7)Bao rut/moc."
        ),
        "dried_path_vi": "Moc: PPE+S_MILDEW. Rut: da bao. Ui nhe khi am neu can.",
        "motion_vi": "Cap1-2 — khong cha rem mong.",
        "water_temp_vi": "~30C; cotton max ~40C neu nhan cho.",
        "aftercare_vi": "Treo thang. Kiem moc. Tranh AC thoi thang rem.",
        "sense_check_vi": "Mat: moc/du. Tay: kho. Size: co rut.",
        "success_rate_vi": "Rem vai: tot. Nham blackout: rui ro.",
        "refuse_when_vi": "Dry-only / moc nang / doi size 100% → tu choi.",
        "must_include_vi": "do size, ~30C, treo am, CAM Javel mau",
        "precheck_en": (
            "Fabric curtain: measure before wash (cotton ~3–5%, linen ~5–8% shrink). "
            "Remove hooks. Sort colors. Mold → S_MILDEW+PPE. "
            "Blackout dry-clean-only → refuse wet wash."
        ),
        "why_en": (
            "[Why] Curtains shrink and mold in humidity. Gentle ~30°C, little detergent, "
            "short spin. Hang damp on rod to straighten. No chlorine on colors."
        ),
        "fresh_path_en": (
            "(1)Measure+photo. (2)Vacuum/brush dust. (3)Spot stains. "
            "(4)Mesh bag/delicate ~30°C mild soap (or hand). (5)Short spin. "
            "(6)Hang damp on rod. Start drying <4h in humid climates. "
            "(7)Disclose shrink/mold risk."
        ),
        "dried_path_en": "Mold: PPE + mildew SOP. Shrink: already disclosed. Light iron while damp if needed.",
        "motion_en": "Cap1–2. Do not scrub sheer fabric hard.",
        "water_temp_en": "~30°C; cotton up to ~40°C if label allows.",
        "aftercare_en": "Hang straight. Check mold periodically. Avoid AC blast causing condensation.",
        "sense_check_en": "Eyes: mold/residue. Hand: dry. Size: shrink check.",
        "success_rate_en": "Plain fabric: good. Misidentified blackout: damage risk.",
        "refuse_when_en": "Dry-clean-only label / heavy mold / demand 100% size restore → refuse.",
        "must_include_en": "measure first, ~30°C, hang damp, no chlorine on colors",
    }


def _curtain_urethane() -> dict[str, str]:
    return {
        "precheck_ko": (
            "우레탄·비닐·PU 코팅/샤워커튼: (A)PU코팅 (B)비닐/PVC/PEVA (C)일반 패브릭과 구분. "
            "사진. 많은 제품은 세탁기 금지 — 국소 닦기 우선."
        ),
        "why_ko": (
            "[왜 이 순서] 코팅=기계·장담금·강용제·아세톤에 박리. "
            "중성+미온 천·연질 솔 국소. 라벨 허용 시에만 섬세≤40℃·유연제·건조기 금지."
        ),
        "fresh_path_ko": (
            "(1)재질 확정. (2)중성(D2/S1) 희석+미온으로 표면 닦기. "
            "(3)곰팡이: A3 1:4+PPE → 헹굼 → 통풍 건조(고온건조 금지). "
            "(4)라벨 허용 기계만: 섬세 찬물~≤40℃·세제 소량·탈수 약+균형용 수건. "
            "(5)걸어서 건조 — 건조기·다리미 금지. (6)박리면 교체/고지."
        ),
        "dried_path_ko": "장담금 금지. 곰팡이 남으면 A3/PPE 반복. 비닐 경화·균열 시 2–3년 교체 안내.",
        "motion_ko": "Cap1–2 닦기. 코팅 세게 문지르기 금지.",
        "water_temp_ko": "미온 국소. 기계(허용 시) ≤40℃.",
        "aftercare_ko": "통풍 걸기. 샤워 후 펼쳐 건조. 고온·다림질 금지.",
        "sense_check_ko": "눈: 박리·곰팡이. 손: 끈적(세제 잔여) 없음.",
        "success_rate_ko": "국소: 양호. 이미 박리·세탁기 후: 낮음.",
        "refuse_when_ko": "세탁기·건조기·아세톤 강요, 박리 진행 → 거절.",
        "must_include_ko": "코팅 구분, 국소 중성, 기계·건조기·아세톤 주의",
        "precheck_vi": "Rem PU/vinyl/PEVA vs rem vai. Anh. Nhieu hang CAM may — uu tien lau.",
        "why_vi": "[Tai sao] Lop phu: may/ngam/A2 = boc. D2/S1 am + sol mem. May chi khi nhan cho: <=40C, CAM xa vai/say.",
        "fresh_path_vi": (
            "(1)Nhan chat lieu. (2)Lau D2/S1 am. (3)Moc: A3 1:4+PPE, xa, kho thoang. "
            "(4)May neu cho: tinh te <=40C, it bot, vat nhe. (5)Treo — CAM dryer. (6)Boc → thay/bao."
        ),
        "dried_path_vi": "Khong ngam dai. Moc: lap A3. Vinyl gia: thay 2-3 nam neu nut.",
        "motion_vi": "Cap1-2 lau — khong cha cot.",
        "water_temp_vi": "Am; may (neu cho) <=40C.",
        "aftercare_vi": "Treo thoang. Mo rem sau tam. CAM ui/say nong.",
        "sense_check_vi": "Mat: boc/moc. Tay: het tron bot.",
        "success_rate_vi": "Lau: tot. Da boc/may: thap.",
        "refuse_when_vi": "Bat may/say/A2 / da boc → tu choi.",
        "must_include_vi": "phan loai phu, lau trung tinh, CAM may/say/A2 khi khong an toan",
        "precheck_en": "PU/vinyl/PEVA coated vs fabric curtain. Photo. Many labels forbid machine — wipe first.",
        "why_en": "[Why] Coating peels with machine soak, acetone, harsh solvent. Mild soap + lukewarm wipe. Machine only if labeled: ≤40°C, no softener/dryer.",
        "fresh_path_en": (
            "(1)Confirm material. (2)Wipe D2/S1 diluted lukewarm. "
            "(3)Mold: A3 1:4+PPE, rinse, air-dry — no hot dryer. "
            "(4)Machine only if label: delicate ≤40°C, little detergent, short spin + balance towels. "
            "(5)Hang dry — no dryer/iron. (6)Peeling → replace/disclose."
        ),
        "dried_path_en": "No long soak. Re-treat mold with A3/PPE. Aged vinyl: replace every 2–3 years if cracked.",
        "motion_en": "Cap1–2 wipe. Do not scrub coating hard.",
        "water_temp_en": "Lukewarm spot; machine (if allowed) ≤40°C.",
        "aftercare_en": "Hang airy. Open after shower. No hot iron/dryer.",
        "sense_check_en": "Eyes: peel/mold. Hand: no detergent slip.",
        "success_rate_en": "Wipe: good. Already peeled/machine-washed: low.",
        "refuse_when_en": "Forced machine/dryer/acetone or active peeling → refuse.",
        "must_include_en": "identify coating, mild wipe, caution machine/dryer/acetone",
    }


def _denim() -> dict[str, str]:
    return {
        "precheck_ko": (
            "데님: 첫 세탁 물빠짐=정상. 흰옷과 같이 금지 — 단독/유사 색. "
            "뒤집기. 고객이 색바램 클레임하면 사진·착용·UV 설명."
        ),
        "why_ko": (
            "[왜 이 순서] 인디고 보호=뒤집기+찬물/~30℃+세제 소량. "
            "직사광선·잦은 건조기=빠른 탈색. 세월 바랜 무늬=특성(세탁 과실로 단정 금지)."
        ),
        "fresh_path_ko": (
            "(1)뒤집기. (2)찬물/~30℃·세제 소량. (3)첫 2–3회 단독 또는 유사 색. "
            "(4)건조기 최소화(수축). (5)그늘 통풍. (6)얼룩은 국소·염소 금지. "
            "(7)대사: 「첫 세탁 물빠짐·세월 바램은 데님 특성입니다」."
        ),
        "dried_path_ko": "마른 얼룩: 국소+약한 세탁. 탈색 복원 100% 금지(에탄올+오일+건조기 꼼수 금지).",
        "motion_ko": "Cap2–3 연질/경질 국소만.",
        "water_temp_ko": "찬물/~30℃.",
        "aftercare_ko": "그늘. 흰옷과 분리. 물빠짐 사전 고지.",
        "sense_check_ko": "눈: 이염 위험 분리. 손: 잔여 세제.",
        "success_rate_ko": "색 유지: 양호. 이미 UV 바램: 복원 낮음.",
        "refuse_when_ko": "흰옷과 강제 혼합·100% 새색 복원 → 거절.",
        "must_include_ko": "뒤집기, 찬물, 흰옷 분리, 첫 물빠짐 정상",
        "precheck_vi": "Denim: lan dau ra mau = binh thuong. RIENG / mau tuong tu — CAM chung trang. Lat trai.",
        "why_vi": "[Tai sao] Bao mau: lat trai + lanh/~30C + bot it. Nang/say = phai nhanh. Van bac = dac trung.",
        "fresh_path_vi": (
            "(1)Lat trai. (2)Lanh/~30C bot it. (3)2-3 lan dau rieng. "
            "(4)Han che say. (5)Phoi bong mat. (6)Spot nhe, CAM Javel. (7)Bao ra mau lan dau."
        ),
        "dried_path_vi": "Vet kho: spot+giat nhe. Phai mau: giai thich / nhuom — CAM meo con+dau+say.",
        "motion_vi": "Cap2-3 spot.",
        "water_temp_vi": "Lanh / ~30C.",
        "aftercare_vi": "Phoi bong mat. CAM giat chung trang.",
        "sense_check_vi": "Mat: tach trang. Tay: het bot.",
        "success_rate_vi": "Giu mau: tot. Da bac UV: thap.",
        "refuse_when_vi": "Bat giat chung trang / doi mau moi 100% → tu choi.",
        "must_include_vi": "lat trai, nuoc lanh, tach trang, ra mau lan dau OK",
        "precheck_en": "Denim: first-wash bleed is normal. Wash alone/similar colors — never with whites. Inside out. Photo if fade claim.",
        "why_en": "[Why] Protect indigo: inside out + cold/~30°C + little detergent. Sun/dryer accelerates fade. Wear/UV whiskers are characteristic — not automatic shop fault.",
        "fresh_path_en": (
            "(1)Inside out. (2)Cold/~30°C little detergent. (3)First 2–3 washes alone. "
            "(4)Minimize dryer (shrink). (5)Shade dry. (6)Spot stains; no chlorine. "
            "(7)Script: first bleed and age fade are normal denim traits."
        ),
        "dried_path_en": "Dried stains: spot + gentle wash. Do not promise 100% recolor (no ethanol+oil+dryer hacks).",
        "motion_en": "Cap2–3 soft/hard brush on spots only.",
        "water_temp_en": "Cold / ~30°C.",
        "aftercare_en": "Shade dry. Keep separate from whites. Disclose bleed risk.",
        "sense_check_en": "Eyes: no white-load mix. Hand: no detergent residue.",
        "success_rate_en": "Color retention: good. Already UV-faded: restore low.",
        "refuse_when_en": "Forced wash with whites / demand brand-new color → refuse.",
        "must_include_en": "inside out, cold water, separate from whites, first bleed normal",
    }


def _goretex() -> dict[str, str]:
    return {
        "precheck_ko": "고어텍스·DWR 기능성: 라벨 확인. 세제 과다·유연제=방수 저하.",
        "why_ko": (
            "[왜 이 순서] 멤브레인·DWR은 잔여 세제·유연제에 약함. "
            "저온·소량·추가 헹굼. 저온 건조가 DWR 재활성화에 도움(기종 허용 시)."
        ),
        "fresh_path_ko": (
            "(1)주머니 비우기·지퍼. (2)섬세 ~30℃·세제 소량(강세제·유연제 금지). "
            "(3)추가 헹굼 1회. (4)저온 건조 짧게(DWR 재활성, 허용 시) 또는 그늘. "
            "(5)방수 약하면 깨끗이 헹군 뒤 DWR 재스프레이(~10회 세탁 후)."
        ),
        "dried_path_ko": "방수 저하: 잔여 제거 → 저온 건조 ~10분 → DWR 재도포. 100% 신품 방수 비보장.",
        "motion_ko": "Cap2 섬세/손세탁 약하게.",
        "water_temp_ko": "~30℃. 건조 저온.",
        "aftercare_ko": "방수 테스트. DWR 재도포 안내. 세제 과다 금지.",
        "sense_check_ko": "물방울이 맺히는지. 손: 세제 잔여 없음.",
        "success_rate_ko": "올바른 세제·헹굼: 양호. 유연제 남용 후: 중간↓.",
        "refuse_when_ko": "유연제·강세제 강제, 고온건조 강제 → 거절.",
        "must_include_ko": "세제 소량, 유연제 금지, 추가 헹굼, DWR",
        "precheck_vi": "Gore-Tex/DWR: doc nhan. Bot nhieu / xa vai = mat chong tham.",
        "why_vi": "[Tai sao] Mang+DWR yeu bot du/xa vai. 30C, bot it, xa them. Say thap tai DWR neu cho.",
        "fresh_path_vi": (
            "(1)Tui+keo. (2)~30C tinh te bot it — CAM xa vai. (3)Xa them. "
            "(4)Say thap ngan neu cho / phoi. (5)Mat chong tham: xa sach → say thap → xit DWR."
        ),
        "dried_path_vi": "Mat DWR: xa du → say ~10 phut → xit lai. Khong 100% moi.",
        "motion_vi": "Cap2 tinh te.",
        "water_temp_vi": "~30C; say thap.",
        "aftercare_vi": "Kiem chong tham. Xit DWR. Tranh bot dam.",
        "sense_check_vi": "Giot nuoc don. Tay: het bot.",
        "success_rate_vi": "Dung quy trinh: tot. Nhieu softener: thap.",
        "refuse_when_vi": "Bat xa vai / say nong → tu choi.",
        "must_include_vi": "bot it, CAM xa vai, xa them, DWR",
        "precheck_en": "Gore-Tex/DWR: check label. Excess detergent/softener kills water repellency.",
        "why_en": "[Why] Membrane/DWR hate detergent residue and softener. Cool wash, little soap, extra rinse. Low dryer heat can reactivate DWR when allowed.",
        "fresh_path_en": (
            "(1)Empty pockets/zips. (2)Delicate ~30°C little detergent — no softener. "
            "(3)Extra rinse. (4)Short low dryer heat if allowed, or shade. "
            "(5)If wet-out: rinse clean → low heat → reapply DWR (~after 10 washes)."
        ),
        "dried_path_en": "Lost DWR: clear residue → ~10 min low heat → respray. Not 100% like new.",
        "motion_en": "Cap2 delicate/hand gentle.",
        "water_temp_en": "~30°C; low dryer heat.",
        "aftercare_en": "Bead test. Offer DWR respray. Avoid heavy detergent.",
        "sense_check_en": "Water beads. Hand: no residue.",
        "success_rate_en": "Correct process: good. Softener abuse: lower.",
        "refuse_when_en": "Forced softener or hot dryer → refuse.",
        "must_include_en": "little detergent, no softener, extra rinse, DWR",
    }


def _baby_wear() -> dict[str, str]:
    return {
        "precheck_ko": "아기·유아복: 성인 세탁과 분리. 무향·저자극 세제. 분유·대변=찬물 단백질 경로.",
        "why_ko": (
            "[왜 이 순서] 아기 피부=자극 최소. 무향 세제·추가 헹굼. "
            "단백질 얼룩은 찬물 먼저(온수=고착). 위생 시 40–60℃(원단 허용)."
        ),
        "fresh_path_ko": (
            "(1)성인 빨래와 분리. (2)분유·분변: E1 찬물 국소; 소변: A3 약희석. "
            "(3)40–60℃ 베이비 세제(라벨). (4)추가 헹굼 필수. "
            "(5)완전 건조(<4h VN). (6)강한 향 유연제 금지."
        ),
        "dried_path_ko": "냄새: A3+추가 헹굼. 고착 얼룩: S_BABY_FORMULA / S_URINE 경로·고지.",
        "motion_ko": "Cap1–2 국소만.",
        "water_temp_ko": "얼룩: 찬물. 세탁: 40–60℃(원단).",
        "aftercare_ko": "완전 건조. 향 강한 유연제 금지.",
        "sense_check_ko": "코: 세제 냄새 과다 없음. 손: 완전 건조.",
        "success_rate_ko": "즉시 찬물 전처리: 높음. 온수 고착 후: 중간↓.",
        "refuse_when_ko": "성인과 강제 혼합·락스 남용 요구 → 거절.",
        "must_include_ko": "성인 분리, 찬물 단백질, 추가 헹굼, 무향",
        "precheck_vi": "Do be: giat RIENG. Bot khong huong. Sua/phan → cold protein.",
        "why_vi": "[Tai sao] Da be: bot nhe, xa them. Vet protein: LANH truoc. 40-60C ve sinh neu vai cho.",
        "fresh_path_vi": (
            "(1)Tach lo. (2)Sua/phan E1 lanh; nuoc tieu A3. (3)40-60C bot baby. "
            "(4)Xa them. (5)Kho <4h. (6)CAM softener manh muoi."
        ),
        "dried_path_vi": "Mui: A3+xa them. Vet khoa: S_BABY_FORMULA/S_URINE.",
        "motion_vi": "Cap1-2 spot.",
        "water_temp_vi": "Vet: lanh. Giat: 40-60C.",
        "aftercare_vi": "Kho han. It softener.",
        "sense_check_vi": "Mui bot nhe. Tay: kho.",
        "success_rate_vi": "Xu ly lanh som: cao. Da khoa nong: thap.",
        "refuse_when_vi": "Bat giat chung nguoi lon / Javel → tu choi.",
        "must_include_vi": "tach nguoi lon, protein lanh, xa them, khong huong",
        "precheck_en": "Baby wear: wash separate from adult loads. Fragrance-free detergent. Milk/feces → cold protein path.",
        "why_en": "[Why] Baby skin needs mild soap + extra rinse. Protein stains: cold first (heat sets). Hygiene wash 40–60°C if fabric allows.",
        "fresh_path_en": (
            "(1)Separate from adult laundry. (2)Milk/feces: E1 cold spot; urine: light A3. "
            "(3)40–60°C baby detergent per label. (4)Extra rinse required. "
            "(5)Fully dry (<4h humid climates). (6)No strong softener."
        ),
        "dried_path_en": "Odor: A3 + extra rinse. Set stains: baby-formula/urine SOPs + disclose.",
        "motion_en": "Cap1–2 spotting only.",
        "water_temp_en": "Stains: cold. Wash: 40–60°C by fabric.",
        "aftercare_en": "Fully dry. Avoid strong fragrance softener.",
        "sense_check_en": "Nose: no heavy detergent. Hand: fully dry.",
        "success_rate_en": "Cold pretreat soon: high. Heat-set: lower.",
        "refuse_when_en": "Forced mix with adult loads / chlorine abuse → refuse.",
        "must_include_en": "separate from adults, cold protein, extra rinse, fragrance-free",
    }


def _swimwear() -> dict[str, str]:
    return {
        "precheck_ko": "수영복·스판덱스: 수영 직후 찬물 헹굼(염소·소금). 건조기·직사광선 금지.",
        "why_ko": "[왜 이 순서] 염소+열=스판 탄성 손상. 찬물·중성 소량·약하게. 짜지 말고 수건으로 누르기.",
        "fresh_path_ko": (
            "(1)즉시 찬물 5분 헹굼. (2)손세탁 중성 소량 또는 망+섬세 찬물. "
            "(3)수건으로 눌러 물기. (4)그늘 건조. (5)건조기·고온·직사광선 금지."
        ),
        "dried_path_ko": "이미 건조기·강한 햇빛: 탄성 저하 가능 — 100% 복원 불가 고지.",
        "motion_ko": "Cap1. 비틀어 짜기 금지.",
        "water_temp_ko": "찬물만.",
        "aftercare_ko": "그늘. 다림질·고온건조 금지.",
        "sense_check_ko": "손: 탄성. 눈: 변색.",
        "success_rate_ko": "즉시 헹굼: 양호. 열 손상 후: 낮음.",
        "refuse_when_ko": "건조기·고온 강제 → 거절.",
        "must_include_ko": "즉시 찬물 헹굼, 찬물만, 건조기 금지",
        "precheck_vi": "Do boi: xa lanh NGAY sau boi. CAM say/nang gay.",
        "why_vi": "[Tai sao] Clo+nhiet hong spandex. Lanh, D3 it, vo nhe. Ep khan — CAM vat xoan.",
        "fresh_path_vi": "(1)Xa lanh 5 phut. (2)Tay/D3 it hoac tui luoi lanh. (3)Ep khan. (4)Phoi bong mat. (5)CAM dryer.",
        "dried_path_vi": "Da say/nang: bao dan hoi giam — khong 100%.",
        "motion_vi": "Cap1 — khong xoan.",
        "water_temp_vi": "LANH.",
        "aftercare_vi": "Bong mat. CAM ui/say nong.",
        "sense_check_vi": "Tay: dan hoi. Mat: phai mau.",
        "success_rate_vi": "Xa ngay: tot. Da nhiet: thap.",
        "refuse_when_vi": "Bat say nong → tu choi.",
        "must_include_vi": "xa lanh ngay, chi lanh, CAM say",
        "precheck_en": "Swimwear/spandex: rinse cold immediately after swim (chlorine/salt). No dryer/hot sun.",
        "why_en": "[Why] Chlorine + heat kills elastane. Cold, little mild soap, gentle. Press in towel — do not wring.",
        "fresh_path_en": (
            "(1)Cold rinse 5 minutes immediately. (2)Hand wash little mild soap or mesh bag cold delicate. "
            "(3)Press in towel. (4)Shade dry. (5)No dryer, high heat, or harsh sun."
        ),
        "dried_path_en": "Already dryer/harsh sun: elasticity loss possible — no 100% restore.",
        "motion_en": "Cap1. Do not twist-wring.",
        "water_temp_en": "Cold only.",
        "aftercare_en": "Shade. No iron/hot dryer.",
        "sense_check_en": "Hand: stretch recovery. Eyes: discoloration.",
        "success_rate_en": "Immediate rinse: good. After heat damage: low.",
        "refuse_when_en": "Forced hot dryer → refuse.",
        "must_include_en": "immediate cold rinse, cold only, no dryer",
    }


def _golf_wear() -> dict[str, str]:
    return {
        "precheck_ko": "골프 기능성 셔츠·바지: 폴리/스판 흡습. 뒤집기. 라벨.",
        "why_ko": (
            "[왜 이 순서] 유연제·건조시트=흡습 막힘. 찬물·운동용/중성 소량. "
            "고온·강효소는 신축·코팅 손상."
        ),
        "fresh_path_ko": (
            "(1)뒤집기. (2)≤30℃ 중성/스포츠 세제 소량. (3)유연제 금지. "
            "(4)충분히 헹굼. (5)그늘 또는 저온 건조 최소. "
            "(6)잔디·진흙은 찬물 국소 먼저. 냄새는 찬물 담금+중성."
        ),
        "dried_path_ko": "땀 냄새: 찬물+중성 재담금(강세제 금지).",
        "motion_ko": "Cap2 섬세.",
        "water_temp_ko": "찬물/≤30℃.",
        "aftercare_ko": "그늘. 유연제 금지. 고온건조 주의.",
        "sense_check_ko": "손: 뻣뻣(잔여) 없음. 코: 땀 냄새.",
        "success_rate_ko": "올바른 저온·무유연제: 양호.",
        "refuse_when_ko": "유연제·고온건조 강제 → 거절.",
        "must_include_ko": "≤30℃, 유연제 금지, 뒤집기",
        "precheck_vi": "Do golf poly/spandex: lat trai. Doc nhan.",
        "why_vi": "[Tai sao] CAM xa vai (mat hut am). Lanh, bot nhe. Nhiet cao hong dan.",
        "fresh_path_vi": (
            "(1)Lat trai. (2)<=30C bot nhe. (3)CAM xa vai. (4)Xa ky. "
            "(5)Phoi/say thap. (6)Co/bun: spot lanh. Mui: ngam lanh+trung tinh."
        ),
        "dried_path_vi": "Mui mo hoi: ngam lanh+trung tinh — khong bot dam.",
        "motion_vi": "Cap2 tinh te.",
        "water_temp_vi": "Lanh / <=30C.",
        "aftercare_vi": "Phoi bong mat. CAM xa vai.",
        "sense_check_vi": "Tay: het cang. Mui: het mo hoi.",
        "success_rate_vi": "Dung quy trinh: tot.",
        "refuse_when_vi": "Bat xa vai / say nong → tu choi.",
        "must_include_vi": "<=30C, CAM xa vai, lat trai",
        "precheck_en": "Golf performance poly/spandex: inside out. Read label.",
        "why_en": "[Why] Softener/dryer sheets clog wicking. Cold, sport/mild detergent little. Heat/harsh enzyme hurts stretch.",
        "fresh_path_en": (
            "(1)Inside out. (2)≤30°C mild/sport detergent little. (3)No softener. "
            "(4)Rinse well. (5)Shade or minimal low dryer. "
            "(6)Grass/mud: cold spot first. Odor: cold soak + mild."
        ),
        "dried_path_en": "Sweat odor: cold soak + mild — no heavy detergent.",
        "motion_en": "Cap2 delicate.",
        "water_temp_en": "Cold / ≤30°C.",
        "aftercare_en": "Shade. No softener. Avoid hot dryer.",
        "sense_check_en": "Hand: no stiffness. Nose: sweat odor gone.",
        "success_rate_en": "Correct cold/no-softener: good.",
        "refuse_when_en": "Forced softener or hot dryer → refuse.",
        "must_include_en": "≤30°C, no softener, inside out",
    }


def _golf_shoe() -> dict[str, str]:
    return {
        "precheck_ko": "골프화: 끈·깔창 분리. 스파이크/밑창 흙 제거. 가죽 vs 천/합성 구분.",
        "why_ko": "[왜 이 순서] 스니커와 같이 고온건조=접착 손상. 가죽=최소 물+크림. 천=≤30℃.",
        "fresh_path_ko": (
            "(1)마른 흙·스파이크 솔. (2)갑피 연질+중성 / 밑창 경질. "
            "(3)천·합성: 손 또는 망 ≤30℃. 가죽: 젖은 천+가죽크림. "
            "(4)헹굼. (5)신문지 채워 그늘 — 고온건조 금지."
        ),
        "dried_path_ko": "재스팟팅. 가죽 담금 금지. 건조기 금지.",
        "motion_ko": "갑피 Cap2 연질; 밑창 Cap2–3.",
        "water_temp_ko": "≤30℃. 가죽=최소 물.",
        "aftercare_ko": "완전 건조 후 착용. 고온건조 금지.",
        "sense_check_ko": "눈: 잔여 흙. 손: 미끄럼 없음.",
        "success_rate_ko": "천·합성: 양호. 가죽: 국소만.",
        "refuse_when_ko": "고온건조·가죽 통세탁 강제 → 거절.",
        "must_include_ko": "끈·깔창 분리, 그늘 건조, 고온건조 금지",
        "precheck_vi": "Giay golf: thao day/lot. Chai gai. Phan da vs vai.",
        "why_vi": "[Tai sao] CAM say nong. Da: it nuoc. Vai: 30C nhe.",
        "fresh_path_vi": (
            "(1)Chai bun/gai. (2)Than sol mem / de sol cung. "
            "(3)Vai: tay/tui luoi 30C. Da: lau am+kem. (4)Xa. (5)Nhet bao phoi — CAM say."
        ),
        "dried_path_vi": "Spot lai. Khong ngam da. CAM say.",
        "motion_vi": "Than Cap2; de Cap2-3.",
        "water_temp_vi": "<=30C; da it nuoc.",
        "aftercare_vi": "Kho han. CAM say nong.",
        "sense_check_vi": "Mat: het bun. Tay: het tron.",
        "success_rate_vi": "Vai: tot. Da: spot.",
        "refuse_when_vi": "Bat say / ngam da → tu choi.",
        "must_include_vi": "thao day+lot, phoi bong mat, CAM say nong",
        "precheck_en": "Golf shoe: remove laces/insoles. Clean cleats. Leather vs fabric/synthetic.",
        "why_en": "[Why] Like sneakers: hot dryer kills glue. Leather: minimal water + cream. Fabric: ≤30°C.",
        "fresh_path_en": (
            "(1)Brush dry mud/cleats. (2)Soft brush upper + mild; hard brush outsole. "
            "(3)Fabric/synth: hand or mesh ≤30°C. Leather: damp wipe + cream. "
            "(4)Rinse. (5)Stuff paper; shade dry — no hot dryer."
        ),
        "dried_path_en": "Re-spot. No leather soak. No dryer.",
        "motion_en": "Upper Cap2 soft; outsole Cap2–3.",
        "water_temp_en": "≤30°C; leather minimal water.",
        "aftercare_en": "Wear fully dry. No hot dryer.",
        "sense_check_en": "Eyes: mud gone. Hand: no slip.",
        "success_rate_en": "Fabric/synth: good. Leather: spot only.",
        "refuse_when_en": "Forced hot dryer or leather soak → refuse.",
        "must_include_en": "remove laces/insoles, shade dry, no hot dryer",
    }


def _hiking_shoe() -> dict[str, str]:
    return {
        "precheck_ko": "등산화: 끈·깔창 분리. 마른 진흙. 멤브레인(고어) vs 가죽 vs 천 구분.",
        "why_ko": (
            "[왜 이 순서] 고온건조 금지. 멤브레인=세제 소량·유연제 금지. "
            "가죽=최소 물+크림. 방수 저하 시 DWR 재도포."
        ),
        "fresh_path_ko": (
            "(1)마른 흙 솔. (2)국소 스포팅. "
            "(3)천·멤브레인: 손/망 ≤30℃ 세제 소량·추가 헹굼. 가죽: 젖은 천+크림. "
            "(4)신문지 그늘 건조 — 고온건조 금지. "
            "(5)마른 뒤 필요 시 DWR 스프레이."
        ),
        "dried_path_ko": "재시도. 건조기 금지. 접착 분리 가능 고지.",
        "motion_ko": "갑피 연질; 밑창 경질 약하게.",
        "water_temp_ko": "≤30℃.",
        "aftercare_ko": "완전 건조·고온건조 금지·건조 보관.",
        "sense_check_ko": "손: 내부 습도 없음. 눈: 진흙 잔여.",
        "success_rate_ko": "천·멤브레인: 양호. 가죽: 국소.",
        "refuse_when_ko": "고온건조 강제 → 거절.",
        "must_include_ko": "끈·깔창 분리, ≤30℃, 고온건조 금지, DWR 선택",
        "precheck_vi": "Giay leo: thao day/lot. Chai bun. Membrane vs da vs vai.",
        "why_vi": "[Tai sao] CAM say nong. Membrane: bot it, CAM xa vai. Da: it nuoc+kem. Co the xit DWR.",
        "fresh_path_vi": (
            "(1)Chai kho. (2)Spot. (3)Vai/membrane: tay/tui 30C bot it + xa them. "
            "Da: lau+kem. (4)Nhet bao phoi — CAM say. (5)Xit DWR neu can."
        ),
        "dried_path_vi": "Lap. CAM say. Bao keo long.",
        "motion_vi": "Than sol mem; de sol cung nhe.",
        "water_temp_vi": "<=30C.",
        "aftercare_vi": "Kho han. CAM say nong.",
        "sense_check_vi": "Tay: het am trong. Mat: het bun.",
        "success_rate_vi": "Vai/membrane: tot. Da: spot.",
        "refuse_when_vi": "Bat say nong → tu choi.",
        "must_include_vi": "thao day+lot, <=30C, CAM say, DWR tuy chon",
        "precheck_en": "Hiking shoe: remove laces/insoles. Dry mud. Membrane vs leather vs fabric.",
        "why_en": "[Why] No hot dryer. Membrane: little detergent, no softener. Leather: minimal water + cream. Reapply DWR if wet-out.",
        "fresh_path_en": (
            "(1)Brush dry mud. (2)Spot clean. "
            "(3)Fabric/membrane: hand/mesh ≤30°C little detergent + extra rinse. Leather: damp wipe + cream. "
            "(4)Stuff paper; shade dry — no hot dryer. "
            "(5)When dry, optional DWR spray."
        ),
        "dried_path_en": "Retry. No dryer. Disclose glue separation risk.",
        "motion_en": "Upper soft brush; outsole hard lightly.",
        "water_temp_en": "≤30°C.",
        "aftercare_en": "Fully dry. No hot dryer. Store dry.",
        "sense_check_en": "Hand: interior dry. Eyes: mud gone.",
        "success_rate_en": "Fabric/membrane: good. Leather: spot.",
        "refuse_when_en": "Forced hot dryer → refuse.",
        "must_include_en": "remove laces/insoles, ≤30°C, no hot dryer, optional DWR",
    }


def _running_mesh() -> dict[str, str]:
    return {
        "precheck_ko": "러닝 메시 운동화: 망사 얇아 찢김 쉬움. 기계 시 반드시 세탁망. 끈·깔창 분리.",
        "why_ko": "[왜 이 순서] 메시=기계 마찰에 약함. 연질/초연질만. ≤30℃. 흰 끈 별도.",
        "fresh_path_ko": (
            "(1)마른 흙 약하게. (2)연질+중성 국소. "
            "(3)손세탁 또는 망+≤30℃ 섬세. (4)충분히 헹굼. "
            "(5)신문지 그늘 — 고온건조 금지. (6)경질 솔을 망사에 쓰지 말 것."
        ),
        "dried_path_ko": "재스팟팅. 경질 솔 금지. 안 되면 메시 착색 한계 고지.",
        "motion_ko": "Cap1–2 연질/초연질, 결 방향.",
        "water_temp_ko": "≤30℃ 섬세.",
        "aftercare_ko": "그늘·형태 유지. 완전 건조 후 착용.",
        "sense_check_ko": "눈: 찢김·잔여. 손: 미끄럼 없음.",
        "success_rate_ko": "조기: 양호. 오래된 메시 착색: 중간↓.",
        "refuse_when_ko": "경질 솔·고온건조 강제 → 거절.",
        "must_include_ko": "세탁망, 연질만, ≤30℃, 고온건조 금지",
        "precheck_vi": "Giay mesh: de rach. BAT BUOC tui luoi. Thao day+lot.",
        "why_vi": "[Tai sao] Mesh yeu ma sat. Chi sol mem. <=30C. Day trang rieng.",
        "fresh_path_vi": (
            "(1)Chai kho nhe. (2)Spot sol mem+trung tinh. "
            "(3)Tay hoac TUI LUOI 30C. (4)Xa ky. (5)Nhet bao phoi — CAM say. (6)CAM sol cung tren mesh."
        ),
        "dried_path_vi": "Spot lai. CAM sol cung. Bao gioi han mau bam mesh.",
        "motion_vi": "Cap1-2 sol mem theo soi.",
        "water_temp_vi": "<=30C tinh te.",
        "aftercare_vi": "Phoi bong mat. Kho han moi mang.",
        "sense_check_vi": "Mat: rach/du. Tay: het tron.",
        "success_rate_vi": "Som: tot. Bam mau cu: thap.",
        "refuse_when_vi": "Bat sol cung / say nong → tu choi.",
        "must_include_vi": "tui luoi, sol mem, <=30C, CAM say",
        "precheck_en": "Mesh running shoe: tear-prone. Mesh bag required in machine. Remove laces/insoles.",
        "why_en": "[Why] Mesh hates drum abrasion. Soft/ultra brush only. ≤30°C. Wash white laces separate.",
        "fresh_path_en": (
            "(1)Light dry brush. (2)Soft brush + mild spot. "
            "(3)Hand or mesh bag ≤30°C delicate. (4)Rinse well. "
            "(5)Stuff paper; shade — no hot dryer. (6)Never hard brush on mesh."
        ),
        "dried_path_en": "Re-spot. No hard brush. Disclose mesh dye hold limits.",
        "motion_en": "Cap1–2 soft/ultra with the weave.",
        "water_temp_en": "≤30°C delicate.",
        "aftercare_en": "Shade, hold shape. Wear fully dry.",
        "sense_check_en": "Eyes: tears/residue. Hand: no slip.",
        "success_rate_en": "Early: good. Old mesh staining: lower.",
        "refuse_when_en": "Forced hard brush or hot dryer → refuse.",
        "must_include_en": "mesh bag, soft brush only, ≤30°C, no hot dryer",
    }


def apply_garment_specialty_hints(graph: dict[str, Any], item_id: str) -> dict[str, Any]:
    if item_id not in GARMENT_SPECIALTY_IDS:
        return graph
    out = dict(graph)
    tools = list(out.get("tools") or [])
    if not any(str(t.get("id")) == "T_CLOTH" for t in tools):
        tools.append({
            "id": "T_CLOTH",
            "name_ko": "흰 천·흡수지",
            "name_vi": "Khan trang",
            "name_en": "White cloth",
            "use_for_ko": "국소 닦기·받침.",
            "use_for_vi": "Lau/lot cuc bo.",
            "use_for_en": "Spot wipe / backer.",
        })
    if item_id in {"I_RUNNING_MESH", "I_SWIMWEAR", "I_GOLF_WEAR"} and not any(
        str(t.get("id")) == "T_MESH_BAG" for t in tools
    ):
        tools.append({
            "id": "T_MESH_BAG",
            "name_ko": "세탁망",
            "name_vi": "Tui luoi",
            "name_en": "Mesh laundry bag",
            "use_for_ko": "메시·스판·기능성 기계 세탁 시 필수.",
            "use_for_vi": "Bat buoc khi may mesh/spandex.",
            "use_for_en": "Required for mesh/spandex machine wash.",
        })
    out["tools"] = tools
    if item_id in {"I_GORETEX", "I_GOLF_WEAR", "I_BABY_WEAR", "I_CURTAIN_FABRIC", "I_DENIM"}:
        out.setdefault("empty_chems_ok", True)
    if item_id == "I_CURTAIN_URETHANE":
        out["chemicals"] = [
            {
                "code": "D2",
                "name_ko": "중성·주방세제(국소)",
                "name_vi": "D2 trung tinh",
                "name_en": "Mild dish soap (spot)",
                "dilution_ko": "약희석·천에 묻혀 닦기.",
                "dilution_vi": "Pha nhe tren khan.",
                "dilution_en": "Light dilution on cloth.",
            }
        ]
        out["empty_chems_ok"] = False
    return out
