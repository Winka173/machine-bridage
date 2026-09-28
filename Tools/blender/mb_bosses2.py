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
    a.part('Heat_vents', 'LavaGlow').box((.4, 1.5, .03), loc=(0, 4.95, 2.545), bevel=0)
    a.part('Deck', 'Undercarriage').grille(.5, 1.6, loc=(0, 4.95, 2.58), rot=(-R90, 0, 0), slats=6, depth=.07,
                                           thickness=.04)
    for s in (-1, 1):                                                                          # hazard chevrons
        for k in range(4):
            mat = 'SafetyStripe' if k % 2 == 0 else 'Charred'
            a.part('Hull_stripes', mat).box((.03, .4, .22), loc=(s * 2.12, -4.1 + k * .4, 2.3), rot=(.5, 0, 0),
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
        a.part(f'Muzzle_brake{suffix}_glow', 'LavaGlow', t).torus(.24, .055, loc=(x, -5.92, zf), rot=FORWARD, seg=14,
                                                                  ring=4)
        a.part(f'Muzzle_brake{suffix}_pilot', 'Alloy', t).cyl(.05, .3, loc=(x, -5.6, zf - .3), rot=FORWARD, seg=6,
                                                              bevel=0)
    a.pivot('Muzzle_main', (0, -5.99, zf), t)
    for k in range(6):                                                                     # mantlet chevrons
        mat = 'SafetyStripe' if k % 2 == 0 else 'Charred'
        a.part('Mantlet_chevrons', mat, t).box((.3, .04, .5), loc=(-.75 + k * .3, -2.31, .52), rot=(0, .5, 0), bevel=0)
    for x, y in ((-.62, -1.7), (.62, -1.7)):                                                # soot above the nozzles
        a.part('Nozzle_soot', 'Charred', t).sphere((.5, .45, .04), loc=(x, y, 1.0), seg=10, rings=4, cut=0)
    for s in (-1, 1):                                                                      # pressure bottles
        for dx in (0, .36):
            a.part('Pressure_bottles', 'Hazard', t).cyl(.16, 1.1, loc=(s * (.9 + dx), 3.1, 1.0), rot=FORWARD, seg=10,
                                                        bevel=.05)
        a.part('Cheek_stripes', 'SafetyStripe', t).box((.05, .7, .2), loc=(s * 1.96, .2, .6), bevel=0)
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
        steel.cyl(.46, .08, loc=(s * .9, -3.3, 2.57), seg=18, bevel=.02, bseg=1)                     # turret rings
    _coilgun(a, 'Mount_gun', (.9, -3.3, 2.62))
    _coilgun(a, 'Mount_gun.001', (-.9, -3.3, 2.62))
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


# ============================================================================= mobile fortress family
def _fortress_chassis(a, snow=True, portholes=True, bridge_glass=True, antenna=True):
    """The mobile fortress's crawler (copied from mb_bosses.mobile_fortress): four track pods with snow
    ploughs, the chassis deck and belly with its fuel tanks, ladders, bumpers, the superstructure deck
    (lit portholes along its flanks if `portholes`), walkways, the command bridge (glazed if
    `bridge_glass`, else an armoured shutter over vision slits) under its visor roof, searchlights and
    an antenna. Snow lies on the top edges if `snow`."""
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    lamp = a.part('Lamps', 'Lamp')

    def snowy(*args, **kw):
        if snow:
            _snow(*args, **kw)
    PX, PY, PL = 3.4, 5.2, 4.8
    pods = a.part('Pods_housing', 'Team')
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * PX, sy * PY
            track_unit(a, x, y, PL, 1.9, 1.8, .62, .46, 1.1, .38, 4, sx, pitch=.34, sprocket=sy,
                       skip=lambda py, pz, nz: pz > 1.36, wheel_seg=12)
            pods.prism([(y + p, z) for p, z in ((-2.62, 1.35), (-2.62, 1.85), (-2.25, 2.3), (2.25, 2.3), (2.62, 1.85),
                                                 (2.62, 1.35))], 2.14, loc=(x, 0, 0), axis='X', bevel=.05)
            for dy in (-1.55, 0, 1.55):
                armor.box((.06, 1.35, .36), loc=(x + sx * 1.085, y + dy, 1.62), bevel=.015, seg=1)
            snowy(a, (1.9, 4.2, .07), (x, y, 2.31))
            steel.cyl(.4, 1.0, loc=(x, y, 2.75), seg=14, bevel=.02, bseg=1)
            armor.box((1.05, 1.05, .22), loc=(x, y, 2.4), bevel=.04, seg=1)
            armor.box((1.1, 1.1, .24), loc=(x, y, 2.93), bevel=.04, seg=1)
            steel.limb((x, y - .95, 2.33), (x - sx * .55, y - .35, 2.98), .12, .12, bevel=0)
            armor.box((.5, .8, .4), loc=(x + sx * .72, y + 1.2, 2.47), bevel=.04, seg=1)
            steel.cyl(.1, .14, loc=(x + sx * .98, y + 1.2, 2.47), rot=ACROSS, seg=8, bevel=0)
            if sy < 0:
                rot = (-.3, 0, 0)
                blade = _frame((x, -8.02, .74), rot)
                armor.box((2.3, .14, 1.05), loc=blade.to_translation(), rot=rot, bevel=.03, seg=1)
                for i in range(6):
                    mat = 'SafetyStripe' if i % 2 == 0 else 'Charred'
                    a.part('Plough_stripes', mat).box((.38, .03, .2), loc=blade @ Vector((-.95 + i * .38, -.075, .36)),
                                                      rot=rot, bevel=0)
                for dx in (-.7, .7):
                    steel.limb(tuple(blade @ Vector((dx, .07, .1))), (x + dx, -7.7, 1.55), .12, .12, bevel=0)
                _headlamp(a, (x - .55, -7.845, 2.0), r=.13)
                _headlamp(a, (x + .55, -7.845, 2.0), r=.13)
            else:
                a.part('Tail_lights', 'Alloy').box((.2, .05, .12), loc=(x + sx * .7, 7.835, 1.6), bevel=.01, seg=1)
    hull.prism([(-6.7, 3.0), (-7.3, 3.45), (-6.6, 4.3), (6.6, 4.3), (7.3, 3.5), (6.8, 3.0)], 7.2, bevel=.07)
    armor.box((4.4, 4.9, 1.8), loc=(0, 0, 2.15), bevel=.06)
    fuel = a.part('Fuel_tanks', 'Fuel')
    for s in (-1, 1):
        fuel.cyl(.42, 4.3, loc=(s * 2.55, 0, 2.42), rot=FORWARD, seg=14, bevel=.12)
        for yy in (-1.4, 0, 1.4):
            armor.cyl(.445, .14, loc=(s * 2.55, yy, 2.42), rot=FORWARD, seg=14, bevel=0)
        a.part('Hazard_bands', 'Hazard').cyl(.435, .3, loc=(s * 2.55, -1.95, 2.42), rot=FORWARD, seg=14, bevel=0)
        dark.grille(1.4, .6, loc=(s * 2.22, 1.2, 1.65), rot=(0, 0, s * R90), slats=4, depth=.06, thickness=.04)
        for yy in (-5.3, -3.2, 3.2, 5.3):
            armor.box((.06, 1.8, .9), loc=(s * 3.615, yy, 3.62), bevel=.02, seg=1)
        dark.grille(1.3, .6, loc=(s * 3.62, 0, 3.7), rot=(0, 0, s * R90), slats=4, depth=.06, thickness=.04)
        ladder(steel, (s * 3.66, -1.2, .35), 4.3, R90, width=.46, step=.4, rung=.03)
    front, back = (-7.3, 3.45), (-6.6, 4.3)
    gy, gz, grot = _glacis(front, back, .45, .03)
    for x in (-1.8, -1.2, -.6, 0, .6, 1.2, 1.8):
        a.part('Spare_links', 'Undercarriage').box((.52, .34, .06), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.012,
                                                   seg=1)
    armor.box((6.2, .3, .45), loc=(0, -7.35, 3.2), bevel=.04, seg=1)
    armor.box((6.2, .3, .45), loc=(0, 7.15, 3.25), bevel=.04, seg=1)
    steel.box((.5, .4, .3), loc=(0, 7.35, 3.1), bevel=.03, seg=1)
    gy, gz, grot = _glacis((7.3, 3.5), (6.6, 4.3), .55, .02)
    for s in (-1, 1):
        dark.grille(1.8, .55, loc=(s * 1.4, gy, gz), rot=(grot + R90, 0, 0), slats=4, depth=.06, thickness=.04)
    fbox(armor, '+y', (-1.3, 4.75, 4.72), (.9, .06, .8), out=.02, bevel=.015)
    fbox(steel, '+y', (-.95, 4.75, 4.72), (.06, .05, .2), out=.06)
    dark.grille(1.1, .45, loc=(1.3, 4.79, 4.75), rot=(0, 0, math.pi), slats=3, depth=.06, thickness=.04)
    for s in (-1, 1):
        _headlamp(a, (s * 2.6, -7.52, 3.2), r=.12, hood=False)
        a.part('Tail_lights', 'Alloy').box((.24, .05, .12), loc=(s * 2.8, 7.2, 3.62), rot=(-.96, 0, 0), bevel=.01,
                                           seg=1)

    def sec(y, z1, w1, z0=4.28, w0=2.9):
        return [(-w0, y, z0), (w0, y, z0), (w1, y, z1), (-w1, y, z1)]
    hull.loft([sec(-5.2, 4.62, 2.85), sec(-4.55, 5.5, 2.62), sec(4.35, 5.5, 2.62), sec(4.75, 5.1, 2.75)], bevel=.06,
              seg=2)
    px, pz, plean = _flank((2.9, 4.28), (2.62, 5.5), .55, .012)
    for s in (-1, 1):
        if portholes:
            for i, yy in enumerate((-3.3, -2.2, -1.1, 0, 1.1, 2.2, 3.3)):
                part = lamp if (i + (s > 0)) % 3 else glass
                part.box((.04, .42, .3), loc=(s * px, yy, pz), rot=(0, -s * plean, 0), bevel=0)
        fx, fz, flean = _flank((2.9, 4.28), (2.62, 5.5), .2, .015)
        armor.box((.06, 8.4, .2), loc=(s * fx, -.1, fz), rot=(0, -s * flean, 0), bevel=.015, seg=1)
        snowy(a, (.4, 2.9, .07), (s * 2.38, .15, 5.51), drifts=False)
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        _railing(rail, [(s * 3.5, -5.1, 4.3), (s * 3.5, 6.4, 4.3)])
        ladder(steel, (s * 2.97, 2.8, 4.3), 5.5, R90, width=.42, step=.38, rung=.03)

    def bsec(y, z1, w1):
        return [(-2.3, y, 5.48), (2.3, y, 5.48), (w1, y, z1), (-w1, y, z1)]
    hull.loft([bsec(-4.3, 5.55, 2.28), bsec(-3.85, 6.45, 2.05), bsec(-1.75, 6.45, 2.05), bsec(-1.5, 6.1, 2.12)],
              bevel=.05, seg=2)
    gy, gz, grot = _glacis((-4.3, 5.55), (-3.85, 6.45), .5, .012)
    frames = a.part('Window_frames', 'Armor')
    if bridge_glass:
        for x in (-1.64, -.82, 0, .82, 1.64):
            glass.box((.72, .66, .04), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0)
        gy2, gz2, _ = _glacis((-4.3, 5.55), (-3.85, 6.45), .5, .03)
        for x in (-2.05, -1.23, -.41, .41, 1.23, 2.05):
            frames.box((.08, .8, .05), loc=(x, gy2, gz2), rot=(grot, 0, 0), bevel=0)
    else:
        gy2, gz2, _ = _glacis((-4.3, 5.55), (-3.85, 6.45), .45, .09)
        armor.box((4.3, .95, .16), loc=(0, gy2, gz2), rot=(grot, 0, 0), bevel=.03, seg=1)            # shutter slab
        gy3, gz3, _ = _glacis((-4.3, 5.55), (-3.85, 6.45), .88, .04)
        for x in (-1.4, 0, 1.4):
            glass.box((.9, .08, .05), loc=(x, gy3, gz3), rot=(grot, 0, 0), bevel=0)                    # vision slits
    bx, bz, blean = _flank((2.3, 5.48), (2.05, 6.45), .55, .012)
    for s in (-1, 1):
        for yy in (-3.25, -2.35):
            if bridge_glass:
                glass.box((.04, .78, .5), loc=(s * bx, yy, bz), rot=(0, -s * blean, 0), bevel=0)
            else:
                armor.box((.12, .82, .56), loc=(s * (bx + .04), yy, bz), rot=(0, -s * blean, 0), bevel=.02, seg=1)
    armor.box((4.45, 2.8, .12), loc=(0, -2.75, 6.5), bevel=.03, seg=1)
    snowy(a, (4.05, 2.4, .08), (0, -2.72, 6.57))
    for s in (-1, 1):
        steel.box((.3, .3, .12), loc=(s * 2.28, -4.05, 6.0), bevel=0)
        _headlamp(a, (s * 2.42, -4.2, 6.12), r=.13)
    if antenna:
        _antenna(a, None, -3.3, 6.2, 4.3, 1.8)


def _fortress_tub(a, x, y):
    """Armoured sponson tub on the chassis deck (z 3.5 .. 4.36) for a cupola or gun turret."""
    armor = a.part('Armor', 'Armor')
    armor.cyl(.72, .86, loc=(x, y, 3.93), seg=18, bevel=.04)
    armor.cyl(.76, .08, loc=(x, y, 4.2), seg=18, bevel=0)


def _mg_cupola(a, name, x, y, z=4.37, flak=False):
    """The fortress's MG cupola (copied) on its own mount `name`; flak=True arms it with twin heavy
    flak barrels and ammunition drums instead of the machine guns."""
    m = pivot(a, name, (x, y, z))
    cup = a.part('MG_cupola', 'Team', m)
    cup.cyl(.56, .4, loc=(0, 0, .21), seg=16, bevel=.04)
    cup.sphere((.5, .5, .22), loc=(0, 0, .4), seg=16, rings=8, cut=0)
    marm = a.part('MG_armor', 'Armor', m)
    marm.box((.5, .3, .3), loc=(0, -.5, .24), bevel=.04, seg=1)
    a.part('MG_glass', 'Glass', m).box((.2, .05, .08), loc=(.25, -.5, .45), rot=(0, 0, .45), bevel=0)
    mg = a.part('MG_guns', 'Steel', m)
    if flak:
        for dx in (-.15, .15):
            mg.cyl(.05, 1.4, loc=(dx, -1.3, .26), rot=FORWARD, seg=8, bevel=0)
            mg.cyl(.075, .2, loc=(dx, -1.95, .26), rot=FORWARD, seg=8, bevel=0)
        for s in (-1, 1):
            a.part('Flak_drums', 'Crate', m).cyl(.18, .26, loc=(s * .55, .1, .35), rot=ACROSS, seg=10, bevel=.03, bseg=1)
        tip, zb = -2.07, .26
    else:
        for dx in (-.11, .11):
            mg.cyl(.035, .95, loc=(dx, -1.1, .24), rot=FORWARD, seg=8, bevel=0)
            mg.cyl(.05, .14, loc=(dx, -1.55, .24), rot=FORWARD, seg=8, bevel=0)
        tip, zb = -1.63, .24
    pivot(a, name.replace('Mount_', 'Muzzle_'), (0, tip, zb), name)


def _fortress_roof(a, radar=True, stacks=True):
    """Superstructure roof (copied): smokestacks, roof hatches and vents, and the radar mast with its
    spinning `Radar` dish if `radar`."""
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    for s in (-1, 1):
        x = s * 2.1
        if stacks:
            steel.lathe([(.4, 5.46), (.4, 6.2), (.34, 6.35), (.34, 6.62)], loc=(x, 3.75, 0), seg=14)
            armor.cyl(.425, .12, loc=(x, 3.75, 5.9), seg=14, bevel=0)
            a.part('Soot', 'Charred').cyl(.28, .05, loc=(x, 3.75, 6.63), seg=12, bevel=0)
        armor.cyl(.26, .07, loc=(s * 1.35, -1.1, 5.52), seg=12, bevel=.02, bseg=1)
        dark.grille(.9, .7, loc=(s * 2.0, 2.3, 5.51), rot=(-R90, 0, 0), slats=4, depth=.07, thickness=.04)
    if radar:
        steel.cyl(.16, 2.0, loc=(0, 4.2, 6.48), r2=.1, seg=10, bevel=0)
        armor.cyl(.3, .12, loc=(0, 4.2, 5.54), seg=12, bevel=.02, bseg=1)
        for zz in (6.1, 6.9):
            steel.box((.9, .06, .06), loc=(0, 4.2, zz), bevel=0)
        a.part('Beacon', 'Alloy').sphere(.06, loc=(.45, 4.2, 6.96), seg=6, rings=4)
        r = a.pivot('Radar', (0, 4.2, 7.48))
        rm = a.part('Radar_mast', 'Steel', r)
        rm.cyl(.2, .12, loc=(0, 0, .06), seg=12, bevel=.02, bseg=1)
        rm.box((.2, .3, .42), loc=(0, .08, .3), bevel=.03, seg=1)
        rm.limb((0, -.2, .45), (0, -.62, .5), .05, .05, bevel=0)
        _dish(a.part('Radar_dish', 'Armor', r), (0, -.12, .45), .85, .34, depth=.2, seg=14, tilt=.2)


def _rocket_battery(a, name, x, y, z=4.3):
    """The fortress's rocket battery (copied) on its own mount `name`: a 3 x 4 pod raised 25 degrees."""
    rk = pivot(a, name, (x, y, z))
    a.part('Launcher_base', 'Steel', rk).cyl(.72, .1, loc=(0, 0, .06), seg=16, bevel=.02, bseg=1)
    lbase = a.part('Launcher_armor', 'Armor', rk)
    lbase.box((.8, .8, .45), loc=(0, .1, .33), bevel=.04)
    for s in (-1, 1):
        lbase.box((.1, .5, .5), loc=(s * .7, .1, .72), bevel=.02, seg=1)
    pitch = math.radians(25)
    lrot = (-pitch, 0, 0)
    centre = Vector((0, 0, .98))
    pod = _frame(centre, lrot)
    a.part('Rocket_pod', 'Team', rk).box((1.3, 1.6, .9), loc=centre, rot=lrot, bevel=.05)
    band = a.part('Pod_bands', 'Armor', rk)
    for yy in (-.66, .66):
        band.box((1.35, .12, .95), loc=pod @ Vector((0, yy, 0)), rot=lrot, bevel=.015, seg=1)
    a.part('Launcher_steel', 'Steel', rk).cyl(.08, 1.56, loc=(0, .1, .72), rot=ACROSS, seg=8, bevel=0)
    for row in (-.25, 0, .25):
        for col in (-.45, -.15, .15, .45):
            _tube_mouth(a, rk, pod @ _frame((col, -.8, row), FORWARD), .1, protrude=.04, seg=8)
    pivot(a, name.replace('Mount_', 'Muzzle_'), tuple(pod @ Vector((0, -.86, 0))), name)


def _howitzer_turret(a, snow=True):
    """The fortress's barbette and howitzer `Turret` (copied)."""
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    armor.cyl(1.75, .76, loc=(0, 1.0, 5.86), seg=28, bevel=.04)
    steel.cyl(1.8, .1, loc=(0, 1.0, 6.28), seg=28, bevel=0)
    t = a.pivot('Turret', (0, 1.0, 6.33))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.2, 2.05), (1.2, 2.05), (1.75, 1.2), (1.75, -.85), (1.05, -1.6), (-1.05, -1.6), (-1.75, -.85),
               (-1.75, 1.2)]
    turret.prism(outline, 1.18, loc=(0, 0, .6), axis='Z', bevel=.07, taper=.88)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((1.3, .6, .95), loc=(0, -1.72, .72), bevel=.06, taper=(.94, .9))
    tarm.cyl(.34, .4, loc=(0, -2.1, .75), rot=FORWARD, seg=14, bevel=.04)
    tip = _barrel(a, t, start_y=-2.05, length=4.4, radius=.17, height=.75, brake=(.52, .6, .48),
                  sleeve=(.3, 1.1, .26), seg=14)
    a.part('Muzzle_brake', 'Undercarriage', t).box((.48, .18, .44), loc=(0, tip[1] + .74, .75), bevel=.04)
    a.pivot('Muzzle_main', tip, t)
    for s in (-1, 1):
        tsteel.cyl(.09, .6, loc=(s * .26, -2.5, 1.02), rot=FORWARD, seg=8, bevel=0)
        tarm.box((.16, 1.6, .5), loc=(s * 1.6, .5, .55), bevel=.03, seg=1)
        _smoke(a, tsteel, 1.1, -.75, 1.25, s, count=3, gap=.1, r=.055, depth=.18)
    tsteel.cyl(.34, .24, loc=(.85, .3, 1.28), seg=16, bevel=.04)
    a.part('Cupola_top', 'Armor', t).cyl(.28, .08, loc=(.85, .3, 1.43), seg=16, bevel=.02, bseg=1)
    _periscopes(a.part('Periscope', 'Glass', t), .85, .3, 1.3, .35, 5)
    a.part('Hatch', 'Armor', t).cyl(.28, .07, loc=(-.7, .9, 1.2), seg=14, bevel=.02, bseg=1)
    tsteel.box((.4, .36, .26), loc=(-.85, -.8, 1.28), bevel=.04)
    a.part('Sight', 'Glass', t).box((.3, .04, .14), loc=(-.85, -.99, 1.3), bevel=0)
    a.part('Vents', 'Undercarriage', t).grille(1.0, .5, loc=(.55, 1.4, 1.2), rot=(-R90, 0, 0), slats=4, depth=.07,
                                               thickness=.04)
    tarm.box((1.4, .1, .6), loc=(0, 2.06, .6), bevel=.02, seg=1)
    if snow:
        _snow(a, (.9, .5, .06), (-.55, 1.5, 1.2), t)


