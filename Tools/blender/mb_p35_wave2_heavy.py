"""Prompt 35 wave 2 (lane A): the heavy turret and its bastion branch rebuilt from scratch on one barbette (owner
decision 4), each from its own spec (Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 2 (lane A)".

The sheet: a big twin 155 mm turret on an armoured concrete base (unit_refs: AK-130 naval mount on shore, A-222
Bereg, M284). A Hegemon coastal-battery barbette, 8 x 8 m: an octagonal battered (18-degree) concrete drum with
formwork lifts, a Team band and the race ring on its deck, the crew door in a cast porch, the ammunition jib crane
lifting a shell, shell pallets and charge canisters, floodlights, a sandbag-and-concertina front and a range post.

- heavy_turret (gun_155_twin_ap): an AK-130-class faceted gun house with two gun ports, twin 155 mm barrels with
  double-baffle brakes, the coaxial MG, the rangefinder housing with its ears across the rear roof, the commander's
  cupola, hatches, vents, a pintle MG on a riser and post (the roof-gun rule), antennas.
- heavy_turret_b (the bastion branch, unit_refs "Maginot fortress, small turrets at the corners"): the same gun
  house and, at the barbette's front corners, two round concrete bastions each carrying a steel cloche cupola with
  its HMG (`Mount_gun`, `Mount_gun.001`, hmg_roof) behind a firing slit.

Runtime nodes (kept): `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main` (its per-barrel `Muzzle_b1/b2_main` are
added by mb_p34_barrels on heavy_turret and written here on heavy_turret_b), `Muzzle_coax`, `Mount_mg` / `Muzzle_mg`,
on _b `Mount_gun[.001]` / `Muzzle_gun[.001]`. Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and the
wave's lean helpers; no other model's builder. Metres, +Z up, -Y front, +X left. Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau
APRON = .1
DECK = 2.75
TY, TZ = .2, 2.92           # the Turret pivot (the old model's)


def _octagon(h, c):
    return [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]


def barbette(a, corners=False):
    """The apron, the battered octagonal drum with its deck, the porch and door, the yard round it. corners=True
    (the bastion branch) leaves the front corner fittings to the bastions."""
    k.extrude(a.part('Base_apron', 'Concrete'), [(-4.0, -4.0), (4.0, -4.0), (4.0, 3.2), (3.2, 4.0), (-4.0, 4.0)],
              APRON, loc=(0, 0, APRON / 2), axis='Z', corner=.05, taper=(.98, .98), caps=(False, True))
    j = a.part('Base_joints', 'Undercarriage')
    for i in range(-3, 4):
        j.box((7.8, .03, .01), loc=(0, i * 1.15, APRON + .003), bevel=0)
        j.box((.03, 7.8, .01), loc=(i * 1.15, 0, APRON + .003), bevel=0)
    H = DECK - APRON
    k.extrude(a.part('Base', 'Plaster'), _octagon(3.85, 1.2), H, loc=(0, 0, APRON + H / 2), axis='Z', chamfer=.06,
              taper=(.82, .82), caps=(False, True))
    for z, f in ((.6, .6 / H), (1.2, 1.2 / H), (1.8, 1.8 / H)):
        hh = 3.85 * (1 - .18 * f) + .012
        cc = 1.2 * (1 - .18 * f)
        ring = _octagon(hh, cc)
        a.part('Lift_joints', 'Undercarriage').tube([(x, y, APRON + z) for x, y in ring + ring[:1]], .015, seg=3,
                                                     caps=False)
    hh = 3.85 * .835
    ring = _octagon(hh + .02, 1.2 * .835)
    a.part('Team_band', 'Team').tube([(x, y, DECK - .22) for x, y in ring + ring[:1]], .07, seg=4, caps=False)
    dj = a.part('Deck_joints', 'Undercarriage')
    for v in (-2.0, 2.0):
        dj.box((5.0, .03, .01), loc=(0, v, DECK + .003), bevel=0)
        dj.box((.03, 5.0, .01), loc=(v, 0, DECK + .003), bevel=0)
    k.ring(a.part('Race', 'Steel'), [(2.4, -.02), (2.55, -.02), (2.55, .08), (2.48, .14), (2.4, .14)],
           loc=(0, TY, DECK), seg=18, worn=(3,))
    bolts = a.part('Kit_bolts', 'Steel')
    for i in range(0 if corners else 12):
        u = i * TAU / 12
        bolts.cyl(.045, .05, loc=(math.cos(u) * 2.62, TY + math.sin(u) * 2.62, DECK + .02), seg=4, bevel=0)
    # Deck corner vents (outside the gun house's sweep) and drain spouts.
    for (x, y) in (() if corners else ((2.45, 2.45), (-2.45, 2.45))):
        k.lathe(a.part('Vents', 'Steel'), [(.1, 0), (.1, .35), (.2, .37), (.2, .44), (0, .48)], loc=(x, y, DECK),
                seg=8, worn=(3,))
    # The crew door in a cast porch at the rear right, a step, the door lamp.
    W.slab(a.part('Door_porch', 'Plaster'), (1.7, .7, 2.4), (-1.5, 3.55, APRON), caps=(False, True))
    K.door(a, (-1.5, 3.91, APRON + .15), (1.1, 2.0), normal=(0, 1, 0), mat='Armor')
    a.part('Door_hazard', 'Hazard').box((1.5, .04, .1), loc=(-1.5, 3.915, APRON + 2.25), bevel=0)
    a.part('Lamps', 'Lamp').box((.22, .06, .12), loc=(-1.5, 3.93, APRON + 2.35), rot=(-.3, 0, 0), bevel=0)
    # The ammunition jib crane at the rear left: a post, the jib (an open truss), the hook lifting a 155 mm shell.
    cr = a.part('Crane', 'CraneYellow')
    cx, cy = 2.6, 3.3
    cr.cyl(.12, 3.6, loc=(cx, cy, APRON + 1.8), seg=8, bevel=0)
    k.block(a.part('Crane_base', 'Concrete'), (.7, .7, .3), loc=(cx, cy, APRON), chamfer=.04)
    for z in (APRON + 3.5, APRON + 3.1):
        cr.box((.08, 2.2, .08), loc=(cx, cy - 1.0, z), bevel=0)
    tr = a.part('Crane_truss', 'Steel')
    for i in range(5):
        y = cy - .1 - i * .5
        tr.tube([(cx, y, APRON + 3.1), (cx, y - .5, APRON + 3.5)], .015, seg=3)
    tr.tube([(cx, cy, APRON + 3.6), (cx, cy - 2.0, APRON + 3.5)], .012, seg=3)
    a.part('Kit_cables', 'Undercarriage').tube([(cx, cy - 1.9, APRON + 3.1), (cx, cy - 1.9, APRON + 1.5)], .012,
                                               seg=3)
    k.lathe(a.part('Shells', 'Gilded'), [(0, 0), (.08, .12), (.078, .7), (.04, .78), (0, .8)],
            loc=(cx, cy - 1.9, APRON + .7), seg=8)
    # Shell pallets and charge canisters, the shells standing in rows; a sandbag front with concertina.
    pal = a.part('Pallets', 'Wood')
    for (x, y) in ((3.3, 1.4), (3.3, 2.4)):
        pal.box((.9, .9, .12), loc=(x, y, APRON + .06), bevel=0)
    for i in range(3):
        for jj in range(2):
            k.lathe(a.part('Shells', 'Gilded'), [(.075, 0), (.075, .55), (.04, .7), (0, .74)],
                    loc=(3.3 + (i - 1) * .26, 1.4 + (jj - .5) * .3, APRON + .12), seg=6, caps=(False, True))
    K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.85, .6, .45), (3.3, 2.4, APRON + .12))
    for i in range(1 if corners else 3):
        a.part('Charge_cans', 'Fuel').cyl(.14, .7, loc=(3.35, -.2 + i * .32, APRON + .35), seg=8, bevel=0)
    if not corners:
        W.bags(a, [(-3.9, -3.9, APRON), (-1.5, -3.9, APRON)], layers=1, bag=(.6, .3, .17), seed=11)
        W.bags(a, [(1.5, -3.9, APRON), (3.9, -3.9, APRON), (3.9, -2.4, APRON)], layers=2, bag=(.6, .3, .17), seed=12)
    K.wire_fence(a, [(-1.3, -4.0, APRON), (1.3, -4.0, APRON)], h=.9, post=.65, strands=3, concertina=False)
    K.floodlight(a, (-3.8, 3.8, APRON), facing=(.6, -1, -.4), pole=3.2)
    if not corners:
        K.floodlight(a, (3.85, -1.2, APRON), facing=(-1, -.3, -.4), pole=2.8)
    post = a.part('Range_post', 'Hazard')
    post.cyl(.04, 1.6, loc=(-3.7, -2.0, APRON + .8), seg=5, bevel=0)
    for z in (.5, 1.1):
        a.part('Range_bands', 'Charred').cyl(.045, .15, loc=(-3.7, -2.0, APRON + z), seg=5, bevel=0)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .4), (.04, .46), (0, .48)], loc=(-.4, 3.75, APRON),
            seg=8, worn=(1,))
    for i in range(8):
        u = i * TAU / 8
        K.dust(a, (math.cos(u) * 3.9, math.sin(u) * 3.9, APRON), radius=1.4, k=.3)


def gun_house(a):
    """The turning gun house on the race (common to both): faceted shell, gun ports, twin 155 mm, coax, rangefinder,
    cupola, hatches, vents, the raised pintle MG, antennas. Returns the Turret pivot."""
    t = a.pivot('Turret', (0, TY, TZ))
    h = 1.65
    top = .05 + h
    k.extrude(a.part('Turret_body', 'Armor', t), [(-1.3, -2.25), (1.3, -2.25), (2.3, -1.2), (2.3, 2.6), (1.8, 3.35),
                                                  (-1.8, 3.35), (-2.3, 2.6), (-2.3, -1.2)], h,
              loc=(0, 0, .05 + h / 2), axis='Z', chamfer=.05, corner=.05, taper=(.82, .86), caps=(False, True))
    # Team side bands, the roof plate seams.
    tb = a.part('Turret_band', 'Team', t)
    for s in (-1, 1):
        tb.box((.03, 3.2, .3), loc=(s * 2.17, .7, .9), rot=(0, -s * .09, 0), bevel=0)
    K.weld(a.part('Kit_welds', 'Charred', t), [(-1.5, -.8, top + .005), (1.5, -.8, top + .005)])
    K.weld(a.part('Kit_welds', 'Charred', t), [(-1.7, 1.3, top + .005), (1.7, 1.3, top + .005)])
    seams = a.part('Panel_seams', 'Charred', t)
    for s in (-1, 1):
        for y in (.2, 1.6):
            seams.box((.02, .04, 1.4), loc=(s * (2.3 - .82 * .09 - .06), y, .8), rot=(0, -s * .1, 0), bevel=0)
    for x in (-1.0, -.35, .35, 1.0):
        seams.box((.04, .02, .9), loc=(x * 1.2, -2.17, .95), rot=(.06, 0, 0), bevel=0)
    a.part('Hazard_marks', 'Hazard', t).box((2.0, .03, .12), loc=(0, 3.27, .3), rot=(-.07, 0, 0), bevel=0)
    # The crew rail round the roof's walkway (sides and rear) and the ladder up the gun house's rear.
    rail = a.part('Railings', 'Steel', t)
    for path in ([(1.8, -.6, top), (1.8, 1.4, top)], [(-1.8, -.6, top), (-1.8, 1.4, top)],
                 [(1.8, 2.3, top), (1.8, 2.75, top), (-1.8, 2.75, top), (-1.8, 2.3, top)]):
        K.railing(rail, path, h=.8, post=.5, r=.018)
    K.ladder(a.part('Ladders', 'Steel', t), (.9, 3.5, .1), (.9, 2.95, top + .6), width=.45, step=.3, r=.018)
    # The two gun ports (cast mantlets) and the twin 155 mm with double-baffle brakes; the coax between.
    for s in (-1, 1):
        k.block(a.part('Mantlet', 'Armor', t), (.6, .55, .7), loc=(s * .78, -2.35, .37), chamfer=.05)
        # The barrel: root collar, the jacket, the fume extractor, the tapered chase; the double-baffle brake.
        k.lathe(a.part('Main_cannon', 'Steel', t), [(.17, -.05), (.17, .12), (.13, .18), (.13, 1.0), (.19, 1.1),
                                                    (.19, 1.6), (.12, 1.7), (.105, 3.56), (0, 3.56)],
                loc=(s * .78, -2.6, .72), rot=K.FORWARD, seg=8, worn=(4, 5))
        k.lathe(a.part('Muzzle_brake', 'Undercarriage', t), [(.1, 3.54), (.18, 3.56), (.18, 3.86), (.08, 3.86),
                                                             (0, 3.84)], loc=(s * .78, -2.6, .72), rot=K.FORWARD,
                seg=8, worn=(1,))
        for f in (3.64, 3.76):
            a.part('Brake_ports', 'Charred', t).box((.4, .05, .06), loc=(s * .78, -2.6 - f, .72), bevel=0)
    a.pivot('Muzzle_main', (0, -6.46, .72), t)
    a.part('Coax', 'Steel', t).cyl(.035, .2, loc=(0, -2.2, .72), rot=(R90, 0, 0), seg=6, bevel=0)
    a.pivot('Muzzle_coax', (0, -2.29, .72), t)
    # The rangefinder housing across the rear roof with its two armoured ears.
    k.block(a.part('Sight', 'Armor', t), (3.2, .5, .38), loc=(0, 1.9, top), chamfer=.05)
    for s in (-1, 1):
        k.lathe(a.part('Sight', 'Armor', t), [(.2, -.25), (.2, .25)], loc=(s * 1.75, 1.9, top + .19), rot=(0, R90, 0),
                seg=8)
        a.part('Glass', 'Glass', t).box((.03, .2, .14), loc=(s * 2.0, 1.85, top + .2), bevel=0)
    # The commander's cupola (a collar, the hatch lid, three vision blocks) and the loader's square hatch.
    k.lathe(a.part('Cupola', 'Armor', t), [(.45, 0), (.45, .18), (.4, .24), (0, .24)], loc=(-.9, .6, top), seg=10,
            worn=(2,))
    k.lathe(a.part('Hatches', 'Armor', t), [(.34, .24), (.34, .29), (0, .31)], loc=(-.9, .6, top), seg=10)
    for i in range(3):
        u = i * TAU / 3 + .5
        a.part('Glass', 'Glass', t).box((.12, .03, .08), loc=(-.9 + math.cos(u) * .45, .6 + math.sin(u) * .45,
                                                              top + .12), rot=(0, 0, u + R90), bevel=0)
    k.block(a.part('Hatches', 'Armor', t), (.7, .8, .06), loc=(.2, -.3, top), chamfer=0)
    K.handle(a.part('Kit_handles', 'Steel', t), (.0, -.3, top + .06), (.4, -.3, top + .06), (0, 0, 1), h=.06)
    for x in (-1.2, 1.2):
        k.lathe(a.part('Vents', 'Steel', t), [(.15, 0), (.15, .1), (.1, .14), (0, .14)], loc=(x, 2.85, top - .05),
                seg=8)
    K.pintle_mg(a, t, (1.0, .5, top), scale=1.2, post=.35, riser=.15)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.5, 2.9, top - .05), h=1.4, r=.025)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.6, 2.9, top - .05), h=1.1, r=.025)
    K.grille(a, (2.18, 2.0, .7), 1.0, .35, facing=(1, 0, 0), slats=5, parent=t)
    for s in (-1, 1):
        a.part('Lamps', 'Lamp', t).box((.16, .04, .1), loc=(s * 1.25, -1.98, top - .4), bevel=0)
        a.part('Lamp_rims', 'Steel', t).box((.2, .08, .04), loc=(s * 1.25, -1.97, top - .33), bevel=0)
    return t


def heavy_turret(a):
    barbette(a)
    gun_house(a)
    k.clean(a)


def heavy_turret_b(a):
    """heavy_turret_b: the gun house plus the two corner bastions with their cloche cupolas (module docstring)."""
    barbette(a, corners=True)
    t = gun_house(a)
    # Per-barrel muzzles (the wrapper does this for heavy_turret only): left to right.
    a.pivot('Muzzle_b1_main', (-.78, 0, 0), 'Muzzle_main')
    a.pivot('Muzzle_b2_main', (.78, 0, 0), 'Muzzle_main')
    K.suffixed(a)
    for i, s in enumerate((-1, 1)):
        x, y = s * 2.62, -2.62
        tag = '' if i == 0 else '__001'
        k.lathe(a.part('Walls_bastions', 'Plaster'), [(1.2, APRON), (1.2, APRON + .2), (1.05, 2.45), (1.1, 2.5),
                                                (1.1, 2.62), (0, 2.62)], loc=(x, y, 0), seg=14, worn=(3,))
        a.part('Team_band', 'Team').cyl(1.08, .14, loc=(x, y, 2.3), seg=10, bevel=0)
        m = a.pivot(K.name('Mount_gun', i), (x, y, 2.71))
        # The cloche: a steel dome with its brim, a firing slit facing forward, the HMG barrel, a periscope stub.
        k.lathe(a.part(f'Cloche{tag}', 'Armor', m), [(.75, -.09), (.82, -.04), (.82, .02), (.72, .15), (.62, .45),
                                                    (.4, .7), (.15, .8), (0, .82)], seg=12, worn=(2, 4))
        a.part(f'Cloche_slit{tag}', 'Undercarriage', m).box((.5, .1, .12), loc=(0, -.66, .32), rot=(.5, 0, 0),
                                                            bevel=0)
        a.part(f'Cloche_gun{tag}', 'Steel', m).cyl(.03, .8, loc=(0, -1.0, .3), rot=(R90 - .2, 0, 0), seg=6, bevel=0)
        a.part(f'Cloche_gun{tag}', 'Steel', m).cyl(.05, .15, loc=(0, -1.33, .37), rot=(R90 - .2, 0, 0), seg=6, bevel=0)
        a.part(f'Cloche_sight{tag}', 'Armor', m).box((.14, .14, .16), loc=(.25, .1, .78), bevel=0)
        a.pivot(K.name('Muzzle_gun', i), (0, -1.3, .3), m)
        # The bastion's loopholes, a lift joint, rungs up its rear.
        for u in (-.9, -.3, .3, .9):
            a.part('Slits', 'Undercarriage').box((.35, .08, .12), loc=(x + math.sin(u) * 1.09, y - math.cos(u) * 1.09,
                                                                      1.2), rot=(0, 0, u), bevel=0)
        ring = [(x + math.cos(v) * 1.135, y + math.sin(v) * 1.135, 1.5) for v in (j * TAU / 12 for j in range(13))]
        a.part('Lift_joints', 'Undercarriage').tube(ring, .012, seg=3, caps=False)
        for z in (.9, 1.6, 2.3):
            a.part('Ladders', 'Steel').tube([(x + s * .22, y + 1.12, z), (x + s * .62, y + .98, z)], .015, seg=3)
    k.clean(a)


BUILDERS = {
    'heavy_turret': (heavy_turret, dict(ao_distance=.9, grime_height=.6, ao_strength=.65)),
    'heavy_turret_b': (heavy_turret_b, dict(ao_distance=.9, grime_height=.6, ao_strength=.65)),
}
