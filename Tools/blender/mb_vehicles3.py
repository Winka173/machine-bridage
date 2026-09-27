"""Machine Brigade ground vehicles, third roster: bigger, longer and longer-ranged machines, built with
frontier_kit and the mb_vehicles / mb_vehicles2 helpers.

  * twin_tank: twin-barrel medium-heavy tank; a wide low turret with two 105 mm guns side by side
    (`Main_cannon` / `Main_cannon_2`, `Muzzle_brake` / `Muzzle_brake_2`, one `Muzzle_main` centred
    between the tips), `Muzzle_coax` between the mantlets and a roof gun on `Mount_mg` (Turret).
  * siege_tank: now built in mb_artillery.py (203 mm self-propelled gun, 2S7 Pion lineage).
  * heavy_rocket_artillery: 8x8 300 mm multiple rocket launcher (Smerch lineage), split armoured cab,
    twelve tubes on `Turret` pitched up 15 degrees; `Mount_mg` on the cab roof (root).
  * ballistic_launcher: 8x8 tactical ballistic missile TEL (Iskander lineage), two missiles raised
    20 degrees on an erector on `Turret`; `Mount_mg` on the cab roof (root).
  * siege_mortar: tracked 240 mm self-propelled mortar (Tyulpan lineage), the mortar at the rear on
    `Turret` pitched up 60 degrees over the hull, a rear spade; `Mount_mg` cupola (root).
    These three have limited main-weapon ammunition and fall back on the machine gun, so theirs is the
    big shielded _heavy_mg rather than the tanks' pintle gun.
  * ballistic_missile and heavy_rocket: projectiles, origin at the centre, nose at -Y, a glowing Alloy
    motor at the tail.

Conventions are those of mb_vehicles.py: metres, +Z up, Blender -Y is the front, origin on the ground at
the footprint centre, turret parts authored relative to the `Turret` empty. Parts named Main_cannon* /
Muzzle_brake* directly under `Turret` recoil straight back, so the pitched mortar tube and the launchers
use other names. Each gun or launcher is the highest thing inside its sweep, so the `Turret` turns all
the way round without passing through the rest of the model; the `Mount_mg` guns have a clear circle
too. Touching parts overlap or stand at least 1 cm apart, never face to face (coplanar faces z-fight).
"""
import math

from mathutils import Euler, Matrix, Vector

from mb_vehicles import (ACROSS, FORWARD, R90, _antenna, _barrel, _basket, _cable, _coax, _era, _exhaust,
                         _face_frame, _frame, _glacis, _grille_frame, _hatch, _headlight, _periscopes, _pick, _rail,
                         _roof_mg, _shovel, _skirt, _smoke, _stowage_bin, _taillight, _track_links, _wheel,
                         tracks)
from mb_vehicles2 import _axis

TAU = math.tau
BACKWARD = (-R90, 0, 0)  # cylinder axis along +Y (towards the tail)


# ----------------------------------------------------------------------------- helpers
def _at(m, loc=(0, 0, 0), rot=(0, 0, 0)):
    """World (loc, rot) of a local placement inside the frame matrix m."""
    mm = m @ _frame(loc, rot)
    return tuple(mm.to_translation()), tuple(mm.to_euler('XYZ'))


def _basis(o, x, y, z):
    """Frame matrix from an origin and three axis vectors."""
    return Matrix(((x[0], y[0], z[0], o[0]), (x[1], y[1], z[1], o[1]), (x[2], y[2], z[2], o[2]), (0, 0, 0, 1)))


def _heavy_mg(a, parent, loc, length=1.1):
    """Heavy machine gun on its own `Mount_mg` yaw pivot, for the launchers that fall back on it once
    their main weapon is spent: a turntable and pintle, a big receiver, a long barrel with a muzzle
    brake, an ammunition box and a wide shield with angled wings, so it reads from the game camera.
    `Muzzle_mg` sits at the barrel tip; the barrel sweeps a circle `length` + 0.21 m in radius."""
    m = a.pivot('Mount_mg', loc, parent)
    mg = a.part('MG', 'Steel', m)
    mg.cyl(.2, .06, loc=(0, 0, .02), seg=12, bevel=.01, bseg=1)                               # turntable
    mg.cyl(.06, .22, loc=(0, 0, .14), seg=8, bevel=0)                                        # pintle
    mg.box((.18, .5, .18), loc=(0, .04, .32), bevel=.02, seg=1)                              # receiver
    mg.box((.06, .18, .1), loc=(0, .34, .26), rot=(.3, 0, 0), bevel=0)                       # spade grips
    front = .04 - .25
    mg.cyl(.036, length, loc=(0, front - length / 2 + .02, .34), rot=FORWARD, seg=8, bevel=0)
    mg.cyl(.052, .16, loc=(0, front - length + .08, .34), rot=FORWARD, seg=8, bevel=0)        # muzzle brake
    a.part('MG_ammo', 'Armor', m).box((.16, .28, .2), loc=(.18, .06, .3), bevel=.02, seg=1)
    shield = a.part('MG_shield', 'Armor', m)
    shield.box((.6, .05, .44), loc=(0, -.3, .38), rot=(-.12, 0, 0), bevel=.012, seg=1)
    for k in (-1, 1):
        shield.box((.3, .05, .4), loc=(k * .42, -.215, .37), rot=(-.12, 0, k * .6), bevel=.012, seg=1)
    a.pivot('Muzzle_mg', (0, front - length, .34), m)


def _grid_fin(frame_part, web_part, m, phi, y_te, r, r0, span, width, chord, wall=.03):
    """Grid fin on a body lying along local Y of m (nose at -Y): a rectangular frame standing out at
    angle phi around the axis (0 = +X, towards +Z), from radius r0 to r0 + span, `width` across and
    `chord` along the body with its trailing edge at y_te; a 3 x 3 lattice of thin webs and a root
    stub down to the body surface at radius r."""
    e = Vector((math.cos(phi), 0, math.sin(phi)))
    t = Vector((-math.sin(phi), 0, math.cos(phi)))
    ax = e.cross(t)                                   # -Y: the frame rises from the trailing edge forwards
    o = Vector((0, y_te, 0))
    f = m @ _basis(o, e, t, ax)
    w = width / 2
    loc, rot = tuple(f.to_translation()), tuple(f.to_euler('XYZ'))
    frame_part.shell([(r0, -w), (r0 + span, -w), (r0 + span, w), (r0, w)], chord, wall, loc=loc, rot=rot, bevel=0)
    inner = chord * .8
    for k in (-1, 1):  # webs: two radial, two across
        l, rr = _at(f, (r0 + span / 2, k * width / 6, chord / 2))
        web_part.box((span - wall, .014, inner), loc=l, rot=rr, bevel=0)
        l, rr = _at(f, (r0 + span / 2 + k * span / 6, 0, chord / 2))
        web_part.box((.014, width - wall, inner), loc=l, rot=rr, bevel=0)
    l, rr = _at(f, ((r + r0) / 2 - .0075, 0, chord * .45))
    frame_part.box((r0 - r + .045, .07, chord * .7), loc=l, rot=rr, bevel=0)


