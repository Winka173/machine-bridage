"""Play-test 14 model wave M6 (lane A): the two gun air-defence vehicles redrawn with their real gun spacing, and the
three hangars of wave M4 given more detail (owner, Docs/prompts/playtest14_vi.txt: "self propelled aa gun, gun missile
aa: check lai model, 2 nong sung auto canon co ve sai, no hoi xa, check design thuc te"; DECISIONS "Play-test 14 model
wave M6 (lane A)").

- aa_vehicle (Self-propelled AA gun): the Leopard-1 hull and running gear of prompt 35 wave 4 kept; a new turret after
  the Gepard / Type 87 / K30 Biho family: a compact box turret with the two 35 mm guns in armoured housings hard
  against its cheeks at mid height (barrel axes 2.0 m apart, inside the hull's width, no longer out over the fenders),
  both on one baked `Elevation` cradle with the trunnion through the turret; the tracking radar dish between them on
  the turret front, the search radar on its mast over the rear, the twin Stinger box (`Mount_missile`) on the rear
  roof, smoke dischargers on the rear cheeks. Both barrels fire: `Muzzle_main` between the mouths with
  `Muzzle_b1_main` / `Muzzle_b2_main` at the two brakes (ModelLibrary.AddBarrelPoints), Main_cannon / Main_cannon_2
  and Muzzle_brake / Muzzle_brake_2 recoil in turn.
- heavy_aa (Gun-missile AA): the KamAZ 8x8 of wave 8 kept; a new Pantsir-S1 / Tunguska combat module: the turret
  house with the round tracking array in its face, the two twin-barrel 2A38M 30 mm guns on the turret's cheeks (pair
  axes 1.5 m apart, the two barrels of a gun 0.15 m apart), the two six-round 57E6 packs outboard of them, guns and
  packs on one `Elevation` trunnion; the search radar (`Radar`) on its post at the rear. Every barrel fires:
  `Muzzle_b1_main` .. `Muzzle_b4_main` under `Muzzle_main` (left and right in turn); `Muzzle_missile` .. `.003` at
  the four tube columns.
- drone_hangar (+ _a, _b), vehicle_hangar_base, aircraft_hangar: see the hangar section.

Built from frontier_kit / mb_kit27 / mb_kit35 primitives only. Metres, +Z up, -Y front, +X left.
"""
import math
import random

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K
import mb_p35c_parts as C
import mb_p35_w2parts as W
import mb_p35_aa_vehicle as GEP
import mb_p35_wave8_trucks as TR

R90 = math.pi / 2
TAU = math.tau


def _barrel_muzzles(a, muzzle, xs, tag='main', zs=None):
    """Muzzle_b<k>_<tag> under the pivot `muzzle`, one per barrel at the x offsets `xs` (in firing order)."""
    for i, x in enumerate(xs):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, zs[i] if zs else 0), muzzle)


# ============================================================================= aa_vehicle (Gepard / Type 87 family)
GX = 1.0            # barrel axis |x| (turret frame): 2.0 m between the barrels, inside the 2.76 m hull
EL = (0, -.42, .5)  # the trunnion (turret frame)
GTIP = -2.88        # barrel mouth y (Elevation frame)


def _kda(a, el, s):
    """One Oerlikon KDA 35 mm in its armoured housing on side s of the turret (Elevation frame)."""
    tag = '' if s > 0 else '_2'
    x = s * GX
    hs = a.part('Gun_housing', 'Team', el)
    # The housing: long, its nose stepped down to the barrel, the top bevelled towards the turret.
    k.extrude(hs, [(-.78, -.1), (-.62, -.2), (.62, -.2), (.7, -.05), (.62, .22), (-.5, .22), (-.72, .1)], .32,
              loc=(x, 0, 0), axis='X', chamfer=.025, corner=.03)
    a.part('Gun_housing_lids', 'Armor', el).box((.26, .7, .02), loc=(x, .05, .232), bevel=0)
    K.rivet_line(a.part('Kit_rivets', 'Steel', el), (x + s * .165, -.5, .14), (x + s * .165, .5, .14), (s, 0, 0),
                 pitch=.2, r=.012)
    K.hinge(a.part('Kit_hinges', 'Steel', el), (x - s * .1, -.3, .235), (x - s * .1, .35, .235), r=.018, knuckles=3)
    # The trunnion hub into the turret cheek and the ammunition feed chute over it.
    a.part('Trunnions', 'Steel', el).cyl(.13, .22, loc=(s * .8, 0, 0), rot=(0, R90, 0), seg=10, bevel=.01)
    a.part('Gun_feeds', 'Armor', el).box((.14, .34, .16), loc=(s * .86, .2, .14), bevel=.01)
    # The barrel: breech sleeve, the tube with its cooling rings, the brake and the muzzle velocity radar.
    bar = a.part(f'Main_cannon{tag}', 'Steel', el)
    k.lathe(bar, [(.085, 0), (.085, .22), (.06, .27), (.05, .7), (.045, 2.0), (0, 2.0)], loc=(x, -.66, 0),
            rot=K.FORWARD, seg=10, worn=(1,))
    for j in range(4):
        bar.cyl(.062, .035, loc=(x, -1.05 - j * .13, 0), rot=K.FORWARD, seg=10, bevel=0)
    br = a.part(f'Muzzle_brake{tag}', 'Undercarriage', el)
    k.lathe(br, [(.048, 0), (.072, .03), (.072, .2), (.058, .24), (0, .24)], loc=(x, GTIP + .24, 0), rot=K.FORWARD,
            seg=10, worn=(1,))
    br.box((.07, .13, .1), loc=(x, GTIP + .2, .1), bevel=.01)                       # the v0 radar


def _gepard_turret(a, detail=False):
    t = a.pivot('Turret', GEP.TUR)
    K.turret_ring(a.part('Turret_ring', 'Armor'), GEP.TUR, .95, h=.05)
    body = a.part('Turret_body', 'Team', t)
    bot = [(-.5, -1.12), (.5, -1.12), (.8, -.85), (.82, 1.2), (.66, 1.42), (-.66, 1.42), (-.82, 1.2), (-.8, -.85)]
    top = [(-.42, -.82), (.42, -.82), (.7, -.6), (.72, 1.15), (.58, 1.32), (-.58, 1.32), (-.72, 1.15), (-.7, -.6)]
    C.slab_loft(body, bot, top, 0, .9)
    k.block(a.part('Turret_roof', 'Armor', t), (1.3, 1.9, .04), loc=(0, .3, .9), chamfer=.01)
    # The cheek armour behind the guns (bolted plates) and the rear bustle box.
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        K.chamfer_box(arm, (.04, .9, .5), loc=(s * .835, .75, .42), c=.01)
        K.rivet_line(a.part('Kit_rivets', 'Steel', t), (s * .86, .35, .62), (s * .86, 1.15, .62), (s, 0, 0),
                     pitch=.2, r=.012)
    C.stowage_box(a, (1.25, .34, .4), (0, 1.58, .42), mat='Armor', latches=2, parent=t)
    # The guns on their cradle.
    el = a.pivot('Elevation', EL, t)
    _kda(a, el, 1)
    _kda(a, el, -1)
    a.part('Cradle', 'Armor', el).cyl(.07, 1.5, loc=(0, 0, 0), rot=(0, R90, 0), seg=8, bevel=0)   # the cross shaft
    m = a.pivot('Muzzle_main', (0, GTIP, 0), el)
    _barrel_muzzles(a, m, (GX, -GX))
    # The tracking radar in its round housing on the turret face, between the guns.
    trk = a.part('Radar_tracker', 'Armor', t)
    k.lathe(trk, [(0, -.08), (.36, -.06), (.4, .04), (.4, .12)], loc=(0, -1.0, .5), rot=K.FORWARD, seg=16, worn=(2,))
    a.part('Radar_tracker_face', 'Undercarriage', t).cyl(.33, .02, loc=(0, -1.12, .5), rot=K.FORWARD, seg=16, bevel=0)
    a.part('Radar_tracker_feed', 'Steel', t).cyl(.06, .12, loc=(0, -1.18, .5), rot=K.FORWARD, seg=8, bevel=0)
    a.part('Radar_tracker_feed', 'Steel', t).box((.5, .02, .03), loc=(0, -1.135, .5), bevel=0)
    # Sights: the commander's roof periscope and the gunner's sight block, laser rangefinder; hatches.
    a.part('Sight', 'Steel', t).cyl(.08, .16, loc=(.35, -.35, .98), seg=8, bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.26, .3, .22), loc=(.35, -.35, 1.15), c=.03)
    a.part('Glass', 'Glass', t).box((.18, .01, .1), loc=(.35, -.505, 1.17), bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.22, .26, .18), loc=(-.4, -.55, .99), c=.03)
    a.part('Glass', 'Glass', t).box((.15, .01, .08), loc=(-.4, -.685, 1.0), bevel=0)
    C.hatch(a, (.38, .35, .92), r=.24, parent=t, periscope=True)
    C.hatch(a, (-.38, .35, .92), r=.24, parent=t, periscope=True)
    # The search radar mast over the rear roof and the wide reflector turning on it (`Radar`).
    mast = a.part('Radar_mast', 'Steel', t)
    k.lathe(mast, [(.16, .92), (.16, .97), (.08, 1.05), (.07, 1.5)], loc=(0, 1.0, 0), seg=10, worn=(1,))
    for s in (-1, 1):
        mast.limb((s * .28, 1.2, .93), (0, 1.0, 1.35), .03, .03, bevel=0)
    r = a.pivot('Radar', (0, 1.0, 1.55), t)
    dish = a.part('Radar_dish', 'Armor', r)
    for i in range(6):
        u = (i - 2.5) / 2.5
        h = .56 * math.sqrt(1 - .45 * u * u)
        k.block(dish, (.25, .035, h), loc=(u * .62, .11 * u * u - .02, -h / 2 + .05),
                rot=(0, 0, -math.atan(.24 * u / .62 * 2.5)), chamfer=.008)
    a.part('Radar_feed', 'Steel', r).box((1.4, .04, .04), loc=(0, .1, -.26), bevel=0)
    a.part('Radar_feed', 'Steel', r).limb((0, .1, 0), (0, -.32, 0), .03, .03, bevel=0)
    a.part('Radar_feed', 'Steel', r).box((.1, .1, .1), loc=(0, -.35, 0), bevel=.01)
    a.part('Radar_drive', 'Armor', r).cyl(.12, .1, loc=(0, 0, -.04), seg=10, bevel=.01)
    # The twin Stinger box on its own pivot on the left rear roof (`Mount_missile`).
    mm = a.pivot('Mount_missile', (.48, .8, .94), t)
    a.part('Launcher_post', 'Steel', mm).cyl(.05, .26, loc=(0, 0, .13), seg=8, bevel=0)
    k.block(a.part('Launcher_box', 'Armor', mm), (.3, .85, .28), loc=(0, 0, .38), chamfer=.03)
    a.part('Launcher_covers', 'Undercarriage', mm).box((.24, .01, .2), loc=(0, -.43, .38), bevel=0)
    a.pivot('Muzzle_missile', (0, -.45, .38), mm)
    # Smoke dischargers on the rear cheeks (behind the gun housings), antennas, the team bands.
    for s in (-1, 1):
        K.smoke_dischargers(a, s * .86, .95, .72, s, count=4, parent=t)
        a.part('Team_band', 'Team', t).box((.01, .8, .08), loc=(s * .855, .6, .25), bevel=0)
        K.lamp(a, (s * .55, -.95, .82), (0, -1, 0), r=.045, parent=t, guard=False)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (-.55, 1.15, .92), h=.4)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.6, 1.25, .92), h=.3)
    a.part('Iff_antenna', 'Armor', t).box((.3, .06, .16), loc=(-.1, 1.38, .97), bevel=.01)
    if detail:
        K.rivet_line(a.part('Kit_rivets', 'Steel', t), (-.6, -.7, .91), (.6, -.7, .91), (0, 0, 1), pitch=.15,
                     r=.012)


def aa_vehicle(a, detail=False):
    """The self-propelled AA gun: see the module docstring."""
    GEP._hull(a)
    GEP._running_gear(a)
    _gepard_turret(a, detail)
    K.dust(a, (0, 0, .3), radius=3.0, k=.12)
    k.clean(a)


# ============================================================================= heavy_aa (Pantsir-S1 on the KamAZ 8x8)
PT = (0, 1.6, 1.3)      # turret pivot
PEL = (0, -.45, .72)    # trunnion (turret frame)
PGX, PGD = .74, .075    # gun pair axis |x|, half the spacing of a gun's two barrels
PTIP = -2.42            # barrel mouth y (Elevation frame)


def _2a38(a, el, s):
    """One twin-barrel 2A38M on side s (Elevation frame): the receiver housing on the turret cheek, two barrels side
    by side with their cooling jackets and flash hiders."""
    tag = '' if s > 0 else '_2'
    x = s * PGX
    rc = a.part('Gun_housing', 'Team', el)
    k.extrude(rc, [(-.6, -.14), (.5, -.14), (.58, 0), (.5, .16), (-.45, .16), (-.62, .04)], .3, loc=(x, 0, -.12),
              axis='X', chamfer=.02, corner=.02)
    a.part('Gun_feeds', 'Armor', el).box((.16, .4, .2), loc=(x + s * .02, .15, .1), bevel=0)
    for dx in (-PGD, PGD):
        bx = x + dx
        k.lathe(a.part(f'Main_cannon{tag}', 'Steel', el),
                [(.042, 0), (.042, .28), (.032, .32), (.03, 1.6), (0, 1.6)], loc=(bx, -.55, -.12), rot=K.FORWARD,
                seg=8)
        k.lathe(a.part(f'Main_cannon{tag}_jacket', 'Armor', el), [(.05, 0), (.05, .32)], loc=(bx, -.62, -.12),
                rot=K.FORWARD, seg=8)
        k.lathe(a.part(f'Muzzle_brake{tag}', 'Undercarriage', el),
                [(.034, 0), (.046, .03), (.046, .24), (0, .25)], loc=(bx, PTIP + .25, -.12), rot=K.FORWARD, seg=8)
    a.part('Gun_braces', 'Steel', el).box((PGD * 2 + .06, .04, .04), loc=(x, -1.3, -.12), bevel=0)


