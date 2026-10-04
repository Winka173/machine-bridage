"""Play-test 14 boss redraw R2 (lane A): the land and air bosses' carried-over or kit weapons, drawn from scratch.

Owner (04/10, Docs/prompts/playtest14_vi.txt, last block): "các tháp súng trên các boss vẽ lại: đừng reuse mà hãy vẽ lại";
"đừng reuse gì hết, tất cả boss khi vẽ lại đều vẽ lại từ đầu". Audit: Docs/models/pt14_reuse_audit.md (R2 rows); DECISIONS
"Play-test 14 boss redraw R2 (lane A)".

Every function here draws for one boss only, from geometry primitives, read from a real design:
- armored_train (Juggernaut, a BP-43 read): the riveted PL-37-style drum turret with its 152 mm (Turret / Main_cannon /
  Muzzle_brake), the locomotive's fixed casemate gun (Muzzle_main.001), the octagonal DShK cupola (Mount_mg), the
  BM-13 rail launcher (Mount_rocket), two 4M quad Maxim AA mounts (Mount_mg.001 / .002), the twin 120 mm mortar in its
  riveted tub (Part_mortar > Mount_mortar).
- nuke_train (Nemesis, a BZhRK "Molodets" read): the angular twin-gun turret on the locomotive (Turret / Main_cannon / _2
  / Muzzle_brake / _2), two Kord remote stations (Mount_mg / .001), the containerised 220 mm rocket packs (Part_rocket),
  the Tor-style vertical-launch SAM turret (Part_missile), the TM-1-180-style railway gun with its tall shield
  (Part_gun152), the Tunguska-style gun / missile turret (Part_aa).
- ixion: the welded wedge turret with the 2A82-style 125 mm (Turret / Main_cannon / Muzzle_brake), the two Kord
  stations on the cab's canopy (Part_cab > Mount_mg / .001).
- mega_gunship (Harpy): the GAU-21 window guns aft (Mount_mg.002 / .003).

The trains and Ixion keep their previous builders' hulls and cars: their weapon functions are swapped for these while
the old builder runs (`swapped`), so no old weapon mesh is drawn. Metres, +Z up, -Y front, +X left.
"""
import contextlib
import math

from mathutils import Vector

import mb_kit27 as k
import mb_kit35 as K

R90 = math.pi / 2
TAU = math.tau


@contextlib.contextmanager
def swapped(module, **funcs):
    """Run with module-level functions replaced (the old builder calls them by their global names)."""
    old = {n: getattr(module, n) for n in funcs}
    for n, f in funcs.items():
        setattr(module, n, f)
    try:
        yield
    finally:
        for n, f in old.items():
            setattr(module, n, f)


def drop_parts(a, *names):
    """Remove every part the previous builder made under these names (any material or parent)."""
    for key in [key for key in a.order if key[0] in names]:
        a.shapes[key].bm.free()
        del a.shapes[key]
        a.order.remove(key)


def fwd(part, profile, loc, seg=12):
    """A turned part along -Y from loc: profile [(radius, distance forward)]."""
    k.lathe(part, profile, loc=loc, rot=K.FORWARD, seg=seg)


def along(part, profile, loc, pitch, seg=12):
    """A turned part along the front, raised `pitch` radians: profile [(radius, distance)]."""
    k.lathe(part, profile, loc=loc, rot=(R90 - pitch, 0, 0), seg=seg)


def per_barrel(a, muzzle, tag, xs):
    for i, x in enumerate(sorted(xs)):
        a.pivot(f'Muzzle_b{i + 1}_{tag}', (x, 0, 0), muzzle)


def rivets(part, pts, r=.028):
    for p in pts:
        part.box((r * 1.6, r * 1.6, r * 1.6), loc=p, bevel=0)


def ring_rivets(part, c, R, z, n, r=.028):
    rivets(part, [(c[0] + math.cos(i * TAU / n) * R, c[1] + math.sin(i * TAU / n) * R, z) for i in range(n)], r)


# ============================================================================= armored_train (Juggernaut)
def jt_turret(a):
    """The gun wagon's turret (Turret), a PL-37 platform's riveted drum read at the boss's 152 mm: the drum on its
    ring with the conical roof, rivet rows and plate seams, the box mantlet with its cheeks, the barrel with the
    recuperator housing and the double-baffle brake (Main_cannon / Muzzle_brake, the recoil parts), the commander's
    cupola with vision slits, the rangefinder across the rear roof, the hatch, the ejection port, grab rails."""
    t = a.pivot('Turret', (0, 3.2, 3.18))
    k.lathe(a.part('Turret_ring', 'Steel', t), [(1.48, -.56), (1.55, -.5), (1.55, -.42), (1.44, -.4)], seg=28)
    body = a.part('Turret_body', 'Team', t)
    k.lathe(body, [(1.4, -.5), (1.44, -.45), (1.44, .85), (1.36, .94), (.98, 1.24), (0, 1.28)], seg=28, worn=(2,))
    rv = a.part('Kit_rivets', 'Steel', t)
    for z in (-.36, .2, .75):
        ring_rivets(rv, (0, 0), 1.455, z, 34, r=.026)
    seams = a.part('Turret_seams', 'Armor', t)
    for i in range(8):
        u = i * TAU / 8 + TAU / 16
        if math.sin(u) < -.6:
            continue
        seams.box((.04, .07, 1.25), loc=(math.cos(u) * 1.45, math.sin(u) * 1.45, .2), rot=(0, 0, u), bevel=0)
    zg = .62
    mant = a.part('Turret_armor', 'Armor', t)
    k.block(mant, (1.05, .5, .9), loc=(0, -1.5, zg - .45), chamfer=.06)
    for sx in (-1, 1):
        k.block(mant, (.18, .45, .78), loc=(sx * .62, -1.36, zg - .39), rot=(0, 0, sx * .25), chamfer=.03)
    rivets(rv, [(sx * .44, -1.76, zg + dz) for sx in (-1, 1) for dz in (-.3, 0, .3)])
    y0 = -1.75
    L = 5.3
    fwd(a.part('Main_cannon', 'Steel', t), [(.17, 0), (.17, .4), (.135, .48), (.12, 4.9), (.125, L), (0, L)],
        (0, y0, zg), seg=14)
    fwd(a.part('Main_cannon_jacket', 'Armor', t), [(.13, 0), (.13, 1.2), (.1, 1.3)], (0, y0, zg + .27), seg=10)
    br = a.part('Muzzle_brake', 'Undercarriage', t)
    fwd(br, [(.13, 0), (.21, .03), (.21, .19), (.16, .21), (.16, .3), (.21, .32), (.21, .48), (.13, .5), (0, .5)],
        (0, y0 - L, zg), seg=14)
    for sx in (-1, 1):
        for dy in (.11, .4):
            br.box((.05, .07, .2), loc=(sx * .2, y0 - L - dy, zg), bevel=0)
    a.pivot('Muzzle_main', (0, y0 - L - .52, zg), t)
    # Roof: the cupola with its slits, the rangefinder with its ear caps, the hatch, the grab rails.
    k.lathe(a.part('Turret_cupola', 'Armor', t), [(.4, 1.1), (.4, 1.42), (.34, 1.5), (0, 1.52)], loc=(-.55, .35, 0),
            seg=14)
    gl = a.part('Glass', 'Glass', t)
    for j in range(5):
        u = -R90 + (j - 2) * .6
        gl.box((.14, .02, .06), loc=(-.55 + math.cos(u) * .405, .35 + math.sin(u) * .405, 1.33), rot=(0, 0, u + R90),
               bevel=0)
    k.lathe(a.part('Turret_rangefinder', 'Armor', t), [(0, -1.25), (.11, -1.25), (.13, -1.15), (.13, 1.15),
                                                       (.11, 1.25), (0, 1.25)], loc=(0, .72, 1.2),
            rot=(0, R90, 0), seg=10)
    for sx in (-1, 1):
        k.block(a.part('Turret_armor', 'Armor', t), (.2, .3, .3), loc=(sx * 1.3, .72, 1.08), chamfer=.03)
    k.lathe(a.part('Turret_hatch', 'Armor', t), [(.32, 0), (.32, .05), (.26, .09), (0, .1)], loc=(.55, .2, 1.18),
            seg=12)
    a.part('Turret_port', 'Armor', t).box((.5, .06, .36), loc=(0, 1.42, .3), bevel=.02)
    hd = a.part('Turret_handles', 'Steel', t)
    for sx in (-1, 1):
        hd.tube([(sx * 1.47, -.6, .66), (sx * 1.47, -.6, .7), (sx * 1.47, .6, .7), (sx * 1.47, .6, .66)], .02, seg=4)
    a.part('Team_band', 'Team', t).cyl(1.46, .14, loc=(0, 0, -.2), seg=28, bevel=0)
    K.whip_antenna(a.part('Antenna', 'Steel', t), (-1.0, 1.0, .9), h=.9, lean=.15)
    K.soot(a, (0, 3.2 + y0 - L, 3.18 + zg), radius=.6, k=.35)


