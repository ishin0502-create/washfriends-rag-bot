# -*- coding: utf-8 -*-
"""Remaining tip-only Items → full KO/VI/EN specialty cards.

I_CARE_LABEL, I_INTAKE_SCRIPT, I_WATER_HARDNESS, I_COLOR_FADE, I_WHITE_FADE,
I_KNIT, I_UNDERWEAR, I_ACTIVEWEAR, I_SCARF, I_GOLF_GLOVE_SYNTH.
Truth: main.py Item seeds + w3_clothing_items. No invented chemistry.
"""
from __future__ import annotations

from typing import Any

OPS_REMAINDER_IDS = frozenset({
    "I_CARE_LABEL",
    "I_INTAKE_SCRIPT",
    "I_CLAIM_SCRIPT",
    "I_WATER_HARDNESS",
    "I_COLOR_FADE",
    "I_WHITE_FADE",
    "I_KNIT",
    "I_UNDERWEAR",
    "I_ACTIVEWEAR",
    "I_SCARF",
    "I_GOLF_GLOVE_SYNTH",
})


def education_for_ops_remainder(item_id: str) -> dict[str, str]:
    return {
        "I_CARE_LABEL": _care_label,
        "I_INTAKE_SCRIPT": _intake,
        "I_CLAIM_SCRIPT": _claim,
        "I_WATER_HARDNESS": _water,
        "I_COLOR_FADE": _color_fade,
        "I_WHITE_FADE": _white_fade,
        "I_KNIT": _knit,
        "I_UNDERWEAR": _underwear,
        "I_ACTIVEWEAR": _activewear,
        "I_SCARF": _scarf,
        "I_GOLF_GLOVE_SYNTH": _golf_glove_synth,
    }.get(item_id, lambda: {})()


def _care_label() -> dict[str, str]:
    out = {
        "precheck_ko": "케어라벨: 옷 안쪽 라벨 찾기. 흐리면 사진. X 표시면 추측 금지 — 그대로 준수.",
        "why_ko": (
            "[왜] 라벨=원단과의 계약. "
            "물통=세탁(숫자=최고 ℃·손=손세탁·X=물세탁 금지). "
            "삼각형=표백(빈칸=가능·사선=산소만·X=금지). "
            "네모=건조(점=열·X원=건조기 금지). 다리미=점 열·X=금지. 원=드라이(P/F/W·X=금지)."
        ),
        "fresh_path_ko": (
            "(1)5그룹 기호 읽기. (2)최고 수온·표백·건조·다림·드라이 적기. "
            "(3)물통 X → 드라이/이관(I_DRY_VS_WET). (4)유색은 보통 산소만. (5)라벨 흐리면 고객 고지."
        ),
        "dried_path_ko": "라벨 소실: 소재 묻고 구석 테스트. 낮은 안전(찬물·표백 금지) 우선.",
        "motion_ko": "Cap0 — 읽기·기록. 추측 금지",
        "water_temp_ko": "물통 숫자 이하. 항상 max보다 낮게 시작",
        "aftercare_ko": "라벨 유지. 잘라내지 말 것.",
        "sense_check_ko": "눈: 5그룹 기록 완료. X면 준수 확인.",
        "success_rate_ko": "라벨 준수=사고↓. 무시=클레임↑.",
        "refuse_when_ko": "X 기호 무시하고 강제 물세탁 → 거절.",
        "must_include_ko": "5그룹 기호, X 준수, 유색 산소만, 추측 금지",
        "precheck_vi": "Tìm nhãn. Ảnh nếu mờ. X → TUÂN THỦ, không đoán.",
        "why_vi": "[Tại sao] Nhãn = hợp đồng. Chậu=nhiệt/tay/X. Tam giác=tẩy. Vuông=sấy. Ủi. Vòng=dry.",
        "fresh_path_vi": "(1)Đọc 5 nhóm. (2)Ghi max. (3)X nước → dry. (4)Màu: oxy. (5)Nhãn mờ → báo.",
        "dried_path_vi": "Nhãn mất: test góc, an toàn thấp.",
        "motion_vi": "Cap0 — đọc, không đoán",
        "water_temp_vi": "Theo số; bắt đầu thấp hơn max",
        "aftercare_vi": "Giữ nhãn. CẤM cắt.",
        "sense_check_vi": "Mắt: ghi đủ 5 nhóm.",
        "success_rate_vi": "Tuân thủ: tốt.",
        "refuse_when_vi": "Bắt bỏ qua X → từ chối.",
        "must_include_vi": "5 nhóm, tuân X, màu oxy, không đoán",
        "precheck_en": "Find care label. Photo if faded. Any X → obey, do not guess.",
        "why_en": "[Why] Label is the fabric contract. Tub=wash max °C/hand/X. Triangle=bleach. Square=dryer. Iron dots. Circle=dry-clean.",
        "fresh_path_en": "(1)Read 5 symbol groups. (2)Note max temp/bleach/dry/iron/dry-clean. (3)Tub X → dry-clean. (4)Colors usually oxygen only. (5)Disclose faded label.",
        "dried_path_en": "Missing label: ask fiber + corner test; safest low path.",
        "motion_en": "Cap0 — read/record. No guessing.",
        "water_temp_en": "At/below tub number; start cooler than max.",
        "aftercare_en": "Keep label. Do not cut off.",
        "sense_check_en": "Eyes: all 5 groups logged.",
        "success_rate_en": "Obey label → fewer incidents.",
        "refuse_when_en": "Forced wet wash past X → refuse.",
        "must_include_en": "5 symbol groups, obey X, oxygen on colors, no guessing",
    }
    try:
        from education_ops_depth_v12 import education_for_ops_depth

        out.update(education_for_ops_depth("I_CARE_LABEL"))
    except Exception:
        pass
    return out


