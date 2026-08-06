"""
response_cache.py
Wash Friends — safe answer cache for repeated / similar franchise questions.

Design goals:
- Fail-open: any cache error → caller continues without cache (no user impact).
- No extra OpenAI calls for lookup (string similarity only).
- Persist in Neo4j (survives Railway restarts).
- Opt-out via ANSWER_CACHE_ENABLED=false
"""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from typing import Optional

from neo4j import GraphDatabase, Driver

_neo4j: Optional[Driver] = None


def _driver() -> Driver:
    global _neo4j
    if _neo4j is None:
        _neo4j = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        )
    return _neo4j


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def is_enabled() -> bool:
    return _env_bool("ANSWER_CACHE_ENABLED", True)


def similarity_threshold() -> float:
    try:
        v = float(os.getenv("ANSWER_CACHE_SIMILARITY", "0.90"))
        return min(0.99, max(0.75, v))
    except ValueError:
        return 0.90


def ttl_days() -> int:
    try:
        return max(1, int(os.getenv("ANSWER_CACHE_TTL_DAYS", "30")))
    except ValueError:
        return 30


def max_entries() -> int:
    try:
        return max(50, int(os.getenv("ANSWER_CACHE_MAX_ENTRIES", "500")))
    except ValueError:
        return 500


def cache_version() -> str:
    # v3: shop names + WF supply products in answers
    return os.getenv("ANSWER_CACHE_VERSION", "v36")


def _normalize_key(text: str) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFD", text.lower().strip())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = t.replace("đ", "d")
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


# Topic guards — avoid matching "coffee on silk" with "coffee on cotton"
_FABRIC_MARKERS = (
    "cotton", "lua", "silk", "len", "wool", "polyester", "denim", "linen", "rayon", "voile",
)
_STAIN_MARKERS = (
    "mau", "blood", "ca phe", "coffee", "tra", "tea", "dau", "oil", "nuoc mam", "fish sauce",
    "laterite", "dat do", "xe may", "motorbike", "muc", "ink", "ca ri", "curry", "nghe",
    # KO — prevent fuzzy cross-topic hits when Hangul questions have empty Latin signatures
    "커피", "피", "혈액", "김치", "주스", "이염", "곰팡이", "케첩", "황변", "누렇", "와이셔츠",
    "립스틱", "가죽", "정장", "색바램", "풀",
)


def _topic_signature(norm: str) -> frozenset:
    if not norm:
        return frozenset()
    # Keep Hangul in signature space: normalize_key lowercases Latin but leaves Hangul
    raw = norm
    sig = set()
    for m in _FABRIC_MARKERS:
        if m in raw:
            sig.add(f"f:{m}")
    for m in _STAIN_MARKERS:
        if m in raw:
            sig.add(f"s:{m}")
    return frozenset(sig)


def _topics_compatible(a: str, b: str) -> bool:
    sa, sb = _topic_signature(a), _topic_signature(b)
    # If either side has no topic tags, do not fuzzy-match (avoids KO↔VI / empty stubs)
    if not sa or not sb:
        return False
    return sa == sb


def _entry_id(norm_q: str, context_key: str) -> str:
    raw = f"{cache_version()}|{context_key}|{norm_q}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _ensure_schema(session) -> None:
    session.run(
        "CREATE CONSTRAINT answer_cache_id IF NOT EXISTS "
        "FOR (c:AnswerCache) REQUIRE c.id IS UNIQUE"
    )


def _prune_old(session) -> None:
    """Keep DB bounded; never raise."""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=ttl_days())
        session.run(
            "MATCH (c:AnswerCache) WHERE c.created_at < $cutoff DELETE c",
            cutoff=cutoff.isoformat(),
        )
        session.run(
            """
            MATCH (c:AnswerCache)
            WITH c ORDER BY c.last_hit_at DESC
            SKIP $max
            WITH collect(c) AS old
            FOREACH (x IN old | DELETE x)
            """,
            max=max_entries(),
        )
    except Exception as e:
        print(f"[CACHE] prune skipped: {e}")


