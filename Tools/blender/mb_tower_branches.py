"""Rank-7 branch models of every tower (tower-branch prompt, section C.1): <tower>_a and <tower>_b, where
A and B are the spec's order, which is also the order of the tower's branch defs in balance.json.

Each model starts from its tower's own builder and swaps the weapon module (barrel count and length,
launcher kind) or adds the branch's signature part, big enough to read at the default phone zoom and at
Low graphics (the shared simplified level and the impostor keep parts this size). The tower's pivots
and muzzles keep their names, so the branch's weapons fire from the right place: a branch that
needs other muzzles (the SAM post's missile box, the steel fortress's two small turrets) gets them.
The guard tower's gun nest (B) is a new low model.

  blender --background --python Tools/blender/build_assets.py -- _a _b     # (also matches other names)

Helpers: strip() drops parts (whole, or only their faces inside a box) and pivots; stretch() lengthens
a barrel by moving the vertices past a point along its bore; grow() scales parts about a point.
"""
import functools
import math
import random

import bmesh
import bpy
from mathutils import Euler, Matrix, Vector

import mb_fortress
import mb_p17_temp
import mb_siege
import mb_towers3
import mb_weapons as wpn
from frontier_kit import chamfered
from mb_siege import bag_arc, crate, lattice, shells
from mb_support import _quadcopter
from mb_towers3 import _runtime_names, _tube_lip
from mb_vehicles import ACROSS, FORWARD, R90, _antenna, _barrel, _dish, _frame, _tube_mouth
from mb_vehicles2 import _axis

TAU = math.tau
BASES = {**mb_siege.BUILDERS, **mb_towers3.BUILDERS, **mb_fortress.BUILDERS, **mb_p17_temp.BUILDERS}


# ----------------------------------------------------------------------------- editing helpers
def _match(name, names):
    return any(name.startswith(n[:-1]) if n.endswith('*') else name == n for n in names)


def _drop_key(a, key):
    a.shapes.pop(key).bm.free()
    a.order.remove(key)


def strip(a, names=(), pivots=(), parents=(), inside=None):
    """Drop the parts named in `names` ('Prefix*' for a prefix): whole, or with `inside` ((x0, y0, z0),
    (x1, y1, z1), model space) only their faces whose centre is in that box; every part on a pivot in
    `parents` (the pivot stays); and the `pivots` with every pivot and part on them."""
    owner = {o: n for n, o in a.pivots.items()}
    gone = set(pivots)
    grew = True
    while grew:
        grew = False
        for n, o in a.pivots.items():
            if n not in gone and o.parent is not None and owner.get(o.parent) in gone:
                gone.add(n)
                grew = True
    lo, hi = (Vector(inside[0]), Vector(inside[1])) if inside else (None, None)
    for key in list(a.order):
        name, _, parent = key
        if parent in gone or parent in parents:
            _drop_key(a, key)
        elif _match(name, names):
            if inside is None:
                _drop_key(a, key)
                continue
            bm = a.shapes[key].bm
            off = a._world(parent).to_translation()
            dead = [f for f in bm.faces
                    if all(lo[i] <= (f.calc_center_median() + off)[i] <= hi[i] for i in range(3))]
            if dead:
                bmesh.ops.delete(bm, geom=dead, context='FACES')
    for n in gone:
        o = a.pivots.pop(n, None)
        if o is not None:
            bpy.data.objects.remove(o)


def stretch(a, names, parent, origin, direction, beyond, delta, pivots=()):
    """Lengthen a barrel: every vertex of the named parts on `parent` (and every named pivot) more than
    `beyond` metres from `origin` along `direction` moves `delta` further along it."""
    d, o = Vector(direction).normalized(), Vector(origin)
    for key in a.order:
        if key[2] == parent and _match(key[0], names):
            for v in a.shapes[key].bm.verts:
                if (v.co - o).dot(d) > beyond:
                    v.co += d * delta
    for n in pivots:
        p = a.pivots[n]
        if (Vector(p.location) - o).dot(d) > beyond:
            p.location = Vector(p.location) + d * delta


def grow(a, names, parent, centre, k):
    c = Vector(centre)
    for key in a.order:
        if key[2] == parent and _match(key[0], names):
            for v in a.shapes[key].bm.verts:
                v.co = c + (v.co - c) * k


def variant(base, mod):
    """The tower's builder, then the branch's changes."""
    build, options = BASES[base]

    @functools.wraps(mod)
    def run(a):
        build(a)
        mod(a)
    return _runtime_names(run), dict(options)


def _ring(part, r, z, tube, seg=24, ring=6, loc=(0, 0)):
    part.torus(r, tube, loc=(loc[0], loc[1], z), seg=seg, ring=ring)


# ----------------------------------------------------------------------------- guard tower
def guard_tower_a(a):
    """Observation (A): a lattice radar mast on the roof's rear left corner with a slotted-array bar
    spinning on `Radar`, and a bigger searchlight."""
    top = 9.94
    mx, my = -.1, 1.1
    lattice(a.part('Watch_mast', 'Steel'), mx, my, top, top + 3.0, .24, .12, 3, leg=.07, brace=.03)
    a.part('Watch_cap', 'Armor').box((.36, .36, .1), loc=(mx, my, top + 3.03), bevel=.01, seg=1)
    a.part('Watch_band', 'Hazard').box((.5, .5, .08), loc=(mx, my, top + .5), bevel=0)
    r = a.pivot('Radar', (mx, my, top + 3.08))
    a.part('Radar_mount', 'Armor', r).cyl(.15, .2, loc=(0, 0, .1), seg=10, bevel=.01, bseg=1)
    a.part('Radar_bar', 'Team', r).box((2.4, .26, .36), loc=(0, 0, .38), bevel=.03, seg=1)
    a.part('Radar_face', 'Medical', r).box((2.3, .05, .26), loc=(0, -.15, .38), bevel=0)
    a.part('Radar_beacon', 'Alloy', r).sphere(.06, loc=(0, .1, .62), seg=8, rings=4)
    grow(a, ('Searchlight_*',), 'Searchlight', (0, 0, 0), 1.3)


def guard_tower_b(a):
    """Gun nest (B), a new low model: a sandbag ring (open at the back) on a 3.5 m concrete pad round a
    shielded 25 mm autocannon on `Turret` (Main_cannon, Muzzle_brake, `Muzzle_main`), ready boxes, and the
    tower's 40 mm grenade launcher riding on the left ammunition box (`Mount_gun` / `Muzzle_gun`)."""
    rng = random.Random(71)
    a.part('Pad', 'Concrete').prism(chamfered(3.5, 3.5, .5), .24, loc=(0, 0, .1), axis='Z', bevel=.04, seg=1,
                                    taper=.99)                                                 # z -.02 .. .22
    bags = a.part('Sandbags', 'Sandbag')
    for course in range(3):
        z = .22 + .1 + course * .21
        bag_arc(bags, rng, 1.45 - course * .05, math.radians(118), math.radians(422), z, size=(.66, .32, .22),
                half=course % 2 == 1)
    for k, (x, y) in enumerate(((1.2, 1.35), (-1.3, 1.3))):
        crate(a, (x, y, .22), size=(.6, .34, .28), yaw=.4 * (k - .5), band=k == 0)
    t = a.pivot('Turret', (0, 0, .22))
    steel = a.part('Turret_steel', 'Steel', t)
    armor = a.part('Turret_armor', 'Armor', t)
    steel.cyl(.6, .1, loc=(0, 0, .05), seg=16, bevel=.015, bseg=1)                               # turntable
    armor.cyl(.18, .6, loc=(0, 0, .4), seg=10, bevel=.01, bseg=1)                                # pedestal
    team = a.part('Gun_cradle', 'Team', t)
    team.box((.5, 1.0, .36), loc=(0, .1, .9), bevel=.04, seg=1)                                  # receiver
    team.box((.34, .5, .2), loc=(0, .5, 1.14), bevel=.03, seg=1)                                 # sight housing
    a.part('Gun_sight', 'Glass', t).box((.26, .04, .12), loc=(0, .24, 1.16), bevel=0)
    a.part('Gun_shield', 'Team', t).box((1.24, .07, .66), loc=(0, -.46, .92), rot=(-.2, 0, 0), bevel=.015, seg=1,
                                        taper=(.8, 1))
    for s in (-1, 1):                                                                            # ammo boxes
        armor.box((.26, .56, .34), loc=(s * .42, .12, .86), bevel=.02, seg=1)
        a.part('Ammo_bands', 'Hazard', t).box((.28, .1, .04), loc=(s * .42, .12, 1.04), bevel=0)
    tip = _barrel(a, t, start_y=-.42, length=1.95, radius=.055, height=.94, seg=12, style='flash',
                  brake=(.16, .22, .16), sleeve=(.2, .6, .085), bands=(.55,))
    a.pivot('Muzzle_main', tip, t)
    wpn.agl(a, (-.42, .2, 1.04), parent=t, post=.1, ammo=-1)


