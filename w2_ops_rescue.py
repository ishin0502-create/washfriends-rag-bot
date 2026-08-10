# -*- coding: utf-8 -*-
"""W2: ops drills, rescue 2nd-pass, aftercare force, dilution gaps.

Accuracy: checklist only — no invented chemistry. Minutes/ratios from existing SOPs.
"""
from __future__ import annotations

# ── Dilution gaps (synced with education_gaps_v7 / V_chem / CHEM_META) ────────
try:
    from education_gaps_v7 import DILUTION_V7 as _DV7

    DILUTION_GAPS = [
        {"code": d["code"], "dilution_vi": d["dilution_vi"], "dilution_ko": d["dilution_ko"]}
        for d in _DV7
    ]
except Exception:
    DILUTION_GAPS = []

# WF supply dilutions (not in CHEM stain path; keep for seed/V_chem parity)
_WF_DILUTION = [
    {
        "code": "WF_SOFT",
        "dilution_vi": "Theo chai Softener Wash Friends — chi buoc xa/hoan thien, khong xu ly vet",
        "dilution_ko": "워시프렌즈 유연제 병 안내 — 헹굼·마감만, 얼룩 처리에 쓰지 말 것",
    },
    {
        "code": "WF_FRAG",
        "dilution_vi": "Xit nhe 1-2 phat theo chai — khong ngap; sau khi do kho/sach",
        "dilution_ko": "병 안내대로 1–2회만 약하게 — 흠뻑 금지; 건조·청결 후",
    },
]
_gap_codes = {d["code"] for d in DILUTION_GAPS}
for _row in _WF_DILUTION:
    if _row["code"] not in _gap_codes:
        DILUTION_GAPS.append(_row)

