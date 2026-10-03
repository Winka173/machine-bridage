"""Play-test 13 follow-up (lane B), DECISIONS "Play-test 13 follow-up (lane B)": applied after every other builder and
wrapper (build_assets.all_builders), without changing what the builders draw except where named below.

1. Gun towers get a baked `Elevation` pivot under `Turret` at the gun's trunnion, carrying the parts that really elevate
   with the gun (barrels, brakes, mantlet or cradle, breech, recuperators, coax, the sight fixed to the cradle) and their
   muzzles. Real life: a gun elevates on its trunnions with its whole cradle; the shield, the carriage, the yoke and the
   crew seats stay. Before, the runtime built the pivot itself (ModelLibrary.AddElevation) from the barrel parts only
   (Main_cannon, Muzzle_brake, Coax), guessed it from their bounds (6 % in from their rear, 30 % up), and left cradles,
   jackets, sleeves, brake bands and recuperators standing when the barrel rose. Node names and pivots are kept: parts
   only move under the new pivot (their world position is unchanged). The view drives a baked pivot exactly as the one
   it builds (VehicleView.Elevate; ModelLibrary measures its rest pitch from Muzzle_main).
2. Launchers whose rounds are visible get indexed round nodes (`Round_N`, `Missile_N_*`, `Rocket_N`) so VehicleView.Loaded
   hides fired rounds: a cover or nose per cell, grouped so a model shows a handful of groups (draw calls).
3. manpads_tower and aa_turret_b: their second muzzles were exported as `Muzzle_missile__001` (no kit rename), which the
   runtime does not read: renamed `.001`.
4. behemoth: mount 6 (now the 120 mm hull gun's shells, play-test 13 lane C) is the third `missile` mount in the data, so
   it fired from the left missile rack's muzzle; a `Muzzle_missile.002` at the hull gun's second barrel puts its shells
   out of the gun (VehicleView: the k-th mount of a slot takes the k-th muzzle of it).

Blender: metres, z up, the front is -Y. Turret-local coordinates for every trunnion.
"""
import math
import re

import bmesh
from mathutils import Vector

import mb_kit35 as K

# ----------------------------------------------------------------------------- shared geometry helpers
# VehicleView.Loaded's round pattern (one modelled round per index).
ROUND_NODE = re.compile(r'^(missile|round|rocket|cruise_missile)_?(\d+)', re.I)



def _base(name):
    return name.split('__')[0].split('.')[0]


def islands(bm):
    """The connected pieces of a bmesh, each a list of faces."""
    seen, out = set(), []
    for f0 in bm.faces:
        if f0 in seen:
            continue
        stack, piece = [f0], []
        seen.add(f0)
        while stack:
            f = stack.pop()
            piece.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g not in seen:
                        seen.add(g)
                        stack.append(g)
        out.append(piece)
    return out


def centre(faces):
    vs = {v for f in faces for v in f.verts}
    c = Vector()
    for v in vs:
        c += v.co
    return c / max(1, len(vs))


def copy_faces(src_shape, faces, dst_shape, offset=Vector()):
    """Copies `faces` (with the 'wear' layer) from one Shape's bmesh to another's, moved by -offset."""
    sbm, dbm = src_shape.bm, dst_shape.bm
    swear = sbm.verts.layers.float.get('wear')
    dwear = dbm.verts.layers.float.get('wear') or dbm.verts.layers.float.new('wear')
    vmap = {}
    for f in faces:
        for v in f.verts:
            if v not in vmap:
                nv = dbm.verts.new(v.co - offset)
                if swear is not None:
                    nv[dwear] = v[swear]
                vmap[v] = nv
    for f in faces:
        try:
            dbm.faces.new([vmap[v] for v in f.verts])
        except ValueError:      # a duplicate face: keep the first
            pass


