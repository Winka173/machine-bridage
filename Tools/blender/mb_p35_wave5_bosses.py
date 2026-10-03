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


BUILDERS = {
    'monster': (monster, dict(ao_distance=1.6, grime_height=1.6)),
}
