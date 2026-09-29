"""Machine Brigade ground vehicles, second roster, built with frontier_kit.

A thermobaric rocket launcher on a tank chassis, a tracked infantry fighting vehicle, a gun-missile
air-defence truck and the premium titan tank (the self-propelled howitzer is in mb_artillery.py). Conventions and
helpers are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front, origin on the ground at
the hull centre, turret parts authored relative to the `Turret` empty.

Rig names (ModelLibrary.cs): `Turret` yaws; Main_cannon* / Muzzle_brake* parts under it recoil (twin
guns are Main_cannon and Main_cannon_2, with `Muzzle_main` centred between their openings).
`Muzzle_<slot>` empties sit at each weapon's opening, independently aimed weapons turn on
`Mount_<name>` and radars spin on `Radar` / `Radar_search`. Touching parts overlap or stand at least
1 cm apart, never face to face (coplanar faces z-fight).
"""
import math

from mathutils import Euler, Vector

import mb_weapons as wpn
from frontier_kit import chamfered
from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _coax, _dish, _flank, _frame, _glacis, _rws,
                         _smoke, _sponson_section, _tube_mouth, _wheel, tracks)


# ----------------------------------------------------------------------------- helpers
def _axis(base, pitch):
    """Points along a bore from `base`, pitched up by `pitch`: at(s, up, side) is s metres along the
    bore, `up` across it (perpendicular, in the vertical plane) and `side` along X."""
    d = Vector((0.0, -math.cos(pitch), math.sin(pitch)))
    u = Vector((0.0, math.sin(pitch), math.cos(pitch)))
    b = Vector(base)
    return lambda s, up=0.0, side=0.0: b + d * s + u * up + Vector((side, 0.0, 0.0))


def _gun(a, parent, x, y, z, length, radius, pitch=0.0, suffix='', seg=14, sleeves=(), extractor=None,
         brake=(.5, .2, 2), brake_seg=None):
    """Long gun from the mantlet at (x, y, z) forwards, pitched up by `pitch`: thermal-sleeve clamps
    [(fraction along, width, radius)], an optional bulged fume extractor (fraction of its centre,
    length, radius) and a grooved muzzle brake (length, radius, grooves) whose bore is recessed so
    it darkens in the baked AO. Parts Main_cannon<suffix> and Muzzle_brake<suffix>; returns the
    centre of the bore opening, where the muzzle empty goes."""
    rot = (R90 - pitch, 0, 0)
    at = _axis((x, y, z), pitch)
    cannon = a.part(f'Main_cannon{suffix}', 'Steel', parent)
    cannon.cyl(radius, length, loc=at(length / 2), rot=rot, seg=seg, bevel=.015, bseg=1)
    for f, w, r in sleeves:  # thin clamps stay unbevelled
        cannon.cyl(r, w, loc=at(length * f), rot=rot, seg=seg, bevel=.01 if w > .15 else 0, bseg=1)
    if extractor:
        f, w, r = extractor
        cannon.lathe([(radius * .9, 0), (r, w * .22), (r, w * .78), (radius * .9, w)], loc=at(length * f - w / 2),
                     rot=rot, seg=seg)
    bl, br, grooves = brake
    step = bl / (2 * grooves + 1)
    bore = radius * .72
    prof = [(radius * .9, 0), (br, .025)]
    for i in range(grooves):
        z0, z1 = (2 * i + 1) * step, (2 * i + 2) * step
        prof += [(br, z0), (br * .8, z0 + .012), (br * .8, z1 - .012), (br, z1)]
    prof += [(br, bl), (bore, bl), (bore, bl - min(.12, bl * .3))]
    a.part(f'Muzzle_brake{suffix}', 'Undercarriage', parent).lathe(prof, loc=at(length - .02), rot=rot,
                                                                   seg=brake_seg or seg)
    return tuple(at(length - .02 + bl))


def _ring_mouth(a, parent, m, r, protrude=.06, seg=8, name='Tubes'):
    """Open launcher tube mouth facing local +Z of matrix m: a steel cup whose bore bottom sits 2 cm
    behind the launcher face, so a dark face plate in front of the launcher shows through it.
    Cheaper than _tube_mouth's separate bore disk on launchers with many tubes."""
    a.part(name, 'Steel', parent).lathe([(r, -.04), (r, protrude), (r * .76, protrude), (r * .76, -.02)],
                                           loc=m.to_translation(), rot=m.to_euler('XYZ'), seg=seg)


def _skirts(part, x, y0, y1, z0, z1, panels, thick=.08, gap=.03, bevel=.025):
    """Side-skirt panels on both sides at |x|, from y0 to y1 with `gap` between panels. Returns the
    panel centres along Y."""
    length = (y1 - y0 - gap * (panels - 1)) / panels
    ys = [y0 + length / 2 + i * (length + gap) for i in range(panels)]
    for s in (-1, 1):
        for y in ys:
            part.box((thick, length, z1 - z0), loc=(s * x, y, (z0 + z1) / 2), bevel=bevel, seg=1)
    return ys


# howitzer: the tracked 155 mm self-propelled howitzer is built in mb_artillery.py.


