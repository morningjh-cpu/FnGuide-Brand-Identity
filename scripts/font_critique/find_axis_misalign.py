"""세로 줄기(축선)가 1~4 단위 어긋난 글자 찾기.
같은 글자 안에서 '세로로 곧은 부분'(세로 직선 끝점, 세로 접선 곡선 끝점)의 x값을 모아
서로 1~4 단위만 다른 값이 있으면(의도한 차이로 보기엔 너무 작음) 보고한다.
또 거의 세로인데 살짝 기운 직선(가로 1~5, 세로 40 이상)도 보고한다.
사용: py scripts/font_critique/find_axis_misalign.py [서체 경로]
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

path = sys.argv[1] if len(sys.argv) > 1 else 'out/font-update/v1.32/fonts/FnGuideLogotype-Regular.otf'
f = TTFont(path)
gs = f.getGlyphSet()
cmap = {v: k for k, v in f.getBestCmap().items()}

def vert_points(rec):
    pts = []  # (x, y)
    tilts = []
    cur = start = None
    for op, a in rec.value:
        if op == 'moveTo':
            cur = start = a[0]
        elif op == 'lineTo':
            p = a[0]
            dx, dy = p[0] - cur[0], p[1] - cur[1]
            if dx == 0 and abs(dy) >= 20:
                pts += [cur, p]
            elif 0 < abs(dx) <= 5 and abs(dy) >= 40:
                tilts.append((cur, p))
            cur = p
        elif op == 'curveTo':
            c1, c2, p = a
            if c1[0] == cur[0] and c1[1] != cur[1]:
                pts.append(cur)
            if c2[0] == p[0] and c2[1] != p[1]:
                pts.append(p)
            cur = p
        elif op == 'closePath':
            if cur and start and cur != start:
                dx, dy = start[0] - cur[0], start[1] - cur[1]
                if dx == 0 and abs(dy) >= 20: pts += [cur, start]
                elif 0 < abs(dx) <= 5 and abs(dy) >= 40: tilts.append((cur, start))
    return pts, tilts

for name in f.getGlyphOrder():
    rec = RecordingPen(); gs[name].draw(rec)
    if not rec.value: continue
    pts, tilts = vert_points(rec)
    xs = sorted(set(p[0] for p in pts))
    near = [(a, b) for i, a in enumerate(xs) for b in xs[i+1:] if 1 <= b - a <= 4]
    if near or tilts:
        u = cmap.get(name)
        ch = chr(u) if u else ''
        msg = []
        for a, b in near:
            ya = sorted(p[1] for p in pts if p[0] == a); yb = sorted(p[1] for p in pts if p[0] == b)
            msg.append(f'x {a}(y{ya}) vs {b}(y{yb})')
        for s, e in tilts:
            msg.append(f'기운 선 {s}->{e}')
        print(f'{name} [{ch}] : ' + ' | '.join(msg))
