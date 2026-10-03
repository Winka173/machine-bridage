"""Prompt 35 wave 4 (lane C): the flame tank rebuilt from scratch (spec: Tools/blender/specs/flame_tank.json).

A TO-55 on the T-55 hull, the gun replaced by a short, thick flame projector as on the M67 "Zippo" (the def's
modelSize 7.12 x 2.66 x 1.87 m): the T-55's sloped upper glacis with the splash board, the flat engine deck with
its louvres, five large road wheels a side with no return rollers, the front idler and the rear sprocket; the
cast dome turret set forward with the commander's cupola on the left, the loader's hatch and the DShK on its ring
on the right, the L-2 searchlight beside the projector and the Tucha smoke dischargers (T-55AM); two armoured
flame-fuel tanks, dark red, lying across the rear deck in cradles; fender stowage, the unditching log and the
200 l drums on the rear plate; rubber side skirts (T-55AM).

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_brake_glow`, `Muzzle_main`, `Coax`,
`Muzzle_coax`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = 1.04, .5          # track centre line, belt width
WR = .345                  # road wheel radius (the T-55's big wheels)
WHEELS = (-2.12, -1.18, -.26, .68, 1.62)
DECK = .98
HALF = 1.0                 # upper hull half width (the fenders reach 1.33)
NOSE, TAIL = -3.3, 3.22
TUR = (0, -.68, DECK)      # turret ring centre


def _hull(a):
    hull = a.part('Hull', 'Team')
    # Side profile: lower glacis, the long upper glacis, the flat deck, the sloped rear plate, the belly.
    prof = [(NOSE, .62), (-2.25, DECK), (2.86, DECK), (TAIL, .88), (TAIL - .08, .46), (-2.9, .38)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.05, corner=.03)
    low = a.part('Hull_lower', 'Armor')
    k.extrude(low, [(NOSE + .2, .62), (-2.8, .34), (2.95, .34), (3.0, .7)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    # Fenders over the tracks, their front mud guards turned down, the rubber skirts below (T-55AM).
    fen = a.part('Fenders', 'Team')
    for s in (-1, 1):
        K.fender(fen, TX, NOSE + .1, TAIL - .02, .94, .5, s, lip=.03)
        fen.box((.5, .05, .22), loc=(s * TX, NOSE + .1, .84), rot=(-.4, 0, 0), bevel=0)
        sk = a.part('Skirts', 'Rubber')
        for j in range(5):
            sk.box((.025, .98, .14), loc=(s * (TX + .24), -2.08 + j * 1.04, .87), bevel=0)
        a.part('Team_band', 'Team').box((.01, 2.2, .08), loc=(s * (HALF + .006), .9, DECK - .1), bevel=0)
    # The splash board across the upper glacis, the driver's hatch on the left, lamps with guards, tow hooks.
    g0, g1 = Vector((0, NOSE, .66)), Vector((0, -2.25, DECK))
    d = (g1 - g0).normalized()
    ang = math.atan2(d.z, -d.y)
    board = a.part('Deck_plates', 'Armor')
    c = g0 + d * .55
    board.box((HALF * 1.7, .05, .09), loc=(0, c.y - .02, c.z + .05), rot=(ang - R90 * .4, 0, 0), bevel=0)
    dh = a.part('Hatches', 'Armor')
    k.lathe(dh, [(0, .07), (.22, .065), (.26, .04), (.26, 0)], loc=(.48, -2.0, DECK), seg=12, worn=(2,))
    K.periscope(a, (.48, -2.3, DECK + .02), facing=(0, -1, 0), size=(.16, .08, .07))
    for s in (-1, 1):
        K.lamp(a, (s * .78, -2.55, .98), (0, -1, .2), r=.07, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .55, NOSE - .02, .52), facing=(0, -1, 0), size=.08)
    K.lamp(a, (-.62, -2.5, 1.03), (0, -1, .1), r=.05, guard=False, glow='Glass')   # the IR driving light
    # The engine deck: radiator louvres across the rear, the access plates, the exhaust louvre on the left fender.
    K.grille(a, (0, 2.3, DECK + .02), 1.5, .7, facing=(0, 0, 1), slats=7, frame_mat='Team')
    K.grille(a, (0, 1.45, DECK + .02), 1.1, .45, facing=(0, 0, 1), slats=4, frame_mat='Team')
    pl = a.part('Deck_plates', 'Armor')
    for y in (.55, .95):
        K.plate(pl, (.7, .32, .02), loc=(-.45, y, DECK + .01))
    K.rivet_line(a.part('Kit_steel', 'Steel'), (-.8, .38, DECK + .02), (-.8, 1.15, DECK + .02), (0, 0, 1),
                 pitch=.12, r=.014)
    K.grille(a, (HALF + .2, 1.7, .97), .4, .16, facing=(0, 0, 1), slats=3, frame_mat='Armor')
    a.pivot('Point_exhaust', (HALF + .2, 1.75, 1.0))
    a.pivot('Point_fire', (0, 1.6, DECK + .3))


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.78, .5, .29), idler=(-2.94, .5, .27), rollers=(),
                       pitch=.3, hide_top=(-2.6, 2.6, .78), disc_mat='Armor', wheel_w=.19, seg=10, teeth=11)
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .2, y, WR, length=.4, back=1)


def _rear(a):
    # The two armoured flame-fuel tanks across the rear deck in their cradles (dark red), their filler caps and
    # the pressure line forward to the turret.
    tanks = a.part('Fuel_tanks', 'BarrelRed')
    cr = a.part('Deck_plates', 'Armor')
    for y in (2.15, 2.72):
        k.lathe(tanks, [(.2, -.95), (.25, -.92), (.27, -.85), (.27, .85), (.25, .92), (.2, .95)],
                loc=(0, y, DECK + .32), rot=(0, R90, 0), seg=14, worn=(2, 3))
        for x in (-.6, 0, .6):
            cr.box((.08, .5, .1), loc=(x, y, DECK + .05), bevel=0)
            a.part('Kit_steel', 'Steel').cyl(.285, .05, loc=(x, y, DECK + .32), rot=(0, R90, 0), seg=10, bevel=0)
        a.part('Fuel_caps', 'Steel').cyl(.06, .05, loc=(.75, y, DECK + .6), seg=8, bevel=0)
    a.part('Kit_cables', 'Undercarriage').tube([(-.5, 2.0, DECK + .5), (-.6, 1.4, DECK + .25), (-.5, .2, DECK + .1)],
                                               .03, seg=5)
    # The unditching log and the two 200 l drums on the rear plate.
    k.lathe(a.part('Log', 'Wood'), [(.1, -1.0), (.12, -.97), (.12, .97), (.1, 1.0)], loc=(0, TAIL + .1, .95),
            rot=(0, R90, 0), seg=8)
    for x in (-.55, .55):
        K.fuel_drum(a.part('Drums', 'Fuel'), a.part('Kit_steel', 'Steel'), (x, TAIL + .12, .55), r=.2, h=.62,
                    lying=True)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .05), loc=(s * .9, TAIL - .02, .95), bevel=0)


def _fenders(a):
    # Right fender: the external fuel cells; left: stowage bins, the tool box, the jerrycans.
    cells = a.part('Fuel_cells', 'Armor')
    for y in (-1.2, -.5, .2):
        K.chamfer_box(cells, (.5, .6, .34), loc=(-TX, y, .95), c=.04)
        a.part('Fuel_caps', 'Steel').cyl(.045, .04, loc=(-TX, y - .18, 1.31), seg=8, bevel=0)
    a.part('Kit_cables', 'Undercarriage').tube([(-TX, -1.5, 1.2), (-TX, .5, 1.2)], .02, seg=4)
    C.stowage_box(a, (.5, .9, .3), (TX + .04, -1.2, .95), mat='Armor', latches=2)
    C.stowage_box(a, (.5, .55, .26), (TX + .04, -.3, .95), mat='Armor', latches=1)
    C.cable_reel(a, (TX + .04, 1.25, 1.17), r=.2, w=.34, axis='Y')


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), TUR, 1.0, h=.06)
    body = a.part('Turret_body', 'Team', t)
    # The cast dome, a little longer than wide (the T-55's), the cheeks fuller at the front.
    k.lathe(body, [(1.02, 0), (1.06, .06), (1.02, .18), (.88, .34), (.6, .47), (.25, .52), (0, .53)], seg=22,
            worn=(1, 2))
    # The thick front casting band and the mantlet slot cover.
    k.ring(body, [(1.03, .05), (1.1, .1), (1.1, .2), (1.03, .26)], seg=22, worn=(1, 2))
    man = a.part('Mantlet', 'Armor', t)
    k.lathe(man, [(.34, 0), (.36, .1), (.3, .22), (.16, .27), (0, .28)], loc=(0, -.95, .26), rot=K.FORWARD, seg=14,
            worn=(1,))
    # The flame projector: a thick jacketed tube, its clamping bands, the nozzle (`Muzzle_brake`) with the pilot
    # flame ring (`Muzzle_brake_glow`).
    tube = a.part('Main_cannon', 'Steel', t)
    k.lathe(tube, [(.15, 0), (.15, .5), (.13, .58), (.12, 1.15), (0, 1.15)], loc=(0, -1.15, .26), rot=K.FORWARD,
            seg=12, worn=(1, 2))
    for j in range(3):
        a.part('Mantlet_bands', 'Armor', t).cyl(.165, .06, loc=(0, -1.3 - j * .2, .26), rot=K.FORWARD, seg=14,
                                                     bevel=0)
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.12, 0), (.15, .06), (.15, .2), (.09, .3), (.06, .3),
                                                         (.06, .24), (0, .24)], loc=(0, -2.28, .26), rot=K.FORWARD,
            seg=14, worn=(1, 2))
    a.part('Muzzle_brake_glow', 'LavaGlow', t).torus(.075, .022, loc=(0, -2.59, .26), rot=K.FORWARD, seg=12, ring=4)
    a.pivot('Muzzle_main', (0, -2.62, .26), t)
    # The coaxial machine gun beside the projector (`Coax`), the gunner's sight aperture, the L-2 searchlight.
    co = a.pivot('Coax', (-.3, -1.0, .26), t)
    a.part('MG_coax', 'Steel', co).cyl(.022, .5, loc=(0, -.25, 0), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_coax', (0, -.5, 0), co)
    k.block(a.part('Sight', 'Armor', t), (.18, .16, .14), loc=(.42, -.82, .42), chamfer=.02)
    a.part('Glass', 'Glass', t).box((.12, .01, .06), loc=(.42, -.905, .49), bevel=0)
    lt = a.part('Searchlight', 'Armor', t)
    k.lathe(lt, [(0, -.12), (.17, -.1), (.19, 0), (.19, .14), (.16, .16)], loc=(-.55, -.8, .5), rot=K.FORWARD,
            seg=12, worn=(2,))
    a.part('Glass', 'Glass', t).cyl(.15, .01, loc=(-.55, -.97, .5), rot=K.FORWARD, seg=12, bevel=0)
    a.part('Kit_steel', 'Steel', t).limb((-.55, -.8, .38), (-.25, -1.15, .26), .02, .02, bevel=0)
    # The commander's cupola on the left with periscopes and its hatch, the loader's hatch on the right with the
    # DShK on its ring mount (raised: the owner's roof-gun rule).
    cup = a.part('Cupola', 'Armor', t)
    k.ring(cup, [(.3, .42), (.36, .42), (.36, .54), (.31, .58)], seg=14, worn=(2,), loc=(.42, .05, 0))
    k.lathe(cup, [(0, .63), (.26, .61), (.31, .58)], loc=(.42, .05, 0), seg=14)
    for i in range(3):
        u = -R90 + (i - 1) * .6
        K.periscope(a, (.42 + math.cos(u) * .34, .05 + math.sin(u) * .34, .5), facing=(math.cos(u), math.sin(u), 0),
                    parent=t, size=(.1, .08, .07))
    C.hatch(a, (-.42, .12, .46), r=.25, parent=t, periscope=True)
    ring = a.part('MG_dshk', 'Steel', t)
    k.ring(ring, [(.34, .5), (.38, .5), (.38, .54), (.34, .54)], loc=(-.42, .12, 0), seg=14)
    for u in (0, R90 * 2):
        ring.box((.03, .03, .12), loc=(-.42 + math.cos(u) * .36, .12, .48), bevel=0)
    mg = a.part('MG_dshk', 'Steel', t)
    mg.limb((-.42, .4, .54), (-.42, .3, .7), .03, .03, bevel=0)                      # the cradle post
    k.extrude(mg, [(-.2, -.06), (.22, -.06), (.24, .05), (-.2, .06)], .12, loc=(-.42, .25, .72), axis='X',
              chamfer=.01)
    k.lathe(mg, [(.04, 0), (.04, .2), (.028, .24), (.025, 1.0), (.04, 1.02), (.04, 1.12), (0, 1.12)],
            loc=(-.42, .05, .72), rot=K.FORWARD, seg=8, worn=(1,))
    k.block(a.part('MG_ammo', 'Crate', t), (.12, .26, .2), loc=(-.27, .2, .56), chamfer=.012)
    # Tucha smoke dischargers either side of the turret front, the snorkel stowed on the turret rear, a stowage
    # bin round the rear, aerials, the team band.
    for s in (-1, 1):
        sp = a.part('Smoke_launchers', 'Armor', t)
        for j in range(4):
            sp.cyl(.04, .2, loc=(s * (.72 + j * .06), -.58 - j * .1, .38), rot=(R90 - .5, 0, s * .4), seg=8, bevel=0)
        a.part('Smoke_brackets', 'Steel', t).box((.3, .06, .06), loc=(s * .8, -.68, .3), rot=(0, 0, s * .6), bevel=0)
    k.lathe(a.part('Snorkel', 'Armor', t), [(.09, -.7), (.11, -.68), (.11, .68), (.09, .7)], loc=(0, .98, .28),
            rot=(0, R90, 0), seg=10)
    for x in (-.5, .5):
        a.part('Kit_steel', 'Steel', t).box((.04, .2, .02), loc=(x, .98, .4), bevel=0)
    stow = a.part('Stowage', 'Canvas', t)
    stow.box((.9, .3, .22), loc=(.55, .72, .26), rot=(0, 0, -.5), bevel=.04)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.6, .55, .4), h=.3)
    a.part('Team_band', 'Team', t).cyl(1.065, .07, loc=(0, 0, .14), seg=22, bevel=0)
    K.rivet_line(a.part('Kit_steel', 'Steel', t), (-.5, -.95, .44), (.3, -.95, .44), (0, -.4, 1), pitch=.1, r=.012)


def flame_tank(a, detail=False):
    """The flame tank: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _rear(a)
    _fenders(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.5, k=.12)
    k.clean(a)


BUILDERS = {
    'flame_tank': (flame_tank, dict(ao_distance=.5, grime_height=.5)),
}
