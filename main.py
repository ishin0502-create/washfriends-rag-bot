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
            "build": "2026-08-06-audit-fix-v1",
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
  'S_GLUE','S_PAINT_LATEX','S_MUSTARD','S_CURRY'
]
OPTIONAL MATCH (s)-[old:USES_CHEMICAL]->()
DELETE old
WITH DISTINCT s
MATCH (a1:Chemical {code:'A1'}),(a2:Chemical {code:'A2'}),(a3:Chemical {code:'A3'}),
      (b1:Chemical {code:'B1'}),(d1:Chemical {code:'D1'}),(d2:Chemical {code:'D2'}),
      (d3:Chemical {code:'D3'}),(n1:Chemical {code:'N1'}),(n3:Chemical {code:'N3'})
FOREACH (_ IN CASE WHEN s.id = 'S_RUST' THEN [1] ELSE [] END |
  MERGE (s)-[:USES_CHEMICAL]->(a3))
FOREACH (_ IN CASE WHEN s.id = 'S_GUM' THEN [1] ELSE [] END |
  SET s = s)
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
  {id:'T_SPRAY',name_vi:'Binh xit rieng (dan nhan)',name_ko:'분무기(라벨 필수)',use_for_vi:'Pha loang A3/D2/B1 — khong tron binh'},
  {id:'T_BRUSH_SHOE',name_vi:'Ban chai de giay (long cung)',name_ko:'운동화 밑창용 경질 솔',use_for_vi:'De cao su — KHONG dung tren mesh/lua'}
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
  {id:'S_LATERITE',precheck_vi:'Dat do — de KHO roi chai bot truoc',motion_vi:'Chai kho → xa lanh → A3 → B1',water_temp_vi:'Lanh/am; khong say khi con mau do',aftercare_vi:'Lap lai neu con sat oxit'}
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
  {code:'S1',dilution_vi:'Theo huong dan chai Wash Friends — uu tien lua/len',dilution_ko:'워시프렌즈 중성세제 병 안내 따름 — 실크·울 우선'}
] AS d
MATCH (c:Chemical {code:d.code})
SET c.dilution_vi = d.dilution_vi, c.dilution_ko = d.dilution_ko
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
   why_vi:'Mau = hemoglobin (protein + sat). Nuoc lanh giu protein hoa tan; nuoc nong/say bien tinh → sat bam soi tao vet nau vinh vien. E1 cat chuoi protein; A4 (vai trang) oxy hoa hemoglobin.',
   fresh_path_vi:'(1) Lat mat trai, xa nuoc LANH 2-3 phut den khi nuoc hong→trong. (2) Ngam N2 2 muong/1L lanh 15-30 phut. (3) Con nhat: nho E1 len vet 15 phut. (4) Giat D3 nuoc lanh. KHONG cha manh, KHONG say khi con vet.',
   dried_path_vi:'Neu da kho: cao nhe vay kho → ngam lanh 30-60 phut → E1 pha loang 30-60 phut → chai mem Cap2. Cotton TRANG: A4 3% test goc khuat 10 phut. Len/lua: KHONG E1/A4 — N2 + S1, bao khach.'},
  {id:'S_BLOOD_DRY',
   why_vi:'Mau kho: protein da gan soi. Can enzyme pha chuoi; nhiet van CAM truoc khi sach hoan toan.',
   fresh_path_vi:'Neu con am: xu ly nhu mau tuoi — xa lanh mat trai truoc moi buoc khac.',
   dried_path_vi:'Cao nhe → ngam lanh → E1 30-60 phut → chai mem. A4 chi cotton trang sau test. Kiem tra anh sang manh TRUOC say; con nau → lap E1.'},
  {id:'S_MOTORBIKE_OIL',
   why_vi:'Dau nhot xe may: dau kho + carbon. Can hut N3 + dung moi D1; thong gio khi dung dung moi.',
   fresh_path_vi:'N3 day hut dau → D1 cham mat trai → A1 neu can → D3/giat cotton-poly.',
   dried_path_vi:'N3 2 lan → D1 lap → kiem tra het nhon truoc say. Khong silk/wool nhiet cao.'},
  {id:'S_BLACK_COFFEE',
   why_vi:'Ca phe den = tannin + mau. Xu ly SOM bang nuoc lanh; A3 (giam 1:4) ho tro pha tannin; say som khoa mau.',
   fresh_path_vi:'Tham/xa lanh mat trai ngay → A3 1 phan giam / 4 phan nuoc → giat. Test goc khuat truoc tay manh.',
   dried_path_vi:'A3 ngam/cham → neu con mau dung B1 (KHONG len/lua) → kiem tra mau truoc say.'},
  {id:'S_MILK_COFFEE',
   why_vi:'Ca phe sua: tannin + protein sua. Xu ly protein (E1/lanh) TRUOC, roi tannin (A3) — khong dao thu tu.',
   fresh_path_vi:'Xa lanh → E1 cho phan sua neu can → A3 cho tannin → giat.',
   dried_path_vi:'E1 ngam lanh → A3 → kiem tra truoc say; B1 chi khi con mau va vai cho phep.'}
] AS o
MATCH (s:Stain {id:o.id})
SET s.why_vi = o.why_vi, s.fresh_path_vi = o.fresh_path_vi, s.dried_path_vi = o.dried_path_vi,
    s.tip = coalesce(s.tip, s.why_vi)
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
   precheck_vi:'Giu form vanh. CAM may/say (hong vanh).',
   why_vi:'Mu: tay + giu hinh. Spotting mo hoi vanh truoc. Chi chat giat NHE/trung tinh — CAM bot dam.',
   fresh_path_vi:'Spotting vanh (chat nhe/trung tinh) → tay lanh + chai mem → nhet bat/bong giu form → phoi bong mat. CAM bot giat manh.',
   dried_path_vi:'Lap spotting vanh bang chat nhe. Khong may.',
   motion_vi:'Luc 2 — chai mem, khong vo vanh',
   water_temp_vi:'Lanh. CHI tay',
   aftercare_vi:'Giu form den kho. CAM say may.'},
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
   precheck_vi:'Chup anh + do dien tich phai mau. Phan biet: (a) UV/thoi gian (b) tay hoa chat pha mau (c) loang mau. Thong bao: thuoc nhuom bi pha = kho/khong phuc hoi 100%.',
   why_vi:'Vai mau mat mau: CAM meo ethanol+dau+may say. CAM dung chat giat/trung tinh nhu "phuc hoi mau". Huong dung: nho → but mau vai (tam thoi). Vua/lon → gui nhuom lai / giai thich + boi thuong. Khong xu ly them bang tay manh.',
   fresh_path_vi:'(1) Anh + dong y khach. (2) Nho (<= dong xu): but mau vai phu hop → co dinh nhiet — NO RO co the phai khi giat. (3) Vua/lon: chuyen co so nhuom, khong cam ket khop mau 100%. (4) CAM tron con+dau roi say may. (5) Khong dung detergent/S1 de "phuc hoi mau".',
   dried_path_vi:'Da xu ly sai (tay/oxy len mau): dung lai, chup anh, tu van nhuom/boi thuong. Khong lap tay.',
   motion_vi:'Luc 1 — chi cham but mau neu chon phuong an nho; khong cha',
   water_temp_vi:'Khong giat tay mau tren cho phai; theo nhan neu chi cham soc',
   aftercare_vi:'Ghi ro gioi han phuc hoi. Phoi bong mat sau. Khuyen khach tranh nang. Dung cu: but mau vai / anh ghi chep — KHONG khan tham nhu xu ly vet.'},
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
      (hard:Tool {id:'T_BRUSH_HARD'}), (shoe:Tool {id:'T_BRUSH_SHOE'}), (spray:Tool {id:'T_SPRAY'})
