"""Prompt 35 wave 6 (lane B): Kraken, the aircraft carrier, rebuilt from scratch (spec: Tools/blender/specs/kraken.json).

General Kessler's flagship (variant of leviathan with all 14 parts; BossText: the longest ship afloat, a flat flight
deck with aircraft parked on it and a CIWS ring; tip: the flight deck feeds its aircraft and carries the air raid,
break it first; the CIWS shoot missiles down). A Kuznetsov / Nimitz-line carrier with its features drawn 1.3-1.5 x
for the boss read (the def's modelSize 110 x 18.4 x 24 m; waterline z 0, keel -3, flight deck z 9): the flared hull
with the bulbous bow, the knuckle, the dark bottom, boot-top and the hull's plating seams and portholes, the
overhanging flight deck with the angled landing deck to port, the ski-jump bow, the deck-edge sponsons and the
three lifts, the catwalks and nets along the edges; the island to starboard: three stepped blocks with the bridge
window bands, the main mast with the spinning search radar (`Part_radar` > `Radar`), the fixed array faces (the
APS's eyes, `Mount_APS`), the funnel (`Part_engine`: the machinery's uptakes, one shade off); the weapons: three
heavy anti-ship missile cells flush in the bow deck (`Part_gun`, `.001`, `.002` with `Mount_gun*`: the parent's
main guns), the VLS block (`Part_vls`), the two SAM box launchers on sponsons (`Part_sec_f` > `Mount_gun.003`,
`Part_sec_a` > `Mount_gun.004`), two CIWS on sponsons (`Part_mg`, `Part_mg.001`) and the two gun galleries with
four mounts each (`Part_aa_l` > `Mount_mg.002` .. `.005`, `Part_aa_r` > `Mount_mg.006` .. `.009`); the weak point:
the landing area with four arresting wires, the deck lines and the parked jets, riveted plates one shade off
(`Part_deck`); more jets and a helicopter forward, the deck tractors, the stern boat bay (`Part_welldeck`); railings,
bollards, anchors, life rafts, lights and Kessler's colour bands.

Its own hull: nothing is taken from leviathan, nyx or sea_cruiser. Runtime nodes kept: every `Part_*`, `Mount_*`,
`Muzzle_*` and `Radar` of the old model at its old place; new: `Mount_APS`. Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TAU = math.tau
BOW, STERN = -55.0, 54.8
B = 8.0                          # waterline half beam
FD = 9.0                         # flight deck height


def half_beam(y):
    f = (y - BOW) / (STERN - BOW)
    if f < .3:
        return B * math.sin(min(1.0, f / .3) * R90) ** .75
    return B * (1 - .08 * max(0.0, f - .85) / .15)


def _hull(a):
    hull = a.part('Hull', 'Armor')
    rings = []
    ys = [STERN, 48.0, 36.0, 20.0, 4.0, -12.0, -26.0, -36.0, -44.0, -49.0, -52.5, BOW + .05]
    for y in ys:
        h = max(half_beam(y), .1)
        f = max(0.0, -y / -BOW)
        keel = -3.0 + (2.2 * f ** 3 if y < -36 else 0)
        top = FD - .9
        rings.append([(-h * 1.08, y, top), (-h * 1.04, y, 4.0), (-h, y, .5), (-h * .9, y, -1.8), (-h * .45, y, keel + .3),
                      (0, y, keel), (h * .45, y, keel + .3), (h * .9, y, -1.8), (h, y, .5), (h * 1.04, y, 4.0),
                      (h * 1.08, y, top)])
    rings[-1] = [(p[0] * .04 + math.copysign(.03, p[0]), BOW + (0 if p[2] > 1 else 1.5), p[2]) for p in rings[-1]]
    k.sharp_loft(hull, rings, chamfer=.08)
    # The bulbous bow under the waterline.
    k.lathe(a.part('Hull_low', 'Undercarriage'), [(0, 0), (.9, .6), (1.3, 2.0), (1.2, 4.0), (0, 4.5)], loc=(0, -53.6, -1.6),
            rot=(-R90, 0, 0), seg=10)
    for s in (-1, 1):
        pts = [(s * (max(half_beam(y), .1) + .03), y) for y in ys[1:-1]]
        idx = tuple(range(len(pts) * 2))
        a.part('Hull_low', 'Undercarriage').mesh([(x, y, .3) for x, y in pts] + [(x * .93, y, -1.7) for x, y in reversed(pts)],
                                                  [idx if s < 0 else tuple(reversed(idx))])
        a.part('Boot_top', 'Hazard').mesh([(x * 1.003, y, .55) for x, y in pts] + [(x * 1.003, y, .3) for x, y in reversed(pts)],
                                          [idx if s < 0 else tuple(reversed(idx))])
        seams = a.part('Hull_seams', 'Undercarriage')
        for i, y in enumerate(range(-44, 50, 6)):
            seams.box((.05, .1, 3.5 + .5 * (i % 3)), loc=(s * (half_beam(y) * 1.05 + .02), y, 3.0), bevel=0)
        P.portholes(a, [(s * (half_beam(y) * 1.06 + .02), y, 5.5) for y in range(-40, 48, 8)], (s, 0, 0), r=.3, seg=6)
        a.part('Team_band', 'Team').box((.05, 30.0, 1.0), loc=(s * (B * 1.07 + .03), -20.0, 6.5), bevel=0)
        k.block(a.part('Anchors', 'Undercarriage'), (.1, 1.4, 1.6), loc=(s * (half_beam(-46.0) * 1.07), -46.0, 5.2),
                chamfer=0)


def _flight_deck(a):
    """The overhanging flight deck: the main deck, the angled deck to port, the ski-jump, sponsons, lifts, nets."""
    fd = a.part('Flight_deck', 'Team')
    plan = [(-8.6, -47.0), (-4.0, -53.0), (4.0, -53.0), (9.0, -47.0), (9.4, -10.0), (9.7, 30.0), (9.2, 54.6),
            (-8.0, 54.6), (-9.3, 30.0), (-9.3, -20.0)]
    k.extrude(fd, plan, .9, loc=(0, 0, FD - .45), axis='Z', chamfer=.06, corner=.1)
    # The ski-jump ramp over the bow.
    ramp = a.part('Ski_jump', 'Team')
    ramp.loft([[(-4.0, -53.0, FD), (4.0, -53.0, FD), (4.0, -53.0, FD + 2.2), (-4.0, -53.0, FD + 2.2)],
               [(-6.5, -47.0, FD), (7.0, -47.0, FD), (7.0, -47.0, FD + .9), (-6.5, -47.0, FD + .9)],
               [(-7.5, -41.0, FD), (8.0, -41.0, FD), (8.0, -41.0, FD + .05), (-7.5, -41.0, FD + .05)]])
    # Deck markings: the angled deck's edge lines and centre line, the bow runways, the lift outlines.
    lines = a.part('Deck_lines', 'SafetyStripe')
    white = a.part('Deck_marks', 'Medical')
    ang = math.radians(8)
    for dx in (-4.2, 0.0, 4.2):
        p0 = Vector((dx + 2.0, 52.0, FD + .02))
        d = Vector((-math.sin(ang), -1, 0)).normalized()
        L = 50.0
        c = p0 + d * L / 2
        (white if dx == 0 else lines).box((.25 if dx == 0 else .35, L, .02), loc=tuple(c), rot=(0, 0, ang), bevel=0)
    for x in (-2.5, 2.5):
        white.box((.25, 30.0, .02), loc=(x, -25.0, FD + .02), bevel=0)
    for i in range(10):
        white.box((1.6, .4, .02), loc=(0, -38.0 + i * 3.0, FD + .02), bevel=0)
    # Three deck-edge lifts (their outlines and platforms), the deck-edge sponsons.
    for x, y in ((9.2, -2.0), (9.2, 22.0), (-9.4, 38.0)):
        s = 1 if x > 0 else -1
        k.block(a.part('Lifts', 'Armor'), (3.4, 6.0, .3), loc=(s * 8.2, y, FD - .1), chamfer=.04)
        a.part('Lift_edges', 'Hazard').box((3.4, .2, .02), loc=(s * 8.2, y - 3.0, FD + .21), bevel=0)
        a.part('Lift_edges', 'Hazard').box((.2, 6.0, .02), loc=(s * 6.5, y, FD + .21), bevel=0)
    for x, y, w, d in ((8.6, -15.5, 3.5, 4.0), (-8.6, -33.0, 3.0, 4.0), (8.6, 47.0, 3.0, 4.0), (-8.8, 51.5, 3.0, 3.6)):
        s = 1 if x > 0 else -1
        k.block(a.part('Sponsons', 'Armor'), (w, d, .5), loc=(s * (10.0 - w / 2), y, FD - 1.8), chamfer=.06)
        a.part('Sponsons', 'Armor').limb((s * 7.5, y, 4.0), (s * (9.8 - w / 2), y, FD - 1.6), .6, .6, bevel=0)
    # Catwalks and safety nets along the deck edges, deck lights.
    nets = a.part('Deck_nets', 'Steel')
    for s in (-1, 1):
        for i in range(28):
            y = -44.0 + i * 3.5
            if (s > 0 and -6 < y < 26) or (s < 0 and 34 < y < 42):
                continue
            nets.box((.6, 3.3, .04), loc=(s * 9.75, y, FD - .4), rot=(0, s * -.3, 0), bevel=0)
        for i in range(10):
            a.part('Deck_lights', 'Lamp').box((.3, .3, .1), loc=(s * 8.6, -40.0 + i * 10.0, FD + .05), bevel=0)


def _island(a):
    """The island to starboard: stepped blocks, the bridge windows, the mast with the radar, the funnel."""
    isl = a.part('Island', 'Team')
    x0 = -7.4
    for (y0, y1, za, zb, w0, w1) in ((-8.0, 9.0, FD, 13.0, 3.2, 3.0), (-6.5, 6.5, 13.0, 15.4, 2.8, 2.6),
                                     (-5.0, 1.5, 15.4, 17.2, 2.4, 2.2)):
        rings = [[(x0 - w0 / 2, y0, za), (x0 + w0 / 2, y0, za), (x0 + w0 / 2, y1, za), (x0 - w0 / 2, y1, za)],
                 [(x0 - w1 / 2, y0 + .3, zb), (x0 + w1 / 2, y0 + .3, zb), (x0 + w1 / 2, y1, zb), (x0 - w1 / 2, y1, zb)]]
        k.sharp_loft(isl, rings, chamfer=.08)
    glass = a.part('Bridge_glass', 'Glass')
    for z, y in ((14.5, -6.25), (16.5, -4.75)):
        for i in range(5):
            glass.box((.4, .06, .5), loc=(x0 - 1.0 + i * .5, y - .02, z), bevel=0)
    for z in (11.0, 14.3):
        for i in range(6):
            glass.box((.06, .9, .5), loc=(x0 + 1.52, -6.0 + i * 2.2, z), bevel=0)
    faces = a.part('Array_faces', 'Glass')
    for nx, ny in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        faces.box((1.8, 1.8, .06), loc=(x0 + nx * 1.22, -1.5 + ny * 3.3 if ny else -1.5, 16.2), rot=K.rot_to((nx, ny, .25)),
                  bevel=0)
    a.pivot('Mount_APS', (x0, -1.5, 16.8))
    # The main mast with yards and the spinning search radar (`Part_radar` > `Radar`).
    mast = a.part('Mast', 'Steel')
    mast.cyl(.3, 2.0, loc=(x0, -3.0, 17.2 + 1.0), seg=8, bevel=0)
    mast.box((4.6, .3, .3), loc=(x0, -3.0, 17.8), bevel=0)
    for dx in (-2.1, 2.1):
        mast.cyl(.08, 1.2, loc=(x0 + dx, -3.0, 18.4), seg=6, bevel=0)
    a.pivot('Part_radar', (x0, -3.0, 18.4))
    r = a.pivot('Radar', (0, 0, 1.1), 'Part_radar')
    k.block(a.part('Radar_array', 'Armor', r), (4.6, .45, 1.1), loc=(0, 0, -.1), chamfer=.08)
    a.part('Radar_face', 'Undercarriage', r).box((4.3, .04, .9), loc=(0, -.25, .45), bevel=0)
    K.tone(a, 'Part_radar', k=.9)
    # The funnel aft on the island (`Part_engine`), its caps and soot.
    a.pivot('Part_engine', (x0, 4.6, 15.3))
    fn = a.part('Funnel', 'Team', 'Part_engine')
    k.extrude(fn, [(-1.3, -2.0), (1.3, -2.0), (1.1, 2.2), (-1.1, 2.2)], 3.0, loc=(0, 0, .2), axis='Z', chamfer=.06,
              taper=(.85, .9))
    for dy in (-.8, .8):
        a.part('Funnel_caps', 'Steel', 'Part_engine').cyl(.5, .6, loc=(0, dy, 1.9), seg=10, bevel=0)
    K.tone(a, 'Part_engine', k=.88)
    K.soot(a, (x0, 4.6, 17.4), radius=3.0, k=.55)
    for i in range(3):
        K.whip_antenna(a.part('Antennas', 'Steel'), (x0 + (i - 1) * 1.0, 7.5, 15.4), h=3.0, r=.08, lean=.05)


def _cells(a):
    """Three heavy missile cells flush in the bow deck (`Part_gun*` > `Mount_gun*`), the VLS block (`Part_vls`)."""
    for i, (x, y) in enumerate(((0.0, -30.0), (0.0, -19.5), (-5.4, 30.0))):
        part = K.name('Part_gun', i)
        a.pivot(part, (x, y, 9.0))
        m = a.pivot(K.name('Mount_gun', i), (0, 0, .2), part)
        sfx = '' if i == 0 else f'_{i:03d}'
        k.block(a.part('Cell_plate' + sfx, 'Armor', m), (3.6, 3.2, .25), loc=(0, .2, -.2), chamfer=.05)
        lids = a.part('Cell_lids' + sfx, 'Steel', m)
        for cx in (-.9, .9):
            for cy in (-.6, .9):
                lids.box((1.4, 1.2, .08), loc=(cx, cy, .1), bevel=0)
        a.part('Cell_bands' + sfx, 'BarrelRed', m).box((3.4, .15, .02), loc=(0, -1.25, .12), bevel=0)
        a.pivot(K.name('Muzzle_gun', i), (0, -1.2, .3), m)
        K.tone(a, part, k=.88)
    p = a.pivot('Part_vls', (-4.6, 11.0, 9.0))
    K.vls(a, (0, 0, .05), 6, 4, cell=1.0, parent=p)
    K.tone(a, 'Part_vls', k=.88)


def _sam_boxes(a):
    for part, mount, muzzle, at in (('Part_sec_f', K.name('Mount_gun', 3), K.name('Muzzle_gun', 3), (-7.6, -33.0, 7.4)),
                                    ('Part_sec_a', K.name('Mount_gun', 4), K.name('Muzzle_gun', 4), (7.6, 47.0, 7.4))):
        a.pivot(part, at)
        m = a.pivot(mount, (0, 0, 0), part)
        sfx = '_f' if part.endswith('f') else '_a'
        k.lathe(a.part('Sam_base' + sfx, 'Steel', m), [(1.0, 0), (1.0, .2), (.8, .3), (0, .3)], seg=12)
        k.block(a.part('Sam_box' + sfx, 'Armor', m), (1.8, 2.2, 1.3), loc=(0, .1, .3), chamfer=.08)
        cells = a.part('Sam_cells' + sfx, 'Undercarriage', m)
        for cx in (-.45, .45):
            for cz in (.65, 1.25):
                cells.box((.7, .04, .5), loc=(cx, -1.02, cz), bevel=0)
        a.pivot(muzzle, (0, -1.25, .95), m)
        K.tone(a, part, k=.9)


def _ciws(a, mount, muzzle, at, parent, sfx, short=False):
    """A CIWS / gun gallery mount on its own pivot: ring, house, six barrels (or a twin 30 mm), the muzzle."""
    m = a.pivot(mount, at, parent)
    k.lathe(a.part('CIWS_ring' + sfx, 'Steel', m), [(.8, -.2), (.8, .1), (.7, .2), (0, .2)], seg=12)
    k.extrude(a.part('CIWS_body' + sfx, 'Team', m), [(-.6, 0), (.6, 0), (.5, .75), (.1, .9), (-.1, .9), (-.5, .75)],
              1.4, loc=(0, .25, .15), axis='Y', chamfer=.05, corner=.03)
    bar = a.part('CIWS_barrels' + sfx, 'Steel', m)
    if short:
        for x in (-.18, .18):
            bar.cyl(.05, 1.6, loc=(x, -1.4, .26), rot=K.FORWARD, seg=6, bevel=0)
        a.pivot(muzzle, (0, -2.25, .26), m)
    else:
        for i in range(6):
            u = i * TAU / 6
            bar.cyl(.028, 1.8, loc=(math.cos(u) * .09, -1.4, .62 + math.sin(u) * .09), rot=K.FORWARD, seg=5, bevel=0)
        a.part('CIWS_bores' + sfx, 'Undercarriage', m).cyl(.16, .08, loc=(0, -2.3, .62), rot=K.FORWARD, seg=10, bevel=0)
    return m


def _guns(a):
    for part, at, mount_at, sfx in (('Part_mg', (-8.0, -15.5, 9.0), (0, 0, .2), '_mg'),
                                    (K.name('Part_mg', 1), (7.4, 51.5, 9.0), (0, 0, .2), '_mg_001')):
        a.pivot(part, at)
        mount = 'Mount_mg' if part == 'Part_mg' else K.name('Mount_mg', 1)
        muzzle = 'Muzzle_mg' if part == 'Part_mg' else K.name('Muzzle_mg', 1)
        m = _ciws(a, mount, muzzle, mount_at, part, sfx)
        a.pivot(muzzle, (0, -2.77, .62), m)
        K.tone(a, part, k=.9)
    # The two gun galleries: four mounts each on a long sponson (port forward, starboard aft).
    for part, at, s, idx in (('Part_aa_l', (7.9, 4.0, 6.8), 1, (2, 3, 4, 5)), ('Part_aa_r', (-7.9, 24.0, 6.8), -1, (6, 7, 8, 9))):
        p = a.pivot(part, at)
        k.block(a.part('Gallery' + part[-2:], 'Armor', p), (2.4, 13.0, .4), loc=(s * .3, 0, -.5), chamfer=.06)
        for gy in (-4.0, 4.0):
            a.part('Gallery' + part[-2:], 'Armor', p).limb((-s * 1.0, gy, -2.5), (s * .4, gy, -.4), .5, .5, bevel=0)
        for j, i in enumerate(idx):
            y = -5.4 + j * 3.6
            mount = K.name('Mount_mg', i)
            muzzle = K.name('Muzzle_mg', i)
            short = j in (1, 2)
            local = (s * .2, y, 0)
            m = _ciws(a, mount, muzzle, local, part, f'_mg_{i:03d}', short=short)
            if not short:
                a.pivot(muzzle, (0, -2.47, .62), m)
        K.tone(a, part, k=.9)


def _deck_weakpoint(a):
    """The landing area (`Part_deck`): arresting wires, riveted plates one shade off, parked jets."""
    p = a.pivot('Part_deck', (2.2, 40.0, 9.0))
    plates = a.part('Deck_plates', 'Team', p)
    rivets = a.part('Kit_rivets', 'Steel', p)
    for i in range(3):
        for j in range(2):
            x, y = -2.8 + j * 5.6, -6.0 + i * 6.0
            k.block(plates, (5.0, 5.4, .08), loc=(x, y, .02), chamfer=.02)
            for dx in (-2.2, 2.2):
                for dy in (-2.4, 2.4):
                    rivets.box((.12, .12, .06), loc=(x + dx, y + dy, .1), bevel=0)
    wires = a.part('Arresting_wires', 'Steel', p)
    for i in range(4):
        wires.box((12.0, .1, .06), loc=(-.5, -8.0 + i * 2.2, .1), rot=(0, 0, math.radians(8)), bevel=0)
    K.tone(a, 'Part_deck', k=.86)
    for j, (x, y, yaw) in enumerate(((-2.5, 3.0, .15), (2.5, 4.5, .15), (1.5, 10.5, 1.4))):
        _jet(a, (x, y, .08), yaw, f'_d{j}', parent=p)


def _jet(a, loc, yaw, tag, parent=None):
    """A parked jet: fuselage, wings, twin fins, canopy (a simple 1.3 x scale fighter, folded on the deck)."""
    x, y, z = loc
    c, s = math.cos(yaw), math.sin(yaw)

    def at(px, py, pz):
        return (x + px * c - py * s, y + px * s + py * c, z + pz)
    body = a.part('Jets', 'Armor', parent)
    body.loft([[at(0, -4.2, .9)], [at(-.5, -2.5, .7), at(.5, -2.5, .7), at(.5, -2.5, 1.3), at(-.5, -2.5, 1.3)],
               [at(-.8, 2.5, .6), at(.8, 2.5, .6), at(.8, 2.5, 1.2), at(-.8, 2.5, 1.2)],
               [at(-.6, 4.0, .7), at(.6, 4.0, .7), at(.6, 4.0, 1.1), at(-.6, 4.0, 1.1)]])
    wings = a.part('Jet_wings', 'Team', parent)
    wings.mesh([at(-.8, -.5, .9), at(-4.0, 2.3, .9), at(-4.0, 3.2, .9), at(-.8, 3.0, .9)], [(0, 1, 2, 3)])
    wings.mesh([at(.8, -.5, .9), at(.8, 3.0, .9), at(4.0, 3.2, .9), at(4.0, 2.3, .9)], [(0, 1, 2, 3)])
    for fx in (-.55, .55):
        wings.mesh([at(fx, 2.4, 1.2), at(fx, 4.0, 1.2), at(fx * 1.3, 4.2, 3.0), at(fx * 1.2, 3.6, 3.0)], [(0, 1, 2, 3)])
        wings.mesh([at(fx, 2.4, 1.2), at(fx * 1.2, 3.6, 3.0), at(fx * 1.3, 4.2, 3.0), at(fx, 4.0, 1.2)], [(0, 1, 2, 3)])
    a.part('Jet_canopies', 'Glass', parent).box((.5, 1.4, .35), loc=at(0, -2.0, 1.45), rot=(0, 0, yaw), bevel=0)


def _forward_and_stern(a):
    for j, (x, y, yaw) in enumerate(((-5.5, -12.0, -.4), (-5.5, -6.0, -.4), (-5.0, 15.0, .2), (5.0, 15.0, -.2),
                                     (2.0, -40.0, 0.0))):
        _jet(a, (x, y, FD + .02), yaw, f'_f{j}')
    # A helicopter forward of the island, deck tractors, fuel carts.
    hx, hy = -3.0, -24.0
    k.block(a.part('Helicopter', 'Armor'), (1.6, 5.0, 1.8), loc=(hx, hy, FD + .3), chamfer=.4)
    a.part('Helicopter', 'Armor').box((.4, 4.0, .4), loc=(hx, hy + 4.2, FD + 1.6), bevel=0)
    rot = a.part('Heli_rotors', 'Undercarriage')
    for u in (0, R90, .8, 2.4):
        rot.box((9.0, .3, .06), loc=(hx, hy, FD + 2.3), rot=(0, 0, u), bevel=0)
    P.clutter(a, 'Deck_tractors', 'CraneYellow', -6.0, 6.0, 0.0, 8.0, FD, 6, seed=81, size=(1.2, 2.4), height=(.6, 1.2),
              gap=1.0)
    P.clutter(a, 'Deck_carts', 'Hazard', -6.5, 2.0, -44.0, -36.0, FD, 6, seed=82, size=(.8, 1.6), height=(.4, .9),
              gap=.8)
    # The stern boat bay (`Part_welldeck`): the open transom gate, a boat inside.
    p = a.pivot('Part_welldeck', (0, 54.4, 2.6))
    k.block(a.part('Bay_frame', 'Armor', p), (7.0, .6, 3.6), loc=(0, .1, -1.8), chamfer=.06)
    a.part('Bay_dark', 'Undercarriage', p).box((5.6, .05, 2.8), loc=(0, .42, -.1), bevel=0)
    K.rhib(a.part('Boats', 'Armor', p), a.part('Boat_tubes', 'Rubber', p), (0, -1.5, -1.6), length=5.0, beam=2.0)
    K.tone(a, 'Part_welldeck', k=.88)


def _fittings(a):
    for s in (-1, 1):
        K.railing(a.part('Railings', 'Steel'), [(s * 9.0, y, FD - .9) for y in (-40.0, -20.0, 0.0, 20.0, 40.0)], h=1.0,
                  post=3.0, r=.05)
        for y in (-30.0, -10.0, 10.0, 30.0):
            for i in range(3):
                k.lathe(a.part('Life_rafts', 'Medical'), [(.45, -.8), (.5, -.7), (.5, .7), (.45, .8)],
                        loc=(s * (half_beam(y) * 1.08 + .25), y + i * 1.8, 7.2), rot=K.FORWARD, seg=6)
        bol = a.part('Bollards', 'Steel')
        for y in (-48.0, -44.0, 50.0):
            for dy in (-.4, .4):
                bol.cyl(.3, .7, loc=(s * 5.0, y + dy, FD + .35 if y < 0 else FD + .35), seg=8, bevel=0)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.4, .4, .4), loc=(s * 9.6, -30.0, FD + .2),
                                                                          bevel=0)
    P.clutter(a, 'Island_fittings', 'Steel', -8.9, -6.0, -7.5, 8.5, FD, 10, seed=83, size=(.5, 1.6), height=(.4, 1.6),
              gap=.5)
    P.clutter(a, 'Hangar_fittings', 'Steel', -6.0, 6.0, 44.0, 53.0, FD, 8, seed=84, size=(.6, 1.8), height=(.3, .9),
              gap=.8)


def kraken(a):
    """Kraken: see the module docstring."""
    K.suffixed(a)
    _hull(a)
    _flight_deck(a)
    _island(a)
    _cells(a)
    _sam_boxes(a)
    _guns(a)
    _deck_weakpoint(a)
    _forward_and_stern(a)
    _fittings(a)
    k.clean(a)


BUILDERS = {
    'kraken': (kraken, dict(ao_distance=3.0, grime_height=.5)),
}
