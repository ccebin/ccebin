"""Generate avatar variants (1024x1024 PNG) in the profile's ember style.

Needs rsvg-convert on PATH. Output: avatar/avatar-<variant>.png
"""
import math
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import gen_assets as g  # noqa: E402  (also regenerates the README assets)

HERE = Path(__file__).parent
OUT = HERE.parent / "avatar"
OUT.mkdir(exist_ok=True)
S = 1024
C = S / 2


def base_defs():
    return f"""
  <radialGradient id="bg" cx="50%" cy="46%" r="70%">
    <stop offset="0" stop-color="#2a1a10"/><stop offset=".55" stop-color="{g.BG}"/><stop offset="1" stop-color="#080504"/></radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="{g.EMBER}" stop-opacity=".38"/>
    <stop offset=".5" stop-color="{g.EMBER}" stop-opacity=".08"/><stop offset="1" stop-color="{g.EMBER}" stop-opacity="0"/></radialGradient>
  <radialGradient id="core"><stop offset="0" stop-color="#fff3df"/><stop offset=".25" stop-color="#ffc38a" stop-opacity=".95"/>
    <stop offset=".6" stop-color="{g.EMBER}" stop-opacity=".45"/><stop offset="1" stop-color="{g.EMBER}" stop-opacity="0"/></radialGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 1  0 0 0 0 .85  0 0 0 0 .7  0 0 0 .07 0"/></filter>"""


def wrap(body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">'
        f"<defs>{base_defs()}</defs>"
        f'<rect width="{S}" height="{S}" fill="url(#bg)"/>{body}'
        f'<rect width="{S}" height="{S}" filter="url(#grain)"/></svg>'
    )


def orbit(rx, ry, rot, opacity=0.6, dash="3 12"):
    return (
        f'<ellipse cx="{C}" cy="{C}" rx="{rx}" ry="{ry}" transform="rotate({rot} {C} {C})" fill="none" '
        f'stroke="{g.EMBER}" stroke-opacity="{opacity}" stroke-width="2" stroke-dasharray="{dash}"/>'
    )


def orbit_bead(rx, ry, rot, t, r, col):
    a = 2 * math.pi * t
    x, y = rx * math.cos(a), ry * math.sin(a)
    rr = math.radians(rot)
    return f'<circle cx="{C + x * math.cos(rr) - y * math.sin(rr):.1f}" cy="{C + x * math.sin(rr) + y * math.cos(rr):.1f}" r="{r}" fill="{col}" filter="url(#glow)"/>'


def monogram():
    """Serif C with an ember dot, inside orbit rings."""
    body = [f'<circle cx="{C}" cy="{C}" r="430" fill="url(#halo)"/>']
    body += [orbit(400, 150, -24), orbit(360, 210, 30, 0.3)]
    body.append(orbit_bead(400, 150, -24, 0.12, 9, g.EMBER))
    body.append(orbit_bead(360, 210, 30, 0.62, 6, g.AMBER))
    size = 640
    w = g.measure(g.SERIF, "C", size)
    x = C - (w + 90) / 2 + 10
    body.append(g.text(g.SERIF, "C", x, C + size * 0.36, size, g.CREAM))
    body.append(f'<circle cx="{x + w + 70:.0f}" cy="{C + size * 0.31:.0f}" r="44" fill="{g.EMBER}" filter="url(#glow)"/>')
    return wrap("".join(body))


def letter_mask(ch, size):
    font = ImageFont.truetype(str(HERE / "fonts/DMSerifDisplay-Regular.ttf"), size)
    img = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((0, 0), ch, font=font)
    d.text(((S - (r - l)) / 2 - l - 40, (S - (b - t)) / 2 - t), ch, font=font, fill=255)
    return np.array(img) > 128


def particle_c():
    """The letter C made of ember particles."""
    rng = random.Random(11)
    mask = letter_mask("C", 760)
    ys, xs = np.nonzero(mask)
    body = [f'<circle cx="{C}" cy="{C}" r="460" fill="url(#halo)"/>', orbit(420, 120, -18, 0.35)]
    dots = []
    for _ in range(1500):
        i = rng.randrange(len(xs))
        x, y = xs[i] + rng.uniform(-3, 3), ys[i] + rng.uniform(-3, 3)
        heat = 1 - math.hypot(x - C, y - C) / 560
        r = rng.choice((1.6, 2.2, 2.8, 3.6, 5.5)) * (0.6 + heat * 0.7)
        col = rng.choices((g.EMBER, g.AMBER, "#ffd2a6", "#fff3df"), (5, 3, 2, 1))[0]
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" opacity="{rng.uniform(.3, 1):.2f}"/>')
    # loose sparks drifting off the letter
    for _ in range(140):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(300, 470)
        dots.append(f'<circle cx="{C + d * math.cos(a):.1f}" cy="{C + d * math.sin(a):.1f}" r="{rng.uniform(1.2, 3):.1f}" '
                    f'fill="{g.AMBER}" opacity="{rng.uniform(.15, .6):.2f}"/>')
    body.append(f'<g filter="url(#glow)">{"".join(dots)}</g>')
    body.append(f'<circle cx="{C + 300}" cy="{C + 228}" r="40" fill="{g.EMBER}" filter="url(#glow)"/>')
    return wrap("".join(body))


def orb():
    """F.R.I.D.A.Y. core: particle sphere, orbits and a bright centre."""
    rng = random.Random(3)
    body = [f'<circle cx="{C}" cy="{C}" r="500" fill="url(#halo)"/>']
    body += [orbit(440, 120, -18), orbit(380, 190, 26, 0.35), orbit(470, 70, -4, 0.3)]
    body += [orbit_bead(440, 120, -18, 0.08, 10, g.EMBER), orbit_bead(380, 190, 26, 0.55, 7, g.AMBER),
             orbit_bead(470, 70, -4, 0.8, 6, "#ffd2a6")]
    n, R = 700, 290
    golden = math.pi * (3 - math.sqrt(5))
    tilt = math.radians(18)
    dots = []
    for k in range(n):
        yk = 1 - 2 * (k + 0.5) / n
        rk = math.sqrt(1 - yk * yk)
        a = k * golden
        x, z = rk * math.cos(a), rk * math.sin(a)
        y = yk * math.cos(tilt) - z * math.sin(tilt)
        z2 = yk * math.sin(tilt) + z * math.cos(tilt)
        depth = (z2 + 1) / 2
        col = rng.choices((g.EMBER, g.AMBER, "#ffd2a6"), (5, 3, 2))[0]
        dots.append(f'<circle cx="{C + x * R:.1f}" cy="{C + y * R:.1f}" r="{1.5 + 3.5 * depth:.1f}" fill="{col}" '
                    f'opacity="{0.15 + 0.85 * depth:.2f}"/>')
    body.append(f'<g filter="url(#glow)">{"".join(dots)}</g>')
    body.append(f'<circle cx="{C}" cy="{C}" r="190" fill="url(#core)"/><circle cx="{C}" cy="{C}" r="34" fill="#fff6e8" filter="url(#glow)"/>')
    return wrap("".join(body))


for name, fn in (("monogram", monogram), ("particle-c", particle_c), ("orb", orb)):
    svg = OUT / f"avatar-{name}.svg"
    svg.write_text(fn())
    png = OUT / f"avatar-{name}.png"
    subprocess.run(["rsvg-convert", "-w", str(S), str(svg), "-o", str(png)], check=True)
    svg.unlink()
    print(png.name, f"{png.stat().st_size / 1024:.0f} KB")
