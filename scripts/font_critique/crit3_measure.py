"""3차 크리틱(v1.33 작업본) 전체 글자 숫자 검사 → out/font-critique/metrics-v1.33.json
검사: ①높이선·넘침 ②기둥·가로획 굵기 ③세리프(깃발) 치수 ④곡선 꺾임 ⑤짧은 선·불필요한 점 ⑥살짝 기운 선 ⑦좌우 대칭 ⑧좌우 여백
사용: py scripts/font_critique/crit3_measure.py [서체]"""
import os, sys, json, math
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out/font-update/v1.33/fonts/FnGuideLogotype-Regular.otf")
f = TTFont(PATH); gs = f.getGlyphSet(); hm = f["hmtx"]
cmap = f.getBestCmap(); u2g = {chr(u): g for u, g in cmap.items()}
g2c = {g: chr(u) for u, g in cmap.items()}

def rec(g):
    r = RecordingPen(); gs[g].draw(r); return r.value

def contours(g):
    cs, cur = [], None
    for op, a in rec(g):
        if op == "moveTo": cur = [("M", a[0])]
        elif op == "lineTo": cur.append(("L", a[0]))
        elif op == "curveTo": cur.append(("C", a))
        elif op == "closePath": cs.append(cur)
    return cs

def flatten(c, n=24):
    pts = [c[0][1]]
    for op, a in c[1:]:
        p0 = pts[-1]
        if op == "L": pts.append(a)
        else:
            c1, c2, p3 = a
            for i in range(1, n + 1):
                t = i / n; mt = 1 - t
                pts.append((mt**3*p0[0]+3*mt*mt*t*c1[0]+3*mt*t*t*c2[0]+t**3*p3[0],
                            mt**3*p0[1]+3*mt*mt*t*c1[1]+3*mt*t*t*c2[1]+t**3*p3[1]))
    return pts

POLY = {}
def polys(g):
    if g not in POLY: POLY[g] = [flatten(c) for c in contours(g)]
    return POLY[g]

def _runs(g, v, horiz):
    """주사선의 잉크 구간 [(a,b)] — 0 아닌 감김 규칙(겹친 획도 하나로 봄)"""
    ev = []
    for P in polys(g):
        for i in range(len(P)):
            (x1, y1), (x2, y2) = P[i - 1], P[i]
            if not horiz: x1, y1, x2, y2 = y1, x1, y2, x2
            if (y1 > v) != (y2 > v):
                ev.append((x1 + (v - y1) * (x2 - x1) / (y2 - y1), 1 if y2 > y1 else -1))
    ev.sort(); out, w, start = [], 0, None
    for x, d in ev:
        nw = w + d
        if w == 0 and nw != 0: start = x
        if w != 0 and nw == 0: out.append((start, x))
        w = nw
    return out
def runs_h(g, y): return _runs(g, y, True)
def runs_v(g, x): return _runs(g, x, False)

def bounds(g):
    P = [p for poly in polys(g) for p in poly]
    if not P: return None
    return (min(p[0] for p in P), min(p[1] for p in P), max(p[0] for p in P), max(p[1] for p in P))

R = {}
UC = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]; LC = [c for c in "abcdefghijklmnopqrstuvwxyz"]; DG = list("0123456789")

# ① 높이선·넘침
R["heights"] = {c: [round(v) for v in bounds(u2g[c])[1::2]] for c in UC + LC + DG}

# ② 기둥 굵기(세로) — 글자별 주사선 높이, 잉크 구간 중 60~160 폭
STEM_Y = {**{c: 200 for c in UC}, **{c: 250 for c in LC}, **{c: 330 for c in DG}}
STEM_Y.update({"f": 250, "j": 250, "p": 250, "q": 250, "g": 250, "y": 250, "t": 250})
R["stems"] = {c: [round(b - a, 1) for a, b in runs_h(u2g[c], STEM_Y[c])] for c in UC + LC + DG}

# 가로획 굵기 — 가운데 세로 주사선에서 잉크 구간
def hbars(c, x):
    return [round(b - a, 1) for a, b in runs_v(u2g[c], x)]
R["hbars"] = {c: hbars(c, (bounds(u2g[c])[0] + bounds(u2g[c])[2]) / 2) for c in UC + LC + DG}

