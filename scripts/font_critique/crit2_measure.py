"""2차 크리틱(v1.31) 측정: 1차 수정 필요 5건 확인, 남은 개선 권장 재측정, 사용·관리 관점 수치.
결과는 out/font-critique/metrics-v1.31.json 에 저장하고 요약을 화면에 찍는다.
실행: py scripts/font_critique/crit2_measure.py
"""
import io, json, os, sys
import numpy as np
import lib
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from measure_core import proportions, hscan, vscan

OUT = lib.ROOT + "out/font-critique/metrics-v1.31.json"
NEW, OLD = "FnGuide v1.31", "FnGuide v1.200"


def bbox_g(f, g):
    bp = BoundsPen(f.gs); f.gs[g].draw(bp); return bp.bounds


def bbox(f, ch):
    return bbox_g(f, f.tt.getBestCmap()[ord(ch)])


def kern(f, a, b, feats=None):
    """두 글자 쌍의 실제 보정값(조판 폭 − 각 글자 폭 합). 합자가 되면 None"""
    gl, w = f.shape(a + b, feats)
    if len(gl) != 2: return None
    hm = f.tt["hmtx"]; cm = f.tt.getBestCmap()
    return w - hm[cm[ord(a)]][0] - hm[cm[ord(b)]][0]


def glyph_names(f, text, feats=None):
    return [g for g, _, _ in f.shape(text, feats)[0]]


def ink_gap(f, text, i):
    """text 의 i번째와 i+1번째 글자 사이, 같은 높이에서 가장 가까운 잉크 간격(서체 단위)"""
    gl, _ = f.shape(text)
    if len(gl) < len(text): return "합자"
    (ga, xa, _), (gb, xb, _) = gl[i], gl[i + 1]
    best = 1e9
    for y in range(0, 720, 6):
        ra = hscan(f, None, y, glyph=ga); rb = hscan(f, None, y, glyph=gb)
        if ra and rb:
            best = min(best, (xb + rb[0][0]) - (xa + ra[-1][1]))
    return round(best, 1)


def table_info(path):
    t = TTFont(path)
    os2, head, hhea = t["OS/2"], t["head"], t["hhea"]
    ff = lib.F(path); bs = [bbox_g(ff, g) for g in t.getGlyphOrder()]
    ymax = max(b[3] for b in bs if b)
    names = {}
    for rec in t["name"].names:
        if rec.platformID == 3:
            names[rec.nameID] = str(rec)
    feats = sorted({fr.FeatureTag for tag in ("GSUB", "GPOS") if tag in t
                    for fr in t[tag].table.FeatureList.FeatureRecord})
    return dict(
        glyphs=len(t.getGlyphOrder()), cmap=len(t.getBestCmap()),
        winAscent=os2.usWinAscent, winDescent=os2.usWinDescent, maxY=ymax,
        fsSelection=hex(os2.fsSelection), fsType=os2.fsType, weight=os2.usWeightClass,
        vendor=os2.achVendID, typo=(os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap),
        hhea=(hhea.ascent, hhea.descent, hhea.lineGap), upm=head.unitsPerEm,
        fontRevision=round(head.fontRevision, 3), names=names, features=feats,
        hinting=[k for k in ("fpgm", "prep", "cvt ", "gasp") if k in t],
    )


def sizes(folder):
    out = {}
    for ext in ("otf", "ttf", "woff"):
        p = f"{folder}/FnGuideLogotype-Regular.{ext}"
        out[ext] = os.path.getsize(p)
    # woff2 는 파일을 만들지 않고 메모리에서만 크기를 잰다
    t = TTFont(f"{folder}/FnGuideLogotype-Regular.otf"); t.flavor = "woff2"
    buf = io.BytesIO(); t.save(buf); out["woff2(계산)"] = len(buf.getvalue())
    return out


def stem_x(f, ch, frac):
    """글자 높이 frac 위치 첫 세로획 두께"""
    b = bbox(f, ch); r = hscan(f, ch, b[1] + (b[3] - b[1]) * frac)
    return r[0][1] - r[0][0]


