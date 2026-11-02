"""대문자 대각선 쌍 간격을 Helvetica Neue 에 맞춘 값 계산 + 미리보기 (서체 파일은 그대로)
방법: Helvetica Neue Medium 이 보정하는 대문자 쌍 18개에 대해
      목표 간격 = FnGuide 의 HH 간격 × (Helvetica 의 그 쌍 간격 ÷ Helvetica 의 HH 간격)
      간격은 같은 높이에서 잰 가장 가까운 잉크 거리(대문자 700 기준). 최소 간격 30, 5 단위 반올림.
실행: py scripts/font_critique/crit2_kern_diag.py → out/font-update/v1.32-preview/kern-diag.json, p4·p5 그림
"""
import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import lib, crit2_measure as cm
from measure_core import bbox

OUT = lib.ROOT + "out/font-update/v1.32-preview/"
RED, BLUE, GRAY, INK = "#B9023D", "#2a7de1", "#80868d", "#17181a"
plt.rcParams["font.family"] = ["Malgun Gothic"]
PAIRS = "AT AV AW AY FA LT LV LW LY PA RT RV RW RY TA VA WA YA".split()
LOGO_PAIRS = {"AI", "IM", "MS", "AP", "PI", "AR", "RE", "ES", "ET", "TF", "PF", "FG"}   # 로고 이름의 대문자 쌍 (안 건드림)

import sys
REF = sys.argv[1] if len(sys.argv) > 1 else "Helvetica Neue Medium"     # 예: py crit2_kern_diag.py "Inter Medium"
TAG = "" if REF.startswith("Helvetica") else "-" + REF.split()[0].lower()
f, h = lib.load("FnGuide v1.31"), lib.load(REF)
kh = 700 / bbox(h, "H")[3]


def calc():
    fHH = cm.ink_gap(f, "HH", 0); hHH = cm.ink_gap(h, "HH", 0) * kh
    rows = {}
    for p in PAIRS:
        assert p not in LOGO_PAIRS
        cur_k = cm.kern(f, p[0], p[1]); cur_g = cm.ink_gap(f, p, 0)
        hg = cm.ink_gap(h, p, 0) * kh
        target = max(30, fHH * hg / hHH)
        new_k = int(round((cur_k + (target - cur_g)) / 5) * 5)
        while cur_g + new_k - cur_k < 30: new_k += 5      # 반올림으로 최소 간격 30 밑으로 가지 않게
        rows[p] = dict(kern_now=cur_k, gap_now=round(cur_g), ref_ratio=round(hg / hHH, 2),
                       gap_target=round(target), kern_new=new_k, delta=new_k - cur_k,
                       gap_new=round(cur_g + new_k - cur_k))
    return dict(HH_fn=round(fHH), HH_helv=round(hHH), pairs=rows)


def draw(ax, text, R, new):
    gl, adv = f.shape(text); s = 1 / f.upm; shift = 0
    for i, (g, gx, gy) in enumerate(gl):
        if new and i > 0:
            p = text[i - 1] + text[i]
            if p in R: shift += R[p]["delta"]
        V, C = [], []
        for op, pts in f.rec(g):
            V += [((gx + px + shift) * s, (gy + py) * s) for px, py in pts] if pts else [(0, 0)]
            C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3,
                  "Q": [Path.CURVE3] * 2, "Z": [Path.CLOSEPOLY]}[op]
        if V: ax.add_patch(PathPatch(Path(V, C), fc=INK, ec="none"))
    return (adv + shift) * s


def figs(R):
    lines = ["HLYH HLVH HLTH HLWH HAVH HAYH HTAH HVAH", "FLY  LTV  AVATAR  WAY  PATRY  YAW"]
    for n, t in enumerate(lines):
        W = f.shape(t)[1] / f.upm + 0.3
        fig, axs = plt.subplots(3, 1, figsize=(1.15 * W, 4.6), dpi=110)
        for ax, (lab, mode) in zip(axs, (("지금 v1.31", "now"), (f"수정안 ({REF} 비율)", "new"), (REF, "ref"))):
            if mode == "ref":
                w = h.draw(ax, t, 0, 0, 0.7 / (bbox(h, "H")[3] / h.upm))
            else:
                w = draw(ax, t, R, mode == "new")
            ax.set_xlim(-0.05, W); ax.set_ylim(-0.1, 0.78); ax.set_aspect("equal"); ax.axis("off")
            ax.set_title(lab, loc="left", fontsize=11, color=RED if mode == "new" else GRAY)
        lib.save(OUT + f"p{4 + n}-kern-diag{TAG}.png")


if __name__ == "__main__":
    res = calc()
    json.dump(res, open(OUT + f"kern-diag{TAG}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("HH", res["HH_fn"], res["HH_helv"])
    for p, r in res["pairs"].items(): print(p, r)
    figs(res["pairs"])
