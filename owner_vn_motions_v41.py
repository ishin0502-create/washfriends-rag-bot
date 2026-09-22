# -*- coding: utf-8 -*-
"""VN L2 hand motions KO/VI/EN — enrich existing + new specialty (no % rates)."""
from __future__ import annotations

_START = {"ko": "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n\n", "vi": "▼ Bắt đầu — làm lần lượt từ trên xuống\n\n", "en": "▼ Start — follow steps in order\n\n"}


def _s(lang: str, n: int, title: str, body: str) -> str:
    if lang == "vi":
        return f"Bước {n}. {title}\n─────\n{body.strip()}\n"
    if lang == "en":
        return f"Step {n}. {title}\n─────\n{body.strip()}\n"
    return f"Step {n}. {title}\n─────\n{body.strip()}\n"


def _pack(lang: str, steps: list[tuple[str, str]]) -> str:
    return _START[lang] + "\n".join(_s(lang, i, t, b) for i, (t, b) in enumerate(steps, 1))


def _fish(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Báo mùi · xả lạnh", "Báo trước: có thể còn mùi. Chỉ nước lạnh 15–20°C, 2–3 phút. Không chà."),
            ("Enzyme", "Bôi enzyme, để 30 phút ở nước ấm nhẹ 30–35°C. Trên 50°C enzyme chết. Lụa/len → trung tính."),
            ("Oxy (áo trắng)", "Còn màu: 1L nước ấm nhẹ + 1 muỗng oxy, 30 phút. Áo màu bỏ qua."),
            ("Giấm khử mùi", "Giấm 1 : nước 4, ngâm 20–30 phút → xả lạnh."),
            ("Giặt · kiểm mùi", "Giặt ấm nhẹ. Còn mùi → lặp giấm. Phơi nắng 2–3 tiếng giúp khử mùi. Cấm javel."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Disclose odor · cold rinse", "Tell customer odor may remain. Cold water 15–20°C, 2–3 min. Do not rub."),
            ("Enzyme", "Apply enzyme 30 min at lukewarm 30–35°C. Above 50°C kills enzyme. Silk/wool → neutral only."),
            ("Oxygen (whites)", "If color left: 1L lukewarm + 1 tbsp oxygen, 30 min. Skip on colors."),
            ("Vinegar for odor", "Vinegar 1 : water 4, soak 20–30 min → cold rinse."),
            ("Wash · smell check", "Wash lukewarm. Odor left → repeat vinegar. Sun 2–3h helps. No chlorine bleach."),
        ])
    return _pack("ko", [
        ("냄새 고지 · 찬물 헹굼", "손님께 냄새가 남을 수 있다고 먼저 말씀하세요. 찬물(15~20°C) 2~3분. 문지르지 마세요."),
        ("효소로 단백질", "효소를 바르고 미지근(30~35°C)에서 30분. 50°C↑면 효소가 죽어요. 실크·울→중성만."),
        ("산소(흰옷만)", "색 남으면: 미지근 1L + 산소 큰술 1, 30분. 유색은 건너뛰세요."),
        ("식초로 냄새", "식초 1 : 물 4, 20~30분 담금 → 찬물 헹굼."),
        ("세탁 · 냄새 확인", "미지근 세탁. 냄새 남으면 식초 반복. 직사광선 2~3시간 탈취에 도움. 락스 금지."),
    ])


def _shrimp(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Báo khó · lạnh", "Mắm tôm mùi rất mạnh — báo cần 2–3 lần. Xả lạnh."),
            ("Baking soda", "2 muỗng baking + ít nước → hỗn hợp sệt, bôi 30 phút (hút mùi) → xả."),
            ("Enzyme → giấm", "Enzyme 30 phút → giấm 1:4 ngâm 30 phút."),
            ("Giặt · lặp", "Giặt. Còn mùi → lặp baking+enzyme+giấm. Cấm javel / che bằng nước hoa."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Hard odor · cold", "Shrimp paste is very strong — disclose 2–3 rounds may be needed. Cold rinse."),
            ("Baking soda paste", "2 tbsp baking soda + little water, paste 30 min → rinse."),
            ("Enzyme → vinegar", "Enzyme 30 min → vinegar 1:4 soak 30 min."),
            ("Wash · repeat", "Wash. Odor left → repeat. No chlorine / perfume cover-up."),
        ])
    return _pack("ko", [
        ("강한 냄새 고지 · 찬물", "맘톰은 냄새가 매우 세요 — 2~3회 필요할 수 있다고 고지. 찬물 헹굼."),
        ("베이킹소다 페이스트", "베이킹소다 2큰술+물 소량 반죽, 30분(냄새 흡착) → 헹굼."),
        ("효소 → 식초", "효소 30분 → 식초 1:4 30분 담금."),
        ("세탁 · 반복", "세탁. 냄새 남으면 반복. 락스·향수 덮기 금지."),
    ])


