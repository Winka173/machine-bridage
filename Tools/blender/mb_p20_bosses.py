"""Machine Brigade prompt 20 pass 2 bosses (DECISIONS 19E): first-pass models on the shared kit.

New bosses:
  * moloch: Varga's mobile factory, 24 x 13 m: a long tracked hull with a raised workshop block, four 120 mm turrets on
    the corners (`Turret` front left with `Muzzle_main`; `Mount_gun` / `.001` / `.002`), a flak mount on the roof
    (`Mount_mg`), two workshop doors at the back (`Part_door_l` / `Part_door_r`), two track units (`Part_track_l/r`),
    smokestacks.
  * daedalus: Aurel's orbital lander, on the Silver Bug's hull, wings, tail and engines (mb_orbital's builders, shared
    to save work) with a cargo hump, three drop-pod bays under it (`Pod_bay_1..3`), two hanging 30 mm guns
    (`Mount_gun`, `Mount_gun.001`), the point-defence lasers and main engine (`Pd_laser_l/r`, `Thruster_main`).
  * kronos: a bucket-wheel excavator (Bagger 288 lineage), 40 x 16 m: four track units (`Part_track_fl/fr/rl/rr`), a
    turntable superstructure, the boom (`Part_boom`) and the bucket wheel at its tip (`Part_wheel`), the control cab
    (`Part_cab`), two 30 mm turrets (`Turret` with `Muzzle_main`, `Mount_gun`) and a rocket pod (`Mount_rocket`).
  * typhon: a missile submarine (Typhoon lineage), 58 x 12 m, origin on the waterline: a broad hull, the sail
    (`Part_sail`) with its SAM launcher (`Mount_missile`), two banks of launch doors (`Part_doors_l/r`), the rudder
    (`Part_rudder`), the bow sonar (`Part_sonar`) and a 100 mm deck gun (`Mount_gun`) for phase 3.
  * ixion: a giant wheel (Tsar Tank lineage), 17 x 12 m: two 9 m wheels (`Part_wheel_l/r`), the hub gondola with its
    76 mm gun (`Turret`, `Muzzle_main`) and the tail with its steering wheel (`Part_steer`).
  * caspian: an ekranoplan (Lun lineage), 52 x 32 m, origin on the water: the hull, short wings (`Part_wing_l/r`), the
    tail, the jet engines on the nose canards (`Part_engines`), the anti-ship launcher on its back (`Part_launcher`)
    and a CIWS in the tail (`Mount_gun`).
Existing bosses (prompt 20 F.3's new weapons, each builder wrapping the current one, no node renamed or moved):
fortress_bastion (a 155 mm casemate `Mount_gun.004`, ZU-23 mounts `Mount_mg` / `.001`), behemoth (120 mm flank guns
`Mount_gun.001` / `.002`, a rocket pod `Mount_rocket`), leviathan (127 mm secondaries `Mount_gun.002` / `.003`), drone_mothership (belly 30 mm guns
`Mount_gun` / `.001`, a second drone bay `Mount_missile.001`), command_airship (105 mm gun pods `Mount_gun.002` /
`.003`), nuke_train (a 152 mm gun car `Part_gun152` > `Mount_gun`, an AA car `Part_aa` > `Mount_mg.002`), silver_bug
(two phase-3 turrets `Mount_gun.002` / `.003`).

Conventions are mb_vehicles'/mb_phase8's: metres, +Z up, Blender -Y is the front, +X the vehicle's left; data
positions (x right, y forward) are Blender (-x, -y). Suffixed pivots are authored `Mount_gun__001` (mb_phase2._suffixed).
Jötunn's second 203 mm and SAM use the mobile fortress model's own spare `Mount_gun` and `Mount_missile.001`
(built for its variants). These are first passes to be refined (ASSET_DEBT).

Headless: blender --background --python Tools/blender/build_assets.py -- moloch kronos typhon ixion caspian daedalus
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import mb_bosses  # noqa: E402
import mb_bosses2  # noqa: E402
import mb_naval  # noqa: E402
import mb_orbital  # noqa: E402
import mb_p16_arms  # noqa: E402
import mb_phase8  # noqa: E402
from mb_phase2 import _suffixed, dotted  # noqa: E402
from mb_phase8 import autocannon, ciws, pv  # noqa: E402
from mb_vehicles import FORWARD, R90  # noqa: E402

AXIS_X = (0, R90, 0)   # a cylinder's axis along X (wheels, rollers)


def _tag(name):
    return name.replace('.', '_').replace('__', '_')


def gun_turret(a, mount, muzzle, loc, parent=None, w=2.6, d=3.2, h=1.2, barrel=5.2, r=.13, twin=False, body='Team'):
    """A heavy gun turret on its own yaw pivot `mount`: a sloped house, a mantlet, one or two long barrels with
    a muzzle brake; `muzzle` at the (left) barrel's tip, between the two for a twin."""
    tag = _tag(mount)
    pk = dotted(parent) if parent else None
    a.part(f'T_ring_{tag}', 'Armor', pk).cyl(w * .45, .12, loc=(loc[0], loc[1], loc[2] + .04), seg=18, bevel=.02, bseg=1)
    m = pv(a, mount, loc, parent)
    a.part(f'T_house_{tag}', body, m).box((w, d, h), loc=(0, .1, h / 2 + .05), bevel=.1, seg=1, taper=(.82, .86))
    arm = a.part(f'T_armor_{tag}', 'Armor', m)
    arm.box((w * .5, .5, h * .6), loc=(0, -d / 2 - .1, h * .55), bevel=.05, seg=1)
    steel = a.part(f'T_barrel_{tag}', 'Steel', m)
    brake = a.part(f'T_brake_{tag}', 'Undercarriage', m)
    bores = a.part(f'T_bore_{tag}', 'Charred', m)
    zb = h * .55
    xs = (-w * .18, w * .18) if twin else (0.0,)
    front = -d / 2 - .3
    tip = front - barrel
    for x in xs:
        steel.cyl(r, barrel, loc=(x, front - barrel / 2, zb), rot=FORWARD, seg=12, bevel=0)
        brake.cyl(r * 1.5, .5, loc=(x, tip + .25, zb), rot=FORWARD, seg=12, bevel=.01, bseg=1)
        bores.cyl(r * .72, .02, loc=(x, tip - .005, zb), rot=FORWARD, seg=10, bevel=0)
    arm.box((.36, .5, .3), loc=(w * .3, .4, h + .15), bevel=.03, seg=1)
    pv(a, muzzle, (0.0 if twin else xs[0], tip, zb), mount)
    return m