def _pantsir_pack(a, el, s):
    """The six-round 57E6 pack on side s outboard of the gun (Elevation frame): two columns of three tubes in a frame,
    the end caps, lifting eyes, the cable runs."""
    xc, y0, y1 = s * 1.15, -1.05, 1.25
    pack = a.part('Missile_pack', 'Team', el)
    K.chamfer_box(pack, (.5, y1 - y0, .76), loc=(xc, (y0 + y1) / 2, .2), c=.03)
    fr = a.part('Pack_frame', 'Armor', el)
    for y in (y0 + .06, (y0 + y1) / 2, y1 - .06):
        fr.box((.54, .06, .8), loc=(xc, y, .2), bevel=0)
    tubes = a.part('Pack_tubes', 'Undercarriage', el)
    for x in (xc - .12, xc + .12):
        for z in (-.04, .2, .44):
            tubes.cyl(.1, .05, loc=(x, y0 - .02, z), rot=K.FORWARD, seg=8, bevel=0)
    eyes = a.part('Kit_eyes', 'Steel', el)
    for y in (y0 + .4, y1 - .4):
        eyes.box((.06, .1, .06), loc=(xc, y, .61), bevel=0)
    a.part('Kit_cables', 'Rubber', el).tube([(xc - s * .25, y1 - .1, .1), (s * .8, y1 - .1, .1)], .025, seg=4)
    a.part('Pack_arms', 'Steel', el).box((.3, .3, .16), loc=(s * .77, .1, .35), bevel=0)   # pack to trunnion


def _pantsir_turret(a):
    t = a.pivot('Turret', PT)
    k.lathe(a.part('Turret_steel', 'Steel', t), [(.82, 0), (.86, .02), (.86, .1), (.8, .12)], seg=16)
    body = a.part('Turret_body', 'Team', t)
    k.sharp_loft(body, [[(-.52, -1.25, .12), (.52, -1.25, .12), (.58, 1.1, .12), (-.58, 1.1, .12)],
                        [(-.58, -1.4, .55), (.58, -1.4, .55), (.6, 1.15, .55), (-.6, 1.15, .55)],
                        [(-.45, -1.15, .95), (.45, -1.15, .95), (.5, 1.05, .98), (-.5, 1.05, .98)]], chamfer=.04)
    arm = a.part('Turret_armor', 'Armor', t)
    for s in (-1, 1):
        K.chamfer_box(arm, (.03, 1.2, .5), loc=(s * .6, .45, .55), c=.01)
    # Guns and packs on the trunnion.
    el = a.pivot('Elevation', PEL, t)
    a.part('Trunnions', 'Steel', el).cyl(.11, 1.25, loc=(0, 0, 0), rot=(0, R90, 0), seg=10, bevel=0)
    for s in (1, -1):
        _2a38(a, el, s)
        _pantsir_pack(a, el, s)
    m = a.pivot('Muzzle_main', (0, PTIP, -.12), el)
    # Firing order left, right, left, right (Main_cannon / Main_cannon_2 recoil in turn with it).
    _barrel_muzzles(a, m, (PGX + PGD, -PGX - PGD, PGX - PGD, -PGX + PGD))
    for i, x in enumerate((1.27, 1.03, -1.03, -1.27)):
        a.pivot('Muzzle_missile' + ('' if i == 0 else f'__{i:03d}'), (x, -1.1, .2), el)
    # The tracking array in the turret's face (the round 1RS2 antenna in its frame), the EO sight under it.
    trk = a.part('Radar_tracker', 'Armor', t)
    k.lathe(trk, [(0, -.06), (.3, -.05), (.34, .03), (.34, .1)], loc=(0, -1.35, .62), rot=K.FORWARD, seg=16,
            worn=(2,))
    a.part('Radar_tracker_face', 'Undercarriage', t).cyl(.28, .02, loc=(0, -1.46, .62), rot=K.FORWARD, seg=16,
                                                         bevel=0)
    grid = a.part('Radar_tracker_grid', 'Steel', t)
    for z in (-.14, 0, .14):
        grid.box((.5 * math.sqrt(1 - (z / .28) ** 2), .01, .015), loc=(0, -1.475, .62 + z), bevel=0)
    K.chamfer_box(a.part('Sight', 'Armor', t), (.3, .3, .22), loc=(0, -1.25, .2), c=.03)
    a.part('Glass', 'Glass', t).box((.2, .01, .12), loc=(0, -1.405, .21), bevel=0)
    # The search radar on its post at the rear (Radar spins it).
    a.part('Search_post', 'Steel', t).cyl(.14, .06, loc=(0, .5, .98), seg=8, bevel=0)
    r = a.pivot('Radar', (0, .5, 1.0), t)
    K.chamfer_box(a.part('Search_drive', 'Armor', r), (.3, .3, .16), loc=(0, 0, .09), c=.03)
    k.block(a.part('Radar_search', 'Team', r), (1.15, .1, .6), loc=(0, .12, .45), rot=(-.25, 0, 0), chamfer=.02)
    a.part('Search_array', 'MetalSheet', r).box((1.05, .02, .5), loc=(0, .05, .45), rot=(-.25, 0, 0), bevel=0)
    for s in (-1, 1):
        a.part('Search_braces', 'Steel', r).limb((s * .12, 0, .12), (s * .5, .18, .3), .04, .04, bevel=0)
    # Roof: hatch, the IFF and the communication whips, the air conditioner, the team panel.
    C.hatch(a, (.25, .45, .97), r=.2, parent=t, periscope=False)
    a.part('Ac_units', 'Armor', t).box((.4, .35, .16), loc=(-.25, -.5, 1.03), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (.4, 1.0, .97), h=.5)
    a.part('Team_band', 'Team', t).box((.9, .4, .012), loc=(0, -.2, .975), bevel=0)


def heavy_aa(a, detail=False):
    """The gun-missile air defence vehicle: see the module docstring."""
    R, WD, HX = .55, .4, .93
    TR._wheels(a, (-3.95, -2.65, 1.45, 2.7), R, WD, HX, nuts=0, springs=False, diff_rear=False)
    TR._rails(a, -4.6, 4.7, .95, .5, cross=(-4.2, -3.3, -1.5, .2, 2.1, 4.4))
    for y0, y1 in ((-4.55, -2.05), (.85, 3.3)):
        TR._fender(a, y0, y1, HX, 1.22, w=.46)
    for s in (-1, 1):
        for y in (-3.3, 2.07):
            a.part('Suspension', 'Steel').box((.1, 1.3, .14), loc=(s * (HX - .32), y, .78), bevel=0)
        a.part('Mud_flaps', 'Rubber').box((.42, .02, .4), loc=(s * HX, 3.33, .92), bevel=0)
        a.part('Tail_lamps', 'LavaGlow').box((.12, .02, .07), loc=(s * .95, 4.85, 1.05), bevel=0)
        K.outrigger(a.part('Outriggers', 'Armor'), a.part('Outrigger_pads', 'Steel'), (s * .75, 4.45, 1.0), s,
                    reach=.25, drop=.62, w=.16)
    TR._pantsir_cab(a)
    TR._pantsir_body(a)
    _pantsir_turret(a)
    a.pivot('Point_fire', (0, -2.1, 2.2))
    a.pivot('Point_exhaust', (.85, -3.1, 2.25))
    k.clean(a)


# ============================================================================= hangars: shared fittings
# Wave M4's hangars scored 58-82 (too few parts for an 8 x 8 m building under the 6,000-triangle tower cap); they are
# not seen in numbers, so wave M6 lets them carry ~9-12k triangles of real fittings (DECISIONS "Play-test 14 model wave
# M6 (lane A)"). Each keeps its M4 footprint and proportions (modelSize unchanged); the three read apart at a glance:
# the drone post (containers, launch rails, drone racks), the motor-pool shed (a full-width roller door over a ramp),
# the helicopter shelter (the fabric arch behind its helipad apron).
import mb_pt14_m4 as M4  # noqa: E402

_pad = M4._pad
_fpv = M4._fpv


def _wall_kit(a, name, mat, axis, plane, out, u0, u1, z0, z1, n, seed, size=(.12, .4), depth=(.06, .16)):
    """n small boxes of varied size (junction boxes, placards, valve boxes) on a wall: the wall is the plane
    `axis` = `plane` ('x' or 'y'), its outward side `out` (+1 / -1); u runs along the wall, z up it."""
    rng = random.Random(seed)
    part = a.part(name, mat)
    q = lambda lo, hi: round(rng.uniform(lo, hi) / .02) * .02 or .02   # noqa: E731
    placed = []
    tries = 0
    while len(placed) < n and tries < n * 40:
        tries += 1
        w, h, d = q(*size), q(*size), q(*depth)
        u, z = rng.uniform(u0 + w / 2, u1 - w / 2), rng.uniform(z0 + h / 2, z1 - h / 2)
        if any(abs(u - pu) < (w + pw) / 2 + .06 and abs(z - pz) < (h + ph) / 2 + .06 for pu, pz, pw, ph in placed):
            continue
        placed.append((u, z, w, h))
        c = plane + out * (d / 2 + .01)
        if axis == 'x':
            part.box((d, w, h), loc=(c, u, z), bevel=0)
        else:
            part.box((w, d, h), loc=(u, c, z), bevel=0)
    return placed


def _bollards(a, points, h=1.0, r=.09):
    """Steel bollards (yellow, two black bands) at the points on the ground."""
    bp = a.part('Bollards', 'CraneYellow')
    bb = a.part('Bollard_bands', 'EliteBlack')
    for x, y, z in points:
        k.lathe(bp, [(r, 0), (r, h - .04), (r * .7, h), (0, h)], loc=(x, y, z), seg=8)
        for f in (.55, .8):
            bb.cyl(r + .008, .08, loc=(x, y, z + h * f), seg=8, bevel=0)


def _guyed_mast(a, loc, h, guys=3, r=.04, name='Antennas', yaw=0.0):
    """A tubular antenna mast with its guy wires and their ground anchors."""
    x, y, z = loc
    m = a.part(name, 'Steel')
    m.cyl(r, h, loc=(x, y, z + h / 2), seg=6, bevel=0)
    g = a.part('Kit_guys', 'Steel')
    for i in range(guys):
        u = yaw + i * TAU / guys
        fx, fy = x + math.cos(u) * h * .38, y + math.sin(u) * h * .38
        g.tube([(x, y, z + h * .8), (fx, fy, z + .02)], .008, seg=3, caps=False)
        g.box((.1, .1, .05), loc=(fx, fy, z + .025), bevel=0)


def _downpipe(a, x, y, z0, z1, out):
    """A rain downpipe with its brackets and the shoe at the foot (out: the wall's outward x sign)."""
    p = a.part('Downpipes', 'Steel')
    p.cyl(.05, z1 - z0, loc=(x, y, (z0 + z1) / 2), seg=6, bevel=0)
    p.box((.12, .14, .08), loc=(x, y, z0 + .04), bevel=0)
    br = a.part('Kit_brackets', 'Steel')
    for z in (z0 + .8, (z0 + z1) / 2 + .3, z1 - .4):
        br.box((.1, .03, .03), loc=(x - out * .05, y, z), bevel=0)


# ============================================================================= drone hangar family
CW, CL, CH = M4.CW, M4.CL, M4.CH
CX, CY, AP, DK, DKT = M4.CX, M4.CY, M4.AP, M4.DK, M4.DKT
CY0, CY1 = M4.CY0, M4.CY1
DE = CX + CW / 2        # deck half width


def _container_open(a, x):
    """The +X container with its end doors swung open: the shell drawn as walls (roof, floor, sides, back) so its
    inside shows, the two leaves standing open at 90 degrees, the drone racks inside (shelves of drone cases, a rack
    of FPVs ready to fly, the charging shelf with its leads)."""
    zc = AP + CH / 2
    sh = a.part('Walls', 'Corrugated')
    t = .06
    sh.box((CW, CL, t), loc=(x, CY, AP + CH - t / 2), bevel=0)                          # roof
    for s in (-1, 1):
        sh.box((t, CL, CH - t), loc=(x + s * (CW / 2 - t / 2), CY, AP + (CH - t) / 2), bevel=0)
    sh.box((CW - 2 * t, t, CH - t), loc=(x, CY1 - t / 2, AP + (CH - t) / 2), bevel=0)
    a.part('Container_floor', 'Wood').box((CW - 2 * t, CL - t, .04), loc=(x, CY, AP + .02), bevel=0)
    a.part('Interior', 'Undercarriage').box((CW - .2, .02, CH - .3), loc=(x, CY1 - .1, AP + CH / 2), bevel=0)
    rb = a.part('Wall_ribs', 'Corrugated')
    for i in range(16):
        y = CY0 + .3 + i * (CL - .6) / 15
        rb.box((.05, .1, CH - .2), loc=(x + (CW / 2 + .02), y, zc), bevel=0)
    cc = a.part('Corner_castings', 'Steel')
    fr = a.part('Door_frames', 'Steel')
    for sx in (-1, 1):
        for y in (CY0, CY1):
            for z in (AP + .06, AP + CH - .06):
                cc.box((.18, .18, .12), loc=(x + sx * (CW / 2 - .07), y, z), bevel=0)
        fr.box((.1, .12, CH - .24), loc=(x + sx * (CW / 2 - .05), CY0 + .03, zc), bevel=0)
    fr.box((CW, .12, .14), loc=(x, CY0 + .03, AP + CH - .14), bevel=0)
    fr.box((CW, .12, .1), loc=(x, CY0 + .03, AP + .09), bevel=0)
    # The leaves open at 90 degrees, their locking bars.
    dr = a.part('Doors', 'Corrugated')
    bars = a.part('Kit_bars', 'Steel')
    for sx in (-1, 1):
        hx = x + sx * (CW / 2 + .03)
        dr.box((.05, CW / 2 - .08, CH - .3), loc=(hx, CY0 - CW / 4 - .02, zc), bevel=0)
        for f in (.3, .7):
            bars.box((.05, .035, CH - .35), loc=(hx + sx * .045, CY0 - f * CW / 2, zc), bevel=0)
        a.part('Door_ribs', 'MetalSheet').box((.02, CW / 2 - .2, .06), loc=(hx - sx * .035, CY0 - CW / 4, zc + .7),
                                             bevel=0)
    # Inside: steel shelving down both walls, varied drone cases on it, the charging shelf at the back.
    rk = a.part('Racks', 'Steel')
    for s in (-1, 1):
        rx = x + s * (CW / 2 - .35)
        for z in (.55, 1.15, 1.75):
            rk.box((.5, 3.4, .03), loc=(rx, CY0 + 2.1, AP + z), bevel=0)
        for y in (CY0 + .45, CY0 + 2.1, CY0 + 3.75):
            for dx in (-.22, .22):
                rk.box((.035, .035, 2.0), loc=(rx + dx, y, AP + 1.0), bevel=0)
        for z in (.585, 1.185, 1.785):
            K.clutter(a, 'Drone_boxes', 'Crate' if s > 0 else 'Team', rx - .22, rx + .22, CY0 + .5, CY0 + 3.7,
                      AP + z, 5, seed=int(z * 100) + s * 7, size=(.18, .42), height=(.12, .34), gap=.05)
    # The FPV rack across the doorway: two shelves of quadcopters ready to fly.
    dk = a.part('Drone_rack', 'Steel')
    for z in (.9, 1.4):
        dk.box((1.3, .4, .03), loc=(x, CY0 + .7, AP + z), bevel=0)
    for dx in (-.63, .63):
        dk.box((.035, .4, 1.4), loc=(x + dx, CY0 + .7, AP + .7), bevel=0)
    for j, dx in enumerate((-.4, 0, .4)):
        _fpv(a, (x + dx, CY0 + .7, AP + .96), yaw=.2 * j, scale=.85)
        _fpv(a, (x + dx, CY0 + .7, AP + 1.46), yaw=-.2 * j, scale=.85)
    bt = a.part('Batteries', 'EliteBlack')
    for i in range(6):
        bt.box((.14, .1, .07 + (i % 3) * .015), loc=(x - .55 + i * .22, CY0 + 3.85, AP + 1.22), bevel=0)
    a.part('Kit_cables', 'Rubber').tube([(x - .6, CY0 + 3.8, AP + 1.3), (x, CY0 + 3.6, AP + 1.6),
                                         (x + .6, CY0 + 3.8, AP + 1.3)], .015, seg=3)
    a.part('Team_band', 'Team').box((.02, CL - .5, .3), loc=(x + (CW / 2 + .05), CY, AP + CH - .45), bevel=0)


