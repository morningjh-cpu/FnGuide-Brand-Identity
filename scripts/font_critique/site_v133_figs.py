"""폰트 업데이트 화면의 v1.33 그림: 실제 v1.32·v1.33 서체 파일로 위(이전)·아래(v1.33)
실행: py scripts/font_critique/site_v133_figs.py → out/font-critique/img/update/v133-*.png
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import lib

OUT = lib.ROOT + "out/font-critique/img/update/"
plt.rcParams["font.family"] = ["Malgun Gothic"]
A = lib.F(lib.ROOT + "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf")
B = lib.F(lib.ROOT + "out/font-update/v1.33/fonts/FnGuideLogotype-Regular.otf")
GRAY, INK, BLUE = "#80868d", "#17181a", "#2a7de1"


def pair(name, text, lines=()):
    W = max(B.shape(text)[1], A.shape(text)[1]) / 1000 + 0.3
    fig, axs = plt.subplots(2, 1, figsize=(1.0 * W, 2.3), dpi=110)
    for ax, (f, lab) in zip(axs, ((A, "v1.32"), (B, "v1.33"))):
        w = f.draw(ax, text, 0, 0, 1.0, color=INK)
        for y in lines: ax.plot([0, w], [y, y], color=BLUE, lw=0.6)
        ax.set_xlim(-0.05, W); ax.set_ylim(-0.25, 0.8); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(lab, loc="left", fontsize=10, color=GRAY)
    lib.save(OUT + name)


def gpath(f, g):
    V, C = [], []
    for op, pts in f.rec(g):
        V += pts if pts else [(0, 0)]
        C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3, "Q": [Path.CURVE3] * 2, "Z": [Path.CLOSEPOLY]}[op]
    return Path(V, C)


def detail(name, items):
    """깃발 부분 확대: 위 v1.32 · 아래 v1.33 (점·손잡이 없이 모양만)"""
    cm = B.tt.getBestCmap()
    fig, axs = plt.subplots(2, len(items), figsize=(2.6 * len(items), 5.4), dpi=110, squeeze=False)
    for j, (ch, cx, cy, r, line) in enumerate(items):
        g = cm[ord(ch)]
        for i, (f, lab) in enumerate(((A, "v1.32"), (B, "v1.33"))):
            ax = axs[i, j]
            ax.add_patch(PathPatch(gpath(f, g), fc=INK, ec="none"))
            ax.axhline(line, color=BLUE, lw=0.8)
            ax.set_xlim(cx - r, cx + r); ax.set_ylim(cy - r, cy + r); ax.set_aspect("equal")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values(): s.set_color("#e3e5e8")
            ax.set_title(f"{ch} · {lab}", loc="left", fontsize=10, color=INK if i else GRAY)
    lib.save(OUT + name)


if __name__ == "__main__":
    pair("v133-flags.png", "minimum quip jumping kiwi", lines=(0.5,))
    pair("v133-caps.png", "HIKE KILN MAVY WAVE", lines=(0.7,))
    pair("v133-round.png", "coco case sage Spectrum", lines=(0.512,))
    pair("v133-figures.png", "1,457 2026.11.09 +11%", lines=(0.644,))
    detail("v133-detail.png", [("n", 60, 450, 120, 500), ("p", 60, 450, 120, 500), ("q", 520, 450, 120, 500),
                               ("I", 120, 620, 130, 700), ("K", 120, 620, 130, 700)])