def _intake() -> dict[str, str]:
    try:
        from education_ops_depth_v12 import education_for_ops_depth

        deep = education_for_ops_depth("I_INTAKE_SCRIPT")
        if deep:
            return deep
    except Exception:
        pass
    return {
        "precheck_ko": "접수: 카메라·전표 2부·위험 태그(실크/울/빈티지) 준비.",
        "why_ko": (
            "[왜] 사진+서명=법적 보호. "
            "필수: 인사→수량·기존 손상 기록→전체+클로즈업 사진→가격·기한→전표 서명. "
            "마른 얼룩은 사전 고지+서면 동의. 사진 없이 접수=패소 위험."
        ),
        "fresh_path_ko": (
            "(1)인사. (2)수량·얼룩 기록. (3)전체+클로즈업 사진. (4)가격·기한. "
            "(5)전표 2부 서명. (6)마른 얼룩: 「100% 안 될 수 있습니다 — 동의하시나요?」 "
            "(7)위험 품목 태그."
        ),
        "dried_path_ko": "클레임: 접수 사진 대조 → 매장 과실이면 사과 / 기존 손상이면 사진 제시.",
        "motion_ko": "Cap0 — 응대·촬영",
        "water_temp_ko": "해당 없음",
        "aftercare_ko": "사진·전표 보관. Zalo 문의 <2시간 응답(사진 있으면).",
        "sense_check_ko": "눈: 사진·서명 완비. 기록: 수량 일치.",
        "success_rate_ko": "사진+동의: 분쟁↓.",
        "refuse_when_ko": "사진·서명 거부하면서 고가 위험품 접수 요구 → 거절.",
        "must_include_ko": "사진 2종, 전표 서명, 마른 얼룩 동의, 위험 태그",
        "precheck_vi": "May anh + phieu 2 ban + tag rui ro.",
        "why_vi": "[Tai sao] Anh+chu ky bao ve. Bat buoc chup + ky. Vet kho: bao truoc.",
        "fresh_path_vi": "(1)Chao. (2)Dem+ghi. (3)Anh tong+close. (4)Gia/thoi gian. (5)Ky 2 ban. (6)Vet kho: xin dong y. (7)Tag.",
        "dried_path_vi": "Khieu nai: doi anh nhan.",
        "motion_vi": "Cap0",
        "water_temp_vi": "N/A",
        "aftercare_vi": "Luu anh+phieu. Zalo <2h.",
        "sense_check_vi": "Mat: du anh+ky.",
        "success_rate_vi": "Anh+dong y: giam tranh chap.",
        "refuse_when_vi": "Tu choi anh/ky mon rui ro → tu choi nhan.",
        "must_include_vi": "2 anh, ky phieu, dong y vet kho, tag",
        "precheck_en": "Camera ready. Two tickets. Risk tags (silk/wool/vintage).",
        "why_en": "[Why] Photo+signature protect legally. Count→photo→price/time→sign. Dried stains need written consent.",
        "fresh_path_en": "(1)Greet. (2)Count+note damage. (3)Full+close-up photos. (4)Price/time. (5)Sign 2 copies. (6)Dried stain consent script. (7)Risk tag.",
        "dried_path_en": "Claim: compare intake photos.",
        "motion_en": "Cap0 — talk + photo.",
        "water_temp_en": "N/A",
        "aftercare_en": "Store photos+ticket. Reply Zalo <2h if photo attached.",
        "sense_check_en": "Eyes: photos+signature complete.",
        "success_rate_en": "Photo+consent → fewer disputes.",
        "refuse_when_en": "No photo/sign on high-risk item → refuse intake.",
        "must_include_en": "two photos, signed ticket, dried-stain consent, risk tag",
    }