# ----------------------------------------------------------------------------- MG bunker
def mg_bunker_a(a):
    """Twin MG (A): a Team twin mantlet in the firing slit with two jacketed heavy barrels
    (Main_cannon, Main_cannon_2) well out of the wall."""
    strip(a, ('Main_cannon', 'Muzzle_brake'), pivots=('Muzzle_main',))
    t, zc = 'Turret', .19
    a.part('Twin_mantlet', 'Team', t).box((.66, .3, .3), loc=(0, -1.72, zc), bevel=.03, seg=1)
    a.part('Twin_cradle', 'Armor', t).box((.5, .7, .2), loc=(0, -1.2, zc), bevel=.02, seg=1)
    tips = []
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .16
        gun = a.part(f'Main_cannon{suffix}', 'Steel', t)
        gun.cyl(.05, 1.2, loc=(x, -2.3, zc), rot=FORWARD, seg=10, bevel=0)
        gun.cyl(.082, .62, loc=(x, -2.1, zc), rot=FORWARD, seg=10, bevel=.01, bseg=1)             # jacket
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).cyl(.075, .2, loc=(x, -2.92, zc), rot=FORWARD, seg=10,
                                                               bevel=0)
        tips.append(Vector((x, -3.03, zc)))
    a.pivot('Muzzle_main', tuple((tips[0] + tips[1]) / 2), t)


def mg_bunker_b(a):
    """Flame bunker (B): a fat flame projector with a glowing pilot ring in the slit instead of the MG,
    two big fuel bottles in a cradle on the back of the roof with a hose into the wall; no ATGM."""
    strip(a, ('Main_cannon', 'Muzzle_brake', 'MG', 'MG_ammo', 'MG_shield', 'ATGM_tripod'),
          pivots=('Muzzle_main', 'Mount_missile'))
    t, zc = 'Turret', .19
    a.part('Flame_body', 'Armor', t).box((.34, .7, .3), loc=(0, -.95, zc), bevel=.03, seg=1)
    a.part('Flame_mantlet', 'Team', t).box((.6, .28, .3), loc=(0, -1.72, zc), bevel=.03, seg=1)
    noz = a.part('Flame_nozzle', 'Steel', t)
    noz.cyl(.1, 1.0, loc=(0, -2.2, zc), r2=.075, rot=FORWARD, seg=12, bevel=.01, bseg=1)
    a.part('Flame_pilot', 'LavaGlow', t).torus(.09, .025, loc=(0, -2.7, zc), rot=FORWARD, seg=12, ring=4)
    a.part('Flame_hose', 'Rubber', t).tube([(0, -.6, zc), (.1, -.3, zc - .05), (0, 0, zc - .08)], .05, seg=6)
    a.pivot('Muzzle_main', (0, -2.74, zc), t)
    strip(a, ('Camo_net*',), inside=((-3, .72, 0), (3, 3, 5)))
    top = 1.84
    for k, y in enumerate((1.02, 1.42)):
        z = top + .32 - k * .06
        a.part('Fuel_bottles', 'BarrelRed').cyl(.24 - k * .03, 1.5, loc=(0, y, z), rot=ACROSS, seg=14, bevel=.07, bseg=2)
        for x in (-.45, .45):
            a.part('Fuel_bands', 'Hazard').cyl(.25 - k * .03, .08, loc=(x, y, z), rot=ACROSS, seg=14, bevel=0)
        a.part('Fuel_valves', 'Steel').cyl(.06, .12, loc=(.8, y, z), rot=ACROSS, seg=8, bevel=0)
    for x in (-.55, .55):
        a.part('Fuel_frame', 'Armor').box((.1, .9, .3), loc=(x, 1.2, top + .12), bevel=.01, seg=1)
    a.part('Fuel_hoses', 'Rubber').tube([(.86, 1.02, top + .32), (1.0, .6, top + .1), (.9, .2, top - .2)], .045, seg=5)


# ----------------------------------------------------------------------------- AA tower
def aa_turret_a(a):
    """Quad flak (A): a second pair of 35 mm barrels over the first (four barrels), the SAM box gone."""
    strip(a, ('SAM_*',), pivots=('Muzzle_missile',))
    pitch = math.radians(28)
    for s, suffix in ((-1, '_3'), (1, '_4')):
        x = s * .78
        base = _axis((x, .25, 1.02), pitch)(1.3, .22)
        _barrel(a, 'Turret', start_y=base.y, length=2.1, radius=.045, height=base.z, pitch=pitch, x=x, suffix=suffix,
                seg=10, style='flash', brake=(.12, .24, .12), sleeve=(.12, .5, .07))
        a.part('Pod_riser', 'Team', 'Turret').box((.34, .9, .24), loc=tuple(_axis((x, .25, 1.02), pitch)(.8, .24)),
                                                 rot=(-pitch, 0, 0), bevel=.03, seg=1)


