"""Prompt 35 wave 6 (lane B): the sea cruiser rebuilt from scratch (spec: Tools/blender/specs/sea_cruiser.json).

The missile cruiser of Leviathan's fleet (unit_refs: Kirov-class, Iowa-class with missiles, Mk 71 203 mm; the old
file's 64 x 11 x 20.7 m, drawn at 0.72 by the data): the long flared hull with the clipper bow, the knuckle and the
sheer, the dark bottom and boot-top, the transom; two twin 203 mm turrets (`Part_gun` > `Mount_gun` forward,
`Part_gun.001` > `Mount_gun.001` aft: armoured gun houses with sighting hoods, barbettes, blast bags, long barrels
with their muzzles: the wrapper adds one muzzle a barrel), VLS fields fore and aft of the forward turret; the tall
stepped superstructure with the bridge window band, bridge wings and the flag deck, the main pyramid mast with its
yards and the spinning air-search radar (`Part_radar` > `Radar`), the fire-control directors, the point-defence
radar faces (the def's interceptor: `Mount_APS` is merged into `Aps_faces`, spec "merged", so the moving
parts stay at glb_check's cap of 10), the twin-uptake funnel, the aft lattice mast; two CIWS on
sponsons (`Part_mg` > `Mount_mg` starboard forward, `Part_mg.001` > `Mount_mg.001` port aft), the quad anti-ship
canisters, two RHIBs in davits (the boats), the hangar and the flight deck with its markings and nets aft;
railings, ladders, life-raft canisters, bollards, capstans, vents, lockers, portholes and Team bands.

Its own hull and superstructure (not sea_corvette's or the bosses'). Runtime nodes kept: `Part_gun`, `Mount_gun`,
`Muzzle_gun`, `Part_gun.001`, `Mount_gun.001`, `Muzzle_gun.001`, `Part_mg`, `Mount_mg`, `Muzzle_mg`, `Part_mg.001`,
`Mount_mg.001`, `Muzzle_mg.001`, `Part_radar`, `Radar`; static parts are folded into fewer meshes (`MERGE`). The muzzles sit at the new barrels' ends
(10.4 m ahead of the mount instead of 12.4 m: the old barrels were 30 % longer than the hull allows). The runtime
sinks ships whole (ShipSinking). Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
BOW, STERN = -32.0, 32.0
B = 5.5


def deck_z(y):
    """The main deck: 3.4 aft, rising from midships to 4.6 at the stem."""
    f = max(0.0, (-y - 4.0) / (-BOW - 4.0))
    return 3.4 + 1.2 * f ** 1.6


def half_beam(y):
    f = (y - BOW) / (STERN - BOW)
    if f < .4:
        return B * math.sin(min(1.0, f / .4) * R90) ** .7
    return B * (1 - .1 * max(0.0, f - .75) / .25)


def _hull(a):
    hull = a.part('Hull', 'Armor')
    rings = []
    ys = [STERN, 26.0, 18.0, 8.0, -4.0, -14.0, -20.0, -25.0, -28.5, -30.8, BOW + .05]
    for y in ys:
        h = max(half_beam(y), .08)
        f = max(0.0, -y / -BOW)
        wl = h * (1 - .25 * f)
        z = deck_z(y)
        keel = -2.4 + (2.0 * f ** 3 if y < -18 else 0)
        rings.append([(-h, y, z), (-h * .99, y, z - 1.2), (-wl, y, .3), (-wl * .75, y, -1.6), (-.4, y, keel),
                      (.4, y, keel), (wl * .75, y, -1.6), (wl, y, .3), (h * .99, y, z - 1.2), (h, y, z)])
    rings[-1] = [(p[0] * .04 + math.copysign(.03, p[0]), BOW - (.0 if p[2] > 1 else -1.6), p[2]) for p in rings[-1]]
    k.sharp_loft(hull, rings, chamfer=.06)
    for s in (-1, 1):
        pts = [(s * (max(half_beam(y), .08) * (1 - .25 * max(0, -y / -BOW)) + .01), y) for y in ys[:-1]]
        idx = tuple(range(len(pts) * 2))
        a.part('Hull_low', 'Undercarriage').mesh([(x, y, .0) for x, y in pts] + [(x * .85, y, -1.5) for x, y in reversed(pts)],
                                                  [idx if s < 0 else tuple(reversed(idx))])
        a.part('Boot_top', 'Hazard').mesh([(x * 1.004, y, .45) for x, y in pts] + [(x * 1.004, y, .15) for x, y in reversed(pts)],
                                          [idx if s < 0 else tuple(reversed(idx))])
        a.part('Team_band', 'Team').box((.03, 22.0, .6), loc=(s * (B + .01), -4.0, deck_z(-4.0) - .8), bevel=0)
        seams = a.part('Hull_seams', 'Undercarriage')
        for i, y in enumerate(range(-26, 30, 3)):
            seams.box((.03, .06, 2.0 + .25 * (i % 4)), loc=(s * (half_beam(y) + .01), y, deck_z(y) - 1.6), bevel=0)
        P.portholes(a, [(s * (half_beam(y) + .01), y, deck_z(y) - 1.0) for y in range(-24, 28, 6)], (s, 0, 0), r=.2,
                    seg=6)
        a.part('Hawse', 'Undercarriage').cyl(.35, .2, loc=(s * half_beam(-28.0) * .95, -28.0, deck_z(-28) - .9),
                                             rot=(0, R90, 0), seg=10, bevel=0)
    deck = a.part('Deck', 'Team')
    for y0, y1, n in ((-31.0, -8.6, 10), (14.6, 19.6, 2)):
        for i in range(n):
            ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
            ha, hb = half_beam(ya) - .08, half_beam(yb) - .08
            deck.mesh([(-ha, ya, deck_z(ya) + .01), (ha, ya, deck_z(ya) + .01), (hb, yb, deck_z(yb) + .01),
                       (-hb, yb, deck_z(yb) + .01)], [(0, 1, 2, 3)])


def _turret(a, part, mount, muzzle, at, aft):
    """A twin 203 mm turret: barbette, the armoured gun house with sighting hoods, blast bags, two long barrels."""
    a.pivot(part, at)
    m = a.pivot(mount, (0, 0, 0), part)
    sfx = '_gun' if not aft else '_gun_001'
    k.lathe(a.part('Barbette' + sfx, 'Armor', m), [(2.3, -.6), (2.3, .1), (2.15, .25), (0, .25)], seg=20, worn=(1,))
    rings = []
    for z, f, w, r in ((.25, -2.6, 1.7, 2.9), (1.7, -2.4, 1.6, 2.8), (2.3, -1.6, 1.3, 2.6)):
        rings.append([(-w * .7, f, z), (w * .7, f, z), (w, f + .9, z), (w, r, z), (-w, r, z), (-w, f + .9, z)])
    k.sharp_loft(a.part('Gunhouse' + sfx, 'Team', m), rings, chamfer=.08)
    a.part('Gunhouse_roof' + sfx, 'Armor', m).box((2.2, 3.2, .05), loc=(0, .4, 2.32), bevel=0)
    hoods = a.part('Sight_hoods' + sfx, 'Armor', m)
    for x in (-1.25, 1.25):
        k.block(hoods, (.5, .8, .35), loc=(x, -.6, 2.25), chamfer=.06)
    a.part('Rangefinder' + sfx, 'Steel', m).box((4.0, .3, .3), loc=(0, 2.0, 1.9), bevel=0)
    for x in (-.55, .55):
        k.lathe(a.part('Blast_bags' + sfx, 'Canvas', m), [(.35, 0), (.42, .15), (.38, .35), (.3, .45)],
                loc=(x, -2.55, 1.15), rot=K.FORWARD, seg=10)
        k.lathe(a.part('Barrels' + sfx, 'Steel', m), [(.24, 0), (.24, .9), (.19, 1.1), (.16, 7.6), (.17, 7.8),
                                                    (0, 7.8)], loc=(x, -2.6, 1.15), rot=K.FORWARD, seg=12,
                worn=(1, 4))
        a.part('Bores' + sfx, 'Undercarriage', m).cyl(.1, .02, loc=(x, -10.41, 1.15), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot(muzzle, (0, -10.4, 1.15), m)
    rungs = a.part('Gunhouse_fit' + sfx, 'Steel', m)
    for i in range(5):
        rungs.box((.5, .04, .04), loc=(0, 2.82, .5 + i * .3), bevel=0)


def _superstructure(a):
    sup = a.part('Superstructure', 'Team')
    z0 = deck_z(-8.0)
    tiers = ((-8.5, 14.5, z0 - .1, 7.4, B - .3, B - .6), (-7.6, 9.5, 7.4, 10.0, B - 1.0, B - 1.3),
             (-6.8, 2.5, 10.0, 12.2, B - 1.8, B - 2.1), (-5.8, -.5, 12.2, 13.6, B - 2.6, B - 2.8))
    for (y0, y1, za, zb, h0, h1) in tiers:
        rings = [[(-h0, y0, za), (h0, y0, za), (h0, y1, za), (-h0, y1, za)],
                 [(-h1, y0 + .5, zb), (h1, y0 + .5, zb), (h1, y1, zb), (-h1, y1, zb)]]
        k.sharp_loft(sup, rings, chamfer=.06)
    glass = a.part('Bridge_glass', 'Glass')
    for i in range(7):
        x = -2.4 + i * .8
        c = [(x + .36, -6.55, 10.6), (x - .36, -6.55, 10.6), (x - .34, -6.25, 11.7), (x + .34, -6.25, 11.7)]
        glass.mesh([(p[0], p[1] - .03, p[2]) for p in c], [(0, 1, 2, 3)])
    for s in (-1, 1):
        k.block(a.part('Bridge_wing', 'Team'), (2.4, 1.8, .2), loc=(s * (B - .9), -6.2, 10.0), chamfer=.04)
        a.part('Bridge_wing', 'Team').limb((s * (B - 1.4), -6.2, 7.6), (s * (B + .1), -6.2, 9.95), .25, .25, bevel=0)
        K.railing(a.part('Railings', 'Steel'), [(s * (B - 2.0), -7.1, 10.2), (s * (B + .3), -7.1, 10.2),
                                                (s * (B + .3), -5.3, 10.2)], h=.9, post=.6, r=.03)
        for y in (-5.8, -4.6, -3.4, -2.2, -1.0, .2, 1.4):
            glass.box((.03, .8, .5), loc=(s * (B - 1.92), y, 11.2), rot=(0, s * .13, 0), bevel=0)
        P.portholes(a, [(s * (B - .42), y, 5.6) for y in range(-7, 14, 3)], (s, 0, .12), r=.22, seg=6)
        P.portholes(a, [(s * (B - 1.12), y, 8.7) for y in range(-6, 9, 3)], (s, 0, .12), r=.2, seg=6)
        for y in (-3.0, 6.0, 12.0):
            a.part('Doors', 'Undercarriage').box((.03, .9, 1.8), loc=(s * (B - .36), y, 5.0), rot=(0, s * .1, 0),
                                                bevel=0)
        K.ladder(a.part('Ladders', 'Steel'), (s * (B - .7), 10.0, 7.4), (s * (B - .7), 9.7, 10.0), width=.5)
        K.railing(a.part('Railings', 'Steel'), [(s * (B - .7), -7.0, 7.4), (s * (B - .7), 14.2, 7.4)], h=.9, post=1.4,
                  r=.025)
    # The main pyramid mast, yards, the air-search radar on its pivot, the fire-control directors, APS faces.
    mast = a.part('Mast', 'Team')
    k.extrude(mast, [(-1.4, -1.2), (1.4, -1.2), (1.4, 1.2), (-1.4, 1.2)], 3.0, loc=(0, -3.0, 15.1), axis='Z',
              chamfer=.06, taper=(.55, .55))
    st = a.part('Mast_steel', 'Steel')
    st.cyl(.12, 1.2, loc=(0, -1.5, 16.0), seg=8, bevel=0)
    st.box((7.0, .3, .3), loc=(0, -3.0, 15.8), bevel=0)
    st.box((4.0, .25, .25), loc=(0, -2.2, 17.4), bevel=0)
    for x in (-2.3, -1.2, 1.2, 2.3):
        st.box((.06, .06, .9), loc=(x, -3.0, 15.4), bevel=0)
    a.pivot('Part_radar', (0, -1.5, 16.6))
    r = a.pivot('Radar', (0, 0, .6), 'Part_radar')
    k.block(a.part('Radar_array', 'Armor', r), (3.6, .35, 1.0), loc=(0, 0, .1), chamfer=.06)
    a.part('Radar_face', 'Undercarriage', r).box((3.4, .03, .8), loc=(0, -.19, .6), bevel=0)
    a.part('Radar_pedestal', 'Steel', r).cyl(.25, .5, loc=(0, 0, -.2), seg=10, bevel=0)
    faces = a.part('Aps_faces', 'Glass')
    for (nx, ny) in ((0, -1), (1, 0), (-1, 0), (0, 1)):
        faces.box((1.1, 1.0, .04), loc=(nx * .95, -3.0 + ny * .95, 14.8), rot=K.rot_to((nx, ny, .35)), bevel=0)
    for x, y, z in ((0, -6.0, 13.6), (0, 9.0, 10.0)):
        k.lathe(a.part('Directors', 'Armor'), [(.7, 0), (.7, .5), (.5, .8), (0, .8)], loc=(x, y, z), seg=12)
        K.dish(a.part('Director_dish', 'Steel'), a.part('Director_feed', 'Steel'), (x, y - .5, z + 1.2), r=.6,
               normal=(0, -1, .2), seg=12)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.0, 1.5, 12.2), h=4.0, r=.05, lean=.04)
    K.whip_antenna(a.part('Antennas', 'Steel'), (2.0, 1.5, 12.2), h=3.6, r=.05, lean=.04)
    # The twin-uptake funnel, its caps, soot; the aft lattice mast.
    k.extrude(a.part('Funnel', 'Team'), [(-1.6, -1.8), (1.6, -1.8), (1.4, 1.8), (-1.4, 1.8)], 3.4, loc=(0, 5.5, 11.6),
              axis='Z', chamfer=.06, taper=(.85, .9))
    a.part('Funnel_band', 'Undercarriage').box((2.75, 3.1, .3), loc=(0, 5.55, 12.9), bevel=0)
    for x in (-.7, .7):
        a.part('Funnel_cap', 'Steel').cyl(.45, .8, loc=(x, 5.6, 13.6), seg=10, bevel=0)
    K.soot(a, (0, 5.6, 14.0), radius=2.4, k=.55)
    lm = a.part('Mast_steel', 'Steel')
    for sx in (-1, 1):
        for sy in (-1, 1):
            lm.tube([(sx * .9, 11.5 + sy * .9, 10.0), (sx * .2, 11.5 + sy * .2, 15.0)], .08, seg=4)
    for zz in (11.5, 13.0):
        w = .9 - .7 * (zz - 10) / 5
        lm.tube([(-w, 11.5 - w, zz), (w, 11.5 - w, zz), (w, 11.5 + w, zz), (-w, 11.5 + w, zz), (-w, 11.5 - w, zz)],
                .04, seg=4)
    lm.box((3.0, .1, .1), loc=(0, 11.5, 14.4), bevel=0)


def _ciws(a, part, mount, muzzle, at, sfx):
    """A CIWS on its own sponson: the ring, the gun house, armour, six barrels and the muzzle."""
    a.pivot(part, at)
    m = a.pivot(mount, (0, 0, 0), part)
    k.lathe(a.part('CIWS_ring' + sfx, 'Steel', m), [(.8, -.3), (.8, .12), (.7, .2), (0, .2)], seg=14)
    k.extrude(a.part('CIWS_body' + sfx, 'Team', m), [(-.6, 0), (.6, 0), (.5, .75), (.1, .9), (-.1, .9), (-.5, .75)],
              1.4, loc=(0, .2, .15), axis='Y', chamfer=.04, corner=.03)
    k.lathe(a.part('CIWS_armor' + sfx, 'Armor', m), [(.24, 0), (.24, .3), (.18, .36), (0, .36)], loc=(0, -.5, .62),
            rot=K.FORWARD, seg=10)
    bar = a.part('CIWS_barrels' + sfx, 'Steel', m)
    for i in range(6):
        u = i * TAU / 6
        bar.cyl(.025, 1.7, loc=(math.cos(u) * .08, -1.65, .62 + math.sin(u) * .08), rot=K.FORWARD, seg=5, bevel=0)
    for y in (-1.0, -2.45):
        a.part('CIWS_bores' + sfx, 'Undercarriage', m).cyl(.15, .08, loc=(0, y, .62), rot=K.FORWARD, seg=10, bevel=0)
    a.part('CIWS_glass' + sfx, 'Glass', m).box((.3, .02, .15), loc=(.38, -.71, .55), bevel=0)
    a.part('CIWS_dark' + sfx, 'Undercarriage', m).box((.9, .02, .4), loc=(0, 1.62, .55), bevel=0)
    a.pivot(muzzle, (0, -2.67, .62), m)


def _weapons(a):
    _turret(a, 'Part_gun', 'Mount_gun', 'Muzzle_gun', (0, -19.0, 4.1), False)
    _turret(a, K.name('Part_gun', 1), K.name('Mount_gun', 1), K.name('Muzzle_gun', 1), (0, 16.0, 3.4), True)
    _ciws(a, 'Part_mg', 'Mount_mg', 'Muzzle_mg', (-3.0, -6.0, 9.2), '_mg')
    _ciws(a, K.name('Part_mg', 1), K.name('Mount_mg', 1), K.name('Muzzle_mg', 1), (3.0, 8.5, 8.2), '_mg_001')
    for x, y, z in ((-3.0, -6.0, 9.2), (3.0, 8.5, 8.2)):
        s = 1 if x > 0 else -1
        k.block(a.part('Sponsons', 'Armor'), (B + .55 - abs(x) + 1.1, 2.4, .3),
                loc=(x + s * (B + .55 - abs(x) - 1.1) / 2, y, z - .3), chamfer=.04)
        a.part('Sponsons', 'Armor').limb((s * (B - .3), y, z - 2.5), (s * (B + .4), y, z - .45), .3, .3, bevel=0)
    for y, z in ((-19.0, 4.1), (16.0, 3.4)):
        K.soot(a, (0, y - 10.4, z + 1.15), radius=1.2, k=.35)
    # VLS fields: forward of the turret and between it and the bridge.
    K.vls(a, (0, -25.0, deck_z(-25.0) + .05), 4, 4, cell=1.0)
    K.vls(a, (0, -12.0, deck_z(-12.0) + .05), 6, 3, cell=1.0)
    # Quad anti-ship canisters both sides abaft the funnel.
    for s in (-1, 1):
        can = a.part('Missile_canisters', 'Armor')
        for i in range(2):
            for j in range(2):
                can.box((.8, 5.0, .8), loc=(s * (2.0 + i * .9), 7.0, 7.4 + 1.0 + j * .9), rot=(-.2, 0, 0), bevel=0)
        a.part('Canister_frames', 'Steel').box((2.0, .25, 2.4), loc=(s * 2.45, 8.9, 7.4 + 1.2), bevel=0)


def _aft(a):
    # The hangar door, the flight deck with its markings, edge nets, deck lights.
    door = a.part('Hangar_door', 'Armor')
    door.box((5.0, .08, 3.4), loc=(0, 14.55, 3.4 + 1.8), bevel=0)
    slats = a.part('Door_slats', 'Undercarriage')
    for i in range(10):
        slats.box((5.0, .03, .03), loc=(0, 14.6, 3.6 + i * .33), bevel=0)
    fd = a.part('Flight_deck', 'Team')
    P.plane(fd, -(B - .3), B - .3, 20.0, STERN - .3, 3.42)
    marks = a.part('Deck_marks', 'Medical')
    k.ring(marks, [(2.6, 3.43), (2.85, 3.43), (2.85, 3.44), (2.6, 3.44)], loc=(0, 26.0, 0), seg=20)
    marks.box((.25, 10.0, .01), loc=(0, 26.0, 3.44), bevel=0)
    a.part('Deck_lines', 'Hazard').box(((B - .5) * 2, .3, .01), loc=(0, 20.4, 3.44), bevel=0)
    nets = a.part('Deck_nets', 'Steel')
    for s in (-1, 1):
        for i in range(10):
            nets.box((.7, .9, .02), loc=(s * (B + .1), 21.0 + i * 1.05, 3.3), rot=(0, s * -.2, 0), bevel=0)
        for i in range(5):
            a.part('Deck_lights', 'Lamp').box((.2, .2, .08), loc=(s * (B - .5), 21.5 + i * 2.2, 3.45), bevel=0)


def _boats_and_fittings(a):
    for s in (-1, 1):
        zx, zy = s * (B - .9 if s < 0 else B - 1.6), (2.0 if s < 0 else -1.5)
        if s < 0:
            k.block(a.part('Davit_platforms', 'Armor'), (1.8, 6.0, .25), loc=(-(B - .3), zy, 7.15), chamfer=.04)
            a.part('Davit_platforms', 'Armor').limb((-(B - .2), zy, 4.5), (-(B + .3), zy, 7.05), .3, .3, bevel=0)
        dav = a.part('Davits', 'Steel')
        for dy in (-1.8, 1.8):
            dav.tube([(s * (B - 2.3), zy + dy, 7.4), (s * (B - 2.3), zy + dy, 9.4), (zx, zy + dy, 9.4)], .1, seg=6)
        K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (zx, zy, 7.9), length=4.6, beam=1.8)
        for dy in (-1.8, 1.8):
            a.part('Kit_cables', 'Undercarriage').tube([(zx, zy + dy, 9.4), (zx, zy + dy * .8, 8.6)], .02, seg=3)
        K.railing(a.part('Railings', 'Steel'), [(s * (half_beam(y) - .1), y, deck_z(y)) for y in (-30.0, -26.0, -20.0, -14.0, -9.0)],
                  h=1.0, post=1.6, r=.03)
        K.railing(a.part('Railings', 'Steel'), [(s * (half_beam(y) - .1), y, deck_z(y)) for y in (14.8, 18.0, 19.8)],
                  h=1.0, post=1.4, r=.03)
        for y in (-2.0, -.6, 10.6, 12.0):
            k.lathe(a.part('Life_rafts', 'Medical'), [(.35, -.6), (.4, -.55), (.4, .55), (.35, .6)],
                    loc=(s * (B - .2), y, 7.9), rot=K.FORWARD, seg=10)
        bol = a.part('Bollards', 'Steel')
        for y in (-29.0, -22.0, -15.0, 17.0, 19.0):
            for dy in (-.3, .3):
                bol.cyl(.2, .5, loc=(s * (half_beam(y) - .7), y + dy, deck_z(y) + .25), seg=8, bevel=0)
        k.lathe(a.part('Capstans', 'Steel'), [(.4, 0), (.4, .1), (.3, .2), (.3, .6), (.4, .7), (0, .7)],
                loc=(s * 1.6, -27.5, deck_z(-27.5)), seg=10)
        a.part('Anchor_chain', 'Undercarriage').tube([(s * 1.6, -27.5, deck_z(-27.5) + .2),
                                                      (s * 3.0, -28.0, deck_z(-28.0) + .05)], .1, seg=4)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.3, .3, .3), loc=(s * (B - .4), -6.2, 10.4),
                                                                          bevel=0)
    P.clutter(a, 'Foredeck_fittings', 'Steel', -3.4, 3.4, -21.5, -14.0, deck_z(-18.0) + .05, 18, seed=51,
              size=(.3, 1.2), height=(.2, .8), gap=.3)
    P.clutter(a, 'Foredeck_fittings', 'Steel', -2.0, 2.0, -30.0, -27.0, deck_z(-28.5), 8, seed=52, size=(.3, .9),
              height=(.2, .6), gap=.3)
    P.clutter(a, 'Roof_fittings', 'Steel', -3.0, 3.0, 3.5, 9.3, 10.0, 16, seed=53, size=(.3, 1.2), height=(.2, 1.0),
              gap=.3)
    P.clutter(a, 'Roof_fittings', 'Steel', -2.4, 2.4, -5.0, 2.3, 12.2, 10, seed=54, size=(.3, 1.0), height=(.2, .8),
              gap=.3)
    P.clutter(a, 'Deck_lockers', 'Armor', -4.2, 4.2, 9.8, 14.2, 7.4, 14, seed=55, size=(.4, 1.4), height=(.3, 1.0),
              gap=.3)
    P.clutter(a, 'Quarterdeck_fittings', 'Steel', -4.0, 4.0, 14.8, 19.6, 3.4, 10, seed=56, size=(.3, 1.0),
              height=(.2, .6), gap=.3)


def _paint(a):
    """Deck paint and contrasting fittings (they read at the battle camera): seam lines across the foredeck,
    non-skid walkways, yellow safety lines, the VLS outlines, red fire boxes and white hose reels."""
    seams = a.part('Deck_seams', 'Undercarriage')
    for y in range(-30, -8, 2):
        h = half_beam(y) - .2
        P.plane(seams, -h, h, y - .04, y + .04, deck_z(y) + .02)
    walk = a.part('Walkways', 'Undercarriage')
    safety = a.part('Deck_lines', 'Hazard')
    for s in (-1, 1):
        for y0 in range(-29, -9, 4):
            y1 = y0 + 3.6
            x = s * (half_beam(y0 + 1.8) - 1.0)
            P.plane(walk, x - .45, x + .45, y0, y1, deck_z(y0 + 1.8) + .025)
            P.plane(safety, x - .55, x - .45, y0, y1, deck_z(y0 + 1.8) + .03)
    for (y, cols, rows) in ((-25.0, 4, 4), (-12.0, 6, 3)):
        w, d = cols * 1.0 + .5, rows * 1.0 + .5
        z = deck_z(y) + .03
        for x0, x1, y0, y1 in ((-w / 2, w / 2, y - d / 2 - .12, y - d / 2), (-w / 2, w / 2, y + d / 2, y + d / 2 + .12),
                               (-w / 2 - .12, -w / 2, y - d / 2, y + d / 2), (w / 2, w / 2 + .12, y - d / 2, y + d / 2)):
            P.plane(safety, x0, x1, y0, y1, z)
    k.block(a.part('Ladder_platform', 'Armor'), (.6, 3.2, .15), loc=(-(B + .15), 18.0, 3.2), chamfer=.03)
    K.ladder(a.part('Ladders', 'Steel'), (-(B + .3), 19.4, 1.0), (-(B + .3), 18.6, 3.25), width=.5)
    P.clutter(a, 'Fire_boxes', 'BarrelRed', -4.6, -3.6, -6.0, 13.0, 7.4, 8, seed=57, size=(.3, .6), height=(.4, .9),
              gap=.6)
    P.clutter(a, 'Hose_reels', 'Medical', 3.6, 4.6, -6.0, 13.0, 7.4, 8, seed=58, size=(.3, .7), height=(.3, .7),
              gap=.6)
    # The boat crane amidships (port): pedestal, slewing house, the jib over the RHIB.
    cr = a.part('Crane', 'CraneYellow')
    cr.cyl(.35, 2.0, loc=(3.4, -1.0, 8.4), seg=10, bevel=0)
    k.block(cr, (1.0, 1.2, .9), loc=(3.4, -1.0, 9.4), chamfer=.06)
    cr.limb((3.4, -1.2, 10.0), (4.9, 1.6, 12.2), .3, .3, bevel=0)
    a.part('Kit_cables', 'Undercarriage').tube([(4.9, 1.6, 12.2), (4.9, 1.8, 9.6)], .03, seg=3)

# Static parts folded into fewer meshes (glb_check's renderer cap): source name -> mesh it joins.
MERGE = {'Ladder_platform': 'Sponsons', 'Davit_platforms': 'Sponsons', 'Hangar_door': 'Deck_lockers',
         'Anchor_chain': 'Hull_seams', 'Hawse': 'Hull_seams', 'Deck_seams': 'Walkways', 'Door_slats': 'Walkways',
         'Doors': 'Walkways', 'Kit_cables': 'Funnel_band', 'Capstans': 'Bollards', 'Canister_frames': 'Davits',
         'Director_dish': 'Mast_steel', 'Director_feed': 'Mast_steel', 'Antennas': 'Mast_steel',
         'Funnel_cap': 'Mast_steel', 'Foredeck_fittings': 'Fittings', 'Quarterdeck_fittings': 'Fittings',
         'Roof_fittings': 'Fittings', 'Hose_reels': 'Life_rafts', 'Deck_lines': 'Boot_top',
         'Bridge_wing': 'Superstructure', 'Flight_deck': 'Deck', 'Portholes': 'Bridge_glass',
         'Gunhouse_fit_gun': 'Rangefinder_gun', 'Gunhouse_fit_gun_001': 'Rangefinder_gun_001',
         'Sight_hoods_gun': 'Barbette_gun', 'Gunhouse_roof_gun': 'Barbette_gun',
         'Sight_hoods_gun_001': 'Barbette_gun_001', 'Gunhouse_roof_gun_001': 'Barbette_gun_001',
         'CIWS_dark_mg': 'CIWS_bores_mg', 'CIWS_dark_mg_001': 'CIWS_bores_mg_001'}


def sea_cruiser(a):
    """The sea cruiser: see the module docstring."""
    K.suffixed(a)
    _hull(a)
    _superstructure(a)
    _weapons(a)
    _aft(a)
    _boats_and_fittings(a)
    _paint(a)
    P.merge_parts(a, MERGE)
    k.clean(a)


BUILDERS = {
    'sea_cruiser': (sea_cruiser, dict(ao_distance=2.0, grime_height=.6)),
}
