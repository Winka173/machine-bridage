"""Prompt 35 wave 11 (lane C): Cerberus rebuilt from scratch (spec: Tools/blender/specs/cerberus.json).

The three-car armoured road train of Varga's Cerberus (the variant of Behemoth keeping the main gun, the two flak
turrets and the rocket pod; the def's modelSize 16.3 x 8.4 x 5.5 m), drawn on the LeTourneau TC-497 Overland Train
pattern: each car rides on giant electric-hub wheels set far out on its sides under armoured wheel arches, so the
train is as wide as the data asks (the old file was 17 % too narrow). The tractor: a low armoured control cab with
vision blocks at the nose, the wedge glacis, the hull deck carrying the big faceted turret (`Turret`) with its
mantlet and the twin 152 mm barrels (bore evacuators, muzzle brakes; the per-barrel muzzles come from mb_fix_barrels'
EXTRA list), the commander's cupola, hatches, smoke dischargers and the stowage basket. The power car: the turbine
generator house with its intake grilles and exhaust stacks, the raised pedestal with the two 30 mm flak turrets
(`Mount_mg` / `.001`), the search radar on its mast, cable reels. The trailer: the 12-tube rocket pod on its ring
(`Mount_rocket`) and the two compact 120 mm turrets at its rear corners (`Mount_gun.001` / `.002`, firing forward).
Between the cars: drawbars with hitch eyes, power cables and rubber bellows. Hub motors, lamps, tow hooks, ladders,
handrails, jerrycans and team bands on every car.

Runtime nodes kept where they were: `Part_tractor` (0, -4.6, 0), `Part_middle` (0, 1.35, 0), `Part_trailer`
(0, 6.3, 0), `Turret` (0, -3.0, 2.9), `Main_cannon`, `Main_cannon_2`, `Muzzle_brake`, `Muzzle_brake_2`,
`Muzzle_main` (0, -8.1, 3.4), `Mount_gun` / `Muzzle_gun` (plain: the 120 mm part is dropped by the variant),
`Mount_mg` / `.001` with their muzzles, `Muzzle_missile` / `.001` (plain: the missile parts are dropped),
`Mount_gun.001` / `.002` with their muzzles, `Mount_rocket` / `Muzzle_rocket`. Metres, +Z up, -Y front, +X left.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
TRACK = 3.25         # the giant wheels' centre line
WR = 1.05
WW = .9


def _wheel(a, p, y, r=WR):
    for s in (-1, 1):
        K.tread_wheel(a, (s * TRACK, y, r), r, WW, s, seg=16, parent=p, tyre='Tyres', rim='Wheels', nuts=0)
        # The hub motor's drum on the inner side and the axle stub to the hull.
        k.lathe(a.part('Hub_motors', 'Steel', p), [(.42 * r, 0), (.42 * r, .3), (.3 * r, .36), (.12, .36)],
                loc=(s * (TRACK - WW / 2 + .02), y, r), rot=(0, -s * R90, 0), seg=10, worn=(1,))
        a.part('Axles', 'Undercarriage', p).box((1.1, .3, .3), loc=(s * (TRACK - WW / 2 - .55), y, r), bevel=0)


def _arch(a, p, y0, y1, ztop, r=WR):
    """An armoured wheel arch over a pair of wheels: sloped top, outer skirt, a lip, bolts."""
    arch = a.part('Wheel_arches', 'Team', p)
    for s in (-1, 1):
        x0 = s * (TRACK - WW / 2 - .1)
        x1 = s * (TRACK + WW / 2 + .15)
        k.extrude(arch, [(x0, ztop), (x1, ztop - .25), (x1, ztop - .35), (x0, ztop - .1)], y1 - y0,
                  loc=(0, (y0 + y1) / 2, 0), rot=(0, 0, 0), axis='Y', chamfer=.04, corner=.02)
        sk = a.part('Skirts', 'Armor', p)
        sk.box((.06, y1 - y0 - .2, .55), loc=(x1 + s * .02, (y0 + y1) / 2, ztop - .6), bevel=0)
        K.rivet_line(a.part('Kit_bolts', 'Steel', p), (x1 + s * .055, y0 + .2, ztop - .45),
                     (x1 + s * .055, y1 - .2, ztop - .45), (s, 0, 0), pitch=.45, r=.03, h=.03, seg=5)


def _hull(a, p, y0, y1, deck, belly=.75, half=2.55, nose=0.0, tail=0.0, name='Body'):
    """A car's hull: a section loft between the arches, sloped lower sides, an optional wedge nose / tail."""
    body = a.part(name, 'Team', p)
    sec = [(0, belly), (half - .5, belly), (half, belly + .55), (half, deck - .2), (half - .15, deck), (0, deck)]
    st = []
    if nose:
        st.append((y0, [(x * .7, belly + .35 + (z - belly) * .25) for x, z in sec]))
        st.append((y0 + nose, sec))
    else:
        st.append((y0, sec))
    if tail:
        st.append((y1 - tail, sec))
        st.append((y1, [(x * .85, belly + .2 + (z - belly) * .6) for x, z in sec]))
    else:
        st.append((y1, sec))
    C.section_loft(body, st)
    a.part('Chassis_' + name.split('_')[-1].lower(), 'Undercarriage', p).box((1.6, y1 - y0 - .4, .3),
                                                                            loc=(0, (y0 + y1) / 2, belly - .1),
                                                                            bevel=0)
    for s in (-1, 1):
        a.part('Team_band', 'Team', p).box((.02, (y1 - y0) * .5, .18), loc=(s * (half + .01), (y0 + y1) / 2,
                                                                             deck - .45), bevel=0)