def aa_turret_b(a):
    """SAM post (B): the guns and their pods give way to two launcher boxes of two missile tubes each
    (four) raised 25 degrees on the gun house's flanks (`Muzzle_missile` and three more), and a light MG
    on the house front (`Muzzle_main`); a concrete revetment replaces the sandbags."""
    strip(a, ('Main_cannon*', 'Muzzle_brake*', 'SAM_*'), pivots=('Muzzle_main', 'Muzzle_missile'))
    # The gun pods, magazines and trunnions stand clear of the gun house (|x| .52): cut them off above the pedestal.
    for names, x in ((('Gun_house', 'Turret_armor'), .56), (('Turret_steel',), .42)):
        for sx in (-1, 1):
            strip(a, names, inside=((min(sx * x, sx * 3), -3, .95), (max(sx * x, sx * 3), 3, 3.5)))
    # A SAM site's concrete revetment (open at the back) in place of the gun pit's sandbags.
    strip(a, ('Sandbags', 'Crates', 'Crate_cleats', 'Crate_bands'))
    wall = a.part('Revetment', 'Concrete')
    wall.box((4.0, .4, .72), loc=(0, -1.8, .66), bevel=.05, seg=1, taper=(1, .85))
    for sx in (-1, 1):
        wall.box((.4, 2.6, .72), loc=(sx * 1.8, -.3, .66), bevel=.05, seg=1, taper=(.85, 1))
        a.part('Revetment_band', 'Hazard').box((.42, .5, .06), loc=(sx * 1.8, .72, 1.03), bevel=0)
    a.part('Revetment_band', 'Hazard').box((1.2, .42, .06), loc=(0, -1.8, 1.03), bevel=0)
    t = 'Turret'
    pitch = math.radians(25)
    srot = (-pitch, 0, 0)
    L = 1.9
    n = 0
    for s in (-1, 1):
        at = _axis((s * .86, .75, 1.05), pitch)
        a.part('SAM_box', 'Team', t).box((.5, L, .9), loc=tuple(at(L / 2 - .3)), rot=srot, bevel=.04, seg=1)
        frame = a.part('SAM_frame', 'Armor', t)
        for d in (-.22, L - .4):
            frame.box((.54, .1, .94), loc=tuple(at(d)), rot=srot, bevel=0)
        a.part('SAM_arm', 'Armor', t).box((.3, .24, .2), loc=(s * .55, .75, 1.0), bevel=0)
        for up in (.22, -.22):
            _tube_mouth(a, t, _frame(at(L - .3, up), (R90 - pitch, 0, 0)), .16, protrude=.05, seg=8, name='SAM_tubes')
            a.pivot('Muzzle_missile' + ('' if n == 0 else f'__{n:03d}'), tuple(at(L - .3 + .05, up)), t)
            n += 1
    a.part('MG', 'Armor', t).box((.16, .44, .16), loc=(-.25, -.62, .8), bevel=.02, seg=1)
    a.part('MG_barrel', 'Steel', t).cyl(.03, .6, loc=(-.25, -1.1, .8), rot=FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_main', (-.25, -1.41, .8), t)


# ----------------------------------------------------------------------------- EW tower
def _ew_column(a, r, h):
    head = a.part('Head_steel', 'Steel', r)
    head.cyl(.36, .08, loc=(0, 0, .04), seg=14, bevel=.015, bseg=1)
    head.cyl(.11, h, loc=(0, 0, .06 + h / 2), seg=10, bevel=0)


def ew_tower_a(a):
    """Drone jammer (A): a white antenna dome on the spinning head, three glowing wave rings spreading
    out and down from it on spokes."""
    strip(a, parents=('Radar',), pivots=('Muzzle_main',))
    r = 'Radar'
    _ew_column(a, r, 1.0)
    a.part('Jam_dome', 'Medical', r).sphere(.72, loc=(0, 0, 1.3), seg=18, rings=10)
    a.part('Jam_band', 'Team', r).torus(.72, .06, loc=(0, 0, 1.3), seg=20, ring=5)
    a.part('Jam_tip', 'LavaGlow', r).sphere(.07, loc=(0, 0, 2.06), seg=8, rings=4)
    waves = a.part('Jam_waves', 'TeamGlow', r)
    spokes = a.part('Jam_spokes', 'Steel', r)
    for R, z, w in ((1.15, 1.2, .05), (1.55, .95, .045), (1.95, .7, .04)):
        waves.torus(R, w, loc=(0, 0, z), seg=28, ring=5)
        for k in range(3):
            u = k * TAU / 3 + R * .3
            spokes.limb((.12 * math.cos(u), .12 * math.sin(u), .45), (R * math.cos(u), R * math.sin(u), z), .025,
                        .025, bevel=0)
    a.pivot('Muzzle_main', (0, -.74, 1.3), r)


def ew_tower_b(a):
    """Radar spoofer (B): one big flat phased-array panel (tiles in a grid) leaning back on the head."""
    strip(a, parents=('Radar',), pivots=('Muzzle_main',))
    r = 'Radar'
    _ew_column(a, r, .9)
    tilt = math.radians(15)
    rot = (-tilt, 0, 0)
    c = Vector((0, 0, 1.55))
    m = _frame(c, rot)
    a.part('Array_panel', 'Team', r).box((2.5, .22, 1.9), loc=tuple(c), rot=rot, bevel=.04, seg=1)
    tiles = a.part('Array_tiles', 'Medical', r)
    for i in range(4):
        for j in range(3):
            p = m @ Vector((-.9 + i * .6, -.12, -.6 + j * .6))
            tiles.box((.54, .04, .54), loc=tuple(p), rot=rot, bevel=.01, seg=1)
    a.part('Array_box', 'Armor', r).box((.8, .3, .6), loc=tuple(m @ Vector((0, .25, -.4))), rot=rot, bevel=.02, seg=1)
    a.part('Array_brace', 'Steel', r).limb((0, .1, .6), tuple(m @ Vector((0, .15, -.7))), .09, .09, bevel=0)
    a.pivot('Muzzle_main', tuple(m @ Vector((0, -.16, 0))), r)


# ----------------------------------------------------------------------------- dragon's teeth
TEETH = ('Teeth', 'Rebar', 'Rubble', 'Moss', 'Hedgehogs', 'Hedgehog_plates')


def _girder_hedgehog(a, loc, yaw, length, flange, t):
    """A Czech hedgehog of heavy bevelled girders (mb_towers3._hedgehog's layout; the bevels catch the light
    up close and melt away in the simplified far level)."""
    turn = Vector((1, 1, 1)).normalized().rotation_difference(Vector((0, 0, 1))).to_matrix()
    spin = Matrix.Rotation(yaw, 3, 'Z')
    c = Vector(loc) + Vector((0, 0, length / 2 / math.sqrt(3)))
    part = a.part('Hedgehogs', 'Rust')
    for axis in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))):
        d = spin @ turn @ axis
        side = d.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = d.cross(side).normalized()
        rot = Matrix((side, up, d)).transposed().to_euler('XYZ')
        part.box((flange, t, length), loc=tuple(c + side * (flange / 2 - t / 2)), rot=rot, bevel=.02, seg=1)
        part.box((t, flange, length), loc=tuple(c + up * (flange / 2 - t / 2)), rot=rot, bevel=.02, seg=1)
    a.part('Hedgehog_plates', 'Steel').box((flange * .9, flange * .9, flange * .9), loc=tuple(c), rot=(.6, .6, yaw),
                                           bevel=.02, seg=1)


def dragons_teeth_a(a):
    """Steel hedgehogs (A): three big Czech hedgehogs of heavy girders in a row on the footing, a small
    one between each pair."""
    strip(a, TEETH)
    for k, x in enumerate((-1.67, 0.0, 1.67)):
        _girder_hedgehog(a, (x, .1 * (k - 1), .1), .35 + k * .9, 2.2, .24, .07)
    for k, x in enumerate((-.83, .83)):
        _girder_hedgehog(a, (x, .75 * (1 - 2 * k), .08), 1.2 + k, 1.2, .14, .05)


def dragons_teeth_b(a):
    """Wire obstacle (B): two rows of concertina loops on steel pickets along the footing with a top wire and
    warning tags; the loops repeat every 5 m, so segments continue end to end."""
    strip(a, TEETH)
    pk = a.part('Pickets', 'Armor')
    wire = a.part('Razor_wire', 'Steel')
    for y in (-.6, .6):
        for x in (-2.1, -.7, .7, 2.1):
            pk.cyl(.06, 1.3, loc=(x, y, .6), seg=12, bevel=.02, bseg=2)
            pk.cyl(.1, .08, loc=(x, y, 1.26), seg=12, bevel=.02, bseg=2)
        # Concertina loops (rings a little askew, crossing each other) rather than one helix: the loops are
        # smooth, so the simplified far level can thin them out.
        for k in range(7):
            x = -2.5 + (k + .5) * 5.0 / 7
            wire.torus(.5, .04, loc=(x, y, .62), rot=(0, R90, .3 if k % 2 else -.3), seg=12, ring=4)
        wire.tube([(-2.5, y, 1.2), (2.5, y, 1.2)], .02, seg=4, caps=False)
        for x in (-1.4, 1.4):
            a.part('Warning_tags', 'Hazard').box((.3, .02, .2), loc=(x, y - .52 * (1 if y < 0 else -1), 1.0), bevel=0)


# ----------------------------------------------------------------------------- minefield
MINES = ('Mine_earth', 'Mine_bodies', 'Mine_plates', 'Mine_fuzes', 'Stake_mine*', 'Tripwire*')


def minefield_a(a):
    """Anti-tank mines (A): three big mines lying on the ground, each with a glowing army-coloured rim
    (clear to their own side), a hazard band and a pressure plate."""
    strip(a, MINES)
    for x, y in ((-1.15, -.95), (1.2, -.35), (-.25, 1.2)):
        a.part('Mine_bodies', 'Armor').cyl(.46, .18, loc=(x, y, .1), seg=16, bevel=.04, bseg=2)
        a.part('Mine_rims', 'TeamGlow').torus(.47, .035, loc=(x, y, .13), seg=16, ring=4)
        a.part('Mine_bands', 'Hazard').cyl(.3, .03, loc=(x, y, .2), seg=16, bevel=0)
        a.part('Mine_plates', 'Steel').cyl(.18, .06, loc=(x, y, .22), seg=12, bevel=.01, bseg=1)


