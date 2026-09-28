"""Machine Brigade boss variants, and the existing bosses rebuilt with one empty per weapon mount.

The data pairs the k-th weapon mount of a slot with the k-th `Mount_<slot>` / `Muzzle_<slot>` of the
model, sorted by name, so a boss with two flak guns needs `Mount_mg` and `Mount_mg.001`, each with its
own `Muzzle_mg` / `Muzzle_mg.001`. The builders of mb_bosses.py / mb_air3.py are copied here and
extended (those files are left as they are); their models are re-exported from here:

  * behemoth: a second twin AA gun on the turret roof (`Mount_mg.001`) mirroring the first, and
    `Muzzle_missile.001` at the second hull-side missile rack. The cupola and hatch move to make room.
  * mobile_fortress: a second rocket battery (`Mount_rocket.001`) beside the first on the rear deck,
    the missile silo moved between them, and a second MG cupola (`Mount_mg.001`) on the other front
    corner where the searchlight tower stood.
  * mega_gunship: twin chin cannons (`Mount_gun`, `Mount_gun.001`), a door gun in each side door
    (`Mount_mg`, `Mount_mg.001`), and `Muzzle_rocket` / `Muzzle_rocket.001` at the left and right pod
    pairs (the main weapon and the secondary rocket salvo).
  * drone_mothership: a second quad flak gun (`Mount_mg.001`) on the back behind the first, and a
    second twin cannon under the gondola on `Mount_main.001` (`Muzzle_main.001`) for the secondary
    mount of slot "main".
  * nuke_train: a second MG cupola (`Mount_mg.001`) on the missile wagon's control cabin.

New boss variants, each with its own silhouette:
  * behemoth_inferno: the behemoth hull with two huge flame projectors on the turret (`Main_cannon`,
    `Main_cannon_2`, `Muzzle_main` between the nozzles), big fuel tanks on the rear deck and fenders,
    a thermobaric rocket box on the forward mount (`Mount_rocket`, `Muzzle_rocket`) and one flak gun
    (`Mount_mg`). Charred, hazard-striped and glowing orange.
  * behemoth_tempest: one very long railgun with four glowing coil rings (`Main_cannon*`,
    `Muzzle_main`), protection-system launchers on the turret sides, a spinning `Radar` on a mast on
    the bustle, two coilgun turrets on the front deck (`Mount_gun`, `Mount_gun.001`) and capacitor
    banks on the rear fenders. Blue emissive details use the kit's `Energy` material.
  * fortress_hive: the mobile fortress as a drone carrier: a big radar dome on a tower where the
    howitzer was, two trainable drone launch racks on the rear deck (`Mount_missile`,
    `Mount_missile.001`), drone bays in the superstructure flanks, a SAM battery on the roof
    (`Mount_rocket`) and a flak cupola on each front corner (`Mount_mg`, `Mount_mg.001`).
  * fortress_bastion: the mobile fortress as a bunker: thick slab armour over the flanks and the
    bridge, four autocannon turrets at the corners (`Mount_gun` .. `Mount_gun.003`, front left, front
    right, rear left, rear right), a heavy mortar in an armoured pit on the roof (`Turret`,
    `Main_cannon` at 45 degrees with a `Mortar_tube_collar` so the game lobs it, `Muzzle_main`) and
    protection-system launchers at the roof corners.
  * sky_fortress ("Spectre"): the sky gunship (AC-130 lineage) scaled 1.3x in a dark scheme with gun
    sponsons on the left: the 105 mm howitzer on `Mount_main`, two 40 mm cannons on `Mount_gun` and
    `Mount_gun.001`, the 25 mm gatling on `Mount_mg` (each barrel out of the left side, +X, with its
    muzzle), `Muzzle_ramp` at the rear ramp launcher and the four `Propeller` .. `Propeller_4`.

Conventions follow mb_bosses: metres, +Z up, Blender -Y is the front, origin on the ground at the
footprint centre (the aircraft: the gunship's wheels on z = 0, the airship and the sky fortress at
their centres). Suffixed pivots are authored as `Mount_mg__001` and renamed by mb_round6.finish.

Headless: blender --background --python Tools/blender/mb_bosses2.py -- [--out DIR] [names...]
"""
import math
import sys
from pathlib import Path

from mathutils import Vector

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from frontier_kit import chamfered  # noqa: E402
from mb_air import _fin, _prop_blade, _revolve, _trap_fin  # noqa: E402
from mb_bosses import (_headlamp, _periscopes, _plate_bolts, _railing, _rotor, _sec6, _snow, _squircle,  # noqa: E402
                       track_unit)