def _tractor(a):
    p = a.pivot('Part_tractor', (0, -4.6, 0))
    y0, y1 = -3.05, 2.75
    deck = 2.78
    _hull(a, p, y0, y1, deck, nose=1.2, name='Body_tractor')
    for y in (-1.75, 1.45):
        _wheel(a, p, y)
    _arch(a, p, -3.0, -.5, 2.5)
    _arch(a, p, .2, 2.7, 2.5)
    # The control cab at the nose: low, sloped front, vision blocks, a hatch, lamps, tow hooks.
    cab = a.part('Cab', 'Armor', p)
    k.extrude(cab, [(-1.2, 0), (1.2, 0), (1.05, .32), (-1.05, .32)], 1.1, loc=(0, -1.6, deck - .02), axis='Y',
              chamfer=.04, corner=.03)
    glass = a.part('Tractor_glass', 'Glass', p)
    for x in (-.7, 0, .7):
        glass.box((.5, .04, .14), loc=(x, -2.14, deck + .16), rot=(.6, 0, 0), bevel=0)
    C.hatch(a, (.55, -1.4, deck + .3), r=.28, parent=p, periscope=True)
    for s in (-1, 1):
        K.lamp(a, (s * 1.7, -2.55, 1.9), (0, -1, .1), r=.11, parent=p)
        K.tow_hook(a.part('Kit_steel', 'Steel', p), (s * .7, y0 - .02, 1.15), facing=(0, -1, 0), size=.12)
        K.ladder(a.part('Ladders', 'Steel', p), (s * 2.6, 2.3, .8), (s * 2.6, 2.3, deck), width=.4, step=.3)
    rail = a.part('Railings', 'Steel', p)
    rail.tube([(-2.3, 2.6, deck), (-2.3, 2.6, deck + .5), (2.3, 2.6, deck + .5), (2.3, 2.6, deck)], .025, seg=4)
    C.jerry_rack(a, (-1.9, -.4, deck), count=3, axis='Y', parent=p)
    K.grille(a, (1.7, .3, deck + .01), 1.0, .9, facing=(0, 0, 1), slats=6, parent=p, frame_mat='Team')
    K.dust(a, (0, -4.6, .3), radius=4.0, k=.16)


