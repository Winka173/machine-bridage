"""Prompt 35 wave 8 (lane A): the ground, sea and rail bosses rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library and mb_p35_w5parts. DECISIONS "Prompt 35 wave 8 (lane A)".
Every boss keeps its def's part nodes (the variant bosses behemoth_mk0, fenrir and scylla hide the parts they drop by
these nodes) and its mounts' places; the guns that fire their barrels together carry their per-barrel muzzles
(Muzzle_b<k>_<tag>) from these builders, so mb_fix_barrels / mb_p34_barrels no longer touch these models.

- behemoth: the land battleship (Object 279's four tracks and flat hull, Baneblade's read): two track units a side
  under armoured skirts, the wide low hull with the sloped glacis and the hull gun turret, the main turret with the
  twin 152 mm in one mantlet, two flak mounts on its roof, APS radar panels and launcher clusters (Mount_APS), the
  two sponson turrets with twin 120 mm over the outer tracks, the rocket box on the engine deck, the missile racks
  on the hull sides, the engine deck with its grilles and exhausts.

Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= shared lean helpers
def per_barrel(a, muzzle, tag, xs):
    """Muzzle_b<k>_<tag> under the pivot `muzzle`, one per barrel at the x offsets `xs` (left to right)."""
    for i, x in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, 0), muzzle)


def twin_turret(a, mount, slot, index, loc, length, r, gap, parent=None, house=(1.6, 2.0, .8), mat='Team',
                brake='baffle', ring=1.0, sight=True, prefix='T'):
    """A small gun turret on its yaw pivot Mount_<slot>[.NNN]: the ring, the faceted house, the mantlet, two barrels
    `gap` apart (sleeve, extractor, brake), the sight and the hatch; Muzzle_<slot>[.NNN] between the barrel tips
    and the per-barrel muzzles. Returns the pivot."""
    m = a.pivot(K.name(mount, index), loc, parent)
    tag = f'_{mount}_{index:03d}' if index else f'_{mount}'
    hw, hd_, hh = house
    k.lathe(a.part(f'{prefix}_ring{tag}', 'Steel', m), [(ring, -.05), (ring * 1.04, 0), (ring * 1.04, .1),
                                                        (ring * .98, .12)], seg=16)
    W.poly_turret(a.part(f'{prefix}_house{tag}', mat, m), [
        (.1, [(-hw * .3, -hd_ * .5), (hw * .3, -hd_ * .5), (hw * .5, -hd_ * .2), (hw * .5, hd_ * .5),
              (-hw * .5, hd_ * .5), (-hw * .5, -hd_ * .2)]),
        (hh, [(-hw * .24, -hd_ * .4), (hw * .24, -hd_ * .4), (hw * .42, -hd_ * .14), (hw * .42, hd_ * .45),
              (-hw * .42, hd_ * .45), (-hw * .42, -hd_ * .14)])], chamfer=.04)
    zg = hh * .55
    K.chamfer_box(a.part(f'{prefix}_armor{tag}', 'Armor', m), (gap + r * 5, .35, hh * .7), loc=(0, -hd_ * .5, zg),
                  c=.04)
    for x in (-gap / 2, gap / 2):
        K.gun_barrel(a, f'{prefix}_barrel{tag}', m, x, -hd_ * .5 - .15, zg, length - .3, r, seg=10,
                     extractor=(.4, 1.45, length * .1), brake_name=f'{prefix}_brake{tag}', brake=brake)
    mz = a.pivot(K.name(f'Muzzle_{slot}', index), (0, -hd_ * .5 - .15 - length, zg), m)
    per_barrel(a, mz, f'{slot}_{index:03d}' if index else slot, (-gap / 2, gap / 2))
    if sight:
        K.chamfer_box(a.part(f'{prefix}_sight{tag}', 'Armor', m), (.24, .3, .22), loc=(hw * .28, -hd_ * .1, hh + .1),
                      c=.02)
        a.part(f'{prefix}_glass{tag}', 'Glass', m).box((.16, .01, .1), loc=(hw * .28, -hd_ * .1 - .155, hh + .12),
                                                     bevel=0)
    return m


# ============================================================================= behemoth
def behemoth(a):
    """See the module docstring. Runtime (the def's parts): Main_cannon / Main_cannon_2 / Muzzle_brake / _2 (main_gun),
    Mount_gun (gun_120), Mount_mg / .001 (flak_r / flak_l, on the turret), Mount_gun.001 / .002 (side_gun_l / _r),
    Mount_rocket (rocket_pod), Mount_APS (aps); Turret, Muzzle_main, Muzzle_missile / .001; per-barrel muzzles."""
    K.suffixed(a)
    # Four track units: two a side, the inner pair under the hull, the outer pair under the sponsons.
    wheels = [-4.6 + i * 1.05 for i in range(9)]
    for tx in (2.2, 3.45):
        W.running_gear(a, tx, .95, .45, wheels, (-5.55, .66, .4), (5.25, .7, .42), rollers=(-2.5, 0, 2.5),
                       roller_z=1.15, top_hidden=1.05, disc_mat='Armor', seg=8, link_pitch=.5, wheel_w=.24, dust=.22)
    hull = a.part('Hull', 'Team')
    K.section_loft(hull, [
        (-6.25, [(0, .95), (2.4, .95), (2.7, 1.25), (2.6, 1.55), (0, 1.62)]),
        (-5.0, [(0, .75), (3.0, .75), (3.45, 1.45), (3.3, 2.2), (0, 2.45)]),
        (4.9, [(0, .75), (3.0, .75), (3.45, 1.45), (3.3, 2.5), (0, 2.6)]),
        (6.0, [(0, .95), (2.8, .95), (3.1, 1.4), (3.0, 2.3), (0, 2.35)])])
    # Armoured skirts over the outer tracks with their rubber flaps; bolted side plates; the team band.
    for s in (-1, 1):
        for j in range(7):
            yc = -5.0 + (j + .5) * 1.45
            K.armour_plate(a, a.part('Skirts', 'Armor'), (1.4, .7, .08), (s * 4.0, yc, 1.25), rot=(0, s * R90, 0),
                           rivet=.45)
            a.part('Skirt_edge', 'Rubber').box((.05, 1.38, .14), loc=(s * 4.02, yc, .82), bevel=0)
        a.part('Fenders', 'Team').box((1.5, 10.4, .08), loc=(s * 3.45, -.1, 1.62), bevel=0)
        a.part('Team_band', 'Team').box((.03, 9.0, .25), loc=(s * 4.06, -.1, 1.45), bevel=0)
        K.lamp(a, (s * 2.4, -6.3, 1.4), (0, -1, .1), r=.14, guard=True)
        a.part('Tail_lights', 'LavaGlow').box((.2, .03, .1), loc=(s * 2.5, 6.05, 1.5), bevel=0)
    # Glacis: composite modules, the driver's vision blocks and hatches, the searchlight, tow hooks.
    for i in range(4):
        K.armour_plate(a, a.part('Armor', 'Armor'), (1.25, 1.0, .14), (-1.9 + i * 1.27, -5.6, 1.98),
                       rot=(-1.05, 0, 0), rivet=.4)
    for x in (-1.6, 1.6):
        K.hatch_round(a, (x, -4.6, 2.45), r=.38, periscopes=2, seg=12)
        a.part('Vision_blocks', 'Glass').box((.5, .03, .1), loc=(x, -4.98, 2.43), rot=(-.4, 0, 0), bevel=0)
    k.lathe(a.part('Searchlight', 'Armor'), [(.2, -.18), (.22, .15), (.17, .2)], loc=(2.6, -5.2, 2.5),
            rot=K.FORWARD, seg=10)
    a.part('Lamps', 'Lamp').cyl(.18, .02, loc=(2.6, -5.39, 2.5), rot=K.FORWARD, seg=10, bevel=0)
    W.tow_set(a, -6.3, 1.1, 1.5, (0, -1, 0))
    _behemoth_deck(a)
    _behemoth_turret(a)
    # The hull gun turret on the glacis (Mount_gun, gun_120), the sponson turrets (side_gun_l / _r).
    twin_turret(a, 'Mount_gun', 'gun', 0, (0, -3.45, 2.63), 2.57, .075, .34, house=(1.5, 1.6, .55))
    for i, s in ((1, 1), (2, -1)):
        sp = a.part('Sponsons', 'Armor')
        W.poly_turret(sp, [(1.62, [(s * 2.7, -2.3), (s * 4.1, -2.0), (s * 4.1, .3), (s * 2.7, .3)]),
                           (2.55, [(s * 2.8, -2.1), (s * 3.95, -1.85), (s * 3.95, .15), (s * 2.8, .15)])],
                      chamfer=.05)
        twin_turret(a, 'Mount_gun', 'gun', i, (s * 3.4, -1.0, 2.6), 3.95, .085, .48, house=(1.4, 1.8, .8), ring=.68)
    # The missile racks on the hull sides (boss_missiles, aimed with the hull).
    for i, s in enumerate((-1, 1)):
        rack = a.part('Missile_racks', 'Armor')
        K.chamfer_box(rack, (.5, 1.6, .6), loc=(s * 2.62, 2.6, 2.12), c=.04)
        for dz in (-.15, .15):
            for dx in (-.12, .12):
                a.part('Rack_box', 'Undercarriage').cyl(.08, .03, loc=(s * 2.62 + dx, 1.8, 2.12 + dz),
                                                        rot=K.FORWARD, seg=8, bevel=0)
        a.part('Rack_frames', 'Steel').box((.6, .08, .7), loc=(s * 2.62, 1.82, 2.12), bevel=0)
        a.pivot(K.name('Muzzle_missile', i), (s * 2.62, 1.9, 2.12))
    a.pivot('Point_fire', (0, 4.0, 2.7))
    a.pivot('Point_exhaust', (2.2, 5.9, 2.8))
    k.clean(a)


def _behemoth_deck(a):
    """The engine deck behind the turret: grille banks, the exhaust stacks, the rocket box on its traversing mount
    (Mount_rocket), jerrycans and spare track links on the deck edge, hatches, antennas, beacons."""
    for x in (-1.6, 1.6):
        K.grille(a, (x, 4.6, 2.6), 1.6, 1.8, facing=(0, 0, 1), slats=7, frame_mat='Team')
    a.part('Deck', 'Armor').box((5.6, 3.0, .04), loc=(0, 4.55, 2.58), bevel=0)
    for s in (-1, 1):
        K.smokestack(a, (s * 2.2, 5.6, 2.2), r=.2, h=.9, mat='Steel')
        K.crate(a.part('Jerrycans', 'Armor'), a.part('Kit_latches', 'Steel'), (.4, 1.4, .45), (s * 2.95, 3.2, 2.5),
                bands=2)
        for j in range(4):
            a.part('Spare_links', 'Undercarriage').box((.9, .22, .06), loc=(s * 2.9, -3.8 + j * .26, 2.3),
                                                       rot=(0, s * .5, 0), bevel=0)
        K.beacon(a, (s * 2.6, 5.4, 2.6), r=.12)
        K.whip_antenna(a.part('Antenna', 'Steel'), (s * 2.5, 2.2, 2.55), h=2.4, lean=.06)
    # The rocket box on the deck (Mount_rocket): the base, the box with its tube face, the elevation rams.
    k.lathe(a.part('Rocket_ring', 'Steel'), [(.9, 0), (.95, .05), (.95, .15), (.88, .18)], loc=(0, 3.8, 2.6), seg=14)
    m = a.pivot('Mount_rocket', (0, 3.8, 4.4))
    K.chamfer_box(a.part('R_base_Mount_rocket', 'Armor', m), (1.4, 1.4, .6), loc=(0, 0, -1.4), c=.05)
    box = a.part('R_box_Mount_rocket', 'Team', m)
    k.block(box, (1.8, 2.0, 1.0), loc=(0, .05, .4), rot=(.32, 0, 0), chamfer=.05)
    tubes = a.part('R_tubes_Mount_rocket', 'Undercarriage', m)
    for i in range(5):
        for j in range(3):
            tubes.cyl(.11, .04, loc=(-.64 + i * .32, -.95, .55 + j * .3 - .15), rot=(R90 + .32, 0, 0), seg=8,
                      bevel=0)
    for s in (-1, 1):
        a.part('R_rams_Mount_rocket', 'Steel', m).tube([(s * .55, .4, -1.1), (s * .5, .1, -.1)], .07, seg=8)
    a.pivot('Muzzle_rocket', (0, -1.05, .9), m)
    for (x, y) in ((-1.9, 2.4), (1.9, 2.4)):
        K.hatch_round(a, (x, y, 2.58), r=.4, periscopes=0, seg=12)
    # One-sided kit (the real thing is never symmetrical): a drum rack on the right rear deck, the tow cable coil and
    # an ammunition locker on the left, a crew ladder on the right side.
    for j in range(3):
        K.fuel_drum(a.part('Drums', 'BarrelRed'), a.part('Drum_bands', 'Steel'), (-2.85, 4.4 + j * .62, 2.45),
                    r=.27, h=.8)
    a.part('Drum_rack', 'Steel').box((.7, 2.0, .06), loc=(-2.85, 5.0, 2.42), bevel=0)
    a.part('Kit_cables', 'Steel').torus(.45, .06, loc=(2.4, -3.0, 2.68), seg=14, ring=5)
    a.part('Kit_cables', 'Steel').torus(.35, .06, loc=(2.4, -3.0, 2.78), seg=14, ring=5)
    K.crate(a.part('Ammo_locker', 'Crate'), a.part('Kit_latches', 'Steel'), (1.2, .7, .5), (1.6, -2.0, 2.62), bands=2)
    K.ladder(a.part('Ladders', 'Steel'), (4.15, 3.6, .3), (4.15, 3.6, 1.65), width=.5, step=.3)
    # Field stowage hung on the left skirts only: a rack of fuel cells and jerrycans on brackets.
    fr = a.part('Stowage_rack', 'Steel')
    fr.box((.45, 3.4, .06), loc=(-4.25, 2.2, .95), bevel=0)
    for y in (.6, 2.2, 3.8):
        fr.box((.45, .06, .6), loc=(-4.25, y, 1.25), bevel=0)
    for j in range(3):
        k.lathe(a.part('Fuel_cells', 'Armor'), [(0, -.5), (.2, -.48), (.22, -.3), (.22, .3), (.2, .48), (0, .5)],
                loc=(-4.25, 1.05 + j * 1.05, 1.22), rot=K.FORWARD, seg=10)
    K.jerrycan(a.part('Jerrycans', 'Armor'), (-4.28, 3.95, 1.0), rot=(0, 0, R90))


def _behemoth_turret(a):
    """The main turret on the Turret pivot: a long faceted house with the cheek composite blocks, the twin 152 mm in
    one broad mantlet (Main_cannon left, Main_cannon_2 right, their brakes), the two flak mounts on the roof
    (Mount_mg right, .001 left), the APS radar panels on the corners and the launcher clusters (Mount_APS), the
    commander's cupola, the sight, the bustle rack, antennas."""
    t = a.pivot('Turret', (0, .4, 3.57))
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.12), 2.2, h=.14)
    W.poly_turret(a.part('Turret_body', 'Team', t), [
        (0, [(-1.3, -2.55), (1.3, -2.55), (2.4, -1.4), (2.45, 2.0), (2.0, 2.6), (-2.0, 2.6), (-2.45, 2.0),
             (-2.4, -1.4)]),
        (.6, [(-1.2, -2.75), (1.2, -2.75), (2.5, -1.5), (2.55, 2.05), (2.1, 2.7), (-2.1, 2.7), (-2.55, 2.05),
              (-2.5, -1.5)]),
        (1.05, [(-1.0, -2.2), (1.0, -2.2), (2.1, -1.2), (2.15, 1.9), (1.8, 2.45), (-1.8, 2.45), (-2.15, 1.9),
                (-2.1, -1.2)])], chamfer=.06)
    for s in (-1, 1):
        W.poly_turret(a.part('Turret_armor', 'Armor', t), [
            (.06, [(s * 1.35, -2.6), (s * 2.42, -1.42), (s * 2.42, -.9), (s * 1.5, -1.9)]),
            (.95, [(s * 1.25, -2.62), (s * 2.5, -1.5), (s * 2.5, -.9), (s * 1.4, -1.95)])], chamfer=.02)
        # APS radar panels on the corners.
        k.block(a.part('Aps_panels', 'Armor', t), (.08, .7, .45), loc=(s * 2.35, -1.0, .78), rot=(0, 0, s * .7),
                chamfer=.015)
        k.block(a.part('Aps_panels', 'Armor', t), (.08, .7, .45), loc=(s * 2.2, 2.1, .78), rot=(0, 0, -s * .7),
                chamfer=.015)
    K.chamfer_box(a.part('Gun_mantlet', 'Armor', t), (2.0, .6, .9), loc=(0, -2.8, .5), c=.07)
    for x, cn, bn in ((-.52, 'Main_cannon', 'Muzzle_brake'), (.52, 'Main_cannon_2', 'Muzzle_brake_2')):
        K.gun_barrel(a, cn, t, x, -3.1, .5, 4.65, .13, seg=12, extractor=(.4, 1.5, .6), brake_name=bn,
                     brake='baffle')
    mz = a.pivot('Muzzle_main', (0, -8.05, .5), t)
    per_barrel(a, mz, 'main', (-.52, .52))
    # Flak mounts on the roof (Mount_mg right at x -.9, Mount_mg.001 left): twin barrels, the shield, the drum.
    for i, x in ((0, -.9), (1, .9)):
        m = a.pivot(K.name('Mount_mg', i), (x, .75, 1.03), t)
        tg = '' if i == 0 else '_001'
        k.lathe(a.part(f'AA_mount{tg}', 'Armor', m), [(.42, 0), (.42, .08), (.32, .14), (.3, .3)], seg=10)
        k.block(a.part(f'AA_mount{tg}', 'Team', m), (.75, .08, .45), loc=(0, -.35, .42), rot=(-.2, 0, 0),
                chamfer=.015)
        for dx in (-.1, .1):
            k.lathe(a.part(f'AA_guns{tg}', 'Steel', m), [(.04, 0), (.04, .25), (.03, .28), (.03, 1.35), (.04, 1.38),
                                                         (.04, 1.46), (0, 1.47)], loc=(dx, -.13, .42),
                    rot=K.FORWARD, seg=6)
        K.chamfer_box(a.part(f'AA_ammo{tg}', 'Crate', m), (.24, .4, .3), loc=(.3, .15, .4), c=.02)
        a.pivot(K.name('Muzzle_mg', i), (0, -1.6, .42), m)
    # APS launcher clusters on the roof rear (Mount_APS at their centre).
    aps = a.pivot('Mount_APS', (0, 1.9, 1.1), t)
    for s in (-1, 1):
        K.chamfer_box(a.part('Aps_cluster', 'Armor', aps), (.5, .4, .3), loc=(s * .6, 0, .1), c=.03)
        for j in range(3):
            a.part('Aps_tubes', 'Undercarriage', aps).cyl(.05, .04, loc=(s * .6 - .15 + j * .15, -.21, .12),
                                                          rot=K.FORWARD, seg=6, bevel=0)
    # Cupola, sight, hatch, bustle rack, antennas, the team panel.
    k.ring(a.part('Cupola_top', 'Armor', t), [(.38, 0), (.45, 0), (.45, .22), (.38, .22)], loc=(-1.3, .6, 1.05),
           seg=12)
    K.hatch_round(a, (1.4, .9, 1.05), r=.38, parent=t, periscopes=2, seg=10)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.4, .45, .35), loc=(1.3, -1.4, 1.2), c=.04)
    a.part('Periscope', 'Glass', t).box((.3, .01, .16), loc=(1.3, -1.63, 1.22), bevel=0)
    rk = a.part('Turret_steel', 'Steel', t)
    for z in (.3, .8):
        rk.tube([(-1.9, 2.65, z), (-1.9, 3.1, z), (1.9, 3.1, z), (1.9, 2.65, z)], .035, seg=4)
    for x in (-1.9, -.95, 0, .95, 1.9):
        rk.tube([(x, 3.1, .3), (x, 3.1, .8)], .03, seg=4)
    K.net_roll(a.part('Jerrycans', 'Canvas', t), a.part('Kit_straps', 'Undercarriage', t), (-.6, 2.85, .5),
               length=1.6, r=.2)
    K.crate(a.part('Jerrycans', 'Crate', t), a.part('Kit_latches', 'Steel', t), (.9, .4, .4), (1.0, 2.85, .3),
            bands=2)
    for x in (-1.7, 1.7):
        K.whip_antenna(a.part('Antenna', 'Steel', t), (x, 2.3, 1.05), h=1.2, lean=.15)
    a.part('Team_band', 'Team', t).box((2.6, 1.6, .02), loc=(0, .3, 1.06), bevel=0)


