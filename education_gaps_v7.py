# -*- coding: utf-8 -*-
"""Education gaps v7: dilution quality, VN iodine(+chili), claim/pricing, mini quizzes.

Additive only — wire via seed + hard-route + CHEM_META sync.
"""
from __future__ import annotations

# ── 1) Dilution upgrades (sync main V_chem + protocol CHEM_META + DILUTION_GAPS) ─
DILUTION_V7: list[dict[str, str]] = [
    {
        "code": "E2",
        "dilution_ko": "전분 효소: 찬물 1L에 큰술 1(또는 병 표기) → 잘 녹여 15–60분 담금. 실크·울 금지.",
        "dilution_vi": "Amylase: 1 muỗng canh / 1L nước lạnh (hoặc theo nhãn) → ngâm 15–60 phút. CẤM lụa/len.",
        "dilution_en": "Amylase: 1 tbsp / 1L cold (or per label); soak 15–60 min. No silk/wool.",
    },
    {
        "code": "E3",
        "dilution_ko": "리파아제: 병 표기; 보통 미온 1L에 큰술 1 → 탈지 후 15–30분 담금. 실크·울 주의.",
        "dilution_vi": "Lipase: theo nhãn; thường 1 muỗng / 1L ấm nhẹ → ngâm 15–30 phút sau khử dầu.",
        "dilution_en": "Lipase: per label; often 1 tbsp / 1L warm; soak 15–30 min after degrease.",
    },
    {
        "code": "B2",
        "dilution_ko": (
            "흰 면만. 예: 가정용 자벨/락스 원액 1 : 물 10–20(병 우선) · 짧은 담금·즉시 헹굼. "
            "유색·실크·울·아세테이트 금지. 식초·암모니아와 절대 혼합 금지."
        ),
        "dilution_vi": (
            "CHỈ cotton TRẮNG. VD: Javel đặc 1 : nước 10–20 (ưu tiên nhãn) · ngâm ngắn · xả ngay. "
            "CẤM màu/lụa/len/acetate. CẤM trộn giấm/amoniac."
        ),
        "dilution_en": (
            "White cotton only. Example: household chlorine 1 : water 10–20 (label first); "
            "short soak then rinse. Never color/silk/wool/acetate. Never mix vinegar/ammonia."
        ),
    },
    {
        "code": "A2",
        "dilution_ko": (
            "원액 극소량만 — 흰 천/솜에 묻혀 안쪽 Cap1 블롯(흡수지 아래). "
            "아세테이트·레이온·트리아세테이트 즉시 금지. 환기·PPE."
        ),
        "dilution_vi": (
            "Nguyên chất rất ít — thấm khăn mặt trái Cap1 (giấy thấm dưới). "
            "CẤM acetate/rayon/triacetate. Thông gió + PPE."
        ),
        "dilution_en": (
            "Neat tiny amount on cloth; Cap1 blot from reverse with blotter under. "
            "Never acetate/rayon/triacetate. Ventilate + PPE."
        ),
    },
    {
        "code": "B1",
        "dilution_ko": (
            "흰옷만·구석 색 테스트. 병 라벨; 보통 찬물·미지근 1L에 큰술 1–2 → 15–45분. "
            "유색·색 미확인·실크·울 금지."
        ),
        "dilution_vi": (
            "CHỈ trắng + test góc. Theo nhãn; thường 1–2 muỗng / 1L lạnh/ấm → 15–45 phút. "
            "CẤM màu/chưa rõ/lụa/len."
        ),
        "dilution_en": (
            "White only + corner test. Per label; often 1–2 tbsp / 1L cold–warm; 15–45 min. "
            "Never colored/unknown/silk/wool."
        ),
    },
    {
        "code": "E1",
        "dilution_ko": "단백질 효소: 찬물 1L에 큰술 1 → 잘 녹여 15–60분(병 우선). 실크·울 금지→중성세제.",
        "dilution_vi": "Protease: 1 muỗng / 1L lạnh → ngâm 15–60 phút (ưu tiên nhãn). CẤM lụa/len → S1.",
        "dilution_en": "Protease: 1 tbsp / 1L cold; soak 15–60 min (label first). No silk/wool → neutral.",
    },
]


