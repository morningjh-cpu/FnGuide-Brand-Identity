"""v1.33(3차 크리틱 전체 반영) 전후 미리보기 → out/font-update/v1.33-preview/critique3.html (그림 c3-*.png)
실행: py scripts/font_critique/v133_preview.py"""
import os, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, lib
from matplotlib.path import Path
from matplotlib.patches import PathPatch

OUT = lib.ROOT + "out/font-update/v1.33-preview/"
os.makedirs(OUT, exist_ok=True)
RED, BLUE, INK, GRAY = "#B9023D", "#2a7de1", "#17181a", "#9aa0a6"
plt.rcParams["font.family"] = ["Malgun Gothic"]; plt.rcParams["axes.unicode_minus"] = False
OLD, NEW = lib.load("FnGuide v1.32"), lib.load("FnGuide v1.33")
CM = {chr(u): g for u, g in NEW.tt.getBestCmap().items()}


def gpath(f, g, dx=0):
    V, C = [], []
    for op, pts in f.rec(g):
        P = [(x + dx, y) for x, y in pts]
        V += P if P else [(0, 0)]
        C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3, "Q": [Path.CURVE3] * 2, "Z": [Path.CLOSEPOLY]}[op]
    return Path(V, C)


def nodes(ax, f, g):
    cur = None
    for op, pts in f.rec(g):
        if op == "C":
            ax.plot([cur[0], pts[0][0]], [cur[1], pts[0][1]], color=BLUE, lw=0.7)
            ax.plot([pts[1][0], pts[2][0]], [pts[1][1], pts[2][1]], color=BLUE, lw=0.7)
        if pts:
            ax.plot(pts[-1][0], pts[-1][1], "s", ms=3.5, color=RED, mec="white", mew=0.4); cur = pts[-1]


def zoompair(items, name, r_default=60):
    """items: (글자, cx, cy, r, 제목, 기준선들) — 위 v1.32, 아래 v1.33"""
    n = len(items)
    fig, axs = plt.subplots(2, n, figsize=(3.3 * n, 6.8), dpi=100, squeeze=False)
    for j, (ch, cx, cy, r, t, lines) in enumerate(items):
        g = CM.get(ch, ch)
        for i, (f, lab) in enumerate(((OLD, "v1.32"), (NEW, "v1.33"))):
            ax = axs[i, j]
            ax.add_patch(PathPatch(gpath(f, g), fc=INK, ec="none", alpha=0.82)); nodes(ax, f, g)
            for y in lines: ax.axhline(y, color=BLUE, lw=0.9)
            ax.set_xlim(cx - r, cx + r); ax.set_ylim(cy - r, cy + r); ax.set_aspect("equal")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values(): s.set_color("#ddd")
            ax.set_title(f"{t} · {lab}" if i == 0 else lab, fontsize=10, loc="left", color=INK if i else GRAY)
    lib.save(OUT + name)


def textpair(lines, name, guides=(), hl=""):
    fig, axs = plt.subplots(len(lines) * 2, 1, figsize=(16, 1.55 * 2 * len(lines)), dpi=100)
    k = 0
    for t in lines:
        for f, lab in ((OLD, "v1.32"), (NEW, "v1.33")):
            ax = axs[k]; k += 1; x = 0
            for ch in t:
                if ch == " ": x += 250; continue
                g = CM[ch]; ax.add_patch(PathPatch(gpath(f, g, x), fc=RED if ch in hl and f is NEW else INK, ec="none"))
                x += f.tt["hmtx"][g][0]
            for y in guides: ax.plot([-20, x], [y, y], color=BLUE, lw=0.7)
            ax.set_xlim(-60, max(x, 6000) + 20); ax.set_ylim(-240, 760); ax.set_aspect("equal"); ax.axis("off")
            ax.text(-60, 780, lab, fontsize=9, color=GRAY)
    lib.save(OUT + name)


# ❶ 소문자 깃발
zoompair([("n", 40, 440, 110, "n (기준)", [500]), ("m", 40, 440, 110, "m", [500]), ("r", 40, 440, 110, "r", [500]),
          ("p", 40, 440, 110, "p", [500]), ("q", 520, 440, 110, "q", [500]), ("i", 40, 440, 110, "i", [500]),
          ("u", 40, 440, 110, "u", [500]), ("k", 40, 640, 110, "k", [697])], "c3-1-flags-lower.png")
textpair(["minimum nirvana", "quip jumping kirk"], "c3-1-flags-text.png", guides=(500, 0), hl="mrpqiujk")
# ❷ 높이선
zoompair([("M", 820, 700, 16, "M 위", [700]), ("A", 300, 700, 16, "A 위", [700]), ("V", 735, 700, 16, "V 오른쪽 위", [700]),
          ("D", 200, 0, 16, "D 바닥", [0]), ("K", 600, 0, 16, "K 바닥", [0]), ("Z", 300, 0, 16, "Z 바닥", [0]),
          ("w", 100, 500, 16, "w 위", [500]), ("j", 167, -210, 16, "j 아래", [-210])], "c3-2-heights.png")
