"""Draw a generated map from above (footprints, roads, camps, objectives) for review.

    python Tools/maps/plot_map.py <map.json> <out.png>
"""
import json
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.patches as patches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_maps import PROPS, BUILDINGS  # noqa: E402

COLOURS = {'tree': '#3f6b3a', 'palm': '#5f8b3a', 'cactus': '#6f8b4a', 'mesa': '#b87444', 'snow_rock': '#9aa2a8',
           'pipeline': '#9ba49c', 'lamp_post': '#333333', 'jersey_barrier': '#aaaaaa', 'dock_bollards': '#444444',
           'market_stall': '#d9a060', 'car': '#c8382c', 'truck': '#c8382c', 'fence': '#86633f', 'hedge': '#4d7a3a',
           'stone_wall': '#8d958c', 'fuel_tank': '#e4e2d8', 'barrel': '#c2402a', 'ammo_crate': '#737a5c'}


def main(src, out):
    text = re.sub(r'^\s*//.*$', '', Path(src).read_text(encoding='utf-8'), flags=re.M)
    m = json.loads(text)
    half = m['size'] / 2
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('#8a9a70')
    for road in m.get('roads', []):
        pts = road['points']
        ax.plot(pts[0::2], pts[1::2], color='#b8a47e', linewidth=road['width'] * 2.6, solid_capstyle='round', zorder=1)
    for p in m['props']:
        d = PROPS[p['def']]
        w, dd = d['width'], d['depth']
        if p.get('rot', 0) % 180 == 90:
            w, dd = dd, w
        colour = COLOURS.get(p['def'], '#b25a40' if p['def'] in BUILDINGS else '#666666')
        ax.add_patch(patches.Rectangle((p['x'] - w / 2, p['z'] - dd / 2), w, dd, color=colour, zorder=3))
        if p['def'] in BUILDINGS and p['def'] not in ('fuel_tank', 'wall'):
            ax.text(p['x'], p['z'], p['def'][:4], fontsize=5, ha='center', va='center', zorder=4)
    for t in m['teams']:
        ax.add_patch(patches.Circle((t['x'], t['z']), 22, fill=False, color='#2060ff' if t['team'] == 0 else '#ff4020'))
    for pt in m.get('points', []):
        ax.add_patch(patches.Circle((pt['x'], pt['z']), pt['radius'], fill=False, color='#ffe060', linewidth=2))
    ax.set_xlim(-half, half)
    ax.set_ylim(-half, half)
    ax.set_aspect('equal')
    fig.savefig(out, dpi=90, bbox_inches='tight')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