def delete_faces(shape, faces):
    bm = shape.bm
    bmesh.ops.delete(bm, geom=list(faces), context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')


def move_part(a, key, parent, offset):
    """Re-parents a whole part (name, mat, old parent) to `parent`, keeping its world position."""
    name, mat, _ = key
    shape = a.shapes.pop(key)
    bmesh.ops.translate(shape.bm, verts=list(shape.bm.verts), vec=-offset)
    new = (name, mat, parent)
    if new in a.shapes:
        copy_faces(shape, list(shape.bm.faces), a.shapes[new])
        a.order.remove(key)
    else:
        a.shapes[new] = shape
        a.order[a.order.index(key)] = new


def world(a, pivot):
    """A pivot's position in the asset's space (pivots only translate)."""
    p = Vector()
    o = a.pivots[pivot]
    while o is not None:
        p += o.location
        o = o.parent
    return p


# ----------------------------------------------------------------------------- 1. baked elevation pivots
# id: (parts and pivots riding the elevation (exact base names), trunnion in Turret space)
_TANK = ('Mantlet', 'Main_cannon', 'Muzzle_brake', 'Coax', 'Muzzle_main', 'Muzzle_coax')
_HEAVY = ('Mantlet', 'Main_cannon', 'Muzzle_brake', 'Brake_ports', 'Coax', 'Muzzle_main', 'Muzzle_coax')
_GUARD = ('MG', 'MG_ammo', 'MG_shield', 'Main_cannon', 'Muzzle_brake', 'Muzzle_main')
_CRAM = ('Main_cannon', 'Muzzle_brake', 'Turret_body', 'Team_band', 'Turret_drum', 'Turret_feed', 'Muzzle_main',
         'Muzzle_gun')
ELEVATION = {
    # Tank-gun turrets: the gun, its cast mantlet and the coax trunnion just behind the mantlet face, on the bore axis.
    'gun_turret': (_TANK, (0.0, -1.95, 0.62)),
    'gun_turret_a': (_TANK + ('Muzzle_sensor',), (0.0, -1.95, 0.62)),
    'gun_turret_b': (_HEAVY + ('Main_cannon_2', 'Muzzle_brake_2'), (0.0, -1.55, 0.58)),
    # The twin 155 mm casemate turrets (the barrels share one cradle and one mantlet).
    'heavy_turret': (_HEAVY, (0.0, -2.2, 0.72)),
    'heavy_turret_b': (_HEAVY, (0.0, -2.2, 0.72)),
    'heavy_turret_a': (_HEAVY + ('Blast_covers', 'Thermal_sleeves', 'Brake_bands'), (0.0, -2.2, 0.72)),
    # Twin / quad autocannon AA turrets: the cradle (with its sleeves and casing chutes) at the barrel roots.
    'aa_turret': (('Gun_cradle', 'Main_cannon', 'Main_cannon_2', 'Muzzle_brake', 'Muzzle_brake_2', 'Gun_sleeves',
                   'Gun_casing_chutes', 'Muzzle_main'), (0.0, -0.75, 0.42)),
    'aa_turret_a': (('Mantlet', 'Main_cannon', 'Main_cannon_2', 'Main_cannon_3', 'Main_cannon_4', 'Muzzle_brake',
                     'Muzzle_brake_2', 'Muzzle_brake_3', 'Muzzle_brake_4', 'Barrel_jackets', 'Gun_sleeves',
                     'Muzzle_main'), (0.0, -0.9, 0.34)),
    # Phalanx: the whole upper mass (gun, magazine drum, feed, the radome, the side FLIR) tilts on the side arms.
    'c_ram': (_CRAM, (0.0, 0.0, 0.6)),
    'c_ram_a': (_CRAM + ('Turret_eo', 'Turret_eo_arm', 'Glass'), (0.0, 0.0, 0.6)),
    # Bofors L/70 on its pedestal: cradle, elevating arc, autoloader with the clips; shield, sights, seats stay.
    'aa_gun_tower': (('Cradle', 'Elevation_arc', 'Loader', 'Clips', 'Clip_rounds', 'Main_cannon', 'Muzzle_brake',
                      'Muzzle_main'), (0.0, 0.0, 0.62)),
    # 88 mm flak: on its trunnions (the Trunnions part) with the cradle, recuperators, breech and loading tray.
    'heavy_flak_tower': (('Cradle', 'Recuperators', 'Breech', 'Loading_tray', 'Main_cannon', 'Muzzle_brake',
                          'Muzzle_main'), (0.0, -0.05, 0.95)),
    # 100 mm AT gun: cradle, recuperators, breech, tray and the direct-fire sight on the cradle; the shield stays.
    'at_gun_emplacement': (('Cradle', 'Recuperators', 'Breech', 'Loading_tray', 'Main_cannon', 'Muzzle_brake',
                            'Brake_ports', 'Sights', 'Muzzle_main'), (0.0, -0.1, 0.56)),
    # Towed howitzers: the cradle group on the carriage trunnions; equilibrators, shield, sight and trails stay.
    'artillery_emplacement': (('Cradle', 'Recoil_cylinders', 'Breech', 'Main_cannon', 'Muzzle_brake', 'Muzzle_main'),
                              (0.0, 0.0, 1.2)),
    'artillery_emplacement_a': (('Cradle', 'Recoil_cyl', 'Main_cannon', 'Thermal_jacket', 'Muzzle_brake',
                                 'Brake_ports', 'Breech_block', 'Muzzle_main'), (0.0, 0.2, 1.4)),
    # The 120 mm mortar: the tube turns on its baseplate socket (the breech ball).
    'artillery_emplacement_b': (('Mortar_tube', 'Breech', 'Tube_bands', 'Cradle', 'Recoil_cyl', 'Muzzle_main'),
                                (0.0, 0.55, 0.37)),
    'coastal_battery': (('Mantlet', 'Main_cannon', 'Muzzle_brake', 'Brake_ports', 'Muzzle_main'), (-0.5, -1.85, 0.85)),
    # SPG-9 on its tripod head: the tube, venturi, cradle, sight and grip; the shield stays on the head.
    'recoilless_gun_tower': (('Cradle', 'Main_cannon', 'Muzzle_brake', 'Venturi', 'Tube_bands', 'Sight_bracket',
                              'Sight', 'Grip', 'Muzzle_main'), (0.0, -0.05, 0.1)),
    # Machine guns on their pintles / cradles / the bunker's ball mount.
    'guard_tower': (_GUARD, (0.0, 0.05, 0.64)),
    'guard_tower_a': (_GUARD, (0.0, 0.05, 0.64)),
    'guard_tower_b': (('Gun_cradle', 'Gun_receiver', 'Main_cannon', 'Muzzle_brake', 'Feed_chute', 'Gun_sight', 'Glass',
                       'Muzzle_main'), (0.0, -0.05, 0.12)),
    'mg_bunker': (('Mantlet', 'Main_cannon', 'Muzzle_brake', 'Ammo_belt', 'Muzzle_main'), (0.0, -1.55, 0.22)),
    'mg_bunker_a': (('Twin_mantlet', 'Main_cannon', 'Main_cannon_2', 'Main_cannon_jacket', 'Main_cannon_2_jacket',
                     'Muzzle_brake', 'Muzzle_brake_2', 'Ammo_belt', 'Muzzle_main'), (0.0, -1.6, 0.22)),
    'mg_bunker_b': (('Flame_gun', 'Nozzle_soot', 'Igniter', 'Muzzle_main'), (0.0, -1.6, 0.19)),
    'bulwark_post': (('MG_receiver', 'Main_cannon', 'Muzzle_brake', 'Gun_belt', 'Sight', 'Glass', 'Muzzle_main'),
                     (0.0, 0.0, 0.16)),
    # The laser's beam director tilts in its yoke (the Trunnions part); the yoke stays.
    'laser_ad_station': (('Director', 'Aperture_rim', 'Aperture', 'Sensor_pod', 'Sensor_lens', 'Director_stripe',
                          'Muzzle_main'), (0.0, 0.0, 0.95)),
    # The headquarters' twin-gun turret: both guns, their shared mantlet block, the coax.
    'headquarters': (('Main_cannon', 'Main_cannon_2', 'Muzzle_brake', 'Muzzle_brake_2', 'Turret_armor', 'Coax_mount',
                      'Coax', 'Muzzle_main', 'Muzzle_coax'), (0.0, -1.55, 0.62)),
    # Missile posts: the tube pack with its grips, batteries and sight on the yoke trunnions (the seat stays).
    'manpads_tower': (('Tubes', 'Tube_bands', 'Grip_stocks', 'Battery_units', 'Seeker_caps', 'Sight_arm', 'Sight',
                       'Glass', 'Muzzle_main', 'Muzzle_missile', 'Round', 'Tube_bores'), (0.0, 0.0, 0.55)),
    'aa_turret_b': (('Launcher_frame', 'Tube_bodies', 'Tube_caps', 'Tube_caps_rear', 'Muzzle_missile', 'Round',
                     'Tube_bores'), (0.0, -0.05, 1.45)),
}


def add_elevation(a, ride, trunnion, turret='Turret'):
    """The `Elevation` pivot under `turret` at `trunnion`, with every part and pivot in `ride` moved onto it."""
    if 'Elevation' in a.pivots:
        raise ValueError(f'{a.name}: already has an Elevation pivot')
    ride = set(ride)
    t = a.pivots[turret]
    off = Vector(trunnion)
    el = a.pivot('Elevation', tuple(off), turret)
    el_obj = a.pivots[el]
    moved = 0
    for key in list(a.order):
        name, _, parent = key
        if parent == turret and (_base(name) in ride or ('Round' in ride and ROUND_NODE.match(name))):
            move_part(a, key, 'Elevation', off)
            moved += 1
    for pname, o in list(a.pivots.items()):
        if pname != 'Elevation' and o.parent is t and (_base(pname) in ride or ('Round' in ride and ROUND_NODE.match(pname))):
            o.parent = el_obj
            o.location = o.location - off
            moved += 1
    if not any(_base(p).startswith('Muzzle_') and o.parent is el_obj for p, o in a.pivots.items()):
        raise ValueError(f'{a.name}: no muzzle rides the Elevation pivot')
    print(f'PT13_ELEVATION {a.name}: {moved} nodes on Elevation at {tuple(round(c, 3) for c in off)}')


# ----------------------------------------------------------------------------- wrapper

def _finishers(name):
    """The per-model steps after the model's own build (and every earlier wrapper)."""
    steps = []
    if name in ROUNDS:
        steps.append(ROUNDS[name])
    if name in ELEVATION:
        ride, trunnion = ELEVATION[name]
        steps.append(lambda a, ride=ride, trunnion=trunnion: add_elevation(a, ride, trunnion))
    if name in EXTRA:
        steps.append(EXTRA[name])
    return steps


def wrap(builders):
    out = dict(builders)
    for name in sorted(set(ELEVATION) | set(ROUNDS) | set(EXTRA)):
        if name not in out:
            continue
        build, options = out[name]
        steps = _finishers(name)

        def run(a, _build=build, _steps=steps, **kw):
            _build(a, **kw)
            K.suffixed(a)
            for step in _steps:
                step(a)
        run.__name__ = getattr(build, '__name__', name)
        out[name] = (run, options)
    return out


# ----------------------------------------------------------------------------- 4. extras


def behemoth_side_gun(a):
    """Mount 6 (the hull gun's second barrel since lane C) is the data's third `missile` mount: its muzzle, the third
    Muzzle_missile, sits at the hull gun turret's second barrel mouth (twin_turret: barrels 0.34 apart, mouth 3.52 m
    ahead of the ring, 0.30 up), so its shells leave the gun and turn with it."""
    a.pivot(K.name('Muzzle_missile', 2), (0.17, -3.52, 0.3025), 'Mount_gun')
    print(f'PT13_EXTRA {a.name}: Muzzle_missile.002 on Mount_gun')


EXTRA = {'behemoth': behemoth_side_gun}


# ----------------------------------------------------------------------------- 2. indexed launcher rounds
# Real life: a fired round leaves its cell. A canister or tube keeps its place, but its frangible front cover (a TEL's
# cell hatch, an NSM / Patriot canister cap, a GMLRS pod cap, a Stinger seeker cap) goes with the round and the dark
# bore shows; open tubes (Grad, Smerch, TOS, a technical's rocket pack) show the rocket's nose until it is fired.
# So a round here is its cover (with a dark bore plate behind it, inside the cover until the cover goes) or its nose
# cone in the tube mouth. Open tubes are grouped by row (and side): a few renderers per launcher, not one per tube.
# Under a turret whose elevation the runtime builds (ModelLibrary.AddElevation takes Turret children named launcher*,
# tubes*, rocket_tubes*, pod*), the rounds hang under a group pivot named so (`Launcher_rounds`, `Tubes_rounds`, ...)
# and rise with the launcher; under a baked Elevation or on an erector (missile_*) they need none.


def _key_of(a, base, parent, mat=None):
    return [k for k in a.order if _base(k[0]) == base and k[2] == parent and (mat is None or k[1] == mat)]


def _frame(faces):
    """An island's centre, its thin axis turned to the front (-Y), its in-plane half size, its front and back offsets
    along that axis, then its in-plane axes with their half extents (u, eu, v, ev)."""
    import numpy as np
    pts = np.array([tuple(v.co) for v in {v for f in faces for v in f.verts}])
    c = pts.mean(axis=0)
    _, vec = np.linalg.eigh(np.cov((pts - c).T))
    n = Vector(vec[:, 0]).normalized()
    if n.y > 0:
        n = -n
    nn = np.array(tuple(n))
    d = (pts - c) @ nn
    inplane = pts - c - np.outer(d, nn)
    half = float(np.sqrt((inplane ** 2).sum(axis=1)).max()) / 2 ** .5
    u, v = Vector(vec[:, 2]).normalized(), Vector(vec[:, 1]).normalized()
    eu = float(np.abs((pts - c) @ np.array(tuple(u))).max())
    ev = float(np.abs((pts - c) @ np.array(tuple(v))).max())
    return Vector(tuple(c)), n, half, float(d.max()), float(-d.min()), u, eu, v, ev


def _poly(shape, pts, n):
    """One flat polygon facing n (its back is never seen: it lies on or inside the launcher)."""
    bm = shape.bm
    if bm.verts.layers.float.get('wear') is None:
        bm.verts.layers.float.new('wear')
    f = bm.faces.new([bm.verts.new(tuple(p)) for p in pts])
    f.normal_update()
    if f.normal.dot(n) < 0:
        f.normal_flip()


def _ngon(shape, c, n, r, seg, phase=0.0):
    u = n.orthogonal().normalized()
    v = n.cross(u).normalized()
    _poly(shape, [c + (u * math.cos(phase + i * math.tau / seg) + v * math.sin(phase + i * math.tau / seg)) * r
                  for i in range(seg)], n)


def _rows(cells, side=False):
    """Groups cells [(centre, normal)] by row (top first) and, with side, by side of the centre line: [[index]]."""
    up = Vector((0, 0, 1))
    n = cells[0][1]
    face_up = (up - n * up.dot(n)).normalized()
    hs = [c.dot(face_up) for c, _ in cells]
    order = sorted(range(len(cells)), key=lambda i: -hs[i])
    gaps = [abs(hs[order[i]] - hs[order[i + 1]]) for i in range(len(order) - 1)]
    tol = max(.02, (max(gaps) if gaps else 1.0) * .35)
    rows, cur = [], [order[0]]
    for i in order[1:]:
        if abs(hs[i] - hs[cur[-1]]) > tol:
            rows.append(cur)
            cur = []
        cur.append(i)
    rows.append(cur)
    if not side:
        return rows
    out = []
    for r in rows:
        for left in (True, False):
            g = [i for i in r if (cells[i][0].x < 0) == left]
            if g:
                out.append(g)
    return out


def _group_pivot(a, name, parent):
    return a.pivot(name, (0, 0, 0), parent) if name else parent


def _drop_if_empty(a, key):
    if not a.shapes[key].bm.faces:
        del a.shapes[key]
        a.order.remove(key)


def split_rounds(a, sources, assign, prefix, parent='Turret', names=None):
    """Moves the islands of the parts `sources` [(base name, mat or None)] into round parts: assign(centre) -> index
    (1-based); the round part is f'{prefix}_{index}{names[base]}'."""
    moved = 0
    for base, mat in sources:
        for key in _key_of(a, base, parent, mat):
            shape = a.shapes[key]
            take = {}
            for faces in islands(shape.bm):
                take.setdefault(assign(centre(faces)), []).extend(faces)
            for i, faces in sorted(take.items()):
                copy_faces(shape, faces, a.part(f'{prefix}_{i}{(names or {}).get(base, "")}', key[1], parent))
                delete_faces(shape, faces)
                moved += 1
            _drop_if_empty(a, key)
    return moved


def cover_rounds(a, cover, mat, parent='Turret', group=None, extra=(), plate_name='Launcher_cells', plates=True,
                 lift=0.0, plate_shift=.012, side_rows=False):
    """Each island of the cover part (a hatch, a cap) is one round, Round_N (top row first, left to right), with the
    islands of the `extra` parts nearest to it across the face (its fittings, the same canister's rear cap); a dark
    bore plate (`plate_name`, one quad) is drawn behind each cover, inside it. lift moves a cover drawn flush with its
    canister's end out in front of it (plate_shift puts the plate in the gap), so the bore shows when the cover goes.
    side_rows groups the covers by row and side (one round per group) for launchers with many tubes."""
    gp = _group_pivot(a, group, parent)
    key = _key_of(a, cover, parent, mat)[0]
    shape = a.shapes[key]
    pieces = islands(shape.bm)
    frames = [_frame(f) for f in pieces]
    cells = [fr[:2] for fr in frames]
    if side_rows:
        rank_of = {i: g for g, members in enumerate(_rows(cells, True), 1) for i in members}
        order = sorted(rank_of, key=lambda i: rank_of[i])
    else:
        order = [i for row in _rows(cells) for i in sorted(row, key=lambda i: cells[i][0].x)]
        rank_of = {i: r for r, i in enumerate(order, 1)}
    n = cells[0][1]

    def flat(p):
        return p - n * p.dot(n)
    for i in order:
        rank = rank_of[i]
        if plates:
            c, nn, _, _, back, u, eu, v, ev = frames[i]
            o = c + nn * (-back + plate_shift)
            _poly(a.part(plate_name, 'Undercarriage', gp),
                  [o + u * (su * eu * .86) + v * (sv * ev * .86) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))], nn)
        copy_faces(shape, pieces[i], a.part(f'Round_{rank}', key[1], gp), -n * lift)
    centres = [flat(cells[i][0]) for i in order]
    ranks = [rank_of[i] for i in order]
    delete_faces(shape, [f for p in pieces for f in p])
    _drop_if_empty(a, key)
    for base, emat in extra:
        for k2 in _key_of(a, base, parent, emat):
            sh = a.shapes[k2]
            take = {}
            for faces in islands(sh.bm):
                p = flat(centre(faces))
                take.setdefault(ranks[min(range(len(centres)), key=lambda j: (centres[j] - p).length)], []).extend(faces)
            for r, faces in take.items():
                copy_faces(sh, faces, a.part(f'Round_{r}', k2[1], gp))
                delete_faces(sh, faces)
            _drop_if_empty(a, k2)
    print(f'PT13_ROUNDS {a.name}: {len(order)} covers in {len(set(ranks))} rounds under {gp}')


