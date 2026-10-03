"""Prompt 35 wave 6 (lane B): the sea corvette rebuilt from scratch (spec: Tools/blender/specs/sea_corvette.json).

An escort corvette of 30 m (unit_refs: OTO Melara 76/62, AK-630; Buyan-M / Steregushchiy layout at small scale): the
flared hull with its raked stem, the knuckle and sheer rising to the bow, the dark bottom and boot-top, the transom;
the foredeck with the anchor gear and breakwater, the 76 mm in its faceted stealth gun house (`Part_gun` >
`Mount_gun` > `Muzzle_gun`), an eight-cell VLS block behind it; the stepped superstructure in three tiers with the
bridge's window band and bridge wings, the integrated pyramid mast with its yards, the spinning search radar
(`Radar`) and the point-defence radar faces (`Mount_APS`: the def's interceptor), the funnel with its cap and
exhausts, two quad anti-ship canister launchers amidships; the hangar aft with its roller door, the AK-630 on the
hangar roof (`Part_mg` > `Mount_mg` > `Muzzle_mg`); the RHIB in its davit (the boat), life-raft canisters,
railings, ladders, bollards, fairleads, vents, deck lockers, portholes and Team bands.

Its own hull and superstructure (not sea_cruiser's or the bosses'). Runtime nodes kept: `Part_gun`, `Mount_gun`,
`Muzzle_gun`, `Part_mg`, `Mount_mg`, `Muzzle_mg`, `Radar`; new: `Mount_APS`; old part names `Hull`, `Deck`,
`Superstructure`, `Bridge_glass`, `Mast`, `Funnel`, `Funnel_cap`, `Hangar`, `Hangar_door`, `Gun_house`,
`Gun_barrel`, `Boot_top`, `Rails`, `CIWS_*`, `Radar_*`. The runtime sinks ships whole (ShipSinking); the hull is one
piece. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
BOW, STERN = -15.0, 15.0
B = 2.8                          # half beam at the deck


def deck_z(y):
    """The main deck's height: 2.3 aft, the sheer rising to 3.0 at the stem."""
    f = max(0.0, (-y - 2.0) / (-BOW - 2.0))
    return 2.3 + .7 * f * f


def half_beam(y):
    f = (y - BOW) / (STERN - BOW)          # 0 stem .. 1 stern
    if f < .45:
        return B * math.sin(min(1.0, f / .45) * R90) ** .75
    return B * (1 - .06 * (f - .45))


