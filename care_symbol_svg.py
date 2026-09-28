# -*- coding: utf-8 -*-
"""ISO 3758-style care-label symbol assets (SVG + PNG) for education quizzes.

Geometry is intentional (tub / triangle / square / iron / circle), not AI art.
Ids match care_label_iso3758.SYMBOLS (1–32).
"""
from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path
from typing import Callable, Optional

from care_label_iso3758 import SYMBOLS

ASSETS_DIR = Path(__file__).resolve().parent / "assets" / "care_symbols"
SIZE = 240  # PNG canvas
STROKE = 7


class _Canvas:
    """Simple black-on-white stroke canvas → SVG path + PNG."""

    def __init__(self, size: int = SIZE):
        self.size = size
        self.ops: list[tuple] = []

    def line(self, x1: float, y1: float, x2: float, y2: float, w: float = STROKE) -> None:
        self.ops.append(("line", x1, y1, x2, y2, w))

    def polyline(self, pts: list[tuple[float, float]], w: float = STROKE, close: bool = False) -> None:
        self.ops.append(("poly", pts, w, close))

    def circle(self, cx: float, cy: float, r: float, w: float = STROKE, fill: bool = False) -> None:
        self.ops.append(("circle", cx, cy, r, w, fill))

    def text(self, s: str, cx: float, cy: float, scale: float = 1.0) -> None:
        self.ops.append(("text", s, cx, cy, scale))

    def to_svg(self) -> str:
        s = self.size
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}">',
            f'<rect width="{s}" height="{s}" fill="#ffffff"/>',
        ]
        for op in self.ops:
            kind = op[0]
            if kind == "line":
                _, x1, y1, x2, y2, w = op
                parts.append(
                    f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="#111" stroke-width="{w}" stroke-linecap="round"/>'
                )
            elif kind == "poly":
                _, pts, w, close = op
                d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
                if close:
                    d += " Z"
                parts.append(
                    f'<path d="{d}" fill="none" stroke="#111" stroke-width="{w}" '
                    f'stroke-linejoin="round" stroke-linecap="round"/>'
                )
            elif kind == "circle":
                _, cx, cy, r, w, fill = op
                fill_attr = '#111' if fill else 'none'
                parts.append(
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                    f'fill="{fill_attr}" stroke="#111" stroke-width="{w}"/>'
                )
            elif kind == "text":
                _, txt, cx, cy, scale = op
                fs = int(28 * scale)
                parts.append(
                    f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                    f'dominant-baseline="central" font-family="Arial,Helvetica,sans-serif" '
                    f'font-size="{fs}" font-weight="700" fill="#111">{_esc(txt)}</text>'
                )
        parts.append("</svg>")
        return "\n".join(parts)

    def to_png_bytes(self) -> bytes:
        n = self.size
        # grayscale 0=black 255=white
        buf = bytearray([255] * (n * n))

        def setp(x: int, y: int, v: int = 0) -> None:
            if 0 <= x < n and 0 <= y < n:
                i = y * n + x
                if v < buf[i]:
                    buf[i] = v

        def thick_line(x1: float, y1: float, x2: float, y2: float, w: float) -> None:
            steps = max(int(math.hypot(x2 - x1, y2 - y1) * 2), 1)
            r = max(int(w / 2), 1)
            for i in range(steps + 1):
                t = i / steps
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
                xi, yi = int(round(x)), int(round(y))
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy <= r * r:
                            setp(xi + dx, yi + dy, 0)

        def thick_poly(pts: list[tuple[float, float]], w: float, close: bool) -> None:
            seq = list(pts)
            if close and seq:
                seq = seq + [seq[0]]
            for a, b in zip(seq, seq[1:]):
                thick_line(a[0], a[1], b[0], b[1], w)

        def thick_circle(cx: float, cy: float, r: float, w: float, fill: bool) -> None:
            if fill:
                ri = int(r)
                for y in range(-ri, ri + 1):
                    for x in range(-ri, ri + 1):
                        if x * x + y * y <= r * r:
                            setp(int(cx) + x, int(cy) + y, 0)
            else:
                # ring
                steps = max(int(2 * math.pi * r * 2), 32)
                for i in range(steps):
                    a0 = 2 * math.pi * i / steps
                    a1 = 2 * math.pi * (i + 1) / steps
                    thick_line(
                        cx + r * math.cos(a0),
                        cy + r * math.sin(a0),
                        cx + r * math.cos(a1),
                        cy + r * math.sin(a1),
                        w,
                    )

        # crude 5x7 digit glyphs
        glyphs = {
            "0": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
            "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
            "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
            "3": ["01110", "10001", "00001", "00110", "00001", "10001", "01110"],
            "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
            "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
            "6": ["01110", "10000", "11110", "10001", "10001", "10001", "01110"],
            "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
            "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
            "9": ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
            "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
            "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
            "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
        }

        def draw_text(txt: str, cx: float, cy: float, scale: float) -> None:
            cell = max(int(4 * scale), 3)
            gap = 1
            total_w = len(txt) * (5 * cell + gap) - gap
            x0 = int(cx - total_w / 2)
            y0 = int(cy - (7 * cell) / 2)
            for i, ch in enumerate(txt):
                g = glyphs.get(ch.upper()) or glyphs.get(ch)
                if not g:
                    continue
                ox = x0 + i * (5 * cell + gap)
                for row, bits in enumerate(g):
                    for col, bit in enumerate(bits):
                        if bit == "1":
                            for yy in range(cell):
                                for xx in range(cell):
                                    setp(ox + col * cell + xx, y0 + row * cell + yy, 0)

        for op in self.ops:
            kind = op[0]
            if kind == "line":
                _, x1, y1, x2, y2, w = op
                thick_line(x1, y1, x2, y2, w)
            elif kind == "poly":
                _, pts, w, close = op
                thick_poly(pts, w, close)
            elif kind == "circle":
                _, cx, cy, r, w, fill = op
                thick_circle(cx, cy, r, w, fill)
            elif kind == "text":
                _, txt, cx, cy, scale = op
                draw_text(txt, cx, cy, scale)

        return _encode_png_gray(n, n, bytes(buf))


