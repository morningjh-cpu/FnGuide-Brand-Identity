"""2차 크리틱(v1.31) 그림 50~54. 실행: py scripts/font_critique/crit2_figs.py"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, lib
from PIL import Image, ImageDraw, ImageFont
from matplotlib.backends.backend_agg import FigureCanvasAgg

OUT = lib.ROOT + "out/font-critique/img/"
RED, BLUE, ORG, GRAY = "#B9023D", "#2a7de1", "#e08a00", "#80868d"
plt.rcParams["font.family"] = ["Malgun Gothic"]
new, old = lib.load("FnGuide v1.31"), lib.load("FnGuide v1.200")


def capk(f):
    from measure_core import bbox
    return 0.7 / (bbox(f, "H")[3] / f.upm)   # 대문자 높이를 0.7em 으로 맞추는 배율


# 그림 50 — 1차 수정 필요 ①~④ 전후
def fig50():
    rows = [("HOCGHO", [(0.700, BLUE), (0.711, RED)], "① C·G 윗부분"),
            ("nvnwnxnyn", [(0.500, BLUE)], "② v·w·x·y 높이"),
            ("nonocnen", [(0.500, BLUE), (0.512, RED)], "③ o·c·e 위 넘침"),
            ("soft lift", [], "④ f 다음 간격"),
            ("Il1 l1I", [], "⑥ I·l·1 구분")]
    fig, axs = plt.subplots(len(rows), 2, figsize=(16, 2.0 * len(rows)), dpi=110)
    for r, (t, lines, lab) in enumerate(rows):
        for c, (f, name) in enumerate(((old, "v1.200"), (new, "v1.31"))):
            ax = axs[r, c]; w = f.draw(ax, t, 0, 0, 1.0, color="#17181a" if c else "#6a6f75")
            for y, col in lines: ax.plot([-0.05, w + 0.05], [y, y], color=col, lw=0.9)
            ax.set_xlim(-0.1, 6.0); ax.set_ylim(-0.25, 0.82); ax.set_aspect("equal"); ax.axis("off")
            ax.set_title(f"{lab} · {name}", loc="left", fontsize=12, color=RED if c else GRAY)
    lib.save(OUT + "50-v131-fixes.png")


# 그림 51 — 대각선 쌍 간격 (⑧): 같은 대문자 높이로
def fig51():
    t = "HLYH HLVH HLTH HAVH HTAH HToH"
    names = ["FnGuide v1.31", "Helvetica Neue Medium", "Rotis Semi Sans Bold", "Inter Medium"]
    fig, axs = plt.subplots(len(names), 1, figsize=(16, 1.6 * len(names)), dpi=110)
    for ax, n in zip(axs, names):
        f = lib.load(n); w = f.draw(ax, t, 0, 0, capk(f), color=RED if "FnGuide" in n else "#17181a")
        ax.set_xlim(-0.05, 11.5); ax.set_ylim(-0.1, 0.78); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(n, loc="left", fontsize=12, color=RED if "FnGuide" in n else GRAY)
    lib.save(OUT + "51-diagonal-pairs.png")


def raster(f, text, px, scale=1.0):
    W = int(px * 24); Hh = int(px * 1.6)
    fig = plt.figure(figsize=(W / 100, Hh / 100), dpi=100); ax = fig.add_axes([0, 0, 1, 1])
    f.draw(ax, text, 0.1 * px, 0.4 * px, px * scale)
    ax.set_xlim(0, W); ax.set_ylim(0, Hh); ax.axis("off")
    cv = FigureCanvasAgg(fig); cv.draw(); a = np.asarray(cv.buffer_rgba())[:, :, :3].copy(); plt.close(fig)
    return a


# 그림 52 — 작은 크기 (⑦): 실제 픽셀 3배 확대
def fig52():
    rows = []; text = "FnGuide WiseReport 2026 Q3 office scene"
    for n in ["FnGuide v1.31", "Rotis Semi Sans Bold", "Helvetica Neue Medium"]:
        f = lib.load(n)
        for px in (12, 14, 16):
            a = raster(f, text, px, capk(f))
            rows.append((f"{n}  {px}px", Image.fromarray(a).resize((a.shape[1] * 3, a.shape[0] * 3), Image.NEAREST)))
    W = max(i.width for _, i in rows); sheet = Image.new("RGB", (W + 10, sum(i.height + 24 for _, i in rows)), "white")
    d = ImageDraw.Draw(sheet); fnt = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 16); y = 0
    for label, img in rows:
        d.text((6, y + 2), label, fill=(185, 2, 61) if "FnGuide" in label else (90, 90, 90), font=fnt)
        sheet.paste(img, (0, y + 22)); y += img.height + 24
    sheet.save(OUT + "52-small-v131.png")


# 그림 53 — 한글과 섞어 쓰기: 같은 글자 크기, 한글 서체 굵기만 바꿈
def fig53():
    U = lib.UF
    pairs = [("Pretendard Regular", U + "Pretendard-Regular.ttf"), ("Pretendard SemiBold", U + "Pretendard-SemiBold.ttf"),
             ("Pretendard Bold", U + "Pretendard-Bold.ttf"), ("맑은 고딕 Bold", lib.SF + "malgunbd.ttf")]
    runs = [("FnGuide", "L"), (" 리서치센터 ", "K"), ("WiseReport", "L"), (" 2026년 3분기 ", "K"), ("Q3", "L")]
    fig, axs = plt.subplots(len(pairs), 1, figsize=(16, 1.5 * len(pairs)), dpi=110)
    for ax, (kn, kp) in zip(axs, pairs):
        k = lib.F(kp); x = 0
        for t, kind in runs:
            x += (new if kind == "L" else k).draw(ax, t, x, 0, 1.0, color=RED if kind == "L" else "#17181a")
        ax.plot([0, x], [0.7, 0.7], color=BLUE, lw=0.6)
        ax.set_xlim(-0.05, 17.5); ax.set_ylim(-0.25, 0.95); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"전용서체 + {kn}", loc="left", fontsize=12, color=GRAY)
    lib.save(OUT + "53-korean-mix.png")


# 그림 54 — 표의 숫자: 기본(비례) vs 고정폭(tnum)
def fig54():
    nums = ["1,111.11", "2,048.50", "10,980.07", "−314.16"]
    fig, axs = plt.subplots(1, 2, figsize=(14, 3.6), dpi=110)
    for ax, (feats, lab) in zip(axs, (({"kern": True}, "기본 (비례 숫자)"), ({"kern": True, "tnum": True}, "고정폭 숫자 (tnum)"))):
        for i, s in enumerate(nums):
            _, w = new.shape(s, feats); w = w / new.upm
            new.draw(ax, s, 5.2 - w, -i * 0.95, 1.0, features=feats)   # 오른쪽 맞춤
        ax.plot([5.2, 5.2], [-3.2, 0.8], color=BLUE, lw=0.6)
        ax.set_xlim(0, 5.5); ax.set_ylim(-3.2, 0.9); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(lab, loc="left", fontsize=12, color=RED if "tnum" in lab else GRAY)
    lib.save(OUT + "54-figures-table.png")


# 그림 55 — 수학 기호 높이 (사용자 의견): 지금 / 올린 안 / 해외 서체
SYM = {"plus", "minus", "equal", "less", "greater", "multiply", "plusminus", "asciitilde"}


def draw_shift(f, ax, text, size, dy, color="#17181a", hl=True):
    """기호 글리프만 dy(서체 단위)만큼 올려 그림 — 시안용, 서체 파일은 그대로"""
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path
    gl, adv = f.shape(text); s = size / f.upm
    for g, gx, gy in gl:
        V, C = [], []
        up = dy if g in SYM else 0
        for op, pts in f.rec(g):
            V += [((gx + px) * s, (gy + py + up) * s) for px, py in pts] if pts else [(0, 0)]
            C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3,
                  "Q": [Path.CURVE3] * 2, "Z": [Path.CLOSEPOLY]}[op]
        if V: ax.add_patch(PathPatch(Path(V, C), fc=RED if (g in SYM and hl) else color, ec="none"))
    return adv * s


def fig55():
    t = "+1.25% −0.48% A+B x=3 <10> 2×3"
    rows = [("FnGuide v1.31 · 지금 (가운데 0.35)", new, 0), ("안 A · 30 올림 (가운데 0.39, Inter·DIN 수준)", new, 30),
            ("안 B · 55 올림 (가운데 0.43, Avenir 수준)", new, 55),
            ("Inter Medium (0.39)", lib.load("Inter Medium"), None), ("Helvetica Neue Medium (0.35)", lib.load("Helvetica Neue Medium"), None)]
    fig, axs = plt.subplots(len(rows), 1, figsize=(16, 1.55 * len(rows)), dpi=110)
    for ax, (lab, f, dy) in zip(axs, rows):
        k = capk(f)
        w = draw_shift(f, ax, t, k, dy or 0) if dy is not None else draw_shift(f, ax, t, k, 0, hl=False)
        ax.plot([0, w], [0.35, 0.35], color=BLUE, lw=0.6)          # 대문자 높이의 절반
        ax.set_xlim(-0.05, w + 0.1); ax.set_ylim(-0.12, 0.78); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(lab, loc="left", fontsize=12, color=RED if "FnGuide" in lab or "안" in lab else GRAY)
    lib.save(OUT + "55-math-symbols.png")


if __name__ == "__main__":
    import sys
    todo = sys.argv[1:] or ["50", "51", "52", "53", "54", "55"]
    for n in todo: globals()["fig" + n]()