def jt_casemate(a):
    """The locomotive's fixed rear-gun casemate (Muzzle_main.001, gun_car_rear) redrawn: the riveted armoured box with
    its raked front plate, the ball mount, the howitzer barrel with the slotted brake laid forward over the cab, the
    vision ports, the roof hatch; the pivot keeps its place."""
    drop_parts(a, 'Rear_casemate', 'Rear_gun', 'Rear_gun_brake')
    cm = a.part('Rear_casemate', 'Armor')
    base = [(-1.15, -2.95), (1.15, -2.95), (1.22, -2.5), (1.22, -1.0), (-1.22, -1.0), (-1.22, -2.5)]
    top = [(-.92, -2.55), (.92, -2.55), (1.02, -2.3), (1.02, -1.12), (-1.02, -1.12), (-1.02, -2.3)]
    k.sharp_loft(cm, [[(x, y, 2.94) for x, y in base], [(x, y, 3.56) for x, y in top]], chamfer=.04)
    rv = a.part('Kit_rivets', 'Steel')
    rivets(rv, [(sx * 1.1, y, 3.12) for sx in (-1, 1) for y in (-2.6, -2.2, -1.8, -1.4)])
    k.lathe(a.part('Rear_ball', 'Team'), [(0, -.32), (.24, -.27), (.32, -.08), (.32, .08), (.24, .27), (0, .32)],
            loc=(0, -2.82, 3.3), rot=K.FORWARD, seg=12)
    fwd(a.part('Rear_gun', 'Steel'), [(.12, 0), (.12, .2), (.095, .26), (.085, 1.75), (0, 1.75)], (0, -3.0, 3.3))
    br = a.part('Rear_gun_brake', 'Undercarriage')
    fwd(br, [(.09, 0), (.14, .02), (.14, .38), (.09, .4), (0, .4)], (0, -4.75, 3.3))
    for sx in (-1, 1):
        br.box((.04, .22, .1), loc=(sx * .14, -4.95, 3.3), bevel=0)
    a.pivots['Muzzle_main__001'].location = (0, -5.17, 3.3)
    for sx in (-1, 1):
        a.part('Vision_slits', 'Glass').box((.03, .36, .08), loc=(sx * 1.13, -1.9, 3.4), rot=(0, sx * .25, 0), bevel=0)
    k.block(a.part('Rear_casemate_hatch', 'Team'), (.5, .5, .06), loc=(.62, -1.5, 3.55), chamfer=.02)


def jt_quad_maxim(a, index, loc, muzzle):
    """A 4M quad Maxim AA mount (the WW2 armoured trains' AA gun) on its yaw pivot Mount_mg[.NNN]: the base plate and
    column, the cradle frame, four water-jacketed Maxims in two rows with their muzzle boosters, the ammunition boxes,
    the ring sight on its post, the spade grips; Muzzle_mg[.NNN] between the muzzles."""
    tag = '' if index == 0 else f'_{index:03d}'
    m = a.pivot(K.name('Mount_mg', index), loc)
    k.lathe(a.part(f'Quad_base{tag}', 'Armor', m), [(.42, -.04), (.42, .04), (.12, .08), (.1, .3), (.14, .33),
                                                    (0, .34)], seg=12)
    mx, my, mz = muzzle
    fr = a.part(f'Quad_frame{tag}', 'Steel', m)
    for sx in (-1, 1):
        fr.box((.04, .55, .42), loc=(sx * .3, .05, mz), bevel=0)
    fr.box((.64, .06, .06), loc=(0, .3, mz - .18), bevel=0)
    jk = a.part(f'Quad_jackets{tag}', 'Armor', m)
    g = a.part(f'Quad_guns{tag}', 'Steel', m)
    L = -my
    for gx in (-.14, .14):
        for gz in (-.1, .1):
            fwd(jk, [(.055, 0), (.06, .04), (.06, .6), (.045, .66), (.045, .7)], (gx, -.1, mz + gz), seg=10)
            for d_ in (.16, .4):
                g.cyl(.064, .02, loc=(gx, -.1 - d_, mz + gz), rot=K.FORWARD, seg=10, bevel=0)
            fwd(g, [(.018, 0), (.018, L - .95), (.04, L - .92), (.03, L - .82), (0, L - .8)], (gx, -.8, mz + gz), seg=6)
            g.box((.08, .3, .1), loc=(gx, .12, mz + gz), bevel=0)
    for sx in (-1, 1):
        k.block(a.part(f'Quad_ammo{tag}', 'Crate', m), (.16, .3, .22), loc=(sx * .46, .08, mz - .2), chamfer=.015)
    g.cyl(.012, .32, loc=(0, -.2, mz + .3), seg=4, bevel=0)
    k.ring(a.part(f'Quad_sight{tag}', 'Steel', m), [(.11, -.006), (.125, -.006), (.125, .006), (.11, .006)],
           loc=(0, -.2, mz + .46), rot=K.FORWARD, seg=12)
    for sx in (-1, 1):
        a.part(f'Quad_grips{tag}', 'Rubber', m).limb((sx * .1, .32, mz), (sx * .1, .44, mz - .08), .03, .03, bevel=0)
    a.pivot(K.name('Muzzle_mg', index), muzzle, m)


