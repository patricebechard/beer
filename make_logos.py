#!/usr/bin/env python3
"""Turns the brand art in pint_logos/ into trimmed, transparent logo-*.png files.

The app draws these in front of the beer, as if printed on the side of the
glass, and the picker uses the same files for its tiles. Backgrounds are keyed
out (or, for a logo that is a perfect circle, masked), transparent margins are
trimmed, and the result is scaled down to LONG_EDGE.

Needs ffmpeg on PATH.

    python3 make_logos.py
"""

import subprocess
import sys

SRC = 'pint_logos'
LONG_EDGE = 480          # plenty for a 3x phone screen at ~60% width

# key:   None                 -> already has an alpha channel, just trim
#        ('color', hex, sim)   -> knock out a flat background colour
#        ('circle', r)         -> keep a centred disc of radius r * width
JOBS = [
    ('michelob', 'Michelob-Ultra-Logo.png',                        None),
    ('pliny',    'Plinytheelderlogo.webp',                          ('circle', 0.478)),
    ('hypa',     'brasseriedubascanada-1634234306.jpg',             ('color', '0xFFFFFF', 0.09)),
    ('guinness', 'guinness-logo-2016.png',                          ('color', '0x000000', 0.07)),
    ('caesar',   'Motts-Clamato-Caesar-Logo-2024_PPT_LowRes-1.png', None),
]


def run(args):
    p = subprocess.run(args, capture_output=True)
    if p.returncode:
        sys.exit(f'ffmpeg failed: {p.stderr.decode()[-500:]}')
    return p.stdout


def size(path):
    out = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
               '-show_entries', 'stream=width,height', '-of', 'csv=p=0', path])
    w, h = out.decode().strip().split(',')[:2]
    return int(w), int(h)


def key_filter(key, w, h):
    """The filter chain that produces a transparent image."""
    if key is None:
        return 'format=rgba'
    kind = key[0]
    if kind == 'color':
        _, colour, sim = key
        return f'format=rgba,colorkey={colour}:{sim}:0.02'
    if kind == 'circle':
        r = key[1] * w
        # keep pixels inside the disc, drop the rest
        return ('format=rgba,'
                f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
                f"a='if(lte(hypot(X-{w / 2:.1f},Y-{h / 2:.1f}),{r:.1f}),255,0)'")
    raise ValueError(kind)


def alpha_bbox(path, chain, w, h):
    """Tightest box holding every pixel that is not fully transparent."""
    raw = run(['ffmpeg', '-v', 'error', '-i', path, '-vf', chain,
               '-f', 'rawvideo', '-pix_fmt', 'rgba', '-'])
    minx, miny, maxx, maxy = w, h, -1, -1
    for y in range(h):
        row = raw[y * w * 4:(y + 1) * w * 4]
        xs = [x for x in range(w) if row[x * 4 + 3] > 8]
        if xs:
            miny = min(miny, y)
            maxy = y
            minx = min(minx, xs[0])
            maxx = max(maxx, xs[-1])
    if maxx < 0:
        sys.exit(f'{path}: everything got keyed out')
    return minx, miny, maxx - minx + 1, maxy - miny + 1


def main():
    for name, fname, key in JOBS:
        src = f'{SRC}/{fname}'
        w, h = size(src)
        chain = key_filter(key, w, h)
        x, y, cw, ch = alpha_bbox(src, chain, w, h)

        scale = min(1.0, LONG_EDGE / max(cw, ch))
        ow, oh = max(1, round(cw * scale)), max(1, round(ch * scale))
        out = f'logo-{name}.png'
        run(['ffmpeg', '-v', 'error', '-y', '-i', src,
             '-vf', f'{chain},crop={cw}:{ch}:{x}:{y},scale={ow}:{oh}:flags=lanczos',
             '-frames:v', '1', out])
        print(f'{out:20} {w}x{h} -> trim {cw}x{ch} @ {x},{y} -> {ow}x{oh}')


if __name__ == '__main__':
    main()
