"""Prompt 35 wave 7 (lane C): the scout jeep rebuilt from scratch (spec: Tools/blender/specs/scout_jeep.json).

An M151A2 MUTT with a WMIK-style gun pedestal (unit_refs: M151 MUTT, Land Rover WMIK, M2 Browning; the sheet: a small
open 4x4 with a roll cage, the machine gun on a post in the middle and fuel cans at the back, "the smallest in the
game, the driver and the gun clearly seen"; the def's modelSize 2.64 x 1.4 x 1.41 m): the open steel tub with its
flat hood, the slotted grille between the front fenders and their lamps, the fold-down windscreen frame with glass,
the roll cage over the crew, four lugged wheels on their axles with coil springs, the spare wheel on the tail; the
seats with the driver at the wheel; the M2 on its pedestal post in the middle (`Turret`: cradle, ammunition can,
shield; MODEL_STANDARD "Roof guns"); jerrycans in the rear rack, the radio and its whip, tail lamps.

Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Point_exhaust`, `Point_fire` (the wrapper
adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .29
AX = (-.82, .78)
TRACK = .56
FLOOR = .5


def _body(a):
    tub = a.part('Body', 'Team')
    # The tub: flat sides with the M151's slight flare, the rear panel, open top (a floor and the side walls).
    k.extrude(tub, [(-.38, FLOOR), (1.15, FLOOR), (1.18, .9), (-.38, .9)], 1.24, axis='X', chamfer=.02)
    hood = a.part('Body', 'Team')                  # the hood (one Body mesh with the tub)
    C.section_loft(hood, [
        (-1.32, [(0, .55), (.47, .55), (.47, .7), (.38, .76), (0, .76)]),
        (-1.24, [(0, .55), (.5, .55), (.5, .75), (.4, .84), (0, .85)]),
        (-.38, [(0, .55), (.53, .55), (.53, .8), (.43, .9), (0, .91)]),
    ])
    for s in (-1, 1):
        fn = a.part('Fenders', 'Team')
        k.extrude(fn, [(-1.3, .66), (-.42, .66), (-.48, .8), (-1.25, .8)], .2, loc=(s * .6, 0, 0), axis='X',
                  chamfer=.01)
        K.lamp(a, (s * .55, -1.31, .74), (0, -1, 0), r=.055, guard=False)
        a.part('Team_band', 'Team').box((.012, 1.2, .05), loc=(s * .625, .38, .78), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.06, .02, .05), loc=(s * .52, 1.185, .82), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .625, .2, .86), (s * .625, .45, .86), (s, 0, 0), h=.03, r=.01)
    # The slotted grille, the bumper with tow hooks, the hood latches, the mirror.
    K.grille(a, (0, -1.29, .7), .7, .22, facing=(0, -1, .1), slats=5, frame_mat='Team')
    bp = a.part('Bumper', 'Steel')
    bp.box((1.3, .08, .1), loc=(0, -1.36, .55), bevel=0)
    for s in (-1, 1):
        K.tow_hook(bp, (s * .4, -1.4, .55), facing=(0, -1, 0), size=.05)
        a.part('Kit_steel', 'Steel').box((.04, .06, .03), loc=(s * .45, -.7, .9), bevel=0)
    K.mirror(a.part('Kit_steel', 'Steel'), (-.62, -.42, .9), -1, arm=.08, size=(.08, .02, .1))
    # The windscreen frame up with its glass, the roll cage over the crew.
    wf = a.part('Windscreen_frame', 'Team')
    sq = [(-.015, -.015), (.015, -.015), (.015, .015), (-.015, .015)]
    k.sweep(wf, sq, [(-.58, -.4, .9), (-.58, -.3, 1.3), (.58, -.3, 1.3), (.58, -.4, .9)])
    a.part('Glass', 'Glass').box((1.1, .01, .36), loc=(0, -.35, 1.1), rot=(-.25, 0, 0), bevel=0)
    rc = a.part('Roll_cage', 'Steel')
    for s in (-1, 1):
        rc.tube([(s * .58, .05, .9), (s * .55, .1, 1.38), (s * .55, .55, 1.38), (s * .58, 1.05, .9)], .025, seg=6,
                caps=False)
    rc.tube([(-.55, .1, 1.38), (.55, .1, 1.38)], .025, seg=6)
    rc.tube([(-.55, .55, 1.38), (.55, .55, 1.38)], .022, seg=6)
    # Seats, the steering wheel and the driver (left-hand drive: +X).
    st = a.part('Seats', 'Canvas')
    for x in (-.3, .3):
        st.box((.38, .38, .08), loc=(x, -.05, .65), bevel=.02)
        st.box((.38, .07, .4), loc=(x, .15, .85), rot=(-.15, 0, 0), bevel=.02)
    sw = a.part('Steering', 'Rubber')
    sw.torus(.13, .015, loc=(.3, -.35, .98), rot=(1.1, 0, 0), seg=10, ring=4)
    sw.limb((.3, -.35, .98), (.3, -.5, .8), .015, .015, bevel=0)
    cr = a.part('Crew', 'Canvas')
    cr.limb((.3, .02, .72), (.3, .08, 1.08), .13, .15, bevel=0)                      # torso
    for s in (-1, 1):
        cr.limb((.3 + s * .15, .05, 1.02), (.3 + s * .12, -.28, .97), .04, .035, bevel=0)   # arms
        cr.limb((.3 + s * .09, -.05, .7), (.3 + s * .1, -.45, .7), .06, .05, bevel=0)      # thighs
    a.part('Crew_head', 'Plaster').sphere(.09, loc=(.3, .05, 1.2), seg=10, rings=6)
    k.lathe(a.part('Crew_helmet', 'Armor'), [(.11, 0), (.115, .03), (.1, .09), (.05, .13), (0, .14)],
            loc=(.3, .05, 1.2), seg=10)


def _chassis(a):
    ax = a.part('Axles', 'Undercarriage')
    for y in AX:
        K.axle(ax, y, WR, TRACK - .1, r=.05)
        for s in (-1, 1):
            C.lugged_tyre(a, (s * TRACK, y, WR), WR, .2, s, lugs=9, seg=12, nuts=5)
            ax.cyl(.045, .2, loc=(s * .4, y, WR + .2), seg=6, bevel=0)                 # coil spring stand-off
    a.part('Undercarriage', 'Undercarriage').box((.5, 2.2, .1), loc=(0, -.05, .45), bevel=0)
    # The spare wheel on the tail, the exhaust under the right side.
    # The spare wheel lies on the bonnet (WMIK style), strapped down.
    r, w = .25, .15
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(r * .6, -w / 2), (r * .93, -w / 2), (r, -w * .3), (r, w * .3),
                                              (r * .93, w / 2), (r * .6, w / 2)], loc=(0, -.85, .91 + w / 2), seg=14,
            worn=(2, 3))
    k.lathe(a.part('Spare_wheel_rim', 'Steel'), [(r * .62, w / 2 - .01), (r * .5, w / 2 - .04), (r * .2, w / 2 - .04),
                                                 (0, w / 2 - .03)], loc=(0, -.85, .91 + w / 2), seg=10)
    a.part('Kit_straps', 'Steel').box((.04, .55, .02), loc=(0, -.85, .91 + w + .005), bevel=0)
    a.part('Exhaust', 'Steel').cyl(.025, .4, loc=(-.45, .95, .42), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Point_exhaust', (-.45, 1.17, .42))
    a.pivot('Point_fire', (0, .1, .9))


def _gun(a):
    """The M2 on its pedestal post in the rear middle (the main weapon)."""
    k.block(a.part('Gun_base', 'Steel'), (.3, .3, .05), loc=(0, .65, FLOOR + .03), chamfer=.01)
    C.roof_gun(a, (0, .65, FLOOR + .05), pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
               muzzle='Muzzle_main', post=.5, length=1.15, scale=.9, shield=True, mat='Armor')
    # Jerrycans in the rear rack, the radio box, the whip.
    C.jerry_rack(a, (.42, .95, FLOOR + .02), count=1, axis='X')
    C.jerry_rack(a, (-.42, .95, FLOOR + .02), count=1, axis='X')
    k.block(a.part('Radio', 'Armor'), (.25, .2, .2), loc=(-.35, .4, FLOOR + .12), chamfer=.015)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.5, 1.1, .9), h=.45, r=.02)


def scout_jeep(a, detail=False):
    """The scout jeep: see the module docstring."""
    _body(a)
    _chassis(a)
    _gun(a)
    K.dust(a, (0, 0, .2), radius=1.6, k=.14)
    k.clean(a)


BUILDERS = {
    'scout_jeep': (scout_jeep, dict(ao_distance=.3, grime_height=.35)),
}
