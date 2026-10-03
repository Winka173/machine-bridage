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


BUILDERS = {
    'gunship_heli': (gunship_heli, dict(ao_distance=.4, grime_height=.3, ao_strength=.65)),
}