def _folded_fin(frame_part, web_part, m, phi, y_hinge, r_in, span, width, depth, wall=.03):
    """Grid fin folded forwards flat against a body lying along local Y of m: the frame hinges at
    y_hinge, runs `span` forwards, `width` across at angle phi around the axis, and stands `depth` out
    from radius r_in; the same 3 x 3 lattice as _grid_fin."""
    e = Vector((math.cos(phi), 0, math.sin(phi)))
    t = Vector((-math.sin(phi), 0, math.cos(phi)))
    f = m @ _basis(Vector((0, y_hinge, 0)) + e * r_in, Vector((0, 1, 0)), t, e)
    w = width / 2
    loc, rot = tuple(f.to_translation()), tuple(f.to_euler('XYZ'))
    frame_part.shell([(-span, -w), (0, -w), (0, w), (-span, w)], depth, wall, loc=loc, rot=rot, bevel=0)
    for k in (-1, 1):
        l, rr = _at(f, (-span / 2, k * width / 6, depth / 2))
        web_part.box((span - wall, .014, depth * .8), loc=l, rot=rr, bevel=0)
        l, rr = _at(f, (-span / 2 + k * span / 6, 0, depth / 2))
        web_part.box((.014, width - wall, depth * .8), loc=l, rot=rr, bevel=0)
    l, rr = _at(f, (.04, 0, depth * .22))
    frame_part.box((.1, .12, depth * .6), loc=l, rot=rr, bevel=0)                               # hinge block


def _ballistic(a, m, length=7.0, r=.45, parent=None, prefix='', seg=12, motor=True, folded=False):
    """Tactical ballistic missile (Iskander lineage) along local -Y of frame m, centred on its origin:
    a dark green body, a white ogive nose and tail skirt with a white band, four grid fins in an X at
    the tail and a steel nozzle round a glowing motor (on a launcher: motor=False and folded=True, the
    fins folded flat along the tail). Parts are named
    Body, Nose... or, with a prefix, Missile_body, Missile_nose... Returns the nose tip in m's frame."""
    h = length / 2

    def n(name):
        return prefix + name.lower() if prefix else name
    body = a.part(n('Body'), 'FoliageDark', parent)
    white = a.part(n('Nose'), 'Medical', parent)
    tail = a.part(n('Tail'), 'Medical', parent)
    loc, rot = _at(m, rot=FORWARD)                        # lathe axis (local Z) along -Y: z = +h is the nose
    body.lathe([(r, -h + 1.05), (r, h - 2.05)], loc=loc, rot=rot, seg=seg)
    white.lathe([(r * .985, h - 2.1), (r * .975, h - 1.8), (r * .9, h - 1.25), (r * .72, h - .72), (r * .4, h - .26),
                 (0, h)], loc=loc, rot=rot, seg=seg)
    tail.lathe([(r * .82, -h), (r * .985, -h + .45), (r * .985, -h + 1.04), (r * .88, -h + 1.04), (r * .88, -h + 1.12)],
               loc=loc, rot=rot, seg=seg)
    band = _at(m, (0, -h * .18, 0), FORWARD)
    a.part(n('Band'), 'Medical', parent).cyl(r + .012, .22, loc=band[0], rot=band[1], seg=seg, bevel=0)
    fins, webs = a.part(n('Grid_fins'), 'Armor', parent), a.part(n('Grid_webs'), 'Armor', parent)
    for k in range(4):
        if folded:  # stowed on a launcher: folded flat along the tail
            _folded_fin(fins, webs, m, math.pi / 4 + k * R90, h - .06, r * .93, r * .84, r * .9, .16)
        else:
            _grid_fin(fins, webs, m, math.pi / 4 + k * R90, h - .06, r * .9, r + .06, r * .84, r * .9, .2)
    # Hollow bell nozzle opening backwards (+Y) with the glowing motor 1 cm off its bottom.
    noz = _at(m, (0, h + .02, 0), BACKWARD)
    a.part(n('Nozzle'), 'Steel', parent).lathe([(r * .5, -.14), (r * .7, .1), (r * .6, .1), (r * .42, 0)],
                                               loc=noz[0], rot=noz[1], seg=8)
    if motor:
        glow = _at(m, (0, h + .04, 0), BACKWARD)
        a.part(n('Motor'), 'Alloy', parent).cyl(r * .38, .02, loc=glow[0], rot=glow[1], seg=8, bevel=0)
    return Vector((0, -h, 0))


