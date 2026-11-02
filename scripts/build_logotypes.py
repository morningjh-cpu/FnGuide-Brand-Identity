"""전용서체(FnGuide Logotype)로 브랜드별 로고타입 SVG를 만든다.

- 글자 간격(커닝)과 f 합자는 서체에 들어 있는 규칙을 그대로 적용한다.
- 회사 CI 공식 로고는 회사 홈페이지 CIP(https://corp.fnguide.com/Company/CIP) 파일을 그대로 쓴다 (data/corp-cip).
  공식 CI는 색 바꾸기 등 변형 금지 → 흰색 판을 만들지 않고 홈페이지가 주는 단색 판만 쓴다.
- 개선된 브랜드 로고 "FnGuide"(FnRed)는 서체 패키지의 원본 파일을 쓴다 (서체 문서 5장 사용 원칙).
- 리타민은 B2C 독립 체계라 전용서체 대신 기존 로고(피그마)를 그대로 쓴다.
- 그룹색 배경용 흰색 판(logos/white/)과 회사 CI 화면에 보여줄 FnPricing(전시용, 다운로드 없음)도 만든다.
- 서체 미리보기의 SVG·PNG 저장에 쓸 글자 모양·간격 정보(font-data.js)도 함께 만든다.
결과: out/brand-site/logos/*.svg, out/brand-site/logos.js, out/brand-site/font-data.js
실행: py scripts/build_logotypes.py   (필요: py -m pip install fonttools uharfbuzz)
      글자 정보(font-data.js)만 다시 만들 때: py scripts/build_logotypes.py --font-data
"""
import json
import re
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "data" / "FnGuide-Logotype-Font"
# 로고타입은 최신 서체 v1.3 으로 만든다 (v1.200: out/font-update/v1.200, 기둥 조정 전 서체: out/font-update/logo-font)
FONT = ROOT / "out" / "font-update" / "v1.32" / "fonts" / "FnGuideLogotype-Regular.otf"
CI_SVG = FONT_DIR / "source-svg" / "0_logo" / "FnGuide.svg"
FIGMA = ROOT / "data" / "figma-logo-parts"
RETAMIN_SVG = FIGMA / "retamin.svg"
CIP = ROOT / "data" / "corp-cip"
OUT = ROOT / "out" / "brand-site"

HEIGHT_PX = 40  # 대문자 높이 700 단위가 28px 정도로 보이는 크기 (1000 단위 = 40px)

# 그룹·색상: 서체 문서 4장 표. 회사 CI 주색상 FnWine #94243A (홈페이지 표의 #962E45는 잘못된 값, 사용자 확인). 개선 로고 FnRed와 구분해 FnWine으로 부름
GROUPS = [
    {"id": "ci", "name": "회사 CI", "color": "#94243A", "colorName": "FnWine"},
    {"id": "b2b", "name": "B2B 대표상품", "color": "#B9023D", "colorName": "FnRed"},
    {"id": "index", "name": "지수", "color": "#45B792", "colorName": "Index"},
    {"id": "fund", "name": "펀드", "color": "#0C3178", "colorName": "Fund"},
    {"id": "contract", "name": "B2B 계약상품", "color": "#1C1C3A", "colorName": "Contract"},
    {"id": "b2c", "name": "B2C 독립 체계", "color": "#2457C5", "colorName": "리타민 · WiseReport · API"},
]
COLOR = {g["id"]: g["color"] for g in GROUPS}

# (파일명, 글자, 그룹, 색상 덮어쓰기) — 브랜드 목록은 피그마 「FnGuide Brand Color」 페이지 기준
BRANDS = [
    ("fnguide-com", "FnGuide.com", "b2b", None),
    ("dataguide", "DataGuide", "b2b", None),
    ("quantiwise", "QuantiWise", "b2b", None),
    ("fnindex", "FnIndex", "index", None),
    ("wiseindex", "WiseIndex", "index", None),
    ("cryptoguide", "CryptoGuide", "index", None),
    ("fundguide", "FundGuide", "fund", None),
    ("pfguide", "PFGuide", "fund", None),
    ("fnaims", "FnAIMS", "fund", None),
    ("fnspectrum", "FnSpectrum", "fund", None),
    ("fnares", "FnARES", "fund", None),
    ("companyguide", "CompanyGuide", "contract", None),
    ("companywise", "CompanyWise", "contract", None),
    ("companyglobal", "CompanyGlobal", "contract", None),
    ("etfglobal", "ETF Global", "contract", None),
    ("marketmonitor", "Market Monitor", "contract", None),
    ("fnspace", "FnSpace", "contract", None),
    ("wisereport", "WiseReport", "b2c", "#594FC8"),  # 2026-10-30 B2B 대표상품 → B2C 독립 체계
    ("fnapi", "FnAPI", "b2c", "#2457C5"),
]



