"""Prompt 35 wave 5 (lane A): tanks and tracked carriers rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library and mb_p35_w5parts (lean running gear). DECISIONS "Prompt 35
wave 5 (lane A)". No hull, turret or weapon of one is drawn by another's function.

- twin_tank: the sheet's twin-gun tank (Rh-120 L/44 x 2): a long low hull on seven road wheels under armoured skirts,
  a very wide flat turret with two guns side by side in their own mantlets, the coax between them, the commander's
  cupola with the 12.7 mm gun standing on its post, the loader's hatch, a bustle rack.
- titan_tank: the super tank (NPzK 140 mm x 2, APS, sub-turret): four tracks (two a side, each in its own sponson),
  a broad stepped hull, the big turret with the twin 140 mm in one mantlet, TOW boxes on the cheeks, APS radar
  panels and launcher clusters, a rear machine-gun turret on the engine deck.
- turtle_tank: the improvised "turtle" (T-72 under a welded shed roof, 2024): the corrugated shell over hull and
  turret down near the ground, its side doors and patches, the anti-drone net, the gun out of a slot in the front,
  the KMT-7 mine roller on its arms ahead of the hull.
- laser_tank: a tracked laser tank-hunter: a mid-size chassis, the turret carrying the beam director on a fork, the
  big round mirror, radiator banks on both sides, the power pack's exhausts, a remote machine-gun station.
- aa_57mm_vehicle: 2S38 Derivatsiya-PVO: the BMP-3 chassis (its low hull, trim vane, six road wheels), the unmanned
  AU-220M turret with the 57 mm gun and its feed housing, the sight drum, the radar mast on the turret rear.
- thermobaric_launcher: TOS-1A Solntsepyok: a T-72 hull, the 24-tube box launcher on its turntable cradle with its
  lifting rams, the dozer blade, crew box, the commander's 12.7 mm gun.
- gps_jammer_vehicle: an EW truck: a KamAZ-type 6x6 cab-over cab, a container shelter on the bed with its
  telescopic mast and the jammer head (`Radar`), stowed antenna sections, the cab-roof weapon station.

Runtime nodes are the old models' (positions within a few centimetres of the old pivots): see each builder.
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w5parts as W

R90 = math.pi / 2
TAU = math.tau


# ============================================================================= twin_tank
def twin_tank(a):
    """The twin-gun tank: see the module docstring. Runtime: Turret, Main_cannon, Main_cannon_2, Muzzle_brake,
    Muzzle_brake_2, Muzzle_main (between the barrels, as before), Coax / Muzzle_coax, Mount_mg / Muzzle_mg,
    Point_fire, Point_exhaust."""
    TX, TW, WR = 1.36, .58, .36
    wheels = [-2.5 + i * .82 for i in range(7)]
    W.running_gear(a, TX, TW, WR, wheels, (-3.05, .64, .3), (3.0, .68, .32), rollers=(-1.2, 1.2),
                   roller_z=.9, top_hidden=.82, disc_mat='Armor', seg=8, link_pitch=.4)
    hull = a.part('Hull', 'Team')
    W.side_hull(hull, [(3.38, .5), (3.42, 1.05), (3.2, 1.32), (-1.5, 1.34), (-3.48, .95), (-3.52, .72),
                       (-3.2, .48)], 2.12)
    low = a.part('Hull_lower', 'Armor')
    W.side_hull(low, [(3.3, .36), (-2.9, .36), (-3.25, .62), (3.3, .62)], 1.8, chamfer=.03)
    # Sponson tops over the tracks, the side armour skirts with their hinge line.
    fen = a.part('Fenders', 'Team')
    for s in (-1, 1):
        K.fender(fen, TX, -3.4, 3.35, 1.0, .64, s)
        sk = a.part('Skirts', 'Team')
        for i in range(5):
            yc = -3.25 + (i + .5) * 1.23
            sk.box((.05, 1.2, .5), loc=(s * (TX + .34), yc, .74), bevel=0)
            a.part('Skirt_flaps', 'Rubber').box((.03, 1.16, .1), loc=(s * (TX + .34), yc, .45), bevel=0)
        a.part('Kit_hinges', 'Steel').tube([(s * (TX + .38), -3.2, .95), (s * (TX + .38), 2.85, .95)], .02, seg=5)
        a.part('Team_band', 'Team').box((.012, 2.2, .1), loc=(s * (TX + .38), -.6, .8), bevel=0)
    # Glacis: driver's hatch with periscopes, headlamps in guards, tow set on the nose.
    hc = (0, -2.25, 1.36)
    k.ring(a.part('Hatches', 'Armor'), [(.24, 0), (.3, 0), (.3, .06), (.24, .06)], loc=hc, seg=10)
    k.lathe(a.part('Hatches', 'Armor'), [(0, .09), (.2, .085), (.25, .06), (.25, .02)], loc=hc, seg=10)
    for dx in (-.22, 0, .22):
        a.part('Sight', 'Armor').box((.16, .1, .08), loc=(dx, -2.58, 1.33), rot=(-.4, 0, 0), bevel=0)
        a.part('Glass', 'Glass').box((.13, .01, .05), loc=(dx, -2.635, 1.32), rot=(-.4, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 1.15, -3.32, 1.08), (0, -1, .1), r=.07, guard=False)
    for x in (-.7, .7):
        K.tow_hook(a.part('Kit_tow', 'Steel'), (x, -3.54, .74), facing=(0, -1, 0), size=.11)
    # Engine deck: two grille banks, access plates with handles, the exhaust louvre at the rear plate.
    K.grille(a, (.5, 2.3, 1.335), .8, 1.1, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.grille(a, (-.5, 2.3, 1.335), .8, 1.1, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.grille(a, (0, 3.43, .95), 1.4, .26, facing=(0, 1, 0), slats=3, frame_mat='Armor')
    steel = a.part('Kit_handles', 'Steel')
    for x in (-.7, .7):
        K.handle(steel, (x - .12, 1.35, 1.35), (x + .12, 1.35, 1.35), (0, 0, 1), h=.05)
    # Fender stowage: toolbox and jerrycans on the right, track links on the left front.
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.5, .9, .3), (-(TX + .02), 1.9, 1.0))
    K.jerrycan(a.part('Jerrycans', 'Crate'), (-(TX + .02), 2.75, 1.0), rot=(0, 0, R90))
    links = a.part('Spare_links', 'Undercarriage')
    for i in range(3):
        links.box((.4, .16, .05), loc=(TX + .02, -2.7 + i * .2, 1.03), bevel=0)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * 1.25, 3.43, 1.15), bevel=0)
    a.pivot('Point_fire', (0, 2.21, 1.44))
    a.pivot('Point_exhaust', (0, 3.51, .86))
    _twin_turret(a)
    k.clean(a)


def _twin_turret(a):
    t = a.pivot('Turret', (0, .34, 1.43))
    body = a.part('Turret_body', 'Team', t)
    # A wide, flat turret: the front a long shallow wedge either side of the two gun ports, the bustle squared off.
    W.poly_turret(body, [
        (0, [(-1.55, -1.25), (1.55, -1.25), (1.62, -.3), (1.62, 1.6), (1.4, 2.05), (-1.4, 2.05), (-1.62, 1.6),
             (-1.62, -.3)]),
        (.34, [(-1.42, -1.55), (1.42, -1.55), (1.66, -.45), (1.66, 1.62), (1.44, 2.1), (-1.44, 2.1), (-1.66, 1.62),
               (-1.66, -.45)]),
        (.62, [(-1.2, -1.2), (1.2, -1.2), (1.44, -.35), (1.44, 1.5), (1.25, 1.95), (-1.25, 1.95), (-1.44, 1.5),
               (-1.44, -.35)])])
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.06), 1.12, h=.1)
    # Two mantlets and guns side by side; the coax between them in its own small housing.
    for i, x in enumerate((.42, -.42)):
        nm = 'Main_cannon' if i == 0 else 'Main_cannon_2'
        br = 'Muzzle_brake' if i == 0 else 'Muzzle_brake_2'
        K.chamfer_box(a.part('Mantlet', 'Armor', t), (.5, .36, .48), loc=(x, -1.62, .36), c=.05)
        k.lathe(a.part('Mantlet_cover', 'Canvas', t), [(.17, 0), (.21, .05), (.19, .12), (.13, .2)],
                loc=(x, -1.8, .36), rot=K.FORWARD, seg=8)
        K.gun_barrel(a, nm, t, x, -1.95, .36, 3.74, .075, seg=12, extractor=(.42, 1.75, .5), brake_name=br,
                     brake='collar', sleeve=1.25)
    a.pivot('Muzzle_main', (0, -5.83, .43), t)
    K.chamfer_box(a.part('Coax_housing', 'Armor', t), (.24, .3, .2), loc=(0, -1.6, .62), c=.03)
    k.lathe(a.part('Coax', 'Steel', t), [(.022, 0), (.022, .42), (0, .43)], loc=(0, -1.75, .64), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (0, -2.42, .64), t)
    # Gunner's sight box on the left cheek, commander's panoramic sight right, the two hatches.
    K.chamfer_box(a.part('Sight', 'Armor', t), (.36, .42, .3), loc=(1.0, -.9, .78), c=.04)
    a.part('Glass', 'Glass', t).box((.28, .01, .14), loc=(1.0, -1.115, .8), bevel=0)
    K.periscope(a, (-.95, -.7, .62), facing=(0, -1, 0), parent=t, size=(.24, .22, .2))
    k.ring(a.part('Hatches', 'Armor', t), [(.3, 0), (.36, 0), (.36, .08), (.3, .08)], loc=(.75, .52, .62), seg=12)
    K.hatch_round(a, (-.7, .6, .62), r=.3, parent=t, periscopes=2, hinge_dir=-1, seg=10)
    K.pintle_mg(a, t, (.75, .52, .7), riser=.1, post=.1, length=1.1, shield=False, ring_r=.3)
    # Smoke dischargers on both front cheeks, stowage boxes on the turret sides, the bustle basket.
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.5, -.55, .4, s, count=3, parent=t)
        K.crate(a.part('Stowage', 'Armor', t), a.part('Kit_latches', 'Steel', t), (.2, .9, .3), (s * 1.74, .7, .12),
                bands=1)
    bk = a.part('Bustle_rack', 'Steel', t)
    pts = [(-1.3, 2.08, .1), (-1.3, 2.4, .1), (1.3, 2.4, .1), (1.3, 2.08, .1)]
    for z in (.1, .42):
        bk.tube([(x, y, z) for x, y, _ in pts], .022, seg=4)
    for x in (-1.3, -.65, 0, .65, 1.3):
        bk.tube([(x, 2.4, .1), (x, 2.4, .42)], .02, seg=4)
    K.net_roll(a.part('Stowage', 'Canvas', t), a.part('Kit_straps', 'Crate', t), (-.5, 2.25, .32), length=1.0, r=.15)
    K.crate(a.part('Ammo_boxes', 'Crate', t), a.part('Kit_latches', 'Steel', t), (.55, .28, .26), (.6, 2.24, .12))
    a.part('Team_band', 'Team', t).box((1.0, .55, .012), loc=(0, .1, .625), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.25, 1.7, .62), h=.62, lean=.25)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.25, 1.75, .62), h=.45, lean=.25)


# ============================================================================= titan_tank
def titan_tank(a):
    """The super tank: see the module docstring. Runtime: Turret, Main_cannon, Main_cannon_2, Muzzle_brake,
    Muzzle_brake_2, Muzzle_main (left barrel; mb_p34_barrels adds Muzzle_b1 / b2_main), Muzzle_coax,
    Muzzle_missile[.001] (the TOW boxes), Mount_mg / Muzzle_mg (the rear sub-turret), Mount_APS, Point_fire,
    Point_exhaust."""
    K.suffixed(a)
    wheels_o = [-3.15 + i * 1.22 for i in range(6)]
    W.running_gear(a, 2.27, .52, .38, wheels_o, (-3.85, .66, .3), (3.75, .7, .32), top_hidden=.85,
                   disc_mat='Armor', seg=8, link_pitch=.6)
    wheels_i = [-2.4 + i * 1.6 for i in range(4)]
    W.running_gear(a, 1.42, .48, .34, wheels_i, (-3.55, .6, .27), (3.55, .64, .29), disc_mat='Armor', seg=6,
                   link_pitch=1.1, top_hidden=.6, teeth=8, dust=0, ends=False)
    hull = a.part('Hull', 'Team')
    # The upper hull spans all four tracks: a long shallow glacis, a stepped deck, the sloped rear plate.
    W.side_hull(hull, [(4.05, .62), (4.1, 1.18), (3.9, 1.45), (-1.9, 1.46), (-3.9, 1.06), (-4.02, .82),
                       (-3.7, .58)], 5.1, chamfer=.07)
    low = a.part('Hull_lower', 'Armor')
    W.side_hull(low, [(3.9, .4), (-3.4, .4), (-3.8, .68), (3.9, .68)], 2.2, chamfer=.04)
    # Glacis composite modules, the driver's hatch and vision blocks, lamps, tow hooks.
    gl = a.part('Glacis_armor', 'Armor')
    for s in (-1, 1):
        for i in range(2):
            x = s * (.75 + i * 1.25)
            gl.box((1.15, 1.2, .14), loc=(x, -2.9, 1.27), rot=(math.atan2(.4, 2.0), 0, 0), bevel=0)
    hc = (0, -1.65, 1.47)
    k.ring(a.part('Hatches', 'Armor'), [(.26, 0), (.32, 0), (.32, .06), (.26, .06)], loc=hc, seg=10)
    k.lathe(a.part('Hatches', 'Armor'), [(0, .09), (.22, .085), (.27, .06), (.27, .02)], loc=hc, seg=10)
    for dx in (-.25, 0, .25):
        a.part('Sight', 'Armor').box((.16, .1, .08), loc=(dx, -2.02, 1.44), rot=(-.35, 0, 0), bevel=0)
        a.part('Glass', 'Glass').box((.13, .01, .05), loc=(dx, -2.075, 1.43), rot=(-.35, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * 2.1, -3.95, 1.0), (0, -1, .1), r=.08, guard=False)
        K.tow_hook(a.part('Kit_tow', 'Steel'), (s * .9, -4.04, .78), facing=(0, -1, 0), size=.12)
        # Armoured skirts on the outer tracks, a team band above them, sponson stowage, exhausts.
        sk = a.part('Skirts', 'Team')
        for i in range(5):
            yc = -3.7 + (i + .5) * 1.46
            sk.box((.06, 1.42, .55), loc=(s * 2.6, yc, .9), bevel=0)
            a.part('Skirt_flaps', 'Rubber').box((.03, 1.38, .1), loc=(s * 2.6, yc, .58), bevel=0)
        a.part('Kit_hinges', 'Steel').tube([(s * 2.64, -3.7, 1.15), (s * 2.64, 3.6, 1.15)], .022, seg=5)
        a.part('Team_band', 'Team').box((.012, 3.0, .1), loc=(s * 2.64, -.8, .95), bevel=0)
        K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.6, 1.1, .32), (s * 2.15, 1.6, 1.46))
        K.exhaust(a, (s * 1.9, 3.85, 1.35), r=.09, length=.45, direction=(0, .5, 1), muffler=False)
    # Engine deck grilles and the rear plate louvres, tail lamps.
    for x in (-.9, .9):
        K.grille(a, (x, 2.95, 1.455), 1.2, 1.3, facing=(0, 0, 1), slats=6, frame_mat='Team')
    K.grille(a, (0, 4.1, 1.0), 2.4, .3, facing=(0, 1, 0), slats=3, frame_mat='Armor')
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow').box((.14, .02, .08), loc=(s * 2.0, 4.07, 1.2), bevel=0)
    a.pivot('Point_fire', (0, 3.4, 1.7))
    a.pivot('Point_exhaust', (1.2, 4.1, 1.25))
    _titan_rear_turret(a)
    _titan_turret(a)
    k.clean(a)


def _titan_rear_turret(a):
    """The rear machine-gun sub-turret on the engine deck: a squat hexagonal turret on its ring, the 12.7 mm."""
    k.ring(a.part('Sub_turret_ring', 'Steel'), [(.46, 0), (.54, 0), (.54, .1), (.46, .1)], loc=(0, 3.05, 1.45), seg=12)
    m = a.pivot('Mount_mg', (0, 3.05, 1.62))
    tb = a.part('Sub_turrets', 'Team', m)
    W.poly_turret(tb, [(-.15, [(-.42, -.4), (.42, -.4), (.5, 0), (.42, .4), (-.42, .4), (-.5, 0)]),
                       (.22, [(-.3, -.32), (.3, -.32), (.38, 0), (.3, .32), (-.3, .32), (-.38, 0)])], chamfer=.03)
    g = a.part('MG', 'Steel', m)
    k.lathe(g, [(.05, 0), (.05, .25), (.032, .3), (.032, 1.25), (.05, 1.27), (.05, 1.4), (0, 1.42)],
            loc=(0, -.25, .08), rot=K.FORWARD, seg=8)
    K.chamfer_box(a.part('MG_mantlet', 'Armor', m), (.22, .16, .18), loc=(0, -.36, .08), c=.02)
    K.periscope(a, (.18, .05, .22), parent=m, size=(.14, .12, .1))
    a.pivot('Muzzle_mg', (0, -1.68, .08), m)


def _titan_turret(a):
    t = a.pivot('Turret', (0, -.3, 1.62))
    body = a.part('Turret_body', 'Team', t)
    W.poly_turret(body, [
        (0, [(-1.2, -1.85), (1.2, -1.85), (1.95, -.9), (1.95, 1.55), (1.6, 1.95), (-1.6, 1.95), (-1.95, 1.55),
             (-1.95, -.9)]),
        (.42, [(-1.05, -2.25), (1.05, -2.25), (2.0, -1.0), (2.0, 1.6), (1.65, 2.0), (-1.65, 2.0), (-2.0, 1.6),
               (-2.0, -1.0)]),
        (.75, [(-.9, -1.8), (.9, -1.8), (1.7, -.85), (1.7, 1.45), (1.45, 1.8), (-1.45, 1.8), (-1.7, 1.45),
               (-1.7, -.85)])], chamfer=.05)
    k.ring(a.part('Turret_steel', 'Steel', t), [(1.34, -.1), (1.48, -.1), (1.48, .02), (1.34, .02)], seg=16)
    # Cheek composite modules with their bolt rows.
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        K.chamfer_box(arm, (.9, .9, .5), loc=(s * 1.4, -1.55, .38), rot=(0, 0, s * .62), c=.04)
        K.rivet_line(a.part('Kit_bolts', 'Steel', t), (s * 1.1, -1.95, .66), (s * 1.75, -1.2, .66), (0, 0, 1),
                     pitch=.32)
    # One broad mantlet carrying the twin 140 mm, the coax above between them.
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (1.75, .42, .62), loc=(0, -2.25, .5), c=.06)
    for i, x in enumerate((-.62, .62)):
        nm = 'Main_cannon' if i == 0 else 'Main_cannon_2'
        br = 'Muzzle_brake' if i == 0 else 'Muzzle_brake_2'
        K.gun_barrel(a, nm, t, x, -2.4, .52, 4.38, .095, seg=12, extractor=(.4, 1.7, .55), brake_name=br,
                     brake='baffle', sleeve=1.25)
    a.pivot('Muzzle_main', (-.62, -6.91, .52), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.025, 0), (.025, .5), (0, .51)], loc=(0, -2.38, .7), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (0, -2.87, .7), t)
    # TOW-class launcher boxes on both cheeks (the ATGM), on short pedestals.
    for i, s in enumerate((-1, 1)):
        x = s * 1.95
        K.chamfer_box(a.part('ATGM_mount', 'Steel', t), (.2, .3, .2), loc=(x, -.9, .78), c=.02)
        K.chamfer_box(a.part('ATGM_pod', 'Armor', t), (.42, 1.25, .36), loc=(x, -.95, .98), c=.03)
        for dx in (-.1, .1):
            a.part('Tubes_bore', 'Undercarriage', t).cyl(.075, .02, loc=(x + dx, -1.58, .98), rot=K.FORWARD, seg=8,
                                                          bevel=0)
        a.pivot(K.name('Muzzle_missile', i), (x, -1.6, .98), t)
    # Commander's and gunner's sights, the cupola, the loader's hatch.
    K.chamfer_box(a.part('Sight', 'Armor', t), (.42, .46, .32), loc=(1.05, -1.0, .9), c=.04)
    a.part('Glass', 'Glass', t).box((.32, .01, .14), loc=(1.05, -1.235, .92), bevel=0)
    K.periscope(a, (-1.05, -.85, .75), facing=(0, -1, 0), parent=t, size=(.26, .24, .24))
    k.lathe(a.part('Cupola', 'Armor', t), [(.38, 0), (.38, .14), (.32, .2), (0, .22)], loc=(-.7, .45, .75), seg=12)
    for i in range(5):
        u = i * TAU / 5
        a.part('Glass', 'Glass', t).box((.12, .02, .06), loc=(-.7 + math.cos(u) * .36, .45 + math.sin(u) * .36, .82),
                                         rot=(0, 0, u + R90), bevel=0)
    k.ring(a.part('Hatches', 'Armor', t), [(.3, 0), (.36, 0), (.36, .08), (.3, .08)], loc=(.75, .55, .75), seg=12)
    k.lathe(a.part('Hatches', 'Armor', t), [(0, .1), (.26, .095), (.31, .07), (.31, .02)], loc=(.75, .55, .75),
            seg=12)
    # APS: radar panels on the four corners, two launcher clusters on the roof rear.
    aps = a.part('APS', 'Armor', t)
    glow = a.part('Aps_cluster_panels', 'Glass', t)
    for sx, sy, yaw in ((1, -1, .5), (-1, -1, -.5), (1, 1, 2.4), (-1, 1, -2.4)):
        c = (sx * 1.55, sy * 1.25 + .2, .88)
        aps.box((.42, .14, .3), loc=c, rot=(0, 0, yaw), bevel=0)
        glow.box((.34, .01, .22), loc=(c[0] - math.sin(yaw) * .075, c[1] - math.cos(yaw) * .075, c[2]),
                 rot=(0, 0, yaw), bevel=0)
    cl = a.part('Aps_cluster', 'Steel', t)
    for s in (-1, 1):
        k.lathe(cl, [(.16, 0), (.16, .1), (.12, .16), (0, .17)], loc=(s * 1.2, 1.2, .75), seg=10)
        for j in range(4):
            u = j * TAU / 4 + .4
            cl.cyl(.045, .2, loc=(s * 1.2 + math.cos(u) * .1, 1.2 + math.sin(u) * .1, .95), rot=(.5, 0, u + R90),
                   seg=6, bevel=0)
    a.pivot('Mount_APS', (0, 1.2, 1.0), t)
    # Smoke dischargers, bustle stowage, the roof team panel, antennas.
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.8, .3, .5, s, count=2, parent=t)
        K.crate(a.part('Stowage', 'Armor', t), a.part('Kit_latches', 'Steel', t), (.22, 1.1, .32),
                (s * 2.12, .9, .15), bands=1)
    K.net_roll(a.part('Stowage', 'Canvas', t), a.part('Kit_straps', 'Crate', t), (0, 2.08, .3), length=2.2, r=.16)
    a.part('Team_band', 'Team', t).box((1.4, .7, .012), loc=(0, -.1, .755), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-1.4, 1.5, .75), h=.5, lean=.3)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.4, 1.5, .75), h=.5, lean=.3)


# ============================================================================= turtle_tank
def turtle_tank(a):
    """The improvised turtle tank: see the module docstring. Runtime: Turret (the gun is laid by the hull: mainAim
    Hull), Main_cannon, Muzzle_brake, Muzzle_main, Coax, Muzzle_coax, Point_fire, Point_exhaust."""
    TX, TW, WR = 1.12, .5, .3
    wheels = [-1.95 + i * .74 for i in range(6)]
    W.running_gear(a, TX, TW, WR, wheels, (-2.55, .52, .26), (2.6, .55, .27), disc_mat='Armor', seg=8,
                   link_pitch=.36, top_hidden=.62, teeth=9)
    hull = a.part('Hull', 'Armor')
    W.side_hull(hull, [(2.95, .42), (3.0, .88), (2.8, 1.08), (-1.1, 1.1), (-2.75, .82), (-2.82, .62),
                       (-2.55, .4)], 1.72, chamfer=.04)
    fen = a.part('Fenders', 'Armor')
    for s in (-1, 1):
        K.fender(fen, TX, -2.8, 2.9, .82, .5, s)
        # The T-72's rubber skirts, ragged, just under the shed's eaves.
        sk = a.part('Skirts', 'Rubber')
        for i in range(6):
            sk.box((.03, .86, .3), loc=(s * (TX + .27), -2.45 + i * .9, .66), rot=(0, 0, .02 * (i % 2 - .5)), bevel=0)
    # KMT-7 mine roller on its two arms ahead of the hull: two roller gangs of toothed discs, the chain between.
    ar = a.part('Mine_roller_arms', 'Armor')
    st = a.part('Mine_roller', 'Steel')
    for s in (-1, 1):
        ar.limb((s * .78, -2.75, .7), (s * .78, -3.75, .42), .14, .16, bevel=0)
        ar.box((.18, .3, .25), loc=(s * .78, -2.78, .72), bevel=0)
        for i in range(4):
            x = s * (.5 + i * .18)
            k.lathe(st, [(.12, -.035), (.27, -.03), (.29, 0), (.27, .03), (.12, .035)], loc=(x, -3.92, .3),
                    rot=(0, R90, 0), seg=10)
        st.cyl(.06, .8, loc=(s * .77, -3.92, .3), rot=(0, R90, 0), seg=6, bevel=0)
    a.part('Kit_cables', 'Steel').tube([(-.45, -3.92, .3), (-.1, -3.95, .12), (.1, -3.95, .12), (.45, -3.92, .3)],
                                       .025, seg=4)
    a.pivot('Point_fire', (0, .3, 2.6))
    a.pivot('Point_exhaust', (.9, 2.9, .9))
    K.exhaust(a, (-1.05, 1.6, 1.0), r=.06, length=.3, direction=(1, .2, .3), muffler=False, cap=False)
    _turtle_turret(a)
    _turtle_shell(a)
    k.clean(a)


def _turtle_turret(a):
    """The T-72 turret under the shed: the cast dome, the gun through the shed's front slot, the coax, the cupola
    with its NSVT (seen through the shed's front opening), the 902A smoke grenade launchers."""
    t = a.pivot('Turret', (0, .1, 1.3))
    k.lathe(a.part('Turret_body', 'Armor', t), [(1.12, -.05), (1.15, .1), (1.08, .3), (.85, .5), (.45, .62),
                                               (0, .64)], loc=(0, -.05, 0), seg=14)
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (.55, .3, .34), loc=(0, -1.05, .35), c=.04)
    K.gun_barrel(a, 'Main_cannon', t, 0, -1.2, .45, 3.0, .07, seg=10, extractor=(.38, 1.6, .45),
                 brake_name='Muzzle_brake', brake='collar', sleeve=1.25)
    a.pivot('Muzzle_main', (0, -4.34, .45), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.022, 0), (.022, 1.95), (0, 1.96)], loc=(-.22, -1.1, .45), rot=K.FORWARD,
            seg=6)
    a.pivot('Muzzle_coax', (-.22, -3.07, .45), t)
    k.ring(a.part('Hatches', 'Armor', t), [(.26, 0), (.32, 0), (.32, .08), (.26, .08)], loc=(-.38, .2, .6), seg=10)
    k.lathe(a.part('Hatches', 'Armor', t), [(0, .1), (.24, .095), (.27, .06), (.27, .02)], loc=(.4, .3, .58), seg=10)
    K.periscope(a, (.45, -.5, .5), facing=(0, -1, 0), parent=t, size=(.22, .2, .2))
    mg = a.part('Roof_mg', 'Steel', t)
    mg.cyl(.04, .3, loc=(-.38, .2, .8), seg=6, bevel=0)
    k.lathe(mg, [(.03, 0), (.03, .9), (.045, .92), (.045, 1.0), (0, 1.02)], loc=(-.38, .0, .98), rot=K.FORWARD, seg=6)
    K.chamfer_box(a.part('MG_ammo', 'Armor', t), (.14, .26, .18), loc=(-.24, .22, .96), c=.02)
    for s in (-1, 1):
        K.smoke_dischargers(a, .95, -.45, .25, s, count=4, parent=t)


