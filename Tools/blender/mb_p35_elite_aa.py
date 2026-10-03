"""Prompt 35 wave 7 (lane C): the elite anti-aircraft tank rebuilt from scratch (spec: Tools/blender/specs/elite_aa.json).

A Skyranger 35 turret on the Leopard 1 hull (unit_refs: Skyranger 35 with AHEAD rounds, the Gepard as the base
chassis; the def's modelSize 7.41 x 3.52 x 3.36 m): the wedge nose and the long upper glacis, vertical sides behind
segmented skirts, seven road wheels a side with the front idler, the rear sprocket and four return rollers, the
engine deck with its grilles and the exhausts on the rear corners; the angular unmanned turret with faceted cheeks,
the def's two 35 mm revolver guns in armoured side pods (cradles, feed covers, ribbed barrels, muzzle sensors), the
search radar turning on its rear mast (`Radar`), the fixed fire-control radar panel on the turret front, the
electro-optical sensor head, the twin Stinger box on the right side (the def's `sam` secondary, aimed with the
turret), smoke dischargers, bins and aerials. Elite marks (DECISIONS 25B2): the team-coloured body, black armour
parts (EliteBlack), gilded bands and red-glowing sights.

Runtime nodes kept: `Turret`, `Main_cannon`, `Main_cannon_2`, `Muzzle_brake`, `Muzzle_brake_2`, `Muzzle_main`,
`Muzzle_missile`, `Radar`, `Radar_dish`, `Radar_mast`, `Launcher_box`, `Hatches`, `Point_exhaust`, `Point_fire`.
Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
BLACK = 'EliteBlack'
BODY = 'Team'
TX, TW = 1.3, .55
WR = .33
WHEELS = (-2.28, -1.55, -.82, -.09, .64, 1.37, 2.1)
TOP = 1.36
NOSE, TAIL = -3.3, 3.28
TUR = (0, .25, TOP)


def _hull(a):
    hull = a.part('Hull', BODY)
    # The Leopard 1 side profile: lower nose plate, the long upper glacis, the flat deck, the sloped rear plate.
    prof = [(NOSE, .62), (NOSE + .3, .82), (-2.0, TOP), (2.95, TOP), (TAIL, 1.0), (TAIL - .06, .45), (-2.85, .42)]
    k.extrude(hull, prof, 2.5, axis='X', chamfer=.06, corner=.03)
    low = a.part('Hull_lower', BLACK)
    k.extrude(low, [(NOSE + .2, .6), (-2.8, .38), (2.9, .38), (2.95, .8)], (TX - TW / 2) * 2, axis='X', chamfer=.02)
    fen = a.part('Fenders', BODY)
    for s in (-1, 1):
        K.fender(fen, TX + .02, NOSE + .2, TAIL - .05, 1.02, .58, s, lip=.03)
        sk = a.part('Skirts', BLACK)
        for j in range(5):
            K.plate(sk, (.035, 1.06, .42), loc=(s * (TX + .3), -2.2 + j * 1.1, .79), chamfer=.01)
        a.part('Skirt_flaps', 'Rubber').box((.02, 5.4, .07), loc=(s * (TX + .3), -.0, .55), bevel=0)
        hb = a.part('Kit_steel', 'Steel')
        for j in range(5):
            hb.box((.03, .5, .03), loc=(s * (TX + .315), -2.2 + j * 1.1, .99), bevel=0)
        a.part('Team_band', 'Gilded').box((.012, 3.2, .06), loc=(s * (TX + .33), .2, .9), bevel=0)
    # Glacis: the driver's hatch and periscopes (left), the headlamps in their guards, tow hooks, a spare track run.
    C.hatch(a, (.55, -1.75, TOP), r=.27, periscope=False)
    for x in (.3, .55, .8):
        K.periscope(a, (x, -2.05, TOP - .02), facing=(0, -1, .3), size=(.13, .07, .06), mat=BLACK)
    for s in (-1, 1):
        K.lamp(a, (s * 1.0, -2.55, 1.15), (0, -1, .2), r=.07, guard=True, mat=BLACK)
        K.tow_hook(a.part('Kit_steel', 'Steel'), (s * .7, NOSE - .02, .66), facing=(0, -1, 0), size=.08)
    tr = a.part('Spare_track', 'Undercarriage')
    for j in range(5):
        tr.box((1.1, .14, .05), loc=(0, -2.85 + j * .17, .84 + j * .1), rot=(-.53, 0, 0), bevel=0)
    # The engine deck: two big grilles, the louvred rear plate, exhausts on the corners, the Team deck panel.
    for x in (-.62, .62):
        K.grille(a, (x, 2.1, TOP + .02), 1.0, 1.15, facing=(0, 0, 1), slats=7, frame_mat=BLACK)
    K.plate(a.part('Deck_plates', BLACK), (2.2, .4, .02), loc=(0, 1.3, TOP + .01))
    K.grille(a, (0, TAIL + .01, .78), 1.6, .3, facing=(0, 1, -.3), slats=6, frame_mat=BLACK)
    for s in (-1, 1):
        K.exhaust(a, (s * 1.05, TAIL - .1, TOP - .1), r=.07, length=.35, direction=(0, 1, .3), muffler=False, cap=False)
        a.part('Tail_lamps', 'EliteGlow').box((.1, .02, .06), loc=(s * 1.1, TAIL + .0, 1.22), bevel=0)
    a.pivot('Point_exhaust', (1.05, TAIL + .15, TOP))
    a.pivot('Point_fire', (0, 1.8, TOP + .3))
    # Stowage: bins on the rear fenders, jerrycans, the tow cable along the left sponson.
    for s in (-1, 1):
        C.stowage_box(a, (.42, .8, .26), (s * (TX + .04), 2.35, 1.02), mat=BLACK, latches=2)
    C.jerry_rack(a, (-(TX + .04), -2.45, 1.02), count=2, axis='Y')
    K.tow_cable(a.part('Tow_cable', 'Undercarriage'), [(1.2, -1.6, TOP + .02), (1.2, .5, TOP + .02),
                                                       (1.05, .9, TOP + .02)], r=.025)


def _running_gear(a):
    for s in (-1, 1):
        C.running_gear(a, s, TX, TW, WHEELS, WR, sprocket=(2.88, .54, .3), idler=(-2.95, .52, .29),
                       rollers=[(-1.9, .9), (-.45, .92), (1.0, .92), (2.45, .9)], pitch=.24, disc_mat=BLACK,
                       wheel_w=.18, seg=9, teeth=12, idler_spokes=6, hide_top=(-2.7, 2.7, .82))
        arms = a.part('Suspension', 'Undercarriage')
        for y in WHEELS:
            C.wheel_arm(arms, s, TX - .2, y, WR, length=.36, back=1, r=.045)


def _gun(a, t, s):
    """One 35 mm revolver gun in its armoured pod outside the turret cheek (s = 1 left, -1 right)."""
    x = s * 1.52
    pod = a.part('Gun_pods', BLACK, t)
    C.slab_loft(pod, [(-.22, -1.0), (.22, -1.0), (.24, .9), (-.24, .9)],
                [(-.18, -.85), (.16, -.85), (.18, .8), (-.18, .8)], .1, .66, loc=(x, 0, 0))
    a.part('Gun_pod_band', 'Gilded', t).box((.5, .06, .3), loc=(x, -.5, .4), bevel=0)
    K.chamfer_box(a.part('Mantlet', BLACK, t), (.34, .3, .34), loc=(x, -1.12, .38), c=.04)
    name, brake = ('Main_cannon', 'Muzzle_brake') if s > 0 else ('Main_cannon_2', 'Muzzle_brake_2')
    end = C.gun_tube(a, name, t, (x, -1.25, .42), 2.8, .055, seg=10, sleeve=0, brake='plain', brake_name=brake)
    rib = a.part(f'{name}_ribs', 'Steel', t)
    for j in range(5):
        rib.cyl(.068, .05, loc=(x, -1.5 - j * .14, .42), rot=K.FORWARD, seg=10, bevel=0)
    # The muzzle velocity sensor ring at the tip, the feed cover on top of the pod.
    k.lathe(a.part('Muzzle_sensor', BLACK, t), [(.07, 0), (.11, .02), (.11, .16), (.07, .18)],
            loc=(x, end[1] + .25, .42), rot=K.FORWARD, seg=10)
    k.block(a.part('Feed_covers', BLACK, t), (.3, .7, .1), loc=(x, .1, .66), chamfer=.02)
    K.handle(a.part('Kit_steel', 'Steel', t), (x - .08, .5, .72), (x + .08, .5, .72), (0, 0, 1), h=.05)
    return end


def _turret(a):
    t = a.pivot('Turret', TUR)
    K.turret_ring(a.part('Turret_ring', BLACK), TUR, 1.0, h=.06)
    body = a.part('Turret_body', BODY, t)
    # The angular Skyranger-style house: a sharp sloped front, faceted cheeks, sides leaning in, the rear bustle.
    bot = [(-.55, -1.2), (.55, -1.2), (1.28, -.6), (1.3, 1.1), (1.0, 1.55), (-1.0, 1.55), (-1.3, 1.1), (-1.28, -.6)]
    top = [(-.4, -.75), (.4, -.75), (1.05, -.35), (1.08, 1.0), (.85, 1.38), (-.85, 1.38), (-1.08, 1.0),
           (-1.05, -.35)]
    C.slab_loft(body, bot, top, 0, .82, mid=([(x * 1.02, y * 1.0) for x, y in bot], .3))
    roof = a.part('Turret_roof', BLACK, t)
    K.plate(roof, (1.6, 1.6, .03), loc=(0, .35, .835))
    K.weld(a.part('Kit_welds', 'Charred', t), [(-1.0, -.3, .84), (1.0, -.3, .84)])
    a.part('Team_band', 'Gilded', t).box((2.18, .02, .07), loc=(0, 1.52, .45), bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Gilded', t).box((.02, 1.4, .07), loc=(s * 1.3, .3, .45), rot=(0, s * .1, 0), bevel=0)
    # The two gun pods; the main muzzle at the left gun (one point in the data).
    end = _gun(a, t, 1)
    _gun(a, t, -1)
    a.pivot('Muzzle_main', (end[0], end[1] - .02, end[2]), t)
    # The fire-control radar panel on the front face, the electro-optical sensor head on the roof front.
    fc = a.part('Radar_panel', BLACK, t)
    K.plate(fc, (.7, .08, .4), loc=(0, -1.0, .45), rot=(-.5, 0, 0))
    a.part('Radar_dish', 'Undercarriage', t).box((.6, .02, .3), loc=(0, -1.05, .47), rot=(-.5, 0, 0), bevel=0)
    eo = a.part('Sight', BLACK, t)
    k.lathe(eo, [(.12, 0), (.12, .12), (.09, .14)], loc=(-.45, -.35, .84), seg=10)
    K.chamfer_box(eo, (.34, .3, .3), loc=(-.45, -.35, .98), c=.05)
    a.part('Glass', 'Glass', t).box((.22, .01, .14), loc=(-.45, -.505, 1.13), bevel=0)
    a.part('Sight_glow', 'EliteGlow', t).box((.14, .01, .08), loc=(-.45, -.51, 1.13), bevel=0)
    # The search radar on its rear mast (spins), the IFF bar under it.
    ms = a.part('Radar_mast', BLACK, t)
    k.lathe(ms, [(.16, 0), (.16, .08), (.08, .12), (.07, .5), (.11, .52), (.11, .58), (0, .58)], loc=(0, 1.0, .84),
            seg=10, worn=(3,))
    for s in (-1, 1):
        ms.limb((s * .3, .8, .84), (0, 1.0, 1.15), .025, .025, bevel=0)
    r = a.pivot('Radar', (0, 1.0, 1.42), t)
    arr = a.part('Radar_array', BLACK, r)
    for d in (-1, 1):
        K.plate(arr, (1.15, .07, .5), loc=(0, d * .06, .28), rot=(d * .18, 0, 0))
    a.part('Radar_face', 'Undercarriage', r).box((1.05, .015, .4), loc=(0, -.11, .28), rot=(-.18, 0, 0), bevel=0)
    a.part('Radar_frame', 'Steel', r).box((.25, .25, .12), loc=(0, 0, .03), bevel=0)
    a.part('Radar_glow', 'EliteGlow', r).box((.06, .06, .04), loc=(.55, 0, .55), bevel=0)
    # The twin Stinger box on the right side (aims with the turret).
    lb = a.part('Launcher_box', BLACK, t)
    k.lathe(lb, [(.05, -.12), (.05, .12)], loc=(-1.12, .6, .7), rot=(0, R90, 0), seg=8)
    K.chamfer_box(lb, (.32, .95, .38), loc=(-1.32, .55, .62), c=.03)
    ms_ = a.part('Missiles', 'Undercarriage', t)
    for dz in (.12, -.12):
        ms_.cyl(.06, .02, loc=(-1.32, .07, .81 + dz), rot=K.FORWARD, seg=8, bevel=0)
    a.part('Missile_caps', 'Hazard', t).box((.26, .02, .04), loc=(-1.32, .07, .99), bevel=0)
    a.pivot('Muzzle_missile', (-1.32, .02, .81), t)
    # Roof: the commander's hatch (unmanned turret: a maintenance hatch), vents, smoke dischargers, aerials.
    C.hatch(a, (.45, .55, .84), r=.25, parent=t, mat=BLACK)
    k.lathe(a.part('Vents', BLACK, t), [(.13, 0), (.13, .07), (.09, .1), (0, .1)], loc=(.55, 1.15, .84), seg=8)
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.02, -.55, .62, s, count=3, parent=t)
        K.whip_antenna(a.part('Antennas', 'Steel', t), (s * .8, 1.35, .84), h=1.0 if s > 0 else .8, r=.02)
    K.crate(a.part('Stowage', BLACK, t), a.part('Kit_latches', 'Steel', t), (1.2, .3, .3), (0, 1.62, .15), bands=2)


def elite_aa(a, detail=False):
    """The elite anti-aircraft tank: see the module docstring."""
    _hull(a)
    _running_gear(a)
    _turret(a)
    K.dust(a, (0, 0, .3), radius=3.6, k=.12)
    k.clean(a)


BUILDERS = {
    'elite_aa': (elite_aa, dict(ao_distance=.5, grime_height=.55)),
}
