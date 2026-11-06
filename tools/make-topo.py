#!/usr/bin/env python3
"""Generate topo.svg and topo-glow.svg: contour lines for the page background.

The terrain is a seeded sum of smooth hills and valleys, traced into contour
lines with marching squares. Change SEED for a different landscape; tune the
look in index.html (opacity) or with LEVELS / STROKE_* below.

    python3 tools/make-topo.py            # writes both files in the repo root
"""
import math
import random
from pathlib import Path

SEED = 7
W, H = 1600, 1000          # SVG canvas (scaled to cover the viewport)
STEP = 8                   # sampling grid spacing in px
LEVELS = 30                # number of contour lines
STROKE = "#18191A"
STROKE_OPACITY = 0.07      # regular lines
INDEX_OPACITY = 0.11       # every 5th line, like an index contour on a map
EPS = 0.7                  # line simplification tolerance in px
GLOW_STROKE = "#E8843A"    # warm amber-orange: the lines lit up around the pointer
GLOW_WIDTH = 1.5
HALO_WIDTH = 7             # soft light around each lit line
HALO_OPACITY = 0.14

rng = random.Random(SEED)
hills = []
for _ in range(30):
    hills.append((
        rng.uniform(-0.1, 1.1) * W,           # x
        rng.uniform(-0.1, 1.1) * H,           # y
        rng.uniform(90, 380),                 # spread
        rng.uniform(0.4, 1.0) * rng.choice((1, 1, -1)),  # height (some valleys)
    ))
waves = [(rng.uniform(0.002, 0.005), rng.uniform(0.002, 0.005),
          rng.uniform(0, math.tau), rng.uniform(0.05, 0.12)) for _ in range(3)]


def height(x, y):
    v = 0.0
    for hx, hy, s, a in hills:
        v += a * math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / (2 * s * s))
    for fx, fy, ph, a in waves:
        v += a * math.sin(x * fx + ph) * math.cos(y * fy - ph)
    return v


nx, ny = W // STEP + 1, H // STEP + 1
grid = [[height(i * STEP, j * STEP) for i in range(nx)] for j in range(ny)]
lo = min(map(min, grid))
hi = max(map(max, grid))

# Marching squares. Edges: 0 top, 1 right, 2 bottom, 3 left.
TABLE = {1: [(3, 2)], 2: [(2, 1)], 3: [(3, 1)], 4: [(0, 1)], 6: [(0, 2)],
         7: [(3, 0)], 8: [(3, 0)], 9: [(0, 2)], 11: [(0, 1)], 12: [(3, 1)],
         13: [(2, 1)], 14: [(3, 2)]}


def trace(level):
    points = {}      # edge key -> (x, y)
    links = {}       # edge key -> neighbouring edge keys

    def edge(i, j, e, a, b, c, d):
        # a tl, b tr, c br, d bl; returns a key shared with the adjacent cell
        if e == 0:
            key, (v0, v1), (x0, y0, x1, y1) = ("h", i, j), (a, b), (i, j, i + 1, j)
        elif e == 2:
            key, (v0, v1), (x0, y0, x1, y1) = ("h", i, j + 1), (d, c), (i, j + 1, i + 1, j + 1)
        elif e == 3:
            key, (v0, v1), (x0, y0, x1, y1) = ("v", i, j), (a, d), (i, j, i, j + 1)
        else:
            key, (v0, v1), (x0, y0, x1, y1) = ("v", i + 1, j), (b, c), (i + 1, j, i + 1, j + 1)
        if key not in points:
            t = (level - v0) / (v1 - v0)
            points[key] = ((x0 + t * (x1 - x0)) * STEP, (y0 + t * (y1 - y0)) * STEP)
        return key

    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b = grid[j][i], grid[j][i + 1]
            d, c = grid[j + 1][i], grid[j + 1][i + 1]
            idx = (a > level) * 8 + (b > level) * 4 + (c > level) * 2 + (d > level)
            if idx in (0, 15):
                continue
            if idx in (5, 10):  # saddle: decide by the cell centre
                centre_high = (a + b + c + d) / 4 > level
                if idx == 5:
                    segs = [(3, 0), (2, 1)] if centre_high else [(3, 2), (0, 1)]
                else:
                    segs = [(0, 1), (3, 2)] if centre_high else [(3, 0), (2, 1)]
            else:
                segs = TABLE[idx]
            for e0, e1 in segs:
                k0 = edge(i, j, e0, a, b, c, d)
                k1 = edge(i, j, e1, a, b, c, d)
                links.setdefault(k0, []).append(k1)
                links.setdefault(k1, []).append(k0)

    # Join segments into polylines: start from open ends first, then loops.
    seen, lines = set(), []
    starts = [k for k, n in links.items() if len(n) == 1] + list(links)
    for start in starts:
        if start in seen:
            continue
        line, cur, prev = [start], start, None
        seen.add(start)
        while True:
            nxt = [k for k in links[cur] if k != prev and k not in seen]
            if not nxt:
                if prev is not None and start in links[cur] and len(line) > 2:
                    line.append(start)  # closed loop
                break
            prev, cur = cur, nxt[0]
            seen.add(cur)
            line.append(cur)
        lines.append([points[k] for k in line])
    return lines