def _turtle_shell(a):
    """The welded shed: a box-section house of corrugated sheet down to 0.62 m over hull and turret, the pitched roof
    with its ribs, the front with the gun slot and two vision slits, a side door each side, patches of rusty and
    fresh sheet, the anti-drone net hung on a tube frame over the front and the roof."""
    shell = a.part('Shell', 'MetalSheet')
    half, y0, y1, zb, ze, zr = 1.41, -2.95, 3.15, .62, 2.05, 2.75
    prof = [(-half, zb), (half, zb), (half, ze), (half * .55, zr - .08), (0, zr), (-half * .55, zr - .08),
            (-half, ze)]
    # Front and back as their own panels (the slot for the gun in the front), the long sides and the roof lofted.
    k.extrude(shell, [(x, z) for x, z in prof], y1 - y0 - .1, loc=(0, (y0 + y1) / 2 + .05, 0), axis='Y',
              chamfer=.03, corner=.0)
    fr = a.part('Shell_front', 'MetalSheet')
    fy = y0 + .04
    for (x0, x1) in ((-half, -.42), (.42, half)):
        fr.box((x1 - x0, .04, ze - zb), loc=((x0 + x1) / 2, fy, (zb + ze) / 2), bevel=0)
    fr.box((.84, .04, 1.05 - zb), loc=(0, fy, (zb + 1.05) / 2), bevel=0)
    fr.box((.84, .04, ze - 2.0), loc=(0, fy, (2.0 + ze) / 2), bevel=0)
    fr.mesh([(-half, fy, ze), (half, fy, ze), (half * .55, fy, zr - .08), (0, fy, zr), (-half * .55, fy, zr - .08)],
            [(0, 1, 2, 3, 4)])
    fr.mesh([(-half, fy + .04, ze), (-half * .55, fy + .04, zr - .08), (0, fy + .04, zr), (half * .55, fy + .04,
             zr - .08), (half, fy + .04, ze)], [(0, 1, 2, 3, 4)])
    # Corrugation ribs over the roof and down the sides, the welded seams, the rusty and fresh patches.
    seams = a.part('Shell_seams', 'Steel')
    for i in range(11):
        y = y0 + .3 + i * .56
        seams.tube([(-half - .02, y, zb + .02), (-half - .02, y, ze), (-half * .55, y, zr - .06), (0, y, zr + .02),
                    (half * .55, y, zr - .06), (half + .02, y, ze), (half + .02, y, zb + .02)], .018, seg=4,
                   caps=False)
    for s in (-1, 1):
        seams.box((.03, y1 - y0, .05), loc=(s * (half + .01), (y0 + y1) / 2, ze), bevel=0)
    for mat, pts in (('Rust', [(1, -1.6, 1.4, .9, .6), (-1, 1.3, 1.1, 1.1, .7), (1, 2.2, 1.6, .6, .5)]),
                     ('Armor', [(-1, -2.0, 1.6, .7, .55), (1, .4, .95, .8, .45)])):
        pp = a.part(f'Shell_patches_{mat}', mat)
        for s, y, z, w, h in pts:
            pp.box((.025, w, h), loc=(s * (half + .02), y, z), rot=(.05 * s, 0, 0), bevel=0)
    rp = a.part('Shell_patches_Rust', 'Rust')
    rp.box((.9, .7, .03), loc=(.65, -.6, zr - .2), rot=(0, -.47, 0), bevel=0)
    # Side doors (hinged sheet on a frame) and vision slits.
    for s in (-1, 1):
        d = a.part('Shell_doors', 'MetalSheet')
        d.box((.03, .75, .9), loc=(s * (half + .03), .9, 1.25), bevel=0)
        K.hinge(a.part('Kit_hinges', 'Steel'), (s * (half + .05), .52, 1.0), (s * (half + .05), .52, 1.5), r=.02,
                knuckles=2)
        K.handle(a.part('Kit_handles', 'Steel'), (s * (half + .05), 1.15, 1.2), (s * (half + .05), 1.15, 1.35),
                 (s, 0, 0), h=.05)
    sl = a.part('Slits', 'Undercarriage')
    for x in (-.85, .85):
        sl.box((.35, .02, .07), loc=(x, fy - .025, 1.6), bevel=0)
    # Stowage: logs and a spare-track bundle strapped to the rear wall, jerrycans by the door.
    lg = a.part('Stowage', 'Wood')
    for i in range(3):
        lg.cyl(.09, 2.2, loc=(0, y1 + .1, .9 + i * .19), rot=(0, R90, 0), seg=7, bevel=0)
    for x in (-1.0, 1.0):
        a.part('Kit_straps', 'Steel').box((.04, .25, .65), loc=(x, y1 + .1, 1.1), bevel=0)
    K.jerrycan(a.part('Jerrycans', 'Crate'), (.8, y1 + .12, .45))
    # The anti-drone net: a tube frame standing off the front and over the front half of the roof, the net on it.
    W.cable(a.part('Net_frame', 'Steel'), [(-half, y0 - .5, zb + .3), (-half, y0 - .5, ze + .2),
                                          (half, y0 - .5, ze + .2), (half, y0 - .5, zb + .3)], r=.03)
    K.net_armour(a, (-half, y0, 0), (half, y0, 0), zb + .3, ze - zb - .1, (0, -1, 0), cell=.32, standoff=.48)
    net = a.part('Anti_drone_net', 'Canvas')
    for i in range(7):
        y = y0 - .3 + i * .55
        net.tube([(-half - .05, y, ze + .05), (0, y + .1, zr + .25), (half + .05, y, ze + .05)], .012, seg=3,
                 caps=False)
    for x in (-1.0, 0, 1.0):
        net.tube([(x, y0 - .5, zr + .1 - abs(x) * .4), (x, y0 + 3.0, zr + .1 - abs(x) * .4)], .012, seg=3, caps=False)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.012, 2.4, .14), loc=(s * (half + .045), -.6, 1.85), bevel=0)
    a.part('Team_band', 'Team').box((1.2, .8, .012), loc=(0, .8, zr + .02), rot=(0, 0, 0), bevel=0)