def _container_side_kit(a, x):
    """Fittings on a container's outer side: the vents, the CSC plate, lashing eyes, the fork pockets."""
    s = 1 if x > 0 else -1
    wx = x + s * CW / 2 + s * .08
    vn = a.part('Container_vents', 'Steel')
    for y in (CY0 + .5, CY1 - .5):
        vn.box((.04, .22, .1), loc=(wx, y, AP + CH - .3), bevel=0)
    a.part('Csc_plate', 'PlasterWhite').box((.02, .3, .2), loc=(wx + s * .01, CY1 - 1.0, AP + 1.4), bevel=0)
    ey = a.part('Kit_eyes', 'Steel')
    for y in (CY0 + 1.5, CY + .3, CY1 - 1.6):
        ey.box((.05, .08, .08), loc=(wx, y, AP + .35), bevel=0)
    for y in (CY - 1.0, CY + 1.0):
        a.part('Fork_pockets', 'Undercarriage').box((.03, .36, .1), loc=(wx - s * .05, y, AP + .1), bevel=0)


def _drone_post(a):
    """The drone operations post (wave M4's layout, more fitted): apron, the closed -X container and the open +X
    container with its racks, the bay with the roller door between them, the roof deck under the anti-drone net, the
    ground control station, the guyed antenna mast and the satcom dish, the generator with its fuel bladder, the FPV
    launch table on the apron."""
    base = a.part('Base', 'Concrete')
    _pad(base, (7.6, CL + .4, AP), loc=(0, CY, AP / 2), chamfer=.02, taper=(.94, .92))
    k.extrude(base, [(-3.0, -3.95), (3.0, -3.95), (3.6, -3.4), (3.6, CY0 - .1), (-3.6, CY0 - .1), (-3.6, -3.4)], AP,
              loc=(0, 0, AP / 2), axis='Z', chamfer=.02)
    jt = a.part('Base_joints', 'Undercarriage')
    jt.box((7.0, .03, .01), loc=(0, -3.2, AP + .002), bevel=0)
    for x in (-1.6, 1.6):
        jt.box((.03, 1.3, .01), loc=(x, -3.3, AP + .002), bevel=0)
    M4._container(a, -CX)
    _container_open(a, CX)
    for x in (-CX, CX):
        _container_side_kit(a, x)
    # The bay between them: back wall, a dark interior, the roller door half up under its drum.
    bay = a.part('Bay_walls', 'Corrugated')
    bay.box((2.4, .08, CH), loc=(0, CY1 - .05, AP + CH / 2), bevel=0)
    a.part('Interior', 'Undercarriage').box((2.36, .02, 1.5), loc=(0, CY0 + 1.4, AP + .76), bevel=0)
    k.block(a.part('Door_drum', 'Steel'), (2.5, .42, .42), loc=(0, CY0 - .12, DK - .22), chamfer=.03)
    a.part('Door_motor', 'Armor').box((.22, .3, .3), loc=(.9, CY0 - .2, DK - .62), bevel=0)
    sl = a.part('Door_slats', 'MetalSheet')
    for i in range(5):
        sl.box((2.36, .04, .18), loc=(0, CY0 + .02, DK - .53 - i * .19), bevel=0)
    a.part('Door_bottom', 'Steel').box((2.38, .06, .06), loc=(0, CY0 + .02, DK - .53 - 4.5 * .19), bevel=0)
    gd = a.part('Door_guides', 'Steel')
    for sx in (-1, 1):
        gd.box((.08, .1, CH - .1), loc=(sx * 1.2, CY0 + .02, AP + CH / 2), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((2.4, .02, .1), loc=(0, CY0 - .02, AP + .06), bevel=0)
    rk = a.part('Racks', 'Steel')
    for x in (-.8, .8):
        rk.box((.5, .4, 1.3), loc=(x, CY0 + 1.2, AP + .65), bevel=0)
    for x in (-.8, .8):
        for z in (.45, .8, 1.15):
            a.part('Drone_boxes', 'Crate').box((.44, .36, .2), loc=(x, CY0 + 1.0, AP + z), bevel=0)
    # The roof deck, its non-slip mats, the parapet bags, the railing and the stair-ladder.
    _pad(a.part('Roof_deck', 'Armor'), (2 * DE + .1, CL + .1, .14), loc=(0, CY, DK + .07), chamfer=.02)
    mats = a.part('Deck_mats', 'Rubber')
    for x, y in ((-1.5, CY0 + 1.3), (1.6, CY0 + 1.0), (0, CY + 1.9)):
        mats.box((1.6, 1.1, .015), loc=(x, y, DKT + .008), bevel=0)
    # The sandbag parapet along the deck's front edge, open in front of the launcher.
    W.bags(a, [(DE - .3, CY0 + .3, DKT), (-.2, CY0 + .3, DKT)], layers=2, bag=(.5, .28, .15), seed=85,
           name='Parapet')
    W.bags(a, [(-2.5, CY0 + .3, DKT), (-DE + .3, CY0 + .3, DKT)], layers=2, bag=(.5, .28, .15), seed=86,
           name='Parapet')
    f0, f1 = CY0, CY1
    K.railing(a.part('Railings', 'Steel'), [(DE - .7, f1, DKT), (DE, f1, DKT), (DE, f0, DKT), (-DE, f0, DKT),
                                            (-DE, f1, DKT), (DE - 1.3, f1, DKT)], h=.95, post=1.2, r=.02)
    a.part('Kick_plates', 'Hazard').box((2 * DE, .02, .1), loc=(0, f0 - .01, DKT + .05), bevel=0)
    K.ladder(a.part('Ladders', 'Steel'), (DE - 1.0, f1 + .5, AP), (DE - 1.0, f1 + .05, DKT + .9), width=.5, step=.3,
             r=.02)
    # The anti-drone net over the deck's rear half on six poles.
    K.camo_net(a, [(-DE + .1, .2, 1.95), (DE - .1, .2, 1.95), (-DE + .1, f1 - .1, 1.75), (DE - .1, f1 - .1, 1.75),
                   (0, .2, 2.0), (0, f1 - .1, 1.8)], .12, DKT, part='Roof_net', garnish=10, seed=81)
    # The ground control station under the net: the radio box, the console with two screens, the operators' seats.
    k.block(a.part('Radio_box', 'Armor'), (.8, .5, .7), loc=(-1.6, 2.0, DKT + .35), chamfer=.03)
    a.part('Glass', 'Glass').box((.5, .02, .3), loc=(-1.6, 1.74, DKT + .5), bevel=0)
    k.block(a.part('Console', 'EliteBlack'), (1.4, .5, .08), loc=(-1.0, 1.1, DKT + .75), chamfer=.01)
    for dx in (-.35, .35):
        a.part('Screens', 'Glass').box((.5, .03, .32), loc=(-1.0 + dx, 1.3, DKT + 1.0), rot=(.2, 0, 0), bevel=0)
        a.part('Screen_backs', 'EliteBlack').box((.54, .04, .36), loc=(-1.0 + dx, 1.33, DKT + 1.0), rot=(.2, 0, 0),
                                                 bevel=0)
    lg = a.part('Bench_legs', 'Steel')
    for dx in (-.6, .6):
        lg.box((.05, .45, .75), loc=(-1.0 + dx, 1.1, DKT + .37), bevel=0)
    seat = a.part('Seats', 'Canvas')
    for dx in (-.35, .35):
        seat.box((.4, .4, .06), loc=(-1.0 + dx, .55, DKT + .45), bevel=0)
        seat.box((.4, .05, .4), loc=(-1.0 + dx, .37, DKT + .7), bevel=0)
        a.part('Seat_legs', 'Steel').cyl(.03, .42, loc=(-1.0 + dx, .55, DKT + .21), seg=5, bevel=0)
    k.block(a.part('Workbench', 'Wood'), (1.6, .6, .08), loc=(1.4, 2.4, DKT + .8), chamfer=.01)
    for dx in (-.7, .7):
        lg.box((.05, .5, .8), loc=(1.4 + dx, 2.4, DKT + .4), bevel=0)
    bt = a.part('Batteries', 'EliteBlack')
    for i in range(4):
        bt.box((.22, .15, .12), loc=(.9 + i * .32, 2.4, DKT + .9), bevel=0)
    _fpv(a, (1.7, 2.35, DKT + .92), yaw=.6)
    K.clutter(a, 'Bench_parts', 'Steel', .7, 2.1, 2.2, 2.6, DKT + .84, 5, seed=92, size=(.06, .18), height=(.03, .1),
              gap=.03)
    # The guyed antenna mast at the rear left corner (panel antennas, an omni, a beacon), the satcom dish, the whip.
    mx, my = DE - .25, f1 - .25
    a.part('Antennas', 'Steel').cyl(.045, 2.1, loc=(mx, my, DKT + 1.05), seg=6, bevel=0)
    g = a.part('Kit_guys', 'Steel')
    for gx, gy in ((mx - 1.0, my), (mx, my - 1.1)):
        g.tube([(mx, my, DKT + 1.8), (gx, gy, DKT + .02)], .008, seg=3, caps=False)
    for u in (0, 2.1, 4.2):
        K.mesh_antenna(a.part('Antennas', 'Steel'), (mx + math.sin(u) * .14, my - math.cos(u) * .14, DKT + 1.75),
                       w=.28, h=.42, normal=(math.sin(u), -math.cos(u), 0), bars=3)
    a.part('Omni_antenna', 'PlasterWhite').cyl(.03, .4, loc=(mx, my, DKT + 2.3), seg=6, bevel=0)
    K.beacon(a, (mx, my, DKT + 2.53), r=.05)
    K.dish(a.part('Satcom_dish', 'PlasterWhite'), a.part('Satcom_feed', 'Steel'), (-DE + .6, f1 - .6, DKT + .9),
           r=.42, normal=(.3, -.5, .8), seg=12)
    a.part('Satcom_post', 'Steel').cyl(.05, .8, loc=(-DE + .6, f1 - .6, DKT + .4), seg=6, bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel'), (-DE + .3, f1 - .3, DKT), h=1.8, r=.018)
    # The EO / thermal camera mast at the deck's front left: the post, the pan-tilt head.
    a.part('Camera_post', 'Steel').cyl(.04, 1.4, loc=(-DE + .25, f0 + .25, DKT + .7), seg=6, bevel=0)
    K.chamfer_box(a.part('Camera_head', 'EliteBlack'), (.2, .24, .18), loc=(-DE + .25, f0 + .2, DKT + 1.5), c=.03)
    a.part('Glass', 'Glass').cyl(.05, .02, loc=(-DE + .25, f0 + .075, DKT + 1.52), rot=K.FORWARD, seg=8, bevel=0)
    # Generator behind the bay on the apron, its fuel bladder and the cable run up to the deck.
    gx, gy = -1.2, CY1 + .25
    k.block(a.part('Generator', 'Armor'), (1.1, .42, .7), loc=(gx, gy, AP + .35), chamfer=.03)
    K.grille(a, (gx - .2, gy + .215, AP + .4), .5, .4, facing=(0, 1, 0), slats=4)
    K.exhaust(a, (gx + .4, gy, AP + .7), r=.035, length=.35)
    K.soot(a, (gx + .4, gy, AP + 1.05), radius=.25, k=.4)
    a.part('Kit_cables', 'Rubber').tube([(gx - .5, gy, AP + .5), (-2.0, gy - .05, AP + .9), (-2.4, gy - .2, DKT)],
                                        .022, seg=4)
    k.lathe(a.part('Fuel_bladder', 'Fuel'), [(.0, .0), (.3, .02), (.36, .12), (.3, .22), (0, .24)],
            loc=(.6, gy, AP), seg=10)
    # Apron, front: the FPV launch table with a quadcopter on it, sandbag wings, jerrycans, a crate, bollards.
    lt = a.part('Launch_table', 'Steel')
    tx, ty = -2.3, -3.35
    lt.box((.9, .7, .04), loc=(tx, ty, AP + .7), bevel=0)
    for dx in (-.4, .4):
        for dy in (-.3, .3):
            lt.box((.035, .035, .7), loc=(tx + dx, ty + dy, AP + .35), bevel=0)
    a.part('Launch_mat', 'Hazard').box((.6, .5, .01), loc=(tx, ty, AP + .725), bevel=0)
    _fpv(a, (tx, ty, AP + .78), yaw=.3)
    W.bags(a, [(-3.4, -3.0, AP), (-3.4, -3.7, AP)], layers=2, bag=(.52, .3, .15), seed=83)
    W.bags(a, [(3.4, -3.0, AP + 0), (3.4, -3.7, AP)], layers=2, bag=(.52, .3, .15), seed=84)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (1.0, -3.6, AP), rot=(0, 0, .2))
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (.7, -3.65, AP), rot=(0, 0, -.1))
    K.crate(a.part('Crates', 'Crate'), a.part('Kit_straps', 'Steel'), (.6, .4, .4), (-.9, -3.55, AP),
            rot=(0, 0, .2))
    K.lamp(a, (1.0, CY0 - .02, DK - .5), facing=(0, -1, -.4), r=.07, guard=True)
    K.lamp(a, (-1.0, CY0 - .02, DK - .5), facing=(0, -1, -.4), r=.07, guard=True)
    W.stack(a, (-.3, -3.35, AP), n=3, size=(.5, .3, .2), yaw=.1, seed=87)
    C.cable_reel(a, (1.75, -3.55, AP + .25), r=.24, w=.32)
    dr = a.part('Drums', 'BarrelRed')
    bd = a.part('Drum_bands', 'Steel')
    for x in (.0, .62):
        K.fuel_drum(dr, bd, (x + 1.3, CY1 + .32, AP), r=.25, h=.8)
    _bollards(a, [(-1.35, CY0 - .25, AP), (1.35, CY0 - .25, AP)], h=.8, r=.07)
    # Deck cases under the net, deck fittings, container bolts, side spares and cable reels, rear wall boxes.
    K.clutter(a, 'Cases', 'Team', -3.4, -.4, 2.6, 3.4, DKT, 4, seed=86, size=(.25, .6), height=(.15, .45))
    K.clutter(a, 'Deck_fittings', 'Steel', -3.3, 3.3, -.4, .9, DKT, 6, seed=89, size=(.1, .3), height=(.05, .25))
    bl = a.part('Kit_bolts', 'Steel')
    for y in (CY0 + .6, CY0 + 2.0, CY0 + 3.4, CY0 + 4.8):
        for z in (AP + .5, AP + 1.4, AP + 2.2):
            bl.box((.06, .04, .06), loc=(-CX - (CW / 2 + .045), y, z), bevel=0)
    K.clutter(a, 'Spares', 'Crate', DE + .06, DE + .3, -2.2, 1.2, AP, 4, seed=87, size=(.2, .25), height=(.2, .6))
    K.clutter(a, 'Cable_reels', 'Undercarriage', -DE - .3, -DE - .06, -2.0, 2.4, AP, 4, seed=88, size=(.2, .25),
              height=(.2, .5))
    _wall_kit(a, 'Wall_boxes', 'Armor', 'y', CY1, 1, -1.1, 1.1, AP + .4, AP + 2.3, 5, seed=93)
    for x, y in ((3.5, -3.6), (-3.5, -3.6), (3.5, 3.6), (-3.5, 3.6)):
        K.dust(a, (x, y, 0), radius=1.6, k=.25)