def cap_rounds(a, bore, mat, cap_mat='Canvas', parent='Turret', group=None, side=False, seg=6, rims=None,
               canisters=False, per_tube=False):
    """A frangible cap in front of each bore (a GMLRS pod's tube caps: a flat seg-gon each, grouped by row and side,
    or one cap per tube), or with canisters one cover over each 2 x 2 block of bores (a PAC-3 canister). The caps sit
    1 cm in front of the bores' (and the `rims` part's) front plane: Round_N."""
    gp = _group_pivot(a, group, parent)
    key = _key_of(a, bore, parent, mat)[0]
    pieces = islands(a.shapes[key].bm)
    frames = [_frame(f) for f in pieces]
    n = frames[0][1]
    fronts = [fr[0].dot(n) + fr[3] for fr in frames]
    if rims:
        for k2 in _key_of(a, rims, parent):
            fronts += [fr[0].dot(n) + fr[3] for fr in map(_frame, islands(a.shapes[k2].bm))]
    plane = max(fronts) + .01

    def on_plane(p):
        return p + n * (plane - p.dot(n))
    cells = [fr[:2] for fr in frames]
    if canisters:
        rows = _rows(cells)
        groups = []
        for h in range(0, len(rows), 2):
            block = [i for r in rows[h:h + 2] for i in r]
            for left in (True, False):
                g = [i for i in block if (cells[i][0].x < 0) == left]
                if g:
                    groups.append(g)
    elif per_tube:
        groups = [[i] for row in _rows(cells) for i in sorted(row, key=lambda i: cells[i][0].x)]
    else:
        groups = _rows(cells, side)
    for g, members in enumerate(groups, 1):
        part = a.part(f'Round_{g}', cap_mat, gp)
        if canisters:
            half = frames[members[0]][2]
            u = n.cross(Vector((0, 0, 1))).normalized()
            v = u.cross(n).normalized()
            us = [frames[i][0].dot(u) for i in members]
            vs = [frames[i][0].dot(v) for i in members]
            m = half * 1.25
            mid = on_plane(sum((frames[i][0] for i in members), Vector()) / len(members))
            hu, hv = (max(us) - min(us)) / 2 + m, (max(vs) - min(vs)) / 2 + m
            _poly(part, [mid + u * (su * hu) + v * (sv * hv) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))], n)
        else:
            for i in members:
                _ngon(part, on_plane(frames[i][0]), n, frames[i][2] * 1.38, seg, math.pi / seg)
    print(f'PT13_ROUNDS {a.name}: {len(pieces)} bores capped in {len(groups)} rounds under {gp}')


