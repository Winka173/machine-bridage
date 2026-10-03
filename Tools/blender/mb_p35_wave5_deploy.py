"""Prompt 35 wave 5 (lane A): the two deploying vehicles rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 5 (lane A)".

- bunker_vehicle: a self-entrenching fighting vehicle (the sheet: an engineer hull with a big dozer blade and a low
  105 mm turret that digs itself in): a high flat engineer hull on seven road wheels, the wide dozer blade on its
  push arms and rams, the low L7 turret on its telescopic riser, side armour plates hinged on the hull edges, the
  rear spades stowed upright on the tail, and the emplacement it raises round itself (bank, sandbags, net).
- siege_tank: a two-mode siege tank (the sheet: 2S4 Tyulpan's 240 mm, M110-style spades, a 105 mm for tank mode,
  StarCraft's siege tank for the poses): a low wide hull whose track ends sit in armoured pods, four hydraulic legs
  folded on the pods, the rear spades, the broad turret drawn in its sieged heading with the fat 240 mm mortar at
  one end and the twin 105 mm that slides into it at the other.

Every Deploy_* pivot is where VehicleView.Deploy expects it (the old files' positions, the rig's lengths in
mb_p22_siege), with the same children names; Turret, Main_cannon*, Muzzle_* and Mount_* as before. Pivots only
translate (frontier_kit), so every pose comes from the view.
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


# ============================================================================= bunker_vehicle
BERM_REST = .01         # the bank's scale at rest (the view grows it from 1 % as the hull sinks: mb_p21_models)


def bunker_vehicle(a):
    """See the module docstring. Runtime: Deploy_blade, Deploy_plate_l / _r, Deploy_spade_l / _r, Deploy_riser,
    Deploy_berm (scaled to 1 % at rest), Turret, Main_cannon, Muzzle_brake, Muzzle_main, Muzzle_mg, Point_fire,
    Point_exhaust."""
    TX, TW, WR = 1.38, .58, .3
    wheels = [-2.6 + i * .86 for i in range(7)]
    W.running_gear(a, TX, TW, WR, wheels, (-3.25, .58, .27), (3.3, .62, .3), rollers=(-1.2, 1.6), roller_z=.86,
                   disc_mat='Armor', seg=8, link_pitch=.45, teeth=10, top_hidden=.8)
    hull = a.part('Hull', 'Team')
    # The engineer hull: a steep nose under the blade, a high flat roof, an armoured stern carrying the spades.
    W.side_hull(hull, [(3.55, .5), (3.6, 1.2), (3.35, 1.72), (-2.4, 1.72), (-3.55, 1.05), (-3.7, .78),
                       (-3.35, .45)], 2.2, chamfer=.06)
    spons = a.part('Sponsons', 'Team')
    for s in (-1, 1):
        W.side_hull(spons, [(3.45, 1.0), (3.4, 1.62), (-2.2, 1.62), (-3.3, 1.0)], .72, chamfer=.05, x=s * 1.38)
        # Hinge brackets for the side plates, a team band, stowage bins on the sponsons.
        for y in (-2.2, -.2, 1.8):
            a.part('Kit_hinges', 'Steel').box((.14, .3, .14), loc=(s * 1.78, y, 1.12), bevel=0)
        a.part('Team_band', 'Team').box((.012, 2.6, .12), loc=(s * 1.745, .3, 1.3), bevel=0)
        a.part('Skirt_edge', 'Rubber').box((.03, 6.4, .2), loc=(s * 1.72, .05, .92), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 1.2, -3.45, 1.32), (0, -1, .2), r=.08)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * 1.5, 3.58, 1.4), bevel=0)
        hc = (s * .62, -2.05, 1.72)
        k.ring(a.part('Hatches', 'Armor'), [(.2, 0), (.25, 0), (.25, .05), (.2, .05)], loc=hc, seg=10)
        k.lathe(a.part('Hatches', 'Armor'), [(0, .07), (.17, .065), (.21, .04), (.21, .02)], loc=hc, seg=10)
        a.part('Sight', 'Armor').box((.14, .09, .07), loc=(s * .62, -2.35, 1.7), rot=(-.5, 0, 0), bevel=0)
        K.exhaust(a, (s * .9, 3.6, 1.4), r=.08, length=.25, direction=(0, 1, .3), muffler=False, cap=False)
    K.grille(a, (0, 2.55, 1.725), 1.6, 1.0, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.5, 1.0, .3), (-1.38, 1.9, 1.62))
    K.net_roll(a.part('Stowage', 'Canvas'), a.part('Kit_straps', 'Crate'), (1.38, 2.0, 1.78), length=1.2, r=.15,
               axis='Y')
    k.ring(a.part('Turret_ring', 'Steel'), [(.72, -.04), (.82, -.04), (.82, .04), (.72, .04)], loc=(0, -.3, 1.7),
           seg=16)
    a.pivot('Point_exhaust', (.9, 3.7, 1.35))
    a.pivot('Point_fire', (0, 2.55, 1.8))
    _bunker_plates(a)
    _bunker_blade(a)
    _bunker_spades(a)
    _bunker_turret(a)
    _bunker_berm(a)
    a.pivots['Deploy_berm'].scale = (BERM_REST,) * 3
    k.clean(a)


def _bunker_plates(a):
    """Side armour plates hinged on the hull edges, standing up beside the turret (they lean out when dug in)."""
    for s, name in ((1, 'Deploy_plate_l'), (-1, 'Deploy_plate_r')):
        p = a.pivot(name, (s * 1.86, 0, 1.14))
        slab = a.part(f'{name}_slab', 'Team', p)
        K.chamfer_box(slab, (.1, 5.2, 1.0), loc=(s * .06, -.2, .52), c=.025)
        ribs = a.part(f'{name}_ribs', 'Armor', p)
        for y in (-2.2, -1.1, 0, 1.1, 2.2):
            ribs.box((.06, .12, .86), loc=(s * .14, y - .2, .5), bevel=0)
        ribs.box((.06, 5.0, .09), loc=(s * .14, -.2, .97), bevel=0)
        ribs.box((.06, 5.0, .09), loc=(s * .14, -.2, .1), bevel=0)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.06, 5.0, loc=(0, -.2, 0), rot=K.FORWARD, seg=6, bevel=0)


def _bunker_blade(a):
    """The dozer blade: push arms on the sponson fronts, two lift rams, the curved mouldboard with ribs and edge."""
    p = a.pivot('Deploy_blade', (0, -2.55, .86))
    arms = a.part('Deploy_blade_arms', 'Steel', p)
    for s in (-1, 1):
        arms.limb((s * 1.6, 0, 0), (s * 1.6, -1.72, -.2), .16, .18, bevel=0)
        arms.limb((s * .9, -.6, .55), (s * 1.0, -1.65, .1), .1, .1, bevel=0)
        arms.limb((s * .9, -.6, .55), (s * .92, -1.0, .38), .16, .16, bevel=0)
    board = [(-1.7, -.55), (-1.98, -.52), (-2.06, -.24), (-2.07, .08), (-2.0, .38), (-1.88, .56), (-1.78, .54),
             (-1.86, .32), (-1.9, .06), (-1.88, -.22), (-1.76, -.42)]
    k.extrude(a.part('Deploy_blade_plate', 'Armor', p), board, 3.95, axis='X', chamfer=.025)
    a.part('Deploy_blade_edge', 'Steel', p).box((3.9, .1, .09), loc=(0, -2.02, -.56), bevel=0)
    ribs = a.part('Deploy_blade_ribs', 'Armor', p)
    for xx in (-1.6, -.8, 0, .8, 1.6):
        ribs.box((.08, .16, .84), loc=(xx, -1.7, -.02), bevel=0)
    ribs.box((3.8, .12, .1), loc=(0, -1.72, .4), bevel=0)


def _bunker_spades(a):
    """The two rear spades stowed upright on the stern, on hinge lugs at the tail."""
    for s, name in ((1, 'Deploy_spade_l'), (-1, 'Deploy_spade_r')):
        x = s * .8
        for dx in (-.38, .38):
            a.part('Spade_lugs', 'Armor').box((.16, .22, .22), loc=(x + dx, 3.6, .72), bevel=0)
        p = a.pivot(name, (x, 3.66, .72))
        K.chamfer_box(a.part(f'{name}_blade', 'Armor', p), (.92, .08, 1.15), loc=(0, .1, .62), c=.02)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.07, .6, rot=ACROSS, seg=8, bevel=0)
        teeth = a.part(f'{name}_teeth', 'Steel', p)
        for dx in (-.33, -.11, .11, .33):
            teeth.box((.14, .06, .16), loc=(dx, .1, 1.25), bevel=0, taper=(.4, 1))
        a.part(f'{name}_ribs', 'Team', p).box((.06, .06, 1.0), loc=(0, .16, .6), bevel=0)


def _bunker_turret(a):
    r = a.pivot('Deploy_riser', (0, -.3, 1.72))
    a.part('Deploy_riser_column', 'Steel', r).cyl(.6, .9, loc=(0, 0, -.43), seg=14, bevel=0)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.63, .08, loc=(0, 0, -.22), seg=14, bevel=0)
    t = a.pivot('Turret', (0, 0, .04), r)
    body = a.part('Turret_body', 'Team', t)
    W.poly_turret(body, [
        (0, [(-.7, -1.3), (.7, -1.3), (1.38, -.75), (1.42, .95), (1.05, 1.45), (-1.05, 1.45), (-1.42, .95),
             (-1.38, -.75)]),
        (.56, [(-.55, -1.15), (.55, -1.15), (1.15, -.65), (1.2, .85), (.9, 1.3), (-.9, 1.3), (-1.2, .85),
               (-1.15, -.65)])], chamfer=.04)
    arm = a.part('Turret_armor', 'Armor', t)
    K.chamfer_box(arm, (.8, .38, .5), loc=(0, -1.4, .3), c=.04)
    K.chamfer_box(arm, (1.9, .38, .34), loc=(0, 1.45, .26), c=.04)
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (.5, .25, .4), loc=(0, -1.6, .34), c=.04)
    K.gun_barrel(a, 'Main_cannon', t, 0, -1.7, .36, 3.98, .075, seg=10, extractor=(.5, 1.5, .4),
                 brake_name='Muzzle_brake', brake='collar', sleeve=1.3)
    a.pivot('Muzzle_main', (0, -5.82, .36), t)
    mg = a.part('MG_port', 'Steel', t)
    K.chamfer_box(mg, (.16, .3, .16), loc=(.55, -1.38, .3), c=.02)
    k.lathe(mg, [(.025, 0), (.025, .5), (.035, .52), (0, .53)], loc=(.55, -1.5, .3), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_mg', (.55, -1.99, .3), t)
    K.periscope(a, (.7, -.55, .56), facing=(0, -1, 0), parent=t, size=(.22, .22, .18))
    K.hatch_round(a, (-.55, .3, .56), r=.27, parent=t, periscopes=2, seg=10)
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.15, -.6, .5, s, count=3, parent=t)
    a.part('Team_band', 'Team', t).box((.9, .5, .012), loc=(0, .4, .565), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.0, 1.1, .56), h=.4, lean=.3)


def _bunker_berm(a):
    """The emplacement in ground space round the scrape (Deploy_berm, grown by the view as the hull sinks): a
    horseshoe earth bank open at the rear, sandbags along the front crest, a camouflage net over the engine deck."""
    p = a.pivot('Deploy_berm', (0, 0, 0))
    xi, yf, yr = 2.4, -4.9, 3.3
    path = [(-xi, yr), (-xi, yf + 1.2), (-xi + .5, yf + .35), (-1.0, yf), (1.0, yf), (xi - .5, yf + .35),
            (xi, yf + 1.2), (xi, yr)]
    prof = [(-.15, 0), (.25, -1.0), (.75, -1.02), (2.2, 0)]   # sweep's v runs down here
    dirt = a.part('Berm_dirt', 'Dirt', p)
    pts3 = [(x, y, 0) for x, y in path]
    k.sweep(dirt, prof, pts3, caps=True, up=(0, 0, 1))
    K.sandbag_run(a, [(-1.6, yf - .1, .95), (1.6, yf - .1, .95)], courses=2, part='Berm_bags', parent=p, lean=True)
    for s in (-1, 1):
        K.sandbag_run(a, [(s * (xi + .2), yf + 1.4, 1.0), (s * (xi + .2), -1.0, 1.0)], courses=1, part='Berm_bags',
                      parent=p, seed=2 + s, lean=True)
    K.camo_net(a, [(-2.6, 2.1, 1.5), (2.6, 2.1, 1.5), (2.6, 4.8, 1.4), (-2.6, 4.8, 1.4)], .25, 0, part='Berm_net',
               pole_part='Berm_posts', parent=p, garnish=8, seed=3)
    g = a.part('Berm_grass', 'Grass', p)
    for i, (x, y) in enumerate([(-3.4, -2.5), (3.5, -1.0), (-3.3, 1.5), (3.4, 2.0), (-1.8, -6.2), (1.6, -6.0)]):
        g.ico(.35, loc=(x, y, .25), sub=1, jitter=.3, seed=i * .9)
    K.crate(a.part('Berm_crates', 'Crate', p), a.part('Kit_latches', 'Steel', p), (.6, .35, .3), (2.0, 4.2, 0))
    K.jerrycan(a.part('Berm_can', 'Crate', p), (2.6, 4.0, 0))


# ============================================================================= siege_tank
LEG_HINGE_Z, LEG_LENGTH, PAD_UNDER = 1.2, 1.45, .07     # the rig's sizes (VehicleView.Deploy: LegHinge, LegLength)
SIEGE_X = 1.3                                            # tracks' and pods' centre line


def siege_tank(a):
    """See the module docstring. Runtime: Deploy_brace_l / _r and Deploy_leg_l / _r (each with its _knee and _ram
    pivots), Deploy_spade_l / _r, Deploy_riser, Turret, Main_cannon_cradle / _sleeve / _tube, Muzzle_brake,
    Muzzle_main (the 240 mm, -Y end of the turret), Deploy_gun / Muzzle_gun (the twin 105 mm at the +Y end),
    Mount_mg / Muzzle_mg, Point_fire, Point_exhaust. Static parts of one material are merged afterwards
    (mb_p35_w5parts.merge_static) to stay under the renderer cap."""
    wheels = [-2.2 + i * .88 for i in range(6)]
    W.running_gear(a, SIEGE_X, .56, .3, wheels, (-3.25, .52, .26), (3.25, .55, .27), disc_mat='Armor', seg=8,
                   link_pitch=.5, top_hidden=.62, teeth=9)
    hull = a.part('Hull', 'Team')
    # A low wide hull with sloped sides between the pods: lofted through sections nose to tail.
    K.section_loft(hull, [
        (-4.02, [(0, .55), (.75, .55), (.98, .8), (.6, .98), (0, .98)]),
        (-3.3, [(0, .38), (.95, .38), (1.02, .95), (.78, 1.36), (0, 1.38)]),
        (3.4, [(0, .38), (.95, .38), (1.02, .95), (.82, 1.38), (0, 1.4)]),
        (3.9, [(0, .5), (.9, .5), (.98, .95), (.82, 1.3), (0, 1.32)])])
    gl = a.part('Glacis_plate', 'Armor')
    K.chamfer_box(gl, (1.5, .9, .08), loc=(0, -3.62, 1.2), rot=(math.atan2(.4, .7), 0, 0), c=.02)
    # Armoured pods over both ends of each track; the legs are hinged on their outer ends.
    for s in (-1, 1):
        for k_ in (-1, 1):
            prof = [(k_ * 3.95, .62), (k_ * 3.75, 1.12), (k_ * 1.55, 1.12), (k_ * 1.4, .95), (k_ * 1.4, .5),
                    (k_ * 3.7, .42)]
            pod = a.part('Track_pods', 'Team')
            k.extrude(pod, prof if k_ < 0 else prof[::-1], .72, loc=(s * SIEGE_X, 0, 0), axis='X', chamfer=.04)
            a.part('Pod_trim', 'Armor').box((.74, 1.9, .06), loc=(s * SIEGE_X, k_ * 2.6, 1.14), bevel=0)
            K.rivet_line(a.part('Kit_bolts', 'Steel'), (s * (SIEGE_X + .37), k_ * 1.6, 1.0),
                         (s * (SIEGE_X + .37), k_ * 3.5, 1.0), (s, 0, 0), pitch=.5)
        a.part('Team_band', 'Team').box((.012, 2.2, .1), loc=(s * 1.03, 0, 1.1), bevel=0)
        a.part('Skirt_edge', 'Rubber').box((.03, 2.6, .16), loc=(s * (SIEGE_X + .3), 0, .62), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .7, -3.95, .98), (0, -1, .1), r=.07, guard=False)
        K.tow_hook(a.part('Kit_tow', 'Steel'), (s * .55, -4.06, .7), facing=(0, -1, 0), size=.1)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * .8, 3.92, 1.15), bevel=0)
        k.lathe(a.part('Exhaust', 'Steel'), [(.1, 0), (.1, .4), (.12, .42), (.12, .46), (.08, .46), (.08, .38), (0, .38)],
                loc=(s * .75, 3.5, 1.4), seg=8)
        K.soot(a, (s * .75, 3.5, 1.86), radius=.4, k=.4)
        K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.5, .7, .3), (s * .62, 1.95, 1.39))
    hc = (-.5, -2.75, 1.38)
    k.ring(a.part('Hatches', 'Armor'), [(.21, 0), (.26, 0), (.26, .05), (.21, .05)], loc=hc, seg=10)
    k.lathe(a.part('Hatches', 'Armor'), [(0, .08), (.18, .075), (.22, .05), (.22, .02)], loc=hc, seg=10)
    for dx in (-.25, 0, .25):
        a.part('Sight', 'Armor').box((.14, .09, .07), loc=(dx, -3.15, 1.36), rot=(-.4, 0, 0), bevel=0)
    K.grille(a, (0, 2.85, 1.4), 1.3, .9, facing=(0, 0, 1), slats=5, frame_mat='Team')
    k.ring(a.part('Turret_ring', 'Steel'), [(.88, -.05), (.98, -.05), (.98, .05), (.88, .05)], loc=(0, .1, 1.39),
           seg=16)
    a.pivot('Point_exhaust', (.75, 3.55, 1.85))
    a.pivot('Point_fire', (0, 2.9, 1.45))
    for s in (1, -1):
        _siege_leg(a, 'brace', s, -1)
        _siege_leg(a, 'leg', s, 1)
    for s, name in ((1, 'Deploy_spade_l'), (-1, 'Deploy_spade_r')):
        x = s * .72
        for dx in (-.36, .36):
            a.part('Spade_lugs', 'Armor').box((.14, .22, .22), loc=(x + dx, 3.86, .66), bevel=0)
        p = a.pivot(name, (x, 3.93, .66))
        K.chamfer_box(a.part(f'{name}_blade', 'Armor', p), (.86, .08, 1.0), loc=(0, .09, .55), c=.02)
        a.part(f'{name}_hinge', 'Steel', p).cyl(.07, .56, rot=ACROSS, seg=8, bevel=0)
        teeth = a.part(f'{name}_hinge', 'Steel', p)
        for dx in (-.3, -.1, .1, .3):
            teeth.box((.14, .06, .14), loc=(dx, .09, 1.1), bevel=0, taper=(.4, 1))
    _siege_turret(a)
    k.clean(a)
    W.merge_static(a)


def _siege_leg(a, root, sx, sy):
    """One hydraulic leg hinged on a pod's outer end (sy -1 front, 1 rear), folded towards the hull's middle: a
    boxed I-section arm with its actuator, the knee at LEG_LENGTH with the ram housing, the ram and its claw pad."""
    lr = 'l' if sx > 0 else 'r'
    hinge = (sx * SIEGE_X, sy * 2.6, LEG_HINGE_Z)
    a.part('Leg_lugs', 'Steel').box((.42, .34, .1), loc=(hinge[0], hinge[1], 1.12), bevel=0)
    p = a.pivot(f'Deploy_{root}_{lr}', hinge)
    arm = a.part(f'Deploy_{root}_{lr}_arm', 'Armor', p)
    for dx in (-.11, .11):
        arm.box((.06, LEG_LENGTH - .1, .26), loc=(dx, -sy * LEG_LENGTH / 2, 0), bevel=0, taper=(1, .9))
    arm.box((.28, LEG_LENGTH - .2, .05), loc=(0, -sy * LEG_LENGTH / 2, .12), bevel=0)
    K.chamfer_box(arm, (.34, .3, .3), loc=(0, -sy * (LEG_LENGTH - .12), 0), c=.03)
    steel = a.part(f'Deploy_{root}_{lr}_steel', 'Steel', p)
    steel.cyl(.15, .42, rot=ACROSS, seg=10, bevel=0)
    steel.cyl(.05, 1.0, loc=(0, -sy * .66, .2), rot=K.FORWARD, seg=6, bevel=0)
    kn = a.pivot(f'Deploy_{root}knee_{lr}', (0, -sy * LEG_LENGTH, 0), p)
    a.part(f'Deploy_{root}knee_{lr}_housing', 'Steel', kn).cyl(.15, .62, loc=(0, 0, .3), seg=10, bevel=0)
    a.part(f'Deploy_{root}knee_{lr}_housing', 'Steel', kn).cyl(.19, .1, loc=(0, 0, .6), seg=10, bevel=0)
    r = a.pivot(f'Deploy_{root}ram_{lr}', (0, 0, 0), kn)
    a.part(f'Deploy_{root}ram_{lr}_rod', 'Steel', r).cyl(.08, .68, loc=(0, 0, .35), seg=8, bevel=0)
    a.part(f'Deploy_{root}ram_{lr}_pad', 'Undercarriage', r).cyl(.3, .1, loc=(0, 0, -PAD_UNDER + .05), seg=12,
                                                                 bevel=.02, bseg=1)
    claws = a.part(f'Deploy_{root}ram_{lr}_rod', 'Steel', r)
    for i in range(4):
        u = i * R90 + math.pi / 4
        claws.box((.1, .1, .1), loc=(math.cos(u) * .27, math.sin(u) * .27, -.04), bevel=0, taper=(.5, .5))


def _siege_turret(a):
    """The broad turret on its tall ring, drawn sieged: the 240 mm mortar (cradle on trunnions, the fat sleeve, the
    inner tube with its lock collar, the big brake: tube and brake run out 1.9 m sieged) at -Y; the twin 105 mm on
    its sliding mantlet (Deploy_gun) at +Y; the roof M2 on its post."""
    r = a.pivot('Deploy_riser', (0, .1, 1.87))
    a.part('Deploy_riser_column', 'Steel', r).cyl(.85, .72, loc=(0, 0, -.33), seg=16, bevel=0)
    a.part('Deploy_riser_bands', 'Armor', r).cyl(.88, .08, loc=(0, 0, -.06), seg=16, bevel=0)
    t = a.pivot('Turret', (0, 0, .04), r)
    W.poly_turret(a.part('Turret_body', 'Team', t), [
        (0, [(-.9, -1.55), (.9, -1.55), (1.25, -.85), (1.25, 1.15), (.95, 1.72), (-.95, 1.72), (-1.25, 1.15),
             (-1.25, -.85)]),
        (.38, [(-.95, -1.62), (.95, -1.62), (1.3, -.9), (1.3, 1.2), (1.0, 1.78), (-1.0, 1.78), (-1.3, 1.2),
               (-1.3, -.9)]),
        (.7, [(-.75, -1.35), (.75, -1.35), (1.05, -.75), (1.05, 1.0), (.8, 1.5), (-.8, 1.5), (-1.05, 1.0),
              (-1.05, -.75)])], chamfer=.04)
    tarm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        for i in range(3):
            K.panel(a, tarm, (.5, .3), (s * 1.31, -.55 + i * .55, .3), (s, 0, 0), t=.04, rivet=.3, parent=t)
    K.periscope(a, (-.8, .95, .7), facing=(0, 1, 0), parent=t, size=(.24, .26, .22))
    k.ring(a.part('Hatches', 'Armor', t), [(.24, 0), (.3, 0), (.3, .07), (.24, .07)], loc=(.55, .35, .7), seg=10)
    k.lathe(a.part('Hatches', 'Armor', t), [(0, .09), (.21, .085), (.25, .06), (.25, .02)], loc=(.55, .35, .7),
            seg=10)
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.15, 1.35, .45, s, count=3, parent=t)
    a.part('Team_band', 'Team', t).box((1.1, .55, .012), loc=(0, .1, .705), bevel=0)
    # The 240 mm siege mortar at the -Y end.
    z = .92
    cradle = a.part('Main_cannon_cradle', 'Armor', t)
    K.chamfer_box(cradle, (1.2, 1.7, .66), loc=(0, -1.05, z - .06), c=.05)
    for s in (-1, 1):
        cradle.cyl(.22, .16, loc=(s * .64, -.45, z), rot=ACROSS, seg=10, bevel=0)
    sleeve = a.part('Main_cannon_sleeve', 'Steel', t)
    k.lathe(sleeve, [(.36, 0), (.36, 1.7), (.41, 1.72), (.41, 1.82), (.3, 1.82), (.3, 1.6), (0, 1.6)],
            loc=(0, -1.8, z), rot=K.FORWARD, seg=14)
    for y in (-2.2, -3.0):
        sleeve.cyl(.38, .07, loc=(0, y, z), rot=K.FORWARD, seg=14, bevel=0)
    tube = a.part('Main_cannon_tube', 'Steel', t)
    tube.cyl(.27, 3.6, loc=(0, -1.8, z), rot=K.FORWARD, seg=14, bevel=0)
    tube.cyl(.32, .14, loc=(0, -1.8, z), rot=K.FORWARD, seg=14, bevel=0)
    brake = a.part('Muzzle_brake', 'Armor', t)
    K.chamfer_box(brake, (.82, .66, .66), loc=(0, -3.94, z), c=.05)
    brake.cyl(.33, .1, loc=(0, -4.28, z), rot=K.FORWARD, seg=14, bevel=0)
    ports = a.part('Muzzle_brake_ports', 'Undercarriage', t)
    for s in (-1, 1):
        for y in (-3.8, -4.06):
            ports.box((.04, .14, .4), loc=(s * .41, y, z), bevel=0)
    a.pivot('Muzzle_main', (0, -4.36, z), t)
    # The twin 105 mm on its mantlet, which slides 3 m back into the turret when sieging.
    p = a.pivot('Deploy_gun', (0, 1.6, .42), t)
    K.chamfer_box(a.part('Mantlet_105', 'Armor', p), (1.0, .5, .46), loc=(0, .05, 0), c=.04)
    tubes = a.part('Gun105_tubes', 'Steel', p)
    brakes = a.part('Gun105_brakes', 'Undercarriage', p)
    for x in (-.22, .22):
        k.lathe(tubes, [(.11, 0), (.11, 1.0), (.085, 1.05), (.085, 2.95), (0, 2.96)], loc=(x, .3, 0),
                rot=(-R90, 0, 0), seg=10)
        brakes.cyl(.11, .28, loc=(x, 3.06, 0), rot=K.FORWARD, seg=8, bevel=0)
    a.part('Mantlet_105', 'Armor', p).box((.62, .14, .12), loc=(0, 2.2, 0), bevel=0)
    a.pivot('Muzzle_gun', (-.22, 3.22, 0), p)
    K.pintle_mg(a, t, (.8, .95, .7), post=.25, length=.9, shield=True)


BUILDERS = {
    'bunker_vehicle': (bunker_vehicle, dict(ao_distance=.6, grime_height=.6)),
    'siege_tank': (siege_tank, dict(ao_distance=.6, grime_height=.6)),
}
