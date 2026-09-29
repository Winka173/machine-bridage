"""Check sheet for the Base screen's map pictures (prompt 14 B.1-B.2).

Draws every Resources/UI/Bases/<map>.png small, with what its JSON says drawn on top: the
camp's edge (cyan), the drop zone (yellow ring), the HQ (white square), the slots from the
map file (dots by size: small, medium, large; utility slots cyan) and the enemy approach
arrows (red, the head on the camp's edge), so framing, orientation and arrows can be checked
at a glance. The projection is done here from the JSON's frame (centre, up, metres across and
down), independently of the game's BaseMapPicture, so the two can be compared.

    python Tools/maps/basemap_sheet.py [out.png]

Default output: Docs/ui-screens/basemaps-sheet.png.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASES = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Resources', 'UI', 'Bases')
MAPS = os.path.join(ROOT, 'Assets', 'MachineBrigade', 'Resources', 'Data', 'maps')

CELL_W, CELL_H, LABEL, GAP, COLUMNS = 480, 300, 26, 8, 4
DOT = {'small': 3.0, 'medium': 4.5, 'large': 6.0}


def load_json(path):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    return json.loads('\n'.join(line for line in text.split('\n') if not line.lstrip().startswith('//')))


def projector(data, width, height):
    cx, cz = data['centre']['x'], data['centre']['z']
    ux, uz = data['up']['x'], data['up']['z']
    n = math.hypot(ux, uz)
    ux, uz = ux / n, uz / n
    rx, rz = uz, -ux
    mw, mh = data['metresWide'], data['metresHigh']

    def at(x, z):
        dx, dz = x - cx, z - cz
        u = 0.5 + (dx * rx + dz * rz) / mw
        v = 0.5 - (dx * ux + dz * uz) / mh
        return u * width, v * height

    def direction(x, z):
        px, py = x * rx + z * rz, -(x * ux + z * uz)
        n = math.hypot(px, py) or 1.0
        return px / n, py / n

    return at, direction, width / mw


def arrow(draw, head, d, length, width, colour):
    hx, hy = head
    dx, dy = d
    tail = (hx - dx * length, hy - dy * length)
    wing = length * 0.42
    px, py = -dy, dx
    base = (hx - dx * wing, hy - dy * wing)
    draw.line([tail, base], fill=(0, 0, 0), width=width + 3)
    draw.line([tail, base], fill=colour, width=width)
    tip = [(hx, hy), (base[0] + px * wing * 0.6, base[1] + py * wing * 0.6), (base[0] - px * wing * 0.6, base[1] - py * wing * 0.6)]
    draw.polygon(tip, fill=colour, outline=(0, 0, 0))


def cell(map_id, font):
    data = load_json(os.path.join(BASES, map_id + '.json'))
    picture = Image.open(os.path.join(BASES, map_id + '.png')).convert('RGB').resize((CELL_W, CELL_H), Image.LANCZOS)
    draw = ImageDraw.Draw(picture, 'RGBA')
    at, direction, ppm = projector(data, CELL_W, CELL_H)

    outline = [at(p['x'], p['z']) for p in data['outline']]
    if len(outline) >= 3:
        draw.line(outline + [outline[0]], fill=(90, 220, 255, 200), width=1)

    dz = at(data['dropZone']['x'], data['dropZone']['z'])
    r = data['dropRadius'] * ppm
    draw.ellipse([dz[0] - r, dz[1] - r, dz[0] + r, dz[1] + r], outline=(255, 214, 60, 230), width=2)

    source = load_json(os.path.join(MAPS, map_id + '_conquest.json'))
    base = next(b for b in source['bases'] if b.get('team', 0) == 0)
    for s in base['slots']:
        x, y = at(s['x'], s['z'])
        size = s.get('size', 'large')
        rad = DOT.get(size, 6.0) if isinstance(size, str) else 3.0 + size * 0.35
        fill = (80, 230, 255) if s.get('kind') == 'utility' else (255, 255, 255)
        draw.ellipse([x - rad, y - rad, x + rad, y + rad], fill=fill, outline=(0, 0, 0), width=1)

    hx, hy = at(data['hq']['x'], data['hq']['z'])
    half = 7.0 * ppm
    draw.rectangle([hx - half, hy - half, hx + half, hy + half], outline=(255, 255, 255), width=2)
    fx, fy = direction(math.sin(math.radians(data['heading'])), math.cos(math.radians(data['heading'])))
    draw.line([(hx, hy), (hx + fx * half * 1.8, hy + fy * half * 1.8)], fill=(255, 255, 255), width=2)

    for a in data['arrows']:
        head = at(a['at']['x'], a['at']['z'])
        d = direction(a['dir']['x'], a['dir']['z'])
        arrow(draw, head, d, 14.0 * ppm + 10, 2 + min(3, a.get('routes', 1)), (235, 40, 40))

    out = Image.new('RGB', (CELL_W, CELL_H + LABEL), (18, 20, 23))
    out.paste(picture, (0, 0))
    label = (f"{map_id}   {len(data['arrows'])} arrows ({data['arrowsFrom']})   {data['metresWide']:.0f} x {data['metresHigh']:.0f} m"
             f"   brightness {data.get('brightness', 0):.2f}")
    ImageDraw.Draw(out).text((8, CELL_H + 5), label, fill=(230, 232, 235), font=font)
    return out


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'Docs', 'ui-screens', 'basemaps-sheet.png')
    ids = sorted(f[:-5] for f in os.listdir(BASES) if f.endswith('.json'))
    try:
        font = ImageFont.truetype('arial.ttf', 15)
    except OSError:
        font = ImageFont.load_default()
    rows = (len(ids) + COLUMNS - 1) // COLUMNS
    sheet = Image.new('RGB', (COLUMNS * (CELL_W + GAP) + GAP, rows * (CELL_H + LABEL + GAP) + GAP), (10, 11, 13))
    for i, map_id in enumerate(ids):
        c = cell(map_id, font)
        sheet.paste(c, (GAP + (i % COLUMNS) * (CELL_W + GAP), GAP + (i // COLUMNS) * (CELL_H + LABEL + GAP)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path)
    print(f'wrote {out_path}: {len(ids)} camps')


if __name__ == '__main__':
    main()