def simplify(pts):
    """Ramer-Douglas-Peucker."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        s, e = stack.pop()
        (x0, y0), (x1, y1) = pts[s], pts[e]
        dx, dy = x1 - x0, y1 - y0
        norm = math.hypot(dx, dy) or 1e-9
        best, bi = 0.0, -1
        for k in range(s + 1, e):
            px, py = pts[k]
            dist = abs(dy * (px - x0) - dx * (py - y0)) / norm if norm > 1e-9 else math.hypot(px - x0, py - y0)
            if dist > best:
                best, bi = dist, k
        if best > EPS:
            keep[bi] = True
            stack += [(s, bi), (bi, e)]
    return [p for p, k in zip(pts, keep) if k]


def path_d(pts):
    out = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    out += [f"L{x:.1f} {y:.1f}" for x, y in pts[1:]]
    return "".join(out).replace(".0 ", " ").replace(".0L", "L")


regular, index = [], []
for n in range(1, LEVELS + 1):
    level = lo + (hi - lo) * n / (LEVELS + 1)
    target = index if n % 5 == 0 else regular
    for line in trace(level):
        line = simplify(line)
        if len(line) >= 2:
            target.append(path_d(line))

def write(name, stroke, width, regular_opacity, index_opacity, index_width, halo=False):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'preserveAspectRatio="xMidYMid slice">\n'
        f'<!-- Generated by tools/make-topo.py (seed {SEED}). Do not edit by hand. -->\n'
        + (f'<path fill="none" stroke="{stroke}" stroke-width="{HALO_WIDTH}" stroke-opacity="{HALO_OPACITY}" '
           f'stroke-linecap="round" stroke-linejoin="round" d="{"".join(regular + index)}"/>\n' if halo else '')
        + f'<g fill="none" stroke="{stroke}" stroke-linejoin="round">\n'
        f'<path stroke-width="{width}" stroke-opacity="{regular_opacity}" d="{"".join(regular)}"/>\n'
        f'<path stroke-width="{index_width}" stroke-opacity="{index_opacity}" d="{"".join(index)}"/>\n'
        f'</g>\n</svg>\n'
    )
    out = Path(__file__).resolve().parent.parent / name
    out.write_text(svg)
    print(f"wrote {out.name}: {len(svg) / 1024:.0f} KB, {len(regular) + len(index)} lines")


# Faint ink lines for the background, and the same lines in amber, which the
# page reveals around the pointer so the map itself lights up.
write("topo.svg", STROKE, 1, STROKE_OPACITY, INDEX_OPACITY, 1)
write("topo-glow.svg", GLOW_STROKE, GLOW_WIDTH, 0.85, 1, GLOW_WIDTH + 0.4, halo=True)
