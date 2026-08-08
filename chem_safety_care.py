# -*- coding: utf-8 -*-
"""Chem safety mini-cards (ops education) — never-mix / bleach / solvent / acid PPE.

I_* ids (not Chemical codes). Full KO/VI/EN. Truth: seed NEVER_MIX + chem roles.
"""
from __future__ import annotations

from typing import Any

CHEM_SAFETY_IDS = frozenset({
    "I_CHEM_NEVER_MIX",
    "I_CHEM_BLEACH",
    "I_CHEM_SOLVENT",
    "I_CHEM_ACID_PPE",
})


def education_for_chem_safety(item_id: str) -> dict[str, str]:
    return {
        "I_CHEM_NEVER_MIX": _never_mix,
        "I_CHEM_BLEACH": _bleach,
        "I_CHEM_SOLVENT": _solvent,
        "I_CHEM_ACID_PPE": _acid_ppe,
    }.get(item_id, lambda: {})()


def _never_mix() -> dict[str, str]:
    return {
        "precheck_ko": "약품 혼합 금지: 작업대에 열린 약품 2종 이상 두면 사고. 한 번에 하나.",
        "why_ko": (
            "[왜] 염소(B2/Javel)+암모니아(A5)=유독 가스. "
            "산+염소도 위험. ‘집에서 섞어 강하게’ 요구는 거절."
        ),
        "fresh_path_ko": (
            "(1)라벨·코드 확인. (2)B2와 A5 절대 혼합·연속 미헹굼 사용 금지. "
            "(3)한 약품 처리→충분히 헹굼→다음. (4)환기. (5)대사: 「섞으면 가스 — 각각 쓰고 헹굽니다」."
        ),
        "dried_path_ko": "이미 혼합 노출: 즉시 환기·대피·물로 헹굼, 병원. 작업 중단.",
        "motion_ko": "Cap0 — 판단·안전",
        "water_temp_ko": "해당 없음(안전 규칙)",
        "aftercare_ko": "사용한 통·솔 헹궈 분리 보관. 혼합 금지 스티커.",
        "sense_check_ko": "코: 이상 냄새(자극)면 즉시 중단·환기.",
        "success_rate_ko": "규칙 준수=사고↓. 위반=급성 위험.",
        "refuse_when_ko": "락스+암모니아 혼합 요구 → 즉시 거절.",
        "must_include_ko": "B2+A5 금지, 헹굼 후 다음 약, 환기, 혼합 거절",
        "precheck_vi": "CAM pha tron hoa chat. Mot loai mot luc.",
        "why_vi": "[Tai sao] Javel(B2)+ammonia(A5)=khi doc. Acid+chlorine nguy hiem. Tu choi pha tron.",
        "fresh_path_vi": (
            "(1)Doc ma. (2)CAM B2+A5. (3)Xu ly 1 → xa ky → moi dung tiep. "
            "(4)Thong gio. (5)Script: khong pha — xa giua cac buoc."
        ),
        "dried_path_vi": "Da hit hon hop: thong gio, ra ngoai, rua nuoc, den BV. Dung viec.",
        "motion_vi": "Cap0 — an toan",
        "water_temp_vi": "N/A",
        "aftercare_vi": "Rua dung cu. Dan CAM tron.",
        "sense_check_vi": "Mui cay → dung ngay + thong gio.",
        "success_rate_vi": "Tuan thu = an toan.",
        "refuse_when_vi": "Bat tron Javel+ammonia → tu choi.",
        "must_include_vi": "CAM B2+A5, xa giua buoc, thong gio, tu choi tron",
        "precheck_en": "Never mix open chemicals. One product at a time.",
        "why_en": (
            "[Why] Chlorine bleach (B2) + ammonia (A5) = toxic gas. "
            "Acid + chlorine also hazardous. Refuse DIY cocktails."
        ),
        "fresh_path_en": (
            "(1)Read codes. (2)Never B2 with A5. (3)Finish one chem → rinse thoroughly → next. "
            "(4)Ventilate. (5)Script: we do not mix — rinse between steps."
        ),
        "dried_path_en": "Exposure: ventilate, exit, rinse, medical. Stop work.",
        "motion_en": "Cap0 — safety decision.",
        "water_temp_en": "N/A",
        "aftercare_en": "Rinse tools; store separate; never-mix sticker.",
        "sense_check_en": "Sharp smell → stop + ventilate.",
        "success_rate_en": "Compliance prevents acute incidents.",
        "refuse_when_en": "Forced bleach+ammonia mix → refuse immediately.",
        "must_include_en": "no B2+A5, rinse between, ventilate, refuse mix",
    }


