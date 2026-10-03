"""Prompt 35 wave 2 (lane A): four tower branches whose base tower is rebuilt in a later wave, rebuilt from scratch
each from its own spec (Tools/blender/specs/<id>.json). DECISIONS "Prompt 35 wave 2 (lane A)". They keep their base's
footprint so the later base rebuild can share the emplacement.

- mg_bunker_b (mg_bunker.flame, bunker_flame; unit_refs Abwehrflammenwerfer 42): a round cast pillbox in an earth
  mound with firing ports, its turning cast-steel cupola (`Turret`) carrying the flame projector (nozzle, igniter,
  hoses); behind it, in a sandbagged pit, the fuel and propellant bottles with their manifold and gauge; scorched
  ground in front, a rear door down steps, a vent stack, a periscope and a whip.
- aa_turret_b (aa_turret.sam, stinger_post; unit_refs Starstreak LML / Mistral ATLAS / RBS-70): a field-built
  sandbag pit open at the rear with duckboards, and on its pedestal the lightweight multiple launcher: the operator's
  seat, the sight unit, two pairs of missile tubes either side, the IFF antenna turning at the back (`Radar`); spare
  missile cases, a battery box, the radio, a camouflage net corner.
- artillery_emplacement_b (artillery_emplacement.mortar, mortar_240_fixed; unit_refs 2B8 / M-240): a U-shaped earth
  and sandbag emplacement open at the rear, the 240 mm mortar raised steeply on its two-wheeled carriage (the big
  baseplate, cradle, recoil cylinders, elevating screw), the loading jib with a bomb on the hook, bombs on pallets,
  the crew MG on a pintle post on the parapet (the roof-gun rule), a whip.
- cp_relay_b (an orphan branch file of the no-branch cp_relay; unit_refs cp_relay.loot "kho chiến lợi phẩm"): a
  salvage relay post: a HESCO-and-fence compound with a container store, a short lattice mast with two dishes and a
  whip, crates of captured kit, a captured gun on a stand, a generator and a flag pole.

Runtime nodes (kept): mg_bunker_b `Turret`, `Muzzle_main`; aa_turret_b `Turret`, `Radar`, `Muzzle_main`,
`Muzzle_missile[.001-.003]`; artillery_emplacement_b `Turret`, `Muzzle_main`, `Mount_mg`, `Muzzle_mg`; cp_relay_b
none. Built only from frontier_kit / mb_kit27 primitives, mb_kit35 and the wave's lean helpers; no other model's
builder. Metres, +Z up, -Y front, +X left. Each under 6,000 triangles.
"""
import math

import mb_kit27 as k
import mb_kit35 as K
import mb_p35_w2parts as W

R90 = math.pi / 2
TAU = math.tau


def _pad(a, outline, h=.1, mat='Concrete', name='Base'):
    k.extrude(a.part(name, mat), outline, h, loc=(0, 0, h / 2), axis='Z', corner=.05, taper=(.97, .97),
              caps=(False, True))


def _stones(a, n, x0, x1, y0, y1, z, seed=0, keep=None):
    """Small stones and clods scattered over a rectangle (golden-ratio spread), skipping points keep() rejects."""
    rk = a.part('Stones', 'Rock')
    for i in range(n):
        x = x0 + (x1 - x0) * ((i * .618 + seed * .13) % 1.0)
        y = y0 + (y1 - y0) * ((i * .382 + seed * .29) % 1.0)
        if keep and not keep(x, y):
            continue
        sz = .1 + (i % 4) * .04
        rk.box((sz, sz * 1.3, sz * .6), loc=(x, y, z + sz * .2), rot=(i * .7, i * .3, i * 1.3), bevel=0)


def _patches(a, spots, z):
    """Trampled ground: flat patches of gravel, bare sand, grass and soot (x, y, size, yaw, material)."""
    for i, (x, y, w, yaw, mat) in enumerate(spots):
        a.part(f'Ground_{mat.lower()}', mat).box((w, w * .7, .006), loc=(x, y, z + .003 + (i % 3) * .001),
                                                 rot=(0, 0, yaw), bevel=0)


def _dust_ring(a, r, n=6, z=.1, k_=.3, cy=0.0):
    for i in range(n):
        u = i * TAU / n
        K.dust(a, (math.cos(u) * r, cy + math.sin(u) * r, z), radius=1.0, k=k_)


