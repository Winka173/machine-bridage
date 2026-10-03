"""Prompt 35 wave 9 (lane C): the Iron Beam laser vehicle rebuilt from scratch (spec: Tools/blender/specs/iron_beam.json).

A truck-mounted Iron Beam (unit_refs: Rafael Iron Beam, 100 kW laser; the def's hel_beam and APS with no shells:
laser air defence, no gun barrel; drawn as the mobile Iron Beam-M on an 8x8 tactical truck, the def's modelSize
8.2 x 2.05 x 2.86 m): the short cab-forward cab with its flat windscreen, doors and mirrors, the grille, bumper and
lamps; four axles on lugged tyres, wings and mud flaps; the equipment shelter on the bed (side doors, lockers, the
power unit's grilles and its exhaust, the chiller's fans on the roof, cable runs); the search radar's flat face on
its mast at the shelter's front (`Radar`); on the shelter's rear the beam director (`Turret`): the turntable, the
yoke and the big round telescope (`Main_cannon`) with its glowing aperture (`Main_cannon_lens`), the tracker's
sensor box and window beside it; whips, toolboxes, the spare wheel.

Runtime nodes kept: `Turret`, `Muzzle_main` (the aperture's centre), `Radar`, `Point_exhaust`, `Point_fire`;
`Mount_APS` added (the def's APS: the laser kills rockets). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .5
AXLES = (-2.85, -1.6, 1.4, 2.65)
TX = .73
FZ = .95
NOSE, TAIL = -4.1, 4.1
SH0, SH1 = -2.2, 4.0      # the shelter's ends
SH_TOP = 2.15


def _cab(a):
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (NOSE, [(0, FZ - .15), (.98, FZ - .15), (1.0, 1.45), (.95, 1.5), (0, 1.5)]),
        (NOSE + .45, [(0, FZ - .15), (1.0, FZ - .15), (1.02, 1.5), (.82, 2.45), (0, 2.48)]),
        (NOSE + 1.75, [(0, FZ - .15), (1.0, FZ - .15), (1.02, 1.5), (.84, 2.5), (0, 2.52)]),
    ])
    K.windscreen(a, [(-.86, NOSE + .05, 1.58), (.86, NOSE + .05, 1.58), (.72, NOSE + .4, 2.38), (-.72, NOSE + .4, 2.38)],
                 frame_mat='Team', wipers=2)
    for s in (-1, 1):
        a.part('Glass', 'Glass').box((.01, .6, .38), loc=(s * .94, NOSE + 1.0, 2.0), rot=(0, s * .2, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        dr.box((.012, .02, .7), loc=(s * 1.025, NOSE + 1.35, 1.3), bevel=0)
        dr.box((.012, .02, .7), loc=(s * 1.025, NOSE + .62, 1.3), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * 1.03, NOSE + 1.1, 1.5), (s * 1.03, NOSE + 1.2, 1.5), (s, 0, 0),
                 h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .95, NOSE + .2, 1.95), s, arm=.06, size=(.04, .02, .16))
        K.lamp(a, (s * .72, NOSE - .01, 1.15), (0, -1, 0), r=.07, guard=True)
        a.part('Steps', 'Steel').box((.08, .4, .03), loc=(s * .98, NOSE + 1.0, .62), bevel=0)
    K.grille(a, (0, NOSE - .01, 1.15), .9, .35, facing=(0, -1, 0), slats=5, frame_mat='Steel')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (2.0, .12, .2), loc=(0, NOSE - .02, FZ - .25), c=.03)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .07, FZ - .3), facing=(0, -1, 0), size=.07)
    # The engine box behind the cab, its exhaust stack.
    eng = a.part('Hull', 'Team')
    C.slab_loft(eng, C.octagon(2.0, .5, .05, y0=NOSE + 2.0), C.octagon(1.5, .36, .05, y0=NOSE + 2.0), FZ, 2.1)
    K.exhaust(a, (.85, NOSE + 2.05, 2.0), r=.06, length=.55, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (.85, NOSE + 2.05, 2.6))


def _chassis(a):
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.15, 7.8, .26), loc=(s * .42, .1, FZ - .13), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for i, y in enumerate(AXLES):
        K.axle(ax, y, WR, TX - .1, r=.06, diff=i in (0, 2))
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .36, s, seg=12)
    wing = a.part('Mud_wings', 'Team')
    for y0, y1 in ((AXLES[0], AXLES[1]), (AXLES[2], AXLES[3])):
        for s in (-1, 1):
            wing.box((.42, y1 - y0 + 1.15, .04), loc=(s * (TX + .02), (y0 + y1) / 2, WR * 2 + .08), bevel=0)
            a.part('Mudflaps', 'Rubber').box((.36, .02, .3), loc=(s * (TX + .02), y1 + .62, .55), bevel=0)
    for s in (-1, 1):
        C.stowage_box(a, (.28, .9, .3), (s * .9, -.1, FZ - .5), mat='Team', latches=2)
        a.part('Tail_lamps', 'Lamp').box((.1, .02, .07), loc=(s * .85, TAIL - .02, FZ), bevel=0)
    K.tread_wheel(a, (-.9, .85, FZ - .15), .4, .26, -1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    a.pivot('Point_fire', (0, 1.0, SH_TOP))


def _shelter(a):
    sh = a.part('Body', 'Team')
    C.slab_loft(sh, C.octagon(2.0, SH1 - SH0, .08, y0=(SH0 + SH1) / 2),
                C.octagon(1.62, SH1 - SH0 - .3, .1, y0=(SH0 + SH1) / 2), FZ + .05, SH_TOP,
                mid=(C.octagon(2.0, SH1 - SH0, .08, y0=(SH0 + SH1) / 2), SH_TOP - .32))
    K.door(a, (1.005, -.7, FZ + .15), size=(.65, 1.0), normal=(1, 0, 0), mat='Team')
    K.door(a, (0, SH1 + .005, FZ + .15), size=(.7, 1.05), normal=(0, 1, 0), mat='Team')
    for s in (-1, 1):
        K.grille(a, (s * 1.005, 2.6, FZ + .65), 1.0, .45, facing=(s, 0, 0), slats=6, frame_mat='Team')
        lk = a.part('Lockers', 'Armor')
        lk.box((.02, .7, .5), loc=(s * 1.005, .9, FZ + .55), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * 1.012, .8, FZ + .55), (s * 1.012, 1.0, FZ + .55), (s, 0, 0),
                 h=.025, r=.01)
    st = a.part('Kit_steel', 'Steel')
    for y in (-1.2, .3, 1.8, 3.3):
        for s in (-1, 1):
            st.box((.02, .04, .9), loc=(s * 1.01, y, FZ + .5), bevel=0)
    # The chiller's two fans on the roof, cable runs, the whips.
    for y in (.0, .95):
        k.block(a.part('Fan_housings', 'Armor'), (.7, .7, .18), loc=(0, y, SH_TOP + .09), chamfer=.03)
        k.ring(a.part('Fan_grilles', 'Steel'), [(.24, SH_TOP + .18), (.28, SH_TOP + .18), (.28, SH_TOP + .2),
                                                (.24, SH_TOP + .2)], loc=(0, y, 0), seg=10)
        a.part('Fan_grilles', 'Undercarriage').cyl(.24, .01, loc=(0, y, SH_TOP + .185), seg=10, bevel=0)
    a.part('Kit_cables', 'Undercarriage').tube([(.5, -.3, SH_TOP + .02), (.55, 1.5, SH_TOP + .02),
                                                (.35, 2.4, SH_TOP + .1)], .03, seg=4)
    for x, y in ((-.7, -1.9), (.7, 3.8)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, SH_TOP), h=.45, r=.014)


def _radar(a):
    """The search radar's flat face on its mast at the shelter's front (spins)."""
    a.part('Radar_mast', 'Steel').cyl(.07, .25, loc=(-.5, -1.6, SH_TOP + .12), seg=8, bevel=0)
    r = a.pivot('Radar', (-.5, -1.6, SH_TOP + .25))
    k.block(a.part('Radar_panel', 'Armor', r), (.75, .14, .26), loc=(0, 0, 0), chamfer=.02)
    a.part('Radar_face', 'Undercarriage', r).box((.68, .02, .2), loc=(0, -.08, .13), bevel=0)


def _beam_director(a):
    """The beam director on the shelter's rear (`Turret`): turntable, yoke, telescope, aperture, tracker."""
    t = a.pivot('Turret', (0, 2.7, SH_TOP))
    a.pivot('Mount_APS', (0, 0, .4), t)
    k.lathe(a.part('Turret_body', 'Team', t), [(.55, 0), (.55, .08), (.45, .16), (.4, .18)], seg=14, worn=(1,))
    yoke = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        k.extrude(yoke, [(-.28, .15), (.28, .15), (.18, .62), (-.18, .62)], .1, loc=(s * .46, 0, 0), axis='X',
                  chamfer=.015, corner=.02)
    a.part('Turret_steel', 'Steel', t).cyl(.06, 1.02, loc=(0, 0, .38), rot=(0, R90, 0), seg=8, bevel=0)
    pitch = math.radians(12)
    rot = (R90 - pitch, 0, 0)
    d = (0, -math.cos(pitch), math.sin(pitch))
    c = (0, .1, .38)
    k.lathe(a.part('Main_cannon', 'PlasterWhite', t), [(.24, -.35), (.33, -.3), (.36, .0), (.36, .38), (.33, .45),
                                                       (0, .45)], loc=c, rot=rot, seg=14, caps=(True, False),
            worn=(2, 4))
    tip = (0, c[1] + d[1] * .46, c[2] + d[2] * .46)
    a.part('Main_cannon_lens', 'Energy', t).cyl(.26, .02, loc=tip, rot=rot, seg=14, bevel=0)
    k.ring(a.part('Main_cannon_bezel', 'Armor', t), [(.27, -.03), (.34, -.03), (.34, .03), (.27, .03)], loc=tip,
           rot=rot, seg=14)
    a.part('Team_band', 'Team', t).cyl(.365, .06, loc=(0, c[1] + d[1] * .1, c[2] + d[2] * .1), rot=rot, seg=14,
                                       bevel=0)
    a.pivot('Muzzle_main', (0, tip[1] - .02, tip[2] + .005), t)
    # The tracker's sensor box beside the telescope, its window.
    k.block(a.part('Sensor', 'Armor', t), (.2, .32, .22), loc=(.62, -.05, .55), chamfer=.02)
    a.part('Glass', 'Glass', t).box((.14, .01, .12), loc=(.62, -.215, .67), bevel=0)
    k.block(a.part('Turret_cooling', 'Armor', t), (.5, .3, .25), loc=(0, .55, .16), chamfer=.03)


def iron_beam(a, detail=False):
    """The Iron Beam-M: see the module docstring."""
    _cab(a)
    _chassis(a)
    _shelter(a)
    _radar(a)
    _beam_director(a)
    K.dust(a, (0, 0, .3), radius=3.8, k=.14)
    k.clean(a)


BUILDERS = {
    'iron_beam': (iron_beam, dict(ao_distance=.4, grime_height=.45)),
}