def _bleach() -> dict[str, str]:
    return {
        "precheck_ko": "표백: B1=산소(유색 신중), B2=염소(흰 면만). 케어라벨 삼각형 확인.",
        "why_ko": "[왜] B2는 흰 면만. 유색·울·실크·단백질 얼룩에 염소=탈색·손상. B1도 울/실크 금지.",
        "fresh_path_ko": (
            "(1)라벨 삼각형. (2)흰 면만 B2 희석. (3)유색=B1 또는 금지. "
            "(4)단백질 얼룩에 뜨거운 염소 금지. (5)사용 후 충분히 헹굼. (6)A5와 혼합 금지."
        ),
        "dried_path_ko": "이미 탈색: 복원 불가 고지. 추가 염소 금지.",
        "motion_ko": "Cap0–1 균일 담금(점 찍기 금지)",
        "water_temp_ko": "제품 라벨; 보통 미온~권장",
        "aftercare_ko": "헹굼 확인. 잔여 염소=황변·손상.",
        "sense_check_ko": "눈: 균일. 코: 잔여 자극 시 재헹굼.",
        "success_rate_ko": "흰 면+라벨 OK: 양호. 유색 염소: 사고.",
        "refuse_when_ko": "유색·실크·울에 B2 요구 → 거절.",
        "must_include_ko": "B2=흰 면만, B1≠울/실크, A5 혼합 금지, 헹굼",
        "precheck_vi": "B1 oxy (mau than), B2 Javel (CHI cotton trang). Doc tam giac nhan.",
        "why_vi": "[Tai sao] B2 chi trang. Mau/len/lua + Javel = hong. B1 CAM len/lua.",
        "fresh_path_vi": (
            "(1)Doc nhan. (2)B2 pha CHI cotton trang. (3)Mau = B1/cam. "
            "(4)CAM Javel nong len protein. (5)Xa ky. (6)CAM tron A5."
        ),
        "dried_path_vi": "Da mat mau: bao khong phuc. CAM them Javel.",
        "motion_vi": "Cap0-1 ngam deu",
        "water_temp_vi": "Theo nhan san pham",
        "aftercare_vi": "Xa ky. Con clo = hong.",
        "sense_check_vi": "Mat: deu. Mui cay → xa lai.",
        "success_rate_vi": "Trang+nhan OK: tot. Javel mau: tai nan.",
        "refuse_when_vi": "Bat B2 mau/lua/len → tu choi.",
        "must_include_vi": "B2 chi trang, B1 CAM len/lua, CAM A5, xa ky",
        "precheck_en": "B1 oxygen (colors careful), B2 chlorine (white cotton ONLY). Read triangle symbol.",
        "why_en": "[Why] B2 whites only. Chlorine on color/wool/silk/protein = damage. B1 also banned on wool/silk.",
        "fresh_path_en": (
            "(1)Label triangle. (2)Dilute B2 white cotton only. (3)Colors=B1 or none. "
            "(4)No hot chlorine on protein stains. (5)Rinse well. (6)Never mix A5."
        ),
        "dried_path_en": "Already bleached uneven: no restore; stop more chlorine.",
        "motion_en": "Cap0–1 even soak (no spot-dot).",
        "water_temp_en": "Per product label.",
        "aftercare_en": "Confirm rinse. Chlorine residue yellows/damages.",
        "sense_check_en": "Eyes: even. Sharp smell → re-rinse.",
        "success_rate_en": "White cotton+label: good. Chlorine on color: incident.",
        "refuse_when_en": "Forced B2 on color/silk/wool → refuse.",
        "must_include_en": "B2 white cotton only, B1≠wool/silk, no A5 mix, rinse",
    }