# ============================================================================= mg_bunker_b
def mg_bunker_b(a):
    """mg_bunker_b: the flame bunker (see the module docstring)."""
    G = .05
    # The earth mound round the pillbox (sloped all round), turf, sandbag courses on its crest at the rear.
    k.lathe(a.part('Berm', 'Dirt'), [(2.2, G), (1.75, .55), (1.55, .62)], seg=16, caps=(False, False), worn=(1,))
    for i, (u, w) in enumerate(((.5, .9), (1.6, .8), (2.7, 1.0), (4.0, .8), (5.2, .9))):
        a.part('Berm_turf', 'Grass').box((w, .5, .03), loc=(math.cos(u) * 1.9, math.sin(u) * 1.9, .35),
                                         rot=(0, .7, u), bevel=0)
    W.bags(a, [(math.cos(t) * 1.75, math.sin(t) * 1.75, .55) for t in [math.radians(d) for d in range(20, 161, 20)]],
           layers=1, bag=(.55, .3, .17), seed=30)
    # The cast drum with its firing ports and lift joint, a Team band under the cupola, form ties.
    k.lathe(a.part('Walls', 'Plaster'), [(1.6, .5), (1.55, .9), (1.5, .93)], seg=16, caps=(False, False), worn=(2,))
    a.part('Team_band', 'Team').cyl(1.535, .1, loc=(0, 0, .82), seg=16, bevel=0)
    for d in (-60, 60, 120, 180, 240):
        t = math.radians(d - 90)
        a.part('Slits', 'Undercarriage').box((.4, .06, .1), loc=(math.cos(t) * 1.57, math.sin(t) * 1.57, .7),
                                             rot=(0, 0, t + R90), bevel=0)
    k.ring(a.part('Race', 'Steel'), [(1.32, .9), (1.45, .9), (1.45, .97), (1.32, .97)], seg=16)
    # The turning cast-steel cupola (the roof) with the flame projector in its embrasure.
    t = a.pivot('Turret', (0, 0, .97))
    k.lathe(a.part('Turret_body', 'Armor', t), [(1.4, 0), (1.38, .2), (1.2, .45), (.8, .65), (.3, .72), (0, .73)],
            seg=14, caps=(False, True), worn=(1, 3))
    a.part('Turret_band', 'Team', t).cyl(1.3, .08, loc=(0, 0, .3), seg=14, bevel=0)
    k.block(a.part('Embrasure', 'Armor', t), (.7, .5, .45), loc=(0, -1.3, .22), chamfer=.04)
    a.part('Embrasure_slot', 'Undercarriage', t).box((.4, .03, .16), loc=(0, -1.56, .22), bevel=0)
    fg = a.part('Flame_gun', 'Steel', t)
    k.lathe(fg, [(.1, 0), (.1, .4), (.07, .45), (.07, .95), (.1, 1.0), (.1, 1.12), (0, 1.12)],
            loc=(0, -1.55, .19), rot=K.FORWARD, seg=8, worn=(4,))
    a.part('Nozzle_soot', 'Charred', t).cyl(.075, .05, loc=(0, -2.68, .19), rot=(R90, 0, 0), seg=8, bevel=0)
    a.part('Igniter', 'Undercarriage', t).box((.08, .25, .08), loc=(.13, -2.45, .26), bevel=0)
    a.part('Hoses', 'Rubber', t).tube([(.1, -1.6, .3), (.25, -1.4, .55), (.35, -.9, .65)], .035, seg=4)
    a.pivot('Muzzle_main', (0, -2.74, .19), t)
    K.periscope(a, (-.45, -.5, .66), facing=(0, -1, 0), parent=t)
    k.lathe(a.part('Hatches', 'Armor', t), [(.38, .65), (.38, .72), (0, .76)], loc=(.2, .35, 0), seg=10)
    K.handle(a.part('Kit_handles', 'Steel', t), (.05, .35, .77), (.35, .35, .77), (0, 0, 1), h=.05)
    # Behind: the sandbagged fuel pit with the fuel and propellant bottles, manifold, gauge, the feed pipe.
    k.extrude(a.part('Base', 'Concrete'), [(-1.3, 1.5), (1.3, 1.5), (1.4, 2.3), (-1.4, 2.3)], .1, loc=(0, 0, G + .05),
              axis='Z', corner=.04, caps=(False, True))
    W.bags(a, [(-1.5, 1.45, G), (-1.6, 2.3, G), (1.6, 2.3, G), (1.5, 1.45, G)], layers=2, bag=(.55, .3, .17),
           seed=31)
    for i, x in enumerate((-.75, -.25, .25)):
        k.lathe(a.part('Fuel_tanks', 'BarrelRed'), [(0, -.6), (.17, -.55), (.2, -.45), (.2, .45), (.17, .55),
                                                    (0, .6)], loc=(x, 1.9, .43), rot=(R90, 0, 0),
                seg=8, worn=(2, 3))
    for x in (.7, .95):
        k.lathe(a.part('Gas_bottles', 'Steel'), [(.11, 0), (.11, .9), (.07, 1.0), (0, 1.03)], loc=(x, 1.95, .15),
                seg=8, worn=(1,))
    man = a.part('Manifold', 'Steel')
    man.tube([(-.75, 1.5, .65), (.95, 1.5, .65)], .03, seg=4)
    man.tube([(0, 1.5, .65), (0, 1.25, .75), (0, 1.0, .85)], .045, seg=5)
    k.lathe(a.part('Gauge', 'PlasterWhite'), [(.08, 0), (.08, .03), (0, .03)], loc=(.4, 1.47, .8), rot=(-R90, 0, 0),
            seg=8)
    a.part('Hazard_marks', 'Hazard').box((.5, .03, .35), loc=(-1.2, 1.38, .9), bevel=0)
    a.part('Flame_sign', 'BarrelRed').box((.36, .03, .24), loc=(-1.2, 1.36, .9), bevel=0)
    # The rear door down two steps, the vent stack, the whip antenna, an extinguisher.
    k.block(a.part('Door_well', 'Plaster'), (1.0, .55, .8), loc=(1.15, 1.25, .4), rot=(0, 0, -.5), chamfer=.03)
    K.door(a, (1.3, 1.5, .1), (.7, .7), normal=(.48, .88, 0), mat='Armor')
    k.lathe(a.part('Vents', 'Steel'), [(.08, 0), (.08, 1.4), (.18, 1.42), (.18, 1.5), (0, 1.56)],
            loc=(-1.1, .9, .55), seg=8, worn=(3,))
    K.whip_antenna(a.part('Antennas', 'Steel'), (-.9, 1.3, .6), h=2.7, r=.022)
    K.wire_fence(a, [(-1.6, -2.55, G), (0, -2.65, G), (1.6, -2.55, G)], h=.6, post=.8, strands=2, concertina=True)
    for i in range(12):
        u = i * TAU / 12
        a.part('Kit_bolts', 'Steel', t).cyl(.03, .03, loc=(math.cos(u) * 1.25, math.sin(u) * 1.25, .42), seg=4,
                                            bevel=0)
    W.stack(a, (-1.9, .8, G), n=2, size=(.45, .28, .2), yaw=1.2, seed=36)
    for i in range(10):
        u = i * TAU / 10 + .2
        a.part('Pickets', 'Wood').cyl(.03, .7, loc=(math.cos(u) * 2.15, math.sin(u) * 2.15, G + .3), seg=4, bevel=0)
    _stones(a, 24, -2.1, 2.1, -2.6, 2.4, G, seed=1, keep=lambda x, y: x * x + y * y > 4.0 or y < -2.0)
    k.lathe(a.part('Extinguishers', 'BarrelRed'), [(.07, 0), (.07, .4), (.04, .46), (0, .48)], loc=(1.35, 2.1, .15),
            seg=8, worn=(1,))
    # Scorched ground in front, the field of fire's range stakes.
    sc = a.part('Scorch', 'Charred')
    for i, (x, y, w, d, r) in enumerate(((0, -2.35, 1.5, .7, 0), (.5, -2.15, .7, .5, .6), (-.6, -2.2, .8, .4, -.5))):
        sc.box((w, d, .006), loc=(x, y, G + .004 + i * .001), rot=(0, 0, r), bevel=0)
    for x in (-1.9, 1.9):
        a.part('Range_post', 'Hazard').cyl(.03, .7, loc=(x, -1.9, G + .35), seg=5, bevel=0)
    _dust_ring(a, 2.0, z=G)
    k.clean(a)


