"""세로 줄기 축선 어긋남 미리보기 → out/font-update/v1.33-preview/axis.html
빨간 세로선 = 어긋난 점의 x, 파란 세로선 = 기준 줄기 x. 빨간 원 = 어긋난 점."""
import os, html
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
V132 = TTFont(os.path.join(ROOT, "out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf"))
V133 = TTFont(os.path.join(ROOT, "out/font-update/v1.33/fonts/FnGuideLogotype-Regular.otf"))

# (글자, 제목, 기준 x, 어긋난 x, 설명, 등급)
ITEMS = [
    ("F", "F", 261, 263, "줄기 오른쪽 면 263 → 261. 굵기 129 = 대문자 기준(H·E·L 과 같음)", "fix"),
    ("E", "E", 261, 263, "F 와 같음. 263 → 261, 굵기 129", "fix"),
    ("m", "m", 214, 217, "첫 줄기 위쪽 217 → 214. 굵기 123 = 지난번 가늘게 조정한 m 기준(217 이면 126)", "fix"),
    ("p", "p", 206, 204, "아래 204·안쪽 205 → 206. 굵기 119 (204 는 117 로 소문자 기준 120 보다 가늚)", "fix"),
    ("b", "b", 201, 200, "동그라미 안쪽 200 → 201. 굵기 119", "fix"),
    ("f_b", "fb 이어 쓰기", 549, 548, "동그라미 안쪽 548 → 549. 굵기 120 = 소문자 기준", "fix"),
    ("q", "q", 372, 373, "아래 내림 373 → 372. 굵기 119 (373 은 118)", "fix"),
    ("u", "u", 409, 410, "아래 410 → 409. 굵기 120 = 소문자 기준 (410 은 119)", "fix"),
    ("dollar", "$", 344, 343, "세로 막대 맨 위 343 → 344 (기둥이 아니라 긴 쪽에 맞춤)", "fix"),
    ("one", "1", 307, 306, "받침 곡선 시작 306 → 307, 줄기 오른쪽 면과 같게 (왼쪽은 원래 168 로 같음). 고정폭 1 도 같이", "fix"),
]

def svg(font, g, xa, xb, size=230):
    gs = font.getGlyphSet(); p = SVGPathPen(gs); gs[g].draw(p)
    adv = font["hmtx"][g][0]; top, bot = 800, -250
    w = max(adv, 600) + 80
    r = RecordingPen(); gs[g].draw(r)
    pts = [pt for _, a in r.value for pt in a]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="#1e6fff"/>' for x, y in pts)
    rings = "" if xb is None else "".join(f'<circle cx="{x}" cy="{y}" r="22" fill="none" stroke="#e00" stroke-width="5"/>' for x, y in pts if x == xb)
    guides = "" if xa is None else (f'<line x1="{xa}" x2="{xa}" y1="{bot}" y2="{top}" stroke="#1e6fff" stroke-width="2" opacity=".7"/>'
                                    f'<line x1="{xb}" x2="{xb}" y1="{bot}" y2="{top}" stroke="#e00" stroke-width="2" opacity=".7"/>')
    return (f'<svg viewBox="-40 {-top} {w} {top-bot}" height="{size}"><g transform="scale(1,-1)">'
            f'<line x1="-40" x2="{w}" y1="0" y2="0" stroke="#ccc"/><path d="{p.getCommands()}" fill="#111" opacity=".85"/>'
            f'{guides}{dots}{rings}</g></svg>')

def zoom(font, g, xa, xb):
    """어긋난 점 근처 확대"""
    gs = font.getGlyphSet(); p = SVGPathPen(gs); gs[g].draw(p)
    r = RecordingPen(); gs[g].draw(r)
    pts = [pt for _, a in r.value for pt in a]
    ys = [y for x, y in pts if x == xb] or [y for x, y in pts if x == xa]
    cy = ys[0]; cx = (xa + xb) / 2
    vb = f"{cx-45} {-(cy+45)} 90 90"
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#1e6fff"/>' for x, y in pts)
    return (f'<svg viewBox="{vb}" height="230"><g transform="scale(1,-1)"><path d="{p.getCommands()}" fill="#111" opacity=".8"/>'
            f'<line x1="{xa}" x2="{xa}" y1="-300" y2="900" stroke="#1e6fff" stroke-width=".6"/>'
            f'<line x1="{xb}" x2="{xb}" y1="-300" y2="900" stroke="#e00" stroke-width=".6"/>{dots}</g></svg>')

LABEL = {"fix": ("고침", "#0a7d3b"), "same": ("같은 경우", "#c0392b"), "minor": ("애매", "#b7791f"), "ok": ("문제 아님", "#666")}
cards = []
for g, title, xa, xb, desc, kind in ITEMS:
    lab, col = LABEL[kind]
    if True:
        body = ('<div class="pair"><div><b>v1.32 (전)</b>' + svg(V132, g, xa, xb) + zoom(V132, g, xa, xb) + '</div>'
                '<div><b>v1.33 (후)</b>' + svg(V133, g, xa, xb) + zoom(V133, g, xa, xb) + '</div></div>')
    cards.append(f'<section><h2>{html.escape(title)} <span style="background:{col}">{lab}</span></h2><p>{html.escape(desc)}</p>{body}</section>')

out = os.path.join(ROOT, "out/font-update/v1.33-preview"); os.makedirs(out, exist_ok=True)
open(os.path.join(out, "axis.html"), "w", encoding="utf-8").write(f"""<!doctype html><meta charset="utf-8"><title>세로 줄기 축선 점검</title>
<style>body{{font-family:Pretendard,'Malgun Gothic',sans-serif;margin:32px;color:#222;background:#fff;max-width:1200px}}
section{{border-top:1px solid #ddd;padding:18px 0}}h2{{margin:0 0 6px;font-size:22px}}h2 span{{color:#fff;font-size:13px;padding:2px 8px;border-radius:10px;vertical-align:middle}}
p{{margin:0 0 10px;color:#444}}svg{{background:#fafafa;margin-right:10px;border:1px solid #eee}}.pair{{display:flex;gap:30px;flex-wrap:wrap}}.pair b{{display:block;margin-bottom:4px}}</style>
<h1>세로 줄기 축선 맞춤 (전용서체 v1.32 → v1.33)</h1>
<p>어느 쪽에 맞출지는 기둥 굵기 검토(2026-10-27) 기준을 따름: 대문자 129, 소문자 120, m 123. 두 값 중 이 굵기에 맞거나 더 가까운 쪽으로 맞춤. 글자 폭·여백·간격 규칙은 그대로.</p>
<p>파란 선 = 기준 줄기 위치, 빨간 선·빨간 원 = 어긋난 점. 오른쪽 작은 그림은 어긋난 자리 확대(가로세로 90 단위, 글자 높이 1000 기준).</p>
{''.join(cards)}""")
print(os.path.join(out, "axis.html"))