def dilution_seed_rows() -> list[dict[str, str]]:
    return [
        {"code": d["code"], "dilution_ko": d["dilution_ko"], "dilution_vi": d["dilution_vi"]}
        for d in DILUTION_V7
    ]


def apply_dilution_to_chem_meta(chem_meta: dict) -> None:
    """Mutate protocol.CHEM_META dilutions in place."""
    for d in DILUTION_V7:
        code = d["code"]
        if code not in chem_meta:
            continue
        chem_meta[code]["dilution_ko"] = d["dilution_ko"]
        chem_meta[code]["dilution_vi"] = d["dilution_vi"]
        if d.get("dilution_en"):
            chem_meta[code]["dilution_en"] = d["dilution_en"]


# ── 2) VN stains: iodine + chili ─────────────────────────────────────────────
VN_STAIN_SEED_V7: list[dict] = [
    {
        "id": "S_IODINE",
        "group_id": "G4",
        "name": "Iodine / povidone-iodine",
        "name_vi": "Thuốc đỏ / iod",
        "name_ko": "요오드·포비돈요오드(thuốc đỏ)",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": False,
        "contains_oil": False,
        "contains_dye": True,
        "urgency": "high",
        "tip": "VN thuốc đỏ / iodine — cold blot → alcohol → white oxygen; no heat/scrub",
        "why_ko": (
            "[왜 이 순서] 요오드·포비돈요오드(thuốc đỏ)=할로겐 색소. "
            "찬물 흡수→알코올 안쪽 블롯→흰/면만 산소. 문지르기·열고착 금지. 100% 비보장."
        ),
        "why_vi": (
            "[Tại sao] Thuốc đỏ/iod = sắc tố halogen. "
            "Thấm lạnh → blot cồn mặt trái → oxy trắng/cotton. CẤM chà/nhiệt. Không 100%."
        ),
        "fresh_path_ko": (
            "(1)요오드/thuốc đỏ·원단 확인. (2)안쪽 찬물 흡수(문지르기 금지). "
            "(3)이소프로필 알코올 흰 천 안쪽 블롯·흡수지(테스트). (4)흰/면: 산소(테스트). "
            "(5)찬물 세탁. (6)건조 전 강광. 실크·울: 중성만·전문 고려."
        ),
        "fresh_path_vi": (
            "(1)Nhận thuốc đỏ/iod + vải. (2)Thấm lạnh mặt trái — CẤM chà. "
            "(3)Cồn isopropyl blot mặt trái + giấy thấm (test). (4)Trắng/cotton: oxy (test). "
            "(5)Giặt lạnh. (6)Ánh sáng trước sấy. Lụa/len: S1 / chuyên."
        ),
        "dried_path_ko": (
            "(1)마른 요오드. (2)알코올 안쪽 블롯 반복(테스트). (3)흰/면 산소 장침지. "
            "(4)세탁·강광. (5)잔색·열고착 가능 — 100% 불가 고지. (6)아세테이트: 용제 중단."
        ),
        "dried_path_vi": (
            "(1)Iod khô. (2)Blot cồn mặt trái lặp (test). (3)Oxy dài trắng/cotton. "
            "(4)Giặt + ánh sáng. (5)Báo còn màu — không 100%. (6)Acetate: dừng dung môi."
        ),
        "success_rate_ko": "신선: 중~양호. 마른·열고착: 낮음. 100% 비보장.",
        "success_rate_vi": "Tươi: TB–khá. Khô/nhiệt: thấp. Không 100%.",
        "refuse_when_ko": "실크·아세테이트에 강한 용제 반복·100% 약속 → 거절·전문.",
        "refuse_when_vi": "Lụa/acetate + dung môi mạnh lặp / hứa 100% → từ chối·chuyên.",
    },
    {
        "id": "S_CHILI",
        "group_id": "G3",
        "name": "Chili / hot sauce",
        "name_vi": "Tương ớt / ớt",
        "name_ko": "칠리·핫소스(tương ớt)",
        "water_spreads": True,
        "contains_protein": False,
        "contains_tannin": True,
        "contains_oil": True,
        "contains_dye": True,
        "urgency": "high",
        "tip": "VN chili sauce — oil+pigment+acid; cold → dish → vinegar → white oxygen",
        "why_ko": (
            "[왜 이 순서] 칠리·핫소스=오일+색소(캡사이신/토마토계)+산. "
            "순서: 찬물→주방세제(오일)→식초 1:4(색소)→흰/면 산소. 문지르기·열고착 금지."
        ),
        "why_vi": (
            "[Tại sao] Tương ớt = dầu + màu + acid. "
            "Thứ tự: lạnh → nước rửa chén → giấm 1:4 → oxy trắng. CẤM chà/nhiệt."
        ),
        "fresh_path_ko": (
            "(1)칠리·원단 확인. (2)여분 긁기·찬물. (3)주방세제 Cap2. "
            "(4)식초 1:4 15분. (5)흰/면 산소(테스트). (6)세탁·강광."
        ),
        "fresh_path_vi": (
            "(1)Nhận tương ớt + vải. (2)Cạo + xả lạnh. (3)Nước rửa chén Cap2. "
            "(4)Giấm 1:4 ~15 phút. (5)Oxy trắng (test). (6)Giặt + ánh sáng."
        ),
        "dried_path_ko": (
            "(1)마른 칠리. (2)주방세제→식초 1:4 장침지 15–30분. (3)흰/면 산소. "
            "(4)세탁·강광. (5)적갈 잔색 가능 — 100% 비보장."
        ),
        "dried_path_vi": (
            "(1)Ớt khô. (2)D2 → giấm 1:4 ngâm 15–30. (3)Oxy trắng. "
            "(4)Giặt + ánh sáng. (5)Báo màu đỏ còn — không 100%."
        ),
        "success_rate_ko": "신선: 양호. 마른·열고착: 중·하. 100% 비보장.",
        "success_rate_vi": "Tươi: khá. Khô/nhiệt: TB–thấp. Không 100%.",
        "refuse_when_ko": "실크에 강한 산소·락스 요구 → 거절.",
        "refuse_when_vi": "Lụa + oxy/Javel mạnh → từ chối.",
    },
]


