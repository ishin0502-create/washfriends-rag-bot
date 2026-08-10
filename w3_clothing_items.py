# -*- coding: utf-8 -*-
"""W3: remaining clothing items + fabric×chem NEVER_USE owner cards."""
from __future__ import annotations

# New Item nodes (kb clothing protocols missing from graph)
CLOTHING_ITEMS = [
    {
        "id": "I_DRESS",
        "name": "Dress / one-piece",
        "name_vi": "Dam / vay lien than",
        "name_ko": "드레스·원피스",
        "fabric_id": "F1",
        "precheck_ko": "원단·안감·장식(비즈) 먼저. 가장 약한 원단 기준으로 세탁.",
        "why_ko": "[왜 이 순서] 원피스는 원단이 다양. 라벨→가장 섬세한 원단 기준. 실크=손세탁·중성세제. 면=기계 가능. 파티드레스=드라이 우선. 지퍼 잠그고 세탁망.",
        "fresh_path_ko": "(1)라벨·원단·장식 확인. (2)실크: 손세탁 ≤30C 중성세제. 면: ~40C. 폴리:~30C. (3)장식=뒤집기+세탁망. (4)드레이프=그늘 걸이 건조. (5)불확실 파티드레스→드라이/거절.",
        "dried_path_ko": "이미 형태 붕괴: 추가 강처리 중단, 전문.",
        "aftercare_ko": "건조 전 강광. 장식·안감 변형 확인.",
        "refuse_when_ko": "고가 파티드레스·불확실 원단 가정 세탁 강제 → 거절·드라이.",
        "sense_check_ko": "눈: 장식·이염. 형태: 드레이프 처짐 없음.",
        "success_rate_ko": "원단 명확: 양호. 복합 장식: 중간.",
        "precheck_vi": "Doc nhan + lot + trang tri truoc.",
        "why_vi": "[Tại sao] Dam = theo vai mong manh nhat. Lua: tay S1. Cotton: may 40C. Dam da hoi: dry-clean.",
        "fresh_path_vi": "(1)Nhan+vai. (2)Lua tay 30C S1. Cotton may 40C. (3)Tui luoi neu hat/sequin. (4)Phoi treo bong mat. (5)Dam da hoi khong chac → dry.",
        "dried_path_vi": "Form hong: dung, chuyen.",
        "aftercare_vi": "Anh sang truoc say. Kiem trang tri.",
        "refuse_when_vi": "Dam dat / khong chac → tu choi may.",
        "sense_check_vi": "Mat: lo mau/trang tri. Form: khong xe.",
        "success_rate_vi": "Vai ro: tot. Trang tri: trung binh.",
    },
    {
        "id": "I_KNIT",
        "name": "Knitwear / sweater",
        "name_vi": "Len dan / ao len",
        "name_ko": "니트·스웨터·뜨개",
        "fabric_id": "F3",
        "precheck_ko": "울/면 니트 구분. 울=중성세제·손세탁. 비틀어 짜기 금지.",
        "why_ko": "[왜 이 순서] 니트는 형태가 생명. 비틀어 짜면 변형. 찬물·중성세제, 눌러 물기만. 반드시 뉘어 건조 — 걸면 어깨 늘어남.",
        "fresh_path_ko": "(1)찬물 또는 ≤30C. (2)중성세제(울) / 면니트만 일반세제 약하게. (3)가볍게 눌러 헹굼 — 짜기 금지. (4)수건 위에 뉘어 형태 잡기→새 수건에 다시 뉘어 그늘 건조. (5)걸이 건조 금지.",
        "dried_path_ko": "이미 늘어남: 복원 제한 고지. 추가 기계 세탁 금지.",
        "aftercare_ko": "뉘어 건조 확인. 건조 전 강광(얼룩 있으면).",
        "refuse_when_ko": "울 니트 세탁기·건조기 강제 → 거절.",
        "sense_check_ko": "손: 비틀림 없음. 눈: 어깨·통 변형 없음.",
        "success_rate_ko": "손세탁+평건: 높음. 기계: 수축·변형 위험.",
        "precheck_vi": "Phan biet len/cotton. CAM vat.",
        "why_vi": "[Tại sao] Len dan = khong vat, phoi nam. May = co rut.",
        "fresh_path_vi": "(1)Lanh/<=30C. (2)S1. (3)Ep nhe, khong vat. (4)Phoi nam dung form. (5)CAM treo.",
        "dried_path_vi": "Da gian: bao gioi han.",
        "aftercare_vi": "Phoi nam. Anh sang neu co vet.",
        "refuse_when_vi": "Bat may/say len → tu choi.",
        "sense_check_vi": "Tay: khong xe. Mat: vai khong gian.",
        "success_rate_vi": "Tay+nam: cao. May: thap.",
    },
    {
        "id": "I_UNDERWEAR",
        "name": "Underwear / lingerie / bra",
        "name_vi": "Do lot / ao nguc / lingerie",
        "name_ko": "속옷·란제리·브라",
        "fabric_id": "F1",
        "precheck_ko": "브라=손세탁 또는 세탁망+섬세. 와이어·훅 보호.",
        "why_ko": "[왜 이 순서] 브라는 기계 직행 시 형태·와이어 손상. 면 팬티는 망+40C 가능. 스판=찬물·약하게. 유연제 과다 금지(탄성↓).",
        "fresh_path_ko": "(1)면 팬티: 세탁망 40C. (2)브라: 손세탁 ≤30C 또는 망+섬세. (3)란제리: 손세탁 중성. (4)건조: 브라 컵 형태 유지·뉘거나 세워 — 걸이 주의. 스판=그늘.",
        "dried_path_ko": "와이어 변형: 복원 어려움 고지.",
        "aftercare_ko": "매일 위생 세탁 권장. 건조 전 확인.",
        "refuse_when_ko": "고가 란제리 강한 표백·건조기 강제 → 거절.",
        "sense_check_ko": "손: 훅·와이어. 눈: 탄성·변색.",
        "success_rate_ko": "손/망: 양호. 기계 직행 브라: 형태 위험.",
        "precheck_vi": "Ao nguc: tay hoac tui luoi.",
        "why_vi": "[Tại sao] Ao nguc CAM may truc tiep. Cotton lot: tui luoi 40C.",
        "fresh_path_vi": "(1)Lot cotton: tui+40C. (2)Ao nguc: tay 30C. (3)Lingerie: tay S1. (4)Phoi giu form cup.",
        "dried_path_vi": "Khung meo: bao.",
        "aftercare_vi": "Giat hang ngay. Kiem form.",
        "refuse_when_vi": "Tay manh/say lingerie dat → tu choi.",
        "sense_check_vi": "Tay: day/khung. Mat: dan hoi.",
        "success_rate_vi": "Tay/tui: tot. May truc: rui ro.",
    },
    {
        "id": "I_ACTIVEWEAR",
        "name": "Sportswear / gym wear",
        "name_vi": "Do the thao / gym",
        "name_ko": "스포츠웨어·운동복·짐웨어",
        "fabric_id": "F2",
        "precheck_ko": "땀=빨리 세탁. 고온·유연제 금지(스판·흡습 기능↓).",
        "why_ko": "[왜 이 순서] 운동복은 즉시 세탁(발효 냄새). ~30C·세제 소량·섬세/스포츠 코스. 유연제 금지. 냄새 심하면 식초 1:4 사전 침지. DWR/고어는 세제 과다 금지.",
        "fresh_path_ko": "(1)즉시 또는 찬물 임시 담금. (2)~30C 기계, 세제 소량. (3)유연제 금지. (4)냄새: 식초 희석 30분 전처리. (5)저온 건조 또는 그늘. DWR는 낮은 열로 재활성화 가능(라벨).",
        "dried_path_ko": "냄새 고착: 식초 재처리. 기능 저하: 방수 스프레이 재도포 검토.",
        "aftercare_ko": "건조 전 강광·냄새(젖은 상태) 확인. 유연제 잔여 금지.",
        "refuse_when_ko": "고온 건조·유연제 강제(기능성) → 거절·고지.",
        "sense_check_ko": "코: 젖은 상태 땀내 없음. 손: 끈적임 없음.",
        "success_rate_ko": "즉시 세탁: 높음. 방치 후: 냄새 잔존 가능.",
        "precheck_vi": "Giat ngay. CAM xa vai + nhiet cao.",
        "why_vi": "[Tại sao] Mo hoi len men nhanh. 30C, it bot, CAM softener.",
        "fresh_path_vi": "(1)Giat ngay. (2)30C it D3. (3)Mui: A3 30 phut. (4)Say thap/phoi. CAM softener.",
        "dried_path_vi": "Mui khoa: A3 lai.",
        "aftercare_vi": "Kiem mui khi uot. Anh sang.",
        "refuse_when_vi": "Bat softener/nhiet cao chuc nang → bao/tu choi.",
        "sense_check_vi": "Mui: het khi uot. Tay: het nhon.",
        "success_rate_vi": "Giat som: cao. De lau: mui ton.",
    },
    {
        "id": "I_SCARF",
        "name": "Scarf / muffler",
        "name_vi": "Khan quang / scarf",
        "name_ko": "스카프·목도리·머플러",
        "fabric_id": "F4",
        "precheck_ko": "실크/울/면 구분. 실크·울=중성·약하게. 이염 주의.",
        "why_ko": "[왜 이 순서] 스카프는 얇고 이염·물짐 쉬움. 손세탁·중성, 비틀지 말 것. 뉘거나 평평 건조. 진한 색은 단독.",
        "fresh_path_ko": "(1)원단 확인. (2)찬물·중성 손세탁 Cap1. (3)눌러 헹굼. (4)단독·그늘 평건. (5)강한 표백 금지.",
        "dried_path_ko": "물짐·이염: 추가 강처리 주의, 고지.",
        "aftercare_ko": "건조 전 강광. 걸이보다 평건 권장(울/니트 스카프).",
        "refuse_when_ko": "고가 실크 스카프 기계·표백 강제 → 거절.",
        "sense_check_ko": "눈: 이염·물짐. 손: 비틀림 없음.",
        "success_rate_ko": "손세탁: 양호. 기계: 위험.",
        "precheck_vi": "Lua/len/cotton. CAM may manh.",
        "why_vi": "[Tại sao] Khan mong — tay S1, khong vat, phoi phang.",
        "fresh_path_vi": "(1)Vai. (2)Tay lanh S1 Cap1. (3)Ep xa. (4)Phoi phang rieng. (5)CAM tay manh.",
        "dried_path_vi": "Vet nuoc/lo mau: bao.",
        "aftercare_vi": "Anh sang. Phoi phang.",
        "refuse_when_vi": "Bat may/tay lua dat → tu choi.",
        "sense_check_vi": "Mat: lo mau. Tay: khong xe.",
        "success_rate_vi": "Tay: tot. May: thap.",
    },
    {
        "id": "I_UNIFORM",
        "name": "Uniform / workwear",
        "name_vi": "Dong phuc / do cong so dac biet",
        "name_ko": "유니폼·근무복·교복",
        "fabric_id": "F2",
        "precheck_ko": "라벨·혼용률·부착물(명찰·견장). 이염·기름·땀 부위 확인.",
        "why_ko": "[왜 이 순서] 유니폼은 폴리·혼방이 많음. 라벨 수온 준수, 명찰·장식은 세탁망. 목·겨드랑이 황변은 효소→산소(흰만). 강한 표백은 유색 금지.",
        "fresh_path_ko": "(1)라벨·장식. (2)전처리 목/겨드랑이. (3)라벨 온도 기계+망. (4)유색: 산소만 신중. (5)건조 전 강광.",
        "dried_path_ko": "황변 고착: 셔츠 황변 SOP 연계, 100% 비보장.",
        "aftercare_ko": "명찰·주름 확인. 건조 전 강광.",
        "refuse_when_ko": "특수 방화/고기능 유니폼 임의 표백 → 거절·매뉴얼.",
        "sense_check_ko": "눈: 황변·이염. 손: 장식 손상 없음.",
        "success_rate_ko": "일반 혼방: 양호. 특수 원단: 매뉴얼 우선.",
        "precheck_vi": "Nhan + phu kien. Vet mo hoi/co.",
        "why_vi": "[Tại sao] Dong phuc poly/hon — theo nhan, tui luoi, pretreat co/nach.",
        "fresh_path_vi": "(1)Nhan. (2)Pretreat. (3)May theo nhan + tui. (4)Mau: than B1. (5)Anh sang truoc say.",
        "dried_path_vi": "Vang khoa: SOP vang ao, bao.",
        "aftercare_vi": "Kiem phu kien. Anh sang.",
        "refuse_when_vi": "Do dac thu bat tay manh → tu choi.",
        "sense_check_vi": "Mat: vang/lo mau. Tay: phu kien.",
        "success_rate_vi": "Hon thuong: tot. Vai dac biet: theo manual.",
    },
]

