"""Prompt 35 wave 4 (lane C): the SHORAD vehicle rebuilt from scratch (spec: Tools/blender/specs/shorad_vehicle.json).

An AN/TWQ-1 Avenger on the HMMWV (the def's modelSize 3.8 x 1.8 x 2.2 m): the HMMWV's wide low body with the
sloping hood and its grille slots, the four big tyres on independent arms with geared hubs, the two-door cab with
its flat windscreen, doors with windows, mirrors, lamps; the cargo bed carrying the Avenger turret: the gunner's
glazed cab in the middle on its turntable, the two four-tube Stinger pods on the elevating arms either side
(`Launcher`, `Launcher_rails`, `Tubes`), the FLIR / laser sensor box, and the M3P .50 under the right pod on its
own mount (the def's free `hmg_selfdef_21`: `Mount_mg`).

Runtime nodes kept: `Turret`, `Turret_body`, `Launcher`, `Launcher_rails`, `Tubes`, `Muzzle_missile`, `Mount_mg`,
`Muzzle_mg`, `Point_exhaust`, `Point_fire` (the wrapper adds `Part_wheel` / `Part_wheelb`). Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
WR = .37
AX = (-1.05, .92)          # axle stations
TRACK = .72
FLOOR = .62


def _body(a):
    body = a.part('Body', 'Team')
    # The hood: low and wide, sloping to the grille; the cab; the bed sides.
    C.section_loft(body, [
        (-1.72, [(0, .55), (.78, .55), (.82, .8), (.68, .88), (0, .9)]),
        (-1.42, [(0, .5), (.88, .5), (.9, .92), (.78, 1.0), (0, 1.02)]),
        (-.7, [(0, .5), (.84, .5), (.86, 1.0), (.78, 1.08), (0, 1.1)]),
        (1.7, [(0, .5), (.84, .5), (.86, 1.0), (.82, 1.04), (0, 1.04)]),
    ])
    K.grille(a, (0, -1.74, .72), .9, .2, facing=(0, -1, 0), slats=6, frame_mat='Team')
    cab = a.part('Cab', 'Team')
    C.slab_loft(cab, [(-.86, -.72), (.86, -.72), (.86, .35), (-.86, .35)], [(-.8, -.45), (.8, -.45), (.8, .3), (-.8, .3)],
                1.1, 1.62)
    K.windscreen(a, [(-.78, -.71, 1.15), (.78, -.71, 1.15), (.76, -.47, 1.58), (-.76, -.47, 1.58)], frame_mat='Team',
                 wipers=2)
    gl = a.part('Windows', 'Glass')
    for s in (-1, 1):
        for y in (-.3, .12):
            gl.box((.02, .34, .3), loc=(s * .865, y, 1.37), bevel=0)
        K.mirror(a.part('Kit_steel', 'Steel'), (s * .8, -.65, 1.3), s, arm=.08)
        K.handle(a.part('Kit_steel', 'Steel'), (s * .91, -.1, 1.05), (s * .91, .05, 1.05), (s, 0, 0), h=.03, r=.01)
        K.lamp(a, (s * .6, -1.72, .82), (0, -1, 0), r=.07, guard=False)
        a.part('Tail_lamps', 'LavaGlow').box((.08, .02, .1), loc=(s * .72, 1.71, .9), bevel=0)
    # Wheel arches, the fender flares, the bumper with its tow shackles.
    fl = a.part('Fender_flares', 'Undercarriage')
    for y in AX:
        for s in (-1, 1):
            k.sweep(fl, [(-.04, -.03), (.06, -.03), (.06, .03), (-.04, .03)],
                    [(s * .84, y + math.cos(u) * (WR + .1), WR + math.sin(u) * (WR + .1)) for u in
                     (0.1, .6, 1.1, 1.57, 2.04, 2.54, 3.04)])
    bp = a.part('Bumper', 'Armor')
    k.block(bp, (1.8, .14, .16), loc=(0, -1.78, .48), chamfer=.02)
    for x in (-.55, .55):
        K.tow_hook(a.part('Kit_steel', 'Steel'), (x, -1.85, .52), facing=(0, -1, 0), size=.06)
    K.exhaust(a, (-.65, 1.45, .5), r=.04, length=.25, direction=(0, 1, 0), muffler=False, cap=False)
    a.pivot('Point_exhaust', (-.65, 1.72, .5))
    a.pivot('Point_fire', (0, -1.2, 1.1))
    # Stowage: the jerrycan on the rear, the cam-net roll on the hood, the antenna.
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (.5, 1.72, .6), rot=(0, 0, 0))
    a.part('Stowage', 'Canvas').cyl(.1, 1.1, loc=(0, -1.0, 1.15), rot=(0, R90, 0), seg=8, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.8, .3, 1.62), h=.4)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.01, 1.6, .08), loc=(s * .865, -.9, .85), bevel=0)


def _chassis(a):
    ax = a.part('Axles', 'Undercarriage')
    for y in AX:
        for s in (-1, 1):
            ax.limb((s * .2, y, .42), (s * (TRACK - .12), y, WR), .05, .05, bevel=0)           # half shafts
            ax.limb((s * .25, y + .1, .32), (s * (TRACK - .15), y + .05, WR - .05), .03, .06, bevel=0)  # arm
            C.lugged_tyre(a, (s * TRACK, y, WR), WR, .3, s, lugs=12, seg=14)
            k.lathe(a.part('Hubs', 'Steel'), [(.08, .15), (.11, .17), (.11, .22), (.06, .24)],
                    loc=(s * TRACK, y, WR), rot=(0, s * R90, 0), seg=8)                    # geared hub
        ax.box((.3, .3, .2), loc=(0, y, .4), bevel=0)                                      # differential
    a.part('Undercarriage', 'Undercarriage').box((1.0, 3.4, .18), loc=(0, 0, .42), bevel=0)


def _turret(a):
    """The Avenger turret on the bed: the turntable, the glazed gunner's cab, the pods, the sensor box, the M3P."""
    t = a.pivot('Turret', (0, .85, 1.04))
    k.ring(a.part('Turret_ring', 'Armor'), [(.66, 0), (.72, 0), (.72, .08), (.66, .08)], loc=(0, .85, 1.04), seg=16)
    cab = a.part('Turret_body', 'Team', t)
    C.slab_loft(cab, [(-.42, -.45), (.42, -.45), (.48, .4), (-.48, .4)], [(-.36, -.32), (.36, -.32), (.4, .35),
                                                                        (-.4, .35)], .08, 1.0)
    gl = a.part('Glass', 'Glass', t)
    gl.box((.62, .02, .45), loc=(0, -.4, .65), rot=(-.25, 0, 0), bevel=0)
    for s in (-1, 1):
        gl.box((.02, .45, .35), loc=(s * .45, -.05, .65), rot=(0, s * .08, 0), bevel=0)
    k.block(a.part('Turret_roof', 'Armor', t), (.75, .7, .04), loc=(0, 0, 1.0), chamfer=.01)
    # The elevating arms and the two four-tube pods.
    for s in (-1, 1):
        x = s * .72
        a.part('Launcher_rails', 'Steel', t).box((.22, .16, .16), loc=(s * .52, 0, .62), bevel=0)
        k.block(a.part('Launcher', 'Team', t), (.32, 1.0, .34), loc=(x, -.05, .45), chamfer=.03)
        tubes = a.part('Tubes', 'Undercarriage', t)
        for i in range(2):
            for j in range(2):
                tubes.cyl(.06, .02, loc=(x + (i - .5) * .14, -.56, .54 + (j - .5) * .15), rot=K.FORWARD, seg=8,
                          bevel=0)
        a.part('Launcher_bands', 'Hazard', t).box((.33, .04, .35), loc=(x, .3, .45), bevel=0)
    a.pivot('Muzzle_missile', (.72, -.58, .62), t)
    # The FLIR / laser sensor box on the left arm, the M3P .50 on its own mount under the right pod.
    k.block(a.part('Sensor', 'Armor', t), (.22, .3, .2), loc=(.72, -.1, .82), chamfer=.02)
    a.part('Glass', 'Glass', t).box((.15, .01, .1), loc=(.72, -.255, .92), bevel=0)
    m = a.pivot('Mount_mg', (-.72, -.1, .3), t)
    mg = a.part('MG', 'Steel', m)
    k.extrude(mg, [(-.22, -.05), (.2, -.05), (.22, .05), (-.22, .06)], .12, axis='X', chamfer=.008)
    k.lathe(mg, [(.035, 0), (.035, .18), (.022, .22), (.02, .85), (.032, .87), (.032, .95), (0, .95)],
            loc=(0, -.22, 0), rot=K.FORWARD, seg=8, worn=(1,))
    k.block(a.part('MG_ammo', 'Crate', m), (.12, .22, .16), loc=(-.13, .05, -.08), chamfer=.01)
    a.pivot('Muzzle_mg', (0, -1.18, 0), m)
    a.part('Team_band', 'Team', t).box((.88, .01, .08), loc=(0, .4, .5), bevel=0)


def shorad_vehicle(a, detail=False):
    """The SHORAD vehicle: see the module docstring."""
    _body(a)
    _chassis(a)
    _turret(a)
    K.dust(a, (0, 0, .2), radius=2.2, k=.18)
    k.clean(a)


BUILDERS = {
    'shorad_vehicle': (shorad_vehicle, dict(ao_distance=.4, grime_height=.45)),
}