WITH cloth, soft, ultra, hard, shoe, spray
MATCH (d2:Chemical {code:'D2'}), (d3:Chemical {code:'D3'}), (a1:Chemical {code:'A1'}),
      (a4:Chemical {code:'A4'}), (n1:Chemical {code:'N1'}), (b1:Chemical {code:'B1'}),
      (s1:Chemical {code:'S1'})
WITH cloth, soft, ultra, hard, shoe, spray, d2, d3, a1, a4, n1, b1, s1
// Full rewire Item tools/chems (drop stale wrong links)
MATCH (i:Item)
OPTIONAL MATCH (i)-[oldt:USES_TOOL]->()
DELETE oldt
WITH cloth, soft, ultra, hard, shoe, spray, d2, d3, a1, a4, n1, b1, s1, i
OPTIONAL MATCH (i)-[oldc:USES_CHEMICAL]->()
DELETE oldc
WITH cloth, soft, ultra, hard, shoe, spray, d2, d3, a1, a4, n1, b1, s1, i
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
  MERGE (i)-[:USES_TOOL]->(soft) MERGE (i)-[:USES_TOOL]->(cloth)
  MERGE (i)-[:USES_CHEMICAL]->(d2) MERGE (i)-[:USES_CHEMICAL]->(n1))
FOREACH (_ IN CASE WHEN i.id IN ['I_GORETEX','I_DOWN_JACKET','I_GOLF_GLOVE_SYNTH','I_FUR_FAUX'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_CHEMICAL]->(d2) MERGE (i)-[:USES_TOOL]->(cloth))
FOREACH (_ IN CASE WHEN i.id IN ['I_GOLF_WEAR','I_GOLF_HAT','I_SUIT_SUMMER'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth) MERGE (i)-[:USES_CHEMICAL]->(d2))
FOREACH (_ IN CASE WHEN i.id = 'I_GOLF_HAT' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(soft))
FOREACH (_ IN CASE WHEN i.id = 'I_DENIM' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(hard) MERGE (i)-[:USES_TOOL]->(cloth)
  MERGE (i)-[:USES_CHEMICAL]->(d2))
FOREACH (_ IN CASE WHEN i.id = 'I_COLOR_FADE' THEN [1] ELSE [] END |
  // No shop detergent / blot cloth — restore = fabric marker or re-dye (see fresh_path)
  SET i = i)
FOREACH (_ IN CASE WHEN i.id = 'I_WHITE_FADE' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(spray)
  MERGE (i)-[:USES_CHEMICAL]->(b1) MERGE (i)-[:USES_CHEMICAL]->(n1) MERGE (i)-[:USES_CHEMICAL]->(a4))
FOREACH (_ IN CASE WHEN i.id IN ['I_SUIT','I_AO_DAI','I_HANBOK'] THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(ultra) MERGE (i)-[:USES_TOOL]->(cloth)
  MERGE (i)-[:USES_CHEMICAL]->(s1))
FOREACH (_ IN CASE WHEN i.id = 'I_FUR_REAL' THEN [1] ELSE [] END |
  MERGE (i)-[:USES_TOOL]->(cloth))
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
