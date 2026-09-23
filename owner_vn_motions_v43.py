# -*- coding: utf-8 -*-
"""VN specialty v43 hand motions (KO/VI) — fills the 8 SOPs missing scripts."""
from __future__ import annotations

_START = "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n\n"
_START_VI = "▼ Bắt đầu — làm lần lượt từ trên xuống\n\n"


def _step(n: int, title: str, body: str) -> str:
    return f"Step {n}. {title}\n─────\n{body.strip()}\n"


def _step_vi(n: int, title: str, body: str) -> str:
    return f"Bước {n}. {title}\n─────\n{body.strip()}\n"


HAND_MOTIONS_KO_V43: dict[str, str] = {
    "S_VN_CHAIN_OIL": (
        _START
        + _step(
            1,
            "체인 기름 확인 · 흡착",
            "오토바이 체인·스프레이 기름입니다(식용유와 다름).\n"
            "물부터 붓지 마세요. 전분·키친타월로 겉 기름을 흡수하세요.\n"
            "실크·울이면 L3 — 전문·거절을 먼저 검토하세요.",
        )
        + "\n"
        + _step(
            2,
            "주방세제로 기름 제거",
            "주방세제를 얼룩에 바르고 15–20분. 문지르지 말고 찍어 주세요.\n"
            "찬물·미온으로 헹구세요.",
        )
        + "\n"
        + _step(
            3,
            "철분 잔색 · 세탁 · 미끄럼 확인",
            "검붉은 잔색이 있으면 식초 또는 레몬 약하게 10–20분(테스트).\n"
            "흰옷만 산소(확인 후). 면·폴리 세탁.\n"
            "미끄러움이 남으면 말리지 마세요.",
        )
    ),
    "S_VN_GASOLINE": (
        _START
        + _step(
            1,
            "휘발유 · 환기 · 불꽃 금지",
            "야외·환기. 불꽃·건조기 금지.\n"
            "겉 기름을 키친타월로 흡수하세요.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 · 헹굼",
            "주방세제 10–15분 → 찬물 헹굼. 냄새 남으면 반복.\n"
            "실크·울·가죽 → 전문.",
        )
        + "\n"
        + _step(3, "세탁 · 냄새 확인", "세탁 후 냄새 확인. 남은 채 건조기 금지.")
    ),
    "S_VN_BRAKE_FLUID": (
        _START
        + _step(
            1,
            "브레이크액 · 즉시 찬물",
            "수용성입니다. 즉시 찬물로 헹구세요(번지기 전).",
        )
        + "\n"
        + _step(
            2,
            "중성세제 세탁",
            "중성·일반 세제로 세탁. 강한 용제 먼저 쓰지 마세요.",
        )
        + "\n"
        + _step(3, "확인", "잔색·번짐 확인. 유색은 이염 주의.")
    ),
    "S_VN_EXHAUST_SOOT": (
        _START
        + _step(
            1,
            "매연 · 마른 털기",
            "젖은 채 문지르지 마세요. 마른 솔·테이프로 검댕을 털어 내세요.",
        )
        + "\n"
        + _step(
            2,
            "주방세제",
            "주방세제 8–15분 → 헹굼.",
        )
        + "\n"
        + _step(
            3,
            "흰옷 산소 · 세탁",
            "흰옷만 산소(테스트). 세탁 후 확인.",
        )
    ),
    "S_VN_RUBBER_MARK": (
        _START
        + _step(
            1,
            "고무 자국 · 마른 제거",
            "마른 천·소프트 고무리무버(테스트)로 겉만. 문지르면 번짐.",
        )
        + "\n"
        + _step(
            2,
            "주방세제",
            "잔여 유분: 주방세제 국소 → 헹굼.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁. 검은 잔영 남으면 사전 고지.")
    ),
    "S_VN_CEMENT": (
        _START
        + _step(
            1,
            "시멘트 · 마른 뒤 긁기",
            "장갑. 젖은 채 문지르지 마세요 — 먼저 말려 긁기·솔.",
        )
        + "\n"
        + _step(
            2,
            "식초 약하게 중화",
            "식초 1:3 정도 20–40분(테스트). 알칼리 중화.\n"
            "실크·울·가죽은 전문.",
        )
        + "\n"
        + _step(3, "세제 세탁", "주방·중성 세제 후 세탁. 잔여 가루 확인.")
    ),
    "S_VN_ACID_RAIN": (
        _START
        + _step(
            1,
            "빗물 자국 · 찬물",
            "찬물로 헹구세요. 강한 알칼리·락스부터 쓰지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "중성 세탁",
            "중성세제로 세탁. 노란 잔색+흰옷만 짧은 산소(테스트).",
        )
        + "\n"
        + _step(3, "확인", "잔색 확인 후 건조.")
    ),
    "S_VN_SWEAT_SUNSCREEN": (
        _START
        + _step(
            1,
            "땀+선크림 구분",
            "목·겨드랑 노란+끈적: 선크림 오일층이 있을 수 있어요.\n"
            "락스 금지(더 누래짐).",
        )
        + "\n"
        + _step(
            2,
            "기름 먼저 → 효소",
            "주방세제로 오일층 → 헹굼 → 효소(단백질/황변).\n"
            "실크·울: 중성만.",
        )
        + "\n"
        + _step(
            3,
            "흰옷 산소 · 확인",
            "흰/면만 산소(테스트). 세탁 후 강광. 완전 복원 비보장 고지.",
        )
    ),
}

