"""폰트 업데이트 화면의 v1.32 그림: 실제 v1.31·v1.32 서체 파일로 위(수정 전)·아래(수정 후)
실행: py scripts/font_critique/site_v132_figs.py → out/font-critique/img/update/v132-*.png
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import lib

OUT = lib.ROOT + "out/font-critique/img/update/"
plt.rcParams["font.family"] = ["Malgun Gothic"]
A = lib.F(lib.ROOT + "out/font-update/v1.31/fonts/FnGuideLogotype-Regular.otf")
B = lib.F(lib.ROOT + "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf")
PRE = lib.F(lib.UF + "Pretendard-Medium.ttf")
GRAY, INK, BLUE = "#80868d", "#17181a", "#2a7de1"


def mixed(ax, f, text):
    """서체에 없는 글자는 Pretendard Medium(회색)으로 — 사용 규칙과 같은 모습"""
    cm = f.tt.getBestCmap(); x = 0; run = ""
    for ch in text + "\0":
        if ch != "\0" and (ord(ch) in cm or ch == " "):
            run += ch; continue
        if run: x += f.draw(ax, run, x, 0, 1.0, color=INK); run = ""
        if ch != "\0": x += PRE.draw(ax, ch, x, 0, 1.0, color="#9aa0a6")
    return x


def pair(name, text, line=None):
    W = max(B.shape(text)[1], A.shape(text)[1]) / 1000 + 0.3
    fig, axs = plt.subplots(2, 1, figsize=(1.0 * W, 2.3), dpi=110)
    for ax, (f, lab) in zip(axs, ((A, "v1.31"), (B, "v1.32"))):
        w = mixed(ax, f, text)
        if line is not None: ax.plot([0, w], [line, line], color=BLUE, lw=0.6)
        ax.set_xlim(-0.05, W); ax.set_ylim(-0.25, 0.8); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(lab, loc="left", fontsize=10, color=GRAY)
    lib.save(OUT + name)


if __name__ == "__main__":
    pair("v132-symbols.png", "+1.25% −0.48% A+B x=3 <10> 2×3 a·b 2026-11-02 A/B @FnGuide", 0.35)
    pair("v132-new.png", "▲1.25% ▼0.48% 25°C 3‰ Q3… 2026 — FnGuide™ DataGuide®")
    pair("v132-diagonal.png", "FLY LTV AVATAR WAY PATRY YAW")
    pair("v132-won.png", "₩1,000 ₩25,000")