def vn_specialty_stain_seed_rows_v7() -> list[dict]:
    return list(VN_STAIN_SEED_V7)


DRIED_IODINE_KO = VN_STAIN_SEED_V7[0]["dried_path_ko"]
DRIED_IODINE_VI = VN_STAIN_SEED_V7[0]["dried_path_vi"]
DRIED_CHILI_KO = VN_STAIN_SEED_V7[1]["dried_path_ko"]
DRIED_CHILI_VI = VN_STAIN_SEED_V7[1]["dried_path_vi"]

RESCUE_IODINE = {
    "ko": "2차: 알코올 안쪽 블롯 1회만 추가(테스트) → 흰/면 산소 → 안 되면 전문. 100% 금지.",
    "vi": "Lần 2: blot cồn mặt trái 1 lần thêm (test) → oxy trắng → không được thì chuyên. CẤM 100%.",
    "en": "2nd: one more reverse alcohol blot (test) → white oxygen → else refer. No 100%.",
}
RESCUE_CHILI = {
    "ko": "2차: 주방세제→식초 1:4 재침지 15–30분 → 흰/면 산소. 적갈 잔색·100% 불가 고지.",
    "vi": "Lần 2: D2 → giấm 1:4 ngâm 15–30 → oxy trắng. Báo màu đỏ — không 100%.",
    "en": "2nd: dish → vinegar 1:4 soak 15–30 → white oxygen. Disclose red residual — no 100%.",
}


