"""전용서체 v1.3 만들기.
v1.200 서체(out/font-update/v1.200/fonts)의 글자·여백·커닝을 그대로 두고, 개선안 보고서의 "수정 후"만 바꾼다.
  ① C·G 윗부분 711  ② v·w·x·y 500  ③ o·c·e 위 넘침 512  ④ ft·fj 이어 쓰기, ty·rv 보정 0
  ⑤ Windows 위쪽 높이 870, Regular 표시  ⑥ 1 받침·l 꼬리  ⑨ 금융 기호 5개 + 고정폭 숫자 선택 기능(tnum)
글자 모양은 scripts/font_critique/after.py·symbols.py 에서 가져온다(보고서 그림과 같은 윤곽).
실행: py scripts/build_v13.py  [--control : 아무것도 안 바꾸고 다시 만들어 v1.200 과 같은지 확인]
      py scripts/build_v13.py --v131 : v1.3 + 대문자–숫자 커닝(out/font-update/work/kern_uc_digit.json, font_critique/kern_ucdigit.py 가 계산)
      py scripts/build_v13.py --v132 : v1.31 + 2차 크리틱 반영(plan/phase-2/06)
        기호 높이(font_critique/crit2_preview.SHIFT) · ₩ 세리프 제거 · 새 기호 8개(crit2_symbols_new) ·
        대문자 대각선 18쌍 Avenir Next Demi 비율(대문자 평균 간격 기준, out/font-update/kern-diag-compare/compare-mean.json) ·
        포함 금지(fsType 2) · 사용 조건 문구 · woff2
        (대각선 18쌍은 처음 Inter 비율로 냈다가 너무 촘촘하다는 검토 의견으로 Avenir 로 바꿈. 별도 버전을 두지 않고 v1.32 에 포함 — plan/phase-2/07)
      py scripts/build_v13.py --v133 : v1.32 + 세로 줄기 축선 맞춤(AXIS_FIX, 찾기는 font_critique/find_axis_misalign.py)
"""
import os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "font_critique"))
import pathops
from fontTools.misc.roundTools import otRound
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "out/font-update/v1.200/fonts/FnGuideLogotype-Regular.otf")
FEA = os.path.join(ROOT, "out/font-update/work/kerning.fea")
CONTROL = "--control" in sys.argv
V133 = "--v133" in sys.argv
V132 = "--v132" in sys.argv or V133
V131 = "--v131" in sys.argv or V132
VERSION = "1.200" if CONTROL else ("1.33" if V133 else "1.32" if V132 else ("1.31" if V131 else "1.3"))
OUTDIR = os.path.join(ROOT, "out/font-update", "control" if CONTROL else "v" + VERSION, "fonts")
FAMILY, STYLE, PS = "FnGuide Logotype", "Regular", "FnGuideLogotype-Regular"

src = TTFont(SRC)
gs = src.getGlyphSet(); hm = src["hmtx"]
order = list(src.getGlyphOrder())
cmap = dict(src.getBestCmap())

def rec_src(g):
    r = RecordingPen(); gs[g].draw(r); return r.value

# ---- 글자 윤곽: {이름: (윤곽(RecordingPen 형식), 폭)} ----
OP = {"M": "moveTo", "L": "lineTo", "C": "curveTo", "Q": "qCurveTo", "Z": "closePath"}
def conv(ops, dx=0):
    """보고서 그림용 형식 [(M/L/C/Z, 점들)] → RecordingPen 형식"""
    return [(OP[o], tuple((x + dx, y) for x, y in pts)) for o, pts in ops]

