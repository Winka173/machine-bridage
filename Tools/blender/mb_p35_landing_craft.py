"""Prompt 35 wave 6 (lane B): the landing craft rebuilt from scratch (spec: Tools/blender/specs/landing_craft.json).

An LCM-8 / LCU-class mechanised landing craft (unit_refs: LCM, a bow-ramp craft carrying two tanks; the data's
17 x 7 m): the box barge hull with its spoon bow and flared shoulders, the dark bottom under the waterline and the
boot-top band, rubbing strakes and the old-tyre fenders hung along both sides; the bow ramp raised and locked, its
ribs, the hinge knuckles and the ramp winch wires to the A-frame; the open well deck with tie-down rings and the
tread plates, the high wing walls with their walkways, railings and ladders; aft the engine casing and the
two-tier wheelhouse with its window band, doors, portholes, the flying-bridge rail, the short mast with its radar
and whips; on the wheelhouse roof the heavy machine gun (`Mount_mg`), on the wing a pintle M134 in its gun tub
(the close-in Gatling an LCAC carries), the Zodiac inflatable on its cradle aft (the boat), the stern anchor winch
and its kedge anchor, bollards, cleats, life rings, exhaust stacks, vents, deck lights and Team bands.

Its own hull: nothing is taken from missile_boat or another craft. Runtime nodes kept: `Mount_mg`, `Muzzle_mg`; old
part names `Hull`, `Ramp`, `Ramp_edges`, `Well`, `Wing_walls`, `Wheelhouse`, `Wheelhouse_glass`, `Bollards`; new for
the ship roles: `Mast`, `Gun_tub`, `Gatling`, `Boats`, `Deck`. The hull's split (`Part_*` for a later break rule):
the runtime sinks ships whole (ShipSinking), so no node is added. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
HALF = 3.3
BOW, STERN = -7.7, 8.5
WELL_Z = .45
GUNWALE = 1.85
AFT_DECK = 1.85
WH_Y0, WH_Y1 = 4.6, 7.9


def _hull(a):
    hull = a.part('Hull', 'Armor')
    rings = []
    # Stations stern to bow: a flat bottom, the chine, vertical sides flaring a little at the shoulders.
    for y, keel, half_b, half_t in ((STERN, -.55, HALF - .45, HALF - .05), (6.0, -.8, HALF - .35, HALF),
                                    (-4.0, -.8, HALF - .35, HALF), (-6.6, -.5, HALF - .7, HALF),
                                    (BOW + .2, .05, HALF - 1.1, HALF - .1)):
        rings.append([(-half_t, y, GUNWALE), (-half_t + .05, y, .3), (-half_b, y, keel + .15), (-half_b + .3, y, keel),
                      (half_b - .3, y, keel), (half_b, y, keel + .15), (half_t - .05, y, .3), (half_t, y, GUNWALE)])
    k.sharp_loft(hull, rings, chamfer=.05)
    # The bottom under the waterline (antifouling) and the boot-top band.
    low = a.part('Hull_low', 'Undercarriage')
    for s in (-1, 1):
        low.box((.02, STERN - BOW - 1.4, .5), loc=(s * (HALF + .002), .6, .05), bevel=0)
        a.part('Boot_top', 'Hazard').box((.02, STERN - BOW - 1.4, .1), loc=(s * (HALF + .004), .6, .34), bevel=0)
        # Rubbing strakes and the tyre fenders on their chains.
        a.part('Strakes', 'Steel').box((.1, STERN - BOW - .9, .12), loc=(s * (HALF + .04), .3, 1.15), bevel=0)
        a.part('Strakes', 'Steel').box((.08, STERN - BOW - .9, .1), loc=(s * (HALF + .03), .3, GUNWALE - .05),
                                       bevel=0)
        for i in range(7):
            y = -5.5 + i * 2.0
            k.lathe(a.part('Fender_tyres', 'Rubber'), [(.12, -.1), (.2, -.08), (.22, 0), (.2, .08), (.12, .1)],
                    loc=(s * (HALF + .17), y, .85), rot=(0, R90, 0), seg=10, caps=(False, False))
            a.part('Fender_chains', 'Steel').box((.02, .02, .55), loc=(s * (HALF + .12), y, 1.3), bevel=0)
        a.part('Team_band', 'Team').box((.012, 9.0, .25), loc=(s * (HALF + .006), -.5, 1.55), bevel=0)
    # The weld seams of the side plating (vertical), small studs along the sheer line.
    seam = a.part('Hull_seams', 'Undercarriage')
    studs = a.part('Kit_studs', 'Steel')
    for s in (-1, 1):
        for i in range(12):
            y = -6.2 + i * 1.2
            seam.box((.012, .015, 1.25), loc=(s * (HALF + .006), y, .95), bevel=0)
            for dz in (.55, 1.65):
                studs.box((.04, .05 + .05 * (i % 3), .05 + .05 * ((i + 1) % 2)), loc=(s * (HALF + .02), y + .6, dz),
                          bevel=0)


def _well(a):
    P.plane(a.part('Well', 'Undercarriage'), -HALF + .55, HALF - .55, BOW + .3, WH_Y0 - .1, WELL_Z)
    plates = a.part('Tread_plates', 'Steel')
    rings = a.part('Tie_downs', 'Steel')
    for i in range(6):
        for j in range(3):
            w, d = 1.35 + .05 * ((i + j) % 4), 1.15 + .05 * ((i * 3 + j) % 5)
            x, y = -1.7 + j * 1.7, -5.6 + i * 1.75
            P.plane(plates, x - w / 2, x + w / 2, y - d / 2, y + d / 2, WELL_Z + .01)
    for i in range(9):
        for x in (-2.55, -.85, .85, 2.55):
            rings.box((.12 + .05 * (i % 3), .12, .04 + .05 * (i % 2)), loc=(x, -6.2 + i * 1.3, WELL_Z + .03), bevel=0)
    # Lashing gear stowed along the well's sides: chain boxes, binders, shackle bins (varied fittings).
    for s in (-1, 1):
        P.clutter(a, 'Lashing_gear', 'Crate', s * (HALF - .95) - .3, s * (HALF - .95) + .3, -6.8, 3.8, WELL_Z, 20,
                  seed=3 + s, size=(.15, .55), height=(.1, .45))
    # The wing walls: thick sides with a walkway on top, railings, ladders down into the well.
    ww = a.part('Wing_walls', 'Team')
    for s in (-1, 1):
        k.block(ww, (.55, WH_Y0 - BOW - .4, GUNWALE + .2 - WELL_Z), loc=(s * (HALF - .275), (BOW + WH_Y0) / 2 + .1,
                                                                          WELL_Z), chamfer=.04)
        P.plane(a.part('Deck', 'Armor'), s * (HALF - .28) - .25, s * (HALF - .28) + .25, BOW + .65, WH_Y0 - .15,
                GUNWALE + .22)
        P.clutter(a, 'Walkway_fittings', 'Steel', s * (HALF - .28) - .2, s * (HALF - .28) + .2, -6.5, 3.6,
                  GUNWALE + .2, 16, seed=11 + s, size=(.1, .35), height=(.06, .3))
        K.railing(a.part('Railings', 'Steel'), [(s * (HALF - .05), BOW + .8, GUNWALE + .22),
                                                (s * (HALF - .05), WH_Y0, GUNWALE + .22)], h=.75, post=1.0, r=.02)
        for y in (-4.5, 1.0):
            K.ladder(a.part('Ladders', 'Steel'), (s * (HALF - .6), y, WELL_Z), (s * (HALF - .6), y, GUNWALE + .2),
                     width=.4, step=.28)
        for y in (-6.5, -2.0, 2.5):
            a.part('Deck_lights', 'Lamp').box((.12, .08, .06), loc=(s * (HALF - .58), y, GUNWALE + .05), bevel=0)


def _ramp(a):
    """The bow ramp raised and locked: the plate leaning forward, ribs, edges, hinges, the winch wires."""
    rp = a.part('Ramp', 'Team')
    y0, z0 = BOW + .1, WELL_Z
    lean = .18
    k.block(rp, (HALF * 2 - .9, .2, 2.0), loc=(0, y0 - math.sin(lean) * 1.0, z0), rot=(-lean, 0, 0), chamfer=.04)
    ribs = a.part('Ramp_ribs', 'Armor')
    for i in range(7):
        x = -2.4 + i * .8
        ribs.box((.08, .12, 1.9), loc=(x, y0 + .14 - math.sin(lean) * 1.0, z0 + .98), rot=(-lean, 0, 0), bevel=0)
    for z in (.6, 1.3):
        ribs.box((HALF * 2 - 1.0, .12, .08), loc=(0, y0 + .14 - math.sin(lean) * z, z0 + z), rot=(-lean, 0, 0),
                 bevel=0)
    edge = a.part('Ramp_edges', 'Steel')
    edge.box((HALF * 2 - .85, .26, .1), loc=(0, y0 - math.sin(lean) * 2.0, z0 + 1.98), rot=(-lean, 0, 0), bevel=0)
    for x in (-2.6, -1.3, 0, 1.3, 2.6):
        edge.cyl(.1, .5, loc=(x, y0 + .05, z0 + .05), rot=(0, R90, 0), seg=8, bevel=0)
    # The A-frame on the wing walls' bow ends with the ramp winch wires.
    af = a.part('Ramp_frame', 'Steel')
    for s in (-1, 1):
        af.tube([(s * (HALF - .3), BOW + .6, GUNWALE + .2), (s * (HALF - .3), BOW + .3, GUNWALE + 1.0)], .06, seg=6)
        a.part('Kit_cables', 'Undercarriage').tube([(s * (HALF - .3), BOW + .3, GUNWALE + 1.0),
                                                    (s * 2.6, y0 - .3, z0 + 1.95)], .015, seg=3)
    af.tube([(-(HALF - .3), BOW + .3, GUNWALE + 1.0), ((HALF - .3), BOW + .3, GUNWALE + 1.0)], .05, seg=6)


def _aft(a):
    """The aft deck, the engine casing and the two-tier wheelhouse, the mast with its radar."""
    P.plane(a.part('Deck', 'Armor'), -HALF + .05, HALF - .05, WH_Y0, STERN, AFT_DECK + .01)
    P.clutter(a, 'Deck_lockers', 'Armor', -HALF + .25, -1.9, 4.7, 6.3, AFT_DECK, 6, seed=21, size=(.2, .6), height=(.2, .6))
    P.clutter(a, 'Roof_fittings', 'Steel', -1.6, 1.4, 5.8, 7.5, 3.42, 10, seed=23, size=(.1, .4), height=(.08, .3))
    P.clutter(a, 'Casing_fittings', 'Steel', -1.9, 1.9, 4.7, 7.8, AFT_DECK + 1.0, 12, seed=25, size=(.1, .45), height=(.08, .4))
    wh = a.part('Wheelhouse', 'Team')
    k.block(wh, (HALF * 2 - 1.4, WH_Y1 - WH_Y0, 1.0), loc=(0, (WH_Y0 + WH_Y1) / 2, AFT_DECK), chamfer=.05)
    rings = []
    for z, y0, h in ((AFT_DECK + 1.0, 5.3, 1.7), (3.35, 5.6, 1.5), (3.42, 5.7, 1.45)):
        rings.append([(-h, y0, z), (h, y0, z), (h, 7.6, z), (-h, 7.6, z)])
    k.sharp_loft(a.part('Wheelhouse_top', 'Team'), rings, chamfer=.04)
    glass = a.part('Wheelhouse_glass', 'Glass')
    # The window band: four raked panes, side windows, portholes on the casing, doors.
    for i in range(4):
        x = -1.2 + i * .8
        c = [(x + .36, 5.31, 2.95), (x - .36, 5.31, 2.95), (x - .34, 5.58, 3.3), (x + .34, 5.58, 3.3)]
        glass.mesh([(p[0], p[1] - .012, p[2]) for p in c], [(0, 1, 2, 3)])
    port = a.part('Portholes', 'Glass')
    rim = a.part('Porthole_rims', 'Steel')
    for s in (-1, 1):
        glass.box((.012, .6, .32), loc=(s * 1.61, 6.6, 3.05), rot=(0, s * .12, 0), bevel=0)
        for y in (5.1, 6.0, 6.9, 7.6):
            rim.cyl(.13, .03, loc=(s * (HALF - .69), y, AFT_DECK + .55), rot=(0, R90, 0), seg=8, bevel=0)
            port.cyl(.1, .02, loc=(s * (HALF - .685), y, AFT_DECK + .55), rot=(0, R90, 0), seg=8, bevel=0)
        a.part('Door_panels', 'Undercarriage').box((.012, .7, 1.4), loc=(s * (HALF - .7), 4.95, AFT_DECK + .7),
                                                   bevel=0)
        K.ladder(a.part('Ladders', 'Steel'), (s * 1.95, 7.7, AFT_DECK), (s * 1.75, 7.7, AFT_DECK + 1.0), width=.35)
    # The flying-bridge rail on the casing roof, the short mast, its radar and whips.
    K.railing(a.part('Railings', 'Steel'), [(-2.0, 7.85, AFT_DECK + 1.0), (-2.0, 4.65, AFT_DECK + 1.0),
                                            (2.0, 4.65, AFT_DECK + 1.0), (2.0, 7.85, AFT_DECK + 1.0)], h=.6, post=.8,
              r=.018)
    mast = a.part('Mast', 'Steel')
    mast.cyl(.07, .45, loc=(.6, 7.1, 3.62), seg=8, bevel=0)
    mast.box((1.2, .06, .06), loc=(.6, 7.1, 3.7), bevel=0)
    k.block(a.part('Radar_scanner', 'Armor'), (.9, .12, .1), loc=(.6, 7.1, 3.85), chamfer=.02)
    for x in (.1, 1.1):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, 7.1, 3.72), h=.25, r=.012)
    for x in (-1.1, 1.1):
        a.part('Nav_lights', 'LavaGlow' if x > 0 else 'SignalGreen').box((.1, .1, .1), loc=(x, 5.5, 3.5), bevel=0)
    # Exhaust stacks either side of the casing, vents.
    for s in (-1, 1):
        K.smokestack(a, (s * 2.05, 7.5, AFT_DECK + 1.0), r=.12, h=.7)
        k.lathe(a.part('Vents', 'Steel'), [(.12, 0), (.12, .35), (.18, .4), (.18, .5), (0, .5)],
                loc=(s * 2.9, 5.0, AFT_DECK), seg=8)


def _weapons(a):
    """The heavy MG on the wheelhouse roof (`Mount_mg`), the Gatling in its wing tub, the Zodiac aft."""
    k.lathe(a.part('Gun_ring', 'Armor'), [(.4, 0), (.4, .14), (.34, .2), (0, .2)], loc=(0, 6.2, 3.42), seg=12)
    m = a.pivot('Mount_mg', (0, 6.2, 3.65))
    st = a.part('Mg_body', 'Undercarriage', m)
    k.block(st, (.14, .5, .16), loc=(0, -.05, .12), chamfer=.01)
    st.box((.04, .06, .25), loc=(0, .1, -.05), bevel=0)
    k.lathe(a.part('Mg_barrel', 'Steel', m), [(.03, 0), (.03, .3), (.02, .35), (.018, 1.25), (0, 1.25)],
            loc=(0, -.3, .22), rot=K.FORWARD, seg=6)
    sh = a.part('Mg_shield', 'Armor', m)
    k.extrude(sh, [(-.35, -.15), (.35, -.15), (.3, .25), (-.3, .25)], .025, loc=(0, -.25, .2), rot=(R90 - .1, 0, 0),
              axis='Z', chamfer=.006)
    a.part('Ammo_can', 'Crate', m).box((.1, .25, .16), loc=(.14, -.05, .06), bevel=0)
    a.pivot('Muzzle_mg', (0, -1.55, .22), m)
    # The gun tub on the port wing with the pintle M134.
    gx = HALF + .02
    k.block(a.part('Gun_sponson', 'Armor'), (1.4, 1.4, .15), loc=(gx - .1, 4.1, GUNWALE + .07), chamfer=.03)
    a.part('Gun_sponson', 'Armor').limb((HALF, 4.1, 1.0), (gx + .3, 4.1, GUNWALE), .12, .12, bevel=0)
    k.ring(a.part('Gun_tub', 'Armor'), [(.5, 0), (.56, 0), (.56, .9), (.5, .9)], loc=(gx, 4.1, GUNWALE + .2),
           seg=12)
    g = a.part('Gatling', 'Steel')
    g.cyl(.04, .7, loc=(gx, 4.1, GUNWALE + .55), seg=6, bevel=0)
    for i in range(6):
        u = i * TAU / 6
        g.cyl(.012, .7, loc=(gx + math.cos(u) * .035, 3.65, GUNWALE + .95 + math.sin(u) * .035),
              rot=K.FORWARD, seg=4, bevel=0)
    k.block(g, (.14, .3, .14), loc=(gx, 4.1, GUNWALE + .88), chamfer=.01)
    # The Zodiac on its cradle on the aft deck (starboard).
    zx, zy = -HALF + .55, 7.0
    cr = a.part('Boat_cradle', 'Steel')
    for dy in (-.6, .6):
        cr.box((1.3, .08, .25), loc=(zx + .3, zy + dy, AFT_DECK + .12), bevel=0)
    tube = a.part('Boats', 'Rubber')
    tube.tube([(zx - .5, zy + 1.0, AFT_DECK + .45), (zx - .5, zy - .6, AFT_DECK + .45), (zx, zy - 1.15, AFT_DECK + .5),
               (zx + .5, zy - .6, AFT_DECK + .45), (zx + .5, zy + 1.0, AFT_DECK + .45)], .2, seg=8)
    k.block(a.part('Boat_floor', 'Armor'), (.8, 2.0, .1), loc=(zx, zy + .05, AFT_DECK + .25), chamfer=.02)
    a.part('Boat_motor', 'Undercarriage').box((.2, .25, .45), loc=(zx, zy + 1.15, AFT_DECK + .45), bevel=0)


def _deck_fittings(a):
    bol = a.part('Bollards', 'Steel')
    cleats = a.part('Cleats', 'Steel')
    for s in (-1, 1):
        for y in (-7.0, -1.5, 4.3, 8.1):
            for dy in (-.15, .15):
                bol.cyl(.08, .28, loc=(s * (HALF - .3), y + dy, GUNWALE + .35 if y < WH_Y0 else AFT_DECK + .14),
                        seg=8, bevel=0)
        for y in (-5.0, 0.0, 3.0):
            cleats.box((.08, .3, .06), loc=(s * (HALF - .28), y, GUNWALE + .26), bevel=0)
        k.ring(a.part('Life_rings', 'BarrelRed'), [(.22, -.04), (.3, -.04), (.3, .04), (.22, .04)],
               loc=(s * (HALF - .69), 5.6, AFT_DECK + .6), rot=(0, R90, 0), seg=10)
    # The stern anchor winch and the kedge anchor on the transom, the transom's lamps.
    k.lathe(a.part('Winch', 'Steel'), [(.25, -.4), (.25, -.35), (.18, -.3), (.18, .3), (.25, .35), (.25, .4)],
            loc=(1.4, 8.15, AFT_DECK + .3), rot=(0, R90, 0), seg=10)
    k.block(a.part('Winch', 'Steel'), (.5, .5, .25), loc=(.6, 8.15, AFT_DECK + .02), chamfer=.03)
    an = a.part('Anchor', 'Undercarriage')
    an.box((.08, .08, .9), loc=(2.6, STERN + .06, 1.2), bevel=0)
    an.box((.7, .08, .08), loc=(2.6, STERN + .06, .78), bevel=0)
    for s in (-1, 1):
        a.part('Tail_lamps', 'Lamp').box((.12, .02, .08), loc=(s * 2.8, STERN + .02, 1.6), bevel=0)


def landing_craft(a):
    """The landing craft: see the module docstring."""
    _hull(a)
    _well(a)
    _ramp(a)
    _aft(a)
    _weapons(a)
    _deck_fittings(a)
    k.clean(a)


BUILDERS = {
    'landing_craft': (landing_craft, dict(ao_distance=.9, grime_height=.6)),
}
