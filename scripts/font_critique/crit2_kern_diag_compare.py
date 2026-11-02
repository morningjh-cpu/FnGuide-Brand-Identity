"""대문자 대각선 18쌍: 여러 해외 서체 비율로 계산해 비교 (Helvetica Neue·Inter 는 이미 본 것이라 뺌)
목표 간격 = FnGuide 기준 간격 × (참고 서체 쌍 간격 ÷ 참고 서체 기준 간격), 최소 30, 5 단위.
기준 간격 두 가지:
  HH   — crit2_kern_diag.py(v1.32)와 같은 방식. FnGuide 는 로고 리듬 때문에 HH 가 유난히 좁아(56) 대각선도 촘촘해진다.
  mean — HH·HO·OH·OO 네 쌍의 평균. 둥근 글자 옆 간격까지 반영한 "대문자 평균 간격"(FnGuide 85).
실행: py scripts/font_critique/crit2_kern_diag_compare.py → out/font-update/kern-diag-compare/
"""
import os, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import lib, crit2_measure as cm
from measure_core import bbox

OUT = lib.ROOT + "out/font-update/kern-diag-compare/"
os.makedirs(OUT, exist_ok=True)
plt.rcParams["font.family"] = ["Malgun Gothic"]
RED, GRAY, INK = "#B9023D", "#80868d", "#17181a"
PAIRS = "AT AV AW AY FA LT LV LW LY PA RT RV RW RY TA VA WA YA".split()
SF, UF = lib.SF, lib.UF
REFS = {
    "Avenir Next Demi": lib.FONTS["Avenir Next Demi"], "DIN Medium": lib.FONTS["DIN Medium"],
    "Futura Medium": lib.FONTS["Futura Medium"], "Rotis Semi Sans Bold": lib.FONTS["Rotis Semi Sans Bold"],
    "Candara Bold": SF + "Candarab.ttf", "Corbel Bold": SF + "corbelb.ttf", "Segoe UI Semibold": SF + "seguisb.ttf",
    "Calibri Bold": SF + "calibrib.ttf", "Verdana Bold": SF + "verdanab.ttf", "Tahoma Bold": SF + "tahomabd.ttf",
    "Trebuchet MS Bold": SF + "trebucbd.ttf", "Arial Bold": SF + "arialbd.ttf",
    "SF Pro Display Semibold": UF + "SF-Pro-Display-Semibold.otf",
    "Georgia Bold": SF + "georgiab.ttf", "Cambria Bold": SF + "cambriab.ttf",
}
f = lib.load("FnGuide v1.31")            # 18쌍 이외는 v1.32 와 같은 글자·간격
V132 = json.load(open(lib.ROOT + "out/font-update/v1.32-preview/kern-diag-inter.json", encoding="utf-8"))["pairs"]


BASIS = ["HH", "HO", "OH", "OO"]


def basis(font, k=1.0, mode="mean"):
    if mode == "HH": return cm.ink_gap(font, "HH", 0) * k
    return sum(cm.ink_gap(font, w, 0) for w in BASIS) / len(BASIS) * k


def calc(mode="mean"):
    fHH = basis(f, 1.0, mode)
    base = {p: (cm.kern(f, p[0], p[1]), cm.ink_gap(f, p, 0)) for p in PAIRS}
    res = {}
    for name, path in REFS.items():
        if not os.path.exists(path): continue
        h = lib.F(path); k = 700 / bbox(h, "H")[3]
        hHH = basis(h, k, mode)
        row = {}
        for p in PAIRS:
            ck, cg = base[p]
            hg = cm.ink_gap(h, p, 0) * k
            target = max(30, fHH * hg / hHH)
            nk = int(round((ck + (target - cg)) / 5) * 5)
            while cg + nk - ck < 30: nk += 5
            row[p] = dict(ratio=round(hg / hHH, 2), kern=nk, gap=round(cg + nk - ck))
        mean_gap = sum(r["gap"] for r in row.values()) / len(row)
        res[name] = dict(pairs=row, mean_gap=round(mean_gap, 1), HH=round(hHH))
        print(name, res[name]["mean_gap"])
    cur = {p: dict(kern=V132[p]["kern_new"], gap=V132[p]["gap_new"]) for p in PAIRS}
    v131 = {p: dict(kern=base[p][0], gap=round(base[p][1])) for p in PAIRS}
    return dict(mode=mode, basis_fn=round(fHH), v131=v131, v132_inter=cur,
                v132_mean_gap=round(sum(r["gap"] for r in cur.values()) / 18, 1),
                v131_mean_gap=round(sum(r["gap"] for r in v131.values()) / 18, 1), refs=res)


def draw(ax, text, kerns):
    gl, adv = f.shape(text); s = 1 / f.upm; shift = 0
    for i, (g, gx, gy) in enumerate(gl):
        if i > 0:
            p = text[i - 1] + text[i]
            if p in kerns: shift += kerns[p] - cm.kern(f, p[0], p[1])
        V, C = [], []
        for op, pts in f.rec(g):
            V += [((gx + px + shift) * s, (gy + py) * s) for px, py in pts] if pts else [(0, 0)]
            C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3,
                  "Q": [Path.CURVE3] * 2, "Z": [Path.CLOSEPOLY]}[op]
        if V: ax.add_patch(PathPatch(Path(V, C), fc=INK, ec="none"))
    return (adv + shift) * s


def fig(R, names, fname, text="FLY LTV AVATAR WAY PATRY YAW"):
    rows = [("v1.31 (원래)", {p: v["kern"] for p, v in R["v131"].items()}, None),
            ("v1.32 지금 (Inter 비율)", {p: v["kern"] for p, v in R["v132_inter"].items()}, None)]
    rows += [(f"{n} 비율 적용", {p: v["kern"] for p, v in R["refs"][n]["pairs"].items()}, n) for n in names]
    W = f.shape(text)[1] / 1000 + 0.6
    fig, axs = plt.subplots(len(rows), 2, figsize=(2.0 * W, 1.05 * len(rows)), dpi=100,
                            gridspec_kw={"width_ratios": [1, 1]})
    for (lab, kk, ref), (a1, a2) in zip(rows, axs):
        draw(a1, text, kk)
        a1.set_title(lab, loc="left", fontsize=10, color=RED if ref else GRAY)
        if ref:
            h = lib.F(REFS[ref]); h.draw(a2, text, 0, 0, 0.7 / (bbox(h, "H")[3] / h.upm))
            a2.set_title(f"{ref} 원래 모습", loc="left", fontsize=10, color=GRAY)
        for a in (a1, a2):
            a.set_xlim(-0.05, W); a.set_ylim(-0.1, 0.78); a.set_aspect("equal"); a.axis("off")
    lib.save(OUT + fname)


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "mean"
    R = calc(mode)
    json.dump(R, open(OUT + f"compare-{mode}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    order = sorted(R["refs"], key=lambda n: R["refs"][n]["mean_gap"])
    print("v1.31", R["v131_mean_gap"], "v1.32", R["v132_mean_gap"], "순서", order)
    if mode == "mean":
        pick = [n for n in order if R["v132_mean_gap"] < R["refs"][n]["mean_gap"] < R["v131_mean_gap"]]
        fig(R, pick, "compare-words.png")
        fig(R, pick, "compare-pairs.png", "HLYH HLVH HLTH HAVH HAWH HTAH HRYH")
        print("미리보기:", pick)