def jt_wagon(a):
    """The gun wagon (wave 8's body, its armour and stowage) with the redrawn weapons: the drum turret, the DShK
    cupola (Mount_mg) and the BM-13 rails (Mount_rocket)."""
    import mb_p35_wave8_bosses as W8
    w0, w1 = W8.TRAIN_CARS[1]
    sec = lambda y, wb, zt, wt: [(-wb, y, 1.34), (wb, y, 1.34), (wb, y, zt - .55), (wt, y, zt), (-wt, y, zt),  # noqa
                                 (-wb, y, zt - .55)]
    k.sharp_loft(a.part('Car_body', 'Team'), [sec(w0, 1.45, 2.4, 1.15), sec(w0 + .5, 1.6, 2.62, 1.3),
                                              sec(w1 - .5, 1.6, 2.62, 1.3), sec(w1, 1.45, 2.4, 1.15)], chamfer=.06)
    a.part('Car_deck', 'Armor').box((2.5, 7.6, .03), loc=(0, (w0 + w1) / 2, 2.63), bevel=0)
    for s in (-1, 1):
        for j in range(5):
            K.armour_plate(a, a.part('Armor', 'Armor'), (.55, 1.35, .05), (s * 1.62, 1.6 + j * 1.5, 1.68),
                           rot=(0, s * R90, 0), rivet=.45)
        a.part('Car_band', 'Team').box((.03, 7.6, .14), loc=(s * 1.63, 5.0, 2.0), bevel=0)
        a.part('Vision_slits', 'Glass').box((.03, .5, .08), loc=(s * 1.45, 5.0, 2.3), rot=(0, s * .5, 0), bevel=0)
        a.part('Tail_lights', 'LavaGlow').box((.12, .03, .08), loc=(s * 1.1, 15.0, 1.4), bevel=0)
    for y in (5.4, 7.2):
        K.crate(a.part('Ammo_boxes', 'Crate'), a.part('Kit_latches', 'Steel'), (.6, .4, .3), (1.0, y, 2.63), bands=1)
    a.part('Vents', 'Steel').cyl(.15, .3, loc=(-1.0, 5.2, 2.78), seg=8, bevel=0)
    jt_turret(a)
    # The DShK cupola: an octagonal riveted drum, the ball mount, the slits, the hatch.
    m = a.pivot('Mount_mg', (0, 6.35, 2.7))
    oc = [(math.cos(u) * .52, math.sin(u) * .52) for u in (i * TAU / 8 + TAU / 16 for i in range(8))]
    k.sharp_loft(a.part('MG_cupola', 'Team', m), [[(x, y, -.06) for x, y in oc],
                                                  [(x * .92, y * .92, .42) for x, y in oc]], chamfer=.03)
    k.lathe(a.part('MG_roof', 'Armor', m), [(.46, .41), (.46, .45), (.3, .5), (0, .51)], seg=8)
    rivets(a.part('Kit_rivets', 'Steel', m), [(x * 1.0, y * 1.0, .3) for x, y in oc])
    k.lathe(a.part('MG_ball', 'Armor', m), [(0, -.15), (.12, -.12), (.15, 0), (.12, .12), (0, .15)],
            loc=(0, -.47, .2), rot=K.FORWARD, seg=10)
    g = a.part('MG_gun', 'Steel', m)
    fwd(g, [(.035, 0), (.035, .78), (.05, .8), (.06, .82), (.06, .9), (0, .92)], (0, -.45, .2), seg=8)
    for d_ in (.2, .35, .5):
        g.cyl(.045, .03, loc=(0, -.45 - d_, .2), rot=K.FORWARD, seg=8, bevel=0)
    gl = a.part('MG_glass', 'Glass', m)
    for i in (2, 4):
        u = i * TAU / 8 + TAU / 16
        gl.box((.03, .16, .05), loc=(math.cos(u) * .5, math.sin(u) * .5, .3), rot=(0, 0, u), bevel=0)
    a.pivot('Muzzle_mg', (0, -1.37, .2), m)
    # The BM-13 rails on their turntable (Mount_rocket): the A-frame, eight I-beam rails in two tiers, the rockets.
    m = a.pivot('Mount_rocket', (0, 8.3, 2.64))
    k.lathe(a.part('Launcher_base', 'Steel', m), [(.58, 0), (.6, .03), (.6, .12), (.5, .14)], seg=14)
    el = math.radians(16)
    d = Vector((0, -math.cos(el), math.sin(el)))
    pivot = Vector((0, .55, .45))
    fr = a.part('Launcher_frame', 'Armor', m)
    for sx in (-1, 1):
        fr.limb((sx * .5, .4, .12), (sx * .55, .55, .45), .1, .1, bevel=0)
        fr.limb((sx * .5, -.3, .12), tuple(pivot + d * .9 + Vector((sx * .55, 0, -.05))), .08, .08, bevel=0)
    rails = a.part('Rocket_rails', 'Steel', m)
    rk = a.part('Rocket_bodies', 'PlasterWhite', m)
    wh = a.part('Rocket_heads', 'Armor', m)
    for tier in (0, 1):
        for i in range(4):
            x = -.45 + i * .3
            base = pivot + Vector((x, 0, tier * .26))
            rails.limb(tuple(base), tuple(base + d * 1.55), .05, .1, bevel=0)
            rb = base + d * .05 + Vector((0, 0, .1))
            k.lathe(rk, [(0, 0), (.066, .02), (.066, 1.05), (0, 1.06)], loc=tuple(rb), rot=(R90 - el, 0, 0), seg=8)
            k.lathe(wh, [(.066, 1.05), (.075, 1.1), (.075, 1.3), (.04, 1.42), (0, 1.46)], loc=tuple(rb),
                    rot=(R90 - el, 0, 0), seg=8)
    for f_ in (.15, 1.35):
        fr.box((1.15, .06, .06), loc=tuple(pivot + d * f_ + Vector((0, 0, .13))), rot=(el, 0, 0), bevel=0)
    tip = pivot + d * 1.55 + Vector((0, 0, .23))
    a.pivot('Muzzle_rocket', tuple(tip), m)


def jt_flatcar(a):
    """The mortar flatcar (wave 8's deck and sides) with the redrawn weapons: the twin 120 mm mortar in its riveted
    tub (Part_mortar: the tub, the ready racks; Mount_mortar: the turntable, two tubes on round baseplates with their
    bipods and the sight), the quad Maxim on the tail (Mount_mg.002)."""
    import mb_p35_wave8_bosses as W8
    m0, m1 = W8.TRAIN_CARS[2]
    mid = (m0 + m1) / 2
    a.part('Deck', 'Armor').box((2.6, m1 - m0, .1), loc=(0, mid, 1.42), bevel=0)
    for s in (-1, 1):
        k.block(a.part('Car_body', 'Team'), (.1, m1 - m0 - .2, .45), loc=(s * 1.28, mid, 1.69), chamfer=.02)
        for e in (-1, 1):
            K.crate(a.part('Mortar_crates', 'Crate'), a.part('Kit_latches', 'Steel'), (.5, .3, .3),
                    (s * .75, mid + e * 1.6, 1.47), bands=1)
    pm = a.pivot('Part_mortar', (0, 12.53, 1.62))
    tub = a.part('Mortar_tub', 'Team', pm)
    k.ring(tub, [(1.12, -.02), (1.2, -.02), (1.2, .5), (1.12, .5)], seg=16)
    k.ring(a.part('Mortar_tub_rim', 'Armor', pm), [(1.1, .5), (1.24, .5), (1.24, .56), (1.1, .56)], seg=16)
    rv = a.part('Kit_rivets', 'Steel', pm)
    for z in (.1, .4):
        ring_rivets(rv, (0, 0), 1.21, z, 24, r=.022)
    for i in range(8):
        u = i * TAU / 8
        a.part('Mortar_tub_seams', 'Armor', pm).box((.03, .05, .5), loc=(math.cos(u) * 1.205, math.sin(u) * 1.205, .24),
                                                    rot=(0, 0, u), bevel=0)
    racks = a.part('Mortar_racks', 'Steel', pm)
    rounds = a.part('Mortar_rounds', 'Fuel', pm)
    for sx in (-1, 1):
        racks.box((.08, .7, .4), loc=(sx * .98, .25, .25), bevel=0)
        for j in range(4):
            k.lathe(rounds, [(0, 0), (.045, .03), (.06, .14), (.06, .32), (.035, .42), (0, .44)],
                    loc=(sx * .9, -.05 + j * .18, .1), seg=8)
    m = a.pivot('Mount_mortar', (0, 0, .1), pm)
    a.part('Mortar_turntable', 'Armor', m).cyl(1.02, .08, loc=(0, 0, .04), seg=18, bevel=0)
    pitch = math.radians(60)
    d = Vector((0, -math.cos(pitch), math.sin(pitch)))
    trot = (R90 - pitch, 0, 0)
    L = 1.8
    for s, nm in ((1, 'Mortar_tube'), (-1, 'Mortar_tube_2')):
        B = Vector((s * .24, .5, .25))
        k.lathe(a.part(nm, 'Steel', m), [(.08, 0), (.08, .12), (.07, .16), (.07, L - .1), (.082, L - .06), (.082, L),
                                         (0, L)], loc=tuple(B), rot=trot, seg=12)
        k.lathe(a.part('Mortar_base', 'Armor', m), [(0, -.02), (.3, -.02), (.3, .03), (.12, .07), (0, .08)],
                loc=(s * .24, .58, .1), seg=12)
        bip = B + d * (L * .55)
        for sx in (-1, 1):
            a.part('Mortar_bipods', 'Steel', m).limb(tuple(bip), (s * .24 + sx * .25, -.25, .1), .04, .04, bevel=0)
        a.part('Mortar_bipods', 'Steel', m).limb((s * .24 - .25, -.25, .12), (s * .24 + .25, -.25, .12), .04, .04,
                                                 bevel=0)
        k.ring(a.part('Mortar_collars', 'Armor', m), [(.08, -.04), (.11, -.04), (.11, .04), (.08, .04)],
               loc=tuple(bip), rot=trot, seg=12)
        a.part('Mortar_bore', 'Charred', m).cyl(.06, .02, loc=tuple(B + d * (L + .005)), rot=trot, seg=10, bevel=0)
    k.block(a.part('Mortar_sight', 'Armor', m), (.1, .14, .18), loc=(.4, .1, .95), chamfer=.015)
    a.part('Glass', 'Glass', m).box((.06, .02, .06), loc=(.4, .02, 1.0), bevel=0)
    a.pivot('Muzzle_mortar', (.24, -.43, 1.86), m)
    K.tone(a, 'Part_mortar', k=.92)
    jt_quad_maxim(a, 2, (0, 14.3, 1.5), (0, -1.1, .35))


