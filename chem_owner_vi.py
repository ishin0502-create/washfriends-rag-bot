# -*- coding: utf-8 -*-
"""Owner-facing Vietnamese chemical labels (shop language, with diacritics).

Single source for CHEM_META / Neo4j Chemical seed / chem_explain cards.
Never teach franchise staff with English-only names like 「Enzyme protease」 alone.
"""
from __future__ import annotations

from typing import Any

# code → owner VI fields
CHEM_OWNER_VI: dict[str, dict[str, str]] = {
    "E1": {
        "name_vi": "Enzyme phân giải đạm (protease)",
        "shop_name_vi": "Nước giặt / bột ngâm có enzyme (nhãn ghi enzyme)",
        "buy_where_vi": "Siêu thị — kệ giặt",
        "dilution_vi": (
            "1 muỗng / 1L nước lạnh (hoặc theo nhãn) → ngâm 15–60 phút. "
            "CẤM lụa/len — chuyển sang nước giặt trung tính. "
            "CẤM ngâm cùng Javel."
        ),
        "when_use_vi": (
            "Vết protein: máu, chất nôn, trứng, sữa, mồ hôi… "
            "Phá chuỗi đạm để dễ giặt. Không phải thuốc tẩy màu."
        ),
        "forbid_vi": "CẤM lụa, len. CẤM trộn Javel/amoniac.",
        "aliases": (
            "enzyme protease", "protease", "enzyme phan giai dam", "e1",
            "bot ngam enzyme", "nuoc giat enzyme", "enzyme đạm", "enzyme dam",
        ),
    },
    "E2": {
        "name_vi": "Enzyme phân giải tinh bột (amylase)",
        "shop_name_vi": "Nước giặt enzyme (tinh bột) / bột ngâm amylase",
        "buy_where_vi": "Siêu thị — kệ giặt",
        "dilution_vi": (
            "1 muỗng canh / 1L nước lạnh (hoặc theo nhãn) → ngâm 15–60 phút. "
            "CẤM lụa/len. CẤM cùng Javel."
        ),
        "when_use_vi": "Vết tinh bột: sốt, cơm, bột… Hỗ trợ giặt sau khi làm sạch bề mặt.",
        "forbid_vi": "CẤM lụa, len. CẤM trộn Javel.",
        "aliases": ("enzyme amylase", "amylase", "e2", "tinh bot"),
    },
    "E3": {
        "name_vi": "Enzyme phân giải dầu mỡ (lipase)",
        "shop_name_vi": "Nước giặt enzyme (dầu mỡ) / lipase",
        "buy_where_vi": "Siêu thị — kệ giặt",
        "dilution_vi": (
            "Theo nhãn; thường 1 muỗng / 1L ấm nhẹ → ngâm 15–30 phút sau khi khử dầu bằng nước rửa chén."
        ),
        "when_use_vi": "Vết dầu mỡ cứng đầu sau bước nước rửa chén / bột hút dầu.",
        "forbid_vi": "Cẩn thận lụa/len — ưu tiên nước giặt trung tính nếu nghi ngờ.",
        "aliases": ("enzyme lipase", "lipase", "e3"),
    },
    "D2": {
        "name_vi": "Nước rửa chén (trung tính)",
        "shop_name_vi": "Nước rửa chén",
        "buy_where_vi": "Siêu thị",
        "dilution_vi": "1–2 giọt nguyên lên vết hoặc pha loãng nhẹ; chấm ngoài→trong.",
        "when_use_vi": "Khử dầu nhẹ–trung bình, hầu hết vải (kể cả lụa/len khi pha rất nhẹ).",
        "forbid_vi": "Không thay Javel. Không trộn hóa chất tẩy mạnh.",
        "aliases": ("nuoc rua chen", "nước rửa chén", "dish soap", "d2", "rua chen"),
    },
    "D1": {
        "name_vi": "Dung môi tẩy dầu (degreaser)",
        "shop_name_vi": "Dung môi tẩy dầu / tẩy nhớt",
        "buy_where_vi": "Cửa ô tô / cửa hóa chất — BẮT BUỘC thông gió",
        "dilution_vi": "Theo nhãn chai; ít nước, khăn, không ngâm dài. Gang tay + thông gió.",
        "when_use_vi": "Dầu máy, nhớt xe — sau khi đã thấm bột hút dầu nếu có.",
        "forbid_vi": "CẤM lụa/len khi có thể. CẤM dùng trong phòng kín.",
        "aliases": ("dung moi tay dau", "degreaser", "d1", "tay nhot"),
    },
    "D3": {
        "name_vi": "Bột / nước giặt mạnh",
        "shop_name_vi": "Nước giặt / bột giặt đậm",
        "buy_where_vi": "Siêu thị",
        "dilution_vi": "Theo nhãn máy giặt; không dùng thay enzyme trên lụa/len.",
        "when_use_vi": "Giặt chính sau khi xử lý cục bộ vết bẩn.",
        "forbid_vi": "Không ưu tiên trên lụa/len — dùng nước giặt trung tính.",
        "aliases": ("bot giat", "nuoc giat manh", "d3"),
    },
    "A3": {
        "name_vi": "Giấm trắng khoảng 5%",
        "shop_name_vi": "Giấm trắng ăn / giấm tinh",
        "buy_where_vi": "Siêu thị",
        "dilution_vi": (
            "1 phần giấm + 4 phần nước → chấm/ngâm 5–15 phút. "
            "CẤM trộn Javel hoặc amoniac."
        ),
        "when_use_vi": "Vết tannin (cà phê, trà, rượu, chất nôn sau enzyme) — phá liên kết màu, khử mùi.",
        "forbid_vi": "CẤM trộn Javel/amoniac. Thận trọng lụa/len — test góc.",
        "aliases": ("giam trang", "giấm", "giam", "vinegar", "a3"),
    },
    "A1": {
        "name_vi": "Cồn isopropyl (sát khuẩn)",
        "shop_name_vi": "Cồn y tế / cồn sát khuẩn 70–90%",
        "buy_where_vi": "Nhà thuốc, siêu thị",
        "dilution_vi": "Nguyên hoặc theo nhãn — test góc, thông gió.",
        "when_use_vi": "Mực, son, một số màu curcumin — thấm khăn mặt trái.",
        "forbid_vi": "Xa lửa. Test màu trước.",
        "aliases": ("con isopropyl", "cồn", "alcohol", "a1", "con y te"),
    },
    "A2": {
        "name_vi": "Acetone (tẩy sơn móng)",
        "shop_name_vi": "Acetone / nước tẩy sơn móng không dầu",
        "buy_where_vi": "Nhà thuốc, cửa hóa chất",
        "dilution_vi": (
            "Nguyên rất ít — thấm khăn mặt trái Cap1 (giấy thấm dưới). "
            "CẤM vải acetate/rayon/triacetate. Thông gió + găng."
        ),
        "when_use_vi": "Kẹo cao su, sơn móng, một số keo — không dùng trên acetate.",
        "forbid_vi": "CẤM acetate, rayon, triacetate. CẤM lụa/len nếu có lựa chọn khác.",
        "aliases": ("acetone", "a2", "tay son mong", "nail polish remover"),
    },
    "A4": {
        "name_vi": "Oxy già 3% (hydrogen peroxide)",
        "shop_name_vi": "Oxy già 3% / hydrogen peroxide",
        "buy_where_vi": "Nhà thuốc",
        "dilution_vi": "Theo nhãn; thường dùng trên đồ trắng — test góc.",
        "when_use_vi": "Làm sáng nhẹ vết còn lại trên cotton trắng sau enzyme/giấm.",
        "forbid_vi": "CẨN thận màu/lụa/len. Không thay Javel lung tung.",
        "aliases": ("oxy gia", "hydrogen peroxide", "a4", "peroxide"),
    },
    "A5": {
        "name_vi": "Amoniac pha loãng",
        "shop_name_vi": "Nước amoniac / ammonia pha",
        "buy_where_vi": "Cửa hóa chất",
        "dilution_vi": "Pha loãng theo nhãn. CẤM trộn Javel (khí độc).",
        "when_use_vi": "Protein cũ khó — chỉ khi được đào tạo; ưu tiên enzyme trước.",
        "forbid_vi": "CẤM trộn Javel. CẤM dùng bừa trên lụa/len.",
        "aliases": ("ammonia", "amoniac", "a5"),
    },
    "B1": {
        "name_vi": "Bột tẩy oxy (an toàn màu hơn Javel)",
        "shop_name_vi": "Bột tẩy oxy / tẩy màu an toàn (oxy)",
        "buy_where_vi": "Siêu thị — kệ giặt",
        "dilution_vi": (
            "CHỈ đồ trắng + test góc. Theo nhãn; thường 1–2 muỗng / 1L lạnh–ấm → 15–45 phút. "
            "CẤM màu / chưa rõ màu / lụa / len."
        ),
        "when_use_vi": "Tẩy sáng vết còn lại trên cotton/linen trắng sau bước enzyme hoặc giấm.",
        "forbid_vi": "CẤM lụa, len, đồ màu, chưa xác nhận màu trắng.",
        "aliases": ("bot tay oxy", "tay oxy", "oxygen bleach", "b1", "oxy"),
    },
    "B2": {
        "name_vi": "Nước Javel (tẩy clo)",
        "shop_name_vi": "Nước Javel / nước tẩy trắng",
        "buy_where_vi": "Siêu thị",
        "dilution_vi": (
            "CHỈ cotton TRẮNG. Ví dụ: Javel đặc 1 : nước 10–20 (ưu tiên nhãn) · ngâm ngắn · xả ngay. "
            "CẤM màu/lụa/len/acetate. CẤM trộn giấm hoặc amoniac."
        ),
        "when_use_vi": "Tẩy mạnh đồ cotton trắng — không dùng như bước đầu cho mọi vết.",
        "forbid_vi": "CẤM màu, lụa, len, acetate. CẤM trộn giấm/amoniac/enzyme cùng bồn.",
        "aliases": ("javel", "javelle", "chlorine", "b2", "nuoc tay trang", "clo"),
    },
    "N1": {
        "name_vi": "Baking soda (bicarbonate)",
        "shop_name_vi": "Bột baking soda / muối nở",
        "buy_where_vi": "Siêu thị, tiệm bánh",
        "dilution_vi": "Rắc hoặc pha nhão nhẹ; sau acid oxalic có thể dùng để trung hòa loãng.",
        "when_use_vi": "Khử mùi, hỗ trợ curcumin/kiềm nhẹ, trung hòa sau acid.",
        "forbid_vi": "Không thay enzyme cho máu tươi.",
        "aliases": ("baking soda", "muoi no", "n1", "bicarbonate"),
    },
    "N2": {
        "name_vi": "Muối ăn",
        "shop_name_vi": "Muối tinh",
        "buy_where_vi": "Siêu thị",
        "dilution_vi": "Rắc / dung dịch mặn lạnh cho máu tươi — không chà nóng.",
        "when_use_vi": "Máu tươi, một số tannin — bước hỗ trợ sớm.",
        "forbid_vi": "Không dùng nước nóng với máu.",
        "aliases": ("muoi an", "muoi tinh", "salt", "n2"),
    },
    "N3": {
        "name_vi": "Bột hút dầu (bột bắp / phấn rôm)",
        "shop_name_vi": "Bột bắp / phấn rôm / bột năng (không dầu)",
        "buy_where_vi": "Siêu thị",
        "dilution_vi": "Phủ dày lên vết dầu 10–30 phút rồi phủi — trước nước rửa chén.",
        "when_use_vi": "Bước đầu mọi vết dầu mỡ — hút dầu trước khi giặt.",
        "forbid_vi": "Không sấy khi còn nhờn.",
        "aliases": ("bot ngo", "bot bap", "phan rom", "starch", "n3", "cornstarch"),
    },
    "S1": {
        "name_vi": "Nước giặt trung tính Wash Friends",
        "shop_name_vi": "Nước giặt trung tính do Wash Friends cung cấp",
        "buy_where_vi": "Kho hàng / cung ứng Wash Friends",
        "dilution_vi": "Theo hướng dẫn chai Wash Friends — ưu tiên lụa/len.",
        "when_use_vi": "Bắt buộc ưu tiên khi cần giặt trung tính / lụa / len / vải nhạy.",
        "forbid_vi": "Không thay bằng enzyme mạnh trên lụa/len.",
        "aliases": ("nuoc giat trung tinh", "s1", "wash friends", "trung tinh"),
    },
    "X1": {
        "name_vi": "Bột tẩy khử (sodium hydrosulfite)",
        "shop_name_vi": "Bột tẩy khử / sodium hydrosulfite (hóa chất chuyên)",
        "buy_where_vi": "Cửa hóa chất chuyên dụng — găng tay, pha mới",
        "dilution_vi": (
            "1 muỗng / 1L nước 40–50°C — PHA MỚI, không để lâu. "
            "CHỈ cotton/linen trắng khi bột oxy thất bại. Xả lạnh ngay."
        ),
        "when_use_vi": "Vàng ố nặng không hết với bột oxy — chỉ cotton/linen trắng + PPE.",
        "forbid_vi": "CẤM đồ màu / lụa / len / da. CẤM trộn Javel.",
        "aliases": ("tay khu", "hydrosulfite", "x1", "reducing bleach"),
    },
    "X2": {
        "name_vi": "Acid oxalic (tẩy rỉ sắt)",
        "shop_name_vi": "Acid oxalic / bột tẩy rỉ (hóa chất)",
        "buy_where_vi": "Cửa hóa chất — BẮT BUỘC găng tay",
        "dilution_vi": (
            "Acid oxalic khoảng 2–3% theo nhãn; cotton/linen/poly ~30 phút; "
            "xả kỹ rồi trung hòa baking soda loãng. CẤM lụa/len — chỉ giấm nhẹ."
        ),
        "when_use_vi": "Rỉ sét / đất đỏ laterite (sắt ôxít). PPE bắt buộc.",
        "forbid_vi": "CẤM Javel trên vết sắt (cố định sắt). CẤM lụa/len dùng X2.",
        "aliases": ("acid oxalic", "oxalic", "x2", "tay ri", "ri set"),
    },
    "L1": {
        "name_vi": "Dung dịch vệ sinh da (leather cleaner)",
        "shop_name_vi": "Dung dịch / xịt vệ sinh da",
        "buy_where_vi": "Cửa đồ da, siêu thị đồ gia dụng / giày",
        "dilution_vi": "Theo nhãn — ít nước, khăn, không ngâm.",
        "when_use_vi": "Da bóng: lau vết / bảo dưỡng. CẤM suede/nubuck ngâm nước.",
        "forbid_vi": "CẤM bột giặt / Javel trên da.",
        "aliases": ("leather cleaner", "l1", "ve sinh da"),
    },
    "L2": {
        "name_vi": "Kem dưỡng da (leather cream)",
        "shop_name_vi": "Kem da / conditioner da",
        "buy_where_vi": "Cửa đồ da, cửa giày",
        "dilution_vi": "Nguyên chất — bôi mỏng, đều, lau dư.",
        "when_use_vi": "BẮT BUỘC sau xử lý mốc/vết trên da bóng — khi da đã khô.",
        "forbid_vi": "CẤM bôi dầu ăn / vaseline.",
        "aliases": ("leather cream", "kem da", "l2", "conditioner da"),
    },
    "L3": {
        "name_vi": "Xịt bảo vệ da (protector)",
        "shop_name_vi": "Xịt chống thấm / protector da–giày",
        "buy_where_vi": "Cửa giày, siêu thị",
        "dilution_vi": "Xịt nhẹ 20–30cm, để khô theo nhãn. Thông gió.",
        "when_use_vi": "Sau kem da khô — bảo vệ. Không thay kem dưỡng.",
        "forbid_vi": "Suede: chỉ xịt suede/nubuck riêng.",
        "aliases": ("protector", "xit bao ve da", "l3"),
    },
    "WF_SOFT": {
        "name_vi": "Nước xả Softener Wash Friends",
        "shop_name_vi": "Nước xả / làm mềm vải Wash Friends",
        "buy_where_vi": "Kho hàng Wash Friends",
        "dilution_vi": "Theo liều máy / hướng dẫn kho.",
        "when_use_vi": "Chỉ khi hoàn thiện / xả vải — không nhắc mỗi câu vết bẩn.",
        "forbid_vi": "Giảm liều nếu khách ghét hương đậm.",
        "aliases": ("softener", "nuoc xa", "wf_soft", "xa vai"),
    },
    "WF_FRAG": {
        "name_vi": "Xịt hương Đức Wash Friends",
        "shop_name_vi": "Xịt hương (Đức) Wash Friends",
        "buy_where_vi": "Kho hàng Wash Friends",
        "dilution_vi": "Xịt nhẹ — đừng quá nhiều.",
        "when_use_vi": "Đồ cao cấp / sau ủi / khách ghét mùi giặt khô — xịt nhẹ.",
        "forbid_vi": "Không nhắc nếu chỉ hỏi xử lý vết bẩn.",
        "aliases": ("xit huong", "wf_frag", "fragrance"),
    },
}