def nose_rounds(a, ring, mat, parent='Turret', group=None, side=True, solid=False, flat=False):
    """A rocket's nose in each tube mouth (a rim ring, or a dark bore disc when solid), grouped by row and side:
    Rocket_N. A cone, or with flat (a launcher seen in numbers, its triangle cap) one quad just inside the rim."""
    gp = _group_pivot(a, group, parent)
    key = _key_of(a, ring, parent, mat)[0]
    pieces = islands(a.shapes[key].bm)
    frames = [_frame(f) for f in pieces]
    groups = _rows([fr[:2] for fr in frames], side)
    for g, members in enumerate(groups, 1):
        part = a.part(f'Rocket_{g}', 'Crate', gp)
        for i in members:
            c, n, half, front = frames[i][:4]
            r = half * (1.0 if solid else .9)       # about the bore: the half size is 0.71 of the outer radius
            if flat:
                _ngon(part, c + n * (front - .01), n, r, 4, math.pi / 4)
                continue
            base, tip = c + n * (front - .06), c + n * (front + .04)
            rot = Vector((0, 0, 1)).rotation_difference(n).to_euler()
            part.cyl(r, (tip - base).length, loc=tuple((base + tip) / 2), rot=tuple(rot), seg=8, r2=r * .3, bevel=0)
    print(f'PT13_ROUNDS {a.name}: {len(pieces)} noses in {len(groups)} rounds under {gp}')


