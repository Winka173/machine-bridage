"""Prompt 35 wave 10 (lane B): the visual jammer (dazzler / decoy-light post) rebuilt to prompt 35's standard (spec:
Tools/blender/specs/visual_jammer.json), keeping what fix L8 got right (DECISIONS "Sửa lỗi tổng hợp L8"): the cast
pad, the ribbed control shelter with a sandbag blast wall in front, the tall braced mast carrying the floodlight head
(lamp panels round a drum), the smoke-generator drums on their rack, the generator, the camouflage net over the
shelter's rear and the aerials, at the def's modelSize 6.0 x 5.0 x 6.5 m (fort Medium, Utility; unarmed).

Prompt 35 adds what the scan asked for (one flat block, tiers 0.19 of the tower gold, symmetric): the pad battered
on every side with a cut corner, the shelter under a mono-pitch roof with its overhang, ribs, door, louvres and
air-conditioner, a ladder to the roof, the mast as a four-legged lattice with X-bracing, a rest platform and the
dazzler head: a turning drum of glowing lamp panels with its hood, two strobe bars and a laser box below; cable
runs down the mast, the drum rack with valves and hoses to the smoke nozzles, the generator with exhaust and fuel,
the net on poles with scrim, sandbags, floodlights, a beacon.

No runtime node (the old file had none). Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and lane B's
helpers; no other model's builder. Metres, +Z up, -Y front, +X left. Under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
G = .15
MX, MY = -1.3, .4      # mast centre
MT = 5.4               # mast top (the head's base)


def _pad(a):
    k.extrude(a.part('Base', 'Concrete'), [(-2.95, -2.45), (2.95, -2.45), (2.95, 1.6), (2.1, 2.45), (-2.95, 2.45)],
              G, loc=(0, 0, G / 2), axis='Z', corner=.06, taper=(.94, .93), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for v in (-1.2, 0, 1.2):
        j.box((5.7, .03, .01), loc=(0, v, G + .003), bevel=0)
    for v in (-1.5, 0, 1.5):
        j.box((.03, 4.7, .01), loc=(v, 0, G + .003), bevel=0)


def _shelter(a):
    """The control shelter on the left: walls, mono-pitch roof, ribs, door, louvres, A/C, ladder, blast wall."""
    sx, sy, w, d, h = 1.4, .7, 2.6, 2.2, 2.0
    W.slab(a.part('Shelter', 'Plaster'), (w, d, h), (sx, sy, G), caps=(False, False))
    # Mono-pitch roof falling to the rear, its overhang and fascia.
    k.extrude(a.part('Roof', 'Armor'), [(-d / 2 - .2, 0), (d / 2 + .2, 0), (d / 2 + .2, .08), (-d / 2 - .2, .38),
                                        (-d / 2 - .2, .3)], w + .3, loc=(sx, sy, G + h), axis='X',
              chamfer=.015)
    ribs = a.part('Shelter_ribs', 'Undercarriage')
    for i in range(6):
        x = sx - w / 2 + .2 + i * (w - .4) / 5
        ribs.box((.06, d + .04, h * .95), loc=(x, sy, G + h / 2), bevel=0)
    K.door(a, (sx + .6, sy - d / 2 - .02, G + .02), (.8, 1.7), normal=(0, -1, 0), mat='Armor')
    K.grille(a, (sx - .6, sy - d / 2 - .03, G + 1.4), .7, .4, facing=(0, -1, 0), slats=5)
    k.block(a.part('Ac_unit', 'PlasterWhite'), (.2, .7, .55), loc=(sx + w / 2 + .1, sy, G + 1.1), chamfer=.02)
    K.grille(a, (sx + w / 2 + .21, sy, G + 1.1), .55, .4, facing=(1, 0, 0), slats=4)
    a.part('Team_band', 'Team').box((w + .02, d + .02, .16), loc=(sx, sy, G + h - .35), bevel=0)
    K.ladder(a.part('Ladders', 'Steel'), (sx - w / 2 - .02, sy + .6, G), (sx - w / 2 - .02, sy + .6, G + h + .5),
             width=.45, step=.3, r=.02)
    K.lamp(a, (sx + .6, sy - d / 2 - .05, G + 1.95), facing=(0, -1, -.3), r=.06)
    K.rivet_line(a.part('Kit_rivets', 'Steel'), (sx - w / 2, sy - d / 2 - .01, G + .15),
                 (sx + w / 2, sy - d / 2 - .01, G + .15), (0, -1, 0), pitch=.22, r=.014)
    K.whip_antenna(a.part('Antennas', 'Steel'), (sx + 1.1, sy + .9, G + h + .3), h=1.4, r=.022)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (sx + .3, sy + .5, G + h + .75), w=.5, h=.4, normal=(0, -1, .1))
    # The sandbag blast wall in front of the shelter.
    P.sandbag_run(a, [(.2, -1.6, G), (2.75, -1.6, G), (2.75, -.9, G)], courses=3, bag=(.55, .3, .15), seed=21,
                  lean=True)


def _mast(a):
    """The four-legged lattice mast with X-bracing, rest platform, cable runs and the dazzler head."""
    ms = a.part('Mast', 'Steel')
    b, t_ = .55, .25
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    for sx, sy in corners:
        ms.tube([(MX + sx * b, MY + sy * b, G), (MX + sx * t_, MY + sy * t_, MT)], .04, seg=4)
        k.block(a.part('Footings', 'Concrete'), (.3, .3, .15), loc=(MX + sx * b, MY + sy * b, G + .075), chamfer=.02)
    zs = [G + .2 + i * .9 for i in range(6)] + [MT]
    br = a.part('Mast_bracing', 'Steel')
    for z0, z1 in zip(zs, zs[1:]):
        f0 = b + (t_ - b) * (z0 - G) / (MT - G)
        f1 = b + (t_ - b) * (z1 - G) / (MT - G)
        for i in range(4):
            p, q = corners[i], corners[(i + 1) % 4]
            br.tube([(MX + p[0] * f0, MY + p[1] * f0, z0), (MX + q[0] * f1, MY + q[1] * f1, z1)], .012, seg=3,
                    caps=False)
            br.tube([(MX + q[0] * f0, MY + q[1] * f0, z0), (MX + p[0] * f1, MY + p[1] * f1, z1)], .012, seg=3,
                    caps=False)
        ring = [(MX + c[0] * f1, MY + c[1] * f1, z1) for c in corners]
        br.tube(ring + ring[:1], .015, seg=3, caps=False)
    k.lathe(a.part('Mast_platform', 'Steel'), [(.7, -.05), (.7, .02), (0, .02)], loc=(MX, MY, G + 3.8), seg=8)
    K.railing(a.part('Railings', 'Steel'), [(MX + .65 * math.cos(u), MY + .65 * math.sin(u), G + 3.82)
                                            for u in (i * TAU / 8 + .4 for i in range(7))], h=.6, post=.5, r=.012)
    a.part('Kit_cables', 'Undercarriage').tube([(MX + .3, MY - .3, MT), (MX + .5, MY - .5, G + .4),
                                                (.2, MY - .2, G + .3), (.1, MY + .1, G + 1.0)], .025, seg=3)
    # The dazzler head: a turning drum of lamp panels under its hood, two strobe bars, the laser box below.
    k.lathe(a.part('Head_drum', 'Armor'), [(.3, 0), (.42, .05), (.42, .7), (.3, .78), (0, .8)], loc=(MX, MY, MT),
            seg=10, worn=(2,))
    lamps = a.part('Lamps', 'Lamp')
    rims = a.part('Lamp_rims', 'Steel')
    for i in range(8):
        u = i * TAU / 8
        c, s = math.cos(u), math.sin(u)
        lamps.box((.22, .03, .26), loc=(MX + c * .44, MY + s * .44, MT + .4), rot=(0, 0, u + R90), bevel=0)
        rims.box((.26, .04, .04), loc=(MX + c * .43, MY + s * .43, MT + .56), rot=(0, 0, u + R90), bevel=0)
    k.lathe(a.part('Head_hood', 'Team'), [(.55, MT + .82), (.5, MT + .9), (.2, MT + 1.0), (0, MT + 1.02)],
            loc=(MX, MY, 0), seg=10)
    for s in (-1, 1):
        a.part('Strobe_bars', 'Armor').box((.12, .7, .1), loc=(MX + s * .55, MY, MT - .25), bevel=0)
        a.part('Lamps', 'Lamp').box((.03, .6, .06), loc=(MX + s * .62, MY, MT - .25), bevel=0)
    k.block(a.part('Laser_box', 'Armor'), (.3, .4, .25), loc=(MX, MY - .2, MT - .55), chamfer=.02)
    a.part('Glass', 'Glass').cyl(.07, .02, loc=(MX, MY - .41, MT - .55), rot=(R90, 0, 0), seg=8, bevel=0)
    K.beacon(a, (MX, MY, MT + 1.02), r=.06)


def _smoke_and_power(a):
    """The smoke-generator drums on their rack with hoses to two nozzles, the generator, fuel."""
    rack = a.part('Racks', 'Steel')
    rx, ry = -1.9, -1.6
    rack.box((1.6, .8, .05), loc=(rx, ry, G + .3), bevel=0)
    for dx in (-.75, .75):
        for dy in (-.35, .35):
            rack.box((.05, .05, .3), loc=(rx + dx, ry + dy, G + .15), bevel=0)
    for i in range(3):
        K.fuel_drum(a.part('Smoke_drums', 'Fuel' if i != 1 else 'BarrelRed'), a.part('Drum_bands', 'Steel'),
                    (rx - .5 + i * .5, ry, G + .33), r=.22, h=.75)
        a.part('Valves', 'Steel').cyl(.04, .1, loc=(rx - .5 + i * .5, ry - .1, G + 1.12), seg=6, bevel=0)
    hose = a.part('Hoses', 'Rubber')
    for i, nx in enumerate((-2.7, -1.1)):
        hose.tube([(rx - .5 + i, ry - .1, G + 1.15), (nx, ry - .5, G + .9), (nx, ry - .7, G + .6)], .025, seg=4)
        k.lathe(a.part('Smoke_nozzles', 'Steel'), [(.04, 0), (.08, .25), (.06, .25)], loc=(nx, -2.3, G + .4),
                rot=K.FORWARD, seg=8, caps=(True, False))
        a.part('Nozzle_posts', 'Steel').box((.05, .05, .4), loc=(nx, -2.3, G + .2), bevel=0)
    gx, gy = .4, 1.7
    k.block(a.part('Generator', 'Armor'), (1.1, .7, .7), loc=(gx, gy, G + .4), chamfer=.03)
    K.grille(a, (gx - .56, gy, G + .45), .5, .4, facing=(-1, 0, 0), slats=4)
    K.exhaust(a, (gx + .3, gy + .2, G + .75), r=.04, length=.4)
    a.part('Generator_skid', 'Undercarriage').box((1.2, .8, .06), loc=(gx, gy, G + .03), bevel=0)
    K.jerrycan(a.part('Jerrycans', 'Armor'), (gx + .75, gy + .1, G))
    K.jerrycan(a.part('Jerrycans', 'Armor'), (gx + .75, gy - .2, G), rot=(0, 0, .3))
    K.floodlight(a, (2.8, 2.2, G), facing=(-.7, -1, -.4), pole=2.6)
    K.floodlight(a, (-2.8, -2.25, G), facing=(.6, 1, -.4), pole=2.2)


MERGE = {n: 'Mast' for n in ('Mast_bracing', 'Mast_platform', 'Drum_bands', 'Valves', 'Nozzle_posts', 'Smoke_nozzles',
                              'Light_poles')}
MERGE.update({n: 'Head_drum' for n in ('Strobe_bars', 'Laser_box', 'Light_housing')})
MERGE.update({n: 'Base_joints' for n in ('Generator_skid', 'Shelter_ribs')})
MERGE.update({'Footings': 'Base'})


def _turn(a):
    """Lay the post out along Y (the def's length 6 m, width 5 m): every root shape and effect point turned -90
    degrees about Z (x, y) -> (y, -x)."""
    import bmesh
    from mathutils import Matrix, Vector
    m = Matrix.Rotation(-R90, 4, 'Z')
    for (name, mat, parent), shape in a.shapes.items():
        if parent is None:
            bmesh.ops.transform(shape.bm, matrix=m, verts=shape.bm.verts[:])
    fx = getattr(a, '_fx35', [])
    for i, (kind, p, r, kk, extra) in enumerate(fx):
        if p is not None:
            fx[i] = (kind, Vector((p.y, -p.x, p.z)), r, kk, extra)


def visual_jammer(a):
    _pad(a)
    _shelter(a)
    _mast(a)
    _smoke_and_power(a)
    P.camo_net(a, [(.2, 1.9, 2.5), (2.8, 1.85, 2.4), (2.8, .3, 2.6), (.2, .5, 2.7)], .25, G, garnish=6, seed=3)
    rk = a.part('Stones', 'Rock')
    for i in range(20):
        u = i * 2.39996
        r = 2.2 + (i % 4) * .08
        sz = .07 + (i % 3) * .04
        rk.box((sz, sz * 1.3, sz * .6), loc=(math.cos(u) * r * 1.1, math.sin(u) * r * .9, G + sz * .2),
               rot=(i * .7, 0, i), bevel=0)
    for (x, y) in ((-2.5, 2.0), (2.5, -2.0), (-2.5, -2.0), (2.5, 2.0)):
        K.dust(a, (x, y, G), radius=1.3, k=.28)
    P.merge_parts(a, MERGE)
    _turn(a)
    k.clean(a)


BUILDERS = {'visual_jammer': (visual_jammer, dict(ao_distance=.6, grime_height=.4, ao_strength=.6))}
