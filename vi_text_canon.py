# -*- coding: utf-8 -*-
"""ASCII Vietnamese laundry copy → proper diacritics.

Applied at seed (Z16e) and at runtime for VI owner answers.
Longest-phrase replacements first. Domain-specific — not a general translator.
"""
from __future__ import annotations

import re
from typing import Any

# Longer phrases first. Avoid 1–2 letter tokens that break chemistry codes.
_PHRASES: list[tuple[str, str]] = [
    ("GIAO DUC DRILL:", "[Tại sao]"),
    ("GIAO DUC:", "[Tại sao]"),
    ("[Tai sao]", "[Tại sao]"),
    ("THU TU BAT BUOC", "THỨ TỰ BẮT BUỘC"),
    ("THU TU:", "THỨ TỰ:"),
    ("BAT BUOC", "BẮT BUỘC"),
    ("CAM say", "CẤM sấy"),
    ("CAM cha", "CẤM chà"),
    ("CAM nong", "CẤM nóng"),
    ("CAM Javel", "CẤM Javel"),
    ("CAM B2", "CẤM B2"),
    ("CAM A5", "CẤM A5"),
    ("CAM meo", "CẤM mẹo"),
    ("CAM ui", "CẤM ủi"),
    ("CAM clo", "CẤM clo"),
    ("CAM tron", "CẤM trộn"),
    ("nuoc rua chen", "nước rửa chén"),
    ("Nuoc rua chen", "Nước rửa chén"),
    ("bot tay oxy", "bột tẩy oxy"),
    ("Bot tay oxy", "Bột tẩy oxy"),
    ("anh sang manh", "ánh sáng mạnh"),
    ("Anh sang manh", "Ánh sáng mạnh"),
    ("TRUOC say", "TRƯỚC sấy"),
    ("truoc say", "trước sấy"),
    ("mat trai", "mặt trái"),
    ("Mat trai", "Mặt trái"),
    ("ngoai→trong", "ngoài→trong"),
    ("thong gio", "thông gió"),
    ("Thong gio", "Thông gió"),
    ("THONG GIO", "THÔNG GIÓ"),
    ("giam trang", "giấm trắng"),
    ("Giam trang", "Giấm trắng"),
    ("giam 1:4", "giấm 1:4"),
    ("nuoc LANH", "nước LẠNH"),
    ("Nuoc LANH", "Nước LẠNH"),
    ("NUOC LANH", "NƯỚC LẠNH"),
    ("nuoc lanh", "nước lạnh"),
    ("Nuoc lanh", "Nước lạnh"),
    ("xa lanh", "xả lạnh"),
    ("Xa lanh", "Xả lạnh"),
    ("nuoc giat", "nước giặt"),
    ("Nuoc giat", "Nước giặt"),
    ("Mau tuoi", "Máu tươi"),
    ("mau tuoi", "máu tươi"),
    ("pha loang", "pha loãng"),
    ("khong cha", "không chà"),
    ("Khong cha", "Không chà"),
    ("cha lan", "chà lan"),
    ("dung moi", "dung môi"),
    ("Dung moi", "Dung môi"),
    ("dung enzyme", "dùng enzyme"),
    ("gang tay", "găng tay"),
    ("khau trang", "khẩu trang"),
    ("cao bot", "cạo bột"),
    ("Cao bot", "Cạo bột"),
    ("test goc", "test góc"),
    ("goc khuat", "góc khuất"),
    ("theo nhan", "theo nhãn"),
    ("phan biet", "phân biệt"),
    ("Phan biet", "Phân biệt"),
    ("truoc khi", "trước khi"),
    ("sau khi", "sau khi"),
    ("sau do", "sau đó"),
    ("co the", "có thể"),
    ("Co the", "Có thể"),
    ("ty le", "tỷ lệ"),
    ("thanh cong", "thành công"),
    ("vinh vien", "vĩnh viễn"),
    ("VINH VIEN", "VĨNH VIỄN"),
    ("vin vien", "vĩnh viễn"),
    ("bao khach", "báo khách"),
    ("bao truoc", "báo trước"),
    ("tu choi", "từ chối"),
    ("cam ket", "cam kết"),
    ("chuyen nghiep", "chuyên nghiệp"),
    ("chuyen pro", "chuyên pro"),
    ("an toan", "an toàn"),
    ("trung binh", "trung bình"),
    ("nhan giat", "nhãn giặt"),
    ("Nhan giat", "Nhãn giặt"),
    ("ky hieu", "ký hiệu"),
    ("huong dan", "hướng dẫn"),
    ("quan ao", "quần áo"),
    ("ca phe", "cà phê"),
    ("Ca phe", "Cà phê"),
    ("ruou vang", "rượu vang"),
    ("Ruou vang", "Rượu vang"),
    ("nuoc tuong", "nước tương"),
    ("nuoc mam", "nước mắm"),
    ("nuoc hoa", "nước hoa"),
    ("nuoc tieu", "nước tiểu"),
    ("chat non", "chất nôn"),
    ("son moi", "son môi"),
    ("son nuoc", "sơn nước"),
    ("son dau", "sơn dầu"),
    ("son mong", "sơn móng"),
    ("ao so mi", "áo sơ mi"),
    ("o nach", "ở nách"),
    ("vong co", "vòng cổ"),
    ("lo mau", "loang màu"),
    ("tinh bot", "tinh bột"),
    ("sua bot", "sữa bột"),
    ("dau nhot", "dầu nhớt"),
    ("dau an", "dầu ăn"),
    ("bot ngo", "bột ngô"),
    ("phan rom", "phấn rôm"),
    ("phoi nang", "phơi nắng"),
    ("bong mat", "bóng mát"),
    ("giay tham", "giấy thấm"),
    ("doi khan", "đổi khăn"),
    ("chu ky", "chu kỳ"),
    ("trau cau", "trầu cau"),
    ("ri set", "rỉ sét"),
    ("dat do", "đất đỏ"),
    ("nam moc", "nấm mốc"),
    ("sat khuan", "sát khuẩn"),
    ("keo cao su", "kẹo cao su"),
    ("sap nen", "sáp nến"),
    ("len/lua", "len/lụa"),
    ("da say", "đã sấy"),
    ("da kho", "đã khô"),
    ("xu ly", "xử lý"),
    ("Xu ly", "Xử lý"),
    ("anh sang", "ánh sáng"),
    ("Anh sang", "Ánh sáng"),
    ("giam ", "giấm "),
    ("Giam ", "Giấm "),
    ("ngam ", "ngâm "),
    ("Ngam ", "Ngâm "),
    ("KHONG", "KHÔNG"),
    ("khong ", "không "),
    ("Khong ", "Không "),
    ("vet ", "vết "),
    ("Vet ", "Vết "),
    ("(1) Nhan", "(1) Nhận"),
    ("nhan:", "nhận:"),
    ("Nhan:", "Nhận:"),
    ("hoac ", "hoặc "),
    ("neu ", "nếu "),
    ("Neu ", "Nếu "),
    ("dung ", "dùng "),
    ("Dung ", "Dùng "),
    ("giat ", "giặt "),
    ("Giat ", "Giặt "),
    ("say ", "sấy "),
    ("Say ", "Sấy "),
    ("tham ", "thấm "),
    ("Tham ", "Thấm "),
    ("THAM", "THẤM"),
    ("xa ", "xả "),
    ("Xa ", "Xả "),
    ("cao ", "cạo "),
    ("Cao ", "Cạo "),
    ("ui ", "ủi "),
    ("lap ", "lặp "),
    ("Lap ", "Lặp "),
    ("SOM ", "SỚM "),
    ("KHO", "KHÔ"),
    ("kho ", "khô "),
    ("TUOI", "TƯƠI"),
    ("tuoi", "tươi"),
    ("Tuoi", "Tươi"),
    ("nhiet", "nhiệt"),
    ("nhon", "nhờn"),
    ("phut", "phút"),
    (" lua", " lụa"),
    ("/lua", "/lụa"),
    ("lua/", "lụa/"),
]


