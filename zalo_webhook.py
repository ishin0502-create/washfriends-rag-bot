"""
Wash Friends Vietnam — Zalo OA Webhook Handler
Zalo OA 메시지 수신 → ChromaDB RAG 검색 → Claude API 답변 → Zalo 전송

Architecture:
  [Franchise owner on Zalo] → [Zalo OA] → [This webhook] → [RAG + Claude] → [Reply]

Setup:
  1. pip install fastapi uvicorn anthropic httpx python-dotenv
  2. Copy .env.example to .env and fill in keys
  3. uvicorn zalo_webhook:app --host 0.0.0.0 --port 8000
  4. Register webhook URL in Zalo OA Developer Console:
     Webhook URL: https://your-domain.com/zalo/webhook
     Events: message (user_send_text, user_send_image)
"""

import os
import json
import hmac
import hashlib
import logging
import asyncio
from datetime import datetime
from typing import Optional

import httpx
import anthropic
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from retriever import WFRetriever

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("wf_zalo")

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")
ZALO_OA_TOKEN       = os.getenv("ZALO_OA_TOKEN")
ZALO_APP_SECRET     = os.getenv("ZALO_APP_SECRET")
ZALO_API_BASE       = "https://openapi.zalo.me/v3.0"

CLAUDE_MODEL        = "claude-sonnet-4-6"
MAX_TOKENS          = 1500
CONVERSATION_TTL    = 3600

conversation_store: dict = {}

# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên nghiệp của Wash Friends Vietnam — chuỗi giặt ủi nhượng quyền hàng đầu.

Nhiệm vụ của bạn: Hỗ trợ chủ cửa hàng nhượng quyền giải quyết các vấn đề giặt ủi trong thực tế hàng ngày.

NGUYÊN TẮC TRẢ LỜI:
1. Trả lời bằng tiếng Việt, ngắn gọn, thực tế — đây là môi trường kinh doanh bận rộn
2. Ưu tiên an toàn: nếu có rủi ro hư hỏng đồ, cảnh báo TRƯỚC, giải pháp SAU
3. Khi không chắc chắn hoặc rủi ro cao, hướng dẫn từ chối nhận đồ thay vì làm sai
4. Luôn đề cập lực tay (cấp 1-5), thời gian, và dấu hiệu thành công khi hướng dẫn kỹ thuật
5. TUYỆT ĐỐI KHÔNG đề cập nguồn thông tin, sách, tài liệu hay tổ chức nào — mọi kiến thức là kinh nghiệm thực tế của Wash Friends tích lũy qua hơn 10 năm hoạt động

GIỚI HẠN:
- Chỉ trả lời về giặt ủi, chăm sóc quần áo, và vận hành cửa hàng giặt ủi
- Câu hỏi ngoài phạm vi: "Xin lỗi, tôi chỉ hỗ trợ về giặt ủi và vận hành cửa hàng Wash Friends."

