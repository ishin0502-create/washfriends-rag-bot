# -*- coding: utf-8 -*-
"""Extra KO L2/L3 + VI hand-motion scripts (safe: education/protocol only).

L3 scripts lead with refuse/refer — no invented solvents or ratios.
"""
from __future__ import annotations

_START = "▼ 이제 시작합니다 — 순서대로 따라 해 주세요\n\n"
_START_VI = "▼ Bắt đầu — làm lần lượt từ trên xuống\n\n"


def _step(n: int, title: str, body: str) -> str:
    return f"Step {n}. {title}\n─────\n{body.strip()}\n"


def _step_vi(n: int, title: str, body: str) -> str:
    return f"Bước {n}. {title}\n─────\n{body.strip()}\n"


# ── Remaining L2 (have protocol; supervisor tone) ──
HAND_MOTIONS_KO_L2_REST: dict[str, str] = {
    "S_CURRY": (
        _START
        + _step(
            1,
            "고형 제거 · 기름 먼저",
            "고형물을 살살 걷어 주세요.\n"
            "주방세제를 약하게 찍어 바르고 5~10분. 기름이 색을 붙잡습니다.",
        )
        + "\n"
        + _step(
            2,
            "베이킹소다 → (흰옷) 산소·짧은 햇빛",
            "베이킹소다 페이스트 15~30분.\n"
            "흰옷만 산소(테스트) 또는 짧은 햇빛. 실크·울·유색은 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 노란 잔색 남은 채 말리지 마세요.")
    ),
    "S_MUSTARD": (
        _START
        + _step(
            1,
            "고형 제거 · 찬물",
            "고형을 걷고 찬물로 흡수하세요. 세게 문지르지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → (흰옷) 산소",
            "주방세제 5~10분 → 헹굼.\n"
            "흰옷만 산소(테스트). 유색·실크·울은 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 노란기 남은 채 말리지 마세요.")
    ),
    "S_SHIRT_YELLOW": (
        _START
        + _step(
            1,
            "락스 금지 · 황변 설명",
            "단백질 황변에 락스는 더 누렇게 만들 수 있어요.\n"
            "완전 제거가 어렵다고 손님께 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "효소 → (흰옷) 산소",
            "효소를 황변 부위에 바르고 20~40분(또는 밤새 페이스트).\n"
            "흰옷만 산소 미온 침지(병 안내·구석 테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 누런기 남은 채 말리지 마세요.")
    ),
    "S_URINE": (
        _START
        + _step(
            1,
            "장갑 · 찬물 · 혼합 금지",
            "장갑 필수. 찬물만. 온수·건조기 금지(단백질 고착).\n"
            "암모니아·염소 세제를 섞지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "효소 → 식초",
            "효소 15~30분 → 식초 Cap1+물 Cap4.\n"
            "실크·울은 효소 금지 → 중성·찬물만.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "충분히 헹군 뒤 세탁. 냄새 남은 채 말리지 마세요.")
    ),
    "S_VOMIT": (
        _START
        + _step(
            1,
            "PPE · 환기 · 고형 제거",
            "장갑·환기. 고형을 살살 걷어 주세요.\n"
            "온수 금지. 암모니아·염소 혼합 금지.",
        )
        + "\n"
        + _step(
            2,
            "찬물 · 효소 → 식초",
            "찬물 헹굼 → 효소 15~30분 → 식초 Cap1+물 Cap4.\n"
            "실크·울은 효소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 냄새·잔색 확인. 남은 채 말리지 마세요.")
    ),
    "S_DEODORANT": (
        _START
        + _step(
            1,
            "흰 잔여 vs 황변 구분",
            "흰 가루·왁스 잔여 → 식초.\n"
            "겨드랑이 누런기 → 효소→(흰옷)산소. 락스 금지.",
        )
        + "\n"
        + _step(
            2,
            "식초 또는 효소",
            "흰 잔여: 식초 Cap1+물 Cap4, 5~15분.\n"
            "황변: 효소 15~30분 → 흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 잔여·누런기 남은 채 말리지 마세요.")
    ),
    "S_PERFUME": (
        _START
        + _step(
            1,
            "찬물 · 나중에 누렇게 될 수 있음",
            "찬물로 헹구세요.\n"
            "흰옷은 나중에 황변될 수 있다고 손님께 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "식초 → (흰옷) 짧은 산소",
            "식초 Cap1+물 Cap4, 5~15분.\n"
            "흰옷만 짧은 산소(테스트). 유색·실크·울은 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 통풍", "세탁 후 통풍 건조. 잔향·누런기 남은 채 건조기 금지.")
    ),
    "S_SUNSCREEN": (
        _START
        + _step(
            1,
            "전분 흡착 · 락스 금지",
            "전분·밀가루를 덮어 10~30분 뒤 털어 주세요.\n"
            "락스 절대 금지(영구 황변). 미끄럼 남은 채 건조 금지.",
        )
        + "\n"
        + _step(
            2,
            "주방세제",
            "주방세제를 약하게 찍어 바르고 1~2분.\n"
            "실크·울은 중성만·약하게.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 미끄럼 없어진 뒤만 건조하세요.")
    ),
    "S_MASCARA": (
        _START
        + _step(
            1,
            "먼저 찍어 흡수 · 문지름 금지",
            "흰 천으로 위에서 꾹꾹. 옆으로 문지르면 번집니다.\n"
            "※ 실크·울은 매니저 확인 후.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 알코올(70% IPA)",
            "주방세제 1~2방울을 흰 천에 묻혀 약하게 찍고 찬물로 헹구세요.\n"
            "잔색이면:\n"
            "⚠️ 환기. 이소프로필 알코올 70%(약국).\n"
            "뒤집기 → 받침 천 → 찍어 빼기(꾹 3초) → 천 교체 5~8번\n"
            "⑧ 찬물(15~20°C) 한 번 헹굼.\n"
            "흰옷만 산소(테스트). 유색·실크·울 산소 금지.\n"
            "🛑 색 빠짐 → 중단.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 밝게 확인. 검은 잔색 남은 채 말리지 마세요.")
    ),
    "S_IODINE": (
        _START
        + _step(
            1,
            "매니저 확인 · 구석 테스트",
            "요오드(포비돈 등)는 색소가 셉니다. 매니저 확인 후 진행.\n"
            "※ 실크·울 → 전문·거절을 먼저 검토하세요.",
        )
        + "\n"
        + _step(
            2,
            "알코올(70% IPA)로 찍어 빼기",
            "⚠️ 환기. 이소프로필 알코올 70%(약국).\n"
            "구석 테스트 30초 → OK면 뒤집기·받침 천·꾹 3초·천 교체 5~10번\n"
            "⑧ 찬물(15~20°C) 헹굼.\n"
            "흰옷만 산소(테스트). 실크·울은 약하게·짧게 또는 중단.\n"
            "🛑 색 빠짐 → 즉시 중단.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 갈색 남은 채 말리지 마세요.")
    ),
    "S_STARCH_TRANSFER": (
        _START
        + _step(
            1,
            "전분 이염 확인",
            "풀·전분 이염이면 일반 세제만으로는 부족할 수 있어요.\n"
            "효소(아밀라아제 계열) 우선. 매니저 확인.",
        )
        + "\n"
        + _step(
            2,
            "효소 담그기",
            "효소 20~40분. 세게 문지르지 마세요.\n"
            "실크·울은 매니저 확인 후 중성만.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 하얀 가루·자국 남은 채 말리지 마세요.")
    ),
    "S_MILDEW": (
        _START
        + _step(
            1,
            "실외 · PPE · 가죽·실크면 전문",
            "실외·장갑·마스크. 마른 포자를 털 때 흡입하지 마세요.\n"
            "가죽·실크·울·심한 침투 → 전문 의뢰 우선.",
        )
        + "\n"
        + _step(
            2,
            "식초 → 산소 · 락스 혼합 금지",
            "식초 Cap1+물 Cap4 담그기 → 흰옷 산소(테스트).\n"
            "흰 면만 희석 락스 검토 시: 식초·암모니아와 절대 혼합 금지(가스).",
        )
        + "\n"
        + _step(3, "세탁 · 통풍", "세탁 후 통풍·햇빛. 곰팡이·냄새 남은 채 건조기 금지.")
    ),
    "S_GUM": (
        _START
        + _step(
            1,
            "냉동해서 깨기",
            "비닐에 넣어 30~60분 냉동. 바삭할 때 Cap2로 깨서 제거하세요.",
        )
        + "\n"
        + _step(
            2,
            "잔여만 아세톤 극소(매니저)",
            "매니저 확인. 아세테이트·실크·울·프린트는 아세톤 금지.\n"
            "허용 원단만: 구석 테스트 후 극소량·장갑·환기.",
        )
        + "\n"
        + _step(3, "주방세제 · 세탁", "주방세제 후 세탁. 끈적 남은 채 말리지 마세요.")
    ),
    "S_CANDLE_WAX": (
        _START
        + _step(
            1,
            "굳힌 뒤 긁기",
            "차갑게 굳힌 뒤 Cap2로 겉 왁스만 살살 긁어 주세요. 깊게 긁지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "흡수지 · 저온 다리미(매니저)",
            "매니저 확인. 흡수지 위·아래 + 저온 다림질로 왁스 옮기기.\n"
            "실크·울·합성은 열 주의 — 의심되면 중단.",
        )
        + "\n"
        + _step(3, "잔색 · 세탁", "남는 색은 주방세제·(흰옷)산소. 세탁 후 확인.")
    ),
    "S_GREASE": (
        _START
        + _step(
            1,
            "전분 흡착 · 미끄럼 확인",
            "전분·밀가루를 덮어 흡수 후 털어 주세요.\n"
            "미끄럼·냄새 남은 채 건조기 금지.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 · 효소",
            "주방세제 1~2분 → 효소 15~30분(실크·울 제외).\n"
            "강한 용제는 매니저 확인 후에만.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 기름 자국 남은 채 말리지 마세요.")
    ),
    "S_CHILI": (
        _START
        + _step(
            1,
            "고춧가루 제거 · 번짐 주의",
            "고춧가루를 살살 털어 주세요. 문지르면 색소가 번집니다.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 식초",
            "주방세제 30초 → 식초 Cap1+물 Cap4.\n"
            "유색은 산소 금지. 흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 빨간·냄새 남은 채 말리지 마세요.")
    ),
    "S_BETEL": (
        _START
        + _step(
            1,
            "매니저 확인 · 고착 위험",
            "빈랑(베트남) 얼룩은 탄닌+색소로 고착이 쉽습니다.\n"
            "매니저 확인 후 진행. 잔색 가능성을 손님께 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "찬물 · 효소 → 식초",
            "찬물 → 효소(실크·울 제외) → 식초 Cap1+물 Cap4.\n"
            "흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 갈색·빨간 남은 채 말리지 마세요.")
    ),
    "S_SHRIMP_PASTE": (
        _START
        + _step(
            1,
            "냄새·유분 고지",
            "맘톰(새우젓 페이스트)은 유분+단백질+색소입니다.\n"
            "냄새 잔존 가능 — 손님께 먼저 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 효소 → 식초",
            "주방세제 → 효소 → 식초 Cap1+물 Cap4.\n"
            "실크·울은 효소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 냄새·색 확인. 남은 채 말리지 마세요.")
    ),
    "S_GAC": (
        _START
        + _step(
            1,
            "오일+색소 순서",
            "가정과(각) = 오일+색소. 주방세제(오일) 먼저 → 색소는 나중.\n"
            "매니저 확인. 구석 테스트.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 알코올·산소(흰옷)",
            "주방세제 → 헹굼.\n"
            "잔색: 테스트 후 알코올. 흰옷만 산소.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 주황·빨간 남은 채 말리지 마세요.")
    ),
    "S_ANNATTO": (
        _START
        + _step(
            1,
            "매니저 · 구석 테스트",
            "아나토(주황 색소)는 고착이 쉽습니다. 매니저 확인.\n"
            "알코올·산소 전 구석 테스트.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 알코올 → (흰옷) 산소",
            "주방세제 → 테스트 후 알코올 찍어 빼기.\n"
            "흰옷만 산소. 유색·실크·울은 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 주황 남은 채 말리지 마세요.")
    ),
}

# ── L3: refuse / refer first (no invented deep chemistry) ──
HAND_MOTIONS_KO_L3: dict[str, str] = {
    "S_ENGINE_OIL": (
        _START
        + _step(
            1,
            "등급·전문 의뢰 먼저",
            "엔진오일은 최난입니다. 실크·울 흡수 → 즉시 전문 의뢰.\n"
            "일반 원단도 부분 제거·잔색을 손님께 먼저 말씀하고 매니저 확인.",
        )
        + "\n"
        + _step(
            2,
            "(매니저 OK) 전분 · 환기",
            "PPE·환기. 고형 제거 → 전분 덮어 흡수 반복.\n"
            "용제는 매니저·환기·화기 금지 조건에서만. 미끄럼 남은 채 건조 금지.",
        )
        + "\n"
        + _step(3, "중단 기준", "더 이상 안 빠지거나 원단이 위험하면 중단 → 전문 의뢰·정중 거절.")
    ),
    "S_MOTORBIKE_OIL": (
        _START
        + _step(
            1,
            "매니저 · 열고착 고지",
            "오토바이 오일(특히 마름)은 열고착·용제 위험이 큽니다.\n"
            "매니저 확인. 잔색·부분 제거를 손님께 말씀하세요.",
        )
        + "\n"
        + _step(
            2,
            "(매니저 OK) 전분 → 주방세제",
            "전분 흡착 → 주방세제. 강한 용제·고온은 실크·울 금지.\n"
            "미끄럼 남은 채 건조 금지.",
        )
        + "\n"
        + _step(3, "중단 기준", "위험·안 빠지면 중단 → 전문 의뢰.")
    ),
    "S_TAR": (
        _START
        + _step(
            1,
            "거절·전문 우선",
            "타르·아스팔트는 성공률이 매우 낮습니다.\n"
            "접수 시 등급 3·전문 의뢰를 먼저 검토하세요.",
        )
        + "\n"
        + _step(
            2,
            "(매니저가 시도 허용 시) 얼려 긁기",
            "차갑게·얼려 Cap2로 겉만. 전분. 용제는 매니저·환기만.\n"
            "인내가 필요하고 완전 제거는 기대하지 마세요.",
        )
        + "\n"
        + _step(3, "중단", "안 되면 즉시 중단·전문 의뢰.")
    ),
    "S_LATERITE": (
        _START
        + _step(
            1,
            "적토 · 락스 금지 · 실크·울 전문",
            "라테라이트(적토)=철. 락스 절대 금지(철 영구 고착).\n"
            "실크·울: 옥살산 금지 → 전문 또는 식초만 약하게. 매니저 필수.",
        )
        + "\n"
        + _step(
            2,
            "(면·린넨·폴리만·매니저) 건조→털기→옥살산",
            "완전 건조 후 털기. 젖은 채 문지르기 금지.\n"
            "옥살산은 매니저·장갑·구석 테스트·15분부터(최대 30분)→즉시 헹굼→베이킹소다 중화.",
        )
        + "\n"
        + _step(3, "이미 세탁·건조면", "복원 불가에 가깝습니다 — 손님께 고지·전문 검토.")
    ),
    "S_RUST": (
        _START
        + _step(
            1,
            "매니저 · 실크·울 금지",
            "녹(철) 처리제는 위험합니다. 실크·울·가죽 → 전문 의뢰.\n"
            "매니저 확인 없이 진행하지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "(허용 원단만) 옥살산·PPE",
            "장갑·구석 테스트. 교육 SOP의 시간만. 즉시 헹굼·중화.\n"
            "락스로 녹을 지우지 마세요.",
        )
        + "\n"
        + _step(3, "중단", "의심되면 중단 → 전문 의뢰.")
    ),
    "S_PAINT_LATEX": (
        _START
        + _step(
            1,
            "마름 페인트 · 성공률 낮음",
            "수성 페인트가 마르면 제거가 어렵습니다. 부분 제거·거절을 손님께 말씀하세요.\n"
            "매니저 확인.",
        )
        + "\n"
        + _step(
            2,
            "(매니저 OK) 긁기 · 세제",
            "겉만 Cap2로 살살. 주방세제. 강한 용제는 매니저만.\n"
            "실크·아세테이트 주의.",
        )
        + "\n"
        + _step(3, "중단", "안 되면 전문 의뢰.")
    ),
    "S_PAINT_OIL": (
        _START
        + _step(
            1,
            "유성페인트 · 시너 위험",
            "아세테이트·실크·울: 시너 금지 → 즉시 전문 의뢰.\n"
            "그 외도 등급 2 부분 제거 우선. 매니저 필수.",
        )
        + "\n"
        + _step(
            2,
            "매니저 지시에만",
            "교육 SOP·매니저 지시 밖의 용제를 쓰지 마세요.\n"
            "환기·화기 금지.",
        )
        + "\n"
        + _step(3, "중단", "위험하면 중단·전문 의뢰.")
    ),
    "S_INK_PERMANENT": (
        _START
        + _step(
            1,
            "유성매직 · 전문·거절 우선",
            "유성매직·영구 마커는 성공률이 낮습니다.\n"
            "실크·울·아세테이트·프린트 → 접수 시 등급 3·전문 우선.",
        )
        + "\n"
        + _step(
            2,
            "(매니저 허용·일반 원단만)",
            "볼펜 SOP와 달리 용제 위험이 큽니다. 매니저 없이 진행 금지.\n"
            "이미 다림질·건조기면 복원 불가 검토.",
        )
        + "\n"
        + _step(3, "중단", "안 되면 정중히 거절·전문 의뢰.")
    ),
    "S_GLUE": (
        _START
        + _step(
            1,
            "502 등 굳은 접착제 · 거절 우선",
            "시아노아크릴레이트(502)가 굳으면 원단 손상 없이 제거가 거의 불가합니다.\n"
            "접수 시 등급 3·전문·반려를 먼저 검토하세요.",
        )
        + "\n"
        + _step(
            2,
            "임의 용제 금지",
            "매니저·전문 지시 없이 아세톤 등을 바르지 마세요.\n"
            "아세테이트·실크는 특히 위험합니다.",
        )
        + "\n"
        + _step(3, "안내", "손님께 복원 불가 가능성을 솔직히 말씀하세요.")
    ),
    "S_NAIL_POLISH": (
        _START
        + _step(
            1,
            "아세톤 · 아세테이트 녹음",
            "매니큐어는 아세톤이 필요할 수 있으나 아세테이트·일부 합성은 녹습니다.\n"
            "매니저 확인. 아세테이트·실크 → 전문 우선.",
        )
        + "\n"
        + _step(
            2,
            "(허용 시만) 테스트 후 극소",
            "구석 테스트 통과 시에만. 흰 천에 묻혀 찍기. 직접 붓지 마세요.",
        )
        + "\n"
        + _step(3, "중단", "색 빠짐·원단 변화 시 즉시 중단.")
    ),
    "S_SHOE_POLISH": (
        _START
        + _step(
            1,
            "구두약 · 용제·다층",
            "왁스+색소+용제층입니다. 성공률 낮음 — 손님께 고지.\n"
            "매니저 확인. 실크·울·스웨이드 → 전문.",
        )
        + "\n"
        + _step(
            2,
            "매니저 지시에만",
            "겉만 살살. 강한 용제는 매니저·환기만.\n"
            "교육에 없는 약품을 쓰지 마세요.",
        )
        + "\n"
        + _step(3, "중단", "안 되면 전문 의뢰.")
    ),
    "S_FECES": (
        _START
        + _step(
            1,
            "위생 · PPE · 분리",
            "장갑 필수. 도구·통을 청결물과 분리.\n"
            "온수·건조기 금지. 감염·냄새 — 손님·직원 안전 우선.",
        )
        + "\n"
        + _step(
            2,
            "찬물 · 효소(매니저)",
            "고형 제거 → 찬물 → 효소(실크·울 제외).\n"
            "심하거나 불안하면 전문·반려 검토.",
        )
        + "\n"
        + _step(3, "세탁 · 소독 정책", "매장 위생 규칙을 따르세요. 잔여·냄새 채 말리지 마세요.")
    ),
}

# ── VI expand: remaining L1 + L2 priority gaps + safe L3 refuse ──
HAND_MOTIONS_VI_EXTRA: dict[str, str] = {
    "S_MILK": (
        _START_VI
        + _step_vi(
            1,
            "Chỉ nước lạnh",
            "Đeo găng nếu cần.\n"
            "Chỉ lạnh. Cấm nóng trước — đạm sẽ đông.",
        )
        + "\n"
        + _step_vi(
            2,
            "Ngâm enzyme",
            "Enzyme 15–30 phút. Lụa/len: cấm enzyme → trung tính lạnh.",
        )
        + "\n"
        + _step_vi(3, "Giặt · kiểm", "Xả kỹ rồi giặt. Còn vết → không sấy.")
    ),
    "S_EGG": (
        _START_VI
        + _step_vi(
            1,
            "Cạo nhẹ · lạnh",
            "Gạt xác trứng. Không dùng nóng trước.",
        )
        + "\n"
        + _step_vi(
            2,
            "Enzyme",
            "Ngâm enzyme 15–30 phút (trừ lụa/len).",
        )
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn đạm → không sấy.")
    ),
    "S_TEA": (
        _START_VI
        + _step_vi(
            1,
            "Lộn trái · thấm lạnh",
            "Lộn trái, thấm lạnh từ trong. Không chà ngang.\n"
            "💡 Trà sữa: ưu tiên enzyme trước.",
        )
        + "\n"
        + _step_vi(
            2,
            "Giấm 1:4",
            "Xịt giấm 1:4, chờ 5–15 phút, xả lạnh.",
        )
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Áo trắng còn vết: oxy sau thử góc.")
    ),
    "S_FRUIT_JUICE": (
        _START_VI
        + _step_vi(1, "Thấm lạnh ngay", "Thấm khăn trắng. Không chà.")
        + "\n"
        + _step_vi(
            2,
            "Giấm · (trắng) oxy",
            "Giấm Cap1+nước Cap4.\n"
            "Áo màu/lụa/len: cấm oxy. Trắng: oxy sau thử.",
        )
        + "\n"
        + _step_vi(3, "Giặt · kiểm", "Giặt. Còn màu → không sấy.")
    ),
    "S_SOFT_DRINK": (
        _START_VI
        + _step_vi(1, "Xả lạnh", "Xả lạnh hết đường dính.")
        + "\n"
        + _step_vi(2, "Giấm nhẹ", "Giấm 1:4 ngắn nếu còn màu.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn ngọt/dính → không sấy (vàng sau).")
    ),
    "S_KETCHUP": (
        _START_VI
        + _step_vi(1, "Gạt · lạnh", "Gạt đặc. Xả lạnh. Không chà mạnh.")
        + "\n"
        + _step_vi(
            2,
            "Nước rửa chén → giấm",
            "Nước rửa chén → giấm 1:4.\n"
            "Trắng: oxy sau thử. Màu: cấm oxy.",
        )
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn đỏ → không sấy.")
    ),
    "S_TOMATO_SAUCE": (
        _START_VI
        + _step_vi(1, "Gạt · không chà", "Gạt sốt. Không chà loang đỏ.")
        + "\n"
        + _step_vi(2, "Nước rửa chén → giấm", "Giống ketchup: D2 → giấm. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn đỏ → không sấy.")
    ),
    "S_CHOCOLATE": (
        _START_VI
        + _step_vi(1, "Gạt · mỡ trước", "Gạt đặc. Nước rửa chén lấy mỡ trước.")
        + "\n"
        + _step_vi(2, "Enzyme → (trắng) oxy", "Enzyme rồi oxy chỉ trắng nếu cần.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nâu → không sấy.")
    ),
    "S_SWEAT_FRESH": (
        _START_VI
        + _step_vi(1, "Cấm javel", "Mồ hôi tươi: cấm javel (dễ vàng hơn).")
        + "\n"
        + _step_vi(2, "Enzyme", "Enzyme 15–30 phút (trừ lụa/len).")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn mùi → không sấy.")
    ),
    "S_SOY_SAUCE": (
        _START_VI
        + _step_vi(1, "Xả lạnh ngay", "Xả lạnh. Cấm nóng sớm (màu đen cố định).")
        + "\n"
        + _step_vi(2, "Enzyme → giấm", "Enzyme → giấm 1:4. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nâu → không sấy.")
    ),
    "S_INK_PEN": (
        _START_VI
        + _step_vi(
            1,
            "Gạt nhẹ · thử góc",
            "Khăn khô lấy mực bề mặt — không chà.\n"
            "※ Lụa/len/in: hỏi quản lý · ưu tiên chuyên/từ chối.",
        )
        + "\n"
        + _step_vi(
            2,
            "Chấm cồn IPA 70%",
            "⚠️ Thông gió. Cồn isopropyl 70% (cồn sát trùng). Cấm methanol.\n"
            "① Lộn trái ② Lót khăn ③ Thấm cồn khăn khác ④ Ấn 3 giây thẳng đứng\n"
            "⑤–⑦ Đổi khăn 5–10 lần ⑧ Xả lạnh 15–20°C một lần.\n"
            "🛑 Phai màu → dừng.",
        )
        + "\n"
        + _step_vi(
            3,
            "Nước rửa chén · giặt",
            "1–2 giọt nước rửa chén nhẹ, xả lạnh.\n"
            "Áo trắng còn mực: thử góc rồi oxy (cấm màu/lụa/len).\n"
            "Không Javel. Giặt; còn mực → không sấy.",
        )
    ),
    "S_MUD": (
        _START_VI
        + _step_vi(1, "Để khô rồi phủi", "Để khô hẳn. Phủi đất. Không chà khi ướt.")
        + "\n"
        + _step_vi(2, "Xả lạnh · giặt", "Xả lạnh rồi giặt. Đất đỏ laterite → SOP laterite.")
        + "\n"
        + _step_vi(3, "Kiểm", "Còn bẩn → không sấy.")
    ),
    "S_GRASS": (
        _START_VI
        + _step_vi(
            1,
            "Phủi · thử góc IPA 70%",
            "Phủi đất. Thử góc cồn isopropyl 70% 30 giây. Phai → dừng cồn.",
        )
        + "\n"
        + _step_vi(
            2,
            "Chấm cồn lấy xanh",
            "⚠️ Thông gió. Lộn trái, ấn 3 giây, đổi khăn 5–10 lần, ⑧ xả lạnh 15–20°C.",
        )
        + "\n"
        + _step_vi(3, "Enzyme · giặt", "Enzyme 15–30 phút rồi giặt. Còn xanh → không sấy.")
    ),
    "S_WHITE_WINE_BEER": (
        _START_VI
        + _step_vi(
            1,
            "Thấm ngay · báo vàng muộn",
            "Thấm khăn. Đường có thể làm vàng sau — báo khách.",
        )
        + "\n"
        + _step_vi(2, "Lạnh · (trắng) oxy", "Xử lý lạnh. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn vàng → không sấy.")
    ),
    "S_BUBBLE_TEA": (
        _START_VI
        + _step_vi(
            1,
            "Thứ tự lớp",
            "① Mỡ/trân châu → ② đạm → ③ tannin trà. Chỉ lạnh.",
        )
        + "\n"
        + _step_vi(2, "Nước rửa chén → enzyme → giấm", "Lần lượt. Lụa/len: cấm enzyme.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nâu → không sấy.")
    ),
    "S_FOUNDATION": (
        _START_VI
        + _step_vi(
            1,
            "Thấm nhẹ · silicone/dầu trước",
            "Thấm khăn. 1–2 giọt nước rửa chén, chờ ~1 phút, xả lạnh.",
        )
        + "\n"
        + _step_vi(
            2,
            "Cồn IPA 70% nếu còn màu",
            "⚠️ Thông gió. Thử góc → ấn 3 giây, đổi khăn, ⑧ xả lạnh. Lụa/len: nhẹ.",
        )
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn → không sấy.")
    ),
    "S_BBQ_SAUCE": (
        _START_VI
        + _step_vi(1, "3 lớp", "① Enzyme → ② nước rửa chén → ③ giấm.")
        + "\n"
        + _step_vi(2, "Làm lần lượt", "Enzyme 15–30 → D2 → giấm 1:4. Lụa/len: cấm enzyme.")
        + "\n"
        + _step_vi(3, "Giặt", "Oxy chỉ trắng. Còn đỏ/nâu → không sấy.")
    ),
    "S_MAYO": (
        _START_VI
        + _step_vi(1, "Mỡ trước · đạm sau", "① Nước rửa chén → ② enzyme. Cấm nóng trước.")
        + "\n"
        + _step_vi(2, "Thực hiện", "D2 1 phút → enzyme 15–30 (trừ lụa/len).")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nhờn → không sấy.")
    ),
    "S_BUTTER": (
        _START_VI
        + _step_vi(1, "Gạt · cấm sấy khi nhờn", "Gạt bơ. Còn nhờn/mùi → không sấy.")
        + "\n"
        + _step_vi(2, "Nước rửa chén · enzyme", "D2 1–2 phút → enzyme (trừ lụa/len).")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn dầu → không sấy.")
    ),
    "S_FISH_SAUCE": (
        _START_VI
        + _step_vi(1, "Báo mùi · lạnh", "Báo khách có thể còn mùi. Chỉ lạnh.")
        + "\n"
        + _step_vi(2, "Enzyme → giấm", "Enzyme → giấm 1:4. Lụa/len: trung tính + giấm nhẹ.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn mùi/màu → không sấy.")
    ),
    "S_BABY_FORMULA": (
        _START_VI
        + _step_vi(1, "Cấm javel · lạnh", "Cấm javel (sắt/đạm). Chỉ lạnh.")
        + "\n"
        + _step_vi(2, "Enzyme", "Enzyme 20–40 phút (trừ lụa/len).")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn vàng → không sấy.")
    ),
    "S_COLLAR_STAIN": (
        _START_VI
        + _step_vi(1, "Cấm javel · enzyme cổ áo", "Cổ áo = đạm+bã nhờn. Cấm javel.")
        + "\n"
        + _step_vi(2, "Enzyme", "Enzyme 20–40 phút. Không chà mạnh.")
        + "\n"
        + _step_vi(3, "Giặt", "Oxy chỉ trắng. Kiểm mặt trong cổ.")
    ),
    "S_SWEAT_YELLOW": (
        _START_VI
        + _step_vi(1, "Cấm javel · báo khách", "Vàng mồ hôi: javel làm tệ hơn. Báo khó sạch hết.")
        + "\n"
        + _step_vi(2, "Enzyme → (trắng) oxy", "Enzyme → oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn vàng → không sấy.")
    ),
    "S_CURRY": (
        _START_VI
        + _step_vi(1, "Mỡ trước", "Gạt. Nước rửa chén 5–10 phút trước.")
        + "\n"
        + _step_vi(2, "Baking soda · oxy trắng", "Bột baking 15–30 phút. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn vàng nghệ → không sấy.")
    ),
    "S_SHIRT_YELLOW": (
        _START_VI
        + _step_vi(1, "Cấm javel", "Vàng áo trắng: cấm javel. Báo khách.")
        + "\n"
        + _step_vi(2, "Enzyme → oxy", "Enzyme rồi oxy (thử góc).")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn vàng → không sấy.")
    ),
    "S_MILDEW": (
        _START_VI
        + _step_vi(
            1,
            "Ngoài trời · PPE · chuyên nếu da/lụa",
            "Ngoài trời, găng, khẩu trang. Da/lụa/len/nặng → ưu tiên chuyên.",
        )
        + "\n"
        + _step_vi(
            2,
            "Giấm → oxy · không trộn javel",
            "Giấm 1:4 → oxy trắng. Không trộn giấm với javel (khí độc).",
        )
        + "\n"
        + _step_vi(3, "Giặt · thoáng", "Giặt, phơi thoáng. Còn mốc → không sấy.")
    ),
    # L3 VI — refuse first
    "S_ENGINE_OIL": (
        _START_VI
        + _step_vi(
            1,
            "Ưu tiên từ chối / chuyên",
            "Dầu động cơ rất khó. Lụa/len thấm → gửi chuyên ngay.\n"
            "Báo khách: chỉ sạch một phần. Hỏi quản lý.",
        )
        + "\n"
        + _step_vi(
            2,
            "(Nếu quản lý cho thử) bột · thông gió",
            "PPE + thông gió. Phủ bột hút → lặp. Dung môi chỉ theo quản lý.\n"
            "Còn nhờn → không sấy.",
        )
        + "\n"
        + _step_vi(3, "Dừng", "Không tiến → dừng, gửi chuyên.")
    ),
    "S_LATERITE": (
        _START_VI
        + _step_vi(
            1,
            "Cấm javel · lụa/len chuyên",
            "Đất đỏ laterite = sắt. Cấm javel. Lụa/len: cấm oxalic → chuyên.\n"
            "Bắt buộc hỏi quản lý.",
        )
        + "\n"
        + _step_vi(
            2,
            "(Cotton/poly · quản lý) khô → oxalic",
            "Để khô, phủi. Không chà khi ướt.\n"
            "Oxalic chỉ theo SOP + găng + thử góc + trung hòa baking.",
        )
        + "\n"
        + _step_vi(3, "Đã giặt/sấy", "Gần như không phục hồi — báo khách.")
    ),
    "S_INK_PERMANENT": (
        _START_VI
        + _step_vi(
            1,
            "Bút dạ dầu · từ chối ưu tiên",
            "Tỷ lệ thành công thấp. Lụa/acetate/in → cấp 3 / chuyên trước.",
        )
        + "\n"
        + _step_vi(2, "Không tự ý dung môi", "Không làm nếu chưa có quản lý.")
        + "\n"
        + _step_vi(3, "Dừng", "Từ chối lịch sự hoặc gửi chuyên.")
    ),
    "S_GLUE": (
        _START_VI
        + _step_vi(
            1,
            "Keo 502 khô · từ chối",
            "Keo khô hầu như không gỡ không hỏng vải. Ưu tiên cấp 3 / trả lại.",
        )
        + "\n"
        + _step_vi(2, "Cấm dung môi tự ý", "Không đổ acetone nếu chưa được chỉ định.")
        + "\n"
        + _step_vi(3, "Báo khách", "Nói thẳng khả năng không phục hồi.")
    ),
    "S_TAR": (
        _START_VI
        + _step_vi(1, "Nhựa đường · chuyên trước", "Rất khó sạch. Ưu tiên chuyên / cấp 3.")
        + "\n"
        + _step_vi(2, "Chỉ khi quản lý cho", "Đông/cạo nhẹ. Không kỳ vọng sạch hết.")
        + "\n"
        + _step_vi(3, "Dừng", "Không được → gửi chuyên.")
    ),
    "S_NAIL_POLISH": (
        _START_VI
        + _step_vi(
            1,
            "Sơn móng · acetate tan",
            "Acetone có thể làm tan acetate. Hỏi quản lý. Acetate/lụa → chuyên.",
        )
        + "\n"
        + _step_vi(2, "Thử góc cực ít", "Chỉ khi được phép. Thấm khăn, không đổ trực tiếp.")
        + "\n"
        + _step_vi(3, "Dừng ngay nếu đổi màu vải", "Dừng → chuyên.")
    ),
}

# ── Tail: last protocol stains + remaining VI gaps ──
HAND_MOTIONS_KO_TAIL: dict[str, str] = {
    "S_SUGARCANE": (
        _START
        + _step(
            1,
            "찬물 흡수 · 문지름 금지",
            "사탕수수즙(느억미아)=당+색소. 안쪽에서 찬물로 흡수하세요.\n"
            "세게 문지르지 마세요. 열고착·건조기 금지.",
        )
        + "\n"
        + _step(
            2,
            "식초 → (흰옷) 산소",
            "식초 Cap1+물 Cap4, 10~20분.\n"
            "흰·면만 산소(테스트). 유색·실크·울은 산소 금지.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 당·색 남은 채 말리지 마세요(나중에 누렇게).")
    ),
    "S_DOENJANG": (
        _START
        + _step(
            1,
            "고형 긁기 · 찬물",
            "된장을 Cap1로 살살 긁어 주세요.\n"
            "찬물로 헹구세요.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 효소",
            "주방세제 → 효소 15~40분.\n"
            "실크·울은 효소 금지. 흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 갈색·냄새 남은 채 말리지 마세요.")
    ),
    "S_GOCHUJANG": (
        _START
        + _step(
            1,
            "페이스트 긁기 · 번짐 주의",
            "고추장을 살살 긁어 주세요. 문지르면 색소가 번집니다.",
        )
        + "\n"
        + _step(
            2,
            "주방세제 → 식초",
            "주방세제 → 식초 Cap1+물 Cap4, 5~15분.\n"
            "유색은 산소 금지. 흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 빨간·냄새 남은 채 말리지 마세요.")
    ),
    "S_PERSIMMON": (
        _START
        + _step(
            1,
            "즉시 찬물 · 문지름 금지",
            "감물(감 얼룩)은 빨리 처리할수록 좋아요.\n"
            "찬물로만 흡수. 세게 문지르지 마세요.",
        )
        + "\n"
        + _step(
            2,
            "식초 반복 → (흰옷) 산소",
            "식초 Cap1+물 Cap4, 10~20분 반복.\n"
            "흰·면만 산소(테스트). 늦으면 한계를 손님께 말씀하세요.",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 갈색 남은 채 말리지 마세요.")
    ),
    "S_CRAYON": (
        _START
        + _step(
            1,
            "차게 해 깨기",
            "얼리거나 차게 한 뒤 Cap2로 깨서 제거하세요.",
        )
        + "\n"
        + _step(
            2,
            "흡수지 · 저온(매니저)",
            "매니저 확인. 흡수지+저온으로 왁스 옮기기.\n"
            "실크·합성 열 주의. 잔여는 주방세제. 흰옷만 산소(테스트).",
        )
        + "\n"
        + _step(3, "세탁 · 확인", "세탁 후 확인. 색·왁스 남은 채 말리지 마세요.")
    ),
    "S_SOFTENER_SPOT": (
        _START
        + _step(
            1,
            "유연제 오일 링 확인",
            "유연제 직접 묻은 오일 링입니다. 미끄럼 남은 채 건조 금지.",
        )
        + "\n"
        + _step(
            2,
            "주방세제로 탈지",
            "주방세제 Cap2, 5~15분. 필요 시 식초 Cap1+물 Cap4.\n"
            "미온으로 다시 세탁.",
        )
        + "\n"
        + _step(3, "확인 후 건조", "미끄럼이 없어진 뒤에만 건조하세요.")
    ),
}

HAND_MOTIONS_VI_TAIL: dict[str, str] = {
    "S_SUGARCANE": (
        _START_VI
        + _step_vi(1, "Thấm lạnh · không chà", "Nước mía = đường+màu. Thấm lạnh từ trong. Cấm chà / sấy sớm.")
        + "\n"
        + _step_vi(2, "Giấm → oxy trắng", "Giấm 1:4 10–20 phút. Oxy chỉ trắng/cotton.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn đường/màu → không sấy (vàng sau).")
    ),
    "S_DOENJANG": (
        _START_VI
        + _step_vi(1, "Cạo · lạnh", "Cạo doenjang nhẹ. Xả lạnh.")
        + "\n"
        + _step_vi(2, "Nước rửa chén → enzyme", "D2 → enzyme 15–40. Lụa/len: cấm enzyme. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nâu/mùi → không sấy.")
    ),
    "S_GOCHUJANG": (
        _START_VI
        + _step_vi(1, "Cạo · không chà", "Cạo gochujang. Không chà loang đỏ.")
        + "\n"
        + _step_vi(2, "Nước rửa chén → giấm", "D2 → giấm 1:4. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn đỏ/mùi → không sấy.")
    ),
    "S_PERSIMMON": (
        _START_VI
        + _step_vi(1, "Ngay · lạnh", "Hồng/quả hồng: xử lý sớm. Thấm lạnh, không chà.")
        + "\n"
        + _step_vi(2, "Giấm lặp · oxy trắng", "Giấm 1:4 10–20 lặp. Oxy chỉ trắng. Trễ → báo khách.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nâu → không sấy.")
    ),
    "S_CRAYON": (
        _START_VI
        + _step_vi(1, "Làm lạnh rồi bẻ", "Làm lạnh/đông rồi bẻ Cap2.")
        + "\n"
        + _step_vi(2, "Giấy + nhiệt thấp (quản lý)", "Hỏi quản lý. Giấy thấm + ủi thấp. D2. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn sáp/màu → không sấy.")
    ),
    "S_SOFTENER_SPOT": (
        _START_VI
        + _step_vi(1, "Vòng dầu softener", "Vòng dầu do softener. Còn nhờn → không sấy.")
        + "\n"
        + _step_vi(2, "Nước rửa chén", "D2 5–15 phút. Có thể giấm 1:4. Giặt ấm lại.")
        + "\n"
        + _step_vi(3, "Sấy khi hết nhờn", "Chỉ sấy khi hết nhờn.")
    ),
    "S_MUSTARD": (
        _START_VI
        + _step_vi(1, "Gạt · lạnh", "Gạt. Thấm lạnh. Không chà.")
        + "\n"
        + _step_vi(2, "Nước rửa chén · oxy trắng", "D2 → oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn vàng → không sấy.")
    ),
    "S_URINE": (
        _START_VI
        + _step_vi(1, "Găng · lạnh · không trộn", "Găng. Chỉ lạnh. Không trộn ammonia + javel.")
        + "\n"
        + _step_vi(2, "Enzyme → giấm", "Enzyme → giấm 1:4. Lụa/len: trung tính.")
        + "\n"
        + _step_vi(3, "Giặt", "Xả kỹ rồi giặt. Còn mùi → không sấy.")
    ),
    "S_VOMIT": (
        _START_VI
        + _step_vi(1, "PPE · thông gió", "Găng + thoáng. Gạt đặc. Cấm nóng. Không trộn hóa chất.")
        + "\n"
        + _step_vi(2, "Lạnh · enzyme → giấm", "Xả lạnh → enzyme → giấm. Lụa/len: cấm enzyme.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn mùi/vết → không sấy.")
    ),
    "S_DEODORANT": (
        _START_VI
        + _step_vi(1, "Cặn trắng vs vàng", "Cặn trắng → giấm. Nách vàng → enzyme → oxy trắng. Cấm javel.")
        + "\n"
        + _step_vi(2, "Xử lý", "Giấm 1:4 hoặc enzyme 15–30.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn cặn/vàng → không sấy.")
    ),
    "S_PERFUME": (
        _START_VI
        + _step_vi(1, "Lạnh · báo vàng muộn", "Xả lạnh. Áo trắng có thể vàng sau — báo khách.")
        + "\n"
        + _step_vi(2, "Giấm · oxy ngắn", "Giấm 1:4. Oxy ngắn chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt · thoáng", "Giặt, phơi thoáng. Không sấy khi còn mùi.")
    ),
    "S_SUNSCREEN": (
        _START_VI
        + _step_vi(1, "Bột hút · cấm javel", "Phủ bột 10–30 phút. Cấm javel. Còn nhờn → không sấy.")
        + "\n"
        + _step_vi(2, "Nước rửa chén", "D2 nhẹ. Lụa/len: trung tính.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Hết nhờn mới sấy.")
    ),
    "S_MASCARA": (
        _START_VI
        + _step_vi(
            1,
            "Thấm trước · không chà",
            "Ấn khăn trắng từ trên. Không chà ngang.\n"
            "※ Lụa/len: hỏi quản lý.",
        )
        + "\n"
        + _step_vi(
            2,
            "Nước rửa chén → cồn IPA 70%",
            "Chấm 1–2 giọt nước rửa chén, xả lạnh.\n"
            "Còn màu: ⚠️ thông gió + cồn 70% — lộn trái, ấn 3 giây, đổi khăn 5–8 lần,\n"
            "⑧ xả lạnh 15–20°C. Oxy chỉ áo trắng.\n"
            "🛑 Phai màu → dừng.",
        )
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn đen → không sấy.")
    ),
    "S_IODINE": (
        _START_VI
        + _step_vi(
            1,
            "Quản lý · thử góc",
            "Iodine mạnh. Hỏi quản lý. Lụa/len: ưu tiên chuyên/từ chối.",
        )
        + "\n"
        + _step_vi(
            2,
            "Chấm IPA 70%",
            "⚠️ Thông gió. Thử góc → lộn trái, ấn 3 giây, đổi khăn, ⑧ xả lạnh. Oxy chỉ trắng.",
        )
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nâu → không sấy.")
    ),
    "S_STARCH_TRANSFER": (
        _START_VI
        + _step_vi(1, "Iểm hồ/tinh bột", "Ưu tiên enzyme. Hỏi quản lý.")
        + "\n"
        + _step_vi(2, "Ngâm enzyme", "Enzyme 20–40 phút. Không chà mạnh.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn bột trắng → không sấy.")
    ),
    "S_GUM": (
        _START_VI
        + _step_vi(1, "Đông rồi bẻ", "Túi + đông 30–60 phút. Bẻ khi giòn.")
        + "\n"
        + _step_vi(2, "Acetone cực ít (quản lý)", "Hỏi quản lý. Cấm acetate/lụa. Thử góc + găng.")
        + "\n"
        + _step_vi(3, "Nước rửa chén · giặt", "D2 rồi giặt. Còn dính → không sấy.")
    ),
    "S_CANDLE_WAX": (
        _START_VI
        + _step_vi(1, "Cạo khi cứng", "Để cứng rồi cạo Cap2 nhẹ.")
        + "\n"
        + _step_vi(2, "Giấy + ủi thấp (quản lý)", "Hỏi quản lý. Giấy thấm + nhiệt thấp. Lụa cẩn thận.")
        + "\n"
        + _step_vi(3, "Giặt", "D2 / oxy trắng nếu cần. Giặt rồi kiểm.")
    ),
    "S_GREASE": (
        _START_VI
        + _step_vi(1, "Bột hút", "Phủ bột. Còn nhờn/mùi → không sấy.")
        + "\n"
        + _step_vi(2, "Nước rửa chén · enzyme", "D2 → enzyme (trừ lụa/len). Dung môi mạnh chỉ quản lý.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn dầu → không sấy.")
    ),
    "S_CHILI": (
        _START_VI
        + _step_vi(1, "Phủi ớt", "Phủi. Không chà.")
        + "\n"
        + _step_vi(2, "Nước rửa chén → giấm", "D2 → giấm 1:4. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn đỏ/mùi → không sấy.")
    ),
    "S_BETEL": (
        _START_VI
        + _step_vi(1, "Quản lý · báo vết", "Trầu/cau khó. Hỏi quản lý. Báo còn vết.")
        + "\n"
        + _step_vi(2, "Lạnh · enzyme → giấm", "Lạnh → enzyme → giấm. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn nâu/đỏ → không sấy.")
    ),
    "S_SHRIMP_PASTE": (
        _START_VI
        + _step_vi(1, "Báo mùi", "Mắm tôm: dầu+đạm+màu. Báo còn mùi.")
        + "\n"
        + _step_vi(2, "D2 → enzyme → giấm", "Lần lượt. Lụa/len: cấm enzyme.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn mùi/màu → không sấy.")
    ),
    "S_GAC": (
        _START_VI
        + _step_vi(1, "Dầu trước màu", "Gấc: dầu rồi màu. Hỏi quản lý. Thử góc.")
        + "\n"
        + _step_vi(2, "D2 → cồn · oxy trắng", "D2 → cồn (thử). Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn cam/đỏ → không sấy.")
    ),
    "S_ANNATTO": (
        _START_VI
        + _step_vi(1, "Quản lý · thử góc", "Annatto dễ cố định. Hỏi quản lý. Thử góc.")
        + "\n"
        + _step_vi(2, "D2 → cồn → oxy trắng", "D2 → cồn. Oxy chỉ trắng.")
        + "\n"
        + _step_vi(3, "Giặt", "Giặt. Còn cam → không sấy.")
    ),
    "S_MOTORBIKE_OIL": (
        _START_VI
        + _step_vi(1, "Quản lý · báo vết", "Dầu xe máy khó, dễ cố định nhiệt. Hỏi quản lý.")
        + "\n"
        + _step_vi(2, "Bột → D2", "Bột hút → D2. Lụa/len: cấm dung môi mạnh/nóng.")
        + "\n"
        + _step_vi(3, "Dừng", "Không được → chuyên.")
    ),
    "S_RUST": (
        _START_VI
        + _step_vi(1, "Quản lý · cấm lụa/len", "Gỉ sắt nguy hiểm. Lụa/len/da → chuyên. Hỏi quản lý.")
        + "\n"
        + _step_vi(2, "Oxalic chỉ vải an toàn", "Găng + thử góc + trung hòa. Không dùng javel cho gỉ.")
        + "\n"
        + _step_vi(3, "Dừng", "Nghi ngờ → dừng, chuyên.")
    ),
    "S_PAINT_LATEX": (
        _START_VI
        + _step_vi(1, "Sơn nước khô · khó", "Báo một phần / từ chối. Hỏi quản lý.")
        + "\n"
        + _step_vi(2, "Cạo nhẹ · D2", "Cạo Cap2. D2. Dung môi mạnh chỉ quản lý.")
        + "\n"
        + _step_vi(3, "Dừng", "Không được → chuyên.")
    ),
    "S_PAINT_OIL": (
        _START_VI
        + _step_vi(1, "Sơn dầu · cấm thinner lụa", "Acetate/lụa/len: cấm thinner → chuyên ngay. Hỏi quản lý.")
        + "\n"
        + _step_vi(2, "Chỉ theo quản lý", "Không tự ý dung môi. Thông gió.")
        + "\n"
        + _step_vi(3, "Dừng", "Nguy hiểm → dừng.")
    ),
    "S_SHOE_POLISH": (
        _START_VI
        + _step_vi(1, "Xi giày · khó", "Nhiều lớp. Báo khách. Lụa/da lộn → chuyên.")
        + "\n"
        + _step_vi(2, "Chỉ quản lý", "Cạo nhẹ. Dung môi mạnh chỉ quản lý + thông gió.")
        + "\n"
        + _step_vi(3, "Dừng", "Không được → chuyên.")
    ),
    "S_FECES": (
        _START_VI
        + _step_vi(1, "Vệ sinh · PPE", "Găng. Tách dụng cụ. Cấm nóng/sấy. An toàn trước.")
        + "\n"
        + _step_vi(2, "Lạnh · enzyme", "Gạt → lạnh → enzyme (trừ lụa/len). Nặng → chuyên/trả.")
        + "\n"
        + _step_vi(3, "Giặt theo quy định", "Theo quy vệ sinh cửa hàng. Còn mùi → không sấy.")
    ),
}