def armored_train_base(a):
    """The wave 8 train with every weapon redrawn here (DECISIONS R2): run W8.armored_train with the wagon, the flatcar
    and the flak swapped, then the locomotive's casemate redrawn."""
    import mb_p35_wave8_bosses as W8
    with swapped(W8, _train_wagon=jt_wagon, _train_flatcar=jt_flatcar, _train_flak=jt_quad_maxim):
        W8.armored_train(a)
    jt_casemate(a)


# ============================================================================= nuke_train (Nemesis)
def nt_turret(a):
    """The locomotive's twin-gun turret (gun_behemoth) redrawn: the armoured ring; on Turret the low angular welded
    house, the wedge composite blocks either side of the mantlet, the bustle with its stowage basket, two barrels with
    thermal sleeves and fume extractors (Main_cannon / _2) and multi-baffle brakes (Muzzle_brake / _2) laid up over
    the cab, the gunner's sight, the commander's panoramic sight, two smoke grenade banks, the datalink panel."""
    k.lathe(a.part('Turret_ring', 'Armor'), [(1.32, -.14), (1.32, 0), (1.24, .08), (0, .08)], loc=(0, -4.9, 2.99),
            seg=24, worn=(1,))
    t = a.pivot('Turret', (0, -4.9, 3.13))
    plan = [(-.95, -1.2), (.95, -1.2), (1.22, -.62), (1.22, .95), (1.02, 1.5), (-1.02, 1.5), (-1.22, .95),
            (-1.22, -.62)]
    k.sharp_loft(a.part('Turret_body', 'Team', t), [[(x, y, 0) for x, y in plan],
                                                    [(x * .9, y + (.32 if y < 0 else -.06), .74) for x, y in plan]],
                 chamfer=.05)
    arm = a.part('Turret_armor', 'Armor', t)
    for sx in (-1, 1):
        k.block(arm, (.62, .7, .62), loc=(sx * .78, -1.32, .06), rot=(.35, 0, sx * -.3), chamfer=.04, taper=(.85, .7))
    k.block(arm, (.78, .42, .5), loc=(0, -1.3, .28), rot=(-.12, 0, 0), chamfer=.05)
    k.block(arm, (2.0, .7, .5), loc=(0, 1.62, .18), chamfer=.04)
    bk = a.part('Turret_basket', 'Steel', t)
    bk.tube([(-.95, 1.95, .7), (-.95, 2.25, .7), (.95, 2.25, .7), (.95, 1.95, .7)], .03, seg=4)
    for x in (-.95, -.32, .32, .95):
        bk.box((.03, .3, .03), loc=(x, 2.1, .45), bevel=0)
        bk.box((.03, .03, .26), loc=(x, 2.25, .57), bevel=0)
    K.crate(a.part('Turret_stowage', 'Crate', t), bk, (.6, .26, .22), (-.5, 2.08, .43), bands=1)
    pitch = math.atan2(1.22 - .52, 4.36 - 1.1)
    Lb = math.hypot(3.26, .7)
    cp, sp = math.cos(pitch), math.sin(pitch)
    for s, cn, br in ((-1, 'Main_cannon', 'Muzzle_brake'), (1, 'Main_cannon_2', 'Muzzle_brake_2')):
        x = s * .3
        along(a.part(cn, 'Steel', t), [(.11, 0), (.11, .32), (.09, .38), (.085, .9), (.105, 1.0), (.105, 1.45),
                                       (.085, 1.55), (.08, Lb - .31), (0, Lb - .31)], (x, -1.1, .52), pitch, seg=12)
        b = a.part(br, 'Undercarriage', t)
        along(b, [(.08, 0), (.13, .03), (.13, .12), (.1, .14), (.1, .18), (.13, .2), (.13, .31), (0, .31)],
              (x, -1.1 - (Lb - .31) * cp, .52 + (Lb - .31) * sp), pitch, seg=12)
    a.pivot('Muzzle_main', (0, -4.36, 1.22), t)
    k.block(a.part('Turret_sight', 'Armor', t), (.32, .38, .3), loc=(.62, -.55, .74), chamfer=.03)
    gl = a.part('Vision_slits', 'Glass', t)
    gl.box((.24, .02, .12), loc=(.62, -.75, .9), bevel=0)
    st = a.part('Turret_steel', 'Steel', t)
    st.cyl(.08, .3, loc=(-.55, .45, .89), seg=8, bevel=0)
    k.lathe(a.part('Turret_sight', 'Armor', t), [(.2, 0), (.2, .22), (.15, .28), (0, .3)], loc=(-.55, .45, 1.04),
            seg=10)
    gl.box((.2, .02, .08), loc=(-.55, .25, 1.15), bevel=0)
    for sx in (-1, 1):
        for j in range(3):
            st.cyl(.045, .3, loc=(sx * (1.0 + j * .04), -.35 + j * .14, .62), rot=(-.6, sx * .5, 0), seg=8, bevel=0)
    st.cyl(.04, .55, loc=(.6, 1.2, 1.0), seg=6, bevel=0)
    k.block(a.part('Datalink', 'Medical', t), (.42, .05, .32), loc=(.6, 1.2, 1.35), rot=(-.4, 0, 0), chamfer=.01)
    a.part('Turret_band', 'Team', t).box((2.05, .02, .14), loc=(0, 1.98, .2), bevel=0)
    K.soot(a, (0, -9.2, 4.3), radius=.7, k=.35)


