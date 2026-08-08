# -*- coding: utf-8 -*-
"""Process-stage education: sort / rinse / QC-handover (franchise ops).

Full KO / VI / EN cards. Keep language fields parallel — sanitize picks one lang.
Do not invent chemistry; checklist + decision scripts only.
"""
from __future__ import annotations

from typing import Any

PROCESS_STAGE_IDS = frozenset({
    "I_SORT",
    "I_RINSE",
    "I_QC_HANDOVER",
})


def education_for_process(item_id: str) -> dict[str, str]:
    if item_id == "I_SORT":
        return _sort()
    if item_id == "I_RINSE":
        return _rinse()
    if item_id == "I_QC_HANDOVER":
        return _qc_handover()
    return {}


def _sort() -> dict[str, str]:
    return {
        "precheck_ko": (
            "세탁물 분류(Sort): 세탁기·담금통에 넣기 전. "
            "수량 세기 → 흰/밝은/진한 유색 → 섬세(실크·울·레이온) → 수건·이불 → "
            "바이오해저드(구토·분변·혈액) 별도. 사진·전표는 접수 스크립트와 함께."
        ),
        "why_ko": (
            "[왜 이 순서] 분류 실패=이염·냄새·세균 교차의 출발점. "
            "흰옷+진한 유색 첫 세탁=이염 사고. 수건·심한 오염+일반 의류=냄새 전이. "
            "섬세는 기계 강코스와 같이 돌리면 손상. "
            "분류는 얼룩 제거보다 먼저 — 잘못 섞이면 전처리 성공해도 클레임."
        ),
        "fresh_path_ko": (
            "(1)전체 수량·품목 확인(접수 사진과 대조). "
            "(2)바구니 5칸 기준 — "
            "A 흰·아주 밝은 면/폴리; "
            "B 유색·진한 색(청·검정·빨강); "
            "C 섬세(실크·울·레이온·넥타이·아오자이/한복); "
            "D 수건·시트·이불(흡수·보풀); "
            "E 바이오해저드·심한 냄새(구토·분변·혈액) — PPE·별도 담금. "
            "(3)데님·새 유색은 첫 1–2회 B에서 단독 또는 유사 색만. "
            "(4)속옷·아기옷은 일반 유색과 섞지 말고 위생 우선(고온 가능 시). "
            "(5)지퍼 올리고 뒤집기·주머니 확인. "
            "(6)분류 후 칸별 전처리·코스 선택. "
            "(7)대사: 「흰옷·유색·섬세·수건을 나눠 돌립니다 — 이염·냄새 방지입니다」."
        ),
        "dried_path_ko": (
            "이미 같이 돌려 이염: 즉시 분리·건조 금지 → 이염(S_DYE_TRANSFER) 경로. "
            "냄새 전이: 추가 헹굼·식초 약희석 후 재분류."
        ),
        "motion_ko": "Cap0 — 분류·판단. 오염물만 PPE Cap0–1.",
        "water_temp_ko": "해당 없음(분류 단계). 칸별 코스에서 결정.",
        "aftercare_ko": "전표에 분류 메모(흰/유색/섬세/별도). 이염 위험 품목은 고객 고지.",
        "sense_check_ko": "눈: 칸 섞임 없음. 코: 바이오해저드 분리. 기록: 수량 일치.",
        "success_rate_ko": "분류 준수: 이염·교차오염↓. 무시: 사고↑.",
        "refuse_when_ko": "흰+진한 유색 강제 혼합, 바이오해저드+일반 혼합 요구 → 거절·고지.",
        "must_include_ko": "흰/유색/섬세 분리, 수건·바이오해저드 별도, 이염 예방",
        "precheck_vi": (
            "Phan loai do giat TRUOC khi cho may/ngam. "
            "Dem so → trang/sang / mau dam → mong manh (lua/len) → khan/chan → "
            "biohazard (non/phan/mau) rieng. Anh+phieu kem tiep nhan."
        ),
        "why_vi": (
            "[Tai sao] Sai phan loai = loang mau + mui + cheo nhiem. "
            "Trang + mau dam lan dau = rui ro loang. Khan/do ban + ao thuong = mui. "
            "Do mong + chuong trinh manh = hong. Phan loai truoc xu ly vet."
        ),
        "fresh_path_vi": (
            "(1)Dem + doi anh phieu. "
            "(2)5 gio — "
            "A trang/sang; B mau dam (jean/den/do); "
            "C mong (lua/len/rayon/ca vat/ao dai/hanbok); "
            "D khan/ga/chan; "
            "E biohazard + mui nang — PPE, ngam rieng. "
            "(3)Denim/mau moi: 1–2 lan rieng hoac cung sac. "
            "(4)Do be / do lot: uu tien ve sinh, khong tron lung tung. "
            "(5)Keo khoa, lat trai, kiem tui. "
            "(6)Roi moi spot + chon chuong trinh theo gio. "
            "(7)Noi khach: tach trang/mau/mong/khan de tranh loang mau va mui."
        ),
        "dried_path_vi": (
            "Da giat chung bi loang: tach ngay, CAM say → S_DYE_TRANSFER. "
            "Mui cheo: xa them + A3 nhe, phan loai lai."
        ),
        "motion_vi": "Cap0 — phan loai. Biohazard: PPE.",
        "water_temp_vi": "N/A o buoc phan loai.",
        "aftercare_vi": "Ghi phieu: trang/mau/mong/rieng. Bao rui ro loang neu can.",
        "sense_check_vi": "Mat: khong tron gio. Mui: biohazard rieng. So luong khop.",
        "success_rate_vi": "Dung phan loai: giam loang. Bo qua: rui ro cao.",
        "refuse_when_vi": "Bat tron trang+mau dam / biohazard+ao thuong → tu choi.",
        "must_include_vi": "tach trang/mau/mong, khan+biohazard rieng, phong loang mau",
        "precheck_en": (
            "Sort before washer/soak. Count → whites/lights → darks → "
            "delicates (silk/wool/rayon) → towels/bedding → "
            "biohazard (vomit/feces/blood) separate. Photos with intake."
        ),
        "why_en": (
            "[Why] Bad sorting causes dye transfer, odor, and cross-contamination. "
            "Whites + new darks = bleed risk. Towels/soiled loads with clothes = odor. "
            "Delicates in a hard cycle = damage. Sort before stain work."
        ),
        "fresh_path_en": (
            "(1)Count items vs intake photos. "
            "(2)Five bins — "
            "A whites/very lights; B darks (denim/black/red); "
            "C delicates (silk/wool/rayon/ties/áo dài/hanbok); "
            "D towels/sheets/duvets; "
            "E biohazard/heavy odor — PPE, separate soak. "
            "(3)New denim/darks: first 1–2 washes alone or same-shade only. "
            "(4)Baby/underwear: hygiene first; do not mix carelessly. "
            "(5)Zip up, turn inside out, empty pockets. "
            "(6)Then pretreat and choose cycle per bin. "
            "(7)Script: we separate whites, colors, delicates, towels to prevent bleed and odor."
        ),
        "dried_path_en": (
            "Already mixed and bled: separate immediately, do not dry → dye-transfer SOP. "
            "Odor transfer: extra rinse + light vinegar, then re-sort."
        ),
        "motion_en": "Cap0 — sorting only. Biohazard: PPE.",
        "water_temp_en": "N/A at sort stage.",
        "aftercare_en": "Note bins on ticket. Disclose bleed risk when needed.",
        "sense_check_en": "Eyes: no mixed bins. Nose: biohazard isolated. Count matches.",
        "success_rate_en": "Good sorting lowers bleed/cross-contam. Skipping raises claims.",
        "refuse_when_en": "Forced whites+darks mix or biohazard with normal clothes → refuse.",
        "must_include_en": "separate whites/colors/delicates, towels+biohazard aside, prevent bleed",
    }