def hanging_gun(a, mount, muzzle, loc, length=2.4, r=.08):
    """A ball turret under a belly: its barrel below the pivot, pointing forward."""
    tag = _tag(mount)
    m = pv(a, mount, loc)
    a.part(f'H_ball_{tag}', 'Armor', m).sphere((.62, .62, .5), loc=(0, 0, -.35), seg=14, rings=6)
    a.part(f'H_barrel_{tag}', 'Steel', m).cyl(r, length, loc=(0, -length / 2 - .3, -.45), rot=FORWARD, seg=10, bevel=0)
    a.part(f'H_bore_{tag}', 'Charred', m).cyl(r * .7, .02, loc=(0, -length - .31, -.45), rot=FORWARD, seg=8, bevel=0)
    pv(a, muzzle, (0, -length - .3, -.45), mount)
    return m


def rocket_box(a, mount, muzzle, loc, parent=None, size=(1.6, 2.0, 1.0)):
    """A box launcher of rocket tubes on its own pivot, tubes laid a little up, facing forward."""
    tag = _tag(mount)
    m = pv(a, mount, loc, parent)
    w, d, h = size
    a.part(f'R_base_{tag}', 'Armor', m).box((w * .6, d * .5, .4), loc=(0, 0, .2), bevel=.04, seg=1)
    a.part(f'R_box_{tag}', 'Team', m).box((w, d, h), loc=(0, 0, .4 + h / 2), rot=(.12, 0, 0), bevel=.05, seg=1)
    faces = a.part(f'R_tubes_{tag}', 'Charred', m)
    for i in range(3):
        for j in range(2):
            faces.cyl(.12, .04, loc=(-w * .3 + i * w * .3, -d / 2 - .02, .4 + h * .3 + j * h * .4), rot=FORWARD, seg=8, bevel=0)
    pv(a, muzzle, (0, -d / 2 - .05, .4 + h / 2), mount)
    return m


