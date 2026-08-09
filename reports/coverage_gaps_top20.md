# Coverage gaps TOP 20

Generated: 2026-08-09T15:56:23.448574+00:00

## Summary
- Matrix issues (silk/wool/acetate/cotton): **0**
- Seed stains missing Protocol: **0**
- Ask failure log clusters: **1**
- Neo4j cache rows used: **0**

## TOP 20 (fix next)

1. **[ask_failure]** `구스이블 세탁방법 알려줘` × `-` — severity=60 weight=12 — empty_graph_or_failure
   - hits=12
2. **[local_topic]** `가죽` × `-` — severity=40 weight=21 — topic:가죽
   - hits=21
3. **[local_topic]** `매니큐어` × `-` — severity=40 weight=3 — topic:매니큐어
   - hits=3
4. **[local_topic]** `아세톤` × `-` — severity=40 weight=3 — topic:아세톤
   - hits=3
5. **[local_topic]** `아세테이트` × `-` — severity=40 weight=2 — topic:아세테이트
   - hits=2
6. **[local_topic]** `토마토소스` × `-` — severity=40 weight=2 — topic:토마토소스
   - hits=2
7. **[local_topic]** `구스` × `-` — severity=40 weight=1 — topic:구스
   - hits=1
8. **[local_topic]** `된장` × `-` — severity=40 weight=1 — topic:된장
   - hits=1
9. **[local_topic]** `기름때` × `-` — severity=40 weight=1 — topic:기름때
   - hits=1

## How to use
1. Fix any `chem_leak` / `empty_*` matrix rows first (CI will fail).
2. Add Protocol/hard-route for `missing_protocol` and frequent ask failures.
3. Re-run: `python scripts/extract_coverage_gaps.py`
4. With Neo4j: `python scripts/extract_coverage_gaps.py --from-cache`