def _silo(a, x, y):
    """Missile silo on the rear deck (copied), its doors open fore and aft so it fits between the two
    rocket batteries; two missiles show. `Muzzle_missile` over the mouths."""
    armor = a.part('Armor', 'Armor')
    dark = a.part('Deck', 'Undercarriage')
    armor.shell(chamfered(1.3, 1.4, .15), .22, .08, loc=(x, y, 4.28), bevel=.015)
    dark.prism(chamfered(1.16, 1.26, .12), .02, loc=(x, y, 4.32), axis='Z', bevel=0)
    for dx in (-.28, .28):
        a.part('Silo_missiles', 'Fuel').lathe([(.2, 4.2), (.2, 4.36), (.14, 4.47), (.05, 4.55), (0, 4.57)],
                                              loc=(x + dx, y, 0), seg=10)
        a.part('Hazard_bands', 'Hazard').cyl(.205, .06, loc=(x + dx, y, 4.35), seg=10, bevel=0)
    lean = math.radians(30)
    for s in (-1, 1):
        armor.box((1.2, .06, .66), loc=(x, y + s * (.71 + .33 * math.sin(lean)), 4.5 + .33 * math.cos(lean)),
                  rot=(-s * lean, 0, 0), bevel=.015, seg=1)
    a.pivot('Muzzle_missile', (x, y, 4.62))


def mobile_fortress(a):
    """Tracked land-crawler fortress (mb_bosses.mobile_fortress) with one empty per weapon mount: the
    howitzer `Turret`, two rocket batteries side by side on the rear deck (`Mount_rocket` left,
    `Mount_rocket.001` right) with the missile silo between them (`Muzzle_missile`), and an MG cupola
    on each front corner (`Mount_mg` left, `Mount_mg.001` right, where the searchlight tower stood)."""
    _fortress_chassis(a)
    for s in (-1, 1):
        _fortress_tub(a, s * 3.2, -6.0)
    _mg_cupola(a, 'Mount_mg', 3.2, -6.0)
    _mg_cupola(a, 'Mount_mg.001', -3.2, -6.0)
    _fortress_roof(a)
    _rocket_battery(a, 'Mount_rocket', 1.9, 6.0)
    _rocket_battery(a, 'Mount_rocket.001', -1.9, 6.0)
    _silo(a, 0, 6.05)
    _snow(a, (1.2, .4, .07), (-2.6, 5.05, 4.31))
    _howitzer_turret(a)