def _solvent() -> dict[str, str]:
    return {
        "precheck_ko": "솔벤트(A1 알코올·A2 아세톤·D1): 환기·화기 금지. 레이온/아세테이트에 아세톤 금지.",
        "why_ko": "[왜] 증기=흡입·화재. 아세톤은 일부 합성·장식 녹임. PPE·소량·국소.",
        "fresh_path_ko": (
            "(1)환기·불꽃 금지. (2)원단 테스트(안쪽). (3)천에 묻혀 국소 Cap1. "
            "(4)A2: 레이온·아세테이트·일부 플라스틱 금지. (5)잔여 중성 세제·헹굼."
        ),
        "dried_path_ko": "원단 녹음·광택 손상: 중단·고지.",
        "motion_ko": "Cap1 국소. 담금 금지",
        "water_temp_ko": "상온·환기",
        "aftercare_ko": "환기 유지. 뚜껑 밀폐 보관.",
        "sense_check_ko": "눈: 원단 손상. 코: 과다 증기면 중단.",
        "success_rate_ko": "국소+테스트: 중간~양호. 무환기 담금: 위험.",
        "refuse_when_ko": "밀폐 공간 대량 사용·아세톤 레이온 → 거절.",
        "must_include_ko": "환기, 패치 테스트, A2≠레이온, 국소만",
        "precheck_vi": "A1/A2/D1: thong gio, CAM lua. CAM acetone tren rayon/acetate.",
        "why_vi": "[Tai sao] Hoi doc/chay. Acetone tan mot so vai/nhua. PPE + cuc bo.",
        "fresh_path_vi": (
            "(1)Thong gio. (2)Test goc. (3)Cham tren khan Cap1. "
            "(4)A2 CAM rayon/acetate. (5)Trung tinh + xa."
        ),
        "dried_path_vi": "Tan/hong bong: dung, bao.",
        "motion_vi": "Cap1 cuc bo; CAM ngam",
        "water_temp_vi": "Phong + thong gio",
        "aftercare_vi": "Giu nap. Thong gio.",
        "sense_check_vi": "Mat: hong vai. Mui nang → dung.",
        "success_rate_vi": "Test+cuc bo: TB-tot. Ngam kin: nguy.",
        "refuse_when_vi": "Bat A2 rayon / kin khi → tu choi.",
        "must_include_vi": "thong gio, test, A2 CAM rayon, cuc bo",
        "precheck_en": "Solvents A1/A2/D1: ventilate, no flame. No acetone on rayon/acetate.",
        "why_en": "[Why] Vapor = inhalation/fire risk. Acetone melts some synthetics/trim. PPE + spot only.",
        "fresh_path_en": (
            "(1)Ventilate; no flame. (2)Hidden patch test. (3)On cloth Cap1 spot. "
            "(4)A2 banned on rayon/acetate/some plastics. (5)Mild soap + rinse residue."
        ),
        "dried_path_en": "Melt/shine loss: stop; disclose.",
        "motion_en": "Cap1 spot. No soak.",
        "water_temp_en": "Ambient + ventilation.",
        "aftercare_en": "Keep lids closed. Keep ventilating.",
        "sense_check_en": "Eyes: fabric damage. Heavy vapor → stop.",
        "success_rate_en": "Tested spot: fair–good. Closed-room soak: dangerous.",
        "refuse_when_en": "Forced acetone on rayon / unventilated flood → refuse.",
        "must_include_en": "ventilate, patch test, A2≠rayon, spot only",
    }


