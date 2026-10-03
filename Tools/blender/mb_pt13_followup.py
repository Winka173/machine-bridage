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
                       'Glass', 'Muzzle_main', 'Muzzle_missile', 'Round'), (0.0, 0.0, 0.55)),
    'aa_turret_b': (('Launcher_frame', 'Tube_bodies', 'Tube_caps', 'Muzzle_missile', 'Round'), (0.0, -0.05, 1.45)),
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
ROUNDS = {}
