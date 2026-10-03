"""Prompt 35 wave 7 (lane C): the ground drone carrier rebuilt from scratch (spec: Tools/blender/specs/ground_drone_carrier.json).

An unmanned tracked carrier on the Milrem Type-X pattern (no sheet row; the old builder drew a THeMIS / Uran-9 class
carrier with three robots on its deck; the def's modelSize 5.0 x 2.0 x 2.4 m): the low armoured hull with its sloped
nose carrying the driving cameras and lamps, side skirts, five road wheels a side with the front idler, the rear
sprocket and two return rollers, the engine grille; the remote weapon station on the front deck (`Turret`: the
turntable, the cradle, the 7.62 mm machine gun with its ammunition can, the sensor head, smoke dischargers), the
comms mast with its antennas, and the rear deck dock with three small tracked reconnaissance robots
(`Minion_1` .. `Minion_3`) behind the folding ramp.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Minion_1`, `Minion_2`, `Minion_3`,
`Hatches`, `Point_exhaust`, `Point_fire`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TX, TW = .78, .36
WR = .24
WHEELS = (-1.35, -.68, 0.0, .68, 1.36)
TOP = 1.05
NOSE, TAIL = -2.35, 2.3
TUR = (0, -1.0, TOP)


def _hull(a):
    hull = a.part('Hull', 'Team')
    C.section_loft(hull, [
        (NOSE, [(0, .48), (.55, .48), (.62, .62), (.55, .7), (0, .7)]),
        (NOSE + .55, [(0, .3), (.6, .3), (.95, .62), (.88, TOP), (0, TOP)]),
        (2.05, [(0, .3), (.6, .3), (.95, .62), (.88, TOP), (0, TOP)]),
        (TAIL, [(0, .4), (.58, .4), (.92, .62), (.84, TOP - .08), (0, TOP - .08)]),
    ])
    a.part('Hull_lower', 'Armor').box((1.2, 4.2, .2), loc=(0, -.05, .36), bevel=0)
    for s in (-1, 1):
        sk = a.part('Skirts', 'Armor')
        for j in range(3):
            K.plate(sk, (.03, 1.25, .34), loc=(s * (TX + .2), -1.3 + j * 1.3, .66), chamfer=.01)
        a.part('Team_band', 'Team').box((.012, 3.8, .06), loc=(s * (TX + .22), -.0, .76), bevel=0)
    # The nose: the driving camera pods, the lamps, tow hooks, a sensor bar.
    sen = a.part('Sensors', 'Armor')
    for s in (-1, 1):
        K.chamfer_box(sen, (.18, .14, .12), loc=(s * .42, NOSE + .25, .78), c=.02)
        a.part('Glass', 'Glass').box((.1, .01, .06), loc=(s * .42, NOSE + .175, .79), bevel=0)
        K.lamp(a, (s * .62, NOSE + .25, .7), (0, -1, .1), r=.05, guard=True)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .35, NOSE - .01, .55), facing=(0, -1, 0), size=.06)
        a.part('Tail_lamps', 'LavaGlow').box((.07, .02, .04), loc=(s * .7, TAIL + .0, .9), bevel=0)
    K.chamfer_box(sen, (.5, .12, .1), loc=(0, NOSE + .4, .86), c=.02)
    # The deck: access hatches, the engine grille amidships, the exhaust, stowage bins along the sides.
    for x in (-.4, .4):
        K.hatch_rect(a, (x, -.25, TOP), (.5, .55))
    K.grille(a, (0, .45, TOP + .02), 1.1, .45, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.exhaust(a, (.72, .6, TOP - .1), r=.05, length=.25, direction=(1, 0, .4), muffler=False, cap=False)
    a.pivot('Point_exhaust', (.88, .6, TOP))
    a.pivot('Point_fire', (0, .3, TOP + .3))
    for s in (-1, 1):
        C.stowage_box(a, (.18, .7, .2), (s * .82, -.3, TOP - .02), mat='Armor', latches=2)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(1.98, .42, .22), idler=(-1.98, .44, .21),
                       rollers=[(-.68, .66), (.68, .66)], pitch=.19, disc_mat='Armor', wheel_w=.14, seg=9,
                       teeth=11, idler_spokes=5, hide_top=(-1.7, 1.8, .64))
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .15, y, WR, length=.28, back=1, r=.035)


def _rws(a):
    """The remote weapon station on the front deck: turntable, cradle, the MG, the sensor head, smoke tubes."""
    k.lathe(a.part('Turntable', 'Armor'), [(.42, 0), (.42, .06), (.36, .1), (0, .1)], loc=TUR, seg=14, worn=(1,))
    p = C.roof_gun(a, (TUR[0], TUR[1], TUR[2] + .1), pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
                   muzzle='Muzzle_main', post=.28, length=1.0, scale=.9, shield=False, mat='Armor')
    sh = a.part('Sight', 'Armor', p)
    K.chamfer_box(sh, (.2, .28, .22), loc=(-.24, -.05, .25), c=.03)
    a.part('Glass', 'Glass', p).box((.14, .01, .1), loc=(-.24, -.195, .28), bevel=0)
    a.part('Turret_armor', 'Team', p).box((.04, .4, .2), loc=(-.36, -.0, .22), bevel=0)
    sm = a.part('Smoke_launchers', 'Armor', p)
    for j in range(3):
        sm.cyl(.035, .16, loc=(.3, -.05 + j * .09, .3), rot=(R90 - .5, 0, -.6), seg=8, bevel=0)


def _mast_and_dock(a):
    # The comms mast at the deck's rear left with its antennas.
    ms = a.part('Mast', 'Steel')
    k.lathe(ms, [(.07, 0), (.07, .05), (.035, .08), (.03, .95), (0, .95)], loc=(-.65, .95, TOP), seg=8, worn=(2,))
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.65, .95, TOP + .95), h=.4, r=.02)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (-.65, .88, TOP + .7), w=.3, h=.25, normal=(0, -1, 0), bars=3)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.65, 1.0, TOP), h=.7, r=.02)
    # The dock: rails on the rear deck, side guides, the folding ramp at the tail.
    dk = a.part('Dock', 'Armor')
    for x in (-.5, 0, .5):
        dk.box((.05, 1.15, .04), loc=(x, 1.62, TOP + .02), bevel=0)
    for s in (-1, 1):
        dk.box((.04, 1.2, .18), loc=(s * .85, 1.62, TOP + .09), bevel=0)
    rp = a.part('Ramp', 'Armor')
    K.plate(rp, (1.4, .5, .04), loc=(0, TAIL + .05, TOP - .25), rot=(-1.1, 0, 0), chamfer=.01)
    st = a.part('Kit_steel', 'Steel')
    K.hinge(st, (-.6, TAIL - .05, TOP - .03), (.6, TAIL - .05, TOP - .03), r=.025, knuckles=3)
    # Three small tracked reconnaissance robots side by side on the dock.
    for i, x in enumerate((-.52, 0, .52)):
        m = a.pivot(f'Minion_{i + 1}', (x, 1.6, TOP + .04))
        k.block(a.part('Minion_hull', 'Team', m), (.3, .78, .2), loc=(0, 0, .17), chamfer=.03, taper=(.9, .9))
        for s in (-1, 1):
            k.extrude(a.part('Minion_tracks', 'Undercarriage', m), [(-.4, .02), (.4, .02), (.44, .1), (.4, .2),
                                                                   (-.4, .2), (-.44, .1)], .08, loc=(s * .19, 0, 0),
                      axis='X', chamfer=.01)
        K.chamfer_box(a.part('Minion_head', 'Armor', m), (.16, .2, .1), loc=(0, -.2, .34), c=.02)
        a.part('Minion_eye', 'Glass', m).box((.1, .01, .05), loc=(0, -.305, .35), bevel=0)
        a.part('Minion_mast', 'Steel', m).cyl(.012, .22, loc=(.08, .25, .38), seg=4, bevel=0)


def ground_drone_carrier(a, detail=False):
    """The ground drone carrier: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _rws(a)
    _mast_and_dock(a)
    K.dust(a, (0, 0, .3), radius=2.6, k=.12)
    k.clean(a)


BUILDERS = {
    'ground_drone_carrier': (ground_drone_carrier, dict(ao_distance=.45, grime_height=.45)),
}