def canon_vi_text(text: str | None) -> str:
    if not text or not isinstance(text, str):
        return text or ""
    out = re.sub(r"^GIAO\s*DUC\s*:?\s*", "[Tại sao] ", text, flags=re.I)
    for src, dst in _PHRASES:
        if src in out:
            out = out.replace(src, dst)
    out = re.sub(r"\bphut\b", "phút", out)
    out = re.sub(r"\bsay\b", "sấy", out)
    out = re.sub(r"\bgiat\b", "giặt", out)
    return out


def canon_vi_dict(d: dict[str, Any]) -> dict[str, Any]:
    out = dict(d)
    for k, v in list(out.items()):
        if isinstance(v, str) and (k.endswith("_vi") or k == "tip"):
            out[k] = canon_vi_text(v)
        elif isinstance(v, dict):
            out[k] = canon_vi_dict(v)
        elif isinstance(v, list):
            out[k] = [
                canon_vi_dict(x)
                if isinstance(x, dict)
                else (canon_vi_text(x) if isinstance(x, str) else x)
                for x in v
            ]
    return out


def apply_vi_canon_to_graph(graph: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(graph, dict):
        return graph
    return canon_vi_dict(graph)


_VI_FIELD_KEYS = (
    "why_vi",
    "fresh_path_vi",
    "dried_path_vi",
    "precheck_vi",
    "motion_vi",
    "water_temp_vi",
    "aftercare_vi",
    "force_metaphor_vi",
    "sense_check_vi",
    "success_rate_vi",
    "refuse_when_vi",
    "must_include_vi",
)


def seed_canon_from_records(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for r in records:
        sid = r.get("id")
        if not sid:
            continue
        row: dict[str, str] = {"id": sid}
        for k in _VI_FIELD_KEYS:
            if r.get(k):
                row[k] = canon_vi_text(str(r[k]))
        if len(row) > 1:
            rows.append(row)
    return rows