def korean_pair(fn):
    """한글 서체와 섞어 쓸 때: 대문자 높이·굵기 비교. 같은 글자 크기(em)에서 잰다."""
    cands = {
        "Pretendard Regular": lib.UF + "Pretendard-Regular.ttf",
        "Pretendard Medium": lib.UF + "Pretendard-Medium.ttf",
        "Pretendard SemiBold": lib.UF + "Pretendard-SemiBold.ttf",
        "Pretendard Bold": lib.UF + "Pretendard-Bold.ttf",
        "Noto Sans KR Medium": lib.UF + "NotoSansKR-Medium.otf",
        "맑은 고딕 Bold": lib.SF + "malgunbd.ttf",
        "맑은 고딕": lib.SF + "malgun.ttf",
        "Spoqa Han Sans Neo Medium": lib.UF + "SpoqaHanSansNeo-Medium.ttf",
    }
    fcap = bbox(fn, "H")[3] / fn.upm
    fstem = stem_x(fn, "H", 0.3) / fn.upm
    res = {"FnGuide": dict(cap=round(fcap, 3), stemH=round(fstem, 4))}
    for name, p in cands.items():
        if not os.path.exists(p): continue
        k = lib.F(p); u = k.upm
        hb_ = bbox(k, "한"); gb = bbox(k, "가")
        hang_h = (max(hb_[3], gb[3]) - min(hb_[1], gb[1])) / u   # 한글 글자 높이
        cap = bbox(k, "H")[3] / u
        stem = stem_x(k, "H", 0.3) / u
        # 한글 세로획: '이'의 ㅣ (오른쪽 세로획) 두께
        ib = bbox(k, "이"); r = hscan(k, "이", ib[1] + (ib[3] - ib[1]) * 0.5)
        hstem = (r[-1][1] - r[-1][0]) / u
        res[name] = dict(cap=round(cap, 3), hangul_h=round(hang_h, 3), stemH=round(stem, 4),
                         hangul_stem=round(hstem, 4),
                         # FnGuide 대문자를 이 서체의 한글 높이 × 0.78 에 맞출 때의 크기 배율 (아래 설명)
                         size_to_cap=round(cap / fcap, 3),
                         stem_ratio_at_cap=round((fstem * (cap / fcap)) / stem, 3))
    return res


def main():
    fN, fO = lib.load(NEW), lib.load(OLD)
    R = {"prop": {}, "heights": {}, "kern": {}, "files": {}, "korean": {}}
    for n in (NEW, OLD, "Rotis Semi Sans Bold", "Helvetica Neue Medium", "Avenir Next Demi", "Inter Medium"):
        R["prop"][n] = proportions(lib.load(n))

    # ① ② ③ 높이
    for n, f in ((NEW, fN), (OLD, fO)):
        R["heights"][n] = {ch: (round(bbox(f, ch)[1]), round(bbox(f, ch)[3]))
                           for ch in "HOCGSnzocevwxyl1I0479"}

    # ④ f 주변, ⑧ 대각선 쌍, 대문자–숫자
    pairs_f = ["ft", "fj", "ty", "rv", "fy", "ff"]
    pairs_diag = ["AV", "AY", "AW", "LT", "LV", "LY", "LW", "Ty", "To", "Te", "Ta", "Vo", "Va", "Yo", "PA", "FA", "VA", "AT"]
    pairs_ud = ["H0", "HO", "T4", "7A", "L1", "Y4", "C4", "A7"]
    for n, f in ((NEW, fN), (OLD, fO), ("Helvetica Neue Medium", lib.load("Helvetica Neue Medium")),
                 ("Inter Medium", lib.load("Inter Medium"))):
        cap = bbox(f, "H")[3]; k = 700 / cap  # 대문자 700 기준으로 환산
        d = {}
        for p in pairs_f + pairs_diag + pairs_ud:
            v = kern(f, p[0], p[1])
            d[p] = None if v is None else round(v * k)
        R["kern"][n] = d
    R["lig"] = {w: glyph_names(fN, w) for w in ("soft", "lift", "fifty", "fjord", "office")}
    R["gap"] = {}
    for w, i in (("soft", 2), ("lift", 2), ("ty", 0), ("rv", 0), ("LY", 0), ("LV", 0), ("AV", 0), ("HO", 0), ("H0", 0)):
        R["gap"][w] = {NEW: ink_gap(fN, w, i), OLD: ink_gap(fO, w, i)}

    # ⑤ ⑨ ⑩ 파일
    for n, folder in ((NEW, "out/font-update/v1.31/fonts"), (OLD, "out/font-update/v1.200/fonts")):
        info = table_info(lib.ROOT + folder + "/FnGuideLogotype-Regular.otf")
        info["ttf_hinting"] = table_info(lib.ROOT + folder + "/FnGuideLogotype-Regular.ttf")["hinting"]
        info["sizes"] = sizes(lib.ROOT + folder)
        cm = TTFont(lib.ROOT + folder + "/FnGuideLogotype-Regular.otf").getBestCmap()
        want = "₩·−±×—–…©®™°‰€%‘’“”•→←↑↓△▲▼"
        info["missing"] = "".join(c for c in want if ord(c) not in cm)
        info["digits_adv"] = {c: TTFont(lib.ROOT + folder + "/FnGuideLogotype-Regular.otf")["hmtx"][cm[ord(c)]][0] for c in "0123456789"}
        R["files"][n] = info
    R["tnum"] = glyph_names(fN, "1024", {"kern": True, "tnum": True})

    # 한글과 섞어 쓰기
    R["korean"] = korean_pair(fN)

    json.dump(R, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(R, ensure_ascii=False, indent=1)[:12000])


if __name__ == "__main__":
    main()