# ── Ops decision drills (question → judge → script → refuse) ─────────────────
OPS_DRILLS = {
    "I_CARE_LABEL": {
        "why_ko": "[왜 이 순서] 케어라벨=원단과의 계약. 기호를 추측하지 말 것. (1)물세탁 기호(숫자=최고℃, 손=손세탁, X=물세탁 금지) (2)표백 삼각형(빈=가능, 사선=산소만, X=표백 금지) (3)건조 사각형 (4)다리미 점 (5)원형=드라이. X가 있으면 그 항목은 절대 위반 금지.",
        "fresh_path_ko": "(1)질문: 라벨이 보이는가? 흐리면 사진. (2)판단: 5그룹 기호를 적어 최고온도·표백·건조·다림질·드라이 여부를 확정. (3)대사: 「라벨 기준 ○℃까지, 표백 ○, 건조 ○입니다」. (4)금지: 기호 X를 무시하고 물세탁/표백/건조기. 라벨 없음→보수(찬물·표백 금지) + 고객 고지.",
        "dried_path_ko": "이미 라벨 무시 세탁: 추가 강한 처리 중단, 손상 여부 사진·고지, 필요 시 전문.",
        "aftercare_ko": "라벨 자르지 말 것. 접수 전표에 읽은 기호 요약 기입.",
        "sense_check_ko": "눈: 5그룹 기호 모두 확인. 손: 라벨 파손 여부.",
        "success_rate_ko": "라벨 선명: 판단 확실. 흐리거나 잘림: 보수 경로만.",
        "refuse_when_ko": "X(물/표백/건조)인데 고객이 강제 요구 → 거절·손해 고지. 추측 해석 금지.",
        "why_vi": "[Tại sao] Nhan = hop dong. Khong doan ky hieu. 5 nhom: giat / tay / say / ui / dry-clean. Co X → TUAN THU.",
        "fresh_path_vi": "(1)Hoi: nhan ro? (2)Doc 5 nhom, ghi max C + bleach + say + ui + dry. (3)Noi khach dung theo nhan. (4)CAM bo qua X. Nhan mat → an toan thap + bao.",
        "aftercare_vi": "Khong cat nhan. Ghi tom tat ky hieu tren phieu.",
        "sense_check_vi": "Mat: du 5 nhom. Tay: nhan khong rach.",
        "success_rate_vi": "Nhan ro: cao. Mo/mat: chi duong an toan.",
        "refuse_when_vi": "Khach bat bat chap X → tu choi + bao rui ro.",
    },
    "I_DRY_VS_WET": {
        "why_ko": "[왜 이 순서] 물세탁 vs 드라이는 라벨 우선. X 물통/드라이 기호 P·F → 드라이·전문. 물세탁 OK: 라벨 허용 면·폴리, 수건·시트. 거절/전문: 진모피, 민감 가죽, 고가 실크, 캔버스 정장. 다운은 약한 물세탁 우선(퍼크 주의).",
        "fresh_path_ko": "(1)질문: 라벨에 물 X / 드라이 표시? 품목(정장·한복·아오자이·다운·가죽)? (2)판단: X 물이면 드라이. 정장·고가 실크→드라이 우선. 다운→온화 물세탁·대형기. (3)대사: 「이 라벨/구조는 ○○가 안전합니다」. (4)금지: 불확실한데 세탁기 강코스.",
        "dried_path_ko": "이미 잘못 물세탁(실크 등): 추가 강처리 중단, 고객 고지, 전문 상담.",
        "aftercare_ko": "전표에 물/드라이 선택 이유 기록.",
        "sense_check_ko": "눈: 라벨·구조 확인. 기록: 선택 사유.",
        "success_rate_ko": "라벨 명확: 높음. 라벨 없음·복합 구조: 중간 — 보수 선택.",
        "refuse_when_ko": "진모피·민감 가죽·캔버스 정장 가정 세탁 강제 → 거절.",
        "why_vi": "[Tại sao] Uu tien nhan. X chau → dry. Suit/silk dat → dry. Down → wet mild. Fur/leather → spot/chuyen.",
        "fresh_path_vi": "(1)Hoi nhan + loai do. (2)X nuoc → dry. (3)Noi ro wet hay dry. (4)CAM may manh khi khong chac.",
        "aftercare_vi": "Ghi ly do wet/dry tren phieu.",
        "sense_check_vi": "Mat: nhan/cau truc. Phieu: ly do.",
        "success_rate_vi": "Nhan ro: cao. Khong nhan: trung binh.",
        "refuse_when_vi": "Fur that / da / suit canvas bat giat nha → tu choi.",
    },
    "I_INTAKE_SCRIPT": {
        "why_ko": "[왜 이 순서] 접수=법적·클레임 방어. 필수: 인사→수량·기존 하자 기록→전체+클로즈업 사진→요금·기간 고지→전표 2부 서명. 마른·고착 얼룩은 「100% 불가 가능」 사전 동의. 사진 없이 접수=분쟁 위험.",
        "fresh_path_ko": "(1)질문 체크: 몇 점? 기존 찢김·탈색? 얼룩 신선/마름? (2)판단: 위험 태그(실크·울·빈티지) 부착 여부. (3)대사: 「사진·전표 남기고, 마른 얼룩은 100% 보장 어렵습니다. 동의하시면 진행합니다」. (4)금지: 사진·서명 없이 접수, 성공 100% 약속.",
        "dried_path_ko": "클레임: 접수 사진과 대조 → 매장 과실이면 사과·보상안 / 기존 하자면 사진 제시.",
        "aftercare_ko": "사진·전표 보관. Zalo 문의는 사진 있으면 2시간 내 응답 목표.",
        "sense_check_ko": "눈: 사진 2장 이상. 손: 전표 서명. 코/기록: 위험 고지 문구.",
        "success_rate_ko": "사진+서명 완료: 분쟁 방어 양호. 미촬영: 위험.",
        "refuse_when_ko": "100% 보장 요구·사진 거부 → 접수 거절 또는 서면 동의 후에만.",
        "why_vi": "[Tại sao] Anh + chu ky bat buoc. Vet kho: bao truoc khong 100%. Khong anh = rui ro kien.",
        "fresh_path_vi": "(1)Dem+ghi. (2)Chup tong+close-up. (3)Bao gia/thoi gian. (4)Phieu 2 ban. (5)Vet kho: xin dong y. (6)CAM nhan khong anh.",
        "aftercare_vi": "Luu anh+phieu. Zalo <2h neu co anh.",
        "sense_check_vi": "Mat: >=2 anh. Tay: chu ky. Phieu: canh bao vet kho.",
        "success_rate_vi": "Du anh+ky: tot. Thieu anh: rui ro cao.",
        "refuse_when_vi": "Doi 100% / tu choi anh → tu choi nhan hoac chi khi co van ban.",
    },
    "I_WATER_HARDNESS": {
        "why_ko": "[왜 이 순서] 경수(Ca/Mg)=세제 거품↓·때·스케일·흰옷 황변. 보정: (1)세제 한 단계↑ 또는 경수용 (2)추가 헹굼 (3)선택: 식초 1:4 최종 헹굼 (4)정기 통세척. 유연제로 헹굼 부족을 대신하지 말 것(수건 흡수력↓).",
        "fresh_path_ko": "(1)질문: 거품 적음? 빨래 뻣뻣? 흰옷 누렇게? 지역(하노이 등)? (2)판단: 경수 의이면 세제+1·추가 헹굼. (3)대사: 「수돗물이 센 편이라 세제·헹굼을 보정합니다」. (4)금지: 유연제만 늘려 경수 해결, 단백질 황변에 락스.",
        "dried_path_ko": "이미 뻣뻣/스케일: 재헹굼+식초 약희석. 세탁조: 식초/구연산 청소(라벨 허용 시).",
        "aftercare_ko": "지역·경수 보정 전표 메모. 수건은 유연제 과다 금지.",
        "sense_check_ko": "손: 뻣뻣함 감소. 눈: 흰옷 황변·스케일. 거품: 적정.",
        "success_rate_ko": "보정 적용: 양호. 방치 시 재발.",
        "refuse_when_ko": "락스로 경수 황변 해결 요구(단백질/유색) → 거절.",
        "why_vi": "[Tại sao] Nuoc cung → tang bot + xa them + A3 xa cuoi tuy chon + ve sinh may. Khong thay bang softener.",
        "fresh_path_vi": "(1)Nhan dau hieu. (2)Bot +1, extra rinse. (3)A3 xa nhe neu can. (4)CAM dung softener thay rinse.",
        "aftercare_vi": "Ghi khu vuc. Khan: it softener.",
        "sense_check_vi": "Tay: het cang. Mat: bot/vang.",
        "success_rate_vi": "Bu dung: tot. Bo qua: tai phat.",
        "refuse_when_vi": "Doi Javel tri vang protein/mau → tu choi.",
    },
    "I_MACHINE_PROFILE": {
        "why_ko": "[왜 이 순서] 코스=원단·라벨 따름. 얼룩은 건조 전 제거(열=고착). 면=표준, 실크·울·얇음=섬세, 수건/침구=고온 가능 시, 기능성=냄새 코스. 건조: 수건 고온·면 중온·폴리 저온·실크/울/스판/아오자이/가죽=건조기 금지. 불확실=섬세+자연건조.",
        "fresh_path_ko": "(1)질문: 원단·라벨·얼룩 잔여? (2)판단: 코스 선택 + 경수면 세제 보정. (3)대사: 「○○ 코스, 건조 전 강광 확인합니다」. (4)금지: 잔여 얼룩 상태로 건조기, 실크·울 건조기.",
        "dried_path_ko": "잔여 세제: 재헹굼. 구김: 약한 스팀(라벨 허용).",
        "aftercare_ko": "세탁/건조 직후 꺼내기. 필터·통 정기 청소. 건조 전 강광 잔여 확인.",
        "sense_check_ko": "눈: 건조 전 강광. 손: 세제 잔여 없음. 코: 이취 없음.",
        "success_rate_ko": "라벨+잔여 확인 후 건조: 높음. 성급 건조: 열고착 위험.",
        "refuse_when_ko": "실크·울·가죽 건조기 강제 → 거절.",
        "why_vi": "[Tại sao] Chon chuong trinh theo vai. Kiem vet TRUOC say. CAM say len/lua/spandex/da.",
        "fresh_path_vi": "(1)Hoi vai+nhan. (2)Chon chuong trinh. (3)Kiem anh sang truoc say. (4)CAM say khi con vet.",
        "aftercare_vi": "Lay do ngay. Ve sinh phin. Anh sang truoc say.",
        "sense_check_vi": "Mat: het vet truoc say. Tay: het bot.",
        "success_rate_vi": "Kiem truoc say: cao. Say som: khoa vet.",
        "refuse_when_vi": "Bat say len/lua/da → tu choi.",
    },
}