def _hull(a):
    hull = a.part('Hull', 'Armor')
    rings = []
    ys = [STERN, 12.0, 8.0, 3.0, -2.0, -6.0, -9.0, -11.5, -13.3, -14.4, BOW + .05]
    for y in ys:
        h = max(half_beam(y), .08)
        f = max(0.0, (-y) / -BOW)
        wl = h * (1 - .22 * f)                    # the waterline narrower forward (flare)
        z = deck_z(y)
        keel = -1.4 + (1.2 * f ** 3 if y < -9 else 0)
        rings.append([(-h, y, z), (-h * .98, y, z - .6), (-wl, y, .2), (-wl * .7, y, -.9), (0, y, keel),
                      (wl * .7, y, -.9), (wl, y, .2), (h * .98, y, z - .6), (h, y, z)])
    rings[-1] = [(math.copysign(.03, p[0]), BOW, p[2]) if abs(p[0]) > 0 else p for p in rings[-1]]
    k.sharp_loft(hull, rings, chamfer=.04)
    for s in (-1, 1):
        pts = [(s * (max(half_beam(y), .08) * (1 - .22 * max(0, -y / -BOW)) + .01), y) for y in ys[:-1]]
        a.part('Hull_low', 'Undercarriage').mesh(
            [(x, y, .0) for x, y in pts] + [(x * .8, y, -.85) for x, y in reversed(pts)],
            [tuple(range(len(pts) * 2)) if s < 0 else tuple(reversed(range(len(pts) * 2)))])
        a.part('Boot_top', 'Hazard').mesh(
            [(x * 1.005, y, .28) for x, y in pts] + [(x * 1.005, y, .1) for x, y in reversed(pts)],
            [tuple(range(len(pts) * 2)) if s < 0 else tuple(reversed(range(len(pts) * 2)))])
        a.part('Team_band', 'Team').box((.02, 8.0, .4), loc=(s * (half_beam(-4.0) + .01), -4.0, deck_z(-4.0) - .45),
                                        bevel=0)
    # Hull plating seams and the knuckle strake, portholes forward, the hawse pipes.
    seams = a.part('Hull_seams', 'Undercarriage')
    for s in (-1, 1):
        for i, y in enumerate(range(-12, 14, 2)):
            h = half_beam(y)
            seams.box((.015, .03, 1.1 + .1 * (i % 3)), loc=(s * (h + .005), y, deck_z(y) - 1.0), bevel=0)
        P.portholes(a, [(s * (half_beam(y) + .005), y, deck_z(y) - .7) for y in (-10.5, -9.5, -8.5, 9.5, 10.5)],
                    (s, 0, 0), r=.13)
        a.part('Hawse', 'Undercarriage').cyl(.18, .1, loc=(s * (half_beam(-13.0) * .95), -13.0, deck_z(-13) - .5),
                                             rot=(0, R90, 0), seg=8, bevel=0)
    # The decks: foredeck and quarterdeck plates (one-sided), the breakwater.
    deck = a.part('Deck', 'Team')
    for y0, y1 in ((-14.4, -6.3), (9.2, STERN - .05)):
        n = 6
        for i in range(n):
            ya, yb = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
            ha, hb = half_beam(ya) - .05, half_beam(yb) - .05
            deck.mesh([(-ha, ya, deck_z(ya) + .01), (ha, ya, deck_z(ya) + .01), (hb, yb, deck_z(yb) + .01),
                       (-hb, yb, deck_z(yb) + .01)], [(0, 1, 2, 3)])
    bw = a.part('Breakwater', 'Armor')
    for s in (-1, 1):
        bw.box((2.2, .08, .45), loc=(s * .9, -11.3, deck_z(-11.3) + .2), rot=(0, 0, s * -.35), bevel=0)


def _gun(a):
    """The 76 mm forward: the stealth gun house on its own pivot (`Part_gun` > `Mount_gun`), the barrel."""
    a.pivot('Part_gun', (0, -9.0, 2.6))
    m = a.pivot('Mount_gun', (0, 0, 0), 'Part_gun')
    k.lathe(a.part('Gun_ring', 'Steel', m), [(1.2, 0), (1.2, .12), (1.1, .2), (0, .2)], seg=16)
    rings = []
    for z, f, w, r in ((.15, -1.0, 1.05, 1.5), (1.0, -.7, .95, 1.45), (1.45, -.2, .6, 1.2)):
        rings.append([(-w * .5, f, z), (w * .5, f, z), (w, f + .6, z), (w, r, z), (-w, r, z), (-w, f + .6, z)])
    k.sharp_loft(a.part('Gun_house', 'Team', m), rings, chamfer=.05)
    k.lathe(a.part('Gun_barrel', 'Steel', m), [(.14, 0), (.14, .2), (.09, .3), (.075, 3.3), (0, 3.3)],
            loc=(0, -.8, .85), rot=K.FORWARD, seg=12, worn=(1,))
    k.lathe(a.part('Gun_brake', 'Undercarriage', m), [(.075, 0), (.11, .04), (.11, .3), (.08, .34), (0, .34)],
            loc=(0, -4.05, .85), rot=K.FORWARD, seg=12)
    a.pivot('Muzzle_gun', (0, -4.2, .85), m)
    a.part('Gun_vents', 'Undercarriage', m).box((.6, .02, .2), loc=(0, 1.5, .9), bevel=0)
    K.soot(a, (0, -13.2, 3.45), radius=.7, k=.35)
    # The eight-cell VLS block behind the gun, the anchor gear on the foredeck.
    K.vls(a, (0, -6.9, deck_z(-6.9) + .05), 4, 2, cell=.55)
    for s in (-1, 1):
        k.lathe(a.part('Windlass', 'Steel'), [(.3, -.2), (.3, -.15), (.2, -.1), (.2, .1), (.3, .15), (.3, .2)],
                loc=(s * .8, -12.3, deck_z(-12.3) + .35), rot=(0, R90, 0), seg=10)
        a.part('Anchor_chain', 'Undercarriage').tube([(s * .8, -12.3, deck_z(-12.3) + .1),
                                                      (s * 1.6, -13.0, deck_z(-13.0) + .03)], .06, seg=4)