# ----------------------------------------------------------------------------- thermobaric launcher
def thermobaric_launcher(a):
    """Heavy thermobaric rocket launcher (TOS-1A lineage) on a tank chassis: a massive armoured
    box of 24 tubes under a hood on a trainable launcher, over a low hull with a dozer blade,
    reactive armour on the glacis and skirts, rear fuel drums, an unditching log and a heavy machine gun
    on a tall pintle at the right rear corner of the hull (Mount_mg)."""
    tracks(a, 1.3, 6.1, .9, .35, 6, .48, belt_width=.6, wheel_seg=10, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.05, .5), (-3.4, 1.08), (3.22, 1.08), (3.22, .5)], 1.9, bevel=.05)       # belly
    nose, brow = (-3.5, 1.1), (-2.3, 1.45)
    hull.prism([(-3.34, 1.02), nose, brow, (3.28, 1.45), (3.38, 1.34), (3.38, 1.02)], 3.1, bevel=.06)
    # Dozer blade folded against the lower glacis.
    by, bz, brot = _glacis((-3.05, .5), (-3.4, 1.08), .45, .09)
    armor.box((2.3, .5, .08), loc=(0, by, bz), rot=(brot, 0, 0), bevel=.02, seg=1)
    for x in (-.8, 0, .8):
        ry, rz, _ = _glacis((-3.05, .5), (-3.4, 1.08), .45, .045)
        armor.box((.08, .44, .05), loc=(x, ry, rz), rot=(brot, 0, 0), bevel=0)
    # Reactive armour on the glacis and the front skirt panels.
    era = a.part('ERA', 'Armor')
    for row, u in enumerate((.3, .72)):
        gy, gz, grot = _glacis(nose, brow, u, .045)
        for x in ((-1.2, -.6, 0, .6, 1.2) if row == 0 else (-1.0, -.35, .35, 1.0)):
            era.box((.52, .4, .1), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
    ys = _skirts(hull, 1.71, -3.05, 3.05, .56, 1.3, 3, thick=.06)
    for s in (-1, 1):
        for y in (-2.5, -1.75):
            for z in (.8, 1.1):
                era.box((.07, .66, .26), loc=(s * 1.765, y, z), bevel=.015, seg=1)
        steel.bolts([(s * 1.75, y, 1.2) for y in (ys[1] - .6, ys[1] + .6, ys[2] - .6, ys[2] + .6)], r=.035, h=.03,
                    rot=ACROSS, bevel=0)
        gy, gz, grot = _glacis(nose, brow, .08, .03)
        a.part('Lamps', 'Lamp').box((.22, .08, .06), loc=(s * 1.3, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
        steel.box((.16, .2, .14), loc=(s * .75, 3.3, .8), bevel=.02, seg=1)                    # tow hooks
        a.part('Tail_lights', 'Alloy').box((.14, .05, .1), loc=(s * 1.35, 3.395, 1.25), bevel=.01, seg=1)
        deck.grille(1.1, .8, loc=(s * .72, 2.55, 1.46), rot=(-R90, 0, 0), slats=5, depth=.08, thickness=.04)
        # External fuel drums on the rear plate, strapped on brackets.
        x = s * .62
        hull.cyl(.26, .92, loc=(x, 3.66, 1.18), rot=ACROSS, seg=12, bevel=.04)
        for dx in (-.3, .3):
            steel.cyl(.272, .05, loc=(x + dx, 3.66, 1.18), rot=ACROSS, seg=12, bevel=0)
        steel.box((.1, .26, .1), loc=(x, 3.47, .94), bevel=.01, seg=1)
    # Unditching log across the rear deck, held by brackets.
    a.part('Log', 'Wood').cyl(.13, 2.7, loc=(0, 3.08, 1.595), rot=ACROSS, seg=10, bevel=.03)
    for x in (-1.1, 1.1):
        steel.box((.08, .32, .1), loc=(x, 3.08, 1.49), bevel=.01, seg=1)
    armor.cyl(.26, .06, loc=(0, -2.0, 1.47), seg=14, bevel=.02, bseg=1)                   # driver's hatch
    armor.box((.5, .8, .3), loc=(-1.25, 2.0, 1.6), bevel=.03, seg=1)                     # rear stowage bins
    armor.box((.5, .8, .3), loc=(1.25, 2.0, 1.6), bevel=.03, seg=1)
    _antenna(a, None, -1.45, 3.2, 1.45, 1.3)                                     # outside the launcher sweep

    t = a.pivot('Turret', (0, -.1, 1.45))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.15, .1, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                    # turntable
    tarm.box((2.1, 2.6, .28), loc=(0, .45, .24), bevel=.04)                             # launcher base
    L, H, W, D = 4.9, 1.0, 2.5, .22
    pitch = .045
    hinge = Vector((0, 2.0, .45))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    centre = hinge - turn @ Vector((0, L / 2, -H / 2))
    pod = _frame(centre, rot)
    tsteel.cyl(.1, 2.2, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)               # elevation hinge
    for s in (-1, 1):
        tarm.box((.18, .6, .42), loc=(s * 1.0, 1.85, .45), bevel=.03, seg=1)             # hinge cheeks
        tsteel.limb((s * .7, -.78, .3), tuple(pod @ Vector((s * .7, -1.2, -H / 2 + .02))), .14, .14, bevel=.02,
                    seg=1)
    a.part('Launcher', 'Team', t).box((W, L, H), loc=centre, rot=rot, bevel=.05)
    shroud = a.part('Launcher_armor', 'Armor', t)
    for s in (-1, 1):
        # Side armour running past the face into a hood around the tube mouths.
        shroud.box((.08, L + D - .15, H + .1), loc=pod @ Vector((s * (W / 2 + .035), (-D - .15) / 2, 0)), rot=rot,
                   bevel=.02, seg=1)
        shroud.box((W + .1, D + .28, .08), loc=pod @ Vector((0, -L / 2 + (.3 - D + .02) / 2, s * (H / 2 + .035))),
                   rot=rot, bevel=.02, seg=1)                                             # top and bottom lips
        tsteel.bolts([pod @ Vector((s * (W / 2 + .085), y, H / 2 - .12)) for y in (-1.9, -1.0, -.1, .8, 1.7)],
                     r=.04, h=.04, rot=ACROSS, bevel=0)
    for y in (-.95, .4, 1.75):                                                           # top ribs
        shroud.box((W + .04, .16, .07), loc=pod @ Vector((0, y, H / 2 + .03)), rot=rot, bevel=.015, seg=1)
    shroud.box((W - .12, .07, H - .12), loc=pod @ Vector((0, L / 2 + .03, 0)), rot=rot, bevel=.02, seg=1)
    # Fire-control sight on the front right of the launcher.
    shroud.box((.42, .5, .28), loc=pod @ Vector((W / 2 - .36, -L / 2 + .6, H / 2 + .145)), rot=rot, bevel=.04)
    a.part('Sight', 'Glass', t).box((.3, .04, .14), loc=pod @ Vector((W / 2 - .36, -L / 2 + .34, H / 2 + .15)),
                                    rot=rot, bevel=.01, seg=1)
    # 24 open tube mouths over a dark face plate inside the hood.
    a.part('Launcher_face', 'Undercarriage', t).box((W - .06, .02, H - .06), loc=pod @ Vector((0, -L / 2 - .015, 0)),
                                                    rot=rot, bevel=0)
    for row in (-.3, 0, .3):
        for col in (-1.015, -.725, -.435, -.145, .145, .435, .725, 1.015):
            _ring_mouth(a, t, pod @ _frame((col, -L / 2, row), FORWARD), .105, protrude=.06, seg=8)
    face = tuple(pod @ Vector((0, -L / 2 - .06, 0)))
    a.pivot('Muzzle_rocket', face, t)
    a.pivot('Muzzle_main', face, t)
    # Second weapon: a heavy machine gun on a tall pintle at the right rear corner of the hull deck (Mount_mg
    # / Muzzle_mg), outside the launcher's sweep and above the unditching log; its 0.7 m barrel stops
    # short of the launcher's back plate.
    wpn.hmg(a, (1.47, 3.22, 1.45), post=.45, length=.7, ammo=-1)


# ----------------------------------------------------------------------------- infantry fighting vehicle
def ifv(a):
    """Tracked infantry fighting vehicle (Bradley / BMP-3 lineage): a tall boxy hull with spaced
    side armour and skirts, a rear ramp with a troop door and roof vision blocks, and a small turret
    with a 30 mm autocannon, a coaxial gun and a twin ATGM box on its left side."""
    tracks(a, 1.22, 5.6, .78, .27, 6, .43, belt_width=.52, wheel_seg=10, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.85, .48), (-3.1, 1.0), (3.15, 1.0), (3.15, .48)], 1.84, bevel=.05)       # belly
    nose, brow = (-3.25, 1.1), (-1.95, 1.85)
    hull.prism([(-3.08, .91), nose, brow, (3.2, 1.85), (3.25, 1.78), (3.25, .91)], 2.96, bevel=.06)
    ys = _skirts(armor, 1.53, -2.95, 2.95, .5, 1.1, 3, thick=.06)
    for s in (-1, 1):
        for y in (-1.25, .45, 2.15):                                                      # spaced side armour
            hull.box((.05, 1.6, .6), loc=(s * 1.5, y, 1.47), bevel=.015, seg=1)
            steel.bolts([(s * 1.53, y + dy, 1.67) for dy in (-.65, .65)], r=.03, h=.03, rot=ACROSS, bevel=0)
        gy, gz, grot = _glacis(nose, brow, .1, .03)
        a.part('Lamps', 'Lamp').box((.22, .1, .06), loc=(s * 1.1, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
        steel.box((.14, .2, .12), loc=(s * .6, -3.02, .82), bevel=.02, seg=1)                  # tow hooks
        a.part('Tail_lights', 'Alloy').box((.14, .05, .1), loc=(s * 1.3, 3.265, 1.66), bevel=.01, seg=1)
        armor.box((.4, .36, .5), loc=(s * 1.24, 3.4, 1.3), bevel=.03, seg=1)                   # rear stowage boxes
    # Driver's hatch and vision blocks front left, engine grille front right.
    armor.cyl(.26, .06, loc=(-.72, -1.55, 1.87), seg=14, bevel=.02, bseg=1)
    glass = a.part('Vision_blocks', 'Glass')
    gy, gz, grot = _glacis(nose, brow, .9, .015)
    for dx in (-.2, 0, .2):
        glass.box((.13, .07, .05), loc=(-.72 + dx, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    deck.grille(.9, .8, loc=(.66, -1.45, 1.86), rot=(-R90, 0, 0), slats=6, depth=.07, thickness=.04)
    deck.grille(.5, .26, loc=(1.49, -2.0, 1.52), rot=(0, 0, R90), slats=3, depth=.05, thickness=.04)  # exhaust
    # Troop compartment roof: cargo hatch and a row of vision blocks along each edge.
    armor.box((1.5, 1.1, .06), loc=(0, 2.2, 1.86), bevel=.015, seg=1)
    steel.box((.06, .9, .05), loc=(.3, 2.2, 1.9), bevel=0)
    for s in (-1, 1):
        for y in (1.2, 2.2):
            glass.box((.08, .2, .09), loc=(s * 1.4, y, 1.87), bevel=.01, seg=1)
    # Rear ramp with the troop door, hinges and handle.
    armor.box((1.9, .08, 1.18), loc=(0, 3.3, 1.13), bevel=.02, seg=1)
    armor.box((.6, .05, .92), loc=(-.42, 3.355, 1.12), bevel=.015, seg=1)
    steel.box((.05, .05, .24), loc=(-.2, 3.39, 1.14), bevel=.01, seg=1)
    for x in (-.7, .7):
        steel.cyl(.05, .3, loc=(x, 3.33, .56), rot=ACROSS, seg=8, bevel=0)
    steel.cyl(.86, .1, loc=(0, -.25, 1.875), seg=20, bevel=.02, bseg=1)                   # turret ring

    t = a.pivot('Turret', (0, -.25, 1.93))
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.6, -.92), (.6, -.92), (.84, -.48), (.84, .72), (.68, .92), (-.68, .92), (-.84, .72), (-.84, -.48)]
    turret.prism(outline, .54, loc=(0, 0, .27), axis='Z', bevel=.05, taper=.86)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm.box((.46, .32, .34), loc=(0, -.98, .27), bevel=.035, taper=(.92, .9))            # mantlet
    tarm.box((1.1, .3, .3), loc=(0, .98, .22), bevel=.03, taper=(.95, .9))                # bustle
    basket = a.part('Basket', 'Steel', t)
    basket.shell(chamfered(1.3, .42, .05), .26, .035, loc=(0, 1.3, .12), floor=.03, bevel=.01)
    a.part('Tarp', 'Canvas', t).box((1.1, .3, .22), loc=(0, 1.3, .25), bevel=.08)
    for s in (-1, 1):
        _smoke(a, tsteel, .6, -.62, .42, s, count=3, gap=.065, r=.042, depth=.14)
    # Sights: gunner's box front left, the commander's independent viewer on a post at the back.
    tsteel.box((.24, .24, .16), loc=(-.34, -.42, .6), bevel=.03)
    sight = a.part('Sight', 'Glass', t)
    sight.box((.18, .04, .09), loc=(-.34, -.55, .6), bevel=.01, seg=1)
    tsteel.cyl(.07, .1, loc=(.42, .42, .58), seg=8, bevel=0)
    tsteel.box((.26, .28, .17), loc=(.42, .42, .69), bevel=.04)
    sight.box((.18, .04, .1), loc=(.42, .27, .7), bevel=.01, seg=1)
    a.part('Hatch', 'Armor', t).cyl(.24, .05, loc=(.1, .1, .555), seg=12, bevel=.015, bseg=1)
    _antenna(a, t, -.56, .72, .5, 1.1)
    # Twin ATGM box on an arm off the left side.
    tsteel.box((.34, .3, .14), loc=(-.9, .05, .3), bevel=.02, seg=1)
    launcher = a.part('Launcher', 'Armor', t)
    launcher.box((.34, 1.05, .52), loc=(-1.12, .05, .42), bevel=.04)
    for z in (.3, .54):
        _tube_mouth(a, t, _frame((-1.12, -.475, z), FORWARD), .09, protrude=.05, seg=10)
    a.pivot('Muzzle_missile', (-1.12, -.535, .42), t)
    tip = _gun(a, t, 0, -1.05, .28, 2.25, .045, seg=10, sleeves=((.06, .34, .075), (.5, .08, .06)),
               brake=(.2, .065, 1))
    a.pivot('Muzzle_main', tip, t)
    _coax(a, t, .32, -.86, .3, length=.3, housing=.26)


# ----------------------------------------------------------------------------- gun-missile air defence
def _twin_autocannon(a, parent, x, y, z, length, pitch, suffix):
    """Double-barrelled 30 mm cannon (2A38 style) from (x, y, z) forwards: two barrels side by side
    with cooling sleeves (Main_cannon<suffix>) and flash hiders (Muzzle_brake<suffix>). Returns the
    centre between the two openings."""
    rot = (R90 - pitch, 0, 0)
    at = _axis((x, y, z), pitch)
    cannon = a.part(f'Main_cannon{suffix}', 'Steel', parent)
    # Each barrel's hider is its own barrel tip (Muzzle_brake, _2 on the other gun, _3 and _4 beside them),
    # so the four barrels fire in turn from their own openings (VehicleView's barrel tips; DECISIONS 13F).
    outer = {'': '', '_2': '_2'}.get(suffix, suffix)
    inner = {'': '_3', '_2': '_4'}.get(suffix, suffix)
    cannon.box((.26, .5, .18), loc=at(.1), rot=(-pitch, 0, 0), bevel=0)                      # breech block
    for side in (-.065, .065):
        brake = a.part(f'Muzzle_brake{outer if side < 0 else inner}', 'Undercarriage', parent)
        cannon.cyl(.04, length, loc=at(length / 2, 0, side), rot=rot, seg=10, bevel=.01, bseg=1)
        cannon.cyl(.058, .5, loc=at(.55, 0, side), rot=rot, seg=10, bevel=.012, bseg=1)       # cooling sleeve
        brake.lathe([(.036, 0), (.056, .02), (.056, .16), (.03, .16), (.03, .1)], loc=at(length - .02, 0, side),
                    rot=rot, seg=8)
    return tuple(at(length + .14))


def heavy_aa(a):
    """8x8 gun-missile air-defence truck (Pantsir lineage): a cab-over truck with an equipment
    module and a combat turret on the rear bed carrying twin double-barrelled 30 mm cannons under
    two six-round missile packs, a tracking dish on the roof front and a search radar on a mast."""
    for y in (-2.85, -1.5, 1.35, 2.7):
        for s in (-1, 1):
            _wheel(a, s * 1.12, y, .56, .44)
    cab = a.part('Cab', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        dark.box((.22, 7.4, .3), loc=(s * .52, -.25, .82), bevel=.03, seg=1)                # frame rails
    for y in (-2.85, -1.5, 1.35, 2.7):
        dark.box((1.84, .2, .16), loc=(0, y, .56), bevel=.02, seg=1)                        # axles
    dark.box((1.5, 1.4, .55), loc=(0, -3.2, 1.0), bevel=.05)                                # engine
    # Cab over the front axle: sloped windscreen, side windows, grille, bumper, lamps and mirrors.
    front, top = (-4.02, 1.95), (-3.84, 2.72)
    cab.prism([(-3.92, 1.24), front, top, (-2.35, 2.78), (-2.3, 1.24)], 2.5, bevel=.07)
    glass = a.part('Windows', 'Glass')
    wy, wz, wrot = _glacis(front, top, .5, .012)
    for s in (-1, 1):
        glass.box((1.02, .62, .04), loc=(s * .56, wy, wz), rot=(wrot, 0, 0), bevel=.01, seg=1)
        glass.box((.04, .72, .42), loc=(s * 1.255, -3.25, 2.3), bevel=.01, seg=1)
        a.part('Lamps', 'Lamp').box((.28, .06, .14), loc=(s * .88, -3.975, 1.45), bevel=.01, seg=1)
        steel.box((.06, .12, .32), loc=(s * 1.42, -3.72, 2.25), bevel=.01, seg=1)             # mirrors
        steel.box((.2, .05, .05), loc=(s * 1.33, -3.72, 2.32), bevel=0)
        armor.box((.52, 2.62, .06), loc=(s * 1.12, -2.18, 1.22), bevel=.02, seg=1)          # front mudguards
        armor.box((.52, 2.6, .06), loc=(s * 1.12, 2.02, 1.24), bevel=.02, seg=1)            # rear mudguards
        a.part('Mud_flaps', 'Rubber').box((.46, .04, .44), loc=(s * 1.12, 3.33, 1.0), bevel=0)
        a.part('Tail_lights', 'Alloy').box((.16, .06, .1), loc=(s * 1.05, 3.97, 1.32), bevel=.01, seg=1)
        # Fuel tank and a stowage locker slung between the axles.
        steel.cyl(.24, 1.2, loc=(s * .84, -.1, .9), rot=FORWARD, seg=12, bevel=.04, bseg=1)
        # Stabiliser jacks at the rear corners, pads stowed above the ground.
        armor.box((.26, .26, .5), loc=(s * .95, 3.6, 1.02), bevel=.03, seg=1)
        steel.cyl(.07, .6, loc=(s * .95, 3.6, .55), seg=10, bevel=0)
        steel.cyl(.2, .07, loc=(s * .95, 3.6, .25), seg=12, bevel=.02, bseg=1)
    dark.grille(1.3, .42, loc=(0, -3.965, 1.6), rot=(-.14, 0, 0), slats=4, depth=.06, thickness=.04)
    steel.box((2.5, .22, .24), loc=(0, -4.02, 1.05), bevel=.04)                             # bumper
    for x in (-.45, 0, .45):
        a.part('Roof_lights', 'Alloy').box((.14, .08, .06), loc=(x, -3.7, 2.77), bevel=.01, seg=1)
    armor.cyl(.25, .06, loc=(.5, -3.0, 2.78), seg=12, bevel=.02, bseg=1)                  # cab hatch
    # Equipment module behind the cab: vents, a side door, a cooling unit and a ladder.
    cab.box((2.5, 1.6, .75), loc=(0, -1.45, 1.62), bevel=.05)
    for s in (-1, 1):
        dark.grille(.9, .4, loc=(s * 1.265, -1.6, 1.7), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.04)
    armor.box((1.2, .9, .1), loc=(0, -1.45, 2.04), bevel=.03, seg=1)              # low under the gun sweep
    dark.grille(.9, .6, loc=(0, -1.45, 2.095), rot=(-R90, 0, 0), slats=4, depth=.06, thickness=.04)
    steel.tube([(-1.29, -.75, .95), (-1.29, -.75, 2.0)], .025, seg=6)
    steel.tube([(-1.29, -1.05, .95), (-1.29, -1.05, 2.0)], .025, seg=6)
    for z in (1.15, 1.4, 1.65, 1.9):
        steel.box((.03, .262, .04), loc=(-1.29, -.9, z), bevel=0)                               # ladder rungs
    steel.cyl(.07, 1.3, loc=(.95, -2.15, 2.05), seg=8, bevel=0)                             # exhaust stack
    steel.cyl(.1, .16, loc=(.95, -2.15, 2.72), seg=8, bevel=0)
    armor.box((2.5, 4.3, .22), loc=(0, 1.8, 1.37), bevel=.04)                              # turret bed
    steel.box((2.46, .16, .2), loc=(0, 4.0, 1.2), bevel=.03)                               # rear bumper

    t = a.pivot('Turret', (0, 1.75, 1.48))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.05, .1, loc=(0, 0, .06), seg=20, bevel=.02, bseg=1)                      # turntable
    tarm.box((1.8, 2.1, .3), loc=(0, .05, .25), bevel=.04, seg=1)                          # base
    body = a.part('Turret_body', 'Team', t)
    outline = [(-.6, -1.0), (.6, -1.0), (.74, -.75), (.74, 1.0), (.6, 1.12), (-.6, 1.12), (-.74, 1.0), (-.74, -.75)]
    body.prism(outline, 1.0, loc=(0, 0, .88), axis='Z', bevel=.05, taper=.93)
    top = 1.38
    tarm.box((1.2, .4, .6), loc=(0, 1.2, .8), bevel=.04, seg=1, taper=(.95, .9))            # rear equipment
    # Electro-optical tracker on the front face.
    tarm.box((.42, .3, .34), loc=(0, -1.05, .95), bevel=.04, seg=1)
    a.part('Sight', 'Glass', t).box((.26, .04, .16), loc=(0, -1.2, .97), bevel=.01, seg=1)
    tips = []
    pitch = .05
    L, H, W = 2.3, .52, .74
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .98
        tarm.box((.34, 1.5, .42), loc=(x, -.25, .7), bevel=.04, seg=1)                     # gun housings
        tsteel.box((.26, .5, .2), loc=(s * .78, -.1, .7), bevel=.02, seg=1)                 # trunnions
        tips.append(_twin_autocannon(a, t, x, -.95, .7, 2.3, pitch, suffix))
        # Six-round missile pack hinged on the housing, level with the guns at rest. Its box is Pack_box; a
        # liner inside the top middle tube is Missile_pack, the launcher each side fires from (DECISIONS 13F).
        mp = 0.0
        hinge = Vector((x, .45, .93))
        rot = (-mp, 0, 0)
        turn = Euler(rot, 'XYZ').to_matrix()
        centre = hinge - turn @ Vector((0, L / 2, -H / 2))
        pack = _frame(centre, rot)
        a.part('Pack_box', 'Team', t).box((W, L, H), loc=centre, rot=rot, bevel=.04)
        a.part('Missile_pack', 'Undercarriage', t).cyl(.06, L - .2, loc=pack @ Vector((0, -.1, .12)), rot=FORWARD, seg=8,
                                                       bevel=0)
        frame = a.part('Pack_frame', 'Armor', t)
        for y in (-L / 2 + .12, L / 2 - .12):
            frame.box((W + .05, .14, H + .05), loc=pack @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
        tsteel.limb((x, -.85, .9), tuple(pack @ Vector((0, -.6, -H / 2 + .02))), .1, .1, bevel=.02)  # ram
        a.part('Pack_face', 'Undercarriage', t).box((W - .06, .02, H - .06), loc=pack @ Vector((0, -L / 2 - .015, 0)),
                                                    rot=rot, bevel=0)
        for cz in (-.12, .12):
            for cx in (-.23, 0, .23):
                _ring_mouth(a, t, pack @ _frame((cx, -L / 2, cz), FORWARD), .085, protrude=.05, seg=8, name='Pack_tubes')
        if s < 0:
            a.pivot('Muzzle_missile', tuple(pack @ Vector((0, -L / 2 - .06, 0))), t)
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    # Tracking radar dish on the roof front; it spins on its own pivot.
    tsteel.cyl(.16, .1, loc=(0, -.55, top), seg=12, bevel=.02, bseg=1)
    r = a.pivot('Radar', (0, -.55, top + .05), t)
    rm = a.part('Radar_mast', 'Steel', r)
    rm.cyl(.08, .22, loc=(0, 0, .11), seg=8, bevel=0)
    rm.box((.12, .2, .16), loc=(0, .02, .3), bevel=.02, seg=1)                             # yoke
    rm.limb((0, -.12, .34), (0, -.44, .34), .03, .03, bevel=0)                               # feed horn
    _dish(a.part('Radar_dish', 'Armor', r), (0, -.06, .34), .34, .34, depth=.13, seg=12, tilt=.2)
    # Search radar on a mast at the back of the roof, spinning on its own pivot.
    tsteel.cyl(.1, .13, loc=(0, .78, top + .055), seg=10, bevel=0)
    rs = a.pivot('Radar_search', (0, .78, top + .11), t)
    sm = a.part('Search_mount', 'Steel', rs)
    sm.cyl(.13, .1, loc=(0, 0, .05), seg=12, bevel=.02, bseg=1)
    sm.box((.16, .14, .26), loc=(0, .06, .2), bevel=.02, seg=1)
    srot = (-.3, 0, 0)
    face = _frame((0, -.02, .34), srot)
    a.part('Search_panel', 'Team', rs).box((1.5, .12, .44), loc=face.to_translation(), rot=srot, bevel=.03)
    a.part('Search_array', 'Armor', rs).box((1.4, .04, .36), loc=face @ Vector((0, -.07, 0)), rot=srot, bevel=.01,
                                           seg=1)
    for z in (-.09, .09):
        sm.box((1.34, .03, .03), loc=face @ Vector((0, -.095, z)), rot=srot, bevel=0)
    _antenna(a, t, .55, 1.0, top - .05, 1.0)


# ----------------------------------------------------------------------------- titan (premium)
def titan_tank(a):
    """Premium super tank: eight road wheels under a wide angular sponson hull with reactive
    armour, an arrowhead turret with a twin 140 mm gun, turret-side ATGM pods, active-protection
    launchers and radar tiles, a remote weapon station and sparing gilded trims."""
    tracks(a, 1.56, 7.9, 1.05, .35, 8, .57, belt_width=.72, wheel_seg=9, lean=True)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    era = a.part('ERA', 'Armor')
    gilt = a.part('Gilt', 'Gilded')
    full = (.62, 1.185, 1.9, 1.15, 1.98, 1.52)
    hull.loft([
        _sponson_section(-4.42, .98, 1.185, 1.34, 1.0, 1.84, 1.3),
        _sponson_section(-2.95, *full),
        _sponson_section(4.05, *full),
        _sponson_section(4.42, .72, 1.185, 1.72, 1.08, 1.9, 1.42),
    ], bevel=.05, seg=2)
    front, back = (-4.42, 1.34), (-2.95, 1.9)
    for row, u in enumerate((.2, .5, .8)):                                                  # glacis ERA
        gy, gz, grot = _glacis(front, back, u, .05)
        for x in ((-.99, -.33, .33, .99) if row < 2 else (-.66, 0, .66)):
            era.box((.6, .42, .1), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
    x, z, lean = _flank((1.98, 1.265), (1.52, 1.9), .5, .025)
    ys = _skirts(hull, 2.0, -3.95, 3.95, .52, 1.34, 4, thick=.1, gap=.04, bevel=.03)
    for s in (-1, 1):
        for y in (-2.4, 2.6):                                                              # flank plates
            armor.box((.06, 1.2, .5), loc=(s * x, y, z), rot=(0, -s * lean, 0), bevel=.015, seg=1)
        for y in (ys[0] - .38, ys[0] + .38, ys[1] - .38, ys[1] + .38):                    # skirt ERA
            for zz in (.78, 1.1):
                era.box((.06, .7, .28), loc=(s * 2.075, y, zz), bevel=.015, seg=1)
        steel.bolts([(s * 2.055, y + dy, .62) for y in ys[2:] for dy in (-.5, .5)], r=.035, h=.03, rot=ACROSS,
                    bevel=0)
        a.part('Lamps', 'Lamp').box((.26, .05, .1), loc=(s * 1.3, -4.435, 1.2), bevel=.01, seg=1)
        steel.box((.16, .22, .16), loc=(s * .7, -4.25, .9), bevel=.02, seg=1)                 # tow hooks
        a.part('Tail_lights', 'Alloy').box((.16, .05, .1), loc=(s * 1.45, 4.435, 1.5), bevel=.01, seg=1)
        steel.cyl(.11, .3, loc=(s * .75, 4.5, 1.45), rot=FORWARD, seg=10, bevel=0)  # exhausts
        deck.grille(1.2, 1.0, loc=(s * .72, 3.35, 1.91), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
        # Gilded crest on each skirt: a chevron on the middle panel.
        gilt.prism([(ys[2] - .34, 1.0), (ys[2], 1.2), (ys[2] + .34, 1.0), (ys[2] + .34, .9), (ys[2], 1.1),
                    (ys[2] - .34, .9)], .02, loc=(s * 2.06, 0, 0), bevel=0)
    armor.cyl(.3, .06, loc=(0, -2.62, 1.91), seg=14, bevel=.02, bseg=1)                    # driver's hatch
    gy, gz, grot = _glacis(front, back, .96, .012)
    a.part('Vision_blocks', 'Glass').box((.6, .07, .05), loc=(0, gy, gz), rot=(grot, 0, 0), bevel=.01, seg=1)
    steel.cyl(1.35, .1, loc=(0, .45, 1.905), seg=16, bevel=.02, bseg=1)                   # turret ring

    t = a.pivot('Turret', (0, .45, 1.96))
    H = .82
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-.72, -1.7), (.72, -1.7), (1.56, -.95), (1.6, 1.25), (1.45, 1.6), (-1.45, 1.6), (-1.6, 1.25),
               (-1.56, -.95)]
    turret.prism(outline, H, loc=(0, 0, H / 2), axis='Z', bevel=.06, taper=.88)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    tgilt = a.part('Turret_gilt', 'Gilded', t)
    for s in (-1, 1):                                                                       # arrowhead cheeks
        tarm.prism([(s * .62, -1.55), (s * 1.6, -.85), (s * 1.6, -1.25), (s * .68, -2.4)], .74, loc=(0, 0, .41),
                   axis='Z', bevel=.04, taper=.9)
        # Gilded trim along the top of each cheek's leading edge.
        p0, p1 = Vector((s * .68 * .9, -2.4 * .9, .78)), Vector((s * 1.6 * .9, -1.25 * .9, .78))
        tgilt.limb(tuple(p0 + Vector((0, .05, 0))), tuple(p1 + Vector((0, .05, 0))), .06, .03, bevel=0)
    tarm.box((1.1, .7, .6), loc=(0, -1.9, .42), bevel=.05, shift=(0, .06))                 # mantlet
    tarm.box((2.7, .9, .64), loc=(0, 1.9, .36), bevel=.05, taper=(.94, .9))                 # bustle
    basket = a.part('Basket', 'Steel', t)
    basket.shell(chamfered(2.5, .5, .06), .3, .04, loc=(0, 2.55, .16), floor=.03, bevel=.01)
    a.part('Tarp', 'Canvas', t).box((2.1, .36, .26), loc=(0, 2.55, .31), bevel=.09, seg=1)
    # Twin gun with gilded bands near the muzzles, coaxial gun between the barrels.
    tips = []
    for x, suffix in ((-.34, ''), (.34, '_2')):
        tips.append(_gun(a, t, x, -2.05, .44, 4.5, .12, suffix=suffix, seg=12, sleeves=((.2, .5, .16),),
                         extractor=(.55, .6, .172), brake=(.5, .2, 1)))
        at = _axis((x, -2.05, .44), 0.0)
        a.part(f'Main_cannon{suffix}_gilt', 'Gilded', t).cyl(.134, .08, loc=at(4.5 * .9), rot=FORWARD, seg=14,
                                                               bevel=0)
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    _coax(a, t, 0, -2.24, .2, length=.4, housing=.26)
    # Roof: commander's panoramic sight, gunner's sight, hatches and a gilded chevron.
    tsteel.cyl(.16, .24, loc=(-.72, -.2, H + .1), seg=12, bevel=.02, bseg=1)
    tsteel.box((.34, .34, .22), loc=(-.72, -.2, H + .31), bevel=.04, seg=1)
    sight = a.part('Sight', 'Glass', t)
    sight.box((.24, .04, .11), loc=(-.72, -.38, H + .32), bevel=.01, seg=1)
    tsteel.box((.4, .36, .26), loc=(.55, -1.0, H + .1), bevel=.04, seg=1)
    sight.box((.28, .04, .12), loc=(.55, -1.19, H + .12), bevel=.01, seg=1)
    hatch = a.part('Hatch', 'Armor', t)
    hatch.cyl(.28, .06, loc=(-.72, .55, H + .02), seg=14, bevel=.02, bseg=1)
    tgilt.prism([(-.36, -.95), (0, -1.2), (.36, -.95), (.36, -.83), (0, -1.08), (-.36, -.83)], .02,
                loc=(0, 0, H + .005), axis='Z', bevel=0)
    _rws(a, t, (.8, .5, H), length=.95)
    a.part('RWS', 'Armor', 'Mount_mg').box((.06, .26, .16), loc=(.21, .14, .25), bevel=0)  # ammo box bracket
    # Turret-side ATGM pods on arms.
    for s in (-1, 1):
        tsteel.box((.3, .34, .16), loc=(s * 1.72, -.3, .5), bevel=.02, seg=1)
        a.part('ATGM_pod', 'Team', t).box((.38, 1.15, .46), loc=(s * 1.9, -.3, .62), bevel=.04, seg=1)
        a.part('Pod_bands', 'Armor', t).box((.41, .12, .49), loc=(s * 1.9, .12, .62), bevel=.015, seg=1)
        for zz in (.51, .73):
            _tube_mouth(a, t, _frame((s * 1.9, -.875, zz), FORWARD), .085, protrude=.05, seg=10)
    a.pivot('Muzzle_missile', (-1.9, -.935, .62), t)
    # Active protection: hard-kill launchers on the rear roof corners, radar tiles on each corner and
    # mortar-style interceptor tubes along the roof edges.
    aps = a.part('APS', 'Armor', t)
    for s in (-1, 1):
        aps.cyl(.13, .16, loc=(s * 1.18, 1.18, H + .07), seg=10, bevel=.02, bseg=1)
        aps.box((.26, .4, .24), loc=(s * 1.18, 1.14, H + .26), bevel=.04, seg=1)
        tsteel.cyl(.07, .12, loc=(s * 1.18, .92, H + .28), rot=FORWARD, seg=8, bevel=0)
        _smoke(a, tsteel, 1.16, -.62, H + .02, s, count=3, gap=.1, r=.06, depth=.2)
        for y, ang in ((-1.1, s * .9), (1.2, s * 2.3)):
            px, py = s * 1.28, y
            aps.box((.34, .1, .26), loc=(px, py, H + .12), rot=(0, 0, ang), bevel=.03, seg=1)
            ox, oy = math.sin(ang) * .055, -math.cos(ang) * .055
            sight.box((.26, .03, .18), loc=(px + ox, py + oy, H + .12), rot=(0, 0, ang), bevel=.008, seg=1)
    _antenna(a, t, -1.3, 1.95, .7, 1.4)
    _antenna(a, t, 1.3, 1.95, .7, 1.1)


# name: (builder, Asset options). Vehicles use tight contact AO like 3d_astra's units.
BUILDERS = {
    'thermobaric_launcher': (thermobaric_launcher, dict(ao_distance=.6, grime_height=.55)),
    'ifv': (ifv, dict(ao_distance=.55, grime_height=.5)),
    'heavy_aa': (heavy_aa, dict(ao_distance=.6, grime_height=.55)),
    'titan_tank': (titan_tank, dict(ao_distance=.65, grime_height=.6)),
}