ĐỊNH DẠNG:
- Tin nhắn Zalo: KHÔNG dùng markdown (no **, no #) — dùng chữ thường, xuống dòng cho dễ đọc trên điện thoại
- Các bước: dùng số (1. 2. 3.) không dùng dấu gạch đầu dòng
- Tối đa 400 từ mỗi câu trả lời — nếu dài hơn, hỏi khách có muốn nghe thêm không
- Emoji hạn chế: chỉ dùng ✅ ⚠️ ❌ khi cần nhấn mạnh

KIẾN THỨC NỀN:
{context}"""

# ─────────────────────────────────────────────
# ZALO API CLIENT
# ─────────────────────────────────────────────

async def zalo_send_text(user_id: str, text: str) -> bool:
    url     = f"{ZALO_API_BASE}/oa/message/cs"
    headers = {
        "access_token": ZALO_OA_TOKEN,
        "Content-Type": "application/json",
    }
    payload = {
        "recipient": {"user_id": user_id},
        "message":   {"text": text},
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, headers=headers, json=payload)
            data = resp.json()
            if data.get("error") == 0:
                return True
            else:
                logger.error(f"Zalo send failed: {data}")
                return False
    except Exception as e:
        logger.error(f"Zalo send exception: {e}")
        return False


async def zalo_send_typing(user_id: str):
    url     = f"{ZALO_API_BASE}/oa/message/cs"
    headers = {"access_token": ZALO_OA_TOKEN, "Content-Type": "application/json"}
    payload = {
        "recipient": {"user_id": user_id},
        "sender_action": "typing_on",
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(url, headers=headers, json=payload)
    except Exception:
        pass


# ─────────────────────────────────────────────
# CONVERSATION MANAGER
# ─────────────────────────────────────────────

def get_history(user_id: str) -> list:
    now = datetime.utcnow().timestamp()
    entry = conversation_store.get(user_id)

    if not entry:
        return []

    if now - entry["last_active"] > CONVERSATION_TTL:
        del conversation_store[user_id]
        logger.info(f"Expired conversation for {user_id}")
        return []

    return entry["history"][-20:]


def save_history(user_id: str, history: list):
    conversation_store[user_id] = {
        "history":     history,
        "last_active": datetime.utcnow().timestamp(),
    }


def reset_history(user_id: str):
    if user_id in conversation_store:
        del conversation_store[user_id]


# ─────────────────────────────────────────────
# RAG + CLAUDE PIPELINE
# ─────────────────────────────────────────────

retriever = WFRetriever(n_results=5, score_threshold=1.3)
claude    = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


async def generate_answer(user_id: str, user_message: str) -> str:
    context = await asyncio.get_event_loop().run_in_executor(
        None, retriever.build_context, user_message
    )

    if not context:
        context = "(Không tìm thấy kiến thức liên quan — trả lời từ kiến thức chung về giặt ủi)"

    history = get_history(user_id)
    messages = history + [{"role": "user", "content": user_message}]

    system = SYSTEM_PROMPT.format(context=context)

    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: claude.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                messages=messages,
            )
        )
        answer = response.content[0].text

        history.append({"role": "user",      "content": user_message})
        history.append({"role": "assistant", "content": answer})
        save_history(user_id, history)

        logger.info(f"[{user_id[:8]}] Q: {user_message[:60]}… → {len(answer)} chars")
        return answer

    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return "Xin lỗi, hệ thống tạm thời gặp sự cố. Vui lòng thử lại sau ít phút."


# ─────────────────────────────────────────────
# WEBHOOK SIGNATURE VERIFICATION
# ─────────────────────────────────────────────

def verify_zalo_signature(raw_body: bytes, mac_header: str) -> bool:
    if not ZALO_APP_SECRET:
        logger.warning("ZALO_APP_SECRET not set — skipping signature verification")
        return True

    expected = hmac.new(
        ZALO_APP_SECRET.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    received = mac_header.replace("sha256=", "")
    return hmac.compare_digest(expected, received)


# ─────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────

app = FastAPI(title="WF Zalo OA Bot", version="3.0")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "kb_collection": "washfriends_kb_v3",
        "model": CLAUDE_MODEL,
        "active_conversations": len(conversation_store),
    }


@app.post("/zalo/webhook")
async def zalo_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_body = await request.body()

    sig_header = request.headers.get("X-ZaloOA-Signature", "")
    if sig_header and not verify_zalo_signature(raw_body, sig_header):
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_name = payload.get("event_name", "")
    logger.info(f"Zalo event: {event_name}")

    if event_name == "user_send_text":
        background_tasks.add_task(handle_user_message, payload)

    return JSONResponse({"error": 0})


async def handle_user_message(payload: dict):
    try:
        sender   = payload.get("sender", {})
        message  = payload.get("message", {})
        user_id  = sender.get("id", "")
        text     = message.get("text", "").strip()

        if not user_id or not text:
            return

        logger.info(f"Message from {user_id}: {text[:80]}")

        if text.lower() in ["/reset", "/xóa", "/xoa", "reset", "bắt đầu lại"]:
            reset_history(user_id)
            await zalo_send_text(user_id, "✅ Đã xóa lịch sử trò chuyện. Bạn có thể bắt đầu câu hỏi mới.")
            return

        if text.lower() in ["/help", "/giúp", "help"]:
            help_text = (
                "Xin chào! Tôi là trợ lý AI của Wash Friends.\n\n"
                "Tôi có thể giúp bạn:\n"
                "1. Xử lý vết bẩn (dầu, cà phê, máu, mực...)\n"
                "2. Giặt đồ theo loại (áo dài, giày, thảm, rèm...)\n"
                "3. Dụng cụ & hóa chất cần dùng\n"
                "4. Quy trình tiếp nhận & từ chối đồ\n"
                "5. Xử lý bồi thường & khiếu nại\n\n"
                "Hãy đặt câu hỏi trực tiếp, ví dụ:\n"
                '"Có vết son môi trên áo lụa trắng, làm sao?"'
            )
            await zalo_send_text(user_id, help_text)
            return

        await zalo_send_typing(user_id)

        answer = await generate_answer(user_id, text)

        if len(answer) > 1900:
            parts = split_message(answer, 1900)
            for part in parts:
                await zalo_send_text(user_id, part)
                await asyncio.sleep(0.5)
        else:
            await zalo_send_text(user_id, answer)

    except Exception as e:
        logger.error(f"handle_user_message error: {e}", exc_info=True)
        try:
            await zalo_send_text(
                user_id,
                "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ WF Support."
            )
        except Exception:
            pass


def split_message(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]

    parts = []
    while len(text) > max_len:
        cut = text.rfind("\n", 0, max_len)
        if cut == -1:
            cut = text.rfind(". ", 0, max_len)
        if cut == -1:
            cut = max_len
        parts.append(text[:cut].strip())
        text = text[cut:].strip()

    if text:
        parts.append(text)
    return parts


# ─────────────────────────────────────────────
# DEVELOPMENT: CLI TEST MODE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import asyncio

    async def cli_test():
        print("=" * 60)
        print("  WF Zalo Bot — CLI Test Mode")
        print("  Type your question (or 'quit' to exit)")
        print("=" * 60)
        test_user = "cli_test_user"

        while True:
            try:
                q = input("\n❓ Bạn: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if q.lower() in ["quit", "exit", "q"]:
                break
            if not q:
                continue

            print("🤔 Đang xử lý...")
            answer = await generate_answer(test_user, q)
            print(f"\n🤖 WF Bot:\n{answer}")

    asyncio.run(cli_test())
