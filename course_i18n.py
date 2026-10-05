# -*- coding: utf-8 -*-
"""Fixed VI/EN copy for sequential course cards. KO stays on LESSONS."""
from __future__ import annotations

from typing import Any

# L1 only for this ship. L2/L3 later.
L1_TEXTS: dict[str, dict[str, str]] = {
    "l1a_01": {
        "title_vi": "Nhãn vải 30 giây",
        "body_vi": (
            "[L1] Nhìn trước: tam giác (tẩy) · hình tròn (chỉ giặt khô) · dấu giặt tay.\n"
            "Bóng + mỏng + trơn → nghi lụa/acetate → tạm dừng mọi hóa chất mạnh."
        ),
        "title_en": "Care label in 30 seconds",
        "body_en": (
            "[L1] Check triangle (bleach), circle (dry-clean only), hand-wash mark first.\n"
            "Shiny + thin + slippery → suspect silk/acetate → hold all strong chemicals."
        ),
    },
    "l1a_02": {
        "title_vi": "Bốn mức nhiệt nước",
        "body_vi": (
            "[L1] Lạnh 15–20°C / ấm nhẹ 30–35°C / nóng 40–50°C / rất nóng 60°C+.\n"
            "Protein (máu, trứng, sữa, mồ hôi, nôn): luôn nước lạnh. Không chắc thì lạnh trước."
        ),
        "title_en": "Four water temperatures",
        "body_en": (
            "[L1] Cold 15–20°C / lukewarm 30–35°C / hot 40–50°C / very hot 60°C+.\n"
            "Protein (blood, egg, milk, sweat, vomit): cold water always. Unsure → cold first."
        ),
    },
    "l1a_03": {
        "title_vi": "Cấm chà · thấm ấn",
        "body_vi": (
            "[L1] Đặt khăn cotton trắng lên vết, ấn thẳng đứng để hút. Đổi khăn mới mỗi lần.\n"
            "Chà ngang đẩy thuốc nhuộm/dầu vào sâu. Nhóm màu: 3 phút đầu chỉ thấm."
        ),
        "title_en": "Do not rub · blot only",
        "body_en": (
            "[L1] White cotton on the stain; press straight down to absorb. New cloth each time.\n"
            "Sideways rubbing drives dye/oil deeper. Dye stains: blot only for the first 3 minutes."
        ),
    },
    "l1a_04": {
        "title_vi": "Kiểm tra ánh sáng mạnh trước khi sấy",
        "body_vi": (
            "[L1] Dưới ánh sáng mạnh: còn màu, nhờn dầu, mùi không.\n"
            "Còn một cái là cấm máy sấy · bàn ủi · nắng. Nhiệt = cố định vĩnh viễn."
        ),
        "title_en": "Strong-light check before drying",
        "body_en": (
            "[L1] Under strong light: leftover color, oil slip, or smell.\n"
            "Any one remaining → no dryer, iron, or sun. Heat = permanent set."
        ),
    },
    "l1a_05": {
        "title_vi": "Thử góc 30 giây",
        "body_vi": (
            "[L1] 1–2 giọt hóa chất ở gấu/lót/đường may → khăn trắng 30 giây.\n"
            "Không phai, loang, hỏng mới làm tiếp. Cồn, acetone, dung môi, tẩy oxy, oxalic: cấm nếu chưa thử."
        ),
        "title_en": "Corner test 30 seconds",
        "body_en": (
            "[L1] 1–2 drops on hem/lining/seam → white cloth 30 seconds.\n"
            "No bleed, spread, or damage, then continue. Alcohol, acetone, solvent, oxygen, oxalic: never skip the test."
        ),
    },
    "l1a_06": {
        "title_vi": "Ba cặp tuyệt đối không trộn",
        "body_vi": (
            "[L1] Giấm + javel / amoniac + javel / tẩy oxy + javel — nguy hiểm hoặc mất tác dụng.\n"
            "Thùng và bàn chải đã dùng javel phải xả sạch mới dùng hóa chất khác."
        ),
        "title_en": "Three mixes you never make",
        "body_en": (
            "[L1] Vinegar+chlorine bleach / ammonia+chlorine / oxygen+chlorine — dangerous or useless.\n"
            "Rinse bleach tubs and brushes fully before any other chemical."
        ),
    },
    "l1a_07": {
        "title_vi": "Ba đồ bảo hộ",
        "body_vi": (
            "[L1] Găng nitrile (máu, nôn, dung môi, oxalic, javel) / khẩu trang (bào tử, bụi) / thông gió (dung môi, javel).\n"
            "Không làm dung môi hay javel trong phòng kín."
        ),
        "title_en": "Three pieces of PPE",
        "body_en": (
            "[L1] Nitrile gloves (blood, vomit, solvent, oxalic, chlorine) / mask (spores, dust) / ventilation (solvent, chlorine).\n"
            "Do not use solvent or chlorine bleach in a closed room."
        ),
    },
    "l1a_08": {
        "title_vi": "Cổng từ chối — 6 tổ hợp",
        "body_vi": (
            "[L1→L3] Các trường hợp này tiệm mới không tự làm — báo không được lúc nhận hoặc từ chối:\n"
            "① Lụa/len/da/acetate + sơn dầu/bút dầu/keo 502\n"
            "② Phai màu đã qua máy sấy ③ Mốc cũ ngấm sâu\n"
            "④ Hóa chất không rõ ⑤ Dầu máy/nhựa đường trên lụa/len ⑥ Vết da/lông cần dung môi hữu cơ"
        ),
        "title_en": "Refuse gate — 6 combinations",
        "body_en": (
            "[L1→L3] Beginner shop must not solo these — disclose “cannot” at intake or refuse:\n"
            "① Silk/wool/leather/acetate + oil paint/oil marker/502 glue\n"
            "② Dye transfer already through a dryer ③ Old deep mold\n"
            "④ Unknown chemical ⑤ Engine oil/tar on silk/wool ⑥ Leather/fur needing organic solvent"
        ),
    },
    "l1a_09": {
        "title_vi": "Năm dụng cụ",
        "body_vi": (
            "[L1] Khăn cotton trắng / khăn giấy / bình xịt 200ml / bàn chải mềm (cỡ bàn chải trẻ em) /\n"
            "chậu ngâm nông / đồng hồ. Cấm khăn màu, lông cứng, bàn chải sắt, làm theo mắt."
        ),
        "title_en": "Five tools",
        "body_en": (
            "[L1] White cotton cloth / paper towel / 200ml spray / soft brush (baby-toothbrush grade) /\n"
            "shallow soak tub / timer. No colored cloth, stiff bristles, wire brush, or guessing by eye."
        ),
    },
    "l1a_10": {
        "title_vi": "Bốn nhóm hóa chất",
        "body_vi": (
            "[L1→L2] Enzyme — cấm lụa/len; trên 40°C thì enzyme chết.\n"
            "Tẩy oxy — chỉ cotton/poly trắng hoặc màu ổn. Javel — chỉ cotton/poly trắng.\n"
            "Dung môi — cấm acetate, rayon, phủ vinyl; bắt buộc thử góc và thông gió."
        ),
        "title_en": "Four chemical groups",
        "body_en": (
            "[L1→L2] Enzyme — no silk/wool; over 40°C it dies.\n"
            "Oxygen bleach — white cotton/poly or stable color only. Chlorine — white cotton/poly only.\n"
            "Solvent — no acetate, rayon, vinyl coating; corner test and ventilation required."
        ),
    },
    "l1b_blood": {
        "title_vi": "Vết mẫu · máu tươi",
        "body_vi": (
            "[L1] Mặt trái, nước lạnh 2–3 phút → nước muối (1L + 2 thìa) 15–30 phút → enzyme 15 phút (cấm lụa/len)\n"
            "→ giặt lạnh → ánh sáng mạnh. Cấm nước nóng và máy sấy. Không chà mạnh."
        ),
        "title_en": "Sample stain · fresh blood",
        "body_en": (
            "[L1] Inside, cold water 2–3 min → salt water (1L + 2 tbsp) 15–30 min → enzyme 15 min (no silk/wool)\n"
            "→ cold wash → strong light. No hot water or dryer. Do not scrub hard."
        ),
    },
    "l1b_coffee": {
        "title_vi": "Vết mẫu · cà phê đen tươi",
        "body_vi": (
            "[L1] Mặt trái, thấm nước lạnh → giấm trắng 1:4 (40ml giấm + 160ml nước) 5–10 phút\n"
            "→ tẩy oxy chỉ cotton trắng 15–30 phút (thử góc) → giặt ấm nhẹ → ánh sáng mạnh. Cấm oxy trên lụa/len."
        ),
        "title_en": "Sample stain · fresh black coffee",
        "body_en": (
            "[L1] Inside, cold-water blot → white vinegar 1:4 (40ml vinegar + 160ml water) 5–10 min\n"
            "→ oxygen on white cotton only 15–30 min (corner test) → lukewarm wash → strong light. No oxygen on silk/wool."
        ),
    },
    "l1b_oil": {
        "title_vi": "Vết mẫu · dầu ăn tươi",
        "body_vi": (
            "[L1] Bột năng/bột mì 10–30 phút → phủi → 1–2 giọt nước rửa chén, ấm nhẹ 5–10 phút, chải nhẹ\n"
            "→ xả → giặt → chỉ sấy khi hết nhờn."
        ),
        "title_en": "Sample stain · fresh cooking oil",
        "body_en": (
            "[L1] Starch/flour 10–30 min → brush off → 1–2 drops dish soap, lukewarm 5–10 min, light brush\n"
            "→ rinse → wash → dry only after the slippery feel is gone."
        ),
    },
    "l1b_ink": {
        "title_vi": "Vết mẫu · mực bút bi tươi",
        "body_vi": (
            "[L1] Isopropanol 70% — thử góc → lót giấy thấm, từ mặt trái thấm thẳng đứng\n"
            "(khăn trắng mới mỗi lần) → giặt lạnh → ánh sáng mạnh. Cấm chà (loang)."
        ),
        "title_en": "Sample stain · fresh ballpoint",
        "body_en": (
            "[L1] 70% isopropyl — corner test → blotter under, blot straight from the back\n"
            "(new white cloth each time) → cold wash → strong light. Do not rub (it spreads)."
        ),
    },
    "l1b_mud": {
        "title_vi": "Vết mẫu · bùn khô",
        "body_vi": (
            "[L1] Để khô hẳn → ra ngoài phủi và chải mềm → giặt với xà phòng\n"
            "→ còn màu thì giấm trắng 1:4 → ánh sáng mạnh. Đừng chà khi còn ướt. Đất đỏ laterite → đường L3."
        ),
        "title_en": "Sample stain · dried mud",
        "body_en": (
            "[L1] Fully dry → outdoors, brush off with a soft brush → detergent wash\n"
            "→ leftover color: white vinegar 1:4 → strong light. Do not rub while wet. Red laterite → L3 path."
        ),
    },
    "l1c_intake": {
        "title_vi": "Nhận đồ 3 phút",
        "body_vi": (
            "[L1] ① Vết gì · khi nào · đã giặt chưa ② Vải · màu\n"
            "③ Ba mức thành công (thử / một phần / không được) + đồng ý chụp ảnh\n"
            "④ Lụa, len, da, acetate: hỏi cấp trên."
        ),
        "title_en": "Intake in 3 minutes",
        "body_en": (
            "[L1] ① Stain, when, already washed? ② Fabric, color\n"
            "③ Three success bands (try / partial / cannot) + photo consent\n"
            "④ Silk, wool, leather, acetate: check with a senior."
        ),
    },
    "l1d_grades": {
        "title_vi": "Ba câu từ chối / báo trước",
        "body_vi": (
            "[L1] Cấp 1: Có thể thử nhưng không cam kết sạch hết.\n"
            "Cấp 2: Khó sạch hết, có thể còn màu. Bạn muốn làm tiếp?\n"
            "Cấp 3: Tiệm không xử lý an toàn được. Chúng tôi hướng dẫn gửi chuyên gia."
        ),
        "title_en": "Three-grade disclosure lines",
        "body_en": (
            "[L1] Grade 1: We can try, but full removal is not guaranteed.\n"
            "Grade 2: Full removal is hard; residue may remain. Shall we proceed?\n"
            "Grade 3: We cannot treat this safely in-shop. We will refer you to a specialist."
        ),
    },
}


def lesson_title_body(lesson: dict[str, Any], lang: str) -> tuple[str, str]:
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    title = str(lesson.get("title") or "")
    body = str(lesson.get("body") or "")
    extra = L1_TEXTS.get(str(lesson.get("id") or ""), {})
    if lang == "vi":
        title = (extra.get("title_vi") or title).strip()
        body = (extra.get("body_vi") or body).strip()
    elif lang == "en":
        title = (extra.get("title_en") or title).strip()
        body = (extra.get("body_en") or body).strip()
    return title, body
