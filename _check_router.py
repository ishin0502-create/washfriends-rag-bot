import re
from pathlib import Path
src = Path("graphrag_engine.py").read_text(encoding="utf-8")
m = re.search(r"def _fetch_graph_context\b.*?(?=\ndef |\Z)", src, re.S)
if not m:
    print("FUNC_NOT_FOUND")
else:
    body = m.group(0)
    returns = re.findall(r"^\s*return context\s*$", body, re.M)
    print("return_context_count=", len(returns))
    daily_m = re.search(r"['\"]daily['\"]", body)
    mystery_m = re.search(r"['\"]mystery['\"]", body)
    qfull = body.find("Q_FULL_CONTEXT")
    print("daily_pos=", daily_m.start() if daily_m else -1)
    print("mystery_pos=", mystery_m.start() if mystery_m else -1)
    print("Q_FULL_CONTEXT_pos=", qfull)
    if daily_m and mystery_m and qfull >= 0:
        print("intents_before_Q_FULL_CONTEXT=", daily_m.start() < qfull and mystery_m.start() < qfull)
    q_assign = re.search(r"Q_FULL_CONTEXT\s*=\s*(?:[ruf]|fr|rf)?(\"\"\"|\'\'\'|\"|\')", src)
    if q_assign:
        quote = q_assign.group(1)
        start = q_assign.end()
        if quote in ('"""', "'''"):
            end = src.find(quote, start)
        else:
            end = src.find(quote, start)
        qtext = src[start:end]
        print("Q_FULL_CONTEXT_has_stain_id=", "stain_id" in qtext)
        for line in qtext.splitlines():
            if "stain" in line.lower():
                print("Q:", line.strip()[:180])
    else:
        print("Q_FULL_CONTEXT_assign_not_found")
    # also show intent-related lines in function
    for i, line in enumerate(body.splitlines(), 1):
        if any(x in line for x in ("daily", "mystery", "Q_FULL_CONTEXT", "return context", "stain_id")):
            print(f"F{i}: {line.rstrip()[:140]}")
