"""Prompt 35 wave 6 (lane B): the bridgelayer rebuilt from scratch (spec: Tools/blender/specs/bridging_vehicle.json).

An MTU-72 / M60 AVLB-class armoured vehicle-launched bridge (the def's modelSize 6.45 x 3.02 x 2.02 m): a T-72
class tank hull without its turret (the sloped glacis with the V splash board, the driver's hatch and periscope on
the front, the flat engine deck with grilles and the rear fuel drums), six road wheels a side, the rear sprocket,
the front idler on its arm, three return rollers and a linked track under rubber side skirts; on top the folded
two-span scissor bridge: two box treadways per half with truss sides, cross ribs and anti-slip tread plates, the
upper half lying reversed on the lower one, the hinge knuckles at the rear, the launching boom on its pivot at the
front with the two hydraulic rams and their hoses; the commander's cupola with a 12.7 mm on a raised mount on the
front right (`Turret`); smoke dischargers on the glacis corners, stowage boxes, tow cable, lamps, hooks, whips,
Team bands.

Its own hull: nothing is taken from another tracked model. Runtime nodes kept: `Turret`, `Main_cannon`,
`Muzzle_brake`, `Muzzle_main`, `Point_exhaust`, `Point_fire`; old part names `Bridge`, `Tread_plates`; new for the
gate: `Cradle` (the gun's mantlet role), `Idlers`, `Smoke_launchers`, `Stowage`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TX, TW = 1.18, .46
WR = .27
WHEELS = (-1.95, -1.22, -.49, .24, .97, 1.7)
NOSE, TAIL = -3.0, 2.88
DECK = 1.08
HALF = 1.3


def _hull(a):
    hull = a.part('Hull', 'Team')
    prof = [(TAIL, .45), (TAIL + .02, DECK - .1), (TAIL - .1, DECK), (NOSE + 1.05, DECK), (NOSE + .1, .72),
            (NOSE, .64), (NOSE + .4, .36), (TAIL - .3, .36)]
    k.extrude(hull, prof, HALF * 2, axis='X', chamfer=.045, corner=.02)
    k.extrude(a.part('Hull_tub', 'Armor'), [(TAIL - .1, .3), (NOSE + .5, .3), (NOSE + .4, .42), (TAIL - .1, .42)],
              1.9, axis='X', chamfer=.02)
    g0, g1 = (NOSE + .1, .72), (NOSE + 1.05, DECK)
    ang = math.atan2(g1[1] - g0[1], g1[0] - g0[0])
    nrm = (0, -math.sin(ang), math.cos(ang))

    def on_glacis(f, x, up=.0):
        y = g0[0] + (g1[0] - g0[0]) * f
        z = g0[1] + (g1[1] - g0[1]) * f
        return (x, y - math.sin(ang) * up, z + math.cos(ang) * up)
    # The V splash board, the driver's hatch and periscope, lamps, hooks, smoke dischargers on the corners.
    sb = a.part('Splash_board', 'Armor')
    for s in (-1, 1):
        sb.box((.9, .04, .12), loc=on_glacis(.5, s * .42, .06), rot=(ang, 0, s * .45), bevel=0)
    K.hatch_round(a, (.5, NOSE + 1.3, DECK), r=.26, periscopes=1, seg=10)
    K.periscope(a, on_glacis(.92, .5, .02), facing=(0, -1, 0), size=(.18, .1, .08))
    for s in (-1, 1):
        K.lamp(a, (s * 1.02, NOSE + .5, .9), (0, -1, .1), r=.06, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .55, NOSE + .1, .5), facing=(0, -1, 0), size=.08)
        K.fender(a.part('Fenders', 'Team'), TX + .02, NOSE + .15, NOSE + .7, .88, .52, s, lip=.035)
        K.smoke_dischargers(a, 1.05, NOSE + .95, DECK + .02, s, count=3)
    # Engine deck grilles, the exhaust on the left side, the two fuel drums on the rear, tail lamps.
    K.grille(a, (.5, 2.0, DECK + .01), .8, .9, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.grille(a, (-.5, 2.0, DECK + .01), .8, .9, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.grille(a, (HALF + .01, 2.35, .9), .45, .22, facing=(1, 0, 0), slats=3, frame_mat='Armor')
    a.pivot('Point_exhaust', (.6, 3.05, .9))
    K.soot(a, (HALF + .05, 2.35, .9), radius=.55, k=.45)
    a.pivot('Point_fire', (0, 0, 1.4))
    drums = a.part('Fuel_drums', 'Armor')
    bands = a.part('Drum_bands', 'Steel')
    for x in (-.55, .55):
        K.fuel_drum(drums, bands, (x - .44, TAIL + .22, .78), r=.22, h=.88, lying=True)
    a.part('Racks', 'Steel').tube([(-1.1, TAIL + .05, .55), (-1.1, TAIL + .42, .55), (1.1, TAIL + .42, .55),
                                   (1.1, TAIL + .05, .55)], .02, seg=4)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .06), loc=(s * 1.05, TAIL + .03, .95), bevel=0)
        a.part('Team_band', 'Team').box((.012, 3.4, .11), loc=(s * (HALF + .006), 0, .95), bevel=0)
    K.tow_cable(a.part('Tow_cable', 'Steel'), [(1.32, -1.6, .98), (1.35, 0, .98), (1.32, 1.6, .98)], r=.025)
    # Stowage boxes on the fenders (left front, right rear), a tarp roll.
    P.toolbox(a, (-(TX + .1), -2.1, DECK + .1), (.36, .8, .24), mat='Armor')
    P.toolbox(a, (TX + .1, 2.2, DECK + .1), (.36, .9, .24), mat='Armor')
    k.block(a.part('Stowage', 'Canvas'), (.34, .7, .22), loc=(-(TX + .1), 2.2, DECK + .12), chamfer=.05,
            taper=(.9, .85))


def _skirts(a):
    for s in (-1, 1):
        sk = a.part('Skirts', 'Rubber')
        for i in range(6):
            yc = NOSE + .9 + i * .78
            k.block(sk, (.03, .8, .45), loc=(s * (TX + .26), yc, .64), chamfer=0)
        a.part('Skirt_edge', 'Steel').box((.035, 5.0, .05), loc=(s * (TX + .26), NOSE + 2.95, .88), bevel=0)


def _bridge(a):
    """The folded scissor bridge: two halves of two box treadways each, the upper reversed on the lower."""
    br = a.part('Bridge', 'Team')
    truss = a.part('Bridge_truss', 'Steel')
    ribs = a.part('Bridge_ribs', 'Armor')
    plates = a.part('Tread_plates', 'Steel')
    y0, y1 = NOSE + 1.15, TAIL + .45
    L = y1 - y0
    yc = (y0 + y1) / 2
    for level, z in enumerate((DECK + .36, DECK + .72)):
        for s in (-1, 1):
            x = s * .9
            # The treadway: a box girder tapering at both ends (ramps), its walkway on top.
            prof = [(y0, z - .12), (y0 + .5, z - .16), (y1 - .5, z - .16), (y1, z - .12), (y1, z + .12),
                    (y0, z + .12)]
            k.extrude(br, prof, 1.14, loc=(x, 0, 0), axis='X', chamfer=.025, corner=.01)
            # Truss sides: diagonal bracing on the outer and inner faces.
            for side in (-1, 1):
                xs = x + side * .58
                n = 9
                for i in range(n):
                    ya = y0 + .4 + i * (L - .8) / n
                    yb = ya + (L - .8) / n
                    truss.tube([(xs, ya, z - .1), (xs, yb, z + .1)], .016, seg=4)
                truss.tube([(xs, y0 + .3, z + .11), (xs, y1 - .3, z + .11)], .018, seg=4)
            # Cross ribs and the anti-slip tread plates on the walkway.
            for i in range(7 if level else 0):
                ribs.box((1.1, .05, .03), loc=(x, y0 + .6 + i * (L - 1.2) / 6, z + .135), bevel=0)
            if level:
                for i in range(4):
                    plates.box((.9, .7, .012), loc=(x, y0 + 1.1 + i * (L - 2.2) / 3, z + .128), bevel=0)
    # The hinge knuckles at the rear between the halves, the locking pins.
    hinges = a.part('Bridge_hinges', 'Steel')
    for x in (-1.3, -.5, .5, 1.3):
        hinges.cyl(.11, .22, loc=(x, y1 - .1, DECK + .54), rot=(0, R90, 0), seg=10, bevel=0)
    # The launching boom: a pivot bracket at the front, the boom under the bridge, the two hydraulic rams + hoses.
    boom = a.part('Boom', 'Armor')
    k.block(boom, (1.3, .55, .3), loc=(0, NOSE + .55, DECK + .02), chamfer=.04)
    boom.cyl(.12, 1.5, loc=(0, NOSE + .55, DECK + .2), rot=(0, R90, 0), seg=10, bevel=0)
    k.block(boom, (.5, 3.2, .14), loc=(0, NOSE + 2.4, DECK + .08), chamfer=.03)
    rams = a.part('Rams', 'Steel')
    hoses = a.part('Kit_cables', 'Rubber')
    for s in (-1, 1):
        rams.limb((s * .45, NOSE + 1.6, DECK + .05), (s * .45, NOSE + .65, DECK + .2), .12, .12, bevel=0)
        rams.cyl(.04, .7, loc=(s * .45, NOSE + .9, DECK + .17), rot=(R90 + .15, 0, 0), seg=6, bevel=0)
        hoses.tube([(s * .55, NOSE + 1.5, DECK + .05), (s * .7, NOSE + 1.8, DECK + .02), (s * .7, NOSE + 2.4, DECK + .02)],
                   .02, seg=4)
    a.part('Team_band', 'Team').box((.012, L - 1.0, .1), loc=(1.48, yc, DECK + .72), bevel=0)
    a.part('Team_band', 'Team').box((.012, L - 1.0, .1), loc=(-1.48, yc, DECK + .72), bevel=0)


def _rws(a):
    """The commander's cupola on the front right with the 12.7 mm on a raised mount (`Turret`)."""
    k.lathe(a.part('Cupola', 'Armor'), [(.34, 0), (.34, .12), (.28, .18), (0, .18)], loc=(1.0, -2.3, DECK - .02), seg=12,
            worn=(1,))
    for i in range(3):
        u = -R90 + (i - 1) * .6
        K.periscope(a, (1.0 + math.cos(u) * .28, -2.3 + math.sin(u) * .28, DECK + .1),
                    facing=(math.cos(u), math.sin(u), 0), size=(.1, .08, .07))
    P.raised_gun(a, (1.0, -2.3, 1.08), parent=None, pivot='Turret', barrel='Main_cannon', brake='Muzzle_brake',
                 muzzle='Muzzle_main', riser=-.04, ring_r=.2, post=.06, length=.7, shield=False, ring=False,
                 mat='Armor', tag='')
    k.block(a.part('Hmg_ammo', 'Crate'), (.14, .32, .2), loc=(1.35, -2.3, DECK + .1), chamfer=.012)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.1, 2.5, DECK), h=.5, r=.02, lean=.15)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.1, 2.5, DECK), h=.45, r=.02, lean=.15)


def bridging_vehicle(a):
    """The bridgelayer: see the module docstring."""
    _hull(a)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(2.42, .55, .25), idler=(-2.58, .5, .24), rollers=(),
                roller_z=.8, wheel_w=.15, hide_top=(-2.4, 2.2, .7), disc_mat='Armor', wheel_seg=9)
    _skirts(a)
    _bridge(a)
    _rws(a)
    k.clean(a)


BUILDERS = {
    'bridging_vehicle': (bridging_vehicle, dict(ao_distance=.5, grime_height=.55)),
}