# 그 밖의 CI (전시용, 다운로드 없음) — (파일명, 이름, 설명, 이미지 파일)
# FnPricing: 에프앤자산평가 홈페이지 CI 이미지 (https://www.fnpricing.com/fr/images/img_ci_logo.png → data/fnpricing)
ARCHIVE = [
    ("ci-fnpricing", "FnPricing", "2011년 6월 창립 — 에프앤자산평가 자체 제작", ROOT / "data" / "fnpricing" / "img_ci_logo.png"),
]

# 서비스 웹사이트 (로고타입 카드에 링크로 표시)
SERVICE_URL = {
    "fnguide-com": "https://www.fnguide.com/",
    "dataguide": "https://dataguide.fnguide.com/",
    "quantiwise": "https://corp.fnguide.com/fng/serviceinfo_quantiwiseIndex",
    "wisereport": "https://www.wisereport.co.kr",
    "fnindex": "https://www.fnindex.co.kr/overview/info/MIS",
    "wiseindex": "https://www.wiseindex.com/Index/Index#/WMI500",
    "cryptoguide": "https://crypto.fnguide.com/",
    "fundguide": "https://www.fundguide.net/",
    "pfguide": "https://www.pfguide.co.kr/",
    "fnaims": "https://www.fnaims.co.kr/",
    "fnspectrum": "https://www.fnspectrum.com/",
    "fnares": "https://devares.fnguide.com/",
    "companyguide": "https://wcomp.fnguide.com/",
    "companywise": "https://comp.wisereport.co.kr/",
    "companyglobal": "https://compglobal.wisereport.co.kr",
    "etfglobal": "https://globaletf.wisereport.co.kr",
    "fnspace": "https://www.fnspace.com/",
    "retamin": "https://retamin.fnguide.com/",
}

ARCHIVE_URL = {"ci-fnpricing": "https://www.fnpricing.com/fr/pc/intro/vision"}


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def svg_doc(path_d, x0, y0, w, h, color):
    """글꼴 단위(1000) 좌표의 도형을 픽셀 크기가 붙은 SVG 한 파일로 감싼다."""
    pw, ph = w * HEIGHT_PX / 1000, h * HEIGHT_PX / 1000
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(pw)}" height="{fmt(ph)}" '
        f'viewBox="{fmt(x0)} {fmt(y0)} {fmt(w)} {fmt(h)}"><path fill="{color}" d="{path_d}"/></svg>\n'
    )


def typeset(text, color, hb_font, glyph_set, upem):
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, {"kern": True, "liga": True})
    names = TTFONT.getGlyphOrder()
    svg_pen = SVGPathPen(glyph_set)
    bounds = BoundsPen(glyph_set)
    x = 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = names[info.codepoint]
        # y축을 뒤집어 SVG 좌표(아래로 증가)로 바꾼다
        t = (1, 0, 0, -1, x + pos.x_offset, -pos.y_offset)
        glyph_set[name].draw(TransformPen(svg_pen, t))
        glyph_set[name].draw(TransformPen(bounds, t))
        x += pos.x_advance
    xmin, ymin, xmax, ymax = bounds.bounds
    return svg_doc(svg_pen.getCommands(), xmin, ymin, xmax - xmin, ymax - ymin, color)