# ============================================================================= laser_tank
def laser_tank(a):
    """The laser tank-hunter: see the module docstring. Runtime: Turret, Main_cannon (the beam director head, which
    elevates), Muzzle_main (the mirror's centre), Point_fire, Point_exhaust."""
    TX, TW, WR = 1.1, .46, .3
    wheels = [-2.0 + i * .8 for i in range(6)]
    W.running_gear(a, TX, TW, WR, wheels, (-2.6, .55, .25), (2.6, .58, .27), rollers=(-1.2, 1.2), roller_z=.78,
                   top_hidden=.7, disc_mat='Armor', seg=8, link_pitch=.34, teeth=9)
    hull = a.part('Hull', 'Team')
    W.side_hull(hull, [(2.95, .45), (3.0, .95), (2.85, 1.24), (-1.2, 1.25), (-2.85, .9), (-2.95, .65),
                       (-2.65, .42)], 1.86, chamfer=.05)
    fen = a.part('Fenders', 'Team')
    for s in (-1, 1):
        K.fender(fen, TX, -2.85, 2.9, .88, .52, s)
        sk = a.part('Skirts', 'Team')
        for i in range(4):
            yc = -2.7 + (i + .5) * 1.35
            sk.box((.05, 1.3, .38), loc=(s * (TX + .3), yc, .7), bevel=0)
        a.part('Team_band', 'Team').box((.012, 1.8, .09), loc=(s * (TX + .33), -.5, .74), bevel=0)
    # Driver's hatch and vision blocks, lamps, tow hooks on the nose.
    hc = (.45, -1.6, 1.26)
    k.ring(a.part('Hatches', 'Armor'), [(.22, 0), (.27, 0), (.27, .05), (.22, .05)], loc=hc, seg=10)
    k.lathe(a.part('Hatches', 'Armor'), [(0, .08), (.18, .075), (.23, .05), (.23, .02)], loc=hc, seg=10)
    for dx in (.27, .45, .63):
        a.part('Sight', 'Armor').box((.14, .09, .07), loc=(dx, -1.93, 1.22), rot=(-.4, 0, 0), bevel=0)
        a.part('Glass', 'Glass').box((.11, .01, .045), loc=(dx, -1.98, 1.21), rot=(-.4, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .95, -2.88, .98), (0, -1, .1), r=.07, guard=False)
        K.tow_hook(a.part('Kit_tow', 'Steel'), (s * .6, -2.97, .62), facing=(0, -1, 0), size=.1)
    # The remote weapon station (7.62 mm, self-defence) on the hull front left: the post, the cradle, the sensor box.
    rws = a.part('Rws', 'Armor')
    rws.cyl(.09, .28, loc=(-.55, -1.3, 1.39), seg=8, bevel=0)
    K.chamfer_box(rws, (.3, .42, .2), loc=(-.55, -1.32, 1.63), c=.03)
    K.chamfer_box(rws, (.14, .16, .16), loc=(-.75, -1.42, 1.66), c=.02)
    a.part('Glass', 'Glass').box((.1, .01, .08), loc=(-.75, -1.505, 1.67), bevel=0)
    k.lathe(a.part('Rws_gun', 'Steel'), [(.025, 0), (.025, .7), (.035, .72), (0, .74)], loc=(-.5, -1.5, 1.64),
            rot=K.FORWARD, seg=6)
    K.chamfer_box(a.part('MG_ammo', 'Armor'), (.12, .22, .16), loc=(-.35, -1.25, 1.62), c=.02)
    # Engine deck: grille, the power pack's two exhausts, the generator's louvres on the rear plate.
    K.grille(a, (0, 2.2, 1.245), 1.2, .9, facing=(0, 0, 1), slats=5, frame_mat='Team')
    K.grille(a, (0, 2.97, .92), 1.1, .24, facing=(0, 1, 0), slats=3, frame_mat='Armor')
    for s in (-1, 1):
        K.exhaust(a, (s * .8, 2.75, 1.25), r=.07, length=.42, direction=(0, .3, 1))
        a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .06), loc=(s * .95, 2.97, 1.1), bevel=0)
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.42, .8, .28), (TX, 1.6, .88))
    K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.42, .6, .28), (-TX, 1.75, .88))
    a.pivot('Point_fire', (0, 2.1, 1.4))
    a.pivot('Point_exhaust', (1.0, 3.0, 1.0))
    _laser_turret(a)
    k.clean(a)


