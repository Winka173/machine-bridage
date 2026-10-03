"""Prompt 35 wave 11 (lane C): the supergun's targeting station rebuilt from scratch (spec: Tools/blender/specs/targeting_station.json).

The fire-control post of the super gun (unit_refs: the Würzburg-Riese radar, a coastal battery's rangefinder post;
the def's footprint 8 x 6.5 m, the old file's 6.5 x 8.15 x 11.0 m): a reinforced-concrete fire-control blockhouse
with battered walls, a thick chamfered roof slab, the observation slit and its visor facing the sea, the steel door
and steps at the rear, vent pipes and sandbags; the armoured rangefinder cupola on the roof with the long stereo
rangefinder arms; the Würzburg-Riese on its pedestal (`Part_radar`), the turning head (`Radar`: the yoke, the
ribbed parabolic dish with its feed on four struts, the operator's cabin behind the dish); the lattice signal mast
(`Part_antenna`: three-legged lattice, dipole arrays, the link dish, floodlights, the obstruction light, guy wires to
anchors); the cable trench, a generator and fuel drums.

Runtime nodes kept where they were: `Part_radar` (2.45, -.25, .25), `Radar` (2.45, -.25, 1.67), `Part_antenna`
(-3.0, 2.45, .25); old mesh names kept (`Radar_dish`, `Radar_yoke`, `Radar_steel`, `Radar_cable`,
`Radar_pedestal`, `Radar_ring`, `Mast`, `Mast_head`, `Mast_footing`, `Dipoles`, `Link_dish`, `Guy_wires`,
`Guy_anchors`, `Floodlights_*`, `Obstruction_light`). Metres, +Z up, -Y front (the sea side), +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau
BH = (-1.0, -.55)          # the blockhouse centre
BW, BL, BHGT = 3.4, 3.0, 2.1


def _blockhouse(a):
    x0, y0 = BH
    k.extrude(a.part('Base', 'Concrete'), [(-2.0, -1.75), (2.0, -1.75), (2.0, 1.95), (-2.0, 1.95)], .2,
              loc=(x0, y0, .1), axis='Z', chamfer=.04, corner=.1, caps=(False, True))
    walls = a.part('Walls', 'Concrete')
    k.extrude(walls, [(-BW / 2, -BL / 2), (BW / 2, -BL / 2), (BW / 2, BL / 2), (-BW / 2, BL / 2)], BHGT,
              loc=(x0, y0, .2 + BHGT / 2), axis='Z', chamfer=.06, corner=.12, taper=(.9, .88), caps=(False, True))
    # The roof slab: thicker than the walls, its edges chamfered all round (it overhangs a little).
    roof = a.part('Roof', 'Concrete')
    zr = .2 + BHGT
    k.extrude(roof, [(-1.75, -1.62), (1.75, -1.62), (1.75, 1.6), (-1.75, 1.6)], .42, loc=(x0, y0, zr + .19),
              axis='Z', chamfer=.14, corner=.22, taper=(.88, .86), ends=(True, True))
    # The observation slit with its visor, facing the sea.
    sl = a.part('Slit', 'Undercarriage')
    sl.box((2.2, .06, .22), loc=(x0, y0 - BL / 2 * .95 - .02, zr - .45), bevel=0)
    vis = a.part('Roof', 'Concrete')
    k.extrude(vis, [(0, 0), (.45, -.05), (.45, .08), (0, .2)], 2.6, loc=(x0, y0 - BL / 2 * .92, zr - .28),
              rot=(0, 0, math.pi), axis='X', chamfer=.03)
    # Rear door and steps, vent pipes, a lamp.
    K.door(a, (x0 + .7, y0 + BL / 2 * .9 + .01, .2 + 1.0), size=(.9, 1.8), normal=(0, 1, 0))
    st = a.part('Base', 'Concrete')
    for i in range(2):
        k.block(st, (1.1, .32, .1), loc=(x0 + .7, y0 + BL / 2 + .25 + i * .3, .2 - .05 - i * .1 + .05), chamfer=0)
    vp = a.part('Kit_steel', 'Steel')
    for vx, vy in ((-1.0, .7), (-.6, .9)):
        k.lathe(vp, [(.08, 0), (.08, .55), (.14, .58), (.14, .66), (0, .7)], loc=(x0 + vx, y0 + vy, zr + .36),
                seg=8, worn=(2,))
    K.lamp(a, (x0 + .7, y0 + BL / 2 * .9 + .05, 2.25), (0, 1, -.3), r=.08)
    # Sandbags along the seaward foot, a stencil band.
    K.sandbag_run(a, [(x0 - 1.8, y0 - 1.95, .2), (x0 + 1.8, y0 - 1.95, .2)], courses=2, bag=(.55, .3, .15),
                  seed=2, lean=True)
    a.part('Team_band', 'Team').box((BW * .82, .02, .25), loc=(x0, y0 - BL / 2 * .9 - .045, zr - .9),
                                    rot=(-.06, 0, 0), bevel=0)


def _rangefinder(a):
    """The armoured cupola on the roof and the stereo rangefinder arms through it."""
    x0, y0 = BH
    z = .2 + BHGT + .4
    cup = a.part('Cupola', 'Armor')
    k.lathe(cup, [(.75, 0), (.75, .12), (.7, .5), (.55, .72), (.2, .8), (0, .81)], loc=(x0, y0 - .2, z), seg=12,
            worn=(1, 3))
    k.ring(a.part('Kit_steel', 'Steel'), [(.74, -.02), (.86, -.02), (.86, .08), (.74, .1)], loc=(x0, y0 - .2, z),
           seg=12)
    rf = a.part('Rangefinder', 'Team')
    k.lathe(rf, [(.11, -1.6), (.13, -1.5), (.13, 1.5), (.11, 1.6)], loc=(x0, y0 - .3, z + .45), rot=(0, R90, 0),
            seg=8)
    for s in (-1, 1):
        k.block(rf, (.32, .3, .3), loc=(x0 + s * 1.62, y0 - .3, z + .45), chamfer=.03, ends=(True, True))
        a.part('Glass', 'Glass').box((.18, .02, .14), loc=(x0 + s * 1.62, y0 - .46, z + .45), bevel=0)
    K.periscope(a, (x0 - .3, y0 - .65, z + .55), facing=(0, -1, 0), size=(.18, .16, .14))
    K.periscope(a, (x0 + .3, y0 - .65, z + .55), facing=(0, -1, 0), size=(.18, .16, .14))
    K.bolt_ring(a.part('Kit_bolts', 'Steel'), (x0, y0 - .2, z + .1), (0, 0, 1), .8, 10, r=.03)


def _radar(a):
    """The Würzburg-Riese: pedestal (Part_radar) and the turning head (Radar)."""
    pr = a.pivot('Part_radar', (2.45, -.25, .25))
    ped = a.part('Radar_pedestal', 'Concrete', pr)
    k.extrude(ped, [(-.75, -.75), (.75, -.75), (.75, .75), (-.75, .75)], .3, loc=(0, 0, -.1), axis='Z',
              chamfer=.04, corner=.06, taper=(.85, .85))
    k.lathe(a.part('Radar_ring', 'Steel', pr), [(.45, .05), (.48, .05), (.48, .7), (.36, 1.3), (.36, 1.42),
                                                 (.5, 1.42)], seg=12, worn=(1, 4))
    r = a.pivot('Radar', (0, 0, 1.42), pr)
    yoke = a.part('Radar_yoke', 'Team', r)
    k.lathe(yoke, [(.5, 0), (.5, .1), (.3, .16)], seg=12)
    for s in (-1, 1):
        k.extrude(yoke, [(-.35, 0), (.35, 0), (.18, 1.45), (-.18, 1.45)], .1, loc=(s * .95, 0, .05), axis='X',
                  chamfer=.02)
    yoke.box((2.0, .5, .12), loc=(0, 0, .14), bevel=0)
    # The dish, raised 20 degrees, with radial ribs on its back and the feed on four struts.
    zc = 1.5
    el = math.radians(20)
    n = (0, -math.cos(el), math.sin(el))
    R = 1.7
    dish = a.part('Radar_dish', 'Steel', r)
    depth = R * .32
    rot = K.rot_to(n)
    m = K.frame((0, 0, zc), rot)
    prof = [(0, -depth * .5)] + [(R * f, depth * f * f - depth * .5) for f in (.3, .55, .8, 1.0)]
    k.lathe(dish, prof + [(R * 1.03, depth * .5 + .02)], loc=(0, 0, zc), rot=rot, seg=18, caps=(False, False))
    back = [(R * 1.03, depth * .5 - .02)] + [(R * f, depth * f * f - depth * .5 - .05) for f in (1.0, .7, .4)] + \
        [(0, -depth * .5 - .05)]
    k.lathe(dish, back, loc=(0, 0, zc), rot=rot, seg=18, caps=(False, False))
    st = a.part('Radar_steel', 'Steel', r)
    for i in range(8):
        u = i * TAU / 8
        c, s = math.cos(u), math.sin(u)
        st.limb(K._at(m, (c * .2, s * .2, -depth * .5 - .1)), K._at(m, (c * R * .98, s * R * .98, depth * .45 - .06)),
                .05, .05, bevel=0)
    tip = K._at(m, (0, 0, depth * .5 + R * .5))
    st.cyl(.09, .25, loc=tip, rot=rot, seg=8, bevel=0)
    for i in range(4):
        u = i * TAU / 4 + TAU / 8
        st.tube([K._at(m, (math.cos(u) * R * .85, math.sin(u) * R * .85, depth * .3)), tip], .02, seg=4)
    for s in (-1, 1):
        st.cyl(.1, .2, loc=(s * .95, 0, zc), rot=(0, R90, 0), seg=8, bevel=0)
    # The operator's cabin behind the dish.
    cab = a.part('Radar_cabin', 'Team', r)
    cb = K._at(m, (0, -.1, -depth * .5 - .55))
    k.block(cab, (1.0, .8, .9), loc=cb, rot=(-el, 0, 0), chamfer=.04, ends=(True, True))
    a.part('Glass', 'Glass', r).box((.5, .02, .2), loc=(cb[0], cb[1] + .41, cb[2] + .15), rot=(-el, 0, 0), bevel=0)
    a.part('Radar_cable', 'Rubber', r).tube([(.6, .2, .2), (.7, .45, .9), (cb[0] + .4, cb[1], cb[2] - .3)], .03,
                                            seg=4)
    a.part('Kit_cables', 'Rubber').tube([(1.8, .3, .25), (.6, .9, .03), (-.4, 1.0, .03), (BH[0] + 1.7, BH[1] + .2,
                                                                                         .5)], .04, seg=4)


def _mast(a):
    """The lattice signal mast (Part_antenna): three legs, zigzag braces, dipoles, link dish, lights, guys."""
    pa = a.pivot('Part_antenna', (-3.0, 2.45, .25))
    k.extrude(a.part('Mast_footing', 'Concrete', pa), [(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)], .3,
              loc=(0, 0, -.1), axis='Z', chamfer=.04, corner=.05, taper=(.85, .85))
    mast = a.part('Mast', 'Steel', pa)
    H = 9.9
    r0, r1 = .42, .26
    legs = [(math.cos(i * TAU / 3 + R90), math.sin(i * TAU / 3 + R90)) for i in range(3)]

    def p(i, z):
        rr = r0 + (r1 - r0) * z / H
        return (legs[i][0] * rr, legs[i][1] * rr, z + .05)
    for i in range(3):
        mast.limb(p(i, 0), p(i, H), .07, .07, bevel=0)
    bays = 14
    for b in range(bays):
        z0, z1 = H * b / bays, H * (b + 1) / bays
        for i in range(3):
            j = (i + 1) % 3
            mast.limb(p(i, z0), p(j, z1), .035, .035, bevel=0)
            if b % 2 == 0:
                mast.limb(p(i, z1), p(j, z1), .035, .035, bevel=0)
    head = a.part('Mast_head', 'Team', pa)
    k.block(head, (.7, .7, .18), loc=(0, 0, H + .14), chamfer=.03)
    dp = a.part('Dipoles', 'Steel', pa)
    for zz in (H - .6, H - 2.0):
        for i in range(3):
            u = i * TAU / 3 + R90 + TAU / 6
            c, s = math.cos(u), math.sin(u)
            dp.limb((c * .3, s * .3, zz), (c * .75, s * .75, zz), .04, .04, bevel=0)
            for dz in (-.5, .5):
                dp.limb((c * .75, s * .75, zz + dz), (c * .75, s * .75, zz), .03, .03, bevel=0)
    K.dish(a.part('Link_dish', 'Plaster', pa), mast, (.0, -.42, H - 3.2), r=.42,
           normal=(0, -1, 0), seg=12)
    K.whip_antenna(a.part('Antennas', 'Steel', pa), (.2, .2, H + .23), h=.55, r=.02)
    a.part('Obstruction_light', 'LavaGlow', pa).sphere(.09, loc=(-.15, -.1, H + .32), seg=8, rings=5)
    for s in (-1, 1):
        mast.limb((0, 0, 4.0), (s * .55, -.35, 4.05), .04, .04, bevel=0)
        k.block(a.part('Floodlights_housing', 'Armor', pa), (.32, .16, .26), loc=(s * .6, -.42, 4.0),
                rot=(-.35, 0, 0), chamfer=.02, ends=(True, True))
        a.part('Floodlights_lens', 'Lamp', pa).box((.26, .02, .2), loc=(s * .6, -.51, 3.97), rot=(-.35, 0, 0),
                                                   bevel=0)
    K.ladder(a.part('Ladders', 'Steel', pa), (0, .3, .2), (0, .2, H - .2), width=.25, step=.35)
    gw = a.part('Guy_wires', 'Rubber', pa)
    an = a.part('Guy_anchors', 'Concrete', pa)
    for i, (u, reach) in enumerate(((R90 + .4, 1.0), (R90 + 2.4, 1.05), (R90 - 1.9, 1.05))):
        c, s = math.cos(u), math.sin(u)
        foot = (c * reach, s * reach, -.15)
        for zz in (H * .5, H * .92):
            gw.tube([p(i, zz), foot], .012, seg=3)
        k.block(an, (.3, .3, .22), loc=(foot[0], foot[1], foot[2] + .11), chamfer=.03)


def _yard(a):
    """Generator and fuel drums between the radar and the mast."""
    gen = a.part('Generator', 'Team')
    gx, gy = 1.0, 2.55
    k.block(gen, (1.0, .6, .6), loc=(gx, gy, .3), chamfer=.04)
    k.extrude(gen, [(-.3, 0), (.3, 0), (.22, .12), (-.22, .12)], 1.0, loc=(gx, gy, .6), axis='X', chamfer=.01)
    K.grille(a, (gx, gy - .31, .32), .6, .3, facing=(0, -1, 0), slats=5)
    K.exhaust(a, (gx + .35, gy + .15, .72), r=.035, length=.35, direction=(0, 0, 1), muffler=False)
    band = a.part('Kit_steel', 'Steel')
    for i, (dx, dy) in enumerate(((1.9, 2.5), (2.4, 2.6), (2.15, 3.05))):
        K.fuel_drum(a.part('Fuel_drums', 'BarrelRed'), band, (dx, dy, 0), r=.27, h=.85)
    K.soot(a, (gx + .35, gy + .15, 1.05), radius=.3, k=.3)


def targeting_station(a, detail=False):
    """The targeting station: see the module docstring."""
    _blockhouse(a)
    _rangefinder(a)
    _radar(a)
    _mast(a)
    _yard(a)
    K.dust(a, (0, 0, 0), radius=4.0, k=.14)
    k.clean(a)


BUILDERS = {
    'targeting_station': (targeting_station, dict(ao_distance=.6, grime_height=.5)),
}
