# KB 파일 인덱스 (`kb/`)

사람·Claude가 읽는 **풍부한 원문**이다.  
라이브 Zalo 답은 이 MD를 전부 읽지 않고, Neo4j 시드 + protocol + KO education을 주로 쓴다.  
→ Claude는 KB로 **깊이·빠진 주제**를 찾고, 제안은 “시드/점주 답에 올릴 짧은 문장”으로 압축할 것.

원본 경로: 저장소 `kb/` (이 패키지에 복사본을 두지 않음 — 용량·중복 방지).  
Claude Project에 넣을 때: 아래 파일을 **추가 업로드**하면 된다.

---

## 핵심 프레임

| 파일 | 내용 |
|------|------|
| `laundry_kb_v3_protocol.md` | v3 철학: 도구·힘·방향·감각·구조. “무엇을”→“어떻게” |
| `laundry_kb_v3_prototype.md` | 프로토타입(립스틱/커피/혈액 등) 상세 카드 |
| `laundry_kb_v3_localization.md` | 베트남 수질·기후·현장 맥락 |
| `laundry_kb_v3_ops_gold.md` | 접수·거절·클레임·운영 골드 규칙 |
| `laundry_kb_v3_wf_products.md` | 본사 공급품·시판 대체(점주 구매 안내) |
| `laundry_kb_v3_advanced_field.md` | 고급 현장: 라벨, 황변, 이염, 다운, 라테라이트, 오토바이 등 |

## 얼룩 그룹

| 파일 | 내용 |
|------|------|
| `laundry_kb_v3_stains_protein.md` | 단백질 |
| `laundry_kb_v3_stains_tannin.md` | 탄닌 |
| `laundry_kb_v3_stains_oil.md` | 오일·지방 |
| `laundry_kb_v3_stains_dye.md` | 색소·염료 |
| `laundry_kb_v3_stains_special.md` | 특수 |

## 품목·도구·기계

| 파일 | 내용 |
|------|------|
| `laundry_kb_v3_tools_equipment.md` | 도구·장비·PPE |
| `laundry_kb_v3_items_clothing.md` | 의류 유형 |
| `laundry_kb_v3_items_home.md` | 홈텍스타일 |
| `laundry_kb_v3_items_ironing.md` | 다림질 |
| `laundry_kb_v3_items_business.md` | 비즈니스/유니폼 등 |
| `laundry_kb_v3_items_machine.md` | 세탁기·건조기 |

---

## 코드 쪽 “살아있는” 교육 (KB보다 라이브에 가깝다)

| 파일 | 역할 |
|------|------|
| `ko_stain_education.py` | 얼룩별 why/fresh/dried **한국어** (이 패키지 `02_STAIN_SOP_KO.md`로 export) |
| `protocol.py` | 실행 순서·약품·분·흰옷 only 스텝 |
| `chem_owner_vi.py` | 점주용 약품 구매·희석 한 줄 |
| `stain_age_buckets.py` | 신선/마름/고착 |
| `specialty_garment_care.py` / `leather_care.py` | 특수 품목·가죽 |
| `main.py` `/admin/seed` | Neo4j에 넣는 시드 |

---

## Claude 업로드 추천 세트 (토큰 절약)

**필수 (작음):**  
`00_BRIEF` ~ `05_ASK_CLAUDE` + `02_STAIN_SOP_KO` + `04_LIVE_ANSWER_EXAMPLES`

**깊이 필요할 때 추가:**  
`protocol.md`, `stains_*.md`, `tools_equipment.md`, `ops_gold.md`, `wf_products.md`, `advanced_field.md`

**나중에:**  
items_* 전부, machine — 특수 품목 챕터 보강할 때.
