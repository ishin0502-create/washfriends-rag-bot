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
  OPENAI_API_KEY
  ZALO_OA_ACCESS_TOKEN, ZALO_OA_REFRESH_TOKEN, ZALO_APP_SECRET, ZALO_APP_ID
  FB_PAGE_TOKEN, FB_VERIFY_TOKEN, FB_APP_SECRET
"""

import os
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

# Load .env for local development (no-op in Railway/Render where vars are set directly)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from typing import Optional

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from graphrag_engine import generate_response, close_driver
from zalo_handler import handle_zalo_webhook, get_zalo_oa_info, diagnose_zalo_brand
from facebook_handler import handle_fb_verify, handle_fb_webhook
from zalo_token import token_refresh_loop


# ─── App lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    print("🚀 Wash Friends Vietnam chatbot backend starting...")
    try:
        from brand_header import clear_all_brand_headers
        n = clear_all_brand_headers()
        print(f"[BRAND] cleared topic cache on boot ({n})")
    except Exception as e:
        print(f"[BRAND] boot clear skipped: {e}")
    stop = asyncio.Event()
    refresh_task = asyncio.create_task(token_refresh_loop(stop))
    try:
        yield
    finally:
        stop.set()
        refresh_task.cancel()
        try:
            await refresh_task
        except asyncio.CancelledError:
            pass
        print("🛑 Shutting down — closing Neo4j driver...")
        close_driver()


app = FastAPI(
    title="Wash Friends Vietnam Chatbot API",
    description="Neo4j GraphRAG + GPT-4o-mini for Vietnamese laundry shop franchise owners",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to Zalo/FB IPs in production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Brand header image only (mascot + logo) — no RAG coupling
_assets_dir = Path(__file__).resolve().parent / "assets"
if _assets_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_assets_dir)), name="static")


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

    # Env var presence (not values) — Railway healthcheck needs HTTP 200 always
    for key in ["OPENAI_API_KEY", "ZALO_OA_ACCESS_TOKEN", "FB_PAGE_TOKEN"]:
        checks[key] = "✅ set" if os.environ.get(key) else "⚠️ missing"

    neo4j_ok = "✅" in str(checks.get("neo4j", ""))
    return JSONResponse(
        content={
            "status": "ok" if neo4j_ok else "degraded",
            "build": "2026-08-06-edu-s9b-perfume-route",
            "checks": checks,
        },
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


@app.get("/admin/brand-test")
async def admin_brand_test(
    token: str = Query(...),
    user_id: Optional[str] = Query(None, description="Optional Zalo user_id to send test image"),
    reset: int = Query(0, description="1 = clear brand topic cache so next chat retries header"),
):
    """Diagnose brand header upload/send. Token: washfriends2024seed"""
    if token != "washfriends2024seed":
        return JSONResponse({"error": "unauthorized"}, status_code=403)
    return await diagnose_zalo_brand(user_id=user_id, reset=bool(reset))


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

    try:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            reply = await loop.run_in_executor(pool, generate_response, body.message)
        return AskResponse(response=reply, user_id=body.user_id)
    except Exception as e:
        # Surface error for debugging (franchise test endpoint only)
        print(f"[ASK ERROR] {type(e).__name__}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": type(e).__name__,
                "detail": str(e)[:500],
                "user_id": body.user_id,
            },
        )




# ─── Admin seed ──────────────────────────────────────────────────────────────

@app.get("/admin/seed")
async def seed_database(token: str = ""):
    """Seed Neo4j with all laundry knowledge. Token: washfriends2024seed"""
    if token != "washfriends2024seed":
        return JSONResponse({"error": "unauthorized"}, status_code=403)
    from neo4j import GraphDatabase as _GD
    _drv = _GD.driver(
        os.getenv("NEO4J_URI"),
        auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
    )
    log = {}
    def _r(s, name, cypher):
        try:
            res = s.run(cypher)
            d = res.data()
            log[name] = d[0] if d else "ok"
        except Exception as e:
            log[name] = f"ERR:{str(e)[:100]}"
    with _drv.session() as s:
        r = s.run("MATCH (n) RETURN labels(n)[0] AS l, count(n) AS c ORDER BY l")
        log["before"] = {row["l"]: row["c"] for row in r}
        _r(s, "A_groups", """
UNWIND [
  {id:'G1',name:'Protein',name_vi:'Protein',description:'Blood egg milk vomit urine - cold water + enzyme',contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:false,
   care_order_vi:'Thu tu: nuoc LANH → enzyme (neu vai cho phep) → xa ky. CAM nuoc nong dau. CAM tron enzyme+tay chlorine. Test goc truoc.',
   care_order_ko:'순서: 찬물 → 효소(원단 허용 시) → 충분히 헹굼. 처음부터 온수 금지. 효소+염소계 표백 혼합 금지. 구석 테스트.'},
  {id:'G2',name:'Oil',name_vi:'Dau mo',description:'Cooking oil butter engine oil cosmetics - absorbent then surfactant',contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false,
   care_order_vi:'Thu tu: hut bot (N3) → surfactant/dung moi (thong gio) → giat. CAM say khi con nhon. Khong pha cocktail ty le bi a.',
   care_order_ko:'순서: 흡착 가루 → 계면활성/탈지(환기) → 세탁. 기름 남은 채 건조 금지. 임의 혼합 비율 금지.'},
  {id:'G3',name:'Tannin',name_vi:'Tannin',description:'Coffee tea wine juice sauces - acid then oxidizer',contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:false,
   care_order_vi:'Thu tu: xu ly SOM + lanh → acid nhe (A3 neu vai cho) → xa → oxy bleach neu con mau (khong len/lua). Test goc.',
   care_order_ko:'순서: 빨리·찬물 → 약한 산(원단 허용 시) → 헹굼 → 남은 색만 산소계(실크·울 금지). 구석 테스트.'},
  {id:'G4',name:'Dye',name_vi:'Thuoc nhuom',description:'Curry turmeric mustard ink - UV and/or solvent',contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,
   care_order_vi:'Thu tu: test phai mau → dung moi/cham mat trai → giat. CAM cha lan. CAM say khi con mau (nhiet khoa mau).',
   care_order_ko:'순서: 이염 테스트 → 용제·뒷면 찍기 → 세탁. 문질러 번지게 금지. 색 남은 채 건조·열 금지.'},
  {id:'G5',name:'Complex',name_vi:'Phuc hop',description:'Fish sauce BBQ sweat - multiple components',contains_protein:true,contains_tannin:true,contains_oil:true,contains_dye:false,
   care_order_vi:'Vet phuc hop: XU LY TUNG THANH PHAN theo fresh_path, XA giua buoc. CAM do chung A+B+C ty le 2:1:1. CAM tron never_mix.',
   care_order_ko:'복합 얼룩: fresh_path대로 성분별 순차 처리, 단계마다 헹굼. A+B+C 2:1:1 혼합 금지. never_mix 절대 준수.'}
] AS g MERGE (n:StainGroup {id:g.id}) SET n += g RETURN count(n) AS created""")
        _r(s, "B_forces", """
UNWIND [
  {level:1,name:'Baby Face',description:'Ultra-gentle - silk lace voile'},
  {level:2,name:'Cleaning Glasses',description:'Gentle - wool cashmere rayon'},
  {level:3,name:'Wiping Table',description:'Medium - thin cotton polyester blend'},
  {level:4,name:'Scrubbing',description:'Strong - thick cotton denim linen'}
] AS f MERGE (n:ForceLevel {level:f.level}) SET n += f RETURN count(n) AS created""")
        _r(s, "C_climate", """
UNWIND [
  {id:'CR1',region:'Vietnam-All',rule:'Cold water for protein - VN summer tap 28-32C near enzyme optimum'},
  {id:'CR2',region:'Vietnam-Hanoi-Winter',rule:'North winter water 15-18C - double enzyme soak time'},
  {id:'CR3',region:'Vietnam-Rainy',rule:'Mud season May-Nov: let mud DRY before brushing'},
  {id:'CR4',region:'Vietnam-All',rule:'High humidity 75-95% - protein stains ferment quickly treat within 2h'},
  {id:'CR5',region:'Vietnam-Central-South',rule:'Laterite red soil: dry first brush then vinegar then oxygen bleach - iron oxide stubborn'},
  {id:'CR6',region:'Vietnam-Urban',rule:'Motorbike oil common: absorbent powder twice then solvent degreaser with ventilation'}
] AS c MERGE (n:ClimateRule {id:c.id}) SET n += c RETURN count(n) AS created""")
        _r(s, "D_fabrics", """
UNWIND [
  {id:'F1',name:'Cotton',name_vi:'Vai cotton',max_temp:60,can_bleach:true,enzyme_safe:true,acid_safe:true},
  {id:'F2',name:'Polyester',name_vi:'Vai polyester',max_temp:40,can_bleach:false,enzyme_safe:true,acid_safe:true},
  {id:'F3',name:'Wool',name_vi:'Vai len',max_temp:30,can_bleach:false,enzyme_safe:false,acid_safe:false},
  {id:'F4',name:'Silk',name_vi:'Vai lua',max_temp:30,can_bleach:false,enzyme_safe:false,acid_safe:false},
  {id:'F5',name:'Linen',name_vi:'Vai linen',max_temp:40,can_bleach:false,enzyme_safe:true,acid_safe:true},
  {id:'F6',name:'Denim',name_vi:'Vai denim',max_temp:40,can_bleach:false,enzyme_safe:true,acid_safe:true},
  {id:'F7',name:'Rayon',name_vi:'Vai rayon',max_temp:30,can_bleach:false,enzyme_safe:false,acid_safe:false},
  {id:'F8',name:'Leather',name_vi:'Da (da bong)',max_temp:30,can_bleach:false,enzyme_safe:false,acid_safe:false},
  {id:'F9',name:'Suede',name_vi:'Da lon / suede / nubuck',max_temp:30,can_bleach:false,enzyme_safe:false,acid_safe:false},
  {id:'F10',name:'Fur',name_vi:'Long thu that (fur)',max_temp:20,can_bleach:false,enzyme_safe:false,acid_safe:false}
] AS f MERGE (n:Fabric {id:f.id}) SET n += f RETURN count(n) AS created""")
        _r(s, "E_chemicals", """
