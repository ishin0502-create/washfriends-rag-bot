"""
Wash Friends Vietnam — RAG Knowledge Base Ingestor
지식베이스 → ChromaDB 벡터 DB 로더

Usage:
    pip install chromadb anthropic python-dotenv tiktoken
    python ingest.py

This script:
1. Reads all v3.0 knowledge base MD files
2. Splits them into smart chunks (by protocol section)
3. Embeds with Anthropic's embedding model (or OpenAI if preferred)
4. Stores in ChromaDB with rich metadata for precise retrieval
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

KB_DIR = Path(__file__).parent / "kb"  # kb/ subdirectory in the repo
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "washfriends_kb_v3"

# Embedding: using OpenAI (widely supported) — swap to Anthropic if preferred
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Knowledge base files (ordered by priority for retrieval)
KB_FILES = [
    # Layer 1: Core operational protocols
    ("tools_equipment",    KB_DIR / "laundry_kb_v3_tools_equipment.md",    "intake_tools"),
    ("stains_oil",         KB_DIR / "laundry_kb_v3_stains_oil.md",         "stains"),
    ("stains_tannin",      KB_DIR / "laundry_kb_v3_stains_tannin.md",      "stains"),
    ("stains_protein",     KB_DIR / "laundry_kb_v3_stains_protein.md",     "stains"),
    ("stains_special",     KB_DIR / "laundry_kb_v3_stains_special.md",     "stains"),
    ("stains_dye",         KB_DIR / "laundry_kb_v3_stains_dye.md",         "stains"),
    ("prototype",          KB_DIR / "laundry_kb_v3_prototype.md",           "stains"),
    # Layer 2: Item-type protocols
    ("items_clothing",     KB_DIR / "laundry_kb_v3_items_clothing.md",     "items"),
    ("items_home",         KB_DIR / "laundry_kb_v3_items_home.md",         "items"),
    ("items_ironing",      KB_DIR / "laundry_kb_v3_items_ironing.md",      "items"),
    ("items_business",     KB_DIR / "laundry_kb_v3_items_business.md",     "business"),
    # Layer 3: Context & localization + advanced field cases
    ("localization",       KB_DIR / "laundry_kb_v3_localization.md",       "context"),
    ("protocol_framework", KB_DIR / "laundry_kb_v3_protocol.md",           "context"),
    ("advanced_field",     KB_DIR / "laundry_kb_v3_advanced_field.md",     "context"),
    ("ops_gold",           KB_DIR / "laundry_kb_v3_ops_gold.md",           "context"),
    ("wf_products",        KB_DIR / "laundry_kb_v3_wf_products.md",        "context"),
]

# Chunking settings
MAX_CHUNK_TOKENS = 800    # ~600 words — fits well in retrieval context
OVERLAP_TOKENS   = 80     # overlap between chunks for continuity


# ─────────────────────────────────────────────
# SMART CHUNKER
# ─────────────────────────────────────────────

class SmartChunker:
    """
    Splits markdown by protocol sections, not arbitrary token windows.
    Priority: H1 > H2 > H3 > paragraph blocks
    Each chunk retains a breadcrumb header for context.
    """

    # Section markers found in WF knowledge base
    PROTOCOL_DELIMITERS = [
        r"^#{1,2} [═─]+",          # ═══ dividers
        r"^# PROTOCOL",            # explicit protocol headers
        r"^## [A-Z\-]+\-\d+",      # e.g. ## HT-1.02, ## S1.1
        r"^### ▶ BƯỚC \d+",        # step headers
        r"^## PART \d+",           # part dividers
    ]

    def __init__(self, max_tokens: int = MAX_CHUNK_TOKENS, overlap: int = OVERLAP_TOKENS):
        self.max_tokens = max_tokens
        self.overlap = overlap
        self._delimiter_re = re.compile(
            "|".join(self.PROTOCOL_DELIMITERS), re.MULTILINE
        )

    def estimate_tokens(self, text: str) -> int:
        # Rough estimate: 1 token ≈ 4 chars (works for mixed VN/KR/EN)
        return len(text) // 4

    def split(self, text: str, source_name: str) -> list[dict]:
        """Returns list of {text, section_path, chunk_index}"""
        lines = text.split("\n")
        chunks = []
        current_lines = []
        current_h1 = ""
        current_h2 = ""
        current_h3 = ""
        chunk_idx = 0

        def flush(lines_buf, force=False):
            nonlocal chunk_idx
            content = "\n".join(lines_buf).strip()
            if not content or (self.estimate_tokens(content) < 30 and not force):
                return
            breadcrumb_parts = [p for p in [current_h1, current_h2, current_h3] if p]
            breadcrumb = " > ".join(breadcrumb_parts)
            full_text = f"[{source_name}] {breadcrumb}\n\n{content}" if breadcrumb else content
            chunks.append({
                "text": full_text,
                "section_path": breadcrumb,
                "chunk_index": chunk_idx,
            })
            chunk_idx += 1

        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                if current_lines:
                    flush(current_lines)
                    current_lines = []
                current_h1 = line.lstrip("# ").strip()
                current_h2 = ""
                current_h3 = ""
                current_lines = [line]
            elif line.startswith("## "):
                if self.estimate_tokens("\n".join(current_lines)) > self.max_tokens * 0.7:
                    flush(current_lines)
                    current_lines = []
                current_h2 = line.lstrip("# ").strip()
                current_h3 = ""
                current_lines.append(line)
            elif line.startswith("### "):
                if self.estimate_tokens("\n".join(current_lines)) > self.max_tokens:
                    flush(current_lines)
                    overlap_lines = current_lines[-self.overlap // 4:] if current_lines else []
                    current_lines = overlap_lines
                current_h3 = line.lstrip("# ").strip()
                current_lines.append(line)
            else:
                current_lines.append(line)
                if self.estimate_tokens("\n".join(current_lines)) > self.max_tokens:
                    flush(current_lines)
                    overlap_lines = current_lines[-self.overlap // 4:]
                    current_lines = overlap_lines

        if current_lines:
            flush(current_lines, force=True)

        return chunks


# ─────────────────────────────────────────────
# METADATA EXTRACTOR
# ─────────────────────────────────────────────

def extract_metadata(chunk_text: str, source_id: str, category: str) -> dict:
    """
    Extract rich metadata from chunk content for filtered retrieval.
    ChromaDB metadata values must be str, int, float, or bool.
    """
    text_lower = chunk_text.lower()

    stain_types = []
    if any(w in text_lower for w in ["dầu", "mỡ", "oil", "grease", "유성"]):
        stain_types.append("oil")
    if any(w in text_lower for w in ["tannin", "cà phê", "coffee", "trà", "탄닌"]):
        stain_types.append("tannin")
    if any(w in text_lower for w in ["protein", "máu", "blood", "trứng", "단백질"]):
        stain_types.append("protein")
    if any(w in text_lower for w in ["mực", "ink", "sơn", "paint", "염료"]):
        stain_types.append("dye_special")

    item_types = []
    if any(w in text_lower for w in ["áo dài", "아오자이"]):
        item_types.append("ao_dai")
    if any(w in text_lower for w in ["giày", "운동화", "shoe", "sneaker"]):
        item_types.append("shoes")
    if any(w in text_lower for w in ["túi", "가방", "bag"]):
        item_types.append("bags")
    if any(w in text_lower for w in ["rèm", "커튼", "curtain"]):
        item_types.append("curtains")
    if any(w in text_lower for w in ["chăn", "이불", "comforter", "bedding"]):
        item_types.append("bedding")
    if any(w in text_lower for w in ["da", "가죽", "leather"]):
        item_types.append("leather")
    if any(w in text_lower for w in ["gore-tex", "기능성", "functional"]):
        item_types.append("functional_fabric")

    chem_codes = re.findall(r'\b([DEBA][1-5]|S1|N[1-3])\b', chunk_text)
    unique_chems = list(dict.fromkeys(chem_codes))[:10]

    has_danger = any(w in chunk_text for w in ["☠️", "🔥", "TUYỆT ĐỐI KHÔNG", "절대 금지", "❌"])
    has_refusal = any(w in text_lower for w in ["từ chối", "거절", "refuse", "không thể xử lý"])

    stars_match = re.search(r'(★+)', chunk_text)
    difficulty = len(stars_match.group(1)) if stars_match else 0

    has_vietnamese = bool(re.search(r'[àáạảãăắặẳẵâấậẩẫèéẹẻẽêếệểễìíịỉĩòóọỏõôốộổỗơớợởỡùúụủũưứựửữỳýỵỷỹđ]', chunk_text))
    has_korean = bool(re.search(r'[가-힣]', chunk_text))

    return {
        "source_id":       source_id,
        "category":        category,
        "stain_types":     ",".join(stain_types) if stain_types else "",
        "item_types":      ",".join(item_types) if item_types else "",
        "chemicals":       ",".join(unique_chems) if unique_chems else "",
        "has_danger":      has_danger,
        "has_refusal":     has_refusal,
        "difficulty":      difficulty,
        "has_vietnamese":  has_vietnamese,
        "has_korean":      has_korean,
        "char_count":      len(chunk_text),
    }


# ─────────────────────────────────────────────
# EMBEDDING FUNCTION
# ─────────────────────────────────────────────

def get_embedding_function():
    if OPENAI_API_KEY:
        print("Using OpenAI text-embedding-3-small")
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model_name="text-embedding-3-small",
        )
    else:
        print("No OPENAI_API_KEY found - using local SentenceTransformer")
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )


# ─────────────────────────────────────────────
# MAIN INGEST PIPELINE
# ─────────────────────────────────────────────

def chunk_id(source_id: str, chunk_index: int, text: str) -> str:
    content_hash = hashlib.md5(text[:200].encode()).hexdigest()[:8]
    return f"{source_id}_{chunk_index:04d}_{content_hash}"


def ingest_all(reset: bool = False):
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = get_embedding_function()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={
            "description": "Wash Friends Vietnam v3.0 Knowledge Base",
            "version": "3.0",
            "language": "vi,ko,en",
        }
    )

    chunker = SmartChunker()
    total_chunks = 0

    print(f"\n{'='*60}")
    print(f"  Wash Friends KB Ingestor v3.0")
    print(f"  Target: {COLLECTION_NAME}")
    print(f"{'='*60}\n")

    for source_id, filepath, category in KB_FILES:
        if not filepath.exists():
            print(f"MISSING: {filepath.name} - skipping")
            continue

        text = filepath.read_text(encoding="utf-8")
        chunks = chunker.split(text, source_id)
        print(f"{filepath.name}: {len(chunks)} chunks")

        batch_ids   = []
        batch_docs  = []
        batch_metas = []

        for chunk in chunks:
            cid  = chunk_id(source_id, chunk["chunk_index"], chunk["text"])
            meta = extract_metadata(chunk["text"], source_id, category)
            meta["section_path"] = chunk["section_path"][:500]

            batch_ids.append(cid)
            batch_docs.append(chunk["text"])
            batch_metas.append(meta)

            if len(batch_ids) >= 100:
                collection.upsert(ids=batch_ids, documents=batch_docs, metadatas=batch_metas)
                total_chunks += len(batch_ids)
                batch_ids, batch_docs, batch_metas = [], [], []

        if batch_ids:
            collection.upsert(ids=batch_ids, documents=batch_docs, metadatas=batch_metas)
            total_chunks += len(batch_ids)

    print(f"\n{'='*60}")
    print(f"Ingestion complete!")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Collection size: {collection.count()} documents")
    print(f"   DB location: {CHROMA_DIR}")
    print(f"{'='*60}\n")

    return collection


def test_retrieval(collection):
    test_queries = [
        "cách giặt áo dài lụa",
        "운동화 밑창 분리 방지",
        "커피 얼룩 제거 방법",
        "vết son môi trên áo trắng",
        "từ chối nhận đồ da lộn",
    ]

    print("\n── RETRIEVAL SMOKE TEST ──")
    for q in test_queries:
        results = collection.query(
            query_texts=[q],
            n_results=2,
            include=["documents", "metadatas", "distances"],
        )
        top_doc  = results["documents"][0][0][:120].replace("\n", " ")
        top_dist = results["distances"][0][0]
        print(f"\nQ: {q}")
        print(f"   [{top_dist:.3f}] {top_doc}...")
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WF KB Ingestor")
    parser.add_argument("--reset", action="store_true", help="Wipe DB and re-ingest")
    parser.add_argument("--test",  action="store_true", help="Run retrieval smoke test after ingest")
    args = parser.parse_args()

    col = ingest_all(reset=args.reset)

    if args.test:
        test_retrieval(col)