def _claim() -> dict[str, str]:
    try:
        from education_ops_depth_v12 import education_for_ops_depth

        deep = education_for_ops_depth("I_CLAIM_SCRIPT")
        if deep:
            return deep
    except Exception:
        pass
    return {
        "why_ko": "[왜] 클레임=사진·전표 증거. 진정→대조→과실 사과 / 기존 손상 사진.",
        "fresh_path_ko": "(1)전표·사진 확인. (2)대조. (3)과실이면 사과·보상안. (4)즉흥 100% 환불 금지.",
        "must_include_ko": "접수사진, 전표, 사과·보상안",
        "why_vi": "[Tại sao] Khiếu nại = ảnh phiếu. Bình tĩnh → đối chiếu.",
        "fresh_path_vi": "(1)Phiếu+ảnh. (2)So. (3)Lỗi shop: xin lỗi. (4)CẤM hoàn 100% nóng.",
        "must_include_vi": "ảnh nhận, phiếu, xin lỗi",
        "why_en": "[Why] Claims need photos+ticket.",
        "fresh_path_en": "(1)Ticket+photos. (2)Compare. (3)Apology+offer if shop fault. (4)No impulse 100% refund.",
        "must_include_en": "intake photo, ticket, apology+offer",
    }


def _water() -> dict[str, str]:
    return {
        "precheck_ko": "경수: 거품 적음·옷 뻣뻣·흰옷 누런 물때·세탁기 스케일. VN 여러 도시 경수.",
        "why_ko": (
            "[왜] Ca/Mg=세제 효과↓·잔여·스케일. "
            "보정: 세제 약간↑ / 경수용·추가 헹굼·선택 A3 마지막 헹굼·정기 통세척. "
            "유연제로 헹굼 대체 금지(수건 흡수↓)."
        ),
        "fresh_path_ko": (
            "(1)경수 징후 확인. (2)세제 +1단계. (3)추가 헹굼. "
            "(4)선택 A3 약희석 마무리 헹굼(락스와 혼합 금지). "
            "(5)흰 누런 물때: 산소 균일(단백질 락스 남용 금지). (6)통 60–90℃ 정기 세척."
        ),
        "dried_path_ko": "뻣뻣: 재헹굼+A3. 석회: citric/A3 통세척.",
        "motion_ko": "Cap0 — 프로그램 보정",
        "water_temp_ko": "원단 따름. 통세척은 고온(라벨 허용 시)",
        "aftercare_ko": "지역 수질 메모. 유연제로 헹굼 대체 금지.",
        "sense_check_ko": "손: 잔여 세제 없음. 눈: 물때↓.",
        "success_rate_ko": "보정 준수: 양호.",
        "refuse_when_ko": "유연제만으로 경수 해결 요구 → 거절·고지.",
        "must_include_ko": "세제 보정, 추가 헹굼, A3 선택, 유연제 대체 금지",
        "precheck_vi": "Dau hieu nuoc cung: it bot, vai cung, vang, can may.",
        "why_vi": "[Tai sao] Ca/Mg giam bot. Bu: bot+ / xa them / A3 / ve sinh may. CAM thay bang softener.",
        "fresh_path_vi": "(1)Nhan. (2)Bot +1. (3)Xa them. (4)A3 cuoi (CAM Javel). (5)Trang: B1. (6)Ve sinh 60-90C.",
        "dried_path_vi": "Cang: xa lai+A3. Can: citric/A3.",
        "motion_vi": "Cap0",
        "water_temp_vi": "Theo vai; ve sinh cao neu cho",
        "aftercare_vi": "Ghi khu vuc. CAM softener thay xa.",
        "sense_check_vi": "Tay: het bot.",
        "success_rate_vi": "Bu dung: tot.",
        "refuse_when_vi": "Chi softener → bao/tu choi.",
        "must_include_vi": "bot+, xa them, A3 tuy chon, CAM softener thay",
        "precheck_en": "Hard water signs: little suds, stiff cloth, yellow whites, machine scale.",
        "why_en": "[Why] Ca/Mg kill detergent. Fix: dose up, extra rinse, optional A3 final rinse, descaling. Softener is not a rinse substitute.",
        "fresh_path_en": "(1)Confirm signs. (2)+1 detergent. (3)Extra rinse. (4)Optional dilute A3 final (never with bleach). (5)White yellowing: even oxygen. (6)Clean drum 60–90°C periodically.",
        "dried_path_en": "Stiff: re-rinse+A3. Scale: citric/A3 clean.",
        "motion_en": "Cap0 — program adjust.",
        "water_temp_en": "Per fabric; hot clean if allowed.",
        "aftercare_en": "Note area water. No softener instead of rinse.",
        "sense_check_en": "Hand: no detergent slip.",
        "success_rate_en": "Correction → good.",
        "refuse_when_en": "Softener-only hard-water fix → refuse/disclose.",
        "must_include_en": "dose up, extra rinse, optional A3, no softener substitute",
    }


