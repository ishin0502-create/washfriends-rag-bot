# PROTOCOL XỬ LÝ v3.0 — MÁY GIẶT & MÁY SẤY
# 세탁 처리 프로토콜 v3.0 — 세탁기 & 건조기
# Wash Friends Professional Knowledge System
# Phiên bản: 3.0
# Alias: laundry_kb_v3_machine.md → this file (items_machine)
---

## NGUYÊN TẮC CỐT LÕI

Chương trình máy = kết hợp **vải + nhãn + vết bẩn**. Vết còn thì **không sấy** (nhiệt = cố định vết). Không chắc → chế độ tinh tế + phơi bóng mát.

Trả lời điểm chủ theo chuẩn Wash Friends: rõ bước, rõ hóa chất (mã E/D/B/A/N/S), rõ lực tay, kiểm tra trước khi sấy/ủi.

---
## PROTOCOL: Hướng dẫn cài máy giặt
**Tên**: Hướng dẫn cài máy giặt / 세탁기 설정 가이드 / Washer Settings Guide
**Độ khó**: ★★☆☆☆
**Hóa chất**: D3 / S1 (theo vải)
**Quy tắc vàng**: Đúng lượng bột. Quá nhiều = tồn dư. Nước cứng VN: xem I_WATER_HARDNESS + thêm xả.

| Bước | Thao tác | Lực tay | Chi tiết | Checkpoint |
|---|---|---|---|---|
| 1 | Chọn chế độ theo vải | 0 | Thường: cotton/poly. Tinh tế: len/lụa/rayon/mỏng. 60°C+: khăn/ga/bé (nhãn cho). Thể thao: mùi. | 📋 Không rõ → tinh tế |
| 2 | Bột đúng liều + xả | 0 | Nước cứng: +1 bậc bột + xả thêm. Down/bé: **bắt buộc** xả thêm. Không thay softener cho xả thừa. | 🖐️ Hết nhám bột |
| 3 | Kiểm trước sấy | 0 | Còn vết/mui/bot → xử lý lại, **cấm sấy**. | 👁️ Ánh sáng mạnh |

---

## PROTOCOL: Hướng dẫn cài máy sấy
**Tên**: Hướng dẫn cài máy sấy / 건조기 설정 가이드 / Dryer Settings Guide
**Độ khó**: ★★☆☆☆
**Hóa chất**: —
**Quy tắc vàng**: CẤM sấy: len, lụa, rayon, spandex, áo dài, da, nhiều mũ cấu trúc. Nghi ngờ → không sấy.

| Bước | Thao tác | Lực tay | Chi tiết | Checkpoint |
|---|---|---|---|---|
| 1 | Đọc nhãn + sạch vết | 0 | ○ sấy được / ❌ cấm. Vết sạch mới sấy. Đồ mới màu đậm: sấy riêng lần đầu. | 📋 Còn vết = dừng |
| 2 | Nhiệt theo nhóm | 0 | Cao: khăn. Vừa: cotton. Thấp: poly. Không nhiệt: thể thao/rất tinh tế. Tip VN: quạt + bóng mát thường đủ (<4h bắt đầu khô). | 📋 VN ưu tiên phơi |
| 3 | Sau sấy | 0 | Lấy ngay (nhàu). Vệ sinh lọc. Còn bột → xả lại. | 🖐️ Hết trơn bột |

---

## PROTOCOL: Liên kết Item GraphRAG
**Tên**: I_MACHINE_PROFILE / 세탁기·건조기 코스
**Độ khó**: ★☆☆☆☆
**Hóa chất**: —
**Quy tắc vàng**: Câu hỏi “máy giặt/sấy cài thế nào” → Item `I_MACHINE_PROFILE` (specialty education). Chi tiết ủi → `laundry_kb_v3_items_ironing.md`.

| Bước | Thao tác | Lực tay | Chi tiết | Checkpoint |
|---|---|---|---|---|
| 1 | Định tuyến | 0 | Máy = items_machine + I_MACHINE_PROFILE. Ủi = items_ironing + I_FINISHING. | 📋 Đúng file |
