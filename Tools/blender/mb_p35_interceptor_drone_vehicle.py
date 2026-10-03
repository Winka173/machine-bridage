"""Prompt 35 wave 9 (lane C): the interceptor drone vehicle rebuilt from scratch (spec:
Tools/blender/specs/interceptor_drone_vehicle.json).

A JLTV-class 4x4 counter-drone vehicle (balance.json interceptor_drone, the main launcher, and coyote_interceptor,
the free secondary; drawn after the Coyote-on-JLTV / LIDS mobile kits, the def's modelSize 5.0 x 2.0 x 2.4 m): the
tall angular armoured hull with the V-shaped belly, the sloped bonnet with its grille and lamps, the crew cab with
four doors, thick armoured windows and the roof hatch, the big lugged tyres on independent suspension arms with
the wheel arches; on the cargo bed the turntable (`Turret`) with the interceptor-drone launch box (six cells, the
cell doors, the hazard band) raised at the front; on the cab roof the small remote mount (`Mount_aam`) with two
Coyote tubes and its sensor ball; the bed's side lockers, jerrycans, the tow points and whips.

Runtime nodes kept: `Turret`, `Muzzle_main`, `Mount_aam`, `Muzzle_aam`, `Hatches`, `Point_exhaust`, `Point_fire`
(the wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .44
AXLES = (-1.55, 1.45)
TX = .78
NOSE, TAIL = -2.5, 2.5


def _hull(a):
    hull = a.part('Hull', 'Team')
    C.section_loft(hull, [
        (NOSE, [(0, .62), (.55, .62), (.78, .8), (.8, 1.0), (.7, 1.08), (0, 1.1)]),
        (NOSE + .3, [(0, .5), (.45, .5), (.86, .72), (.9, 1.08), (.8, 1.2), (0, 1.24)]),
        (-.95, [(0, .45), (.42, .45), (.9, .7), (.95, 1.2), (.9, 1.32), (0, 1.36)]),
        (TAIL - .15, [(0, .48), (.42, .48), (.9, .7), (.95, 1.2), (.9, 1.3), (0, 1.32)]),
        (TAIL, [(0, .55), (.42, .55), (.86, .72), (.9, 1.18), (.86, 1.26), (0, 1.28)]),
    ])
    cab = a.part('Cab', 'Team')
    C.slab_loft(cab, [(-.9, -1.05), (.9, -1.05), (.9, .6), (-.9, .6)],
                [(-.72, -.6), (.72, -.6), (.72, .5), (-.72, .5)], 1.3, 2.08)
    # Armoured windows: the split windscreen and the side windows; doors with their handles.
    for s in (-1, 1):
        K.windscreen(a, [(s * .05 if s > 0 else -.82, -1.02, 1.38), (.82 if s > 0 else -.05, -1.02, 1.38),
                         (.68 if s > 0 else -.05, -.64, 2.0), (s * .05 if s > 0 else -.68, -.64, 2.0)],
                     frame_mat='Team', wipers=1)
        gl = a.part('Glass', 'Glass')
        for y in (-.55, .15):
            gl.box((.01, .48, .4), loc=(s * .815, y, 1.7), rot=(0, s * .23, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        for y in (-.3, .4):
            dr.box((.012, .02, .55), loc=(s * .955, y, 1.0), bevel=0)
        for y in (-.5, .2):
            K.handle(a.part('Kit_steel', 'Steel'), (s * .96, y, 1.15), (s * .96, y + .12, 1.15), (s, 0, 0), h=.025,
                     r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .86, -.95, 1.65), s, arm=.06, size=(.04, .02, .14))
        K.lamp(a, (s * .62, NOSE + .02, .95), (0, -1, 0), r=.06, guard=True)
        a.part('Steps', 'Steel').box((.08, .5, .03), loc=(s * .92, -.15, .5), bevel=0)
    K.grille(a, (0, NOSE + .01, .88), .7, .25, facing=(0, -1, 0), slats=5, frame_mat='Steel')
    K.grille(a, (0, NOSE + .7, 1.22), .8, .5, facing=(0, -.25, 1), slats=5, frame_mat='Team')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (1.6, .12, .16), loc=(0, NOSE - .02, .62), c=.02)
    for s in (-1, 1):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, NOSE - .06, .6), facing=(0, -1, 0), size=.06)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .45, TAIL + .03, .62), facing=(0, 1, 0), size=.06)
        a.part('Tail_lamps', 'Lamp').box((.08, .02, .06), loc=(s * .8, TAIL + .005, 1.05), bevel=0)
    C.hatch(a, (0, -.15, 2.08), r=.28, mat='Team')
    K.exhaust(a, (-.85, .55, 1.2), r=.04, length=.3, direction=(0, 0, 1))
    a.pivot('Point_exhaust', (-.85, .55, 1.55))
    a.pivot('Point_fire', (0, -.2, 1.6))


def _running_gear(a):
    for y in AXLES:
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .32, s, seg=12)
            arm = a.part('Suspension', 'Undercarriage')
            arm.limb((s * .3, y, .5), (s * (TX - .12), y, WR), .04, .04, bevel=0)
            arm.limb((s * .3, y + .15, .7), (s * (TX - .12), y, WR + .12), .035, .035, bevel=0)
            arch = a.part('Wheel_arches', 'Team')
            k.extrude(arch, [(-.55, 0), (.55, 0), (.42, .12), (-.42, .12)], .3, loc=(s * (TX + .03), y, WR * 2 + .02),
                      axis='X', chamfer=.01)
    a.part('Axles', 'Undercarriage').box((.5, 3.4, .14), loc=(0, -.05, .5), bevel=0)


def _bed(a):
    """The cargo bed's lockers and stowage, the launch box on its turntable (`Turret`)."""
    for s in (-1, 1):
        lk = a.part('Lockers', 'Team')
        lk.box((.02, 1.5, .42), loc=(s * .955, 1.6, 1.0), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .962, 1.4, 1.1), (s * .962, 1.6, 1.1), (s, 0, 0), h=.025, r=.01)
    C.jerry_rack(a, (-.6, 2.35, 1.32), count=2, axis='X')
    t = a.pivot('Turret', (0, 1.5, 1.32))
    k.lathe(a.part('Turntable', 'Steel', t), [(.5, 0), (.5, .05), (.4, .1), (0, .11)], seg=12)
    cr = a.part('Launcher_cradle', 'Armor', t)
    for s in (-1, 1):
        k.extrude(cr, [(-.35, .08), (.35, .08), (.25, .45), (-.3, .4)], .06, loc=(s * .55, 0, 0), axis='X',
                  chamfer=.01)
    pitch = math.radians(20)
    rot = (-pitch, 0, 0)
    d = (0, -math.cos(pitch), math.sin(pitch))
    c = (0, .05, .62)
    L = 1.45
    box = a.part('Launcher', 'Team', t)
    k.extrude(box, [(-.5, -.24), (.5, -.24), (.5, .24), (-.5, .24)], L, loc=c, rot=rot, axis='Y', chamfer=.02,
              corner=.02)
    face = (0, c[1] + d[1] * L / 2, c[2] + d[2] * L / 2)
    up = (0, math.sin(pitch), math.cos(pitch))
    doors = a.part('Launcher_doors', 'Armor', t)
    for col in range(3):
        for row in range(2):
            x = (col - 1) * .3
            u = (row - .5) * .22
            doors.box((.26, .02, .18), loc=(x, face[1] + up[1] * u - .012 * math.cos(pitch), face[2] + up[2] * u +
                                            .012 * math.sin(pitch)), rot=rot, bevel=0)
    a.part('Hazard_marks', 'Hazard', t).box((.02, L * .8, .08), loc=(.51, c[1], c[2] + .12), rot=rot, bevel=0)
    a.part('Launcher_rams', 'Steel', t).limb((0, .4, .1), (0, .25, .45), .04, .05, bevel=0)
    a.pivot('Muzzle_main', (0, face[1] - .05 * math.cos(pitch), face[2] + .05 * math.sin(pitch)), t)