def track_unit(a, name, x, y, length, height=2.2, width=2.4, parent=None):
    """A track unit on `name` (its part empty): rubber track round a frame, road wheels, a sprocket."""
    p = pv(a, name, (x, y, 0), parent)
    a.part(f'Tr_belt_{_tag(name)}', 'Rubber', p).box((width, length, height), loc=(0, 0, height / 2 + .05), bevel=height * .45, seg=3)
    wheels = a.part(f'Tr_wheels_{_tag(name)}', 'Undercarriage', p)
    n = max(3, int(length / 1.6))
    for k in range(n):
        yy = -length / 2 + height * .5 + k * (length - height) / max(1, n - 1)
        for s in (-1, 1):
            wheels.cyl(height * .32, .12, loc=(s * (width / 2 + .02), yy, height * .45), rot=AXIS_X, seg=14, bevel=0)
    a.part(f'Tr_guard_{_tag(name)}', 'Armor', p).box((width + .2, length * .96, .16), loc=(0, 0, height + .12), bevel=.04, seg=1)
    return p


def stripe_door(a, name, loc, w=3.4, h=3.6):
    """A workshop door (its part empty): an armoured slab in a hazard-striped frame, on the hull's rear face."""
    p = pv(a, name, loc)
    a.part(f'Door_{_tag(name)}', 'Armor', p).box((w, .3, h), loc=(0, .15, h / 2), bevel=.05, seg=1)
    frame = a.part(f'Door_frame_{_tag(name)}', 'Hazard', p)
    frame.box((w + .5, .2, .25), loc=(0, .1, h + .1), bevel=.02, seg=1)
    for s in (-1, 1):
        frame.box((.25, .2, h), loc=(s * (w / 2 + .12), .1, h / 2), bevel=.02, seg=1)
    a.part(f'Door_lamp_{_tag(name)}', 'Lamp', p).box((.3, .1, .2), loc=(w / 2 - .3, .32, h + .35), bevel=0)
    return p


# ============================================================================== Moloch

def moloch(a):
    """Varga's mobile factory: see the module docstring."""
    _suffixed(a)
    hull = a.part('Hull', 'Team')
    armor = a.part('Hull_armor', 'Armor')
    steel = a.part('Hull_steel', 'Steel')
    for s, name in ((1, 'Part_track_l'), (-1, 'Part_track_r')):
        track_unit(a, name, s * 5.9, 0, 23, height=2.6, width=2.4)
    hull.box((9.4, 22.4, 3.2), loc=(0, 0, 3.4), bevel=.3, seg=2, taper=(.96, .98))                    # z 1.8 .. 5.0
    armor.prism([(-11.8, 2.0), (-11.8, 3.6), (-10.2, 5.2), (-8.5, 5.2), (-8.5, 2.0)], 9.8, axis='X', bevel=.1, seg=1)  # glacis
    a.part('Workshop', 'Team').box((8.2, 13.0, 3.6), loc=(0, 3.2, 6.8), bevel=.25, seg=2)              # z 5 .. 8.6
    armor.box((8.8, 1.0, 1.0), loc=(0, -3.6, 5.3), bevel=.1, seg=1)
    for x in (-2.2, 2.2):
        steel.cyl(.6, 3.6, loc=(x, 7.6, 10.0), seg=14, bevel=.04, bseg=1)                                 # smokestacks
        a.part('Stack_tops', 'Charred').cyl(.62, .3, loc=(x, 7.6, 11.9), seg=14, bevel=0)
    a.part('Vents', 'Undercarriage').grille(5.0, 1.4, loc=(0, 5.0, 8.62), rot=(-R90, 0, 0), slats=8)
    for y in (-2.0, 1.0, 4.0, 7.0):
        armor.box((9.6, .5, .3), loc=(0, y, 5.05), bevel=.03, seg=1)                                       # rib plates
    # The four corner turrets (x right, y forward in the data: fl (-4.4, 7.6), fr (4.4, 7.6), rl, rr).
    gun_turret(a, 'Turret', 'Muzzle_main', (4.4, -7.6, 5.0), w=2.8, d=3.4)
    gun_turret(a, 'Mount_gun', 'Muzzle_gun', (-4.4, -7.6, 5.0), w=2.8, d=3.4)
    gun_turret(a, 'Mount_gun.001', 'Muzzle_gun.001', (4.4, 4.6, 8.6), w=2.6, d=3.2)
    gun_turret(a, 'Mount_gun.002', 'Muzzle_gun.002', (-4.4, 4.6, 8.6), w=2.6, d=3.2)
    autocannon(a, 'Mount_mg', (0, -1.4, 8.6), length=2.6, size=(1.5, 1.7, .7))
    stripe_door(a, 'Part_door_l', (3.0, 11.3, 1.9))
    stripe_door(a, 'Part_door_r', (-3.0, 11.3, 1.9))