def _color_fade() -> dict[str, str]:
    return {
        "precheck_ko": (
            "유색 색바램: 사진+면적. "
            "(a)착용·UV (b)약품 탈색 (c)이염. 데님 바랜 자국=특성일 수 있음. 100% 복원 금지."
        ),
        "why_ko": (
            "[왜] 유색 탈색=염료 약화. "
            "세제·소금·커피·청바지 같이 돌려 ‘재염색’ 민간요법 금지. "
            "동전 이하=패브릭 마커 임시. 손바닥 이상=전문 염색/보상 논의."
        ),
        "fresh_path_ko": (
            "(1)사진·동의·한계 고지. "
            "(2)작음(≤동전): 동일색 패브릭 마커 → 바깥→안 점찍기 → 제품 지침 고착 — 세탁 시 다시 빠질 수 있음 고지. "
            "(3)중간/큼: 마커만으로 끝내지 말 것 — 염색 이관/보상. "
            "(4)세제·청바지 동시세탁 ‘재염색’·에탄올+오일+건조기 금지."
        ),
        "dried_path_ko": "이미 표백 탈색: 중단·사진·염색/보상. 산소/염소로 ‘맞춤’ 금지.",
        "motion_ko": "작은 마커만 Cap1 점. 중·대: 전면 마커 금지",
        "water_temp_ko": "복원 단계=통세탁/열담금 염색 금지. 유지 세탁은 뒤집기·찬물·단독.",
        "aftercare_ko": "강광 확인. 마커=임시. 그늘. 뒤집기·찬물·단독 권고.",
        "sense_check_ko": "눈: 색 맞춤 한계. 기록: 동의 문구.",
        "success_rate_ko": "작은 점: 임시 양호. 중·대: 낮음 — 사전 고지.",
        "refuse_when_ko": "100% 원상복구·민간요법 강제 → 거절.",
        "must_include_ko": "100% 비보장, 작은 점만 마커, 중·대는 염색/보상, 민간요법 금지",
        "precheck_vi": "Anh+dien tich. UV/tay/loang. Denim bac = dac trung. CAM 100%.",
        "why_vi": "[Tai sao] Khong phuc bang bot/muoi/cafe/jean moi. Nho: but. Vua/lon: nhuom/boi.",
        "fresh_path_vi": "(1)Anh+dong y. (2)Nho: but. (3)Vua/lon: chuyen. (4)CAM meo dan gian.",
        "dried_path_vi": "Da tay: dung, anh, nhuom/boi. CAM oxy can bang mau.",
        "motion_vi": "But nho Cap1. Vua/lon: khong but toan.",
        "water_temp_vi": "Khong ngam nhuom tai quay. Duy tri: lat+lanh+rieng.",
        "aftercare_vi": "Anh sang. But tam thoi. Phoi bong.",
        "sense_check_vi": "Mat: gioi han mau.",
        "success_rate_vi": "Nho: tam. Lon: thap.",
        "refuse_when_vi": "Bat 100%/meo → tu choi.",
        "must_include_vi": "khong 100%, but nho, lon=nhuom/boi, CAM meo",
        "precheck_en": "Photo+area. UV wear vs chemical fade vs bleed. Denim whiskers may be normal. No 100% restore.",
        "why_en": "[Why] Color loss ≠ magic restore. No detergent/salt/coffee/new-jeans folk dyes. Coin-size marker; palm+ → pro dye/compensate.",
        "fresh_path_en": "(1)Photo+consent+limits. (2)Small: fabric marker dab out→in; disclose wash-off. (3)Medium/large: refer dye/compensate. (4)No folk re-dye hacks.",
        "dried_path_en": "Already bleached: stop; photo; dye/pay. No oxygen to 'even' colors.",
        "motion_en": "Small marker Cap1 only. No full-panel marker on large fades.",
        "water_temp_en": "No shop hot re-dye soak. Maintain: inside out, cold, alone.",
        "aftercare_en": "Strong light. Marker temporary. Shade. Cold separate washes.",
        "sense_check_en": "Eyes: color match limits. Record consent.",
        "success_rate_en": "Tiny spot: temporary fair. Large: low — disclose.",
        "refuse_when_en": "Forced 100% / folk hacks → refuse.",
        "must_include_en": "no 100%, marker only if tiny, large→dye/pay, no folk hacks",
    }


