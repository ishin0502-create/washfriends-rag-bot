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


L2_TEXTS: dict[str, dict[str, str]] = {
    "l2a_01": {
        "title_vi": "Vải × màu × tươi/khô — cotton, linen",
        "body_vi": (
            "[L2] Cotton/linen: trắng + tươi → thử góc rồi dùng hóa chất được phép.\n"
            "Trắng + khô → ngâm tẩy oxy lâu / enzyme qua đêm được. Màu + tươi → oxy chỉ để thử.\n"
            "Màu + khô → nguyên tắc cấm oxy, lặp giấm trắng."
        ),
        "title_en": "Fabric × color × fresh/dry — cotton, linen",
        "body_en": (
            "[L2] Cotton/linen: white+fresh → corner test, then allowed chemicals.\n"
            "White+dry → long oxygen soak / overnight enzyme OK. Colored+fresh → oxygen for test only.\n"
            "Colored+dry → no oxygen in principle; repeat white vinegar."
        ),
    },
    "l2a_02": {
        "title_vi": "Vải × màu — poly so với lụa/len",
        "body_vi": (
            "[L2] Poly/pha: oxy OK (trắng), trần 60°C. Màu khô: ưu tiên giấm và nước rửa chén.\n"
            "Lụa/len: cấm enzyme, oxy, javel, dung môi, oxalic. Chỉ xà phòng trung tính + nước lạnh.\n"
            "Nặng thì gửi chuyên gia là đúng."
        ),
        "title_en": "Fabric × color — poly vs silk/wool",
        "body_en": (
            "[L2] Poly/blend: oxygen OK (white), 60°C cap. Colored dry: vinegar and dish soap first.\n"
            "Silk/wool: no enzyme, oxygen, chlorine, solvent, oxalic. Neutral + cold water only.\n"
            "If severe, referring out is the right answer."
        ),
    },
    "l2a_03": {
        "title_vi": "Da, da lộn, acetate",
        "body_vi": (
            "[L2] Da, da lộn, acetate: cấm ngâm nước.\n"
            "Chăm sóc chuyên dụng hoặc gửi chuyên gia. Tiệm mới đừng ‘cho máy giặt một lần’."
        ),
        "title_en": "Leather, suede, acetate",
        "body_en": (
            "[L2] Leather, suede, acetate: no water soak at all.\n"
            "Specialty care or refer out. Beginners must not ‘just run the washer once’."
        ),
    },
    "l2b_01": {
        "title_vi": "Ba nhóm · tannin (cà phê, rượu, nước ép…)",
        "body_vi": (
            "[L2] Tannin: nước lạnh ngay → giấm trắng 1:4 → oxy chỉ cotton trắng.\n"
            "Nhiệt sớm cố định màu. Cấm oxy trên lụa/len.\n"
            "(Cà phê, trà, rượu vang, nước ép, xì dầu, trầu, nước mía, rượu trắng)"
        ),
        "title_en": "Three families · tannin (coffee, wine, juice…)",
        "body_en": (
            "[L2] Tannin: immediate cold water → white vinegar 1:4 → oxygen on white cotton only.\n"
            "Early heat sets dye. No oxygen on silk/wool.\n"
            "(Coffee, tea, wine, juice, soy, betel, sugarcane juice, white wine)"
        ),
    },
    "l2b_02": {
        "title_vi": "Ba nhóm · protein (máu, trứng, sữa…)",
        "body_vi": (
            "[L2] Protein: chỉ nước lạnh (cấm nóng) → enzyme (lụa/len: xà phòng trung tính) → giặt lạnh/ấm nhẹ.\n"
            "Nhiệt = nâu vĩnh viễn. Máu, trứng, sữa, mồ hôi, nôn, phân, nước tiểu, sữa mẹ cùng nhóm."
        ),
        "title_en": "Three families · protein (blood, egg, milk…)",
        "body_en": (
            "[L2] Protein: cold water only (no hot) → enzyme (silk/wool: neutral) → cold/lukewarm wash.\n"
            "Heat = permanent brown. Blood, egg, milk, sweat, vomit, feces, urine, breast milk are the same family."
        ),
    },
    "l2b_03": {
        "title_vi": "Ba nhóm · dầu–mỡ",
        "body_vi": (
            "[L2] Dầu–mỡ: bột hút (bột năng) → nước rửa chén → lipase nếu cần → hết nhờn mới sấy.\n"
            "Bị nhiệt cố định thì tỷ lệ thành công giảm mạnh. Cấm dung môi mạnh/nóng trên lụa/len.\n"
            "(Dầu ăn, bơ, mayo, nhớt máy, nhựa đường, son, kem chống nắng…)"
        ),
        "title_en": "Three families · oil–fat",
        "body_en": (
            "[L2] Oil–fat: absorb (starch) → dish soap → lipase if needed → dry only after slip is gone.\n"
            "Heat-set oil: success rate drops hard. No strong solvent/high heat on silk/wool.\n"
            "(Cooking oil, butter, mayo, engine oil, tar, lipstick, sunscreen…)"
        ),
    },
    "l2c_01": {
        "title_vi": "Màu/thuốc nhuộm (son, mực, thuốc nhuộm tóc…)",
        "body_vi": (
            "[L2] (1) Từ mặt trái (2) lót giấy thấm (3) chấm cồn hoặc acetone\n"
            "(4) thấm thẳng, khăn mới mỗi lần. Chà thì loang ngang.\n"
            "Acetate, rayon, phủ vinyl: tuyệt đối cấm acetone (làm tan sợi)."
        ),
        "title_en": "Dye stains (lipstick, ink, hair dye…)",
        "body_en": (
            "[L2] (1) From the back (2) blotter underneath (3) alcohol or acetone dab\n"
            "(4) vertical blot, new cloth each time. Rubbing spreads sideways.\n"
            "Acetate, rayon, vinyl coating: never acetone (it melts the fiber)."
        ),
    },
    "l2d_01": {
        "title_vi": "Cây quyết định tẩy oxy",
        "body_vi": (
            "[L2] ① Cotton/poly trắng hoặc màu ổn? Không thì dừng.\n"
            "② Thử góc 30 giây đạt? Không thì dừng.\n"
            "③ Oxy già 3% (cotton trắng) hoặc ngâm percarbonate ấm nhẹ (đúng trần nhiệt).\n"
            "Màu chưa rõ, lụa, len, da, nylon, spandex → cấm oxy."
        ),
        "title_en": "Oxygen-bleach decision tree",
        "body_en": (
            "[L2] ① White cotton/poly or stable color? Else stop.\n"
            "② 30s corner test pass? Else stop.\n"
            "③ 3% peroxide (white cotton) or lukewarm percarbonate soak (respect the cap).\n"
            "Unknown color, silk, wool, leather, nylon, spandex → no oxygen at all."
        ),
    },
    "l2e_01": {
        "title_vi": "Phai màu sang áo khác (dye transfer)",
        "body_vi": (
            "[L2] Tách khỏi máy ngay, cấm sấy (nhiệt cố định).\n"
            "Cotton/poly trắng riêng → ngâm oxy lâu rồi giặt lại.\n"
            "Màu, lụa, len → oxy chỉ thử, cấm javel, cân nhắc chuyên gia.\n"
            "Đã qua máy sấy = xếp lại là không phục hồi."
        ),
        "title_en": "Dye transfer",
        "body_en": (
            "[L2] Pull out of the washer immediately; no dryer (heat sets it).\n"
            "White cotton/poly alone → long oxygen soak, then rewash.\n"
            "Colored, silk, wool → oxygen test only, no chlorine, consider a specialist.\n"
            "Already through a dryer = reclassify as not recoverable."
        ),
    },
}


