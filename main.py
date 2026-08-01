"""
main.py
Wash Friends Vietnam - FastAPI Chatbot Backend
"""
import os
from contextlib import asynccontextmanager
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from graphrag_engine import generate_response, close_driver
from zalo_handler import handle_zalo_webhook, get_zalo_oa_info
from facebook_handler import handle_fb_verify, handle_fb_webhook

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Wash Friends Vietnam chatbot backend starting...")
    yield
    close_driver()

app = FastAPI(title="Wash Friends Vietnam Chatbot API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

@app.get("/health")
async def health():
    checks = {}
    try:
        from graphrag_engine import _get_driver
        _get_driver().verify_connectivity()
        checks["neo4j"] = "connected"
    except Exception as e:
        checks["neo4j"] = f"error: {e}"
    for key in ["ANTHROPIC_API_KEY", "ZALO_OA_ACCESS_TOKEN", "FB_PAGE_TOKEN"]:
        checks[key] = "set" if os.environ.get(key) else "missing"
    ok = all("error" not in v and "missing" not in v for v in checks.values())
    return JSONResponse({"status": "ok" if ok else "degraded", "checks": checks})

@app.post("/webhook/zalo")
async def zalo_webhook(request: Request):
    return await handle_zalo_webhook(request)

@app.get("/zalo/info")
async def zalo_info():
    return await get_zalo_oa_info()

@app.get("/webhook/facebook", response_class=PlainTextResponse)
async def facebook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    return await handle_fb_verify(hub_mode=hub_mode, hub_challenge=hub_challenge, hub_verify_token=hub_verify_token)

@app.post("/webhook/facebook")
async def facebook_webhook(request: Request):
    return await handle_fb_webhook(request)

class AskRequest(BaseModel):
    message: str
    user_id: str = "test_user"

class AskResponse(BaseModel):
    response: str
    user_id: str

@app.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest):
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        reply = await loop.run_in_executor(pool, generate_response, body.message)
    return AskResponse(response=reply, user_id=body.user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), workers=1, reload=True)
