"""Generate the animated SVG assets for the ccebin profile README.

Text is converted to outlines so the SVGs need no web fonts.
"""
import math
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
OUT = HERE.parent / "assets"
OUT.mkdir(parents=True, exist_ok=True)

SERIF = TTFont(HERE / "fonts/DMSerifDisplay-Regular.ttf")
SERIF_IT = TTFont(HERE / "fonts/DMSerifDisplay-Italic.ttf")
MONO = TTFont("/usr/share/fonts/TTF/JetBrainsMono-Medium.ttf")
MONO_B = TTFont("/usr/share/fonts/TTF/JetBrainsMono-Bold.ttf")

BG = "#110c09"
CREAM = "#f4e7d4"
MUTED = "#b8946f"
EMBER = "#ff8a3d"
AMBER = "#f2b25c"
JADE = "#52cf86"
LINE = "#f2b25c"

random.seed(7)
import os
PREVIEW = bool(os.environ.get('PREVIEW'))


def measure(font, s, size, tracking=0.0):
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    k = size / font["head"].unitsPerEm
    return sum(hmtx[cmap[ord(c)]][0] * k + tracking for c in s) - tracking


def text(font, s, x, y, size, fill, tracking=0.0, anchor="start", extra=""):
    """Return an SVG <path> with `s` outlined at baseline (x, y)."""
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    hmtx = font["hmtx"]
    k = size / font["head"].unitsPerEm
    w = measure(font, s, size, tracking)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    cx = x
    for c in s:
        g = cmap[ord(c)]
        gs[g].draw(TransformPen(pen, (k, 0, 0, -k, cx, y)))
        cx += hmtx[g][0] * k + tracking
    return f'<path d="{pen.getCommands()}" fill="{fill}" {extra}/>'


def reg_mark(x, y, r=9):
    return (
        f'<g stroke="{LINE}" stroke-opacity=".55" stroke-width="1.3" fill="none">'
        f'<circle cx="{x}" cy="{y}" r="{r}"/>'
        f'<path d="M{x - r * 2} {y}H{x + r * 2}M{x} {y - r * 2}V{y + r * 2}"/></g>'
    )


def frame(w, h, inset=28):
    return (
        f'<rect x="{inset}" y="{inset}" width="{w - 2 * inset}" height="{h - 2 * inset}" '
        f'fill="none" stroke="{LINE}" stroke-opacity=".28" stroke-width="1.3"/>'
        + "".join(reg_mark(x, y) for x in (inset + 30, w - inset - 30) for y in (inset + 30, h - inset - 30))
    )


def defs_common(w, h):
    return f"""
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 .85  0 0 0 0 .7  0 0 0 .09 0"/>
  </filter>
  <radialGradient id="vignette" cx="50%" cy="50%" r="75%">
    <stop offset="60%" stop-color="#000" stop-opacity="0"/>
    <stop offset="100%" stop-color="#000" stop-opacity=".55"/>
  </radialGradient>"""


def background(w, h):
    return (
        f'<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>'
        f'<rect width="{w}" height="{h}" rx="18" filter="url(#grain)"/>'
    )


def svg(w, h, body, defs="", label=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{label}">\n<defs>{defs_common(w, h)}{defs}</defs>\n'
        f'<clipPath id="round"><rect width="{w}" height="{h}" rx="18"/></clipPath>\n'
        f'<g clip-path="url(#round)">{background(w, h)}{body}'
        f'<rect width="{w}" height="{h}" fill="url(#vignette)"/></g>\n</svg>\n'
    )


