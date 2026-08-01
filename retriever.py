"""
Wash Friends Vietnam — RAG Retriever
ChromaDB 검색 + 컨텍스트 조립 모듈

Used by the Zalo OA webhook handler and by any other interface
that needs to answer questions using the WF knowledge base.
"""

import os
import re
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

CHROMA_DIR      = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "washfriends_kb_v3"
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")


# ─────────────────────────────────────────────
# QUERY CLASSIFIER
# ─────────────────────────────────────────────

class QueryClassifier:
    """
    Detects intent and entities in the user's question to
    enable filtered retrieval (faster, more precise).
    """

    STAIN_KEYWORDS = {
        "oil":         ["dầu", "mỡ", "son môi", "kem", "bơ", "dầu ăn", "greasy",
                        "유성", "기름", "버터", "립스틱", "크림"],
        "tannin":      ["cà phê", "trà", "rượu vang", "nước tương", "nước mắm", "cà ri",
                        "탄닌", "커피", "차", "와인", "간장", "카레"],
        "protein":     ["máu", "trứng", "sữa", "mồ hôi", "cỏ", "bùn", "chocolate",
                        "단백질", "혈액", "피", "달걀", "우유", "땀", "잔디"],
        "dye_special": ["mực", "sơn", "thuốc nhuộm", "gỉ sét", "nấm mốc",
                        "염료", "잉크", "페인트", "녹", "곰팡이"],
    }

    ITEM_KEYWORDS = {
        "ao_dai":          ["áo dài", "아오자이"],
        "shoes":           ["giày", "sneaker", "운동화", "골프화", "등산화", "구두"],
        "bags":            ["túi", "balô", "가방", "핸드백", "백팩"],
        "curtains":        ["rèm", "커튼", "màn"],
        "bedding":         ["chăn", "mền", "이불", "베개", "comforter"],
        "towels":          ["khăn", "수건", "towel"],
        "leather":         ["da", "가죽", "leather", "da lộn", "스웨이드"],
        "functional":      ["gore-tex", "고어텍스", "chống thấm", "방수"],
        "military":        ["quân phục", "군복"],
        "underwear":       ["đồ lót", "속옷", "bra", "áo lót"],
        "carpet":          ["thảm", "카펫"],
        "stroller":        ["xe đẩy", "유모차"],
        "hat":             ["mũ", "모자"],
        "scarf":           ["khăn quàng", "스카프"],
        "ironing":         ["ủi", "다림질", "steam", "hơi nước"],
    }

    OPERATIONAL_KEYWORDS = {
        "refusal":      ["từ chối", "거절", "không thể", "không nhận", "refuse"],
        "compensation": ["bồi thường", "보상", "hư hỏng", "손상", "đền bù"],
        "intake":       ["tiếp nhận", "phân loại", "접수", "sorting", "nhận đồ"],
        "tools":        ["dụng cụ", "도구", "tools", "bàn chải", "솔", "hóa chất", "세제"],
        "pricing":      ["giá", "가격", "price", "phí", "chi phí"],
    }

    def classify(self, query: str) -> dict:
        q_lower = query.lower()

        detected_stains = [
            st for st, kws in self.STAIN_KEYWORDS.items()
            if any(kw in q_lower for kw in kws)
        ]
        detected_items = [
            it for it, kws in self.ITEM_KEYWORDS.items()
            if any(kw in q_lower for kw in kws)
        ]
        detected_ops = [
            op for op, kws in self.OPERATIONAL_KEYWORDS.items()
            if any(kw in q_lower for kw in kws)
        ]

        if detected_ops:
            primary_category = detected_ops[0]
        elif detected_stains:
            primary_category = "stains"
        elif detected_items:
            primary_category = "items"
        else:
            primary_category = None

        return {
            "stains":   detected_stains,
            "items":    detected_items,
            "ops":      detected_ops,
            "category": primary_category,
        }


# ─────────────────────────────────────────────
# RETRIEVER
# ─────────────────────────────────────────────

class WFRetriever:
    """
    Main retrieval class. Call retrieve(query) to get relevant context
    assembled from ChromaDB.
    """

    def __init__(self, n_results: int = 5, score_threshold: float = 1.2):
        self.n_results       = n_results
        self.score_threshold = score_threshold
        self.classifier      = QueryClassifier()
        self._collection     = None

    def _get_collection(self):
        if self._collection is None:
            if OPENAI_API_KEY:
                ef = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=OPENAI_API_KEY,
                    model_name="text-embedding-3-small",
                )
            else:
                ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name="paraphrase-multilingual-MiniLM-L12-v2"
                )
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            self._collection = client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=ef,
            )
        return self._collection

    def retrieve(
        self,
        query: str,
        n_results: Optional[int] = None,
        filter_category: Optional[str] = None,
    ) -> list[dict]:
        col = self._get_collection()
        n   = n_results or self.n_results

        intent = self.classifier.classify(query)

        where = None
        if filter_category:
            where = {"category": filter_category}

        results = col.query(
            query_texts=[query],
            n_results=n,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            if dist > self.score_threshold:
                continue
            chunks.append({
                "text":     doc,
                "source":   meta.get("source_id", "unknown"),
                "category": meta.get("category", ""),
                "section":  meta.get("section_path", ""),
                "score":    round(dist, 4),
                "metadata": meta,
            })

        return chunks

    def build_context(self, query: str, max_chars: int = 6000) -> str:
        chunks = self.retrieve(query)

        if not chunks:
            return ""

        seen_sections = set()
        unique_chunks = []
        for c in chunks:
            section_key = c["section"][:80]
            if section_key not in seen_sections:
                seen_sections.add(section_key)
                unique_chunks.append(c)

        context_parts = []
        total = 0
        for i, c in enumerate(unique_chunks, 1):
            header  = f"── Nguồn {i}: [{c['source']}] {c['section']} (độ liên quan: {c['score']}) ──"
            block   = f"{header}\n{c['text']}\n"
            if total + len(block) > max_chars:
                break
            context_parts.append(block)
            total += len(block)

        return "\n".join(context_parts)