# Process-stage drills — keep in sync via process_stage_care (full KO/VI/EN).
try:
    from process_stage_care import PROCESS_STAGE_IDS, education_for_process

    for _pid in sorted(PROCESS_STAGE_IDS):
        _edu = education_for_process(_pid)
        if _edu:
            OPS_DRILLS[_pid] = {
                k: v
                for k, v in _edu.items()
                if k.startswith(
                    (
                        "why_",
                        "fresh_path_",
                        "dried_path_",
                        "aftercare_",
                        "sense_check_",
                        "success_rate_",
                        "refuse_when_",
                        "precheck_",
                        "must_include_",
                    )
                )
            }
except Exception:
    pass

# Chem-safety drills — full KO/VI/EN from chem_safety_care.
try:
    from chem_safety_care import CHEM_SAFETY_IDS, education_for_chem_safety

    for _cid in sorted(CHEM_SAFETY_IDS):
        _cedu = education_for_chem_safety(_cid)
        if _cedu:
            OPS_DRILLS[_cid] = {
                k: v
                for k, v in _cedu.items()
                if k.startswith(
                    (
                        "why_",
                        "fresh_path_",
                        "dried_path_",
                        "aftercare_",
                        "sense_check_",
                        "success_rate_",
                        "refuse_when_",
                        "precheck_",
                        "must_include_",
                    )
                )
            }