glyphs = {g: (rec_src(g), hm[g][0]) for g in order}
changed = set()
AXIS_FIX = {}
if not CONTROL:
    import after, symbols
    G = lambda ch: cmap[ord(ch)]
    for g, ops in after.OV.items():                              # ①②③⑥
        glyphs[g] = (conv(ops), after.ADV.get(g, hm[g][0])); changed.add(g)
    new = {"f_t": (after.F_T, after.F_T_ADV), "f_j": (after.F_J, after.F_J_ADV)}   # ④
    names = {"₩": ("uni20A9", 0x20A9), "−": ("minus", 0x2212), "±": ("plusminus", 0x00B1),
             "×": ("multiply", 0x00D7), "·": ("periodcentered", 0x00B7)}      # ⑨ 금융 기호
    for ch, (nm, u) in names.items():
        new[nm] = symbols.NEW[ch]; cmap[u] = nm
    # ⑨ 고정폭 숫자(선택 기능): 0~9 와 + − ± 를 600 칸 가운데에
    TAB = symbols.TAB
    for nm in ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]:
        ops = after.OV.get(nm) or None
        base = conv(ops) if ops else rec_src(nm)
        a = after.ADV.get(nm, hm[nm][0])
        glyphs[nm + ".tf"] = ([(o, tuple((x + (TAB - a) / 2, y) for x, y in p)) for o, p in base], TAB)
    for nm, src_ops, a in [("plus", rec_src("plus"), hm["plus"][0]),
                           ("minus", conv(symbols.MINUS), symbols.PLUS_ADV),
                           ("plusminus", conv(symbols.PLUSMINUS), symbols.PLUS_ADV)]:
        glyphs[nm + ".tf"] = ([(o, tuple((x + (TAB - a) / 2, y) for x, y in p)) for o, p in src_ops], TAB)
    for nm, (ops, a) in new.items():
        glyphs[nm] = (conv(ops), round(a))
    if V132:
        import crit2_preview as pv, crit2_symbols_new as sn
        # ₩ 왼쪽 위 세리프 제거 (v1.31 윤곽에서 세리프 점만 바꾼 것)
        glyphs["uni20A9"] = (conv(pv.REPLACE["uni20A9"]), glyphs["uni20A9"][1]); changed.add("uni20A9")
        # 기호 높이: 수학 기호 B안·가운뎃점·하이픈·en 대시·/ \·@ (고정폭 + − ± 포함)
        for g, dy in pv.SHIFT.items():
            ops, a = glyphs[g]
            glyphs[g] = ([(o, tuple((x, y + dy) for x, y in pts)) for o, pts in ops], a); changed.add(g)
        # 새 기호 8개
        NEWNAME = {"▲": ("uni25B2", 0x25B2), "▼": ("uni25BC", 0x25BC), "°": ("degree", 0x00B0),
                   "‰": ("perthousand", 0x2030), "…": ("ellipsis", 0x2026), "—": ("emdash", 0x2014),
                   "™": ("trademark", 0x2122), "®": ("registered", 0x00AE)}
        for ch, (a, path) in sn.build().items():
            nm, u = NEWNAME[ch]; r = RecordingPen(); path.draw(r)
            glyphs[nm] = (r.value, a); cmap[u] = nm
    if V133:
        # 세로 줄기 축선 맞춤 {글자: {옛 점: 새 점}} — plan/phase-2/08
        # 어느 x 로 맞출지는 기둥 굵기 검토(plan/phase-1/08)의 굵기를 기준으로: 대문자 129, 소문자 120, m 123(가늘게 조정한 값)
        X = lambda g, a, b, ys: {(a, y): (b, y) for y in ys}
        AXIS_FIX = {
            "F": X("F", 263, 261, (600, 620)),               # 132~261 = 129 (263 이면 131)
            "E": X("E", 263, 261, (600, 620)),               # F 와 같음
            "m": X("m", 217, 214, (396, 503)),               # 91~214 = 123 (217 이면 126)
            "p": {**X("p", 204, 206, (-210, 52)), **X("p", 205, 206, (142, 212, 254, 308))},   # 87~206 = 119 (204 는 117, 205 는 118)
            "b": X("b", 200, 201, (142, 212, 254, 308)),     # 82~201 = 119 (200 은 118)
            "f_b": X("f_b", 548, 549, (142, 212, 254, 308)), # 429~549 = 120
            "q": X("q", 373, 372, (-210, 52)),               # 372~491 = 119 (373 은 118)
            "u": X("u", 410, 409, (0, 93)),                  # 409~529 = 120 (410 은 119)
            "dollar": X("dollar", 343, 344, (678, 752)),     # 세로 막대 오른쪽 면 344 로 (기둥 아님, 긴 쪽에 맞춤)
            "one": X("one", 306, 307, (75, 108, 133, 135)),  # 받침 곡선 시작을 기둥 오른쪽 면 307 에 (왼쪽 168 과 같은 방식)
            "one.tf": X("one.tf", 369, 370, (75, 108, 133, 135)),
        }
        # 점 옮기기는 아래 contours() 에서 겹침 합치기 뒤에 한다(1 처럼 다시 그린 글자는 합친 뒤 좌표가 기준).
        # 옮긴 글자를 changed 에 넣지 않음: 겹침 합치기(pathops)가 다른 곡선을 건드리지 않게
    added = [g for g in glyphs if g not in order]
    order += added; changed |= set(added)

