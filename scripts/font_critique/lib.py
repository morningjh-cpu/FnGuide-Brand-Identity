"""크리틱용 공통 도구: 아무 서체나 하르프버즈로 조판해 matplotlib 으로 그림"""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from matplotlib.path import Path
from matplotlib.patches import PathPatch

import os as _os
ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..")).replace("\\", "/") + "/"
_HOME = _os.path.expanduser("~").replace("\\", "/")
UF = _HOME + "/AppData/Local/Microsoft/Windows/Fonts/"
SF = "C:/Windows/Fonts/"
FONTS = {
    "FnGuide v1.31": ROOT + "out/font-update/v1.31/fonts/FnGuideLogotype-Regular.otf",
    "FnGuide v1.200": ROOT + "out/font-update/v1.200/fonts/FnGuideLogotype-Regular.otf",
    "FnGuide (logo)": ROOT + "out/font-update/logo-font/FnGuideLogotype-Regular.otf",
    "Helvetica Neue Medium": UF + "HelveticaNeue-Medium.otf",
    "Avenir Next Demi": UF + "AvenirNextLTPro-Demi.otf",
    "Futura Medium": SF + "Futura Medium.otf",
    "DIN Medium": SF + "DIN Medium.otf",
    "Inter Medium": UF + "Inter_18pt-Medium.ttf",
    "Rotis Semi Sans Bold": UF + "RotisSemiSansStd-Bold.otf",
    "Candara Bold": SF + "Candarab.ttf",
}

class F:
    def __init__(self, path):
        self.file = path
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.upm = self.tt["head"].unitsPerEm
        blob = hb.Blob.from_file_path(path)
        self.hbf = hb.Font(hb.Face(blob))
        self.order = self.tt.getGlyphOrder()
        self._cache = {}

    def shape(self, text, features=None):
        buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
        hb.shape(self.hbf, buf, features or {"kern": True, "liga": True})
        out, x = [], 0
        for i, p in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((self.order[i.codepoint], x + p.x_offset, p.y_offset))
            x += p.x_advance
        return out, x

    def rec(self, g):
        """글리프 → [(op, [(x,y)...])] (2차 곡선은 하나씩 풀어 둠)"""
        if g not in self._cache:
            pen = _Pen(self.gs); self.gs[g].draw(pen); self._cache[g] = pen.ops
        return self._cache[g]

    def path(self, text, x0=0, y0=0, size=1.0, features=None):
        """텍스트 → matplotlib Path (단위: em*size)"""
        glyphs, adv = self.shape(text, features)
        s = size / self.upm
        V, C = [], []
        for g, gx, gy in glyphs:
            for op, pts in self.rec(g):
                P = [(x0 + (gx + px) * s, y0 + (gy + py) * s) for px, py in pts]
                V += P if P else [(0, 0)]
                C += {"M": [Path.MOVETO], "L": [Path.LINETO], "C": [Path.CURVE4] * 3,
                      "Q": [Path.CURVE3] * 2, "Z": [Path.CLOSEPOLY]}[op]
        return (Path(V, C) if V else None), adv * s

    def draw(self, ax, text, x0=0, y0=0, size=1.0, color="#111", features=None):
        p, w = self.path(text, x0, y0, size, features)
        if p is not None:
            ax.add_patch(PathPatch(p, fc=color, ec="none", lw=0))
        return w

class _Pen(BasePen):
    def __init__(self, gs):
        super().__init__(gs); self.ops = []
    def _moveTo(self, p): self.ops.append(("M", [p]))
    def _lineTo(self, p): self.ops.append(("L", [p]))
    def _curveToOne(self, a, b, c): self.ops.append(("C", [a, b, c]))
    def _qCurveToOne(self, a, b): self.ops.append(("Q", [a, b]))
    def _closePath(self): self.ops.append(("Z", []))
    _endPath = _closePath

def load(name):
    return F(FONTS[name])


def save(path, tries=20):
    """그림 저장. 미리보기 창이 파일을 잠깐 잡고 있으면 실패하므로 잠시 기다렸다 다시 시도한다."""
    import time
    import matplotlib.pyplot as plt
    for i in range(tries):
        try:
            plt.savefig(path, bbox_inches="tight"); plt.close(); return
        except OSError:
            if i == tries - 1: raise
            time.sleep(0.5)
