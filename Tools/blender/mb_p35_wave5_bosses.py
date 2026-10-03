"""Prompt 35 wave 5 (lane A): the wave's ground and sea bosses rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library. DECISIONS "Prompt 35 wave 5 (lane A)". No hull is shared
with a sibling or with the wave 1 bosses (bastion's casemate on two tracks, hive's crawler platform, inferno's
Object 279 shell, tempest's slab hull).

- monster: the 800 mm self-propelled siege gun (unit_refs: 2B1 Oka 420 mm, Object 271): a long armoured gun
  carriage on four tracked bogie units at its corners, each in its own armoured pod; the huge barrel on a
  slab-sided gun house with recoil cylinders and the shell hoist; twin 100 mm turrets on the front corners, 40 mm
  turrets aft, the 155 mm casemate gun in the glacis, a ZU-23-2 on a balcony each side, the twin Kornet on the rear
  deck, the engine house with its stacks.
- landing_hovercraft: Zubr / LCAC air-cushion landing craft: the buoyancy hull on its black skirt, the cargo deck
  between the two side structures, the bow ramp, the three-tier side superstructures, the two big ducted
  propellers aft, four six-barrel CIWS and the two A-22 rocket launchers (see its section).
- typhon, caspian: see their sections.

Runtime nodes are the old models' (boss parts and mountWeapons in balance.json unchanged).
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau
ACROSS = (0, R90, 0)


def _lift(e):
    """A lathe rotation laying its +Z along the front (-Y) tilted up by e radians."""
    return (R90 - e, 0, 0)


# ============================================================================= monster
M_DECK = 7.2            # the carriage's upper deck


def _monster_track(a, i, x, y):
    """One tracked bogie unit on its Part_track pivot (breakable): the belt round five road wheels, the sprocket and
    the idler, a link every 0.6 m, an armoured pod over its top with a hinged skirt, the bogie strut to the hull."""
    p = a.pivot(K.name('Part_track', i), (x, y, 0))
    s = 1 if x > 0 else -1
    wr, L, tw = 1.0, 9.4, 2.4
    wheels = [-3.4 + j * 1.7 for j in range(5)]
    ends = ((-L / 2 + 1.0, 1.3, .95), (L / 2 - 1.0, 1.35, 1.0))
    pts = []
    for cy, cz, r in ends + tuple((yy, wr, wr + .1) for yy in wheels):
        for jj in range(20):
            u = jj * TAU / 20
            pts.append((cy + r * math.cos(u), cz + r * math.sin(u)))
    import mb_vehicles as mv
    outline = mv._hull2d(pts)
    belt = a.part(f'Track_belt_{i}', 'Undercarriage', p)
    k.extrude(belt, outline, tw, axis='X', chamfer=0)
    for (py, pz), (ty, tz) in mv._perimeter(outline, .6, .0):
        if pz > 2.0:
            continue
        belt.box((tw + .08, .2, .1), loc=(0, py + tz * .04, pz - ty * .04), rot=(math.atan2(tz, ty), 0, 0), bevel=0)
    wh = a.part(f'Track_wheels_{i}', 'Armor', p)
    for yy in wheels:
        for side in (-1, 1):
            k.lathe(wh, [(0, .12), (wr * .55, .12), (wr * .8, .05), (wr * .92, .06), (wr * .92, -.06), (0, -.06)],
                    loc=(side * (tw / 2 - .25), yy, wr), rot=(0, side * R90, 0), seg=12)
    for (cy, cz, r) in ends:
        for side in (-1, 1):
            k.lathe(wh, [(0, .1), (r * .5, .1), (r * .9, .03), (r, .03), (r, -.06), (0, -.06)],
                    loc=(side * (tw / 2 - .2), cy, cz), rot=(0, side * R90, 0), seg=12)
    pod = a.part('Track_pods', 'Team', p)
    W.poly_turret(pod, [(2.25, [(-1.55, -4.9), (1.55, -4.9), (1.55, 4.9), (-1.55, 4.9)]),
                        (3.9, [(-1.45, -4.3), (1.45, -4.3), (1.45, 4.5), (-1.45, 4.5)])], chamfer=.08)
    sk = a.part('Skirts', 'Armor', p)
    for j in range(4):
        sk.box((.12, 2.2, 1.2), loc=(s * 1.62, -3.45 + j * 2.3, 1.65), bevel=0)
    K.rivet_line(a.part('Kit_rivets', 'Steel', p), (s * 1.7, -4.4, 2.15), (s * 1.7, 4.4, 2.15), (s, 0, 0), pitch=.6,
                 r=.05, h=.05)
    a.part('Hazard_stripes', 'Hazard', p).box((3.0, .06, .3), loc=(0, -4.92, 3.4), bevel=0)
    for yy in (-2.4, 2.4):
        K.grille(a, (0, yy, 3.92), 2.0, 1.6, facing=(0, 0, 1), slats=5, parent=p, frame_mat='Armor')
    K.hatch_round(a, (0, 0, 3.9), r=.45, parent=p, periscopes=0, seg=10)
    strut = a.part('Strut_beams', 'Steel', p)
    strut.box((1.8, 1.4, 1.0), loc=(-s * 2.2, 0, 3.3), bevel=0)
    strut.cyl(.55, 1.6, loc=(-s * 1.5, 0, 3.3), rot=ACROSS, seg=12, bevel=0)
    K.dust(a, (x, y, .3), radius=4.5, k=.3)


def monster(a):
    """See the module docstring. Runtime: Turret, Part_barrel, Main_cannon, Muzzle_brake, Muzzle_main, Mount_gun,
    Mount_gun.001 (front turrets, single barrels: mb_fix_barrels twins them), Mount_gun.002 / .003 (40 mm aft),
    Mount_gun.004 (casemate), Mount_mg / .001 (ZU-23 balconies), Part_missile / Mount_missile / Muzzle_missile,
    Part_track .. .003, Point_fire, Point_exhaust."""
    K.suffixed(a)
    for i, (x, y) in enumerate(((8.6, -11.6), (-8.6, -11.6), (8.6, 11.4), (-8.6, 11.4))):
        _monster_track(a, i, x, y)
    hull = a.part('Hull', 'Team')
    # Lower carriage between the pods, the upper superstructure with the sloped glacis (casemate port in it) and the
    # sloped stern.
    W.side_hull(a.part('Chassis', 'Armor'), [(15.2, 2.6), (15.4, 4.9), (-14.8, 4.9), (-15.0, 2.6)], 11.2, chamfer=.1)
    K.section_loft(hull, [
        (-15.35, [(0, 4.0), (6.3, 4.0), (6.3, 4.55), (5.5, 4.95), (0, 4.95)]),
        (-11.0, [(0, 4.8), (6.6, 4.8), (6.6, 6.35), (5.7, M_DECK), (0, M_DECK)]),
        (14.6, [(0, 4.8), (6.6, 4.8), (6.6, 6.35), (5.7, M_DECK), (0, M_DECK)]),
        (15.6, [(0, 4.8), (6.6, 4.8), (6.6, 6.2), (5.7, 6.55), (0, 6.55)])])
    # Riveted armour plates on the sides, the hazard band on the nose, ladders up the sides.
    for s in (-1, 1):
        for j in range(5):
            K.armour_plate(a, a.part('Armor_plates', 'Armor'), (2.6, 4.4, .16), (s * 6.66, -9.0 + j * 4.6, 5.9),
                           rot=(0, s * R90, 0), rivet=.55)
        K.ladder(a.part('Ladders', 'Steel'), (s * 6.75, 7.5, 2.6), (s * 6.75, 7.5, M_DECK), width=.6, step=.4)
        a.part('Team_band', 'Team').box((.03, 20.0, .5), loc=(s * 6.62, 0, 6.85), bevel=0)
    a.part('Hazard_stripes', 'Hazard').box((12.6, .06, .35), loc=(0, -15.33, 4.45), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 4.5, -15.0, 5.0), (0, -1, .2), r=.25)
        K.beacon(a, (s * 6.2, -10.5, M_DECK), r=.18)
        K.beacon(a, (s * 6.2, 14.2, M_DECK), r=.18)
    # Deck: railings round the edges, hatches, the walkway plates.
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        K.railing(rail, [(s * 6.45, -10.5, M_DECK), (s * 6.45, 14.4, M_DECK)], h=1.0, post=2.4, r=.04)
    for (x, y) in ((-3.5, -6.5), (3.5, 12.6), (-3.5, 12.6)):
        K.hatch_round(a, (x, y, M_DECK), r=.55, periscopes=0, seg=12)
    _monster_deck(a)
    _monster_balconies(a)
    _monster_fuel(a)
    _monster_engine(a)
    _monster_turret(a)
    _monster_secondaries(a)
    a.pivot('Point_fire', (0, 14.0, 6.6))
    a.pivot('Point_exhaust', (2.7, 18.2, 8.2))
    k.clean(a)


def _monster_deck(a):
    """Deck dressing that reads at the battle camera: bolted deck plates in rows (dark seams between), the yellow
    walkway lines, the ammunition stacks and the loading crane on the left (the Kornet sits right), vents, cable
    runs to the turret."""
    dp = a.part('Deck_plates', 'Armor')
    for row, y0 in enumerate((-10.4, -7.6, 9.3, 11.6)):
        for col in range(4):
            x = -4.2 + col * 2.8
            if row >= 2 and abs(x - 2.6 + 1.4) < 1.6:
                continue
            K.panel(a, dp, (2.6, 2.2), (x, y0, M_DECK), (0, 0, 1), t=.05, rivet=.6)
    wl = a.part('Hazard_stripes', 'Hazard')
    for s in (-1, 1):
        wl.box((.2, 24.0, .02), loc=(s * 5.3, 2.0, M_DECK + .01), bevel=0)
    W.lifting_eyes(a.part('Kit_tow', 'Steel'), [(s * 5.9, y, M_DECK + .05) for s in (-1, 1) for y in (-9.0, 13.5)],
                   r=.18)
    # Ammunition: 800 mm rounds on cradles and charge cases stacked on the left rear deck.
    for j in range(3):
        k.lathe(a.part('Shell_racks', 'Hazard'), [(0, -1.2), (.4, -1.1), (.42, .6), (.2, 1.1), (0, 1.15)],
                loc=(-2.3 - j * .95, 9.6, M_DECK + .5), rot=K.FORWARD, seg=10)
    rk = a.part('Shell_racks_frame', 'Steel')
    for yy in (8.9, 10.3):
        rk.box((3.2, .15, .3), loc=(-3.25, yy, M_DECK + .15), bevel=0)
    for j in range(4):
        K.crate(a.part('Ammo_crates', 'Crate'), a.part('Kit_latches', 'Steel'), (1.1, .7, .6),
                (-4.6 + (j % 2) * 1.2, 11.6 + (j // 2) * .8, M_DECK), bands=2)
    # The loading crane on the left: a post, the jib over the stacks, its hook block.
    cr = a.part('Crane', 'CraneYellow')
    cr.cyl(.35, 3.0, loc=(-5.6, 13.4, M_DECK + 1.5), seg=10, bevel=0)
    cr.limb((-5.6, 13.4, M_DECK + 2.8), (-2.6, 10.2, M_DECK + 3.4), .3, .4, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(-2.6, 10.2, M_DECK + 3.3), (-2.6, 10.2, M_DECK + 1.8)], .03, seg=4)
    a.part('Crane_hook', 'Steel').box((.4, .4, .5), loc=(-2.6, 10.2, M_DECK + 1.6), bevel=0)
    # Vents and the cable runs from the hull to the gun house's ring.
    for (x, y) in ((4.6, -2.5), (4.6, 7.5), (-4.6, 7.0)):
        K.grille(a, (x, y, M_DECK + .02), 1.4, 1.0, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    W.cable(a.part('Kit_cables', 'Steel'), [(4.4, 8.6, M_DECK + .1), (3.6, 8.0, M_DECK + .1), (3.2, 7.4, M_DECK + .5)],
            r=.08)
    W.cable(a.part('Kit_cables', 'Steel'), [(-4.4, -3.6, M_DECK + .1), (-3.6, -3.2, M_DECK + .1),
                                            (-3.2, -2.6, M_DECK + .5)], r=.08)


def _monster_fuel(a):
    """External fuel cells in a frame on the left side only, between the front pod and the balcony (the right
    side carries the Kornet's ammunition lockers on deck instead)."""
    fr = a.part('Fuel_frame', 'Steel')
    fr.box((1.6, 5.2, .2), loc=(-7.4, -3.6, 4.9), bevel=0)
    for yy in (-5.9, -1.3):
        fr.limb((-6.6, yy, 4.0), (-8.0, yy, 4.85), .18, .18, bevel=0)
    for j in range(3):
        k.lathe(a.part('Fuel_cells', 'Armor'), [(0, -.75), (.55, -.7), (.6, -.5), (.6, .5), (.55, .7), (0, .75)],
                loc=(-7.4, -5.2 + j * 1.6, 5.6), rot=K.FORWARD, seg=12)
        a.part('Kit_straps', 'Steel').cyl(.63, .08, loc=(-7.4, -5.2 + j * 1.6, 5.6), rot=K.FORWARD, seg=12, bevel=0)
    a.part('Hazard_stripes', 'Hazard').box((.06, 5.0, .2), loc=(-8.0, -3.6, 5.1), bevel=0)


def _monster_balconies(a):
    """A balcony each side carrying a ZU-23-2 on its raised pedestal (Mount_mg, Mount_mg.001)."""
    for i, s in enumerate((1, -1)):
        x = s * 7.3
        bal = a.part('Balconies', 'Armor')
        bal.box((2.2, 5.0, .25), loc=(s * 7.55, 2.4, 5.6), bevel=0)
        for yy in (.4, 4.4):
            bal.limb((s * 6.6, yy, 4.6), (s * 8.4, yy, 5.5), .2, .3, bevel=0)
        K.railing(a.part('Railings', 'Steel'), [(s * 6.7, -.05, 5.72), (s * 8.6, -.05, 5.72), (s * 8.6, 4.85, 5.72),
                                                (s * 6.7, 4.85, 5.72)], h=.9, post=1.2, r=.035)
        ped = a.part('Zu_pedestals', 'Steel')
        k.lathe(ped, [(.45, 0), (.45, .12), (.18, .2), (.18, .8), (.3, .85), (.3, .92)], loc=(x, 2.4, 5.73), seg=10)
        m = a.pivot(K.name('Mount_mg', i), (x, 2.4, 6.7))
        zu = a.part(K.name('Zu23_mount', i), 'Armor', m)
        K.chamfer_box(zu, (1.0, 1.0, .5), loc=(0, .15, .1), c=.05)
        for side in (-1, 1):
            zu.box((.08, .7, .5), loc=(side * .55, .1, .25), bevel=0)
        g = a.part(K.name('Zu23_guns', i), 'Steel', m)
        for side in (-.16, .16):
            k.lathe(g, [(.06, 0), (.06, .5), (.04, .55), (.04, 2.6), (.06, 2.62), (.06, 2.85), (0, 2.86)],
                    loc=(side, -.35, .36), rot=K.FORWARD, seg=8)
            a.part(K.name('Zu23_mags', i), 'Crate', m).box((.18, .45, .4), loc=(side, .05, .65), bevel=0)
        a.part(K.name('Zu23_seat', i), 'Undercarriage', m).box((.5, .4, .1), loc=(.6, .55, .3), bevel=0)
        a.pivot(K.name('Muzzle_mg', i), (0, -3.25, .36), m)


def _monster_engine(a):
    """The engine house on the rear deck: louvred sides, two smokestacks, the cooling grilles."""
    eh = a.part('Engine_house', 'Team')
    W.poly_turret(eh, [(M_DECK - .05, [(-4.8, 14.0), (4.8, 14.0), (4.8, 19.6), (-4.8, 19.6)]),
                       (M_DECK + 1.2, [(-4.4, 14.4), (4.4, 14.4), (4.4, 19.3), (-4.4, 19.3)])], chamfer=.08)
    W.side_hull(a.part('Chassis', 'Armor'), [(19.6, 4.0), (19.6, M_DECK), (15.4, M_DECK), (15.4, 4.0)], 9.0,
                chamfer=.08)
    for s in (-1, 1):
        K.grille(a, (s * 4.62, 16.8, M_DECK + .6), 3.6, .7, facing=(s, 0, .2), slats=6, frame_mat='Armor')
        K.smokestack(a, (s * 2.7, 18.2, M_DECK + 1.15), r=.45, h=1.6)
    K.grille(a, (0, 16.3, M_DECK + 1.21), 4.5, 2.6, facing=(0, 0, 1), slats=8, frame_mat='Armor')
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.5, .05, .25), loc=(s * 4.0, 19.63, 6.4), bevel=0)