# --------------------------------------------------------------------------- header
def header():
    W, H = 1600, 560
    OX, OY = 1175, 262  # orb centre
    parts = []

    parts.append(f'<circle cx="{OX}" cy="{OY}" r="420" fill="url(#halo)"/>')
    parts.append(frame(W, H))

    # left column: editorial wordmark
    parts.append(text(MONO, "GITHUB.COM/CCEBIN", 92, 118, 15, MUTED, tracking=3.2))
    parts.append(f'<path d="M92 132H330" stroke="{LINE}" stroke-opacity=".35"/>')
    parts.append(text(SERIF, "Cebin", 80, 338, 238, CREAM, tracking=-4))
    dot_x = 80 + measure(SERIF, "Cebin", 238, -4) + 22
    parts.append(
        f'<circle cx="{dot_x:.1f}" cy="322" r="17" fill="{EMBER}">'
        f'<animate attributeName="opacity" values="1;.45;1" dur="2.4s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{dot_x:.1f}" cy="322" r="17" fill="none" stroke="{EMBER}" stroke-width="2">'
        f'<animate attributeName="r" values="17;46" dur="2.4s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".8;0" dur="2.4s" repeatCount="indefinite"/></circle>'
    )
    parts.append(text(MONO_B, "AI ASSISTANTS THAT TALK BACK.", 92, 404, 23, CREAM, tracking=5.2))
    parts.append(f'<path d="M92 436H760" stroke="{LINE}" stroke-opacity=".45" stroke-width="1.3"/>')
    parts.append(text(MONO, "VOICE  /  AGENTS  /  OFFLINE-FIRST TOOLS  /  3D", 92, 474, 14.5, MUTED, tracking=3))

    # status chip
    chip = text(MONO, "ONLINE · LISTENING", 1288, 99, 13.5, CREAM, tracking=2.6)
    parts.append(
        f'<rect x="1252" y="76" width="244" height="34" rx="17" fill="#1c140f" stroke="{LINE}" stroke-opacity=".4"/>'
        f'<circle cx="1272" cy="93" r="5" fill="{JADE}">'
        f'<animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>{chip}'
    )

    # orbit rings with particles riding them
    rings = [(250, 62, -16, 26), (210, 92, 22, 34), (290, 40, -4, 46)]
    for i, (rx, ry, rot, dur) in enumerate(rings):
        d = f"M{OX - rx} {OY}a{rx} {ry} 0 1 0 {2 * rx} 0a{rx} {ry} 0 1 0 {-2 * rx} 0"
        parts.append(
            f'<g transform="rotate({rot} {OX} {OY})">'
            f'<path id="orbit{i}" d="{d}" fill="none" stroke="{EMBER}" stroke-opacity=".5" '
            f'stroke-width="1.2" stroke-dasharray="2 9">'
            f'<animate attributeName="stroke-dashoffset" values="0;-110" dur="6s" repeatCount="indefinite"/></path>'
        )
        for j in range(2):
            parts.append(
                f'<circle r="{4 - j * 1.5}" fill="{AMBER if j else EMBER}">'
                f'<animateMotion dur="{dur}s" begin="-{j * dur / 2 + i * 3}s" repeatCount="indefinite">'
                f'<mpath href="#orbit{i}"/></animateMotion></circle>'
            )
        parts.append("</g>")

    # particle sphere rotating around the y axis (3D, projected)
    n, R, T, steps = 170, 128, 18, 16
    golden = math.pi * (3 - math.sqrt(5))
    tilt = math.radians(18)
    dots = []
    for k in range(n):
        yk = 1 - 2 * (k + 0.5) / n
        rk = math.sqrt(1 - yk * yk)
        phi = k * golden
        xs, ys, os_ = [], [], []
        for s in range(steps + 1):
            a = phi + 2 * math.pi * s / steps
            x, z = rk * math.cos(a), rk * math.sin(a)
            y = yk * math.cos(tilt) - z * math.sin(tilt)
            z2 = yk * math.sin(tilt) + z * math.cos(tilt)
            xs.append(f"{OX + x * R:.1f}")
            ys.append(f"{OY + y * R:.1f}")
            os_.append(f"{0.12 + 0.88 * (z2 + 1) / 2:.2f}")
        size = random.choice((1.6, 2, 2.4, 2.8))
        col = random.choice((EMBER, EMBER, AMBER, "#ffd2a6"))
        dots.append(
            f'<circle r="{size}" cx="{xs[0]}" cy="{ys[0]}" opacity="{os_[0]}" fill="{col}">'
            f'<animate attributeName="cx" values="{";".join(xs)}" dur="{T}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{";".join(ys)}" dur="{T}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="{";".join(os_)}" dur="{T}s" repeatCount="indefinite"/></circle>'
        )
    parts.append(f'<g>{"".join(dots)}</g>')

    # core
    parts.append(
        f'<circle cx="{OX}" cy="{OY}" r="70" fill="url(#core)">'
        f'<animate attributeName="r" values="62;76;62" dur="3.2s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{OX}" cy="{OY}" r="14" fill="#fff6e8"/>'
    )

    # rising embers
    for _ in range(26):
        x = OX + random.uniform(-170, 170)
        y0 = OY + random.uniform(40, 150)
        dur = random.uniform(4, 9)
        drift = random.uniform(-40, 40)
        parts.append(
            f'<circle cx="{x:.0f}" cy="{y0:.0f}" r="{random.uniform(1, 2.4):.1f}" fill="{AMBER}" opacity="0">'
            f'<animate attributeName="cy" values="{y0:.0f};{y0 - random.uniform(200, 320):.0f}" dur="{dur:.1f}s" '
            f'begin="-{random.uniform(0, dur):.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{x:.0f};{x + drift:.0f}" dur="{dur:.1f}s" '
            f'begin="-{random.uniform(0, dur):.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;.9;0" dur="{dur:.1f}s" '
            f'begin="-{random.uniform(0, dur):.1f}s" repeatCount="indefinite"/></circle>'
        )

    # voice waveform
    bars = 46
    gap = 10
    x0 = OX - bars * gap / 2
    base = 470
    wave = []
    for b in range(bars):
        env = math.sin(math.pi * (b + 0.5) / bars) ** 1.4
        vals = [max(3, env * random.uniform(6, 44)) for _ in range(6)]
        vals.append(vals[0])
        hv = ";".join(f"{v:.0f}" for v in vals)
        yv = ";".join(f"{base - v / 2:.0f}" for v in vals)
        wave.append(
            f'<rect x="{x0 + b * gap:.0f}" y="{base - vals[0] / 2:.0f}" height="{vals[0]:.0f}" width="4" rx="2" fill="url(#bar)">'
            f'<animate attributeName="height" values="{hv}" dur="2.6s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{yv}" dur="2.6s" repeatCount="indefinite"/></rect>'
        )
    parts.append(f'<g opacity=".9">{"".join(wave)}</g>')

    # HUD annotations
    parts.append(
        f'<g stroke="{LINE}" stroke-opacity=".5" fill="none" stroke-width="1.2">'
        f'<path d="M{OX - 118} {OY - 98}L{OX - 190} {OY - 170}H{OX - 300}"/>'
        f'<path d="M{OX + 128} {OY + 70}L{OX + 210} {OY + 132}H{OX + 300}"/></g>'
        f'<circle cx="{OX - 118}" cy="{OY - 98}" r="3" fill="{EMBER}"/>'
        f'<circle cx="{OX + 128}" cy="{OY + 70}" r="3" fill="{EMBER}"/>'
    )
    parts.append(text(MONO, "F.R.I.D.A.Y. // CORE", OX - 300, OY - 180, 12.5, MUTED, tracking=2.2))
    parts.append(text(MONO, "VOICE · TR", OX + 300, OY + 122, 12.5, MUTED, tracking=2.2, anchor="end"))

    defs = f"""
  <radialGradient id="halo"><stop offset="0" stop-color="{EMBER}" stop-opacity=".22"/>
    <stop offset=".45" stop-color="{EMBER}" stop-opacity=".06"/><stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient>
  <radialGradient id="core"><stop offset="0" stop-color="#fff3df"/><stop offset=".25" stop-color="#ffc38a" stop-opacity=".95"/>
    <stop offset=".6" stop-color="{EMBER}" stop-opacity=".45"/><stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient>
  <linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="{EMBER}"/></linearGradient>"""
    return svg(W, H, "".join(parts), defs, "Cebin. AI assistants that talk back.")