def minefield_b(a):
    """Scatter mines (B): a dozen small mines strewn over the patch and a mine dispenser on a skid in the
    corner, its six tubes pointing up and out."""
    strip(a, MINES)
    rng = random.Random(58)
    for i in range(4):
        for j in range(4):
            if (i, j) in ((3, 3), (3, 2)):
                continue
            x = -1.65 + i * 1.05 + rng.uniform(-.25, .25)
            y = -1.65 + j * 1.05 + rng.uniform(-.25, .25)
            a.part('Mine_bodies', 'Armor').cyl(.15, .08, loc=(x, y, .06), seg=10, bevel=.015, bseg=1)
            a.part('Mine_caps', 'Hazard').cyl(.07, .03, loc=(x, y, .11), seg=8, bevel=0)
    dx, dy = 1.45, 1.35
    a.part('Dispenser_skid', 'Steel').box((1.2, .8, .1), loc=(dx, dy, .08), bevel=0)
    pitch = math.radians(40)
    rot = (-pitch, 0, math.radians(45))
    m = _frame((dx, dy, .55), rot)
    a.part('Dispenser', 'Team').box((1.0, .5, .7), loc=(dx, dy, .55), rot=rot, bevel=.04, seg=1)
    for i in range(3):
        for j in range(2):
            _tube_mouth(a, None, m @ _frame((-.3 + i * .3, -.26, -.15 + j * .3), FORWARD), .1, protrude=.05, seg=10,
                        name='Dispenser_tubes')


# ----------------------------------------------------------------------------- ATGM tower
def atgm_tower_a(a):
    """Top attack (A): the launcher raised 1.8 m on a steel column with hazard bands, and a sensor mast
    with a ball sight on the launcher."""
    rise = 1.8
    a.pivots['Turret'].location.z += rise
    tx, ty, roof = 0.0, -.15, 3.27
    a.part('Launch_column', 'Steel').cyl(.3, rise + .1, loc=(tx, ty, roof + rise / 2), seg=14, bevel=.02, bseg=1)
    for z in (.3, rise - .2):
        a.part('Launch_column_band', 'Hazard').cyl(.315, .12, loc=(tx, ty, roof + z), seg=14, bevel=0)
    a.part('Launch_collar', 'Armor').cyl(.5, .14, loc=(tx, ty, roof + rise - .02), seg=14, bevel=.02, bseg=1)
    t = 'Turret'
    a.part('Sensor_mast', 'Steel', t).cyl(.05, 1.0, loc=(.52, .4, .9), seg=8, bevel=0)
    a.part('Sensor_ball', 'Armor', t).sphere(.2, loc=(.52, .4, 1.5), seg=12, rings=8)
    a.part('Sensor_eye', 'Glass', t).cyl(.1, .04, loc=(.52, .22, 1.5), rot=FORWARD, seg=10, bevel=0)


def atgm_tower_b(a):
    """Multi-role (B): a 2 x 2 box of four tubes (`Muzzle_missile` and three more) round the sight, and a
    small air-search radar spinning on the launcher."""
    strip(a, ('Launcher', 'Launcher_bands', 'ATGM_pod', 'Launcher_bores'),
          pivots=('Muzzle_missile', 'Muzzle_missile__001', 'Muzzle_main'))
    t = 'Turret'
    zt_, xr, yr, yf, rt = .95, .5, .45, -1.45, .11
    tubes = a.part('Launcher', 'Team', t)
    bands = a.part('Launcher_bands', 'Armor', t)
    lips = a.part('ATGM_pod', 'Steel', t)
    bores = a.part('Launcher_bores', 'Undercarriage', t)
    n = 0
    for dz in (.2, -.2):
        for s in (-1, 1):
            x, z = s * xr, zt_ + dz
            tubes.cyl(rt, yr - yf, loc=(x, (yr + yf) / 2, z), rot=FORWARD, seg=12, bevel=.015, bseg=1)
            bands.cyl(rt + .015, .08, loc=(x, yr, z), rot=FORWARD, seg=12, bevel=.01, bseg=1)
            _tube_lip(lips, bores, x, yf, z, rt + .01)
            a.pivot('Muzzle_missile' + ('' if n == 0 else f'__{n:03d}'), (x, yf - .06, z), t)
            n += 1
    for s in (-1, 1):
        bands.box((.24, .16, .6), loc=(s * xr, yf + .5, zt_), bevel=.01, seg=1)
    a.pivot('Muzzle_main', (-xr, yf - .06, zt_ + .2), t)
    a.part('Radar_post', 'Steel', t).cyl(.05, .5, loc=(0, .62, .7), seg=8, bevel=0)
    r = a.pivot('Radar', (0, .62, .95), t)
    _dish(a.part('Radar_dish', 'Armor', r), (0, .05, .3), .42, .28, depth=.12, seg=12, tilt=.3)
    a.part('Radar_arm', 'Steel', r).box((.08, .12, .3), loc=(0, .08, .15), bevel=0)


# ----------------------------------------------------------------------------- C-RAM
def c_ram_a(a):
    """Centurion (A): the flat search radar becomes a big white ball radome on its mast."""
    strip(a, parents=('Radar',))
    r = 'Radar'
    a.part('Radar_turntable', 'Armor', r).cyl(.22, .14, loc=(0, 0, .07), seg=12, bevel=.02, bseg=1)
    a.part('Radar_neck', 'Steel', r).cyl(.12, .3, loc=(0, 0, .25), seg=10, bevel=0)
    a.part('Radar_ball', 'Medical', r).sphere(.66, loc=(0, 0, .95), seg=18, rings=10)
    a.part('Radar_band', 'Team', r).torus(.66, .05, loc=(0, 0, .95), seg=20, ring=5)
    a.part('Radar_beacon', 'Alloy', r).sphere(.06, loc=(0, 0, 1.64), seg=8, rings=4)


def c_ram_b(a):
    """Iron Dome (B): the Phalanx gives way to a tilted canister launcher of twenty interceptors (4 x 5)
    raised 50 degrees on hydraulic rams; `Muzzle_main` / `Muzzle_gun` at the middle of its face."""
    strip(a, ('Pod_*', 'Main_cannon', 'Muzzle_brake', 'Trunnion_hubs'), pivots=('Muzzle_main', 'Muzzle_gun'))
    strip(a, ('Turret_white', 'Base_band'), inside=((-3, -4, 2.1), (3, 3, 9)))
    t = 'Turret'
    pitch = math.radians(50)
    rot = (-pitch, 0, 0)
    L, W, H = 2.3, 1.6, 1.3
    hinge = Vector((0, .55, .5))
    turn = Euler(rot, 'XYZ').to_matrix()
    mid = hinge + turn @ Vector((0, -L / 2 + .15, H / 2 + .05))
    box = _frame(mid, rot)
    a.part('Launcher_box', 'Team', t).box((W, L, H), loc=tuple(mid), rot=rot, bevel=.05, seg=1)
    frame = a.part('Launcher_frame', 'Medical', t)
    for y in (-L / 2 + .12, L / 2 - .12):
        frame.box((W + .06, .14, H + .06), loc=tuple(box @ Vector((0, y, 0))), rot=rot, bevel=.02, seg=1)
    a.part('Launcher_face', 'Undercarriage', t).box((W - .1, .04, H - .1), loc=tuple(box @ Vector((0, -L / 2 - .01, 0))),
                                                    rot=rot, bevel=0)
    for i in range(5):
        for j in range(4):
            _tube_mouth(a, t, box @ _frame((-.6 + i * .3, -L / 2 - .02, -.45 + j * .3), FORWARD), .12, protrude=.05,
                        seg=10, name='Launcher_tubes')
    a.part('Launcher_hinge', 'Steel', t).cyl(.1, W + .3, loc=tuple(hinge), rot=ACROSS, seg=10, bevel=.01, bseg=1)
    for s in (-1, 1):
        a.part('Launcher_rams', 'Steel', t).limb((s * .5, -.35, .35), tuple(box @ Vector((s * .5, -.2, -H / 2))), .1,
                                                .1, bevel=.01)
    face = box @ Vector((0, -L / 2 - .08, 0))
    a.pivot('Muzzle_main', tuple(face), t)
    a.pivot('Muzzle_gun', tuple(face), t)


