# -*- coding: utf-8 -*-
"""A/B/C/D choices for weekly exam banks. Keyword accept still grades free text."""
from __future__ import annotations

# id -> answer letter + choices per lang (exactly 4 lines A–D)
EXAM_MCQ: dict[str, dict] = {
    "l1e_label": {
        "answer": "B",
        "ko": ["A. 모두 세탁기 가능", "B. 삼각형=표백, 원=드라이, 손=손세탁", "C. 원=표백", "D. 삼각형=건조기"],
        "en": ["A. All machine-wash OK", "B. Triangle=bleach, circle=dry clean, hand=hand wash", "C. Circle=bleach", "D. Triangle=dryer"],
        "vi": ["A. Giặt máy tất cả được", "B. Tam giác=tẩy, tròn=giặt khô, tay=giặt tay", "C. Tròn=tẩy", "D. Tam giác=sấy"],
    },
    "l1e_temp_protein": {
        "answer": "B",
        "ko": ["A. 온수", "B. 찬물", "C. 건조기", "D. 다리미"],
        "en": ["A. Hot water", "B. Cold water", "C. Dryer", "D. Iron"],
        "vi": ["A. Nước nóng", "B. Nước lạnh", "C. Máy sấy", "D. Bàn ủi"],
    },
    "l1e_blot": {
        "answer": "A",
        "ko": ["A. 흰 천으로 수직 블롯", "B. 세게 문지르기", "C. 바로 건조기", "D. 락스 뿌리기"],
        "en": ["A. Vertical blot with white cloth", "B. Rub hard", "C. Dryer now", "D. Pour bleach"],
        "vi": ["A. Thấm thẳng khăn trắng", "B. Chà mạnh", "C. Sấy ngay", "D. Đổ javel"],
    },
    "l1e_heat": {
        "answer": "C",
        "ko": ["A. 예, 빨리 말리면 됨", "B. 예, 다리미만", "C. 아니오 — 열이 고착", "D. 상관없음"],
        "en": ["A. Yes, dry fast", "B. Yes, iron only", "C. No — heat sets the stain", "D. Does not matter"],
        "vi": ["A. Có, sấy nhanh", "B. Có, chỉ ủi", "C. Không — nhiệt cố định vết", "D. Không sao"],
    },
    "l1e_corner": {
        "answer": "A",
        "ko": ["A. 구석·안감 30초 테스트", "B. 바로 전면 도포", "C. 온수 담그기", "D. 건조기 먼저"],
        "en": ["A. Hidden-corner 30s test", "B. Apply all over now", "C. Soak hot", "D. Dryer first"],
        "vi": ["A. Thử góc khuất 30 giây", "B. Bôi cả mặt ngay", "C. Ngâm nóng", "D. Sấy trước"],
    },
    "l1e_mix": {
        "answer": "B",
        "ko": ["A. 식초+중성세제", "B. 식초+락스", "C. 찬물+식초", "D. 중성세제+물"],
        "en": ["A. Vinegar + mild soap", "B. Vinegar + chlorine bleach", "C. Cold water + vinegar", "D. Mild soap + water"],
        "vi": ["A. Giấm + xà phòng trung tính", "B. Giấm + javel", "C. Nước lạnh + giấm", "D. Xà phòng + nước"],
    },
    "l1e_ppe": {
        "answer": "A",
        "ko": ["A. 니트릴 장갑", "B. 면장갑만", "C. 장갑 불필요", "D. 비닐봉지"],
        "en": ["A. Nitrile gloves", "B. Cotton gloves only", "C. No gloves needed", "D. Plastic bag"],
        "vi": ["A. Găng nitrile", "B. Chỉ găng cotton", "C. Không cần găng", "D. Túi nilon"],
    },
    "l1e_refuse": {
        "answer": "B",
        "ko": ["A. 무리해서 시도", "B. 거절·전문 의뢰 안내", "C. 락스부터", "D. 건조기부터"],
        "en": ["A. Force a try", "B. Refuse / refer specialist", "C. Bleach first", "D. Dryer first"],
        "vi": ["A. Cố tẩy", "B. Từ chối / gửi chuyên gia", "C. Javel trước", "D. Sấy trước"],
    },
    "l1e_enzyme": {
        "answer": "A",
        "ko": ["A. 실크 또는 울", "B. 흰 면만", "C. 모든 폴리", "D. 데님만"],
        "en": ["A. Silk or wool", "B. White cotton only", "C. All polyester", "D. Denim only"],
        "vi": ["A. Lụa hoặc len", "B. Chỉ cotton trắng", "C. Mọi polyester", "D. Chỉ denim"],
    },
    "l1e_oxygen": {
        "answer": "A",
        "ko": ["A. 흰 면·폴리 또는 색 안정(구석 테스트)", "B. 실크 전부", "C. 울 전부", "D. 색 미확인 전부"],
        "en": ["A. White cotton/poly or color-stable (corner test)", "B. All silk", "C. All wool", "D. All unknown color"],
        "vi": ["A. Cotton/poly trắng hoặc màu ổn (thử góc)", "B. Mọi lụa", "C. Mọi len", "D. Mọi màu chưa rõ"],
    },
    "l1e_blood": {
        "answer": "A",
        "ko": ["A. 갈색으로 영구 고착", "B. 더 잘 지워짐", "C. 아무 일 없음", "D. 표백만 되면 됨"],
        "en": ["A. Sets brown permanently", "B. Comes out easier", "C. Nothing happens", "D. Bleach later is enough"],
        "vi": ["A. Nâu và cố định vĩnh viễn", "B. Dễ sạch hơn", "C. Không sao", "D. Tẩy sau cũng được"],
    },
    "l1e_coffee": {
        "answer": "B",
        "ko": ["A. 식초 1 : 물 1", "B. 식초 1 : 물 4", "C. 식초만", "D. 락스 1 : 물 4"],
        "en": ["A. Vinegar 1 : water 1", "B. Vinegar 1 : water 4", "C. Vinegar only", "D. Bleach 1 : water 4"],
        "vi": ["A. Giấm 1 : nước 1", "B. Giấm 1 : nước 4", "C. Chỉ giấm", "D. Javel 1 : nước 4"],
    },
    "l1e_oil": {
        "answer": "B",
        "ko": ["A. 색만 연하면 됨", "B. 미끄럼(기름기)이 없어야 함", "C. 냄새만 없으면 됨", "D. 바로 건조기"],
        "en": ["A. Color lighter is enough", "B. Slippery/oily feel must be gone", "C. Smell gone is enough", "D. Dryer immediately"],
        "vi": ["A. Màu nhạt là đủ", "B. Phải hết nhờn/dầu", "C. Hết mùi là đủ", "D. Sấy ngay"],
    },
    "l1e_ink": {
        "answer": "A",
        "ko": ["A. 옆으로·깊이 번짐", "B. 더 빨리 지워짐", "C. 원단이 하얘짐", "D. 아무 문제 없음"],
        "en": ["A. Spreads sideways and deeper", "B. Comes out faster", "C. Fabric turns white", "D. No problem"],
        "vi": ["A. Loang ngang và sâu", "B. Sạch nhanh hơn", "C. Vải trắng ra", "D. Không sao"],
    },
    "l1e_mud": {
        "answer": "B",
        "ko": ["A. 바로 물로 문지른다", "B. 말린 뒤 털고 솔질", "C. 온수에 담근다", "D. 건조기부터"],
        "en": ["A. Rub with water now", "B. Dry first, then brush off", "C. Soak hot", "D. Dryer first"],
        "vi": ["A. Chà nước ngay", "B. Để khô rồi chải", "C. Ngâm nóng", "D. Sấy trước"],
    },
    "l1e_grade": {
        "answer": "B",
        "ko": ["A. 등급 1", "B. 등급 2", "C. 등급 3", "D. 등급 없음"],
        "en": ["A. Grade 1", "B. Grade 2", "C. Grade 3", "D. No grade"],
        "vi": ["A. Cấp 1", "B. Cấp 2", "C. Cấp 3", "D. Không cấp"],
    },
    "l1e_care_x": {
        "answer": "B",
        "ko": ["A. 더 세게 세탁하라는 뜻", "B. 물세탁 금지(하지 말 것)", "C. 표백 가능", "D. 고온 가능"],
        "en": ["A. Wash harder", "B. Do not wash (crossed tub)", "C. Bleach OK", "D. High heat OK"],
        "vi": ["A. Giặt mạnh hơn", "B. Cấm giặt nước (gạch chéo)", "C. Được tẩy", "D. Được nhiệt cao"],
    },
    "l2e_cotton_dry_color": {
        "answer": "B",
        "ko": ["A. 예, 산소 바로", "B. 아니오 — 유색+마름은 산소 원칙 금지", "C. 락스만", "D. 건조기만"],
        "en": ["A. Yes, oxygen now", "B. No — colored+dry, oxygen off", "C. Chlorine only", "D. Dryer only"],
        "vi": ["A. Có, oxy ngay", "B. Không — màu+khô cấm oxy", "C. Chỉ javel", "D. Chỉ sấy"],
    },
    "l2e_silk_chem": {
        "answer": "C",
        "ko": ["A. 효소 OK", "B. 산소 OK", "C. 전부 금지 — 중성+찬물", "D. 락스 OK"],
        "en": ["A. Enzyme OK", "B. Oxygen OK", "C. All banned — mild + cold", "D. Chlorine OK"],
        "vi": ["A. Enzyme được", "B. Oxy được", "C. Cấm hết — trung tính + lạnh", "D. Javel được"],
    },
    "l2e_leather": {
        "answer": "B",
        "ko": ["A. 예, 세탁기 OK", "B. 아니오 — 침지 금지, 전용/전문", "C. 온수만", "D. 산소만"],
        "en": ["A. Yes, washer OK", "B. No soak — specialty/pro", "C. Hot only", "D. Oxygen only"],
        "vi": ["A. Có, máy giặt được", "B. Không ngâm — chăm sóc/chuyên gia", "C. Chỉ nóng", "D. Chỉ oxy"],
    },
    "l2e_tannin": {
        "answer": "A",
        "ko": ["A. 찬물 → 흰 식초 1:4", "B. 온수 → 락스", "C. 건조기 → 식초", "D. 다리미 → 산소"],
        "en": ["A. Cold → white vinegar 1:4", "B. Hot → bleach", "C. Dryer → vinegar", "D. Iron → oxygen"],
        "vi": ["A. Lạnh → giấm trắng 1:4", "B. Nóng → javel", "C. Sấy → giấm", "D. Ủi → oxy"],
    },
    "l2e_protein_heat": {
        "answer": "A",
        "ko": ["A. 갈색 영구 고착", "B. 더 잘 빠짐", "C. 표백 효과", "D. 아무 변화 없음"],
        "en": ["A. Brown permanent set", "B. Easier removal", "C. Bleach effect", "D. No change"],
        "vi": ["A. Nâu cố định", "B. Dễ sạch", "C. Như tẩy", "D. Không đổi"],
    },
    "l2e_oil_dry": {
        "answer": "A",
        "ko": ["A. 미끄럼(기름기)", "B. 색만", "C. 무게만", "D. 라벨만"],
        "en": ["A. Slippery/oily feel", "B. Color only", "C. Weight only", "D. Label only"],
        "vi": ["A. Cảm giác nhờn", "B. Chỉ màu", "C. Chỉ cân nặng", "D. Chỉ nhãn"],
    },
    "l2e_dye_blot": {
        "answer": "A",
        "ko": ["A. 문지르지 말고 블롯", "B. 세게 문지른다", "C. 바로 건조", "D. 락스 담금"],
        "en": ["A. Blot, do not rub", "B. Rub hard", "C. Dry now", "D. Soak bleach"],
        "vi": ["A. Thấm, không chà", "B. Chà mạnh", "C. Sấy ngay", "D. Ngâm javel"],
    },
    "l2e_acetone_ban": {
        "answer": "A",
        "ko": ["A. 아세테이트·트리아세테이트 금지", "B. 면만 금지", "C. 전부 OK", "D. 실크만 OK"],
        "en": ["A. Ban on acetate/triacetate", "B. Cotton only banned", "C. All OK", "D. Silk only OK"],
        "vi": ["A. Cấm acetate/triacetate", "B. Chỉ cấm cotton", "C. Tất cả được", "D. Chỉ lụa được"],
    },
    "l2e_oxygen_tree": {
        "answer": "A",
        "ko": ["A. 흰 면·폴리·색 안정 + 구석 테스트", "B. 실크 여부만", "C. 냄새만", "D. 라벨 색만"],
        "en": ["A. White cotton/poly/stable color + corner test", "B. Silk only", "C. Smell only", "D. Label color only"],
        "vi": ["A. Cotton/poly trắng/màu ổn + thử góc", "B. Chỉ lụa", "C. Chỉ mùi", "D. Chỉ màu nhãn"],
    },
    "l2e_oxygen_ban": {
        "answer": "A",
        "ko": ["A. 실크·울·가죽 등", "B. 흰 면만 금지", "C. 폴리만 금지", "D. 금지 원단 없음"],
        "en": ["A. Silk/wool/leather etc.", "B. White cotton only banned", "C. Poly only banned", "D. No ban"],
        "vi": ["A. Lụa/len/da…", "B. Chỉ cấm cotton trắng", "C. Chỉ cấm poly", "D. Không cấm"],
    },
    "l2e_dye_transfer": {
        "answer": "B",
        "ko": ["A. 건조기 OK", "B. 건조 금지 — 열고착", "C. 다리미 OK", "D. 상관없음"],
        "en": ["A. Dryer OK", "B. No heat — sets the transfer", "C. Iron OK", "D. Does not matter"],
        "vi": ["A. Sấy được", "B. Cấm nhiệt — cố định loang", "C. Ủi được", "D. Không sao"],
    },
    "l2e_dryer_transfer": {
        "answer": "B",
        "ko": ["A. 복원 가능", "B. 복원 불가(등급 3 계열)", "C. 식초만 하면 됨", "D. 산소만 하면 됨"],
        "en": ["A. Restorable", "B. Not restorable (grade-3 class)", "C. Vinegar enough", "D. Oxygen enough"],
        "vi": ["A. Phục hồi được", "B. Không phục hồi (cấp 3)", "C. Giấm là đủ", "D. Oxy là đủ"],
    },
    "l3e_retry_order": {
        "answer": "A",
        "ko": ["A. 원단·잔여 얼룩 재판단 후 2차", "B. 바로 락스", "C. 바로 건조기", "D. 순서 없음"],
        "en": ["A. Re-judge fabric/residue, then 2nd try", "B. Bleach now", "C. Dryer now", "D. No order"],
        "vi": ["A. Đánh giá lại vải/vết rồi lần 2", "B. Javel ngay", "C. Sấy ngay", "D. Không thứ tự"],
    },
    "l3e_no_heat_hide": {
        "answer": "B",
        "ko": ["A. 열로 감춘다", "B. 열로 감추지 않는다", "C. 다리미로 마무리", "D. 햇빛 건조"],
        "en": ["A. Hide with heat", "B. Do not hide with heat", "C. Iron to finish", "D. Sun dry"],
        "vi": ["A. Giấu bằng nhiệt", "B. Không giấu bằng nhiệt", "C. Ủi xong", "D. Phơi nắng"],
    },
    "l3e_grade2": {
        "answer": "B",
        "ko": ["A. 말하지 않는다", "B. 잔색 가능을 미리 고지", "C. 무조건 무료 재세탁", "D. 등급 1로 적는다"],
        "en": ["A. Say nothing", "B. Disclose residue risk first", "C. Always free rewash", "D. Write grade 1"],
        "vi": ["A. Không nói", "B. Báo trước còn màu", "C. Luôn giặt lại miễn phí", "D. Ghi cấp 1"],
    },
    "l3e_down_jacket": {
        "answer": "B",
        "ko": ["A. 예, 통째로 담가도 됨", "B. 아니오 — 국소만 중성·미온", "C. 락스 담금", "D. 고온 건조만"],
        "en": ["A. Yes, soak the whole jacket", "B. No — spot only, mild/lukewarm", "C. Bleach soak", "D. High-heat dry only"],
        "vi": ["A. Có, ngâm cả áo", "B. Không — chỉ chỗ bẩn, trung tính/ấm", "C. Ngâm javel", "D. Chỉ sấy nóng"],
    },
    "l3e_waterproof": {
        "answer": "B",
        "ko": ["A. 예, 유연제·산소 OK", "B. 아니오 — 유연제·산소·염소 금지", "C. 락스만 OK", "D. 상관없음"],
        "en": ["A. Yes, softener + oxygen OK", "B. No — no softener/oxygen/chlorine", "C. Chlorine only OK", "D. Does not matter"],
        "vi": ["A. Có, làm mềm + oxy được", "B. Không — cấm làm mềm/oxy/javel", "C. Chỉ javel được", "D. Không sao"],
    },
    "l3e_laterite": {
        "answer": "A",
        "ko": ["A. 철 고착·악화 (젖은 문지름·락스 금지)", "B. 더 잘 빠짐", "C. 표백 효과", "D. 아무 일 없음"],
        "en": ["A. Iron sets / worsens (no wet rub, no bleach)", "B. Comes out easier", "C. Bleach effect", "D. Nothing happens"],
        "vi": ["A. Sắt cố định/xấu đi (cấm chà ướt, javel)", "B. Dễ sạch hơn", "C. Như tẩy", "D. Không sao"],
    },
    "l3e_motorbike_oil": {
        "answer": "A",
        "ko": ["A. 미끄럼(기름기)이 없어야 함", "B. 색만 연하면 됨", "C. 바로 건조기", "D. 냄새만 없으면 됨"],
        "en": ["A. Slippery/oily feel must be gone", "B. Lighter color is enough", "C. Dryer now", "D. Smell gone is enough"],
        "vi": ["A. Phải hết nhờn/dầu", "B. Màu nhạt là đủ", "C. Sấy ngay", "D. Hết mùi là đủ"],
    },
    "l3e_kimchi_broth": {
        "answer": "B",
        "ko": ["A. 예, 유색에도 산소 OK", "B. 아니오 — 유색 산소 원칙 금지", "C. 락스부터", "D. 건조기부터"],
        "en": ["A. Yes, oxygen on colored cotton", "B. No — oxygen off on colored", "C. Bleach first", "D. Dryer first"],
        "vi": ["A. Có, oxy trên cotton màu", "B. Không — cấm oxy trên màu", "C. Javel trước", "D. Sấy trước"],
    },
    "l3e_mold_leather": {
        "answer": "B",
        "ko": ["A. 세탁기 침지", "B. 가죽 전용/전문, 물 담금 금지", "C. 산소표백", "D. 고온 건조"],
        "en": ["A. Washer soak", "B. Leather specialty; no soak", "C. Oxygen bleach", "D. High-heat dry"],
        "vi": ["A. Ngâm máy giặt", "B. Chăm sóc da/chuyên; không ngâm", "C. Tẩy oxy", "D. Sấy nóng"],
    },
    "l3e_claim_photo": {
        "answer": "A",
        "ko": ["A. 라벨·원상태·근접 3장(자연광)", "B. 기억만 한다", "C. 사진 1장만", "D. 나중에 찍는다"],
        "en": ["A. Label + stain + close-up, 3 shots in daylight", "B. Memory only", "C. One photo only", "D. Shoot later"],
        "vi": ["A. Nhãn + vết + cận, 3 ảnh ánh sáng tự nhiên", "B. Chỉ nhớ", "C. Chỉ 1 ảnh", "D. Chụp sau"],
    },
    "l3e_pro_refer": {
        "answer": "B",
        "ko": ["A. 예, 매장에서 복원 시도", "B. 아니오 — 불가·전문·등급 재분류", "C. 락스로 시도", "D. 열로 감추기"],
        "en": ["A. Yes, try in-shop restore", "B. No — not restorable; specialist/regrade", "C. Try bleach", "D. Hide with heat"],
        "vi": ["A. Có, tiệm tự phục hồi", "B. Không — không phục hồi; chuyên/xếp lại cấp", "C. Thử javel", "D. Giấu nhiệt"],
    },
    "l3e_bleach_not_universal": {
        "answer": "A",
        "ko": ["A. 악화·황변·손상 가능", "B. 만능으로 해결", "C. 실크에 특히 좋음", "D. 데오에 필수"],
        "en": ["A. Can worsen / yellow / damage", "B. Fixes everything", "C. Great on silk", "D. Required on deodorant"],
        "vi": ["A. Có thể xấu/vàng/hỏng", "B. Chữa hết", "C. Rất tốt cho lụa", "D. Bắt buộc với khử mùi"],
    },
}


def mcq_for(qid: str, lang: str) -> tuple[list[str], str]:
    row = EXAM_MCQ.get(str(qid or ""))
    if not row:
        return [], ""
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    choices = list(row.get(lang) or row.get("ko") or [])
    answer = str(row.get("answer") or "").strip().upper()[:1]
    return choices, answer