def _rinse() -> dict[str, str]:
    return {
        "precheck_ko": (
            "헹굼(Rinse) 교육: 세제·효소·표백·경수 잔여를 빼는 단계. "
            "증상: 뻣뻣함, 흰옷 황변 재발, 피부 자극, 냄새 재발, 다운·이불 뭉침. "
            "경수면 I_WATER_HARDNESS와 함께 보정."
        ),
        "why_ko": (
            "[왜 이 순서] 전처리·세탁만큼 헹굼이 품질을 좌우. "
            "잔여 세제=재황변·뻣뻣·피부자극. 다운·구스·패딩·유아복=추가 헹굼 필수. "
            "경수(Ca/Mg)=거품↓·잔여↑ → 세제+1과 추가 헹굼. "
            "유연제로 헹굼 부족을 대신하지 말 것(수건 흡수력↓). "
            "표백·효소 후 잔여 화학을 남긴 채 건조=손상·냄새."
        ),
        "fresh_path_ko": (
            "(1)질문: 뻣뻣? 거품 많이 남음? 아기옷·다운·이불·경수 지역? "
            "(2)기본: 표준 헹굼 후 잔여 느낌이면 추가 헹굼 1회. "
            "(3)필수 추가 헹굼 — 구스·솜이불·패딩, 유아복, 수건(유연제 과다 시), "
            "효소/산소 장침지 후, 경수 보정 시. "
            "(4)경수 선택: 최종 헹굼에 흰 식초(A3) 약희석(매장 기준) — "
            "락스·암모니아와 섞지 말 것. 실크·울은 식초 신중. "
            "(5)거품이 많으면 세제량↓ 다음 세탁부터 + 지금 추가 헹굼. "
            "(6)건조·다림질 전 손·눈으로 미끄럼·잔여 확인. "
            "(7)대사: 「세제·경수 잔여를 빼려고 헹굼을 한 번 더 합니다」."
        ),
        "dried_path_ko": (
            "이미 뻣뻣·비린내·황변 재발: 재헹굼(+경수면 A3 약희석). "
            "유연제만 더 넣어 해결 금지."
        ),
        "motion_ko": "Cap0 — 코스·추가헹굼 선택.",
        "water_temp_ko": "헹굼은 찬물~미온(원단·라벨). 고온 헹굼으로 잔여 고정하지 말 것.",
        "aftercare_ko": "잔여 없이 건조. 수건 유연제 과다 금지. 경수 지역 전표 메모.",
        "sense_check_ko": "손: 미끄럼·뻣뻣 감소. 눈: 거품·잔여 없음. 코: 세제 냄새 과다 없음.",
        "success_rate_ko": "추가 헹굼+경수 보정: 양호. 방치: 재발.",
        "refuse_when_ko": "유연제만으로 경수·잔여 해결 요구, 락스로 뻣뻣함 해결 → 거절.",
        "must_include_ko": "추가 헹굼, 잔여 세제 제거, 경수 시 보정, 유연제 대체 금지",
        "precheck_vi": (
            "Giao duc xa (rinse): loai bot/enzyme/tay/nuoc cung. "
            "Dau hieu: vai cang, vang lai, kich ung, mui lai, long/chan vun. "
            "Nuoc cung → xem them I_WATER_HARDNESS."
        ),
        "why_vi": (
            "[Tai sao] Xa kem = chat luong kem. Bot du = vang/cang/kich ung. "
            "Down/chan/do be: BAT BUOC xa them. Nuoc cung: tang bot + xa them. "
            "Khong thay xa bang softener (mat tham khan)."
        ),
        "fresh_path_vi": (
            "(1)Hoi: cang? con bot? do be/down/chan? nuoc cung? "
            "(2)Co du → them 1 lan xa. "
            "(3)Bat buoc xa them: long ngong/chan/phao, do be, khan (softener thua), "
            "sau ngam enzyme/oxy dai, nuoc cung. "
            "(4)Nuoc cung: A3 pha nhe o xa cuoi — CAM tron Javel/amoniac; lua/len than trong. "
            "(5)Bot nhieu: giam bot lan sau + xa them bay gio. "
            "(6)Truoc say/ui: tay+mat kiem con bot. "
            "(7)Noi: xa them de het bot/nuoc cung."
        ),
        "dried_path_vi": "Cang/mui/vang lai: xa lai (+A3 neu cung). CAM chi them softener.",
        "motion_vi": "Cap0 — chon xa them.",
        "water_temp_vi": "Xa lanh~am theo nhan. Khong dung nhiet de 'fix' bot.",
        "aftercare_vi": "Say khi het bot. Khan: it softener. Ghi khu vuc nuoc cung.",
        "sense_check_vi": "Tay: het tron/cang. Mat: het bot. Mui: khong nong bot.",
        "success_rate_vi": "Xa them + bu nuoc cung: tot. Bo qua: tai phat.",
        "refuse_when_vi": "Chi softener thay xa / Javel tri cang → tu choi.",
        "must_include_vi": "xa them, het bot du, bu nuoc cung, CAM thay bang softener",
        "precheck_en": (
            "Rinse education: remove detergent/enzyme/bleach/hard-water residue. "
            "Signs: stiffness, re-yellowing, skin irritation, odor return, clumped down. "
            "Hard water → also use I_WATER_HARDNESS."
        ),
        "why_en": (
            "[Why] Poor rinsing ruins results. Residue causes yellowing, stiffness, irritation. "
            "Down/duvet/baby loads need an extra rinse. Hard water needs more detergent + rinse. "
            "Do not replace rinsing with fabric softener (hurts towel absorbency)."
        ),
        "fresh_path_en": (
            "(1)Ask: stiff? suds left? baby/down/duvet? hard water area? "
            "(2)If residue feel → add one extra rinse. "
            "(3)Always extra rinse: goose/cotton duvet/down jacket, baby wear, "
            "oversoftened towels, after long enzyme/oxygen soaks, hard-water correction. "
            "(4)Hard water option: light white vinegar (A3) in final rinse — "
            "never mix with chlorine/ammonia; careful on silk/wool. "
            "(5)Too many suds: reduce detergent next time + extra rinse now. "
            "(6)Before dry/iron: check hand/eyes for slipperiness. "
            "(7)Script: we add a rinse to clear detergent and hard-water residue."
        ),
        "dried_path_en": (
            "Already stiff/odorous/re-yellowed: re-rinse (+ light A3 if hard water). "
            "Do not fix with softener only."
        ),
        "motion_en": "Cap0 — choose extra rinse.",
        "water_temp_en": "Cold–lukewarm per label. Do not 'set' residue with heat.",
        "aftercare_en": "Dry only when residue-free. Limit softener on towels. Note hard water on ticket.",
        "sense_check_en": "Hand: less stiff/slippery. Eyes: no foam. Nose: no heavy detergent smell.",
        "success_rate_en": "Extra rinse + hard-water fix: good. Skipping: recurrence.",
        "refuse_when_en": "Softener-only hard-water fix or chlorine for stiffness → refuse.",
        "must_include_en": "extra rinse, remove residue, hard-water correction, no softener substitute",
    }