except Exception:
    pass

# Remaining tip-only ops/clothing — full cards from specialty_ops_remainder_care.
try:
    from specialty_ops_remainder_care import OPS_REMAINDER_IDS, education_for_ops_remainder

    for _rid in sorted(OPS_REMAINDER_IDS):
        if _rid in OPS_DRILLS:
            continue  # keep existing care/intake/water/machine drills if already present
        _redu = education_for_ops_remainder(_rid)
        if _redu:
            OPS_DRILLS[_rid] = {
                k: v
                for k, v in _redu.items()
                if k.startswith(
                    (
                        "why_",
                        "fresh_path_",
                        "dried_path_",
                        "aftercare_",
                        "sense_check_",
                        "success_rate_",
                        "refuse_when_",
                        "precheck_",
                        "must_include_",
                    )
                )
            }
except Exception:
    pass

AFTERCARE_FORCE_KO = (
    "건조·다림질 전 강광으로 잔여 확인. 얼룩·미끄럼·냄새 남은 채 열을 가하면 열고착."
)
AFTERCARE_FORCE_VI = (
    "Ánh sáng mạnh TRƯỚC sấy/ủi. Còn vết/nhờn/mùi mà sấy = khóa vết."
)
AFTERCARE_FORCE_EN = (
    "Strong-light check BEFORE dry/iron. Heat with residue sets the stain."
)

# Overlay unsigned VI ops drills with diacritic canon (education_parity_v5).
try:
    from education_parity_v5 import OPS_VI_CANON

    for _oid, _fields in OPS_VI_CANON.items():
        if _oid in OPS_DRILLS:
            OPS_DRILLS[_oid].update(_fields)
except Exception:
    pass

try:
    from education_gaps_v7 import OPS_DRILLS_V7

    OPS_DRILLS.update(OPS_DRILLS_V7)
except Exception:
    pass