# --------------------------------------------------------------------------- terminal
def terminal():
    W, H = 1600, 470
    T = 14.0  # loop length (s)
    parts = [frame(W, H)]
    wx, wy, ww, wh = 110, 92, 1380, 292
    parts.append(
        f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="#18110d" stroke="{LINE}" stroke-opacity=".3"/>'
        f'<path d="M{wx} {wy + 44}H{wx + ww}" stroke="{LINE}" stroke-opacity=".2"/>'
    )
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        parts.append(f'<circle cx="{wx + 26 + i * 22}" cy="{wy + 22}" r="6.5" fill="{c}" opacity=".85"/>')
    parts.append(text(MONO, "cebin@cachyos: ~/Projects/f.r.i.d.a.y", wx + ww / 2, wy + 27, 14, MUTED, anchor="middle"))

    size, lh = 21, 40
    cw = MONO["hmtx"][MONO.getBestCmap()[ord("a")]][0] * size / MONO["head"].unitsPerEm
    lx = wx + 34
    ly = wy + 92

    # (segments, start, end) — each line reveals char by char between start and end (seconds)
    lines = [
        ([("$ ", EMBER), ("npm run friday", CREAM)], 0.6, 2.2),
        ([("▸ voice session ....... ", MUTED), ("connected", JADE), ("  gemini live", MUTED)], 2.8, 2.8),
        ([("▸ agent tools ......... ", MUTED), ("ready", JADE)], 3.3, 3.3),
        ([("▸ phone link .......... ", MUTED), ("paired", JADE)], 3.8, 3.8),
        ([("› ", EMBER), ("“Merhaba Cebin. Bugün ne inşa ediyoruz?”", AMBER)], 4.8, 8.2),
    ]
    for li, (segs, t0, t1) in enumerate(lines):
        y = ly + li * lh
        full = "".join(s for s, _ in segs)
        n = len(full)
        cx = lx
        for s, col in segs:
            parts.append(f'<g clip-path="url(#reveal{li})">{text(MONO, s, cx, y, size, col)}</g>')
            cx += len(s) * cw
        # discrete width steps for a typing feel
        if t1 > t0:
            times = [0, t0 / T] + [(t0 + (t1 - t0) * (i + 1) / n) / T for i in range(n)] + [(T - 0.6) / T]
            widths = [0, 0] + [(i + 1) * cw for i in range(n)] + [0]
        else:
            times = [0, t0 / T, (T - 0.6) / T]
            widths = [0, n * cw, 0]
        kt = ";".join(f"{t:.4f}" for t in times)
        wv = ";".join(f"{v:.1f}" for v in widths)
        parts.insert(0, (
            f'<clipPath id="reveal{li}"><rect x="{lx}" y="{y - size}" height="{size * 1.6}" width="{n * cw if PREVIEW else 0:.1f}">'
            f'<animate attributeName="width" values="{wv}" keyTimes="{kt}" calcMode="discrete" dur="{T}s" '
            f'repeatCount="indefinite"/></rect></clipPath>'
        ))

    # blinking cursor that follows the last line
    last = "".join(s for s, _ in lines[-1][0])
    cy = ly + 4 * lh
    parts.append(
        f'<rect x="{lx + len(last) * cw + 6:.1f}" y="{cy - size + 2}" width="{cw * 0.9:.1f}" height="{size + 4}" fill="{EMBER}" opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;0;1;0;1;0;1;0;0" '
        f'keyTimes="0;{8.3 / T:.3f};{8.8 / T:.3f};{9.3 / T:.3f};{9.8 / T:.3f};{10.3 / T:.3f};{10.8 / T:.3f};{11.3 / T:.3f};{11.8 / T:.3f};{12.3 / T:.3f};1" '
        f'calcMode="discrete" dur="{T}s" repeatCount="indefinite"/></rect>'
    )

    parts.append(text(MONO, "ON THE WORKBENCH  ·  F.R.I.D.A.Y.  ·  TURKISH VOICE ASSISTANT HUD", 110, 424, 13.5, MUTED, tracking=2.6))
    parts.append(text(MONO, "NEXT.JS · THREE.JS · GEMINI LIVE", 1490, 424, 13.5, EMBER, tracking=2.6, anchor="end"))
    return svg(W, H, "".join(parts), "", "Terminal: F.R.I.D.A.Y. booting and greeting Cebin.")


# --------------------------------------------------------------------------- footer
def footer():
    W, H = 1600, 220
    parts = [frame(W, H, inset=22)]
    parts.append(text(SERIF_IT, "Listen. Build. Ship.", W / 2, 128, 64, CREAM, anchor="middle"))
    parts.append(text(MONO, "MADE IN THE DARK, BY THE GLOW OF A TERMINAL", W / 2, 168, 12.5, MUTED, tracking=3, anchor="middle"))
    for i in range(3):
        parts.append(
            f'<circle cx="{W / 2 - 24 + i * 24}" cy="58" r="3.5" fill="{EMBER}">'
            f'<animate attributeName="opacity" values=".2;1;.2" dur="1.5s" begin="{i * 0.25}s" repeatCount="indefinite"/></circle>'
        )
    return svg(W, H, "".join(parts), "", "Listen. Build. Ship.")


for name, fn in (("header", header), ("workbench", terminal), ("footer", footer)):
    p = OUT / f"{name}.svg"
    p.write_text(fn())
    print(p.name, f"{p.stat().st_size / 1024:.0f} KB")
