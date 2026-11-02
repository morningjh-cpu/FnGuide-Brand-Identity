"""2차 크리틱 반영 수정안 미리보기 (서체 파일은 고치지 않음, 그림만)
- 수학 기호: B안 — 가운데 높이를 + 기준 55 올린 높이(299, 대문자의 0.43)에 모두 맞춤
- 그 밖에 낮은 기호: 하이픈·en 대시 280, 가운뎃점 299, / \\ +30, @ +50
- ₩: 왼쪽 위 세리프 제거 (왼쪽 굵은 획 바깥선을 위로 곧게 이어 700 에서 끝냄)
실행: py scripts/font_critique/crit2_preview.py  → out/font-update/v1.32-preview/
"""
import os, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from fontTools.pens.boundsPen import BoundsPen
import lib

OUT = lib.ROOT + "out/font-update/v1.32-preview/"
os.makedirs(OUT, exist_ok=True)
RED, BLUE, GRAY, INK = "#B9023D", "#2a7de1", "#80868d", "#17181a"
plt.rcParams["font.family"] = ["Malgun Gothic"]
f = lib.load("FnGuide v1.31")


def center(g):
    bp = BoundsPen(f.gs); f.gs[g].draw(bp); b = bp.bounds; return (b[1] + b[3]) / 2


MATH_T = round(center("plus") + 55)        # B안: + 를 55 올린 가운데 높이
groups = {
    "수학 기호 (B안)": (["plus", "minus", "plusminus", "equal", "less", "greater", "multiply", "asciitilde",
                        "plus.tf", "minus.tf", "plusminus.tf"], MATH_T),
    "하이픈·en 대시": (["hyphen", "endash"], 280),
    "가운뎃점": (["periodcentered"], MATH_T),
}
SHIFT = {}
for _, (gs, target) in groups.items():
    for g in gs: SHIFT[g] = round(target - center(g))
SHIFT.update({"slash": 30, "backslash": 30, "at": 50})

# ₩ 새 윤곽: 세리프 점(258,700)→(46,700)→(46,664)→(61,661)→곡선→(168,560) 을 지우고
# 바깥선 (229,318)-(308,6) 의 기울기로 (213,383) 에서 700 까지 곧게 이음
_k = (229 - 308) / (318 - 6)
TOP_X = round(229 + _k * (700 - 318))       # ≈ 132


def won_ops():
    ops = []
    for op, pts in f.rec("uni20A9"):
        ops.append((op, [(round(x), round(y)) for x, y in pts]))
    out, skip = [], False
    for op, pts in ops:
        if op == "L" and pts == [(258, 700)]:
            out.append((op, pts)); out.append(("L", [(TOP_X, 700)])); skip = True; continue
        if skip:
            if op == "L" and pts == [(213, 383)]:
                skip = False; out.append((op, pts))
            continue
        out.append((op, pts))
    return out


REPLACE = {"uni20A9": won_ops()}


def draw(ax, text, x0=0, y0=0, size=1.0, new=False, feats=None, hl=True):
    gl, adv = f.shape(text, feats); s = size / f.upm
    for g, gx, gy in gl:
        ops = REPLACE.get(g, f.rec(g)) if new else f.rec(g)
        up = SHIFT.get(g, 0) if new else 0
        V, C = [], []
        for op, pts in ops:
            V += [(x0 + (gx + px) * s, y0 + (gy + py + up) * s) for px, py in pts] if pts else [(0, 0)]
            C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3,
                  "Q": [Path.CURVE3] * 2, "Z": [Path.CLOSEPOLY]}[op]
        if V:
            mark = hl and (g in SHIFT or g in REPLACE)
            ax.add_patch(PathPatch(Path(V, C), fc=RED if mark else INK, ec="none"))
    return adv * s


SAMPLES = [
    ("수학 기호", "+1.25% \u22120.48% \u00b10.5 A+B x=3 <10> 2\u00d73 ~5", None),
    ("표 숫자 (고정폭)", "+1,024.50 \u2212314.16 \u00b12.00", {"kern": True, "tnum": True}),
    ("하이픈·대시", "2026-11-02  10\u201320  e-mail  -0.48", None),
    ("가운뎃점", "FnGuide\u00b7WiseReport  A\u00b7B\u00b7C", None),
    ("빗금", "A/B  1/2  and/or  C:\\Data", None),
    ("골뱅이", "help@fnguide.com  @FnGuide", None),
    ("원화", "\u20a91,000  \u20a925,000  W\u20a9", None),
]


def fig_rows():
    W = max(f.shape(t, ft)[1] for _, t, ft in SAMPLES) / f.upm + 0.2
    fig, axs = plt.subplots(len(SAMPLES) * 2, 1, figsize=(1.2 * W, 1.15 * 2 * len(SAMPLES)), dpi=110)
    for i, (lab, t, feats) in enumerate(SAMPLES):
        for j, new in enumerate((False, True)):
            ax = axs[i * 2 + j]
            w = draw(ax, t, 0, 0, 1.0, new, feats)
            ax.plot([0, w], [0.35, 0.35], color=BLUE, lw=0.5)
            ax.set_xlim(-0.05, W); ax.set_ylim(-0.25, 0.8); ax.set_aspect("equal"); ax.axis("off")
            ax.set_title(f"{lab} · {'수정안' if new else '지금 v1.31'}", loc="left", fontsize=11,
                         color=RED if new else GRAY)
    lib.save(OUT + "p1-before-after.png")


def fig_won():
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), dpi=110)
    for ax, (lab, t, new) in zip(axs, (("지금", "\u20a9", False), ("수정안", "\u20a9", True), ("참고: W", "W", False))):
        draw(ax, t, 0, 0, 1.0, new, hl=False)
        for y in (0, 0.7): ax.plot([-0.05, 1.2], [y, y], color=BLUE, lw=0.5)
        ax.set_xlim(-0.05, 1.2); ax.set_ylim(-0.08, 0.78); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(lab, loc="left", fontsize=12, color=RED if new else GRAY)
    lib.save(OUT + "p2-won.png")


def fig_ref():
    from measure_core import bbox
    t = "+1.25% \u22120.48% A+B x=3 <10> 2\u00d73 a\u00b7b e-mail"
    W = f.shape(t)[1] / f.upm * 1.12
    fig, axs = plt.subplots(4, 1, figsize=(1.2 * W, 6.4), dpi=110)
    rows = [("FnGuide 수정안", None), ("Avenir Next Demi", "Avenir Next Demi"),
            ("Inter Medium", "Inter Medium"), ("FnGuide 지금 v1.31", None)]
    for ax, (lab, ref) in zip(axs, rows):
        if ref:
            r = lib.load(ref); k = 0.7 / (bbox(r, "H")[3] / r.upm); w = r.draw(ax, t, 0, 0, k)
        else:
            w = draw(ax, t, 0, 0, 1.0, new=("수정안" in lab), hl=False)
        ax.plot([0, w], [0.35, 0.35], color=BLUE, lw=0.5)
        ax.set_xlim(-0.05, W); ax.set_ylim(-0.25, 0.8); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(lab, loc="left", fontsize=11, color=RED if "수정안" in lab else GRAY)
    lib.save(OUT + "p3-reference.png")


if __name__ == "__main__":
    fig_rows(); fig_won(); fig_ref()
    info = {"math_target": MATH_T, "shift": SHIFT, "won_top_x": TOP_X}
    json.dump(info, open(OUT + "shift.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(info)
