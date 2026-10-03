"""Prompt 35 wave 4 (lane C): Moloch, Varga's chapter 6 mobile factory boss, rebuilt from scratch
(spec: Tools/blender/specs/moloch.json).

A tracked mobile factory after the sheet's references (the Fatboy of Supreme Commander, the C&C war factory / MCV;
26.5 x 14.4 x 12.1 m like the old file, which the game scales by the def's size 1.51): two huge track units under
riveted guard plates (`Part_track_l` / `_r`, the card's "break the tracks and it slows down"); the hull between
them with the sloped prow and the dozer bar; the armoured command bridge at the front; the factory hall with its
sloped walls, the sawtooth roof with skylights, the gantry crane, the vents and the smokestacks; the four twin
120 mm turrets: two on the forward sponsons (`Turret`, `Mount_gun`), two on the raised rear gun deck
(`Mount_gun.001` / `.002`); the twin 35 mm flak mount on the roof (`Mount_mg`); the two factory doors in the stern
with their ramp, hazard frames and warning lamps (`Part_door_l` / `_r`: the card's weak side, armour 2 at the rear);
stacked supply crates, drums, ladders and railings; the owner general's colour band round the hall.

The turrets model both barrels; mb_fix_barrels adds their per-barrel muzzles (moloch moved to its EXTRA list).
Runtime nodes kept: `Turret`, `Mount_gun` (+ `.001`, `.002`), `Mount_mg`, `Muzzle_main`, `Muzzle_gun` (+ `.001`, `.002`),
`Muzzle_mg`, `Part_track_l`, `Part_track_r`, `Part_door_l`, `Part_door_r` (the wrapper adds `Muzzle_b1_*` / `_b2_*`).
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C
import mb_vehicles as mv

R90 = math.pi / 2
TX, TW = 5.9, 2.5
DECK = 3.7
HALL_TOP = 8.6
WHEELS = (-9.4, -7.05, -4.7, -2.35, 0.0, 2.35, 4.7, 7.05, 9.4)
WR = .95


def _track(a, s):
    """One track unit on its Part_track pivot: the belt, links, road wheels with hubs, sprocket, idler, rollers,
    the riveted guard plates over the top run, the side bogie frame."""
    node = 'Part_track_l' if s > 0 else 'Part_track_r'
    p = a.pivot(node, (s * TX, 0, 0))
    belt = a.part('Tracks', 'Undercarriage', p)
    links = a.part('Track_links', 'Undercarriage', p)
    sp, ip = (11.2, 1.6, 1.25), (-11.3, 1.5, 1.15)
    pts = []
    for cy, cz, r in ((sp[0], sp[1], sp[2] + .1), (ip[0], ip[1], ip[2] + .1)) + tuple((y, WR, WR + .1) for y in WHEELS):
        for i in range(24):
            u = i * math.tau / 24
            pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
    outline = mv._hull2d(pts)
    k.extrude(belt, outline, TW, axis='X', chamfer=0)
    for (py, pz), (ty, tz) in mv._perimeter(outline, .55, 0.0):
        if pz > 2.4 and -10.5 < py < 10.5:
            continue                                       # the guard plates hide the top run
        ny, nz = tz, -ty
        k.block(links, (TW + .08, .22, .12), loc=(0, py + ny * .04, pz + nz * .04), rot=(math.atan2(tz, ty), 0, 0),
                chamfer=0)
    xo = s * (TW / 2 - .3)
    wheels = a.part('Wheels', 'Armor', p)
    tyres = a.part('Tyres', 'Undercarriage', p)
    hubs = a.part('Hubs', 'Steel', p)
    rot = (0, s * R90, 0)
    for y in WHEELS:
        k.lathe(tyres, [(WR * .8, -.35), (WR, -.3), (WR, .3), (WR * .8, .35)], loc=(xo, y, WR), rot=rot, seg=12,
                worn=(1, 2))
        k.lathe(wheels, [(0, .42), (WR * .3, .42), (WR * .55, .36), (WR * .75, .38), (WR * .8, .3)], loc=(xo, y, WR),
                rot=rot, seg=12, worn=(3,))
        for j in range(4):
            u = j * math.tau / 4 + .4
            hubs.cyl(.06, .06, loc=(xo + s * .44, y + math.cos(u) * WR * .4, WR + math.sin(u) * WR * .4), rot=rot,
                     seg=6, bevel=0)
    # The toothed sprocket at the rear, the idler at the front, return rollers.
    sy, sz, sr = sp
    outline_s = []
    for i in range(14):
        u = i * math.tau / 14
        for du, rr in ((-.15, sr * .86), (-.06, sr * 1.05), (.06, sr * 1.05), (.15, sr * .86)):
            outline_s.append((math.cos(u + du) * rr, math.sin(u + du) * rr))
    k.extrude(a.part('Sprockets', 'Armor', p), outline_s, .5, loc=(xo, sy, sz), axis='X', chamfer=.03)
    iy, iz, ir = ip
    k.lathe(a.part('Idlers', 'Armor', p), [(0, .4), (ir * .4, .4), (ir * .5, .3), (ir * .9, .3), (ir, .15),
                                           (ir, -.35), (0, -.35)], loc=(xo, iy, iz), rot=rot, seg=16, worn=(4,))
    for y in (-6.0, 0.0, 6.0):
        k.lathe(a.part('Rollers', 'Undercarriage', p), [(.25, -.25), (.3, -.2), (.3, .2), (.25, .25)],
                loc=(xo, y, 2.45), rot=rot, seg=10)
    # The bogie frame along the outside, the guard plates over the top run (riveted, the breakable look), the
    # mud flaps.
    fr = a.part('Track_frame', 'Armor', p)
    k.block(fr, (.3, 19.5, .5), loc=(s * (TW / 2 + .02), 0, 1.1), chamfer=.05)
    for j in range(5):
        y = -9.2 + j * 4.6
        K.armour_plate(a, a.part('Skirts', 'Team', p), (1.3, 4.4, .12), (s * (TW / 2 + .12), y, 2.65),
                       rot=(0, s * R90, 0), rivet=.9, parent=p)
    K.tone(a, node, k=.9)
    K.dust(a, (s * TX, 0, .3), radius=8.0, k=.35)


def _hull(a):
    hull = a.part('Hull', 'Team')
    # The hull between and over the tracks: the sloped prow, the sides, the sponson deck.
    C.section_loft(hull, [
        (-13.2, [(0, 1.3), (3.2, 1.3), (3.4, 1.9), (3.2, 2.3), (0, 2.3)]),
        (-12.0, [(0, .9), (4.4, .9), (4.6, 2.4), (6.4, 3.1), (0, 3.3)]),
        (-10.6, [(0, .8), (4.6, .8), (4.7, 2.6), (7.15, DECK - .1), (0, DECK)]),
        (11.0, [(0, .8), (4.6, .8), (4.7, 2.6), (7.15, DECK - .1), (0, DECK)]),
        (12.6, [(0, 1.0), (4.4, 1.0), (4.5, 2.5), (6.8, DECK - .3), (0, DECK - .2)]),
    ])
    # The dozer bar across the prow, the floodlights, tow eyes.
    bar = a.part('Dozer_bar', 'Steel')
    k.block(bar, (8.4, .5, .7), loc=(0, -13.4, .9), chamfer=.08)
    for x in (-3.0, 3.0):
        bar.limb((x, -13.2, 1.3), (x, -12.0, 2.0), .18, .18, bevel=0)
    for x in (-2.0, 2.0):
        K.floodlight(a, (x, -12.6, 2.6), facing=(0, -1, -.2), pole=.6)
    # Deck plating seams and rivet rows along the sponsons, the general's colour band round the hull.
    rv = a.part('Kit_rivets', 'Steel')
    for s in (-1, 1):
        K.rivet_line(rv, (s * 7.1, -10.2, DECK - .15), (s * 7.1, 10.8, DECK - .15), (s, 0, 0), pitch=1.0, r=.06)
        a.part('Team_band', 'TeamGlow').box((.03, 21.0, .25), loc=(s * 7.17, .3, DECK - .45), bevel=0)
    K.dust(a, (0, -12.5, 1.0), radius=4.0, k=.25)


def _bridge(a):
    """The armoured command bridge at the front of the hall: sloped walls, the vision slit band, the roof sensors."""
    br = a.part('Bridge', 'Team')
    C.slab_loft(br, [(-1.5, -9.6), (2.5, -9.6), (2.6, -5.6), (-1.8, -5.6)], [(-1.0, -9.0), (2.0, -9.0), (2.1, -5.8),
                                                                            (-1.3, -5.8)], DECK, 7.2)
    gl = a.part('Glass', 'Glass')
    gl.box((2.8, .05, .35), loc=(.5, -9.32, 6.2), rot=(-.18, 0, 0), bevel=0)
    for s in (-1, 1):
        gl.box((.05, 1.6, .3), loc=(2.3 if s > 0 else -1.55, -7.6, 6.2), rot=(0, s * -.1, 0), bevel=0)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (1.0, -7.0, 7.2), w=.8, h=.8, normal=(0, -1, 0), bars=4)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-1.4, -6.4, 7.2), h=2.0)
    k.block(a.part('Bridge_roof', 'Armor'), (3.4, 3.4, .25), loc=(.4, -7.4, 7.2), chamfer=.06)
    K.dish(a.part('Antennas', 'Steel'), a.part('Kit_steel', 'Steel'), (-.8, -8.0, 7.75), r=.5, normal=(0, -1, .5))


def _hall(a):
    """The factory hall: sloped walls, wide rear gun deck, sawtooth roof with skylights, vents, crane, stacks."""
    hall = a.part('Body', 'Team')
    C.slab_loft(hall, [(-3.1, -5.4), (3.1, -5.4), (3.3, 10.8), (-3.3, 10.8)], [(-2.7, -4.9), (2.7, -4.9), (2.9, 10.4),
                                                                              (-2.9, 10.4)], DECK, HALL_TOP)
    # The raised rear gun deck either side of the hall carrying the rear turrets.
    for s in (-1, 1):
        gd = a.part('Gun_deck', 'Armor')
        C.slab_loft(gd, [(s * 2.9, 2.2), (s * 6.0, 2.6), (s * 6.0, 7.0), (s * 2.9, 7.2)],
                    [(s * 2.8, 2.6), (s * 5.6, 2.9), (s * 5.6, 6.6), (s * 2.8, 6.8)], DECK, HALL_TOP - .05)
        K.armour_plate(a, a.part('Hull_plates', 'Armor'), (2.6, 3.6, .15), (s * 5.85, 4.8, 6.0), rot=(0, s * R90, 0),
                       rivet=.9)
    # Wall panels with rivets, the general's band.
    for s in (-1, 1):
        for y in (-3.0, .5, 8.8):
            K.armour_plate(a, a.part('Hull_plates', 'Armor'), (2.4, 2.6, .15), (s * 3.15, y, 5.4), rot=(0, s * R90, 0),
                           rivet=.9)
        a.part('Team_band', 'TeamGlow').box((.03, 16.5, .3), loc=(s * 2.95, 2.8, 7.6), rot=(0, s * .03, 0), bevel=0)
    # The sawtooth roof: four bays, each with a sloped glazed face towards the rear.
    roof = a.part('Roof', 'Armor')
    sky = a.part('Skylights', 'Glass')
    for y0 in (-4.6, .6, 3.6, 6.6):
        k.extrude(roof, [(y0, HALL_TOP), (y0 + 2.3, HALL_TOP + .6), (y0 + 2.6, HALL_TOP + .6), (y0 + 2.7, HALL_TOP)],
                  5.0, axis='X', chamfer=.03)
        sky.mesh([(-2.4, y0 + 2.62, HALL_TOP + .56), (2.4, y0 + 2.62, HALL_TOP + .56), (2.4, y0 + 2.7, HALL_TOP + .06),
                  (-2.4, y0 + 2.7, HALL_TOP + .06)], [(0, 1, 2, 3)])
    # Vents along the roof edge, the gantry crane on its rails, the smokestacks at the rear.
    for y in (-1.6, .1):
        K.grille(a, (1.9, y, HALL_TOP + .02), .7, .5, facing=(0, 0, 1), slats=4, frame_mat='Armor')
    rails = a.part('Crane', 'CraneYellow')
    for x in (-2.55, 2.55):
        rails.box((.18, 9.0, .18), loc=(x, 5.5, HALL_TOP + .95), bevel=0)
        for y in (1.5, 5.5, 9.5):
            rails.box((.14, .14, .9), loc=(x, y, HALL_TOP + .45), bevel=0)
    k.block(rails, (5.4, .45, .45), loc=(0, 5.0, HALL_TOP + 1.04), chamfer=.04)
    k.block(rails, (.8, .8, .6), loc=(1.2, 5.0, HALL_TOP + .6), chamfer=.05)
    a.part('Kit_steel', 'Steel').cyl(.04, 1.4, loc=(1.2, 5.0, HALL_TOP + .2), seg=6, bevel=0)
    for x, h in ((-1.9, 3.2), (-.6, 2.6)):
        K.smokestack(a, (x, 9.2, HALL_TOP), r=.45, h=h)
    k.block(a.part('Hull_plates', 'Armor'), (1.4, 1.6, 1.0), loc=(1.4, 9.0, HALL_TOP), chamfer=.08)   # the AC plant
    K.grille(a, (1.4, 9.0, HALL_TOP + 1.02), 1.1, 1.2, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    a.pivot('Point_exhaust', (-1.9, 9.2, HALL_TOP + 3.2))
    a.pivot('Point_fire', (0, 3.0, HALL_TOP + .5))
    # Railings round the roof, ladders up the hall's side, a floodlight at each corner.
    K.railing(a.part('Railings', 'Steel'), [(-2.6, -4.8, HALL_TOP), (2.6, -4.8, HALL_TOP), (2.6, 10.2, HALL_TOP),
                                            (-2.6, 10.2, HALL_TOP), (-2.6, -4.8, HALL_TOP)], h=.9, post=2.0)
    for s in (-1, 1):
        K.ladder(a.part('Ladders', 'Steel'), (s * 3.35, -1.0, DECK), (s * 3.0, -1.0, HALL_TOP), width=.6)
        K.floodlight(a, (s * 2.5, 10.1, HALL_TOP), facing=(0, 1, -.3), pole=1.2)


def _stern(a):
    """The two factory doors (Part_door_l / _r) in the stern, the ramp, hazard frames and warning lamps."""
    fr = a.part('Hangar_frame', 'Armor')
    k.block(fr, (8.4, .6, .6), loc=(0, 11.05, 4.0), chamfer=.06)
    for x in (-4.0, 0.0, 4.0):
        k.block(fr, (.6, .6, 3.4), loc=(x, 11.05, .6), chamfer=.06)
    hz = a.part('Hazard_frames', 'Hazard')
    for s in (-1, 1):
        door = a.pivot('Part_door_l' if s > 0 else 'Part_door_r', (s * 2.0, 11.3, 1.9))
        dp = a.part('Doors', 'Steel', door)
        k.block(dp, (3.2, .2, 3.2), loc=(0, 0, -1.2), chamfer=.04)
        for z in (-.6, .2, 1.0):
            dp.box((3.1, .06, .1), loc=(0, .12, z), bevel=0)
        a.part('Door_stripes', 'Hazard', door).box((3.2, .05, .25), loc=(0, .13, -1.05), bevel=0)
        K.tone(a, 'Part_door_l' if s > 0 else 'Part_door_r', k=.85)
        hz.box((.12, .1, 3.4), loc=(s * 3.65, 11.4, 2.2), bevel=0)
        K.beacon(a, (s * 3.6, 11.4, 4.4), r=.18)
    # The ramp, the stern plates with rivets, the tail lamps.
    rp = a.part('Ramp', 'Armor')
    k.extrude(rp, [(11.0, .6), (12.9, .05), (12.9, .2), (11.0, .8)], 7.6, axis='X', chamfer=.04)
    for x in (-6.0, 6.0):
        a.part('Tail_lamps', 'LavaGlow').box((.5, .05, .25), loc=(x, 12.7, 2.6), bevel=0)


def _turret(a, pivot, loc, muzzle, parent=None):
    """A twin 120 mm turret on its pivot: the ring and barbette, the sloped house, the mantlet, two barrels with
    bore evacuators and muzzle brakes, the commander's cupola and a periscope."""
    x, y, z = loc
    k.lathe(a.part('Barbettes', 'Armor'), [(1.75, z - 1.1), (1.75, z - .05), (1.6, z), (1.5, z)], loc=(x, y, 0),
            seg=18, worn=(2,))
    t = a.pivot(pivot, loc, parent)
    tag = pivot.replace('Mount_gun', 'g').replace('__', '').replace('.', '')
    house = a.part(f'Turret_house{tag}', 'Team', t)
    C.slab_loft(house, [(-1.3, -1.9), (1.3, -1.9), (1.7, -1.2), (1.7, 1.6), (1.3, 2.0), (-1.3, 2.0), (-1.7, 1.6),
                        (-1.7, -1.2)],
                [(-1.0, -1.5), (1.0, -1.5), (1.4, -1.0), (1.45, 1.45), (1.1, 1.8), (-1.1, 1.8), (-1.45, 1.45),
                 (-1.4, -1.0)], 0, 1.35)
    man = a.part(f'Mantlet{tag}', 'Armor', t)
    k.extrude(man, [(-.35, -.4), (.25, -.45), (.35, .45), (-.25, .5)], 1.5, loc=(0, -1.9, .66), axis='X',
              chamfer=.06, corner=.04)
    bar = a.part(f'Barrels{tag}', 'Steel', t)
    for bx in (-.31, .31):
        k.lathe(bar, [(.2, 0), (.2, .3), (.15, .4), (.13, 5.0), (0, 5.0)], loc=(bx, -2.0, .66), rot=K.FORWARD, seg=10,
                worn=(1,))
        k.lathe(bar, [(.14, -.3), (.2, -.2), (.2, .2), (.14, .3)], loc=(bx, -4.2, .66), rot=K.FORWARD, seg=10,
                worn=(1, 2))
        k.lathe(a.part(f'Brakes{tag}', 'Undercarriage', t), [(.13, 0), (.22, .05), (.22, .45), (.16, .5), (0, .5)],
                loc=(bx, -6.95, .66), rot=K.FORWARD, seg=10, worn=(1, 2))
    a.pivot(muzzle, (0, -7.5, .66), t)
    C.hatch(a, (.7, .6, 1.35), r=.4, parent=t, periscope=True)
    K.periscope(a, (-.7, -.4, 1.35), facing=(0, -1, 0), parent=t, size=(.3, .25, .25))
    K.rivet_line(a.part('Kit_rivets', 'Steel', t), (-1.4, -1.0, 1.0), (1.4, -1.0, 1.0), (0, -.5, 1), pitch=.4, r=.05)
    a.part('Team_band', 'TeamGlow', t).box((3.3, .04, .2), loc=(0, 1.97, .6), bevel=0)
    return t