# ============================================================================== Daedalus

def daedalus(a):
    """Aurel's orbital lander on the Silver Bug's airframe: see the module docstring."""
    _suffixed(a)
    rng = random.Random(1977)
    mb_orbital._build_hull(a, 0.0, False, rng)
    mb_orbital._build_wing(a, 1, 0.0, torn=False)
    mb_orbital._build_wing(a, -1, 0.0, torn=False)
    mb_orbital._build_tail_fin(a, 0.0)
    mb_orbital._build_engines(a, mb_orbital._node('Thruster_main', 0.0), torn=False)
    mb_orbital._build_pd_laser(a, 'Pd_laser_l', mb_orbital._node('Pd_laser_l', 0.0))
    mb_orbital._build_pd_laser(a, 'Pd_laser_r', mb_orbital._node('Pd_laser_r', 0.0))
    # The cargo hump over the troop deck and its hatches.
    hump = a.part('Cargo_hump', 'Team')
    hump.box((7.0, 16.0, 2.6), loc=(0, 1.0, 3.2), bevel=.8, seg=3, taper=(.8, .9))
    a.part('Cargo_ribs', 'Alloy').box((7.4, .4, .5), loc=(0, -4.0, 3.9), bevel=.1, seg=1)
    a.part('Cargo_lamps', 'TeamGlow').box((5.6, .2, .12), loc=(0, -7.0, 3.6), bevel=0)
    for i, (x, y) in enumerate(((4.0, 2.0), (0.0, 5.0), (-4.0, 2.0))):
        p = pv(a, f'Pod_bay_{i + 1}', (x, y, -2.0))
        a.part(f'Bay_frame_{i + 1}', 'Armor', p).box((3.0, 3.6, .5), loc=(0, 0, 0), bevel=.1, seg=1)
        a.part(f'Bay_pod_{i + 1}', 'Team', p).cyl(1.0, 1.6, loc=(0, 0, -.8), seg=14, r2=.7, bevel=.05, bseg=1)
        a.part(f'Bay_glow_{i + 1}', 'Energy', p).cyl(.5, .05, loc=(0, 0, -1.62), seg=12, bevel=0)
    hanging_gun(a, 'Mount_gun', 'Muzzle_gun', (2.4, -6.0, -1.4))
    hanging_gun(a, 'Mount_gun.001', 'Muzzle_gun.001', (-2.4, -6.0, -1.4))


# ============================================================================== Kronos