def nt_rws(a, mount, muzzle, loc):
    """A Kord 12.7 mm remote weapon station (the train's close guns) on its yaw pivot: the low base ring, the
    cradle box, the gun with its cone brake, the ammunition box, the sensor head with its two windows."""
    m = a.pivot(mount, loc)
    k.lathe(a.part('Rws_base', 'Armor', m), [(.38, -.05), (.38, .06), (.3, .1), (0, .1)], seg=12, worn=(1,))
    k.block(a.part('Rws_cradle', 'Team', m), (.36, .6, .26), loc=(0, .02, .08), chamfer=.03)
    fwd(a.part('Rws_gun', 'Steel', m), [(.04, 0), (.04, .25), (.03, .3), (.03, .9), (.05, .92), (.04, .98), (0, 1.0)],
        (0, -.27, .2))
    k.block(a.part('Rws_ammo', 'Armor', m), (.16, .34, .2), loc=(.28, .08, .1), chamfer=.015)
    k.block(a.part('Rws_sensor', 'Armor', m), (.18, .26, .2), loc=(-.28, -.08, .14), chamfer=.02)
    gl = a.part('MG_glass', 'Glass', m)
    gl.box((.06, .02, .06), loc=(-.32, -.215, .2), bevel=0)
    gl.box((.06, .02, .06), loc=(-.24, -.215, .2), bevel=0)
    a.pivot(muzzle, (0, -1.27, .2), m)


def nt_rocket_car(a):
    """Rocket flatcar (Part_rocket > Mount_rocket > Muzzle_rocket): the turntable and the elevating cradle with two
    containerised packs of six 220 mm tubes (Uragan-1M style), their mouths, ribs and lifting lugs, the rams, the
    cable loom; ammunition crates on the deck."""
    import mb_p35_nuke_train as NT
    p, yc = NT._flatcar(a, 11.38, 15.43, 'Part_rocket', 13.4)
    k.lathe(a.part('Rocket_pedestal', 'Armor', p), [(.92, 0), (.92, .12), (.62, .2), (.56, .6), (0, .6)], seg=16,
            worn=(1,))
    a.part('Rocket_band', 'Team', p).cyl(.93, .06, loc=(0, 0, .06), seg=16, bevel=0)
    m = a.pivot('Mount_rocket', (0, 0, .64), p)
    k.block(a.part('Rocket_cradle', 'Steel', m), (1.5, 1.0, .22), loc=(0, .15, .05), chamfer=.03)
    elev = math.atan2(.68, 1.3)
    rot = (-elev, 0, 0)
    mm = K.frame((0, .5, .62), rot)
    for sx in (-1, 1):
        cx = sx * .42
        k.block(a.part('Rocket_packs', 'Team', m), (.78, 2.9, .6), loc=K._at(mm, (cx, 0, -.05)), rot=rot, chamfer=.04)
        for i in range(3):
            for j in range(2):
                p0 = K._at(mm, (cx - .24 + i * .24, -1.455, -.2 + j * .3))
                a.part('Rocket_mouths', 'Charred', m).cyl(.1, .02, loc=p0, rot=(R90 - elev, 0, 0), seg=10, bevel=0)
                k.ring(a.part('Rocket_rims', 'Steel', m), [(.1, -.01), (.115, -.01), (.115, .01), (.1, .01)],
                       loc=p0, rot=(R90 - elev, 0, 0), seg=10)
        for f_ in (-.9, 0, .9):
            a.part('Rocket_ribs', 'Armor', m).box((.8, .07, .64), loc=K._at(mm, (cx, f_, -.05)), rot=rot, bevel=0)
        for f_ in (-1.0, 1.0):
            a.part('Rocket_lugs', 'Steel', m).box((.12, .12, .1), loc=K._at(mm, (cx, f_, .3)), rot=rot, bevel=0)
    for s in (-1, 1):
        a.part('Rocket_rams', 'Steel', m).limb((s * .55, -.35, .05), K._at(mm, (s * .55, -.7, -.38)), .08, .08,
                                               bevel=0)
    a.part('Rocket_cables', 'Rubber', m).tube([(.7, .5, .1), (.8, 1.0, .3), K._at(mm, (.8, 1.3, .1))], .03, seg=4)
    a.pivot('Muzzle_rocket', K._at(mm, (0, -1.5, -.05)), m)
    NT._crates(a, (-.95, 1.5, .0), n=2, yaw=R90, size=(.45, 1.0, .3), parent=p)
    NT._crates(a, (1.0, -1.55, .0), n=2, yaw=R90, size=(.45, 1.0, .3), parent=p)
    K.tone(a, 'Rocket_', k=.9)


def nt_sam_car(a):
    """SAM flatcar (Part_missile > Mount_missile > Muzzle_missile): a Tor-style turret: the low turntable, the box
    turret with the vertical launch module (eight cell hatches, one open) in its middle, the tracking phased array on
    the raked front, the search radar on its hinge on top, the EO box; Muzzle_missile on the open cell (vertical
    launch). Kept under the railway gun's barrel line."""
    import mb_p35_nuke_train as NT
    p, yc = NT._flatcar(a, 16.19, 20.24, 'Part_missile', 18.22)
    k.lathe(a.part('Sam_base', 'Armor', p), [(1.12, 0), (1.12, .1), (.98, .18), (0, .18)], seg=16, worn=(1,))
    m = a.pivot('Mount_missile', (0, 0, .32), p)
    k.lathe(a.part('Sam_pedestal', 'Steel', m), [(.98, -.14), (.98, .02), (.9, .07), (0, .07)], seg=16)
    body = a.part('Sam_body', 'Team', m)
    plan = [(-.85, -.95), (.85, -.95), (.98, -.7), (.98, 1.05), (-.98, 1.05), (-.98, -.7)]
    k.sharp_loft(body, [[(x, y, .07) for x, y in plan], [(x * .96, y + (.28 if y < 0 else 0), .98) for x, y in plan]],
                 chamfer=.05)
    k.block(a.part('Sam_array', 'Undercarriage', m), (1.25, .08, .62), loc=(0, -.86, .52), rot=(.29, 0, 0),
            chamfer=.02, ends=(True, True))
    a.part('Sam_array_frame', 'Armor', m).box((1.38, .06, .72), loc=(0, -.83, .52), rot=(.29, 0, 0), bevel=0)
    vls = a.part('Sam_vls', 'Armor', m)
    k.block(vls, (1.1, .9, .1), loc=(0, .35, .98), chamfer=.02)
    cells = a.part('Sam_cells', 'Steel', m)
    for i in range(4):
        for j in range(2):
            x, y = -.39 + i * .26, .16 + j * .38
            if (i, j) == (0, 0):
                a.part('Sam_cell_open', 'Charred', m).box((.2, .3, .01), loc=(x, y, 1.085), bevel=0)
                cells.box((.2, .03, .3), loc=(x, y - .15, 1.23), rot=(-.25, 0, 0), bevel=0)
            else:
                cells.box((.2, .3, .03), loc=(x, y, 1.09), bevel=0)
    # The search radar on its hinge on top rear, the EO box at the front corner, the generator behind.
    a.part('Sam_hinge', 'Steel', m).cyl(.05, .9, loc=(0, .95, 1.06), rot=(0, R90, 0), seg=8, bevel=0)
    k.block(a.part('Sam_radar', 'Armor', m), (1.3, .12, .5), loc=(0, .98, 1.33), rot=(-.25, 0, 0), chamfer=.02,
            ends=(True, True))
    a.part('Sam_radar_face', 'Medical', m).box((1.2, .02, .42), loc=(0, .91, 1.33), rot=(-.25, 0, 0), bevel=0)
    k.block(a.part('Sam_eo', 'Armor', m), (.22, .26, .2), loc=(.75, -.5, .98), chamfer=.02)
    a.part('Glass', 'Glass', m).box((.14, .02, .1), loc=(.75, -.64, 1.08), bevel=0)
    a.pivot('Muzzle_missile', (-.39, .16, 1.3), m)
    k.block(a.part('Sam_generator', 'Team', p), (1.0, .7, .7), loc=(-.75, 1.55, .35), chamfer=.04)
    K.grille(a, (-.75, 1.19, .38), .6, .35, facing=(0, -1, 0), slats=4, parent=p)
    K.tone(a, 'Sam_', k=.9)