def _white_fade() -> dict[str, str]:
    return {
        "precheck_ko": "흰·밝은 옷만. 사진. 표백 후 흰 반점=OBA 깨짐. 유색에 이 경로 금지.",
        "why_ko": (
            "[왜] 흰옷 얼룩환·부분 탈색은 점 찍기보다 "
            "산소표백을 전체에 균일 담가야 맞춤. 점만 바르면 더 얼룩환."
        ),
        "fresh_path_ko": (
            "(1)흰/밝은 확인. (2)산소표백 희석액으로 전체 균일 ~45분(제품 지침). "
            "(3)헹굼. (4)남은 점만: 베이킹소다+과산화 약페이스트 10분(점만). "
            "(5)면 허용 시 ~40℃ 세탁. (6)강광 확인."
        ),
        "dried_path_ko": "여전히 얼룩환: 균일 담금 반복(점 찍기 금지). 안 되면 한계 고지.",
        "motion_ko": "Cap0–1 균일 담금. 강한 문지르기 금지",
        "water_temp_ko": "라벨. 면 보통 ~40℃ 후세탁",
        "aftercare_ko": "흰 균일 확인. 유색→I_COLOR_FADE.",
        "sense_check_ko": "눈: 흰 균일. 강광.",
        "success_rate_ko": "조기·균일: 양호. 오래된 얼룩환: 중간.",
        "refuse_when_ko": "유색에 흰옷 경로 강제 → 거절.",
        "must_include_ko": "흰만, 전체 균일 산소, 점 찍기 금지, 유색 금지",
        "precheck_vi": "CHI trang/sang. Anh. Dom trang = OBA. CAM mau.",
        "why_vi": "[Tai sao] Can bang bang B1 DEU TOAN BO — cham diem = lo hon.",
        "fresh_path_vi": "(1)Xac nhan trang. (2)Ngam B1 deu ~45 phut. (3)Xa. (4)Dom: paste N1+A4 10 phut. (5)~40C neu cotton. (6)Anh sang.",
        "dried_path_vi": "Con lech: ngam deu lai. Bao gioi han.",
        "motion_vi": "Cap0-1 ngam deu",
        "water_temp_vi": "Theo nhan; cotton ~40C",
        "aftercare_vi": "Kiem trang deu. Mau → I_COLOR_FADE.",
        "sense_check_vi": "Mat: trang deu.",
        "success_rate_vi": "Som+deu: tot.",
        "refuse_when_vi": "Bat len mau → tu choi.",
        "must_include_vi": "chi trang, B1 deu, CAM cham diem, CAM mau",
        "precheck_en": "Whites/lights only. Photo. White spots after bleach = OBA break. Never on colors.",
        "why_en": "[Why] Even oxygen soak balances whites. Spot-dabbing makes halos worse.",
        "fresh_path_en": "(1)Confirm white. (2)Even oxygen soak ~45 min per label. (3)Rinse. (4)Remaining dots: light baking soda+peroxide paste 10 min. (5)~40°C if cotton allows. (6)Strong light.",
        "dried_path_en": "Still uneven: repeat even soak (no spot dots). Disclose limits.",
        "motion_en": "Cap0–1 even soak. No hard rub.",
        "water_temp_en": "Per label; cotton often ~40°C after.",
        "aftercare_en": "Check even white. Colors → I_COLOR_FADE.",
        "sense_check_en": "Eyes: even white under strong light.",
        "success_rate_en": "Early even soak: good. Old halo: fair.",
        "refuse_when_en": "Forced white path on colors → refuse.",
        "must_include_en": "whites only, even oxygen soak, no spot-dotting, no colors",
    }


def _knit() -> dict[str, str]:
    return {
        "precheck_ko": "니트: 울/면 구분. 울=중성·손세탁. 비틀어 짜기 금지.",
        "why_ko": "[왜] 니트=형태가 생명. 비틀면 변형. 찬물·중성, 눌러 물기만. 뉘어 건조 — 걸면 어깨 늘어남.",
        "fresh_path_ko": "(1)찬물/≤30℃. (2)울=S1, 면니트만 약세제. (3)눌러 헹굼 — 짜기 금지. (4)수건 위 평건·형태. (5)걸이 건조 금지.",
        "dried_path_ko": "이미 늘어남: 복원 한계 고지. 추가 기계 금지.",
        "motion_ko": "Cap1. 짜기 금지",
        "water_temp_ko": "≤30℃",
        "aftercare_ko": "평건 확인. 얼룩 있으면 강광.",
        "sense_check_ko": "손: 비틀림 없음. 눈: 어깨·통.",
        "success_rate_ko": "손+평건: 높음. 기계: 수축·변형 위험.",
        "refuse_when_ko": "울 니트 세탁기·건조기 강제 → 거절.",
        "must_include_ko": "짜기 금지, 평건, 걸이 금지, 울=S1",
        "precheck_vi": "Len/cotton. CAM vat.",
        "why_vi": "[Tai sao] Form = mang. Khong vat, phoi nam. May = rut.",
        "fresh_path_vi": "(1)Lanh. (2)S1. (3)Ep, CAM vat. (4)Phoi nam. (5)CAM treo.",
        "dried_path_vi": "Da gian: bao gioi han.",
        "motion_vi": "Cap1; CAM vat",
        "water_temp_vi": "<=30C",
        "aftercare_vi": "Phoi nam. Anh sang neu vet.",
        "sense_check_vi": "Tay: khong xe. Mat: vai.",
        "success_rate_vi": "Tay+nam: cao. May: thap.",
        "refuse_when_vi": "Bat may/say len → tu choi.",
        "must_include_vi": "CAM vat, phoi nam, CAM treo, S1",
        "precheck_en": "Knit: wool vs cotton. Wool=neutral hand wash. No wring.",
        "why_en": "[Why] Shape is everything. Wringing warps. Cold mild; press water only. Flat dry — hang stretches shoulders.",
        "fresh_path_en": "(1)Cold/≤30°C. (2)Wool S1; cotton knit mild only. (3)Press-rinse — no wring. (4)Flat reshape on towels. (5)No hang dry.",
        "dried_path_en": "Already stretched: disclose limits. No more machine.",
        "motion_en": "Cap1. No wring.",
        "water_temp_en": "≤30°C.",
        "aftercare_en": "Confirm flat dry. Strong light if stained.",
        "sense_check_en": "Hand: no twist. Eyes: shoulders/body.",
        "success_rate_en": "Hand+flat: high. Machine: shrink/warp risk.",
        "refuse_when_en": "Forced washer/dryer on wool knit → refuse.",
        "must_include_en": "no wring, flat dry, no hang, wool=S1",
    }