def font_data():
    """서체 미리보기 SVG·PNG 저장용: 글자 모양·합자·글자 간격을 브라우저에서 쓸 수 있게 뽑는다.

    외부 프로그램 없이 페이지가 직접 글자를 그리도록, 간격은 하르프버즈로 두 글자씩 조판해 잰 값을 그대로 쓴다.
    미리보기와 같아야 하므로 로고용 FONT가 아니라 사이트가 쓰는 서체 파일을 읽는다.
    """
    site_font = OUT / "fonts" / "FnGuideLogotype-Regular.otf"
    font = TTFont(site_font)
    hb_font = hb.Font(hb.Face(hb.Blob.from_file_path(str(site_font))))
    glyph_set = font.getGlyphSet()
    names = font.getGlyphOrder()
    cmap = font.getBestCmap()
    glyphs = {}
    for name in names:
        pen = SVGPathPen(glyph_set, fmt)
        glyph_set[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
        glyphs[name] = [glyph_set[name].width, pen.getCommands()]
    liga = []
    for lookup in font["GSUB"].table.LookupList.Lookup:
        for sub in lookup.SubTable:
            for first, ligs in getattr(sub, "ligatures", {}).items():
                for lg in ligs:
                    seq = [first] + lg.Component
                    rev = {v: k for k, v in cmap.items()}
                    liga.append(["".join(chr(rev[g]) for g in seq), lg.LigGlyph])
    liga.sort(key=lambda x: -len(x[0]))
    # 조판 단위: 글자 하나 또는 합자 하나. 두 단위씩 조판해 둘째 글자 위치에서 첫 글자 폭을 뺀 값이 간격 보정
    units = [(chr(c), n) for c, n in cmap.items()] + [(s, n) for s, n in liga]
    kern = {}
    for s1, n1 in units:
        for s2, n2 in units:
            buf = hb.Buffer()
            buf.add_str(s1 + s2)
            buf.guess_segment_properties()
            hb.shape(hb_font, buf, {"kern": True, "liga": True})
            got = [names[i.codepoint] for i in buf.glyph_infos]
            if got != [n1, n2]:
                continue  # 이어 붙이면 새 합자가 생기는 쌍 — 합자 쪽에서 처리됨
            dx = buf.glyph_positions[0].x_advance - glyphs[n1][0]
            if dx:
                kern[f"{n1} {n2}"] = dx
    data = {"upem": font["head"].unitsPerEm, "cmap": {chr(c): n for c, n in cmap.items()},
            "liga": liga, "kern": kern, "glyphs": glyphs}
    (OUT / "font-data.js").write_text(
        "window.FONT_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"font-data: {len(glyphs)} glyphs, {len(liga)} ligatures, {len(kern)} kerning pairs")


def official_ci():
    """공식 FnGuide 로고 원본에서 그림 부분만 잘라 낸다 (모양·색은 그대로)."""
    src = CI_SVG.read_text(encoding="utf-8")
    color = re.search(r"fill:\s*(#[0-9a-fA-F]{6})", src).group(1)
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', src)
    bounds = BoundsPen(None)
    for d in ds:
        parse_path(d, bounds)
    xmin, ymin, xmax, ymax = bounds.bounds
    w, h = xmax - xmin, ymax - ymin
    scale = HEIGHT_PX * 0.7 / h  # 원본 높이를 서체 대문자 높이(700)에 맞춘다
    paths = "".join(f'<path fill="{color}" d="{d}"/>' for d in ds)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w * scale)}" height="{fmt(h * scale)}" '
        f'viewBox="{fmt(xmin)} {fmt(ymin)} {fmt(w)} {fmt(h)}">{paths}</svg>\n'
    )


def existing_logo(path, keep_ids=False):
    """기존 로고 파일을 모양·색 그대로 쓴다 (피그마 내보내기 속성만 정리, 잘라내기 영역 id는 필요하면 남김)."""
    src = path.read_text(encoding="utf-8")
    attrs = "preserveAspectRatio|overflow|style" if keep_ids else "preserveAspectRatio|overflow|style|id"
    src = re.sub(r'\s(' + attrs + r')="[^"]*"', "", src)
    return src.strip() + "\n"


def compose(w, h, parts, out_h=56):
    """피그마 조각을 정해진 위치에 놓아 SVG 한 파일로 합친다."""
    body = []
    for name, x, y in parts:
        src = (FIGMA / f"{name}.svg").read_text(encoding="utf-8")
        vb = re.search(r'viewBox="([^"]+)"', src).group(1)
        pw, ph = re.search(r'width="([^"]+)" height="([^"]+)"', src).groups()
        inner = re.search(r"<svg[^>]*>(.*)</svg>", src, re.S).group(1)
        inner = re.sub(r'\s(id|data-figma-[\w-]+)="[^"]*"', "", inner)
        body.append(f'<svg x="{x}" y="{y}" width="{pw}" height="{ph}" viewBox="{vb}" overflow="visible">{inner.strip()}</svg>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w * out_h / h)}" height="{out_h}" '
        f'viewBox="0 0 {w} {h}" fill="none">' + "".join(body) + "</svg>\n"
    )


def recolor(svg):
    """홈페이지 단색 Dark Gray 파일의 회색 #6B7B84를 확정 색 #778288로 다시 칠한다 (사용자 확인)."""
    return svg.replace('fill="#6B7B84"', 'fill="#778288"')