# ── 4–5) Claim / pricing / quizzes ───────────────────────────────────────────
OPS_DRILLS_V7: dict[str, dict[str, str]] = {
    "I_CLAIM_SCRIPT": {
        "why_ko": (
            "[왜 이 순서] 클레임=사진·전표가 증거. "
            "순서: 진정→접수 사진 대조→매장 과실이면 사과·보상안 / 기존 하자면 사진 제시. "
            "감정 대응·즉흥 100% 환불 약속 금지."
        ),
        "fresh_path_ko": (
            "(1)질문: 언제 접수? 전표·사진 있는가? (2)판단: 접수 사진과 현재 상태 대조. "
            "(3)대사: 「접수 때 사진과 비교해 확인하겠습니다」→ 과실이면 「죄송합니다. "
            "보상안을 제안드리겠습니다」/ 기존 하자면 「이 손상은 접수 사진에 이미 있습니다」. "
            "(4)금지: 사진 없이 무조건 인정, 고함 대응, 임의 전액 환불 약속."
        ),
        "dried_path_ko": "이미 분쟁 장기화: 본사 에스컬레이션·서면 기록만. 추가 구두 약속 금지.",
        "aftercare_ko": "사진·전표·대화 요약 보관. Zalo 답은 사실만·24시간 내.",
        "sense_check_ko": "눈: 접수 사진. 손: 전표 서명. 기록: 과실 여부 한 줄.",
        "success_rate_ko": "사진+전표 있으면 방어 양호. 없으면 위험 — 다음부터 필수.",
        "refuse_when_ko": "폭언·협박·허위 주장 → 정중 중단·본사 연결. 추가 처리 약속 금지.",
        "why_vi": (
            "[Tại sao] Khiếu nại = ảnh phiếu là bằng chứng. "
            "Bình tĩnh → đối chiếu ảnh lúc nhận → lỗi cửa hàng: xin lỗi+phương án / "
            "hư sẵn: đưa ảnh. CẤM hứa hoàn 100% nóng giận."
        ),
        "fresh_path_vi": (
            "(1)Hỏi: nhận lúc nào? có phiếu+ảnh? (2)So ảnh nhận vs hiện tại. "
            "(3)Lỗi shop: xin lỗi + thương lượng. Hư sẵn: chỉ ảnh. "
            "(4)CẤM nhận lỗi không ảnh; CẤM cãi lớn."
        ),
        "aftercare_vi": "Lưu ảnh+phiếu+tóm tắt. Trả lời Zalo đúng sự thật.",
        "sense_check_vi": "Mắt: ảnh nhận. Tay: chữ ký. Ghi: có lỗi hay không.",
        "success_rate_vi": "Có ảnh+phiếu: phòng thủ tốt. Không ảnh: rủi ro cao.",
        "refuse_when_vi": "Đe dọa/đòi bồi không căn cứ → dừng lịch sự + HQ.",
        "must_include_ko": "접수 사진, 전표, 사과·보상안",
    },
    "I_PRICING_SCRIPT": {
        "why_ko": (
            "[왜 이 순서] 요금=자신감+가치 설명. 구체 숫자는 매장 가격표를 본다(날조 금지). "
            "순서: 기본 요금 안내→얼룩 추가비 가능성→이의 제기 시 가치(전문 약·원단 보호) 설명."
        ),
        "fresh_path_ko": (
            "(1)질문: 품목·수량·얼룩 유무? (2)판단: 가격표 구간 확인(추정 금지). "
            "(3)대사: 「기본 세탁은 가격표 ○○ 구간입니다. 얼룩 전문 처리는 추가될 수 있습니다. "
            "24시간 내 완료 목표입니다」. 비싸다는 말→「전문 얼룩 약과 원단 보호 공정이 포함됩니다」. "
            "(4)금지: 임의 할인 남발·가격 추측·숨은 추가비."
        ),
        "dried_path_ko": "이미 구두로 다른 금액 약속: 전표 기준으로 정정·사과. 추가 임의 할인 금지.",
        "aftercare_ko": "전표에 기본+추가(얼룩) 항목을 분리 기입.",
        "sense_check_ko": "눈: 가격표. 손: 전표 항목. 말: 가치 한 문장.",
        "success_rate_ko": "가격표 보고 안내: 신뢰↑. 추측 금액: 분쟁↑.",
        "refuse_when_ko": "원가 이하·무리 할인 강요 → 정중 거절·본사 기준 안내.",
        "why_vi": (
            "[Tại sao] Giá = rõ + tự tin. Số tiền: xem bảng giá cửa hàng (CẤM bịa). "
            "Báo cơ bản → phụ phí vết → giải thích giá trị khi khách than đắt."
        ),
        "fresh_path_vi": (
            "(1)Hỏi món+số+vết. (2)Xem bảng giá. "
            "(3)Nói: giá cơ bản theo bảng; vết có thể phụ phí; mục tiêu 24h. "
            "Than đắt → giải thích hóa chất+bảo vệ vải. (4)CẤM bịa số / giảm lung tung."
        ),
        "aftercare_vi": "Ghi tách phí cơ bản và phụ phí vết trên phiếu.",
        "sense_check_vi": "Mắt: bảng giá. Tay: phiếu. Nói: 1 câu giá trị.",
        "success_rate_vi": "Theo bảng giá: tin cậy cao. Đoán giá: rủi ro tranh chấp.",
        "refuse_when_vi": "Ép giảm dưới giá vốn → từ chối lịch sự.",
        "must_include_ko": "가격표, 추가비, 가치 설명",
    },
    "I_QUIZ_STAINS": {
        "why_ko": (
            "[왜 연습] 점주 단원: 얼룩 화학 퀴즈. "
            "질문→정답→이유. 암기보다 「왜 이 약·이 순서」."
        ),
        "fresh_path_ko": (
            "(1)Q1: 신선한 피 — 온수? → 정답: 찬물만(단백질 고착). "
            "(2)Q2: 레드와인 1차 — 문지르기? → 정답: 금지(번짐)·식초 1:4. "
            "(3)Q3: 잉크 — 솔로 문지르기? → 정답: 안쪽 알코올 블롯. "
            "(4)Q4: 유성 페인트 vs 수성? → 정답: 용제(환기) vs 찬물+세제. "
            "(5)Q5: 마른 얼룩 식초 담금? → 정답: 15–30분(신선 5–15 아님). "
            "(6)복습: 100% 약속 금지."
        ),
        "dried_path_ko": "틀리면 해당 SOP fresh_path를 다시 읽기.",
        "aftercare_ko": "주 1회 5문항 복습 권장.",
        "sense_check_ko": "입으로 정답+이유를 한 문장으로 말할 수 있으면 통과.",
        "success_rate_ko": "5문항 중 4 이상: 현장 투입 가능 수준.",
        "refuse_when_ko": "정답만 외우고 이유를 못하면 재학습.",
        "why_vi": "[Tại sao] Quiz vết bẩn: hỏi → đáp → lý do.",
        "fresh_path_vi": (
            "(1)Máu tươi — nước nóng? → Chỉ lạnh. "
            "(2)Rượu đỏ — chà? → CẤM; giấm 1:4. "
            "(3)Mực — chải? → Blot cồn mặt trái. "
            "(4)Sơn dầu vs nước? → Dung môi vs lạnh+D2. "
            "(5)Vết khô ngâm giấm? → 15–30 phút. "
            "(6)CẤM hứa 100%."
        ),
        "aftercare_vi": "Ôn 5 câu / tuần.",
        "sense_check_vi": "Nói được đáp + lý do = đạt.",
        "success_rate_vi": "≥4/5: đạt.",
        "refuse_when_vi": "Chỉ thuộc đáp, không hiểu → học lại.",
        "must_include_ko": "정답, 이유, 100% 금지",
    },
    "I_QUIZ_FABRIC": {
        "why_ko": (
            "[왜 연습] 점주 단원: 원단 안전 퀴즈. "
            "실크·울·아세테이트·표백 한도를 틀리면 사고."
        ),
        "fresh_path_ko": (
            "(1)Q1: 실크에 효소? → 정답: 금지→중성세제. "
            "(2)Q2: 아세테이트에 아세톤? → 정답: 즉시 금지(녹음). "
            "(3)Q3: 유색에 락스(B2)? → 정답: 금지. "
            "(4)Q4: 케어라벨 X 물통? → 정답: 물세탁 금지·드라이/전문. "
            "(5)Q5: 원단 미확인 표백? → 정답: Cap1·표백 보류. "
            "(6)복습: 라벨 > 추측."
        ),
        "dried_path_ko": "오답 문항의 fabric_care 카드를 다시 읽기.",
        "aftercare_ko": "신규 직원 첫 주 필수.",
        "sense_check_ko": "금지 3가지(효소·아세톤·락스)를 바로 말할 수 있으면 통과.",
        "success_rate_ko": "5문항 중 4 이상: 안전 교육 통과.",
        "refuse_when_ko": "금지 항목을 헷갈리면 단독 스포팅 금지.",
        "must_include_ko": "실크 효소 금지, 아세테이트 아세톤 금지, 표백 보류, 정답",
        "why_vi": "[Tại sao] Quiz vải: lụa/len/acetate/tẩy.",
        "fresh_path_vi": (
            "(1)Lụa + enzyme? → CẤM → S1. "
            "(2)Acetate + acetone? → CẤM. "
            "(3)Màu + Javel? → CẤM. "
            "(4)Nhãn X chậu? → CẤM giặt nước. "
            "(5)Chưa rõ vải + tẩy? → Cap1, tạm dừng tẩy. "
            "(6)Nhãn > đoán."
        ),
        "aftercare_vi": "Nhân viên mới: tuần đầu bắt buộc.",
        "sense_check_vi": "Nói 3 CẤM ngay = đạt.",
        "success_rate_vi": "≥4/5: đạt.",
        "refuse_when_vi": "Nhầm CẤM → không spotting một mình.",
        "must_include_ko": "실크 효소 금지, 아세테이트 아세톤 금지, 표백 보류",
    },
}