def _esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _encode_png_gray(w: int, h: int, gray: bytes) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = bytearray()
    for y in range(h):
        raw.append(0)
        row = gray[y * w : (y + 1) * w]
        for v in row:
            raw.extend((v, v, v))  # RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def _draw_x(c: _Canvas, x1: float, y1: float, x2: float, y2: float) -> None:
    c.line(x1, y1, x2, y2)
    c.line(x2, y1, x1, y2)


def _draw_tub(c: _Canvas, *, number: Optional[str] = None, hand: bool = False,
              lines: int = 0, crossed: bool = False) -> None:
    # open-top wash tub
    c.polyline([(48, 55), (55, 95), (185, 95), (192, 55)], close=False)
    c.line(48, 55, 192, 55)
    if number:
        c.text(number, 120, 78, scale=1.35)
    if hand:
        # simplified hand inside tub
        c.polyline([(95, 70), (100, 62), (108, 62), (112, 70), (112, 88), (95, 88)], close=True)
        c.line(100, 62, 100, 52)
        c.line(108, 62, 108, 52)
    if crossed:
        _draw_x(c, 60, 50, 180, 100)
    for i in range(lines):
        y = 108 + i * 12
        c.line(70, y, 170, y, w=5)


def _draw_triangle(c: _Canvas, *, crossed: bool = False, oxygen_only: bool = False) -> None:
    c.polyline([(120, 40), (50, 170), (190, 170)], close=True)
    if crossed:
        _draw_x(c, 70, 70, 170, 160)
    if oxygen_only:
        c.line(85, 95, 120, 155, w=5)
        c.line(105, 85, 140, 145, w=5)


def _draw_square_tumble(c: _Canvas, *, dots: int = 0, crossed: bool = False, empty_circle: bool = False) -> None:
    c.polyline([(55, 45), (185, 45), (185, 175), (55, 175)], close=True)
    c.circle(120, 110, 42, fill=False)
    if empty_circle and dots == 0 and not crossed:
        pass
    if dots == 1:
        c.circle(120, 110, 8, fill=True, w=1)
    elif dots == 2:
        c.circle(105, 110, 7, fill=True, w=1)
        c.circle(135, 110, 7, fill=True, w=1)
    if crossed:
        _draw_x(c, 70, 60, 170, 160)


def _draw_air_dry(c: _Canvas, mode: str) -> None:
    # square frame
    c.polyline([(55, 45), (185, 45), (185, 175), (55, 175)], close=True)
    if mode == "line":  # hang
        c.line(75, 70, 165, 70)
    elif mode == "shade":  # hang in shade (double top + slash)
        c.line(75, 65, 165, 65)
        c.line(75, 78, 165, 78)
        c.line(160, 55, 175, 90, w=5)
    elif mode == "flat":
        c.line(75, 150, 165, 150)
    elif mode == "drip":
        c.line(90, 70, 90, 150)
        c.line(120, 70, 120, 150)
        c.line(150, 70, 150, 150)


