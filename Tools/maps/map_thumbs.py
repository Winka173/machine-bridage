"""Battlefield pictures for the menus (Field Command 2.0): each map from above, drawn from its data.

    python Tools/maps/map_thumbs.py            (every map with a _conquest file)
    python Tools/maps/map_thumbs.py redrock     (one map)

Writes Assets/MachineBrigade/Resources/UI/Maps/<map>.png, 640 x 360: the map's middle band seen from
above in its theme's colours (ground, water, roads, buildings, trees, rock), the capture points as
rings and the two camps in the team colours (ours blue, theirs red), the land outside the map's
outline shaded. The map dropdown, the chapter cards, the mission detail and the briefing card show
them (MapArt). Re-run after changing a map in build_maps.py.
"""
import json
import random
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_maps import PROPS, BUILDINGS  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MAPS = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'Data' / 'maps'
OUT = ROOT / 'Assets' / 'MachineBrigade' / 'Resources' / 'UI' / 'Maps'
SIZE = 900          # the square drawn before cropping
WIDTH, HEIGHT = 640, 360

GROUND = {'temperate': (104, 120, 78), 'desert': (196, 166, 116), 'snow': (214, 222, 226), 'harbor': (112, 122, 108),
          'volcanic': (70, 64, 62), 'jungle': (74, 100, 60), 'urban': (122, 124, 120)}
ROAD = {'urban': (62, 63, 65), 'snow': (170, 172, 168), 'desert': (170, 142, 98)}
WATER = {'jungle': (80, 70, 42), 'volcanic': (230, 90, 20)}
TREES = {'tree', 'palm', 'cactus', 'pine', 'jungle_tree_a', 'jungle_tree_b', 'jungle_tree_c', 'bamboo_clump', 'fern_bush',
         'charred_tree', 'dead_tree', 'hedge', 'bush'}
ROCKS = {'mesa', 'snow_rock', 'basalt_rock_a', 'basalt_rock_b', 'basalt_rock_c', 'obsidian_spire', 'volcanic_cliff', 'boulders',
         'cliff', 'rock'}
ALLY = (108, 192, 255)
ENEMY = (224, 81, 58)
BONE = (233, 230, 223)


def shade(colour, k):
    return tuple(max(0, min(255, int(c * k))) for c in colour)


def load(path):
    return json.loads(re.sub(r'^\s*//.*$', '', path.read_text(encoding='utf-8'), flags=re.M))