def _launch_points(a, p):
    a.pivot('Muzzle_main', p)
    a.pivot('Muzzle_door_l', p)


def _fpv_rails(a, x, y0, y1, z0, n=3, pitch=.42):
    """A trestle of n parallel FPV launch rails, raised 20 degrees, with an FPV on each sled; returns the mouth of
    the middle rail."""
    rail = a.part('Launch_rail', 'Steel')
    ang = .35
    z1 = z0 + (y0 - y1) * math.tan(ang)
    for i in range(n):
        rx = x + (i - (n - 1) / 2) * pitch
        for s_ in (-1, 1):
            rail.tube([(rx + s_ * .1, y0, z0), (rx + s_ * .1, y1, z1)], .022, seg=4)
        for t in (.12, .5, .88):
            rail.box((.26, .035, .035), loc=(rx, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t - .01), bevel=0)
        _fpv(a, (rx, y0 + (y1 - y0) * .55, z0 + (z1 - z0) * .55 + .06), yaw=R90 + .1 * i, scale=.9)
        a.part('Rail_stops', 'Hazard').box((.24, .04, .06), loc=(rx, y0 + .02, z0 + .02), bevel=0)
    w = (n - 1) * pitch / 2 + .25
    tr = a.part('Trestle', 'Steel')
    for yy, zz in ((y0 - .05, z0), (y1 + .25, z1 - .09)):
        for s_ in (-1, 1):
            tr.limb((x + s_ * (w + .1), yy, DKT), (x + s_ * w, yy, zz - .03), .04, .04, bevel=0)
        tr.box((2 * w + .1, .05, .05), loc=(x, yy, zz - .04), bevel=0)
    return (x, y1 - .1, z1 + .05)


def drone_hangar(a, detail=False):
    """The drone hangar (fpv_hangar): the post with a trestle of three FPV launch rails at the deck's front."""
    _drone_post(a)
    p = _fpv_rails(a, -1.3, CY0 + 2.3, CY0 + .45, DKT + .42, n=3)
    _fpv(a, (1.2, 1.9, DKT + .9), yaw=.4)
    K.clutter(a, 'Drone_cases', 'Crate', .1, 1.6, -1.6, -.5, DKT, 5, seed=90, size=(.2, .45), height=(.1, .3))
    K.clutter(a, 'Rail_spares', 'Steel', 1.9, 3.2, -1.8, -.6, DKT, 5, seed=91, size=(.08, .3), height=(.05, .2))
    _launch_points(a, p)
    k.clean(a)


def _lancet(a, p, d, rot):
    """A Lancet on the catapult shuttle at p along d: the body, the nose, the two X wing sets."""
    from mathutils import Matrix
    body = a.part('Drones', 'Armor')
    body.cyl(.07, 1.3, loc=tuple(p), rot=rot, seg=8, bevel=0)
    a.part('Drone_boxes', 'Undercarriage').cyl(.07, .12, loc=tuple(p + d * .7), rot=rot, seg=8, r2=.02, bevel=0)
    wings = a.part('Drone_arms', 'Steel')
    for off, span in ((.35, .5), (-.45, .4)):
        c = p + d * off
        for u in (.785, 2.356):
            m = Matrix.Translation(c) @ Matrix.Rotation(-math.atan2(d.z, -d.y), 4, 'X') @ Matrix.Rotation(u, 4, 'Y')
            wings.box((span * 2, .2, .015), loc=tuple(c), rot=m.to_euler('XYZ'), bevel=0)


def drone_hangar_a(a, detail=False):
    """drone_hangar_a (lancet_hangar): the post with the Lancet pneumatic catapult and the Lancet canisters."""
    _drone_post(a)
    rail = a.part('Launch_rail', 'Steel')
    x = -1.3
    y0, y1 = CY + 1.6, CY0 + .2
    z0, z1 = DKT + .35, DKT + .35 + (y0 - y1) * math.tan(.26)
    for s_ in (-1, 1):
        rail.tube([(x + s_ * .14, y0, z0), (x + s_ * .14, y1, z1)], .03, seg=4)
        rail.tube([(x + s_ * .1, y0, z0 - .22), (x + s_ * .1, y1, z1 - .22)], .02, seg=4)
    n = 7
    for i in range(n + 1):
        t = i / n
        yy, zz = y0 + (y1 - y0) * t, z0 + (z1 - z0) * t
        rail.limb((x - .12, yy, zz), (x + .1, yy + .25, zz - .22 + .06), .02, .02, bevel=0)
        rail.box((.3, .03, .03), loc=(x, yy, zz - .11), bevel=0)
    tr = a.part('Trestle', 'Steel')
    for t, h in ((.15, z0 - .2), (.75, z0 + (z1 - z0) * .75 - .2)):
        yy = y0 + (y1 - y0) * t
        for s_ in (-1, 1):
            tr.limb((x + s_ * .4, yy, DKT), (x + s_ * .12, yy, h), .05, .05, bevel=0)
    k.lathe(a.part('Air_bottles', 'Hazard'), [(.16, 0), (.16, 1.1), (.08, 1.2), (0, 1.22)],
            loc=(x + .55, y0 - .3, DKT + .2), rot=(R90, 0, 0), seg=10)
    k.block(a.part('Compressor', 'Armor'), (.5, .6, .45), loc=(x + .65, y0 + .2, DKT + .22), chamfer=.02)
    K.grille(a, (x + .91, y0 + .2, DKT + .25), .4, .3, facing=(1, 0, 0), slats=3)
    a.part('Kit_cables', 'Rubber').tube([(x + .5, y0 + .1, DKT + .3), (x + .1, y0, z0 - .1)], .02, seg=4)
    t = .35
    p = Vector((x, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t + .12))
    d = Vector((0, y1 - y0, z1 - z0)).normalized()
    _lancet(a, p, d, K.rot_to(tuple(-d)))
    # The Lancet canisters (transport tubes) racked on the deck's right front on their stand.
    cr = a.part('Canisters', 'Team')
    caps = a.part('Canister_caps', 'Undercarriage')
    for i in range(3):
        for j in range(2):
            cx, cz = 1.1 + i * .36, DKT + .25 + j * .32
            cr.cyl(.15, 1.5, loc=(cx, -1.3, cz), rot=K.FORWARD, seg=10, bevel=0)
            caps.cyl(.12, .02, loc=(cx, -2.06, cz), rot=K.FORWARD, seg=8, bevel=0)
    stand = a.part('Canister_stand', 'Steel')
    for y in (-1.85, -.75):
        stand.box((1.2, .08, .1), loc=(1.46, y, DKT + .05), bevel=0)
    K.clutter(a, 'Drone_cases', 'Crate', 1.0, 3.2, .0, .9, DKT, 4, seed=95, size=(.2, .45), height=(.1, .3))
    _launch_points(a, (x, y1 - .1, z1 + .05))
    k.clean(a)


def drone_hangar_b(a, detail=False):
    """drone_hangar_b (fpv_hangar_swarm): the post with nine swarm launch cells (lids open, FPVs inside) and the
    battery charging racks."""
    _drone_post(a)
    cells = a.part('Launch_rail', 'Steel')
    lids = a.part('Cell_lids', 'Armor')
    x0, y0 = -2.6, CY0 + .45
    for i in range(3):
        for j in range(3):
            cx, cy = x0 + j * .62, y0 + .2 + i * .58
            cells.box((.56, .5, .32), loc=(cx, cy, DKT + .16), bevel=0)
            a.part('Cell_bores', 'Undercarriage').box((.46, .4, .01), loc=(cx, cy, DKT + .325), bevel=0)
            lids.box((.5, .03, .44), loc=(cx, cy + .27, DKT + .5), rot=(-.25, 0, 0), bevel=0)
            _fpv(a, (cx, cy, DKT + .28), yaw=.3 * i + .2 * j, scale=.9)
    k.block(a.part('Control_cabinet', 'Armor'), (.5, .4, 1.0), loc=(x0 + 2.1, y0 + .3, DKT + .5), chamfer=.02)
    a.part('Glass', 'Glass').box((.3, .02, .2), loc=(x0 + 2.1, y0 + .09, DKT + .75), bevel=0)
    a.part('Antennas', 'Steel').cyl(.03, 1.4, loc=(x0 + 2.2, y0 + .4, DKT + 1.7), seg=6, bevel=0)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (x0 + 2.2, y0 + .3, DKT + 2.3), w=.35, h=.35, normal=(0, -1, 0),
                   bars=3)
    a.part('Kit_cables', 'Rubber').tube([(x0 + 1.9, y0 + .3, DKT + .2), (x0 + 1.6, y0 + .8, DKT + .05),
                                         (x0 + .9, y0 + 1.0, DKT + .05)], .02, seg=4)
    # The charging racks: two shelf units with battery packs in rows, the charge lights.
    for rx in (1.3, 2.4):
        sh = a.part('Charge_racks', 'Steel')
        for z in (.3, .65, 1.0):
            sh.box((.9, .4, .03), loc=(rx, -1.2, DKT + z), bevel=0)
        for dx in (-.43, .43):
            sh.box((.035, .4, 1.05), loc=(rx + dx, -1.2, DKT + .52), bevel=0)
        bt = a.part('Batteries', 'Hazard' if rx < 2 else 'EliteBlack')
        for z in (.33, .68):
            for i in range(4):
                bt.box((.16, .12, .08 + i * .01), loc=(rx - .3 + i * .2, -1.2, DKT + z + .05), bevel=0)
        a.part('Charge_leds', 'SignalGreen').box((.8, .01, .03), loc=(rx, -1.41, DKT + .95), bevel=0)
    _launch_points(a, (x0 + .62, y0 + .78, DKT + .45))
    k.clean(a)


# ============================================================================= vehicle hangar (motor-pool shed)
VX = M4.VX
VY0, VY1 = M4.VY0, M4.VY1
VE, VR = M4.VE, M4.VR
DW = 2.72           # door half width: the roller door takes the whole front between two narrow piers
DH = 3.28           # door head
_gable = M4._gable
RSLOPE = math.atan(.12 / .57)


def _roller_door(a):
    """The full-width roller door: the coil box with its end plates and the motor, the door a little over half up
    (slats with their wind locks, the bottom bar with its hazard band and pull handles), the guide channels, the
    pier bollards, the push-button station."""
    y = VY0
    box = a.part('Door_drum', 'Steel')
    k.block(box, (2 * DW + .3, .55, .55), loc=(0, y - .3, DH + .27), chamfer=.04)
    for s in (-1, 1):
        box.box((.04, .6, .6), loc=(s * (DW + .17), y - .3, DH + .27), bevel=0)
    k.block(a.part('Door_motor', 'Armor'), (.32, .3, .36), loc=(DW + .4, y - .3, DH + .1), chamfer=.02)
    a.part('Door_chain', 'Steel').box((.03, .03, 1.6), loc=(DW + .42, y - .25, DH - .9), bevel=0)
    sl = a.part('Door_slats', 'MetalSheet')
    lk = a.part('Door_locks', 'Steel')
    zb = 1.55
    n = int((DH - zb) / .17)
    for i in range(n):
        z = DH - .09 - i * .17
        sl.box((2 * DW - .04, .05, .15), loc=(0, y + .04, z), bevel=0)
        for s in (-1, 1):
            lk.box((.05, .07, .05), loc=(s * (DW - .1), y + .04, z), bevel=0)
    a.part('Door_bottom', 'Steel').box((2 * DW - .02, .08, .1), loc=(0, y + .04, zb - .02), bevel=0)
    a.part('Hazard_marks', 'Hazard').box((2 * DW - .04, .02, .06), loc=(0, y - .01, zb + .02), bevel=0)
    hd = a.part('Kit_handles', 'Steel')
    for x in (-1.2, 1.2):
        K.handle(hd, (x - .1, y - .02, zb + .12), (x + .1, y - .02, zb + .12), (0, -1, 0), h=.05)
    gd = a.part('Door_guides', 'Steel')
    for s in (-1, 1):
        gd.box((.12, .16, DH - .12), loc=(s * (DW + .04), y - .02, .12 + (DH - .12) / 2), bevel=0)
    _bollards(a, [(-DW - .15, y - .35, .12), (DW + .15, y - .35, .12)], h=1.0, r=.1)
    k.block(a.part('Door_station', 'Armor'), (.18, .1, .28), loc=(-DW - .28, y - .08, 1.4), chamfer=.01)
    a.part('Door_buttons', 'LavaGlow').box((.06, .02, .12), loc=(-DW - .28, y - .14, 1.42), bevel=0)