# ============================================================================= aa_turret_b
def aa_turret_b(a):
    """aa_turret_b: the lightweight multiple launcher in its sandbag pit (see the module docstring)."""
    G = .1
    _pad(a, [(-2.25, -2.0), (-2.0, -2.25), (2.0, -2.25), (2.25, -2.0), (2.25, 2.25), (-1.4, 2.25), (-2.25, 1.4)], G,
         mat='Dirt')
    ring = [(math.sin(t) * 1.95, -math.cos(t) * 1.95, G) for t in [math.radians(d) for d in range(-130, 131, 13)]]
    W.bags(a, ring, layers=1, bag=(.6, .32, .18), seed=32)
    W.bags(a, [(x, y, G + .16) for x, y, _ in ring], layers=1, bag=(.6, .32, .18), seed=33, mat='Canvas',
           name='Sandbags_new')
    W.bags(a, [(x * 1.02, y * 1.02, G + .32) for x, y, _ in ring[3:-3]], layers=1, bag=(.6, .32, .18), seed=34)
    st0 = a.part('Stains', 'Charred')
    for (x, y, r) in ((.5, -.6, .3), (-.6, .2, 1.1), (.2, .9, 2.0)):
        st0.box((.6, .4, .006), loc=(x, y, G + .004), rot=(0, 0, r), bevel=0)
    for (x, y, r) in ((-2.0, -2.0, .4), (2.05, -1.9, 1.2), (-2.1, .9, 2.2), (2.1, .3, .9), (0, -2.15, 0)):
        a.part('Turf', 'Grass').box((.5, .3, .05), loc=(x, y, G + .02), rot=(0, 0, r), bevel=0)
    W.stack(a, (-1.5, 1.2, G), n=2, size=(.5, .3, .22), yaw=.3, seed=35)
    _stones(a, 30, -2.2, 2.2, -2.2, 2.2, G, seed=2, keep=lambda x, y: x * x + y * y > 4.6 or (abs(x) < 1.6 and abs(y) < 1.6 and x * x + y * y > .6))
    for (x, y, r) in ((-1.0, -1.0, .5), (1.1, -.9, 2.1), (1.2, .7, 1.3)):
        a.part('Stains', 'Charred').box((.35, .5, .006), loc=(x, y, G + .005), rot=(0, 0, r), bevel=0)
    _patches(a, [(-1.1, -.3, .7, .4, 'Sandstone'), (.9, -.2, .6, 1.2, 'Rock'), (-.3, -1.2, .7, 2.0, 'SandstoneDark'),
                 (.6, -1.25, .5, .7, 'Sandstone'), (-1.2, .55, .5, 1.6, 'Rock'), (2.05, 1.6, .6, .3, 'FoliageDark'),
                 (-2.0, -1.4, .6, 1.0, 'FoliageLight'), (1.6, -2.0, .5, 2.4, 'FoliageDark'),
                 (-.2, 2.05, .8, .2, 'SandstoneDark'), (1.0, 1.9, .5, .9, 'Rock')], G)
    duck = a.part('Duckboards', 'Wood')
    for i in range(6):
        duck.box((1.2, .12, .04), loc=(0, .9 + i * .2, G + .02), bevel=0)
    for x in (-.5, .5):
        duck.box((.08, 1.2, .05), loc=(x, 1.4, G + .01), bevel=0)
    k.ring(a.part('Race', 'Steel'), [(.55, G), (.62, G), (.62, G + .1), (.55, G + .1)], seg=12)
    t = a.pivot('Turret', (0, 0, .3))
    st = a.part('Turret_steel', 'Steel', t)
    k.lathe(a.part('Turret_socket', 'Armor', t), [(.5, 0), (.5, .08), (.2, .12), (.15, .95), (0, .95)], seg=10,
            worn=(1,))
    # The operator's seat and foot rest, the sight unit with its hood, the hand grips.
    k.block(a.part('Seats', 'Canvas', t), (.45, .42, .1), loc=(0, .5, .62), chamfer=.02)
    k.block(a.part('Seats', 'Canvas', t), (.45, .08, .5), loc=(0, .72, .9), chamfer=.02)
    st.tube([(0, .1, .55), (0, .5, .55)], .03, seg=4)
    st.box((.4, .2, .03), loc=(0, -.35, .3), bevel=0)
    k.block(a.part('Sight', 'Armor', t), (.32, .38, .3), loc=(0, -.25, 1.1), chamfer=.03)
    a.part('Glass', 'Glass', t).box((.2, .03, .12), loc=(0, -.45, 1.14), bevel=0)
    K.handle(a.part('Kit_handles', 'Steel', t), (-.22, -.05, 1.0), (.22, -.05, 1.0), (0, 1, .3), h=.08)
    # The two launcher pairs on side arms, elevated 12 degrees: tubes with end caps (dark mouths), clamps, the
    # thermal battery boxes under them.
    el = math.radians(12)
    rot = (R90 - el, 0, 0)
    d = (0, -math.cos(el), math.sin(el))
    mouths = []
    for s in (-1, 1):
        x = s * .86
        st.tube([(0, 0, .9), (x * .9, 0, 1.4)], .04, seg=5)
        k.block(a.part('Launcher_frame', 'Team', t), (.12, .9, .55), loc=(x * .78, -.05, 1.45), rot=(-el, 0, 0),
                chamfer=.02)
        for zt in (2.25, 1.85):
            y0 = .78
            L = (y0 + (.65 if zt > 2.0 else .84)) / math.cos(el)
            z0 = zt - .3 - L * math.sin(el)
            c = (x, y0 + d[1] * L / 2, z0 + d[2] * L / 2)
            k.lathe(a.part('Tube_bodies', 'Team', t), [(.08, -L / 2), (.08, L / 2)], loc=c, rot=rot, seg=8,
                    caps=(False, False), worn=(0, 1))
            for f in (-.46, .46):
                a.part('Tube_caps', 'Undercarriage', t).cyl(.09, .06, loc=(c[0], c[1] + d[1] * f * L,
                                                                           c[2] + d[2] * f * L), rot=rot, seg=8,
                                                           bevel=0)
            mouths.append((x, y0 + d[1] * L, zt - .3))
        a.part('Battery_boxes', 'Fuel', t).box((.12, .2, .14), loc=(x, .4, 1.05), bevel=0)
    K.suffixed(a)
    order = [mouths[0], mouths[2], mouths[1], mouths[3]]          # upper left, upper right, lower left, lower right
    for i, p in enumerate(order):
        a.pivot(K.name('Muzzle_missile', i), p, t)
    a.pivot('Muzzle_main', (-.25, -1.41, .8), t)
    # The IFF antenna turning on a post behind the seat.
    st.tube([(0, .8, .9), (0, .62, 1.6)], .03, seg=4)
    r = a.pivot('Radar', (0, .62, 1.7), t)
    k.block(a.part('Radar_array', 'Armor', r), (.6, .06, .2), loc=(0, 0, -.1), chamfer=.015)
    a.part('Radar_face', 'Undercarriage', r).box((.55, .02, .14), loc=(0, -.04, 0), bevel=0)
    # Round the pit: spare missile cases on a rack, the battery box and radio, a whip, a camouflage net corner.
    rack = a.part('Rocket_rack', 'Wood')
    for x in (-1.0, -.2):
        rack.box((.08, .5, .35), loc=(x, 1.7, G + .17), bevel=0)
    for i in range(3):
        k.block(a.part('Missile_cases', 'Crate'), (1.05, .2, .2), loc=(-.6, 1.6 + (i % 2) * .22, G + .45 + (i // 2) * .2),
                chamfer=0)
    k.block(a.part('Radio_box', 'Armor'), (.35, .25, .3), loc=(1.1, 1.6, G + .15), chamfer=.02)
    K.whip_antenna(a.part('Antennas', 'Steel'), (1.2, 1.7, G + .3), h=2.4, r=.022)
    a.part('Kit_cables', 'Undercarriage').tube([(1.0, 1.55, G + .1), (.5, .9, G + .02), (.1, .3, G + .3)], .02, seg=4)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (1.6, 1.5, G), rot=(0, 0, .3))
    poles = [(1.4, 1.0, 1.8), (2.15, 1.1, 1.6), (2.15, 2.15, 1.5), (1.3, 2.15, 1.7)]
    for (x, y, h) in poles:
        a.part('Net_poles', 'Wood').cyl(.035, h, loc=(x, y, G + h / 2), seg=5, bevel=0)
    pts = [(x, y, G + h) for (x, y, h) in poles]
    mid = (1.75, 1.6, G + 1.35)
    tris = []
    for i in range(4):
        tris += [pts[i], pts[(i + 1) % 4], mid]
    a.part('Camo_net', 'Canvas').mesh(tris, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(4)])
    a.part('Camo_net', 'Canvas').mesh(tris, [(3 * i, 3 * i + 2, 3 * i + 1) for i in range(4)])
    for (x, y) in ((1.6, 1.2), (2.0, 1.9)):
        a.part('Camo_garnish', 'Foliage').box((.45, .35, .03), loc=(x, y, G + 1.5), rot=(.1, .1, x), bevel=0)
    a.part('Signs', 'PlasterWhite').box((.5, .03, .35), loc=(-1.6, 1.9, G + .6), bevel=0)
    a.part('Sign_posts', 'Wood').cyl(.03, .7, loc=(-1.6, 1.93, G + .35), seg=5, bevel=0)
    _dust_ring(a, 1.9, z=G)
    k.clean(a)


