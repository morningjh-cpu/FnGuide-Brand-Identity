"""보고서용 기호 8개 시안: ▲ ▼ ° ‰ … — ™ ® (서체 파일은 그대로, 그림·윤곽만)
- 크기·위치는 Pretendard·Inter·Helvetica Neue 등 실측 비율을 참고
- 기존 글자 조각(% . – T M R)을 써서 서체 성격을 지킴. ™ ® 는 줄인 글자의 획을 두껍게 보정
- 수학 기호 등 높이 수정안(crit2_preview.SHIFT)을 함께 적용한 상태로 보여 줌
실행: py scripts/font_critique/crit2_symbols_new.py → out/font-update/v1.32-preview/ (n1·n2 그림, new-glyphs.json)
"""
import json, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath
import pathops
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.svgPathPen import SVGPathPen
import lib, crit2_preview as pv

OUT = pv.OUT
RED, BLUE, GRAY, INK = pv.RED, pv.BLUE, pv.GRAY, pv.INK
f = pv.f
cm = f.tt.getBestCmap(); hm = f.tt["hmtx"]
MATH = pv.MATH_T                 # 수학 기호 가운데 높이 299
DASH_UP = pv.SHIFT["endash"]      # 대시 무리 올림 값(26)
K = 0.5522847498                  # 원을 베지어로 그릴 때의 상수


def P():
    return pathops.Path()


def ellipse(cx, cy, rx, ry):
    p = P(); pen = p.getPen()
    pen.moveTo((cx + rx, cy))
    pen.curveTo((cx + rx, cy + K * ry), (cx + K * rx, cy + ry), (cx, cy + ry))
    pen.curveTo((cx - K * rx, cy + ry), (cx - rx, cy + K * ry), (cx - rx, cy))
    pen.curveTo((cx - rx, cy - K * ry), (cx - K * rx, cy - ry), (cx, cy - ry))
    pen.curveTo((cx + K * rx, cy - ry), (cx + rx, cy - K * ry), (cx + rx, cy))
    pen.closePath(); return p


def poly(pts):
    p = P(); pen = p.getPen(); pen.moveTo(pts[0])
    for q in pts[1:]: pen.lineTo(q)
    pen.closePath(); return p


def ring(cx, cy, r, side, topbot):
    """바깥 원 - 안쪽 타원: 옆 두께 side, 위아래 두께 topbot (전용서체처럼 굵기 차이)"""
    return pathops.op(ellipse(cx, cy, r, r), ellipse(cx, cy, r - side, r - topbot), pathops.PathOp.DIFFERENCE)


def glyph_path(ch, scale=1.0, dx=0, dy=0, contours=None):
    """기존 글자 윤곽 → pathops Path (contours 로 일부 윤곽만 고를 수 있음)"""
    rp = RecordingPen(); f.gs[cm[ord(ch)]].draw(rp)
    if contours is not None:
        parts, cur = [], []
        for op, args in rp.value:
            cur.append((op, args))
            if op in ("closePath", "endPath"): parts.append(cur); cur = []
        rp.value = [x for i, part in enumerate(parts) if i in contours for x in part]
    p = P(); tp = TransformPen(p.getPen(), (scale, 0, 0, scale, dx, dy)); rp.replay(tp)
    return pathops.simplify(p)


def embolden(p, w):
    """획을 양쪽으로 w/2씩 두껍게"""
    s = pathops.Path(p); s.stroke(w, pathops.LineCap.BUTT_CAP, pathops.LineJoin.MITER_JOIN, 4)
    return pathops.op(p, s, pathops.PathOp.UNION)


def union(*ps):
    out = ps[0]
    for q in ps[1:]: out = pathops.op(out, q, pathops.PathOp.UNION)
    return out


def build():
    G = {}
    # ▲ ▼ : 폭 520·높이 450, 가운데를 수학 기호 높이에 맞춤, 좌우 여백 60
    w, h, sb = 520, 450, 60; y0 = MATH - h / 2
    G["▲"] = (w + 2 * sb, poly([(sb, y0), (sb + w, y0), (sb + w / 2, y0 + h)]))
    G["▼"] = (w + 2 * sb, poly([(sb, y0 + h), (sb + w / 2, y0), (sb + w, y0 + h)]))
    # ° : 지름 300, 위끝 705, 옆 70·위아래 45
    G["°"] = (420, ring(60 + 150, 705 - 150, 150, 70, 45))
    # ‰ : % 오른쪽 아래 고리(윤곽 3·4)를 400 옆에 하나 더
    per = glyph_path("%"); extra = glyph_path("%", dx=400, contours=[3, 4])
    G["‰"] = (hm["percent"][0] + 400, union(per, extra))
    # … : 마침표 3개를 마침표 너비 간격으로
    pa = hm["period"][0]
    G["…"] = (3 * pa, union(*(glyph_path(".", dx=i * pa) for i in range(3))))
    # — : en 대시 두께(66)·높이(+26 올린 뒤)로 한 칸 너비, 양쪽 여백 50
    G["—"] = (1000, poly([(50, 221 + DASH_UP), (950, 221 + DASH_UP), (950, 287 + DASH_UP), (50, 287 + DASH_UP)]))
    # ™ : T·M 을 0.42배로 줄여 위끝 700 에 맞춤, 획 +21 보정
    s = 0.42; dy = 700 - 700 * s; lsb = 40
    t = glyph_path("T", s, lsb - 37 * s, dy)
    m = glyph_path("M", s, lsb - 37 * s + hm["T"][0] * s - 10, dy)
    tm = embolden(union(t, m), 21)
    tm2 = pathops.Path(); tm.draw(TransformPen(tm2.getPen(), (1, 0, 0, 1, 0, 700 - tm.bounds[3]))); tm = tm2   # 두껍게 한 만큼 내려 위끝 700
    G["™"] = (round(lsb - 37 * s + (hm["T"][0] + hm["M"][0]) * s - 10 + lsb), tm)
    # ® : 지름 560 고리(옆 50·위아래 38), 위끝 710, 안에 R 0.40배 + 획 +20 보정
    r = 280; cx, cy = 50 + r, 710 - r; s = 0.40
    rw, rh = (662 - 26) * s, 700 * s
    R = embolden(glyph_path("R", s, cx - rw / 2 - 26 * s, cy - rh / 2), 20)
    G["®"] = (2 * r + 100, union(ring(cx, cy, r, 50, 38), R))
    return G