def _curry(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Xả lạnh · không chà", "Nghệ/cà ri dễ loang — xả lạnh, không chà."),
            ("Nước rửa chén", "Màu tan dầu: bôi nước rửa chén 10 phút → xả ấm nhẹ 35–40°C."),
            ("Oxy trắng", "Áo trắng: oxy 30 phút (thêm nếu cần, tối đa 2 giờ)."),
            ("Giặt + phơi nắng", "Giặt xong phơi nắng 2–3 tiếng — UV làm nhạt curcumin. Trong nhà dễ còn vàng."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Cold rinse · no rub", "Turmeric spreads — cold rinse, do not rub."),
            ("Dish soap", "Oil-soluble dye: dish soap 10 min → lukewarm rinse 35–40°C."),
            ("Oxygen whites", "Whites: oxygen 30 min (extend up to 2h)."),
            ("Wash + sun", "After wash, sun 2–3h — UV fades curcumin. Indoor dry may leave yellow."),
        ])
    return _pack("ko", [
        ("찬물 · 문지르지 마세요", "강황·카레는 번져요. 찬물 헹굼, 문지르지 마세요."),
        ("주방세제", "지용성 색소: 주방세제 10분 → 미지근(35~40°C) 헹굼."),
        ("산소(흰옷)", "흰옷: 산소 30분(필요 시 추가, 최대 2시간)."),
        ("세탁 + 직사광선", "세탁 후 직사광선 2~3시간 — 자외선이 커큐민을 옅게 해요. 실내 건조는 잔색 남기 쉬움."),
    ])


def _betel(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Báo khó", "Trầu/cau gần như thuốc nhuộm — báo dễ còn vết."),
            ("Thấm lạnh", "Xả/thấm lạnh. Cấm chà."),
            ("Giấm 1:4", "Giấm 1:4, 15 phút → thấm khăn."),
            ("Cồn · oxy trắng", "Chấm cồn 5–10 lần. Áo trắng: oxy 30 phút. Giặt."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Hard stain disclose", "Betel is near a natural dye — residual likely."),
            ("Cold blot", "Cold blot. Do not rub."),
            ("Vinegar 1:4", "Vinegar 1:4, 15 min → blot."),
            ("Alcohol · oxygen", "Alcohol blot 5–10×. Whites: oxygen 30 min. Wash."),
        ])
    return _pack("ko", [
        ("어려움 고지", "빈랑·짜우는 천연 염료에 가깝습니다 — 잔색 가능하다고 고지하세요."),
        ("찬물 흡수", "찬물로 흡수. 문지르지 마세요."),
        ("식초 1:4", "식초 1:4, 15분 → 천으로 찍기."),
        ("알코올 · 산소", "알코올 블롯 5~10회. 흰옷 산소 30분. 세탁."),
    ])