L3_TEXTS: dict[str, dict[str, str]] = {
    "l3a_01": {
        "title_vi": "Thứ tự lần 2·3 sau lần 1 thất bại",
        "body_vi": (
            "[L3] Lần 1 fail → đọc lại vải và vết còn → đúng nhóm khác rồi mới lần 2.\n"
            "Lần 2 cũng fail → báo lại cấp 2 (sạch một phần) → chấp nhận còn màu hoặc gửi chuyên gia.\n"
            "Javel không phải thuốc vạn năng (khử mùi, vàng, sữa bột, phai màu, lụa, len có thể nặng hơn)."
        ),
        "title_en": "2nd/3rd try after a failed 1st wash",
        "body_en": (
            "[L3] Failed 1st → re-judge fabric and leftover stain → confirm a different family, then 2nd try.\n"
            "2nd also fails → re-disclose grade 2 (partial) → accept residue or refer out.\n"
            "Chlorine is not universal (deodorant, yellowing, formula, transfer, silk, wool can worsen)."
        ),
    },
    "l3a_02": {
        "title_vi": "Cấm che bằng nhiệt",
        "body_vi": (
            "[L3] Cấm ủi/sấy cho ‘tạm che’ — khiếu nại sẽ nặng hơn.\n"
            "Còn màu, nhờn, mùi thì đừng thêm nhiệt."
        ),
        "title_en": "Do not hide stains with heat",
        "body_en": (
            "[L3] Do not iron/dry to ‘sort of hide it’ — claims get worse.\n"
            "If residue, slip, or smell remains, do not add heat."
        ),
    },
    "l3b_01": {
        "title_vi": "Đồ đặc biệt · da, phao, vest",
        "body_vi": (
            "[L3] Da, da lộn, lông thú: cấm ngâm nước · chuyên dụng/chuyên gia.\n"
            "Phao: chỉ chỗ bẩn, trung tính/ấm nhẹ. Ngâm cả áo cần chuyên dụng + sấy khô hẳn.\n"
            "Vest (len): chỉ chỗ vết, nhẹ. Cả áo nguyên tắc giặt khô."
        ),
        "title_en": "Specialty · leather, down, suits",
        "body_en": (
            "[L3] Leather, suede, fur: no soak · specialty/refer.\n"
            "Down: local neutral/lukewarm only. Full soak needs specialty + complete dry.\n"
            "Suit (wool): light spot only. Whole garment: dry-clean in principle."
        ),
    },
    "l3b_02": {
        "title_vi": "Đồ đặc biệt · áo chức năng, đồ trẻ",
        "body_vi": (
            "[L3] Chống nước/thể thao: cấm nước xả, oxy, javel · bột chuyên dụng.\n"
            "Đồ trẻ: cấm javel và hương mạnh. Oxy/enzyme thì xả thật kỹ.\n"
            "Chỉ phơi nắng khi hết màu dư."
        ),
        "title_en": "Specialty · technical wear, baby clothes",
        "body_en": (
            "[L3] Waterproof/sports: no softener, oxygen, chlorine · specialty detergent.\n"
            "Baby clothes: no chlorine or strong fragrance. Oxygen/enzyme: rinse thoroughly.\n"
            "Sun-dry only when no leftover color."
        ),
    },
    "l3c_01": {
        "title_vi": "Việt Nam · laterite (đất đỏ)",
        "body_vi": (
            "[L3] Cấm chà ướt và javel (sắt cố định).\n"
            "Khô hẳn → chải khô (đeo khẩu trang) → nước lạnh → (chỉ cotton/linen/poly) đường oxalic.\n"
            "Lụa/len: giấm thật nhẹ thôi · nặng thì chuyên gia."
        ),
        "title_en": "Vietnam · laterite (red earth)",
        "body_en": (
            "[L3] Never rub wet or use chlorine (iron sets).\n"
            "Fully dry → dry brush (mask) → cold water → (cotton/linen/poly only) oxalic path.\n"
            "Silk/wool: weak vinegar only · severe → specialist."
        ),
    },
    "l3c_02": {
        "title_vi": "Việt Nam · nhớt xe máy, nước mắm",
        "body_vi": (
            "[L3] Nhớt xe: lặp bột hút → khử mỡ (thông gió, cấm lửa) → nước rửa chén → hết nhờn mới sấy.\n"
            "Nước mắm: nước lạnh → enzyme → giấm trắng 1:4 (mùi) → oxy chỉ cotton trắng → xả kỹ."
        ),
        "title_en": "Vietnam · motorbike oil, fish sauce",
        "body_en": (
            "[L3] Bike oil: repeat absorb powder → degrease (ventilate, no flame) → dish soap → dry only with no slip.\n"
            "Fish sauce: cold water → enzyme → white vinegar 1:4 (odor) → oxygen on white cotton only → rinse well."
        ),
    },
    "l3c_03": {
        "title_vi": "Việt Nam · nước kimchi, mốc ẩm",
        "body_vi": (
            "[L3] Nước kimchi: bỏ cái đặc → mặt trái nước lạnh → nước rửa chén → giấm → oxy chỉ áo trắng (cấm oxy trên màu).\n"
            "Mốc: ngoài trời + PPE → phủi bào tử khô → giấm → oxy chỉ vải được phép. Da/lụa/len/nặng = chuyên gia."
        ),
        "title_en": "Vietnam · kimchi broth, damp mold",
        "body_en": (
            "[L3] Kimchi broth: remove solids → inside cold water → dish soap → vinegar → oxygen on white only (no oxygen on colored).\n"
            "Mold: outdoors + PPE → brush dry spores → vinegar → oxygen only on allowed fabric. Leather/silk/wool/heavy = specialist."
        ),
    },
    "l3d_01": {
        "title_vi": "Khiếu nại · ảnh nhận đồ, giấy đồng ý",
        "body_vi": (
            "[L3] Ảnh lúc nhận bắt buộc: nhãn · vết nguyên trạng · cận màu — 3 tấm (ánh sáng tự nhiên).\n"
            "Cấp 2·3: lưu giấy đồng ý hoặc tin nhắn Zalo.\n"
            "Tiệm mới cấm hứa bồi thường trước khi cấp trên quyết."
        ),
        "title_en": "Claims · intake photos, consent",
        "body_en": (
            "[L3] Intake photos required: label, stain as-is, color close-up — 3 shots (daylight).\n"
            "Grade 2–3: save a consent form or Zalo reply.\n"
            "Beginner shops must not promise payout before a senior decides."
        ),
    },
    "l3d_02": {
        "title_vi": "Ranh giới gửi chuyên gia",
        "body_vi": (
            "[L3] Xem ngay chuyên gia/từ chối:\n"
            "Lụa, len, da, lông thú, acetate / sơn dầu, bút dầu, keo 502, nhớt khô, mốc cũ\n"
            "/ phai màu đã qua máy sấy — cấm cố tại tiệm."
        ),
        "title_en": "When to refer out",
        "body_en": (
            "[L3] Refer or refuse immediately:\n"
            "Silk, wool, leather, fur, acetate / oil paint, oil marker, 502, dried engine oil, old mold\n"
            "/ dye transfer already through a dryer — no in-house force try."
        ),
    },
    "l3e_01": {
        "title_vi": "Câu nói khi gửi chuyên gia",
        "body_vi": (
            "[L3] 「Vết và vải này tiệm chúng tôi không xử lý an toàn được.\n"
            "Nếu cố, nguy cơ hỏng sợi và mất màu rất cao.\n"
            "Chúng tôi sẽ hướng dẫn gửi chuyên gia, hoặc trả đồ nếu quý khách không muốn nhận.」"
        ),
        "title_en": "Referral script",
        "body_en": (
            "[L3] 「This stain and fabric are not safe for us to treat in-shop.\n"
            "Trying anyway risks fiber damage and color loss.\n"
            "We can refer you to a specialist, or return the item if you prefer not to proceed.」"
        ),
    },
}


def lesson_title_body(lesson: dict[str, Any], lang: str) -> tuple[str, str]:
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    title = str(lesson.get("title") or "")
    body = str(lesson.get("body") or "")
    lid = str(lesson.get("id") or "")
    extra = L1_TEXTS.get(lid) or L2_TEXTS.get(lid) or L3_TEXTS.get(lid) or {}
    if lang == "vi":
        title = (extra.get("title_vi") or title).strip()
        body = (extra.get("body_vi") or body).strip()
    elif lang == "en":
        title = (extra.get("title_en") or title).strip()
        body = (extra.get("body_en") or body).strip()
    return title, body