def _roof_mount(a):
    """The small remote mount on the cab roof with two Coyote tubes and the sensor ball (`Mount_aam`)."""
    k.lathe(a.part('Aam_base', 'Armor'), [(.2, 0), (.2, .06), (.12, .1), (.1, .14)], loc=(.45, .25, 2.08), seg=10)
    m = a.pivot('Mount_aam', (.45, .25, 2.22))
    k.block(a.part('Aam_cradle', 'Armor', m), (.18, .25, .1), loc=(0, 0, 0), chamfer=.015)
    tb = a.part('Aam_tubes', 'Canvas', m)
    for dx in (-.09, .09):
        tb.cyl(.07, .9, loc=(dx, -.15, .12), rot=(R90 - .15, 0, 0), seg=8, bevel=0)
        a.part('Aam_caps', 'Undercarriage', m).cyl(.072, .03, loc=(dx, -.6, .19), rot=(R90 - .15, 0, 0), seg=8,
                                                   bevel=0)
    k.lathe(a.part('Sensor', 'Armor', m), [(.0, 0), (.09, .03), (.1, .1), (.08, .17), (0, .19)], loc=(-.18, -.05, .02),
            seg=8)
    a.part('Glass', 'Glass', m).box((.08, .01, .06), loc=(-.18, -.145, .11), bevel=0)
    a.pivot('Muzzle_aam', (.09, -.62, .19), m)
    for x, y in ((-.7, .45), (.7, 2.3)):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, 2.08 if y < 1 else 1.32), h=.5, r=.012)


def interceptor_drone_vehicle(a, detail=False):
    """The interceptor drone vehicle: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _bed(a)
    _roof_mount(a)
    K.dust(a, (0, 0, .3), radius=2.6, k=.14)
    k.clean(a)


BUILDERS = {
    'interceptor_drone_vehicle': (interceptor_drone_vehicle, dict(ao_distance=.35, grime_height=.4)),
}
