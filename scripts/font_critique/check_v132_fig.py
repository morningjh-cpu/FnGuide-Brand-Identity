"""v1.32 실제 서체 파일(OTF·TTF)로 그린 확인 그림 → out/font-update/v1.32/v1.32-check.png"""
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, lib
f = lib.F(lib.ROOT + "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf")
g = lib.F(lib.ROOT + "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.ttf")
L = ["+1.25% −0.48% ±0.5 A+B x=3 <10> 2×3", "▲1.25% ▼0.48% 25°C 3‰ ₩25,000",
     "2026-11-02 — Q3… a·b A/B help@fnguide.com", "FLY LTV AVATAR WAY PATRY YAW", "FnGuide™ DataGuide® WiseReport"]
W = max(f.shape(t)[1] for t in L) / 1000 + 0.2
fig, axs = plt.subplots(len(L) * 2, 1, figsize=(1.1 * W, 1.1 * 2 * len(L)), dpi=100)
for i, t in enumerate(L):
    for j, (ff, lab) in enumerate(((f, "OTF"), (g, "TTF"))):
        ax = axs[i * 2 + j]; ff.draw(ax, t, 0, 0, 1.0)
        ax.set_xlim(-0.05, W); ax.set_ylim(-0.25, 0.8); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(f"v1.32 {lab}", loc="left", fontsize=9, color="#80868d")
lib.save(lib.ROOT + "out/font-update/v1.32/v1.32-check.png")
