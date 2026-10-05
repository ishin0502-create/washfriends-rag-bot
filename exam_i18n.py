# -*- coding: utf-8 -*-
"""VI/EN text for weekly exam banks. KO stays on the bank items."""
from __future__ import annotations

from typing import Any

# id -> q_en, q_vi, explain_en, explain_vi, accept_extra (regex)
TEXTS: dict[str, dict[str, str]] = {
    "l1e_label": {
        "q_en": "On a care label, what do the triangle, circle, and hand-wash marks mean? (short)",
        "q_vi": "Trên nhãn bảo quản, tam giác, hình tròn và dấu giặt tay nghĩa là gì? (ngắn)",
        "explain_en": "Triangle=bleach, circle=dry clean, hand-wash mark=hand wash first.",
        "explain_vi": "Tam giác=tẩy, hình tròn=giặt khô, dấu giặt tay=ưu tiên giặt tay.",
        "accept_extra": r"bleach|dry\s*clean|hand\s*wash|tẩy|giặt\s*khô|giat\s*kho|giặt\s*tay|giat\s*tay",
    },
    "l1e_temp_protein": {
        "q_en": "For protein stains (blood, egg, milk), what water temperature first?",
        "q_vi": "Vết protein (máu, trứng, sữa) phải dùng nước thế nào lúc đầu?",
        "explain_en": "Protein: cold water first. Hot water/dryer sets a brown stain.",
        "explain_vi": "Protein: nước lạnh trước. Nước nóng/máy sấy làm nâu, cố định.",
        "accept_extra": r"cold|nước\s*lạnh|nuoc\s*lanh|lạnh",
    },
    "l1e_blot": {
        "q_en": "For dye/ink, do not rub — what should you do first?",
        "q_vi": "Vết thuốc nhuộm/mực: không chà — phải làm gì trước?",
        "explain_en": "Blot straight down with a white cloth. Sideways rubbing spreads dye.",
        "explain_vi": "Thấm thẳng đứng bằng khăn trắng. Chà ngang làm loang.",
        "accept_extra": r"blot|press|absorb|thấm|tham|ấn|an\s*xuống|khăn\s*trắng",
    },
    "l1e_heat": {
        "q_en": "Residue color, oil slip, or smell left — OK to use dryer/iron? (yes/no + why)",
        "q_vi": "Còn màu, nhờn dầu hoặc mùi — được dùng máy sấy/bàn ủi không? (có/không + lý do)",
        "explain_en": "No. Heat permanently sets the stain. Check in strong light first.",
        "explain_vi": "Không. Nhiệt cố định vết. Kiểm tra dưới ánh sáng mạnh rồi mới sấy.",
        "accept_extra": r"no|không|khong|cấm|cam|không\s*được",
    },
    "l1e_corner": {
        "q_en": "Before alcohol, acetone, or oxygen bleach, what 30-second check is required?",
        "q_vi": "Trước cồn, acetone hoặc tẩy oxy, phải kiểm tra 30 giây thế nào?",
        "explain_en": "Hidden-corner test 30s (hem/lining/seam). No bleed/damage, then continue.",
        "explain_vi": "Thử góc khuất 30 giây (gấu/lót/đường may). Không phai/hỏng mới làm tiếp.",
        "accept_extra": r"corner|patch\s*test|hem|lining|góc|goc|thử|thu|đường\s*may|lót",
    },
    "l1e_mix": {
        "q_en": "Name one mix you must never combine. (example: A + B)",
        "q_vi": "Nêu một cặp hóa chất tuyệt đối không trộn. (ví dụ: A + B)",
        "explain_en": "Vinegar+bleach / ammonia+bleach / oxygen+chlorine bleach — dangerous or useless.",
        "explain_vi": "Giấm+javel / amoniac+javel / tẩy oxy+javel — nguy hiểm hoặc mất tác dụng.",
        "accept_extra": r"vinegar.*bleach|ammonia.*bleach|giấm.*javel|giam.*javel|amoniac.*javel",
    },
    "l1e_ppe": {
        "q_en": "For blood, vomit, solvent, or bleach work, which gloves are the default?",
        "q_vi": "Làm máu, nôn, dung môi, javel thì găng tay mặc định loại nào?",
        "explain_en": "Nitrile gloves (+ mask/ventilation if needed).",
        "explain_vi": "Găng nitrile (+ khẩu trang/thông gió nếu cần).",
        "accept_extra": r"nitrile|rubber|găng|gang|nitrile",
    },
    "l1e_refuse": {
        "q_en": "Oil paint on silk: should a beginner shop force a try, or refuse / refer to a specialist?",
        "q_vi": "Sơn dầu trên lụa: tiệm mới nên cố tẩy, hay từ chối / gửi chuyên gia?",
        "explain_en": "Refuse/refer first — specialist handoff, not a forced attempt.",
        "explain_vi": "Từ chối/gửi chuyên gia trước — không cố tẩy.",
        "accept_extra": r"refuse|refer|specialist|từ\s*chối|tu\s*choi|chuyên|chuyen",
    },
    "l1e_enzyme": {
        "q_en": "Name one fabric that must not get enzyme detergent.",
        "q_vi": "Nêu một loại vải không được dùng enzyme.",
        "explain_en": "No enzyme on silk/wool. Over 40°C also weakens enzyme.",
        "explain_vi": "Cấm enzyme trên lụa/len. Trên 40°C enzyme cũng yếu.",
        "accept_extra": r"silk|wool|lụa|lua|len|wool",
    },
    "l1e_oxygen": {
        "q_en": "Which clothes may get oxygen bleach? (fabric/color, short)",
        "q_vi": "Tẩy oxy chỉ dùng cho áo nào? (vải/màu, ngắn)",
        "explain_en": "White cotton/poly or color-stable dyed (corner test). No silk/wool/unknown color.",
        "explain_vi": "Cotton/poly trắng hoặc màu ổn (thử góc). Cấm lụa/len/màu chưa rõ.",
        "accept_extra": r"white|cotton|poly|trắng|trang|cotton|màu\s*ổn",
    },
    "l1e_blood": {
        "q_en": "What happens if you use hot water or a dryer on fresh blood?",
        "q_vi": "Máu tươi mà dùng nước nóng hoặc máy sấy thì sao?",
        "explain_en": "Protein sets brown permanently. Start with cold water.",
        "explain_vi": "Protein nâu và cố định. Bắt đầu nước lạnh.",
        "accept_extra": r"set|permanent|brown|cố\s*định|co\s*dinh|nâu|nau",
    },
    "l1e_coffee": {
        "q_en": "White vinegar : water ratio for fresh black coffee? (e.g. 1:4)",
        "q_vi": "Tỷ lệ giấm trắng : nước cho cà phê đen tươi? (ví dụ 1:4)",
        "explain_en": "White vinegar 1 : water 4 (example 40ml vinegar + 160ml water).",
        "explain_vi": "Giấm trắng 1 : nước 4 (ví dụ 40ml giấm + 160ml nước).",
        "accept_extra": r"1\s*:\s*4|one\s*to\s*four|1\s*\/\s*4",
    },
    "l1e_oil": {
        "q_en": "Before putting cooking-oil stains in the dryer, which feel must be gone?",
        "q_vi": "Vết dầu ăn trước khi sấy, cảm giác nào phải hết?",
        "explain_en": "Dry only after the slippery/oily feel is gone.",
        "explain_vi": "Chỉ sấy khi hết nhờn/dầu.",
        "accept_extra": r"slip|oily|grease|nhờn|nhon|dầu|dau",
    },
    "l1e_ink": {
        "q_en": "Why must you not rub ballpoint ink while using alcohol?",
        "q_vi": "Tẩy mực bút bi bằng cồn, vì sao không được chà?",
        "explain_en": "Rubbing spreads ink sideways and deeper. Vertical blot, new white cloth each time.",
        "explain_vi": "Chà làm mực loang ngang và sâu. Thấm thẳng, mỗi lần khăn trắng mới.",
        "accept_extra": r"spread|bleed|deeper|loang|lan|sâu|sau",
    },
    "l1e_mud": {
        "q_en": "Dried mud: wash/rub with water immediately, or dry first then brush off?",
        "q_vi": "Bùn khô: giặt/chà nước ngay, hay để khô rồi chải?",
        "explain_en": "Fully dry, then brush outdoors with a soft brush. Wet rubbing drives mud in.",
        "explain_vi": "Khô hẳn, ra ngoài chải bàn chải mềm. Chà ướt đẩy bùn sâu.",
        "accept_extra": r"dry|brush|khô|kho|chải|chai|bàn\s*chải",
    },
    "l1e_grade": {
        "q_en": "Telling the guest ‘full removal is hard; residue may remain’ is grade 1, 2, or 3?",
        "q_vi": "Báo khách ‘khó sạch hết, có thể còn màu’ là cấp 1, 2 hay 3?",
        "explain_en": "Grade 2 = partial removal possible; residue may remain — disclose.",
        "explain_vi": "Cấp 2 = có thể sạch một phần, còn màu — phải báo trước.",
        "accept_extra": r"two|grade\s*2|cấp\s*2|cap\s*2",
    },
    "l2e_cotton_dry_color": {
        "q_en": "Dried stain on colored cotton/linen: is oxygen bleach allowed in principle? (yes/no + short)",
        "q_vi": "Vết khô trên cotton/linen màu: nguyên tắc có được tẩy oxy không? (có/không + ngắn)",
        "explain_en": "Colored + dry → oxygen no. Repeat white vinegar first.",
        "explain_vi": "Màu + khô → cấm oxy. Ưu tiên giấm trắng lặp lại.",
        "accept_extra": r"no|không|khong|vinegar|giấm|giam",
    },
    "l2e_silk_chem": {
        "q_en": "On silk/wool, may you use enzyme, oxygen, chlorine, or solvent? (short)",
        "q_vi": "Lụa/len: enzyme, oxy, javel, dung môi — cái nào được? (ngắn)",
        "explain_en": "Silk/wool: no enzyme/oxygen/chlorine/solvent/oxalic. Neutral + cold water only.",
        "explain_vi": "Lụa/len: cấm enzyme/oxy/javel/dung môi/oxalic. Chỉ trung tính + nước lạnh.",
        "accept_extra": r"none|no|không|khong|cấm|neutral|trung\s*tính|nước\s*lạnh",
    },
    "l2e_leather": {
        "q_en": "May leather, suede, or acetate go fully into a washing machine?",
        "q_vi": "Da, da lộn, acetate có được cho cả áo vào máy giặt không?",
        "explain_en": "No soaking. Specialty care or refer out.",
        "explain_vi": "Cấm ngâm nước. Chăm sóc chuyên dụng hoặc gửi chuyên gia.",
        "accept_extra": r"no|không|khong|cấm|specialist|chuyên",
    },
    "l2e_tannin": {
        "q_en": "Basic order for tannin stains (coffee/wine)? (cold water → ?)",
        "q_vi": "Thứ tự cơ bản vết tannin (cà phê/rượu vang)? (nước lạnh → ?)",
        "explain_en": "Immediate cold water → white vinegar 1:4 → oxygen on white cotton only. No early heat.",
        "explain_vi": "Nước lạnh ngay → giấm trắng 1:4 → oxy chỉ cotton trắng. Cấm nhiệt sớm.",
        "accept_extra": r"vinegar|1\s*:\s*4|giấm|giam|cold|nước\s*lạnh",
    },
    "l2e_protein_heat": {
        "q_en": "What happens if you hit protein (blood/egg/milk) with hot water first?",
        "q_vi": "Protein (máu/trứng/sữa) mà nước nóng trước thì sao?",
        "explain_en": "Heat sets protein brown permanently. Cold water only.",
        "explain_vi": "Nhiệt làm protein nâu, cố định. Chỉ nước lạnh.",
        "accept_extra": r"set|brown|permanent|cố\s*định|nâu|nau",
    },
    "l2e_oil_dry": {
        "q_en": "Before drying oil/fat stains, which feel must be gone?",
        "q_vi": "Vết dầu/mỡ trước khi sấy, cảm giác nào phải hết?",
        "explain_en": "Dry only after slip/grease is gone. Heat-set oil is much harder.",
        "explain_vi": "Hết nhờn mới sấy. Dầu bị nhiệt cố định thì rất khó.",
        "accept_extra": r"slip|grease|oily|nhờn|nhon|dầu",
    },
    "l2e_dye_blot": {
        "q_en": "Lipstick/ink dye: do not rub — what instead?",
        "q_vi": "Son/mực: không chà — làm cách nào?",
        "explain_en": "From the back, blotter underneath, vertical blot. Rubbing spreads dye.",
        "explain_vi": "Từ mặt trái, lót giấy thấm, thấm thẳng. Chà làm loang.",
        "accept_extra": r"blot|press|thấm|tham|mặt\s*trái|giấy\s*thấm",
    },
    "l2e_acetone_ban": {
        "q_en": "Name one fabric that must never get acetone.",
        "q_vi": "Nêu một loại vải tuyệt đối không acetone.",
        "explain_en": "Acetate, rayon, vinyl coating — acetone melts the fiber.",
        "explain_vi": "Acetate, rayon, phủ vinyl — acetone làm tan sợi.",
        "accept_extra": r"acetate|rayon|vinyl|coating",
    },
    "l2e_oxygen_tree": {
        "q_en": "Name two checks before oxygen bleach. (fabric + test)",
        "q_vi": "Hai việc phải kiểm trước tẩy oxy? (vải + thử)",
        "explain_en": "White cotton/poly or stable color + 30s corner test pass.",
        "explain_vi": "Cotton/poly trắng hoặc màu ổn + thử góc 30 giây đạt.",
        "accept_extra": r"white|cotton|corner|test|trắng|thử\s*góc|poly",
    },
    "l2e_oxygen_ban": {
        "q_en": "Name one fabric that must not get oxygen bleach.",
        "q_vi": "Nêu một loại vải không được tẩy oxy.",
        "explain_en": "No oxygen on silk, wool, leather, nylon, spandex, or unknown color.",
        "explain_vi": "Cấm oxy trên lụa, len, da, nylon, spandex, màu chưa rõ.",
        "accept_extra": r"silk|wool|leather|nylon|spandex|lụa|len|da",
    },
    "l2e_dye_transfer": {
        "q_en": "If dye transferred from another garment, is the dryer OK?",
        "q_vi": "Bị phai màu sang áo khác, được cho máy sấy không?",
        "explain_en": "No dryer — heat sets transfer. Separate and treat first.",
        "explain_vi": "Cấm sấy — nhiệt cố định màu loang. Tách và xử lý trước.",
        "accept_extra": r"no|không|khong|cấm|set",
    },
    "l2e_dryer_transfer": {
        "q_en": "Dye transfer that already went through a dryer: recoverable or not?",
        "q_vi": "Màu loang đã qua máy sấy: phục hồi được hay không?",
        "explain_en": "Dryer-passed transfer = not recoverable (grade-3 type).",
        "explain_vi": "Đã sấy = không phục hồi (cấp 3).",
        "accept_extra": r"not|impossible|no|không|khong|cấp\s*3|grade\s*3",
    },
    "l3e_retry_order": {
        "q_en": "After a failed 1st wash, what must you do before a 2nd try? (re-read fabric/family)",
        "q_vi": "Lần 1 thất bại, trước lần 2 phải làm gì? (đọc lại vải/nhóm vết)",
        "explain_en": "Failed 1st → re-judge fabric and leftover stain → confirm a different family, then 2nd try.",
        "explain_vi": "Lần 1 fail → đọc lại vải và vết còn → đúng nhóm khác rồi mới lần 2.",
        "accept_extra": r"re-?judge|fabric|family|đọc\s*lại|doc\s*lai|vải|nhóm",
    },
    "l3e_no_heat_hide": {
        "q_en": "If residue, slip, or smell remains, may you ‘hide’ it with iron/dryer?",
        "q_vi": "Còn màu, nhờn, mùi — được ‘che’ bằng ủi/sấy không?",
        "explain_en": "No hiding with heat — claims get worse. Do not apply heat.",
        "explain_vi": "Cấm che bằng nhiệt — khiếu nại nặng hơn. Không ủi/sấy.",
        "accept_extra": r"no|không|khong|cấm",
    },
    "l3e_grade2": {
        "q_en": "If the 2nd try also fails, which grade idea must the owner tell the guest first?",
        "q_vi": "Lần 2 cũng fail, chủ tiệm phải nói với khách khái niệm cấp nào trước?",
        "explain_en": "Re-disclose grade 2 (partial removal) → accept residue or refer out.",
        "explain_vi": "Báo lại cấp 2 (sạch một phần) → chấp nhận còn màu hoặc gửi chuyên gia.",
        "accept_extra": r"grade\s*2|two|cấp\s*2|cap\s*2|partial",
    },
    "l3e_down_jacket": {
        "q_en": "May you fully soak a down jacket in water to wash it?",
        "q_vi": "Áo lông vũ (phao) có được ngâm cả áo để giặt không?",
        "explain_en": "Down: local neutral/lukewarm only. Full soak needs specialty + full dry.",
        "explain_vi": "Phao: chỉ chỗ bẩn, trung tính/ấm. Ngâm cả áo cần chuyên dụng + sấy khô hẳn.",
        "accept_extra": r"no|không|khong|local|spot|chỗ|trung\s*tính",
    },
    "l3e_waterproof": {
        "q_en": "On waterproof/sports shells, may you use fabric softener or oxygen bleach?",
        "q_vi": "Áo chống nước/thể thao: được dùng nước xả vải hoặc tẩy oxy không?",
        "explain_en": "Waterproof/sports: no softener/oxygen/chlorine — specialty detergent.",
        "explain_vi": "Chống nước/thể thao: cấm xả vải/oxy/javel — chỉ bột chuyên dụng.",
        "accept_extra": r"no|không|khong|cấm|specialty|chuyên",
    },
    "l3e_laterite": {
        "q_en": "Laterite (red earth): what if you rub it wet or use chlorine bleach?",
        "q_vi": "Đất laterite (đỏ): chà ướt hoặc dùng javel thì sao?",
        "explain_en": "Never rub wet or use chlorine (iron set). Dry, then dry brush.",
        "explain_vi": "Cấm chà ướt và javel (sắt cố định). Để khô rồi chải khô.",
        "accept_extra": r"set|worse|no|không|brush|dry|chải|cấm",
    },
    "l3e_motorbike_oil": {
        "q_en": "After treating motorbike oil, which feel must be gone before the dryer?",
        "q_vi": "Xử lý nhớt xe máy xong, cảm giác nào phải hết trước khi sấy?",
        "explain_en": "Absorb, degrease, dish soap, then dry only with no slip.",
        "explain_vi": "Hút, khử mỡ, nước rửa chén, hết nhờn mới sấy.",
        "accept_extra": r"slip|grease|nhờn|nhon|dầu|degrease",
    },
    "l3e_kimchi_broth": {
        "q_en": "Kimchi broth on colored cotton: is oxygen bleach allowed in principle?",
        "q_vi": "Nước kimchi trên cotton màu: nguyên tắc có được tẩy oxy không?",
        "explain_en": "No oxygen on colored. Cold water, detergent, vinegar → oxygen on white only.",
        "explain_vi": "Cấm oxy trên màu. Nước lạnh, xà phòng, giấm → oxy chỉ áo trắng.",
        "accept_extra": r"no|không|khong|cấm|vinegar|giấm|white",
    },
    "l3e_mold_leather": {
        "q_en": "Heavy mold on leather/silk/wool: may the shop force oxygen bleach?",
        "q_vi": "Mốc nặng trên da/lụa/len: tiệm có được cố tẩy oxy không?",
        "explain_en": "Leather/silk/wool/heavy = specialist. Oxygen path only on allowed fabrics.",
        "explain_vi": "Da/lụa/len/nặng = chuyên gia. Oxy chỉ vải được phép.",
        "accept_extra": r"specialist|refer|no|không|chuyên|cấm",
    },
    "l3e_claim_photo": {
        "q_en": "For claims / grade 2–3 intake, how many photos and under what light? (short)",
        "q_vi": "Khiếu nại / nhận cấp 2–3: mấy ảnh, ánh sáng thế nào? (ngắn)",
        "explain_en": "3 photos in daylight: label, stain as-is, color close-up. Consent + save on Zalo.",
        "explain_vi": "3 ảnh ánh sáng tự nhiên: nhãn, vết nguyên trạng, cận màu. Giấy đồng ý + lưu Zalo.",
        "accept_extra": r"3|three|daylight|natural|ba|ánh\s*sáng|nhãn|label",
    },
    "l3e_pro_refer": {
        "q_en": "Dye transfer that already went through a dryer — may the shop try to restore it in-house?",
        "q_vi": "Màu loang đã qua máy sấy — tiệm có được tự phục hồi không?",
        "explain_en": "No in-house force try — specialist and re-grade.",
        "explain_vi": "Cấm cố tại tiệm — chuyên gia và xếp lại cấp.",
        "accept_extra": r"no|không|khong|specialist|chuyên|grade\s*3|cấp\s*3",
    },
    "l3e_bleach_not_universal": {
        "q_en": "What usually happens if you use chlorine bleach on deodorant, formula milk, or silk stains?",
        "q_vi": "Javel cho vết khử mùi, sữa bột, lụa thì thường ra sao?",
        "explain_en": "Chlorine is not universal — deodorant yellowing, formula, transfer, silk/wool can worsen.",
        "explain_vi": "Javel không phải thuốc vạn năng — khử mùi/vàng, sữa bột, phai màu, lụa/len có thể nặng hơn.",
        "accept_extra": r"worse|yellow|damage|no|không|xấu|vàng|cấm",
    },
}

_SUFFIX = {
    "ko": "\n(짧게 정답만 보내 주세요)",
    "en": "\n(Short answer — English or Korean keywords OK)",
    "vi": "\n(Trả lời ngắn — từ khóa Việt/Hàn OK)",
}


def localized_bank_item(it: dict[str, Any], lang: str, source: str) -> dict[str, str]:
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    extra = TEXTS.get(str(it.get("id") or ""), {})
    if lang == "en":
        q = (extra.get("q_en") or it.get("q") or "").strip()
        explain = (extra.get("explain_en") or it.get("explain") or "").strip()
    elif lang == "vi":
        q = (extra.get("q_vi") or it.get("q") or "").strip()
        explain = (extra.get("explain_vi") or it.get("explain") or "").strip()
    else:
        q = (it.get("q") or "").strip()
        explain = (it.get("explain") or "").strip()
    accept = str(it.get("accept") or "")
    more = (extra.get("accept_extra") or "").strip()
    if more:
        accept = f"{accept}|{more}" if accept else more
    return {
        "id": str(it.get("id") or ""),
        "q": q + _SUFFIX[lang],
        "accept": accept,
        "explain": explain,
        "lang": lang,
        "source": source,
    }