def png_logo(path, out_h=56):
    """PNG 로고를 웹페이지에 바로 넣을 수 있게 SVG로 감싼다 (그림은 그대로)."""
    import base64
    import struct
    data = path.read_bytes()
    w, h = struct.unpack(">II", data[16:24])
    b64 = base64.b64encode(data).decode()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(w * out_h / h)}" height="{out_h}" viewBox="0 0 {w} {h}">'
            f'<image width="{w}" height="{h}" href="data:image/png;base64,{b64}"/></svg>')


def to_white(svg):
    """색이 있는 칠을 모두 흰색으로 바꾼 판 (모양은 그대로)."""
    return re.sub(r'fill="#[0-9A-Fa-f]{3,6}"', 'fill="#FFFFFF"', svg)


TTFONT = TTFont(FONT)


def main():
    blob = hb.Blob.from_file_path(str(FONT))
    hb_font = hb.Font(hb.Face(blob))
    glyph_set = TTFONT.getGlyphSet()
    upem = TTFONT["head"].unitsPerEm

    (OUT / "logos" / "white").mkdir(parents=True, exist_ok=True)
    items = []
    # 회사 CI: 홈페이지 공식 파일 (흰색 판은 홈페이지 단색 판만)
    official = []
    for file, name, src, white, kind, extra in [
        ("fnguide-ci", "FnGuide CI", "cip.svg", "logo_white.svg", "official",
         [("wine", "단색 FnWine", "logo_red.svg"), ("darkgray", "단색 FnDarkGray", "logo_darkGray.svg")]),
        ("fnguide-inc", "FnGuide Inc.", "logo_cip1.svg", None, "logotype", []),
        ("fnguide-kr", "(주)에프앤가이드", "logo_cip2.svg", None, "logotype", []),
    ]:
        official.append({"id": file, "name": name, "kind": kind, "svg": existing_logo(CIP / src, True),
                         "white": existing_logo(CIP / white, True) if white else None,
                         "variants": [{"key": k, "label": lb, "svg": recolor(existing_logo(CIP / f, True)).strip()} for k, lb, f in extra]})
    entries = [("fnguide", "FnGuide", "ci", official_ci())]
    for file, text, group, color in BRANDS:
        entries.append((file, text, group, typeset(text, color or COLOR[group], hb_font, glyph_set, upem)))
    # B2C 순서: Retamin → WiseReport → FnAPI (리타민을 B2C 맨 앞에)
    entries.insert(next(i for i, e in enumerate(entries) if e[2] == "b2c"), ("retamin", "Retamin", "b2c", existing_logo(RETAMIN_SVG)))
    for o in official:
        (OUT / "logos" / f"{o['id']}.svg").write_text(o["svg"], encoding="utf-8")
        if o["white"]:
            (OUT / "logos" / "white" / f"{o['id']}.svg").write_text(o["white"], encoding="utf-8")
        for v in o["variants"]:
            (OUT / "logos" / f"{o['id']}-{v['key']}.svg").write_text(v["svg"] + "\n", encoding="utf-8")
        w, h = (float(v) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', o["svg"]).groups())
        items.append({"id": o["id"], "name": o["name"], "group": "ci", "kind": o["kind"], "w": w, "h": h, "note": "",
                      "svg": o["svg"].strip(), "white": o["white"].strip() if o["white"] else None,
                      "variants": o["variants"]})
    for file, text, group, svg in entries:
        white = to_white(svg)
        (OUT / "logos" / f"{file}.svg").write_text(svg, encoding="utf-8")
        (OUT / "logos" / "white" / f"{file}.svg").write_text(white, encoding="utf-8")
        w, h = (float(v) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', svg).groups())
        items.append({"id": file, "name": "FnGuide (개선 로고)" if file == "fnguide" else text, "group": group,
                      "kind": "improved" if file == "fnguide" else "bi", "w": w, "h": h, "note": "",
                      "url": SERVICE_URL.get(file, ""),
                      "svg": svg.strip(), "white": white.strip()})
    archive = [{"id": f, "name": n, "desc": d, "url": ARCHIVE_URL.get(f, ""), "svg": png_logo(img)} for f, n, d, img in ARCHIVE]
    (OUT / "logos.js").write_text(
        "window.BRAND = " + json.dumps({"groups": GROUPS, "logos": items, "archive": archive}, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"logotypes: {len(items)}")
    font_data()


if __name__ == "__main__":
    font_data() if "--font-data" in sys.argv else main()