def lookup(question: str, context_key: str = "") -> Optional[str]:
    """
    Return cached answer if exact or fuzzy match found.
    Returns None on miss or any error (fail-open).
    """
    if not is_enabled():
        return None
    norm_q = _normalize_key(question)
    if len(norm_q) < 8:
        return None
    ctx = (context_key or "").strip()
    try:
        driver = _driver()
        with driver.session() as session:
            _ensure_schema(session)
            eid = _entry_id(norm_q, ctx)
            row = session.run(
                """
                MATCH (c:AnswerCache {id: $id, cache_version: $ver})
                RETURN c.answer AS answer
                """,
                id=eid,
                ver=cache_version(),
            ).single()
            if row and row.get("answer"):
                ans = row["answer"]
                if _is_stub_answer(ans):
                    print(f"[CACHE SKIP] stub exact id={eid[:8]}")
                else:
                    session.run(
                        """
                        MATCH (c:AnswerCache {id: $id})
                        SET c.hit_count = coalesce(c.hit_count, 0) + 1,
                            c.last_hit_at = $now
                        """,
                        id=eid,
                        now=datetime.now(timezone.utc).isoformat(),
                    )
                    print(f"[CACHE HIT] exact id={eid[:8]}")
                    return ans

            # Fuzzy scan — recent entries only (no OpenAI cost)
            threshold = similarity_threshold()
            rows = session.run(
                """
                MATCH (c:AnswerCache {cache_version: $ver})
                WHERE c.context_key = $ctx OR ($ctx = '' AND coalesce(c.context_key,'') = '')
                RETURN c.question_norm AS qn, c.answer AS answer
                ORDER BY c.last_hit_at DESC
                LIMIT 250
                """,
                ver=cache_version(),
                ctx=ctx,
            ).data()

            best_score = 0.0
            best_answer = None
            for r in rows:
                qn = r.get("qn") or ""
                ans = r.get("answer") or ""
                if _is_stub_answer(ans):
                    continue
                if not _topics_compatible(norm_q, qn):
                    continue
                score = _similarity(norm_q, qn)
                if score > best_score:
                    best_score = score
                    best_answer = ans

            if best_answer and best_score >= threshold:
                print(f"[CACHE HIT] fuzzy score={best_score:.2f}")
                return best_answer

    except Exception as e:
        print(f"[CACHE] lookup failed (fail-open): {e}")
    return None


def _should_store(answer: str) -> bool:
    if not answer or len(answer.strip()) < 80:
        return False
    low = _normalize_key(answer)
    # Do not cache "not found" / clarification-only stubs
    if low.startswith("xin loi") and "khong tim thay" in low:
        return False
    if low.startswith("toi da nhan anh") and "kho xac dinh" in low:
        return False
    if "해당 정보를 찾을 수 없" in answer or "정보를 찾을 수 없" in answer:
        return False
    return True


def _is_stub_answer(answer: str) -> bool:
    if not answer:
        return True
    if "해당 정보를 찾을 수 없" in answer or "정보를 찾을 수 없" in answer:
        return True
    low = _normalize_key(answer)
    if "khong tim thay thong tin" in low or "khong tim thay" in low[:80]:
        return True
    return False


def store(question: str, answer: str, context_key: str = "") -> None:
    """Persist answer for future reuse. Fail-open."""
    if not is_enabled() or not _should_store(answer):
        return
    norm_q = _normalize_key(question)
    if len(norm_q) < 8:
        return
    ctx = (context_key or "").strip()
    eid = _entry_id(norm_q, ctx)
    now = datetime.now(timezone.utc).isoformat()
    try:
        driver = _driver()
        with driver.session() as session:
            _ensure_schema(session)
            session.run(
                """
                MERGE (c:AnswerCache {id: $id})
                SET c.question_norm = $qn,
                    c.question_raw = $qr,
                    c.answer = $answer,
                    c.context_key = $ctx,
                    c.cache_version = $ver,
                    c.created_at = coalesce(c.created_at, $now),
                    c.last_hit_at = $now,
                    c.hit_count = coalesce(c.hit_count, 0)
                """,
                id=eid,
                qn=norm_q,
                qr=(question or "")[:500],
                answer=answer,
                ctx=ctx,
                ver=cache_version(),
                now=now,
            )
            _prune_old(session)
            print(f"[CACHE STORE] id={eid[:8]} len={len(answer)}")
    except Exception as e:
        print(f"[CACHE] store failed (fail-open): {e}")


def build_context_key(entities: dict) -> str:
    """Stable key for image / entity-based lookups. Includes lang so KO/VI don't collide."""
    parts = [
        str(entities.get("lang") or "vi"),
        str(entities.get("intent") or "treatment"),
        str(entities.get("stain_id") or ""),
        str(entities.get("stain_type") or ""),
        str(entities.get("fabric_type") or ""),
    ]
    return "|".join(parts).lower()


def question_for_cache(caption: str, entities: dict, fallback: str = "") -> str:
    """Best-effort cache key text (image captions may be empty)."""
    for text in (caption, fallback):
        t = (text or "").strip()
        if len(_normalize_key(t)) >= 8:
            return t
    stain = str(entities.get("stain_type") or entities.get("stain_id") or "")
    fabric = str(entities.get("fabric_type") or "")
    synth = f"{stain} {fabric}".strip()
    if len(_normalize_key(synth)) >= 8:
        return synth
    return (fallback or caption or synth).strip()
