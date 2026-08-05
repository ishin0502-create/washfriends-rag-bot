import json, urllib.request
for name, msg in [("ask_vi.json", "vet dat do laterite tren quan jean"), ("ask_en.json", "laterite soil on jeans")]:
    open(name, "w", encoding="utf-8").write(json.dumps({"message": msg}))
print("wrote files")