def r_ballistic(a):
    """The two Iskander missiles on the erector: Missile_1 (at Muzzle_main, fired first) and Missile_2."""
    names = {'Missile_bodies': '_body', 'Missile_fins': '_fins', 'Missile_nozzles': '_nozzle',
             'Missile_seekers': '_seeker', 'Missile_bands': '_bands'}
    mx = a.pivots['Muzzle_main'].location.x
    moved = split_rounds(a, [(b, None) for b in names], lambda c: 1 if (c.x > 0) == (mx > 0) else 2, 'Missile',
                         names=names)
    print(f'PT13_ROUNDS {a.name}: {moved} missile parts split into Missile_1 / Missile_2')


def r_cruise(a):
    cover_rounds(a, 'Launcher_hatches', 'Armor', group='Launcher_rounds', extra=[('Launcher_hatch_fittings', 'Steel')])


def r_coastal(a):
    # The front caps (dark) are the covers; each takes the rear cap (Armor) of its canister.
    # Their caps were drawn flush with the canister ends (coplanar): lifted 6.5 cm, the bore plate in the gap.
    cover_rounds(a, 'Canister_caps', 'Undercarriage', group='Launcher_rounds', extra=[('Canister_caps', 'Armor')],
                 lift=.065, plate_shift=.05)