# ----------------------------------------------------------------------------- twin tank
def twin_tank(a):
    """Twin-barrel medium-heavy tank: a low hull as wide as the tracks behind five-panel bolted skirts,
    reactive armour on the glacis and turret cheeks, and a wide low turret with two baffle-braked
    105 mm guns side by side, a coaxial gun between the mantlets, a roof machine gun on the commander's
    cupola, smoke dischargers, bins and a bustle rack."""
    tracks(a, 1.34, 6.3, .92, .3, 7, .5, belt_width=.64, wheel_seg=10, lean=True, sprocket=1)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-2.95, .56), (-3.2, 1.1), (3.1, 1.1), (3.1, .56)], 1.96, bevel=.05)       # belly between belts
    front, brow = (-3.38, 1.2), (-2.25, 1.52)
    hull.prism([(-3.25, 1.06), front, brow, (2.9, 1.52), (3.22, 1.3), (3.22, 1.06)], 3.3, bevel=.06)
    for s in (-1, 1):
        _skirt(a, s, 1.715, -3.0, 2.95, .56, 1.3, 5, thick=.1)
        steel.box((.16, .2, .14), loc=(s * .55, -3.1, .84), bevel=.02, seg=1)               # tow hooks
        steel.box((.16, .2, .14), loc=(s * .55, 3.14, .84), bevel=.02, seg=1)
        _exhaust(a, s * .55, 3.22, 1.18, .5, .14)
        _taillight(a, s * 1.3, 3.22, 1.18)
        # Armoured headlights at the front corners of the glacis.
        gy, gz, grot = _glacis(front, brow, .16, .04)
        armor.box((.34, .2, .16), loc=(s * 1.3, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
        ly, lz, _ = _glacis(front, brow, .07, .05)
        a.part('Lamps', 'Lamp').box((.22, .03, .09), loc=(s * 1.3, ly, lz), rot=(grot, 0, 0), bevel=0)
        # Rear deck: engine grilles in frames and two bins at the corners, low under the guns.
        deck.grille(1.0, .8, loc=(s * .62, 2.35, 1.53), rot=(-R90, 0, 0), slats=6, depth=.08, thickness=.04)
        _grille_frame(a, s * .62, 2.35, 1.51, 1.0, .8, t=.04)
        _stowage_bin(a, (s * 1.32, 2.85, 1.51), (.5, .5, .22), latch_side=0)
        # Tow cables along the deck edges.
        _cable(a, [(s * 1.55, -2.0, 1.545), (s * 1.55, .6, 1.545), (s * 1.53, 2.2, 1.545)])
    for row, u in enumerate((.3, .72)):                                                     # glacis ERA
        gy, gz, grot = _glacis(front, brow, u, .035)
        for x in ((-1.0, -.5, 0, .5, 1.0) if row else (-.95, -.32, .32, .95)):
            armor.box((.44, .38, .1), loc=(x, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
    _hatch(a, 0, -1.95, 1.51, .26)                                                           # driver's hatch
    _periscopes(a, [(dx, -2.3, 1.51, 0) for dx in (-.18, 0, .18)])
    _shovel(a, (-1.45, -1.2, 1.535), length=1.0)
    _pick(a, (1.45, -1.3, 1.54), length=.9)
    steel.cyl(1.3, .1, loc=(0, .2, 1.54), seg=24, bevel=.02, bseg=1)                         # turret ring

    t = a.pivot('Turret', (0, .2, 1.58))
    H = .62
    turret = a.part('Turret_body', 'Team', t)
    outline = [(-1.25, 1.4), (1.25, 1.4), (1.52, .85), (1.52, -.5), (1.08, -1.3), (-1.08, -1.3), (-1.52, -.5),
               (-1.52, .85)]
    turret.prism(outline, H, loc=(0, 0, H / 2), axis='Z', bevel=.06, taper=.88)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel = a.part('Turret_steel', 'Steel', t)
    for b0, b1 in (((1.08, -1.3), (1.52, -.5)), ((-1.52, -.5), (-1.08, -1.3))):             # cheek ERA
        _era(a, _face_frame(b0, b1, H, .88, u=.5, v=.45), 2, 2, (.28, .22, .09), parent=t, bevel=0)
    tips = []
    for s, suffix in ((-1, ''), (1, '_2')):
        x = s * .46
        tarm.box((.5, .46, .5), loc=(x, -1.36, .34), bevel=.05, seg=1, taper=(.92, .92))    # mantlets
        tips.append(_barrel(a, t, start_y=-1.5, length=3.3, radius=.078, height=.34, brake=(.24, .28, .22),
                            sleeve=(.42, .6, .115), x=x, suffix=suffix, seg=12, style='baffle', bands=(.2, .74)))
        _stowage_bin(a, (s * 1.48, .3, .1), (.18, .9, .36), parent=t, latch_side=s)          # side bins
        _smoke(a, tsteel, 1.18, -.62, .55, s, count=3, gap=.09, r=.05, depth=.16)
        _rail(a, [(s * 1.14, -.3, H - .02), (s * 1.14, -.3, H + .05), (s * 1.14, .55, H + .05),
                  (s * 1.14, .55, H - .02)], parent=t)
    a.pivot('Muzzle_main', (0, tips[0][1], tips[0][2]), t)
    _coax(a, t, 0, -1.25, .3, length=.4, housing=.3)
    # Bustle and its stowage rack.
    tarm.box((2.3, .5, .48), loc=(0, 1.52, .3), bevel=.05, seg=1, taper=(.95, .9))
    _basket(a, -1.05, 1.05, 1.78, 2.14, .06, .3, parent=t)
    # Roof: commander's cupola with the machine gun, gunner's sight, loader's hatch and antennas.
    tsteel.cyl(.3, .16, loc=(.72, .3, H + .04), seg=16, bevel=.03, bseg=1)
    a.part('Cupola_top', 'Armor', t).cyl(.26, .06, loc=(.72, .3, H + .14), seg=16, bevel=.015, bseg=1)
    glass = a.part('Periscope', 'Glass', t)
    for k in range(4):
        ang = k * TAU / 4 + .4
        glass.box((.1, .05, .07), loc=(.72 + math.cos(ang) * .3, .3 + math.sin(ang) * .3, H + .07),
                  rot=(0, 0, ang + R90), bevel=0)
    _roof_mg(a, t, (.72, .3, H + .165), length=.85)
    tarm.box((.36, .32, .26), loc=(-.62, -.55, H + .1), bevel=.04, seg=1)                   # gunner's sight
    a.part('Sight', 'Glass', t).box((.26, .04, .13), loc=(-.62, -.72, H + .12), bevel=.01, seg=1)
    _hatch(a, -.62, .4, H - .01, .25, parent=t)                                              # loader's hatch
    _periscopes(a, [(-.62, .06, H - .01, 0)], parent=t)
    a.part('Vents', 'Undercarriage', t).grille(.5, .3, loc=(0, .85, H + .005), rot=(-R90, 0, 0), slats=3, depth=.05,
                                               thickness=.035)
    tsteel.cyl(.02, .28, loc=(-.3, 1.0, H + .12), seg=5, bevel=0)                            # wind sensor
    tsteel.box((.08, .08, .1), loc=(-.3, 1.0, H + .3), bevel=0)
    for x, height in ((-.95, 1.2), (.95, .9)):                                                 # on the bustle
        tsteel.box((.09, .09, .06), loc=(x, 1.55, .54), bevel=0)
        _antenna(a, t, x, 1.55, .55, height)


# ----------------------------------------------------------------------------- siege tank
# siege_tank: the 203 mm self-propelled gun is built in mb_artillery.py.


# ----------------------------------------------------------------------------- wheeled launchers
def _jack(a, x, y, top, pad=.22):
    """Stabiliser jack at (x, y) hanging from `top`: an armoured housing, the ram and a pad stowed
    20 cm above the ground."""
    a.part('Jacks', 'Armor').box((.3, .3, .56), loc=(x, y, top - .27), bevel=.03, seg=1)
    bottom = top - .54
    a.part('Jack_rams', 'Steel').cyl(.075, bottom - .24, loc=(x, y, (bottom + .24) / 2), seg=10, bevel=0)
    a.part('Jack_pads', 'Steel').cyl(pad, .07, loc=(x, y, .235), seg=12, bevel=.02, bseg=1)


def heavy_rocket_artillery(a):
    """8x8 300 mm multiple rocket launcher (Smerch lineage): the split armoured cab of its heavy chassis
    (two cabs either side of the engine), an equipment module behind them, and twelve 300 mm tubes in
    a banded pack raised 15 degrees on a trainable launcher over the rear axles. Stabiliser jacks,
    side lockers, mudguards and a pintle machine gun on the left cab roof."""
    axles = (-3.35, -1.45, 2.0, 3.9)
    for y in axles:
        for s in (-1, 1):
            _wheel(a, s * 1.18, y, .62, .48, seg=14)
    cab = a.part('Cab', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    for s in (-1, 1):
        dark.box((.24, 11.4, .34), loc=(s * .5, .1, .95), bevel=.03, seg=1)                       # frame rails
    for y in axles:
        dark.box((1.9, .22, .18), loc=(0, y, .62), bevel=.02, seg=1)                             # axles
    dark.box((2.5, 1.95, .46), loc=(0, -4.95, 1.0), bevel=.04, seg=1)                            # front body
    # Split cab: two armoured cabs with the engine between them.
    front, top = (-6.0, 1.9), (-5.68, 2.78)
    for s in (-1, 1):
        x = s * .93
        cab.prism([(-5.95, 1.12), front, top, (-4.05, 2.84), (-3.95, 1.12)], 1.02, loc=(x, 0, 0), bevel=.06)
        wy, wz, wrot = _glacis(front, top, .45, .012)
        glass.box((.74, .5, .04), loc=(x, wy, wz), rot=(wrot, 0, 0), bevel=.01, seg=1)
        vy, vz, _ = _glacis(front, top, .9, .03)
        armor.box((.98, .14, .07), loc=(x, vy, vz), rot=(wrot, 0, 0), bevel=.015, seg=1)          # visor
        fy, fz, _ = _glacis(front, top, .45, .03)
        armor.box((.06, .56, .05), loc=(x, fy, fz), rot=(wrot, 0, 0), bevel=0)                    # pane bar
        ox = s * 1.44
        glass.box((.04, .5, .3), loc=(ox + s * .005, -4.95, 2.35), bevel=.01, seg=1)             # side window
        armor.box((.06, .62, .07), loc=(ox + s * .02, -4.95, 2.56), bevel=.01, seg=1)            # window shutter
        for y in (-5.62, -4.3):
            armor.box((.03, .04, 1.1), loc=(ox + s * .007, y, 1.82), bevel=0)                    # door lines
        steel.box((.04, .16, .05), loc=(ox + s * .02, -4.5, 1.95), bevel=0)                       # handle
        steel.box((.2, .3, .05), loc=(ox + s * .02, -4.95, .98), bevel=0)                         # step
        steel.tube([(ox, -5.7, 2.5), (ox + s * .06, -5.82, 2.52)], .018, seg=4)                   # mirror arm
        armor.box((.05, .16, .26), loc=(ox + s * .06, -5.86, 2.44), bevel=.01, seg=1)
        _headlight(a, s * 1.1, -5.97, 1.4, guard=False)
        steel.box((.16, .14, .14), loc=(s * .55, -6.22, .98), bevel=.02, seg=1)                  # tow hooks
        a.part('Marker_lights', 'Alloy').box((.1, .05, .05), loc=(x + s * .3, -5.66, 2.8), bevel=0)
        # Mudguards over each axle pair, mud flaps behind the rear wheels, side lockers between.
        armor.box((.6, 3.4, .06), loc=(s * 1.2, -2.4, 1.28), bevel=.015, seg=1)
        armor.box((.6, 3.3, .06), loc=(s * 1.2, 2.95, 1.28), bevel=.015, seg=1)
        a.part('Mud_flaps', 'Rubber').box((.48, .04, .42), loc=(s * 1.18, 4.66, 1.03), bevel=0)
        armor.box((.34, 1.9, .62), loc=(s * 1.18, .28, .99), bevel=.03, seg=1)
        for y in (-.2, .76):
            steel.box((.03, .06, .08), loc=(s * 1.36, y, 1.18), bevel=0)
        steel.cyl(.25, 1.4, loc=(s * .74, .28, .9), rot=FORWARD, seg=12, bevel=.04, bseg=1)       # fuel tanks
        # Stabiliser jacks behind the front bogie and at the rear.
        _jack(a, s * 1.18, -2.4, 1.36)
        _jack(a, s * 1.1, 5.55, 1.36)
        _taillight(a, s * 1.05, 5.9, 1.4)
    dark.box((.76, 1.95, .9), loc=(0, -4.95, 1.62), bevel=.03, seg=1)                            # engine
    cab.box((.8, 1.9, .1), loc=(0, -4.95, 2.1), bevel=.03, seg=1)                                # engine hood
    dark.grille(.64, .5, loc=(0, -5.94, 1.62), slats=4, depth=.05, thickness=.04)                 # radiator
    steel.box((2.9, .22, .24), loc=(0, -6.08, .98), bevel=.04)                                   # bumper
    armor.cyl(.08, .5, loc=(0, -6.22, .98), rot=ACROSS, seg=10, bevel=0)                          # winch drum
    # Left cab roof: the machine gun on a raised ring. Right cab: hatch and antenna.
    armor.cyl(.36, .12, loc=(-.93, -4.95, 2.85), seg=16, bevel=.02, bseg=1)
    _heavy_mg(a, None, (-.93, -4.95, 2.9))
    _hatch(a, .93, -4.85, 2.81, .26)
    _antenna(a, None, 1.25, -4.25, 2.83, 1.3)
    # Equipment module behind the cabs: vents, exhaust stack and a ladder.
    cab.box((2.7, 1.25, 1.0), loc=(0, -3.2, 1.77), bevel=.05)
    for s in (-1, 1):
        dark.grille(.7, .4, loc=(s * 1.365, -3.2, 1.9), rot=(0, 0, s * R90), slats=4, depth=.05, thickness=.04)
    armor.box((1.4, .7, .1), loc=(0, -3.2, 2.3), bevel=.03, seg=1)
    steel.cyl(.07, 1.2, loc=(1.2, -2.5, 1.95), seg=8, bevel=0)                                   # exhaust stack
    steel.cyl(.1, .16, loc=(1.2, -2.5, 2.58), seg=8, bevel=0)
    for z in (1.5, 2.2):
        steel.box((.06, .14, .06), loc=(1.2, -2.58, z), bevel=0)
    steel.tube([(-1.1, -2.55, 1.0), (-1.1, -2.55, 2.28)], .025, seg=6)                           # ladder
    steel.tube([(-.8, -2.55, 1.0), (-.8, -2.55, 2.28)], .025, seg=6)
    for z in (1.3, 1.6, 1.9, 2.2):
        steel.box((.32, .03, .04), loc=(-.95, -2.55, z), bevel=0)
    # Launcher bed with raised edges and tie-down rings; control boxes at its front.
    cab.box((2.7, 8.3, .22), loc=(0, 1.75, 1.4), bevel=.04)
    for s in (-1, 1):
        armor.box((.07, 8.2, .07), loc=(s * 1.31, 1.75, 1.525), bevel=0)
        for y0, y1 in ((-1.35, 1.25), (3.55, 5.75)):                                              # walkway plates
            armor.box((.5, y1 - y0, .04), loc=(s * .98, (y0 + y1) / 2, 1.52), bevel=0)
        for y in (-1.6, .4, 2.4, 4.4):
            steel.box((.04, .1, .06), loc=(s * 1.365, y, 1.42), bevel=0)
        _stowage_bin(a, (s * .8, -1.8, 1.5), (.8, .7, .34), latch_side=0)
    steel.box((2.6, .18, .2), loc=(0, 5.98, 1.12), bevel=.03)                                    # rear bumper

    t = a.pivot('Turret', (0, 2.4, 1.51))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.05, .12, loc=(0, 0, .05), seg=20, bevel=.02, bseg=1)                           # turntable
    tarm.box((1.7, 3.9, .3), loc=(0, 1.05, .27), bevel=.05, seg=1, taper=(.94, .97))              # launch frame
    L, H, W, R = 5.8, 1.29, 1.72, .2
    pitch = math.radians(15)
    hinge = Vector((0, 3.0, .6))
    rot = (-pitch, 0, 0)
    turn = Euler(rot, 'XYZ').to_matrix()
    centre = hinge - turn @ Vector((0, L / 2, -H / 2))
    pod = _frame(centre, rot)
    tsteel.cyl(.12, 2.1, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)                      # elevation hinge
    for s in (-1, 1):
        tarm.box((.16, .5, .55), loc=(s * .95, 3.0, .5), bevel=.02, seg=1)                        # hinge cheeks
        tsteel.limb((s * .55, -.55, .4), tuple(pod @ Vector((s * .55, -1.0, -H / 2 - .02))), .15, .15, bevel=.02,
                    seg=1)                                                                        # elevation rams
    tubes = a.part('Tubes', 'Team', t)
    bores = a.part('Tube_bores', 'Undercarriage', t)
    trot = (R90 - pitch, 0, 0)
    for row in (-.43, 0, .43):
        for col in (-.645, -.215, .215, .645):
            loc = pod @ Vector((col, 0, row))
            tubes.lathe([(R, -L / 2 + .05), (R, L / 2), (R * .78, L / 2), (R * .78, L / 2 - .2)], loc=loc, rot=trot,
                        seg=10)
            bores.cyl(R * .74, .02, loc=pod @ Vector((col, -L / 2 + .19, row)), rot=trot, seg=10, bevel=0)
    frame = a.part('Pack_frame', 'Armor', t)
    for y in (-L / 2 + .35, -.2, L / 2 - .3):                                                     # bands
        frame.box((W + .1, .16, H + .1), loc=pod @ Vector((0, y, 0)), rot=rot, bevel=.02, seg=1)
    tsteel.box((.34, L - .5, .14), loc=pod @ Vector((0, .1, -H / 2 - .09)), rot=rot, bevel=.02, seg=1)  # spine
    for s in (-1, 1):
        for z in (-.215, .215):                                                                   # side rails
            frame.box((.06, L - .8, .1), loc=pod @ Vector((s * (W / 2 + .03), .1, z)), rot=rot, bevel=0)
        for y in (-L / 2 + .35, L / 2 - .3):
            tsteel.box((.12, .12, .1), loc=pod @ Vector((s * .6, y, H / 2 + .09)), rot=rot, bevel=0)  # lugs
    a.part('Cable_box', 'Armor', t).box((.3, .6, .22), loc=pod @ Vector((W / 2 - .2, .9, H / 2 + .12)), rot=rot,
                                        bevel=.03, seg=1)
    a.pivot('Muzzle_main', tuple(pod @ Vector((0, -L / 2 - .02, 0))), t)


def ballistic_launcher(a):
    """8x8 tactical ballistic missile TEL (Iskander lineage): a wide four-door cab, a long armoured body
    whose roof doors hang folded down its sides, four stabiliser jacks and an equipment housing behind
    the cab. Two missiles lie raised 20 degrees on a trainable erector (beams, saddles and clamp
    straps on a hinged frame lifted by twin rams); a pintle machine gun rides the cab roof."""
    axles = (-4.35, -2.6, 1.9, 3.65)
    for y in axles:
        for s in (-1, 1):
            _wheel(a, s * 1.2, y, .64, .5, seg=14)
    cab = a.part('Cab', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    dark = a.part('Chassis', 'Undercarriage')
    glass = a.part('Windows', 'Glass')
    for s in (-1, 1):
        dark.box((.24, 11.8, .34), loc=(s * .52, 0, .98), bevel=.03, seg=1)                       # frame rails
    for y in axles:
        dark.box((1.94, .22, .18), loc=(0, y, .64), bevel=.02, seg=1)                            # axles
    # Wide cab over the front axle: split windscreen, four doors, grille, bumper and lamps.
    front, top = (-6.25, 2.08), (-6.02, 2.96)
    cab.prism([(-6.2, 1.36), front, top, (-3.9, 3.02), (-3.82, 1.36)], 2.98, bevel=.07)
    wy, wz, wrot = _glacis(front, top, .52, .012)
    for s in (-1, 1):
        glass.box((1.26, .64, .04), loc=(s * .68, wy, wz), rot=(wrot, 0, 0), bevel=.01, seg=1)
        ox = s * 1.49
        for y in (-5.55, -4.6):
            glass.box((.04, .6, .42), loc=(ox + s * .005, y, 2.45), bevel=.01, seg=1)             # side windows
        for y in (-6.02, -5.08, -4.1):
            armor.box((.03, .04, 1.4), loc=(ox + s * .007, y, 2.0), bevel=0)                     # door lines
        for y in (-5.25, -4.3):
            steel.box((.04, .16, .05), loc=(ox + s * .02, y, 2.1), bevel=0)                       # handles
        steel.box((.2, .8, .05), loc=(ox - s * .05, -5.55, 1.24), bevel=0)                        # steps
        steel.tube([(ox, -5.95, 2.72), (ox + s * .04, -6.08, 2.74)], .018, seg=4)                 # mirror arms
        armor.box((.05, .16, .3), loc=(ox + s * .04, -6.1, 2.62), bevel=.01, seg=1)
        a.part('Lamps', 'Lamp').box((.3, .06, .14), loc=(s * 1.05, -6.215, 1.62), bevel=.01, seg=1)
        a.part('Marker_lights', 'Alloy').box((.14, .08, .06), loc=(s * 1.1, -5.9, 3.0), bevel=.01, seg=1)
        steel.box((.16, .14, .14), loc=(s * .6, -6.36, 1.12), bevel=.02, seg=1)                  # tow hooks
        # Front mudguards, jacks, mud flaps and lockers on the chassis.
        armor.box((.58, 2.9, .06), loc=(s * 1.2, -3.5, 1.33), bevel=.015, seg=1)
        a.part('Mud_flaps', 'Rubber').box((.48, .04, .42), loc=(s * 1.2, 4.42, 1.06), bevel=0)
        _jack(a, s * 1.2, -1.4, 1.4)
        _jack(a, s * 1.1, 5.4, 1.4)
        armor.box((.34, 1.8, .6), loc=(s * 1.17, -.35, 1.05), bevel=.03, seg=1)                   # lockers
        steel.cyl(.25, 1.3, loc=(s * .74, .15, .95), rot=FORWARD, seg=12, bevel=.04, bseg=1)      # fuel tanks
    dark.grille(1.4, .4, loc=(0, -6.215, 1.8), slats=4, depth=.06, thickness=.04)
    steel.box((2.96, .22, .24), loc=(0, -6.3, 1.12), bevel=.04)                                   # bumper
    for x in (-.35, .35):
        a.part('Marker_lights', 'Alloy').box((.14, .08, .06), loc=(x, -5.9, 3.0), bevel=.01, seg=1)
    # Cab roof: the machine gun on a raised ring front left, a hatch, an air-conditioner and an antenna.
    armor.cyl(.36, .12, loc=(-.8, -5.1, 3.02), seg=16, bevel=.02, bseg=1)
    _heavy_mg(a, None, (-.8, -5.1, 3.07))
    _hatch(a, .75, -5.0, 3.0, .26)
    armor.box((.8, .6, .26), loc=(.7, -4.25, 3.12), bevel=.04, seg=1)
    dark.grille(.6, .4, loc=(.7, -4.25, 3.26), rot=(-R90, 0, 0), slats=3, depth=.05, thickness=.035)
    _antenna(a, None, 1.3, -3.95, 3.02, 1.3)
    # Armoured body: the roof doors hang folded down both sides, with hinges along the top edge.
    cab.box((2.94, 9.9, .7), loc=(0, 1.25, 1.71), bevel=.05)
    for s in (-1, 1):
        for y0, y1 in ((-3.45, -.4), (-.3, 2.75), (2.85, 5.95)):
            armor.box((.05, y1 - y0, .5), loc=(s * 1.485, (y0 + y1) / 2, 1.72), bevel=.012, seg=1)
            for y in (y0 + .3, (y0 + y1) / 2, y1 - .3):
                steel.box((.06, .14, .07), loc=(s * 1.5, y, 1.99), bevel=0)                       # hinges
            steel.box((.04, .2, .05), loc=(s * 1.515, (y0 + y1) / 2, 1.56), bevel=0)             # handle
        a.part('Tail_lights', 'Alloy').box((.16, .06, .1), loc=(s * 1.1, 6.21, 1.85), bevel=.01, seg=1)
        a.part('Lamps', 'Lamp').box((.12, .06, .1), loc=(s * .88, 6.21, 1.85), bevel=.01, seg=1)
    for s in (-1, 1):                                                                            # walkways
        armor.box((.34, 8.6, .04), loc=(s * 1.24, 1.4, 2.065), bevel=0)
        for y in (-2.9, -.4, 2.1, 4.6):
            steel.box((.1, .06, .05), loc=(s * 1.42, y, 2.07), bevel=0)                           # tie-downs
    for y in (-1.6, 4.5):                                                                          # roof hatches
        armor.box((1.2, .8, .04), loc=(0, y, 2.065), bevel=.01, seg=1)
    armor.box((.9, .06, .5), loc=(0, 6.21, 1.68), bevel=.015, seg=1)                             # rear door
    steel.box((.24, .05, .05), loc=(.25, 6.25, 1.7), bevel=0)
    steel.box((2.6, .18, .2), loc=(0, 6.26, 1.28), bevel=.03)                                     # rear bumper
    # Equipment housing on the front of the body, outside the erector's sweep.
    cab.box((2.5, .9, .5), loc=(0, -3.2, 2.28), bevel=.04)
    for s in (-1, 1):
        dark.grille(.5, .3, loc=(s * 1.255, -3.2, 2.3), rot=(0, 0, s * R90), slats=3, depth=.05, thickness=.035)
    steel.cyl(.07, .6, loc=(1.05, -2.72, 2.5), seg=8, bevel=0)                                   # exhaust
    steel.cyl(.1, .14, loc=(1.05, -2.72, 2.84), seg=8, bevel=0)

    t = a.pivot('Turret', (0, 1.6, 2.06))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(1.0, .12, loc=(0, 0, .04), seg=20, bevel=.02, bseg=1)                           # turntable
    tarm.box((1.6, 1.8, .3), loc=(0, .1, .25), bevel=.04, seg=1)                                  # erector base
    tarm.box((1.9, 2.65, .22), loc=(0, 2.225, .2), bevel=.03, seg=1)                              # boom platform
    pitch = math.radians(20)
    hinge = (0, 3.45, .42)
    at = _axis(hinge, pitch)
    brot = (-pitch, 0, 0)
    tsteel.cyl(.12, 2.16, loc=hinge, rot=ACROSS, seg=10, bevel=.02, bseg=1)                     # hinge
    for s in (-1, 1):
        tarm.box((.18, .5, .45), loc=(s * .96, 3.4, .4), bevel=.02, seg=1)                        # hinge cheeks
    beams = a.part('Erector', 'Armor', t)
    for x in (-.66, .66):
        beams.box((.22, 6.2, .24), loc=at(3.1, 0, x), rot=brot, bevel=.03, seg=1)                 # beams
        for sta in (1.4, 3.6, 5.8):
            beams.box((.7, .32, .3), loc=at(sta, .18, x), rot=brot, bevel=.03, seg=1)             # saddles
        for sta in (1.4, 5.8):                                                                    # clamp straps
            tsteel.box((.16, .12, .72), loc=at(sta, .6, x - .51), rot=brot, bevel=0)
            tsteel.box((.16, .12, .72), loc=at(sta, .6, x + .51), rot=brot, bevel=0)
            tsteel.box((1.1, .12, .1), loc=at(sta, 1.09, x), rot=brot, bevel=0)
    for sta in (.6, 3.0, 5.2):
        tsteel.box((1.1, .16, .16), loc=at(sta, 0, 0), rot=brot, bevel=0)                         # cross members
    for s in (-1, 1):
        tsteel.limb((s * .35, -.4, .38), tuple(at(4.9, -.12, s * .5)), .16, .16, bevel=.02, seg=1)  # rams
    for x in (-.66, .66):
        _ballistic(a, _frame(at(3.6, .6, x), brot), parent=t, prefix='Missile_', seg=12, motor=False,
                   folded=True)
    a.pivot('Muzzle_main', tuple(at(7.15, .6, 0)), t)


# ----------------------------------------------------------------------------- siege mortar
def siege_mortar(a):
    """Tracked 240 mm self-propelled mortar (Tyulpan lineage): a low chassis with seven road wheels and
    return rollers, spare links and guarded lamps on the glacis, engine grilles, a commander's cupola
    with the machine gun, and a huge short mortar at the rear on a trainable mount: breech drum and
    base plate hanging over the tail, a cradle between tall trunnion brackets, recuperators and an
    elevation ram, laid 60 degrees up over the hull. A recoil spade folds up under the tail."""
    tracks(a, 1.22, 6.5, .82, .29, 7, .46, belt_width=.54, wheel_seg=10, lean=True, sprocket=-1, rollers=2)
    hull = a.part('Hull', 'Team')
    armor = a.part('Armor', 'Armor')
    steel = a.part('Steel', 'Steel')
    deck = a.part('Deck', 'Undercarriage')
    hull.prism([(-3.1, .5), (-3.5, 1.02), (3.45, 1.02), (3.35, .5)], 1.8, bevel=.05)             # belly
    nose, brow = (-3.72, 1.14), (-2.45, 1.55)
    hull.prism([(-3.58, .97), nose, brow, (3.45, 1.55), (3.6, 1.38), (3.6, .97)], 3.0, bevel=.06)
    for s in (-1, 1):
        # Guarded headlights on the glacis corners, tow hooks, spare track links.
        gy, gz, grot = _glacis(nose, brow, .2, .04)
        armor.box((.32, .2, .16), loc=(s * 1.2, gy, gz), rot=(grot, 0, 0), bevel=.02, seg=1)
        ly, lz, _ = _glacis(nose, brow, .126, .05)
        a.part('Lamps', 'Lamp').box((.2, .03, .09), loc=(s * 1.2, ly, lz), rot=(grot, 0, 0), bevel=0)
        gy, gz, grot = _glacis(nose, brow, .55, 0)
        _track_links(a, _frame((s * .62, gy, gz), (grot, 0, 0)), 3, width=.46)
        steel.box((.14, .2, .14), loc=(s * .6, -3.34, .78), bevel=.02, seg=1)
        steel.box((.14, .2, .14), loc=(s * .6, 3.44, .78), bevel=.02, seg=1)
        _taillight(a, s * 1.25, 3.6, 1.2)
        # Side stowage: bins on the hull flanks and a tow cable along the deck edge.
        for y, d in ((-2.0, 1.0), (-.75, 1.0), (1.25, 1.2)):
            armor.box((.14, d, .34), loc=(s * 1.55, y, 1.3), bevel=.02, seg=1)
            steel.box((.03, .06, .08), loc=(s * 1.625, y, 1.38), bevel=0)
        _cable(a, [(s * 1.38, -2.1, 1.575), (s * 1.38, -.4, 1.575), (s * 1.36, .7, 1.575)])
    # Front deck: engine grilles and exhaust on the right, driver's hatch and the cupola on the left.
    for y, d in ((-2.0, .7), (-1.1, .6)):
        deck.grille(1.0, d, loc=(.72, y, 1.56), rot=(-R90, 0, 0), slats=5, depth=.07, thickness=.04)
        _grille_frame(a, .72, y, 1.54, 1.0, d, t=.04)
    deck.grille(.6, .2, loc=(1.505, .15, 1.3), rot=(0, 0, R90), slats=2, depth=.05, thickness=.04)  # exhaust
    _hatch(a, -.75, -2.1, 1.54, .26)
    _periscopes(a, [(-.75 + dx, -2.42, 1.54, 0) for dx in (-.17, 0, .17)])
    armor.cyl(.38, .26, loc=(-.75, -1.2, 1.64), seg=16, bevel=.03, bseg=1)                       # cupola
    glass = a.part('Periscopes', 'Glass')
    for k in range(5):
        ang = -R90 + (k - 2) * .62
        glass.box((.1, .05, .07), loc=(-.75 + math.cos(ang) * .38, -1.2 + math.sin(ang) * .38, 1.7),
                  rot=(0, 0, ang + R90), bevel=0)
    _heavy_mg(a, None, (-.75, -1.2, 1.76))
    _hatch(a, .6, .35, 1.54, .28)                                                                 # crew hatches
    _hatch(a, -.6, .35, 1.54, .28)
    for x in (-.45, .45):
        a.part('Ammo_boxes', 'Crate').box((.42, .3, .24), loc=(x, -.35, 1.66), bevel=.02, seg=1)
    _antenna(a, None, 1.3, -.25, 1.54, 1.3)
    for s in (-1, 1):                                                                             # ready rounds
        for y in (.85, 1.5):
            a.part('Ammo_boxes', 'Crate').box((.46, .68, .34), loc=(s * 1.25, y, 1.71), bevel=.02, seg=1)
            steel.box((.5, .06, .06), loc=(s * 1.25, y, 1.86), bevel=0)
    # Recoil spade folded up under the tail.
    lean = .38
    spade = a.part('Spade', 'Armor')
    spade.box((2.3, .12, .75), loc=(0, 3.86, .82), rot=(lean, 0, 0), bevel=.03, seg=1)
    for x in (-.7, 0, .7):
        spade.box((.08, .14, .62), loc=(x, 3.79, .84), rot=(lean, 0, 0), bevel=0)
    for x in (-.8, -.27, .27, .8):
        steel.box((.14, .1, .14), loc=(x, 4.02, .47), rot=(lean, 0, 0), bevel=0)
    for s in (-1, 1):
        steel.limb((s * .9, 3.36, .72), (s * .9, 3.84, .76), .12, .12, bevel=.02)
    steel.cyl(.06, 2.0, loc=(0, 3.82, .74), rot=ACROSS, seg=8, bevel=0)
    steel.cyl(.95, .08, loc=(0, 2.5, 1.56), seg=20, bevel=.02, bseg=1)                           # turret ring

    t = a.pivot('Turret', (0, 2.5, 1.58))
    tsteel = a.part('Turret_steel', 'Steel', t)
    tarm = a.part('Turret_armor', 'Armor', t)
    tsteel.cyl(.9, .08, loc=(0, 0, .02), seg=20, bevel=.02, bseg=1)                            # turntable
    tarm.box((1.5, 1.65, .44), loc=(0, .075, .24), bevel=.05, seg=1, taper=(.92, .92))             # mount base
    pitch = math.radians(60)
    at = _axis((0, 1.0, 1.05), pitch)                                                               # breech end
    rot = (R90 - pitch, 0, 0)
    tilt = Euler(rot, 'XYZ').to_matrix()
    L = 3.0
    tube = a.part('Mortar_tube', 'Team', t)
    tube.lathe([(.31, -.05), (.28, L - .36), (.36, L - .32), (.36, L), (.23, L), (.23, L - .3)], loc=at(0), rot=rot,
               seg=16)
    a.part('Mortar_bore', 'Undercarriage', t).cyl(.22, .02, loc=at(L - .28), rot=rot, seg=14, bevel=0)
    tube.cyl(.315, .14, loc=at(L * .6), rot=rot, seg=16, bevel=0)                                  # band
    breech = a.part('Mortar_breech', 'Armor', t)
    breech.cyl(.44, .6, loc=at(.1), rot=rot, seg=16, bevel=.04)
    breech.cyl(.62, .12, loc=at(-.26), rot=rot, seg=16, bevel=.03)                                 # base plate
    for k in range(4):                                                                             # plate ribs
        rib = (tilt @ Euler((0, 0, k * math.pi / 4), 'XYZ').to_matrix()).to_euler('XYZ')
        breech.box((1.12, .07, .12), loc=at(-.37 + k * .015), rot=tuple(rib), bevel=0)
    tarm.cyl(.4, .9, loc=at(.95), rot=rot, seg=16, bevel=.03)                                     # cradle
    tsteel.cyl(.12, 1.44, loc=at(.95), rot=ACROSS, seg=10, bevel=0)                               # trunnions
    ty, tz = at(.95).y, at(.95).z
    for s in (-1, 1):
        tarm.box((.16, .6, tz + .24 - .42), loc=(s * .62, ty, (tz + .24 + .42) / 2), bevel=.03, seg=1)  # brackets
        tsteel.cyl(.18, .06, loc=(s * .72, ty, tz), rot=ACROSS, seg=10, bevel=0)                  # trunnion caps
    rec = a.part('Recuperators', 'Steel', t)
    for side in (-.18, .18):
        rec.cyl(.08, 1.1, loc=at(1.3, -.44, side), rot=rot, seg=10, bevel=0)
        rec.cyl(.095, .06, loc=at(1.85, -.44, side), rot=rot, seg=10, bevel=0)
    tsteel.limb((0, -.55, .44), tuple(at(1.3, -.48)), .16, .16, bevel=.02, seg=1)                   # elevation ram
    tarm.box((.18, .22, .18), loc=(-.62, ty - .41, 1.55), bevel=.02, seg=1)                         # sight
    a.part('Sight', 'Glass', t).box((.12, .04, .1), loc=(-.62, ty - .53, 1.57), bevel=.01, seg=1)
    a.pivot('Muzzle_main', tuple(at(L + .02)), t)


# ----------------------------------------------------------------------------- projectiles
def ballistic_missile(a):
    """Tactical ballistic missile, 7 m long and 0.9 m across (nose at -Y, origin at the centre): dark
    green and white, grid fins at the tail and a glowing motor."""
    _ballistic(a, Matrix.Identity(4))


def heavy_rocket(a):
    """300 mm heavy rocket, 3.5 m long (nose at -Y, origin at the centre): dark body with steel bands,
    a hazard-yellow ogive warhead, four swept tail fins on a collar and a glowing motor."""
    h, r = 1.75, .15
    a.part('Body', 'Armor').lathe([(r * .86, -h + .02), (r, -h + .12), (r, h - 1.02)], rot=FORWARD, seg=10)
    a.part('Warhead', 'Hazard').lathe([(r * .985, h - 1.08), (r * .975, h - .8), (r * .84, h - .45), (r * .56, h - .2),
                                       (r * .22, h - .04), (0, h)], rot=FORWARD, seg=10)
    steel = a.part('Bands', 'Steel')
    for y in (-.45, .55):
        steel.cyl(r + .012, .06, loc=(0, y, 0), rot=FORWARD, seg=10, bevel=0)
    fins = a.part('Fins', 'Armor')
    steel.cyl(r + .01, .36, loc=(0, h - .26, 0), rot=FORWARD, seg=10, bevel=0)             # fin collar
    for k in range(4):
        ang = math.pi / 4 + k * R90
        prof = [(h - .34, r), (h - .16, r + .19), (h - .03, r + .19), (h - .03, r)]
        fins.prism(prof, .014, loc=(0, 0, 0), rot=(0, ang - R90, 0), bevel=0)
    a.part('Nozzle', 'Steel').lathe([(r * .56, -.12), (r * .74, .08), (r * .62, .08), (r * .46, 0)],
                                    loc=(0, h - .01, 0), rot=BACKWARD, seg=10)
    a.part('Motor', 'Alloy').cyl(r * .42, .02, loc=(0, h + .01, 0), rot=BACKWARD, seg=10, bevel=0)


# name: (builder, Asset options). Vehicles use tight contact AO like 3d_astra's units.
BUILDERS = {
    'twin_tank': (twin_tank, dict(ao_distance=.6, grime_height=.55)),
    'heavy_rocket_artillery': (heavy_rocket_artillery, dict(ao_distance=.6, grime_height=.55)),
    'ballistic_launcher': (ballistic_launcher, dict(ao_distance=.6, grime_height=.55)),
    'siege_mortar': (siege_mortar, dict(ao_distance=.6, grime_height=.55)),
    'ballistic_missile': (ballistic_missile, dict(ao_distance=.35, ground=False)),
    'heavy_rocket': (heavy_rocket, dict(ao_distance=.15, ground=False)),
}