# ----------------------------------------------------------------------------- gun turret
def gun_turret_a(a):
    """120 mm sniper (A): the gun two metres longer, a long telescopic sight on the roof."""
    pitch = .02
    d = (0, -math.cos(pitch), math.sin(pitch))
    stretch(a, ('Main_cannon', 'Muzzle_brake'), 'Turret', (0, -2.04, .58), d, 2.2, 2.0, pivots=('Muzzle_main',))
    t, top = 'Turret', 1.07
    a.part('Scope_mounts', 'Armor', t).box((.22, .9, .22), loc=(-.72, -.55, top + .16), bevel=.02, seg=1)
    scope = a.part('Scope', 'Steel', t)
    scope.cyl(.11, 1.5, loc=(-.72, -.8, top + .38), rot=FORWARD, seg=12, bevel=.015, bseg=1)
    scope.cyl(.15, .3, loc=(-.72, -1.5, top + .38), rot=FORWARD, seg=12, bevel=.015, bseg=1)       # objective
    a.part('Scope_lens', 'Glass', t).cyl(.12, .03, loc=(-.72, -1.66, top + .38), rot=FORWARD, seg=12, bevel=0)


def gun_turret_b(a):
    """57 mm autocannon (B): two short barrels side by side with flash hiders, a tracking radar dish on a
    post at the turret's rear."""
    strip(a, ('Main_cannon', 'Muzzle_brake'), pivots=('Muzzle_main',))
    t, top = 'Turret', 1.07
    tips = []
    for s, suffix in ((-1, ''), (1, '_2')):
        tips.append(Vector(_barrel(a, t, start_y=-2.0, length=2.0, radius=.08, height=.58, x=s * .3, suffix=suffix,
                                   seg=12, style='flash', brake=(.2, .3, .2), sleeve=(.25, .7, .11), bands=(.6,))))
    a.pivot('Muzzle_main', tuple((tips[0] + tips[1]) / 2), t)
    a.part('Radar_post', 'Steel', t).cyl(.09, .5, loc=(0, 1.65, top + .25), seg=10, bevel=0)
    r = a.pivot('Radar', (0, 1.65, top + .5), t)
    a.part('Radar_mount', 'Armor', r).box((.2, .2, .26), loc=(0, .05, .13), bevel=.02, seg=1)
    _dish(a.part('Radar_dish', 'Medical', r), (0, -.05, .45), .62, .42, depth=.16, seg=14, tilt=.25)
    a.part('Radar_feed', 'Lamp', r).box((.08, .06, .08), loc=(0, -.5, .5), bevel=0)


# ----------------------------------------------------------------------------- rocket battery
ROCKET_BOX = ('Launcher_box', 'Box_frame', 'Box_face', 'Tubes', 'Tubes_bore', 'Tube_covers', 'Box_stencil')


def _rocket_box():
    pitch = math.radians(30)
    rot = (-pitch, 0, 0)
    hinge = Vector((0, .75, 1.0))
    L, W, Hb = 2.5, 1.9, 1.0
    turn = Euler(rot, 'XYZ').to_matrix()
    mid = hinge - turn @ Vector((0, L / 2 - .25, -Hb / 2 - .05))
    return _frame(mid, rot), rot, L, W, Hb


def rocket_turret_a(a):
    """Cluster rockets (A): an open rail rack of sixteen bare tubes (4 x 4) in three frame rings."""
    strip(a, ROCKET_BOX)
    t = 'Turret'
    box, rot, L, W, Hb = _rocket_box()
    tubes = a.part('Launcher_tubes', 'Steel', t)
    for i in range(4):
        for j in range(4):
            x, z = -.69 + i * .46, -.36 + j * .24
            tubes.cyl(.1, L - .1, loc=tuple(box @ Vector((x, 0, z))), rot=(R90 - math.radians(30), 0, 0), seg=10,
                      bevel=0)
            _tube_mouth(a, t, box @ _frame((x, -L / 2 + .03, z), FORWARD), .1, protrude=.05, seg=10,
                        name='Launcher_mouths')
    frame = a.part('Launcher_rack', 'Team', t)
    for y in (-L / 2 + .2, 0, L / 2 - .15):
        for s in (-1, 1):
            frame.box((.1, .12, Hb + .1), loc=tuple(box @ Vector((s * (W / 2 + .02), y, 0))), rot=rot, bevel=0)
            frame.box((W + .14, .12, .1), loc=tuple(box @ Vector((0, y, s * (Hb / 2 + .02)))), rot=rot, bevel=0)
    for s in (-1, 1):
        frame.box((.1, L, .1), loc=tuple(box @ Vector((s * (W / 2 + .02), 0, -Hb / 2 - .02))), rot=rot, bevel=0)


def rocket_turret_b(a):
    """Guided long-range rockets (B): the box stays shut: two big white frangible covers over its face,
    a hazard band round it and a datalink mast on the launcher base."""
    strip(a, ('Box_face', 'Tubes', 'Tubes_bore', 'Tube_covers'))
    t = 'Turret'
    box, rot, L, W, Hb = _rocket_box()
    for x in (-.47, .47):
        a.part('Launcher_covers', 'Medical', t).box((.86, .06, .86), loc=tuple(box @ Vector((x, -L / 2 - .02, 0))),
                                                    rot=rot, bevel=.02, seg=1)
    a.part('Launcher_seam', 'Charred', t).box((.08, .07, Hb - .05), loc=tuple(box @ Vector((0, -L / 2 - .015, 0))),
                                              rot=rot, bevel=0)
    a.part('Launcher_band', 'Hazard', t).box((W + .08, .2, Hb + .08), loc=tuple(box @ Vector((0, .2, 0))), rot=rot,
                                             bevel=.01, seg=1)
    a.part('Datalink_mast', 'Steel', t).cyl(.05, 1.7, loc=(-.9, .9, 1.3), seg=8, bevel=0)
    _dish(a.part('Datalink_dish', 'Medical', t), (-.9, .78, 2.1), .3, .3, depth=.1, seg=10, tilt=.5)


# ----------------------------------------------------------------------------- artillery emplacement
def artillery_emplacement_a(a):
    """Counter-battery howitzer (A): the barrel 1.6 m longer, and a counter-battery radar dish spinning
    on a mast at the pit's left front corner."""
    pitch = math.radians(20)
    at = _axis((0, .15, 1.2), pitch)
    stretch(a, ('Main_cannon', 'Muzzle_brake'), 'Turret', tuple(at(1.05)),
            (0, -math.cos(pitch), math.sin(pitch)), 2.3, 1.6, pivots=('Muzzle_main',))
    mx, my = -2.75, -2.55
    a.part('Radar_trailer', 'Team').box((1.0, 1.3, .36), loc=(mx, my, .5), bevel=.03, seg=1)
    for s in (-1, 1):
        a.part('Radar_wheels', 'Rubber').cyl(.26, .18, loc=(mx + s * .58, my + .2, .27), rot=ACROSS, seg=12, bevel=.03,
                                             bseg=1)
    a.part('Radar_mast', 'Steel').cyl(.09, 1.7, loc=(mx, my, 1.5), seg=10, bevel=0)
    r = a.pivot('Radar', (mx, my, 2.35))
    a.part('Radar_mount', 'Armor', r).box((.3, .3, .3), loc=(0, .1, .15), bevel=.02, seg=1)
    _dish(a.part('Radar_dish', 'Medical', r), (0, -.05, .6), 1.0, .66, depth=.22, seg=14, tilt=.35)
    a.part('Radar_feed', 'Lamp', r).box((.1, .08, .1), loc=(0, -.8, .75), bevel=0)