def _laser_turret(a):
    t = a.pivot('Turret', (0, -.3, 1.32))
    body = a.part('Turret_body', 'Team', t)
    W.poly_turret(body, [
        (-.05, [(-.8, -.95), (.8, -.95), (1.05, -.5), (1.05, 1.2), (.85, 1.45), (-.85, 1.45), (-1.05, 1.2),
                (-1.05, -.5)]),
        (.42, [(-.65, -.85), (.65, -.85), (.92, -.42), (.92, 1.1), (.75, 1.35), (-.75, 1.35), (-.92, 1.1),
               (-.92, -.42)])], chamfer=.04)
    k.ring(a.part('Turret_steel', 'Steel', t), [(.82, -.08), (.95, -.08), (.95, .02), (.82, .02)], seg=16)
    # Radiator banks on both sides: angled panels with glowing cores and their fan housings.
    for s in (-1, 1):
        rad = a.part('Radiators', 'Armor', t)
        K.chamfer_box(rad, (.14, 1.3, .55), loc=(s * 1.08, .45, .3), rot=(0, s * .25, 0), c=.02)
        for i in range(6):
            a.part('Radiator_glow', 'Energy', t).box((.02, .16, .4), loc=(s * 1.16, -.05 + i * .2, .32),
                                                     rot=(0, s * .25, 0), bevel=0)
        k.lathe(a.part('Radiator_fans', 'Steel', t), [(.2, 0), (.2, .06), (.16, .08), (0, .09)],
                loc=(s * .55, .95, .42), seg=12)
    # The power cabinet at the rear, the IRST ball and a whip antenna.
    K.chamfer_box(a.part('Power_cabinet', 'Armor', t), (1.3, .5, .35), loc=(0, 1.15, .58), c=.04)
    for i in range(4):
        a.part('Kit_handles', 'Steel', t).box((.18, .02, .02), loc=(-.45 + i * .3, 1.41, .62), bevel=0)
    k.lathe(a.part('Sensor', 'Armor', t), [(.0, 0), (.12, 0), (.14, .08), (.12, .18), (0, .2)], loc=(.62, -.55, .42),
            seg=10)
    a.part('Glass', 'Glass', t).box((.12, .02, .07), loc=(.62, -.69, .52), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.7, 1.15, .42), h=.55, lean=.3)
    for s in (-1, 1):
        K.smoke_dischargers(a, .85, -.6, .25, s, count=3, parent=t)
    a.part('Team_band', 'Team', t).box((.9, .5, .012), loc=(0, .2, .425), bevel=0)
    # The fork: two arms up from a turntable, the trunnions, the beam director head (Main_cannon) with its big
    # round mirror, the hood over it and the lens in the middle.
    fork = a.part('Director_trunnions', 'Armor', t)
    k.lathe(fork, [(.5, 0), (.5, .08), (.42, .12), (0, .12)], loc=(0, -.35, .42), seg=14)
    for s in (-1, 1):
        fork.limb((s * .74, -.35, .48), (s * .74, -.85, .88), .14, .22, bevel=0)
        a.part('Cradle', 'Steel', t).cyl(.1, .12, loc=(s * .68, -.85, .88), rot=(0, R90, 0), seg=10, bevel=0)
    head = a.part('Main_cannon', 'Armor', t)
    k.lathe(head, [(.0, -.5), (.45, -.46), (.6, -.27), (.63, .05), (.6, .12)], loc=(0, -.85, .88), rot=K.FORWARD,
            seg=16)
    k.lathe(a.part('Main_cannon_hood', 'Team', t), [(.64, -.02), (.67, .02), (.67, .15), (.61, .17)],
            loc=(0, -.85, .88), rot=K.FORWARD, seg=16)
    k.lathe(a.part('Main_cannon_lens', 'Energy', t), [(0, .14), (.36, .13), (.52, .11)], loc=(0, -.85, .88),
            rot=K.FORWARD, seg=16, caps=(False, True))
    k.lathe(a.part('Main_cannon_head', 'Steel', t), [(.08, .1), (.08, .2), (.05, .26), (0, .27)],
            loc=(0, -.85, .88), rot=K.FORWARD, seg=10)
    a.pivot('Muzzle_main', (0, -1.41, .88), t)