# ----------------------------------------------------------------------------- fortress_hive
def _drone_rack(a, name, x, y, z=4.3):
    """Trainable drone launch rack on its own mount `name`: a turntable and yoke, an inclined ramp with
    twin rails, a one-way attack drone ready on top and a second one slung under the ramp, a booster
    bottle and a blast deflector; `Muzzle_missile*` at the ready drone's nose."""
    from mb_new_trucks import _shahed
    m = pivot(a, name, (x, y, z))
    a.part('Rack_base', 'Steel', m).cyl(.8, .12, loc=(0, 0, .06), seg=16, bevel=.02, bseg=1)
    base = a.part('Rack_armor', 'Armor', m)
    base.box((1.0, 1.0, .4), loc=(0, .2, .32), bevel=.04, seg=1)
    pitch = math.radians(20)
    rot = (-pitch, 0, 0)
    frame = _frame((0, 0, 1.05), rot)
    a.part('Rack_ramp', 'Team', m).box((.9, 2.6, .12), loc=frame @ Vector((0, 0, 0)), rot=rot, bevel=.03, seg=1)
    for s in (-1, 1):
        a.part('Rack_rails', 'Steel', m).box((.06, 2.7, .08), loc=frame @ Vector((s * .3, 0, .09)), rot=rot, bevel=0)
        base.box((.12, .5, .8), loc=(s * .45, .5, .7), bevel=.02, seg=1)                          # yoke arms
    a.part('Rack_stripe', 'SafetyStripe', m).box((.92, .1, .13), loc=frame @ Vector((0, -1.2, 0)), rot=rot, bevel=0)
    base.box((1.1, .12, .6), loc=frame @ Vector((0, 1.4, .1)), rot=(-pitch + .5, 0, 0), bevel=.02, seg=1)  # deflector
    k = .72
    _shahed(a, frame @ _frame((0, -.1, .2), (0, 0, 0)), m, k=k)
    _shahed(a, frame @ _frame((0, .15, -.24), (0, 0, 0)), m, k=k)
    a.part('Rack_booster', 'Hazard', m).cyl(.09, .5, loc=frame @ Vector((0, 1.05, .28)), rot=(R90 - pitch, 0, 0),
                                             seg=8, bevel=0)
    pivot(a, name.replace('Mount_', 'Muzzle_'), tuple(frame @ Vector((0, -.1 - 1.52 * k, .2))), name)


def _sam_battery(a, name, x, y, z):
    """SAM battery on its own mount `name`: a turntable, a yoke with a guidance radar and a box of four
    big canisters raised 30 degrees; `Muzzle_rocket` at the canister face (the canisters'
    `Launcher_tubes_bore` face is the rocket slot's launch face)."""
    m = pivot(a, name, (x, y, z))
    a.part('Sam_base', 'Steel', m).cyl(.75, .12, loc=(0, 0, .06), seg=16, bevel=.02, bseg=1)
    arm = a.part('Sam_armor', 'Armor', m)
    arm.box((.9, .9, .4), loc=(0, .15, .32), bevel=.04, seg=1)
    for s in (-1, 1):
        arm.box((.12, .6, .6), loc=(s * .62, .15, .72), bevel=.02, seg=1)
    pitch = math.radians(30)
    lrot = (-pitch, 0, 0)
    c = Vector((0, .05, 1.0))
    box = _frame(c, lrot)
    a.part('Sam_box', 'Team', m).box((1.1, 1.5, .95), loc=c, rot=lrot, bevel=.05, seg=1)
    for yy in (-.62, .62):
        arm.box((1.14, .1, .99), loc=box @ Vector((0, yy, 0)), rot=lrot, bevel=.015, seg=1)
    for cx in (-.26, .26):
        for cz in (-.22, .22):
            _tube_mouth(a, m, box @ _frame((cx, -.75, cz), FORWARD), .19, protrude=.05, seg=10, name='Launcher_tubes')
    a.part('Sam_radar', 'Armor', m).box((.7, .08, .5), loc=(0, .72, 1.25), rot=(.3, 0, 0), bevel=.02, seg=1)
    pivot(a, name.replace('Mount_', 'Muzzle_'), tuple(box @ Vector((0, -.8, 0))), name)


def fortress_hive(a):
    """Drone-carrier fortress ("Hive"): the mobile fortress crawler with drone bays in its chassis
    flanks, a big radar dome on a tower where the howitzer stood, a SAM battery on the rear roof
    (`Mount_rocket`), two trainable drone launch racks on the rear deck (`Mount_missile` left,
    `Mount_missile.001` right) and a twin flak cupola on each front corner (`Mount_mg`,
    `Mount_mg.001`)."""
    _fortress_chassis(a, snow=False, antenna=False)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    for s in (-1, 1):
        _fortress_tub(a, s * 3.2, -6.0)
    _mg_cupola(a, 'Mount_mg', 3.2, -6.0, flak=True)
    _mg_cupola(a, 'Mount_mg.001', -3.2, -6.0, flak=True)
    _fortress_roof(a, radar=False)
    # Drone bays: dark openings with striped sills in both chassis flanks.
    for s in (-1, 1):
        for y in (-3.1, 3.1):
            a.part('Bay_openings', 'Undercarriage').box((.1, 2.2, 1.0), loc=(s * 3.62, y, 3.62), bevel=0)
            for zz in (3.08, 4.16):
                a.part('Bay_sills', 'SafetyStripe').box((.14, 2.3, .1), loc=(s * 3.64, y, zz), bevel=0)
            for dy in (-1.15, 1.15):
                armor.box((.16, .12, 1.12), loc=(s * 3.64, y + dy, 3.62), bevel=0)
    # Big radar dome on a tower over the old barbette.
    armor.cyl(1.25, 1.0, loc=(0, 1.0, 5.98), seg=24, bevel=.04)
    steel.cyl(1.32, .1, loc=(0, 1.0, 6.5), seg=24, bevel=0)
    a.part('Radar_dome', 'Fuel').sphere(1.55, loc=(0, 1.0, 6.62), seg=24, rings=12, cut=-.15)
    a.part('Dome_band', 'Armor').cyl(1.535, .12, loc=(0, 1.0, 6.6), seg=24, bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.1, loc=(0, 1.0, 8.2), seg=8, rings=5)
    _antenna(a, None, 1.0, 1.9, 6.4, 1.2)                                       # on the dome tower's rim
    _sam_battery(a, 'Mount_rocket', 0, 3.6, 5.5)
    _drone_rack(a, 'Mount_missile', 1.85, 6.15)
    _drone_rack(a, 'Mount_missile.001', -1.85, 6.15)


# ----------------------------------------------------------------------------- fortress_bastion
def _autocannon_turret(a, name, x, y, z):
    """Squat autocannon turret on its own mount `name`: a faceted armoured housing, twin 35 mm barrels
    with flash hiders, ammunition boxes and a sight; `Muzzle_gun*` between the tips."""
    m = pivot(a, name, (x, y, z))
    body = a.part('Gun_turret', 'Team', m)
    body.prism([(-.55, .55), (.55, .55), (.7, .15), (.7, -.3), (.45, -.62), (-.45, -.62), (-.7, -.3), (-.7, .15)], .55,
               loc=(0, 0, .29), axis='Z', bevel=.05, taper=.85)
    arm = a.part('Gun_turret_armor', 'Armor', m)
    arm.box((.7, .28, .4), loc=(0, -.68, .32), bevel=.04, seg=1)
    guns = a.part('Gun_barrels', 'Steel', m)
    for dx in (-.16, .16):
        guns.cyl(.06, 1.9, loc=(dx, -1.7, .34), rot=FORWARD, seg=8, bevel=0)
        guns.cyl(.085, .22, loc=(dx, -2.6, .34), rot=FORWARD, seg=8, bevel=0)
        guns.cyl(.09, .3, loc=(dx, -.95, .34), rot=FORWARD, seg=8, bevel=0)
    for s in (-1, 1):
        a.part('Gun_ammo', 'Crate', m).box((.24, .5, .3), loc=(s * .66, .15, .34), bevel=.03, seg=1)
    a.part('Gun_sight', 'Glass', m).box((.18, .04, .1), loc=(.3, -.58, .62), bevel=0)
    pivot(a, name.replace('Mount_', 'Muzzle_'), (0, -2.73, .34), name)


def fortress_bastion(a):
    """Bunker fortress ("Bastion"): the mobile fortress crawler under thick slab armour (plates over the
    superstructure flanks and the chassis sides, an armoured shutter with vision slits over the bridge),
    an autocannon turret on a tub at each corner (`Mount_gun` front left, `Mount_gun.001` front right,
    `Mount_gun.002` rear left, `Mount_gun.003` rear right), a heavy mortar laid 45 degrees up in an
    armoured pit on the roof (`Turret`, `Main_cannon`, `Muzzle_main`) and protection-system launchers
    at the roof corners."""
    _fortress_chassis(a, snow=False, portholes=False, bridge_glass=False)
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    slabs = a.part('Slab_armor', 'Armor')
    px, pz, plean = _flank((2.9, 4.28), (2.62, 5.5), .5, .08)
    for s in (-1, 1):
        for y in (-3.3, -1.1, 1.1, 3.3):                                           # superstructure slabs
            slabs.box((.18, 2.05, 1.05), loc=(s * px, y, pz), rot=(0, -s * plean, 0), bevel=.03, seg=1)
            _plate_bolts(steel, s * (px + .1), (y - .8, y + .8), pz + .3, r=.04, h=.05)
        for y in (-4.6, -1.55, 1.55, 4.6):                                         # chassis side slabs
            slabs.box((.2, 2.9, 1.1), loc=(s * 3.72, y, 3.72), bevel=.03, seg=1)
            _plate_bolts(steel, s * 3.83, (y - 1.2, y, y + 1.2), 4.1, r=.04, h=.05)
    for s in (-1, 1):
        _fortress_tub(a, s * 3.2, -6.0)
        _fortress_tub(a, s * 2.6, 6.25)
    _autocannon_turret(a, 'Mount_gun', 3.2, -6.0, 4.37)
    _autocannon_turret(a, 'Mount_gun.001', -3.2, -6.0, 4.37)
    _autocannon_turret(a, 'Mount_gun.002', 2.6, 6.25, 4.37)
    _autocannon_turret(a, 'Mount_gun.003', -2.6, 6.25, 4.37)
    _fortress_roof(a, radar=False)
    # Protection-system launchers at the roof corners.
    for sx in (-1, 1):
        for y in (-.9, 2.7):
            armor.box((.5, .5, .32), loc=(sx * 2.3, y, 5.66), bevel=.03, seg=1)
            for k in range(2):
                _tube_mouth(a, None, _frame((sx * (2.3 + .2), y - .12 + k * .24, 5.72), (.3, 0, sx * -R90)), .08,
                            protrude=.1, seg=8, name='Aps_tubes')
            a.part('Aps_sensors', 'Glass').box((.04, .3, .14), loc=(sx * 2.56, y, 5.6), bevel=0)
    # Mortar pit on the roof: a round armoured wall, the turntable and the mortar laid 45 degrees up.
    armor.shell([(1.95 * math.cos(u), 1.0 + 1.95 * math.sin(u)) for u in (k * math.tau / 20 for k in range(20))],
                .95, .22, loc=(0, 0, 5.48), bevel=.02)
    a.part('Pit_stripes', 'SafetyStripe').torus(1.84, .07, loc=(0, 1.0, 6.44), seg=24, ring=4)
    a.part('Deck', 'Undercarriage').cyl(1.74, .04, loc=(0, 1.0, 5.52), seg=20, bevel=0)
    for k in range(6):                                                            # ready rounds on the wall
        u = math.pi * 1.15 + k * .18
        a.part('Pit_shells', 'Fuel').cyl(.13, .7, loc=(1.6 * math.cos(u), 1.0 + 1.6 * math.sin(u), 5.9), seg=8,
                                         bevel=.04)
    t = a.pivot('Turret', (0, 1.0, 5.54))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.2, .1, loc=(0, 0, .05), seg=20, bevel=.02, bseg=1)
    tarm.box((1.4, 1.6, .4), loc=(0, .2, .3), bevel=.04, seg=1, taper=(.9, .9))
    # The tube's rear on its axis is A. The game pivots the barrel group 6 % of its length from the
    # back and 30 % of its height from the bottom; a buffer hanging under the breech sets that bottom,
    # so the pivot P falls on the axis just behind the breech, where the trunnion caps are.
    pitch = math.radians(45)
    A = Vector((0, .45, 1.2))
    at = _axis(A, pitch)
    rot = (R90 - pitch, 0, 0)
    L = 2.6
    P = Vector((0, A.y + .377, A.z - .377))
    tube = a.part('Main_cannon', 'Steel', t)
    tube.lathe([(.36, 0), (.34, L - .45), (.42, L - .4), (.42, L), (.27, L), (.27, L - .3)], loc=tuple(at(0)), rot=rot,
               seg=16)
    tube.cyl(.37, .14, loc=tuple(at(L * .5)), rot=rot, seg=16, bevel=0)
    a.part('Main_cannon_bore', 'Undercarriage', t).cyl(.26, .02, loc=tuple(at(L - .26)), rot=rot, seg=14, bevel=0)
    a.part('Main_cannon_breech', 'Armor', t).cyl(.46, .3, loc=tuple(at(-.15)), rot=rot, seg=16, bevel=.04)
    a.part('Mortar_tube_collar', 'Armor', t).cyl(.44, .5, loc=tuple(at(.6)), rot=rot, seg=16, bevel=.03)
    zb = A.z - 1.453
    a.part('Main_cannon_buffer', 'Armor', t).box((.3, .3, A.z - .45 - zb), loc=(0, A.y + .2, (zb + A.z - .45) / 2),
                                                bevel=.02, seg=1)
    for s in (-1, 1):
        tarm.box((.16, .6, P.z + .1), loc=(s * .56, P.y, (P.z + .1) / 2 + .02), bevel=.03, seg=1)   # trunnion brackets
        tsteel.cyl(.17, .1, loc=(s * .66, P.y, P.z), rot=ACROSS, seg=10, bevel=0)
    tsteel.cyl(.07, 1.0, loc=tuple(P), rot=ACROSS, seg=8, bevel=0)                                  # trunnion pin
    tsteel.limb((0, -.55, .45), tuple(at(1.2, -.38)), .14, .14, bevel=.02, seg=1)                   # elevation ram
    a.pivot('Muzzle_main', tuple(at(L + .02)), t)