def ops_seed_rows_v7() -> list[dict]:
    rows = []
    for iid, fields in OPS_DRILLS_V7.items():
        row = {"id": iid}
        row.update(fields)
        rows.append(row)
    return rows


OPS_ITEM_IDS_V7 = tuple(OPS_DRILLS_V7.keys())


# ── Care-label constraints helper ────────────────────────────────────────────
def care_label_constraints(label: dict) -> dict:
    """Map vision care-label JSON → entity flags for SOP chem/temp clamps."""
    if not isinstance(label, dict):
        return {}
    wash = label.get("wash") if isinstance(label.get("wash"), dict) else {}
    bleach = label.get("bleach") if isinstance(label.get("bleach"), dict) else {}
    out: dict = {"_from_care_label": True}
    fiber = label.get("fiber_text") or label.get("fabric_type") or ""
    if fiber:
        out["fabric_type"] = fiber
        out["_care_fiber"] = fiber
    if wash.get("max_temp_c"):
        try:
            out["care_max_temp_c"] = int(wash["max_temp_c"])
        except (TypeError, ValueError):
            pass
    if wash.get("do_not_wash"):
        out["care_do_not_wash"] = True
    if wash.get("hand_wash_only"):
        out["care_hand_wash_only"] = True
    if bleach.get("oxygen_only"):
        out["care_oxygen_only"] = True
    if bleach.get("do_not_bleach") or bleach.get("allowed") is False:
        if not bleach.get("oxygen_only"):
            out["care_no_bleach"] = True
    return out