# ============================================================================= aa_57mm_vehicle
def aa_57mm_vehicle(a):
    """2S38 Derivatsiya-PVO: see the module docstring. Runtime: Turret, Main_cannon, Muzzle_brake, Muzzle_main,
    Radar (spins), Point_fire, Point_exhaust."""
    TX, TW, WR = 1.0, .42, .29
    wheels = [-1.85 + i * .72 for i in range(6)]
    W.running_gear(a, TX, TW, WR, wheels, (-2.4, .5, .24), (2.5, .52, .25), rollers=(-1.1, .3, 1.6), roller_z=.74,
                   top_hidden=.68, disc_mat='Armor', seg=8, link_pitch=.32, teeth=9)
    hull = a.part('Hull', 'Team')
    # The BMP-3's hull: the long flat nose with the trim vane folded on it, the low deck, the high square stern.
    W.side_hull(hull, [(2.95, .4), (2.98, 1.1), (2.75, 1.14), (-.6, 1.05), (-1.9, .92), (-2.65, .7),
                       (-2.62, .52), (-2.3, .38)], 2.0, chamfer=.04)
    tub = a.part('Hull_tub', 'Armor')
    W.side_hull(tub, [(2.8, .3), (-2.1, .3), (-2.35, .5), (2.8, .5)], 1.55, chamfer=.03)
    vane = a.part('Trim_vane', 'Team')
    vane.box((1.9, .5, .05), loc=(0, -2.25, .93), rot=(-.55, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Steel', 'Steel').box((.05, .25, .05), loc=(s * .8, -2.05, 1.0), bevel=0)
    fen = a.part('Fenders', 'Team')
    for s in (-1, 1):
        K.fender(fen, TX, -2.55, 2.85, .8, .46, s)
        sk = a.part('Skirt_edge', 'Rubber')
        sk.box((.03, 5.0, .2), loc=(s * (TX + .23), .15, .68), bevel=0)
        a.part('Team_band', 'Team').box((.012, 1.6, .09), loc=(s * (TX + .26), -.5, .86), bevel=0)
    # Driver's hatch between two crew hatches on the nose, vision blocks, lamps, tow hooks.
    for x in (-.55, 0, .55):
        hc = (x, -1.45, 1.0)
        k.ring(a.part('Hatches', 'Armor'), [(.17, 0), (.21, 0), (.21, .05), (.17, .05)], loc=hc, seg=10)
        k.lathe(a.part('Hatches', 'Armor'), [(0, .07), (.15, .065), (.18, .04), (.18, .02)], loc=hc, seg=10)
        a.part('Sight', 'Armor').box((.12, .08, .06), loc=(x, -1.72, .98), rot=(-.4, 0, 0), bevel=0)
    for s in (-1, 1):
        K.lamp(a, (s * .78, -2.5, .86), (0, -1, .1), r=.06, guard=False)
        K.tow_hook(a.part('Kit_tow', 'Steel'), (s * .5, -2.66, .55), facing=(0, -1, 0), size=.09)
        # The stern doors (the BMP-3's rear exit over the engine), the water-jet covers under them.
        d = a.part('Rear_doors', 'Team')
        d.box((.6, .04, .55), loc=(s * .35, 2.99, .72), bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * .3 - .1, 3.02, .8), (s * .3 + .1, 3.02, .8), (0, 1, 0), h=.04)
        a.part('Jet_covers', 'Armor').cyl(.16, .06, loc=(s * .75, 2.98, .45), rot=K.FORWARD, seg=10, bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .02, .06), loc=(s * .88, 2.99, 1.02), bevel=0)
    # Engine deck: louvres, the exhaust on the right, stowage boxes on the rear fenders.
    K.grille(a, (0, 2.2, 1.125), 1.1, .7, facing=(0, 0, 1), slats=5, frame_mat='Team')
    K.grille(a, (-.85, 1.7, 1.0), .25, .6, facing=(-1, 0, .3), slats=3, frame_mat='Armor')
    for s in (-1, 1):
        K.crate(a.part('Stowage', 'Armor'), a.part('Kit_latches', 'Steel'), (.38, .7, .26), (s * TX, 2.15, .8))
    a.pivot('Point_fire', (0, 1.0, 1.1))
    a.pivot('Point_exhaust', (.7, 2.95, .85))
    _aa57_turret(a)
    k.clean(a)