# ============================================================================= mobile_fortress
def mobile_fortress(a):
    """See the module docstring. Runtime (the def's parts): Main_cannon / Muzzle_brake (howitzer), Mount_rocket /
    .001 (rockets_l / _r), Mount_mg / .001 (flak_l / _r), Radar (emp), Mount_gun (howitzer_2, on the turret roof),
    Mount_missile.001 (sam); Turret, Muzzle_main, Mount_missile / Muzzle_missile (the silo, part missiles)."""
    K.suffixed(a)
    # The four crawler trucks at the corners, two track units each, their frames and jacking cylinders.
    for yc in (-5.4, 5.3):
        wheels = [yc - 1.2 + i * .8 for i in range(4)]
        for tx in (2.75, 3.85):
            W.running_gear(a, tx, .9, .36, wheels, (yc - 1.75, .5, .34), (yc + 1.72, .52, .36), rollers=(yc,),
                           roller_z=.98, top_hidden=None, disc_mat='Armor', seg=8, link_pitch=.45, wheel_w=.2,
                           dust=.2)
        for s in (-1, 1):
            K.chamfer_box(a.part('Truck_frames', 'Armor'), (2.2, 3.9, .7), loc=(s * 3.3, yc, 1.55), c=.06)
            for dy in (-1.1, 1.1):
                k.lathe(a.part('Jacks', 'Steel'), [(.24, 0), (.24, .5), (.18, .55), (.18, 1.0)],
                        loc=(s * 3.3, yc + dy, 1.85), seg=10, worn=(1,))
            a.part('Hazard_bands', 'Hazard').box((.03, 3.6, .14), loc=(s * 4.41, yc, 1.75), bevel=0)
            K.lamp(a, (s * 3.3, yc - 1.96 if yc < 0 else yc + 1.96, 1.6), (0, -1 if yc < 0 else 1, 0), r=.12,
                   guard=True, glow='Lamp' if yc < 0 else 'LavaGlow')
    # The platform: a thick lofted slab with chamfered edges, the deck plates, railings, hazard edges, ladders.
    K.section_loft(a.part('Hull', 'Team'), [
        (-7.9, [(0, 2.85), (4.0, 2.85), (4.2, 3.3), (4.0, 3.95), (0, 3.95)]),
        (-7.2, [(0, 2.65), (4.4, 2.65), (4.55, 3.2), (4.4, 4.0), (0, 4.0)]),
        (7.2, [(0, 2.65), (4.4, 2.65), (4.55, 3.2), (4.4, 4.0), (0, 4.0)]),
        (7.85, [(0, 2.85), (4.0, 2.85), (4.2, 3.3), (4.0, 3.95), (0, 3.95)])])
    dp = a.part('Deck', 'Armor')
    for col in range(2):
        for y in (-4.0, 5.0):
            K.panel(a, dp, (3.6, 1.9), (-1.95 + col * 3.9, y, 4.0), (0, 0, 1), t=.04, rivet=.5)
    for s in (-1, 1):
        K.railing(a.part('Railings', 'Steel'), [(s * 4.3, -7.0, 4.0), (s * 4.3, 7.0, 4.0)], h=.9, post=1.75, r=.035)
        a.part('Plough_stripes', 'Hazard').box((.04, 14.0, .2), loc=(s * 4.56, 0, 3.2), bevel=0)
        K.ladder(a.part('Ladders', 'Steel'), (s * 4.42, -2.6, .3), (s * 4.42, -2.6, 2.65), width=.6, step=.4)
        a.part('Team_band', 'Team').box((.03, 12.0, .3), loc=(s * 4.42, 0, 3.7), bevel=0)
    for j in range(3):
        k.lathe(a.part('Fuel_tanks', 'Armor'), [(0, -.8), (.4, -.75), (.42, -.5), (.42, .5), (.4, .75), (0, .8)],
                loc=(-3.95, -1.6 + j * 1.75, 2.2), rot=K.FORWARD, seg=10)
    for j in range(5):
        a.part('Spare_links', 'Undercarriage').box((.8, .22, .06), loc=(3.0, 1.0 + j * .26, 4.03), bevel=0)
    # Deck dressing: walkway lines, more deck plates, the ammunition stack, lifting eyes, the loading crane on the
    # left (its jib out over the side), cable runs.
    for s in (-1, 1):
        a.part('Hazard_bands', 'Hazard').box((.18, 14.0, .02), loc=(s * 3.75, 0, 4.01), bevel=0)
        for y in (-2.6, .3, 3.2):
            K.panel(a, a.part('Deck', 'Armor'), (.9, 2.6), (s * 3.85, y, 4.0), (0, 0, 1), t=.03, rivet=.4)
    for j in range(4):
        K.crate(a.part('Ammo_crates', 'Crate'), a.part('Kit_latches', 'Steel'), (.9, .6, .5),
                (3.3 - (j % 2) * 1.0, -3.9 + (j // 2) * .7, 4.25), bands=2)
    W.lifting_eyes(a.part('Kit_tow', 'Steel'), [(s * 4.1, y, 4.05) for s in (-1, 1) for y in (-6.6, 6.6)], r=.14)
    cr = a.part('Crane', 'CraneYellow')
    cr.cyl(.25, 2.2, loc=(-3.6, 3.4, 5.1), seg=10, bevel=0)
    cr.limb((-3.6, 3.4, 6.0), (-4.75, 1.6, 6.4), .2, .28, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(-4.75, 1.6, 6.3), (-4.75, 1.6, 5.0)], .03, seg=4)
    a.part('Crane_hook', 'Steel').box((.3, .3, .35), loc=(-4.75, 1.6, 4.85), bevel=0)
    W.cable(a.part('Kit_cables', 'Rubber'), [(1.2, 6.6, 4.05), (1.0, 5.0, 4.05), (.6, 4.6, 4.3)], r=.07)
    _fortress_bridge(a)
    _fortress_core(a)
    _fortress_rear(a)
    _fortress_turret(a)
    k.clean(a)


def _fortress_bridge(a):
    """The glazed command bridge on the front of the deck (the Kharkovchanka / Sandcrawler read): the raked window
    band in its frames, the roof with its sensors, the flak cupolas on the front corners (Mount_mg, .001)."""
    br = a.part('Bridge', 'Team')
    W.poly_turret(br, [(4.0, [(-2.3, -7.4), (2.3, -7.4), (2.6, -6.2), (2.6, -4.6), (-2.6, -4.6), (-2.6, -6.2)]),
                       (4.5, [(-2.3, -7.45), (2.3, -7.45), (2.6, -6.25), (2.6, -4.6), (-2.6, -4.6), (-2.6, -6.25)]),
                       (5.6, [(-1.9, -6.75), (1.9, -6.75), (2.3, -6.0), (2.3, -4.7), (-2.3, -4.7), (-2.3, -6.0)])],
                  chamfer=.05)
    # The window band: panes on the raked faces between the frames.
    for i in range(5):
        x = -1.6 + i * .8
        a.part('Windows', 'Glass').mesh([(x - .34, -7.47, 4.6), (x + .34, -7.47, 4.6), (x + .3, -6.82, 5.45),
                                         (x - .3, -6.82, 5.45)], [(0, 1, 2, 3)])
        a.part('Window_frames', 'Armor').box((.06, .1, 1.05), loc=(x + .4, -7.15, 5.02), rot=(-.85, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Windows', 'Glass').mesh([(s * 2.35, -7.2, 4.6), (s * 2.62, -6.25, 4.6), (s * 2.32, -6.0, 5.45),
                                         (s * 2.0, -6.75, 5.45)], [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
    a.part('Window_frames', 'Armor').box((4.7, .12, .1), loc=(0, -7.45, 4.55), bevel=0)
    a.part('Bridge_roof', 'Medical').box((3.6, 1.2, .04), loc=(0, -5.4, 5.62), bevel=0)
    a.part('Team_band', 'Team').box((4.4, .1, .25), loc=(0, -4.6, 5.2), bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor'), (.6, .5, .4), loc=(-1.2, -5.6, 5.8), c=.04)
    a.part('Periscope', 'Glass').box((.4, .01, .2), loc=(-1.2, -5.86, 5.82), bevel=0)
    K.whip_antenna(a.part('Antenna', 'Steel'), (1.6, -5.2, 5.6), h=2.0, lean=.05)
    K.beacon(a, (.8, -5.0, 5.6), r=.12)
    # Flak cupolas on the front corners of the deck.
    for i, s in ((0, 1), (1, -1)):
        m = a.pivot(K.name('Mount_mg', i), (s * 3.2, -6.0, 4.37))
        tg = '' if i == 0 else '_001'
        k.lathe(a.part(f'MG_cupola{tg}', 'Team', m), [(.75, -.37), (.75, -.1), (.7, .1), (.55, .35), (.3, .5),
                                                      (0, .55)], seg=14)
        k.block(a.part(f'MG_armor{tg}', 'Armor', m), (.6, .3, .4), loc=(0, -.62, .1), chamfer=.03)
        for dx in (-.1, .1):
            k.lathe(a.part(f'MG_guns{tg}', 'Steel', m), [(.04, 0), (.04, .25), (.03, .28), (.03, .95), (.045, .98),
                                                         (.045, 1.05), (0, 1.06)], loc=(dx, -.58, .24),
                    rot=K.FORWARD, seg=6)
        a.part(f'MG_glass{tg}', 'Glass', m).box((.3, .02, .1), loc=(.3, -.62, .35), rot=(-.4, 0, .3), bevel=0)
        a.pivot(K.name('Muzzle_mg', i), (0, -1.63, .24), m)


def _fortress_core(a):
    """The armoured core block in the middle of the deck carrying the turret: battered walls with the vents, the
    hatches and the ladder up, the radar mast with its EMP dish (Radar spins), the exhaust stacks either side."""
    core = a.part('Armor', 'Armor')
    k.block(core, (6.2, 7.6, 2.25), loc=(0, .3, 5.12), chamfer=.08, taper=(.92, .9))
    for s in (-1, 1):
        K.grille(a, (s * 3.0, .3, 5.0), 3.0, .8, facing=(s, 0, 0), slats=8, frame_mat='Team')
        K.smokestack(a, (s * 2.6, 3.6, 6.2), r=.28, h=1.1, mat='Steel')
        K.armour_plate(a, a.part('Armor', 'Armor'), (2.6, 1.6, .12), (s * 2.9, -2.4, 5.1), rot=(0, s * 1.35, 0),
                       rivet=.4)
    K.hatch_round(a, (-2.2, -2.8, 6.25), r=.42, periscopes=0, seg=12)
    K.ladder(a.part('Ladders', 'Steel'), (2.4, -3.6, 4.0), (2.4, -3.3, 6.25), width=.5, step=.35)
    k.lathe(a.part('Radar_mast', 'Steel'), [(.3, 6.25), (.3, 6.4), (.16, 6.5), (.14, 7.35), (.2, 7.4)],
            loc=(0, 4.2, 0), seg=10)
    r = a.pivot('Radar', (0, 4.2, 7.48))
    K.dish(a.part('Radar_dish', 'Medical', r), a.part('Radar_feed', 'Steel', r), (0, 0, .4), r=.75,
           normal=(0, -.6, .8), seg=14)
    a.part('Radar_drive', 'Armor', r).cyl(.22, .2, loc=(0, 0, .05), seg=10, bevel=0)
    for x, y in ((1.8, -2.8), (-1.8, 3.2)):
        a.part('Vents', 'Steel').cyl(.18, .4, loc=(x, y, 6.4), seg=8, bevel=0)
        a.part('Vents', 'Armor').cyl(.28, .06, loc=(x, y, 6.62), r2=.18, seg=8, bevel=0)


def _fortress_rear(a):
    """The rear deck: the two rocket pods on their mounts (Mount_rocket left x 1.9, .001 right), the missile silo
    between them (Mount_missile / Muzzle_missile at its hatches), the SAM box on the left rear (Mount_missile.001)."""
    for i, s in ((0, 1), (1, -1)):
        m = a.pivot(K.name('Mount_rocket', i), (s * 1.9, 6.0, 4.3))
        tg = '' if i == 0 else '_001'
        k.lathe(a.part(f'Launcher_base{tg}', 'Steel', m), [(.6, -.3), (.62, -.25), (.62, -.15), (.55, -.12)], seg=12)
        K.chamfer_box(a.part(f'Launcher_armor{tg}', 'Armor', m), (.8, .9, .7), loc=(0, .2, .2), c=.04)
        k.block(a.part(f'Rocket_pod{tg}', 'Team', m), (1.1, 1.8, .9), loc=(0, .1, 1.0), rot=(.5, 0, 0), chamfer=.05)
        face = a.part(f'Tubes_bore{tg}', 'Undercarriage', m)
        for ix in (-.3, 0, .3):
            for iz in (-.22, .2):
                face.cyl(.11, .04, loc=(ix, -.78, 1.34 + iz), rot=(R90 + .5, 0, 0), seg=8, bevel=0)
        a.part(f'Launcher_steel{tg}', 'Steel', m).tube([(s * .3, .5, .0), (s * .3, -.2, .7)], .06, seg=8)
        a.pivot(K.name('Muzzle_rocket', i), (0, -.78, 1.34), m)
    # The silo hatches between the pods: four lids in a frame, one open with a missile nose showing.
    sil = a.part('Silo_missiles', 'Armor')
    for dx in (-.35, .35):
        for dy in (-.35, .35):
            k.block(sil, (.6, .6, .1), loc=(dx, 6.05 + dy, 4.05), chamfer=.02)
    k.lathe(a.part('Silo_missiles', 'Fuel'), [(0, .55), (.16, .35), (.2, .1), (.2, -.2)], loc=(.35, 6.4, 4.1),
            seg=10)
    a.part('Hazard_bands', 'Hazard').box((1.6, 1.6, .02), loc=(0, 6.05, 4.005), bevel=0)
    m = a.pivot('Mount_missile', (0, 6.05, 4.62))
    a.pivot('Muzzle_missile', (0, 0, 0), m)
    # The SAM box: base, the tilted four-cell box, its radar plate.
    m = a.pivot('Mount_missile__001', (-2.9, 5.0, 4.3))
    k.lathe(a.part('Sam_base', 'Steel', m), [(.5, -.3), (.52, -.25), (.52, -.15), (.45, -.12)], seg=12)
    k.block(a.part('Sam_box', 'Team', m), (.9, 1.2, .7), loc=(0, .1, .8), rot=(.55, 0, 0), chamfer=.04)
    for dx in (-.2, .2):
        for dz in (-.15, .15):
            a.part('Sam_armor', 'Undercarriage', m).cyl(.12, .03, loc=(dx, -.52, 1.15 + dz), rot=(R90 + .55, 0, 0),
                                                        seg=8, bevel=0)
    k.block(a.part('Sam_radar', 'Armor', m), (.7, .08, .55), loc=(0, .65, .9), chamfer=.015)
    a.pivot('Muzzle_missile__001', (0, -.52, 1.15), m)


def _fortress_turret(a):
    """The main turret (2S7-class 203 mm) on the Turret pivot: the big gun house with its cheek plates, the long
    203 mm barrel with its recoil cylinders and the brake (Main_cannon / Muzzle_brake), the loading tray, the second
    gun on its roof mount (Mount_gun: Gun2 house, barrel, sleeve, brake), the cupola, hatches."""
    t = a.pivot('Turret', (0, 1.0, 6.33))
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.1), 2.3, h=.14)
    W.poly_turret(a.part('Turret_body', 'Team', t), [
        (0, [(-1.4, -2.3), (1.4, -2.3), (2.2, -1.2), (2.2, 2.3), (-2.2, 2.3), (-2.2, -1.2)]),
        (.7, [(-1.3, -2.45), (1.3, -2.45), (2.25, -1.3), (2.25, 2.35), (-2.25, 2.35), (-2.25, -1.3)]),
        (1.2, [(-1.1, -2.0), (1.1, -2.0), (1.95, -1.05), (1.95, 2.2), (-1.95, 2.2), (-1.95, -1.05)])], chamfer=.06)
    for s in (-1, 1):
        K.armour_plate(a, a.part('Turret_armor', 'Armor', t), (1.4, 1.0, .1), (s * 1.75, -1.85, .6),
                       rot=(0, 0, s * .9), rivet=.35)
        a.part('Turret_steel', 'Steel', t).cyl(.12, 2.0, loc=(s * .32, -2.9, .95), rot=K.FORWARD, seg=8, bevel=0)
    K.chamfer_box(a.part('Turret_armor', 'Armor', t), (1.1, .7, .9), loc=(0, -2.5, .75), c=.06)
    K.gun_barrel(a, 'Main_cannon', t, 0, -2.8, .75, 3.89, .17, seg=14, extractor=(.3, 1.4, .6), brake='baffle')
    a.pivot('Muzzle_main', (0, -6.99, .75), t)
    # The second gun on the roof (Mount_gun).
    m = a.pivot('Mount_gun', (0, 1.0, 1.19), t)
    k.lathe(a.part('Gun2_base', 'Steel', m), [(.6, -.08), (.63, -.04), (.63, .05), (.58, .07)], seg=12)
    W.poly_turret(a.part('Gun2_house', 'Armor', m), [
        (.05, [(-.4, -.7), (.4, -.7), (.6, -.3), (.6, .7), (-.6, .7), (-.6, -.3)]),
        (.6, [(-.32, -.55), (.32, -.55), (.5, -.22), (.5, .62), (-.5, .62), (-.5, -.22)])], chamfer=.03)
    K.gun_barrel(a, 'Gun2_barrel', m, 0, -.7, .42, 2.28, .08, seg=10, extractor=(.4, 1.5, .3),
                 brake_name='Gun2_brake', brake='baffle')
    a.part('Gun2_sleeve', 'Canvas', m).cyl(.15, .2, loc=(0, -.75, .42), rot=K.FORWARD, seg=8, bevel=0)
    a.pivot('Muzzle_gun', (0, -3.28, .42), m)
    k.ring(a.part('Cupola_top', 'Armor', t), [(.38, 0), (.45, 0), (.45, .22), (.38, .22)], loc=(-1.3, 1.2, 1.2),
           seg=12)
    K.hatch_round(a, (1.3, 1.4, 1.2), r=.4, parent=t, periscopes=2, seg=10, mat='Armor')
    a.part('Hatch', 'Steel', t).box((.6, .06, .06), loc=(1.3, 1.0, 1.24), bevel=0)
    a.part('Team_band', 'Team', t).box((2.4, 1.4, .02), loc=(0, 1.2, 1.205), bevel=0)
    K.whip_antenna(a.part('Antenna', 'Steel', t), (-1.7, 2.0, 1.2), h=1.0, lean=.15)


BUILDERS = {
    'behemoth': (behemoth, dict(ao_distance=.9, grime_height=.8, ao_strength=.72)),
    'mobile_fortress': (mobile_fortress, dict(ao_distance=1.1, grime_height=1.0, ao_strength=.7)),
}