def artillery_emplacement_b(a):
    """240 mm heavy mortar (B): the howitzer gives way to a squat mortar with a very fat tube raised 60
    degrees (Mortar_tube, `Muzzle_main`) on a turntable base plate, recoil cylinders and a rack of
    240 mm bombs."""
    strip(a, parents=('Turret',), pivots=('Muzzle_main',))
    t = 'Turret'
    a.part('Mortar_base', 'Armor', t).cyl(1.15, .16, loc=(0, 0, .08), seg=20, bevel=.03, bseg=1)
    a.part('Mortar_ring', 'Steel', t).cyl(.75, .1, loc=(0, 0, .2), seg=18, bevel=.015, bseg=1)
    team = a.part('Mortar_carriage', 'Team', t)
    for s in (-1, 1):
        team.box((.14, 1.1, .8), loc=(s * .55, .2, .62), bevel=.03, seg=1, taper=(1, .6))
    pitch = math.radians(60)
    at = _axis((0, .55, .72), pitch)
    rot = (R90 - pitch, 0, 0)
    tube = a.part('Mortar_tube', 'Steel', t)
    L = 3.0
    tube.cyl(.3, L, loc=tuple(at(L / 2 - .5)), rot=rot, seg=18, bevel=.03, bseg=1)
    tube.cyl(.36, .55, loc=tuple(at(-.35)), rot=rot, seg=18, bevel=.04, bseg=1)                 # breech
    for f in (.3, .7):
        a.part('Mortar_tube_bands', 'Armor', t).cyl(.33, .1, loc=tuple(at(L * f - .5)), rot=rot, seg=18, bevel=0)
    a.part('Mortar_tube_lip', 'Undercarriage', t).lathe([(.34, 0), (.34, .14), (.24, .14), (.24, .02)],
                                                       loc=tuple(at(L - .5)), rot=rot, seg=18)
    a.part('Mortar_trunnion', 'Steel', t).cyl(.12, 1.26, loc=(0, .55, .72), rot=ACROSS, seg=10, bevel=.01, bseg=1)
    for s in (-1, 1):
        a.part('Mortar_rams', 'Steel', t).limb((s * .38, -.45, .3), tuple(at(.9, 0, s * .38)), .11, .11, bevel=.01)
    a.pivot('Muzzle_main', tuple(at(L - .5 + .16)), t)
    for s in (-1, 1):
        shells(a, (s * 1.3, .9, .2), 2, 1, r=.12, h=.9, pitch=.26, yaw=R90, parent=t)
        crate(a, (s * 1.25, -.6, .16), size=(.9, .5, .36), yaw=R90, parent=t, band=s < 0)


# ----------------------------------------------------------------------------- heavy fortress
def heavy_turret_a(a):
    """Long-range coastal gun (A): both 155 mm barrels 2.4 m longer, and a wide rangefinder bar across the
    turret roof."""
    stretch(a, ('Main_cannon', 'Main_cannon_2', 'Muzzle_brake', 'Muzzle_brake_2'), 'Turret', (0, 0, 0), (0, -1, 0),
            4.0, 2.4, pivots=('Muzzle_main',))
    t, zt = 'Turret', 1.5
    a.part('Rangefinder', 'Armor', t).box((5.0, .5, .44), loc=(0, .7, zt + .3), bevel=.05, seg=1)
    for s in (-1, 1):
        a.part('Rangefinder_hoods', 'Team', t).box((.5, .6, .56), loc=(s * 2.55, .7, zt + .3), bevel=.05, seg=1)
        a.part('Rangefinder_lens', 'Glass', t).box((.3, .04, .26), loc=(s * 2.55, .38, zt + .32), bevel=0)


def heavy_turret_b(a):
    """Steel fortress (B): thick armour plates standing round the roof edge and on the turret's flanks,
    and two small MG turrets at the roof's front corners (`Mount_gun`, `Mount_gun.001` with `Muzzle_gun`,
    `Muzzle_gun.001`), which turn all the way round."""
    roof = 2.71
    plates = a.part('Roof_plates', 'Armor')
    bolts = a.part('Roof_plate_bolts', 'Steel')
    for side in range(4):
        u = side * R90
        c, s = math.cos(u), math.sin(u)
        for off in (-1.3, 0.0, 1.3):
            x, y = 3.0 * c - off * s, 3.0 * s + off * c
            plates.box((1.1, .36, .32), loc=(x, y, roof + .16), rot=(0, 0, u + R90), bevel=.04, seg=1)
            bolts.bolts([(3.19 * c - (off + k) * s, 3.19 * s + (off + k) * c, roof + .18) for k in (-.3, .3)],
                        r=.045, h=.04, rot=(R90, 0, u + R90), seg=6, bevel=0)
    # Thick plates on the casemate's front and sides, leaning with its batter, clear of the embrasures.
    lean = math.atan((3.0 - 2.79) / 2.2)
    wall = a.part('Wall_plates', 'Armor')
    for (nx, ny), offs in (((0, -1), (0.0,)), ((1, 0), (-1.3, 1.3)), ((-1, 0), (-1.3, 1.3))):
        u = math.atan2(ny, nx) + R90
        for off in offs:
            x, y = 3.12 * nx - off * ny, 3.12 * ny + off * nx
            wall.box((1.5, .36, 1.6), loc=(x, y, 1.04), rot=(lean, 0, u - math.pi), bevel=.05, seg=1)
            bolts.bolts([(x + nx * .2 + (k * ny), y + ny * .2 - (k * nx), z) for k in (-.5, .5) for z in (.6, 1.5)],
                        r=.05, h=.04, rot=(R90 - lean, 0, u - math.pi), seg=6, bevel=0)
    t = 'Turret'
    for s in (-1, 1):
        a.part('Turret_slabs', 'Armor', t).box((.2, 2.9, 1.0), loc=(s * 2.24, .3, .66), bevel=.04, seg=1)
    for k, sx in enumerate((-1, 1)):
        suffix = '' if k == 0 else '__001'
        m = a.pivot('Mount_gun' + suffix, (sx * 2.62, -2.62, roof))
        a.part('Small_turret_ring', 'Hazard', m).cyl(.55, .1, loc=(0, 0, .05), seg=14, bevel=.015, bseg=1)
        a.part('Small_turret', 'Team', m).cyl(.5, .42, r2=.4, loc=(0, 0, .31), seg=14, bevel=.04, bseg=1)
        a.part('Small_turret_top', 'Armor', m).cyl(.32, .08, loc=(0, 0, .56), seg=12, bevel=.02, bseg=1)
        a.part('Small_turret_mg', 'Steel', m).cyl(.05, .8, loc=(0, -.8, .3), rot=FORWARD, seg=8, bevel=0)
        a.part('Small_turret_hider', 'Undercarriage', m).cyl(.07, .14, loc=(0, -1.22, .3), rot=FORWARD, seg=8,
                                                            bevel=0)
        a.pivot('Muzzle_gun' + suffix, (0, -1.3, .3), m)


# ----------------------------------------------------------------------------- Patriot
def _canister_box():
    TH = math.radians(38)
    L = 4.2
    d = Vector((0, -math.cos(TH), math.sin(TH)))
    u = Vector((0, math.sin(TH), math.cos(TH)))
    C = Vector((0, 1.0, .9)) + d * (L / 2) + u * .85
    return _frame(C, (-TH, 0, 0)), (-TH, 0, 0), L


def missile_battery_a(a):
    """PAC-3 (A): one launcher box whose face holds sixteen small tubes (4 x 4) behind a white cover frame."""
    strip(a, ('Launcher', 'Launcher_covers', 'Launcher_plugs', 'Launcher_frame', 'Launcher_stencil', 'Launcher_lugs'))
    t = 'Turret'
    box, rot, L = _canister_box()
    a.part('Launcher', 'Team', t).box((1.7, L, 1.7), loc=tuple(box @ Vector((0, 0, 0))), rot=rot, bevel=.04, seg=1)
    a.part('Launcher_face', 'Medical', t).box((1.64, .05, 1.64), loc=tuple(box @ Vector((0, -L / 2 - .01, 0))),
                                              rot=rot, bevel=.01, seg=1)
    for i in range(4):
        for j in range(4):
            _tube_mouth(a, t, box @ _frame((-.6 + i * .4, -L / 2 - .03, -.6 + j * .4), FORWARD), .14, protrude=.05,
                        seg=10, name='Launcher_tubes')
    frame = a.part('Launcher_frame', 'Armor', t)
    for y in (-L / 2 + .12, 0, L / 2 - .12):
        frame.box((1.8, .1, 1.8), loc=tuple(box @ Vector((0, y, 0))), rot=rot, bevel=.01, seg=1)
    for s in (-1, 1):
        a.part('Launcher_stencil', 'Hazard', t).box((.03, .9, .22), loc=tuple(box @ Vector((s * .86, -1.25, .43))),
                                                    rot=rot, bevel=0)