def _mildew(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("PPE · khô phủi", "Găng + khẩu trang. Phủi bào tử khi còn khô (làm ướt trước dễ ngấm). Ngoài trời/thông gió."),
            ("Trắng: oxy · màu: giấm", "Trắng: 2 muỗng oxy / 1L ấm nhẹ, 1 giờ. Màu: giấm 1:2, 30 phút. Không trộn javel+giấm."),
            ("Giặt · khô hẳn", "Giặt. Phơi nắng đến khô hẳn — chưa khô dễ mốc lại. Báo khách phòng ẩm."),
        ])
    if lang == "en":
        return _pack("en", [
            ("PPE · dry brush", "Gloves + mask. Brush spores while dry (wetting drives spores in). Outdoors/ventilate."),
            ("White oxygen · color vinegar", "White: 2 tbsp oxygen / 1L lukewarm, 1h. Color: vinegar 1:2, 30 min. Never mix chlorine+vinegar."),
            ("Wash · fully dry", "Wash. Sun until bone-dry — damp storage regrows mold. Advise dehumidifier."),
        ])
    return _pack("ko", [
        ("PPE · 마른 채 털기", "장갑·마스크. 마른 상태에서 포자 털기(먼저 적시면 더 먹음). 야외·환기."),
        ("흰옷 산소 · 유색 식초", "흰옷: 산소 큰술 2 / 1L 미온, 1시간. 유색: 식초 1:2, 30분. 락스+식초 혼합 금지."),
        ("세탁 · 완전 건조", "세탁. 직사광선으로 완전히 마를 때까지. 덜 마르면 재발. 제습·보관 안내."),
    ])


def _motorbike(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Tiền xử lý", "Nước rửa chén nguyên chất 15–20 phút → xả ấm ~40°C. Lặp nếu cần. Thông gió."),
            ("Chấm cồn", "Còn dầu: chấm cồn khăn trắng. Cấm sấy khi còn nhờn."),
            ("Oxy trắng · giặt", "Áo trắng oxy 30 phút. Giặt ấm nhẹ."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Pre-treat", "Neat dish soap 15–20 min → lukewarm ~40°C rinse. Repeat. Ventilate."),
            ("Alcohol blot", "If oil left: alcohol on white cloth. No dryer while greasy."),
            ("Oxygen · wash", "Whites: oxygen 30 min. Wash lukewarm."),
        ])
    return _pack("ko", [
        ("전처리", "주방세제 원액 15~20분 → 미지근(~40°C) 헹굼. 필요 시 반복. 환기."),
        ("알코올 블롯", "기름 남으면 흰 천에 알코올. 미끄러운 채 건조기 금지."),
        ("산소·세탁", "흰옷 산소 30분. 미지근 세탁."),
    ])


def _sunscreen(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Dầu/silicon", "Nước rửa chén nguyên 15 phút → xả ấm nhẹ."),
            ("Ố vàng", "Áo trắng: oxy 30 phút nếu còn vàng. Cấm javel (vàng cố định)."),
            ("Giặt", "Giặt. Nhắc khách xử lý đều để khỏi tích tụ."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Oil/silicone", "Neat dish soap 15 min → lukewarm rinse."),
            ("Yellow cast", "Whites: oxygen 30 min if yellow left. No chlorine (sets yellow)."),
            ("Wash", "Wash. Advise regular pre-treat to avoid buildup."),
        ])
    return _pack("ko", [
        ("오일·실리콘", "주방세제 원액 15분 → 미지근 헹굼."),
        ("노란 자국", "흰옷: 남으면 산소 30분. 락스 금지(황변 고착)."),
        ("세탁", "세탁. 누적 방지로 정기 전처리 안내."),
    ])


def _laterite(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Để khô · phủi", "Ướt mà chà càng ngấm. Khô hẳn rồi phủi."),
            ("Giấm / chanh", "Giấm hoặc nước chanh 15 phút (axit hòa sắt oxit) → xả."),
            ("Xà phòng · oxy", "Nước rửa chén 10 phút. Áo trắng oxy 30 phút. Giặt."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Dry · brush", "Rubbing wet drives clay in. Fully dry then brush."),
            ("Vinegar / lemon", "Vinegar or lemon 15 min (acid dissolves iron oxide) → rinse."),
            ("Soap · oxygen", "Dish soap 10 min. Whites oxygen 30 min. Wash."),
        ])
    return _pack("ko", [
        ("말려 털기", "젖은 채 문지르면 더 박혀요. 완전 건조 후 솔로 털기."),
        ("식초·레몬", "식초 또는 레몬즙 15분(산이 산화철을 녹임) → 헹굼."),
        ("세제 · 산소", "주방세제 10분. 흰옷 산소 30분. 세탁."),
    ])