def _qc_handover() -> dict[str, str]:
    return {
        "precheck_ko": (
            "QC·고객 인도: 건조·포장·픽업 직전. "
            "강광(또는 밝은 빛)+촉감+후각. 접수 사진과 대조. "
            "잔여 얼룩·이염·형태·단추/지퍼·완전 건조 확인."
        ),
        "why_ko": (
            "[왜 이 순서] 클레임의 상당수는 출고 전 미확인·고지 부족. "
            "잔여 채 열(건조·다림질)=열고착. "
            "한계(마른 얼룩·산화 황변·이염)는 인도 멘트에 남겨야 분쟁 방어. "
            "접수(I_INTAKE) 사진과 QC는 한 세트."
        ),
        "fresh_path_ko": (
            "(1)강광으로 잔여 얼룩·이염·황변 확인 — 있으면 건조/다리미 중단·재처리 또는 고지. "
            "(2)손: 미끄럼(세제 잔여)·축축함(미건조)·뻣뻣함. "
            "(3)코: 약품·곰팡이·연기 냄새. "
            "(4)형태: 어깨·챙·구두 형태·단추·지퍼·비즈. "
            "(5)접수 사진과 비교 — 기존 하자는 전표·사진으로 설명. "
            "(6)인도 멘트 예: "
            "「오늘은 여기까지입니다. 더 세게 하면 원단·색이 상할 수 있어요. "
            "마른·고착 얼룩은 100% 보장이 어렵습니다」. "
            "(7)포장·픽업 안내·보관(통풍·비닐 장기 밀봉 주의). "
            "(8)실패 시: 재처리 / 부분 환불·이관 / 거절 — 전표에 사유 기록."
        ),
        "dried_path_ko": (
            "이미 출고 후 클레임: 접수·QC 사진 대조 → 매장 과실이면 사과·재처리안 / "
            "기존 하자·사전 고지였으면 사진·멘트 제시."
        ),
        "motion_ko": "Cap0 — 검사·소통. 재처리 시에만 해당 SOP 힘 사용.",
        "water_temp_ko": "해당 없음(검사 단계).",
        "aftercare_ko": "사진·전표 보관. Zalo 문의는 사진 있으면 신속 응답. 한계 고지 문구 유지.",
        "sense_check_ko": "눈·손·코 3감 + 사진 대조 + 인도 멘트 완료.",
        "success_rate_ko": "QC+고지: 분쟁↓. 미검사 출고: 클레임↑.",
        "refuse_when_ko": "잔여 얼룩 상태 강제 출고·100% 새것 복원 약속 요구 → 거절.",
        "must_include_ko": "강광 잔여 확인, 접수 사진 대조, 한계 고지, 출고 체크리스트",
        "precheck_vi": (
            "QC + ban giao: truoc say/goi/lay do. "
            "Anh sang manh + tay + mui. Doi anh luc nhan. "
            "Kiem vet du, loang mau, form, nut/keo, kho han."
        ),
        "why_vi": (
            "[Tai sao] Nhieu khieu nai = thieu QC/bao truoc. "
            "Con vet ma say/ui = khoa nhiet. "
            "Gioi han (vet kho/vang oxy hoa/loang) phai noi luc giao. "
            "Anh tiep nhan + QC di cung nhau."
        ),
        "fresh_path_vi": (
            "(1)Anh sang: vet/loang/vang — neu con: dung say/ui, xu ly lai hoac bao. "
            "(2)Tay: tron bot / am / cang. "
            "(3)Mui: hoa chat/moc/khoi. "
            "(4)Form: vai/mu/giay, nut, keo, hat. "
            "(5)Doi anh luc nhan — hong san: giai thich bang anh/phieu. "
            "(6)Loi giao: "
            "Hom nay den day; lam manh hon co the hong vai/mau. "
            "Vet kho khong bao 100%. "
            "(7)Goi + huong dan lay/bao quan (thoang, tranh nilon lau). "
            "(8)Fail: xu ly lai / hoan 1 phan-chuyen / tu choi — ghi ly do."
        ),
        "dried_path_vi": (
            "Khieu nai sau giao: doi anh nhan+QC → loi tiem thi xin loi/xu ly lai; "
            "hong san da bao thi dua anh/loi da noi."
        ),
        "motion_vi": "Cap0 — kiem + giao tiep.",
        "water_temp_vi": "N/A.",
        "aftercare_vi": "Luu anh+phieu. Tra loi Zalo nhanh neu co anh. Giu cau bao gioi han.",
        "sense_check_vi": "Mat+tay+mui + doi anh + da noi gioi han.",
        "success_rate_vi": "QC+bao: giam kien. Xuat thieu kiem: khieu nai cao.",
        "refuse_when_vi": "Bat giao khi con vet / hua 100% moi → tu choi.",
        "must_include_vi": "anh sang kiem vet, doi anh nhan, bao gioi han, checklist giao",
        "precheck_en": (
            "QC + handover: just before dry/pack/pickup. "
            "Strong light + touch + smell. Compare intake photos. "
            "Check residue, bleed, shape, buttons/zips, fully dry."
        ),
        "why_en": (
            "[Why] Many claims come from skipping QC or not disclosing limits. "
            "Heat on residue sets stains. "
            "Limits (dried stains, oxidation yellowing, bleed) must be spoken at handover. "
            "Intake photos and QC are one system."
        ),
        "fresh_path_en": (
            "(1)Strong light: residue/bleed/yellow — if present: stop dry/iron; rework or disclose. "
            "(2)Hand: detergent slip / damp / stiff. "
            "(3)Nose: chemical/mildew/smoke. "
            "(4)Shape: shoulders/brim/shoes, buttons, zips, beads. "
            "(5)Compare intake photos — explain pre-existing damage with ticket/photos. "
            "(6)Handover script: "
            "This is as far as is safe today; pushing harder can damage fiber/color. "
            "Dried/set stains are not 100% guaranteed. "
            "(7)Pack + pickup/storage tips (airflow; avoid long plastic bagging). "
            "(8)On fail: rework / partial refund-refer / refuse — write reason on ticket."
        ),
        "dried_path_en": (
            "Post-pickup claim: compare intake+QC photos → shop fault: apologize/rework; "
            "pre-existing/disclosed: show photos and prior script."
        ),
        "motion_en": "Cap0 — inspect and communicate.",
        "water_temp_en": "N/A.",
        "aftercare_en": "Keep photos/ticket. Reply fast on Zalo if photos attached. Keep limit language.",
        "sense_check_en": "Eyes+hand+nose + photo match + limit script spoken.",
        "success_rate_en": "QC+disclose lowers disputes. Shipping without check raises claims.",
        "refuse_when_en": "Forced release with residue or demand for 100% like-new promise → refuse.",
        "must_include_en": "strong-light residue check, intake photo match, disclose limits, handover checklist",
    }


