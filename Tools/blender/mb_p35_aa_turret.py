"""Prompt 35 wave 9 (lane C): the AA turret and its flak branch rebuilt from scratch together (specs:
Tools/blender/specs/aa_turret.json, aa_turret_a.json).

Both stand on one emplacement (the def's 4.5 x 4.5 m tower; the old files' 5.4 x 4.5 m footprint kept): a cast
concrete pad with a raised plinth and race ring, a sandbag parapet of three courses with the entry gap at the rear,
the ready-round boxes and a tarp in the rear bay, the field telephone post and its whip, a fire extinguisher, so the
branch reads as the same post with a new mount:

- aa_turret (tower_flak_30, the 2A38 twin 30 mm; secondary `sam`, unit_refs: the Tunguska's 2A38 and the Stinger):
  a low angular one-man gun house on the race, the 2A38's two barrels side by side on one cradle (sleeves, muzzle
  brakes), the twin Stinger launch tubes on an arm on the gun house's left (`Muzzle_missile`, aim Turret), the small
  search radar spinning on its mast behind (`Radar`), the gunner's sight head, hatch, periscopes and a beacon.
- aa_turret_a (aa_turret.flak, flak_quad: the ZSU-23-4's four 23 mm): the same pad and parapet with a fourth bay of
  ready rounds; on the race the Shilka's flat slab-sided turret with the four 23 mm barrels in two pairs (upper and
  lower) out of a wide mantlet, the RPK-2 dish on its folding mast at the rear (`Radar`), the commander's cupola.

Runtime nodes kept: `Turret`, `Main_cannon` (+ `_2`, `_3`, `_4` on the flak branch), `Muzzle_brake` (+ the same),
`Muzzle_main`, `Muzzle_missile` (aa_turret), `Radar`. Metres, +Z up, -Y front, +X left. Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C

R90 = math.pi / 2
TAU = math.tau
G = .04
PAD_Z = .2           # top of the pad
RACE_Z = .52         # top of the plinth / race ring (the turret pivot)
TY = .1            # the race centre (a little forward: the rear bay behind it)
OUT = [(-1.95, -2.45), (1.95, -2.45), (2.2, -2.1), (2.2, 2.1), (1.95, 2.68), (-1.95, 2.68), (-2.2, 2.1),
       (-2.2, -2.1)]


def _emplacement(a, bays=3):
    """Pad, plinth, race, parapet, the rear bay's stores; shared by the base and the branch."""
    # No slab under the whole post (the ground is the floor): the cast plinth and an apron round it.
    k.lathe(a.part('Base', 'Concrete'), [(1.62, G), (1.55, PAD_Z), (1.32, PAD_Z)], loc=(0, TY, 0), seg=18,
            caps=(False, False), worn=(1,))
    ties = a.part('Base_ties', 'Steel')
    for i in range(6):
        u = i * TAU / 6 + .3
        ties.cyl(.022, .02, loc=(math.cos(u) * 1.6, TY + math.sin(u) * 1.6, G + .08), rot=(R90, 0, u + R90), seg=6,
                 bevel=0)
    k.lathe(a.part('Plinth', 'Concrete'), [(1.32, PAD_Z), (1.28, RACE_Z - .08), (1.2, RACE_Z - .04), (1.2, RACE_Z - .03)],
            loc=(0, TY, 0), seg=18, caps=(False, True), worn=(1,))
    k.ring(a.part('Race', 'Steel'), [(1.02, RACE_Z - .04), (1.12, RACE_Z - .04), (1.12, RACE_Z), (1.02, RACE_Z)],
           loc=(0, TY, 0), seg=18)
    k.ring(a.part('Team_band', 'Team'), [(1.3, PAD_Z + .1), (1.315, PAD_Z + .1), (1.315, PAD_Z + .17), (1.3, PAD_Z + .17)],
           loc=(0, TY, 0), seg=18)
    # The sandbag parapet: three courses round the front and sides, the entry gap at the rear right.
    path = [(-1.55, 2.35), (-2.0, 2.0), (-2.0, -2.0), (-1.75, -2.25), (1.75, -2.25), (2.0, -2.0), (2.0, 2.0),
            (1.6, 2.35), (.55, 2.4)]
    k.sweep(a.part('Berm', 'Dirt'), [(.34, 0), (-.34, 0), (-.2, -.5), (.2, -.5)], [(x, y, G) for x, y in path],
            caps=False, worn=(2,))   # the sweep's v runs down here
    K.sandbag_run(a, [(x, y, G + .5) for x, y in path], courses=1, bag=(.56, .3, .15), part='Sandbags', seed=9,
                  lean=True)
    K.sandbag_run(a, [(-1.5, 2.4, G + .65), (-.7, 2.42, G + .65)], courses=1, bag=(.56, .3, .15),
                  part='Sandbags', seed=4, lean=True)
    turf = a.part('Berm_turf', 'Grass')
    for x, y, u in ((-2.0, -1.0, R90), (2.0, .6, R90), (.4, -2.25, 0), (-1.1, -2.25, 0), (-2.0, 1.2, R90)):
        turf.box((.7, .5, .03), loc=(x + (.3 if abs(x) < 1.9 else math.copysign(.33, x)) * 0, y, G + .3),
                 rot=(0, 0, u), bevel=0)
    # The rear bay: duckboards, ready-round boxes on pallets, a tarp, the field telephone post and its whip, an
    # extinguisher, the crew's tools and helmets, spent cases round the plinth, a camouflage net over the bay.
    C.duckboard(a, (-.3, 1.95, G), 3.0, .9, planks=9, seed=3, axis='Y')
    pal = a.part('Pallets', 'Wood')
    for i in range(bays):
        x = -1.45 + i * .62
        k.block(pal, (.56, .7, .08), loc=(x, 1.75, G + .09), chamfer=0)
        for j in range(2):
            k.block(a.part('Ammo_boxes', 'Crate'), (.5 - .02 * j, .3, .2 + .02 * i), loc=(x, 1.6 + j * .32, G + .17),
                    chamfer=.012)
        k.block(a.part('Ammo_boxes', 'Crate'), (.5, .3, .2), loc=(x, 1.75, G + .39 + .02 * i), rot=(0, 0, .08 * i),
                chamfer=.012)
        a.part('Kit_handles', 'Steel').box((.04, .2, .02), loc=(x, 1.75, G + .6 + .02 * i), bevel=0)
    K.net_roll(a.part('Tarp', 'Canvas'), a.part('Kit_straps', 'Steel'), (1.35, 1.95, G + .12), length=.9, r=.12,
               axis='Y')
    post = a.part('Masts', 'Wood')
    post.cyl(.05, 1.95, loc=(1.75, 2.1, G + .975), seg=6, bevel=0)
    k.block(a.part('Phone_box', 'Armor'), (.22, .12, .28), loc=(1.75, 2.02, G + 1.0), chamfer=.02)
    a.part('Kit_cables', 'Undercarriage').tube([(1.75, 2.0, G + 1.0), (1.4, 1.5, G + .03), (.6, 1.1, G + .03),
                                                (.3, .9, PAD_Z + .1)], .012, seg=4)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.75, 2.1, G + 1.95), h=1.1, r=.015)
    a.part('Extinguisher', 'BarrelRed').cyl(.07, .45, loc=(-1.7, 1.1, G + .225), seg=8, bevel=0)
    C.entrenching_tools(a, (-1.62, -.6, G), yaw=-R90, lean=.4)
    C.helmets(a, [(-1.25, 1.2, G), (1.45, 1.3, G + .02)])
    C.casings(a, (0, TY), 2.0, 26, r=.017, length=(.12, .22), seed=11, z=G)
    K.camo_net(a, [(-1.9, 2.5, 1.25), (1.9, 2.5, 1.25), (1.7, 1.25, 1.45), (-1.7, 1.25, 1.45)], .18, G,
               part='Camo_net', garnish=10, seed=2)
    K.dust(a, (0, 0, G), radius=2.6, k=.14)