def _monster_turret(a):
    """The gun house (Turret) and the 800 mm barrel on Part_barrel: a slab-sided house with sloped cheeks, the
    massive cradle and recoil cylinders, the barrel tilted up 7 degrees with its jacket rings and muzzle bell, the
    shell hoist and its rail on the house's back."""
    t = a.pivot('Turret', (0, 3.0, 8.0))
    body = a.part('Turret_body', 'Team', t)
    W.poly_turret(body, [
        (-.6, [(-3.0, -6.0), (3.0, -6.0), (4.2, -4.2), (4.2, 4.6), (3.2, 5.8), (-3.2, 5.8), (-4.2, 4.6),
               (-4.2, -4.2)]),
        (2.4, [(-2.8, -5.6), (2.8, -5.6), (4.0, -3.9), (4.0, 4.4), (3.0, 5.6), (-3.0, 5.6), (-4.0, 4.4),
               (-4.0, -3.9)]),
        (3.9, [(-2.0, -4.2), (2.0, -4.2), (3.1, -3.0), (3.1, 3.8), (2.4, 4.8), (-2.4, 4.8), (-3.1, 3.8),
               (-3.1, -3.0)])], chamfer=.1)
    k.ring(a.part('Turret_steel', 'Steel', t), [(4.0, -.85), (4.5, -.85), (4.5, -.55), (4.0, -.55)], seg=24)
    for s in (-1, 1):
        for j in range(3):
            K.armour_plate(a, a.part('Turret_armor', 'Armor', t), (1.9, 2.6, .14), (s * 4.06, -2.4 + j * 2.6, 1.0),
                           rot=(0, s * R90, 0), rivet=.5, parent=t)
    K.hatch_round(a, (2.2, 2.6, 3.9), r=.55, parent=t, periscopes=2, seg=12)
    K.periscope(a, (-2.0, -2.6, 3.9), facing=(0, -1, 0), parent=t, size=(.6, .55, .5))
    K.floodlight(a, (-2.6, -3.6, 3.9), facing=(0, -1, -.15), pole=.6, parent=t)
    a.part('Team_band', 'Team', t).box((4.0, 2.5, .03), loc=(0, .8, 3.92), bevel=0)
    for (x, y) in ((-1.4, -3.2), (1.4, -3.2), (-1.6, 3.3), (1.6, 3.3)):
        K.panel(a, a.part('Turret_armor', 'Armor', t), (1.6, 1.5), (x, y, 3.9), (0, 0, 1), t=.06, rivet=.5,
                parent=t)
    K.grille(a, (0, -1.5, 3.92), 1.4, 1.0, facing=(0, 0, 1), slats=5, parent=t, frame_mat='Armor')
    # Shell hoist: a rail out of the house's back and the trolley with a 800 mm round in its cradle.
    hoist = a.part('Shell_hoist', 'Steel', t)
    hoist.box((.25, 3.0, .3), loc=(0, 6.8, 3.4), bevel=0)
    for s in (-1, 1):
        hoist.limb((s * .9, 5.4, 2.0), (s * .1, 7.8, 3.3), .15, .15, bevel=0)
    hoist.box((.8, .8, .6), loc=(0, 7.6, 3.0), bevel=0)
    k.lathe(a.part('Shell', 'Hazard', t), [(0, -1.2), (.4, -1.1), (.42, .6), (.2, 1.1), (0, 1.15)],
            loc=(0, 7.6, 2.0), rot=K.FORWARD, seg=12)
    # The gun: cradle on trunnions, recoil cylinders, the tilted barrel (Part_barrel pivot at the trunnion line).
    pb = a.pivot('Part_barrel', (0, -6.18, 1.87), t)
    e = math.atan2(11.89 - 9.87, 19.66 - 3.18)
    K.chamfer_box(a.part('Barrel_cradle', 'Armor', pb), (2.8, 3.6, 2.6), loc=(0, .4, 0), rot=(-e, 0, 0), c=.12)
    for s in (-1, 1):
        a.part('Barrel_cradle', 'Armor', pb).cyl(.75, .6, loc=(s * 1.6, 1.0, 0), rot=ACROSS, seg=14, bevel=0)
    d = Vector((0, -math.cos(e), math.sin(e)))
    rc = a.part('Recoil_cylinders', 'Steel', pb)
    for s in (-1, 1):
        o = Vector((s * .85, 0, .9))
        k.lathe(rc, [(.28, 0), (.28, 5.0), (.2, 5.1), (.2, 5.6), (0, 5.62)], loc=tuple(o + d * -1.0), rot=_lift(e),
                seg=10)
    # Barrel profile from the breech ring to the muzzle bell; Main_cannon carries the boss part (Main_cannon*).
    L = 16.6
    prof = [(1.25, -1.2), (1.25, -.4), (1.0, -.3), (1.0, 3.0), (1.08, 3.05), (1.08, 3.35), (.92, 3.4), (.92, 8.0),
            (.98, 8.05), (.98, 8.3), (.8, 8.35), (.72, L - 1.3), (.8, L - 1.2), (.8, L - .3), (.62, L), (0, L)]
    k.lathe(a.part('Main_cannon', 'Steel', pb), prof, loc=(0, -1.6 * math.cos(e) * 0, 0), rot=_lift(e), seg=20,
            worn=(5, 9))
    k.lathe(a.part('Muzzle_brake', 'Undercarriage', pb), [(.95, L - .9), (1.0, L - .8), (1.0, L + .2), (.7, L + .25),
                                                           (0, L + .25)], rot=_lift(e), seg=20)
    a.part('Main_cannon_bands', 'Team', pb).cyl(.95, .5, loc=tuple(d * 9.5), rot=_lift(e), seg=20, bevel=0)
    a.pivot('Muzzle_main', (0, -22.66, 3.89), t)
    K.soot(a, (0, -19.66, 11.89), radius=2.0, k=.4)


