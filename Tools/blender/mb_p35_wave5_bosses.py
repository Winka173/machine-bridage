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
        W.poly_turret(tier, [(H_DECK, [(s * 4.1, -3.5), (s * 6.9, -3.5), (s * 6.9, 2.5), (s * 4.1, 2.5)]),
                             (H_DECK + 1.3, [(s * 4.4, -3.0), (s * 6.6, -3.0), (s * 6.6, 2.2), (s * 4.4, 2.2)])],
                      chamfer=.06)
        # Gas-turbine exhausts aft of the tier, louvred vent boxes, deck hatches.
        for j, y in enumerate((-9.6, -5.0, 9.6)):
            K.hatch_rect(a, (s * 5.0, y, H_DECK), size=(.7, .9), normal=(0, 0, 1))
        K.exhaust(a, (s * 6.4, 9.6, H_DECK), r=.35, length=1.3, direction=(0, .3, 1), muffler=False)
        K.exhaust(a, (s * 4.6, 9.6, H_DECK), r=.35, length=1.3, direction=(0, .3, 1), muffler=False)
        for y in (-1.8, .6):
            K.grille(a, (s * 4.08, y, H_DECK + .6), 1.4, .6, facing=(-s, 0, 0), slats=4, frame_mat='Armor')
        win = a.part('Cabin_glass', 'Glass')
        for j in range(5):
            win.box((.02, .7, .45), loc=(s * 6.91, -2.8 + j * 1.15, H_DECK + .8), bevel=0)
            win.box((.02, .7, .45), loc=(s * 4.09, -2.8 + j * 1.15, H_DECK + .8), bevel=0)
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
    W.poly_turret(cab, [(H_DECK + 1.3, [(3.9, -9.6), (7.1, -9.6), (7.1, -6.4), (3.9, -6.4)]),
                        (H_DECK + 2.6, [(4.1, -9.0), (6.9, -9.0), (6.9, -6.6), (4.1, -6.6)])], chamfer=.06)
    K.chamfer_box(cab, (3.2, 3.2, 1.3), loc=(5.5, -8.0, H_DECK + .65), c=.06)
    win = a.part('Cabin_glass', 'Glass')
    win.box((2.6, .02, .5), loc=(5.5, -9.32, H_DECK + 1.95), rot=(-.43, 0, 0), bevel=0)
    for s in (-1, 1):
        win.box((.02, 1.8, .45), loc=(5.5 + s * 1.5, -7.8, H_DECK + 1.95), bevel=0)
    # Mast with the radar dome, antennas, the beacon and the APS sensor head.
    mast = a.part('Antenna', 'Steel')
    mast.cyl(.12, 2.0, loc=(5.5, -7.2, H_DECK + 3.6), seg=8, bevel=0)
    mast.box((1.8, .08, .08), loc=(5.5, -7.2, H_DECK + 4.1), bevel=0)
    k.lathe(a.part('Radar_dome', 'PlasterWhite'), [(.5, 0), (.55, .25), (.35, .55), (0, .62)],
            loc=(5.5, -7.2, H_DECK + 4.55), seg=12)
    K.whip_antenna(a.part('Antenna', 'Steel'), (4.3, -6.7, H_DECK + 2.6), h=1.6)
    K.beacon(a, (6.8, -6.8, H_DECK + 2.6), r=.15)
    K.chamfer_box(a.part('Mast_lights', 'Armor'), (.5, .5, .4), loc=(4.4, -8.9, H_DECK + 2.8), c=.04)
    K.radar_mast(a, (-5.5, -8.4, H_DECK), h=3.4)
    a.pivot('Mount_APS', (4.4, -8.9, H_DECK + 3.0))
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


BUILDERS = {
    'monster': (monster, dict(ao_distance=1.6, grime_height=1.6)),
    'landing_hovercraft': (landing_hovercraft, dict(ao_distance=1.0, grime_height=2.2)),
}