def _underwear() -> dict[str, str]:
    return {
        "precheck_ko": "속옷·브라: 브라=손세탁 또는 망+섬세. 와이어·훅 보호.",
        "why_ko": "[왜] 브라 기계 직행=형태·와이어 손상. 면 팬티=망+40℃. 스판=찬물. 유연제 과다=탄성↓.",
        "fresh_path_ko": "(1)면 팬티: 망 40℃. (2)브라: 손≤30℃ 또는 망+섬세. (3)란제리: 손·중성. (4)브라 컵 형태 유지 건조 — 걸이 주의.",
        "dried_path_ko": "와이어 변형: 복원 어려움 고지.",
        "motion_ko": "Cap1–2",
        "water_temp_ko": "브라 ≤30℃. 면 팬티 ~40℃",
        "aftercare_ko": "위생 세탁. 형태 확인.",
        "sense_check_ko": "손: 훅·와이어. 눈: 탄성.",
        "success_rate_ko": "손/망: 양호. 브라 직행 기계: 위험.",
        "refuse_when_ko": "고가 란제리 강표백·건조기 → 거절.",
        "must_include_ko": "브라 손/망, 와이어 보호, 유연제 과다 금지",
        "precheck_vi": "Ao nguc: tay hoac tui.",
        "why_vi": "[Tai sao] May truc = hong khung. Lot cotton: tui 40C.",
        "fresh_path_vi": "(1)Lot: tui 40C. (2)Ao nguc: tay 30C. (3)Lingerie: tay S1. (4)Phoi giu cup.",
        "dried_path_vi": "Khung meo: bao.",
        "motion_vi": "Cap1-2",
        "water_temp_vi": "Ao nguc <=30C; lot ~40C",
        "aftercare_vi": "Giat hang ngay. Form.",
        "sense_check_vi": "Tay: day/khung.",
        "success_rate_vi": "Tay/tui: tot.",
        "refuse_when_vi": "Tay manh/say dat → tu choi.",
        "must_include_vi": "ao nguc tay/tui, bao khung, CAM softener dam",
        "precheck_en": "Bra: hand or mesh delicate. Protect wire/hooks.",
        "why_en": "[Why] Machine bare bras warp wires. Cotton panties: mesh ~40°C. Spandex: cold. Excess softener kills stretch.",
        "fresh_path_en": "(1)Cotton panties: mesh 40°C. (2)Bra: hand ≤30°C or mesh delicate. (3)Lingerie: hand mild. (4)Dry holding cup shape.",
        "dried_path_en": "Bent wire: hard to restore — disclose.",
        "motion_en": "Cap1–2.",
        "water_temp_en": "Bra ≤30°C; cotton panties ~40°C.",
        "aftercare_en": "Daily hygiene wash. Check form.",
        "sense_check_en": "Hand: hooks/wire. Eyes: stretch.",
        "success_rate_en": "Hand/mesh: good. Bare machine bra: risky.",
        "refuse_when_en": "Forced bleach/dryer on luxury lingerie → refuse.",
        "must_include_en": "bra hand/mesh, protect wire, no heavy softener",
    }


