"""Prompt 35 wave 8 (lane A): the gunship helicopter and the flying boss rebuilt from scratch, each from its own spec
(Tools/blender/specs/<id>.json), on the kit35 library and the wave 5 loft helpers (body_loft, span_loft). DECISIONS
"Prompt 35 wave 8 (lane A)". attack_helicopter and fighter_jet are the owner's gold (prompt 27 V2): not here.

- gunship_heli: Mi-24P Hind (sheet: 0.4 x): the stepped tandem "double bubble" canopies, the troop cabin with its
  door windows (the door guns), the two engines on top with their intakes and sideways exhausts, the five-blade
  rotor, the tail boom with the fin and the three-blade tail rotor on the left, the anhedral stub wings with
  rocket pods inboard and the ATGM tubes on the tip rails, the chin gun turret, the tricycle gear, the flare
  dispensers on the boom.

Runtime nodes are the old models' (positions within a few centimetres of the old pivots): see each builder.
Metres, +Z up, -Y front, +X left.
"""
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
from mb_p35_wave5_air import FOIL14, body_loft, resample, span_loft

R90 = math.pi / 2
TAU = math.tau
ACROSS = (0, R90, 0)


# ============================================================================= gunship_heli (Mi-24P)
def gunship_heli(a):
    """See the module docstring. Runtime: Rotor, Tail_rotor, Mount_gun / Muzzle_gun (chin turret), Muzzle_rocket /
    .001 (pods), Muzzle_missile / .001 (wing-tip tubes), Muzzle_door_l / _r, Pods, Pod_face, Launch_tubes,
    Point_fire, Point_exhaust; mb_flare_mounts adds Mount_Flare_* at the Flares dispensers."""
    K.suffixed(a)
    fus = a.part('Fuselage', 'Team')
    body_loft(fus, resample([(-3.35, .06, .55, .7, .5), (-3.2, .24, .42, .86, .45), (-2.9, .34, .36, .95, .42),
                             (-2.4, .42, .33, 1.02, .42), (-1.9, .5, .32, 1.12, .42), (-1.2, .55, .3, 1.3, .45),
                             (-.2, .56, .3, 1.36, .45), (.5, .5, .36, 1.34, .5), (1.0, .32, .62, 1.22, .5),
                             (2.0, .16, .86, 1.12, .5), (3.0, .12, .92, 1.1, .5), (3.55, .08, .95, 1.12, .5)], 24),
              smooth=.08)
    # The double bubble: the gunner's canopy low in front, the pilot's raised behind it, their frames.
    cg = a.part('Canopy', 'Glass')
    k.lathe(cg, [(0, -.32), (.24, -.25), (.3, -.05), (.27, .15), (.15, .3), (0, .34)], loc=(0, -2.75, .95),
            rot=(-R90 * .95, 0, 0), seg=10)
    k.lathe(cg, [(0, -.36), (.3, -.28), (.36, -.05), (.33, .2), (.18, .36), (0, .4)], loc=(0, -2.05, 1.2),
            rot=(-R90 * .95, 0, 0), seg=10)
    fr = a.part('Canopy_frames', 'Armor')
    for y, z, w in ((-2.95, 1.0, .28), (-2.55, 1.1, .3), (-2.3, 1.25, .34), (-1.8, 1.42, .34)):
        fr.box((w * 2, .04, .05), loc=(0, y, z), bevel=0)
    fr.box((.04, 1.4, .04), loc=(0, -2.4, 1.32), rot=(-.25, 0, 0), bevel=0)
    # The cabin: door windows either side (the door guns poke out), the armoured side panels, the step.
    for s in (-1, 1):
        for y in (-1.15, -.5, .1):
            a.part('Windows', 'Glass').box((.02, .3, .22), loc=(s * .555, y, .88), bevel=0)
        a.part('Door_frames', 'Armor').box((.025, .5, .5), loc=(s * .56, -.5, .85), bevel=0)
        k.lathe(a.part('Gun', 'Steel'), [(.022, 0), (.022, .3), (0, .31)], loc=(s * .6, -.2, .75), rot=K.FORWARD,
                seg=6)
        K.panel(a, a.part('Armor', 'Armor'), (.7, .3), (s * .5, -2.3, .62), (s, 0, 0), t=.02, rivet=.15)
        a.part('Team_band', 'Team').box((.012, 1.4, .08), loc=(s * .54, -.6, .55), bevel=0)
    a.pivot('Muzzle_door_l', (.65, -.5, .75))
    a.pivot('Muzzle_door_r', (-.65, -.5, .75))
    # Engines on top: two nacelles with intakes (dust covers), the exhausts angled out, the oil cooler hump.
    nac = a.part('Engine_nacelles', 'Team')
    for s in (-1, 1):
        k.lathe(nac, [(.06, -.85), (.16, -.75), (.19, -.3), (.19, .6), (.12, .85)], loc=(s * .32, -.35, 1.42),
                rot=(-R90, 0, 0), seg=10)
        a.part('Intakes', 'Undercarriage').cyl(.14, .03, loc=(s * .32, -1.21, 1.42), rot=K.FORWARD, seg=10, bevel=0)
        a.part('Intake_covers', 'Armor').cyl(.17, .06, loc=(s * .32, -1.26, 1.42), rot=K.FORWARD, seg=10, bevel=0)
        k.lathe(a.part('Exhausts', 'Steel'), [(.11, 0), (.13, .22), (.1, .32)], loc=(s * .45, .2, 1.3),
                rot=(-R90, 0, s * .9), seg=10)
        K.soot(a, (s * .62, .3, 1.3), radius=.35, k=.4)
    K.chamfer_box(a.part('Oil_cooler', 'Armor'), (.36, .5, .22), loc=(0, .45, 1.5), c=.04)
    K.grille(a, (0, .2, 1.615), .3, .3, facing=(0, 0, 1), slats=4, frame_mat='Armor')
    # Mast and the five-blade rotor (Rotor spins).
    k.lathe(a.part('Mast', 'Steel'), [(.12, 1.45), (.09, 1.62), (.08, 1.72)], loc=(0, -.55, 0), seg=10)
    r = a.pivot('Rotor', (0, -.55, 1.72))
    K.rotor_head(a, r, 5, 3.2, .28, hub=.28, phase=R90)
    # Tail boom: fin with the tail rotor on the left, the stabilisers, the tail skid, the flares.
    K.fin(a.part('Fins', 'Team'), (2.9, .75), (3.35, .45), 1.0, z0=1.05, t=.09, cant=0)
    span_loft(a.part('Stabilizers', 'Team'), [(-.75, 2.65, 2.95, 1.0, .1), (0, 2.6, 2.98, 1.0, .1),
                                              (.75, 2.65, 2.95, 1.0, .1)], foil=FOIL14)
    tr = a.pivot('Tail_rotor', (.14, 3.4, 1.5))
    K.tail_rotor(a, tr, 3, .62, .12, side=1)
    a.part('Undercarriage', 'Steel').tube([(0, 3.3, .95), (0, 3.45, .62)], .025, seg=5)
    for s in (-1, 1):
        K.flare_dispenser(a, (s * .17, 2.0, .92), normal=(s, 0, -.3), cols=2, rows=2, cell=.05)
    # Stub wings with anhedral, pylons, the rocket pods inboard, the ATGM tubes on the tip rails.
    wg = a.part('Stub_wings', 'Team')
    for s in (-1, 1):
        fs = (0, .5, 1.0)
        span_loft(wg, [(s * (.5 + 1.25 * f), -1.0 + .15 * f, -.35 - .05 * f, .72 - .14 * f, .16)
                       for f in (fs if s > 0 else fs[::-1])], foil=FOIL14)
        a.part('Pylons', 'Armor').box((.06, .45, .18), loc=(s * 1.2, -.6, .55), bevel=0)
        k.lathe(a.part('Pods', 'Team'), [(0, -.45), (.13, -.4), (.14, .35), (.12, .45)], loc=(s * 1.2, -.22, .44),
                rot=(-R90, 0, 0), seg=10)
        a.part('Pod_face', 'Undercarriage').cyl(.12, .02, loc=(s * 1.2, -.67, .44), rot=K.FORWARD, seg=10, bevel=0)
        a.part('Pod_bands', 'Steel').cyl(.145, .04, loc=(s * 1.2, -.45, .44), rot=K.FORWARD, seg=10, bevel=0)
        a.part('Tip_rails', 'Armor').box((.06, .7, .4), loc=(s * 1.76, -.65, .58), bevel=0)
        for dz in (.08, -.08):
            k.lathe(a.part('Launch_tubes', 'Armor'), [(.045, -.45), (.05, -.4), (.05, .4)],
                    loc=(s * 1.66, -.55, .64 + dz), rot=(-R90, 0, 0), seg=8)
        a.part('Wing_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.04, .08, .04), loc=(s * 1.8, -.5, .8),
                                                                          bevel=0)
    a.pivot('Muzzle_rocket', (-1.2, -.67, .44))
    a.pivot('Muzzle_rocket__001', (1.2, -.67, .44))
    a.pivot('Muzzle_missile', (-1.66, -.97, .64))
    a.pivot('Muzzle_missile__001', (1.66, -.97, .64))
    # The chin gun turret (Mount_gun) with the twin-barrel 30 mm, the sensor and the air-data boom.
    m = a.pivot('Mount_gun', (0, -3.1, .42))
    k.lathe(a.part('Gun_turret', 'Armor', m), [(.16, -.08), (.18, .02), (.13, .1), (0, .12)], seg=10)
    for dx in (-.03, .03):
        k.lathe(a.part('Gun', 'Steel', m), [(.025, 0), (.025, .5), (.035, .52), (.035, .6), (0, .61)],
                loc=(dx, -.0, -.02), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_gun', (0, -.6, -.02), m)
    k.lathe(a.part('Sensor', 'Armor'), [(0, -.1), (.1, -.08), (.12, 0), (.1, .1), (0, .12)], loc=(.3, -3.0, .5),
            seg=8)
    a.part('Antennas', 'Steel').cyl(.012, .5, loc=(-.25, -3.45, .8), rot=K.FORWARD, seg=4, bevel=0)
    # The gear: nose pair, the mains on their trailing struts (Tyres, Undercarriage).
    for x in (-.08, .08):
        k.lathe(a.part('Tyres', 'Rubber'), [(.08, -.04), (.13, -.03), (.13, .03), (.08, .04)], loc=(x, -2.55, .13),
                rot=ACROSS, seg=10)
    a.part('Undercarriage', 'Steel').tube([(0, -2.5, .38), (0, -2.55, .13)], .03, seg=5)
    for s in (-1, 1):
        k.lathe(a.part('Tyres', 'Rubber'), [(.1, -.06), (.17, -.05), (.17, .05), (.1, .06)], loc=(s * .78, .3, .17),
                rot=ACROSS, seg=10)
        a.part('Undercarriage', 'Steel').tube([(s * .5, .2, .45), (s * .78, .3, .17)], .035, seg=5)
        a.part('Undercarriage', 'Steel').tube([(s * .52, -.2, .5), (s * .74, .25, .22)], .025, seg=5)
    K.beacon(a, (0, .9, 1.25), r=.05)
    a.pivot('Point_fire', (0, -.3, 1.2))
    a.pivot('Point_exhaust', (.45, .2, 1.26))
    k.clean(a)


# ============================================================================= mega_gunship (ACH-47 "Guns-A-Go-Go")
def _chinook_rotor(a, pivot, prefix, R, chord, phase, blades=3):
    """A three-blade Chinook rotor under its pivot: the hub with its droop stops, the blade grips and the long
    blades with their tip stripes."""
    hub = a.part(f'{prefix}_hub', 'Steel', pivot)
    k.lathe(hub, [(.42, -.1), (.46, 0), (.46, .12), (.3, .2), (.12, .32), (0, .34)], seg=12, worn=(1, 2))
    gr = a.part(f'{prefix}_grips', 'Armor', pivot)
    bl = a.part(f'{prefix}_blades', 'Armor', pivot)
    tp = a.part(f'{prefix}_tips', 'Hazard', pivot)
    for j in range(blades):
        u = phase + j * TAU / blades
        c, s_ = math.cos(u), math.sin(u)
        k.block(gr, (.9, .3, .14), loc=(c * .8, s_ * .8, .02), rot=(0, 0, u), chamfer=.02)
        for f0, f1, ch in ((1.2, R * .35, chord * 1.05), (R * .35, R * .7, chord), (R * .7, R - .45, chord * .9)):
            L = f1 - f0
            bl.box((L, ch, .05), loc=(c * (f0 + L / 2), s_ * (f0 + L / 2), .03 - f0 * .006), rot=(.05, 0, u),
                   bevel=0)
        tp.box((.45, chord * .92, .052), loc=(c * (R - .22), s_ * (R - .22), .03 - R * .006), rot=(.05, 0, u),
               bevel=0)


def mega_gunship(a):
    """See the module docstring (mega_gunship). Runtime (the def's parts): Mount_gun / .001 (gun_l / gun_r, the chin
    turrets), Mount_mg / .001 (minigun_l / _r, the forward windows), Rotor_rear (rotor_rear); Rotor, Muzzle_rocket /
    .001 (the stub pods), Muzzle_missile (the belly launcher), Mount_mg.002 / .003 (the door guns: the data's two
    boss_hmg); mb_flare_mounts adds Mount_Flare_*."""
    K.suffixed(a)
    fus = a.part('Fuselage', 'Team')
    # The Chinook box fuselage: the rounded nose, the long constant section, the rising rear ramp line.
    stations = resample([(-8.6, .25, 1.6, 2.2), (-8.2, .9, 1.2, 2.9), (-7.4, 1.25, 1.0, 3.25), (-6.4, 1.42, .95, 3.4),
                         (5.0, 1.42, .95, 3.45), (7.2, 1.38, 1.4, 3.5), (8.6, 1.2, 2.3, 3.55)], 22)
    rings = []
    for y, w, zb, zt in stations:
        zc = (zb + zt) / 2
        rings.append([(0, y, zb), (w * .85, y, zb + .1), (w, y, zc - (zc - zb) * .5), (w, y, zc + (zt - zc) * .4),
                      (w * .82, y, zt - .05), (0, y, zt), (-w * .82, y, zt - .05), (-w, y, zc + (zt - zc) * .4),
                      (-w, y, zc - (zc - zb) * .5), (-w * .85, y, zb + .1)])
    fus.loft(rings, bevel=0)
    # Cockpit glazing, the frames, the nose sensor.
    cg = a.part('Canopy', 'Glass')
    for s in (-1, 1):
        cg.mesh([(s * .3, -8.55, 2.3), (s * 1.0, -8.15, 2.35), (s * 1.0, -7.7, 3.05), (s * .3, -8.0, 3.0)],
                [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        cg.mesh([(s * 1.27, -7.9, 2.3), (s * 1.27, -7.0, 2.3), (s * 1.27, -7.0, 2.95), (s * 1.27, -7.7, 3.0)],
                [(0, 1, 2, 3) if s > 0 else (3, 2, 1, 0)])
        a.part('Canopy_frames', 'Armor').box((.04, .05, .8), loc=(s * .65, -8.15, 2.67), rot=(-.6, 0, 0), bevel=0)
    a.part('Canopy_frames', 'Armor').box((2.1, .06, .06), loc=(0, -8.0, 3.02), bevel=0)
    k.lathe(a.part('Sensor', 'Armor'), [(0, -.18), (.2, -.15), (.24, 0), (.2, .16), (0, .2)], loc=(0, -8.75, 1.4),
            seg=10)
    a.part('Lamps', 'Lamp').box((.16, .02, .1), loc=(0, -8.96, 1.42), bevel=0)
    # Cabin windows, frame bands, armour plates on the sides, the side door (right front), the team band.
    for s in (-1, 1):
        for y in (-3.4, -2.2, -1.0, .2, 1.4, 2.6, 3.8):
            a.part('Canopy', 'Glass').box((.03, .45, .45), loc=(s * 1.43, y, 2.45), bevel=0)
        for y in (-6.0, -3.0, 0.0, 3.0, 6.0):
            a.part('Frame_bands', 'Armor').box((.03, .08, 2.3), loc=(s * 1.44, y, 2.2), bevel=0)
        K.panel(a, a.part('Armor', 'Armor'), (2.4, .9), (s * 1.45, -5.4, 1.55), (s, 0, 0), t=.04, rivet=.3)
        a.part('Team_band', 'Team').box((.03, 11.0, .2), loc=(s * 1.44, -.5, 3.05), bevel=0)
        a.part('Nav_lights', 'LavaGlow' if s > 0 else 'SignalGreen').box((.05, .1, .05), loc=(s * 1.45, -7.0, 3.3),
                                                                         bevel=0)
    a.part('Door', 'Armor').box((.04, 1.1, 1.6), loc=(-1.44, -6.2, 1.95), bevel=0)
    # The Chinook's side fuel pods along the lower fuselage, their access panels and filler caps; the rear ramp.
    for s in (-1, 1):
        pod = a.part('Fuel_pods', 'Team')
        for y0, y1, w0, w1 in ((-3.6, -3.0, .1, .5), (-3.0, 3.8, .5, .5), (3.8, 4.6, .5, .1)):
            k.sharp_loft(pod, [[(s * 1.4, y0, 1.0), (s * (1.4 + w0), y0, 1.05), (s * (1.4 + w0), y0, 1.75),
                                (s * 1.4, y0, 1.85)],
                               [(s * 1.4, y1, 1.0), (s * (1.4 + w1), y1, 1.05), (s * (1.4 + w1), y1, 1.75),
                                (s * 1.4, y1, 1.85)]], chamfer=.04)
        for y in (-2.0, .4, 2.8):
            K.panel(a, a.part('Armor', 'Armor'), (1.1, .45), (s * 1.92, y, 1.42), (s, 0, 0), t=.02, rivet=.2)
        a.part('Steel', 'Steel').cyl(.06, .04, loc=(s * 1.85, -.8, 1.86), seg=8, bevel=0)
        K.handle(a.part('Kit_handles', 'Steel'), (s * 1.45, -6.6, 2.4), (s * 1.45, -6.6, 2.9), (s, 0, 0), h=.05)
    ramp = a.part('Ramp', 'Armor')
    k.block(ramp, (2.5, 1.5, .08), loc=(0, 8.15, 1.75), rot=(-.85, 0, 0), chamfer=.02)
    for x in (-1.0, 1.0):
        a.part('Kit_hinges', 'Steel').cyl(.06, .3, loc=(x, 7.6, 1.32), rot=(0, R90, 0), seg=8, bevel=0)
    for j in range(6):
        a.part('Ramp_ribs', 'Steel').box((2.2, .05, .04), loc=(0, 7.75 + j * .14, 1.4 + j * .12), rot=(-.85, 0, 0),
                                          bevel=0)
    # Pylon fairing panels, grilles and the hydraulic lines along the tunnel.
    for y in (-6.4, -5.2):
        K.grille(a, (.56, y, 3.85), .5, .3, facing=(1, 0, 0), slats=3, frame_mat='Armor')
    for s in (-1, 1):
        K.grille(a, (s * .62, 6.8, 4.6), .9, .5, facing=(s, 0, 0), slats=4, frame_mat='Armor')
        a.part('Kit_cables', 'Rubber').tube([(s * .3, -4.4, 3.6), (s * .3, 0, 3.65), (s * .3, 4.6, 3.6)], .03, seg=4)
    # The two pylons: the low forward one and the tall aft one with its engines either side.
    k.sharp_loft(a.part('Fuselage', 'Team'), [[(-.8, -7.3, 3.35), (.8, -7.3, 3.35), (.8, -4.4, 3.4), (-.8, -4.4, 3.4)],
                                              [(-.55, -6.6, 4.3), (.55, -6.6, 4.3), (.55, -5.0, 4.3),
                                               (-.55, -5.0, 4.3)]], chamfer=.05)
    k.sharp_loft(a.part('Fuselage', 'Team'), [[(-1.0, 4.6, 3.4), (1.0, 4.6, 3.4), (1.0, 8.2, 3.5), (-1.0, 8.2, 3.5)],
                                              [(-.6, 5.6, 5.3), (.6, 5.6, 5.3), (.6, 7.9, 5.3), (-.6, 7.9, 5.3)]],
                 chamfer=.05)
    a.part('Steel', 'Steel').box((.5, 10.0, .25), loc=(0, .5, 3.55), bevel=0)       # the drive-shaft tunnel
    for s in (-1, 1):
        k.lathe(a.part('Engines', 'Armor'), [(.08, -1.2), (.4, -1.1), (.45, -.6), (.45, .7), (.35, 1.05),
                                             (.3, 1.15)], loc=(s * 1.25, 6.5, 4.0), rot=(-R90, 0, 0), seg=12)
        a.part('Intake_screens', 'Undercarriage').cyl(.36, .03, loc=(s * 1.25, 5.3, 4.0), rot=K.FORWARD, seg=12,
                                                      bevel=0)
        a.part('Soot', 'Charred').cyl(.28, .05, loc=(s * 1.25, 7.66, 4.0), rot=K.BACKWARD, seg=10, bevel=0)
        K.soot(a, (s * 1.25, 7.8, 4.0), radius=.6, k=.45)
        a.part('Steel', 'Steel').box((.3, .8, .25), loc=(s * .85, 6.5, 3.75), bevel=0)
    r = a.pivot('Rotor', (0, -5.8, 4.6))
    _chinook_rotor(a, r, 'Rotor', 7.6, .62, R90)
    rr = a.pivot('Rotor_rear', (0, 6.7, 5.66))
    _chinook_rotor(a, rr, 'Rotor_rear', 7.6, .62, -R90)
    # Stub pylons with the rocket pods (pod_l / pod_r), the belly missile launcher, the gear.
    for i, s in ((0, 1), (1, -1)):
        k.block(a.part('Pylons', 'Armor'), (1.2, .9, .16), loc=(s * 2.0, -.85, 1.6), rot=(0, s * -.12, 0), chamfer=.02)
        a.part('Pylons', 'Armor').box((.1, .7, .4), loc=(s * 2.67, -.85, 1.65), bevel=0)
        k.lathe(a.part('Pods', 'Team'), [(0, -.55), (.24, -.48), (.26, .45), (.22, .6)], loc=(s * 2.67, -.75, 1.4),
                rot=(-R90, 0, 0), seg=10)
        tubes = a.part('Pod_tubes', 'Undercarriage')
        for j in range(7):
            u = j * TAU / 6 if j else 0
            rr_ = .14 if j else 0
            tubes.cyl(.05, .02, loc=(s * 2.67 + math.cos(u) * rr_, -1.31, 1.4 + math.sin(u) * rr_), rot=K.FORWARD,
                      seg=6, bevel=0)
        a.part('Wing_lights', 'Lamp').box((.06, .08, .05), loc=(s * 2.95, -.85, 1.65), bevel=0)
        a.pivot(K.name('Muzzle_rocket', i), (s * 2.67, -1.3, 1.4))
    K.chamfer_box(a.part('Missile_rack', 'Armor'), (.9, 1.4, .3), loc=(0, -.35, .95), c=.03)
    for dx in (-.25, .25):
        K.store(a, (dx, .1, .7), .07, 1.3, body='Missiles', body_mat='Fuel', fins='Missile_fins', seg=8)
        a.part('Missile_noses', 'Glass').cyl(.05, .03, loc=(dx, -1.21, .7), rot=K.FORWARD, seg=6, bevel=0)
    a.pivot('Muzzle_missile', (0, -1.25, .7))
    gear = a.part('Gear', 'Steel')
    for x, y in ((-1.0, -5.0), (1.0, -5.0), (-1.1, 5.6), (1.1, 5.6)):
        gear.tube([(x * .8, y, 1.0), (x, y, .35)], .06, seg=6)
        k.lathe(a.part('Tyres', 'Rubber'), [(.14, -.1), (.3, -.09), (.3, .09), (.14, .1)], loc=(x, y, .3),
                rot=(0, R90, 0), seg=12)
    a.part('Undercarriage', 'Armor').box((2.4, .3, .25), loc=(0, -5.0, .95), bevel=0)
    # The chin gun turrets (gun_l Mount_gun at x .56, gun_r Mount_gun.001) and the forward miniguns.
    for i, s in ((0, 1), (1, -1)):
        m = a.pivot(K.name('Mount_gun', i), (s * .56, -7.1, 1.1))
        tg = '' if i == 0 else '_001'
        k.lathe(a.part(f'Gun_turret{tg}', 'Armor', m), [(.3, -.12), (.32, .02), (.24, .14), (0, .16)], seg=10)
        k.lathe(a.part(f'Gun{tg}', 'Steel', m), [(.05, 0), (.05, 1.3), (.07, 1.33), (.07, 1.42), (0, 1.43)],
                loc=(0, -.2, -.2), rot=K.FORWARD, seg=8)
        K.chamfer_box(a.part(f'Gun{tg}', 'Steel', m), (.2, .45, .2), loc=(0, .05, -.18), c=.02)
        a.pivot(K.name('Muzzle_gun', i), (0, -1.62, -.2), m)
    for i, s in ((0, 1), (1, -1)):
        m = a.pivot(K.name('Mount_mg', i), (s * 1.52, -4.6, 1.7))
        tg = '' if i == 0 else '_001'
        k.lathe(a.part(f'Door_gun_mount{tg}', 'Armor', m), [(.18, -.1), (.2, 0), (.15, .14), (.1, .3)], seg=8)
        bar = a.part(f'Door_gun_barrels{tg}', 'Steel', m)
        for j in range(6):
            u = j * TAU / 6
            bar.cyl(.018, .8, loc=(math.cos(u) * .05, -.62 + .0, .56 + math.sin(u) * .05), rot=(R90 - .5, 0, 0),
                    seg=4, bevel=0)
        K.chamfer_box(a.part(f'Door_gun{tg}', 'Steel', m), (.2, .4, .2), loc=(0, -.1, .38), c=.02)
        a.pivot(K.name('Muzzle_mg', i), (0, -1.02, .56), m)
    # The door guns at the rear cabin windows (the data's two boss_hmg: Mount_mg.002 left, .003 right).
    for i, s in ((2, 1), (3, -1)):
        m = a.pivot(K.name('Mount_mg', i), (s * 1.55, 3.2, 2.1))
        tg = f'_{i:03d}'
        a.part(f'Door_gun_mount{tg}', 'Steel', m).cyl(.05, .35, loc=(0, 0, .1), seg=6, bevel=0)
        k.lathe(a.part(f'Door_gun{tg}', 'Steel', m), [(.035, 0), (.035, .75), (.05, .78), (.05, .86), (0, .87)],
                loc=(0, -.05, .3), rot=K.FORWARD, seg=6)
        K.chamfer_box(a.part(f'Door_gun{tg}', 'Steel', m), (.14, .3, .16), loc=(0, .1, .3), c=.015)
        a.pivot(K.name('Muzzle_mg', i), (0, -.92, .3), m)
    for s in (-1, 1):
        K.flare_dispenser(a, (s * 1.43, 4.0, 1.7), normal=(s, 0, -.3), cols=2, rows=2, cell=.07)
    K.beacon(a, (0, 1.5, 3.7), r=.08)
    K.whip_antenna(a.part('Steel', 'Steel'), (.3, -2.0, 3.65), h=.6, lean=.3)
    k.clean(a)


BUILDERS = {
    'gunship_heli': (gunship_heli, dict(ao_distance=.4, grime_height=.3, ao_strength=.65)),
    'mega_gunship': (mega_gunship, dict(ao_distance=.8, grime_height=.5, ao_strength=.75)),
}