from mb_round6 import main, pivot, uniform_scale  # noqa: E402
from mb_themes import ladder  # noqa: E402
from mb_town import fbox  # noqa: E402
from mb_vehicles import _antenna, _barrel, _dish, _flank, _frame, _glacis, _smoke, _tube_mouth  # noqa: E402
from mb_vehicles2 import _axis, _gun  # noqa: E402

R90 = math.pi / 2
FORWARD = (R90, 0, 0)    # cylinder axis along Y (local +Z -> -Y)
BACKWARD = (-R90, 0, 0)  # local +Z -> +Y
ACROSS = (0, R90, 0)     # cylinder axis along X


# ============================================================================= behemoth family
def _behemoth_chassis(a, racks=True, stacks=True, fore_ring=True):
    """The behemoth's hull (copied from mb_bosses.behemoth): four track units on their own fenders, the
    stepped hull with its prow and casemate, bolt-on plates, the prow's links and lamps, front-fender
    bins, the front deck hatches, the casemate roof and barbette ring. racks: the missile racks over the
    rear track units (`Muzzle_missile` right, `Muzzle_missile.001` left); stacks: the rear deck's
    grilles and exhaust stacks; fore_ring: the forward mount's turret ring."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    glass = a.part('Vision_blocks', 'Glass')
    TX, TY, TW, TL = 2.62, 3.0, 1.0, 5.2
    fender = a.part('Fenders', 'Team')
    for sx in (-1, 1):
        for sy in (-1, 1):
            y0 = sy * TY
            track_unit(a, sx * TX, y0, TL, TW, 1.5, .52, .42, 1.05, .34, 4, sx, pitch=.3, sprocket=sy,
                       skip=lambda py, pz, nz: nz > .8, wheel_seg=12)
            fender.box((1.2, TL + .2, .1), loc=(sx * TX, y0, 1.61), bevel=.03, seg=1)
            for end in (-1, 1):
                c = Vector((sx * TX, y0 + end * (TL / 2 + .15), 1.43))
                fender.box((1.2, .5, .08), loc=c, rot=(end * .75, 0, 0), bevel=.02, seg=1)
            armor.box((.07, TL - .5, .42), loc=(sx * 3.19, y0, 1.37), bevel=.015, seg=1)
            _plate_bolts(steel, sx * 3.23, [y0 + d for d in (-1.8, 0, 1.8)], 1.3, r=.03)
        armor.box((.85, .66, .9), loc=(sx * 2.58, 0, 1.05), bevel=.05, taper=(.9, .85))
        steel.cyl(.24, .2, loc=(sx * 3.05, 0, .95), rot=ACROSS, seg=12, bevel=.02, bseg=1)
    full = (1.95, .45, 2.05, 2.3, 1.9, 2.55)
    hull.loft([_sec6(-6.3, .95, 1.05, 1.25, 1.45, 1.1, 1.62), _sec6(-5.3, 1.55, .5, 1.95, 1.75, 1.75, 2.22),
               _sec6(-4.35, *full), _sec6(5.35, *full), _sec6(5.95, 1.85, .7, 2.05, 2.2, 1.85, 2.45)], bevel=.07, seg=2)

    def sec(y, z1, w1, z0=2.53, w0=1.84):
        return [(-w0, y, z0), (w0, y, z0), (w1, y, z1), (-w1, y, z1)]
    hull.loft([sec(-2.2, 2.66, 1.8), sec(-1.45, 3.35, 1.6), sec(3.6, 3.35, 1.6), sec(4.2, 2.92, 1.72)], bevel=.06,
              seg=2)
    for s in (-1, 1):
        for y in (-3.3, -1.25, .8, 4.85):
            armor.box((.06, 1.9, .5), loc=(s * 2.075, y, 2.0), bevel=.015, seg=1)
            _plate_bolts(steel, s * 2.11, (y - .75, y, y + .75), 2.17, r=.028)
        fx, fz, lean = _flank((1.84, 2.53), (1.6, 3.35), .52, .025)
        for y in (-.7, .7, 2.1):
            armor.box((.06, 1.25, .5), loc=(s * fx, y, fz), rot=(0, -s * lean, 0), bevel=.015, seg=1)
    links = a.part('Spare_links', 'Undercarriage')
    lower, upper = ((-6.3, 1.62), (-5.3, 2.22)), ((-5.3, 2.22), (-4.35, 2.55))
    gy, gz, grot = _glacis(*lower, .5, .03)
    for x in (-.95, -.32, .32, .95):
        links.box((.56, .3, .06), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.012, seg=1)
        steel.box((.46, .06, .05), loc=(x, gy + .1, gz + .05), rot=(grot, 0, 0), bevel=0)
    gy, gz, grot = _glacis(*upper, .5, .045)
    for x in (-1.4, -.7, 0, .7, 1.4):
        armor.box((.64, .46, .12), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
    for s in (-1, 1):
        _headlamp(a, (s * .7, -6.33, 1.34), r=.12)
        _headlamp(a, (s * 2.62, -5.6, 1.86), r=.11)
        armor.box((.36, .3, .2), loc=(s * 2.62, -5.45, 1.72), bevel=.03, seg=1)
        steel.box((.18, .24, .16), loc=(s * .45, -6.3, 1.0), bevel=.02, seg=1)
        a.part('Tail_lights', 'Alloy').box((.18, .05, .1), loc=(s * 1.7, 5.975, 2.12), bevel=.01, seg=1)
        armor.box((.78, 1.25, .38), loc=(s * 2.62, -2.55, 1.84), bevel=.04, seg=1)
        steel.box((.8, .06, .06), loc=(s * 2.62, -2.55, 2.04), bevel=0)
        for dy in (-1.25, -1.03):
            a.part('Jerrycans', 'Hazard').box((.3, .18, .44), loc=(s * 2.62, dy, 1.87), bevel=.03, seg=1)
    for s in (-1, 1):
        armor.cyl(.3, .07, loc=(s * 1.4, -3.95, 2.58), seg=14, bevel=.02, bseg=1)
        for dx in (-.18, 0, .18):
            glass.box((.13, .06, .08), loc=(s * 1.4 + dx, -4.33, 2.59), bevel=0)
    if fore_ring:
        steel.cyl(.98, .12, loc=(0, -3.45, 2.57), seg=24, bevel=.03, bseg=1)
    for s in (-1, 1):
        armor.cyl(.3, .07, loc=(s * 1.05, 2.75, 3.37), seg=14, bevel=.02, bseg=1)
        _periscopes(glass, s * 1.05, 2.75, 3.4, .36, 3, start=R90 - .8, arc=1.6)
    steel.cyl(1.58, .26, loc=(0, .4, 3.44), seg=28, bevel=.03)
    if racks:
        rot = (-math.radians(12), 0, 0)
        for s in (-1, 1):
            x = s * 2.62
            armor.box((.6, 1.6, .16), loc=(x, 3.0, 1.73), bevel=.03, seg=1)
            armor.box((.1, 1.2, .5), loc=(s * 2.2, 3.1, 1.95), bevel=.02, seg=1)
            centre = Vector((x, 2.9, 2.12))
            rack = _frame(centre, rot)
            a.part('Missile_racks', 'Team').box((.62, 1.9, .56), loc=centre, rot=rot, bevel=.04)
            frame = a.part('Rack_frames', 'Armor')
            for yy in (-.82, .82):
                frame.box((.67, .12, .61), loc=rack @ Vector((0, yy, 0)), rot=rot, bevel=.015, seg=1)
            for cz in (-.13, .13):
                for cx in (-.19, 0, .19):
                    _tube_mouth(a, None, rack @ _frame((cx, -.95, cz), FORWARD), .085, protrude=.05, seg=8)
            steel.limb((x, 2.2, 1.8), tuple(rack @ Vector((0, -.55, -.28))), .1, .1, bevel=0)
            pivot(a, 'Muzzle_missile' if s < 0 else 'Muzzle_missile.001', tuple(rack @ Vector((0, -1.0, 0))))
    if stacks:
        for s in (-1, 1):
            deck.grille(1.1, 1.0, loc=(s * .75, 4.95, 2.56), rot=(-R90, 0, 0), slats=6, depth=.09, thickness=.04)
            for dy in (4.65, 5.2):
                x = s * 1.55
                steel.cyl(.15, 1.2, loc=(x, dy, 3.13), seg=10, bevel=0)
                armor.cyl(.19, .6, loc=(x, dy, 3.08), seg=10, bevel=.02, bseg=1)
                a.part('Soot', 'Charred').cyl(.165, .06, loc=(x, dy, 3.72), seg=10, bevel=0)
            steel.box((.08, .9, .08), loc=(s * 1.55, 4.925, 3.3), bevel=0)
    armor.box((3.6, .1, .5), loc=(0, 5.99, 1.6), bevel=.02, seg=1)
    for x in (-1.1, 1.1):
        steel.box((.2, .22, .18), loc=(x, 6.03, 1.2), bevel=.02, seg=1)
    _antenna(a, None, -1.6, 5.75, 2.47, 1.2)


def _behemoth_turret(a, ears=True):
    """The behemoth's main turret body (copied): angled armour, bustle with bins, smoke dischargers, the
    mantlet block, gunner's sight, vents and antennas; the battleship rangefinder with its ears if
    `ears`. The commander's cupola sits at the front centre of the roof and the hatch behind it, so
    both roof AA mounts fit. Returns the Turret pivot."""
    t = a.pivot('Turret', (0, .4, 3.57))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.55, 2.25), (1.55, 2.25), (1.95, 1.35), (1.95, -.85), (1.25, -1.85), (-1.25, -1.85), (-1.95, -.85),
               (-1.95, 1.35)]
    turret.prism(outline, 1.0, loc=(0, 0, .51), axis='Z', bevel=.07, taper=.88)
    turret.box((3.3, 1.2, .82), loc=(0, 2.75, .47), bevel=.06, taper=(.93, .9))
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    glass = a.part('Vision_blocks', 'Glass')
    for s in (-1, 1):
        p0, p1 = Vector((s * 1.25, -1.85)), Vector((s * 1.95, -.85))
        mid, d = (p0 + p1) / 2, (p1 - p0).normalized()
        c = mid + Vector((d.y, -d.x)) * s * .06
        tarm.box((1.1, .14, .74), loc=(c.x, c.y, .44), rot=(0, 0, math.atan2(d.y, d.x)), bevel=.03, seg=1)
        tarm.box((.18, 1.5, .5), loc=(s * 1.72, 2.65, .5), bevel=.03, seg=1)
        _smoke(a, tsteel, 1.3, -.95, .92, s, count=4, gap=.1, r=.055, depth=.18)
    tarm.box((1.9, .7, .82), loc=(0, -1.95, .5), bevel=.06, taper=(.95, .9))
    if ears:
        tsteel.cyl(.15, 4.3, loc=(0, 1.7, .94), rot=ACROSS, seg=12, bevel=.02, bseg=1)
        for s in (-1, 1):
            tarm.box((.34, .46, .44), loc=(s * 2.12, 1.7, .94), bevel=.05)
            glass.box((.2, .04, .2), loc=(s * 2.12, 1.46, .96), bevel=.01, seg=1)
    # Commander's cupola (front centre) with a searchlight on the right front corner.
    tsteel.cyl(.36, .26, loc=(0, -.45, 1.0), seg=16, bevel=.04)
    a.part('Cupola_top', 'Armor', t).cyl(.3, .08, loc=(0, -.45, 1.16), seg=16, bevel=.02, bseg=1)
    _periscopes(a.part('Periscope', 'Glass', t), 0, -.45, 1.02, .37, 5)
    a.part('Searchlight', 'Lamp', t).cyl(.12, .05, loc=(1.45, -.35, 1.06), rot=FORWARD, seg=10, bevel=.01, bseg=1)
    tarm.cyl(.16, .24, loc=(1.45, -.22, 1.06), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    tsteel.box((.44, .4, .28), loc=(-.95, -1.05, 1.0), bevel=.04)
    a.part('Sight', 'Glass', t).box((.32, .04, .15), loc=(-.95, -1.26, 1.02), bevel=.01, seg=1)
    a.part('Vents', 'Undercarriage', t).grille(1.3, .6, loc=(0, 2.85, .885), rot=(-R90, 0, 0), slats=5, depth=.07,
                                               thickness=.04)
    a.part('Hatch', 'Armor', t).cyl(.3, .07, loc=(0, 1.05, 1.02), seg=14, bevel=.02, bseg=1)
    _antenna(a, t, -1.45, 3.1, .88, 1.0)
    _antenna(a, t, 1.45, 3.1, .88, .8)
    return t


def _twin_aa(a, t, name, x, y, z=1.03):
    """Twin AA gun on the turret roof on its own mount `name` (copied from the behemoth)."""
    a.part('Turret_steel', 'Steel', t).cyl(.46, .1, loc=(x, y, z - .05), seg=16, bevel=.02, bseg=1)
    m = pivot(a, name, (x, y, z), t)
    base = a.part('AA_mount', 'Armor', m)
    base.cyl(.42, .16, loc=(0, 0, .09), seg=16, bevel=.03, bseg=1)
    base.box((.5, .6, .3), loc=(0, .05, .3), bevel=.04)
    base.box((.66, .06, .36), loc=(0, -.34, .4), rot=(-.15, 0, 0), bevel=.012, seg=1, taper=(.85, 1))
    gun = a.part('AA_guns', 'Steel', m)
    for dx in (-.16, .16):
        gun.box((.12, .5, .14), loc=(dx, -.05, .42), bevel=.02, seg=1)
        gun.cyl(.035, 1.25, loc=(dx, -.925, .42), rot=FORWARD, seg=8, bevel=0)
        gun.cyl(.055, .16, loc=(dx, -1.52, .42), rot=FORWARD, seg=8, bevel=0)
        a.part('AA_ammo', 'Hazard', m).box((.14, .3, .22), loc=(dx * 2.4, .15, .34), bevel=.03, seg=1)
    pivot(a, name.replace('Mount_', 'Muzzle_'), (0, -1.6, .42), name)


def behemoth(a):
    """Super-heavy "land battleship" (mb_bosses.behemoth) with one empty per weapon mount: the twin
    cannon `Turret`, the forward secondary turret on `Mount_gun`, two twin AA guns on the turret roof
    (`Mount_mg` left of centre, `Mount_mg.001` right) and the two hull-side missile racks
    (`Muzzle_missile`, `Muzzle_missile.001`)."""
    _behemoth_chassis(a)
    g = a.pivot('Mount_gun', (0, -3.45, 2.63))
    ft = a.part('Gun_turret', 'Team', g)
    ft.prism([(-.6, .76), (.6, .76), (.84, .3), (.84, -.3), (.5, -.8), (-.5, -.8), (-.84, -.3), (-.84, .3)], .56,
             loc=(0, 0, .3), axis='Z', bevel=.05, taper=.84)
    garm = a.part('Gun_armor', 'Armor', g)
    garm.box((.62, .34, .44), loc=(0, -.84, .3), bevel=.04)
    garm.box((1.0, .26, .32), loc=(0, .76, .26), bevel=.03, taper=(.95, .9))
    gs = a.part('Gun_steel', 'Steel', g)
    gs.cyl(.07, 2.3, loc=(0, -2.15, .3), rot=FORWARD, seg=10, bevel=0)
    gs.cyl(.11, .5, loc=(0, -1.2, .3), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    a.part('Gun_brake', 'Undercarriage', g).box((.2, .3, .18), loc=(0, -3.35, .3), bevel=.025)
    gs.cyl(.18, .1, loc=(.3, .2, .6), seg=10, bevel=.02, bseg=1)
    gs.box((.22, .22, .16), loc=(-.35, -.2, .62), bevel=.03)
    a.part('Gun_sight', 'Glass', g).box((.16, .04, .09), loc=(-.35, -.32, .63), bevel=.01, seg=1)
    a.pivot('Muzzle_gun', (0, -3.52, .3), g)
    t = _behemoth_turret(a)
    a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        a.part('Turret_armor', 'Armor', t).cyl(.3, .45, loc=(s * .52, -2.36, .5), rot=FORWARD, seg=14, bevel=.04)
    tips = []
    for s, suffix in ((-1, ''), (1, '_2')):
        tip = _barrel(a, t, start_y=-2.3, length=5.3, radius=.15, height=.5, brake=(.44, .5, .42),
                      sleeve=(.3, .9, .22), x=s * .52, suffix=suffix, seg=14)
        a.part(f'Muzzle_brake{suffix}', 'Undercarriage', t).box((.4, .16, .36), loc=(s * .52, tip[1] + .62, .5),
                                                                 bevel=.04)
        tips.append(tip)
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    _twin_aa(a, t, 'Mount_mg', -.9, .75)
    _twin_aa(a, t, 'Mount_mg.001', .9, .75)


# ----------------------------------------------------------------------------- behemoth_inferno
def _fuel_tank(a, loc, r, length, axis='y', bands=3, stripe=True):
    """Big armoured fuel tank lying along Y (or X): a red shell with domed ends, dark straps, a hazard
    band, a filler cap and a sooty scorch patch on its top."""
    x, y, z = loc
    rot = FORWARD if axis == 'y' else ACROSS
    body = a.part('Fuel_tanks', 'BarrelRed')
    body.cyl(r, length, loc=loc, rot=rot, seg=16, bevel=r * .35)
    straps = a.part('Tank_straps', 'Armor')
    for k in range(bands):
        f = (k + .5) / bands - .5
        p = (x, y + f * length * .82, z) if axis == 'y' else (x + f * length * .82, y, z)
        straps.cyl(r + .03, .12, loc=p, rot=rot, seg=16, bevel=0)
    if stripe:
        p = (x, y - length * .3, z) if axis == 'y' else (x - length * .3, y, z)
        a.part('Tank_hazard', 'Hazard').cyl(r + .015, .22, loc=p, rot=rot, seg=16, bevel=0)
    a.part('Tank_caps', 'Steel').cyl(.09, .1, loc=(x, y, z + r + .03), seg=8, bevel=0)
    a.part('Scorch', 'Charred').sphere((length * .18 if axis == 'x' else r * .7, length * .18 if axis == 'y' else r * .7,
                                        .04), loc=(x + (length * .22 if axis == 'x' else 0),
                                                   y + (length * .22 if axis == 'y' else 0), z + r - .025), seg=10,
                                       rings=4, cut=0)


def behemoth_inferno(a):
    """Flame-thrower behemoth ("Inferno"): the behemoth hull without its missile racks and exhaust
    stacks, big red fuel tanks on the rear deck and on both rear fenders with fuel lines to the
    barbette; the turret carries two huge flame projectors (armoured tubes with heat jackets, charred
    nozzles with glowing pilot rings) instead of the twin cannon, pressure bottles on the bustle and a
    flak gun on the roof; a thermobaric rocket box turns on the forward mount. Hazard stripes and soot
    everywhere."""
    _behemoth_chassis(a, racks=False, stacks=False)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    # Rear deck: two long tanks side by side, grilles between them; fender tanks over the rear tracks.
    for s in (-1, 1):
        _fuel_tank(a, (s * .95, 4.95, 3.1), .55, 1.9)
        for yy in (4.35, 5.55):
            armor.box((.9, .16, .3), loc=(s * .95, yy, 2.62), bevel=.02, seg=1)                 # cradles
        _fuel_tank(a, (s * 2.62, 3.0, 2.2), .5, 3.4, bands=4)
        for yy in (1.9, 4.1):
            armor.box((.9, .2, .28), loc=(s * 2.62, yy, 1.76), bevel=.02, seg=1)
        a.part('Fuel_lines', 'Rubber').tube([(s * .95, 4.0, 3.2), (s * .9, 3.4, 3.42), (s * .7, 2.2, 3.48)], .07,
                                            seg=6)
        a.part('Fuel_lines', 'Rubber').tube([(s * 2.62, 1.3, 2.3), (s * 2.3, .6, 2.45), (s * 1.9, .2, 2.6)], .06,
                                            seg=6)
        a.part('Deck', 'Undercarriage').grille(.5, 1.6, loc=(0, 4.95, 2.56), rot=(-R90, 0, 0), slats=6, depth=.07,
                                               thickness=.04)
    for s in (-1, 1):                                                                          # hazard chevrons
        for k in range(4):
            mat = 'SafetyStripe' if k % 2 == 0 else 'Charred'
            a.part('Hull_stripes', mat).box((.03, .4, .22), loc=(s * 2.1, -4.4 + k * .4, 2.3), rot=(.5, 0, 0),
                                            bevel=0)
    # Thermobaric rocket box on the forward mount, kept low under the flame projectors' sweep.
    rk = pivot(a, 'Mount_rocket', (0, -3.45, 2.63))
    a.part('Launcher_base', 'Steel', rk).cyl(.85, .12, loc=(0, 0, .06), seg=18, bevel=.02, bseg=1)
    lb = a.part('Launcher_armor', 'Armor', rk)
    lb.box((1.1, 1.2, .3), loc=(0, .1, .25), bevel=.04, seg=1)
    for s in (-1, 1):
        lb.box((.12, .7, .42), loc=(s * .72, .1, .45), bevel=.02, seg=1)
    pitch = math.radians(10)
    lrot = (-pitch, 0, 0)
    centre = Vector((0, -.05, .66))
    box = _frame(centre, lrot)
    a.part('Rocket_box', 'Team', rk).box((1.3, 1.9, .7), loc=centre, rot=lrot, bevel=.05)
    for yy in (-.7, .7):
        a.part('Rocket_box_bands', 'Charred').box((1.35, .14, .75), loc=box @ Vector((0, yy, 0)), rot=lrot, bevel=.015,
                                                  seg=1)
    a.part('Rocket_box_stripe', 'Hazard').box((1.36, .08, .76), loc=box @ Vector((0, .2, 0)), rot=lrot, bevel=0)
    for row in (-.17, .17):
        for col in (-.45, -.15, .15, .45):
            _tube_mouth(a, rk, box @ _frame((col, -.95, row), FORWARD), .12, protrude=.04, seg=8)
    pivot(a, 'Muzzle_rocket', tuple(box @ Vector((0, -1.0, 0))), 'Mount_rocket')
    # Turret: two flame projectors in armoured sleeves, fuel hoses, pressure bottles, one flak gun.
    t = _behemoth_turret(a, ears=False)
    tarm = a.part('Turret_armor', 'Armor', t)
    zf = .55
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .62
        tarm.cyl(.36, .5, loc=(x, -2.2, zf), rot=FORWARD, seg=14, bevel=.04)                          # sleeves
        tube = a.part(f'Main_cannon{suffix}', 'Steel', t)
        tube.cyl(.24, 3.0, loc=(x, -3.85, zf), rot=FORWARD, seg=14, bevel=.02, bseg=1)
        jacket = a.part(f'Main_cannon{suffix}_jacket', 'Charred', t)
        for f in (-3.0, -3.7, -4.4):
            jacket.cyl(.28, .22, loc=(x, f, zf), rot=FORWARD, seg=14, bevel=0)                         # heat fins
        a.part(f'Main_cannon{suffix}_hose', 'Rubber', t).tube([(x - s * .2, -2.0, zf + .3), (x - s * .2, -2.8, zf + .3),
                                                               (x - s * .05, -3.1, zf + .22)], .06, seg=6)
        nozzle = a.part(f'Muzzle_brake{suffix}', 'Charred', t)
        nozzle.lathe([(.25, -.05), (.34, .2), (.36, .5), (.3, .62), (.16, .62), (.16, .45)], loc=(x, -5.35, zf),
                     rot=FORWARD, seg=14)
        a.part(f'Muzzle_brake{suffix}_glow', 'LavaGlow', t).torus(.2, .035, loc=(x, -5.9, zf), rot=FORWARD, seg=14,
                                                                  ring=4)
        a.part(f'Muzzle_brake{suffix}_pilot', 'Alloy', t).cyl(.05, .3, loc=(x, -5.6, zf - .3), rot=FORWARD, seg=6,
                                                              bevel=0)
    a.pivot('Muzzle_main', (0, -5.99, zf), t)
    for s in (-1, 1):                                                                      # pressure bottles
        for dx in (0, .36):
            a.part('Pressure_bottles', 'Hazard', t).cyl(.16, 1.1, loc=(s * (.9 + dx), 3.1, 1.0), rot=FORWARD, seg=10,
                                                        bevel=.05)
        a.part('Turret_stripes', 'SafetyStripe', t).box((.05, .7, .2), loc=(s * 1.96, .2, .6), bevel=0)
    _twin_aa(a, t, 'Mount_mg', -.9, .75)


# ----------------------------------------------------------------------------- behemoth_tempest
def _coilgun(a, name, loc):
    """Compact coilgun turret on its own mount `name`: a faceted Team housing, a long thin barrel with
    two glowing coil rings and a slotted muzzle; `Muzzle_gun*` at the tip."""
    m = pivot(a, name, loc)
    body = a.part('Coil_turret', 'Team', m)
    body.prism([(-.5, .6), (.5, .6), (.66, .2), (.66, -.3), (.4, -.62), (-.4, -.62), (-.66, -.3), (-.66, .2)], .5,
               loc=(0, 0, .27), axis='Z', bevel=.04, taper=.84)
    arm = a.part('Coil_armor', 'Armor', m)
    arm.box((.44, .3, .36), loc=(0, -.66, .3), bevel=.03, seg=1)
    arm.box((.7, .3, .26), loc=(0, .66, .24), bevel=.03, seg=1)
    barrel = a.part('Coil_barrel', 'Steel', m)
    barrel.cyl(.07, 2.4, loc=(0, -1.95, .32), rot=FORWARD, seg=10, bevel=0)
    for f in (-1.35, -2.25):
        a.part('Coil_rings', 'Energy', m).cyl(.13, .12, loc=(0, f, .32), rot=FORWARD, seg=10, bevel=0)
        arm.cyl(.14, .05, loc=(0, f + .1, .32), rot=FORWARD, seg=10, bevel=0)
    a.part('Coil_muzzle', 'Undercarriage', m).box((.2, .22, .18), loc=(0, -3.2, .32), bevel=.02, seg=1)
    a.part('Coil_glow', 'Energy', m).box((.5, .05, .06), loc=(0, .82, .36), bevel=0)
    pivot(a, name.replace('Mount_', 'Muzzle_'), (0, -3.33, .32), name)


def behemoth_tempest(a):
    """Railgun behemoth ("Tempest"): the behemoth hull with capacitor banks and coolant pipes on the rear
    fenders instead of the missile racks, two coilgun turrets side by side on the front deck
    (`Mount_gun` left, `Mount_gun.001` right), and a turret carrying one very long railgun (rails
    over a dark core, Team clamps and four glowing coil rings), protection-system launchers and radar
    panels on its flanks and a spinning search `Radar` on a mast over the bustle."""
    _behemoth_chassis(a, racks=False, fore_ring=False)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    energy = a.part('Energy_glow', 'Energy')
    for s in (-1, 1):
        x = s * 2.62
        bank = a.part('Capacitor_banks', 'Team')
        bank.box((.9, 3.6, .8), loc=(x, 3.0, 2.06), bevel=.06, seg=1)
        for k in range(5):
            armor.box((.95, .08, .84), loc=(x, 1.5 + k * .75, 2.06), bevel=0)                        # cell ribs
        energy.box((.04, 3.2, .06), loc=(x + s * .47, 3.0, 2.3), bevel=0)
        a.part('Coolant_pipes', 'Pipe').tube([(x - s * .3, 1.2, 2.46), (x - s * .3, 1.0, 2.7), (s * 1.9, .6, 2.75),
                                              (s * 1.7, .2, 3.2)], .07, seg=6)
        steel.cyl(.46, .08, loc=(s * 1.0, -3.6, 2.57), seg=18, bevel=.02, bseg=1)                    # coil rings
    _coilgun(a, 'Mount_gun', (1.0, -3.6, 2.62))
    _coilgun(a, 'Mount_gun.001', (-1.0, -3.6, 2.62))
    # Turret with the railgun.
    t = _behemoth_turret(a, ears=False)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    zr = .52
    L = 7.6
    y0 = -2.2
    core = a.part('Main_cannon', 'Armor', t)
    core.box((.4, L, .44), loc=(0, y0 - L / 2, zr), bevel=.03, seg=1)
    rails = a.part('Main_cannon_rails', 'Steel', t)
    for side in (-.2, .2):
        rails.box((.1, L - .5, .16), loc=(side, y0 - L / 2 - .25, zr + .22), bevel=0)
    bands = a.part('Main_cannon_bands', 'Team', t)
    for k in range(6):
        bands.box((.56, .12, .54), loc=(0, y0 - .6 - k * 1.25, zr), bevel=.01, seg=1)
    coils = a.part('Main_cannon_coils', 'Energy', t)
    coil_arm = a.part('Main_cannon_coil_frames', 'Armor', t)
    for k in range(4):
        yc = y0 - 1.25 - k * 1.55
        coils.cyl(.42, .16, loc=(0, yc, zr), rot=FORWARD, seg=16, bevel=0)
        coil_arm.cyl(.47, .06, loc=(0, yc - .12, zr), rot=FORWARD, seg=16, bevel=0)
        coil_arm.cyl(.47, .06, loc=(0, yc + .12, zr), rot=FORWARD, seg=16, bevel=0)
    a.part('Main_cannon_sleeve', 'Team', t).box((.8, 1.2, .72), loc=(0, y0 + .1, zr), bevel=.05, seg=1)
    mz = a.part('Muzzle_brake', 'Armor', t)
    for side in (-.22, .22):
        mz.box((.18, .4, .66), loc=(side, y0 - L - .1, zr), bevel=.02, seg=1)
    a.part('Muzzle_brake_bore', 'Energy', t).box((.24, .04, .26), loc=(0, y0 - L + .02, zr), bevel=0)
    a.pivot('Muzzle_main', (0, y0 - L - .32, zr), t)
    # Protection-system launchers and flat radar panels on the turret flanks.
    for s in (-1, 1):
        tarm.box((.1, .7, .5), loc=(s * 1.9, -.2, .55), rot=(0, 0, 0), bevel=.02, seg=1)                # radar panel
        a.part('Aps_faces', 'Energy', t).box((.03, .5, .32), loc=(s * 1.96, -.2, .55), bevel=0)
        tarm.box((.5, .5, .36), loc=(s * 1.75, 1.1, 1.0), bevel=.03, seg=1)                             # APS launcher
        for k in range(2):
            m = _frame((s * (1.75 + .12), 1.0 + k * .22, 1.08), (.2, 0, s * -R90))
            _tube_mouth(a, t, m, .08, protrude=.1, seg=8, name='Aps_tubes')
    # Radar mast on the bustle: a lattice pole and the spinning search array.
    tsteel.cyl(.1, 1.3, loc=(0, 2.9, 1.5), seg=8, bevel=0)
    tarm.cyl(.24, .12, loc=(0, 2.9, .92), seg=12, bevel=.02, bseg=1)
    for zz in (1.2, 1.7):
        tsteel.box((.7, .05, .05), loc=(0, 2.9, zz), bevel=0)
    r = a.pivot('Radar', (0, 2.9, 2.15), t)
    ra = a.part('Radar_array', 'Armor', r)
    ra.box((1.6, .12, .55), loc=(0, -.12, .3), rot=(.25, 0, 0), bevel=.03, seg=1)
    a.part('Radar_face', 'Energy', r).box((1.4, .03, .4), loc=(0, -.19, .31), rot=(.25, 0, 0), bevel=0)
    a.part('Radar_mount', 'Steel', r).cyl(.14, .2, loc=(0, 0, .08), seg=10, bevel=0)
