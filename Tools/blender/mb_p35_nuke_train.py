"""Prompt 35 wave 12 (lane C): the nuke train (Nemesis) rebuilt from scratch (spec: Tools/blender/specs/nuke_train.json).

A rail boss on 1.435 m gauge, the old file's six cars kept at their places and lengths (41.2 m over the couplers, the
headstocks at y -10.62 / -1.58, -0.82 / 10.62, 11.38 / 15.43, 16.19 / 20.24, 20.97 / 25.02, 25.78 / 29.83) and every
runtime pivot at its old place. Real references: the BZhRK "Molodets" (the RT-23 rail-mobile ICBM: the launcher car
with its roof doors and the catenary diverter that swings the overhead wire clear before a launch), the Soviet BP-43
armoured train (the armoured locomotive with its turret) and railway artillery / air-defence flatcars.

1. Armoured diesel locomotive (front): V plough with the obstacle deflector and hazard chevrons, the wedge cab with
   vision slits under a brow, headlamps, horn, side doors with steps and handrails, the hood of bolted sloped plates
   with louvres, radiator fans under grilles and twin exhaust stacks; two three-axle bogies behind armoured skirts;
   the twin gun turret on the hood (`Turret`, `Main_cannon` / `_2`, `Muzzle_brake` / `_2`, `Muzzle_main` between
   the tips: the mantlet, the bustle, the commander's sight, the dish mast) and the MG cupola on the cab roof
   (`Mount_mg` / `Muzzle_mg`).
2. The launcher car: the launch-control cabin at its front (vents, slits, warning lights, datalink, the second MG
   cupola `Mount_mg.001` / `Muzzle_mg.001`), the armoured trough with the two roof doors swung open on their hinges,
   the folded catenary diverter, hazard chevrons and radiation signs; the erector (`Erector`, hinged at the rear,
   rest pose lowered: the strongback, the saddles and the clamp bands, the hydraulic rams) carrying the ICBM under
   `Icbm_payload` (the `icbm` projectile's red shroud, white stages, yellow bands, black rings, trefoils, fins).
3. Rocket flatcar (`Part_rocket` > `Mount_rocket` > `Muzzle_rocket`): a 16-tube 220 mm launcher pod on its turntable.
4. SAM flatcar (`Part_missile` > `Mount_missile` > `Muzzle_missile`): a Roland-pattern turret: the low turntable
   (under the 152 mm barrel's line) with a launch tube pair on each side arm, the search radar folded behind.
5. Gun flatcar (`Part_gun152` > `Mount_gun` > `Muzzle_gun`): a 152 mm gun on its low pedestal, shield, cradle,
   recuperators, the long barrel with its brake reaching forward over the SAM car, the outrigger jacks.
6. AA flatcar (`Part_aa` > `Mount_mg.002` > `Muzzle_mg.002`): a twin 35 mm turret with its radar dish.

Every car: side sills with the general's Team band, SA-3 automatic couplers, air hoses, corner steps and handrails,
two bogies (frames, axle boxes, springs, wheels, the bolster). The flatcar loads are their Part_* pivots (one
shade off). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
GAUGE = 1.435
ICBM_L, ICBM_R = 9.7, .75


# ============================================================================= running gear and frames
def _bogie(a, y, axles, base, wr=.46, parent=None, side=True):
    """A bogie under y: side frames with the axle boxes and springs, the wheelsets, the bolster."""
    fr = a.part('Bogies', 'Undercarriage', parent)
    L = base + .9
    for s in (-1, 1):
        x = s * (GAUGE / 2 + .14)
        k.block(fr, (.16, L, .32), loc=(x, y, wr + .02), chamfer=.03)
        for i in range(axles):
            yy = y - base / 2 + i * base / max(1, axles - 1)
            fr.box((.22, .3, .28), loc=(x + s * .02, yy, wr), bevel=0)
            a.part('Bogie_springs', 'Steel', parent).cyl(.065, .22, loc=(x, yy, wr + .28), seg=6, bevel=0)
    wheels = a.part('Rail_wheels', 'Steel', parent)
    for i in range(axles):
        yy = y - base / 2 + i * base / max(1, axles - 1)
        for s in (-1, 1):
            k.lathe(wheels, [(0, -.06), (wr * .9, -.06), (wr, -.03), (wr, .04), (wr * 1.08, .06), (0, .06)],
                    loc=(s * GAUGE / 2, yy, wr), rot=(0, s * R90, 0), seg=12)
        fr.cyl(.07, GAUGE + .1, loc=(0, yy, wr), rot=(0, R90, 0), seg=6, bevel=0)
    k.block(fr, (GAUGE + .3, .5, .26), loc=(0, y, wr + .2), chamfer=.03)
    a.part('Brake_cylinders', 'Armor', parent).cyl(.12, .3, loc=(.45, y, wr + .38), rot=(0, R90, 0), seg=8, bevel=0)


def _frame(a, y0, y1, z=1.25, w=3.1, front=True, rear=True, band=True):
    """Side sills, headstocks, SA-3 couplers with air hoses, corner steps and handrails between y0 and y1."""
    sill = a.part('Underframe', 'Undercarriage')
    for s in (-1, 1):
        k.block(sill, (.16, y1 - y0, .32), loc=(s * (w / 2 - .08), (y0 + y1) / 2, z - .16), chamfer=.02)
        if band:
            a.part('Car_band', 'Team').box((.012, (y1 - y0) * .7, .12), loc=(s * (w / 2 + .002), (y0 + y1) / 2,
                                                                              z - .12), bevel=0)
    co = a.part('Couplers', 'Steel')
    hs = a.part('Headstocks', 'Armor')
    for y, e, on in ((y0, -1, front), (y1, 1, rear)):
        k.block(hs, (w, .14, .36), loc=(0, y, z - .18), chamfer=.02)
        if not on:
            continue
        co.box((.22, .36, .2), loc=(0, y + e * .2, z - .25), bevel=0)
        k.block(co, (.3, .14, .28), loc=(0, y + e * .38, z - .25), chamfer=.02)
        a.part('Air_hoses', 'Rubber').tube([(.35, y + e * .05, z - .3), (.42, y + e * .25, z - .55),
                                            (.38, y + e * .32, z - .45)], .025, seg=4)
        for s in (-1, 1):
            st = a.part('Car_steps', 'Steel')
            st.box((.36, .2, .03), loc=(s * (w / 2 - .2), y - e * .15, z - .55), bevel=0)
            st.box((.03, .03, .45), loc=(s * (w / 2 - .02), y - e * .05, z - .35), bevel=0)


# ============================================================================= 1. locomotive
def _sec(y, wb, zb, wm, zm, wt, zt):
    return [(-wb, y, zb), (wb, y, zb), (wm, y, zm), (wt, y, zt), (-wt, y, zt), (-wm, y, zm)]


def _locomotive(a):
    Y0, Y1 = -10.62, -1.58
    for y in (-8.55, -3.65):
        _bogie(a, y, 3, 2.2, .5)
    _frame(a, Y0, Y1, z=1.3, front=False)
    hull = a.part('Hull', 'Team')
    k.sharp_loft(hull, [_sec(-10.45, 1.5, 1.32, 1.5, 1.85, .9, 2.25), _sec(-9.7, 1.6, 1.32, 1.62, 2.05, 1.2, 2.95),
                        _sec(-9.0, 1.6, 1.32, 1.62, 2.25, 1.22, 3.45), _sec(-7.3, 1.6, 1.32, 1.62, 2.25, 1.22, 3.45),
                        _sec(-7.0, 1.6, 1.32, 1.62, 2.1, 1.18, 3.05), _sec(-2.3, 1.6, 1.32, 1.62, 2.1, 1.18, 3.05),
                        _sec(-1.75, 1.55, 1.32, 1.57, 2.05, 1.1, 2.75)], chamfer=.05)
    arm = a.part('Armor', 'Armor')
    bolts = a.part('Kit_bolts', 'Steel')
    # The V plough with its obstacle deflector and chevrons.
    k.sharp_loft(arm, [[(-.3, -10.99, .2), (.3, -10.99, .2), (1.35, -10.66, .2), (1.45, -10.42, .2),
                        (-1.45, -10.42, .2), (-1.35, -10.66, .2)],
                       [(-.25, -10.7, 1.0), (.25, -10.7, 1.0), (1.25, -10.54, 1.0), (1.38, -10.4, 1.0),
                        (-1.38, -10.4, 1.0), (-1.25, -10.54, 1.0)]], chamfer=.03)
    chev = a.part('Chevrons', 'SafetyStripe')
    for s in (-1, 1):
        for i in range(3):
            chev.box((.18, .03, .55), loc=(s * (.45 + i * .32), -10.86 + i * .1 * .9, .62), rot=(0, s * .5, -s * .3),
                     bevel=0)
    # The wedge cab: vision slits under the brow, the driver's slit, headlamps, horn, the roof hatch.
    gl = a.part('Vision_slits', 'Glass')
    ang = math.atan2(3.45 - 2.95, .7)
    for x in (-.72, 0, .72):
        gl.box((.5, .12, .04), loc=(x, -9.4, 3.18), rot=(ang, 0, 0), bevel=0)
    arm.box((2.2, .26, .06), loc=(0, -9.2, 3.42), bevel=0)
    gl.box((.7, .12, .04), loc=(0, -10.1, 2.58), rot=(math.atan2(.7, .75), 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .78, -10.47, 1.7), (0, -1, 0), r=.13, mat='Armor', guard=True)
        a.part('Lamps', 'Lamp').box((.14, .04, .1), loc=(s * 1.05, -10.47, 1.95), bevel=0)
        for y in (-8.55, -7.75):
            gl.box((.03, .5, .1), loc=(s * 1.47, y, 2.95), rot=(0, -s * .32, 0), bevel=0)
        k.block(a.part('Cab_doors', 'Armor'), (.04, .64, .72), loc=(s * 1.63, -7.95, 1.75), chamfer=.01)
        a.part('Handrails', 'Steel').tube([(s * 1.68, -8.35, 1.4), (s * 1.68, -8.35, 2.2)], .02, seg=4)
        a.part('Car_steps', 'Steel').box((.3, .5, .03), loc=(s * 1.55, -7.95, .95), bevel=0)
        # Armoured bogie skirts with their bolts, the side plates of the hood with seams and louvres.
        for y in (-8.55, -3.65):
            k.block(arm, (.06, 3.3, .8), loc=(s * 1.67, y, 1.1), chamfer=.015)
            bolts.bolts([(s * 1.71, y + d, 1.42) for d in (-1.4, -.7, 0, .7, 1.4)], r=.028, h=.03, rot=(0, R90, 0),
                        seg=6, bevel=0)
        for y in (-6.3, -5.0, -3.7, -2.4):
            k.block(arm, (.06, 1.2, .52), loc=(s * 1.42, y, 2.56), rot=(0, -s * .44, 0), chamfer=.012)
            bolts.bolts([(s * 1.45, y + d, 2.6) for d in (-.5, .5)], r=.025, h=.03, rot=(0, R90, 0), seg=6, bevel=0)
        K.grille(a, (s * 1.645, -5.55, 1.72), 1.1, .5, facing=(s, 0, 0), slats=4)
        K.grille(a, (s * 1.645, -2.9, 1.72), 1.1, .5, facing=(s, 0, 0), slats=4)
        a.part('Sandboxes', 'Armor').box((.3, .4, .3), loc=(s * 1.3, -10.2, 1.1), bevel=.02)
    # The roof: radiator fans under grilles ahead of and behind the turret, exhaust stacks, horn, hatch, antenna.
    for y, d in ((-6.55, .62), (-2.85, .52)):
        a.part('Fans', 'Rubber').cyl(d * .45, .04, loc=(0, y, 3.07), seg=12, bevel=0)
        K.grille(a, (0, y, 3.1), 1.3, d, facing=(0, 0, 1), slats=4)
    for s in (-1, 1):
        K.exhaust(a, (s * .6, -2.35, 3.0), r=.11, length=.45, direction=(0, 0, 1), muffler=False)
        K.soot(a, (s * .6, -2.35, 3.5), radius=.5, k=.45)
    k.lathe(a.part('Steel', 'Steel'), [(.05, 0), (.09, .3), (0, .31)], loc=(-.55, -9.3, 3.55), rot=K.FORWARD, seg=8)
    K.hatch_rect(a, (-.5, -7.6, 3.46), size=(.7, .5), normal=(0, 0, 1))
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.35, -2.6, 2.6), h=1.3, r=.025)
    a.pivot('Point_exhaust', (.6, -2.35, 3.5))
    a.pivot('Point_fire', (0, -5.5, 3.2))
    _loco_turret(a)
    _cupola(a, 'Mount_mg', 'Muzzle_mg', (.45, -8.3, 3.53))


def _loco_turret(a):
    """The twin gun turret on the hood (gun_behemoth)."""
    k.lathe(a.part('Turret_ring', 'Armor'), [(1.28, -.14), (1.28, 0), (1.2, .07), (0, .07)], loc=(0, -4.9, 2.99),
            seg=24, worn=(1,))
    t = a.pivot('Turret', (0, -4.9, 3.13))
    body = a.part('Turret_body', 'Team', t)
    k.sharp_loft(body, [[(-1.05, -1.05, 0), (1.05, -1.05, 0), (1.15, .9, 0), (-1.15, .9, 0)],
                        [(-.85, -.85, .82), (.85, -.85, .82), (.95, .85, .85), (-.95, .85, .85)]], chamfer=.05)
    k.block(a.part('Turret_armor', 'Armor', t), (1.9, .55, .7), loc=(0, 1.2, .38), chamfer=.04)   # the bustle
    pitch = math.atan2(1.22 - .52, 4.36 - 1.1)
    k.block(a.part('Turret_armor', 'Armor', t), (1.15, .42, .65), loc=(0, -1.08, .52), rot=(-.21, 0, 0), chamfer=.05)
    Lb = math.hypot(3.26, .7)
    cp, sp = math.cos(pitch), math.sin(pitch)
    for s, cn, br in ((-1, 'Main_cannon', 'Muzzle_brake'), (1, 'Main_cannon_2', 'Muzzle_brake_2')):
        x = s * .3
        rot = (R90 - pitch, 0, 0)
        k.lathe(a.part(cn, 'Steel', t), [(.1, 0), (.1, .3), (.08, .36), (.07, Lb - .31), (0, Lb - .31)],
                loc=(x, -1.1, .52), rot=rot, seg=12, worn=(1,))
        k.lathe(a.part(br, 'Undercarriage', t), [(.07, 0), (.12, .03), (.12, .28), (.09, .31), (0, .31)],
                loc=(x, -1.1 - (Lb - .31) * cp, .52 + (Lb - .31) * sp), rot=rot, seg=12)
    a.pivot('Muzzle_main', (0, -4.36, 1.22), t)
    st = a.part('Turret_steel', 'Steel', t)
    k.block(a.part('Turret_sight', 'Armor', t), (.36, .4, .3), loc=(.55, -.3, .95), chamfer=.03)
    a.part('Vision_slits', 'Glass', t).box((.26, .02, .14), loc=(.55, -.51, 1.0), bevel=0)
    st.cyl(.05, .55, loc=(-.55, .8, 1.1), seg=6, bevel=0)
    K.dish(a.part('Datalink', 'Medical', t), st, (-.55, .8, 1.45), r=.3, normal=(0, -.5, .8), seg=10)
    a.part('Turret_band', 'Team', t).box((1.95, .02, .14), loc=(0, 1.48, .5), bevel=0)
    a.part('Kit_bolts', 'Steel', t).bolts([(s * .45, -1.32, .35 + dz) for s in (-1, 1) for dz in (0, .3)], r=.03,
                                          h=.03, rot=K.FORWARD, seg=6, bevel=0)
    K.soot(a, (0, -9.2, 4.3), radius=.7, k=.35)


def _cupola(a, mount, muzzle, loc):
    """An MG cupola: the armoured drum on its ring, vision blocks, the gun in the shield (muzzle 1.25 ahead)."""
    m = a.pivot(mount, loc)
    k.lathe(a.part('MG_cupola', 'Armor', m), [(.42, -.05), (.42, .1), (.36, .32), (.2, .4), (0, .42)], seg=12,
            worn=(1, 2))
    gl = a.part('MG_glass', 'Glass', m)
    for i in range(4):
        u = -R90 + (i - 1.5) * .55
        gl.box((.12, .02, .07), loc=(math.cos(u) * .38, math.sin(u) * .38, .22), rot=(0, 0, u + R90), bevel=0)
    k.lathe(a.part('MG_gun', 'Steel', m), [(.035, 0), (.035, .9), (0, .9)], loc=(0, -.35, .16), rot=K.FORWARD, seg=6)
    k.block(a.part('MG_armor', 'Armor', m), (.36, .06, .26), loc=(0, -.4, .16), chamfer=.015)
    a.pivot(muzzle, (0, -1.25, .16), m)


# ============================================================================= 2. launcher car
def _launcher_car(a):
    Y0, Y1 = -.82, 10.62
    for y in (1.3, 8.5):
        _bogie(a, y, 2, 1.8, .46)
    _frame(a, Y0, Y1, z=1.34)
    hull = a.part('Hull', 'Team')
    trough = [(-1.6, 1.34), (1.6, 1.34), (1.62, 2.2), (1.35, 2.7), (1.02, 2.7), (1.02, 2.05), (-1.02, 2.05),
              (-1.02, 2.7), (-1.35, 2.7), (-1.62, 2.2)]
    k.sharp_loft(hull, [[(x, y, z) for x, z in trough] for y in (1.0, 10.45)], chamfer=.04)
    a.part('Trough_liner', 'Undercarriage').box((2.0, 9.3, .04), loc=(0, 5.7, 2.07), bevel=0)
    arm = a.part('Armor', 'Armor')
    bolts = a.part('Kit_bolts', 'Steel')
    chev, bars = a.part('Chevrons', 'SafetyStripe'), a.part('Chevron_bars', 'Charred')
    for s in (-1, 1):
        for y in (1.3, 8.5):
            k.block(arm, (.06, 2.9, .8), loc=(s * 1.665, y, 1.1), chamfer=.015)
            bolts.bolts([(s * 1.7, y + d, 1.4) for d in (-1.2, -.4, .4, 1.2)], r=.028, h=.03, rot=(0, R90, 0), seg=6,
                        bevel=0)
        # The roof doors swung open: each a long curved panel hinged at the trough's top edge, leaning out.
        door = a.part('Roof_doors', 'Team')
        k.extrude(door, [(-.05, 0), (.05, 0), (.25, 1.15), (.15, 1.17)], 9.0, loc=(s * 1.36, 5.8, 2.72),
                  rot=(0, 0, 0) if s > 0 else (0, 0, math.pi), axis='Y', chamfer=.02)
        for y in (2.0, 4.5, 7.0, 9.5):
            a.part('Door_hinges', 'Steel').cyl(.06, .4, loc=(s * 1.36, y, 2.72), rot=K.FORWARD, seg=6, bevel=0)
            a.part('Door_rams', 'Steel').limb((s * 1.25, y, 2.4), (s * 1.5, y, 3.3), .05, .05, bevel=0)
        # Hazard chevrons along the upper chamfer, radiation signs on the side walls, seams, tail lamps.
        for y0, y1 in ((1.2, 3.6), (7.2, 10.1)):
            chev.box((.04, y1 - y0, .3), loc=(s * 1.5, (y0 + y1) / 2, 2.45), rot=(0, -s * 1.07, 0), bevel=0)
            n = int((y1 - y0) / .5)
            for i in range(n):
                bars.box((.045, .12, .34), loc=(s * 1.505, y0 + (i + .5) * (y1 - y0) / n, 2.45),
                         rot=(.6 * s, -s * 1.07, 0), bevel=0)
        _trefoil(a, (s * 1.625, 5.4, 1.8), s, .7)
        for y in (4.1, 6.7):
            arm.box((.04, .07, .8), loc=(s * 1.635, y, 1.76), bevel=0)
        a.part('Tail_lights', 'Alloy').box((.14, .04, .1), loc=(s * 1.3, 10.47, 2.3), bevel=0)
    # The launch-control cabin at the front: vents, slits, warning lights, datalink, the second MG cupola.
    cab = a.part('Control_cabin', 'Team')
    k.sharp_loft(cab, [[(-1.55, -.7, 1.34), (1.55, -.7, 1.34), (1.55, .95, 1.34), (-1.55, .95, 1.34)],
                       [(-1.5, -.66, 3.0), (1.5, -.66, 3.0), (1.5, .95, 3.0), (-1.5, .95, 3.0)],
                       [(-1.1, -.5, 3.4), (1.1, -.5, 3.4), (1.1, .9, 3.4), (-1.1, .9, 3.4)]], chamfer=.05)
    for s in (-1, 1):
        a.part('Vision_slits', 'Glass').box((.03, .45, .1), loc=(s * 1.53, -.2, 2.75), bevel=0)
        a.part('Warning_lights', 'Alloy').cyl(.09, .14, loc=(s * .95, .5, 3.45), seg=8, bevel=0)
        _trefoil(a, (s * 1.535, .45, 2.2), s, .45)
    K.grille(a, (0, -.69, 2.2), 1.4, .5, facing=(0, -1, 0), slats=4)
    K.dish(a.part('Datalink', 'Medical'), a.part('Datalink', 'Armor'), (.55, .4, 3.62), r=.3, normal=(0, -.5, .8),
           seg=10)
    a.part('Steel', 'Steel').cyl(.05, .25, loc=(.55, .4, 3.48), seg=6, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.0, .7, 3.4), h=1.1, r=.025)
    _cupola(a, 'Mount_mg__001', 'Muzzle_mg__001', (-.45, -.28, 3.5))
    # The folded catenary diverter on the cabin's rear: a mast and the long arm laid along the trough's edge.
    dv = a.part('Diverter', 'Steel')
    dv.limb((1.2, 1.05, 3.0), (1.2, 1.05, 3.6), .12, .12, bevel=0)
    dv.limb((1.2, 1.05, 3.55), (1.15, 4.6, 3.05), .08, .06, bevel=0)
    a.part('Diverter', 'Hazard').box((.1, .4, .1), loc=(1.15, 4.5, 3.05), bevel=0)
    _erector(a)


def _trefoil(a, loc, s, size):
    """A radiation sign on a side wall facing s: the yellow plate, the three black blades and the hub."""
    x, y, z = loc
    a.part('Signs', 'SafetyStripe').box((.02, size, size), loc=(x, y, z), bevel=0)
    bl = a.part('Trefoils', 'Charred')
    for i in range(3):
        u = R90 + i * TAU / 3
        bl.box((.022, size * .2, size * .28), loc=(x + s * .006, y + math.cos(u) * size * .2, z + math.sin(u) * size * .2),
               rot=(u - R90, 0, 0), bevel=0)
    bl.cyl(size * .07, .024, loc=(x + s * .006, y, z), rot=(0, R90, 0), seg=8, bevel=0)


def _erector(a):
    """The erector hinged at the trough's rear (static brackets and pin; the strongback, saddles, clamp bands and
    rams on `Erector`), the ICBM on `Icbm_payload`."""
    arm = a.part('Armor', 'Armor')
    for s in (-1, 1):
        k.block(arm, (.18, .8, .75), loc=(s * .92, 10.2, 2.35), chamfer=.03)
    a.part('Steel', 'Steel').cyl(.12, 2.06, loc=(0, 10.25, 2.4), rot=(0, R90, 0), seg=10, bevel=0)
    e = a.pivot('Erector', (0, 10.25, 2.4))
    fr = a.part('Erector_frame', 'Steel', e)
    for x in (-.42, .42):
        k.block(fr, (.14, 9.3, .22), loc=(x, -4.7, .22), chamfer=.02)
    for y in (-8.0, -5.5, -3.0, -.8):
        fr.box((.98, .1, .12), loc=(0, y, .22), bevel=0)
    k.block(fr, (1.5, .5, .5), loc=(0, -.1, .18), chamfer=.04)
    cl = a.part('Erector_clamps', 'Armor', e)
    for y in (-8.3, -5.9, -3.4, -1.6):
        k.block(cl, (1.4, .3, .32), loc=(0, y, .26), chamfer=.03)
    for y in (-6.25, -3.25):
        k.ring(cl, [(ICBM_R + .01, -.11), (ICBM_R + .07, -.1), (ICBM_R + .07, .1), (ICBM_R + .01, .11)],
               loc=(0, y, .9), rot=K.FORWARD, seg=20)
    for s in (-1, 1):
        a.part('Erector_rams', 'Steel', e).limb((s * .55, -2.0, .1), (s * .55, -4.2, -.3), .1, .1, bevel=0)
    p = a.pivot('Icbm_payload', (0, -ICBM_L / 2, .9), e)
    _icbm(a, p)


def _icbm(a, p):
    """The missile (the `icbm` projectile's scheme), centred on its pivot, nose at -Y."""
    L, r = ICBM_L, ICBM_R
    h = L / 2
    k.lathe(a.part('Icbm_warhead', 'BarrelRed', p), [(0, -h), (.18, -h + .15), (.38, -h + .5), (.56, -h + 1.0),
                                                      (.68, -h + 1.55), (.74, -h + 2.05), (r, -h + 2.3)],
            rot=K.BACKWARD, seg=20)
    k.lathe(a.part('Icbm_body', 'Fuel', p), [(r, -h + 2.3), (r, h - .9)], rot=K.BACKWARD, seg=20, caps=(False, False))
    k.lathe(a.part('Icbm_skirt', 'Armor', p), [(r, h - .9), (.8, h - .55), (.84, h), (.5, h), (0, h)],
            rot=K.BACKWARD, seg=20, worn=(1, 2))
    k.lathe(a.part('Icbm_nozzle', 'Undercarriage', p), [(.48, h - .1), (.4, h + .1), (.22, h + .12)], rot=K.BACKWARD,
            seg=14, caps=(False, False))
    for y in (-h + 2.35, .2, 2.9):
        k.ring(a.part('Icbm_bands', 'Hazard', p), [(r - .02, y - .16), (r + .018, y - .15), (r + .018, y + .15),
                                                   (r - .02, y + .16)], rot=K.BACKWARD, seg=20)
        if y > -1:
            for dy in (-.2, .2):
                k.ring(a.part('Icbm_rings', 'Charred', p), [(r - .03, y + dy - .035), (r + .026, y + dy - .03),
                                                            (r + .026, y + dy + .03), (r - .03, y + dy + .035)],
                       rot=K.BACKWARD, seg=20)
    for s in (-1, 1):
        sign = a.part('Icbm_signs', 'SafetyStripe', p)
        sign.box((.02, .8, .8), loc=(s * (r + .005), -1.1, 0), bevel=0)
        bl = a.part('Icbm_trefoils', 'Charred', p)
        for i in range(3):
            u = R90 + i * TAU / 3
            bl.box((.022, .16, .22), loc=(s * (r + .012), -1.1 + math.cos(u) * .16, math.sin(u) * .16),
                   rot=(u - R90, 0, 0), bevel=0)
    a.part('Icbm_raceway', 'Armor', p).box((.12, L - 3.7, .05), loc=(0, .65, r + .015), bevel=0)
    fins = a.part('Icbm_fins', 'Armor', p)
    for i in range(4):
        u = math.pi / 4 + i * R90
        c, s = math.cos(u), math.sin(u)
        k.extrude(fins, [(h - 1.15, 0), (h - .2, 0), (h - .35, .42), (h - .9, .42)], .05,
                  loc=(c * r * .95, 0, s * r * .95), rot=(0, R90 - u, 0), axis='X', chamfer=0)


# ============================================================================= 3-6. flatcars
def _flatcar(a, y0, y1, part, pivot_y, deck=1.62):
    """A flatcar: frame, two bogies, the deck with planks and stake pockets; returns its load pivot."""
    yc = (y0 + y1) / 2
    for y in (y0 + 1.0, y1 - 1.0):
        _bogie(a, y, 2, 1.1, .42)
    _frame(a, y0, y1, z=deck - .1)
    k.block(a.part('Car_deck', 'Armor'), (2.9, y1 - y0 - .1, .12), loc=(0, yc, deck - .06), chamfer=.015)
    pl = a.part('Deck_planks', 'Wood')
    n = int((y1 - y0 - .4) / .5)
    for i in range(n):
        pl.box((2.6, .02, .012), loc=(0, y0 + .45 + i * .5, deck + .004), bevel=0)
    sp = a.part('Stake_pockets', 'Steel')
    for i in range(4):
        y = y0 + .5 + i * (y1 - y0 - 1.0) / 3
        for s in (-1, 1):
            sp.box((.06, .14, .16), loc=(s * 1.47, y, deck - .1), bevel=0)
    # Stanchions in the stake pockets with a chain rail between (the crew's guard), one side open for loading.
    rail = a.part('Car_rails', 'Steel')
    ys = [y0 + .5 + i * (y1 - y0 - 1.0) / 3 for i in range(4)]
    for y in ys:
        rail.box((.04, .04, .9), loc=(1.47, y, deck + .45), bevel=0)
    rail.tube([(1.47, ys[0], deck + .85), (1.47, ys[-1], deck + .85)], .018, seg=4, caps=False)
    rail.tube([(1.47, ys[0], deck + .5), (1.47, ys[-1], deck + .5)], .014, seg=4, caps=False)
    return a.pivot(part, (0, pivot_y, deck)), yc


def _crates(a, loc, n=3, yaw=0.0, size=(.5, .8, .3), parent=None, mat='Crate'):
    """A stack of ammunition crates on the deck (each with its lid line, bands and rope handles)."""
    x, y, z = loc
    for i in range(n):
        K.crate(a.part('Ammo_crates', mat, parent), a.part('Crate_bands', 'Steel', parent), size,
                (x + (i % 2) * .03, y + (i // 2) * .0, z + i * size[2]), rot=(0, 0, yaw + (i % 2) * .06))


def _rocket_car(a):
    p, yc = _flatcar(a, 11.38, 15.43, 'Part_rocket', 13.4)
    k.lathe(a.part('Rocket_pedestal', 'Armor', p), [(.9, 0), (.9, .12), (.6, .2), (.55, .6), (0, .6)], seg=16,
            worn=(1,))
    a.part('Rocket_band', 'Team', p).cyl(.91, .06, loc=(0, 0, .06), seg=16, bevel=0)
    m = a.pivot('Mount_rocket', (0, 0, .64), p)
    k.block(a.part('Rocket_cradle', 'Steel', m), (1.2, 1.0, .25), loc=(0, .1, .05), chamfer=.03)
    elev = math.atan2(.68, 1.3)
    rot = (-elev, 0, 0)
    c = (0, .55, .5)
    mm = K.frame(c, rot)
    k.block(a.part('Rocket_box', 'Team', m), (1.5, 2.9, .9), loc=c, rot=rot, chamfer=.05)
    tubes = a.part('Rocket_tubes', 'Undercarriage', m)
    for i in range(4):
        for j in range(4):
            tubes.cyl(.13, .04, loc=K._at(mm, (-.54 + i * .36, -1.455, -.3 + j * .2)), rot=(R90 - elev, 0, 0),
                      seg=8, bevel=0)
    k.block(a.part('Rocket_box', 'Armor', m), (1.6, .1, 1.0), loc=K._at(mm, (0, -1.43, 0)), rot=rot, chamfer=.02)
    for s in (-1, 1):
        a.part('Rocket_rams', 'Steel', m).limb((s * .5, -.3, .05), K._at(mm, (s * .5, -.6, -.45)), .08, .08, bevel=0)
    for i in range(3):
        a.part('Rocket_ribs', 'Armor', m).box((1.52, .08, .06), loc=K._at(mm, (0, -.8 + i * .9, .47)), rot=rot, bevel=0)
    a.part('Rocket_band', 'Team', m).box((1.52, .4, .02), loc=K._at(mm, (0, .9, .46)), rot=rot, bevel=0)
    a.part('Rocket_cables', 'Rubber', m).tube([(.6, .5, .1), (.7, 1.0, .3), K._at(mm, (.6, 1.3, .2))], .03, seg=4)
    a.pivot('Muzzle_rocket', (0, -.9, .68), m)
    _crates(a, (-.9, 1.5, .0), n=2, yaw=R90, size=(.45, 1.0, .3), parent=p)
    _crates(a, (.95, -1.5, .0), n=2, yaw=R90, size=(.45, 1.0, .3), parent=p)
    K.tone(a, 'Rocket_', k=.9)


def _sam_car(a):
    p, yc = _flatcar(a, 16.19, 20.24, 'Part_missile', 18.22)
    k.lathe(a.part('Sam_base', 'Armor', p), [(1.1, 0), (1.1, .1), (.95, .18), (0, .18)], seg=16, worn=(1,))
    m = a.pivot('Mount_missile', (0, 0, .32), p)
    k.lathe(a.part('Sam_pedestal', 'Team', m), [(.95, -.14), (.95, .02), (.85, .08), (0, .08)], seg=16)
    elev = math.atan2(2.45 - .9, 1.3)
    for s in (-1, 1):
        x = s * 1.0
        a.part('Sam_yoke', 'Armor', m).limb((x, .2, .05), (x, .1, .9), .22, .3, bevel=.02)
        rot = (-elev, 0, 0)
        c = (x * 1.08, -.35, 1.5)
        mm = K.frame(c, rot)
        for dx in (-.14, .14):
            k.lathe(a.part('Sam_tubes', 'Team', m), [(.13, -1.0), (.15, -.95), (.15, .95), (.13, 1.0)],
                    loc=K._at(mm, (dx, 0, 0)), rot=(R90 - elev, 0, 0), seg=10, caps=(True, True))
            a.part('Sam_tube_caps', 'Undercarriage', m).cyl(.12, .02, loc=K._at(mm, (dx, -1.01, 0)),
                                                            rot=(R90 - elev, 0, 0), seg=10, bevel=0)
        a.part('Sam_bands', 'Hazard', m).box((.34, .06, .32), loc=K._at(mm, (0, -.6, 0)), rot=rot, bevel=0)
    # The search radar folded flat behind, the tracking dish on its post.
    a.part('Sam_steel', 'Steel', m).cyl(.06, .5, loc=(0, .85, .3), seg=6, bevel=0)
    k.block(a.part('Sam_radar', 'Armor', m), (1.3, .5, .08), loc=(0, .85, .58), rot=(-.25, 0, 0), chamfer=.02)
    a.part('Sam_radar_face', 'Medical', m).box((1.2, .02, .04), loc=(0, .62, .6), rot=(-.25, 0, 0), bevel=0)
    a.pivot('Muzzle_missile', (0, -1.3, 2.45), m)
    # The power unit and the reload canisters on the deck's ends (clear of the turret's sweep).
    k.block(a.part('Sam_generator', 'Team', p), (1.0, .7, .7), loc=(-.75, 1.55, .35), chamfer=.04)
    K.grille(a, (-.75, 1.19, .38), .6, .35, facing=(0, -1, 0), slats=4, parent=p)
    K.exhaust(a, (-1.1, 1.7, .7), r=.04, length=.3, direction=(0, 0, 1), parent=p, muffler=False)
    for dx in (.55, .85):
        k.lathe(a.part('Sam_reloads', 'Team', p), [(.13, -.55), (.15, -.5), (.15, .5), (.13, .55)],
                loc=(dx, 1.6, .17), rot=(0, R90, R90), seg=8)
    a.part('Sam_reloads', 'Steel', p).box((.7, .2, .06), loc=(.7, 1.6, .03), bevel=0)
    K.tone(a, 'Sam_', k=.9)


def _gun_car(a):
    p, yc = _flatcar(a, 20.97, 25.02, 'Part_gun152', 23.0)
    for s in (-1, 1):
        for y in (-1.3, 1.3):
            # The outrigger jacks stowed upright against the car's sides for the run (feet folded up).
            a.part('Gun_jacks', 'Steel', p).limb((s * 1.5, y, -.6), (s * 1.5, y, .25), .12, .12, bevel=0)
            a.part('Gun_jacks', 'Armor', p).box((.08, .36, .36), loc=(s * 1.6, y, .1), bevel=0)
    m = a.pivot('Mount_gun', (0, 0, .1), p)
    k.lathe(a.part('Gun_pedestal', 'Armor', m), [(1.0, -.1), (1.0, .05), (.8, .12), (0, .12)], seg=16, worn=(1,))
    house = a.part('Gun_shield', 'Team', m)
    for s in (-1, 1):
        k.block(house, (.08, 1.6, 1.1), loc=(s * .75, .1, .66), chamfer=.02)
        a.part('Gun_cheeks', 'Armor', m).box((.16, .7, .6), loc=(s * .4, .2, .5), bevel=.02)
    k.block(house, (1.58, .1, 1.0), loc=(0, -.68, .7), rot=(.2, 0, 0), chamfer=.02)
    elev = math.atan2(.61 - .45, 6.7 - .5)
    rot = (R90 - elev, 0, 0)
    k.lathe(a.part('Gun_barrel', 'Steel', m), [(.13, 0), (.13, .8), (.1, .9), (.085, 5.6), (0, 5.6)],
            loc=(0, -.5, .45), rot=rot, seg=12, worn=(1,))
    k.lathe(a.part('Gun_brake', 'Undercarriage', m), [(.09, 0), (.15, .04), (.15, .55), (.11, .6), (0, .6)],
            loc=(0, -6.1, .45 + 5.6 * math.sin(elev)), rot=rot, seg=12)
    k.block(a.part('Gun_cradle', 'Armor', m), (.5, 1.6, .4), loc=(0, .05, .45), chamfer=.03)
    for s in (-1, 1):
        a.part('Gun_recuperators', 'Steel', m).cyl(.08, 1.4, loc=(s * .17, -.25, .7), rot=K.FORWARD, seg=8, bevel=0)
    k.block(a.part('Gun_breech', 'Armor', m), (.4, .55, .4), loc=(0, .95, .45), chamfer=.03)
    a.pivot('Muzzle_gun', (0, -6.7, .61), m)
    a.part('Gun_band', 'Hazard', m).box((1.6, .02, .12), loc=(0, -.74, 1.05), rot=(.2, 0, 0), bevel=0)
    # Ready rounds in a rack on the car's rear end, charge cases beside them.
    rk = a.part('Gun_rack', 'Steel', p)
    rk.box((1.2, .6, .05), loc=(0, 1.65, .25), bevel=0)
    for i in range(5):
        k.lathe(a.part('Gun_rounds', 'Fuel', p), [(0, -.4), (.05, -.33), (.075, -.2), (.075, .38), (0, .4)],
                loc=(-.48 + i * .24, 1.65, .36), rot=(0, R90, R90), seg=8)
    _crates(a, (1.05, 1.5, .0), n=2, size=(.5, .6, .35), parent=p)
    K.tone(a, 'Gun_', k=.9)


def _aa_car(a):
    p, yc = _flatcar(a, 25.78, 29.83, 'Part_aa', 27.8)
    m = a.pivot('Mount_mg__002', (0, 0, .1), p)
    k.lathe(a.part('Aa_ring', 'Steel', m), [(1.0, -.1), (1.0, .02), (.9, .06), (0, .06)], seg=16)
    house = a.part('Aa_house', 'Team', m)
    k.sharp_loft(house, [[(-.6, -.8, .06), (.6, -.8, .06), (.7, .9, .06), (-.7, .9, .06)],
                         [(-.5, -.6, .7), (.5, -.6, .7), (.6, .8, .75), (-.6, .8, .75)]], chamfer=.04)
    for s in (-1, 1):
        x = s * .82
        k.block(a.part('Aa_cradles', 'Armor', m), (.26, 1.2, .38), loc=(x, -.1, .28), chamfer=.03)
        k.lathe(a.part('Aa_guns', 'Steel', m), [(.06, 0), (.06, .25), (.045, .3), (.04, 2.45), (0, 2.45)],
                loc=(x, -.7, .3), rot=(R90 - math.atan2(.06, 3.35), 0, 0), seg=8)
        a.part('Aa_brakes', 'Undercarriage', m).cyl(.06, .2, loc=(x, -3.15, .35), rot=K.FORWARD, seg=8, bevel=0)
        a.part('Aa_ammo', 'Armor', m).box((.2, .5, .35), loc=(s * 1.02, .3, .35), bevel=.02)
    a.pivot('Muzzle_mg__002', (0, -3.35, .36), m)
    a.part('Aa_steel', 'Steel', m).cyl(.05, .45, loc=(0, .75, .95), seg=6, bevel=0)
    K.dish(a.part('Aa_radar', 'Medical', m), a.part('Aa_steel', 'Steel', m), (0, .75, 1.3), r=.35,
           normal=(0, -.6, .6), seg=12)
    k.block(a.part('Aa_sight', 'Glass', m), (.18, .12, .14), loc=(.3, -.62, .7), chamfer=.015)
    for s in (-1, 1):
        a.part('Tail_lights', 'Alloy').box((.14, .04, .1), loc=(s * 1.3, 29.85, 1.25), bevel=0)
    _crates(a, (-1.0, 1.5, .0), n=3, size=(.5, .7, .28), parent=p)
    K.tone(a, 'Aa_', k=.9)


def nuke_train(a, detail=False):
    """The nuke train: see the module docstring."""
    _locomotive(a)
    _launcher_car(a)
    _rocket_car(a)
    _sam_car(a)
    _gun_car(a)
    _aa_car(a)
    K.dust(a, (0, 10, 0), radius=22, k=.12)
    k.clean(a)
    K.suffixed(a)


BUILDERS = {
    'nuke_train': (nuke_train, dict(ao_distance=.8, grime_height=.7)),
}