def _flak(a):
    """The twin 35 mm flak mount on the roof (`Mount_mg`)."""
    k.lathe(a.part('Flak_base', 'Armor'), [(1.1, 0), (1.1, .25), (.9, .35)], loc=(0, -1.4, HALL_TOP), seg=16)
    m = a.pivot('Mount_mg', (0, -1.4, HALL_TOP + .35))
    k.extrude(a.part('Flak_house', 'Team', m), [(-.8, 0), (.8, 0), (.7, .9), (-.7, .9)], 1.6, loc=(0, .1, 0), axis='Y',
              chamfer=.05, corner=.05)
    g = a.part('Flak_guns', 'Steel', m)
    for x in (-.45, .45):
        k.lathe(g, [(.09, 0), (.09, .3), (.06, .35), (.05, 2.6), (0, 2.6)], loc=(x, -.8, .55), rot=K.FORWARD, seg=8,
                worn=(1,))
        for j in range(4):
            g.cyl(.075, .05, loc=(x, -1.2 - j * .2, .55), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_mg', (0, -3.55, .55), m)
    k.lathe(a.part('Flak_radar', 'Armor', m), [(0, -.05), (.35, -.03), (.38, .05)], loc=(0, .7, 1.1),
            rot=(R90 * .7, 0, 0), seg=12)


def _stores(a):
    """Supply crates stacked on the forward sponsons, drums, the cable reels."""
    crates = a.part('Crates', 'Crate')
    bands = a.part('Kit_straps', 'Steel')
    for i, (y, n) in enumerate(((-3.5, 2), (-2.2, 1), (-.9, 2), (.4, 1))):
        for j in range(n):
            K.crate(crates, bands, (1.1, 1.1, .7), (5.8, y, DECK + j * .72), rot=(0, 0, .1), bands=1)
    for y in (-3.4, -2.6, -1.8):
        for x in (-5.4, -6.2):
            K.fuel_drum(a.part('Drums', 'Fuel'), bands, (x, y, DECK), r=.35, h=1.0)
    C.cable_reel(a, (-5.6, 9.0, DECK + .5), r=.5, w=.8, axis='Y')
    C.cable_reel(a, (5.6, 9.0, DECK + .5), r=.5, w=.8, axis='Y')


def _details(a):
    """Wall ribs, deck plates, hazard stripes, the pipe runs and the conveyor arm on the right side."""
    rib = a.part('Hall_ribs', 'Armor')
    for s in (-1, 1):
        for y in (-4.4, -2.6, 2.6, 7.2, 10.0):
            rib.box((.2, .3, 4.7), loc=(s * 3.08, y, (DECK + HALL_TOP) / 2), rot=(0, -s * .08, 0), bevel=0)
        rib.box((.18, 15.2, .25), loc=(s * 3.05, 2.7, DECK + 1.2), rot=(0, -s * .08, 0), bevel=0)
    dp = a.part('Deck_plates', 'Armor')
    for s in (-1, 1):
        for y in (7.6, 9.0, 10.3):
            for x in (4.9, 6.2):
                dp.box((1.15, 1.2, .05), loc=(s * x, y, DECK + .02), bevel=0)
    hz = a.part('Hazard_frames', 'Hazard')
    for i in range(7):
        hz.box((.55, .52, .72), loc=(-3.3 + i * 1.1, -13.4, .9), bevel=0)
    # Pipe runs along the left wall from the stacks to the sponson.
    pipes = a.part('Pipes', 'Steel')
    for z in (5.0, 5.5):
        pipes.tube([(3.35, 9.5, z), (3.35, -4.0, z), (4.2, -4.6, DECK + .3)], .14, seg=8)
    # The conveyor arm on the right: a tower on the hall's flank and the inclined belt down to the sponson deck.
    cv = a.part('Conveyor', 'CraneYellow')
    k.block(cv, (1.4, 1.6, 6.6), loc=(-3.6, -2.4, DECK), chamfer=.06)
    k.extrude(cv, [(-.5, 0), (.5, 0), (.5, .2), (.35, .2), (.35, .45), (-.35, .45), (-.35, .2), (-.5, .2)], 4.2,
              loc=(-5.2, -2.4, 8.0), rot=(0, -.9, 0), axis='X', chamfer=0)
    a.part('Conveyor_belt', 'Undercarriage').box((3.9, .7, .05), loc=(-5.2, -2.4, 8.28), rot=(0, -.9, 0), bevel=0)
    for z in (5.2, 7.0, 9.4):
        K.grille(a, (-4.31, -2.4, z), 1.0, .6, facing=(-1, 0, 0), slats=4, frame_mat='CraneYellow')
    a.part('Kit_steel', 'Steel').limb((-6.6, -2.4, DECK), (-6.4, -2.4, 6.3), .15, .15, bevel=0)
    # The spare-track rack hung on the right sponson's side: brackets, spare links, a tool board.
    rk = a.part('Racks', 'Steel')
    for y in (-.4, 1.8, 4.0):
        rk.box((.7, .12, .12), loc=(-7.45, y, DECK - .2), bevel=0)
        rk.box((.1, .12, 1.2), loc=(-7.75, y, DECK - .8), bevel=0)
    sp = a.part('Spare_track', 'Undercarriage')
    for i in range(12):
        sp.box((.16, .36, .9), loc=(-7.85, -.5 + i * .4, DECK - .75), bevel=0)
    k.block(a.part('Stowage', 'Armor'), (.4, 1.4, .6), loc=(-7.8, 5.0, DECK - 1.2), chamfer=.04)


def moloch(a, detail=False):
    """Moloch, the mobile factory: see the module docstring."""
    K.suffixed(a)
    for s in (-1, 1):
        _track(a, s)
    _hull(a)
    _bridge(a)
    _hall(a)
    _stern(a)
    _turret(a, 'Turret', (4.4, -7.6, 5.0), 'Muzzle_main')
    _turret(a, 'Mount_gun', (-4.4, -7.6, 5.0), 'Muzzle_gun')
    _turret(a, 'Mount_gun__001', (4.4, 4.6, HALL_TOP), 'Muzzle_gun__001')
    _turret(a, 'Mount_gun__002', (-4.4, 4.6, HALL_TOP), 'Muzzle_gun__002')
    _flak(a)
    _stores(a)
    _details(a)
    k.clean(a)


BUILDERS = {
    'moloch': (moloch, dict(ao_distance=1.2, grime_height=1.2)),
}
