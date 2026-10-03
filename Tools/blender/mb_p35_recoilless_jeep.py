"""Prompt 35 wave 12 (lane C): the recoilless jeep rebuilt from scratch (spec: Tools/blender/specs/recoilless_jeep.json).

The M38A1C (the US Army / USMC 106 mm carrier jeep; the def's modelSize 3.5 x 1.4 x 1.6 m and its recoilless_106):
the round-nosed body that tells it from the scout jeep's M151 (wave 7): the crowned hood between the rolled front
wings with their arches, the seven-slot grille with the round headlamps and the brush guard, the split windscreen
folded flat on the hood with the notch the gun needs, the open tub with its curved side cut-outs, seats, steering
wheel and the jerrycan on the tail; leaf springs on beam axles, four lugged wheels, the spare on the right flank.

The M40A1 106 mm recoilless rifle on its M79 pedestal mount in the rear (`Turret`, the old pivot): the pedestal
column with the traverse ring and handwheel, the cradle and trunnions, the elevation handwheel and the firing knob;
the long tube (`Main_cannon`) with the perforated breech chamber and the hinged venturi breech block with its
operating handle, the muzzle ring (`Muzzle_brake`) and `Muzzle_main` at the tip; the M8C .50 spotting rifle on its
two brackets on top of the tube; the M92F telescope on the left of the cradle. Four rounds in the rear rack, the
radio and its whip, blackout lamps, tow pintle, Team bands.

Runtime nodes kept at the old places: `Turret` (0, 0.6, 1.05), `Main_cannon`, `Muzzle_brake`, `Muzzle_main`,
`Point_exhaust`, `Point_fire` (the wrapper adds `Part_wheel` / `Part_wheelb` from the Tyres / Wheels / Hubs pieces).
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
WR = .35
AX = (-1.0, .98)
TRACK = .56
FLOOR = .52
COWL = -.52                  # the windscreen hinge line
TAIL = 1.62
TURRET = (0, .6, 1.05)


def _body(a):
    tub = a.part('Body', 'Team')
    # The tub: side walls with the curved crew cut-outs, the rear panel, the floor.
    for s in (-1, 1):
        k.extrude(tub, [(COWL, FLOOR), (.56, FLOOR), (.6, .66), (.72, .77), (.86, .82), (1.1, .82), (1.24, .77),
                        (1.36, .66), (1.4, FLOOR), (TAIL - .14, FLOOR), (TAIL - .14, .98), (.95, .98), (.85, .9), (.55, .86), (.2, .86),
                        (-.05, .9), (-.2, .98), (COWL, .98)], .05, loc=(s * .6, 0, 0), axis='X', chamfer=.012)
    k.extrude(tub, [(-.46, FLOOR), (.46, FLOOR), (.46, .98), (-.46, .98)], .05, loc=(0, TAIL - .02, 0), axis='Y',
              chamfer=.012)
    for s in (-1, 1):            # the rounded-off rear corners (45-degree panels)
        k.block(tub, (.2, .05, .46), loc=(s * .53, TAIL - .085, FLOOR + .23), rot=(0, 0, -s * math.pi / 4),
                chamfer=.01)
    tub.box((1.2, TAIL - COWL, .04), loc=(0, (TAIL + COWL) / 2, FLOOR + .02), bevel=0)
    k.block(a.part('Body', 'Team'), (1.25, .12, .4), loc=(0, COWL, .78), chamfer=.02)       # the cowl / dash
    # The crowned hood and the rolled front wings with their wheel arches.
    C.section_loft(a.part('Body', 'Team'), [
        (-1.56, [(0, .62), (.36, .62), (.36, .86), (.26, .935), (0, .955)]),
        (-1.5, [(0, .62), (.37, .62), (.37, .89), (.27, .97), (0, .99)]),
        (COWL + .06, [(0, .62), (.4, .62), (.4, .92), (.29, 1.0), (0, 1.02)]),
    ])
    for s in (-1, 1):
        prof = [(-1.62, .72), (-1.6, .82), (-1.52, .9), (-1.36, .95), (COWL + .02, .96), (COWL + .02, .62),
                (-.66, .62), (-.72, .74), (-.86, .82), (-1.0, .845), (-1.14, .82), (-1.28, .74), (-1.34, .62),
                (-1.62, .62)]
        k.extrude(a.part('Body_wings', 'Team'), prof, .3, loc=(s * .55, 0, 0), axis='X', chamfer=.015)
        a.part('Team_band', 'Team').box((.012, .7, .07), loc=(s * .627, .1, .78), bevel=0)
        # The rear wheel housing inside the arch and the flat arch lip.
        a.part('Body', 'Team').box((.3, .9, .04), loc=(s * .47, .98, .84), bevel=0)
        a.part('Body_wings', 'Team').box((.06, .86, .03), loc=(s * .63, .98, .845), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.06, .02, .05), loc=(s * .5, TAIL + .03, .86), bevel=0)
        a.part('Tail_lamps', 'Lamp').box((.04, .02, .03), loc=(s * .5, TAIL + .03, .78), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .627, 1.15, .9), (s * .627, 1.4, .9), (s, 0, 0), h=.03, r=.01)
    # The seven-slot grille, the headlamps set in it, the brush guard, the bumper with its tow hooks.
    gr = a.part('Grille', 'Team')
    k.block(gr, (.64, .04, .3), loc=(0, -1.58, .78), chamfer=.01)
    slots = a.part('Grilles', 'Undercarriage')
    for i in range(7):
        slots.box((.035, .02, .22), loc=(-.24 + i * .08, -1.6, .79), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .25, -1.61, .9), (0, -1, 0), r=.06, guard=False)
    guard = a.part('Brush_guard', 'Steel')
    for s in (-1, 1):
        guard.tube([(s * .3, -1.68, .58), (s * .3, -1.68, .95), (s * .12, -1.68, 1.0)], .016, seg=4)
    bp = a.part('Bumper', 'Steel')
    k.block(bp, (1.36, .1, .14), loc=(0, -1.68, .56), chamfer=.012)
    for s in (-1, 1):
        K.tow_hook(bp, (s * .42, -1.74, .55), facing=(0, -1, 0), size=.06)
        a.part('Team_band', 'Team').box((.18, .012, .08), loc=(s * .55, -1.736, .56), bevel=0)
    # Hood latches and the left mirror on its arm off the cowl.
    for s in (-1, 1):
        a.part('Kit_steel', 'Steel').box((.03, .06, .05), loc=(s * .38, -1.2, .97), bevel=0)
    K.mirror(a.part('Kit_steel', 'Steel'), (.6, COWL, .98), 1, arm=.06, size=(.08, .02, .1))
    # The split windscreen folded flat on the hood, the gap the gun needs, its hinges and the wiper motors.
    wf = a.part('Windscreen_frame', 'Team')
    for s in (-1, 1):
        x0, x1 = s * .12, s * .6
        k.block(wf, (abs(x1 - x0), .38, .03), loc=((x0 + x1) / 2, COWL - .25, 1.04), chamfer=.008)
        a.part('Glass', 'Glass').box((abs(x1 - x0) - .08, .3, .01), loc=((x0 + x1) / 2, COWL - .25, 1.06), bevel=0)
        a.part('Kit_hinges', 'Steel').cyl(.018, .2, loc=(s * .38, COWL - .05, 1.02), rot=(0, R90, 0), seg=6, bevel=0)
    a.part('Windscreen_frame', 'Rubber').box((.3, .12, .04), loc=(0, COWL - .32, 1.03), bevel=0)   # the gun's rest pad
    # Seats, the steering wheel (left-hand drive, +X), the hand brake.
    st = a.part('Seats', 'Canvas')
    for x in (-.28, .28):
        k.block(st, (.38, .4, .08), loc=(x, -.18, .7), chamfer=.02)
        k.block(st, (.38, .07, .38), loc=(x, .04, .9), rot=(-.18, 0, 0), chamfer=.02)
    sw = a.part('Steering', 'Rubber')
    sw.torus(.13, .015, loc=(.28, -.42, 1.0), rot=(1.1, 0, 0), seg=10, ring=4)
    sw.limb((.28, -.42, 1.0), (.28, -.5, .82), .015, .015, bevel=0)
    a.part('Kit_steel', 'Steel').limb((.05, -.3, .58), (.05, -.25, .78), .02, .02, bevel=0)


def _chassis(a):
    ax = a.part('Axles', 'Undercarriage')
    sp = a.part('Leaf_springs', 'Undercarriage')
    for y in AX:
        K.axle(ax, y, WR, TRACK - .08, r=.05)
        for s in (-1, 1):
            C.lugged_tyre(a, (s * TRACK, y, WR), WR, .21, s, lugs=10, seg=12, nuts=4)
            K.leaf_spring(sp, s * .42, y, WR + .08, .72, leaves=2, w=.06)
    fr = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        fr.box((.07, 3.1, .12), loc=(s * .38, -.05, .5), bevel=0)
    fr.box((.84, .07, .1), loc=(0, -1.5, .5), bevel=0)
    fr.box((.84, .07, .1), loc=(0, 1.45, .5), bevel=0)
    # The spare wheel on the tail panel (right of centre), the jerrycan beside it on the left.
    r, w = .3, .17
    loc = (-.2, TAIL + .03 + w / 2, .74)
    k.lathe(a.part('Spare_wheel', 'Rubber'), [(r * .6, -w / 2), (r * .93, -w / 2), (r, -w * .3), (r, w * .3),
                                              (r * .93, w / 2), (r * .6, w / 2)], loc=loc, rot=K.BACKWARD, seg=14,
            worn=(2, 3))
    k.lathe(a.part('Spare_wheel_rim', 'Steel'), [(r * .62, w / 2 - .01), (r * .5, w / 2 + .01), (r * .2, w / 2 + .01),
                                                 (0, w / 2 + .02)], loc=loc, rot=K.BACKWARD, seg=10)
    a.part('Spare_wheel_rim', 'Steel').box((.1, .06, .1), loc=(-.2, TAIL + .03, .74), bevel=0)
    C.jerry_rack(a, (.32, TAIL + .1, .6), count=1, axis='X', rot=(0, 0, R90))
    a.part('Exhaust', 'Steel').tube([(-.3, -.3, .44), (-.42, .9, .42), (-.45, 1.62, .45)], .028, seg=6)
    a.pivot('Point_exhaust', (-.45, 1.66, .45))
    K.soot(a, (-.45, 1.7, .45), radius=.25, k=.35)
    a.part('Kit_steel', 'Steel').cyl(.035, .12, loc=(0, TAIL + .08, .52), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Point_fire', (0, .2, .9))


def _rifle(a):
    """The M40A1 on its M79 pedestal mount (Turret) with the M8C spotting rifle and the M92F telescope."""
    k.block(a.part('Kit_steel', 'Steel'), (.36, .36, .05), loc=(0, TURRET[1], FLOOR + .05), chamfer=.012)
    k.lathe(a.part('Pedestal', 'Armor'), [(.1, 0), (.09, .06), (.07, .1), (.07, .44), (0, .44)],
            loc=(0, TURRET[1], FLOOR + .07), seg=12, worn=(1,))
    t = a.pivot('Turret', TURRET)
    k.lathe(a.part('Traverse_ring', 'Steel', t), [(.13, -.04), (.14, -.02), (.14, .02), (.11, .04), (0, .04)], seg=12)
    zb = .4                                                   # the bore axis above the pivot
    cr = a.part('Cradle', 'Armor', t)
    k.block(cr, (.2, .7, .12), loc=(0, -.05, zb - .12), chamfer=.02)
    for s in (-1, 1):
        cr.box((.04, .18, .3), loc=(s * .1, 0, zb - .15), bevel=0)
        a.part('Traverse_ring', 'Steel', t).cyl(.04, .05, loc=(s * .125, 0, zb - .04), rot=(0, R90, 0), seg=8, bevel=0)
    hw = a.part('Traverse_ring', 'Steel', t)
    hw.torus(.08, .01, loc=(-.2, .12, zb - .18), rot=(0, R90, 0), seg=8, ring=3)       # elevation
    hw.limb((-.12, .12, zb - .18), (-.2, .12, zb - .18), .015, .015, bevel=0)
    hw.torus(.07, .01, loc=(.08, .25, .05), rot=(R90, 0, 0), seg=8, ring=3)           # traverse
    hw.limb((.08, .1, .05), (.08, .25, .05), .015, .015, bevel=0)
    a.part('Firing_knob', 'BarrelRed', t).cyl(.025, .05, loc=(-.2, .12, zb - .18), rot=(0, R90, 0), seg=6, bevel=0)
    # The tube: chamber section, the long barrel, the muzzle ring.
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.065, 0), (.065, .3), (.058, .36), (.054, 2.05), (0, 2.05)],
            loc=(0, -.05, zb), rot=K.FORWARD, seg=12, worn=(1,))
    k.lathe(a.part('Breech_chamber', 'Armor', t), [(.075, -.62), (.11, -.56), (.11, -.12), (.075, -.05),
                                                   (.068, 0)], loc=(0, -.05, zb), rot=K.FORWARD, seg=12, worn=(1, 2))
    holes = a.part('Breech', 'Undercarriage', t)
    for i in range(4):
        for j in range(3):
            u = R90 + (j - 1) * TAU / 6 + (i % 2) * TAU / 12
            holes.box((.015, .05, .03), loc=(math.cos(u) * .111, .2 + i * .1, zb + math.sin(u) * .111),
                      rot=(0, -u, 0), bevel=0)
    # The venturi breech block (hinged open-cone), its operating handle.
    k.lathe(a.part('Breech', 'Armor', t), [(.09, 0), (.12, .06), (.14, .22), (.13, .26), (.1, .26), (.06, .08)],
            loc=(0, .57, zb), rot=K.BACKWARD, seg=12, worn=(2, 3))
    a.part('Breech', 'Undercarriage', t).cyl(.095, .02, loc=(0, .82, zb), rot=K.BACKWARD, seg=12, bevel=0)
    a.part('Traverse_ring', 'Steel', t).tube([(.12, .62, zb + .04), (.22, .72, zb + .02), (.22, .78, zb - .06)],
                                             .014, seg=4)
    k.lathe(a.part('Muzzle_brake', 'Armor', t), [(.06, 0), (.072, .02), (.072, .12), (.062, .14), (0, .14)],
            loc=(0, -2.0, zb), rot=K.FORWARD, seg=12)
    a.pivot('Muzzle_main', (0, -2.15, zb), t)
    K.soot(a, (0, -2.13 + TURRET[1], TURRET[2] + zb), radius=.25, k=.35)
    # The M8C spotting rifle on two brackets above the tube, its flash hider and its small breech.
    sp = a.part('Spotting_rifle', 'Steel', t)
    for y in (-.55, .25):
        sp.box((.03, .05, .1), loc=(0, y, zb + .1), bevel=0)
    k.lathe(sp, [(.018, 0), (.018, 1.2), (0, 1.2)], loc=(0, .4, zb + .16), rot=K.FORWARD, seg=6)
    k.block(a.part('Spotting_rifle', 'Armor', t), (.06, .28, .07), loc=(0, .48, zb + .16), chamfer=.01)
    sp.cyl(.024, .06, loc=(0, -.82, zb + .16), rot=K.FORWARD, seg=6, bevel=0)
    # The M92F telescope on the left of the cradle, its eyepiece and the elbow.
    k.lathe(a.part('Sight', 'Armor', t), [(.03, 0), (.035, .02), (.035, .32), (.04, .36), (0, .36)],
            loc=(.16, .15, zb + .05), rot=K.FORWARD, seg=8)
    a.part('Glass', 'Glass', t).cyl(.03, .01, loc=(.16, -.215, zb + .05), rot=K.FORWARD, seg=8, bevel=0)
    a.part('Sight', 'Rubber', t).cyl(.03, .05, loc=(.16, .18, zb + .05), rot=K.FORWARD, seg=8, bevel=0)
    a.part('Team_band', 'Team', t).cyl(.07, .06, loc=(0, -1.0, zb), rot=K.FORWARD, seg=12, bevel=0)


def _stowage(a):
    """Four rounds in the rack along the rear left, the radio and its whip, a tarp."""
    rk = a.part('Kit_steel', 'Steel')
    for y in (.95, 1.45):
        rk.box((.4, .04, .2), loc=(.38, y, FLOOR + .12), bevel=0)
    for i in range(4):
        x = .24 + (i % 2) * .14
        z = FLOOR + .13 + (i // 2) * .12
        k.lathe(a.part('Rounds', 'Fuel'), [(0, -.36), (.04, -.3), (.05, -.2), (.05, .25), (.055, .26), (.055, .33),
                                           (0, .34)], loc=(x, 1.2, z), rot=K.BACKWARD, seg=6)
    k.block(a.part('Radio', 'Armor'), (.26, .22, .24), loc=(-.38, 1.35, FLOOR + .14), chamfer=.015)
    a.part('Radio', 'Undercarriage').box((.18, .01, .1), loc=(-.38, 1.235, FLOOR + .17), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.55, TAIL - .05, .98), h=.55, r=.02, lean=.1)
    k.lathe(a.part('Tarp_roll', 'Canvas'), [(0, -.45), (.07, -.44), (.08, -.4), (.08, .4), (.07, .44), (0, .45)],
            loc=(0, TAIL - .1, 1.03), rot=(0, R90, 0), seg=8, worn=(2, 3))
    st = a.part('Kit_straps', 'Rubber')
    for x in (-.25, .25):
        st.cyl(.085, .03, loc=(x, TAIL - .1, 1.03), rot=(0, R90, 0), seg=8, bevel=0)


def recoilless_jeep(a, detail=False):
    """The recoilless jeep: see the module docstring."""
    _body(a)
    _chassis(a)
    _rifle(a)
    _stowage(a)
    K.dust(a, (0, 0, .2), radius=1.8, k=.15)
    k.clean(a)


BUILDERS = {
    'recoilless_jeep': (recoilless_jeep, dict(ao_distance=.45, grime_height=.45)),
}
