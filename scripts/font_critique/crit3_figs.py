"""3차 크리틱(v1.33 작업본) 그림 60~69. 실행: py scripts/font_critique/crit3_figs.py [번호...]"""
import sys, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, lib
from matplotlib.path import Path
from matplotlib.patches import PathPatch

OUT = lib.ROOT + "out/font-critique/img/"
RED, BLUE, ORG, GRAY, INK = "#B9023D", "#2a7de1", "#e08a00", "#80868d", "#17181a"
plt.rcParams["font.family"] = ["Malgun Gothic"]
plt.rcParams["axes.unicode_minus"] = False
F = lib.load("FnGuide v1.33")
G = {chr(u): g for u, g in F.tt.getBestCmap().items() if 33 <= u < 127}


def gpath(g, dx=0, dy=0):
    V, C = [], []
    for op, pts in F.rec(g):
        P = [(x + dx, y + dy) for x, y in pts]
        V += P if P else [(0, 0)]
        C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3, "Z": [Path.CLOSEPOLY]}[op]
    return Path(V, C)


def glyph(ax, g, dx=0, dy=0, fc=INK, alpha=1, nodes=False):
    ax.add_patch(PathPatch(gpath(g, dx, dy), fc=fc, ec="none", lw=0, alpha=alpha))
    if not nodes:
        return
    cur = None
    for op, pts in F.rec(g):
        P = [(x + dx, y + dy) for x, y in pts]
        if op == "C":
            ax.plot([cur[0], P[0][0]], [cur[1], P[0][1]], color=BLUE, lw=0.8)
            ax.plot([P[1][0], P[2][0]], [P[1][1], P[2][1]], color=BLUE, lw=0.8)
            ax.plot([P[0][0], P[1][0]], [P[0][1], P[1][1]], "o", ms=3, color=BLUE)
        if P:
            ax.plot(P[-1][0], P[-1][1], "s", ms=4, color=RED, mec="white", mew=0.5)
            cur = P[-1]


def zoom(ax, g, cx, cy, r, title, lines=(), nodes=True):
    glyph(ax, g, fc=INK, alpha=0.8, nodes=nodes)
    for y, col in lines:
        ax.axhline(y, color=col, lw=0.9)
    ax.set_xlim(cx - r, cx + r); ax.set_ylim(cy - r, cy + r); ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([]); ax.set_title(title, fontsize=11, loc="left")
    for s in ax.spines.values():
        s.set_color("#ddd")


def adv(g):
    return F.tt["hmtx"][g][0]


def row(ax, text, lines=(), hl=()):
    x = 0
    for ch in text:
        if ch == " ":
            x += 250; continue
        g = G[ch]; glyph(ax, g, x, 0, fc=RED if ch in hl else INK); x += adv(g) + 30
    for y, col in lines:
        ax.plot([-20, x], [y, y], color=col, lw=1.3)
    ax.set_xlim(-40, x + 20); ax.set_ylim(-240, 760); ax.set_aspect("equal"); ax.axis("off")
    return x


# 60 소문자 깃발 세리프: 기둥 왼쪽 면을 맞춰 겹쳐 보기
FLAG_X = {"n": 92, "m": 91, "r": 93, "p": 87, "i": 88, "u": 84, "j": 231, "h": 82, "b": 82, "l": 82, "k": 82, "d": 382}
def fig60():
    fig, axs = plt.subplots(1, 2, figsize=(16, 5.6), dpi=110)
    cols = ["#17181a", "#B9023D", "#2a7de1", "#e08a00", "#2f7d4f", "#8e44ad", "#16a085"]
    for ax, grp, base, title in ((axs[0], "nmrpiuj", 0, "x높이 깃발 n m r p i u j"),
                                 (axs[1], "hblkd", 197, "어센더 깃발 h b l k d (197 내려 겹침)")):
        for k, c in enumerate(grp):
            ax.add_patch(PathPatch(gpath(G[c], -FLAG_X[c], -base), fc="none", ec=cols[k], lw=1.4))
        ax.set_xlim(-110, 130); ax.set_ylim(405, 512); ax.set_aspect("equal")
        for y in (500, 464, 431):
            ax.axhline(y, color="#bbb", lw=0.6, ls="--")
        ax.legend(handles=[plt.Line2D([], [], color=cols[k], lw=2, label=c) for k, c in enumerate(grp)],
                  loc="lower right", fontsize=11, ncol=4)
        ax.set_title(title + " — 기둥 왼쪽 면을 0 에 맞춤", fontsize=12, loc="left")
        ax.set_xticks(range(-100, 131, 20)); ax.tick_params(labelsize=8); ax.grid(alpha=0.15)
    lib.save(OUT + "60-flags-lower.png")


# 61 대문자 깃발
def fig61():
    items = [("H", 90, 640, "H (기준: 위 수평 700)"), ("I", 90, 640, "I (위가 기움, 끝 두께 43)"), ("K", 90, 640, "K (위가 기움)"),
             ("M", 90, 640, "M (높이 704)"), ("A", 250, 640, "A (높이 699)"), ("V", 90, 640, "V"), ("Y", 90, 640, "Y"), ("W", 90, 640, "W")]
    fig, axs = plt.subplots(2, 4, figsize=(16, 8.4), dpi=110)
    for ax, (c, cx, cy, t) in zip(axs.flat, items):
        zoom(ax, G[c], cx, cy, 95, t, lines=[(700, BLUE)])
    lib.save(OUT + "61-flags-upper.png")


