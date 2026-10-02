"""Prompt 34 L7: separable parts for the wreck breakup by class (DECISIONS "Prompt 34 L5/L6/L7").

A wreck breaks up by its class (Scripts/Game/Effects/WreckBreakup.cs), from `Part_*` nodes, the runtime's rigid groups
(ModelLibrary.PartPattern, letters only after "Part_"). The classes that lacked parts get them here, after each target's
own builder (and its high-detail twin's), without changing a vertex: geometry the builder made is MOVED under a new pivot.

* Wheeled vehicles: `Part_wheel` (the front left wheel) and `Part_wheelb` (the rear right one), each pivoting at its centre:
  the tyre, rim and hub pieces (connected pieces of the builder's Tyres / Wheels / Rims / Hubs meshes) whose centres meet.
* Fixed-wing aircraft: `Part_wing`, the left wing outboard of the fuselage (the faces whose centre lies left of the
  fuselage's half width, estimated from the nose, ahead of the tailplanes; a flying wing along its whole length),
  pivoting at its root; with it go what hangs under it (pylons, missiles, nacelles, lights). `Part_tail` (the rear 38 %
  of a fighter, for breaking in two) is written but not used: it put the Su-27 over its renderer hard cap.

Helicopters need nothing: their Rotor and Tail_rotor are already their own nodes. Tanks have their Turret; trucks,
artillery, drones and ships break up without parts (cargo and ammunition blasts, ShipSinking).
"""
import re

import bmesh
from mathutils import Vector

import frontier_kit as kit

WHEELED = ['armored_car', 'combat_wreck_car', 'coastal_ashm_vehicle', 'fibre_fpv_carrier', 'fpv_carrier',
           'ground_cruise_missile_vehicle', 'heavy_aa', 'interceptor_drone_vehicle', 'iron_beam', 'long_sam',
           'microwave_vehicle', 'nlos_atgm_vehicle', 'radar_scout', 'radar_support_vehicle', 'recoilless_jeep',
           'rocket_technical', 'scout_jeep', 'shorad_vehicle', 'towed_at_gun', 'vbied', 'wheeled_gun', 'zu23_technical']
FIGHTERS = ['attack_jet', 'fighter_jet', 'stealth_fighter', 'glide_bomber', 'interceptor_jet', 'prop_attack_plane']
# Flying wings: their swept wing reaches the rear, so the left wing is cut along its whole length (no tailplanes).
FLYING_WINGS = ['stealth_bomber', 'stealth_naval_strike']
BIG_AIRCRAFT = ['heavy_bomber', 'stealth_bomber', 'sky_gunship', 'swarm_carrier', 'recon_jet', 'stealth_naval_strike',
                'aerial_tanker']

WHEEL_NAME = re.compile(r'^(tyres?|tires?|wheels?|rims?|hubs?|hub_caps?|wheel_[a-z]+)$', re.I)
SAME_WHEEL = 0.3      # m: pieces whose centres are closer than this are one wheel
MIN_WHEEL = 0.3       # m: a wheel is at least this tall
TAIL_SHARE = 0.38     # the fighters' tail: the rear share of the length
TAILPLANES = 0.22     # the wing stops ahead of the rear share where the tailplanes are
# Meshes the runtime finds by name (bombs that drop, guns that recoil, parachutes...) stay where their builder put them.
KEEP = re.compile(r'^(bombs|pump_beam|erector|searchlight|lift|blade|parachute)', re.I)


def _kept(name):
    return bool(KEEP.match(name) or kit.RUNTIME.match(name) or kit.RIG.match(name))


def targets():
    out = {}
    for name in WHEELED:
        out[name] = ('wheels',)
    # Fighters lose a wing (the prompt's first choice). The second, the fuselage breaking in two (`add_wing_tail(tail=True)`,
    # `Part_tail`), put the Su-27 over its renderer hard cap (47 of 44; glb_check), so it is not built.
    for name in FIGHTERS:
        out[name] = ('wing',)
    for name in BIG_AIRCRAFT:
        out[name] = ('wing', 'whole') if name in FLYING_WINGS else ('wing',)
    return out


def _components(bm):
    bm.verts.index_update()
    seen = set()
    out = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack, piece = [v], []
        seen.add(v.index)
        while stack:
            u = stack.pop()
            piece.append(u)
            for e in u.link_edges:
                w = e.other_vert(u)
                if w.index not in seen:
                    seen.add(w.index)
                    stack.append(w)
        out.append(piece)
    return out


def _copy_faces(a, key, faces, pivot, centre):
    """Copies `faces` of shape `key` into the same-named shape under `pivot` (local to `centre`), with their vertex layers."""
    name, mat, parent = key
    src = a.shapes[key]
    m = a._world(parent)
    dst = a.part(name, mat, pivot, flat=getattr(src, 'flat', False))
    layers = [(l, dst.bm.verts.layers.float.get(l.name) or dst.bm.verts.layers.float.new(l.name)) for l in src.bm.verts.layers.float]
    vmap = {}
    for f in faces:
        for v in f.verts:
            if v not in vmap:
                nv = dst.bm.verts.new((m @ v.co) - centre)
                for ls, ld in layers:
                    nv[ld] = v[ls]
                vmap[v] = nv
    for f in faces:
        try:
            dst.bm.faces.new([vmap[v] for v in f.verts])
        except ValueError:  # a duplicate face: the copy has it already
            pass


def _move_pieces(a, key, piece_verts, pivot, centre):
    src = a.shapes[key]
    faces = list({f for v in piece_verts for f in v.link_faces})
    _copy_faces(a, key, faces, pivot, centre)
    bmesh.ops.delete(src.bm, geom=list(piece_verts), context='VERTS')


