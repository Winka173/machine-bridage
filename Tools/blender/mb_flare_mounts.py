"""Fix prompt L4 (DECISIONS "Sửa lỗi tổng hợp L4 / L5 / L6"): the flare launch points, `Mount_Flare_*` empties, on every
unit with flares, added after each one's own builder (and its high-detail twin's), without changing a vertex.

The flares leave from these points (Scripts/Game/Views/VehicleView.FxPoints.cs FlarePoints, EffectsDirector.Munitions.cs
FlareSalvo): the rear fuselage or tail boom on both sides and the tail root, as on the real aircraft:

* `Mount_Flare_L` / `Mount_Flare_R`: at the middle of the model's prompt 29 dispenser tubes (`Flares`) on each side where it
  has them; else on the rear fuselage's sides, 68 % of the way back, at the fuselage's half width (from its nose, as
  mb_p34_parts does) and its middle height there.
* `Mount_Flare_L2` / `Mount_Flare_R2`: a big aircraft's second tube row (the "angel wings" comes from both rows at once).
* `Mount_Flare_TL` / `Mount_Flare_TR`: the tail root, 86 % of the way back, close beside the centre line.

Never a bare `Mount_Flare`: the runtime reads `Mount_<letters>` as a weapon mount's yaw pivot (ModelLibrary.MountPattern,
glb_analyze's 'mount', MuzzleGeometryAudit's groups); the `_L` / `_R` / `_TL` suffix keeps these out of all three (the
pattern allows letters only before an optional `.001`). They are plain empties (no mesh), so they add no triangle or
renderer; the runtime keeps every transform when it merges a template's meshes.

Blender: x across (+ right), y along (+ the tail: the nose is -Y), z up.
"""
import re

FLARE_UNITS = ['attack_helicopter', 'gunship_heli', 'scout_heli', 'attack_jet', 'heavy_bomber', 'sky_gunship', 'fighter_jet',
               'stealth_fighter', 'swarm_carrier', 'elite_attack_helicopter', 'glide_bomber', 'interceptor_jet',
               'prop_attack_plane', 'light_attack_heli', 'twin_rotor_gunship', 'aerial_tanker', 'heavy_lift_helicopter',
               'mega_gunship', 'drone_mothership', 'sky_fortress', 'morrigan']

TUBES = re.compile(r'^flares$', re.I)
ROW_GAP = 0.15      # m along the hull: tubes farther apart are a second row (ModelLibrary.EffectRowGap)
SIDE_BACK = 0.68    # the rear fuselage's points, share of the length from the nose
TAIL_BACK = 0.86    # the tail root's
# What is never the fuselage: spinning or moving parts and the runtime's own pieces.
SKIP = re.compile(r'^(rotor|tail_rotor|propeller|blades|flares|flares_glow|beacon|antenna|missiles?|bombs|pods?|rocket)', re.I)


def _points(a, test):
    """World positions of the vertices of the asset's static shapes whose name passes `test`."""
    pts = []
    for key, shape in a.shapes.items():
        name, _, parent = key
        if not shape.bm.verts or not test(name):
            continue
        if parent is not None and a._moving(parent):
            continue
        m = a._world(parent)
        pts += [m @ v.co for v in shape.bm.verts]
    return pts


def _rows(pts):
    """Tube vertices split into rows along the hull: the mean point of each."""
    pts = sorted(pts, key=lambda p: p.y)
    rows, start = [], 0
    for i in range(1, len(pts) + 1):
        if i < len(pts) and pts[i].y - pts[i - 1].y < ROW_GAP:
            continue
        row = pts[start:i]
        start = i
        rows.append(sum(row, row[0] * 0) / len(row))
    return rows


def _station(body, y, half):
    """The fuselage's middle height at station `y` (its vertices within `half` x 1.3 of the centre line)."""
    length = max(p.y for p in body) - min(p.y for p in body)
    reach = max(0.12, 0.05 * length)
    near = sorted(p.z for p in body if abs(p.y - y) < reach and abs(p.x) <= half * 1.3)
    if not near:
        near = sorted(p.z for p in body)
    return near[len(near) // 2]


def add_mounts(a):
    body = _points(a, lambda n: not SKIP.match(n))
    if not body:
        print(f'FLARE_MOUNTS {a.name}: no static geometry, nothing added')
        return
    ymin, ymax = min(p.y for p in body), max(p.y for p in body)
    length = ymax - ymin
    nose = sorted(abs(p.x) for p in body if p.y < ymin + 0.2 * length)
    span = max(abs(p.x) for p in body)
    half = nose[int(len(nose) * 0.9)] if nose else 0.1 * span
    half = max(0.08, min(half, 0.3 * span if span > 0 else half))
    placed = []
    tubes = _points(a, lambda n: TUBES.match(n))
    for side, tag in ((-1, 'L'), (1, 'R')):
        rows = _rows([p for p in tubes if p.x * side > 0.01])
        if rows:
            for i, c in enumerate(rows[:2]):
                name = f'Mount_Flare_{tag}{"" if i == 0 else "2"}'
                a.pivot(name, (c.x, c.y, c.z))
                placed.append(name)
        else:
            y = ymin + SIDE_BACK * length
            name = f'Mount_Flare_{tag}'
            a.pivot(name, (side * half, y, _station(body, y, half)))
            placed.append(name)
    y = ymin + TAIL_BACK * length
    z = _station(body, y, half)
    for side, tag in ((-1, 'TL'), (1, 'TR')):
        name = f'Mount_Flare_{tag}'
        a.pivot(name, (side * max(0.05, half * 0.45), y, z))
        placed.append(name)
    print(f'FLARE_MOUNTS {a.name}: {", ".join(placed)} (length {length:.2f}, half width {half:.2f}, tubes {len(tubes)})')


def wrap(builders):
    """The builders with the flare points added after each flare unit's own build (and its high-detail twin's)."""
    out = dict(builders)
    for name in FLARE_UNITS:
        for key in (name, f'{name}_hd'):
            if key not in out:
                continue
            build, options = out[key]

            def run(a, build=build, **kw):
                build(a, **kw)
                add_mounts(a)
            run.__name__ = getattr(build, '__name__', key)
            run.__doc__ = (build.__doc__ or '') + '\n\nFix prompt L4: Mount_Flare_* points.'
            out[key] = (run, options)
    return out