def _barrel(a, name, parent, loc, length, r, pitch, brake=None, sleeve=0, seg=10):
    """A gun barrel along -Y pitched up `pitch` rad from loc: tube, optional sleeve bands and a muzzle brake part.
    Returns the tip."""
    rot = (R90 - pitch, 0, 0)
    d = (0, -math.cos(pitch), math.sin(pitch))
    x, y, z = loc
    k.lathe(a.part(name, 'Steel', parent), [(r * 1.3, 0), (r * 1.3, length * .12), (r, length * .15), (r * .85, length),
                                             (0, length)], loc=loc, rot=rot, seg=seg, worn=(1,))
    for j in range(sleeve):
        f = .25 + j * .2
        a.part('Gun_sleeves', 'Armor', parent).cyl(r * 1.15, .06, loc=(x + d[0] * length * f, y + d[1] * length * f,
                                                                             z + d[2] * length * f), rot=rot, seg=seg,
                                                      bevel=0)
    tip = (x + d[0] * length, y + d[1] * length, z + d[2] * length)
    if brake:
        k.lathe(a.part(brake, 'Undercarriage', parent), [(r * 1.0, -r * 2.6), (r * 1.5, -r * 2.4), (r * 1.5, -r * .3),
                                                        (r * 1.1, 0), (0, 0)], loc=tip, rot=rot, seg=seg, worn=(2,))
    return tip