def _superstructure(a):
    sup = a.part('Superstructure', 'Team')
    z0 = deck_z(-6.0)
    # Three tiers, their walls leaning in (the stealth faceting), the bridge on the second tier.
    for (y0, y1, za, zb, h0, h1) in ((-6.0, 4.0, z0 - .1, 4.6, B - .2, B - .5), (-5.4, 1.5, 4.6, 6.4, B - .6, B - .9),
                                     (-4.6, -1.2, 6.4, 7.6, B - 1.1, B - 1.3)):
        rings = [[(-h0, y0, za), (h0, y0, za), (h0, y1, za), (-h0, y1, za)],
                 [(-h1, y0 + .45, zb), (h1, y0 + .45, zb), (h1, y1, zb), (-h1, y1, zb)]]
        k.sharp_loft(sup, rings, chamfer=.04)
    # The bridge window band on the front of the second tier, side windows, the bridge wings.
    glass = a.part('Bridge_glass', 'Glass')
    for i in range(5):
        x = -1.4 + i * .7
        c = [(x + .32, -5.32, 5.35), (x - .32, -5.32, 5.35), (x - .3, -5.1, 6.0), (x + .3, -5.1, 6.0)]
        glass.mesh([(p[0], p[1] - .03, p[2]) for p in c], [(0, 1, 2, 3)])
    for s in (-1, 1):
        for y in (-4.3, -3.3, -2.3):
            glass.box((.02, .7, .4), loc=(s * (B - .78), y, 5.7), rot=(0, s * .17, 0), bevel=0)
        k.block(a.part('Bridge_wings', 'Team'), (.9, 1.0, .12), loc=(s * (B - .2), -4.6, 4.95), chamfer=.03)
        K.railing(a.part('Rails', 'Steel'), [(s * (B - .7), -5.1, 5.07), (s * (B + .25), -5.1, 5.07),
                                             (s * (B + .25), -4.1, 5.07)], h=.7, post=.5, r=.02)
        P.portholes(a, [(s * (B - .35), y, 3.3) for y in (-4.5, -2.5, -.5, 1.5, 3.2)], (s, .0, .15), r=.13)
        for y in (-3.4, 2.4):
            a.part('Doors', 'Undercarriage').box((.02, .8, 1.6), loc=(s * (B - .27), y, 3.3), rot=(0, s * .1, 0),
                                                bevel=0)
    # The integrated pyramid mast: a faceted tower on the third tier, yards, the radar on top, APS faces.
    mast = a.part('Mast', 'Team')
    k.extrude(mast, [(-.9, -.8), (.9, -.8), (.9, .8), (-.9, .8)], 2.2, loc=(0, -2.9, 8.7), axis='Z', chamfer=.04,
              taper=(.55, .55))
    st = a.part('Mast_steel', 'Steel')
    st.cyl(.08, 1.2, loc=(0, -2.0, 10.2), seg=8, bevel=0)
    st.box((3.0, .08, .08), loc=(0, -2.6, 9.3), bevel=0)
    for x in (-1.4, 1.4):
        st.box((.04, .04, .5), loc=(x, -2.6, 9.05), bevel=0)
    r = a.pivot('Radar', (0, -1.8, 10.4))
    k.block(a.part('Radar_bar', 'Armor', r), (2.4, .3, .5), loc=(0, 0, .05), chamfer=.04)
    a.part('Radar_face', 'Undercarriage', r).box((2.2, .02, .38), loc=(0, -.16, .3), bevel=0)
    a.part('Radar_pedestal', 'Steel', r).cyl(.15, .3, loc=(0, 0, -.1), seg=10, bevel=0)
    faces = a.part('Aps_faces', 'Glass')
    for (nx, ny) in ((0, -1), (1, 0), (-1, 0), (0, 1)):
        rot = K.rot_to((nx, ny, .3))
        faces.box((.7, .7, .03), loc=(nx * .62, -2.9 + ny * .62, 8.5), rot=rot, bevel=0)
    a.pivot('Mount_APS', (0, -2.9, 9.0))
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, -1.5, 7.6), h=2.0, r=.03, lean=.05)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.9, -1.5, 7.6), h=1.8, r=.03, lean=.05)
    # The funnel with its cap and exhaust pipes, aft of the mast.
    k.extrude(a.part('Funnel', 'Team'), [(-.9, -1.0), (.9, -1.0), (.8, 1.0), (-.8, 1.0)], 1.6, loc=(0, 2.5, 7.2),
              axis='Z', chamfer=.04, taper=(.85, .9))
    a.part('Funnel_cap', 'Undercarriage').box((1.5, 1.6, .1), loc=(0, 2.55, 8.05), bevel=0)
    for x in (-.35, .35):
        a.part('Exhausts', 'Steel').cyl(.15, .5, loc=(x, 2.6, 8.25), seg=8, bevel=0)
    K.soot(a, (0, 2.6, 8.4), radius=1.2, k=.5)
    # Two quad anti-ship canister launchers amidships, each pair of tubes canted.
    for s in (-1, 1):
        lb = a.part('Missile_canisters', 'Armor')
        for i in range(2):
            for j in range(2):
                lb.box((.42, 3.0, .42), loc=(s * (1.0 + i * .46), 1.5, deck_z(1.5) + 2.2 + j * .46), rot=(-.25, 0, 0),
                       bevel=0)
        a.part('Canister_frames', 'Steel').box((1.0, .15, 1.6), loc=(s * 1.23, 2.6, deck_z(2.6) + 2.15), bevel=0)