def kronos(a):
    """A bucket-wheel excavator: see the module docstring."""
    _suffixed(a)
    for name, x, y in (('Part_track_fl', 6.5, -8.0), ('Part_track_fr', -6.5, -8.0), ('Part_track_rl', 6.5, 8.0), ('Part_track_rr', -6.5, 8.0)):
        track_unit(a, name, x, y, 9.0, height=2.4, width=3.0)
    frame = a.part('Undercarriage_frame', 'Undercarriage')
    frame.box((13.0, 22.0, 1.4), loc=(0, 0, 3.2), bevel=.2, seg=1)
    body = a.part('Body', 'Team')
    body.cyl(7.0, 1.2, loc=(0, 0, 4.4), seg=32, bevel=.1, bseg=1)                                       # turntable
    body.box((11.0, 20.0, 4.6), loc=(0, 2.0, 7.3), bevel=.4, seg=2)                                     # z 5 .. 9.6
    armor = a.part('Body_armor', 'Armor')
    armor.box((11.6, 1.0, 3.4), loc=(0, -8.0, 7.0), bevel=.2, seg=1)
    for y in (-3.0, 3.0, 9.0):
        armor.box((11.4, .6, .4), loc=(0, y, 9.7), bevel=.05, seg=1)
    # Counterweight boom at the back.
    a.part('Counterweight', 'Armor').box((6.0, 5.0, 3.6), loc=(0, 17.0, 9.0), bevel=.3, seg=1)
    a.part('Tail_girder', 'Steel').limb((0, 11.5, 9.0), (0, 15.0, 9.4), 2.4, 1.6)
    # The boom and the wheel at its tip.
    pb = pv(a, 'Part_boom', (0, -13.0, 10.0))
    girder = a.part('Boom_girder', 'Hazard', pb)
    girder.limb((0, 5.0, -.6), (0, -8.0, -.8), 2.2, 2.0)
    steel = a.part('Boom_steel', 'Steel', pb)
    for s in (-1, 1):
        steel.limb((s * .9, 4.0, .6), (s * .9, -7.0, .2), .25, .25)
    pw = pv(a, 'Part_wheel', (0, -22.0, 9.0))
    wheel = a.part('Wheel_rim', 'Steel', pw)
    wheel.torus(5.6, .45, loc=(0, 0, 0), rot=AXIS_X, seg=36, ring=8)
    wheel.cyl(1.2, 2.8, loc=(0, 0, 0), rot=AXIS_X, seg=16, bevel=.05, bseg=1)
    spokes = a.part('Wheel_spokes', 'Armor', pw)
    buckets = a.part('Wheel_buckets', 'Team', pw)
    teeth = a.part('Wheel_teeth', 'Charred', pw)
    for k in range(12):
        ang = k * math.tau / 12
        c, s = math.cos(ang), math.sin(ang)
        spokes.limb((0, 0, 0), (0, 5.3 * s, 5.3 * c), .3, .3)
        buckets.box((2.6, 1.6, 1.4), loc=(0, 6.1 * s, 6.1 * c), rot=(-ang, 0, 0), bevel=.15, seg=1)
        teeth.box((2.4, .3, .3), loc=(0, 6.9 * s, 6.9 * c), rot=(-ang, 0, 0), bevel=0)
    pc = pv(a, 'Part_cab', (-3.0, -4.0, 9.6))
    a.part('Cab_box', 'Team', pc).box((3.0, 3.2, 2.6), loc=(0, 0, 1.3), bevel=.15, seg=1)
    a.part('Cab_glass', 'Glass', pc).box((2.6, .1, 1.1), loc=(0, -1.62, 1.6), bevel=0)
    gun_turret(a, 'Turret', 'Muzzle_main', (4.0, 2.0, 9.6), w=1.8, d=2.2, h=.9, barrel=2.8, r=.07, twin=True)
    autocannon(a, 'Mount_gun', (-4.0, 2.0, 9.6), length=2.8, size=(1.6, 1.9, .8))
    rocket_box(a, 'Mount_rocket', 'Muzzle_rocket', (0, 9.0, 9.6))


# ============================================================================== Typhon

def typhon(a):
    """A missile submarine: see the module docstring."""
    _suffixed(a)
    hull = a.part('Hull', 'Team')
    hull.sphere((6.0, 29.0, 3.6), loc=(0, 0, .2), seg=28, rings=12)
    a.part('Casing', 'Armor').box((7.6, 30.0, 1.0), loc=(0, 1.0, 3.3), bevel=.45, seg=2)                 # deck casing
    ps = pv(a, 'Part_sail', (0, -6.0, 3.6))
    a.part('Sail_body', 'Team', ps).box((3.2, 9.0, 5.2), loc=(0, 0, 2.6), bevel=.8, seg=3, taper=(.8, .7))
    a.part('Sail_planes', 'Armor', ps).box((8.6, 1.6, .3), loc=(0, -1.0, 3.2), bevel=.12, seg=1)
    a.part('Sail_masts', 'Steel', ps).cyl(.15, 2.2, loc=(0, 1.8, 6.3), seg=8, bevel=0)
    rocket_box(a, 'Mount_missile', 'Muzzle_missile', (0, -3.0, 9.0), size=(1.4, 1.8, .9))
    for s, name in ((1, 'Part_doors_l'), (-1, 'Part_doors_r')):
        pd = pv(a, name, (s * 2.2, 6.0, 3.8))
        lids = a.part(f'Doors_{_tag(name)}', 'Armor', pd)
        rims = a.part(f'Doors_rim_{_tag(name)}', 'Hazard', pd)
        for k in range(5):
            lids.cyl(.8, .16, loc=(0, -4.0 + k * 2.0, 0), seg=16, bevel=.03, bseg=1)
            rims.torus(.82, .06, loc=(0, -4.0 + k * 2.0, .08), seg=16, ring=6)
    pr = pv(a, 'Part_rudder', (0, 27.0, 1.0))
    fins = a.part('Rudder_fins', 'Armor', pr)
    fins.box((.4, 3.2, 5.0), loc=(0, 0, 1.6), bevel=.1, seg=1)
    fins.box((7.0, 2.6, .35), loc=(0, .2, 0), bevel=.1, seg=1)
    a.part('Screws', 'Steel', pr).cyl(1.2, .5, loc=(0, 2.2, -.4), rot=FORWARD, seg=12, bevel=.05, bseg=1)
    pn = pv(a, 'Part_sonar', (0, -26.0, 1.2))
    a.part('Sonar_dome', 'Alloy', pn).sphere((2.4, 2.8, 1.8), loc=(0, 0, 0), seg=18, rings=8)
    autocannon(a, 'Mount_gun', (0, -16.0, 3.8), length=4.0, r=.1, size=(1.9, 2.4, 1.0))