def _mangosteen(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Báo rất khó", "Măng cụt gần thuốc nhuộm — báo khó sạch hết. Áo màu: ưu tiên chuyên."),
            ("Xả lạnh ngay", "Càng sớm càng tốt."),
            ("Cồn · oxy", "Chấm cồn. Áo trắng: oxy 1–2 giờ. Giặt + phơi nắng."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Mangosteen — very hard", "Near natural dye — residual likely. Colors: consider specialist."),
            ("Cold rinse ASAP", "Faster is better."),
            ("Alcohol · oxygen", "Alcohol blot. Whites: oxygen 1–2h. Wash + sun."),
        ])
    return _pack("ko", [
        ("매우 어려움 고지", "망고스틴은 천연 염료에 가깝습니다 — 완전 제거 어렵다고 고지. 유색은 전문 우선."),
        ("즉시 찬물", "빠를수록 좋아요."),
        ("알코올 · 산소", "알코올 블롯. 흰옷 산소 1~2시간. 세탁+직사광선."),
    ])


def _durian(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Dầu trước", "Nước rửa chén 10 phút → xả."),
            ("Baking soda", "Bột baking paste 30 phút (hút mùi) → xả."),
            ("Giấm · giặt · nắng", "Giấm 1:4, 20 phút. Giặt. Phơi nắng 3–4 tiếng. Có thể cần 2–3 lần."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Durian fat first", "Dish soap 10 min → rinse."),
            ("Baking soda", "Paste 30 min for odor → rinse."),
            ("Vinegar · wash · sun", "Vinegar 1:4, 20 min. Wash. Sun 3–4h. May need 2–3 rounds."),
        ])
    return _pack("ko", [
        ("지방 먼저", "주방세제 10분 → 헹굼."),
        ("베이킹소다", "페이스트 30분(냄새 흡착) → 헹굼."),
        ("식초 · 세탁 · 햇빛", "식초 1:4, 20분. 세탁. 직사광선 3~4시간. 2~3회 필요할 수 있음."),
    ])


def _jackfruit(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Dầu ăn hòa nhựa", "Nhựa mít tan trong dầu, không tan nước. Thoa dầu ăn, xoa nhẹ → rồi nước rửa chén lấy dầu."),
            ("Xả đường", "Xả lạnh lấy đường."),
            ("Oxy · giặt", "Áo trắng oxy 30 phút. Giặt."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Cooking oil on latex", "Sap dissolves in oil, not water. Rub little cooking oil → then dish soap to remove oil."),
            ("Sugar rinse", "Cold rinse for sugar."),
            ("Oxygen · wash", "Whites oxygen 30 min. Wash."),
        ])
    return _pack("ko", [
        ("식용유로 수액 녹이기", "미 수액은 물에 안 녹고 기름에 녹아요. 식용유 소량 문지른 뒤 → 주방세제로 기름 제거."),
        ("당분 헹굼", "찬물로 당분 헹굼."),
        ("산소 · 세탁", "흰옷 산소 30분. 세탁."),
    ])


def _banh_xeo(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Tinh bột trước", "Gạt khô tinh bột → xả lạnh."),
            ("Dầu dừa", "Ấm nhẹ ~40°C làm tan → nước rửa chén 10 phút."),
            ("Màu nghệ", "Nước rửa chén hoặc cồn → oxy trắng → giặt + phơi nắng."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Starch first", "Scrape dry starch → cold rinse."),
            ("Coconut oil", "Lukewarm ~40°C to melt → dish soap 10 min."),
            ("Turmeric dye", "Dish soap or alcohol → oxygen whites → wash + sun."),
        ])
    return _pack("ko", [
        ("전분 먼저", "마른 전분 긁기 → 찬물 헹굼."),
        ("코코넛 오일", "미지근(~40°C)으로 녹인 뒤 주방세제 10분."),
        ("강황 색소", "주방세제 또는 알코올 → 흰옷 산소 → 세탁+직사광선."),
    ])