def nt_gun_car(a):
    """Gun flatcar (Part_gun152 > Mount_gun > Muzzle_gun): a TM-1-180-style railway mount: the turntable, the two tall
    side frames with their lightening holes and trunnions, the wrapped shield with its roof, the cradle and the
    recoil cylinders over the barrel, the long barrel laid up at its rest elevation (clear over the SAM car) with the
    brake (Gun_barrels / Gun_muzzles kick back on the mount), the loading tray and ready rounds, the outrigger jacks
    stowed on the car's sides."""
    import mb_p35_nuke_train as NT
    p, yc = NT._flatcar(a, 20.97, 25.02, 'Part_gun152', 23.0)
    for s in (-1, 1):
        for y in (-1.3, 1.3):
            a.part('Gun_jacks', 'Steel', p).limb((s * 1.52, y, -.55), (s * 1.52, y, .3), .13, .13, bevel=0)
            k.block(a.part('Gun_jacks', 'Armor', p), (.1, .42, .32), loc=(s * 1.6, y, .05), chamfer=.015)
    m = a.pivot('Mount_gun', (0, 0, .1), p)
    k.lathe(a.part('Gun_turntable', 'Armor', m), [(1.08, -.1), (1.08, .06), (.9, .12), (0, .12)], seg=18, worn=(1,))
    tz = 1.55
    fr = a.part('Gun_frames', 'Armor', m)
    for sx in (-1, 1):
        k.extrude(fr, [(-.9, .1), (.95, .1), (.6, tz + .25), (-.2, tz + .35), (-.9, .5)], .1, loc=(sx * .5, 0, 0),
                  axis='X', chamfer=.02)
        for hy, hz in ((-.2, .55), (.45, .55)):
            a.part('Gun_holes', 'Charred', m).box((.11, .3, .28), loc=(sx * .5, hy, hz), bevel=0)
        a.part('Gun_trunnions', 'Steel', m).cyl(.13, .16, loc=(sx * .58, .1, tz), rot=(0, R90, 0), seg=10, bevel=0)
    el = math.radians(8)
    d = Vector((0, -math.cos(el), math.sin(el)))
    rot = (R90 - el, 0, 0)
    sh = a.part('Gun_shield', 'Team', m)
    zb = tz - .78
    k.extrude(sh, [(-1.02, 0), (1.02, 0), (.84, 1.38), (-.84, 1.38)], .1, loc=(0, -.62, zb), rot=(.16, 0, 0), axis='Y',
              chamfer=.02)
    for sx in (-1, 1):
        k.extrude(sh, [(-.66, 0), (.8, 0), (.8, 1.0), (.1, 1.3), (-.6, 1.36)], .08, loc=(sx * (.98 - .0), .02, zb),
                  rot=(0, sx * -.08, 0), axis='X', chamfer=.015)
    k.extrude(sh, [(-.84, -.62), (.84, -.62), (.8, .2), (-.8, .2)], .07, loc=(0, -.06, zb + 1.36), rot=(-.05, 0, 0),
              axis='Z', chamfer=.02)
    rv = a.part('Kit_rivets', 'Steel', m)
    for zz in (.15, .7, 1.22):
        rivets(rv, [(x, -.69 + zz * .16, zb + zz) for x in (-.8, -.5, .5, .8)], r=.025)
    k.block(a.part('Gun_sight', 'Armor', m), (.26, .32, .24), loc=(-.55, -.5, zb + 1.43), chamfer=.03)
    a.part('Glass', 'Glass', m).box((.18, .02, .1), loc=(-.55, -.67, zb + 1.53), bevel=0)
    a.part('Gun_port', 'Charred', m).box((.38, .12, .55), loc=(0, -.66, tz + .02), rot=(.16, 0, 0), bevel=0)
    for sx in (-1, 1):
        k.ring(a.part('Gun_wheels', 'Steel', m), [(.16, -.015), (.19, -.015), (.19, .015), (.16, .015)],
               loc=(sx * .62, .7, 1.0), rot=(0, R90, 0), seg=10)
    c0 = Vector((0, .2, tz))
    k.block(a.part('Gun_cradle', 'Steel', m), (.42, 1.5, .38), loc=tuple(c0 + d * .1), rot=(el, 0, 0), chamfer=.03)
    for sx in (-1, 1):
        k.lathe(a.part('Gun_recoil', 'Steel', m), [(.08, 0), (.08, 1.4), (0, 1.42)],
                loc=tuple(c0 + Vector((sx * .14, 0, .24)) + d * -.3), rot=rot, seg=8)
    L = 6.2
    b0 = c0 + d * -.6
    k.lathe(a.part('Gun_barrels', 'Steel', m), [(.15, 0), (.15, .7), (.12, .8), (.1, L - .6), (.105, L), (0, L)],
            loc=tuple(b0), rot=rot, seg=12)
    k.lathe(a.part('Gun_muzzles', 'Undercarriage', m), [(.1, 0), (.17, .04), (.17, .5), (.12, .55), (0, .55)],
            loc=tuple(b0 + d * L), rot=rot, seg=12)
    a.pivot('Muzzle_gun', tuple(b0 + d * (L + .57)), m)
    k.block(a.part('Gun_breech', 'Armor', m), (.44, .55, .44), loc=tuple(c0 + d * -1.05), rot=(el, 0, 0), chamfer=.03)
    a.part('Gun_band', 'Hazard', m).box((1.7, .02, .1), loc=(0, -.72 + 1.15 * .16, zb + 1.15), rot=(.16, 0, 0), bevel=0)
    k.block(a.part('Gun_tray', 'Steel', m), (.5, 1.0, .06), loc=(0, 1.15, .85), chamfer=.01)
    rk = a.part('Gun_rack', 'Steel', p)
    rk.box((1.2, .55, .05), loc=(0, 1.65, .25), bevel=0)
    for i in range(5):
        k.lathe(a.part('Gun_rounds', 'Fuel', p), [(0, -.4), (.05, -.33), (.075, -.2), (.075, .38), (0, .4)],
                loc=(-.48 + i * .24, 1.65, .36), rot=(0, R90, R90), seg=8)
    K.soot(a, (0, 23.0 + (b0 + d * L).y, 1.72 + (b0 + d * L).z), radius=.5, k=.3)
    K.tone(a, 'Gun_', k=.9)