def _draw_iron(c: _Canvas, *, dots: int = 0, crossed: bool = False) -> None:
    # iron silhouette
    c.polyline([(50, 130), (70, 70), (175, 70), (195, 100), (195, 130)], close=True)
    c.line(50, 130, 195, 130)
    if dots == 1:
        c.circle(120, 105, 7, fill=True, w=1)
    elif dots == 2:
        c.circle(105, 105, 7, fill=True, w=1)
        c.circle(135, 105, 7, fill=True, w=1)
    elif dots == 3:
        c.circle(95, 105, 6, fill=True, w=1)
        c.circle(120, 105, 6, fill=True, w=1)
        c.circle(145, 105, 6, fill=True, w=1)
    if crossed:
        _draw_x(c, 65, 60, 180, 145)


def _draw_circle_letter(c: _Canvas, letter: str, *, lines: int = 0, crossed: bool = False) -> None:
    c.circle(120, 110, 55, fill=False)
    if not crossed:
        c.text(letter, 120, 112, scale=2.0)
    if crossed:
        _draw_x(c, 70, 60, 170, 160)
    for i in range(lines):
        y = 175 + i * 12
        c.line(70, y, 170, y, w=5)


def _build(sid: int) -> _Canvas:
    c = _Canvas()
    # Map id → drawer (matches SYMBOLS hints)
    drawers: dict[int, Callable[[], None]] = {
        1: lambda: _draw_tub(c, number="40"),
        2: lambda: _draw_triangle(c, crossed=True),
        3: lambda: _draw_square_tumble(c, dots=1),
        4: lambda: _draw_iron(c, dots=2),
        5: lambda: _draw_tub(c, number="60"),
        6: lambda: _draw_circle_letter(c, "P"),
        7: lambda: _draw_tub(c, number="30"),
        8: lambda: _draw_square_tumble(c, crossed=True),
        9: lambda: _draw_tub(c, crossed=True),
        10: lambda: _draw_circle_letter(c, "F"),
        11: lambda: _draw_iron(c, dots=3),
        12: lambda: _draw_iron(c, dots=1),
        13: lambda: _draw_triangle(c, oxygen_only=True),
        14: lambda: _draw_tub(c, number="40", lines=1),
        15: lambda: _draw_square_tumble(c, dots=2),
        16: lambda: _draw_circle_letter(c, "P", lines=1),
        17: lambda: _draw_iron(c, crossed=True),
        18: lambda: _draw_air_dry(c, "shade"),
        19: lambda: _draw_tub(c, number="30", lines=2),
        20: lambda: _draw_triangle(c),
        21: lambda: _draw_circle_letter(c, "F", lines=1),
        22: lambda: _draw_circle_letter(c, "W"),
        23: lambda: _draw_circle_letter(c, "W", lines=1),
        24: lambda: _draw_circle_letter(c, "W", lines=2),
        25: lambda: _draw_circle_letter(c, "P", crossed=True),
        26: lambda: _draw_tub(c, hand=True),
        27: lambda: _draw_tub(c, number="95"),
        28: lambda: _draw_air_dry(c, "flat"),
        29: lambda: _draw_air_dry(c, "line"),
        30: lambda: _draw_air_dry(c, "drip"),
        31: lambda: _draw_tub(c, number="50"),
        32: lambda: _draw_tub(c, number="70"),
    }
    fn = drawers.get(sid)
    if fn:
        fn()
    else:
        c.text("?", 120, 120, scale=2)
    return c


def svg_for(symbol_id: int) -> str:
    return _build(int(symbol_id)).to_svg()


def png_bytes_for(symbol_id: int) -> bytes:
    return _build(int(symbol_id)).to_png_bytes()


def asset_paths(symbol_id: int) -> tuple[Path, Path]:
    ensure_assets()
    base = ASSETS_DIR / f"symbol_{int(symbol_id):02d}"
    return base.with_suffix(".svg"), base.with_suffix(".png")


def ensure_assets(force: bool = False) -> Path:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for sid in SYMBOLS:
        svg_p = ASSETS_DIR / f"symbol_{sid:02d}.svg"
        png_p = ASSETS_DIR / f"symbol_{sid:02d}.png"
        if force or not svg_p.exists() or not png_p.exists():
            canv = _build(sid)
            svg_p.write_text(canv.to_svg(), encoding="utf-8")
            png_p.write_bytes(canv.to_png_bytes())
        # sidecar meaning for humans / HQ
        meta = ASSETS_DIR / f"symbol_{sid:02d}.txt"
        if force or not meta.exists():
            row = SYMBOLS[sid]
            meta.write_text(
                f"id={sid}\nko={row.get('ko')}\nen={row.get('en')}\nvi={row.get('vi')}\n"
                f"cat={row.get('cat')}\nhint={row.get('hint')}\n",
                encoding="utf-8",
            )
    return ASSETS_DIR


if __name__ == "__main__":
    d = ensure_assets(force=True)
    print(f"wrote {len(SYMBOLS)} symbols → {d}")