HAND_MOTIONS_VI_V43: dict[str, str] = {
    "S_VN_CHAIN_OIL": (
        _START_VI
        + _step_vi(
            1,
            "Dầu xích · thấm bột",
            "Dầu xích xe máy (khác dầu ăn). Đừng đổ nước trước — thấm bột/khăn.\n"
            "Lụa/len → L3 chuyên/từ chối.",
        )
        + "\n"
        + _step_vi(
            2,
            "Nước rửa chén",
            "Bôi nước rửa chén 15–20 phút, chấm không chà → xả.",
        )
        + "\n"
        + _step_vi(
            3,
            "Giấm nếu còn sắt · giặt",
            "Còn đỏ sẫm: giấm/chanh nhẹ 10–20' (test). Oxy chỉ trắng.\n"
            "Giặt cotton/poly. Còn nhờn → không sấy.",
        )
    ),
    "S_VN_GASOLINE": (
        _START_VI
        + _step_vi(1, "Xăng · thông gió", "Ngoài trời. Cấm lửa/sấy. Thấm khăn.")
        + "\n"
        + _step_vi(2, "Rửa chén", "Nước rửa chén 10–15' → xả. Lụa/len → chuyên.")
        + "\n"
        + _step_vi(3, "Giặt · mùi", "Giặt. Còn mùi → không sấy.")
    ),
    "S_VN_BRAKE_FLUID": (
        _START_VI
        + _step_vi(1, "Dầu thắng · xả lạnh ngay", "Hòa tan nước — xả lạnh ngay.")
        + "\n"
        + _step_vi(2, "Giặt trung tính", "Giặt S1/trung tính. Chưa dùng dung môi mạnh.")
        + "\n"
        + _step_vi(3, "Kiểm", "Kiểm vết/lem màu.")
    ),
    "S_VN_EXHAUST_SOOT": (
        _START_VI
        + _step_vi(1, "Bồ hóng · phủi khô", "Không chà ướt. Phủi khô/băng dính.")
        + "\n"
        + _step_vi(2, "Rửa chén", "Nước rửa chén 8–15' → xả.")
        + "\n"
        + _step_vi(3, "Oxy trắng · giặt", "Oxy chỉ trắng. Giặt.")
    ),
    "S_VN_RUBBER_MARK": (
        _START_VI
        + _step_vi(1, "Vết cao su", "Khăn khô / tẩy cao su nhẹ (test). Không chà loang.")
        + "\n"
        + _step_vi(2, "Rửa chén", "Còn dầu: nước rửa chén → xả.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Báo nếu còn bóng đen.")
    ),
    "S_VN_CEMENT": (
        _START_VI
        + _step_vi(1, "Xi măng · cạo khô", "Găng. Để khô rồi cạo — không chà ướt.")
        + "\n"
        + _step_vi(2, "Giấm trung hòa", "Giấm 1:3 ~20–40' (test). Lụa/da → chuyên.")
        + "\n"
        + _step_vi(3, "Giặt", "Xà phòng rồi giặt.")
    ),
    "S_VN_ACID_RAIN": (
        _START_VI
        + _step_vi(1, "Vết mưa · lạnh", "Xả lạnh. Chưa dùng Javel trước.")
        + "\n"
        + _step_vi(2, "Giặt trung tính", "S1. Oxy ngắn chỉ trắng nếu vàng.")
        + "\n"
        + _step_vi(3, "Kiểm", "Soi rồi sấy.")
    ),
    "S_VN_SWEAT_SUNSCREEN": (
        _START_VI
        + _step_vi(1, "Mồ hôi + kem chống nắng", "Cổ/nách vàng+dính: lớp dầu kem. Cấm Javel.")
        + "\n"
        + _step_vi(2, "Dầu trước → enzyme", "Rửa chén → xả → enzyme. Lụa/len: chỉ S1.")
        + "\n"
        + _step_vi(3, "Oxy trắng", "Oxy nếu trắng. Báo khó trắng lại 100%.")
    ),
}


def merge_v43_motions() -> tuple[dict[str, str], dict[str, str]]:
    return dict(HAND_MOTIONS_KO_V43), dict(HAND_MOTIONS_VI_V43)