def _activewear() -> dict[str, str]:
    return {
        "precheck_ko": "스포츠웨어: 땀=빨리 세탁. 고온·유연제 금지(스판·흡습↓).",
        "why_ko": "[왜] 즉시 세탁(발효 냄새). ~30℃·세제 소량. 유연제 금지. 냄새 심하면 A3 1:4 전처리.",
        "fresh_path_ko": "(1)즉시 또는 찬물 임시. (2)~30℃ 세제 소량. (3)유연제 금지. (4)냄새: A3 30분. (5)저온/그늘 건조.",
        "dried_path_ko": "냄새 고착: A3 재처리. 기능↓: DWR 재도포 검토.",
        "motion_ko": "Cap2 섬세",
        "water_temp_ko": "~30℃",
        "aftercare_ko": "젖은 상태 냄새·강광 확인.",
        "sense_check_ko": "코(젖은 상태): 땀내 없음.",
        "success_rate_ko": "즉시: 높음. 방치: 냄새 잔존.",
        "refuse_when_ko": "고온·유연제 강제 → 거절·고지.",
        "must_include_ko": "즉시 세탁, ≤30℃, 유연제 금지, 냄새 A3",
        "precheck_vi": "Giat ngay. CAM xa vai + nhiet cao.",
        "why_vi": "[Tai sao] Mo hoi len men. 30C it bot. CAM softener.",
        "fresh_path_vi": "(1)Giat ngay. (2)30C it. (3)CAM softener. (4)Mui: A3 30 phut. (5)Say thap/phoi.",
        "dried_path_vi": "Mui: A3 lai.",
        "motion_vi": "Cap2",
        "water_temp_vi": "~30C",
        "aftercare_vi": "Kiem mui khi uot.",
        "sense_check_vi": "Mui khi uot: het.",
        "success_rate_vi": "Som: cao.",
        "refuse_when_vi": "Bat softener/nhiet → bao.",
        "must_include_vi": "giat ngay, 30C, CAM softener, A3 mui",
        "precheck_en": "Activewear: wash sweat ASAP. No high heat/softener.",
        "why_en": "[Why] Sweat ferments fast. ~30°C little detergent. No softener. Odor: A3 1:4 pretreat.",
        "fresh_path_en": "(1)Wash ASAP or cold hold. (2)~30°C little soap. (3)No softener. (4)Odor: A3 30 min. (5)Low dryer/shade.",
        "dried_path_en": "Set odor: A3 again. Lost DWR: respray if labeled.",
        "motion_en": "Cap2 delicate.",
        "water_temp_en": "~30°C.",
        "aftercare_en": "Smell-check wet. Strong light.",
        "sense_check_en": "Nose when wet: no sweat smell.",
        "success_rate_en": "Immediate: high. Delayed: odor remains.",
        "refuse_when_en": "Forced softener/high heat → refuse/disclose.",
        "must_include_en": "wash ASAP, ≤30°C, no softener, A3 for odor",
    }


def _scarf() -> dict[str, str]:
    return {
        "precheck_ko": "스카프: 실크/울/면 구분. 실크·울=중성·약하게. 이염 주의.",
        "why_ko": "[왜] 얇아 이염·물짐 쉬움. 손세탁·중성, 비틀지 말 것. 평건. 진한 색 단독.",
        "fresh_path_ko": "(1)원단 확인. (2)찬물 중성 Cap1. (3)눌러 헹굼. (4)단독·그늘 평건. (5)강한 표백 금지.",
        "dried_path_ko": "물짐·이염: 추가 강처리 주의·고지.",
        "motion_ko": "Cap1",
        "water_temp_ko": "찬물 / ≤30℃",
        "aftercare_ko": "강광. 울/니트 스카프=평건.",
        "sense_check_ko": "눈: 이염·물짐. 손: 비틀림 없음.",
        "success_rate_ko": "손세탁: 양호. 기계: 위험.",
        "refuse_when_ko": "고가 실크 스카프 기계·표백 → 거절.",
        "must_include_ko": "손세탁, 평건, 단독, 표백 금지",
        "precheck_vi": "Lua/len/cotton. CAM may manh.",
        "why_vi": "[Tai sao] Mong — tay S1, khong vat, phoi phang.",
        "fresh_path_vi": "(1)Vai. (2)Tay lanh S1 Cap1. (3)Ep xa. (4)Phoi phang rieng. (5)CAM tay manh.",
        "dried_path_vi": "Vet nuoc/lo mau: bao.",
        "motion_vi": "Cap1",
        "water_temp_vi": "Lanh",
        "aftercare_vi": "Anh sang. Phoi phang.",
        "sense_check_vi": "Mat: lo mau.",
        "success_rate_vi": "Tay: tot.",
        "refuse_when_vi": "Bat may/tay lua → tu choi.",
        "must_include_vi": "tay, phoi phang, rieng, CAM tay manh",
        "precheck_en": "Scarf: silk/wool/cotton. Silk/wool=mild. Watch bleed.",
        "why_en": "[Why] Thin → bleed/water rings. Hand mild, no wring. Flat dry. Dark colors alone.",
        "fresh_path_en": "(1)Fiber. (2)Cold mild Cap1. (3)Press-rinse. (4)Alone, shade flat. (5)No harsh bleach.",
        "dried_path_en": "Rings/bleed: careful; disclose.",
        "motion_en": "Cap1.",
        "water_temp_en": "Cold / ≤30°C.",
        "aftercare_en": "Strong light. Wool/knit scarves flat dry.",
        "sense_check_en": "Eyes: bleed/rings. Hand: no twist.",
        "success_rate_en": "Hand: good. Machine: risky.",
        "refuse_when_en": "Forced machine/bleach on silk scarf → refuse.",
        "must_include_en": "hand wash, flat dry, alone, no harsh bleach",
    }


