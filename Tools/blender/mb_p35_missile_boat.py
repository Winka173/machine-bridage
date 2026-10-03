"""Prompt 35 wave 6 (lane B): the missile boat rebuilt from scratch (spec: Tools/blender/specs/missile_boat.json).

A 14 m planing fast attack craft with an S-8 rocket launcher (unit_refs: a 14 m planing-hull attack boat, S-8
80 mm; the data's 14 x 3.8 m): the deep-vee planing hull with its flared, raked bow and hard chines, the spray
rails, the dark bottom and boot-top band, the rubbing strake and the transom with its two stern drives; the low
wheelhouse with raked windows and a roof hatch, the short radar mast with the scanner, whips and lights; on the
wheelhouse roof the heavy machine gun behind its shield (`Mount_mg`); aft on a trainable launcher (`Mount_rocket`)
two S-8 pods with their tube faces; a pintle minigun on the bridge wing (the close-in Gatling patrol boats carry),
two life-raft canisters (the boat role), railings, bollards, cleats, fenders, the exhaust outlets, deck lockers,
the ammunition boxes and Team bands.

Its own hull: nothing is taken from landing_craft or another craft. Runtime nodes kept: `Mount_mg`, `Muzzle_mg`,
`Mount_rocket`, `Muzzle_rocket`; old part names `Hull`, `Deck`, `Cabin`, `Cabin_glass`, `Mast`, `Rocket_pods`,
`Pod_tubes`, `Mg_body`, `Mg_barrel`, `Stripe`. The runtime sinks ships whole (ShipSinking). Metres, +Z up, -Y front,
+X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
BOW, STERN = -7.0, 6.9
DECK = 1.25


def _hull(a):
    hull = a.part('Hull', 'Armor')
    rings = []
    # Stations stern to bow: a deep vee, hard chines, the topsides flaring out forward, the sheer rising to the bow.
    for y, hw, chine, keel, top in ((STERN, 1.78, 1.6, -.55, DECK), (5.0, 1.84, 1.65, -.6, DECK),
                                    (3.0, 1.88, 1.68, -.62, DECK), (1.0, 1.9, 1.67, -.65, DECK),
                                    (-1.0, 1.9, 1.62, -.68, DECK + .02), (-2.6, 1.85, 1.5, -.66, DECK + .06),
                                    (-4.0, 1.75, 1.3, -.6, DECK + .12), (-5.0, 1.55, 1.05, -.5, DECK + .18),
                                    (-5.8, 1.25, .75, -.35, DECK + .25), (-6.5, .8, .4, -.05, DECK + .3),
                                    (BOW + .1, .2, .1, .3, DECK + .35)):
        rings.append([(-hw, y, top), (-hw * .97, y, top - .45), (-chine, y, .15), (-chine * .5, y, keel * .55),
                      (0, y, keel), (chine * .5, y, keel * .55), (chine, y, .15), (hw * .97, y, top - .45),
                      (hw, y, top)])
    k.sharp_loft(hull, rings, chamfer=.03)
    low = a.part('Hull_low', 'Undercarriage')
    for s in (-1, 1):
        low.mesh([(s * 1.6, 6.8, .14), (s * 1.6, -3.5, .14), (s * 1.0, -5.5, .14), (s * 1.0, -5.5, -.1),
                  (s * 1.6, -3.5, -.1), (s * 1.6, 6.8, -.1)], [(0, 1, 2, 3, 4, 5) if s > 0 else (5, 4, 3, 2, 1, 0)])
        a.part('Stripe', 'Hazard').box((.02, 9.0, .1), loc=(s * 1.75, 1.8, .6), rot=(0, s * -.12, 0), bevel=0)
        # Spray rails along the bottom, the rubbing strake, fenders on lines.
        for dz, f in ((-.2, .55), (-.4, .3)):
            a.part('Spray_rails', 'Armor').box((.06, 9.5, .05), loc=(s * f * 1.6, 1.0, dz), bevel=0)
        a.part('Strakes', 'Rubber').box((.08, 11.0, .1), loc=(s * 1.9, .5, DECK - .1), bevel=0)
        for y in (-2.5, 1.0, 4.0):
            a.part('Fenders', 'Rubber').cyl(.1, .55, loc=(s * 1.93, y, .85), seg=10, bevel=0)
            a.part('Fender_lines', 'Canvas').box((.015, .015, .3), loc=(s * 1.93, y, 1.25), bevel=0)
        a.part('Team_band', 'Team').box((.012, 4.0, .22), loc=(s * 1.89, -.8, 1.0), bevel=0)
    P.plane(a.part('Deck', 'Team'), -1.75, 1.75, -4.0, STERN - .05, DECK + .01)
    # The transom: two stern drives, the exhaust outlets, the boarding step.
    for x in (-.8, .8):
        a.part('Stern_drives', 'Undercarriage').box((.25, .5, .7), loc=(x, STERN + .2, .0), bevel=0)
        k.lathe(a.part('Props', 'Steel'), [(.2, 0), (.2, .05), (0, .08)], loc=(x, STERN + .48, -.2), rot=K.BACKWARD,
                seg=8)
        a.part('Exhaust_outlets', 'Undercarriage').cyl(.09, .1, loc=(x, STERN + .02, .55), rot=K.BACKWARD, seg=8,
                                                        bevel=0)
    a.part('Boarding_step', 'Steel').box((2.4, .35, .06), loc=(0, STERN + .15, .35), bevel=0)
    K.soot(a, (0, STERN + .1, .55), radius=.8, k=.4)


def _cabin(a):
    cab = a.part('Cabin', 'Team')
    rings = []
    for z, y0, y1, h in ((DECK, -3.3, .4, 1.45), (2.1, -2.6, .3, 1.3), (2.25, -2.3, .2, 1.18)):
        rings.append([(-h, y0, z), (h, y0, z), (h, y1, z), (-h, y1, z)])
    k.sharp_loft(cab, rings, chamfer=.04)
    glass = a.part('Cabin_glass', 'Glass')
    for i in range(4):
        x = -1.0 + i * .66
        c = [(x + .3, -3.15, 1.62), (x - .3, -3.15, 1.62), (x - .27, -2.68, 2.04), (x + .27, -2.68, 2.04)]
        glass.mesh([(p[0], p[1] - .012, p[2]) for p in c], [(0, 1, 2, 3)])
    for s in (-1, 1):
        for y in (-1.8, -.9):
            glass.box((.012, .7, .32), loc=(s * 1.39, y, 1.85), rot=(0, s * .14, 0), bevel=0)
        a.part('Door_panels', 'Undercarriage').box((.012, .55, .9), loc=(s * 1.43, -.1, 1.7), bevel=0)
    K.hatch_round(a, (.5, -.6, 2.25), r=.25, periscopes=0, seg=10)
    # The radar mast, scanner, whips, lights; roof fittings.
    mast = a.part('Mast', 'Steel')
    mast.tube([(-.3, -.2, 2.25), (0, -.25, 3.4)], .04, seg=6)
    mast.tube([(.3, -.2, 2.25), (0, -.25, 3.4)], .04, seg=6)
    mast.box((.9, .06, .06), loc=(0, -.25, 3.2), bevel=0)
    k.block(a.part('Radar_scanner', 'Armor'), (1.0, .14, .1), loc=(0, -.25, 3.45), chamfer=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.45, -.25, 3.2), h=.5, r=.012)
    K.whip_antenna(a.part('Antennas', 'Steel'), (.45, -.25, 3.2), h=.45, r=.012)
    a.part('Nav_lights', 'LavaGlow').box((.08, .08, .08), loc=(-1.3, -2.5, 2.2), bevel=0)
    a.part('Nav_lights', 'SignalGreen').box((.08, .08, .08), loc=(1.3, -2.5, 2.2), bevel=0)
    P.clutter(a, 'Roof_fittings', 'Steel', -1.0, 1.0, -.15, .15, 2.25, 6, seed=31, size=(.08, .25), height=(.05, .2))
    K.railing(a.part('Railings', 'Steel'), [(-1.1, .15, 2.25), (-1.1, -2.2, 2.25), (1.1, -2.2, 2.25), (1.1, .15, 2.25)],
              h=.45, post=.6, r=.015)


def _weapons(a):
    # The heavy MG on the wheelhouse roof behind its shield (`Mount_mg`).
    k.lathe(a.part('Gun_ring', 'Armor'), [(.36, 0), (.36, .12), (.3, .18), (0, .18)], loc=(0, -.8, 2.25), seg=12)
    m = a.pivot('Mount_mg', (0, -.8, 2.45))
    k.block(a.part('Mg_body', 'Undercarriage', m), (.14, .5, .16), loc=(0, -.05, .1), chamfer=.01)
    k.lathe(a.part('Mg_barrel', 'Steel', m), [(.03, 0), (.03, .3), (.02, .35), (.018, 1.1), (0, 1.1)],
            loc=(0, -.35, .22), rot=K.FORWARD, seg=6)
    k.extrude(a.part('Gun_shield', 'Armor', m), [(-.38, -.15), (.38, -.15), (.33, .28), (-.33, .28)], .025,
              loc=(0, -.3, .18), rot=(R90 - .1, 0, 0), axis='Z', chamfer=.006)
    a.part('Ammo_can', 'Crate', m).box((.1, .25, .16), loc=(.14, -.05, .05), bevel=0)
    a.pivot('Muzzle_mg', (0, -1.45, .22), m)
    # The trainable launcher aft with two S-8 pods (`Mount_rocket`).
    k.lathe(a.part('Launcher_base', 'Armor'), [(.55, 0), (.55, .12), (.45, .2), (0, .2)], loc=(0, 2.6, DECK), seg=14)
    r = a.pivot('Mount_rocket', (0, 2.6, 1.3))
    cr = a.part('Launcher_cradle', 'Armor', r)
    k.block(cr, (.5, .6, .45), loc=(0, .1, .1), chamfer=.04)
    for s in (-1, 1):
        cr.limb((s * .2, .1, .4), (s * .42, -.1, .75), .08, .1, bevel=0)
    tilt = (R90 + .3, 0, 0)
    for s in (-1, 1):
        x = s * .48
        k.lathe(a.part('Rocket_pods', 'Team', r), [(.24, -.85), (.26, -.8), (.26, -.3), (.27, -.27), (.27, -.2),
                                                   (.26, -.17), (.26, .4), (.27, .43), (.27, .5), (.26, .53),
                                                   (.26, .75), (.2, .85), (0, .86)],
                loc=(x, -.3, .8), rot=tilt, seg=16, worn=(1, 4, 8))
        face = a.part('Pod_face', 'Undercarriage', r)
        faces = a.part('Pod_tubes', 'Undercarriage', r)
        cx, cy, cz = x, -.3 - math.cos(.3) * .86, .8 - math.sin(.3) * .86
        face.cyl(.24, .02, loc=(cx, cy, cz), rot=tilt, seg=12, bevel=0)
        for i in range(7):
            u = i * TAU / 6
            rr = 0 if i == 6 else .13
            faces.cyl(.035, .03, loc=(cx + math.cos(u) * rr, cy - .01, cz + math.sin(u) * rr * .95), rot=tilt, seg=6,
                      bevel=0)
    a.pivot('Muzzle_rocket', (0, -1.3, .8), r)
    # The pintle minigun on the port bridge wing (the close-in Gatling), its ammunition box.
    g = a.part('Gatling', 'Steel')
    g.cyl(.035, .6, loc=(1.62, -2.0, DECK + .3), seg=6, bevel=0)
    for i in range(6):
        u = i * TAU / 6
        g.cyl(.01, .55, loc=(1.62 + math.cos(u) * .03, -2.45, DECK + .66 + math.sin(u) * .03), rot=K.FORWARD, seg=4,
              bevel=0)
    k.block(g, (.12, .26, .12), loc=(1.62, -2.0, DECK + .6), chamfer=.01)
    a.part('Ammo_boxes', 'Crate').box((.2, .3, .25), loc=(1.62, -1.6, DECK), bevel=0)


def _deck(a):
    # Reload pods on their rack amidships (two spare S-8 pods), the searchlight and horn on the cabin roof.
    rack = a.part('Reload_rack', 'Steel')
    for x in (-1.0, -.4):
        k.lathe(a.part('Reload_pods', 'Team'), [(.22, -.75), (.24, -.7), (.24, .65), (.18, .75), (0, .76)],
                loc=(x, 1.0, DECK + .32), rot=K.FORWARD, seg=14, worn=(1, 2))
        for y in (.5, 1.5):
            rack.box((.5, .06, .2), loc=(x, y, DECK + .1), bevel=0)
    k.lathe(a.part('Searchlight', 'Armor'), [(.12, 0), (.14, .05), (.14, .2), (0, .2)], loc=(-.6, -1.9, 2.4),
            rot=K.FORWARD, seg=12)
    a.part('Lamps', 'Lamp').cyl(.12, .01, loc=(-.6, -2.11, 2.4), rot=K.FORWARD, seg=12, bevel=0)
    a.part('Searchlight', 'Armor').cyl(.04, .15, loc=(-.6, -1.85, 2.3), seg=6, bevel=0)
    k.lathe(a.part('Horn', 'Steel'), [(.03, 0), (.05, .1), (.1, .25), (0, .25)], loc=(.7, -1.9, 2.35), rot=K.FORWARD,
            seg=8, caps=(True, False))
    P.portholes(a, [(s * 1.42, y, 1.55) for s in (-1, 1) for y in (-2.9, -.5)], (1, 0, 0), r=.09)
    K.railing(a.part('Railings', 'Steel'), [(-1.7, 6.6, DECK), (-1.75, 3.0, DECK), (-1.6, -3.6, DECK + .1),
                                            (0, -6.5, DECK + .32), (1.6, -3.6, DECK + .1), (1.75, 3.0, DECK),
                                            (1.7, 6.6, DECK)], h=.7, post=.9, r=.018)
    bol = a.part('Bollards', 'Steel')
    for s in (-1, 1):
        for y in (-5.0, 6.3):
            for dy in (-.12, .12):
                bol.cyl(.06, .2, loc=(s * 1.3 * (.6 if y < 0 else 1), y + dy, DECK + (.22 if y < 0 else .1)), seg=8,
                        bevel=0)
        a.part('Cleats', 'Steel').box((.06, .25, .05), loc=(s * 1.5, 1.2, DECK + .03), bevel=0)
    # Two life-raft canisters on their cradle, deck lockers and ammunition boxes, fuel fillers.
    for x in (-1.0, -.4):
        k.lathe(a.part('Lifeboat_canisters', 'Medical'), [(.2, -.35), (.22, -.32), (.22, .32), (.2, .35)],
                loc=(x, 5.6, DECK + .25), rot=K.FORWARD, seg=10)
        a.part('Kit_straps', 'Undercarriage').box((.46, .04, .46), loc=(x, 5.6, DECK + .25), bevel=0)
    a.part('Boat_cradle', 'Steel').box((1.0, .9, .05), loc=(-.7, 5.6, DECK + .02), bevel=0)
    P.clutter(a, 'Deck_lockers', 'Armor', .2, 1.6, 4.4, 6.6, DECK, 10, seed=33, size=(.2, .55), height=(.2, .5))
    P.clutter(a, 'Ammo_boxes', 'Crate', -1.6, -.2, 2.0, 3.9, DECK, 8, seed=34, size=(.2, .45), height=(.15, .35))
    P.clutter(a, 'Deck_fittings', 'Steel', -1.2, 1.2, -5.8, -3.6, DECK + .15, 12, seed=35, size=(.08, .3),
              height=(.05, .2))
    k.lathe(a.part('Anchor_winch', 'Steel'), [(.15, -.2), (.15, -.15), (.1, -.1), (.1, .1), (.15, .15), (.15, .2)],
            loc=(0, -5.4, DECK + .4), rot=(0, R90, 0), seg=10)


def missile_boat(a):
    """The missile boat: see the module docstring."""
    _hull(a)
    _cabin(a)
    _weapons(a)
    _deck(a)
    k.clean(a)


BUILDERS = {
    'missile_boat': (missile_boat, dict(ao_distance=.7, grime_height=.5)),
}