# ============================================================================== Ixion

def ixion(a):
    """A giant wheel: see the module docstring."""
    _suffixed(a)
    for s, name in ((1, 'Part_wheel_l'), (-1, 'Part_wheel_r')):
        p = pv(a, name, (s * 5.2, -3.0, 4.6))
        rim = a.part(f'Rim_{_tag(name)}', 'Steel', p)
        rim.torus(4.3, .32, loc=(0, 0, 0), rot=AXIS_X, seg=40, ring=8)
        tread = a.part(f'Tread_{_tag(name)}', 'Undercarriage', p)
        tread.cyl(4.55, .9, loc=(0, 0, 0), rot=AXIS_X, seg=40, bevel=.08, bseg=1)
        spokes = a.part(f'Spokes_{_tag(name)}', 'Team', p)
        for k in range(10):
            ang = k * math.tau / 10
            spokes.limb((0, 0, 0), (0, 4.1 * math.sin(ang), 4.1 * math.cos(ang)), .18, .28)
        a.part(f'Hub_{_tag(name)}', 'Armor', p).cyl(.8, 1.4, loc=(0, 0, 0), rot=AXIS_X, seg=16, bevel=.05, bseg=1)
    axle = a.part('Axle', 'Undercarriage')
    axle.cyl(.45, 10.0, loc=(0, -3.0, 4.6), rot=AXIS_X, seg=14, bevel=0)
    body = a.part('Gondola', 'Team')
    body.box((3.4, 4.6, 2.4), loc=(0, -2.6, 6.2), bevel=.25, seg=2)
    a.part('Gondola_armor', 'Armor').box((3.0, 1.0, 1.2), loc=(0, -5.0, 5.6), bevel=.15, seg=1)
    tail = a.part('Tail', 'Undercarriage')
    tail.limb((0, -1.0, 5.2), (0, 7.2, 1.8), 1.0, .9)
    tail.limb((.6, -1.0, 4.2), (.6, 7.0, 1.5), .3, .3)
    tail.limb((-.6, -1.0, 4.2), (-.6, 7.0, 1.5), .3, .3)
    ps = pv(a, 'Part_steer', (0, 7.6, 1.3))
    a.part('Steer_wheel', 'Rubber', ps).cyl(1.2, .8, loc=(0, 0, 0), rot=AXIS_X, seg=18, bevel=.1, bseg=1)
    a.part('Steer_fork', 'Steel', ps).box((1.4, .3, 1.6), loc=(0, 0, .8), bevel=.05, seg=1)
    gun_turret(a, 'Turret', 'Muzzle_main', (0, -1.0, 7.4), w=1.9, d=2.2, h=1.0, barrel=3.2, r=.09)


# ============================================================================== Caspian