def r_patriot(a):
    cover_rounds(a, 'Launcher_covers', 'Medical', group='Launcher_rounds')


def r_patriot_a(a):
    # PAC-3: four canisters of four missiles; each canister's cover goes with its missiles.
    cap_rounds(a, 'Launcher_tubes_bore', 'Undercarriage', cap_mat='Medical', group='Launcher_rounds',
               rims='Launcher_tubes', canisters=True)


def r_mlrs(a):
    """The six-tube pod: a canvas cap on every tube (four were drawn, two tubes open), one round each, as flat
    octagons on the drawn caps' plane (the pod is seen in numbers: under its triangle cap)."""
    key = _key_of(a, 'Tube_caps', 'Turret', 'Canvas')[0]
    sh = a.shapes[key]
    delete_faces(sh, list(sh.bm.faces))
    _drop_if_empty(a, key)
    cap_rounds(a, 'Tubes_bore', 'Undercarriage', cap_mat='Canvas', group='Tubes_rounds', seg=8, rims='Tubes',
               per_tube=True)


def r_elite_mlrs(a):
    cap_rounds(a, 'Tubes_bore', 'Undercarriage', cap_mat='Crate', group='Tubes_rounds', side=True, seg=6,
               rims='Pod_face')


def r_smerch(a):
    nose_rounds(a, 'Tubes_bore', 'Undercarriage', group='Tubes_rounds', side=False, solid=True)


