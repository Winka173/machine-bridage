"""Prompt 35 wave 9 (lane C): the mobile repair vehicle rebuilt from scratch (spec:
Tools/blender/specs/mobile_repair_vehicle.json).

A BREM-K-class armoured repair and recovery vehicle on the BTR-80 8x8 hull (balance.json: the MTO-UB-class
repair vehicle, slow, wide-reaching repair; drawn as the armoured BREM-K so it reads as a front-line repair unit,
the def's modelSize 6.45 x 3.02 x 2.02 m): the boat-shaped hull with its sloped upper plates, the bow's trim vane
and the driver's vision blocks, four axles on big tyres with their wheel arches and suspension arms, the folded
crane jib along the roof on its slewing base with the hook block, the bow winch with its cable, the spade at the
rear, tow bars, toolboxes and the welding set's gas bottles on the sponsons, the roof hatches, the self-defence
12.7 mm on its post on the commander's cupola (`Turret`, the def's main hmg_selfdef_15), whips and lamps.

Runtime nodes kept: `Turret`, `Muzzle_main` (the roof gun's), `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y
front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .47
AXLES = (-2.25, -.95, .9, 2.2)
TX = 1.1
NOSE, TAIL = -3.2, 3.2
TOP = 1.62


def _hull(a):
    hull = a.part('Hull', 'Team')

    def sec(lw, lz, sw, sz, tw):
        return [(0, lz), (lw, lz), (sw, sz - .2), (sw, sz), (tw, TOP), (0, TOP)]
    C.section_loft(hull, [
        (NOSE, sec(.5, .75, .9, 1.0, .8)),
        (NOSE + .7, sec(.8, .45, 1.28, 1.1, 1.0)),
        (TAIL - .5, sec(.8, .45, 1.28, 1.1, 1.0)),
        (TAIL, sec(.65, .6, 1.15, 1.05, .9)),
    ])
    # The trim vane on the bow, the driver's and commander's vision blocks, lamps, tow hooks.
    K.plate(a.part('Trim_vane', 'Armor'), (1.6, .45, .03), loc=(0, NOSE + .22, 1.12), rot=(-.5, 0, 0), chamfer=.01)
    for s in (-1, 1):
        for x in (.2, .45):
            a.part('Visors', 'Glass').box((.16, .02, .08), loc=(s * x, NOSE + .62, 1.5), rot=(-.6, 0, 0), bevel=0)
        K.lamp(a, (s * .7, NOSE + .2, 1.2), (0, -1, .1), r=.06, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .02, .78), facing=(0, -1, 0), size=.07)
        a.part('Tail_lamps', 'Lamp').box((.08, .02, .06), loc=(s * .8, TAIL + .005, 1.2), bevel=0)
    for x in (-.35, .35):
        C.hatch(a, (x, NOSE + 1.15, TOP), r=.22)
    K.grille(a, (0, 2.3, TOP + .01), 1.2, .8, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.exhaust(a, (-1.05, 2.4, 1.3), r=.05, length=.3, direction=(-1, 0, .3))
    a.pivot('Point_exhaust', (-1.3, 2.4, 1.4))
    a.pivot('Point_fire', (0, .8, TOP + .3))


def _running_gear(a):
    ax = a.part('Axles', 'Undercarriage')
    for i, y in enumerate(AXLES):
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .34, s, seg=12)
            a.part('Suspension', 'Undercarriage').limb((s * .55, y + .15, .6), (s * (TX - .15), y, WR), .05, .05,
                                                       bevel=0)
            arch = a.part('Wheel_arches', 'Armor')
            arch.box((.3, 1.0, .03), loc=(s * (TX + .02), y, WR * 2 + .08), bevel=0)
        if i in (0, 2):
            ax.box((1.0, .2, .2), loc=(0, (y + AXLES[i + 1]) / 2, .55), bevel=0)


def _crane(a):
    """The crane on its slewing base at the rear, the jib folded forward along the roof, the hook block."""
    k.lathe(a.part('Crane_base', 'Armor'), [(.4, 0), (.4, .12), (.32, .18), (0, .2)], loc=(.55, 1.9, TOP), seg=12)
    jb = a.part('Crane', 'CraneYellow')
    k.extrude(jb, [(-.12, -.12), (.12, -.12), (.1, .12), (-.1, .12)], 3.3, loc=(.55, .35, TOP + .35),
              rot=(-.03, 0, 0), axis='Y', chamfer=.015)
    jb.limb((.55, 1.9, TOP + .18), (.55, 1.6, TOP + .45), .14, .12, bevel=0)
    a.part('Crane_ram', 'Steel').limb((.55, 1.4, TOP + .2), (.55, .6, TOP + .4), .05, .06, bevel=0)
    a.part('Crane_rest', 'Steel').box((.4, .1, .3), loc=(.55, -1.3, TOP + .15), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((.26, .5, .02), loc=(.55, -1.2, TOP + .48), bevel=0)
    hk = a.part('Hook_block', 'Steel')
    k.block(hk, (.14, .1, .18), loc=(.55, -1.4, TOP + .2), chamfer=.015)
    a.part('Kit_cables', 'Undercarriage').tube([(.55, -1.35, TOP + .45), (.55, -1.4, TOP + .3)], .012, seg=4)


def _kit(a):
    """Bow winch, rear spade, tow bars, toolboxes, gas bottles, roof gun, whips."""
    wn = a.part('Winch', 'Steel')
    k.lathe(wn, [(.14, -.35), (.14, .35)], loc=(0, NOSE + .3, .8), rot=(0, R90, 0), seg=10)
    a.part('Tow_cable', 'Undercarriage').tube([(-.2, NOSE + .25, .9), (-.15, NOSE - .02, .78)], .02, seg=4)
    k.block(a.part('Spade', 'Steel'), (1.8, .14, .5), loc=(0, TAIL + .1, .55), rot=(-.25, 0, 0), chamfer=.02)
    for s in (-1, 1):
        a.part('Spade_rams', 'Steel').limb((s * .7, TAIL - .2, 1.0), (s * .7, TAIL + .05, .6), .04, .05, bevel=0)
        a.part('Tow_bars', 'Steel').limb((s * 1.25, -1.6, TOP - .38), (s * 1.25, 1.6, TOP - .38), .04, .04, bevel=0)
        C.stowage_box(a, (.28, .9, .3), (s * 1.37, .0, 1.0), mat='Team', latches=2)
    gb = a.part('Gas_bottles', 'BarrelRed')
    for j in range(2):
        k.lathe(gb, [(.0, 0), (.1, .02), (.11, .1), (.11, .75), (.06, .85), (0, .86)], loc=(-1.36, 1.55 + j * .25, .95),
                seg=8)
    a.part('Kit_straps', 'Steel').box((.06, .6, .04), loc=(-1.42, 1.67, 1.4), bevel=0)
    C.ammo_tins(a, (-1.37, -1.4, 1.0), n=3, size=(.12, .26, .2), axis='Y')
    C.jerry_rack(a, (1.38, 1.6, 1.0), count=2, axis='Y')
    # The commander's cupola and the 12.7 mm on its post (the def's main weapon).
    k.lathe(a.part('Cupola', 'Armor'), [(.36, 0), (.36, .1), (.3, .16), (0, .17)], loc=(-.45, -.35, TOP), seg=12)
    C.roof_gun(a, (-.45, -.35, TOP + .17), pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
               muzzle='Muzzle_main', post=.08, length=1.0, scale=.8, shield=True, mat='Team')
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.95, 2.7, TOP), h=.4, r=.012)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.95, 2.7, TOP), h=.35, r=.012)


def mobile_repair_vehicle(a, detail=False):
    """The BREM-K-class repair vehicle: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _crane(a)
    _kit(a)
    K.dust(a, (0, 0, .3), radius=3.2, k=.14)
    k.clean(a)


BUILDERS = {
    'mobile_repair_vehicle': (mobile_repair_vehicle, dict(ao_distance=.4, grime_height=.45)),
}