def _aa57_turret(a):
    """The AU-220M unmanned module: a low angular house, the 57 mm gun in its armoured cradle with the feed housing
    on the left, the coax, the sight drum on the roof, smoke launchers, the radar on a mast at the rear."""
    t = a.pivot('Turret', (0, .5, 1.05))
    body = a.part('Turret_body', 'Team', t)
    W.poly_turret(body, [
        (0, [(-.7, -1.0), (.7, -1.0), (1.0, -.4), (1.0, .95), (.8, 1.15), (-.8, 1.15), (-1.0, .95), (-1.0, -.4)]),
        (.32, [(-.62, -1.12), (.62, -1.12), (1.02, -.45), (1.02, 1.0), (.82, 1.2), (-.82, 1.2), (-1.02, 1.0),
               (-1.02, -.45)]),
        (.6, [(-.5, -.9), (.5, -.9), (.85, -.35), (.85, .9), (.7, 1.05), (-.7, 1.05), (-.85, .9), (-.85, -.35)])],
        chamfer=.04)
    k.ring(a.part('Turret_armor', 'Armor', t), [(.8, -.07), (.9, -.07), (.9, .02), (.8, .02)], seg=16)
    K.chamfer_box(a.part('Mantlet', 'Armor', t), (.5, .42, .5), loc=(0, -1.18, .42), c=.05)
    K.chamfer_box(a.part('Feed_housing', 'Armor', t), (.32, .7, .3), loc=(.42, -.8, .62), c=.04)
    K.gun_barrel(a, 'Main_cannon', t, 0, -1.38, .42, 1.57, .055, seg=10, extractor=(.3, 1.3, .3),
                 brake_name='Muzzle_brake', brake='baffle', sleeve=1.55)
    a.pivot('Muzzle_main', (0, -3.25, .42), t)
    k.lathe(a.part('MG_coax', 'Steel', t), [(.02, 0), (.02, .4), (0, .41)], loc=(-.3, -1.32, .36), rot=K.FORWARD,
            seg=6)
    # The sight drum (gunner's optical-electronic sight) and its glass, the commander's panoramic head.
    k.lathe(a.part('Sight_drum', 'Armor', t), [(.22, 0), (.22, .28), (.18, .32), (0, .33)], loc=(-.48, -.45, .6),
            seg=12)
    a.part('Sight_glass', 'Glass', t).box((.2, .02, .12), loc=(-.48, -.67, .76), bevel=0)
    K.periscope(a, (.5, .15, .6), facing=(0, -1, 0), parent=t, size=(.2, .18, .18))
    for s in (-1, 1):
        K.smoke_dischargers(a, .95, -.3, .3, s, count=3, parent=t)
        K.crate(a.part('Stowage', 'Armor', t), a.part('Kit_latches', 'Steel', t), (.16, .6, .26), (s * 1.1, .45, .1),
                bands=1)
    a.part('Team_band', 'Team', t).box((.8, .5, .012), loc=(0, .25, .605), bevel=0)
    # The radar mast on the turret rear and the spinning panel array.
    mast = a.part('Radar_mast', 'Steel', t)
    mast.cyl(.07, .4, loc=(0, .7, .8), seg=8, bevel=0)
    for s in (-1, 1):
        mast.limb((s * .25, .55, .6), (0, .7, .9), .04, .04, bevel=0)
    r = a.pivot('Radar', (0, .7, 1.0), t)
    K.chamfer_box(a.part('Radar_panel', 'Armor', r), (.85, .12, .48), loc=(0, -.05, .26), c=.02)
    a.part('Radar_back', 'Steel', r).box((.5, .14, .2), loc=(0, .08, .2), bevel=0)
    a.part('Radar_face', 'Undercarriage', r).box((.75, .01, .38), loc=(0, -.115, .26), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.7, .95, .6), h=.5, lean=.25)


BUILDERS = {
    'twin_tank': (twin_tank, dict(ao_distance=.5, grime_height=.6)),
    'titan_tank': (titan_tank, dict(ao_distance=.6, grime_height=.6)),
    'turtle_tank': (turtle_tank, dict(ao_distance=.5, grime_height=.6)),
    'laser_tank': (laser_tank, dict(ao_distance=.5, grime_height=.6)),
    'aa_57mm_vehicle': (aa_57mm_vehicle, dict(ao_distance=.5, grime_height=.6)),
}
