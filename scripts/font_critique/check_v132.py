"""v1.32 확인: ① 바뀐 글자 ② 바뀐 글자 쌍 간격 ③ 모든 글자 쌍 닿음 ④ 파일 설정
실행: py scripts/font_critique/check_v132.py → out/font-update/v1.32/check.json
"""
import json, itertools
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
import lib, crit2_preview as pv

A = lib.F(lib.ROOT + "out/font-update/v1.31/fonts/FnGuideLogotype-Regular.otf")
B = lib.F(lib.ROOT + "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf")
OUT = lib.ROOT + "out/font-update/v1.32/check.json"


def gpath(f, g, dx=0):
    p = pathops.Path(); f.gs[g].draw(TransformPen(p.getPen(), (1, 0, 0, 1, dx, 0)))
    return pathops.simplify(p)


def area(p):
    return abs(p.area) if len(list(p.contours)) else 0


# ① 글자 모양·폭
changed, width = [], []
for g in A.order:
    if g not in B.gs: changed.append((g, "없어짐")); continue
    x = pathops.op(gpath(A, g), gpath(B, g), pathops.PathOp.XOR)
    if area(x) > 1: changed.append(g)
    if A.tt["hmtx"][g][0] != B.tt["hmtx"][g][0]: width.append(g)
added = [g for g in B.order if g not in A.gs]
expect = set(pv.SHIFT) | {"uni20A9"}

# ② 글자 쌍 간격 (두 서체 모두에 있는 글자끼리, 합자 끔)
cmA, cmB = A.tt.getBestCmap(), B.tt.getBestCmap()
chars = [chr(u) for u in sorted(cmB) if u > 32]
old = [c for c in chars if ord(c) in cmA]


def kern(f, a, b):
    gl, w = f.shape(a + b, {"kern": True, "liga": False})
    cm = f.tt.getBestCmap(); hm = f.tt["hmtx"]
    return w - hm[cm[ord(a)]][0] - hm[cm[ord(b)]][0]


kdiff = {}
for a, b in itertools.product(old, old):
    ka, kb = kern(A, a, b), kern(B, a, b)
    if ka != kb: kdiff[a + b] = (ka, kb)
newk = {}
for a, b in itertools.product(chars, chars):
    if ord(a) in cmA and ord(b) in cmA: continue
    k = kern(B, a, b)
    if k: newk[a + b] = k

# ③ 닿음 검사 (v1.32, 커닝 적용, 합자 끔)
touch, n = [], 0
P = {}
for a, b in itertools.product(chars, chars):
    gl, _ = B.shape(a + b, {"kern": True, "liga": False})
    (ga, xa, _), (gb, xb, _) = gl
    if ga not in P: P[ga] = gpath(B, ga)
    pb = gpath(B, gb, xb - xa)
    if not len(list(P[ga].contours)) or not len(list(pb.contours)): continue
    n += 1
    if area(pathops.op(P[ga], pb, pathops.PathOp.INTERSECTION)) > 0.5: touch.append(a + b)

# ④ 파일 설정
t = TTFont(lib.ROOT + "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf")
names = {(r.nameID, r.langID): str(r) for r in t["name"].names if r.platformID == 3}
res = dict(
    changed_glyphs=sorted(changed), unexpected_changed=sorted(set(changed) - expect), missing_expected=sorted(expect - set(changed)),
    width_changed=width, added=added,
    kern_changed=kdiff, kern_unexpected=sorted(set(kdiff) - set(json.load(open(pv.OUT + "kern-diag-inter.json", encoding="utf-8"))["pairs"])),
    new_glyph_kern_pairs=len(newk), pairs_checked=n, touching=touch,
    fsType=t["OS/2"].fsType, version=names.get((5, 0x409)), license_en=names.get((13, 0x409)), license_ko=names.get((13, 0x412)),
    glyphs=len(t.getGlyphOrder()), cmap=len(t.getBestCmap()),
)
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, ":", v if not isinstance(v, dict) or len(v) < 30 else f"{len(v)}개")