def nt_aa_car(a):
    """AA flatcar (Part_aa > Mount_mg.002 > Muzzle_mg.002): a Tunguska-style turret: the ring, the faceted turret, a
    pair of 30 mm barrels either side with their cooling jackets, two missile containers behind each gun pair, the
    tracking dish at the front of the roof, the search antenna on its post behind; Muzzle_mg.002 between the gun tips."""
    import mb_p35_nuke_train as NT
    p, yc = NT._flatcar(a, 25.78, 29.83, 'Part_aa', 27.8)
    m = a.pivot('Mount_mg__002', (0, 0, .1), p)
    k.lathe(a.part('Aa_ring', 'Steel', m), [(1.02, -.1), (1.02, .02), (.92, .06), (0, .06)], seg=16)
    plan = [(-.55, -.85), (.55, -.85), (.72, -.4), (.72, .95), (-.72, .95), (-.72, -.4)]
    k.sharp_loft(a.part('Aa_house', 'Team', m), [[(x, y, .06) for x, y in plan],
                                                 [(x * .9, y + (.2 if y < 0 else -.05), .82) for x, y in plan]],
                 chamfer=.04)
    zg = .5
    for sx in (-1, 1):
        x = sx * .86
        k.block(a.part('Aa_cradles', 'Armor', m), (.22, 1.0, .5), loc=(x, -.15, zg - .25), chamfer=.03)
        for dz in (-.09, .09):
            fwd(a.part('Aa_guns', 'Steel', m), [(.06, 0), (.06, .5), (.042, .56), (.035, 2.4), (.045, 2.42),
                                                (.045, 2.55), (0, 2.56)], (x, -.6, zg + dz), seg=8)
        for f_ in (.25,):
            a.part('Aa_guns', 'Steel', m).box((.1, .1, .3), loc=(x, -.6 - f_, zg), bevel=0)
        for j, dz in enumerate((.12, .34)):
            fwd(a.part('Aa_missiles', 'Armor', m), [(.085, -.55), (.09, -.5), (.09, .6), (.085, .65)],
                (sx * (1.1 + j * .0), .35, zg + dz), seg=10)
            a.part('Aa_missile_caps', 'Charred', m).cyl(.07, .02, loc=(sx * 1.1, -.31, zg + dz), rot=K.FORWARD, seg=10,
                                                        bevel=0)
    a.pivot('Muzzle_mg__002', (0, -3.17, zg), m)
    k.lathe(a.part('Aa_dish', 'Medical', m), [(0, 0), (.15, .02), (.28, .07), (.34, .11)], loc=(0, -.45, 1.05),
            rot=(R90 + .3, 0, 0), seg=14)
    a.part('Aa_steel', 'Steel', m).cyl(.05, .25, loc=(0, -.38, .92), seg=6, bevel=0)
    a.part('Aa_steel', 'Steel', m).cyl(.05, .5, loc=(0, .65, 1.05), seg=6, bevel=0)
    k.block(a.part('Aa_search', 'Armor', m), (1.2, .1, .36), loc=(0, .68, 1.38), rot=(-.2, 0, 0), chamfer=.02,
            ends=(True, True))
    a.part('Aa_search_face', 'Undercarriage', m).box((1.1, .02, .3), loc=(0, .62, 1.38), rot=(-.2, 0, 0), bevel=0)
    k.block(a.part('Aa_sight', 'Glass', m), (.18, .12, .14), loc=(.3, -.62, .82), chamfer=.015)
    for s in (-1, 1):
        a.part('Tail_lights', 'Alloy').box((.14, .04, .1), loc=(s * 1.3, 29.85, 1.25), bevel=0)
    NT._crates(a, (-1.0, 1.5, .0), n=3, size=(.5, .7, .28), parent=p)
    K.tone(a, 'Aa_', k=.9)


def nuke_train_base(a):
    """The wave 12 train with every weapon redrawn here (DECISIONS R2): NT.nuke_train with the turret, the cupolas
    and the four flatcars swapped (the ICBM erector, the launcher car and the locomotive's hull are kept)."""
    import mb_p35_nuke_train as NT
    with swapped(NT, _loco_turret=nt_turret, _cupola=nt_rws, _rocket_car=nt_rocket_car, _sam_car=nt_sam_car,
                 _gun_car=nt_gun_car, _aa_car=nt_aa_car):
        NT.nuke_train(a)


# ============================================================================= ixion
def ix_turret(a):
    """Ixion's turret redrawn for the 26 m truck: the welded wedge house (not a cast dome), the composite wedge blocks
    either side of the mantlet with Relikt-style tiles on them, the long bustle with its slat-armoured sides, the
    2A82-style 125 mm with its segmented thermal sleeve, fume extractor and muzzle reference collar (Main_cannon /
    Muzzle_brake), the commander's panoramic sight, the gunner's sight block, two hatches, smoke grenade banks, the
    bustle rack; Muzzle_main at the collar's mouth (the old place)."""
    import mb_p35_ixion as IX
    t = a.pivot('Turret', IX.TURRET)
    k.lathe(a.part('Turret_steel', 'Steel', t), [(2.7, -.05), (2.86, -.02), (2.86, .1), (2.7, .14)], seg=30)
    base = [(-1.55, -2.6), (1.55, -2.6), (2.75, -1.55), (2.9, 1.6), (2.5, 3.3), (-2.5, 3.3), (-2.9, 1.6),
            (-2.75, -1.55)]
    top = [(-1.25, -2.15), (1.25, -2.15), (2.42, -1.25), (2.6, 1.5), (2.25, 3.1), (-2.25, 3.1), (-2.6, 1.5),
           (-2.42, -1.25)]
    body = a.part('Turret_body', 'Team', t)
    k.sharp_loft(body, [[(x, y, .05) for x, y in base], [(x * 1.01, y, .55) for x, y in base],
                        [(x, y, 1.18) for x, y in top]], chamfer=.08)
    k.inset(body, lambda c, n, f: abs(n.z) < .4 and c.y > -1.0, width=.12, depth=-.03)
    arm = a.part('Turret_armor', 'Armor', t)
    tiles = a.part('Era_tiles', 'Armor', t)
    for sx in (-1, 1):
        k.block(arm, (1.45, 1.55, .95), loc=(sx * 1.45, -2.65, .12), rot=(0, 0, sx * .42), chamfer=.06,
                taper=(.85, .65))
        for i in range(3):
            for j in range(2):
                tiles.box((.42, .34, .06), loc=(sx * (.95 + i * .45), -2.95 + i * .2 + j * .38, 1.1 + j * .02),
                          rot=(.12, 0, sx * .42), bevel=.01)
    zg = .627
    k.block(arm, (1.3, .9, .95), loc=(0, -2.75, zg - .47), chamfer=.08)
    y0, L = -3.386, 8.6
    fwd(a.part('Main_cannon', 'Steel', t), [(.3, 0), (.3, .55), (.25, .62), (.25, 2.3), (.31, 2.4), (.31, 3.6),
                                            (.25, 3.7), (.24, 5.3), (.22, 5.4), (.22, L), (0, L)], (0, y0, zg), seg=16)
    for f_ in (1.0, 1.6, 4.4, 6.6):
        k.ring(a.part('Turret_sleeve_bands', 'Armor', t), [(.25, -.04), (.275, -.04), (.275, .04), (.25, .04)],
               loc=(0, y0 - f_, zg), rot=K.FORWARD, seg=14)
    fwd(a.part('Muzzle_brake', 'Undercarriage', t), [(.22, 0), (.26, .03), (.26, .17), (.22, .2), (0, .2)],
        (0, y0 - L, zg), seg=16)
    a.part('Turret_mrs', 'Steel', t).box((.12, .2, .12), loc=(0, y0 - L + .1, zg + .29), bevel=0)
    a.pivot('Muzzle_main', (0, y0 - L - .18, zg), t)
    # Sights, hatches, the smoke banks, the slat armour on the bustle sides, the rack.
    st = a.part('Turret_fit', 'Steel', t)
    st.cyl(.16, .2, loc=(-1.0, -.6, 1.28), seg=10, bevel=0)
    k.block(a.part('Turret_sights', 'Armor', t), (.6, .7, .4), loc=(-1.0, -.6, 1.36), chamfer=.06)
    gl = a.part('Glass', 'Glass', t)
    gl.box((.4, .03, .18), loc=(-1.0, -.96, 1.58), bevel=0)
    gl.box((.4, .03, .18), loc=(-1.0, -.24, 1.58), bevel=0)
    k.block(a.part('Turret_sights', 'Armor', t), (.62, .8, .42), loc=(1.25, -1.35, 1.18), chamfer=.05,
            taper=(.9, .8))
    gl.box((.44, .03, .2), loc=(1.25, -1.76, 1.34), rot=(-.3, 0, 0), bevel=0)
    for x, y in ((1.15, .55), (-1.25, .9)):
        k.lathe(a.part('Turret_hatches', 'Armor', t), [(.46, 0), (.46, .07), (.38, .12), (0, .13)], loc=(x, y, 1.17),
                seg=14)
        st.box((.14, .2, .1), loc=(x + .44, y, 1.23), bevel=0)
    for sx in (-1, 1):
        for j in range(4):
            st.cyl(.07, .42, loc=(sx * (2.55 - j * .05), -1.0 + j * .2, .95), rot=(-.5, sx * .55, 0), seg=8, bevel=0)
        slat = a.part('Turret_slats', 'Steel', t)
        for j in range(7):
            slat.box((.05, .05, .75), loc=(sx * 2.98, .4 + j * .38, .55), bevel=0)
        for z in (.2, .9):
            slat.box((.05, 2.4, .05), loc=(sx * 2.98, 1.55, z), bevel=0)
        for y in (.4, 2.7):
            slat.box((.14, .05, .05), loc=(sx * 2.92, y, .9), bevel=0)
    a.part('Team_band', 'Team', t).box((3.6, .05, .25), loc=(0, 3.31, .55), bevel=0)
    K.whip_antenna(a.part('Antennas', 'Steel', t), (1.4 * 1.38, 1.55 * 1.38, 1.18), h=.5, r=.06)
    K.soot(a, (0, IX.TURRET[1] + y0 - L, zg + IX.TURRET[2]), radius=.8, k=.35)