def _golf_glove_synth() -> dict[str, str]:
    return {
        "precheck_ko": "합성·메시 골프장갑: 손세탁 우선. 기계는 라벨+세탁망 섬세만.",
        "why_ko": "[왜] 합성=찬물·약세제. 유연제·고온건조 금지(그립·접착↓).",
        "fresh_path_ko": "(1)찬물·약세제 손세탁·약하게. (2)또는 망+30℃ 섬세. (3)헹굼. (4)평건. (5)고온건조 금지.",
        "dried_path_ko": "잔여 때: 손세탁 재시도. 건조기 금지.",
        "motion_ko": "Cap2",
        "water_temp_ko": "찬물 / ≤30℃",
        "aftercare_ko": "평건. 완전 건조 후 착용.",
        "sense_check_ko": "손: 끈적임 없음. 눈: 메시 찢김.",
        "success_rate_ko": "손세탁: 양호.",
        "refuse_when_ko": "고온건조·강세제 강제 → 거절.",
        "must_include_ko": "손/망, ≤30℃, 유연제 금지, 고온건조 금지",
        "precheck_vi": "Synthetic/mesh: tay; may chi tui neu nhan.",
        "why_vi": "[Tai sao] Lanh + chat nhe. CAM xa vai. CAM say nong.",
        "fresh_path_vi": "(1)Tay lanh chat nhe. (2)Hoac tui 30C. (3)Xa. (4)Phoi phang. (5)CAM say.",
        "dried_path_vi": "Lap tay. CAM say.",
        "motion_vi": "Cap2",
        "water_temp_vi": "Lanh / <=30C",
        "aftercare_vi": "Phoi phang. CAM say.",
        "sense_check_vi": "Tay: het nhon. Mat: rach mesh.",
        "success_rate_vi": "Tay: tot.",
        "refuse_when_vi": "Bat say nong → tu choi.",
        "must_include_vi": "tay/tui, <=30C, CAM xa vai, CAM say",
        "precheck_en": "Synthetic/mesh golf glove: hand first; machine only mesh bag if labeled.",
        "why_en": "[Why] Cold + mild. No softener/hot dryer (grip/glue).",
        "fresh_path_en": "(1)Hand cold mild gently. (2)Or mesh ≤30°C delicate. (3)Rinse. (4)Flat dry. (5)No hot dryer.",
        "dried_path_en": "Re-hand wash. No dryer.",
        "motion_en": "Cap2.",
        "water_temp_en": "Cold / ≤30°C.",
        "aftercare_en": "Flat dry. Wear fully dry.",
        "sense_check_en": "Hand: no slip. Eyes: mesh tears.",
        "success_rate_en": "Hand: good.",
        "refuse_when_en": "Forced hot dryer/harsh detergent → refuse.",
        "must_include_en": "hand/mesh, ≤30°C, no softener, no hot dryer",
    }


def apply_ops_remainder_hints(graph: dict[str, Any], item_id: str) -> dict[str, Any]:
    if item_id not in OPS_REMAINDER_IDS:
        return graph
    out = dict(graph)
    tools = list(out.get("tools") or [])
    if item_id in {"I_UNDERWEAR", "I_GOLF_GLOVE_SYNTH", "I_SCARF", "I_ACTIVEWEAR"} and not any(
        str(t.get("id")) == "T_MESH_BAG" for t in tools
    ):
        tools.append({
            "id": "T_MESH_BAG",
            "name_ko": "세탁망",
            "name_vi": "Tui luoi",
            "name_en": "Mesh laundry bag",
            "use_for_ko": "섬세·브라·장갑·스카프 기계 시.",
            "use_for_vi": "Bao ve do mong khi may.",
            "use_for_en": "Protect delicates in machine.",
        })
        out["tools"] = tools
    if item_id in {
        "I_CARE_LABEL", "I_INTAKE_SCRIPT", "I_CLAIM_SCRIPT", "I_WATER_HARDNESS",
        "I_COLOR_FADE", "I_WHITE_FADE", "I_KNIT", "I_SCARF", "I_ACTIVEWEAR",
    }:
        out.setdefault("empty_chems_ok", True)
    return out