def apply_process_stage_hints(graph: dict[str, Any], item_id: str) -> dict[str, Any]:
    """Light tool stubs for ops cards (no invented chemistry kits)."""
    if item_id not in PROCESS_STAGE_IDS:
        return graph
    out = dict(graph)
    tools = list(out.get("tools") or [])
    if not any(str(t.get("id")) == "T_CLOTH" for t in tools):
        tools.append({
            "id": "T_CLOTH",
            "name_ko": "흰 천·검사용",
            "name_vi": "Khan trang (kiem)",
            "name_en": "White cloth (inspect)",
            "use_for_ko": "잔여·이염 육안 확인 시 받침·닦기.",
            "use_for_vi": "Lot/lau khi kiem vet.",
            "use_for_en": "Blot/backer while inspecting residue.",
        })
    if item_id == "I_QC_HANDOVER" and not any(
        str(t.get("id")) == "T_UV_LAMP" for t in tools
    ):
        tools.append({
            "id": "T_UV_LAMP",
            "name_ko": "강광·UV(잔여 검사)",
            "name_vi": "Den UV / anh sang manh",
            "name_en": "Strong light / UV check",
            "use_for_ko": "출고 전 잔여 얼룩·이염 확인.",
            "use_for_vi": "Kiem vet truoc giao.",
            "use_for_en": "Residue/bleed check before handover.",
        })
    if item_id == "I_RINSE":
        out["chemicals"] = [
            {
                "code": "A3",
                "name_ko": "흰 식초(최종 헹굼 선택·경수)",
                "name_vi": "Giam trang (xa cuoi tuy chon)",
                "name_en": "White vinegar (optional final rinse)",
                "dilution_ko": "약희석·매장 기준. 락스·암모니아와 혼합 금지. 실크·울 신중.",
                "dilution_vi": "Pha nhe. CAM tron Javel/amoniac. Lua/len than trong.",
                "dilution_en": "Light dilution per store SOP. Never mix with chlorine/ammonia. Careful on silk/wool.",
            }
        ]
        out["empty_chems_ok"] = False
    out["tools"] = tools
    return out