def _gun_house(a, t):
    """aa_turret: the angular one-man gun house, the 2A38, the Stinger arm, the radar."""
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.7, -.75), (.7, -.75), (.95, -.35), (.95, .8), (.7, 1.05), (-.7, 1.05), (-.95, .8), (-.95, -.35)]
    top = [(-.5, -.45), (.5, -.45), (.78, -.2), (.78, .7), (.6, .9), (-.6, .9), (-.78, .7), (-.78, -.2)]
    C.slab_loft(body, bot, top, 0, .72, mid=([(x * 1.02, y * 1.02) for x, y in bot], .3))
    K.plate(a.part('Turret_armor', 'Armor', t), (1.2, 1.1, .03), loc=(0, .22, .735), chamfer=.01)
    a.part('Turret_steel', 'Steel', t).box((1.9, .03, .06), loc=(0, 1.04, .32), bevel=0)
    # The cradle and the 2A38's two barrels side by side (pitched up 18 degrees).
    cr = a.part('Gun_cradle', 'Armor', t)
    k.extrude(cr, [(-.16, -.16), (.18, -.2), (.22, .2), (-.12, .22)], .62, loc=(0, -.78, .4), axis='X', chamfer=.03,
              corner=.02)
    pitch = math.radians(18)
    tips = []
    for i, x in enumerate((-.14, .14)):
        suf = '' if i == 0 else '_2'
        tips.append(_barrel(a, f'Main_cannon{suf}', t, (x, -.9, .42), 2.0, .045, pitch, brake=f'Muzzle_brake{suf}',
                            sleeve=2))
    for s in (-1, 1):
        a.part('Gun_casing_chutes', 'Undercarriage', t).box((.08, .3, .12), loc=(s * .36, -.62, .2), bevel=0)
    a.pivot('Muzzle_main', ((tips[0][0] + tips[1][0]) / 2, tips[0][1] - .03, tips[0][2] + .01), t)
    # The twin Stinger tubes on their arm (left side), Muzzle_missile at the upper tube's mouth.
    arm = a.part('Launcher_arm', 'Steel', t)
    arm.limb((.95, .1, .4), (1.18, .05, .5), .05, .05, bevel=0)
    k.block(arm, (.1, .5, .12), loc=(1.2, .05, .44), chamfer=.01)
    tb = a.part('Launcher_tubes', 'Canvas', t)
    pm = math.radians(14)
    for j, z in enumerate((.66, .84)):
        tb.cyl(.075, 1.5, loc=(1.22, .0, z), rot=(R90 - pm, 0, 0), seg=10, bevel=0)
        a.part('Launcher_caps', 'Undercarriage', t).cyl(.08, .04, loc=(1.22, -.73, z + .18), rot=(R90 - pm, 0, 0),
                                                        seg=10, bevel=0)
    a.part('Launcher_grips', 'Steel', t).box((.04, .2, .14), loc=(1.3, .15, .62), bevel=0)
    a.pivot('Muzzle_missile', (1.22, -.76, 1.03), t)
    # The gunner's sight head, hatch, periscopes, the beacon.
    sh = a.part('Sight', 'Armor', t)
    K.chamfer_box(sh, (.3, .32, .26), loc=(-.38, -.25, .73), c=.03)
    a.part('Glass', 'Glass', t).box((.22, .01, .12), loc=(-.38, -.415, .86), bevel=0)
    C.hatch(a, (.3, .45, .735), r=.24, parent=t)
    for x in (-.15, .08):
        K.periscope(a, (x, -.4, .73), facing=(0, -1, 0), parent=t, size=(.1, .07, .06))
    K.beacon(a, (-.55, .75, .735), parent=t, r=.07)
    a.part('Beacon', 'Alloy', t).box((.04, .04, .02), loc=(-.55, .75, .74), bevel=0)
    # The search radar on its mast behind the hatch (spins).
    k.lathe(a.part('Radar_mast', 'Steel', t), [(.07, 0), (.07, .5), (.05, .55)], loc=(0, .85, .72), seg=8)
    r = a.pivot('Radar', (0, .85, 1.3), t)
    K.dish(a.part('Radar_dish', 'Armor', r), a.part('Radar_feed', 'Steel', r), (0, 0, .25), r=.42,
           normal=(0, -1, .2), seg=14)
    a.part('Radar_feed', 'Steel', r).box((.1, .1, .3), loc=(0, .05, .1), bevel=0)