def _turret(a):
    t = a.pivot('Turret', (0, -3.0, 2.9))
    house = a.part('Turret_body', 'Team', t)
    bot = [(-1.2, -1.3), (1.2, -1.3), (1.6, -.6), (1.6, 1.5), (1.3, 1.85), (-1.3, 1.85), (-1.6, 1.5), (-1.6, -.6)]
    top = [(-.95, -1.05), (.95, -1.05), (1.35, -.45), (1.38, 1.35), (1.1, 1.6), (-1.1, 1.6), (-1.38, 1.35),
           (-1.35, -.45)]
    C.slab_loft(house, bot, top, 0, .95)
    k.ring(a.part('Turret_ring', 'Steel', t), [(1.35, -.06), (1.5, -.06), (1.5, .06), (1.35, .08)], seg=24)
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        K.plate(arm, (.06, 1.0, .6), loc=(s * 1.45, -.95, .45), rot=(0, 0, s * .52), chamfer=.012)
    k.block(arm, (2.3, 2.4, .05), loc=(0, .35, .975), chamfer=.015)
    # Mantlet and the twin 152 mm barrels.
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.3, -.35), (.22, -.38), (.3, .35), (-.22, .38)], 1.7, loc=(0, -1.35, .5), axis='X',
              chamfer=.05, corner=.04)
    for x, nm, br in ((-.45, 'Main_cannon', 'Muzzle_brake'), (.45, 'Main_cannon_2', 'Muzzle_brake_2')):
        C.gun_tube(a, nm, t, (x, -1.6, .5), 3.0, .12, seg=12, sleeve=2, extractor=(.4, 1.5), brake=None)
        bp = a.part(br, 'Steel', t)
        k.extrude(bp, [(-.2, -.16), (.2, -.16), (.2, .16), (-.2, .16)], .5, loc=(x, -4.85, .5), axis='Y',
                  chamfer=.04, corner=.04)
        a.part(br + '_ports', 'Undercarriage', t).box((.42, .14, .2), loc=(x, -4.8, .5), bevel=0)
    a.pivot('Muzzle_main', (0, -5.1, .5), t)
    K.soot(a, (0, -8.1, 3.4), radius=.8, k=.35)
    # Cupola, hatches, the old Mount_gun pivot (a plain sight post: the 120 mm part is dropped), smoke, basket.
    cup = a.part('Hatches', 'Armor', t)
    k.ring(cup, [(.36, .95), (.45, .95), (.45, 1.12), (.38, 1.16)], loc=(.6, .6, 0), seg=14, worn=(2,))
    for i in range(5):
        u = i * TAU / 5 + .3
        K.periscope(a, (.6 + math.cos(u) * .42, .6 + math.sin(u) * .42, 1.08),
                    facing=(math.cos(u), math.sin(u), 0), parent=t, size=(.1, .08, .07))
    C.hatch(a, (.6, .6, 1.14), r=.33, parent=t)
    k.block(a.part('Sight_post', 'Armor', t), (.36, .4, .3), loc=(-.65, -.3, 1.1), chamfer=.03, ends=(True, True))
    a.part('Glass', 'Glass', t).box((.26, .02, .12), loc=(-.65, -.51, 1.12), bevel=0)
    a.pivot('Mount_gun', (-.65, -.3, .95), t)
    a.pivot('Muzzle_gun', (0, -1.55, .17), 'Mount_gun')
    for s in (-1, 1):
        K.smoke_dischargers(a, 1.45, -.4, .75, s, count=4, parent=t)
        K.whip_antenna(a.part('Antennas', 'Steel', t), (s * 1.1, 1.4, .97), h=.9)
    bk = a.part('Stowage_basket', 'Steel', t)
    bk.tube([(-1.2, 1.85, .5), (-1.2, 2.25, .5), (1.2, 2.25, .5), (1.2, 1.85, .5)], .03, seg=4)
    bk.tube([(-1.2, 2.25, .2), (1.2, 2.25, .2)], .03, seg=4)
    C.stowage_box(a, (1.0, .35, .35), (-.5, 2.05, .2), parent=t, name='Stowage')
    K.net_roll(a.part('Tarp', 'Canvas', t), a.part('Kit_straps', 'Steel', t), (.6, 2.05, .35), length=.9, r=.13)
    a.part('Team_band', 'Team', t).box((.02, 2.0, .14), loc=(1.61, .5, .5), bevel=0)
    a.part('Team_band', 'Team', t).box((.02, 2.0, .14), loc=(-1.61, .5, .5), bevel=0)


