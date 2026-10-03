"""Prompt 35 wave 1 (lane B): the swarm carrier rebuilt from scratch (spec: Tools/blender/specs/swarm_carrier.json).

A C-130J Super Hercules (0.4 x real, the def's modelSize 11.93 x 16.3 x 4.79 m; the sheet: "four-engined high-wing
transport, high tail, the rear door open dropping drones"): the round fuselage with the stepped cockpit and its
window band, the radome, the main-gear sponsons low on both sides, the upswept tail with the cargo ramp lowered and
the drone rack on it; the straight high wing with four turboprop nacelles (chin intakes, outboard exhausts) and the
J model's six-bladed scimitar propellers; the tall fin with its dorsal fillet and rudder, the tailplane; two
stand-off missiles (the def's `jassm` loads) on underwing pylons; chaff / flare dispensers in two rows on each side
of the rear fuselage; blade antennas, beacon and navigation lights.

Its own airframe: nothing is taken from the sky gunship (an AC-130U with the four-bladed props and side guns).
Runtime nodes kept: `Propeller`, `Propeller_2`, `Propeller_3`, `Propeller_4` (spinners), `Muzzle_drone` (the ramp's
lip), `Point_exhaust`, `Point_fire`; the wrappers add `Part_wing` (mb_p34_parts) and the `Mount_Flare_*` points from
the `Flares` rows (mb_flare_mounts). Metres, +Z up, -Y front (the nose), +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_parts27 as p27

R90 = math.pi / 2
NOSE, TAIL = -5.96, 5.97
R = .86                       # the hold's radius
ZC = .1                       # the fuselage centre line
WING_Z = 1.0
ENGINES = (4.3, 2.2)          # nacelle offsets (outboard, inboard)
PROP_Y = -2.18


def _section(y, r, zc, flat=.12, top=0.0):
    """A fuselage cross-section ring: round, the floor a little flattened, `top` raises the crown (cockpit)."""
    pts = []
    for i in range(14):
        u = i * math.tau / 14
        x, z = math.cos(u) * r, math.sin(u) * r
        if z < -r * .7:
            z = -r * .7 - (z + r * .7) * flat
        if z > 0:
            z += top * (z / r)
        pts.append((x, y, zc + z))
    return pts


def _fuselage(a):
    body = a.part('Fuselage', 'Team')
    rings = [[(0, NOSE, ZC - .05)]]
    for y, r, zc, top in ((-5.8, .36, ZC - .05, 0), (-5.45, .66, ZC, 0), (-5.0, .82, ZC + .02, .12),
                          (-4.5, R, ZC + .03, .16), (-3.9, R, ZC, .04), (2.3, R, ZC, 0), (3.0, .8, ZC + .28, 0),
                          (4.0, .6, ZC + .66, 0), (5.0, .4, ZC + .98, 0), (5.7, .22, ZC + 1.15, 0)):
        rings.append(_section(y, r, zc, top=top))
    rings.append([(0, TAIL, ZC + 1.22)])
    body.loft(rings, bevel=0)
    a.part('Radome', 'Undercarriage').loft([[(0, NOSE - .02, ZC - .05)]] + [_section(-5.82, .34, ZC - .05)],
                                           bevel=0)
    # Main-gear sponsons along the lower sides, the wing-root fairing on top.
    spon = a.part('Gear_pods', 'Armor')
    for s in (-1, 1):
        k.extrude(spon, [(-1.0, -.62), (1.7, -.62), (2.1, -.35), (1.7, -.12), (-.9, -.12), (-1.3, -.38)], .3,
                  loc=(s * (R - .02), 0, 0), axis='X', chamfer=.04, corner=.06)
        a.part('Hull_dark', 'Undercarriage').box((.012, 1.9, .03), loc=(s * (R + .13), .3, -.5), bevel=0)
    k.extrude(a.part('Fuselage', 'Team'), [(-1.4, WING_Z - .14), (1.3, WING_Z - .14), (1.0, WING_Z + .12),
                                                    (-1.1, WING_Z + .12)], .9, axis='X', chamfer=.04, corner=.08)
    # The cockpit window band, the crew door, the team band round the hold.
    zs = ZC + .52
    K.windscreen(a, [(-.42, -5.18, zs), (.42, -5.18, zs), (.34, -4.92, zs + .3), (-.34, -4.92, zs + .3)],
                 frame_mat='Undercarriage', wipers=2, bar=.03)
    can = a.part('Canopy', 'Glass')
    for s in (-1, 1):
        can.box((.012, .55, .2), loc=(s * .74, -4.8, zs + .1), rot=(0, s * .45, 0), bevel=0)
        can.box((.012, .2, .14), loc=(s * .8, -4.35, zs - .02), rot=(0, s * .5, 0), bevel=0)
        for y in (-3.2, -2.2, -1.2, 1.2, 1.9):                            # cargo hold portholes
            a.part('Canopy', 'Glass').cyl(.06, .02, loc=(s * (R - .005), y, ZC + .25), rot=(0, R90, 0), seg=8,
                                           bevel=0)
        a.part('Bands', 'Armor').box((.012, .9, .14), loc=(s * (R + .005), -.2, ZC + .05), bevel=0)
    a.part('Hull_dark', 'Undercarriage').box((.012, .45, .7), loc=(.86, -3.9, ZC - .1), bevel=0)           # crew door
    # Blade antennas, the beacon, the refuelling probe stub.
    ant = a.part('Antennas', 'Steel')
    for y in (-3.2, -.2, 3.0):
        K.blade_antenna(ant, (0, y, ZC + R + (.05 if y < 2.5 else .45)), h=.18, chord=.18)
    a.part('Nav_lights', 'TeamGlow').cyl(.06, .06, loc=(0, -1.8, WING_Z + .14), seg=8, bevel=0)
    a.pivot('Point_fire', (0, -.2, WING_Z))


def _ramp(a):
    """The rear cargo door open: the ramp lowered, the dark hold mouth, the upper door raised into the tail, the drone
    rack on the ramp with FPV drones, one dropping."""
    mouth = a.part('Hull_dark', 'Undercarriage')
    mouth.mesh([(-.72, 2.45, ZC - .55), (.72, 2.45, ZC - .55), (.5, 4.3, ZC + .55), (-.5, 4.3, ZC + .55)],
               [(0, 1, 2, 3)])
    ramp = a.part('Ramp', 'Armor')
    p0, p1 = Vector((0, 2.55, ZC - .62)), Vector((0, 4.55, -1.15))
    d = (p1 - p0)
    ang = math.atan2(d.z, d.y)
    k.block(ramp, (1.3, d.length, .06), loc=tuple((p0 + p1) / 2), rot=(ang, 0, 0), chamfer=0)
    for s in (-1, 1):
        ramp.box((.05, d.length, .14), loc=tuple((p0 + p1) / 2 + Vector((s * .63, 0, .06))), rot=(ang, 0, 0),
                 bevel=0)
        a.part('Drone_rack', 'Steel').tube([(s * .62, 3.0, ZC - .3), tuple(p0 + d * .55 + Vector((s * .62, 0, .05)))],
                                            .02, seg=4)
    a.part('Ramp', 'Armor').box((1.0, .9, .04), loc=(0, 4.1, ZC + .62), rot=(-.35, 0, 0), bevel=0)
    a.pivot('Muzzle_drone', tuple(p1 + Vector((0, .05, -.05))))
    # The drone rack: rails along the ramp, quads with their warheads, one in the air under the tail.
    rails = a.part('Drone_rack', 'Steel')
    for s in (-1, 1):
        rails.box((.04, d.length * .8, .04), loc=tuple((p0 + p1) / 2 + Vector((s * .3, 0, .07))), rot=(ang, 0, 0),
                  bevel=0)
    for i, f in enumerate((.2, .5, .8, 1.12)):
        c = p0 + d * f + Vector((0, 0, .14 if f < 1 else -.12))
        _drone(a, c, ang if f < 1 else .3, spin=i * .4)


def _drone(a, c, pitch, spin=0.0):
    fr = a.part('Drone_frames', 'Undercarriage')
    for u in (math.pi / 4, -math.pi / 4):
        fr.box((.42, .04, .025), loc=tuple(c), rot=(pitch, 0, u + spin), bevel=0)
    for i in range(4):
        u = i * R90 + math.pi / 4 + spin
        p = Vector(c) + Vector((math.cos(u) * .2, math.sin(u) * .2 * math.cos(pitch), math.sin(u) * .2 * math.sin(pitch)
                                ))
        a.part('Drone_rack', 'Steel').cyl(.035, .04, loc=tuple(p + Vector((0, 0, .02))), seg=6, bevel=0)
    a.part('Drone_warheads', 'Team').cyl(.045, .2, loc=tuple(Vector(c) + Vector((0, 0, -.04))), rot=(R90 + pitch, 0, 0),
                                         seg=6, bevel=0)
    a.part('Nav_lights', 'TeamGlow').box((.03, .03, .03), loc=tuple(Vector(c) + Vector((0, 0, .03))), bevel=0)


def _wings(a):
    w = a.part('Wings', 'Team')
    K.wing(w, (-1.0, 1.95), (-.55, 1.08), 8.15, x0=0, z=WING_Z, t=.14, dihedral=.035)
    # Flap and aileron seams along the trailing edge, team wingtips, navigation lights.
    seam = a.part('Hull_dark', 'Undercarriage')
    tipz = WING_Z + math.tan(.035) * 8.15
    for s in (-1, 1):
        for x0, x1 in ((1.0, 3.6), (3.8, 5.9), (6.1, 7.9)):
            f0, f1 = x0 / 8.15, x1 / 8.15
            ya = .95 - .42 * f0
            yb = .95 - .42 * f1
            za, zb = WING_Z + math.tan(.035) * x0 + .04, WING_Z + math.tan(.035) * x1 + .04
            seam.tube([(s * x0, ya - .3, za), (s * x1, yb - .2, zb)], .012, seg=3)
        a.part('Bands', 'Armor').box((.5, 1.0, .07), loc=(s * 7.85, -.05, tipz + .02), bevel=0)
        a.part('Nav_lights', 'TeamGlow').box((.06, .12, .05), loc=(s * 8.13, -.5, tipz + .02), bevel=0)


def _engines(a):
    nac = a.part('Nacelles', 'Armor')
    names = ('Propeller', 'Propeller_2', 'Propeller_3', 'Propeller_4')
    for i, x in enumerate((ENGINES[0], ENGINES[1], -ENGINES[1], -ENGINES[0])):
        z = WING_Z - .2
        k.lathe(nac, [(.12, PROP_Y + .18), (.24, PROP_Y + .4), (.28, PROP_Y + .9), (.27, .2), (.2, 1.0), (.08, 1.35)],
                loc=(x, 0, z), rot=K.BACKWARD, seg=10, worn=(2,))
        nac.box((.3, 2.2, .2), loc=(x, -.6, z + .2), bevel=0)                 # the pylon fairing into the wing
        K.intake(a.part('Intakes', 'Armor'), a.part('Hull_dark', 'Undercarriage'), (x, PROP_Y + .34, z - .2), .2,
                 .14, .3, facing=(0, -1, 0), lip=.025)
        side = 1 if x > 0 else -1
        k.lathe(a.part('Exhausts', 'Steel'), [(.07, 0), (.07, .25), (.06, .26)], loc=(x + side * .26, .45, z + .05),
                rot=(R90 + .3, 0, side * .5), seg=8)
        K.soot(a, (x + side * .3, .7, z + .05), radius=.6, k=.4)
        # The six-bladed scimitar propeller on its spinner (`Propeller*` spin about the nacelle axis).
        p = a.pivot(names[i], (x, PROP_Y, z))
        k.lathe(a.part('Prop_blades', 'Undercarriage', p), [(0, -.32), (.1, -.24), (.15, -.06), (.16, .1)], rot=K.BACKWARD,
                seg=10, worn=(2,))
        bl = a.part('Prop_blades', 'Undercarriage', p)
        for j in range(6):
            u = j * math.tau / 6 + i * .2
            prof = [(.0, -.06), (.3, -.075), (.6, -.04), (.8, .03), (.82, .06), (.6, .05), (.3, .06), (.0, .05)]
            pts = []
            for rr, t in prof:
                cu, su = math.cos(u), math.sin(u)
                pts.append((rr * cu - t * su, rr * su + t * cu))
            k.extrude(bl, pts, .025, loc=(0, -.05, 0), rot=(R90, 0, 0), axis='Z')
    a.pivot('Point_exhaust', (ENGINES[0] + .3, .7, WING_Z - .15))


def _tail(a):
    fin = a.part('Tail_fin', 'Team')
    K.fin(fin, (3.35, 2.45), (4.95, 1.0), 2.35, x=0, z0=ZC + 1.0, t=.1)
    k.extrude(fin, [(2.6, ZC + .8), (3.6, ZC + .8), (3.6, ZC + 1.25)], .2, axis='X', chamfer=.02)     # dorsal fillet
    a.part('Hull_dark', 'Undercarriage').tube([(0, 4.75, ZC + 1.15), (0, 5.4, ZC + 3.3)], .014, seg=3)
    a.part('Bands', 'Armor').box((.13, .9, .28), loc=(0, 4.95, ZC + 2.7), rot=(.35, 0, 0), bevel=0)
    tp = a.part('Tailplanes', 'Team')
    K.wing(tp, (4.35, 1.5), (5.15, .7), 3.1, x0=0, z=ZC + 1.12, t=.1)
    a.part('Nav_lights', 'TeamGlow').box((.05, .05, .08), loc=(0, TAIL - .02, ZC + 1.25), bevel=0)


def _stores(a):
    """Two stand-off missiles on underwing pylons between the engines and the tips; flare dispensers aft."""
    py = a.part('Pylons', 'Armor')
    for s in (-1, 1):
        x = s * 6.0
        zw = WING_Z + math.tan(.035) * 6.0 - .08
        K.pylon(py, x, -.85, .2, zw, zw - .22, w=.08)
        zm = zw - .34
        body = a.part('Missiles', 'Armor')
        k.extrude(body, [(-.13, -.07), (.13, -.07), (.09, .08), (-.09, .08)], 1.6, loc=(x, -.3, zm), axis='Y',
                  chamfer=.02, taper=.9)
        k.lathe(a.part('Missiles', 'Armor'), [(.1, 0), (.06, .18), (0, .24)], loc=(x, -1.1, zm), rot=K.FORWARD,
                seg=4)
        a.part('Missiles', 'Armor').box((.7, .5, .015), loc=(x, -.25, zm + .085), bevel=0)        # folded wing
        a.part('Missiles', 'Armor').box((.015, .22, .18), loc=(x, .42, zm + .12), bevel=0)
    for s in (-1, 1):
        for y in (2.0, 2.65):
            K.flare_dispenser(a, (s * (R - .12), y, ZC - .48), normal=(s * .5, 0, -.86), cols=3, rows=2, cell=.06)


def swarm_carrier(a):
    """The swarm carrier: see the module docstring."""
    _fuselage(a)
    _ramp(a)
    _wings(a)
    _engines(a)
    _tail(a)
    _stores(a)
    k.clean(a)


BUILDERS = {
    'swarm_carrier': (swarm_carrier, dict(ao_distance=.6, grime_height=.0, ground=False)),
}