def _dragon(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Xả lạnh ngay", "Tan nước — xả sớm thì dễ ra."),
            ("Oxy nếu còn", "Áo trắng oxy 30 phút."),
            ("Giặt", "Giặt bình thường."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Cold rinse ASAP", "Water-soluble — early rinse works well."),
            ("Oxygen if needed", "Whites: oxygen 30 min."),
            ("Wash", "Normal wash."),
        ])
    return _pack("ko", [
        ("즉시 찬물", "수용성 — 빨리 헹구면 잘 빠져요."),
        ("산소(필요 시)", "흰옷 잔색이면 산소 30분."),
        ("세탁", "일반 세탁."),
    ])


def _mango(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Xả lạnh", "Lấy đường/xơ."),
            ("Nước rửa chén", "Carotene tan dầu — 10 phút."),
            ("Oxy · nắng", "Áo trắng oxy 30 phút. Giặt + phơi nắng."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Cold rinse", "Remove sugar/fiber."),
            ("Dish soap", "Carotene is oil-soluble — 10 min."),
            ("Oxygen · sun", "Whites oxygen 30 min. Wash + sun."),
        ])
    return _pack("ko", [
        ("찬물 헹굼", "당분·섬유질 제거."),
        ("주방세제", "카로틴은 지용성 — 10분."),
        ("산소 · 햇빛", "흰옷 산소 30분. 세탁+직사광선."),
    ])


def _rambutan(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [("Xả lạnh", "Chủ yếu đường."), ("Oxy nhẹ", "Còn màu: oxy trắng 15 phút."), ("Giặt", "Giặt.")])
    if lang == "en":
        return _pack("en", [("Cold rinse", "Mostly sugar."), ("Light oxygen", "If color: whites 15 min."), ("Wash", "Wash.")])
    return _pack("ko", [("찬물 헹굼", "당분 위주."), ("산소 약하게", "잔색이면 흰옷 15분."), ("세탁", "세탁.")])


def _coconut(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Làm tan ấm", "Dầu dừa đông khi mát — xả ấm ~40°C trước. Đừng chà khi còn đặc."),
            ("Nước rửa chén", "Nguyên chất 15 phút → xả ấm."),
            ("Giặt", "Giặt. Còn nhờn → không sấy."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Melt first", "Solid when cool — lukewarm ~40°C first. Do not rub while hard."),
            ("Dish soap", "Neat 15 min → lukewarm rinse."),
            ("Wash", "Wash. No dryer while greasy."),
        ])
    return _pack("ko", [
        ("먼저 녹이기", "차가우면 굳어요 — 미지근(~40°C)으로 녹인 뒤. 굳은 채 문지르지 마세요."),
        ("주방세제", "원액 15분 → 미지근 헹굼."),
        ("세탁", "세탁. 미끄러운 채 건조기 금지."),
    ])


def _incense(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Khô phủi", "Ướt chà → carbon ngấm. Phủi khô / dán băng keo."),
            ("Nước rửa chén", "10 phút lấy dầu nhang."),
            ("Giặt · giấm nếu mùi", "Giặt. Còn mùi: giấm 1:4, 10 phút."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Dry remove", "Wet rub drives carbon in. Dry brush / tape."),
            ("Dish soap", "10 min for incense oil."),
            ("Wash · vinegar if odor", "Wash. Odor: vinegar 1:4, 10 min."),
        ])
    return _pack("ko", [
        ("건식 제거", "젖은 채 문지르면 탄소가 박혀요. 마른 채 털기/테이프."),
        ("주방세제", "향유 10분."),
        ("세탁 · 냄새면 식초", "세탁. 냄새 남으면 식초 1:4, 10분."),
    ])


def _sa_te(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Dầu trước", "Nước rửa chén 5 phút → xả ấm nhẹ. Không chà (màu ớt loang)."),
            ("Cồn lấy màu ớt", "Chấm cồn 70% 5–10 lần → xả lạnh."),
            ("Oxy · giặt", "Áo trắng oxy 30 phút. Giặt + phơi nắng."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Oil first", "Dish soap 5 min → lukewarm rinse. Do not rub (chili spreads)."),
            ("Alcohol for chili", "IPA 70% blot 5–10× → cold rinse."),
            ("Oxygen · wash", "Whites oxygen 30 min. Wash + sun."),
        ])
    return _pack("ko", [
        ("기름 먼저", "주방세제 5분 → 미지근 헹굼. 문지르지 마세요(고추 색소 번짐)."),
        ("알코올로 고추 색소", "IPA 70% 찍어 빼기 5~10회 → 찬물 헹굼."),
        ("산소 · 세탁", "흰옷 산소 30분. 세탁+직사광선."),
    ])


