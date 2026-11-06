"""v1.33 확인: ① 바뀐 글자(예상 목록과 비교)·폭 ② 글자 쌍 간격 규칙 그대로인지 ③ 모든 글자 쌍 닿음 ④ 3차 크리틱 항목 수치
실행: py scripts/font_critique/check_v133.py → out/font-update/v1.33/check.json
"""
import json, itertools, os, sys
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
import lib, v133_edits as ED

A = lib.F(lib.ROOT + "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf")
B = lib.F(lib.ROOT + "out/font-update/v1.33/fonts/FnGuideLogotype-Regular.otf")
OUT = lib.ROOT + "out/font-update/v1.33/check.json"
AXIS = {"F", "E", "m", "p", "b", "f_b", "q", "u", "dollar", "one", "one.tf"}


def gpath(f, g, dx=0):
    p = pathops.Path(); f.gs[g].draw(TransformPen(p.getPen(), (1, 0, 0, 1, dx, 0)))
    return pathops.simplify(p)


def area(p):
    return abs(p.area) if len(list(p.contours)) else 0


# ① 글자 모양·폭 (겹친 넓이가 1 넘게 달라진 글자)
changed, width, small = [], {}, []
for g in A.order:
    x = area(pathops.op(gpath(A, g), gpath(B, g), pathops.PathOp.XOR))
    if x > 0: (changed if x > 1 else small).append(g)
    if A.tt["hmtx"][g][0] != B.tt["hmtx"][g][0]: width[g] = (A.tt["hmtx"][g][0], B.tt["hmtx"][g][0])
expect = AXIS | set(ED.SUB) | set(ED.SUB_OPTIONAL) | set(ED.SHIFT_Y) | ED.COLLINEAR | set(ED.SHIFT_X)

# ② 글자 쌍 간격 규칙
cm = B.tt.getBestCmap()
chars = [chr(u) for u in sorted(cm) if u > 32]


def kern(f, a, b):
    gl, w = f.shape(a + b, {"kern": True, "liga": False})
    hm = f.tt["hmtx"]; c = f.tt.getBestCmap()
    return w - hm[c[ord(a)]][0] - hm[c[ord(b)]][0]


kdiff = {a + b: (kern(A, a, b), kern(B, a, b)) for a, b in itertools.product(chars, chars) if kern(A, a, b) != kern(B, a, b)}

# ③ 닿음 검사 (커닝 적용, 합자 끔)
touch, n, P = [], 0, {}
for a, b in itertools.product(chars, chars):
    gl, _ = B.shape(a + b, {"kern": True, "liga": False})
    (ga, xa, _), (gb, xb, _) = gl
    if ga not in P: P[ga] = gpath(B, ga)
    pb = gpath(B, gb, xb - xa)
    if not len(list(P[ga].contours)) or not len(list(pb.contours)): continue
    n += 1
    if area(pathops.op(P[ga], pb, pathops.PathOp.INTERSECTION)) > 0.5: touch.append(a + b)
touch_before = []
for p in touch:
    gl, _ = A.shape(p, {"kern": True, "liga": False})
    (ga, xa, _), (gb, xb, _) = gl
    if area(pathops.op(gpath(A, ga), gpath(A, gb, xb - xa), pathops.PathOp.INTERSECTION)) > 0.5: touch_before.append(p)

# 좌우 여백 변화(글자 사이 간격에 영향)
def sb(f, g):
    b = gpath(f, g).bounds
    return (round(b[0]), round(f.tt["hmtx"][g][0] - b[2])) if b else None
sbdiff = {g: (sb(A, g), sb(B, g)) for g in sorted(set(changed) | set(small)) if sb(A, g) != sb(B, g)}

t = TTFont(lib.ROOT + "out/font-update/v1.33/fonts/FnGuideLogotype-Regular.otf")
res = dict(changed_glyphs=sorted(changed), tiny_changed=sorted(small),
           unexpected_changed=sorted((set(changed) | set(small)) - expect), expected_unchanged=sorted(expect - set(changed) - set(small)),
           width_changed=width, sidebearing_changed=sbdiff,
           kern_changed=kdiff, pairs_checked=n, touching=touch, touching_also_in_v132=touch_before,
           version=str(t["name"].getName(5, 3, 1, 0x409)), glyphs=len(t.getGlyphOrder()))
json.dump(res, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, ":", v)