def _monster_secondaries(a):
    """Front 100 mm turrets (single barrel each: mb_fix_barrels makes them twins), 40 mm turrets aft, the casemate
    155 mm in the glacis, the twin Kornet on the rear deck."""
    for i, (x, y) in enumerate(((5.07, -9.51), (-5.07, -9.51))):
        k.ring(a.part('Turret_rings', 'Steel'), [(1.1, -.05), (1.3, -.05), (1.3, .15), (1.1, .15)], loc=(x, y, M_DECK),
               seg=16)
        m = a.pivot(K.name('Mount_gun', i), (x, y, 7.4))
        house = a.part(K.name('Gun_house', i), 'Team', m)
        W.poly_turret(house, [(0, [(-1.2, -1.2), (1.2, -1.2), (1.3, .6), (.9, 1.4), (-.9, 1.4), (-1.3, .6)]),
                              (1.3, [(-.85, -.9), (.85, -.9), (1.0, .5), (.7, 1.15), (-.7, 1.15), (-1.0, .5)])],
                      chamfer=.06)
        K.chamfer_box(a.part(K.name('Gun_mantlet', i), 'Armor', m), (.7, .4, .6), loc=(0, -1.3, .42), c=.05)
        K.gun_barrel(a, K.name('Gun_barrel', i), m, 0, -1.45, .42, 2.66, .12, seg=12, extractor=(.45, 1.5, .4),
                     brake_name=K.name('Gun_brake', i), brake='collar')
        K.periscope(a, (.5, .3, 1.3), facing=(0, -1, 0), parent=m, size=(.3, .28, .25))
        a.pivot(K.name('Muzzle_gun', i), (0, -4.25, .42), m)
    for j, (x, y) in enumerate(((4.9, 9.9), (-4.9, 9.9))):
        i = j + 2
        k.ring(a.part('Turret_rings', 'Steel'), [(.9, -.05), (1.05, -.05), (1.05, .15), (.9, .15)], loc=(x, y, M_DECK),
               seg=16)
        m = a.pivot(K.name('Mount_gun', i), (x, y, 7.4))
        bof = a.part(K.name('Bofors_mount', i), 'Armor', m)
        k.lathe(bof, [(.9, 0), (.9, .2), (.6, .3), (0, .3)], seg=14)
        for s in (-1, 1):
            bof.box((.1, 1.4, 1.1), loc=(s * .55, .1, .75), bevel=0)
        K.chamfer_box(a.part(K.name('Bofors_shield', i), 'Team', m), (1.6, .12, .9), loc=(0, -.75, .7), c=.03)
        g = a.part(K.name('Bofors_gun', i), 'Steel', m)
        K.chamfer_box(g, (.4, 1.2, .4), loc=(0, -.1, .55), c=.04)
        k.lathe(g, [(.07, 0), (.07, 2.6), (.1, 2.62), (.1, 3.0), (0, 3.02)], loc=(0, -.7, .42), rot=K.FORWARD, seg=10)
        a.part(K.name('Bofors_clips', i), 'Crate', m).box((.3, .4, .5), loc=(0, .2, 1.0), bevel=0)
        a.pivot(K.name('Muzzle_gun', i), (0, -4.25, .42), m)
    # The casemate 155 mm in its ball mount in the glacis.
    k.lathe(a.part('Casemate_ball', 'Armor'), [(0, -.8), (1.2, -.6), (1.35, 0), (1.2, .5), (.9, .8)],
            loc=(0, -12.05, 6.4), rot=K.FORWARD, seg=16)
    m = a.pivot(K.name('Mount_gun', 4), (0, -12.05, 6.4))
    K.gun_barrel(a, 'T_barrel_Mount_gun_004', m, 0, -1.0, .72, 6.45, .16, seg=12, extractor=(.4, 1.6, .5),
                 brake_name='T_brake_Mount_gun_004', brake='baffle')
    a.pivot(K.name('Muzzle_gun', 4), (0, -7.6, .72), m)
    # The twin Kornet on its pedestal on the rear deck (Part_missile breaks off).
    pm = a.pivot('Part_missile', (2.6, 12.6, 8.0))
    k.lathe(a.part('Atgm_pedestal', 'Steel', pm), [(.7, -.8), (.7, -.65), (.25, -.5), (.25, .85), (.35, .9)], seg=12)
    mm = a.pivot('Mount_missile', (0, 0, .9), pm)
    K.chamfer_box(a.part('Atgm_cradle', 'Armor', mm), (1.0, .6, .5), loc=(0, 0, .25), c=.04)
    e = .55
    for s in (-.25, .25):
        k.lathe(a.part('Launch_tubes', 'Fuel', mm), [(.16, -1.0), (.18, -.95), (.18, 1.4), (.16, 1.45)],
                loc=(s + .5, -.2, 1.0), rot=_lift(e), seg=10)
        a.part('Launch_tubes_bore', 'Undercarriage', mm).cyl(.13, .02,
                                                             loc=(s + .5, -.2 - 1.45 * math.cos(e), 1.0 + 1.45 * math.sin(e)),
                                                             rot=_lift(e), seg=10, bevel=0)
    K.chamfer_box(a.part('Atgm_armor', 'Armor', mm), (.5, .5, .6), loc=(-.35, .1, .7), c=.04)
    a.part('Atgm_sight_glass', 'Glass', mm).box((.3, .02, .2), loc=(-.35, -.16, .8), bevel=0)
    a.pivot('Muzzle_missile', (.5, -1.35, 1.44), mm)


# ============================================================================= landing_hovercraft
H_DECK = 4.2            # the side structures' weather deck


def _hover_ciws(a, part_name, i, slot, loc):
    """An AK-630-class six-barrel mount on its Part_* pivot (breakable): the pedestal ring, the turning mount
    (Mount_<slot>), the domed gun house, the barrel cluster with its cooling jacket and the radar-guided sight."""
    p = a.pivot(K.name(part_name, i), loc)
    k.lathe(a.part(K.name(f'Ciws_base_{slot}', i), 'Armor', p), [(.85, -.05), (.85, .15), (.6, .25), (0, .25)],
            seg=14)
    m = a.pivot(K.name(f'Mount_{slot}', i), (0, 0, .02), p)
    body = a.part(K.name(f'Ciws_body_{slot}', i), 'Team', m)
    W.poly_turret(body, [(.2, [(-.6, -.55), (.6, -.55), (.7, .2), (.5, .75), (-.5, .75), (-.7, .2)]),
                         (1.05, [(-.42, -.4), (.42, -.4), (.5, .15), (.36, .6), (-.36, .6), (-.5, .15)])],
                  chamfer=.05)
    g = a.part(K.name(f'Ciws_barrels_{slot}', i), 'Steel', m)
    k.lathe(g, [(.17, 0), (.17, 1.9), (.14, 1.95), (0, 1.96)], loc=(0, -.5, .62), rot=K.FORWARD, seg=10)
    k.lathe(g, [(.21, .1), (.21, .5), (.18, .55), (0, .56)], loc=(0, -.5, .62), rot=K.FORWARD, seg=10)
    a.part(K.name(f'Ciws_bores_{slot}', i), 'Undercarriage', m).cyl(.12, .02, loc=(0, -2.47, .62), rot=K.FORWARD,
                                                                   seg=10, bevel=0)
    k.lathe(a.part(K.name(f'Ciws_dome_{slot}', i), 'PlasterWhite', m), [(.3, 0), (.32, .18), (.2, .34), (0, .38)],
            loc=(.35, .25, 1.02), seg=10)
    a.pivot(K.name(f'Muzzle_{slot}', i), (0, -2.67, .62), m)


def _hover_rockets(a, i, loc):
    """An A-22 Ogon 140 mm launcher on its Part_rocket pivot: the turntable, the cradle and the 22-tube box with
    its armoured covers."""
    p = a.pivot(K.name('Part_rocket', i), loc)
    k.lathe(a.part(K.name('Launcher_base_rocket', i), 'Armor', p), [(.9, -.1), (.9, .1), (.6, .2), (0, .2)], seg=14)
    m = a.pivot(K.name('Mount_rocket', i), (0, 0, .02), p)
    for s in (-1, 1):
        a.part(K.name('Launcher_cheeks_rocket', i), 'Armor', m).box((.14, .9, .9), loc=(s * .8, .1, .5), bevel=0)
    a.part(K.name('Launcher_pin_rocket', i), 'Steel', m).cyl(.12, 1.8, loc=(0, .1, .7), rot=ACROSS, seg=8, bevel=0)
    e = .35
    box = a.part(K.name('Rocket_box_rocket', i), 'Team', m)
    K.chamfer_box(box, (1.4, 1.9, 1.0), loc=(0, -.3, .95), rot=(-e, 0, 0), c=.05)
    d = Vector((0, -math.cos(e), math.sin(e)))
    up = Vector((0, math.sin(e), math.cos(e)))
    face = Vector((0, -.3, .95)) + d * .96
    tb = a.part('Launcher_tubes_bore', 'Undercarriage', m)
    for c in range(5):
        for r in range(4):
            q = face + Vector(((c - 2) * .25, 0, 0)) + up * ((r - 1.5) * .22)
            tb.cyl(.075, .02, loc=tuple(q), rot=_lift(e), seg=8, bevel=0)
    a.part(K.name('Launcher_bands_rocket', i), 'Hazard', m).box((1.42, .1, 1.02), loc=tuple(Vector((0, -.3, .95)) +
                                                                                          d * .6), rot=(-e, 0, 0),
                                                                bevel=0)
    a.pivot(K.name('Muzzle_rocket', i), (0, -.68, .81), m)


