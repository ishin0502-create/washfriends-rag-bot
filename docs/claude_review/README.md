# Claude 검토 패키지 README

Wash Friends **점주 세탁 교육**을 Claude에 넘겨 보강·검토하기 위한 묶음이다.

폴더: `docs/claude_review/`

| 파일 | 용도 |
|------|------|
| `00_BRIEF.md` | 목표·금지·산출물 형식 (**먼저 읽기**) |
| `01_CURRICULUM_NOW.md` | 지금 강한/약한 교육 축 |
| `02_STAIN_SOP_KO.md` | 얼룩별 한국어 why / fresh / dried (export) |
| `03_KB_INDEX.md` | `kb/` 원문 목록 + 업로드 추천 |
| `04_LIVE_ANSWER_EXAMPLES.md` | 라이브 답 샘플 |
| `05_ASK_CLAUDE.md` | Claude에 붙여넣을 프롬프트 |

---

## Claude에 전달하는 방법

### 방법 A — Claude Projects (추천)

1. [claude.ai](https://claude.ai) → **Project** 생성  
   이름 예: `Wash Friends Owner Education`
2. Project Knowledge에 업로드:
   - 이 폴더의 `00`~`05` 전부
   - (선택) `kb/laundry_kb_v3_protocol.md`, `stains_*.md`, `tools_equipment.md`, `ops_gold.md`, `wf_products.md`
3. 새 채팅에서 `05_ASK_CLAUDE.md` 본문을 붙여넣기

### 방법 B — ZIP

1. `docs/claude_review` + 필요한 `kb` 파일을 ZIP
2. Project 또는 채팅에 첨부

### 방법 C — 채팅만

토큰이 부족하면 **필수만**: `00`, `01`, `02`, `04`, `05`

---

## 우리 팀이 Claude 답을 받은 뒤

1. `REVIEW_FINDINGS` / `SOP_PATCH_PROPOSALS` 검토  
2. 맞는 패치만 `ko_stain_education.py` / `protocol.py` / 시드에 반영  
3. `/ask` 스모크 → Railway 배포  
4. **틀린 팁은 시드에 넣지 않음**

---

## 재생성

`02_STAIN_SOP_KO.md`는 아래 스크립트로 다시 만들 수 있다.

```bash
python scripts/export_claude_review_sop.py
```