def apply_owner_vi_to_chem_meta(chem_meta: dict[str, dict[str, str]]) -> None:
    """Mutate CHEM_META in place with owner VI fields."""
    for code, own in CHEM_OWNER_VI.items():
        slot = chem_meta.setdefault(code, {})
        for k in ("name_vi", "dilution_vi"):
            if own.get(k):
                slot[k] = own[k]
        # Keep shop fields available for explain/seed even if CHEM_META historically lacked them
        for k in ("shop_name_vi", "buy_where_vi", "when_use_vi", "forbid_vi"):
            if own.get(k):
                slot[k] = own[k]


def chem_seed_overlay_rows() -> list[dict[str, Any]]:
    """Neo4j Chemical SET rows from owner VI catalog."""
    rows = []
    for code, own in CHEM_OWNER_VI.items():
        rows.append(
            {
                "code": code,
                "name_vi": own.get("name_vi") or "",
                "shop_name_vi": own.get("shop_name_vi") or "",
                "buy_where_vi": own.get("buy_where_vi") or "",
                "dilution_vi": own.get("dilution_vi") or "",
                "when_use_vi": own.get("when_use_vi") or "",
            }
        )
    return rows


def match_chem_code(text: str, prefer_codes: list[str] | None = None) -> str:
    """Return best chem code from user text + optional session preference."""
    import unicodedata

    raw = unicodedata.normalize("NFKC", (text or "")).lower()
    prefer = [c.upper() for c in (prefer_codes or []) if c]

    # Explicit code tokens
    for code in list(prefer) + list(CHEM_OWNER_VI.keys()):
        if re_code_in_text(code, raw):
            return code

    # Alias scan — prefer session chems first
    ordered = prefer + [c for c in CHEM_OWNER_VI if c not in prefer]
    best = ""
    best_len = 0
    for code in ordered:
        for alias in CHEM_OWNER_VI[code].get("aliases") or ():
            a = str(alias).lower()
            if a and a in raw and len(a) >= best_len:
                best = code
                best_len = len(a)
    if best:
        return best

    # Generic "enzyme" with session E1/E2/E3
    if "enzyme" in raw or "men " in raw:
        for c in ("E1", "E2", "E3"):
            if c in prefer:
                return c
        return "E1"
    return ""