def _hover_fan(a, i, loc):
    """A ducted propeller on its Part_fan pivot: the duct ring with its band and stators, the rudder vanes behind
    it, the pylon under it, the four-blade propeller (Propeller / Propeller_2 spins)."""
    p = a.pivot(K.name('Part_fan', i), loc)
    R = 2.35
    duct = a.part(K.name('Duct_fan', i), 'Team', p)
    k.ring(duct, [(R, -.7), (R + .25, -.65), (R + .3, .5), (R + .2, .8), (R, .75)], rot=K.FORWARD, seg=24)
    k.ring(a.part(K.name('Duct_band_fan', i), 'Hazard', p), [(R + .05, -.5), (R + .32, -.5), (R + .32, -.25),
                                                            (R + .05, -.25)], rot=K.FORWARD, seg=24)
    st = a.part(K.name('Fan_stators_fan', i), 'Armor', p)
    for j in range(4):
        u = j * TAU / 4 + TAU / 8
        st.box((.12, .14, R * 2), loc=(0, .5, 0), rot=(0, u, 0), bevel=0)
    for j in range(3):
        a.part(K.name('Fan_armor_fan', i), 'Armor', p).box((.12, .9, R * 1.8), loc=((j - 1) * 1.2, 1.3, 0),
                                                            bevel=0)
    a.part(K.name('Fan_armor_fan', i), 'Armor', p).box((1.0, 2.0, 2.2), loc=(0, .2, -R - .9), bevel=0)
    pr = a.pivot('Propeller' if i == 0 else 'Propeller_2', (0, -.1, 0), p)
    bl = a.part('Propeller_blades' if i == 0 else 'Propeller_2_blades', 'Undercarriage', pr)
    for j in range(4):
        u = j * TAU / 4 + i * .4
        bl.box((.5, .08, R * .92), loc=(math.cos(u) * R * .47, 0, math.sin(u) * R * .47), rot=(.25, -u + R90, 0),
               bevel=0, taper=(.6, 1))
    k.lathe(a.part('Propeller_hub' if i == 0 else 'Propeller_2_hub', 'Steel', pr), [(0, -.5), (.35, -.3), (.4, .2),
                                                                                    (.3, .4)], rot=K.FORWARD,
            seg=10)


def landing_hovercraft(a):
    """Zubr / LCAC air-cushion landing craft: see the module docstring. Runtime: Part_ramp / Muzzle_ramp, Part_fan /
    .001 with Propeller / Propeller_2, Part_gun / .001 and Part_mg / .001 (CIWS, each with Mount_ and Muzzle_),
    Part_rocket / .001 (A-22, with Mount_ / Muzzle_), Mount_APS (added: the def has APS)."""
    K.suffixed(a)
    # The black skirt with its finger segments, the buoyancy hull above it, the rub rail.
    skirt = a.part('Skirt', 'Rubber')
    ring = [(-7.6, -13.0), (-6.6, -15.4), (6.6, -15.4), (7.6, -13.0), (7.9, 11.5), (6.8, 13.5), (-6.8, 13.5),
            (-7.9, 11.5)]
    inner = [(x * .92, y * .95) for x, y in ring]
    k.sharp_loft(skirt, [[(x * .94, y * .96, 0) for x, y in ring], [(x, y, .9) for x, y in ring],
                         [(x * .99, y * .99, 2.1) for x, y in ring]], chamfer=.05)
    fing = a.part('Skirt_fingers', 'Rubber')
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 1.1))
        for j in range(n):
            f = (j + .5) / n
            x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            fing.box((.55, .5, 1.1), loc=(x * 1.0, y * 1.0, .55), rot=(0, 0, math.atan2(y1 - y0, x1 - x0)), bevel=0,
                     taper=(.7, 1.3))
    hull = a.part('Hull', 'Team')
    k.sharp_loft(hull, [[(x, y, 2.05) for x, y in ring], [(x * 1.01, y * 1.01, 2.45) for x, y in ring],
                        [(x * .93, y * .96, 3.1) for x, y in ring]], chamfer=.06)
    a.part('Rub_rail', 'Undercarriage').tube([(x * 1.005, y * 1.005, 2.2) for x, y in ring + ring[:1]], .14, seg=6)
    # Cargo deck between the side structures, its tie-down rows and the markings.
    deck = a.part('Cargo_deck', 'Armor')
    deck.box((6.8, 22.0, .1), loc=(0, -.5, 3.12), bevel=0)
    td = a.part('Tie_downs', 'Steel')
    for x in (-2.4, -.8, .8, 2.4):
        for j in range(9):
            td.cyl(.08, .06, loc=(x, -10.0 + j * 2.3, 3.18), seg=6, bevel=0)
    mk = a.part('Deck_markings', 'Hazard')
    for x in (-3.2, 3.2):
        mk.box((.15, 21.0, .02), loc=(x, -.5, 3.18), bevel=0)
    mk.box((6.2, .15, .02), loc=(0, 9.8, 3.18), bevel=0)
    # The two side structures: lower block, upper tier with windows, the wheelhouse on the left front.
    for s in (-1, 1):
        ss = a.part('Side_structures', 'Team')
        W.poly_turret(ss, [(3.0, [(s * 3.5, -12.2), (s * 7.6, -11.0), (s * 7.6, 11.4), (s * 3.5, 11.4)]),
                           (H_DECK, [(s * 3.6, -11.7), (s * 7.4, -10.7), (s * 7.4, 11.2), (s * 3.6, 11.2)])][::1]
                      if s > 0 else
                      [(3.0, [(s * 3.5, -12.2), (s * 3.5, 11.4), (s * 7.6, 11.4), (s * 7.6, -11.0)]),
                       (H_DECK, [(s * 3.6, -11.7), (s * 3.6, 11.2), (s * 7.4, 11.2), (s * 7.4, -10.7)])],
                      chamfer=.08)
        tier = a.part('Superstructure', 'Team')
        # The left tier starts aft of the left CIWS (Part_gun.001 at y -3.0), the right one ahead of it.
        ty0, ty1 = (-3.5, 2.5) if s > 0 else (-1.9, 3.4)
        W.poly_turret(tier, [(H_DECK, [(s * 4.1, ty0), (s * 6.9, ty0), (s * 6.9, ty1), (s * 4.1, ty1)]),
                             (H_DECK + 1.3, [(s * 4.4, ty0 + .5), (s * 6.6, ty0 + .5), (s * 6.6, ty1 - .3),
                                             (s * 4.4, ty1 - .3)])],
                      chamfer=.06)
        # Gas-turbine exhausts aft of the tier, louvred vent boxes, deck hatches (clear of the mounts and cabin).
        for j, y in enumerate((-5.0,) if s > 0 else (-9.6, -5.0)):
            K.hatch_rect(a, (s * 5.0, y, H_DECK), size=(.7, .9), normal=(0, 0, 1))
        K.exhaust(a, (s * 6.4, 9.6, H_DECK), r=.35, length=1.3, direction=(0, .3, 1), muffler=False)
        K.exhaust(a, (s * 4.6, 9.6, H_DECK), r=.35, length=1.3, direction=(0, .3, 1), muffler=False)
        for y in (ty0 + 1.7, ty0 + 4.1):
            K.grille(a, (s * 4.08, y, H_DECK + .6), 1.4, .6, facing=(-s, 0, 0), slats=4, frame_mat='Armor')
        win = a.part('Cabin_glass', 'Glass')
        for j in range(5 if s > 0 else 4):
            win.box((.02, .7, .45), loc=(s * 6.91, ty0 + .7 + j * 1.15, H_DECK + .8), bevel=0)
            win.box((.02, .7, .45), loc=(s * 4.09, ty0 + .7 + j * 1.15, H_DECK + .8), bevel=0)
        # Lift-fan intakes (louvred) aft of the tier, life-raft canisters along the outer edge, railings.
        for y in (4.8, 7.6):
            K.chamfer_box(a.part('Intakes', 'Armor'), (2.6, 2.2, 1.6), loc=(s * 5.6, y, H_DECK + .8), c=.06)
            K.grille(a, (s * 5.6, y, H_DECK + 1.62), 2.2, 1.8, facing=(0, 0, 1), slats=6, frame_mat='Armor')
        for j in range(6):
            k.lathe(a.part('Life_rafts', 'PlasterWhite'), [(.28, -.45), (.3, -.4), (.3, .4), (.28, .45)],
                    loc=(s * 7.25, -9.0 + j * .9, H_DECK + .32), rot=K.FORWARD, seg=8)
        K.railing(a.part('Railings', 'Steel'), [(s * 7.45, -10.5, H_DECK), (s * 7.45, 9.6, H_DECK)], h=.9, post=1.6,
                  r=.03)
        K.ladder(a.part('Railings', 'Steel'), (s * 3.5, 8.0, 3.15), (s * 3.5, 8.0, H_DECK), width=.5, step=.3)
        a.part('Team_band', 'Team').box((.03, 18.0, .35), loc=(s * 7.62, -.5, 3.6), bevel=0)
        for j in range(6):
            K.panel(a, a.part('Side_panels', 'Armor'), (2.6, .8), (s * 7.6, -9.0 + j * 3.2, 3.55), (s, 0, 0), t=.04,
                    rivet=.5)
            K.panel(a, a.part('Side_panels', 'Armor'), (2.4, .7), (s * 3.5, -9.0 + j * 3.2, 3.6), (-s, 0, 0), t=.04,
                    rivet=0)
        K.railing(a.part('Railings', 'Steel'), [(s * 3.65, -10.8, H_DECK), (s * 3.65, 9.6, H_DECK)], h=.9, post=1.8,
                  r=.03)
        bl = a.part('Bollards', 'Steel')
        for y in (-10.2, -4.0, 2.0, 8.6):
            bl.cyl(.12, .35, loc=(s * 7.1, y, H_DECK + .17), seg=8, bevel=0)
        a.part('Hazard_stripes', 'Hazard').box((.2, 21.0, .02), loc=(s * 7.2, -.3, H_DECK + .01), bevel=0)
        K.dust(a, (s * 7.6, -.5, .3), radius=6.0, k=.3)
        a.part('Nav_red' if s > 0 else 'Nav_green', 'LavaGlow' if s > 0 else 'SignalGreen').box(
            (.1, .3, .15), loc=(s * 7.45, -10.6, H_DECK + .2), bevel=0)
        a.part('Stern_lights', 'Lamp').box((.3, .1, .2), loc=(s * 6.0, 11.25, H_DECK - .2), bevel=0)
    cab = a.part('Cabin', 'Team')
    # The wheelhouse ahead of the right CIWS (Part_gun at y -6.4) and inboard of the life rafts.
    W.poly_turret(cab, [(H_DECK + 1.3, [(3.9, -10.6), (6.8, -10.6), (6.8, -7.4), (3.9, -7.4)]),
                        (H_DECK + 2.6, [(4.1, -10.0), (6.6, -10.0), (6.6, -7.6), (4.1, -7.6)])], chamfer=.06)
    K.chamfer_box(cab, (2.9, 3.2, 1.3), loc=(5.35, -9.0, H_DECK + .65), c=.06)
    win = a.part('Cabin_glass', 'Glass')
    win.box((2.4, .02, .5), loc=(5.35, -10.32, H_DECK + 1.95), rot=(-.43, 0, 0), bevel=0)
    for s in (-1, 1):
        win.box((.02, 1.8, .45), loc=(5.35 + s * 1.36, -8.8, H_DECK + 1.95), bevel=0)
    # Mast with the radar dome, antennas, the beacon and the APS sensor head.
    mast = a.part('Antenna', 'Steel')
    mast.cyl(.12, 2.0, loc=(5.35, -8.2, H_DECK + 3.6), seg=8, bevel=0)
    mast.box((1.8, .08, .08), loc=(5.35, -8.2, H_DECK + 4.1), bevel=0)
    k.lathe(a.part('Radar_dome', 'PlasterWhite'), [(.5, 0), (.55, .25), (.35, .55), (0, .62)],
            loc=(5.35, -8.2, H_DECK + 4.55), seg=12)
    K.whip_antenna(a.part('Antenna', 'Steel'), (4.3, -7.9, H_DECK + 2.6), h=1.6)
    K.beacon(a, (6.4, -7.9, H_DECK + 2.6), r=.15)
    K.chamfer_box(a.part('Mast_lights', 'Armor'), (.5, .5, .4), loc=(4.4, -9.9, H_DECK + 2.8), c=.04)
    K.radar_mast(a, (-5.5, -8.4, H_DECK), h=3.4)
    a.pivot('Mount_APS', (4.4, -9.9, H_DECK + 3.0))
    # Cargo: two tarp-covered vehicles chained down and a pallet row (the troops it lands).
    for j, y in enumerate((-6.8, 1.0)):
        tarp = a.part('Cargo_tarps', 'Canvas')
        W.poly_turret(tarp, [(3.17, [(-1.55, y - 3.2), (1.55, y - 3.2), (1.55, y + 3.2), (-1.55, y + 3.2)]),
                             (4.4, [(-1.3, y - 2.6), (1.3, y - 2.6), (1.3, y + 3.0), (-1.3, y + 3.0)]),
                             (5.3, [(-.9, y - 1.2), (.9, y - 1.2), (.9, y + 2.2), (-.9, y + 2.2)])], chamfer=.1)
        ch = a.part('Kit_cables', 'Steel')
        for dy in (-2.6, 2.6):
            for sx in (-1, 1):
                ch.tube([(sx * 1.4, y + dy, 3.9), (sx * 2.4, y + dy * 1.2, 3.18)], .04, seg=4)
        for dy in (-1.8, 0, 1.8):
            a.part('Kit_straps', 'Crate').box((3.2, .12, .04), loc=(0, y + dy, 4.42), bevel=0)
    for j in range(3):
        K.crate(a.part('Cargo_pallets', 'Crate'), a.part('Kit_latches', 'Steel'), (1.2, 1.0, .9),
                (-1.4 + j * 1.4, 6.8, 3.17), bands=2)
    # A boat davit at the stern's left with the rescue boat hung out behind (the Zubr's port quarter).
    dv = a.part('Davit', 'Steel')
    dv.cyl(.15, 2.5, loc=(-5.2, 12.6, H_DECK + 1.25), seg=8, bevel=0)
    dv.limb((-5.2, 12.6, H_DECK + 2.4), (-5.2, 14.6, H_DECK + 2.1), .14, .14, bevel=0)
    K.rhib(a.part('Rhib', 'Armor'), a.part('Rhib_tube', 'Rubber'), (-5.2, 14.7, H_DECK + .2), length=3.2, beam=1.5)
    # Bow: the ramp on Part_ramp (raised for transit), bow lamps; Muzzle_ramp where the vehicles leave.
    pr = a.pivot('Part_ramp', (0, -12.5, 2.3))
    ramp = a.part('Ramp', 'Team', pr)
    ramp.box((6.6, .3, 4.2), loc=(0, -.3, 2.1), rot=(-.18, 0, 0), bevel=.04)
    ribs = a.part('Ramp_ribs', 'Armor', pr)
    for x in (-2.4, -.8, .8, 2.4):
        ribs.box((.15, .2, 4.0), loc=(x, -.62, 2.05), rot=(-.18, 0, 0), bevel=0)
    a.part('Ramp_edges', 'Hazard', pr).box((6.65, .32, .25), loc=(0, -.68, 4.0), rot=(-.18, 0, 0), bevel=0)
    a.part('Ramp_steel', 'Steel', pr).cyl(.18, 6.4, rot=ACROSS, seg=8, bevel=0)
    for s in (-1, 1):
        a.part('Ramp_steel', 'Steel', pr).limb((s * 3.0, .3, .3), (s * 3.0, -.4, 3.2), .14, .14, bevel=0)
    a.pivot('Muzzle_ramp', (0, -3.16, -2.2), pr)
    for s in (-1, 1):
        K.lamp(a, (s * 4.5, -12.0, H_DECK - .5), (0, -1, 0), r=.18)
    # Weapons: four CIWS (asymmetric as before), two A-22 launchers, the stern fans.
    _hover_ciws(a, 'Part_gun', 0, 'gun', (5.3, -6.4, 4.3))
    _hover_ciws(a, 'Part_gun', 1, 'gun', (-5.3, -3.0, 4.3))
    for i, s in enumerate((1, -1)):
        k.lathe(a.part('Weapon_columns', 'Armor'), [(.7, 0), (.7, .6), (.85, .62)], loc=(s * 5.3, 3.7, H_DECK), seg=12)
        _hover_ciws(a, 'Part_mg', i, 'mg', (s * 5.3, 3.7, 4.8))
        _hover_rockets(a, i, (s * 5.3, -11.2, 4.45))
        _hover_fan(a, i, (s * 5.3, 10.9, 6.55))
    k.clean(a)


