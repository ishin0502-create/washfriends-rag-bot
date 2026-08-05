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
from zalo_token import token_refresh_loop


# ─── App lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown hooks."""
    print("🚀 Wash Friends Vietnam chatbot backend starting...")
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
            "build": "2026-08-05-rich-safe-v2",
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
  {id:'G1',name:'Protein',name_vi:'Protein',description:'Blood egg milk vomit urine - cold water + enzyme',contains_protein:true,contains_tannin:false,contains_oil:false,contains_dye:false},
  {id:'G2',name:'Oil',name_vi:'Dau mo',description:'Cooking oil butter engine oil cosmetics - absorbent then surfactant',contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false},
  {id:'G3',name:'Tannin',name_vi:'Tannin',description:'Coffee tea wine juice sauces - acid then oxidizer',contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:false},
  {id:'G4',name:'Dye',name_vi:'Thuoc nhuom',description:'Curry turmeric mustard ink - UV and/or solvent',contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true},
  {id:'G5',name:'Complex',name_vi:'Phuc hop',description:'Fish sauce BBQ sweat - multiple components',contains_protein:true,contains_tannin:true,contains_oil:true,contains_dye:false}
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
  {id:'F7',name:'Rayon',name_vi:'Vai rayon',max_temp:30,can_bleach:false,enzyme_safe:false,acid_safe:false}
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
  {id:'S_COOKING_OIL',name:'Cooking Oil',name_vi:'Dau an',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Talc absorb then dish soap scrub warm water'},
  {id:'S_ENGINE_OIL',name:'Engine Oil',name_vi:'Dau dong co',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Solvent degreaser first then strong detergent - dark stain'},
  {id:'S_GREASE',name:'Grease/Lard',name_vi:'Mo',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Absorb with cornstarch then dish soap lipase enzyme'},
  {id:'S_MAYO',name:'Mayonnaise',name_vi:'Sot mayonnaise',group_id:'G2',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'same_day',tip:'Scrape protease+lipase combo soak'},
  {id:'S_COLLAR_STAIN',name:'Collar Stain',name_vi:'Vong co',group_id:'G2',water_spreads:false,contains_protein:true,contains_tannin:false,contains_oil:true,contains_dye:false,urgency:'low',tip:'Old sebum: strong detergent scrub or enzyme paste soak overnight'},
  {id:'S_SHOE_POLISH',name:'Shoe Polish',name_vi:'Xi giay',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Solvent then dish soap - color dye difficult to remove'},
  {id:'S_LIPSTICK',name:'Lipstick',name_vi:'Son moi',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Dish soap blot no spread alcohol for pigment'},
  {id:'S_FOUNDATION',name:'Foundation',name_vi:'Kem nen',group_id:'G2',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Dish soap blot gently micellar water'},
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
  {id:'S_FRUIT_JUICE',name:'Fruit Juice',name_vi:'Nuoc trai cay',group_id:'G3',water_spreads:true,contains_protein:false,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Cold water immediately oxygen bleach for stubborn'},
  {id:'S_TOMATO_SAUCE',name:'Tomato Sauce',name_vi:'Sot ca chua',group_id:'G3',water_spreads:false,contains_protein:false,contains_tannin:true,contains_oil:true,contains_dye:true,urgency:'immediate',tip:'Scrape then dish soap for oil then vinegar for tannin'},
  {id:'S_SOY_SAUCE',name:'Soy Sauce',name_vi:'Nuoc tuong',group_id:'G3',water_spreads:true,contains_protein:true,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Cold water enzyme for protein then vinegar for tannin'},
  {id:'S_FISH_SAUCE',name:'Fish Sauce',name_vi:'Nuoc mam',group_id:'G3',water_spreads:true,contains_protein:true,contains_tannin:true,contains_oil:false,contains_dye:true,urgency:'immediate',tip:'Cold water enzyme soak - difficult salt odor vinegar deodorize'},
  {id:'S_BBQ_SAUCE',name:'BBQ Sauce',name_vi:'Sot BBQ',group_id:'G3',water_spreads:false,contains_protein:true,contains_tannin:true,contains_oil:true,contains_dye:true,urgency:'same_day',tip:'Triple action: enzyme+dish soap+vinegar sequential treatment'}
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
  {id:'S_MILDEW',name:'Mildew',name_vi:'Nam moc',group_id:'G5',water_spreads:false,contains_protein:false,contains_tannin:false,contains_oil:false,contains_dye:true,urgency:'same_day',tip:'Sun dry after wash; white cotton may use diluted chlorine carefully; colored: oxygen bleach soak - severe mildew may not fully recover'},
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
MATCH (e1:Chemical {code:'E1'}),(e2:Chemical {code:'N2'}),(e3:Chemical {code:'A5'})
FOREACH (c IN [e1,e2,e3] | MERGE (s)-[:USES_CHEMICAL]->(c))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "L_chem_oil", """
MATCH (s:Stain) WHERE s.contains_oil=true
MATCH (d1:Chemical {code:'D2'}),(d2:Chemical {code:'N3'}),(d3:Chemical {code:'E3'})
FOREACH (c IN [d1,d2,d3] | MERGE (s)-[:USES_CHEMICAL]->(c))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "M_chem_tannin", """
MATCH (s:Stain) WHERE s.contains_tannin=true
MATCH (a1:Chemical {code:'A3'}),(b1:Chemical {code:'B1'})
FOREACH (c IN [a1,b1] | MERGE (s)-[:USES_CHEMICAL]->(c))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "N_chem_dye", """
MATCH (s:Stain) WHERE s.contains_dye=true
MATCH (a1:Chemical {code:'A1'}),(b1:Chemical {code:'B1'})
FOREACH (c IN [a1,b1] | MERGE (s)-[:USES_CHEMICAL]->(c))
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
MATCH (f:Fabric) WHERE f.can_bleach=false
MATCH (c:Chemical) WHERE c.code IN ['B1','B2']
MERGE (f)-[:NEVER_USE]->(c)
RETURN count(*) AS rels""")
        _r(s, "R_never_mix", """
MATCH (c1:Chemical {code:'B2'}),(c2:Chemical {code:'A5'})
MERGE (c1)-[:NEVER_MIX_WITH]->(c2)
MERGE (c2)-[:NEVER_MIX_WITH]->(c1)
RETURN count(*) AS rels""")
        # Additive ops fields — fail-soft; never deletes existing stain/chem nodes
        _r(s, "T_tools", """
UNWIND [
  {id:'T_BRUSH_SOFT',name_vi:'Ban chai spotting mem',name_ko:'연질 스포팅 솔',use_for_vi:'Cotton, polyester, vet thuong'},
  {id:'T_BRUSH_HARD',name_vi:'Ban chai spotting cung',name_ko:'경질 스포팅 솔',use_for_vi:'Denim, canvas, giay the thao'},
  {id:'T_BRUSH_ULTRA',name_vi:'Ban chai sieu mem / mieng fot',name_ko:'초연질 솔·스펀지',use_for_vi:'Lua, len, vai mong — khong cha manh'},
  {id:'T_CLOTH',name_vi:'Khan trang sach / giay tham',name_ko:'흰 천·흡수지',use_for_vi:'Tham, lot duoi, khong cha lan'},
  {id:'T_SPRAY',name_vi:'Binh xit rieng (dan nhan)',name_ko:'분무기(라벨 필수)',use_for_vi:'Pha loang A3/D2/B1 — khong tron binh'}
] AS t MERGE (n:Tool {id:t.id}) SET n += t RETURN count(n) AS created""")
        _r(s, "U_stain_ops_protein", """
MATCH (s:Stain) WHERE s.contains_protein = true
SET s.precheck_vi = coalesce(s.precheck_vi, 'Xac nhan vai + vet tuoi/kho + KHONG dung nuoc nong dau'),
    s.motion_vi = coalesce(s.motion_vi, 'Tham/cao tu NGOAI vao TAM — khong cha lan'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Nuoc LANH (duoi 40C). Enzyme toi uu ~30-37C sau khi da an toan'),
    s.aftercare_vi = coalesce(s.aftercare_vi, 'Kiem tra anh sang manh TRUOC khi say/ui. Con vet → xu ly lai, khong say')
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_oil", """
MATCH (s:Stain) WHERE s.contains_oil = true AND coalesce(s.contains_protein,false) = false
SET s.precheck_vi = coalesce(s.precheck_vi, 'Xac nhan vai + hut dau truoc (N3) — khong say khi con dau'),
    s.motion_vi = coalesce(s.motion_vi, 'Hut bot → xit/tham mat trai → cha nhe vong tron ngoai→trong'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Am 30-40C sau khi da tay dau; cotton co the am hon neu nhan cho phep'),
    s.aftercare_vi = coalesce(s.aftercare_vi, 'Het cam giac nhon + kiem tra truoc say. Con loang → lap D1/D2')
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_tannin", """
MATCH (s:Stain) WHERE s.contains_tannin = true AND coalesce(s.contains_protein,false) = false AND coalesce(s.contains_oil,false) = false
SET s.precheck_vi = coalesce(s.precheck_vi, 'Xu ly SOM + nuoc lanh; test goc khuat truoc acid/tay'),
    s.motion_vi = coalesce(s.motion_vi, 'Tham mat trai, ngoai→trong — khong cha lan mau'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Nuoc lanh luc dau; sau A3 co the giat am nhe neu vai cho phep'),
    s.aftercare_vi = coalesce(s.aftercare_vi, 'Kiem tra mau con lai truoc say; B1 neu con mau (khong len/lua)')
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_dye", """
MATCH (s:Stain) WHERE s.contains_dye = true AND coalesce(s.contains_oil,false) = false AND coalesce(s.contains_protein,false) = false AND coalesce(s.contains_tannin,false) = false
SET s.precheck_vi = coalesce(s.precheck_vi, 'Test phai mau o goc khuat; xac nhan muc but hay but long'),
    s.motion_vi = coalesce(s.motion_vi, 'CHAM/THAM tu mat trai — TUYET DOI khong cha lan'),
    s.water_temp_vi = coalesce(s.water_temp_vi, 'Phong nhiet; giat lanh/am nhe sau khi het muc'),
    s.aftercare_vi = coalesce(s.aftercare_vi, 'Kiem tra ky truoc say — nhiet khoa mau muc')
RETURN count(s) AS updated""")
        _r(s, "U_stain_ops_overrides", """
UNWIND [
  {id:'S_BLOOD_FRESH',precheck_vi:'Mau tuoi — uu tien ngay, chi nuoc lanh',motion_vi:'Xa mat trai, tham — Cap luc 1, khong cha',water_temp_vi:'Chi nuoc LANH',aftercare_vi:'Kiem tra truoc say; con nau → E1'},
  {id:'S_INK_PEN',precheck_vi:'Test goc khuat; lot giay tham duoi',motion_vi:'Cham A1 mat trai, thay khan — khong cha',water_temp_vi:'Xu ly o nhiet do phong; giat lanh sau',aftercare_vi:'Het muc moi say'},
  {id:'S_INK_PERMANENT',precheck_vi:'But long kho — test vai; co the khong het 100%',motion_vi:'A2/A1 cham nhe mat trai',water_temp_vi:'Nhiet phong',aftercare_vi:'Thong bao khach neu con vet'},
  {id:'S_MOTORBIKE_OIL',precheck_vi:'Dau nhot xe may — thong gio khi dung D1',motion_vi:'N3 day 2 lan → D1 → A1 cham → D3',water_temp_vi:'Giat am/nong chi cotton-poly; khong silk/wool',aftercare_vi:'Kiem tra nhon truoc say'},
  {id:'S_LATERITE',precheck_vi:'Dat do — de KHO roi chai bot truoc',motion_vi:'Chai kho → xa lanh → A3 → B1',water_temp_vi:'Lanh/am; khong say khi con mau do',aftercare_vi:'Lap lai neu con sat oxit'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.precheck_vi = o.precheck_vi, s.motion_vi = o.motion_vi,
    s.water_temp_vi = o.water_temp_vi, s.aftercare_vi = o.aftercare_vi
RETURN count(s) AS updated""")
        _r(s, "V_chem_dilution", """
UNWIND [
  {code:'E1',dilution_vi:'1 muong canh / 1 lit nuoc lanh; khuay tan, ngam 15-60 phut'},
  {code:'N2',dilution_vi:'2 muong canh / 1 lit nuoc lanh (mau tuoi)'},
  {code:'A3',dilution_vi:'1 phan giam / 4 phan nuoc (khu mui / tannin)'},
  {code:'A5',dilution_vi:'1 muong canh / 1 coc nuoc — KHONG tron B2'},
  {code:'A4',dilution_vi:'Dung 3% nguyen (vai trang cotton)'},
  {code:'A1',dilution_vi:'Cham bang bong/khan — khong do ngap'},
  {code:'D2',dilution_vi:'1-2 giot nguyen chat len vet hoac pha loang nhe'},
  {code:'S1',dilution_vi:'Theo huong dan chai Wash Friends — uu tien lua/len'}
] AS d
MATCH (c:Chemical {code:d.code})
SET c.dilution_vi = d.dilution_vi
RETURN count(c) AS updated""")
        _r(s, "W_tool_links", """
MATCH (soft:Tool {id:'T_BRUSH_SOFT'}), (hard:Tool {id:'T_BRUSH_HARD'}),
      (ultra:Tool {id:'T_BRUSH_ULTRA'}), (cloth:Tool {id:'T_CLOTH'}), (spray:Tool {id:'T_SPRAY'})
WITH soft, hard, ultra, cloth, spray
MATCH (s:Stain)
FOREACH (_ IN CASE WHEN s.contains_oil = true OR s.contains_tannin = true THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(soft) MERGE (s)-[:USES_TOOL]->(cloth))
FOREACH (_ IN CASE WHEN s.contains_dye = true THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(cloth) MERGE (s)-[:USES_TOOL]->(soft))
FOREACH (_ IN CASE WHEN s.contains_protein = true THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(cloth) MERGE (s)-[:USES_TOOL]->(ultra))
FOREACH (_ IN CASE WHEN s.id IN ['S_MOTORBIKE_OIL','S_ENGINE_OIL','S_MUD','S_LATERITE'] THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(hard))
FOREACH (_ IN CASE WHEN s.contains_tannin = true OR s.id STARTS WITH 'S_INK' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_TOOL]->(spray))
RETURN count(DISTINCT s) AS stains""")
        _r(s, "X_fabric_hints", """
UNWIND [
  {id:'F1',dry_hint_vi:'Say may OK neu sach; uu tien bong mat + quat',iron_hint_vi:'Ui 180-200C khi con am'},
  {id:'F2',dry_hint_vi:'Say nhiet thap; tranh nhiet cao (bong)',iron_hint_vi:'Ui thap 110-130C'},
  {id:'F3',dry_hint_vi:'KHONG say may — phoi phang bong mat',iron_hint_vi:'Hoi nuoc + lot vai, khong ui truc tiep'},
  {id:'F4',dry_hint_vi:'KHONG say may — bong mat',iron_hint_vi:'110C mat trai + lot, TAT hoi'},
  {id:'F5',dry_hint_vi:'Phoi/say vua; ui khi am',iron_hint_vi:'Ui cao 200-220C khi am'},
  {id:'F6',dry_hint_vi:'Say vua; lan dau giat rieng mau',iron_hint_vi:'Ui vua neu can'},
  {id:'F7',dry_hint_vi:'KHONG say may neu co the',iron_hint_vi:'Nhiet thap, can than'}
] AS h
MATCH (f:Fabric {id:h.id})
SET f.dry_hint_vi = h.dry_hint_vi, f.iron_hint_vi = h.iron_hint_vi
RETURN count(f) AS updated""")
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
   why_vi:'Mau = hemoglobin (protein + sat). Nuoc nong/say bien tinh protein, sat bam soi tao vet nau vinh vien. Chi nuoc LANH ban dau.',
   fresh_path_vi:'LAT mat trai, xa nuoc LANH manh day mau ra; N2 ngam neu can; con nhat → E1. KHONG nuoc nong, KHONG say khi con vet.',
   dried_path_vi:'Da kho/nau: E1 ngam lanh; cotton TRANG con mau co the A4 3% test goc khuat 10-15 phut; len/lua tranh E1/A4 — dung S1 + bao khach.'},
  {id:'S_BLOOD_DRY',
   why_vi:'Mau kho: protein da gan soi. Can enzyme pha chuoi protein; nhiet van cam truoc khi sach.',
   fresh_path_vi:'Neu con am: xu ly nhu mau tuoi — xa lanh mat trai truoc.',
   dried_path_vi:'E1 ngam/cham; A4 chi vai trang sau khi test; kiem tra ky truoc say.'},
  {id:'S_MOTORBIKE_OIL',
   why_vi:'Dau nhot xe may: dau kho + carbon. Can hut N3 + dung moi D1, thong gio.',
   fresh_path_vi:'N3 day → D1 cham → A1 neu can → D3/giat cotton-poly.',
   dried_path_vi:'N3 2 lan → D1 lap → kiem tra nhon truoc say. Khong silk/wool nhiet cao.'},
  {id:'S_BLACK_COFFEE',
   why_vi:'Ca phe den = tannin + mau. Xu ly som nuoc lanh; A3 ho tro; say som khoa mau.',
   fresh_path_vi:'Tham/xa lanh mat trai → A3 1:4 → giat.',
   dried_path_vi:'A3 → B1 neu con mau (khong len/lua) → kiem tra truoc say.'},
  {id:'S_MILK_COFFEE',
   why_vi:'Ca phe sua: tannin + protein sua. Xu ly protein (E1/lanh) truoc, roi tannin (A3).',
   fresh_path_vi:'Xa lanh → E1 neu can cho phan sua → A3 cho tannin → giat.',
   dried_path_vi:'E1 ngam lanh → A3 → kiem tra truoc say; B1 chi khi con mau va vai cho phep.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.why_vi = o.why_vi, s.fresh_path_vi = o.fresh_path_vi, s.dried_path_vi = o.dried_path_vi
RETURN count(s) AS updated""")
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