# 62 높이선·기준선 이탈
def fig62():
    items = [("M", 820, 700, "M 위 704 (+4)"), ("I", 250, 700, "I 위 701 (+1)"), ("A", 300, 700, "A 위 699 (-1)"), ("V", 735, 700, "V 오른쪽 위 699"),
             ("D", 200, 0, "D 바닥 1 (+1)"), ("K", 600, 0, "K 오른쪽 바닥 -1"), ("Z", 300, 0, "Z 바닥 -1"), ("4", 420, 0, "4 바닥 -1"),
             ("w", 100, 500, "w 위 498 (-2)"), ("z", 250, 500, "z 위 498 (-2)"), ("y", 172, -210, "y 아래 -209"), ("j", 167, -210, "j 아래 -207 (-3)")]
    fig, axs = plt.subplots(3, 4, figsize=(16, 12), dpi=100)
    for ax, (c, cx, cy, t) in zip(axs.flat, items):
        zoom(ax, G[c], cx, cy, 14, t, lines=[(cy, BLUE)], nodes=False)
    lib.save(OUT + "62-heights.png")


# 63 곡선 이음매 꺾임
def fig63():
    items = [("V", 144, 619, 40, "V 깃발 끝 10.7°"), ("Y", 144, 619, 40, "Y 같은 자리 3.0°"), ("A", 205, 660, 30, "A 깃발 7.3°"),
             ("K", 40, 636, 30, "K 깃발 5.5°"), ("G", 632, 29, 40, "G 아래 7.9°"), ("e", 344, 57, 30, "e 아래 끝 5.3°"),
             ("f", 491, 604, 30, "f 위 끝 4.5° (fi ft fj 도)"), ("H", 118, 638, 30, "대문자 깃발 이음 2.0° (11자 공통)")]
    fig, axs = plt.subplots(2, 4, figsize=(16, 8.4), dpi=110)
    for ax, (c, cx, cy, r, t) in zip(axs.flat, items):
        zoom(ax, G[c], cx, cy, r, t)
    lib.save(OUT + "63-kinks.png")


# 64 불필요한 점·짧은 선
def fig64():
    items = [("w", 55, 440, 70, "w 세리프: 곡선 대신 짧은 직선 12개"), ("a", 252, 498, 12, "a 1 단위 계단"), ("k", 519, 488, 12, "k 1 단위 계단"),
             ("r", 416, 496, 12, "r 1 단위 계단"), ("E", 535, 540, 14, "E F 세리프 끝 3 단위 턱"), ("8", 419, 338, 12, "8 1 단위 짧은 선")]
    fig, axs = plt.subplots(2, 3, figsize=(15, 10), dpi=100)
    for ax, (c, cx, cy, r, t) in zip(axs.flat, items):
        zoom(ax, G[c], cx, cy, r, t)
    lib.save(OUT + "64-nodes.png")


# 65 둥근 소문자 가는 획
def fig65():
    fig, axs = plt.subplots(2, 1, figsize=(15, 6.6), dpi=110)
    row(axs[0], "bodpq", lines=[(512, GRAY), (500, BLUE), (0, BLUE)], hl="o")
    axs[0].set_title("o 위·아래 가는 획 49~50  /  b d p q 둥근 획 58~66  /  c 아래 45 · e 아래 47", fontsize=12, loc="left")
    row(axs[1], "dobop pocpa cede", hl="oce")
    axs[1].set_title("문장 속 회색도(획 굵기 고르기)", fontsize=12, loc="left")
    lib.save(OUT + "65-round-contrast.png")


# 66 d 동그라미 높이
def fig66():
    fig, ax = plt.subplots(figsize=(14, 3.6), dpi=110)
    row(ax, "bdpqo", lines=[(512, RED), (501, ORG), (488, BLUE), (500, "#bbb")], hl="d")
    ax.set_title("동그라미 위: d 488 · b p q 501 · o 512 (회색 = x높이 500)", fontsize=12, loc="left")
    lib.save(OUT + "66-d-bowl.png")


# 67 숫자 높이
def fig67():
    fig, ax = plt.subplots(figsize=(14, 3.2), dpi=110)
    row(ax, "1457 1023689", lines=[(655, RED), (644, BLUE), (0, GRAY)], hl="1")
    ax.set_title("평평한 숫자 위 644(4 5 7) · 둥근 숫자 655(넘침) · 1 은 평평한데 655", fontsize=12, loc="left")
    lib.save(OUT + "67-figure-height.png")


# 68 부리 세리프
def fig68():
    items = [("E", 575, 600, 70, "E 위 1.4°"), ("E", 585, 80, 70, "E 아래 1.4°"), ("L", 597, 80, 70, "L 1.8°"),
             ("T", 40, 600, 70, "T 1.4°"), ("Z", 66, 600, 70, "Z 위 1.8°"), ("Z", 585, 80, 70, "Z 아래 2.1°")]
    fig, axs = plt.subplots(1, 6, figsize=(18, 3.6), dpi=110)
    for ax, (c, cx, cy, r, t) in zip(axs.flat, items):
        zoom(ax, G[c], cx, cy, r, t)
    lib.save(OUT + "68-beak-serifs.png")


# 69 전체 견본(큰 크기)
def fig69():
    fig, axs = plt.subplots(4, 1, figsize=(16, 9.5), dpi=110)
    for ax, t in zip(axs, ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "abcdefghijklm", "nopqrstuvwxyz 0123456789"]):
        row(ax, t)
    lib.save(OUT + "69-specimen.png")


FIGS = {n: globals()[f"fig{n}"] for n in range(60, 70)}
for n in ([int(a) for a in sys.argv[1:]] or list(FIGS)):
    FIGS[n](); print("그림", n)