# ============================================================================= typhon
T_DECK = 3.8            # the casing deck


def typhon(a):
    """Project 941 Akula (Typhoon) at the game's scale: the very wide flat hull (two pressure hulls under one casing),
    the 20 missile tubes in two rows FORWARD of the sail (as on the real boat) under the hinged doors (Part_doors_l,
    Part_doors_r), the long low sail aft of them with its masts and the SAM post (Mount_missile), the retractable
    bow planes, the chin sonar dome (Part_sonar), the cruciform stern with the end-plated planes and the twin
    shrouded screws (Part_rudder), a deck gun on the forecasing (Mount_gun; single barrel, mb_fix_barrels twins it).
    The boss parts sit where the real boat has them (the old file had the silo aft of the sail); nodes are named as
    before. Runtime: Part_sail, Part_doors_l, Part_doors_r, Part_rudder, Part_sonar, Mount_missile / Muzzle_missile,
    Mount_gun / Muzzle_gun."""
    K.suffixed(a)
    hull = a.part('Hull', 'Armor')
    # Stations bow (-Y) to stern: a flattened ellipse, widest amidships, tapering to the screws.
    st = []
    for y, w, h, zc in ((-29.5, .4, .4, .5), (-28.6, 2.6, 2.0, .45), (-26.5, 4.4, 3.0, .4), (-22.0, 5.4, 3.4, .35),
                        (-12.0, 5.75, 3.5, .3), (8.0, 5.75, 3.5, .3), (16.0, 5.4, 3.2, .3), (22.0, 3.6, 2.4, .35),
                        (26.0, 1.6, 1.3, .4), (27.6, .5, .5, .4)):
        st.append((y, K.ellipse_half(w, h, zc, n=8)))
    K.section_loft(hull, st)
    # The casing deck on top, the limber holes along its sides, the waterline band.
    casing = a.part('Deck_casing', 'Armor')
    W.poly_turret(casing, [(T_DECK - .7, [(-3.6, -25.0), (3.6, -25.0), (4.1, -18.0), (4.1, 14.0), (2.8, 19.5),
                                          (-2.8, 19.5), (-4.1, 14.0), (-4.1, -18.0)]),
                           (T_DECK, [(-3.0, -24.0), (3.0, -24.0), (3.6, -18.0), (3.6, 13.5), (2.4, 18.6),
                                     (-2.4, 18.6), (-3.6, 13.5), (-3.6, -18.0)])], chamfer=.06)
    holes = a.part('Limber_holes', 'Undercarriage')
    for s in (-1, 1):
        for j in range(34):
            y = -21.0 + j * 1.05
            holes.box((.05, .55, .16), loc=(s * (4.1 - .02 if -18 < y < 14 else 3.7), y, T_DECK - .45), bevel=0)
        a.part('Waterline_band', 'BarrelRed').box((.04, 40.0, .3), loc=(s * 6.07, -2.0, .3), bevel=0)
        a.part('Team_band', 'Team').box((.04, 30.0, .25), loc=(s * 5.95, -2.0, 1.6), bevel=0)
    # Anechoic tile seams on the upper hull (thin dark lines), cleats, an escape hatch row, the anchor recess.
    seams = a.part('Tile_seams', 'Undercarriage')
    for j in range(12):
        y = -18.0 + j * 3.0
        seams.tube([(-5.6, y, 1.9), (-4.4, y, 3.0)], .03, seg=3, caps=False)
        seams.tube([(5.6, y, 1.9), (4.4, y, 3.0)], .03, seg=3, caps=False)
    # The anechoic coating on the casing: big tiles in rows, some darker (renewed) and some fallen off (the bare
    # steel shows dark), the look of the real boats.
    tiles = a.part('Deck_tiles', 'Team')
    dark = a.part('Deck_tiles_new', 'Armor')
    bare = a.part('Deck_tiles_bare', 'Undercarriage')
    for j in range(17):
        y = -23.0 + j * 2.45
        if -17.2 < y < -.8:
            continue
        half = 3.0 if y < -18 else 3.5 if y < 13.5 else 2.6
        n = 3 if half > 2.8 else 2
        for c in range(n):
            x = -half + (c + .5) * (2 * half / n)
            code = (j * 7 + c * 3) % 11
            part = bare if code == 0 else dark if code in (3, 7) else tiles
            part.box((2 * half / n - .12, 2.33, .05), loc=(x, y, T_DECK + .02), bevel=0)
    for s in (-1, 1):
        for j in range(13):
            y = -19.0 + j * 2.9
            code = (j * 5 + (s > 0)) % 7
            part = bare if code == 0 else dark if code == 4 else tiles
            part.box((.05, 2.75, 1.0), loc=(s * 5.66, y, 2.05), rot=(0, s * -.55, 0), bevel=0)
    cl = a.part('Cleats', 'Steel')
    for s in (-1, 1):
        for y in (-22.0, -17.5, 11.0, 15.0):
            cl.box((.15, .5, .12), loc=(s * 3.2, y, T_DECK + .06), bevel=0)
    for y in (-21.5, 12.5, 16.5):
        K.hatch_round(a, (0, y, T_DECK), r=.45, periscopes=0, seg=10)
    a.part('Anchor_recess', 'Undercarriage').box((.6, .9, .5), loc=(1.6, -26.0, 2.2), rot=(0, 0, .3), bevel=0)
    # Surfaced fittings: the stanchions and lifelines rigged along the casing, mooring bollards, the two rescue buoy
    # hatches (yellow-marked), ventilation grilles aft, a coiled line.
    rail = a.part('Railings', 'Steel')
    for s in (-1, 1):
        K.railing(rail, [(s * 3.3, -22.5, T_DECK), (s * 3.3, -17.6, T_DECK)], h=.9, post=1.0, r=.03)
        K.railing(rail, [(s * 3.3, 9.5, T_DECK), (s * 3.3, 17.0, T_DECK)], h=.9, post=1.0, r=.03)
        bl = a.part('Bollards', 'Steel')
        for y in (-23.0, -18.5, 10.0, 14.0, 17.5):
            for dy in (-.25, .25):
                bl.cyl(.13, .4, loc=(s * 2.6, y + dy, T_DECK + .2), seg=8, bevel=0)
    for y in (-.2, 1.6):
        K.chamfer_box(a.part('Rescue_buoys', 'Hazard'), (1.6, 1.0, .12), loc=(-2.6, y, T_DECK + .05), c=.03)
    for (x, y) in ((1.8, 15.5), (-1.8, 15.5), (0, 18.0)):
        K.grille(a, (x, y, T_DECK + .03), 1.2, .8, facing=(0, 0, 1), slats=5, frame_mat='Armor')
    k.ring(a.part('Rope_coil', 'Canvas'), [(.25, 0), (.45, 0), (.45, .12), (.25, .12)], loc=(2.0, -20.0, T_DECK), seg=10)
    # Bow planes (retracted into the casing sides), the chin sonar dome on Part_sonar.
    for s in (-1, 1):
        K.wing(a.part('Bow_planes', 'Armor'), (-21.8, 1.8), (-21.3, 1.2), 1.4, x0=5.25, z=1.0, t=.12, sides=(s,))
    ps = a.pivot('Part_sonar', (0, -26.0, 1.2))
    k.lathe(a.part('Sonar_dome', 'Armor', ps), [(0, -1.0), (1.5, -.8), (2.0, 0), (1.6, .9), (0, 1.1)],
            loc=(0, .4, -1.6), rot=K.FORWARD, seg=14)
    a.part('Sonar_band', 'Hazard', ps).cyl(1.95, .2, loc=(0, .3, -1.6), rot=K.FORWARD, seg=14, bevel=0)
    a.part('Sonar_emitter', 'Glass', ps).box((1.4, .05, .6), loc=(0, -.62, -1.6), bevel=0)
    K.tone(a, 'Part_sonar', k=.85)
    _typhon_silo(a)
    _typhon_sail(a)
    _typhon_stern(a)
    _typhon_gun(a)
    k.clean(a)


