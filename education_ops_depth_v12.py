# -*- coding: utf-8 -*-
"""Ops education depth v12 — intake dried disclosure + claim script.

Raises franchise ops coaching without LMS: ticket wording, dried-stain consent,
claim calm→photo→escalate. KO / VI (diacritics) / EN parallel.
"""
from __future__ import annotations

OPS_DEPTH_IDS = frozenset({
    "I_INTAKE_SCRIPT",
    "I_CLAIM_SCRIPT",
    "I_CARE_LABEL",
})

# Applied last onto OPS_DRILLS / specialty cards.
OPS_DEPTH_V12: dict[str, dict[str, str]] = {
    "I_INTAKE_SCRIPT": {
        "precheck_ko": (
            "접수 준비: 카메라·전표 2부·위험 태그(실크/울/빈티지/가죽). "
            "마른·고착·열고착 여부를 먼저 눈으로 확인."
        ),
        "why_ko": (
            "[왜 이 순서] 사진+서명=클레임 방어. "
            "필수: 인사→수량·기존 손상→전체+클로즈업 사진→요금·기한→전표 서명. "
            "마른 얼룩=「이미 색이 고정됐을 수 있어 100% 제거 불가」사전 고지+서면 동의. "
            "사진 없이 접수=분쟁 패소 위험. 성공 100% 약속 금지."
        ),
        "fresh_path_ko": (
            "(1)인사·수량 확인. (2)기존 찢김·탈색·구멍 기록. "
            "(3)전체 사진 + 얼룩 클로즈업(최소 2장). "
            "(4)요금·완료 기한 고지(가격표 기준·추측 금지). "
            "(5)전표 2부 서명. "
            "(6)마른·고착 얼룩이면 대사: "
            "「이미 마른/오래된 얼룩은 100% 제거가 안 될 수 있습니다. "
            "잔여·변형 가능성을 이해하시고 동의하시면 접수합니다」→ 전표에 √체크. "
            "(7)위험 품목 태그. (8)사진·전표 보관."
        ),
        "dried_path_ko": (
            "(1)마른 얼룩 정의: 어제 이상·이미 세탁/건조/다림·색이 안 번짐. "
            "(2)전표 「마른얼룩 한계고지」칸에 체크+고객 이니셜. "
            "(3)100% 요구 시 접수 거절 또는 서면 동의 후에만. "
            "(4)클레임 시: 접수 사진 대조(과실 vs 기존 손상)."
        ),
        "aftercare_ko": "사진·전표 보관. Zalo 문의는 사진 있으면 2시간 내 사실만 답.",
        "sense_check_ko": "눈: 사진≥2. 손: 서명. 기록: 마른얼룩 동의 √.",
        "success_rate_ko": "사진+마른얼룩 동의: 분쟁↓. 미촬영·구두만: 위험.",
        "refuse_when_ko": (
            "사진/서명 거부, 또는 「무조건 100% 지워달라」만 요구 → 접수 거절. "
            "고가 위험품은 서면 동의 필수."
        ),
        "must_include_ko": "사진2, 전표서명, 마른얼룩 100%불가 동의, 위험태그",
        "precheck_vi": (
            "Chuẩn bị: máy ảnh + phiếu 2 bản + tag rủi ro (lụa/len/vintage/da). "
            "Nhìn trước: vết khô / đã giặt-sấy-ủi?"
        ),
        "why_vi": (
            "[Tại sao] Ảnh + chữ ký = phòng khiếu nại. "
            "Bắt buộc: chào → đếm/hư sẵn → ảnh tổng+close → giá/thời hạn → ký phiếu. "
            "Vết khô: báo trước 「không 100%」 + đồng ý trên phiếu. "
            "Không ảnh = rủi ro tranh chấp. CẤM hứa 100%."
        ),
        "fresh_path_vi": (
            "(1)Chào + đếm món. (2)Ghi hư sẵn (rách/phai/lỗ). "
            "(3)Ảnh tổng + close-up vết (≥2). "
            "(4)Báo giá/thời hạn theo bảng giá (CẤM bịa). "
            "(5)Ký phiếu 2 bản. "
            "(6)Nếu vết khô/cũ: nói "
            "「Vết đã khô/cũ có thể không hết 100%. "
            "Anh/chị đồng ý tiếp nhận với rủi ro còn vết không?」→ tick trên phiếu. "
            "(7)Tag rủi ro. (8)Lưu ảnh+phiếu."
        ),
        "dried_path_vi": (
            "(1)Vết khô = từ hôm qua / đã giặt-sấy-ủi / màu không lan. "
            "(2)Tick ô 「cảnh báo vết khô」+ ký tắt khách. "
            "(3)Đòi 100% → từ chối nhận hoặc chỉ khi có văn bản đồng ý. "
            "(4)Khiếu nại: đối chiếu ảnh lúc nhận."
        ),
        "aftercare_vi": "Lưu ảnh+phiếu. Zalo <2 giờ, chỉ đúng sự thật nếu có ảnh.",
        "sense_check_vi": "Mắt: ≥2 ảnh. Tay: chữ ký. Phiếu: tick vết khô.",
        "success_rate_vi": "Ảnh + đồng ý vết khô: giảm tranh chấp. Thiếu ảnh: rủi ro cao.",
        "refuse_when_vi": (
            "Từ chối ảnh/ký, hoặc chỉ đòi 「xóa 100%」 → từ chối nhận. "
            "Đồ rủi ro cao: bắt buộc đồng ý văn bản."
        ),
        "must_include_vi": "2 ảnh, ký phiếu, đồng ý không 100% vết khô, tag rủi ro",
        "precheck_en": (
            "Ready: camera, two tickets, risk tags (silk/wool/vintage/leather). "
            "Visually check dried/heat-set stains first."
        ),
        "why_en": (
            "[Why] Photo+signature defend claims. "
            "Flow: greet→count/prior damage→full+close photos→price/time→sign. "
            "Dried stains need advance 「not 100%」disclosure + written consent. "
            "No photo = dispute risk. Never promise 100%."
        ),
        "fresh_path_en": (
            "(1)Greet + count. (2)Note prior tears/fades/holes. "
            "(3)Full + close-up stain photos (≥2). "
            "(4)Price/turnaround from price list (no inventing). "
            "(5)Sign two tickets. "
            "(6)If dried/old: script "
            "「Dried/old stains may not come out 100%. "
            "Do you accept intake with residual risk?」→ checkbox on ticket. "
            "(7)Risk tag. (8)Store photos+ticket."
        ),
        "dried_path_en": (
            "(1)Dried = yesterday+ / already washed-dried-ironed / color won't spread. "
            "(2)Ticket checkbox 「dried-stain limit」+ customer initial. "
            "(3)Demands 100% → refuse or written consent only. "
            "(4)Claim: compare intake photos."
        ),
        "aftercare_en": "Keep photos+ticket. Zalo <2h with facts if photo attached.",
        "sense_check_en": "Eyes: ≥2 photos. Hand: signature. Record: dried consent ✓.",
        "success_rate_en": "Photo+dried consent → fewer disputes. No photo → high risk.",
        "refuse_when_en": (
            "Refuses photo/sign, or demands guaranteed 100% removal → refuse intake. "
            "High-risk items need written consent."
        ),
        "must_include_en": "2 photos, signed ticket, dried not-100% consent, risk tag",
    },
    "I_CLAIM_SCRIPT": {
        "precheck_ko": "클레임: 진정. 접수 사진·전표·작업 기록부터 찾기. 감정 대응 금지.",
        "why_ko": (
            "[왜 이 순서] 클레임=증거로 말한다. "
            "진정→접수 사진 대조→매장 과실이면 사과·보상안 / 기존 손상이면 사진 제시. "
            "즉흥 100% 환불·고함 대응 금지. 장기화는 본사 에스컬레이션·서면만."
        ),
        "fresh_path_ko": (
            "(1)질문: 언제 접수? 전표·사진 있는가? "
            "(2)판단: 접수 사진 vs 현재 상태 대조(매장 과실 / 기존 손상 / 마른얼룩 한계고지 여부). "
            "(3)대사(과실): 「접수 사진과 비교해 확인했습니다. 죄송합니다. "
            "보상안을 제안드리겠습니다」. "
            "(4)대사(기존 손상): 「이 부분은 접수 사진에 이미 있습니다」→ 사진 보여주기. "
            "(5)대사(마른얼룩): 「접수 때 잔여 가능에 동의하셨습니다」→ 전표 체크 확인. "
            "(6)금지: 사진 없이 무조건 인정, 고함 대응, 임의 전액 환불 약속."
        ),
        "dried_path_ko": (
            "이미 분쟁 장기화: 추가 구두 약속 금지. "
            "본사 연결·서면(사진·전표·대화 요약)만. Zalo는 사실만·24시간 내."
        ),
        "aftercare_ko": "사진·전표·대화 한 줄 요약 보관. 동일 이슈 반복 시 본사 공유.",
        "sense_check_ko": "눈: 접수 사진. 손: 전표 서명·마른얼룩 체크. 기록: 과실 여부 한 줄.",
        "success_rate_ko": "사진+전표+마른얼룩 동의: 방어 양호. 없으면 위험 — 다음 접수부터 필수.",
        "refuse_when_ko": (
            "폭언·협박·허위 주장 → 정중 중단·본사 연결. "
            "추가 무상 재처리·전액 환불 즉흥 약속 금지."
        ),
        "must_include_ko": "접수사진, 전표, 과실vs기존손상, 사과·보상안, 100%환불즉흥금지",
        "precheck_vi": (
            "Khiếu nại: bình tĩnh. Tìm ảnh nhận + phiếu + ghi chú trước. CẤM đáp cảm xúc."
        ),
        "why_vi": (
            "[Tại sao] Khiếu nại = nói bằng bằng chứng. "
            "Bình tĩnh → đối chiếu ảnh lúc nhận → lỗi cửa hàng: xin lỗi+phương án / "
            "hư sẵn: đưa ảnh / vết khô: chỉ tick đồng ý lúc nhận. "
            "CẤM hứa hoàn 100% nóng giận. Kéo dài → HQ + văn bản."
        ),
        "fresh_path_vi": (
            "(1)Hỏi: nhận lúc nào? có phiếu+ảnh? "
            "(2)So ảnh nhận vs hiện tại (lỗi shop / hư sẵn / đã cảnh báo vết khô). "
            "(3)Lỗi shop: 「Tôi đã đối chiếu ảnh. Xin lỗi. Tôi đề xuất phương án」. "
            "(4)Hư sẵn: 「Phần này đã có trên ảnh lúc nhận」→ đưa ảnh. "
            "(5)Vết khô: 「Khi nhận đã đồng ý có thể còn vết」→ kiểm tick phiếu. "
            "(6)CẤM nhận lỗi không ảnh; CẤM cãi lớn; CẤM hứa hoàn hết ngay."
        ),
        "dried_path_vi": (
            "Tranh chấp kéo dài: CẤM hứa miệng thêm. "
            "Nối HQ + lưu văn bản (ảnh/phiếu/tóm tắt). Zalo chỉ sự thật, trong 24 giờ."
        ),
        "aftercare_vi": "Lưu ảnh+phiếu+1 dòng tóm tắt. Lặp lại → báo HQ.",
        "sense_check_vi": "Mắt: ảnh nhận. Tay: chữ ký + tick vết khô. Ghi: có lỗi hay không.",
        "success_rate_vi": "Có ảnh+phiếu+đồng ý vết khô: phòng thủ tốt. Thiếu: rủi ro cao.",
        "refuse_when_vi": (
            "Đe dọa / đòi bồi không căn cứ → dừng lịch sự + HQ. "
            "CẤM hứa xử lý miễn phí / hoàn hết nóng giận."
        ),
        "must_include_vi": "ảnh nhận, phiếu, lỗi vs hư sẵn, xin lỗi+phương án, CẤM hoàn 100% nóng",
        "precheck_en": "Claim: stay calm. Pull intake photos+ticket+notes first. No emotional reply.",
        "why_en": (
            "[Why] Claims are evidence-based. "
            "Calm→compare intake photos→shop fault: apology+offer / prior damage: show photo / "
            "dried-stain: point to consent checkbox. "
            "Never impulsive 100% refund. Escalate long disputes to HQ in writing."
        ),
        "fresh_path_en": (
            "(1)Ask: intake date? ticket+photos? "
            "(2)Compare intake vs now (shop fault / prior damage / dried-stain consent). "
            "(3)Shop fault: 「Compared with intake photos. Sorry. Here is a remedy offer」. "
            "(4)Prior damage: 「This was already on the intake photo」→ show it. "
            "(5)Dried stain: 「You consented that residual was possible」→ ticket checkbox. "
            "(6)Never admit without photos; never shout; never promise full refund on impulse."
        ),
        "dried_path_en": (
            "Long dispute: no new verbal promises. "
            "HQ + written file (photos/ticket/summary). Zalo facts only within 24h."
        ),
        "aftercare_en": "Store photos+ticket+one-line summary. Repeat issues → share with HQ.",
        "sense_check_en": "Eyes: intake photo. Hand: signature+dried checkbox. Note: fault yes/no.",
        "success_rate_en": "Photos+ticket+dried consent: strong defense. Missing: high risk.",
        "refuse_when_en": (
            "Abuse/threats/false claims → polite stop + HQ. "
            "No impulsive free rework / full refund promise."
        ),
        "must_include_en": "intake photo, ticket, fault vs prior damage, apology+offer, no impulse 100% refund",
    },
    "I_CARE_LABEL": {
        "why_vi": (
            "[Tại sao] Nhãn = hợp đồng với vải. Không đoán ký hiệu. "
            "5 nhóm: (1)chậu giặt — số = max °C, tay = giặt tay, X = cấm nước "
            "(2)tam giác tẩy — trống = được, gạch = chỉ oxy, X = cấm "
            "(3)vuông sấy (4)bàn ủi chấm nhiệt (5)vòng dry-clean. Có X → TUÂN THỦ."
        ),
        "fresh_path_vi": (
            "(1)Hỏi: nhãn rõ? mờ thì chụp ảnh. "
            "(2)Đọc đủ 5 nhóm; ghi max °C + tẩy + sấy + ủi + dry. "
            "(3)Nói khách đúng theo nhãn. "
            "(4)Chậu X → dry / I_DRY_VS_WET. "
            "(5)Vải màu: thường chỉ oxy. "
            "(6)CẤM bỏ qua X. Nhãn mất → đường an toàn thấp + báo khách."
        ),
        "aftercare_vi": "Không cắt nhãn. Ghi tóm tắt ký hiệu trên phiếu nhận.",
        "sense_check_vi": "Mắt: đủ 5 nhóm. Tay: nhãn không rách.",
        "success_rate_vi": "Nhãn rõ: cao. Mờ/mất: chỉ đường an toàn.",
        "refuse_when_vi": "Khách bắt bất chấp X → từ chối + báo rủi ro hỏng.",
        "must_include_vi": "5 nhóm ký hiệu, tuân X, màu chỉ oxy, không đoán",
    },
}


def apply_ops_depth(drills: dict[str, dict[str, str]]) -> None:
    """Merge v12 depth into OPS_DRILLS in place (later keys win)."""
    for iid, fields in OPS_DEPTH_V12.items():
        cur = dict(drills.get(iid) or {})
        cur.update(fields)
        drills[iid] = cur


def education_for_ops_depth(item_id: str) -> dict[str, str]:
    return dict(OPS_DEPTH_V12.get(item_id) or {})