# Owner-facing NEVER_USE summaries (mirror Fabric NEVER_USE seed — do not invent)
FABRIC_NEVER_USE_CARD = {
    "silk": {
        "ko": "실크 금지: 효소·산소/염소 표백·강한 산·옥살산·환원표백. 우선 중성세제·찬물·Cap1–2.",
        "vi": "Lua CAM: enzyme, tay oxy/Javel, acid manh, X2, X1. Uu tien S1 + lanh + Cap1–2.",
        "en": "Silk NEVER: enzyme, oxygen/chlorine bleach, strong acid, oxalic, reducing bleach. Prefer neutral + cold + Cap1–2.",
    },
    "wool": {
        "ko": "울 금지: 효소·산소/염소 표백·강한 산·옥살산. 중성세제·찬물·비틀기 금지.",
        "vi": "Len CAM: enzyme, tay oxy/Javel, acid manh, X2. S1 + lanh, khong vat.",
        "en": "Wool NEVER: enzyme, oxygen/chlorine bleach, strong acid, oxalic. Neutral + cold; no wring.",
    },
    "leather": {
        "ko": "가죽 금지: 세탁기·산소/염소 표백·효소·강한 침지. 최소 수분·전문 크림.",
        "vi": "Da CAM: may giat, tay oxy/Javel, enzyme, ngam manh. It nuoc + kem da.",
        "en": "Leather NEVER: washer, bleach, enzyme, heavy soak. Minimal water + leather cream.",
    },
    "suede": {
        "ko": "스웨이드 금지: 물·표백·효소 과다. 마른 브러시 우선, 심하면 전문.",
        "vi": "Suede CAM: nuoc/tay/enzyme manh. Chai kho uu tien, nang → chuyen.",
        "en": "Suede NEVER: water/bleach/heavy enzyme. Dry brush first; severe → pro.",
    },
    "fur": {
        "ko": "모피 금지: 물세탁·표백·건조기. 전문 모피 클리닝.",
        "vi": "Long thu CAM: giat nuoc, tay, may say. Chuyen fur.",
        "en": "Fur NEVER: wet wash, bleach, dryer. Professional fur clean only.",
    },
    "rayon": {
        "ko": "레이온 주의: 아세톤 금지, 물에 약함 — 손세탁·형태 고정 건조.",
        "vi": "Rayon: CAM acetone, yeu nuoc — tay + giu form khi kho.",
        "en": "Rayon: no acetone; weak when wet — hand wash + reshape dry.",
    },
}


def never_use_card_for_fabric(fabric_type: str, lang: str = "ko") -> str:
    ft = (fabric_type or "").lower()
    key = ""
    if "silk" in ft or "lua" in ft:
        key = "silk"
    elif "wool" in ft or "len" in ft:
        key = "wool"
    elif "suede" in ft or "nubuck" in ft:
        key = "suede"
    elif "leather" in ft or ft == "da":
        key = "leather"
    elif "fur" in ft:
        key = "fur"
    elif "rayon" in ft:
        key = "rayon"
    if not key:
        return ""
    card = FABRIC_NEVER_USE_CARD[key]
    return card.get(lang) or card["ko"]


def clothing_seed_rows():
    return list(CLOTHING_ITEMS)