def _ramp(a):
    """The concrete ramp down from the floor to the yard in front of the door: the sloped slab, its kerbs with hazard
    paint, the anti-slip grooves across it, the drain grate at its foot."""
    y0, y1 = VY0 - .05, VY0 - .62
    rp = a.part('Ramp', 'Concrete')
    k.extrude(rp, [(y0, .12), (y1, .0), (y1, -.02), (y0, -.02)], 2 * DW + .4, axis='X')
    kb = a.part('Ramp_kerbs', 'Concrete')
    hz = a.part('Ramp_paint', 'Hazard')
    for s in (-1, 1):
        k.extrude(kb, [(y0, .2), (y1, .08), (y1, -.02), (y0, -.02)], .16, loc=(s * (DW + .28), 0, 0), axis='X')
        hz.box((.165, .3, .012), loc=(s * (DW + .28), y1 + .2, .107), rot=(RSLOPE, 0, 0), bevel=0)
    gv = a.part('Ramp_grooves', 'Undercarriage')
    for i in range(4):
        f = (i + .5) / 4
        gv.box((2 * DW + .2, .04, .01), loc=(0, y0 + (y1 - y0) * f, .12 - .12 * f + .004), rot=(RSLOPE, 0, 0),
               bevel=0)
    a.part('Drain_grate', 'Steel').box((2 * DW, .12, .015), loc=(0, y1 - .07, .006), bevel=0)


def vehicle_hangar_base(a, detail=False):
    """The vehicle hangar (balance vehicle_hangar's model): the motor-pool shed with the full-width roller door and
    the ramp (wave M4's shed, the front reworked and more fitted)."""
    base = a.part('Base', 'Concrete')
    _pad(base, (6.7, 7.5, .12), loc=(0, 0, .06), chamfer=.02)
    fl = a.part('Floor_lines', 'Hazard')
    for x in (-1.9, 1.9):
        fl.box((.08, 6.2, .01), loc=(x, -.3, .125), bevel=0)
    fl.box((3.8, .08, .01), loc=(0, VY0 + .25, .125), bevel=0)
    a.part('Oil_stains', 'Charred').cyl(.6, .01, loc=(.3, -.8, .123), seg=10, bevel=0)
    a.part('Oil_stains', 'Charred').cyl(.35, .01, loc=(-1.1, .9, .123), seg=8, bevel=0)
    _ramp(a)
    # Portal frames at four bays, the knee braces, the eaves beams.
    pf = a.part('Portal_frame', 'Steel')
    for y in (VY0, -1.2, 1.2, VY1):
        for s_ in (-1, 1):
            pf.box((.2, .22, VE), loc=(s_ * (VX - .1), y, .12 + VE / 2), bevel=0)
            pf.limb((s_ * (VX - .1), y, VE + .02), (0, y, VR - .05), .18, .22, bevel=0)
            pf.limb((s_ * (VX - .2), y, VE - .7), (s_ * (VX - 1.0), y, VE + .25), .08, .1, bevel=0)
    for s_ in (-1, 1):
        pf.box((.14, VY1 - VY0, .16), loc=(s_ * (VX - .12), (VY0 + VY1) / 2, VE - .05), bevel=0)
    # Cladding: side walls, the rear gable, the front gable over the door and the two narrow piers.
    wl = a.part('Walls', 'Corrugated')
    for s_ in (-1, 1):
        wl.box((.06, VY1 - VY0, VE - .1), loc=(s_ * VX, (VY0 + VY1) / 2, .12 + (VE - .1) / 2), bevel=0)
    k.extrude(wl, [(-VX, .12), (VX, .12), (VX, VE), (0, VR), (-VX, VE)], .06, loc=(0, VY1, 0), axis='Y')
    k.extrude(wl, [(-VX, DH + .55), (VX, DH + .55), (VX, VE), (0, VR), (-VX, VE)], .06, loc=(0, VY0, 0), axis='Y')
    for s_ in (-1, 1):
        wl.box((VX - DW - .1, .06, DH + .45), loc=(s_ * (VX + DW + .1) / 2, VY0, .12 + (DH + .45) / 2), bevel=0)
    a.part('Interior', 'Undercarriage').box((2 * DW, .02, .55), loc=(0, VY0 + .05, DH + .3), bevel=0)
    # Cladding ribs, broken by the window band (a girt under it), the base flashing.
    rib = a.part('Wall_ribs', 'MetalSheet')
    for s_ in (-1, 1):
        for i in range(12):
            y = VY0 + .3 + i * (VY1 - VY0 - .6) / 11
            rib.box((.04, .06, 2.45), loc=(s_ * (VX + .04), y, .3 + 1.225), bevel=0)
            rib.box((.04, .06, .2), loc=(s_ * (VX + .04), y, VE - .17), bevel=0)
        a.part('Girts', 'Steel').box((.05, VY1 - VY0, .08), loc=(s_ * (VX + .06), (VY0 + VY1) / 2, 2.83), bevel=0)
        a.part('Flashing', 'Steel').box((.05, VY1 - VY0, .1), loc=(s_ * (VX + .05), (VY0 + VY1) / 2, .2), bevel=0)
    # High strip windows down both sides between the frames.
    gl = a.part('Glass', 'Glass')
    wf = a.part('Window_frames', 'Steel')
    for s_ in (-1, 1):
        for yc in (-2.4, 0, 2.35):
            gl.box((.02, 1.5, .4), loc=(s_ * (VX + .075), yc, VE - .55), bevel=0)
            for dz in (-.22, .22):
                wf.box((.05, 1.6, .05), loc=(s_ * (VX + .08), yc, VE - .55 + dz), bevel=0)
            for dy in (-.75, 0, .75):
                wf.box((.05, .05, .44), loc=(s_ * (VX + .08), yc + dy, VE - .55), bevel=0)
    _vehicle_roof(a)
    _roller_door(a)
    k.block(a.part('Sign', 'Team'), (1.6, .05, .5), loc=(0, VY0 - .05, 4.0), rot=K.FORWARD, chamfer=.01)
    a.part('Sign_mark', 'PlasterWhite').box((.7, .02, .12), loc=(0, VY0 - .09, 4.0), bevel=0)
    for s_ in (-1, 1):
        a.part('Hazard_marks', 'Hazard').box((.1, .02, 1.2), loc=(s_ * (DW + .35), VY0 - .05, .72), bevel=0)
        K.lamp(a, (s_ * 1.6, VY0 - .62, DH + .32), facing=(0, -1, -.6), r=.07, guard=True)
    _vehicle_inside(a)
    # The office lean-to on the left side, its window and door, the masts on its roof, its AC.
    ox0, ox1 = VX + .06, VX + .82
    k.block(a.part('Office', 'Plaster'), (ox1 - ox0, 3.0, 2.5), loc=((ox0 + ox1) / 2, .4, .12 + 1.25), chamfer=.03)
    k.block(a.part('Office_roof', 'MetalSheet'), (ox1 - ox0 + .2, 3.2, .08), loc=((ox0 + ox1) / 2 + .05, .4, 2.66),
            rot=(0, -.12, 0), chamfer=.01)
    a.part('Glass', 'Glass').box((.02, 1.0, .6), loc=(ox1 + .01, 1.0, 1.6), bevel=0)
    a.part('Window_frames', 'Steel').box((.03, 1.1, .06), loc=(ox1 + .015, 1.0, 1.27), bevel=0)
    a.part('Window_bars', 'Steel').box((.03, .04, .6), loc=(ox1 + .02, 1.0, 1.6), bevel=0)
    K.door(a, (ox1 + .01, -.5, .12), size=(.75, 1.95), normal=(1, 0, 0), mat='Armor')
    a.part('Office_step', 'Concrete').box((.26, .9, .12), loc=(ox1 + .13, -.5, .06), bevel=0)
    a.part('Antennas', 'Steel').cyl(.04, 2.6, loc=(ox1 - .2, 1.6, 2.7 + 1.3), seg=6, bevel=0)
    K.mesh_antenna(a.part('Antennas', 'Steel'), (ox1 - .2, 1.45, 4.6), w=.35, h=.5, normal=(0, -1, 0), bars=3)
    K.whip_antenna(a.part('Antennas', 'Steel'), (ox1 - .2, -.8, 2.7), h=1.8, r=.018)
    k.block(a.part('Aircon', 'PlasterWhite'), (.55, .3, .4), loc=((ox0 + ox1) / 2, 2.07, .5), chamfer=.02)
    a.part('Aircon_fan', 'Undercarriage').cyl(.15, .02, loc=((ox0 + ox1) / 2, 2.23, .52), rot=K.FORWARD, seg=8,
                                              bevel=0)
    _wall_kit(a, 'Office_boxes', 'Armor', 'x', ox1, 1, .1, 1.8, 2.0, 2.4, 2, seed=101, depth=(.04, .08))
    _shed_kit(a)
    for s_ in (-1, 1):
        K.floodlight(a, (s_ * 3.62, VY0 - .25, 0), facing=(-s_ * .3, -1, -.5), pole=4.6)
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-VX - .35, -1.8, .12), rot=(0, 0, R90))
    K.jerrycan(a.part('Jerrycans', 'Fuel'), (-VX - .35, -1.45, .12), rot=(0, 0, R90 + .1))
    a.part('Tow_bar', 'Steel').box((.1, 1.6, .08), loc=(-VX - .45, 1.2, .16), rot=(0, 0, .1), bevel=0)
    for x, y in ((3.4, -3.9), (-3.4, -3.9), (0, -4.1)):
        K.dust(a, (x, y, 0), radius=1.8, k=.3)
    k.clean(a)


def _vehicle_roof(a):
    """The gable roof: the two sheeted slopes, their laps, the skylights, the ridge cap with its continuous ridge
    vent, two turbine ventilators, the gutters and downpipes, the lightning rods."""
    rf = a.part('Roof', 'MetalSheet')
    pitch = math.atan((VR - VE) / VX)
    slope = math.hypot(VX, VR - VE) + .35
    # Each slope one sheet facing up (its underside is never seen), a fascia strip along the eave and the verges.
    ex, ez, rz = VX + .48, VE - .03, VR + .08
    ya, yb = VY0 - .25, VY1 + .25
    for s_ in (-1, 1):
        q = [(s_ * ex, ya, ez), (s_ * ex, yb, ez), (0, yb, rz), (0, ya, rz)]
        rf.mesh(q if s_ > 0 else q[::-1], [(0, 1, 2, 3)])
        fa = a.part('Fascias', 'Steel')
        fa.box((.04, yb - ya, .12), loc=(s_ * (ex + .02), (ya + yb) / 2, ez - .04), bevel=0)
        for y in (ya, yb):
            fa.box((ex, .04, .1), loc=(s_ * ex / 2, y + (.02 if y == ya else -.02), (ez + rz) / 2 - .02),
                   rot=(0, s_ * pitch, 0), bevel=0)
    a.part('Ridge_cap', 'Steel').box((.24, VY1 - VY0 + .5, .06), loc=(0, (VY0 + VY1) / 2, VR + .11), bevel=0)
    rv = a.part('Ridge_vent', 'Steel')
    rv.box((.34, VY1 - VY0 - 1.0, .05), loc=(0, (VY0 + VY1) / 2, VR + .3), bevel=0)
    for i in range(9):
        rv.box((.04, .04, .16), loc=(0, VY0 + .6 + i * (VY1 - VY0 - 1.2) / 8, VR + .2), bevel=0)
    lap = a.part('Roof_ribs', 'Steel')
    sky = a.part('Skylights', 'Glass')
    for s_ in (-1, 1):
        cx, cz = s_ * (VX / 2 + .14), (VE + VR) / 2 + .06
        nx, nz = -s_ * math.sin(pitch), math.cos(pitch)
        for i in range(12):
            y = VY0 - .2 + i * (VY1 - VY0 + .4) / 11
            lap.box((slope, .05, .03), loc=(cx + nx * .04, y, cz + nz * .04), rot=(0, s_ * pitch, 0), bevel=0)
        for y in (-2.3, .1, 2.3):
            sky.box((slope * .45, .75, .02), loc=(cx + nx * .035 - s_ * .25, y, cz + nz * .035 + .2),
                    rot=(0, s_ * pitch, 0), bevel=0)
    K.grille(a, (0, VY1 + .04, 3.85), .7, .35, facing=(0, 1, 0), slats=4)
    for y in (-1.2, 1.4):
        k.lathe(a.part('Ventilators', 'Steel'), [(.1, 0), (.1, .15), (.2, .2), (.22, .38), (.12, .46), (0, .48)],
                loc=(.6, y, _gable(.6) + .05), seg=8)
    gt = a.part('Gutters', 'Steel')
    for s_ in (-1, 1):
        gt.box((.12, VY1 - VY0 + .5, .1), loc=(s_ * (VX + .45), (VY0 + VY1) / 2, VE - .05), bevel=0)
        _downpipe(a, s_ * (VX + .45), VY1 + .15, .12, VE - .1, s_)
    for y in (VY0 + .1, 0.0, VY1 - .1):
        a.part('Lightning_rods', 'Steel').cyl(.015, .9, loc=(0, y, VR + .55), seg=4, bevel=0)
    a.part('Roof_aerial', 'Steel').cyl(.02, 1.2, loc=(-1.0, 2.9, _gable(-1.0) + .65), seg=4, bevel=0)
    a.part('Roof_aerial', 'Steel').box((.5, .03, .03), loc=(-1.0, 2.9, _gable(-1.0) + 1.1), bevel=0)
    # Roof plant on the right slope: the water tank on its frame, two extract fan cowls, the roof hatch.
    wx = 1.9
    wz = _gable(wx) + .1
    st = a.part('Tank_frame', 'Steel')
    for dx in (-.35, .35):
        for dy in (-.3, .3):
            st.box((.05, .05, .5), loc=(wx + dx, -2.4 + dy, wz + .25 - dx * .3), bevel=0)
    st.box((.8, .7, .04), loc=(wx, -2.4, wz + .5), bevel=0)
    k.lathe(a.part('Water_tank', 'PlasterWhite'), [(.3, 0), (.32, .05), (.32, .6), (.25, .66), (0, .68)],
            loc=(wx, -2.4, wz + .52), seg=10, worn=(1,))
    for i, (x, y, r) in enumerate(((2.3, -.6, .2), (2.0, .6, .16))):
        z = _gable(x) + .08
        k.lathe(a.part('Fan_cowls', 'Steel'), [(r, 0), (r, .18), (r * .8, .3), (0, .32)], loc=(x, y, z), seg=8)
        a.part('Fan_cowls', 'Undercarriage').cyl(r * .85, .02, loc=(x, y, z + .2 + i * .01), seg=8, bevel=0)
    pitch_ = math.atan((VR - VE) / VX)
    k.block(a.part('Roof_hatch', 'Hazard'), (.8, .8, .14), loc=(-2.0, .9, _gable(-2.0) + .15), rot=(0, -pitch_, 0),
            chamfer=.01)
    a.part('Roof_hatch_lid', 'Armor').box((.7, .7, .03), loc=(-2.0, .9, _gable(-2.0) + .24), rot=(0, -pitch_, 0),
                                          bevel=0)
    # Fastener rows down every other sheet lap.
    fx = a.part('Roof_fixings', 'Steel')
    for s_ in (-1, 1):
        nx, nz = -s_ * math.sin(pitch), math.cos(pitch)
        for i in range(0, 12, 2):
            y = VY0 - .2 + i * (VY1 - VY0 + .4) / 11 + .05
            for f in (.15, .45, .75):
                x = s_ * (.2 + f * (VX - .2))
                fx.box((.05, .05, .03), loc=(x + nx * .06, y, _gable(x) + .14 + nz * .02), rot=(0, s_ * pitch, 0),
                       bevel=0)


