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


BUILDERS = {
    'twin_tank': (twin_tank, dict(ao_distance=.5, grime_height=.6)),
}
