"""Prompt 35 wave 6 (lane B): Nyx, the stealth destroyer, rebuilt from scratch (spec: Tools/blender/specs/nyx.json).

General Kessler's Nyx (variant of leviathan keeping turret_fore, vls, ciws_fore, ciws_aft; BossText: a wave-piercing,
pyramid-topped destroyer, a railgun every 8 s, hidden until it fires; tip: the CIWS stop your missiles, the missile
cells carry its anti-ship missile). A Zumwalt-class destroyer with its features drawn 1.3-1.5 x for the boss read
(the def's modelSize 53 x 8.9 x 11 m, keel 1.6 m under the waterline at z 0): the tumblehome hull with its
reverse-raked wave-piercing bow, the knuckle and the dark band at the waterline, the chines; the faceted pyramid
deckhouse with the flush radar faces (the APS's eyes, `Mount_APS`), the bridge's slit windows, the two exhaust
uplifts on its top and the comms mast; on the foredeck the railgun in its faceted stealth turret with the long
rails, the capacitor bank and the barrel shroud (`Part_gun` > `Mount_gun` > `Muzzle_gun`); the peripheral VLS
banks along both deck edges (`Part_vls`: riveted, one shade off, the weak point the tip names); two CIWS
(`Part_mg` > `Mount_mg` on the deckhouse, `Part_mg.001` > `Mount_mg.001` aft); the hangar and the helicopter deck
aft with its markings and nets, the stern boat bay; fairleads, bollards, the anchor recesses, warning lights,
Kessler's colour bands.

Its own hull: nothing is taken from leviathan, kraken or another ship. Runtime nodes kept: `Part_gun`, `Mount_gun`,
`Muzzle_gun`, `Part_vls`, `Part_mg`, `Mount_mg`, `Muzzle_mg`, `Part_mg.001`, `Mount_mg.001`, `Muzzle_mg.001`; new:
`Mount_APS`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
BOW, STERN = -26.5, 26.4
B = 4.45                         # the waterline half beam
DECK = 3.0


def half_beam(y):
    f = (y - BOW) / (STERN - BOW)
    if f < .35:
        return B * math.sin(min(1.0, f / .35) * R90) ** .8
    return B * (1 - .05 * max(0.0, f - .8) / .2)


def _hull(a):
    hull = a.part('Hull', 'Team')
    rings = []
    ys = [STERN, 24.0, 22.0, 18.0, 14.0, 9.0, 4.0, -1.0, -6.0, -10.0, -14.0, -17.0, -19.0, -21.0, -22.5, -23.8,
          -24.8, -25.7, BOW + .05]
    for y in ys:
        h = max(half_beam(y), .1)
        f = max(0.0, -y / -BOW)
        keel = -1.6 + (1.4 * f ** 3 if y < -16 else 0)
        # Tumblehome: the sides lean in above the waterline (deck narrower than the waterline beam).
        rings.append([(-h * .8, y, DECK), (-h, y, .6), (-h * .96, y, -.3), (-h * .55, y, keel + .2), (0, y, keel),
                      (h * .55, y, keel + .2), (h * .96, y, -.3), (h, y, .6), (h * .8, y, DECK)])
    # The wave-piercing bow: the stem raked backwards (the waterline point ahead of the deck edge).
    rings[-1] = [(p[0] * .04 + math.copysign(.03, p[0]), BOW + (2.2 if p[2] > 2 else (.9 if p[2] > .3 else 0)), p[2])
                 for p in rings[-1]]
    k.sharp_loft(hull, rings, chamfer=.05)
    for s in (-1, 1):
        pts = [(s * (max(half_beam(y), .1) + .015), y) for y in ys[1:-1]]
        idx = tuple(range(len(pts) * 2))
        a.part('Hull_low', 'Undercarriage').mesh([(x, y, .45) for x, y in pts] + [(x * .97, y, -.3) for x, y in reversed(pts)],
                                                  [idx if s < 0 else tuple(reversed(idx))])
        a.part('Boot_top', 'Hazard').mesh([(x * 1.002, y, .6) for x, y in pts] + [(x * 1.002, y, .45) for x, y in reversed(pts)],
                                          [idx if s < 0 else tuple(reversed(idx))])
        a.part('Team_band', 'Team').box((.03, 10.0, .45), loc=(s * (B * .9 + .02), -10.0, 1.9), rot=(0, s * -.2, 0),
                                        bevel=0)
        seams = a.part('Hull_seams', 'Undercarriage')
        for i, y in enumerate(range(-20, 24, 3)):
            seams.box((.03, .05, 1.6 + .2 * (i % 3)), loc=(s * (half_beam(y) * .91 + .01), y, 1.7), rot=(0, s * -.2, 0),
                      bevel=0)
        for y in (-21.5, 21.0):
            a.part('Fairleads', 'Steel').box((.12, .6, .3), loc=(s * (half_beam(y) * .8 + .02), y, DECK - .25),
                                             rot=(0, s * -.2, 0), bevel=0)
        a.part('Anchor_recess', 'Undercarriage').box((.04, .8, .8), loc=(s * (half_beam(-22.0) * .9 + .02), -22.0, 1.8),
                                                     rot=(0, s * -.2, 0), bevel=0)
    deck = a.part('Deck', 'Team')
    for y0, y1 in ((-24.5, -8.5), (11.5, 18.0)):
        for i in range(4):
            ya, yb = y0 + (y1 - y0) * i / 4, y0 + (y1 - y0) * (i + 1) / 4
            ha, hb = half_beam(ya) * .8 - .05, half_beam(yb) * .8 - .05
            deck.mesh([(-ha, ya, DECK + .01), (ha, ya, DECK + .01), (hb, yb, DECK + .01), (-hb, yb, DECK + .01)],
                      [(0, 1, 2, 3)])
    bol = a.part('Bollards', 'Steel')
    for s in (-1, 1):
        for y in (-23.0, -17.0, 13.0, 17.5):
            for dy in (-.25, .25):
                bol.cyl(.15, .35, loc=(s * (half_beam(y) * .8 - .5), y + dy, DECK + .17), seg=8, bevel=0)


def _deckhouse(a):
    """The faceted pyramid deckhouse: sloped walls, flush radar faces, slit windows, the uplifts, the comms mast."""
    dh = a.part('Deckhouse', 'Team')
    rings = []
    for z, y0, y1, h in ((DECK - .05, -8.4, 11.5, 3.5), (6.0, -6.6, 10.0, 2.6), (8.2, -5.0, 7.5, 1.6),
                         (9.0, -4.2, 5.8, 1.1)):
        rings.append([(-h, y0, z), (h, y0, z), (h, y1, z), (-h, y1, z)])
    k.sharp_loft(dh, rings, chamfer=.06)
    faces = a.part('Radar_faces', 'Glass')
    for (nx, ny, x, y) in ((0, -1, 0, -7.2), (1, 0, 2.95, -2.0), (-1, 0, -2.95, -2.0), (0, 1, 0, 10.4)):
        rot = K.rot_to((nx, ny, .7))
        faces.box((1.8, 1.8, .04), loc=(x, y, 6.6), rot=rot, bevel=0)
    a.pivot('Mount_APS', (0, -2.0, 8.6))
    glass = a.part('Bridge_glass', 'Glass')
    for i in range(6):
        x = -1.6 + i * .64
        glass.box((.5, .05, .22), loc=(x, -6.95, 6.25), rot=(.56, 0, 0), bevel=0)
    for x in (-.55, .55):
        k.extrude(a.part('Uplifts', 'Armor'), [(-.45, -1.0), (.45, -1.0), (.45, 1.0), (-.45, 1.0)], .8,
                  loc=(x, 3.0, 9.35), axis='Z', chamfer=.05, taper=(.85, .9))
        a.part('Uplift_grilles', 'Undercarriage').box((.7, 1.7, .03), loc=(x, 3.0, 9.76), bevel=0)
    K.soot(a, (0, 3.0, 9.8), radius=1.6, k=.5)
    m = a.part('Comms_mast', 'Steel')
    m.cyl(.12, .7, loc=(0, 6.2, 9.35), seg=8, bevel=0)
    m.box((2.0, .1, .1), loc=(0, 6.2, 9.55), bevel=0)
    for x in (-.9, .9):
        m.cyl(.05, .3, loc=(x, 6.2, 9.72), seg=6, bevel=0)
    a.part('Warning_lights', 'LavaGlow').box((.12, .12, .12), loc=(0, 6.2, 9.76), bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.03, 6.0, .35), loc=(s * 3.15, 1.0, 4.0), rot=(0, s * -.38, 0), bevel=0)
        P.portholes(a, [(s * 3.28, y, 3.8) for y in (-5.0, -2.0, 1.0, 4.0, 7.0)], (s, 0, .4), r=.18, seg=6)
    # The hangar door at the deckhouse's aft end.
    a.part('Hangar_door', 'Armor').box((4.0, .06, 2.4), loc=(0, 11.52, DECK + 1.3), bevel=0)
    slats = a.part('Door_slats', 'Undercarriage')
    for i in range(8):
        slats.box((4.0, .03, .03), loc=(0, 11.57, DECK + .3 + i * .3), bevel=0)


def _railgun(a):
    """The railgun forward in its faceted stealth turret (`Part_gun` > `Mount_gun` > `Muzzle_gun`)."""
    a.pivot('Part_gun', (0, -13.2, 3.0))
    m = a.pivot('Mount_gun', (0, 0, .2), 'Part_gun')
    k.lathe(a.part('Gun_ring', 'Steel', m), [(2.1, -.2), (2.1, .05), (1.95, .15), (0, .15)], seg=18)
    rings = []
    for z, f, w, r in ((.1, -2.4, 1.6, 2.6), (1.3, -2.0, 1.45, 2.4), (1.75, -1.0, 1.0, 2.0)):
        rings.append([(-w * .45, f, z), (w * .45, f, z), (w, f + 1.0, z), (w, r, z), (-w, r, z), (-w, f + 1.0, z)])
    k.sharp_loft(a.part('Gun_house', 'Team', m), rings, chamfer=.06)
    # The rails in their shroud, the bands, the bore; the capacitor bank behind.
    k.extrude(a.part('Gun_rails', 'Armor', m), [(-.35, -.25), (.35, -.25), (.35, .25), (-.35, .25)], 7.4,
              loc=(0, -5.6, .75), axis='Y', chamfer=.04)
    bands = a.part('Gun_bands', 'Steel', m)
    for y in (-3.0, -4.6, -6.2, -7.8):
        bands.box((.8, .2, .6), loc=(0, y, .75), bevel=0)
    a.part('Gun_bore', 'Undercarriage', m).box((.3, .03, .2), loc=(0, -9.32, .75), bevel=0)
    a.pivot('Muzzle_gun', (0, -9.35, .75), m)
    k.block(a.part('Capacitors', 'Armor', m), (2.2, 1.0, .5), loc=(0, 2.4, 1.0), chamfer=.06)
    cells = a.part('Capacitor_cells', 'TeamGlow', m)
    for x in (-.7, 0, .7):
        cells.box((.4, .04, .25), loc=(x, 2.91, 1.25), bevel=0)
    K.soot(a, (0, -22.55, 3.95), radius=1.0, k=.35)


def _vls(a):
    """The peripheral VLS banks along both deck edges (`Part_vls`): riveted cells, one shade off."""
    p = a.pivot('Part_vls', (0, 3.45, 3.0))
    plates = a.part('Vls_plates', 'Armor', p)
    lids = a.part('Vls_hatches', 'Steel', p)
    rivets = a.part('Kit_rivets', 'Steel', p)
    for y0, y1 in ((-21.5, -16.0), (12.0, 17.0)):
        for s in (-1, 1):
            x = s * (half_beam((y0 + y1) / 2) * .8 - .7)
            k.block(plates, (1.1, y1 - y0, .25), loc=(x, (y0 + y1) / 2 - 3.45, .0), chamfer=.04)
            n = int((y1 - y0) / .9)
            for i in range(n):
                yy = y0 + .45 + i * .9 - 3.45
                lids.box((.8, .7, .04), loc=(x, yy, .26), bevel=0)
                rivets.box((.06, .06, .04), loc=(x + s * .45, yy, .27), bevel=0)
    K.tone(a, 'Part_vls', k=.86)


def _ciws(a, part, mount, muzzle, at, sfx):
    a.pivot(part, at)
    m = a.pivot(mount, (0, 0, .34), part)
    k.lathe(a.part('CIWS_ring' + sfx, 'Steel', m), [(.9, -.34), (.9, .1), (.8, .2), (0, .2)], seg=14)
    k.extrude(a.part('CIWS_body' + sfx, 'Team', m), [(-.65, 0), (.65, 0), (.55, .8), (.1, .95), (-.1, .95), (-.55, .8)],
              1.5, loc=(0, .25, .15), axis='Y', chamfer=.05, corner=.03)
    k.lathe(a.part('CIWS_armor' + sfx, 'Armor', m), [(.26, 0), (.26, .3), (.2, .36), (0, .36)], loc=(0, -.55, .62),
            rot=K.FORWARD, seg=10)
    bar = a.part('CIWS_barrels' + sfx, 'Steel', m)
    for i in range(6):
        u = i * TAU / 6
        bar.cyl(.028, 1.9, loc=(math.cos(u) * .09, -1.85, .62 + math.sin(u) * .09), rot=K.FORWARD, seg=5, bevel=0)
    for y in (-1.1, -2.75):
        a.part('CIWS_bores' + sfx, 'Undercarriage', m).cyl(.16, .08, loc=(0, y, .62), rot=K.FORWARD, seg=10, bevel=0)
    a.part('CIWS_glass' + sfx, 'Glass', m).box((.3, .02, .15), loc=(.4, -.76, .55), bevel=0)
    a.pivot(muzzle, (0, -2.87, .62), m)
    K.tone(a, part, k=.9)


def _aft(a):
    fd = a.part('Flight_deck', 'Team')
    P.plane(fd, -3.3, 3.3, 18.2, 25.5, DECK + .02)
    marks = a.part('Deck_marks', 'Medical')
    k.ring(marks, [(2.0, DECK + .03), (2.2, DECK + .03), (2.2, DECK + .04), (2.0, DECK + .04)], loc=(0, 22.0, 0), seg=20)
    marks.box((.2, 7.0, .01), loc=(0, 21.8, DECK + .04), bevel=0)
    a.part('Deck_lines', 'Hazard').box((6.4, .25, .01), loc=(0, 18.4, DECK + .04), bevel=0)
    nets = a.part('Deck_nets', 'Steel')
    for s in (-1, 1):
        for i in range(7):
            nets.box((.6, .9, .02), loc=(s * 3.55, 18.8 + i * .98, DECK - .1), rot=(0, s * -.25, 0), bevel=0)
        for i in range(4):
            a.part('Deck_lights', 'Lamp').box((.2, .2, .08), loc=(s * 3.1, 19.0 + i * 2.0, DECK + .05), bevel=0)
    # The stern boat bay door in the transom, the boat inside.
    a.part('Boat_bay', 'Undercarriage').box((3.0, .06, 1.4), loc=(0, STERN + .02, 1.6), bevel=0)
    P.clutter(a, 'Deck_fittings', 'Steel', -2.6, 2.6, -24.0, -16.5, DECK, 12, seed=71, size=(.3, 1.0), height=(.2, .6),
              gap=.4)
    P.clutter(a, 'Deck_fittings', 'Steel', -2.8, 2.8, 12.0, 17.5, DECK, 8, seed=72, size=(.3, 1.0), height=(.2, .6),
              gap=.4)
    P.clutter(a, 'Roof_fittings', 'Steel', -1.4, 1.4, -3.8, 1.5, 9.0, 8, seed=73, size=(.3, .9), height=(.2, .6),
              gap=.3)


def _panels(a):
    """Flush radar-absorbent panels on the deckhouse faces (each its own plate, a shade off), the panel seams,
    access hatches along its foot, the CIWS sponson under the forward mount, the boat in the stern bay."""
    pan = a.part('Deckhouse_panels', 'Armor')
    seams = a.part('Deckhouse_seams', 'Undercarriage')
    for s in (-1, 1):
        for i, y in enumerate((-5.6, -3.2, -.8, 1.6, 4.0, 6.4, 8.8)):
            w = 2.0 + .1 * (i % 3)
            pan.box((.05, w, 1.6), loc=(s * 3.0, y, 4.6), rot=(0, s * -.4, 0), bevel=0)
            seams.box((.04, .04, 2.6), loc=(s * 3.05, y + w / 2 + .1, 4.6), rot=(0, s * -.4, 0), bevel=0)
        for i, y in enumerate((-4.0, -1.0, 2.0, 5.0)):
            pan.box((.05, 2.2 + .1 * i, 1.0), loc=(s * 1.95, y, 7.1), rot=(0, s * -.6, 0), bevel=0)
        for y in (-6.5, -2.5, 1.5, 5.5, 9.5):
            K.plate(a.part('Deckhouse_hatches', 'Armor'), (.04, 1.0, 1.4), loc=(s * 3.42, y, DECK + .85),
                    rot=(0, s * -.42, 0))
    k.block(a.part('Sponsons', 'Armor'), (2.0, 2.2, .3), loc=(-2.09, -4.9, 5.8), chamfer=.04)
    a.part('Sponsons', 'Armor').limb((-2.09, -4.9, 5.8), (-2.4, -4.9, 4.4), .4, .4, bevel=0)
    K.rhib(a.part('Boats', 'Armor'), a.part('Boat_tubes', 'Rubber'), (0, 24.5, .9), length=3.6, beam=1.5)
    a.part('Kit_cables', 'Undercarriage').tube([(-.9, 25.8, 2.4), (-.6, 24.2, 1.6)], .03, seg=3)
    P.clutter(a, 'Deck_fittings', 'Steel', -2.0, 2.0, -12.0, -9.0, DECK, 6, seed=74, size=(.3, .8), height=(.2, .5),
              gap=.4)


def _paint(a):
    """Deck seam lines and non-skid walkways in segments, flush hull panels along the sides (each its own plate)."""
    seams = a.part('Deck_seams', 'Undercarriage')
    walk = a.part('Walkways', 'Undercarriage')
    for y in range(-24, -8, 2):
        h = half_beam(y) * .8 - .2
        P.plane(seams, -h, h, y - .05, y + .05, DECK + .02)
    for s in (-1, 1):
        for y0 in (-23.5, -20.0, -16.5, -13.0, 12.0, 15.0):
            x = s * (half_beam(y0 + 1.5) * .8 - 1.4)
            P.plane(walk, x - .4, x + .4, y0, y0 + 3.0, DECK + .025)
        hp = a.part('Hull_panels', 'Armor')
        for i, y in enumerate(range(-18, 22, 4)):
            L = 2.6 + .2 * (i % 3)
            hp.box((.04, L, 1.0), loc=(s * (half_beam(y) * .93 + .03), y, 1.5), rot=(0, s * -.2, 0), bevel=0)


def nyx(a):
    """Nyx: see the module docstring."""
    K.suffixed(a)
    _hull(a)
    _deckhouse(a)
    _railgun(a)
    _vls(a)
    _ciws(a, 'Part_mg', 'Mount_mg', 'Muzzle_mg', (-2.09, -4.9, 6.1), '_mg')
    _ciws(a, K.name('Part_mg', 1), K.name('Mount_mg', 1), K.name('Muzzle_mg', 1), (1.29, 12.9, 3.0), '_mg_001')
    _aft(a)
    _panels(a)
    _paint(a)
    k.clean(a)


BUILDERS = {
    'nyx': (nyx, dict(ao_distance=1.6, grime_height=.5)),
}