def _vehicle_inside(a):
    """Inside the shed: the dark back, the two-post lift, the hoist beam with its trolley, the bench and tool board,
    cabinets, tyres, drums, the engine on its stand, the parts shelving, spare road wheels and track links."""
    a.part('Interior', 'Undercarriage').box((6.1, .02, 3.0), loc=(0, VY1 - .1, 1.6), bevel=0)
    lift = a.part('Vehicle_lift', 'CraneYellow')
    for s_ in (-1, 1):
        lift.box((.22, .3, 2.6), loc=(s_ * 1.45, .9, .12 + 1.3), bevel=.01)
        lift.box((.1, 1.2, .08), loc=(s_ * 1.0, .9, .9), bevel=0)
    lift.box((3.1, .2, .14), loc=(0, .9, 2.75), bevel=0)
    a.part('Lift_controls', 'Armor').box((.15, .1, .3), loc=(1.45, .7, 1.2), bevel=0)
    k.block(a.part('Bench_top', 'Wood'), (.7, 2.2, .08), loc=(2.6, 1.6, 1.0), chamfer=.01)
    bl = a.part('Bench_legs', 'Steel')
    for y in (.6, 2.6):
        bl.box((.6, .05, 1.0), loc=(2.6, y, .6), bevel=0)
    tc = a.part('Tool_cabinets', 'Team')
    for y in (-.4, .3):
        k.block(tc, (.55, .6, 1.5), loc=(2.75, y, .87), chamfer=.02)
    a.part('Bench_tools', 'Steel').box((.4, 1.4, .12), loc=(2.55, 1.6, 1.1), bevel=.01)
    a.part('Tool_board', 'Wood').box((.03, 1.6, .9), loc=(3.05, 1.6, 1.75), bevel=0)
    _wall_kit(a, 'Board_tools', 'Steel', 'x', 3.035, -1, .9, 2.3, 1.4, 2.1, 6, seed=97, size=(.04, .3),
              depth=(.02, .05))
    ty = a.part('Tyres', 'Rubber')
    for i in range(3):
        k.ring(ty, [(.22, 0), (.38, 0), (.4, .1), (.38, .22), (.22, .22)], loc=(-2.55, 2.4, .12 + i * .23), seg=8)
    dr = a.part('Drums', 'BarrelRed')
    bd = a.part('Drum_bands', 'Steel')
    for x, y in ((-2.65, .9), (-2.1, .6)):
        K.fuel_drum(dr, bd, (x, y, .12))
    a.part('Hoist', 'Steel').box((.18, 6.4, .14), loc=(-1.0, -.1, 3.25), bevel=0)
    k.block(a.part('Hoist_trolley', 'CraneYellow'), (.3, .3, .2), loc=(-1.0, -.5, 3.08), chamfer=.02)
    a.part('Hoist_hook', 'CraneYellow').box((.12, .14, .3), loc=(-1.0, -.5, 2.35), bevel=.01)
    a.part('Hoist_chain', 'Steel').cyl(.012, .55, loc=(-1.0, -.5, 2.75), seg=4, bevel=0)
    sh = a.part('Shelving', 'Steel')
    for z in (.5, 1.1, 1.7, 2.3):
        sh.box((.5, 2.4, .04), loc=(-2.75, -1.6, z), bevel=0)
    for y in (-2.75, -.45):
        sh.box((.5, .05, 2.3), loc=(-2.75, y, 1.27), bevel=0)
    for z in (.52, 1.12, 1.72):
        K.clutter(a, 'Bins', 'Crate', -2.98, -2.52, -2.7, -.5, z, 4, seed=int(z * 10), size=(.2, .45),
                  height=(.15, .4))
    k.block(a.part('Engine', 'Undercarriage'), (.6, .8, .55), loc=(-.9, -2.2, .7), chamfer=.04)
    a.part('Engine_parts', 'Steel').box((.2, .5, .15), loc=(-.9, -2.2, 1.05), bevel=0)
    es = a.part('Engine_stand', 'CraneYellow')
    es.box((.08, .9, .08), loc=(-.9, -2.2, .38), bevel=0)
    es.box((.7, .08, .08), loc=(-.9, -2.6, .16), bevel=0)
    es.box((.7, .08, .08), loc=(-.9, -1.8, .16), bevel=0)
    rw = a.part('Road_wheels', 'Armor')
    rt = a.part('Road_wheel_tyres', 'Rubber')
    for x, y, z in ((1.5, -2.6, .2), (2.0, -2.5, .2), (1.75, -2.55, .38)):
        rw.cyl(.3, .14, loc=(x, y, z), seg=10, bevel=.01)
        rt.cyl(.31, .08, loc=(x, y, z), seg=10, bevel=0)
    tl = a.part('Track_links', 'Undercarriage')
    for i in range(8):
        tl.box((.5, .16, .05), loc=(.4, -2.9 + i * .17, .15 + (i % 2) * .01), rot=(0, 0, .03 * i), bevel=0)
    K.clutter(a, 'Bench_parts', 'Steel', 2.35, 2.85, .65, 2.55, 1.04, 6, seed=93, size=(.08, .25), height=(.04, .16))
    K.clutter(a, 'Floor_kit', 'Crate', -1.6, -.3, 2.2, 3.3, .12, 5, seed=95, size=(.15, .45), height=(.1, .4))
    # The crew lockers along the back wall, the wall lamps, the extinguishers on the frames, jack stands, a creeper.
    lk = a.part('Lockers', 'Team')
    for i in range(5):
        k.block(lk, (.42, .45, 1.8 + (i % 2) * .05), loc=(.2 + i * .45, VY1 - .35, .12 + .9), chamfer=.01)
        a.part('Locker_vents', 'Undercarriage').box((.25, .01, .1), loc=(.2 + i * .45, VY1 - .58, 1.6), bevel=0)
    for x in (-2.0, 0, 2.0):
        K.lamp(a, (x, VY1 - .15, 2.9), facing=(0, -1, -.5), r=.06, guard=False)
    ex = a.part('Extinguishers', 'BarrelRed')
    for x, y in ((VX - .25, -1.0), (-VX + .25, 1.0)):
        k.lathe(ex, [(.08, 0), (.08, .5), (.04, .58), (0, .6)], loc=(x, y, .9), seg=8)
    js = a.part('Jack_stands', 'CraneYellow')
    for x, y in ((-.4, .2), (.4, .2), (-.4, 1.6), (.4, 1.6)):
        k.lathe(js, [(.14, 0), (.05, .05), (.04, .45), (.07, .47), (0, .5)], loc=(x, y, .12), seg=6)
    a.part('Creeper', 'EliteBlack').box((.45, 1.0, .06), loc=(1.3, 1.9, .2), bevel=0)
    tags = a.part('Bay_marks', 'PlasterWhite')
    for i, x in enumerate((-1.2, -.4, .4, 1.2)):
        tags.box((.3 + i * .04, .12, .01), loc=(x, VY0 + .45, .125), bevel=0)
    bolts = a.part('Kit_bolts', 'Steel')
    for y in (VY0, -1.2, 1.2, VY1):
        for s_ in (-1, 1):
            for dx in (-.08, .08):
                bolts.box((.04, .04, .05), loc=(s_ * (VX - .1) + dx, y - .14, .15), bevel=0)


def _shed_kit(a):
    """Outside the shed: the roof's solar panels and faction panel, the heater stack and roof walkway; AC units, the
    electrical cabinet, conduit, wall boxes and the gas cage on the right wall; the oil tank, pallets, crates and the
    A-frame gantry with a power pack at the rear; spare tyres on the right."""
    pitch = math.atan((VR - VE) / VX)
    sol = a.part('Solar_panels', 'EliteBlack')
    sfr = a.part('Solar_frames', 'Steel')
    for y in (-2.6, -1.4, -.2):
        x = -1.55
        z = _gable(x) + .14
        sol.box((1.5, 1.05, .03), loc=(x, y, z), rot=(0, -pitch, 0), bevel=0)
        sfr.box((1.56, .05, .06), loc=(x, y - .54, z - .01), rot=(0, -pitch, 0), bevel=0)
    a.part('Solar_inverter', 'Armor').box((.2, .3, .4), loc=(-VX - .14, -1.4, 2.5), bevel=0)
    a.part('Roof_mark', 'Team').box((1.3, 1.3, .02), loc=(1.6, 1.8, _gable(1.6) + .13), rot=(0, pitch, 0), bevel=0)
    a.part('Roof_mark_bar', 'PlasterWhite').box((.9, .22, .02), loc=(1.6, 1.8, _gable(1.6) + .15),
                                                rot=(0, pitch, .7), bevel=0)
    k.lathe(a.part('Heater_stack', 'Steel'), [(.09, 0), (.09, 1.3), (.18, 1.32), (.18, 1.42), (0, 1.5)],
            loc=(-2.3, 2.6, _gable(-2.3)), seg=8, worn=(3,))
    K.soot(a, (-2.3, 2.6, _gable(-2.3) + 1.45), radius=.35, k=.4)
    wk = a.part('Roof_walkway', 'Steel')
    for y in (-3.0, -1.5, 0, 1.5, 3.0):
        wk.box((.5, 1.2 + (y % 1.0) * .1, .04), loc=(.32, y, _gable(.32) + .17), rot=(0, pitch, 0), bevel=0)
    ac = a.part('Aircon', 'PlasterWhite')
    for y, w in ((-2.3, .8), (-1.2, .65)):
        k.block(ac, (.4, w, .55), loc=(-VX - .26, y, .45), chamfer=.02)
        a.part('Aircon_fan', 'Undercarriage').cyl(.2, .02, loc=(-VX - .47, y, .48), rot=(0, R90, 0), seg=8, bevel=0)
        a.part('Kit_cables', 'Rubber').tube([(-VX - .1, y, .7), (-VX - .08, y, 1.4)], .02, seg=4)
    k.block(a.part('Electric_cabinet', 'Armor'), (.25, .7, 1.1), loc=(-VX - .15, .4, 1.1), chamfer=.02)
    a.part('Hazard_marks', 'Hazard').box((.02, .25, .2), loc=(-VX - .28, .4, 1.4), bevel=0)
    a.part('Conduit', 'Steel').tube([(-VX - .12, .4, 1.65), (-VX - .12, .4, 3.1), (-VX - .12, 2.6, 3.1)], .03, seg=4)
    _wall_kit(a, 'Wall_boxes', 'Armor', 'x', -VX - .06, -1, -3.3, -.1, 1.3, 2.7, 4, seed=102)
    _wall_kit(a, 'Wall_panels', 'Team', 'y', VY1 + .06, 1, -.2, 3.0, 1.2, 3.0, 4, seed=103, size=(.35, .7),
              depth=(.06, .12))
    _wall_kit(a, 'Wall_boxes', 'Steel', 'x', VX + .06, 1, -3.3, -1.3, 1.0, 2.6, 4, seed=104)
    _wall_kit(a, 'Pier_boxes', 'Armor', 'y', VY0 - .03, -1, DW + .25, VX, .9, 2.2, 2, seed=105, size=(.1, .2))
    cage = a.part('Gas_cage', 'Steel')
    cage.box((.7, 1.0, .05), loc=(-VX - .45, 2.6, 1.6), bevel=0)
    for dx, dy in ((-.3, -.45), (.3, -.45), (-.3, .45), (.3, .45)):
        cage.box((.04, .04, 1.5), loc=(-VX - .45 + dx, 2.6 + dy, .85), bevel=0)
    gb = a.part('Gas_bottles', 'Hazard')
    for j, dy in enumerate((-.25, .05, .32)):
        k.lathe(gb, [(.1, 0), (.1, .95 + j * .06), (.05, 1.05 + j * .06), (0, 1.06 + j * .06)],
                loc=(-VX - .45, 2.6 + dy, .12), seg=8)
    k.lathe(a.part('Oil_tank', 'Fuel'), [(.38, 0), (.42, .05), (.42, 1.55), (.38, 1.6), (0, 1.6)],
            loc=(-1.8, VY1 + .45, .85), rot=(0, R90, 0), seg=10, worn=(1, 2))
    st = a.part('Tank_stand', 'Steel')
    for x in (-1.6, -.4):
        st.box((.08, .7, .5), loc=(x, VY1 + .45, .35), bevel=0)
    a.part('Tank_valve', 'BarrelRed').box((.12, .12, .12), loc=(-.13, VY1 + .45, .7), bevel=0)
    K.clutter(a, 'Crates', 'Crate', .3, 1.4, VY1 + .12, VY1 + .48, .12, 3, seed=91, size=(.25, .45), height=(.2, .6))
    a.part('Pallets', 'Wood').box((1.1, .4, .1), loc=(.85, VY1 + .3, .06), bevel=0)
    gx, gy = 2.4, VY1 + .45
    gf = a.part('Gantry', 'CraneYellow')
    for s_ in (-1, 1):
        gf.limb((gx + s_ * .6, gy - .25, .12), (gx + s_ * .6, gy, 2.4), .08, .08, bevel=0)
        gf.limb((gx + s_ * .6, gy + .25, .12), (gx + s_ * .6, gy, 2.4), .08, .08, bevel=0)
    gf.box((1.4, .14, .16), loc=(gx, gy, 2.45), bevel=0)
    a.part('Hoist_chain', 'Steel').cyl(.012, 1.0, loc=(gx, gy, 1.9), seg=4, bevel=0)
    k.block(a.part('Power_pack', 'Undercarriage'), (.7, .45, .5), loc=(gx, gy, 1.15), chamfer=.04)
    K.grille(a, (gx, gy - .235, 1.2), .45, .3, facing=(0, -1, 0), slats=3)
    ty = a.part('Tyres', 'Rubber')
    for i in range(2):
        k.ring(ty, [(.24, -.11), (.4, -.11), (.42, 0), (.4, .11), (.24, .11)], loc=(VX + .3 + i * .12, -2.6 + i * .5,
                                                                                      .5), rot=(0, R90 - .25, 0),
               seg=8)
    bolts = a.part('Kit_bolts', 'Steel')
    for s_ in (-1, 1):
        for y in (-3.0, -1.6, -.2, 1.2, 2.6):
            bolts.box((.03, .05, .05), loc=(s_ * (VX + .1), y, .3), bevel=0)
    # Front right corner: three drums on a drip tray; the spare road wheel rack on the left.
    a.part('Drip_tray', 'Steel').box((.9, .7, .08), loc=(-VX - .45, -3.25, .04), bevel=0)
    dr = a.part('Drums', 'BarrelRed')
    bd = a.part('Drum_bands', 'Steel')
    for dx, dy in ((-.2, -.15), (.2, -.15), (0, .2)):
        K.fuel_drum(dr, bd, (-VX - .45 + dx, -3.25 + dy, .08), r=.2, h=.75)
    wr = a.part('Wheel_rack', 'Steel')
    for y in (1.0, 2.0):
        wr.box((.06, .06, 1.0), loc=(VX + .5, y, .62), bevel=0)
    wr.box((.06, 1.06, .06), loc=(VX + .5, 1.5, 1.1), bevel=0)
    rw = a.part('Road_wheels', 'Armor')
    for y in (1.2, 1.5, 1.8):
        rw.cyl(.3, .12, loc=(VX + .32, y, .55), rot=K.FORWARD, seg=10, bevel=.01)