# ❸ 윤곽 정리
zoompair([("V", 144, 619, 45, "V 깃발 끝", []), ("w", 55, 440, 75, "w 세리프", []), ("e", 344, 57, 25, "e 아래 끝", []),
          ("a", 252, 505, 14, "a 위", []), ("r", 418, 494, 14, "r 끝", [])], "c3-3-cleanup.png")
# ❹ 대문자 깃발
zoompair([("H", 90, 640, 100, "H (기준)", [700]), ("I", 90, 640, 100, "I", [700]), ("K", 90, 640, 100, "K", [700])], "c3-4-flags-upper.png")
textpair(["HIKE INK KIWI", "HAMLINE KILN"], "c3-4-flags-text.png", guides=(700, 0), hl="IK")
# ❺ 미세 꺾임
zoompair([("H", 118, 638, 22, "H 깃발 이음", []), ("A", 230, 660, 45, "A 깃발", []), ("h", 30, 627, 40, "h 깃발 아래", [])], "c3-5-kinks.png")
# ❻ 가는 획 · ❼ 넘침
textpair(["bodpq coco", "case sage gas"], "c3-6-7-round.png", guides=(512, 500, 0), hl="oceasg")
zoompair([("o", 283, 480, 60, "o 위", [512]), ("c", 258, 480, 60, "c 위", [512]), ("e", 260, 480, 60, "e 위", [512]),
          ("s", 224, 480, 60, "s 위", [512]), ("a", 252, 480, 60, "a 위", [512]), ("S", 310, 690, 60, "S 위", [711])], "c3-6-7-zoom.png")
# ❽ 숫자 1
textpair(["1457 1023689 2026"], "c3-8-figure.png", guides=(644, 655, 0), hl="1")
# ❾ 부리 세리프
zoompair([("E", 560, 560, 60, "E 위", []), ("L", 575, 110, 60, "L", []), ("T", 60, 560, 60, "T 왼쪽", []),
          ("Z", 80, 560, 60, "Z 위", []), ("Z", 565, 110, 60, "Z 아래", [])], "c3-9-beaks.png")
# 전체 견본
textpair(["ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz", "0123456789 FnGuide DataGuide WiseReport"], "c3-specimen.png")

SEC = [("❶ 소문자 깃발 — n 치수로 통일(꼭대기 500·끝까지 93·끝 두께 33), k 는 h 와 같게", ["c3-1-flags-lower.png", "c3-1-flags-text.png"]),
       ("❷ 높이선·기준선 — 평평한 면을 700 / 0 / 500 / −210 에", ["c3-2-heights.png"]),
       ("❸ 윤곽 정리 — V 깃발 끝 꺾임, w 세리프 곡선, e·a·r 겹친 점·계단", ["c3-3-cleanup.png"]),
       ("❹ 대문자 깃발 — I·K 를 H 와 같은 수평 윗면으로(좌우 여백 그대로, 폭 I 347→344 · K 713→706)", ["c3-4-flags-upper.png", "c3-4-flags-text.png"]),
       ("❺ 미세 꺾임 — 깃발 이음 손잡이를 한 줄로", ["c3-5-kinks.png"]),
       ("❻ 가는 획 56 · ❼ 둥근 넘침(S 711, s·a 512 근처, g 평평한 위 500)", ["c3-6-7-zoom.png", "c3-6-7-round.png"]),
       ("❽ 숫자 1 높이 655 → 644", ["c3-8-figure.png"]),
       ("❾ 부리 세리프 기울기 1.42° 통일, 안쪽 턱 정리", ["c3-9-beaks.png"]),
       ("전체 견본", ["c3-specimen.png"])]
html = ['<!doctype html><meta charset="utf-8"><title>v1.33 전후 비교</title>',
        '<style>body{font-family:Pretendard,"Malgun Gothic",sans-serif;margin:32px auto;max-width:1400px;padding:0 16px;color:#222;background:#fff}'
        'h2{font-size:19px;margin:40px 0 10px;border-top:1px solid #ddd;padding-top:16px}img{width:100%;border:1px solid #eee;margin:6px 0}'
        '.note{background:#f5f6f7;border-radius:8px;padding:12px 16px;font-size:14px;color:#444}</style>',
        '<h1>전용서체 v1.33 — 3차 크리틱 전체 반영 전후 비교</h1>',
        '<p class="note">확대 그림은 위가 v1.32(지금 공개본), 아래가 v1.33. 빨간 네모 = 점, 파란 선 = 곡선 손잡이·기준선. 문장 견본은 v1.33 에서 바뀐 글자를 빨간색으로 표시.<br>'
        '확인: 바뀐 글자 64자(예상 외 0), 글자 사이 간격 규칙 변화 0, 글자 쌍 12,544쌍 닿음 0. 아직 공개 전(zip·사이트·로고는 v1.32 그대로).</p>']
for t, imgs in SEC:
    html.append(f"<h2>{t}</h2>" + "".join(f'<img src="{i}">' for i in imgs))
open(OUT + "critique3.html", "w", encoding="utf-8").write("\n".join(html))
print(OUT + "critique3.html")