def _typhon_silo(a):
    """The missile deck forward of the sail: a raised flat hump, 20 tube doors in two rows of ten, each door on its
    hinge with a rim; the left row on Part_doors_l, the right on Part_doors_r (breakable)."""
    hump = a.part('Missile_hump', 'Obsidian')
    W.poly_turret(hump, [(T_DECK - .05, [(-3.4, -17.0), (3.4, -17.0), (3.4, -1.0), (-3.4, -1.0)]),
                         (T_DECK + .55, [(-3.1, -16.6), (3.1, -16.6), (3.1, -1.3), (-3.1, -1.3)])], chamfer=.06)
    for i, (s, nm) in enumerate(((1, 'Part_doors_l'), (-1, 'Part_doors_r'))):
        p = a.pivot(nm, (s * 1.6, -9.0, T_DECK + .55))
        lids = a.part(f'Doors_{nm[5:]}', 'Team', p)
        rims = a.part(f'Doors_rim_{nm[5:]}', 'Steel', p)
        hinges = a.part(f'Doors_hinge_{nm[5:]}', 'Steel', p)
        for j in range(10):
            y = -6.75 + j * 1.5
            k.lathe(rims, [(.62, -.02), (.7, -.02), (.7, .06), (.62, .06)], loc=(0, y, 0), seg=14)
            k.lathe(lids, [(0, .12), (.5, .1), (.62, .05), (.62, .02)], loc=(0, y, 0), seg=14)
            hinges.box((.12, .3, .12), loc=(s * .72, y, .06), bevel=0)
        K.tone(a, nm, k=.88)


def _typhon_sail(a):
    """The long low sail (Part_sail) aft of the silo: a streamlined fin with the ice-breaking rounded top, the
    bridge windows, the mast and periscope stubs, the snorkel head, and the SAM post on its top (Mount_missile)."""
    p = a.pivot('Part_sail', (0, 4.0, 3.6))
    body = a.part('Sail_body', 'Armor', p)
    rings = []
    for z, sc in ((.1, 1.0), (4.5, .97), (6.6, .88), (7.0, .7)):
        pts = [(-1.6 * sc, -3.2 * sc), (-1.3 * sc, -4.4 * sc), (0, -5.0 * sc), (1.3 * sc, -4.4 * sc),
               (1.6 * sc, -3.2 * sc), (1.5 * sc, 2.5 * sc), (.8 * sc, 4.6 * sc), (0, 5.0 * sc), (-.8 * sc, 4.6 * sc),
               (-1.5 * sc, 2.5 * sc)]
        rings.append((z, pts))
    W.poly_turret(body, rings, chamfer=.06)
    top = a.part('Sail_top', 'Team', p)
    top.box((2.2, 6.0, .1), loc=(0, -.5, 7.0), bevel=0)
    win = a.part('Sail_windows', 'Glass', p)
    for s in (-1, 1):
        for j in range(3):
            win.box((.02, .5, .3), loc=(s * 1.32, -3.2 + j * .6, 6.4), bevel=0)
    win.box((1.6, .02, .3), loc=(0, -4.35, 6.5), rot=(-.4, 0, 0), bevel=0)
    masts = a.part('Sail_masts', 'Steel', p)
    for (y, h, r) in ((-.6, .6, .16), (.2, .9, .13), (1.0, .7, .2), (1.9, .5, .24)):
        k.lathe(masts, [(r, 7.0), (r, 7.0 + h), (r * 1.3, 7.0 + h + .05), (r * 1.3, 7.0 + h + .35), (0, 7.0 + h + .4)],
                loc=(0, y, 0), seg=8)
    a.part('Sail_planes', 'Armor', p).box((.6, 1.4, .5), loc=(0, 3.4, 6.8), bevel=0)
    for sx in (-1, 1):
        K.ladder(a.part('Railings', 'Steel', p), (sx * 1.6, 1.5, .2), (sx * 1.55, 1.5, 6.9), width=.45, step=.35)
        k.ring(a.part('Life_rings', 'BarrelRed', p), [(.28, -.05), (.4, -.05), (.4, .05), (.28, .05)],
               loc=(sx * 1.58, -1.0, 5.6), rot=(0, R90, 0), seg=10)
    K.railing(a.part('Railings', 'Steel', p), [(-1.0, -4.0, 7.05), (1.0, -4.0, 7.05), (1.2, 2.0, 7.05),
                                               (-1.2, 2.0, 7.05), (-1.0, -4.0, 7.05)], h=.9, post=.9, r=.025)
    for s in (-1, 1):
        K.lamp(a, (s * .5, -4.6, 6.4), (0, -1, 0), r=.12, parent=p, guard=False)
    m = a.pivot('Mount_missile', (0, -2.6, 7.05), p)
    k.lathe(a.part('R_base_Mount_missile', 'Armor', m), [(.45, -.4), (.45, .1), (.3, .2), (0, .2)], seg=10)
    K.chamfer_box(a.part('R_box_Mount_missile', 'Team', m), (1.2, 1.6, .7), loc=(0, -.2, .6), rot=(-.3, 0, 0), c=.05)
    tb = a.part('R_tubes_Mount_missile', 'Undercarriage', m)
    for dx in (-.3, .3):
        for dz in (-.15, .15):
            tb.cyl(.13, .02, loc=(dx, -.98, .85 + dz), rot=_lift(.3), seg=8, bevel=0)
    a.pivot('Muzzle_missile', (0, -.95, .85), m)
    K.tone(a, 'Part_sail', k=.92)