def ix_kord(a, parent, loc, index=0, scale=1.0, slot='mg', post=0.0, **_):
    """Ixion's canopy guns (the cab's Mount_mg / .001, sized x `scale` for the 26 m truck): a Kord 12.7 mm on a 6U6-
    style pedestal: the base flange and column (`post` high), the yoke, the receiver with its top cover, the barrel
    with the cone brake, the box magazine, the small flat shield with its sight slot, the grips; Muzzle_<slot>[.NNN]."""
    sc = scale
    tag = '' if index == 0 else f'__{index:03d}'
    x, y, z = loc
    col = a.part(f'Kord_post{tag}', 'Steel', parent)
    k.lathe(col, [(.12 * sc, 0), (.12 * sc, .03 * sc), (.045 * sc, .05 * sc), (.04 * sc, post), (.06 * sc, post + .02),
                  (.06 * sc, post + .05 * sc), (0, post + .05 * sc)], loc=(x, y, z), seg=10)
    for i in range(3):
        u = i * TAU / 3
        col.limb((x + math.cos(u) * .1 * sc, y + math.sin(u) * .1 * sc, z + .03 * sc),
                 (x + math.cos(u) * .03 * sc, y + math.sin(u) * .03 * sc, z + post * .5), .015 * sc, .015 * sc, bevel=0)
    m = a.pivot(K.name(f'Mount_{slot}', index), (x, y, z + post + .05 * sc), parent)
    yk = a.part(f'Kord_yoke{tag}', 'Armor', m)
    for sx in (-1, 1):
        yk.box((.02 * sc, .14 * sc, .16 * sc), loc=(sx * .07 * sc, .0, .08 * sc), bevel=0)
    k.block(a.part(f'Kord_body{tag}', 'Armor', m), (.1 * sc, .42 * sc, .1 * sc), loc=(0, .04 * sc, .12 * sc),
            chamfer=.012 * sc)
    k.block(a.part(f'Kord_body{tag}', 'Armor', m), (.09 * sc, .2 * sc, .04 * sc), loc=(0, .08 * sc, .22 * sc),
            chamfer=.008 * sc)
    Lg = 1.1 * sc
    fwd(a.part(f'Kord_gun{tag}', 'Steel', m), [(.03 * sc, 0), (.03 * sc, .08 * sc), (.02 * sc, .1 * sc),
                                              (.02 * sc, Lg - .55 * sc), (.04 * sc, Lg - .52 * sc),
                                              (.035 * sc, Lg - .44 * sc), (0, Lg - .42 * sc)],
        (0, -.17 * sc, .17 * sc), seg=8)
    k.block(a.part(f'Kord_mag{tag}', 'Crate', m), (.08 * sc, .16 * sc, .12 * sc), loc=(.09 * sc, .06 * sc, .1 * sc),
            chamfer=.01 * sc)
    k.extrude(a.part(f'Kord_shield{tag}', 'Team', m), [(-.18 * sc, -.12 * sc), (.18 * sc, -.12 * sc),
                                                      (.16 * sc, .14 * sc), (-.16 * sc, .14 * sc)], .015 * sc,
              loc=(0, -.2 * sc, .2 * sc), axis='Y', chamfer=0)
    a.part(f'Kord_slot{tag}', 'Charred', m).box((.05 * sc, .02 * sc, .03 * sc), loc=(-.08 * sc, -.21 * sc, .26 * sc),
                                                bevel=0)
    for sx in (-1, 1):
        a.part(f'Kord_grips{tag}', 'Rubber', m).limb((sx * .04 * sc, .25 * sc, .14 * sc),
                                                     (sx * .04 * sc, .3 * sc, .07 * sc), .02 * sc, .02 * sc, bevel=0)
    a.pivot(K.name(f'Muzzle_{slot}', index), (0, -.17 * sc - (Lg - .42 * sc) - .01 * sc, .17 * sc), m)


def ixion_base(a):
    """The P35 truck with its turret and canopy guns redrawn here (DECISIONS R2)."""
    import mb_p35_ixion as IX
    with swapped(IX, _turret=ix_turret), swapped(K, pintle_mg=ix_kord):
        IX.ixion(a)


# ============================================================================= mega_gunship (Harpy)
def hp_gau21(a, index, s):
    """A GAU-21 (M3M .50) on its window mount aft (Mount_mg.002 left, .003 right): the swing arm and the pintle
    socket out of the window, the receiver with its feed tray cover, the barrel with the vented flash hider and the
    carrying handle, the spade grips, the ammunition can and its flexible chute into the cabin; Muzzle_mg.NNN."""
    tag = f'_{index:03d}'
    arm = a.part('Hmg_brackets', 'Steel')
    arm.limb((s * 1.36, 3.2, 1.9), (s * 1.66, 3.2, 1.9), .07, .07, bevel=0)
    arm.limb((s * 1.36, 3.0, 1.9), (s * 1.36, 3.4, 1.9), .06, .06, bevel=0)
    a.part('Gau_window', 'Charred').box((.03, .6, .46), loc=(s * 1.375, 3.2, 2.12), bevel=0)
    m = a.pivot(K.name('Mount_mg', index), (s * 1.68, 3.2, 1.96))
    k.lathe(a.part(f'Gau_pintle{tag}', 'Steel', m), [(.05, -.08), (.05, .08), (.07, .1), (.07, .14), (0, .15)], seg=8)
    k.block(a.part(f'Gau_body{tag}', 'Armor', m), (.14, .5, .16), loc=(0, .02, .22), chamfer=.02)
    k.block(a.part(f'Gau_body{tag}', 'Armor', m), (.12, .26, .05), loc=(0, .08, .325), chamfer=.01)
    g = a.part(f'Gau_barrel{tag}', 'Steel', m)
    fwd(g, [(.045, 0), (.045, .1), (.03, .14), (.03, .9), (.045, .93), (.045, 1.05), (0, 1.06)], (0, -.22, .23), seg=8)
    for d_ in (.96, 1.0):
        g.box((.1, .015, .015), loc=(0, -.22 - d_, .23), bevel=0)
    g.tube([(0, -.3, .32), (0, -.35, .4), (0, -.55, .4), (0, -.6, .32)], .012, seg=4)
    for sx in (-1, 1):
        a.part(f'Gau_grips{tag}', 'Rubber', m).limb((sx * .05, .27, .24), (sx * .05, .36, .16), .025, .025, bevel=0)
    k.block(a.part(f'Gau_ammo{tag}', 'Crate', m), (.18, .3, .22), loc=(s * -.2, .1, .14), chamfer=.015)
    a.part(f'Gau_chute{tag}', 'Undercarriage', m).tube([(s * -.12, .06, .26), (s * -.25, .1, .32), (s * -.3, .2, .25)],
                                                       .035, seg=6)
    a.pivot(K.name('Muzzle_mg', index), (0, -1.3, .23), m)