def draw(map_id):
    m = load(MAPS / f'{map_id}_conquest.json')
    theme = m.get('theme', 'temperate')
    size = m['size']
    half = size / 2
    scale = SIZE / size
    ground = GROUND.get(theme, GROUND['temperate'])

    def px(x, z):
        return ((x + half) * scale, (half - z) * scale)

    img = Image.new('RGB', (SIZE, SIZE), ground)
    # A little texture in the ground: soft blotches a shade lighter and darker.
    noise = Image.new('L', (SIZE // 12, SIZE // 12))
    rnd = random.Random(map_id)
    noise.putdata([rnd.randint(0, 255) for _ in range(noise.width * noise.height)])
    noise = noise.resize((SIZE, SIZE), Image.BICUBIC).filter(ImageFilter.GaussianBlur(10))
    img = Image.composite(Image.new('RGB', (SIZE, SIZE), shade(ground, 1.08)), Image.new('RGB', (SIZE, SIZE), shade(ground, 0.92)), noise)
    d = ImageDraw.Draw(img, 'RGBA')

    def rect(p):
        spec = PROPS.get(p['def'])
        if spec is None:
            return None
        w, dd = spec['width'], spec['depth']
        if p.get('rot', 0) % 180 == 90:
            w, dd = dd, w
        a = px(p['x'] - w / 2, p['z'] + dd / 2)
        b = px(p['x'] + w / 2, p['z'] - dd / 2)
        return [a, b]

    # Water and lava first, under everything.
    for p in m['props']:
        if p['def'] in ('river_water', 'river_ford', 'lava_pool'):
            r = rect(p)
            if r is None:
                continue
            water = (230, 90, 20) if p['def'] == 'lava_pool' else WATER.get(theme, (47, 95, 122))
            if p['def'] == 'river_ford':
                water = shade(water, 1.25)
            d.rectangle(r, fill=water)
    # Roads.
    road = ROAD.get(theme, shade(ground, 1.18))
    for r in m.get('roads', []):
        pts = r['points']
        width = max(2, int(r['width'] * scale))
        line = [px(pts[i], pts[i + 1]) for i in range(0, len(pts), 2)]
        d.line(line, fill=road, width=width, joint='curve')
        for x, y in line:
            d.ellipse([x - width / 2, y - width / 2, x + width / 2, y + width / 2], fill=road)
    # Props: trees as round dark blots, rock grey, buildings as roofs, the rest as small marks.
    for p in m['props']:
        kind = p['def']
        if kind in ('river_water', 'river_ford', 'lava_pool'):
            continue
        r = rect(p)
        if r is None:
            continue
        if kind in TREES or 'tree' in kind:
            (x0, y0), (x1, y1) = r
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            rad = max(2.0, (x1 - x0 + y1 - y0) / 3)
            d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=shade(ground, 0.62) + (230,))
        elif kind in ROCKS or 'rock' in kind or 'cliff' in kind:
            d.rectangle(r, fill=shade((120, 118, 112), 0.9 if theme != 'snow' else 1.2) + (235,))
        elif kind in BUILDINGS or kind in ('hangar', 'highrise_a', 'highrise_b', 'skyscraper', 'parking_garage', 'command_hq', 'base_wall'):
            d.rectangle(r, fill=(58, 60, 64, 245) if theme == 'urban' else (86, 80, 72, 245))
            (x0, y0), (x1, y1) = r
            d.rectangle([x0, y0, x1, y1], outline=(30, 32, 34, 180))
        else:
            d.rectangle(r, fill=shade(ground, 0.8) + (170,))
    # Outside the outline is terrain: shaded.
    if m.get('boundary'):
        flat = m['boundary']
        poly = [px(flat[i], flat[i + 1]) for i in range(0, len(flat), 2)]
        mask = Image.new('L', (SIZE, SIZE), 255)
        ImageDraw.Draw(mask).polygon(poly, fill=0)
        img = Image.composite(Image.new('RGB', (SIZE, SIZE), shade(ground, 0.45)), img, mask.filter(ImageFilter.GaussianBlur(4)))
        d = ImageDraw.Draw(img, 'RGBA')
    # Capture points and camps.
    for pt in m.get('points', []):
        x, y = px(pt['x'], pt['z'])
        rad = max(6, pt['radius'] * scale)
        d.ellipse([x - rad, y - rad, x + rad, y + rad], outline=BONE + (230,), width=3)
    for t in m['teams']:
        x, y = px(t['x'], t['z'])
        colour = ALLY if t['team'] == 0 else ENEMY
        d.rectangle([x - 9, y - 9, x + 9, y + 9], fill=colour + (235,), outline=(16, 19, 23, 255), width=2)
    # The middle band, 16:9, softened at the edges.
    top = (SIZE - SIZE * HEIGHT // WIDTH) // 2
    img = img.crop((0, top, SIZE, top + SIZE * HEIGHT // WIDTH)).resize((WIDTH, HEIGHT), Image.LANCZOS)
    vignette = Image.new('L', (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(vignette).rectangle([18, 12, WIDTH - 18, HEIGHT - 12], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(22))
    img = Image.composite(img, Image.new('RGB', (WIDTH, HEIGHT), shade(ground, 0.55)), vignette)
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / f'{map_id}.png', optimize=True)
    return OUT / f'{map_id}.png'


def main():
    ids = sys.argv[1:] or sorted(p.name[:-len('_conquest.json')] for p in MAPS.glob('*_conquest.json'))
    for map_id in ids:
        print('wrote', draw(map_id))


if __name__ == '__main__':
    main()
