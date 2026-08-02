"""
main.py
Wash Friends Vietnam — FastAPI Chatbot Backend

Endpoints:
  GET  /health                 — health check + Neo4j connectivity
  POST /webhook/zalo           — Zalo OA webhook receiver
  POST /webhook/facebook       — Facebook Messenger webhook receiver
  GET  /webhook/facebook       — Facebook webhook verification
  POST /ask                    — Direct API for testing (no platform auth needed)

Start:
  uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

Environment variables required:
  NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
  ANTHROPIC_API_KEY
  ZALO_OA_ACCESS_TOKEN, ZALO_APP_SECRET
  FB_PAGE_TOKEN, FB_VERIFY_TOKEN, FB_APP_SECRET
"""

import os
from contextlib import asynccontextmanager

# Load .env for local development (no-op in Railway/Render where vars are set directly)
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


# ─── App lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    print("🚀 Wash Friends Vietnam chatbot backend starting...")
    yield
    print("🛑 Shutting down — closing Neo4j driver...")
    close_driver()


app = FastAPI(
    title="Wash Friends Vietnam Chatbot API",
    description="Neo4j GraphRAG + Claude AI for Vietnamese laundry shop franchise owners",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to Zalo/FB IPs in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/zalo_verifierKC6ODPNWCGyMvA0nySeN5YF3jXVFjMDEE3Wt.html")
async def zalo_domain_verify():
    """Zalo domain verification file."""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
    <meta property="zalo-platform-site-verification" content="KC6ODPNWCGyMvA0nySeN5YF3jXVFjMDEE3Wt" />
</head>
<body>
There Is No Limit To What You Can Accomplish Using Zalo!
</body>
</html>""")


@app.get("/health")
async def health():
    """Health check — verifies Neo4j connection and env vars."""
    checks = {}

    # Neo4j connectivity
    try:
        from graphrag_engine import _get_driver
        driver = _get_driver()
        driver.verify_connectivity()
        checks["neo4j"] = "✅ connected"
    except Exception as e:
        checks["neo4j"] = f"❌ {e}"

    # Env var presence (not values)
    for key in ["ANTHROPIC_API_KEY", "ZALO_OA_ACCESS_TOKEN", "FB_PAGE_TOKEN"]:
        checks[key] = "✅ set" if os.environ.get(key) else "⚠️ missing"

    all_ok = all("✅" in v for v in checks.values())
    return JSONResponse(
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
        status_code=200,
    )


# ─── Zalo webhook ─────────────────────────────────────────────────────────────

@app.post("/webhook/zalo")
async def zalo_webhook(request: Request):
    return await handle_zalo_webhook(request)


@app.get("/zalo/info")
async def zalo_info():
    """Dev tool — verify Zalo OA token is valid."""
    return await get_zalo_oa_info()


# ─── Facebook webhook ─────────────────────────────────────────────────────────

@app.get("/webhook/facebook", response_class=PlainTextResponse)
async def facebook_verify(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    return await handle_fb_verify(
        hub_mode=hub_mode,
        hub_challenge=hub_challenge,
        hub_verify_token=hub_verify_token,
    )


@app.post("/webhook/facebook")
async def facebook_webhook(request: Request):
    return await handle_fb_webhook(request)


# ─── Direct test API ──────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    message: str
    user_id: str = "test_user"

class AskResponse(BaseModel):
    response: str
    user_id: str

@app.post("/ask", response_model=AskResponse)
async def ask(body: AskRequest):
    """
    Direct test endpoint — bypasses Zalo/FB auth.
    curl -X POST /ask -H 'Content-Type: application/json' \\
         -d '{"message": "Vết cà phê trên lục thì xử lý thế nào?"}'
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        reply = await loop.run_in_executor(pool, generate_response, body.message)

    return AskResponse(response=reply, user_id=body.user_id)


# ─── Dev runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=1,
        reload=True,  # Dev only — remove in production
    )