# ④ 곡선 꺾임: 이어지는 두 선의 방향 차이 0.3~15도
def tangents(c):
    """각 꼭지점의 (들어오는 방향, 나가는 방향)"""
    segs = []
    pts = [c[0][1]]
    for op, a in c[1:]:
        p0 = pts[-1]
        if op == "L": segs.append((p0, p0, a, a)); pts.append(a)
        else: segs.append((p0, a[0], a[1], a[2])); pts.append(a[2])
    if pts[-1] != pts[0]: segs.append((pts[-1], pts[-1], pts[0], pts[0]))
    segs = [s for s in segs if s[0] != s[3]]
    out = []
    for i in range(len(segs)):
        a, b = segs[i - 1], segs[i]
        # 들어오는 방향: a 끝 - a 의 마지막 제어점(같으면 앞의 것)
        ain = next((p for p in (a[2], a[1], a[0]) if p != a[3]), None)
        bout = next((p for p in (b[1], b[2], b[3]) if p != b[0]), None)
        if ain is None or bout is None: continue
        d1 = math.atan2(a[3][1] - ain[1], a[3][0] - ain[0]); d2 = math.atan2(bout[1] - b[0][1], bout[0] - b[0][0])
        ang = abs((math.degrees(d2 - d1) + 180) % 360 - 180)
        curvy = (a[1] != a[0] or a[2] != a[3]) or (b[1] != b[0] or b[2] != b[3])
        out.append((b[0], round(ang, 2), curvy))
    return out
kinks = {}
for g in f.getGlyphOrder():
    for c in contours(g):
        for pt, ang, curvy in tangents(c):
            if curvy and 0.3 <= ang <= 15:
                kinks.setdefault(g, []).append([list(pt), ang])
R["kinks"] = kinks

# ⑤ 짧은 선(< 4)·같은 직선 위 불필요한 점
short, colin = {}, {}
for g in f.getGlyphOrder():
    for c in contours(g):
        pts = [c[0][1]] + [a if op == "L" else a[2] for op, a in c[1:]]
        ops = ["M"] + [op for op, a in c[1:]]
        for i in range(1, len(pts)):
            d = math.dist(pts[i - 1], pts[i])
            if 0 < d < 4: short.setdefault(g, []).append([list(pts[i - 1]), list(pts[i]), round(d, 1)])
        for i in range(1, len(pts) - 1):
            if ops[i] == "L" and ops[i + 1] == "L":
                (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], pts[i], pts[i + 1]
                if abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)) < 1e-6 and pts[i] not in (pts[i-1], pts[i+1]):
                    colin.setdefault(g, []).append(list(pts[i]))
R["short_segments"] = short; R["collinear_points"] = colin

# ⑥ 살짝 기운 선: 세로/가로에서 0.3~3도
tilt = {}
for g in f.getGlyphOrder():
    for c in contours(g):
        pts = [c[0][1]] + [a if op == "L" else a[2] for op, a in c[1:]]
        ops = ["M"] + [op for op, a in c[1:]]
        for i in range(1, len(pts)):
            if ops[i] != "L": continue
            (x0, y0), (x1, y1) = pts[i - 1], pts[i]; L = math.dist(pts[i-1], pts[i])
            if L < 30: continue
            a = math.degrees(math.atan2(abs(y1 - y0), abs(x1 - x0)))
            off = min(a, 90 - a)
            if 0.3 <= off <= 3: tilt.setdefault(g, []).append([list(pts[i-1]), list(pts[i]), round(off, 2)])
R["tilted_lines"] = tilt

# ⑦ 좌우 대칭(대칭이어야 할 글자): 래스터 XOR 넓이 ÷ 글자 넓이
SYM = list("AHIMOTUVWXYovwxz0o8") + ["zero"]
def raster(g, mirror=False, step=4):
    x0, y0, x1, y1 = bounds(g); cx = (x0 + x1) / 2; cells = set()
    y = y0 + step / 2
    while y < y1:
        for a, b in runs_h(g, y):
            xa, xb = (2 * cx - b, 2 * cx - a) if mirror else (a, b)
            for k in range(int(math.ceil(xa / step)), int(math.floor(xb / step)) + 1): cells.add((k, int(y)))
        y += step
    return cells
sym = {}
for c in "AOTXovx08":
    g = u2g[c]; A = raster(g); B = raster(g, True)
    sym[c] = round(len(A ^ B) / max(1, len(A)) * 100, 2)
R["symmetry_xor_pct"] = sym

# ⑧ 좌우 여백
R["sidebearings"] = {c: [round(bounds(u2g[c])[0]), round(hm[u2g[c]][0] - bounds(u2g[c])[2])] for c in UC + LC + DG}
R["advance"] = {c: hm[u2g[c]][0] for c in UC + LC + DG}

out = os.path.join(ROOT, "out/font-critique/metrics-v1.33.json")
json.dump(R, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(out)