def caspian(a):
    """An ekranoplan: see the module docstring."""
    _suffixed(a)
    hull = a.part('Hull', 'Team')
    hull.box((5.4, 44.0, 5.6), loc=(0, 2.0, 3.6), bevel=1.2, seg=3, taper=(.9, .95))                   # z .8 .. 6.4
    hull.sphere((2.7, 6.0, 2.8), loc=(0, -20.0, 3.6), seg=18, rings=8)                                  # nose
    a.part('Hull_bottom', 'Undercarriage').box((5.0, 40.0, .6), loc=(0, 2.0, .9), bevel=.2, seg=1)
    a.part('Cockpit', 'Glass').box((2.6, 2.4, .8), loc=(0, -17.0, 6.1), rot=(-.3, 0, 0), bevel=.1, seg=1)
    for s, name in ((1, 'Part_wing_l'), (-1, 'Part_wing_r')):
        p = pv(a, name, (s * 11.0, 0, 2.6))
        a.part(f'Wing_{_tag(name)}', 'Team', p).box((16.0, 9.0, .7), loc=(0, 0, 0), bevel=.25, seg=2, taper=(1, .7))
        a.part(f'Float_{_tag(name)}', 'Armor', p).box((1.2, 7.0, 1.4), loc=(s * 7.8, 0, -.7), bevel=.3, seg=1)
    fin = a.part('Tail_fin', 'Team')
    fin.box((.8, 8.0, 10.0), loc=(0, 21.0, 10.0), bevel=.2, seg=1, taper=(.6, .6))
    fin.box((18.0, 5.0, .6), loc=(0, 22.0, 15.0), bevel=.2, seg=1)
    pe = pv(a, 'Part_engines', (0, -18.0, 5.4))
    canard = a.part('Canards', 'Armor', pe)
    canard.box((14.0, 3.0, .5), loc=(0, 0, 0), bevel=.15, seg=1)
    jets = a.part('Jets', 'Steel', pe)
    glow = a.part('Jet_glow', 'Energy', pe)
    for i in range(4):
        for s in (-1, 1):
            x = s * (1.6 + i * 1.5)
            jets.cyl(.62, 3.4, loc=(x, 0, 1.0), rot=FORWARD, seg=12, bevel=.05, bseg=1)
            glow.cyl(.4, .05, loc=(x, 1.73, 1.0), rot=FORWARD, seg=10, bevel=0)
    pl = pv(a, 'Part_launcher', (0, 2.0, 6.4))
    tubes = a.part('Launch_canisters', 'Team', pl)
    for k in range(3):
        for s in (-1, 1):
            tubes.cyl(.75, 7.0, loc=(s * .95, -3.0 + k * 3.0, .9 + k * .5), rot=(R90 - .15, 0, 0), seg=14, bevel=.05, bseg=1)
    ciws(a, 'Mount_gun', (0, 17.0, 6.4))


# ============================================================================== the existing bosses' new weapons (F.3)

def fortress_bastion(a):
    """mb_p16_arms.fortress_bastion with a 155 mm casemate on the bow and two ZU-23 mounts on the flanks."""
    mb_p16_arms.fortress_bastion(a)
    a.part('Casemate', 'Armor').box((3.2, 3.0, 2.4), loc=(0, -7.6, 3.4), bevel=.2, seg=1, taper=(.85, .8))
    gun_turret(a, 'Mount_gun.004', 'Muzzle_gun.004', (0, -8.6, 3.2), w=1.8, d=1.8, h=1.0, barrel=4.4, r=.11)
    for s, mount in ((1, 'Mount_mg'), (-1, 'Mount_mg.001')):
        autocannon(a, mount, (s * 3.9, 1.5, 5.2), length=1.6, r=.04, size=(1.0, 1.1, .5), body='Armor')


def behemoth(a):
    """mb_bosses2.behemoth with two 120 mm guns on its flanks and a rocket pod on its back."""
    _suffixed(a)
    mb_bosses2.behemoth(a)
    for s, mount in ((1, 'Mount_gun.001'), (-1, 'Mount_gun.002')):
        a.part(f'Sponson_{_tag(mount)}', 'Armor').box((1.4, 2.6, 1.2), loc=(s * 3.4, -1.0, 2.2), bevel=.12, seg=1)
        gun_turret(a, mount, mount.replace('Mount_', 'Muzzle_'), (s * 3.4, -1.0, 2.6), w=1.4, d=1.8, h=.8, barrel=3.8, r=.1)
    rocket_box(a, 'Mount_rocket', 'Muzzle_rocket', (0, 3.8, 4.4))


def leviathan(a):
    """mb_naval.leviathan with two 127 mm secondaries on the beam."""
    mb_naval.leviathan(a)
    for s, mount in ((1, 'Mount_gun.002'), (-1, 'Mount_gun.003')):
        autocannon(a, mount, (s * 5.2, -4.0, 6.0), length=4.2, r=.1, size=(2.0, 2.6, 1.1))


