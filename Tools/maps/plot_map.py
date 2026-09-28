"""Draw a generated map from above (footprints, roads, camps, objectives, map units) for review.

    python Tools/maps/plot_map.py <map.json> <out.png>
    python Tools/maps/plot_map.py --bases <map.json> <out.png>   (the map beside close-ups of its camps)

Lava, river water and fords are drawn as flat surfaces under everything else. Siege maps also
show the fortress: walls dark, gates as open yellow frames, the command HQ outlined in red, and
every map unit as a marker (team 0 blue, team 1 red) labelled with its kind.

Bases (see hardpoints.py) are drawn in the team's colour: the HQ as a filled square with its
facing, each tower hardpoint as a square as big as its size (L, M, S, darker the larger), numbered in
slot order within its size (most important first), each utility hardpoint as a diamond (U), the drop zone round the rally as a dashed circle, and the
outpost hardpoints at the capture points as yellow squares.

A siege map's fortress (its "fortress" block): the outer line as a dashed red line, the fortress's
tower hardpoints as red squares by size with their ring (1-3), utility hardpoints as green diamonds,
closed gates as solid red bars, the super-gun as a large star, and the line in (a rail line or a
runway) as a dashed grey track with its stop as a ringed dot.
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
           'ammo_dump': '#ff9000', 'vehicle_hangar': '#5a6a5a', 'razor_wire': '#b0b0b0', 'sandbag_wall': '#a8956a',
           'shield_generator': '#30c0ff', 'radar_station': '#ffffff', 'fortress_gate': '#ff2020'}
SURFACES = {'lava_pool': '#ff5a10', 'river_water': '#5a4a2a', 'river_ford': '#9a8a5a'}
OPEN = {'helipad': '#d8d8d0', 'base_gate': '#ffd000'}
LABELLED = {'hangar', 'highrise_a', 'highrise_b', 'skyscraper', 'parking_garage', 'temple_ruin', 'fuel_depot',
            'vehicle_hangar', 'ammo_dump', 'stilt_hut', 'control_tower', 'radar_dome'}
UNIT_LABELS = {'gun_turret': 'GT', 'aa_turret': 'AA', 'rocket_turret': 'RT', 'mg_bunker': 'MG',
               'artillery_emplacement': 'AR', 'guard_tower': 'TW'}
GROUND = {'volcanic': '#4a4442', 'jungle': '#4f6a3e', 'urban': '#8a8a86', 'snow': '#dfe6ea', 'desert': '#cfae7c'}


TEAM = {0: '#1f5bff', 1: '#e8321a'}
SLOT_METRES = {'small': 5.0, 'medium': 6.5, 'large': 9.0}
SLOT_SHADE = {'large': 0.85, 'medium': 0.6, 'small': 0.35}


def slot_metres(s):
    size = s.get('size', 8)
    return SLOT_METRES.get(size, 8.0) if isinstance(size, str) else float(size)


def draw_bases(ax, m, labels=True):
    """HQs, hardpoints, drop zones and outposts (see the notes at the top)."""
    import math
    for base in m.get('bases', []):
        colour = TEAM.get(base['team'], '#ffffff')
        hq = base['hq']
        ax.add_patch(patches.Rectangle((hq['x'] - 6, hq['z'] - 6), 12, 12, facecolor=colour, edgecolor='white', linewidth=1.5, zorder=12))
        h = math.radians(hq.get('heading', 0))
        ax.plot([hq['x'], hq['x'] + math.sin(h) * 9], [hq['z'], hq['z'] + math.cos(h) * 9], color='white', linewidth=1.5, zorder=13)
        ax.text(hq['x'], hq['z'], 'HQ', fontsize=7 if labels else 4, color='white', weight='bold', ha='center', va='center', zorder=14)
        seen = {}
        for s in base.get('slots', []):
            size = slot_metres(s)
            name = s.get('size') if isinstance(s.get('size'), str) else 'large'
            key = (s.get('kind'), name)
            seen[key] = seen.get(key, 0) + 1
            if s.get('kind') == 'utility':
                r = size / 2
                ax.add_patch(patches.Polygon([(s['x'], s['z'] - r), (s['x'] + r, s['z']), (s['x'], s['z'] + r), (s['x'] - r, s['z'])],
                                             closed=True, facecolor='#39d98a', edgecolor=colour, linewidth=1.5, zorder=12))
                tag = f'U{seen[key]}'
            else:
                ax.add_patch(patches.Rectangle((s['x'] - size / 2, s['z'] - size / 2), size, size, facecolor=colour,
                                               alpha=SLOT_SHADE.get(name, 0.55), edgecolor='white', linewidth=1.0, zorder=12))
                tag = f'{name[0].upper()}{seen[key]}'
            f = math.radians(s.get('facing', 0))
            ax.plot([s['x'], s['x'] + math.sin(f) * size * 0.6], [s['z'], s['z'] + math.cos(f) * size * 0.6], color='white',
                    linewidth=0.8, zorder=13)
            if labels:
                ax.text(s['x'], s['z'], tag, fontsize=5.5, color='black', weight='bold', ha='center', va='center', zorder=14)
    for t in m['teams']:
        ax.add_patch(patches.Circle((t['x'], t['z']), 16, fill=False, linestyle='--', linewidth=1.2,
                                    color=TEAM.get(t['team'], '#ffffff'), zorder=11))
        ax.plot([t['x']], [t['z']], marker='+', color=TEAM.get(t['team'], '#ffffff'), markersize=8, zorder=11)
    for pt in m.get('points', []):
        for s in pt.get('outpost', []):
            size = slot_metres(s)
            ax.add_patch(patches.Rectangle((s['x'] - size / 2, s['z'] - size / 2), size, size, facecolor='#ffd21a',
                                           edgecolor='black', linewidth=1.0, zorder=12))
            if labels and isinstance(s.get('size'), str):
                ax.text(s['x'], s['z'], s['size'][0].upper(), fontsize=5.5, color='black', weight='bold', ha='center',
                        va='center', zorder=14)


def draw_fortress(ax, m, half):
    import math
    f = m.get('fortress')
    if not f:
        return
    c = f.get('outerLine')
    if c is not None:
        ax.plot([c - half, half], [half, c - half], color='#ff3020', linestyle='--', linewidth=1.6, zorder=10)
    for s in f.get('slots', []):
        size = slot_metres(s)
        if s.get('kind') == 'utility':
            r = size / 2
            ax.add_patch(patches.Polygon([(s['x'], s['z'] - r), (s['x'] + r, s['z']), (s['x'], s['z'] + r), (s['x'] - r, s['z'])],
                                         closed=True, facecolor='#39d98a', edgecolor='#e8321a', linewidth=1.2, zorder=12))
        else:
            ax.add_patch(patches.Rectangle((s['x'] - size / 2, s['z'] - size / 2), size, size, facecolor='#e8321a',
                                           alpha=SLOT_SHADE.get(s.get('size'), 0.55), edgecolor='white', linewidth=0.8, zorder=12))
        ax.text(s['x'], s['z'], str(s.get('ring', '')), fontsize=5, color='white', weight='bold', ha='center', va='center', zorder=14)
    gun = f.get('superGun')
    if gun:
        ax.plot([gun['x']], [gun['z']], marker='*', markersize=16, color='#ff1010', markeredgecolor='white', zorder=13)
    line = f.get('arrival')
    if line:
        pts = line['path']
        ax.plot(pts[0::2], pts[1::2], color='#d0d0d0', linestyle='--', linewidth=3 if line['kind'] == 'rail' else 8, alpha=0.8, zorder=6)
        ax.plot([line['stop'][0]], [line['stop'][1]], marker='o', markersize=9, markerfacecolor='#ffe040', markeredgecolor='black', zorder=13)
    for p in m['props']:
        if p['def'] == 'fortress_gate':
            w, d = (10, 1.4) if p.get('rot', 0) % 180 == 0 else (1.4, 10)
            ax.add_patch(patches.Rectangle((p['x'] - w / 2, p['z'] - d / 2), w, d, color='#ff2020', zorder=6))


def main(src, out, bases=False):
    text = re.sub(r'^\s*//.*$', '', Path(src).read_text(encoding='utf-8'), flags=re.M)
    m = json.loads(text)
    half = m['size'] / 2
    if bases and m.get('bases'):
        fig, axes = plt.subplots(1, 1 + len(m['bases']), figsize=(10 + 7 * len(m['bases']), 10),
                                 gridspec_kw={'width_ratios': [10] + [7] * len(m['bases'])})
        for ax in axes:
            draw_map(ax, m, half)
            draw_bases(ax, m, labels=ax is not axes[0])
            for t in ax.texts:
                t.set_clip_on(True)
        axes[0].set_title(m['id'])
        for ax, base in zip(axes[1:], m['bases']):
            cx, cz = base['hq']['x'], base['hq']['z']
            span = 62
            ax.set_xlim(cx - span, cx + span)
            ax.set_ylim(cz - span, cz + span)
            towers = [s for s in base['slots'] if s.get('kind') != 'utility']
            sizes = ', '.join(f"{sum(1 for s in towers if s.get('size') == n)} {n}" for n in ('large', 'medium', 'small'))
            ax.set_title(f"team {base['team']} camp: towers {sizes}; {len(base['slots']) - len(towers)} utility")
        fig.savefig(out, dpi=80, bbox_inches='tight')
        plt.close(fig)
        return
    fig, ax = plt.subplots(figsize=(10, 10))
    draw_map(ax, m, half)
    draw_bases(ax, m, labels=False)
    draw_fortress(ax, m, half)
    ax.set_title(m['id'])
    fig.savefig(out, dpi=90, bbox_inches='tight')
    plt.close(fig)


def draw_map(ax, m, half):
    ax.set_facecolor(GROUND.get(m.get('theme'), '#8a9a70'))
    road_colour = '#3e3f41' if m.get('theme') == 'urban' else '#b8a47e'
    for road in m.get('roads', []):
        # In metres (a strip per segment, round at the joints), so close-ups show the true width.
        pts = road['points']
        half_width = road['width'] / 2
        for i in range(0, len(pts) - 2, 2):
            ax_, az, bx, bz = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
            length = ((bx - ax_) ** 2 + (bz - az) ** 2) ** 0.5 or 1.0
            nx, nz = -(bz - az) / length * half_width, (bx - ax_) / length * half_width
            ax.add_patch(patches.Polygon([(ax_ + nx, az + nz), (bx + nx, bz + nz), (bx - nx, bz - nz), (ax_ - nx, az - nz)],
                                         closed=True, color=road_colour, linewidth=0, zorder=1))
        for i in range(0, len(pts), 2):
            ax.add_patch(patches.Circle((pts[i], pts[i + 1]), half_width, color=road_colour, linewidth=0, zorder=1))

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


if __name__ == '__main__':
    if sys.argv[1] == '--bases':
        main(sys.argv[2], sys.argv[3], bases=True)
    else:
        main(sys.argv[1], sys.argv[2])