def _shilka(a, t):
    """aa_turret_a: the ZSU-23-4's flat slab-sided turret, four 23 mm barrels, the RPK-2 dish, the cupola."""
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.95, -.85), (.95, -.85), (1.0, -.7), (1.0, 1.0), (-1.0, 1.0), (-1.0, -.7)]
    top = [(-.85, -.6), (.85, -.6), (.9, -.48), (.9, .9), (-.9, .9), (-.9, -.48)]
    C.slab_loft(body, bot, top, 0, .62)
    K.plate(a.part('Turret_armor', 'Armor', t), (1.6, 1.3, .03), loc=(0, .2, .635), chamfer=.01)
    st = a.part('Turret_steel', 'Steel', t)
    for s in (-1, 1):
        st.box((.03, 1.6, .05), loc=(s * 1.0, .1, .3), bevel=0)
        for y in (-.3, .2, .7):
            K.handle(st, (s * 1.0, y - .1, .45), (s * 1.0, y + .1, .45), (s, 0, 0), h=.04, r=.01)
    # The wide mantlet and four 23 mm barrels in two pairs (upper and lower).
    man = a.part('Mantlet', 'Armor', t)
    k.extrude(man, [(-.18, -.22), (.12, -.25), (.16, .25), (-.14, .27)], 1.0, loc=(0, -.9, .32), axis='X',
              chamfer=.03, corner=.02)
    pitch = math.radians(20)
    tips = []
    names = ['', '_2', '_3', '_4']
    for i, (x, z) in enumerate(((-.36, .43), (.36, .43), (-.36, .24), (.36, .24))):
        tips.append(_barrel(a, f'Main_cannon{names[i]}', t, (x, -1.0, z), 1.95, .032, pitch,
                            brake=f'Muzzle_brake{names[i]}', sleeve=1, seg=8))
        a.part('Barrel_jackets', 'Armor', t).cyl(.06, .4, loc=(x, -1.15, z + .06), rot=(R90 - pitch, 0, 0), seg=8,
                                                 bevel=0)
    cx = sum(p[0] for p in tips) / 4
    cz = sum(p[2] for p in tips) / 4
    a.pivot('Muzzle_main', (cx, tips[0][1] - .03, cz), t)
    # The RPK-2 dish on its folding mast at the rear (spins), the commander's cupola and the driver's hatch.
    mast = a.part('Radar_mast', 'Steel', t)
    k.block(mast, (.5, .3, .25), loc=(0, .75, .62), chamfer=.03)
    mast.limb((0, .8, .85), (0, .82, 1.25), .05, .06, bevel=0)
    r = a.pivot('Radar', (0, .82, 1.3), t)
    K.dish(a.part('Radar_dish', 'Armor', r), a.part('Radar_feed', 'Steel', r), (0, 0, .35), r=.55,
           normal=(0, -1, .15), seg=16)
    a.part('Radar_feed', 'Steel', r).box((.12, .12, .3), loc=(0, .05, .15), bevel=0)
    k.lathe(a.part('Cupola', 'Armor', t), [(.26, 0), (.26, .12), (.2, .2), (0, .22)], loc=(-.45, .2, .63), seg=10,
            worn=(2,))
    for i in range(4):
        u = i * TAU / 4 - R90
        K.periscope(a, (-.45 + math.cos(u) * .23, .2 + math.sin(u) * .23, .66),
                    facing=(math.cos(u), math.sin(u), 0), parent=t, size=(.08, .06, .05))
    C.hatch(a, (.45, .35, .635), r=.24, parent=t)
    # The base's missile pivot kept on the roof (the gate reads the base def's `sam`; the branch carries no missile).
    a.pivot('Muzzle_missile', (.75, .6, .7), t)
    K.beacon(a, (.75, -.35, .635), parent=t, r=.06)
    a.part('Beacon', 'Alloy', t).box((.04, .04, .02), loc=(.75, -.35, .64), bevel=0)
    for s in (-1, 1):
        a.part('Hatch_fittings', 'Steel', t).box((.3, .02, .2), loc=(s * .6, -.73, .45), rot=(-.3, 0, 0), bevel=0)
        k.block(a.part('Stowage', 'Canvas', t), (.18, .7, .22), loc=(s * 1.06, .45, .2), chamfer=.04)


def aa_turret(a, detail=False):
    """The AA turret: see the module docstring."""
    _emplacement(a, bays=3)
    t = a.pivot('Turret', (0, TY, RACE_Z))
    _gun_house(a, t)
    k.clean(a)


def aa_turret_a(a, detail=False):
    """The flak branch (ZSU-23-4 turret): see the module docstring."""
    _emplacement(a, bays=4)
    t = a.pivot('Turret', (0, TY, RACE_Z))
    _shilka(a, t)
    k.clean(a)


BUILDERS = {
    'aa_turret': (aa_turret, dict(ao_distance=.4, grime_height=.35)),
    'aa_turret_a': (aa_turret_a, dict(ao_distance=.4, grime_height=.35)),
}
