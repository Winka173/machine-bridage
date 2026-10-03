"""Prompt 35 wave 9 (lane C): the combat wreck car rebuilt from scratch (spec: Tools/blender/specs/combat_wreck_car.json).

An improvised armoured car built out of an old sedan (balance.json: the light car that dies into a gun pit, the
Battle Bus idea; drawn after the up-armoured civilian cars of the Libyan and Syrian wars, the def's modelSize
4.78 x 2.08 x 1.49 m, a placed prop that blocks nothing in prompt 33, its footprint kept): the low sedan body
with welded steel plates over the bonnet, the doors and the boot (weld seams, bolt heads, rust patches), the
windscreen plated over with two vision slits, the side windows boxed in with firing ports, the bull bar and the
spare tyre on the boot, wheels half covered by plate skirts; on the roof the shielded gun ring (`Turret`): the
ring, the gun post, the bent shield and the 12.7 mm (`Main_cannon`, the def's mg_jeep) with a light coaxial gun
beside it (`Coax`); jerrycans and a sandbag on the boot, a whip.

Runtime nodes kept: `Turret`, `Wreck_turret` (where the gun pit forms), `Main_cannon`, `Muzzle_brake`, `Muzzle_main`,
`Coax`, `Muzzle_coax`, `Gun_post`, `Gun_shield`, `Point_exhaust`, `Point_fire` (the wrapper adds `Part_wheel` /
`Part_wheelb`). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .32
AXLES = (-1.45, 1.35)
TX = .78
NOSE, TAIL = -2.35, 2.35
TOP = 1.13


def _body(a):
    body = a.part('Body', 'Team')
    C.section_loft(body, [
        (NOSE, [(0, .38), (.8, .38), (.84, .6), (.78, .7), (0, .72)]),
        (NOSE + .25, [(0, .3), (.88, .3), (.92, .62), (.86, .78), (0, .8)]),
        (-.95, [(0, .3), (.9, .3), (.94, .66), (.88, .82), (0, .84)]),
        (-.4, [(0, .3), (.9, .3), (.94, .68), (.72, TOP - .02), (0, TOP)]),
        (.75, [(0, .3), (.9, .3), (.94, .68), (.72, TOP - .02), (0, TOP)]),
        (1.25, [(0, .3), (.9, .3), (.94, .66), (.88, .86), (0, .88)]),
        (TAIL, [(0, .38), (.84, .38), (.86, .6), (.8, .8), (0, .82)]),
    ])
    # Welded plates over the bonnet, doors and boot; seams, bolts, rust.
    pl = a.part('Armor_plates', 'Rust')
    K.plate(pl, (1.5, 1.0, .03), loc=(0, -1.55, .83), rot=(.03, 0, 0), chamfer=.006)
    K.plate(pl, (1.5, .9, .03), loc=(0, 1.75, .87), rot=(-.04, 0, 0), chamfer=.006)
    K.plate(pl, (1.45, .5, .03), loc=(0, -.68, 1.0), rot=(-.55, 0, 0), chamfer=.006)
    for s in (-1, 1):
        for y, w in ((-.4, .55), (.25, .6), (.85, .5)):
            K.plate(a.part('Armor_plates', 'Steel'), (.03, w, .42), loc=(s * .955, y, .62), rot=(0, s * .05, 0),
                    chamfer=.006)
        a.part('Skirts', 'Rust').box((.03, .8, .2), loc=(s * .97, AXLES[0], .52), bevel=0)
        a.part('Skirts', 'Rust').box((.03, .8, .2), loc=(s * .97, AXLES[1], .52), bevel=0)
    wl = a.part('Kit_welds', 'Undercarriage')
    for y in (-1.05, 1.3):
        wl.tube([(-.75, y, .87), (.75, y, .87)], .012, seg=3)
    bolts = a.part('Kit_bolts', 'Steel')
    for i in range(6):
        for s in (-1, 1):
            bolts.cyl(.018, .02, loc=(s * .97, -.6 + i * .3, .8), rot=(0, R90, 0), seg=5, bevel=0)
    # The plated windscreen with its vision slits, the boxed side windows with firing ports.
    for x in (-.32, .32):
        a.part('Visors', 'Glass').box((.36, .02, .05), loc=(x, -.62, 1.05), rot=(-.55, 0, 0), bevel=0)
    for s in (-1, 1):
        for y in (-.15, .5):
            a.part('Glass', 'Glass').box((.01, .2, .06), loc=(s * .86, y, .98), rot=(0, s * .4, 0), bevel=0)
            a.part('Firing_ports', 'Undercarriage').cyl(.035, .02, loc=(s * .96, y, .7), rot=(0, R90, 0), seg=6,
                                                        bevel=0)
        K.lamp(a, (s * .62, NOSE - .01, .6), (0, -1, 0), r=.06, guard=False)
        a.part('Tail_lamps', 'Lamp').box((.12, .02, .06), loc=(s * .66, TAIL + .005, .68), bevel=0)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .9, -.45, .9), s, arm=.06, size=(.04, .02, .08))
    # Bull bar, spare tyre on the boot, the exhaust.
    bb = a.part('Bull_bar', 'Steel')
    bb.tube([(-.7, NOSE - .02, .35), (-.7, NOSE - .1, .75), (.7, NOSE - .1, .75), (.7, NOSE - .02, .35)], .03, seg=5,
            caps=False)
    bb.tube([(-.7, NOSE - .08, .55), (.7, NOSE - .08, .55)], .025, seg=5)
    K.tread_wheel(a, (0, 1.85, .97), .3, .18, 1, seg=10, tyre='Spare_wheel', rim='Spare_wheel_rim')
    a.part('Exhaust', 'Steel').cyl(.03, .4, loc=(-.5, TAIL - .1, .3), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Point_exhaust', (-.5, TAIL + .1, .3))
    a.pivot('Point_fire', (0, .3, .9))
    C.jerry_rack(a, (-.55, 2.05, .88), count=2, axis='X')
    a.part('Sandbags', 'Sandbag').box((.5, .3, .14), loc=(.6, 2.15, .95), rot=(0, 0, .2), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.85, 1.4, .88), h=.6, r=.012)


def _running_gear(a):
    ax = a.part('Axles', 'Undercarriage')
    for y in AXLES:
        K.axle(ax, y, WR, TX - .1, r=.045, diff=False)
        for s in (-1, 1):
            K.tread_wheel(a, (s * TX, y, WR), WR, .24, s, seg=12)


def _gun(a):
    """The shielded gun ring on the roof (`Turret`), its post, shield, 12.7 mm and coax."""
    k.ring(a.part('Gun_ring', 'Steel'), [(.33, 0), (.4, 0), (.4, .06), (.33, .06)], loc=(0, .15, TOP), seg=12)
    t = a.pivot('Turret', (0, .15, TOP + .05))
    a.pivot('Wreck_turret', (0, .15, TOP), None)
    a.part('Gun_post', 'Steel', t).cyl(.04, .16, loc=(0, 0, .08), seg=8, bevel=0)
    sh = a.part('Gun_shield', 'Rust', t)
    k.extrude(sh, [(-.36, -.12), (.36, -.12), (.32, .2), (.1, .23), (-.1, .23), (-.32, .2)], .025,
              loc=(0, -.28, .2), rot=(R90 - .15, 0, 0), axis='Z', chamfer=.006, corner=.01)
    for s in (-1, 1):
        k.extrude(sh, [(-.1, -.12), (.1, -.12), (.08, .14), (-.08, .14)], .02, loc=(s * .42, -.2, .2),
                  rot=(R90, 0, s * .6), axis='Z', chamfer=.005)
    k.block(a.part('Gun_receiver', 'Undercarriage', t), (.12, .38, .12), loc=(0, .02, .2), chamfer=.012)
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.03, 0), (.03, .2), (.022, .25), (.02, .8), (0, .8)],
            loc=(0, -.17, .26), rot=K.FORWARD, seg=8, worn=(1,))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.024, 0), (.035, .02), (.035, .1), (.025, .12), (0, .12)],
            loc=(0, -.95, .26), rot=K.FORWARD, seg=8)
    a.pivot('Muzzle_main', (0, -1.08, .26), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.016, 0), (.016, .55), (0, .55)], loc=(.15, -.15, .2), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (.15, -.71, .2), t)
    k.block(a.part('Ammo_boxes', 'Crate', t), (.12, .22, .14), loc=(-.14, .05, .12), chamfer=.01)
    K.handle(a.part('Kit_handles', 'Steel', t), (-.05, .32, .3), (.05, .32, .3), (0, 1, 0), h=.05, r=.012)


def combat_wreck_car(a, detail=False):
    """The combat wreck car: see the module docstring."""
    _body(a)
    _running_gear(a)
    _gun(a)
    K.dust(a, (0, 0, .2), radius=2.4, k=.16)
    k.clean(a)


BUILDERS = {
    'combat_wreck_car': (combat_wreck_car, dict(ao_distance=.35, grime_height=.4)),
}
