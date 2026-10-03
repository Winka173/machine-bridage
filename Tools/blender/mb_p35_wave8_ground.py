"""Prompt 35 wave 8 (lane A): a tank and a boat rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library and mb_p35_w5parts' lean running gear. DECISIONS "Prompt 35
wave 8 (lane A)".

- heavy_tank: Object 195 / T-95 (sheet: 0.8 x): a long low hull on seven road wheels under side skirts, the small
  angular unmanned turret with the big 152 mm (thermal sleeve, fume extractor, baffle brake) in its mantlet, the
  30 mm beside it, the commander's sight, smoke banks, the 12.7 mm on its post, stowage. heavy_tank_hd is the same
  builder with detail=True (mb_detail: bolt rows, more segments; no pivot added or moved).
- river_gunboat: a riverine monitor (Project 1204 Shmel class): a shallow hull with a raked bow and spray strakes,
  the tank-type turret forward with the 100 mm, the low armoured wheelhouse with its mast, the machine-gun tub, the
  rocket rail aft, rails, bollards, life rings, the engine vents and the twin exhausts.

Runtime nodes are the old models' (positions within a few centimetres of the old pivots): see each builder.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_detail as hd
import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= heavy_tank (Object 195)
def heavy_tank(a, detail=False):
    """See the module docstring. Runtime: Turret, Main_cannon, Muzzle_brake, Muzzle_main, Coax / Muzzle_coax (the
    30 mm), Mount_mg / Muzzle_mg, Point_fire, Point_exhaust."""
    hd.mark(a, detail)
    TX, TW, WR = 1.16, .6, .33
    wheels = [-2.55 + i * .83 for i in range(7)]
    W.running_gear(a, TX, TW, WR, wheels, (-3.2, .52, .28), (3.05, .55, .3), rollers=(-1.3, 0, 1.3), roller_z=.86,
                   top_hidden=.78, disc_mat='Armor', seg=12 if detail else 8, link_pitch=.3 if detail else .4)
    hull = a.part('Hull', 'Team')
    W.side_hull(hull, [(3.25, .45), (3.27, 1.0), (3.05, 1.3), (-1.9, 1.32), (-3.35, .92), (-3.4, .68),
                       (-3.1, .42)], 2.2)
    W.side_hull(a.part('Armor', 'Armor'), [(3.15, .32), (-2.95, .32), (-3.25, .6), (3.15, .6)], 1.75, chamfer=.03)
    # Sponsons, skirts with their rubber edge and hinge line, the glacis composite modules.
    for s in (-1, 1):
        K.fender(a.part('Fenders', 'Team'), TX, -3.35, 3.2, .98, .66, s)
        for i in range(6):
            yc = -3.15 + (i + .5) * 1.05
            k.block(a.part('Skirts', 'Team'), (.05, 1.02, .46), loc=(s * (TX + .35), yc, .72), chamfer=.012)
            a.part('Skirt_edge', 'Rubber').box((.03, 1.0, .08), loc=(s * (TX + .35), yc, .45), bevel=0)
        a.part('Kit_hinges', 'Steel').tube([(s * (TX + .39), -3.1, .93), (s * (TX + .39), 3.0, .93)], .018, seg=5)
        a.part('Team_band', 'Team').box((.012, 2.4, .1), loc=(s * (TX + .385), -.4, .8), bevel=0)
    for i in range(3):
        k.block(a.part('Glacis_armor', 'Armor'), (.62, .5, .08), loc=(-.68 + i * .68, -2.55, 1.13),
                rot=(-.57, 0, 0), chamfer=.015)
    # The crew capsule hatches in the hull front (Object 195: the crew sits in the hull), periscopes.
    for x in (-.55, 0, .55):
        hc = (x, -1.55, 1.32)
        k.ring(a.part('Hatch_fittings', 'Steel'), [(.2, 0), (.25, 0), (.25, .05), (.2, .05)], loc=hc, seg=10)
        k.lathe(a.part('Hatches', 'Armor'), [(0, .07), (.18, .065), (.22, .04), (.22, .02)], loc=hc, seg=10)
        a.part('Periscope_hoods', 'Armor').box((.14, .1, .07), loc=(x, -1.85, 1.33), rot=(-.3, 0, 0), bevel=0)
        a.part('Periscope', 'Glass').box((.11, .01, .04), loc=(x, -1.905, 1.325), rot=(-.3, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .95, -3.3, 1.02), (0, -1, .15), r=.06, guard=True)
        a.part('Light_rims', 'Armor').box((.18, .04, .14), loc=(s * .95, -3.28, 1.02), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .07), loc=(s * .9, 3.28, 1.15), bevel=0)
    W.tow_set(a, -3.44, .62, .7, (0, -1, 0))
    # Engine deck: two grille banks, the exhaust louvres right rear, stowage bins and a fuel drum rack.
    K.grille(a, (.55, 2.2, 1.325), .8, 1.3, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.grille(a, (-.55, 2.2, 1.325), .8, 1.3, facing=(0, 0, 1), slats=6, frame_mat='Team')
    a.part('Deck', 'Armor').box((2.1, 1.7, .03), loc=(0, 2.2, 1.31), bevel=0)
    K.grille(a, (1.2, 3.29, .95), .5, .24, facing=(0, 1, 0), slats=3, frame_mat='Armor')
    K.soot(a, (1.2, 3.3, 1.0), radius=.4, k=.45)
    for s in (-1, 1):
        K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.3, 1.1, .3), (s * 1.3, 1.6, 1.13),
                bands=1)
        a.part('Stowage', 'Armor').cyl(.2, .7, loc=(s * .6, 3.4, 1.0), rot=(0, R90, 0), seg=10, bevel=.02)
    K.tow_cable(a.part('Kit_cables', 'Steel'), [(1.32, -2.6, 1.0), (1.36, -1.0, 1.02), (1.36, .6, 1.02)], r=.025)
    if detail:
        bolts = a.part('Hull_bolts', 'Steel')
        for s in (-1, 1):
            hd.bolt_line(bolts, (s * 1.1, -2.9, 1.31), (s * 1.1, 3.0, 1.31), 24)
            hd.bolt_line(bolts, (s * (TX + .38), -3.1, .6), (s * (TX + .38), 3.0, .6), 20, rot=hd.RIGHT_X)
    _heavy_turret(a, detail)
    a.pivot('Point_fire', (0, 2.1, 1.38))
    a.pivot('Point_exhaust', (1.2, 3.2, 1.0))
    k.clean(a)


def _heavy_turret(a, detail):
    """The small unmanned turret on the Turret pivot: a low faceted house with the wedge front, the cheek blocks,
    the mantlet with the 152 mm and the 30 mm beside it, the sight heads, smoke banks, the 12.7 mm on its post,
    the bustle box and antennas."""
    t = a.pivot('Turret', (0, .45, 1.32))
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.04), .95, h=.08)
    body = a.part('Turret_body', 'Team', t)
    W.poly_turret(body, [
        (0, [(-.5, -1.45), (.5, -1.45), (1.0, -.7), (1.0, 1.3), (.8, 1.55), (-.8, 1.55), (-1.0, 1.3), (-1.0, -.7)]),
        (.3, [(-.45, -1.62), (.45, -1.62), (1.05, -.8), (1.05, 1.35), (.85, 1.62), (-.85, 1.62), (-1.05, 1.35),
              (-1.05, -.8)]),
        (.5, [(-.35, -1.25), (.35, -1.25), (.85, -.6), (.85, 1.25), (.7, 1.5), (-.7, 1.5), (-.85, 1.25),
              (-.85, -.6)])])
    for s in (-1, 1):
        W.poly_turret(a.part('Turret_armor', 'Armor', t), [
            (.04, [(s * .5, -1.5), (s * .95, -.78), (s * .95, -.5), (s * .55, -.9)]),
            (.42, [(s * .45, -1.55), (s * 1.0, -.85), (s * 1.0, -.5), (s * .5, -.95)])], chamfer=.015)
        K.smoke_dischargers(a, s * 1.0, -.3, .36, s, count=4, parent=t)
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (.5, .4, .42), loc=(0, -1.62, .3), c=.04)
    K.gun_barrel(a, 'Main_cannon', t, 0, -1.82, .32, 3.56, .1, seg=14 if detail else 12, extractor=(.4, 1.5, .5),
                 brake='baffle')
    a.pivot('Muzzle_main', (0, -5.68, .32), t)
    # The 30 mm beside the gun: its housing and barrel.
    K.chamfer_box(a.part('Coax_housing', 'Armor', t), (.2, .4, .2), loc=(.3, -1.6, .42), c=.02)
    k.lathe(a.part('Coax', 'Steel', t), [(.03, 0), (.03, .2), (.022, .22), (.022, .38), (0, .39)],
            loc=(.3, -1.6, .42), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (.3, -1.99, .42), t)
    # Gunner's sight left, the commander's panoramic sight on its mast right.
    K.chamfer_box(a.part('Sight', 'Armor', t), (.3, .34, .24), loc=(-.55, -.8, .58), c=.03)
    a.part('Glass', 'Glass', t).box((.22, .01, .12), loc=(-.55, -.975, .6), bevel=0)
    a.part('Sight', 'Steel', t).cyl(.06, .22, loc=(.45, -.1, .6), seg=8, bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.26, .26, .2), loc=(.45, -.1, .78), c=.03)
    a.part('Glass', 'Glass', t).box((.16, .01, .1), loc=(.45, -.235, .8), bevel=0)
    K.pintle_mg(a, t, (.55, .5, .46), length=.65, post=.1, shield=False)
    # Bustle box, antennas, the roof panel.
    K.crate(a.part('Stowage', 'Armor', t), a.part('Kit_latches', 'Steel', t), (1.2, .3, .3), (0, 1.75, .14),
            bands=1)
    for x in (-.7, .7):
        K.whip_antenna(a.part('Antennas', 'Steel', t), (x, 1.2, .5), h=.4, lean=.2)
    a.part('Team_band', 'Team', t).box((.9, .7, .012), loc=(0, .4, .505), bevel=0)
    if detail:
        hd.bolt_line(a.part('Turret_bolts', 'Steel', t), (-.8, 1.4, .5), (.8, 1.4, .5), 10)


# ============================================================================= river_gunboat (Shmel-class monitor)
def _hull_rings(y_stations):
    """Hard-chine sections [(y, half_beam_deck, half_beam_chine, deck_z, chine_z, keel_z)] -> loft rings."""
    rings = []
    for y, hd_, hc, zd, zc, zk in y_stations:
        rings.append([(-hd_, y, zd), (-hc, y, zc), (-hc * .35, y, zk + .06), (0, y, zk), (hc * .35, y, zk + .06),
                      (hc, y, zc), (hd_, y, zd)])
    return rings


def river_gunboat(a):
    """See the module docstring. Runtime: Turret, Main_cannon, Muzzle_brake, Muzzle_main (the 100 mm forward),
    Mount_mg / Muzzle_mg (the aft gun tub), Point_fire, Point_exhaust."""
    st = [(4.0, 1.42, 1.38, .82, .32, .12), (3.0, 1.5, 1.45, .8, .3, .1), (1.5, 1.52, 1.47, .8, .28, .1),
          (0.0, 1.52, 1.45, .82, .28, .1), (-1.5, 1.42, 1.3, .86, .32, .12), (-2.6, 1.1, .9, .93, .42, .18),
          (-3.3, .55, .35, 1.0, .6, .35), (-3.6, .06, .04, 1.06, .85, .7)]
    a.part('Hull', 'Team').loft(_hull_rings(st), bevel=0)
    deck = a.part('Deck', 'Armor')
    k.extrude(deck, [(-1.4, 3.9), (1.4, 3.9), (1.44, -1.4), (1.0, -2.6), (.4, -3.3), (-.4, -3.3), (-1.0, -2.6),
                     (-1.44, -1.4)], .04, loc=(0, 0, .84), axis='Z')
    # Rub rail and spray strakes along the sides, old tyres hung as fenders, the boot-top band.
    for s in (-1, 1):
        a.part('Undercarriage', 'Undercarriage').tube([(s * 1.42, 3.95, .8), (s * 1.53, 1.5, .79),
                                                       (s * 1.5, -1.5, .84), (s * 1.08, -2.6, .92),
                                                       (s * .5, -3.3, 1.0)], .045, seg=5)
        for z, y1 in ((.45, -2.9), (.6, -3.15)):
            a.part('Strakes', 'Armor').tube([(s * 1.47, 2.5, z), (s * 1.42, -1.5, z + .03), (s * .9 * (1.1 - z), y1,
                                                                                           z + .12)], .025, seg=4)
        for y in (-.6, 1.0, 2.6):
            a.part('Fender_tyres', 'Rubber').torus(.16, .06, loc=(s * 1.55, y, .55), rot=(0, R90, 0), seg=10, ring=5)
            a.part('Fender_ropes', 'Canvas').cyl(.012, .25, loc=(s * 1.54, y, .78), seg=4, bevel=0)
        a.part('Team_band', 'Team').box((.012, 4.6, .1), loc=(s * 1.53, .6, .68), bevel=0)
        K.railing(a.part('Railings', 'Steel'), [(s * 1.36, 3.85, .86), (s * 1.38, 2.2, .86)], h=.5, post=.55,
                  r=.016)
        K.railing(a.part('Railings', 'Steel'), [(s * 1.38, -.4, .86), (s * 1.3, -1.7, .88), (s * .9, -2.6, .95)],
                  h=.45, post=.6, r=.016)
        for y in (3.6, -2.3):
            k.lathe(a.part('Bollards', 'Steel'), [(.07, 0), (.07, .16), (.1, .18), (.1, .22), (0, .22)],
                    loc=(s * 1.1 * (1 if y > 0 else .7), y, .86), seg=8)
    # Anchor and its windlass on the forecastle, the jack staff.
    k.lathe(a.part('Windlass', 'Armor'), [(.12, -.2), (.12, .2)], loc=(0, -2.85, 1.02), rot=(0, R90, 0), seg=10)
    a.part('Anchor', 'Steel').box((.08, .05, .4), loc=(.35, -3.32, .82), rot=(.4, 0, 0), bevel=0)
    a.part('Anchor', 'Steel').box((.32, .05, .06), loc=(.35, -3.4, .64), rot=(.4, 0, 0), bevel=0)
    a.part('Antennas', 'Steel').cyl(.015, .6, loc=(0, -3.5, 1.35), seg=4, bevel=0)
    _boat_turret(a)
    _boat_wheelhouse(a)
    _boat_aft(a)
    a.pivot('Point_fire', (0, .5, 1.1))
    a.pivot('Point_exhaust', (.8, 3.76, .5))
    k.clean(a)


def _boat_turret(a):
    """The tank-type turret forward on its barbette: the cast-look house (lofted), the mantlet, the 100 mm with its
    bore evacuator and baffle brake, the commander's cupola, the sight drum, the stowage on the turret rear."""
    k.lathe(a.part('Barbette', 'Armor'), [(.95, 0), (.95, .1), (.88, .14)], loc=(0, -1.3, .84), seg=16)
    t = a.pivot('Turret', (0, -1.3, .98))
    body = a.part('Turret_body', 'Team', t)
    W.poly_turret(body, [
        (0, [(-.55, -.85), (.55, -.85), (.85, -.3), (.85, .55), (.6, .85), (-.6, .85), (-.85, .55), (-.85, -.3)]),
        (.3, [(-.5, -.9), (.5, -.9), (.82, -.35), (.82, .6), (.58, .9), (-.58, .9), (-.82, .6), (-.82, -.35)]),
        (.5, [(-.35, -.62), (.35, -.62), (.6, -.25), (.6, .5), (.45, .72), (-.45, .72), (-.6, .5), (-.6, -.25)])])
    K.chamfer_box(a.part('Turret_armor', 'Armor', t), (.42, .3, .34), loc=(0, -.92, .2), c=.04)
    K.gun_barrel(a, 'Main_cannon', t, 0, -1.02, .3, 1.23, .065, seg=10, extractor=(.45, 1.6, .3), brake='baffle')
    a.pivot('Muzzle_main', (0, -2.55, .3), t)
    k.ring(a.part('Turret_armor', 'Armor', t), [(.2, 0), (.25, 0), (.25, .1), (.2, .1)], loc=(.28, .2, .5), seg=10)
    k.lathe(a.part('Turret_armor', 'Armor', t), [(0, .16), (.18, .15), (.22, .12), (.22, .1)], loc=(.28, .2, .5),
            seg=10)
    a.part('Sight_drum', 'Armor', t).cyl(.11, .16, loc=(-.3, -.3, .58), seg=10, bevel=0)
    a.part('Sight_glass', 'Glass', t).box((.1, .01, .06), loc=(-.3, -.41, .6), bevel=0)
    K.crate(a.part('Stowage', 'Armor', t), a.part('Kit_latches', 'Steel', t), (.7, .25, .22), (0, .93, .12), bands=1)
    a.part('Team_band', 'Team', t).box((.6, .5, .012), loc=(0, .05, .505), bevel=0)