# ---- 겹친 획 합치기(새로 만들거나 바꾼 글자만) → 윤곽선 목록 ----
def contours(g):
    ops = glyphs[g][0]
    if g in changed:
        p = pathops.Path(); pen = p.getPen()
        for o, pts in ops: getattr(pen, o)(*pts)
        p.simplify(fix_winding=True)
        r = RecordingPen(); p.draw(r); ops = r.value
    if g in AXIS_FIX:
        mp, n, new_ops = AXIS_FIX[g], 0, []
        for o, pts in ops:
            pts = tuple((otRound(x), otRound(y)) for x, y in pts)     # 저장 때와 같은 반올림(1 은 원본이 306.5 같은 소수)
            q = tuple(mp.get(pt, pt) for pt in pts)
            n += sum(1 for x, y in zip(pts, q) if tuple(x) != y); new_ops.append((o, q))
        assert n == len(mp), (g, n, len(mp)); ops = new_ops
    cs, cur = [], []
    for o, pts in ops:
        if o == "moveTo": cur = [(o, pts)]
        elif o in ("closePath", "endPath"):
            if cur: cs.append(cur)
            cur = []
        else: cur.append((o, pts))
    if cur: cs.append(cur)
    return cs

def poly(c): return [pt for op, pts in c for pt in pts]
def area(c):
    p = poly(c); return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2