def _typhon_stern(a):
    """Part_rudder: the cruciform stern, the upper rudder with the towed-array pod, the stern planes with their end
    fins, the twin seven-blade screws in their shrouds."""
    p = a.pivot('Part_rudder', (0, 27.0, 1.0))
    fins = a.part('Rudder_fins', 'Armor', p)
    K.fin(fins, (-3.0, 4.0), (-1.2, 2.6), 4.6, z0=.2, t=.12)
    K.fin(fins, (-3.0, 3.6), (-1.6, 2.4), -3.2, z0=-.2, t=.12)
    K.wing(fins, (-3.5, 4.0), (-2.0, 2.4), 3.6, x0=.6, z=-.1, t=.1)
    for s in (-1, 1):
        fins.box((.12, 2.2, 1.6), loc=(s * 4.2, -1.8, -.1), bevel=0)
    k.lathe(a.part('Rudder_pod', 'Armor', p), [(0, -1.0), (.35, -.8), (.35, 1.2), (0, 1.5)], loc=(0, -.2, 4.8),
            rot=(-R90, 0, 0), seg=10)
    for s in (-1, 1):
        x = s * 2.4
        k.ring(a.part('Screw_shrouds', 'Armor', p), [(1.25, -1.0), (1.45, -.9), (1.45, .7), (1.25, .8)],
               loc=(x, -2.8, -.3), rot=K.FORWARD, seg=16)
        sc = a.part('Screws', 'Steel', p)
        for j in range(7):
            u = j * TAU / 7
            sc.box((.35, .06, 1.15), loc=(x + math.cos(u) * .65, -2.8, -.3 + math.sin(u) * .65),
                   rot=(.35, -u + R90, 0), bevel=0, taper=(.5, 1))
        k.lathe(a.part('Screw_hubs', 'Steel', p), [(0, -.7), (.4, -.5), (.4, .5), (0, .8)], loc=(x, -2.8, -.3),
                rot=(-R90, 0, 0), seg=10)
    K.tone(a, 'Part_rudder', k=.9)


def _typhon_gun(a):
    """A deck gun on the forecasing (the game's addition: the def's 57 / 100 mm), on Mount_gun: a low turret, one
    barrel (mb_fix_barrels makes the pair)."""
    k.ring(a.part('Turret_rings', 'Steel'), [(1.1, -.05), (1.25, -.05), (1.25, .12), (1.1, .12)],
           loc=(0, -19.5, T_DECK), seg=16)
    m = a.pivot('Mount_gun', (0, -19.5, T_DECK))
    house = a.part('Gun_house_gun', 'Armor', m)
    W.poly_turret(house, [(0, [(-1.1, -1.2), (1.1, -1.2), (1.2, .5), (.8, 1.3), (-.8, 1.3), (-1.2, .5)]),
                          (1.1, [(-.75, -.9), (.75, -.9), (.85, .4), (.55, 1.05), (-.55, 1.05), (-.85, .4)])],
                  chamfer=.06)
    K.chamfer_box(a.part('Gun_armor_gun', 'Team', m), (.6, .4, .5), loc=(0, -1.25, .52), c=.04)
    K.gun_barrel(a, 'Gun_barrel_gun', m, 0, -1.4, .52, 3.76, .1, seg=12, extractor=(.45, 1.5, .4),
                 brake_name='Gun_brake_gun', brake='collar')
    K.periscope(a, (.45, .3, 1.1), facing=(0, -1, 0), parent=m, size=(.24, .22, .2))
    a.pivot('Muzzle_gun', (0, -5.3, .52), m)


# ============================================================================= caspian
def caspian(a):
    """Lun-class ekranoplan (MD-160, 'the Caspian Sea Monster'): the long boat hull with its planing step and chines,
    the cockpit (Bridge) and the dorsal spine, the eight turbofans on the canard pylon behind the cockpit
    (Part_engines), the short low wings with end-plate floats and flaps (Part_wing_l / _r), the huge T-tail, the
    six Moskit canisters in pairs on the spine (Part_launcher), the six-barrel CIWS aft (Mount_gun), two ZU-23-2
    turrets on the spine (Mount_mg / .001; the def's two zu23, two barrels each). Runtime: Part_engines,
    Part_launcher, Part_wing_l, Part_wing_r, Mount_gun / Muzzle_gun, Mount_mg[.001] / Muzzle_mg[.001] with the
    per-barrel Muzzle_b1 / b2_mg[_001]."""
    K.suffixed(a)
    hull = a.part('Hull', 'Team')
    st = []
    for y, w, top, bot in ((-26.8, .3, 3.4, 3.0), (-25.8, 1.4, 4.6, 1.6), (-23.0, 2.4, 6.0, .9), (-16.0, 2.8, 6.9, .6),
                           (0.0, 2.9, 7.0, .5), (12.0, 2.7, 6.8, .9), (20.0, 2.0, 6.4, 2.0), (26.0, .5, 6.1, 4.8)):
        zc, h = (top + bot) / 2, (top - bot) / 2
        st.append((y, K.ellipse_half(w, h, zc, n=12, flat=.25)))
    K.section_loft(hull, st)
    _caspian_fittings(a)
    # Chines along the bottom, the planing step under the wing, the keel; dark bottom paint below the chine.
    ch = a.part('Hull_chines', 'Armor')
    for s in (-1, 1):
        ch.tube([(s * 1.9, -24.0, 1.5), (s * 2.7, -16.0, 1.0), (s * 2.8, 0.0, .95), (s * 2.6, 12.0, 1.3),
                 (s * 1.9, 20.0, 2.3)], .16, seg=5)
    a.part('Planing_step', 'Armor').box((5.0, .5, .5), loc=(0, 3.5, .7), bevel=0)
    a.part('Hull_bottom', 'Undercarriage').box((3.0, 30.0, .1), loc=(0, -5.0, .52), bevel=0)
    for s in (-1, 1):
        a.part('Side_stripe', 'Team').box((.04, 34.0, .5), loc=(s * 2.86, -3.0, 4.2), bevel=0)
        win = a.part('Portholes', 'Glass')
        for j in range(18):
            win.cyl(.18, .05, loc=(s * 2.86, -14.0 + j * 1.4, 5.3), rot=ACROSS, seg=8, bevel=0)
        hp = a.part('Hull_panels', 'Armor')
        for j in range(8):
            if j % 2:
                continue
            hp.box((.04, 3.6, 1.6), loc=(s * 2.84, -14.0 + j * 4.0, 2.7), rot=(0, s * .2, 0), bevel=0)
        for j in range(6):
            a.part('Hull_strakes', 'Steel').box((.12, 2.0, .1), loc=(s * 2.3, -20.0 + j * 4.0, 1.0), bevel=0)
    # The cockpit glazing on the nose (Bridge), the radome, the dorsal spine, the canards on the nose.
    br = a.part('Bridge', 'Team')
    W.poly_turret(br, [(5.6, [(-2.2, -23.6), (2.2, -23.6), (2.4, -19.0), (-2.4, -19.0)]),
                       (7.3, [(-1.6, -22.6), (1.6, -22.6), (1.8, -19.4), (-1.8, -19.4)])], chamfer=.08)
    cg = a.part('Cockpit', 'Glass')
    cg.box((3.0, .04, .8), loc=(0, -23.1, 6.45), rot=(-.55, 0, 0), bevel=0)
    for s in (-1, 1):
        cg.box((.04, 2.4, .6), loc=(s * 2.25, -21.2, 6.5), rot=(0, s * .3, 0), bevel=0)
    k.lathe(a.part('Radome', 'PlasterWhite'), [(0, -.8), (.9, -.5), (1.0, .3), (.7, .8)], loc=(0, -26.4, 3.3),
            rot=K.FORWARD, seg=12)
    spine = a.part('Launcher_fairing', 'Armor')
    W.poly_turret(spine, [(6.8, [(-1.6, -15.0), (1.6, -15.0), (1.6, 16.0), (-1.6, 16.0)]),
                          (7.6, [(-1.2, -14.0), (1.2, -14.0), (1.2, 15.0), (-1.2, 15.0)])], chamfer=.06)
    K.wing(a.part('Canards', 'Team'), (-24.6, 2.2), (-24.0, 1.3), 2.4, x0=2.0, z=4.0, t=.1)
    _caspian_engines(a)
    _caspian_wings(a)
    _caspian_tail(a)
    _caspian_weapons(a)
    k.clean(a)


def _caspian_fittings(a):
    """Hull fittings: crew hatches on the top, the boarding doors' outlines on both sides, blade antennas on the
    spine, mooring bollards and the searchlight on the nose deck, life-raft canisters behind the cockpit."""
    for y in (-14.5, -6.0, 18.0):
        K.hatch_rect(a, (0, y, 7.0), size=(.9, 1.1), normal=(0, 0, 1))
    for s in (-1, 1):
        dl = a.part('Door_lines', 'Undercarriage')
        for y in (-17.0, 9.0):
            dl.box((.04, 1.2, .05), loc=(s * 2.88, y, 5.9), bevel=0)
            dl.box((.04, 1.2, .05), loc=(s * 2.88, y, 3.9), bevel=0)
            dl.box((.04, .05, 2.0), loc=(s * 2.88, y - .6, 4.9), bevel=0)
            dl.box((.04, .05, 2.0), loc=(s * 2.88, y + .6, 4.9), bevel=0)
        for y in (-25.0, -23.6):
            a.part('Bollards', 'Steel').cyl(.14, .4, loc=(s * .9, y, 4.85), seg=8, bevel=0)
    for j in range(5):
        K.blade_antenna(a.part('Antennas', 'Steel'), (0, -12.0 + j * 6.0, 7.6), h=.5, chord=.4)
    K.floodlight(a, (0, -24.4, 4.85), facing=(0, -1, -.1), pole=.5)
    # Access panels of their own sizes along the upper hull (avionics, fuel, hydraulics bays), vents beside the spine.
    ap = a.part('Access_panels', 'Armor')
    for j, (y, w, l) in enumerate(((-15.5, .9, 1.2), (-11.0, 1.1, .8), (-8.5, .7, 1.5), (-3.5, 1.3, 1.0),
                                    (1.5, .8, .9), (5.0, 1.0, 1.6), (8.0, .6, .7), (11.5, 1.2, 1.3))):
        for s in (-1, 1):
            ap.box((w, l, .03), loc=(s * 2.05, y + s * .3, 6.62), rot=(0, s * .5, 0), bevel=0)
    for j, (y, w) in enumerate(((-9.5, .6), (-1.0, .9), (6.5, .5))):
        for s in (-1, 1):
            K.grille(a, (s * 1.75, y, 6.95), w, w * .8, facing=(s * .3, 0, 1), slats=3, frame_mat='Armor')
    for j in range(4):
        k.lathe(a.part('Life_rafts', 'PlasterWhite'), [(.3, -.5), (.32, -.45), (.32, .45), (.3, .5)],
                loc=((j - 1.5) * .75, -17.6, 7.15), rot=K.FORWARD, seg=8)