def _boat_wheelhouse(a):
    """The low armoured wheelhouse: sloped faces with slit windows, the roof with its searchlight, the mast with
    the navigation radar array and the yard with antennas, the life rings on its sides, the engine vents behind."""
    wh = a.part('Deckhouse', 'Team')
    W.poly_turret(wh, [(.84, [(-1.0, -.35), (1.0, -.35), (1.0, 1.6), (-1.0, 1.6)]),
                       (1.4, [(-1.0, -.42), (1.0, -.42), (1.0, 1.6), (-1.0, 1.6)]),
                       (1.75, [(-.8, -.05), (.8, -.05), (.8, 1.45), (-.8, 1.45)])], chamfer=.04)
    for x in (-.5, 0, .5):
        a.part('Windows', 'Glass').box((.36, .02, .1), loc=(x, -.24, 1.58), rot=(-.75, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Windows', 'Glass').box((.02, .3, .1), loc=(s * .91, .3, 1.58), rot=(0, s * .5, 0), bevel=0)
        K.door(a, (s * 1.0, 1.0, .86), size=(.5, .8), normal=(s, 0, 0), mat='Team', frame_mat='Armor')
        k.ring(a.part('Life_rings', 'BarrelRed'), [(.13, -.03), (.2, -.03), (.2, .03), (.13, .03)],
               loc=(s * 1.03, .2, 1.15), rot=(0, R90, 0), seg=10)
    # Searchlight, the mast with the radar array and yard, whips.
    a.part('Steel', 'Steel').cyl(.05, .15, loc=(.5, .2, 1.83), seg=6, bevel=0)
    k.lathe(a.part('Lamps', 'Armor'), [(.12, -.12), (.12, .12), (.09, .14)], loc=(.5, .14, 1.98), rot=K.FORWARD,
            seg=10)
    a.part('Lamps', 'Lamp').cyl(.1, .02, loc=(.5, .01, 1.98), rot=K.FORWARD, seg=10, bevel=0)
    m = a.part('Steel', 'Steel')
    m.cyl(.06, 1.0, loc=(-.2, .9, 2.25), seg=8, bevel=0)
    m.box((1.3, .05, .05), loc=(-.2, .9, 2.55), bevel=0)
    a.part('Radar_back', 'Armor').box((.12, .2, .12), loc=(-.2, .9, 2.72), bevel=0)
    a.part('Radar_array', 'Armor').box((.8, .08, .1), loc=(-.2, .82, 2.8), bevel=0)
    for x in (-.8, .4):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x, .9, 2.57), h=.3, lean=.0)
    a.part('Team_band', 'Team').box((1.4, .9, .012), loc=(0, .7, 1.755), bevel=0)
    # Engine room vents and the funnel-less exhausts behind the wheelhouse.
    for x in (-.6, .6):
        k.lathe(a.part('Vents', 'Armor'), [(.1, 0), (.1, .3), (.14, .32), (.16, .4), (.14, .5), (0, .5)],
                loc=(x, 2.0, .86), seg=8)
    K.grille(a, (0, 2.3, .875), 1.0, .5, facing=(0, 0, 1), slats=5, frame_mat='Armor')


