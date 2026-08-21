#!/usr/bin/env python3
"""Draws icon-192.png / icon-512.png: a pint of lager on a rounded square.

Pure stdlib (zlib + struct) so it runs anywhere, with supersampled edges.

    python3 make_icons.py
"""

import math
import struct
import zlib

# ── layout, in fractions of the icon size ──
CORNER   = 0.205        # rounded-square radius
G_TOP    = 0.150        # glass top / bottom
G_BOT    = 0.870
TOP_HALF = 0.215        # glass half-width at the top / bottom (tapered)
BOT_HALF = 0.174
G_ROUND  = 0.070        # rounded bottom corners
STROKE   = 0.019        # glass wall thickness
FOAM_TOP = 0.169        # head fills right up to the rim
FOAM_BOT = 0.330

BG     = (0x33, 0x22, 0x1a)
BEER_T = (0xff, 0xdc, 0x7a)
BEER_B = (0xe8, 0x93, 0x12)
FOAM   = (0xff, 0xfc, 0xf4)
WALL   = (0xee, 0xfa, 0xff)

# (x, y, r) bubbles in the beer and cells in the foam, in icon fractions
BUBBLES = [(0.44, 0.52, 0.016), (0.57, 0.61, 0.012), (0.48, 0.70, 0.019),
           (0.60, 0.44, 0.011), (0.40, 0.62, 0.010), (0.55, 0.76, 0.014)]
FOAM_CELLS = [(0.41, 0.252, 0.030), (0.52, 0.240, 0.036), (0.61, 0.263, 0.026),
              (0.45, 0.292, 0.022), (0.57, 0.297, 0.019)]


def over(dst, src, a):
    """Alpha-composite src over dst."""
    return tuple(s * a + d * (1 - a) for d, s in zip(dst, src))


def in_round_rect(x, y, r):
    """Is (x,y) inside the unit rounded square? (rounded-box signed distance)"""
    qx = abs(x - 0.5) - (0.5 - r)
    qy = abs(y - 0.5) - (0.5 - r)
    outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
    return outside + min(max(qx, qy), 0.0) - r <= 0.0


def in_glass(x, y, inset):
    """Is (x,y) inside the glass, shrunk by `inset` on every side?"""
    top, bot = G_TOP + inset, G_BOT - inset
    if not (top <= y <= bot):
        return False
    t = (y - G_TOP) / (G_BOT - G_TOP)
    hw = TOP_HALF + (BOT_HALF - TOP_HALF) * t - inset
    if hw <= 0:
        return False
    dx = abs(x - 0.5)
    r = G_ROUND
    if y > bot - r:                       # rounded bottom corners
        dy = y - (bot - r)
        hw -= r - math.sqrt(max(0.0, r * r - dy * dy))
    return dx <= hw


def surface_y(x):
    """Wavy boundary between the foam and the beer."""
    return FOAM_BOT + 0.012 * math.sin(x * 34.0)


def shade(x, y):
    """Colour of one sample: (r, g, b, a), each 0..1 * 255 for rgb."""
    if not in_round_rect(x, y, CORNER):
        return None

    col = BG
    outer = in_glass(x, y, 0.0)
    inner = in_glass(x, y, STROKE)

    if inner:
        col = over(col, (255, 255, 255), 0.07)      # glass tint
        sy = surface_y(x)
        if y >= sy:                                  # beer
            t = (y - sy) / max(1e-6, G_BOT - sy)
            beer = tuple(a + (b - a) * t for a, b in zip(BEER_T, BEER_B))
            col = over(col, beer, 1.0)
            # rising bubbles
            for bx, by, br in BUBBLES:
                d = math.hypot(x - bx, y - by)
                if d <= br:
                    col = over(col, (255, 255, 245), 0.55 if d < br * 0.6 else 0.3)
        elif y >= FOAM_TOP:                          # head
            col = over(col, FOAM, 1.0)
            for cx, cy, cr in FOAM_CELLS:
                d = math.hypot(x - cx, y - cy)
                if d <= cr:
                    col = over(col, (226, 210, 184), 0.30 if d > cr * 0.66 else 0.14)

    if outer and not inner:                          # glass wall
        col = over(col, WALL, 0.42)

    return col


def render(size, ss=4):
    """Supersampled RGBA rows."""
    rows = []
    step = 1.0 / (size * ss)
    off = step * 0.5
    for py in range(size):
        row = bytearray()
        for px in range(size):
            r = g = b = a = 0.0
            for sy in range(ss):
                y = (py * ss + sy) / (size * ss) + off
                for sx in range(ss):
                    x = (px * ss + sx) / (size * ss) + off
                    c = shade(x, y)
                    if c is not None:
                        r += c[0]; g += c[1]; b += c[2]; a += 1.0
            n = ss * ss
            if a == 0:
                row += b'\0\0\0\0'
            else:
                # un-premultiply: average colour over covered samples only
                row += bytes((int(r / a + 0.5), int(g / a + 0.5), int(b / a + 0.5),
                              int(a / n * 255 + 0.5)))
        rows.append(bytes(row))
    return rows


def write_png(path, size, rows):
    raw = b''.join(b'\0' + r for r in rows)

    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c))

    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    print(f'{path}  {size}x{size}  {len(png)} bytes')


if __name__ == '__main__':
    for size, ss in ((192, 4), (512, 3)):
        write_png(f'icon-{size}.png', size, render(size, ss))