def _caspian_engines(a):
    """Part_engines: the canard pylon behind the cockpit carrying four NK-87-class turbofans a side side by side,
    their intakes forward, nozzles angled down to blow under the wing."""
    p = a.pivot('Part_engines', (0, -18.0, 5.4))
    K.wing(a.part('Engine_pylon', 'Team', p), (-1.6, 4.6), (-.6, 3.0), 6.8, x0=2.4, z=.2, t=.14, dihedral=.05)
    jets = a.part('Jets', 'Armor', p)
    intk = a.part('Jet_intakes', 'Undercarriage', p)
    glow = a.part('Jet_glow', 'LavaGlow', p)
    for s in (-1, 1):
        for j in range(4):
            x = s * (3.4 + j * 1.45)
            k.lathe(jets, [(.55, -2.6), (.68, -2.3), (.7, 1.0), (.55, 2.2), (.45, 2.4)], loc=(x, 0, 1.1),
                    rot=(R90 + .08, 0, 0), seg=16)
            intk.cyl(.52, .05, loc=(x, -2.62, 1.1 + .2), rot=K.FORWARD, seg=16, bevel=0)
            k.lathe(a.part('Jet_spinners', 'Steel', p), [(.2, 0), (.15, .3), (0, .45)], loc=(x, -2.55, 1.3),
                    rot=K.FORWARD, seg=10)
            a.part('Jet_cowl_lines', 'Undercarriage', p).cyl(.71, .06, loc=(x, -.6, 1.15), rot=(R90 + .08, 0, 0),
                                                             seg=16, bevel=0)
            glow.cyl(.4, .05, loc=(x, 2.42, 1.1 - .2), rot=K.FORWARD, seg=10, bevel=0)
    K.tone(a, 'Part_engines', k=.86)


def _caspian_wings(a):
    """Part_wing_l / _r: the short thick low wing, the flaps, the end-plate float, a hazard stripe and the faction
    mark on it."""
    for s, nm in ((1, 'Part_wing_l'), (-1, 'Part_wing_r')):
        p = a.pivot(nm, (s * 11.0, 0.0, 2.6))
        w = a.part(f'Wing_{nm[5:]}', 'Team', p)
        K.wing(w, (-6.0, 13.0), (-2.5, 8.0), 14.2, x0=-8.2, z=0, t=.13, sides=(s,))
        fl = a.part(f'Wing_flaps_{nm[5:]}', 'Armor', p)
        for j in range(3):
            fl.box((1.9, 1.4, .18), loc=(s * (-7.2 + j * 2.0), 6.6 - j * .4, -.2), rot=(.25, 0, 0), bevel=0)
        fw = a.part(f'Float_{nm[5:]}', 'Armor', p)
        fw.box((.5, 9.0, 3.4), loc=(s * 8.2, .8, -.5), bevel=.1, taper=(1, .7))
        k.lathe(fw, [(0, -2.0), (.6, -1.4), (.8, 2.0), (.5, 4.0), (0, 4.4)], loc=(s * 8.2, .3, -1.9),
                rot=(-R90, 0, 0), seg=10)
        a.part(f'Wing_mark_{nm[5:]}', 'Hazard', p).box((.4, 8.0, .02), loc=(s * 6.6, 1.5, .55), bevel=0)
        wp = a.part(f'Wing_panels_{nm[5:]}', 'Armor', p)
        for j in range(4):
            for r in range(2):
                if (j + r) % 2:
                    continue
                xx = s * (-6.8 + j * 3.2)
                wp.box((2.8, 2.6, .03), loc=(xx, -2.0 + r * 3.0 + j * .5, .62 - abs(j) * .02), bevel=0)
        sd = a.part(f'Static_dischargers_{nm[5:]}', 'Steel', p)
        for j in range(6):
            sd.box((.04, .5, .04), loc=(s * (-6.0 + j * 2.3), 7.2 - j * .45, .0), bevel=0)
        for xx in (-4.0, 1.0):
            a.part(f'Wing_fences_{nm[5:]}', 'Armor', p).box((.06, 7.0, .45), loc=(s * xx, .8, .45), bevel=0)
        for j in range(3):
            a.part(f'Flap_tracks_{nm[5:]}', 'Armor', p).box((.35, 1.6, .4), loc=(s * (-6.2 + j * 2.0), 6.6, -.45),
                                                            bevel=0, taper=(.6, .6))
        a.part(f'Nav_light_{nm[5:]}', 'LavaGlow' if s > 0 else 'SignalGreen', p).box((.2, .4, .2),
                                                                                      loc=(s * 8.5, -3.2, 1.2),
                                                                                      bevel=0)
        K.tone(a, nm, k=.9)


def _caspian_tail(a):
    """The huge swept fin with its rudder line, the T-tail stabiliser with elevators, the fin mark."""
    tf = a.part('Tail_fin', 'Team')
    K.fin(tf, (14.0, 11.0), (21.5, 4.6), 9.4, z0=6.6, t=.11)
    a.part('Fin_mark', 'Team').box((.03, 2.0, 1.4), loc=(.35, 20.5, 12.5), bevel=0)
    st = a.part('Stabiliser', 'Team')
    K.wing(st, (20.6, 5.2), (23.2, 2.8), 8.6, x0=.3, z=15.8, t=.1)
    a.part('Elevators', 'Armor').box((15.0, .9, .18), loc=(0, 25.3, 15.8), bevel=0)
    a.part('Rudder_line', 'Armor').box((.25, .6, 7.0), loc=(0, 25.0, 11.8), rot=(-.55, 0, 0), bevel=0)
    K.beacon(a, (0, 25.8, 16.3), r=.2)


def _caspian_weapons(a):
    """Part_launcher: three pairs of Moskit canisters on the spine, their caps; the CIWS aft on Mount_gun; two
    ZU-23-2 turrets on the spine."""
    p = a.pivot('Part_launcher', (0, 2.0, 6.4))
    can = a.part('Launch_canisters', 'Armor', p)
    caps = a.part('Canister_caps', 'Hazard', p)
    e = .12
    for j in range(3):
        y0 = -9.0 + j * 7.0
        for s in (-1, 1):
            x = s * .95
            k.lathe(can, [(.62, 0), (.66, .1), (.66, 6.2), (.62, 6.3)], loc=(x, y0 + 6.0, 1.6), rot=_lift(e), seg=12)
            caps.cyl(.6, .06, loc=(x, y0 + 6.0 - 6.32 * math.cos(e), 1.6 + 6.32 * math.sin(e)), rot=_lift(e), seg=12,
                     bevel=0)
        cr = a.part('Canister_cradles', 'Steel', p)
        for yy in (y0 + 1.0, y0 + 4.5):
            cr.box((2.6, .3, 1.6), loc=(0, yy, 1.0), bevel=0)
        bands = a.part('Canister_bands', 'Steel', p)
        for s in (-1, 1):
            for f in (1.2, 3.1, 5.0):
                q = Vector((s * .95, y0 + 6.0, 1.6)) + Vector((0, -math.cos(e), math.sin(e))) * f
                bands.cyl(.7, .12, loc=tuple(q), rot=_lift(e), seg=12, bevel=0)
    K.tone(a, 'Part_launcher', k=.9)
    # CIWS aft on the spine.
    k.lathe(a.part('CIWS_ring_gun', 'Steel'), [(.8, 0), (.8, .15), (.6, .2), (0, .2)], loc=(0, 17.0, 6.2), seg=14)
    m = a.pivot('Mount_gun', (0, 17.0, 6.4))
    W.poly_turret(a.part('CIWS_body_gun', 'Team', m), [(0, [(-.6, -.55), (.6, -.55), (.7, .2), (.5, .75), (-.5, .75),
                                                          (-.7, .2)]),
                                                     (1.0, [(-.4, -.4), (.4, -.4), (.5, .15), (.35, .6), (-.35, .6),
                                                            (-.5, .15)])], chamfer=.05)
    k.lathe(a.part('CIWS_barrels_gun', 'Steel', m), [(.16, 0), (.16, 1.9), (0, 1.92)], loc=(0, -.5, .62),
            rot=K.FORWARD, seg=10)
    k.lathe(a.part('CIWS_dark_gun', 'PlasterWhite', m), [(.3, 0), (.32, .18), (.2, .34), (0, .38)],
            loc=(.35, .25, 1.0), seg=10)
    a.pivot('Muzzle_gun', (0, -2.67, .62), m)
    # Two ZU-23-2 turrets on the spine, two barrels each, a muzzle per barrel.
    for i, y in enumerate((-12.0, 13.0)):
        k.ring(a.part('Zu_rings', 'Steel'), [(.55, 0), (.7, 0), (.7, .15), (.55, .15)], loc=(0, y, 7.55), seg=12)
        m = a.pivot(K.name('Mount_mg', i), (0, y, 7.7))
        W.poly_turret(a.part(K.name('Zu_turret', i), 'Team', m),
                      [(0, [(-.7, -.6), (.7, -.6), (.75, .5), (-.75, .5)]),
                       (.7, [(-.5, -.4), (.5, -.4), (.55, .4), (-.55, .4)])], chamfer=.04)
        g = a.part(K.name('Zu_guns', i), 'Steel', m)
        for x in (-.2, .2):
            k.lathe(g, [(.05, 0), (.05, 2.2), (.07, 2.22), (.07, 2.45), (0, 2.46)], loc=(x, -.5, .4),
                    rot=K.FORWARD, seg=8)
        mz = a.pivot(K.name('Muzzle_mg', i), (0, -2.96, .4), m)
        suf = '' if i == 0 else '_001'
        a.pivot(f'Muzzle_b1_mg{suf}', (-.2, 0, 0), mz)
        a.pivot(f'Muzzle_b2_mg{suf}', (.2, 0, 0), mz)


BUILDERS = {
    'monster': (monster, dict(ao_distance=1.6, grime_height=1.6)),
    'landing_hovercraft': (landing_hovercraft, dict(ao_distance=1.0, grime_height=2.2)),
    'typhon': (typhon, dict(ao_distance=1.0, grime_height=2.5)),
    'caspian': (caspian, dict(ao_distance=1.0, grime_height=2.0)),
}
