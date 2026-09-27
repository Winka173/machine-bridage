"""Draw a generated map from above (footprints, roads, camps, objectives, map units) for review.

    python Tools/maps/plot_map.py <map.json> <out.png>

Lava, river water and fords are drawn as flat surfaces under everything else. Siege maps also
show the fortress: walls dark, gates as open yellow frames, the command HQ outlined in red, and
every map unit as a marker (team 0 blue, team 1 red) labelled with its kind.
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
           'stone_wall': '#8d958c', 'fuel_tank': '#e4e2d8', 'barrel': '#c2402a', 'ammo_crate': '#737a5c',
           # Volcanic
           'basalt_rock_a': '#3a3634', 'basalt_rock_b': '#3a3634', 'basalt_rock_c': '#3a3634', 'obsidian_spire': '#1c1a22',
           'lava_vent': '#ff7a1a', 'charred_tree': '#4a3a30', 'volcanic_cliff': '#2c2624',
           # Jungle
           'jungle_tree_a': '#2f5a2a', 'jungle_tree_b': '#2f5a2a', 'jungle_tree_c': '#2f5a2a', 'bamboo_clump': '#7a9a3a',
           'fern_bush': '#4f8a3a', 'temple_ruin': '#8f8a6a', 'stilt_hut': '#9a7040',
           # Airbase
           'hangar': '#8a9496', 'control_tower': '#d0d0c8', 'parked_jet': '#e03a1a', 'fuel_truck': '#ff5a1a',
           'radar_dome': '#e8e8e0', 'revetment': '#7d7a70', 'runway_light': '#ffe040',
           # City
           'highrise_a': '#6a7a8a', 'highrise_b': '#6a7a8a', 'skyscraper': '#4a5a70', 'parking_garage': '#8a8a80',
           'billboard': '#e0b030', 'bus': '#e08a1a', 'traffic_light': '#20c040',
           # Siege
           'command_hq': '#b01010', 'base_wall': '#202020', 'floodlight_mast': '#ffffa0', 'fuel_depot': '#ff4a00',
           'ammo_dump': '#ff9000', 'vehicle_hangar': '#5a6a5a', 'razor_wire': '#b0b0b0', 'sandbag_wall': '#a8956a'}
SURFACES = {'lava_pool': '#ff5a10', 'river_water': '#5a4a2a', 'river_ford': '#9a8a5a'}
OPEN = {'helipad': '#d8d8d0', 'base_gate': '#ffd000'}
LABELLED = {'hangar', 'highrise_a', 'highrise_b', 'skyscraper', 'parking_garage', 'temple_ruin', 'fuel_depot',
            'vehicle_hangar', 'ammo_dump', 'stilt_hut', 'control_tower', 'radar_dome'}
UNIT_LABELS = {'gun_turret': 'GT', 'aa_turret': 'AA', 'rocket_turret': 'RT', 'mg_bunker': 'MG',
               'artillery_emplacement': 'AR', 'guard_tower': 'TW'}
GROUND = {'volcanic': '#4a4442', 'jungle': '#4f6a3e', 'urban': '#8a8a86', 'snow': '#dfe6ea', 'desert': '#cfae7c'}


def main(src, out):
    text = re.sub(r'^\s*//.*$', '', Path(src).read_text(encoding='utf-8'), flags=re.M)
    m = json.loads(text)
    half = m['size'] / 2
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor(GROUND.get(m.get('theme'), '#8a9a70'))
    road_colour = '#3e3f41' if m.get('theme') == 'urban' else '#b8a47e'
    for road in m.get('roads', []):
        pts = road['points']
        ax.plot(pts[0::2], pts[1::2], color=road_colour, linewidth=road['width'] * 2.6, solid_capstyle='butt', zorder=1)

    def footprint(p):
        d = PROPS[p['def']]
        w, dd = d['width'], d['depth']
        if p.get('rot', 0) % 180 == 90:
            w, dd = dd, w
        return p['x'] - w / 2, p['z'] - dd / 2, w, dd

    for p in m['props']:
        x, z, w, dd = footprint(p)
        kind = p['def']
        if kind in SURFACES:
            ax.add_patch(patches.Rectangle((x, z), w, dd, color=SURFACES[kind], zorder=2, linewidth=0))
        elif kind in OPEN:
            ax.add_patch(patches.Rectangle((x, z), w, dd, fill=False, edgecolor=OPEN[kind], linewidth=1.5, zorder=4))
        else:
            colour = COLOURS.get(kind, '#b25a40' if kind in BUILDINGS else '#666666')
            ax.add_patch(patches.Rectangle((x, z), w, dd, color=colour, zorder=3))
            if (kind in BUILDINGS and kind not in ('fuel_tank', 'wall')) or kind in LABELLED:
                ax.text(p['x'], p['z'], kind[:4], fontsize=5, ha='center', va='center', zorder=4)
        if kind == 'command_hq':
            ax.add_patch(patches.Rectangle((x - 1.5, z - 1.5), w + 3, dd + 3, fill=False, edgecolor='#ff2020',
                                           linewidth=2.5, zorder=5))
            ax.text(p['x'], p['z'], 'HQ', fontsize=11, color='white', weight='bold', ha='center', va='center', zorder=6)
    for u in m.get('units', []):
        colour = '#2060ff' if u['team'] == 0 else '#ff2a10'
        ax.add_patch(patches.Circle((u['x'], u['z']), 2.0, color=colour, zorder=7))
        ax.text(u['x'], u['z'] + 2.8, UNIT_LABELS.get(u['def'], u['def'][:2]), fontsize=6, color=colour, weight='bold',
                ha='center', va='bottom', zorder=7)
    if m.get('boundary'):
        # Outside the outline is terrain: shade it and draw the edge.
        flat = m['boundary']
        poly = list(zip(flat[0::2], flat[1::2]))
        outer = [(-half, -half), (half, -half), (half, half), (-half, half)]
        from matplotlib.path import Path as MPath
        codes = [MPath.MOVETO] + [MPath.LINETO] * 3 + [MPath.CLOSEPOLY] + [MPath.MOVETO] + [MPath.LINETO] * (len(poly) - 1) + [MPath.CLOSEPOLY]
        verts = outer + [outer[0]] + poly[::-1] + [poly[-1]]
        ax.add_patch(patches.PathPatch(MPath(verts, codes), facecolor='#3b3a36', alpha=0.85, edgecolor='none', zorder=8))
        ax.plot([x for x, _ in poly] + [poly[0][0]], [z for _, z in poly] + [poly[0][1]], color='#f0e8d0', linewidth=1.2, zorder=9)
    for t in m['teams']:
        ax.add_patch(patches.Circle((t['x'], t['z']), 22, fill=False, color='#2060ff' if t['team'] == 0 else '#ff4020'))
    for pt in m.get('points', []):
        ax.add_patch(patches.Circle((pt['x'], pt['z']), pt['radius'], fill=False, color='#ffe060', linewidth=2))
    ax.set_xlim(-half, half)
    ax.set_ylim(-half, half)
    ax.set_aspect('equal')
    ax.set_title(m['id'])
    fig.savefig(out, dpi=90, bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