def _flak(a, mount, loc, parent):
    """A twin 30 mm flak turret on a mount pivot: house, twin barrels, the gunner's sight."""
    m = a.pivot(mount, loc, parent)
    tag = mount.replace('Mount_mg', '').replace('__', '_')
    house = a.part('Gun_house_mg' + tag, 'Team', m)
    k.extrude(house, [(-.5, 0), (.5, 0), (.42, .45), (-.36, .5)], 1.2, loc=(0, -.05, 0), axis='Y',
              chamfer=.04, corner=.03, taper=(.8, 1))
    k.ring(a.part('Gun_ring_mg' + tag, 'Steel', parent), [(.55, -.04), (.65, -.04), (.65, .04), (.55, .05)],
           loc=loc, seg=14)
    for x in (-.18, .18):
        C.gun_tube(a, 'Gun_barrel_mg' + tag, m, (x, -.6, .3), 2.15, .045, seg=8, sleeve=None, brake='plain',
                   brake_name='Gun_brake_mg' + tag)
    K.periscope(a, (.3, -.2, .5), facing=(0, -1, 0), parent=m, size=(.14, .12, .1))
    a.pivot(mount.replace('Mount', 'Muzzle'), (0, -2.8, .31), mount)


def _middle(a):
    p = a.pivot('Part_middle', (0, 1.35, 0))
    y0, y1 = -2.5, 2.5
    deck = 2.5
    _hull(a, p, y0, y1, deck, name='Body_middle')
    for y in (-1.3, 1.3):
        _wheel(a, p, y)
    _arch(a, p, -2.45, -.15, 2.4)
    _arch(a, p, .15, 2.45, 2.4)
    # The turbine generator house, its intakes and exhaust stacks.
    gh = a.part('Generator_house', 'Armor', p)
    k.extrude(gh, [(-2.3, 0), (2.3, 0), (2.1, .55), (-2.1, .55)], 1.4, loc=(0, 1.75, deck), axis='Y', chamfer=.05,
              corner=.04)
    for s in (-1, 1):
        K.grille(a, (s * 2.22, 1.75, deck + .28), 1.0, .35, facing=(s, 0, .2), slats=5, parent=p, frame_mat='Armor')
        k.lathe(a.part('Exhaust', 'Steel', p), [(.18, 0), (.18, .9), (.24, .95), (.24, 1.1), (.2, 1.1)],
                loc=(s * 1.5, 2.15, deck + .5), seg=10, worn=(3,))
        K.soot(a, (s * 1.5, 3.5, deck + 1.6), radius=.5, k=.45)
        C.cable_reel(a, (s * 2.0, -1.9, deck + .25), r=.24, w=.35, axis='Y', parent=p)
        K.ladder(a.part('Ladders', 'Steel', p), (s * 2.6, -.1, .8), (s * 2.6, -.1, deck), width=.4, step=.3)
    # The pedestal with the flak turrets, the radar mast; the plain missile pivots (parts dropped by the variant).
    ped = a.part('Aa_pedestal', 'Team', p)
    k.extrude(ped, [(-1.6, -1.0), (1.6, -1.0), (1.6, 1.0), (-1.6, 1.0)], 1.05, loc=(0, .05, deck + .5),
              axis='Z', chamfer=.06, corner=.08, taper=(.9, .9))
    _flak(a, 'Mount_mg', (-.97, .05, 3.55), p)
    _flak(a, 'Mount_mg__001', (.97, .05, 3.55), p)
    for i, sx in enumerate((-1, 1)):
        a.pivot('Muzzle_missile' if i == 0 else 'Muzzle_missile__001', (sx * 1.75, -.1, 3.1), p)
    mast = a.part('Aa_mast', 'Steel', p)
    k.lathe(mast, [(.14, 0), (.14, 1.9), (.1, 1.95)], loc=(0, 1.3, deck + 1.05), seg=8, worn=(1,))
    for s in (-1, 1):
        mast.limb((s * .6, 1.3, deck + 1.05), (0, 1.3, deck + 2.0), .05, .05, bevel=0)
    rad = a.part('Aa_radar', 'Armor', p)
    k.block(rad, (1.9, .18, .85), loc=(0, 1.3, 5.0), rot=(-.25, 0, 0), chamfer=.03, ends=(True, True))
    rr = a.part('Aa_radar_ribs', 'Steel', p)
    for i in range(5):
        rr.box((.03, .05, .8), loc=(-.8 + i * .4, 1.2, 5.0), rot=(-.25, 0, 0), bevel=0)
    K.beacon(a, (1.2, -.6, deck + 1.55), parent=p, r=.1)
    K.dust(a, (0, 1.35, .3), radius=3.5, k=.16)