def re_code_in_text(code: str, raw: str) -> bool:
    import re

    return bool(re.search(rf"(?<![a-z0-9]){re.escape(code.lower())}(?![a-z0-9])", raw))


def owner_card(code: str, *, lang: str = "vi") -> dict[str, str]:
    code = (code or "").upper()
    own = dict(CHEM_OWNER_VI.get(code) or {})
    own["code"] = code
    return own


def enrich_graph_chemicals_vi(graph: dict) -> dict:
    """Overwrite chemicals[] VI display fields from owner catalog."""
    if not isinstance(graph, dict):
        return graph
    out = dict(graph)
    chems = []
    for c in out.get("chemicals") or []:
        if not c:
            continue
        row = dict(c)
        code = str(row.get("code") or "").upper()
        own = CHEM_OWNER_VI.get(code) or {}
        if own:
            row["name_vi"] = own.get("name_vi") or row.get("name_vi")
            row["shop_name_vi"] = own.get("shop_name_vi") or row.get("shop_name_vi")
            row["buy_where_vi"] = own.get("buy_where_vi") or row.get("buy_where_vi")
            row["dilution_vi"] = own.get("dilution_vi") or row.get("dilution_vi")
            row["when_use_vi"] = own.get("when_use_vi") or row.get("when_use_vi")
        chems.append(row)
    out["chemicals"] = chems
    return out