RESCUE_BY_GROUP = {
    "G1": {
        "ko": "2차: 찬물 재확인 → 효소 농도·시간↑(원단 허용 시, 실크·울 금지) → 흰 면만 과산화/산소 검토. 고객에 성공률↓ 고지.",
        "vi": "Lần 2: xả lạnh lại → tăng enzyme (không len/lụa) → oxy/A4 chỉ cotton trắng. Báo tỷ lệ thấp.",
        "en": "2nd: re-rinse cold → longer enzyme if fabric allows → oxygen only on white cotton. Disclose lower odds.",
    },
    "G2": {
        "ko": "2차: 전분 흡착 재실시 → 주방세제/용제(환기) 반복 → 미끄럼 없어진 뒤에만 건조. 이미 열고착이면 성공률 낮음 고지.",
        "vi": "Lần 2: N3 lại → D2/D1 (thông gió) lặp → hết nhờn mới sấy. Đã khóa nhiệt: báo thấp.",
        "en": "2nd: re-absorb powder → repeat surfactant/solvent (ventilate) → dry only when not greasy. Heat-set = low odds.",
    },
    "G3": {
        "ko": "2차: 식초 1:4 재침지 → 흰/면만 산소표백(실크·울 금지) → 건조 전 강광. 이미 건조·고착 색소면 100% 비보장.",
        "vi": "Lần 2: A3 1:4 lại → B1 chỉ trắng/cotton → ánh sáng trước sấy. Đã khóa: không 100%.",
        "en": "2nd: vinegar 1:4 again → oxygen on white cotton only → strong light before dry. Set dye = no 100%.",
    },
    "G4": {
        "ko": "2차: 안쪽 블롯만 반복(문지르기 금지) → 구석 테스트 후 용제 → 실패 시 중단·전문. 100% 비보장.",
        "vi": "Lần 2: blot mặt trái lặp → dung môi sau test → fail thì dừng/chuyên. Không 100%.",
        "en": "2nd: blot reverse only → solvent after corner test → stop/refer if failing. No 100%.",
    },
    "G5": {
        "ko": "2차: fresh_path 성분별 순서를 한 바퀴 더(단계마다 헹굼) → 안 되면 전문 의. 혼합 칵테일 금지.",
        "vi": "Lần 2: lặp từng lớp theo fresh_path, xả giữa bước → không được thì chuyên. CẤM pha cocktail.",
        "en": "2nd: one more pass per fresh_path layer with rinses → else refer. No chemical cocktails.",
    },
}


def rescue_card_for_stain(sc: dict) -> dict:
    sid = str(sc.get("id") or "").strip()
    stain_card = None
    try:
        from education_parity_v5 import RESCUE_BY_STAIN, RESCUE_DISCLOSE_VI_CANON

        stain_card = RESCUE_BY_STAIN.get(sid)
        disclose_vi = RESCUE_DISCLOSE_VI_CANON
    except Exception:
        disclose_vi = (
            "Lan 1 that bai/vet kho: bao ty le thap truoc khi lam lan 2. CAM hua 100%."
        )
    if not stain_card:
        try:
            from education_gaps_v7 import RESCUE_CHILI, RESCUE_IODINE

            if sid == "S_IODINE":
                stain_card = RESCUE_IODINE
            elif sid == "S_CHILI":
                stain_card = RESCUE_CHILI
        except Exception:
            pass
    if not stain_card:
        try:
            from education_gaps_v8 import RESCUE_BY_STAIN_V8

            stain_card = RESCUE_BY_STAIN_V8.get(sid)
        except Exception:
            pass
    if not stain_card:
        try:
            from education_dried_parity_v11 import rescue_for_stain

            stain_card = rescue_for_stain(sid)
        except Exception:
            pass

    gid = ""
    grp = sc.get("group_id") or sc.get("group")
    if isinstance(grp, dict):
        gid = str(grp.get("id") or "")
    elif isinstance(grp, str):
        gid = grp
    if gid not in RESCUE_BY_GROUP:
        if sc.get("contains_tannin"):
            gid = "G3"
        elif sc.get("contains_oil") and not sc.get("contains_protein"):
            gid = "G2"
        elif sc.get("contains_protein") and not sc.get("contains_tannin"):
            gid = "G1"
        elif sc.get("contains_dye"):
            gid = "G4"
        else:
            gid = "G5"
    group_card = RESCUE_BY_GROUP[gid]
    card = stain_card or group_card
    dried_ko = (sc.get("dried_path_ko") or "").strip()
    dried_vi = (sc.get("dried_path_vi") or "").strip()
    return {
        "rescue_2nd_ko": (dried_ko + " / " if dried_ko else "") + card["ko"],
        "rescue_2nd_vi": (dried_vi + " / " if dried_vi else "") + card["vi"],
        "rescue_2nd_en": card["en"],
        "rescue_disclose_ko": "1차 실패·마른 얼룩: 성공률 하락·잔여 가능을 고지한 뒤에만 2차 진행. 100% 약속 금지.",
        "rescue_disclose_vi": disclose_vi,
        "rescue_disclose_en": "After 1st fail/dried stain: disclose lower odds before 2nd pass. Never promise 100%.",
    }


def ops_seed_rows():
    rows = []
    for iid, fields in OPS_DRILLS.items():
        row = {"id": iid}
        row.update(fields)
        rows.append(row)
    return rows
