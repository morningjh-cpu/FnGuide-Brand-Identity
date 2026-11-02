"""measure.py 의 측정 함수를 불러 쓸 수 있게 뺀 것 (measure.py 는 실행하면 바로 1차 metrics.json 을 덮어쓴다)"""
import numpy as np
from matplotlib.path import Path
from fontTools.pens.boundsPen import BoundsPen


def runs(mask, coords):
    out = []; on = None
    for v, c in zip(mask, coords):
        if v and on is None: on = c
        if not v and on is not None: out.append((on, c)); on = None
    if on is not None: out.append((on, coords[-1]))
    return out


_pcache = {}


def _polys(f, ch=None, glyph=None):
    key = (f.file, ch, glyph)
    if key not in _pcache:
        if glyph is None:
            p, _ = f.path(ch, size=f.upm)
        else:
            from matplotlib.path import Path as P
            V, C = [], []
            for op, pts in f.rec(glyph):
                V += pts if pts else [(0, 0)]
                C += {"M": [P.MOVETO], "L": [P.LINETO], "C": [P.CURVE4] * 3,
                      "Q": [P.CURVE3] * 2, "Z": [P.CLOSEPOLY]}[op]
            p = P(V, C) if V else None
        _pcache[key] = [] if p is None else p.to_polygons(closed_only=False)
    return _pcache[key]


def inside(f, ch, pts, glyph=None):
    n = np.zeros(len(pts), int)
    for poly in _polys(f, ch, glyph):
        n += Path(poly).contains_points(pts)
    return n % 2 == 1


def hscan(f, ch, y, x0=-200, x1=2500, glyph=None):
    xs = np.arange(x0, x1, 0.5)
    return runs(inside(f, ch, np.c_[xs, np.full_like(xs, y)], glyph), xs)


def vscan(f, ch, x, y0=-400, y1=1200):
    ys = np.arange(y0, y1, 0.5)
    return runs(inside(f, ch, np.c_[np.full_like(ys, x), ys]), ys)


def bbox(f, ch):
    g = f.tt.getBestCmap()[ord(ch)]; bp = BoundsPen(f.gs); f.gs[g].draw(bp); return bp.bounds


def adv(f, ch):
    return f.tt["hmtx"][f.tt.getBestCmap()[ord(ch)]][0]


def proportions(f):
    """1차 크리틱과 같은 방식의 비례 측정 (대문자 높이 1000 기준)"""
    H = bbox(f, "H"); cap = H[3]; xh = bbox(f, "x")[3]
    O = bbox(f, "O"); o = bbox(f, "o"); l = bbox(f, "l"); p = bbox(f, "p")
    Hs = hscan(f, "H", cap * 0.3); stemH = Hs[0][1] - Hs[0][0]
    cx = (H[0] + H[2]) / 2; bar = [r for r in vscan(f, "H", cx) if r[0] > 0][0]; barH = bar[1] - bar[0]
    ns = hscan(f, "n", xh * 0.3); stem_n = ns[0][1] - ns[0][0]
    Os = hscan(f, "O", cap * 0.5); Oside = Os[0][1] - Os[0][0]
    Ov = vscan(f, "O", (O[0] + O[2]) / 2); Otop = Ov[-1][1] - Ov[-1][0]
    os_ = hscan(f, "o", xh * 0.5); oside = os_[0][1] - os_[0][0]
    ov = vscan(f, "o", (o[0] + o[2]) / 2); otop = ov[-1][1] - ov[-1][0]
    k = 1000 / cap
    r = dict(xh_cap=xh / cap, asc_cap=l[3] / cap, desc_cap=-p[1] / cap,
             O_over_top=(O[3] - cap) * k, O_over_bot=-O[1] * k,
             o_over_top=(o[3] - xh) * k, o_over_bot=-o[1] * k,
             stemH=stemH * k, n_vs_H=stem_n / stemH, contrast_H=barH / stemH,
             contrast_O=Otop / Oside, contrast_o=otop / oside,
             O_H=adv(f, "O") / adv(f, "H"))
    return {kk: round(float(v), 3) for kk, v in r.items()}
