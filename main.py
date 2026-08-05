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
            "build": "2026-08-05-ask-errdetail",
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
  {code:'E1',name:'Protease Enzyme',name_vi:'Enzyme protease',role:'Breaks protein chains',safe_on_wool:false,safe_on_silk:false},
  {code:'E2',name:'Amylase Enzyme',name_vi:'Enzyme amylase',role:'Breaks starch',safe_on_wool:false,safe_on_silk:false},
  {code:'E3',name:'Lipase Enzyme',name_vi:'Enzyme lipase',role:'Breaks fat/oil',safe_on_wool:false,safe_on_silk:false},
  {code:'D1',name:'Solvent Degreaser',name_vi:'Dung moi tay dau',role:'Dissolves heavy oil - use with ventilation',safe_on_wool:false,safe_on_silk:false},
  {code:'D2',name:'Dish Soap',name_vi:'Nuoc rua chen',role:'Mild surfactant safe for most fabrics',safe_on_wool:true,safe_on_silk:true},
  {code:'D3',name:'Strong Detergent',name_vi:'Bot giat manh',role:'Heavy-duty washing detergent',safe_on_wool:false,safe_on_silk:false},
  {code:'B1',name:'Oxygen Bleach',name_vi:'Tay oxy',role:'Color-safe bleach',safe_on_wool:false,safe_on_silk:false},
  {code:'B2',name:'Chlorine Bleach',name_vi:'Javel',role:'Strong bleach WHITE cotton ONLY',safe_on_wool:false,safe_on_silk:false},
  {code:'A1',name:'Isopropyl Alcohol',name_vi:'Con isopropyl',role:'Dissolves pigments ink polish curcumin',safe_on_wool:false,safe_on_silk:false},
  {code:'A2',name:'Acetone',name_vi:'Acetone',role:'Strong solvent for polymer stains gum nail polish',safe_on_wool:false,safe_on_silk:false},
  {code:'A3',name:'White Vinegar 5%',name_vi:'Giam trang 5%',role:'Mild acid breaks tannin bonds neutralizes alkali odor',safe_on_wool:false,safe_on_silk:false},
  {code:'A4',name:'Hydrogen Peroxide 3%',name_vi:'Hydrogen peroxide 3%',role:'Light oxidizer for white fabrics',safe_on_wool:false,safe_on_silk:false},
  {code:'A5',name:'Diluted Ammonia',name_vi:'Ammonia pha loang',role:'Mild alkali for old protein - NEVER mix with bleach',safe_on_wool:false,safe_on_silk:false},
  {code:'N1',name:'Baking Soda',name_vi:'Baking soda',role:'Mild abrasive odor absorber alkaline for curcumin',safe_on_wool:true,safe_on_silk:false},
  {code:'N2',name:'Table Salt',name_vi:'Muoi an',role:'Draws out fresh blood and tannin',safe_on_wool:true,safe_on_silk:true},
  {code:'N3',name:'Corn Starch/Talc',name_vi:'Bot ngo/bot talc',role:'Oil absorber first step for all oil stains',safe_on_wool:true,safe_on_silk:true},
  {code:'S1',name:'Silk/Wool Detergent',name_vi:'Nuoc giat to lua',role:'pH-neutral for delicate protein fibers',safe_on_wool:true,safe_on_silk:true}
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
