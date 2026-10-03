"""Prompt 35 wave 7 (lane C): the rocket technical rebuilt from scratch (spec: Tools/blender/specs/rocket_technical.json).

A 6th-generation Toyota Hilux single cab with a Type 63 107 mm twelve-tube launcher on the bed (unit_refs: the Hilux
technical and the Type 63; the sheet: a civilian pickup with a small twelve-tube rocket grid on the rear bed; the
def's modelSize 4.39 x 1.5 x 1.86 m; a single cab so it reads apart from the double-cab zu23_technical): the cab with
its windscreen, side and rear windows, doors and mirrors, the hood with its grille, bumper and lamps, the ladder
frame with the front axle and the leaf-sprung rear axle on lugged tyres, the long bed with its dropsides and
tailgate; the launcher on a turntable on the bed (`Turret`: the cradle, three rows of four tubes, `Muzzle_main` at
the grid's centre), the 12.7 mm on its post on the roll bar behind the cab (the def's free `mg_jeep_selfdef`),
rocket crates, jerrycans, a tarp and the whip.

Runtime nodes kept: `Turret`, `Tubes_bore`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`, `Point_exhaust`, `Point_fire` (the
wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .33
AX = (-1.32, 1.18)
TRACK = .64
BED = .78


def _cab(a):
    body = a.part('Body', 'Team')
    # The hood and front wings: a low bonnet sloping to the grille.
    C.section_loft(body, [
        (-2.2, [(0, .5), (.7, .5), (.72, .78), (.62, .86), (0, .87)]),
        (-2.1, [(0, .45), (.74, .45), (.75, .85), (.66, .95), (0, .96)]),
        (-1.0, [(0, .45), (.75, .45), (.75, .9), (.68, 1.0), (0, 1.02)]),
    ])
    cab = a.part('Cab', 'Team')
    C.section_loft(cab, [
        (-1.02, [(0, .45), (.75, .45), (.75, .95), (.7, 1.02), (0, 1.02)]),
        (-.5, [(0, .45), (.75, .45), (.75, .98), (.6, 1.48), (0, 1.5)]),
        (.05, [(0, .45), (.75, .45), (.75, .98), (.6, 1.48), (0, 1.5)]),
    ])
    K.windscreen(a, [(-.66, -1.0, 1.04), (.66, -1.0, 1.04), (.55, -.52, 1.45), (-.55, -.52, 1.45)], frame_mat='Team',
                 wipers=2)
    gl = a.part('Glass', 'Glass')
    gl.box((1.1, .01, .3), loc=(0, .055, 1.25), bevel=0)
    for s in (-1, 1):
        gl.box((.01, .48, .34), loc=(s * .69, -.22, 1.22), rot=(0, s * .28, 0), bevel=0)
        dr = a.part('Doors', 'Team')
        dr.box((.012, .9, .02), loc=(s * .755, -.47, .92), bevel=0)
        dr.box((.012, .02, .5), loc=(s * .755, -.02, .72), bevel=0)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .76, -.12, .92), (s * .76, -.02, .92), (s, 0, 0), h=.025, r=.01)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .72, -.88, 1.1), s, arm=.02, size=(.05, .02, .1))
        K.lamp(a, (s * .55, -2.21, .74), (0, -1, 0), r=.06, guard=False)
        a.part('Team_band', 'Team').box((.012, 1.6, .05), loc=(s * .757, .9, .9), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.05, .02, .14), loc=(s * .68, 2.17, .9), bevel=0)
    K.grille(a, (0, -2.21, .7), .8, .2, facing=(0, -1, 0), slats=4, frame_mat='Steel')
    bp = a.part('Bumper', 'Steel')
    K.chamfer_box(bp, (1.5, .1, .14), loc=(0, -2.24, .5), c=.02)
    a.part('Kit_steel', 'Steel').box((1.0, .04, .2), loc=(0, -2.25, .65), bevel=0)        # bull bar plate
    a.part('Team_band', 'Team').box((1.1, .9, .01), loc=(0, -.47, 1.505), bevel=0)


def _chassis(a):
    ch = a.part('Chassis', 'Undercarriage')
    for s in (-1, 1):
        ch.box((.08, 4.1, .14), loc=(s * .38, -.05, .45), bevel=0)
    ax = a.part('Axles', 'Undercarriage')
    for y in AX:
        K.axle(ax, y, WR, TRACK - .1, r=.05)
        for s in (-1, 1):
            C.lugged_tyre(a, (s * TRACK, y, WR), WR, .22, s, lugs=9, seg=12, nuts=5)
    for s in (-1, 1):
        K.leaf_spring(a.part('Leaf_springs', 'Undercarriage'), s * .38, AX[1], WR + .1, .9, leaves=3)
    fl = a.part('Fender_flares', 'Team')
    for y in AX:
        for s in (-1, 1):
            fl.box((.1, .78, .03), loc=(s * .7, y, WR * 2 + .08), rot=(0, s * .3, 0), bevel=0)
    a.part('Exhaust', 'Steel').cyl(.025, .4, loc=(-.4, 1.92, .38), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Point_exhaust', (-.4, 2.12, .38))
    a.pivot('Point_fire', (0, 1.0, 1.1))


def _bed(a):
    bed = a.part('Bed', 'Team')
    k.block(bed, (1.5, 2.1, .06), loc=(0, 1.12, BED), chamfer=0)
    for s in (-1, 1):
        K.plate(bed, (.04, 2.1, .36), loc=(s * .73, 1.12, BED + .2), chamfer=.008)
    K.plate(bed, (1.5, .04, .36), loc=(0, .1, BED + .2), chamfer=.008)
    K.plate(a.part('Tailgate', 'Team'), (1.42, .04, .34), loc=(0, 2.16, BED + .2), chamfer=.008)
    st = a.part('Kit_steel', 'Steel')
    for s in (-1, 1):
        for y in (.6, 1.2, 1.8):
            st.box((.02, .04, .3), loc=(s * .755, y, BED + .2), bevel=0)
    # The roll bar behind the cab carrying the MG post.
    rb = a.part('Roll_bar', 'Steel')
    rb.tube([(-.68, .2, BED + .35), (-.6, .2, 1.5), (.6, .2, 1.5), (.68, .2, BED + .35)], .03, seg=6, caps=False)
    rb.tube([(-.6, .2, 1.5), (-.35, .5, BED + .4)], .025, seg=5)
    rb.tube([(.6, .2, 1.5), (.35, .5, BED + .4)], .025, seg=5)
    K.pintle_mg(a, None, (.25, .2, 1.5), post=.08, length=1.0, scale=.85)
    # Stowage: rocket crates stacked at the front of the bed, a jerrycan, a rolled tarp, the whip.
    cr = a.part('Crates', 'Crate')
    for i, (x, z) in enumerate(((-.42, 0), (-.42, .17), (.45, 0))):
        K.crate(cr, a.part('Kit_straps', 'Steel'), (.4, .9, .16), (x, .65, BED + .03 + z), bands=1)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (.5, 1.85, BED + .03), rot=(0, 0, R90))
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Steel'), (0, .35, BED + .45), length=1.1, r=.1)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.7, -.05, 1.5), h=.32, r=.018)


def _launcher(a):
    t = a.pivot('Turret', (0, 1.38, BED + .03))
    a.part('Pedestal', 'Steel').cyl(.12, .2, loc=(0, 1.38, BED + .1), seg=10, bevel=0)
    k.lathe(a.part('Turntable', 'Steel', t), [(.4, 0), (.4, .05), (.32, .09), (.1, .2), (0, .2)], seg=12, worn=(1,))
    cr = a.part('Cradle', 'Armor', t)
    for s in (-1, 1):
        k.extrude(cr, [(-.25, .1), (.25, .1), (.2, .62), (-.15, .58)], .03, loc=(s * .44, 0, 0), axis='X', chamfer=.005)
    k.lathe(cr, [(.04, -.46), (.04, .46)], loc=(0, 0, .5), rot=(0, R90, 0), seg=8)
    pitch = math.radians(12)
    c, sn = math.cos(pitch), math.sin(pitch)
    tubes = a.part('Tubes', 'Team', t)
    bore = a.part('Tubes_bore', 'Undercarriage', t)
    L = 1.15
    for row in range(3):
        for col in range(4):
            x = (col - 1.5) * .155
            z = .5 + row * .15
            y = 0
            tubes.cyl(.07, L, loc=(x, y, z), rot=(R90 - pitch, 0, 0), seg=8, bevel=0)
            bore.cyl(.055, .02, loc=(x, y - L / 2 * c - .005, z + L / 2 * sn), rot=(R90 - pitch, 0, 0), seg=8,
                     bevel=0)
    band = a.part('Tube_bands', 'Steel', t)
    for f in (-.3, .3):
        band.box((.66, .03, .48), loc=(0, f * c, .65 - f * sn), rot=(-pitch, 0, 0), bevel=0)
    a.part('Sight', 'Steel', t).box((.06, .12, .1), loc=(.36, -.2, .92), bevel=0)
    a.pivot('Muzzle_main', (0, -L / 2 * c - .03, .65 + L / 2 * sn), t)


def rocket_technical(a, detail=False):
    """The rocket technical: see the module docstring."""
    _cab(a)
    _chassis(a)
    _bed(a)
    _launcher(a)
    K.dust(a, (0, 0, .2), radius=2.4, k=.14)
    k.clean(a)


BUILDERS = {
    'rocket_technical': (rocket_technical, dict(ao_distance=.35, grime_height=.4)),
}
