import json, re
from pathlib import Path
out = Path("_tmp_ask")

def load(p):
    raw = Path(p).read_text(encoding="utf-8", errors="replace")
    try:
        d = json.loads(raw)
    except Exception:
        return raw, raw
    ans = d.get("response") or d.get("answer") or raw
    return ans, raw

lat, lat_raw = load(out/"out_laterite.json")
blood, blood_raw = load(out/"out_blood.json")

tip_keys = ["kho","dry","brush","vinegar","giam","oxy","laterite","dat do","đất đỏ","giấm","khô"]
blood_bad = ["mau tuoi","máu tươi","blood","N2","E1"]
# for laterite verdict: tip-like AND NOT mau tuoi/blood
lat_l = lat.lower()
tip_hits = [k for k in tip_keys if k.lower() in lat_l]
bad_hits = [k for k in ["mau tuoi","máu tươi","blood"] if k.lower() in lat_l]
# also check unicode-normalized loosely
has_mau = ("mau" in lat_l and "tuoi" in lat_l) or "máu" in lat or "mau tuoi" in lat_l
has_blood_chem = "n2" in lat_l or "e1" in lat_l or "muối" in lat or "muoi" in lat_l

fixed = bool(tip_hits) and not has_mau and "blood" not in lat_l
# user said: FIXED if tip-like AND NOT mau tuoi/blood
verdict = "FIXED" if fixed else "STILL_WRONG"

blood_l = blood.lower()
blood_ok = any(k in blood_l for k in ["mau","máu","n2","e1"]) or "muoi" in blood_l or "muối" in blood

print("=== LATERITE SNIPPET ===")
print(lat[:600].replace("\n"," / "))
print("tip_hits=", tip_hits)
print("has_mau/blood=", has_mau, "blood" in lat_l)
print("LATERITE_VERDICT=", verdict)
print()
print("=== BLOOD SNIPPET ===")
print(blood[:600].replace("\n"," / "))
print("blood_markers=", [k for k in ["mau","N2","E1","muoi","enzyme"] if k.lower() in blood_l or k in blood])
print("BLOOD_OK=", blood_ok)