def _acid_ppe() -> dict[str, str]:
    return {
        "precheck_ko": "산·강알칼리(A3 식초·A5 암모니아·X2 옥살산 등): 장갑·눈 보호. 원단 안전 확인.",
        "why_ko": "[왜] 산/알칼리는 피부·눈·일부 섬유 손상. X2는 특히 주의. 사용 후 중성화·헹굼.",
        "fresh_path_ko": (
            "(1)니트릴 장갑·환기. (2)희석비 준수(예 A3 1:4). (3)울/실크에 강한 산 금지. "
            "(4)처리 후 충분히 헹굼. (5)B2와 절대 혼합 금지."
        ),
        "dried_path_ko": "피부/눈 접촉: 물로 15분+의료. 원단 손상 고지.",
        "motion_ko": "Cap0–1. 튀 금지",
        "water_temp_ko": "희석액 상온",
        "aftercare_ko": "장갑 폐기/세척. 잔여 산 헹굼 확인.",
        "sense_check_ko": "손: 미끄러움·자극 없으면 헹굼 OK.",
        "success_rate_ko": "PPE+희석: 안전. 원액·무PPE: 사고.",
        "refuse_when_ko": "원액 피부 도포·무장갑 요구 → 거절.",
        "must_include_ko": "장갑·환기, 희석, 울/실크 주의, B2 혼합 금지",
        "precheck_vi": "A3/A5/X2: gang tay + bao mat. Kiem an toan vai.",
        "why_vi": "[Tai sao] Acid/ki → da/mat/vai. X2 than. Sau xu ly: xa / trung hoa.",
        "fresh_path_vi": (
            "(1)Gang nitrile + thong gio. (2)Pha dung (A3 1:4). (3)CAM acid manh len/lua. "
            "(4)Xa ky. (5)CAM tron B2."
        ),
        "dried_path_vi": "Dinh da/mat: rua 15 phut + y te. Bao hong vai.",
        "motion_vi": "Cap0-1; CAM vung",
        "water_temp_vi": "Pha o nhiet phong",
        "aftercare_vi": "Rua gang. Kiem het acid.",
        "sense_check_vi": "Tay: het tron/kich → xa OK.",
        "success_rate_vi": "PPE+pha: an toan. Nguyen chat: nguy.",
        "refuse_when_vi": "Bat bo gang / bo nguyen chat → tu choi.",
        "must_include_vi": "gang+thong gio, pha dung, than len/lua, CAM B2",
        "precheck_en": "Acids/alkalis (A3/A5/X2…): gloves + eye protection. Check fabric safety.",
        "why_en": "[Why] Skin/eye/fiber damage. X2 especially careful. Rinse/neutralize after.",
        "fresh_path_en": (
            "(1)Nitrile gloves + ventilate. (2)Follow dilution (e.g. A3 1:4). "
            "(3)No strong acid on wool/silk. (4)Rinse well. (5)Never mix B2."
        ),
        "dried_path_en": "Skin/eye contact: 15 min water + medical. Disclose fiber damage.",
        "motion_en": "Cap0–1. No splash.",
        "water_temp_en": "Ambient dilution.",
        "aftercare_en": "Wash/dispose gloves. Confirm acid gone.",
        "sense_check_en": "Hand: no slip/irritation → rinse OK.",
        "success_rate_en": "PPE+dilution: safe. Neat/no PPE: incident.",
        "refuse_when_en": "Forced neat on skin / no gloves → refuse.",
        "must_include_en": "gloves+ventilate, dilute, wool/silk caution, no B2 mix",
    }


def apply_chem_safety_hints(graph: dict[str, Any], item_id: str) -> dict[str, Any]:
    if item_id not in CHEM_SAFETY_IDS:
        return graph
    out = dict(graph)
    tools = list(out.get("tools") or [])
    if not any(str(t.get("id")) == "T_GLOVE_NITRILE" for t in tools):
        tools.append({
            "id": "T_GLOVE_NITRILE",
            "name_ko": "니트릴 장갑",
            "name_vi": "Gang nitrile",
            "name_en": "Nitrile gloves",
            "use_for_ko": "산·알칼리·솔벤트 PPE.",
            "use_for_vi": "PPE acid/ki/dung moi.",
            "use_for_en": "PPE for acid/alkali/solvent.",
        })
    out["tools"] = tools
    out.setdefault("empty_chems_ok", True)
    return out


_CHEM_META = {
    "I_CHEM_NEVER_MIX": ("Chemical never-mix rules", "Cam pha tron hoa chat", "약품 혼합 금지", "F1"),
    "I_CHEM_BLEACH": ("Bleach safety (B1/B2)", "An toan tay (B1/B2)", "표백 안전(B1/B2)", "F1"),
    "I_CHEM_SOLVENT": ("Solvent safety (A1/A2/D1)", "An toan dung moi", "솔벤트 안전(A1/A2/D1)", "F1"),
    "I_CHEM_ACID_PPE": ("Acid/alkali PPE", "PPE acid/ki", "산·알칼리 PPE", "F1"),
}


def chem_seed_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for iid, (name, name_vi, name_ko, fid) in _CHEM_META.items():
        edu = education_for_chem_safety(iid)
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