def _hangar(a):
    """The hangar aft with its roller door, the AK-630 on its roof (`Part_mg` > `Mount_mg`)."""
    k.block(a.part('Hangar', 'Team'), (B * 2 - .6, 5.0, 4.85 - 2.3), loc=(0, 6.7, 2.3), chamfer=.06)
    door = a.part('Hangar_door', 'Armor')
    door.box((3.0, .06, 2.2), loc=(0, 9.22, 3.4), bevel=0)
    slats = a.part('Door_slats', 'Undercarriage')
    for i in range(8):
        slats.box((3.0, .02, .02), loc=(0, 9.26, 2.45 + i * .27), bevel=0)
    a.pivot('Part_mg', (0, 6.5, 4.85))
    m = a.pivot('Mount_mg', (0, 0, 0), 'Part_mg')
    k.lathe(a.part('CIWS_ring_mg', 'Steel', m), [(.7, 0), (.7, .12), (.6, .2), (0, .2)], seg=14)
    k.extrude(a.part('CIWS_body_mg', 'Team', m), [(-.55, 0), (.55, 0), (.45, .7), (.1, .85), (-.1, .85), (-.45, .7)],
              1.3, loc=(0, .2, .15), axis='Y', chamfer=.04, corner=.03)
    k.lathe(a.part('CIWS_armor_mg', 'Armor', m), [(.22, 0), (.22, .3), (.16, .36), (0, .36)], loc=(0, -.45, .62),
            rot=K.FORWARD, seg=10)
    bar = a.part('CIWS_barrels_mg', 'Steel', m)
    for i in range(6):
        u = i * TAU / 6
        bar.cyl(.025, 1.7, loc=(math.cos(u) * .08, -1.65, .62 + math.sin(u) * .08), rot=K.FORWARD, seg=5, bevel=0)
    for y in (-1.0, -2.45):
        a.part('CIWS_bores_mg', 'Undercarriage', m).cyl(.15, .08, loc=(0, y, .62), rot=K.FORWARD, seg=10, bevel=0)
    a.part('CIWS_glass_mg', 'Glass', m).box((.3, .02, .15), loc=(.35, -.66, .55), bevel=0)
    a.pivot('Muzzle_mg', (0, -2.67, .62), m)