def _nuoc_cham(lang: str) -> str:
    if lang == "vi":
        return _pack("vi", [
            ("Xả đường", "Xả lạnh trước (đường trong nước chấm)."),
            ("Enzyme", "Enzyme 30 phút (protein nước mắm)."),
            ("Cồn nếu ớt · giấm mùi", "Còn đỏ: chấm cồn. Còn mùi: giấm 1:4. Giặt + thông gió."),
        ])
    if lang == "en":
        return _pack("en", [
            ("Rinse sugar", "Cold rinse first (sugar in dipping sauce)."),
            ("Enzyme", "Enzyme 30 min (fish-sauce protein)."),
            ("Alcohol if chili · vinegar odor", "Red left: alcohol. Odor: vinegar 1:4. Wash + air."),
        ])
    return _pack("ko", [
        ("당분 헹굼", "찬물로 먼저(디핑소스 설탕)."),
        ("효소", "효소 30분(피시소스 단백질)."),
        ("고추면 알코올 · 냄새면 식초", "빨간 잔색: 알코올. 냄새: 식초 1:4. 세탁+통풍."),
    ])


def _chili(lang: str) -> str:
    return _sa_te(lang)


_BUILDERS = {
    "S_FISH_SAUCE": _fish,
    "S_SHRIMP_PASTE": _shrimp,
    "S_CURRY": _curry,
    "S_BETEL": _betel,
    "S_MILDEW": _mildew,
    "S_MOTORBIKE_OIL": _motorbike,
    "S_SUNSCREEN": _sunscreen,
    "S_LATERITE": _laterite,
    "S_CHILI": _chili,
    "S_VN_MANGOSTEEN": _mangosteen,
    "S_VN_DURIAN": _durian,
    "S_VN_JACKFRUIT": _jackfruit,
    "S_VN_BANH_XEO": _banh_xeo,
    "S_VN_DRAGON_FRUIT": _dragon,
    "S_VN_MANGO": _mango,
    "S_VN_RAMBUTAN": _rambutan,
    "S_VN_COCONUT_OIL": _coconut,
    "S_VN_INCENSE_ASH": _incense,
    "S_VN_SA_TE": _sa_te,
    "S_VN_NUOC_CHAM": _nuoc_cham,
}


def motions_for(sid: str, lang: str) -> str:
    fn = _BUILDERS.get(sid)
    if not fn:
        return ""
    lang = lang if lang in {"ko", "vi", "en"} else "ko"
    return fn(lang)


def all_motion_maps() -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    ko, vi, en = {}, {}, {}
    for sid in _BUILDERS:
        ko[sid] = motions_for(sid, "ko")
        vi[sid] = motions_for(sid, "vi")
        en[sid] = motions_for(sid, "en")
    return ko, vi, en


