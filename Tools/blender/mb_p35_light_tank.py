"""Prompt 35 wave 3 (lane B): the light tank rebuilt from scratch (spec: Tools/blender/specs/light_tank.json).

An amphibious light tank of the PT-76 / ZBD-05 line (unit_sheet: a low boat-shaped hull, a small turret set forward,
a long slim 57 mm gun; 0.8 x the real vehicles; the def's modelSize 6.39 x 2.61 x 1.89 m): the welded boat hull with
its pointed bow seen from above, the folded trim vane on the bow plate, the bilge and the two water-jet ports at the
stern, the driver's hatch with periscopes; six road wheels a side, the rear sprocket and the front idler, a linked
track, side skirts with rubber flaps over the top run; the compact angular turret on a ring forward of the middle:
the mantlet with the long 57 mm barrel (multi-slot brake, a fume extractor, the gun-launched ATGM fires from the same
bore), the coaxial machine gun, the gunner's sight head, the commander's cupola with periscopes and a 7.62 mm pintle
gun on its post (MODEL_STANDARD "Roof guns"), smoke grenade launchers on both turret flanks, the rear turret bin;
on the engine deck the grilles, the snorkel stowed, a tarpaulin and two crates; Team bands.

`detail=True` (the `_hd` twin for PC High) gives the wheels, links and turret more segments.
Its own hull: no shape is taken from the BMPT or the other tanks.
Runtime nodes kept: `Turret`, `Main_cannon`, `Muzzle_brake`, `Muzzle_main`, `Coax`, `Muzzle_coax`, `Point_exhaust`,
`Point_fire`; named for the gate: `Mantlet`, `Idlers`, `Skirts`, `Mount_mg`, `Smoke_launchers`, `Stowage`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35b_parts as P

R90 = math.pi / 2
TX, TW = 1.0, .4
WR = .27
WHEELS = (-1.72, -1.08, -.44, .2, .84, 1.48)
DECK = 1.1
TURRET = (0, -.55, DECK)


def _hull(a, d):
    hull = a.part('Hull', 'Team')
    # Plan sections bottom to deck: the boat bow pointed in plan, the stern square with a slight rake.
    def ring(z, half, nose, tail, bow):
        return [(-half, tail, z), (-half, nose + bow, z), (-half * .45, nose + bow * .25, z), (0, nose, z),
                (half * .45, nose + bow * .25, z), (half, nose + bow, z), (half, tail, z)]
    rings = [ring(.38, .78, -2.25, 2.55, .55), ring(.78, 1.2, -2.85, 2.62, .9), ring(DECK, 1.18, -2.62, 2.6, .85)]
    k.sharp_loft(hull, rings, chamfer=.04)
    # The trim vane folded on the bow plate, its hinges; headlamps in guards; tow hooks.
    vane = a.part('Trim_vane', 'Armor')
    k.extrude(vane, [(-.75, 0), (.75, 0), (.6, .55), (-.6, .55)], .035, loc=(0, -2.62, .95), rot=(R90 - .75, 0, 0),
              axis='Z', chamfer=.01)
    for x in (-.5, .5):
        K.hinge(a.part('Kit_hinges', 'Steel'), (x - .1, -2.68, .9), (x + .1, -2.68, .9), r=.02, knuckles=2)
    for s in (-1, 1):
        K.lamp(a, (s * .78, -2.25, 1.12), (0, -1, .1), r=.055, mat='Armor', guard=True)
        K.tow_hook(a.part('Kit_hooks', 'Steel'), (s * .5, -2.7, .66), facing=(0, -1, 0), size=.07)
    # The driver's hatch and periscopes on the bow deck (centre), the engine deck grilles, the exhaust.
    K.hatch_round(a, (0, -1.75, DECK), r=.26, periscopes=3, seg=10 if not d else 14)
    K.grille(a, (0, 1.45, DECK + .02), 1.3, .8, facing=(0, 0, 1), slats=6, frame_mat='Armor')
    K.grille(a, (-.75, 2.2, DECK + .02), .5, .35, facing=(0, 0, 1), slats=3, frame_mat='Armor')
    a.part('Exhaust_louvres', 'Undercarriage').box((.5, .02, .18), loc=(.6, 2.62, 1.0), bevel=0)
    a.pivot('Point_exhaust', (.6, 2.66, 1.0))
    K.soot(a, (.6, 2.66, 1.0), radius=.45, k=.4)
    a.pivot('Point_fire', (0, 1.2, 1.35))
    # The stern: two water-jet ports, their covers, the tail lamps, the rear tow pintle.
    for s in (-1, 1):
        k.ring(a.part('Jet_ports', 'Undercarriage'), [(.13, 0), (.18, 0), (.18, .05), (.13, .05)],
               loc=(s * .55, 2.6, .62), rot=(-R90, 0, 0), seg=12)
        a.part('Jet_covers', 'Armor').box((.36, .03, .36), loc=(s * .55, 2.66, .85), rot=(-.5, 0, 0), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.1, .01, .06), loc=(s * 1.0, 2.61, 1.08), bevel=0)
    K.tow_hook(a.part('Kit_hooks', 'Steel'), (0, 2.62, .5), facing=(0, 1, 0), size=.08)
    # Deck stowage: the snorkel tube, a tarpaulin roll, two crates (the gate's stowage), Team bands on the sides.
    k.lathe(a.part('Snorkel', 'Armor'), [(.09, -.8), (.09, .8)], loc=(-.95, .9, DECK + .1), rot=K.FORWARD, seg=8)
    P.canvas_roll(a, (.2, 2.35, DECK + .1), 1.3, r=.1)
    st = a.part('Stowage', 'Crate')
    K.crate(st, a.part('Kit_straps', 'Steel'), (.5, .4, .28), (.85, .7, DECK), bands=1)
    K.crate(st, a.part('Kit_straps', 'Steel'), (.45, .4, .24), (.85, .25, DECK), rot=(0, 0, .1), bands=1)
    for s in (-1, 1):
        a.part('Team_band', 'Team').box((.012, 3.2, .1), loc=(s * 1.205, .1, .98), bevel=0)


def _skirts(a):
    sk = a.part('Skirts', 'Armor')
    rub = a.part('Skirt_flaps', 'Rubber')
    L = 4.4 / 5
    for s in (-1, 1):
        for i in range(5):
            yc = -2.05 + (i + .5) * L
            sk.box((.035, L - .03, .26), loc=(s * (TX + .23), yc, .88), bevel=0)
            rub.box((.02, L - .05, .1), loc=(s * (TX + .23), yc, .7), bevel=0)


def _turret(a, d):
    t = a.pivot('Turret', TURRET)
    body = a.part('Turret_body', 'Team', t)
    rings = []
    for z, f, w, r in ((0, -.85, .82, .95), (.32, -.9, .84, 1.0), (.55, -.55, .7, .9)):
        rings.append([(-w * .55, f, z), (w * .55, f, z), (w, f + .4, z), (w, r - .15, z), (w - .12, r, z),
                      (-w + .12, r, z), (-w, r - .15, z), (-w, f + .4, z)])
    k.sharp_loft(body, rings, chamfer=.035)
    K.turret_ring(a.part('Turret_steel', 'Steel', t), (0, 0, -.04), .78, h=.06)
    k.block(a.part('Turret_armor', 'Armor', t), (1.2, .5, .35), loc=(0, 1.05, .22), chamfer=.04)     # rear bin
    # The mantlet, the long 57 mm barrel with its fume extractor and multi-slot brake, the coax.
    k.block(a.part('Mantlet', 'Armor', t), (.42, .3, .3), loc=(0, -.92, .28), chamfer=.04)
    L = 1.8
    seg = 12 if d else 10
    k.lathe(a.part('Main_cannon', 'Steel', t), [(.07, 0), (.07, .25), (.048, .3), (.045, .95), (.07, 1.0),
                                                (.07, 1.3), (.045, 1.35), (.04, L), (0, L)],
            loc=(0, -1.07, .28), rot=K.FORWARD, seg=seg, worn=(1, 4))
    mb = a.part('Muzzle_brake', 'Undercarriage', t)
    k.lathe(mb, [(.04, 0), (.065, .02), (.065, .32), (.05, .34), (0, .34)], loc=(0, -1.07 - L, .28), rot=K.FORWARD,
            seg=seg)
    ports = a.part('Brake_ports', 'Charred', t)
    for j in range(4):
        for s in (-1, 1):
            ports.box((.01, .04, .03), loc=(s * .066, -1.07 - L - .06 - j * .07, .28), bevel=0)
    a.pivot('Muzzle_main', (0, -1.07 - L - .36, .28), t)
    k.lathe(a.part('Coax', 'Steel', t), [(.022, 0), (.022, .35), (0, .36)], loc=(.28, -.95, .24), rot=K.FORWARD, seg=6)
    a.pivot('Muzzle_coax', (.28, -1.32, .24), t)
    # The gunner's sight head (left), the commander's cupola (right) with its pintle MG on a post, smoke launchers.
    gs = a.part('Sight', 'Armor', t)
    k.block(gs, (.26, .32, .24), loc=(.45, -.45, .66), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.2, .01, .1), loc=(.45, -.615, .69), bevel=0)
    K.hatch_round(a, (-.4, .15, .55), r=.27, parent=t, periscopes=3, seg=14 if d else 10)
    for s in (-1, 1):
        K.smoke_dischargers(a, .76, -.35, .38, s, count=3, parent=t)
    P.raised_gun(a, (-.4, .5, .55), parent=t, pivot='Mount_mg', barrel='MG', brake='MG_flash', muzzle='Muzzle_mg',
                 riser=.02, ring_r=.18, post=.06, length=.8, shield=False, ring=False, mat='Armor', tag='_cdr')
    a.part('Team_band', 'Team', t).box((.9, .6, .015), loc=(0, .2, .555), bevel=0)
    K.whip_antenna(a.part('Turret_steel', 'Steel', t), (.6, .85, .55), h=.2, r=.018, lean=.15)


def light_tank(a, detail=False):
    """The light tank: see the module docstring."""
    _hull(a, detail)
    P.track_run(a, TX, TW, WHEELS, WR, sprocket=(2.22, .52, .25), idler=(-2.28, .46, .24), rollers=(),
                wheel_w=.15, hide_top=(-2.0, 2.0, .62), disc_mat='Armor', wheel_seg=12 if detail else 9,
                link_pitch=.18 if detail else .24)
    _skirts(a)
    _turret(a, detail)
    k.clean(a)


BUILDERS = {
    'light_tank': (light_tank, dict(ao_distance=.45, grime_height=.55)),
}