def _move_faces(a, key, faces, pivot, centre):
    if not faces:
        return
    _copy_faces(a, key, faces, pivot, centre)
    bmesh.ops.delete(a.shapes[key].bm, geom=list(faces), context='FACES')


def add_wheels(a):
    found = []  # (height, key, verts, lo, hi)
    for key, shape in list(a.shapes.items()):
        name, mat, parent = key
        if not WHEEL_NAME.match(name) or not shape.bm.verts:
            continue
        if parent is not None and a._moving(parent):
            continue
        m = a._world(parent)
        for piece in _components(shape.bm):
            pts = [m @ v.co for v in piece]
            lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
            hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
            found.append((hi.z - lo.z, key, piece, lo, hi))
    # The biggest pieces (the tyres) found the wheels; a rim, hub or bolt joins the wheel whose box holds its centre.
    groups = []  # [centre, [(key, verts)], height, lo, hi]
    pad = Vector((0.05, 0.05, 0.05))
    for height, key, piece, lo, hi in sorted(found, key=lambda t: -t[0]):
        c = (lo + hi) * 0.5
        for g in groups:
            if all(g[3][i] - pad[i] <= c[i] <= g[4][i] + pad[i] for i in range(3)) or (g[0] - c).length < SAME_WHEEL:
                g[1].append((key, piece))
                break
        else:
            groups.append([c, [(key, piece)], height, lo, hi])
    wheels = [g for g in groups if g[2] >= MIN_WHEEL and abs(g[0].x) > 0.2]
    left = [g for g in wheels if g[0].x < 0]
    right = [g for g in wheels if g[0].x > 0]
    if not left or not right:
        print(f'P34_PARTS {a.name}: wheels: {len(left)} left, {len(right)} right, nothing to separate')
        return
    front_left = min(left, key=lambda g: g[0].y)   # the front is -Y
    rear_right = max(right, key=lambda g: g[0].y)
    for pivot, g in (('Part_wheel', front_left), ('Part_wheelb', rear_right)):
        a.pivot(pivot, tuple(g[0]))
        for key, piece in g[1]:
            _move_pieces(a, key, piece, pivot, g[0])
    print(f'P34_PARTS {a.name}: Part_wheel at {tuple(round(x, 2) for x in front_left[0])}, '
          f'Part_wheelb at {tuple(round(x, 2) for x in rear_right[0])} ({len(wheels)} wheels)')


def add_wing_tail(a, tail, whole=False):
    keys = [k for k, s in a.shapes.items() if k[2] is None and s.bm.faces and not _kept(k[0])]
    pts = [v.co for k in keys for v in a.shapes[k].bm.verts]
    if not pts:
        return
    ymin, ymax = min(p.y for p in pts), max(p.y for p in pts)
    length = ymax - ymin
    span = max(abs(p.x) for p in pts)
    nose = sorted(abs(p.x) for p in pts if p.y < ymin + 0.2 * length)
    half = nose[int(len(nose) * 0.9)] if nose else 0.1 * span
    cut = max(half * 1.15 + 0.05, 0.12 * span)
    plane_from = ymax + 1.0 if whole else ymax - TAILPLANES * length
    tail_from = ymin + (1 - TAIL_SHARE) * length
    wing, rear = {}, {}
    for k in keys:
        for f in a.shapes[k].bm.faces:
            c = f.calc_center_median()
            if c.x < -cut and c.y < plane_from:
                wing.setdefault(k, []).append(f)
            elif tail and c.y > tail_from:
                rear.setdefault(k, []).append(f)
    moved = sum(len(v) for v in wing.values())
    if moved == 0:
        print(f'P34_PARTS {a.name}: no wing faces outboard of {cut:.2f} m')
    else:
        wc = [f.calc_center_median() for fs in wing.values() for f in fs]
        root = Vector((-cut, sum(c.y for c in wc) / len(wc), sum(c.z for c in wc) / len(wc)))
        a.pivot('Part_wing', tuple(root))
        for k, fs in wing.items():
            _move_faces(a, k, fs, 'Part_wing', root)
        print(f'P34_PARTS {a.name}: Part_wing: {moved} faces left of x {-cut:.2f} (span {span:.2f}, fuselage {half:.2f})')
    if tail:
        n = sum(len(v) for v in rear.values())
        if n:
            rc = [f.calc_center_median() for fs in rear.values() for f in fs]
            root = Vector((0.0, tail_from, sum(c.z for c in rc) / len(rc)))
            a.pivot('Part_tail', tuple(root))
            for k, fs in rear.items():
                _move_faces(a, k, fs, 'Part_tail', root)
            print(f'P34_PARTS {a.name}: Part_tail: {n} faces behind y {tail_from:.2f}')


def add_parts(a, kinds):
    if 'wheels' in kinds:
        add_wheels(a)
    if 'wing' in kinds:
        add_wing_tail(a, 'tail' in kinds, 'whole' in kinds)


def wrap(builders):
    """The builders with the separable parts added after each target's own build (and its high-detail twin's)."""
    out = dict(builders)
    for name, kinds in targets().items():
        for key in (name, f'{name}_hd'):
            if key not in out:
                continue
            build, options = out[key]

            def run(a, build=build, kinds=kinds, **kw):
                build(a, **kw)
                add_parts(a, kinds)
            run.__name__ = getattr(build, '__name__', key)
            run.__doc__ = (build.__doc__ or '') + '\n\nPrompt 34 L7: separable wreck parts.'
            out[key] = (run, options)
    return out