def inside(pt, c):
    p, x, y, r = poly(c), pt[0], pt[1], False
    for i in range(len(p)):
        (x1,y1),(x2,y2) = p[i], p[i-1]
        if (y1>y) != (y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: r = not r
    return r
def draw(cs, pen, ps_style, g):
    """윤곽 방향 맞추기 (CFF: 반시계 외곽, TT: 시계 외곽).
    바꾸지 않은 글자는 v1.200 OTF 방향이 이미 맞으므로 그대로(TT 는 모두 뒤집기)만 한다.
    L·E 처럼 겹친 두 조각으로 된 글자를 '안쪽 구멍'으로 잘못 판단해 겹친 곳이 뚫리는 것을 막기 위해서다.
    바꾼 글자는 pathops 로 겹침을 합친 뒤라, 안에 있으면 구멍으로 보고 방향을 정한다."""
    for i, c in enumerate(cs):
        if g in changed:
            depth = sum(inside(c[0][1][0], o) for j, o in enumerate(cs) if j != i)
            want_ccw = (depth % 2 == 0) == ps_style
            flip = (area(c) > 0) != want_ccw
        else:
            flip = not ps_style
        target = ReverseContourPen(pen) if flip else pen
        target.moveTo(c[0][1][0])
        for op, pts in c[1:]: getattr(target, op)(*pts)
        target.closePath()

CS = {g: contours(g) for g in order}

if V133:   # 3차 크리틱 전체 반영(font_critique/v133_edits.py) — 최종 서체와 같은 점 순서·방향으로 맞춘 뒤 고친다
    import v133_edits as ED
    from fontTools.pens.basePen import BasePen
    class _Cubic(BasePen):      # 2차 곡선은 OTF 에 저장될 때처럼 3차 곡선으로 풀어 기록
        def __init__(self): super().__init__(None); self.value = []
        def _moveTo(self, p): self.value.append(("moveTo", (p,)))
        def _lineTo(self, p): self.value.append(("lineTo", (p,)))
        def _curveToOne(self, a, b, c): self.value.append(("curveTo", (a, b, c)))
        def _closePath(self): self.value.append(("closePath", ()))
    def ser(cs):
        r = _Cubic(); g_ = ser.g; draw(cs, r, True, g_); out = []; last = None
        for o, pts in r.value:
            if o == "closePath": out.append("Z"); continue
            rp = tuple((otRound(x), otRound(y)) for x, y in pts)
            if o == "lineTo" and rp[-1] == last: continue        # 반올림 뒤 길이 0 인 선은 버림(저장 때도 사라짐)
            last = rp[-1]
            out.append({"moveTo": "M", "lineTo": "L", "curveTo": "C"}[o] + " ".join(f"{otRound(x)},{otRound(y)}" for x, y in pts))
        return " ".join(out)
    def parse(s):
        cs, cur = [], None
        for tok in s.replace(" Z", " Z|").split("|"):
            tok = tok.strip()
            if not tok: continue
            items = []
            for part in tok.split(" "):
                if part[0] in "MLCZ": items.append([part[0], []]); part = part[1:]
                if part: items[-1][1].append(tuple(int(v) for v in part.split(",")))
            c = []
            for o, pts in items:
                if o == "M": c.append(("moveTo", (pts[0],)))
                elif o == "L": c.append(("lineTo", tuple(pts)))
                elif o == "C": c.append(("curveTo", tuple(pts)))
            cs.append(c)
        return cs
    def collinear(cs):
        out = []
        for c in cs:
            pts = [c[0][1][0]] + [p[-1] for o, p in c[1:]]; keep = [c[0]]
            for i in range(1, len(c)):
                o, p = c[i]
                if o == "lineTo" and i + 1 < len(c) and c[i + 1][0] == "lineTo":
                    (x0, y0), (x1, y1), (x2, y2) = pts[i - 1], p[0], c[i + 1][1][0]
                    if (x1 - x0) * (y2 - y0) == (y1 - y0) * (x2 - x0): pts[i] = pts[i - 1]; continue
                keep.append(c[i])
            out.append(keep)
        return out
    EDITED = set()
    for g in set(ED.SUB) | set(ED.SUB_OPTIONAL) | set(ED.SHIFT_Y) | ED.COLLINEAR | set(ED.SHIFT_X):
        if g not in CS: continue
        ser.g = g; s = ser(CS[g])
        subs = (ED.SUB.get(g) or [(a, b) for a, b in ED.SUB_OPTIONAL.get(g, []) if a in s]) + ED.SUB2.get(g, [])
        for a, b in subs:
            assert s.count(a) == 1, (g, a, s)
            s = s.replace(a, b)
        cs = parse(s)
        if g in ED.SHIFT_Y:
            y0, dy = ED.SHIFT_Y[g]
            cs = [[(o, tuple((x, y + dy) if y >= y0 else (x, y) for x, y in p)) for o, p in c] for c in cs]
        if g in ED.COLLINEAR: cs = collinear(cs)
        if g in ED.SHIFT_X:
            dx = ED.SHIFT_X[g]
            cs = [[(o, tuple((x + dx, y) for x, y in p)) for o, p in c] for c in cs]
            glyphs[g] = (glyphs[g][0], glyphs[g][1] + dx)
        CS[g] = cs; EDITED.add(g)
    print("v1.33 윤곽 고침:", len(EDITED), "글자")

# ---- 글자 쌍 간격·합자·선택 기능 ----
fea = open(FEA, encoding="utf-8").read()
if not CONTROL:
    # ④ ty·rv: 간격을 벌리던 +20 을 0 으로 (기존 줄을 고침 — 같은 쌍을 다시 적으면 뒤엣것은 무시됨)
    for pr in ("t y", "r v"):
        fea, n = re.subn(r"(\n\s*pos " + pr + r") -?\d+;", r"\1 0;", fea); assert n == 1, pr
    # ① C·G 윗부분을 올리면서 C·G 다음 키 큰 대문자와 간격이 줄어(CV·CW·CY 는 닿음) v1.200 간격으로 되돌린다
    for pr, v in {"C Y": -100, "C V": -100, "C W": -100, "C X": -95, "C U": -80, "G Y": -115}.items():
        fea, n = re.subn(r"(\n\s*pos " + pr + r") -?\d+;", r"\g<1> " + str(v) + ";", fea); assert n == 1, pr
    fix_pairs = ["    pos C I -75;", "    pos C K -75;"]     # 묶음 규칙(@L_I -95)보다 먼저 적용되는 개별 쌍
    # f_t·f_j 왼쪽은 f 와 같은 묶음, 오른쪽은 t·j 의 개별 쌍을 그대로 복사
    fea = re.sub(r"(@L_f = \[[^\]]*)\]", r"\1 f_t f_j]", fea, count=1)
    extra = list(fix_pairs)
    for line in fea.splitlines():
        m = re.match(r"\s*pos (t|j) (\S+) (-?\d+);", line)
        if m: extra.append(f"    pos {'f_t' if m.group(1) == 't' else 'f_j'} {m.group(2)} {m.group(3)};")
        m = re.match(r"\s*pos (\S+) f (-?\d+);", line)
        if m: extra += [f"    pos {m.group(1)} f_t {m.group(2)};", f"    pos {m.group(1)} f_j {m.group(2)};"]
    # − ± × 는 + 와 같은 묶음
    fea = re.sub(r"(@R_symbols = \[[^\]]*)\]", r"\1 minus plusminus multiply]", fea, count=1)
    fea = re.sub(r"(@L_symbols = \[[^\]]*)\]", r"\1 minus plusminus multiply]", fea, count=1)
    i = fea.rindex("} kern;")
    if V131:   # v1.31: 대문자–숫자 쌍 (기존 규칙에 없던 쌍. 고정폭 숫자 .tf 는 다른 글자라 적용되지 않음)
        import json
        KUD = json.load(open(os.path.join(ROOT, "out/font-update/work/kern_uc_digit.json"), encoding="utf-8"))
        assert not any(re.search(r"\n\s*pos " + k + " ", fea) for k in KUD)
        extra += ["    # v1.31: 대문자–숫자"] + [f"    pos {k} {v};" for k, v in KUD.items()]
    if V132:
        # 대문자 대각선 18쌍: Avenir Next Demi 비율, 대문자 평균 간격 기준 (기존 개별 쌍 줄은 고치고, 없으면 더함)
        KD = {p: r["kern"] for p, r in json.load(open(os.path.join(ROOT, "out/font-update/kern-diag-compare/compare-mean.json"),
              encoding="utf-8"))["refs"]["Avenir Next Demi"]["pairs"].items()}
        extra.append("    # v1.32: 대문자 대각선 쌍·새 기호")
        for pr, kv in KD.items():
            fea, n = re.subn(r"(\n\s*pos " + pr[0] + " " + pr[1] + r") -?\d+;", r"\g<1> " + str(kv) + ";", fea)
            if n == 0: extra.append(f"    pos {pr[0]} {pr[1]} {kv};")
            else: assert n == 1, pr
        # 새 기호 간격 묶음: ‰ 는 % 와, … 는 마침표(오른쪽)와, — 는 대시와, ▲▼ 는 + 와 같은 묶음
        for cls, add in (("@R_symbols", "perthousand ellipsis uni25B2 uni25BC"), ("@L_symbols", "perthousand uni25B2 uni25BC"),
                         ("@R_dashes", "emdash"), ("@L_dashes", "emdash")):
            fea, n = re.subn(r"(" + cls + r" = \[[^\]]*)\]", r"\1 " + add + "]", fea, count=1); assert n == 1, cls
        for line in fea.splitlines():        # 마침표·% 의 개별 쌍도 복사
            m = re.match(r"\s*pos (\S+) (period|percent) (-?\d+);", line)
            if m: extra.append(f"    pos {m.group(1)} {'ellipsis' if m.group(2) == 'period' else 'perthousand'} {m.group(3)};")
            m = re.match(r"\s*pos percent (\S+) (-?\d+);", line)
            if m: extra.append(f"    pos perthousand {m.group(1)} {m.group(2)};")
        i = fea.rindex("} kern;")
    fea = fea[:i] + "\n    # v1.3: 이어 쓰기 글자 f_t f_j\n" + "\n".join(extra) + "\n" + fea[i:]
    fea = fea.replace("    sub f i by f_i;", "    sub f i by f_i;\n    sub f t by f_t;\n    sub f j by f_j;")
    digits = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "plus", "minus", "plusminus"]
    fea += "\n# ---- v1.3: 고정폭 숫자 (선택 기능, 표에서 켬) ----\nfeature tnum {\n" + \
           "".join(f"    sub {d} by {d}.tf;\n" for d in digits) + "} tnum;\n"

