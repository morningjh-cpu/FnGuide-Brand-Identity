"""한글 대용 서체 미리보기: 전용서체 + Source Han Serif(= Noto Serif KR, 같은 디자인) 굵기별, 비교용 Pretendard Medium
실행: py scripts/font_critique/korean_pair_preview.py → out/font-critique/korean-pair/
Noto Serif KR 은 가변 서체라 굵기별 고정 파일을 임시 폴더에 만들어 쓴다(다시 만들 수 있음).
"""
import os, json, tempfile
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
import lib
from measure_core import bbox, hscan

OUT = lib.ROOT + "out/font-critique/korean-pair/"
os.makedirs(OUT, exist_ok=True)
RED, BLUE, GRAY, INK = "#B9023D", "#2a7de1", "#80868d", "#17181a"
plt.rcParams["font.family"] = ["Malgun Gothic"]
VF = "C:/Windows/Fonts/NotoSerifKR-VF.ttf"
fn = lib.load("FnGuide v1.31")


def instances():
    tmp = tempfile.mkdtemp(prefix="serifkr-")
    out = {}
    for w, name in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")):
        t = TTFont(VF); instancer.instantiateVariableFont(t, {"wght": w}, inplace=True)
        p = f"{tmp}/NotoSerifKR-{w}.ttf"; t.save(p); out[f"Source Han Serif {name}"] = p
    out["(비교) Pretendard Medium"] = lib.UF + "Pretendard-Medium.ttf"
    return out


def stem_v(f, ch, frac=0.5, last=True):
    b = bbox(f, ch); r = hscan(f, ch, b[1] + (b[3] - b[1]) * frac)
    seg = r[-1] if last else r[0]; return (seg[1] - seg[0]) / f.upm


def measure(fonts):
    fstem = stem_v(fn, "H", 0.3, last=False)
    res = {"FnGuide": dict(cap=round(bbox(fn, "H")[3] / fn.upm, 3), stem=round(fstem, 4))}
    for n, p in fonts.items():
        k = lib.F(p)
        res[n] = dict(cap=round(bbox(k, "H")[3] / k.upm, 3),
                      hangul_h=round((max(bbox(k, "한")[3], bbox(k, "가")[3]) - min(bbox(k, "한")[1], bbox(k, "가")[1])) / k.upm, 3),
                      hangul_stem=round(stem_v(k, "이"), 4))
        res[n]["fn_stem_ratio"] = round(fstem / res[n]["hangul_stem"], 2)   # 전용서체 기둥 ÷ 한글 세로획
    return res


def fig(fonts, runs, name, rowh=1.5):
    k0 = {n: lib.F(p) for n, p in fonts.items()}
    W = 0
    for n, k in k0.items():
        W = max(W, sum((fn if kind == "L" else k).shape(t)[1] / (fn if kind == "L" else k).upm for t, kind in runs))
    fig, axs = plt.subplots(len(fonts), 1, figsize=(1.05 * W, rowh * len(fonts)), dpi=110)
    for ax, (n, k) in zip(axs, k0.items()):
        x = 0
        for t, kind in runs:
            x += (fn if kind == "L" else k).draw(ax, t, x, 0, 1.0, color=RED if kind == "L" else INK)
        ax.plot([0, x], [0.7, 0.7], color=BLUE, lw=0.5)
        ax.set_xlim(-0.05, W + 0.1); ax.set_ylim(-0.28, 0.98); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"전용서체 + {n}", loc="left", fontsize=12, color=GRAY if "비교" in n else INK)
    lib.save(OUT + name)


if __name__ == "__main__":
    fonts = instances()
    m = measure(fonts)
    json.dump(m, open(OUT + "metrics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(m, ensure_ascii=False, indent=1))
    fig(fonts, [("FnGuide", "L"), (" 리서치센터 ", "K"), ("WiseReport", "L"), (" 2026년 3분기 ", "K"), ("Q3", "L")], "k1-title.png")
    fig(fonts, [("DataGuide", "L"), (" 기업 분석 ", "K"), ("+1.25%", "L"), (" 상승 ", "K"), ("▲", "K"), (" 매출 ", "K"), ("₩25,000", "L")], "k2-numbers.png")