# ============================================================================= aircraft hangar (helicopter shelter)
HX, HZ = M4.HX, M4.HZ
HY0, HY1 = M4.HY0, M4.HY1
_arch = M4._arch


def _heli_kit(a):
    """The shelter's fittings inside and on the apron: the maintenance stand, tool chests, spares, the gantry beam
    with its chain hoist, the spare engine on its dolly, the tug, the light masts, cones, sandbag corners, rear
    vents."""
    ms = a.part('Work_stand', 'CraneYellow')
    x0, y0 = -1.9, .4
    ms.box((1.4, 1.0, .06), loc=(x0, y0, 1.8), bevel=0)
    for dx in (-.65, .65):
        for dy in (-.45, .45):
            ms.box((.06, .06, 1.75), loc=(x0 + dx, y0 + dy, .95), bevel=0)
    K.railing(a.part('Work_stand_rails', 'Steel'), [(x0 - .7, y0 - .5, 1.83), (x0 + .7, y0 - .5, 1.83),
                                                    (x0 + .7, y0 + .5, 1.83)], h=.8, post=.7, r=.018)
    stp = a.part('Work_stand_steps', 'Steel')
    for i in range(6):
        stp.box((.55, .2, .03), loc=(x0 + .1, y0 + .65 + i * .22, 1.62 - i * .27), bevel=0)
    K.clutter(a, 'Tool_chests', 'Team', 1.2, 3.1, 2.0, 3.6, .1, 5, seed=97, size=(.3, .7), height=(.4, 1.0))
    K.clutter(a, 'Spares', 'Crate', -3.2, -1.2, 1.8, 3.0, .1, 4, seed=98, size=(.25, .6), height=(.15, .45))
    # The gantry beam along the shelter's axis, its trolley and chain hoist.
    gb = a.part('Gantry', 'CraneYellow')
    gb.box((.16, HY1 - HY0 - .3, .2), loc=(.6, (HY0 + HY1) / 2, 3.65), bevel=0)
    for y in (HY0 + .3, HY1 - .3):
        gb.box((.1, .1, .3), loc=(.6, y, 3.9), bevel=0)
    k.block(a.part('Hoist_trolley', 'Steel'), (.3, .34, .22), loc=(.6, 1.2, 3.44), chamfer=.02)
    a.part('Hoist_chain', 'Steel').cyl(.012, 1.0, loc=(.6, 1.2, 2.83), seg=4, bevel=0)
    a.part('Hoist_hook', 'CraneYellow').box((.12, .14, .2), loc=(.6, 1.2, 2.25), bevel=.01)
    # The spare turboshaft engine on its dolly under the hoist.
    k.lathe(a.part('Spare_engine', 'Alloy'), [(.0, 0), (.22, .05), (.26, .4), (.24, 1.0), (.16, 1.2), (0, 1.22)],
            loc=(.6, .65, .75), rot=K.FORWARD, seg=10, worn=(2, 3))
    dl = a.part('Engine_dolly', 'Steel')
    dl.box((.7, 1.3, .06), loc=(.6, .05, .4), bevel=0)
    for dy in (-.5, .5):
        dl.box((.06, .06, .3), loc=(.6, .05 + dy, .55), bevel=0)
    wh = a.part('Tyres', 'Rubber')
    for dx in (-.3, .3):
        for dy in (-.55, .55):
            wh.cyl(.1, .06, loc=(.6 + dx, .05 + dy, .2), rot=(0, R90, 0), seg=8, bevel=0)
    # The tow tug on the pad's right edge.
    tg = a.part('Tug', 'CraneYellow')
    k.block(tg, (.9, 1.5, .5), loc=(-2.9, -2.8, .45), chamfer=.04)
    k.block(tg, (.7, .5, .35), loc=(-2.9, -2.25, .87), chamfer=.03)
    a.part('Glass', 'Glass').box((.6, .02, .2), loc=(-2.9, -2.51, .9), bevel=0)
    a.part('Tug_beacon', 'Lamp').cyl(.05, .08, loc=(-2.9, -2.25, 1.09), seg=6, bevel=0)
    for dy in (-.5, .5):
        for s_ in (-1, 1):
            wh.cyl(.2, .14, loc=(-2.9 + s_ * .48, -2.8 + dy, .3), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Tow_bar', 'Steel').box((.08, .7, .06), loc=(-2.9, -3.75, .3), rot=(.1, 0, 0), bevel=0)
    K.floodlight(a, (3.8, 3.85, .1), facing=(-.4, -1, -.6), pole=5.2)
    cones = a.part('Cones', 'Hazard')
    for x, y in ((3.6, -4.0), (-.9, -4.0), (.9, -4.0)):
        k.lathe(cones, [(.14, 0), (.14, .03), (.04, .5), (0, .5)], loc=(x, y, .1), seg=6)
    for s_ in (-1, 1):
        W.bags(a, [(s_ * 3.85, HY1 - .3, .1), (s_ * 3.85, HY1 - 1.4, .1)], layers=2, bag=(.5, .28, .15),
               seed=99 + s_)
    K.clutter(a, 'Small_parts', 'Steel', -.9, .3, 2.6, 3.6, .1, 6, seed=96, size=(.1, .3), height=(.05, .25))
    a.part('Front_band', 'Team').tube([(x * 1.012, HY0 - .09, z + .03) for x, z in _arch(1.0)[2:-2]], .05, seg=4,
                                      caps=False)
    K.floodlight(a, (-3.85, -.4, .1), facing=(.5, -1, -.6), pole=4.4)
    K.floodlight(a, (3.85, -.45, .1), facing=(-.5, -1, -.6), pole=4.0)
    # Light bars on the poles: a crossarm with two more lamp heads on each.
    for x, y, h in ((3.8, 3.85, 5.2), (-3.85, -.4, 4.4), (3.85, -.45, 4.0)):
        sx = -1 if x > 0 else 1                     # the arm reaches in over the slab
        a.part('Light_arms', 'Steel').box((.8, .06, .06), loc=(x + sx * .4, y, h - .3), bevel=0)
        for dx in (.35, .72):
            k.block(a.part('Light_housing', 'Armor'), (.22, .14, .18), loc=(x + sx * dx, y - .06, h - .42),
                    rot=(-.5, 0, 0), chamfer=.02)
    # The parts shelving down the right wall with bins, oil drums, the wheel dollies.
    sh = a.part('Shelving', 'Steel')
    sx = -HX + .55
    for z in (.45, 1.0, 1.55):
        sh.box((.45, 1.8, .03), loc=(sx, 2.75, z), bevel=0)
    for y in (1.88, 3.62):
        sh.box((.45, .04, 1.6), loc=(sx, y, .9), bevel=0)
    for z in (.47, 1.02, 1.57):
        K.clutter(a, 'Bins', 'Crate', sx - .2, sx + .2, 1.95, 3.55, z, 4, seed=int(z * 31), size=(.15, .4),
                  height=(.12, .35))
    dr = a.part('Drums', 'BarrelRed')
    bd = a.part('Drum_bands', 'Steel')
    for x, y in ((2.9, 1.0), (3.05, 1.5)):
        K.fuel_drum(dr, bd, (x, y, .1), r=.22, h=.8)
    dl = a.part('Wheel_dollies', 'CraneYellow')
    for x in (-1.6, -1.0):
        dl.box((.5, .3, .1), loc=(x, 3.55, .2), bevel=0)
        dl.box((.04, .04, .6), loc=(x, 3.5, .5), rot=(.4, 0, 0), bevel=0)
    K.grille(a, (1.6, HY1 + .06, 3.0), .9, .5, facing=(0, 1, 0), slats=4)
    K.grille(a, (-1.6, HY1 + .06, 3.0), .9, .5, facing=(0, 1, 0), slats=4)


def _arch_z(x):
    """The fabric's height at x (the arch line, linear between its points)."""
    pts = sorted(_arch(1.0)[1:-1])
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            return z0 + (z1 - z0) * (x - x0) / (x1 - x0 or 1)
    return .1


def _shell(a):
    """The fabric arch on its steel ribs: the shell, seven ribs, purlins, the fabric seams between the ribs, the crown
    with its vents, beacons, lightning rod and cable tray, the closed rear end with its door, the side anchors and
    straps, the HVAC unit with its duct into the fabric, the folded front doors."""
    outer = _arch(1.0)
    inner = [(x * .985, .1 + (z - .1) * .985) for x, z in outer]
    k.extrude(a.part('Roof', 'Canvas'), outer + inner[::-1], HY1 - HY0, loc=(0, (HY0 + HY1) / 2, 0), axis='Y')
    ribs = a.part('Arch_ribs', 'Steel')
    ys = [HY0 - .04 + i * (HY1 - HY0 + .06) / 6 for i in range(7)]
    for y in ys:
        ribs.tube([(x * 1.01, y, z + (.03 if z > .2 else 0)) for x, z in outer], .06, seg=4)
    seams = a.part('Fabric_seams', 'Undercarriage')
    for y0, y1 in zip(ys, ys[1:]):
        ym = (y0 + y1) / 2
        seams.tube([(x * 1.004, ym, z + .01) for x, z in outer[2:-2]], .015, seg=3, caps=False)
    k.extrude(a.part('Walls', 'Canvas'), outer, .05, loc=(0, HY1, 0), axis='Y')
    a.part('Interior', 'Undercarriage').box((6.6, .02, 3.6), loc=(0, HY1 - .08, 1.9), bevel=0)
    pur = a.part('Purlins', 'Steel')
    for i in (2, 4, 6, 8):
        x, z = outer[i]
        pur.tube([(x * 1.012, HY0 - .04, z + .03), (x * 1.012, HY1 + .02, z + .03)], .025, seg=4, caps=False)
    crown = HZ + .02
    for y in (.3, 1.6, 2.9):
        k.lathe(a.part('Ventilators', 'Steel'), [(.1, 0), (.1, .12), (.18, .16), (.2, .32), (.1, .4), (0, .42)],
                loc=(0, y, crown - .02), seg=8)
    K.beacon(a, (0, HY0 + .05, crown + .08), r=.07)
    K.beacon(a, (0, HY1 - .05, crown + .08), r=.07)
    for x, y in ((0, 2.25), (-2.0, .6), (2.1, 3.3)):
        zt = _arch_z(x)
        a.part('Lightning_rods', 'Steel').cyl(.015, 1.1, loc=(x, y, zt + .55), seg=4, bevel=0)
    for x, y in ((1.5, 1.0), (-1.5, 2.2)):
        k.lathe(a.part('Ventilators', 'Steel'), [(.08, 0), (.08, .1), (.15, .13), (.16, .26), (.08, .32), (0, .34)],
                loc=(x, y, _arch_z(x) - .02), seg=8)
    a.part('Cable_tray', 'Steel').tube([(.35, HY0 + .1, crown - .02), (.35, HY1 - .1, crown - .02)], .03, seg=4)
    K.door(a, (2.2, HY1 + .03, .1), size=(.9, 2.0), normal=(0, 1, 0), mat='Armor')
    K.ladder(a.part('Ladders', 'Steel'), (-1.2, HY1 + .24, .1), (-1.2, HY1 + .06, 3.3), width=.45, step=.3, r=.018)
    k.block(a.part('Aircon', 'PlasterWhite'), (.6, 1.0, .8), loc=(-HX - .2, 2.2, .5), chamfer=.03)
    a.part('Aircon_fan', 'Undercarriage').cyl(.25, .02, loc=(-HX - .51, 2.2, .55), rot=(0, R90, 0), seg=10, bevel=0)
    a.part('Hvac_duct', 'Canvas').tube([(-HX - .2, 2.2, .9), (-HX - .25, 2.2, 1.6), (-HX + .1, 2.2, 2.0)], .16, seg=8)
    an = a.part('Anchors', 'Steel')
    for s_ in (-1, 1):
        for y in (HY0 + .1, .85, 2.4, HY1):
            an.box((.3, .3, .06), loc=(s_ * (HX + .12), y, .13), bevel=0)
    tb = a.part('Team_band', 'Team')
    for s_ in (-1, 1):
        tb.box((.03, HY1 - HY0 - .2, .35), loc=(s_ * (HX + .015), (HY0 + HY1) / 2, 2.2), bevel=0)
    st = a.part('Kit_straps', 'Hazard')
    for s_ in (-1, 1):
        for y in (.85, 2.4):
            st.limb((s_ * (HX + .12), y - .7, .16), (s_ * (HX - .25), y, 2.6), .04, .02, bevel=0)
            st.limb((s_ * (HX + .12), y + .7, .16), (s_ * (HX - .25), y, 2.6), .04, .02, bevel=0)
    dr = a.part('Doors', 'Canvas')
    dfr = a.part('Door_frames', 'Steel')
    for s_ in (-1, 1):
        dr.box((.06, 1.3, 3.2), loc=(s_ * (HX + .12), HY0 + .7, .1 + 1.6), bevel=0)
        dfr.box((.08, 1.38, .08), loc=(s_ * (HX + .14), HY0 + .7, 3.32), bevel=0)
        dfr.box((.08, .08, 3.2), loc=(s_ * (HX + .14), HY0 + .02, 1.7), bevel=0)
        dfr.box((.08, .08, 3.2), loc=(s_ * (HX + .14), HY0 + 1.38, 1.7), bevel=0)
        a.part('Door_guides', 'Steel').box((.12, .5, .08), loc=(s_ * (HX + .05), HY0 + .2, 3.38), bevel=0)
        for y in (HY0 + .2, HY0 + 1.2):
            a.part('Door_rollers', 'Rubber').cyl(.07, .06, loc=(s_ * (HX + .12), y, .17), rot=(0, R90, 0), seg=8,
                                                 bevel=0)
    a.part('Side_door', 'Armor').box((.06, .8, 1.9), loc=(HX + .03, 3.2, 1.05), bevel=.01)
    a.part('Door_frames', 'Steel').box((.08, .95, .08), loc=(HX + .05, 3.2, 2.05), bevel=0)
    a.part('Side_step', 'Steel').box((.4, .8, .1), loc=(HX + .25, 3.2, .15), bevel=0)


def _lattice_mast(a, loc, h, w=.36, bay=.5):
    """A self-supporting triangular lattice mast: three legs, the zig-zag bracing on each face, the panel antennas,
    a link dish, the whip and the obstruction beacon on top."""
    x, y, z = loc
    legs = [(x + math.cos(u) * w * .58, y + math.sin(u) * w * .58) for u in (R90, R90 + TAU / 3, R90 + 2 * TAU / 3)]
    lg = a.part('Mast_legs', 'Steel')
    for lx, ly in legs:
        lg.cyl(.025, h, loc=(lx, ly, z + h / 2), seg=5, bevel=0)
    br = a.part('Mast_bracing', 'Steel')
    n = int(h / bay)
    for i in range(n):
        z0, z1 = z + i * bay, z + (i + 1) * bay
        for j in range(3):
            (ax, ay), (bx, by) = legs[j], legs[(j + 1) % 3]
            p0, p1 = ((ax, ay, z0), (bx, by, z1)) if i % 2 == 0 else ((bx, by, z0), (ax, ay, z1))
            br.limb(p0, p1, .016, .016, bevel=0)
    for u in (0, 2.1):
        K.mesh_antenna(a.part('Antennas', 'Steel'), (x + math.sin(u) * .3, y - math.cos(u) * .3, z + h - .5),
                       w=.28, h=.5, normal=(math.sin(u), -math.cos(u), 0), bars=3)
    K.dish(a.part('Link_dish', 'PlasterWhite'), a.part('Link_feed', 'Steel'), (x + .3, y - .1, z + h - 1.4), r=.25,
           normal=(1, -.4, 0), seg=10)
    K.whip_antenna(a.part('Antennas', 'Steel'), (x, y, z + h), h=.8, r=.015)
    K.beacon(a, (x - .1, y, z + h + .05), r=.05)


def _apron(a):
    """The helipad apron: the slab, the circle and H, the taxi line into the shelter, edge lights, tie-downs, the
    guyed windsock mast, the antenna mast, the fuel point, the ground power unit, the fire cart, chocks."""
    base = a.part('Base', 'Concrete')
    _pad(base, (7.3, HY1 - HY0 + .3, .1), loc=(0, (HY0 + HY1) / 2, .05), chamfer=.02)
    k.extrude(base, [(-3.5, -4.0), (3.5, -4.0), (3.9, -3.3), (3.9, HY0 - .15), (-3.9, HY0 - .15), (-3.9, -3.3)], .1,
              loc=(0, 0, .05), axis='Z', chamfer=.02)
    jt = a.part('Base_joints', 'Undercarriage')
    for x in (-1.95, 1.95):
        jt.box((.03, 3.2, .008), loc=(x, -2.45, .103), bevel=0)
    py = -2.45
    pm = a.part('Pad_marks', 'PlasterWhite')
    k.ring(pm, [(1.3, .1), (1.5, .1), (1.5, .115), (1.3, .115)], loc=(0, py, 0), seg=24)
    for s_ in (-1, 1):
        pm.box((.16, .9, .012), loc=(s_ * .32, py, .108), bevel=0)
    pm.box((.5, .16, .012), loc=(0, py, .108), bevel=0)
    tl = a.part('Taxi_line', 'Hazard')
    for i in range(4):
        tl.box((.12, .35, .01), loc=(0, -.85 + i * .5, .105), bevel=0)
    pe = a.part('Pad_edge', 'Hazard')
    for s_ in (-1, 1):
        pe.box((.1, 3.0, .01), loc=(s_ * 3.7, py + .1, .106), bevel=0)
    lights = a.part('Edge_lights', 'SignalGreen')
    for x in (-3.7, 3.7):
        for y in (-3.9, -2.45, -1.0):
            lights.cyl(.05, .08, loc=(x, y, .14), seg=6, bevel=0)
    for x in (-2.4, -1.2, 0, 1.2, 2.4):
        lights.box((.08, .08, .08), loc=(x, -4.0, .14), bevel=0)
    tie = a.part('Tie_downs', 'Steel')
    for i in range(8):
        u = i * TAU / 8 + .2
        tie.box((.08 + (i % 3) * .02, .08, .04), loc=(math.cos(u) * 1.9, py + math.sin(u) * 1.9 * .75, .12), bevel=0)
    # The windsock mast at the front left corner (guyed, banded, a beacon on top), the antenna mast at the rear right.
    a.part('Mast', 'Steel').cyl(.045, 3.4, loc=(3.75, -3.85, 1.8), seg=6, bevel=0)
    a.part('Mast_bands', 'Hazard').cyl(.052, .3, loc=(3.75, -3.85, 3.0), seg=6, bevel=0)
    k.lathe(a.part('Windsock', 'Hazard'), [(.16, 0), (.11, .5), (.07, 1.0), (0, 1.0)], loc=(3.75, -3.85, 3.35),
            rot=(R90 - .3, 0, -2.2), seg=8, caps=(False, False))
    K.beacon(a, (3.75, -3.85, 3.55), r=.05)
    g = a.part('Kit_guys', 'Steel')
    for gx, gy in ((3.75 - 1.1, -3.85), (3.75, -3.85 + 1.1)):
        g.tube([(3.75, -3.85, 2.8), (gx, gy, .12)], .008, seg=3, caps=False)
        g.box((.1, .1, .05), loc=(gx, gy, .125), bevel=0)
    _lattice_mast(a, (-3.7, 3.85, .1), 4.6)
    g.tube([(-3.7, 3.85, 3.9), (-3.75, 1.9, .12)], .008, seg=3, caps=False)
    g.box((.1, .1, .05), loc=(-3.75, 1.9, .125), bevel=0)
    for i in range(8):
        u = i * TAU / 8 + .6
        tie.box((.06, .06, .03), loc=(math.cos(u) * 1.05, py + math.sin(u) * 1.05 * .75, .115), bevel=0)
    for x in (-3.2, -2.0, -.8, .8, 2.0, 3.2):
        lights.cyl(.04, .06, loc=(x, -.85, .13), seg=6, bevel=0)
    for x, y in ((-3.6, -1.0), (3.65, -1.05), (-.5, -.6), (.5, -.6)):
        k.lathe(a.part('Cones', 'Hazard'), [(.12, 0), (.12, .03), (.035, .45), (0, .45)], loc=(x, y, .1), seg=6)
    W.bags(a, [(2.55, -3.7, .1), (2.55, -2.4, .1)], layers=2, bag=(.48, .28, .15), seed=111, name='Revetment')
    # The fuel point at the front right: the tank on its cradle, the pump cabinet, the hose reel, the spill kit.
    ft = a.part('Fuel_tank', 'Fuel')
    k.lathe(ft, [(.32, 0), (.36, .05), (.36, 1.25), (.32, 1.3), (0, 1.3)], loc=(-3.45, -3.0, .5), rot=(R90, 0, 0),
            seg=10, worn=(1, 2))
    cr = a.part('Tank_cradle', 'Steel')
    for y in (-3.3, -2.0):
        cr.box((.6, .1, .4), loc=(-3.45, y, .3), bevel=0)
    k.block(a.part('Fuel_pump', 'Armor'), (.35, .3, .6), loc=(-3.45, -1.5, .4), chamfer=.02)
    a.part('Hazard_marks', 'Hazard').box((.25, .02, .12), loc=(-3.45, -1.66, .55), bevel=0)
    k.lathe(a.part('Hose_reel', 'BarrelRed'), [(.25, -.06), (.25, .06)], loc=(-3.0, -1.6, .4), rot=(0, R90, 0),
            seg=10)
    a.part('Kit_cables', 'Rubber').tube([(-3.0, -1.75, .3), (-2.6, -2.0, .12), (-1.8, -2.1, .12)], .025, seg=4)
    k.block(a.part('Spill_kit', 'Hazard'), (.4, .3, .45), loc=(-3.55, -.95, .32), chamfer=.02)
    gpu = a.part('Ground_power', 'Team')
    k.block(gpu, (.6, .9, .6), loc=(2.75, -1.55, .5), chamfer=.03)
    K.grille(a, (2.44, -1.55, .55), .6, .35, facing=(-1, 0, 0), slats=4)
    wh = a.part('Tyres', 'Rubber')
    for dy in (-.35, .35):
        for s_ in (-1, 1):
            wh.cyl(.13, .08, loc=(2.75 + s_ * .33, -1.55 + dy, .23), rot=(0, R90, 0), seg=8, bevel=0)
    a.part('Kit_cables', 'Rubber').tube([(2.45, -1.9, .4), (2.0, -2.2, .12), (1.2, -2.45, .12)], .025, seg=4)
    fc = a.part('Fire_cart', 'BarrelRed')
    k.lathe(fc, [(.18, 0), (.18, .8), (.1, .9), (0, .92)], loc=(3.3, -.95, .3), seg=8)
    k.lathe(fc, [(.12, 0), (.12, .7), (.06, .8), (0, .82)], loc=(3.3, -.55, .3), seg=8)
    a.part('Fire_cart_frame', 'Steel').box((.4, .8, .05), loc=(3.3, -.75, .28), bevel=0)
    for dy in (-.3, .3):
        wh.cyl(.14, .06, loc=(3.08, -.75 + dy, .24), rot=(0, R90, 0), seg=8, bevel=0)
    chk = a.part('Chocks', 'CraneYellow')
    for x in (-.7, .7):
        chk.box((.3, .2, .12), loc=(x, -1.2, .16), bevel=.01)
    for x, y in ((3.0, -3.6), (-3.0, -3.6), (0, -1.0)):
        K.dust(a, (x, y, 0), radius=1.7, k=.25)


def aircraft_hangar(a, detail=False):
    """The aircraft hangar: the tension-fabric helicopter shelter behind its helipad apron (module docstring)."""
    _apron(a)
    _shell(a)
    _heli_kit(a)
    # Inside: the rotor blade rack (blades and their covers), the tool cart, the lamps over the door.
    rk = a.part('Blade_rack', 'Steel')
    for x in (-2.6, -1.7):
        rk.box((.06, .06, 1.3), loc=(x, 3.4, .75), bevel=0)
    for z in (.7, 1.0, 1.3):
        a.part('Rotor_blades', 'Armor').box((1.4, .26, .04), loc=(-2.15, 3.3, z), rot=(.0, .0, .05), bevel=0)
        a.part('Blade_covers', 'Canvas').box((.4, .3, .07), loc=(-2.7 + z * .6, 3.3, z + .01), bevel=0)
    k.block(a.part('Tool_cart', 'Team'), (.6, .45, .8), loc=(2.4, 2.9, .5), chamfer=.02)
    K.lamp(a, (0, HY0 - .05, 3.9), facing=(0, -1, -.6), r=.08, guard=True)
    for s_ in (-1, 1):
        K.lamp(a, (s_ * 1.8, HY0 - .05, 3.3), facing=(0, -1, -.6), r=.06, guard=True)
    k.clean(a)


BUILDERS = {
    'aa_vehicle': (aa_vehicle, dict(ao_distance=.5, grime_height=.5)),
    'heavy_aa': (heavy_aa, dict(ao_distance=.5, grime_height=.5)),
    'drone_hangar': (drone_hangar, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'drone_hangar_a': (drone_hangar_a, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'drone_hangar_b': (drone_hangar_b, dict(ao_distance=.8, grime_height=.5, ao_strength=.65)),
    'vehicle_hangar_base': (vehicle_hangar_base, dict(ao_distance=1.0, grime_height=.6, ao_strength=.7)),
    'aircraft_hangar': (aircraft_hangar, dict(ao_distance=1.0, grime_height=.6, ao_strength=.7)),
}
