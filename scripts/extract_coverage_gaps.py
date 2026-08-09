# -*- coding: utf-8 -*-
"""Extract TOP coverage gaps: static Protocol×fabric matrix + local ask signals.

Usage:
  python scripts/extract_coverage_gaps.py
  python scripts/extract_coverage_gaps.py --from-cache   # needs NEO4J_* env

Outputs:
  reports/coverage_gaps_top20.md
  reports/coverage_gaps_full.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from protocol import (  # noqa: E402
    PROTOCOL_BUILDERS,
    _chem_blocked,
    _fabric_flags,
    apply_protocol_to_graph,
    has_protocol,
)

REPORT_DIR = ROOT / "reports"
DELICATE = [
    ("cotton", "F1", "Cotton"),
    ("silk", "F4", "Silk"),
    ("wool", "F3", "Wool"),
    ("acetate", "F11", "Acetate"),
]


def _graph(stain_id: str, fabric_id: str, fabric_name: str) -> dict:
    sturdy = fabric_id in {"F1", "F2", "F5", "F6"}
    return {
        "stain_context": {"id": stain_id},
        "fabric_context": {
            "id": fabric_id,
            "name": fabric_name,
            "acid_safe": sturdy,
            "enzyme_safe": sturdy,
            "can_oxygen": sturdy,
            "can_bleach": fabric_id == "F1",
        },
        "chemicals": [],
        "tools": [],
        "garment_color": "white",
    }


def matrix_gaps() -> list[dict]:
    gaps: list[dict] = []
    for ft, fid, fn in DELICATE:
        for sid in sorted(PROTOCOL_BUILDERS):
            ent = {"stain_id": sid, "fabric_type": ft, "garment_color": "white"}
            out = apply_protocol_to_graph(_graph(sid, fid, fn), entities=ent)
            tools = out.get("tools") or []
            chems = out.get("chemicals") or []
            flags = _fabric_flags(out, ent)
            leak_codes = []
            for c in chems:
                code = str(c.get("code") or "")
                blocked, rk, _rv = _chem_blocked(code, flags, "white")
                if blocked:
                    leak_codes.append(code)
            severity = 0
            reasons = []
            if leak_codes:
                severity = 100
                reasons.append(f"chem_leak:{','.join(leak_codes)}")
            if not chems:
                severity = max(severity, 80)
                reasons.append("empty_chems")
            if not tools:
                severity = max(severity, 70)
                reasons.append("empty_tools")
            if not reasons:
                continue
            gaps.append(
                {
                    "kind": "matrix",
                    "stain_id": sid,
                    "fabric_type": ft,
                    "fabric_id": fid,
                    "severity": severity,
                    "reasons": reasons,
                    "tool_ids": [t.get("id") for t in tools],
                    "chem_codes": [c.get("code") for c in chems],
                    "weight": 1,
                }
            )
    return gaps


def seed_vs_protocol_gaps() -> list[dict]:
    """Stains referenced in main.py seed that lack Protocol builders."""
    main = (ROOT / "main.py").read_text(encoding="utf-8", errors="ignore")
    seeded = sorted(set(re.findall(r"id:'(S_[A-Z0-9_]+)'", main)))
    gaps = []
    for sid in seeded:
        if has_protocol(sid):
            continue
        gaps.append(
            {
                "kind": "missing_protocol",
                "stain_id": sid,
                "fabric_type": "*",
                "fabric_id": "",
                "severity": 90,
                "reasons": ["no_protocol_builder"],
                "tool_ids": [],
                "chem_codes": [],
                "weight": 3,
            }
        )
    return gaps


def failure_log_gaps() -> list[dict]:
    path = ROOT / "logs" / "ask_failures.jsonl"
    if not path.exists():
        return []
    counts: Counter[str] = Counter()
    samples: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("reason") in {"unit_test", "test"}:
            continue
        msg = str(row.get("message") or "").strip()
        if not msg or msg == "smoke":
            continue
        key = msg[:120]
        counts[key] += 1
        samples.setdefault(key, msg)
    gaps = []
    for key, n in counts.most_common(40):
        gaps.append(
            {
                "kind": "ask_failure",
                "stain_id": "",
                "fabric_type": "",
                "fabric_id": "",
                "severity": 60,
                "reasons": ["empty_graph_or_failure"],
                "tool_ids": [],
                "chem_codes": [],
                "weight": n,
                "message": samples[key],
                "hits": n,
            }
        )
    return gaps


def local_ask_topic_gaps() -> list[dict]:
    """Weak signal from local smoke/ask JSON leftovers (dev artifacts)."""
    topic_re = re.compile(
        r"(구스|이불|패딩|혼방|아세테이트|나일론|가죽|스웨이드|감물|된장|"
        r"고추장|매니큐어|아세톤|기름때|토마토소스|goose|duvet|acetate)",
        re.I,
    )
    counts: Counter[str] = Counter()
    for p in list(ROOT.glob("_ask_*.json")) + list((ROOT / "_smoke_v10").glob("*.txt")):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")[:2000]
        except OSError:
            continue
        for m in topic_re.findall(text):
            counts[m.lower()] += 1
    gaps = []
    for topic, n in counts.most_common(20):
        gaps.append(
            {
                "kind": "local_topic",
                "stain_id": "",
                "fabric_type": "",
                "fabric_id": "",
                "severity": 40,
                "reasons": [f"topic:{topic}"],
                "tool_ids": [],
                "chem_codes": [],
                "weight": n,
                "message": topic,
                "hits": n,
            }
        )
    return gaps


def neo4j_cache_gaps() -> list[dict]:
    """Optional: rank AnswerCache questions when NEO4J_* is set."""
    import os

    uri = os.getenv("NEO4J_URI") or ""
    user = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER") or ""
    password = os.getenv("NEO4J_PASSWORD") or ""
    if not (uri and user and password):
        return []
    try:
        from neo4j import GraphDatabase
    except ImportError:
        return []

    gaps: list[dict] = []
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            rows = session.run(
                """
                MATCH (c:AnswerCache)
                RETURN coalesce(c.question_raw, c.question_norm) AS q,
                       coalesce(c.hit_count, 1) AS hits,
                       c.context_key AS ck
                ORDER BY hits DESC
                LIMIT 300
                """
            )
            for r in rows:
                q = str(r["q"] or "")
                hits = int(r["hits"] or 1)
                ck = str(r["ck"] or "")
                gaps.append(
                    {
                        "kind": "answer_cache",
                        "stain_id": "",
                        "fabric_type": "",
                        "fabric_id": "",
                        "severity": 50,
                        "reasons": ["cache_frequent"],
                        "tool_ids": [],
                        "chem_codes": [],
                        "weight": hits,
                        "message": q[:200],
                        "hits": hits,
                        "context_key": ck,
                    }
                )
    finally:
        driver.close()
    return gaps


def score(g: dict) -> float:
    return float(g.get("severity", 0)) * (1.0 + 0.15 * float(g.get("weight", 1)))


def rank_top(gaps: list[dict], n: int = 20) -> list[dict]:
    # Dedupe matrix by stain×fabric keeping highest severity
    best: dict[str, dict] = {}
    passthrough = []
    for g in gaps:
        if g["kind"] == "matrix":
            k = f"matrix:{g['stain_id']}:{g['fabric_type']}:{','.join(g['reasons'])}"
            if k not in best or score(g) > score(best[k]):
                best[k] = g
        elif g["kind"] == "missing_protocol":
            k = f"missing:{g['stain_id']}"
            best[k] = g
        else:
            passthrough.append(g)
    merged = list(best.values()) + passthrough
    merged.sort(key=score, reverse=True)
    return merged[:n]


def write_reports(all_gaps: list[dict], top: list[dict], meta: dict) -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "meta": meta,
        "top20": top,
        "all_gaps": all_gaps,
        "counts": {
            "total": len(all_gaps),
            "matrix": sum(1 for g in all_gaps if g["kind"] == "matrix"),
            "missing_protocol": sum(1 for g in all_gaps if g["kind"] == "missing_protocol"),
            "ask_failure": sum(1 for g in all_gaps if g["kind"] == "ask_failure"),
        },
    }
    (REPORT_DIR / "coverage_gaps_full.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Coverage gaps TOP 20",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "## Summary",
        f"- Matrix issues (silk/wool/acetate/cotton): **{payload['counts']['matrix']}**",
        f"- Seed stains missing Protocol: **{payload['counts']['missing_protocol']}**",
        f"- Ask failure log clusters: **{payload['counts']['ask_failure']}**",
        f"- Neo4j cache rows used: **{meta.get('neo4j_rows', 0)}**",
        "",
        "## TOP 20 (fix next)",
        "",
    ]
    for i, g in enumerate(top, 1):
        title = g.get("stain_id") or g.get("message") or g["kind"]
        fab = g.get("fabric_type") or "-"
        lines.append(
            f"{i}. **[{g['kind']}]** `{title}` × `{fab}` — "
            f"severity={g['severity']} weight={g.get('weight')} — "
            f"{', '.join(g.get('reasons') or [])}"
        )
        if g.get("chem_codes") is not None and g["kind"] == "matrix":
            lines.append(
                f"   - tools={g.get('tool_ids')} chems={g.get('chem_codes')}"
            )
        if g.get("hits"):
            lines.append(f"   - hits={g['hits']}")
    lines.extend(
        [
            "",
            "## How to use",
            "1. Fix any `chem_leak` / `empty_*` matrix rows first (CI will fail).",
            "2. Add Protocol/hard-route for `missing_protocol` and frequent ask failures.",
            "3. Re-run: `python scripts/extract_coverage_gaps.py`",
            "4. With Neo4j: `python scripts/extract_coverage_gaps.py --from-cache`",
            "",
        ]
    )
    (REPORT_DIR / "coverage_gaps_top20.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-cache", action="store_true", help="Also query Neo4j AnswerCache")
    args = ap.parse_args()

    all_gaps: list[dict] = []
    all_gaps.extend(matrix_gaps())
    all_gaps.extend(seed_vs_protocol_gaps())
    all_gaps.extend(failure_log_gaps())
    all_gaps.extend(local_ask_topic_gaps())
    neo = neo4j_cache_gaps() if args.from_cache else []
    all_gaps.extend(neo)

    top = rank_top(all_gaps, 20)
    meta = {
        "protocols": len(PROTOCOL_BUILDERS),
        "fabrics": [f[0] for f in DELICATE],
        "neo4j_rows": len(neo),
        "from_cache": bool(args.from_cache),
    }
    write_reports(all_gaps, top, meta)

    print(f"protocols={meta['protocols']} matrix_gaps={sum(1 for g in all_gaps if g['kind']=='matrix')}")
    print(f"wrote {REPORT_DIR / 'coverage_gaps_top20.md'}")
    for i, g in enumerate(top, 1):
        title = g.get("stain_id") or g.get("message") or g["kind"]
        print(f"{i:02d}. [{g['kind']}] {title} x {g.get('fabric_type') or '-'} :: {g.get('reasons')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