def _boat_aft(a):
    """The aft deck: the gun tub (sandbagged ring) with the heavy machine gun on its pedestal (Mount_mg), ammunition
    boxes, the smoke pots on the transom, the twin exhausts, the ensign staff, the rope coil."""
    k.ring(a.part('Ciws_tub', 'Armor'), [(.55, 0), (.6, 0), (.6, .35), (.55, .35)], loc=(0, 3.1, .86), seg=14)
    K.pintle_mg(a, None, (0, 3.1, .9), scale=1.5, length=.4, post=0, shield=True)
    K.crate(a.part('Stowage', 'Crate'), a.part('Kit_latches', 'Steel'), (.4, .25, .2), (.85, 3.0, .96), bands=1)
    K.crate(a.part('Stowage', 'Crate'), a.part('Kit_latches', 'Steel'), (.4, .25, .2), (-.85, 3.2, .96), bands=1)
    for x in (-.8, .8):
        a.part('Exhaust', 'Steel').cyl(.08, .3, loc=(x, 3.95, .55), rot=K.BACKWARD, seg=8, bevel=0)
        K.soot(a, (x, 4.05, .55), radius=.3, k=.45)
    for x in (-.4, .4):
        a.part('Smoke_pots', 'Armor').cyl(.12, .3, loc=(x, 3.85, .99), seg=8, bevel=0)
    a.part('Steel', 'Steel').cyl(.015, .8, loc=(0, 3.95, 1.25), seg=4, bevel=0)
    a.part('Ensign', 'Team').box((.01, .3, .2), loc=(0, 4.1, 1.55), bevel=0)
    a.part('Rope_coil', 'Canvas').torus(.15, .04, loc=(-1.0, 2.7, .9), seg=10, ring=4)


BUILDERS = {
    'heavy_tank': (heavy_tank, dict(ao_distance=.6, grime_height=.55)),
    'river_gunboat': (river_gunboat, dict(ao_distance=.6, ao_strength=.5, grime_height=.05)),
}