def drone_mothership(a):
    """mb_bosses.drone_mothership with two hanging 30 mm guns and a second drone bay."""
    _suffixed(a)
    mb_bosses2.drone_mothership(a)
    hanging_gun(a, 'Mount_gun', 'Muzzle_gun', (2.2, -6.0, -5.2))
    hanging_gun(a, 'Mount_gun.001', 'Muzzle_gun.001', (-2.2, -6.0, -5.2))
    m = pv(a, 'Mount_missile.001', (0, 6.0, -4.2))
    a.part('Bay2_frame', 'Armor', m).box((3.0, 3.4, .6), loc=(0, 0, 0), bevel=.1, seg=1)
    a.part('Bay2_doors', 'Hazard', m).box((2.6, 3.0, .1), loc=(0, 0, -.35), bevel=0)
    pv(a, 'Muzzle_missile.001', (0, 0, -.5), 'Mount_missile.001')


def command_airship(a):
    """mb_phase8.command_airship with two 105 mm gun pods slung either side."""
    mb_phase8.command_airship(a)
    for s, mount in ((1, 'Mount_gun.002'), (-1, 'Mount_gun.003')):
        a.part(f'Pod_strut_{_tag(mount)}', 'Steel').limb((s * 5.5, 0, -1.0), (s * 7.5, 0, -2.4), .3, .3)
        a.part(f'Pod_{_tag(mount)}', 'Team').box((1.8, 4.4, 1.6), loc=(s * 7.5, 0, -3.0), bevel=.4, seg=2)
        hanging_gun(a, mount, mount.replace('Mount_', 'Muzzle_'), (s * 7.5, -1.6, -3.4), length=3.0, r=.1)


def nuke_train(a):
    """mb_p16_arms.nuke_train with two more flatcars: a 152 mm gun car and an AA car."""
    mb_p16_arms.nuke_train(a)
    mb_p16_arms._flatcar(a, 21.0, 25.05, 20.24, tail=False)
    mb_p16_arms._flatcar(a, 25.81, 29.86, 25.05, tail=True)
    pg = pv(a, 'Part_gun152', (0, 23.0, 1.62))
    gun_turret(a, 'Mount_gun', 'Muzzle_gun', (0, 0, .1), parent='Part_gun152', w=2.2, d=2.8, h=1.1, barrel=5.0, r=.12)
    pa = pv(a, 'Part_aa', (0, 27.8, 1.62))
    autocannon(a, 'Mount_mg.002', (0, 0, .1), parent='Part_aa', length=2.4, size=(1.5, 1.7, .7))
    del pg, pa


def silver_bug(a):
    """mb_orbital.silver_bug with two more turrets round the hull (they wake in phase 3)."""
    mb_orbital.silver_bug(a)
    for s, mount in ((1, 'Mount_gun.002'), (-1, 'Mount_gun.003')):
        autocannon(a, mount, (s * 6.5, 6.0, 2.2), length=2.4, size=(1.3, 1.5, .62))


BUILDERS = {
    'moloch': (moloch, dict(ao_distance=1.2, grime_height=1.0)),
    'daedalus': (daedalus, dict(ao_distance=.4, ground=False)),
    'kronos': (kronos, dict(ao_distance=1.4, grime_height=1.2)),
    'typhon': (typhon, dict(ao_distance=1.0, grime_height=.3)),
    'ixion': (ixion, dict(ao_distance=1.0, grime_height=.8)),
    'caspian': (caspian, dict(ao_distance=1.0, grime_height=.3)),
    'fortress_bastion': (fortress_bastion, dict(ao_distance=1.1, grime_height=1.0)),
    'behemoth': (behemoth, dict(ao_distance=.9, grime_height=.8)),
    'leviathan': (leviathan, dict(ao_distance=1.5, grime_height=1.0)),
    'drone_mothership': (drone_mothership, dict(ao_distance=1.2, ground=False)),
    'command_airship': (command_airship, dict(ao_distance=1.3, ground=False)),
    'nuke_train': (nuke_train, dict(ao_distance=.8, grime_height=.7)),
    'silver_bug': (silver_bug, dict(ao_distance=.4, ground=False)),
}