def missile_battery_b(a):
    """Long-range radar (B): the mast carries a very big search reflector (4.6 m) on its spinning head; the
    launcher keeps its four big canisters."""
    strip(a, parents=('Radar',))
    r = 'Radar'
    a.part('Radar_turntable', 'Armor', r).cyl(.5, .14, loc=(0, 0, .07), seg=14, bevel=.02, bseg=1)
    a.part('Radar_cabin', 'Team', r).box((.9, .8, .6), loc=(0, .3, .44), bevel=.03, seg=1)
    rs = a.part('Radar_struts', 'Steel', r)
    rs.limb((0, 0, .6), (0, -.1, 1.25), .14, .14, bevel=0)
    _dish(a.part('Radar_reflector', 'Medical', r), (0, -.15, 1.3), 2.3, .95, depth=.4, seg=18, tilt=.22)
    horn = Vector((0, -1.9, 1.05))
    for p in ((-1.5, -.6, 1.45), (1.5, -.6, 1.45), (0, -.6, .6)):
        rs.limb(p, tuple(horn), .05, .05, bevel=0)
    a.part('Radar_horn', 'Armor', r).box((.36, .3, .28), loc=tuple(horn + Vector((0, -.06, 0))), bevel=.02, seg=1)
    a.part('Radar_feed', 'Lamp', r).box((.2, .03, .12), loc=tuple(horn + Vector((0, .1, 0))), bevel=0)
    a.part('Radar_iff', 'Armor', r).box((2.6, .14, .18), loc=(0, -.35, 2.3), rot=(.22, 0, 0), bevel=.02, seg=1)
    a.part('Radar_beacon', 'Alloy', r).sphere(.08, loc=(0, .5, .8), seg=8, rings=5)


# ----------------------------------------------------------------------------- drone hangar
DX, DY, ZD = -.55, .7, 3.45
DECK = ((DX - 1.3, DY - 1.65, ZD - .1), (DX + 1.3, DY + 1.65, ZD + 3))
RAIL = ('Launch_rail', 'Rail_tracks', 'Rail_stripe', 'Rail_frame', 'Rail_cable')


def _hangar_muzzles(a, at, rot):
    strip(a, pivots=('Muzzle_door_l', 'Muzzle_main'))
    for name in ('Muzzle_door_l', 'Muzzle_main'):
        a.pivot(name, tuple(at))
        a.pivots[name].rotation_euler = rot


def _lancet(a, m, k=1.0):
    """Lancet loitering munition along -Y of matrix m: a slim body with two cruciform wing sets."""
    body = a.part('Lancet_body', 'Team')
    body.cyl(.085 * k, 1.25 * k, loc=tuple(m @ Vector((0, 0, 0))), rot=(m.to_euler('XYZ').x + R90, 0, 0), seg=10,
             bevel=.02, bseg=1)
    a.part('Lancet_nose', 'Glass').sphere(.08 * k, loc=tuple(m @ Vector((0, -.64 * k, 0))), seg=8, rings=5)
    wings = a.part('Lancet_wings', 'Armor')
    for y, span in ((-.3, .9), (.42, .75)):
        for ang in (math.radians(45), math.radians(-45)):
            wings.box((span * k, .16 * k, .02), loc=tuple(m @ Vector((0, y * k, 0))),
                      rot=tuple((m.to_3x3() @ Matrix.Rotation(ang, 3, 'Y')).to_euler('XYZ')), bevel=0)


def drone_hangar_a(a):
    """Lancet (A): the roof's quadcopter rail and shelf give way to a long catapult rail with a Lancet
    ready on its carriage, and two Lancet cases on the deck."""
    strip(a, RAIL)
    strip(a, ('Drone_*',), inside=DECK)
    pitch = math.radians(16)
    d = Vector((0, -math.cos(pitch), math.sin(pitch)))
    nrm = Vector((0, math.sin(pitch), math.cos(pitch)))
    base = Vector((DX + .35, DY + 1.45, ZD + .25))
    L = 4.4
    rot = (-pitch, 0, 0)
    a.part('Catapult', 'Team').box((.4, L, .14), loc=tuple(base + d * (L / 2)), rot=rot, bevel=.02, seg=1)
    for s in (-1, 1):
        a.part('Catapult_tracks', 'Steel').box((.05, L, .05), loc=tuple(base + d * (L / 2) + nrm * .09 +
                                                                        Vector((s * .13, 0, 0))), rot=rot, bevel=0)
        a.part('Catapult_legs', 'Armor').limb((base.x + s * .18, (base + d * L * .8).y, ZD),
                                              tuple(base + d * (L * .8) + Vector((s * .18, 0, -.05))), .08, .08, bevel=0)
    a.part('Catapult_stripe', 'SafetyStripe').box((.42, .14, .15), loc=tuple(base + d * (L - .08)), rot=rot, bevel=0)
    a.part('Catapult_block', 'Armor').box((.6, .5, .3), loc=(base.x, base.y + .1, ZD + .12), bevel=.02, seg=1)
    ready = base + d * (L - 1.3) + nrm * .26
    _lancet(a, _frame(tuple(ready), rot), k=1.5)
    for k in range(2):
        a.part('Lancet_cases', 'Crate').box((.45, 1.7, .32), loc=(DX - .75, DY + .1, ZD + .16 + k * .34), bevel=.03,
                                            seg=1)
    _hangar_muzzles(a, ready + nrm * .1 + d * .8, rot)


def drone_hangar_b(a):
    """Drone swarm (B): the rail and shelf give way to a big Team rack of twelve open drone bays (4 x 3)
    facing forward, a small quadcopter in each."""
    strip(a, RAIL)
    strip(a, ('Drone_*',), inside=DECK)
    w, d, h = 2.3, 1.3, 1.5
    cx, cy, z0 = DX, DY + .6, ZD
    a.part('Swarm_rack', 'Team').box((w, d, h), loc=(cx, cy, z0 + h / 2), bevel=.04, seg=1)
    inner = a.part('Swarm_bays', 'Undercarriage')
    frame = a.part('Swarm_frames', 'Steel')
    for i in range(4):
        for j in range(3):
            x, z = cx - .81 + i * .54, z0 + .27 + j * .48
            inner.box((.46, .6, .38), loc=(x, cy - d / 2 + .28, z), bevel=0)
            frame.box((.5, .04, .04), loc=(x, cy - d / 2 - .02, z - .21), bevel=0)
            _quadcopter(a, _frame((x, cy - d / 2 + .15, z - .17), (0, 0, 0)), k=.9, full=False)
    a.part('Swarm_lamp', 'TeamGlow').box((w - .2, .05, .08), loc=(cx, cy - d / 2 - .02, z0 + h - .06), bevel=0)
    _hangar_muzzles(a, Vector((cx, cy - d / 2 - .4, z0 + h + .3)), (0, 0, 0))


# ----------------------------------------------------------------------------- shield generator
def shield_tower_a(a):
    """Shield dome (A): a cage of glowing ribs and two rings over the base, closing on the pylon."""
    ribs = a.part('Dome_ribs', 'TeamGlow')
    for k in range(8):
        az = math.radians(22.5) + k * TAU / 8
        pts = []
        for i in range(11):
            e = 1.35 * i / 10
            rr = 3.3 * math.cos(e)
            pts.append((rr * math.cos(az), rr * math.sin(az), .3 + 4.4 * math.sin(e)))
        ribs.tube(pts, .065, seg=6)
    rings = a.part('Dome_rings', 'TeamGlow')
    for z in (2.5, 3.8):
        rr = 3.3 * math.cos(math.asin((z - .3) / 4.4))
        rings.torus(rr, .055, loc=(0, 0, z), seg=32, ring=5)
    a.part('Dome_collar', 'Steel').torus(.74, .1, loc=(0, 0, 4.62), seg=16, ring=6)