def _boats_and_deck(a):
    # The RHIB in its davit on the starboard side abaft the superstructure.
    zx, zy, zz = -2.0, 5.0, 5.0
    dav = a.part('Davits', 'Steel')
    for dy in (-1.4, 1.4):
        dav.tube([(-(B - .9), zy + dy, 4.85), (-(B - .9), zy + dy, 6.0), (zx - .2, zy + dy, 6.0)], .07, seg=6)
    K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (zx - .2, zy, zz), length=3.6, beam=1.4)
    a.part('Kit_cables', 'Undercarriage').tube([(zx - .2, zy - 1.4, 6.0), (zx - .2, zy - 1.2, zz + .6)], .015, seg=3)
    # Railings round the decks, ladders, life-raft canisters on the hangar sides, bollards, fairleads.
    for s in (-1, 1):
        K.railing(a.part('Rails', 'Steel'), [(s * (half_beam(y) - .08), y, deck_z(y)) for y in (-14.0, -12.0, -9.0, -6.2)],
                  h=.9, post=1.1, r=.025)
        K.railing(a.part('Rails', 'Steel'), [(s * (half_beam(y) - .08), y, deck_z(y)) for y in (9.3, 12.0, 14.8)],
                  h=.9, post=1.1, r=.025)
        K.railing(a.part('Rails', 'Steel'), [(s * (B - .35), 4.3, 4.85), (s * (B - .35), 9.0, 4.85)], h=.8, post=1.0,
                  r=.02)
        K.ladder(a.part('Ladders', 'Steel'), (s * 1.5, 9.4, deck_z(9.4)), (s * 1.5, 9.25, 4.85), width=.45)
        for y in (6.0, 7.2, 8.4):
            k.lathe(a.part('Life_rafts', 'Medical'), [(.25, -.45), (.28, -.4), (.28, .4), (.25, .45)],
                    loc=(s * (B - .15), y, 3.7), rot=K.FORWARD, seg=10)
        bol = a.part('Bollards', 'Steel')
        for y in (-13.0, -8.0, 10.5, 14.0):
            for dy in (-.18, .18):
                bol.cyl(.12, .35, loc=(s * (half_beam(y) - .45), y + dy, deck_z(y) + .17), seg=8, bevel=0)
        a.part('Fairleads', 'Steel').box((.2, .5, .2), loc=(s * (half_beam(11.5) - .12), 11.5, deck_z(11.5) + .1),
                                         bevel=0)
    # Deck fittings: vents, lockers and boxes on the decks and the superstructure roofs.
    P.clutter(a, 'Deck_lockers', 'Armor', -2.0, 2.0, 9.8, 14.5, deck_z(12.0), 14, seed=41, size=(.3, 1.0),
              height=(.25, .8))
    P.clutter(a, 'Foredeck_fittings', 'Steel', -1.6, 1.6, -11.0, -7.9, deck_z(-9.5) + .1, 10, seed=42,
              size=(.15, .5), height=(.1, .4), gap=.15)
    P.clutter(a, 'Roof_fittings', 'Steel', -1.8, 1.8, -.4, 3.8, 4.6, 16, seed=43, size=(.2, .8), height=(.15, .6))
    P.clutter(a, 'Roof_fittings', 'Steel', -1.5, 1.5, -1.2, 1.4, 6.4, 8, seed=44, size=(.15, .6), height=(.1, .5))
    P.clutter(a, 'Hangar_fittings', 'Steel', -2.0, 2.0, 7.6, 9.0, 4.85, 8, seed=45, size=(.2, .6), height=(.1, .5))
    for s in (-1, 1):
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.15, .15, .15), loc=(s * (B + .2), -4.6, 5.3),
                                                                          bevel=0)


def sea_corvette(a):
    """The sea corvette: see the module docstring."""
    K.suffixed(a)
    _hull(a)
    _gun(a)
    _superstructure(a)
    _hangar(a)
    _boats_and_deck(a)
    k.clean(a)


BUILDERS = {
    'sea_corvette': (sea_corvette, dict(ao_distance=1.2, grime_height=.5)),
}
