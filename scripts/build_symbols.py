"""피그마에서 내보낸 서비스 심볼 아이콘(data/Symbol)을 사이트용으로 정리한다.

피그마 내보내기에는 캔버스·섹션·프레임 바탕이 함께 들어 있으므로
아이콘 그룹(KEEP 의 id)과 <defs>(그러데이션)만 남겨 out/brand-site/symbols.js 로 쓴다.
사이트는 내 컴퓨터 파일로 열기 때문에 SVG 를 따로 불러오지 않고 js 안에 글자로 담는다.

실행: py scripts/build_symbols.py
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "Symbol"
OUT = ROOT / "out" / "brand-site" / "symbols.js"
NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

# 서비스 id: (원본 파일, 남길 그룹 id, 설명) — 피그마 "FnGuide Brand Symbol" 페이지
KEEP = {
    "retamin": ("retamin/retamin-icon-navy.svg", "img/retamin-app-icon", "Report의 R — 네모·세모·원"),
    "dataguide": ("dataguide/figma/dataguide-icon-256.svg", "Icon-set", "D·G와 ∞ — 무한한 데이터 흐름"),
    "cryptoguide": ("cryptoguide/cryptoguide-icon-512.svg", "CryptoGuide", "Crypto·Guide 이니셜의 큐브"),
    # 일러스트레이터 내보내기(사용자 디자인 2026-10-30): 그룹 id 대신 None — 파일 전체를 쓴다
    "wisereport": ("wisereport/WR-White-modify.svg", None, "Wise·Report 이니셜 W·R"),
}

# 바탕색 바꾸기 (원본 파일은 그대로 두고 사이트용만): DataGuide 는 피그마 #BF2645 대신 FnRed 2025 (사용자 요청 2026-10-29)
RECOLOR = {"dataguide": {"#BF2645": "#B9023D"}}

def illustrator(root):
    """일러스트레이터 SVG: <style> 의 클래스 색을 fill 로 옮기고, 한글 그러데이션 id 를 영문으로 바꾼다
    (사이트가 id 뒤에 크기를 붙일 때 영문·숫자만 알아봄). 크기는 viewBox 에서 가져온다."""
    style = root.find(f"{{{NS}}}defs/{{{NS}}}style")
    # 클래스별 속성: fill·opacity 는 그대로 속성으로, 나머지(mix-blend-mode·isolation)는 style 로
    rules = {c: dict(re.findall(r"([\w-]+):\s*([^;]+);", body)) for c, body in re.findall(r"\.(\w+)\s*\{([^}]*)\}", style.text)}
    style_parent = root.find(f"{{{NS}}}defs")
    style_parent.remove(style)
    ids = {e.get("id"): f"paint{i}" for i, e in enumerate(e for e in root.iter() if e.tag.endswith("linearGradient"))}
    for e in root.iter():
        if e.get("class"):
            css = []
            for k, v in rules[e.attrib.pop("class")].items():
                v = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{ids[m.group(1)]})", v.strip())
                if k in ("fill", "opacity"):
                    e.set(k, v)
                else:
                    css.append(f"{k}:{v}")
            if css:
                e.set("style", ";".join(css))
        if e.tag.endswith("linearGradient"):
            e.set("id", ids[e.get("id")])
        elif "id" in e.attrib:
            del e.attrib["id"]
        e.attrib.pop("data-name", None)
    w, h = root.get("viewBox").split()[2:]
    out = ET.Element(f"{{{NS}}}svg", {"width": w, "height": h, "viewBox": f"0 0 {w} {h}", "fill": "none"})
    out.extend(e for e in root if not e.tag.endswith("defs"))
    out.extend(e for e in root if e.tag.endswith("defs"))
    return re.sub(r">\s+<", "><", ET.tostring(out, encoding="unicode"))


def clean(path, keep_id):
    root = ET.parse(SRC / path).getroot()
    if keep_id is None:
        return illustrator(root)
    w, h = root.get("width"), root.get("height")
    group = next(e for e in root.iter() if e.get("id") == keep_id)
    defs = [e for e in root if e.tag == f"{{{NS}}}defs"]
    out = ET.Element(f"{{{NS}}}svg", {"width": w, "height": h, "viewBox": f"0 0 {w} {h}", "fill": "none"})
    out.append(group)
    out.extend(defs)
    for e in out.iter():  # 피그마 레이어 이름(id)은 필요 없음 — 그러데이션 id 만 남김
        if e.get("id") and not e.tag.endswith("linearGradient") and not e.tag.endswith("clipPath") and not e.tag.endswith("mask"):
            del e.attrib["id"]
    svg = ET.tostring(out, encoding="unicode")
    return re.sub(r">\s+<", "><", svg)


def main():
    data = {}
    for sid, (path, keep_id, desc) in KEEP.items():
        svg = clean(path, keep_id)
        # 서비스마다 그러데이션 id 가 같으므로(paint0_linear_4_5306) 한 화면에 함께 그려도 섞이지 않게 바꾼다
        svg = svg.replace("paint", f"{sid}-paint")
        for a, b in RECOLOR.get(sid, {}).items():
            svg = svg.replace(a, b)
        data[sid] = {"svg": svg, "desc": desc, "size": int(re.search(r'width="(\d+)', svg).group(1))}
    OUT.write_text("window.SYMBOLS = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print("symbols:", ", ".join(data))


if __name__ == "__main__":
    main()