def _gun120(a, mount, loc, parent):
    m = a.pivot(mount, loc, parent)
    tag = mount.replace('Mount_gun', '').replace('__', '_')
    house = a.part('Gun_house_gun' + tag, 'Armor', m)
    k.extrude(house, [(-.38, 0), (.38, 0), (.32, .36), (-.3, .4)], .9, loc=(0, .1, 0), axis='Y', chamfer=.03,
              corner=.03)
    k.ring(a.part('Gun_ring_gun' + tag, 'Steel', parent), [(.4, -.03), (.48, -.03), (.48, .04), (.4, .05)], loc=loc,
           seg=12)
    C.gun_tube(a, 'Gun_barrel_gun' + tag, m, (0, -.35, .17), 1.15, .07, seg=10, extractor=(.45, 1.5),
               brake='plain', brake_name='Gun_brake_gun' + tag)
    a.pivot(mount.replace('Mount', 'Muzzle'), (0, -1.55, .17), mount)


def _trailer(a):
    p = a.pivot('Part_trailer', (0, 6.3, 0))
    y0, y1 = -1.9, 1.85
    deck = 2.2
    _hull(a, p, y0, y1, deck, belly=.7, tail=.6, name='Body_trailer')
    r = .95
    for y in (-.95, 1.05):
        _wheel(a, p, y, r=r)
    _arch(a, p, -1.95, 1.95, 2.15, r=r)
    # The rocket pod on its ring.
    m = a.pivot('Mount_rocket', (0, -.1, 2.5), p)
    k.lathe(a.part('Rocket_ring', 'Steel', m), [(.95, -.3), (1.0, -.25), (1.0, -.1), (.9, 0)], seg=18, worn=(2,))
    pod = a.part('Rocket_pod', 'Team', m)
    k.block(pod, (2.3, 2.7, 1.05), loc=(0, .05, .6), rot=(.12, 0, 0), chamfer=.07, ends=(True, True))
    tubes = a.part('Rocket_tubes', 'Charred', m)
    for i in range(4):
        for j in range(3):
            tubes.cyl(.16, .04, loc=(-.81 + i * .54, -1.29, .6 + (j - 1) * .33 - .02), rot=(R90 + .12, 0, 0), seg=8,
                      bevel=0)
    a.part('Rocket_bands', 'Hazard', m).box((2.32, .14, 1.07), loc=(0, -.9, .65), rot=(.12, 0, 0), bevel=0)
    a.pivot('Muzzle_rocket', (0, -1.48, .62), 'Mount_rocket')
    _gun120(a, 'Mount_gun__001', (1.5, 1.35, 2.5), p)
    _gun120(a, 'Mount_gun__002', (-1.5, 1.35, 2.5), p)
    for s in (-1, 1):
        a.part('Tail_lamps', 'LavaGlow', p).box((.3, .03, .14), loc=(s * 1.6, y1 + .01, 1.6), bevel=0)
    K.dust(a, (0, 6.3, .3), radius=3.0, k=.16)


def _couplings(a):
    """Drawbars, hitch eyes, power cables and bellows between the cars (world frame: they bend with nothing)."""
    for y0, y1, z in ((-1.9, -1.15, 1.25), (3.85, 4.4, 1.2)):
        k.block(a.part('Couplings', 'Armor'), (.5, y1 - y0 + .4, .3), loc=(0, (y0 + y1) / 2, z), chamfer=.04)
        k.ring(a.part('Kit_steel', 'Steel'), [(.22, -.08), (.3, -.08), (.3, .08), (.22, .08)],
               loc=(0, y1 + .1, z + .15), seg=12)
        for x in (-.9, .9):
            a.part('Power_cables', 'Rubber').tube([(x, y0 - .1, 2.2), (x * 1.05, (y0 + y1) / 2, 1.85),
                                                  (x, y1 + .1, 2.1)], .06, seg=5)
        bel = a.part('Bellows', 'Rubber')
        for i in range(3):
            yy = y0 + (i + .5) * (y1 - y0) / 3
            bel.box((1.8, .12, .9), loc=(0, yy, 1.8), bevel=0)


def cerberus(a, detail=False):
    """Cerberus, the armoured road train: see the module docstring."""
    K.suffixed(a)
    _tractor(a)
    _turret(a)
    _middle(a)
    _trailer(a)
    _couplings(a)
    k.clean(a)


BUILDERS = {
    'cerberus': (cerberus, dict(ao_distance=.6, ao_strength=.65, grime_height=.4)),
}