def r_grad(a):
    # The tube ends are drawn as solid steel hex caps on the frame plate: a loaded tube shows its cap, a fired one a
    # dark bore (one quad each, 1 cm in front of the frame: the pack is seen in numbers, at its triangle cap).
    cover_rounds(a, 'Rocket_tubes_face', 'Steel', group='Rocket_tubes_rounds', plate_name='Rocket_tubes_bores',
                 plate_shift=.02, side_rows=True)


def r_tos(a):
    nose_rounds(a, 'Tubes', 'Undercarriage', group='Tubes_rounds', side=True, solid=True)


def r_technical(a):
    nose_rounds(a, 'Tubes_bore', 'Undercarriage', group='Tubes_rounds', side=False, solid=True)


def r_manpads(a):
    cover_rounds(a, 'Seeker_caps', 'BarrelRed', plate_name='Tube_bores')


def r_aa_turret_b(a):
    # Each tube has a cap at both ends: the front ones (lower y) are the covers, each takes its rear cap.
    key = _key_of(a, 'Tube_caps', 'Turret', 'Undercarriage')[0]
    sh = a.shapes[key]
    rear = [f for p in islands(sh.bm) if centre(p).y > 0 for f in p]
    copy_faces(sh, rear, a.part('Tube_caps_rear', 'Undercarriage', 'Turret'))
    delete_faces(sh, rear)
    cover_rounds(a, 'Tube_caps', 'Undercarriage', plate_name='Tube_bores', extra=[('Tube_caps_rear', 'Undercarriage')])


ROUNDS = {
    'ballistic_launcher': r_ballistic, 'ground_cruise_missile_vehicle': r_cruise, 'coastal_ashm_vehicle': r_coastal,
    'missile_battery': r_patriot, 'missile_battery_b': r_patriot, 'missile_battery_a': r_patriot_a,
    'mlrs': r_mlrs, 'elite_mlrs': r_elite_mlrs, 'heavy_rocket_artillery': r_smerch, 'grad_truck': r_grad,
    'thermobaric_launcher': r_tos, 'rocket_technical': r_technical, 'manpads_tower': r_manpads,
    'aa_turret_b': r_aa_turret_b,
}