def shield_tower_b(a):
    """Tower shields (B): no pylon; a short central emitter and eight small emitter posts (on the four
    capacitors and at the pad's edges), each with a small orb and a glowing beam stub reaching out."""
    strip(a, ('Pylon*',), pivots=('Emitter',))
    a.part('Core_mast', 'Armor').cyl(.6, 1.3, r2=.4, loc=(0, 0, 2.8), seg=8, bevel=.03)
    a.part('Core_rings', 'Steel').torus(.52, .07, loc=(0, 0, 2.7), seg=16, ring=6)
    e = a.pivot('Emitter', (0, 0, 3.85))
    a.part('Emitter_orb', 'TeamGlow', e).sphere(.42, seg=16, rings=10)
    a.part('Emitter_ring', 'Steel', e).torus(.75, .07, seg=24, ring=6)
    posts = a.part('Node_posts', 'Steel')
    orbs = a.part('Node_orbs', 'TeamGlow')
    beams = a.part('Node_beams', 'TeamGlow')
    for x, y, z0, hgt in ([(sx * 2.6, sy * 2.6, 2.2, 1.5) for sx in (-1, 1) for sy in (-1, 1)] +
                          [(3.25, 0, .28, 2.9), (-3.25, 0, .28, 2.9), (0, 3.25, .28, 2.9), (0, -3.25, .28, 2.9)]):
        posts.cyl(.08, hgt, loc=(x, y, z0 + hgt / 2), seg=8, bevel=0)
        a.part('Node_caps', 'Armor').cyl(.16, .12, loc=(x, y, z0 + hgt), seg=10, bevel=.01, bseg=1)
        top = Vector((x, y, z0 + hgt + .25))
        orbs.sphere(.22, loc=tuple(top), seg=12, rings=8)
        out = Vector((x, y, 0)).normalized()
        tip = top + out * .9 + Vector((0, 0, .5))
        beams.limb(tuple(top + out * .2), tuple(tip), .06, .06, bevel=0)


# ----------------------------------------------------------------------------- CP relay
CRATES = ('Crates', 'Crate_cleats', 'Crate_bands')


def _container(a, loc, size, yaw=0.0, mat='Team', tilt=0.0):
    x, y, z = loc
    w, d, h = size
    rot = (tilt, 0, yaw)
    m = _frame((x, y, z + h / 2), rot)
    a.part(f'Container_{mat.lower()}', mat).box((w, d, h), loc=(x, y, z + h / 2), rot=rot, bevel=.03, seg=1)
    ribs = a.part('Container_ribs', 'Armor')
    for k in range(5):
        ribs.box((.05, d + .03, h - .06), loc=tuple(m @ Vector((-w / 2 + .2 + k * (w - .4) / 4, 0, 0))), rot=rot, bevel=0)
    a.part('Container_doors', 'Armor').box((.04, d - .1, h - .1), loc=tuple(m @ Vector((w / 2 + .01, 0, 0))), rot=rot,
                                           bevel=0)


def cp_relay_a(a):
    """Supply relay (A): the crate stack gives way to a comms container with a big dish on its roof and a
    second whip."""
    strip(a, CRATES)
    _container(a, (-.85, -1.4, .24), (2.0, 1.0, 1.0), yaw=.05)
    a.part('Dish_post', 'Steel').cyl(.06, .5, loc=(-.85, -1.4, 1.5), seg=8, bevel=0)
    _dish(a.part('Dish_big', 'Medical'), (-.85, -1.35, 1.9), .62, .62, depth=.18, seg=14, tilt=.9)
    _antenna(a, None, -1.6, -1.7, 1.25, 1.6)


def cp_relay_b(a):
    """Spoils depot (B): no mast; a yellow jib crane with its hook over a pile of captured containers (one
    lying askew on two others) and a loot crate on the hook."""
    strip(a, CRATES + ('Mast', 'Footings', 'Mast_cap', 'Whip', 'Obstruction_light', 'Mast_beacon', 'Dishes',
                       'Dish_mounts', 'Dish_feeds', 'Cables'))
    cx, cy = 1.35, 1.25
    a.part('Crane_base', 'Concrete').box((.8, .8, .2), loc=(cx, cy, .3), bevel=.03, seg=1)
    crane = a.part('Crane', 'CraneYellow')
    crane.cyl(.16, 3.4, loc=(cx, cy, 2.0), seg=12, bevel=.02, bseg=1)
    tip = Vector((0.0, -1.5, 3.6))
    crane.limb((cx, cy, 3.6), tuple(tip), .2, .18, bevel=.02)
    back = Vector((cx, cy, 3.6)) + (Vector((cx, cy, 3.6)) - tip).normalized() * .9
    crane.limb((cx, cy, 3.6), tuple(back), .2, .18, bevel=.02)
    a.part('Crane_weight', 'Concrete').box((.5, .5, .5), loc=tuple(back - Vector((0, 0, .15))), bevel=.03, seg=1)
    a.part('Crane_cab', 'Glass').box((.36, .36, .36), loc=(cx - .25, cy - .1, 3.3), bevel=.02, seg=1)
    a.part('Crane_cable', 'Steel').cyl(.02, .75, loc=(tip.x, tip.y, 3.2), seg=5, bevel=0)
    a.part('Crane_hook', 'Charred').box((.2, .2, .2), loc=(tip.x, tip.y, 2.78), bevel=.02, seg=1)
    crate(a, (tip.x, tip.y, 2.22), size=(.7, .5, .44), yaw=.3)
    _container(a, (-.95, -1.5, .24), (1.6, .8, .8), yaw=.05, mat='ContainerRed')
    _container(a, (.9, -1.45, .24), (1.6, .8, .8), yaw=-.1, mat='ContainerBlue')
    _container(a, (0.0, -1.5, 1.06), (1.5, .78, .76), yaw=.12, mat='ContainerRed', tilt=.05)

BUILDERS = {
    'guard_tower_a': variant('guard_tower', guard_tower_a),
    'guard_tower_b': (guard_tower_b, dict(ao_distance=.7, grime_height=.5)),
    'mg_bunker_a': variant('mg_bunker', mg_bunker_a),
    'mg_bunker_b': variant('mg_bunker', mg_bunker_b),
    'aa_turret_a': variant('aa_turret', aa_turret_a),
    'aa_turret_b': variant('aa_turret', aa_turret_b),
    'ew_tower_a': variant('ew_tower', ew_tower_a),
    'ew_tower_b': variant('ew_tower', ew_tower_b),
    'dragons_teeth_a': variant('dragons_teeth', dragons_teeth_a),
    'dragons_teeth_b': variant('dragons_teeth', dragons_teeth_b),
    'minefield_a': variant('minefield', minefield_a),
    'minefield_b': variant('minefield', minefield_b),
    'atgm_tower_a': variant('atgm_tower', atgm_tower_a),
    'atgm_tower_b': variant('atgm_tower', atgm_tower_b),
    'c_ram_a': variant('c_ram', c_ram_a),
    'c_ram_b': variant('c_ram', c_ram_b),
    'gun_turret_a': variant('gun_turret', gun_turret_a),
    'gun_turret_b': variant('gun_turret', gun_turret_b),
    'rocket_turret_a': variant('rocket_turret', rocket_turret_a),
    'rocket_turret_b': variant('rocket_turret', rocket_turret_b),
    'artillery_emplacement_a': variant('artillery_emplacement', artillery_emplacement_a),
    'artillery_emplacement_b': variant('artillery_emplacement', artillery_emplacement_b),
    'heavy_turret_a': variant('heavy_turret', heavy_turret_a),
    'heavy_turret_b': variant('heavy_turret', heavy_turret_b),
    'missile_battery_a': variant('missile_battery', missile_battery_a),
    'missile_battery_b': variant('missile_battery', missile_battery_b),
    'drone_hangar_a': variant('drone_hangar', drone_hangar_a),
    'drone_hangar_b': variant('drone_hangar', drone_hangar_b),
    'shield_tower_a': variant('shield_tower', shield_tower_a),
    'shield_tower_b': variant('shield_tower', shield_tower_b),
    'cp_relay_a': variant('cp_relay', cp_relay_a),
    'cp_relay_b': variant('cp_relay', cp_relay_b),
}