# ============================================================================= artillery_emplacement_b
def artillery_emplacement_b(a):
    """artillery_emplacement_b: the 240 mm mortar in its U-shaped emplacement (see the module docstring)."""
    G = .09
    _pad(a, [(-3.4, -3.3), (3.4, -3.3), (3.4, 3.4), (-2.6, 3.4), (-3.4, 2.6)], G, mat='Dirt')
    # The U of the emplacement: an earth berm with sloped faces, sandbag courses on its crest, timber revetment
    # inside, the crew's ammunition niche.
    berm = a.part('Berm', 'Dirt')
    k.extrude(berm, [(-.6, 0), (.6, 0), (.2, .65), (-.2, .65)], 6.6, loc=(0, -2.85, G), axis='X', caps=(True, True))
    for s in (-1, 1):
        k.extrude(berm, [(-.6, 0), (.6, 0), (.2, .65), (-.2, .65)], 5.0, loc=(s * 2.95, .15, G), rot=(0, 0, R90),
                  axis='X', caps=(True, True))
    W.bags(a, [(-2.9, -2.85, G + .65), (2.9, -2.85, G + .65)], layers=1, bag=(.6, .32, .18), seed=33)
    for s in (-1, 1):
        W.bags(a, [(s * 2.95, -2.4, G + .65), (s * 2.95, 2.5, G + .65)], layers=1, bag=(.6, .32, .18), seed=34 + s)
    rev = a.part('Revetment', 'Wood')
    for x in (-1.8, -.6, .6, 1.8):
        rev.box((.12, .12, .8), loc=(x, -2.25, G + .4), bevel=0)
    rev.box((4.4, .06, .25), loc=(0, -2.22, G + .55), bevel=0)
    rev.box((4.4, .06, .25), loc=(0, -2.22, G + .2), bevel=0)
    # The mortar: the big round baseplate, the carriage (two wheels, trail), the cradle and the tube raised steeply.
    t = a.pivot('Turret', (0, 0, .09))
    k.lathe(a.part('Baseplate', 'Armor', t), [(1.1, 0), (1.1, .1), (.95, .16), (.4, .2), (0, .2)], loc=(0, .55, 0),
            seg=14, worn=(1, 2))
    for i in range(6):
        u = i * TAU / 6
        a.part('Baseplate_ribs', 'Steel', t).box((.75, .06, .12), loc=(math.cos(u) * .62, .55 + math.sin(u) * .62,
                                                                     .2), rot=(0, 0, u), bevel=0)
    el = math.radians(62)
    tube_rot = (R90 - el, 0, 0)
    p0 = (0, .55, .35)
    L = 3.08
    d = (0, -math.cos(el), math.sin(el))
    c = tuple(p0[i] + d[i] * L / 2 for i in range(3))
    k.lathe(a.part('Mortar_tube', 'Team', t), [(.2, -L / 2), (.2, -L / 2 + .3), (.17, -L / 2 + .4), (.16, L / 2 - .15),
                                               (.19, L / 2 - .1), (.19, L / 2), (.13, L / 2), (.13, L / 2 - .1)],
            loc=c, rot=tube_rot, seg=10, worn=(5,))
    k.lathe(a.part('Breech', 'Armor', t), [(0, -.2), (.25, -.15), (.25, .15), (.2, .2)], loc=p0, rot=tube_rot, seg=10)
    for f in (.3, .55):
        q = tuple(p0[i] + d[i] * L * f for i in range(3))
        a.part('Tube_bands', 'Steel', t).cyl(.2, .08, loc=q, rot=tube_rot, seg=10, bevel=0)
    # Cradle and carriage: the yoke at 55 % up the tube, two legs to the axle, the wheels, recoil cylinders, the
    # elevating screw.
    q = tuple(p0[i] + d[i] * L * .45 for i in range(3))
    cr = a.part('Cradle', 'Armor', t)
    k.block(cr, (.6, .3, .25), loc=q, rot=(-el, 0, 0), chamfer=.03)
    car = a.part('Carriage', 'Armor', t)
    for s in (-1, 1):
        car.limb((s * .3, q[1], q[2]), (s * .75, -.55, .5), .12, .12, bevel=0)
        K.tread_wheel(a, (s * .95, -.55, .5), .5, .3, s, seg=12, parent=t)
        a.part('Recoil_cyl', 'Steel', t).tube([(s * .14, p0[1] - .05, p0[2] + .25), (s * .14, q[1] + .05, q[2] - .1)],
                                             .05, seg=6)
    a.part('Axles', 'Steel', t).cyl(.07, 1.7, loc=(0, -.55, .5), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Elevating_screw', 'Steel', t).tube([(0, -.55, .5), (0, q[1] - .1, q[2] - .15)], .045, seg=6)
    a.pivot('Muzzle_main', (0, -.78, 3.02), t)
    # The loading jib on the right rear with a 240 mm bomb on its hook, bombs on pallets, the shell tray.
    jx, jy = -1.9, 1.6
    jib = a.part('Crane', 'CraneYellow')
    jib.cyl(.09, 2.8, loc=(jx, jy, G + 1.4), seg=8, bevel=0)
    jib.box((.08, 1.6, .1), loc=(jx + .3, jy - .6, G + 2.75), rot=(0, 0, -.5), bevel=0)
    a.part('Crane_truss', 'Steel').tube([(jx, jy, G + 2.2), (jx + .6, jy - 1.3, G + 2.72)], .02, seg=3)
    a.part('Kit_cables', 'Undercarriage').tube([(jx + .65, jy - 1.3, G + 2.7), (jx + .65, jy - 1.3, G + 1.6)], .012,
                                               seg=3)
    K.missile(a, (jx + .65, jy - 1.3, G + 1.55), .12, 1.0, direction=(0, 0, -1), fins=4, body='Mortar_bombs',
              seeker='Steel', band=False)
    k.block(a.part('Crane_base', 'Concrete'), (.6, .6, .3), loc=(jx, jy, G + .15), chamfer=.04)
    pal = a.part('Pallets', 'Wood')
    for (x, y) in ((1.9, 1.0), (1.9, 1.95)):
        pal.box((1.2, .8, .12), loc=(x, y, G + .06), bevel=0)
        for i in range(3):
            K.missile(a, (x - .4 + i * .4, y + .38, G + .27), .12, .95, direction=(0, -1, 0), fins=4,
                      body='Mortar_bombs', seeker='Steel', band=False)
    k.block(a.part('Loading_tray', 'Steel'), (.5, 1.4, .1), loc=(-.7, 1.4, G + .55), chamfer=0)
    for (x, y) in ((-.9, .8), (-.5, .8), (-.9, 2.0), (-.5, 2.0)):
        a.part('Loading_tray', 'Steel').box((.05, .05, .5), loc=(x, y, G + .25), bevel=0)
    # The crew MG on a pintle post on the front-left parapet (the roof-gun rule), the whip and the radio.
    K.pintle_mg(a, None, (1.73, -2.47, .72), post=.4, scale=1.0, length=.9)
    # The plank floor under the carriage, side revetments, a second sandbag course (newer bags), a camouflage net
    # over the rear right, ammunition boxes and charge cases.
    fl = a.part('Floor', 'Wood')
    for i in range(10):
        fl.box((2.6, .2, .05), loc=(0, -1.6 + i * .27, G + .025), rot=(0, 0, .01 * (i % 3 - 1)), bevel=0)
    for s in (-1, 1):
        for y in (-1.3, 0, 1.3):
            rev.box((.12, .12, .8), loc=(s * 2.25, y, G + .4), bevel=0)
        rev.box((.06, 3.6, .25), loc=(s * 2.22, 0, G + .5), bevel=0)
    W.bags(a, [(-2.6, -2.85, G + .83), (2.6, -2.85, G + .83)], layers=1, bag=(.6, .32, .18), seed=37, mat='Canvas',
           name='Sandbags_new')
    poles = [(-2.3, 1.0, 2.0), (-.8, 1.0, 2.2), (-.8, 3.1, 1.9), (-2.3, 3.1, 1.8)]
    for (x, y, h) in poles:
        a.part('Net_poles', 'Wood').cyl(.04, h, loc=(x, y, G + h / 2), seg=5, bevel=0)
    pts = [(x, y, G + h) for (x, y, h) in poles]
    mid = (-1.55, 2.05, G + 1.6)
    tris = []
    for i in range(4):
        tris += [pts[i], pts[(i + 1) % 4], mid]
    a.part('Camo_net', 'Canvas').mesh(tris, [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(4)])
    a.part('Camo_net', 'Canvas').mesh(tris, [(3 * i, 3 * i + 2, 3 * i + 1) for i in range(4)])
    for (x, y) in ((-1.9, 1.5), (-1.1, 2.5), (-1.9, 2.7)):
        a.part('Camo_garnish', 'Foliage').box((.5, .4, .03), loc=(x, y, G + 1.8), rot=(.12, .1, x), bevel=0)
    W.stack(a, (1.0, 2.6, G), n=3, size=(.55, .3, .24), yaw=.2, seed=38)
    # Sod and turf on the berm slopes (two grass tones), stones over the floor and the berms.
    for (x, y, w, d, yaw, tilt) in ((0, -3.25, 6.0, .35, 0, .55), (0, -2.45, 4.0, .3, 0, -.55), (3.35, .2, 4.4, .35, R90, .55),
                                    (-3.35, .2, 4.4, .35, R90, .55), (2.55, .2, 3.6, .3, R90, -.55),
                                    (-2.55, .2, 3.6, .3, R90, -.55)):
        mat = 'Grass' if tilt > 0 else 'FoliageDark'
        if yaw == 0:
            size, rot = (w, d, .03), (tilt, 0, 0)
        else:
            size, rot = (d, w, .03), (0, tilt * (1 if x > 0 else -1), 0)
        a.part(f'Berm_sod_{mat.lower()}', mat).box(size, loc=(x, y, G + .33), rot=rot, bevel=0)
    _stones(a, 32, -3.3, 3.3, -3.3, 3.3, G, seed=3, keep=lambda x, y: abs(x) < 2.3 and -2.3 < y < .3 and abs(x) > 1.2)
    _patches(a, [(-1.7, -1.6, .8, .4, 'Sandstone'), (1.6, -1.7, .7, 1.2, 'Rock'), (-1.75, .1, .7, 2.0, 'SandstoneDark'),
                 (1.7, .2, .6, .7, 'Sandstone'), (-1.0, 3.0, .8, 1.6, 'Rock'), (.6, 3.05, .7, .3, 'FoliageDark'),
                 (2.6, 3.0, .6, 1.0, 'SandstoneDark'), (-1.6, -.8, .5, 2.4, 'Charred'), (1.3, -1.0, .5, .5, 'Charred'),
                 (-2.0, 1.4, .6, .2, 'Sandstone'), (2.0, 1.45, .7, .9, 'Rock'), (0, 2.75, .6, 1.4, 'Sandstone')], G)
    W.stack(a, (2.4, 2.7, G), n=2, size=(.55, .3, .24), yaw=-.3, seed=39)
    for i in range(4):
        a.part('Charge_cans', 'Fuel').cyl(.13, .55, loc=(.3 + i * .3, 2.0, G + .28), seg=8, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-2.6, 2.6, G), h=2.6, r=.022)
    k.block(a.part('Radio_box', 'Armor'), (.35, .25, .3), loc=(-2.4, 2.75, G + .15), chamfer=.02)
    for (x, y) in ((-2.0, -1.6), (2.0, -1.6)):
        a.part('Aiming_posts', 'Hazard').cyl(.03, 1.4, loc=(x, y, G + .7), seg=5, bevel=0)
        a.part('Aiming_bands', 'Charred').cyl(.034, .15, loc=(x, y, G + 1.0), seg=5, bevel=0)
    a.part('Scorch', 'Charred').box((1.6, 1.0, .006), loc=(0, -1.0, G + .004), bevel=0)
    _dust_ring(a, 2.6, n=8, z=G)
    k.clean(a)