if V132:   # 기록용: 실제로 넣은 간격·합자 규칙
    os.makedirs(os.path.dirname(OUTDIR), exist_ok=True)
    open(os.path.join(os.path.dirname(OUTDIR), "features.fea"), "w", encoding="utf-8").write(fea)

def lsb(g):
    bp = BoundsPen(None)
    draw(CS[g], bp, True, g)
    return round(bp.bounds[0]) if bp.bounds else 0

def build(kind):
    fb = FontBuilder(1000, isTTF=(kind == "ttf"))
    fb.setupGlyphOrder(order); fb.setupCharacterMap(cmap)
    if kind == "otf":
        cs = {}
        for g in order:
            pen = T2CharStringPen(round(glyphs[g][1]), None); draw(CS[g], pen, True, g); cs[g] = pen.getCharString()
        fb.setupCFF(PS, {"FullName": f"{FAMILY} {STYLE}", "version": VERSION}, cs, {})
    else:
        gl = {}
        for g in order:
            pen = TTGlyphPen(None); draw(CS[g], Cu2QuPen(pen, 1.0, reverse_direction=False), False, g); gl[g] = pen.glyph()
        fb.setupGlyf(gl)
    fb.setupHorizontalMetrics({g: (round(glyphs[g][1]), lsb(g)) for g in order})
    fb.setupHorizontalHeader(ascent=800, descent=-250)
    fb.setupNameTable({"familyName": FAMILY, "styleName": STYLE, "uniqueFontIdentifier": f"{PS};{VERSION}",
                       "fullName": f"{FAMILY} {STYLE}", "psName": PS, "version": f"Version {VERSION}",
                       "copyright": "Copyright (c) 2026 FnGuide. All rights reserved.",
                       **({"licenseDescription": {"en": "For FnGuide internal use only until the FnGuide typeface including its own Korean glyphs is completed.",
                                                  "ko": "에프앤가이드 고유의 한글 글꼴까지 포함된 폰트가 완성되기 전까지 사내에서만 사용합니다."}} if V132 else {}),
                       "description": "Logotype font based on the FnGuide logo (A-Z, a-z, 0-9, ASCII punctuation"
                                      + ("" if CONTROL else ", financial symbols, tabular figures (tnum)") + (", report symbols" if V132 else "") + "; internal use)."})
    win_asc, fs_sel = (850, 0) if CONTROL else (870, 0x40)          # ⑤ Windows 위쪽 높이 870, Regular 표시
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-250, sTypoLineGap=0, usWinAscent=win_asc, usWinDescent=260,
                sxHeight=498, sCapHeight=700, fsType=(0x0002 if V132 else 0x0008), achVendID="FNGD", fsSelection=fs_sel)
    fb.setupPost()
    fb.font["head"].fontRevision = float(VERSION)
    addOpenTypeFeaturesFromString(fb.font, fea)
    os.makedirs(OUTDIR, exist_ok=True)
    fb.font.save(os.path.join(OUTDIR, f"{PS}.{kind}"))
    return fb.font

build("otf"); f = build("ttf")
f.flavor = "woff"; f.save(os.path.join(OUTDIR, f"{PS}.woff"))
if V132:
    f.flavor = "woff2"; f.save(os.path.join(OUTDIR, f"{PS}.woff2"))
print(VERSION, len(order), "글자 →", OUTDIR)