# ============================================================================= mega gunship
def _chin_gun(a, name, x, y=-7.1, z=1.1):
    """Three-barrel chin cannon on its own mount `name` (copied from the mega gunship's)."""
    g = pivot(a, name, (x, y, z))
    a.part('Gun_turret', 'Armor', g).sphere(.32, loc=(0, 0, -.12), seg=14, rings=8)
    gun = a.part('Gun', 'Steel', g)
    gun.cyl(.13, .3, loc=(0, -.38, -.2), rot=FORWARD, seg=10, bevel=.02, bseg=1)
    for k in range(3):
        ang = R90 + k * math.tau / 3
        gun.cyl(.035, 1.1, loc=(math.cos(ang) * .06, -1.05, -.2 + math.sin(ang) * .06), rot=FORWARD, seg=6, bevel=0)
    gun.cyl(.11, .08, loc=(0, -1.45, -.2), rot=FORWARD, seg=10, bevel=0)
    pivot(a, name.replace('Mount_', 'Muzzle_'), (0, -1.62, -.2), name)


def _door_gun(a, name, s):
    """Door gun on its own mount `name` in the side door on side s (copied from the mega gunship's)."""
    a.part('Steel', 'Steel').box((.3, .3, .06), loc=(s * 1.43, -4.6, 1.62), bevel=0)                  # gun sill
    m = pivot(a, name, (s * 1.52, -4.6, 1.7))
    a.part('Door_gun_mount', 'Steel', m).cyl(.05, .5, loc=(0, 0, .25), seg=8, bevel=0)
    mgun = a.part('Door_gun', 'Armor', m)
    mgun.box((.16, .5, .18), loc=(0, .05, .55), bevel=.03, seg=1)
    mgun.box((.16, .22, .2), loc=(s * .17, .15, .5), bevel=.02, seg=1)
    barrels = a.part('Door_gun_barrels', 'Steel', m)
    barrels.cyl(.07, .8, loc=(0, -.6, .56), rot=FORWARD, seg=8, bevel=0)
    barrels.cyl(.085, .06, loc=(0, -.96, .56), rot=FORWARD, seg=8, bevel=0)
    pivot(a, name.replace('Mount_', 'Muzzle_'), (0, -1.02, .56), name)