# ============================================================================= cp_relay_b
def cp_relay_b(a):
    """cp_relay_b: the salvage relay post (see the module docstring)."""
    G = .1
    _pad(a, [(-2.0, -2.0), (2.0, -2.0), (2.0, 2.0), (-2.0, 2.0)], G)
    j = a.part('Base_joints', 'Undercarriage')
    for v in (-1.0, 0, 1.0):
        j.box((3.9, .03, .01), loc=(0, v, G + .003), bevel=0)
        j.box((.03, 3.9, .01), loc=(v, 0, G + .003), bevel=0)
    # HESCO cells along the front and the left, a wire fence on the right with its gate posts.
    for i in range(3):
        K.hesco(a, (-1.0 + i * 1.0, -1.65, G), size=(.95, .7, 1.0))
    for i in range(2):
        K.hesco(a, (1.7, -.6 + i * 1.0, G), size=(.7, .95, 1.0))
    K.wire_fence(a, [(-1.95, -1.2, G), (-1.95, 1.95, G), (0, 1.95, G)], h=1.4, post=.8, strands=3, concertina=False)
    # The container store at the rear left (its roof, doors with locking bars, Team stripe).
    W.slab(a.part('Shelter', 'ContainerBlue'), (2.4, 1.2, 1.25), (.6, 1.25, G), caps=(False, False))
    k.block(a.part('Roof', 'ContainerBlue'), (2.45, 1.25, .08), loc=(.6, 1.25, G + 1.29), chamfer=0)
    for x in (-.3, .1, .5, .9, 1.3):
        a.part('Container_ribs', 'Undercarriage').box((.05, 1.23, 1.2), loc=(x + .1, 1.25, G + .62), bevel=0)
    door = a.part('Doors', 'ContainerBlue')
    door.box((.03, 1.1, 1.15), loc=(-.62, 1.25, G + .6), bevel=0)
    for y in (.95, 1.55):
        a.part('Locking_bars', 'Steel').cyl(.02, 1.15, loc=(-.65, y, G + .6), seg=4, bevel=0)
    a.part('Team_band', 'Team').box((2.42, .02, .15), loc=(.6, .64, G + 1.0), bevel=0)
    # The short lattice mast with two dishes and a whip, guyed; the equipment box at its foot.
    mx, my = -1.1, .6
    ms = a.part('Mast', 'Steel')
    for (dx, dy) in ((-.25, -.25), (.25, -.25), (0, .3)):
        ms.tube([(mx + dx, my + dy, G), (mx + dx * .3, my + dy * .3, G + 3.1)], .03, seg=4)
    for z in (.8, 1.6, 2.4):
        f = 1 - .7 * z / 3.1
        pts = [(mx + dx * f, my + dy * f, G + z) for (dx, dy) in ((-.25, -.25), (.25, -.25), (0, .3), (-.25, -.25))]
        ms.tube(pts, .015, seg=3, caps=False)
    K.dish(a.part('Dish', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (mx - .25, my - .1, G + 2.6), r=.42,
           normal=(-.3, -1, .1), seg=12)
    K.dish(a.part('Dish', 'PlasterWhite'), a.part('Dish_feed', 'Steel'), (mx + .2, my + .1, G + 2.0), r=.32,
           normal=(.5, 1, 0), seg=12)
    K.whip_antenna(a.part('Antennas', 'Steel'), (mx, my, G + 3.1), h=.5, r=.02)
    for (x, y) in ((-1.9, -.4), (-1.9, 1.7), (-.2, .9)):
        a.part('Guy_wires', 'Steel').tube([(mx, my, G + 2.8), (x, y, G)], .007, seg=3)
    k.block(a.part('Equipment_box', 'Armor'), (.5, .4, .7), loc=(-1.2, 1.4, G + .35), chamfer=.03)
    # Salvage: crates of captured kit (some open), a captured MG on a stand, tyres, a generator, the flag pole.
    crates = a.part('Crates', 'Crate')
    straps = a.part('Kit_straps', 'Steel')
    for (x, y, z, r) in ((.6, -.6, 0, .1), (.6, -.6, .35, -.15), (1.1, .1, 0, .5)):
        K.crate(crates, straps, (.8, .5, .35), (x, y, G + z), rot=(0, 0, r), bands=1)
    k.block(a.part('Crates', 'Crate'), (.8, .5, .2), loc=(-.3, -.5, G + .1), chamfer=0)
    for i in range(3):
        a.part('Loose_rifles', 'Undercarriage').box((.9, .06, .05), loc=(-.3, -.62 + i * .12, G + .22), rot=(0, 0, .05),
                                                    bevel=0)
    st = a.part('Gun_stand', 'Steel')
    for u in (0, 2.1, 4.2):
        st.tube([(-.2, .4, G + .9), (-.2 + math.cos(u) * .4, .4 + math.sin(u) * .4, G)], .02, seg=4)
    a.part('Captured_gun', 'Armor').box((.12, .7, .14), loc=(-.2, .25, G + .98), bevel=0)
    a.part('Captured_gun', 'Armor').cyl(.025, .7, loc=(-.2, -.35, G + 1.0), rot=(R90, 0, 0), seg=6, bevel=0)
    for i in range(2):
        k.lathe(a.part('Tyres', 'Rubber'), [(.25, 0), (.4, .02), (.42, .12), (.4, .22), (.25, .24)],
                loc=(1.45, -1.0, G + i * .24), seg=10, caps=(False, False))
    k.block(a.part('Generator', 'Armor'), (.6, .45, .45), loc=(1.5, .9, G + .22), chamfer=.03)
    K.exhaust(a, (1.65, .9, G + .45), r=.035, length=.35)
    a.part('Flag_pole', 'Steel').cyl(.025, 3.4, loc=(1.85, 1.85, G + 1.7), seg=6, bevel=0)
    a.part('Flag', 'Team').box((.03, .7, .45), loc=(1.85, 1.5, G + 3.15), rot=(0, 0, .1), bevel=0)
    _dust_ring(a, 1.7, z=G)
    k.clean(a)


BUILDERS = {
    'mg_bunker_b': (mg_bunker_b, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
    'aa_turret_b': (aa_turret_b, dict(ao_distance=.5, grime_height=.12, ao_strength=.55)),
    'artillery_emplacement_b': (artillery_emplacement_b, dict(ao_distance=.4, grime_height=.1, ao_strength=.45)),
    'cp_relay_b': (cp_relay_b, dict(ao_distance=.6, grime_height=.4, ao_strength=.65)),
}