# Clarity extras (setdefault merge) — language-keyed outlook
EXTRA_STATUS_KO = {
    "S_FISH_SAUCE": (
        "◆ 【먼저 확인】 느억맘·액젓·피시소스\n"
        "· 방금 묻었나요, 이미 말랐나요?\n"
        "· 방금 묻음 → 냄새가 덜 밸 수 있음 · 마름·열 거침 → 냄새 반복·잔취 가능\n"
        "· 온수·건조기를 먼저 쓰지 마세요 · 락스 금지 · 냄새 완전 제거는 보장하지 마세요"
    ),
    "S_VN_MANGOSTEEN": "◆ 【먼저 확인】 망고스틴\n· 매우 강한 보라 색소 — 잔색 고지 필수\n· 유색·실크는 전문 검토",
    "S_VN_DURIAN": "◆ 【먼저 확인】 두리안\n· 색보다 냄새 · 1회에 안 빠질 수 있음 — 고지",
    "S_VN_BANH_XEO": "◆ 【먼저 확인】 반쎄오\n· 전분→오일→강황 순서 · 복합 얼룩",
}
EXTRA_STATUS_VI = {
    "S_FISH_SAUCE": "◆ 【Kiểm tra trước】 Nước mắm\n· Mới → ít mùi hơn · Khô → có thể lặp · Nhiệt → mùi cố định\n· Cấm javel",
    "S_VN_MANGOSTEEN": "◆ 【Kiểm tra trước】 Măng cụt\n· Màu rất mạnh — báo còn vết\n· Áo màu/lụa: xem chuyên",
    "S_VN_DURIAN": "◆ 【Kiểm tra trước】 Sầu riêng\n· Mùi nặng hơn màu — có thể cần nhiều lần",
    "S_VN_BANH_XEO": "◆ 【Kiểm tra trước】 Bánh xèo\n· Tinh bột → dầu → nghệ · phức hợp",
}
EXTRA_SOFT_OUTLOOK = {
    "S_FISH_SAUCE": {
        "ko": (
            "◆ 【예상 결과】\n"
            "· 방금 묻은 직후: 색·냄새가 나아질 수 있음\n"
            "· 마름·열: 냄새가 남을 수 있음 — 접수 때 동의"
        ),
        "vi": (
            "◆ 【Kết quả kỳ vọng】\n"
            "· Mới dính: màu/mùi có thể đỡ\n"
            "· Khô/nhiệt: dễ còn mùi — đồng ý khi nhận"
        ),
        "en": (
            "◆ 【Expected result】\n"
            "· Just stained: color/odor may improve\n"
            "· Dried/heat: odor may remain — get consent"
        ),
    },
    "S_VN_MANGOSTEEN": {
        "ko": "◆ 【예상 결과】\n· 부분 개선 · 완전 제거 어렵다고 고지",
        "vi": "◆ 【Kết quả kỳ vọng】\n· Cải thiện một phần · báo khó sạch hết",
        "en": "◆ 【Expected result】\n· Partial only · disclose hard residual",
    },
    "S_CURRY": {
        "ko": "◆ 【예상 결과】\n· 신선+직사광선: 노란기 개선\n· 마름·실내건조: 잔색 가능",
        "vi": "◆ 【Kết quả kỳ vọng】\n· Mới + nắng: vàng nhạt hơn\n· Khô/phơi trong nhà: dễ còn",
        "en": "◆ 【Expected result】\n· Fresh + sun: yellow fades\n· Dried/indoor: residual possible",
    },
}
EXTRA_DONTS_KO = {
    "S_FISH_SAUCE": ["락스로 느억맘을 지우지 마세요 — 냄새가 더 고착될 수 있어요", "향수로 냄새를 덮지 마세요"],
    "S_SHRIMP_PASTE": ["락스 금지", "섬유유연제·향수로 냄새 덮기 금지"],
    "S_VN_MANGOSTEEN": ["완전 제거를 보장하지 마세요", "유색에 강한 표백을 함부로 쓰지 마세요"],
}
EXTRA_DONTS_VI = {
    "S_FISH_SAUCE": ["Không dùng javel cho nước mắm — mùi dễ cố định hơn", "Không xịt nước hoa che mùi"],
    "S_SHRIMP_PASTE": ["Cấm javel", "Không che mùi bằng nước xả / nước hoa"],
    "S_VN_MANGOSTEEN": ["Không cam kết sạch 100%", "Không tẩy mạnh tùy tiện lên áo màu"],
}
EXTRA_TOOL_EXTRAS = {
    "S_FISH_SAUCE": {
        "ko": [
            "효소계 세제(프로테아제·라벨에 효소/enzyme)",
            "흰 식초(냄새 중화·줄이기용)",
            "산소계 표백제(흰옷만·과탄산)",
            "담금통(옷을 담그는 대야)",
        ],
        "vi": ["Nước giặt enzyme (protease)", "Giấm (giảm mùi)", "Oxy trắng", "Chậu ngâm"],
        "en": ["Enzyme detergent (protease)", "Vinegar (reduce odor)", "Oxygen bleach (whites)", "Soak basin"],
    },
    "S_VN_DURIAN": {
        "ko": ["주방세제", "베이킹소다", "식초"],
        "vi": ["Nước rửa chén", "Baking soda", "Giấm"],
        "en": ["Dish soap", "Baking soda", "Vinegar"],
    },
}