def mega_gunship(a):
    """Tandem-rotor heavy gunship (mb_bosses.mega_gunship) with one empty per weapon mount: twin chin
    cannons (`Mount_gun` left, `Mount_gun.001` right), a door gun in each side door (`Mount_mg` left,
    `Mount_mg.001` right), `Muzzle_rocket` at the left rocket pods (main weapon) and
    `Muzzle_rocket.001` at the right ones (the secondary salvo), `Muzzle_missile` between the rails,
    `Rotor` front and `Rotor_rear`. The sensor ball moves to the nose centre between the chin guns."""
    body = a.part('Fuselage', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')
    body.loft([_squircle(-8.45, .45, 2.15, .42), _squircle(-8.1, .95, 2.2, .85), _squircle(-7.4, 1.22, 2.3, 1.15),
               _squircle(-6.5, 1.3, 2.35, 1.28), _squircle(5.6, 1.3, 2.35, 1.28), _squircle(7.3, 1.24, 2.62, 1.0),
               _squircle(8.45, 1.1, 3.05, .55)], bevel=0)
    arc = dict(n=13, a0=.22, a1=math.pi - .22)
    canopy = ((-8.1, .98, 2.2, .88), (-7.4, 1.25, 2.3, 1.18), (-7.1, 1.277, 2.317, 1.223))
    glass.loft([_squircle(y, w, zc, h, **arc) for y, w, zc, h in canopy])
    for y, w, zc, h in canopy:
        frames.tube(_squircle(y, w + .015, zc, h + .015, n=11, a0=.15, a1=math.pi - .15), .055, seg=6)
    for u in (R90, R90 - .7, R90 + .7):
        frames.tube([_squircle(y, w + .02, zc, h + .02, n=1, a0=u, a1=u)[0] for y, w, zc, h in canopy], .04, seg=5)
    for s in (-1, 1):
        glass.box((.5, .5, .03), loc=(s * .45, -7.95, 1.4), rot=(.9, 0, 0), bevel=0)
    for s in (-1, 1):
        glass.box((.04, .75, .45), loc=(s * 1.29, -6.65, 2.52), bevel=0)
        frames.box((.05, .82, .07), loc=(s * 1.29, -6.65, 2.78), bevel=0)
        armor.box((.05, 1.3, .5), loc=(s * 1.268, -6.35, 1.78), bevel=.015, seg=1)
        for y in (-3.4, -2.2, -1.0, 1.4, 2.6, 3.8):
            glass.box((.03, .3, .3), loc=(s * 1.3, y, 2.55), bevel=0)
        for y in (-2.8, 2.0):
            armor.box((.05, 1.6, .42), loc=(s * 1.268, y, 1.8), bevel=.015, seg=1)
            _plate_bolts(steel, s * 1.3, (y - .65, y, y + .65), 1.96, r=.025, h=.03)
    body.box((.76, 8.4, .3), loc=(0, -.35, 3.68), bevel=.1, seg=2)
    for y in (-3.1, -.6, 1.4, 3.3):
        armor.box((.8, .08, .32), loc=(0, y, 3.69), bevel=.02, seg=1)
    bands = a.part('Frame_bands', 'Armor')
    for y in (-5.2, -1.6, 2.0, 4.6):
        bands.loft([_squircle(y - .05, 1.32, 2.35, 1.3, n=20), _squircle(y + .05, 1.32, 2.35, 1.3, n=20)])
    body.box((1.4, 2.8, .8), loc=(0, -5.85, 3.8), bevel=.22, seg=2, taper=(.72, .82))
    steel.cyl(.17, .45, loc=(0, -5.8, 4.33), seg=10, bevel=0)
    steel.cyl(.34, .06, loc=(0, -5.8, 4.28), seg=12, bevel=0)
    body.prism([(3.6, 3.45), (8.4, 3.3), (8.4, 4.2), (7.9, 5.2), (5.7, 5.3), (4.5, 4.35)], 1.5, bevel=.14, seg=2)
    steel.cyl(.18, .4, loc=(0, 6.7, 5.43), seg=10, bevel=0)
    steel.cyl(.36, .06, loc=(0, 6.7, 5.36), seg=12, bevel=0)
    for s in (-1, 1):
        x = s * 1.38
        body.lathe([(.34, -1.65), (.46, -1.4), (.5, -.2), (.47, 1.1), (.36, 1.62)], loc=(x, 5.6, 4.3), rot=BACKWARD,
                   seg=14)
        dark.cyl(.35, .06, loc=(x, 3.95, 4.3), rot=FORWARD, seg=14, bevel=0)
        a.part('Intake_screens', 'Steel').torus(.36, .035, loc=(x, 3.9, 4.3), rot=FORWARD, seg=14, ring=4)
        for k in range(3):
            a.part('Intake_screens', 'Steel').box((.7, .03, .03), loc=(x, 3.88 - k * .012, 4.3),
                                                  rot=(0, k * math.pi / 3, 0), bevel=0)
        steel.cyl(.13, .14, loc=(x, 3.9, 4.3), rot=FORWARD, r2=.04, seg=8, bevel=0)
        armor.box((.6, 1.5, .28), loc=(s * .95, 5.5, 4.25), bevel=.04, seg=1)
        m = _frame((x + s * .08, 7.45, 4.42), (-R90 + .5, 0, s * -.35))
        dark.cyl(.3, .6, loc=m.to_translation(), rot=m.to_euler('XYZ'), seg=12, bevel=.02, bseg=1)
        a.part('Soot', 'Charred').cyl(.24, .04, loc=m @ Vector((0, 0, .29)), rot=m.to_euler('XYZ'), seg=12, bevel=0)
        dark.grille(.9, .45, loc=(s * .76, 6.6, 4.75), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)

    def sponson(y, w, h, s):
        return [(s * 1.45 + px, y, pz) for px, _, pz in _squircle(y, w, 1.3, h, n=12, p=2.6)]
    for s in (-1, 1):
        body.loft([sponson(-3.95, .22, .2, s), sponson(-3.3, .44, .4, s), sponson(3.9, .46, .42, s),
                   sponson(4.65, .24, .22, s)], bevel=0)
        for y in (-2.4, -.6, 1.2, 3.0):
            armor.box((.05, 1.5, .34), loc=(s * 1.905, y, 1.3), bevel=.012, seg=1)
        a.part('Flares', 'Armor').box((.12, .5, .3), loc=(s * 1.9, 4.05, 1.72), bevel=.02, seg=1)
        dark.box((.04, .42, .22), loc=(s * 1.97, 4.05, 1.72), bevel=0)
    tyres, gear = a.part('Tyres', 'Rubber'), a.part('Gear', 'Steel')
    for s in (-1, 1):
        for dx in (-.16, .16):
            tyres.cyl(.38, .2, loc=(s * 1.45 + dx, -3.25, .38), rot=ACROSS, seg=12, bevel=.06, bseg=1)
        gear.cyl(.06, .6, loc=(s * 1.45, -3.25, .38), rot=ACROSS, seg=6, bevel=0)
        gear.limb((s * 1.45, -3.25, .38), (s * 1.45, -3.1, 1.0), .12, .12, bevel=.02, seg=1)
        gear.limb((s * 1.45, -3.2, .5), (s * 1.3, -2.4, 1.05), .07, .07, bevel=0)
        tyres.cyl(.42, .24, loc=(s * 1.62, 4.1, .42), rot=ACROSS, seg=12, bevel=.07, bseg=1)
        gear.limb((s * 1.5, 4.1, .42), (s * 1.45, 4.0, 1.0), .13, .13, bevel=.02, seg=1)
        gear.limb((s * 1.5, 4.05, .55), (s * 1.3, 3.2, 1.0), .07, .07, bevel=0)
    pods = a.part('Pods', 'Armor')
    missiles, noses = a.part('Missiles', 'Fuel'), a.part('Missile_noses', 'Armor')
    fins = a.part('Missile_fins', 'Armor')
    for s in (-1, 1):
        body.prism([(s * 1.2, -.95), (s * 4.3, -.62), (s * 4.3, .5), (s * 1.2, .78)], .2, loc=(0, 0, 2.05), axis='Z',
                   bevel=.05)
        armor.box((.12, 1.0, .5), loc=(s * 4.33, -.05, 2.0), bevel=.02, seg=1)
        a.part('Wing_lights', 'TeamGlow').box((.06, .14, .07), loc=(s * 4.41, .2, 2.18), bevel=0)
        for x in (2.33, 3.02):
            x *= s
            armor.box((.12, .7, .28), loc=(x, -.1, 1.83), bevel=.02, seg=1)
            pods.lathe([(.23, -1.0), (.32, -.8), (.32, .85), (.28, 1.0)], loc=(x, -.25, 1.4), rot=FORWARD, seg=12)
            dark.cyl(.26, .03, loc=(x, -1.255, 1.4), rot=FORWARD, seg=12, bevel=0)
            for k in range(7):
                ox, oz = (0, 0) if k == 6 else (math.cos(k * math.tau / 6) * .15, math.sin(k * math.tau / 6) * .15)
                a.part('Pod_tubes', 'Steel').cyl(.045, .04, loc=(x + ox, -1.27, 1.4 + oz), rot=FORWARD, seg=6, bevel=0)
        x = s * 3.72
        armor.box((.1, 1.5, .16), loc=(x, -.1, 1.87), bevel=.02, seg=1)
        for dx in (-.19, .19):
            mx = x + dx
            for mz in (1.66, 1.4):
                missiles.cyl(.1, 1.5, loc=(mx, -.2, mz), rot=FORWARD, seg=10, bevel=0)
                noses.cyl(.1, .28, r2=.03, loc=(mx, -1.09, mz), rot=FORWARD, seg=10, bevel=0)
                for k in range(4):
                    _fin(fins, (mx, .42, mz), math.pi / 4 + k * R90, .08, .22, .02, .09)
            armor.box((.05, .5, .1), loc=(mx, -.2, 1.79), bevel=0)
        armor.box((.08, 1.3, .3), loc=(x, -.2, 1.53), bevel=.015, seg=1)
    a.pivot('Muzzle_rocket', (2.675, -1.3, 1.4))
    pivot(a, 'Muzzle_rocket.001', (-2.675, -1.3, 1.4))
    a.pivot('Muzzle_missile', (0, -1.25, 1.53))
    fbox(a.part('Door', 'Charred'), '+x', (1.29, -4.6, 2.3), (.9, .03, 1.3), out=.01)
    fbox(armor, '+x', (1.29, -3.95, 2.3), (.08, .05, 1.4), out=.02)
    fbox(a.part('Door', 'Charred'), '-x', (-1.29, -4.6, 2.3), (.9, .03, 1.3), out=.01)
    fbox(armor, '-x', (-1.29, -3.95, 2.3), (.08, .05, 1.4), out=.02)
    armor.box((.5, .4, .3), loc=(-1.35, -4.6, 3.35), bevel=.04, seg=1)
    steel.limb((-1.35, -4.6, 3.35), (-1.7, -4.6, 3.3), .08, .08, bevel=0)
    _door_gun(a, 'Mount_mg', 1)
    _door_gun(a, 'Mount_mg.001', -1)
    _chin_gun(a, 'Mount_gun', .56)
    _chin_gun(a, 'Mount_gun.001', -.56)
    armor.sphere(.19, loc=(0, -7.9, 1.32), seg=12, rings=8)                                        # sensor ball
    a.part('Sensor', 'Glass').cyl(.08, .04, loc=(0, -8.08, 1.32), rot=FORWARD, seg=10, bevel=0)
    a.part('Lamps', 'Lamp').box((.3, .2, .05), loc=(0, -6.2, 1.06), bevel=0)
    steel.tube([(1.2, -6.4, 2.95), (1.14, -7.8, 2.93), (1.08, -9.6, 2.9)], .065, seg=8)
    steel.cyl(.09, .22, loc=(1.08, -9.68, 2.9), rot=FORWARD, r2=.05, seg=8, bevel=0)
    for y in (-2.5, 2.0):
        steel.box((.04, .6, .3), loc=(0, y, 3.72), rot=(-.4, 0, 0), bevel=0)
    steel.cyl(.015, .8, loc=(.6, 1.0, 1.0), seg=5, bevel=0)
    fbox(armor, '+y', (0, 8.45, 3.0), (1.9, .05, .9), out=.02, bevel=.015)
    for x in (-.6, .6):
        steel.box((.12, .08, .08), loc=(x, 8.51, 2.56), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.09, loc=(0, 7.4, 5.28), seg=8, rings=5)
    steel.cyl(.2, .3, loc=(0, 8.2, 4.05), rot=BACKWARD, seg=10, bevel=.02, bseg=1)
    a.part('Sensor', 'Glass').cyl(.16, .04, loc=(0, 8.37, 4.05), rot=BACKWARD, seg=10, bevel=0)
    for s in (-1, 1):
        a.part('Nav_lights', 'TeamGlow').box((.05, .12, .08), loc=(s * .77, 7.6, 4.7), bevel=0)
        for y in (-3.0, 3.5):
            steel.box((.28, .22, .04), loc=(s * 1.98, y, 1.05), bevel=0)
        dark.box((.05, .5, .3), loc=(s * .77, 4.8, 3.95), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.07, loc=(0, 1.0, 1.05), seg=8, rings=5)
    steel.cyl(.12, .2, loc=(0, -.6, 1.0), seg=8, bevel=0)
    _rotor(a, 'Rotor', (0, -5.8, 4.6), R90)
    _rotor(a, 'Rotor_rear', (0, 6.7, 5.66), R90 + math.pi / 3)


# ============================================================================= drone mothership
def _quad_flak(a, name, y):
    """Quad flak gun on the envelope's back on its own mount `name` (copied from the mothership's)."""
    from mb_air3 import _env_r
    zt = _env_r(y)
    a.part('Armor', 'Armor').cyl(1.2, .2, loc=(0, y, zt + .08), seg=18, bevel=.03, bseg=1)
    m = pivot(a, name, (0, y, zt + .19))
    fb = a.part('Flak_body', 'Team', m)
    fb.cyl(1.05, .26, loc=(0, 0, .13), seg=18, bevel=.04, bseg=1)
    fb.box((1.35, 1.2, .66), loc=(0, .08, .58), bevel=.07, seg=1, taper=(.85, .9))
    a.part('Flak_shield', 'Armor', m).box((1.75, .1, .74), loc=(0, -.62, .64), rot=(-.25, 0, 0), bevel=.025, seg=1,
                                           taper=(.85, 1))
    a.part('Flak_sight', 'Glass', m).box((.22, .14, .12), loc=(.45, -.62, .88), rot=(-.25, 0, 0), bevel=0)
    flak = a.part('Flak_guns', 'Steel', m)
    for x in (-.3, .3):
        for z in (.5, .76):
            flak.cyl(.045, 2.0, loc=(x, -1.45, z), rot=FORWARD, seg=6, bevel=0)
            flak.cyl(.065, .2, loc=(x, -2.43, z), rot=FORWARD, seg=6, bevel=0)
    for s in (-1, 1):
        a.part('Flak_ammo', 'Crate', m).box((.3, .6, .4), loc=(s * .8, .25, .55), bevel=.03, seg=1)
    pivot(a, name.replace('Mount_', 'Muzzle_'), (0, -2.55, .63), name)


def drone_mothership(a):
    """Armoured drone-carrier airship (mb_air3.drone_mothership) with one empty per weapon mount: the twin
    autocannon `Turret` under the nose (`Muzzle_main`), a second twin cannon hanging under the gondola
    on `Mount_main.001` (`Muzzle_main.001`, the secondary mount of slot main), two quad flak guns on
    the back (`Mount_mg` forward, `Mount_mg.001` aft), `Muzzle_missile` at the drone bay and the four
    ducted `Propeller` .. `Propeller_4`. The hatch and an antenna move clear of the second flak gun,
    the keel skid ends ahead of the second cannon. Origin at the envelope centre (it flies)."""
    from mb_air import LEFT, RIGHT, Planform, _upright, _wing
    from mb_air3 import ENVELOPE, _ducted_fan, _env_plate, _env_r, _fpv_drone, _searchlight
    skin = a.part('Envelope', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    plates = a.part('Plates', 'Team')
    skin.lathe(ENVELOPE, rot=BACKWARD, seg=32)
    armor.lathe([(0, -13.68), (.32, -13.56), (1.36, -13.3), (1.7, -13.0), (1.62, -12.94), (0, -12.94)], rot=BACKWARD,
                seg=20)
    steel.cyl(.12, .5, r2=.04, loc=(0, -13.85, 0), rot=FORWARD, seg=8, bevel=0)
    armor.lathe([(.66, 13.4), (.62, 13.75), (.3, 14.05), (0, 14.1)], rot=BACKWARD, seg=12)
    a.part('Tail_light', 'TeamGlow').sphere(.1, loc=(0, 14.1, 0), seg=8, rings=5)
    step = 2.45
    for i in range(8):
        y0 = -10.4 + i * step
        _env_plate(armor, y0, y0 + step - .08, -.46, .46, na=5)
        for s in (-1, 1):
            _env_plate(plates, y0 + step / 2, min(y0 + step * 1.5 - .08, 10.2), s * .56, s * 1.08, na=4)
    for i in range(6):
        y0 = -9.0 + i * 2.7
        for s in (-1, 1):
            _env_plate(armor, y0, y0 + 2.62, s * 1.2, s * 1.72, na=4, out=.07, inn=.035)
    fin = Planform(0, 5.6, 7.0, 10.4, 6.2, 2.6, .42, .14)
    moving = a.part('Control_surfaces', 'Armor')
    for frame in (RIGHT, LEFT):
        _wing(skin, moving, fin, frame, cs=[(3.3, 5.4, .7)], lower=1.0, bevel=.02)
    for up in (0.0, math.pi):
        _wing(skin, moving, fin, _upright(0, 0, up), cs=[(3.3, 5.4, .7)], lower=1.0, bevel=.02)
    glow = a.part('Nav_lights', 'TeamGlow')
    for s in (-1, 1):
        glow.box((.08, .3, .1), loc=(s * 5.62, 11.7, 0), bevel=0)
    a.part('Beacon', 'TeamGlow').sphere(.12, loc=(0, 11.8, 5.64), seg=8, rings=5)
    for pv, x, y in (('Propeller', 5.6, -3.5), ('Propeller_2', -5.6, -3.5), ('Propeller_3', 5.6, 6.0),
                     ('Propeller_4', -5.6, 6.0)):
        _ducted_fan(a, pv, x, y, -.8)
    hull = a.part('Gondola', 'Team')
    rings = [_sec6(-7.5, .5, -4.7, 1.05, -4.25, 1.0, -3.3), _sec6(-6.9, .95, -5.35, 1.4, -4.45, 1.25, -3.3),
             _sec6(-2.0, .95, -5.35, 1.4, -4.45, 1.25, -3.3), _sec6(-1.3, .7, -5.0, 1.2, -4.4, 1.1, -3.3)]
    hull.loft(rings, bevel=.05, seg=1)
    glass = a.part('Windows', 'Glass')
    glass.box((1.7, .03, .32), loc=(0, -7.51, -3.98), bevel=0)
    frame = a.part('Window_frames', 'Armor')
    for x in (-.45, .45):
        frame.box((.06, .07, .4), loc=(x, -7.52, -3.98), bevel=0)
    frame.box((1.9, .05, .06), loc=(0, -7.54, -3.78), bevel=0)
    fx, fz, lean = _flank((1.4, -4.45), (1.25, -3.3), .3, .012)
    px, pz, plean = _flank((.95, -5.35), (1.4, -4.45), .52, .025)
    for s in (-1, 1):
        glass.box((.03, .5, .3), loc=(s * 1.24, -7.2, -3.98), rot=(0, 0, s * -.62), bevel=0)
        for y in (-6.3, -5.55, -4.8, -4.05, -3.3, -2.55):
            glass.box((.03, .52, .26), loc=(s * fx, y, fz), rot=(0, -s * lean, 0), bevel=0)
        for y, L in ((-5.4, 2.6), (-2.75, 1.5)):
            armor.box((.06, L, .56), loc=(s * px, y, pz), rot=(0, -s * plean, 0), bevel=.015, seg=1)
            steel.bolts([(s * (px + .035), y + d, pz + dz) for d in (-L / 2 + .12, L / 2 - .12) for dz in (-.18, .18)],
                        r=.03, h=.03, rot=(0, R90, 0), seg=6, bevel=0)
        steel.tube([(s * 1.46, -6.6, -4.42), (s * 1.46, -2.2, -4.42)], .025, seg=5)
        _searchlight(a, (s * .72, -7.2, -5.1), yaw=s * -.25, pitch=.3, r=.18)
    armor.cyl(.08, .16, loc=(0, -6.6, -5.38), seg=8, bevel=0)
    armor.sphere(.22, loc=(0, -6.6, -5.55), seg=12, rings=8)
    a.part('Sensor', 'Glass').cyl(.09, .04, loc=(0, -6.8, -5.57), rot=FORWARD, seg=10, bevel=0)
    steel.box((.16, 2.7, .1), loc=(0, -4.75, -5.38), bevel=0)                                  # keel skid (shortened)
    a.part('Lamps', 'Lamp').box((.34, .04, .08), loc=(0, -7.53, -4.45), bevel=0)
    steel.cyl(.012, 1.2, loc=(.55, -1.2, -5.5), seg=5, bevel=0)                                # trailing aerial
    bay = a.part('Bay', 'Armor')
    yb = 2.3
    for s in (-1, 1):
        bay.box((.1, 6.4, 1.9), loc=(s * 1.6, yb, -3.65), bevel=.02, seg=1)
    for y in (yb - 3.2, yb + 3.2):
        bay.box((3.2, .1, 1.9), loc=(0, y, -3.65), bevel=.02, seg=1)
    dark.box((3.1, 6.2, .04), loc=(0, yb, -3.85), bevel=0)
    stripe = a.part('Bay_sills', 'SafetyStripe')
    bars = a.part('Bay_sill_bars', 'Charred')
    doors = a.part('Bay_doors', 'Team')
    for s in (-1, 1):
        stripe.box((.14, 6.42, .12), loc=(s * 1.6, yb, -4.62), bevel=0)
        for k in range(8):
            bars.box((.16, .12, .15), loc=(s * 1.6, yb - 3.0 + k * .85, -4.62), rot=(.6, 0, 0), bevel=0)
        c = Vector((s * 1.66, yb, -4.62)) + Vector((s * math.sin(.35), 0, -math.cos(.35))) * .62
        doors.box((.05, 6.2, 1.2), loc=tuple(c), rot=(0, -s * .35, 0), bevel=.01, seg=1)
    for y in (yb - 3.2, yb + 3.2):
        stripe.box((3.4, .14, .12), loc=(0, y, -4.6), bevel=0)
    rails = a.part('Racks', 'Steel')
    for x in (-.78, .78):
        rails.box((.1, 6.1, .1), loc=(x, yb, -3.92), bevel=0)
        for k in range(5):
            _fpv_drone(a, x, yb + (k - 2) * 1.2, -4.16, k)
    a.pivot('Muzzle_missile', (0, yb, -4.62))
    _searchlight(a, (0, yb + 3.36, -4.35), yaw=math.pi, pitch=.3, r=.16)
    # Twin autocannon turret under the nose.
    yt = -10.8
    armor.prism([(yt - .7, -2.6), (yt + .7, -2.6), (yt + .4, -3.5), (yt - .4, -3.5)], .5, bevel=.03)
    steel.cyl(.62, .1, loc=(0, yt, -3.5), seg=16, bevel=0)
    t = a.pivot('Turret', (0, yt, -3.55))
    tb = a.part('Turret_body', 'Team', t)
    tb.cyl(.72, .5, r2=.6, loc=(0, 0, -.28), rot=(math.pi, 0, 0), seg=16, bevel=.05)
    tb.sphere((.58, .58, .25), loc=(0, 0, -.5), seg=16, rings=6, rot=(math.pi, 0, 0), cut=0)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((.8, .5, .46), loc=(0, -.55, -.38), bevel=.05, seg=1)
    a.part('Turret_sight', 'Glass', t).box((.2, .04, .1), loc=(.3, -.81, -.2), bevel=0)
    tips = []
    for x, suffix in ((-.2, ''), (.2, '_2')):
        tips.append(_gun(a, t, x, -.72, -.38, 1.7, .065, suffix=suffix, seg=10, sleeves=((.35, .2, .09),),
                         brake=(.36, .09, 2), brake_seg=10))
    a.pivot('Muzzle_main', tuple((Vector(tips[0]) + Vector(tips[1])) / 2), t)
    # Second twin cannon hanging under the rear of the gondola on its own mount.
    steel.cyl(.5, .1, loc=(0, -2.2, -5.33), seg=16, bevel=0)                                     # mount ring
    g = pivot(a, 'Mount_main.001', (0, -2.2, -5.38))
    gb = a.part('Gondola_gun_body', 'Team', g)
    gb.cyl(.55, .36, r2=.46, loc=(0, 0, -.18), rot=(math.pi, 0, 0), seg=16, bevel=.04)
    gb.sphere((.44, .44, .18), loc=(0, 0, -.36), seg=16, rings=6, rot=(math.pi, 0, 0), cut=0)
    a.part('Gondola_gun_armor', 'Armor', g).box((.66, .42, .36), loc=(0, -.46, -.3), bevel=.04, seg=1)
    gg = a.part('Gondola_guns', 'Steel', g)
    for x in (-.16, .16):
        gg.cyl(.055, 1.5, loc=(x, -1.35, -.3), rot=FORWARD, seg=8, bevel=0)
        gg.cyl(.08, .26, loc=(x, -.8, -.3), rot=FORWARD, seg=8, bevel=0)
        a.part('Gondola_gun_brakes', 'Undercarriage', g).cyl(.075, .2, loc=(x, -2.1, -.3), rot=FORWARD, seg=8, bevel=0)
    a.part('Gondola_gun_sight', 'Glass', g).box((.16, .04, .08), loc=(.25, -.67, -.18), bevel=0)
    pivot(a, 'Muzzle_main.001', (0, -2.22, -.3), 'Mount_main.001')
    # Two quad flak guns on the back.
    _quad_flak(a, 'Mount_mg', -4.8)
    _quad_flak(a, 'Mount_mg.001', 3.4)
    ys = [-10.4] + [y for _, y in ENVELOPE if -10.4 < y < 9.2] + [9.2]
    for s in (-1, 1):
        steel.tube([(s * (_env_r(y) + .45) * math.sin(.5), y, (_env_r(y) + .45) * math.cos(.5)) for y in ys], .025,
                   seg=4)
        for i in range(9):
            y = -10.4 + i * 2.45 - .04 if i < 8 else 9.2
            r = _env_r(y)
            steel.limb((s * (r + .02) * math.sin(.5), y, (r + .02) * math.cos(.5)),
                       (s * (r + .46) * math.sin(.5), y, (r + .46) * math.cos(.5)), .04, .04, bevel=0)
        _searchlight(a, (s * .9, -8.2, _env_r(-8.2) * math.cos(.25) + .2), yaw=s * .3, pitch=.15, r=.18, up=False)
    for y in (-1.8, 6.5):
        _antenna(a, None, .3, y, _env_r(y) + .02, 1.4)
    a.part('Hatch', 'Armor').cyl(.35, .1, loc=(0, .6, _env_r(.6) + .09), seg=12, bevel=.02, bseg=1)
    for k in range(4):
        a0 = -2.2 + k * 1.1
        _env_plate(armor, -12.3, -10.55, a0 + .04, a0 + 1.06, na=4, out=.07, inn=.04)
    for a0, a1 in ((.18, 1.39), (1.75, 2.96)):
        for s in (-1, 1):
            _env_plate(plates, 10.45, 12.0, s * a0, s * a1, na=4, out=.06, inn=.03)


# ============================================================================= nuke train
def nuke_train(a):
    """Armoured locomotive and missile wagon (mb_air3.nuke_train) with one empty per weapon mount: the
    twin flak `Turret` on the hood, an MG cupola on the cab roof (`Mount_mg`) and a second one on the
    wagon's launch-control cabin (`Mount_mg.001`, the cabin's antenna moved aside); the `Erector` and
    `Icbm_payload` as before."""
    from mb_air3 import ICBM_LENGTH, ICBM_R, _icbm, _trefoil_flat
    from mb_bosses import _bogie, _underframe
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Deck', 'Undercarriage')
    glass = a.part('Vision_slits', 'Glass')
    for y in (-8.55, -3.65):
        _bogie(a, y, 3, 1.1, .5, 3.2)
    _underframe(a, -10.62, -1.58)
    hull.loft([_sec6(-10.45, 1.5, 1.34, 1.5, 1.85, .9, 2.25), _sec6(-9.7, 1.62, 1.34, 1.62, 2.05, 1.2, 2.95),
               _sec6(-9.0, 1.62, 1.34, 1.62, 2.25, 1.22, 3.45), _sec6(-7.3, 1.62, 1.34, 1.62, 2.25, 1.22, 3.45),
               _sec6(-7.0, 1.62, 1.34, 1.62, 2.1, 1.18, 3.05), _sec6(-2.3, 1.62, 1.34, 1.62, 2.1, 1.18, 3.05),
               _sec6(-1.75, 1.57, 1.34, 1.57, 2.05, 1.1, 2.75)], bevel=.06, seg=2)
    armor.loft([[(-.35, -10.99, .15), (.35, -10.99, .15), (1.3, -10.69, .15), (1.4, -10.42, .15), (-1.4, -10.42, .15),
                 (-1.3, -10.69, .15)],
                [(-.3, -10.67, .95), (.3, -10.67, .95), (1.2, -10.52, .95), (1.35, -10.37, .95), (-1.35, -10.37, .95),
                 (-1.2, -10.52, .95)]], bevel=.03, seg=1)
    for s in (-1, 1):
        _headlamp(a, (s * .78, -10.46, 1.68), r=.15)
        a.part('Lamps', 'Lamp').box((.14, .04, .1), loc=(s * 1.05, -10.465, 1.95), bevel=0)
    gy, gz, grot = _glacis((-9.7, 2.95), (-9.0, 3.45), .55, .012)
    for x in (-.72, 0, .72):
        glass.box((.5, .1, .04), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=0)
    gy, gz, grot = _glacis((-9.7, 2.95), (-9.0, 3.45), .82, .03)
    armor.box((2.2, .2, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    gy, gz, grot = _glacis((-10.45, 2.25), (-9.7, 2.95), .5, .012)
    glass.box((.7, .1, .04), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=0)
    fx, fz, flean = _flank((1.62, 2.25), (1.22, 3.45), .6, .012)
    for s in (-1, 1):
        for y in (-8.55, -7.75):
            glass.box((.03, .5, .1), loc=(s * fx, y, fz), rot=(0, -s * flean, 0), bevel=0)
        fbox(armor, '+x' if s > 0 else '-x', (s * 1.62, -7.9, 1.72), (.62, .05, .7), out=.02, bevel=.01)
        steel.box((.04, .04, .5), loc=(s * 1.68, -7.5, 1.8), bevel=0)
        for y in (-8.55, -3.65):
            armor.box((.06, 3.3, .8), loc=(s * 1.665, y, 1.1), bevel=.015, seg=1)
            _plate_bolts(steel, s * 1.7, [y + d for d in (-1.4, -.7, 0, .7, 1.4)], 1.4, r=.028)
        for y in (-6.9, -4.2):
            armor.box((.04, .07, .64), loc=(s * 1.635, y, 1.7), bevel=0)
        dark.grille(1.1, .5, loc=(s * 1.64, -5.55, 1.72), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)
        dark.grille(1.1, .5, loc=(s * 1.64, -2.9, 1.72), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.035)
        px, pz, plean = _flank((1.62, 2.1), (1.18, 3.05), .64, .025)
        for y in (-6.3, -5.0, -3.7, -2.4):
            armor.box((.06, 1.2, .5), loc=(s * px, y, pz), rot=(0, -s * plean, 0), bevel=.015, seg=1)
            _plate_bolts(steel, s * (px + .03), (y - .5, y + .5), pz + .2, r=.025, h=.03)
        hx, hz, _ = _flank((1.62, 2.1), (1.18, 3.05), .3, .09)
        steel.tube([(s * hx, -6.8, hz), (s * hx, -2.0, hz)], .025, seg=5)
        for y in (-6.5, -4.4, -2.3):
            steel.box((.03, .03, .1), loc=(s * (hx - .04), y, hz - .03), bevel=0)
    for y, d in ((-6.6, .6), (-2.9, .5)):
        a.part('Fans', 'Rubber').cyl(d * .45, .04, loc=(0, y, 3.07), seg=14, bevel=0)
        dark.grille(1.3, d, loc=(0, y, 3.1), rot=(-R90, 0, 0), slats=4, depth=.07, thickness=.035)
    for s in (-1, 1):
        steel.cyl(.12, .45, loc=(s * .6, -2.35, 3.2), seg=10, bevel=0)
        a.part('Soot', 'Charred').cyl(.135, .05, loc=(s * .6, -2.35, 3.42), seg=10, bevel=0)
    steel.box((.06, .06, .1), loc=(-.55, -9.3, 3.49), bevel=0)
    steel.cyl(.05, .3, loc=(-.55, -9.3, 3.56), rot=FORWARD, r2=.09, seg=8, bevel=0)
    armor.box((.7, .5, .1), loc=(-.5, -7.6, 3.48), bevel=.02, seg=1)
    _antenna(a, None, -1.4, -2.6, 2.55, 1.2)
    armor.cyl(1.25, .14, loc=(0, -4.9, 3.06), seg=24, bevel=.02, bseg=1)
    t = a.pivot('Turret', (0, -4.9, 3.13))
    tb = a.part('Turret_body', 'Team', t)
    outline = [(-.9, 1.2), (.9, 1.2), (1.15, .6), (1.15, -.55), (.75, -1.05), (-.75, -1.05), (-1.15, -.55), (-1.15, .6)]
    tb.prism(outline, .85, loc=(0, 0, .45), axis='Z', bevel=.06, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tarm.box((1.1, .42, .62), loc=(0, -1.05, .52), rot=(-.21, 0, 0), bevel=.05, seg=1)
    tips = []
    for x, suffix in ((-.3, ''), (.3, '_2')):
        tips.append(_gun(a, t, x, -1.2, .55, 2.8, .075, pitch=.21, suffix=suffix, seg=10,
                         sleeves=((.2, .35, .12), (.62, .06, .09)), brake=(.45, .11, 3), brake_seg=10))
    a.pivot('Muzzle_main', tuple((Vector(tips[0]) + Vector(tips[1])) / 2), t)
    for s in (-1, 1):
        a.part('Ammo_drums', 'Crate', t).box((.3, .8, .46), loc=(s * 1.2, .15, .48), bevel=.04, seg=1)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tsteel.cyl(.06, .5, loc=(-.5, .8, 1.1), seg=8, bevel=0)
    _dish(a.part('Fire_control_dish', 'Armor', t), (-.5, .75, 1.45), .38, .3, depth=.14, seg=12, tilt=.3)
    a.part('Hatch', 'Armor', t).cyl(.26, .06, loc=(.45, .5, .9), seg=14, bevel=.02, bseg=1)
    a.part('Sight', 'Glass', t).box((.26, .04, .12), loc=(.62, -.77, .95), bevel=0)
    tsteel.box((.34, .3, .22), loc=(.62, -.62, .95), bevel=.03)

    def cupola(name, x, y, z0, base=.56, r=.46):
        armor.cyl(base, .1, loc=(x, y, z0 - .05), seg=16, bevel=.02, bseg=1)
        m = pivot(a, name, (x, y, z0))
        cup = a.part('MG_cupola', 'Team', m)
        cup.cyl(r, .26, loc=(0, 0, .14), seg=16, bevel=.04)
        cup.sphere((r - .06, r - .06, .16), loc=(0, 0, .26), seg=16, rings=8, cut=0)
        a.part('MG_armor', 'Armor', m).box((.32, .24, .2), loc=(0, -r + .06, .16), bevel=.03, seg=1)
        a.part('MG_glass', 'Glass', m).box((.16, .05, .06), loc=(.2, -r + .08, .32), rot=(0, 0, .45), bevel=0)
        mg = a.part('MG_gun', 'Steel', m)
        mg.cyl(.032, .72, loc=(0, -.85, .16), rot=FORWARD, seg=8, bevel=0)
        mg.cyl(.045, .12, loc=(0, -1.18, .16), rot=FORWARD, seg=8, bevel=0)
        pivot(a, name.replace('Mount_', 'Muzzle_'), (0, -1.25, .16), name)
    cupola('Mount_mg', .45, -8.3, 3.53)
    # Missile wagon.
    for y in (1.3, 8.5):
        _bogie(a, y, 2, 1.8, .46, 2.7)
    _underframe(a, -.82, 10.62)
    steel.box((.1, .5, .08), loc=(0, -1.2, 1.1), bevel=0)
    trough = [(-1.6, 1.34), (1.6, 1.34), (1.62, 2.2), (1.35, 2.7), (1.02, 2.7), (1.02, 2.05), (-1.02, 2.05),
              (-1.02, 2.7), (-1.35, 2.7), (-1.62, 2.2)]
    hull.loft([[(x, y, z) for x, z in trough] for y in (-.65, 10.45)], bevel=.04, seg=1)
    dark.box((2.0, 10.3, .04), loc=(0, 4.9, 2.06), bevel=0)
    fx, fz, flean = _flank((1.62, 2.2), (1.35, 2.7), .5, .015)
    stripe, bars = a.part('Chevrons', 'SafetyStripe'), a.part('Chevron_bars', 'Charred')
    sign, blades = a.part('Signs', 'SafetyStripe'), a.part('Trefoils', 'Charred')
    for s in (-1, 1):
        for y in (1.3, 8.5):
            armor.box((.06, 2.9, .8), loc=(s * 1.665, y, 1.1), bevel=.015, seg=1)
            _plate_bolts(steel, s * 1.7, [y + d for d in (-1.2, -.4, .4, 1.2)], 1.4, r=.028)
        for y0, y1 in ((.1, 3.4), (6.6, 10.1)):
            stripe.box((.04, y1 - y0, .3), loc=(s * fx, (y0 + y1) / 2, fz), rot=(0, -s * flean, 0), bevel=0)
            n = int((y1 - y0) / .5)
            for k in range(n):
                yk = y0 + (k + .5) * (y1 - y0) / n
                bars.box((.04, .12, .34), loc=(s * (fx + .012), yk, fz + .003), rot=(.6 * s, -s * flean, 0),
                         bevel=0)
        _trefoil_flat(sign, blades, (s * 1.62, 5.0, 1.78), s, .72)
        for y in (4.1, 5.9):
            armor.box((.04, .07, .8), loc=(s * 1.635, y, 1.76), bevel=0)
        a.part('Tail_lights', 'Alloy').box((.14, .04, .1), loc=(s * 1.3, 10.465, 2.3), bevel=0)
    cab = a.part('Control_cabin', 'Team')
    cab.box((3.1, 1.25, 2.05), loc=(0, -.1, 2.35), bevel=.06, seg=1, taper=(1, .7), shift=(0, -.18))
    for s in (-1, 1):
        glass.box((.03, .45, .1), loc=(s * 1.56, -.2, 2.95), bevel=0)
        a.part('Warning_lights', 'Alloy').cyl(.09, .14, loc=(s * 1.1, -.35, 3.43), seg=8, bevel=0)
    dark.grille(1.4, .5, loc=(0, -.73, 2.3), slats=4, depth=.05, thickness=.035)
    _dish(a.part('Datalink', 'Steel'), (.55, -.4, 3.55), .3, .3, depth=.1, seg=10, tilt=.6)
    steel.cyl(.05, .25, loc=(.55, -.35, 3.43), seg=6, bevel=0)
    _antenna(a, None, 1.3, -.1, 3.38, 1.2)
    _trefoil_flat(sign, blades, (1.55, -.05, 2.2), 1, .5)
    _trefoil_flat(sign, blades, (-1.55, -.05, 2.2), -1, .5)
    cupola('Mount_mg.001', -.45, -.28, 3.5, base=.48, r=.4)                         # on the cabin roof
    for s in (-1, 1):
        armor.box((.18, .8, .75), loc=(s * .92, 10.2, 2.35), bevel=.03, seg=1)
    steel.cyl(.12, 2.06, loc=(0, 10.25, 2.4), rot=ACROSS, seg=10, bevel=0)
    e = a.pivot('Erector', (0, 10.25, 2.4))
    cradle = a.part('Erector_frame', 'Steel', e)
    for x in (-.42, .42):
        cradle.box((.14, 9.3, .22), loc=(x, -4.7, .22), bevel=.02, seg=1)
    cradle.box((1.5, .5, .5), loc=(0, -.1, .18), bevel=.04, seg=1)
    ecl = a.part('Erector_clamps', 'Armor', e)
    for y in (-8.3, -5.9, -3.4, -1.6):
        ecl.box((1.4, .3, .32), loc=(0, y, .26), bevel=.03, seg=1)
    for y in (-6.25, -3.25):
        ecl.cyl(ICBM_R + .05, .22, loc=(0, y, .9), rot=FORWARD, seg=20, bevel=.02, bseg=1)
    p = a.pivot('Icbm_payload', (0, -ICBM_LENGTH / 2, .9), e)
    _icbm(a, p, seg=20, detail=True)


# ============================================================================= sky fortress
def _side_mount(a, name, loc, tilt=.14):
    """A left-side gun position on its own mount `name` at loc (on the fuselage side): returns
    (pivot, at, rot), `at(t)` giving the point t metres out along the barrel (+X, tilted down by `tilt`)
    relative to the pivot."""
    m = pivot(a, name, loc)
    d = Vector((math.cos(tilt), 0, -math.sin(tilt)))
    return m, (lambda t: tuple(d * t)), (0, R90 + tilt, 0)


def sky_fortress(a):
    """Boss gunship ("Spectre", AC-130 lineage, 1.3x the sky gunship): the sky gunship's airframe in a
    dark scheme (black fuselage and wing, team-painted nacelles, fin, sponsons and stripes), four gun
    sponsons bulging from the left side and a sensor sponson on the right, ECM pods under the wings and
    flare pods on the tail. Left-side battery front to back: the 25 mm gatling on `Mount_mg`, two
    40 mm cannons on `Mount_gun` and `Mount_gun.001`, the 105 mm howitzer on `Mount_main`, each barrel
    out of the left (+X) with its `Muzzle_*`; `Muzzle_ramp` at the rear ramp's launcher; `Propeller` ..
    `Propeller_4` spin about Y. Origin at the fuselage centre (it flies)."""
    from mb_air import LEFT, RIGHT, Planform, _dome, _patch, _pylon, _sec, _skin_panel, _skin_z, _upright, _wing
    from mb_air2 import _turboprop
    body = a.part('Fuselage', 'EliteBlack')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Undercarriage', 'Undercarriage')
    moving = a.part('Control_surfaces', 'Armor')
    team = a.part('Team_panels', 'Team')
    glow = a.part('Wing_lights', 'EliteGlow')
    glass = a.part('Canopy', 'Glass')
    frames = a.part('Canopy_frames', 'Armor')

    def sec(y, w, zb, zt):
        return _sec(y, w, zb, zt, n=24, pt=2.2, pb=2.4)
    hull = [sec(-5.85, .5, -.62, .52), sec(-5.35, .82, -.86, .86), sec(-4.7, .95, -.92, .98), sec(-3.6, .98, -.93, 1.0),
            sec(2.4, .98, -.93, 1.0), sec(3.3, .96, -.74, 1.0), sec(4.3, .88, -.36, .98), sec(5.2, .7, .06, .95),
            sec(5.9, .44, .38, .9), sec(6.4, .22, .56, .82)]
    body.loft(hull + [[(0, 6.66, .7)]], bevel=.02, seg=1)
    armor.loft([[(0, -6.36, -.12)], _sec(-6.2, .24, -.4, .14, n=24), _sec(-5.8, .47, -.6, .42, n=24)], bevel=0)
    _patch(glass, hull, -5.85, -5.35, 9, 15, out=.02, inn=.012, bevel=0)
    for i in (10, 12, 14):
        frames.tube([tuple(Vector(r_[i]) + Vector((0, 0, .03))) for r_ in (hull[0], hull[1])], .022, seg=5)
    frames.tube([tuple(Vector(q) + Vector((0, 0, .03))) for q in hull[1][9:16]], .022, seg=5)
    _patch(glass, hull, -5.2, -4.85, 10, 14, out=.02, inn=.012, bevel=0)
    for s in (-1, 1):
        glass.box((.03, .42, .26), loc=(s * .905, -5.0, .56), rot=(0, 0, s * -.12), bevel=0)
    steel.tube([(.42, -4.3, .96), (.46, -5.6, 1.08), (.48, -6.5, 1.1)], .035, seg=8)
    steel.cyl(.05, .12, r2=.03, loc=(.48, -6.55, 1.1), rot=FORWARD, seg=8, bevel=0)
    # Team stripes round the fuselage and a spine band.
    _patch(team, hull, -3.4, -3.0, 13, 23, out=.016, inn=.012, bevel=0)
    _patch(team, hull, 4.0, 4.3, 13, 23, out=.016, inn=.012, bevel=0)
    _patch(team, hull, -3.0, 4.0, 17, 19, out=.014, inn=.012, bevel=0)
    for s in (-1, 1):
        armor.box((.1, .6, .3), loc=(s * .88, 4.3, .45), rot=(0, 0, s * .12), bevel=.02, seg=1)
        dark.grille(.5, .22, loc=(s * .935, 4.3, .45), rot=(0, 0, s * (R90 + .12)), slats=3, depth=.03, thickness=.03)
        glow.box((.02, .6, .04), loc=(s * .965, -3.0, .1), bevel=0)
        spon = [[(s * .86 + q[0], q[1], q[2]) for q in _sec(y, w, -1.0, -.25, n=12)] for y, w in
                ((-1.35, .24), (-.6, .3), (1.5, .3), (2.2, .22))]
        team.loft([[(s * .86, -1.95, -.6)]] + spon + [[(s * .86, 2.7, -.6)]], bevel=.02, seg=1)   # gear sponsons
    for y, z in ((-2.0, 1.0), (1.9, 1.0), (-.5, -.93)):
        steel.box((.02, .28, .2), loc=(0, y, z + (.08 if z > 0 else -.08)), rot=(-.35 if z > 0 else .35, 0, 0),
                  bevel=0, taper=(1, .5))
    body.loft([_dome(y, w, _skin_z(hull, y, w) - .04, z1) for y, w, z1 in
               ((-1.5, .4, 1.04), (-.9, .72, 1.2), (1.4, .72, 1.2), (2.2, .4, 1.04))], bevel=.02, seg=1)
    wing = Planform(0, 8.5, -.9, -.6, 2.3, 1.15, .36, .14, 1.1, 1.18)
    tracks = a.part('Flap_tracks', 'Armor')
    for frame in (RIGHT, LEFT):
        _wing(body, moving, wing, frame, cs=[(.95, 4.9, .7), (5.0, 8.25, .7)], bevel=0)
        _skin_panel(team, wing, frame, 6.2, 8.3, .12, .62)                                     # team wingtips
        for x in (1.4, 3.3, 5.6, 7.2):
            te, zb = wing.te(x), wing.bottom(x, .8)
            tracks.loft([[frame(x + q[0], q[1], q[2]) for q in _sec(y, .06, zb - h, zb + .03, n=6)]
                         for y, h in ((te - .75, .03), (te - .2, .12), (te + .25, .06))], bevel=0)
    for s in (-1, 1):
        glow.box((.06, .16, .06), loc=(s * 8.52, wing.le(8.5) + .15, wing.at(8.5)[3]), bevel=.01, seg=1)
    for pv, x in (('Propeller', -4.5), ('Propeller_2', -2.4), ('Propeller_3', 2.4), ('Propeller_4', 4.5)):
        _turboprop(a, x, wing.le(abs(x)) - 1.9, .9, pv, wing.te(abs(x)), 1 if x > 0 else -1)
    pylons = a.part('Pylons', 'Armor')
    for s in (-1, 1):                                                      # ECM pods where the tanks hung
        x = s * 3.45
        zb = wing.bottom(3.45)
        a.part('Ecm_pods', 'Armor').lathe([(0, 0), (.12, .2), (.2, .6), (.2, 2.0), (.12, 2.5), (.03, 2.7)],
                                          loc=(x, -1.9, zb - .36), rot=BACKWARD, seg=10)
        a.part('Ecm_windows', 'Glass').box((.03, .5, .14), loc=(x + s * .2, -.9, zb - .36), bevel=0)
        _pylon(pylons, x, -1.2, .3, zb + .05, zb - .15, w=.08)
    stab = Planform(.2, 3.35, 4.8, 5.55, 1.5, .85, .14, .07, .83)
    for frame in (RIGHT, LEFT):
        _wing(body, moving, stab, frame, cs=[(.4, 3.2, .68)], bevel=0)
    fin = Planform(0, 3.3, 4.25, 5.75, 2.3, 1.15, .2, .1)
    _wing(team, moving, fin, _upright(0, .76, 0), cs=[(.3, 3.1, .66)], lower=1.0)
    a.part('Beacon', 'EliteGlow').sphere(.06, loc=(0, 5.95, 4.08), seg=8, rings=5)
    # Gun sponsons bulging from the left side, one per gun, and a sensor sponson on the right.
    for y, w in ((-3.3, .36), (-.95, .45), (.75, .45), (2.85, .62)):
        team.loft([[(.62 + q[0], q[1], q[2]) for q in _sec(yy, ww, -.62, .5, n=12)]
                   for yy, ww in ((y - w - .3, .12), (y - w, .42), (y + w, .42), (y + w + .35, .12))], bevel=.02,
                  seg=1)
    team.loft([[(-.62 + q[0], q[1], q[2]) for q in _sec(yy, ww, -.55, .35, n=12)]
               for yy, ww in ((-2.7, .12), (-2.3, .42), (-.8, .42), (-.4, .12))], bevel=.02, seg=1)
    sensor = a.part('Sensor', 'Glass')
    for (x, y, z), rr, side in (((.5, -4.7, -.98), .24, 1), ((-1.02, -1.55, -.5), .22, -1)):
        armor.cyl(rr * .45, .2, loc=(x, y, z + rr * .9), seg=10, bevel=0)
        armor.sphere(rr, loc=(x, y, z), seg=12, rings=8)
        sensor.cyl(rr * .42, .04, loc=(x + side * (rr - .012), y, z - rr * .15), rot=ACROSS, seg=10, bevel=0)
    # 25 mm gatling.
    m, at, rot = _side_mount(a, 'Mount_mg', (1.02, -3.3, 0.0))
    a.part('Gatling_port', 'Armor', m).box((.18, .5, .42), loc=(0, 0, .02), bevel=.03, seg=1)
    gat = a.part('Gatling', 'Steel', m)
    gat.cyl(.08, .14, loc=at(.1), rot=rot, seg=10, bevel=0)
    for k in range(5):
        ang = k * math.tau / 5
        off = Vector((0, math.cos(ang) * .05, math.sin(ang) * .05))
        gat.cyl(.02, .72, loc=tuple(Vector(at(.5)) + off), rot=rot, seg=5, bevel=0)
    gat.cyl(.075, .06, loc=at(.8), rot=rot, seg=10, bevel=0)
    pivot(a, 'Muzzle_mg', at(.89), 'Mount_mg')
    # Two 40 mm cannons.
    for name, y in (('Mount_gun', -.95), ('Mount_gun.001', .75)):
        m, at, rot = _side_mount(a, name, (1.02, y, .05))
        a.part('Cannon_port', 'Armor', m).box((.2, .7, .5), loc=(0, 0, .02), bevel=.03, seg=1)
        c = a.part('Cannon', 'Steel', m)
        c.cyl(.085, .36, loc=at(.2), rot=rot, seg=10, bevel=.01, bseg=1)
        c.cyl(.065, 1.0, loc=at(.6), rot=rot, seg=10, bevel=0)
        c.cyl(.09, .2, r2=.06, loc=at(1.12), rot=rot, seg=10, bevel=0)
        pivot(a, name.replace('Mount_', 'Muzzle_'), at(1.24), name)
    # 105 mm howitzer.
    m, at, rot = _side_mount(a, 'Mount_main', (1.02, 2.85, .02))
    a.part('Howitzer_port', 'Armor', m).box((.24, 1.0, .72), loc=(0, 0, .02), bevel=.04, seg=1)
    h = a.part('Howitzer', 'Steel', m)
    h.cyl(.13, .5, loc=at(.25), rot=rot, seg=12, bevel=.015, bseg=1)
    h.cyl(.085, 1.5, loc=at(.85), rot=rot, seg=12, bevel=0)
    a.part('Howitzer_brake', 'Undercarriage', m).box((.2, .28, .24), loc=at(1.62), rot=(0, .14, 0), bevel=.03, seg=1)
    pivot(a, 'Muzzle_main', at(1.76), 'Mount_main')
    # Rear ramp launcher and flare pods.
    armor.box((.5, .5, .3), loc=(0, 4.55, -.42), bevel=.04, seg=1)
    for k in range(5):
        steel.cyl(.045, .44, loc=(-.16 + k * .08, 4.62, -.42), rot=BACKWARD, seg=6, bevel=0)
    a.pivot('Muzzle_ramp', (0, 4.95, -.42))
    a.post = [uniform_scale(1.3)]


BUILDERS = {
    'behemoth': (behemoth, dict(ao_distance=.9, grime_height=.8)),
    'behemoth_inferno': (behemoth_inferno, dict(ao_distance=.9, grime_height=.8)),
    'behemoth_tempest': (behemoth_tempest, dict(ao_distance=.9, grime_height=.8)),
    'mobile_fortress': (mobile_fortress, dict(ao_distance=1.1, grime_height=1.0)),
    'fortress_hive': (fortress_hive, dict(ao_distance=1.1, grime_height=1.0)),
    'fortress_bastion': (fortress_bastion, dict(ao_distance=1.1, grime_height=1.0)),
    'mega_gunship': (mega_gunship, dict(ao_distance=.8, grime_height=.5)),
    'drone_mothership': (drone_mothership, dict(ao_distance=1.2, ground=False)),
    'nuke_train': (nuke_train, dict(ao_distance=.8, grime_height=.7)),
    'sky_fortress': (sky_fortress, dict(ao_distance=.9, ground=False)),
}


if __name__ == '__main__':
    main(BUILDERS)