def to_mpl(p, x0, s=1 / 1000):
    rp = RecordingPen(); p.draw(rp)
    V, C = [], []
    for op, args in rp.value:
        if op == "moveTo": V.append(args[0]); C.append(MPath.MOVETO)
        elif op == "lineTo": V.append(args[0]); C.append(MPath.LINETO)
        elif op == "curveTo": V += list(args); C += [MPath.CURVE4] * 3
        elif op == "qCurveTo": V += list(args); C += [MPath.CURVE3] * 2
        elif op == "closePath": V.append((0, 0)); C.append(MPath.CLOSEPOLY)
    V = [(x0 + x * s, y * s) for x, y in V]
    return MPath(V, C) if V else None


PRE = lib.F(lib.UF + "Pretendard-Medium.ttf")


def draw_line(ax, text, G, mode):
    """mode: new(새 기호 + 높이 수정안) / now(지금 v1.31, 없는 글자는 Pretendard Medium)"""
    x = 0; run = ""

    def flush():
        nonlocal x, run
        if run: x += pv.draw(ax, run, x, 0, 1.0, new=(mode == "new"), hl=False); run = ""
    for ch in text:
        if ch in G:
            flush()
            if mode == "new":
                adv, p = G[ch]; mp = to_mpl(p, x)
                ax.add_patch(PathPatch(mp, fc=RED, ec="none")); x += adv / 1000
            else:
                x += PRE.draw(ax, ch, x, 0, 1.0, color="#6a6f75")
        else:
            run += ch
    flush(); return x


def figs(G):
    # n1: 글자 확대 — 숫자·대문자와 함께
    t = "H0▲▼0°C 1‰ …—™®"
    fig, ax = plt.subplots(1, 1, figsize=(16, 2.6), dpi=120)
    w = draw_line(ax, t, G, "new")
    for y, c in ((0, BLUE), (0.7, BLUE), (MATH / 1000, RED)):
        ax.plot([-0.05, w + 0.05], [y, y], color=c, lw=0.6)
    ax.set_xlim(-0.1, w + 0.1); ax.set_ylim(-0.12, 0.8); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("새 기호 (빨강). 파란 선 = 기준선·대문자 높이, 빨간 선 = 수학 기호 가운데 높이", loc="left", fontsize=11, color=GRAY)
    lib.save(OUT + "n1-new-glyphs.png")
    # n2: 문장 예시 — 지금(Pretendard 대신) / 수정안
    S = ["KOSPI ▲1.25%  ▼0.48%", "25°C  3‰  WiseReport™", "2026 — Q3…  DataGuide®"]
    fig, axs = plt.subplots(len(S) * 2, 1, figsize=(16, 1.25 * 2 * len(S)), dpi=110)
    W = 12
    for i, t in enumerate(S):
        for j, mode in enumerate(("now", "new")):
            ax = axs[i * 2 + j]; draw_line(ax, t, G, mode)
            ax.set_xlim(-0.05, W); ax.set_ylim(-0.25, 0.8); ax.set_aspect("equal"); ax.axis("off")
            ax.set_title("지금 v1.31 (없는 글자는 Pretendard Medium, 회색)" if mode == "now" else "수정안 (새 기호, 빨강)",
                         loc="left", fontsize=11, color=GRAY if mode == "now" else RED)
    lib.save(OUT + "n2-sentences.png")


def check(G):
    """새 기호와 이웃 글자(숫자·대문자·소문자) 닿음 검사 — 커닝 없이 글자 폭만으로 놓았을 때"""
    near = []
    others = "0123456789HOAVTYnoe%"
    for ch, (adv, p) in G.items():
        for o in others:
            g = cm[ord(o)]; op_ = glyph_path(o)
            for left, right, la in ((p, op_, adv), (op_, p, hm[g][0])):
                q = pathops.Path(); right.draw(TransformPen(q.getPen(), (1, 0, 0, 1, la, 0)))
                inter = pathops.op(left, q, pathops.PathOp.INTERSECTION)
                if len(list(inter.contours)) > 0: near.append((ch, o))
    return near


if __name__ == "__main__":
    G = build()
    data = {}
    for ch, (adv, p) in G.items():
        sp = SVGPathPen(None); p.draw(sp)
        b = p.bounds
        data[ch] = dict(advance=int(adv), bounds=[round(v) for v in b], svg=sp.getCommands())
    json.dump(data, open(OUT + "new-glyphs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for ch, d in data.items(): print(ch, d["advance"], d["bounds"])
    print("닿는 쌍:", check(G) or "없음")
    figs(G)