UNWIND [
  {code:'E1',name:'Protease Enzyme',name_vi:'Enzyme protease',role:'Breaks protein chains',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Nuoc giat co enzyme / bot ngam enzyme',buy_where_vi:'Sieu thi',alt1_vi:'Ngam nuoc giat enzyme',alt2_vi:'Khong dung len/lua — chuyen S1',alt3_vi:'',example_brands_vi:'Nuoc giat ghi enzyme tren nhan',wf_supply:false,when_use_vi:''},
  {code:'E2',name:'Amylase Enzyme',name_vi:'Enzyme amylase',role:'Breaks starch',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Nuoc giat enzyme (tinh bot)',buy_where_vi:'Sieu thi',alt1_vi:'E1 combo neu co',alt2_vi:'',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'E3',name:'Lipase Enzyme',name_vi:'Enzyme lipase',role:'Breaks fat/oil',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Nuoc giat enzyme (dau mo)',buy_where_vi:'Sieu thi',alt1_vi:'D2 + E1',alt2_vi:'',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'D1',name:'Solvent Degreaser',name_vi:'Dung moi tay dau',role:'Dissolves heavy oil - use with ventilation',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Dung moi tay dau / tay nhot',buy_where_vi:'Cua o to, cua hoa chat — THONG GIO',alt1_vi:'D2 dac + kien nhan',alt2_vi:'San pham tay dau xe may',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'D2',name:'Dish Soap',name_vi:'Nuoc rua chen',role:'Mild surfactant safe for most fabrics',safe_on_wool:true,safe_on_silk:true,shop_name_vi:'Nuoc rua chen',buy_where_vi:'Sieu thi',alt1_vi:'Nuoc rua chen dam dac',alt2_vi:'',alt3_vi:'',example_brands_vi:'Sunlight, Mama, My Hao (vi du)',wf_supply:false,when_use_vi:''},
  {code:'D3',name:'Strong Detergent',name_vi:'Bot giat manh',role:'Heavy-duty washing detergent',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Nuoc giat / bot giat dam',buy_where_vi:'Sieu thi',alt1_vi:'Nuoc giat liquid dam',alt2_vi:'',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'B1',name:'Oxygen Bleach',name_vi:'Tay oxy',role:'Color-safe bleach',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Bot tay oxy / tay mau an toan',buy_where_vi:'Sieu thi ke giat',alt1_vi:'Bot tay vai mau',alt2_vi:'Khong dung len/lua',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'B2',name:'Chlorine Bleach',name_vi:'Javel',role:'Strong bleach WHITE cotton ONLY',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Nuoc Javel / nuoc tay trang',buy_where_vi:'Sieu thi',alt1_vi:'CHI cotton trang',alt2_vi:'Khong mau/len/lua',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'A1',name:'Isopropyl Alcohol',name_vi:'Con isopropyl',role:'Dissolves pigments ink polish curcumin',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Con sat khuan / con y te 70-90%',buy_where_vi:'Nha thuoc, sieu thi',alt1_vi:'Alcohol sat trung 70%',alt2_vi:'Nuoc tay trang co con (test goc khuat)',alt3_vi:'Chat tay muc chuyen dung',example_brands_vi:'Con y te 70% / 90% (vi du)',wf_supply:false,when_use_vi:''},
  {code:'A2',name:'Acetone',name_vi:'Acetone',role:'Strong solvent for polymer stains gum nail polish',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Acetone / dung moi son mong',buy_where_vi:'Nha thuoc, cua hoa chat',alt1_vi:'Nuoc tay son mong khong dau',alt2_vi:'A1 neu vet nhe',alt3_vi:'Mang do chuyen sau',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'A3',name:'White Vinegar 5%',name_vi:'Giam trang 5%',role:'Mild acid breaks tannin bonds neutralizes alkali odor',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Giam trang nau an / giam tinh',buy_where_vi:'Sieu thi',alt1_vi:'Giam an pha loang',alt2_vi:'Nuoc cot chanh pha (test mau)',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'A4',name:'Hydrogen Peroxide 3%',name_vi:'Hydrogen peroxide 3%',role:'Light oxidizer for white fabrics',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Oxy gia 3% / hydrogen peroxide',buy_where_vi:'Nha thuoc',alt1_vi:'Oxy gia 3% pharmacy',alt2_vi:'B1 nhe tren trang',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'A5',name:'Diluted Ammonia',name_vi:'Ammonia pha loang',role:'Mild alkali for old protein - NEVER mix with bleach',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Nuoc ammonia / amoniac pha',buy_where_vi:'Cua hoa chat',alt1_vi:'KHONG tron B2',alt2_vi:'E1 cho protein cu neu an toan vai',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'N1',name:'Baking Soda',name_vi:'Baking soda',role:'Mild abrasive odor absorber alkaline for curcumin',safe_on_wool:true,safe_on_silk:false,shop_name_vi:'Bot baking soda / muoi no',buy_where_vi:'Sieu thi, bakery',alt1_vi:'',alt2_vi:'',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'N2',name:'Table Salt',name_vi:'Muoi an',role:'Draws out fresh blood and tannin',safe_on_wool:true,safe_on_silk:true,shop_name_vi:'Muoi tinh',buy_where_vi:'Sieu thi',alt1_vi:'',alt2_vi:'',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'N3',name:'Corn Starch/Talc',name_vi:'Bot ngo/bot talc',role:'Oil absorber first step for all oil stains',safe_on_wool:true,safe_on_silk:true,shop_name_vi:'Bot bap / phan rom / bot nang',buy_where_vi:'Sieu thi',alt1_vi:'Phan em be (khong dau)',alt2_vi:'',alt3_vi:'',example_brands_vi:'',wf_supply:false,when_use_vi:''},
  {code:'S1',name:'Wash Friends Neutral Detergent',name_vi:'Nuoc giat trung tinh Wash Friends',role:'WF supply pH-neutral for silk wool delicate',safe_on_wool:true,safe_on_silk:true,shop_name_vi:'Nuoc giat trung tinh do Wash Friends cung cap',buy_where_vi:'Kho hang / cung ung Wash Friends',alt1_vi:'Wool shampoo neu het hang WF',alt2_vi:'Giat tay nuoc lanh rat nhe',alt3_vi:'Khong dung enzyme',example_brands_vi:'Wash Friends supply',wf_supply:true,when_use_vi:'Bat buoc uu tien khi can chat giat trung tinh / lua / len'},
  {code:'WF_SOFT',name:'Wash Friends Softener',name_vi:'Nuoc xa Softener Wash Friends',role:'WF fabric softener - popular fragrance',safe_on_wool:true,safe_on_silk:true,shop_name_vi:'Nuoc xa / lam mem vai Wash Friends',buy_where_vi:'Kho hang Wash Friends',alt1_vi:'Giam lieu neu khach ghet huong dam',alt2_vi:'Bo qua neu khach yeu cau khong xa',alt3_vi:'',example_brands_vi:'Wash Friends supply',wf_supply:true,when_use_vi:'Chi khi hoan thien / xa vai — khong nhac moi cau vet ban'},
  {code:'WF_FRAG',name:'Wash Friends German Fragrance Spray',name_vi:'Xit huong Duc Wash Friends',role:'Premium fragrance spray after dry or before dry',safe_on_wool:true,safe_on_silk:true,shop_name_vi:'Xit huong (Duc) Wash Friends',buy_where_vi:'Kho hang Wash Friends',alt1_vi:'Xit nhe — dung qua nhieu',alt2_vi:'',alt3_vi:'',example_brands_vi:'Wash Friends supply',wf_supply:true,when_use_vi:'CHI: do cao cap / sau ui / khach ghet mui giat kho — xit nhe. Khong nhac neu chi hoi xu ly vet ban'}
] AS c MERGE (n:Chemical {code:c.code}) SET n += c RETURN count(n) AS created""")
        # Stage2 additive: specialty chems from ops_gold / advanced_field — does NOT alter existing chem rows
        _r(s, "E2_specialty_chems_x1_x2", """
UNWIND [
  {code:'X1',name:'Reducing Bleach (sodium hydrosulfite)',name_vi:'Tay khu X1 (sodium hydrosulfite)',name_ko:'환원 표백제(하이드로설파이트계)',role:'Severe white yellowing when oxygen fails — WHITE cotton/linen ONLY',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Bot tay khu / sodium hydrosulfite (hoa chat)',buy_where_vi:'Cua hoa chat chuyen dung — gang tay, pha moi',buy_where_ko:'화공점(전문) — 장갑 필수, 즉석 조제',alt1_vi:'Chi khi B1 that bai tren cotton/linen TRANG',alt2_vi:'CAM do mau / len / lua / da',alt3_vi:'Xa lanh ngay sau xu ly',alt1_ko:'산소표백 실패 후 흰 면·린넨만',alt2_ko:'유색·실크·울·가죽 금지',alt3_ko:'처리 후 즉시 찬물 헹굼',example_brands_vi:'',wf_supply:false,when_use_vi:'Vang o NANG khong het voi B1 — cotton/linen trang. Pha moi 40-50C, ngam 15-30 phut, xa lanh ngay. Gang tay. CAM B2 tron.',dilution_vi:'1 muong X1 / 1L nuoc 40-50C — PHA MOI, khong de lau',dilution_ko:'40–50℃ 물 1L에 X1 큰술 1 — 즉석만 사용, 15–30분 담금 후 즉시 헹굼'},
  {code:'X2',name:'Oxalic Acid',name_vi:'Acid oxalic X2',name_ko:'옥살산(녹·철 얼룩용)',role:'Iron oxide / rust / laterite iron — PPE gloves required',safe_on_wool:false,safe_on_silk:false,shop_name_vi:'Acid oxalic / bot tay ri (hoa chat)',buy_where_vi:'Cua hoa chat — BAT BUOC gang tay',buy_where_ko:'화공점 — 반드시 장갑',alt1_vi:'A3 + nuoc chanh nhe neu khong co X2 (yeu hon)',alt2_vi:'CAM B2 tren sat oxit (co dinh sat)',alt3_vi:'Sau X2: xa + trung hoa N1 loang',alt1_ko:'없으면 식초·레몬(약함)',alt2_ko:'철 얼룩에 락스 금지(철 고착)',alt3_ko:'사용 후 헹굼 + 베이킹소다 약희석 중화',example_brands_vi:'',wf_supply:false,when_use_vi:'Ri set / dat do laterite (sat oxit). Cotton/linen/poly: 2-3% ~30 phut. Len/lua: KHONG X2 — dung A3 nhe. Gang tay. CAM B2.',dilution_vi:'Acid oxalic ~2-3% theo nhan; cotton/linen/poly ~30 phut; xa + N1 loang trung hoa',dilution_ko:'라벨 기준 약 2–3%; 면·린넨·폴리 ~30분; 헹굼 후 베이킹소다 약희석으로 중화'}
] AS c
MERGE (n:Chemical {code:c.code})
SET n += c
RETURN count(n) AS created""")
        _r(s, "E2b_x_chem_safety_links", """
MATCH (c:Chemical) WHERE c.code IN ['X1','X2']
MATCH (f:Fabric) WHERE f.id IN ['F3','F4','F7','F8','F9','F10']
MERGE (f)-[:NEVER_USE]->(c)
WITH count(*) AS _
MATCH (c2:Chemical {code:'X1'})
MATCH (f2:Fabric) WHERE f2.id IN ['F2','F6']
MERGE (f2)-[:NEVER_USE]->(c2)
WITH count(*) AS _
MATCH (s:Stain {id:'S_RUST'}),(x2:Chemical {code:'X2'})
MERGE (s)-[:USES_CHEMICAL]->(x2)
WITH count(*) AS _
MATCH (s2:Stain {id:'S_LATERITE'}),(x2b:Chemical {code:'X2'})
MERGE (s2)-[:USES_CHEMICAL]->(x2b)
WITH count(*) AS _
MATCH (s3:Stain {id:'S_SHIRT_YELLOW'}),(x1:Chemical {code:'X1'})
MERGE (s3)-[:USES_CHEMICAL]->(x1)
RETURN count(*) AS rels""")
        _r(s, "F_stains_protein", """
UNWIND [
  {id:'S_BLOOD_FRESH',name:'Fresh Blood',name_vi:'Mau tuoi',group_id:'G1',water_spreads:true,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:false,urgency:'immediate',tip:'Cold water only - hot sets protein'},
  {id:'S_BLOOD_DRY',name:'Dried Blood',name_vi:'Mau kho',group_id:'G1',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:false,urgency:'same_day',tip:'Enzyme soak 30min then scrub'},
  {id:'S_EGG',name:'Egg',name_vi:'Trung',group_id:'G1',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:false,urgency:'same_day',tip:'Scrape yolk cold water enzyme'},
  {id:'S_MILK',name:'Milk',name_vi:'Sua',group_id:'G1',water_spreads:true,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:false,urgency:'same_day',tip:'Rinse cold enzyme soak - sour milk harder'},
  {id:'S_VOMIT',name:'Vomit',name_vi:'Chat non',group_id:'G1',water_spreads:false,contains_protein:true,contains_tannin:true,contains_oil:false,contains_dye:false,urgency:'immediate',tip:'Scrape remove solids enzyme soak deodorize'},
  {id:'S_URINE',name:'Urine',name_vi:'Nuoc tieu',group_id:'G1',water_spreads:true,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Vinegar soak kills bacteria enzyme removes protein odor'},
  {id:'S_FECES',name:'Feces',name_vi:'Phan',group_id:'G1',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Remove solids cold water enzyme soak'},
  {id:'S_BABY_FORMULA',name:'Baby Formula',name_vi:'Sua cong thuc',group_id:'G1',water_spreads:true,contains_protein:true,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Lipase + protease combo soak warm'},
  {id:'S_GRASS',name:'Grass',name_vi:'Co xanh',group_id:'G1',water_spreads:false,contains_protein:true,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'Alcohol first then enzyme then oxygen bleach'},
  {id:'S_MUD',name:'Mud',name_vi:'Bun dat',group_id:'G1',water_spreads:false,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:false,urgency:'low',tip:'Let dry completely brush off then wash - never wet scrub fresh'},
  {id:'S_CHOCOLATE',name:'Chocolate',name_vi:'Socola',group_id:'G1',water_spreads:false,contains_protein:true,contains_tannin:true,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Scrape cold water enzyme 30min oxygen bleach if needed'}
] AS s MERGE (n:Stain {id:s.id}) SET n += s RETURN count(n) AS created""")
        _r(s, "G_stains_oil", """
UNWIND [
  {id:'S_BUTTER',name:'Butter',name_vi:'Bo',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Cornstarch absorb 10min brush then dish soap'},
  {id:'S_COOKING_OIL',name:'Cooking Oil',name_vi:'Dau an',name_ko:'식용유·오일·기름(식용)',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Absorb powder then dish soap; lipase enzyme if available; never dry while greasy'},
  {id:'S_ENGINE_OIL',name:'Engine Oil',name_vi:'Dau dong co',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Solvent degreaser first then strong detergent - dark stain'},
  {id:'S_GREASE',name:'Grease/Lard',name_vi:'Mo',name_ko:'기름때·그리즈',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Absorb cornstarch then dish soap + lipase enzyme'},
  {id:'S_MAYO',name:'Mayonnaise',name_vi:'Sot mayonnaise',name_ko:'마요네즈',group_id:'G2',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Scrape; dish soap for oil THEN protease enzyme for egg protein — order matters'},
  {id:'S_COLLAR_STAIN',name:'Collar Stain',name_vi:'Vong co / vet co ao so mi',name_ko:'목때·칼라 황변',group_id:'G2',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'low',tip:'Sebum+skin: enzyme on dry collar first; NEVER chlorine (yellow worsens); then oxygen'},
  {id:'S_SHOE_POLISH',name:'Shoe Polish',name_vi:'Xi giay',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Solvent then dish soap - color dye difficult to remove'},
  {id:'S_LIPSTICK',name:'Lipstick',name_vi:'Son moi',name_ko:'립스틱·립스틱 자국',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'3-layer: wax scrape then oil (alcohol blot from back) then pigment (dish soap/oxy). Never rub — blot only. Silk/wool: test corner'},
  {id:'S_FOUNDATION',name:'Foundation',name_vi:'Kem nen',name_ko:'파운데이션·쿠션·화장품',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Oil base + pigment: blot gently dish soap first then alcohol spot if color remains. Silk/wool: S1 only'},
  {id:'S_CANDLE_WAX',name:'Candle Wax',name_vi:'Sap nen',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'low',tip:'Freeze+break then iron with paper to absorb wax'},
  {id:'S_GUM',name:'Chewing Gum',name_vi:'Keo cao su',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:false,urgency:'low',tip:'Freeze with ice bag then break apart carefully'},
  {id:'S_MOTORBIKE_OIL',name:'Motorbike Oil',name_vi:'Dau nhot xe may',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'VN specialty: N3 thick absorb twice then D1 ventilated then A1 spot then D3 wash - check before dry - silk/wool skip hot wash'},
  {id:'S_DEODORANT',name:'Deodorant Stain',name_vi:'Vet khu mui',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'low',tip:'White residue: vinegar dilute soak then wash; yellow armpit: oxygen bleach soak then enzyme'},
  {id:'S_PAINT_LATEX',name:'Latex Paint',name_vi:'Son nuoc',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'While wet rinse cold scrape then detergent; once dry much harder solvent test corner first'},
  {id:'S_RUST',name:'Rust',name_vi:'Ri set',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'Oxalic/specialty rust remover on cotton; silk/wool use diluted vinegar instead - neutralize after - gloves required'}
] AS s MERGE (n:Stain {id:s.id}) SET n += s RETURN count(n) AS created""")
        _r(s, "H_stains_tannin", """
UNWIND [
  {id:'S_BLACK_COFFEE',name:'Black Coffee',name_vi:'Ca phe den',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:false,urgency:'immediate',tip:'Cold water immediately vinegar soak then wash'},
  {id:'S_MILK_COFFEE',name:'Milk Coffee',name_vi:'Ca phe sua',group_id:'G3',water_spreads:true,contains_protein:true,contains_tannin:true,contains_oil:false,contains_dye:false,urgency:'immediate',tip:'Enzyme for protein first then vinegar for tannin'},
  {id:'S_TEA',name:'Tea',name_vi:'Nuoc tra',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:false,urgency:'immediate',tip:'Cold water vinegar soak oxygen bleach for old stain'},
  {id:'S_RED_WINE',name:'Red Wine',name_vi:'Ruou vang do',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Salt immediately absorb then sparkling water then oxygen bleach'},
  {id:'S_WHITE_WINE_BEER',name:'White Wine/Beer',name_vi:'Ruou vang trang/Bia',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:false,urgency:'immediate',tip:'Cold water immediately - may become invisible then yellow over time'},
  {id:'S_SOFT_DRINK',name:'Soft Drink/Cola',name_vi:'Nuoc ngot',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Cold water vinegar if colored drink vinegar soak'},
  {id:'S_FRUIT_JUICE',name:'Fruit Juice',name_vi:'Nuoc trai cay / juice',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Cold water immediately; vinegar 1:4 then oxygen bleach if color remains — white cotton OK for B1; silk/wool no B1'},
  {id:'S_TOMATO_SAUCE',name:'Tomato Sauce',name_vi:'Sot ca chua',name_ko:'토마토 소스',group_id:'G3',water_spreads:false,contains_protein:false,contains_tannin:true,contains_oil:true,contains_dye:true,urgency:'immediate',tip:'Scrape then dish soap for oil then vinegar for tannin/lycopene'},
  {id:'S_KETCHUP',name:'Ketchup',name_vi:'Tuong ca / ketchup',name_ko:'케첩',group_id:'G3',water_spreads:false,contains_protein:false,contains_tannin:true,contains_oil:true,contains_dye:true,urgency:'immediate',tip:'Ketchup=tomato dye+sugar+oil film. Scrape→dish soap→vinegar→oxygen on white'},
  {id:'S_SOY_SAUCE',name:'Soy Sauce',name_vi:'Nuoc tuong',name_ko:'간장',group_id:'G3',water_spreads:true,contains_protein:true,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Cold water enzyme for protein then vinegar for tannin/dye'},
  {id:'S_FISH_SAUCE',name:'Fish Sauce',name_vi:'Nuoc mam',name_ko:'느억맘·액젓',group_id:'G3',water_spreads:true,contains_protein:true,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Cold enzyme; salt odor needs vinegar deodorize; dye may need oxygen on white'},
  {id:'S_BBQ_SAUCE',name:'BBQ Sauce',name_vi:'Sot BBQ',name_ko:'BBQ 소스',group_id:'G3',water_spreads:false,contains_protein:true,contains_tannin:true,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Triple: enzyme then dish soap then vinegar sequential'},
  {id:'S_KIMCHI',name:'Kimchi / kimchi broth',name_vi:'Kim chi / nuoc kim chi',name_ko:'김치·김치국물',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:true,contains_dye:true,urgency:'immediate',tip:'Kimchi: chili dye + oil + salt/acid. Cold rinse ASAP; dish soap for oil then vinegar; oxygen bleach on white only'},
  {id:'S_BUBBLE_TEA',name:'Bubble tea / milk tea boba',name_vi:'Tra sua tran chau / bubble tea',name_ko:'버블티·밀크티·타피오카',group_id:'G3',water_spreads:true,contains_protein:true,contains_tannin:true,contains_oil:true,contains_dye:true,urgency:'immediate',tip:'4 layers: tea tannin + milk protein + tapioca starch + sugar. Order: cold rinse → enzyme → dish soap → vinegar → oxygen on white. NEVER hot first'}
] AS s MERGE (n:Stain {id:s.id}) SET n += s RETURN count(n) AS created""")
        _r(s, "I_stains_dye", """
UNWIND [
  {id:'S_MUSTARD',name:'Mustard',name_vi:'Mu-ta-det',group_id:'G4',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'Scrape baking soda paste then oxygen bleach - curcumin UV sensitive dry in sun'},
  {id:'S_CURRY',name:'Curry/Turmeric',name_vi:'Ca ri/Nghe',group_id:'G4',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Dish soap for oil then baking soda then sun bleach UV'},
  {id:'S_INK_PEN',name:'Pen Ink',name_vi:'Muc but bi',group_id:'G4',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'Isopropyl alcohol blot - never rub spreads dye'},
  {id:'S_INK_PERMANENT',name:'Permanent Marker',name_vi:'But long',group_id:'G4',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'Acetone or alcohol - test fabric first may not remove fully'},
  {id:'S_SWEAT_FRESH',name:'Fresh Sweat',name_vi:'Mo hoi tuoi',group_id:'G5',water_spreads:true,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:false,urgency:'same_day',tip:'Enzyme soak cold then wash - bacteria cause odor'},
  {id:'S_SWEAT_YELLOW',name:'Yellow Armpit Stain',name_vi:'Ve o nach',group_id:'G5',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'low',tip:'Old sweat+deodorant: oxygen bleach soak 2h then enzyme - difficult'},
  {id:'S_PERFUME',name:'Perfume/Alcohol Spray',name_vi:'Nuoc hoa',group_id:'G5',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'Vinegar diluted soak - may yellow white fabric over time'},
  {id:'S_NAIL_POLISH',name:'Nail Polish',name_vi:'Son mong',group_id:'G4',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Acetone from back of fabric - never rub into fiber'},
  {id:'S_MILDEW',name:'Mildew / mold',name_vi:'Nam moc',name_ko:'곰팡이·곰팡이 제거',group_id:'G5',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'PPE outdoors brush; vinegar soak kill; oxygen for pigment; chlorine ONLY white cotton; never dry until clear'},
  {id:'S_DYE_TRANSFER',name:'Dye transfer / color bleed',name_vi:'Lo mau / mau lan / dye transfer',name_ko:'이염·물든 옷',group_id:'G4',water_spreads:true,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Do NOT dry. Oxygen bleach long soak; white cotton may use diluted chlorine carefully; silk/wool no bleach'},
  {id:'S_STARCH_TRANSFER',name:'Starch sizing dye bleed',name_vi:'Ho tinh bot / starch + mau lan',name_ko:'풀(전분)·풀로 묻은 이염',group_id:'G4',water_spreads:true,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Amylase enzyme digests starch carrier then oxygen for dye; do not dry'},
  {id:'S_SHIRT_YELLOW',name:'Yellowed white dress shirt',name_vi:'Ao so mi trang vang / yellowed shirt',name_ko:'누렇게 된 와이셔츠·흰셔츠 황변',group_id:'G5',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'low',tip:'Sebum+sweat oxidize. Enzyme FIRST. NEVER chlorine on protein yellow (worse). Then oxygen soak. Soft brush only'},
  {id:'S_LATERITE',name:'Laterite Red Soil',name_vi:'Dat do laterite / laterite / dat do',group_id:'G5',water_spreads:false,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'VN red soil: let DRY brush off then cold rinse then vinegar then oxygen bleach - iron oxide may need specialty acid with gloves neutralize after'},
  {id:'S_GLUE',name:'Glue/Adhesive',name_vi:'Keo dan',group_id:'G4',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:false,urgency:'same_day',tip:'Water-based glue: soak warm detergent; solvent glue: A2/A1 test corner then blot - scrape excess first'}
] AS s MERGE (n:Stain {id:s.id}) SET n += s RETURN count(n) AS created""")
        _r(s, "J_relationships", """
MATCH (stain:Stain) WHERE stain.group_id IS NOT NULL
MATCH (grp:StainGroup {id: stain.group_id})
MERGE (stain)-[:BELONGS_TO]->(grp)
RETURN count(*) AS rels""")
        _r(s, "K_chem_protein", """
MATCH (s:Stain) WHERE s.contains_protein=true
MATCH (e1:Chemical {code:'E1'})
MERGE (s)-[:USES_CHEMICAL]->(e1)
RETURN count(DISTINCT s) AS stains""")
        _r(s, "K2_chem_blood_salt_ammonia", """
// Salt / diluted ammonia — blood only (not every protein stain)
MATCH (s:Stain) WHERE s.id IN ['S_BLOOD_FRESH','S_BLOOD_DRY']
MATCH (n2:Chemical {code:'N2'}),(a5:Chemical {code:'A5'})
FOREACH (c IN [n2,a5] | MERGE (s)-[:USES_CHEMICAL]->(c))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "K3_drop_protein_salt_ammonia_elsewhere", """
MATCH (s:Stain)-[r:USES_CHEMICAL]->(c:Chemical)
WHERE s.contains_protein = true
  AND c.code IN ['N2','A5']
  AND NOT s.id IN ['S_BLOOD_FRESH','S_BLOOD_DRY']
DELETE r
RETURN count(*) AS dropped""")
        _r(s, "L_chem_oil", """
MATCH (s:Stain) WHERE s.contains_oil=true
MATCH (d2:Chemical {code:'D2'}),(n3:Chemical {code:'N3'})
FOREACH (c IN [d2,n3] | MERGE (s)-[:USES_CHEMICAL]->(c))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "L2_chem_oil_lipase", """
// Lipase only where fat/oil enzyme helps — not candle wax
MATCH (s:Stain) WHERE s.contains_oil=true AND NOT s.id IN ['S_CANDLE_WAX']
MATCH (e3:Chemical {code:'E3'})
MERGE (s)-[:USES_CHEMICAL]->(e3)
RETURN count(DISTINCT s) AS stains""")
        _r(s, "L3_drop_wax_enzyme", """
MATCH (s:Stain {id:'S_CANDLE_WAX'})-[r:USES_CHEMICAL]->(c:Chemical)
WHERE c.code IN ['E3','E1','E2']
DELETE r
RETURN count(*) AS dropped""")
        _r(s, "M_chem_tannin", """
MATCH (s:Stain) WHERE s.contains_tannin=true
MATCH (a1:Chemical {code:'A3'}),(b1:Chemical {code:'B1'})
FOREACH (c IN [a1,b1] | MERGE (s)-[:USES_CHEMICAL]->(c))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "N_chem_dye", """
MATCH (s:Stain) WHERE s.contains_dye=true
  AND NOT s.id IN ['S_RUST','S_PAINT_LATEX','S_MUSTARD','S_CURRY','S_GLUE']
MATCH (a1:Chemical {code:'A1'}),(b1:Chemical {code:'B1'})
FOREACH (c IN [a1,b1] | MERGE (s)-[:USES_CHEMICAL]->(c))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "N2_specialty_stain_chems", """
// Rewrite specialty stains: drop stale flag links, attach protocol chems
MATCH (s:Stain) WHERE s.id IN [
  'S_RUST','S_GUM','S_CANDLE_WAX','S_MOTORBIKE_OIL','S_ENGINE_OIL',
  'S_GLUE','S_PAINT_LATEX','S_MUSTARD','S_CURRY','S_KIMCHI',
  'S_DYE_TRANSFER','S_STARCH_TRANSFER','S_SHIRT_YELLOW','S_MILDEW',
  'S_KETCHUP','S_TOMATO_SAUCE','S_MAYO','S_COLLAR_STAIN',
  'S_SOY_SAUCE','S_FISH_SAUCE','S_COOKING_OIL','S_GREASE',
  'S_LIPSTICK','S_FOUNDATION','S_BUBBLE_TEA'
]
OPTIONAL MATCH (s)-[old:USES_CHEMICAL]->()
DELETE old
WITH DISTINCT s
MATCH (a1:Chemical {code:'A1'}),(a2:Chemical {code:'A2'}),(a3:Chemical {code:'A3'}),
      (b1:Chemical {code:'B1'}),(b2:Chemical {code:'B2'}),
      (d1:Chemical {code:'D1'}),(d2:Chemical {code:'D2'}),
      (d3:Chemical {code:'D3'}),(n1:Chemical {code:'N1'}),(n3:Chemical {code:'N3'}),
      (e1:Chemical {code:'E1'}),(e2:Chemical {code:'E2'}),(e3:Chemical {code:'E3'})
FOREACH (_ IN CASE WHEN s.id = 'S_RUST' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(a3))
FOREACH (_ IN CASE WHEN s.id = 'S_CANDLE_WAX' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(n3) MERGE (s)-[:USES_CHEMICAL]->(d2))
FOREACH (_ IN CASE WHEN s.id IN ['S_MOTORBIKE_OIL','S_ENGINE_OIL'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(n3) MERGE (s)-[:USES_CHEMICAL]->(d1)
  MERGE (s)-[:USES_CHEMICAL]->(a1) MERGE (s)-[:USES_CHEMICAL]->(d3))
FOREACH (_ IN CASE WHEN s.id = 'S_GLUE' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(d2) MERGE (s)-[:USES_CHEMICAL]->(a1)
  MERGE (s)-[:USES_CHEMICAL]->(a2))
FOREACH (_ IN CASE WHEN s.id = 'S_PAINT_LATEX' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(d2) MERGE (s)-[:USES_CHEMICAL]->(a1))
FOREACH (_ IN CASE WHEN s.id IN ['S_MUSTARD','S_CURRY'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(n1) MERGE (s)-[:USES_CHEMICAL]->(b1)
  MERGE (s)-[:USES_CHEMICAL]->(d2))
FOREACH (_ IN CASE WHEN s.id IN ['S_KIMCHI','S_KETCHUP','S_TOMATO_SAUCE','S_BUBBLE_TEA'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(d2) MERGE (s)-[:USES_CHEMICAL]->(a3)
  MERGE (s)-[:USES_CHEMICAL]->(b1))
FOREACH (_ IN CASE WHEN s.id = 'S_BUBBLE_TEA' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(e1) MERGE (s)-[:USES_CHEMICAL]->(e2))
FOREACH (_ IN CASE WHEN s.id = 'S_DYE_TRANSFER' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(b1) MERGE (s)-[:USES_CHEMICAL]->(a3)
  MERGE (s)-[:USES_CHEMICAL]->(b2) MERGE (s)-[:USES_CHEMICAL]->(d3))
FOREACH (_ IN CASE WHEN s.id = 'S_STARCH_TRANSFER' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(e2) MERGE (s)-[:USES_CHEMICAL]->(b1)
  MERGE (s)-[:USES_CHEMICAL]->(d3))
FOREACH (_ IN CASE WHEN s.id IN ['S_SHIRT_YELLOW','S_COLLAR_STAIN'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(e1) MERGE (s)-[:USES_CHEMICAL]->(e3)
  MERGE (s)-[:USES_CHEMICAL]->(d2) MERGE (s)-[:USES_CHEMICAL]->(b1))
FOREACH (_ IN CASE WHEN s.id = 'S_MILDEW' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(a3) MERGE (s)-[:USES_CHEMICAL]->(b1)
  MERGE (s)-[:USES_CHEMICAL]->(b2) MERGE (s)-[:USES_CHEMICAL]->(d3))
FOREACH (_ IN CASE WHEN s.id = 'S_MAYO' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(d2) MERGE (s)-[:USES_CHEMICAL]->(e1)
  MERGE (s)-[:USES_CHEMICAL]->(e3))
FOREACH (_ IN CASE WHEN s.id IN ['S_SOY_SAUCE','S_FISH_SAUCE'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(e1) MERGE (s)-[:USES_CHEMICAL]->(a3)
  MERGE (s)-[:USES_CHEMICAL]->(b1))
FOREACH (_ IN CASE WHEN s.id IN ['S_COOKING_OIL','S_GREASE'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(n3) MERGE (s)-[:USES_CHEMICAL]->(d2)
  MERGE (s)-[:USES_CHEMICAL]->(e3))
FOREACH (_ IN CASE WHEN s.id = 'S_LIPSTICK' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(d2) MERGE (s)-[:USES_CHEMICAL]->(a1)
  MERGE (s)-[:USES_CHEMICAL]->(b1))
FOREACH (_ IN CASE WHEN s.id = 'S_FOUNDATION' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(d2) MERGE (s)-[:USES_CHEMICAL]->(a1)
  MERGE (s)-[:USES_CHEMICAL]->(b1))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "O_force_levels", """
MATCH (s:Stain)
MATCH (f:ForceLevel)
WITH s, f
WHERE (s.contains_protein=true AND f.level IN [2,3])
   OR (s.contains_oil=true AND f.level IN [3,4])
   OR (s.contains_tannin=true AND f.level IN [2,3])
   OR (s.contains_dye=true AND f.level IN [2,3])
MERGE (s)-[:REQUIRES_FORCE]->(f)
RETURN count(*) AS rels""")
        _r(s, "P_delicate_warn", """
MATCH (s:Stain) WHERE s.contains_protein=true
MATCH (f:Fabric) WHERE f.enzyme_safe=false
MERGE (s)-[:CAUTION_ON]->(f)
RETURN count(*) AS rels""")
        _r(s, "Q_bleach_warn", """
MATCH (f:Fabric) WHERE f.id IN ['F2','F5','F6']
MATCH (c:Chemical {code:'B1'})
OPTIONAL MATCH (f)-[r:NEVER_USE]->(c)
DELETE r
WITH count(r) AS _del
MATCH (f2:Fabric) WHERE f2.can_bleach=false
MATCH (c2:Chemical {code:'B2'})
MERGE (f2)-[:NEVER_USE]->(c2)
WITH count(*) AS _b2
MATCH (f3:Fabric) WHERE f3.id IN ['F3','F4','F7','F8','F9','F10']
MATCH (c3:Chemical {code:'B1'})
MERGE (f3)-[:NEVER_USE]->(c3)
WITH count(*) AS _b1
MATCH (fo:Fabric) WHERE fo.id IN ['F1','F2','F5','F6']
SET fo.can_oxygen = true
WITH count(*) AS _ox1
MATCH (fn:Fabric) WHERE fn.id IN ['F3','F4','F7','F8','F9','F10']
SET fn.can_oxygen = false
RETURN count(*) AS rels""")
        _r(s, "R_never_mix", """
MATCH (c1:Chemical {code:'B2'}),(c2:Chemical {code:'A5'})
MERGE (c1)-[:NEVER_MIX_WITH]->(c2)
MERGE (c2)-[:NEVER_MIX_WITH]->(c1)
RETURN count(*) AS rels""")
        # Additive ops fields — fail-soft; never deletes existing stain/chem nodes
        _r(s, "T_tools", """
UNWIND [
  {id:'T_BRUSH_SOFT',name_vi:'Ban chai spotting mem',name_ko:'연질 스포팅 솔',use_for_vi:'Cotton, polyester, vet thuong, vanh mu'},
  {id:'T_BRUSH_HARD',name_vi:'Ban chai spotting cung',name_ko:'경질 스포팅 솔',use_for_vi:'Denim, canvas, giay the thao'},
  {id:'T_BRUSH_ULTRA',name_vi:'Ban chai sieu mem / mieng fot',name_ko:'초연질 솔·스펀지',use_for_vi:'Lua, len, vai mong — khong cha manh'},
  {id:'T_CLOTH',name_vi:'Khan trang sach / giay tham',name_ko:'흰 천·흡수지',use_for_vi:'Tham, lot duoi, khong cha lan'},
  {id:'T_SPRAY',name_vi:'Binh xit rieng (dan nhan)',name_ko:'분무기(라벨 필수)',use_for_vi:'Pha loang A3/D2/B1 — khong tron binh; PPE khi xit hoa chat'},
  {id:'T_BRUSH_SHOE',name_vi:'Ban chai de giay (long cung)',name_ko:'운동화 밑창용 경질 솔',use_for_vi:'De cao su — KHONG dung tren mesh/lua'},
  {id:'T_GLOVE_NITRILE',name_vi:'Gang tay nitrile (PPE)',name_ko:'니트릴 장갑(PPE)',use_for_vi:'BAT BUOC voi X2/B2/A1/A2/dung moi — khong dung gang mong voi acid/tay'},
  {id:'T_MESH_BAG',name_vi:'Tui luoi giat',name_ko:'세탁망',use_for_vi:'Do mong, mu mem (neu cho phep), gang, day giay — giam ma sat may'}
] AS t MERGE (n:Tool {id:t.id}) SET n += t RETURN count(n) AS created""")
        _r(s, "U_stain_ops_protein", """
MATCH (s:Stain) WHERE s.contains_protein = true
SET s.precheck_vi = coalesce(s.precheck_vi, 'Xac nhan vai + vet tuoi/kho + KHONG dung nuoc nong dau'),
    s.motion_vi = coalesce(s.motion_vi, 'Tham/cao tu NGOAI vao TAM — khong cha lan'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Nuoc LANH (duoi 40C). Enzyme toi uu ~30-37C sau khi da an toan'),
    s.aftercare_vi = coalesce(s.aftercare_vi,
      'Anh sang manh: con vet → xu ly lai, CAM say. Phoi bong mat thoang; tranh nang gay (phai mau). Ui theo iron_hint vai neu can.')
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_oil", """
MATCH (s:Stain) WHERE s.contains_oil = true AND coalesce(s.contains_protein,false) = false
SET s.precheck_vi = coalesce(s.precheck_vi, 'Xac nhan vai + hut dau truoc (N3) — khong say khi con dau'),
    s.motion_vi = coalesce(s.motion_vi, 'Hut bot → xit/tham mat trai → cha nhe vong tron ngoai→trong'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Am 30-40C sau khi da tay dau; cotton co the am hon neu nhan cho phep'),
    s.aftercare_vi = coalesce(s.aftercare_vi,
      'Het cam giac nhon + kiem tra truoc say. Con loang → lap. Phoi thoang bong mat; tranh nang gay. Ui theo vai.')
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_tannin", """
MATCH (s:Stain) WHERE s.contains_tannin = true AND coalesce(s.contains_protein,false) = false AND coalesce(s.contains_oil,false) = false
SET s.precheck_vi = coalesce(s.precheck_vi, 'Xu ly SOM + nuoc lanh; test goc khuat truoc acid/tay'),
    s.motion_vi = coalesce(s.motion_vi, 'Tham mat trai, ngoai→trong — khong cha lan mau'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Nuoc lanh luc dau; sau A3 co the giat am nhe neu vai cho phep'),
    s.aftercare_vi = coalesce(s.aftercare_vi,
      'Kiem tra mau con lai truoc say; con → lap (B1 neu vai cho, khong len/lua). Phoi bong mat thoang, tranh nang gay.')
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_dye", """
MATCH (s:Stain) WHERE s.contains_dye = true AND coalesce(s.contains_oil,false) = false AND coalesce(s.contains_protein,false) = false AND coalesce(s.contains_tannin,false) = false
SET s.precheck_vi = coalesce(s.precheck_vi, 'Test phai mau o goc khuat; xac nhan muc but hay but long'),
    s.motion_vi = coalesce(s.motion_vi, 'CHAM/THAM tu mat trai — TUYET DOI khong cha lan'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Phong nhiet; giat lanh/am nhe sau khi het muc'),
    s.aftercare_vi = coalesce(s.aftercare_vi,
      'Kiem tra ky truoc say — nhiet khoa mau. Phoi bong mat thoang; tranh nang gay. Ui thap theo vai.')
RETURN count(s) AS updated""")
        # Enrich short/default aftercare already stored (additive; keeps stain-specific overrides that mention specialty paths)
        _r(s, "W_aftercare_enrich", """
MATCH (s:Stain)
WHERE s.aftercare_vi IN [
  'Kiem tra anh sang manh TRUOC khi say/ui. Con vet → xu ly lai, khong say',
  'Het cam giac nhon + kiem tra truoc say. Con loang → lap D1/D2',
  'Kiem tra mau con lai truoc say; B1 neu con mau (khong len/lua)',
  'Kiem tra ky truoc say — nhiet khoa mau muc'
]
SET s.aftercare_vi = CASE
  WHEN s.contains_oil = true AND coalesce(s.contains_protein,false) = false
    THEN 'Het nhon + anh sang manh truoc say. Con → lap. Phoi thoang bong mat; tranh nang gay (phai mau). Ui theo iron_hint vai.'
  WHEN s.contains_tannin = true AND coalesce(s.contains_protein,false) = false AND coalesce(s.contains_oil,false) = false
    THEN 'Anh sang manh: con mau → lap (oxy chi neu vai cho, khong silk/wool). Phoi bong mat thoang; tranh nang gay.'
  WHEN s.contains_dye = true
    THEN 'Anh sang manh truoc say — nhiet khoa mau. Phoi bong mat thoang; tranh nang gay. Ui thap theo vai.'
  ELSE
    'Anh sang manh: con vet → xu ly lai, CAM say. Phoi bong mat thoang; tranh nang gay. Ui theo iron_hint vai neu can.'
END
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_overrides", """
UNWIND [
  {id:'S_BLOOD_FRESH',precheck_vi:'Mau tuoi — uu tien ngay, chi nuoc lanh',motion_vi:'Xa mat trai, tham — Cap luc 1, khong cha',water_temp_vi:'Chi nuoc LANH',aftercare_vi:'Kiem tra truoc say; con nau → E1'},
  {id:'S_INK_PEN',precheck_vi:'Test goc khuat; lot giay tham duoi',motion_vi:'Cham A1 mat trai, thay khan — khong cha',water_temp_vi:'Xu ly o nhiet do phong; giat lanh sau',aftercare_vi:'Het muc moi say'},
  {id:'S_INK_PERMANENT',precheck_vi:'But long kho — test vai; co the khong het 100%',motion_vi:'A2/A1 cham nhe mat trai',water_temp_vi:'Nhiet phong',aftercare_vi:'Thong bao khach neu con vet'},
  {id:'S_MOTORBIKE_OIL',precheck_vi:'Dau nhot xe may — thong gio khi dung D1',motion_vi:'N3 day 2 lan → D1 → A1 cham → D3',water_temp_vi:'Giat am/nong chi cotton-poly; khong silk/wool',aftercare_vi:'Kiem tra nhon truoc say'},
  {id:'S_LATERITE',precheck_vi:'Dat do — de KHO roi chai bot truoc',motion_vi:'Chai kho → xa lanh → A3 → B1',water_temp_vi:'Lanh/am; khong say khi con mau do',aftercare_vi:'Lap lai neu con sat oxit'},
  {id:'S_FRUIT_JUICE',precheck_vi:'Nuoc trai cay / juice tren vai — xu ly SOM. Ghi ro vai trang hay mau. Test goc khuat.',motion_vi:'Tham/nhan nhe ngoai→trong mat trai — khong cha lan',water_temp_vi:'Bat dau nuoc LANH; sau A3 co the giat am neu vai cho',aftercare_vi:'Anh sang manh: con mau → lap A3 roi B1 (vai trang/cotton cho phep; CAM len/lua). Phoi bong mat, tranh nang gay.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.precheck_vi = o.precheck_vi, s.motion_vi = o.motion_vi,
    s.water_temp_vi = o.water_temp_vi, s.aftercare_vi = o.aftercare_vi
RETURN count(s) AS updated""")
        _r(s, "V_chem_dilution", """
UNWIND [
  {code:'E1',dilution_vi:'1 muong canh / 1 lit nuoc lanh; khuay tan, ngam 15-60 phut',dilution_ko:'찬물 1리터에 큰술 1 → 잘 녹여 15–60분 담금'},
  {code:'N2',dilution_vi:'2 muong canh / 1 lit nuoc lanh (mau tuoi)',dilution_ko:'찬물 1리터에 소금 큰술 2 (선혈)'},
  {code:'A3',dilution_vi:'1 phan giam + 4 phan nuoc (khu mui / tannin)',dilution_ko:'식초 1 : 물 4 (탄닌·냄새)'},
  {code:'A5',dilution_vi:'1 muong canh / 1 coc nuoc — KHONG tron B2',dilution_ko:'물 1컵에 큰술 1 — 락스(염소)와 절대 혼합 금지'},
  {code:'A4',dilution_vi:'Dung 3% nguyen (vai trang cotton)',dilution_ko:'3% 원액 (흰 면만, 구석 테스트)'},
  {code:'A1',dilution_vi:'Cham bang bong/khan — khong do ngap',dilution_ko:'솜·흰 천으로 가볍게 찍기 (흠뻑 붓지 말 것)'},
  {code:'D2',dilution_vi:'1-2 giot nguyen chat len vet hoac pha loang nhe',dilution_ko:'얼룩에 1–2방울 또는 약하게 희석'},
  {code:'S1',dilution_vi:'Theo huong dan chai Wash Friends — uu tien lua/len',dilution_ko:'워시프렌즈 중성세제 병 안내 따름 — 실크·울 우선'},
  {code:'B1',dilution_vi:'Theo nhan chai; thuong ngam 15-45 phut nuoc am/lanh — test mau',dilution_ko:'병 라벨 따름; 보통 찬물·미지근 15–45분 담금 — 구석 색 테스트'},
  {code:'D3',dilution_vi:'Theo nhan chai; uu tien chuong trinh thuong sau khi da xu ly vet',dilution_ko:'병 라벨 따름; 얼룩 전처리 후 일반 세탁 용량'},
  {code:'N1',dilution_vi:'Paste: baking soda + it nuoc; hoac 1-2 muong / 1 lit khi ngam',dilution_ko:'페이스트: 베이킹소다+물 약간; 또는 담글 때 1리터에 1–2큰술'},
  {code:'N3',dilution_vi:'Phu day len vet dau 10-30 phut roi chai bot',dilution_ko:'기름 얼룩에 두껍게 덮어 10–30분 후 털어내기'},
  {code:'D1',dilution_vi:'Cham it, thong gio; khong do ngap — theo nhan san pham',dilution_ko:'환기 필수, 소량 찍기 — 제품 라벨 따름'},
  {code:'E3',dilution_vi:'Theo nhan enzyme; thuong ngam am nhe 15-30 phut sau khi tay dau',dilution_ko:'라벨 따름; 보통 탈지 후 미지근 15–30분 담금'}
] AS d
MATCH (c:Chemical {code:d.code})
SET c.dilution_vi = d.dilution_vi, c.dilution_ko = d.dilution_ko
RETURN count(c) AS updated""")
        _r(s, "V2b_chem_alt_ko", """
UNWIND [
  {code:'E1',alt1_ko:'슈퍼 효소 표기 세제·효소 담금제',alt2_ko:'실크·울이면 워시프렌즈 중성세제만 (효소 금지)',alt3_ko:''},
  {code:'N2',alt1_ko:'식용 소금(정제염)',alt2_ko:'',alt3_ko:''},
  {code:'N1',alt1_ko:'베이킹소다(슈퍼)',alt2_ko:'',alt3_ko:''},
  {code:'D2',alt1_ko:'중성 주방세제',alt2_ko:'',alt3_ko:''},
  {code:'D3',alt1_ko:'일반 세탁 세제(액체/분말)',alt2_ko:'',alt3_ko:''},
  {code:'B1',alt1_ko:'산소계·과탄산 표백제(옥시클린 계열 등)',alt2_ko:'실크·울·모피 금지',alt3_ko:''},
  {code:'A3',alt1_ko:'식용 흰 식초 약 5%',alt2_ko:'레몬즙 희석(색 테스트)',alt3_ko:''},
  {code:'A4',alt1_ko:'약국 과산화수소 3%',alt2_ko:'흰 면에만; 없으면 산소계 표백제 약하게',alt3_ko:''},
  {code:'A1',alt1_ko:'약국 소독용 알코올 70–90%',alt2_ko:'',alt3_ko:''},
  {code:'S1',alt1_ko:'워시프렌즈 창고 중성세제',alt2_ko:'일시품절 시 울샴푸·극약 손세탁',alt3_ko:'효소·산소계와 병행 금지(민감 원단)'}
] AS x
MATCH (c:Chemical {code:x.code})
SET c.alt1_ko = x.alt1_ko, c.alt2_ko = x.alt2_ko, c.alt3_ko = x.alt3_ko
RETURN count(c) AS updated""")
        _r(s, "V2_chem_owner_labels", """
UNWIND [
  {code:'E1',name_ko:'효소(프로테아제) 세제·효소제',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'E2',name_ko:'전분 분해 효소 세제',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'E3',name_ko:'유지 분해 효소 세제',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'D1',name_ko:'기름·오일 용제(탈지제)',buy_where_ko:'자동차용품·화공점 (환기 필수)',buy_where_vi:'Cua o to / cua hoa chat — THONG GIO'},
  {code:'D2',name_ko:'주방세제(중성)',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'D3',name_ko:'일반 세탁 세제(강력)',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'B1',name_ko:'산소계 표백제(과탄산 계열)',buy_where_ko:'슈퍼 세탁용품 코너',buy_where_vi:'Sieu thi ke giat (chu tu mua)'},
  {code:'B2',name_ko:'염소계 표백제(락스/자벨)',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua) — CHI cotton trang'},
  {code:'A1',name_ko:'이소프로필 알코올(소독용 알코올)',buy_where_ko:'약국·슈퍼',buy_where_vi:'Nha thuoc, sieu thi'},
  {code:'A2',name_ko:'아세톤(매니큐어 리무버 계열)',buy_where_ko:'약국·화공점',buy_where_vi:'Nha thuoc, cua hoa chat'},
  {code:'A3',name_ko:'흰 식초(식용 식초 약 5%)',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'A4',name_ko:'과산화수소 3%(옥시)',buy_where_ko:'약국',buy_where_vi:'Nha thuoc'},
  {code:'A5',name_ko:'암모니아 희석액',buy_where_ko:'화공점',buy_where_vi:'Cua hoa chat — KHONG tron Javel'},
  {code:'N1',name_ko:'베이킹소다',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'N2',name_ko:'소금(식염)',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'N3',name_ko:'옥수수 전분·베이비파우더(오일 흡착)',buy_where_ko:'슈퍼/마트',buy_where_vi:'Sieu thi (chu tu mua)'},
  {code:'S1',name_ko:'워시프렌즈 중성세제',buy_where_ko:'워시프렌즈 본사·창고 공급',buy_where_vi:'Kho hang / cung ung noi bo Wash Friends'},
  {code:'WF_SOFT',name_ko:'워시프렌즈 섬유유연제',buy_where_ko:'워시프렌즈 본사·창고 공급',buy_where_vi:'Kho hang Wash Friends'},
  {code:'WF_FRAG',name_ko:'워시프렌즈 독일 향수 스프레이',buy_where_ko:'워시프렌즈 본사·창고 공급',buy_where_vi:'Kho hang Wash Friends'}
] AS x
MATCH (c:Chemical {code:x.code})
SET c.name_ko = x.name_ko, c.buy_where_ko = x.buy_where_ko, c.buy_where_vi = x.buy_where_vi
RETURN count(c) AS updated""")
        _r(s, "W_tool_links", """
MATCH (soft:Tool {id:'T_BRUSH_SOFT'}), (hard:Tool {id:'T_BRUSH_HARD'}),
      (ultra:Tool {id:'T_BRUSH_ULTRA'}), (cloth:Tool {id:'T_CLOTH'}), (spray:Tool {id:'T_SPRAY'})
WITH soft, hard, ultra, cloth, spray
MATCH (s:Stain)
FOREACH (_ IN CASE WHEN s.contains_oil = true OR s.contains_tannin = true THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(soft) MERGE (s)-[:USES_TOOL]->(cloth))
FOREACH (_ IN CASE WHEN s.contains_dye = true AND NOT s.id IN ['S_RUST','S_GUM'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(cloth) MERGE (s)-[:USES_TOOL]->(soft))
FOREACH (_ IN CASE WHEN s.contains_protein = true THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(cloth) MERGE (s)-[:USES_TOOL]->(ultra))
FOREACH (_ IN CASE WHEN s.id IN ['S_MOTORBIKE_OIL','S_ENGINE_OIL','S_MUD','S_LATERITE'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(hard))
FOREACH (_ IN CASE WHEN s.contains_tannin = true OR s.id STARTS WITH 'S_INK' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(spray))
FOREACH (_ IN CASE WHEN s.id IN ['S_GUM','S_CANDLE_WAX'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(cloth))
FOREACH (_ IN CASE WHEN s.id = 'S_RUST' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(cloth) MERGE (s)-[:USES_TOOL]->(soft))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "X_fabric_hints", """
UNWIND [
  {id:'F1',dry_hint_vi:'Say may OK neu sach; uu tien bong mat + quat',iron_hint_vi:'Ui 180-200C khi con am'},
  {id:'F2',dry_hint_vi:'Say nhiet thap; tranh nhiet cao (bong)',iron_hint_vi:'Ui thap 110-130C'},
  {id:'F3',dry_hint_vi:'KHONG say may — phoi phang bong mat',iron_hint_vi:'Hoi nuoc + lot vai, khong ui truc tiep'},
  {id:'F4',dry_hint_vi:'KHONG say may — bong mat',iron_hint_vi:'110C mat trai + lot, TAT hoi'},
  {id:'F5',dry_hint_vi:'Phoi/say vua; ui khi am',iron_hint_vi:'Ui cao 200-220C khi am'},
  {id:'F6',dry_hint_vi:'Say vua; lan dau giat rieng mau',iron_hint_vi:'Ui vua neu can'},
  {id:'F7',dry_hint_vi:'KHONG say may neu co the',iron_hint_vi:'Nhiet thap, can than'},
  {id:'F8',dry_hint_vi:'KHONG say may / KHONG nang truc tiep — phoi bong mat, boi kem da sau',iron_hint_vi:'KHONG ui'},
  {id:'F9',dry_hint_vi:'KHONG nuoc / KHONG say — chi kho, chuyen chuyen nghiep neu uot',iron_hint_vi:'KHONG ui'},
  {id:'F10',dry_hint_vi:'KHONG may/say — treo moc rong vai, thoang khi, tranh nang/nhiet; chuyen chuyen gia long',iron_hint_vi:'KHONG ui / KHONG steam manh'}
] AS h
MATCH (f:Fabric {id:h.id})
SET f.dry_hint_vi = h.dry_hint_vi, f.iron_hint_vi = h.iron_hint_vi
RETURN count(f) AS updated""")
        _r(s, "X2_leather_never_bleach", """
MATCH (f:Fabric) WHERE f.id IN ['F8','F9','F10']
MATCH (c:Chemical) WHERE c.code IN ['B1','B2','A4','E1','E2','E3','D3']
MERGE (f)-[:NEVER_USE]->(c)
RETURN count(*) AS rels""")
        # Category explain paths — KB principles only; never invent folk tips
        _r(s, "Y_paths_protein", """
MATCH (s:Stain) WHERE s.contains_protein = true
SET s.why_vi = coalesce(s.why_vi,
  'Protein bien tinh tren ~40C: nhiet/say lam vet dong cung gan soi — KHONG dao nguoc. Uu tien nuoc lanh + enzyme E1 (khong dung E1 tren len/lua).'),
    s.fresh_path_vi = coalesce(s.fresh_path_vi,
  'Vet TUOI: lat mat trai, xa nuoc LANH day protein ra ngoai; co the ngam N2 (muoi) nuoc lanh; roi E1 theo dilution neu con vet. Khong xa phong banh kiem manh neu khong can.'),
    s.dried_path_vi = coalesce(s.dried_path_vi,
  'Vet KHO/CU: ngam/cham E1 nuoc lanh 15-60 phut; con mau tren cotton trang co the A4 3% test goc khuat; len/lua: S1 trung tinh, tranh E1/A4 manh.')
RETURN count(s) AS updated""")
        _r(s, "Y_paths_oil", """
MATCH (s:Stain) WHERE s.contains_oil = true AND coalesce(s.contains_protein,false) = false
SET s.why_vi = coalesce(s.why_vi,
  'Dau/mo bam soi: can hut (N3) + pha tan (D1/D2) truoc khi giat. Say khi con dau se khoa vet.'),
    s.fresh_path_vi = coalesce(s.fresh_path_vi,
  'Vet TUOI: thấm bot N3 hut dau → D2/D1 cham mat trai → xa → giat. Thong gio khi dung dung moi.'),
    s.dried_path_vi = coalesce(s.dried_path_vi,
  'Vet KHO: N3 day 1-2 lan → D1/D2 lap lai → D3/giat. Kiem tra het nhon truoc say.')
RETURN count(s) AS updated""")
        _r(s, "Y_paths_tannin", """
MATCH (s:Stain) WHERE s.contains_tannin = true AND coalesce(s.contains_protein,false) = false AND coalesce(s.contains_oil,false) = false
SET s.why_vi = coalesce(s.why_vi,
  'Tannin (ca phe/tra/ruou...): xu ly SOM + nuoc lanh; acid nhe (A3) ho tro; nhiet som co the khoa mau.'),
    s.fresh_path_vi = coalesce(s.fresh_path_vi,
  'Vet TUOI: tham mat trai nuoc lanh → A3 pha 1:4 neu can → giat. Test goc khuat truoc khi tay manh.'),
    s.dried_path_vi = coalesce(s.dried_path_vi,
  'Vet KHO: A3 → neu con mau B1 (khong len/lua) → kiem tra truoc say.')
RETURN count(s) AS updated""")
        _r(s, "Y_paths_dye", """
MATCH (s:Stain) WHERE s.contains_dye = true AND coalesce(s.contains_oil,false) = false AND coalesce(s.contains_protein,false) = false AND coalesce(s.contains_tannin,false) = false
SET s.why_vi = coalesce(s.why_vi,
  'Mau muc/but: de lan. Chi CHAM/THAM mat trai; nhiet say khoa mau muc.'),
    s.fresh_path_vi = coalesce(s.fresh_path_vi,
  'Vet TUOI: lot giay tham, cham A1/A2 mat trai, thay khan lien — khong cha.'),
    s.dried_path_vi = coalesce(s.dried_path_vi,
  'Vet KHO: lap A1/A2 nhe; thong bao khach neu khong het 100%; het muc moi say.')
RETURN count(s) AS updated""")
        _r(s, "Z_paths_overrides", """
UNWIND [
  {id:'S_BLOOD_FRESH',
   why_vi:'GIAO DUC: Mau tuoi = hemoglobin (protein + sat). Nuoc LANH giu protein hoa tan — nuoc nong/say bien tinh → sat bam soi tao vet nau VINH VIEN. Muoi hut mau tuoi; enzyme protease cat chuoi protein; giat sau. Vai trang: oxy gia 3% them (test goc). Len/lua: KHONG enzyme/oxy — S1 trung tinh. CAM meo kem danh rang.',
   fresh_path_vi:'(1) Nhan: mau TUOI, vai nao. (2) Lat mat trai, xa LANH 2-3 phut den nuoc trong. (3) Ngam muoi an 2 muong canh/1 lit nuoc lanh 15-30 phut (sieu thi). (4) Con nhat: enzyme protease 15 phut (nhan enzyme; sieu thi) — KHONG len/lua (S1). (5) Giat nuoc giat thuong lanh. (6) Anh sang manh TRUOC say. KHONG cha manh.',
   dried_path_vi:'Neu kho: xu ly nhu mau kho — xem S_BLOOD_DRY. Neu con am: xa lanh mat trai truoc moi buoc.'},
  {id:'S_BLOOD_DRY',
   why_vi:'GIAO DUC: Mau kho = protein da gan soi. Can enzyme protease pha chuoi lau hon. Nhiet van CAM. Oxy gia 3% chi cotton trang sau test. Bao khach neu vet nau da khoa.',
   fresh_path_vi:'Neu con am: xu ly nhu mau tuoi — xa lanh mat trai truoc.',
   dried_path_vi:'(1) Cao nhe vay kho. (2) Ngam lanh 30-60 phut. (3) Enzyme protease pha loang 30-60 phut → chai mem. (4) Cotton TRANG: oxy gia 3% test goc 10 phut. (5) Len/lua: muoi + S1, KHONG enzyme/oxy. (6) Anh sang manh TRUOC say; con nau → lap enzyme.'},
  {id:'S_MOTORBIKE_OIL',
   why_vi:'GIAO DUC: Dau nhot xe may = dau kho + carbon. Buoc 1 hut (bot ngo/phan rom) → Buoc 2 dung moi tay dau (THONG GIO, khong lua) → Buoc 3 giat. Say khi con nhon = khoa vet. Silk/wool: khong dung moi manh/nhiet cao — bao khach.',
   fresh_path_vi:'(1) Nhan: dau nhot xe may, vai. (2) Bot ngo/phan rom day hut 10-30 phut, chai bot. Lap neu nhieu. (3) Dung moi tay dau cham mat trai (thong gio). (4) Con mau: con sat khuan nhe neu can (test). (5) Giat nuoc giat thuong cotton-poly. (6) Het nhon moi say.',
   dried_path_vi:'Bot hut 2 lan → dung moi lap → kiem tra het nhon truoc say. Khong silk/wool nhiet cao.'},
  {id:'S_BLACK_COFFEE',
   why_vi:'GIAO DUC: Ca phe den = tannin + mau. Xu ly SOM nuoc LANH — nhiet/say khoa mau. Giam trang 5% (1:4) pha tannin; con mau: bot tay oxy (khong len/lua). Neu ca phe SUA/latte: enzyme/nuoc rua chen TRUOC roi giam. CAM meo: kem danh rang, ethanol cocktail, giam 1:1.',
   fresh_path_vi:'(1) Nhan: ca phe den (khong sua), tuoi/kho, vai. (2) Tham/xa lanh mat trai (khong cha lan). (3) Giam trang 1:4 cham/xit 5-10 phut. (4) Con mau: bot tay oxy theo chai (trang/cotton; test). (5) Giat am nhe neu cho. (6) Anh sang manh truoc say.',
   dried_path_vi:'Giam trang ngam/cham → bot tay oxy neu con mau (KHONG len/lua) → kiem tra truoc say.'},
  {id:'S_MILK_COFFEE',
   why_vi:'GIAO DUC: Latte/ca phe sua = tannin + protein/mo sua. THU TU BAT BUOC: protein/mo (enzyme protease hoac nuoc rua chen) TRUOC → tannin (giam 1:4) SAU. Dao thu tu = mau khoa. Nhiet cao khoa protein.',
   fresh_path_vi:'(1) Nhan: latte/sua. (2) Xa lanh. (3) Enzyme protease (hoac nuoc rua chen neu mo) 15-30 phut. (4) Xa → giam trang 1:4. (5) Giat. (6) Oxy chi khi con mau + vai cho phep; test goc.',
   dried_path_vi:'Enzyme ngam lanh → giam trang → kiem tra truoc say; bot tay oxy neu can.'},
  {id:'S_FRUIT_JUICE',
   why_vi:'GIAO DUC: Juice = tannin + mau hoa qua (anthocyanin/carotenoid). SOM + lanh. Buoc1 giam 1:4. Buoc2 bot tay oxy neu con mau (trang/cotton OK; CAM len/lua). CAM say khoa mau.',
   fresh_path_vi:'(1) Nhan: juice/trai cay, trang/mau. (2) Tham/xa LANH mat trai. (3) Giam 1:4 cham/xit → tham. (4) Con mau: bot tay oxy (trang uu tien; test). (5) Giat am nhe. (6) CAM say khi con mau.',
   dried_path_vi:'Giam ngam → oxy neu can (khong len/lua) → anh sang manh truoc say. Vai mau: than trong oxy.'},
  {id:'S_KIMCHI',
   why_vi:'GIAO DUC: Kim chi/nuoc kim chi = bot ot (mau) + dau + muoi/acid. Xu ly SOM lanh. THU TU: cao bot → xa lanh → nuoc rua chen (dau) → giam 1:4 (mau/mui) → oxy CHI vai trang con mau. CAM say khoa mau ot. CAM meo kem danh rang.',
   fresh_path_vi:'(1) Cao bot ot/thuc an. (2) Xa/tham LANH mat trai. (3) Nuoc rua chen 1-2 giot cham ngoai→trong. (4) Xa → giam 1:4 5-10 phut. (5) Trang con mau: bot tay oxy (test). Mau: lap giam, than trong oxy. (6) Giat; KHONG say khi con vet.',
   dried_path_vi:'Ngam lanh + nuoc rua chen → giam → oxy neu trang. Mui: giam them + xa ky. Bao neu mau ot vin vien.'},
  {id:'S_KETCHUP',
   why_vi:'GIAO DUC: Ketchup = lycopene (mau ca chua) + duong + mang dau. Cao bot truoc. THU TU: nuoc rua chen (dau) → giam 1:4 (tannin/lycopene) → bot tay oxy neu trang con mau. Nhiet som khoa mau do.',
   fresh_path_vi:'(1) Cao bot ketchup. (2) Tham/xa lanh/mat am nhe. (3) Nuoc rua chen 1-2 giot ngoai→trong. (4) Xa → giam 1:4 5-10 phut. (5) Con mau trang: bot tay oxy (test). (6) Giat; CAM say khi con mau.',
   dried_path_vi:'Ngam + nuoc rua chen → giam lap → oxy neu trang. Bao khach neu mau do vin vien.'},
  {id:'S_TOMATO_SAUCE',
   why_vi:'GIAO DUC: Sot ca chua = lycopene + dau nau. Giong ketchup: cao → nuoc rua chen → giam → oxy trang. Khong cha lan mau do.',
   fresh_path_vi:'Cao → xa/tham → nuoc rua chen → giam 1:4 → oxy neu trang con mau → giat. CAM say khi con mau.',
   dried_path_vi:'Ngam + nuoc rua chen → giam → oxy trang neu can. Kiem tra truoc say.'},
  {id:'S_MAYO',
   why_vi:'GIAO DUC: Mayonnaise = dau (mo) + trung (protein). THU TU: cao → nuoc rua chen/lipase cho DAU TRUOC → enzyme protease cho PROTEIN. Dao thu tu = mo khoa protein. Nhiet cao khoa protein. Khong oxy truoc khi het mo.',
   fresh_path_vi:'(1) Cao bot mayo. (2) Nuoc rua chen 1-2 giot cham 5-10 phut (hoac enzyme lipase). (3) Xa. (4) Enzyme protease 15-30 phut neu con nhat trung. (5) Giat am nhe. (6) Het nhon moi say.',
   dried_path_vi:'Ngam lanh + nuoc rua chen → enzyme protease → giat. Lap neu con mo.'},
  {id:'S_COOKING_OIL',
   why_vi:'GIAO DUC: Dau an bam soi. Buoc1 hut (bot ngo/phan rom) → Buoc2 nuoc rua chen (surfactant) → Buoc3 enzyme lipase neu co. Say khi con nhon = khoa vet bong. Phan biet dau an vs dau nhot xe may.',
   fresh_path_vi:'(1) Bot ngo/phan rom day 10-30 phut, chai. (2) Nuoc rua chen 1-2 giot cham am nhe. (3) Enzyme lipase neu con nhon. (4) Giat. (5) Het nhon moi say.',
   dried_path_vi:'Hut bot 2 lan → nuoc rua chen/lapase → giat. Kiem tra nhon truoc say.'},
  {id:'S_GREASE',
   why_vi:'GIAO DUC: Mo/grease = lipid dam. Hut bot → nuoc rua chen + lipase. Khong say khi con mo.',
   fresh_path_vi:'Hut bot → nuoc rua chen → lipase neu can → giat. Het nhon moi say.',
   dried_path_vi:'Hut 2 lan → nuoc rua chen/lapase → giat. Bao neu mo cu kho.'},
  {id:'S_SOY_SAUCE',
   why_vi:'GIAO DUC: Nuoc tuong = protein len men + tannin/mau den. THU TU: xa lanh → enzyme protease → giam 1:4 → oxy neu trang con mau. Nhiet som khoa mau.',
   fresh_path_vi:'(1) Xa/tham LANH ngay. (2) Enzyme protease 15-30 phut. (3) Giam 1:4. (4) Trang con mau: bot tay oxy (test). (5) Giat. (6) CAM say khi con mau.',
   dried_path_vi:'Ngam lanh + enzyme → giam → oxy trang neu can. Anh sang manh truoc say.'},
  {id:'S_FISH_SAUCE',
   why_vi:'GIAO DUC: Nuoc mam = protein + muoi + mau. Mui man kho: giam deodorize. THU TU: xa lanh → enzyme → giam (mau+mui) → oxy trang neu can. Bao khach mui co the ton tai nhe.',
   fresh_path_vi:'(1) Xa LANH. (2) Enzyme protease 15-30 phut. (3) Giam 1:4 cham/ngam (mui). (4) Oxy neu trang con mau. (5) Giat xa ky. (6) CAM say khi con mau/mui manh.',
   dried_path_vi:'Ngam enzyme → giam lap (mui) → oxy trang neu can. Bao neu mui vin vien.'},
  {id:'S_COLLAR_STAIN',
   why_vi:'GIAO DUC: Vet co ao so mi = sebum + mo hoi + da chet oxy hoa → vang/xam. Enzyme (protease/lipase) len CO KHO truoc khi uot. CAM Javel/chlorine tren protein vang — lam VANG HON (tai lieu laundry cong nghiep). Sau do bot tay oxy. Ban chai mem thoi. CAM ui khi con vet.',
   fresh_path_vi:'(1) Nhan: vong co, ao so mi. (2) Nho enzyme protease/lipase len co KHO 5-15 phut. (3) Nuoc rua chen nhe neu mo. (4) Ngam bot tay oxy am (theo chai) 1-2 gio neu trang. (5) Giat. (6) Anh sang; con → lap. CAM chlorine.',
   dried_path_vi:'Enzyme paste dem neu cu → oxy ngam → giat. Bao khach vet rat cu co the con bong. CAM chlorine/ui khi con vet.'},
  {id:'S_SHIRT_YELLOW',
   why_vi:'GIAO DUC: Ao so mi trang vang toan than/co/tay = sebum+mo hoi oxy hoa + co the deodorant. KHONG dung chlorine (lam vang hon). THU TU: enzyme TRUOC → bot tay oxy ngam SAU. Soft brush. Lien quan vong co (S_COLLAR) neu chi co.',
   fresh_path_vi:'(1) Nhan: ao so mi trang vang (khong phai lo mau). (2) Enzyme protease/lipase pretreat vung vang. (3) Ngam bot tay oxy am theo chai 1-6 gio (test). (4) Giat detergent. (5) Anh sang manh; lap neu can. (6) CAM Javel; CAM say/ui khi con vang.',
   dried_path_vi:'Enzyme dem → oxy ngam dai → giat. Bao neu vang cu khong het 100%. Goi y tach rieng trang khi giat.'},
  {id:'S_DYE_TRANSFER',
   why_vi:'GIAO DUC: Lo mau / dye transfer = mau tu ao khac bam khi giat. XU LY NGAY — CAM say/ui (nhiet khoa mau). Bot tay oxy ngam dai (toi 6-8 gio theo chai) roi giat lai. Vai TRANG cotton: co the Javel pha loang CAN THAN. Vai mau/len/lua: CHI oxy + test; khong chlorine. Bao khach co the khong het 100%.',
   fresh_path_vi:'(1) Tach khoi may, KHONG say. (2) Phan biet trang vs mau, lua/len. (3) Ngam bot tay oxy theo chai (lanh/am) toi da theo nhan (thuong nhieu gio). (4) Giat detergent. (5) Anh sang; lap oxy neu can. (6) Trang cotton: Javel pha loang chi khi can + an toan vai. CAM say khi con mau lan.',
   dried_path_vi:'Neu da say: kho hon — van thu oxy ngam dai, bao khach ty le thanh cong thap. Khong chlorine tren mau/len/lua.'},
  {id:'S_STARCH_TRANSFER',
   why_vi:'GIAO DUC: Ho tinh bot (starch/풀) + mau lan: starch la mang giu mau. THU TU: enzyme amylase (phan tinh bot) TRUOC → bot tay oxy cho mau SAU. CAM say. Neu chi lo mau khong ho → xu ly nhu S_DYE_TRANSFER.',
   fresh_path_vi:'(1) Nhan: ho/풀 + mau lan. (2) Enzyme amylase (nuoc giat ghi tinh bot/amylase) ngam 15-60 phut. (3) Xa. (4) Bot tay oxy ngam. (5) Giat. (6) CAM say khi con mau.',
   dried_path_vi:'Amylase ngam → oxy → giat. Bao neu mau da say.'},
  {id:'S_MILDEW',
   why_vi:'GIAO DUC: Nam moc = nam + sac to. An toan: PPE, xu ly NGOAI TROI, chai/hut bot bao tu (CCI). Giam trang giet nam (acid). Bot tay oxy pha sac to. Javel CHI cotton trang + khong tron giam/ammonia. Oxy KHONG phai chat khu trung. CAM say khi con vet moc. Da/suede: chuyen chuyen nghiep.',
   fresh_path_vi:'(1) Dua ra ngoai, deo gang/khau trang neu nang. (2) Chai kho bot moc (khong hit). (3) Ngam giam trang pha (vd 1:4 den dam hon theo vai) nhieu gio. (4) Giat + bot tay oxy theo chai. (5) Trang cotton: Javel pha loang CHI neu an toan + KHONG tron giam. (6) Phoi nang/gio; CAM say khi con vet/mui.',
   dried_path_vi:'Chai ngoai troi → giam ngam → oxy → giat. Bao khach vet moc nang co the vin vien; da/len/lua can than hoac chuyen pro.'},
  {id:'S_LIPSTICK',
   why_vi:'GIAO DUC: Son moi = 3 lop: (1) sap ngoai — cao nhe, (2) dau giua — con isopropyl THAM mat trai (blot, khong cha), (3) pigment mau — nuoc rua chen roi bot tay oxy neu trang. THU TU BAT BUOC — bo qua sap hoac cha thay vi blot = that bai. Len/lua: test goc; co the chi D2 + S1. CAM say/ui khoa mau. Thong gio khi dung con.',
   fresh_path_vi:'(1) Nhan: son moi, tuoi/kho, vai (dac biet len/lua). (2) Test goc khuat voi con 70% truoc. (3) Cao bot sap ngoai→trong (thia mem, luc 2). (4) Lat mat trai, lot giay tham trang duoi → nho con mat trai vung vet → THAM thang dung (blot) 3-5 chu ky, doi khan sach moi chu ky — KHONG cha ngang. (5) Mat phai con mau: nuoc rua chen 1-2 giot, chai mem 45°. (6) Trang/cotton con mau: bot tay oxy (test). (7) Giat am nhe. (8) Anh sang manh TRUOC say.',
   dried_path_vi:'Neu da say/ui: ty le thap — van thu cao+con blot+oxy. Bao khach pigment co the vin vien. Len/lua: than trong hoac chuyen pro.'},
  {id:'S_FOUNDATION',
   why_vi:'GIAO DUC: Kem nen/cushion = dau nen + pigment. THAM nhe (blot) — KHONG cha lan. Nuoc rua chen cho dau TRUOC → con isopropyl cham cho mau neu can (test goc). Len/lua: chi S1 trung tinh + tham rat nhe. CAM say khi con mau.',
   fresh_path_vi:'(1) Nhan: kem nen/cushion/BB, vai. (2) Test goc voi con neu can. (3) THAM khan trang ngoai→trong — khong cha. (4) Nuoc rua chen pha loang nhe cham/xit 5-10 phut. (5) Xa → con cham mat trai neu con mau (test). (6) Trang: bot tay oxy neu can. (7) Giat/S1 neu len/lua. (8) CAM say khi con vet.',
   dried_path_vi:'Nuoc rua chen ngam → con blot → oxy trang neu can. Bao neu da say kho.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.why_vi = o.why_vi, s.fresh_path_vi = o.fresh_path_vi, s.dried_path_vi = o.dried_path_vi,
    s.tip = coalesce(o.why_vi, s.tip)
RETURN count(s) AS updated""")
        _r(s, "Z_paths_stage3_thin", """
UNWIND [
  {id:'S_LATERITE',
   why_vi:'GIAO DUC: Dat do laterite = sat oxit (Fe2O3) + set — KHONG giong bun thuong. CAM coi uot (lan mau). CAM Javel/B2 (co dinh sat VINH VIEN). THU TU: de KHO → chai bot → xa lanh → acid oxalic X2 (gang tay) tren cotton/linen/poly → xa → trung hoa N1 loang → A3 chelation neu can → B1 neu con mau (khong len/lua). Len/lua: KHONG X2 — A3/nuoc chanh nhe + bao khach.',
   fresh_path_vi:'(1) Nhan: dat do / laterite (mau do sat), vai. (2) De KHO hoan toan — CAM coi khi uot. (3) Chai kho bot ngoai troi (khau trang neu bui). (4) Xa LANH. (5) Cotton/linen/poly: acid oxalic X2 ~2-3% theo nhan, gang tay, ~30 phut (test goc). (6) Xa ky → N1 loang trung hoa. (7) Con mau: A3 pha roi B1 neu vai cho. (8) Len/lua: chi A3 nhe; bao chuyen pro neu nang. CAM B2. CAM say khi con mau do.',
   dried_path_vi:'Neu da giat/say som: ty le thap — van thu X2 (vai an toan) + trung hoa. Bao khach sat an sau kho het 100%.'},
  {id:'S_CURRY',
   why_vi:'GIAO DUC: Ca ri/nghe = dau + curcumin (mau vang kho). THU TU: nuoc rua chen (dau) TRUOC → baking soda/kiềm nhe → anh sang UV/phoi nang co kiem soat (curcumin phai mau) → bot tay oxy neu trang. CAM chi giat nuoc — dau giu mau. Len/lua: test; tranh oxy/nang manh.',
   fresh_path_vi:'(1) Nhan: ca ri/nghe, tuoi/kho, vai mau hay trang. (2) Cao bot. (3) Nuoc rua chen cham 5-10 phut (pha dau). (4) Xa → paste baking soda + it nuoc, de 15-30 phut. (5) Phoi nang ngan (kiem soat) neu curcumin con — hoac B1 tren trang/cotton (test). (6) Giat. (7) Anh sang manh TRUOC say. Len/lua: D2 + S1, khong B1.',
   dried_path_vi:'D2 ngam → N1 paste → B1 trang neu can. Bao khach mau nghe co the vin vien sau say.'},
  {id:'S_INK_PEN',
   why_vi:'GIAO DUC: Muc but bi = dye tan trong dung moi. CHI THAM/CHAM mat trai — cha = lan mau. Lot giay tham. Con isopropyl. Het muc moi say (nhiet khoa). Test goc. Len/lua: rat than; co the khong het 100%.',
   fresh_path_vi:'(1) Nhan: muc but, vai. (2) Test goc voi con 70%. (3) Lot giay tham duoi. (4) Lat mat trai — nho con, THAM thang dung, doi khan sach moi chu ky — KHONG cha. (5) Lap den het muc. (6) Giat lanh. (7) Anh sang manh TRUOC say.',
   dried_path_vi:'Con blot lap nhieu lan. Bao khach neu muc da say/ui — ty le thap.'},
  {id:'S_INK_PERMANENT',
   why_vi:'GIAO DUC: But long = polymer + pigment. A2 acetone hoac A1 — test vai (co the hong in/son). Thong gio. Khong cam ket 100%. CAM cha lan.',
   fresh_path_vi:'(1) Nhan: but long/permanent. (2) Test goc A2/A1. (3) Lot tham, cham mat trai, blot — khong cha. (4) Thong gio. (5) Giat sau khi het muc toi da. (6) Bao khach con vet co the. CAM say khi con muc.',
   dried_path_vi:'Lap A2/A1. Neu khong doi: bao chuyen pro / chap nhan vet.'},
  {id:'S_RUST',
   why_vi:'GIAO DUC: Ri set = sat oxit. CAM Javel (co dinh sat). Then chot: acid oxalic X2 + gang tay; xa + trung hoa N1. Cotton/linen/poly OK. Len/lua: KHONG X2 — A3/chanh nhe + bao. PPE.',
   fresh_path_vi:'(1) Nhan: ri set (nau do), vai. (2) Gang tay. (3) Cotton/linen/poly: X2 ~2-3% theo nhan ~15-30 phut (test). (4) Xa ky → N1 loang trung hoa. (5) Con mau: A3 roi B1 neu trang cho phep. (6) Len/lua: A3 nhe thoi. CAM B2. Anh sang TRUOC say.',
   dried_path_vi:'X2 (vai an toan) → trung hoa. Bao neu sat an sau.'},
  {id:'S_SWEAT_YELLOW',
   why_vi:'GIAO DUC: Ve o nach vang = mo hoi + protein + thuong deodorant/aluminum. CAM chlorine (vang hon). THU TU: enzyme (protein) TRUOC → bot tay oxy (vang) SAU. Giam pha neu can khu mui. Ao so mi toan than → xem S_SHIRT_YELLOW.',
   fresh_path_vi:'(1) Nhan: o nach vang, vai trang/mau. (2) Enzyme protease/lipase pretreat vung nach (kho) 15-30 phut — KHONG len/lua (S1). (3) Ngam B1 theo chai neu trang/cotton (test). (4) Giat. (5) Con mui: A3 1:4. (6) CAM Javel. Anh sang TRUOC say.',
   dried_path_vi:'Enzyme dem → B1 ngam dai → giat. Bao khach vet cu co the con bong.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.why_vi = o.why_vi, s.fresh_path_vi = o.fresh_path_vi, s.dried_path_vi = o.dried_path_vi,
    s.tip = coalesce(o.why_vi, s.tip)
RETURN count(s) AS updated""")
        _r(s, "Z2_kimchi_ops", """
MATCH (s:Stain {id:'S_KIMCHI'})
SET s.precheck_vi = 'Kim chi/nuoc kim chi — xu ly SOM. Phan biet vai trang vs mau. Test goc khuat truoc tay oxy.',
    s.motion_vi = 'Cao bot → tham/xa lanh mat trai ngoai→trong — khong cha lan mau ot',
    s.water_temp_vi = 'Bat dau nuoc LANH; sau do giat am nhe neu vai cho phep',
    s.aftercare_vi = 'Anh sang manh: con mau ot → lap (oxy chi vai trang). Phoi bong mat. CAM say khoa mau.',
    s.name_ko = '김치·김치국물'
RETURN count(s) AS updated""")
        _r(s, "Z3_edu_ops_ko", """
UNWIND [
  {id:'S_KETCHUP',name_ko:'케첩',precheck_vi:'Ketchup/tuong ca — cao bot, phan biet trang/mau'},
  {id:'S_TOMATO_SAUCE',name_ko:'토마토 소스',precheck_vi:'Sot ca chua — lycopene+dau'},
  {id:'S_MAYO',name_ko:'마요네즈',precheck_vi:'Mayo: dau TRUOC, protein SAU'},
  {id:'S_COOKING_OIL',name_ko:'식용유·오일(식용)',precheck_vi:'Dau an — khong nham dau nhot xe'},
  {id:'S_GREASE',name_ko:'기름때·그리즈',precheck_vi:'Mo — hut bot truoc'},
  {id:'S_SOY_SAUCE',name_ko:'간장',precheck_vi:'Nuoc tuong — enzyme roi giam'},
  {id:'S_FISH_SAUCE',name_ko:'느억맘·액젓',precheck_vi:'Nuoc mam — enzyme + giam mui'},
  {id:'S_COLLAR_STAIN',name_ko:'목때·칼라 황변',precheck_vi:'Vong co — CAM chlorine'},
  {id:'S_SHIRT_YELLOW',name_ko:'누렇게 된 와이셔츠',precheck_vi:'Ao so mi vang — enzyme roi oxy; CAM Javel'},
  {id:'S_DYE_TRANSFER',name_ko:'이염·물든 옷',precheck_vi:'Lo mau — CAM say; oxy ngam dai'},
  {id:'S_STARCH_TRANSFER',name_ko:'풀로 묻은 이염',precheck_vi:'Ho tinh bot + mau — amylase roi oxy'},
  {id:'S_MILDEW',name_ko:'곰팡이·곰팡이 제거',precheck_vi:'Nam moc — PPE ngoai troi; da/suede → pro'},
  {id:'S_BLOOD_FRESH',name_ko:'핏자국(신선)',precheck_vi:'Mau tuoi — CHI nuoc lanh'},
  {id:'S_BLOOD_DRY',name_ko:'핏자국(마른)',precheck_vi:'Mau kho — enzyme dai'},
  {id:'S_BLACK_COFFEE',name_ko:'커피(블랙)',precheck_vi:'Ca phe den — giam roi oxy'},
  {id:'S_MILK_COFFEE',name_ko:'라떼·우유커피',precheck_vi:'Ca phe sua — enzyme TRUOC giam'},
  {id:'S_FRUIT_JUICE',name_ko:'주스·과일즙',precheck_vi:'Juice — giam roi oxy'},
  {id:'S_MOTORBIKE_OIL',name_ko:'오토바이 오일',precheck_vi:'Dau nhot — thong gio khi dung moi'},
  {id:'S_LIPSTICK',name_ko:'립스틱·립스틱 자국',precheck_vi:'Son moi — 3 lop: sap→dau(con blot mat trai)→pigment. KHONG cha'},
  {id:'S_FOUNDATION',name_ko:'파운데이션·쿠션·화장품',precheck_vi:'Kem nen — blot; D2 roi con; len/lua → S1'},
  {id:'S_LATERITE',name_ko:'라테라이트·붉은 흙(적토)',precheck_vi:'Dat do — de KHO; CAM B2; X2 gang tay'},
  {id:'S_CURRY',name_ko:'카레·강황',precheck_vi:'Ca ri/nghe — D2 dau TRUOC, curcumin sau'},
  {id:'S_INK_PEN',name_ko:'볼펜·잉크',precheck_vi:'Muc but — blot mat trai A1; CAM cha'},
  {id:'S_INK_PERMANENT',name_ko:'유성매직·영구마커',precheck_vi:'But long — A2/A1 test; khong cam ket 100%'},
  {id:'S_RUST',name_ko:'녹·녹물',precheck_vi:'Ri set — X2 gang tay; CAM B2'},
  {id:'S_SWEAT_YELLOW',name_ko:'겨드랑이 황변',precheck_vi:'O nach vang — enzyme roi B1; CAM Javel'}
] AS x
MATCH (s:Stain {id:x.id})
SET s.name_ko = x.name_ko, s.precheck_vi = coalesce(x.precheck_vi, s.precheck_vi)
RETURN count(s) AS updated""")
        _r(s, "Z4_name_ko_remaining", """
UNWIND [
  {id:'S_EGG',name_ko:'계란·달걀 얼룩'},
  {id:'S_MILK',name_ko:'우유·유제품 얼룩'},
  {id:'S_VOMIT',name_ko:'토·구토물'},
  {id:'S_URINE',name_ko:'소변·오줌 얼룩'},
  {id:'S_FECES',name_ko:'대변·분변 오염'},
  {id:'S_BABY_FORMULA',name_ko:'분유 얼룩'},
  {id:'S_GRASS',name_ko:'잔디·풀물'},
  {id:'S_MUD',name_ko:'진흙·흙탕물'},
  {id:'S_CHOCOLATE',name_ko:'초콜릿'},
  {id:'S_BUTTER',name_ko:'버터'},
  {id:'S_ENGINE_OIL',name_ko:'엔진오일·기계유'},
  {id:'S_SHOE_POLISH',name_ko:'구두약'},
  {id:'S_CANDLE_WAX',name_ko:'양초·촛농'},
  {id:'S_GUM',name_ko:'껌'},
  {id:'S_DEODORANT',name_ko:'데오드란트·땀억제제 얼룩'},
  {id:'S_PAINT_LATEX',name_ko:'수성 페인트'},
  {id:'S_TEA',name_ko:'차·녹차·홍차'},
  {id:'S_RED_WINE',name_ko:'레드와인'},
  {id:'S_WHITE_WINE_BEER',name_ko:'화이트와인·맥주'},
  {id:'S_SOFT_DRINK',name_ko:'탄산음료·콜라'},
  {id:'S_MUSTARD',name_ko:'머스터드·겨자'},
  {id:'S_GLUE',name_ko:'접착제·본드'},
  {id:'S_NAIL_POLISH',name_ko:'매니큐어·네일'},
  {id:'S_SWEAT_FRESH',name_ko:'땀(신선)·땀냄새'},
  {id:'S_PERFUME',name_ko:'향수·알코올 스프레이'}
] AS x
MATCH (s:Stain {id:x.id})
SET s.name_ko = coalesce(s.name_ko, x.name_ko)
RETURN count(s) AS updated""")
        _r(s, "Z6_bubble_tea_path", """
MATCH (s:Stain {id:'S_BUBBLE_TEA'})
SET s.name_ko = '버블티·밀크티·타피오카',
    s.precheck_vi = 'Tra sua tran chau: 4 lop (tannin + protein sua + tinh bot + duong). CAM nuoc nong dau. Cao tran chau.',
    s.why_vi = 'GIAO DUC: Bubble tea = tannin tra + protein sua + tinh bot san + duong. THU TU: xa LANH → enzyme (protein+tinh bot) → D2 (mo sua) → A3 (tannin) → B1 neu trang. Bo enzyme = kem hieu qua.',
    s.fresh_path_vi = '(1) Cao/bo tran chau. (2) Xa LANH ngay. (3) Enzyme E1/E2 ngam lanh 15-30 phut. (4) D2 1-2 giot cham. (5) A3 1:4 ~15 phut. (6) Giat; con mau trang → B1. CAM say khi con vet.',
    s.dried_path_vi = 'Ngam enzyme dai → D2 → A3 → B1 trang. Duong kho de vang — B1 phong.',
    s.motion_vi = 'Tham ngoai→trong; khong cha lan',
    s.water_temp_vi = 'LANH luc dau; sau do ~40C neu vai cho',
    s.aftercare_vi = 'Anh sang truoc say. Phoi bong mat.',
    s.tip = coalesce(s.why_vi, s.tip)
RETURN count(s) AS updated""")
        _r(s, "Z7_paths_drinks_rich", """
UNWIND [
  {id:'S_TEA',
   why_vi:'GIAO DUC: Nuoc tra (den/xanh/oolong) = tannin + mau. Xu ly SOM + nuoc LANH — nhiet/say khoa mau vang-nau. THU TU: xa lanh → giam trang 1:4 (pha tannin) → bot tay oxy neu trang/cotton con mau. CAM len/lua + B1. Duong trong tra da kho de vang — bao khach.',
   fresh_path_vi:'(1) Nhan: tra (den/xanh), tuoi/kho, vai. (2) Xa/tham LANH mat trai ngoai→trong — khong cha. (3) A3 1:4 xit/ngam 5-15 phut. (4) Xa. (5) Con mau trang/cotton: B1 theo chai 15-45 phut (test). (6) Giat. (7) Anh sang TRUOC say. Len/lua: A3 nhe + S1, khong B1.',
   dried_path_vi:'A3 ngam dai → B1 trang neu can. Bao neu da say: ty le thap.',
   force_metaphor_vi:'Cap1–2: tham nhe nhu lau kinh — cha lan tannin',
   force_metaphor_ko:'Cap1–2: 안경 닦듯 흡수 — 문지르면 탄닌 번짐',
   sense_check_vi:'Mat: mau nhat. Mui: het mui tra. Anh sang: khong vet.',
   sense_check_ko:'눈: 색 옅어짐. 코: 찻물 냄새 감소. 강광: 잔존 없음.',
   success_rate_vi:'Tuoi+lanh: cao. Da say: thap — bao truoc.',
   success_rate_ko:'신선·찬물: 높음. 건조 후: 낮음 — 사전 고지.',
   refuse_when_vi:'Khach doi 100% tren lua/len sau say → tu choi cam ket.',
   refuse_when_ko:'실크·울·건조 후 100% 요구 → 보장 거절.'},
  {id:'S_RED_WINE',
   why_vi:'GIAO DUC: Ruou vang do = anthocyanin + tannin + acid/duong. SOM + LANH. Muoi/tham hut bot neu rat tuoi (tuy chon) → giam 1:4 → oxy trang neu can. CAM say khoa mau do-tim. Vai mau: test; khong Javel.',
   fresh_path_vi:'(1) Nhan: ruou vang do, tuoi. (2) Tham/hut bot (muoi hoac giay) ngoai→trong — khong cha. (3) Xa lanh. (4) A3 1:4 5-15 phut. (5) Trang/cotton con mau: B1. (6) Giat lanh/am nhe. (7) Anh sang TRUOC say.',
   dried_path_vi:'A3 ngam → B1 trang. Bao mau da khoa sau say co the vin vien.',
   force_metaphor_vi:'Cap1: tham hut — khong cha lan mau do',
   force_metaphor_ko:'Cap1: 흡수만 — 문지르면 붉은 색소 확산',
   sense_check_vi:'Mat: mau do nhat. Anh sang truoc say.',
   sense_check_ko:'눈: 붉은색 감소. 건조 전 강광 확인.',
   success_rate_vi:'Xu ly trong 1 gio: tot. Qua dem/say: thap.',
   success_rate_ko:'1시간 내: 양호. 하룻밤·건조 후: 낮음.',
   refuse_when_vi:'Lua mong / in hoa — test fail thi dung oxy.',
   refuse_when_ko:'얇은 실크·프린트 — 테스트 실패 시 산소표백 중단.'},
  {id:'S_WHITE_WINE_BEER',
   why_vi:'GIAO DUC: Ruou vang trang/bia = tannin nhe + duong/men — moi co the GIAN (khong thay) roi VANG sau. Xu ly SOM du khong thay mau. Lanh → giam nhe → giat. Trang: oxy phong vang. CAM say khi nghi con duong.',
   fresh_path_vi:'(1) Nhan: trang/bia, tuoi (co the trong). (2) Xa lanh ngay. (3) A3 1:4 nhe 5-10 phut. (4) Giat. (5) Trang: B1 ngan neu so vang. (6) Anh sang / de kho bong mat.',
   dried_path_vi:'Vang sau: A3 roi B1 trang. Bao duong kho gay vang cham.',
   force_metaphor_vi:'Cap1–2: xu ly som du khong thay mau',
   force_metaphor_ko:'Cap1–2: 안 보여도 즉시 처리 (나중에 황변)',
   sense_check_vi:'Mui men giam; anh sang khong bong vang.',
   sense_check_ko:'발효 냄새 감소; 강광에서 노란 기미 없음.',
   success_rate_vi:'Som: cao. Vang sau tuan: trung binh.',
   success_rate_ko:'즉시: 높음. 며칠 후 황변: 중간.',
   refuse_when_vi:'Khong cam ket trang 100% neu da vang lau.',
   refuse_when_ko:'오래된 황변 100% 복원 비보장.'},
  {id:'S_SOFT_DRINK',
   why_vi:'GIAO DUC: Nuoc ngot/cola = duong + mau/acid (cola: caramel mau + phosphoric). Duong kho = dinh + vang. SOM xa lanh → giam neu mau → oxy trang. CAM say khi con ngot/dinh.',
   fresh_path_vi:'(1) Nhan: cola/nuoc ngot, tuoi. (2) Xa/tham lanh. (3) A3 1:4 5-10 phut neu mau. (4) Xa. (5) Trang con mau/vang: B1. (6) Giat. (7) Anh sang TRUOC say.',
   dried_path_vi:'Ngam am nhe + A3 → B1 trang. Bao dinh duong kho kho.',
   force_metaphor_vi:'Cap1–2: xa het ngot truoc khi say',
   force_metaphor_ko:'Cap1–2: 단맛·점성 없앤 뒤 건조',
   sense_check_vi:'Tay: het dinh. Mui: het ngot. Mat: mau nhat.',
   sense_check_ko:'손: 끈적임 없음. 코: 단맛 감소. 눈: 색소 감소.',
   success_rate_vi:'Tuoi: cao. Kho dinh: can ngam dai.',
   success_rate_ko:'신선: 높음. 마른 당분: 장시간 침지 필요.',
   refuse_when_vi:'Vai mau nhay — test truoc B1.',
   refuse_when_ko:'예민 유색 원단 — 산소표백 전 테스트.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.why_vi = o.why_vi, s.fresh_path_vi = o.fresh_path_vi, s.dried_path_vi = o.dried_path_vi,
    s.tip = coalesce(o.why_vi, s.tip),
    s.force_metaphor_vi = o.force_metaphor_vi, s.force_metaphor_ko = o.force_metaphor_ko,
    s.sense_check_vi = o.sense_check_vi, s.sense_check_ko = o.sense_check_ko,
    s.success_rate_vi = o.success_rate_vi, s.success_rate_ko = o.success_rate_ko,
    s.refuse_when_vi = o.refuse_when_vi, s.refuse_when_ko = o.refuse_when_ko
RETURN count(s) AS updated""")
        _r(s, "Z8_paths_biohazard_rich", """
UNWIND [
  {id:'S_VOMIT',
   why_vi:'GIAO DUC: Chat non = acid da day + protein thuc an + mat (bile mau vang/xanh) + virus/vi khuan. BAT BUOC gang tay (T_GLOVE). CAM nuoc nong (khoa protein). THU TU: cao ran → xa LANH → enzyme E1 → A3 (mui/acid) → B1 neu trang con mau. Khong mo ta chi tiet truoc mat khach — noi "vet huu co".',
   fresh_path_vi:'(1) PPE: gang tay day + khau trang neu mui nang; khu vuc thong gio. (2) Cao toan bo chat ran vao tui — KHONG cha. (3) Xa LANH mat trai ngoai→trong. (4) E1 ngam lanh 30-45 phut (nong do cao hon thuong). (5) Xa; A3 1:4 ~15 phut khu mui/acid. (6) Giat; trang/cotton con mau: B1. (7) Phoi nang neu duoc (UV). Anh sang TRUOC say.',
   dried_path_vi:'E1 ngam dai/qua dem → A3 → B1 trang. Bao ty le thap neu da say khoa mau mat.',
   force_metaphor_vi:'Cap2: cao nhe + tham — khong cha day acid vao soi',
   force_metaphor_ko:'Cap2: 긁어내고 흡수 — 문지르면 위산·잔여물이 섬유로 침투',
   sense_check_vi:'Mat: het manh thuc an. Mui: het mui non (enzyme/giam). Tay(gang): vai mem.',
   sense_check_ko:'눈: 음식물 잔여 없음. 코: 구토 냄새 감소. 손(장갑): 천 부드러움.',
   success_rate_vi:'Xu ly SOM + PPE dung: 60-80%. Da say/lua: thap.',
   success_rate_ko:'즉시+PPE: 60–80%. 건조·실크: 낮음.',
   refuse_when_vi:'Khong gang tay → dung. Lua/len vet lon → dry clean. Khach doi 100% sau say → bao truoc.',
   refuse_when_ko:'장갑 없이 작업 금지. 실크·울 대량 → 드라이. 건조 후 100% 요구 → 사전 고지 거절.'},
  {id:'S_URINE',
   why_vi:'GIAO DUC: Nuoc tieu tuoi = urea+muoi (de). KHO = vi khuan → ammonia + uric acid (khong tan nuoc thuong) → mui khai + vang. BAT BUOC gang. CAM A5 ammonia (cong mui). CAM B2+ammonia (khi doc). THU TU: tham/xa lanh → E1 (pha uric) → A3 trung hoa → B1 neu vang trang.',
   fresh_path_vi:'(1) Gang tay. (2) Tham hut toi da Cap1 ngoai→trong. (3) Xa LANH mat trai. (4) E1 ngam 30 phut. (5) Giat lanh/am. (6) Kiem tra mui khi uot + anh sang (vang).',
   dried_path_vi:'(1) Ngam lanh 15 phut. (2) E1 nong do cao 45-60 phut — buoc QUAN TRONG (uric). (3) A3 1:4 ~30 phut. (4) Tuy chon N1 khu mui. (5) Giat + B1 trang neu vang. (6) Phoi nang. Dem/tham: spot E1+A3+N1 — khong giat may chung.',
   force_metaphor_vi:'Cap1 tuoi (chi tham); Cap2 kho (enzyme dai) — khong cha manh',
   force_metaphor_ko:'신선 Cap1 흡수만; 마른 후 Cap2 효소 장침지 — 세게 문지르지 말 것',
   sense_check_vi:'Mui: het khai khi uot. Mat: khong vang. Tay: vai mem.',
   sense_check_ko:'코: 젖은 상태에서도 암모니아 냄새 없음. 눈: 황변 없음. 손: 천 부드러움.',
   success_rate_vi:'Tuoi: cao (~80%). Kho dem/tham: ~50% — bao truoc.',
   success_rate_ko:'신선: 높음(~80%). 마른 매트리스: ~50% — 사전 고지.',
   refuse_when_vi:'CAM A5/B2 voi ammonia. Khong cam ket 100% mui cu tren nem.',
   refuse_when_ko:'암모니아(A5)·염소(B2) 금지(가스 위험). 오래된 매트리스 냄새 100% 비보장.'},
  {id:'S_FECES',
   why_vi:'GIAO DUC: Phan = protein + vi khuan (nguy co cao) + sac to mat (bile) kho tay. PPE NANG: gang day + khau trang + khu rieng + sat khuan ban. CAM tron voi do sach. CAM nong luc dau. THU TU: cao ran → xa lanh → E1 cao → B1 mau mat → giat nhiet cao an toan + UV.',
   fresh_path_vi:'(1) Gang day + khau trang; niem lot ban. (2) Cao het chat ran vao tui — Cap2, ngoai→trong, KHONG cha. (3) Xa LANH manh mat trai. (4) E1 nong do cao 45-60 phut. (5) Con mau vang-nau: B1 1-2 gio (sau protein). (6) Giat nhiet cao nhat an toan vai. (7) Phoi nang. Sat khuan dung cu + ban.',
   dried_path_vi:'E1 qua dem → B1 dai → trang cotton co the B2 pha loang SAU protein (test). Bao mau mat co the con nhe.',
   force_metaphor_vi:'Cap2: cao sach truoc — cha khi uot = lan sau',
   force_metaphor_ko:'Cap2: 고체 먼저 제거 — 젖은 채 문지르면 번짐·심부 침투',
   sense_check_vi:'Mat: het ran + mau nhat. Mui: het. Sau: ban/dung cu da sat khuan.',
   sense_check_ko:'눈: 고체 없음·색 옅음. 코: 냄새 없음. 작업대·도구 소독 완료.',
   success_rate_vi:'Protein sach: tot; mau mat: ~65% — bao truoc.',
   success_rate_ko:'단백질 제거: 양호; 담즙 색소: ~65% — 사전 고지.',
   refuse_when_vi:'Lua/len → dry clean. Khong PPE → dung. Khong giat chung do sach.',
   refuse_when_ko:'실크·울 → 드라이. PPE 없이 작업 금지. 청결 세탁물과 혼합 금지.'},
  {id:'S_BABY_FORMULA',
   why_vi:'GIAO DUC: Sua bot = casein/whey + mo thuc vat + SAT (iron) + lactose. Kho hon sua tuoi. CAM B2 (chlorine + sat = vet CAM VINH VIEN). CAM nong luc dau (khoa sat+protein). THU TU: cao → xa lanh → D2 (mo) → E1 (protein) → A3 neu vang/cam (sat) → giat am nhe. Phoi nang tot cho do be.',
   fresh_path_vi:'(1) Cao sua dac. (2) Xa LANH mat trai. (3) D2 2-4 giot massage nhe Cap2. (4) Xa. (5) E1 ngam lanh 30-45 phut. (6) Con vang/cam: A3 (giam) 15 phut len vet. (7) Giat 30-35C. (8) Anh sang TRUOC say; phoi nang OK.',
   dried_path_vi:'Ngam E1 dai → D2 → A3 cho sat. VAN CAM B2. Bao neu da giat nong/B2: vet cam kho phuc.',
   force_metaphor_vi:'Cap2: D2 truoc E1 — mo thuc vat bam dai',
   force_metaphor_ko:'Cap2: D2(유분)→E1(단백질) 순서 — 분유 식물성 지방이 끈김',
   sense_check_vi:'Tay: het dinh/tron. Mat: het trang sua + khong cam. Mui: het chua.',
   sense_check_ko:'손: 끈적·미끄럼 없음. 눈: 분유 잔여·주황 기미 없음. 코: 신내 없음.',
   success_rate_vi:'SOM + dung thu tu: cao. Da B2/nong: sat cam — thap.',
   success_rate_ko:'즉시·정석 순서: 높음. 이미 B2·온수: 철분 주황 — 낮음.',
   refuse_when_vi:'Khach da dung Javel/B2 → bao vet cam co the vinh vien.',
   refuse_when_ko:'이미 락스(B2) 사용 → 주황 반점 영구 가능 고지.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.why_vi = o.why_vi, s.fresh_path_vi = o.fresh_path_vi, s.dried_path_vi = o.dried_path_vi,
    s.tip = coalesce(o.why_vi, s.tip),
    s.force_metaphor_vi = o.force_metaphor_vi, s.force_metaphor_ko = o.force_metaphor_ko,
    s.sense_check_vi = o.sense_check_vi, s.sense_check_ko = o.sense_check_ko,
    s.success_rate_vi = o.success_rate_vi, s.success_rate_ko = o.success_rate_ko,
    s.refuse_when_vi = o.refuse_when_vi, s.refuse_when_ko = o.refuse_when_ko
RETURN count(s) AS updated""")
        _r(s, "Z9_paths_specialty_oil_rich", """
UNWIND [
  {id:'S_ENGINE_OIL',
   why_vi:'GIAO DUC: Dau dong co = hydrocarbon + carbon den — kho nhat nhom dau. THONG GIO bat buoc khi dung moi (D1). THU TU: cao dac → N3 hut (lap) → D1 xit + tham (giay duoi) → A1 cham mau con (test) → D3 giat nong neu cotton/poly. CAM say khi con nhon. Lua/len: khong buoc nong.',
   fresh_path_vi:'(1) PPE + thong gio. (2) Cao phan dac Cap2 ngoai→trong. (3) N3 phu day 30 phut; phui; lap den bot it den. (4) D1 xit + vo sol Cap3, giay tham duoi — lap 2-3 lan. (5) A1 cham vet mau con (test goc). (6) D2/D3 giat; cotton/poly ~40-60C neu cho. (7) Anh sang TRUOC say.',
   dried_path_vi:'N3+D1 lap nhieu lan. Bao ty le thap neu da say khoa carbon.',
   force_metaphor_vi:'Cap1 N3 → Cap3 D1 — khong cha lan den',
   force_metaphor_ko:'Cap1 흡착분→Cap3 용제 — 검정 오일 번지게 문지르지 말 것',
   sense_check_vi:'Tay: het nhon. Mat: bot N3 it den. Mui: het dau (con mui moi tam).',
   sense_check_ko:'손: 미끄럼 없음. 눈: N3 검게 덜함. 코: 오일 냄새 감소.',
   success_rate_vi:'Lap 2-4 lan: trung binh-cao. Da say den: thap.',
   success_rate_ko:'2–4회 반복: 중~높음. 건조 후 검정 고착: 낮음.',
   refuse_when_vi:'Khong thong gio + dung moi. Lua/len vet lon → chuyen. Khong cam ket 100% carbon.',
   refuse_when_ko:'환기 없이 용제 금지. 실크·울 대량 → 전문. 탄소 잔여 100% 비보장.'},
  {id:'S_GUM',
   why_vi:'GIAO DUC: Keo cao su = polymer dan — DONG LANH la chia khoa. Am = dinh lai. THU TU: tui nilon + tu dong 30-60 phut → be/cao ngay khi gion → A2 it neu can dau (CAM acetate/rayon) → D2 giat. Khong ui nong len keo.',
   fresh_path_vi:'(1) Cho vao tui, dong 30-60 phut den CUNG. (2) Lay ra, be/cao Cap2 NHANH. (3) Con can: dong lai neu can. (4) Can dau: A2 rat it Cap1 (test; CAM acetate). (5) D2 + giat am. (6) Kiem tra TRUOC say.',
   dried_path_vi:'Dong lai + be. Neu da ui nong: kho hon — bao truoc.',
   force_metaphor_vi:'Cap2 be khi gion — am = dinh lai',
   force_metaphor_ko:'Cap2: 얼려 바삭할 때 깨기 — 따뜻하면 다시 붙음',
   sense_check_vi:'Tay: het dan/gion. Mat: het manh keo.',
   sense_check_ko:'손: 끈적임 없음. 눈: 껌 조각 없음.',
   success_rate_vi:'Dong dung cach: cao. Da ui/am: trung binh.',
   success_rate_ko:'냉동 정석: 높음. 이미 다림질·따뜻: 중간.',
   refuse_when_vi:'Acetate/rayon + A2 → dung. Vai mong de rach khi cao → bao.',
   refuse_when_ko:'아세테이트/레이온+아세톤 금지. 얇은 원단 긁힘 위험 고지.'},
  {id:'S_CANDLE_WAX',
   why_vi:'GIAO DUC: Sap nen = sap + mau (neu mau). DONG/pha vo sap TRUOC — roi UI thap qua giay tham hut sap. Sau do D2/D1 neu can dau. CAM ui truc tiep khong giay (lan mau).',
   fresh_path_vi:'(1) De kho/dong ngan → be/cao Cap1-2. (2) Dat giay tham 2 mat → ui nhiet THAP di chuyen — doi giay khi tham sap. (3) Con dau: D2 Cap2 hoac D1 nhe + thong gio. (4) Mau con tren trang: B1 (test). (5) Giat. (6) Anh sang TRUOC say.',
   dried_path_vi:'Lap ui+giay. Mau khoa: bao ty le mau thap.',
   force_metaphor_vi:'Cap1 cao + ui qua giay — khong cha sap am',
   force_metaphor_ko:'Cap1 긁기 + 종이 사이 저온 다림질 — 따뜻한 왁스 문지르기 금지',
   sense_check_vi:'Tay: het sap cung. Mat: giay khong con hut sap.',
   sense_check_ko:'손: 왁스 딱딱함 없음. 눈: 종이에 더 이상 왁스 안 옮음.',
   success_rate_vi:'Sap trong: cao. Mau nen dam: trung binh.',
   success_rate_ko:'무색 왁스: 높음. 진한 색소 양초: 중간.',
   refuse_when_vi:'Lua mong / in hoa — ui test goc; fail thi chuyen.',
   refuse_when_ko:'얇은 실크·프린트 — 구석 다림질 테스트 실패 시 전문.'},
  {id:'S_DEODORANT',
   why_vi:'GIAO DUC: Vet trang khu mui = tinh the muoi nhom (Al). A3 (giam) hoa tan Al3+. CAM B2 (chlorine) — vang VINH VIEN. Neu vang nach (mo+protein): B1/enzyme sau khi trang sach — khac protocol trang.',
   fresh_path_vi:'(1) Nhan: trang (muoi Al) hay vang nach. (2) Trang: A3 nguyen/loang thoa 10-15 phut Cap2. (3) Them D2 massage + xa. (4) Giat ~40C. (5) CAM B2. (6) Vang nach: sau do B1/E1 theo vai (test).',
   dried_path_vi:'A3 dai hon. Da dung Javel → bao vang co the vinh vien.',
   force_metaphor_vi:'Cap2 massage A3 — khong B2',
   force_metaphor_ko:'Cap2: 식초로 문지르듯 — 염소(B2) 절대 금지',
   sense_check_vi:'Mat: het bot trang. Tay: het ron sap. CAM B2.',
   sense_check_ko:'눈: 흰 가루 잔여 없음. 손: 왁스감 없음. B2 금지 확인.',
   success_rate_vi:'Vet trang: cao. Vang nach cu: trung binh.',
   success_rate_ko:'흰 잔여: 높음. 오래된 겨드랑이 황변: 중간.',
   refuse_when_vi:'Khach da B2 → bao vang. Lua: A3 nhe + test.',
   refuse_when_ko:'이미 B2 → 황변 고지. 실크: 식초 약하게+테스트.'},
  {id:'S_PERFUME',
   why_vi:'GIAO DUC: Nuoc hoa = con + tinh dau + mau — de VANG vai trang theo thoi gian. Xu ly SOM. THU TU: xa/tham → A3 1:4 ngam → giat. Trang: theo doi vang; B1 phong neu can. CAM say khi con con/dau thom dam.',
   fresh_path_vi:'(1) Nhan: moi xa. (2) Tham/xa lanh Cap1. (3) A3 1:4 15-30 phut. (4) Giat. (5) Trang so vang: B1 ngan (test). (6) Phoi bong mat — anh sang kiem tra vang.',
   dried_path_vi:'Vang sau: A3 → B1 trang. Bao kho phuc 100% neu da oxi hoa.',
   force_metaphor_vi:'Cap1 tham — khong cha lan mau/con',
   force_metaphor_ko:'Cap1 흡수 — 문지르면 색소·알코올 번짐',
   sense_check_vi:'Mui: het nuoc hoa dam. Mat: khong bong vang moi.',
   sense_check_ko:'코: 진한 향 감소. 눈: 새 황변 없음.',
   success_rate_vi:'Som: cao. Vang cu trang: thap-trung binh.',
   success_rate_ko:'즉시: 높음. 오래된 흰옷 황변: 낮~중.',
   refuse_when_vi:'Khong cam ket trang 100% sau vang lau. Lua: test A3.',
   refuse_when_ko:'오래된 황변 100% 복원 비보장. 실크: 식초 테스트.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.why_vi = o.why_vi, s.fresh_path_vi = o.fresh_path_vi, s.dried_path_vi = o.dried_path_vi,
    s.tip = coalesce(o.why_vi, s.tip),
    s.force_metaphor_vi = o.force_metaphor_vi, s.force_metaphor_ko = o.force_metaphor_ko,
    s.sense_check_vi = o.sense_check_vi, s.sense_check_ko = o.sense_check_ko,
    s.success_rate_vi = o.success_rate_vi, s.success_rate_ko = o.success_rate_ko,
    s.refuse_when_vi = o.refuse_when_vi, s.refuse_when_ko = o.refuse_when_ko
RETURN count(s) AS updated""")
        # Priority 1–2 item care — same field names as stain paths (owner 1)-6) flow)
        _r(s, "I_items_care", """
UNWIND [
  {id:'I_LEATHER_GARMENT',name:'Leather garment',name_vi:'Ao/quan da bong',name_ko:'가죽 의류(무지/매끈 가죽)',fabric_id:'F8',
   precheck_vi:'Phan biet da bong vs suede. CAM may giat. Test goc khuat truoc khi dung con.',
   why_vi:'Da bong: it nuoc toi da; may giat/nhiet/tay oxy = hong. Sau xu ly can boi kem da.',
   fresh_path_vi:'Khan am nhe lau → kho. Vet: khan + con sat khuan 70% CHAM nhe (test). CAM tay oxy. Roi boi kem da.',
   dried_path_vi:'Vet cu/nam: chai/kho khan → con nhe neu can. Sau long/dien rong → chuyen chuyen nghiep. CAM may.',
   motion_vi:'Luc 1 — chi tham/lau, khong cha manh',
   water_temp_vi:'It nuoc, nhiet phong. KHONG ngam may.',
   aftercare_vi:'Phoi bong mat. Boi kem da. KHONG say may, KHONG nang gay.'},
  {id:'I_SUEDE_GARMENT',name:'Suede garment',name_vi:'Ao/quan da lon (suede/nubuck)',name_ko:'스웨이드·누벅 의류',fabric_id:'F9',
   precheck_vi:'Be mat nhung = suede. CAM nuoc. Uot → chuyen ngay.',
   why_vi:'Suede + nuoc = vet vinh vien. Chi chai kho / tay kho. CAM may, CAM tay oxy.',
   fresh_path_vi:'Chai suede kho ngoai→trong. Vet dau nhe: tay kho (gom). Khong het → chuyen.',
   dried_path_vi:'Khong ngam. Bao khach chuyen chuyen nghiep neu uot/nam sau long.',
   motion_vi:'Luc 1 — chai kho nhe theo chieu long',
   water_temp_vi:'KHONG dung nuoc',
   aftercare_vi:'De kho bong mat. KHONG say/ui. Thong bao khach neu con vet.'},
  {id:'I_LEATHER_BAG',name:'Leather bag',name_vi:'Tui da / vi da',name_ko:'가죽 가방·지갑',fabric_id:'F8',
   precheck_vi:'Lay het do trong tui. Da/PU: it nuoc. Dat tien / khong chac → tu choi xu ly sau.',
   why_vi:'Tui da: it nuoc, dung dich da. CAM may giat/say (hong hinh).',
   fresh_path_vi:'Lau khan am nhe → kho. Vet: spotting nhe dung dich da / con test goc. Boi kem da.',
   dried_path_vi:'Khong ngam. Sau xu ly giu hinh, phoi bong mat.',
   motion_vi:'Luc 1 — lau/tham, khong ngam',
   water_temp_vi:'It nuoc, nhiet phong',
   aftercare_vi:'Phoi boi hinh. KHONG say. Boi kem da neu can.'},
  {id:'I_SUEDE_BAG',name:'Suede bag',name_vi:'Tui da lon / suede',name_ko:'스웨이드 가방',fabric_id:'F9',
   precheck_vi:'Suede tui: CAM nuoc. Dat tien → chuyen chuyen nghiep.',
   why_vi:'Suede tui + nuoc = vet. Chi chai kho / chuyen.',
   fresh_path_vi:'Chai kho. Khong het → chuyen. CAM may.',
   dried_path_vi:'Tu choi ngam/may. Bao khach chuyen.',
   motion_vi:'Luc 1 — chai kho',
   water_temp_vi:'KHONG nuoc',
   aftercare_vi:'Kho bong mat. KHONG say.'},
  {id:'I_SNEAKER',name:'Sneaker / sport shoe',name_vi:'Giay sneaker / the thao (vai/canvas)',name_ko:'스니커즈·일반 운동화(천·캔버스)',fabric_id:'F2',
   precheck_vi:'Phan loai chat lieu TRUOC. Thao DAY + LOT rieng. Chai kho bun/dat ngoai troi. May: tui luoi + dem khan. Chup anh vet/keo long truoc xu ly.',
   why_vi:'Sneaker: CAM say nhiet cao (keo/mui xop hong). Nuoc <=30C, chat giat TRUNG TINH it. Kiềm manh de gay VANG de trang. Day/lot giat RIENG.',
   fresh_path_vi:'(1) Chai kho. (2) Spotting: than giay=sol MEM + nuoc rua chen/pha loang; de cao su=sol CUNG nhe. (3) Ngam ngan <=10-30 phut neu can. (4) Giat tay hoac may tui luoi 30C. (5) Xa ky — ton du kiềm gay vang. (6) Nhet bao/khan, phoi BONG MAT.',
   dried_path_vi:'Vet bun: paste bot giat + baking soda + it nuoc, chai, xa. Canh trang/midsole den: lap spotting trung tinh, KHONG hao danh 100%. Tranh nang gay (vang).',
   motion_vi:'Than/luoi: luc 2 sol mem mot chieu. De cao su: luc 2-3 sol cung. Khong cha ngang mau phoi mau.',
   water_temp_vi:'<=30C. Khong nuoc nong.',
   aftercare_vi:'CAM say may nong. Say khi/quat + nhet bao. Kho HAN moi mang. Doi bao khi am.'},
  {id:'I_RUNNING_MESH',name:'Mesh running shoe',name_vi:'Giay chay bo luoi / mesh',name_ko:'러닝화·망사(메시) 운동화',fabric_id:'F2',
   precheck_vi:'Luoi/mesh mong — de rach. BAT BUOC tui luoi neu may. Thao day+lot. Chai kho nhe.',
   why_vi:'Mesh: ma sat may de hong soi. Chi sol MEM/mieng fot. Nhiet thap. Day trang giat rieng.',
   fresh_path_vi:'Chai kho nhe → spotting sol mem + chat trung tinh loang → tay hoac may TUI LUOI 30C tinh te → xa ky → nhet bao phoi bong mat.',
   dried_path_vi:'Vet sau tren mesh: lap spotting, khong chai cung. Khong het → bao khach (mesh de bam mau).',
   motion_vi:'Luc 1-2 — sol sieu mem/mem, mot chieu theo soi',
   water_temp_vi:'<=30C, chuong trinh tinh te',
   aftercare_vi:'CAM say nong. Phoi bong mat + giu form. Kho han moi mang.'},
  {id:'I_SNEAKER_WHITE',name:'White sneaker panel / midsole',name_vi:'Giay trang / canh trang / de trang (midsole)',name_ko:'흰 창·흰 옆면 운동화',fabric_id:'F2',
   precheck_vi:'Xu ly RIENG canh/de trang. Ghi nhan: de cao su va vai khac sol. Thong bao: kho trang 100% neu da oxi hoa.',
   why_vi:'De/canh trang de VANG neu ton du kiềm hoac say nang. Dung chat TRUNG TINH, xa ky, phoi bong mat (nua kho tranh vang).',
   fresh_path_vi:'Chai kho → paste nhe: bot giat trung tinh + baking soda + it nuoc len canh/de → sol mem (vai) / sol cung nhe (cao su) → xa KY → phoi bong mat, nhet bao.',
   dried_path_vi:'Lap 1-2 lan. Con xam do oxi hoa: bao khach, khong dung tay manh gay hong keo.',
   motion_vi:'Canh vai: sol mem. De cao su: sol cung nhe, khong cha len mesh',
   water_temp_vi:'Lanh/~30C, khong nong',
   aftercare_vi:'Phoi bong mat den kho. CAM say nong / nang gay. Bao khach neu con o.'},
  {id:'I_SHOE_LACES',name:'Shoe laces',name_vi:'Day giay (dac biet day trang)',name_ko:'운동화 끈(특히 흰 끈)',fabric_id:'F1',
   precheck_vi:'LUON thao day ra giat RIENG (khong de trong giay). Day mau/trang tach lo.',
   why_vi:'Day trong giay khi giat = ban lan + khong sach. Day trang de vang neu kiềm ton du / say nang.',
   fresh_path_vi:'Ngam nuoc lanh + chat giat trung tinh 15-30 phut → chai mem hoac vo tui luoi giat nhe → xa KY → phoi bong mat (khong say nong).',
   dried_path_vi:'Con xam: ngam them + baking soda nhe, xa ky. Khong het → bao khach thay day.',
   motion_vi:'Luc 2 — chai mem doc day, khong xoan manh',
   water_temp_vi:'Lanh/~30C',
   aftercare_vi:'Phoi thang bong mat. CAM say nong. Lap lai khi giay kho.'},
  {id:'I_LEATHER_SHOE',name:'Leather shoe',name_vi:'Giay da bong',name_ko:'가죽 구두',fabric_id:'F8',
   precheck_vi:'Giay da: it nuoc toi da — chi spotting. CAM ngam/may neu khong chac.',
   why_vi:'Giay da: nuoc nhieu = bien dang. Spotting nhe + kem da. CAM say may.',
   fresh_path_vi:'Chai kho → khan + nuoc rua chen rat loang / dung dich da Cham → lau kho → kem da.',
   dried_path_vi:'Khong ngam. Con vet nang → chuyen. Phoi bong mat, nhet bao.',
   motion_vi:'Luc 1 — lau nhe',
   water_temp_vi:'It nuoc, nhiet phong',
   aftercare_vi:'Kem da. KHONG say may. Phoi bong mat + giu form.'},
  {id:'I_SUEDE_SHOE',name:'Suede shoe',name_vi:'Giay da lon / suede',name_ko:'스웨이드 구두',fabric_id:'F9',
   precheck_vi:'Suede giay: CAM nuoc. Uot → chuyen.',
   why_vi:'Suede giay + nuoc = vet. Chai suede kho / tay kho. CAM may/say.',
   fresh_path_vi:'Chai kho theo chieu long. Vet dau: tay kho. Khong het → chuyen.',
   dried_path_vi:'Khong ngam. Bao khach chuyen neu nang.',
   motion_vi:'Luc 1 — chai kho',
   water_temp_vi:'KHONG nuoc',
   aftercare_vi:'Kho bong mat. KHONG say.'},
  {id:'I_GORETEX',name:'Waterproof functional wear',name_vi:'Do chong tham / Gore-Tex / DWR',name_ko:'고어텍스·기능성 방수 의류',fabric_id:'F2',
   precheck_vi:'Gore-Tex/DWR: giat it bot, nhiet thap. Ton du bot = mat chong tham.',
   why_vi:'Mang chong tham: bot giat qua nhieu / xa vai = hong DWR. Say nhiet thap co the tai kich hoat DWR.',
   fresh_path_vi:'Giat 30C tinh te, bot giat LONG it. KHONG xa vai. Xa them 1 lan. Say nhiet thap ngan (tai DWR) neu may cho phep.',
   dried_path_vi:'Neu mat chong tham: giat sach ton du → say thap ~10 phut → xit lai DWR sau ~10 lan giat.',
   motion_vi:'Luc 2 — may tinh te / tay nhe',
   water_temp_vi:'~30C; nhiet thap khi say',
   aftercare_vi:'Kiem tra chong tham. Co the xit lai DWR. Tranh bot giat dam.'},
  {id:'I_DOWN_JACKET',name:'Down / padded jacket',name_vi:'Ao phao / ao don long',name_ko:'다운·패딩 점퍼',fabric_id:'F2',
   precheck_vi:'Khoa keo, lam rong tui trong. Giat 30C tinh te, bot it, xa them.',
   why_vi:'Ao phao: ton du bot = don von. Khong kho het = moc. Say thap + rũ (bong tennis neu co).',
   fresh_path_vi:'30C tinh te, bot giat it. Them 1 lan xa. Vat rat nhe. Say nhiet thap + rũ thuong xuyen (hoac quat manh neu khong co say).',
   dried_path_vi:'Kiem tra giua ao khong lanh = kho. Chua kho → say/quat them. CAM de am lau.',
   motion_vi:'Luc 2 — chuong trinh tinh te',
   water_temp_vi:'~30C; say nhiet thap',
   aftercare_vi:'Kho HOAN TOAN truoc khi cat. Ru deu don. Tranh am keo dai.'},
  {id:'I_GLOVE_LEATHER',name:'Leather glove',name_vi:'Gang tay da',name_ko:'가죽 장갑',fabric_id:'F8',
   precheck_vi:'Gang da: nuoc toi thieu. CAM ngam lau.',
   why_vi:'Gang da + nuoc nhieu = bien dang/nut. Lau nhe + kem da.',
   fresh_path_vi:'Khan am nhe lau → kho → kem da.',
   dried_path_vi:'Khong ngam. Hong form → bao khach.',
   motion_vi:'Luc 1',
   water_temp_vi:'It nuoc',
   aftercare_vi:'Kem da. Kho tu nhien.'},
  {id:'I_SUIT',name:'Wool / business suit',name_vi:'Vest / bo suit len (dong)',name_ko:'정장·수트(울·캔버스)',fabric_id:'F3',
   precheck_vi:'Chup anh. Kiem canvas/lot trong. Nhe + khong vet → steamer. Vet/mui → dry-clean / wet-clean chuyen. CAM may giat thuong.',
   why_vi:'Suit: cau truc vai + lot. May nha = meo vai. Dry-clean CHI KHI can (vet/mui) — lam thuong xuyen lam yeu soi. Giua lan: chai + treo moc rong + nghi 24-48h.',
   fresh_path_vi:'Chai mem theo soi → treo thoang. Vet: tham NGOAI→TRONG, khong cha lan. Spotting trung tinh nhe neu an toan. Khong het / co canvas → chuyen dry-clean. Ui: steamer dung, tranh ep manh nguc/ve ao.',
   dried_path_vi:'Vet kho: khong ngam may. Chuyen chuyen + thong bao khach. Khong hao danh het 100%.',
   motion_vi:'Luc 1-2 — chai/tham, khong vo may',
   water_temp_vi:'KHONG may nha. Spotting lanh neu bat buoc',
   aftercare_vi:'Moc go rong vai. Tui vai thoang (khong nilon kin). Nghi giua lan mac. CAM say may.'},
  {id:'I_SUIT_SUMMER',name:'Summer linen/cotton suit',name_vi:'Suit he linen/cotton mong',name_ko:'여름 정장(린넨·코튼 얇은)',fabric_id:'F5',
   precheck_vi:'Phan biet linen/cotton vs len. Nhan truoc. Co lot/canvas → xu ly nhu suit dong neu khong chac.',
   why_vi:'Linen/cotton: de nhao. Chi chat giat TRUNG TINH / nhe — CAM bot dam. Tay/may tinh te neu khong canvas. Uu tien steamer + ui khi am.',
   fresh_path_vi:'Spotting nhe → tay/may tinh te ~30C chat TRUNG TINH (neu nhan cho phep) → xa ky → phoi/treo → ui khi am. Co lot phuc tap → dry-clean. CAM bot giat manh.',
   dried_path_vi:'Vet kho: ngam ngan + spotting trung tinh, khong cha manh. Khong het → chuyen.',
   motion_vi:'Luc 2 — nhe, tui luoi neu may',
   water_temp_vi:'~30C; khong nong',
   aftercare_vi:'Ui am. Treo moc rong. CAM say nong.'},
  {id:'I_AO_DAI',name:'Ao dai',name_vi:'Ao dai (truyen thong VN)',name_ko:'아오자이',fabric_id:'F4',
   precheck_vi:'BAT BUOC phan loai: lua vs polyester (nhan VN thuong SAI). Silk=S1. Poly=trung tinh nhe. Anh + tu choi neu khong chac.',
   why_vi:'Ao dai = ton trong toi da. CHI tay. CAM may/vat/say. Luc 1. Phoi bong mat phang.',
   fresh_path_vi:'Tay nuoc lanh + chat trung tinh silk (lua) hoac nhe (poly). NHUNG nhe — KHONG cha/vat. Xa 3 lan. Phoi bong mat phang. Ui mat trai ~110C, lot vai; lua TAT hoi.',
   dried_path_vi:'Vet: spotting sieu nhe mat trai. Lua + nuoc de de vet nuoc — thong bao khach. Khong het → chuyen.',
   motion_vi:'Luc 1 — baby face, khong cha',
   water_temp_vi:'Lanh / <=30C. CHI tay',
   aftercare_vi:'CAM say/nang gay. Ui mat trai. Treo moc dem vai.'},
  {id:'I_HANBOK',name:'Hanbok',name_vi:'Hanbok (trang phuc Han)',name_ko:'한복',fabric_id:'F4',
   precheck_vi:'Phan loai vai: bon gyeon/silk, moshi, cotton, poly. Nhuan mau tu nhien de phai. Git/goreum/tay ao khac chat → nguy co lem mau. Anh + dong y khach.',
   why_vi:'Hanbok cao cap: uu tien dry-clean chuyen. May = hong may/form. Bleach CAM. Lua: it nuoc, luc 1. Mau git/goreum de lem.',
   fresh_path_vi:'Uu tien chuyen dry-clean neu silk/nhuan mau/do dat. Neu poly/cotton nhan cho phep: tay lanh trung tinh, KHONG cha, xa ky, phoi bong mat. Spotting: tham, khong lau vong.',
   dried_path_vi:'Vet thuc an tren silk: tranh nuoc (de vet nuoc) — tham + chuyen nhanh. Khong het → bao khach.',
   motion_vi:'Luc 1 — khong vo may',
   water_temp_vi:'Lanh. Uu tien dry-clean',
   aftercare_vi:'Kho het roi cat. Thoang khi, tranh am moc. CAM say may.'},
  {id:'I_GOLF_WEAR',name:'Golf performance wear',name_vi:'Do golf (ao/quan performance)',name_ko:'골프복(기능성 셔츠·바지)',fabric_id:'F2',
   precheck_vi:'Poly/spandex moisture-wick. Lat mat trai. Doc nhan.',
   why_vi:'Do golf: CAM xa vai / dryer sheet (bit ken hut am). Nuoc lanh, chat giat NHE/the thao — KHONG bot dam/enzyme manh. Nhiet cao hong dan hoi.',
   fresh_path_vi:'Lat trai → may/tay <=30C chat giat nhe/the thao → KHONG xa vai → xa ky → phoi / say thap toi thieu. Vet co/bun: spotting lanh truoc. Mui: ngam lanh + trung tinh.',
   dried_path_vi:'Mui mo hoi: ngam lanh + trung tinh, khong bot dam. Lap neu can.',
   motion_vi:'Luc 2 — chuong trinh tinh te',
   water_temp_vi:'Lanh / <=30C',
   aftercare_vi:'Phoi bong mat. CAM xa vai. Tranh say nong.'},
  {id:'I_GOLF_SHOE',name:'Golf shoe',name_vi:'Giay golf',name_ko:'골프화',fabric_id:'F2',
   precheck_vi:'Thao day/lot. Lam sach dinh/gai (cleat) truoc. Phan da vs vai/synthetic.',
   why_vi:'Giong sneaker: CAM say nong (keo). Da: it nuoc. Vai/synthetic: 30C nhe. Gai/de: chai cung nhe.',
   fresh_path_vi:'Chai kho bun → spotting sol mem (than) / sol cung (de) → tay hoac tui luoi 30C neu vai → xa → nhet bao phoi bong mat. Da: chi lau am + kem da.',
   dried_path_vi:'Lap spotting. Khong ngam da. CAM say may.',
   motion_vi:'Than luc 2 sol mem; de luc 2-3',
   water_temp_vi:'<=30C; da = it nuoc',
   aftercare_vi:'Kho han moi mang. CAM say nong. Bao quan kho.'},
  {id:'I_GOLF_HAT',name:'Golf / sports cap',name_vi:'Mu golf / mu luoi trai',name_ko:'골프모자·캡',fabric_id:'F2',
   precheck_vi:'Phan biet mu CUNG (vanh buckram/cardboard) vs mu MEM. Golf/cap: CAM may/dishwasher/say (hong vanh). Spotting vanh mo hoi TRUOC.',
   why_vi:'GIAO DUC: Mu cau truc = giu form. New Era/cap: CHI spot-clean vanh + panel — CAM ngam toan bo / may (vanh vo). Chat NHE/trung tinh + chai mem. A3 loang chi vanh neu vang mo hoi (test mau). Nhet bat/bong giu form khi kho.',
   fresh_path_vi:'(1) Lat vanh mo hoi. (2) D2/S1 loang + chai mem vanh (vong tron nhe). (3) Khan am lau xa xa phong. (4) Panel: spot tung mau (tranh lo mau). (5) Nhet khan/bat giu crown. (6) Phoi bong mat dung — CAM say/ui/dishwasher.',
   dried_path_vi:'Lap spotting vanh. Vang cu: A3 1:4 chi vanh 5-10 phut (test). Khong het → bao khach.',
   motion_vi:'Luc 1-2 — chai mem; KHONG vo vanh',
   water_temp_vi:'Lanh. Spot/tay cuc bo — CAM may',
   aftercare_vi:'Giu form den kho han (VN: quat, <4h bat dau kho). CAM say may.'},
  {id:'I_HAT_CAP',name:'Baseball / fashion cap (structured or soft)',name_vi:'Mu luoi trai / baseball cap',name_ko:'야구모자·캡·일반 모자',fabric_id:'F2',
   precheck_vi:'(A) Mu CUNG/fitted: CHI spot-clean — CAM may/dishwasher. (B) Mu MEM/dad cap: tay lanh duoc; may CHI neu nhan cho + tui luoi. Da/suede vanh → pro.',
   why_vi:'GIAO DUC: Mo hoi vanh = dau+muoi+protein. Thu tu: spot vanh → giu form khi kho. CAM nhiet (vanh mem/vo). Len: lanh cuc, khong cha. Tham khao New Era care: mild detergent, air dry natural position.',
   fresh_path_vi:'(1) Phan loai cung/mem. (2) Spotting vanh: D2/S1 + chai mem. (3) Mu mem: tay chau lanh ngam ngan + chai vanh, KHONG vat vanh. (4) Xa/khan am. (5) Nhet bat/khan giu crown + chinh vanh. (6) Phoi bong mat. CAM dishwasher/say.',
   dried_path_vi:'Vanh vang: A3 1:4 test → enzyme nhe neu can. Logo theu: khong cha manh.',
   motion_vi:'Luc 1-2 sol mem; khong gap vanh',
   water_temp_vi:'Lanh. Mu cung = spot; mu mem = tay/lanh',
   aftercare_vi:'Kho dung form. CAM say/ui. Bao quan khong dep vanh.'},
  {id:'I_GOLF_GLOVE_LEATHER',name:'Leather golf glove',name_vi:'Gang golf da (cabretta)',name_ko:'골프장갑(가죽)',fabric_id:'F8',
   precheck_vi:'Da cabretta: CAM may. Nuoc toi thieu. Khong giat qua thuong. CAM con sat khuan/alcohol (lam kho nut da).',
   why_vi:'Gang golf da: may/ngam = cung/nut. Chi lau nhe + kem da. CAM tay oxy, CAM alcohol.',
   fresh_path_vi:'Khan am + xa phong da/kem da nhe lau → khan am lau du → tham kho → de kho phang (co the deo vai phut giu form) → kem da. CAM con/alcohol.',
   dried_path_vi:'Khong ngam. Con ban: lap lau nhe. Bao khach neu gia.',
   motion_vi:'Luc 1 — lau, khong vo',
   water_temp_vi:'It nuoc lanh',
   aftercare_vi:'Kho tu nhien. CAM say. Kem da.'},
  {id:'I_GOLF_GLOVE_SYNTH',name:'Synthetic golf glove',name_vi:'Gang golf synthetic / mesh',name_ko:'골프장갑(합성·메쉬)',fabric_id:'F2',
   precheck_vi:'Synthetic/mesh: tay uu tien; may chi tui luoi tinh te neu nhan cho.',
   why_vi:'Synthetic: lanh + chat nhe. CAM xa vai. CAM say nong.',
   fresh_path_vi:'Tay lanh + chat nhe, vo nhe → xa → phoi phang. Hoac tui luoi 30C tinh te.',
   dried_path_vi:'Lap tay neu ban. Khong say.',
   motion_vi:'Luc 2',
   water_temp_vi:'Lanh / <=30C',
   aftercare_vi:'Phoi phang. CAM say.'},
  {id:'I_FUR_REAL',name:'Real fur garment',name_vi:'Ao long thu that (fur)',name_ko:'모피·진짜 퍼',fabric_id:'F10',
   precheck_vi:'Phan biet long that vs gia. Anh. TU CHOI may/say/dry-clean thuong. Khuyen chuyen tiem long chuyen.',
   why_vi:'Fur that: CAM may/say/dry-clean thuong (kho dau da, de rach). Chi chuyen gia long. Bui hut dau tu nhien → can ve sinh chuyen dinh ky.',
   fresh_path_vi:'KHONG xu ly tai tiem thuong. Lac bui nhe, treo moc rong vai, thoang khi. Uot mua: lac, treo kho CHAM, CAM may say/toc, CAM chai khi uot. Chuyen chuyen gia.',
   dried_path_vi:'CAM ngam/hoa chat gia dinh. Bao khach chuyen chuyen. Quyen tu choi.',
   motion_vi:'Luc 0-1 — khong cha khi uot',
   water_temp_vi:'KHONG giat nuoc tai tiem',
   aftercare_vi:'Cat thoang, toi, mat. Tranh nang/nuoc hoa xit len ao. Chuyen kho lanh mua he neu co.'},
  {id:'I_FUR_FAUX',name:'Faux / synthetic fur',name_vi:'Long gia / faux fur',name_ko:'인조 모피·페이크 퍼',fabric_id:'F2',
   precheck_vi:'Long gia (acrylic/modacrylic): nhiet cao = xoan long. Doc nhan.',
   why_vi:'Faux fur: CAM nhiet cao / steam manh (xoan long khong phuc hoi). Giat nhe, treo ngay, say thap toi thieu.',
   fresh_path_vi:'Lat trai. May/tay nhe ~30C chat trung tinh, tai thap, thoi gian ngan. Treo ngay sau giat. CAM ui/steam manh. Say: nhiet thap/tat neu can.',
   dried_path_vi:'Long xep: chai mem KHI KHO theo chieu long. Khong het → thong bao.',
   motion_vi:'Luc 2 — nhe, tai thap',
   water_temp_vi:'~30C; CAM nong',
   aftercare_vi:'Treo thoang. CAM say nong / ui.'},
  {id:'I_HIKING_SHOE',name:'Hiking / outdoor shoe',name_vi:'Giay leo nui / outdoor',name_ko:'등산화',fabric_id:'F2',
   precheck_vi:'Thao day/lot. Chai bun kho. Phan membrane (Gore-Tex) vs da vs vai.',
   why_vi:'Outdoor: CAM say nong. Membrane: bot it, KHONG xa vai. Da: it nuoc + kem. Luoi: sol mem.',
   fresh_path_vi:'Chai kho → spotting → tay/tui luoi 30C bot it neu vai/membrane → xa them → nhet bao phoi bong mat. Da: lau am + kem. Sau kho co the xit DWR neu mat chong tham.',
   dried_path_vi:'Lap. Khong say may. Bao khach neu keo long.',
   motion_vi:'Than sol mem; de sol cung nhe',
   water_temp_vi:'<=30C',
   aftercare_vi:'Kho han. CAM say nong. Bao quan kho.'},
  {id:'I_DENIM',name:'Denim jeans / jacket / skirt',name_vi:'Do denim (quan jean / ao / vay)',name_ko:'청바지·청자켓·청치마(데님)',fabric_id:'F6',
   precheck_vi:'Denim indigo: lan dau ra mau = BINH THUONG. Giat RIENG / mau tuong tu — CAM chung do trang. Lat trai. Chup anh neu khach kieu phai mau.',
   why_vi:'Denim: bao mau bang lat trai + nuoc lanh/~30C + bot it. Phoi bong mat (nang gay = phai mau nhanh). Van bac theo thoi gian = dac trung, khong phai loi giat neu da bao khach.',
   fresh_path_vi:'Lat trai → 30C/lanh, chat giat it → giat rieng 2-3 lan dau → han che say may (co) → phoi bong mat. Vet: spotting nhe, khong tay chlorine.',
   dried_path_vi:'Vet kho: spotting + giat nhe. Phai mau/bac mau do nang/tuoi: giai thich dac trung hoac chuyen nhuom/but mau — khong hao danh 100%. CAM meo con+dau+say.',
   motion_vi:'Luc 2-3 — sol mem/cung nhe tuy cho',
   water_temp_vi:'Lanh / ~30C',
   aftercare_vi:'Phoi bong mat thoang. Tranh nang gay. CAM giat chung trang. Bao khach lan dau ra mau.'},
  {id:'I_COLOR_FADE',name:'Faded colored garment restore',name_vi:'Phuc hoi mat mau / phai mau (vai mau)',name_ko:'유색 옷 색바램·탈색 복원',fabric_id:'F1',
   precheck_vi:'Chup anh + do dien tich. Phan loai: (a) UV/mac theo thoi gian (b) tay hoa chat pha mau (c) loang mau. Denim bac mau do mac+UV = dac trung — giai thich khach, khong goi la loi giat neu da bao. CAM hao danh phuc hoi 100%.',
   why_vi:'Vai mau mat mau = thuoc nhuom yeu/pha — khong phuc hoi than ky bang chat giat/S1/muoi/cafe/tra/giat chung quan jean moi. Huong dung: NHO (<= dong xu) but mau vai tam thoi; VUA/LON gui nhuom chuyen hoac giai thich + boi thuong. CAM meo ethanol+dau+say, CAM ngam nong tu nhuom tai tiem neu khong phai dich vu nhuom.',
   fresh_path_vi:'(1) Anh + dong y khach + NO RO gioi han. (2) NHO (<= dong xu): but mau vai dung mau → cham nhe ngoai→trong → co dinh nhiet theo huong dan but — NO RO se phai lai khi giat. (3) VUA (long ban tay) / LON: KHONG chi but — chuyen nhuom / bao khach khong khop mau 100% / boi thuong hop ly. (4) CAM detergent, CAM giat chung jean moi de "nhuom lai", CAM cafe/tra/muoi 10:1.',
   dried_path_vi:'Da tay/oxy pha mau: dung lai, anh, nhuom/boi thuong. Khong lap tay. Khong dung oxy/chlorine de "can bang" vai mau.',
   motion_vi:'Chi khi chon but (cho nho): luc 1, cham/but ngoai→trong, khong cha, khong lan mau. Vua/lon: khong cham but toan bo.',
   water_temp_vi:'Buoc PHUC HOI: khong giat may/tay, khong ngam nong+thuoc nhuom tai quay. But mau: it am/kho theo nhan but. Sau khi xu ly xong, neu khach giu mon: giat rieng lat trai nuoc lanh (bao mau) — do la DUY TRI mau, khong phai phuc hoi.',
   aftercare_vi:'Anh sang manh kiem tra. Ghi ro: but = tam thoi; vua/lon = nhuom/boi thuong. Phoi bong mat, CAM nang gay. Khuyen khach giat lat trai + lanh + rieng de giam phai tiep.'},
  {id:'I_DRESS_SHIRT',name:'Dress shirt / white business shirt care',name_vi:'Ao so mi cong so (cham soc thuong)',name_ko:'와이셔츠·드레스셔츠(일반 세탁·관리)',fabric_id:'F1',
   precheck_vi:'Phan biet: (A) giat/quan ly thuong — dung I_DRESS_SHIRT. (B) ao VANG/hoi o nach/vong co vang — chuyen S_SHIRT_YELLOW / S_COLLAR_STAIN / S_SWEAT_YELLOW. Doc nhan giat. Tach trang vs mau.',
   why_vi:'GIAO DUC: Ao so mi cotton/cotton-pha = giat thuong + pretreat co/tay ao. KHONG mac dinh = SOP tay vang. Cam Javel thuong xuyen (yeu soi + vang protein). Co/tay ban: enzyme/D2 len CHO KHO truoc. Ui: co → manchette → tay → than. Ho tinh bot (tuy chon) SAU khi sach.',
   fresh_path_vi:'(1) Nhan: ao so mi sach/ban nhe, KHONG vang toan than. (2) Lat mat trai; kiem tra nut/cau. (3) Spotting co + manchette: D2/enzyme nho len CHO KHO 5-15 phut. (4) Giat tay hoac may nhe 30-40C, chat giat trung tinh/manh vua — tach trang. (5) Xa ky. (6) Ui/ho neu can: co→manchette→tay→than; phoi bong mat. Neu DA VANG: dung S_SHIRT_YELLOW (enzyme→B1; CAM Javel).',
   dried_path_vi:'Ban kho o co: enzyme/D2 pretreat lai. Con vang: S_SHIRT_YELLOW. Iem: S_DYE_TRANSFER. CAM say khoa khi con vet.',
   motion_vi:'Co/manchette: luc 2 sol mem mot chieu. Than: giat may nhe — khong cha manh.',
   water_temp_vi:'30-40C cotton; nhan giat uu tien. Khong nuoc soi.',
   aftercare_vi:'Phoi bong mat / say thap neu nhan cho. Ui theo thu tu co→tay→than. Treo moc. Ho (tuy chon) khi ao da sach kho.'},
  {id:'I_CURTAIN_FABRIC',name:'Fabric window curtain',name_vi:'Rem vai thuong (cua so)',name_ko:'일반 커튼·패브릭 커튼',fabric_id:'F2',
   precheck_vi:'Do dai/rong TRUOC giat (bao khach co cotton 3-5%, linen 5-8%). Thao moc/moc treo. Phan loai mau. Rem moc → S_MILDEW + PPE. Rem lot blackout: doc nhan — co the chi dry-clean.',
   why_vi:'GIAO DUC: Rem vai = rut + moc (VN am). Giat tinh te 30C, D2/D3 it, vat ngan. Treo UOT de trong luc keo phang. Chu ky: 1 thang (phong), 2 tuan (tam). CAM Javel mau.',
   fresh_path_vi:'(1) Do size + anh. (2) Hut/chai bui. (3) Spotting vet. (4) May tui luoi/tinh te ~30C chat nhe — hoac tay. (5) Vat ngan. (6) Treo ngay len thanh khi con am. VN: bat dau kho <4h.',
   dried_path_vi:'Moc: PPE + protocol S_MILDEW. Rut: bao khach. Ui nhe neu can khi am.',
   motion_vi:'Luc 1-2 — khong cha manh rem mong',
   water_temp_vi:'~30C; cotton toi da 40C neu nhan cho',
   aftercare_vi:'Treo thang. Kiem moc dinh ky. Tranh AC thoi thang rem (dong condens).'},
  {id:'I_CURTAIN_URETHANE',name:'Urethane / vinyl / PU coated curtain',name_vi:'Rem phu urethane / vinyl / PU (tam tam)',name_ko:'우레탄·비닐·PU 코팅 커튼·샤워커튼',fabric_id:'F2',
   precheck_vi:'Phan biet: (A) PU/urethane coated (B) vinyl/PVC/PEVA liner (C) rem vai thuong. Anh. Nhieu hang CAM may — uu tien lau tai cho.',
   why_vi:'GIAO DUC: Lop phu PU/vinyl: may nhieu = boc/lot (IFI/coated fabric). Uu tien: xa phong TRUNG TINH + nuoc am + mien fot/sol mem. CAM dung moi manh/A2. Neu may (chi khi nhan cho): tinh te, <=40C, them khan can bang, CAM xa vai, CAM say — treo kho. Phenol CAM tren urethane; ammonia pha OK hon tren PU (medical fabric guides).',
   fresh_path_vi:'(1) Nhan chat lieu. (2) Lau mat: D2/S1 loang + nuoc am, sol mem. (3) Vet moc: A3 1:4 + PPE, xa, kho thoang — CAM say nong. (4) Neu nhan cho may: tinh te lanh/am, it bot, vat nhe + khan. (5) Treo kho — CAM dryer. (6) Boc lot → thay / bao khach.',
   dried_path_vi:'Khong ngam dai. Con moc: lap A3/PPE. Vinyl gia: thay dinh ky 2-3 nam neu cung/nut.',
   motion_vi:'Luc 1-2 — lau/spot; khong cha cot',
   water_temp_vi:'Am nhe; may (neu cho) <=40C',
   aftercare_vi:'Treo kho thoang. Mo rem sau tam (chong moc). CAM ui/say nong.'},
  {id:'I_DUVET_GOOSE',name:'Goose / duck down duvet',name_vi:'Chan long ngong/vit (down)',name_ko:'구스이불·거위털·다운 이불',fabric_id:'F1',
   precheck_vi:'Doc nhan. Ra/rach = sua TRUOC. May NHO → gui may lon (7kg+/laundromat). Vo chan (duvet cover) giat thuong — loi down it giat (1-3 nam).',
   why_vi:'GIAO DUC: Down = giu dau tu nhien. CAM dry-clean PERC (hut dau, gion). Uu tien giat nuoc: may LON front-load, nuoc LANH/<=30C, chat down-wash / trung tinh IT, THEM xa. Say thap + bong tennis/dryer ball, dung-fluff 2-3h — KHO 100% (moc). Feathered Friends/FabricCare: mild, no bleach/softener.',
   fresh_path_vi:'(1) Kiem rach. (2) Spotting vo. (3) May lon: delicate, lanh, down detergent/S1 it, extra rinse. (4) CAM vat manh/vat tay. (5) Say thap + 2-3 bong sach; 20-30 phut dung, vo cum tay, lap den kho GIUA. (6) Phoi them neu can.',
   dried_path_vi:'Cum uot = moc 24h — say/phoi tiep. Con mui: lap xa + say kho.',
   motion_vi:'Luc 0-1 — khong vat xoan',
   water_temp_vi:'Lanh / <=30C',
   aftercare_vi:'Dung vo chan. Bao quan kho thoang. CAM bleach/xa vai.'},
  {id:'I_DUVET_COTTON',name:'Cotton batting / synthetic fill comforter',name_vi:'Chan bong / chan poly (khong long)',name_ko:'솜이불·폴리이불·일반 충전 이불',fabric_id:'F1',
   precheck_vi:'Phan biet long (I_DUVET_GOOSE) vs bong/poly. May nho → may lon. Kiem rach. Nhieu queen/king CAN laundromat.',
   why_vi:'GIAO DUC: Bong/poly ben hon down nhung de von neu thieu xa/say. May lon, tinh te/bulky, 30-40C, D2/D3 IT, THEM xa (bot ton = cung). Say thap/vua + bong tennis; dung-fluff. CAM xa vai. Acme/Bedsure: drum phai du cho tumbling.',
   fresh_path_vi:'(1) Do size vs may. (2) Spotting. (3) May: 30-40C, bot it, extra rinse. (4) Say thap + bong; 20-30 phut vo. (5) Kiem giua chan khong am. (6) VN: bat dau kho <4h.',
   dried_path_vi:'Von: say lai + bong. Moc: S_MILDEW + PPE neu nang.',
   motion_vi:'Luc 0 — may; spotting luc 2 sol mem',
   water_temp_vi:'30-40C (khong soi)',
   aftercare_vi:'Vo chan giat thuong. Chan: 2-4 lan/nam neu co vo.'},
  {id:'I_WHITE_FADE',name:'White / light fabric fade balance',name_vi:'Phuc hoi mat mau vai trang/sang (OBA)',name_ko:'흰·밝은 옷 탈색·얼룩 환 복원',fabric_id:'F1',
   precheck_vi:'CHI vai trang/sang. Chup anh. Dom trang sau tay = OBA bi pha. CAM ap dung len vai mau.',
   why_vi:'Vai trang: can bang bang tay oxy DEU TOAN BO (khong cham tung diem — de lo hon). Paste baking soda + oxy gia chi cho cho sot. Phoi nang ngan co the can bang UV — neu nhan/vai cho phep.',
   fresh_path_vi:'Ngam TOAN BO bot tay oxy pha loang deu ~45 phut (theo huong dan) → xa → neu con dom: paste baking soda + oxy gia nhe 10 phut chi cho sot → giat ~40C neu cotton cho → kiem tra duoi anh sang.',
   dried_path_vi:'Con lech mau: lap ngam deu (khong cham diem). Khong het → bao khach gioi han.',
   motion_vi:'Luc 0-1 — ngam deu, khong cha manh',
   water_temp_vi:'Theo nhan; cotton thuong ~40C sau xu ly',
   aftercare_vi:'Kiem tra trang deu. Vai mau → CAM quy trinh nay (chuyen I_COLOR_FADE).'}
] AS it
MERGE (i:Item {id:it.id})
SET i.name = it.name, i.name_vi = it.name_vi, i.name_ko = it.name_ko,
    i.precheck_vi = it.precheck_vi, i.why_vi = it.why_vi,
    i.fresh_path_vi = it.fresh_path_vi, i.dried_path_vi = it.dried_path_vi,
    i.motion_vi = it.motion_vi, i.water_temp_vi = it.water_temp_vi, i.aftercare_vi = it.aftercare_vi,
    i.fabric_id = it.fabric_id
WITH it, i
MATCH (f:Fabric {id:it.fabric_id})
MERGE (i)-[:MADE_OF]->(f)
RETURN count(i) AS created""")
        _r(s, "I_items_chem_tools", """
MATCH (cloth:Tool {id:'T_CLOTH'}), (soft:Tool {id:'T_BRUSH_SOFT'}), (ultra:Tool {id:'T_BRUSH_ULTRA'}),
      (hard:Tool {id:'T_BRUSH_HARD'}), (shoe:Tool {id:'T_BRUSH_SHOE'}), (spray:Tool {id:'T_SPRAY'}),
      (glove:Tool {id:'T_GLOVE_NITRILE'}), (mesh:Tool {id:'T_MESH_BAG'})
WITH cloth, soft, ultra, hard, shoe, spray, glove, mesh
MATCH (d2:Chemical {code:'D2'}),(d3:Chemical {code:'D3'}),(a1:Chemical {code:'A1'}),
      (a3:Chemical {code:'A3'}),(a4:Chemical {code:'A4'}),(n1:Chemical {code:'N1'}),
      (b1:Chemical {code:'B1'}),(s1:Chemical {code:'S1'}),(e1:Chemical {code:'E1'})
WITH cloth, soft, ultra, hard, shoe, spray, glove, mesh, d2, d3, a1, a3, a4, n1, b1, s1, e1
// Full rewire Item tools/chems (drop stale wrong links)
MATCH (i:Item)
OPTIONAL MATCH (i)-[oldt:USES_TOOL]->()
DELETE oldt
WITH cloth, soft, ultra, hard, shoe, spray, glove, mesh, d2, d3, a1, a3, a4, n1, b1, s1, e1, i
OPTIONAL MATCH (i)-[oldc:USES_CHEMICAL]->()
DELETE oldc
WITH cloth, soft, ultra, hard, shoe, spray, glove, mesh, d2, d3, a1, a3, a4, n1, b1, s1, e1, i
FOREACH (_ IN CASE WHEN i.id IN ['I_LEATHER_GARMENT','I_LEATHER_BAG','I_GLOVE_LEATHER'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_CHEMICAL]->(a1))
FOREACH (_ IN CASE WHEN i.id = 'I_LEATHER_SHOE' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_CHEMICAL]->(a1) MERGE (i)-[:USES_CHEMICAL]->(d2))
FOREACH (_ IN CASE WHEN i.id = 'I_GOLF_GLOVE_LEATHER' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth))
FOREACH (_ IN CASE WHEN i.id IN ['I_SUEDE_GARMENT','I_SUEDE_BAG','I_SUEDE_SHOE'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_TOOL]->(cloth))
FOREACH (_ IN CASE WHEN i.id IN ['I_SNEAKER','I_RUNNING_MESH','I_SNEAKER_WHITE','I_GOLF_SHOE','I_HIKING_SHOE'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_TOOL]->(shoe)
  MERGE (i)-[:USES_CHEMICAL]->(d2) MERGE (i)-[:USES_CHEMICAL]->(n1))
FOREACH (_ IN CASE WHEN i.id = 'I_SHOE_LACES' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_TOOL]->(mesh)
  MERGE (i)-[:USES_CHEMICAL]->(d2) MERGE (i)-[:USES_CHEMICAL]->(n1))
FOREACH (_ IN CASE WHEN i.id IN ['I_GORETEX','I_DOWN_JACKET','I_GOLF_GLOVE_SYNTH','I_FUR_FAUX'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_CHEMICAL]->(d2) MERGE (i)-[:USES_TOOL]->(cloth))
FOREACH (_ IN CASE WHEN i.id IN ['I_GOLF_WEAR','I_GOLF_HAT','I_HAT_CAP','I_SUIT_SUMMER','I_DRESS_SHIRT'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_CHEMICAL]->(d2))
FOREACH (_ IN CASE WHEN i.id = 'I_DRESS_SHIRT' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_CHEMICAL]->(n1))
FOREACH (_ IN CASE WHEN i.id IN ['I_GOLF_HAT','I_HAT_CAP'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_CHEMICAL]->(a3) MERGE (i)-[:USES_CHEMICAL]->(s1))
FOREACH (_ IN CASE WHEN i.id IN ['I_CURTAIN_FABRIC','I_DUVET_COTTON'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_TOOL]->(mesh)
  MERGE (i)-[:USES_CHEMICAL]->(d2) MERGE (i)-[:USES_CHEMICAL]->(d3))
FOREACH (_ IN CASE WHEN i.id = 'I_CURTAIN_URETHANE' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_TOOL]->(glove)
  MERGE (i)-[:USES_CHEMICAL]->(d2) MERGE (i)-[:USES_CHEMICAL]->(a3) MERGE (i)-[:USES_CHEMICAL]->(s1))
FOREACH (_ IN CASE WHEN i.id = 'I_DUVET_GOOSE' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_CHEMICAL]->(s1) MERGE (i)-[:USES_CHEMICAL]->(d2))
FOREACH (_ IN CASE WHEN i.id = 'I_DENIM' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(hard) MERGE (i)-[:USES_TOOL]->(cloth)
  MERGE (i)-[:USES_CHEMICAL]->(d2))
// I_COLOR_FADE: no tool/chem links — marker/re-dye only via fresh_path + engine synthetic tool
FOREACH (_ IN CASE WHEN i.id = 'I_WHITE_FADE' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(spray)
  MERGE (i)-[:USES_CHEMICAL]->(b1) MERGE (i)-[:USES_CHEMICAL]->(n1) MERGE (i)-[:USES_CHEMICAL]->(a4))
FOREACH (_ IN CASE WHEN i.id IN ['I_SUIT','I_AO_DAI','I_HANBOK'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(ultra) MERGE (i)-[:USES_TOOL]->(cloth)
  MERGE (i)-[:USES_CHEMICAL]->(s1))
FOREACH (_ IN CASE WHEN i.id = 'I_FUR_REAL' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth))
// PPE glove available as graph tool for chem-heavy workflows
FOREACH (_ IN CASE WHEN i.id IN ['I_CURTAIN_URETHANE','I_DUVET_GOOSE','I_DUVET_COTTON'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(glove))
RETURN count(i) AS items""")
        _r(s, "S_clear_answer_cache", """
MATCH (c:AnswerCache)
WITH collect(c) AS nodes
FOREACH (x IN nodes | DETACH DELETE x)
RETURN size(nodes) AS cleared""")
        r2 = s.run("MATCH (n) RETURN labels(n)[0] AS l, count(n) AS c ORDER BY l")
        log["after"] = {row["l"]: row["c"] for row in r2}
        r3 = s.run("MATCH ()-[r]->() RETURN type(r) AS t, count(r) AS c ORDER BY t")
        log["relationships"] = {row["t"]: row["c"] for row in r3}
        r4 = s.run(
            "MATCH (s:Stain) WHERE s.id IN "
            "['S_LATERITE','S_MOTORBIKE_OIL','S_MILDEW','S_RUST'] "
            "RETURN s.id AS id, s.name_vi AS name_vi ORDER BY id"
        )
        log["vn_specialty_stains"] = [dict(row) for row in r4]
        log["kb_docs"] = {
            "note": "Graph education is seeded via /admin/seed (Neo4j). Markdown under kb/ is the human protocol mirror — run python ingest.py to refresh Chroma if used.",
            "home": "kb/laundry_kb_v3_items_home.md",
            "hats": "kb/laundry_kb_v3_items_clothing.md",
            "tools_ppe": "kb/laundry_kb_v3_tools_equipment.md",
            "bubble_tea": "kb/laundry_kb_v3_stains_tannin.md",
        }
    _drv.close()
    return JSONResponse(log)

# ─── Dev runner ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        workers=1,
        reload=False,
    )
